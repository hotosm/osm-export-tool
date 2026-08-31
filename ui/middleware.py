from ui.hanko_helpers import get_mapped_django_user_by_hanko, is_hanko_admin


class HankoUserMapMiddleware:
    """Maps the authenticated Hanko user to request.user so that
    Django's @login_required() decorator works transparently.
    Also grants admin rights from ADMIN_EMAILS."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if hasattr(request, 'hotosm') and request.hotosm.user:
            django_user = get_mapped_django_user_by_hanko(request.hotosm.user)
            if django_user:
                is_admin = is_hanko_admin(request.hotosm.user.email)
                django_user.is_superuser = is_admin
                # Django's admin gates on is_staff, not is_superuser, so setting
                # only the latter produced an account holding every permission
                # that the admin still turned away: the navbar showed the Admin
                # entry (it checks auth.add_user) and the link bounced through
                # /admin/login/ back to the home page with nothing explaining why.
                # Keep any is_staff already granted in the database — five users
                # have it without being superusers, and it is their admin access.
                django_user.is_staff = is_admin or django_user.is_staff
                request.user = django_user
        return self.get_response(request)
