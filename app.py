import streamlit as st
from models import Mitglied, Aktivitaet, Idee
from logic import berechne_beitrag
from database import init_dateien, lade, speichern, aktualisieren

st.set_page_config(page_title="Vereinsverwaltung", page_icon="👥", layout="wide")
st.title("Vereinsverwaltung")

# Logo rechts oben mit neuer Syntax
col1, col2 = st.columns([3,1])

with col1:
    st.write("")  # leer

with col2:
    st.image("logo.png", use_container_width=True)

# Optional: CSS laden, wenn vorhanden
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
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Tabs
tab_m, tab_a, tab_i = st.tabs(["Mitglieder", "Aktivitäten", "Ideen/Anmerkungen"])

# --------------------------------------------------------------------
# Mitglieder
# --------------------------------------------------------------------
with tab_m:
    st.subheader("Mitgliederverwaltung")

    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("➕ Mitglied hinzufügen", key="btn_add_member"):
            st.session_state.show_mitglied_form = True
    with col_btn2:
        if st.button("📋 Mitgliederliste anzeigen", key="btn_list_member"):
            st.session_state.show_mitglieder_list = True

    # Formular zum Hinzufügen
    if st.session_state.show_mitglied_form:
        with st.form(key="form_mitglied_add", clear_on_submit=True):
            name = st.text_input("Name", key="member_name")
            kategorie = st.selectbox("Kategorie", ["Kind", "Familie", "Erwachsener"], key="member_cat")
            beitrag = st.number_input("Individueller Beitrag (optional)", min_value=0.0, step=1.0, key="member_fee")
            submitted = st.form_submit_button("Speichern Mitglied")
        if submitted:
            if not name.strip():
                st.error("Bitte einen Namen eingeben.")
            else:
                m = Mitglied(name.strip(), kategorie, beitrag)
                speichern("mitglieder", {"name": m.name, "kategorie": m.kategorie, "beitrag": m.beitrag})
                st.success(f"{m.name} gespeichert.")
                # Formular geschlossen halten oder wieder öffnen? Hier lassen wir es offen.
        if st.button("Formular schließen", key="close_member_form"):
            st.session_state.show_mitglied_form = False

    # Mitgliederliste mit Bearbeiten/Löschen
    if st.session_state.show_mitglieder_list:
        mitglieder = lade("mitglieder")
        if not mitglieder:
            st.info("Keine Mitglieder vorhanden.")
        else:
            for idx, m in enumerate(mitglieder):
                pseudo = Mitglied(m["name"], m["kategorie"], float(m.get("beitrag", 0)))
                beitrag_calc = berechne_beitrag(pseudo)

                exp = st.expander(f"👤 {m['name']} | {m['kategorie']} | {beitrag_calc} €", expanded=False)
                with exp:
                    # Bearbeiten-Form
                    with st.form(key=f"form_edit_member_{idx}"):
                        neuer_name = st.text_input("Neuer Name", value=m["name"], key=f"edit_member_name_{idx}")
                        neue_kategorie = st.selectbox(
                            "Neue Kategorie",
                            ["Kind", "Familie", "Erwachsener"],
                            index=["Kind", "Familie", "Erwachsener"].index(m["kategorie"]),
                            key=f"edit_member_cat_{idx}",
                        )
                        neuer_beitrag = st.number_input(
                            "Neuer Beitrag",
                            min_value=0.0,
                            step=1.0,
                            value=float(m.get("beitrag", 0)),
                            key=f"edit_member_fee_{idx}",
                        )
                        save_edit = st.form_submit_button("Änderungen speichern")
                    if save_edit:
                        m["name"] = neuer_name.strip() or m["name"]
                        m["kategorie"] = neue_kategorie
                        m["beitrag"] = neuer_beitrag
                        aktualisieren("mitglieder", mitglieder)
                        st.success("Änderungen gespeichert.")

                    # Löschen-Button
                    if st.button("Löschen", key=f"delete_member_{idx}"):
                        neue_liste = [x for x in mitglieder if not (x["name"] == m["name"] and x["kategorie"] == m["kategorie"] and x.get("beitrag", 0) == m.get("beitrag", 0))]
                        aktualisieren("mitglieder", neue_liste)
                        st.warning(f"{m['name']} gelöscht.")

        if st.button("Liste schließen", key="close_member_list"):
            st.session_state.show_mitglieder_list = False

# --------------------------------------------------------------------
# Aktivitäten
# --------------------------------------------------------------------
with tab_a:
    st.subheader("Aktivitätenverwaltung")

    col_btn3, col_btn4 = st.columns(2)
    with col_btn3:
        if st.button("➕ Aktivität hinzufügen", key="btn_add_aktiv"):
            st.session_state.show_aktiv_form = True
    with col_btn4:
        if st.button("📋 Aktivitätenliste anzeigen", key="btn_list_aktiv"):
            st.session_state.show_aktiv_list = True

    # Formular Aktivität hinzufügen
    if st.session_state.show_aktiv_form:
        with st.form(key="form_aktiv_add", clear_on_submit=True):
            akt_name = st.text_input("Aktivitätsname", key="aktiv_name")
            ort = st.text_input("Ort", key="aktiv_ort")
            teilnehmer_raw = st.text_area("Teilnehmer (Komma-getrennt)", key="aktiv_participants")
            submitted = st.form_submit_button("Speichern Aktivität")
        if submitted:
            if not akt_name.strip():
                st.error("Bitte einen Aktivitätsnamen eingeben.")
            else:
                akt = {
                    "name": akt_name.strip(),
                    "ort": ort.strip(),
                    "teilnehmer": [t.strip() for t in teilnehmer_raw.split(",") if t.strip()],
                }
                speichern("aktivitaeten", akt)
                st.success(f"Aktivität '{akt_name}' gespeichert.")
        if st.button("Formular schließen", key="close_aktiv_form"):
            st.session_state.show_aktiv_form = False

    # Liste Aktivitäten mit Bearbeiten/Löschen
    if st.session_state.show_aktiv_list:
        aktivitaeten = lade("aktivitaeten")
        if not aktivitaeten:
            st.info("Keine Aktivitäten vorhanden.")
        else:
            for idx, a in enumerate(aktivitaeten):
                teilnehmer_str = ", ".join(a.get("teilnehmer", []))
                exp = st.expander(f"⚽ {a['name']} | Ort: {a['ort']} | Teilnehmer: {teilnehmer_str}", expanded=False)
                with exp:
                    with st.form(key=f"form_edit_aktiv_{idx}"):
                        neuer_name = st.text_input("Neuer Name", value=a["name"], key=f"edit_aktiv_name_{idx}")
                        neuer_ort = st.text_input("Neuer Ort", value=a["ort"], key=f"edit_aktiv_ort_{idx}")
                        neue_teilnehmer_raw = st.text_area("Neue Teilnehmer (Komma)", value=teilnehmer_str, key=f"edit_aktiv_participants_{idx}")
                        save_edit = st.form_submit_button("Änderungen speichern")
                    if save_edit:
                        a["name"] = neuer_name.strip() or a["name"]
                        a["ort"] = neuer_ort.strip()
                        a["teilnehmer"] = [t.strip() for t in neue_teilnehmer_raw.split(",") if t.strip()]
                        aktualisieren("aktivitaeten", aktivitaeten)
                        st.success("Änderungen gespeichert.")

                    if st.button("Löschen", key=f"delete_aktiv_{idx}"):
                        neue_liste = [x for x in aktivitaeten if not (x["name"] == a["name"] and x["ort"] == a["ort"])]
                        aktualisieren("aktivitaeten", neue_liste)
                        st.warning(f"Aktivität '{a['name']}' gelöscht.")

        if st.button("Liste schließen", key="close_aktiv_list"):
            st.session_state.show_aktiv_list = False

# --------------------------------------------------------------------
# Ideen / Anmerkungen
# --------------------------------------------------------------------
with tab_i:
    st.subheader("Ideen und Anmerkungen")

    col_btn5, col_btn6 = st.columns(2)
    with col_btn5:
        if st.button("➕ Idee hinzufügen", key="btn_add_idee"):
            st.session_state.show_idee_form = True
    with col_btn6:
        if st.button("📋 Ideenliste anzeigen", key="btn_list_ideen"):
            st.session_state.show_ideen_list = True

    # Formular Idee hinzufügen
    if st.session_state.show_idee_form:
        with st.form(key="form_idee_add", clear_on_submit=True):
            idee_titel = st.text_input("Idee/Anmerkung", key="idee_title")
            geber = st.text_input("Name des Ideengebers", key="idee_geber")
            submitted = st.form_submit_button("Speichern Idee")
        if submitted:
            if not idee_titel.strip():
                st.error("Bitte einen Titel eingeben.")
            else:
                idee = {"titel": idee_titel.strip(), "geber": geber.strip()}
                speichern("ideen", idee)
                st.success("Idee gespeichert.")
        if st.button("Formular schließen", key="close_idee_form"):
            st.session_state.show_idee_form = False

    # Liste Ideen mit Bearbeiten/Löschen
    if st.session_state.show_ideen_list:
        ideen = lade("ideen")
        if not ideen:
            st.info("Keine Ideen vorhanden.")
        else:
            for idx, i in enumerate(ideen):
                exp = st.expander(f"💡 {i['titel']} | Geber: {i['geber']}", expanded=False)
                with exp:
                    with st.form(key=f"form_edit_idee_{idx}"):
                        neuer_titel = st.text_input("Neuer Titel", value=i["titel"], key=f"edit_idee_title_{idx}")
                        neuer_geber = st.text_input("Neuer Geber", value=i["geber"], key=f"edit_idee_geber_{idx}")
                        save_edit = st.form_submit_button("Änderungen speichern")
                    if save_edit:
                        i["titel"] = neuer_titel.strip() or i["titel"]
                        i["geber"] = neuer_geber.strip()
                        aktualisieren("ideen", ideen)
                        st.success("Änderungen gespeichert.")

                    if st.button("Löschen", key=f"delete_idee_{idx}"):
                        neue_liste = [x for x in ideen if not (x["titel"] == i["titel"] and x["geber"] == i["geber"])]
                        aktualisieren("ideen", neue_liste)
                        st.warning(f"Idee '{i['titel']}' gelöscht.")

        if st.button("Liste schließen", key="close_ideen_list"):
            st.session_state.show_ideen_list = False
