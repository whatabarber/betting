from prizepicks_scanner import update_prizepicks_data
from bovada_scanner import update_bovada_data

# Just update the local JSON files
update_prizepicks_data()
update_bovada_data()

print("✅ JSON files updated locally.")
print("📂 You can now manually upload to GitHub if needed.")
