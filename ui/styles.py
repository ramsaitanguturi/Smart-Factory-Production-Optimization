"""
Industrial SCADA & Control Center CSS Styling
Provides dual-theme support:
- Dark Mode: sleek industrial SCADA command center with glassmorphic panels and neon indicators.
- Light Mode: modern high-contrast industrial engineering laboratory with crisp elevation and clean typography.
"""
from typing import Dict, Any


def get_theme_palette(theme: str = "dark") -> Dict[str, str]:
    """Returns standardized theme palette tokens for Plotly visualizations and dynamic UI styling."""
    is_light = (str(theme).lower() == "light")
    if is_light:
        return {
            "name": "light",
            "paper_bg": "#ffffff",
            "plot_bg": "#f8fafc",
            "text_primary": "#0f172a",
            "text_secondary": "#334155",
            "text_muted": "#64748b",
            "border_color": "#cbd5e1",
            "grid_color": "#e2e8f0",
            "accent_blue": "#0284c7",
            "accent_cyan": "#0891b2",
            "accent_green": "#059669",
            "accent_amber": "#d97706",
            "accent_red": "#dc2626",
            "gauge_bg": "#f1f5f9",
            "gauge_border": "#cbd5e1",
            "tick_color": "#64748b",
            "line_secondary": "#64748b",
            "card_bg": "#ffffff",
            "card_border": "#cbd5e1",
            "header_clock_bg": "#f1f5f9",
            "header_clock_border": "#cbd5e1",
            "header_clock_val": "#0284c7",
            "status_box_bg": "#ffffff",
            "status_box_border": "#cbd5e1",
            "sub_box_bg": "#f1f5f9",
            "sub_box_border": "#0284c7",
            "title_color": "#0f172a",
            "track_bg": "#e2e8f0",
        }
    else:
        return {
            "name": "dark",
            "paper_bg": "rgba(15, 23, 42, 0.6)",
            "plot_bg": "rgba(15, 23, 42, 0.8)",
            "text_primary": "#f8fafc",
            "text_secondary": "#cbd5e1",
            "text_muted": "#94a3b8",
            "border_color": "#334155",
            "grid_color": "#1e293b",
            "accent_blue": "#38bdf8",
            "accent_cyan": "#06b6d4",
            "accent_green": "#10b981",
            "accent_amber": "#f59e0b",
            "accent_red": "#ef4444",
            "gauge_bg": "rgba(15, 23, 42, 0.8)",
            "gauge_border": "#334155",
            "tick_color": "#64748b",
            "line_secondary": "#94a3b8",
            "card_bg": "rgba(17, 24, 39, 0.85)",
            "card_border": "rgba(51, 65, 85, 0.6)",
            "header_clock_bg": "rgba(15, 23, 42, 0.8)",
            "header_clock_border": "#334155",
            "header_clock_val": "#38bdf8",
            "status_box_bg": "rgba(15, 23, 42, 0.85)",
            "status_box_border": "#334155",
            "sub_box_bg": "rgba(30, 41, 59, 0.5)",
            "sub_box_border": "#38bdf8",
            "title_color": "#f1f5f9",
            "track_bg": "#1e293b",
        }


SHARED_CSS = """
/* Import Modern Industrial & Monospace Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Pulse Animations */
@keyframes pulse-border-dark {
    0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.5); }
    70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
    100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

@keyframes pulse-border-light {
    0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(220, 38, 38, 0); }
    100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
}

@keyframes pulse-dot {
    0% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.7); }
    50% { transform: scale(1.25); opacity: 1; box-shadow: 0 0 0 7px rgba(239, 68, 68, 0); }
    100% { transform: scale(0.9); opacity: 0.8; box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* Status Badges */
.badge-status {
    display: inline-flex;
    align-items: center;
    gap: 7px;
    padding: 0.32rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.12);
    transition: all 0.2s ease;
}

/* Live Pulse Dot Base */
.pulse-dot {
    width: 9px;
    height: 9px;
    border-radius: 50%;
    display: inline-block;
    flex-shrink: 0;
}

/* Status Legend Bar */
.status-legend-bar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 12px;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    margin-bottom: 1.2rem;
    font-size: 0.8rem;
}

.status-legend-item {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-weight: 500;
}

/* KPI Card Base */
.kpi-card {
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
}

.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 0.4rem;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}

.kpi-sub {
    font-size: 0.75rem;
    margin-top: 0.2rem;
}

/* Machine Card Base */
.machine-card {
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

/* Sub-stat Grid Box */
.sub-stat-box {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    font-size: 0.78rem;
    margin-top: 10px;
    padding: 8px;
    border-radius: 6px;
}

/* Comparison Metric Box */
.comparison-box {
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
    transition: transform 0.2s ease;
}

.comparison-box:hover {
    transform: translateY(-2px);
}

.improvement-badge {
    font-weight: 700;
    font-size: 0.95rem;
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
    margin-top: 0.4rem;
}

.stButton > button,
div[data-testid="stFormSubmitButton"] > button {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s ease;
    min-height: 42px;
}
"""

DARK_THEME_CSS = """
/* Control Room Dark Theme */
.stApp {
    background: radial-gradient(circle at 10% 10%, #0d131f 0%, #080c14 100%);
    color: #e2e8f0;
}

[data-testid="stSidebar"] {
    background-color: #0b0f19 !important;
    border-right: 1px solid #1e293b;
}

/* Header & Title Styling */
.scada-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 1.8rem;
    background: linear-gradient(90deg, rgba(15, 23, 42, 0.95) 0%, rgba(30, 41, 59, 0.9) 100%);
    border: 1px solid rgba(56, 189, 248, 0.25);
    border-radius: 12px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.45);
    margin-bottom: 1.5rem;
}

.scada-title {
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #38bdf8 0%, #818cf8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.scada-subtitle {
    font-size: 0.85rem;
    color: #94a3b8;
    margin-top: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}

/* KPI Card Styling */
.kpi-card {
    background: rgba(17, 24, 39, 0.85);
    border: 1px solid rgba(51, 65, 85, 0.6);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.kpi-card:hover {
    border-color: rgba(56, 189, 248, 0.5);
    box-shadow: 0 6px 20px rgba(56, 189, 248, 0.15);
}

.kpi-label { color: #94a3b8; }
.kpi-value { color: #f8fafc; }
.kpi-sub { color: #64748b; }

/* Machine Card Styling */
.machine-card {
    background: rgba(15, 23, 42, 0.9);
    border: 1px solid #334155;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.machine-card.status-normal { border-left: 5px solid #10b981; }
.machine-card.status-warning {
    border-left: 5px solid #f59e0b;
    background: rgba(30, 27, 18, 0.85);
}
.machine-card.status-critical {
    border-left: 5px solid #ef4444;
    background: rgba(38, 18, 22, 0.9);
    animation: pulse-border-dark 2s infinite;
}
.machine-card.status-failed {
    border-left: 5px solid #7f1d1d;
    background: rgba(45, 10, 15, 0.95);
}
.machine-card.status-maintenance {
    border-left: 5px solid #3b82f6;
    background: rgba(15, 28, 48, 0.9);
}

.sub-stat-box {
    background: rgba(15, 23, 42, 0.6);
    border: 1px solid #1e293b;
    color: #cbd5e1;
}

/* Badges Dark */
.badge-status.badge-normal, .badge-normal {
    background: rgba(16, 185, 129, 0.2) !important;
    color: #34d399 !important;
    border: 1.5px solid rgba(16, 185, 129, 0.45) !important;
}
.badge-status.badge-warning, .badge-warning {
    background: rgba(245, 158, 11, 0.2) !important;
    color: #fbbf24 !important;
    border: 1.5px solid rgba(245, 158, 11, 0.45) !important;
}
.badge-status.badge-critical, .badge-critical {
    background: rgba(239, 68, 68, 0.25) !important;
    color: #f87171 !important;
    border: 1.5px solid rgba(239, 68, 68, 0.55) !important;
}
.badge-status.badge-failed, .badge-failed {
    background: rgba(127, 29, 29, 0.4) !important;
    color: #fca5a5 !important;
    border: 1.5px solid rgba(220, 38, 38, 0.6) !important;
}
.badge-status.badge-maintenance, .badge-maintenance {
    background: rgba(59, 130, 246, 0.2) !important;
    color: #60a5fa !important;
    border: 1.5px solid rgba(59, 130, 246, 0.45) !important;
}

/* Live Pulse Dots Dark */
.pulse-dot.dot-normal { background: #10b981; box-shadow: 0 0 8px #10b981; }
.pulse-dot.dot-warning { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
.pulse-dot.dot-critical {
    background: #ef4444;
    box-shadow: 0 0 10px #ef4444;
    animation: pulse-dot 1.5s infinite ease-in-out;
}
.pulse-dot.dot-failed { background: #7f1d1d; box-shadow: 0 0 8px #b91c1c; }
.pulse-dot.dot-maintenance { background: #3b82f6; box-shadow: 0 0 8px #3b82f6; }

/* Status Legend Dark */
.status-legend-bar {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid #1e293b;
    color: #cbd5e1;
}

/* Section Banner Dark */
.section-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.7rem 1rem;
    background: rgba(30, 41, 59, 0.6);
    border-left: 4px solid #38bdf8;
    border-radius: 6px;
    margin: 1.2rem 0 0.8rem 0;
    font-weight: 600;
    font-size: 1.05rem;
    color: #f1f5f9;
}

/* Comparison Metric Box Dark */
.comparison-box {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid #334155;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
}

.improvement-badge {
    color: #34d399;
    background: rgba(16, 185, 129, 0.15);
}

/* Streamlit Widgets Dark */
div[data-testid="stRadio"] label div p,
div[data-testid="stRadio"] label p,
div[data-testid="stRadio"] label span {
    color: #cbd5e1 !important;
    font-weight: 500;
}

[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span {
    color: #cbd5e1 !important;
}

div[data-baseweb="select"] > div {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
}

div[data-baseweb="select"] * {
    color: #f8fafc !important;
}

div[data-baseweb="input"] {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
}

div[data-baseweb="input"] input {
    background-color: #111827 !important;
    color: #f8fafc !important;
}

/* Buttons in Dark Mode */
.stButton > button:not([kind="primary"]),
div[data-testid="stFormSubmitButton"] > button:not([kind="primary"]) {
    background-color: #111827 !important;
    border: 1px solid #334155 !important;
    color: #e2e8f0 !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.stButton > button:not([kind="primary"]):hover,
div[data-testid="stFormSubmitButton"] > button:not([kind="primary"]):hover {
    background-color: #1e293b !important;
    border-color: #38bdf8 !important;
    color: #38bdf8 !important;
}

.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
    color: #ffffff !important;
    border: 1px solid rgba(56, 189, 248, 0.4) !important;
    box-shadow: 0 4px 14px rgba(2, 132, 199, 0.35) !important;
}

.stButton > button[kind="primary"] *,
div[data-testid="stFormSubmitButton"] > button[kind="primary"] * {
    color: #ffffff !important;
}

.stButton > button[kind="primary"]:hover,
div[data-testid="stFormSubmitButton"] > button[kind="primary"]:hover {
    background: linear-gradient(135deg, #0369a1 0%, #1d4ed8 100%) !important;
    box-shadow: 0 6px 20px rgba(56, 189, 248, 0.4) !important;
}
"""

LIGHT_THEME_CSS = """
/* Modern Clean Industrial Light Theme */
:root, .stApp, [data-testid="stSidebar"], [data-testid="stSidebarUserContent"], [data-testid="stAppViewContainer"] {
    --text-color: #0f172a !important;
    --background-color: #f8fafc !important;
    --secondary-background-color: #ffffff !important;
    --primary-color: #0284c7 !important;
    color: #0f172a !important;
}

.stApp {
    background: linear-gradient(180deg, #f8fafc 0%, #edf2f7 100%) !important;
    color: #0f172a !important;
}

/* Global text color resets for light mode */
.stApp p, .stApp span, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6,
div[data-testid="stMarkdownContainer"] p,
div[data-testid="stMarkdownContainer"] span {
    color: #0f172a !important;
}

/* Sidebar styling in Light Mode */
[data-testid="stSidebar"], section[data-testid="stSidebar"] {
    background-color: #ffffff !important;
    border-right: 1px solid #e2e8f0 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p,
[data-testid="stSidebar"] div[role="radiogroup"] label *,
[data-testid="stSidebar"] div[data-testid="stRadio"] label * {
    color: #0f172a !important;
    font-weight: 500;
}

/* Form & widget labels */
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] *,
[data-testid="stSlider"] label,
[data-testid="stSlider"] label *,
[data-testid="stSelectbox"] label,
[data-testid="stSelectbox"] label * {
    color: #1e293b !important;
    font-weight: 600 !important;
}

/* Selectbox / Dropdowns with high specificity */
div[data-baseweb="select"] {
    background-color: #ffffff !important;
}

div[data-baseweb="select"] > div {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
}

div[data-baseweb="select"] * {
    color: #0f172a !important;
}

html body [data-testid="stAppViewContainer"] [data-baseweb="select"],
html body [data-testid="stAppViewContainer"] [data-baseweb="select"] div,
html body [data-testid="stAppViewContainer"] [data-baseweb="select"] span,
html body [data-testid="stAppViewContainer"] [data-baseweb="select"] p,
html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] > div > div,
html body [data-testid="stAppViewContainer"] div[data-testid="stSelectbox"] div[role="combobox"] {
    color: #0f172a !important;
    border-color: #cbd5e1 !important;
}

html body [data-testid="stAppViewContainer"] [data-baseweb="select"] svg {
    fill: #0f172a !important;
    color: #0f172a !important;
}

div[data-baseweb="popover"],
div[data-baseweb="menu"],
div[data-baseweb="menu"] * {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

/* Inputs & Numbers */
div[data-baseweb="input"] {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
}

div[data-baseweb="input"] input {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

/* Checkbox text */
div[data-testid="stCheckbox"] label span p {
    color: #1e293b !important;
    font-weight: 500;
}

/* Sliders */
div[data-testid="stSlider"] div {
    color: #334155 !important;
}

/* Alerts / Info Boxes */
div[data-testid="stAlert"] {
    background-color: #f1f5f9 !important;
    border: 1px solid #cbd5e1 !important;
    color: #1e293b !important;
}

div[data-testid="stAlert"] p,
div[data-testid="stAlert"] span {
    color: #1e293b !important;
}

/* Buttons in Light Mode */
.stButton > button:not([kind="primary"]),
div[data-testid="stFormSubmitButton"] > button:not([kind="primary"]) {
    background-color: #ffffff !important;
    border: 1px solid #cbd5e1 !important;
    color: #1e293b !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.03);
}

.stButton > button:not([kind="primary"]):hover,
div[data-testid="stFormSubmitButton"] > button:not([kind="primary"]):hover {
    background-color: #f8fafc !important;
    border-color: #0284c7 !important;
    color: #0284c7 !important;
}

.stButton > button[kind="primary"],
div[data-testid="stFormSubmitButton"] > button[kind="primary"] {
    background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
    color: #ffffff !important;
    border: none !important;
    box-shadow: 0 4px 12px rgba(2, 132, 199, 0.25) !important;
}

.stButton > button[kind="primary"] *,
div[data-testid="stFormSubmitButton"] > button[kind="primary"] * {
    color: #ffffff !important;
}

/* Header & Title Styling */
.scada-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1.2rem 1.8rem;
    background: linear-gradient(90deg, #ffffff 0%, #f8fafc 100%);
    border: 1px solid #cbd5e1;
    border-radius: 12px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
    margin-bottom: 1.5rem;
}

.scada-title {
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #0284c7 0%, #4338ca 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
}

.scada-subtitle {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 0.25rem;
    font-family: 'JetBrains Mono', monospace;
}

/* KPI Card Styling */
.kpi-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
}

.kpi-card:hover {
    border-color: rgba(2, 132, 199, 0.5);
    box-shadow: 0 6px 20px rgba(2, 132, 199, 0.12);
}

.kpi-label { color: #64748b; }
.kpi-value { color: #0f172a; }
.kpi-sub { color: #94a3b8; }

/* Machine Card Styling */
.machine-card {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
}

.machine-card.status-normal { border-left: 5px solid #059669; }
.machine-card.status-warning {
    border-left: 5px solid #d97706;
    background: #fffbeb;
}
.machine-card.status-critical {
    border-left: 5px solid #dc2626;
    background: #fef2f2;
    animation: pulse-border-light 2s infinite;
}
.machine-card.status-failed {
    border-left: 5px solid #7f1d1d;
    background: #fee2e2;
}
.machine-card.status-maintenance {
    border-left: 5px solid #0284c7;
    background: #f0f9ff;
}

.sub-stat-box {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    color: #334155;
}

/* Badges Light - High specificity with !important */
.badge-status.badge-normal, .badge-normal {
    background: rgba(16, 185, 129, 0.16) !important;
    color: #047857 !important;
    border: 1.5px solid rgba(16, 185, 129, 0.45) !important;
}
.badge-status.badge-warning, .badge-warning {
    background: rgba(245, 158, 11, 0.16) !important;
    color: #b45309 !important;
    border: 1.5px solid rgba(245, 158, 11, 0.45) !important;
}
.badge-status.badge-critical, .badge-critical {
    background: rgba(239, 68, 68, 0.16) !important;
    color: #dc2626 !important;
    border: 1.5px solid rgba(239, 68, 68, 0.45) !important;
}
.badge-status.badge-failed, .badge-failed {
    background: rgba(127, 29, 29, 0.18) !important;
    color: #7f1d1d !important;
    border: 1.5px solid rgba(185, 28, 28, 0.5) !important;
}
.badge-status.badge-maintenance, .badge-maintenance {
    background: rgba(2, 132, 199, 0.16) !important;
    color: #0369a1 !important;
    border: 1.5px solid rgba(2, 132, 199, 0.45) !important;
}

/* Live Pulse Dots Light */
.pulse-dot.dot-normal { background: #059669; box-shadow: 0 0 8px rgba(5, 150, 105, 0.6); }
.pulse-dot.dot-warning { background: #d97706; box-shadow: 0 0 8px rgba(217, 119, 6, 0.6); }
.pulse-dot.dot-critical {
    background: #dc2626;
    box-shadow: 0 0 10px rgba(220, 38, 38, 0.7);
    animation: pulse-dot 1.5s infinite ease-in-out;
}
.pulse-dot.dot-failed { background: #7f1d1d; box-shadow: 0 0 8px rgba(127, 29, 29, 0.6); }
.pulse-dot.dot-maintenance { background: #0284c7; box-shadow: 0 0 8px rgba(2, 132, 199, 0.6); }

/* Status Legend Light */
.status-legend-bar {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    color: #334155;
}

/* Section Banner Light */
.section-banner {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0.7rem 1rem;
    background: #e2e8f0;
    border-left: 4px solid #0284c7;
    border-radius: 6px;
    margin: 1.2rem 0 0.8rem 0;
    font-weight: 600;
    font-size: 1.05rem;
    color: #0f172a;
}

/* Comparison Metric Box Light */
.comparison-box {
    background: #ffffff;
    border: 1px solid #cbd5e1;
    box-shadow: 0 4px 14px rgba(0, 0, 0, 0.04);
}

.improvement-badge {
    color: #047857;
    background: rgba(16, 185, 129, 0.15);
}

/* Metrics Value in Light Mode */
[data-testid="stMetricValue"] div {
    color: #0f172a !important;
}

[data-testid="stMetricLabel"] p {
    color: #64748b !important;
}

.stTabs [data-baseweb="tab-list"] {
    background-color: #f1f5f9;
    border-radius: 8px;
    padding: 4px;
}

.stTabs [data-baseweb="tab"] {
    color: #475569;
}

.stTabs [aria-selected="true"] {
    color: #0284c7 !important;
    font-weight: 700;
}
"""


def apply_custom_styles(theme: str = "dark") -> str:
    """
    Returns the complete CSS stylesheet string wrapped in <style> tags
    for injection into Streamlit via st.markdown.
    Supports both 'dark' and 'light' theme selections.
    """
    selected_theme = str(theme).lower().strip()
    theme_rules = LIGHT_THEME_CSS if selected_theme == "light" else DARK_THEME_CSS
    return f"<style>\n{SHARED_CSS}\n{theme_rules}\n</style>"
