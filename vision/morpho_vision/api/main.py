"""
FastAPI Microservice for LEAF & SEED MORPHO-ANALYZER.
Provides RESTful endpoints for automated batch analysis and direct SahelTraits-DB sync.
"""

from contextlib import asynccontextmanager
from pathlib import Path
import shutil
import tempfile
import time
from typing import List, Optional
import cv2
import fastapi
from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import numpy as np

from morpho_vision.api.saheltraits_client import SahelTraitsClient
from morpho_vision.api.schemas import (
    BatchItemSummary,
    BatchProcessRequest,
    BatchProcessResponse,
    CalibrationResponse,
    HerbivoryDetail,
    LeafAnalysisResponse,
    SahelTraitsSyncRequest,
    SahelTraitsSyncResponse,
    SeedAnalysisResponse,
    SingleLeafOut,
    SingleSeedOut,
)
from morpho_vision.config import DEFAULT_CONFIG
from morpho_vision.pipeline import MorphoVisionPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure directories exist
    DEFAULT_CONFIG.output_dir.mkdir(parents=True, exist_ok=True)
    (DEFAULT_CONFIG.output_dir / "qc_overlays").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Leaf & Seed Morpho-Analyzer Microservice",
    description="Automated computer vision microservice for plant functional traits (Thèse Doctorat 2026-2029)",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

pipeline = MorphoVisionPipeline(DEFAULT_CONFIG)
saheltraits_client = SahelTraitsClient(DEFAULT_CONFIG.traceability.saheltraits_base_url)


@app.get("/api/v1/health", tags=["Health"])
def health_check():
    """Returns microservice health and vision runtime environment status."""
    return {
        "status": "healthy",
        "service": "Leaf & Seed Morpho-Analyzer",
        "author": "YAGO Abdoul Rachide",
        "component": "Vision Layer 2",
        "opencv_version": cv2.__version__,
        "fallback_dpi": DEFAULT_CONFIG.calibration.fallback_dpi,
        "calibration_target": f"{DEFAULT_CONFIG.calibration.known_area_cm2} cm2",
    }


@app.post("/api/v1/analyze/leaf", response_model=LeafAnalysisResponse, tags=["Analysis"])
async def analyze_leaf(
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None),
    is_compound: bool = Form(False),
    qr_tag_override: Optional[str] = Form(None),
):
    """Analyzes a leaf scan: measures area (cm²), perimeter, length, width, circularity,

    aspect ratio, herbivory %, and extracts QR code tag.
    """
    temp_path = None
    try:
        if file is not None:
            # Save uploaded file to temp file
            suffix = Path(file.filename or "leaf.jpg").suffix or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                temp_path = tmp.name
            target_input = temp_path
        elif image_path:
            target_input = image_path
            if not Path(target_input).exists():
                raise HTTPException(status_code=400, detail=f"Image file '{target_input}' does not exist.")
        else:
            raise HTTPException(status_code=400, detail="Either 'file' or 'image_path' must be provided.")

        result, qc_path, elapsed = pipeline.process_leaf_scan(
            image_input=target_input,
            is_compound=is_compound,
            qr_tag_override=qr_tag_override,
            save_qc_overlay=True,
        )

        leaves_out = [
            SingleLeafOut(
                leaf_id=l.leaf_id,
                area_cm2=l.area_cm2,
                perimeter_cm=l.perimeter_cm,
                length_cm=l.length_cm,
                width_cm=l.width_cm,
                circularity=l.circularity,
                aspect_ratio=l.aspect_ratio,
                centroid_x=l.centroid_x,
                centroid_y=l.centroid_y,
                herbivory=HerbivoryDetail(
                    herbivory_percentage=l.herbivory.herbivory_percentage,
                    consumed_area_cm2=l.herbivory.consumed_area_cm2,
                    reconstructed_intact_area_cm2=l.herbivory.reconstructed_intact_area_cm2,
                    internal_hole_count=l.herbivory.internal_hole_count,
                    internal_holes_area_cm2=l.herbivory.internal_holes_area_cm2,
                    marginal_damage_area_cm2=l.herbivory.marginal_damage_area_cm2,
                ),
            )
            for l in result.leaves
        ]

        scale_resp = CalibrationResponse(
            pixels_per_cm=result.scale_info.pixels_per_cm,
            pixels_per_mm=result.scale_info.pixels_per_mm,
            cm2_per_pixel=result.scale_info.cm2_per_pixel,
            mm2_per_pixel=result.scale_info.mm2_per_pixel,
            marker_detected=result.scale_info.marker_detected,
            method=result.scale_info.method,
            dpi_equivalent=result.scale_info.dpi_equivalent,
            marker_box=list(result.scale_info.marker_box) if result.scale_info.marker_box else None,
        )

        return LeafAnalysisResponse(
            success=True,
            qr_code_tag=result.qr_code_tag,
            total_leaf_area_cm2=result.total_leaf_area_cm2,
            mean_leaf_area_cm2=result.mean_leaf_area_cm2,
            std_leaf_area_cm2=result.std_leaf_area_cm2,
            leaf_count=result.leaf_count,
            mean_length_cm=result.mean_length_cm,
            mean_width_cm=result.mean_width_cm,
            mean_circularity=result.mean_circularity,
            mean_herbivory_pct=result.mean_herbivory_pct,
            is_compound=result.is_compound,
            rachis_detected=result.rachis_detected,
            scale=scale_resp,
            leaves=leaves_out,
            qc_overlay_path=str(qc_path) if qc_path else None,
            processing_time_sec=elapsed,
        )
    finally:
        if temp_path and Path(temp_path).exists():
            try:
                Path(temp_path).unlink()
            except Exception:
                pass


@app.post("/api/v1/analyze/seed", response_model=SeedAnalysisResponse, tags=["Analysis"])
async def analyze_seed(
    file: Optional[UploadFile] = File(None),
    image_path: Optional[str] = Form(None),
    qr_tag_override: Optional[str] = Form(None),
):
    """Analyzes a seed scan: counts seeds, measures length, width, projected area,

    eccentricity, circularity, and detects bruchid beetle emergence holes.
    """
    temp_path = None
    try:
        if file is not None:
            suffix = Path(file.filename or "seed.jpg").suffix or ".jpg"
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                shutil.copyfileobj(file.file, tmp)
                temp_path = tmp.name
            target_input = temp_path
        elif image_path:
            target_input = image_path
            if not Path(target_input).exists():
                raise HTTPException(status_code=400, detail=f"Image file '{target_input}' does not exist.")
        else:
            raise HTTPException(status_code=400, detail="Either 'file' or 'image_path' must be provided.")

        result, qc_path, elapsed = pipeline.process_seed_scan(
            image_input=target_input,
            qr_tag_override=qr_tag_override,
            save_qc_overlay=True,
        )

        seeds_out = [
            SingleSeedOut(
                seed_id=s.seed_id,
                length_mm=s.length_mm,
                width_mm=s.width_mm,
                projected_area_mm2=s.projected_area_mm2,
                perimeter_mm=s.perimeter_mm,
                circularity=s.circularity,
                eccentricity=s.eccentricity,
                aspect_ratio=s.aspect_ratio,
                bruchid_attacked=s.bruchid.is_attacked,
                bruchid_hole_count=s.bruchid.hole_count,
            )
            for s in result.seeds
        ]

        scale_resp = CalibrationResponse(
            pixels_per_cm=result.scale_info.pixels_per_cm,
            pixels_per_mm=result.scale_info.pixels_per_mm,
            cm2_per_pixel=result.scale_info.cm2_per_pixel,
            mm2_per_pixel=result.scale_info.mm2_per_pixel,
            marker_detected=result.scale_info.marker_detected,
            method=result.scale_info.method,
            dpi_equivalent=result.scale_info.dpi_equivalent,
            marker_box=list(result.scale_info.marker_box) if result.scale_info.marker_box else None,
        )

        return SeedAnalysisResponse(
            success=True,
            qr_code_tag=result.qr_code_tag,
            total_seed_count=result.total_seed_count,
            mean_area_mm2=result.mean_area_mm2,
            std_area_mm2=result.std_area_mm2,
            mean_length_mm=result.mean_length_mm,
            std_length_mm=result.std_length_mm,
            mean_width_mm=result.mean_width_mm,
            std_width_mm=result.std_width_mm,
            mean_eccentricity=result.mean_eccentricity,
            mean_circularity=result.mean_circularity,
            attacked_seed_count=result.attacked_seed_count,
            bruchid_attack_rate_pct=result.bruchid_attack_rate_pct,
            scale=scale_resp,
            seeds=seeds_out,
            qc_overlay_path=str(qc_path) if qc_path else None,
            processing_time_sec=elapsed,
        )
    finally:
        if temp_path and Path(temp_path).exists():
            try:
                Path(temp_path).unlink()
            except Exception:
                pass


@app.post("/api/v1/batch", response_model=BatchProcessResponse, tags=["Batch Processing"])
async def batch_process(req: BatchProcessRequest):
    """Processes an entire directory of scanned images in batch."""
    in_dir = Path(req.input_directory)
    if not in_dir.exists() or not in_dir.is_dir():
        raise HTTPException(status_code=400, detail=f"Directory '{req.input_directory}' not found.")

    out_dir = Path(req.output_directory) if req.output_directory else DEFAULT_CONFIG.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]
    files = [f for f in in_dir.iterdir() if f.suffix.lower() in extensions]

    if not files:
        return BatchProcessResponse(
            success=True,
            total_files=0,
            successful_files=0,
            failed_files=0,
            total_elapsed_time_sec=0.0,
            average_speed_per_scan_sec=0.0,
            items=[],
        )

    t0 = time.perf_counter()
    items: List[BatchItemSummary] = []
    success_count = 0
    fail_count = 0

    for f in files:
        f_t0 = time.perf_counter()
        try:
            if req.scan_type == "leaf":
                res, _, el = pipeline.process_leaf_scan(
                    image_input=f,
                    is_compound=req.is_compound,
                    save_qc_overlay=True,
                    output_dir=out_dir / "qc_overlays",
                )
                pipeline.exporter.export_leaf_to_csv(res, out_dir / f"{f.stem}_metrics.csv")
                pipeline.exporter.export_to_json(res, out_dir / f"{f.stem}_data.json")

                items.append(
                    BatchItemSummary(
                        filename=f.name,
                        qr_code_tag=res.qr_code_tag,
                        organ_count=res.leaf_count,
                        main_metric=res.total_leaf_area_cm2,
                        processing_time_sec=el,
                        status="SUCCESS",
                    )
                )
            else:
                res, _, el = pipeline.process_seed_scan(
                    image_input=f,
                    save_qc_overlay=True,
                    output_dir=out_dir / "qc_overlays",
                )
                pipeline.exporter.export_seed_to_csv(res, out_dir / f"{f.stem}_metrics.csv")
                pipeline.exporter.export_to_json(res, out_dir / f"{f.stem}_data.json")

                items.append(
                    BatchItemSummary(
                        filename=f.name,
                        qr_code_tag=res.qr_code_tag,
                        organ_count=res.total_seed_count,
                        main_metric=res.mean_area_mm2,
                        processing_time_sec=el,
                        status="SUCCESS",
                    )
                )
            success_count += 1
        except Exception as e:
            fail_count += 1
            el = time.perf_counter() - f_t0
            items.append(
                BatchItemSummary(
                    filename=f.name,
                    qr_code_tag=None,
                    organ_count=0,
                    main_metric=0.0,
                    processing_time_sec=round(el, 3),
                    status="FAILED",
                    error=str(e),
                )
            )

    total_time = round(time.perf_counter() - t0, 3)
    avg_speed = round(total_time / len(files), 3) if files else 0.0

    return BatchProcessResponse(
        success=True,
        total_files=len(files),
        successful_files=success_count,
        failed_files=fail_count,
        total_elapsed_time_sec=total_time,
        average_speed_per_scan_sec=avg_speed,
        items=items,
    )


@app.post("/api/v1/sync/saheltraits", response_model=SahelTraitsSyncResponse, tags=["SahelTraits-DB"])
async def sync_to_saheltraits(req: SahelTraitsSyncRequest):
    """Synchronizes extracted morphometric traits directly to SahelTraits-DB backend."""
    # Look up individual tree in SahelTraits-DB
    ind = await saheltraits_client.get_individual_by_qr(req.qr_code_tag, token=req.auth_token)
    if not ind:
        return SahelTraitsSyncResponse(
            success=False,
            individual_id=None,
            measurements_created=0,
            traits_synced=[],
            details=f"Tree with QR code tag '{req.qr_code_tag}' not found in SahelTraits-DB.",
        )

    ind_id = ind.get("ind_id")

    # Load results JSON
    json_path = Path(req.results_json_path)
    if not json_path.exists():
        raise HTTPException(status_code=400, detail=f"JSON file '{req.results_json_path}' not found.")

    import json
    with open(json_path, "r", encoding="utf-8") as fp:
        data = json.load(fp)

    scan_type = data.get("type")
    payloads = []

    if scan_type == "LEAF_SCAN":
        payloads.append({
            "ind_id": ind_id,
            "trait_name_ets": "Leaf_Area",
            "trait_value": float(data.get("total_leaf_area_cm2", 0.0)),
            "unit": "cm2",
            "organ_sampled": "Feuille",
            "measurement_protocol": "Standard flatbed 600 DPI scan with automated segmentation",
        })
        payloads.append({
            "ind_id": ind_id,
            "trait_name_ets": "Leaf_Herbivory_Pct",
            "trait_value": float(data.get("mean_herbivory_pct", 0.0)),
            "unit": "%",
            "organ_sampled": "Feuille",
            "measurement_protocol": "Convex hull reconstruction + perforation detection",
        })
    elif scan_type == "SEED_SCAN":
        payloads.append({
            "ind_id": ind_id,
            "trait_name_ets": "Seed_Area_Mean",
            "trait_value": float(data.get("mean_area_mm2", 0.0)),
            "unit": "mm2",
            "organ_sampled": "Graine",
            "measurement_protocol": "Projected seed area",
        })
        payloads.append({
            "ind_id": ind_id,
            "trait_name_ets": "Seed_Bruchid_Attack_Rate",
            "trait_value": float(data.get("bruchid_attack_rate_pct", 0.0)),
            "unit": "%",
            "organ_sampled": "Graine",
            "measurement_protocol": "Automated emergence hole detection",
        })

    created = await saheltraits_client.push_measurements(payloads, token=req.auth_token)
    traits_synced = [p["trait_name_ets"] for p in created]

    return SahelTraitsSyncResponse(
        success=len(created) > 0,
        individual_id=ind_id,
        measurements_created=len(created),
        traits_synced=traits_synced,
        details=f"Synced {len(created)}/{len(payloads)} traits to tree {ind_id}.",
    )


@app.get("/api/v1/qc-image/{filename}", tags=["Quality Control"])
async def get_qc_image(filename: str):
    """Serves the generated quality control overlay image."""
    img_path = DEFAULT_CONFIG.output_dir / "qc_overlays" / filename
    if not img_path.exists():
        raise HTTPException(status_code=404, detail="QC image not found.")
    return FileResponse(img_path, media_type="image/jpeg")
