import importlib
import copy
from bson import ObjectId
from datetime import datetime
import time
from flask import g
from pymongo import MongoClient

class FileModel():
    def __init__(self, fileID=None):
        self._id = ObjectId(fileID)
        self.file_collection = getattr(g,'database',MongoClient('localhost', 27017)).db_file.fs.files
        self.chunk_collection = getattr(g,'database',MongoClient('localhost', 27017)).db_file.fs.chunks

        self.model_nodes = importlib.import_module("NetvisServer.nodes.models")
        self.model_devices = importlib.import_module("NetvisServer.devices.models")
        self.NodeModel = self.model_nodes.NodeModel
        self.DeviceModel = self.model_devices.DeviceModel

    def get(self):
        result = {}
        if self._id is not None:
            req = self.file_collection.find_one({"_id": self._id})
            if req is not None:
                req['_id'] = str(req['_id'])
                result = req
            return result

    def get_files_from_device(self, deviceID):
        results = []
        device = self.DeviceModel(ObjectId(deviceID)).get()
        if len(device['filenames']) > 0:
            for i, file in enumerate(device['filenames']):
                # pathCopy = copy.deepcopy(path)
                # pathCopy.append(i)
                results.append({"id": file['objectID'], "value": file['filename'], "size": file['length'],
                                "level": 3,
                                "type": file['content_type'],
                                "date": self.dateConverter(file['upload_date'])})
        return results

    def delete_file(self, deleteList):
        for id in deleteList:
            self.delete_one(id)

    def delete_one(self, id=None):
        self.file_collection.find_one_and_delete({'_id': ObjectId(id)})
        self.chunk_collection.find_one_and_delete({'files_id': ObjectId(id)})

    def dateConverter(self, strDate):
        # strDate formart like  ('%Y-%m-%d %H:%M:%S') to microseconds
        st = str(strDate).split('.')

        dt = st[0].split()
        d = dt[0].split('-')
        t = dt[1].split(':')
        return time.mktime((int(d[0]), int(d[1]), int(d[2]), int(t[0]), int(t[1]), int(t[2]), 0, 0, 0))

    def get_all_files(self):
        results = []
        nodes = self.NodeModel().get_all()

        for ind, node in enumerate(nodes):
            newName = node['nodeName'].split(',')
            if len(newName) == 1:
                nodeName = newName[0]
            else:
                nodeName = newName[0] + ', ' + newName[1]
            folder = {"_id": node['_id'], "value": nodeName, "size": 0, "open": False, "level": 0,
                      "bgc": {"background-color": "transparent"}, "path": [ind],
                      "type": "folder", "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            folder_SR = {"_id": node['_id'] + 'sr', "value": 'Switch & Router', "open": False, "level": 1, "size": 0,
                         "bgc": {"background-color": "transparent"},
                         "type": "folder", "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "data": [],
                         "path": [ind, 0]}
            folder_AG = {"_id": node['_id'] + 'ag', "value": 'Aggregation', "open": False, "level": 1, "size": 0,
                         "bgc": {"background-color": "transparent"},
                         "type": "folder", "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "data": [],
                         "path": [ind, 1]}
            folder_DF = {"_id": node['_id'] + 'df', "value": 'Dark Fiber', "open": False, "level": 1, "size": 0,
                         "bgc": {"background-color": "transparent"},
                         "type": "folder", "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "data": [],
                         "path": [ind, 2]}
            folder_FP = {"_id": node['_id'] + 'fp', "value": 'Flight Pack', "open": False, "level": 1, "size": 0,
                         "bgc": {"background-color": "transparent"},
                         "type": "folder", "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'), "data": [],
                         "path": [ind, 3]}
            folder_VD = {"_id": node['_id'] + 'vd', "value": 'Virtual Device', "open": False, "level": 1, "size": 0,
                         "bgc": {"background-color": "transparent"},
                         "type": "folder", "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                         "data": [], "path": [ind, 4]}
            folder['data'] = [folder_SR, folder_AG, folder_DF, folder_FP, folder_VD]

            if 'deviceList' in node.keys():
                for dev in node['deviceList']:
                    device = self.DeviceModel(dev).get()
                    if device['properties']['deviceType'] != 'PTN':
                        device = self.DeviceModel(dev).get()
                        folder_Device = {"id": device['_id'], "_id": device['_id'], "value": device['deviceName'],
                                         "size": 0, "level": 2,
                                         "type": "folder", "date": device['updateDate']}
                        data = []
                        path = []
                        if device['properties']['deviceType'] == 'ARISTA' or device['properties'][
                            'deviceType'] == 'MELLANOX':
                            path = [ind, 0, len(folder_SR['data'])]
                            folder_Device['path'] = [ind, 0, len(folder_SR['data'])]
                        elif device['properties']['deviceType'] == 'IPX':
                            folder_Device['path'] = [ind, 1, len(folder_AG['data'])]
                            path = [ind, 1, len(folder_AG['data'])]
                        elif device['properties']['deviceType'] == 'MUX' or device['properties'][
                            'deviceType'] == 'DEMUX':
                            folder_Device['path'] = [ind, 2, len(folder_DF['data'])]
                            path = [ind, 2, len(folder_DF['data'])]
                        elif device['properties']['deviceType'] == 'FP':
                            folder_Device['path'] = [ind, 3, len(folder_FP['data'])]
                            path = [ind, 3, len(folder_FP['data'])]
                        elif device['properties']['deviceType'] == 'VD':
                            folder_Device['path'] = [ind, 4, len(folder_VD['data'])]
                            path = [ind, 4, len(folder_VD['data'])]

                        if len(device['filenames']) > 0:
                            for i, file in enumerate(device['filenames']):
                                pathCopy = copy.deepcopy(path)
                                pathCopy.append(i)

                                if 'length' in file:
                                    file['length'] = (file['length']) / 1000
                                    if file['length'] < 1000:
                                        file['length'] = str(round(file['length'], 2)) + ' Kb'
                                    else:
                                        file['length'] = (file['length']) / 1000
                                        if file['length'] < 1000:
                                            file['length'] = str(round(file['length'], 2)) + ' Mb'
                                        else:
                                            file['length'] = (file['length']) / 1000
                                            if file['length'] < 1000:
                                                file['length'] = str(round(file['length'], 2)) + ' Gb'
                                            else:
                                                file['length'] = (file['length']) / 1000
                                                file['length'] = str(round(file['length'], 2)) + ' Tb'
                                else:
                                    file['length'] = 'Unkown'
                                data.append({"id": file['objectID'], "_id": file['objectID'], "value": file['filename'],
                                             "size": file['length'],
                                             "level": 3, "path": pathCopy,
                                             "type": file['content_type'],
                                             "date": file['upload_date']})
                        folder_Device['data'] = data

                        if device['properties']['deviceType'] == 'ARISTA' or device['properties'][
                            'deviceType'] == 'MELLANOX':
                            folder_SR['data'].append(folder_Device)
                        elif device['properties']['deviceType'] == 'IPX':
                            folder_AG['data'].append(folder_Device)
                        elif device['properties']['deviceType'] == 'MUX' or device['properties'][
                            'deviceType'] == 'DEMUX':
                            folder_DF['data'].append(folder_Device)
                        elif device['properties']['deviceType'] == 'FP':
                            folder_FP['data'].append(folder_Device)
                        elif device['properties']['deviceType'] == 'VD':
                            folder_VD['data'].append(folder_Device)

            results.append(folder)
        # results = sorted(results, key=lambda v: (v['value'].upper(), v['value'][0].islower())) # v['value']
        results = sorted(results, key=lambda v: v['value'].upper())  # v['value']
        return results
        # for devices in devicesList:
        #     if devices['properties']['deviceType'] != 'PTN':
        #         result = {"id": devices['_id'], "value": devices['deviceName'], "size": 0, "open": True,
        #                   "type": "folder", "date": dateConverter(devices['updateDate']), "webix_files": 1}
        #
        #         data = []
        #         if len(devices['filenames']) > 0:
        #             for file in devices['filenames']:
        #                 data.append({"id": file['objectID'], "value": file['filename'], "size": file['length'],
        #                              "type": file['content_type'], "date": dateConverter(file['upload_date'])})
        #         result['data'] = data
        #         results.append(result)
        # return json.dumps(
        #     [{"id": "FilesDrive", "value": 'Files Drive', "size": 0, "type": "folder", "open": True, "data": results}])
