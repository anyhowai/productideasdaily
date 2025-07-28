#!/usr/bin/env python3
"""
Daily Job Script

Runs scraping and categorization, then pushes data to GitHub.
"""

import logging
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def run_scraping() -> bool:
    """Run the scraper."""
    try:
        logger.info("Starting scraping...")
        from apify_scraper import run_scraping_job

        result_file = run_scraping_job()
        if result_file and Path(result_file).exists():
            logger.info(f"Scraping completed: {result_file}")
            return True
        else:
            logger.error("Scraping failed")
            return False
    except Exception as e:
        logger.error(f"Scraping error: {e}")
        return False


def run_categorization() -> bool:
    """Run the categorizer."""
    try:
        logger.info("Starting categorization...")
        from categorizer import TweetCategorizer

        # Get today's data file
        today = datetime.now(timezone.utc).strftime("%d%m%y")
        data_file = f"data/scraped/{today}_data.json"

        if not Path(data_file).exists():
            logger.error(f"Data file not found: {data_file}")
            return False

        categorizer = TweetCategorizer()
        result = categorizer.analyze_tweets(data_file)
        categorizer.save_results(result)

        logger.info("Categorization completed")
        return True
    except Exception as e:
        logger.error(f"Categorization error: {e}")
        return False


def configure_git() -> bool:
    """Configure Git for automated environment."""
    try:
        # Set Git user info if not already set
        subprocess.run(
            ["git", "config", "--global", "user.name", "Product Ideas Bot"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            ["git", "config", "--global", "user.email", "tohpinren@gmail.com"],
            check=True,
            capture_output=True,
        )

        # Configure credential helper for automated environments
        subprocess.run(
            ["git", "config", "--global", "credential.helper", "store"],
            check=True,
            capture_output=True,
        )

        # If GitHub token is available, configure it
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            # Update remote URL to include token
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"], capture_output=True, text=True
            )
            if result.returncode == 0:
                remote_url = result.stdout.strip()
                if remote_url.startswith("https://github.com/"):
                    # Replace with token-based URL
                    new_url = remote_url.replace(
                        "https://github.com/", f"https://{github_token}@github.com/"
                    )
                    subprocess.run(
                        ["git", "remote", "set-url", "origin", new_url],
                        check=True,
                        capture_output=True,
                    )
                    logger.info("GitHub token configured")

        logger.info("Git configured for automated environment")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Git configuration error: {e}")
        return False


def push_to_github() -> bool:
    """Commit and push data changes to GitHub."""
    try:
        logger.info("Pushing data to GitHub...")

        # Check if we're in a git repo
        if not Path(".git").exists():
            logger.warning("Not in git repository")
            return True

        # Check if there are changes in data directory
        result = subprocess.run(
            ["git", "status", "--porcelain", "data/"], capture_output=True, text=True
        )

        if not result.stdout.strip():
            logger.info("No changes in data directory to commit")
            return True

        # Add only data directory changes
        subprocess.run(["git", "add", "data/"], check=True, capture_output=True)

        # Check if there are staged changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"], capture_output=True, text=True
        )

        if not result.stdout.strip():
            logger.info("No staged changes to commit")
            return True

        # Commit
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        commit_msg = f"Daily data update - {date_str}"
        subprocess.run(
            ["git", "commit", "-m", commit_msg], check=True, capture_output=True
        )

        # Push
        subprocess.run(["git", "push"], check=True, capture_output=True)

        logger.info("Successfully pushed data to GitHub")
        return True

    except subprocess.CalledProcessError as e:
        logger.error(f"Git error: {e}")
        return False
    except Exception as e:
        logger.error(f"Push error: {e}")
        return False


def main():
    """Main execution."""
    logger.info("Starting daily job...")

    # Validate environment
    if not os.getenv("APIFY_TOKEN") or not os.getenv("GEMINI_API_KEY"):
        logger.error(
            "Missing required environment variables: APIFY_TOKEN, GEMINI_API_KEY"
        )
        sys.exit(1)

    # Check for GitHub token
    if not os.getenv("GITHUB_TOKEN"):
        logger.warning(
            "GITHUB_TOKEN not set - Git push may fail in automated environments"
        )

    # Run scraping
    if not run_scraping():
        logger.error("Job failed at scraping stage")
        sys.exit(1)

    # Run categorization
    if not run_categorization():
        logger.error("Job failed at categorization stage")
        sys.exit(1)

    # Configure Git and push to GitHub
    configure_git()
    push_to_github()

    logger.info("Daily job completed successfully")


if __name__ == "__main__":
    main()
