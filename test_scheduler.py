#!/usr/bin/env python3
import time
from datetime import datetime, timedelta
import pytz
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

def test_job():
    print(f"⏰ Test job executed at {datetime.now().isoformat()}")

def main():
    print("Starting scheduler test...")
    
    # Create scheduler
    scheduler = BackgroundScheduler(
        timezone=pytz.UTC,
        job_defaults={
            'coalesce': True,
            'misfire_grace_time': 3600
        }
    )
    
    # Start scheduler
    scheduler.start()
    print(f"Scheduler started at {datetime.now().isoformat()}")
    print(f"Scheduler timezone: {scheduler.timezone}")
    print(f"Scheduler running status: {scheduler.running}")
    
    # Add a test job to run every 5 seconds
    next_run_time = datetime.now(pytz.UTC) + timedelta(seconds=2)
    job = scheduler.add_job(
        func=test_job,
        trigger=IntervalTrigger(seconds=5),
        id="test_job",
        name="Test Job",
        next_run_time=next_run_time
    )
    
    print(f"Job scheduled to start at: {next_run_time.isoformat()}")
    print(f"Current time: {datetime.now(pytz.UTC).isoformat()}")
    print("Waiting for job executions...")
    
    # Wait for job executions
    try:
        for i in range(3):
            time.sleep(10)
            print(f"Current time: {datetime.now().isoformat()}")
            print(f"Next run time: {job.next_run_time.isoformat() if job.next_run_time else None}")
    except KeyboardInterrupt:
        print("Test interrupted")
    finally:
        print("Shutting down scheduler...")
        scheduler.shutdown()
        print("Scheduler shutdown complete")

if __name__ == "__main__":
    main()
