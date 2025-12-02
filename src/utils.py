# src/utils.py
import pandas as pd
import os

def get_data_path():
    """
    Returns the path to the CSV data file.
    Works both locally and on Streamlit Cloud.
    
    Why this function exists:
    - When running locally: python is in 'src/' folder
    - When running on Streamlit Cloud: python is in root folder
    - This function handles both cases automatically
    """
    # Get the directory where this script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to project root, then into 'data' folder
    project_root = os.path.dirname(current_dir)
    data_path = os.path.join(project_root, 'data', 'video_cards.csv')
    
    return data_path

def carregar_dados():
    """
    Loads video card data from a CSV file into a Pandas DataFrame.
    
    This is our new "source of truth" - a simple CSV file that:
    - Requires no database server
    - Works on Streamlit Cloud
    - Can be updated by committing changes to GitHub
    """
    data_path = get_data_path()
    print(f"Attempting to load data from: {data_path}")
    
    try:
        # pd.read_csv reads a CSV file and returns a DataFrame
        # Much simpler than connecting to a database!
        df = pd.read_csv(data_path)
        
        print(f"✅ Successfully loaded {len(df)} rows from CSV.")
        return df
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find data file at {data_path}")
        return pd.DataFrame()
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return pd.DataFrame()