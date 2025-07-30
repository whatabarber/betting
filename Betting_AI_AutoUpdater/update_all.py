from prizepicks_scanner import update_prizepicks_data
from bovada_scanner import update_bovada_data
import os

# Step 1: Update data
update_prizepicks_data()
update_bovada_data()

# Step 2: Auto push to GitHub
os.system("git add ../data/props.json ../data/games.json")
os.system("git commit -m 'Auto-update data files'")
os.system("git push origin main")
print("✅ Data updated and pushed to GitHub.")
