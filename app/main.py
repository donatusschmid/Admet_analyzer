import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if str(_root) not in sys.path:
    sys.path.insert(0, str(_root))

import pandas as pd
import streamlit as st

from app.services.aggregator import run_pipeline
from app.services.excel_export import (
    build_batch_excel,
    default_batch_filename,
    pipeline_result_to_row,
)
from app.services.smiles_file import parse_smiles_upload

BRIGIMADLIN_SMILES = (
    "CC1=C(C=CC2=C3C[C@H]4[C@@H](N3N=C12)[C@@H]([C@]5(N4CC6CC6)C7=C(C=C(C=C7)Cl)NC5=O)"
    "C8=C(C(=CC=C8)Cl)F)C(=O)O"
)

st.set_page_config(page_title="ADMET Analyzer", layout="wide")

st.markdown(
    """
    <style>
    /* Hellgrau gefüllt, sichtbarer Rahmen wie zuvor (feste Farben, zuverlässig) */
    .stApp .stButton > button,
    .stApp div[data-testid="stDownloadButton"] button {
        background-color: #e6e6e6 !important;
        background-image: none !important;
        color: #1a1a1a !important;
        border: 1px solid #8f8f8f !important;
        border-radius: var(--st-button-radius, var(--st-base-radius, 0.375rem)) !important;
        box-shadow: none !important;
    }
    .stApp .stButton > button:hover,
    .stApp div[data-testid="stDownloadButton"] button:hover {
        background-color: #d8d8d8 !important;
        border-color: #7a7a7a !important;
        color: #000000 !important;
        filter: none !important;
    }
    .stApp .stButton > button:focus-visible,
    .stApp div[data-testid="stDownloadButton"] button:focus-visible {
        box-shadow: 0 0 0 2px #7a7a7a !important;
        outline: none !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧪 ADMET Multi-Tool Analyzer")
st.caption(
    "Vergleich von **SwissADME**, **ADMETlab 3.0** und **pkCSM** (jeweils in silico, keine Experimente). "
    "Löslichkeits-Modelle nutzen unterschiedliche Skalen — Werte sind roh wie von der jeweiligen Seite übernommen."
)


def _ui_runtime_hints(tab_kurz: str) -> None:
    """Klare Erwartungen: Dauer, wo gerechnet wird, Mobil/Sleep."""
    with st.expander(
        f"Hinweise: Laufzeit, Mobilgerät, wo die Berechnung läuft ({tab_kurz})",
        expanded=False,
    ):
        st.markdown(
            """
1. **Wo wird gerechnet?** Auf dem Rechner oder Server, auf dem diese App mit `streamlit run` läuft — **nicht** im Handy-Browser. Der Browser zeigt nur die Oberfläche.

2. **Dauer:** Pro Molekül laufen **drei** Web-Tools nacheinander (SwissADME → ADMETlab → pkCSM). Das kann **mehrere Minuten** dauern; der Fortschrittsbalken zeigt den **Zwischenstand** (Schritte 1/5 … 5/5).

3. **Smartphone / Tablet:** Geht das Gerät in den **Ruhezustand** oder wird der Tab stark gedrosselt, kann die Verbindung zur App abbrechen — dann fehlen ggf. Ergebnisse oder es erscheint ein Verbindungsfehler. Für zuverlässige Läufe: **Bildschirm wach halten** (z. B. eingesteckt) oder einen **Desktop-Browser** nutzen.

4. **Laptop als Server:** Wenn hier Streamlit läuft: **Energiesparmodus, Deckel zu** oder Sleep können den Prozess stoppen — während eines Laufs den Rechner **wach** lassen.
            """.strip()
        )


tab_single, tab_batch = st.tabs(["Einzelmolekül", "Batch (Datei)"])


def _show_single_result(results: dict) -> None:
    if results.get("errors"):
        st.warning("Teilweise fehlgeschlagen — siehe Details unten.")
        for tool, msg in results["errors"].items():
            st.error(f"**{tool}:** {msg}")

    st.subheader("📊 Vergleich (Kernparameter)")
    df = pd.DataFrame(results["normalized"])
    st.dataframe(df.T, width="stretch")

    with st.expander("Detail-Parsing pro Tool"):
        st.json(results.get("parsed", {}))

    st.subheader("🔍 Rohdaten (HTML-Metadaten)")
    raw_compact = {}
    for name, payload in results.get("raw", {}).items():
        if not isinstance(payload, dict):
            raw_compact[name] = payload
            continue
        raw_compact[name] = {k: v for k, v in payload.items() if k != "html"}
        raw_compact[name]["html_chars"] = len(payload.get("html") or "")
    st.json(raw_compact)

    with st.expander("Vollständiges Roh-HTML (sehr groß)"):
        for name, payload in results.get("raw", {}).items():
            html = (payload or {}).get("html")
            if html:
                st.markdown(f"**{name}** — {len(html)} Zeichen")
                st.download_button(
                    f"HTML herunterladen ({name})",
                    html,
                    file_name=f"{name}_result.html",
                    mime="text/html",
                    key=f"dl_html_single_{name}",
                    type="secondary",
                )


with tab_single:
    _ui_runtime_hints("Einzelmolekül")

    if "smiles_input" not in st.session_state:
        st.session_state.smiles_input = ""

    if st.button("Beispiel: Brigimadlin einsetzen", key="btn_brigi"):
        st.session_state.smiles_input = BRIGIMADLIN_SMILES

    st.text_area(
        "SMILES eingeben",
        placeholder="SMILES hier einfügen …",
        height=120,
        key="smiles_input",
    )

    smiles = st.session_state.smiles_input

    if st.button("Alle drei Tools ausführen", type="secondary", key="btn_single"):
        if not (smiles or "").strip():
            st.warning("Bitte SMILES eingeben oder Beispiel laden.")
        else:
            progress = st.progress(0.0, text="Start …")
            try:

                def _on_progress(frac: float, msg: str) -> None:
                    progress.progress(frac, text=msg)

                results = run_pipeline(smiles, on_progress=_on_progress)
            except Exception as e:
                progress.progress(0.0, text="Abgebrochen / Fehler.")
                st.error(f"Unerwarteter Fehler: {e}")
                st.stop()
            st.session_state["last_single_results"] = results

    if st.session_state.get("last_single_results"):
        _show_single_result(st.session_state["last_single_results"])

with tab_batch:
    _ui_runtime_hints("Batch")

    st.markdown(
        "**Batch:** CSV (Spalte `smiles` / `SMILES` oder erste Spalte), optional `id` / `name` / `compound_id` — "
        "oder **TXT/SMI/.batch** (eine SMILES pro Zeile, `#` Kommentar)."
    )
    st.warning(
        "Jede Zeile löst nacheinander alle drei Web-Tools aus — rechnen Sie mit **mehreren Minuten pro Verbindung**. "
        "Der Fortschrittsbalken zeigt **Struktur x/y** und den **Zwischenstand** innerhalb jedes Laufs (1/5 … 5/5)."
    )

    up = st.file_uploader(
        "SMILES-Datei",
        type=["csv", "txt", "smi", "batch"],
        help="UTF-8. Bei CSV: SMILES-Spalte oder erste Spalte. .batch wie TXT (eine SMILES pro Zeile).",
    )
    max_n = st.number_input(
        "Max. Anzahl Strukturen (Abschneiden)",
        min_value=1,
        max_value=200,
        value=20,
        help="Schützt vor extrem langen Läufen.",
    )

    if st.button("Batch starten", type="secondary", key="btn_batch") and up is not None:
        raw = up.getvalue()
        pairs = parse_smiles_upload(up.name, raw)
        if not pairs:
            st.error("Keine SMILES in der Datei gefunden.")
            st.stop()
        if len(pairs) > max_n:
            st.info(f"Nur die ersten **{max_n}** von {len(pairs)} Einträgen werden verarbeitet.")
            pairs = pairs[:max_n]

        rows = []
        n_pairs = len(pairs)
        progress = st.progress(0.0, text="Start …")
        for i, (cid, smi) in enumerate(pairs):
            base = i / n_pairs
            span = 1.0 / n_pairs

            def _on_batch_progress(
                frac: float,
                msg: str,
                _base=base,
                _span=span,
                _idx=i,
                _label=cid,
                _total=n_pairs,
            ) -> None:
                progress.progress(
                    min(1.0, _base + frac * _span),
                    text=f"Struktur {_idx + 1}/{_total} ({_label}) — {msg}",
                )

            _on_batch_progress(0.0, "Start …")
            try:
                res = run_pipeline(smi, on_progress=_on_batch_progress)
            except Exception as e:
                res = {
                    "errors": {
                        "swissadme": str(e),
                        "admetlab": str(e),
                        "pkcsm": str(e),
                    },
                    "normalized": {},
                    "parsed": {},
                    "raw": {},
                }
            rows.append(pipeline_result_to_row(cid, smi, res))
        progress.progress(1.0, text="Fertig.")

        batch_df = pd.DataFrame(rows)
        st.session_state["batch_df"] = batch_df
        st.session_state["batch_xlsx"] = build_batch_excel(batch_df)
        st.session_state["batch_fname"] = default_batch_filename()

    if st.session_state.get("batch_df") is not None:
        st.subheader("Batch-Vorschau")
        st.dataframe(st.session_state["batch_df"], width="stretch", height=320)
        st.download_button(
            "Excel herunterladen (.xlsx)",
            data=st.session_state["batch_xlsx"],
            file_name=st.session_state.get("batch_fname") or default_batch_filename(),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="dl_batch_xlsx",
        )
