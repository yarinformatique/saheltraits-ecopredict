import csv
import io
import json
import zipfile
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.individual import Individual
from app.models.site import SitePlot
from app.models.spatial_types import wkt_to_geojson
from app.models.taxonomy import Taxonomy
from app.models.trait import TraitMeasurement


class ExportService:
    """Service d'exportation des données de traits fonctionnels

    conformes aux standards FAIR, ETS v1.0 et Darwin Core Archive (DwC-A).
    """

    @staticmethod
    def query_traits_dataset(
        db: Session,
        species: Optional[str] = None,
        climatic_zone: Optional[str] = None,
        trait_name: Optional[str] = None,
        qc_status: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Requête optimisée extrayant les mesures de traits enrichies des dimensions

        taxonomie, placette spatiale et individu.
        """
        query = (
            db.query(TraitMeasurement, Individual, Taxonomy, SitePlot)
            .join(Individual, TraitMeasurement.ind_id == Individual.ind_id)
            .join(Taxonomy, Individual.taxon_id == Taxonomy.taxon_id)
            .join(SitePlot, Individual.plot_id == SitePlot.plot_id)
        )

        if species:
            query = query.filter(
                (Taxonomy.scientific_name.ilike(f"%{species}%"))
                | (Taxonomy.accepted_name_gbif.ilike(f"%{species}%"))
            )
        if climatic_zone:
            query = query.filter(SitePlot.climatic_zone == climatic_zone)
        if trait_name:
            query = query.filter(TraitMeasurement.trait_name_ets == trait_name)
        if qc_status:
            query = query.filter(TraitMeasurement.qc_flag == qc_status)

        rows = query.all()
        dataset = []

        for meas, ind, taxo, plot in rows:
            geom_tree = wkt_to_geojson(ind.geom_tree)
            coords = (
                geom_tree.get("coordinates")
                if geom_tree and "coordinates" in geom_tree
                else [None, None]
            )
            lon = coords[0] if coords else None
            lat = coords[1] if coords else None

            dataset.append({
                "meas_id": meas.meas_id,
                "ind_id": ind.ind_id,
                "plot_id": plot.plot_id,
                "site_name": plot.site_name,
                "climatic_zone": plot.climatic_zone,
                "elevation_m": plot.elevation_m,
                "taxon_id": taxo.taxon_id,
                "scientific_name": taxo.scientific_name,
                "accepted_name_gbif": taxo.accepted_name_gbif,
                "family": taxo.family,
                "genus": taxo.genus,
                "functional_group": taxo.functional_group,
                "iucn_status": taxo.iucn_status,
                "qr_code_tag": ind.qr_code_tag,
                "dbh_cm": ind.dbh_cm,
                "total_height_m": ind.total_height_m,
                "crown_diameter_m": ind.crown_diameter_m,
                "decimal_longitude": lon,
                "decimal_latitude": lat,
                "trait_name_ets": meas.trait_name_ets,
                "trait_value": meas.trait_value,
                "unit": meas.unit,
                "organ_sampled": meas.organ_sampled,
                "measurement_protocol": meas.measurement_protocol,
                "measurement_date": meas.measurement_date.isoformat()
                if meas.measurement_date
                else None,
                "qc_flag": meas.qc_flag,
                "qc_notes": meas.qc_notes,
            })

        return dataset

    @staticmethod
    def to_csv(dataset: List[Dict[str, Any]]) -> str:
        """Génère un flux CSV standardisé."""
        output = io.StringIO()
        if not dataset:
            return ""

        headers = list(dataset[0].keys())
        writer = csv.DictWriter(output, fieldnames=headers)
        writer.writeheader()
        for row in dataset:
            writer.writerow(row)

        return output.getvalue()

    @staticmethod
    def to_json(dataset: List[Dict[str, Any]]) -> str:
        """Génère un JSON formaté prêt pour l'analyse."""
        return json.dumps(
            {
                "standard": "Ecological Trait-data Standard (ETS v1.0)",
                "total_records": len(dataset),
                "data": dataset,
            },
            indent=2,
            ensure_ascii=False,
        )

    @staticmethod
    def to_dwca_zip(dataset: List[Dict[str, Any]]) -> bytes:
        """Construit une archive zip conforme au standard Darwin Core Archive (DwC-A)

        avec meta.xml, occurrence.txt et l'extension measurementorfact.txt.
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(
            zip_buffer, "w", zipfile.ZIP_DEFLATED
        ) as dwca_archive:
            # 1. meta.xml descriptif de l'archive
            meta_xml = """<?xml version="1.0" encoding="UTF-8"?>
<archive xmlns="http://rs.tdwg.org/dwc/text/" metadata="metadata.xml">
  <core encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\n" ignoreHeaderLines="1" rowType="http://rs.tdwg.org/dwc/terms/Occurrence">
    <files>
      <location>occurrence.txt</location>
    </files>
    <id index="0" />
    <field index="0" term="http://rs.tdwg.org/dwc/terms/occurrenceID"/>
    <field index="1" term="http://rs.tdwg.org/dwc/terms/basisOfRecord"/>
    <field index="2" term="http://rs.tdwg.org/dwc/terms/scientificName"/>
    <field index="3" term="http://rs.tdwg.org/dwc/terms/acceptedNameUsage"/>
    <field index="4" term="http://rs.tdwg.org/dwc/terms/family"/>
    <field index="5" term="http://rs.tdwg.org/dwc/terms/genus"/>
    <field index="6" term="http://rs.tdwg.org/dwc/terms/decimalLongitude"/>
    <field index="7" term="http://rs.tdwg.org/dwc/terms/decimalLatitude"/>
    <field index="8" term="http://rs.tdwg.org/dwc/terms/geodeticDatum"/>
    <field index="9" term="http://rs.tdwg.org/dwc/terms/locality"/>
    <field index="10" term="http://rs.tdwg.org/dwc/terms/eventDate"/>
    <field index="11" term="http://rs.tdwg.org/dwc/terms/organismQuantity"/>
    <field index="12" term="http://rs.tdwg.org/dwc/terms/organismQuantityType"/>
  </core>
  <extension encoding="UTF-8" fieldsTerminatedBy="\\t" linesTerminatedBy="\\n" ignoreHeaderLines="1" rowType="http://rs.tdwg.org/dwc/terms/MeasurementOrFact">
    <files>
      <location>measurementorfact.txt</location>
    </files>
    <coreid index="0" />
    <field index="0" term="http://rs.tdwg.org/dwc/terms/occurrenceID"/>
    <field index="1" term="http://rs.tdwg.org/dwc/terms/measurementID"/>
    <field index="2" term="http://rs.tdwg.org/dwc/terms/measurementType"/>
    <field index="3" term="http://rs.tdwg.org/dwc/terms/measurementValue"/>
    <field index="4" term="http://rs.tdwg.org/dwc/terms/measurementUnit"/>
    <field index="5" term="http://rs.tdwg.org/dwc/terms/measurementMethod"/>
    <field index="6" term="http://rs.tdwg.org/dwc/terms/measurementDeterminedDate"/>
    <field index="7" term="http://rs.tdwg.org/dwc/terms/measurementRemarks"/>
  </extension>
</archive>"""
            dwca_archive.writestr("meta.xml", meta_xml.strip())

            # 2. occurrence.txt (Dédoublonnage par individu / occurrence)
            occurrences_seen = {}
            for row in dataset:
                ind_id = row["ind_id"]
                if ind_id not in occurrences_seen:
                    occurrences_seen[ind_id] = row

            occ_buffer = io.StringIO()
            occ_writer = csv.writer(occ_buffer, delimiter="\t")
            occ_writer.writerow([
                "occurrenceID",
                "basisOfRecord",
                "scientificName",
                "acceptedNameUsage",
                "family",
                "genus",
                "decimalLongitude",
                "decimalLatitude",
                "geodeticDatum",
                "locality",
                "eventDate",
                "organismQuantity",
                "organismQuantityType",
            ])
            for ind_id, row in occurrences_seen.items():
                occ_writer.writerow([
                    row["ind_id"],
                    "LivingSpecimen",
                    row["scientific_name"],
                    row["accepted_name_gbif"] or row["scientific_name"],
                    row["family"],
                    row["genus"],
                    row["decimal_longitude"] or "",
                    row["decimal_latitude"] or "",
                    "WGS84",
                    f"{row['site_name']} ({row['climatic_zone']})",
                    row["measurement_date"] or "",
                    1,
                    "individuals",
                ])
            dwca_archive.writestr("occurrence.txt", occ_buffer.getvalue())

            # 3. measurementorfact.txt (Mesures de traits rattachées)
            fact_buffer = io.StringIO()
            fact_writer = csv.writer(fact_buffer, delimiter="\t")
            fact_writer.writerow([
                "occurrenceID",
                "measurementID",
                "measurementType",
                "measurementValue",
                "measurementUnit",
                "measurementMethod",
                "measurementDeterminedDate",
                "measurementRemarks",
            ])
            for row in dataset:
                fact_writer.writerow([
                    row["ind_id"],
                    row["meas_id"],
                    row["trait_name_ets"],
                    row["trait_value"],
                    row["unit"],
                    row["measurement_protocol"] or "",
                    row["measurement_date"] or "",
                    f"QC_FLAG={row['qc_flag']}; {row['qc_notes'] or ''}",
                ])
            dwca_archive.writestr(
                "measurementorfact.txt", fact_buffer.getvalue()
            )

        zip_buffer.seek(0)
        return zip_buffer.getvalue()
