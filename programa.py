import OpenSSL.crypto as crypto
import datetime

def firmar_pdf_con_p12(p12_path, password, input_pdf_path, output_pdf_path, dct):
    try:
        # Carga el archivo .p12
        p12 = crypto.load_pkcs12(open(p12_path, 'rb').read(), password)

        # Obtiene la clave privada y el certificado
        private_key = p12.get_privatekey()
        certificate = p12.get_certificate()

        # Crea una cadena de firma utilizando los parámetros dct
        signature_text = f"Firmado por: {dct['contact']} ({dct['location']}) el {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

        # Firma el PDF (debes adaptar esto según tu caso específico)
        # Aquí solo se muestra cómo agregar la firma al PDF
        # Debes cargar el PDF real y aplicar la firma correctamente
        with open(input_pdf_path, 'rb') as pdf_file:
            pdf_data = pdf_file.read()
            signed_data = crypto.sign(private_key, pdf_data, 'sha256')

        # Guarda el PDF firmado
        with open(output_pdf_path, 'wb') as signed_pdf_file:
            signed_pdf_file.write(signed_data)

        print(f"PDF firmado correctamente y guardado como {output_pdf_path}")
    except Exception as e:
        print(f"Error al firmar el PDF: {str(e)}")

# Ruta al archivo .p12 y contraseña
p12_path = 'firma1.p12'
password = '1111'

# Ruta al PDF a firmar y ruta de salida para el PDF firmado
input_pdf_path = '12.pdf'
output_pdf_path = '12_firmado.pdf'


# Diccionario dct
dct = {
    "sigflags": 3,
    "contact": "contacto@ejemplo.com",
    "location": "Ecuador",
    "signingdate": datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d%H%M%S%z"),
    "reason": "Firmado digitalmente",
    "signaturebox": (50, 50, 150, 150),
    "signature_manual": "qr.png",
}

# Llama a la función para firmar el PDF
firmar_pdf_con_p12(p12_path, password, input_pdf_path, output_pdf_path, dct)
