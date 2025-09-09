import streamlit as st
import google.generativeai as genai

# Show title and description.
st.title("📄 Document question answering")
st.write(
    "Upload a document below and ask a question about it – Gemini will answer! "
    "To use this app, you need to provide your Gemini API key. "
)

# Ask user for their Gemini API key via `st.text_input`.
# You may also store the API key in `./.streamlit/secrets.toml` using the key name "gemini_api_key".
gemini_api_key = st.secrets.get("gemini_api_key")
if not gemini_api_key:
    st.info("Please add your Gemini API key to continue.", icon="🗝️")
else:
    # NOTE: There is no official OpenAI Python client for Gemini. 
    # You need to use Google's generativeai client or an HTTP client for Gemini API.
    # For demonstration, we'll show a typical approach using google.generativeai
    # (You must install google-generativeai: pip install google-generativeai)

    genai.configure(api_key=gemini_api_key)

    # ドキュメントの内容をセッションに保存
    # ブラウザリロード後もアップロード済みファイル内容が残るよう、ファイル内容をst.session_stateに必ず保存する
    if "document" not in st.session_state:
        st.session_state.document = None
    if "document_name" not in st.session_state:
        st.session_state.document_name = None

    # Let the user upload a file via `st.file_uploader`, keeping its value after reload
    uploaded_file = st.file_uploader(
        "Upload a document (.txt or .md)", type=("txt", "md"), key="file_uploader"
    )

    if uploaded_file is not None:
        # 新しいファイルがアップロードされた場合のみ内容を保存
        file_content = uploaded_file.read().decode(errors="ignore")
        # ファイル内容と名前をセッションに保存
        st.session_state.document = file_content
        st.session_state.document_name = uploaded_file.name

    # アップロード済みファイルがあれば表示
    if st.session_state.document is not None and st.session_state.document_name is not None:
        st.success(f"アップロード済みファイル: {st.session_state.document_name}")

    # チャット履歴をセッションに保存
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # チャットUI
    st.write("## チャット")
    for message in st.session_state.chat_history:
        if message["role"] == "user":
            st.chat_message("user").write(message["content"])
        else:
            st.chat_message("ai").write(message["content"])

    # チャット入力欄
    if st.session_state.document:
        user_input = st.chat_input("質問を入力してください")
        if user_input:
            # Gemini へのプロンプトを構築
            prompt = (
                f"あなたはアップロードされたドキュメントに基づいて質問に答えるAIアシスタントです。\n"
                f"ドキュメント内容: {st.session_state.document}\n\n"
                f"--- これまでの会話 ---\n"
            )
            # これまでの会話をプロンプトに追加（最新5件まで）
            for msg in st.session_state.chat_history[-5:]:
                role = "ユーザー" if msg["role"] == "user" else "アシスタント"
                prompt += f"{role}: {msg['content']}\n"
            # 今回の質問
            prompt += f"ユーザー: {user_input}\nアシスタント:"

            # Gemini 2.5 Flash (gemini-2.5-flash) で応答
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content(prompt)
            ai_response = response.text

            # チャット履歴に追加
            st.session_state.chat_history.append({"role": "user", "content": user_input})
            st.session_state.chat_history.append({"role": "ai", "content": ai_response})

            # 応答を表示
            st.chat_message("ai").write(ai_response)
    else:
        st.info("まずドキュメントをアップロードしてください。")
