import dash
from dash import html
from config import THEME, FONTS

dash.register_page(__name__, path="/ratios", name="Ratios & Analyse", order=3,
                   title="Dashboard Bancaire · Ratios")

layout = html.Div([
    html.Div([
        html.Span("EN CONSTRUCTION", style={
            "color": THEME["accent"], "fontSize": "9px",
            "letterSpacing": "3px", "fontFamily": FONTS["mono"], "fontWeight": "600"
        }),
        html.H2("Ratios & Analyse Financière", style={
            "color": THEME["text"], "fontFamily": FONTS["display"],
            "fontWeight": "300", "marginTop": "8px", "fontSize": "28px"
        }),
        html.P("Solvabilité · Liquidité · Rentabilité · ROA · ROE",
            style={"color": THEME["text_muted"], "fontFamily": FONTS["mono"],
                   "fontSize": "12px", "marginTop": "12px"}),
    ], style={"padding": "60px 40px"})
], style={"background": THEME["bg_dark"], "minHeight": "100vh"})
