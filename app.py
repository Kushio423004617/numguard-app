import streamlit as st
import phonenumbers
from phonenumbers import geocoder, carrier, timezone
import folium
from streamlit_folium import st_folium
from fpdf import FPDF
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="NumGuard // Phone Intelligence", 
    page_icon="🛡️", 
    layout="wide"
)

# Professional Cyber Security / SOC Aesthetic CSS + Hiding Streamlit Default Menu & Footer
st.markdown("""
    <style>
    /* Itago ang Streamlit Default Menu (hamburger) at Footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    .stApp {
        background-color: #0b0f19;
        color: #e2e8f0;
        font-family: 'Share Tech Mono', monospace, sans-serif;
    }
    section[data-testid="stSidebar"] {
        background-color: #07090e;
        border-right: 1px solid #1e293b;
    }
    .app-title {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(45deg, #38bdf8, #818cf8, #c084fc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
        animation: fadeIn 0.8s ease-in-out;
    }
    .app-subtitle {
        color: #64748b;
        font-size: 0.95rem;
        animation: fadeIn 1s ease-in-out;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes pulseAlert {
        0% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4); }
        70% { box-shadow: 0 0 0 10px rgba(239, 68, 68, 0); }
        100% { box-shadow: 0 0 0 0 rgba(239, 68, 68, 0); }
    }
    .badge-high-risk {
        background-color: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        color: #ef4444;
        padding: 14px 18px;
        border-radius: 8px;
        font-size: 0.95rem;
        animation: pulseAlert 2s infinite;
    }
    .badge-secure {
        background-color: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        color: #10b981;
        padding: 14px 18px;
        border-radius: 8px;
        font-size: 0.95rem;
    }
    .stTextInput input, .stTextArea textarea {
        background-color: #0f172a !important;
        color: #38bdf8 !important;
        border: 1px solid #1e293b !important;
        border-radius: 6px !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #0284c7, #0369a1) !important;
        color: #ffffff !important;
        font-weight: 700;
        border: none;
        border-radius: 6px;
        letter-spacing: 0.5px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(2, 132, 199, 0.4);
    }
    div[data-testid="stMetric"] {
        background-color: #0f172a;
        border: 1px solid #1e293b;
        padding: 18px;
        border-radius: 8px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        transform: translateY(-3px);
    }
    div[data-testid="stMetric"] label {
        color: #64748b !important;
        font-size: 0.8rem !important;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
        font-size: 1.3rem !important;
    }
    @media (max-width: 768px) {
        .app-title { font-size: 1.5rem; }
    }
    </style>
""", unsafe_allow_html=True)

# Helper Class para mag-generate ng PDF Report
class PDFReport(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 16)
        self.set_text_color(2, 132, 199)
        self.cell(0, 10, "NUMGUARD // THREAT INTELLIGENCE REPORT", 0, 1, "C")
        self.set_font("helvetica", "I", 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 5, "Official OSINT & Scam Verification Summary", 0, 1, "C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Generated securely via NumGuard Platform - Page {self.page_no()}", 0, 0, "C")

def generate_pdf_report(data):
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Metadata Section
    pdf.set_font("helvetica", "B", 12)
    pdf.set_text_color(30, 41, 59)
    pdf.cell(0, 8, "1. TARGET METADATA SUMMARY", 0, 1)
    
    pdf.set_font("helvetica", "", 10)
    pdf.set_text_color(50, 50, 50)
    
    fields = [
        ("Target Number:", data["full_number"]),
        ("Scan Timestamp:", data["timestamp"]),
        ("Region / Country:", data["country_desc"] if data["country_desc"] else "Unknown"),
        ("Network Carrier:", data["carrier_name"] if data["carrier_name"] else "Unknown"),
        ("Line Classification:", data["num_type_str"]),
        ("VoIP / High Risk Status:", "YES (Potential Virtual/Spoof Asset)" if data["is_voip"] else "NO (Standard Carrier Infrastructure)")
    ]
    
    for label, val in fields:
        pdf.set_font("helvetica", "B", 10)
        pdf.cell(50, 7, label, 0, 0)
        pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 7, str(val), 0, 1)
        
    pdf.ln(5)
    pdf.set_font("helvetica", "B", 12)
    pdf.cell(0, 8, "2. SECURITY ADVISORY & RECOMMENDATIONS", 0, 1)
    
    pdf.set_font("helvetica", "", 10)
    advisory_text = (
        "This report is automatically generated for threat analysis and digital verification. "
        "If this target is associated with cyber extortion, fake legal warrants, or financial fraud, "
        "do not send any funds or personal information. Retain screenshots and file a formal complaint "
        "to the PNP Anti-Cybercrime Group (PNP-ACG) or NBI Cybercrime Division."
    )
    pdf.multi_cell(0, 6, advisory_text)
    
    return pdf.output()

if "scan_data" not in st.session_state:
    st.session_state.scan_data = None

# Sidebar Configuration
with st.sidebar:
    st.markdown("### ⚙️ Control Panel")
    st.markdown("---")
    country_choice = st.selectbox(
        "Default Country Prefix",
        [
            "Philippines (+63)",
            "United States (+1)",
            "United Kingdom (+44)",
            "Canada (+1)",
            "Australia (+61)",
            "Singapore (+65)",
            "Japan (+81)",
            "South Korea (+82)",
            "Manual Input (+)"
        ]
    )
    st.markdown("---")
    st.markdown("""
        <div style='color: #64748b; font-size: 0.85rem; line-height: 1.8;'>
        🛡️ Status: <span style='color: #10b981; font-weight: bold;'>Active</span><br>
        🔒 Security: <span style='color: #38bdf8; font-weight: bold;'>Optimized</span>
        </div>
    """, unsafe_allow_html=True)

# Header
st.markdown('<p class="app-title">📞 NumGuard // Phone Intelligence</p>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">Interactive phone number verification and threat message analysis system.</p>', unsafe_allow_html=True)
st.markdown("---")

prefix_map = {
    "Philippines (+63)": "+63",
    "United States (+1)": "+1",
    "United Kingdom (+44)": "+44",
    "Canada (+1)": "+1",
    "Australia (+61)": "+61",
    "Singapore (+65)": "+65",
    "Japan (+81)": "+81",
    "South Korea (+82)": "+82",
    "Manual Input (+)": ""
}
selected_prefix = prefix_map.get(country_choice, "")

# Main Tabs
tab1, tab2 = st.tabs(["📞 Phone Lookup", "🚨 Threat Message Analyzer"])

with tab1:
    col1, col2 = st.columns([3, 1])
    with col1:
        user_input = st.text_input("Target Phone Number", placeholder="Halimbawa: 9171234567")
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        scan_button = st.button("🔍 Scan Number", use_container_width=True)

    if scan_button:
        if not user_input:
            st.warning("Mangyaring maglagay ng numerong susuriin.")
        else:
            with st.spinner("Sinusuri ang metadata..."):
                try:
                    cleaned_input = user_input.strip()
                    if cleaned_input.startswith("0") and selected_prefix:
                        cleaned_input = cleaned_input[1:]
                    
                    full_number = selected_prefix + cleaned_input if not cleaned_input.startswith("+") else cleaned_input

                    parsed_number = phonenumbers.parse(full_number)
                    
                    if not phonenumbers.is_valid_number(parsed_number):
                        st.error(f"Hindi balido o mali ang format ng numerong '{full_number}'.")
                        st.session_state.scan_data = None
                    else:
                        country_desc = geocoder.description_for_number(parsed_number, "en")
                        carrier_name = carrier.name_for_number(parsed_number, "en")
                        timezones = timezone.time_zones_for_number(parsed_number)
                        number_type = phonenumbers.number_type(parsed_number)
                        
                        type_mapping = {
                            0: "Fixed Line", 1: "Mobile Cellular", 2: "Fixed/Mobile Hybrid",
                            3: "Toll Free", 4: "Premium Rate", 5: "Shared Cost",
                            6: "VoIP (Virtual / High Risk)", 7: "Personal", 8: "Pager", 9: "UAN", 10: "Voicemail"
                        }
                        num_type_str = type_mapping.get(number_type, "Unknown")
                        is_voip = (number_type == 6)

                        coords = [14.5995, 120.9842]
                        zoom_level = 6

                        if "United States" in country_desc or full_number.startswith("+1"):
                            coords, zoom_level = [37.0902, -95.7129], 4
                        elif "United Kingdom" in country_desc or full_number.startswith("+44"):
                            coords, zoom_level = [55.3781, -3.4360], 5
                        elif "Australia" in country_desc or full_number.startswith("+61"):
                            coords, zoom_level = [-25.2744, 133.7751], 4
                        elif "Singapore" in country_desc or full_number.startswith("+65"):
                            coords, zoom_level = [1.3521, 103.8198], 11
                        elif "Japan" in country_desc or full_number.startswith("+81"):
                            coords, zoom_level = [36.2048, 138.2529], 5
                        elif "South Korea" in country_desc or full_number.startswith("+82"):
                            coords, zoom_level = [35.9077, 127.7669], 7

                        st.session_state.scan_data = {
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "full_number": full_number,
                            "country_desc": country_desc,
                            "carrier_name": carrier_name,
                            "timezones": list(timezones),
                            "num_type_str": num_type_str,
                            "is_voip": is_voip,
                            "coords": coords,
                            "zoom_level": zoom_level
                        }
                except Exception as ex:
                    st.error(f"May naganap na error: {ex}")

    if st.session_state.scan_data:
        data = st.session_state.scan_data
        
        st.markdown("---")
        
        if data["is_voip"]:
            st.markdown('<div class="badge-high-risk">⚠️ Mataas na Panganib: VoIP / Virtual number ang target. Kadalasang ginagamit ito sa mga online scam o digital spoofing.</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="badge-secure">✅ Ligtas/Normal: Nakarehistro ang numerong ito sa pampublikong telco infrastructure.</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric(label="Rehiyon / Bansa", value=data["country_desc"] if data["country_desc"] else "Hindi Tukoy")
        with m2:
            st.metric(label="Network Carrier", value=data["carrier_name"] if data["carrier_name"] else "Hindi Tukoy")
        with m3:
            st.metric(label="Uri ng Linya", value=data["num_type_str"])

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 🗺️ Mapa ng Rehiyon")
        
        current_zoom = 12 if data["coords"] == [14.5995, 120.9842] else data["zoom_level"]
        
        m = folium.Map(location=data["coords"], zoom_start=current_zoom)
        folium.Marker(
            data["coords"],
            popup=f"<b>Target:</b> {data['full_number']}<br><b>Carrier:</b> {data['carrier_name']}",
            tooltip="Lokasyon ng Rehiyon",
            icon=folium.Icon(color="red" if data["is_voip"] else "blue", icon="shield")
        ).add_to(m)

        st_folium(m, width="100%", height=450)

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### 📥 I-download ang PDF Ulat")
        
        pdf_data = generate_pdf_report(data)
        st.download_button(
            label="📥 I-download ang PDF Threat Report",
            data=bytes(pdf_data),
            file_name=f"threat_report_{data['full_number'].replace('+', '')}.pdf",
            mime="application/pdf"
        )

with tab2:
    st.markdown("### 🚨 Pagsusuri ng Banta o Text Message")
    st.markdown("<p style='color: #64748b; font-size: 0.9rem;'>I-paste dito ang mensahe ng scammer para suriin kung ito ay pekeng warrant o extortion attempt.</p>", unsafe_allow_html=True)
    
    threat_text_input = st.text_area("Nilalaman ng Mensahe", placeholder="Halimbawa: 'May warrant of arrest ka na dahil sa hindi mo pagbayad...'")
    
    if st.button("🔎 Suriin ang Mensahe", use_container_width=False):
        if not threat_text_input:
            st.warning("Walang tekstong nailagay para suriin.")
        else:
            text_lower = threat_text_input.lower()
            red_flags = []
            
            if any(w in text_lower for w in ["warrant", "arrest", "hulihin", "pulis", "nbi", "korte", "subpoena"]):
                red_flags.append("Pekeng Pagbabanta ng Kaso o Pag-aresto")
            if any(w in text_lower for w in ["bayad", "pera", "gcash", "maya", "transfer", "multa"]):
                red_flags.append("Pamimilit na Magpadala ng Pera")
            if any(w in text_lower for w in ["kaagad", "agad", "emergency", "bilisan", "oras"]):
                red_flags.append("Pagmamadali para Magdulot ng Takot")

            st.markdown("---")
            if red_flags:
                st.markdown('<div class="badge-high-risk">⚠️ Babala: Ang mensaheng ito ay naglalaman ng mga kilalang taktika ng online scam o cyber extortion. HINDI ITO OPISYAL NA UTOS NG KORTE.</div>', unsafe_allow_html=True)
                st.markdown("#### Mga Natukoy na Palatandaan:")
                for rf in red_flags:
                    st.markdown(f"- 🔴 {rf}")
                st.info("💡 **Tandaan:** Walang ahensya ng gobyerno ang nagpapadala ng warrant sa text. Huwag pansinin at huwag magpadala ng pera.")
            else:
                st.markdown('<div class="badge-secure">✅ Walang nakitang matinding banta ng extortion batay sa mga keyword, ngunit mag-ingat pa rin.</div>', unsafe_allow_html=True)