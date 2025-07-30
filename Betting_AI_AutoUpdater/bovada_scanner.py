
import json
def update_bovada_data():
    games = [
        {
            "matchup": "Texas vs Baylor",
            "line": "Texas -6.5",
            "sharp_pct": "74%",
            "public_pct": "61%",
            "league": "CFB",
            "commentary": "Baylor QB out. Texas off a bye. Revenge game. 🔥"
        },
        {
            "matchup": "Chiefs vs Broncos",
            "line": "Chiefs -9.5",
            "sharp_pct": "48%",
            "public_pct": "90%",
            "league": "NFL",
            "commentary": "Huge public load on KC. Possible trap spot. ⚠️"
        }
    ]
    with open("../data/games.json", "w") as f:
        json.dump(games, f, indent=2)
