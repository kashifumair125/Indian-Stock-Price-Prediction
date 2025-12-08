"""
Premium Responsive Styles for Stock Prediction App
Modern, Mobile-First CSS with Dark Mode Support
"""

def get_premium_css(dark_mode=False):
    """Generate premium responsive CSS based on theme"""

    # Color schemes
    if dark_mode:
        colors = {
            'bg_primary': '#0e1117',
            'bg_secondary': '#1a1d29',
            'bg_tertiary': '#262b3d',
            'text_primary': '#ffffff',
            'text_secondary': '#b4b8c5',
            'border': '#2d3548',
            'accent_1': '#667eea',
            'accent_2': '#764ba2',
            'success': '#10b981',
            'danger': '#ef4444',
            'warning': '#f59e0b',
            'info': '#3b82f6',
        }
    else:
        colors = {
            'bg_primary': '#ffffff',
            'bg_secondary': '#f8f9fa',
            'bg_tertiary': '#f0f2f6',
            'text_primary': '#262730',
            'text_secondary': '#6c757d',
            'border': '#e1e4e8',
            'accent_1': '#667eea',
            'accent_2': '#764ba2',
            'success': '#2ca02c',
            'danger': '#d62728',
            'warning': '#ff7f0e',
            'info': '#1f77b4',
        }

    return f"""
<style>
    /* ========================================
       PREMIUM RESPONSIVE STYLES
       Mobile-First Approach with Dark Mode
       ======================================== */

    /* Root Variables */
    :root {{
        --bg-primary: {colors['bg_primary']};
        --bg-secondary: {colors['bg_secondary']};
        --bg-tertiary: {colors['bg_tertiary']};
        --text-primary: {colors['text_primary']};
        --text-secondary: {colors['text_secondary']};
        --border: {colors['border']};
        --accent-1: {colors['accent_1']};
        --accent-2: {colors['accent_2']};
        --success: {colors['success']};
        --danger: {colors['danger']};
        --warning: {colors['warning']};
        --info: {colors['info']};
        --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
        --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 15px rgba(0,0,0,0.1);
        --shadow-xl: 0 20px 25px rgba(0,0,0,0.15);
        --radius-sm: 0.375rem;
        --radius-md: 0.5rem;
        --radius-lg: 0.75rem;
        --radius-xl: 1rem;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }}

    /* Base Styles */
    .stApp {{
        background: var(--bg-primary);
        color: var(--text-primary);
        transition: var(--transition);
    }}

    /* Hide Default Streamlit Elements */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    header {{visibility: hidden;}}

    /* ========================================
       TYPOGRAPHY - Responsive Font Sizes
       ======================================== */

    h1, h2, h3, h4, h5, h6 {{
        color: var(--text-primary);
        font-weight: 700;
        line-height: 1.2;
    }}

    /* Mobile First - Base sizes */
    h1 {{ font-size: 1.75rem; }}
    h2 {{ font-size: 1.5rem; }}
    h3 {{ font-size: 1.25rem; }}
    h4 {{ font-size: 1.1rem; }}

    /* Tablet & Up */
    @media (min-width: 640px) {{
        h1 {{ font-size: 2.25rem; }}
        h2 {{ font-size: 1.875rem; }}
        h3 {{ font-size: 1.5rem; }}
        h4 {{ font-size: 1.25rem; }}
    }}

    /* Desktop & Up */
    @media (min-width: 1024px) {{
        h1 {{ font-size: 3rem; }}
        h2 {{ font-size: 2.25rem; }}
        h3 {{ font-size: 1.875rem; }}
        h4 {{ font-size: 1.5rem; }}
    }}

    /* ========================================
       HEADER - Animated Gradient
       ======================================== */

    .main-header {{
        font-size: clamp(1.75rem, 4vw, 3.5rem);
        background: linear-gradient(
            135deg,
            var(--accent-1) 0%,
            var(--accent-2) 50%,
            var(--info) 100%
        );
        background-size: 200% 200%;
        animation: gradientShift 8s ease infinite;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin: 1rem 0 2rem 0;
        font-weight: 800;
        letter-spacing: -0.02em;
    }}

    @keyframes gradientShift {{
        0%, 100% {{ background-position: 0% 50%; }}
        50% {{ background-position: 100% 50%; }}
    }}

    /* ========================================
       CARDS - Modern Glass Morphism
       ======================================== */

    .glass-card {{
        background: {f'rgba(255, 255, 255, 0.05)' if dark_mode else 'rgba(255, 255, 255, 0.95)'};
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        border-radius: var(--radius-xl);
        border: 1px solid {f'rgba(255, 255, 255, 0.1)' if dark_mode else 'rgba(0, 0, 0, 0.05)'};
        box-shadow: var(--shadow-lg);
        padding: clamp(1rem, 3vw, 2rem);
        margin: 1rem 0;
        transition: var(--transition);
    }}

    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
    }}

    .metric-card {{
        background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%);
        padding: clamp(1rem, 2vw, 1.5rem);
        border-radius: var(--radius-lg);
        color: white;
        text-align: center;
        box-shadow: var(--shadow-md);
        margin: 0.5rem 0;
        transition: var(--transition);
    }}

    .metric-card:hover {{
        transform: scale(1.05);
        box-shadow: var(--shadow-xl);
    }}

    .metric-card h3 {{
        color: white;
        font-size: clamp(0.875rem, 2vw, 1rem);
        margin-bottom: 0.5rem;
        opacity: 0.9;
    }}

    .metric-card h2 {{
        color: white;
        font-size: clamp(1.5rem, 3vw, 2.5rem);
        margin: 0;
        font-weight: 800;
    }}

    /* Status Cards */
    .success-box {{
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: var(--radius-lg);
        color: white;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }}

    .warning-box {{
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: var(--radius-lg);
        color: white;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }}

    .error-box {{
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: var(--radius-lg);
        color: white;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }}

    .info-box {{
        background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%);
        padding: clamp(1rem, 3vw, 1.5rem);
        border-radius: var(--radius-lg);
        color: white;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }}

    /* ========================================
       BUTTONS - Premium Interactive Styles
       ======================================== */

    .stButton > button {{
        background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%);
        color: white;
        border: none;
        border-radius: 9999px;
        padding: 0.75rem 2rem;
        font-weight: 700;
        font-size: clamp(0.875rem, 2vw, 1.1rem);
        box-shadow: var(--shadow-md);
        transition: var(--transition);
        width: 100%;
        cursor: pointer;
    }}

    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: var(--shadow-xl);
        background: linear-gradient(135deg, var(--accent-2) 0%, var(--accent-1) 100%);
    }}

    .stButton > button:active {{
        transform: translateY(0);
    }}

    /* Popular Stock Buttons */
    .popular-stock-btn button {{
        background: var(--bg-secondary) !important;
        color: var(--accent-1) !important;
        border: 2px solid var(--accent-1) !important;
        border-radius: 9999px !important;
        padding: 0.6rem 1.2rem !important;
        font-weight: 700 !important;
        width: 100% !important;
        transition: var(--transition) !important;
    }}

    .popular-stock-btn button:hover {{
        background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%) !important;
        color: white !important;
        transform: translateY(-2px) !important;
        box-shadow: var(--shadow-lg) !important;
    }}

    /* ========================================
       SIDEBAR - Responsive & Modern
       ======================================== */

    [data-testid="stSidebar"] {{
        background: var(--bg-secondary);
        border-right: 1px solid var(--border);
        transition: var(--transition);
    }}

    /* Mobile - Overlay Sidebar */
    @media (max-width: 768px) {{
        [data-testid="stSidebar"] {{
            position: fixed;
            z-index: 999;
            height: 100vh;
            overflow-y: auto;
        }}

        [data-testid="stSidebar"][aria-expanded="false"] {{
            margin-left: -300px;
        }}
    }}

    .sidebar-banner {{
        background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%);
        color: white;
        padding: clamp(0.75rem, 2vw, 1rem);
        border-radius: var(--radius-lg);
        text-align: center;
        margin: 1rem 0;
        box-shadow: var(--shadow-md);
    }}

    /* ========================================
       FORM ELEMENTS - Enhanced UX
       ======================================== */

    .stSelectbox, .stTextInput, .stSlider {{
        margin: 0.5rem 0;
    }}

    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {{
        background: var(--bg-tertiary);
        border: 1px solid var(--border);
        border-radius: var(--radius-md);
        color: var(--text-primary);
        padding: 0.75rem 1rem;
        transition: var(--transition);
    }}

    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {{
        border-color: var(--accent-1);
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
    }}

    /* ========================================
       PROGRESS & LOADING - Smooth Animations
       ======================================== */

    .stProgress > div > div > div > div {{
        background: linear-gradient(90deg, var(--accent-1), var(--accent-2));
    }}

    .loading-skeleton {{
        background: linear-gradient(
            90deg,
            var(--bg-secondary) 25%,
            var(--bg-tertiary) 50%,
            var(--bg-secondary) 75%
        );
        background-size: 200% 100%;
        animation: loading 1.5s ease-in-out infinite;
        border-radius: var(--radius-md);
        height: 20px;
        margin: 0.5rem 0;
    }}

    @keyframes loading {{
        0% {{ background-position: 200% 0; }}
        100% {{ background-position: -200% 0; }}
    }}

    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.5; }}
    }}

    .pulse {{
        animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
    }}

    /* ========================================
       TABLES - Modern DataFrames
       ======================================== */

    .dataframe {{
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        width: 100%;
        font-size: clamp(0.75rem, 1.5vw, 0.9rem);
    }}

    .dataframe thead th {{
        background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%);
        color: white;
        padding: 0.75rem;
        font-weight: 700;
        text-align: left;
    }}

    .dataframe tbody tr {{
        border-bottom: 1px solid var(--border);
        transition: var(--transition);
    }}

    .dataframe tbody tr:hover {{
        background: var(--bg-tertiary);
    }}

    .dataframe tbody td {{
        padding: 0.75rem;
        color: var(--text-primary);
    }}

    /* ========================================
       RESPONSIVE GRID - Flexible Layouts
       ======================================== */

    .responsive-grid {{
        display: grid;
        gap: 1rem;
        grid-template-columns: 1fr;
    }}

    @media (min-width: 640px) {{
        .responsive-grid {{
            grid-template-columns: repeat(2, 1fr);
        }}
    }}

    @media (min-width: 1024px) {{
        .responsive-grid {{
            grid-template-columns: repeat(3, 1fr);
        }}
    }}

    @media (min-width: 1280px) {{
        .responsive-grid {{
            grid-template-columns: repeat(4, 1fr);
        }}
    }}

    /* ========================================
       TOOLTIPS & HELP - Better Guidance
       ======================================== */

    .tooltip {{
        position: relative;
        display: inline-block;
        cursor: help;
    }}

    .tooltip:hover::after {{
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background: var(--bg-tertiary);
        color: var(--text-primary);
        padding: 0.5rem 1rem;
        border-radius: var(--radius-md);
        font-size: 0.875rem;
        white-space: nowrap;
        box-shadow: var(--shadow-lg);
        z-index: 1000;
    }}

    /* ========================================
       CHARTS - Enhanced Plotly Styling
       ======================================== */

    .js-plotly-plot {{
        border-radius: var(--radius-lg);
        overflow: hidden;
        box-shadow: var(--shadow-md);
        margin: 1rem 0;
    }}

    /* ========================================
       METRICS - Streamlit Native Enhancement
       ======================================== */

    [data-testid="stMetricValue"] {{
        font-size: clamp(1.5rem, 3vw, 2.5rem);
        font-weight: 700;
        color: var(--text-primary);
    }}

    [data-testid="stMetricDelta"] {{
        font-size: clamp(0.875rem, 1.5vw, 1rem);
    }}

    /* ========================================
       FLOATING ACTION BUTTON - Mobile UX
       ======================================== */

    .fab {{
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: linear-gradient(135deg, var(--accent-1) 0%, var(--accent-2) 100%);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        box-shadow: var(--shadow-xl);
        cursor: pointer;
        transition: var(--transition);
        z-index: 998;
    }}

    .fab:hover {{
        transform: scale(1.1) rotate(90deg);
        box-shadow: 0 8px 30px rgba(102, 126, 234, 0.4);
    }}

    /* Hide on desktop */
    @media (min-width: 1024px) {{
        .fab {{
            display: none;
        }}
    }}

    /* ========================================
       DARK MODE TOGGLE - Smooth Transition
       ======================================== */

    .dark-mode-toggle {{
        position: fixed;
        top: 20px;
        right: 20px;
        width: 50px;
        height: 50px;
        border-radius: 50%;
        background: var(--bg-secondary);
        border: 2px solid var(--border);
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        transition: var(--transition);
        z-index: 999;
        box-shadow: var(--shadow-md);
    }}

    .dark-mode-toggle:hover {{
        transform: rotate(180deg);
        box-shadow: var(--shadow-lg);
    }}

    /* ========================================
       ACCESSIBILITY - A11Y Improvements
       ======================================== */

    *:focus {{
        outline: 2px solid var(--accent-1);
        outline-offset: 2px;
    }}

    .sr-only {{
        position: absolute;
        width: 1px;
        height: 1px;
        padding: 0;
        margin: -1px;
        overflow: hidden;
        clip: rect(0, 0, 0, 0);
        white-space: nowrap;
        border-width: 0;
    }}

    /* ========================================
       RESPONSIVE UTILITIES
       ======================================== */

    /* Hide on mobile */
    .hide-mobile {{
        display: none;
    }}

    @media (min-width: 768px) {{
        .hide-mobile {{
            display: block;
        }}
    }}

    /* Show only on mobile */
    .show-mobile {{
        display: block;
    }}

    @media (min-width: 768px) {{
        .show-mobile {{
            display: none;
        }}
    }}

    /* ========================================
       PERFORMANCE OPTIMIZATIONS
       ======================================== */

    * {{
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
    }}

    img {{
        max-width: 100%;
        height: auto;
    }}

    /* Reduce motion for accessibility */
    @media (prefers-reduced-motion: reduce) {{
        * {{
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }}
    }}
</style>
"""
