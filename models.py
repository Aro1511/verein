class Mitglied:
    def __init__(self, name: str, kategorie: str, beitrag: float = 0.0):
        self.name = name
        self.kategorie = kategorie
        self.beitrag = beitrag

    def to_dict(self):
        return {"name": self.name, "kategorie": self.kategorie, "beitrag": self.beitrag}

    @staticmethod
    def from_dict(data: dict):
        return Mitglied(data["name"], data["kategorie"], float(data.get("beitrag", 0)))


class Aktivitaet:
    def __init__(self, name: str, ort: str, teilnehmer: list = None):
        self.name = name
        self.ort = ort
        self.teilnehmer = teilnehmer or []

    def to_dict(self):
        return {"name": self.name, "ort": self.ort, "teilnehmer": self.teilnehmer}

    @staticmethod
    def from_dict(data: dict):
        return Aktivitaet(data["name"], data["ort"], data.get("teilnehmer", []))


class Idee:
    def __init__(self, titel: str, geber: str):
        self.titel = titel
        self.geber = geber

    def to_dict(self):
        return {"titel": self.titel, "geber": self.geber}

    @staticmethod
    def from_dict(data: dict):
        return Idee(data["titel"], data["geber"])


class Einkommen:
    def __init__(self, name: str, art: str, betrag: float, datum: str):
        self.name = name
        self.art = art
        self.betrag = betrag
        self.datum = datum

    def to_dict(self):
        return {"name": self.name, "art": self.art, "betrag": self.betrag, "datum": self.datum}

    @staticmethod
    def from_dict(data: dict):
        return Einkommen(data["name"], data["art"], float(data.get("betrag", 0)), data.get("datum", ""))


# ✅ NEU: Ausgabe-Klasse
class Ausgabe:
    def __init__(self, kategorie: str, betrag: float, datum: str):
        self.kategorie = kategorie
        self.betrag = betrag
        self.datum = datum  # Format: "YYYY-MM-DD"

    def to_dict(self):
        return {
            "kategorie": self.kategorie,
            "betrag": self.betrag,
            "datum": self.datum
        }

    @staticmethod
    def from_dict(data: dict):
        return Ausgabe(
            data["kategorie"],
            float(data.get("betrag", 0)),
            data.get("datum", "")
        )
