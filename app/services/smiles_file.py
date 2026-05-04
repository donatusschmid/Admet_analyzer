"""Parse SMILES lists from uploaded text/CSV files."""

from __future__ import annotations

import io

import pandas as pd


def parse_smiles_upload(file_name: str, raw_bytes: bytes) -> list[tuple[str, str]]:
    """
    Return list of (compound_id, smiles).

    - .csv: column smiles/SMILES/smile (or first column); optional id/name/compound_id.
    - .txt / .smi / .batch: one SMILES per non-empty line; # starts a comment line.
    """
    text = raw_bytes.decode("utf-8", errors="replace")
    name = (file_name or "").lower()

    if name.endswith(".csv"):
        df = pd.read_csv(io.StringIO(text))
        if df.empty or len(df.columns) == 0:
            return []
        cols_lower = {str(c).strip().lower(): c for c in df.columns}
        smiles_col = None
        for key in ("smiles", "smile", "canonical_smiles", "smi"):
            if key in cols_lower:
                smiles_col = cols_lower[key]
                break
        if smiles_col is None:
            smiles_col = df.columns[0]

        id_col = None
        for key in ("id", "name", "compound_id", "compound", "mol", "identifier"):
            if key in cols_lower:
                id_col = cols_lower[key]
                break

        out: list[tuple[str, str]] = []
        for i, row in df.iterrows():
            smi = row.get(smiles_col)
            if smi is None or (isinstance(smi, float) and pd.isna(smi)):
                continue
            smi_s = str(smi).strip()
            if not smi_s:
                continue
            if id_col is not None:
                cid = row.get(id_col)
                if cid is not None and not (isinstance(cid, float) and pd.isna(cid)):
                    cid_s = str(cid).strip()
                else:
                    cid_s = f"Compound_{i + 1}"
            else:
                cid_s = f"Compound_{i + 1}"
            out.append((cid_s, smi_s))
        return out

    lines: list[tuple[str, str]] = []
    for i, line in enumerate(text.splitlines()):
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        lines.append((f"Compound_{i + 1}", s))
    return lines
