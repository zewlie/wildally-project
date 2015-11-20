from celery.task import task
from redis import Redis
from model import connect_to_db, User, Org, Animal, Click, ClickFilter
from server import app, load_click_info_from_db
from datetime import datetime, date, timedelta
import os

app.debug = False
connect_to_db(app)

@task()
def test_task():

    gathered_clicks = import_gathered_clicks()
    insert = insert_clicks_into_db(gathered_clicks)
    reset = reset_gathered_clicks()

    click_info_from_db = load_click_info_from_db()
    orgs, animals, clicks, click_filters = click_info_from_db

    for org in orgs:

        org_id = org.id

        now = datetime.now()
        today = now.date()

        previous_weeks = 3
        previous_days = 6
        previous_hours = 23

        analytics = {
                     "month": {},
                     "week": {},
                     "day": {},
                     "filters": { "all": {},
                                  "day": {},
                                  "week": {},
                                  "month": {}, 
                                  },
                     "allfilters": { "all": {},
                                     "day": {},
                                     "week": {},
                                     "month": {}, 
                                  },
                     }

        for animal in animals:
            for key in analytics["filters"]:
                analytics["filters"][key][str(animal.id)] = [animal.name, 0]
                analytics["filters"][key]["volunteers"] = ["volunteers", 0]
                analytics["filters"][key]["none"] = ["none", 0]

                analytics["allfilters"][key][str(animal.id)] = [animal.name, 0]
                analytics["allfilters"][key]["volunteers"] = ["volunteers", 0]
                analytics["allfilters"][key]["none"] = ["none", 0]


        while previous_weeks >= 0:
            week_end = today - timedelta(days=(6 + (previous_weeks * 7)))
            week_start = week_end + timedelta(days=6)
            analytics["month"]["week" + str(previous_weeks)] = [date.strftime(week_start, "%m/%d") + " - " + date.strftime(week_end, "%m/%d"), 0]
            previous_weeks -= 1

        while previous_days >= 0:
            day = today - timedelta(days=previous_days)
            analytics["week"]["day" + str(previous_days)] = [date.strftime(day, "%m/%d"), 0]
            # analytics["week"].append(["day" + str(previous_days), date.strftime(day, "%m/%d"), 0])
            previous_days -= 1

        while previous_hours >= 0:
            hour_start = now - timedelta(hours=previous_hours)
            hour_end = hour_start + timedelta(hours=1)
            analytics["day"]["hour" + str(previous_hours)] = [date.strftime(hour_start, "%I %p").lstrip("0") + " - " + date.strftime(hour_end, "%I %p").lstrip("0"), 0]
            previous_hours -= 1

        for click in clicks:

            for click_filter in click.click_filters:
                if str(click_filter.filter_id) in analytics["allfilters"]["month"].keys():
                    analytics["allfilters"]["all"][str(click_filter.filter_id)][1] += 1
                elif str(click_filter.filter_id) == "volun":
                    analytics["allfilters"]["all"]["volunteers"][1] += 1
                elif click_filter.filter_id == "":
                    analytics["allfilters"]["all"]["none"][1] += 1

            if click.org_id == org_id:

                for click_filter in click.click_filters:
                    if str(click_filter.filter_id) in analytics["filters"]["month"].keys():
                        analytics["filters"]["all"][str(click_filter.filter_id)][1] += 1
                    elif str(click_filter.filter_id) == "volun":
                        analytics["filters"]["all"]["volunteers"][1] += 1
                    elif click_filter.filter_id == "":
                        analytics["filters"]["all"]["none"][1] += 1

            day_delta = (today - click.time.date()).days
            hour_delta = 100

            # If a click occured yesterday, compare the remaining time (before midnight) against the current time's time since midnight
            # This will give the hour_delta across days
            if day_delta == 1:
                yesterday_seconds_remaining = 86400 - (click.time.hour * 3600) + (click.time.minute * 60) + click.time.second
                today_seconds = (now.hour * 3600) + (now.minute * 60) + now.second
                hour_delta = (yesterday_seconds_remaining + today_seconds) / 3600
            elif day_delta == 0:
                hour_delta = (now - click.time).seconds / 3600

            if day_delta < 7:

                for click_filter in click.click_filters:
                        if str(click_filter.filter_id) in analytics["allfilters"]["week"].keys():
                            analytics["allfilters"]["week"][str(click_filter.filter_id)][1] += 1
                            analytics["allfilters"]["month"][str(click_filter.filter_id)][1] += 1
                        elif str(click_filter.filter_id) == "volun":
                            analytics["allfilters"]["week"]["volunteers"][1] += 1
                            analytics["allfilters"]["month"]["volunteers"][1] += 1
                        elif click_filter.filter_id == "":
                            analytics["allfilters"]["week"]["none"][1] += 1
                            analytics["allfilters"]["month"]["none"][1] += 1

                if click.org_id == org_id:

                    analytics["week"]["day" + str(day_delta)][1] += 1
                    analytics["month"]["week0"][1] += 1

                    for click_filter in click.click_filters:
                        if str(click_filter.filter_id) in analytics["filters"]["week"].keys():
                            analytics["filters"]["week"][str(click_filter.filter_id)][1] += 1
                            analytics["filters"]["month"][str(click_filter.filter_id)][1] += 1
                        elif str(click_filter.filter_id) == "volun":
                            analytics["filters"]["week"]["volunteers"][1] += 1
                            analytics["filters"]["month"]["volunteers"][1] += 1
                        elif click_filter.filter_id == "":
                            analytics["filters"]["week"]["none"][1] += 1
                            analytics["filters"]["month"]["none"][1] += 1

            elif day_delta < 28:

                for click_filter in click.click_filters:
                    if str(click_filter.filter_id) in analytics["allfilters"]["month"].keys():
                        analytics["allfilters"]["month"][str(click_filter.filter_id)][1] += 1
                    elif str(click_filter.filter_id) == "volun":
                        analytics["allfilters"]["month"]["volunteers"][1] += 1
                    elif click_filter.filter_id == "":
                        analytics["allfilters"]["month"]["none"][1] += 1

                if click.org_id == org_id:

                    analytics["month"]["week" + str((day_delta / 7) + 1)][1] += 1

                    for click_filter in click.click_filters:
                        if str(click_filter.filter_id) in analytics["filters"]["month"].keys():
                            analytics["filters"]["month"][str(click_filter.filter_id)][1] += 1
                        elif str(click_filter.filter_id) == "volun":
                            analytics["filters"]["month"]["volunteers"][1] += 1
                        elif click_filter.filter_id == "":
                            analytics["filters"]["month"]["none"][1] += 1

            if hour_delta < 24:

                for click_filter in click.click_filters:
                    if str(click_filter.filter_id) in analytics["allfilters"]["month"].keys():
                        analytics["allfilters"]["day"][str(click_filter.filter_id)][1] += 1
                    elif str(click_filter.filter_id) == "volun":
                        analytics["allfilters"]["day"]["volunteers"][1] += 1
                    elif click_filter.filter_id == "":
                        analytics["allfilters"]["day"]["none"][1] += 1

                if click.org_id == org_id:

                    analytics["day"]["hour" + str(hour_delta)][1] += 1

                    for click_filter in click.click_filters:
                        if str(click_filter.filter_id) in analytics["filters"]["month"].keys():
                            analytics["filters"]["day"][str(click_filter.filter_id)][1] += 1
                        elif str(click_filter.filter_id) == "volun":
                            analytics["filters"]["day"]["volunteers"][1] += 1
                        elif click_filter.filter_id == "":
                            analytics["filters"]["day"]["none"][1] += 1

            # for click_filter2 in click.click_filters:
            #     if str(click_filter2.filter_id) in analytics["allfilters"].keys():
            #         analytics["allfilters"][str(click_filter2.filter_id)][1] += 1
            #     elif click_filter2.filter_id == "volun":
            #         analytics["allfilters"]["volunteers"][1] += 1
            #     elif click_filter2.filter_id == "":
            #         analytics["allfilters"]["none"][1] += 1

        with open(os.path.join("./static/user/analytics/analytics_" + str(org_id) + ".txt"), 'wb') as analytics_json:
            analytics_json.write(str(analytics))

        analytics_json.close()

 
    return None