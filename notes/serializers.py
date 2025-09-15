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


class ProjectCreateSerializer(serializers.ModelSerializer):
    technologies = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Technology.objects.all(), write_only=True, required=False
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), write_only=True, required=False
    )

    # Representation (for response)
    technologies_list = serializers.StringRelatedField(
        many=True, source="technologies", read_only=True
    )
    tags_list = serializers.StringRelatedField(many=True, source="tags", read_only=True)

    links = serializers.ListField(
        child=serializers.DictField(), write_only=True, required=False
    )
    images = serializers.ListField(
        child=serializers.ImageField(), write_only=True, required=False
    )

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "summary",
            "thumbnail",
            "priority",
            "technologies",  # write-only
            "tags",  # write-only
            "technologies_list",  # read-only
            "tags_list",  # read-only
            "links",
            "images",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def create(self, validated_data):
        links_data = validated_data.pop("links", [])
        images_data = validated_data.pop("images", [])
        technologies = validated_data.pop("technologies", [])
        tags = validated_data.pop("tags", [])

        project = Project.objects.create(**validated_data)
        project.technologies.set(technologies)
        project.tags.set(tags)

        # Create related links
        for link in links_data:
            Link.objects.create(
                project=project,
                name=link.get("name"),
                url=link.get("url"),
                icon=link.get("icon", None),
            )

        # Create related images
        for image in images_data:
            ProjectImage.objects.create(project=project, image=image)

        return project
