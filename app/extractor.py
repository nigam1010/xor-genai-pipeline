from typing import Dict, Any
from datetime import datetime
from dateparser.search import search_dates
import spacy

# Load a small English model. If missing, run:
#   python -m spacy download en_core_web_sm
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    raise RuntimeError("spaCy model 'en_core_web_sm' not found. Run: python -m spacy download en_core_web_sm")

def _dedup(seq):
    seen, out = set(), []
    for x in seq:
        if x not in seen:
            out.append(x); seen.add(x)
    return out

def extract_entities(text: str) -> Dict[str, Any]:
    doc = nlp(text)

    # PERSON entities
    persons = [e.text.strip() for e in doc.ents if e.label_ == "PERSON"]
    persons = _dedup([p for p in persons if p])

    # Dates (absolute + relative)
    dates_out = []
    found = search_dates(
        text,
        settings={
            "PREFER_DAY_OF_MONTH": "first",
            "RELATIVE_BASE": datetime.now(),
            "RETURN_AS_TIMEZONE_AWARE": False
        }
    )
    if found:
        for raw, dt in found:
            try:
                dates_out.append(dt.date().isoformat())
            except Exception:
                dates_out.append(raw)
    dates_out = _dedup(dates_out)

    return {"persons": persons, "dates": dates_out}
