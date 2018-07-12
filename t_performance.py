def record_event(event):
    print(event)


def get_past_match_results(team_a, team_b):
    query = "SELECT * FROM match WHERE (team_a={0} AND team_b={1})" \
            " OR (team_a={2} AND team_b={3})" \
            " ORDER BY date ASC".format(team_a, team_b, team_b, team_a)
    print(query)
    return []


def past_performance_request(team_a, team_b, start_time, end_time):

    results = {
        "matches": [],
        "total_matches": 0,
        "start_period": None,
        "end_period": None,
        "wins": {
            team_a: 0,
            team_b: 0,
        },
        "draws": {
            "nils": 0,
            "scores": 0
        }
    }
    past_results = get_past_match_results(team_a, team_b)
    results['total_matches'] = len(past_results)
    results["start_period"] = past_results[0].date
    results['end_period'] = past_results[-1].date
    matches = []

    for match in past_results:
        if match.team_a_win:
            results['wins'][match.team_a] = results['wins'][match.team_a] + 1
        elif match.team_b_win:
            results['wins'][match.team_b] = results['wins'][match.team_b] + 1
        elif match.score_draw:
            results['draws']['scores'] = results['draws']['scores'] + 1
        elif match.nil_draw:
            results['draws']['nils'] = results['draws']['nils'] + 1
        else:
            raise Exception

        matches.append({"team_a": match.team_a,
                        "team_b": match.team_b,
                        "results": match.results,
                        "location": match.location})
        results['matches'].append(matches)

    record_event({"past_performance_request": {"team_a": team_a,
                                               "team_b": team_b}})
    return results
