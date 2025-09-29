# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a LinkedIn message analysis project that processes LinkedIn conversation exports. The project analyzes CSV exports of LinkedIn messages to extract insights about conversations and connections.

## Development Commands

**Environment Setup:**
```bash
# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run analysis (when main script exists)
python src/parser.py
```

## Project Structure

- `src/` - Source code modules
  - `parser.py` - Core CSV parsing functionality for LinkedIn message exports
- `data/` - LinkedIn message CSV exports (contains sample data)
- `notebooks/` - Jupyter notebooks for analysis
- `outputs/` - Generated analysis outputs
- `venv/` - Python virtual environment (Python 3.13.7)

## Project-Specific Rules

### Data Privacy and Security
- **NEVER** commit actual LinkedIn message data to version control
- Use only sanitized sample data in `data/messages_test_sample.csv`
- Always work with anonymized or test data for development
- Be cautious with personal information in message content

### Code Standards
- Follow pandas best practices for CSV processing
- Use type hints for all function parameters and returns
- Handle timestamp parsing errors gracefully with `errors="coerce"`
- Normalize column names consistently (lowercase with underscores)

### Data Processing Guidelines
- Always validate CSV structure before processing
- Use UTC timestamps throughout the application
- Handle missing or malformed data gracefully
- Preserve original conversation threading via `thread_id`

### Development Workflow
- Test parsing functions with the sample CSV data first
- Create Jupyter notebooks in `notebooks/` for exploratory analysis
- Save processed outputs to `outputs/` directory
- Keep source code modular in separate files under `src/`

## Architecture Notes

- **Data Processing**: Uses pandas for CSV manipulation and datetime conversion
- **Column Normalization**: Headers are cleaned and standardized in `parser.py:load_messages_csv()`
- **Timestamp Handling**: Converts LinkedIn UTC timestamps to pandas datetime objects
- **Error Handling**: Uses `errors="coerce"` for timestamp parsing to handle malformed dates

## Data Format

LinkedIn message export CSV structure:
- `CONVERSATION ID` → `thread_id`
- `FROM` → `sender`
- `TO` → `recipient`
- `DATE` → `timestamp`
- `CONTENT` → `content`
- Profile URLs preserved for relationship mapping