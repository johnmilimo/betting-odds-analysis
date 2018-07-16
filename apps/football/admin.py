from django.contrib import admin
from apps.football.models import *
# Register your models here.

admin.site.register(Team)
admin.site.register(Match)
admin.site.register(League)
admin.site.register(MatchFile)
