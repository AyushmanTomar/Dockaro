from pypdf import PdfReader,PdfWriter
from PIL import Image
import os

def extract_text():
    reader = PdfReader("test.pdf")
    page = reader.pages[1]
    print(page.extract_text())

def extract_img():
    reader = PdfReader("test.pdf")
    page = reader.pages[0]
    for count, image_file_object in enumerate(page.images):
        with open(str(count) + image_file_object.name, "wb") as fp:
            fp.write(image_file_object.data)


def merge_pdf():
    merger = PdfWriter()

    input1 = open("document1.pdf", "rb")
    input2 = open("document2.pdf", "rb")
    input3 = open("document3.pdf", "rb")

    # Add the first 3 pages of input1 document to output
    merger.append(fileobj=input1, pages=(0, 3))
    # Insert the first page of input2 into the output beginning after the second page
    merger.merge(position=2, fileobj=input2, pages=(0, 1))
    # Append entire input3 document to the end of the output document
    merger.append(input3)

    # Write to an output PDF document
    output = open("document-output.pdf", "wb")
    merger.write(output)
    merger.close()
    output.close()

def duplicate():
    reader = PdfReader("big-old-file.pdf")
    writer = PdfWriter()
    for page in reader.pages:
        writer.add_page(page)

    if reader.metadata is not None:
        writer.add_metadata(reader.metadata)

    with open("smaller-new-file.pdf", "wb") as fp:
        writer.write(fp)

def image_compression():
    writer = PdfWriter(clone_from="example.pdf")

    for page in writer.pages:
        for img in page.images:
            img.replace(img.image, quality=80)

    with open("out.pdf", "wb") as f:
        writer.write(f)

def loss_less():
    writer = PdfWriter(clone_from="example.pdf")
    for page in writer.pages:
        page.compress_content_streams()  # This is CPU intensive!

    with open("out.pdf", "wb") as f:
        writer.write(f)



def heavy_compression():
    duplicate()
    image_compression()
    loss_less()

def moderate_compression():
    duplicate()
    loss_less()



def compression ():
    ch=1
    if ch==1:
        loss_less()
    elif ch==2:
        moderate_compression()
    else:
        heavy_compression()



def encription():
    reader = PdfReader("test.pdf")
    writer = PdfWriter(clone_from=reader)

    writer.encrypt("ayushman", algorithm="AES-256")

    with open("encrypted-pdf.pdf", "wb") as f:
        writer.write(f)


def decript():
    #need corrrect password
    reader = PdfReader("encrypted-pdf.pdf")

    if reader.is_encrypted:
        reader.decrypt("ayushman")

    writer = PdfWriter(clone_from=reader)
    with open("decrypted-pdf.pdf", "wb") as f:
        writer.write(f)

def img_to_pdf(img_folder, output_pdf):
    img_files = [i for i in os.listdir(img_folder) if i.endswith(".jpg") or i.endswith(".png")]

    img_list = []
    for i in img_files:
        img_path = os.path.join(img_folder, i)
        img = Image.open(img_path)
        if img.mode == "RGBA":
            img = img.convert("RGB")
        img_list.append(img)

    if img_list:
        img_list[0].save(output_pdf, "PDF", resolution=100.0, save_all=True, append_images=img_list[1:])
    else:
        print("No images found in the folder.")


decript()