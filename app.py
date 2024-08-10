from flask import Flask,request,render_template

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/encryptpdf')
def encryptpdf():
    return render_template('upload.html')

if __name__ == '__main__':
    app.run(debug=True)