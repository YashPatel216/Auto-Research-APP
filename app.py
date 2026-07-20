import html as html_lib
import re

import streamlit as st
from tenacity import retry, stop_after_attempt, wait_fixed

from agents import (
    build_search_agent,
    build_scrap_agent,
    writer_chain,
    critic_chain,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AutoResearcher",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="collapsed",
)


# ============================================================
# DESIGN TOKENS
# ============================================================

BG = "#030405"

SEARCH = "#5EEAD4"
SCRAPE = "#C4A7FF"
WRITE = "#86EFAC"
CRITIQUE = "#FDBA74"

TEXT = "#F8FAFC"
BODY_TEXT = "#D7DDE7"
MUTED = "#8B96A7"


# ============================================================
# CUSTOM CSS
# ============================================================

CUSTOM_CSS = f"""
<style>

@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Space+Grotesk:wght@500;600;700&family=Space+Mono:wght@400;700&display=swap');


/* ============================================================
   GLOBAL PAGE
============================================================ */

html,
body {{
    background: {BG} !important;
    color: {TEXT} !important;
    font-family: 'DM Sans', sans-serif !important;
}}


.stApp,
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background:
        radial-gradient(
            circle at 50% -10%,
            #181D25 0%,
            #090C11 38%,
            #030405 100%
        ) !important;

    color: {TEXT} !important;
}}


[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"] {{
    background: transparent !important;
}}


#MainMenu,
footer {{
    visibility: hidden;
}}


.block-container {{
    max-width: 1250px;
    padding-top: 1rem;
    padding-bottom: 5rem;
}}


/* ============================================================
   GLOBAL TEXT
============================================================ */

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li,
[data-testid="stWidgetLabel"] p,
label {{
    color: {TEXT} !important;
    font-family: 'DM Sans', sans-serif !important;
}}


/* ============================================================
   HERO
============================================================ */

.hero {{
    width: 100%;

    text-align: center;

    margin-left: auto;
    margin-right: auto;

    padding: 4.5rem 0 1.8rem 0;
}}


.hero h1 {{
    margin: 0;

    font-family:
        'Space Grotesk',
        sans-serif !important;

    font-size:
        clamp(
            3.5rem,
            7vw,
            5.8rem
        );

    font-weight: 700;

    letter-spacing:
        -0.055em;

    line-height: 1;

    color:
        #FFFFFF !important;

    text-shadow:
        0 15px 50px
        rgba(
            0,
            0,
            0,
            0.65
        );
}}


.hero p {{
    margin-top: 1.1rem;

    font-family:
        'Space Mono',
        monospace !important;

    font-size: 0.72rem;

    font-weight: 400;

    letter-spacing:
        0.20em;

    text-transform:
        uppercase;

    color:
        {MUTED} !important;
}}


/* ============================================================
   PIPELINE
============================================================ */

.pipeline-rail {{
    display: flex;

    justify-content: center;

    align-items: center;

    gap: 0.7rem;

    flex-wrap: wrap;

    max-width: 1000px;

    margin:
        0 auto
        3.2rem auto;
}}


.pipeline-node {{
    display: flex;

    align-items: center;

    justify-content: center;

    gap: 0.7rem;

    min-width: 145px;

    padding:
        0.75rem
        1.2rem;

    background:
        linear-gradient(
            145deg,
            rgba(25, 30, 38, 0.94),
            rgba(6, 8, 12, 0.99)
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.10
        ) !important;

    border-radius:
        11px;

    color:
        #E4E9F0 !important;

    font-family:
        'Space Mono',
        monospace !important;

    font-size:
        0.70rem;

    font-weight:
        700;

    letter-spacing:
        0.07em;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.04
        ),
        0 12px 35px
        rgba(
            0,
            0,
            0,
            0.45
        );

    backdrop-filter:
        blur(18px);

    transition:
        all
        0.25s
        ease;
}}


.pipeline-node:hover {{
    transform:
        translateY(-3px);

    border-color:
        rgba(
            94,
            234,
            212,
            0.45
        ) !important;

    background:
        linear-gradient(
            145deg,
            rgba(30, 37, 46, 0.96),
            rgba(8, 11, 15, 1)
        ) !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.06
        ),
        0 16px 40px
        rgba(
            0,
            0,
            0,
            0.55
        );
}}


/* ============================================================
   PIPELINE DOT ANIMATION
============================================================ */

@keyframes pulse-dot {{

    0%,
    100% {{
        opacity: 1;
        transform: scale(1);
    }}

    50% {{
        opacity: 0.35;
        transform: scale(0.75);
    }}

}}


.dot {{
    display: inline-block;

    width: 7px;

    height: 7px;

    border-radius: 50%;

    flex-shrink: 0;

    animation:
        pulse-dot
        2s
        ease-in-out
        infinite;
}}


/* ============================================================
   INPUT CONTAINER
============================================================ */

div[data-testid="stTextInput"],
div[data-testid="stTextInput"] > div {{
    background:
        transparent !important;
}}


/* ============================================================
   INPUT
============================================================ */

div[data-testid="stTextInput"] input {{
    height:
        52px !important;

    min-height:
        52px !important;

    background:
        linear-gradient(
            145deg,
            rgba(21, 26, 34, 0.96),
            rgba(5, 7, 10, 0.99)
        ) !important;

    color:
        #F8FAFC !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.12
        ) !important;

    border-radius:
        11px !important;

    padding:
        0 1.25rem !important;

    box-sizing:
        border-box !important;

    font-family:
        'DM Sans',
        sans-serif !important;

    font-size:
        0.95rem !important;

    font-weight:
        400 !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.04
        ),
        0 10px 30px
        rgba(
            0,
            0,
            0,
            0.35
        ) !important;

    transition:
        border-color
        0.25s ease,
        box-shadow
        0.25s ease !important;
}}


div[data-testid="stTextInput"] input::placeholder {{
    color:
        #758091 !important;

    opacity:
        1;
}}


div[data-testid="stTextInput"] input:focus {{
    border-color:
        {SEARCH} !important;

    outline:
        none !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.05
        ),
        0 0 0 3px
        rgba(
            94,
            234,
            212,
            0.08
        ),
        0 12px 35px
        rgba(
            0,
            0,
            0,
            0.45
        ) !important;
}}


/* ============================================================
   INITIALIZE BUTTON
   BLACK POLISHED GLASS
============================================================ */

div.stButton > button {{
    width:
        100% !important;

    height:
        52px !important;

    min-height:
        52px !important;

    padding:
        0 1.5rem !important;

    box-sizing:
        border-box !important;

    background:
        linear-gradient(
            145deg,
            rgba(28, 34, 43, 0.97),
            rgba(7, 9, 13, 0.99)
        ) !important;

    color:
        #F8FAFC !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.13
        ) !important;

    border-radius:
        11px !important;

    font-family:
        'Space Mono',
        monospace !important;

    font-size:
        0.75rem !important;

    font-weight:
        700 !important;

    letter-spacing:
        0.05em;

    text-transform:
        uppercase;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.06
        ),
        0 10px 30px
        rgba(
            0,
            0,
            0,
            0.45
        ) !important;

    transition:
        all
        0.25s
        ease;
}}


div.stButton > button p {{
    margin: 0 !important;

    color:
        #F8FAFC !important;

    font-family:
        'Space Mono',
        monospace !important;

    font-weight:
        700 !important;
}}


div.stButton > button:hover {{
    background:
        linear-gradient(
            145deg,
            rgba(36, 44, 55, 0.98),
            rgba(10, 13, 18, 1)
        ) !important;

    color:
        #FFFFFF !important;

    border-color:
        {SEARCH} !important;

    transform:
        translateY(-2px);

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.08
        ),
        0 15px 40px
        rgba(
            0,
            0,
            0,
            0.55
        ),
        0 0 25px
        rgba(
            94,
            234,
            212,
            0.08
        ) !important;
}}


/* ============================================================
   CUSTOM PROCESSING PANEL
   REPLACES st.status()
============================================================ */

.processing-panel {{
    position: relative;

    display: flex;

    align-items: center;

    gap: 1rem;

    width: 100%;

    box-sizing: border-box;

    margin-top: 1.2rem;

    margin-bottom: 1.5rem;

    padding:
        1.2rem
        1.4rem;

    background:
        linear-gradient(
            145deg,
            rgba(20, 25, 32, 0.98),
            rgba(4, 6, 9, 0.99)
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.10
        ) !important;

    border-radius:
        14px;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.04
        ),
        0 18px 50px
        rgba(
            0,
            0,
            0,
            0.55
        );

    overflow:
        hidden;
}}


/* Teal top accent */

.processing-panel::before {{
    content: "";

    position: absolute;

    top: 0;

    left: 0;

    width: 100%;

    height: 2px;

    background:
        linear-gradient(
            90deg,
            transparent,
            {SEARCH},
            transparent
        );
}}


/* Processing indicator */

.processing-spinner {{
    position: relative;

    width: 20px;

    height: 20px;

    min-width: 20px;

    border:
        2px solid
        rgba(
            94,
            234,
            212,
            0.18
        );

    border-top-color:
        {SEARCH};

    border-radius:
        50%;

    animation:
        processing-spin
        0.8s
        linear
        infinite;
}}


@keyframes processing-spin {{

    from {{
        transform:
            rotate(0deg);
    }}

    to {{
        transform:
            rotate(360deg);
    }}

}}


/* Processing content */

.processing-content {{
    display: flex;

    flex-direction: column;

    gap: 0.25rem;
}}


.processing-title {{
    color:
        #F8FAFC !important;

    font-family:
        'Space Grotesk',
        sans-serif !important;

    font-size:
        1rem;

    font-weight:
        600;

    letter-spacing:
        -0.01em;
}}


.processing-step {{
    color:
        #9CA8B8 !important;

    font-family:
        'DM Sans',
        sans-serif !important;

    font-size:
        0.88rem;

    font-weight:
        400;
}}


/* ============================================================
   COMPLETED PROCESSING PANEL
============================================================ */

.processing-complete {{
    position: relative;

    display: flex;

    align-items: center;

    gap: 1rem;

    width: 100%;

    box-sizing: border-box;

    margin-top: 1.2rem;

    margin-bottom: 1.5rem;

    padding:
        1.2rem
        1.4rem;

    background:
        linear-gradient(
            145deg,
            rgba(18, 29, 27, 0.98),
            rgba(4, 8, 8, 0.99)
        ) !important;

    border:
        1px solid
        rgba(
            94,
            234,
            212,
            0.20
        ) !important;

    border-radius:
        14px;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.04
        ),
        0 18px 50px
        rgba(
            0,
            0,
            0,
            0.50
        );
}}


.complete-icon {{
    display: flex;

    align-items: center;

    justify-content: center;

    width: 24px;

    height: 24px;

    min-width: 24px;

    border-radius: 50%;

    background:
        rgba(
            94,
            234,
            212,
            0.10
        );

    border:
        1px solid
        rgba(
            94,
            234,
            212,
            0.35
        );

    color:
        {SEARCH} !important;

    font-family:
        'Space Mono',
        monospace;

    font-size:
        0.75rem;

    font-weight:
        700;
}}


/* ============================================================
   RESULT CARDS
============================================================ */

.glass {{
    position: relative;

    overflow: hidden;

    background:
        linear-gradient(
            145deg,
            rgba(21, 26, 34, 0.97),
            rgba(5, 7, 10, 0.99)
        ) !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.09
        ) !important;

    border-radius:
        18px;

    padding:
        2.6rem
        2.8rem;

    min-height:
        280px;

    margin-bottom:
        1.8rem;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.04
        ),
        0 25px 70px
        rgba(
            0,
            0,
            0,
            0.52
        ) !important;

    backdrop-filter:
        blur(20px);

    transition:
        transform
        0.25s ease,
        border-color
        0.25s ease,
        box-shadow
        0.25s ease;
}}


.glass:hover {{
    transform:
        translateY(-3px);

    border-color:
        var(--accent) !important;

    box-shadow:
        inset 0 1px 0
        rgba(
            255,
            255,
            255,
            0.05
        ),
        0 30px 80px
        rgba(
            0,
            0,
            0,
            0.60
        ) !important;
}}


.glass::before {{
    content: "";

    position: absolute;

    top: 0;

    left: 0;

    width: 100%;

    height: 3px;

    background:
        var(--accent);
}}


/* ============================================================
   CARD HEADER
============================================================ */

.glass-header {{
    display: flex;

    align-items: center;

    gap: 1.2rem;

    margin-bottom:
        1.6rem;
}}


.glass-header .tag {{
    font-family:
        'Space Mono',
        monospace !important;

    font-size:
        0.78rem;

    font-weight:
        700;

    letter-spacing:
        0.09em;

    text-transform:
        uppercase;
}}


.glass-header h3 {{
    margin: 0;

    font-family:
        'Space Grotesk',
        sans-serif;

    font-size:
        1.55rem;

    font-weight:
        600;

    letter-spacing:
        -0.025em;

    color:
        #FFFFFF !important;
}}


/* ============================================================
   CARD CONTENT
============================================================ */

.glass-body {{
    color:
        {BODY_TEXT} !important;

    font-family:
        'DM Sans',
        sans-serif;

    font-size:
        1.08rem;

    font-weight:
        400;

    line-height:
        1.85;

    white-space:
        pre-wrap;

    overflow-wrap:
        anywhere;

    min-height:
        170px;

    max-height:
        600px;

    overflow-y:
        auto;

    padding-right:
        1rem;
}}


/* ============================================================
   SCROLLBAR
============================================================ */

.glass-body::-webkit-scrollbar {{
    width: 5px;
}}


.glass-body::-webkit-scrollbar-track {{
    background:
        transparent;
}}


.glass-body::-webkit-scrollbar-thumb {{
    background:
        #374151;

    border-radius:
        10px;
}}


.glass-body::-webkit-scrollbar-thumb:hover {{
    background:
        #566173;
}}


/* ============================================================
   SCORE BADGE
============================================================ */

.score-badge {{
    display:
        inline-flex;

    align-items:
        center;

    justify-content:
        center;

    width:
        68px;

    height:
        68px;

    border-radius:
        14px;

    border:
        1px solid
        rgba(
            253,
            186,
            116,
            0.30
        );

    background:
        linear-gradient(
            145deg,
            rgba(253, 186, 116, 0.10),
            rgba(5, 7, 10, 0.90)
        );

    color:
        {CRITIQUE};

    font-family:
        'Space Grotesk',
        sans-serif;

    font-size:
        1.55rem;

    font-weight:
        700;

    flex-shrink:
        0;
}}


/* ============================================================
   ALERTS
============================================================ */

div[data-testid="stAlert"] {{
    background:
        linear-gradient(
            145deg,
            rgba(24, 28, 35, 0.98),
            rgba(6, 8, 11, 0.99)
        ) !important;

    color:
        #F8FAFC !important;

    border:
        1px solid
        rgba(
            255,
            255,
            255,
            0.10
        ) !important;

    border-radius:
        12px !important;
}}


div[data-testid="stAlert"] p {{
    color:
        #F8FAFC !important;
}}


/* ============================================================
   ERROR
============================================================ */

.error-glass {{
    background:
        linear-gradient(
            145deg,
            rgba(40, 15, 20, 0.90),
            rgba(8, 5, 7, 0.99)
        );

    border:
        1px solid
        rgba(
            251,
            113,
            133,
            0.30
        );

    border-left:
        3px solid
        #FB7185;

    border-radius:
        12px;

    padding:
        1.3rem
        1.6rem;

    color:
        #FDA4AF !important;

    font-family:
        'Space Mono',
        monospace;

    font-size:
        0.9rem;
}}


/* ============================================================
   REMOVE LIGHT CONTAINER BACKGROUNDS
============================================================ */

[data-testid="stVerticalBlock"],
[data-testid="stHorizontalBlock"] {{
    background:
        transparent;
}}

</style>
"""


# ============================================================
# APPLY CSS
# ============================================================

st.markdown(
    CUSTOM_CSS,
    unsafe_allow_html=True,
)


# ============================================================
# HERO
# ============================================================

HERO_HTML = (
    '<div class="hero">'
    '<h1>AutoResearcher</h1>'
    '<p>Intelligent Agent Pipeline</p>'
    '</div>'
)

st.markdown(
    HERO_HTML,
    unsafe_allow_html=True,
)


# ============================================================
# PIPELINE MODULES
# ============================================================

PIPELINE_HTML = (
    f'<div class="pipeline-rail">'

    f'<div class="pipeline-node">'
    f'<span class="dot" '
    f'style="background:{SEARCH};'
    f'color:{SEARCH};'
    f'animation-delay:0s;">'
    f'</span>'
    f'01 SEARCH'
    f'</div>'

    f'<div class="pipeline-node">'
    f'<span class="dot" '
    f'style="background:{SCRAPE};'
    f'color:{SCRAPE};'
    f'animation-delay:0.4s;">'
    f'</span>'
    f'02 SCRAPE'
    f'</div>'

    f'<div class="pipeline-node">'
    f'<span class="dot" '
    f'style="background:{WRITE};'
    f'color:{WRITE};'
    f'animation-delay:0.8s;">'
    f'</span>'
    f'03 WRITE'
    f'</div>'

    f'<div class="pipeline-node">'
    f'<span class="dot" '
    f'style="background:{CRITIQUE};'
    f'color:{CRITIQUE};'
    f'animation-delay:1.2s;">'
    f'</span>'
    f'04 CRITIQUE'
    f'</div>'

    f'</div>'
)

st.markdown(
    PIPELINE_HTML,
    unsafe_allow_html=True,
)


# ============================================================
# HELPERS
# ============================================================

@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(2),
    reraise=True,
)
def _invoke_agent(
    agent,
    user_message: str,
):

    return agent.invoke(
        {
            "messages": [
                (
                    "user",
                    user_message,
                )
            ]
        }
    )


# ============================================================
# RESULT CARD
# ============================================================

def _glass_card(
    tag: str,
    title: str,
    body: str,
    accent: str,
):

    safe_tag = html_lib.escape(
        str(tag)
    )

    safe_title = html_lib.escape(
        str(title)
    )

    safe_body = html_lib.escape(
        str(body)
    )

    card_html = (
        f'<div class="glass" '
        f'style="--accent:{accent};">'

        f'<div class="glass-header">'

        f'<span class="tag" '
        f'style="color:{accent} !important;">'
        f'{safe_tag}'
        f'</span>'

        f'<h3>'
        f'{safe_title}'
        f'</h3>'

        f'</div>'

        f'<div class="glass-body">'
        f'{safe_body}'
        f'</div>'

        f'</div>'
    )

    st.markdown(
        card_html,
        unsafe_allow_html=True,
    )


# ============================================================
# PROCESSING PANEL
# ============================================================

def _processing_html(
    title: str,
    step: str,
):

    safe_title = html_lib.escape(
        str(title)
    )

    safe_step = html_lib.escape(
        str(step)
    )

    return (
        f'<div class="processing-panel">'

        f'<div class="processing-spinner">'
        f'</div>'

        f'<div class="processing-content">'

        f'<div class="processing-title">'
        f'{safe_title}'
        f'</div>'

        f'<div class="processing-step">'
        f'{safe_step}'
        f'</div>'

        f'</div>'

        f'</div>'
    )


# ============================================================
# COMPLETE PANEL
# ============================================================

def _complete_html():

    return (
        f'<div class="processing-complete">'

        f'<div class="complete-icon">'
        f'✓'
        f'</div>'

        f'<div class="processing-content">'

        f'<div class="processing-title">'
        f'Research pipeline complete'
        f'</div>'

        f'<div class="processing-step">'
        f'Search, extraction, writing and critique completed successfully.'
        f'</div>'

        f'</div>'

        f'</div>'
    )


# ============================================================
# SCORE EXTRACTOR
# ============================================================

def _extract_score(
    feedback: str,
) -> str:

    match = re.search(
        r"Score\s*:\s*(\d+(?:\.\d+)?)\s*/\s*10",
        str(feedback),
        re.IGNORECASE,
    )

    if match:
        return match.group(1)

    return "—"


# ============================================================
# INPUT CONSOLE
# ============================================================

col1, col2 = st.columns(
    [5, 1],
    vertical_alignment="center",
)


with col1:

    topic = st.text_input(
        "Research topic",
        placeholder=(
            "e.g. Impact of quantum computing "
            "on cryptography..."
        ),
        label_visibility="collapsed",
    )


with col2:

    run_clicked = st.button(
        "Initialize",
        use_container_width=True,
    )


# ============================================================
# SESSION STATE
# ============================================================

if "history" not in st.session_state:
    st.session_state.history = None


# ============================================================
# RUN PIPELINE
# ============================================================

if run_clicked:

    if not topic or not topic.strip():

        st.warning(
            "Please enter a research topic to begin."
        )

    else:

        state = {}

        # Custom processing placeholder
        # This replaces Streamlit st.status()

        processing_placeholder = st.empty()

        try:

            # ====================================================
            # 01 SEARCH
            # ====================================================

            processing_placeholder.markdown(
                _processing_html(
                    "Gathering intelligence...",
                    "01 · Initializing Search Agent",
                ),
                unsafe_allow_html=True,
            )

            search_agent = (
                build_search_agent()
            )

            search_result = _invoke_agent(
                search_agent,
                (
                    "Please search the web for "
                    "research and reliable information "
                    f"on the topic: {topic}."
                ),
            )

            state["search_result"] = (
                search_result[
                    "messages"
                ][-1].content
            )


            # ====================================================
            # 02 SCRAPE
            # ====================================================

            processing_placeholder.markdown(
                _processing_html(
                    "Extracting deep content...",
                    "02 · Scraping relevant research sources",
                ),
                unsafe_allow_html=True,
            )

            reader_agent = (
                build_scrap_agent()
            )

            reader_result = _invoke_agent(
                reader_agent,
                (
                    "Based on the following research "
                    f"results about {topic}, pick the "
                    "most relevant URLs and scrape them "
                    "for deeper content on the topic."
                    "\n\n"
                    "Search results:\n"
                    f"{state['search_result'][:800]}"
                ),
            )

            state["scraped_content"] = (
                reader_result[
                    "messages"
                ][-1].content
            )


            # ====================================================
            # 03 WRITE
            # ====================================================

            processing_placeholder.markdown(
                _processing_html(
                    "Drafting technical report...",
                    "03 · Compiling research into a structured report",
                ),
                unsafe_allow_html=True,
            )

            research_combined = (
                "SEARCH RESULT:\n"
                f"{state['search_result']}"
                "\n\n"
                "DETAILED SCRAPED CONTENT:\n"
                f"{state['scraped_content']}"
            )

            state["report"] = (
                writer_chain.invoke(
                    {
                        "topic":
                            topic,

                        "research":
                            research_combined,
                    }
                )
            )


            # ====================================================
            # 04 CRITIQUE
            # ====================================================

            processing_placeholder.markdown(
                _processing_html(
                    "Executing editorial critique...",
                    "04 · Reviewing accuracy, quality and completeness",
                ),
                unsafe_allow_html=True,
            )

            state["feedback"] = (
                critic_chain.invoke(
                    {
                        "report":
                            state["report"],

                        "research":
                            research_combined,
                    }
                )
            )


            # ====================================================
            # COMPLETE
            # ====================================================

            processing_placeholder.markdown(
                _complete_html(),
                unsafe_allow_html=True,
            )

            state["topic"] = topic

            st.session_state.history = (
                state
            )


        # ========================================================
        # ERROR HANDLING
        # ========================================================

        except Exception as exc:

            processing_placeholder.empty()

            safe_error = html_lib.escape(
                str(exc)
            )

            error_html = (
                f'<div class="error-glass">'
                f'Pipeline exception: '
                f'{safe_error}'
                f'</div>'
            )

            st.markdown(
                error_html,
                unsafe_allow_html=True,
            )


# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.history:

    state = (
        st.session_state.history
    )


    # ========================================================
    # 01 SEARCH
    # ========================================================

    _glass_card(
        "01 · Search",
        "Sources Gathered",
        state[
            "search_result"
        ],
        SEARCH,
    )


    # ========================================================
    # 02 SCRAPE
    # ========================================================

    _glass_card(
        "02 · Scrape",
        "Deep Content Extracted",
        state[
            "scraped_content"
        ],
        SCRAPE,
    )


    # ========================================================
    # 03 WRITE
    # ========================================================

    _glass_card(
        "03 · Write",
        (
            "Compiled Report: "
            f"{state['topic']}"
        ),
        state[
            "report"
        ],
        WRITE,
    )


    # ========================================================
    # 04 CRITIQUE
    # ========================================================

    score = _extract_score(
        state[
            "feedback"
        ]
    )

    safe_feedback = html_lib.escape(
        str(
            state[
                "feedback"
            ]
        )
    )

    critique_html = (
        f'<div class="glass" '
        f'style="--accent:{CRITIQUE};">'

        f'<div class="glass-header" '
        f'style="justify-content:space-between;">'

        f'<div style="'
        f'display:flex;'
        f'align-items:center;'
        f'gap:1.2rem;'
        f'">'

        f'<span class="tag" '
        f'style="color:{CRITIQUE} !important;">'
        f'04 · Critique'
        f'</span>'

        f'<h3>'
        f'Editorial Review'
        f'</h3>'

        f'</div>'

        f'<div class="score-badge">'
        f'{score}'
        f'</div>'

        f'</div>'

        f'<div class="glass-body">'
        f'{safe_feedback}'
        f'</div>'

        f'</div>'
    )

    st.markdown(
        critique_html,
        unsafe_allow_html=True,
    )