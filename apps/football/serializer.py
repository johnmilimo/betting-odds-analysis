from rest_framework import serializers
from apps.football.models import Match


class MatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Match
        fields = ('id', 'team_a', 'team_b', 'results')
