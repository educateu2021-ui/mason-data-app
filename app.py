import streamlit as st
import pandas as pd
from io import BytesIO
from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials

# ------------ CONFIG ------------

st.set_page_config(page_title="Mason Data Manager", layout="wide")

# 🔗 GOOGLE SHEET CONFIG
GOOGLE_SHEET_ID = "1JEAVT5DusNCw5kYaClvAPkA6_AtRJa0p46nS3r0vEKs"
SHEET_TAB_NAME = "Master"  # change if your tab name is different

# ------------ GOOGLE SHEETS HELPERS ------------

def get_gsheet_client():
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"], scopes=scopes
    )
    return gspread.authorize(creds)

def read_sheet(sheet_id: str, tab: str = SHEET_TAB_NAME) -> pd.DataFrame:
    gc = get_gsheet_client()
    sh = gc.open_by_key(sheet_id)
    ws = sh.worksheet(tab)
    data = ws.get_all_records()
    return pd.DataFrame(data)

def write_sheet(sheet_id: str, df: pd.DataFrame, tab: str = SHEET_TAB_NAME):
    gc = get_gsheet_client()
    sh = gc.open_by_key(sheet_id)
    try:
        ws = sh.worksheet(tab)
    except gspread.exceptions.WorksheetNotFound:
        ws = sh.add_worksheet(title=tab, rows="5000", cols="30")

    ws.clear()

    if df.empty:
        return

    values = [df.columns.tolist()] + df.astype(str).values.tolist()
    ws.update(values)

def save_monthly_snapshot():
    month_tab = datetime.now().strftime("%Y_%b")  # e.g. 2025_Nov
    write_sheet(GOOGLE_SHEET_ID, st.session_state["data"], month_tab)
    st.success(f"Monthly report saved to tab: {month_tab}")

# ------------ HEADER ------------

st.markdown(
    """
    <header class="mde-header">
        <div class="mde-header-inner">
            <h1 class="mde-title">Mason Data Explorer</h1>
            <div class="mde-header-right">
                <span class="mde-header-tag">Field Visit & Registration Tracker</span>
            </div>
        </div>
    </header>
    """,
    unsafe_allow_html=True,
)

# ------------ GLOBAL CSS (theme) ------------

st.markdown("""
<style>
/* Page & layout */
body {
    background-color: #f1f5f9;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.block-container {
    padding-top: 1.5rem;
    max-width: 1200px;
}

/* Header */
.mde-header {
    width: 100%;
    background: #ffffff;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
    margin-bottom: 1rem;
}
.mde-header-inner {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0.8rem 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
}
.mde-title {
    font-size: 1.7rem;
    font-weight: 800;
    color: #4338ca;
    margin: 0;
}
.mde-header-right {
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.mde-header-tag {
    font-size: 0.75rem;
    padding: 0.3rem 0.6rem;
    border-radius: 999px;
    background: #eef2ff;
    color: #4f46e5;
    font-weight: 600;
}

/* Expander like card */
[data-testid="stExpander"] {
    border-radius: 0.75rem;
    border: 1px solid #e5e7eb;
    box-shadow: 0 10px 15px rgba(15, 23, 42, 0.04);
    background: #ffffff;
}

/* Filter section labels */
.mde-label {
    font-size: 0.8rem;
    font-weight: 600;
    color: #6b7280;
    margin-bottom: 0.15rem;
    display: flex;
    align-items: center;
    gap: 0.35rem;
}
.mde-label span.icon {
    font-size: 0.9rem;
}

/* Give widgets rounded look */
div[data-baseweb="select"] > div,
.stSelectbox > div > div {
    border-radius: 0.5rem;
}
.stTextInput > div > div input {
    border-radius: 0.5rem;
}

/* Buttons */
div.stButton > button {
    border-radius: 0.5rem;
    padding: 0.45rem 0.9rem;
    font-weight: 600;
}

/* Metric cards (KPIs) */
[data-testid="metric-container"] {
    background: #ffffff;
    border-radius: 0.85rem;
    padding: 0.75rem 0.9rem;
    box-shadow: 0 8px 16px rgba(15, 23, 42, 0.04);
    border: 1px solid #e5e7eb;
}
[data-testid="stMetricLabel"] > div {
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #6b7280;
}
[data-testid="stMetricValue"] {
    font-size: 1.9rem;
    font-weight: 800;
    color: #4f46e5;
}

/* Chart cards */
.mde-chart-card {
    background: #ffffff;
    border-radius: 0.85rem;
    padding: 1rem;
    box-shadow: 0 10px 15px rgba(15, 23, 42, 0.05);
    border: 1px solid #e5e7eb;
}
.mde-chart-title {
    font-size: 0.95rem;
    font-weight: 600;
    text-align: center;
    margin-bottom: 0.5rem;
    color: #334155;
}

/* Scrollbar */
::-webkit-scrollbar { width: 8px; height: 8px; }
::-webkit-scrollbar-track { background: #f1f5f9; }
::-webkit-scrollbar-thumb { background: #cbd5f5; border-radius: 4px; }
::-webkit-scrollbar-thumb:hover { background: #a5b4fc; }
</style>
""", unsafe_allow_html=True)

# Optional Tailwind JS
st.markdown('<script src="https://cdn.tailwindcss.com"></script>', unsafe_allow_html=True)

# ------------ HELPERS ------------

def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [str(c).strip() for c in df.columns]
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df = df.fillna("")
    if "S.NO" in df.columns:
        df["S.NO"] = pd.to_numeric(df["S.NO"], errors="coerce").fillna(0).astype(int)
    return df

def get_template_excel() -> bytes:
    columns = [
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER",
        "DLR NAME", "Location", "DAY", "Category",
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other",
        "Visited_Status", "Visited_At", "Registered_Status", "Registered_At"
    ]
    df_template = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df_template.to_excel(writer, index=False, sheet_name="Template")
    return output.getvalue()

def load_excel_data(uploaded_file) -> pd.DataFrame | None:
    try:
        df = pd.read_excel(uploaded_file)
        return clean_dataframe(df)
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def save_state_for_undo():
    st.session_state["prev_data"] = st.session_state["data"].copy()

def to_excel(df: pd.DataFrame) -> bytes:
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="MasonData")
    return output.getvalue()

def get_initial_dataset() -> pd.DataFrame:
    try:
        df = read_sheet(GOOGLE_SHEET_ID, SHEET_TAB_NAME)
        if df.empty:
            raise ValueError("Empty sheet")
        return clean_dataframe(df)
    except Exception as e:
        st.warning(f"No data found in Google Sheet or error loading it. Starting with empty dataset. ({e})")
        df = pd.DataFrame(columns=[
            "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER",
            "DLR NAME", "Location", "DAY", "Category",
            "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other",
            "Visited_Status", "Visited_At", "Registered_Status", "Registered_At"
        ])
        return df

# ------------ SESSION STATE INIT ------------

if "data" not in st.session_state:
    st.session_state["data"] = get_initial_dataset()

if "prev_data" not in st.session_state:
    st.session_state["prev_data"] = None

# Ensure status columns exist even for older files
for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At"]:
    if col not in st.session_state["data"].columns:
        st.session_state["data"][col] = ""

# Filter-related session defaults
defaults = {
    "filter_day": "All",
    "filter_location": "All",
    "filter_cat": "All",
    "filter_visit_status": "All",
    "filter_reg_status": "All",
    "filter_mobile_input": "",
    "filter_mobile_query": "",
    "filter_only_products": False,
    "filter_no_products": False,
    "reset_filters": False,
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Apply reset BEFORE widgets render
if st.session_state.get("reset_filters", False):
    for k, v in defaults.items():
        st.session_state[k] = v
    st.session_state["reset_filters"] = False

# ------------ INLINE UPDATE FUNCTION FOR CARDS ------------

def update_entry(sno: int, column_name: str, widget_key: str, is_checkbox: bool = False):
    """Update one field from card widgets and push to Google Sheets."""
    df = st.session_state["data"]
    if "S.NO" not in df.columns:
        return

    mask = df["S.NO"] == sno
    if not mask.any():
        return

    if is_checkbox:
        val = bool(st.session_state.get(widget_key, False))
        df.loc[mask, column_name] = "YES" if val else ""
    else:
        val = st.session_state.get(widget_key, "")
        df.loc[mask, column_name] = val

    st.session_state["data"] = df
    write_sheet(GOOGLE_SHEET_ID, df.copy(), SHEET_TAB_NAME)

# ------------ DATA MANAGEMENT EXPANDER ------------

with st.expander("🛠️ Data Management (Import / Add / Undo)", expanded=False):

    # Undo
    if st.session_state["prev_data"] is not None:
        if st.button("↩️ Undo Last Change", type="primary"):
            st.session_state["data"] = st.session_state["prev_data"]
            st.session_state["prev_data"] = None
            write_sheet(GOOGLE_SHEET_ID, st.session_state["data"], SHEET_TAB_NAME)
            st.success("Restored previous version!")
            st.rerun()

    op_tab1, op_tab2, op_tab3 = st.tabs(["➕ Add Single Entry", "📂 Import Excel", "📅 Monthly Snapshot"])

    # --- IMPORT TAB ---
    with op_tab2:
        col1, col2 = st.columns(2)
        with col1:
            st.info("Step 2: Upload Data")
            uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])
            if uploaded_file is not None:
                if st.button("Load Data"):
                    new_data = load_excel_data(uploaded_file)
                    if new_data is not None:
                        save_state_for_undo()
                        st.session_state["data"] = new_data
                        for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At"]:
                            if col not in st.session_state["data"].columns:
                                st.session_state["data"][col] = ""
                        write_sheet(GOOGLE_SHEET_ID, st.session_state["data"], SHEET_TAB_NAME)
                        st.success(f"Loaded {len(new_data)} rows and saved to Google Sheet!")
                        st.rerun()

    # --- ADD ENTRY TAB ---
    with op_tab1:
        with st.form("entry_form"):
            c1, c2, c3 = st.columns(3)
            with c1:
                mason_code = st.text_input("Mason Code", key="form_mason_code")
            with c2:
                mason_name = st.text_input("Mason Name", key="form_mason_name")
            with c3:
                contact_number = st.text_input("Contact Number", key="form_contact_number")

            c4, c5, c6, c7 = st.columns(4)
            with c4:
                dlr_name = st.text_input("DLR Name", key="form_dlr_name")
            with c5:
                location = st.text_input("Location", key="form_location")
            with c6:
                day = st.selectbox(
                    "Day",
                    ["MONDAY", "TUESDAY", "WEDNESDAY",
                     "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"],
                    key="form_day",
                )
            with c7:
                category = st.selectbox("Category", ["E", "M", "Other"], key="form_category")

            st.write("**Products (Check box for YES)**")
            pc1, pc2, pc3, pc4, pc5, pc6 = st.columns(6)
            with pc1:
                hw305 = st.checkbox("HW305", key="form_hw305")
            with pc2:
                hw101 = st.checkbox("HW101", key="form_hw101")
            with pc3:
                hw201 = st.checkbox("Hw201", key="form_hw201")
            with pc4:
                hw103 = st.checkbox("HW103", key="form_hw103")
            with pc5:
                hw302 = st.checkbox("HW302", key="form_hw302")
            with pc6:
                hw310 = st.checkbox("HW310", key="form_hw310")

            other_notes = st.text_input("Other / Remarks", key="form_other")
            submitted = st.form_submit_button("Add Line Item")

            if submitted:
                if not mason_name:
                    st.error("Mason Name is required!")
                else:
                    save_state_for_undo()
                    if "S.NO" in st.session_state["data"].columns and not st.session_state["data"].empty:
                        new_sno = st.session_state["data"]["S.NO"].max() + 1
                    else:
                        new_sno = 1

                    new_row = {
                        "S.NO": new_sno,
                        "MASON CODE": mason_code,
                        "MASON NAME": mason_name,
                        "CONTACT NUMBER": contact_number,
                        "DLR NAME": dlr_name,
                        "Location": location,
                        "DAY": day,
                        "Category": category,
                        "HW305": "YES" if hw305 else "",
                        "HW101": "YES" if hw101 else "",
                        "Hw201": "YES" if hw201 else "",
                        "HW103": "YES" if hw103 else "",
                        "HW302": "YES" if hw302 else "",
                        "HW310": "YES" if hw310 else "",
                        "other": other_notes,
                        "Visited_Status": "",
                        "Visited_At": "",
                        "Registered_Status": "",
                        "Registered_At": "",
                    }

                    st.session_state["data"] = pd.concat(
                        [st.session_state["data"], pd.DataFrame([new_row])],
                        ignore_index=True,
                    )
                    write_sheet(GOOGLE_SHEET_ID, st.session_state["data"], SHEET_TAB_NAME)

                    # CLEAR FORM FIELDS
                    for key in [
                        "form_mason_code", "form_mason_name", "form_contact_number",
                        "form_dlr_name", "form_location", "form_other"
                    ]:
                        st.session_state[key] = ""
                    for key in ["form_hw305", "form_hw101", "form_hw201", "form_hw103", "form_hw302", "form_hw310"]:
                        st.session_state[key] = False
                    st.session_state["form_day"] = "MONDAY"
                    st.session_state["form_category"] = "E"

                    st.success("Entry added & saved to Google Sheet!")
                    st.rerun()

        with col2:
            st.info("Step 1: Download Template")
            st.download_button(
                label="📄 Download Blank Excel Template",
                data=get_template_excel(),
                file_name="mason_data_template.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

    # --- MONTHLY SNAPSHOT TAB ---
    with op_tab3:
        st.info("Save the current data as a monthly snapshot sheet in the same Google Sheet.")
        if st.button("📅 Save Monthly Report to Google Sheet"):
            save_monthly_snapshot()

# ------------ FILTER SECTION ------------

with st.expander("🔍 Filter Data", expanded=True):
    base_df = st.session_state["data"].copy()

    # --- FIRST ROW: Day, Location, Category, Product flags ---
    fc1, fc2, fc3, fc4 = st.columns(4)

    with fc1:
        st.markdown('<div class="mde-label"><span class="icon">📅</span>Day</div>', unsafe_allow_html=True)
        days_list = [
            str(x).strip()
            for x in base_df.get("DAY", "").unique()
            if str(x).strip()
        ]
        days = ["All"] + sorted(set(days_list))
        selected_day = st.selectbox(
            "",
            days,
            key="filter_day",
        )

    df_for_location = base_df.copy()
    if selected_day != "All":
        df_for_location = df_for_location[df_for_location["DAY"] == selected_day]

    with fc2:
        st.markdown('<div class="mde-label"><span class="icon">📍</span>Location</div>', unsafe_allow_html=True)
        locs = [
            str(x).strip()
            for x in df_for_location.get("Location", "").unique()
            if str(x).strip()
        ]
        locations = ["All"] + sorted(set(locs))
        selected_location = st.selectbox(
            "",
            locations,
            key="filter_location",
        )

    df_for_category = df_for_location.copy()
    if selected_location != "All":
        df_for_category = df_for_category[df_for_category["Location"] == selected_location]

    with fc3:
        st.markdown('<div class="mde-label"><span class="icon">🏷️</span>Category</div>', unsafe_allow_html=True)
        cats_raw = [
            str(x).strip()
            for x in df_for_category.get("Category", "").unique()
            if str(x).strip() != ""
        ]
        cats = ["All"] + sorted(set(cats_raw))
        has_blank = (df_for_category.get("Category", "") == "").any()
        if has_blank:
            cats.append("Blank / Uncategorized")

        selected_cat = st.selectbox(
            "",
            cats,
            key="filter_cat",
        )

    with fc4:
        st.markdown('<div class="mde-label"><span class="icon">📦</span>Product Visibility</div>', unsafe_allow_html=True)
        show_only_products = st.checkbox(
            "Has Products",
            key="filter_only_products",
        )
        show_no_products = st.checkbox(
            "No Products",
            key="filter_no_products",
        )

    vc1, vc2 = st.columns(2)
    with vc1:
        st.markdown('<div class="mde-label"><span class="icon">🧭</span>Visited Status</div>', unsafe_allow_html=True)
        visit_filter = st.selectbox(
            "",
            ["All", "Visited", "Not Visited"],
            key="filter_visit_status",
        )
    with vc2:
        st.markdown('<div class="mde-label"><span class="icon">📝</span>Registered Status</div>', unsafe_allow_html=True)
        reg_filter = st.selectbox(
            "",
            ["All", "Registered", "Not Registered"],
            key="filter_reg_status",
        )

    mc1, mc2, mc3 = st.columns([3, 1, 1])
    with mc1:
        st.markdown('<div class="mde-label"><span class="icon">📱</span>Search by Mobile Number</div>', unsafe_allow_html=True)
        st.session_state["filter_mobile_input"] = st.text_input(
            "",
            value=st.session_state.get("filter_mobile_input", ""),
            placeholder="Enter full or partial number...",
        )
    with mc2:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        if st.button("Search", key="btn_mobile_search"):
            st.session_state["filter_mobile_query"] = st.session_state["filter_mobile_input"].strip()
            st.rerun()
    with mc3:
        st.markdown("&nbsp;", unsafe_allow_html=True)
        if st.button("🔄 Reset Filters", key="btn_reset_filters"):
            st.session_state["reset_filters"] = True
            st.rerun()

# ------------ APPLY FILTERS ------------

df_display = st.session_state["data"].copy()

if not df_display.empty:
    selected_day = st.session_state.get("filter_day", "All")
    if selected_day != "All":
        df_display = df_display[df_display["DAY"] == selected_day]

    selected_location = st.session_state.get("filter_location", "All")
    if selected_location != "All":
        df_display = df_display[df_display["Location"] == selected_location]

    selected_cat = st.session_state.get("filter_cat", "All")
    if selected_cat == "Blank / Uncategorized":
        df_display = df_display[
            df_display["Category"].isna() | (df_display["Category"] == "")
        ]
    elif selected_cat != "All":
        df_display = df_display[df_display["Category"] == selected_cat]

    visit_filter = st.session_state.get("filter_visit_status", "All")
    if "Visited_Status" in df_display.columns:
        if visit_filter == "Visited":
            df_display = df_display[df_display["Visited_Status"] == "Visited"]
        elif visit_filter == "Not Visited":
            df_display = df_display[
                (df_display["Visited_Status"].isna()) |
                (df_display["Visited_Status"] == "")
            ]

    reg_filter = st.session_state.get("filter_reg_status", "All")
    if "Registered_Status" in df_display.columns:
        if reg_filter == "Registered":
            df_display = df_display[df_display["Registered_Status"] == "Registered"]
        elif reg_filter == "Not Registered":
            df_display = df_display[
                (df_display["Registered_Status"].isna()) |
                (df_display["Registered_Status"] == "")
            ]

    hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
    show_only_products = st.session_state.get("filter_only_products", False)
    show_no_products = st.session_state.get("filter_no_products", False)

    if show_only_products:
        mask = df_display[hw_cols].apply(
            lambda x: x.astype(str).str.contains("YES", case=False).any(), axis=1
        )
        df_display = df_display[mask]

    if show_no_products:
        mask = df_display[hw_cols].apply(
            lambda x: not x.astype(str).str.contains("YES", case=False).any(), axis=1
        )
        df_display = df_display[mask]

    mobile_query = st.session_state.get("filter_mobile_query", "")
    if mobile_query and "CONTACT NUMBER" in df_display.columns:
        contact_str = df_display["CONTACT NUMBER"].astype(str).str.replace(".0", "", regex=False)
        df_display = df_display[
            contact_str.str.contains(mobile_query, case=False, na=False)
        ]

# ------------ METRICS ------------

st.markdown("### 📊 Dashboard Overview")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Masons", len(st.session_state["data"]))
m2.metric("Visible Rows", len(df_display))
m3.metric(
    "Unique Locations (Filtered)",
    df_display["Location"].nunique() if "Location" in df_display.columns else 0,
)
m4.metric(
    "Unique DLRs (Filtered)",
    df_display["DLR NAME"].nunique() if "DLR NAME" in df_display.columns else 0,
)

st.divider()

# ------------ MAIN TABS ------------

tab_cards, tab_graphs, tab_data = st.tabs(
    ["📇 Mason Cards", "📈 Analytics", "📝 Data Editor"]
)

# ==========================================
#        EDITABLE CARDS SECTION
# ==========================================
with tab_cards:
    st.subheader("Mason Directory")
    st.info("💡 Tip: Click a card to expand. Any change you make inside is saved to Google Sheets automatically.")

    if df_display.empty:
        st.warning("No records found matching filters.")
    else:
        for index, row in df_display.iterrows():
            sno = int(row["S.NO"]) if "S.NO" in row else index

            # Header visuals
            name = row.get("MASON NAME", "Unknown")
            code = row.get("MASON CODE", "")
            loc = row.get("Location", "")
            contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "")

            is_visited = row.get("Visited_Status") == "Visited"
            is_registered = row.get("Registered_Status") == "Registered"

            status_badges = ""
            if is_visited:
                status_badges += "🧭 "
            if is_registered:
                status_badges += "✅ "

            card_label = f"{status_badges} **{name}** "
            if code:
                card_label += f"({code}) "
            if loc:
                card_label += f" | 📍 {loc}"
            if contact:
                card_label += f" | 📞 {contact}"

            with st.expander(card_label, expanded=False):

                # 1. PRIMARY DETAILS
                st.markdown("#### 👤 Personal Details")
                c1, c2, c3 = st.columns(3)

                with c1:
                    st.text_input(
                        "Mason Name",
                        value=name,
                        key=f"name_{sno}",
                        on_change=update_entry,
                        args=(sno, "MASON NAME", f"name_{sno}")
                    )
                with c2:
                    st.text_input(
                        "Mason Code",
                        value=code,
                        key=f"code_{sno}",
                        on_change=update_entry,
                        args=(sno, "MASON CODE", f"code_{sno}")
                    )
                with c3:
                    st.text_input(
                        "Contact Number",
                        value=contact,
                        key=f"cont_{sno}",
                        on_change=update_entry,
                        args=(sno, "CONTACT NUMBER", f"cont_{sno}")
                    )

                # 2. LOCATION & META
                st.markdown("#### 📍 Location & Classification")
                l1, l2, l3, l4 = st.columns(4)
                with l1:
                    st.text_input(
                        "Location", value=loc, key=f"loc_{sno}",
                        on_change=update_entry, args=(sno, "Location", f"loc_{sno}")
                    )
                with l2:
                    st.text_input(
                        "DLR Name", value=row.get("DLR NAME", ""), key=f"dlr_{sno}",
                        on_change=update_entry, args=(sno, "DLR NAME", f"dlr_{sno}")
                    )
                with l3:
                    st.text_input(
                        "Day", value=row.get("DAY", ""), key=f"day_{sno}",
                        on_change=update_entry, args=(sno, "DAY", f"day_{sno}")
                    )
                with l4:
                    current_cat = row.get("Category", "")
                    options = ["E", "M", "Other", ""]
                    try:
                        idx = options.index(current_cat) if current_cat in options else 3
                    except ValueError:
                        idx = 3
                    st.selectbox(
                        "Category", options,
                        index=idx,
                        key=f"cat_{sno}",
                        on_change=update_entry, args=(sno, "Category", f"cat_{sno}")
                    )

                # 3. PRODUCTS
                st.markdown("#### 📦 Products Interested")
                p_cols = st.columns(6)
                hw_list = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]

                for i, prod in enumerate(hw_list):
                    val_str = str(row.get(prod, "")).upper()
                    is_checked = "YES" in val_str
                    with p_cols[i]:
                        st.checkbox(
                            prod,
                            value=is_checked,
                            key=f"{prod}_{sno}",
                            on_change=update_entry,
                            args=(sno, prod, f"{prod}_{sno}", True)
                        )

                # 4. REMARKS / OTHER
                st.markdown("#### 📝 Remarks")
                st.text_area(
                    "Other Notes",
                    value=row.get("other", ""),
                    height=68,
                    key=f"other_{sno}",
                    on_change=update_entry,
                    args=(sno, "other", f"other_{sno}")
                )

                st.markdown("---")

                # 5. ACTION BUTTONS
                b1, b2, b3 = st.columns([1, 1, 1])

                with b1:
                    if contact and len(contact) > 5:
                        st.markdown(
                            f"""<a href="tel:{contact}" style="display:block;text-align:center;background:#166534;color:white;padding:8px;border-radius:5px;text-decoration:none;">📞 Call Now</a>""",
                            unsafe_allow_html=True
                        )
                    else:
                        st.caption("🚫 No valid number")

                with b2:
                    v_label = "✅ Visited" if is_visited else "Mark Visited"
                    v_type = "primary" if is_visited else "secondary"
                    if st.button(v_label, key=f"btn_vis_{sno}", type=v_type, use_container_width=True):
                        df = st.session_state["data"]
                        new_status = "" if is_visited else "Visited"
                        df.loc[df["S.NO"] == sno, "Visited_Status"] = new_status
                        df.loc[df["S.NO"] == sno, "Visited_At"] = (
                            datetime.now().strftime("%Y-%m-%d") if new_status else ""
                        )
                        st.session_state["data"] = df
                        write_sheet(GOOGLE_SHEET_ID, df.copy(), SHEET_TAB_NAME)
                        st.rerun()

                with b3:
                    r_label = "✅ Registered" if is_registered else "Mark Registered"
                    r_type = "primary" if is_registered else "secondary"
                    if st.button(r_label, key=f"btn_reg_{sno}", type=r_type, use_container_width=True):
                        df = st.session_state["data"]
                        new_status = "" if is_registered else "Registered"
                        df.loc[df["S.NO"] == sno, "Registered_Status"] = new_status
                        df.loc[df["S.NO"] == sno, "Registered_At"] = (
                            datetime.now().strftime("%Y-%m-%d") if new_status else ""
                        )
                        st.session_state["data"] = df
                        write_sheet(GOOGLE_SHEET_ID, df.copy(), SHEET_TAB_NAME)
                        st.rerun()

# ----- ANALYTICS TAB -----
with tab_graphs:
    st.subheader("Data Visualizations")

    if not df_display.empty:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('<div class="mde-chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="mde-chart-title">Masons per Location</div>', unsafe_allow_html=True)
            if "Location" in df_display.columns:
                st.bar_chart(df_display["Location"].value_counts())
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown('<div class="mde-chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="mde-chart-title">Masons per Day</div>', unsafe_allow_html=True)
            if "DAY" in df_display.columns:
                st.bar_chart(df_display["DAY"].value_counts())
            st.markdown('</div>', unsafe_allow_html=True)

        col3, col4 = st.columns(2)
        hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]

        with col3:
            st.markdown('<div class="mde-chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="mde-chart-title">Product Popularity</div>', unsafe_allow_html=True)
            available = [c for c in hw_cols if c in df_display.columns]
            if available:
                counts = df_display[available].apply(
                    lambda x: x.astype(str).str.contains("YES", case=False).sum()
                )
                st.bar_chart(counts)
            st.markdown('</div>', unsafe_allow_html=True)

        with col4:
            st.markdown('<div class="mde-chart-card">', unsafe_allow_html=True)
            st.markdown('<div class="mde-chart-title">Category Distribution</div>', unsafe_allow_html=True)
            if "Category" in df_display.columns:
                st.bar_chart(df_display["Category"].value_counts())
            st.markdown('</div>', unsafe_allow_html=True)

# ----- DATA EDITOR TAB -----
with tab_data:
    st.subheader("Raw Data Table (Editable View)")

    column_config = {
        "CONTACT NUMBER": st.column_config.TextColumn("Contact"),
        "HW305": st.column_config.TextColumn("HW305", width="small"),
        "HW101": st.column_config.TextColumn("HW101", width="small"),
        "Hw201": st.column_config.TextColumn("Hw201", width="small"),
        "HW103": st.column_config.TextColumn("HW103", width="small"),
        "HW302": st.column_config.TextColumn("HW302", width="small"),
        "HW310": st.column_config.TextColumn("HW310", width="small"),
    }

    edit_df = df_display.copy()
    if not edit_df.empty and "CONTACT NUMBER" in edit_df.columns:
        edit_df["CONTACT NUMBER"] = edit_df["CONTACT NUMBER"].astype(str)

    edited_df = st.data_editor(
        edit_df,
        num_rows="dynamic",
        use_container_width=True,
        height=500,
        column_config=column_config,
    )

    st.write("---")

    # Currently view-only for Google Sheets. Use cards for edits.
    if not st.session_state["data"].empty:
        st.download_button(
            "📥 Download Full Current Report (All Masons)",
            to_excel(st.session_state["data"]),
            "mason_full_report.xlsx",
        )

# ------------ TOP RIGHT SHEET UPDATE BUTTON ------------

top_left, top_right = st.columns([5, 1])

with top_right:
    if st.button("💾 Update Google Sheet", key="btn_sync_top", use_container_width=True):
        if not st.session_state["data"].empty:
            write_sheet(GOOGLE_SHEET_ID, st.session_state["data"].copy(), SHEET_TAB_NAME)
            st.success("Google Sheet updated with current Mason data!")
        else:
            st.warning("No data to update. Add or import some rows first.")
