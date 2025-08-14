from typing import Dict, Any
from math import exp

# Simple helper to compute score based on rules
def score(user_profile: Dict[str, Any], listing: Dict[str, Any]) -> int:
    s = 0
    # +30 game + server
    if user_profile.get("game") == listing.get("game"):
        s += 20
        if user_profile.get("server") and user_profile.get("server") == listing.get("server"):
            s += 10

    # +15 time/availability overlap (naive string overlap check)
    u_av = (user_profile.get("availability") or "").lower()
    l_av = (listing.get("availability") or "").lower()
    if u_av and l_av:
        overlap = len(set(u_av.split()) & set(l_av.split()))
        s += min(15, overlap * 3)

    # +10 language match
    if user_profile.get("language") and user_profile.get("language") == listing.get("language"):
        s += 10

    # +20 role/need match
    need = listing.get("team_need") or {}
    u_role = (user_profile.get("role") or "").lower()
    if u_role and need:
        # if the role is needed and count > 0
        for role, count in need.items():
            if role.lower() == u_role and int(count) > 0:
                s += 20
                break

    # +15 game-specific signals
    gs = listing.get("game_specific") or {}
    ugs = user_profile.get("game_specific") or {}
    game = listing.get("game")
    if game == "dota2":
        # closeness of rank MMR
        mmr_l = gs.get("rank_mmr")
        mmr_u = ugs.get("rank_mmr")
        if mmr_l and mmr_u:
            diff = abs(int(mmr_l) - int(mmr_u))
            # smaller diff -> higher score
            s += max(0, 15 - min(15, diff // 200))
    if game == "wow":
        ilvl_l = gs.get("ilvl"); ilvl_u = ugs.get("ilvl")
        if ilvl_l and ilvl_u:
            diff = abs(int(ilvl_l) - int(ilvl_u))
            s += max(0, 10 - min(10, diff // 5))
        # raid days overlap
        days_l = set((gs.get("raid_days") or []))
        days_u = set((ugs.get("raid_days") or []))
        s += min(5, len(days_l & days_u))
    if game == "diablo":
        n_l = gs.get("nightmare_tier"); n_u = ugs.get("nightmare_tier")
        if n_l and n_u:
            diff = abs(int(n_l) - int(n_u))
            s += max(0, 15 - min(15, diff))

    # +5 profile completeness
    filled = sum(1 for k in ["display_name","language","timezone"] if user_profile.get(k))
    if filled >= 3:
        s += 5

    # +5 freshness, assume listing dict has 'age_days'
    age = listing.get("age_days", 0)
    s += max(0, 5 - min(5, int(age)))

    return min(100, s)
