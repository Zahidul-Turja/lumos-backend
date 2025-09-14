from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from notes.models import Tag, Technology, Project
from notes.serializers import (
    TagSerializer,
    TechnologySerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
)


class TagsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        tags = Tag.objects.all()
        serializer = TagSerializer(tags, many=True, context={"request": request})
        return Response(
            {
                "success": True,
                "message": "Tags fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )


class TechnologiesListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        technologies = Technology.objects.all()
        serializer = TechnologySerializer(
            technologies, many=True, context={"request": request}
        )
        return Response(
            {
                "success": True,
                "message": "Technologies fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
