from django.db import models


# Create your models here.
class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.ImageField(upload_to="tag_icons/", blank=True, null=True)
    color = models.CharField(max_length=7, blank=True, null=True)  # Hex color code

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Tags"
        db_table = "tags"


class Technology(models.Model):
    name = models.CharField(max_length=50, unique=True)
    icon = models.ImageField(upload_to="technology_icons/", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Technologies"
        db_table = "technologies"


class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    thumbnail = models.ImageField(
        upload_to="project_thumbnails/", blank=True, null=True
    )

    technologies = models.ManyToManyField(
        Technology, related_name="projects", blank=True
    )
    tags = models.ManyToManyField(Tag, related_name="projects", blank=True)

    priority = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Projects"
        db_table = "projects"
        ordering = ["-priority", "-created_at"]


class Link(models.Model):
    project = models.ForeignKey(Project, related_name="links", on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    url = models.URLField()
    icon = models.ImageField(upload_to="link_icons/", blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Links"
        db_table = "links"


class ProjectImage(models.Model):
    project = models.ForeignKey(
        Project, related_name="images", on_delete=models.CASCADE
    )
    image = models.ImageField(upload_to="project_images/")
    caption = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"Image for {self.project.name}"

    class Meta:
        verbose_name_plural = "Project Images"
        db_table = "project_images"
