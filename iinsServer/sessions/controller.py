from datetime import datetime, timedelta
from uuid import uuid4
from flask import request, json, session
from flask.sessions import SessionInterface
from . import models
from pymongo import MongoClient
from flask import g

class SystemService():
    def __init__(self):
        self.model = models

    def sessions(self):
        if request.method == 'GET':
            input_data = request.args
            if input_data["datatype"] in session.keys():
                session_output = session[input_data["datatype"]]
                session.pop(input_data["datatype"])
            else:
                session_output = {}
            return json.dumps(session_output)
        elif request.method == 'POST':
            input_data = json.loads(request.data)
            session[input_data["datatype"]] = input_data
            return json.dumps({"status": "success"})
        else:
            return "Error"


class MongoSessionInterface(SessionInterface):
    def __init__(self, collection='sessions'):
        self.db = MongoClient('localhost', 27017).db_meta[collection]

    def open_session(self, app, request):
        sid = request.cookies.get(app.session_cookie_name)
        if sid:
            stored_session = self.db.find_one({'sid': sid})
            if stored_session:
                if stored_session.get('expiration') > datetime.utcnow():
                    return models.MongoSession(initial=stored_session['data'],
                                               sid=stored_session['sid'])
        sid = str(uuid4())
        return models.MongoSession(sid=sid)

    def save_session(self, app, session, response):
        domain = self.get_cookie_domain(app)
        if not session:
            response.delete_cookie(app.session_cookie_name, domain=domain)
            return
        if self.get_expiration_time(app, session):
            expiration = self.get_expiration_time(app, session)
        else:
            expiration = datetime.utcnow() + timedelta(hours=1)
        self.db.update({'sid': session.sid},
                       {'sid': session.sid,
                        'data': session,
                        'expiration': expiration}, True)
        response.set_cookie(app.session_cookie_name, session.sid,
                            expires=self.get_expiration_time(app, session),
                            httponly=True, domain=domain)