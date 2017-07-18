from . import models
# from NetvisServer.devices.models import DeviceModel
# from NetvisServer.devices.models import PortModel
# from NetvisServer.routes.models import RouteModel
# from NetvisServer.nodes.models import NodeModel
# from NetvisServer.files.models import FileModel
from NetvisServer.searching import models as SeachingModel
from pymongo import MongoClient
from bson import ObjectId

class InitDatabase():
    def __init__(self):
        self.model =models
        self.model.InitDatabaeModel().initDB()
        self.check_data()

    def check_data(self):
        devices =[]
        ports =[]
        nodes =[]
        routes =[]

        devices = self.get_devices()
        ports = self.get_ports()
        nodes = self.get_nodes()
        routes = self.get_routes()

        updateDevice = False
        for device in devices:
            if "authorization" not in device:
                print('Add authorization on device')
                self.model.InitDatabaeModel(device['_id']).fast_set_devices(authorization={"users": [], "groups": [], "companies": []})

            if 'typeClass' not in device['properties']:
                print('Add type class on device type')
                if device['properties']['deviceType'] == "ARISTA" or device['properties']['deviceType'] == "MELLANOX":
                    device['properties']['typeClass'] = "Switches & Routers"
                elif device['properties']['deviceType'] == "IPX":
                    device['properties']['typeClass'] = "Aggregators"
                elif device['properties']['deviceType'] == "MUX" or device['properties']['deviceType'] == "DEMUX":
                    device['properties']['typeClass'] = "Dark Fiber"
                elif device['properties']['deviceType'] == "FP":
                    device['properties']['typeClass'] = "Flight Packs"
                elif device['properties']['deviceType'] == "VD":
                    device['properties']['typeClass'] = "Virtual Devices"
                elif device['properties']['deviceType'] == "PTN":
                    device['properties']['typeClass'] = "PTN"
                self.model.InitDatabaeModel(device['_id']).fast_set_devices(properties=device['properties'])

            if 'filenames' in device:
                for file in device['filenames']:
                    req = MongoClient('localhost', 27017).db_file.fs.files.find_one({"_id": ObjectId(file['objectID'])})
                    if req is not None:
                        req['_id'] = str(req['_id'])
                        f = req
                        if '_id' not in f:
                            updateDevice = True
                            device['filenames'].remove(file)
                            print('Delete unused file')
                if updateDevice:
                    updateDevice = False
                    self.model.InitDatabaeModel(device['_id']).fast_set_devices(filenames=device['filenames'])
            if 'ports' in device['properties']:
                del device['properties']['ports']
                print('Delete ports in device properties')
                self.model.InitDatabaeModel(device['_id']).fast_set_devices(properties=device['properties'])

        for port in ports:
            if "authorization" not in port:
                print('Add authorization on port')
                self.model.InitDatabaeModel(port['_id']).fast_set_ports(authorization={"users": [], "groups": [], "companies": []})
            if 'notificationDate' not in port['properties']:
                print('Add notification date on port')
                port['properties']['notificationDate'] = 'None'
                self.model.InitDatabaeModel(port['_id']).fast_set_ports(properties=port['properties'])
            if 'expiryDate' not in port['properties']:
                print('Add expiry date on port')
                port['properties']['expiryDate'] = 'None'
                self.model.InitDatabaeModel(port['_id']).fast_set_ports(properties=port['properties'])

            if 'notificationDate' not in port:
                print('Add notification date on port')
                self.model.InitDatabaeModel(port['_id']).fast_set_ports(notificationDate='None')
            if 'expiryDate' not in port:
                print('Add expiry date on port')
                self.model.InitDatabaeModel(port['_id']).fast_set_ports(expiryDate='None')
            if 'routePresentation' not in port['route'] and port['status']!='Init':
                print('Add route presentation on port')
                port['route']['routePresentation'] = 'Visible'
                self.model.InitDatabaeModel(port['_id']).fast_set_ports(route=port['route'])
            if 'circuitID' not in port:
                print('Add circuit ID on port')
                self.model.InitDatabaeModel(port['_id']).fast_set_ports(circuitID='')


        for route in routes:
            if 'authorization' not in route:
                print('Add authorization on route')
                self.model.InitDatabaeModel(route['_id']).fast_set_routes(authorization={"users": [], "groups": [], "companies": []})
            if 'portStatus' in route:
                if (route['portStatus']['pending'] == 0):
                    status = 'Active'
                else:
                    status = 'Pending'
                self.model.InitDatabaeModel(route['_id']).fast_set_routes(status=status, authorization={"users": [], "groups": [], "companies": []})
            if 'config' in route:
                portIDListForRresentation = []
                for key in route['config'].keys():
                    for config in route['config'][key]:
                        if 'expiryDate' not in config:
                            print('Add expiry date on route')
                            config['expiryDate'] = 'None'
                            self.model.InitDatabaeModel(route['_id']).fast_set_routes(config=route['config'])
                        if 'notificationDate' not in config:
                            print('Add expiry date on route')
                            config['notificationDate'] = 'None'
                            self.model.InitDatabaeModel(route['_id']).fast_set_routes(config=route['config'])
                        if 'routePresentation' not in config:
                            config['routePresentation'] = 'Visible'
                            self.model.InitDatabaeModel(route['_id']).fast_set_routes(config=route['config'])
                            if 'routePresentation' not in route:
                                route['routePresentation'] = {'visible': 1, 'trigger': 0, 'hidden': 0}
                            else:
                                route['routePresentation']['visible'] += 1
                            self.model.InitDatabaeModel(route['_id']).fast_set_routes(routePresentation=route['routePresentation'])

        # RouteModel(route['_id']).et_route_status_summary()

        for node in nodes:
            if 'authorization' not in node:
                print('Add authorization on node')
                self.model.InitDatabaeModel(node['_id']).fast_set_nodes(authorization={"users": [], "groups": [], "companies": []})


    def get_devices(self):
        result = []
        condition = {"status": {"$nin": ["Deleted"]}, "properties.deviceType": {'$in': ['IPX','FP','MUX','VD','DEMUX','ARISTA','MELLANOX']}}
        req = MongoClient('localhost', 27017).db_mnm.devices.find(condition)
        for r in req:
            r['_id'] = str(r['_id'])
            result.append(r)
        return  result

    def get_ports(self):
        results = []
        req = MongoClient('localhost', 27017).db_mnm.ports.find({"status": {"$nin": ["Deleted"]}})
        for r in req:
            r['_id'] = str(r['_id'])
            results.append(r)
        return results

    def get_nodes(self):
        result = []
        req = MongoClient('localhost', 27017).db_mnm.nodes.find({'ifShow': True})
        for r in req:
            r['_id'] = str(r['_id'])
            result.append(r)
        return result

    def get_routes(self):
        result = []
        condition = {"status": {"$nin": ["Deleted"]}}
        req = MongoClient('localhost', 27017).db_mnm.routes.find(condition)
        for r in req:
            r['_id'] = str(r['_id'])
            result.append(r)
        return result
