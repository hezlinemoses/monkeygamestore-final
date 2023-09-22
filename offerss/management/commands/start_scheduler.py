from traceback import print_tb
from django.core.management.base import BaseCommand, CommandError
from redis import Redis
from rq import Queue
from rq_scheduler import Scheduler
from datetime import datetime, timedelta,timezone
from datetime import timedelta
from redis import Redis

from rq import Worker,Queue
from rq.registry import ScheduledJobRegistry


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        # This is necessary to prevent dupes
        scheduler = Scheduler(connection=Redis(host='redis_service'))
        list_of_job_instances = scheduler.get_jobs()
        for job in list_of_job_instances:
            print(job)


