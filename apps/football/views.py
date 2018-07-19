import json
from django.shortcuts import render
from django.views import View
from custom_commands.management.commands.populate_sample_data import Command

from lxml import html as ht
from datetime import datetime
from apps.football.models import *
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.football.utils.analyzer import MatchAnalyzer
from django.core.paginator import Paginator


class MatchView(View):
    template_name = 'matches.html'

    def get(self, request):

        match_list = Match.objects.all().order_by('-results')
        paginator = Paginator(match_list, 30)  # Show 30 matches per page

        page = request.GET.get('page')
        data = paginator.get_page(page)

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
        category = request.POST['category']
        print("category:", category)
        obj, created = MatchFile.objects.get_or_create(document=_file)
        if category == 'results':
            print("process results")
            self.process_results_data(obj.document)
        else:
            self.process_odds_data(obj.document)

        return HttpResponse('File uploaded successfully!')

    def chunks(self, leng, n):
        # For item i in a range that is a length of l,
        for i in range(0, len(leng), n):
            # Create an index range for l of n items:
            yield leng[i:i + n]

    def process_odds_data(self, _file):
        html_text = _file.read()
        tree = ht.fromstring(html_text)

        # ['16/07/18', '16/07/18', '16/07/18']
        time = tree.xpath('//li[@class="date"]/timecomponent[@show-date="true"]/span[@class="ng-binding"]/text()')

        # ['Agropecuario Argentino', 'Draw', 'Lujan', 'Breidablik', 'Draw', 'Fjolnir', 'Fylkir', 'Draw', 'KR Reykjavik']
        teams = tree.xpath('//span[@class="team"]/text()')

        # ['2.02', '3.35', '3.62', '1.64', '4.01', '4.75', '3.19', '3.66', '2.07']
        odds = tree.xpath('//span[@class="odd"]/text()')

        # ['Argentina - Copa Argentina', 'Iceland - Urvalsdeild', 'Iceland - Urvalsdeild']
        leagues = tree.xpath('//div/div/span[@class="name"]/text()')
        leagues = [x.replace('\n', '') for x in leagues if x != '\n']

        print(leagues)
        print()

        matches = list(self.chunks(teams, 3))
        odds = list(self.chunks(odds, 3))

        index = 0
        for match in matches:
            obj, created = Match.objects.get_or_create(
                team_a=match[0],
                team_b=match[2],
                match_date=datetime.strptime(time[index], '%d/%m/%y'),
            )
            obj.odds = " | ".join(odds[index])
            if created:
                obj.league = leagues[index],
            obj.save()

            index += 1

    def process_results_data(self, _file):
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
                    'league': league[i],
                    'date': time[i],
                    'results': results[i]
                }
            )

        Command().populate_results(matches)
