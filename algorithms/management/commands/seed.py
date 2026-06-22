"""
Seed the registry with categories and a few representative algorithms
transcribed from the MedAlgo Hub prototype dataset.

    python manage.py seed

Idempotent: re-running updates existing rows by slug/kind.
"""

import datetime as dt

from django.core.management.base import BaseCommand

from algorithms.models import Algorithm, Category, Version

CATEGORIES = [
    ("engine", "Engines", "Segmentation backbones. Swap nnU-Net for an alternative pipeline.", 0),
    ("architecture", "Architectures", "Model topologies that run inside an engine.", 1),
    ("preprocessor", "Preprocessors", "Data transforms applied before training.", 2),
    ("augmentation", "Augmentations", "Training-time augmentation strategies.", 3),
    ("dataset_adapter", "Dataset Adapters", "Ingest data sources & formats (DICOM, OME-TIFF, GeoTIFF).", 4),
    ("metric", "Metrics", "Evaluation measures and clinical scores.", 5),
    ("postprocessor", "Postprocessors", "Mask refinement after inference.", 6),
    ("exporter", "Exporters", "Output targets — DICOM-SEG, STL, RT-STRUCT.", 7),
    ("domain_pack", "Domain Packs", "Bundled plugins + courses for a field.", 8),
    ("visualizer", "Visualizers", "UI overlays — 3D render, uncertainty heatmaps.", 9),
    ("report", "Reports", "Generated documents and structured reports.", 10),
]

# A representative slice of the prototype's EXT catalogue across categories,
# fields and capability classes.
ALGORITHMS = [
    {
        "slug": "nnunet-core", "name": "nnU-Net", "kind": "engine", "field": "medical",
        "author_handle": "segmentforge", "official": True, "verified": True, "license": "Apache-2.0",
        "installs": 48210, "rating": 4.9, "ratings_count": 612,
        "blurb": "The self-configuring reference engine. Fingerprints a dataset and derives the full training plan automatically.",
        "long_description": "nnU-Net analyses your dataset's fingerprint (spacing, intensity distribution, shapes) and self-configures preprocessing, network topology and the training recipe — no manual tuning.",
        "cap_gpu": True, "cap_network": False, "cap_filesystem": "read-write", "cap_data_access": "images-rw",
        "hooks": ["on_fingerprint", "on_plan", "on_train_start", "on_epoch_end", "after_infer"],
        "deps": ["torch>=2.1", "numpy>=1.24", "SimpleITK>=2.3"],
        "versions": [
            {"version": "1.4.2", "released_on": "2026-05-18", "line": "current", "tag": "patch", "diff_summary": "+412 -96", "compat": {"1.2": "warn", "1.3": "ok", "1.4": "ok"}, "notes": ["Fix: planner OOM on >1k-slice CT volumes", "Deterministic seeding across DDP ranks"]},
            {"version": "1.4.0", "released_on": "2026-04-02", "line": "", "tag": "minor", "diff_summary": "+3.1k -880", "compat": {"1.2": "warn", "1.3": "ok", "1.4": "ok"}, "notes": ["Residual encoder presets (M/L/XL)", "2x faster fingerprinting"]},
            {"version": "1.2.0", "released_on": "2025-09-14", "line": "deprecated", "tag": "major", "diff_summary": "+12k", "compat": {"1.2": "ok", "1.3": "bad", "1.4": "bad"}, "notes": ["Initial platform-wrapped release"]},
        ],
    },
    {
        "slug": "swin-unetr", "name": "Swin UNETR", "kind": "architecture", "field": "medical",
        "author_handle": "project-monai", "verified": True, "license": "Apache-2.0",
        "installs": 8330, "rating": 4.5, "ratings_count": 174,
        "blurb": "Shifted-window transformer encoder with a CNN decoder. Robust pretraining.",
        "long_description": "Hierarchical shifted-window transformer encoder paired with a convolutional decoder; ships with self-supervised pretrained weights.",
        "cap_gpu": True, "cap_network": False, "cap_filesystem": "read-only", "cap_data_access": "images-ro",
        "hooks": ["on_plan_override"], "deps": ["torch>=2.1", "monai>=1.3"],
        "versions": [
            {"version": "1.3.2", "released_on": "2026-05-01", "line": "current", "tag": "patch", "diff_summary": "+300 -90", "compat": {"1.2": "warn", "1.3": "ok", "1.4": "ok"}, "notes": ["48-feature preset", "BTCV pretrained weights"]},
        ],
    },
    {
        "slug": "surface-dice", "name": "Surface Dice", "kind": "metric", "field": "medical",
        "author_handle": "jane.doe", "verified": True, "license": "Apache-2.0",
        "installs": 14200, "rating": 4.8, "ratings_count": 330,
        "blurb": "Boundary-aware overlap at a tolerance band. The clinician's metric.",
        "long_description": "Computes the surface Dice coefficient at a configurable tolerance (mm), rewarding boundary accuracy rather than bulk overlap. Reads masks only — never sees raw images.",
        "cap_gpu": False, "cap_network": False, "cap_filesystem": "read-only", "cap_data_access": "masks-only",
        "hooks": ["on_metric_compute"], "deps": ["numpy>=1.24", "scipy>=1.10"],
        "versions": [
            {"version": "1.2.0", "released_on": "2026-05-12", "line": "current", "tag": "minor", "diff_summary": "+120 -60", "compat": {"1.2": "ok", "1.3": "ok", "1.4": "ok"}, "notes": ["Vectorised distance transform (4x faster)", "Per-class tolerance support"]},
        ],
    },
    {
        "slug": "z-norm", "name": "Percentile Z-Norm", "kind": "preprocessor", "field": "generic",
        "author_handle": "segmentforge", "official": True, "verified": True, "license": "Apache-2.0",
        "installs": 21300, "rating": 4.7, "ratings_count": 402,
        "blurb": "Clip to percentile window, then z-score. The default intensity normalizer.",
        "long_description": "Clips intensities to a percentile window then applies z-score normalization. A safe default for most modalities.",
        "cap_gpu": False, "cap_network": False, "cap_filesystem": "read-only", "cap_data_access": "images-ro",
        "hooks": ["before_preprocess"], "deps": ["numpy>=1.24"],
        "versions": [
            {"version": "1.0.3", "released_on": "2026-05-02", "line": "current", "tag": "patch", "diff_summary": "+18 -6", "compat": {"1.2": "ok", "1.3": "ok", "1.4": "ok"}, "notes": ["NaN-safe percentiles"]},
        ],
    },
    {
        "slug": "geotiff-in", "name": "GeoTIFF Adapter", "kind": "dataset_adapter", "field": "remote-sensing",
        "author_handle": "terrasense", "verified": True, "license": "MIT",
        "installs": 1280, "rating": 4.1, "ratings_count": 33,
        "blurb": "Read multi-band GeoTIFF tiles for landcover segmentation.",
        "long_description": "Reads multi-band GeoTIFF tiles with windowed access — proof the core is field-agnostic beyond medical imaging.",
        "cap_gpu": False, "cap_network": False, "cap_filesystem": "read-only", "cap_data_access": "images-ro",
        "hooks": ["on_ingest"], "deps": ["rasterio>=1.3", "numpy>=1.24"],
        "versions": [
            {"version": "0.4.0", "released_on": "2026-03-15", "line": "current", "tag": "minor", "diff_summary": "+80", "compat": {"1.2": "ok", "1.3": "ok", "1.4": "ok"}, "notes": ["Windowed reads"]},
        ],
    },
    {
        "slug": "dicom-seg-out", "name": "DICOM-SEG Exporter", "kind": "exporter", "field": "medical",
        "author_handle": "segmentforge", "official": True, "verified": True, "license": "Apache-2.0",
        "installs": 8800, "rating": 4.6, "ratings_count": 160,
        "blurb": "Write masks back as standards-compliant DICOM-SEG.",
        "long_description": "Exports inference masks as standards-compliant DICOM Segmentation objects with segment colour presets.",
        "cap_gpu": False, "cap_network": False, "cap_filesystem": "read-write", "cap_data_access": "masks-only",
        "hooks": ["on_export"], "deps": ["pydicom>=2.4", "highdicom>=0.22"],
        "versions": [
            {"version": "1.3.0", "released_on": "2026-04-30", "line": "current", "tag": "minor", "diff_summary": "+90 -20", "compat": {"1.2": "ok", "1.3": "ok", "1.4": "ok"}, "notes": ["Segment color presets"]},
        ],
    },
]


class Command(BaseCommand):
    help = "Seed categories and representative algorithms from the prototype dataset."

    def handle(self, *args, **options):
        cats = {}
        for kind, label, desc, order in CATEGORIES:
            cat, _ = Category.objects.update_or_create(
                kind=kind, defaults={"label": label, "description": desc, "order": order}
            )
            cats[kind] = cat
        self.stdout.write(self.style.SUCCESS(f"Categories: {len(cats)}"))

        for spec in ALGORITHMS:
            versions = spec.pop("versions", [])
            kind = spec.pop("kind")
            algo, _ = Algorithm.objects.update_or_create(
                slug=spec["slug"],
                defaults={
                    **spec,
                    "category": cats[kind],
                    "status": Algorithm.Status.PUBLISHED,
                    "repo_url": f"https://github.com/segmentforge/{spec['slug']}",
                },
            )
            for v in versions:
                Version.objects.update_or_create(
                    algorithm=algo,
                    version=v["version"],
                    defaults={
                        "released_on": dt.date.fromisoformat(v["released_on"]),
                        "line": v["line"],
                        "tag": v["tag"],
                        "diff_summary": v["diff_summary"],
                        "compat": v["compat"],
                        "notes": v["notes"],
                    },
                )
        self.stdout.write(self.style.SUCCESS(f"Algorithms: {len(ALGORITHMS)}"))
        self.stdout.write(self.style.SUCCESS("Seed complete."))
