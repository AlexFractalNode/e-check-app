import os

# --- KONFIGURATION ---
OUTPUT_FILE = "index.html"
APP_TITLE = "E-Check App"

# --- DER APP CODE (HTML/CSS/JS) ---
html_content = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>E-Check App</title>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <style>
        :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #10b981; --danger: #ef4444; }
        body { font-family: -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        
        header { padding: 1rem; text-align: center; font-weight: 800; font-size: 1.2rem; background: rgba(15, 23, 42, 0.9); border-bottom: 1px solid #334155; z-index: 10; }
        
        #scanner-wrapper { flex: 1; position: relative; background: #000; display: flex; align-items: center; justify-content: center; }
        #reader { width: 100%; height: 100%; object-fit: cover; }
        
        /* Scanner UI Überlagerung */
        .scan-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; display: flex; align-items: center; justify-content: center; }
        .scan-box { width: 250px; height: 250px; border: 4px solid var(--primary); border-radius: 20px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.5); position: relative; }
        
        /* Bottom Sheet */
        #result-sheet { position: absolute; bottom: 0; left: 0; right: 0; background: var(--card); border-radius: 20px 20px 0 0; padding: 1.5rem; transform: translateY(110%); transition: transform 0.3s ease; box-shadow: 0 -10px 40px rgba(0,0,0,0.5); z-index: 20; max-height: 80vh; overflow-y: auto; }
        #result-sheet.open { transform: translateY(0); }
        
        .status-badge { display: inline-block; padding: 6px 14px; border-radius: 99px; font-weight: bold; font-size: 0.9rem; margin-bottom: 1rem; text-transform: uppercase; }
        .status-safe { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .status-danger { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        
        h2 { margin: 0 0 0.5rem 0; font-size: 1.5rem; }
        p { color: #94a3b8; line-height: 1.5; margin-bottom: 1.5rem; }
        
        .btn { width: 100%; padding: 15px; border: none; border-radius: 12px; font-weight: bold; font-size: 1rem; cursor: pointer; margin-top: 1rem; }
        .btn-close { background: #334155; color: white; }
        
        /* Debug Input (Versteckt, oben rechts antippen für Test) */
        .debug-trigger { position: absolute; top: 0; right: 0; width: 50px; height: 50px; z-index: 99; opacity: 0; }
    </style>
</head>
<body>

<header>🥗 E-Check Scanner</header>

<div id="scanner-wrapper">
    <div id="reader"></div>
    <div class="scan-overlay"><div class="scan-box"></div></div>
    <div class="debug-trigger" onclick="lookupCode('E120')"></div>
</div>

<div id="result-sheet">
    <div id="result-content">Lade Daten...</div>
    <button class="btn btn-close" onclick="startScanner()">Nächstes Produkt scannen</button>
</div>

<script>
    let db = {};
    let html5QrcodeScanner = null;

    // 1. DATENBANK LADEN
    fetch('app_database.json')
        .then(r => {
            if (!r.ok) throw new Error("HTTP error " + r.status);
            return r.json();
        })
        .then(data => { 
            db = data; 
            console.log("✅ Datenbank geladen:", Object.keys(db).length, "Einträge");
        })
        .catch(e => {
            console.error(e);
            document.getElementById('result-content').innerHTML = "⚠️ Fehler: Datenbank konnte nicht geladen werden.<br>Bitte Seite neu laden.";
            document.getElementById('result-sheet').classList.add('open');
        });

    // 2. SCANNER LOGIK
    function onScanSuccess(decodedText) {
        if(html5QrcodeScanner) {
            try { html5QrcodeScanner.clear(); } catch(e){}
        }
        lookupCode(decodedText);
    }

    function startScanner() {
        document.getElementById('result-sheet').classList.remove('open');
        
        // Verhindert mehrfachen Start
        if(html5QrcodeScanner) return; 

        html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
        html5QrcodeScanner.render(onScanSuccess, (err) => { /* Fehler ignorieren (Scan läuft) */ });
    }

    // 3. DATEN ABGLEICH
    function lookupCode(code) {
        code = code.toUpperCase().trim();
        // Versuch E-Nummer zu finden (auch wenn Barcode gescannt wurde - MVP Hack)
        // In Zukunft: API Call Barcode -> E-Nummer
        
        const data = db[code];
        const content = document.getElementById('result-content');
        const sheet = document.getElementById('result-sheet');

        if (data) {
            // BEKANNTES PRODUKT
            const isSafe = data.r.toLowerCase().includes("unbedenklich") || data.r.toLowerCase().includes("safe");
            const statusClass = isSafe ? "status-safe" : "status-danger";
            
            content.innerHTML = `
                <div class="status-badge ${statusClass}">${data.r}</div>
                <h2>${code} - ${data.n}</h2>
                <div style="display:flex; gap:10px; margin-bottom:1rem;">
                    <span>${data.v ? "🌱 Vegan" : "🥩 Nicht Vegan"}</span>
                    <span>${data.g ? "🍞 Glutenfrei" : "🌾 Enthält Gluten"}</span>
                </div>
                <p>${data.d}</p>
            `;
        } else {
            // UNBEKANNTES PRODUKT
            content.innerHTML = `
                <div class="status-badge status-danger">Unbekannt</div>
                <h2>${code}</h2>
                <p>Dieser Code ist noch nicht in unserer Datenbank.</p>
            `;
        }
        sheet.classList.add('open');
    }

    // Start beim Laden
    startScanner();
</script>

</body>
</html>
"""

# Datei schreiben
print(f"🏗️ Erstelle {OUTPUT_FILE}...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ Fertig!")
