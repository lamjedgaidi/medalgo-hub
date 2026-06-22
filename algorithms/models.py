"""
Core registry model.

Design notes
------------
* We are a *registry + knowledge* layer, not a compute platform. An
  ``Algorithm`` points at where its code and data actually live (a Git repo,
  a Hugging Face dataset). We store metadata and pointers, never the heavy
  bytes and never patient data.
* Capabilities (gpu / network / filesystem / data access) are declared, not
  enforced here — they describe what an algorithm *needs* so the catalogue
  can be filtered and, later, so an execution tier can be gated on them.
* ``license`` is required on every algorithm: we redistribute other people's
  work, so each entry must declare under what terms.
"""

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class Category(models.Model):
    """A kind of plugin (engine, metric, exporter, ...)."""

    class Kind(models.TextChoices):
        ENGINE = "engine", "Engine"
        ARCHITECTURE = "architecture", "Architecture"
        PREPROCESSOR = "preprocessor", "Preprocessor"
        AUGMENTATION = "augmentation", "Augmentation"
        DATASET_ADAPTER = "dataset_adapter", "Dataset Adapter"
        METRIC = "metric", "Metric"
        POSTPROCESSOR = "postprocessor", "Postprocessor"
        EXPORTER = "exporter", "Exporter"
        DOMAIN_PACK = "domain_pack", "Domain Pack"
        VISUALIZER = "visualizer", "Visualizer"
        REPORT = "report", "Report"

    kind = models.CharField(max_length=32, choices=Kind.choices, unique=True)
    label = models.CharField(max_length=64)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name_plural = "categories"
        ordering = ["order", "label"]

    def __str__(self):
        return self.label


class Field(models.TextChoices):
    MEDICAL = "medical", "Medical"
    REMOTE_SENSING = "remote-sensing", "Remote sensing"
    MATERIALS = "materials", "Materials"
    GENERIC = "generic", "Generic"


class FileSystemAccess(models.TextChoices):
    NONE = "none", "None"
    READ_ONLY = "read-only", "Read-only"
    READ_WRITE = "read-write", "Read-write"


class DataAccess(models.TextChoices):
    NONE = "none", "None"
    MASKS_ONLY = "masks-only", "Masks only"
    IMAGES_RO = "images-ro", "Images (read-only)"
    IMAGES_RW = "images-rw", "Images (read-write)"


class Algorithm(models.Model):
    """A published (or draft) algorithm / plugin in the registry."""

    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        IN_REVIEW = "in-review", "In review"
        PUBLISHED = "published", "Published"

    slug = models.SlugField(max_length=80, unique=True)
    name = models.CharField(max_length=120)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="algorithms")
    field = models.CharField(max_length=24, choices=Field.choices, default=Field.GENERIC)

    # Who owns it on the platform; author_handle is the display credit
    # (may differ, e.g. an org handle, and is kept for seed/imported data).
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="algorithms",
    )
    author_handle = models.CharField(max_length=80, blank=True)

    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    official = models.BooleanField(default=False)
    verified = models.BooleanField(default=False)

    # Required: we redistribute other people's work.
    license = models.CharField(max_length=64)

    blurb = models.CharField(max_length=240, help_text="One-line summary for cards.")
    long_description = models.TextField(blank=True, help_text="Markdown. The 'read about it' body.")

    # Pointers — the heavy bytes live elsewhere. We never host them.
    repo_url = models.URLField(blank=True, help_text="Git repo (source of record).")
    dataset_url = models.URLField(blank=True, help_text="Hugging Face / dataset pointer.")
    homepage_url = models.URLField(blank=True)
    docs_url = models.URLField(blank=True)

    # Declared capabilities (filtering + future execution gating).
    cap_gpu = models.BooleanField(default=False)
    cap_network = models.BooleanField(default=False)
    cap_filesystem = models.CharField(
        max_length=16, choices=FileSystemAccess.choices, default=FileSystemAccess.READ_ONLY
    )
    cap_data_access = models.CharField(
        max_length=16, choices=DataAccess.choices, default=DataAccess.NONE
    )

    hooks = models.JSONField(default=list, blank=True, help_text="Lifecycle hook names.")
    deps = models.JSONField(default=list, blank=True, help_text="Dependency specifiers.")

    # Denormalised community signals (cheap to read on list pages).
    installs = models.PositiveIntegerField(default=0)
    rating = models.FloatField(default=0)
    ratings_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-installs", "name"]
        indexes = [
            models.Index(fields=["category", "field"]),
            models.Index(fields=["status"]),
        ]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:80]
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("algorithms:detail", args=[self.slug])

    @property
    def current_version(self):
        return self.versions.filter(line=Version.Line.CURRENT).first() or self.versions.first()

    @property
    def is_paid(self):
        return self.license.lower() == "commercial"


class Version(models.Model):
    """An immutable release of an algorithm, pinned to a source commit."""

    class Line(models.TextChoices):
        CURRENT = "current", "Current"
        STABLE = "", "Stable"
        DEPRECATED = "deprecated", "Deprecated"

    class Tag(models.TextChoices):
        MAJOR = "major", "Major"
        MINOR = "minor", "Minor"
        PATCH = "patch", "Patch"

    algorithm = models.ForeignKey(Algorithm, on_delete=models.CASCADE, related_name="versions")
    version = models.CharField(max_length=32, help_text="Semver, e.g. 1.4.2")
    released_on = models.DateField(null=True, blank=True)
    line = models.CharField(max_length=16, choices=Line.choices, blank=True, default=Line.STABLE)
    tag = models.CharField(max_length=8, choices=Tag.choices, default=Tag.MINOR)

    commit_sha = models.CharField(max_length=64, blank=True, help_text="Immutable source pointer.")
    diff_summary = models.CharField(max_length=64, blank=True, help_text="e.g. +412 -96")
    notes = models.JSONField(default=list, blank=True, help_text="Changelog bullet points.")

    # Compatibility against each core line: {"1.2": "ok|warn|bad", ...}
    compat = models.JSONField(default=dict, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-released_on", "-created_at"]
        constraints = [
            models.UniqueConstraint(fields=["algorithm", "version"], name="unique_algorithm_version"),
        ]

    def __str__(self):
        return f"{self.algorithm.name} {self.version}"
