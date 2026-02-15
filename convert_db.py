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
        print("❌ Fehler: Datei nicht gefunden.")
        return

    app_db = {}

    for item in raw_data:
        e_code = item.get('e_number', '').strip().upper()
        if not e_code: continue

        # 1. Name sicherstellen
        name = item.get('name', '')
        if isinstance(name, list): name = " ".join([str(x) for x in name])
        name = str(name)

        # 2. Rating sicherstellen
        rating = item.get('health_check', {}).get('rating', 'Unbekannt')
        if isinstance(rating, list): rating = rating[0] if rating else 'Unbekannt'
        rating = str(rating)

        # 3. Intro Hook sicherstellen (HIER WAR DER FEHLER)
        raw_hook = item.get('intro_hook', '')
        if isinstance(raw_hook, list):
            # Falls es eine Liste ist ["Satz 1", "Satz 2"] -> "Satz 1 Satz 2"
            intro = " ".join([str(x) for x in raw_hook])
        else:
            intro = str(raw_hook)

        # Jetzt können wir sicher schneiden, weil 'intro' garantiert ein String ist
        short_desc = intro[:150] + "..." if len(intro) > 150 else intro

        app_db[e_code] = {
            "n": name,
            "r": rating,
            "v": item.get('dietary_info', {}).get('is_vegan', False),
            "g": item.get('dietary_info', {}).get('is_gluten_free', False),
            "d": short_desc
        }

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(app_db, f, ensure_ascii=False, separators=(',', ':'))
    
    print(f"✅ Fertig! {len(app_db)} Einträge konvertiert.")

if __name__ == "__main__":
    convert()
