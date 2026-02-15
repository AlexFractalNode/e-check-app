import os

# --- KONFIGURATION ---
OUTPUT_FILE = "index.html"
APP_TITLE = "E-Check Scanner"

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
        :root { --bg: #0f172a; --card: #1e293b; --text: #f8fafc; --primary: #10b981; --warning: #f59e0b; --danger: #ef4444; }
        body { font-family: -apple-system, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 0; height: 100vh; display: flex; flex-direction: column; overflow: hidden; }
        
        header { padding: 1rem; text-align: center; font-weight: 800; font-size: 1.2rem; background: rgba(15, 23, 42, 0.9); border-bottom: 1px solid #334155; z-index: 10; display:flex; justify-content:center; align-items:center; gap:10px; }
        
        #scanner-wrapper { flex: 1; position: relative; background: #000; display: flex; align-items: center; justify-content: center; }
        #reader { width: 100%; height: 100%; object-fit: cover; }
        
        .scan-overlay { position: absolute; top: 0; left: 0; right: 0; bottom: 0; pointer-events: none; display: flex; align-items: center; justify-content: center; }
        .scan-box { width: 250px; height: 250px; border: 4px solid var(--primary); border-radius: 20px; box-shadow: 0 0 20px rgba(16, 185, 129, 0.5); position: relative; }
        
        /* Loading Spinner */
        .spinner { border: 4px solid rgba(255,255,255,0.1); border-left-color: var(--primary); border-radius: 50%; width: 30px; height: 30px; animation: spin 1s linear infinite; margin: 20px auto; display: none; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

        /* Bottom Sheet */
        #result-sheet { position: absolute; bottom: 0; left: 0; right: 0; background: var(--card); border-radius: 20px 20px 0 0; padding: 1.5rem; transform: translateY(110%); transition: transform 0.3s ease; box-shadow: 0 -10px 40px rgba(0,0,0,0.5); z-index: 20; max-height: 85vh; overflow-y: auto; }
        #result-sheet.open { transform: translateY(0); }
        
        .product-header { display: flex; gap: 15px; align-items: center; margin-bottom: 1.5rem; }
        .product-img { width: 60px; height: 60px; border-radius: 10px; background: #334155; object-fit: cover; }
        .product-info h2 { margin: 0; font-size: 1.2rem; line-height: 1.2; }
        .product-brand { font-size: 0.9rem; color: #94a3b8; }
        
        .additive-list { display: flex; flex-direction: column; gap: 10px; }
        .additive-item { background: rgba(255,255,255,0.05); padding: 12px; border-radius: 8px; display: flex; justify-content: space-between; align-items: center; }
        .additive-code { font-weight: bold; min-width: 60px; }
        
        .badge { padding: 4px 10px; border-radius: 99px; font-size: 0.75rem; font-weight: bold; text-transform: uppercase; }
        .b-green { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .b-orange { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
        .b-red { background: rgba(239, 68, 68, 0.2); color: #f87171; }
        
        .btn { width: 100%; padding: 15px; border: none; border-radius: 12px; font-weight: bold; font-size: 1rem; cursor: pointer; margin-top: 1.5rem; }
        .btn-close { background: #334155; color: white; }
        .btn-affiliate { background: var(--primary); color: white; margin-top: 10px; display: none; }
        
    </style>
</head>
<body>

<header>🥗 E-Check Scanner</header>

<div id="scanner-wrapper">
    <div id="reader"></div>
    <div class="scan-overlay"><div class="scan-box"></div></div>
</div>

<div id="result-sheet">
    <div id="loading" class="spinner"></div>
    <div id="result-content" style="display:none;"></div>
    <button id="scan-btn" class="btn btn-close" onclick="startScanner()">Nächstes Produkt scannen</button>
</div>

<script>
    let db = {};
    let html5QrcodeScanner = null;
    let isScanning = true;

    // 1. LADE DEINE LOKALE DATENBANK (für den Abgleich)
    fetch('app_database.json')
        .then(r => r.json())
        .then(data => { db = data; console.log("DB Ready:", Object.keys(db).length); })
        .catch(e => console.error("DB Error:", e));

    // 2. SCANNER STARTEN
    function startScanner() {
        document.getElementById('result-sheet').classList.remove('open');
        setTimeout(() => {
            document.getElementById('result-content').style.display = 'none';
            document.getElementById('loading').style.display = 'none';
        }, 300);

        if(html5QrcodeScanner) return; // Läuft schon

        html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
        html5QrcodeScanner.render(onScanSuccess, (err) => {});
        isScanning = true;
    }

    function onScanSuccess(barcode) {
        if(!isScanning) return;
        isScanning = false;
        
        try { html5QrcodeScanner.clear(); html5QrcodeScanner = null; } catch(e){}
        
        analyzeProduct(barcode);
    }

    // 3. API AUFRUF & ANALYSE
    async function analyzeProduct(barcode) {
        const sheet = document.getElementById('result-sheet');
        const content = document.getElementById('result-content');
        const loader = document.getElementById('loading');
        
        sheet.classList.add('open');
        loader.style.display = 'block';
        content.innerHTML = "";

        try {
            // A) FRAGE OPEN FOOD FACTS
            const response = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
            const data = await response.json();

            loader.style.display = 'none';
            content.style.display = 'block';

            if (data.status === 0) {
                content.innerHTML = `<h2>Nicht gefunden 🤷‍♂️</h2><p>Barcode ${barcode} ist nicht in der globalen Datenbank.</p>`;
                return;
            }

            const product = data.product;
            const additives = product.additives_tags || []; // ["en:e120", "en:e330"]
            
            // B) ANALYSIERE INHALTSSTOFFE MIT DEINER DB
            let htmlList = "";
            let maxRisk = 0; // 0=Safe, 1=Medium, 2=Danger
            let foundVeganIssue = false;

            if (additives.length === 0) {
                 htmlList = `<div class="additive-item"><span>✅ Keine E-Nummern deklariert.</span></div>`;
            } else {
                additives.forEach(tag => {
                    // "en:e120" -> "E120"
                    let code = tag.split(':')[1].toUpperCase();
                    let info = db[code]; // Suche in DEINER Datenbank

                    if (info) {
                        // Risiko Bestimmung
                        let riskClass = "b-green";
                        if (info.r.includes("Vorsicht")) { riskClass = "b-orange"; if(maxRisk<1) maxRisk=1; }
                        if (info.r.includes("Bedenklich") || info.r.includes("Hoch")) { riskClass = "b-red"; maxRisk=2; }
                        
                        if (!info.v) foundVeganIssue = true; // Nicht vegan!

                        htmlList += `
                        <div class="additive-item">
                            <div>
                                <div class="additive-code">${code} <span class="badge ${riskClass}">${info.r}</span></div>
                                <div style="font-size:0.8rem; color:#94a3b8;">${info.n}</div>
                            </div>
                            <div style="font-size:1.2rem;">${info.v ? "🌱" : "🥩"}</div>
                        </div>`;
                    } else {
                        // E-Nummer gefunden, aber nicht in unserer DB
                        htmlList += `<div class="additive-item"><div><strong>${code}</strong></div><span class="badge b-orange">Unbekannt</span></div>`;
                    }
                });
            }

            // C) ERGEBNIS ANZEIGEN
            let statusEmoji = maxRisk === 0 ? "✅" : (maxRisk === 1 ? "⚠️" : "⛔");
            let statusText = maxRisk === 0 ? "Safe" : (maxRisk === 1 ? "Naja..." : "Vorsicht!");
            
            // Affiliate Button Logik
            let affiliateBtn = "";
            if (maxRisk === 2 || foundVeganIssue) {
                 affiliateBtn = `<button class="btn btn-affiliate" onclick="window.open('https://www.amazon.de/s?k=bio+alternative+${product.product_name}&tag=DEIN-TAG', '_blank')">🌿 Gesunde Alternative finden</button>`;
            }

            content.innerHTML = `
                <div class="product-header">
                    <img src="${product.image_front_small_url || 'https://via.placeholder.com/60'}" class="product-img">
                    <div class="product-info">
                        <div class="product-brand">${product.brands || 'Marke unbekannt'}</div>
                        <h2>${product.product_name || 'Produkt'}</h2>
                    </div>
                </div>
                
                <div style="margin-bottom:1rem; display:flex; justify-content:space-between; align-items:center;">
                    <h3>Analyse</h3>
                    <span class="badge ${maxRisk===0?'b-green':(maxRisk===1?'b-orange':'b-red')}" style="font-size:1rem;">${statusEmoji} ${statusText}</span>
                </div>

                <div class="additive-list">
                    ${htmlList}
                </div>
                
                ${affiliateBtn}
            `;

        } catch (e) {
            loader.style.display = 'none';
            content.style.display = 'block';
            content.innerHTML = `<p>Fehler bei der Verbindung. Hast du Internet?</p>`;
            console.error(e);
        }
    }

    startScanner();
</script>

</body>
</html>
"""

# Datei schreiben
print(f"🏗️ Erstelle {OUTPUT_FILE} mit API-Power...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ Fertig!")
