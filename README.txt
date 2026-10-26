# DefenceSite AI — relevance-checked blueprint screening prototype

## Included modules
- `defence_site_planner_multipage.html`: main planner and blueprint upload page.
- `blueprint_analysis_db.html`: animated multi-stage analysis screen; extracts PDF text / image OCR in the browser and displays the report.
- `app.py`: Flask API with a document-relevance gate, infrastructure keyword screening and SQLite history.
- `defence_factory.db`: general factory safety / environmental screening rules and evaluation history.
- `requirements.txt`: Flask dependency.

## What changed in this version
1. A relevance gate checks whether readable document content looks like a facility/site/factory layout before detailed screening.
2. Unrelated or low-information files are marked `REJECTED`, with the reason and instructions for what to upload instead. A rejected document is not given a misleading safety/quality score.
3. Relevant drawings are screened against active SQLite rules for emergency egress, fire protection, ventilation, water/drainage, waste/material storage, electrical utilities, traffic/circulation, accessibility/welfare, emergency arrangements and room zoning.
4. The report shows matched labels, evidence categories, checks without readable evidence, recommendations, and a text-evidence coverage indicator. The coverage indicator is not a safety score.
5. The report page uses a staged animated scan workflow and a drawing preview inspired by the supplied reference video.
6. The back-to-planner action returns to `/`, the Flask homepage route.

## Run on Windows
1. Install Python 3.10+.
2. Keep all project files together in one folder.
3. Open PowerShell in that folder.
4. Run:
   ```powershell
   py -m pip install -r requirements.txt
   py app.py
   ```
5. Keep PowerShell running and open http://127.0.0.1:5000
6. Upload a PDF/image/TXT drawing and press the analyse button.

## API checks
- `GET /api/health` — reports database connection and active rule count.
- `POST /api/analyze` — receives extracted text, notes and filename; returns document relevance, matched categories, findings and evaluation record ID.
- `GET /api/history` — lists the latest 20 saved summary records.

## Important limitations
- The relevance gate and rule screening use transparent keyword/text evidence. It is not a trained AI vision model.
- The animated scan line is a presentation effect, not actual object detection. This version does not identify machine objects, measure geometry, verify clearances, understand drawing scale or assess structural integrity.
- A missing text label does not prove a feature is absent; a detected label does not prove it is correctly designed or safe.
- This is preliminary screening only, not legal, engineering, fire-safety or construction approval. Qualified professionals must review the complete drawing.
- The browser extracts PDF/image text. Extracted text is sent transiently to the local Flask API for matching; the server stores only summary findings and file metadata, not the uploaded blueprint or extracted text.
- PDF.js and Tesseract.js load from CDNs, so internet access is needed for those features.
