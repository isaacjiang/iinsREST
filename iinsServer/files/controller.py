
from flask import make_response, request, json
from . import models
from pymongo import MongoClient

from pprint import pprint

class FileService():
    def __init__(self):
        self.model = models
        self.db_policy = MongoClient('localhost', 27017).db_policy


    def upload_documents(self):
        output = []
        if len(request.files) > 0:
            for i in range(0, len(request.files)):
                inputfile= request.files['file']

                gridfsOut=self.model.FilesModel().upload_file(inputfile.read(),
                                                 content_type=inputfile.content_type,
                                                 filename=inputfile.filename)
                output.append(gridfsOut)

                # text =  self.get_pdf_text(inputfile)
                # dictct=self.convert_text(text)
                # dict['PolicyDocument'] = output
                # self.save(dict)
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
            elif idx == 1: policy['Agent']['Address'] = tx
            elif idx == 2: policy['Agent']['PhoneNumber'] = tx
            elif 'Policy Holder:' in tx: policy['PolicyDetails']['PolicyHolder'] = tx.split(': ')[1]
            elif 'Date of Birth:' in tx: policy['PolicyDetails']['DateOfBirth'] = tx.split(': ')[1]
            elif 'Address:' in tx: policy['PolicyDetails']['Address1'] = tx.split(': ')[1]
            elif idx == 8: policy['PolicyDetails']['Address2'] = tx
            elif 'Phone Number:' in tx: policy['PolicyDetails']['PhoneNumber'] = tx.split(': ')[1]
            elif 'Email:' in tx: policy['PolicyDetails']['Email'] = tx.split(': ')[1]
            elif 'Policy Number:' in tx: policy['PolicyDetails']['PolicyNumber'] = tx.split(': ')[1]
            elif 'Application Date:' in tx: policy['PolicyDetails']['ApplicationDate'] = tx.split(': ')[1]
            elif 'Effective Date:' in tx: policy['PolicyDetails']['EffectiveDate'] = tx.split(': ')[1]
            elif 'Expiry Date:' in tx: policy['PolicyDetails']['ExpiryDate'] = tx.split(': ')[1]
            elif 'Number of Days:' in tx: policy['PolicyDetails']['NumberOfDays'] = tx.split(': ')[1]
            elif 'Insurance Plan:' in tx: policy['CoverageDetails']['InsurancePlan'] = tx.split(':')[1]
            elif idx==23: policy['CoverageDetails']['InsurancePlan'] += tx.replace('  ','')
            elif 'Plan Type:' in tx: policy['CoverageDetails']['PlanType'] = tx.split(': ')[1]
            elif 'Sum Insured:' in tx: policy['CoverageDetails']['SumInsured'] = tx.split(': $')[1]
            elif 'Deductible:' in tx: policy['CoverageDetails']['Deductible'] = tx.split(': $')[1]
            elif 'Beneficiary:' in tx: policy['CoverageDetails']['Beneficiary'] = tx.split(': ')[1]
            elif 'Total Premium:' in tx: policy['PaymentDetails']['TotalPremium'] = tx.split(': $')[1]
            elif 'Premium:' in tx:  policy['PaymentDetails']['Premium'] = tx.split(': $')[1]
            elif 'Payment Date:' in tx: policy['PaymentDetails']['PaymentDate'] = tx.split(': ')[1]
            elif 'Payment Method:' in tx: policy['PaymentDetails']['PaymentMethod'] = tx.split(': ')[1]

            elif 'Special Note' in tx: policy['SpecialNote'] = ''
            elif idx>=29 and idx<=51: policy['SpecialNote'] += tx
        pprint(policy)
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
        # doc.initialize('')
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
        # print(request.args)
        file_object = self.model.FilesModel().download_file(request.args['file_id'])
        response = make_response(file_object.read())
        response.headers['Content-Type'] = file_object.content_type
        response.headers['filename'] = file_object.filename
        response.headers["Content-Disposition"] = "attachment; filename= " + response.headers['filename'] + " "
        # response.headers["Content-Disposition"] = "inline"
        return response



