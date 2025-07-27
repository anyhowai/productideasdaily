import dash
from dash import html, dcc, Output, Input, State, MATCH
import dash_bootstrap_components as dbc
import json
import plotly.graph_objects as go

with open("../data/analysis/260725_analysis.json") as f:
    data = json.load(f)

product_data = data["product_requests"]
summary_data = data["summary"]

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

def create_card(product_data, idx, dark_mode):
    tweets = product_data["tweets"]
    background = "#212529" if dark_mode else "white"
    text_color = "white" if dark_mode else "black"
    border_color = "#444" if dark_mode else "#ccc"
    
    tweets_list = html.Div(
        children=[
            dbc.Card(
                dbc.CardBody([
                    html.Blockquote(tweet["text"], style={"color": text_color}),
                    html.Small(f"@{tweet['user_handle']} on {tweet['created_at']} — ❤️ {tweet['engagement_score']}", style={"color": text_color}),
                    html.Br(),
                    html.A("View Tweet", href=tweet["url"], target="_blank", style={"color": "#0d6efd" if not dark_mode else "#66b2ff"})
                ]),
                className="mb-2",
                style={"backgroundColor": background, "borderColor": border_color}
            )
            for tweet in tweets
        ],
        id={"type": "tweets-list", "index": idx},
        style={
            "display": "none",
            "maxHeight": "300px",
            "overflowY": "auto",
            "border": f"1px solid {border_color}",
            "borderRadius": "5px",
            "marginTop": "50px",
            "padding": "10px",
            "backgroundColor": background,
            "boxShadow": "0 4px 8px rgba(0, 0, 0, 0.1)",
            "position": "relative",
            "zIndex": "10"
        }
    )

    return dbc.Card([
        dbc.CardHeader(html.H5(f"💡 Idea {idx + 1}: {product_data['category']}", style={"color": text_color})),
        dbc.CardBody([
            html.P(f"🎯 Target: {product_data['target_audience']}", className="card-text", style={"color": text_color}),
            html.P(f"🔥 Urgency: {product_data['urgency_level']}", className="card-text", style={"color": text_color}),
            html.P(f"🧠 Description: {product_data['description']}", className="card-text", style={"color": text_color}),
            html.P(f"❗ Pain Point: {product_data['pain_point']}", className="card-text", style={"color": text_color}),
            html.Br(),
            dbc.Button("💬 Related Tweets", id={"type": "show-tweets-btn", "index": idx}, style={"marginBottom":"30px"}),
            html.Br(),
            tweets_list
        ])],
        style={"backgroundColor": background, "borderColor": border_color}, className="mb-4")

app.layout = html.Div([
    # Main header
    html.Div([
        html.H3("💡 Startup Ideas Bot", style={"flex": "1"}),
        dbc.Switch(
            id="theme-switch",
            label="Dark Mode",
            value=False,
            style={"marginLeft": "auto"}
        ),
    ], style={"display": "flex", "alignItems": "center", "padding": "10px", "borderBottom": "1px solid #ccc"}),

    # Summary Section with children list fully defined
    html.Div(
        id="summary-section",
        style={"display": "flex", "gap": "12px", "justifyContent": "center", "flexWrap": "wrap"},
        children=[
            html.Div(
                style={
                    "backgroundColor": "#f8f9fa",
                    "padding": "20px",
                    "borderRadius": "10px",
                    "minWidth": "150px",
                    "textAlign": "center",
                    "flex": "1",
                },
                children=[
                    html.H5("Total Tweets", style={"marginBottom": "10px"}),
                    html.H2(f"{summary_data['total_tweets_analyzed']:,}", style={"fontSize": "2.5rem"})
                ]
            ),
            html.Div(
                style={
                    "backgroundColor": "#f8f9fa",
                    "padding": "20px",
                    "borderRadius": "10px",
                    "minWidth": "150px",
                    "textAlign": "center",
                    "flex": "1",
                },
                children=[
                    html.H5("Product Requests", style={"marginBottom": "10px"}),
                    html.H2(f"{summary_data['product_requests_found']:,}", style={"fontSize": "2.5rem"})
                ]
            ),
            html.Div(
                style={
                    "width": "220px",
                    "height": "200px",
                    "padding": "10px",
                    "borderRadius": "10px",
                    "backgroundColor": "#f8f9fa",
                    "boxShadow": "0 2px 4px rgba(0,0,0,0.1)",
                    "textAlign": "center",
                    "flex": "1",
                },
                children=[
                    dcc.Graph(
                        id="token-usage-pie",
                        style={"height": "140px"},
                        config={"displayModeBar": False},
                    ),
                    html.Small("Total Tokens", className="text-muted d-block text-center"),
                    html.H5(f"{summary_data['token_usage']['total_tokens']:,}", className="fw-bold text-info text-center")
                ]
            )
        ]
    ),

    # Container for product idea cards
    html.Div([
        dbc.Container(id="cards-container", fluid=True)
    ], style={
        "marginTop": "240px",
        "padding": "20px",
        "overflowY": "auto",
        "maxHeight": "calc(100vh - 240px)"
    })
], id="page-content", style={
    "backgroundColor": "white",
    "color": "black",
    "height": "100vh",
    "overflow": "auto"
})


@app.callback(
    Output("cards-container", "children"),
    Input("theme-switch", "value")
)
def render_cards(dark_mode):
    return [create_card(product, idx, dark_mode) for idx, product in enumerate(product_data)]

@app.callback(
    Output({"type": "tweets-list", "index": MATCH}, "style"),
    Input({"type": "show-tweets-btn", "index": MATCH}, "n_clicks"),
    State({"type": "tweets-list", "index": MATCH}, "style")
)
def toggle_tweets_list(n_clicks, current_style):
    if n_clicks is None:
        return {"display": "none"}
    if current_style and current_style.get("display") == "none":
        return {**current_style, "display": "block"}
    return {**current_style, "display": "none"}

@app.callback(
    Output("page-content", "style"),
    Input("theme-switch", "value")
)
def toggle_page_style(dark_mode):
    if dark_mode:
        return {
            "backgroundColor": "#121212",
            "color": "white",
            "minHeight": "100vh",
            "padding": "20px"
        }
    else:
        return {
            "backgroundColor": "white",
            "color": "black",
            "minHeight": "100vh",
            "padding": "20px"
        }

@app.callback(
    Output("summary-section", "style"),
    Input("theme-switch", "value")
)
def update_summary_style(dark_mode):
    if dark_mode:
        return {
            "position": "fixed",
            "top": "0",
            "left": "0",
            "right": "0",
            "zIndex": "1000",
            "backgroundColor": "#212529",  # dark background
            "color": "white",
            "padding": "20px",
            "borderBottom": "1px solid #444",
            "display": "flex",
            "gap": "12px",
            "justifyContent": "center",
            "flexWrap": "wrap"
        }
    else:
        return {
            "position": "fixed",
            "top": "0",
            "left": "0",
            "right": "0",
            "zIndex": "1000",
            "backgroundColor": "white",
            "color": "black",
            "padding": "20px",
            "borderBottom": "1px solid #ccc",
            "display": "flex",
            "gap": "12px",
            "justifyContent": "center",
            "flexWrap": "wrap"
        }

@app.callback(
    Output("token-usage-pie", "figure"),
    Input("theme-switch", "value")
)
def update_token_pie(dark_mode):
    input_tokens = summary_data["token_usage"]["input_tokens"]
    output_tokens = summary_data["token_usage"]["output_tokens"]
    colors_dark = ["#636EFA", "#EF553B"]
    colors_light = ["#636EFA", "#EF553B"]

    fig = go.Figure(data=[
        go.Pie(
            labels=["Input Tokens", "Output Tokens"],
            values=[input_tokens, output_tokens],
            hole=0.6,
            marker=dict(colors=colors_dark if dark_mode else colors_light),
            textinfo="none",
        )
    ])
    fig.update_layout(
        showlegend=True,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color="white" if dark_mode else "black",
        margin=dict(l=0, r=0, t=0, b=0),
        height=200,
    )
    return fig

if __name__ == "__main__":
    app.run(debug=True)
