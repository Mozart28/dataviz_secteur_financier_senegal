# ============================================================
#  home.py — Page d'accueil avec particules + compteurs animés
# ============================================================
from dash import html, dcc
from config import get_theme, SECTOR_META, MONO, SERIF, SANS


def get_layout():
    T = get_theme()

    return html.Div([

        # ── Canvas particules (JS inline) ─────────────────────
        html.Canvas(id="particles-canvas", style={
            "position": "fixed", "top": "0", "left": "0",
            "width": "100%", "height": "100%",
            "zIndex": "0", "pointerEvents": "none",
        }),

        # ── Contenu principal ─────────────────────────────────
        html.Div([

            # Hero
            html.Div([
                html.Div([
                    html.Div("OBSERVATOIRE ÉCONOMIQUE · SÉNÉGAL 2015–2022", style={
                        "color": T["muted"], "fontSize": "9px",
                        "fontFamily": MONO, "letterSpacing": "4px",
                        "fontWeight": "600", "marginBottom": "20px",
                        "animation": "fadeInUp 0.6s ease forwards",
                    }),
                    html.H1([
                        "Tableau de bord ",
                        html.Br(),
                        html.Span("Multi-Secteur", style={
                            "background": "linear-gradient(135deg, #F0B429 0%, #3FB950 50%, #58A6FF 100%)",
                            "WebkitBackgroundClip": "text",
                            "WebkitTextFillColor": "transparent",
                            "backgroundClip": "text",
                        }),
                    ], style={
                        "fontFamily": SERIF, "fontWeight": "300",
                        "fontSize": "52px", "margin": "0 0 20px",
                        "lineHeight": "1.1", "color": T["text"],
                        "animation": "fadeInUp 0.6s 0.1s ease both",
                    }),
                    html.P(
                        "Analyse intégrée des secteurs bancaire, énergétique et assurantiel "
                        "du Sénégal. Données officielles BCEAO",
                        style={
                            "color": T["muted"], "fontFamily": SANS,
                            "fontSize": "15px", "maxWidth": "480px",
                            "lineHeight": "1.8", "margin": "0",
                            "animation": "fadeInUp 0.6s 0.2s ease both",
                        }
                    ),
                ], style={"flex": "1"}),

                # Compteurs animés
                html.Div([
                    _animated_counter("168", "enregistrements", "#F0B429", 0),
                    _animated_counter("35k+", "mesures solaires", "#3FB950", 100),
                    _animated_counter("1000", "contrats assurance", "#58A6FF", 200),
                    _animated_counter("49", "KPIs / banque", "#A78BFA", 300),
                ], style={
                    "display": "grid", "gridTemplateColumns": "1fr 1fr",
                    "gap": "16px", "animation": "fadeInUp 0.6s 0.3s ease both",
                }),

            ], style={
                "display": "flex", "alignItems": "center",
                "justifyContent": "space-between",
                "padding": "60px 64px 52px",
                "borderBottom": f"1px solid {T['border']}",
                "flexWrap": "wrap", "gap": "40px",
                "position": "relative",
            }),

            # ── Cartes secteurs ───────────────────────────────
            html.Div([
                html.Div([
                    html.Div("▸ CHOISISSEZ UN SECTEUR", style={
                        "color": T["muted"], "fontSize": "9px",
                        "fontFamily": MONO, "letterSpacing": "3px",
                        "fontWeight": "600", "marginBottom": "32px",
                        "animation": "fadeInUp 0.6s 0.4s ease both",
                    }),
                    html.Div([
                        _sector_card("bancaire", T, delay=500),
                        _sector_card("energie", T, delay=600),
                        _sector_card("assurance", T, delay=700),
                    ], style={"display": "flex", "gap": "20px", "flexWrap": "wrap"}),
                ]),
            ], style={"padding": "48px 64px"}),

            # ── Footer ────────────────────────────────────────
            html.Div([
                html.Span("Données officielles · ", style={
                    "color": T["muted"], "fontFamily": MONO, "fontSize": "9px"}),
                html.Span("BCEAO", style={
                    "color": T["muted"], "fontFamily": MONO,
                    "fontSize": "9px", "opacity": "0.5"}),
            ], style={
                "padding": "20px 64px",
                "borderTop": f"1px solid {T['border']}",
            }),

        ], style={
            "position": "relative", "zIndex": "1",
            "minHeight": "100vh", "background": "transparent",
            "display": "flex", "flexDirection": "column",
        }),

        # ── Script particules + compteurs ─────────────────────
        html.Script("""
(function() {
    // ── Particules ──────────────────────────────────────────
    function initParticles() {
        var canvas = document.getElementById('particles-canvas');
        if (!canvas) { setTimeout(initParticles, 100); return; }
        var ctx = canvas.getContext('2d');
        var W = window.innerWidth, H = window.innerHeight;
        canvas.width = W; canvas.height = H;

        var colors = ['#F0B429', '#3FB950', '#58A6FF', '#A78BFA'];
        var particles = [];
        for (var i = 0; i < 55; i++) {
            particles.push({
                x: Math.random() * W,
                y: Math.random() * H,
                r: Math.random() * 1.5 + 0.3,
                dx: (Math.random() - 0.5) * 0.35,
                dy: (Math.random() - 0.5) * 0.35,
                color: colors[Math.floor(Math.random() * colors.length)],
                alpha: Math.random() * 0.5 + 0.1,
            });
        }

        function draw() {
            ctx.clearRect(0, 0, W, H);
            // Lignes de connexion
            for (var i = 0; i < particles.length; i++) {
                for (var j = i+1; j < particles.length; j++) {
                    var dx = particles[i].x - particles[j].x;
                    var dy = particles[i].y - particles[j].y;
                    var dist = Math.sqrt(dx*dx + dy*dy);
                    if (dist < 120) {
                        ctx.beginPath();
                        ctx.moveTo(particles[i].x, particles[i].y);
                        ctx.lineTo(particles[j].x, particles[j].y);
                        ctx.strokeStyle = 'rgba(48,54,61,' + (1 - dist/120) * 0.8 + ')';
                        ctx.lineWidth = 0.5;
                        ctx.stroke();
                    }
                }
            }
            // Points
            particles.forEach(function(p) {
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
                ctx.fillStyle = p.color.replace(')', ',' + p.alpha + ')').replace('rgb', 'rgba').replace('#', '');
                // Utilisation directe de la couleur hex avec alpha
                ctx.globalAlpha = p.alpha;
                ctx.fillStyle = p.color;
                ctx.fill();
                ctx.globalAlpha = 1;
                // Mouvement
                p.x += p.dx; p.y += p.dy;
                if (p.x < 0 || p.x > W) p.dx *= -1;
                if (p.y < 0 || p.y > H) p.dy *= -1;
            });
            requestAnimationFrame(draw);
        }
        draw();

        window.addEventListener('resize', function() {
            W = canvas.width  = window.innerWidth;
            H = canvas.height = window.innerHeight;
        });
    }
    initParticles();

    // ── Compteurs animés ────────────────────────────────────
    function animateCounters() {
        var counters = document.querySelectorAll('.animated-counter');
        counters.forEach(function(el) {
            var target = el.getAttribute('data-target');
            var isK = target.indexOf('k') > -1;
            var isPlus = target.indexOf('+') > -1;
            var num = parseInt(target.replace(/[^0-9]/g, ''));
            var duration = 1800;
            var start = performance.now();
            function update(now) {
                var elapsed = now - start;
                var progress = Math.min(elapsed / duration, 1);
                var eased = 1 - Math.pow(1 - progress, 3);
                var current = Math.floor(eased * num);
                el.textContent = current + (isK ? 'k' : '') + (isPlus ? '+' : '');
                if (progress < 1) requestAnimationFrame(update);
                else el.textContent = target;
            }
            setTimeout(function() { requestAnimationFrame(update); },
                parseInt(el.getAttribute('data-delay') || 0));
        });
    }

    // Observer pour déclencher les compteurs quand visibles
    if ('IntersectionObserver' in window) {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(e) {
                if (e.isIntersecting) { animateCounters(); observer.disconnect(); }
            });
        });
        function observeCounters() {
            var el = document.querySelector('.animated-counter');
            if (el) observer.observe(el);
            else setTimeout(observeCounters, 200);
        }
        observeCounters();
    } else {
        setTimeout(animateCounters, 500);
    }
})();
        """),

    ], style={
        "background": "#0D1117",
        "minHeight": "100vh",
        "color": "#E6EDF3",
    })


def _animated_counter(value, label, accent, delay):
    return html.Div([
        html.Div(
            value,
            className="animated-counter",
            **{"data-target": value, "data-delay": str(delay)},
            style={
                "color": accent, "fontSize": "32px",
                "fontWeight": "700", "fontFamily": MONO,
                "lineHeight": "1", "marginBottom": "6px",
            }
        ),
        html.Div(label, style={
            "color": "#8B949E", "fontSize": "9px",
            "fontFamily": MONO, "letterSpacing": "1.5px",
        }),
    ], style={
        "background": "#161B22",
        "border": "1px solid #30363D",
        "borderRadius": "8px",
        "padding": "20px",
        "borderLeft": f"3px solid {accent}",
    })


def _sector_card(sector_key, T, delay=0):
    meta   = SECTOR_META[sector_key]
    accent = meta["accent"]
    h      = accent.lstrip("#")
    r, g, b = int(h[0:2],16), int(h[2:4],16), int(h[4:6],16)

    return dcc.Link(
        html.Div([
            # Icône
            html.Div(meta["icon"], style={
                "fontSize": "36px", "lineHeight": "1",
                "marginBottom": "16px",
            }),
            html.Div(
                "● EN LIGNE" if meta["pages"] > 0 else "● BIENTÔT",
                style={
                    "fontSize": "8px", "fontFamily": MONO,
                    "letterSpacing": "1.5px", "fontWeight": "600",
                    "color": accent if meta["pages"] > 0 else T["muted"],
                    "marginBottom": "12px",
                }
            ),
            html.H2(meta["label"], style={
                "color": T["text"], "fontFamily": SERIF,
                "fontWeight": "300", "fontSize": "22px",
                "margin": "0 0 6px", "letterSpacing": "0.3px",
            }),
            html.P(meta["sublabel"], style={
                "color": T["muted"], "fontFamily": MONO,
                "fontSize": "10px", "margin": "0 0 20px",
                "letterSpacing": "0.5px",
            }),
            html.Div(style={
                "height": "1px",
                "background": f"linear-gradient(90deg, {accent}, transparent)",
                "marginBottom": "20px",
            }),
            html.Div([
                html.Div([
                    html.Div(str(meta["pages"]) if meta["pages"] > 0 else "—",
                        style={"color": accent, "fontSize": "28px",
                               "fontWeight": "700", "fontFamily": MONO,
                               "lineHeight": "1"}),
                    html.Div("pages", style={"color": T["muted"],
                        "fontSize": "9px", "fontFamily": MONO,
                        "letterSpacing": "1px", "marginTop": "4px"}),
                ]),
                html.Div(style={"width": "1px", "background": T["border"],
                                "margin": "0 20px", "alignSelf": "stretch"}),
                html.Div([
                    html.Div(
                        "BCEAO" if sector_key == "bancaire" else
                        "SENELEC" if sector_key == "energie" else "CIMA",
                        style={"color": accent, "fontSize": "14px",
                               "fontWeight": "700", "fontFamily": MONO}),
                    html.Div("source", style={"color": T["muted"],
                        "fontSize": "9px", "fontFamily": MONO,
                        "letterSpacing": "1px", "marginTop": "4px"}),
                ]),
            ], style={"display": "flex", "alignItems": "center",
                      "marginBottom": "20px"}),
            html.Div(
                "Accéder →" if meta["pages"] > 0 else "Données en attente",
                style={
                    "background": f"rgba({r},{g},{b},0.12)" if meta["pages"] > 0
                                  else "transparent",
                    "border": f"1px solid {accent if meta['pages'] > 0 else T['border']}",
                    "color": accent if meta["pages"] > 0 else T["muted"],
                    "padding": "10px 20px", "borderRadius": "6px",
                    "fontFamily": MONO, "fontSize": "11px",
                    "fontWeight": "600", "textAlign": "center",
                    "letterSpacing": "1px",
                }
            ),
        ], style={
            "background": T["card"],
            "border": f"1px solid {T['border']}",
            "borderRadius": "12px",
            "padding": "32px 28px",
            "cursor": "pointer" if meta["pages"] > 0 else "default",
            "transition": "transform 0.2s ease, box-shadow 0.2s ease",
            "position": "relative",
            "overflow": "hidden",
            "borderTop": f"3px solid {accent}",
            "animation": f"fadeInUp 0.6s {delay}ms ease both",
        }, className="sector-card"),
        href=f"/{sector_key}" if meta["pages"] > 0 else "#",
        style={"textDecoration": "none", "flex": "1"},
    )
