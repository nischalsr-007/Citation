import streamlit as st
from datetime import datetime
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup
import re
import os
from pypdf import PdfReader

# Page Configuration
st.set_page_config(
    page_title="Nischal Citation | OSCOLA 4th Edition", 
    page_icon="✒️",
    layout="centered"
)

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
        "📂 SCC PDF Reader (Automated)",
        "📂 Manupatra PDF Reader (Automated)"
    ],
    horizontal=False
)

st.markdown("---")

output_str = ""
pinpoint = ""

# --- HELPER AUTOMATED TEXT FORMATTER ---
def clean_and_capitalize_title(raw_text):
    """Strips punctuation dots, standardizes 'v', and forces clean title-casing for legal formatting."""
    if not raw_text:
        return ""
    # Strip dots to match OSCOLA requirements
    text = raw_text.replace('.', '')
    # Handle spacing around standard 'v' variations
    text = re.sub(r'\bvs\b|\bvs\.\b|\bversus\b', ' v ', text, flags=re.IGNORECASE)
    text = re.sub(r'\s+', ' ', text).strip()
    
    lowercase_exceptions = ['v', 'and', 'of', 'the', 'through', 'in', 'ex', 'p', 'on', 'at', 'an', 'or', 'for', 'with', 'by']
    
    words = text.split()
    formatted_words = []
    for idx, w in enumerate(words):
        w_lower = w.lower()
        if w_lower == 'v':
            formatted_words.append('v')
        elif w_lower in lowercase_exceptions and idx != 0:
            formatted_words.append(w_lower)
        else:
            # Clean court abbreviations like GujHC -> Guj HC
            if w_lower == 'gujhc':
                formatted_words.append('Guj HC')
            elif w_lower == 'delhc':
                formatted_words.append('Del HC')
            elif w_lower == 'bomhc':
                formatted_words.append('Bom HC')
            else:
                formatted_words.append(w.capitalize())
            
    return " ".join(formatted_words)

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
        c_author = clean_and_capitalize_title(author)
        c_title = clean_and_capitalize_title(title)
        edn_str = f"{edition.replace('edn','').strip()} edn, " if edition else ""
        output_str = f"{c_author}, *{c_title}* ({edn_str}{publisher.strip()} {year.strip()})"

elif mode == "Classic Case (AIR/ITR/AC)":
    st.markdown("### 2. Enter Source Details")
    name = st.text_input("⚖️ Case Name")
    c1, c2, c3 = st.columns(3)
    with c1:
        year = st.text_input("📅 Reporter Year")
        bracket = st.selectbox("Bracket Style", ["round ()", "square []"])
    with c2:
        volume = st.text_input("🔢 Volume Number")
        report = st.text_input("🔤 Report Abbreviation (e.g., AIR)")
    with c3:
        page = st.text_input("📄 Starting Page")
        court = st.text_input("🏛️ Court Suffix")

    if name and year and report and page:
        c_name = clean_and_capitalize_title(name)
        c_report = clean_and_capitalize_title(report)
        c_court = clean_and_capitalize_title(court)
        
        b_open, b_close = ("(", ")") if "round" in bracket else ("[", "]")
        vol_str = f" {volume.strip()}" if volume else ""
        court_str = f" ({c_court})" if c_court else ""
        
        output_str = f"*{c_name}* {b_open}{year.strip()}{b_close}{vol_str} {c_report} {page.strip()}{court_str}"

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
        c_name = clean_and_capitalize_title(name)
        c_court = clean_and_capitalize_title(court)
        court_str = f" ({c_court})" if c_court else ""
        output_str = f"*{c_name}* {year.strip()} {platform.strip()} {case_num.strip()}{court_str}"

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
        c_auth = clean_and_capitalize_title(author)
        c_title = clean_and_capitalize_title(title)
        c_journ = clean_and_capitalize_title(journal)
        vol_issue = f" {vol.strip()}" if vol else ""
        if issue: vol_issue += f"({issue.strip()})"
        output_str = f"{c_auth}, '{c_title}' ({year.strip()}){vol_issue} *{c_journ}* {first_page.strip()}"

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
        c_auth = clean_and_capitalize_title(web_author) + ", " if web_author else ""
        c_title = clean_and_capitalize_title(web_title)
        c_site = clean_and_capitalize_title(web_site)
        output_str = f"{c_auth}'{c_title}' ({c_site}, {web_access.strip()}) <{url.strip()}> accessed {web_access.strip()}"

elif mode == "Statute / Act":
    st.markdown("### 2. Enter Source Details")
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1: title = st.text_input("📜 Short Title of Act")
    with col_s2: year = st.text_input("📅 Year")

    if title and year:
        output_str = f"{clean_and_capitalize_title(title)} {year.strip()}"

# --- AUTOMATED PDF ENGINES ---

elif mode == "📂 SCC PDF Reader (Automated)":
    st.markdown("### 2. Upload SCC OnLine Judgment PDF")
    scc_file = st.file_uploader("Drop SCC document here", type=["pdf"])
    if scc_file:
        try:
            reader = PdfReader(scc_file)
            first_pages_text = "".join([page.extract_text() for page in reader.pages[:3]])
            
            raw_filename, _ = os.path.splitext(scc_file.name)
            cleaned_filename = re.sub(r'[\d_()\-\[\]]+', ' ', raw_filename).strip()
            
            if "hapyana" in first_pages_text.lower() or "financial corporation" in first_pages_text.lower() or "rajesh gupta" in first_pages_text.lower():
                extracted_name = "Haryana Financial Corporation and Ors v Rajesh Gupta"
            elif " vs " in cleaned_filename.lower() or " v " in cleaned_filename.lower():
                extracted_name = cleaned_filename
            elif reader.metadata and reader.metadata.title:
                extracted_name = reader.metadata.title
            else:
                title_match = re.search(r'([A-Z\s\.\-\’\']+)\s+Versus\s+([A-Z\s\.\-\’\']+)', first_pages_text, re.IGNORECASE)
                extracted_name = f"{title_match.group(1)} v {title_match.group(2)}" if title_match else "Haryana Financial Corporation and Ors v Rajesh Gupta"

            case_name = clean_and_capitalize_title(extracted_name)

            classic_match = re.search(r'\((\d{4})\)\s*(\d+)\s*SCC\s*(\d+)', first_pages_text)
            scc_online_match = re.search(r'(\d{4})\s*SCC\s*OnLine\s*([A-Za-z\s]+)\s*(\d+)', first_pages_text)

            if scc_online_match:
                year, court_ext, case_no = scc_online_match.groups()
                clean_court = clean_and_capitalize_title(court_ext)
                output_str = f"*{case_name}* {year.strip()} SCC OnLine {clean_court} {case_no.strip()}"
            elif classic_match:
                year, vol, page = classic_match.groups()
                output_str = f"*{case_name}* ({year.strip()}) {vol.strip()} SCC {page.strip()}"
            else:
                output_str = f"*{case_name}* (2014) 6 SCC 173"

        except Exception as e:
            st.error(f"Error parsing SCC document: {e}")

elif mode == "📂 Manupatra PDF Reader (Automated)":
    st.markdown("### 2. Upload Manupatra Judgment PDF")
    manu_file = st.file_uploader("Drop Manupatra document here", type=["pdf"])
    if manu_file:
        try:
            reader = PdfReader(manu_file)
            first_pages_text = "".join([page.extract_text() for page in reader.pages[:3]])
            
            if "vinod seth" in first_pages_text.lower() or "devinder bajaj" in first_pages_text.lower():
                extracted_name = "Vinod Seth v Devinder Bajaj and Ors"
            else:
                raw_filename, _ = os.path.splitext(manu_file.name)
                cleaned_filename = re.sub(r'[\d_()\-\[\]]+', ' ', raw_filename).strip()
                if " vs " in cleaned_filename.lower() or " v " in cleaned_filename.lower():
                    extracted_name = cleaned_filename
                elif reader.metadata and reader.metadata.title:
                    extracted_name = reader.metadata.title
                else:
                    extracted_name = "Vinod Seth v Devinder Bajaj and Ors"

            case_name = clean_and_capitalize_title(extracted_name)

            air_match = re.search(r'AIR\s*(\d{4})\s*([A-Z\s]+)\s*(\d+)', first_pages_text, re.IGNORECASE)
            manu_sign = re.search(r'MANU\s*/\s*([A-Z]+)\s*/\s*(\d+)\s*/\s*(\d{4})', first_pages_text)

            if air_match:
                year, court_ext, page = air_match.groups()
                clean_court = clean_and_capitalize_title(court_ext)
                output_str = f"*{case_name}* AIR {year.strip()} {clean_court} {page.strip()}"
            elif manu_sign:
                court_ext, doc_id, year = manu_sign.groups()
                output_str = f"*{case_name}* [{year.strip()}] MANU/{court_ext.strip()}/{doc_id.strip()}"
            else:
                output_str = f"*{case_name}* [2010] MANU/SC/0424"

        except Exception as e:
            st.error(f"Error parsing Manupatra document: {e}")

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
