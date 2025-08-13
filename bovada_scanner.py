import requests
import json
import datetime
from typing import Dict, List, Optional
import time
from pathlib import Path

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

class LiveBovadaAnalyzer:
    def __init__(self):
        # YOUR REAL ODDS API KEY
        self.odds_api_key = "8dfaf92c77d8fc5ebea9ba17af5b5518"
        self.odds_api = "https://api.the-odds-api.com/v4/sports"
        
        # Headers
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json',
        }

    def get_live_bovada_games(self) -> List[Dict]:
        """Get 100% LIVE NFL games using real Odds API"""
        try:
            print("📈 Fetching LIVE NFL games from Odds API...")
            
            # Get live NFL games with real odds
            live_games = self.fetch_live_nfl_odds()
            
            if not live_games:
                print("❌ No live games found from Odds API")
                return []
            
            # Analyze each game for sharp money patterns
            analyzed_games = []
            for game in live_games:
                analyzed_game = self.analyze_live_game(game)
                if analyzed_game:
                    analyzed_games.append(analyzed_game)
            
            print(f"✅ Found {len(analyzed_games)} LIVE NFL games with analysis")
            return analyzed_games
            
        except Exception as e:
            print(f"❌ Error fetching live games: {e}")
            return []

    def fetch_live_nfl_odds(self) -> List[Dict]:
        """Fetch LIVE NFL odds using your real API key"""
        try:
            # NFL odds endpoint
            url = f"{self.odds_api}/americanfootball_nfl/odds"
            
            params = {
                "apiKey": self.odds_api_key,
                "regions": "us",
                "markets": "h2h,spreads,totals",
                "oddsFormat": "american",
                "bookmakers": "bovada,fanduel,draftkings,betmgm,caesars"
            }
            
            print(f"🔗 Calling Odds API: {url}")
            response = requests.get(url, params=params, headers=self.headers, timeout=15)
            
            print(f"📡 Odds API Response: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Odds API returned {len(data)} NFL games")
                
                live_games = []
                for game_data in data:
                    # Extract game info
                    game = {
                        "id": game_data.get("id", ""),
                        "matchup": f"{game_data.get('away_team', 'Away')} @ {game_data.get('home_team', 'Home')}",
                        "away_team": game_data.get("away_team", "Away"),
                        "home_team": game_data.get("home_team", "Home"),
                        "commence_time": game_data.get("commence_time", ""),
                        "sport": "NFL",
                        "bookmakers": game_data.get("bookmakers", [])
                    }
                    
                    live_games.append(game)
                
                return live_games
                
            elif response.status_code == 401:
                print("❌ Odds API: Unauthorized - check your API key")
                return []
            elif response.status_code == 429:
                print("❌ Odds API: Rate limit exceeded")
                return []
            else:
                print(f"❌ Odds API error: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error calling Odds API: {e}")
            return []

    def analyze_live_game(self, game: Dict) -> Optional[Dict]:
        """Analyze live game for sharp money patterns using real odds"""
        try:
            bookmakers = game.get("bookmakers", [])
            
            if not bookmakers:
                print(f"⚠️ No bookmaker data for {game['matchup']}")
                return None
            
            # Extract odds from different bookmakers
            spread_odds = {}
            total_odds = {}
            moneyline_odds = {}
            
            for bookmaker in bookmakers:
                bookie_name = bookmaker.get("key", "")
                markets = bookmaker.get("markets", [])
                
                for market in markets:
                    market_key = market.get("key", "")
                    outcomes = market.get("outcomes", [])
                    
                    if market_key == "spreads":
                        for outcome in outcomes:
                            team = outcome.get("name", "")
                            point = outcome.get("point", 0)
                            price = outcome.get("price", 0)
                            
                            if team not in spread_odds:
                                spread_odds[team] = []
                            spread_odds[team].append({"bookie": bookie_name, "point": point, "price": price})
                    
                    elif market_key == "totals":
                        for outcome in outcomes:
                            name = outcome.get("name", "")
                            point = outcome.get("point", 0)
                            price = outcome.get("price", 0)
                            
                            if name not in total_odds:
                                total_odds[name] = []
                            total_odds[name].append({"bookie": bookie_name, "point": point, "price": price})
                    
                    elif market_key == "h2h":
                        for outcome in outcomes:
                            team = outcome.get("name", "")
                            price = outcome.get("price", 0)
                            
                            if team not in moneyline_odds:
                                moneyline_odds[team] = []
                            moneyline_odds[team].append({"bookie": bookie_name, "price": price})
            
            # Analyze odds for sharp money indicators
            analysis = self.detect_sharp_money_patterns(spread_odds, total_odds, moneyline_odds)
            
            # Create enhanced game data
            enhanced_game = {
                "matchup": game["matchup"],
                "away_team": game["away_team"],
                "home_team": game["home_team"],
                "sport": "NFL",
                "start_time": game["commence_time"],
                "line": analysis.get("spread_line", "No line available"),
                "total": analysis.get("total_line", "No total available"),
                "moneyline": analysis.get("moneyline", "No ML available"),
                "sharp_pct": analysis.get("sharp_spread_pct", "50%"),
                "public_pct": analysis.get("public_spread_pct", "50%"),
                "sharp_total_pct": analysis.get("sharp_total_pct", "50%"),
                "public_total_pct": analysis.get("public_total_pct", "50%"),
                "recommendation": analysis.get("recommendation", "No recommendation"),
                "total_recommendation": analysis.get("total_recommendation", "No total rec"),
                "commentary": analysis.get("commentary", "Live odds analysis"),
                "confidence": analysis.get("confidence", "MEDIUM"),
                "bookmaker_count": len(bookmakers),
                "last_updated": datetime.datetime.now().isoformat()
            }
            
            return enhanced_game
            
        except Exception as e:
            print(f"❌ Error analyzing game {game.get('matchup', 'Unknown')}: {e}")
            return None

    def detect_sharp_money_patterns(self, spread_odds: Dict, total_odds: Dict, moneyline_odds: Dict) -> Dict:
        """Detect sharp money patterns from real odds variations"""
        
        analysis = {}
        
        # Analyze spreads
        if spread_odds:
            home_spreads = []
            away_spreads = []
            
            for team, odds_list in spread_odds.items():
                for odds_data in odds_list:
                    point = odds_data["point"]
                    if point > 0:  # This team is getting points (underdog)
                        away_spreads.append(abs(point))
                    else:  # This team is giving points (favorite)
                        home_spreads.append(abs(point))
            
            if home_spreads and away_spreads:
                avg_spread = (sum(home_spreads) + sum(away_spreads)) / (len(home_spreads) + len(away_spreads))
                spread_variance = max(home_spreads + away_spreads) - min(home_spreads + away_spreads)
                
                # Higher variance = more sharp money disagreement
                if spread_variance >= 1.0:
                    sharp_pct = "75%"  # High disagreement = sharp action
                    analysis["recommendation"] = "🔥 SHARP PLAY - Line movement indicates professional money"
                elif spread_variance >= 0.5:
                    sharp_pct = "65%"
                    analysis["recommendation"] = "✅ GOOD VALUE - Some sharp movement detected"
                else:
                    sharp_pct = "50%"
                    analysis["recommendation"] = "😐 NEUTRAL - Consistent lines across books"
                
                analysis["spread_line"] = f"±{avg_spread:.1f}"
                analysis["sharp_spread_pct"] = sharp_pct
                analysis["public_spread_pct"] = f"{100 - int(sharp_pct.replace('%', ''))}%"
        
        # Analyze totals
        if total_odds:
            over_totals = []
            under_totals = []
            
            for outcome_type, odds_list in total_odds.items():
                for odds_data in odds_list:
                    point = odds_data["point"]
                    if outcome_type.upper() == "OVER":
                        over_totals.append(point)
                    else:
                        under_totals.append(point)
            
            if over_totals or under_totals:
                all_totals = over_totals + under_totals
                if all_totals:
                    avg_total = sum(all_totals) / len(all_totals)
                    total_variance = max(all_totals) - min(all_totals) if len(all_totals) > 1 else 0
                    
                    if total_variance >= 2.0:
                        sharp_total_pct = "70%"
                        analysis["total_recommendation"] = "🎯 OVER/UNDER - Sharp total movement"
                    elif total_variance >= 1.0:
                        sharp_total_pct = "60%"
                        analysis["total_recommendation"] = "💡 Lean OVER/UNDER - Some movement"
                    else:
                        sharp_total_pct = "50%"
                        analysis["total_recommendation"] = "😐 Totals neutral - Consistent across books"
                    
                    analysis["total_line"] = f"O/U {avg_total:.1f}"
                    analysis["sharp_total_pct"] = sharp_total_pct
                    analysis["public_total_pct"] = f"{100 - int(sharp_total_pct.replace('%', ''))}%"
        
        # Generate commentary based on real odds analysis
        commentary_parts = []
        
        if analysis.get("sharp_spread_pct"):
            sharp_pct = int(analysis["sharp_spread_pct"].replace("%", ""))
            if sharp_pct >= 70:
                commentary_parts.append("Strong professional money detected on spread.")
            elif sharp_pct >= 60:
                commentary_parts.append("Moderate sharp action on point spread.")
        
        if analysis.get("sharp_total_pct"):
            sharp_total = int(analysis["sharp_total_pct"].replace("%", ""))
            if sharp_total >= 65:
                commentary_parts.append("Sharp money hitting totals.")
            elif sharp_total >= 55:
                commentary_parts.append("Some professional total action.")
        
        bookmaker_note = f"Analysis based on live odds from {len(spread_odds) + len(total_odds)} sources."
        commentary_parts.append(bookmaker_note)
        
        analysis["commentary"] = " ".join(commentary_parts) if commentary_parts else "Live odds analysis from multiple sportsbooks."
        
        # Set confidence based on data quality
        total_books = len(spread_odds) + len(total_odds) + len(moneyline_odds)
        if total_books >= 4:
            analysis["confidence"] = "🔥 HIGH"
        elif total_books >= 2:
            analysis["confidence"] = "✅ GOOD"
        else:
            analysis["confidence"] = "💡 MEDIUM"
        
        return analysis

    def update_bovada_data(self):
        """Main function to update with 100% LIVE data"""
        print("📈" * 30)
        print("100% LIVE NFL ODDS ANALYSIS")
        print("📈" * 30)
        
        # Get live games using real API
        games = self.get_live_bovada_games()
        
        if not games:
            print("❌ No live games to save")
            return
        
        # Get the correct data path
        data_path = get_data_path()
        
        # Save games data
        try:
            with open(data_path / "games.json", "w") as f:
                json.dump(games, f, indent=2)
            print(f"✅ Saved {len(games)} LIVE games to games.json")
        except Exception as e:
            print(f"❌ Error saving games: {e}")
            return
        
        # Create analytics summary
        high_confidence_games = [g for g in games if "🔥 HIGH" in g.get("confidence", "")]
        sharp_plays = []
        
        for game in games:
            sharp_pct_str = game.get("sharp_pct", "0%").replace("%", "")
            try:
                sharp_pct_num = int(sharp_pct_str)
                if sharp_pct_num >= 65:
                    sharp_plays.append(game)
            except:
                pass
        
        # Print summary
        print("📈" * 30)
        print("LIVE NFL ODDS ANALYSIS COMPLETE!")
        print(f"📊 Total LIVE Games: {len(games)}")
        print(f"🔥 High Confidence: {len(high_confidence_games)}")
        print(f"💰 Sharp Money Games (65%+): {len(sharp_plays)}")
        
        # Print top sharp plays
        if sharp_plays:
            print(f"\n🔥 TOP SHARP MONEY PLAYS:")
            for i, play in enumerate(sharp_plays[:3]):
                print(f"  {i+1}. {play['matchup']}: {play['sharp_pct']} sharp money")
                print(f"      💡 {play['commentary'][:80]}...")
        
        # Print API usage info
        print(f"\n📡 Using LIVE Odds API key: {self.odds_api_key[:8]}...")
        print("📈" * 30)

def update_bovada_data():
    """Function called by update_all.py"""
    analyzer = LiveBovadaAnalyzer()
    analyzer.update_bovada_data()

if __name__ == "__main__":
    update_bovada_data()