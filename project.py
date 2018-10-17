from flask import Flask, render_template, url_for

app = Flask(__name__)

#creating pages

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/upload')
def upload():
    return render_template('upload.html')

@app.route('/search')
def search():
    return render_template('search.html')

@app.route('/result')
def result():
    return render_template('result.html')


if __name__=='__main__':
    app.run(debug=True)