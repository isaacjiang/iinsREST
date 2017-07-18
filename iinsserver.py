__author__ = 'Isaac Jiang'

from iinsServer import iinsapp
#
import eventlet
from gunicorn.workers import geventlet
from gunicorn.app.base import BaseApplication
from gunicorn.six import iteritems
from gunicorn import glogging

class GunicornApp(BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super(GunicornApp, self).__init__()

    def load_config(self):
        config = dict([(key, value) for key, value in iteritems(self.options)
                       if key in self.cfg.settings and value is not None])
        for key, value in iteritems(config):
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

if __name__ == "__main__":
    GunicornApp(iinsapp,{'bind': '%s:%s' % ('localhost', '5101'),'workers': 1,"worker_class":'eventlet'}).run()
    # socketio.run(netvisapp, host='localhost', port=5101, debug=True,use_reloader=True)
    # netvisapp.run(host='localhost', port=5101, debug=True)

