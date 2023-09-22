import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MonkeyGameStore.settings')
django.setup()
from rq_scheduler import Scheduler
from redis import Redis
import coupons.models
import coupons.tasks

scheduler = Scheduler(connection=Redis(host="redis_service"))

def start_coupon(id):
    coupon = coupons.models.Coupon.objects.get(id = id)
    coupon.status = 'Active'
    job = scheduler.enqueue_at(coupon.valid_till,coupons.tasks.end_coupon,coupon.id)
    coupon.end_job_id = job.id
    coupon.save()

def end_coupon(id):
    coupon = coupons.models.Coupon.objects.get(id = id)
    if coupon.status != 'Expired':
        coupon.status ='Expired'
        coupon.save()
