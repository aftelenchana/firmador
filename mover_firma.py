from PyPDF2 import PdfFileReader, PdfFileWriter

def move_signature_to_page(signed_pdf_file, output_pdf_file, page_number):
    # Leer el PDF firmado
    reader = PdfFileReader(signed_pdf_file)

    # Obtener la página con la firma
    signature_page = reader.getPage(-1)

    # Eliminar la página con la firma
    writer = PdfFileWriter()
    for i in range(reader.getNumPages() - 1):
        writer.addPage(reader.getPage(i))

    # Insertar la página con la firma en la posición deseada
    writer.insertPage(signature_page, page_number)

    # Guardar el PDF
    with open(output_pdf_file, "wb") as f:
        writer.write(f)

# Uso del script
move_signature_to_page("documento_firmado.pdf", "documento_firmado_final.pdf", 2)
