# ---upload and download  imports ---
from __future__ import print_function
import os
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import io
from googleapiclient.http import MediaIoBaseDownload
# --------------
from flask import Flask, render_template, url_for, request, redirect,flash, send_from_directory, Markup, jsonify
from werkzeug.utils import secure_filename
from db_setup import Base, courseDetails
import requests
from sqlalchemy import create_engine, asc, desc
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy



DATABASE_URL = os.environ['DATABASE_URL']
app = Flask(__name__.split('.')[0])
app.secret_key = 'super_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

engine = create_engine(DATABASE_URL)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

ALLOWED_EXTENSIONS = set(['pdf','doc','docx'])
linkToCdir = os.path.dirname(__file__)
pathToFiles = os.path.dirname(os.path.join(linkToCdir, 'static/files/'))
pathToCred = os.path.join(linkToCdir,'project-actsci-60d303260f9b.json')
UPLOAD_FOLDER = pathToFiles
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
bucket = app.config['UPLOAD_FOLDER']


#----- creating pages - views

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/recent')
def recent():
    listRecentDetails = session.query(courseDetails).order_by(asc(courseDetails.id)).all()
    revlistRecentDetails = reversed(listRecentDetails)
    counter=0
    newlistRecentDetails=[]
    for course in revlistRecentDetails:
        if counter != 30:
            newlistRecentDetails.append(course)
            counter += 1
        else:
            break
    return render_template('recent.html', newlistRecentDetails=newlistRecentDetails)

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/search')
def search():
    return render_template('search.html')

# result route eliminated!
@app.route('/result')
def result():
    return render_template('result.html')

#----- Backend functionalities

#check for valid extention
def valid_ext(filename):
    return '.' in filename and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

#check for valid code name
def valid_code(code):
    if " " in code:
            splitedcode = code.rsplit(" ")
            jointcode = splitedcode[0]+splitedcode[1]
            return jointcode.upper()
    else:
            return code.upper()

def upload_file(newfile):
    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('storage.json')
    creds = store.get()
    filename = os.path.basename(newfile)
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
        
    DRIVE = discovery.build('drive', 'v2', http=creds.authorize(Http()))

    metadata = {'title': filename, 'parents':[{'id': '1w5m48c-7CrcaCOuI9aGnxeXKIoDCutcN', 'kind':'drive#childList'}]}
    res = DRIVE.files().insert(body=metadata,
            media_body=newfile, fields='mimeType,exportLinks,id').execute()
    if res:
        return res['id']
         

#store store files to folder, details to database and rename both filename on both filesystem and database
@app.route('/storeDetails', methods=['POST', 'GET'])
def storeDetails():
    if request.method == 'POST':
        file = request.files['file-name']
        if file.filename == " ":
            flash("pls select a file")
            return redirect('upload')
        else:
            courseTitle = request.form['course-title']
            courseCode = valid_code(request.form['course-code'])
            Category = request.form['category']
            if (courseTitle and courseCode and Category and valid_ext(file.filename) and 'file-name' in request.files):

                # first upload file to base folder
                fileName = secure_filename(file.filename)
                file.save(os.path.join(bucket, fileName))
                filePath = os.path.join(bucket, fileName)

                # second push file to cloud
                download_id = upload_file(filePath)  

                # store file details in data base 
                # past question will have the year beside it - past question-2019
                newDetail = courseDetails(
                    filepath = filePath,
                    filename = fileName,
                    coursetitle = courseTitle,
                    coursecode = courseCode,
                    download_id = download_id,
                    category = Category,
                )
                session.rollback()
                session.add(newDetail)
                session.commit()

                # rename file with course title field
                filename = secure_filename(file.filename)
                fileExt = "."+filename.rsplit('.',1)[1].lower()

                #rename file in database
                getFile = session.query(courseDetails).filter_by(filename=fileName).one()
                file_num = str(getFile.id)
                newName = getFile.coursetitle+" uid: "+file_num
                getFile.filename = newName+fileExt
                # getFile.coursetitle = newName
                session.add(getFile)
                session.commit()

                return redirect(url_for('recent'))
            else:
                msg = Markup("Make sure you put in ALL file details before uploading.<br/>Files must be in DOC or PDF format")
                flash(msg)
                return redirect('upload')
    else:
        return redirect('upload')

# download files
@app.route('/download/<file_id>')
def download(file_id):
    SCOPES = 'https://www.googleapis.com/auth/drive'
    store = file.Storage('storage.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
        
    DRIVE = discovery.build('drive', 'v2', http=creds.authorize(Http()))
    request = DRIVE.files().get_media(fileId=file_id)
    # flash('Downloading...')
    getFile = session.query(courseDetails).filter_by(download_id=file_id).one()
    file_name = getFile.filename
    print(file_name)
    fh = io.FileIO(os.path.join(bucket, file_name), mode='w')
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
    return send_from_directory(bucket,file_name, as_attachment=True)
    

# search for files
@app.route('/getSearchInput', methods=['GET', 'POST'])
def getSearchInput():
    if request.method == 'POST':
        searchCode = valid_code(request.form['code'])
        if searchCode == "":
            flash("Pls enter a valid course code")
            return render_template('result.html')
        if searchCode and 'code' in request.form:
            return redirect(url_for('compareinput', searchCode = searchCode))
        else:
            #flash message here
            flash("You did not enter any course code")
            return redirect(url_for('search'))
    return redirect(url_for('result'))

#compare input with database and show result
@app.route('/compareinput/<searchCode>')
def compareinput(searchCode):
    getMatchingDetails = session.query(courseDetails).filter_by(coursecode = searchCode).all()
    displayCode = searchCode
    if getMatchingDetails:
        return render_template('result.html', getMatchingDetails = getMatchingDetails, displayCode=displayCode)
    else:
        flash("No file found. Pls enter correct code")
        return redirect(url_for('result'))


if __name__=='__main__':
    app.run(debug=True)


    # # ALTER SEQUENCE course_details_id_seq RESTART WITH 1
