#!/usr/bin/env python3
"""
Simple Railway Monitor - No Email Setup Required
This version saves the report to a file and prints results to console.
You can manually check the results and send them to yourself.
"""

import requests
import json
import time
from datetime import datetime, timedelta
import pytz
from typing import Dict, List
import os

# Configuration
RAILWAY_APP_URL = "https://house-scraper-production-7202.up.railway.app/"  # Replace with your actual URL
CHECK_INTERVAL = 300  # Check every 5 minutes
TARGET_TIME = 7  # 07:00 CEST
CEST = pytz.timezone('Europe/Amsterdam')

class SimpleRailwayMonitor:
    """Simple Railway monitoring without email dependencies."""
    
    def __init__(self, app_url: str):
        self.app_url = app_url
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def check_railway_app(self) -> Dict:
        """Check Railway app status."""
        current_time = datetime.now(CEST)
        
        try:
            # Health check
            health_response = requests.get(f"{self.app_url}/health", timeout=10)
            health_ok = health_response.status_code == 200
            
            # Scraper status
            scraper_response = requests.get(f"{self.app_url}/api/scraper/status", timeout=10)
            scraper_ok = scraper_response.status_code == 200
            scraper_data = scraper_response.json() if scraper_ok else {}
            
            # Listings data
            data_response = requests.get(f"{self.app_url}/api/data", timeout=10)
            data_ok = data_response.status_code == 200
            
            result = {
                'time': current_time.strftime('%Y-%m-%d %H:%M:%S CEST'),
                'timestamp': current_time.isoformat(),
                'health_ok': health_ok,
                'scraper_ok': scraper_ok,
                'data_ok': data_ok,
                'scraper_running': scraper_data.get('is_running', False),
                'total_jobs': scraper_data.get('total_jobs', 0),
                'jobs': scraper_data.get('jobs', []),
                'response_times': {
                    'health': health_response.elapsed.total_seconds() if health_ok else 0,
                    'scraper': scraper_response.elapsed.total_seconds() if scraper_ok else 0,
                    'data': data_response.elapsed.total_seconds() if data_ok else 0
                }
            }
            
            # Count total listings
            if data_ok:
                data_json = data_response.json()
                profiles = data_json.get('profiles', {})
                total_listings = sum(len(p.get('listings', [])) for p in profiles.values())
                new_listings = sum(len([l for l in p.get('listings', []) if l.get('is_new', False)]) for p in profiles.values())
                result['total_listings'] = total_listings
                result['new_listings'] = new_listings
            else:
                result['total_listings'] = 0
                result['new_listings'] = 0
                
            return result
            
        except Exception as e:
            return {
                'time': current_time.strftime('%Y-%m-%d %H:%M:%S CEST'),
                'timestamp': current_time.isoformat(),
                'error': str(e),
                'health_ok': False,
                'scraper_ok': False,
                'data_ok': False,
                'scraper_running': False,
                'total_jobs': 0,
                'jobs': [],
                'total_listings': 0,
                'new_listings': 0
            }
    
    def print_status(self, result: Dict):
        """Print current status to console."""
        status = "✅" if result['health_ok'] and result['scraper_ok'] and result['scraper_running'] else "❌"
        print(f"{status} {result['time']} | Health: {result['health_ok']} | Scraper: {result['scraper_running']} | Jobs: {result['total_jobs']} | Listings: {result['total_listings']}")
        
        if result.get('error'):
            print(f"   Error: {result['error']}")
    
    def generate_summary(self) -> str:
        """Generate summary report."""
        if not self.results:
            return "No monitoring data collected."
        
        total_checks = len(self.results)
        successful_checks = sum(1 for r in self.results if r['health_ok'] and r['scraper_ok'])
        scraper_running_checks = sum(1 for r in self.results if r['scraper_running'])
        
        success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0
        scraper_uptime = (scraper_running_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Get latest status
        latest = self.results[-1]
        
        summary = f"""
🏠 Railway Periodic Scraping Monitor Report
{'=' * 50}

Monitoring Period: {self.start_time} to {self.end_time}
Total Duration: {self.end_time - self.start_time}

📊 Summary Statistics:
- Total Checks: {total_checks}
- Successful Checks: {successful_checks}
- Success Rate: {success_rate:.1f}%
- Scraper Uptime: {scraper_uptime:.1f}%

🔍 Latest Status:
- Time: {latest['time']}
- Health OK: {latest['health_ok']}
- Scraper Running: {latest['scraper_running']}
- Total Jobs: {latest['total_jobs']}
- Total Listings: {latest['total_listings']}
- New Listings: {latest['new_listings']}

📋 Scheduled Jobs:
"""
        
        for job in latest.get('jobs', []):
            summary += f"- {job.get('name', 'Unknown')}: {job.get('next_run', 'Unknown')}\n"
        
        summary += f"\n🎯 Conclusion:\n"
        if success_rate >= 95 and scraper_uptime >= 95:
            summary += "✅ SUCCESS: Railway periodic scraping is working correctly!"
        elif success_rate >= 80 and scraper_uptime >= 80:
            summary += "⚠️ WARNING: Railway periodic scraping is mostly working but has some issues."
        else:
            summary += "❌ FAILURE: Railway periodic scraping has significant issues."
        
        return summary
    
    def save_detailed_report(self):
        """Save detailed report to JSON file."""
        report_data = {
            'monitoring_period': {
                'start': self.start_time.isoformat(),
                'end': self.end_time.isoformat(),
                'duration': str(self.end_time - self.start_time)
            },
            'summary': {
                'total_checks': len(self.results),
                'successful_checks': sum(1 for r in self.results if r['health_ok'] and r['scraper_ok']),
                'scraper_running_checks': sum(1 for r in self.results if r['scraper_running']),
                'success_rate': (sum(1 for r in self.results if r['health_ok'] and r['scraper_ok']) / len(self.results) * 100) if self.results else 0,
                'scraper_uptime': (sum(1 for r in self.results if r['scraper_running']) / len(self.results) * 100) if self.results else 0
            },
            'detailed_results': self.results
        }
        
        filename = f"railway_monitor_detailed_{datetime.now(CEST).strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w') as f:
            json.dump(report_data, f, indent=2)
        
        print(f"📄 Detailed report saved to: {filename}")
    
    def run_monitoring(self):
        """Run the monitoring until 07:00 CEST."""
        print("🏠 Railway Periodic Scraping Monitor")
        print("=" * 50)
        print(f"Monitoring: {self.app_url}")
        print(f"Check interval: {CHECK_INTERVAL} seconds")
        print(f"Will monitor until: 07:00 CEST")
        print()
        
        self.start_time = datetime.now(CEST)
        
        try:
            while True:
                current_time = datetime.now(CEST)
                
                # Check if it's 07:00 CEST or later
                if current_time.hour >= TARGET_TIME:
                    print(f"\n✅ Reached {TARGET_TIME}:00 CEST - finishing monitoring")
                    break
                
                # Perform check
                result = self.check_railway_app()
                self.results.append(result)
                self.print_status(result)
                
                # Wait for next check
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            print("\n⏹️ Monitoring stopped by user")
        except Exception as e:
            print(f"\n❌ Monitoring error: {e}")
        
        self.end_time = datetime.now(CEST)
        
        # Generate and display summary
        print("\n" + "=" * 50)
        print("📊 FINAL REPORT")
        print("=" * 50)
        
        summary = self.generate_summary()
        print(summary)
        
        # Save detailed report
        self.save_detailed_report()
        
        # Create summary file
        summary_filename = f"railway_monitor_summary_{datetime.now(CEST).strftime('%Y%m%d_%H%M%S')}.txt"
        with open(summary_filename, 'w') as f:
            f.write(summary)
        print(f"📄 Summary report saved to: {summary_filename}")
        
        print("\n📧 To send this report to yourself, copy the summary above and email it to dioncobelens@me.com")

def main():
    """Main function."""
    # Get Railway URL
    railway_url = input("Enter your Railway app URL (or press Enter for default): ").strip()
    if not railway_url:
        # Try to detect from railway CLI
        try:
            import subprocess
            result = subprocess.run(['railway', 'domain'], capture_output=True, text=True)
            if result.returncode == 0 and result.stdout.strip():
                railway_url = f"https://{result.stdout.strip()}"
                print(f"📡 Auto-detected Railway URL: {railway_url}")
            else:
                railway_url = RAILWAY_APP_URL
                print("⚠️ Could not auto-detect Railway URL, using default")
        except:
            railway_url = RAILWAY_APP_URL
            print("⚠️ Please update RAILWAY_APP_URL in the script")
    
    # Test connection
    print(f"\n🔍 Testing connection to {railway_url}...")
    try:
        response = requests.get(f"{railway_url}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Connection successful!")
        else:
            print(f"⚠️ Connection returned status: {response.status_code}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("Please check your Railway URL and try again.")
        return
    
    # Create and run monitor
    monitor = SimpleRailwayMonitor(railway_url)
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
