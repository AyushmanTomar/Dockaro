from flask import Flask,request,render_template,make_response,send_file,jsonify
from io import BytesIO
from pypdf import PdfReader,PdfWriter
import os
import markdown
import re
import google.generativeai as genai
from dotenv import load_dotenv
load_dotenv()


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


@app.route('/pdfsummary')
def pdfsummary():
    return render_template('summary.html')


@app.route('/gensummary', methods=['POST'])
def summary():
    error=None
    file = request.files['file']
    extra = request.form['extra']
    specific=request.form['specific']
    reader = PdfReader(file)
    text = ""
    i=1
    for page in reader.pages:
        text = text+"page "+str(i)+":\n\n"+page.extract_text()
        i+=1
    prompt=text +"\nYour Name is DocKaro Ai, generate large page wise summary of the above text explaining concepts covered on that page concidering examples on that respective page.once this is done print At the end list of questions possible to ask in exam from the text.Tell no extra details."
    if(extra):
        prompt+=" also print"+extra+"in a new section named 'Answer to your question.'"
    elif(specific):
        prompt=text+"\n"+specific
    ans = dockaroai(prompt)
    html = markdown.markdown(ans)
    html = re.sub(r'\- ', '<br>', html)
    html = re.sub(r'\* ', '<br>', html)
    # print(html)
    return jsonify({'response': html})


def dockaroai(prompt):
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=api_key)
    
    generation_config = {
    "temperature": 0.2,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 15000,
    "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
    model_name="gemini-1.0-pro",
    generation_config=generation_config,
    )

    chat_session = model.start_chat(
    history=[
    ]
    )
    response = chat_session.send_message(prompt)
    return(response.text)


@app.route('/compress')
def compress():
    return render_template('compress.html')

@app.route('/compresspdf', methods=['POST'])
def compresspdf():
    images=request.form['images'] #1 for remove 0 to compress
    q = request.form['quality'] # returns integer from 0 -80
    q=int(q)
    file = request.files['file']
    print(images+"  ",images,q)
    if(file):
        reader = PdfReader(file)
        writer = PdfWriter()
        for page in reader.pages:
            writer.add_page(page)
        if reader.metadata is not None:
            writer.add_metadata(reader.metadata)
        if (images=='1'):
            writer.remove_images()
        for page in writer.pages:
            if(images=='0'):
                for img in page.images:
                    img.replace(img.image, quality=q)
            page.compress_content_streams()
            if reader.metadata is not None:
                writer.add_metadata(reader.metadata)

        stream = BytesIO()
        writer.write(stream)
        stream.seek(0)
        file_name=file.filename[:-4]+"_compressed.pdf"
        response = make_response(send_file(stream, mimetype='application/pdf'))
        response.headers["Content-Disposition"] = f"attachment; filename={file_name}"
        return response

    



if __name__ == '__main__':
    app.run(debug=True)