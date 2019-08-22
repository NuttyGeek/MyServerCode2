from flask import request
from flask_restful import Resource
from server_app.helper import filter_sentence, print_it, make_a_dir
from werkzeug.utils import secure_filename
import os
import server_app.object_detection_helper as object_detection
from server_app.tools import app_path


class Hello(Resource):
    def get(self):
        return {"name": "Speech To Text"}

class Ping(Resource):
    def get(self):
        return  {"status": "Working"}


cwd = os.getcwd()
print("cwd: "+cwd)
UPLOAD_FOLDER = '/tmp/uploadFolder'
FRAME_UPLOAD_FOLDER = cwd+"/server_app/input/"
FRAMES_PROCESSED_FOLDER = cwd+"/server_app/output/"
class Upload(Resource):
    def post(self):
        file = request.files['image']
        print("got the file")
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            return {"message": True}


class Keywords(Resource):
    def post(self):
        args = request.get_json()
        sentence = args['sentence']
        keywords = filter_sentence(sentence)
        return {'keywords': keywords}

class SpeechToText(Resource):
    def post(self):
        args = request.args
        files = args['files']
        response_final = print_it(files)
        return response_final

class ObjectDetection(Resource):
    '''
    take the video and frame and 
    '''
    def post(self):
        file = request.files['frame']
        print("got the file")
        args = request.form
        video_name = args['video']
        if file:
            filename = secure_filename(file.filename)
            print("[saving raw file] filename: "+filename)
            file.save(os.path.join(FRAME_UPLOAD_FOLDER,video_name,filename))
            print("saved the file in os")
        # create a dircetory for uploading files 
        make_a_dir(FRAME_UPLOAD_FOLDER+video_name)
        # create a dir for processed images 
        make_a_dir(FRAMES_PROCESSED_FOLDER+video_name)
        object_detection.execute(filename, video_name)
        res = object_detection.create_pixel_dict(FRAMES_PROCESSED_FOLDER+video_name+"/"+filename,
        FRAME_UPLOAD_FOLDER+video_name+"/"+filename)
        return {'video':video_name,'frame': filename,'data': res}