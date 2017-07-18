from celery import signals
from celery.app import app_or_default
from importlib import import_module

capp = app_or_default()

from .models import TasksManagement


@capp.task(name='initializationTasks')
def initializationTasks():

    print('Done initializationTasks tasks."')

@capp.task(name='setupPeriodicTasks')
def setupPeriodicTasks(queue):
    tasks= TasksManagement().getTasks(queue)
    for t in tasks:
        t["_id"]=str(t['_id'])
        taskName = t['taskName'].split('@')[0]
        functionName = taskName[taskName.rfind('.')+1:len(taskName)]
        moduleName = taskName[0:taskName.rfind('.')]+'.tasks'
        if moduleName and functionName:
            task = getattr(import_module(moduleName),functionName)
            task.apply_async(args=[t],queue=t['queue'],routing_key=queue+'_tasks')
            if 'duration' in t.keys() and t['duration'] !=0:
                TasksManagement().stopTaskByName(t['taskName'])
    # return 'Done setupPeriodicTasks tasks. '+module+' '+ queue


@signals.task_success.connect
def task_success_handler(sender=None, result=None, **kwargs):
    if sender.name in ['TasksScheduler.tasksSV.getPortsOverviewStatus','TasksScheduler.tasksSV.getDeviceEnvInfo']:
        result['_id'] =str(result['_id'])
        functionName = sender.name[sender.name.rfind('.')+1:len(sender.name)]
        # Emiter().emit(functionName,[result],room=functionName+"@"+result['IP'])
        print('task success : '+ sender.name)

@signals.task_failure.connect
def task_failure_handler(sender=None, task_id=None, args=None,exception=None, **kwargs):
    print('task failure : '+ sender.name,task_id,args,exception)