from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import barcode
from barcode.writer import ImageWriter
import os
import subprocess


def generer_facture(facture, fichier_sortie="facture_a4.pdf"):
    # Créer un fichier PDF au format A4
    c = canvas.Canvas(fichier_sortie, pagesize=A4)
    width, height = A4  # Largeur = 210 mm, Hauteur = 297 mm

    # Ajouter le logo (en haut à gauche)
    logo_path = "assets/images/logo_shekinah_.png"  # Remplace par le chemin de ton logo
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(
            logo, 50, height - 100, width=100, height=50
        )  # Ajuster la taille et la position

    # Ajouter le nom de la pharmacie (à gauche, sous le logo)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(50, height - 130, facture["pharmacie"]["nom"])
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 150, facture["pharmacie"]["adresse"])
    c.drawString(50, height - 170, facture["pharmacie"]["telephone"])

    # Ajouter les informations du client et le numéro de facture (en haut à droite)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(width - 250, height - 100, "Facture pour :")
    c.setFont("Helvetica", 12)
    c.drawString(width - 250, height - 120, facture["client"]["nom"])
    c.drawString(width - 250, height - 140, facture["client"]["adresse"])
    c.drawString(
        width - 250, height - 160, f"Numéro de facture : {facture['numero_facture']}"
    )

    # Ajouter les détails des produits (au centre)
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, height - 210, "Détails de la facture :")
    c.setFont("Helvetica", 12)
    y = height - 230
    for produit in facture["produits"]:
        ligne = f"{produit['nom']} - {produit['quantite']} x {produit['prix_unitaire']} € = {produit['quantite'] * produit['prix_unitaire']} €"
        c.drawString(50, y, ligne)
        y -= 20  # Espace entre les lignes

    # Calculer le total
    total = sum(
        produit["quantite"] * produit["prix_unitaire"]
        for produit in facture["produits"]
    )
    c.setFont("Helvetica-Bold", 14)
    c.drawString(50, y - 30, f"Total : {total} €")

    # Ajouter la date
    c.setFont("Helvetica", 10)
    c.drawString(50, y - 60, f"Date : {facture['date']}")

    # Générer un code-barres
    code = facture["numero_facture"]
    code_barre = barcode.get("code128", code, writer=ImageWriter())
    code_barre_path = f"barcode_{code}"
    code_barre.save(code_barre_path)  # Sauvegarder le code-barre en image

    # Ajouter le code-barres en bas de la facture
    c.drawImage(
        f"{code_barre_path}.png", 50, 50, width=200, height=50
    )  # Ajuster la taille et la position

    # Enregistrer le PDF
    c.save()

    # Supprimer l'image du code-barres après utilisation
    os.remove(f"{code_barre_path}.png")

    # Ouvrir l'imprimante par défaut pour imprimer la facture
    imprimer_facture(fichier_sortie)


def imprimer_facture(fichier_pdf):
    """
    Ouvre l'imprimante par défaut pour imprimer le fichier PDF.
    """
    if os.name == "nt":  # Windows
        os.startfile(fichier_pdf, "print")
    elif os.name == "posix":  # Linux ou macOS
        subprocess.run(["lp", fichier_pdf])
    else:
        print("Système d'exploitation non supporté pour l'impression automatique.")


# Exemple d'utilisation
facture = {
    "pharmacie": {
        "nom": "Pharmacie du Coin",
        "adresse": "123 Rue de la Santé, Ville",
        "telephone": "01 23 45 67 89",
    },
    "client": {"nom": "Jean Dupont", "adresse": "456 Avenue des Patients, Ville"},
    "produits": [
        {"nom": "Paracétamol", "quantite": 2, "prix_unitaire": 5.0},
        {"nom": "Vitamine C", "quantite": 1, "prix_unitaire": 10.0},
    ],
    "date": "2023-10-25",
    "numero_facture": "FAC-2023-001",
}

generer_facture(facture)
