from django.contrib import auth, messages
from django.shortcuts import redirect


class ActiveAccountMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.can_use_platform:
            auth.logout(request)
            messages.error(request, "계정이 휴면 또는 차단되어 로그아웃되었습니다.")
            return redirect("users:login")
        return self.get_response(request)
