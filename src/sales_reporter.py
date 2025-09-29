# src/sales_reporter.py
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict, List

def generate_sales_focused_report(df: pd.DataFrame, sales_performance: Dict,
                                 sales_patterns: List[Dict], sales_insights: Dict,
                                 output_path: str):
    """
    Generate a comprehensive sales-focused report.
    """

    print(f"💼 Generating sales-focused report: {output_path}")

    md_content = []

    # Header
    md_content.extend([
        "# 💼 LinkedIn Sales Outreach Analysis Report",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Focus:** Sales & Business Messages Only",
        f"**Scope:** Conversations YOU initiated with business intent",
        "",
        "---",
        ""
    ])

    if not sales_performance:
        md_content.extend([
            "## ⚠️ No Sales Messages Found",
            "",
            "No messages were classified as sales/business focused in your outbound conversations.",
            "This might mean:",
            "- Your LinkedIn usage is primarily social/networking",
            "- Sales messages use different language patterns",
            "- Classification criteria need adjustment",
            "",
            "*This analysis looks for business keywords like: opportunity, role, company, service, revenue, etc.*"
        ])

        # Write to file and return early
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(md_content))
        return

    # Executive Summary
    total_sales = sales_performance.get('sales_total_messages', 0)
    sales_response_rate = sales_performance.get('sales_response_rate', 0)
    non_sales_rate = sales_performance.get('non_sales_response_rate', 0)
    sales_responses = sales_performance.get('sales_responses', 0)

    md_content.extend([
        "## 📊 Sales Performance Summary",
        "",
        f"You sent **{total_sales:,} sales-focused messages** in conversations you initiated.",
        f"**{sales_responses:,} messages** received responses (**{sales_response_rate:.1%}** response rate).",
        "",
        "### Key Sales Metrics",
        "",
        f"- **Sales Messages Sent:** {total_sales:,}",
        f"- **Sales Response Rate:** {sales_response_rate:.1%}",
        f"- **Non-Sales Response Rate:** {non_sales_rate:.1%}",
    ])

    # Sales vs non-sales comparison
    if non_sales_rate > 0:
        lift = sales_insights.get('sales_vs_non_sales_lift', 0)
        if lift > 0:
            md_content.append(f"- **Sales Performance:** {lift:.1%} better than casual messages ✅")
        else:
            md_content.append(f"- **Sales Performance:** {abs(lift):.1%} worse than casual messages ⚠️")

    md_content.extend(["", "---", ""])

    # Sales Performance by Type
    sales_by_type = sales_performance.get('sales_performance_by_type', {})
    if sales_by_type:
        md_content.extend([
            "## 💼 Performance by Sales Message Type",
            "",
            "| Sales Type | Messages Sent | Got Response | Response Rate | Avg Response Time | Avg Sentiment |",
            "|------------|---------------|--------------|---------------|-------------------|----------------|"
        ])

        for sales_type, metrics in sales_by_type.items():
            type_name = sales_type.replace('_', ' ').title()
            total = metrics['total_sent']
            responses = metrics['got_response']
            rate = metrics['response_rate']
            time_hours = metrics['avg_response_time_hours']
            sentiment = metrics['avg_sentiment']

            md_content.append(
                f"| {type_name} | {total} | {responses} | "
                f"{rate:.1%} | {time_hours:.1f}h | {sentiment:.2f} |"
            )

        md_content.extend(["", "---", ""])

    # Similar Sales Patterns
    if sales_patterns:
        md_content.extend([
            "## 🎯 Your Most Effective Sales Patterns",
            "",
            "*Similar sales messages that consistently get responses*",
            ""
        ])

        for i, pattern in enumerate(sales_patterns[:5], 1):
            preview = pattern['pattern_preview']
            count = pattern['message_count']
            avg_time = pattern['avg_response_time']
            sentiment = pattern['avg_sentiment']
            sales_types = list(set(pattern['sales_types']))

            md_content.extend([
                f"### Pattern #{i} - Used {count} times",
                f"**Response Time:** {avg_time:.1f}h | **Sentiment:** {sentiment:.2f} | **Types:** {', '.join(sales_types)}",
                "",
                f"**Pattern Preview:** {preview}",
                "",
                "**Example Messages:**"
            ])

            for j, example in enumerate(pattern['example_messages'][:2], 1):
                md_content.extend([
                    f"#### Example {j}:",
                    "```",
                    example,
                    "```",
                    ""
                ])

        md_content.extend(["---", ""])

    # Top Performing Sales Messages from patterns data
    top_sales_examples = []
    if sales_patterns:
        for pattern in sales_patterns[:3]:  # Top 3 patterns
            for example in pattern['example_messages'][:3]:  # Up to 3 examples each
                top_sales_examples.append({
                    'content': example,
                    'sales_type': pattern['sales_types'][0] if pattern['sales_types'] else 'business',
                    'avg_response_time': pattern['avg_response_time'],
                    'sentiment_polarity': pattern['avg_sentiment']
                })

    if len(top_sales_examples) > 0:
        md_content.extend([
            "## 🏆 Top 10 Sales Messages That Got Responses",
            "",
            "*Your most successful business outreach messages*",
            ""
        ])

        for i, msg in enumerate(top_sales_examples[:10], 1):
            content = str(msg['content'])
            sales_type = msg.get('sales_type', 'unknown').replace('_', ' ').title()
            response_time = msg['avg_response_time']
            sentiment = msg['sentiment_polarity']

            md_content.extend([
                f"### #{i} - {sales_type} ({response_time:.1f}h response)",
                f"**Pattern Message** | **Sentiment:** {sentiment:.2f}",
                "",
                "```",
                content,
                "```",
                ""
            ])

        md_content.extend(["---", ""])

    # Sales Insights and Recommendations
    best_type = sales_insights.get('best_performing_sales_type', 'Unknown')
    worst_type = sales_insights.get('worst_performing_sales_type', 'Unknown')
    recommendations = sales_insights.get('top_sales_recommendations', [])

    md_content.extend([
        "## 💡 Sales Performance Insights",
        "",
        "### 📈 What's Working",
        ""
    ])

    if best_type and best_type != 'Unknown':
        best_display = best_type.replace('_', ' ').title()
        md_content.append(f"🎯 **Best performing sales approach:** {best_display} messages")

    if worst_type and worst_type != 'Unknown' and worst_type != best_type:
        worst_display = worst_type.replace('_', ' ').title()
        md_content.append(f"⚠️ **Least effective approach:** {worst_display} messages")

    if recommendations:
        md_content.extend([
            "",
            "### 🚀 Key Recommendations",
            ""
        ])
        for rec in recommendations:
            md_content.append(f"- {rec}")

    md_content.extend([
        "",
        "### 🎯 Sales Optimization Action Plan",
        "",
        "1. **Double down on winners** - Use your top-performing sales patterns more frequently",
        "2. **A/B test variations** - Create slight modifications of successful messages",
        "3. **Segment by message type** - Tailor approach based on what's working for each sales category",
        "4. **Track and measure** - Monitor which new patterns get the best response rates",
        "5. **Optimize timing** - Send sales messages when you historically get fastest responses",
        "",
        "### 📊 Sales Message Checklist",
        "",
        "Before sending your next sales message, ensure it has:",
        "- [ ] Clear value proposition",
        "- [ ] Specific business context",
        "- [ ] Call to action",
        "- [ ] Personalization",
        "- [ ] Professional but friendly tone",
        "",
        "---",
        ""
    ])

    # Footer
    md_content.extend([
        "## 📋 Sales Analysis Summary",
        "",
        f"- **Analysis Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Sales Messages Analyzed:** {total_sales:,}",
        f"- **Sales Response Rate:** {sales_response_rate:.1%}",
        f"- **Sales Patterns Identified:** {len(sales_patterns)}",
        f"- **Best Sales Type:** {best_type.replace('_', ' ').title() if best_type != 'Unknown' else 'N/A'}",
        "",
        "*This report focuses specifically on your business/sales messaging to help optimize your LinkedIn outreach ROI.*"
    ])

    # Write to file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))

    print(f"✅ Sales-focused report saved to: {output_path}")
    print(f"💼 Analyzed {total_sales} sales messages with {sales_response_rate:.1%} response rate")

def generate_sales_copy_bank(df: pd.DataFrame, sales_patterns: List[Dict], output_path: str):
    """
    Generate a copy bank specifically for sales messages.
    """

    print(f"💼 Generating sales copy bank: {output_path}")

    md_content = []

    # Header
    md_content.extend([
        "# 💼 Sales Message Copy Bank",
        "",
        f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "*Your most effective sales message templates for business outreach*",
        "",
        "---",
        ""
    ])

    # Get top sales messages from patterns
    top_sales_examples = []
    if sales_patterns:
        for pattern in sales_patterns[:5]:  # Top 5 patterns
            for example in pattern['example_messages'][:3]:  # Up to 3 examples each
                top_sales_examples.append({
                    'content': example,
                    'sales_type': pattern['sales_types'][0] if pattern['sales_types'] else 'business',
                    'avg_response_time': pattern['avg_response_time'],
                    'sentiment_polarity': pattern['avg_sentiment']
                })

    if len(top_sales_examples) > 0:
        md_content.extend([
            "## 🏆 Top 15 Sales Messages That Work",
            "",
            "*Copy these proven sales messages or use as inspiration*",
            ""
        ])

        for i, msg in enumerate(top_sales_examples[:15], 1):
            sales_type = msg.get('sales_type', 'business').replace('_', ' ').title()
            response_time = msg['avg_response_time']
            sentiment = msg['sentiment_polarity']

            md_content.extend([
                f"### Sales Message #{i} - {sales_type}",
                f"**Performance:** {response_time:.1f}h response | Sentiment: {sentiment:.2f}",
                "",
                "```",
                msg['content'],
                "```",
                ""
            ])

        md_content.extend(["---", ""])

    # Sales patterns by category
    if sales_patterns:
        md_content.extend([
            "## 📋 Sales Templates by Category",
            ""
        ])

        for i, pattern in enumerate(sales_patterns, 1):
            sales_types = list(set(pattern['sales_types']))
            category = sales_types[0].replace('_', ' ').title() if sales_types else 'Business'

            md_content.extend([
                f"### {category} Templates (Pattern #{i})",
                f"**Usage:** {pattern['message_count']} times | **Avg Response:** {pattern['avg_response_time']:.1f}h",
                ""
            ])

            for j, example in enumerate(pattern['example_messages'], 1):
                md_content.extend([
                    f"#### Template {j}:",
                    "",
                    "```",
                    example,
                    "```",
                    ""
                ])

        md_content.extend(["---", ""])

    # Sales message frameworks
    md_content.extend([
        "## 🎯 Sales Message Frameworks",
        "",
        "### The \"Value First\" Framework",
        "```",
        "Hi [Name],",
        "",
        "[Specific value proposition or achievement]",
        "[Social proof or relevant experience]",
        "",
        "[Clear question or call to action]",
        "",
        "Best,",
        "[Your name]",
        "```",
        "",
        "### The \"Problem-Solution\" Framework",
        "```",
        "Hi [Name],",
        "",
        "I noticed [specific observation about their business/role]",
        "",
        "I've helped similar [companies/professionals] with [specific result]",
        "[Brief credibility statement]",
        "",
        "Would you be interested in [specific next step]?",
        "",
        "Best,",
        "[Your name]",
        "```",
        "",
        "### The \"Connection\" Framework",
        "```",
        "Hi [Name],",
        "",
        "[Mutual connection or common ground]",
        "",
        "I'm reaching out because [specific reason related to their business]",
        "[Brief value proposition]",
        "",
        "[Question or meeting request]",
        "",
        "Best,",
        "[Your name]",
        "```",
        "",
        "---",
        ""
    ])

    # Usage guidelines
    md_content.extend([
        "## 📋 Sales Message Best Practices",
        "",
        "### ✅ Do's",
        "- Research the recipient and their company before messaging",
        "- Lead with value, not with what you want",
        "- Be specific about what you're offering",
        "- Include relevant social proof or credentials",
        "- Make the call-to-action clear and easy",
        "- Personalize with specific details",
        "",
        "### ❌ Don'ts",
        "- Don't send generic, templated messages",
        "- Don't make it all about you",
        "- Don't be pushy or aggressive",
        "- Don't use too much sales jargon",
        "- Don't write novels - keep it concise",
        "- Don't forget to follow up professionally",
        "",
        "### 📈 Optimization Tips",
        "1. **A/B test subject lines** when possible",
        "2. **Track response rates** for different message types",
        "3. **Time your messages** based on recipient's likely schedule",
        "4. **Follow up strategically** - don't give up after one message",
        "5. **Continuously refine** based on what gets responses",
        "",
        "---",
        ""
    ])

    # Footer
    total_sales = len(top_sales_examples)
    patterns_count = len(sales_patterns)

    md_content.extend([
        "## 📊 Copy Bank Summary",
        "",
        f"- **High-Performance Messages:** {total_sales}",
        f"- **Proven Patterns:** {patterns_count}",
        f"- **Success Rate:** Based on messages that got responses",
        "",
        "*Use these templates as starting points and always personalize for your specific audience and goals.*"
    ])

    # Write to file
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(md_content))

    print(f"✅ Sales copy bank saved to: {output_path}")
    print(f"📋 Contains {total_sales} proven sales messages and {patterns_count} patterns")