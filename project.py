from flask import Flask, render_template, url_for, request, redirect,flash, send_from_directory
from werkzeug.utils import secure_filename
from db_setup import Base, courseDetails
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///filedetails.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

app = Flask(__name__)
ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'doc', 'jpeg'])
linkToCdir = os.path.dirname(os.path.abspath(__file__))
pathToFiles = os.path.dirname(os.path.join(linkToCdir, 'static/files/'))
UPLOAD_FOLDER = pathToFiles
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
uploadFolder = app.config['UPLOAD_FOLDER']

#creating pages - views

@app.route('/')
@app.route('/index')
@app.route('/home')
def index():
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    listRecentDetails = session.query(courseDetails).all()
    return render_template('index.html', listRecentDetails=listRecentDetails)

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


# Back end functionalities



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


#store file to folder on click - uploads
@app.route('/storefile', methods=['POST', 'GET'])
def storefile():
    if request.method == 'POST':
        courseTitle = request.form['course-title']
        courseCode = valid_code(request.form['course-code'])
        Category = request.form['category']
        Year = request.form['year']
        
        if (courseTitle and courseCode and Category and Year):
            file = request.files['file-name']
            if (valid_ext(file.filename) and 'file-name' in request.files):
                filename = secure_filename(file.filename)
                file.save(os.path.join(uploadFolder, filename))
                return redirect(url_for(
                    'storeDetails', 
                    fileName = filename,  
                    courseTitle=courseTitle, 
                    courseCode=courseCode,
                    Category = Category,
                    Year = Year
                    )
                )
        else:
            flash("make sure you put in ALL file details before uploading")
            return redirect('upload')
    return render_template('upload.html')
        

#store remaining file details to database
@app.route('/storeDetails/<fileName>/<courseTitle>/<courseCode>/<Category>/<Year>')
def storeDetails(fileName,courseTitle,courseCode,Category,Year):
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
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
    return redirect(url_for('index',))

# download engines
@app.route('/download/<name>')
def download(name):
    return send_from_directory(uploadFolder, name, as_attachment = True)

# search engine
@app.route('/getSearchInput', methods=['GET', 'POST'])
def getSearchInput():
    if request.method == 'POST':
        searchCode = valid_code(request.form['code'])
        if searchCode == "":
            flash("You did not type in any course code. Pls enter a valid course code")
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
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    getMatchingDetails = session.query(courseDetails).filter_by(coursecode = searchCode).all()
    if getMatchingDetails:
        return render_template('result.html', getMatchingDetails = getMatchingDetails)
    else:
        flash("no file found for that course code. pls check and enter correct code ")
        return redirect(url_for('result'))
        



if __name__=='__main__':
    app.secret_key = 'date_of_birth'
    app.run(debug=True)