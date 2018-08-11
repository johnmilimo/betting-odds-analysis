from django.contrib import admin
from apps.football.models import *
from django.contrib import admin


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ('team_a', 'team_b', 'league',
                    'three_way_odds', 'double_chance_odds',
                    'over_under_25_odds', 'both_to_score_odds',
                    'results', 'match_date')


admin.site.register(Team)
admin.site.register(League)
admin.site.register(MatchFile)
