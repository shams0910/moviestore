import os
from celery import Celery
from celery.schedules import crontab
from scrapping import scrape

app = Celery(
    "tasks",
    broker="redis://redis",
    backend="redis://redis/0"
)


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=1, day_of_week=1),
        call_scrape.s(),
        name='scrape every 20'
    )


@app.task
def call_scrape():
    scrape(db_url=os.environ.get("DB_HOST"))
