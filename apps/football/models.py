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
    team_a = models.CharField(max_length=30)
    team_b = models.CharField(max_length=30)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    match_date = models.DateField()
    results = models.CharField(max_length=5)
    team_a_win = models.BooleanField(default=False)
    team_b_win = models.BooleanField(default=False)
    score_draw = models.BooleanField(default=False)
    nil_draw = models.BooleanField(default=False)
    other = JSONField()

    def __str__(self):
        return self.team_a + " Vs " + self.team_b
