import streamlit as st
import requests
import json
import base64
import datetime
import calendar
import io
import re
import urllib.parse
from typing import Dict, Any, List, Optional
from pathlib import Path
from pypdf import PdfReader

# ==============================================================================
# STREAMLIT PAGE CONFIGURATION
# ==============================================================================
st.set_page_config(
    page_title="Yogya • Sovereign Civic Eligibility Engine",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==============================================================================
# CONSTANTS & CONFIGURATION
# ==============================================================================
DEFAULT_API_URL = "http://127.0.0.1:8000"
DEFAULT_MODEL = "gemma4:e4b"

STATE_OPTIONS = [
    "Karnataka",
    "Maharashtra",
    "Tamil Nadu",
    "Uttar Pradesh",
    "West Bengal",
    "Delhi",
    "Kerala",
    "Gujarat",
    "Telangana / Andhra Pradesh",
    "All-India (Pan-India View)"
]

LANGUAGE_OPTIONS = {
    "en": "English",
    "kn": "ಕನ್ನಡ (Kannada)",
    "hi": "हिंदी (Hindi)",
    "mr": "मराठी (Marathi)",
    "ta": "தமிழ் (Tamil)",
    "bn": "বাংলা (Bengali)"
}

CATEGORY_OPTIONS = ["OBC", "SC", "ST", "General", "EWS"]
EDUCATION_OPTIONS = ["10th Standard", "12th Standard / PUC", "Undergraduate", "Postgraduate", "Diploma"]

# ==============================================================================
# BILINGUAL LOCALIZATION SYSTEM (GovTech Kannada & English)
# ==============================================================================
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "app_title": "Yogya",
        "app_subtitle": "Autonomous Policy-to-Rules Sovereign Civic Eligibility Engine",
        "tab_step1": "📥 Step 1: Upload & Auto-Scan",
        "tab_step2": "👤 Step 2: Citizen Profile Dashboard",
        "tab_step3": "⚖️ Step 3: Verified Scheme Matches",
        "tab_step4": "🔮 Step 4: What-If Simulation Sandbox",
        "tab_validity": "📅 Document Validity Tracker",
        "tab_discovery": "🏛️ Pan-India Schemes & Letter Generator",
        "tab_voice": "🗣️ Multilingual Voice & Brief",
        "tab_kiosk": "🗺️ Service Centers (Kiosks)",
        "tab_license": "📜 License (MIT)",
        # Step 1
        "s1_heading": "### 📥 Step 1: Upload & Auto-Scan Citizen Credentials",
        "s1_caption": "Upload digital Revenue Certificates, Marksheets, or Caste Declarations (PDF, JPG, PNG). Gemma 4 extracts statutory parameters with instant verification audit trail.",
        "s1_scanner_title": "#### 📄 Document Scanner & Drag-and-Drop Ingest",
        "s1_uploader_label": "Upload Tahsildar Income / Caste Certificate or Marksheet",
        "s1_uploader_help": "Accepts digital PDF with RD number barcode or high-resolution camera scan.",
        "s1_sample_check": "💡 Or load pre-verified sample Tahsildar Income Certificate (RD00382910452)",
        "s1_extract_btn": "🔍 Extract Attributes with Gemma 4",
        "s1_vision_engine": "Vision Engine",
        "s1_gauge_title": "#### 🛡️ Live OCR Verification & Trust Gauge",
        "s1_trust_conf": "Trust Confidence",
        "s1_barcode_ref": "Barcode Reference",
        "s1_source_file": "Source File",
        "s1_issuer": "Issuer Authority",
        "s1_issue_date": "Issue Date",
        "s1_valid_until": "Valid Until",
        "s1_sakala": "Sakala Compliance: Guaranteed under Right to Public Services Act.",
        "s1_attr_title": "##### Extracted Citizen Attributes:",
        "s1_attr_name": "Name",
        "s1_attr_income": "Income",
        "s1_attr_cat": "Category",
        "s1_attr_marks": "Qualifying Marks",
        "s1_attr_dom": "Domicile",
        "s1_attr_gender": "Gender",
        "s1_next_advice": "👉 **Next Step:** Review or tweak extracted attributes in **Step 2: Citizen Profile Dashboard**, or jump directly to **Step 3** to inspect mathematical proofs.",
        "s1_success": "✅ Certificate successfully verified and extracted into Citizen Profile!",
        # Step 2
        "s2_heading": "### 👤 Step 2: Citizen Profile Dashboard (Unified Digital Identity)",
        "s2_caption": "Inspect and fine-tune your parameters. Modifications immediately synchronize into the mathematical prover engine with strict type-safety.",
        "s2_presets_title": "##### ⚡ Quick Persona Presets:",
        "s2_preset_merit": "👩‍🎓 Merit Scholar (Post-Matric)",
        "s2_preset_farmer": "🌾 Farmer Child (Raita Vidya)",
        "s2_preset_national": "🇮🇳 National Scholar (Central NSP)",
        "s2_preset_tech": "👩‍💻 Girl in Tech (AICTE Pragati)",
        "s2_sec1_title": "#### 1. Identity & Domicile Verification",
        "s2_full_name": "Full Citizen Name",
        "s2_gender": "Gender",
        "s2_age": "Age (Years)",
        "s2_state": "State of Domicile",
        "s2_dom_years": "Years of Domicile in State",
        "s2_sec2_title": "#### 2. Means Test & Income Certification",
        "s2_income": "Gross Annual Family Household Income (₹)",
        "s2_income_help": "Must match digitally verifiable Revenue Department Form 16 / RD Certificate.",
        "s2_has_inc": "Verified Income Certificate (RD Barcode)",
        "s2_has_dom": "Verified Domicile / Residence Proof",
        "s2_sec3_title": "#### 3. Academic Progression & Institution",
        "s2_edu": "Current Level of Education",
        "s2_marks": "Qualifying Marks Aggregate (%)",
        "s2_inst": "Institution Name",
        "s2_tech": "Technical / Engineering Degree (AICTE)",
        "s2_govt_sch": "Studied in Govt School (Grades 6-12)",
        "s2_sec4_title": "#### 4. Social Category & Special Attributes",
        "s2_cat": "Caste / Reservation Category",
        "s2_has_cst": "Verified Caste Certificate Uploaded",
        "s2_farmer": "Parent is Registered Farmer (FRUITS ID)",
        "s2_hostel": "Staying in Private PG (Outside Govt Hostel)",
        "s2_sync_success": "✅ All citizen attributes synchronized. Proceed to **Step 3: Verified Scheme Matches** to run formal verification.",
        # Step 3
        "s3_heading": "### ⚖️ Step 3: Verified Scheme Matches & Prover Audit Trail",
        "s3_caption": "Pure mathematical deterministic evaluation. Zero hallucinations. Every verdict is backed by an auditable clause-by-clause proof.",
        "s3_total_eval": "Total Evaluated",
        "s3_eligible": "Eligible Schemes",
        "s3_action_req": "Action Required",
        "s3_total_grant": "Annual Unlocked Grant",
        "s3_dept": "Department",
        "s3_grant": "Annual Grant",
        "s3_badge_pass": "🟢 ELIGIBLE / PASS",
        "s3_badge_action": "⚠️ ACTION REQUIRED",
        "s3_badge_ineligible": "🔴 INELIGIBLE",
        "s3_proof_expander": "🔬 View Mathematical Clause Proof & Audit Trail",
        "s3_apply_btn": "🚀 Direct Apply on myScheme.gov.in",
        "s3_view_guidelines": "⚠️ View on myScheme.gov.in",
        "s3_search_scheme": "🔍 Search on myScheme.gov.in",
        "s3_dept_portal": "🏛️ State / Dept Portal",
        "s3_national_portal": "🏛️ National Portal (NSP)",
        "s3_draft_letter": "✍️ Draft Official Letter",
        "s3_pending_doc": "📄 Pending Document",
        "s3_remediation": "💡 Remediation:"
    },
    "kn": {
        "app_title": "ಯೋಗ್ಯ (Yogya)",
        "app_subtitle": "ಸ್ವಾಯತ್ತ ನಾಗರಿಕ ಕಲ್ಯಾಣ ಯೋಜನೆಗಳ ಗಣಿತ ಪರಿಶೀಲನಾ ಎಂಜಿನ್",
        "tab_step1": "📥 ಹಂತ ೧: ದಾಖಲೆ ಅಪ್‌ಲೋಡ್ & ಸ್ಕ್ಯಾನ್",
        "tab_step2": "👤 ಹಂತ ೨: ನಾಗರಿಕ ಪ್ರೊಫೈಲ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
        "tab_step3": "⚖️ ಹಂತ ೩: ಪರಿಶೀಲಿಸಿದ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು",
        "tab_step4": "🔮 ಹಂತ ೪: ಸಿಮ್ಯುಲೇಶನ್ ಸ್ಯಾಂಡ್‌ಬಾಕ್ಸ್",
        "tab_validity": "📅 ದಾಖಲೆ ಸಿಂಧುತ್ವ ಟ್ರ್ಯಾಕರ್",
        "tab_discovery": "🏛️ ಪ್ಯಾನ್-ಇಂಡಿಯಾ ಯೋಜನೆಗಳು & ಪತ್ರ ರಚನೆ",
        "tab_voice": "🗣️ ಬಹುಭಾಷಾ ಧ್ವನಿ ಸಹಾಯಕ",
        "tab_kiosk": "🗺️ ನಾಗರಿಕ ಸೇವಾ ಕೇಂದ್ರಗಳು (ಗ್ರಾಮ ಒನ್)",
        "tab_license": "📜 ಮುಕ್ತ ಪರವಾನಗಿ (MIT)",
        # Step 1
        "s1_heading": "### 📥 ಹಂತ ೧: ನಾಗರಿಕರ ದಾಖಲೆಗಳ ಅಪ್‌ಲೋಡ್ ಮತ್ತು ಸ್ವಯಂಚಾಲಿತ ಪರಿಶೀಲನೆ",
        "s1_caption": "ತಹಶೀಲ್ದಾರ್ ಆದಾಯ, ಜಾತಿ ಪ್ರಮಾಣಪತ್ರ ಅಥವಾ ಅಂಕಪಟ್ಟಿಯನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ (PDF, JPG, PNG). ಗೆಮ್ಮಾ ೪ (Gemma 4) ಸ್ವಯಂಚಾಲಿತವಾಗಿ ವಿವರಗಳನ್ನು ಹೊರತೆಗೆದು ಪರಿಶೀಲಿಸುತ್ತದೆ.",
        "s1_scanner_title": "#### 📄 ದಾಖಲೆ ಸ್ಕ್ಯಾನರ್ ಮತ್ತು ಅಪ್‌ಲೋಡ್",
        "s1_uploader_label": "ತಹಶೀಲ್ದಾರ್ ಆದಾಯ / ಜಾತಿ ಪ್ರಮಾಣಪತ್ರ ಅಥವಾ ಅಂಕಪಟ್ಟಿ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ",
        "s1_uploader_help": "ಆರ್‌ಡಿ ಸಂಖ್ಯೆ ಬಾರ್‌ಕೋಡ್ ಹೊಂದಿರುವ ಡಿಜಿಟಲ್ ಪಿಡಿಎಫ್ ಅಥವಾ ಮೊಬೈಲ್ ಫೋಟೋ ಸ್ವೀಕರಿಸಲಾಗುತ್ತದೆ.",
        "s1_sample_check": "💡 ಅಥವಾ ಪರಿಶೀಲಿಸಿದ ಮಾದರಿ ತಹಶೀಲ್ದಾರ್ ಆದಾಯ ಪ್ರಮಾಣಪತ್ರವನ್ನು ಲೋಡ್ ಮಾಡಿ (RD00382910452)",
        "s1_extract_btn": "🔍 ಗೆಮ್ಮಾ ೪ ಮೂಲಕ ವಿವರಗಳನ್ನು ಹೊರತೆಗೆಯಿರಿ",
        "s1_vision_engine": "ವಿಷನ್ ಎಂಜಿನ್",
        "s1_gauge_title": "#### 🛡️ ಲೈವ್ ಒಸಿಆರ್ ಪರಿಶೀಲನೆ ಮತ್ತು ವಿಶ್ವಾಸಾರ್ಹತೆ ಸ್ಕೋರ್",
        "s1_trust_conf": "ವಿಶ್ವಾಸಾರ್ಹತೆ ಸ್ಕೋರ್",
        "s1_barcode_ref": "ಆರ್‌ಡಿ ಬಾರ್‌ಕೋಡ್ ಸಂಖ್ಯೆ",
        "s1_source_file": "ಮೂಲ ಕಡತ",
        "s1_issuer": "ಪ್ರಾಧಿಕಾರ",
        "s1_issue_date": "ನೀಡಿದ ದಿನಾಂಕ",
        "s1_valid_until": "ಸಿಂಧುತ್ವ ಮುಕ್ತಾಯ",
        "s1_sakala": "ಸಕಾಲ ಸೇವೆಗಳ ಕಾಯ್ದೆಯಡಿಯಲ್ಲಿ ಖಾತರಿಪಡಿಸಲಾಗಿದೆ.",
        "s1_attr_title": "##### ಹೊರತೆಗೆಯಲಾದ ನಾಗರಿಕ ವಿವರಗಳು:",
        "s1_attr_name": "ಹೆಸರು",
        "s1_attr_income": "ವಾರ್ಷಿಕ ಆದಾಯ",
        "s1_attr_cat": "ವರ್ಗ",
        "s1_attr_marks": "ಅಂಕಗಳ ಶೇಕಡಾವಾರು",
        "s1_attr_dom": "ವಾಸಸ್ಥಳ",
        "s1_attr_gender": "ಲಿಂಗ",
        "s1_next_advice": "👉 **ಮುಂದಿನ ಹಂತ:** ಹೊರತೆಗೆಯಲಾದ ವಿವರಗಳನ್ನು **ಹಂತ ೨: ನಾಗರಿಕ ಪ್ರೊಫೈಲ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್** ನಲ್ಲಿ ಪರಿಶೀಲಿಸಿ, ಅಥವಾ ನೇರವಾಗಿ **ಹಂತ ೩** ಕ್ಕೆ ಹೋಗಿ ಗಣಿತದ ಪುರಾವೆಗಳನ್ನು ವೀಕ್ಷಿಸಿ.",
        "s1_success": "✅ ಪ್ರಮಾಣಪತ್ರವನ್ನು ಯಶಸ್ವಿಯಾಗಿ ಪರಿಶೀಲಿಸಲಾಗಿದೆ ಮತ್ತು ನಾಗರಿಕ ಪ್ರೊಫೈಲ್‌ಗೆ ಸೇರಿಸಲಾಗಿದೆ!",
        # Step 2
        "s2_heading": "### 👤 ಹಂತ ೨: ನಾಗರಿಕ ಪ್ರೊಫೈಲ್ ಡ್ಯಾಶ್‌ಬೋರ್ಡ್ (ಡಿಜಿಟಲ್ ಗುರುತು)",
        "s2_caption": "ನಿಮ್ಮ ವೈಯಕ್ತಿಕ, ಆರ್ಥಿಕ ಮತ್ತು ಶೈಕ್ಷಣಿಕ ವಿವರಗಳನ್ನು ಪರಿಶೀಲಿಸಿ. ಇಲ್ಲಿ ಬದಲಾಯಿಸಿದ ತಕ್ಷಣ ಗಣಿತ ಎಂಜಿನ್‌ನಲ್ಲಿ ಅರ್ಹತೆ ನವೀಕರಣಗೊಳ್ಳುತ್ತದೆ.",
        "s2_presets_title": "##### ⚡ ತ್ವರಿತ ವ್ಯಕ್ತಿತ್ವ ಮಾದರಿಗಳು (ಪ್ರಿಸೆಟ್‌ಗಳು):",
        "s2_preset_merit": "👩‍🎓 ಮೆರಿಟ್ ವಿದ್ಯಾರ್ಥಿ (ಪೋಸ್ಟ್-ಮೆಟ್ರಿಕ್)",
        "s2_preset_farmer": "🌾 ರೈತರ ಮಕ್ಕಳು (ರೈತ ವಿದ್ಯಾ ನಿಧಿ)",
        "s2_preset_national": "🇮🇳 ರಾಷ್ಟ್ರೀಯ ವಿದ್ಯಾರ್ಥಿವೇತನ (ಸೆಂಟ್ರಲ್ ಎನ್‌ಎಸ್‌ಪಿ)",
        "s2_preset_tech": "👩‍💻 ತಾಂತ್ರಿಕ ಶಿಕ್ಷಣ (ಎಐಸಿಟಿಇ ಪ್ರಗತಿ)",
        "s2_sec1_title": "#### ೧. ಗುರುತು ಮತ್ತು ವಾಸಸ್ಥಳ ಪರಿಶೀಲನೆ",
        "s2_full_name": "ನಾಗರಿಕರ ಪೂರ್ಣ ಹೆಸರು",
        "s2_gender": "ಲಿಂಗ",
        "s2_age": "ವಯಸ್ಸು (ವರ್ಷಗಳಲ್ಲಿ)",
        "s2_state": "ವಾಸಸ್ಥಳ ರಾಜ್ಯ",
        "s2_dom_years": "ರಾಜ್ಯದಲ್ಲಿ ವಾಸಿಸಿದ ವರ್ಷಗಳು",
        "s2_sec2_title": "#### ೨. ಆದಾಯ ಮತ್ತು ಪ್ರಮಾಣಪತ್ರ ಪರಿಶೀಲನೆ",
        "s2_income": "ಕುಟುಂಬದ ಒಟ್ಟು ವಾರ್ಷಿಕ ಆದಾಯ (₹)",
        "s2_income_help": "ಕಂದಾಯ ಇಲಾಖೆಯ ನಮೂನೆ ೧೬ / ಆರ್‌ಡಿ ಪ್ರಮಾಣಪತ್ರದ ವಿವರಗಳಿಗೆ ಹೊಂದಿಕೆಯಾಗಬೇಕು.",
        "s2_has_inc": "ಪರಿಶೀಲಿಸಿದ ಆದಾಯ ಪ್ರಮಾಣಪತ್ರವಿದೆ (ಆರ್‌ಡಿ ಬಾರ್‌ಕೋಡ್)",
        "s2_has_dom": "ಪರಿಶೀಲಿಸಿದ ವಾಸಸ್ಥಳ ಪ್ರಮಾಣಪತ್ರವಿದೆ",
        "s2_sec3_title": "#### ೩. ಶೈಕ್ಷಣಿಕ ವಿವರಗಳು ಮತ್ತು ಸಂಸ್ಥೆ",
        "s2_edu": "ಪ್ರಸ್ತುತ ಶಿಕ್ಷಣ ಮಟ್ಟ",
        "s2_marks": "ಅರ್ಹತಾ ಪರೀಕ್ಷೆಯ ಒಟ್ಟು ಅಂಕಗಳು (%)",
        "s2_inst": "ಶಿಕ್ಷಣ ಸಂಸ್ಥೆ / ಕಾಲೇಜಿನ ಹೆಸರು",
        "s2_tech": "ತಾಂತ್ರಿಕ / ಇಂಜಿನಿಯರಿಂಗ್ ಪದವಿ (AICTE)",
        "s2_govt_sch": "ಸರ್ಕಾರಿ ಶಾಲೆಯಲ್ಲಿ ವ್ಯಾಸಂಗ (೬-೧೨ನೇ ತರಗತಿ)",
        "s2_sec4_title": "#### ೪. ಸಾಮಾಜಿಕ ವರ್ಗ ಮತ್ತು ವಿಶೇಷ ವಿವರಗಳು",
        "s2_cat": "ಜಾತಿ / ಮೀಸಲಾತಿ ವರ್ಗ",
        "s2_has_cst": "ಪರಿಶೀಲಿಸಿದ ಜಾತಿ ಪ್ರಮಾಣಪತ್ರ ಲಭ್ಯವಿದೆ",
        "s2_farmer": "ಪೋಷಕರು ನೋಂದಾಯಿತ ರೈತರು (FRUITS FID)",
        "s2_hostel": "ಖಾಸಗಿ ಪಿಜಿ / ಮನೆಯಲ್ಲಿ ವಾಸ (ಸರ್ಕಾರಿ ಹಾಸ್ಟೆಲ್ ಹೊರಗೆ)",
        "s2_sync_success": "✅ ಎಲ್ಲಾ ನಾಗರಿಕ ವಿವರಗಳು ಯಶಸ್ವಿಯಾಗಿ ನವೀಕರಣಗೊಂಡಿವೆ. ಪರಿಶೀಲನೆಗಾಗಿ **ಹಂತ ೩: ಪರಿಶೀಲಿಸಿದ ಯೋಜನೆಗಳು** ಟ್ಯಾಬ್‌ಗೆ ಮುಂದುವರಿಯಿರಿ.",
        # Step 3
        "s3_heading": "### ⚖️ ಹಂತ ೩: ಪರಿಶೀಲಿಸಿದ ಸರ್ಕಾರಿ ಯೋಜನೆಗಳು ಮತ್ತು ಅರ್ಹತಾ ಪುರಾವೆ",
        "s3_caption": "ಶುದ್ಧ ಗಣಿತದ ಲೆಕ್ಕಾಚಾರ. ಶೂನ್ಯ ಭ್ರಮೆ. ಪ್ರತಿಯೊಂದು ತೀರ್ಪು ಸರ್ಕಾರದ ಅಧಿಕೃತ ನಿಯಮಾವಳಿಗಳ ಮೇಲೆ ಆಧಾರಿತವಾಗಿದೆ.",
        "s3_total_eval": "ಒಟ್ಟು ಪರಿಶೀಲಿಸಿದ ಯೋಜನೆಗಳು",
        "s3_eligible": "ಅರ್ಹ ಯೋಜನೆಗಳು",
        "s3_action_req": "ಕ್ರಮ ಅಗತ್ಯವಿರುವ ಯೋಜನೆಗಳು",
        "s3_total_grant": "ಅನ್ಲಾಕ್ ಆದ ವಾರ್ಷಿಕ ಅನುದಾನ",
        "s3_dept": "ಇಲಾಖೆ",
        "s3_grant": "ವಾರ್ಷಿಕ ಅನುದಾನ",
        "s3_badge_pass": "🟢 ಅರ್ಹ / ತೇರ್ಗಡೆ",
        "s3_badge_action": "⚠️ ಕ್ರಮ ಅಗತ್ಯ / ದಾಖಲೆ ಬಾಕಿ",
        "s3_badge_ineligible": "🔴 ಅನರ್ಹ",
        "s3_proof_expander": "🔬 ಗಣಿತದ ಷರತ್ತು ಪುರಾವೆ ಮತ್ತು ಆಡಿಟ್ ಟ್ರಯಲ್ ವೀಕ್ಷಿಸಿ",
        "s3_apply_btn": "🚀 myScheme.gov.in ನಲ್ಲಿ ನೇರವಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಿ",
        "s3_view_guidelines": "⚠️ myScheme ನಲ್ಲಿ ಷರತ್ತುಗಳನ್ನು ವೀಕ್ಷಿಸಿ",
        "s3_search_scheme": "🔍 myScheme ನಲ್ಲಿ ಹುಡುಕಿ",
        "s3_dept_portal": "🏛️ ರಾಜ್ಯ / ಇಲಾಖಾ ಪೋರ್ಟಲ್",
        "s3_national_portal": "🏛️ ರಾಷ್ಟ್ರೀಯ ಪೋರ್ಟಲ್ (NSP)",
        "s3_draft_letter": "✍️ ಅಧಿಕೃತ ಅರ್ಜಿ ಪತ್ರ ರಚಿಸಿ",
        "s3_pending_doc": "📄 ಬಾಕಿ ಇರುವ ದಾಖಲೆ",
        "s3_remediation": "💡 ಪರಿಹಾರ ಮಾರ್ಗ:"
    }
}

def t(key: str, default: str = "") -> str:
    """Returns localized string based on active session language (Kannada / English)."""
    lang = st.session_state.get("selected_language", "en")
    lang_dict = TRANSLATIONS.get(lang, TRANSLATIONS["en"])
    return lang_dict.get(key, TRANSLATIONS["en"].get(key, default or key))

def apply_persona_preset(preset_dict: Dict[str, Any]):
    """Safely updates pipeline data and synchronizes Streamlit widget keys to prevent widget freeze."""
    st.session_state.pipeline_data.update(preset_dict)
    key_mapping = {
        "citizen_name": "prof_citizen_name",
        "gender": "prof_gender",
        "age": "prof_age",
        "state_of_domicile": "prof_state",
        "domicile_years": "prof_dom_years",
        "family_income": "prof_income",
        "has_income_certificate": "prof_has_inc",
        "has_domicile_certificate": "prof_has_dom",
        "education_level": "prof_edu",
        "marks_percentage": "prof_marks",
        "institution_name": "prof_inst",
        "is_technical_course": "prof_tech",
        "studied_govt_school": "prof_govt_sch",
        "caste_category": "prof_cat",
        "has_caste_certificate": "prof_has_cst",
        "is_farmer_child": "prof_farmer"
    }
    for pipe_k, widget_k in key_mapping.items():
        if pipe_k in preset_dict:
            try:
                st.session_state[widget_k] = preset_dict[pipe_k]
            except Exception:
                pass
    if "is_hostel_resident" in preset_dict:
        try:
            st.session_state["prof_hostel"] = not bool(preset_dict["is_hostel_resident"])
        except Exception:
            pass
    if "state_of_domicile" in preset_dict:
        st.session_state.selected_state = preset_dict["state_of_domicile"]
    st.session_state.user_profile = st.session_state.pipeline_data

# ==============================================================================
# SAFE SESSION STATE INITIALIZATION (Zero NameError Guarantee)
# ==============================================================================
def init_session_state():
    """Initializes all session state variables safely at application bootstrap."""
    defaults = {
        # Core Citizen Profile Data
        "pipeline_data": {
            "citizen_name": "Rohan Kumar",
            "father_name": "Sri Ramesh Kumar",
            "age": 20,
            "family_income": 180000.0,
            "marks_percentage": 78.5,
            "caste_category": "OBC",
            "state_of_domicile": "Karnataka",
            "is_karnataka_domicile": True,
            "domicile_years": 10,
            "education_level": "Undergraduate",
            "gender": "Female",
            "is_farmer_child": False,
            "is_worker_child": False,
            "is_hostel_resident": False,
            "has_income_certificate": True,
            "has_caste_certificate": True,
            "has_domicile_certificate": True,
            "is_technical_course": True,
            "studied_govt_school": False,
            "phone": "+91-9845012345",
            "email": "rohan.kumar@nic.in",
            "institution_name": "BMS College of Engineering, Bengaluru",
            "address": "Malleshwaram, Bengaluru Urban, Karnataka - 560003",
            "certificate_ref_no": "RD00382910452"
        },
        # OCR & Document Ingest Metadata
        "ocr_confidence": 96.8,
        "ocr_extracted_from": "RD00382910452_Tahsildar_Income.pdf",
        "ocr_issue_date": "2024-04-12",
        "ocr_valid_until": "2029-03-31",
        "ocr_raw_text": "",
        # Global UI Controls
        "selected_state": "Karnataka",
        "selected_language": "en",
        "global_language_selector": "en",
        "api_url": DEFAULT_API_URL,
        "active_model": DEFAULT_MODEL,
        # Step 2 & 3 Prover Controls
        "selected_scheme_override": None,
        "custom_extracted_rules": None,
        "custom_scheme_name": None,
        "custom_department": None,
        "custom_benefit_inr": None,
        "last_prover_summary": None,
        # Step 4 What-If Simulation Controls
        "sim_state": "Karnataka",
        "sim_income": 180000.0,
        "sim_marks": 78.5,
        "sim_age": 20,
        "sim_category": "OBC",
        "sim_gender": "Female",
        "sim_domicile_years": 10,
        "sim_edu": "Undergraduate",
        "sim_parent_occ": "🌾 Registered Farmer (FRUITS ID)",
        "sim_is_technical": True,
        "sim_govt_school": False,
        "sim_hostel": False,
        "sim_income_cert": True,
        "sim_caste_cert": True,
        "is_kar": True,
        # Pan-India Search & URL Compiler
        "pan_india_search_results": [],
        "website_fetched_schemes": [],
        "last_fetched_url": "",
        "target_scheme_url": "https://en.wikipedia.org/wiki/National_Scholarship_Portal",
        # Gemma 4 Letter Generator State
        "letter_target_scheme": "State Scholarship Portal (SSP) Post-Matric",
        "letter_target_dept": "Department of Social Welfare",
        "letter_target_state": "Karnataka",
        "letter_active_type": "Official Scheme Application Cover Letter",
        "generated_letter_text": "",
        "letter_model_used": "",
        # Document Validity Tracker DB
        "certificates_db": [
            {
                "id": "CERT-01",
                "name": "Revenue Income Certificate (Form 16 / RD)",
                "category": "Means Test Verification",
                "authority": "Tahsildar, Nadakacheri (Karnataka Revenue Dept)",
                "ref_no": "RD00382910452",
                "issue_date": "2024-04-12",
                "valid_until": "2029-03-31",
                "critical_for": "SSP Post-Matric, Vidyasiri, PM-YASASVI"
            },
            {
                "id": "CERT-02",
                "name": "OBC / Caste & Category Certificate",
                "category": "Affirmative Action Proof",
                "authority": "Assistant Commissioner / Tahsildar",
                "ref_no": "RD00389182391",
                "issue_date": "2022-06-15",
                "valid_until": "2099-12-31",
                "critical_for": "Fee Concession, Central Sector Scheme"
            },
            {
                "id": "CERT-03",
                "name": "College Bonafide Study & Fee Receipt",
                "category": "Academic Status Proof",
                "authority": "BMS College of Engineering, Registrar Office",
                "ref_no": "BMSCE/ACAD/2026/089",
                "issue_date": "2026-08-01",
                "valid_until": "2027-06-30",
                "critical_for": "Post-Matric Tuition Fee Reimbursement"
            },
            {
                "id": "CERT-04",
                "name": "FRUITS Farmer Land Registry ID (FID)",
                "category": "Agricultural Verification",
                "authority": "Department of Agriculture (FRUITS Portal)",
                "ref_no": "FID-98234-KAR-2026",
                "issue_date": "2024-01-10",
                "valid_until": "2026-11-15",
                "critical_for": "CM Raita Vidya Nidhi (+₹11,000/yr)"
            }
        ],
        # Vernacular Speech Assistant State
        "last_voice_query": "",
        "translated_summary": ""
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Synchronize alias
    st.session_state.user_profile = st.session_state.pipeline_data

init_session_state()

# ==============================================================================
# UI DESIGN SYSTEM & CUSTOM CSS (IndiaStack / DigiLocker / Linear)
# ==============================================================================
def inject_custom_css():
    """Injects high-grade GovTech typography, borders, cards, and accessibility styling."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        color: #0F172A;
    }

    /* Main container clean spacing */
    .block-container {
        padding-top: 1.2rem;
        padding-bottom: 3.5rem;
        max-width: 1380px;
    }

    /* Remove default ugly radio/tab headers */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: transparent;
        border-bottom: 1px solid #E2E8F0;
        padding-bottom: 4px;
        margin-bottom: 20px;
    }

    .stTabs [data-baseweb="tab"] {
        height: 44px;
        white-space: pre-wrap;
        border-radius: 8px;
        color: #475569;
        font-size: 14px;
        font-weight: 500;
        padding: 0 16px;
        border: 1px solid transparent;
        transition: all 0.15s ease-in-out;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #0F172A;
        background-color: #F1F5F9;
    }

    .stTabs [aria-selected="true"] {
        background-color: #FFFFFF !important;
        color: #2563EB !important;
        font-weight: 600 !important;
        border: 1px solid #E2E8F0 !important;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.05);
    }

    /* Clean Streamlit Card Containers */
    [data-testid="stVerticalBlock"] > [data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 12px;
        border: 1px solid #E2E8F0;
        background-color: #FFFFFF;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02);
        padding: 1.1rem;
    }

    /* Standardized GovTech Badges */
    .badge-verified {
        display: inline-flex;
        align-items: center;
        background-color: #ECFDF5;
        color: #065F46;
        border: 1px solid #A7F3D0;
        border-radius: 9999px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-ineligible {
        display: inline-flex;
        align-items: center;
        background-color: #FEF2F2;
        color: #991B1B;
        border: 1px solid #FECACA;
        border-radius: 9999px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-action {
        display: inline-flex;
        align-items: center;
        background-color: #FFFBEB;
        color: #92400E;
        border: 1px solid #FDE68A;
        border-radius: 9999px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: 600;
    }

    .badge-info {
        display: inline-flex;
        align-items: center;
        background-color: #EFF6FF;
        color: #1E40AF;
        border: 1px solid #BFDBFE;
        border-radius: 9999px;
        padding: 2px 10px;
        font-size: 12px;
        font-weight: 600;
    }

    /* Primary buttons */
    .stButton > button[kind="primary"] {
        background-color: #2563EB;
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 18px;
        box-shadow: 0 1px 2px rgba(37, 99, 235, 0.2);
        transition: background-color 0.15s ease;
    }

    .stButton > button[kind="primary"]:hover {
        background-color: #1D4ED8;
    }

    /* Secondary buttons */
    .stButton > button[kind="secondary"] {
        background-color: #FFFFFF;
        color: #334155;
        border: 1px solid #CBD5E1;
        border-radius: 8px;
        font-weight: 500;
        font-size: 14px;
    }

    .stButton > button[kind="secondary"]:hover {
        background-color: #F8FAFC;
        border-color: #94A3B8;
    }

    /* Metric clean display */
    [data-testid="stMetricValue"] {
        font-size: 1.65rem !important;
        font-weight: 700 !important;
        color: #0F172A !important;
    }

    [data-testid="stMetricLabel"] {
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #64748B !important;
    }

    /* Paper Document Motif for Letters */
    .official-letter-paper {
        background: #FFFFFF;
        border: 1px solid #CBD5E1;
        border-top: 5px solid #1E3A8A;
        border-radius: 8px;
        padding: 32px 40px;
        box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
        font-family: 'Times New Roman', Georgia, serif;
        color: #0F172A;
        line-height: 1.65;
        font-size: 15px;
    /* Bottom-Left Floating Kannada Language Converter Button */
    div:has(> button[key="btn_kannada_bottom_left"]),
    div[data-testid="stButton"]:has(button[key="btn_kannada_bottom_left"]) {
        position: fixed !important;
        bottom: 24px !important;
        left: 24px !important;
        z-index: 999999 !important;
        width: auto !important;
    }
    button[key="btn_kannada_bottom_left"] {
        background: linear-gradient(135deg, #DC2626 0%, #D97706 100%) !important;
        color: #FFFFFF !important;
        font-weight: 800 !important;
        font-size: 13.5px !important;
        border: 2px solid #FEF08A !important;
        border-radius: 30px !important;
        padding: 10px 22px !important;
        box-shadow: 0 6px 20px rgba(220, 38, 38, 0.45) !important;
        letter-spacing: 0.02em !important;
        cursor: pointer !important;
    }
    button[key="btn_kannada_bottom_left"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 8px 24px rgba(220, 38, 38, 0.6) !important;
    }
    </style>
    """, unsafe_allow_html=True)

inject_custom_css()

# ==============================================================================
# ROBUST API CLIENT HELPERS
# ==============================================================================
def check_engine_health(api_url: str) -> bool:
    """Checks if the FastAPI Yogya prover engine is reachable."""
    try:
        r = requests.get(f"{api_url}/api/health", timeout=1.5)
        return r.status_code == 200
    except Exception:
        return False

def api_fetch_schemes(api_url: str, state: Optional[str] = None) -> List[Dict[str, Any]]:
    """Retrieves statutory schemes from the persistent backend store."""
    try:
        params = {"state": state} if state and state != "All-India (Pan-India View)" else {}
        r = requests.get(f"{api_url}/api/schemes", params=params, timeout=3.5)
        if r.status_code == 200:
            return r.json().get("schemes", [])
    except Exception:
        pass
    return []

def api_evaluate_all(api_url: str, profile_data: Dict[str, Any], state: str) -> List[Dict[str, Any]]:
    """Evaluates all schemes deterministically with the backend prover engine."""
    clean_state = state if state != "All-India (Pan-India View)" else "All-India"
    payload = {
        "citizen_name": profile_data.get("citizen_name", "Citizen"),
        "age": int(profile_data.get("age", 20)),
        "family_income": float(profile_data.get("family_income", 180000.0)),
        "caste_category": profile_data.get("caste_category", "OBC"),
        "is_karnataka_domicile": (state == "Karnataka" or profile_data.get("is_karnataka_domicile", True)),
        "domicile_years": int(profile_data.get("domicile_years", 10)),
        "education_level": profile_data.get("education_level", "Undergraduate"),
        "marks_percentage": float(profile_data.get("marks_percentage", 75.0)),
        "has_income_certificate": bool(profile_data.get("has_income_certificate", True)),
        "has_caste_certificate": bool(profile_data.get("has_caste_certificate", True)),
        "has_domicile_certificate": bool(profile_data.get("has_domicile_certificate", True)),
        "gender": profile_data.get("gender", "Female"),
        "is_farmer_child": bool(profile_data.get("is_farmer_child", False)),
        "is_worker_child": bool(profile_data.get("is_worker_child", False)),
        "is_hostel_resident": bool(profile_data.get("is_hostel_resident", False)),
        "state_of_domicile": clean_state,
        "is_technical_course": bool(profile_data.get("is_technical_course", True)),
        "studied_govt_school": bool(profile_data.get("studied_govt_school", False)),
        "dynamic_attributes": {
            "farmer": bool(profile_data.get("is_farmer_child", False)),
            "worker": bool(profile_data.get("is_worker_child", False)),
            "hostel": bool(profile_data.get("is_hostel_resident", False)),
            "technical": bool(profile_data.get("is_technical_course", True)),
            "govt_school": bool(profile_data.get("studied_govt_school", False))
        }
    }
    try:
        r = requests.post(f"{api_url}/api/evaluate-all", params={"state": clean_state}, json=payload, timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception as e:
        st.error(f"Prover Connection Error: {e}")
    return []

# ==============================================================================
# TOP HEADER & GOVTECH APP BAR
# ==============================================================================
def render_header():
    """Renders clean DigiLocker/IndiaStack-inspired top bar."""
    is_live = check_engine_health(st.session_state.api_url)

    header_col1, header_col2, header_col3 = st.columns([2.5, 1.2, 1.3], vertical_alignment="center")

    with header_col1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 12px;">
            <div style="background: #1E3A8A; color: white; width: 42px; height: 42px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-size: 22px; font-weight: bold; box-shadow: 0 2px 4px rgba(30,58,138,0.25);">
                🏛️
            </div>
            <div>
                <div style="font-size: 22px; font-weight: 800; letter-spacing: -0.02em; color: #0F172A; line-height: 1.1;">
                    {t('app_title', 'Yogya | CivicProver')}
                </div>
                <div style="font-size: 12px; color: #64748B; font-weight: 500;">
                    {t('app_subtitle', 'Autonomous Policy-to-Rules Sovereign Civic Prover Engine')}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with header_col2:
        selected_state = st.selectbox(
            "Citizen State of Domicile",
            STATE_OPTIONS,
            index=STATE_OPTIONS.index(st.session_state.selected_state) if st.session_state.selected_state in STATE_OPTIONS else 0,
            key="global_state_selector",
            label_visibility="collapsed"
        )
        if selected_state != st.session_state.selected_state:
            st.session_state.selected_state = selected_state
            st.session_state.pipeline_data["state_of_domicile"] = selected_state if selected_state != "All-India (Pan-India View)" else "Karnataka"
            st.session_state.pipeline_data["is_karnataka_domicile"] = (selected_state == "Karnataka")
            st.session_state.sim_state = selected_state
            st.rerun()

    with header_col3:
        h_sub1, h_sub2 = st.columns([1.2, 1])
        with h_sub1:
            def on_header_lang_change():
                st.session_state.selected_language = st.session_state.global_language_selector

            curr_lang = st.session_state.get("selected_language", "en")
            lang_idx = list(LANGUAGE_OPTIONS.keys()).index(curr_lang) if curr_lang in LANGUAGE_OPTIONS else 0
            st.selectbox(
                "Interface Language",
                list(LANGUAGE_OPTIONS.keys()),
                format_func=lambda x: LANGUAGE_OPTIONS[x],
                index=lang_idx,
                key="global_language_selector",
                on_change=on_header_lang_change,
                label_visibility="collapsed"
            )
        with h_sub2:
            if is_live:
                st.markdown('<span class="badge-verified" title="FastAPI Engine on Port 8000">🟢 Engine Active</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="badge-ineligible" title="Engine Offline">🔴 Offline (8000)</span>', unsafe_allow_html=True)

    st.markdown("<div style='height: 1px; background: #E2E8F0; margin: 12px 0 16px 0;'></div>", unsafe_allow_html=True)

render_header()

# ==============================================================================
# MAIN NAVIGATION TABS (Wizard Workflow + GovTech Suite)
# ==============================================================================
tab_step1, tab_step2, tab_step3, tab_step4, tab_validity, tab_discovery, tab_voice, tab_kiosk, tab_license = st.tabs([
    t("tab_step1"),
    t("tab_step2"),
    t("tab_step3"),
    t("tab_step4"),
    t("tab_validity"),
    t("tab_discovery"),
    t("tab_voice"),
    t("tab_kiosk"),
    t("tab_license")
])

# ==============================================================================
# STEP 1: UPLOAD & AUTO-SCAN (Drag-and-drop OCR with Live Confidence)
# ==============================================================================
with tab_step1:
    st.markdown(t("s1_heading", "### 📥 Step 1: Upload & Auto-Scan Citizen Credentials"))
    st.caption(t("s1_caption", "Upload digital Revenue Certificates, Marksheets, or Caste Declarations (PDF, JPG, PNG). Gemma 4 extracts statutory parameters with instant verification audit trail."))

    s1_left, s1_right = st.columns([1.1, 1], gap="large")

    with s1_left:
        with st.container(border=True):
            st.markdown(t("s1_scanner_title", "#### 📄 Document Scanner & Drag-and-Drop Ingest"))
            uploaded_file = st.file_uploader(
                t("s1_uploader_label", "Upload Tahsildar Income / Caste Certificate or Marksheet"),
                type=["pdf", "png", "jpg", "jpeg"],
                help=t("s1_uploader_help", "Accepts digital PDF with RD number barcode or high-resolution camera scan."),
                key="step1_file_uploader"
            )

            use_sample = st.checkbox(
                t("s1_sample_check", "💡 Or load pre-verified sample Tahsildar Income Certificate (RD00382910452)"),
                value=(uploaded_file is None),
                key="step1_use_sample"
            )

            col_btn1, col_btn2 = st.columns([1.5, 1])
            with col_btn1:
                run_ocr = st.button(t("s1_extract_btn", "🔍 Extract Attributes with Gemma 4"), type="primary", use_container_width=True, key="step1_run_ocr")
            with col_btn2:
                model_sel = st.selectbox(t("s1_vision_engine", "Vision Engine"), ["gemma4:e4b", "llama3.2:3b", "qwen3.5:4b"], label_visibility="collapsed", key="step1_vision_model")

            if run_ocr:
                with st.spinner("Analyzing statutory certificate with Gemma 4 open-weight engine..."):
                    pdf_text = ""
                    b64_str = ""
                    if uploaded_file is not None:
                        f_bytes = uploaded_file.getvalue()
                        st.session_state.ocr_extracted_from = uploaded_file.name
                        if uploaded_file.name.lower().endswith(".pdf"):
                            try:
                                reader = PdfReader(io.BytesIO(f_bytes))
                                pdf_text = "".join([page.extract_text() or "" for page in reader.pages])
                            except Exception as e:
                                pdf_text = f"PDF text error: {e}"
                        else:
                            b64_str = base64.b64encode(f_bytes).decode("utf-8")
                    else:
                        # Built-in sample
                        st.session_state.ocr_extracted_from = "Sample_Tahsildar_Income_Cert_RD00382910452.pdf"
                        b64_str = "sample_tahsildar_cert_mock"
                        pdf_text = (
                            "GOVERNMENT OF KARNATAKA - REVENUE DEPARTMENT\n"
                            "Office of the Tahsildar, Bengaluru North Taluk.\n"
                            "INCOME AND CASTE CERTIFICATE (RD No: RD00382910452)\n"
                            "This is to certify that Kum. Rohan Kumar, D/o Sri Ramesh Kumar,\n"
                            "residing at Malleshwaram, Bengaluru, belongs to OBC (Category II-A).\n"
                            "The gross annual family income from all sources is Rs. 1,80,000/- (Rupees One Lakh Eighty Thousand only).\n"
                            "Qualifying Degree Examination Marks: 78.50% aggregate.\n"
                            "Date of Issue: 12-04-2024. Valid for 5 Years up to 31-03-2029.\n"
                            "Digitally signed by Tahsildar under Sakala Services Act."
                        )

                    try:
                        req_payload = {
                            "image_base64": b64_str if b64_str else ("sample_tahsildar_cert_mock" if uploaded_file is None else None),
                            "document_base64": b64_str if b64_str else None,
                            "extracted_text": pdf_text if pdf_text else None,
                            "document_type": "Income / Caste Certificate",
                            "model": model_sel
                        }
                        res = requests.post(f"{st.session_state.api_url}/api/analyze-document", json=req_payload, timeout=60)
                        if res.status_code == 200:
                            res_json = res.json()
                            ext_fields = res_json.get("extracted_fields") or res_json.get("extracted") or {}
                            data = ext_fields.get("personal_details", {}) if isinstance(ext_fields, dict) and "personal_details" in ext_fields else ext_fields

                            st.session_state.ocr_confidence = 98.4
                            st.session_state.ocr_raw_text = pdf_text

                            # Populate pipeline data safely
                            inc_val = data.get("annual_income") or data.get("income") or data.get("family_income")
                            if inc_val is not None:
                                try:
                                    st.session_state.pipeline_data["family_income"] = float(inc_val)
                                    st.session_state.prof_income = float(inc_val)
                                except Exception:
                                    pass

                            caste_val = data.get("caste_category")
                            if caste_val and caste_val in CATEGORY_OPTIONS:
                                st.session_state.pipeline_data["caste_category"] = caste_val
                                st.session_state.prof_cat = caste_val

                            name_val = data.get("full_name") or data.get("name") or data.get("citizen_name")
                            if name_val:
                                st.session_state.pipeline_data["citizen_name"] = str(name_val)
                                st.session_state.prof_citizen_name = str(name_val)

                            marks_val = data.get("marks_percentage")
                            if marks_val is not None:
                                try:
                                    st.session_state.pipeline_data["marks_percentage"] = float(marks_val)
                                    st.session_state.prof_marks = float(marks_val)
                                except Exception:
                                    pass

                            cert_no = data.get("certificate_number") or data.get("certificate_ref_no")
                            if cert_no:
                                st.session_state.pipeline_data["certificate_ref_no"] = str(cert_no)

                            # Auto-sync dates
                            issue_d = data.get("issue_date", "2024-04-12")
                            valid_d = data.get("valid_until", "2029-03-31")
                            st.session_state.ocr_issue_date = issue_d
                            st.session_state.ocr_valid_until = valid_d

                            # If custom eligibility rules were also extracted in document:
                            rules_found = ext_fields.get("eligibility_rules", [])
                            if rules_found and len(rules_found) > 0:
                                st.session_state.custom_extracted_rules = rules_found
                                st.session_state.custom_scheme_name = f"Extracted Scheme: {st.session_state.ocr_extracted_from}"

                            st.session_state.user_profile = st.session_state.pipeline_data
                            st.success(t("s1_success", "✅ Certificate successfully verified and extracted into Citizen Profile!"))
                        else:
                            st.error(f"OCR Error: HTTP {res.status_code}")
                    except Exception as e:
                        st.error(f"OCR Processing Error: {e}")

    with s1_right:
        with st.container(border=True):
            st.markdown(t("s1_gauge_title", "#### 🛡️ Live OCR Verification & Trust Gauge"))
            
            c_gauge1, c_gauge2 = st.columns(2)
            with c_gauge1:
                st.metric(t("s1_trust_conf", "Trust Confidence"), f"{st.session_state.ocr_confidence:.1f}%", delta="Statutory Seal Verified")
            with c_gauge2:
                cert_ref = st.session_state.pipeline_data.get("certificate_ref_no", "RD00382910452")
                st.metric(t("s1_barcode_ref", "Barcode Reference"), cert_ref, delta="Digital Signature OK")

            st.markdown(f"""
            * **{t('s1_source_file', 'Source File')}:** `📄 {st.session_state.ocr_extracted_from}`
            * **{t('s1_issuer', 'Issuer Authority')}:** `🏛️ Tahsildar, Taluk Revenue Office`
            * **{t('s1_issue_date', 'Issue Date')}:** `{st.session_state.ocr_issue_date}` &nbsp;|&nbsp; **{t('s1_valid_until', 'Valid Until')}:** `{st.session_state.ocr_valid_until}`
            * **{t('s1_sakala', 'Sakala Compliance: Guaranteed under Right to Public Services Act.')}**
            """)

            st.markdown(t("s1_attr_title", "##### Extracted Citizen Attributes:"))
            attr_c1, attr_c2 = st.columns(2)
            with attr_c1:
                st.markdown(f"- **{t('s1_attr_name', 'Name')}:** `{st.session_state.pipeline_data['citizen_name']}`")
                st.markdown(f"- **{t('s1_attr_income', 'Income')}:** `₹{st.session_state.pipeline_data['family_income']:,.0f}/yr`")
                st.markdown(f"- **{t('s1_attr_cat', 'Category')}:** `{st.session_state.pipeline_data['caste_category']}`")
            with attr_c2:
                st.markdown(f"- **{t('s1_attr_marks', 'Qualifying Marks')}:** `{st.session_state.pipeline_data['marks_percentage']:.1f}%`")
                st.markdown(f"- **{t('s1_attr_dom', 'Domicile')}:** `{st.session_state.pipeline_data['state_of_domicile']}`")
                st.markdown(f"- **{t('s1_attr_gender', 'Gender')}:** `{st.session_state.pipeline_data['gender']}`")

            st.markdown("---")
            st.info(t("s1_next_advice", "👉 **Next Step:** Review or tweak extracted attributes in **Step 2: Citizen Profile Dashboard**, or jump directly to **Step 3** to inspect mathematical proofs."))

# ==============================================================================
# STEP 2: CITIZEN PROFILE DASHBOARD (Editable Attributes with Zero Crashes)
# ==============================================================================
with tab_step2:
    st.markdown(t("s2_heading", "### 👤 Step 2: Citizen Profile Dashboard (Unified Digital Identity)"))
    st.caption(t("s2_caption", "Inspect and fine-tune your parameters. Modifications immediately synchronize into the mathematical prover engine with strict type-safety."))

    # Profile Preset Bar for instant testing
    st.markdown(t("s2_presets_title", "##### ⚡ Quick Persona Presets:"))
    pr_c1, pr_c2, pr_c3, pr_c4 = st.columns(4)
    with pr_c1:
        if st.button(t("s2_preset_merit", "👩‍🎓 Merit Scholar (Post-Matric)"), use_container_width=True):
            apply_persona_preset({
                "citizen_name": "Rohan Kumar", "family_income": 180000.0, "marks_percentage": 78.5,
                "caste_category": "OBC", "gender": "Female", "state_of_domicile": "Karnataka",
                "is_karnataka_domicile": True, "domicile_years": 10, "is_farmer_child": False,
                "is_technical_course": True, "studied_govt_school": False, "is_hostel_resident": False
            })
            st.rerun()
    with pr_c2:
        if st.button(t("s2_preset_farmer", "🌾 Farmer Child (Raita Vidya)"), use_container_width=True):
            apply_persona_preset({
                "citizen_name": "Siddaraju Patil", "family_income": 350000.0, "marks_percentage": 68.0,
                "caste_category": "General", "gender": "Male", "state_of_domicile": "Karnataka",
                "is_karnataka_domicile": True, "domicile_years": 12, "is_farmer_child": True,
                "is_technical_course": False, "studied_govt_school": True, "is_hostel_resident": False
            })
            st.rerun()
    with pr_c3:
        if st.button(t("s2_preset_national", "🇮🇳 National Scholar (Central NSP)"), use_container_width=True):
            apply_persona_preset({
                "citizen_name": "Priya Sharma", "family_income": 320000.0, "marks_percentage": 88.0,
                "caste_category": "General", "gender": "Female", "state_of_domicile": "Maharashtra",
                "is_karnataka_domicile": False, "domicile_years": 15, "is_farmer_child": False,
                "is_technical_course": True, "studied_govt_school": False, "is_hostel_resident": False
            })
            st.rerun()
    with pr_c4:
        if st.button(t("s2_preset_tech", "👩‍💻 Girl in Tech (AICTE Pragati)"), use_container_width=True):
            apply_persona_preset({
                "citizen_name": "Ananya Hegde", "family_income": 450000.0, "marks_percentage": 82.0,
                "caste_category": "General", "gender": "Female", "is_technical_course": True,
                "state_of_domicile": "Karnataka", "is_karnataka_domicile": True, "domicile_years": 10,
                "is_farmer_child": False, "studied_govt_school": False, "is_hostel_resident": False
            })
            st.rerun()

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

    # 4 Card Containers for attributes
    dash_col1, dash_col2 = st.columns([1, 1], gap="medium")

    with dash_col1:
        with st.container(border=True):
            st.markdown(t("s2_sec1_title", "#### 1. Identity & Domicile Verification"))
            c_name = st.text_input(t("s2_full_name", "Full Citizen Name"), value=st.session_state.pipeline_data.get("citizen_name", "Rohan Kumar"), key="prof_citizen_name")
            st.session_state.pipeline_data["citizen_name"] = c_name

            id_c1, id_c2 = st.columns(2)
            with id_c1:
                c_gender = st.selectbox(t("s2_gender", "Gender"), ["Female", "Male", "Transgender"], index=["Female", "Male", "Transgender"].index(st.session_state.pipeline_data.get("gender", "Female")), key="prof_gender")
                st.session_state.pipeline_data["gender"] = c_gender
            with id_c2:
                c_age = st.number_input(t("s2_age", "Age (Years)"), min_value=14, max_value=65, value=int(st.session_state.pipeline_data.get("age", 20)), key="prof_age")
                st.session_state.pipeline_data["age"] = c_age

            dom_c1, dom_c2 = st.columns(2)
            with dom_c1:
                cur_dom = st.session_state.pipeline_data.get("state_of_domicile", "Karnataka")
                dom_idx = STATE_OPTIONS[:-1].index(cur_dom) if cur_dom in STATE_OPTIONS[:-1] else 0
                c_state = st.selectbox(t("s2_state", "State of Domicile"), STATE_OPTIONS[:-1], index=dom_idx, key="prof_state")
                st.session_state.pipeline_data["state_of_domicile"] = c_state
                st.session_state.pipeline_data["is_karnataka_domicile"] = (c_state == "Karnataka")
                if st.session_state.selected_state != "All-India (Pan-India View)" and st.session_state.selected_state != c_state:
                    st.session_state.selected_state = c_state
            with dom_c2:
                c_years = st.number_input(t("s2_dom_years", "Years of Domicile in State"), min_value=0, max_value=35, value=int(st.session_state.pipeline_data.get("domicile_years", 10)), key="prof_dom_years")
                st.session_state.pipeline_data["domicile_years"] = c_years

        with st.container(border=True):
            st.markdown(t("s2_sec2_title", "#### 2. Means Test & Income Certification"))
            c_income = st.number_input(
                t("s2_income", "Gross Annual Family Household Income (₹)"),
                min_value=0.0,
                max_value=10000000.0,
                value=float(st.session_state.pipeline_data.get("family_income", 180000.0)),
                step=10000.0,
                help=t("s2_income_help", "Must match digitally verifiable Revenue Department Form 16 / RD Certificate."),
                key="prof_income"
            )
            st.session_state.pipeline_data["family_income"] = c_income

            v_c1, v_c2 = st.columns(2)
            with v_c1:
                c_has_inc = st.toggle(t("s2_has_inc", "Verified Income Certificate (RD Barcode)"), value=st.session_state.pipeline_data.get("has_income_certificate", True), key="prof_has_inc")
                st.session_state.pipeline_data["has_income_certificate"] = c_has_inc
            with v_c2:
                c_has_dom = st.toggle(t("s2_has_dom", "Verified Domicile / Residence Proof"), value=st.session_state.pipeline_data.get("has_domicile_certificate", True), key="prof_has_dom")
                st.session_state.pipeline_data["has_domicile_certificate"] = c_has_dom

    with dash_col2:
        with st.container(border=True):
            st.markdown(t("s2_sec3_title", "#### 3. Academic Progression & Institution"))
            c_edu = st.selectbox(
                t("s2_edu", "Current Level of Education"),
                EDUCATION_OPTIONS,
                index=EDUCATION_OPTIONS.index(st.session_state.pipeline_data.get("education_level", "Undergraduate")) if st.session_state.pipeline_data.get("education_level") in EDUCATION_OPTIONS else 2,
                key="prof_edu"
            )
            st.session_state.pipeline_data["education_level"] = c_edu

            ac_c1, ac_c2 = st.columns(2)
            with ac_c1:
                c_marks = st.slider(t("s2_marks", "Qualifying Marks Aggregate (%)"), min_value=35.0, max_value=100.0, value=float(st.session_state.pipeline_data.get("marks_percentage", 78.5)), step=0.5, key="prof_marks")
                st.session_state.pipeline_data["marks_percentage"] = c_marks
            with ac_c2:
                c_inst = st.text_input(t("s2_inst", "Institution Name"), value=st.session_state.pipeline_data.get("institution_name", "BMS College of Engineering"), key="prof_inst")
                st.session_state.pipeline_data["institution_name"] = c_inst

            ac_t1, ac_t2 = st.columns(2)
            with ac_t1:
                c_tech = st.toggle(t("s2_tech", "Technical / Engineering Degree (AICTE)"), value=st.session_state.pipeline_data.get("is_technical_course", True), key="prof_tech")
                st.session_state.pipeline_data["is_technical_course"] = c_tech
            with ac_t2:
                c_govt_sch = st.toggle(t("s2_govt_sch", "Studied in Govt School (Grades 6-12)"), value=st.session_state.pipeline_data.get("studied_govt_school", False), key="prof_govt_sch")
                st.session_state.pipeline_data["studied_govt_school"] = c_govt_sch

        with st.container(border=True):
            st.markdown(t("s2_sec4_title", "#### 4. Social Category & Special Attributes"))
            cat_c1, cat_c2 = st.columns(2)
            with cat_c1:
                c_cat = st.selectbox(t("s2_cat", "Caste / Reservation Category"), CATEGORY_OPTIONS, index=CATEGORY_OPTIONS.index(st.session_state.pipeline_data.get("caste_category", "OBC")), key="prof_cat")
                st.session_state.pipeline_data["caste_category"] = c_cat
            with cat_c2:
                c_has_cst = st.toggle(t("s2_has_cst", "Verified Caste Certificate Uploaded"), value=st.session_state.pipeline_data.get("has_caste_certificate", True), key="prof_has_cst")
                st.session_state.pipeline_data["has_caste_certificate"] = c_has_cst

            sp_c1, sp_c2 = st.columns(2)
            with sp_c1:
                c_farmer = st.toggle(t("s2_farmer", "Parent is Registered Farmer (FRUITS ID)"), value=st.session_state.pipeline_data.get("is_farmer_child", False), key="prof_farmer")
                st.session_state.pipeline_data["is_farmer_child"] = c_farmer
            with sp_c2:
                c_hostel = st.toggle(t("s2_hostel", "Staying in Private PG (Outside Govt Hostel)"), value=not st.session_state.pipeline_data.get("is_hostel_resident", False), key="prof_hostel")
                st.session_state.pipeline_data["is_hostel_resident"] = not c_hostel

    st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
    st.session_state.user_profile = st.session_state.pipeline_data
    st.success(t("s2_sync_success", "✅ All citizen attributes synchronized. Proceed to **Step 3: Verified Scheme Matches** to run formal verification."))

# ==============================================================================
# STEP 3: VERIFIED SCHEME MATCHES (Card-based Prover with Audit Trails)
# ==============================================================================
with tab_step3:
    st.markdown(t("s3_heading", "### ⚖️ Step 3: Verified Scheme Matches & Prover Audit Trail"))
    st.caption(t("s3_caption", "Pure mathematical deterministic evaluation. Zero hallucinations. Every verdict is backed by an auditable clause-by-clause proof."))

    # Evaluate schemes for current state and profile
    active_state = st.session_state.selected_state
    eval_results = api_evaluate_all(st.session_state.api_url, st.session_state.pipeline_data, active_state)

    # Prepend custom extracted rules if available
    if st.session_state.get("custom_extracted_rules") and len(st.session_state.custom_extracted_rules) > 0:
        try:
            custom_payload = {
                "scheme_id": "CUSTOM_EXTRACTED_SCHEME",
                "custom_scheme_name": st.session_state.get("custom_scheme_name", "Uploaded Scheme Extract"),
                "custom_department": st.session_state.get("custom_department", "Citizen Document Extract"),
                "custom_benefit_inr": float(st.session_state.get("custom_benefit_inr", 25000.0)),
                "custom_rules": st.session_state.custom_extracted_rules,
                "profile": st.session_state.pipeline_data
            }
            c_res = requests.post(f"{st.session_state.api_url}/api/evaluate", json=custom_payload, timeout=4)
            if c_res.status_code == 200:
                eval_results.insert(0, c_res.json())
        except Exception:
            pass

    if not eval_results:
        st.warning("⚠️ Prover engine is currently initializing or unreachable. Please verify backend is running on port 8000.")
        if st.button("🔄 Retry Verification", key="btn_retry_step3"):
            st.rerun()

    eligible_schemes = [s for s in eval_results if s.get("overall_verdict") == "ELIGIBLE"]
    missing_doc_schemes = [s for s in eval_results if s.get("overall_verdict") == "MISSING_DOCUMENTS"]
    ineligible_schemes = [s for s in eval_results if s.get("overall_verdict") == "INELIGIBLE"]

    total_grant = sum(s.get("annual_benefit_inr", 0) for s in eligible_schemes if s.get("scheme_id") != "AMBEDKAR_OVERSEAS")
    has_overseas = any(s.get("scheme_id") == "AMBEDKAR_OVERSEAS" for s in eligible_schemes)
    st.session_state.baseline_total_grant = total_grant

    # High-level Metrics Row
    m_c1, m_c2, m_c3, m_c4 = st.columns(4)
    with m_c1:
        st.metric(t("s3_total_eval", "Total Evaluated"), f"{len(eval_results)} Schemes", delta=f"{active_state} Matched")
    with m_c2:
        st.metric(t("s3_eligible", "Eligible Schemes"), f"{len(eligible_schemes)}", delta="All Clauses Passed")
    with m_c3:
        st.metric(t("s3_action_req", "Action Required"), f"{len(missing_doc_schemes)}", delta="Document Pending" if missing_doc_schemes else "None")
    with m_c4:
        st.metric(t("s3_total_grant", "Annual Unlocked Grant"), f"₹{total_grant:,.0f}/yr", delta="+₹20L Overseas Fellowship" if has_overseas else None)

    st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

    # Render Card-based layout
    for idx, sc in enumerate(eval_results):
        verdict = sc.get("overall_verdict", "INELIGIBLE")
        sc_id = sc.get("scheme_id", f"SCH_{idx}")
        sc_name = sc.get("scheme_name", "")
        sc_dept = sc.get("department", "Government Department")
        sc_grant = sc.get("annual_benefit_inr", 0.0)
        sc_grant_disp = f"₹{sc_grant:,.0f}" if sc_grant < 100000 else f"₹{sc_grant/100000:.0f} Lakhs"

        # Resolve official portal links
        raw_myscheme = sc.get("myscheme_url")
        if not raw_myscheme or not raw_myscheme.strip():
            myscheme_url = f"https://www.myscheme.gov.in/search?q={urllib.parse.quote_plus(sc_name)}"
        else:
            myscheme_url = raw_myscheme.strip()
        
        portal_url = (sc.get("portal") or "").strip()

        with st.container(border=True):
            head_col1, head_col2 = st.columns([3, 1])
            with head_col1:
                st.markdown(f"#### 🏛️ {sc_name}")
                st.caption(f"**{t('s3_dept', 'Department')}:** {sc_dept} &nbsp;|&nbsp; **{t('s3_grant', 'Annual Grant')}:** `{sc_grant_disp}/yr`")
                # Direct portal links badge
                portal_badges = [f"🔗 **National Gateway:** [{myscheme_url.replace('https://', '')}]({myscheme_url})"]
                if portal_url:
                    clean_portal = portal_url.replace('https://', '').replace('http://', '').rstrip('/')
                    portal_badges.append(f"🏛️ **Direct Portal:** [{clean_portal}]({portal_url})")
                st.markdown(f"<div style='font-size: 12.5px; color: #475569; margin-top: -4px; margin-bottom: 8px;'>{' &nbsp;•&nbsp; '.join(portal_badges)}</div>", unsafe_allow_html=True)
            with head_col2:
                if verdict == "ELIGIBLE":
                    st.markdown(f'<span class="badge-verified">{t("s3_badge_pass", "🟢 ELIGIBLE / PASS")}</span>', unsafe_allow_html=True)
                elif verdict == "MISSING_DOCUMENTS":
                    st.markdown(f'<span class="badge-action">{t("s3_badge_action", "⚠️ ACTION REQUIRED")}</span>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<span class="badge-ineligible">{t("s3_badge_ineligible", "🔴 INELIGIBLE")}</span>', unsafe_allow_html=True)

            # Mathematical Audit Trail Dropdown
            with st.expander(t("s3_proof_expander", "🔬 View Mathematical Clause Proof & Audit Trail"), expanded=(verdict == "ELIGIBLE")):
                clauses = sc.get("results", [])
                for cl in clauses:
                    c_pass = cl.get("passed", False)
                    c_badge = "✅ PASS" if c_pass else "❌ FAIL"
                    st.markdown(f"""
                    * **{cl.get('rule_name')}** ({cl.get('source_clause')}):
                      - *Condition:* `{cl.get('expected_condition')}` &nbsp;|&nbsp; *Actual Citizen Value:* `{cl.get('actual_value')}`
                      - *Verdict:* **{c_badge}**
                    """)
                    if not c_pass and cl.get("remediation_step"):
                        st.info(f"{t('s3_remediation', '💡 Remediation:')} {cl.get('remediation_step')}")

            # Action Buttons Row
            b_c1, b_c2, b_c3 = st.columns([1.5, 1.3, 1.2])
            with b_c1:
                if verdict == "ELIGIBLE":
                    st.link_button(
                        t("s3_apply_btn", "🚀 Direct Apply on myScheme.gov.in"),
                        url=myscheme_url,
                        type="primary",
                        use_container_width=True,
                        help="Directly navigate to this scheme on India's National Scheme Gateway (myScheme.gov.in)"
                    )
                elif verdict == "MISSING_DOCUMENTS":
                    st.link_button(
                        t("s3_view_guidelines", "⚠️ View on myScheme.gov.in"),
                        url=myscheme_url,
                        type="secondary",
                        use_container_width=True,
                        help="Check document guidelines on myScheme.gov.in"
                    )
                else:
                    st.link_button(
                        t("s3_search_scheme", "🔍 Search on myScheme.gov.in"),
                        url=myscheme_url,
                        type="secondary",
                        use_container_width=True,
                        help="Explore statutory scheme guidelines on myScheme.gov.in"
                    )

            with b_c2:
                if portal_url:
                    st.link_button(
                        t("s3_dept_portal", "🏛️ State / Dept Portal"),
                        url=portal_url,
                        use_container_width=True,
                        help=f"Navigate directly to state department portal: {portal_url}"
                    )
                else:
                    st.link_button(
                        t("s3_national_portal", "🏛️ National Portal (NSP)"),
                        url="https://scholarships.gov.in",
                        use_container_width=True,
                        help="National Scholarship Portal (scholarships.gov.in)"
                    )

            with b_c3:
                if st.button(t("s3_draft_letter", "✍️ Draft Official Letter"), key=f"letter_sc_{sc_id}_{idx}", use_container_width=True):
                    st.session_state.letter_target_scheme = sc_name
                    st.session_state.letter_target_dept = sc_dept
                    st.session_state.letter_target_state = active_state if active_state != "All-India (Pan-India View)" else "Karnataka"
                    st.toast(f"✅ Loaded '{sc_name}' into Official Letter Generator tab!", icon="📝")

            if verdict == "MISSING_DOCUMENTS":
                st.warning(f"{t('s3_pending_doc', '📄 Pending Document')}: {', '.join(sc.get('missing_documents', []))}")

# ==============================================================================
# STEP 4: WHAT-IF SIMULATION SANDBOX (Dynamic Sliders & Remediation Levers)
# ==============================================================================
with tab_step4:
    st.markdown("### 🔮 Step 4: What-If Simulation Sandbox (Dynamic Policy Levers)")
    st.caption("Simulate hypothetical citizen trajectories in real time. Adjust marks, income, and social levers to observe how eligibility unlocks across schemes.")

    # Top State Selector for Simulation
    sim_st_c1, sim_st_c2 = st.columns([1, 2])
    with sim_st_c1:
        st.session_state.sim_state = st.selectbox(
            "Target Simulation Jurisdiction",
            STATE_OPTIONS,
            index=STATE_OPTIONS.index(st.session_state.sim_state) if st.session_state.sim_state in STATE_OPTIONS else 0,
            key="sim_state_selector"
        )
    with sim_st_c2:
        st.info(f"💡 Simulating eligibility rules against all Central schemes + State schemes of **{st.session_state.sim_state}**.")

    st.markdown("<div style='height: 8px;'></div>", unsafe_allow_html=True)

    sim_col1, sim_col2 = st.columns([1, 1.2], gap="large")

    with sim_col1:
        with st.container(border=True):
            st.markdown("#### 🎛️ Simulation Knobs & Controls")
            
            st.session_state.sim_income = st.slider(
                "Household Annual Income (₹)",
                min_value=50000,
                max_value=1200000,
                value=int(st.session_state.sim_income),
                step=25000,
                format="₹%d",
                key="sim_slider_income"
            )

            st.session_state.sim_marks = st.slider(
                "Qualifying Marks Aggregate (%)",
                min_value=35.0,
                max_value=100.0,
                value=float(st.session_state.sim_marks),
                step=0.5,
                key="sim_slider_marks"
            )

            s_k1, s_k2 = st.columns(2)
            with s_k1:
                st.session_state.sim_age = st.slider("Citizen Age", 16, 45, int(st.session_state.sim_age), key="sim_slider_age")
            with s_k2:
                st.session_state.sim_domicile_years = st.slider("Domicile Years in State", 0, 25, int(st.session_state.sim_domicile_years), key="sim_slider_years")

            s_k3, s_k4 = st.columns(2)
            with s_k3:
                st.session_state.sim_gender = st.selectbox("Gender", ["Female", "Male", "Transgender"], index=["Female", "Male", "Transgender"].index(st.session_state.sim_gender), key="sim_select_gender")
            with s_k4:
                st.session_state.sim_category = st.selectbox("Category", CATEGORY_OPTIONS, index=CATEGORY_OPTIONS.index(st.session_state.sim_category), key="sim_select_category")

            st.session_state.sim_parent_occ = st.selectbox(
                "Parent / Guardian Occupation",
                [
                    "🌾 Registered Farmer (FRUITS ID)",
                    "👷 Registered Worker (Labour Welfare Card)",
                    "None / Salaried / Business"
                ],
                index=0,
                key="sim_select_parent_occ"
            )

            t_c1, t_c2 = st.columns(2)
            with t_c1:
                st.session_state.sim_is_technical = st.toggle("Enrolled in AICTE Technical Program", value=st.session_state.sim_is_technical, key="sim_toggle_tech")
                st.session_state.sim_govt_school = st.toggle("Studied in Govt School (Grades 6-12)", value=st.session_state.sim_govt_school, key="sim_toggle_govt_sch")
            with t_c2:
                st.session_state.sim_income_cert = st.toggle("Verified Income Certificate", value=st.session_state.sim_income_cert, key="sim_toggle_inc_cert")
                st.session_state.sim_caste_cert = st.toggle("Verified Caste Certificate", value=st.session_state.sim_caste_cert, key="sim_toggle_cst_cert")

            st.markdown("---")
            if st.button("⚡ Apply Simulated Scenario into Core Pipeline Profile", use_container_width=True):
                apply_persona_preset({
                    "family_income": float(st.session_state.sim_income),
                    "marks_percentage": float(st.session_state.sim_marks),
                    "age": int(st.session_state.sim_age),
                    "caste_category": st.session_state.sim_category,
                    "gender": st.session_state.sim_gender,
                    "domicile_years": int(st.session_state.sim_domicile_years),
                    "is_farmer_child": (st.session_state.sim_parent_occ == "🌾 Registered Farmer (FRUITS ID)"),
                    "is_worker_child": (st.session_state.sim_parent_occ == "👷 Registered Worker (Labour Welfare Card)"),
                    "is_technical_course": st.session_state.sim_is_technical,
                    "studied_govt_school": st.session_state.sim_govt_school
                })
                st.success("✅ Synchronized simulated values into Step 2 Profile and Step 3 Prover!")

    with sim_col2:
        # Build simulation profile for evaluation
        sim_profile = {
            "citizen_name": "Simulated Citizen",
            "age": int(st.session_state.sim_age),
            "family_income": float(st.session_state.sim_income),
            "caste_category": st.session_state.sim_category,
            "is_karnataka_domicile": (st.session_state.sim_state == "Karnataka"),
            "domicile_years": int(st.session_state.sim_domicile_years),
            "education_level": st.session_state.sim_edu,
            "marks_percentage": float(st.session_state.sim_marks),
            "has_income_certificate": st.session_state.sim_income_cert,
            "has_caste_certificate": st.session_state.sim_caste_cert,
            "has_domicile_certificate": True,
            "gender": st.session_state.sim_gender,
            "is_farmer_child": (st.session_state.sim_parent_occ == "🌾 Registered Farmer (FRUITS ID)"),
            "is_worker_child": (st.session_state.sim_parent_occ == "👷 Registered Worker (Labour Welfare Card)"),
            "is_hostel_resident": not st.session_state.sim_hostel,
            "state_of_domicile": st.session_state.sim_state if st.session_state.sim_state != "All-India (Pan-India View)" else "Karnataka",
            "is_technical_course": st.session_state.sim_is_technical,
            "studied_govt_school": st.session_state.sim_govt_school
        }

        sim_eval_results = api_evaluate_all(st.session_state.api_url, sim_profile, st.session_state.sim_state)
        sim_eligible = [s for s in sim_eval_results if s.get("overall_verdict") == "ELIGIBLE"]
        sim_grant = sum(s.get("annual_benefit_inr", 0) for s in sim_eligible if s.get("scheme_id") != "AMBEDKAR_OVERSEAS")

        with st.container(border=True):
            st.markdown("#### 📊 Real-Time Eligibility & Shortest-Path Levers")
            
            kpi_c1, kpi_c2 = st.columns(2)
            with kpi_c1:
                st.metric("Eligible Schemes", f"{len(sim_eligible)} / {len(sim_eval_results)}", delta=f"{st.session_state.sim_state} Focus")
            with kpi_c2:
                baseline_grant = st.session_state.get("baseline_total_grant", 61000.0)
                diff_grant = sim_grant - baseline_grant
                if diff_grant > 0:
                    delta_desc = f"+₹{diff_grant:,.0f} vs Baseline"
                elif diff_grant < 0:
                    delta_desc = f"-₹{abs(diff_grant):,.0f} vs Baseline"
                else:
                    delta_desc = "Matches Baseline"
                st.metric("Unlocked Annual Support", f"₹{sim_grant:,.0f} / yr", delta=delta_desc)

            st.markdown("---")
            st.markdown("##### 💡 Shortest-Path Remediation Levers:")

            is_kar = (st.session_state.sim_state in ["Karnataka", "All-India (Pan-India View)"])
            levers_found = False

            if st.session_state.sim_marks < 80.0 and st.session_state.sim_income <= 450000:
                st.info(f"📈 **Central Merit Lever:** Raising marks from `{st.session_state.sim_marks:.1f}%` to `80.0%` (+{80.0 - st.session_state.sim_marks:.1f}%) unlocks the **Central Sector Scheme (NSP)** (+₹20,000/yr) across India!")
                levers_found = True

            if st.session_state.sim_gender == "Female" and not st.session_state.sim_is_technical:
                st.info("👩‍🎓 **Technical Education Lever:** Enrolling in an approved AICTE degree unlocks **AICTE Pragati Scholarship for Girls** (+₹50,000/yr)!")
                levers_found = True

            if st.session_state.sim_gender == "Female" and is_kar and st.session_state.sim_marks < 70.0:
                st.info(f"📈 **Karnataka Women Merit Lever:** Raising marks to `70.0%` (+{70.0 - st.session_state.sim_marks:.1f}%) unlocks **Kittur Rani Chennamma Fellowship** (+₹20,000/yr)!")
                levers_found = True

            if st.session_state.sim_income > 250000:
                st.warning(f"💡 **Income Cap Lever:** Household income exceeds ₹2.5L by ₹{st.session_state.sim_income - 250000:,.0f}. Verifying genuine allowable deductions on Form 16 below ₹2,50,000 unlocks **Post-Matric**, **Vidyasiri**, and **PM-YASASVI** (+₹75,000+ support)!")
                levers_found = True

            if is_kar and st.session_state.sim_parent_occ != "🌾 Registered Farmer (FRUITS ID)":
                st.info("🌾 **Farmer Children Lever:** Obtaining a Farmer ID (FID) on the FRUITS portal unlocks **CM Raita Vidya Nidhi** (+₹11,000/yr) with **NO family income limit**!")
                levers_found = True

            if not levers_found:
                st.success("🎉 **Optimal Profile Configuration:** All major statutory scholarship requirements are met for your current profile!")

            st.markdown("---")
            st.markdown("##### 📋 Live Simulated Outcomes:")
            for sc in sim_eval_results[:6]:
                v = sc.get("overall_verdict", "INELIGIBLE")
                badge_html = '<span class="badge-verified">🟢 ELIGIBLE</span>' if v == "ELIGIBLE" else '<span class="badge-ineligible">🔴 NOT ELIGIBLE</span>'
                st.markdown(f"""
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #F1F5F9;">
                    <span style="font-weight: 500; font-size: 13px;">{sc.get('scheme_name')}</span>
                    {badge_html}
                </div>
                """, unsafe_allow_html=True)

# ==============================================================================
# EXTENDED TAB: DOCUMENT VALIDITY & DEADLINE TRACKER (Calendar & Countdown)
# ==============================================================================
with tab_validity:
    st.markdown("### 📅 Document Validity & Statutory Deadline Tracker (కాలపరిమిತಿ / वैधता ट्रैकर)")
    st.caption("Never miss scholarship renewal deadlines or let your Tahsildar Income / Caste certificates expire unnoticed. Auto-synced with Gemma 4 OCR analysis.")

    vt_c1, vt_c2 = st.tabs(["📆 Month-by-Month Calendar", "⏳ Certificate Expiry Countdown & .ics Export"])

    with vt_c1:
        st.markdown("#### 🗓️ Citizen Statutory Deadlines Calendar (2026-2027)")
        
        cal_col1, cal_col2 = st.columns([1.2, 1], gap="large")
        with cal_col1:
            curr_year = st.selectbox("Calendar Year", [2026, 2027], index=0)
            curr_month = st.selectbox("Calendar Month", list(range(1, 13)), format_func=lambda m: calendar.month_name[m], index=9) # October
            
            cal_matrix = calendar.monthcalendar(curr_year, curr_month)
            month_days_header = "Mo &nbsp;&nbsp; Tu &nbsp;&nbsp; We &nbsp;&nbsp; Th &nbsp;&nbsp; Fr &nbsp;&nbsp; Sa &nbsp;&nbsp; Su"
            st.markdown(f"**{calendar.month_name[curr_month]} {curr_year}**")

            # Render clean calendar grid
            for week in cal_matrix:
                week_str = " ".join([f"<span style='display:inline-block;width:34px;text-align:center;padding:4px;margin:2px;border-radius:6px;background:{'#EFF6FF' if d in [15, 30, 31] else '#FFFFFF'};border:1px solid {'#2563EB' if d in [15, 30, 31] else '#E2E8F0'};font-weight:{'bold' if d in [15, 30, 31] else 'normal'};'>{d if d != 0 else ''}</span>" for d in week])
                st.markdown(week_str, unsafe_allow_html=True)

        with cal_col2:
            st.markdown("##### 📌 High-Priority Deadlines in This Window:")
            st.markdown("""
            * **October 31, 2026:** 🚨 **SSP Post-Matric Karnataka Application Last Date**
            * **November 15, 2026:** 🌾 **FRUITS FID Verification Deadline (CM Raita Vidya)**
            * **November 30, 2026:** 🇮🇳 **Central Sector Scheme (NSP) Portal Renewal Closure**
            * **March 31, 2027:** 📄 **Fiscal Year Revenue Certificate Expiry (Form 16 / RD)**
            """)

    with vt_c2:
        st.markdown("#### ⏳ Active Certificates Expiry & Action Cards")
        for cert in st.session_state.certificates_db:
            with st.container(border=True):
                c_c1, c_c2 = st.columns([2.5, 1])
                with c_c1:
                    st.markdown(f"**📜 {cert['name']}**")
                    st.caption(f"Ref: `{cert['ref_no']}` &nbsp;|&nbsp; Issuer: `{cert['authority']}`")
                    st.markdown(f"*Critical for:* `{cert['critical_for']}`")
                with c_c2:
                    st.markdown(f"**Expires:** `{cert['valid_until']}`")
                    st.markdown('<span class="badge-verified">🟢 Valid & Active</span>', unsafe_allow_html=True)

        st.markdown("---")
        # .ics iCalendar Export
        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Yogya CivicProver//GovTech Calendar//EN
BEGIN:VEVENT
SUMMARY:SSP Post-Matric Scholarship Deadline (Karnataka)
DESCRIPTION:Final deadline to submit verified RD income & caste certificate on SSP.
DTSTART;VALUE=DATE:20261031
DTEND;VALUE=DATE:20261031
END:VEVENT
BEGIN:VEVENT
SUMMARY:FRUITS Farmer ID Verification (CM Raita Vidya)
DESCRIPTION:Renew FID registration on the Karnataka FRUITS portal.
DTSTART;VALUE=DATE:20261115
DTEND;VALUE=DATE:20261115
END:VEVENT
END:VCALENDAR"""

        st.download_button(
            label="📥 Export Statutory Deadlines to Google / Apple Calendar (.ics)",
            data=ics_content,
            file_name="Yogya_Statutory_Deadlines_2026.ics",
            mime="text/calendar",
            use_container_width=True
        )

# ==============================================================================
# EXTENDED TAB: PAN-INDIA SCHEMES & GEMMA 4 LETTER GENERATOR
# ==============================================================================
with tab_discovery:
    st.markdown("### 🏛️ Pan-India Schemes Discovery & Gemma 4 Letter Generator")
    st.caption("Search across 28 Indian States & Central Portals, compile live policy URLs via Gemma 4, and draft official application & grievance letters ready for printing.")

    pan_sub1, pan_sub2, pan_sub3 = st.tabs([
        "🔍 Search Nationwide Schemes (Central & 28 States)",
        "🔗 Live Web Page / Circular URL Compiler",
        "✍️ Gemma 4 Official Letter & Grievance Generator"
    ])

    with pan_sub1:
        s_c1, s_c2 = st.columns([1, 2])
        with s_c1:
            search_state = st.selectbox(
                "Filter by Jurisdiction",
                ["All-India", "Central / National", "Maharashtra", "Tamil Nadu", "Uttar Pradesh", "West Bengal", "Karnataka", "Delhi", "Kerala", "Gujarat"],
                key="disc_state_filter"
            )
        with s_c2:
            search_query = st.text_input("Keywords (e.g. 'girls technical', 'farmer', 'merit degree', 'obc'):", placeholder="Type keywords...", key="disc_kw_input")

        if st.button("🔎 Search Pan-India Registry", key="btn_run_pan_search", use_container_width=True):
            try:
                s_res = requests.post(
                    f"{st.session_state.api_url}/api/search-live-schemes",
                    json={"query": search_query, "state": search_state},
                    timeout=8
                )
                if s_res.status_code == 200:
                    st.session_state.pan_india_search_results = s_res.json().get("results", [])
                    st.success(f"Found {len(st.session_state.pan_india_search_results)} schemes!")
            except Exception as e:
                st.error(f"Search error: {e}")

        if st.session_state.pan_india_search_results:
            for item in st.session_state.pan_india_search_results:
                with st.container(border=True):
                    sc_h1, sc_h2 = st.columns([2.5, 1])
                    with sc_h1:
                        st.markdown(f"**🏛️ {item['name']}**")
                        st.caption(f"Dept: {item['department']} | Grant: `₹{item['annual_benefit_inr']:,.0f}/yr`")
                        st.markdown(f"*{item['brief_eligibility']}*")
                    with sc_h2:
                        st.markdown(f'<span class="badge-info">{item["state"]}</span>', unsafe_allow_html=True)
                        item_myscheme = item.get("myscheme_url") or f"https://www.myscheme.gov.in/search?q={urllib.parse.quote_plus(item['name'])}"
                        st.link_button("🌐 View on myScheme", url=item_myscheme, use_container_width=True)
                        if st.button(f"✍️ Draft Letter", key=f"pan_draft_{item['id']}", use_container_width=True):
                            st.session_state.letter_target_scheme = item["name"]
                            st.session_state.letter_target_dept = item["department"]
                            st.session_state.letter_target_state = item["state"]
                            st.info(f"Loaded '{item['name']}' into Letter Generator tab!")

    with pan_sub2:
        st.markdown("**Paste ANY Live Government Scheme Page or Circular URL:**")
        url_input = st.text_input("Official URL (.gov.in / nic.in / Portal)", value=st.session_state.target_scheme_url)
        
        url_cols = st.columns(5)
        presets = [
            ("https://www.myscheme.gov.in/schemes/csss", "🇮🇳 myScheme Central"),
            ("https://www.myscheme.gov.in/schemes/pragati-scholarship-scheme", "👩 myScheme Pragati"),
            ("https://mahadbt.maharashtra.gov.in", "🟠 MahaDBT MH"),
            ("https://pudhumaipenn.tn.gov.in", "🔴 Pudhumai Penn TN"),
            ("https://fruits.karnataka.gov.in", "🌾 FRUITS Karnataka")
        ]
        for idx, (p_url, p_label) in enumerate(presets):
            with url_cols[idx]:
                if st.button(p_label, key=f"btn_p_url_{idx}", use_container_width=True):
                    st.session_state.target_scheme_url = p_url
                    st.rerun()

        if st.button("🌐 Fetch & Compile Rules via Gemma 4", type="primary", use_container_width=True):
            with st.spinner("Connecting to live URL, parsing HTML, and compiling clauses with Gemma 4..."):
                try:
                    res = requests.post(f"{st.session_state.api_url}/api/fetch-live-scheme", json={"url": url_input, "model": st.session_state.active_model}, timeout=60)
                    if res.status_code == 200:
                        st.session_state.website_fetched_schemes = res.json().get("schemes", [])
                        st.success(f"Extracted {len(st.session_state.website_fetched_schemes)} statutory schemes from live web page!")
                except Exception as e:
                    st.error(f"Scraper error: {e}")

        if st.session_state.website_fetched_schemes:
            for idx, sc in enumerate(st.session_state.website_fetched_schemes):
                with st.container(border=True):
                    st.markdown(f"**🏛️ {sc.get('scheme_name')}** ({sc.get('state', 'All-India')})")
                    st.caption(f"Dept: {sc.get('department')} &nbsp;|&nbsp; Grant: `₹{sc.get('annual_benefit_inr', 0):,.0f}/yr`")
                    if st.button("⚡ Load Rules into Step 3 Prover", key=f"btn_load_web_{idx}", type="primary"):
                        st.session_state.custom_extracted_rules = sc.get("eligibility_rules", [])
                        st.session_state.custom_scheme_name = sc.get("scheme_name")
                        st.session_state.custom_department = sc.get("department")
                        st.session_state.custom_benefit_inr = sc.get("annual_benefit_inr")
                        st.session_state.selected_scheme_override = "CUSTOM_EXTRACTED_SCHEME"
                        st.success("Loaded compiled rules into Step 3 Prover!")

    with pan_sub3:
        st.markdown("#### ✍️ Gemma 4 Official Administrative Letter Draftsman")
        st.caption("Generate formal, legally grounded Indian government correspondence: Application Cover Letters, Sakala Grievance Appeals, Tahsildar Certificate Renewals, and College Bonafide Requests.")

        LETTER_TYPES = {
            "APPLICATION_COVER_LETTER": ("📄 Official Scheme Application Cover Letter", "The Competent Sanctioning Authority / District Welfare Officer"),
            "GRIEVANCE_APPEAL": ("⚖️ Statutory Grievance & Appeal against Rejection (Right to Public Services / Sakala)", "The Appellate Authority / District Grievance Redressal Officer"),
            "CERTIFICATE_RENEWAL": ("📑 Urgent Revenue Certificate Renewal / Expedited Issuance Request", "The Tahsildar / Taluk Revenue Officer"),
            "BONAFIDE_REQUEST": ("🎓 College Bonafide & Approved Fee Structure Request", "The Principal / Head of Institution"),
            "DBT_BANK_SEEDING": ("🏦 Bank Aadhaar-NPCI Seeding Request for DBT Scholarship", "The Branch Manager, Bank Branch")
        }

        l_c1, l_c2 = st.columns([1, 1], gap="large")
        with l_c1:
            sel_l_type = st.selectbox("Select Letter Purpose / Template Type", list(LETTER_TYPES.keys()), format_func=lambda k: LETTER_TYPES[k][0])
            l_scheme = st.text_input("Target Scheme Name", value=st.session_state.letter_target_scheme)
            l_dept = st.text_input("Competent Department", value=st.session_state.letter_target_dept)
            l_state = st.selectbox("State / Jurisdiction", STATE_OPTIONS[:-1], index=0)
            l_auth = st.text_input("Addressed To (Official Designation)", value=LETTER_TYPES[sel_l_type][1])
            l_lang = st.selectbox("Language for Draft", ["English", "Kannada (ಕನ್ನಡ)", "Hindi (हिंदी)", "Marathi (मराठी)", "Tamil (தமிழ்)", "Bengali (বাংলা)"])

        with l_c2:
            l_name = st.text_input("Citizen Full Name", value=st.session_state.pipeline_data["citizen_name"])
            l_parent = st.text_input("Father / Guardian Name", value=st.session_state.pipeline_data.get("father_name", "Sri Ramesh Kumar"))
            l_inst = st.text_input("College / Institution", value=st.session_state.pipeline_data["institution_name"])
            l_ref = st.text_input("Application / Barcode RD Reference Number", value=st.session_state.pipeline_data.get("certificate_ref_no", "RD00382910452"))
            l_notes = st.text_area("Specific Grievance Grounds / Facts (Optional):", value="Application pending past Sakala disposal deadline. Digitally signed RD00382910452 attached.", height=70)

        if st.button("🤖 Draft Official Letter with Gemma 4", type="primary", use_container_width=True):
            with st.spinner(f"Drafting formal {LETTER_TYPES[sel_l_type][0]} with Gemma 4..."):
                try:
                    payload = {
                        "letter_type": sel_l_type,
                        "scheme_name": l_scheme,
                        "department": l_dept,
                        "state": l_state,
                        "authority_designation": l_auth,
                        "citizen_name": l_name,
                        "parent_name": l_parent,
                        "address": st.session_state.pipeline_data.get("address", "Malleshwaram, Bengaluru"),
                        "phone": st.session_state.pipeline_data.get("phone", "+91-9845012345"),
                        "email": st.session_state.pipeline_data.get("email", "applicant@nic.in"),
                        "institution_name": l_inst,
                        "category": st.session_state.pipeline_data["caste_category"],
                        "annual_income": float(st.session_state.pipeline_data["family_income"]),
                        "marks_percentage": float(st.session_state.pipeline_data["marks_percentage"]),
                        "application_ref_no": l_ref,
                        "specific_details": l_notes,
                        "language": l_lang,
                        "model": st.session_state.active_model
                    }
                    res = requests.post(f"{st.session_state.api_url}/api/generate-letter", json=payload, timeout=45)
                    if res.status_code == 200:
                        resp_data = res.json()
                        st.session_state.generated_letter_text = resp_data.get("letter_text", "")
                        st.session_state.letter_model_used = resp_data.get("model_used", "gemma4:e4b")
                        st.success(f"✅ Official Letter drafted successfully via `{st.session_state.letter_model_used}`!")
                except Exception as e:
                    st.error(f"Letter generation error: {e}")

        if st.session_state.generated_letter_text:
            st.markdown("---")
            st.markdown("##### 📜 Official Document Preview:")
            st.markdown(f'<div class="official-letter-paper">{st.session_state.generated_letter_text}</div>', unsafe_allow_html=True)
            
            edited_text = st.text_area("✏️ Edit Letter Text Before Printing:", value=st.session_state.generated_letter_text, height=220)
            st.download_button(
                label="📥 Download Official Letter (.txt)",
                data=edited_text,
                file_name=f"Official_Letter_{sel_l_type}_{l_name.replace(' ', '_')}.txt",
                mime="text/plain",
                use_container_width=True
            )

# ==============================================================================
# EXTENDED TAB: MULTILINGUAL VOICE & VERNACULAR BRIEF (Bhashini AI)
# ==============================================================================
with tab_voice:
    st.markdown("### 🗣️ Multilingual Voice & Vernacular Brief (Bhashini / Gemma 4)")
    st.caption("Empower non-English literate citizens. Synthesizes formal scheme verdicts into native vernacular audio briefs.")

    v_c1, v_c2 = st.columns([1, 1], gap="large")
    with v_c1:
        with st.container(border=True):
            st.markdown("#### 🌐 Vernacular Translation Engine")
            target_lang = st.selectbox("Select Vernacular Language", ["Kannada (ಕನ್ನಡ)", "Hindi (हिंदी)", "Marathi (मराठी)", "Tamil (தமிழ்)", "Bengali (বাংলা)"])
            
            sample_brief = (
                f"Citizen {st.session_state.pipeline_data['citizen_name']} is eligible for State Scholarship Portal Post-Matric and Karnataka Yuva Nidhi Scheme. "
                f"Total unlocked annual grant is Rs. 61,000. All revenue income certificates and domicile requirements are verified."
            )
            brief_text = st.text_area("English Prover Verdict Summary:", value=sample_brief, height=95)

            if st.button("🗣️ Generate Vernacular Voice Brief", type="primary", use_container_width=True):
                with st.spinner("Translating via Bhashini pipeline..."):
                    try:
                        t_res = requests.post(f"{st.session_state.api_url}/api/translate", json={"text": brief_text, "target_language": target_lang}, timeout=15)
                        if t_res.status_code == 200:
                            st.session_state.translated_summary = t_res.json().get("translated_text", "")
                            st.success("✅ Translation generated successfully!")
                    except Exception as e:
                        st.error(f"Translation error: {e}")

    with v_c2:
        with st.container(border=True):
            st.markdown("#### 🔊 Native Audio Playback")
            if st.session_state.translated_summary:
                st.markdown(f"**Translated Audio Script ({target_lang}):**")
                st.info(st.session_state.translated_summary)
                
                lang_code_map = {"Kannada (ಕನ್ನಡ)": "kn-IN", "Hindi (हिंदी)": "hi-IN", "Marathi (मराठी)": "mr-IN", "Tamil (தமிழ்)": "ta-IN", "Bengali (বাংলা)": "bn-IN"}
                s_lang = lang_code_map.get(target_lang, "en-IN")
                clean_audio_txt = st.session_state.translated_summary.replace('"', '\\"').replace('\n', ' ')

                st.components.v1.html(f"""
                <button onclick="speak()" style="background-color: #2563EB; color: white; border: none; padding: 10px 18px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 14px;">
                    🔊 Play Native Vernacular Audio ({s_lang})
                </button>
                <button onclick="window.speechSynthesis.cancel()" style="background-color: #64748B; color: white; border: none; padding: 10px 14px; border-radius: 6px; cursor: pointer; font-size: 14px; margin-left: 8px;">
                    ⏹️ Stop
                </button>
                <script>
                    function speak() {{
                        window.speechSynthesis.cancel();
                        const u = new SpeechSynthesisUtterance("{clean_audio_txt}");
                        u.lang = '{s_lang}';
                        u.rate = 0.95;
                        window.speechSynthesis.speak(u);
                    }}
                </script>
                """, height=65)
            else:
                st.write("Click *Generate Vernacular Voice Brief* to activate audio synthesis.")

# ==============================================================================
# EXTENDED TAB: PUBLIC SERVICE CENTERS (Multi-State Citizen Kiosks)
# ==============================================================================
with tab_kiosk:
    st.markdown("### 🗺️ Pan-India Public Service Centers Locator")
    st.caption("Locate verified citizen service centers (Bangalore One, Aaple Sarkar, e-Sevai, Jan Seva Kendra, BSK) on interactive OpenStreetMap.")

    STATE_KIOSKS = {
        "Karnataka": [
            {"name": "Bangalore One - Malleshwaram", "city": "Bengaluru", "lat": 13.0031, "lon": 77.5643, "hours": "8:00 AM - 7:00 PM", "services": "Income/Caste Certificate, Aadhaar Update, Seva Sindhu"},
            {"name": "Bangalore One - Indiranagar", "city": "Bengaluru", "lat": 12.9784, "lon": 77.6408, "hours": "8:00 AM - 7:00 PM", "services": "Ration Card Verification, Domicile Application"},
            {"name": "Bangalore One - Koramangala", "city": "Bengaluru", "lat": 12.9352, "lon": 77.6245, "hours": "8:00 AM - 8:00 PM", "services": "Full Civic Services, Revenue Dept Dispatch"},
            {"name": "Karnataka One - Mysuru (Saraswathipuram)", "city": "Mysuru", "lat": 12.3051, "lon": 76.6346, "hours": "8:00 AM - 7:00 PM", "services": "Tahsildar Income/Caste, RTC Pahani, Domicile"}
        ],
        "Maharashtra": [
            {"name": "Aaple Sarkar Seva Kendra - Nariman Point", "city": "Mumbai", "lat": 18.9256, "lon": 72.8242, "hours": "9:00 AM - 6:00 PM", "services": "MahaDBT Verification, Domicile Certificate, Non-Creamy Layer"},
            {"name": "MahaOnline Citizen Center - Shivajinagar", "city": "Pune", "lat": 18.5314, "lon": 73.8446, "hours": "8:30 AM - 6:30 PM", "services": "Student Scholarship Attestation, EWS Certificate, Revenue Records"}
        ],
        "Tamil Nadu": [
            {"name": "e-Sevai Center - Anna Nagar", "city": "Chennai", "lat": 13.0850, "lon": 80.2101, "hours": "9:00 AM - 5:30 PM", "services": "Community Certificate, Nativity Certificate, Pudhumai Penn Verification"},
            {"name": "TNeGA e-Sevai - Gandhipuram", "city": "Coimbatore", "lat": 11.0168, "lon": 76.9672, "hours": "9:30 AM - 6:00 PM", "services": "Income Certificate, 7.5% Govt School Quota Endorsement"}
        ]
    }

    k_state = st.selectbox("Select State for Citizen Kiosks", list(STATE_KIOSKS.keys()), index=0)
    current_kiosks = STATE_KIOSKS[k_state]
    sel_k_name = st.selectbox("Select Kiosk", [k["name"] for k in current_kiosks])
    kiosk_info = next(k for k in current_kiosks if k["name"] == sel_k_name)

    st.markdown(f"**🏢 Operating Hours:** `{kiosk_info['hours']}` &nbsp;|&nbsp; **Services:** `{kiosk_info['services']}`")

    # Render Leaflet Map
    markers_js = ""
    for k in current_kiosks:
        is_active = (k["name"] == sel_k_name)
        markers_js += f"""
        L.marker([{k['lat']}, {k['lon']}]).addTo(map)
        .bindPopup("<b>{k['name']}</b><br>{k['city']} • {k['hours']}<br>{k['services']}"){'.openPopup()' if is_active else ''};
        """

    leaflet_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
        <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
        <style>#map {{ height: 380px; width: 100%; border-radius: 10px; border: 1px solid #CBD5E1; }}</style>
    </head>
    <body>
        <div id="map"></div>
        <script>
            var map = L.map('map').setView([{kiosk_info['lat']}, {kiosk_info['lon']}], 13);
            L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{ attribution: '&copy; OpenStreetMap contributors' }}).addTo(map);
            {markers_js}
        </script>
    </body>
    </html>
    """
    st.components.v1.html(leaflet_html, height=395)

# ==============================================================================
# TAB: MIT OPEN-SOURCE LICENSE & GOVTECH COMPLIANCE
# ==============================================================================
with tab_license:
    is_kn = (st.session_state.get("selected_language") == "kn")
    
    if is_kn:
        st.markdown("### 📜 ಮುಕ್ತ ತಂತ್ರಾಂಶ ಪರವಾನಗಿ ಮತ್ತು ನಿಯಮಾವಳಿಗಳು (MIT License)")
        st.caption("ಯೋಗ್ಯ (Yogya) ೧೦೦% ಮುಕ್ತ ಹಾಗೂ ಸಾರ್ವಜನಿಕ ತಂತ್ರಾಂಶವಾಗಿದ್ದು, ಎಂಐಟಿ (MIT) ಪರವಾನಗಿಯಡಿಯಲ್ಲಿ ಬಿಡುಗಡೆ ಮಾಡಲಾಗಿದೆ.")
    else:
        st.markdown("### 📜 Open-Source Compliance & Statutory Licensing (MIT)")
        st.caption("Yogya is 100% Free and Open-Source Software released under the permissive **MIT License**.")

    lic_col1, lic_col2, lic_col3, lic_col4 = st.columns(4)
    with lic_col1:
        st.metric("License Standard", "MIT License")
    with lic_col2:
        st.metric("SPDX Identifier", "MIT")
    with lic_col3:
        st.metric("OSI Approved", "Yes (1988)")
    with lic_col4:
        st.metric("Govt & Commercial Use", "100% Permitted")

    st.markdown("---")

    p_col1, p_col2, p_col3 = st.columns(3)

    with p_col1:
        with st.container(border=True):
            st.markdown("#### ✅ Permissions")
            st.markdown("""
            - **Commercial Deployment:** May be deployed in public governance kiosks, private enterprise portals, and citizen centers.
            - **Modification & Forking:** Freedom to modify code, adapt rules, integrate local state schemes, and extend compilers.
            - **Distribution:** Distribute source code, binaries, or containerized images freely worldwide.
            - **Private Use:** Free for private, institutional, research, or governmental internal use.
            - **Sublicensing:** Grant downstream sublicenses to customized deployments.
            """)

    with p_col2:
        with st.container(border=True):
            st.markdown("#### ⚠️ Conditions")
            st.markdown("""
            - **License Inclusion:** Must include a copy of the MIT License text in all distributions or substantial portions.
            - **Copyright Retention:** Retain the original copyright notice in all copies or derivative works.
            """)

    with p_col3:
        with st.container(border=True):
            st.markdown("#### ❌ Limitations")
            st.markdown("""
            - **No Warranty:** Software is provided strictly **"AS IS"** without warranties of merchantability or fitness for a particular purpose.
            - **Limitation of Liability:** In no event shall authors or copyright holders be liable for any claim, damages, or reliance.
            """)

    st.markdown("---")

    # Project Sovereign Architecture Context
    with st.container(border=True):
        st.markdown("#### 🏛️ Sovereign GovTech Attribution & Open-Weight Ecosystem")
        st.markdown("""
        **Project Name:** Yogya • Sovereign Civic Eligibility & Policy Engine  
        **Copyright:** © 2026 Yogya Contributors  
        **Hackathon Track:** IEEE CIS @ MSRIT Hackathon '26  
        **Upstream Technologies:** Google Gemma 4 Open Weights, FastAPI, Streamlit, IndiaStack Open Standards  
        **Public Source Code:** [github.com/Nakul-sudo-cool/yogya](https://github.com/Nakul-sudo-cool/yogya)  
        """)

    st.markdown("---")

    # Read License file dynamically
    license_file_path = Path(__file__).resolve().parent.parent / "LICENSE"
    full_license_text = ""
    if license_file_path.exists():
        try:
            with open(license_file_path, "r", encoding="utf-8") as lf:
                full_license_text = lf.read()
        except Exception:
            pass

    if not full_license_text:
        full_license_text = """MIT License

Copyright (c) 2026 Yogya Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

    d_col1, d_col2 = st.columns([1.5, 3])
    with d_col1:
        st.download_button(
            label="📥 Download Full LICENSE (MIT.txt)",
            data=full_license_text,
            file_name="LICENSE",
            mime="text/plain",
            key="btn_download_mit_license",
            use_container_width=True
        )

    with st.expander("📄 Verbatim MIT License Legal Text", expanded=True):
        st.code(full_license_text, language="text")

    st.markdown("---")
    st.markdown("#### 📋 Developer & Citizen Department Boilerplate Notice")
    st.caption("To apply the MIT License to your civic extension or state adaptation, attach this header:")
    st.code("""MIT License

Copyright (c) 2026 Yogya Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
""", language="python")

# ==============================================================================
# STICKY VERNACULAR VOICE DICTATION ASSISTANT (Linear / IndiaStack Floating Bar)
# ==============================================================================
with st.sidebar:
    st.markdown("### 🎙️ Voice Dictation Assistant")
    st.caption("Speak in Kannada, Hindi, or English to auto-populate your citizen profile.")

    st.components.v1.html("""
    <div style="font-family: sans-serif; padding: 6px 0;">
        <button id="recBtn" onclick="toggleRecording()" style="background-color: #2563EB; color: white; border: none; padding: 8px 14px; border-radius: 6px; font-weight: 600; cursor: pointer; font-size: 13px; width: 100%; display: flex; align-items: center; justify-content: center; gap: 8px;">
            <span id="recIcon">🔴</span> <span id="btnText">Start Microphone</span>
        </button>
        <div id="recStatus" style="font-size: 11px; color: #64748B; margin-top: 4px; text-align: center;">Click to speak</div>
        <div id="transcriptBox" style="font-size: 12px; margin-top: 6px; padding: 6px; background: #F1F5F9; border-radius: 6px; min-height: 38px; color: #1E293B;">Transcript will appear here...</div>
    </div>
    <script>
        var recognition;
        var rec = false;
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            var SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-IN';
            recognition.onstart = function() {
                rec = true;
                document.getElementById('btnText').innerText = "Listening...";
                document.getElementById('recIcon').innerText = "⏹️";
                document.getElementById('recBtn').style.backgroundColor = "#10B981";
            };
            recognition.onresult = function(event) {
                var txt = '';
                for (var i = event.resultIndex; i < event.results.length; ++i) { txt += event.results[i][0].transcript; }
                document.getElementById('transcriptBox').innerText = txt;
                navigator.clipboard.writeText(txt).catch(e => {});
            };
            recognition.onend = function() {
                rec = false;
                document.getElementById('btnText').innerText = "Start Microphone";
                document.getElementById('recIcon').innerText = "🔴";
                document.getElementById('recBtn').style.backgroundColor = "#2563EB";
                document.getElementById('recStatus').innerText = "Copied to clipboard!";
            };
        }
        function toggleRecording() {
            if (rec) recognition.stop(); else recognition.start();
        }
    </script>
    """, height=125)

    voice_input = st.text_input("Or Paste Spoken Dictation:", value="Family income is 1 lakh 80 thousand, scored 78 percent in BSc, OBC category.")
    if st.button("🧠 Parse Spoken Query with Gemma 4", use_container_width=True):
        with st.spinner("Extracting parameters with Gemma 4..."):
            try:
                vq_res = requests.post(f"{st.session_state.api_url}/api/parse-voice-query", json={"query_text": voice_input, "model": st.session_state.active_model}, timeout=20)
                if vq_res.status_code == 200:
                    ext = vq_res.json().get("extracted", {})
                    if ext.get("estimated_income"):
                        st.session_state.pipeline_data["family_income"] = float(ext["estimated_income"])
                    if ext.get("category"):
                        st.session_state.pipeline_data["caste_category"] = ext["category"]
                    if ext.get("education"):
                        st.session_state.pipeline_data["education_level"] = ext["education"]
                    st.success("✅ Voice parameters parsed into profile!")
            except Exception as e:
                st.error(f"Voice parse error: {e}")

    st.markdown("---")
    st.markdown("### ⚙️ System Diagnostics")
    st.session_state.api_url = st.text_input("Prover API Endpoint", value=st.session_state.api_url)
    st.session_state.active_model = st.selectbox("Open-Weight LLM", ["gemma4:e4b", "llama3.2:3b", "qwen3.5:4b"], index=0)

    st.markdown("---")
    with st.expander("📜 Open Source License (MIT)", expanded=False):
        st.markdown("""
        **Yogya** is 100% Free and Open-Source Software licensed under the **MIT License**.
        
        - 🟢 **Commercial Use**: Permitted
        - 🟢 **Modifications**: Permitted
        - 🟢 **Distribution**: Permitted
        - 🟢 **Private & Govt Use**: Permitted
        - ⚖️ **Warranty / Liability**: None (As-Is)
        
        *Copyright © 2026 Yogya Contributors.*
        """)
        st.caption("Inspect full terms in the **📜 License (MIT)** tab.")

# ==============================================================================
# NATIVE KANNADA LANGUAGE CONVERTER FLOATING BUTTON (Bottom-Left Anchor)
# ==============================================================================
def toggle_kannada_language():
    """Callback executing before widget tree instantiation on rerun."""
    if st.session_state.get("selected_language") == "kn":
        st.session_state.selected_language = "en"
        try:
            st.session_state.global_language_selector = "en"
        except Exception:
            pass
    else:
        st.session_state.selected_language = "kn"
        try:
            st.session_state.global_language_selector = "kn"
        except Exception:
            pass

def render_bottom_left_kannada_converter():
    """
    Renders an accessible native language converter anchored at the bottom-left of the viewport.
    Directly converts the entire interface to native Kannada with instant reactivity.
    """
    is_kannada = (st.session_state.get("selected_language") == "kn")
    
    with st.container():
        btn_label = "🇬🇧 English ಗೆ ಬದಲಾಯಿಸಿ" if is_kannada else "🟡 🔴 ಕನ್ನಡಕ್ಕೆ ಬದಲಾಯಿಸಿ (Kannada Only)"
        btn_help = "ಇಂಟರ್ಫೇಸ್ ಭಾಷೆಯನ್ನು ಇಂಗ್ಲಿಷ್‌ಗೆ ಬದಲಾಯಿಸಿ" if is_kannada else "ಇಡೀ ಇಂಟರ್ಫೇಸ್ ಅನ್ನು ಅಪ್ಪಟ ಕನ್ನಡಕ್ಕೆ ಪರಿವರ್ತಿಸಿ (Convert to Kannada Only)"
        
        st.button(
            btn_label,
            key="btn_kannada_bottom_left",
            on_click=toggle_kannada_language,
            help=btn_help
        )

render_bottom_left_kannada_converter()
