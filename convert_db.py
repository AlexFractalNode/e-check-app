import json

# Konfiguration
INPUT_FILE = 'generated_additives.json'
OUTPUT_FILE = 'app_database.json'

def convert():
    print(f"🔄 Lade {INPUT_FILE}...")
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8') as f:
            raw_data = json.load(f)
    except FileNotFoundError:
        print("❌ Fehler: Datei nicht gefunden. Bitte lade 'generated_additives.json' herunter!")
        return

    # Wir bauen ein Dictionary für O(1) Zugriff (superschnell)
    # Key = E-Nummer (z.B. "E100"), Value = Infos
    app_db = {}

    for item in raw_data:
        # E-Nummer bereinigen (E100, e100 -> E100)
        e_code = item.get('e_number', '').strip().upper()
        
        if not e_code: continue

        # Daten für die App extrahieren (nur das Wichtigste!)
        app_db[e_code] = {
            "n": item.get('name', ''), # Name
            "r": item.get('health_check', {}).get('rating', 'Unbekannt'), # Risiko
            "v": item.get('dietary_info', {}).get('is_vegan', False), # Vegan?
            "g": item.get('dietary_info', {}).get('is_gluten_free', False), # Glutenfrei?
            "d": item.get('intro_hook', '')[:150] + "..." # Kurze Beschreibung
        }

    # Speichern
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(app_db, f, ensure_ascii=False, separators=(',', ':')) # Minified für Speed
    
    print(f"✅ Fertig! {len(app_db)} Stoffe in '{OUTPUT_FILE}' optimiert.")
    print("   -> Diese Datei ist jetzt klein, schnell und perfekt für die App.")

if __name__ == "__main__":
    convert()