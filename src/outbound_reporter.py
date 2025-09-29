# src/outbound_reporter.py
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def generate_outbound_focused_report(outbound_df: pd.DataFrame, starters_analysis: Dict,
                                   templates_df: pd.DataFrame, outbound_insights: Dict,
                                   failed_analysis: Dict, output_path: str):
    """
    Generate a comprehensive outbound-focused Markdown report.
    """

    print(f"🎯 Generating outbound-focused report: {output_path}")

    md_content = []

    # Header
    md_content.extend([
        "# 🎯 LinkedIn Outbound Analysis Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Focus:** Conversations YOU initiated (outbound only)",
        f"**Note:** This excludes your replies to conversations others started",
        "",
        "---",
        ""
    ])

    # Executive Summary
    total_outbound = outbound_insights.get('total_outbound_messages', 0)
    response_rate = outbound_insights.get('overall_outbound_response_rate', 0)
    successful = outbound_insights.get('successful_outbound_messages', 0)

    md_content.extend([
        "## 📊 Outbound Performance Summary",
        "",
        f"You sent **{total_outbound:,} messages in conversations YOU started** with a **{response_rate:.1%} response rate**.",
        f"**{successful:,} messages** received responses, while **{total_outbound - successful:,}** did not.",
        "",
        "### Key Performance Metrics",
        "",
        f"- **Messages in Conversations You Started:** {total_outbound:,}",
        f"- **Messages That Got Responses:** {successful:,}",
        f"- **Response Rate:** {response_rate:.1%}",
        f"- **Average Response Time:** {outbound_insights.get('avg_response_time_hours', 0):.1f} hours",
        f"- **Quick Responses (<24h):** {outbound_insights.get('quick_response_rate_24h', 0):.1%}",
        "",
        "---",
        ""
    ])

    # Conversation Starters Analysis
    if starters_analysis:
        starter_rate = starters_analysis.get('starter_response_rate', 0)
        total_starters = starters_analysis.get('total_conversation_starters', 0)
        successful_starters = starters_analysis.get('successful_starters', 0)

        md_content.extend([
            "## 🚀 Conversation Starters Analysis",
            "",
            f"You initiated **{total_starters:,} conversations**, with **{successful_starters:,}** getting responses (**{starter_rate:.1%}** success rate).",
            "",
            "### Conversation Starter Performance by Type",
            "",
            "| Message Type | Total Sent | Got Response | Response Rate | Avg Response Time | Avg Sentiment |",
            "|--------------|------------|--------------|---------------|-------------------|----------------|"
        ])

        if 'type_performance' in starters_analysis:
            for _, row in starters_analysis['type_performance'].iterrows():
                msg_type = row['message_type']
                total = int(row['got_response_count'])
                responded = int(row['got_response_sum'])
                rate = row['got_response_mean']
                avg_time = row['response_time_hours_mean'] if pd.notnull(row['response_time_hours_mean']) else 0
                sentiment = row['sentiment_polarity_mean']

                md_content.append(
                    f"| {msg_type.replace('_', ' ').title()} | {total} | {responded} | "
                    f"{rate:.1%} | {avg_time:.1f}h | {sentiment:.2f} |"
                )

        md_content.extend(["", "---", ""])

    # Top Performing Messages
    if len(outbound_df[outbound_df['got_response']]) > 0:
        top_performers = outbound_df[outbound_df['got_response']].nlargest(10, 'performance_score')

        md_content.extend([
            "## 🏆 Top 10 Performing Outbound Messages",
            "",
            "*Your most successful messages that got responses*",
            ""
        ])

        for i, (_, msg) in enumerate(top_performers.iterrows(), 1):
            contact = msg['contact_person']
            content = str(msg['content'])
            response_time = msg['response_time_hours'] if pd.notnull(msg['response_time_hours']) else 0
            sentiment = msg['sentiment_polarity']
            msg_type = msg['message_type'].replace('_', ' ').title()
            date = msg['timestamp'].strftime('%Y-%m-%d')

            md_content.extend([
                f"### #{i} - {msg_type} ({response_time:.1f}h response)",
                f"**To:** {contact} | **Date:** {date} | **Sentiment:** {sentiment:.2f}",
                "",
                f"```",
                f"{content}",
                f"```",
                ""
            ])

        md_content.extend(["---", ""])

    # Message Templates Analysis
    if len(templates_df) > 0:
        md_content.extend([
            "## 📝 Your Most Effective Message Templates",
            "",
            "*Message patterns you use repeatedly that get responses*",
            "",
            "| Template Preview | Usage Count | Response Rate | Avg Response Time | Avg Sentiment |",
            "|------------------|-------------|---------------|-------------------|----------------|"
        ])

        for _, template in templates_df.head(10).iterrows():
            preview = template['template_preview'][:40] + "..."
            usage = int(template['usage_count'])
            response_rate = template['response_rate']
            response_time = template['avg_response_time'] if pd.notnull(template['avg_response_time']) else 0
            sentiment = template['avg_sentiment']

            md_content.append(
                f"| {preview} | {usage} | {response_rate:.1%} | "
                f"{response_time:.1f}h | {sentiment:.2f} |"
            )

        md_content.extend(["", "### Full Template Examples", ""])

        for i, (_, template) in enumerate(templates_df.head(5).iterrows(), 1):
            md_content.extend([
                f"#### Template #{i} (Used {int(template['usage_count'])} times - {template['response_rate']:.1%} response rate)",
                "",
                f"```",
                f"{template['example_full_message']}",
                f"```",
                ""
            ])

        md_content.extend(["---", ""])

    # What Doesn't Work - Failed Messages Analysis
    if failed_analysis and failed_analysis.get('total_failed', 0) > 0:
        total_failed = failed_analysis['total_failed']
        failed_length = failed_analysis['avg_failed_length']
        failed_sentiment = failed_analysis['avg_failed_sentiment']

        md_content.extend([
            f"## ❌ What Doesn't Work - Failed Messages Analysis",
            "",
            f"**{total_failed:,} messages** didn't receive responses. Here's what to avoid:",
            "",
            "### Failed Message Characteristics",
            "",
            f"- **Average Length:** {failed_length:.0f} characters",
            f"- **Average Sentiment:** {failed_sentiment:.2f}",
            "",
            "### Failed Message Types",
            "",
            "| Message Type | Count |",
            "|--------------|-------|"
        ])

        for msg_type, count in failed_analysis.get('failed_by_type', {}).items():
            md_content.append(f"| {msg_type.replace('_', ' ').title()} | {count} |")

        md_content.extend(["", "---", ""])

    # Success vs Failure Comparison
    successful_length = outbound_insights.get('successful_avg_length', 0)
    failed_length = outbound_insights.get('failed_avg_length', 0)
    successful_sentiment = outbound_insights.get('successful_avg_sentiment', 0)
    failed_sentiment = outbound_insights.get('failed_avg_sentiment', 0)

    md_content.extend([
        "## 📊 Success vs Failure Pattern Analysis",
        "",
        "| Metric | Successful Messages | Failed Messages | Difference |",
        "|--------|-------------------|-----------------|------------|",
        f"| Avg Length | {successful_length:.0f} chars | {failed_length:.0f} chars | {successful_length - failed_length:+.0f} |",
        f"| Avg Sentiment | {successful_sentiment:.2f} | {failed_sentiment:.2f} | {successful_sentiment - failed_sentiment:+.2f} |",
        "",
        "---",
        ""
    ])

    # Actionable Insights and Recommendations
    md_content.extend([
        "## 💡 Actionable Insights & Recommendations",
        "",
        "### ✅ What's Working Well",
        ""
    ])

    if response_rate > 0.6:
        md_content.append("🎉 **Excellent response rate!** Your outbound strategy is highly effective.")
    elif response_rate > 0.4:
        md_content.append("👍 **Good response rate.** You're doing well with room for optimization.")
    elif response_rate > 0.2:
        md_content.append("📈 **Average performance.** Focus on improving your top templates.")
    else:
        md_content.append("🔄 **Low response rate.** Consider revamping your approach using successful examples.")

    # Best message types
    best_types = outbound_insights.get('best_message_types', {})
    if best_types:
        md_content.extend([
            "",
            "**Your most successful message types:**"
        ])
        for msg_type, count in list(best_types.items())[:3]:
            md_content.append(f"- {msg_type.replace('_', ' ').title()}: {count} successful messages")

    # Length insights
    if successful_length > failed_length:
        diff = successful_length - failed_length
        md_content.append(f"\n📏 **Length matters:** Your successful messages are {diff:.0f} characters longer on average.")
    elif failed_length > successful_length:
        diff = failed_length - successful_length
        md_content.append(f"\n📏 **Keep it concise:** Your failed messages are {diff:.0f} characters longer on average.")

    # Sentiment insights
    if successful_sentiment > failed_sentiment:
        md_content.append("😊 **Positive tone works:** Your successful messages have more positive sentiment.")

    md_content.extend([
        "",
        "### 🎯 Action Plan",
        "",
        "1. **Use your winning templates** - Leverage your most successful message patterns",
        "2. **Optimize message length** - " + (
            f"Keep messages around {successful_length:.0f} characters" if successful_length > 0 else "Experiment with different lengths"
        ),
        "3. **Maintain positive tone** - " + (
            f"Target sentiment score of {successful_sentiment:.2f} or higher" if successful_sentiment > 0 else "Focus on more positive language"
        ),
        "4. **Focus on working types** - " + (
            f"Prioritize {list(best_types.keys())[0].replace('_', ' ')} messages" if best_types else "Analyze your most successful message types"
        ),
        "5. **A/B test variations** - Try slight modifications of your top performers",
        "",
        "### 📈 Quick Wins",
        "",
        "- Copy your top 5 performing messages as templates",
        "- Avoid patterns that consistently fail to get responses",
        "- Follow up on conversations that started successfully",
        "- Time your outreach based on when you get quick responses",
        "",
        "---",
        ""
    ])

    # Footer
    md_content.extend([
        "## 📋 Report Summary",
        "",
        f"- **Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Total Outbound Messages:** {total_outbound:,}",
        f"- **Response Rate:** {response_rate:.1%}",
        f"- **Templates Identified:** {len(templates_df)}",
        "",
        "*This report focuses specifically on your outbound messaging performance to help you optimize your LinkedIn outreach strategy.*"
    ])

    # Write to file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))

    print(f"✅ Outbound-focused report saved to: {output_path}")
    print(f"📝 Report contains detailed analysis of {total_outbound:,} outbound messages")

def generate_message_copy_bank(outbound_df: pd.DataFrame, templates_df: pd.DataFrame, output_path: str):
    """
    Generate a copy bank of your most effective messages for easy reuse.
    """

    print(f"📋 Generating message copy bank: {output_path}")

    md_content = []

    # Header
    md_content.extend([
        "# 💬 Your LinkedIn Message Copy Bank",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "*Your most effective message templates from conversations YOU initiated*",
        "*These are messages that got responses in outbound conversations*",
        "",
        "---",
        ""
    ])

    # Top Performers for Copy-Paste
    top_performers = outbound_df[outbound_df['got_response']].nlargest(15, 'performance_score')

    if len(top_performers) > 0:
        md_content.extend([
            "## 🏆 Top 15 High-Performance Messages",
            "",
            "*Copy these exact messages or use as inspiration*",
            ""
        ])

        for i, (_, msg) in enumerate(top_performers.iterrows(), 1):
            response_time = msg['response_time_hours'] if pd.notnull(msg['response_time_hours']) else 0
            msg_type = msg['message_type'].replace('_', ' ').title()
            sentiment = msg['sentiment_polarity']

            md_content.extend([
                f"### Message #{i} - {msg_type}",
                f"**Performance:** {response_time:.1f}h response time | Sentiment: {sentiment:.2f}",
                "",
                f"```",
                f"{msg['content']}",
                f"```",
                ""
            ])

    # Templates by Category
    if len(templates_df) > 0:
        md_content.extend([
            "---",
            "",
            "## 📝 Message Templates by Category",
            ""
        ])

        # Group by message type if we can identify it
        outbound_with_templates = outbound_df[outbound_df['got_response']].copy()

        # Group successful messages by type
        for msg_type in outbound_with_templates['message_type'].unique():
            type_messages = outbound_with_templates[
                outbound_with_templates['message_type'] == msg_type
            ].nlargest(3, 'performance_score')

            if len(type_messages) > 0:
                md_content.extend([
                    f"### {msg_type.replace('_', ' ').title()} Messages",
                    ""
                ])

                for i, (_, msg) in enumerate(type_messages.iterrows(), 1):
                    response_time = msg['response_time_hours'] if pd.notnull(msg['response_time_hours']) else 0

                    md_content.extend([
                        f"#### Example {i} ({response_time:.1f}h response)",
                        "",
                        f"```",
                        f"{msg['content']}",
                        f"```",
                        ""
                    ])

    # Quick Copy Section
    short_messages = top_performers[top_performers['message_length'] < 200].head(5)

    if len(short_messages) > 0:
        md_content.extend([
            "---",
            "",
            "## ⚡ Quick Copy - Short Messages",
            "",
            "*Brief, effective messages perfect for quick outreach*",
            ""
        ])

        for i, (_, msg) in enumerate(short_messages.iterrows(), 1):
            md_content.extend([
                f"**{i}.** {msg['content']}",
                ""
            ])

    # Footer
    md_content.extend([
        "---",
        "",
        "## 📋 Usage Tips",
        "",
        "1. **Personalize:** Always customize with the recipient's name and company",
        "2. **Context matters:** Adapt messages based on how you found the contact",
        "3. **Follow up:** Use different templates for follow-up messages",
        "4. **Track results:** Monitor which templates work best for your audience",
        "",
        f"*Copy bank generated from analysis of {len(outbound_df):,} outbound messages*"
    ])

    # Write to file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))

    print(f"✅ Message copy bank saved to: {output_path}")
    print(f"💬 Contains {len(top_performers)} high-performance message examples")