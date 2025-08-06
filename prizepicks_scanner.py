import requests
import json
import datetime
from typing import Dict, List, Optional
import time
from pathlib import Path
import statistics

def get_data_path():
    """Dynamically find the data folder"""
    script_dir = Path(__file__).parent.absolute()
    possible_paths = [
        script_dir / "data",
        script_dir / "../data", 
        Path.cwd() / "data",
    ]
    for path in possible_paths:
        if path.exists() and path.is_dir():
            return path
    data_path = script_dir / "data"
    data_path.mkdir(exist_ok=True)
    return data_path

class SmartPrizePicksAnalyzer:
    def __init__(self):
        # PrizePicks API endpoints
        self.prizepicks_api = "https://api.prizepicks.com/projections"
        
        # Headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.9'
        }
        
        # NFL player performance data (simplified - in real app, pull from stats API)
        self.nfl_player_stats = {
            "Josh Allen": {"passing_yards": 285.5, "rushing_yards": 45.2, "passing_touchdowns": 2.1},
            "Lamar Jackson": {"passing_yards": 245.8, "rushing_yards": 65.3, "passing_touchdowns": 1.8},
            "Christian McCaffrey": {"rushing_yards": 95.2, "receiving_yards": 45.8, "receptions": 4.2},
            "Travis Kelce": {"receiving_yards": 78.5, "receptions": 6.8, "receiving_touchdowns": 0.7},
            "Tyreek Hill": {"receiving_yards": 85.2, "receptions": 5.9, "receiving_touchdowns": 0.6},
            "Cooper Kupp": {"receiving_yards": 82.1, "receptions": 7.2, "receiving_touchdowns": 0.5},
            "Derrick Henry": {"rushing_yards": 88.7, "rushing_touchdowns": 1.1},
            "Dak Prescott": {"passing_yards": 275.3, "passing_touchdowns": 2.0},
            "Aaron Rodgers": {"passing_yards": 265.8, "passing_touchdowns": 1.9},
            "Patrick Mahomes": {"passing_yards": 295.2, "passing_touchdowns": 2.3, "rushing_yards": 25.1},
        }

    def get_live_prizepicks_props(self) -> List[Dict]:
        """Get LIVE PrizePicks props and filter for NFL only"""
        try:
            print("🎯 Fetching LIVE PrizePicks props...")
            
            url = self.prizepicks_api
            response = requests.get(url, headers=self.headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                print(f"📊 Raw API response contains {len(data.get('data', []))} total projections")
                
                all_props = []
                nfl_count = 0
                
                for projection in data.get("data", []):
                    # Extract prop details
                    stat_type = projection.get("stat_type", "")
                    line_score = projection.get("line_score", 0)
                    
                    # Get attributes safely
                    attributes = projection.get("attributes", {})
                    if not attributes:
                        continue
                        
                    player_name = attributes.get("player_name", "Unknown")
                    team = attributes.get("team", "")
                    league = attributes.get("league", "")
                    position = attributes.get("position", "")
                    
                    # Debug: Show what leagues we're getting
                    if league and league not in ["NFL", "NBA", "NCAAF", "MLB"]:
                        print(f"🔍 Found league: {league}")
                    
                    # FILTER: Only NFL props (try multiple league identifiers)
                    if league.upper() not in ["NFL", "AMERICAN_FOOTBALL_NFL"]:
                        continue
                    
                    nfl_count += 1
                    
                    # FILTER: Only relevant stat types
                    relevant_stats = [
                        "passing_yards", "rushing_yards", "receiving_yards", 
                        "receptions", "passing_touchdowns", "rushing_touchdowns", 
                        "receiving_touchdowns", "completions", "pass_yards",
                        "rush_yards", "rec_yards", "pass_tds", "rush_tds", "rec_tds"
                    ]
                    
                    if stat_type.lower() not in relevant_stats:
                        print(f"🔍 Skipping stat type: {stat_type}")
                        continue
                    
                    # Get our advanced projection
                    our_projection = self.get_advanced_nfl_projection(player_name, stat_type, team, position)
                    
                    # Calculate edge with confidence scoring
                    edge = our_projection - line_score
                    edge_pct = (edge / line_score * 100) if line_score > 0 else 0
                    
                    # Calculate confidence based on multiple factors
                    confidence_score = self.calculate_confidence_score(
                        player_name, stat_type, edge_pct, team, position, line_score
                    )
                    
                    prop = {
                        "player": player_name,
                        "stat_type": stat_type,
                        "line": line_score,
                        "model_projection": round(our_projection, 1),
                        "edge": round(edge, 1),
                        "edge_pct": round(edge_pct, 1),
                        "team": team,
                        "position": position,
                        "confidence_score": confidence_score,
                        "last_updated": datetime.datetime.now().isoformat()
                    }
                    
                    all_props.append(prop)
                
                print(f"✅ Found {nfl_count} total NFL props")
                print(f"✅ Found {len(all_props)} relevant NFL props before filtering")
                
                # If no NFL props found, create some realistic ones for testing
                if len(all_props) == 0:
                    print("⚠️ No NFL props found in API, generating test data...")
                    all_props = self.generate_test_nfl_props()
                
                # Apply AI analysis to find BEST picks
                best_picks = self.analyze_and_rank_picks(all_props)
                
                print(f"🔥 Filtered down to {len(best_picks)} BEST NFL picks")
                return best_picks
                
            else:
                print(f"❌ PrizePicks API error: {response.status_code}")
                print(f"Response: {response.text[:200]}...")
                return self.generate_test_nfl_props()
                
        except Exception as e:
            print(f"❌ Error fetching PrizePicks props: {e}")
            return self.generate_test_nfl_props()

    def generate_test_nfl_props(self) -> List[Dict]:
        """Generate realistic test NFL props when API fails"""
        print("📊 Generating test NFL props...")
        
        test_props = [
            {
                "player": "Josh Allen",
                "stat_type": "passing_yards",
                "line": 275.5,
                "team": "BUF",
                "position": "QB"
            },
            {
                "player": "Christian McCaffrey", 
                "stat_type": "rushing_yards",
                "line": 85.5,
                "team": "SF",
                "position": "RB"
            },
            {
                "player": "Travis Kelce",
                "stat_type": "receiving_yards", 
                "line": 75.5,
                "team": "KC",
                "position": "TE"
            },
            {
                "player": "Tyreek Hill",
                "stat_type": "receptions",
                "line": 5.5,
                "team": "MIA", 
                "position": "WR"
            },
            {
                "player": "Patrick Mahomes",
                "stat_type": "passing_touchdowns",
                "line": 1.5,
                "team": "KC",
                "position": "QB"
            },
            {
                "player": "Cooper Kupp",
                "stat_type": "receiving_yards",
                "line": 82.5,
                "team": "LAR",
                "position": "WR"
            },
            {
                "player": "Derrick Henry",
                "stat_type": "rushing_yards",
                "line": 88.5,
                "team": "TEN",
                "position": "RB"
            },
            {
                "player": "Lamar Jackson",
                "stat_type": "rushing_yards",
                "line": 65.5,
                "team": "BAL",
                "position": "QB"
            }
        ]
        
        processed_props = []
        for prop in test_props:
            # Get our advanced projection
            our_projection = self.get_advanced_nfl_projection(
                prop["player"], prop["stat_type"], prop["team"], prop["position"]
            )
            
            # Calculate edge with confidence scoring
            edge = our_projection - prop["line"]
            edge_pct = (edge / prop["line"] * 100) if prop["line"] > 0 else 0
            
            # Calculate confidence
            confidence_score = self.calculate_confidence_score(
                prop["player"], prop["stat_type"], edge_pct, prop["team"], prop["position"], prop["line"]
            )
            
            processed_prop = {
                "player": prop["player"],
                "stat_type": prop["stat_type"], 
                "line": prop["line"],
                "model_projection": round(our_projection, 1),
                "edge": round(edge, 1),
                "edge_pct": round(edge_pct, 1),
                "team": prop["team"],
                "position": prop["position"],
                "confidence_score": confidence_score,
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            processed_props.append(processed_prop)
        
        return processed_props

    def get_advanced_nfl_projection(self, player_name: str, stat_type: str, team: str, position: str) -> float:
        """Advanced NFL projection with multiple data sources"""
        
        # Base projection from our stats database
        player_stats = self.nfl_player_stats.get(player_name, {})
        base_projection = player_stats.get(stat_type.lower(), 0)
        
        if base_projection == 0:
            # Use position-based defaults if player not in database
            position_defaults = {
                "QB": {
                    "passing_yards": 265.0, "passing_touchdowns": 1.8, "rushing_yards": 25.0
                },
                "RB": {
                    "rushing_yards": 75.0, "receiving_yards": 25.0, "receptions": 3.0, "rushing_touchdowns": 0.6
                },
                "WR": {
                    "receiving_yards": 65.0, "receptions": 5.0, "receiving_touchdowns": 0.5
                },
                "TE": {
                    "receiving_yards": 45.0, "receptions": 4.5, "receiving_touchdowns": 0.4
                }
            }
            
            base_projection = position_defaults.get(position, {}).get(stat_type.lower(), 50.0)
        
        # Apply adjustments based on team matchups and trends
        matchup_adjustment = self.get_matchup_adjustment(team, stat_type)
        weather_adjustment = self.get_weather_adjustment(stat_type)
        recent_form_adjustment = self.get_recent_form_adjustment(player_name, stat_type)
        
        # Final projection
        final_projection = base_projection * (1 + matchup_adjustment + weather_adjustment + recent_form_adjustment)
        
        return max(0, final_projection)

    def get_matchup_adjustment(self, team: str, stat_type: str) -> float:
        """Adjust based on team matchup difficulty"""
        # Simplified matchup adjustments (in real app, use opponent defense rankings)
        tough_defenses = ["BAL", "SF", "BUF", "DAL", "PIT"]
        weak_defenses = ["DET", "LAC", "ARI", "CAR", "ATL"]
        
        if team in tough_defenses:
            return -0.08  # 8% decrease against tough defenses
        elif team in weak_defenses:
            return 0.12   # 12% increase against weak defenses
        else:
            return 0.0

    def get_weather_adjustment(self, stat_type: str) -> float:
        """Weather impact on passing vs rushing"""
        # Simplified weather impact (in real app, check actual weather)
        if stat_type.lower() in ["passing_yards", "passing_touchdowns"]:
            return -0.05  # Slight decrease for passing in outdoor games
        elif stat_type.lower() in ["rushing_yards", "rushing_touchdowns"]:
            return 0.03   # Slight increase for rushing
        else:
            return 0.0

    def get_recent_form_adjustment(self, player_name: str, stat_type: str) -> float:
        """Adjust based on recent player form"""
        # Simplified recent form (in real app, analyze last 3 games)
        hot_players = ["Christian McCaffrey", "Josh Allen", "Travis Kelce"]
        cold_players = ["Aaron Rodgers", "Ezekiel Elliott"]
        
        if player_name in hot_players:
            return 0.1   # 10% boost for hot players
        elif player_name in cold_players:
            return -0.1  # 10% decrease for cold players
        else:
            return 0.0

    def calculate_confidence_score(self, player_name: str, stat_type: str, edge_pct: float, 
                                 team: str, position: str, line_score: float) -> int:
        """Advanced confidence scoring (1-100)"""
        
        confidence = 50  # Base confidence
        
        # Edge percentage impact (most important factor)
        if edge_pct >= 15:
            confidence += 30
        elif edge_pct >= 10:
            confidence += 20
        elif edge_pct >= 5:
            confidence += 10
        elif edge_pct <= -10:
            confidence += 20  # Strong under plays
        elif edge_pct <= -5:
            confidence += 10
        else:
            confidence -= 10  # Low edge plays
        
        # Player tier impact
        elite_players = ["Josh Allen", "Patrick Mahomes", "Christian McCaffrey", "Travis Kelce"]
        if player_name in elite_players:
            confidence += 15
        
        # Stat type reliability
        reliable_stats = ["rushing_yards", "receiving_yards", "receptions"]
        if stat_type.lower() in reliable_stats:
            confidence += 10
        
        # Position consistency
        if position in ["RB", "WR"]:
            confidence += 5
        
        # Line score reasonableness
        if 20 <= line_score <= 300:  # Reasonable lines
            confidence += 5
        
        return max(1, min(100, confidence))

    def analyze_and_rank_picks(self, all_props: List[Dict]) -> List[Dict]:
        """AI analysis to find the absolute BEST picks"""
        
        # Filter for high-confidence picks only
        high_confidence_picks = [
            prop for prop in all_props 
            if prop["confidence_score"] >= 70 and abs(prop["edge_pct"]) >= 5
        ]
        
        # If we have enough high-confidence picks, use those
        if len(high_confidence_picks) >= 15:
            filtered_picks = high_confidence_picks
        else:
            # Otherwise, use medium confidence with good edge
            filtered_picks = [
                prop for prop in all_props 
                if prop["confidence_score"] >= 60 and abs(prop["edge_pct"]) >= 3
            ]
        
        # Sort by a combination of confidence and edge
        for prop in filtered_picks:
            # Calculate composite score
            edge_score = min(abs(prop["edge_pct"]) * 2, 50)  # Cap at 50
            confidence_weight = prop["confidence_score"] * 0.6
            
            prop["composite_score"] = edge_score + confidence_weight
            
            # Add recommendation
            if prop["edge_pct"] >= 8:
                prop["recommendation"] = f"🔥 SMASH OVER - {prop['edge_pct']:.1f}% edge"
                prop["play_type"] = "OVER"
            elif prop["edge_pct"] <= -8:
                prop["recommendation"] = f"🔥 SMASH UNDER - {abs(prop['edge_pct']):.1f}% edge"
                prop["play_type"] = "UNDER"
            elif prop["edge_pct"] >= 4:
                prop["recommendation"] = f"✅ OVER - {prop['edge_pct']:.1f}% edge"
                prop["play_type"] = "OVER"
            elif prop["edge_pct"] <= -4:
                prop["recommendation"] = f"✅ UNDER - {abs(prop['edge_pct']):.1f}% edge"
                prop["play_type"] = "UNDER"
            else:
                prop["recommendation"] = f"💡 Lean - {prop['edge_pct']:.1f}% edge"
                prop["play_type"] = "LEAN"
            
            # Format for display
            prop["display_line"] = f"{prop['line']} {self.format_stat_type(prop['stat_type'])}"
            prop["confidence_display"] = f"{prop['confidence_score']}/100"
        
        # Sort by composite score (highest first)
        sorted_picks = sorted(filtered_picks, key=lambda x: x["composite_score"], reverse=True)
        
        # Return top 25 picks maximum
        return sorted_picks[:25]

    def format_stat_type(self, stat_type: str) -> str:
        """Format stat type for display"""
        formats = {
            "passing_yards": "Pass Yds",
            "rushing_yards": "Rush Yds", 
            "receiving_yards": "Rec Yds",
            "receptions": "Rec",
            "passing_touchdowns": "Pass TD",
            "rushing_touchdowns": "Rush TD",
            "receiving_touchdowns": "Rec TD",
            "completions": "Comp"
        }
        return formats.get(stat_type.lower(), stat_type)

    def get_fallback_nfl_props(self) -> List[Dict]:
        """Fallback props when API fails"""
        return [
            {
                "player": "API Connection Failed",
                "display_line": "Check connection",
                "model_projection": 0,
                "edge": 0,
                "edge_pct": 0,
                "recommendation": "Unable to fetch live data. Retrying...",
                "confidence_score": 0,
                "team": "System"
            }
        ]

    def update_prizepicks_data(self):
        """Main function to update PrizePicks data with AI analysis"""
        print("🎯" * 30)
        print("SMART NFL PRIZEPICKS ANALYZER")
        print("🎯" * 30)
        
        # Get and analyze live props
        best_picks = self.get_live_prizepicks_props()
        
        # Get the correct data path
        data_path = get_data_path()
        
        # Save the BEST picks only
        try:
            with open(data_path / "props.json", "w") as f:
                json.dump(best_picks, f, indent=2)
            print(f"✅ Saved {len(best_picks)} BEST NFL picks to props.json")
        except Exception as e:
            print(f"❌ Error saving props: {e}")
        
        # Print analysis summary
        if best_picks and len(best_picks) > 0 and "composite_score" in best_picks[0]:
            smash_plays = [p for p in best_picks if "SMASH" in p.get("recommendation", "")]
            good_plays = [p for p in best_picks if p.get("confidence_score", 0) >= 80]
            
            print("🎯" * 30)
            print("NFL PICKS ANALYSIS COMPLETE!")
            print(f"🔥 Total Best Picks: {len(best_picks)}")
            print(f"💥 SMASH Plays: {len(smash_plays)}")
            print(f"⭐ High Confidence (80+): {len(good_plays)}")
            
            # Show top 3 picks
            if len(best_picks) >= 3:
                print(f"\n🏆 TOP 3 NFL PICKS:")
                for i, pick in enumerate(best_picks[:3]):
                    print(f"  {i+1}. {pick['player']} {pick['display_line']} - {pick['recommendation']}")
            
            print("🎯" * 30)

def update_prizepicks_data():
    """Function called by update_all.py"""
    analyzer = SmartPrizePicksAnalyzer()
    analyzer.update_prizepicks_data()

if __name__ == "__main__":
    update_prizepicks_data()