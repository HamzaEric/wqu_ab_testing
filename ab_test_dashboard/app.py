from dash import Dash, html, dcc, Input, Output
from visuals import GraphBuilder
from stats import StatsBuilder, Experiment

app = Dash(__name__)
server = app.server  # <--- ADD THIS LINE FOR GUNICORN
app.title = "A/B Testing Dashboard"

gb = GraphBuilder()
sb = StatsBuilder()
exp = Experiment()

# Global style enforcing a clean, mono-spaced developer aesthetic
base_style = {'fontFamily': 'JetBrains Mono, monospace', 'padding': '20px', 'maxWidth': '1200px', 'margin': '0 auto'}

app.layout = html.Div(style=base_style, children=[
    html.H1("ETL & A/B Testing Web Application Dashboard", style={'textAlign': 'center'}),
    html.Hr(),

    # --- TOP SECTION: ALL CONFIGURATIONS ---
    html.H2("1. Applicant Demographics Selection"),
    dcc.Dropdown(
        id="demo-chart-dropdown",
        options=["Nationality Map", "Age Histogram", "Education Bar Chart"],
        value="Nationality Map",
        style={'width': '50%', 'marginBottom': '20px'}
    ),

    html.Hr(),

    html.H2("2. Experiment Configuration"),
    html.Label("Minimum Detectable Effect Size:"),
    dcc.Slider(
        id="effect-size-slider", min=0.01, max=0.5, step=0.01, value=0.05,
        marks={i / 10: str(i / 10) for i in range(1, 6)}
    ),
    html.Div(id="experiment-stats-output", style={'marginTop': '20px', 'fontWeight': 'bold'}),

    html.Hr(),

    # --- MIDDLE SECTION: ACTION BUTTON ---
    html.H2("3. Run Simulation"),
    html.Button(
        "Run Chi-Square Test", id="run-experiment-button", n_clicks=0,
        style={'padding': '10px 20px', 'fontSize': '16px', 'cursor': 'pointer', 'fontFamily': 'JetBrains Mono',
               'backgroundColor': '#f0f0f0'}
    ),

    html.Hr(),

    # --- BOTTOM SECTION: ALL GRAPHS AND RESULTS ---
    html.H2("4. Dashboard Results"),

    # 1. Text verdict of the experiment
    html.Div(id="chi-square-results", style={'marginTop': '20px', 'fontSize': '18px', 'marginBottom': '30px'}),

    # 2. Demographics Graph outputs here
    html.Div(id="demo-chart-output", style={'marginBottom': '50px'}),

    # 3. Chi-Square Graph outputs here
    html.Div(id="results-graph-output")
])


# --- CALLBACKS ---

@app.callback(
    Output("demo-chart-output", "children"),
    Input("demo-chart-dropdown", "value")
)
def update_demo_chart(selection):
    if selection == "Nationality Map":
        return dcc.Graph(figure=gb.build_nat_choropleth())
    elif selection == "Age Histogram":
        return dcc.Graph(figure=gb.build_age_hist())
    elif selection == "Education Bar Chart":
        return dcc.Graph(figure=gb.build_ed_bar())


@app.callback(
    Output("experiment-stats-output", "children"),
    Input("effect-size-slider", "value")
)
def update_experiment_stats(effect_size):
    n_obs = sb.calculate_n_obs(effect_size=effect_size)
    return f"Required Sample Size per group: {n_obs} applicants"


@app.callback(
    Output("chi-square-results", "children"),
    Output("results-graph-output", "children"),
    Input("run-experiment-button", "n_clicks"),
    prevent_initial_call=True
)
def run_and_display_results(n_clicks):
    contingency_table, chi2, p_value = exp.run_chi_square()

    if p_value is None:
        return "Not enough data to run the experiment.", dcc.Graph(figure=gb.build_contingency_bar())

    verdict = "Statistically Significant! Reject the Null Hypothesis." if p_value < 0.05 else "Not Statistically Significant. Fail to reject the Null Hypothesis."

    results_text = html.Div([
        html.P(f"Chi-Square Statistic: {chi2:.4f}"),
        html.P(f"P-Value: {p_value:.4f}"),
        html.P(f"Verdict: {verdict}",
               style={'color': '#d9534f' if p_value >= 0.05 else '#5cb85c', 'fontWeight': 'bold'})
    ])

    return results_text, dcc.Graph(figure=gb.build_contingency_bar())


if __name__ == "__main__":
    # dev_tools_ui=False hides the white error popup box
    app.run(debug=True, dev_tools_ui=False, port=8050)