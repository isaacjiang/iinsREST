
import gridfs
from pymongo import MongoClient
from flask import g
from bson import ObjectId

class FilesModel():
    def __init__(self):
        self.db_file = getattr(g,'database',MongoClient('localhost', 27017)).iins_files
        self.gfs = gridfs.GridFS(self.db_file)


    def upload_file(self,file,content_type,filename):

        file_id = self.gfs.put(file,content_type=content_type,filename=filename)
        gridfsOut = self.gfs.get(file_id)
        output = {"file_id": str(file_id),"content_type": gridfsOut.content_type,
         "filename": gridfsOut.filename,"length": gridfsOut.length,"upload_date": gridfsOut.upload_date.strftime('%Y-%m-%d %H:%M:%S')
         }
        return output

    def download_file(self,file_id):

        file_object=self.gfs.get(ObjectId(file_id))

        return file_object