import os

# --- KONFIGURATION ---
OUTPUT_FILE = "index.html"
LEXIKON_BASE_URL = "https://alexfractalnode.github.io/E-Nummern-Lexikon"

# --- DER APP CODE (HTML/CSS/JS) ---
html_content = f"""
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no, viewport-fit=cover">
    <title>E-Check Pro</title>
    <script src="https://unpkg.com/html5-qrcode" type="text/javascript"></script>
    <style>
        :root {{ 
            --bg: #0f172a; 
            --card-bg: #1e293b; 
            --text-main: #f1f5f9; 
            --text-muted: #94a3b8;
            --primary: #10b981; 
            --warning: #f59e0b; 
            --danger: #ef4444; 
            --safe: #22c55e;
            --accent: #3b82f6;
        }}
        
        * {{ box-sizing: border-box; -webkit-tap-highlight-color: transparent; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; 
            background: var(--bg); 
            color: var(--text-main); 
            margin: 0; padding: 0; 
            height: 100vh; 
            display: flex; flex-direction: column; 
            overflow: hidden; 
        }}
        
        /* Modern Header */
        header {{ 
            position: absolute; top: 0; left: 0; right: 0;
            padding: 1rem; padding-top: max(1rem, env(safe-area-inset-top));
            text-align: center; 
            background: linear-gradient(180deg, rgba(15,23,42,0.9) 0%, rgba(15,23,42,0) 100%);
            z-index: 20;
            pointer-events: none;
        }}
        header h1 {{ margin: 0; font-size: 1.2rem; font-weight: 800; text-shadow: 0 2px 4px rgba(0,0,0,0.5); color: white; }}
        
        /* Fullscreen Scanner */
        #scanner-wrapper {{ flex: 1; position: relative; background: #000; }}
        #reader {{ width: 100%; height: 100%; object-fit: cover; }}
        
        /* UI Overlay */
        .scan-overlay {{ 
            position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
            display: flex; align-items: center; justify-content: center; 
            pointer-events: none;
        }}
        .scan-frame {{ 
            width: 280px; height: 280px; 
            border: 2px solid rgba(255,255,255,0.3); 
            border-radius: 24px; 
            position: relative; 
            box-shadow: 0 0 0 4000px rgba(0,0,0,0.6); /* Dimmed Background */
        }}
        .scan-frame::after {{
            content: ''; position: absolute; top: -2px; left: -2px; right: -2px; bottom: -2px;
            border: 2px solid var(--primary); border-radius: 24px;
            clip-path: polygon(0% 20%, 0% 0%, 20% 0%, 80% 0%, 100% 0%, 100% 20%, 100% 80%, 100% 100%, 80% 100%, 20% 100%, 0% 100%, 0% 80%);
            animation: pulse 2s infinite;
        }}
        @keyframes pulse {{ 0% {{ opacity: 0.5; }} 50% {{ opacity: 1; }} 100% {{ opacity: 0.5; }} }}

        /* Loading */
        .loader {{
            position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
            width: 40px; height: 40px; border: 4px solid rgba(255,255,255,0.2);
            border-top-color: var(--primary); border-radius: 50%;
            animation: spin 0.8s linear infinite; display: none; z-index: 30;
        }}
        @keyframes spin {{ to {{ transform: translate(-50%, -50%) rotate(360deg); }} }}

        /* Bottom Sheet (Result) */
        #result-sheet {{ 
            position: absolute; bottom: 0; left: 0; right: 0; 
            background: var(--card-bg); 
            border-radius: 24px 24px 0 0; 
            padding: 1.5rem; padding-bottom: max(1.5rem, env(safe-area-inset-bottom));
            transform: translateY(110%); 
            transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1); 
            box-shadow: 0 -10px 40px rgba(0,0,0,0.5); 
            z-index: 40; 
            max-height: 85vh; 
            overflow-y: auto; 
            border-top: 1px solid rgba(255,255,255,0.1);
        }}
        #result-sheet.open {{ transform: translateY(0); }}
        
        .drag-handle {{ width: 40px; height: 4px; background: rgba(255,255,255,0.2); border-radius: 2px; margin: 0 auto 1.5rem auto; }}

        /* Product Header */
        .product-header {{ display: flex; gap: 16px; align-items: start; margin-bottom: 1.5rem; }}
        .product-img {{ 
            width: 80px; height: 80px; border-radius: 16px; 
            background: #334155; object-fit: cover; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }}
        .product-info {{ flex: 1; }}
        .product-brand {{ font-size: 0.85rem; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 4px; }}
        .product-title {{ margin: 0; font-size: 1.3rem; line-height: 1.3; font-weight: 700; }}

        /* Sections */
        .section-title {{ font-size: 0.9rem; font-weight: 700; color: var(--text-muted); margin: 1.5rem 0 0.8rem 0; text-transform: uppercase; letter-spacing: 0.05em; }}
        
        /* Grid for Diet Info */
        .diet-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; }}
        .diet-card {{ 
            background: rgba(255,255,255,0.05); border-radius: 12px; padding: 12px; 
            display: flex; align-items: center; gap: 10px; border: 1px solid rgba(255,255,255,0.05);
        }}
        .diet-icon {{ font-size: 1.5rem; }}
        .diet-label {{ font-size: 0.9rem; font-weight: 600; }}
        .diet-sub {{ font-size: 0.75rem; color: var(--text-muted); display: block; }}
        
        .status-green {{ color: var(--safe); }}
        .status-red {{ color: var(--danger); }}
        .status-grey {{ color: var(--text-muted); }}

        /* Additive List */
        .additive-list {{ display: flex; flex-direction: column; gap: 8px; }}
        .additive-item {{ 
            background: rgba(255,255,255,0.05); padding: 14px; border-radius: 12px; 
            display: flex; justify-content: space-between; align-items: center; 
            border: 1px solid transparent; transition: all 0.2s; cursor: pointer;
        }}
        .additive-item:active {{ background: rgba(255,255,255,0.1); transform: scale(0.98); }}
        
        /* Clickable Indicator */
        .additive-arrow {{ color: var(--text-muted); font-size: 1.2rem; opacity: 0.5; }}

        .code-badge {{ 
            font-family: monospace; font-weight: bold; font-size: 0.9rem; 
            padding: 4px 8px; border-radius: 6px; margin-right: 8px;
            background: rgba(0,0,0,0.3);
        }}
        
        .risk-dot {{ width: 10px; height: 10px; border-radius: 50%; display: inline-block; margin-right: 6px; }}
        .dot-green {{ background: var(--safe); box-shadow: 0 0 8px var(--safe); }}
        .dot-orange {{ background: var(--warning); box-shadow: 0 0 8px var(--warning); }}
        .dot-red {{ background: var(--danger); box-shadow: 0 0 8px var(--danger); }}

        /* Button */
        .btn {{ 
            width: 100%; padding: 16px; border: none; border-radius: 16px; 
            font-weight: 700; font-size: 1rem; cursor: pointer; margin-top: 2rem; 
            transition: transform 0.2s;
        }}
        .btn:active {{ transform: scale(0.97); }}
        .btn-primary {{ background: var(--primary); color: #000; }}
        .btn-close {{ background: rgba(255,255,255,0.1); color: white; }}
        
    </style>
</head>
<body>

<header>
    <h1>E-Check Pro</h1>
</header>

<div id="scanner-wrapper">
    <div id="reader"></div>
    <div class="scan-overlay">
        <div class="scan-frame"></div>
    </div>
    <div id="loading" class="loader"></div>
</div>

<div id="result-sheet">
    <div class="drag-handle"></div>
    <div id="result-content"></div>
    <button class="btn btn-close" onclick="startScanner()">Nächstes Produkt scannen</button>
</div>

<script>
    const LEXIKON_URL = "{LEXIKON_BASE_URL}";
    let db = {{}};
    let html5QrcodeScanner = null;
    let isScanning = true;

    // 1. DATENBANK LADEN
    fetch('app_database.json')
        .then(r => r.json())
        .then(data => {{ db = data; console.log("DB Ready"); }})
        .catch(e => console.error("DB Error", e));

    // 2. HELPER: Slug Generator für URL (muss wie Python logic sein)
    function createSlug(code, name) {{
        let text = code + "-" + name;
        text = text.toLowerCase();
        // Ersetze alles was nicht a-z0-9 ist durch Bindestrich
        text = text.replace(/[^a-z0-9]+/g, '-');
        // Entferne Bindestriche am Anfang/Ende
        text = text.replace(/^-+|-+$/g, '');
        return text;
    }}

    // 3. HELPER: Übersetzer für OFF Tags
    function translateTag(tag) {{
        // en:gluten -> Gluten
        if(!tag) return "";
        return tag.split(':')[1].replace(/-/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
    }}

    // 4. SCANNER STARTEN (Back Camera Forced)
    function startScanner() {{
        document.getElementById('result-sheet').classList.remove('open');
        document.getElementById('loading').style.display = 'none';

        if(html5QrcodeScanner) return;

        html5QrcodeScanner = new Html5QrcodeScanner("reader", {{ 
            fps: 10, 
            qrbox: 250,
            facingMode: {{ exact: "environment" }} // Versucht Rückkamera zu erzwingen
        }});
        
        html5QrcodeScanner.render(onScanSuccess, (err) => {{}});
        isScanning = true;
    }}

    function onScanSuccess(barcode) {{
        if(!isScanning) return;
        isScanning = false;
        
        try {{ html5QrcodeScanner.clear(); html5QrcodeScanner = null; }} catch(e){{}}
        
        analyzeProduct(barcode);
    }}

    // 5. ANALYSE LOGIK
    async function analyzeProduct(barcode) {{
        const sheet = document.getElementById('result-sheet');
        const content = document.getElementById('result-content');
        const loader = document.getElementById('loading');
        
        loader.style.display = 'block';
        content.innerHTML = "";

        try {{
            // API ABFRAGE
            const response = await fetch(`https://world.openfoodfacts.org/api/v0/product/${{barcode}}.json`);
            const data = await response.json();

            loader.style.display = 'none';
            sheet.classList.add('open');

            if (data.status === 0) {{
                content.innerHTML = `<h2>Nicht gefunden 🤷‍♂️</h2><p>Unbekannter Barcode: ${{barcode}}</p>`;
                return;
            }}

            const p = data.product;
            
            // --- DATEN EXTRAHIEREN ---
            
            // 1. DIET INFO (Vegan, Palmöl, etc.)
            const analysis = p.ingredients_analysis_tags || [];
            const isVegan = analysis.includes('en:vegan');
            const isNonVegan = analysis.includes('en:non-vegan');
            const isPalmOil = analysis.includes('en:palm-oil');
            
            // 2. ALLERGENE
            const allergens = p.allergens_tags || []; // ["en:gluten", "en:milk"]
            
            // 3. E-NUMMERN
            const additives = p.additives_tags || [];
            
            // --- HTML GENERIEREN ---
            
            // Header
            let html = `
                <div class="product-header">
                    <img src="${{p.image_front_small_url || 'https://via.placeholder.com/80'}}" class="product-img">
                    <div class="product-info">
                        <div class="product-brand">${{p.brands || 'Marke unbekannt'}}</div>
                        <h2 class="product-title">${{p.product_name || 'Produkt'}}</h2>
                    </div>
                </div>
            `;

            // Section: DIET & ALARM
            html += `<div class="diet-grid">`;
            
            // Vegan Status
            if(isVegan) {{
                html += `<div class="diet-card"><div class="diet-icon">🌱</div><div><span class="diet-label status-green">Vegan</span><span class="diet-sub">Verifiziert</span></div></div>`;
            }} else if(isNonVegan) {{
                html += `<div class="diet-card"><div class="diet-icon">🥩</div><div><span class="diet-label status-red">Nicht Vegan</span><span class="diet-sub">Tierische Stoffe</span></div></div>`;
            }} else {{
                html += `<div class="diet-card"><div class="diet-icon">❓</div><div><span class="diet-label status-grey">Unbekannt</span><span class="diet-sub">Vegan Status</span></div></div>`;
            }}

            // Palmöl
            if(isPalmOil) {{
                html += `<div class="diet-card"><div class="diet-icon">🌴</div><div><span class="diet-label status-red">Palmöl</span><span class="diet-sub">Enthalten</span></div></div>`;
            }}
            
            html += `</div>`; // End Grid

            // Section: ALLERGENE
            if(allergens.length > 0) {{
                html += `<div class="section-title">⚠️ Allergene</div><div class="diet-grid">`;
                allergens.forEach(a => {{
                    html += `<div class="diet-card" style="border-color: rgba(239,68,68,0.3)">
                                <span class="diet-label status-red">${{translateTag(a)}}</span>
                             </div>`;
                }});
                html += `</div>`;
            }}

            // Section: E-NUMMERN (CLICKABLE)
            if(additives.length > 0) {{
                html += `<div class="section-title">🧪 Zusatzstoffe</div><div class="additive-list">`;
                
                additives.forEach(tag => {{
                    let code = tag.split(':')[1].toUpperCase();
                    let info = db[code]; // Check lokale DB
                    
                    let riskDot = "dot-orange";
                    let riskName = "Unbekannt";
                    let niceName = "Lade...";
                    let slugUrl = "#";

                    if(info) {{
                        niceName = info.n;
                        riskName = info.r;
                        if(info.r.includes("Unbedenklich")) riskDot = "dot-green";
                        if(info.r.includes("Bedenklich") || info.r.includes("Hoch")) riskDot = "dot-red";
                        
                        // Generiere Link zum Lexikon
                        const slug = createSlug(code, niceName);
                        slugUrl = `${{LEXIKON_URL}}/${{slug}}.html`;
                    }} else {{
                        // Fallback für unbekannte E-Nummern
                        niceName = "Nicht in DB";
                    }}

                    // Clickable Row
                    html += `
                    <div class="additive-item" onclick="window.open('${{slugUrl}}', '_blank')">
                        <div style="display:flex; align-items:center;">
                            <span class="${{riskDot}} risk-dot"></span>
                            <div>
                                <div><span class="code-badge">${{code}}</span> <span style="font-weight:600; font-size:0.95rem;">${{niceName}}</span></div>
                                <div style="font-size:0.8rem; color:#94a3b8; margin-top:4px;">${{riskName}}</div>
                            </div>
                        </div>
                        <div class="additive-arrow">›</div>
                    </div>`;
                }});
                html += `</div>`;
            }} else {{
                html += `<div style="margin-top:1.5rem; text-align:center; color:#94a3b8; background:rgba(255,255,255,0.05); padding:1rem; border-radius:12px;">✅ Clean Label: Keine E-Nummern deklariert.</div>`;
            }}

            content.innerHTML = html;

        }} catch (e) {{
            loader.style.display = 'none';
            content.innerHTML = `<p>Fehler: Kein Internet?</p>`;
            sheet.classList.add('open');
        }}
    }}

    startScanner();
</script>

</body>
</html>
"""

# Datei schreiben
print(f"🏗️ Erstelle {OUTPUT_FILE} (Pro Version)...")
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    f.write(html_content)
print("✅ Fertig!")
