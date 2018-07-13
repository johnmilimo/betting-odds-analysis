from django.shortcuts import render
from django.views import View
from apps.football.models import *
from apps.football.serializer import MatchSerializer

class MatchView(View):
    template_name = 'matches.html'

    def get(self, request):
        matches = MatchSerializer.data
        return render(request, self.template_name, {'form': matches})
