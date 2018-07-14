import json
from django.shortcuts import render
from django.views import View
from django.views.decorators.csrf import csrf_protect

from apps.football.models import *
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.football.utils.analyzer import MatchAnalyzer

class MatchView(View):
    template_name = 'matches.html'

    def get(self, request):

        # data = serializers.serialize("json", Match.objects.all())
        data = Match.objects.all().order_by('-match_date')
        return render(request, self.template_name, {'data': data})

    def post(self, request):
        print("post logging: ", dict(request.POST))
        analysis_type = request.POST['analysis_type']
        if analysis_type=='single_team':
            team = request.POST.get('team')
            if not team:
                return HttpResponse("team is required")
            analyzer = MatchAnalyzer(team)
            results = analyzer.analyze_team_performance()
        else:
            team_a = request.POST['team_a']
            team_b = request.POST['team_b']
            if not team_a or not team_b:
                return HttpResponse("team_a and team_b values are required")
            analyzer = MatchAnalyzer(team_a, team_b)
            results = analyzer.analyze_match_performance()

        return HttpResponse(json.dumps(results),
                                content_type="application/json")


class UploadMatchData(LoginRequiredMixin, View):
    template_name = 'upload.html'
    redirect_field_name = 'next'

    def get(self, request):
        return render(request, self.template_name)

    @csrf_protect
    def post(self, request):
        return HttpResponse('File uploaded successfully!')


