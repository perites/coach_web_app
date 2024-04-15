from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import datetime
import random
import base64
import web_confg
from tools import get_session_by_week, tx

app = Flask(__name__)
app.config['IMAGES'] = 'templates/images'


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
    sessions = get_session_by_week(week_number)
    first_last_dates = get_week_dates(datetime.datetime.now().year, week_number)

    return render_template("one_week_sessions.html",
                           sessions=sessions,
                           status_colors=web_confg.status_colors,
                           enumerate=enumerate,
                           week_number=week_number,
                           first_last_dates=first_last_dates,
                           )


@app.route('/groups')
def one_week_group_sessions():
    request_dict = request.args.to_dict()
    if not (week_number := request_dict.get("week")):
        week_number = datetime.datetime.now().isocalendar()[1]
        return redirect(f'/groups?week={week_number}')

    week_number = int(week_number)
    sessions_and_clients = get_session_by_week(week_number, groups=True)
    first_last_dates = get_week_dates(datetime.datetime.now().year, week_number)

    return render_template("one_week_group_sessions.html",
                           sessions_and_clients=sessions_and_clients,
                           group_status_colors=web_confg.group_status_colors,
                           enumerate=enumerate,
                           week_number=week_number,
                           first_last_dates=first_last_dates,
                           ukr_type=tx.ukr_group_type)


def get_week_dates(year, week_number):
    first_day = datetime.datetime(year, 1, 1)
    first_day_of_week = first_day + datetime.timedelta(days=(week_number - 1) * 7 - first_day.weekday())
    last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
    return f"{first_day_of_week:%d.%m}", f"{last_day_of_week:%d.%m}"


@app.route('/generate')
def generate():
    random_index = random.randint(0, len(web_confg.IMAGES_NAMES) - 1)
    index = random_index.to_bytes(length=1, byteorder='big')

    encrypted_index = web_confg.cipher.encrypt(index)
    encrypted_index_b64 = base64.urlsafe_b64encode(encrypted_index).decode()

    return redirect(url_for('image', encrypted_index=encrypted_index_b64))


@app.route('/map/<encrypted_index>')
def image(encrypted_index):
    return render_template("map.html", file_url=url_for("get_image", encrypted_index=encrypted_index))


@app.route("/get-image/<encrypted_index>")
def get_image(encrypted_index):
    encrypted_index_bytes = base64.urlsafe_b64decode(encrypted_index)
    index = int.from_bytes(web_confg.cipher.decrypt(encrypted_index_bytes), byteorder='big')
    image_name = web_confg.IMAGES_NAMES[index]
    return send_from_directory(app.config['IMAGES'], image_name)


if __name__ == '__main__':
    app.run()
