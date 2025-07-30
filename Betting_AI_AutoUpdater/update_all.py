from prizepicks_scanner import update_prizepicks_data
from bovada_scanner import update_bovada_data

# Update only the JSON files
update_prizepicks_data()
update_bovada_data()

print("✅ PrizePicks and Bovada JSON files updated locally.")
print("🔁 Now run: git add data/props.json data/games.json")
print("   then:    git commit -m 'Daily update'")
print("   then:    git push origin main")
