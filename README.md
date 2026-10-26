# 🛡️ SENTINEL BASE AI - 3D Spatial Intelligence & Defence Site Planner

A state-of-the-art interactive 3D spatial planning, digital twin, and defense infrastructure layout platform built with **Three.js**, **Tailwind CSS**, and **Python / Flask**.

![License](https://img.shields.io/badge/License-MIT-blue.svg)
![Python](https://img.shields.io/badge/Python-3.10%2B-brightgreen)
![ThreeJS](https://img.shields.io/badge/Three.js-r128-orange)
![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v3-cyan)

---

## 🚀 Key Features

- **🌐 Interactive 3D Spatial Twin (WebGL / Three.js)**:
  - Real-time 3D orbital inspection of military industrial plant layouts.
  - Multi-angle camera presets: Drone Orbit, 2D/3D Top-Down, High-Bay Assembly Hall, and Hazmat Zone.
  - Interactive layer toggles for 3D structural buildings, heavy industrial machinery, glowing hazard domes, and projected blueprint grid.
  - Interactive day/night tactical lighting modes.

- **🗺️ Direct Blueprint to 3D Spatial Pipeline**:
  - Upload architectural or site blueprints directly from the UI.
  - Automatic persistence using browser `IndexedDB` with instant projection onto the 3D ground plane.
  - Offline fallback support — works seamlessly via Flask or directly in any modern browser via double-click.

- **📑 Automated Compliance & Audit Report Generator**:
  - Live inspection telemetry for structural units, power consumption, explosion risk zones, and clearance radii.
  - Instant audit report generation with direct PDF / Print capability.

- **🏗️ Defence Site Planner HUD**:
  - Interactive blueprint analysis and zone layout management.
  - Real-time telemetry monitoring for defense production lines.

---

## 📂 Project Structure

```text
DefenceSite_AI/
├── app.py                             # Flask server with dynamic port allocation & static serving
├── defence_site_planner_multipage.html# Main defense site planner frontend
├── blueprint_3d_spatial.html          # Interactive 3D WebGL Digital Twin & Audit Generator
├── blueprint_analysis_db.html         # SQLite blueprint database inspection interface
├── defence_factory.db                 # SQLite database storing facility telemetry & zones
├── tailwind.css                       # Local Tailwind styling backup
├── requirements.txt                   # Python dependencies (Flask, Flask-CORS)
├── START_DEFENCESITE.bat              # One-click Windows launch launcher
└── README.md                          # Project documentation
```

---

## ⚡ Quick Start

### Option 1: One-Click Windows Launch (Recommended)
Simply double-click the included batch launcher:
```text
START_DEFENCESITE.bat
```
This automatically installs dependencies, chooses an available port (5000, 5050, 8080, or 8000), launches the server, and opens your default browser.

---

### Option 2: Run via Python CLI

1. **Clone the repository**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/DefenceSite_AI.git
   cd DefenceSite_AI
   ```

2. **(Optional) Create a virtual environment**:
   ```bash
   python -m venv .venv
   # On Windows:
   .venv\Scripts\activate
   # On Linux/macOS:
   source .venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Start the application**:
   ```bash
   python app.py
   ```
   Open your browser at `http://127.0.0.1:5000` (or the port displayed in terminal).

---

### Option 3: Standalone Offline Mode (Zero Install)
You can directly double-click:
- `defence_site_planner_multipage.html` for the Planner Dashboard
- `blueprint_3d_spatial.html` for the 3D Spatial Digital Twin

All 3D WebGL scenes, blueprint local storage, and audit report generation work 100% client-side without needing a server.

---

## 🛠️ Tech Stack
- **Frontend**: HTML5, Three.js (r128), OrbitControls, Tailwind CSS, JavaScript (ES6+), IndexedDB API
- **Backend**: Python 3, Flask, SQLite3
- **Visualization**: WebGL volumetric meshes, procedural lighting, radial blast-radius shaders

---

## 📄 License
This project is open-source and available under the [MIT License](LICENSE).
