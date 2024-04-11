import sys
from peewee import fn
import web_confg

sys.path.append(web_confg.PATH_TO_DB_MODELS)
from models import Session, GroupSession, GroupSessionToClients
from texts import Text

tx = Text()


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
