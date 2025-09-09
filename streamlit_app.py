import streamlit as st
import sqlite3
import google.generativeai as genai
import datetime

# DB初期化
def init_db():
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()
    # ファイルテーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_name TEXT,
            content TEXT,
            uploaded_at TIMESTAMP
        )
    ''')
    # チャット履歴テーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS chat_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            role TEXT,
            content TEXT,
            created_at TIMESTAMP,
            FOREIGN KEY(file_id) REFERENCES files(id)
        )
    ''')
    conn.commit()
    conn.close()

def save_file_to_db(file_name, content):
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute("INSERT INTO files (file_name, content, uploaded_at) VALUES (?, ?, ?)", (file_name, content, now))
    file_id = c.lastrowid
    conn.commit()
    conn.close()
    return file_id

def get_latest_file():
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()
    c.execute("SELECT id, file_name, content FROM files ORDER BY uploaded_at DESC LIMIT 1")
    row = c.fetchone()
    conn.close()
    return row

def save_chat_to_db(file_id, role, content):
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()
    now = datetime.datetime.now()
    c.execute("INSERT INTO chat_history (file_id, role, content, created_at) VALUES (?, ?, ?, ?)", (file_id, role, content, now))
    conn.commit()
    conn.close()

def get_chat_history(file_id):
    conn = sqlite3.connect("app_data.db")
    c = conn.cursor()
    c.execute("SELECT role, content FROM chat_history WHERE file_id=? ORDER BY created_at ASC", (file_id,))
    rows = c.fetchall()
    conn.close()
    return [{"role": r, "content": c} for r, c in rows]

# 初期化
init_db()

# Streamlit本体
st.title("📄 Document question answering (with DB persistence)")

gemini_api_key = st.secrets.get("gemini_api_key")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    genai.configure(api_key=gemini_api_key)

    # ファイルアップロード
    uploaded_file = st.file_uploader("Upload a document (.txt or .md)", type=("txt", "md"))
    if uploaded_file:
        file_content = uploaded_file.read().decode(errors="ignore")
        file_id = save_file_to_db(uploaded_file.name, file_content)
    else:
        file_row = get_latest_file()
        if file_row:
            file_id, file_name, file_content = file_row
            st.success(f"アップロード済みファイル: {file_name}")
        else:
            file_id, file_content = None, None

    # チャット履歴
    if file_id:
        chat_history = get_chat_history(file_id)
    else:
        chat_history = []

    # チャットUI
    st.write("## チャット")
    for message in chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("ai").write(message["content"])

    if file_content:
        user_input = st.chat_input("質問を入力してください")
        if user_input:
            prompt = (
                f"あなたはアップロードされたドキュメントに基づいて質問に答えるAIアシスタントです。\n"
                f"ドキュメント内容: {file_content}\n\n"
                f"--- これまでの会話 ---\n"
            )
            for msg in chat_history[-5:]:
                role = "ユーザー" if msg["role"] == "user" else "アシスタント"
                prompt += f"{role}: {msg['content']}\n"
            prompt += f"ユーザー: {user_input}\nアシスタント:"

            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            ai_response = response.text

            save_chat_to_db(file_id, "user", user_input)
            save_chat_to_db(file_id, "ai", ai_response)

            st.chat_message("ai").write(ai_response)
    else:
        st.info("まずドキュメントをアップロードしてください。")
