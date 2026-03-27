from ui.hanko_helpers import get_mapped_django_user_by_hanko


class HankoUserMapMiddleware:
    """Maps the authenticated Hanko user to request.user so that
    Django's @login_required() decorator works transparently."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'hotosm') and request.hotosm.user:
            django_user = get_mapped_django_user_by_hanko(request.hotosm.user)
            if django_user:
                request.user = django_user
        return self.get_response(request)
