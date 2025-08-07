## 🗃️ NL_to_SQL_with_Automated_DB
---


🧠 Natural Language to SQL Interface
This project is a Streamlit-based web app that converts natural language prompts into SQL queries using a fine-tuned T5 language model. It also includes a SQL Workbench-style interface for creating tables, inserting rows, and querying data—making it perfect for non-technical users or rapid prototyping.

---

🚀 Features
---
🔍 Natural Language to SQL Generator
Enter plain English queries like:

"Show all students older than 18"

- Converts it into valid SQL using a Transformer model.

- Executes and displays query results on the fly.

---


🛠️ SQL Workbench
---

- Create SQLite tables visually.

- Add columns with types (INTEGER, TEXT, REAL, DATE).

- Insert data through a dynamic form.

- See live data in the UI.

- Ask natural language questions about the table data.

---


📦 Tech Stack
| Layer     | Technology                                              |
| --------- | ------------------------------------------------------- |
| Frontend  | [Streamlit](https://streamlit.io/)                      |
| Backend   | [SQLite](https://sqlite.org/index.html)                 |
| LLM Model | `T5ForConditionalGeneration` (HuggingFace Transformers) |
| Language  | Python 3.10+                                            |

---


🛠️ Setup Instructions


🔧 1. Clone the repository
```bash
git clone https://github.com/smaranng/NL_to_SQL_with_Automated_DB.git


cd nl_to_sql
```
---


📦 2. Install Dependencies


We recommend using a virtual environment:

- `streamlit`


- `torch`


- `transformers`


- `pandas`

---



📥 3. Add the Fine-Tuned T5 Model
Place your custom-trained T5 model directory named nl_to_sql_model/ inside the project root. It should contain:
```

nl_to_sql_model/
├── config.json
├── pytorch_model.bin
├── tokenizer_config.json
├── tokenizer.json
├── special_tokens_map.json
└── vocab files...

```
You can also load a public HuggingFace model here by modifying load_model() in the code.

---

▶️ 4. Run the App


```bash
streamlit run fullsql.py
```

---


📁 Project Structure

```
├── fullsql.py               # Main Streamlit app
├── user_db.sqlite           # SQLite database (auto-generated)
├── nl_to_sql_model/         # Fine-tuned T5 model directory
└── README.md
```

---


✨ Example Prompts


Try these in the NL to SQL generator tab:
```
Get all employees with salary > 50000

Show all students born after 2000

List orders where amount < 1000
```

---

🔐 Notes


- Data is stored in a local SQLite file (user_db.sqlite).

- Only basic types supported: INTEGER, TEXT, REAL, DATE.

- App supports dynamic table creation and insertion with DATE pickers.

- Aliases like "employee" or "staff" are normalized internally for flexibility.

---

🧠 Model Training (Optional)


If you're interested in training your own model:

Use the T5 architecture (t5-small, t5-base, etc.).

Format input as "translate English to SQL: {question}"

Output: valid SQL syntax targeting your schema.

Fine-tune using Hugging Face's Trainer API.

---


🙌 Credits
Hugging Face Transformers

Streamlit

SQLite



