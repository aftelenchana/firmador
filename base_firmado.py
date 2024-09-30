from endesive import pdf
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.hazmat.primitives import hashes
import datetime
from PyPDF2 import PdfReader

def sign_pdf(pdf_file, p12_file, password, signed_pdf_file):
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

# Uso del script
sign_pdf("downloaded_2909202401099331702000120010030000001121234567812.pdf", "pp.p12", "Inspi1234", "documento_firmado2.pdf")