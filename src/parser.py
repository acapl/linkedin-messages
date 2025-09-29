# src/parser.py
import pandas as pd
from typing import Optional

def load_messages_csv(file_path: str) -> pd.DataFrame:
    """Load LinkedIn messages from single export CSV and return cleaned DataFrame"""

    # Load raw CSV
    df = pd.read_csv(file_path)

    # Normalize column names - headers (in case of inconsistencies)
    df.columns = df.columns.str.strip().str.upper()

    # Rename useful columns
    df = df.rename(columns={
        "CONVERSATION ID": "thread_id",
        "FROM": "sender",
        "TO": "recipient",
        "DATE": "timestamp",
        "CONTENT": "content",
    })

    # Convert timestamp string to datetime object
    df["timestamp"] = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")

    # Add additional useful columns from LinkedIn export
    if "SENDER PROFILE URL" in df.columns:
        df = df.rename(columns={"SENDER PROFILE URL": "sender_profile_url"})
    if "RECIPIENT PROFILE URLS" in df.columns:
        df = df.rename(columns={"RECIPIENT PROFILE URLS": "recipient_profile_urls"})
    if "CONVERSATION TITLE" in df.columns:
        df = df.rename(columns={"CONVERSATION TITLE": "conversation_title"})
    if "ATTACHMENTS" in df.columns:
        df = df.rename(columns={"ATTACHMENTS": "attachments"})

    # Remove rows with missing essential data
    df = df.dropna(subset=['thread_id', 'sender', 'content'])

    # Sort by thread and timestamp for proper conversation flow
    df = df.sort_values(['thread_id', 'timestamp'])

    return df

def validate_csv_structure(file_path: str) -> bool:
    """Validate that the CSV has the required LinkedIn export structure"""
    try:
        df = pd.read_csv(file_path, nrows=1)
        required_columns = ["CONVERSATION ID", "FROM", "TO", "DATE", "CONTENT"]
        df.columns = df.columns.str.strip().str.upper()

        for col in required_columns:
            if col not in df.columns:
                print(f"Missing required column: {col}")
                return False
        return True
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return False
