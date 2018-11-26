from flask import Flask, render_template, url_for, request, redirect,flash, send_from_directory, Markup, Response
from werkzeug.utils import secure_filename
from db_setup import Base, courseDetails
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from flask_sqlalchemy import SQLAlchemy
from boto3 import client
import boto3


app = Flask(__name__)

DATABASE_URL = os.environ['DATABASE_URL']
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
UPLOAD_FOLDER = pathToFiles
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
uploadFolder = app.config['UPLOAD_FOLDER']

#----- creating pages - views

@app.route('/')
@app.route('/home')
@app.route('/index')
def index():
    listRecentDetails = session.query(courseDetails).all()
    revlistRecentDetails = reversed(listRecentDetails)
    counter=0
    newlistRecentDetails=[]
    for course in revlistRecentDetails:
        if counter != 10:
            newlistRecentDetails.append(course)
            counter += 1
        else:
            break
    return render_template('index.html', newlistRecentDetails=newlistRecentDetails)

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

#store store files to folder, details to database and rename both filename on both filesystem and database
@app.route('/storeDetails', methods=['POST', 'GET'])
def storeDetails():
    if request.method == 'POST':
        file = request.files['file-name']
        if file.filename == " ":
            flash("you didnt select any file")
            return redirect('upload')
        else:
            courseTitle = request.form['course-title']
            courseCode = valid_code(request.form['course-code'])
            Category = request.form['category']
            Year = request.form['year']
            if (courseTitle and courseCode and Category and Year and valid_ext(file.filename) and 'file-name' in request.files):    
                fileName = secure_filename(file.filename)
                filePath = os.path.join(uploadFolder, fileName)
                newDetail = courseDetails(
                    filepath = filePath,
                    filename = fileName,
                    coursetitle = courseTitle,
                    coursecode = courseCode,
                    category = Category,
                    year = Year,
                )
                session.rollback()
                session.add(newDetail)
                session.commit()

                filename = secure_filename(file.filename)
                fileExt = "."+filename.rsplit('.',1)[1].lower()
                #rename file in database
                getFile = session.query(courseDetails).filter_by(filename=fileName).one()
                getFile.filename = (str(getFile.id)+fileExt)
                newName = getFile.filename
                #rename path
                # filePath = os.path.join(uploadFolder, newName)
                # getFile.filepath = filePath
                #rename file to be stored in folder
                # file.save(os.path.join(uploadFolder, filename))
                s3 = boto3.resource('s3')
                s3.Bucket('actscibucket').put_object(Key=newName, Body=file)
                session.add(getFile)
                session.commit()
                return redirect(url_for('index'))
            else:
                msg = Markup("Make sure you put in ALL file details before uploading.<br/>Files must be in DOC or PDF format")
                flash(msg)
                return redirect('upload')
    else:
        return redirect('upload')

def get_client():
    return client(
        's3',
        'us-east-1',
        aws_access_key_id = os.environ['S3_KEY_ID'],
        aws_secret_access_key= os.environ['S3_SECRET_KEY']
    )
    
# download files
@app.route('/download/<name>')
def download(name):
    s3 = get_client()
    file = s3.get_object(Bucket='actscibucket', Key=name)
    
    return Response(
        file['Body'].read(),
        mimetype='text/plain',
        headers={"Content-Disposition": "attachment;filename=%s" % name}
    )

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
