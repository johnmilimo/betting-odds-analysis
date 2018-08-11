import re
from collections import OrderedDict

from django.shortcuts import render
from django.views import View
from lxml import html as ht
from apps.football.models import *
from django.utils import timezone
from django.http import HttpResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from apps.football.utils.analyzer import MatchAnalyzer
from django.core.paginator import Paginator


class MatchView(View):
    template_name = 'matches.html'

    def get(self, request):

        # match_list = Match.objects.all().exclude(results__exact='').order_by('-three_way_odds')
        match_list = Match.objects.all().order_by('-league')
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
            analyzer = MatchAnalyzer(team_a.strip())
            results = analyzer.analyze_team_performance()
            results['single'] = True

        elif team_a and team_b:
            analyzer = MatchAnalyzer(team_a.strip(), team_b.strip())
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
            # self.process_odds_data(obj.document)
            self.process_odds_data_updated(obj.document)

        return HttpResponse('File uploaded successfully!')

    def chunks(self, leng, n):
        # For item i in a range that is a length of l,
        for i in range(0, len(leng), n):
            # Create an index range for l of n items:
            yield leng[i:i + n]

    def populate_results(self, matches):

        def format_date(date_string):
            datetime_object = timezone.datetime.strptime(date_string,
                                                '%d/%m/%y %H:%M')
            return datetime_object

        for match in matches:
            try:
                team_a_win = False
                team_b_win = False
                score_draw = False
                nil_draw = False
                teams = match['team'].split(" vs ")
                team_a, team_b = teams[0], teams[1]
                date = format_date(match['date'])
                league = match['league']
                result_with_half_time = match['results']
                result = result_with_half_time.split(' ')[0].replace("-", ":")
                if int(result.split(":")[0]) > int(result.split(":")[1]):
                    team_a_win = True
                elif int(result.split(":")[1]) > int(result.split(":")[0]):
                    team_b_win = True
                elif int(result.split(":")[0]) == int(result.split(":")[1]) \
                        and int(result.split(":")[0]) > 0:
                    score_draw = True
                elif int(result.split(":")[0]) == int(result.split(":")[1]) \
                        and int(result.split(":")[0]) == 0:
                    nil_draw = True

                entry, created = Match.objects.get_or_create(team_a=team_a,
                                                             team_b=team_b,
                                                             match_date=date)
                entry.results = result
                entry.league = league
                entry.team_a_win = team_a_win
                entry.team_b_win = team_b_win
                entry.score_draw = score_draw
                entry.nil_draw = nil_draw
                entry.save()
            except Exception as e:
                print(match)
                print(e)

    def concatenate_odds(self, odds_list):
        return " | ".join(odds_list)

    def process_odds_data_updated(self, _file):
        html_text = _file.read()
        tree = ht.fromstring(html_text)

        # leagues
        leagues = tree.xpath(
            '//div[@class="league-row"]/div[@class="event-text ng-binding"]/text()')
        leagues = [x.replace('\n', '') for x in leagues if x != '\n']
        leagues_info = OrderedDict()
        start = 0
        for league in leagues:
            end = start + int(re.search(r'\((.*?)\)',league).group(1))
            leagues_info[league.split(" (")[0]] = [start, end]
            start = end
        # matches
        teams = tree.xpath(
            '//div[@class="event-names event-column"]/div[@class="event-text ng-binding"]/text()')
        teams = [x.replace('\n', '') for x in teams if x != '\n']
        matches = list(self.chunks(teams, 2))

        # match date / time
        date = tree.xpath(
            '//time-component[@show-date="true"][@show-time="true"]/span[@class="ng-binding"]/text()')

        # Three way
        home = tree.xpath(
            '//div[@class="event-selections"]/div[@title="Home"]/div[@class="ng-binding"]/text()')
        draw = tree.xpath(
            '//div[@class="event-selections"]/div[@title="Draw"]/div[@class="ng-binding"]/text()')
        away = tree.xpath(
            '//div[@class="event-selections"]/div[@title="Away"]/div[@class="ng-binding"]/text()')

        # Both teams to score
        yes = tree.xpath(
            '//div[@class="event-selections"]/div[@title="Yes"]/div[@class="ng-binding"]/text()')
        no = tree.xpath(
            '//div[@class="event-selections"]/div[@title="No"]/div[@class="ng-binding"]/text()')

        # Over / Under 2.50
        over = tree.xpath(
            '//div[@class="event-selections"]/div[@title="Over"]/div[@class="ng-binding"]/text()')
        under = tree.xpath(
            '//div[@class="event-selections"]/div[@title="Under"]/div[@class="ng-binding"]/text()')

        # Double Chance
        one_or_x = tree.xpath(
            '//div[@class="event-selections"]/div[@title="1 or X"]/div[@class="ng-binding"]/text()')
        x_or_two = tree.xpath(
            '//div[@class="event-selections"]/div[@title="X or 2"]/div[@class="ng-binding"]/text()')
        one_or_two = tree.xpath(
            '//div[@class="event-selections"]/div[@title="1 or 2"]/div[@class="ng-binding"]/text()')

        for league, slicer in leagues_info.items():
            match_counter = slicer[0]
            for match in matches[slicer[0]:slicer[1]]:
                home_team = match[0]
                away_team = match[1]
                double_chance_odds = self.concatenate_odds([one_or_x[match_counter],
                                                       x_or_two[match_counter],
                                                       one_or_two[match_counter]])
                over_under_25_odds = self.concatenate_odds([over[match_counter],
                                                       under[match_counter]])
                both_to_score_odds = self.concatenate_odds([yes[match_counter],
                                                             no[match_counter]])
                three_way_odds = self.concatenate_odds([home[match_counter],
                                                        draw[match_counter],
                                                        away[match_counter]])
                date_time = date[match_counter].split(" ")
                match_date = date_time[0] + " " + date_time[2]
                match_league = league

                obj, created = Match.objects.get_or_create(
                    team_a=home_team,
                    team_b=away_team,
                    match_date=timezone.datetime.strptime(
                        match_date, '%d/%m/%y %H:%M'),
                )
                obj.three_way_odds = three_way_odds
                obj.both_to_score_odds = both_to_score_odds
                obj.over_under_25_odds = over_under_25_odds
                obj.double_chance_odds = double_chance_odds
                if created:
                    obj.league = match_league
                obj.save()

                match_counter += 1

    def process_odds_data(self, _file):
        html_text = _file.read()
        tree = ht.fromstring(html_text)

        # ['16/07/18', '16/07/18', '16/07/18']
        date = tree.xpath('//li[@class="date"]/timecomponent[@show-date="true"]/span[@class="ng-binding"]/text()')

        # [22:00', '22:30']
        time = tree.xpath('//li[@class="time"]/timecomponent[@show-date="false"]/span[@class="ng-binding"]/text()')

        # ['Agropecuario Argentino', 'Draw', 'Lujan', 'Breidablik', 'Draw', 'Fjolnir', 'Fylkir', 'Draw', 'KR Reykjavik']
        teams = tree.xpath('//span[@class="team"]/text()')

        # ['2.02', '3.35', '3.62', '1.64', '4.01', '4.75', '3.19', '3.66', '2.07']
        odds = tree.xpath('//span[@class="odd"]/text()')

        # ['Argentina - Copa Argentina', 'Iceland - Urvalsdeild', 'Iceland - Urvalsdeild']
        leagues = tree.xpath('//div/div/span[@class="name"]/text()')
        leagues = [x.replace('\n', '') for x in leagues if x != '\n']

        matches = list(self.chunks(teams, 3))
        odds = list(self.chunks(odds, 3))

        index = 0
        for match in matches:
            obj, created = Match.objects.get_or_create(
                team_a=match[0],
                team_b=match[2],
                match_date=timezone.datetime.strptime(date[index]+' '+time[index], '%d/%m/%y %H:%M'),
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

        for i in range(len(teams)):
            matches.append(
                {
                    'team': teams[i],
                    'league': league[i],
                    'date': time[i],
                    'results': results[i]
                }
            )

        self.populate_results(matches)
