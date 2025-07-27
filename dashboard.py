"""
Dashboard application for displaying startup ideas analysis.

This module provides a Dash-based web interface for visualizing product requests
and related tweet data from analysis results.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

import dash
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from dash import MATCH, Input, Output, State, dcc, html

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("dashboard.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


# Constants
def get_analysis_data_file() -> Path:
    """
    Get the analysis data file path for the current date.

    Returns:
        Path to the analysis data file for today's date
    """
    today = datetime.now()
    date_str = today.strftime("%d%m%y")  # Format: DDMMYY
    return Path(f"data/analysis/{date_str}_analysis.json")


ANALYSIS_DATA_FILE = get_analysis_data_file()
DEFAULT_COLORS = {
    "primary": "#0d6efd",
    "secondary": "#6c757d",
    "success": "#198754",
    "danger": "#dc3545",
    "warning": "#ffc107",
    "info": "#0dcaf0",
    "light": "#f8f9fa",
    "dark": "#212529",
}

DARK_MODE_COLORS = {
    "background": "#121212",
    "card_background": "#212529",
    "text": "white",
    "border": "#444",
    "link": "#66b2ff",
}

LIGHT_MODE_COLORS = {
    "background": "white",
    "card_background": "white",
    "text": "black",
    "border": "#ccc",
    "link": "#0d6efd",
}

# Global state for error handling
data_load_error: Optional[str] = None
product_data: List[Dict[str, Any]] = []
summary_data: Dict[str, Any] = {}


# Data loading
def load_analysis_data(file_path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Load analysis data from JSON file.

    Args:
        file_path: Path to the analysis data file

    Returns:
        Tuple of (product_data, summary_data)

    Raises:
        FileNotFoundError: If the data file doesn't exist
        json.JSONDecodeError: If the file contains invalid JSON
        KeyError: If required keys are missing from the data
        PermissionError: If the file cannot be read due to permissions
    """
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        if not isinstance(data, dict):
            raise ValueError("Data file must contain a JSON object")

        if "product_requests" not in data:
            raise KeyError("Missing 'product_requests' key in data file")

        if "summary" not in data:
            raise KeyError("Missing 'summary' key in data file")

        product_requests = data["product_requests"]
        summary = data["summary"]

        if not isinstance(product_requests, list):
            raise ValueError("'product_requests' must be a list")

        if not isinstance(summary, dict):
            raise ValueError("'summary' must be a dictionary")

        logger.info(f"Successfully loaded {len(product_requests)} product requests")
        return product_requests, summary

    except FileNotFoundError:
        error_msg = f"Analysis data file not found: {file_path}"
        logger.error(error_msg)
        raise FileNotFoundError(error_msg)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in analysis data file: {e}"
        logger.error(error_msg)
        raise json.JSONDecodeError(error_msg, e.doc, e.pos)
    except KeyError as e:
        error_msg = f"Missing required key in analysis data: {e}"
        logger.error(error_msg)
        raise KeyError(error_msg)
    except PermissionError as e:
        error_msg = f"Permission denied reading data file: {e}"
        logger.error(error_msg)
        raise PermissionError(error_msg)
    except ValueError as e:
        error_msg = f"Invalid data format: {e}"
        logger.error(error_msg)
        raise ValueError(error_msg)


def load_data_with_error_handling() -> (
    Tuple[List[Dict[str, Any]], Dict[str, Any], Optional[str]]
):
    """
    Load data with comprehensive error handling and user-friendly messages.

    Returns:
        Tuple of (product_data, summary_data, error_message)
    """
    global data_load_error

    try:
        product_data, summary_data = load_analysis_data(ANALYSIS_DATA_FILE)
        data_load_error = None
        return product_data, summary_data, None

    except FileNotFoundError:
        error_msg = "Data file not found. Please ensure the analysis data file exists in the correct location."
        logger.error(f"Data loading failed: {error_msg}")
        data_load_error = error_msg
        return [], {}, error_msg

    except json.JSONDecodeError:
        error_msg = (
            "Data file contains invalid JSON format. Please check the file structure."
        )
        logger.error(f"Data loading failed: {error_msg}")
        data_load_error = error_msg
        return [], {}, error_msg

    except KeyError as e:
        error_msg = f"Data file is missing required information: {e}. Please regenerate the analysis data."
        logger.error(f"Data loading failed: {error_msg}")
        data_load_error = error_msg
        return [], {}, error_msg

    except PermissionError:
        error_msg = "Cannot read the data file due to permission restrictions. Please check file permissions."
        logger.error(f"Data loading failed: {error_msg}")
        data_load_error = error_msg
        return [], {}, error_msg

    except ValueError as e:
        error_msg = (
            f"Data file has invalid format: {e}. Please regenerate the analysis data."
        )
        logger.error(f"Data loading failed: {error_msg}")
        data_load_error = error_msg
        return [], {}, error_msg

    except Exception as e:
        error_msg = f"An unexpected error occurred while loading data: {str(e)}"
        logger.error(f"Data loading failed with unexpected error: {e}", exc_info=True)
        data_load_error = error_msg
        return [], {}, error_msg


# Load data with error handling
product_data, summary_data, data_load_error = load_data_with_error_handling()


def reload_data() -> None:
    """
    Reload data and update global state.
    """
    global product_data, summary_data, data_load_error, ANALYSIS_DATA_FILE
    logger.info("Attempting to reload data...")
    # Update the file path to current date
    ANALYSIS_DATA_FILE = get_analysis_data_file()
    product_data, summary_data, data_load_error = load_data_with_error_handling()
    if data_load_error:
        logger.warning(f"Data reload failed: {data_load_error}")
    else:
        logger.info("Data reload successful")


# Initialize Dash app
app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
)


def get_theme_colors(dark_mode: bool) -> Dict[str, str]:
    """
    Get color scheme based on theme mode.

    Args:
        dark_mode: Whether dark mode is enabled

    Returns:
        Dictionary of color values for the theme
    """
    return DARK_MODE_COLORS if dark_mode else LIGHT_MODE_COLORS


def create_error_alert(error_message: str, colors: Dict[str, str]) -> dbc.Alert:
    """
    Create an error alert component for displaying data loading errors.

    Args:
        error_message: The error message to display
        colors: Theme color dictionary

    Returns:
        Dash Bootstrap Alert component
    """
    return dbc.Alert(
        [
            html.H4("Data Loading Error", className="alert-heading"),
            html.P(error_message),
            html.Hr(),
            html.P("Please check the following:", className="mb-0"),
            html.Ul(
                [
                    html.Li("The analysis data file exists in the correct location"),
                    html.Li("The file has proper read permissions"),
                    html.Li("The file contains valid JSON data"),
                    html.Li("The data structure matches the expected format"),
                ]
            ),
            html.Hr(),
            dbc.Button(
                "Retry Loading Data",
                id="retry-load-btn",
                color="primary",
                size="sm",
                style={"marginTop": "10px"},
            ),
        ],
        color="danger",
        dismissable=True,
        style={
            "backgroundColor": colors["card_background"],
            "borderColor": colors["border"],
            "color": colors["text"],
        },
    )


def create_loading_spinner() -> dbc.Spinner:
    """
    Create a loading spinner component.

    Returns:
        Dash Bootstrap Spinner component
    """
    return dbc.Spinner(
        html.Div("Loading data..."), color="primary", type="border", fullscreen=True
    )


def create_tweet_card(tweet: Dict[str, Any], colors: Dict[str, str]) -> dbc.Card:
    """
    Create a card component for a single tweet.

    Args:
        tweet: Tweet data dictionary
        colors: Theme color dictionary

    Returns:
        Dash Bootstrap Card component
    """
    return dbc.Card(
        dbc.CardBody(
            [
                html.Blockquote(tweet["text"], style={"color": colors["text"]}),
                html.Small(
                    f"@{tweet['user_handle']} on {tweet['created_at']} — {tweet['engagement_score']}",
                    style={"color": colors["text"]},
                ),
                html.Br(),
                html.A(
                    "View Tweet",
                    href=tweet["url"],
                    target="_blank",
                    style={"color": colors["link"]},
                ),
            ]
        ),
        className="mb-2",
        style={
            "backgroundColor": colors["card_background"],
            "borderColor": colors["border"],
        },
    )


def create_tweets_list(
    tweets: List[Dict[str, Any]], idx: int, colors: Dict[str, str]
) -> html.Div:
    """
    Create a collapsible list of tweets.

    Args:
        tweets: List of tweet dictionaries
        idx: Index for component identification
        colors: Theme color dictionary

    Returns:
        Dash HTML Div component containing tweets
    """
    return html.Div(
        children=[create_tweet_card(tweet, colors) for tweet in tweets],
        id={"type": "tweets-list", "index": idx},
        style={
            "display": "none",
            "maxHeight": "300px",
            "overflowY": "auto",
            "border": f"1px solid {colors['border']}",
            "borderRadius": "5px",
            "marginTop": "50px",
            "padding": "10px",
            "backgroundColor": colors["card_background"],
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            "position": "relative",
            "zIndex": "10",
        },
    )


def create_product_card(
    product_data: Dict[str, Any], idx: int, dark_mode: bool
) -> dbc.Card:
    """
    Create a card component for a product idea.

    Args:
        product_data: Product data dictionary
        idx: Index for component identification
        dark_mode: Whether dark mode is enabled

    Returns:
        Dash Bootstrap Card component
    """
    colors = get_theme_colors(dark_mode)
    tweets = product_data.get("tweets", [])

    tweets_list = create_tweets_list(tweets, idx, colors)

    return dbc.Card(
        [
            dbc.CardHeader(
                html.H5(
                    f"Idea {idx + 1}: {product_data['category']}",
                    style={"color": colors["text"]},
                )
            ),
            dbc.CardBody(
                [
                    html.P(
                        f"Target: {product_data['target_audience']}",
                        className="card-text",
                        style={"color": colors["text"]},
                    ),
                    html.P(
                        f"Description: {product_data['description']}",
                        className="card-text",
                        style={"color": colors["text"]},
                    ),
                    html.P(
                        f"Pain Point: {product_data['pain_point']}",
                        className="card-text",
                        style={"color": colors["text"]},
                    ),
                    html.Br(),
                    dbc.Button(
                        "Related Tweets",
                        id={"type": "show-tweets-btn", "index": idx},
                        style={"marginBottom": "30px"},
                    ),
                    html.Br(),
                    tweets_list,
                ]
            ),
        ],
        style={
            "backgroundColor": colors["card_background"],
            "borderColor": colors["border"],
        },
        className="mb-4",
    )


# App layout
app.layout = html.Div(
    [
        # Header with theme switch
        html.Div(
            [
                html.Div(
                    [
                        html.H3("10 Product Ideas of the Day", style={"margin": "0"}),
                        html.P(
                            datetime.now().strftime("%B %d, %Y"),
                            style={"margin": "0", "fontSize": "14px", "color": "#666"},
                        ),
                    ],
                    style={"flex": "1"},
                ),
                dbc.Switch(
                    id="theme-switch",
                    label="Dark Mode",
                    value=False,
                    style={"marginLeft": "auto"},
                ),
            ],
            id="header",
            style={
                "display": "flex",
                "alignItems": "center",
                "padding": "10px",
                "borderBottom": "1px solid #ccc",
                "backgroundColor": "white",
            },
        ),
        # Error container
        html.Div(id="error-container"),
        # Cards container
        html.Div(
            [dbc.Container(id="cards-container", fluid=True)],
            style={
                "marginTop": "20px",
                "padding": "20px",
                "overflowY": "auto",
                "maxHeight": "calc(100vh - 80px)",
            },
        ),
    ],
    id="page-content",
    style={
        "backgroundColor": "white",
        "color": "black",
        "height": "100vh",
        "overflow": "auto",
    },
)


# Callbacks
@app.callback(
    [
        Output("header", "style"),
        Output("error-container", "children"),
    ],
    [Input("theme-switch", "value")],
)
def render_error_and_header(
    dark_mode: bool,
) -> Tuple[Dict[str, str], List[Union[dbc.Alert, html.Div]]]:
    """
    Render error alerts and update header styling based on data loading status.

    Args:
        dark_mode: Whether dark mode is enabled

    Returns:
        Tuple of (header_style, error_components)
    """
    colors = get_theme_colors(dark_mode)

    # Update header styling
    header_style = {
        "display": "flex",
        "alignItems": "center",
        "padding": "10px",
        "borderBottom": f"1px solid {colors['border']}",
        "backgroundColor": colors["card_background"],
    }

    # Handle error state
    if data_load_error:
        error_components = [create_error_alert(data_load_error, colors)]
    else:
        error_components = []

    return header_style, error_components


@app.callback(Output("cards-container", "children"), Input("theme-switch", "value"))
def render_cards(dark_mode: bool) -> List[Union[dbc.Card, html.Div]]:
    """
    Render product idea cards based on theme and data availability.

    Args:
        dark_mode: Whether dark mode is enabled

    Returns:
        List of card components or error message
    """
    colors = get_theme_colors(dark_mode)

    if data_load_error:
        return [
            html.Div(
                "No product data available. Please fix the data loading error above.",
                style={
                    "textAlign": "center",
                    "padding": "40px",
                    "color": colors["text"],
                    "backgroundColor": colors["card_background"],
                    "border": f"1px solid {colors['border']}",
                    "borderRadius": "5px",
                    "margin": "20px",
                },
            )
        ]

    if not product_data:
        return [
            html.Div(
                "No product data found in the analysis file.",
                style={
                    "textAlign": "center",
                    "padding": "40px",
                    "color": colors["text"],
                    "backgroundColor": colors["card_background"],
                    "border": f"1px solid {colors['border']}",
                    "borderRadius": "5px",
                    "margin": "20px",
                },
            )
        ]

    return [
        create_product_card(product, idx, dark_mode)
        for idx, product in enumerate(product_data)
    ]


@app.callback(
    Output({"type": "tweets-list", "index": MATCH}, "style"),
    Input({"type": "show-tweets-btn", "index": MATCH}, "n_clicks"),
    State({"type": "tweets-list", "index": MATCH}, "style"),
)
def toggle_tweets_list(
    n_clicks: Optional[int], current_style: Optional[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Toggle visibility of tweets list.

    Args:
        n_clicks: Number of button clicks
        current_style: Current style dictionary

    Returns:
        Updated style dictionary
    """
    if n_clicks is None:
        style = (current_style or {}).copy()
        style["display"] = "none"
        return style

    if current_style and current_style.get("display") == "none":
        style = current_style.copy()
        style["display"] = "block"
        return style
    return {**(current_style or {}), "display": "none"}


@app.callback(Output("page-content", "style"), Input("theme-switch", "value"))
def toggle_page_style(dark_mode: bool) -> Dict[str, str]:
    """
    Update page styling based on theme.

    Args:
        dark_mode: Whether dark mode is enabled

    Returns:
        Style dictionary for page content
    """
    colors = get_theme_colors(dark_mode)
    return {
        "backgroundColor": colors["background"],
        "color": colors["text"],
        "minHeight": "100vh",
        "padding": "20px",
    }


@app.callback(Output("header", "children"), Input("theme-switch", "value"))
def update_header_text_color(dark_mode: bool) -> html.Div:
    """
    Update header text color based on theme.

    Args:
        dark_mode: Whether dark mode is enabled

    Returns:
        Header component with updated text color
    """
    colors = get_theme_colors(dark_mode)
    return html.Div(
        [
            html.Div(
                [
                    html.H3(
                        "10 Product Ideas of the Day",
                        style={"margin": "0", "color": colors["text"]},
                    ),
                    html.P(
                        datetime.now().strftime("%B %d, %Y"),
                        style={
                            "margin": "0",
                            "fontSize": "14px",
                            "color": colors["text"] if dark_mode else "#666",
                        },
                    ),
                ],
                style={"flex": "1"},
            ),
            dbc.Switch(
                id="theme-switch",
                label="Dark Mode",
                value=dark_mode,
                style={"marginLeft": "auto"},
            ),
        ],
    )


@app.callback(
    [
        Output("error-container", "children", allow_duplicate=True),
        Output("cards-container", "children", allow_duplicate=True),
    ],
    Input("retry-load-btn", "n_clicks"),
    prevent_initial_call=True,
)
def handle_retry_load(
    n_clicks: Optional[int],
) -> Tuple[
    List[Union[dbc.Alert, html.Div]],
    List[Union[dbc.Card, html.Div]],
]:
    """
    Handle retry button click to reload data.

    Args:
        n_clicks: Number of button clicks

    Returns:
        Tuple of (error_components, card_components)
    """
    if n_clicks is None:
        raise dash.exceptions.PreventUpdate

    reload_data()

    # Re-render all components with updated data
    colors = get_theme_colors(False)  # Default to light mode for retry

    if data_load_error:
        error_components = [create_error_alert(data_load_error, colors)]
        card_components = [
            html.Div(
                "No product data available. Please fix the data loading error above.",
                style={
                    "textAlign": "center",
                    "padding": "40px",
                    "color": colors["text"],
                    "backgroundColor": colors["card_background"],
                    "border": f"1px solid {colors['border']}",
                    "borderRadius": "5px",
                    "margin": "20px",
                },
            )
        ]
    else:
        error_components = []

        if not product_data:
            card_components = [
                html.Div(
                    "No product data found in the analysis file.",
                    style={
                        "textAlign": "center",
                        "padding": "40px",
                        "color": colors["text"],
                        "backgroundColor": colors["card_background"],
                        "border": f"1px solid {colors['border']}",
                        "borderRadius": "5px",
                        "margin": "20px",
                    },
                )
            ]
        else:
            card_components = [
                create_product_card(product, idx, False)
                for idx, product in enumerate(product_data)
            ]

    return error_components, card_components


if __name__ == "__main__":
    app.run(debug=True)
