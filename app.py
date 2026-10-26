from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import json
import re
from pathlib import Path
from datetime import datetime, timezone
import webbrowser
from threading import Timer

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "defence_factory.db"

app = Flask(__name__, static_folder=None)
app.config["MAX_CONTENT_LENGTH"] = 1 * 1024 * 1024

RELEVANCE_GROUPS = {
    "facility_context": [
        "factory", "industrial", "manufacturing", "plant", "facility",
        "workshop", "warehouse", "production", "assembly"
    ],
    "drawing_context": [
        "blueprint", "floor plan", "floorplan", "site plan", "layout",
        "plan view", "architectural", "drawing", "legend", "scale",
        "dimension", "north arrow", "sqm", "sq m", "m²", "room schedule"
    ],
    "spatial_features": [
        "room", "office", "entrance", "exit", "corridor", "door", "wall",
        "stair", "ramp", "loading bay", "loading dock", "parking", "road",
        "pedestrian", "vehicle", "storage", "warehouse"
    ],
    "infrastructure": [
        "fire exit", "fire extinguisher", "hydrant", "sprinkler",
        "ventilation", "exhaust", "electrical", "transformer", "generator",
        "drainage", "wastewater", "effluent", "toilet", "washroom",
        "first aid", "assembly point", "water tank", "pump room",
        "emergency exit"
    ],
}

DOCUMENT_TYPES = {
    "resume": ["resume", "curriculum vitae", "education", "skills", "experience"],
    "invoice": ["invoice", "gst", "tax invoice", "subtotal", "bill to", "total"],
    "certificate": ["certificate", "awarded", "issued", "completion"],
    "book": ["chapter", "isbn", "publisher", "contents"],
}


def connect_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def ensure_db():
    if not DB_PATH.exists():
        raise RuntimeError(
            f"SQLite database file is missing: {DB_PATH}. "
            "Place defence_factory.db in the same folder as app.py."
        )


def matches(term, text):
    """Match whole words and phrases without matching partial words."""
    term = str(term).casefold().strip()
    text = str(text).casefold()
    if not term:
        return False
    if " " in term or "²" in term:
        return term in text
    return re.search(
        r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])",
        text
    ) is not None


def classify_document(text, notes=""):
    combined = (text + "\n" + notes).casefold()
    groups = {
        name: [term for term in terms if matches(term, combined)]
        for name, terms in RELEVANCE_GROUPS.items()
    }
    active_groups = [name for name, terms in groups.items() if terms]
    matched_terms = sorted({
        term for terms in groups.values() for term in terms
    })

    valid = (
        (
            bool(groups["drawing_context"])
            and (
                bool(groups["facility_context"])
                or bool(groups["spatial_features"])
                or bool(groups["infrastructure"])
            )
        )
        or (
            bool(groups["facility_context"])
            and len(groups["spatial_features"] + groups["infrastructure"]) >= 2
        )
        or (
            len(matched_terms) >= 6 and bool(groups["spatial_features"])
        )
    )

    if not text.strip() and not notes.strip():
        valid = False
        reason = (
            "No readable text was extracted. This may be a scanned or "
            "image-only document; try a clearer PDF/image or add a short "
            "description in the notes."
        )
    elif len(text.strip()) < 35 and not notes.strip():
        valid = False
        reason = (
            "Too little readable content to verify that this is a site/"
            "facility blueprint. Add a room schedule or descriptive notes, "
            "or upload a clearer file."
        )
    elif not valid:
        reason = (
            "The document does not contain enough facility-layout evidence. "
            "We could not identify a convincing combination of site/factory "
            "context, drawing/layout terms, spatial features or infrastructure "
            "labels. It may be an unrelated PDF."
        )
    else:
        reason = (
            "The extracted content contains facility/layout evidence. "
            "This confirms relevance only; it does not certify the drawing "
            "or verify dimensions."
        )

    return {
        "valid": valid,
        "reason": reason,
        "groups": groups,
        "active_groups": active_groups,
        "matched_terms": matched_terms,
    }


def detect_invalid_document(text):
    txt = text.casefold()
    for doc_type, words in DOCUMENT_TYPES.items():
        hits = sum(1 for word in words if word in txt)
        if hits >= 2:
            return {
                "valid": False,
                "type": doc_type,
                "reason": f"This looks like a {doc_type}, not a blueprint.",
            }
    return {"valid": True, "type": "blueprint", "reason": ""}


def blueprint_confidence(relevance, detected_categories):
    score = 0
    score += len(relevance["matched_terms"]) * 5
    score += len(relevance["active_groups"]) * 15
    score += detected_categories * 5
    if relevance["valid"]:
        score += 20
    return min(score, 100)


@app.get("/")
def home():
    return send_from_directory(BASE_DIR, "defence_site_planner_multipage.html")


@app.get("/defence_site_planner_multipage.html")
def planner_page():
    return send_from_directory(BASE_DIR, "defence_site_planner_multipage.html")


@app.get("/blueprint_analysis_db.html")
def analysis_page():
    return send_from_directory(BASE_DIR, "blueprint_analysis_db.html")


@app.get("/blueprint_3d_spatial.html")
def spatial_3d_page():
    return send_from_directory(BASE_DIR, "blueprint_3d_spatial.html")


@app.get("/blueprint_3d.html")
def spatial_3d_page_alias():
    return send_from_directory(BASE_DIR, "blueprint_3d_spatial.html")


@app.get("/api/health")
def health():
    try:
        ensure_db()
        with connect_db() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM blueprint_checks WHERE active=1"
            ).fetchone()[0]
        return jsonify({"ok": True, "database": "connected", "active_rules": count})
    except Exception as exc:
        app.logger.exception("Health check failed")
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.post("/api/analyze")
def analyze():
    data = request.get_json(silent=True) or {}
    filename = str(data.get("filename", "uploaded-blueprint"))[:240]
    extracted = str(data.get("extracted_text", ""))[:250000]
    notes = str(data.get("notes", ""))[:10000]
    combined = (extracted + "\n" + notes).casefold()
    char_count = len(extracted.strip())

    try:
        ensure_db()

        relevance = classify_document(extracted, notes)
        invalid = detect_invalid_document(extracted)

        if not invalid["valid"]:
            return jsonify({
                "ok": True,
                "status": "REJECTED",
                "document_valid": False,
                "summary": invalid["reason"],
                "confidence": 0,
                "document_type": invalid["type"],
                "quality_score": 0,
                "findings": [],
            })

        with connect_db() as conn:
            rules = conn.execute(
                "SELECT check_key, title, keyword_terms_json, recommendation, "
                "detected_message FROM blueprint_checks "
                "WHERE active=1 ORDER BY id"
            ).fetchall()

            findings = []
            detected_categories = 0

            if relevance["valid"]:
                for rule in rules:
                    try:
                        terms = json.loads(rule["keyword_terms_json"] or "[]")
                    except (TypeError, json.JSONDecodeError):
                        app.logger.warning(
                            "Invalid keyword_terms_json for rule %s",
                            rule["check_key"],
                        )
                        terms = []

                    hits = [
                        term for term in terms
                        if isinstance(term, str) and matches(term, combined)
                    ]

                    if hits:
                        detected_categories += 1
                        findings.append({
                            "title": rule["title"],
                            "detail": rule["detected_message"],
                            "detected": True,
                            "matched_terms": hits,
                            "rule_key": rule["check_key"],
                        })
                        findings.append({
                            "title": "Recommended verification: " + rule["title"],
                            "detail": rule["recommendation"],
                            "detected": False,
                            "rule_key": rule["check_key"],
                        })
                    else:
                        findings.append({
                            "title": "Not evidenced in readable text: " + rule["title"],
                            "detail": (
                                str(rule["recommendation"])
                                + " No matching label was found in the extracted "
                                "text; this does not prove the feature is absent."
                            ),
                            "detected": False,
                            "rule_key": rule["check_key"],
                        })

                quality = min(
                    100,
                    round(
                        (min(char_count, 5000) / 5000) * 35
                        + len(relevance["active_groups"]) * 12
                        + detected_categories * 4
                    ),
                )
                confidence = blueprint_confidence(relevance, detected_categories)
                status = "PRELIMINARY"
                summary = (
                    "Relevant facility/layout content detected. The system "
                    "screened readable labels against the active safety, "
                    "environment, utility, accessibility and circulation rules."
                )
            else:
                findings = [
                    {
                        "title": "Upload rejected: blueprint relevance not established",
                        "detail": relevance["reason"],
                        "detected": False,
                    },
                    {
                        "title": "What to upload",
                        "detail": (
                            "Use a factory/site floor plan, facility layout, "
                            "architectural plan or infrastructure drawing. A "
                            "brochure, resume, invoice, certificate or unrelated "
                            "document should not pass this check."
                        ),
                        "detected": False,
                    },
                    {
                        "title": "How to improve detection",
                        "detail": (
                            "Upload a text-readable PDF or high-resolution image. "
                            "Include a title block, room names, legend, dimensions "
                            "or a room schedule. You may add a short accurate "
                            "description in the notes field."
                        ),
                        "detected": False,
                    },
                ]
                quality = 0
                confidence = 0
                status = "REJECTED"
                summary = (
                    "No detailed facility assessment was produced because the "
                    "file did not pass the relevance check."
                )

            cursor = conn.execute(
                "INSERT INTO blueprint_evaluations "
                "(filename, characters_extracted, detected_categories, "
                "findings_json, status) VALUES (?, ?, ?, ?, ?)",
                (
                    filename,
                    char_count,
                    detected_categories,
                    json.dumps(findings),
                    status,
                ),
            )
            evaluation_id = cursor.lastrowid
            conn.commit()

            return jsonify({
                "ok": True,
                "status": status,
                "document_valid": relevance["valid"],
                "relevance_reason": relevance["reason"],
                "relevance_groups": relevance["active_groups"],
                "matched_relevance_terms": relevance["matched_terms"],
                "summary": summary,
                "quality_score": quality,
                "confidence": confidence,
                "evaluation_id": evaluation_id,
                "rules_used": len(rules) if relevance["valid"] else 0,
                "detected_categories": detected_categories,
                "total_categories": len(rules),
                "findings": findings,
                "saved_at": datetime.now(timezone.utc).isoformat(),
                "storage_note": (
                    "Only summary findings and file metadata are stored. "
                    "The uploaded blueprint and extracted text are not stored."
                ),
            })

    except sqlite3.Error as exc:
        app.logger.exception("Database analysis failed")
        return jsonify({
            "ok": False,
            "error": "Database analysis failed: " + str(exc),
        }), 500
    except Exception as exc:
        app.logger.exception("Blueprint analysis failed")
        return jsonify({
            "ok": False,
            "error": "Blueprint analysis failed: " + str(exc),
        }), 500


@app.get("/api/history")
def history():
    try:
        ensure_db()
        with connect_db() as conn:
            rows = conn.execute(
                "SELECT id, filename, evaluation_timestamp, "
                "characters_extracted, detected_categories, status "
                "FROM blueprint_evaluations ORDER BY id DESC LIMIT 20"
            ).fetchall()
        return jsonify({"evaluations": [dict(row) for row in rows]})
    except Exception as exc:
        app.logger.exception("History API failed")
        return jsonify({"ok": False, "error": str(exc)}), 500


@app.get("/<path:filename>")
def serve_file(filename):
    target = BASE_DIR / filename
    if target.is_file():
        return send_from_directory(BASE_DIR, filename)
    return "The requested URL was not found on the server.", 404


def open_browser(port):
    try:
        webbrowser.open(f"http://127.0.0.1:{port}/blueprint_3d_spatial.html")
    except Exception:
        pass


if __name__ == "__main__":
    ensure_db()
    for port in [5000, 5050, 8080, 8000]:
        try:
            print(f"DefenceSite AI running at http://127.0.0.1:{port}/blueprint_3d_spatial.html")
            Timer(1.2, open_browser, args=[port]).start()
            app.run(host="127.0.0.1", port=port, debug=False)
            break
        except OSError as e:
            if "10048" in str(e) or "already in use" in str(e).lower():
                print(f"Port {port} in use, trying next port...")
                continue
            raise
