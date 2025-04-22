# decorators.py 파일 생성
from functools import wraps
from django.shortcuts import redirect
from basiccontent.models import User

def prevent_resubmission(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user_id = request.session.get('user_id')

        if user_id:
            if User.objects.filter(id=user_id, is_completed=True).exists():
                return redirect('basiccontent:post-end')

        return view_func(request, *args, **kwargs)

    return _wrapped_view