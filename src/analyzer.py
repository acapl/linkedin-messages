# src/analyzer.py
import pandas as pd
import re
from datetime import timedelta
from typing import Dict, List, Tuple
from textblob import TextBlob

def analyze_message_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add sentiment analysis to messages using TextBlob.

    Args:
        df: DataFrame with message content

    Returns:
        DataFrame with added sentiment columns
    """
    df = df.copy()

    print("🧠 Analyzing message sentiment...")

    def get_sentiment(text):
        if pd.isna(text) or text.strip() == "":
            return 0, 0

        try:
            blob = TextBlob(str(text))
            return blob.sentiment.polarity, blob.sentiment.subjectivity
        except:
            return 0, 0

    sentiment_scores = df['content'].apply(get_sentiment)
    df['sentiment_polarity'] = [score[0] for score in sentiment_scores]
    df['sentiment_subjectivity'] = [score[1] for score in sentiment_scores]

    # Classify sentiment
    df['sentiment_label'] = df['sentiment_polarity'].apply(
        lambda x: 'positive' if x > 0.1 else ('negative' if x < -0.1 else 'neutral')
    )

    return df

def calculate_message_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate various message metrics (length, word count, etc.).

    Args:
        df: DataFrame with message content

    Returns:
        DataFrame with added metric columns
    """
    df = df.copy()

    print("📏 Calculating message metrics...")

    # Basic length metrics
    df['message_length'] = df['content'].str.len()
    df['word_count'] = df['content'].str.split().str.len()

    # Count question marks (engagement indicator)
    df['question_count'] = df['content'].str.count(r'\?')

    # Count exclamation marks (enthusiasm indicator)
    df['exclamation_count'] = df['content'].str.count(r'!')

    # Check for URLs (LinkedIn profiles, external links)
    df['has_url'] = df['content'].str.contains(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
        regex=True, na=False
    )

    # Check for LinkedIn profile mentions
    df['has_linkedin_profile'] = df['content'].str.contains(
        r'linkedin\.com/in/', regex=True, na=False
    )

    # Check for common greeting patterns
    greeting_patterns = [
        r'\bhi\b', r'\bhello\b', r'\bhey\b', r'\bthanks\b', r'\bthank you\b',
        r'\bhope\b', r'\bgood morning\b', r'\bgood afternoon\b'
    ]
    df['has_greeting'] = df['content'].str.contains(
        '|'.join(greeting_patterns), regex=True, case=False, na=False
    )

    return df

def detect_replies_and_response_times(df: pd.DataFrame) -> pd.DataFrame:
    """
    Detect replies and calculate response times within conversation threads.

    Args:
        df: DataFrame with messages sorted by thread and timestamp

    Returns:
        DataFrame with reply detection and timing columns
    """
    df = df.copy().sort_values(['thread_id', 'timestamp'])

    print("⏱️  Detecting replies and response times...")

    # Initialize new columns
    df['is_reply'] = False
    df['is_first_message'] = False
    df['is_outbound_initiated'] = False
    df['response_time_hours'] = pd.NaT
    df['previous_sender'] = None

    # Get user name (assuming it's already identified from direction classification)
    user_name = df[df['direction'] == 'outbound']['sender'].iloc[0]

    for thread_id in df['thread_id'].unique():
        thread_df = df[df['thread_id'] == thread_id].copy()

        if len(thread_df) == 0:
            continue

        # Mark first message in thread
        first_idx = thread_df.index[0]
        df.loc[first_idx, 'is_first_message'] = True

        # Check if this thread was initiated by the user (outbound)
        first_message_sender = thread_df.iloc[0]['sender']
        is_outbound_thread = (first_message_sender == user_name)

        # Mark all messages in this thread with outbound initiation flag
        for idx in thread_df.index:
            df.loc[idx, 'is_outbound_initiated'] = is_outbound_thread

        # Process subsequent messages
        for i, (idx, row) in enumerate(thread_df.iterrows()):
            if i == 0:
                continue

            prev_idx = thread_df.index[i-1]
            prev_row = thread_df.iloc[i-1]

            # Check if this is a reply (different sender than previous)
            if row['sender'] != prev_row['sender']:
                df.loc[idx, 'is_reply'] = True
                df.loc[idx, 'previous_sender'] = prev_row['sender']

                # Calculate response time
                time_diff = row['timestamp'] - prev_row['timestamp']
                df.loc[idx, 'response_time_hours'] = float(time_diff.total_seconds() / 3600)

    return df

def analyze_conversation_flow(df: pd.DataFrame) -> Dict:
    """
    Analyze conversation flow patterns and reply dynamics.

    Args:
        df: DataFrame with analyzed messages

    Returns:
        Dictionary with conversation flow insights
    """
    print("🔄 Analyzing conversation flow patterns...")

    # Overall reply statistics
    total_messages = len(df)
    total_replies = len(df[df['is_reply'] == True])
    total_first_messages = len(df[df['is_first_message'] == True])

    # Response time analysis
    response_times = df[df['is_reply'] == True]['response_time_hours'].dropna()

    # Analyze by direction
    outbound_messages = df[df['direction'] == 'outbound']
    inbound_messages = df[df['direction'] == 'inbound']

    # Quick response analysis (< 1 hour)
    quick_responses = response_times[response_times < 1]

    # Find conversation starters vs replies
    outbound_first_messages = df[
        (df['direction'] == 'outbound') & (df['is_first_message'] == True)
    ]

    # Analyze message length by direction
    outbound_avg_length = outbound_messages['message_length'].mean()
    inbound_avg_length = inbound_messages['message_length'].mean()

    # Sentiment analysis by direction
    outbound_avg_sentiment = outbound_messages['sentiment_polarity'].mean()
    inbound_avg_sentiment = inbound_messages['sentiment_polarity'].mean()

    return {
        'total_messages': total_messages,
        'total_replies': total_replies,
        'total_first_messages': total_first_messages,
        'reply_rate': total_replies / total_first_messages if total_first_messages > 0 else 0,

        'avg_response_time_hours': response_times.mean() if len(response_times) > 0 else 0,
        'median_response_time_hours': response_times.median() if len(response_times) > 0 else 0,
        'quick_response_count': len(quick_responses),
        'quick_response_rate': len(quick_responses) / len(response_times) if len(response_times) > 0 else 0,

        'outbound_message_count': len(outbound_messages),
        'inbound_message_count': len(inbound_messages),
        'outbound_avg_length': outbound_avg_length,
        'inbound_avg_length': inbound_avg_length,

        'outbound_avg_sentiment': outbound_avg_sentiment,
        'inbound_avg_sentiment': inbound_avg_sentiment,

        'conversation_starters': len(outbound_first_messages),
        'conversations_initiated': len(outbound_first_messages)
    }

def find_top_performing_messages(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """
    Find top performing outbound messages (those that received replies).

    Args:
        df: DataFrame with analyzed messages
        limit: Number of top messages to return

    Returns:
        DataFrame with top performing messages
    """
    print("🎯 Finding top performing message templates...")

    # Get outbound messages that received replies
    outbound_with_replies = df[
        (df['direction'] == 'outbound') &
        (df['thread_id'].isin(df[df['is_reply'] == True]['thread_id']))
    ].copy()

    if len(outbound_with_replies) == 0:
        return pd.DataFrame()

    # Score messages based on various factors
    outbound_with_replies['performance_score'] = (
        (outbound_with_replies['sentiment_polarity'] + 1) * 2 +  # Positive sentiment
        (outbound_with_replies['has_greeting'].astype(int)) * 1 +  # Has greeting
        (outbound_with_replies['question_count'] * 0.5) +  # Asks questions
        (outbound_with_replies['word_count'] / 100) * 0.1  # Length factor
    )

    # Get top performers
    top_messages = outbound_with_replies.nlargest(limit, 'performance_score')

    return top_messages[['content', 'contact_person', 'sentiment_polarity',
                        'message_length', 'word_count', 'performance_score',
                        'timestamp', 'has_greeting', 'question_count']]