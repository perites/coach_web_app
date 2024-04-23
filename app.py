import logging

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import logout_user, current_user, login_required

# import tools
from login_logic import login_manager, authenticate
from flask_bootstrap import Bootstrap5
from flask_wtf import CSRFProtect
from forms import LoginForm, EditSingleSessionForm, EditGroupSessionForm
import datetime
import random
import base64
import web_confg
from tools import get_session_by_week, tx, error_catcher, get_week_dates, get_session_by_id, get_all_clients, confg, \
    get_client_by_id, get_group_session_by_id, get_all_coaches, get_coach_by_id, session_delete_client

app = Flask(__name__)
log = logging.getLogger('werkzeug')
log.disabled = True

app.config["SECRET_KEY"] = 'c42e8d7afdsdfds56342385cb9e30b6b'
login_manager.init_app(app)
bootstrap = Bootstrap5(app)
csfr = CSRFProtect(app)
app.config['IMAGES'] = 'templates/images'


@app.route("/login", methods=["GET", "POST"])
# @error_catcher
def login():
    if request.method == "GET":
        return render_template("login.html", form=LoginForm())

    form = request.form.to_dict()
    username = form["username"]
    password = form["password"]

    return authenticate(username, password)


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


@app.route('/admin/sessions')
@login_required
def admin_single_sessions():
    request_dict = request.args.to_dict()
    if not (week_number := request_dict.get("week")):
        week_number = datetime.datetime.now().isocalendar()[1]
        return redirect(f'/admin/sessions?week={week_number}')

    week_number = int(week_number)
    sessions = get_session_by_week(week_number)
    first_last_dates = get_week_dates(datetime.datetime.now().year, week_number)

    return render_template("admin_one_week_sessions.html",
                           sessions=sessions,
                           status_colors=web_confg.status_colors,
                           enumerate=enumerate,
                           week_number=week_number,
                           first_last_dates=first_last_dates,
                           )


@app.route("/admin/edit/session/<session_id>")
@login_required
def edit_session(session_id):
    session = get_session_by_id(session_id)
    if not session:
        return render_template("error.html", message="Індивідуальна сесія з таким айді не знайдена")

    form = EditSingleSessionForm()
    form.status.choices = list(map(lambda n: f"{n[1][1]} {n[0]}", confg.SESSIONS_STATUSES.items()))
    form.status.default = f"{confg.SESSIONS_STATUSES[session.status][1]} {session.status}"
    form.add_client.choices = list(
        map(lambda n: tx.user_representation(n, unmark=False), list(get_all_clients()))) + ['Нікого']
    form.process()
    return render_template("edit_single_session.html", form=form,
                           session=session,
                           client_text=tx.user_representation(session.client) if session.client else "Ще немає")


@app.route("/admin/edit/session/<session_id>", methods=["POST"])
@login_required
def edit_session_post(session_id):
    session = get_session_by_id(session_id)
    form = request.form.to_dict()

    session_old_status = session.status
    session.status = int(form['status'][-1])
    logging.info(
        f"Session with id {session.id}| Updating status:s {int(form['status'][-1])}, old status: {session_old_status}")

    if form.get("delete_client"):
        deleted_client_id = session.client.id if session.client else "No client"
        session.client = None
        session.booked_at = None
        session.status = 1
        logging.info(f"Session with id {session.id}| Deleted client with id {deleted_client_id} successfully")

    if form['add_client'] != "Нікого":
        client_id = form['add_client'].split("id:")[1]
        client = get_client_by_id(client_id)
        old_client_id = session.client.id if session.client else "No client"
        session.client = client
        session.booked_at = datetime.datetime.now(confg.KYIV_TZ)
        session.status = 2
        logging.info(
            f"Session with id {session.id}| Added client with id {client_id} successfully, old client id: {old_client_id}")

    session.save()
    logging.info(f"Session with id {session.id} | All changes applied successfully.")
    return redirect(f"/admin/edit/session/{session_id}")


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


@app.route('/admin/groups')
@login_required
def admin_one_week_group_sessions():
    request_dict = request.args.to_dict()
    if not (week_number := request_dict.get("week")):
        week_number = datetime.datetime.now().isocalendar()[1]
        return redirect(f'/admin/groups?week={week_number}')

    week_number = int(week_number)
    sessions_and_clients = get_session_by_week(week_number, groups=True)
    first_last_dates = get_week_dates(datetime.datetime.now().year, week_number)

    return render_template("admin_one_week_group_sessions.html",
                           sessions_and_clients=sessions_and_clients,
                           group_status_colors=web_confg.group_status_colors,
                           enumerate=enumerate,
                           week_number=week_number,
                           first_last_dates=first_last_dates,
                           ukr_type=tx.ukr_group_type)


@app.route("/admin/edit/group/<session_id>")
@login_required
def edit_group_session(session_id):
    session = get_group_session_by_id(session_id)
    if not session:
        return render_template("error.html", message="Сесія групового типу з таким айді не знайдена")

    clients = session.clients

    form = EditGroupSessionForm()
    form.status.choices = list(map(lambda n: f"{n[1][1]} {n[0]}", confg.GROUP_SESSIONS_STATUSES.items()))
    form.status.default = f"{confg.GROUP_SESSIONS_STATUSES[session.status][1]} {session.status}"

    form.date.default = session.date
    form.starting_time.default = session.starting_time

    form.change_coach.choices = list(
        map(lambda n: tx.user_representation(n, coach=True, unmark=False), list(get_all_coaches())))
    form.change_coach.default = tx.user_representation(session.coach, coach=True, unmark=False)

    form.delete_client.choices = list(
        map(lambda n: tx.user_representation(n.client, unmark=False), list(clients))) + ['Нікого']
    form.process()

    return render_template("edit_group_session.html", form=form, session=session)


@app.route("/admin/edit/group/<session_id>", methods=["POST"])
@login_required
def edit_group_session_post(session_id):
    session = get_group_session_by_id(session_id)
    form = request.form.to_dict()

    new_coach = get_coach_by_id(form['change_coach'].split("id:")[1])
    date = datetime.datetime.strptime(form['date'], '%Y-%m-%d')
    starting_time = datetime.datetime.strptime(form['starting_time'], "%H:%M").time()

    session_status = int(form['status'][-1])
    if form['delete_client'] != "Нікого":
        delete_client = get_client_by_id(form['delete_client'].split("id:")[1])
    else:
        delete_client = None

    logging.info(f"Updating group session with id {session.id} and parameters "
                 f"[status:{session.status} to {session_status},"
                 f" coach:{session.coach} to {new_coach},"
                 f" date:{session.date} to {date},"
                 f"starting_time:{starting_time},"
                 f"clients: {list(map(lambda n: n.client.id, session.clients))},"
                 f"delete client: {delete_client}")
    session.status = session_status
    session.coach = new_coach
    session.date = date
    session.starting_time = starting_time
    session_delete_client(session, delete_client) if delete_client else None

    session.save()

    return redirect(f'/admin/edit/group/{session_id}')


@app.route('/regenerate')
def regenerate():
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
