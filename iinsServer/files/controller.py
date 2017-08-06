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
        self.db_policy = MongoClient('localhost', 27017).db_policy


    def upload_documents(self):
        output = []
        if len(request.files) > 0:
            for i in range(0, len(request.files)):
                text =  self.get_pdf_text(request.files['file'])
                dict=self.convert_text(text)

                gridfsOut=self.model.FilesModel().upload_file(request.files['file'].read(),
                                                 content_type=request.files['file'].content_type,
                                                 filename=request.files['file'].filename)
                output.append(gridfsOut)
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

    def download_documents(self):
        print(request.args)
        file_object = self.model.FilesModel().download_file(request.args['file_id'])
        response = make_response(file_object.read())
        response.headers['Content-Type'] = file_object.content_type
        response.headers['filename'] = file_object.filename
        response.headers["Content-Disposition"] = "attachment; filename= " + response.headers['filename'] + " "
        return response



