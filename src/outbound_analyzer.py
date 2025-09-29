# src/outbound_analyzer.py
import pandas as pd
import re
from typing import Dict, List, Tuple
from collections import Counter

def analyze_outbound_performance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Analyze outbound messages and their performance - focused on conversation starters.

    Args:
        df: DataFrame with analyzed messages

    Returns:
        DataFrame with outbound message performance analysis
    """

    print("🎯 Analyzing outbound message performance...")

    # Get ONLY messages from conversations that YOU initiated
    # This excludes replies you sent to conversations others started
    outbound_df = df[
        (df['direction'] == 'outbound') &
        (df['is_outbound_initiated'] == True)
    ].copy()

    print(f"📊 Found {len(outbound_df)} messages in conversations YOU started")

    # For each outbound message, check if it got a response
    outbound_performance = []

    for idx, msg in outbound_df.iterrows():
        thread_id = msg['thread_id']
        msg_timestamp = msg['timestamp']

        # Find if there was a response to this message in the same thread
        thread_messages = df[df['thread_id'] == thread_id].copy()
        thread_messages = thread_messages.sort_values('timestamp')

        # Get messages after this outbound message
        responses = thread_messages[
            (thread_messages['timestamp'] > msg_timestamp) &
            (thread_messages['direction'] == 'inbound')
        ]

        got_response = len(responses) > 0

        # If got response, calculate response time
        response_time_hours = None
        responder = None
        if got_response:
            first_response = responses.iloc[0]
            response_time_hours = (first_response['timestamp'] - msg_timestamp).total_seconds() / 3600
            responder = first_response['sender']

        # Determine if this is a conversation starter (first message in thread AND you started it)
        is_conversation_starter = msg['is_first_message'] and msg['is_outbound_initiated']

        # Determine message type based on content patterns
        content_lower = str(msg['content']).lower()

        message_type = "other"
        if any(word in content_lower for word in ['thanks', 'thank you']):
            message_type = "thank_you"
        elif any(word in content_lower for word in ['hi ', 'hello', 'hey']):
            message_type = "greeting"
        elif '?' in msg['content']:
            message_type = "question"
        elif any(word in content_lower for word in ['follow up', 'following up']):
            message_type = "follow_up"
        elif any(word in content_lower for word in ['opportunity', 'position', 'role', 'job']):
            message_type = "opportunity_inquiry"
        elif any(word in content_lower for word in ['connect', 'connection', 'network']):
            message_type = "connection_request"

        outbound_performance.append({
            'message_id': idx,
            'thread_id': thread_id,
            'timestamp': msg['timestamp'],
            'contact_person': msg['contact_person'],
            'content': msg['content'],
            'message_length': msg['message_length'],
            'word_count': msg['word_count'],
            'sentiment_polarity': msg['sentiment_polarity'],
            'got_response': got_response,
            'response_time_hours': response_time_hours,
            'responder': responder,
            'is_conversation_starter': is_conversation_starter,
            'message_type': message_type,
            'has_greeting': msg.get('has_greeting', False),
            'question_count': msg.get('question_count', 0),
            'has_url': msg.get('has_url', False),
            'has_linkedin_profile': msg.get('has_linkedin_profile', False)
        })

    performance_df = pd.DataFrame(outbound_performance)

    # Calculate performance score
    performance_df['performance_score'] = (
        performance_df['got_response'].astype(int) * 10 +  # Got response is most important
        (performance_df['sentiment_polarity'] + 1) * 2 +   # Positive sentiment
        performance_df['has_greeting'].astype(int) * 1 +   # Has greeting
        (performance_df['question_count'] * 0.5) +         # Asks questions
        (performance_df['word_count'] / 50) * 0.1          # Reasonable length
    )

    return performance_df

def get_conversation_starters_analysis(outbound_df: pd.DataFrame) -> Dict:
    """
    Analyze conversation starter performance specifically.
    """

    starters = outbound_df[outbound_df['is_conversation_starter']].copy()

    if len(starters) == 0:
        return {}

    total_starters = len(starters)
    successful_starters = len(starters[starters['got_response']])
    starter_response_rate = successful_starters / total_starters

    # Analyze by message type - fix the math
    type_stats = []

    for msg_type in starters['message_type'].unique():
        type_msgs = starters[starters['message_type'] == msg_type]
        total_count = len(type_msgs)
        response_count = type_msgs['got_response'].sum()
        response_rate = response_count / total_count if total_count > 0 else 0

        # Only calculate response time for messages that got responses
        responded_msgs = type_msgs[type_msgs['got_response'] == True]
        avg_response_time = responded_msgs['response_time_hours'].mean() if len(responded_msgs) > 0 else 0

        type_stats.append({
            'message_type': msg_type,
            'got_response_count': total_count,
            'got_response_sum': response_count,
            'got_response_mean': response_rate,
            'response_time_hours_mean': avg_response_time,
            'sentiment_polarity_mean': type_msgs['sentiment_polarity'].mean(),
            'message_length_mean': type_msgs['message_length'].mean()
        })

    type_performance = pd.DataFrame(type_stats)

    # Best performing starters
    best_starters = starters[starters['got_response']].nlargest(10, 'performance_score')

    return {
        'total_conversation_starters': total_starters,
        'successful_starters': successful_starters,
        'starter_response_rate': starter_response_rate,
        'type_performance': type_performance,
        'best_starters': best_starters,
        'avg_starter_length': starters['message_length'].mean(),
        'avg_starter_sentiment': starters['sentiment_polarity'].mean()
    }

def get_message_templates(outbound_df: pd.DataFrame, min_occurrences: int = 2) -> pd.DataFrame:
    """
    Extract and analyze message templates/patterns that you use frequently.
    """

    print("📝 Extracting message templates and patterns...")

    # Get successful messages (those that got responses)
    successful_messages = outbound_df[outbound_df['got_response']].copy()

    if len(successful_messages) == 0:
        return pd.DataFrame()

    # Extract common opening patterns (first 50 characters)
    openings = successful_messages['content'].apply(lambda x: str(x)[:50].strip())
    opening_counts = openings.value_counts()

    # Extract common phrases (simple approach)
    all_content = ' '.join(successful_messages['content'].astype(str))

    # Find common greeting patterns
    greeting_patterns = [
        r'Hi [A-Z][a-z]+',
        r'Hello [A-Z][a-z]+',
        r'Hey [A-Z][a-z]+',
        r'Thanks [A-Z][a-z]+',
        r'Thank you [A-Z][a-z]+',
    ]

    pattern_matches = {}
    for pattern in greeting_patterns:
        matches = re.findall(pattern, all_content)
        if matches:
            pattern_matches[pattern] = len(matches)

    # Analyze template performance
    templates = []

    # Group similar messages by first 30 characters
    successful_messages['template_key'] = successful_messages['content'].apply(
        lambda x: str(x)[:30].lower().strip()
    )

    template_groups = successful_messages.groupby('template_key')

    for template_key, group in template_groups:
        if len(group) >= min_occurrences:  # Only templates used multiple times
            templates.append({
                'template_preview': template_key,
                'usage_count': len(group),
                'response_rate': group['got_response'].mean(),
                'avg_response_time': group['response_time_hours'].mean(),
                'avg_sentiment': group['sentiment_polarity'].mean(),
                'avg_length': group['message_length'].mean(),
                'example_full_message': group.iloc[0]['content']
            })

    templates_df = pd.DataFrame(templates)
    if len(templates_df) > 0:
        templates_df = templates_df.sort_values(['response_rate', 'usage_count'], ascending=[False, False])

    return templates_df

def analyze_failed_outreach(outbound_df: pd.DataFrame) -> Dict:
    """
    Analyze messages that didn't get responses to identify patterns to avoid.
    """

    failed_messages = outbound_df[~outbound_df['got_response']].copy()

    if len(failed_messages) == 0:
        return {}

    # Analyze characteristics of failed messages
    failed_analysis = {
        'total_failed': len(failed_messages),
        'avg_failed_length': failed_messages['message_length'].mean(),
        'avg_failed_sentiment': failed_messages['sentiment_polarity'].mean(),
        'failed_by_type': failed_messages['message_type'].value_counts().to_dict(),
        'common_failed_starters': failed_messages[
            failed_messages['is_conversation_starter']
        ]['content'].apply(lambda x: str(x)[:50]).value_counts().head(5).to_dict()
    }

    return failed_analysis

def get_outbound_insights(outbound_df: pd.DataFrame) -> Dict:
    """
    Generate comprehensive insights about outbound messaging performance.
    Only includes messages from conversations YOU initiated.
    """

    total_outbound = len(outbound_df)
    successful_outbound = len(outbound_df[outbound_df['got_response']])
    overall_response_rate = successful_outbound / total_outbound if total_outbound > 0 else 0

    # Response time analysis
    responded_messages = outbound_df[outbound_df['got_response']].copy()

    if len(responded_messages) > 0:
        avg_response_time = responded_messages['response_time_hours'].mean()
        median_response_time = responded_messages['response_time_hours'].median()
        quick_responses = len(responded_messages[responded_messages['response_time_hours'] < 24])
        quick_response_rate = quick_responses / len(responded_messages)
    else:
        avg_response_time = median_response_time = quick_response_rate = 0
        quick_responses = 0

    # Message characteristics of successful vs failed
    successful = outbound_df[outbound_df['got_response']]
    failed = outbound_df[~outbound_df['got_response']]

    insights = {
        'total_outbound_messages': total_outbound,
        'successful_outbound_messages': successful_outbound,
        'overall_outbound_response_rate': overall_response_rate,
        'avg_response_time_hours': avg_response_time,
        'median_response_time_hours': median_response_time,
        'quick_responses_24h': quick_responses,
        'quick_response_rate_24h': quick_response_rate,

        # Message characteristics
        'successful_avg_length': successful['message_length'].mean() if len(successful) > 0 else 0,
        'failed_avg_length': failed['message_length'].mean() if len(failed) > 0 else 0,
        'successful_avg_sentiment': successful['sentiment_polarity'].mean() if len(successful) > 0 else 0,
        'failed_avg_sentiment': failed['sentiment_polarity'].mean() if len(failed) > 0 else 0,

        # Best performing characteristics
        'best_message_types': successful['message_type'].value_counts().head(3).to_dict() if len(successful) > 0 else {},
        'worst_message_types': failed['message_type'].value_counts().head(3).to_dict() if len(failed) > 0 else {},
    }

    return insights