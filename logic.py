from datetime import datetime

# Kategorien
FIXKOSTEN = ["Miete", "Nebenkosten", "Wärme", "Wasser"]
VARIABLE_AUSGABEN = ["Einkäufe", "Aktivitäten", "Aufwandkosten"]


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


def berechne_monatsausgaben(ausgaben, monat, jahr):
    gesamt = 0
    for a in ausgaben:
        datum = datetime.strptime(a.datum, "%Y-%m-%d")
        if datum.month == monat and datum.year == jahr:
            gesamt += a.betrag
    return gesamt


def berechne_jahresausgaben(ausgaben, jahr):
    gesamt = 0
    for a in ausgaben:
        datum = datetime.strptime(a.datum, "%Y-%m-%d")
        if datum.year == jahr:
            gesamt += a.betrag
    return gesamt


def berechne_fixkosten(ausgaben):
    return sum(a.betrag for a in ausgaben if a.kategorie in FIXKOSTEN)


def berechne_variable_ausgaben(ausgaben):
    return sum(a.betrag for a in ausgaben if a.kategorie in VARIABLE_AUSGABEN)
