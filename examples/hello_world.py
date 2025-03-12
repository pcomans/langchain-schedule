from datetime import datetime, timedelta
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

def print_current_time():
    print(f"Current time is: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def print_message(message):
    print(f"Message: {message} at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    # Create a scheduler
    scheduler = BlockingScheduler()
    
    # Add a job that runs every 10 seconds
    scheduler.add_job(
        print_current_time,
        IntervalTrigger(seconds=10),
        id='time_printer'
    )
    
    # Add a job that runs once after 30 seconds
    scheduler.add_job(
        print_message,
        'date',
        run_date=datetime.now() + timedelta(seconds=30),
        args=['One-time task executed!'],
        id='one_time_task'
    )
    
    # Add a job that runs every minute on the 30th second
    scheduler.add_job(
        print_message,
        CronTrigger(second=30),
        args=['Cron job executed!'],
        id='cron_task'
    )
    
    print("Starting scheduler...")
    print("Press Ctrl+C to exit")
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        print("\nScheduler stopped.")

if __name__ == "__main__":
    main() 