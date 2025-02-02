import shutil
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import pathlib
import os
import subprocess
from reportlab.graphics.barcode import code128


def generer_facture(
    list_medicaments,
    prix_total,
    reduction,
    charges_connexes,
    date,
    bar_code,
    montant_final,
    nom_client,
    num_facture,
    montant_en_lettres,
):
    dossier_sortie = (
        str(os.path.expanduser("~")).replace("\\", "/") + "/Factures SHEKINA PHARMA/"
    )
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
    fichier_sortie = dossier_sortie + f"facture_{num_facture}.pdf"
    c = canvas.Canvas(filename=fichier_sortie, pagesize=A4)
    width, height = A4

    # Définir les marges
    marge_gauche = 50
    marge_droite = 50
    marge_haut = 50
    marge_bas = 50

    # Position de départ pour le contenu
    y_position = height - marge_haut

    # En-tête gauche
    c.setFont("Helvetica-Bold", 11)
    c.drawString(marge_gauche, y_position, "PHARMACIE SHEKINAK")
    y_position -= 15
    c.drawString(marge_gauche, y_position, "RCCM/20-A-782")
    y_position -= 15
    c.drawString(marge_gauche, y_position, "ID. NAT : 17-G4701-N773876")
    y_position -= 15
    c.drawString(marge_gauche, y_position, "N° IMPOT : A 2160128F")
    y_position -= 15
    c.drawString(marge_gauche, y_position, "Tél / (+243) 97 41 16 448, 82 76 062 44")
    y_position -= 15
    c.drawString(marge_gauche, y_position, "AV DU 04 JANVIER, C/KASUKU")
    y_position -= 15
    c.drawString(marge_gauche, y_position, "KINDU VILLE")
    y_position -= 30  # Espacement supplémentaire

    # En-tête droite
    c.setFont("Helvetica", 11)
    c.drawString(
        width - marge_droite - 190,
        height - marge_haut,
        f"Date : {date}",
    )
    c.setFont("Helvetica", 12)
    logo_path = (
        str(pathlib.Path(__file__).parent.parent.resolve()).replace("\\", "/")
        + "/assets/images/logo.png"
    )  # Remplace par le chemin de ton logo
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(
            logo,
            width - marge_droite - 175,
            height - marge_haut - 110,
            width=100,
            height=100,
        )

    # Titre de la facture
    c.setFont("Helvetica-Bold", 16)
    text = f"FACTURE N° {num_facture}"
    text_width = c.stringWidth(text, "Helvetica-Bold", 16)
    c.drawString((width - text_width) / 2, y_position, text)
    y_position -= 30  # Espacement supplémentaire

    # Informations du client
    c.setFont("Helvetica", 12)
    c.drawString(marge_gauche, y_position, f"Client {nom_client} doit ")
    y_position -= 30  # Espacement supplémentaire

    # Données du tableau
    # data = [
    #     ["N°", "Quantité", "Forme", "Produit", "Prix Unitaire", "Prix Total"],
    #     ["1", "2", "Comprimé", "Paracétamol", "5", "10"],
    #     ["2", "1", "Gélule", "Ibuprofène", "8", "8"],
    #     ["3", "1", "Instrument", "Thermomètre", "15", "15"],
    # ]

    # Ajouter des lignes supplémentaires pour simuler une longue table
    # for i in range(4, 5):
    #     data.append([str(i), "1", "Comprimé", f"Produit {i}", "10", "10"])

    # Créer le tableau avec ReportLab
    table = Table(
        list_medicaments, colWidths=[30, 60, 80, 160, 80, 80]
    )  # Ajuster les largeurs des colonnes
    table.setStyle(
        TableStyle(
            [
                (
                    "BACKGROUND",
                    (0, 0),
                    (-1, 0),
                    colors.grey,
                ),  # Couleur de fond pour l'en-tête
                (
                    "TEXTCOLOR",
                    (0, 0),
                    (-1, 0),
                    colors.whitesmoke,
                ),  # Couleur du texte pour l'en-tête
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),  # Alignement du texte au centre
                (
                    "FONTNAME",
                    (0, 0),
                    (-1, 0),
                    "Helvetica-Bold",
                ),  # Police en gras pour l'en-tête
                (
                    "BOTTOMPADDING",
                    (0, 0),
                    (-1, 0),
                    12,
                ),  # Espacement en bas pour l'en-tête
                (
                    "BACKGROUND",
                    (0, 1),
                    (-1, -1),
                    colors.beige,
                ),  # Couleur de fond pour les autres lignes
                ("GRID", (0, 0), (-1, -1), 1, colors.black),  # Bordures du tableau
            ]
        )
    )

    # Calculer la hauteur du tableau
    table_height = (
        len(list_medicaments) * 20
    )  # Estimation de la hauteur (20 points par ligne)

    # Vérifier si le tableau dépasse la hauteur disponible
    if y_position - table_height < marge_bas:
        c.showPage()  # Créer une nouvelle page
        y_position = height - marge_haut  # Réinitialiser la position Y

    # Dessiner le tableau sur le canvas
    table.wrapOn(c, width - marge_gauche - marge_droite, height)
    table.drawOn(c, marge_gauche, y_position - table_height)
    y_position -= table_height + 20  # Espacement après le tableau

    # Calculer le montant final

    # Ajouter les informations de total, réduction, charges et montant final
    c.setFont("Helvetica-Bold", 12)
    c.drawString(marge_gauche, y_position, f"Total : {prix_total}")
    y_position -= 20
    c.drawString(marge_gauche, y_position, f"Réduction accordée : {reduction}")
    y_position -= 20
    c.drawString(marge_gauche, y_position, f"Charges connexes : {charges_connexes}")
    y_position -= 20
    c.drawString(marge_gauche, y_position, f"Montant final à payer : {montant_final}")
    y_position -= 20
    c.setFillColor(colors.green)
    c.drawString(marge_gauche, y_position, f"En lettre : {montant_en_lettres}")
    y_position -= 40  # Espacement supplémentaire
    # Ajouter le message en rouge
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.red)
    message = "LES MARCHANDISES VENDUES NE SONT NI REPRISES NI ECHANGEES"
    c.drawString(marge_gauche, y_position, message)
    y_position -= 30  # Espacement supplémentaire

    # Générer un code-barres
    c.setFillColor(colors.black)
    barcode_instance = code128.Code128(bar_code, barHeight=50, barWidth=1.2)
    barcode_instance.drawOn(c, width - marge_droite - 150, y_position - 50)

    # Sauvegarder le PDF
    c.save()

    # Ouvrir le fichier PDF généré
    ouvrir_fichier(fichier_sortie)


def ouvrir_fichier(fichier_pdf):
    if os.name == "nt":  # Windows
        os.startfile(fichier_pdf)
    elif os.name == "posix":  # Linux ou macOS
        subprocess.run(["xdg-open", fichier_pdf])
    else:
        print("Système d'exploitation non supporté pour l'ouverture automatique.")

    # # deplacer le fichier dans le dossier de l'utilisateur (ecrasser le fichier si il existe)
    # try:
    #     shutil.copy(fichier_pdf, str(os.path.expanduser("~")) + "Facture")
    # except Exception as e:
    #     pass
    # # shutil.move(fichier_pdf, os.path.expanduser("~"))


# # Exemple d'utilisation
# list_medicaments = [
#     {
#         "designation": "Paracétamol",
#         "quantite": 2,
#         "forme": "Comprimé",
#         "prix_unitaire": 5,
#     },
#     {"designation": "Ibuprofène", "quantite": 1, "forme": "Gélule", "prix_unitaire": 8},
#     {
#         "designation": "Thermomètre",
#         "quantite": 1,
#         "forme": "Instrument",
#         "prix_unitaire": 15,
#     },
# ]
# prix_total = 33  # Total calculé
# reduction = 5  # Réduction accordée
# charges_connexes = 2  # Charges supplémentaires

# generer_facture(list_medicaments, prix_total, reduction, charges_connexes)
