#!/usr/bin/env python3
"""
LinkedIn DM Analyzer - Main Entry Point

A privacy-first tool to analyze your LinkedIn Direct Messages locally.
No API access required - works with CSV exports from LinkedIn Data Privacy page.
"""

import os
import sys
import argparse
from pathlib import Path

from src.parser import load_messages_csv, validate_csv_structure

def main():
    parser = argparse.ArgumentParser(
        description="Analyze LinkedIn Direct Messages from CSV export",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                           # Use default sample data
  python main.py -f data/my_messages.csv  # Analyze specific CSV file
  python main.py --output results.xlsx    # Custom output filename

Privacy Note: All processing is done locally. Your data never leaves your computer.
        """
    )

    parser.add_argument(
        "-f", "--file",
        default="data/messages_test_sample.csv",
        help="Path to LinkedIn messages CSV file (default: data/messages_test_sample.csv)"
    )

    parser.add_argument(
        "-o", "--output",
        default="outputs/linkedin_analysis.xlsx",
        help="Output Excel file path for results (default: outputs/linkedin_analysis.xlsx)"
    )

    parser.add_argument(
        "--markdown", "--md",
        action="store_true",
        help="Also generate Markdown report alongside Excel"
    )

    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only validate CSV structure without processing"
    )

    args = parser.parse_args()

    # Check if input file exists
    if not os.path.exists(args.file):
        print(f"❌ Error: File '{args.file}' not found")
        print("\n💡 Tip: Export your LinkedIn messages from:")
        print("   Settings & Privacy > Data Privacy > Get a copy of your data > Messages")
        sys.exit(1)

    print("🔍 LinkedIn DM Analyzer Starting...")
    print(f"📁 Input file: {args.file}")
    print(f"📊 Output file: {args.output}")
    print()

    # Step 1: Validate CSV structure
    print("🔬 Validating CSV structure...")
    if not validate_csv_structure(args.file):
        print("❌ CSV validation failed. Please check your LinkedIn export format.")
        sys.exit(1)
    print("✅ CSV structure is valid")

    if args.validate_only:
        print("🎉 Validation complete!")
        sys.exit(0)

    # Step 2: Load and parse messages
    print("📖 Loading messages...")
    try:
        df = load_messages_csv(args.file)
        total_messages = len(df)
        total_threads = df['thread_id'].nunique()
        date_range = f"{df['timestamp'].min().date()} to {df['timestamp'].max().date()}"

        print(f"✅ Loaded {total_messages:,} messages")
        print(f"💬 Found {total_threads:,} conversation threads")
        print(f"📅 Date range: {date_range}")
        print()

    except Exception as e:
        print(f"❌ Error loading CSV: {e}")
        sys.exit(1)

    # Create output directory if it doesn't exist
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Step 3: Classify message direction
    print("📊 Classifying message direction...")
    from src.direction import classify_message_direction, get_conversation_summary, analyze_response_patterns

    df_with_direction = classify_message_direction(df)

    # Step 4: Analyze messages
    print("🧠 Performing message analysis...")
    from src.analyzer import (
        analyze_message_sentiment, calculate_message_metrics,
        detect_replies_and_response_times, analyze_conversation_flow,
        find_top_performing_messages
    )

    # Run all analysis functions
    analyzed_df = analyze_message_sentiment(df_with_direction)
    analyzed_df = calculate_message_metrics(analyzed_df)
    analyzed_df = detect_replies_and_response_times(analyzed_df)

    # Get conversation insights
    conversation_summary = get_conversation_summary(analyzed_df)
    conversation_stats = analyze_response_patterns(analyzed_df)
    analysis_results = analyze_conversation_flow(analyzed_df)
    top_messages = find_top_performing_messages(analyzed_df)

    # Step 4b: Outbound-focused analysis
    print("🎯 Analyzing outbound message performance...")
    from src.outbound_analyzer import (
        analyze_outbound_performance, get_conversation_starters_analysis,
        get_message_templates, analyze_failed_outreach, get_outbound_insights
    )

    outbound_performance = analyze_outbound_performance(analyzed_df)
    starters_analysis = get_conversation_starters_analysis(outbound_performance)
    templates_df = get_message_templates(outbound_performance)
    failed_analysis = analyze_failed_outreach(outbound_performance)
    outbound_insights = get_outbound_insights(outbound_performance)

    # Step 4c: Sales-focused analysis
    print("💼 Analyzing sales-focused messages...")
    from src.sales_analyzer import (
        classify_sales_messages, analyze_sales_performance,
        find_similar_sales_patterns, get_sales_insights
    )

    # Classify sales messages in the full analyzed dataset
    analyzed_df = classify_sales_messages(analyzed_df)

    # Analyze sales performance
    sales_performance = analyze_sales_performance(analyzed_df, outbound_performance)
    sales_patterns = find_similar_sales_patterns(analyzed_df, outbound_performance)
    sales_insights = get_sales_insights(analyzed_df, sales_performance, sales_patterns)

    # Step 5: Generate reports
    print("📋 Generating reports...")
    from src.reporter import generate_excel_report, print_quick_summary
    from src.markdown_reporter import generate_markdown_report, generate_summary_markdown
    from src.outbound_reporter import generate_outbound_focused_report, generate_message_copy_bank
    from src.sales_reporter import generate_sales_focused_report, generate_sales_copy_bank

    # Always generate Excel report
    generate_excel_report(
        analyzed_df=analyzed_df,
        contact_summary=conversation_summary,
        analysis_results=analysis_results,
        conversation_stats=conversation_stats,
        top_messages=top_messages,
        output_path=args.output
    )

    # Generate Markdown reports
    base_path = Path(args.output).with_suffix('')

    # Always generate a quick summary markdown
    summary_md_path = f"{base_path}_summary.md"
    generate_summary_markdown(analysis_results, conversation_stats, summary_md_path)

    # Generate full markdown report if requested or by default
    if args.markdown or True:  # Always generate by default
        full_md_path = f"{base_path}_full_report.md"
        generate_markdown_report(
            analyzed_df=analyzed_df,
            contact_summary=conversation_summary,
            analysis_results=analysis_results,
            conversation_stats=conversation_stats,
            top_messages=top_messages,
            output_path=full_md_path
        )

    # Generate outbound-focused reports
    outbound_report_path = f"{base_path}_outbound_analysis.md"
    generate_outbound_focused_report(
        outbound_df=outbound_performance,
        starters_analysis=starters_analysis,
        templates_df=templates_df,
        outbound_insights=outbound_insights,
        failed_analysis=failed_analysis,
        output_path=outbound_report_path
    )

    # Generate message copy bank
    copy_bank_path = f"{base_path}_message_copy_bank.md"
    generate_message_copy_bank(
        outbound_df=outbound_performance,
        templates_df=templates_df,
        output_path=copy_bank_path
    )

    # Generate sales-focused reports
    sales_report_path = f"{base_path}_sales_analysis.md"
    generate_sales_focused_report(
        df=analyzed_df,
        sales_performance=sales_performance,
        sales_patterns=sales_patterns,
        sales_insights=sales_insights,
        output_path=sales_report_path
    )

    # Generate sales copy bank
    sales_copy_path = f"{base_path}_sales_copy_bank.md"
    generate_sales_copy_bank(
        df=analyzed_df,
        sales_patterns=sales_patterns,
        output_path=sales_copy_path
    )

    # Print summary to console
    print_quick_summary(analysis_results, conversation_stats)

if __name__ == "__main__":
    main()