from django.shortcuts import get_object_or_404, redirect
from mainsite.models import Group

class OwnerCheck:
    def dispatch(self, request, *args, **kwargs):
        self.group = get_object_or_404(Group, slug__iexact=kwargs.get('slug'))
        if self.group not in request.user.account.groups.all():
            return redirect(self.group)
        return super().dispatch(request, *args, **kwargs)