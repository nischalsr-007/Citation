import streamlit as st
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

# 1. Page Configuration
st.set_page_config(
    page_title="Nischal Citation | OSCOLA 4th Edition", 
    page_icon="✒️",
    layout="centered"
)

# 2. Crash Protection: Pre-initialize web variables in Streamlit memory
if "fetched_title" not in st.session_state:
    st.session_state.fetched_title = ""
if "fetched_site" not in st.session_state:
    st.session_state.fetched_site = ""
if "fetched_date" not in st.session_state:
    st.session_state.fetched_date = ""

# 3. Custom Visual Styling
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

# --- HEADER ---
st.markdown("<h1 class='main-title'>✒️ Nischal Citation</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-title'>Premium OSCOLA 4th Edition Citation Suite</p>", unsafe_allow_html=True)

# --- SECTION 1: SOURCE PICKER ---
st.markdown("### 1. Select Source Category")
mode = st.radio(
    "Choose what you want to cite:",
    ["Book", "Classic Case (AIR/ITR/AC)", "Online Case (SCC OnLine)", "Journal Article", "Website Link", "Statute / Act"],
    horizontal=True,
    label_visibility="collapsed"
)

st.markdown("---")

# --- SECTION 2: VARIABLE INITIALIZATION & DYNAMIC FIELDS ---
output_str = ""
pinpoint = ""

st.markdown("### 2. Enter Source Details")

if mode == "Book":
    title = st.text_input("📚 Book Title")
    author = st.text_input("👤 Author(s)")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        year = st.text_input("📅 Year")
    with col2:
        edition = st.text_input("🔢 Edition (e.g., 3rd)")
    with col3:
        publisher = st.text_input("🏢 Publisher")

    if author and title:
        edn = f" ({edition.replace('edn','').strip()} edn," if edition else " ("
        output_str = f"{author}, *{title}*{edn} {publisher} {year})"

elif mode == "Classic Case (AIR/ITR/AC)":
    name = st.text_input("⚖️ Case Name (e.g., Valappad Co-operative Stores v Srinivasa Iyer)")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        year = st.text_input("📅 Reporter Year")
        bracket = st.selectbox("Bracket Style", ["round ()", "square []"])
    with c2:
        volume = st.text_input("🔢 Volume Number")
        report = st.text_input("🔤 Report Abbreviation (e.g., AIR, ITR)")
    with c3:
        page = st.text_input("📄 Starting Page")
        court = st.text_input("🏛️ Court Suffix (e.g., SC, J&K)")

    if name and year and report and page:
        b_open, b_close = ("(", ")") if "round" in bracket else ("[", "]")
        vol_str = f" {volume}" if volume else ""
        court_str = f" ({court})" if court else ""
        output_str = f"*{name}* {b_open}{year}{b_close}{vol_str} {report} {page}{court_str}"

elif mode == "Online Case (SCC OnLine)":
    name = st.text_input("⚖️ Case Name (e.g., Suresh Kumar Joon v Mool Chand)")
    
    c1, c2, c3 = st.columns([1, 1.5, 1.5])
    with c1:
        year = st.text_input("📅 Database Year")
    with c2:
        platform = st.text_input("💻 Platform", value="SCC OnLine")
        court = st.text_input("🏛️ Court Suffix (e.g., Del HC)")
    with c3:
        case_num = st.text_input("🔢 Unique Electronic No. (e.g., Del 3602)")

    if name and year and case_num:
        court_str = f" ({court})" if court else ""
        output_str = f"*{name}* {year} {platform} {case_num}{court_str}"

elif mode == "Journal Article":
    title = st.text_input("📰 Article Title")
    author = st.text_input("👤 Author(s)")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        year = st.text_input("📅 Year")
    with c2:
        vol = st.text_input("Volume")
    with c3:
        issue = st.text_input("Issue")
    with c4:
        first_page = st.text_input("First Page")
    
    journal = st.text_input("🔤 Journal Abbreviation / Name")

    if author and title and journal:
        vol_issue = f" {vol}" if vol else ""
        if issue: vol_issue += f"({issue})"
        output_str = f"{author}, '{title}' ({year}){vol_issue} *{journal}* {first_page}"

elif mode == "Website Link":
    url = st.text_input("🔗 Paste URL Link")
    
    if st.button("⚡ Auto-Fetch Details From Link"):
        if url:
            if not url.startswith("http://") and not url.startswith("https://"):
                url = "https://" + url
            try:
                headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
                response = requests.get(url, headers=headers, timeout=5)
                soup = BeautifulSoup(response.text, "html.parser")
                
                fetched_title = soup.title.string.strip() if soup.title else "Webpage"
                if " - " in fetched_title: fetched_title = fetched_title.split(" - ")[0]
                if " | " in fetched_title: fetched_title = fetched_title.split(" | ")[0]
                
                parsed_domain = urlparse(url).netloc
                domain_parts = parsed_domain.replace("www.", "").split(".")
                fetched_site = domain_parts[0].capitalize() if domain_parts else "Webpage"
                fetched_date = datetime.now().strftime("%d %B %Y")
                
                st.session_state.fetched_title = fetched_title
                st.session_state.fetched_site = fetched_site
                st.session_state.fetched_date = fetched_date
                st.success("Details updated! Check the text inputs below.")
            except Exception as e:
                st.error(f"Auto-fetch failed: {str(e)}")
        else:
            st.warning("Please enter a URL first.")

    web_author = st.text_input("👤 Author (Leave blank if unknown)")
    web_title = st.text_input("📋 Webpage Title", value=st.session_state.fetched_title)
    web_site = st.text_input("🌐 Website/Platform Name", value=st.session_state.fetched_site)
    web_access = st.text_input("📅 Date Accessed", value=st.session_state.fetched_date)

    if web_title and url:
        auth_str = f"{web_author}, " if web_author else ""
        site_str = f" ({web_site})" if web_site else " (Webpage)"
        acc_str = f" accessed {web_access}" if web_access else ""
        output_str = f"{auth_str}'{web_title}'{site_str} <{url}>{acc_str}"

elif mode == "Statute / Act":
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        title = st.text_input("📜 Short Title of Act (e.g., Indian Contract Act)")
    with col_s2:
        year = st.text_input("📅 Year")

    if title and year:
        output_str = f"{title} {year}"

# --- SECTION 3: PINPOINT SYSTEM ---
st.markdown("### 3. Pinpoint / Jump Numbers (Optional)")
col_p1, col_p2 = st.columns(2)
with col_p1:
    page_num = st.text_input("Pinpoint Page Number", key="web_p")
with col_p2:
    para_num = st.text_input("Pinpoint Paragraph Number", key="web_pa")

if mode == "Statute / Act":
    if page_num: pinpoint += f" s {page_num}"
    if para_num: pinpoint += f" para {para_num}"
else:
    if page_num: pinpoint += f" {page_num}"
    if para_num: pinpoint += f" [{para_num}]"

# --- SECTION 4: OUTPUT DISPLAY ---
st.markdown("---")
st.markdown("### 4. Formatted OSCOLA Output Preview")

if output_str:
    final_citation = output_str + pinpoint
    clean_citation = " ".join(final_citation.split())
    st.info(clean_citation)
    st.caption("💡 **Tip:** Highlight the text box above to copy your citation straight into Word!")
else:
    st.caption("Awaiting entries... Populate the mandatory fields above to see your citation.")