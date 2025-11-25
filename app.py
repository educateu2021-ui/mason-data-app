import streamlit as st
import pandas as pd
from io import BytesIO

# Set page configuration
st.set_page_config(page_title="Mason Data Manager", layout="wide")

st.title("Mason Data Management System")

# --- Helper Functions ---

def get_template_excel():
    """Generates an empty template file with correct headers"""
    columns = [
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER", 
        "DLR NAME", "Location", "DAY", "Category", 
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other"
    ]
    df_template = pd.DataFrame(columns=columns)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df_template.to_excel(writer, index=False, sheet_name='Template')
    return output.getvalue()

def load_excel_data(uploaded_file):
    """Helper to read excel and standardize columns"""
    try:
        df = pd.read_excel(uploaded_file)
        
        # Simple cleanup
        df = df.fillna("")
        
        # Ensure 'S.NO' is numeric
        if "S.NO" in df.columns:
            df["S.NO"] = pd.to_numeric(df["S.NO"], errors='coerce').fillna(0).astype(int)
            
        return df
    except Exception as e:
        st.error(f"Error loading file: {e}")
        return None

def save_state_for_undo():
    """Saves the current dataframe to history before making changes"""
    st.session_state['prev_data'] = st.session_state['data'].copy()

# --- Session State Initialization ---
if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=[
        "S.NO", "MASON CODE", "MASON NAME", "CONTACT NUMBER", 
        "DLR NAME", "Location", "DAY", "Category", 
        "HW305", "HW101", "Hw201", "HW103", "HW302", "HW310", "other"
    ])

if 'prev_data' not in st.session_state:
    st.session_state['prev_data'] = None

# --- Sidebar: Controls & Entry ---
with st.sidebar:
    st.title("Controls")
    
    # --- SECTION: TEMPLATE ---
    st.subheader("1. Get Template")
    st.download_button(
        label="📄 Download Blank Excel Template",
        data=get_template_excel(),
        file_name='mason_data_template.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        help="Download this file, fill it with data, and upload it below."
    )
    
    st.divider()

    # --- SECTION: UPLOAD ---
    st.subheader("2. Import Data")
    uploaded_file = st.file_uploader("Upload Excel File", type=['xlsx', 'xls'])
    if uploaded_file is not None:
        if st.button("Load Data"):
            new_data = load_excel_data(uploaded_file)
            if new_data is not None:
                save_state_for_undo()
                st.session_state['data'] = new_data
                st.success(f"Loaded {len(new_data)} rows!")
                st.rerun()

    # --- SECTION: UNDO ---
    if st.session_state['prev_data'] is not None:
        st.write("---")
        if st.button("↩️ Undo Last Change"):
            st.session_state['data'] = st.session_state['prev_data']
            st.session_state['prev_data'] = None 
            st.success("Restored previous version!")
            st.rerun()

    st.divider()

    # --- SECTION: SINGLE ENTRY ---
    with st.expander("➕ Add Single Entry"):
        with st.form("entry_form"):
            mason_code = st.text_input("Mason Code")
            mason_name = st.text_input("Mason Name")
            contact_number = st.text_input("Contact Number")
            dlr_name = st.text_input("DLR Name")
            location = st.text_input("Location")
            
            day = st.selectbox("Day", ["MONDAY", "TUESDAY", "WEDNESDAY", "THURSDAY", "FRIDAY", "SATURDAY", "SUNDAY"])
            category = st.selectbox("Category", ["E", "M", "Other"])
            
            st.write("**Products (YES/NO)**")
            c1, c2 = st.columns(2)
            with c1:
                hw305 = st.checkbox("HW305")
                hw101 = st.checkbox("HW101")
                hw201 = st.checkbox("Hw201")
            with c2:
                hw103 = st.checkbox("HW103")
                hw302 = st.checkbox("HW302")
                hw310 = st.checkbox("HW310")
                
            other_notes = st.text_input("Other / Remarks")
            
            submitted = st.form_submit_button("Add Line Item")

            if submitted:
                if not mason_name:
                    st.error("Mason Name is required!")
                else:
                    save_state_for_undo()
                    new_sno = len(st.session_state['data']) + 1 if 'S.NO' in st.session_state['data'].columns else 1
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
                        "other": other_notes
                    }
                    st.session_state['data'] = pd.concat([st.session_state['data'], pd.DataFrame([new_row])], ignore_index=True)
                    st.success("Entry added!")
                    st.rerun()

    st.divider()
    
    # --- SECTION: FILTERS ---
    st.subheader("🔍 Filters")
    
    df_display = st.session_state['data'].copy()
    
    locations = ["All"] + sorted(list(df_display["Location"].unique())) if "Location" in df_display.columns else ["All"]
    selected_location = st.selectbox("Filter by Location", locations)
    
    days = ["All"] + sorted(list(df_display["DAY"].unique())) if "DAY" in df_display.columns else ["All"]
    selected_day = st.selectbox("Filter by Day", days)

    cats = ["All"] + sorted(list(df_display["Category"].unique())) if "Category" in df_display.columns else ["All"]
    selected_cat = st.selectbox("Filter by Category", cats)

    show_only_products = st.checkbox("Show only with Products")
    show_no_products = st.checkbox("Show only with NO Products")

# --- Main Dashboard ---

if not df_display.empty:
    if selected_location != "All":
        df_display = df_display[df_display["Location"] == selected_location]
    if selected_day != "All":
        df_display = df_display[df_display["DAY"] == selected_day]
    if selected_cat != "All":
        df_display = df_display[df_display["Category"] == selected_cat]
        
    hw_cols = ["HW305", "HW101", "Hw201", "HW103", "HW302", "HW310"]
    if show_only_products:
        mask = df_display[hw_cols].apply(lambda x: x.astype(str).str.contains('YES', case=False).any(), axis=1)
        df_display = df_display[mask]
    if show_no_products:
        mask = df_display[hw_cols].apply(lambda x: not x.astype(str).str.contains('YES', case=False).any(), axis=1)
        df_display = df_display[mask]

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Masons", len(st.session_state['data']))
m2.metric("Visible Rows", len(df_display))
m3.metric("Unique Locations", df_display["Location"].nunique() if "Location" in df_display.columns else 0)
m4.metric("Unique DLRs", df_display["DLR NAME"].nunique() if "DLR NAME" in df_display.columns else 0)

st.write("### Mason Database")

column_config = {
    "CONTACT NUMBER": st.column_config.LinkColumn(
        "Contact",
        help="Click to Call",
        validate=r"^\+?[0-9]*$",
        display_text=r"(\+?[0-9]*)",
    ),
    "HW305": st.column_config.TextColumn("HW305", width="small"),
    "HW101": st.column_config.TextColumn("HW101", width="small"),
    "Hw201": st.column_config.TextColumn("Hw201", width="small"),
    "HW103": st.column_config.TextColumn("HW103", width="small"),
    "HW302": st.column_config.TextColumn("HW302", width="small"),
    "HW310": st.column_config.TextColumn("HW310", width="small"),
}

if not df_display.empty and "CONTACT NUMBER" in df_display.columns:
    df_display["CONTACT NUMBER"] = df_display["CONTACT NUMBER"].astype(str)

edited_df = st.data_editor(
    df_display, 
    num_rows="dynamic", 
    use_container_width=True,
    height=500,
    column_config=column_config
)

st.write("---")

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='MasonData')
    return output.getvalue()

if not df_display.empty:
    st.download_button(
        label="📥 Export Filtered Data to Excel",
        data=to_excel(df_display),
        file_name='mason_data_export.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
else:
    st.info("No data to display. Upload an Excel file or add an entry.")
