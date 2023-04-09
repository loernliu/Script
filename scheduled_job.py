from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
import time


def print_test():
    print("--------------------")


job_defaults = {"misfire_grace_time": 30}
scheduler1 = BackgroundScheduler(job_defaults=job_defaults)
trigger1 = CronTrigger(second=20)
scheduler1.add_job(print_test, trigger=trigger1)
scheduler1.start()
while True:
    time.sleep(30)
