"""VoterGuard backend MVP: image analysis, duplicate-photo screening, review, audit."""
import json
from contextlib import asynccontextmanager
from typing import Literal, Optional

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from .config import get_settings
from .db import audit, get_conn, init_db, now
from .image_analysis import LIMITATIONS, ImageRejected, analyze_image_bytes, phash_distance

REVIEW_NOTICE = (
    "Possible match for human review only. Visual similarity is not identity proof "
    "and is not a fraud determination."
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="VoterGuard API (MVP prototype)",
    version="0.1.0",
    description="Review-support prototype. Uses synthetic data only. Not connected to INEC.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings()["cors_origins"],
    allow_origin_regex=r"https://voterguard[a-z0-9\-]*\.vercel\.app",
    allow_methods=["*"],
    allow_headers=["*"],
)


async def read_upload(file: UploadFile) -> bytes:
    limit = get_settings()["max_upload_bytes"]
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise HTTPException(413, f"File too large. Limit is {limit / 1024 / 1024:g} MB.")
    return data


def run_analysis(data: bytes) -> dict:
    try:
        return analyze_image_bytes(data)
    except ImageRejected as e:
        raise HTTPException(400, str(e))


def save_analysis(conn, filename: Optional[str], r: dict) -> int:
    cur = conn.execute(
        "INSERT INTO analyses (created_at, filename, size_bytes, sha256, image_format, width, height, "
        "phash, warning_count, metrics_json, findings_json) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        (
            now(), filename, r["size_bytes"], r["sha256"], r["image_format"], r["width"], r["height"],
            r["phash"], r["warning_count"], json.dumps(r["metrics"]), json.dumps(r["findings"]),
        ),
    )
    audit(conn, "image_analyzed", "analysis", cur.lastrowid, {"sha256": r["sha256"]})
    return cur.lastrowid


def analysis_row(row) -> dict:
    return {
        "id": row["id"],
        "created_at": row["created_at"],
        "filename": row["filename"],
        "size_bytes": row["size_bytes"],
        "sha256": row["sha256"],
        "image_format": row["image_format"],
        "width": row["width"],
        "height": row["height"],
        "phash": row["phash"],
        "warning_count": row["warning_count"],
        "metrics": json.loads(row["metrics_json"]),
        "findings": json.loads(row["findings_json"]),
        "limitations": LIMITATIONS,
    }


@app.get("/health")
def health():
    with get_conn() as conn:
        conn.execute("SELECT 1")
    return {"status": "ok", "database": "ok", "version": app.version}


# ---------- Workflow A: image intake and basic analysis ----------
@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    data = await read_upload(file)
    result = run_analysis(data)
    with get_conn() as conn:
        new_id = save_analysis(conn, file.filename, result)
        row = conn.execute("SELECT * FROM analyses WHERE id=?", (new_id,)).fetchone()
    return analysis_row(row)


@app.get("/analyses")
def list_analyses(limit: int = Query(50, ge=1, le=200)):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [analysis_row(r) for r in rows]


@app.get("/analyses/{analysis_id}")
def get_analysis(analysis_id: int):
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM analyses WHERE id=?", (analysis_id,)).fetchone()
    if not row:
        raise HTTPException(404, "Analysis not found.")
    return analysis_row(row)


# ---------- Workflow B: duplicate-photo screening ----------
@app.post("/collection")
async def add_to_collection(label: str = Form(..., min_length=1, max_length=120), file: UploadFile = File(...)):
    """Add a SYNTHETIC reference image to the local test collection."""
    data = await read_upload(file)
    r = run_analysis(data)
    with get_conn() as conn:
        cur = conn.execute(
            "INSERT INTO collection_images (created_at, label, filename, sha256, phash, width, height) "
            "VALUES (?,?,?,?,?,?,?)",
            (now(), label, file.filename, r["sha256"], r["phash"], r["width"], r["height"]),
        )
        audit(conn, "collection_image_added", "collection_image", cur.lastrowid, {"label": label})
    return {"id": cur.lastrowid, "label": label, "sha256": r["sha256"], "phash": r["phash"]}


@app.get("/collection")
def list_collection():
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM collection_images ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


@app.post("/screen")
async def screen(file: UploadFile = File(...), max_distance: int = Query(10, ge=0, le=20)):
    """Analyze an image and compare it with the local collection (exact hash + pHash)."""
    data = await read_upload(file)
    r = run_analysis(data)
    candidates = []
    with get_conn() as conn:
        analysis_id = save_analysis(conn, file.filename, r)
        for ref in conn.execute("SELECT * FROM collection_images").fetchall():
            exact = ref["sha256"] == r["sha256"]
            dist = phash_distance(r["phash"], ref["phash"])
            if exact or dist <= max_distance:
                sim = round(1 - dist / 64, 4)
                cur = conn.execute(
                    "INSERT INTO match_candidates (created_at, analysis_id, collection_id, exact_match, "
                    "hamming_distance, similarity) VALUES (?,?,?,?,?,?)",
                    (now(), analysis_id, ref["id"], int(exact), dist, sim),
                )
                candidates.append({
                    "match_id": cur.lastrowid,
                    "collection_id": ref["id"],
                    "label": ref["label"],
                    "exact_match": exact,
                    "hamming_distance": dist,
                    "similarity": sim,
                    "disposition": "pending",
                    "notice": REVIEW_NOTICE,
                })
        audit(conn, "screening_run", "analysis", analysis_id, {"candidates": len(candidates)})
        row = conn.execute("SELECT * FROM analyses WHERE id=?", (analysis_id,)).fetchone()
    candidates.sort(key=lambda c: c["hamming_distance"])
    return {
        "analysis": analysis_row(row),
        "max_distance": max_distance,
        "candidates": candidates,
    }


class Review(BaseModel):
    disposition: Literal["confirmed_duplicate", "not_duplicate", "needs_more_info"]
    reviewer: str = Field(..., min_length=1, max_length=80)
    note: Optional[str] = Field(None, max_length=500)


@app.get("/matches")
def list_matches(disposition: Optional[str] = None, limit: int = Query(100, ge=1, le=500)):
    sql = (
        "SELECT m.*, c.label FROM match_candidates m JOIN collection_images c ON c.id = m.collection_id"
    )
    args: list = []
    if disposition:
        sql += " WHERE m.disposition = ?"
        args.append(disposition)
    sql += " ORDER BY m.id DESC LIMIT ?"
    args.append(limit)
    with get_conn() as conn:
        rows = conn.execute(sql, args).fetchall()
    return [dict(r) for r in rows]


@app.patch("/matches/{match_id}/review")
def review_match(match_id: int, body: Review):
    with get_conn() as conn:
        if not conn.execute("SELECT 1 FROM match_candidates WHERE id=?", (match_id,)).fetchone():
            raise HTTPException(404, "Match candidate not found.")
        conn.execute(
            "UPDATE match_candidates SET disposition=?, reviewer=?, note=?, reviewed_at=? WHERE id=?",
            (body.disposition, body.reviewer, body.note, now(), match_id),
        )
        audit(conn, "match_reviewed", "match_candidate", match_id,
              {"disposition": body.disposition}, actor=body.reviewer)
        row = conn.execute("SELECT * FROM match_candidates WHERE id=?", (match_id,)).fetchone()
    return dict(row)


# ---------- Dashboard data and audit ----------
@app.get("/stats")
def stats():
    with get_conn() as conn:
        one = lambda q: conn.execute(q).fetchone()[0]
        by_disp = {
            r["disposition"]: r["n"]
            for r in conn.execute("SELECT disposition, COUNT(*) n FROM match_candidates GROUP BY disposition")
        }
        return {
            "analyses_total": one("SELECT COUNT(*) FROM analyses"),
            "analyses_with_warnings": one("SELECT COUNT(*) FROM analyses WHERE warning_count > 0"),
            "collection_images": one("SELECT COUNT(*) FROM collection_images"),
            "match_candidates_total": one("SELECT COUNT(*) FROM match_candidates"),
            "match_candidates_by_disposition": by_disp,
        }


@app.get("/audit")
def list_audit(limit: int = Query(50, ge=1, le=500)):
    with get_conn() as conn:
        rows = conn.execute("SELECT * FROM audit_events ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [dict(r) for r in rows]
