from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from cryptography import x509
from cryptography.hazmat.primitives.serialization import pkcs12
from PyPDF2 import PdfReader, PdfWriter
import requests
import os
import datetime
import qrcode
import tempfile
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from PIL import Image
from endesive import pdf


app = Flask(__name__)

def add_white_background(image):
    # Crear una nueva imagen con fondo blanco
    background = Image.new("RGB", image.size, (255, 255, 255))
    background.paste(image, (0, 0), image.convert("RGBA"))
    return background


def read_p12_file(p12_path, password):
    with open(p12_path, 'rb') as p12_file:
        p12_data = p12_file.read()

    # Cargar el archivo P12 y extraer la clave privada y el certificado
    private_key, certificate, _ = serialization.pkcs12.load_key_and_certificates(
        p12_data, password.encode(), backend=default_backend()
    )
    return private_key, certificate

def get_signer_name(certificate):
    # Obtener el nombre del firmante desde el certificado
    subject = certificate.subject
    return subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value




def download_file(url, save_path):
    try:
        print(f"Attempting to download file from {url}")
        response = requests.get(url)
        response.raise_for_status()  # Lanza un error si la descarga falla
        with open(save_path, 'wb') as f:
            f.write(response.content)
        print(f"Downloaded {url} with size {os.path.getsize(save_path)} bytes")
        return save_path
    except requests.exceptions.RequestException as e:
        print(f"Error downloading file from {url}: {str(e)}")
        raise Exception(f"Error downloading file from {url}: {str(e)}")

def generate_qr_code(data, qr_img_path):
    qr_img = qrcode.make(data)
    qr_img.save(qr_img_path)
    print(f"QR code saved as: {qr_img_path}")


def sign_pdf_imagenes(pdf_path, p12_path, p12_password, logo_path, signed_pdf_path):
    # Leer el PDF
    with open(pdf_path, 'rb') as pdf_file:
        pdf_data = pdf_file.read()

    pdf_reader = PdfReader(io.BytesIO(pdf_data))
    pdf_writer = PdfWriter()

    # Agregar todas las páginas al PdfWriter
    for page_num in range(len(pdf_reader.pages)):
        pdf_writer.add_page(pdf_reader.pages[page_num])

    # Crear un QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data('Firma Digital')
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white')

    # Guardar la imagen del QR en un archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        img.save(tmp_file, format='PNG')
        tmp_file_path = tmp_file.name

    # Leer el archivo P12 para obtener la clave privada y el certificado
    private_key, certificate = read_p12_file(p12_path, p12_password)

    # Obtener el nombre del firmante desde el certificado
    signer_name = get_signer_name(certificate)

    # Dividir el nombre y apellido en dos líneas
    name_parts = signer_name.split()
    if len(name_parts) >= 4:
        first_line = ' '.join(name_parts[:2])
        second_line = ' '.join(name_parts[2:])
    else:
        first_line = name_parts[0]
        second_line = ' '.join(name_parts[1:])

    # Cargar el logo desde el archivo descargado
    logo = Image.open(logo_path)  # Usar PIL para abrir el logo
    logo_with_background = add_white_background(logo)
    logo_tempfile = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    logo_with_background.save(logo_tempfile, format='PNG')
    logo_tempfile_path = logo_tempfile.name

    # Obtener la fecha actual
    current_date = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")

    # Crear un lienzo para la anotación de firma
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)

    # Dibujar el QR en el lienzo
    can.drawImage(tmp_file_path, 100, 100, width=80, height=80)

    # Dibujar el logo al lado del QR
    can.drawImage(logo_tempfile_path, 300, 130, width=50, height=50)

    can.setFont("Times-Bold", 7)
    # Agregar texto al lado de la imagen del QR
    can.drawString(175, 160, "Firmado digitalmente por")
    can.setFont("Times-Bold", 8)
    can.drawString(175, 150, first_line)
    can.drawString(175, 140, second_line)
    # Dibujar la fecha actual debajo del nombre
    can.drawString(175, 130, current_date)

    can.save()

    # Mover el lienzo al inicio del buffer
    packet.seek(0)
    new_pdf = PdfReader(packet)

    # Obtener la última página y agregar la anotación de firma
    last_page = pdf_writer.pages[-1]
    last_page.merge_page(new_pdf.pages[0])

    # Guardar el PDF firmado en un archivo
    with open(signed_pdf_path, 'wb') as output_pdf_file:
        pdf_writer.write(output_pdf_file)



def sign_pdf(pdf_file, p12_file, password, signed_pdf_file):
    # Leer el archivo .p12 y la contraseña
    # Leer el archivo .p12 y la contraseña
    with open(p12_file, "rb") as f:
        p12_data = f.read()
    private_key, certificate, additional_certificates = pkcs12.load_key_and_certificates(p12_data, password.encode())

    # Leer el archivo PDF
    with open(pdf_file, "rb") as f:
        data = f.read()

    # Obtener el número total de páginas y el tamaño de la última página
    reader = PdfReader(pdf_file)
    total_pages = len(reader.pages)
    page_height = int(reader.pages[total_pages - 1].mediabox[3])

    # Firmar el PDF
    dct = {
        "sigflags": 3,
        "contact": "GABRIEL ULPIANO GARCIA TORRES <gugarcia@utpl.edu.ec>",
        "location": "Ecuador",
        "signingdate": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%z"),
        "reason": "Firmado digitalmente",
        "signaturebox": (50, 50, 50, 50),  # Ajustar la ubicación de la firma a la parte inferior de la página
        "signature_manual": "qr.png",   # Esta es la apariencia de la firma. Puedes ajustar estos valores para cambiar la apariencia de la firma.
        "certification_level": 1,  # 1: No changes, 2: Form fill-in, 3: Form fill-in and annotations
        "identifier": "1102615794"  # Reemplaza con el valor real de la cédula
    } 
    signed_data = pdf.cms.sign(data, dct, private_key, certificate, [], 'sha256')

    # Guardar el PDF firmado
    with open(signed_pdf_file, "wb") as f:
        f.write(data)
        f.write(signed_data)

    print(f"Signed PDF saved as: {signed_pdf_file}")


@app.route('/sign_pdf', methods=['POST'])
def sign_pdf_route():
    p12_url = request.json.get('P12_URL')
    p12_password = request.json.get('P12_PASSWORD')
    pdf_url = request.json.get('pdf_url')
    logo_url = request.json.get('logo_url')

    p12_filename = os.path.basename(p12_url)
    pdf_filename = os.path.basename(pdf_url)
    logo_filename = os.path.basename(logo_url)
    
    p12_path = f'downloaded_{p12_filename}'
    pdf_path = f'downloaded_{pdf_filename}'
    logo_path = f'downloaded_{logo_filename}'
    signed_pdf_imagenes_path = f'firmadoimagenes_{pdf_filename}'
    signed_pdf_certificado_path = f'firmadocertificado_{pdf_filename}'

    try:
        download_file(p12_url, p12_path)
        download_file(pdf_url, pdf_path)
        download_file(logo_url, logo_path)

        if not os.path.exists(p12_path) or os.path.getsize(p12_path) == 0:
            raise Exception(f"P12 file not downloaded or is empty: {p12_path}")

        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise Exception(f"PDF file not downloaded or is empty: {pdf_path}")

        if not os.path.exists(logo_path) or os.path.getsize(logo_path) == 0:
            raise Exception(f"Logo file not downloaded or is empty: {logo_path}")

        sign_pdf_imagenes(pdf_path, p12_path, p12_password, logo_path, signed_pdf_imagenes_path)
        sign_pdf(pdf_path, p12_path, p12_password, signed_pdf_certificado_path)

        signed_pdf_url_imagenes = f"http://localhost:5000/{signed_pdf_imagenes_path}"
        signed_pdf_url_certificado = f"http://localhost:5000/{signed_pdf_certificado_path}"

        print(f"Response: {{'message': 'PDF signed successfully', 'signed_pdf_url_imagenes': '{signed_pdf_url_imagenes}', 'signed_pdf_url_certificado': '{signed_pdf_url_certificado}'}}")
        
        return jsonify({
            'message': 'PDF signed successfully',
            'signed_pdf_url_imagenes': signed_pdf_url_imagenes,
            'signed_pdf_url_certificado': signed_pdf_url_certificado
        }), 200

    except Exception as e:
        print(f"Error in /sign_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/hola', methods=['GET'])
def hello():
    return "Hola, mundo!"

if __name__ == '__main__':
    app.run(debug=True)
