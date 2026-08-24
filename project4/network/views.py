from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse

from .models import Post, User


def paginate_posts(request, posts_queryset):
    paginator = Paginator(posts_queryset, 10)
    page_number = request.GET.get("page")
    return paginator.get_page(page_number)


def build_post_context(request, posts, page_heading):
    liked_post_ids = set()
    if request.user.is_authenticated:
        liked_post_ids = set(
            request.user.liked_posts.filter(pk__in=[post.pk for post in posts])
            .values_list("pk", flat=True)
        )
    return {
        "posts": posts,
        "page_heading": page_heading,
        "liked_post_ids": liked_post_ids,
        "show_new_post_form": False,
    }


def index(request):
    posts = paginate_posts(request, Post.objects.order_by("-timestamp").all())
    context = build_post_context(request, posts, "All Posts")
    context["show_new_post_form"] = request.user.is_authenticated
    return render(request, "network/index.html", context)


@login_required
def following_view(request):
    following_ids = request.user.following.values_list("pk", flat=True)
    posts = paginate_posts(
        request,
        Post.objects.filter(user_id__in=following_ids)
        .select_related("user")
        .order_by("-timestamp"),
    )
    context = build_post_context(request, posts, "Following")
    context["show_new_post_form"] = False
    return render(request, "network/index.html", context)


def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    posts = paginate_posts(
        request, Post.objects.filter(user=profile_user).order_by("-timestamp")
    )
    follower_count = profile_user.followers.count()
    following_count = profile_user.following.count()
    show_follow_button = (
        request.user.is_authenticated and request.user != profile_user
    )
    is_following = (
        request.user.is_authenticated
        and show_follow_button
        and request.user.following.filter(pk=profile_user.pk).exists()
    )
    return render(
        request,
        "network/profile.html",
        {
            "profile_user": profile_user,
            "posts": posts,
            "liked_post_ids": set(
                request.user.liked_posts.filter(pk__in=[post.pk for post in posts])
                .values_list("pk", flat=True)
            )
            if request.user.is_authenticated
            else set(),
            "follower_count": follower_count,
            "following_count": following_count,
            "show_follow_button": show_follow_button,
            "is_following": is_following,
        },
    )


@login_required
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return HttpResponseRedirect(reverse("profile", args=[username]))
    if request.method == "POST":
        if request.user.following.filter(pk=target.pk).exists():
            request.user.following.remove(target)
        else:
            request.user.following.add(target)
    return HttpResponseRedirect(reverse("profile", args=[username]))


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

@login_required
def post(request):
    if request.method == "POST":
        content = request.POST["content"]
        Post.objects.create(content=content, user=request.user)
    return HttpResponseRedirect(reverse("index"))


@login_required
def edit_post(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    post = get_object_or_404(Post, pk=post_id)
    if post.user != request.user:
        return JsonResponse({"error": "Forbidden."}, status=403)

    content = request.POST.get("content", "").strip()
    if not content:
        return JsonResponse({"error": "Content cannot be empty."}, status=400)

    post.content = content
    post.save()
    return JsonResponse({"message": "Post updated.", "content": post.content})


@login_required
def toggle_like(request, post_id):
    if request.method != "POST":
        return JsonResponse({"error": "POST required."}, status=405)

    post = get_object_or_404(Post, pk=post_id)
    if post.liked_by.filter(pk=request.user.pk).exists():
        post.liked_by.remove(request.user)
        liked = False
    else:
        post.liked_by.add(request.user)
        liked = True

    return JsonResponse({"liked": liked, "like_count": post.liked_by.count()})