# ============================================================
#  home.py — Page d'accueil avec panneau "Sources" slide-in
#  Le callback toggle_about_panel est dans app.py
# ============================================================
from dash import html, dcc
from config import get_theme, SECTOR_META, MONO, SERIF, SANS


def get_layout():
    T = get_theme()

    return html.Div([

        html.Canvas(id="particles-canvas", style={
            "position": "fixed", "top": "0", "left": "0",
            "width": "100%", "height": "100%",
            "zIndex": "0", "pointerEvents": "none",
        }),

        html.Div(id="about-backdrop", style={
            "position": "fixed", "inset": "0",
            "background": "rgba(0,0,0,0.5)",
            "zIndex": "99", "display": "none", "cursor": "pointer",
        }),

        # ── Panneau Sources ───────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div("◈", style={
                        "fontSize": "20px",
                        "background": "linear-gradient(135deg, #F0B429, #3FB950, #58A6FF)",
                        "WebkitBackgroundClip": "text",
                        "WebkitTextFillColor": "transparent",
                        "backgroundClip": "text",
                        "marginRight": "10px",
                    }),
                    html.Div("SOURCES DE DONNÉES", style={
                        "color": "#E6EDF3", "fontFamily": MONO,
                        "fontSize": "11px", "letterSpacing": "2px", "fontWeight": "600",
                    }),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Button("✕", id="about-close", n_clicks=0, style={
                    "background": "none", "border": "none",
                    "color": "#8B949E", "fontSize": "18px",
                    "cursor": "pointer", "padding": "4px 8px",
                }),
            ], style={
                "display": "flex", "alignItems": "center",
                "justifyContent": "space-between",
                "padding": "24px 28px 20px",
                "borderBottom": "1px solid #21262D",
            }),
            html.Div([
                _source_card("🏦", "#F0B429", "BCEAO",
                    "Banque Centrale des États de l'Afrique de l'Ouest",
                    "Secteur Bancaire", "2015 — 2022",
                    "24 banques · 168 enregistrements",
                    ["Bilans agrégés annuels", "Comptes de résultat",
                     "49 KPIs par établissement", "Extraction PDF automatisée (pipeline v9)"]),
                _source_card("⚡", "#3FB950", "Parc Photovoltaïque · Sénégal",
                    "Mesures capteurs terrain · Installation PV",
                    "Secteur Énergie", "2015 — 2022",
                    "Capteurs terrain · 35 000+ mesures",
                    ["Production solaire par panneau",
                     "Données d'irradiance & température",
                     "Performance et rendement PV",
                     "Séries temporelles horaires"]),
                _source_card("◉", "#58A6FF", "Compagnie d'Assurance · Confidentiel",
                    "Données réelles anonymisées · Portefeuille entreprise",
                    "Secteur Assurance", "2015 — 2022",
                    "Données réelles · Anonymisées",
                    ["Portefeuilles vie & non-vie",
                     "Sinistres et taux de liquidation",
                     "Profil des assurés",
                     "Rentabilité technique"]),
                html.Div([
                    html.Div("◆ NOTE", style={"color": "#8B949E", "fontFamily": MONO,
                        "fontSize": "8px", "letterSpacing": "2px", "marginBottom": "8px"}),
                    html.P(
                        "Toutes les données sont exprimées en millions de FCFA "
                        "sauf indication contraire. Les données 2021–2022 sont "
                        "extraites automatiquement depuis les publications officielles PDF.",
                        style={"color": "#8B949E", "fontFamily": MONO,
                               "fontSize": "10px", "lineHeight": "1.7", "margin": "0"}),
                ], style={"background": "#0D1117", "border": "1px solid #21262D",
                          "borderRadius": "8px", "padding": "16px", "marginTop": "8px"}),
            ], style={"padding": "20px 28px 28px", "overflowY": "auto", "flex": "1"}),
        ], id="about-panel", style={
            "position": "fixed", "top": "0", "right": "0",
            "width": "420px", "height": "100vh",
            "background": "#161B22", "borderLeft": "1px solid #30363D",
            "zIndex": "100", "transform": "translateX(100%)",
            "transition": "transform 0.35s cubic-bezier(0.4, 0, 0.2, 1)",
            "display": "flex", "flexDirection": "column",
            "boxShadow": "-24px 0 64px rgba(0,0,0,0.6)",
        }),

        # ── Contenu principal ─────────────────────────────────
        html.Div([
            html.Div([
                html.Div([
                    html.Div("OBSERVATOIRE ÉCONOMIQUE · SÉNÉGAL 2015–2022", style={
                        "color": T["muted"], "fontSize": "9px", "fontFamily": MONO,
                        "letterSpacing": "4px", "fontWeight": "600", "marginBottom": "20px",
                    }),
                    html.H1([
                        "Tableau de bord ", html.Br(),
                        html.Span("Multi-Secteur", style={
                            "background": "linear-gradient(135deg, #F0B429 0%, #3FB950 50%, #58A6FF 100%)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                            "backgroundClip": "text",
                        }),
                    ], style={"fontFamily": SERIF, "fontWeight": "300", "fontSize": "52px",
                              "margin": "0 0 20px", "lineHeight": "1.1", "color": T["text"]}),
                    html.P(
                        "Analyse intégrée des secteurs bancaire, énergétique et assurantiel "
                        "du Sénégal. Sources : BCEAO · Parc PV · Données confidentielles.",
                        style={"color": T["muted"], "fontFamily": SANS, "fontSize": "15px",
                               "maxWidth": "480px", "lineHeight": "1.8", "margin": "0 0 28px"}),
                    html.Button([
                        html.Span("◈ ", style={"opacity": "0.7"}),
                        "Sources de données",
                    ], id="about-open", n_clicks=0, style={
                        "background": "rgba(88,166,255,0.08)",
                        "border": "1px solid rgba(88,166,255,0.3)",
                        "borderRadius": "6px", "color": "#58A6FF",
                        "fontFamily": MONO, "fontSize": "11px",
                        "fontWeight": "600", "letterSpacing": "1.5px",
                        "padding": "10px 20px", "cursor": "pointer",
                    }),
                ], style={"flex": "1"}),
                html.Div([
                    _animated_counter("168", "enregistrements", "#F0B429", 0),
                    _animated_counter("35k+", "mesures solaires", "#3FB950", 100),
                    _animated_counter("1000", "contrats assurance", "#58A6FF", 200),
                    _animated_counter("49", "KPIs / banque", "#A78BFA", 300),
                ], style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "16px"}),
            ], style={
                "display": "flex", "alignItems": "center", "justifyContent": "space-between",
                "padding": "60px 64px 52px", "borderBottom": f"1px solid {T['border']}",
                "flexWrap": "wrap", "gap": "40px",
            }),
            html.Div([
                html.Div("▸ CHOISISSEZ UN SECTEUR", style={
                    "color": T["muted"], "fontSize": "9px", "fontFamily": MONO,
                    "letterSpacing": "3px", "fontWeight": "600", "marginBottom": "32px",
                }),
                html.Div([
                    _sector_card("bancaire", T, 500),
                    _sector_card("energie",  T, 600),
                    _sector_card("assurance",T, 700),
                ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
            ], style={"padding": "48px 64px"}),
            html.Div([
                html.Span("Données officielles · ", style={
                    "color": T["muted"], "fontFamily": MONO, "fontSize": "9px"}),
                html.Span("BCEAO · Parc PV Sénégal · Données confidentielles · M2 Big Data", style={
                    "color": T["muted"], "fontFamily": MONO, "fontSize": "9px", "opacity": "0.5"}),
            ], style={"padding": "20px 64px", "borderTop": f"1px solid {T['border']}"}),
        ], style={"position": "relative", "zIndex": "1",
                  "minHeight": "100vh", "display": "flex", "flexDirection": "column"}),

        # ── Script particules + compteurs ─────────────────────
        html.Script("""
(function() {
    function initParticles() {
        var canvas = document.getElementById('particles-canvas');
        if (!canvas) { setTimeout(initParticles, 100); return; }
        var ctx = canvas.getContext('2d');
        var W = window.innerWidth, H = window.innerHeight;
        canvas.width = W; canvas.height = H;
        var colors = ['#F0B429','#3FB950','#58A6FF','#A78BFA'];
        var particles = [];
        for (var i = 0; i < 55; i++) {
            particles.push({ x:Math.random()*W, y:Math.random()*H,
                r:Math.random()*1.5+0.3, dx:(Math.random()-0.5)*0.35,
                dy:(Math.random()-0.5)*0.35,
                color:colors[Math.floor(Math.random()*colors.length)],
                alpha:Math.random()*0.5+0.1 });
        }
        function draw() {
            ctx.clearRect(0,0,W,H);
            for (var i=0;i<particles.length;i++)
                for (var j=i+1;j<particles.length;j++) {
                    var dx=particles[i].x-particles[j].x, dy=particles[i].y-particles[j].y;
                    var d=Math.sqrt(dx*dx+dy*dy);
                    if (d<120) { ctx.beginPath(); ctx.moveTo(particles[i].x,particles[i].y);
                        ctx.lineTo(particles[j].x,particles[j].y);
                        ctx.strokeStyle='rgba(48,54,61,'+(1-d/120)*0.8+')';
                        ctx.lineWidth=0.5; ctx.stroke(); }
                }
            particles.forEach(function(p) {
                ctx.beginPath(); ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
                ctx.globalAlpha=p.alpha; ctx.fillStyle=p.color; ctx.fill(); ctx.globalAlpha=1;
                p.x+=p.dx; p.y+=p.dy;
                if(p.x<0||p.x>W) p.dx*=-1; if(p.y<0||p.y>H) p.dy*=-1;
            });
            requestAnimationFrame(draw);
        }
        draw();
        window.addEventListener('resize',function(){W=canvas.width=window.innerWidth;H=canvas.height=window.innerHeight;});
    }
    initParticles();
    function animateCounters() {
        document.querySelectorAll('.animated-counter').forEach(function(el) {
            var target=el.getAttribute('data-target');
            var isK=target.indexOf('k')>-1, isPlus=target.indexOf('+')>-1;
            var num=parseInt(target.replace(/[^0-9]/g,''));
            var start=performance.now();
            function update(now) {
                var p=Math.min((now-start)/1800,1),e=1-Math.pow(1-p,3);
                el.textContent=Math.floor(e*num)+(isK?'k':'')+(isPlus?'+':'');
                if(p<1) requestAnimationFrame(update); else el.textContent=target;
            }
            setTimeout(function(){requestAnimationFrame(update);},parseInt(el.getAttribute('data-delay')||0));
        });
    }
    setTimeout(animateCounters, 400);
})();
        """),

    ], style={"background": "#0D1117", "minHeight": "100vh", "color": "#E6EDF3"})


def _source_card(icon, accent, name, full, sector, period, coverage, items):
    h = accent.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return html.Div([
        html.Div([
            html.Span(icon, style={"fontSize": "22px", "marginRight": "12px"}),
            html.Div([
                html.Div(name, style={"color": accent, "fontFamily": MONO, "fontSize": "14px", "fontWeight": "700"}),
                html.Div(sector, style={"color": "#8B949E", "fontFamily": MONO, "fontSize": "9px"}),
            ]),
            html.Div(period, style={"color": accent, "fontFamily": MONO, "fontSize": "9px",
                                    "fontWeight": "600", "marginLeft": "auto", "opacity": "0.8"}),
        ], style={"display": "flex", "alignItems": "center", "marginBottom": "10px"}),
        html.Div(full, style={"color": "#8B949E", "fontFamily": MONO, "fontSize": "9px",
                              "marginBottom": "12px", "fontStyle": "italic"}),
        html.Div(style={"height": "1px", "background": f"linear-gradient(90deg, {accent}, transparent)",
                        "marginBottom": "12px", "opacity": "0.4"}),
        html.Div(coverage, style={
            "background": f"rgba({r},{g},{b},0.08)", "border": f"1px solid rgba({r},{g},{b},0.2)",
            "borderRadius": "4px", "padding": "4px 10px", "color": accent,
            "fontFamily": MONO, "fontSize": "9px", "display": "inline-block", "marginBottom": "12px"}),
        html.Ul([html.Li(item, style={"color": "#8B949E", "fontFamily": MONO, "fontSize": "10px",
                                      "lineHeight": "1.8", "listStyle": "none", "paddingLeft": "0"})
                 for item in items], style={"margin": "0", "padding": "0"}),
    ], style={"background": "#0D1117", "border": "1px solid #21262D",
              "borderLeft": f"3px solid {accent}", "borderRadius": "8px",
              "padding": "16px", "marginBottom": "12px"})


def _animated_counter(value, label, accent, delay):
    return html.Div([
        html.Div(value, className="animated-counter",
            **{"data-target": value, "data-delay": str(delay)},
            style={"color": accent, "fontSize": "32px", "fontWeight": "700",
                   "fontFamily": MONO, "lineHeight": "1", "marginBottom": "6px"}),
        html.Div(label, style={"color": "#8B949E", "fontSize": "9px",
                               "fontFamily": MONO, "letterSpacing": "1.5px"}),
    ], style={"background": "#161B22", "border": "1px solid #30363D",
              "borderRadius": "8px", "padding": "20px", "borderLeft": f"3px solid {accent}"})


def _sector_card(sector_key, T, delay=0):
    meta   = SECTOR_META[sector_key]
    accent = meta["accent"]
    h = accent.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)
    return dcc.Link(
        html.Div([
            html.Div(meta["icon"], style={"fontSize": "36px", "lineHeight": "1", "marginBottom": "16px"}),
            html.Div("● EN LIGNE" if meta["pages"] > 0 else "● BIENTÔT",
                style={"fontSize": "8px", "fontFamily": MONO, "letterSpacing": "1.5px",
                       "fontWeight": "600", "color": accent if meta["pages"] > 0 else T["muted"],
                       "marginBottom": "12px"}),
            html.H2(meta["label"], style={"color": T["text"], "fontFamily": SERIF,
                                          "fontWeight": "300", "fontSize": "22px", "margin": "0 0 6px"}),
            html.P(meta["sublabel"], style={"color": T["muted"], "fontFamily": MONO,
                                            "fontSize": "10px", "margin": "0 0 20px"}),
            html.Div(style={"height": "1px", "background": f"linear-gradient(90deg, {accent}, transparent)",
                            "marginBottom": "20px"}),
            html.Div([
                html.Div([
                    html.Div(str(meta["pages"]) if meta["pages"] > 0 else "—",
                        style={"color": accent, "fontSize": "28px", "fontWeight": "700",
                               "fontFamily": MONO, "lineHeight": "1"}),
                    html.Div("pages", style={"color": T["muted"], "fontSize": "9px",
                                             "fontFamily": MONO, "marginTop": "4px"}),
                ]),
                html.Div(style={"width": "1px", "background": T["border"],
                                "margin": "0 20px", "alignSelf": "stretch"}),
                html.Div([
                    html.Div("BCEAO" if sector_key=="bancaire" else "PARC PV" if sector_key=="energie" else "CONFIDENTIEL",
                        style={"color": accent, "fontSize": "14px", "fontWeight": "700", "fontFamily": MONO}),
                    html.Div("source", style={"color": T["muted"], "fontSize": "9px",
                                              "fontFamily": MONO, "marginTop": "4px"}),
                ]),
            ], style={"display": "flex", "alignItems": "center", "marginBottom": "20px"}),
            html.Div("Accéder →" if meta["pages"] > 0 else "Données en attente", style={
                "background": f"rgba({r},{g},{b},0.12)" if meta["pages"] > 0 else "transparent",
                "border": f"1px solid {accent if meta['pages'] > 0 else T['border']}",
                "color": accent if meta["pages"] > 0 else T["muted"],
                "padding": "10px 20px", "borderRadius": "6px", "fontFamily": MONO,
                "fontSize": "11px", "fontWeight": "600", "textAlign": "center"}),
        ], style={
            "background": T["card"], "border": f"1px solid {T['border']}",
            "borderRadius": "12px", "padding": "32px 28px",
            "cursor": "pointer" if meta["pages"] > 0 else "default",
            "transition": "transform 0.2s ease, box-shadow 0.2s ease",
            "borderTop": f"3px solid {accent}",
            "animation": f"fadeInUp 0.6s {delay}ms ease both",
        }, className="sector-card"),
        href=f"/{sector_key}" if meta["pages"] > 0 else "#",
        style={"textDecoration": "none", "flex": "1"})
