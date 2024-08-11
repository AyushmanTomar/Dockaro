from flask import Flask,request,render_template,make_response,send_file,after_this_request
import io
from io import BytesIO
from pypdf import PdfReader,PdfWriter

app = Flask(__name__)

@app.route('/')
def homepage():
    return render_template('index.html')


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/encrypt')
def encryptpdf():
    return render_template('encrypt.html',error=None)

@app.route('/decrypt')
def decryptpdf():
    return render_template('decrypt.html',error=None)


@app.route('/encryptpdf', methods=['POST'])
def encrypt_pdf():
    error=None
    file = request.files['file']
    password = request.form['password']
    repassword=request.form['repassword']
    if(password!=repassword):
        error="Error: Password doesn’t match!!"
        return(render_template('encrypt.html',error=error))

    if file and password:
        reader = PdfReader(file)
        writer = PdfWriter(clone_from=reader)
        writer.encrypt(password, algorithm="AES-256")
        stream = BytesIO()
        writer.write(stream)
        stream.seek(0)
        file_name=file.filename[:-4]+"_encrypted.pdf"
        response = make_response(send_file(stream, mimetype='application/pdf'))
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        return response
    error="Error: File or password missing"
    return(render_template('encrypt.html',error=error))

@app.route('/decryptpdf', methods=['POST'])
def decrypt_pdf():
    error=None
    file = request.files['file']
    password = request.form['password']
    repassword=request.form['repassword']
    if(password!=repassword):
        error="Error: Password doesn’t match!!"
        return(render_template('encrypt.html',error=error))

    if file and password:
        reader = PdfReader(file)
        if reader.is_encrypted:
            reader.decrypt(password)
            writer = PdfWriter(clone_from=reader)
            stream = BytesIO()
            writer.write(stream)
            stream.seek(0)
            file_name=file.filename[:-4]+"_decrypted.pdf"
            response = make_response(send_file(stream, mimetype='application/pdf'))
            response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
            return response
        else:
            error="Error: File is not encrypted"
            return(render_template('decrypt.html',error=error))
    error="Error: File or password missing"
    return(render_template('encrypt.html',error=error))

if __name__ == '__main__':
    app.run(debug=True)