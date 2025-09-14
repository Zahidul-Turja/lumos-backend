from rest_framework import serializers

from notes.models import Tag, Technology, Link, Project, ProjectImage


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["id", "name", "icon", "color"]


class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = ["id", "name", "icon"]


class LinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Link
        fields = ["id", "name", "url", "icon"]


class ProjectImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectImage
        fields = ["id", "image", "caption"]


class ProjectDetailSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)
    tags = TagSerializer(many=True)
    links = LinkSerializer(many=True)
    images = ProjectImageSerializer(many=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "summary",
            "thumbnail",
            "technologies",
            "tags",
            "links",
            "images",
            "priority",
            "created_at",
            "updated_at",
        ]


class ProjectListSerializer(serializers.ModelSerializer):
    technologies = TechnologySerializer(many=True)
    tags = TagSerializer(many=True)

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "summary",
            "thumbnail",
            "technologies",
            "tags",
            "priority",
        ]
