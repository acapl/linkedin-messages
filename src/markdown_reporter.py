# src/markdown_reporter.py
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def generate_markdown_report(analyzed_df: pd.DataFrame, contact_summary: pd.DataFrame,
                           analysis_results: Dict, conversation_stats: Dict,
                           top_messages: pd.DataFrame, output_path: str):
    """
    Generate comprehensive Markdown report with all analysis results.

    Args:
        analyzed_df: DataFrame with all analyzed messages
        contact_summary: Summary statistics by contact
        analysis_results: Dictionary with analysis results
        conversation_stats: Dictionary with conversation statistics
        top_messages: DataFrame with top performing messages
        output_path: Path for output Markdown file
    """

    print(f"📝 Generating Markdown report: {output_path}")

    # Create markdown content
    md_content = []

    # Header
    md_content.extend([
        "# 🔍 LinkedIn DM Analysis Report",
        f"",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Analysis Period:** {analyzed_df['timestamp'].min().date()} to {analyzed_df['timestamp'].max().date()}",
        f"",
        "---",
        ""
    ])

    # Executive Summary
    md_content.extend([
        "## 📊 Executive Summary",
        "",
        f"This report analyzes **{analysis_results.get('total_messages', 0):,} LinkedIn messages** across **{conversation_stats.get('total_contacts', 0):,} conversations** to provide insights into networking performance and outreach effectiveness.",
        "",
        "### Key Highlights",
        "",
        f"- **Response Rate:** {conversation_stats.get('overall_response_rate', 0):.1%} ({conversation_stats.get('contacts_who_responded', 0)} out of {conversation_stats.get('total_contacts', 0)} contacts responded)",
        f"- **Message Volume:** {analysis_results.get('outbound_message_count', 0):,} sent, {analysis_results.get('inbound_message_count', 0):,} received",
        f"- **Response Time:** Average {analysis_results.get('avg_response_time_hours', 0):.1f} hours",
        f"- **Quick Responses:** {analysis_results.get('quick_response_rate', 0):.1%} responded within 1 hour",
        f"- **Message Sentiment:** Your messages: {analysis_results.get('outbound_avg_sentiment', 0):.2f}, Contacts: {analysis_results.get('inbound_avg_sentiment', 0):.2f}",
        "",
        "---",
        ""
    ])

    # Detailed Metrics
    md_content.extend([
        "## 📈 Detailed Performance Metrics",
        "",
        "### Response Analysis",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Contacts | {conversation_stats.get('total_contacts', 0):,} |",
        f"| Contacts Who Responded | {conversation_stats.get('contacts_who_responded', 0):,} |",
        f"| Contacts Who Ghosted | {conversation_stats.get('contacts_who_ghosted', 0):,} |",
        f"| Overall Response Rate | {conversation_stats.get('overall_response_rate', 0):.1%} |",
        f"| Weighted Response Rate | {conversation_stats.get('weighted_response_rate', 0):.1%} |",
        "",
        "### Message Volume",
        "",
        "| Direction | Count | Percentage |",
        "|-----------|-------|------------|",
        f"| Outbound (Sent by You) | {analysis_results.get('outbound_message_count', 0):,} | {(analysis_results.get('outbound_message_count', 0) / analysis_results.get('total_messages', 1) * 100):.1f}% |",
        f"| Inbound (Received) | {analysis_results.get('inbound_message_count', 0):,} | {(analysis_results.get('inbound_message_count', 0) / analysis_results.get('total_messages', 1) * 100):.1f}% |",
        f"| **Total Messages** | **{analysis_results.get('total_messages', 0):,}** | **100%** |",
        "",
        "### Timing Analysis",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Average Response Time | {analysis_results.get('avg_response_time_hours', 0):.1f} hours |",
        f"| Median Response Time | {analysis_results.get('median_response_time_hours', 0):.1f} hours |",
        f"| Quick Responses (<1h) | {analysis_results.get('quick_response_count', 0):,} ({analysis_results.get('quick_response_rate', 0):.1%}) |",
        "",
        "### Message Quality",
        "",
        "| Metric | Outbound | Inbound |",
        "|--------|----------|---------|",
        f"| Average Length (characters) | {analysis_results.get('outbound_avg_length', 0):.0f} | {analysis_results.get('inbound_avg_length', 0):.0f} |",
        f"| Average Sentiment Score | {analysis_results.get('outbound_avg_sentiment', 0):.2f} | {analysis_results.get('inbound_avg_sentiment', 0):.2f} |",
        "",
        "> **Sentiment Scale:** -1.0 (very negative) to +1.0 (very positive)",
        "",
        "---",
        ""
    ])

    # Top Contacts
    if len(contact_summary) > 0:
        top_contacts = contact_summary.head(10)
        md_content.extend([
            "## 👥 Top 10 Most Active Contacts",
            "",
            "| Contact | Total Messages | Your Messages | Their Messages | Response Rate | Last Contact |",
            "|---------|----------------|---------------|----------------|---------------|--------------|"
        ])

        for _, contact in top_contacts.iterrows():
            last_contact = contact['last_contact'].strftime('%Y-%m-%d') if pd.notnull(contact['last_contact']) else 'N/A'
            md_content.append(
                f"| {contact['contact_person']} | {contact['total_messages']} | "
                f"{contact['outbound_messages']} | {contact['inbound_messages']} | "
                f"{contact['response_rate']:.1%} | {last_contact} |"
            )

        md_content.extend(["", "---", ""])

    # Top Performing Messages
    if len(top_messages) > 0:
        md_content.extend([
            "## 🎯 Top 5 Performing Messages",
            "",
            "*Messages that received responses, ranked by engagement score*",
            ""
        ])

        for i, (_, msg) in enumerate(top_messages.head(5).iterrows(), 1):
            contact = msg['contact_person']
            content = str(msg['content'])[:200] + "..." if len(str(msg['content'])) > 200 else str(msg['content'])
            sentiment = msg['sentiment_polarity']
            score = msg['performance_score']
            date = msg['timestamp'].strftime('%Y-%m-%d')

            md_content.extend([
                f"### #{i} - Score: {score:.2f}",
                f"**To:** {contact}  ",
                f"**Date:** {date}  ",
                f"**Sentiment:** {sentiment:.2f}",
                "",
                f"> {content}",
                ""
            ])

        md_content.extend(["---", ""])

    # Ghosted Contacts Analysis
    ghosted = conversation_stats.get('ghosted_contacts', [])
    if ghosted:
        md_content.extend([
            f"## 👻 Contacts Who Didn't Respond ({len(ghosted)} contacts)",
            "",
            "*These contacts received outbound messages but never responded*",
            ""
        ])

        # Show first 20 ghosted contacts
        for contact in ghosted[:20]:
            md_content.append(f"- {contact}")

        if len(ghosted) > 20:
            md_content.append(f"- ... and {len(ghosted) - 20} more")

        md_content.extend(["", "---", ""])

    # Best Responders
    best_responders = contact_summary[
        (contact_summary['has_response']) & (contact_summary['response_rate'] >= 0.5)
    ].head(10)

    if len(best_responders) > 0:
        md_content.extend([
            "## ⭐ Best Responders (50%+ Response Rate)",
            "",
            "| Contact | Response Rate | Total Conversations | Last Contact |",
            "|---------|---------------|---------------------|--------------|"
        ])

        for _, contact in best_responders.iterrows():
            last_contact = contact['last_contact'].strftime('%Y-%m-%d') if pd.notnull(contact['last_contact']) else 'N/A'
            md_content.append(
                f"| {contact['contact_person']} | {contact['response_rate']:.1%} | "
                f"{contact['total_messages']} | {last_contact} |"
            )

        md_content.extend(["", "---", ""])

    # Insights and Recommendations
    response_rate = conversation_stats.get('overall_response_rate', 0)
    avg_sentiment = analysis_results.get('outbound_avg_sentiment', 0)
    quick_response_rate = analysis_results.get('quick_response_rate', 0)

    md_content.extend([
        "## 💡 Key Insights & Recommendations",
        "",
        "### Performance Assessment",
        ""
    ])

    if response_rate >= 0.7:
        md_content.append("🎉 **Excellent networking performance!** Your 70%+ response rate is outstanding.")
    elif response_rate >= 0.5:
        md_content.append("👍 **Good networking performance.** Your response rate is above average.")
    elif response_rate >= 0.3:
        md_content.append("📈 **Room for improvement.** Consider refining your messaging approach.")
    else:
        md_content.append("🔄 **Significant improvement needed.** Review successful message templates.")

    md_content.extend(["", "### Message Quality Insights", ""])

    if avg_sentiment > 0.15:
        md_content.append("😊 **Positive messaging tone** - Your messages maintain good sentiment.")
    elif avg_sentiment > 0:
        md_content.append("😐 **Neutral messaging tone** - Consider adding more enthusiasm.")
    else:
        md_content.append("😕 **Negative messaging tone** - Focus on more positive language.")

    md_content.extend(["", "### Timing Insights", ""])

    if quick_response_rate > 0.6:
        md_content.append("⚡ **Great engagement** - Most responses come quickly when people reply.")
    elif quick_response_rate > 0.3:
        md_content.append("⏰ **Moderate engagement** - Some contacts take time to respond.")
    else:
        md_content.append("🐌 **Slow responses** - Consider following up or adjusting approach.")

    md_content.extend([
        "",
        "### Action Items",
        "",
        "1. **Leverage top performers** - Use your highest-scoring message templates as inspiration",
        "2. **Follow up strategically** - Re-engage with best responders for ongoing opportunities",
        "3. **Refine messaging** - Learn from successful conversations to improve response rates",
        "4. **Time optimization** - Schedule follow-ups based on typical response patterns",
        "",
        "---",
        ""
    ])

    # Footer
    md_content.extend([
        "## 📋 Report Details",
        "",
        f"- **Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Data Period:** {analyzed_df['timestamp'].min().date()} to {analyzed_df['timestamp'].max().date()}",
        f"- **Messages Analyzed:** {len(analyzed_df):,}",
        f"- **Conversations:** {analyzed_df['thread_id'].nunique():,}",
        f"- **Unique Contacts:** {contact_summary.shape[0] if len(contact_summary) > 0 else 0}",
        "",
        "*Generated by LinkedIn DM Analyzer - Your privacy-first networking insights tool*"
    ])

    # Write to file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))

    print(f"✅ Markdown report saved to: {output_path}")
    print(f"📝 Report contains {len([line for line in md_content if line.strip()])} lines of insights")

def generate_summary_markdown(analysis_results: Dict, conversation_stats: Dict, output_path: str):
    """Generate a quick summary Markdown file with key metrics only."""

    summary_content = [
        "# 📊 LinkedIn DM Analysis - Quick Summary",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        "## Key Metrics",
        "",
        f"- **Total Messages:** {analysis_results.get('total_messages', 0):,}",
        f"- **Total Contacts:** {conversation_stats.get('total_contacts', 0):,}",
        f"- **Response Rate:** {conversation_stats.get('overall_response_rate', 0):.1%}",
        f"- **Messages Sent:** {analysis_results.get('outbound_message_count', 0):,}",
        f"- **Messages Received:** {analysis_results.get('inbound_message_count', 0):,}",
        f"- **Avg Response Time:** {analysis_results.get('avg_response_time_hours', 0):.1f} hours",
        f"- **Quick Response Rate:** {analysis_results.get('quick_response_rate', 0):.1%}",
        f"- **Your Sentiment:** {analysis_results.get('outbound_avg_sentiment', 0):.2f}",
        f"- **Contact Sentiment:** {analysis_results.get('inbound_avg_sentiment', 0):.2f}"
    ]

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(summary_content))

    print(f"📄 Summary saved to: {output_path}")