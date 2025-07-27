# Startup Idea Discovery

Product that scrapes targeted tweets from X, categorizes them using an LLM into pain points or idea requests, and presents them in a dashboard for quick ideation.

## Overview

**What**: Scrape tweets matching keywords for tweets that fall into these categories:

1. Pain and anger: Tweets that express anger or frustration about something
2. Advice requests: Tweets asking for advice
3. Solution requests: Tweets asking for a solution for problem
4. Wish this exists tweets

**Why**: Identify unmet needs and early startup ideas from user frustrations.

## Workflow

Daily Scraper → Storage -> LLM Categorizer → Dashboard

## Architecture

- **Scraper**: Queries X using Scweet Twitter (X) Scraper on Apify; runs once daily, saves tweets to a database
- **Categorizer**: Feeds tweets into Gemini 2.5 Flash to classify and summarize, saves insights into database
- **Dashboard**: Web UI displaying categories, counts, and examples

## Tech Stack

| Component   | Role                          | Example Tech               |
| ----------- | ----------------------------- | -------------------------- |
| Scraper     | Fetch tweets daily per query  | Apify (Scweet actor)       |
| Categorizer | LLM classification & summary  | Gemini 2.5 Flash           |
| Storage     | Persist structured output     | PostgreSQL or MongoDB      |
| Dashboard   | Visualize themes and examples | React, Vue, or static page |

## Setup & Usage

1. **Clone the repository**
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Create `.env` file** with:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
4. **Configure scraper queries and run on apify website to generate .json data.**
5. **Run the tweet analysis**:
   ```bash
   python categorizer.py
   ```

## Project Structure

```
/
├── categorizer.py      # LLM prompt and output processing
├── dashboard/          # Frontend application code
├── data/               # Raw and categorized tweet data
└── README.md           # This document
```
