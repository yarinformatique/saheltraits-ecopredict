"""
Data export module for Leaf & Seed Morpho-Analyzer.
Generates CSV, JSON, and SahelTraits-DB formatted measurement payloads.
"""

from dataclasses import asdict
import json
from pathlib import Path
from typing import Any, Dict, List, Union
import pandas as pd

from morpho_vision.leaf_analyzer.analyzer import LeafScanResult
from morpho_vision.seed_analyzer.morphometry import SeedScanResult


class DataExporter:
    """Exports morphometric results to tabular and structured formats."""

    @staticmethod
    def export_leaf_to_csv(result: LeafScanResult, output_path: Union[str, Path]) -> Path:
        """Exports individual leaf metrics and scan summary to CSV."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        rows = []
        for leaf in result.leaves:
            rows.append({
                "qr_code_tag": result.qr_code_tag,
                "leaf_id": leaf.leaf_id,
                "area_cm2": leaf.area_cm2,
                "perimeter_cm": leaf.perimeter_cm,
                "length_cm": leaf.length_cm,
                "width_cm": leaf.width_cm,
                "circularity": leaf.circularity,
                "aspect_ratio": leaf.aspect_ratio,
                "herbivory_pct": leaf.herbivory.herbivory_percentage,
                "consumed_area_cm2": leaf.herbivory.consumed_area_cm2,
                "intact_area_cm2": leaf.herbivory.reconstructed_intact_area_cm2,
                "internal_hole_count": leaf.herbivory.internal_hole_count,
                "centroid_x": leaf.centroid_x,
                "centroid_y": leaf.centroid_y,
                "scale_pixels_per_cm": result.scale_info.pixels_per_cm if result.scale_info else None,
                "scale_method": result.scale_info.method if result.scale_info else None,
            })

        df = pd.DataFrame(rows)
        df.to_csv(out_p, index=False)
        return out_p

    @staticmethod
    def export_seed_to_csv(result: SeedScanResult, output_path: Union[str, Path]) -> Path:
        """Exports individual seed metrics to CSV."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        rows = []
        for seed in result.seeds:
            rows.append({
                "qr_code_tag": result.qr_code_tag,
                "seed_id": seed.seed_id,
                "length_mm": seed.length_mm,
                "width_mm": seed.width_mm,
                "projected_area_mm2": seed.projected_area_mm2,
                "perimeter_mm": seed.perimeter_mm,
                "circularity": seed.circularity,
                "eccentricity": seed.eccentricity,
                "aspect_ratio": seed.aspect_ratio,
                "bruchid_attacked": seed.bruchid.is_attacked,
                "bruchid_hole_count": seed.bruchid.hole_count,
                "centroid_x": seed.centroid_x,
                "centroid_y": seed.centroid_y,
                "scale_pixels_per_mm": result.scale_info.pixels_per_mm if result.scale_info else None,
            })

        df = pd.DataFrame(rows)
        df.to_csv(out_p, index=False)
        return out_p

    @staticmethod
    def export_to_json(
        result: Union[LeafScanResult, SeedScanResult],
        output_path: Union[str, Path],
    ) -> Path:
        """Exports comprehensive structured results to JSON."""
        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)

        if isinstance(result, LeafScanResult):
            data: Dict[str, Any] = {
                "type": "LEAF_SCAN",
                "qr_code_tag": result.qr_code_tag,
                "leaf_count": result.leaf_count,
                "total_leaf_area_cm2": result.total_leaf_area_cm2,
                "mean_leaf_area_cm2": result.mean_leaf_area_cm2,
                "std_leaf_area_cm2": result.std_leaf_area_cm2,
                "mean_length_cm": result.mean_length_cm,
                "mean_width_cm": result.mean_width_cm,
                "mean_circularity": result.mean_circularity,
                "mean_herbivory_pct": result.mean_herbivory_pct,
                "is_compound": result.is_compound,
                "scale": {
                    "pixels_per_cm": result.scale_info.pixels_per_cm if result.scale_info else None,
                    "method": result.scale_info.method if result.scale_info else None,
                },
                "leaves": [
                    {
                        "leaf_id": l.leaf_id,
                        "area_cm2": l.area_cm2,
                        "perimeter_cm": l.perimeter_cm,
                        "length_cm": l.length_cm,
                        "width_cm": l.width_cm,
                        "circularity": l.circularity,
                        "aspect_ratio": l.aspect_ratio,
                        "herbivory_pct": l.herbivory.herbivory_percentage,
                        "consumed_area_cm2": l.herbivory.consumed_area_cm2,
                        "intact_area_cm2": l.herbivory.reconstructed_intact_area_cm2,
                        "hole_count": l.herbivory.internal_hole_count,
                    }
                    for l in result.leaves
                ],
            }
        else:
            data = {
                "type": "SEED_SCAN",
                "qr_code_tag": result.qr_code_tag,
                "total_seed_count": result.total_seed_count,
                "mean_area_mm2": result.mean_area_mm2,
                "std_area_mm2": result.std_area_mm2,
                "mean_length_mm": result.mean_length_mm,
                "std_length_mm": result.std_length_mm,
                "mean_width_mm": result.mean_width_mm,
                "std_width_mm": result.std_width_mm,
                "mean_eccentricity": result.mean_eccentricity,
                "mean_circularity": result.mean_circularity,
                "attacked_seed_count": result.attacked_seed_count,
                "bruchid_attack_rate_pct": result.bruchid_attack_rate_pct,
                "scale": {
                    "pixels_per_mm": result.scale_info.pixels_per_mm if result.scale_info else None,
                    "method": result.scale_info.method if result.scale_info else None,
                },
                "seeds": [
                    {
                        "seed_id": s.seed_id,
                        "length_mm": s.length_mm,
                        "width_mm": s.width_mm,
                        "projected_area_mm2": s.projected_area_mm2,
                        "perimeter_mm": s.perimeter_mm,
                        "circularity": s.circularity,
                        "eccentricity": s.eccentricity,
                        "aspect_ratio": s.aspect_ratio,
                        "bruchid_attacked": s.bruchid.is_attacked,
                        "hole_count": s.bruchid.hole_count,
                    }
                    for s in result.seeds
                ],
            }

        with open(out_p, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        return out_p

    @staticmethod
    def to_saheltraits_payloads(
        result: Union[LeafScanResult, SeedScanResult],
        ind_id: str,
        instrument_id: str = "SCANNER_600DPI_MORPHOVISION_V1",
    ) -> List[Dict[str, Any]]:
        """Converts results into list of SahelTraits-DB TraitMeasurementCreate payloads."""
        payloads = []

        if isinstance(result, LeafScanResult):
            # 1. Total Leaf Area
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Leaf_Area",
                "trait_value": result.total_leaf_area_cm2,
                "unit": "cm2",
                "organ_sampled": "Feuille",
                "measurement_protocol": "Standard flatbed scan at 600 DPI, automated segmentation with MorphoVision V1",
                "instrument_id": instrument_id,
            })
            # 2. Mean Unitary Leaf Area
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Leaf_Area_Mean",
                "trait_value": result.mean_leaf_area_cm2,
                "unit": "cm2",
                "organ_sampled": "Feuille",
                "measurement_protocol": "Mean individual leaf lamina area",
                "instrument_id": instrument_id,
            })
            # 3. Leaf Length
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Leaf_Length",
                "trait_value": result.mean_length_cm,
                "unit": "cm",
                "organ_sampled": "Feuille",
                "measurement_protocol": "Feret maximum length",
                "instrument_id": instrument_id,
            })
            # 4. Leaf Width
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Leaf_Width",
                "trait_value": result.mean_width_cm,
                "unit": "cm",
                "organ_sampled": "Feuille",
                "measurement_protocol": "Feret minimum width perpendicular to length",
                "instrument_id": instrument_id,
            })
            # 5. Herbivory damage %
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Leaf_Herbivory_Pct",
                "trait_value": result.mean_herbivory_pct,
                "unit": "%",
                "organ_sampled": "Feuille",
                "measurement_protocol": "Reconstructed convex hull missing area + internal chewing perforations",
                "instrument_id": instrument_id,
            })
        else:
            # Seed measurements
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Seed_Lot_Count",
                "trait_value": float(result.total_seed_count),
                "unit": "count",
                "organ_sampled": "Graine",
                "measurement_protocol": "Automated watershed seed lot counting",
                "instrument_id": instrument_id,
            })
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Seed_Area_Mean",
                "trait_value": result.mean_area_mm2,
                "unit": "mm2",
                "organ_sampled": "Graine",
                "measurement_protocol": "Projected seed surface area",
                "instrument_id": instrument_id,
            })
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Seed_Length_Mean",
                "trait_value": result.mean_length_mm,
                "unit": "mm",
                "organ_sampled": "Graine",
                "measurement_protocol": "Major axis / Feret max",
                "instrument_id": instrument_id,
            })
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Seed_Width_Mean",
                "trait_value": result.mean_width_mm,
                "unit": "mm",
                "organ_sampled": "Graine",
                "measurement_protocol": "Minor axis / Feret min",
                "instrument_id": instrument_id,
            })
            payloads.append({
                "ind_id": ind_id,
                "trait_name_ets": "Seed_Bruchid_Attack_Rate",
                "trait_value": result.bruchid_attack_rate_pct,
                "unit": "%",
                "organ_sampled": "Graine",
                "measurement_protocol": "Automated circular emergence hole detection (0.8-3.5mm)",
                "instrument_id": instrument_id,
            })

        return payloads
