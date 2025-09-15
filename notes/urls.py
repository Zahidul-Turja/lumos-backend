from django.urls import path
from notes import views

notes_url_patterns = [
    path("tags/", views.TagsListView.as_view(), name="tags-list"),
    path(
        "technologies/", views.TechnologiesListView.as_view(), name="technologies-list"
    ),
    path("projects/", views.ProjectsListView.as_view(), name="projects-list"),
    path("projects/create/", views.ProjectCreateView.as_view(), name="project-create"),
    path(
        "projects/<int:pk>/", views.ProjectDetailView.as_view(), name="project-detail"
    ),
]
