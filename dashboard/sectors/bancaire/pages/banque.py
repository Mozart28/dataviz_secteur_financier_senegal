import dash
from dash import html
from config import THEME, FONTS

dash.register_page(__name__, path="/banque", name="Profil Banque", order=1,
                   title="Dashboard Bancaire · Profil Banque")

layout = html.Div([
    html.Div([
        html.Span("EN CONSTRUCTION", style={
            "color": THEME["accent"], "fontSize": "9px",
            "letterSpacing": "3px", "fontFamily": FONTS["mono"], "fontWeight": "600"
        }),
        html.H2("Profil Banque", style={
            "color": THEME["text"], "fontFamily": FONTS["display"],
            "fontWeight": "300", "marginTop": "8px", "fontSize": "28px"
        }),
        html.P("Évolution des KPIs par banque · Ratios financiers · Export PDF",
            style={"color": THEME["text_muted"], "fontFamily": FONTS["mono"],
                   "fontSize": "12px", "marginTop": "12px"}),
    ], style={"padding": "60px 40px"})
], style={"background": THEME["bg_dark"], "minHeight": "100vh"})
