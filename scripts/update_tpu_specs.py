# scripts/update_tpu_specs.py

import requests
from bs4 import BeautifulSoup
import mysql.connector
import sys
import re
import time
import os
import urllib.parse
import json  # Import for JSON file

# --- Database Connection Function (Unchanged) ---
def create_db_connection():
    """Establishes a connection to the MySQL database."""
    try:
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="79864876",  # <-- IMPORTANT: CHANGE THIS
            database="gpu_dashboard"
        )
        print("✅ Database connection successful!")
        return connection
    except mysql.connector.Error as err:
        print(f"Error connecting to database: {err}")
        sys.exit(1)

# --- Load Card List from JSON File ---
def load_cards_from_json(filepath):
    """
    Reads the JSON file and returns a list of TPU card names (keys).
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            card_map = json.load(f)
        
        cards = list(card_map.keys())
        
        if not cards:
            print(f"Warning: '{filepath}' is empty.")
            return []
        
        print(f"Successfully loaded {len(cards)} cards from '{filepath}'.")
        return cards
    except FileNotFoundError:
        print(f"❌ CRITICAL ERROR: Could not find card list file at '{filepath}'")
        return []
    except json.JSONDecodeError:
        print(f"❌ CRITICAL ERROR: '{filepath}' contains invalid JSON.")
        return []

# --- Parse Memory String (Unchanged) ---
def parse_memory_string(mem_str):
    """
    Parses '12 GB / GDDR6 / 192 bit' into vram and mem_type
    """
    try:
        parts = mem_str.split(' / ')
        vram = parts[0].strip()       # "12 GB"
        mem_type = parts[1].strip()   # "GDDR6"
        return vram, mem_type
    except Exception:
        print(f"  > Warning: Could not parse memory string: {mem_str}")
        return "N/A", "N/A"

# --- Database Insertion Function (Unchanged) ---
def insert_card_data(connection, card_data_tuple):
    """
    Inserts or updates a card in the video_cards table.
    Tuple is: (tpu_model_name, vram, bus_interface, memory_type)
    """
    query = """
    INSERT INTO video_cards (tpu_model_name, vram, bus_interface, memory_type)
    VALUES (%s, %s, %s, %s)
    ON DUPLICATE KEY UPDATE
    bus_interface = VALUES(bus_interface),
    memory_type = VALUES(memory_type);
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, card_data_tuple)
        connection.commit()
        print(f"  > ✅ Successfully inserted/updated {card_data_tuple[0]} in database.\n")
    except mysql.connector.Error as err:
        print(f"  > ❌ Error inserting data: {err}\n")
        connection.rollback()
    finally:
        cursor.close()

# --- Scrape TPU Search API (Unchanged) ---
def find_spec_from_search(card_name_to_find):
    """
    Uses the search API to find the specs for a *specific* card name.
    Includes retry logic for rate limiting.
    """
    
    query = urllib.parse.quote_plus(card_name_to_find)
    url = f"https://www.techpowerup.com/gpu-specs/?q={query}&ajax"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.techpowerup.com/gpu-specs/"
    }
    
    print(f"Processing: {card_name_to_find}...")
    print(f"  > Calling API: {url}")
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 429:
                retry_count += 1
                if retry_count < max_retries:
                    wait_time = 30 * retry_count  # Wait 30, 60, 90 seconds
                    print(f"  > ⚠️ Rate limited (429). Waiting {wait_time} seconds before retry {retry_count}/{max_retries}...")
                    time.sleep(wait_time)
                    continue
                else:
                    print(f"  > ❌ Error: Max retries reached. Server is rate-limiting. Try again later.")
                    return None
            
            if response.status_code != 200:
                print(f"  > Error: API request failed with status {response.status_code}")
                return None
            
            break  # Success, exit retry loop
            
        except requests.exceptions.Timeout:
            print(f"  > Error: Request timed out")
            return None
        except requests.exceptions.RequestException as e:
            print(f"  > Error: Request failed: {e}")
            return None
    
    try:
        
        response_json = response.json()
        html_string = response_json['list']
        soup = BeautifulSoup(html_string, 'html.parser')
        
        print(f"  > Parsing search results...")
        
        # The HTML contains BOTH desktop table and mobile divs
        # Use the mobile structure as it's easier to parse (divs with spans)
        mobile_items = soup.find_all('div', class_='items-mobile--item')
        
        if not mobile_items:
            print(f"  > Error: No mobile items found.")
            return None
        
        print(f"  > Found {len(mobile_items)} card(s)")
        
        matches = []
        search_terms = card_name_to_find.strip().lower()
        
        for idx, item in enumerate(mobile_items, 1):
            # Find the card name
            name_link = item.find('a', class_='item-name')
            if not name_link:
                continue
            
            found_name = name_link.get_text(strip=True)
            
            # Find property rows
            prop_rows = item.find_all('div', class_='item-properties-row')
            
            bus_interface = "N/A"
            mem_string = "N/A"
            
            # Parse each property row - spans contain the data
            for prop_row in prop_rows:
                spans = prop_row.find_all('span')
                for span in spans:
                    text = span.get_text(strip=True)
                    
                    # Memory format: "4 GB / GDDR6 / 128 bit"
                    if 'GB' in text and '/' in text and ('GDDR' in text or 'HBM' in text or 'DDR' in text):
                        mem_string = text
                    
                    # Bus format: "PCIe 3.0 x16"
                    if 'PCIe' in text and 'x' in text:
                        bus_interface = text
            
            if idx <= 5:
                print(f"     [{idx}] '{found_name}'")
                print(f"           Bus: {bus_interface}, Memory: {mem_string}")
            
            found_name_lower = found_name.lower()
            
            # Try exact match
            if found_name_lower == search_terms:
                print(f"  > ✓ Found exact match!")
                vram, mem_type = parse_memory_string(mem_string)
                
                return {
                    "name": found_name,
                    "bus": bus_interface,
                    "vram": vram,
                    "mem_type": mem_type
                }
            
            # Collect fuzzy matches
            search_base = search_terms.replace(' gddr6', '').replace(' gddr5', '').replace(' gddr5x', '').replace(' gb', '').strip()
            found_base = found_name_lower.replace(' gddr6', '').replace(' gddr5', '').replace(' gddr5x', '').replace(' gb', '').strip()
            
            if search_base in found_base or found_base in search_base:
                matches.append({
                    "name": found_name,
                    "bus": bus_interface,
                    "mem_string": mem_string,
                    "similarity": len(set(search_base.split()) & set(found_base.split()))
                })
        
        # Use best fuzzy match
        if matches:
            matches.sort(key=lambda x: x['similarity'], reverse=True)
            best_match = matches[0]
            
            print(f"  > ✓ Found fuzzy match: '{best_match['name']}'")
            
            vram, mem_type = parse_memory_string(best_match['mem_string'])
            
            return {
                "name": card_name_to_find,
                "bus": best_match['bus'],
                "vram": vram,
                "mem_type": mem_type
            }
        
        print(f"  > ✗ Error: Could not find match for '{card_name_to_find}'")
        return None

    except Exception as e:
        print(f"  > ✗ Error during scraping/parsing: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- Main Execution (MODIFIED) ---
def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    
    # Use the JSON file as the source of card names
    card_list_filepath = os.path.join(script_dir, "graphic_card_list.json")
    
    CARDS_TO_FIND = load_cards_from_json(card_list_filepath)
    if not CARDS_TO_FIND:
        print("Halting script: No cards to process.")
        return
    
    db_conn = create_db_connection()
    
    # Check which cards already have data
    cursor = db_conn.cursor()
    cursor.execute("SELECT tpu_model_name FROM video_cards WHERE bus_interface IS NOT NULL AND bus_interface != ''")
    existing_cards = set(row[0] for row in cursor.fetchall())
    cursor.close()
    
    print(f"\n📊 Found {len(existing_cards)} cards already in database with specs.")
    
    cards_to_process = [card for card in CARDS_TO_FIND if card not in existing_cards]
    
    if not cards_to_process:
        print("✅ All cards already have specs! Nothing to do.")
        db_conn.close()
        return
    
    print(f"📝 Will process {len(cards_to_process)} remaining cards.\n")

    for idx, card_name in enumerate(cards_to_process, 1):
        print(f"\n[{idx}/{len(cards_to_process)}] Processing: {card_name}")
        specs = find_spec_from_search(card_name)
        
        if specs:
            data_tuple = (
                specs['name'],
                specs['vram'],
                specs['bus'],
                specs['mem_type']
            )
            insert_card_data(db_conn, data_tuple)
        
        # Be respectful to the server - wait 12-15 seconds between requests
        if idx < len(cards_to_process):  # Don't sleep after the last card
            wait_time = 15  # Increased delay to 15 seconds
            print(f"  > Waiting {wait_time} seconds before next request...")
            time.sleep(wait_time)

    db_conn.close()
    print("\n--- All cards processed. Script finished. ---")
if __name__ == "__main__":
    main()