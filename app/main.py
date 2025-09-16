from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from .extractor import extract_entities
from .db import init_db, insert_record, list_records

app = FastAPI(title="Xorstack Gen-AI Entities API", version="1.0.0")

class ExtractRequest(BaseModel):
    text: str
    source: Optional[str] = "api:text"

@app.on_event("startup")
def startup_event():
    init_db()

@app.post("/extract")
def extract(req: ExtractRequest):
    if not req.text or not req.text.strip():
        raise HTTPException(status_code=400, detail="Text is empty.")
    ents = extract_entities(req.text)
    created_at = datetime.utcnow().isoformat()

    
    src: str = req.source or "api:text"

    rec_id = insert_record(src, ents["persons"], ents["dates"], req.text, created_at)
    return {
        "id": rec_id,
        "source": src,
        "persons": ents["persons"],
        "dates": ents["dates"],
        "created_at": created_at,
    }

@app.post("/extract-file")
async def extract_file(file: UploadFile = File(...)):
    # UploadFile.filename can be None; guard before .lower()
    fname = file.filename or ""
    if not fname.lower().endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are supported.")

    content = (await file.read()).decode("utf-8", errors="ignore")
    ents = extract_entities(content)
    created_at = datetime.utcnow().isoformat()

    rec_id = insert_record(fname, ents["persons"], ents["dates"], content, created_at)
    return {
        "id": rec_id,
        "source": fname,
        "persons": ents["persons"],
        "dates": ents["dates"],
        "created_at": created_at,
    }

@app.get("/records")
def records(limit: int = 50, offset: int = 0):
    return list_records(limit=limit, offset=offset)
