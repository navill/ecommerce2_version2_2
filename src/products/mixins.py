from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.utils.decorators import method_decorator


# object: python 최상위 클래스
class StaffRequiredMixin(object):
    @classmethod
    def as_view(cls, *args, **kwargs):
        # ListView(StaffRequiredMixin, ListView).as_view()
        # 정의 시 as_view에 대한 'unresolved attribute reference' 경고
        # 실제 사용 시, ListView에 정의된 as_view를 사용할 수 있다.
        view = super(StaffRequiredMixin, cls).as_view(*args, **kwargs)
        # login 시 필요한 조건을 만족하는지 검사하기 위해 매개변수에 해당 view를 인가
        # login_required -> are you logged in? -> dispatch -> are you staff member?
        # staff_member_required -> are you staff member??
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_staff:
            return super(StaffRequiredMixin, self).dispatch(request, *args, **kwargs)
        else:
            raise Http404


class LoginRequiredMixin(object):
    @classmethod
    def as_view(cls, *args, **kwargs):
        view = super(LoginRequiredMixin, cls).as_view(*args, **kwargs)
        return login_required(view)

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(request, *args, **kwargs)
