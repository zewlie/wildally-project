"""Celery tasks."""

from celery.task import task
from redis import Redis
from model import connect_to_db, User, Org, Animal, Click, ClickFilter
from server import app, update_analytics, load_click_info_from_db
from datetime import datetime, date, timedelta
import os

app.debug = False
connect_to_db(app)

@task()
def update_analytics_task():
    update_analytics()

    return None