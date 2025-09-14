from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination

from notes.models import Tag, Technology, Project
from notes.serializers import (
    TagSerializer,
    TechnologySerializer,
    ProjectListSerializer,
    ProjectDetailSerializer,
)


class Pagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


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


class ProjectsListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        projects = Project.objects.all().order_by("-priority", "-created_at")
        pagination = Pagination()
        paginated_projects = pagination.paginate_queryset(projects, request)
        serializer = ProjectListSerializer(
            paginated_projects, many=True, context={"request": request}
        )

        return Response(
            {
                "success": True,
                "message": "Projects fetched successfully",
                "data": pagination.get_paginated_response(serializer.data).data,
            },
            status=status.HTTP_200_OK,
        )


class ProjectDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, id):
        try:
            project = Project.objects.get(id=id)
        except Project.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Project not found",
                    "data": None,
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ProjectDetailSerializer(project, context={"request": request})
        return Response(
            {
                "success": True,
                "message": "Project fetched successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
