import os
from django.conf import settings
from apps.football.models import Match
from django.core.management.base import BaseCommand, CommandError
from datetime import datetime

SAMPLE_MATCHES = [
    {
        "date": '13/07/18 21:15',
        "team": 'Sonderjyske vs AaB Aalborg',
        "league": 'Superligaen, Denmark',
        "results": '0:1'
     },
    {
        "date": '13/07/18 21:10',
        'team': 'Galarneau, Alexis vs Soeda, GO',
        'results': '0:2',
        'league': 'Winnipeg, Canada'
    },
    {
        'date': '13/07/18 21:00',
        'team': 'Cork City vs Burnley',
        'league': 'Club Friendly Games, International',
        'results': '0:1'
    },
    {
        'team': 'Cong Anh Nhan Dan vs XM Fico Tay Ninh',
        'league': 'V-League 2, Vietnam',
        'date': '14/07/18 11:30',
        'results': '3:1'
    },
    {
        'team': 'Hainan Haihan vs Hunan Xiangtao',
        'league': 'China League 2, South, China',
        'date': '14/07/18 11:30',
        'results': '1:1'
    },
    {
        'team': 'Brisbane Strikers vs Redlands Utd',
        'league': 'NPL, Queensland, Australia',
        'date': '14/07/18 11:00',
        'results': '0:0'
    },
    {
        'team': 'Kromeriz vs MFK Dubnica',
        'league': 'Club Friendly Games, International',
        'date': '14/07/18 11:30',
        'results': '4:1'
    },
    {
        'team': 'Yanbian Beiguo vs Baotou Nanjiao',
        'league': 'China League 2, North, China',
        'date': '14/07/18 10:30',
        'results': '2:1'
    },
    {
        'team': 'Univ of Queensland vs Grange Thistle',
        'league': 'Brisbane Premier League, Australia',
        'date': '14/07/18 10:00',
        'results': '3:2'
    },
    {
        'team': 'Hebei Jingying vs Qingdao Jonoon',
        'league': 'China League 2, North, China',
        'date': '14/07/18 11:00',
        'results': '2:1'
    }
]


class Command(BaseCommand):
    help = 'Create Sample Data'

    def populate_results(self, data):
        for match in data:
            try:
                team_a_win = False
                team_b_win = False
                score_draw = False
                nil_draw = False
                teams = match['team'].split(" vs ")
                team_a, team_b = teams[0], teams[1]
                date = self.format_date(match['date'])
                league = match['league']
                result = match['results'].split(' ')[0].replace("-",":")
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

                obj, created = Match.objects.get_or_create(
                    team_a=team_a,
                    team_b=team_b,
                    match_date=date,
                )
                obj.results = result
                obj.league = league
                obj.team_a_win = team_a_win
                obj.team_b_win = team_b_win
                obj.score_draw = score_draw
                obj.nil_draw = nil_draw
                obj.save()
            except Exception as e:
                print(match)
                print(e)

    def handle(self, *args, **options):
        try:
            self.populate_results(SAMPLE_MATCHES)
        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS("Successfully created sample data"))

    @staticmethod
    def format_date(date_string):
        datetime_object = datetime.strptime(date_string,
                                            '%d/%m/%y %H:%M')
        return datetime_object
