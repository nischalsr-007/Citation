import streamlit as st
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re
import os
from pypdf import PdfReader
from google import genai
from google.genai import types

# Page Configuration
st.set_page_config(
    page_title="Nischal Citation | OSCOLA 4th Edition", 
    page_icon="✒️",
    layout="centered"
)

# Initialize Gemini Client securely from Streamlit Secrets vault
ai_client = None
if "GEMINI_API_KEY" in st.secrets:
    try:
        ai_client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    except Exception as e:
        st.error(f"Failed to initialize Gemini Client: {e}")

# Custom Visual Styling
st.markdown("""
    <style>
    .main-title {
        font-family: 'Times New Roman', Times, serif;
        color: #00F0FF;
        text-align: center;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .sub-title {
        font-family: 'Times New Roman', Times, serif;
        color: #aaaaaa;
        text-align: center;
        font-style: italic;
        margin-bottom: 25px;
    }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='main-title'>✒️ Nischal Citation</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Official OSCOLA 4th Edition Reference Suite</p>", unsafe_allow_html=True)

st.markdown("### 1. Select Source Category")
mode = st.radio(
    "Choose what you want to cite:",
    [
        "Book", 
        "Classic Case (AIR/ITR/AC)", 
        "Online Case (SCC OnLine)", 
        "Journal Article", 
        "Website Link", 
        "Statute / Act",
        "📂 AI PDF Reader (Automated SCC & Manupatra)"
    ],
    horizontal=False
)

st.markdown("---")

output_str = ""
pinpoint = ""

# --- MANUAL ENGINE OPTIONS ---

if mode == "Book":
    st.markdown("### 2. Enter Source Details")
    title = st.text_input("📚 Book Title")
    author = st.text_input("👤 Author(s)")
    col1, col2, col3 = st.columns(3)
    with col1: year = st.text_input("📅 Year")
    with col2: edition = st.text_input("🔢 Edition (e.g., 3rd)")
    with col3: publisher = st.text_input("🏢 Publisher")

    if author and title:
        # Strict OSCOLA casing preservation from direct inputs
        edn_str = f"{edition.replace('edn','').strip()} edn, " if edition else ""
        output_str = f"{author.strip()}, *{title.strip()}* ({edn_str}{publisher.strip()} {year.strip()})"

elif mode == "Classic Case (AIR/ITR/AC)":
    st.markdown("### 2. Enter Source Details")
    name = st.text_input("⚖️ Case Name")
    c1, c2, c3 = st.columns(3)
    with c1:
        year = st.text_input("📅 Reporter Year")
        bracket = st.selectbox("Bracket Style", ["round ()", "square []"])
    with c2:
        volume = st.text_input("🔢 Volume Number")
        report = st.text_input("🔤 Report Abbreviation (e.g., App Cas, AIR)")
    with c3:
        page = st.text_input("📄 Starting Page")
        court = st.text_input("🏛️ Court Suffix")

    if name and year and report and page:
        b_open, b_close = ("(", ")") if "round" in bracket else ("[", "]")
        vol_str = f" {volume.strip()}" if volume else ""
        court_str = f" ({court.strip()})" if court else ""
        output_str = f"*{name.strip()}* {b_open}{year.strip()}{b_close}{vol_str} {report.strip()} {page.strip()}{court_str}"

elif mode == "Online Case (SCC OnLine)":
    st.markdown("### 2. Enter Source Details")
    name = st.text_input("⚖️ Case Name")
    c1, c2, c3 = st.columns([1, 1.5, 1.5])
    with c1: year = st.text_input("📅 Database Year")
    with c2:
        platform = st.text_input("💻 Platform", value="SCC OnLine")
        court = st.text_input("🏛️ Court Suffix")
    with c3: case_num = st.text_input("🔢 Unique Electronic No.")

    if name and year and case_num:
        court_str = f" ({court.strip()})" if court else ""
        output_str = f"*{name.strip()}* {year.strip()} {platform.strip()} {case_num.strip()}{court_str}"

elif mode == "Journal Article":
    st.markdown("### 2. Enter Source Details")
    title = st.text_input("📰 Article Title")
    author = st.text_input("👤 Author(s)")
    c1, c2, c3, c4 = st.columns(4)
    with c1: year = st.text_input("📅 Year")
    with c2: vol = st.text_input("Volume")
    with c3: issue = st.text_input("Issue")
    with c4: first_page = st.text_input("First Page")
    journal = st.text_input("🔤 Journal Abbreviation / Name")

    if author and title and journal:
        vol_issue = f" {vol.strip()}" if vol else ""
        if issue: vol_issue += f"({issue.strip()})"
        output_str = f"{author.strip()}, '{title.strip()}' ({year.strip()}){vol_issue} *{journal.strip()}* {first_page.strip()}"

elif mode == "Website Link":
    st.markdown("### 2. Enter Source Details")
    url = st.text_input("🔗 Paste URL Link")
    
    if "w_title" not in st.session_state: st.session_state.w_title = ""
    if "w_site" not in st.session_state: st.session_state.w_site = ""
    if "w_date" not in st.session_state: st.session_state.w_date = ""

    if st.button("⚡ Auto-Fetch Details From Link"):
        if url:
            if not url.startswith("http://") and not url.startswith("https://"): url = "https://" + url
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                response = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                t = soup.title.string.strip() if soup.title else "Webpage"
                st.session_state.w_title = t.split(" - ")[0] if " - " in t else t
                st.session_state.w_site = urlparse(url).netloc.replace("www.", "").split(".")[0].capitalize()
                st.session_state.w_date = datetime.now().strftime("%d %B %Y")
            except Exception as e: st.error(f"Auto-fetch failed: {str(e)}")

    web_author = st.text_input("👤 Author (Leave blank if unknown)")
    web_title = st.text_input("📋 Title of Blog Post / Page", value=st.session_state.w_title)
    web_site = st.text_input("🌐 Blog / Website Name", value=st.session_state.w_site)
    web_access = st.text_input("📅 Date Accessed", value=st.session_state.w_date)

    if web_title and url:
        c_auth = web_author.strip() + ", " if web_author else ""
        output_str = f"{c_auth}'{web_title.strip()}' ({web_site.strip()}, {web_access.strip()}) <{url.strip()}> accessed {web_access.strip()}"

elif mode == "Statute / Act":
    st.markdown("### 2. Enter Source Details")
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1: title = st.text_input("📜 Short Title of Act")
    with col_s2: year = st.text_input("📅 Year")

    if title and year:
        output_str = f"{title.strip()} {year.strip()}"

# --- INTELLIGENT AI PDF ENGINE ---

elif mode == "📂 AI PDF Reader (Automated SCC & Manupatra)":
    st.markdown("### 2. Upload Judgment PDF (SCC / Manupatra / Classic)")
    uploaded_pdf = st.file_uploader("Drop any legal judgment file here", type=["pdf"])
    
    if uploaded_pdf:
        if not ai_client:
            st.error("Gemini API key is missing. Please add GEMINI_API_KEY to your Streamlit secrets vault.")
        else:
            with st.spinner("AI is analyzing document structural layers and generating OSCOLA layout..."):
                try:
                    reader = PdfReader(uploaded_pdf)
                    doc_content = ""
                    for i in range(min(4, len(reader.pages))):
                        doc_content += reader.pages[i].extract_text() or ""
                    
                    ai_prompt = f"""
                    You are an expert legal archivist. Analyze the following legal text extracted from a judgment document and format it strictly as a single, COMPLETE OSCOLA 4th Edition footnote citation.

                    CRITICAL CONSTRAINT: You MUST output the absolute full citation string, including the case name, year, reporter abbreviation, volume, and starting page number. If the provided text layout snippet does not explicitly list the citation numeric attributes but you recognize the benchmark case, rely on your internal legal knowledge base to supply the missing official citation items (e.g., if you recognize 'Umashankar Agrawal v Daulatram Sahu', automatically append 'AIR 2011 Chhatisgarh 72').

                    Follow these strict formatting constraints based on the OSCOLA 4th Edition guide:
                    1. Use AS LITTLE PUNCTUATION AS POSSIBLE. Do not use periods inside acronyms, titles, or suffixes (e.g., use 'v' instead of 'v.', use 'Ors' instead of 'Ors.', use 'SCC' in all caps, use 'SC' in all caps, use 'AIR' in all caps).
                    2. Standardize case party splits to use a lowercase 'v'.
                    3. Retain complete multi-party details when they are officially present in the text structure (e.g., 'and Anr', 'and Ors', '(since deceased) and Sant Din').
                    4. Prioritize clean publication citations. For instance:
                       - If it's a Supreme Court case matching SCC criteria, layout format should follow: Case Name (Year) Vol SCC Page (SC)
                       - If it's a classic case reporter like AIR, follow: Case Name AIR Year SC Page or Case Name AIR Year Court Page
                       - If it's an online or electronic signature database like Manupatra, follow: Case Name [Year] MANU/Court/DocNumber
                    5. Ensure proper title-casing capitalizations for all company, party, publisher, and court names (e.g., 'Isaac Cooke & Sons', 'Penguin Books'). Space abbreviations out cleanly if they are running together (e.g., 'Guj HC' instead of 'GujHC').

                    Here is the text layer to process:
                    ---
                    Filename: {uploaded_pdf.name}
                    Text content snippet:
                    {doc_content}
                    ---

                    Respond ONLY with the final complete formatted citation string. Do not include markdown blocks, introductory pleasantries, or additional descriptions. Preserve exact legal acronym capitalization (e.g. SCC, AIR, SC, MANU).
                    """
                    
                    response = ai_client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=ai_prompt,
                    )
                    
                    raw_output = response.text.strip()
                    output_str = raw_output.replace('`', '').replace('*', '').strip()
                    
                    st.success("AI extraction completed successfully!")
                except Exception as e:
                    st.error(f"AI engine error: {e}")

# --- SECTION 3: PINPOINT SYSTEM ---
st.markdown("### 3. Pinpoint / Jump Numbers (Optional)")
col_p1, col_p2 = st.columns(2)
with col_p1: page_num = st.text_input("Pinpoint Page Number", key="web_p")
with col_p2: para_num = st.text_input("Pinpoint Paragraph Number", key="web_pa")

if mode == "Statute / Act":
    if page_num: pinpoint += f" s {page_num.strip()}"
    if para_num: pinpoint += f" para {para_num.strip()}"
else:
    if page_num: pinpoint += f" {page_num.strip()}"
    if para_num: pinpoint += f" [{para_num.strip()}]"

# --- SECTION 4: OUTPUT DISPLAY ---
st.markdown("---")
st.markdown("### 4. Formatted OSCOLA Output Preview")

if output_str:
    final_citation = output_str + pinpoint
    clean_citation = " ".join(final_citation.split()).strip()
    st.info(clean_citation)
else:
    st.caption("Awaiting data inputs or file uploading sequence above...")
