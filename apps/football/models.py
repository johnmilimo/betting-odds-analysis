from django.db import models
from django.contrib.postgres.fields import JSONField


class Team(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Location(models.Model):
    name = models.CharField(max_length=30)
    created = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Match(models.Model):
    team_a = models.CharField(max_length=50)
    team_b = models.CharField(max_length=50)
    location = models.CharField(max_length=100)
    created_at = models.DateField(auto_now_add=True)
    match_date = models.DateField()
    results = models.CharField(max_length=5)
    team_a_win = models.BooleanField(default=False)
    team_b_win = models.BooleanField(default=False)
    score_draw = models.BooleanField(default=False)
    nil_draw = models.BooleanField(default=False)
    other = JSONField(default=dict)

    def __str__(self):
        return self.team_a + " Vs " + self.team_b
