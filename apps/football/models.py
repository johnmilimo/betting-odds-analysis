from django.db import models
from django.utils import timezone
from django.contrib.postgres.fields import JSONField


class Team(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class League(models.Model):
    name = models.CharField(max_length=30)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    team_a = models.CharField(max_length=50)
    team_b = models.CharField(max_length=50)
    league = models.CharField(max_length=100)
    created_at = models.DateTimeField(default=timezone.now)
    match_date = models.DateTimeField()
    results = models.CharField(max_length=5)
    odds = models.CharField(max_length=20, blank=True)
    team_a_win = models.BooleanField(default=False)
    team_b_win = models.BooleanField(default=False)
    score_draw = models.BooleanField(default=False)
    nil_draw = models.BooleanField(default=False)
    other = JSONField(default=dict)

    def __str__(self):
        return self.team_a + " Vs " + self.team_b


class MatchFile(models.Model):
    description = models.CharField(max_length=255, blank=True)
    document = models.FileField(upload_to='match_files/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
