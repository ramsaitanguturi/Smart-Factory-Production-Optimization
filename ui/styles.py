"""
Industrial SCADA & Control Center CSS Styling
Provides dark-mode industrial design with glassmorphic panels, neon accents,
and animated machine status indicators.
"""

INDUSTRIAL_CSS = """
<style>
/* Import Modern Industrial & Monospace Fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Control Room Dark Theme Override */
.stApp {
    background: radial-gradient(circle at 10% 10%, #0d131f 0%, #080c14 100%);
    color: #e2e8f0;
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
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.kpi-card:hover {
    transform: translateY(-2px);
    border-color: rgba(56, 189, 248, 0.5);
}

.kpi-label {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #94a3b8;
    margin-bottom: 0.4rem;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 700;
    color: #f8fafc;
    font-family: 'JetBrains Mono', monospace;
}

.kpi-sub {
    font-size: 0.75rem;
    color: #64748b;
    margin-top: 0.2rem;
}

/* Machine Floor Twin Card */
.machine-card {
    background: rgba(15, 23, 42, 0.9);
    border-radius: 12px;
    border: 1px solid #334155;
    padding: 1.25rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
    transition: all 0.25s ease;
}

.machine-card.status-normal {
    border-left: 5px solid #10b981;
}

.machine-card.status-warning {
    border-left: 5px solid #f59e0b;
    background: rgba(30, 27, 18, 0.85);
}

.machine-card.status-critical {
    border-left: 5px solid #ef4444;
    background: rgba(38, 18, 22, 0.9);
    animation: pulse-border 2s infinite;
}

.machine-card.status-failed {
    border-left: 5px solid #dc2626;
    background: rgba(45, 10, 15, 0.95);
}

@keyframes pulse-border {
    0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
    100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
}

/* Status Badges */
.badge-status {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 0.25rem 0.65rem;
    border-radius: 9999px;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.05em;
    font-family: 'JetBrains Mono', monospace;
}

.badge-normal {
    background: rgba(16, 185, 129, 0.15);
    color: #34d399;
    border: 1px solid rgba(16, 185, 129, 0.3);
}

.badge-warning {
    background: rgba(245, 158, 11, 0.15);
    color: #fbbf24;
    border: 1px solid rgba(245, 158, 11, 0.3);
}

.badge-critical {
    background: rgba(239, 68, 68, 0.2);
    color: #f87171;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

.badge-maintenance {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
}

/* Live Pulse Dot */
.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    display: inline-block;
}
.pulse-dot.dot-normal { background: #10b981; box-shadow: 0 0 8px #10b981; }
.pulse-dot.dot-warning { background: #f59e0b; box-shadow: 0 0 8px #f59e0b; }
.pulse-dot.dot-critical { background: #ef4444; box-shadow: 0 0 8px #ef4444; }

/* Section Header Bar */
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

/* Comparison Metric Box (Before vs After) */
.comparison-box {
    background: rgba(15, 23, 42, 0.8);
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 1rem;
    text-align: center;
}

.improvement-badge {
    color: #34d399;
    font-weight: 700;
    font-size: 0.95rem;
    background: rgba(16, 185, 129, 0.15);
    padding: 0.2rem 0.6rem;
    border-radius: 6px;
    display: inline-block;
    margin-top: 0.4rem;
}
</style>
"""


def apply_custom_styles():
    """Returns the CSS string wrapped in st.markdown for Streamlit injection."""
    return INDUSTRIAL_CSS
