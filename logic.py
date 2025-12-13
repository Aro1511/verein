def berechne_beitrag(mitglied):
    if mitglied.beitrag > 0:
        return mitglied.beitrag
    if mitglied.kategorie == "Kind":
        return 10
    elif mitglied.kategorie == "Familie":
        return 20
    elif mitglied.kategorie == "Erwachsener":
        return 15
    return 0
