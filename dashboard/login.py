# ============================================================
#  login.py — Page d'authentification
# ============================================================
import os
from dash import html, dcc, Input, Output, State, callback, no_update
from config import MONO, SERIF, SANS

APP_PASSWORD = os.environ.get("APP_PASSWORD", "senegal2024")


def get_layout():
    return html.Div([
        html.Div(className="login-grid-bg"),
        html.Div([
            html.Div([
                html.Div("◈", style={
                    "fontSize": "48px",
                    "background": "linear-gradient(135deg, #F0B429, #3FB950, #58A6FF)",
                    "WebkitBackgroundClip": "text",
                    "WebkitTextFillColor": "transparent",
                    "backgroundClip": "text",
                    "lineHeight": "1", "marginBottom": "20px", "display": "block",
                }),
                html.Div("OBSERVATOIRE ÉCONOMIQUE", style={
                    "color": "#8B949E", "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "4px",
                    "fontWeight": "600", "marginBottom": "8px",
                }),
                html.H1("Sénégal", style={
                    "fontFamily": SERIF, "fontWeight": "300",
                    "fontSize": "36px", "color": "#E6EDF3",
                    "margin": "0 0 6px", "letterSpacing": "1px",
                }),
                html.Div("Dashboard Multi-Secteur", style={
                    "color": "#8B949E", "fontFamily": MONO,
                    "fontSize": "11px", "letterSpacing": "1px",
                }),
            ], style={"textAlign": "center", "marginBottom": "48px"}),

            html.Div([
                html.Div("ACCÈS SÉCURISÉ", style={
                    "color": "#8B949E", "fontSize": "9px",
                    "fontFamily": MONO, "letterSpacing": "3px",
                    "fontWeight": "600", "marginBottom": "24px",
                    "textAlign": "center",
                }),
                html.Div([
                    html.Div("MOT DE PASSE", style={
                        "color": "#8B949E", "fontSize": "9px",
                        "fontFamily": MONO, "letterSpacing": "2px",
                        "marginBottom": "8px",
                    }),
                    dcc.Input(
                        id="login-password",
                        type="password",
                        placeholder="••••••••••••",
                        debounce=True,
                        style={
                            "width": "100%", "background": "#0D1117",
                            "border": "1px solid #30363D", "borderRadius": "6px",
                            "padding": "12px 16px", "color": "#E6EDF3",
                            "fontFamily": MONO, "fontSize": "14px",
                            "outline": "none", "boxSizing": "border-box",
                            "letterSpacing": "4px",
                        },
                        n_submit=0,
                    ),
                ], style={"marginBottom": "20px"}),

                html.Div(id="login-error", style={
                    "color": "#F85149", "fontSize": "11px",
                    "fontFamily": MONO, "textAlign": "center",
                    "marginBottom": "16px", "minHeight": "16px",
                }),

                html.Button("ENTRER →", id="login-btn", n_clicks=0, style={
                    "width": "100%",
                    "background": "linear-gradient(135deg, rgba(240,180,41,0.15), rgba(63,185,80,0.15))",
                    "border": "1px solid rgba(240,180,41,0.4)",
                    "borderRadius": "6px", "color": "#F0B429",
                    "fontFamily": MONO, "fontSize": "12px",
                    "fontWeight": "600", "letterSpacing": "3px",
                    "padding": "14px", "cursor": "pointer",
                }),

                html.Div(style={
                    "height": "1px",
                    "background": "linear-gradient(90deg, transparent, #30363D, transparent)",
                    "margin": "28px 0",
                }),
                html.Div([
                    html.Span("🏦 Bancaire  ", style={"color": "#F0B429"}),
                    html.Span("⚡ Énergie  ",  style={"color": "#3FB950"}),
                    html.Span("◉ Assurance",  style={"color": "#58A6FF"}),
                ], style={
                    "textAlign": "center", "fontFamily": MONO,
                    "fontSize": "10px", "color": "#8B949E",
                }),
            ], style={
                "background": "#161B22", "border": "1px solid #30363D",
                "borderRadius": "12px", "padding": "36px",
                "borderTop": "3px solid #F0B429",
                "boxShadow": "0 24px 64px rgba(0,0,0,0.6)",
                "width": "360px",
            }),

            html.Div("BCEAO · SENELEC · CIMA · M2 Big Data", style={
                "color": "#8B949E", "fontSize": "9px",
                "fontFamily": MONO, "letterSpacing": "2px",
                "textAlign": "center", "marginTop": "32px", "opacity": "0.5",
            }),

        ], style={
            "display": "flex", "flexDirection": "column",
            "alignItems": "center", "justifyContent": "center",
            "minHeight": "100vh", "position": "relative", "zIndex": "1",
        }),

    ], style={
        "background": "#0D1117", "minHeight": "100vh",
        "position": "relative", "overflow": "hidden",
    })


# ── Callback : vérifie le mot de passe et met à jour auth-store ──
@callback(
    Output("auth-store",   "data"),
    Output("login-error",  "children"),
    Input("login-btn",      "n_clicks"),
    Input("login-password", "n_submit"),
    State("login-password", "value"),
    prevent_initial_call=True,
)
def check_login(n_clicks, n_submit, password):
    if not password:
        return no_update, "Entrez votre mot de passe."
    if password == APP_PASSWORD:
        return {"authenticated": True}, ""
    return no_update, "❌ Mot de passe incorrect."
