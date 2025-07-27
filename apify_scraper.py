"""
Apify Twitter/X Scraper Script

This script performs Twitter/X scraping using Apify's API with configurable parameters
for finding product requests and startup ideas.
"""

import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from apify_client import ApifyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("apify_scraper.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

# Constants
TWITTER_SCRAPER_ACTOR_ID = "EvFXOhwR6wsOWmdSK"  # Twitter Scraper actor ID


class ApifyScraperConfig:
    """Configuration class for Apify Twitter scraper."""

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize scraper configuration.

        Args:
            config: Dictionary containing scraper parameters
        """
        self.blue_verified = config.get("blue_verified", False)
        self.hashtags = config.get("hashtags", False)
        self.images = config.get("images", False)
        self.lang = config.get("lang", "en")
        self.max_items = config.get("maxItems", "1000")
        self.mentions = config.get("mentions", False)
        self.min_likes = config.get("min_likes", "5")
        self.min_replies = config.get("min_replies", "2")
        self.min_retweets = config.get("min_retweets", "1")
        self.replies = config.get("replies", False)
        self.retweets = config.get("retweets", False)
        self.since = config.get("since", "2025-07-26")
        self.type = config.get("type", "Top")
        self.until = config.get("until", "2025-07-27")
        self.verified = config.get("verified", False)
        self.videos = config.get("videos", False)
        self.words_or = config.get("words_or", [])
        self.words_and = config.get("words_and", [])
        self.hashtag = config.get("hashtag", [])
        self.from_user = config.get("from_user", "")
        self.to_user = config.get("to_user", "")
        self.geocode = config.get("geocode", "")
        self.place = config.get("place", "")
        self.near = config.get("near", "")
        self.within = config.get("within", "")


class ApifyScraper:
    """Main scraper class for Apify Twitter/X scraping using official client."""

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Apify scraper.

        Args:
            api_token: Apify API token. If None, reads from APIFY_TOKEN env var.
        """
        self.api_token = api_token or os.getenv("APIFY_TOKEN")
        if not self.api_token:
            raise ValueError(
                "Apify API token is required. Set APIFY_TOKEN environment variable or pass api_token parameter."
            )

        self.client = ApifyClient(self.api_token)
        self.actor_id = TWITTER_SCRAPER_ACTOR_ID

    def run_scraper(self, config: ApifyScraperConfig) -> List[Dict[str, Any]]:
        """
        Run the Twitter scraper and get results.

        Args:
            config: Scraper configuration object

        Returns:
            List of scraped tweet data
        """
        # Prepare the Actor input
        run_input = {
            "words_and": config.words_and,
            "words_or": config.words_or,
            "hashtag": config.hashtag,
            "since": config.since,
            "until": config.until,
            "maxItems": config.max_items,
            "from_user": config.from_user,
            "to_user": config.to_user,
            "type": config.type,
            "lang": config.lang,
            "verified": config.verified,
            "blue_verified": config.blue_verified,
            "retweets": config.retweets,
            "replies": config.replies,
            "mentions": config.mentions,
            "hashtags": config.hashtags,
            "images": config.images,
            "videos": config.videos,
            "min_likes": config.min_likes,
            "min_replies": config.min_replies,
            "min_retweets": config.min_retweets,
            "geocode": config.geocode,
            "place": config.place,
            "near": config.near,
            "within": config.within,
        }

        logger.info(f"Starting Twitter scraper with actor ID: {self.actor_id}")
        logger.info(
            f"Search parameters: since={config.since}, until={config.until}, maxItems={config.max_items}"
        )
        logger.info(
            f"Search filters: words_and={config.words_and}, words_or={config.words_or}, hashtag={config.hashtag}"
        )
        logger.info(
            f"Content filters: min_likes={config.min_likes}, min_replies={config.min_replies}, min_retweets={config.min_retweets}"
        )
        logger.info(
            f"User filters: verified={config.verified}, blue_verified={config.blue_verified}"
        )
        logger.info(
            f"Content types: retweets={config.retweets}, replies={config.replies}, images={config.images}, videos={config.videos}"
        )

        # Run the Actor and wait for it to finish
        logger.info("Initiating Apify actor run...")
        run = self.client.actor(self.actor_id).call(run_input=run_input)

        if not run:
            raise RuntimeError("Apify actor run failed - no run data returned")

        logger.info(f"Scraping run completed. Dataset ID: {run['defaultDatasetId']}")
        logger.info(f"Run status: {run.get('status', 'unknown')}")
        logger.info(f"Run started at: {run.get('startedAt', 'unknown')}")
        logger.info(f"Run finished at: {run.get('finishedAt', 'unknown')}")

        # Fetch results from the run's dataset
        logger.info("Fetching results from dataset...")
        results = []
        tweet_count = 0
        retweet_count = 0
        reply_count = 0
        quote_count = 0

        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            results.append(item)

            # Count different types of content
            if item.get("isRetweet"):
                retweet_count += 1
            elif item.get("isReply"):
                reply_count += 1
            elif item.get("isQuote"):
                quote_count += 1
            else:
                tweet_count += 1

        logger.info(f"Retrieved {len(results)} total items from dataset")
        logger.info(
            f"Content breakdown: {tweet_count} tweets, {retweet_count} retweets, {reply_count} replies, {quote_count} quotes"
        )

        # Log engagement statistics if available
        if results:
            likes = [
                item.get("likesCount", 0) for item in results if item.get("likesCount")
            ]
            retweets = [
                item.get("retweetCount", 0)
                for item in results
                if item.get("retweetCount")
            ]
            replies = [
                item.get("replyCount", 0) for item in results if item.get("replyCount")
            ]

            if likes:
                logger.info(
                    f"Engagement stats - Likes: avg={sum(likes)/len(likes):.1f}, max={max(likes)}, min={min(likes)}"
                )
            if retweets:
                logger.info(
                    f"Engagement stats - Retweets: avg={sum(retweets)/len(retweets):.1f}, max={max(retweets)}, min={min(retweets)}"
                )
            if replies:
                logger.info(
                    f"Engagement stats - Replies: avg={sum(replies)/len(replies):.1f}, max={max(replies)}, min={min(replies)}"
                )

        return results

    def save_results(
        self, results: List[Dict[str, Any]], output_dir: str = "data/scraped"
    ) -> str:
        """
        Save scraping results to a JSON file.

        Args:
            results: List of scraped data
            output_dir: Directory to save results in

        Returns:
            Path to the saved file
        """
        # Create output directory if it doesn't exist
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Generate filename with current date
        date_str = datetime.now().strftime("%d%m%y")
        filename = f"{date_str}_data.json"
        file_path = output_path / filename

        # Calculate file size before saving
        data_size = len(json.dumps(results, ensure_ascii=False).encode("utf-8"))

        # Save results
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        # Get actual file size after saving
        actual_size = file_path.stat().st_size

        logger.info(f"Saved {len(results)} results to {file_path}")
        logger.info(f"File size: {actual_size:,} bytes ({actual_size/1024:.1f} KB)")
        logger.info(
            f"Estimated data size: {data_size:,} bytes ({data_size/1024:.1f} KB)"
        )

        # Log unique users if available
        if results:
            unique_users = set()
            verified_users = 0
            blue_verified_users = 0

            for item in results:
                username = item.get("username")
                if username:
                    unique_users.add(username)
                if item.get("verified"):
                    verified_users += 1
                if item.get("blueVerified"):
                    blue_verified_users += 1

            logger.info(f"Unique users found: {len(unique_users)}")
            logger.info(f"Verified users: {verified_users}")
            logger.info(f"Blue verified users: {blue_verified_users}")

        return str(file_path)


def load_config(config_file: str = "scraper_config.json") -> Dict[str, Any]:
    """
    Load configuration from JSON file.

    Args:
        config_file: Path to configuration JSON file

    Returns:
        Configuration dictionary

    Raises:
        FileNotFoundError: If config file doesn't exist
        json.JSONDecodeError: If config file is invalid JSON
    """
    config_path = Path(config_file)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_file}")

    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def update_dates_dynamically(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update the since and until dates in the config to be dynamic.

    Args:
        config: Configuration dictionary

    Returns:
        Updated configuration with dynamic dates
    """
    # Get today's date and 2 days ago
    today = datetime.now()
    two_days_ago = today - timedelta(days=2)

    # Create a copy of the config and update dates
    updated_config = config.copy()
    updated_config["since"] = two_days_ago.strftime("%Y-%m-%d")
    updated_config["until"] = today.strftime("%Y-%m-%d")

    logger.info(
        f"Updated dates: since={updated_config['since']}, until={updated_config['until']}"
    )
    return updated_config


def run_scraping_job(
    config: Optional[Dict[str, Any]] = None,
    api_token: Optional[str] = None,
) -> Optional[str]:
    """
    Run a complete scraping job.

    Args:
        config: Scraping configuration. If None, loads from JSON file.
        api_token: Apify API token. If None, reads from environment.

    Returns:
        Path to saved results file, or None if failed
    """
    start_time = datetime.now()
    logger.info("=" * 60)
    logger.info("STARTING APIFY TWITTER SCRAPING JOB")
    logger.info("=" * 60)

    try:
        # Use provided config or load from file
        if config is None:
            config = load_config()
            logger.info("Loaded configuration from scraper_config.json")

        # Update dates dynamically (2 days ago to today)
        config = update_dates_dynamically(config)

        # Initialize scraper
        logger.info("Initializing Apify scraper...")
        scraper = ApifyScraper(api_token=api_token)

        # Create config object
        scraper_config = ApifyScraperConfig(config)

        # Run scraper and get results
        logger.info("Starting scraping process...")
        results = scraper.run_scraper(scraper_config)

        # Save results
        logger.info("Saving results to file...")
        output_file = scraper.save_results(results)

        end_time = datetime.now()
        duration = end_time - start_time

        logger.info("=" * 60)
        logger.info("SCRAPING JOB COMPLETED SUCCESSFULLY")
        logger.info(f"Total duration: {duration}")
        logger.info(f"Results saved to: {output_file}")
        logger.info(f"Total items scraped: {len(results)}")
        logger.info("=" * 60)

        return output_file

    except Exception as e:
        end_time = datetime.now()
        duration = end_time - start_time

        logger.error("=" * 60)
        logger.error("SCRAPING JOB FAILED")
        logger.error(f"Duration before failure: {duration}")
        logger.error(f"Error: {e}")
        logger.error("=" * 60)
        return None


def main():
    """Main function to run the scraper."""
    try:
        print("Starting Apify Twitter/X scraper...")

        # Run the scraping job (will auto-load config from JSON or use defaults)
        result_file = run_scraping_job()

        if result_file:
            print(f"Scraping completed successfully!")
            print(f"Results saved to: {result_file}")
        else:
            print("Scraping failed. Check the logs for details.")
            sys.exit(1)

    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
