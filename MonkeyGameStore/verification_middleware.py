from django.shortcuts import redirect
from django.urls import reverse


class VerificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        try:
            if not request.user.is_verified:
                if request.path != (reverse('verification')) and request.path !=(reverse('logout')):
                    return redirect('verification')
        except:
            pass

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response