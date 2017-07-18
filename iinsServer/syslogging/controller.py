from . import models
from .models import Logging
from flask import json, request
import flask_excel as excel
from datetime import datetime
from types import *
import copy


class LoggingService():
    def __init__(self):
        self.model = models

    def get(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            log = self.model.Logging().get(data['_id'], data['date'])
            log['_id'] = str(log['_id'])
            return json.dumps(log)

    def query_today(self):
        if request.method == 'POST':
            return self.model.Logging().query_today()

    def make_multicast_log(self):
        if request.method == 'POST':
            data = json.loads(request.data)

            multicastsBefore = {"multicasts": []}
            multicastsAfter = {"multicasts": []}

            for multicastIP in data['multicastChanges'].keys():
                # find the multicast that was changed. multicastIP is unique
                ind = -1
                count = 0
                for i in data['multicastrouting']:
                    if i['multicastIP'] == multicastIP:
                        ind = count
                    else:
                        count += 1

                multicastCopy = copy.deepcopy(data['multicastrouting'][ind])
                for portChange in data['multicastChanges'][multicastIP].keys():
                    multicastCopy['destination'][portChange]['routed'] = not multicastCopy['destination'][portChange][
                        'routed']
                multicastsBefore['multicasts'].append(multicastCopy)
                multicastsAfter['multicasts'].append(data['multicastrouting'][ind])

            self.model.Logging("Get the Username", "Edit Routing", "Edit Routing", 'Routing', multicastsAfter,
                               multicastsBefore, []).save()  #####CHANGE LATER
            return json.dumps({"message": "Successfully Logged"})

    def query_period(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            return self.model.Logging().query_period(data['start'], data['end'])

    # sets diff field of log to the changes between before and after.
    # log: Log object
    # Note: Lists/Array fields are ignored
    def getChanges(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            if data['log']['function'] == "Undo":
                return json.dumps([])
            before = data['log']['before']
            after = data['log']['after']
            diff = self.getChangesRecursion(before, after, [], before, after, data['log']['location'],
                                            data['log']['function'])
            self.model.Logging().set(data['log']['_id'], diff,
                                     data['log']['date_time'][0: data['log']['date_time'].index(' ')])

            return json.dumps(diff)

    # *Assumes if before and after have the same field name and 'path' ( ['properties']['deviceGeneralName'], for example), then they are of the same type*
    # currentPosition: list of fields used to reach this field( current field included)
    def getChangesRecursion(self, before, after, currentPosition, originalbefore, originalafter, location, logFunction):

        #         Future:use location of log to specify (ports of device, config of routes)
        # ----------------------------------HELPER FUNCTIONS----------------------------------
        # camelCase111 String to 'Camel Case 111'
        def camelToEnglish(x):
            inNumbers = False
            inCaps = True
            if x == "":
                return x
            elif x in NAME_MAPPING:
                return NAME_MAPPING[x]

            msg = x[0].upper()
            for letter in x[1:]:
                if (letter != " "):
                    if (inCaps == False and letter.isupper()):
                        inNumbers = False
                        inCaps = True
                        msg += ' '
                    elif (inNumbers == False and '0' <= letter and letter <= '9'):
                        msg += ' '
                        inNumber = True
                        inCaps = False

                    else:
                        inCaps = False
                        inNumber = False
                    msg += letter
            return msg

        # Converts {streetNo,street,city,province,country} to ex. 7 Willow Street Waterloo Ontario Canada
        def addressToString(address):
            return address['formatted_address']
            # return address['streetNo'] + " " + address['street'] + " " + address['city'] + " " + address[
            #     'province'] + " " + address['country']

        # ----------------------------------CONSTANTS----------------------------------
        NAME_MAPPING = {"rpatsNo": "RPATS Number"}
        DEVICE_BLACK_LIST = [['colocatedPtn'], ['filenames'], ['deviceType'], ['additionalInfo', 'typedCount'],
                             ['deviceType']]
        NODE_BLACK_LIST = [['ifShow'], ['_id']]
        PTN_BLACK_LIST = [['status'], ['currentCoordinates'], ['routeID'], ['properties', 'status'],
                          ['properties', 'configuration'], ['properties', 'additionalInfo'],
                          ['properties', 'deviceType'], ['properties', '_id'],
                          ['properties', 'properties'], ['installedDate']]
        TAG_BLACK_LIST = [['tagType'], ['tagFilter'], ['taggedNum'], ['keys'], ['tagCreateDate']]
        USER_BLACK_LIST = [['OriginName']]
        # Blacklist > Special...: If on blacklist, won't be compared even if in SpecialList
        BLACK_LIST = [['updateDate'], ['method'], ['username'], ['beforeDevices'], [
            'undoredo']] + PTN_BLACK_LIST + NODE_BLACK_LIST + DEVICE_BLACK_LIST + TAG_BLACK_LIST + USER_BLACK_LIST

        SPECIAL_ADDRESS = ['location']  # Dict for storing coordinates and address
        SPECIAL_PORTS = ['ports']  # List of device ports
        SPECIAL_AUTOTAG = ['deviceTypeList']  # List of autotags
        SPECIAL_PERMISSION = ['permission']  # Field for permission
        SPECIAL_ROUTE_CONFIG = ['config']  # List of port details in route. Only for deleting route
        SPECIAL_NODE_DEVICE = ['actualDeviceList']  # List of devices on node prior to deletion
        SPECIAL_ROUTING_APPLY = []  # List of routing multicasts
        # ----------------------------------Finally...The actual code----------------------------------

        diff = []

        if ((before is None and after is None) or (
            (currentPosition in BLACK_LIST) and (logFunction != 'Add User' and logFunction != 'Edit User'))):
            # Do nothing
            neverusethis = 1

        elif (location == 'Routing' and currentPosition == SPECIAL_ROUTING_APPLY):
            def removeChars(str):
                temp = ""
                for c in str:
                    if c >= "0" and c <= "9":
                        temp += c

                return temp

            UNROUTED = "unrouted"
            ROUTED = "routed"
            diff.append([{"cell": "Edited Multicasts", "format": "bold"}])
            for ind, m in enumerate(after['multicasts']):
                needHeader = True
                for port in m['destination'].keys():

                    if after['multicasts'][ind]['destination'][port]['routed'] != \
                            before['multicasts'][ind]['destination'][port]['routed']:
                        b = UNROUTED
                        a = ROUTED
                        if after['multicasts'][ind]['destination'][port]['routed'] == False:
                            b = ROUTED
                            a = UNROUTED

                        # if needHeader:
                        #     needHeader = False
                        #
                        #     diff.append([{"cell":'', "format": ""}])
                        #     diff.append([{"cell": m['multicastIP'] + ':', "format": ""}])
                        temp = ""
                        if len(after['multicasts'][ind]['source']) > 0:
                            temp = " P" + removeChars(after['multicasts'][ind]['source'].keys()[0])
                        diff.append([{"cell": m['multicastIP'] + temp + " ", "format": "bold"},
                                     {"cell": a + " to", "format": ""},
                                     {"cell": " P" + removeChars(after['multicasts'][ind]['destination'][port]['port']),
                                      "format": "bold"}])
                        diff.append([{"cell": "", "format": ""}])


        elif (currentPosition == SPECIAL_PERMISSION):
            def permissionCodeToText(c):
                if c == '0':
                    return 'Superuser (Read/Write)'
                elif c == '1':
                    return 'User (Read/Write)'
                elif c == '2':
                    return 'User (Read Only)'
                else:
                    return c

            if before is None:
                diff.append([{"cell": "Permission: " + permissionCodeToText(after), "format": ""}])
                diff.append([{"cell": "", "format": ""}])

            elif after is None:
                # diff.append([{"cell": "Permission Removed", "format": ""}])
                # diff.append([{"cell": "", "format": ""}])
                neverusethis = 1
            elif (before != after):
                diff.append([{"cell": "Permission Changed From: ", "format": ""}])
                diff.append([{"cell": permissionCodeToText(after), "format": ""}])
                diff.append([{"cell": "To", "format": ""}])
                diff.append([{"cell": permissionCodeToText(before), "format": ""}])
                diff.append([{"cell": "", "format": ""}])

        elif (currentPosition == SPECIAL_AUTOTAG):
            # Changes to autotags
            if (before is None):

                if (len(after) > 0):
                    diff.append([{"cell": "Autotags Added:", "format": ""}])
                    for t in after:
                        diff.append([{"cell": " - " + t, "format": ""}])
                    diff.append([{"cell": "", "format": ""}])
            elif (after is None):
                newR = True
                for b in before:
                    # if not (b in after):
                    if (newR):
                        newR = False
                        diff.append([{"cell": "Autotags Removed:", "format": ""}])
                    diff.append([{"cell": " - " + b, "format": ""}])
                if newR == False:
                    diff.append([{"cell": "", "format": ""}])

                    # newA = True
                    # for a in after:
                    #     if not (a in before):
                    #         if (newA):
                    #             newA = False
                    #             diff.append([{"cell": "Autotags Added:", "format": ""}])
                    #         diff.append([{"cell": " - " + a, "format": ""}])
                    # if newA == False:
                    #     diff.append([{"cell": "", "format": ""}])
            else:
                newR = True
                for b in before:
                    if not (b in after):
                        if (newR):
                            newR = False
                            diff.append([{"cell": "Autotags Removed:", "format": ""}])
                        diff.append([{"cell": " - " + b, "format": ""}])
                if newR == False:
                    diff.append([{"cell": "", "format": ""}])

                newA = True
                for a in after:
                    if not (a in before):
                        if (newA):
                            newA = False
                            diff.append([{"cell": "Autotags Added:", "format": ""}])
                        diff.append([{"cell": " - " + a, "format": ""}])
                if newA == False:
                    diff.append([{"cell": "", "format": ""}])

        elif (currentPosition == SPECIAL_ADDRESS):
            # Check for changes to address, evident from change of coordinates

            if before is None or 'address' not in before.keys() or (type(before['address']) is str) or \
                    (type(before['address']) is str) or before['address'] is None:

                if after is not None and 'address' in after.keys():
                    # diff.append([{"cell": camelToEnglish(currentPosition[-1]) + ": " + addressToString(
                    #     after['address']), "format": ""}])
                    diff.append([{"cell": camelToEnglish(currentPosition[-1]) + ": " +
                        after['address']['formatted_address'], "format": ""}])
                    diff.append([{"cell": "", "format": ""}])

            elif (after is None or 'address' not in after.keys() or after['address'] is None):
                neverusethis = 1
                # diff.append([{"cell": camelToEnglish(currentPosition[-1] + " Removed"), "format": ""}])
                # diff.append([{"cell": "", "format": ""}])
            else:
                # beforeAddress = addressToString(before['address'])
                # afterAddress = addressToString(after['address'])
                if (before['coordinates']['lng'] != after['coordinates']['lng'] or before['coordinates']['lat'] !=
                    after['coordinates']['lat']):
                    diff.append([{"cell": camelToEnglish(SPECIAL_ADDRESS[-1]) + " Changed From:", "format": ""}])
                    diff.append([{"cell": before['address']['formatted_address'], "format": ""}])
                    diff.append([{"cell": "To", "format": ""}])
                    diff.append([{"cell": after['address']['formatted_address'], "format": ""}])
                    diff.append([{"cell": "", "format": ""}])

        elif (currentPosition == SPECIAL_PORTS):
            # Check for changes to Ports

            if (before is not None and after is not None) and (
                            'deviceGeneralName' in originalbefore['properties'].keys() and 'deviceGeneralName' in
                        originalafter[
                            'properties'].keys()) \
                    and (originalbefore['properties']['deviceGeneralName'] == originalafter['properties'][
                        'deviceGeneralName']):
                numPorts = len(after)

                for i in range(0, numPorts):
                    newEntry = True
                    if ((after is None or after[i]['status'] == "Init") and (
                                    before is None or before[i]['status'] == "Init")):
                        # do nothing
                        neverusethis = 1
                    elif (after is None or after[i]['status'] == "Init"):

                        newEntry = False
                        diff.append([{
                            "cell": "Connection Removed: ",
                            "format": "bold"
                        }])
                        diff.append([{
                            "cell": self.model.Logging().DeviceModel(before[i]['route']['deviceID']).get_contain_deleted()[
                                'deviceName'],
                            "format": ""
                        }])
                        diff.append([{
                            "cell": "Port: " + str(i + 1),
                            "format": ""
                        }])
                        diff.append([{
                            "cell": "",
                            "format": ""
                        }])

                    elif (before is None or before[i]['status'] == "Init"):
                        # New Device
                        newEntry = False
                        diff.append([{"cell": after[i]['status'] + " Connection Created:", "format": "bold"}])
                        diff.append([{
                            "cell": "Connected From: " + originalafter['deviceName'],
                            "format": ""
                        }])
                        diff.append([{
                            "cell": "Port: " + str(i + 1),
                            "format": ""
                        }])

                        diff.append([{
                            "cell": "Speed: " + after[i]['portSpeed'],
                            "format": ""
                        }])

                        diff.append([{"cell": "Connected To: " +
                                              self.model.Logging().DeviceModel(after[i]['route']['deviceID']).get_contain_deleted()[
                                                  'deviceName'], "format": ""}])

                        if (originalafter['properties']['deviceType'] == 'IPX' and (
                                        after[i]['route']['destDeviceType'] == 'MUX' or after[i]['route'][
                                    'destDeviceType'] == 'DEMUX')):
                            diff.append([{
                                "cell": "Rx: " + after[i]['route']['connections'][0]['waveLength'],
                                "format": ""
                            }])
                            diff.append([{
                                "cell": "Tx: " + after[i]['route']['connections'][1]['waveLength'],
                                "format": ""
                            }])

                        else:
                            diff.append([{
                                "cell": "Port: " + str(after[i]['route']['connections'][0]['portID']),
                                "format": ""
                            }])
                            diff.append([{
                                "cell": "Speed: " + after[i]['route']['connections'][0]['portSpeed'],
                                "format": ""
                            }])
                        needSplit = True
                        if ('projectID' in after[i]['properties'].keys() and after[i]['properties']['projectID'] != ""):
                            diff.append([{
                                "cell": "",
                                "format": ""
                            }])
                            needSplit = False
                            diff.append([{
                                "cell": "RPATS: " + after[i]['properties']['projectID'],
                                "format": ""
                            }])

                        if ('portDescription' in after[i]['properties'].keys() and after[i]['properties'][
                            'portDescription'] != ""):
                            if needSplit:
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])
                                needSplit = False
                            diff.append([{
                                "cell": "Description: " + after[i]['properties']['portDescription'],
                                "format": ""
                            }])

                        if ('portLimit' in after[i].keys() and after[i][
                            'portLimit'] != ""):
                            if needSplit:
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])
                                needSplit = False
                            diff.append([{
                                "cell": "Port Limit: " + after[i]['portLimit'],
                                "format": ""
                            }])
                        if ('opexCost' in after[i].keys() and after[i][
                            'opexCost'] != ""):
                            if needSplit:
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])
                                needSplit = False
                            diff.append([{
                                "cell": "Port Cost: " + str(after[i]['opexCost']),
                                "format": ""
                            }])

                        if (len(after[i]['properties']['tags']) > 0):
                            if needSplit:
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])
                                needSplit = False
                            diff.append([{"cell": "Tags:", "format": ""}])

                            for t in after[i]['properties']['tags']:
                                diff.append([{"cell": " - " + t, "format": ""}])

                        if (newEntry == False):
                            diff.append([{"cell": "", "format": ""}])


                    else:
                        # change the route

                        if (after[i]['route']['deviceID'] != before[i]['route']['deviceID']):
                            newEntry = False
                            diff.append([{
                                "cell": "Connection Removed: ",
                                "format": "bold"
                            }])
                            diff.append([{
                                "cell": self.model.Logging().DeviceModel(before[i]['route']['deviceID']).get_contain_deleted()[
                                    'deviceName'],
                                "format": ""
                            }])
                            diff.append([{
                                "cell": "Port: " + str(i + 1),
                                "format": ""
                            }])
                            diff.append([{
                                "cell": "",
                                "format": ""
                            }])
                            diff.append([{
                                "cell": after[i]['status'] + " Connection Created:",
                                "format": "bold"
                            }])
                            diff.append([{
                                "cell": "Connected From: " + originalafter['deviceName'],
                                "format": ""
                            }])

                            diff.append([{
                                "cell": "Port: " + str(i + 1),
                                "format": ""
                            }])

                            diff.append([{
                                "cell": "Speed: " + after[i]['portSpeed'],
                                "format": ""
                            }])

                            diff.append([{
                                "cell": "Connected To: " +
                                        self.model.Logging().DeviceModel(after[i]['route']['deviceID']).get_contain_deleted()[
                                            'deviceName'],
                                "format": ""
                            }])

                            if (originalafter['properties']['deviceType'] == 'IPX' and (
                                            after[i]['route']['destDeviceType'] == 'MUX' or after[i]['route'][
                                        'destDeviceType'] == 'DEMUX')):

                                diff.append([{
                                    "cell": "Rx: " + after[i]['route']['connections'][0]['waveLength'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "Tx: " + after[i]['route']['connections'][1]['waveLength'],
                                    "format": ""
                                }])


                            else:
                                diff.append([{
                                    "cell": "Port: " + str(after[i]['route']['connections'][0]['portID']),
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "Speed: " + str(after[i]['route']['connections'][0]['portSpeed']),
                                    "format": ""
                                }])

                            newlined = False
                            if ('projectID' in after[i]['properties'].keys() and after[i]['properties'][
                                'projectID'] != ""):
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])
                                newlined = True
                                diff.append([{
                                    "cell": "RPATS: " + after[i]['properties']['projectID'],
                                    "format": ""
                                }])

                            if ('portDescription' in after[i]['properties'].keys() and after[i]['properties'][
                                'portDescription'] != ""):

                                if (newlined == False):
                                    diff.append([{"cell": "", "format": ""}])
                                    newlined = True

                                diff.append([{
                                    "cell": "Description: " + after[i]['properties']['portDescription'],
                                    "format": ""
                                }])

                            if ('portLimit' in after[i].keys() and after[i][
                                'portLimit'] != ""):
                                if needSplit:
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])
                                    needSplit = False
                                diff.append([{
                                    "cell": "Port Limit: " + after[i]['portLimit'],
                                    "format": ""
                                }])

                            if ('opexCost' in after[i].keys() and after[i][
                                'opexCost'] != ""):
                                if needSplit:
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])
                                    needSplit = False
                                diff.append([{
                                    "cell": "Port Cost: " + after[i]['opexCost'],
                                    "format": ""
                                }])

                            if (len(after[i]['properties']['tags']) > 0):
                                if (newlined == False):
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])
                                    newlined = True

                                diff.append([{"cell": "Tags:", "format": ""}])

                                for t in after[i]['properties']['tags']:

                                    diff.append([{"cell": " - " + t.tagName, "format": ""}])

                                    if (newEntry == False):
                                        diff.append([{"cell": "", "format": ""}])


                        else:
                            if (('portDescription' not in before[i]['properties'].keys() or before[i]['properties'][
                                'portDescription'] == "") and
                                    ('portDescription' not in after[i]['properties'].keys() or after[i]['properties'][
                                        'portDescription'] == "")):
                                # No change
                                neverusethis = 1

                            elif ('portDescription' not in before[i]['properties'].keys() or before[i]['properties'][
                                'portDescription'] == ""):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Edited Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Description: " + after[i]['properties']['portDescription'],
                                    "format": ""
                                }])

                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            elif ('portDescription' not in after[i]['properties'] or after[i]['properties'][
                                'portDescription'] == ""):

                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Edited Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Description Removed",
                                    "format": ""
                                }])

                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            else:

                                if (after[i]['properties']['portDescription'] != before[i]['properties'][
                                    'portDescription']):

                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "Description Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": before[i]['properties']['portDescription'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": after[i]['properties']['portDescription'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])

                            if (('projectID' not in before[i]['properties'] or before[i]['properties'][
                                'projectID'] == "") and
                                    ('projectID' not in after[i]['properties'] or after[i]['properties'][
                                        'projectID'] == "")):
                                # No Change
                                neverusethis = 1


                            elif ('projectID' not in before[i]['properties'] or before[i]['properties'][
                                'projectID'] == ""):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Edited Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "RPATS ID: " + after[i]['properties']['projectID'],
                                    "format": ""
                                }])

                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            elif ('projectID' not in after[i]['properties'] or after[i]['properties'][
                                'projectID'] == ""):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "RPATS ID Removed",
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": before[i]['properties']['projectID'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            else:

                                if (after[i]['properties']['projectID'] != before[i]['properties']['projectID']):

                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "RPATS ID Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": before[i]['properties']['projectID'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": after[i]['properties']['projectID'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])

                            if (('portLimit' not in before[i] or before[i]['portLimit'] == "") and
                                    ('portLimit' not in after[i] or after[i]['portLimit'] == "")):
                                # No Change
                                neverusethis = 1

                            elif ('portLimit' not in before[i] or before[i]['portLimit'] == ""):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Edited Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Port Limit: " + after[i]['portLimit'],
                                    "format": ""
                                }])

                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            elif ('portLimit' not in after[i] or after[i]['portLimit'] == ""):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Port Limit Removed",
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": before[i]['portLimit'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            else:

                                if (after[i]['portLimit'] != before[i]['portLimit']):

                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "Port Limit Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": before[i]['portLimit'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": after[i]['portLimit'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])

                            if (('opexCost' not in before[i] or before[i]['opexCost'] == "") and
                                    ('opexCost' not in after[i] or after[i]['opexCost'] == "")):
                                # No Change
                                neverusethis = 1

                            elif ('opexCost' not in before[i] or before[i]['opexCost'] == ""):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Edited Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Port Cost: " + after[i]['opexCost'],
                                    "format": ""
                                }])

                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            elif ('opexCost' not in after[i] or after[i]['opexCost'] == ""):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Port Cost Removed",
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": before[i]['opexCost'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            else:

                                if (after[i]['opexCost'] != before[i]['opexCost']):

                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "Port Cost Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": before[i]['opexCost'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": after[i]['opexCost'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])

                            if (after[i]['status'] != before[i]['status']):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Edited Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Status Changed From:",
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": before[i]['status'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "To",
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": after[i]['status'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            if (after[i]['portSpeed'] != before[i]['portSpeed']):
                                if (newEntry):
                                    newEntry = False
                                    diff.append([{
                                        "cell": "Edited Port " + str(i + 1) + ":",
                                        "format": "bold"
                                    }])

                                diff.append([{
                                    "cell": "Port Speed Changed From:",
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": before[i]['portSpeed'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "To",
                                    "format": ""
                                }])

                                diff.append([{
                                    "cell": after[i]['portSpeed'],
                                    "format": ""
                                }])
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

                            if (originalafter['properties']['deviceType'] == "IPX" and (
                                            after[i]['route']['destDeviceType'] == "MUX" or after[i]['route'][
                                        'destDeviceType'] == "DEMUX")):

                                if (after[i]['route']['connections'][0]['waveLength'] !=
                                        before[i]['route']['connections'][0]['waveLength']):
                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "Rx Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": before[i]['route']['connections'][0]['waveLength'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": after[i]['route']['connections'][0]['waveLength'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])

                                if (after[i]['route']['connections'][1]['waveLength'] !=
                                        before[i]['route']['connections'][1]['waveLength']):
                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "Tx Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": before[i]['route']['connections'][1]['waveLength'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": after[i]['route']['connections'][1]['waveLength'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])
                            else:
                                if (after[i]['route']['connections'][0]['portID'] !=
                                        before[i]['route']['connections'][0]['portID']):

                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "Connected Port Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": str(before[i]['route']['connections'][0]['portID']),
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": str(after[i]['route']['connections'][0]['portID']),
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])

                                if (after[i]['route']['connections'][0]['portSpeed'] !=
                                        before[i]['route']['connections'][0]['portSpeed']):
                                    if (newEntry):
                                        newEntry = False
                                        diff.append([{
                                            "cell": "Edited Port " + str(i + 1) + ":",
                                            "format": "bold"
                                        }])

                                    diff.append([{
                                        "cell": "Connected Port Speed Changed From:",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": before[i]['route']['connections'][0]['portSpeed'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "To",
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": after[i]['route']['connections'][0]['portSpeed'],
                                        "format": ""
                                    }])
                                    diff.append([{
                                        "cell": "",
                                        "format": ""
                                    }])

                            if ('tags' in before[i]['properties'] and 'tags' in after[i]['properties']):
                                if (len(before[i]['properties']['tags']) > 0 or len(
                                        after[i]['properties']['tags']) > 0):

                                    rtags = False
                                    for t in before[i]['properties']['tags']:

                                        found = False
                                        for a in after[i]['properties']['tags']:
                                            if (a == t):
                                                found = True

                                        if (found == False):
                                            rtags = True

                                    if (rtags):
                                        if (newEntry):
                                            newEntry = False
                                            diff.append([{
                                                "cell": "Edited Port " + str(i + 1) + ":",
                                                "format": "bold"
                                            }])

                                        diff.append([{
                                            "cell": "Tags Removed:",
                                            "format": ""
                                        }])
                                        for t in before[i]['properties']['tags']:

                                            found = False
                                            for a in after[i]['properties']['tags']:

                                                if (a == t):
                                                    found = True

                                            if (found == False):
                                                diff.append([{
                                                    "cell": " - " + t,
                                                    "format": ""
                                                }])

                                    atags = False
                                    for t in after[i]['properties']['tags']:

                                        found = False
                                        for a in before[i]['properties']['tags']:

                                            if (a == t):
                                                found = True

                                        if (found == False):
                                            atags = True

                                    if (atags):
                                        diff.append([{
                                            "cell": "Tags Added: ",
                                            "format": ""
                                        }])
                                        for t in after[i]['properties']['tags']:

                                            found = False
                                            for a in before[i]['properties']['tags']:

                                                if (a == t):
                                                    found = True

                                            if (found == False):
                                                diff.append([{
                                                    "cell": " - " + t,
                                                    "format": ""
                                                }])

                            if (newEntry == False):
                                diff.append([{
                                    "cell": "",
                                    "format": ""
                                }])

        elif (before is None):
            # New field added

            if (type(after) is dict):
                for key in after.keys():
                    toadd = self.getChangesRecursion(None, after[key], currentPosition + [key], originalbefore,
                                                     originalafter, location, logFunction)
                    if (len(toadd) > 0):
                        diff += toadd
            # elif (type(after) is ListType):
            #     for element in after:
            #         toadd = self.getChangesRecursion(None, after[element], currentPosition,originalbefore,originalafter)
            #         if (len(toadd) > 0):
            #             diff += toadd
            else:
                # "Basic" values: 1, "hello", not lists/dicts
                if currentPosition != []:
                    diff.append([{"cell": camelToEnglish(currentPosition[-1]) + ": " + str(after), "format": ""}])
                    diff.append([{"cell": "", "format": ""}])

        elif (after is None):

            if (currentPosition == SPECIAL_NODE_DEVICE):
                if len(before) > 0:
                    if len(before) == 1:
                        diff.append([{"cell": "Deleted Device:", "format": "bold"}])
                    else:
                        diff.append([{"cell": "Deleted Devices:", "format": "bold"}])

                    for dev in before:
                        diff.append([{"cell": " - " + dev['deviceName'], "format": ""}])
            elif (currentPosition == SPECIAL_ROUTE_CONFIG):
                if type(
                        before) is dict and 'additionalInformation' not in before.keys() and 'features' not in before.keys():
                    for routeKey in before.keys():
                        diff.append([{"cell": "Removed Route Between:", "format": "bold"}])
                        if ((before[routeKey][0]['destDeviceType'] != "MUX") and
                                (before[routeKey][0]['destDeviceType'] != "DEMUX")):
                            diff.append(
                                [{"cell": " - " +
                                          self.model.Logging().DeviceModel(before[routeKey][0]['deviceID']).get_contain_deleted()[
                                              'deviceName'] + " Port " + str(
                                    before[routeKey][0]['connections'][0]['portID']),
                                  "format": ""}])
                        else:
                            if (before[routeKey][0]['connections'][0]['waveLength'] == 'Common'):
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][0]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Rx " + str(
                                        before[routeKey][0]['connections'][0]['waveLength']),
                                      "format": ""}])

                            elif (before[routeKey][0]['connections'][1]['waveLength'] == 'Common'):
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][0]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Tx " + str(
                                        before[routeKey][0]['connections'][1]['waveLength']),
                                      "format": ""}])

                            else:
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][0]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Rx " + str(
                                        before[routeKey][0]['connections'][0]['waveLength']),
                                      "format": ""}])
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][0]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Tx " + str(
                                        before[routeKey][0]['connections'][1]['waveLength']),
                                      "format": ""}])

                        if ((before[routeKey][1]['destDeviceType'] != "MUX") and
                                (before[routeKey][1]['destDeviceType'] != "DEMUX")):
                            diff.append(
                                [{"cell": " - " +
                                          self.model.Logging().DeviceModel(before[routeKey][1]['deviceID']).get_contain_deleted()[
                                              'deviceName'] + " Port " + str(
                                    before[routeKey][1]['connections'][0]['portID']),
                                  "format": ""}])
                        else:
                            if (before[routeKey][1]['connections'][0]['waveLength'] == 'Common'):
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][1]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Rx " + str(
                                        before[routeKey][1]['connections'][0]['waveLength']),
                                      "format": ""}])
                            elif (before[routeKey][1]['connections'][1]['waveLength'] == 'Common'):
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][1]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Tx " + str(
                                        before[routeKey][1]['connections'][1]['waveLength']),
                                      "format": ""}])

                            else:
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][1]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Rx " + str(
                                        before[routeKey][1]['connections'][0]['waveLength']),
                                      "format": ""}])
                                diff.append(
                                    [{"cell": " - " +
                                              self.model.Logging().DeviceModel(before[routeKey][1]['deviceID']).get_contain_deleted()[
                                                  'deviceName'] + " Tx " + str(
                                        before[routeKey][1]['connections'][1]['waveLength']),
                                      "format": ""}])

                        # diff.append(
                        #     [{"cell": " - " + self.model.Logging().DeviceModel(before[routeKey][0]['deviceID']).get_contain_deleted()[
                        #         'deviceName'] + " Port " + str(before[routeKey][0]['portID']), "format": ""}])
                        # diff.append(
                        #     [{"cell": " - " + self.model.Logging().DeviceModel(before[routeKey][1]['deviceID']).get_contain_deleted()[
                        #         'deviceName'] + " Port " + str(before[routeKey][1]['portID']), "format": ""}])
                        diff.append([{"cell": "", "format": ""}])
            elif (type(before) is dict):
                for beforekey in before.keys():
                    toadd = self.getChangesRecursion(before[beforekey], None, currentPosition + [beforekey],
                                                     originalbefore, originalafter, location, logFunction)

                    diff += toadd

        else:
            # Process Dictionary
            if (type(after) is dict):
                for key in after.keys():
                    if (key in before.keys()):
                        toadd = self.getChangesRecursion(before[key], after[key], currentPosition + [key],
                                                         originalbefore, originalafter, location, logFunction)
                        if (len(toadd) > 0):
                            diff += toadd
                    else:
                        # New key added
                        toadd = self.getChangesRecursion(None, after[key], currentPosition + [key], originalbefore,
                                                         originalafter, location, logFunction)
                        if (len(toadd) > 0):
                            diff += toadd
            elif (type(after) is list):
                # Do Nothing
                neverusethis = 1
            else:
                # Process leaves: String,Int,Boolean...
                if (before != after):
                    if (type(before) is str and type(after) is str):
                        if (before.strip() == ""):
                            diff.append([{"cell": camelToEnglish(currentPosition[-1]) + ": " + after, "format": ""}])
                        elif (after.strip() == ""):
                            diff.append([{"cell": camelToEnglish(currentPosition[-1]) + " Removed", "format": ""}])
                        else:
                            diff.append(
                                [{"cell": camelToEnglish(currentPosition[-1]) + " Changed From:", "format": ""}])
                            diff.append([{"cell": before, "format": ""}])
                            diff.append([{"cell": "To", "format": ""}])
                            diff.append([{"cell": after, "format": ""}])
                    elif (type(before) is str and type(after) is str):
                        if (before == ''):
                            diff.append([{"cell": camelToEnglish(currentPosition[-1]) + ": " + after, "format": ""}])
                        elif (after == ''):
                            diff.append([{"cell": camelToEnglish(currentPosition[-1]) + " Removed", "format": ""}])
                        else:
                            diff.append(
                                [{"cell": camelToEnglish(currentPosition[-1]) + " Changed From:", "format": ""}])
                            diff.append([{"cell": str(before), "format": ""}])
                            diff.append([{"cell": "To", "format": ""}])
                            diff.append([{"cell": str(after), "format": ""}])
                    else:
                        diff.append([{"cell": camelToEnglish(currentPosition[-1]) + " Changed From:", "format": ""}])
                        diff.append([{"cell": str(before), "format": ""}])
                        diff.append([{"cell": "To", "format": ""}])
                        diff.append([{"cell": str(after), "format": ""}])
                    diff.append([{"cell": "", "format": ""}])

        return diff

    def getChangesSelf(self, log):
        before = log['before']
        after = log['after']
        diff = self.getChangesRecursion(before, after, [], before, after, log['location'], log['function'])
        self.model.Logging().set(log['_id'], diff, log['date_time'][0: log['date_time'].index(' ')])
        return diff

    def export_logs(self):
        sortField = request.args['sortField']
        sortReverse = (request.args['reverse'] == 'true')
        startDate = request.args['startDate']
        endDate = request.args['endDate']
        filename = datetime.now().strftime('%Y-%m-%d') + "-MVRT-LOGS"

        logs = self.model.Logging().query_period(startDate, endDate, True)

        if sortField != 'none':
            logs = sorted(logs, key=lambda d: d[sortField].upper(), reverse=sortReverse)

        spreadsheet = [
            ["Entry Time", "User", "Description", "Additional Information"]]

        for l in logs:

            temp = [l['date_time'], l['user'], l['content']]

            # if ('additionalinfo' not in l.keys() or len(l['additionalinfo']) == 0):
            l['additionalinfo'] = self.getChangesSelf(l)
            self.model.Logging().set(l['_id'], l['additionalinfo'], l['date_time'][0: l['date_time'].index(' ')])
            t = ""
            for a in l['additionalinfo']:

                if (a[0]['cell'] == ""):
                    temp.append(t)
                    t = ""
                else:
                    for part in a:
                        if part != "":
                            if t != "":
                                t = t + " " + str(part['cell'])
                            else:
                                t = t + str(part['cell'])

            if (t != ""):
                temp.append(t)
            spreadsheet.append(temp)

        return excel.make_response_from_array(spreadsheet, "csv", file_name=filename)
