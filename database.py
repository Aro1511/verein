import json, os

DATEIEN = {
    "mitglieder": "mitglieder.json",
    "aktivitaeten": "aktivitaeten.json",
    "ideen": "ideen.json",
    "einkommen": "einkommen.json"
}

def init_dateien():
    for datei in DATEIEN.values():
        if not os.path.exists(datei):
            with open(datei, "w", encoding="utf-8") as f:
                json.dump([], f, indent=4, ensure_ascii=False)

def lade(dateiname):
    try:
        with open(DATEIEN[dateiname], "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def speichern(dateiname, eintrag):
    daten = lade(dateiname)
    daten.append(eintrag)
    with open(DATEIEN[dateiname], "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)

def aktualisieren(dateiname, daten):
    with open(DATEIEN[dateiname], "w", encoding="utf-8") as f:
        json.dump(daten, f, indent=4, ensure_ascii=False)
