import streamlit as st
import sqlite3
import pandas as pd
import torch
from transformers import T5Tokenizer, T5ForConditionalGeneration

# ========== Load Model ==========
@st.cache_resource
def load_model():
    tokenizer = T5Tokenizer.from_pretrained("nl_to_sql_model")
    model = T5ForConditionalGeneration.from_pretrained("nl_to_sql_model")
    return tokenizer, model

tokenizer, model = load_model()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# ========== Setup DB ==========
conn = sqlite3.connect("user_db.sqlite", check_same_thread=False)
cursor = conn.cursor()

# ========== Sidebar Navigation ==========
st.sidebar.markdown("### 🗃️ Navigation")

# Red-colored button styles
st.sidebar.markdown("""
    <style>
    .stButton > button {
        color: red;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

if "page" not in st.session_state:
    st.session_state.page = "SQL Generator"

if st.sidebar.button("🔍 View Our SQL Generator"):
    st.session_state.page = "SQL Generator"
if st.sidebar.button("🛠️ View Our SQL Workbench"):
    st.session_state.page = "SQL Workbench"

# ========== Alias Mapping ==========
alias_to_actual = {
    "emp": "employees",
    "employee": "employees",
    "staff": "employees",
    "pupil": "students",
    "learner": "students",
    "item": "products",
    "purchase": "orders",
    "subject": "courses",
    "students": "student",
    "lib": "libraries",
    "library": "libraries",
    "students":"studentss",
    "employees":"employeess"
}
actual_to_alias = {v: k for k, v in alias_to_actual.items()}

def normalize_prompt(prompt):
    for alias, actual in alias_to_actual.items():
        prompt = prompt.replace(alias, actual)
    return prompt

def denormalize_sql(sql, prompt):
    for alias, actual in alias_to_actual.items():
        if alias in prompt and actual in sql:
            sql = sql.replace(actual, alias)
    return sql

# ========== SQL Generator ==========
if st.session_state.page == "SQL Generator":
    st.title("🧠 Natural Language to SQL Generator Using LLMs")
    user_input = st.text_area("Enter a natural language prompt", height=150)

    if st.button("Generate SQL"):
        if user_input.strip():
            input_ids = tokenizer(user_input, return_tensors="pt").input_ids.to(device)
            output = model.generate(input_ids, max_length=64, num_beams=4, early_stopping=True)
            sql_query = tokenizer.decode(output[0], skip_special_tokens=True)
            st.code(sql_query, language="sql")
        else:
            st.warning("⚠️ Please enter a prompt first.")

# ========== SQL Workbench ==========
elif st.session_state.page == "SQL Workbench":
    st.title("🧠 Natural Language to SQL Interface (Workbench Style)")

    if "table_created" not in st.session_state:
        st.session_state.table_created = False
        st.session_state.table_name = ""
        st.session_state.col_defs = []
        st.session_state.insert_section_visible = False

    st.header("📁 Create a Table")
    table_name = st.text_input("Table name")
    num_columns = st.number_input("How many columns?", min_value=1, max_value=10, step=1)

    col_defs = []
    st.subheader("Define Columns")
    for i in range(num_columns):
        col_name = st.text_input(f"Column {i+1} Name", key=f"name_{i}")
        col_type = st.selectbox(f"Column {i+1} Type", ["INTEGER", "TEXT", "REAL", "DATE"], key=f"type_{i}")
        col_defs.append((col_name.strip(), col_type))

    if st.button("Create Table"):
        if not table_name.strip():
            st.error("❌ Table name is required.")
        elif any(not name for name, _ in col_defs):
            st.error("❌ All column names must be filled in.")
        else:
            try:
                col_str = ", ".join([f"{name} {dtype}" for name, dtype in col_defs])
                cursor.execute(f"CREATE TABLE \"{table_name}\" ({col_str})")
                conn.commit()
                st.success(f"✅ Table '{table_name}' created.")
                st.session_state.table_created = True
                st.session_state.table_name = table_name
                st.session_state.col_defs = col_defs
                st.session_state.insert_section_visible = True
            except Exception as e:
                st.error(f"❌ Error creating table: {e}")

    if st.session_state.insert_section_visible:
        st.header("➕ Insert Rows")
        with st.form("insert_form", clear_on_submit=True):
            values = []
            for col_name, col_type in st.session_state.col_defs:
                if col_type == "DATE":
                    val = st.date_input(f"Date for {col_name}", key=f"val_{col_name}")
                    values.append(val.strftime("%Y-%m-%d"))
                else:
                    val = st.text_input(f"Value for {col_name}", key=f"val_{col_name}")
                    values.append(val)

            submitted = st.form_submit_button("Insert Row")

            if submitted:
                try:
                    q_marks = ", ".join(["?"] * len(values))
                    cursor.execute(f"INSERT INTO \"{st.session_state.table_name}\" VALUES ({q_marks})", values)
                    conn.commit()
                    st.success("✅ Row inserted successfully!")
                except Exception as e:
                    st.error(f"❌ Error inserting row: {e}")

        st.subheader("📊 Current Table Data")
        try:
            df = pd.read_sql_query(f"SELECT * FROM \"{st.session_state.table_name}\"", conn)
            st.dataframe(df)
        except Exception as e:
            st.error(f"❌ Error loading table data: {e}")

    if st.session_state.table_created:
        st.header("💬 Ask a Question in Natural Language")
        user_input = st.text_area("Example: Get all emp with age > 25", height=100)

        if st.button("Generate SQL and Execute"):
            if user_input.strip():
                try:
                    normalized_input = normalize_prompt(user_input.lower())
                    input_ids = tokenizer(normalized_input, return_tensors="pt").input_ids.to(device)
                    output = model.generate(input_ids, max_length=64, num_beams=4, early_stopping=True)
                    sql_query = tokenizer.decode(output[0], skip_special_tokens=True)
                    final_sql = denormalize_sql(sql_query, user_input.lower())

                    st.write("🔎 Generated SQL Query:")
                    st.code(final_sql, language="sql")

                    try:
                        result = pd.read_sql_query(final_sql, conn)
                        st.success("✅ Query executed successfully!")
                        st.dataframe(result)
                    except Exception as e:
                        st.error(f"❌ Error executing query: {e}")
                except Exception as e:
                    st.error(f"❌ Model generation error: {e}")
            else:
                st.warning("⚠️ Please enter a natural language prompt.")
