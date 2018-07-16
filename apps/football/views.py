import json
from django.shortcuts import render
from django.views import View
from custom_commands.management.commands.populate_sample_data import Command

from lxml import html as ht
from apps.football.models import *
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.football.utils.analyzer import MatchAnalyzer

class MatchView(View):
    template_name = 'matches.html'

    def get(self, request):

        # data = serializers.serialize("json", Match.objects.all())
        data = Match.objects.all().order_by('-match_date')

        return render(request, self.template_name, {'data': data, "results": {}})

    def post(self, request):
        print("post logging: ", dict(request.POST))
        team_a = request.POST['team_a']
        team_b = request.POST['team_b']
        results = {
            "matches": {}
        }

        if team_a and (not team_b):
            analyzer = MatchAnalyzer(team_a)
            results = analyzer.analyze_team_performance()
            results['single'] = True

        elif team_a and team_b:
            analyzer = MatchAnalyzer(team_a, team_b)
            results = analyzer.analyze_match_performance()
            results['single'] = False

        matches = results['matches']
        del results['matches']

        return render(request, self.template_name, {'data': matches, "results": results})


class UploadMatchData(LoginRequiredMixin, View):
    template_name = 'upload.html'
    redirect_field_name = 'next'

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):

        _file = request.FILES['datafile']
        if not _file:
            return HttpResponse('FAILED: You havent uploaded any file')
        obj, created = MatchFile.objects.get_or_create(document=_file)
        self.handle_uploaded_file(obj.document)

        return HttpResponse('File uploaded successfully!')

    def handle_uploaded_file(self, _file):
        html_text = _file.read()
        matches = []
        tree = ht.fromstring(html_text)
        time = tree.xpath('//time[@class="ng-binding"]/text()')
        teams = tree.xpath('//li[@class="event"]/span[@class="ng-binding"]/text()')
        league = tree.xpath('//span[@class="league ng-binding"]/text()')
        results = tree.xpath('//li[@class="result"]/span[@class="ng-binding"]/text()')

        print(results)
        print()

        for i in range(len(teams)):
            matches.append(
                {
                    'team': teams[i],
                    'location': league[i],
                    'date': time[i],
                    'results': results[i]
                }
            )

        Command().populate(matches)
