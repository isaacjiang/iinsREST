from . import models
from flask import json, request

class WorkflowService():
    def __init__(self):
        self.model = models

    def getWorkflow(self):
        jobName = request.args.get('jobName')
        username = request.args.get('username')
        results = self.model.WorkFlowModel(jobName,username).getWorkflow()
        return json.dumps(results)

    def launchWorkflow(self):
        if request.method == 'POST':
            task = json.loads(request.data)
            if 'taskMethod' in task.keys():
                result=[]
                if task['taskMethod'] == 'editDevice':
                    workflow = self.model.WorkFlow('addDevice', task['username'])
                    for i in range(1, 7, 1):
                        workflow.update_task('addDevice', task['username'], i,
                                             {'data': task['data'], 'status': 'saved', 'canSetAddress': False,'method':"edit"})
                    result = workflow.get_all()
                    return result
                elif task['taskMethod'] == 'editPtn':
                    workflow = self.model.WorkFlow('addPtn', task['username'])
                    for i in range(1, 3, 1):
                        workflow.update_task('addPtn', task['username'], i,
                                             {'data': task['data'], 'status': 'saved', 'canSetAddress': False,'method':"edit"})
                    result = workflow.get_all()
                    return result
                elif task['taskMethod'] == 'addDeviceFromNode':
                    workflow = self.model.WorkFlow('addDevice', task['username'])
                    workflow.clear_user_all_task()
                    self.model.WorkFlow('addDevice', task['username']).__init__()
                    for i in range(1, 7, 1):
                        workflow.update_task('addDevice', task['username'], i,
                                         {'data.location': task['data'], 'status': 'normal', 'canSetAddress': False})
                    result = workflow.get_all()
                    return result

                # elif task['method'] == 'fromOpenAddress':
                #     workflow = self.model.WorkFlow('addDevice', task['username'])
                #     workflow.clear_user_all_task()
                #     self.model.WorkFlow('addDevice', task['username']).__init__()
                #     workflow.update_task('addDevice', task['username'], 1, {'data': task['data']})
                #     workflow.update_task('addDevice', task['username'], 4,
                #                          {'canSetAddress': False, 'data': task['data'],
                #                           'method': 'fromOpenAddress'})
                #     result = workflow.get_all()
                #     return result

            else:
                if task['back']:
                    # print 'back', task['processName'], task['username'], task['taskID']
                    workflow = self.model.WorkFlow(task['processName'], task['userName'])
                    workflow.fast_set(task['taskID'], False, data=task['data'], status='normal')
                    result = workflow.get_all()
                else:
                    # print 'next', task['processName'], task['username'], task['taskID']
                    workflow = self.model.WorkFlow(task['processName'], task['userName'])
                    workflow.fast_set(task['taskID'], True, data=task['data'], status='saved')
                    result = workflow.get_all()
                return result



    def clearworkflow(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            workflow = self.model.WorkFlow(data['processName'], data['username'])
            workflow.clear_user_all_task()
            results = workflow.get_all()
            return results
