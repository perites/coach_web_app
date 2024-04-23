import sys
import logging
from peewee import fn
import web_confg
from flask import render_template
import datetime

sys.path.append(web_confg.PATH_TO_DB_MODELS)
from models import Session, GroupSession, GroupSessionToClients, Client, Coach
from texts import Text
from database import get_session_by_id, get_client_by_chat_id, get_group_session_by_id
import confg

tx = Text()

logging.basicConfig(format='%(levelname)s: %(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                    filename=web_confg.LOG_PATH, filemode='w', level=logging.INFO, encoding='utf-8')

error_logger = logging.getLogger('error_logger')
error_handler = logging.FileHandler(web_confg.ERROR_LOG_PATH)
error_formatter = logging.Formatter('%(levelname)s: %(asctime)s - %(message)s')
error_handler.setFormatter(error_formatter)
error_logger.addHandler(error_handler)
error_logger.setLevel(logging.ERROR)
error_logger.propagate = False


def get_client_by_id(client_id):
    client = Client.get_by_id(client_id)
    return client


def session_delete_client(session, client):
    session_to_client = GroupSessionToClients.get(
        GroupSessionToClients.group_session == session,
        GroupSessionToClients.client == client
    )

    logging.info(f'Deleting client with id {client.id} from group session with id {session.id}')

    session_to_client.delete_instance()
    session_to_client.save()

    return


def get_coach_by_id(coach_id):
    coach = Coach.get_by_id(coach_id)
    return coach


def get_session_by_week(week_number, groups=False):
    if groups:
        sessions_and_clients = list()
        sessions = GroupSession.select().where(fn.DATE_PART('week', GroupSession.date) == week_number).order_by(
            GroupSession.date,
            GroupSession.starting_time)

        for session in sessions:
            clients = GroupSessionToClients.select().where(GroupSessionToClients.group_session == session)
            clients = map(lambda n: n.client, clients)

            sessions_and_clients.append((session, clients))

        return sessions_and_clients

    sessions = Session.select().where(fn.DATE_PART('week', Session.date) == week_number).order_by(Session.date,
                                                                                                  Session.starting_time)
    return sessions


def get_all_clients():
    clients = Client.select()

    return clients


def get_all_coaches():
    coaches = Coach.select()

    return Coach


def error_catcher(func):
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except Exception as e:
            return render_template("error_page.html", error=e)

    return wrapper


def get_week_dates(year, week_number):
    first_day = datetime.datetime(year, 1, 1)
    first_day_of_week = first_day + datetime.timedelta(days=(week_number - 1) * 7 - first_day.weekday())
    last_day_of_week = first_day_of_week + datetime.timedelta(days=6)
    return f"{first_day_of_week:%d.%m}", f"{last_day_of_week:%d.%m}"
