def number_to_words(nombre):
    # units = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
    # teens = [
    #     "dix",
    #     "onze",
    #     "douze",
    #     "treize",
    #     "quatorze",
    #     "quinze",
    #     "seize",
    #     "dix-sept",
    #     "dix-huit",
    #     "dix-neuf",
    # ]
    # tens = [
    #     "",
    #     "",
    #     "vingt",
    #     "trente",
    #     "quarante",
    #     "cinquante",
    #     "soixante",
    #     "septante",
    #     "quatre-vingts",
    #     "nonante",
    # ]

    # if num == 0:
    #     return "zéro"

    # if num < 0:
    #     return "moins " + number_to_words(-num)

    # words = ""

    # if num // 1000000000 > 0:
    #     words += number_to_words(num // 1000000000) + " milliard "
    #     num %= 1000000000

    # if num // 1000000 > 0:
    #     mmi = num // 1000000
    #     if mmi == 1:
    #         words += "un million "
    #     else:
    #         words += number_to_words(mmi) + " millions "
    #     num %= 1000000

    # if num // 1000 > 0:
    #     dizm = num // 1000
    #     if dizm == 1:
    #         words += "mille "
    #     else:
    #         words += number_to_words(dizm) + " mille "
    #     num %= 1000

    # if num // 100 > 0:
    #     ctm = num // 100
    #     if ctm == 1:
    #         words += "cent "
    #     else:
    #         words += units[ctm] + " cents "
    #     num %= 100

    # if num > 19:
    #     words += tens[num // 10] + " "
    #     num %= 10
    # elif num >= 10:
    #     words += teens[num - 10] + " "
    #     return words.strip()

    # if num > 0:
    #     words += units[num] + " "

    # return words.strip().capitalize()
    units = [
        "zéro",
        "un",
        "deux",
        "trois",
        "quatre",
        "cinq",
        "six",
        "sept",
        "huit",
        "neuf",
    ]
    teens = [
        "dix",
        "onze",
        "douze",
        "treize",
        "quatorze",
        "quinze",
        "seize",
        "dix-sept",
        "dix-huit",
        "dix-neuf",
    ]
    tens = [
        "",
        "dix",
        "vingt",
        "trente",
        "quarante",
        "cinquante",
        "soixante",
        "soixante-dix",
        "quatre-vingt",
        "quatre-vingt-dix",
    ]

    def convert_chunk(chunk):
        if chunk < 10:
            return units[chunk]
        elif 10 <= chunk < 20:
            return teens[chunk - 10]
        elif 20 <= chunk < 100:
            return tens[chunk // 10] + (
                "-" + convert_chunk(chunk % 10) if chunk % 10 != 0 else ""
            )
        elif 100 <= chunk < 1000:
            if chunk // 100 == 1:
                return "cent" + (
                    " " + convert_chunk(chunk % 100) if chunk % 100 != 0 else ""
                )
            else:
                return (
                    units[chunk // 100]
                    + " cent"
                    + (" " + convert_chunk(chunk % 100) if chunk % 100 != 0 else "")
                )
        elif 1000 <= chunk < 1000000:
            if chunk // 1000 == 1:
                return "mille" + (
                    " " + convert_chunk(chunk % 1000) if chunk % 1000 != 0 else ""
                )
            else:
                return (
                    convert_chunk(chunk // 1000)
                    + " mille"
                    + (" " + convert_chunk(chunk % 1000) if chunk % 1000 != 0 else "")
                )
        elif 1000000 <= chunk < 1000000000:
            return (
                convert_chunk(chunk // 1000000)
                + " million"
                + (" " + convert_chunk(chunk % 1000000) if chunk % 1000000 != 0 else "")
            )
        elif 1000000000 <= chunk < 1000000000000:
            return (
                convert_chunk(chunk // 1000000000)
                + " milliard"
                + (
                    " " + convert_chunk(chunk % 1000000000)
                    if chunk % 1000000000 != 0
                    else ""
                )
            )
        else:
            return "Nombre trop grand"

    if isinstance(nombre, float):
        entier, decimal = str(abs(nombre)).split(".")
        entier = int(entier)
        decimal = int(decimal)
        partie_entiere = convert_chunk(entier)
        partie_decimale = convert_chunk(decimal)
        return f"{'moins ' if nombre < 0 else ''}{partie_entiere} virgule {partie_decimale}"
    else:
        if nombre < 0:
            return f"moins {convert_chunk(abs(nombre))}"
        else:
            return convert_chunk(nombre)
