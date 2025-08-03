# Product Ideas Daily: Startup Idea Discovery Platform

A comprehensive platform that scrapes targeted tweets from X (Twitter), categorizes them using AI to identify pain points and product requests, and presents insights through an interactive dashboard for startup ideation.

## Overview

**What**: Automated system that scrapes tweets matching specific keywords and categorizes them into:

1. **Product Requests**: Tweets asking for tools, apps, or solutions that don't exist
2. **Pain Points**: Tweets expressing frustration about existing problems
3. **Advice Requests**: Tweets asking for recommendations or guidance
4. **Wish Lists**: Tweets wishing certain tools or features existed

**Why**: Identify unmet market needs and early startup opportunities from real user frustrations and requests.

## Architecture

The system follows a modular architecture with three main components:

- **Scraper** (`apify_scraper.py`): Uses Apify's Twitter Scraper to fetch tweets daily based on configured keywords
- **Categorizer** (`categorizer.py`): Processes tweets through Gemini 2.5 Flash to classify and extract insights
- **Dashboard** (`dashboard.py`): Interactive web interface built with Dash for visualizing results

## Tech Stack

| Component   | Technology                     | Purpose                                      |
| ----------- | ------------------------------ | -------------------------------------------- |
| Scraper     | Apify Client + Twitter Scraper | Fetch tweets with configurable filters       |
| Categorizer | Google Gemini 2.5 Flash        | AI-powered tweet analysis and classification |
| Dashboard   | Dash + Plotly + Bootstrap      | Interactive web visualization                |
| Storage     | JSON files                     | Structured data persistence                  |
| Automation  | Python scripts                 | Daily job orchestration                      |

## Features

- **Automated Daily Scraping**: Configurable keyword-based tweet collection
- **AI-Powered Analysis**: Intelligent categorization using Gemini 2.5 Flash
- **Interactive Dashboard**: Dark/light mode with date selection and filtering
- **Structured Data**: JSON-based storage with analysis results
- **Error Handling**: Comprehensive logging and error recovery
- **Responsive Design**: Mobile-friendly dashboard interface

## Project Structure

```
gummy-x/
├── apify_scraper.py      # Twitter/X scraping using Apify
├── categorizer.py        # AI-powered tweet analysis
├── dashboard.py          # Interactive web dashboard
├── daily_job.py          # Automated daily execution
├── scraper_config.json   # Scraping configuration
├── requirements.txt      # Python dependencies
├── data/
│   ├── scraped/          # Raw tweet data (DDMMYY_data.json)
│   └── analysis/         # Processed analysis results (DDMMYY_analysis.json)
├── logs/                 # Application logs
└── gummyx/              # Virtual environment
```

## Setup & Installation

### Prerequisites

- Python 3.11+
- Apify account and API token
- Google Gemini API key

### Installation

1. **Clone the repository**:

   ```bash
   git clone <repository-url>
   cd gummy-x
   ```

2. **Create and activate virtual environment**:

   ```bash
   python -m venv gummyx
   source gummyx/bin/activate  # On Windows: gummyx\Scripts\activate
   ```

3. **Install dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Create a `.env` file in the project root:

   ```env
   GEMINI_API_KEY=your_gemini_api_key_here
   APIFY_TOKEN=your_apify_token_here
   GITHUB_TOKEN=your_github_token_here  # Optional, for automated commits
   ```

5. **Configure scraping parameters**:
   Edit `scraper_config.json` to customize:
   - Keywords and search terms
   - Date ranges
   - Engagement filters (likes, replies, retweets)
   - Language and location settings

## Usage

### Manual Execution

1. **Run scraping**:

   ```bash
   python apify_scraper.py
   ```

2. **Analyze tweets**:

   ```bash
   python categorizer.py
   ```

3. **Launch dashboard**:
   ```bash
   python dashboard.py
   ```
   The dashboard will be available at `http://localhost:8050`

### Automated Daily Job

Run the complete pipeline:

```bash
python daily_job.py
```

This will:

- Execute scraping with current configuration
- Process tweets through AI analysis
- Save results to date-stamped files
- Optionally commit changes to Git

## Configuration

### Scraper Configuration (`scraper_config.json`)

Key configuration options:

- `words_or`: Array of keywords to search for (OR logic)
- `words_and`: Array of required keywords (AND logic)
- `min_likes`, `min_replies`, `min_retweets`: Engagement filters
- `since`, `until`: Date range for scraping
- `lang`: Language filter (default: "en")
- `maxItems`: Maximum tweets to collect

### Dashboard Features

- **Date Selection**: Choose from available analysis dates
- **Theme Toggle**: Switch between light and dark modes
- **Interactive Cards**: Expandable product request details
- **Tweet Examples**: View source tweets for each category
- **Error Handling**: Graceful handling of missing data

## Data Format

### Scraped Data (`data/scraped/DDMMYY_data.json`)

```json
{
  "id": "tweet_id",
  "text": "tweet_content",
  "user_handle": "@username",
  "created_at": "2025-07-26T10:30:00Z",
  "engagement_score": 15,
  "url": "https://twitter.com/..."
}
```

### Analysis Results (`data/analysis/DDMMYY_analysis.json`)

```json
{
  "total_tweets_analyzed": 150,
  "product_requests": [
    {
      "category": "Product Request",
      "description": "Tool description",
      "pain_point": "Problem being solved",
      "target_audience": "Who needs this",
      "urgency_level": "High/Medium/Low",
      "tweets": [...]
    }
  ],
  "token_usage": {"input": 5000, "output": 2000}
}
```

## Development

### Logging

All components log to the `logs/` directory:

- `apify_scraper.log`: Scraping operations
- `categorizer.log`: AI analysis operations
- `dashboard.log`: Dashboard interactions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
