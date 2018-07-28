from apps.football.models import Match


class MatchAnalyzer:
    def __init__(self, team_a, team_b=None):
        self.team_a = team_a
        self.team_b = team_b

    def get_past_matches(self):

        if self.team_b:
            response = Match.objects.raw(
                "SELECT * FROM football_match WHERE (team_a = %s AND team_b = %s AND results<>'') "
                "OR (team_a = %s AND team_b = %s AND results<>'')",
                [self.team_a, self.team_b, self.team_b, self.team_a])
        else:
            response = Match.objects.raw(
                "SELECT * FROM football_match WHERE (team_a = %s OR team_b = %s) AND results<>''",
                [self.team_a, self.team_a])

        return response

    def analyze_team_performance(self):
        results = {
            "team": self.team_a,
            "matches": [],
            "total_matches": 0,
            "start_period": None,
            "end_period": None,
            "total_wins": 0,
            "total_nil_draws": 0,
            "total_score_draws": 0,
            "points": 0
        }

        past_results = self.get_past_matches()

        if not len(list(past_results)):
            return results

        print(past_results)
        print('..')

        results['start_period'] = str(past_results[0].match_date)
        results['end_period'] = str(past_results[-1].match_date)

        for match in past_results:
            results['total_matches'] += 1
            if (match.team_a_win and match.team_a == self.team_a) or \
                    (match.team_b_win and match.team_b == self.team_a):
                results['total_wins'] += 1
                results['points'] += 1
                scores = [int(score) for score in match.results.split(':')]
                results['points'] += abs(scores[0] - scores[1])
            elif match.score_draw:
                results['total_score_draws'] += 1
                results['points'] += 1
            elif match.nil_draw:
                results['total_nil_draws'] += 1
                results['points'] += 1
            else:
                pass

            results['matches'].append(self.get_match_data(match))

        self.record_event({"team_performance_request": {"team": self.team_a}})

        return results

    def analyze_match_performance(self):

        results = {
            "matches": [],
            "total_matches": 0,
            "start_period": None,
            "end_period": None,
            "total_wins_per_team": {
                self.team_a: 0,
                self.team_b: 0,
            },
            "total_nil_draws": 0,
            "total_score_draws": 0
        }

        past_results = self.get_past_matches()

        if not len(list(past_results)):
            return results

        results['start_period'] = str(past_results[0].match_date)
        results['end_period'] = str(past_results[-1].match_date)

        for match in past_results:
            results['total_matches'] += 1
            if match.team_a_win:
                results['total_wins_per_team'][match.team_a] += 1
            elif match.team_b_win:
                results['total_wins_per_team'][match.team_b] += 1
            elif match.score_draw:
                results['total_score_draws'] += 1
            elif match.nil_draw:
                results['total_nil_draws'] += 1
            else:
                pass

            results['matches'].append(self.get_match_data(match))

        results['team'] = self.team_a + " Vs " + self.team_b

        self.record_event({"past_performance_request": {"team_a": self.team_a,
                                                   "team_b": self.team_b}})

        return results

    def record_event(self, event):
        print(event)

    def get_match_data(self, match):
        return {
            "team_a": match.team_a,
            "team_b": match.team_b,
            "odds": match.odds,
            "results": match.results,
            "league": match.league,
            "match_date": match.match_date
        }

