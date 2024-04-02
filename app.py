from flask import Flask, render_template, request
import datetime

import sys

import web_confg

sys.path.append(web_confg.PATH_TO_DB_MODELS)
import database

app = Flask(__name__)


@app.route('/sessions')
def one_week_sessions():
    request_dict = request.args.to_dict()
    week_number = request_dict.get("week") or datetime.datetime.now().isocalendar()[1]

    sessions = database.get_session_by_week(week_number)

    return render_template("one_week_sessions.html", sessions=sessions, status_colors =web_confg.status_colors )


if __name__ == '__main__':
    app.run()
