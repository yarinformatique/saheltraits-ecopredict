"""
Command Line Interface (CLI) for LEAF & SEED MORPHO-ANALYZER.
Provides commands for single-file processing, batch execution, calibration validation,
and starting the FastAPI microservice.
"""

import argparse
from pathlib import Path
import sys
import time
import uvicorn

from morpho_vision.calibration.calibrator import ScaleCalibrator
from morpho_vision.config import DEFAULT_CONFIG
from morpho_vision.pipeline import MorphoVisionPipeline


def main():
    parser = argparse.ArgumentParser(
        prog="morpho-vision",
        description="Leaf & Seed Morpho-Analyzer — Computer Vision Pipeline (Thèse Doctorat 2026-2029)",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available subcommands")

    # Command: leaf
    leaf_p = subparsers.add_parser("leaf", help="Analyze a leaf scan image")
    leaf_p.add_argument("--input", "-i", required=True, help="Path to scanned image")
    leaf_p.add_argument("--output-dir", "-o", default="data/output", help="Output directory")
    leaf_p.add_argument("--compound", "-c", action="store_true", help="Enable leaflet separation for compound leaves")
    leaf_p.add_argument("--qr-tag", help="Override tree QR code tag")
    leaf_p.add_argument("--no-overlay", action="store_true", help="Disable QC overlay generation")

    # Command: seed
    seed_p = subparsers.add_parser("seed", help="Analyze a seed scan image")
    seed_p.add_argument("--input", "-i", required=True, help="Path to scanned image")
    seed_p.add_argument("--output-dir", "-o", default="data/output", help="Output directory")
    seed_p.add_argument("--qr-tag", help="Override tree QR code tag")
    seed_p.add_argument("--no-overlay", action="store_true", help="Disable QC overlay generation")

    # Command: batch
    batch_p = subparsers.add_parser("batch", help="Batch process a directory of scans")
    batch_p.add_argument("--input-dir", "-i", required=True, help="Input directory containing scan images")
    batch_p.add_argument("--output-dir", "-o", default="data/output", help="Output directory")
    batch_p.add_argument("--type", "-t", choices=["leaf", "seed"], default="leaf", help="Organ type")
    batch_p.add_argument("--compound", "-c", action="store_true", help="Enable leaflet separation for compound leaves")

    # Command: calibrate
    calib_p = subparsers.add_parser("calibrate", help="Test calibration marker detection")
    calib_p.add_argument("--input", "-i", required=True, help="Path to image")
    calib_p.add_argument("--known-area", "-a", type=float, default=4.0, help="Known marker area in cm2 (default 4.0)")

    # Command: server
    srv_p = subparsers.add_parser("server", help="Start the FastAPI microservice")
    srv_p.add_argument("--host", default="0.0.0.0", help="Host IP (default 0.0.0.0)")
    srv_p.add_argument("--port", "-p", type=int, default=8001, help="Port (default 8001)")
    srv_p.add_argument("--reload", action="store_true", help="Enable live code reload")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    pipeline = MorphoVisionPipeline(DEFAULT_CONFIG)

    if args.command == "leaf":
        print(f"[*] Processing leaf scan: {args.input}")
        res, qc_path, elapsed = pipeline.process_leaf_scan(
            image_input=args.input,
            is_compound=args.compound,
            qr_tag_override=args.qr_tag,
            save_qc_overlay=not args.no_overlay,
            output_dir=Path(args.output_dir) / "qc_overlays",
        )
        out_dir = Path(args.output_dir)
        csv_p = pipeline.exporter.export_leaf_to_csv(res, out_dir / f"{Path(args.input).stem}_metrics.csv")
        json_p = pipeline.exporter.export_to_json(res, out_dir / f"{Path(args.input).stem}_data.json")

        print("=" * 60)
        print("LEAF MORPHOMETRIC EXTRACTION COMPLETED")
        print("=" * 60)
        print(f"QR Code Tag        : {res.qr_code_tag or 'None (Untagged)'}")
        print(f"Leaf / Leaflet Count: {res.leaf_count}")
        print(f"Total Leaf Area    : {res.total_leaf_area_cm2} cm2")
        print(f"Mean Unit Leaf Area: {res.mean_leaf_area_cm2} cm2 (+/- {res.std_leaf_area_cm2})")
        print(f"Mean Length        : {res.mean_length_cm} cm | Mean Width: {res.mean_width_cm} cm")
        print(f"Mean Circularity   : {res.mean_circularity}")
        print(f"Herbivory Lost Area: {res.mean_herbivory_pct}%")
        print(f"Scale Calibration  : {res.scale_info.pixels_per_cm:.2f} px/cm ({res.scale_info.method})")
        print(f"Processing Time    : {elapsed} seconds (< 2s acceptance threshold)")
        print(f"CSV Export         : {csv_p}")
        print(f"JSON Export        : {json_p}")
        if qc_path:
            print(f"QC Overlay Image   : {qc_path}")
        print("=" * 60)

    elif args.command == "seed":
        print(f"[*] Processing seed scan: {args.input}")
        res, qc_path, elapsed = pipeline.process_seed_scan(
            image_input=args.input,
            qr_tag_override=args.qr_tag,
            save_qc_overlay=not args.no_overlay,
            output_dir=Path(args.output_dir) / "qc_overlays",
        )
        out_dir = Path(args.output_dir)
        csv_p = pipeline.exporter.export_seed_to_csv(res, out_dir / f"{Path(args.input).stem}_metrics.csv")
        json_p = pipeline.exporter.export_to_json(res, out_dir / f"{Path(args.input).stem}_data.json")

        print("=" * 60)
        print("SEED MORPHOMETRIC EXTRACTION COMPLETED")
        print("=" * 60)
        print(f"QR Code Tag        : {res.qr_code_tag or 'None (Untagged)'}")
        print(f"Total Seed Count   : {res.total_seed_count}")
        print(f"Mean Projected Area: {res.mean_area_mm2} mm2 (+/- {res.std_area_mm2})")
        print(f"Mean Length (L)    : {res.mean_length_mm} mm (+/- {res.std_length_mm})")
        print(f"Mean Width (l)     : {res.mean_width_mm} mm (+/- {res.std_width_mm})")
        print(f"Mean Eccentricity  : {res.mean_eccentricity} | Circularity: {res.mean_circularity}")
        print(f"Bruchid Predation  : {res.bruchid_attack_rate_pct}% ({res.attacked_seed_count} attacked)")
        print(f"Scale Calibration  : {res.scale_info.pixels_per_mm:.2f} px/mm ({res.scale_info.method})")
        print(f"Processing Time    : {elapsed} seconds (< 2s acceptance threshold)")
        print(f"CSV Export         : {csv_p}")
        print(f"JSON Export        : {json_p}")
        if qc_path:
            print(f"QC Overlay Image   : {qc_path}")
        print("=" * 60)

    elif args.command == "batch":
        in_dir = Path(args.input_dir)
        out_dir = Path(args.output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        extensions = [".jpg", ".jpeg", ".png", ".tif", ".tiff"]
        files = [f for f in in_dir.iterdir() if f.suffix.lower() in extensions]
        print(f"[*] Starting batch processing: {len(files)} scan files found in {in_dir}")

        t0 = time.perf_counter()
        success = 0
        for idx, f in enumerate(files, start=1):
            try:
                if args.type == "leaf":
                    res, _, el = pipeline.process_leaf_scan(
                        image_input=f,
                        is_compound=args.compound,
                        save_qc_overlay=True,
                        output_dir=out_dir / "qc_overlays",
                    )
                    pipeline.exporter.export_leaf_to_csv(res, out_dir / f"{f.stem}_metrics.csv")
                    print(f"[{idx}/{len(files)}] {f.name}: {res.leaf_count} leaves, {res.total_leaf_area_cm2} cm2 in {el}s")
                else:
                    res, _, el = pipeline.process_seed_scan(
                        image_input=f,
                        save_qc_overlay=True,
                        output_dir=out_dir / "qc_overlays",
                    )
                    pipeline.exporter.export_seed_to_csv(res, out_dir / f"{f.stem}_metrics.csv")
                    print(f"[{idx}/{len(files)}] {f.name}: {res.total_seed_count} seeds in {el}s")
                success += 1
            except Exception as e:
                print(f"[{idx}/{len(files)}] ERROR on {f.name}: {e}")

        total_time = round(time.perf_counter() - t0, 3)
        avg_speed = round(total_time / len(files), 3) if files else 0.0
        print("=" * 60)
        print(f"Batch completed: {success}/{len(files)} files succeeded in {total_time}s (Avg: {avg_speed}s/scan)")
        print("=" * 60)

    elif args.command == "calibrate":
        import cv2
        import numpy as np
        data = np.fromfile(args.input, dtype=np.uint8)
        img = cv2.imdecode(data, cv2.IMREAD_COLOR)
        calibrator = ScaleCalibrator(DEFAULT_CONFIG.calibration)
        calib = calibrator.calibrate(img, known_area_cm2=args.known_area)
        print(f"Calibration Result for {args.input}:")
        print(f"  Method           : {calib.method}")
        print(f"  Marker Detected  : {calib.marker_detected}")
        print(f"  Pixels per cm    : {calib.pixels_per_cm:.2f}")
        print(f"  Pixels per mm    : {calib.pixels_per_mm:.2f}")
        print(f"  DPI Equivalent   : {calib.dpi_equivalent:.1f}")
        if calib.marker_box:
            print(f"  Marker Box       : {calib.marker_box}")

    elif args.command == "server":
        print(f"[*] Starting Leaf & Seed Morpho-Analyzer FastAPI service on {args.host}:{args.port}")
        uvicorn.run("morpho_vision.api.main:app", host=args.host, port=args.port, reload=args.reload)


if __name__ == "__main__":
    main()
