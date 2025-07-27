"""
Tweet Categorizer using Gemini 2.5 Pro

This module analyzes tweets to identify tools and products that people want,
categorizing them by type and extracting key insights for startup ideation.
"""

import json
import logging
import os
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

import google.generativeai as genai  # type: ignore
from dotenv import load_dotenv

# Configure logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_dir / "categorizer.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get date in format DDMMYY
date = datetime.now().strftime("%d%m%y")

DATA_FILE = f"data/scraped/{date}_data.json"
MODEL = "gemini-2.5-flash"
ANALYSIS_DATA_FILE = f"data/analysis/{date}_analysis.json"


@dataclass
class TweetData:
    """Structured tweet data for analysis."""

    id: str
    text: str
    user_handle: str
    created_at: str
    engagement_score: int
    url: str


@dataclass
class ProductRequest:
    """Structured product request extracted from tweets."""

    category: str
    description: str
    pain_point: str
    target_audience: str
    urgency_level: str
    tweets: List[TweetData]


@dataclass
class AnalysisResult:
    """Results from tweet analysis."""

    total_tweets_analyzed: int
    product_requests: List[ProductRequest]
    token_usage: Dict[str, int]


class TweetCategorizer:
    """Main categorizer class using Gemini 2.5 Pro for tweet analysis."""

    def __init__(self, api_key: Optional[str] = None):
        """Initialize the categorizer with Gemini API."""
        logger.info("Initializing TweetCategorizer")
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            logger.error("GEMINI_API_KEY not found in environment variables")
            raise ValueError("GEMINI_API_KEY not found in environment variables")

        logger.info(f"Configuring Gemini API with model: {MODEL}")
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(
            MODEL,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for consistent, focused responses
                top_p=0.8,  # Nucleus sampling for quality
                top_k=40,  # Limit token selection for better coherence
            ),
        )
        logger.info("TweetCategorizer initialized successfully")

    def _ensure_directory_exists(self, file_path: str) -> None:
        """Ensure the directory for the given file path exists."""
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)

    def load_tweet_data(self, file_path: str) -> List[TweetData]:
        """Load and structure tweet data from JSON file."""
        logger.info(f"Loading tweet data from: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
            logger.info(f"Successfully loaded {len(raw_data)} raw tweets from file")
        except FileNotFoundError:
            logger.error(f"Data file not found: {file_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in data file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading tweet data: {e}")
            raise

        tweets = []
        for tweet in raw_data:
            # Calculate engagement score
            engagement = (
                tweet.get("tweet_favorite_count", 0)
                + tweet.get("tweet_retweet_count", 0) * 2
                + tweet.get("tweet_reply_count", 0) * 3
            )

            tweet_data = TweetData(
                id=tweet.get("id", ""),
                text=tweet.get("tweet_text", ""),
                user_handle=tweet.get("user_handle", ""),
                created_at=tweet.get("tweet_created_at", ""),
                engagement_score=engagement,
                url=tweet.get("tweet_url", ""),
            )
            tweets.append(tweet_data)

        logger.info(f"Processed {len(tweets)} structured tweets")
        return tweets

    def create_analysis_prompt(self, tweets: List[TweetData]) -> str:
        """Create a comprehensive prompt for Gemini to analyze tweets."""
        logger.info(f"Creating analysis prompt for {len(tweets)} tweets")

        tweet_texts = []
        for tweet in tweets:
            tweet_texts.append(f"{tweet.id}: {tweet.text}")

        tweets_text = "\n".join(tweet_texts)
        logger.debug(f"Prepared {len(tweet_texts)} tweet texts for analysis")

        prompt = f"""
You are an expert startup analyst and market researcher specializing in identifying unmet market needs from social media data. Your task is to analyze tweets and extract actionable product opportunities for entrepreneurs and product managers.

## TASK
Analyze the provided tweets to identify genuine product requests and market opportunities. Extract exactly 10 product requests that represent the most promising business opportunities.

## ANALYSIS CRITERIA
For each product request, identify:

1. **Product Category**: The specific type of tool, app, or service being requested
   - Examples: "Productivity Tool", "Social Media App", "Developer Tool", "Health App", "E-commerce Solution", "Educational Platform"
   - Be specific and descriptive

2. **Description**: A clear, concise description of the desired product functionality
   - Focus on what the user wants to accomplish
   - Include key features mentioned or implied

3. **Pain Point**: The specific problem, frustration, or unmet need the user is experiencing
   - Identify the root cause of their frustration
   - Describe the current workaround or limitation

4. **Target Audience**: The primary users who would benefit from this product
   - Examples: "Developers", "Content Creators", "Small Business Owners", "Students", "Remote Workers"
   - Be specific about demographics or professional groups

5. **Urgency Level**: Assess the urgency based on language intensity and context
   - **High**: Uses words like "desperately need", "frustrated", "annoying", "wish this existed"
   - **Medium**: Shows interest but less emotional language
   - **Low**: Casual mention or curiosity

6. **Tweet IDs**: List all tweet IDs that contribute to this product request
   - Use the EXACT tweet IDs as shown in the tweet list below (e.g., "tweet-1949046525050417589")
   - Include tweets that express similar needs or pain points
   - Group related requests together

## QUALITY FILTERS
- Focus on genuine product opportunities, not casual complaints
- Prioritize requests with clear use cases and target audiences
- Look for patterns and recurring themes across multiple tweets
- Exclude requests that are too vague or already have existing solutions
- Ensure each request represents a distinct product opportunity

## OUTPUT FORMAT
Return your analysis as a JSON object with exactly this structure:

{{
    "product_requests": [
        {{
            "category": "string",
            "description": "string",
            "pain_point": "string",
            "target_audience": "string",
            "urgency_level": "High|Medium|Low",
            "tweet_ids": ["string", "string", "string"]
        }}
    ]
}}

## IMPORTANT INSTRUCTIONS
- Return ONLY the JSON object, no additional text
- Do not include markdown formatting, code blocks, or explanatory text
- Ensure the JSON is valid and properly formatted
- Include exactly 10 product requests, no more, no less
- Each product request should be distinct and represent a different opportunity
- Use tweet IDs exactly as they appear in the list below (numeric format only)

## TWEETS TO ANALYZE
{tweets_text}
"""
        logger.info("Analysis prompt created successfully")
        return prompt

    def _validate_gemini_response(self, response_text: str) -> bool:
        """Validate that the Gemini response is not empty and contains valid content."""
        if not response_text or not response_text.strip():
            logger.error("Empty response received from Gemini API")
            return False

        # Check if response looks like JSON
        if not (response_text.startswith("{") and response_text.endswith("}")):
            logger.error("Response does not appear to be valid JSON")
            return False

        # Try to parse as JSON to validate structure
        try:
            json.loads(response_text)
            return True
        except json.JSONDecodeError as e:
            logger.error(f"Response is not valid JSON: {e}")
            return False

    def analyze_tweets_with_gemini(
        self, tweets: List[TweetData]
    ) -> tuple[List[ProductRequest], Dict[str, int]]:
        """Use Gemini to analyze tweets and extract product requests."""
        if not tweets:
            logger.warning("No tweets provided for analysis")
            return [], {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

        logger.info("Starting Gemini analysis of tweets")
        prompt = self.create_analysis_prompt(tweets)

        try:
            logger.info("Sending request to Gemini API")
            response = self.model.generate_content(prompt)
            response_text = response.text
            logger.info("Received response from Gemini API")
            logger.info(f"Response text: {response_text}")

            # Clean response text
            response_text = response_text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]

            # Clean up any remaining whitespace
            response_text = response_text.strip()

            # Validate response
            if not self._validate_gemini_response(response_text):
                logger.error("Response validation failed")
                return [], {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

            # Extract token usage from response
            token_usage = {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}
            usage_metadata = response.usage_metadata
            if usage_metadata:
                token_usage = {
                    "input_tokens": usage_metadata.prompt_token_count,
                    "output_tokens": usage_metadata.candidates_token_count,
                    "total_tokens": usage_metadata.total_token_count,
                }
                logger.info(
                    f"Token usage: {token_usage['input_tokens']} input, "
                    f"{token_usage['output_tokens']} output, "
                    f"{token_usage['total_tokens']} total"
                )
            else:
                logger.warning("No token usage metadata available in response")

            # Load as JSON
            logger.debug("Parsing Gemini response as JSON")
            try:
                analysis_data = json.loads(response_text)
                logger.info("Successfully parsed Gemini response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Gemini response as JSON: {e}")
                logger.error(f"Response text: {response_text[:500]}...")
                return [], token_usage

            product_requests = []
            raw_requests = analysis_data.get("product_requests", [])
            logger.info(f"Found {len(raw_requests)} raw product requests in response")

            for item in raw_requests:
                # Convert tweets to Dict[id, tweet]
                tweets_dict = {tweet.id: tweet for tweet in tweets}
                tweet_ids = item.get("tweet_ids", [])

                # Handle tweet ID mapping with error handling
                matched_tweets = []
                for tweet_id in tweet_ids:
                    if tweet_id in tweets_dict:
                        matched_tweets.append(tweets_dict[tweet_id])
                    else:
                        logger.warning(f"Could not find tweet with ID: {tweet_id}")

                if not matched_tweets:
                    logger.warning(
                        f"Could not find matching tweets for product request with tweet IDs: {tweet_ids}"
                    )
                    matched_tweets = []

                product_request = ProductRequest(
                    category=item.get("category", "Unknown"),
                    description=item.get("description", ""),
                    pain_point=item.get("pain_point", ""),
                    target_audience=item.get("target_audience", ""),
                    urgency_level=item.get("urgency_level", "Medium"),
                    tweets=matched_tweets,
                )
                product_requests.append(product_request)

            logger.info(
                f"Successfully processed {len(product_requests)} product requests"
            )
            return product_requests, token_usage

        except Exception as e:
            logger.error(f"Error analyzing tweets with Gemini: {e}")
            return [], {"input_tokens": 0, "output_tokens": 0, "total_tokens": 0}

    def analyze_tweets(self, file_path: str) -> AnalysisResult:
        """Main analysis function that processes tweets and returns insights."""
        logger.info("Starting tweet analysis")
        logger.info(f"Loading tweet data from: {file_path}")
        all_tweets = self.load_tweet_data(file_path)

        logger.info(f"Loaded {len(all_tweets)} tweets")

        if not all_tweets:
            logger.warning("No tweets found in data file")
            return AnalysisResult(
                total_tweets_analyzed=0,
                product_requests=[],
                token_usage={"input_tokens": 0, "output_tokens": 0, "total_tokens": 0},
            )

        logger.info("Starting Gemini analysis")
        product_requests, token_usage = self.analyze_tweets_with_gemini(all_tweets)

        logger.info(f"Extracted {len(product_requests)} product requests")

        logger.info("Tweet analysis completed successfully")
        return AnalysisResult(
            total_tweets_analyzed=len(all_tweets),
            product_requests=product_requests,
            token_usage=token_usage,
        )

    def save_results(
        self,
        result: AnalysisResult,
        output_file: str = ANALYSIS_DATA_FILE,
    ):
        """Save analysis results to JSON file."""
        logger.info(f"Saving analysis results to: {output_file}")

        output_data = {
            "summary": {
                "total_tweets_analyzed": result.total_tweets_analyzed,
                "product_requests_found": len(result.product_requests),
                "token_usage": result.token_usage,
            },
            "product_requests": [
                {
                    "category": req.category,
                    "description": req.description,
                    "pain_point": req.pain_point,
                    "target_audience": req.target_audience,
                    "urgency_level": req.urgency_level,
                    "tweets": [
                        {
                            "id": tweet.id,
                            "text": tweet.text,
                            "user_handle": tweet.user_handle,
                            "created_at": tweet.created_at,
                            "engagement_score": tweet.engagement_score,
                            "url": tweet.url,
                        }
                        for tweet in req.tweets
                    ],
                }
                for req in result.product_requests
            ],
        }

        try:
            # Ensure output directory exists
            self._ensure_directory_exists(output_file)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Results successfully saved to {output_file}")
        except Exception as e:
            logger.error(f"Error saving results to {output_file}: {e}")
            raise

    def print_summary(self, result: AnalysisResult):
        """Print a formatted summary of the analysis results."""
        logger.info("Printing analysis summary")

        print("\n" + "=" * 60)
        print("TWEET ANALYSIS SUMMARY")
        print("=" * 60)

        print(f"Total tweets analyzed: {result.total_tweets_analyzed}")
        print(f"Product requests found: {len(result.product_requests)}")

        # Print token usage
        print("\nToken Usage:")
        print(f"• Input tokens: {result.token_usage['input_tokens']:,}")
        print(f"• Output tokens: {result.token_usage['output_tokens']:,}")
        print(f"• Total tokens: {result.token_usage['total_tokens']:,}")

        # Print all product requests
        print("\nALL PRODUCT REQUESTS:")
        for req in result.product_requests:
            print(f"\n{req.category}")
            print(f"   Description: {req.description}")
            print(f"   Pain Point: {req.pain_point}")
            print(f"   Target Audience: {req.target_audience}")
            print(f"   Urgency Level: {req.urgency_level}")
            print(f"   Tweet IDs: {[tweet.id for tweet in req.tweets]}")

        logger.info("Analysis summary printed successfully")


def main():
    """Main function to run the tweet analysis."""
    logger.info("Starting tweet categorizer application")

    try:
        # Initialize categorizer
        logger.info("Initializing TweetCategorizer")
        categorizer = TweetCategorizer()

        # Analyze tweets
        data_file = DATA_FILE
        logger.info(f"Checking data file: {data_file}")

        if not Path(data_file).exists():
            logger.error(f"Data file not found: {data_file}")
            print(f"Data file not found: {data_file}")
            return

        logger.info("Starting tweet analysis")
        result = categorizer.analyze_tweets(data_file)

        # Print summary
        logger.info("Printing analysis summary")
        categorizer.print_summary(result)

        # Save results
        logger.info("Saving analysis results")
        categorizer.save_results(result)

        logger.info("Analysis completed successfully")
        print("\nAnalysis complete!")

    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        print(f"Error during analysis: {e}")


if __name__ == "__main__":
    main()
