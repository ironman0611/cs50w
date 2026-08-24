from .models import College


def college_nav(request):
    if not request.user.is_authenticated:
        return {}
    return {
        "nav_colleges": College.objects.order_by("name"),
    }
