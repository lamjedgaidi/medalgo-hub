from django.contrib import admin

from .models import Algorithm, Category, Version


class VersionInline(admin.TabularInline):
    model = Version
    extra = 0
    fields = ("version", "line", "tag", "released_on", "diff_summary", "commit_sha")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("label", "kind", "order")
    prepopulated_fields = {}


@admin.register(Algorithm)
class AlgorithmAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "field", "status", "official", "verified", "installs", "rating")
    list_filter = ("status", "category", "field", "official", "verified")
    search_fields = ("name", "slug", "blurb", "author_handle")
    prepopulated_fields = {"slug": ("name",)}
    inlines = [VersionInline]
    fieldsets = (
        (None, {"fields": ("name", "slug", "category", "field", "status")}),
        ("Ownership", {"fields": ("owner", "author_handle", "official", "verified", "license")}),
        ("Content", {"fields": ("blurb", "long_description")}),
        ("Pointers (we host none of these bytes)", {"fields": ("repo_url", "dataset_url", "homepage_url", "docs_url")}),
        ("Declared capabilities", {"fields": ("cap_gpu", "cap_network", "cap_filesystem", "cap_data_access", "hooks", "deps")}),
        ("Community signals", {"fields": ("installs", "rating", "ratings_count")}),
    )


@admin.register(Version)
class VersionAdmin(admin.ModelAdmin):
    list_display = ("algorithm", "version", "line", "tag", "released_on")
    list_filter = ("line", "tag")
    search_fields = ("algorithm__name", "version")
