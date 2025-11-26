import streamlit as st
import pandas as pd
from io import BytesIO
from pathlib import Path
from datetime import datetime

# ------------ CONFIG ------------
st.set_page_config(page_title="Mason Data Manager", layout="wide")

# Header
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

# ------------ GLOBAL CSS ------------
st.markdown("""
<style>
/* Page & layout */
body { background-color: #f1f5f9; }
.block-container { padding-top: 0.5rem; max-width: 1200px; }

/* Header */
.mde-header {
    position: sticky; top: 0; z-index: 50; width: 100%;
    background: #ffffff; box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06); margin-bottom: 1rem;
}
.mde-header-inner {
    max-width: 1200px; margin: 0 auto; padding: 0.8rem 1.5rem;
    display: flex; align-items: center; justify-content: space-between;
}
.mde-title { font-size: 1.7rem; font-weight: 800; color: #4338ca; margin: 0; }
.mde-header-tag {
    font-size: 0.75rem; padding: 0.3rem 0.6rem; border-radius: 999px;
    background: #eef2ff; color: #4f46e5; font-weight: 600;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #ffffff; border-radius: 0.85rem; padding: 0.75rem;
    box-shadow: 0 4px 6px rgba(0,0,0,0.04); border: 1px solid #e5e7eb;
}

/* Custom Expander Styling */
.streamlit-expanderHeader {
    font-weight: 600;
    color: #1e293b;
    background-color: #ffffff;
    border-radius: 0.5rem;
}
</style>
""", unsafe_allow_html=True)

# ------------ HELPERS ------------

DATA_FILE = "mason_data.xlsx"

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

# --- AUTO SAVE CALLBACK ---
def update_entry(sno, col, key_name, is_checkbox=False):
    """
    Updates a specific cell in the dataframe immediately when changed.
    """
    new_value = st.session_state[key_name]
    
    # Handle Checkbox logic (True -> YES, False -> "")
    if is_checkbox:
        new_value = "YES" if new_value else ""

    # Locate the row by S.NO in the main dataset
    idx = st.session_state["data"].index[st.session_state["data"]["S.NO"] == sno].tolist()
    
    if idx:
        row_idx = idx[0]
        st.session_state["data"].at[row_idx, col] = new_value
        # Save to disk immediately
        st.session_state["data"].to_excel(DATA_FILE, index=False)

# ------------ SESSION STATE INIT ------------

if "data" not in st.session_state:
    if Path(DATA_FILE).exists():
        st.session_state["data"] = clean_dataframe(pd.read_excel(DATA_FILE))
    else:
        st.session_state["data"] = pd.DataFrame(columns=[
            "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER",
            "DLR NAME", "Location", "DAY", "Category",
            "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other",
            "Visited_Status", "Visited_At", "Registered_Status", "Registered_At"
        ])

if "prev_data" not in st.session_state:
    st.session_state["prev_data"] = None

# Ensure columns exist
for col in ["Visited_Status", "Visited_At", "Registered_Status", "Registered_At", "other"]:
    if col not in st.session_state["data"].columns:
        st.session_state["data"][col] = ""

# Filter Defaults
for k in ["filter_day", "filter_location", "filter_cat", "filter_visit_status", 
          "filter_reg_status", "filter_mobile_input", "filter_mobile_query"]:
    if k not in st.session_state:
        st.session_state[k] = "All" if "filter" in k and "input" not in k and "query" not in k else ""
if "filter_only_products" not in st.session_state: st.session_state["filter_only_products"] = False
if "filter_no_products" not in st.session_state: st.session_state["filter_no_products"] = False
if "reset_filters" not in st.session_state: st.session_state["reset_filters"] = False

# Reset Logic
if st.session_state["reset_filters"]:
    st.session_state["filter_day"] = "All"
    st.session_state["filter_location"] = "All"
    st.session_state["filter_cat"] = "All"
    st.session_state["filter_visit_status"] = "All"
    st.session_state["filter_reg_status"] = "All"
    st.session_state["filter_only_products"] = False
    st.session_state["filter_no_products"] = False
    st.session_state["filter_mobile_input"] = ""
    st.session_state["filter_mobile_query"] = ""
    st.session_state["reset_filters"] = False

# ------------ DATA MANAGEMENT ------------

with st.expander("🛠️ Data Management (Import / Add / Undo)", expanded=False):
    if st.session_state["prev_data"] is not None:
        if st.button("↩️ Undo Last Change", type="primary"):
            st.session_state["data"] = st.session_state["prev_data"]
            st.session_state["prev_data"] = None
            st.session_state["data"].to_excel(DATA_FILE, index=False)
            st.rerun()

    t1, t2 = st.tabs(["➕ Add Entry", "📂 Import Excel"])
    with t2:
        uf = st.file_uploader("Upload Excel", type=["xlsx"])
        if uf and st.button("Load"):
            nd = load_excel_data(uf)
            if nd is not None:
                save_state_for_undo()
                st.session_state["data"] = nd
                st.session_state["data"].to_excel(DATA_FILE, index=False)
                st.rerun()
        st.download_button("Download Template", get_template_excel(), "template.xlsx")
    
    with t1:
        with st.form("new_entry"):
            c1, c2 = st.columns(2)
            nm = c1.text_input("Name")
            loc = c2.text_input("Location")
            if st.form_submit_button("Add"):
                save_state_for_undo()
                sno = st.session_state["data"]["S.NO"].max() + 1 if not st.session_state["data"].empty else 1
                new_row = {"S.NO": sno, "MASON NAME": nm, "Location": loc}
                st.session_state["data"] = pd.concat([st.session_state["data"], pd.DataFrame([new_row])], ignore_index=True)
                st.session_state["data"].to_excel(DATA_FILE, index=False)
                st.rerun()

# ------------ FILTER LOGIC ------------

with st.expander("🔍 Filter Data", expanded=True):
    base_df = st.session_state["data"].copy()
    f1, f2, f3 = st.columns(3)
    
    days = ["All"] + sorted([x for x in base_df["DAY"].unique() if str(x).strip()])
    sel_day = f1.selectbox("Day", days, key="filter_day")
    
    if sel_day != "All": base_df = base_df[base_df["DAY"] == sel_day]
    
    locs = ["All"] + sorted([x for x in base_df["Location"].unique() if str(x).strip()])
    sel_loc = f2.selectbox("Location", locs, key="filter_location")

    mob = f3.text_input("Search Mobile", key="filter_mobile_input")
    if f3.button("Search"): st.session_state["filter_mobile_query"] = mob
    if f3.button("Reset"): st.session_state["reset_filters"] = True; st.rerun()

# Apply Filters
df_display = st.session_state["data"].copy()
if st.session_state["filter_day"] != "All":
    df_display = df_display[df_display["DAY"] == st.session_state["filter_day"]]
if st.session_state["filter_location"] != "All":
    df_display = df_display[df_display["Location"] == st.session_state["filter_location"]]
if st.session_state["filter_mobile_query"]:
    df_display = df_display[df_display["CONTACT NUMBER"].astype(str).str.contains(st.session_state["filter_mobile_query"], case=False)]

# ------------ DASHBOARD ------------

st.markdown("### 📊 Overview")
m1, m2, m3 = st.columns(3)
m1.metric("Total Masons", len(st.session_state["data"]))
m2.metric("Filtered View", len(df_display))
m3.metric("Locations", df_display["Location"].nunique())

st.divider()

# ------------ TABS ------------

tab_cards, tab_raw = st.tabs(["📇 Live Editable Cards", "📝 Raw Data"])

# ==========================================
#        NEW EDITABLE CARDS SECTION
# ==========================================
with tab_cards:
    st.info("💡 **Tip:** Click a card to expand. Any change you make inside is **saved automatically**.")
    
    if df_display.empty:
        st.warning("No records found matching filters.")
    
    # Iterate through the filtered dataframe
    for index, row in df_display.iterrows():
        
        sno = row["S.NO"] # Unique ID
        
        # --- Prepare Card Header Visuals ---
        name = row.get("MASON NAME", "Unknown")
        code = row.get("MASON CODE", "")
        loc = row.get("Location", "")
        contact = str(row.get("CONTACT NUMBER", "")).replace(".0", "")
        
        # Status Badges
        is_visited = row.get("Visited_Status") == "Visited"
        is_registered = row.get("Registered_Status") == "Registered"
        
        status_badges = ""
        if is_visited: status_badges += "🧭 "
        if is_registered: status_badges += "✅ "
        
        # Card Label (Header)
        card_label = f"{status_badges} **{name}** "
        if code: card_label += f"({code}) "
        if loc: card_label += f" | 📍 {loc}"
        if contact: card_label += f" | 📞 {contact}"

        # --- The Card (Expander) ---
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
                st.selectbox(
                    "Category", ["E", "M", "Other", ""],
                    index=["E", "M", "Other", ""].index(row.get("Category", "")) if row.get("Category") in ["E", "M", "Other"] else 3,
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
                        args=(sno, prod, f"{prod}_{sno}", True) # True indicates checkbox logic
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
            
            # 5. ACTION BUTTONS (CALL / VISIT / REGISTER)
            b1, b2, b3 = st.columns([1, 1, 1])
            
            # Call Button (HTML Link)
            with b1:
                if contact and len(contact) > 5:
                    st.markdown(
                        f"""<a href="tel:{contact}" style="display:block;text-align:center;background:#166534;color:white;padding:8px;border-radius:5px;text-decoration:none;">📞 Call Now</a>""", 
                        unsafe_allow_html=True
                    )
                else:
                    st.caption("🚫 No valid number")

            # Visited Toggle
            with b2:
                v_label = "✅ Visited" if is_visited else "Mark Visited"
                v_type = "primary" if is_visited else "secondary"
                if st.button(v_label, key=f"btn_vis_{sno}", type=v_type, use_container_width=True):
                    new_status = "" if is_visited else "Visited"
                    st.session_state["data"].loc[st.session_state["data"]["S.NO"]==sno, "Visited_Status"] = new_status
                    st.session_state["data"].loc[st.session_state["data"]["S.NO"]==sno, "Visited_At"] = datetime.now().strftime("%Y-%m-%d") if new_status else ""
                    st.session_state["data"].to_excel(DATA_FILE, index=False)
                    st.rerun()

            # Registered Toggle
            with b3:
                r_label = "✅ Registered" if is_registered else "Mark Registered"
                r_type = "primary" if is_registered else "secondary"
                if st.button(r_label, key=f"btn_reg_{sno}", type=r_type, use_container_width=True):
                    new_status = "" if is_registered else "Registered"
                    st.session_state["data"].loc[st.session_state["data"]["S.NO"]==sno, "Registered_Status"] = new_status
                    st.session_state["data"].loc[st.session_state["data"]["S.NO"]==sno, "Registered_At"] = datetime.now().strftime("%Y-%m-%d") if new_status else ""
                    st.session_state["data"].to_excel(DATA_FILE, index=False)
                    st.rerun()

# ----- RAW DATA TAB -----
with tab_raw:
    st.dataframe(st.session_state["data"], use_container_width=True)
    st.download_button("Download Excel", to_excel(st.session_state["data"]), "data.xlsx")
