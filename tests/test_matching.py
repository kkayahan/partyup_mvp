from app.services.matching import score

def test_score_basics():
    user = {"game":"dota2","server":None,"language":"tr","availability":"weekends","role":"pos4",
            "game_specific":{"rank_mmr":3500}}
    listing = {"game":"dota2","server":None,"language":"tr","availability":"weekends",
               "team_need":{"pos4":1},"game_specific":{"rank_mmr":3700},"age_days":0}
    s = score(user, listing)
    assert 0 <= s <= 100
