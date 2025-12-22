import json, os

# Alle JSON-Dateien im Projekt
DATEIEN = {
    "mitglieder": "mitglieder.json",
    "aktivitaeten": "aktivitaeten.json",
    "ideen": "ideen.json",
    "einkommen": "einkommen.json",
    "ausgaben": "ausgabe.json"   # ✅ NEU hinzugefügt
}

# Erstellt alle Dateien, falls sie nicht existieren
def init_dateien():
    for datei in DATEIEN.values():
        if not os.path.exists(datei):
            with open(datei, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

# Lädt Daten aus einer Datei
def lade(dateiname):
    try:
        with open(DATEIEN[dateiname], "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Speichert EINEN neuen Eintrag in eine Datei
def speichern(dateiname, eintrag):
    daten = lade(dateiname)
    daten.append(eintrag)
    with open(DATEIEN[dateiname], "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)

# Überschreibt eine Datei komplett mit neuen Daten
def aktualisieren(dateiname, daten):
    with open(DATEIEN[dateiname], "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)
