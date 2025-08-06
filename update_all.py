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

def setup_github_auth():
    """Set up GitHub authentication with token"""
    print("\n🔑 GITHUB AUTHENTICATION SETUP")
    print("-" * 50)
    
    # Check if token is in environment variable
    token = os.getenv('GITHUB_TOKEN')
    if token:
        print("✅ Found GITHUB_TOKEN environment variable")
        return token
    
    # Check if there's a token file
    token_file = Path(__file__).parent / ".github_token"
    if token_file.exists():
        try:
            with open(token_file, 'r') as f:
                token = f.read().strip()
            print("✅ Found token in .github_token file")
            return token
        except:
            pass
    
    # Prompt user for token
    print("🔑 GitHub Personal Access Token not found.")
    print("💡 You can either:")
    print("   1. Set GITHUB_TOKEN environment variable")
    print("   2. Create a .github_token file with your token")
    print("   3. Enter it now (will be saved to .github_token)")
    
    token = input("\n🔑 Enter your GitHub token (or press Enter to skip): ").strip()
    
    if token:
        # Save token to file for future use
        try:
            with open(token_file, 'w') as f:
                f.write(token)
            print("✅ Token saved to .github_token file")
            
            # Add .github_token to .gitignore to keep it secure
            gitignore_file = Path(__file__).parent / ".gitignore"
            gitignore_content = ""
            if gitignore_file.exists():
                with open(gitignore_file, 'r') as f:
                    gitignore_content = f.read()
            
            if ".github_token" not in gitignore_content:
                with open(gitignore_file, 'a') as f:
                    f.write("\n.github_token\n")
                print("✅ Added .github_token to .gitignore")
                
        except Exception as e:
            print(f"⚠️ Could not save token: {e}")
        
        return token
    
    return None

def push_to_github():
    """Auto-push updated JSON files to GitHub with token authentication"""
    try:
        print("\n🚀 PUSHING TO GITHUB...")
        print("-" * 50)
        
        # Get current directory (your project root)
        project_root = Path(__file__).parent.absolute()
        os.chdir(project_root)
        
        # Check if this is a git repository
        if not (project_root / ".git").exists():
            print("❌ Not a git repository. Initialize with 'git init' first.")
            return False
        
        # Set up authentication
        token = setup_github_auth()
        
        # Get remote URL
        try:
            result = subprocess.run(["git", "remote", "get-url", "origin"], 
                                  capture_output=True, text=True, check=True)
            remote_url = result.stdout.strip()
            print(f"📡 Remote URL: {remote_url}")
        except subprocess.CalledProcessError:
            print("❌ No remote 'origin' found. Set up your GitHub repository first.")
            return False
        
        # If we have a token, update the remote URL to use it
        if token:
            # Extract username and repo from URL
            if "github.com/" in remote_url:
                # Handle both SSH and HTTPS URLs
                if remote_url.startswith("git@github.com:"):
                    # Convert SSH to HTTPS with token
                    repo_path = remote_url.replace("git@github.com:", "").replace(".git", "")
                    new_url = f"https://{token}@github.com/{repo_path}.git"
                elif remote_url.startswith("https://github.com/"):
                    # Add token to existing HTTPS URL
                    repo_path = remote_url.replace("https://github.com/", "").replace(".git", "")
                    new_url = f"https://{token}@github.com/{repo_path}.git"
                elif ":" in remote_url and "@github.com" in remote_url:
                    # URL already has credentials, keep as is
                    new_url = remote_url
                else:
                    new_url = remote_url
                
                # Update remote URL temporarily
                subprocess.run(["git", "remote", "set-url", "origin", new_url], check=False)
                print("✅ Updated remote URL with authentication")
        
        # Add the JSON files
        data_path = get_data_path()
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
            
            # Push to GitHub (handle upstream branch setup)
            push_result = subprocess.run(["git", "push"], capture_output=True, text=True)
            
            # If push fails due to no upstream, set it up
            if push_result.returncode != 0 and "no upstream branch" in push_result.stderr:
                print("🔧 Setting up upstream branch...")
                # Get current branch name
                branch_result = subprocess.run(["git", "branch", "--show-current"], 
                                             capture_output=True, text=True)
                current_branch = branch_result.stdout.strip() if branch_result.returncode == 0 else "master"
                
                # Set upstream and push
                push_result = subprocess.run(["git", "push", "--set-upstream", "origin", current_branch], 
                                           capture_output=True, text=True)
            
            if push_result.returncode == 0:
                print("🚀 Successfully pushed to GitHub!")
                print("🔄 Vercel will auto-deploy your updates")
                return True
            else:
                print(f"❌ Push failed: {push_result.stderr}")
                if "authentication" in push_result.stderr.lower():
                    print("💡 Authentication failed. Check your GitHub token.")
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
    
    print("🚀" * 40)
    print(f"LIVE BETTING DATA UPDATE - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🚀" * 40)
    
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
    print("-" * 50)
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
    print("-" * 50)
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

# Main execution
if __name__ == "__main__":
    # Get data path first
    data_path = get_data_path()
    
    # Check current data freshness
    check_data_freshness(data_path)
    
    # Run main update
    results = enhanced_update_all()

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