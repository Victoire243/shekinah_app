def number_to_words(num):
    units = ["", "un", "deux", "trois", "quatre", "cinq", "six", "sept", "huit", "neuf"]
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
        "",
        "vingt",
        "trente",
        "quarante",
        "cinquante",
        "soixante",
        "septante",
        "quatre-vingts",
        "nonante",
    ]

    if num == 0:
        return "zéro"

    if num < 0:
        return "moins " + number_to_words(-num)

    words = ""

    if num // 1000000000 > 0:
        words += number_to_words(num // 1000000000) + " milliard "
        num %= 1000000000

    if num // 1000000 > 0:
        mmi = num // 1000000
        if mmi == 1:
            words += "un million "
        else:
            words += number_to_words(mmi) + " millions "
        num %= 1000000

    if num // 1000 > 0:
        dizm = num // 1000
        if dizm == 1:
            words += "mille "
        else:
            words += number_to_words(dizm) + " mille "
        num %= 1000

    if num // 100 > 0:
        ctm = num // 100
        if ctm == 1:
            words += "cent "
        else:
            words += units[ctm] + " cents "
        num %= 100

    if num > 19:
        words += tens[num // 10] + " "
        num %= 10
    elif num >= 10:
        words += teens[num - 10] + " "
        return words.strip()

    if num > 0:
        words += units[num] + " "

    return words.strip().capitalize()
