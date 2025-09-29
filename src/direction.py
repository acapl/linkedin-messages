# src/direction.py
import pandas as pd
from typing import Tuple, Set

def identify_user_profile(df: pd.DataFrame) -> str:
    """
    Identify the user's LinkedIn profile name from the dataset.
    Returns the most frequent sender name (assuming user sends more than receives).
    """
    sender_counts = df['sender'].value_counts()

    # The user is likely the person who appears most frequently as sender
    # in their own message export
    user_name = sender_counts.index[0]

    print(f"🔍 Identified user profile: {user_name}")
    print(f"📊 {user_name} sent {sender_counts.iloc[0]} messages")

    return user_name

def classify_message_direction(df: pd.DataFrame, user_name: str = None) -> pd.DataFrame:
    """
    Add direction classification to messages (inbound/outbound).

    Args:
        df: DataFrame with parsed LinkedIn messages
        user_name: Optional user name override. If None, will auto-detect.

    Returns:
        DataFrame with added 'direction' and 'contact_person' columns
    """
    df = df.copy()

    # Auto-detect user name if not provided
    if user_name is None:
        user_name = identify_user_profile(df)

    # Classify message direction
    df['direction'] = df['sender'].apply(
        lambda sender: 'outbound' if sender == user_name else 'inbound'
    )

    # Identify contact person (the other person in each thread)
    df['contact_person'] = df.apply(
        lambda row: row['recipient'] if row['sender'] == user_name else row['sender'],
        axis=1
    )

    return df

def get_conversation_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate a summary of conversations by contact person.

    Returns:
        DataFrame with conversation statistics per contact
    """
    # Group by contact person and thread
    contact_stats = []

    for contact in df['contact_person'].unique():
        contact_df = df[df['contact_person'] == contact]

        # Get all threads with this contact
        threads = contact_df['thread_id'].unique()

        total_messages = len(contact_df)
        outbound_messages = len(contact_df[contact_df['direction'] == 'outbound'])
        inbound_messages = len(contact_df[contact_df['direction'] == 'inbound'])

        # Calculate if contact responded
        has_response = inbound_messages > 0

        # Get date range
        first_message = contact_df['timestamp'].min()
        last_message = contact_df['timestamp'].max()

        # Get conversation thread count
        thread_count = len(threads)

        contact_stats.append({
            'contact_person': contact,
            'total_messages': total_messages,
            'outbound_messages': outbound_messages,
            'inbound_messages': inbound_messages,
            'thread_count': thread_count,
            'has_response': has_response,
            'first_contact': first_message,
            'last_contact': last_message,
            'response_rate': inbound_messages / outbound_messages if outbound_messages > 0 else 0
        })

    summary_df = pd.DataFrame(contact_stats)

    # Sort by last contact date (most recent first)
    summary_df = summary_df.sort_values('last_contact', ascending=False)

    return summary_df

def analyze_response_patterns(df: pd.DataFrame) -> dict:
    """
    Analyze response patterns across all conversations.

    Returns:
        Dictionary with response pattern statistics
    """
    summary = get_conversation_summary(df)

    total_contacts = len(summary)
    contacts_who_responded = len(summary[summary['has_response']])
    overall_response_rate = contacts_who_responded / total_contacts if total_contacts > 0 else 0

    # Calculate average response rate (weighted by outbound messages)
    weighted_response_rate = (
        summary['inbound_messages'].sum() / summary['outbound_messages'].sum()
        if summary['outbound_messages'].sum() > 0 else 0
    )

    # Find ghosted contacts (outbound messages but no response)
    ghosted_contacts = summary[
        (summary['outbound_messages'] > 0) & (summary['inbound_messages'] == 0)
    ]

    return {
        'total_contacts': total_contacts,
        'contacts_who_responded': contacts_who_responded,
        'contacts_who_ghosted': len(ghosted_contacts),
        'overall_response_rate': overall_response_rate,
        'weighted_response_rate': weighted_response_rate,
        'avg_messages_per_contact': summary['total_messages'].mean(),
        'avg_outbound_per_contact': summary['outbound_messages'].mean(),
        'most_active_contact': summary.loc[summary['total_messages'].idxmax(), 'contact_person'],
        'ghosted_contacts': ghosted_contacts['contact_person'].tolist()
    }