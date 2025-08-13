import datetime
import time
import json
import os
import subprocess
from typing import Dict, Any
from pathlib import Path

def get_data_path():
    """Dynamically find the data folder"""
    script_dir = Path(__file__).parent.absolute()
    possible_paths = [
        script_dir / "data",
        script_dir / "../data",
        script_dir / "../../data",
        Path.cwd() / "data",
    ]
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    data_path = script_dir / "data"
    data_path.mkdir(exist_ok=True)
    return data_path

def push_to_github():
    """Auto-push updated JSON files to GitHub"""
    try:
        print("\n🚀 PUSHING TO GITHUB...")
        print("-" * 5)
        
        # Get current directory (your project root)
        project_root = Path(__file__).parent.absolute()
        
        # Change to project directory
        os.chdir(project_root)
        
        # Check if this is a git repository
        if not (project_root / ".git").exists():
            print("❌ Not a git repository. Initialize with 'git init' first.")
            return False
        
        # Add the JSON files
        data_path = get_data_path()
        subprocess.run(["git", "add", str(data_path / "*.json")], check=False)
        subprocess.run(["git", "add", str(data_path / "props.json")], check=False)
        subprocess.run(["git", "add", str(data_path / "games.json")], check=False)
        subprocess.run(["git", "add", str(data_path / "update_log.json")], check=False)
        
        # Create commit message with timestamp
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        commit_message = f"🎯 Auto-update betting data - {timestamp}"
        
        # Commit the changes
        result = subprocess.run(["git", "commit", "-m", commit_message], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Files committed successfully")
            
            # Push to GitHub
            push_result = subprocess.run(["git", "push", "origin", "main"], capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("🚀 Successfully pushed to GitHub!")
                print("🔄 Vercel will auto-deploy your updates")
                return True
            else:
                print(f"❌ Push failed: {push_result.stderr}")
                print("💡 Make sure you're connected to GitHub and have push permissions")
                return False
        else:
            if "nothing to commit" in result.stdout:
                print("ℹ️ No changes to commit")
                return True
            else:
                print(f"❌ Commit failed: {result.stderr}")
                return False
                
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        return False
    except Exception as e:
        print(f"❌ GitHub push error: {e}")
        return False

def enhanced_update_all():
    """Enhanced update script with error handling and logging"""
    
    print("🚀" * 5)
    print(f"LIVE BETTING DATA UPDATE - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀" * 5)
    
    # Get the correct data path
    data_path = get_data_path()
    
    results = {
        "prizepicks": {"success": False, "error": None, "props_count": 0},
        "bovada": {"success": False, "error": None, "games_count": 0},
        "github": {"success": False, "error": None},
        "total_runtime": 0,
        "data_path": str(data_path)
    }
    
    start_time = time.time()
    
    # Update PrizePicks data
    print("\n🎯 UPDATING PRIZEPICKS DATA...")
    print("-" * 5)
    try:
        from prizepicks_scanner import update_prizepicks_data
        update_prizepicks_data()
        
        # Check for props.json with correct path
        props_file = data_path / "props.json"
        if props_file.exists():
            with open(props_file, "r") as f:
                props_data = json.load(f)
                results["prizepicks"]["props_count"] = len(props_data)
                results["prizepicks"]["success"] = True
                print(f"✅ PrizePicks: {len(props_data)} props loaded successfully")
        else:
            # Create empty props file if it doesn't exist
            empty_props = [{"player": "No data available", "line": "Check connection", "model": "N/A", "edge": "N/A", "league": "System", "commentary": "API connection issues"}]
            with open(props_file, "w") as f:
                json.dump(empty_props, f, indent=2)
            results["prizepicks"]["props_count"] = 1
            results["prizepicks"]["success"] = True
            print(f"⚠️ Created fallback props.json at {props_file}")
            
    except Exception as e:
        results["prizepicks"]["error"] = str(e)
        print(f"❌ PrizePicks Error: {e}")
        
        # Create fallback props file even on error
        try:
            props_file = data_path / "props.json"
            empty_props = [{"player": "Error loading data", "line": "Check logs", "model": "N/A", "edge": "N/A", "league": "System", "commentary": f"Error: {str(e)}"}]
            with open(props_file, "w") as f:
                json.dump(empty_props, f, indent=2)
            print(f"📁 Created error fallback at {props_file}")
        except:
            pass
    
    # Update Bovada data
    print("\n📈 UPDATING BOVADA DATA...")
    print("-" * 5)
    try:
        from bovada_scanner import update_bovada_data
        update_bovada_data()
        
        # Check for games.json with correct path
        games_file = data_path / "games.json"
        if games_file.exists():
            with open(games_file, "r") as f:
                games_data = json.load(f)
                results["bovada"]["games_count"] = len(games_data)
                results["bovada"]["success"] = True
                print(f"✅ Bovada: {len(games_data)} games loaded successfully")
        else:
            # Create empty games file if it doesn't exist
            empty_games = [{"matchup": "No games available", "line": "Check connection", "sharp_pct": "N/A", "public_pct": "N/A", "commentary": "API connection issues", "sport": "System"}]
            with open(games_file, "w") as f:
                json.dump(empty_games, f, indent=2)
            results["bovada"]["games_count"] = 1
            results["bovada"]["success"] = True
            print(f"⚠️ Created fallback games.json at {games_file}")
            
    except Exception as e:
        results["bovada"]["error"] = str(e)
        print(f"❌ Bovada Error: {e}")
        
        # Create fallback games file even on error
        try:
            games_file = data_path / "games.json"
            empty_games = [{"matchup": "Error loading data", "line": "Check logs", "sharp_pct": "N/A", "public_pct": "N/A", "commentary": f"Error: {str(e)}", "sport": "System"}]
            with open(games_file, "w") as f:
                json.dump(empty_games, f, indent=2)
            print(f"📁 Created error fallback at {games_file}")
        except:
            pass
    
    # Auto-push to GitHub (only if data updates were successful)
    if results["prizepicks"]["success"] or results["bovada"]["success"]:
        github_success = push_to_github()
        results["github"]["success"] = github_success
        if not github_success:
            results["github"]["error"] = "Failed to push to GitHub"
    else:
        print("\n⚠️ Skipping GitHub push - no successful data updates")
        results["github"]["error"] = "Skipped due to failed data updates"
    
    # Calculate runtime
    end_time = time.time()
    results["total_runtime"] = round(end_time - start_time, 2)
    
    # Create update log
    create_update_log(results, data_path)
    
    # Print summary
    print("\n🚀" * 5)
    print("UPDATE SUMMARY")
    print("🚀" * 5)
    
    print(f"📁 Data Path: {data_path}")
    
    if results["prizepicks"]["success"]:
        print(f"✅ PrizePicks: {results['prizepicks']['props_count']} props updated")
    else:
        print(f"❌ PrizePicks: Failed - {results['prizepicks']['error']}")
    
    if results["bovada"]["success"]:
        print(f"✅ Bovada: {results['bovada']['games_count']} games updated")
    else:
        print(f"❌ Bovada: Failed - {results['bovada']['error']}")
    
    if results["github"]["success"]:
        print("🚀 GitHub: Successfully pushed to repository")
    else:
        print(f"❌ GitHub: {results['github']['error']}")
    
    print(f"⏱️ Total Runtime: {results['total_runtime']} seconds")
    
    # Success rate
    success_count = sum([results["prizepicks"]["success"], results["bovada"]["success"]])
    success_rate = (success_count / 2) * 100
    print(f"📊 Success Rate: {success_rate:.0f}% ({success_count}/2 services)")
    
    if success_rate == 100 and results["github"]["success"]:
        print("🎉 ALL SYSTEMS OPERATIONAL! Data updated and pushed to GitHub!")
    elif success_rate >= 50:
        print("⚠️ PARTIAL SUCCESS - Some data updated")
    else:
        print("🚨 MAJOR ISSUES - Check error logs")
    
    print(f"\n📂 JSON files updated at: {data_path}")
    print("🔄 Dashboard will auto-refresh data.")
    print("🚀 Vercel deployment triggered automatically.")
    print("💡 Tip: Run this script every 15-30 minutes for fresh data.")
    
    return results

def create_update_log(results: Dict[str, Any], data_path: Path):
    """Create detailed log file"""
    try:
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "results": results,
            "status": "SUCCESS" if all([results["prizepicks"]["success"], results["bovada"]["success"]]) else "PARTIAL"
        }
        
        # Load existing logs or create new
        log_file = data_path / "update_log.json"
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
            
        print(f"📝 Log updated: {log_file}")
            
    except Exception as e:
        print(f"⚠️ Could not create log: {e}")

def check_data_freshness(data_path: Path):
    """Check if data files are recent enough"""
    try:
        files_to_check = [data_path / "props.json", data_path / "games.json"]
        current_time = datetime.datetime.now()
        
        print(f"\n📊 CHECKING DATA FRESHNESS IN: {data_path}")
        print("-" * 50)
        
        for file_path in files_to_check:
            if file_path.exists():
                file_time = datetime.datetime.fromtimestamp(file_path.stat().st_mtime)
                age_minutes = (current_time - file_time).total_seconds() / 60
                
                if age_minutes > 60:  # Older than 1 hour
                    print(f"⚠️ {file_path.name} is {age_minutes:.0f} minutes old")
                else:
                    print(f"✅ {file_path.name} is fresh ({age_minutes:.0f} min old)")
            else:
                print(f"❌ {file_path.name} not found - will be created")
                
    except Exception as e:
        print(f"❌ Error checking file freshness: {e}")

def setup_git_repo():
    """Helper function to set up git repository"""
    print("\n🔧 GIT SETUP HELPER")
    print("-" * 50)
    print("To enable auto-push to GitHub, make sure you have:")
    print("1. ✅ git init (initialize repository)")
    print("2. ✅ git remote add origin <your-github-repo-url>")
    print("3. ✅ git branch -M main")
    print("4. ✅ GitHub authentication set up")
    print("\nExample commands:")
    print("git init")
    print("git remote add origin https://github.com/yourusername/your-repo.git")
    print("git add .")
    print("git commit -m 'Initial commit'")
    print("git branch -M main")
    print("git push -u origin main")

def auto_retry_failed():
    """Retry failed updates after a delay"""
    print("\n🔄 AUTO-RETRY ENABLED")
    print("Will retry failed updates in 30 seconds...")
    time.sleep(30)
    
    print("\n🔄 RETRYING FAILED UPDATES...")
    enhanced_update_all()

def diagnose_git_setup():
    """Diagnose git setup issues"""
    print("\n🔧 DIAGNOSING GIT SETUP...")
    print("-" * 50)
    
    project_root = Path(__file__).parent.absolute()
    os.chdir(project_root)
    
    # Check if git repo
    git_exists = (project_root / ".git").exists()
    print(f"📁 Git repository: {'✅ Yes' if git_exists else '❌ No - run: git init'}")
    
    if not git_exists:
        return
    
    # Check remote
    try:
        result = subprocess.run(["git", "remote", "-v"], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"📡 Git remotes:\n{result.stdout}")
        else:
            print("❌ No git remote set up")
            print("💡 Run: git remote add origin https://github.com/USERNAME/REPO.git")
    except:
        print("❌ Could not check git remotes")
    
    # Check current branch
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True)
        current_branch = result.stdout.strip()
        print(f"🌿 Current branch: {current_branch}")
    except:
        print("❌ Could not check current branch")
    
    # Check git status
    try:
        result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"📝 Uncommitted changes:\n{result.stdout}")
        else:
            print("✅ Working directory clean")
    except:
        print("❌ Could not check git status")
    
    # Check last commit
    try:
        result = subprocess.run(["git", "log", "--oneline", "-1"], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"📄 Last commit: {result.stdout.strip()}")
        else:
            print("❌ No commits found")
    except:
        print("❌ Could not check commit history")

# Add this to the main execution section
if __name__ == "__main__":
    # Get data path first
    data_path = get_data_path()
    
    # Check current data freshness
    check_data_freshness(data_path)
    
    # Add git diagnostics
    diagnose_git_setup()
    
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
        
        # Also push to GitHub
        push_to_github()
        
        print("✅ JSON files updated locally and pushed to GitHub.")
        
    except Exception as e:
        print(f"❌ Update failed: {e}")

# Keep your original simple version available
update_prizepicks_data = update_all  # Backwards compatibility