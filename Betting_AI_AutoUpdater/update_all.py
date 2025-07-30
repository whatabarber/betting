from prizepicks_scanner import update_prizepicks_data
from bovada_scanner import update_bovada_data
import os

# Update data files
update_prizepicks_data()
update_bovada_data()

# Use git only if files changed
os.system("git status")
os.system("git add .")
os.system("git commit -m \"Daily auto-update of data files\" || echo No changes to commit")
os.system("git push origin main")
print("✅ Data updated and pushed to GitHub.")
