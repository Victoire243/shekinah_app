from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from barcode import Code128
from barcode.writer import ImageWriter
import os


def generate_invoice(invoice_number, client_name, items, total, output_path):
    pdf_path = os.path.join(output_path, f"facture_{invoice_number}.pdf")
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4

    # Ajouter le logo et le nom de l'entreprise
    c.drawImage(
        "logo.png", 2 * cm, height - 3 * cm, width=4 * cm, height=2 * cm
    )  # Assurez-vous d'avoir un logo.png
    c.setFont("Helvetica-Bold", 16)
    c.drawString(7 * cm, height - 2 * cm, "Nom de l'entreprise")

    # Informations de la facture
    c.setFont("Helvetica", 12)
    c.drawString(2 * cm, height - 5 * cm, f"Numéro de facture: {invoice_number}")
    c.drawString(2 * cm, height - 6 * cm, f"Client: {client_name}")

    # Ajouter les produits
    y_position = height - 8 * cm
    c.drawString(2 * cm, y_position, "Produits:")
    y_position -= 1 * cm
    for item in items:
        product, quantity, price = item
        c.drawString(2 * cm, y_position, f"- {product} (x{quantity}) : {price} $")
        y_position -= 0.8 * cm

    # Total
    c.setFont("Helvetica-Bold", 12)
    c.drawString(2 * cm, y_position, f"Total: {total} $")

    # Générer un code-barres en mémoire
    barcode_buffer = BytesIO()
    barcode = Code128(f"FACT-{invoice_number}", writer=ImageWriter())
    barcode.write(barcode_buffer)
    barcode_buffer.seek(0)

    # Insérer le code-barres dans le PDF
    c.drawImage(
        barcode_buffer, 2 * cm, y_position - 4 * cm, width=6 * cm, height=2 * cm
    )

    # Finaliser le PDF
    c.save()
    print(f"Facture générée : {pdf_path}")

    return pdf_path


# Exemple d'utilisation
items = [("Paracétamol", 2, 5), ("Ibuprofène", 1, 8), ("Thermomètre", 1, 15)]
generate_invoice("123456", "Jean Dupont", items, 33, output_path=".")
