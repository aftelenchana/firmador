from cryptography import x509
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization.pkcs12 import serialize_key_and_certificates, load_key_and_certificates
import datetime
from cryptography.hazmat.backends import default_backend

# Generar una clave privada
key = rsa.generate_private_key(
    public_exponent=65537,
    key_size=2048,
    backend=default_backend()
)

# Crear una solicitud de certificado
builder = x509.CertificateBuilder()

# Establecer los detalles del sujeto y del emisor
subject = issuer = x509.Name([
    x509.NameAttribute(NameOID.COMMON_NAME, u"NECCDA EVELYN MENDIETA GONZALEZ"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"ENTIDAD DE CERTIFICACION DE INFORMACION"),
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"EC"),
])

# Crear un certificado autofirmado
cert = builder.subject_name(
    subject
).issuer_name(
    issuer
).public_key(
    key.public_key()
).serial_number(
    x509.random_serial_number()
).not_valid_before(
    datetime.datetime.now(datetime.timezone.utc)
).not_valid_after(
    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=10*365)
).sign(key, hashes.SHA256(), default_backend())

# Crear un archivo .p12 y guardarlo
p12 = serialize_key_and_certificates(b"certificate.p12", key, cert, None, serialization.BestAvailableEncryption(b"1111"))
with open("firma1.p12", "wb") as f:
    f.write(p12)

# Validar la clave privada con el certificado generado
try:
    (loaded_key, loaded_cert, _) = load_key_and_certificates(p12, b"1111", default_backend())
    loaded_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    print("La clave privada coincide con el certificado.")
except Exception as e:
    print("Error al validar la clave privada con el certificado:", e)
