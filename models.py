class Mitglied:
    def __init__(self, name: str, kategorie: str, beitrag: float):
        self.name = name
        self.kategorie = kategorie
        self.beitrag = beitrag

class Aktivitaet:
    def __init__(self, name: str, ort: str, teilnehmer: list = None):
        self.name = name
        self.ort = ort
        self.teilnehmer = teilnehmer or []

class Idee:
    def __init__(self, titel: str, geber: str):
        self.titel = titel
        self.geber = geber
