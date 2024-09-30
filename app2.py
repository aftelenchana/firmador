from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.serialization import pkcs12
from PyPDF2 import PdfReader, PdfWriter
import requests
import os
import datetime
import qrcode
from endesive import pdf

app = Flask(__name__)

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

    # Definir nombres de archivos para la descarga
    p12_filename = os.path.basename(p12_url)
    pdf_filename = os.path.basename(pdf_url)
    
    # Definir rutas para los archivos descargados
    p12_path = f'downloaded_{p12_filename}'
    pdf_path = f'downloaded_{pdf_filename}'
    signed_pdf_path = f'firmado_{pdf_filename}'

    try:
        # Descargar los archivos
        download_file(p12_url, p12_path)
        download_file(pdf_url, pdf_path)

        # Verificar la existencia de los archivos descargados
        if not os.path.exists(p12_path) or os.path.getsize(p12_path) == 0:
            raise Exception(f"P12 file not downloaded or is empty: {p12_path}")

        if not os.path.exists(pdf_path) or os.path.getsize(pdf_path) == 0:
            raise Exception(f"PDF file not downloaded or is empty: {pdf_path}")

        # Firmar el PDF
        sign_pdf(pdf_path, p12_path, p12_password, signed_pdf_path)

        # Generar la URL para acceder al PDF firmado
        signed_pdf_url = f"http://localhost:5000/{signed_pdf_path}"

        return jsonify({'message': 'PDF signed successfully', 'signed_pdf_url': signed_pdf_url}), 200

    except Exception as e:
        print(f"Error in /sign_pdf: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/hola', methods=['GET'])
def hello():
    return "Hola, mundo!"

if __name__ == '__main__':
    app.run(debug=True)
