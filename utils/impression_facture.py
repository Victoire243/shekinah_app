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
    # Dossier de sortie
    dossier_sortie = (
        str(os.path.expanduser("~")).replace("\\", "/") + "/Factures SHEKINA PHARMA/"
    )
    if not os.path.exists(dossier_sortie):
        os.makedirs(dossier_sortie)
    fichier_sortie = dossier_sortie + f"facture_{num_facture}.pdf"

    # Création du canvas
    c = canvas.Canvas(filename=fichier_sortie, pagesize=A4)
    width, height = A4

    # Marges
    marge_gauche = 50
    marge_droite = 50
    marge_haut = 50
    marge_bas = 50

    # Position de départ en Y
    y_position = height - marge_haut

    # --------------------------------------------------------------------------
    # En-tête (partie statique)
    # --------------------------------------------------------------------------
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

    # En-tête droit et logo
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
    )
    if os.path.exists(logo_path):
        logo = ImageReader(logo_path)
        c.drawImage(
            logo,
            width - marge_droite - 175,
            height - marge_haut - 110,
            width=100,
            height=100,
        )

    # Titre de la facture centré
    c.setFont("Helvetica-Bold", 16)
    text = f"FACTURE N° {num_facture}"
    text_width = c.stringWidth(text, "Helvetica-Bold", 16)
    c.drawString((width - text_width) / 2, y_position, text)
    y_position -= 30

    # Informations du client
    c.setFont("Helvetica", 12)
    c.drawString(marge_gauche, y_position, f"Client {nom_client} doit ")
    y_position -= 30

    # --------------------------------------------------------------------------
    # Affichage du tableau avec découpage automatique sur plusieurs pages
    # --------------------------------------------------------------------------
    # On utilise une hauteur de ligne estimée (en points)
    row_height = 20

    # Configuration du tableau
    col_widths = [30, 40, 60, 200, 80, 80]
    table_style = TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),  # En-tête
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]
    )

    # Préparation des données du tableau
    # On suppose que la première ligne de list_medicaments est l'en-tête
    data_total = list_medicaments[:]  # copie de la liste
    if not data_total:
        data_total = [["", "", "", "", "", ""]]
    header = data_total[0]
    data_rows = data_total[1:]  # toutes les lignes après l'en-tête

    # --- Sur la première page ---
    # Calcul du nombre maximum de lignes (en incluant l'en-tête) qui tiennent sur la page actuelle
    available_height = y_position - marge_bas
    max_rows_first = int(available_height // row_height)
    if max_rows_first < 1:
        # Si même l'en-tête ne tient pas, on passe à une nouvelle page
        c.showPage()
        y_position = height - marge_haut
        available_height = y_position - marge_bas
        max_rows_first = int(available_height // row_height)

    # Si le tableau complet tient sur la page
    if len(data_total) <= max_rows_first:
        sub_table_data = data_total
        sub_table = Table(sub_table_data, colWidths=col_widths)
        sub_table.setStyle(table_style)
        w, h = sub_table.wrap(width - marge_gauche - marge_droite, height)
        sub_table.drawOn(c, marge_gauche, y_position - h)
        y_position = y_position - h - 20  # espacement après le tableau
    else:
        # Le tableau ne tient pas en entier sur la première page.
        # On affiche d'abord le sous-tableau composé de l'en-tête et des (max_rows_first - 1) premières lignes.
        first_chunk = data_rows[: max_rows_first - 1]  # -1 pour l'en-tête
        sub_table_data = [header] + first_chunk
        sub_table = Table(sub_table_data, colWidths=col_widths)
        sub_table.setStyle(table_style)
        w, h = sub_table.wrap(width - marge_gauche - marge_droite, height)
        sub_table.drawOn(c, marge_gauche, y_position - h)
        # Retirer les lignes déjà affichées
        data_rows = data_rows[max_rows_first - 1 :]
        # Fin de la page en cours
        c.showPage()
        # --- Sur les pages suivantes ---
        # Sur chaque page, la hauteur disponible est celle comprise entre marge_haut et marge_bas
        # Comme on réaffiche l'en-tête du tableau sur chaque page, on déduit une ligne.
        max_rows_other = int((height - marge_haut - marge_bas) // row_height) - 1
        while data_rows:
            current_y = height - marge_haut  # réinitialiser la position en haut de page
            # Prendre autant de lignes que possible
            chunk = data_rows[:max_rows_other]
            sub_table_data = [header] + chunk
            sub_table = Table(sub_table_data, colWidths=col_widths)
            sub_table.setStyle(table_style)
            w, h = sub_table.wrap(width - marge_gauche - marge_droite, height)
            sub_table.drawOn(c, marge_gauche, current_y - h)
            # Retirer les lignes affichées
            data_rows = data_rows[max_rows_other:]
            # Préparer la page suivante si besoin
            if data_rows:
                c.showPage()
        # Après le tableau, on place le curseur pour la suite
        y_position = current_y - h - 20

    # --------------------------------------------------------------------------
    # Affichage des totaux et autres informations (vérification de l'espace restant)
    # --------------------------------------------------------------------------
    # Si l'espace restant est insuffisant pour afficher la suite, on passe à une nouvelle page
    if y_position - 100 < marge_bas:
        c.showPage()
        y_position = height - marge_haut

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
    y_position -= 40

    # Message en rouge
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(colors.red)
    message = "LES MARCHANDISES VENDUES NE SONT NI REPRISES NI ECHANGEES"
    c.drawString(marge_gauche, y_position, message)
    y_position -= 30

    # --------------------------------------------------------------------------
    # Génération du code-barres
    # --------------------------------------------------------------------------
    c.setFillColor(colors.black)
    barcode_instance = code128.Code128(bar_code, barHeight=50, barWidth=1.2)
    barcode_instance.drawOn(c, width - marge_droite - 150, y_position - 50)

    # Sauvegarder le PDF
    c.save()
    ouvrir_fichier(fichier_sortie)


def ouvrir_fichier(fichier_pdf):
    if os.name == "nt":  # Windows
        os.startfile(fichier_pdf)
    elif os.name == "posix":  # Linux ou macOS
        subprocess.run(["xdg-open", fichier_pdf])
    else:
        print("Système d'exploitation non supporté pour l'ouverture automatique.")
