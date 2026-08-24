
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("following", views.following_view, name="following"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("post", views.post, name="post"),
    path("post/<int:post_id>/edit", views.edit_post, name="edit_post"),
    path("post/<int:post_id>/like", views.toggle_like, name="toggle_like"),
    path("profile/<str:username>", views.profile, name="profile"),
    path(
        "profile/<str:username>/follow",
        views.follow_toggle,
        name="follow_toggle",
    ),
]
