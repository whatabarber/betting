import datetime
import time
import json
import os
from typing import Dict, Any

def enhanced_update_all():
    """Enhanced update script with error handling and logging"""
    
    print("🚀" * 40)
    print(f"LIVE BETTING DATA UPDATE - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀" * 40)
    
    results = {
        "prizepicks": {"success": False, "error": None, "props_count": 0},
        "bovada": {"success": False, "error": None, "games_count": 0},
        "total_runtime": 0
    }
    
    start_time = time.time()
    
    # Update PrizePicks data
    print("\n🎯 UPDATING PRIZEPICKS DATA...")
    print("-" * 50)
    try:
        from prizepicks_scanner import update_prizepicks_data
        update_prizepicks_data()
        
        # Verify props.json was created and has data
        if os.path.exists("../data/props.json"):
            with open("../data/props.json", "r") as f:
                props_data = json.load(f)
                results["prizepicks"]["props_count"] = len(props_data)
                results["prizepicks"]["success"] = True
                print(f"✅ PrizePicks: {len(props_data)} props loaded successfully")
        else:
            raise FileNotFoundError("props.json not created")
            
    except Exception as e:
        results["prizepicks"]["error"] = str(e)
        print(f"❌ PrizePicks Error: {e}")
    
    # Update Bovada data
    print("\n📈 UPDATING BOVADA DATA...")
    print("-" * 50)
    try:
        from bovada_scanner import update_bovada_data
        update_bovada_data()
        
        # Verify games.json was created and has data
        if os.path.exists("../data/games.json"):
            with open("../data/games.json", "r") as f:
                games_data = json.load(f)
                results["bovada"]["games_count"] = len(games_data)
                results["bovada"]["success"] = True
                print(f"✅ Bovada: {len(games_data)} games loaded successfully")
        else:
            raise FileNotFoundError("games.json not created")
            
    except Exception as e:
        results["bovada"]["error"] = str(e)
        print(f"❌ Bovada Error: {e}")
    
    # Calculate runtime
    end_time = time.time()
    results["total_runtime"] = round(end_time - start_time, 2)
    
    # Create update log
    create_update_log(results)
    
    # Print summary
    print("\n🚀" * 40)
    print("UPDATE SUMMARY")
    print("🚀" * 40)
    
    if results["prizepicks"]["success"]:
        print(f"✅ PrizePicks: {results['prizepicks']['props_count']} props updated")
    else:
        print(f"❌ PrizePicks: Failed - {results['prizepicks']['error']}")
    
    if results["bovada"]["success"]:
        print(f"✅ Bovada: {results['bovada']['games_count']} games updated")
    else:
        print(f"❌ Bovada: Failed - {results['bovada']['error']}")
    
    print(f"⏱️ Total Runtime: {results['total_runtime']} seconds")
    
    # Success rate
    success_count = sum([results["prizepicks"]["success"], results["bovada"]["success"]])
    success_rate = (success_count / 2) * 100
    print(f"📊 Success Rate: {success_rate:.0f}% ({success_count}/2 services)")
    
    if success_rate == 100:
        print("🎉 ALL SYSTEMS OPERATIONAL!")
    elif success_rate >= 50:
        print("⚠️ PARTIAL SUCCESS - Some data updated")
    else:
        print("🚨 MAJOR ISSUES - Check error logs")
    
    print("\n📂 JSON files updated locally.")
    print("🔄 Dashboard will auto-refresh data.")
    print("💡 Tip: Run this script every 15-30 minutes for fresh data.")
    
    return results

def create_update_log(results: Dict[str, Any]):
    """Create detailed log file"""
    try:
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "results": results,
            "status": "SUCCESS" if all([results["prizepicks"]["success"], results["bovada"]["success"]]) else "PARTIAL"
        }
        
        # Load existing logs or create new
        log_file = "../data/update_log.json"
        try:
            with open(log_file, "r") as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
        
        # Add new log entry
        logs.append(log_entry)
        
        # Keep only last 100 entries
        logs = logs[-100:]
        
        # Save updated logs
        with open(log_file, "w") as f:
            json.dump(logs, f, indent=2)
            
    except Exception as e:
        print(f"⚠️ Could not create log: {e}")

def check_data_freshness():
    """Check if data files are recent enough"""
    try:
        files_to_check = ["../data/props.json", "../data/games.json"]
        current_time = datetime.datetime.now()
        
        for file_path in files_to_check:
            if os.path.exists(file_path):
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                age_minutes = (current_time - file_time).total_seconds() / 60
                
                if age_minutes > 60:  # Older than 1 hour
                    print(f"⚠️ {os.path.basename(file_path)} is {age_minutes:.0f} minutes old")
                else:
                    print(f"✅ {os.path.basename(file_path)} is fresh ({age_minutes:.0f} min old)")
            else:
                print(f"❌ {os.path.basename(file_path)} not found")
                
    except Exception as e:
        print(f"❌ Error checking file freshness: {e}")

def auto_retry_failed():
    """Retry failed updates after a delay"""
    print("\n🔄 AUTO-RETRY ENABLED")
    print("Will retry failed updates in 30 seconds...")
    time.sleep(30)
    
    print("\n🔄 RETRYING FAILED UPDATES...")
    enhanced_update_all()

# Main execution
if __name__ == "__main__":
    # Check current data freshness
    print("📊 CHECKING CURRENT DATA FRESHNESS...")
    check_data_freshness()
    
    # Run main update
    results = enhanced_update_all()
    
    # Auto-retry if needed (optional)
    success_rate = sum([results["prizepicks"]["success"], results["bovada"]["success"]]) / 2 * 100
    
    if success_rate < 100:
        retry = input(f"\n🤔 Success rate: {success_rate:.0f}%. Retry failed updates? (y/n): ")
        if retry.lower() == 'y':
            auto_retry_failed()

# For external calls (your current usage)
def update_all():
    """Simple function for external scripts"""
    try:
        from prizepicks_scanner import update_prizepicks_data
        from bovada_scanner import update_bovada_data
        
        update_prizepicks_data()
        update_bovada_data()
        print("✅ JSON files updated locally.")
        
    except Exception as e:
        print(f"❌ Update failed: {e}")

# Keep your original simple version available
update_prizepicks_data = update_all  # Backwards compatibility
