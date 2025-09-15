from django.contrib import admin
from notes.models import Tag, Technology, Link, Project, ProjectImage


# Register your models here.
class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1


class LinkInline(admin.TabularInline):
    model = Link
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    inlines = [ProjectImageInline, LinkInline]
    list_display = ("name", "priority", "created_at", "updated_at")
    search_fields = ("name", "description", "summary")
    list_filter = ("technologies", "tags")
    ordering = ("-priority", "name")


admin.site.register(Project, ProjectAdmin)
admin.site.register(Tag)
admin.site.register(Technology)
admin.site.register(Link)
