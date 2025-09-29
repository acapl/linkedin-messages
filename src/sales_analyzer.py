# src/sales_analyzer.py
import pandas as pd
import re
from typing import Dict, List, Tuple
from difflib import SequenceMatcher
import numpy as np

def classify_sales_messages(df: pd.DataFrame) -> pd.DataFrame:
    """
    Classify messages as sales/business focused vs casual conversation.
    """

    print("💼 Classifying sales-focused messages...")

    df = df.copy()

    def is_sales_message(content):
        if pd.isna(content):
            return False

        content_lower = str(content).lower()

        # Sales keywords
        sales_keywords = [
            # Job/career related
            'opportunity', 'position', 'role', 'job', 'hire', 'hiring', 'candidate',
            'application', 'applied', 'resume', 'cv', 'interview',

            # Business/service related
            'business', 'company', 'client', 'customer', 'service', 'services',
            'consulting', 'consultant', 'help', 'assist', 'solution',
            'revenue', 'growth', 'arr', 'saas', 'sales', 'marketing',

            # Partnership/collaboration
            'partner', 'partnership', 'collaborate', 'collaboration', 'work together',
            'project', 'freelance', 'contract', 'contractor',

            # Meeting/demo requests
            'meeting', 'call', 'demo', 'presentation', 'discuss', 'chat',
            'schedule', 'available', 'time', 'calendar',

            # Value propositions
            'experience', 'expertise', 'skills', 'background', 'portfolio',
            'results', 'success', 'achieve', 'deliver', 'provide'
        ]

        # Count sales keywords
        sales_score = sum(1 for keyword in sales_keywords if keyword in content_lower)

        # Business context patterns
        business_patterns = [
            r'\$\d+[mk]?\s*(arr|revenue|million|thousand)',  # Revenue mentions
            r'\d+\+?\s*(years?|months?)\s*(experience|exp)',  # Experience
            r'(ceo|cto|founder|manager|director|lead)',  # Titles
            r'(startup|company|business|firm|agency)',  # Business entities
            r'b2b|saas|fintech|web3|crypto',  # Industries
        ]

        pattern_matches = sum(1 for pattern in business_patterns if re.search(pattern, content_lower))

        # Questions that sound like sales qualifying
        sales_questions = [
            r'are you (open|interested|available|looking)',
            r'would you (like|be interested|consider)',
            r'do you (need|want|have|work)',
            r'what (are you|do you|is your)',
            r'how (many|much|long|do you)'
        ]

        question_matches = sum(1 for pattern in sales_questions if re.search(pattern, content_lower))

        # Calculate final sales score
        total_score = sales_score + (pattern_matches * 2) + (question_matches * 1.5)

        return total_score >= 2  # Threshold for sales classification

    # Classify each message
    df['is_sales_message'] = df['content'].apply(is_sales_message)

    # Further classify sales message types
    def get_sales_type(content):
        if pd.isna(content):
            return 'other'

        content_lower = str(content).lower()

        if any(word in content_lower for word in ['job', 'position', 'role', 'hire', 'candidate', 'application']):
            return 'job_seeking'
        elif any(word in content_lower for word in ['service', 'help', 'consulting', 'solution', 'provide']):
            return 'service_offering'
        elif any(word in content_lower for word in ['partner', 'collaboration', 'work together', 'project']):
            return 'partnership'
        elif any(word in content_lower for word in ['meeting', 'call', 'demo', 'schedule', 'available']):
            return 'meeting_request'
        else:
            return 'business_general'

    # Only classify sales type for sales messages
    df['sales_type'] = df.apply(
        lambda row: get_sales_type(row['content']) if row['is_sales_message'] else 'non_sales',
        axis=1
    )

    sales_count = df['is_sales_message'].sum()
    total_count = len(df)

    print(f"📊 Found {sales_count} sales messages out of {total_count} total ({sales_count/total_count:.1%})")

    return df

def analyze_sales_performance(df: pd.DataFrame, outbound_performance_df: pd.DataFrame = None) -> Dict:
    """
    Analyze performance of sales-focused messages specifically.
    """

    print("💼 Analyzing sales message performance...")

    # If we have outbound performance data, use that, otherwise calculate responses manually
    if outbound_performance_df is not None and 'got_response' in outbound_performance_df.columns:
        # Merge sales classification with outbound performance data
        sales_messages = outbound_performance_df.merge(
            df[['is_sales_message', 'sales_type']].reset_index(),
            left_index=True, right_on='index', how='left'
        )
        sales_messages = sales_messages[sales_messages['is_sales_message'] == True]
    else:
        # Calculate responses manually for sales messages
        sales_messages = df[
            (df['is_sales_message'] == True) &
            (df['direction'] == 'outbound') &
            (df['is_outbound_initiated'] == True)
        ].copy()

        # Calculate if each message got a response
        sales_messages['got_response'] = False
        for idx, msg in sales_messages.iterrows():
            thread_id = msg['thread_id']
            msg_timestamp = msg['timestamp']

            # Find responses in the same thread after this message
            responses = df[
                (df['thread_id'] == thread_id) &
                (df['timestamp'] > msg_timestamp) &
                (df['direction'] == 'inbound')
            ]

            sales_messages.loc[idx, 'got_response'] = len(responses) > 0

    if len(sales_messages) == 0:
        return {}

    # Calculate response rates by sales type
    sales_performance = {}

    for sales_type in sales_messages['sales_type'].unique():
        if sales_type == 'non_sales':
            continue

        type_messages = sales_messages[sales_messages['sales_type'] == sales_type]

        total_sent = len(type_messages)
        got_response = type_messages['got_response'].sum()
        response_rate = got_response / total_sent if total_sent > 0 else 0

        # Calculate average metrics
        responded_messages = type_messages[type_messages['got_response'] == True]

        avg_response_time = responded_messages['response_time_hours'].mean() if len(responded_messages) > 0 else 0
        avg_sentiment = type_messages['sentiment_polarity'].mean()
        avg_length = type_messages['message_length'].mean()

        sales_performance[sales_type] = {
            'total_sent': int(total_sent),
            'got_response': int(got_response),
            'response_rate': response_rate,
            'avg_response_time_hours': avg_response_time,
            'avg_sentiment': avg_sentiment,
            'avg_length': avg_length
        }

    # Overall sales vs non-sales comparison
    # We need to calculate non-sales responses using the same method as sales messages
    if outbound_performance_df is not None:
        # Filter for non-sales from outbound performance data
        all_outbound_with_sales = outbound_performance_df.merge(
            df[['is_sales_message']].reset_index(),
            left_index=True, right_on='index', how='left'
        )
        non_sales_messages = all_outbound_with_sales[all_outbound_with_sales['is_sales_message'] == False]
    else:
        # Calculate manually for non-sales messages
        non_sales_messages = df[
            (df['is_sales_message'] == False) &
            (df['direction'] == 'outbound') &
            (df['is_outbound_initiated'] == True)
        ].copy()

        # Calculate responses for non-sales messages too
        non_sales_messages['got_response'] = False
        for idx, msg in non_sales_messages.iterrows():
            thread_id = msg['thread_id']
            msg_timestamp = msg['timestamp']

            responses = df[
                (df['thread_id'] == thread_id) &
                (df['timestamp'] > msg_timestamp) &
                (df['direction'] == 'inbound')
            ]

            non_sales_messages.loc[idx, 'got_response'] = len(responses) > 0

    overall_stats = {
        'sales_total_messages': len(sales_messages),
        'sales_responses': int(sales_messages['got_response'].sum()),
        'sales_response_rate': sales_messages['got_response'].mean(),
        'non_sales_total_messages': len(non_sales_messages),
        'non_sales_responses': int(non_sales_messages['got_response'].sum()) if len(non_sales_messages) > 0 else 0,
        'non_sales_response_rate': non_sales_messages['got_response'].mean() if len(non_sales_messages) > 0 else 0,
        'sales_performance_by_type': sales_performance
    }

    return overall_stats

def find_similar_sales_patterns(df: pd.DataFrame, outbound_performance_df: pd.DataFrame = None, similarity_threshold: float = 0.6) -> List[Dict]:
    """
    Find clusters of similar sales messages using fuzzy matching.
    """

    print("🔍 Finding similar sales message patterns...")

    # Get successful sales messages
    if outbound_performance_df is not None and 'got_response' in outbound_performance_df.columns:
        # Use outbound performance data merged with sales classification
        sales_with_performance = outbound_performance_df.merge(
            df[['is_sales_message', 'sales_type']].reset_index(),
            left_index=True, right_on='index', how='left'
        )
        sales_messages = sales_with_performance[
            (sales_with_performance['is_sales_message'] == True) &
            (sales_with_performance['got_response'] == True)
        ].copy()
    else:
        # Calculate manually - this is a fallback
        sales_messages = df[
            (df['is_sales_message'] == True) &
            (df['direction'] == 'outbound') &
            (df['is_outbound_initiated'] == True)
        ].copy()

        # Calculate which ones got responses
        successful_indices = []
        for idx, msg in sales_messages.iterrows():
            thread_id = msg['thread_id']
            msg_timestamp = msg['timestamp']

            responses = df[
                (df['thread_id'] == thread_id) &
                (df['timestamp'] > msg_timestamp) &
                (df['direction'] == 'inbound')
            ]

            if len(responses) > 0:
                successful_indices.append(idx)

        sales_messages = sales_messages.loc[successful_indices]

    if len(sales_messages) == 0:
        return []

    # Group similar messages
    message_groups = []
    processed_indices = set()

    for i, (idx, msg) in enumerate(sales_messages.iterrows()):
        if idx in processed_indices:
            continue

        current_content = str(msg['content']).lower().strip()
        similar_messages = [msg]
        processed_indices.add(idx)

        # Find similar messages
        for j, (idx2, msg2) in enumerate(sales_messages.iterrows()):
            if idx2 in processed_indices:
                continue

            other_content = str(msg2['content']).lower().strip()

            # Calculate similarity ratio
            similarity = SequenceMatcher(None, current_content, other_content).ratio()

            if similarity >= similarity_threshold:
                similar_messages.append(msg2)
                processed_indices.add(idx2)

        # Only keep groups with multiple messages
        if len(similar_messages) >= 2:
            # Calculate group metrics
            response_times = [m['response_time_hours'] for m in similar_messages if pd.notnull(m['response_time_hours'])]

            group_data = {
                'pattern_preview': current_content[:100] + "..." if len(current_content) > 100 else current_content,
                'message_count': len(similar_messages),
                'response_rate': 1.0,  # All are successful since we filtered for got_response=True
                'avg_response_time': np.mean(response_times) if response_times else 0,
                'avg_sentiment': np.mean([m['sentiment_polarity'] for m in similar_messages]),
                'avg_length': np.mean([m['message_length'] for m in similar_messages]),
                'sales_types': [m['sales_type'] for m in similar_messages],
                'contacts': [m['contact_person'] for m in similar_messages],
                'example_messages': [m['content'] for m in similar_messages[:3]]  # Store up to 3 examples
            }

            message_groups.append(group_data)

    # Sort by usage count and response performance
    message_groups.sort(key=lambda x: (x['message_count'], -x['avg_response_time']), reverse=True)

    return message_groups

def get_sales_insights(df: pd.DataFrame, sales_performance: Dict, sales_patterns: List[Dict]) -> Dict:
    """
    Generate actionable insights about sales messaging performance.
    """

    if not sales_performance:
        return {}

    insights = {
        'total_sales_messages': sales_performance.get('sales_total_messages', 0),
        'sales_response_rate': sales_performance.get('sales_response_rate', 0),
        'non_sales_response_rate': sales_performance.get('non_sales_response_rate', 0),
        'sales_vs_non_sales_lift': 0,
        'best_performing_sales_type': None,
        'worst_performing_sales_type': None,
        'most_common_patterns': len(sales_patterns),
        'top_sales_recommendations': []
    }

    # Calculate sales vs non-sales performance
    sales_rate = sales_performance.get('sales_response_rate', 0)
    non_sales_rate = sales_performance.get('non_sales_response_rate', 0)

    if non_sales_rate > 0:
        insights['sales_vs_non_sales_lift'] = (sales_rate - non_sales_rate) / non_sales_rate

    # Find best and worst performing sales types
    sales_by_type = sales_performance.get('sales_performance_by_type', {})
    if sales_by_type:
        type_performance = [(k, v['response_rate']) for k, v in sales_by_type.items() if v['total_sent'] >= 3]

        if type_performance:
            type_performance.sort(key=lambda x: x[1], reverse=True)
            insights['best_performing_sales_type'] = type_performance[0][0]
            insights['worst_performing_sales_type'] = type_performance[-1][0]

    # Generate recommendations
    recommendations = []

    if sales_rate > non_sales_rate:
        recommendations.append(f"Sales messages perform {(sales_rate/non_sales_rate - 1)*100:.0f}% better than casual messages")
    else:
        recommendations.append("Consider making messages more casual - sales messages underperform")

    if insights['best_performing_sales_type']:
        best_type = insights['best_performing_sales_type'].replace('_', ' ').title()
        recommendations.append(f"Focus on {best_type} messages - they get the best response rates")

    if len(sales_patterns) > 0:
        top_pattern = sales_patterns[0]
        recommendations.append(f"Reuse your top pattern (used {top_pattern['message_count']} times successfully)")

    insights['top_sales_recommendations'] = recommendations

    return insights