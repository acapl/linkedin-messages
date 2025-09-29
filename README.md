# LinkedIn DM Analyzer

A privacy-first Python tool that analyzes your LinkedIn Direct Messages locally to provide insights into your outbound sales and networking performance. No API access required - works entirely with CSV exports from LinkedIn's Data Privacy page.

## Features

- **Response Rate Analysis** - Track success rates for outbound conversations you initiated
- **Sales Message Classification** - Identify business opportunities, partnership requests, and sales patterns
- **Response Time Metrics** - Understand how quickly prospects reply to your outreach
- **Sentiment Analysis** - Gauge the tone of your conversations and recipient engagement
- **Top Message Templates** - Find your most effective conversation starters and follow-ups
- **Contact Management** - See engagement levels and response patterns with each contact
- **Professional Reports** - Export detailed Excel and Markdown reports with sales insights
- **Privacy First** - All processing done locally, data never leaves your computer

## 🚀 Quick Start

### Prerequisites

- Python 3.8+ (tested with Python 3.13)
- LinkedIn message export CSV file

### Installation

1. **Clone or download this project**
   ```bash
   git clone <repository-url>
   cd linkedin-dm-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Get your LinkedIn data**
   - Go to LinkedIn Settings & Privacy
   - Navigate to "Data Privacy" → "Get a copy of your data"
   - Select "Messages" and download the export
   - Place the CSV file in the `data/` folder

### Usage

**Basic analysis with sample data:**
```bash
python main.py
```

**Analyze your own data:**
```bash
python main.py -f data/your_messages.csv -u "Your Name"
```

**Custom output location:**
```bash
python main.py -f data/your_messages.csv -u "Your Name" -o reports/my_analysis.xlsx
```

**Generate both Excel and Markdown reports:**
```bash
python main.py -f data/your_messages.csv -u "Your Name" --markdown
```

**Validate CSV structure only:**
```bash
python main.py --validate-only -f data/your_messages.csv
```

## 📁 Project Structure

```
linkedin-dm-analyzer/
├── data/                    # LinkedIn CSV exports
│   └── sample_messages.csv # Anonymized sample data
├── outputs/                 # Generated reports
│   └── linkedin_analysis.xlsx
├── src/                     # Core analysis modules
│   ├── parser.py           # CSV parsing and validation
│   ├── direction.py        # Message direction classification
│   ├── analyzer.py         # Core metrics and conversation analysis
│   ├── outbound_analyzer.py # Outbound message performance analysis
│   ├── sales_analyzer.py   # Sales-focused message classification
│   ├── reporter.py         # Excel report generation
│   ├── sales_reporter.py   # Sales-specific Excel reports
│   └── markdown_reporter.py # Markdown report generation
├── main.py                 # Main entry point
├── requirements.txt        # Python dependencies
├── CLAUDE.md              # Development guidelines
└── README.md              # This file
```

## What You'll Get

The tool generates comprehensive reports with sales-focused insights:

### Excel Reports
**Summary Sheet**
- Outbound conversation metrics (only conversations you initiated)
- Response rates and timing analysis
- Sales message classification breakdown
- Performance trends and patterns

**Outbound Performance**
- Individual conversation analysis
- Response tracking for each prospect
- Message timing and follow-up patterns
- Conversion funnel insights

**Sales Analysis**
- Business opportunity identification
- Partnership and collaboration patterns
- Meeting request success rates
- Message type performance comparison

**Contact Analysis**
- Individual prospect engagement levels
- Response rates per contact
- Relationship development tracking
- Priority contact identification

**Top Messages**
- Highest performing outreach templates
- Messages that generated responses
- Sentiment and engagement analysis
- Effective conversation starters

### Markdown Reports
- Executive summary with key metrics
- Sales performance insights
- Actionable recommendations
- Message template suggestions

## Advanced Features

### Outbound Focus
- **Conversation Initiation Detection**: Only analyzes conversations you started
- **True Outbound Filtering**: Excludes replies and inbound messages
- **Response Tracking**: Monitors which prospects engage with your outreach

### Sales Intelligence
- **Message Classification**: Automatically categorizes messages as:
  - Service/Product Offering
  - Partnership Opportunities
  - Job Seeking/Recruitment
  - Meeting Requests
  - General Business
- **Pattern Recognition**: Identifies successful message templates and approaches
- **Conversion Analysis**: Tracks which message types generate responses

### Performance Analytics
- **Response Rate Calculation**: Accurate metrics for outbound success
- **Timing Analysis**: Response time patterns and optimal outreach timing
- **Engagement Scoring**: Message quality indicators (questions, personalization, length)
- **Follow-up Tracking**: Multi-touch conversation analysis

## 🛠️ Customization

### Adding New Analysis

The modular structure makes it easy to add new analysis features:

1. **Add analysis functions** to `src/analyzer.py`
2. **Update reporting** in `src/reporter.py`
3. **Integrate in** `main.py`

### Custom Metrics

You can extend the analysis by modifying the analyzer functions:

- **Message patterns**: Regex matching for specific phrases
- **Time-based analysis**: Weekly/monthly trending
- **Industry-specific**: Custom scoring for different sectors

## 🔒 Privacy & Security

- **Local Processing**: All analysis runs on your computer
- **No API Calls**: No data sent to external services
- **No Data Storage**: Tool doesn't persist your data
- **Open Source**: Fully transparent code you can inspect

## 📝 Data Format Requirements

Your LinkedIn CSV export should include these columns:
- `CONVERSATION ID` - Thread identifier
- `FROM` - Message sender name
- `TO` - Message recipient name
- `DATE` - Message timestamp
- `CONTENT` - Message text content

## 🐛 Troubleshooting

**CSV Validation Failed?**
- Ensure you downloaded "Messages" from LinkedIn Data Privacy
- Check that the CSV has the required columns
- Try the `--validate-only` flag to see specific issues

**Import Errors?**
- Ensure you're in the virtual environment (`source venv/bin/activate`)
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.8+)

**No Messages Found?**
- Verify the CSV file path
- Check that messages exist in the date range
- Ensure the CSV isn't empty or corrupted

## Use Cases

### Sales Teams
- **Outreach Optimization**: Identify which message templates generate the highest response rates
- **Prospect Prioritization**: Focus on contacts who have shown engagement
- **Performance Tracking**: Monitor team member outbound success rates
- **Template Library**: Build a database of proven effective messages

### Business Development
- **Partnership Analysis**: Track success rates for collaboration requests
- **Market Research**: Understand response patterns across different industries
- **Relationship Mapping**: Identify warm contacts for future opportunities
- **Conversion Funnel**: Analyze the path from first contact to meeting

### Recruiting & HR
- **Candidate Engagement**: Optimize recruitment messaging and response rates
- **Talent Pipeline**: Track ongoing conversations with potential hires
- **Market Intelligence**: Understand competitive landscape through networking

## Roadmap

Future enhancements planned:

- **Interactive Dashboard**: Streamlit web interface for real-time analysis
- **Advanced AI**: GPT-powered message optimization recommendations
- **Team Analytics**: Multi-user analysis for sales teams
- **CRM Integration**: Export insights to Salesforce, HubSpot, etc.
- **Time Series Analysis**: Seasonal and trending performance insights

## Contributing

Contributions welcome! Priority areas:

- Advanced sales metrics and KPIs
- Industry-specific message classification
- Integration with popular CRM systems
- Performance visualization improvements
- Multi-language support for global teams

## 📄 License

This project is open source. See LICENSE file for details.

## ⚠️ Disclaimer

This tool is for personal analysis only. Respect LinkedIn's Terms of Service and privacy regulations. Only use with your own exported data.

---

**Built with Python 3.13 • Pandas • TextBlob • OpenPyXL**

*Your LinkedIn networking insights, analyzed locally and privately.*