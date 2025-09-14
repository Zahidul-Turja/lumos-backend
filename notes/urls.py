from django.urls import path
from notes import views

notes_url_patterns = [
    path("tags/", views.TagsListView.as_view(), name="tags-list"),
    path(
        "technologies/", views.TechnologiesListView.as_view(), name="technologies-list"
    ),
]
