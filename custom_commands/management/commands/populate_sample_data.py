import os
from django.conf import settings
from apps.football.models import Match
from django.core.management.base import BaseCommand, CommandError

SAMPLE_MATCHES = [
    {
        "date": '13/07/18 21:15',
        "team": 'Sonderjyske vs AaB Aalborg',
        "location": 'Superligaen, Denmark',
        "results": '0:1'
     },
    {
        "date": '13/07/18 21:10',
        'team': 'Galarneau, Alexis vs Soeda, GO',
        'results': '0:2',
        'location': 'Winnipeg, Canada'
    },
    {
        'date': '13/07/18 21:00',
        'team': 'Cork City vs Burnley',
        'location': 'Club Friendly Games, International',
        'results': '0:1'
    }
]


class Command(BaseCommand):
    help = 'Create Sample Data'

    def handle(self, *args, **options):
        try:
            pass
        except Exception as e:
            raise CommandError(e)

        self.stdout.write(self.style.SUCCESS("Successfully created sample data"))
