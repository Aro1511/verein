import streamlit as st

# Seite konfigurieren (nur EINMAL!)
st.set_page_config(page_title="Vereinsverwaltung", page_icon="👥", layout="wide")

# Sprache auf Deutsch setzen
st.markdown(
    """
    <script>
    document.documentElement.lang = 'de';
    </script>
    """,
    unsafe_allow_html=True
)

from models import Mitglied, Aktivitaet, Idee, Einkommen, Ausgabe
from logic import (
    berechne_beitrag,
    berechne_monatsausgaben,
    berechne_jahresausgaben,
    berechne_fixkosten,
    berechne_variable_ausgaben
)
from database import init_dateien, lade, speichern, aktualisieren
from datetime import datetime

# Logo
col1, col2 = st.columns([3, 1])
with col1:
    st.write("Vereinsverwaltung")
with col2:
    st.image("logo.png", use_container_width=True)

st.title("Vereinsverwaltung")

# CSS laden
def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

init_dateien()
load_css("style.css")

# Session-State Defaults
defaults = {
    "show_mitglied_form": False,
    "show_mitglieder_list": False,
    "show_aktiv_form": False,
    "show_aktiv_list": False,
    "show_idee_form": False,
    "show_ideen_list": False,
    "show_einkommen_form": False,
    "show_einkommen_list": False,
    "show_ausgabe_form": False,
    "show_ausgabe_list": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Tabs
tab_m, tab_a, tab_i, tab_e, tab_x = st.tabs([
    "Mitglieder",
    "Aktivitäten",
    "Ideen/Anmerkungen",
    "einnahme",
    "Ausgaben"   # ✅ NEU
])

# --------------------------------------------------------------------
# Mitglieder
# --------------------------------------------------------------------
with tab_m:
    st.subheader("Mitgliederverwaltung")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Mitglied hinzufügen"):
            st.session_state.show_mitglied_form = True
    with col_btn2:
        if st.button("📋 Mitgliederliste anzeigen"):
            st.session_state.show_mitglieder_list = True

    if st.session_state.show_mitglied_form:
        with st.form(key="form_mitglied_add", clear_on_submit=True):
            name = st.text_input("Name")
            kategorie = st.selectbox("Kategorie", ["Kind", "Familie", "Erwachsener"])
            beitrag = st.number_input("Individueller Beitrag (optional)", min_value=0.0, step=1.0)
            submitted = st.form_submit_button("Speichern Mitglied")
        if submitted:
            if not name.strip():
                st.error("Bitte einen Namen eingeben.")
            else:
                m = Mitglied(name.strip(), kategorie, beitrag)
                speichern("mitglieder", m.to_dict())
                st.success(f"{m.name} gespeichert.")
        if st.button("Formular schließen"):
            st.session_state.show_mitglied_form = False

    if st.session_state.show_mitglieder_list:
        mitglieder_roh = lade("mitglieder")
        mitglieder = [Mitglied.from_dict(m) for m in mitglieder_roh] if mitglieder_roh else []
        if not mitglieder:
            st.info("Keine Mitglieder vorhanden.")
        else:
            for idx, m in enumerate(mitglieder):
                beitrag_calc = berechne_beitrag(m)
                exp = st.expander(f"👤 {m.name} | {m.kategorie} | {beitrag_calc} €")
                with exp:
                    with st.form(key=f"form_edit_member_{idx}"):
                        neuer_name = st.text_input("Neuer Name", value=m.name)
                        neue_kategorie = st.selectbox(
                            "Neue Kategorie",
                            ["Kind", "Familie", "Erwachsener"],
                            index=["Kind", "Familie", "Erwachsener"].index(m.kategorie),
                        )
                        neuer_beitrag = st.number_input(
                            "Neuer Beitrag",
                            min_value=0.0,
                            step=1.0,
                            value=float(m.beitrag),
                        )
                        save_edit = st.form_submit_button("Änderungen speichern")
                    if save_edit:
                        m.name = neuer_name.strip() or m.name
                        m.kategorie = neue_kategorie
                        m.beitrag = neuer_beitrag
                        aktualisieren("mitglieder", [x.to_dict() for x in mitglieder])
                        st.success("Änderungen gespeichert.")

                    if st.button("Löschen", key=f"delete_member_{idx}"):
                        neue_liste = [x.to_dict() for x in mitglieder if x is not m]
                        aktualisieren("mitglieder", neue_liste)
                        st.warning(f"{m.name} gelöscht.")

        if st.button("Liste schließen", key="close_mitglieder"):
            st.session_state.show_mitglieder_list = False

# --------------------------------------------------------------------
# Aktivitäten
# --------------------------------------------------------------------
with tab_a:
    st.subheader("Aktivitätenverwaltung")

    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("➕ Aktivität hinzufügen"):
            st.session_state.show_aktiv_form = True
    with col_btn4:
        if st.button("📋 Aktivitätenliste anzeigen"):
            st.session_state.show_aktiv_list = True

    if st.session_state.show_aktiv_form:
        with st.form(key="form_aktiv_add", clear_on_submit=True):
            akt_name = st.text_input("Aktivitätsname")
            ort = st.text_input("Ort")
            teilnehmer_raw = st.text_area("Teilnehmer (Komma-getrennt)")
            submitted = st.form_submit_button("Speichern Aktivität")
        if submitted:
            if not akt_name.strip():
                st.error("Bitte einen Aktivitätsnamen eingeben.")
            else:
                teilnehmer_liste = [t.strip() for t in teilnehmer_raw.split(",") if t.strip()]
                akt = Aktivitaet(akt_name.strip(), ort.strip(), teilnehmer_liste)
                speichern("aktivitaeten", akt.to_dict())
                st.success(f"Aktivität '{akt.name}' gespeichert.")
        if st.button("Formular schließen"):
            st.session_state.show_aktiv_form = False

    if st.session_state.show_aktiv_list:
        aktivitaeten_roh = lade("aktivitaeten")
        aktivitaeten = [Aktivitaet.from_dict(a) for a in aktivitaeten_roh] if aktivitaeten_roh else []
        if not aktivitaeten:
            st.info("Keine Aktivitäten vorhanden.")
        else:
            for idx, a in enumerate(aktivitaeten):
                teilnehmer_str = ", ".join(a.teilnehmer)
                exp = st.expander(f"⚽ {a.name} | Ort: {a.ort} | Teilnehmer: {teilnehmer_str}")
                with exp:
                    with st.form(key=f"form_edit_aktiv_{idx}"):
                        neuer_name = st.text_input("Neuer Name", value=a.name)
                        neuer_ort = st.text_input("Neuer Ort", value=a.ort)
                        neue_teilnehmer_raw = st.text_area(
                            "Neue Teilnehmer (Komma)",
                            value=teilnehmer_str,
                        )
                        save_edit = st.form_submit_button("Änderungen speichern")
                    if save_edit:
                        a.name = neuer_name.strip() or a.name
                        a.ort = neuer_ort.strip()
                        a.teilnehmer = [t.strip() for t in neue_teilnehmer_raw.split(",") if t.strip()]
                        aktualisieren("aktivitaeten", [x.to_dict() for x in aktivitaeten])
                        st.success("Änderungen gespeichert.")

                    if st.button("Löschen", key=f"delete_aktiv_{idx}"):
                        neue_liste = [x.to_dict() for x in aktivitaeten if x is not a]
                        aktualisieren("aktivitaeten", neue_liste)
                        st.warning(f"Aktivität '{a.name}' gelöscht.")

        if st.button("Liste schließen", key="close_aktiv"):
            st.session_state.show_aktiv_list = False

# --------------------------------------------------------------------
# Ideen / Anmerkungen
# --------------------------------------------------------------------
with tab_i:
    st.subheader("Ideen und Anmerkungen")

    col_btn5, col_btn6 = st.columns(2)
    with col_btn5:
        if st.button("➕ Idee hinzufügen"):
            st.session_state.show_idee_form = True
    with col_btn6:
        if st.button("📋 Ideenliste anzeigen"):
            st.session_state.show_ideen_list = True

    if st.session_state.show_idee_form:
        with st.form(key="form_idee_add", clear_on_submit=True):
            idee_titel = st.text_input("Idee/Anmerkung")
            geber = st.text_input("Name des Ideengebers")
            submitted = st.form_submit_button("Speichern Idee")
        if submitted:
            if not idee_titel.strip():
                st.error("Bitte einen Titel einggeben.")
            else:
                idee = Idee(idee_titel.strip(), geber.strip())
                speichern("ideen", idee.to_dict())
                st.success("Idee gespeichert.")
        if st.button("Formular schließen"):
            st.session_state.show_idee_form = False

    if st.session_state.show_ideen_list:
        ideen_roh = lade("ideen")
        ideen = [Idee.from_dict(i) for i in ideen_roh] if ideen_roh else []
        if not ideen:
            st.info("Keine Ideen vorhanden.")
        else:
            for idx, i in enumerate(ideen):
                exp = st.expander(f"💡 {i.titel} | Geber: {i.geber}")
                with exp:
                    with st.form(key=f"form_edit_idee_{idx}"):
                        neuer_titel = st.text_input("Neuer Titel", value=i.titel)
                        neuer_geber = st.text_input("Neuer Geber", value=i.geber)
                        save_edit = st.form_submit_button("Änderungen speichern")
                    if save_edit:
                        i.titel = neuer_titel.strip() or i.titel
                        i.geber = neuer_geber.strip()
                        aktualisieren("ideen", [x.to_dict() for x in ideen])
                        st.success("Änderungen gespeichert.")

                    if st.button("Löschen", key=f"delete_idee_{idx}"):
                        neue_liste = [x.to_dict() for x in ideen if x is not i]
                        aktualisieren("ideen", neue_liste)
                        st.warning(f"Idee '{i.titel}' gelöscht.")

        if st.button("Liste schließen", key="close_ideen"):
            st.session_state.show_ideen_list = False

# --------------------------------------------------------------------
# Einkommen
# --------------------------------------------------------------------
with tab_e:
    st.subheader("einnahme")

    col_btn7, col_btn8 = st.columns(2)
    with col_btn7:
        if st.button("➕ Einnahme hinzufügen"):
            st.session_state.show_einkommen_form = True
    with col_btn8:
        if st.button("📋 Einnahmeliste anzeigen"):
            st.session_state.show_einkommen_list = True

    if st.session_state.show_einkommen_form:
        with st.form(key="form_einkommen_add", clear_on_submit=True):
            eink_name = st.text_input("Name")
            eink_art = st.selectbox(
                "Art des Einkommens",
                ["Spende", "Monatliche Gebühr", "Geschenk", "Sonstiges"],
            )
            eink_betrag = st.number_input("Betrag (€)", min_value=0.0, step=1.0)
            submitted_e = st.form_submit_button("Speichern Einkommen")
        if submitted_e:
            if not eink_name.strip():
                st.error("Bitte einen Namen eingeben.")
            else:
                eintrag = Einkommen(
                    name=eink_name.strip(),
                    art=eink_art,
                    betrag=eink_betrag,
                    datum=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
                speichern("einkommen", eintrag.to_dict())
                st.success("Einkommen gespeichert.")
        if st.button("Formular schließen"):
            st.session_state.show_einkommen_form = False

    if st.session_state.show_einkommen_list:
        daten_roh = lade("einkommen")
        daten = [Einkommen.from_dict(d) for d in daten_roh] if daten_roh else []
        if not daten:
            st.info("Keine Einkommen vorhanden.")
        else:
            st.markdown("#### 📆 Monatsübersicht")
            monate = [
                "Januar", "Februar", "März", "April", "Mai", "Juni",
                "Juli", "August", "September", "Oktober", "November", "Dezember"
            ]

            cols = st.columns(4)
            for i, monat in enumerate(monate, start=1):
                col = cols[(i - 1) % 4]
                with col:
                    if st.button(monat):
                        gefiltert = []
                        for d in daten:
                            dt_str = d.datum or ""
                            dt = None
                            for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
                                try:
                                    dt = datetime.strptime(dt_str, fmt)
                                    break
                                except ValueError:
                                    continue
                            if dt and dt.month == i:
                                gefiltert.append(d)

                        if gefiltert:
                            st.write(f"### Einnahmen im {monat}")
                            st.table([x.to_dict() for x in gefiltert])
                            gesamt = sum(float(x.betrag or 0) for x in gefiltert)
                            st.success(f"Gesamteinnahmen im {monat}: {gesamt:.2f} €")
                        else:
                            st.info(f"Keine Einträge für {monat}.")

        if st.button("Liste schließen", key="close_einkommen"):
            st.session_state.show_einkommen_list = False

# --------------------------------------------------------------------
# ✅ NEU: Ausgaben
# --------------------------------------------------------------------
with tab_x:
    st.subheader("Ausgabenverwaltung")

    col_btn9, col_btn10 = st.columns(2)
    with col_btn9:
        if st.button("➕ Ausgabe hinzufügen"):
            st.session_state.show_ausgabe_form = True
    with col_btn10:
        if st.button("📋 Ausgabenliste anzeigen"):
            st.session_state.show_ausgabe_list = True

    # -------------------------
    # Ausgabe hinzufügen
    # -------------------------
    if st.session_state.show_ausgabe_form:
        with st.form(key="form_ausgabe_add", clear_on_submit=True):
            kategorie = st.selectbox(
                "Kategorie",
                ["Miete", "Nebenkosten", "Wärme", "Wasser", "Einkäufe", "Aktivitäten", "Aufwandkosten"]
            )
            betrag = st.number_input("Betrag (€)", min_value=0.0, step=1.0)
            datum = st.date_input("Datum")
            submitted_x = st.form_submit_button("Speichern Ausgabe")

        if submitted_x:
            eintrag = Ausgabe(
                kategorie=kategorie,
                betrag=betrag,
                datum=datum.strftime("%Y-%m-%d")
            )
            speichern("ausgaben", eintrag.to_dict())
            st.success("Ausgabe gespeichert.")

        if st.button("Liste schließen", key="close_ausgaben"):
            st.session_state.show_ausgabe_form = False

    # -------------------------
    # Ausgabenliste
    # -------------------------
    if st.session_state.show_ausgabe_list:
        ausgaben_roh = lade("ausgaben")
        ausgaben = [Ausgabe.from_dict(a) for a in ausgaben_roh] if ausgaben_roh else []

        if not ausgaben:
            st.info("Keine Ausgaben vorhanden.")
        else:
            st.write("### Alle Ausgaben")
            st.table([a.to_dict() for a in ausgaben])

            # Monatsberechnung
            st.write("### 📆 Monatsausgaben berechnen")
            monat = st.number_input("Monat (1-12)", min_value=1, max_value=12, step=1)
            jahr = st.number_input("Jahr", min_value=2000, max_value=2100, step=1)
            if st.button("Berechnen Monatsausgaben"):
                gesamt = berechne_monatsausgaben(ausgaben, monat, jahr)
                st.success(f"Gesamtausgaben im {monat}/{jahr}: {gesamt:.2f} €")

            # Jahresberechnung
            st.write("### 📅 Jahresausgaben berechnen")
            jahr2 = st.number_input("Jahr auswählen", min_value=2000, max_value=2100, step=1, key="jahr2")
            if st.button("Berechnen Jahresausgaben"):
                gesamt = berechne_jahresausgaben(ausgaben, jahr2)
                st.success(f"Gesamtausgaben im Jahr {jahr2}: {gesamt:.2f} €")

            # Fixkosten
            st.write("### 🏠 Fixkosten gesamt")
            fix = berechne_fixkosten(ausgaben)
            st.info(f"Fixkosten gesamt: {fix:.2f} €")

            # Variable Kosten
            st.write("### 🛒 Variable Ausgaben gesamt")
            var = berechne_variable_ausgaben(ausgaben)
            st.info(f"Variable Ausgaben gesamt: {var:.2f} €")

        if st.button("Liste schließen"):
            st.session_state.show_ausgabe_list = False
