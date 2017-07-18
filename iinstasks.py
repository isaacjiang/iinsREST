#!flask/bin/python
from __future__ import absolute_import, unicode_literals
import eventlet
eventlet.monkey_patch()

from celery import current_app
from celery.bin import worker,beat
from multiprocessing import  Process
import iinsREST.iinsTasks

cworker = worker.worker(app=current_app._get_current_object())
cbeat = beat.beat(app=current_app._get_current_object())
options =current_app.conf['worker_options']

proc0 = Process(target=cbeat.run, kwargs=options['beat'])
proc1 = Process(target=cworker.run, kwargs=options['default'])

proc0.start()
proc1.start()



