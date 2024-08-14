from flask import Flask,request,render_template,make_response,send_file,jsonify,after_this_request,send_from_directory
from io import BytesIO
from pdf2image import convert_from_path
import os
import zipfile
from pypdf import PdfReader,PdfWriter
import os
import markdown
import fitz
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



@app.route('/toimages')
def pdfimages():
    return render_template('toimages.html',error="")



@app.route('/pdftoimages', methods=['POST'])
def topdfimages():
    if 'file' not in request.files:
        error= "No file part"
        return render_template('toimages.html',error=error)
    
    file = request.files['file']
    all = request.form.get('all','0')
    i = request.form.get('start','0')
    j = request.form.get('end','-1')
    
    if file.filename == '':
        error= "No selected file"
        return render_template('toimages.html',error=error)
    
    pdf_document = fitz.open(stream=file.read(), filetype="pdf")
    image_files = []
    if (all=='1'):
        i=0
        j=int(pdf_document.page_count)
        print(1)
    elif (j=='' or j==None or int(j)>pdf_document.page_count or int(j)<0):
        if(int(i)!=0):
            i=int(i)-1
        else:
            i=0
        j=int(pdf_document.page_count)
        print(2)
    elif ( int(i)>pdf_document.page_count or int(i)<0 ):
        i=0
        j=int(pdf_document.page_count)
    elif ( int(i)==0 ):
        i=0
        j=int(j)
    else:
        i=int(i)-1
        j=int(j)
        print(3)
    print(type(i),type(j))
    for page_num in range(i,j):
        page = pdf_document.load_page(page_num)
        pix = page.get_pixmap()
        image_filename = f"page_{page_num + 1}.png"
        pix.save(image_filename)
        image_files.append(image_filename)

    zip_buffer = BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for image_file in image_files:
            zip_file.write(image_file)
            os.remove(image_file)

    zip_buffer.seek(0)
    return send_file(zip_buffer, mimetype='application/zip', as_attachment=True, download_name='images.zip')



if __name__ == '__main__':
    app.run(debug=True)