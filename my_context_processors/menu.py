# from django.core.context_processors import request
from mainsite.models import Group
def main(request):
    return {'groupcount': Group.objects.all().count()}