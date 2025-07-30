
import json
def update_prizepicks_data():
    props = [
        {
            "player": "Justin Jefferson",
            "line": "89.5 Rec Yds",
            "model": "102.3",
            "edge": "+13",
            "league": "NFL",
            "commentary": "Facing bottom-5 pass D. Game script favors pass-heavy. ✅"
        },
        {
            "player": "LeBron James",
            "line": "6.5 Ast",
            "model": "6.1",
            "edge": "-0.4",
            "league": "NBA",
            "commentary": "Against top assist defense. Might fall short."
        }
    ]
    with open("../data/props.json", "w") as f:
        json.dump(props, f, indent=2)
