from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.db.models.user import User
from app.db.models.listing import Listing
from app.services.security import get_password_hash

def ensure_user(db: Session, email: str, name: str) -> User:
    u = db.query(User).filter(User.email == email).first()
    if u: return u
    u = User(email=email, password_hash=get_password_hash("password123"), display_name=name, language="tr")
    db.add(u); db.commit(); db.refresh(u)
    return u

def create_listing(db: Session, user: User, **kwargs):
    l = Listing(user_id=user.id, **kwargs)
    db.add(l); db.commit()

def run():
    db = SessionLocal()
    try:
        # Create sample users
        tr = ensure_user(db, "kayahan@example.com", "Kayahan")
        en = ensure_user(db, "sarah@example.com", "Sarah")

        # WoW examples
        create_listing(db, tr, game="wow", title="Horde Mythic raid team LF DPS",
            description="Looking for Havoc DH for Tue/Thu 19:00-22:00 CET.", region="EU", server="Tarren Mill",
            language="en", playstyle="semi-hardcore", voice="discord", availability="weekdays 19:00-22:00 CET",
            tags=["raid","mythic","pve"], team_need={"DPS":2,"Healer":0,"preferred_role":"DPS"},
            game_specific={"faction":"Horde","class":"Demon Hunter","spec":"Havoc","ilvl":485,"raid_days":["Tue","Thu"]})
        create_listing(db, en, game="wow", title="Alliance keys +15-18",
            description="Chill keys, need tank.", region="EU", server="Silvermoon",
            language="en", playstyle="casual", voice="discord", availability="weeknights",
            tags=["keys","m+","dungeon"], team_need={"Tank":1,"preferred_role":"Tank"},
            game_specific={"faction":"Alliance","class":"Any","spec":"Any","ilvl":470,"keys_level":"15-18"})

        # Dota 2
        create_listing(db, tr, game="dota2", title="Pos4/5 stacking for ranked",
            description="3.5k MMR, looking for pos1/2 carry.", region="EU", server=None,
            language="tr", playstyle="casual", voice="discord", availability="weekends",
            tags=["ranked","pos4","support"], team_need={"pos1":1,"pos2":1,"preferred_role":"pos4"},
            game_specific={"rank_mmr":3500,"role":"pos4","captains_mode":False,"scrim":True})

        # New World
        create_listing(db, en, game="new_world", title="OPR team needs healer",
            description="EU central, need dedicated healer for OPR.", region="EU", server=None,
            language="en", playstyle="semi-hardcore", voice="discord", availability="evenings CET",
            tags=["OPR","pvp"], team_need={"Healer":1,"preferred_role":"Healer"},
            game_specific={"world":"Aeternum","company":"N/A","weapon_setup":"VG/Life","activity":"OPR"})

        # Diablo
        create_listing(db, tr, game="diablo", title="NM 45-50 runs, seasonal",
            description="Pulls + fast clears. Trading OK.", region="EU", server=None,
            language="tr", playstyle="hardcore", voice="discord", availability="weekday nights",
            tags=["nightmare","seasonal","pve"], team_need={"DPS":2,"preferred_role":"DPS"},
            game_specific={"seasonal":True,"class":"Barbarian","build":"HOTA","nightmare_tier":48,"trading":True})

        # Knight Online
        create_listing(db, en, game="knight_online", title="El Morad PK party",
            description="Looking for mage for CZ PK.", region="TR", server="Ares",
            language="tr", playstyle="semi-hardcore", voice="ts3", availability="weekends afternoon",
            tags=["PK","cz","pvp"], team_need={"Mage":1,"preferred_role":"Mage"},
            game_specific={"server":"Ares","nation":"El Morad","class":"Mage","level":70,"focus":"PK","ts_party":True})
    finally:
        db.close()

if __name__ == "__main__":
    run()
