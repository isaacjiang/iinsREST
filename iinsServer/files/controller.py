import importlib
from math import radians, cos, sin, asin, sqrt
from datetime import datetime
from . import models
import gridfs
from bson.objectid import ObjectId
from flask import make_response, request, json
# import xmltodict
from pymongo import MongoClient
from math import radians, cos, sin, asin, sqrt
from pprint import pprint

class FileService():
    def __init__(self):
        self.model = models
        self.collection = MongoClient('localhost', 27017).db_file
        self.db_policy = MongoClient('localhost', 27017).db_policy
    def get_all(self):
        if request.method == 'POST':
            data = json.loads(request.data)
            results = []
            if data['key'] == 'all':
                results = self.model.FileModel().get_all_files()
            elif data['key'] == 'device':
                results = self.model.FileModel().get_files_from_device(data['deviceID'])
            return json.dumps(results)

    def createFolder(self):
        if request.form['action'] == 'createfolder':
            deviceID = request.form['target']
        if request.form['target'] != 'FilesDrive':

            file = {"objectID": request.form['ObjectID'],
                    "content_type": "folder",
                    "filename": request.form['fileName'],
                    "length": 0,
                    "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            # self.DeviceModel(deviceID).update_filenames(file)
            return json.dumps(file)

    def filesService(self):
        gfs = gridfs.GridFS(self.collection)
        if request.form['action'] == "files":
            devices = self.DeviceModel(request.form['source']).get()
            data = []
            if len(devices['filenames']) > 0:
                for file in devices['filenames']:
                    data.append({"id": file['objectID'], "value": file['filename'], "size": file['length'],
                                 "type": file['content_type'], "date": self.utils.dateConverter(file['upload_date'])})
            return json.dumps({"parent": request.form['source'], "data": data})

        if request.form['action'] == "download":
            objectID = request.form['source']
            gfs = gridfs.GridFS(self.collection)
            file = gfs.get(ObjectId(objectID)).read()
            response = make_response(file)
            response.headers['Content-Type'] = gfs.get(ObjectId(objectID)).content_type
            response.headers['filename'] = gfs.get(ObjectId(objectID)).filename
            response.headers["Content-Disposition"] = "attachment; filename= " + response.headers['filename'] + " "
            return response

        if request.form['action'] == "move":
            fileObjectIDs = request.form['source'].split(",")
            sourceParentID = request.form['sourceParentID']
            target = request.form['target']
            response = []
            for fileObjectID in fileObjectIDs:
                gridfsOut = gfs.get(ObjectId(fileObjectID))
                file = {"objectID": str(fileObjectID),
                        "content_type": gridfsOut.content_type,
                        "filename": gridfsOut.filename,
                        "length": gridfsOut.length,
                        "upload_date": gridfsOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                        }
                # self.DeviceModel(sourceParentID).update_filenames(file, delete=True)
                # self.DeviceModel(target).update_filenames(file)
                response.append({"id": str(fileObjectID), "value": gridfsOut.filename})
            return json.dumps(response)

        if request.form['action'] == "copy":
            fileObjectIDs = request.form['source'].split(",")
            sourceParentID = request.form['sourceParentID']
            target = request.form['target']
            response = []
            for fileObjectID in fileObjectIDs:
                gridfsOut = gfs.get(ObjectId(fileObjectID))
                file = {"objectID": str(fileObjectID),
                        "content_type": gridfsOut.content_type,
                        "filename": gridfsOut.filename,
                        "length": gridfsOut.length,
                        "upload_date": gridfsOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                        }

                newOjectID = gfs.put(gridfsOut.read(),
                                     content_type=gridfsOut.content_type,
                                     filename=gridfsOut.filename)

                newgridfsOut = gfs.get(ObjectId(newOjectID))
                newfile = {"objectID": str(newOjectID),
                           "content_type": newgridfsOut.content_type,
                           "filename": newgridfsOut.filename,
                           "length": newgridfsOut.length,
                           "upload_date": newgridfsOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                           }

                # self.DeviceModel(target).update_filenames(newfile)
                response.append({"id": str(newOjectID), "value": newgridfsOut.filename})
            return json.dumps(response)

        if request.form['action'] == "remove":
            fileObjectIDs = request.form['source'].split(",")
            sourceParentID = request.form['sourceParentID']
            response = []
            for fileObjectID in fileObjectIDs:
                gridfsOut = gfs.get(ObjectId(fileObjectID))
                file = {"objectID": str(fileObjectID),
                        "content_type": gridfsOut.content_type,
                        "filename": gridfsOut.filename,
                        "length": gridfsOut.length,
                        "upload_date": gridfsOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                        }
                # self.DeviceModel(sourceParentID).update_filenames(file, delete=True)
                response.append({"id": str(fileObjectID), "value": gridfsOut.filename})
            return json.dumps(response)

        if request.form['action'] == "rename":
            fileObjectID = request.form['source']
            sourceParentID = request.form['sourceParentID']
            newfilename = request.form['target']
            oldFileOut = gfs.get(ObjectId(fileObjectID))
            oldFile = {"objectID": str(fileObjectID),
                       "content_type": oldFileOut.content_type,
                       "filename": oldFileOut.filename,
                       "length": oldFileOut.length,
                       "upload_date": oldFileOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                       }
            newOjectID = gfs.put(oldFileOut.read(),
                                 content_type=oldFileOut.content_type,
                                 filename=newfilename)
            gfs.delete(ObjectId(fileObjectID))
            gridfsOut = gfs.get(ObjectId(newOjectID))
            file = {"objectID": str(newOjectID),
                    "content_type": gridfsOut.content_type,
                    "filename": gridfsOut.filename,
                    "length": gridfsOut.length,
                    "upload_date": gridfsOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                    }
            self.DeviceModel(sourceParentID).update_filenames(oldFile, delete=True)
            self.DeviceModel(sourceParentID).update_filenames(file)
            return json.dumps({"id": str(newOjectID), "value": gridfsOut.filename})

    def upload_file(self):
        if request.method == "POST":
            output = []
            gfs = gridfs.GridFS(self.collection)
            if len(request.files) > 0:
                for i in range(0, len(request.files)):
                    text =  self.get_pdf_text(request.files['file'])
                    dict=self.convert_text(text)

                    objectID = gfs.put(request.files['file'].read(),
                                       content_type=request.files['file'].content_type,
                                       filename=request.files['file'].filename)
                    gridfsOut = gfs.get(objectID)  # .length,gfs.get(objectID).upload_date
                    output.append({"objectID": str(objectID),
                                   "content_type": gridfsOut.content_type,
                                   "filename": gridfsOut.filename,
                                   "length": gridfsOut.length,
                                   "upload_date": gridfsOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
                                   })
                    print(output)
                    dict['PolicyDocument'] = output
                    self.save(dict)
            return json.dumps(output)

    def save(self,dict):
        # dict=json.loads(dict)
        if 'PolicyDetails' in dict.keys() and 'PolicyNumber' in dict['PolicyDetails'].keys():
            self.db_policy.policy.update_one({'PolicyDetails.PolicyNumber':dict['PolicyDetails']['PolicyNumber']},{"$set":dict},upsert=True)

    def convert_text(self,text):
        # print(text)
        policy={"Agent":{},"PolicyDetails":{},"CoverageDetails":{},'PaymentDetails':{}}
        for idx,tx in enumerate(text.split('\n')):
            # print(idx,tx)
            if 'JF Agent' in tx: policy['Agent']['Name'] = tx.split(' - ')[1]
            if idx == 1: policy['Agent']['Address'] = tx
            if idx == 2: policy['Agent']['PhoneNumber'] = tx
            if 'Policy Holder:' in tx: policy['PolicyDetails']['PolicyHolder'] = tx.split(': ')[1]
            if 'Date of Birth:' in tx: policy['PolicyDetails']['DateOfBirth'] = tx.split(': ')[1]
            if 'Address:' in tx: policy['PolicyDetails']['Address1'] = tx.split(': ')[1]
            if idx == 8: policy['PolicyDetails']['Address2'] = tx
            if 'Phone Number:' in tx: policy['PolicyDetails']['PhoneNumber'] = tx.split(': ')[1]
            if 'Email:' in tx: policy['PolicyDetails']['Email'] = tx.split(': ')[1]
            if 'Policy Number:' in tx: policy['PolicyDetails']['PolicyNumber'] = tx.split(': ')[1]
            if 'Application Date:' in tx: policy['PolicyDetails']['ApplicationDate'] = tx.split(': ')[1]
            if 'Effective Date:' in tx: policy['PolicyDetails']['EffectiveDate'] = tx.split(': ')[1]
            if 'Expiry Date:' in tx: policy['PolicyDetails']['ExpiryDate'] = tx.split(': ')[1]
            if 'Number of Days:' in tx: policy['PolicyDetails']['NumberOfDays'] = tx.split(': ')[1]
            if 'Insurance Plan:' in tx: policy['CoverageDetails']['InsurancePlan'] = tx.split(':')[1]
            if idx==23: policy['CoverageDetails']['InsurancePlan'] += tx.replace('  ','')
            if 'Plan Type:' in tx: policy['CoverageDetails']['PlanType'] = tx.split(': ')[1]
            if 'Sum Insured:' in tx: policy['CoverageDetails']['SumInsured'] = tx.split(': $')[1]
            if 'Deductible:' in tx: policy['CoverageDetails']['Deductible'] = tx.split(': $')[1]
            if 'Beneficiary:' in tx: policy['CoverageDetails']['Beneficiary'] = tx.split(': ')[1]
            if 'Total Premium:' in tx: policy['PaymentDetails']['TotalPremium'] = tx.split(': $')[1]
            if 'Premium:' in tx:  policy['PaymentDetails']['Premium'] = tx.split(': $')[1]
            if 'Payment Date:' in tx: policy['PaymentDetails']['PaymentDate'] = tx.split(': ')[1]
            if 'Payment Method:' in tx: policy['PaymentDetails']['PaymentMethod'] = tx.split(': ')[1]

            if 'Special Note' in tx: policy['SpecialNote'] = ''
            if idx>=29 and idx<=51: policy['SpecialNote'] += tx
        # pprint(policy)
        return policy


    def get_pdf_text(self,fp):
        from pdfminer.pdfparser import PDFParser, PDFDocument
        from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
        from pdfminer.converter import PDFPageAggregator
        from pdfminer.layout import LAParams, LTTextBox, LTTextLine
        parser = PDFParser(fp)
        doc = PDFDocument()
        parser.set_document(doc)
        doc.set_parser(parser)
        doc.initialize('')
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        # Process each page contained in the document.
        text_total = ''
        for page in doc.get_pages():
            interpreter.process_page(page)
            layout = device.get_result()
            for lt_obj in layout:
                if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                    # print(lt_obj.get_text())
                    text_total += lt_obj.get_text()
        return text_total

    def delete_file(self):
        if request.method == "POST":
            data = json.loads(request.data)
            gfs = gridfs.GridFS(self.collection)
            for file in data:
                # files = file['files']
                deviceID = file['deviceID']
                response = []
                self.model.FileModel().delete_file([file['files']])
                # self.DeviceModel(deviceID).update_filenames(file['files'], delete=True)
            return json.dumps([])

    def download_file(self):
        objectID = request.args['fileID']
        gfs = gridfs.GridFS(self.collection)
        file = gfs.get(ObjectId(objectID)).read()
        response = make_response(file)
        response.headers['Content-Type'] = gfs.get(ObjectId(objectID)).content_type
        response.headers['filename'] = gfs.get(ObjectId(objectID)).filename
        response.headers["Content-Disposition"] = "attachment; filename= " + response.headers['filename'] + " "
        return response

    def paste_file(self):
        if request.method == "POST":
            data = json.loads(request.data)
            filesIDList = data['fileID']
            deviceID = data['deviceID']
            for filesID in filesIDList:
                file = self.model.FileModel(filesID).get()
                if '_id' in file:
                    del file['_id']
                    gfs = gridfs.GridFS(self.collection)
                    objectID = gfs.put(gfs.get(ObjectId(filesID)).read(),
                                       content_type=file['contentType'],
                                       filename=file['filename'])

                    file_device = {"objectID": str(objectID),
                                   "content_type": file['contentType'],
                                   "filename": file['filename'],
                                   "length": file['length'],
                                   "upload_date": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                                   }

                    device = self.model.FileModel().DeviceModel(deviceID).get()
                    device['filenames'].append(file_device)
                    self.model.FileModel().DeviceModel(deviceID).fast_set(filenames=device['filenames'])
            return json.dumps([])


