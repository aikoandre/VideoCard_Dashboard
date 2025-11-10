# scripts/update_passmark_scores.py

import requests
from bs4 import BeautifulSoup
import mysql.connector
import sys
import re
import time
import os
import json # New import for our map file

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

# --- 1. Get Cards from OUR Database (Unchanged) ---
def get_cards_from_db(connection):
    """
    Fetches all cards from our video_cards table that
    don't have a PassMark score yet.
    Returns a list of tuples: [(card_id, tpu_model_name), ...]
    """
    cards_to_update = []
    cursor = connection.cursor()
    try:
        query = "SELECT card_id, tpu_model_name FROM video_cards WHERE passmark_g3d_score IS NULL"
        cursor.execute(query)
        cards_to_update = cursor.fetchall()
        print(f"Found {len(cards_to_update)} cards in our database that need a PassMark score.")
        return cards_to_update
    except mysql.connector.Error as err:
        print(f"Error fetching cards from DB: {err}")
        return []
    finally:
        cursor.close()

# --- 2. Scrape PassMark for ALL Scores (Unchanged) ---
def scrape_passmark_master_list():
    """
    Scrapes the PassMark list page ONCE to get all scores.
    Returns a dictionary: {"geforce rtx 3060": 16782, ...} (all lowercase)
    """
    url = "https://www.videocardbenchmark.net/gpu_list.php"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"}
    
    score_dict = {}
    print(f"\nFetching PassMark master score list from {url}...")
    
    try:
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Error: Failed to fetch PassMark page, status {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', id='cputable')
        if not table:
            print("Error: Could not find table with id='cputable'.")
            return None
            
        rows = table.find('tbody').find_all('tr')
        
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 2:
                card_name = cells[0].get_text(strip=True)
                score_text = cells[1].get_text(strip=True)
                
                if card_name and score_text:
                    try:
                        score = int(score_text.replace(',', ''))
                        score_dict[card_name.lower()] = score
                    except ValueError:
                        pass
                        
        print(f"✅ Successfully parsed {len(score_dict)} scores from PassMark.")
        return score_dict

    except Exception as e:
        print(f"Error parsing PassMark HTML: {e}")
        return None

# --- 3. Update ONE Card in DB (Unchanged) ---
def update_card_score(connection, card_id, score):
    """
    Runs the UPDATE command to add the score to the card's row.
    """
    query = "UPDATE video_cards SET passmark_g3d_score = %s WHERE card_id = %s"
    cursor = connection.cursor()
    try:
        cursor.execute(query, (score, card_id))
        connection.commit()
        print(f"  > ✅ Updated score for card_id {card_id} to {score}")
    except mysql.connector.Error as err:
        print(f"  > ❌ Error updating score for card_id {card_id}: {err}")
        connection.rollback()
    finally:
        cursor.close()

# --- 4. Load the Name Map ---
def load_name_map(filepath):
    """Loads the JSON file mapping TPU names to PassMark names."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            name_map = json.load(f)
        print(f"Successfully loaded {len(name_map)} name mappings from '{filepath}'.")
        return name_map
    except FileNotFoundError:
        print(f"❌ CRITICAL ERROR: Could not find '{filepath}'")
        return None
    except json.JSONDecodeError:
        print(f"❌ CRITICAL ERROR: '{filepath}' contains invalid JSON. Please check it.")
        return None

# --- Main Execution (MODIFIED) ---
def main():
    script_dir = os.path.dirname(os.path.realpath(__file__))
    map_filepath = os.path.join(script_dir, "graphic_card_list.json")
    
    db_conn = create_db_connection()
    
    # 1. Load our "translator" map
    name_map = load_name_map(map_filepath)
    if not name_map:
        print("Halting: Cannot proceed without name map.")
        db_conn.close()
        return

    # 2. Get our list of cards
    cards_to_update = get_cards_from_db(db_conn)
    if not cards_to_update:
        print("No cards need updating. Exiting.")
        db_conn.close()
        return

    # 3. Get the master score list from PassMark
    passmark_scores = scrape_passmark_master_list()
    if not passmark_scores:
        print("Could not fetch PassMark scores. Exiting.")
        db_conn.close()
        return
        
    print("\n--- Matching and Updating Scores ---")
    
    # 4. Loop, Match, and Update
    for card in cards_to_update:
        card_id, tpu_model_name = card
        print(f"Processing: {tpu_model_name} (ID: {card_id})")
        
        # 4a. Find the PassMark name from our map
        if tpu_model_name not in name_map:
            print(f"  > ❌ No mapping found for '{tpu_model_name}' in passmark_name_map.json. Skipping.")
            continue
            
        passmark_name = name_map[tpu_model_name].lower()
        
        # 4b. Find that name in the scraped score list
        if passmark_name in passmark_scores:
            found_score = passmark_scores[passmark_name]
            print(f"  > Found match: '{tpu_model_name}' -> '{passmark_name}' -> Score: {found_score}")
            # 4c. Update the DB
            update_card_score(db_conn, card_id, found_score)
        else:
            print(f"  > ❌ Mapped name '{passmark_name}' not found in PassMark's list. Skipping.")
        
    db_conn.close()
    print("\n--- PassMark score update finished. ---")


if __name__ == "__main__":
    main()