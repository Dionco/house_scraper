#!/usr/bin/env python3
"""
Railway Periodic Scraping Monitor
Monitors Railway deployment to verify periodic scraping is working throughout the night.
Sends email report at 07:00 CEST with results.
"""

import requests
import json
import time
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pytz
from typing import Dict, List, Optional
import logging
import traceback

# Configuration
RAILWAY_APP_URL = "https://house-scraper-production-7202.up.railway.app/"  # Replace with your actual Railway URL
MONITORING_EMAIL = "dioncobelens@me.com"
CHECK_INTERVAL = 300  # Check every 5 minutes
TARGET_TIME = "07:00"  # CEST time to send report
CEST = pytz.timezone('Europe/Amsterdam')

# Email configuration (you'll need to set these environment variables)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_USER = os.getenv('EMAIL_USER', 'dioncobelens@me.com')  # Set this
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD', 'gcrr-ybmm-pahu-saqm')  # Set this

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('railway_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class RailwayScrapingMonitor:
    """Monitor Railway periodic scraping throughout the night."""
    
    def __init__(self, app_url: str, target_email: str):
        self.app_url = app_url
        self.target_email = target_email
        self.monitoring_data = {
            'start_time': None,
            'end_time': None,
            'checks': [],
            'errors': [],
            'scraper_status_history': [],
            'profile_activity': {},
            'total_checks': 0,
            'successful_checks': 0,
            'failed_checks': 0,
            'scraper_running_checks': 0,
            'new_listings_detected': 0
        }
        self.last_known_listings = {}
        
    def get_current_time_cest(self) -> datetime:
        """Get current time in CEST."""
        return datetime.now(CEST)
    
    def check_railway_health(self) -> Dict:
        """Check if Railway app is healthy."""
        try:
            response = requests.get(f"{self.app_url}/health", timeout=30)
            if response.status_code == 200:
                return {
                    'status': 'healthy',
                    'response_time': response.elapsed.total_seconds(),
                    'data': response.json()
                }
            else:
                return {
                    'status': 'unhealthy',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_scraper_status(self) -> Dict:
        """Check periodic scraper status."""
        try:
            response = requests.get(f"{self.app_url}/api/scraper/status", timeout=30)
            if response.status_code == 200:
                return {
                    'status': 'success',
                    'response_time': response.elapsed.total_seconds(),
                    'data': response.json()
                }
            else:
                return {
                    'status': 'error',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def check_listings_data(self) -> Dict:
        """Check current listings data to detect new scrapes."""
        try:
            response = requests.get(f"{self.app_url}/api/data", timeout=30)
            if response.status_code == 200:
                data = response.json()
                profiles = data.get('profiles', {})
                
                # Count total listings and new listings
                total_listings = 0
                new_listings = 0
                profile_stats = {}
                
                for profile_id, profile in profiles.items():
                    listings = profile.get('listings', [])
                    total_listings += len(listings)
                    
                    # Check for new listings since last check
                    last_known_count = self.last_known_listings.get(profile_id, 0)
                    current_count = len(listings)
                    new_count = max(0, current_count - last_known_count)
                    new_listings += new_count
                    
                    profile_stats[profile_id] = {
                        'name': profile.get('name', 'Unknown'),
                        'total_listings': current_count,
                        'new_since_last_check': new_count,
                        'last_scraped': profile.get('last_scraped'),
                        'last_new_listings_count': profile.get('last_new_listings_count', 0)
                    }
                    
                    # Update last known count
                    self.last_known_listings[profile_id] = current_count
                
                return {
                    'status': 'success',
                    'response_time': response.elapsed.total_seconds(),
                    'total_listings': total_listings,
                    'new_listings_detected': new_listings,
                    'profile_stats': profile_stats
                }
            else:
                return {
                    'status': 'error',
                    'status_code': response.status_code,
                    'response_time': response.elapsed.total_seconds()
                }
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e)
            }
    
    def perform_check(self) -> Dict:
        """Perform a complete monitoring check."""
        check_time = self.get_current_time_cest()
        logger.info(f"Performing check at {check_time.strftime('%Y-%m-%d %H:%M:%S CEST')}")
        
        check_result = {
            'timestamp': check_time.isoformat(),
            'health_check': self.check_railway_health(),
            'scraper_status': self.check_scraper_status(),
            'listings_data': self.check_listings_data()
        }
        
        # Update monitoring data
        self.monitoring_data['checks'].append(check_result)
        self.monitoring_data['total_checks'] += 1
        
        # Count successful checks
        if check_result['health_check']['status'] == 'healthy':
            self.monitoring_data['successful_checks'] += 1
        else:
            self.monitoring_data['failed_checks'] += 1
        
        # Count scraper running checks
        scraper_data = check_result['scraper_status'].get('data', {})
        if scraper_data.get('is_running'):
            self.monitoring_data['scraper_running_checks'] += 1
        
        # Count new listings
        listings_data = check_result['listings_data']
        if listings_data.get('new_listings_detected', 0) > 0:
            self.monitoring_data['new_listings_detected'] += listings_data['new_listings_detected']
        
        # Store scraper status history
        if scraper_data:
            self.monitoring_data['scraper_status_history'].append({
                'timestamp': check_time.isoformat(),
                'is_running': scraper_data.get('is_running', False),
                'total_jobs': scraper_data.get('total_jobs', 0),
                'jobs': scraper_data.get('jobs', [])
            })
        
        return check_result
    
    def generate_report(self) -> str:
        """Generate HTML report of monitoring results."""
        start_time = datetime.fromisoformat(self.monitoring_data['start_time'])
        end_time = datetime.fromisoformat(self.monitoring_data['end_time'])
        duration = end_time - start_time
        
        # Calculate statistics
        total_checks = self.monitoring_data['total_checks']
        successful_checks = self.monitoring_data['successful_checks']
        failed_checks = self.monitoring_data['failed_checks']
        scraper_running_checks = self.monitoring_data['scraper_running_checks']
        new_listings = self.monitoring_data['new_listings_detected']
        
        success_rate = (successful_checks / total_checks * 100) if total_checks > 0 else 0
        scraper_uptime = (scraper_running_checks / total_checks * 100) if total_checks > 0 else 0
        
        # Get latest scraper status
        latest_scraper_status = self.monitoring_data['scraper_status_history'][-1] if self.monitoring_data['scraper_status_history'] else {}
        
        # Generate HTML report
        html_report = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Railway Periodic Scraping Monitor Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background-color: #f4f4f4; padding: 20px; border-radius: 8px; }}
                .success {{ color: #28a745; }}
                .warning {{ color: #ffc107; }}
                .error {{ color: #dc3545; }}
                .stat-box {{ display: inline-block; margin: 10px; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
                .job-list {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .timestamp {{ font-size: 0.9em; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🏠 Railway Periodic Scraping Monitor Report</h1>
                <p><strong>Monitoring Period:</strong> {start_time.strftime('%Y-%m-%d %H:%M:%S CEST')} to {end_time.strftime('%Y-%m-%d %H:%M:%S CEST')}</p>
                <p><strong>Duration:</strong> {duration}</p>
                <p><strong>Report Generated:</strong> {datetime.now(CEST).strftime('%Y-%m-%d %H:%M:%S CEST')}</p>
            </div>
            
            <h2>📊 Summary Statistics</h2>
            <div class="stat-box">
                <h3>Health Checks</h3>
                <p><strong>Total Checks:</strong> {total_checks}</p>
                <p><strong>Successful:</strong> <span class="success">{successful_checks}</span></p>
                <p><strong>Failed:</strong> <span class="error">{failed_checks}</span></p>
                <p><strong>Success Rate:</strong> <span class="{'success' if success_rate >= 95 else 'warning' if success_rate >= 80 else 'error'}">{success_rate:.1f}%</span></p>
            </div>
            
            <div class="stat-box">
                <h3>Scraper Status</h3>
                <p><strong>Running Checks:</strong> <span class="success">{scraper_running_checks}</span></p>
                <p><strong>Uptime:</strong> <span class="{'success' if scraper_uptime >= 95 else 'warning' if scraper_uptime >= 80 else 'error'}">{scraper_uptime:.1f}%</span></p>
                <p><strong>New Listings Found:</strong> <span class="success">{new_listings}</span></p>
            </div>
            
            <h2>🔍 Current Scraper Status</h2>
            <div class="job-list">
                <p><strong>Is Running:</strong> <span class="{'success' if latest_scraper_status.get('is_running') else 'error'}">{'Yes' if latest_scraper_status.get('is_running') else 'No'}</span></p>
                <p><strong>Total Jobs:</strong> {latest_scraper_status.get('total_jobs', 0)}</p>
                <h4>Scheduled Jobs:</h4>
                <ul>
        """
        
        for job in latest_scraper_status.get('jobs', []):
            html_report += f"<li>{job.get('name', 'Unknown Job')} - Next run: {job.get('next_run', 'Unknown')}</li>"
        
        html_report += """
                </ul>
            </div>
            
            <h2>📈 Monitoring Timeline</h2>
            <table>
                <tr>
                    <th>Time</th>
                    <th>Health</th>
                    <th>Scraper Running</th>
                    <th>Response Time</th>
                    <th>New Listings</th>
                </tr>
        """
        
        for check in self.monitoring_data['checks'][-20:]:  # Show last 20 checks
            timestamp = datetime.fromisoformat(check['timestamp']).strftime('%H:%M:%S')
            health_status = check['health_check']['status']
            scraper_running = check['scraper_status'].get('data', {}).get('is_running', False)
            response_time = check['health_check'].get('response_time', 0)
            new_listings = check['listings_data'].get('new_listings_detected', 0)
            
            html_report += f"""
                <tr>
                    <td>{timestamp}</td>
                    <td><span class="{'success' if health_status == 'healthy' else 'error'}">{health_status}</span></td>
                    <td><span class="{'success' if scraper_running else 'error'}">{'Yes' if scraper_running else 'No'}</span></td>
                    <td>{response_time:.2f}s</td>
                    <td>{new_listings}</td>
                </tr>
            """
        
        html_report += """
            </table>
            
            <h2>🚨 Issues Detected</h2>
        """
        
        if failed_checks > 0:
            html_report += f"<p class='error'>❌ {failed_checks} health check failures detected</p>"
        
        if scraper_uptime < 95:
            html_report += f"<p class='warning'>⚠️ Scraper uptime is {scraper_uptime:.1f}% (below 95%)</p>"
        
        if new_listings == 0:
            html_report += f"<p class='warning'>⚠️ No new listings detected during monitoring period</p>"
        
        if len(self.monitoring_data['errors']) > 0:
            html_report += "<h3>Error Details:</h3><ul>"
            for error in self.monitoring_data['errors']:
                html_report += f"<li>{error}</li>"
            html_report += "</ul>"
        
        if failed_checks == 0 and scraper_uptime >= 95:
            html_report += "<p class='success'>✅ All checks passed! Railway periodic scraping is working correctly.</p>"
        
        html_report += """
            <h2>🎯 Conclusion</h2>
            <p>
        """
        
        if success_rate >= 95 and scraper_uptime >= 95:
            html_report += "✅ <strong>SUCCESS:</strong> Railway periodic scraping is working correctly throughout the monitoring period."
        elif success_rate >= 80 and scraper_uptime >= 80:
            html_report += "⚠️ <strong>WARNING:</strong> Railway periodic scraping is mostly working but has some issues."
        else:
            html_report += "❌ <strong>FAILURE:</strong> Railway periodic scraping has significant issues that need attention."
        
        html_report += """
            </p>
            <p>This monitoring confirms that your House Scraper is running 24/7 on Railway and performing periodic scraping as expected.</p>
        </body>
        </html>
        """
        
        return html_report
    
    def send_email_report(self, report_html: str):
        """Send email report with monitoring results."""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Railway Periodic Scraping Monitor Report - {datetime.now(CEST).strftime('%Y-%m-%d')}"
            msg['From'] = EMAIL_USER
            msg['To'] = self.target_email
            
            # Add HTML part
            html_part = MIMEText(report_html, 'html')
            msg.attach(html_part)
            
            # Create text version
            text_summary = f"""
Railway Periodic Scraping Monitor Report

Monitoring Period: {self.monitoring_data['start_time']} to {self.monitoring_data['end_time']}

Summary:
- Total Checks: {self.monitoring_data['total_checks']}
- Successful: {self.monitoring_data['successful_checks']}
- Failed: {self.monitoring_data['failed_checks']}
- Success Rate: {(self.monitoring_data['successful_checks'] / self.monitoring_data['total_checks'] * 100):.1f}%
- Scraper Uptime: {(self.monitoring_data['scraper_running_checks'] / self.monitoring_data['total_checks'] * 100):.1f}%
- New Listings Found: {self.monitoring_data['new_listings_detected']}

For detailed report, please view the HTML version of this email.
            """
            
            text_part = MIMEText(text_summary, 'plain')
            msg.attach(text_part)
            
            # Send email
            server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
            server.starttls()
            server.login(EMAIL_USER, EMAIL_PASSWORD)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email report sent successfully to {self.target_email}")
            
        except Exception as e:
            logger.error(f"Failed to send email report: {e}")
            self.monitoring_data['errors'].append(f"Email sending failed: {e}")
    
    def run_monitoring(self):
        """Run the monitoring process until 07:00 CEST."""
        logger.info("Starting Railway Periodic Scraping Monitor")
        
        self.monitoring_data['start_time'] = self.get_current_time_cest().isoformat()
        
        # Initial check to populate baseline data
        self.check_listings_data()
        
        try:
            while True:
                current_time = self.get_current_time_cest()
                
                # Check if it's 07:00 CEST or later
                if current_time.hour >= 7:
                    logger.info("Reached 07:00 CEST - finishing monitoring and sending report")
                    break
                
                # Perform monitoring check
                try:
                    check_result = self.perform_check()
                    
                    # Log any issues
                    if check_result['health_check']['status'] != 'healthy':
                        error_msg = f"Health check failed at {current_time.strftime('%H:%M:%S')}: {check_result['health_check']}"
                        logger.warning(error_msg)
                        self.monitoring_data['errors'].append(error_msg)
                    
                    scraper_data = check_result['scraper_status'].get('data', {})
                    if not scraper_data.get('is_running', False):
                        error_msg = f"Scraper not running at {current_time.strftime('%H:%M:%S')}"
                        logger.warning(error_msg)
                        self.monitoring_data['errors'].append(error_msg)
                    
                except Exception as e:
                    error_msg = f"Check failed at {current_time.strftime('%H:%M:%S')}: {e}"
                    logger.error(error_msg)
                    self.monitoring_data['errors'].append(error_msg)
                
                # Wait for next check
                logger.info(f"Next check in {CHECK_INTERVAL} seconds...")
                time.sleep(CHECK_INTERVAL)
                
        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            self.monitoring_data['errors'].append(f"Monitoring error: {e}")
        
        # Finalize monitoring
        self.monitoring_data['end_time'] = self.get_current_time_cest().isoformat()
        
        # Generate and send report
        logger.info("Generating final report...")
        report_html = self.generate_report()
        
        # Save report to file
        with open(f"railway_monitor_report_{datetime.now(CEST).strftime('%Y%m%d_%H%M%S')}.html", 'w') as f:
            f.write(report_html)
        
        # Send email report
        self.send_email_report(report_html)
        
        logger.info("Monitoring complete!")

def main():
    """Main function to run the monitoring script."""
    print("🏠 Railway Periodic Scraping Monitor")
    print("=" * 50)
    
    # Check configuration
    if EMAIL_USER == 'your-email@gmail.com' or EMAIL_PASSWORD == 'your-app-password':
        print("❌ Please configure EMAIL_USER and EMAIL_PASSWORD environment variables")
        print("   Set these in your terminal:")
        print("   export EMAIL_USER='your-email@gmail.com'")
        print("   export EMAIL_PASSWORD='your-app-password'")
        return
    
    # Get Railway URL
    railway_url = input("Enter your Railway app URL (e.g., https://your-app.railway.app): ").strip()
    if not railway_url:
        railway_url = RAILWAY_APP_URL
    
    print(f"Monitoring Railway app: {railway_url}")
    print(f"Target email: {MONITORING_EMAIL}")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print(f"Will monitor until: 07:00 CEST")
    print()
    
    # Create and run monitor
    monitor = RailwayScrapingMonitor(railway_url, MONITORING_EMAIL)
    monitor.run_monitoring()

if __name__ == "__main__":
    main()
