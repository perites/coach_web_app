from flask import Flask, render_template, request, redirect
import datetime

import sys

import web_confg

sys.path.append(web_confg.PATH_TO_DB_MODELS)
import database

app = Flask(__name__)


@app.route('/')
def home():
    return redirect("/sessions")


@app.route('/sessions')
def one_week_sessions():
    request_dict = request.args.to_dict()
    if not (week_number := request_dict.get("week")):
        week_number = datetime.datetime.now().isocalendar()[1]
        return redirect(f'/sessions?week={week_number}')

    week_number = int(week_number)
    sessions = database.get_session_by_week(week_number)
    first_last_dates = get_week_dates(datetime.datetime.now().year, week_number)

    return render_template("one_week_sessions.html",
                           sessions=sessions,
                           status_colors=web_confg.status_colors,
                           enumerate=enumerate,
                           week_number=week_number,
                           first_last_dates=first_last_dates)


def get_week_dates(year, week_number):
    first_day = datetime.datetime(year, 1, 1)
    first_day_of_week = first_day + datetime.timedelta(days=(week_number - 1) * 7 - first_day.weekday())
    last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
    return (f"{first_day_of_week:%d.%m}", f"{last_day_of_week:%d.%m}")


if __name__ == '__main__':
    app.run()
