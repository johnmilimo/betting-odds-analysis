from django.shortcuts import render
from django.views import View
from apps.football.models import *
from django.core import serializers


class MatchView(View):
    template_name = 'matches.html'

    def get(self, request):

        # data = serializers.serialize("json", Match.objects.all())
        data = Match.objects.all()
        return render(request, self.template_name, {'data': data})
