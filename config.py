# config.py
import streamlit as st

PAGE_CONFIG = {
    "page_title": "Quantum Logistics Pro",
    "page_icon": "⚛️",
    "layout": "wide",
    "initial_sidebar_state": "expanded"
}

# AuthKit — Frosted Glass Midnight Theme
CUSTOM_CSS = """
<style>
    /* ── Fonts ─────────────────────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Space+Grotesk:wght@500&family=JetBrains+Mono:wght@400&display=swap');

    /* ── Design Tokens ──────────────────────────────────────────── */
    :root {
        --color-midnight-canvas: #05060f;
        --color-steel-plate:     #2f343e;
        --color-fog-veil:        #9da7ba;
        --color-moon-mist:       #c7d3ea;
        --color-frost-glow:      #d1e4fa;
        --color-ice-highlight:   #d8ecf8;
        --color-pure-white:      #ffffff;
        --color-void-violet:     #663af3;
        --color-blueprint-blue:  #b6d9fc;
        --color-glass-edge:      rgba(186,215,247,0.12);
        --color-luminous-fill:   rgba(199,211,234,0.12);
        --gradient-headline:     linear-gradient(0deg, #d8ecf8 0%, #98c0ef 100%);

        --radius-pill:   999px;
        --radius-card:   16px;
        --radius-badge:  6px;
        --radius-icon:   9999px;

        --elevation-glass:
            inset 0 1px 1px rgba(216,236,248,0.20),
            inset 0 24px 48px rgba(199,211,234,0.05),
            0 24px 32px rgba(6,6,14,0.70);
    }

    /* ── Global Background ──────────────────────────────────────── */
    .stApp {
        background-color: var(--color-midnight-canvas);
        background-image:
            /* conic spotlight halo */
            conic-gradient(at 50% -5%,
                transparent 45%,
                rgba(124,145,182,0.30) 49%,
                rgba(124,145,182,0.50) 50%,
                rgba(124,145,182,0.30) 51%,
                transparent 55%),
            /* background grid */
            linear-gradient(rgba(186,215,247,0.06) 1px, transparent 1px),
            linear-gradient(90deg, rgba(186,215,247,0.06) 1px, transparent 1px);
        background-size: 100% 100%, 90px 90px, 90px 90px;
        background-attachment: fixed;
        color: var(--color-frost-glow);
        font-family: 'Inter', sans-serif;
    }

    /* ── Headings ────────────────────────────────────────────────── */
    h1, h2, h3 {
        font-family: 'Space Grotesk', sans-serif !important;
        font-weight: 500 !important;
        background: var(--gradient-headline);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.01em;
    }
    h1 { font-size: 44px !important; }
    h2 { font-size: 28px !important; }
    h3 { font-size: 24px !important; }

    /* ── Body / Text Hierarchy ───────────────────────────────────── */
    /* Note: deliberately exclude `span` and `div` here — Streamlit uses
       Material Icons inside spans; overriding their font breaks the glyphs
       and causes _arrow_right_ / _arrow_down_ literal text. */
    p, li, label {
        font-family: 'Inter', sans-serif;
    }
    .stMarkdown p      { color: var(--color-frost-glow);   }
    .stCaption,
    [data-testid="stCaptionContainer"] {
        color: var(--color-fog-veil) !important;
        font-size: 12px !important;
    }

    /* ── Sidebar ─────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background-color: rgba(5,6,15,0.97) !important;
        border-right: 1px inset var(--color-glass-edge) !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-size: 20px !important;
    }

    /* ── Glass Card — Metric + Expander ──────────────────────────── */
    div[data-testid="stMetric"],
    div[data-testid="stExpander"] {
        background: rgba(186,214,247,0.03) !important;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border-radius: var(--radius-card) !important;
        border: 1px inset var(--color-glass-edge) !important;
        padding: 24px !important;
        box-shadow: var(--elevation-glass) !important;
        transition: box-shadow 0.25s ease;
    }
    div[data-testid="stMetric"]:hover {
        box-shadow:
            inset 0 1px 1px rgba(216,236,248,0.28),
            inset 0 24px 48px rgba(199,211,234,0.08),
            0 24px 40px rgba(6,6,14,0.80) !important;
    }

    /* Metric value & label */
    div[data-testid="stMetricValue"] > div {
        color: var(--color-frost-glow) !important;
        font-family: 'Space Grotesk', sans-serif !important;
        font-size: 28px !important;
        font-weight: 500 !important;
        text-shadow: none !important;
    }
    div[data-testid="stMetricLabel"] > div {
        color: var(--color-moon-mist) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 13px !important;
        font-weight: 500 !important;
    }

    /* ── Primary CTA Button — Void Violet ───────────────────────── */
    div.stButton > button[kind="primary"] {
        background: var(--color-void-violet) !important;
        color: var(--color-pure-white) !important;
        border: none !important;
        border-radius: var(--radius-badge) !important;  /* 6px — exception per spec */
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 15px !important;
        letter-spacing: 0.02em;
        padding: 12px 24px !important;
        box-shadow: 0 0 0 0 transparent !important;
        transition: background 0.2s ease, box-shadow 0.2s ease !important;
        text-transform: none;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #7a52f5 !important;
        box-shadow:
            0 0 24px rgba(102,58,243,0.45),
            inset 0 1px 1px rgba(255,255,255,0.15) !important;
        transform: translateY(-1px);
    }
    div.stButton > button[kind="primary"]::before { content: none; }

    /* ── Secondary / Ghost Buttons ───────────────────────────────── */
    div.stButton > button:not([kind="primary"]) {
        background: rgba(186,214,247,0.06) !important;
        color: var(--color-pure-white) !important;
        border: 1px inset var(--color-glass-edge) !important;
        border-radius: var(--radius-pill) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 8px 16px !important;
        transition: background 0.2s ease !important;
        box-shadow: none !important;
        text-shadow: none !important;
    }
    div.stButton > button:not([kind="primary"]):hover {
        background: rgba(186,214,247,0.12) !important;
        transform: none;
    }

    /* ── Download Button — Ghost Pill ────────────────────────────── */
    div[data-testid="stDownloadButton"] > button {
        background: rgba(186,214,247,0.06) !important;
        color: var(--color-pure-white) !important;
        border: 1px inset var(--color-glass-edge) !important;
        border-radius: var(--radius-pill) !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 500 !important;
        font-size: 13px !important;
        padding: 8px 20px !important;
        transition: background 0.2s ease !important;
        box-shadow: none !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background: rgba(186,214,247,0.12) !important;
        transform: none;
        box-shadow: none !important;
    }

    /* ── Inputs, Selects, Sliders ────────────────────────────────── */
    input, select, textarea {
        background: rgba(186,214,247,0.04) !important;
        color: var(--color-frost-glow) !important;
        border: 1px inset var(--color-glass-edge) !important;
        border-radius: var(--radius-badge) !important;
        font-family: 'Inter', sans-serif !important;
    }
    div[data-testid="stSlider"] > div > div > div {
        background: var(--color-void-violet) !important;
    }
    div[data-testid="stNumberInput"] input {
        border-radius: var(--radius-badge) !important;
    }

    /* ── Radio (nav) ─────────────────────────────────────────────── */
    div[data-testid="stRadio"] label {
        color: var(--color-moon-mist) !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 14px !important;
        font-weight: 500 !important;
    }
    div[data-testid="stRadio"] label:has(input:checked) {
        color: var(--color-frost-glow) !important;
    }

    /* ── Dividers ────────────────────────────────────────────────── */
    hr {
        border-color: var(--color-glass-edge) !important;
        margin: 16px 0 !important;
    }

    /* ── DataFrame ───────────────────────────────────────────────── */
    div[data-testid="stDataFrame"] {
        background: rgba(186,214,247,0.02);
        border: 1px inset var(--color-glass-edge);
        border-radius: var(--radius-card);
        padding: 12px;
    }

    /* ── Status / Alert strips ───────────────────────────────────── */
    div[data-testid="stAlert"] {
        border-radius: var(--radius-badge) !important;
        border: 1px inset var(--color-glass-edge) !important;
        font-family: 'Inter', sans-serif !important;
    }

    /* ── Expander header text ────────────────────────────────────── */
    /* Target the label <p> only — NOT the icon <span> which uses
       Material Icons font. Targeting summary span breaks the arrow glyphs. */
    div[data-testid="stExpander"] summary p,
    div[data-testid="stExpander"] summary > div > p {
        font-family: 'Inter', sans-serif !important;
        color: var(--color-moon-mist) !important;
        font-weight: 600 !important;
        font-size: 14px !important;
    }

    /* ── Tabs ────────────────────────────────────────────────────── */
    div[data-testid="stTabs"] button {
        font-family: 'Inter', sans-serif !important;
        color: var(--color-fog-veil) !important;
        font-weight: 500 !important;
        border-radius: var(--radius-badge) var(--radius-badge) 0 0 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: var(--color-frost-glow) !important;
        border-bottom-color: var(--color-void-violet) !important;
    }

    /* ── Map glass wrapper (applied via st.markdown container) ───── */
    .authkit-map-card {
        background: rgba(186,214,247,0.03);
        border-radius: var(--radius-card);
        border: 1px inset var(--color-glass-edge);
        box-shadow: var(--elevation-glass);
        padding: 24px;
        margin-bottom: 16px;
    }

    /* ── Eyebrow label ───────────────────────────────────────────── */
    .authkit-eyebrow {
        display: flex;
        align-items: center;
        gap: 12px;
        justify-content: center;
        margin-bottom: 8px;
    }
    .authkit-eyebrow span {
        font-family: 'JetBrains Mono', monospace;
        font-size: 13px;
        font-weight: 400;
        letter-spacing: 0.10em;
        color: var(--color-moon-mist);
        text-transform: uppercase;
    }
    .authkit-eyebrow::before,
    .authkit-eyebrow::after {
        content: '';
        flex: 1;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--color-glass-edge), transparent);
    }

    /* ── Status pill badges ──────────────────────────────────────── */
    .authkit-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: var(--color-luminous-fill);
        color: var(--color-frost-glow);
        border: 1px inset var(--color-glass-edge);
        border-radius: var(--radius-badge);
        padding: 4px 10px;
        font-family: 'Inter', sans-serif;
        font-size: 12px;
        font-weight: 500;
    }
    .authkit-badge.status-ok    { color: #86efac; }
    .authkit-badge.status-run   { color: #fcd34d; }
    .authkit-badge.status-err   { color: #f87171; }
    .authkit-badge.status-idle  { color: var(--color-fog-veil); }

    /* ── Map header block ────────────────────────────────────────── */
    .authkit-map-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 16px;
    }
    .authkit-map-icon {
        width: 40px; height: 40px;
        border-radius: var(--radius-icon);
        background: var(--color-luminous-fill);
        border: 1px inset var(--color-glass-edge);
        display: flex; align-items: center; justify-content: center;
        font-size: 18px;
        flex-shrink: 0;
    }
    .authkit-map-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 500;
        color: var(--color-ice-highlight);
        line-height: 1.2;
    }
    .authkit-map-subtitle {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        letter-spacing: 0.10em;
        color: var(--color-fog-veil);
        text-transform: uppercase;
        margin-top: 2px;
    }

    /* ── Fleet breakdown inline badges ──────────────────────────── */
    .authkit-fleet-badge {
        display: inline-flex;
        flex-direction: column;
        gap: 2px;
        background: var(--color-luminous-fill);
        border: 1px inset var(--color-glass-edge);
        border-radius: var(--radius-badge);
        padding: 8px 14px;
        margin: 4px;
    }
    .authkit-fleet-badge .label {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: var(--color-fog-veil);
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    .authkit-fleet-badge .value {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 500;
        color: var(--color-ice-highlight);
    }

    /* ── Sidebar footer caption ──────────────────────────────────── */
    .authkit-sidebar-footer {
        text-align: center;
        color: var(--color-fog-veil);
        font-family: 'Inter', sans-serif;
        font-size: 11px;
        margin-top: 8px;
        opacity: 0.75;
    }
</style>
"""

def load_css():
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
