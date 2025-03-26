import streamlit as st
import requests

# 📌 SecretsからAPIキーを取得
books_api_key = st.secrets["google"]["books_api_key"]
# 確認用で記載していたが、記載しない方が良い旨いただいためコメントアウト
# st.sidebar.text_input("APIキー確認用", value=books_api_key, type="password")
# st.write("🔍 secrets の中身（debug）:", st.secrets)

# 📚 Google Books APIを使って本を検索する関数
def search_books(query, books_api_key, max_results=5):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": query,
        "maxResults": max_results,
        "printType": "books",
        "key": books_api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    else:
        st.error(f"⚠️ Google Books APIリクエストに失敗しました（{response.status_code}）")
        return []

# 🌟 Streamlitアプリ本体
st.title("📚 学びたい内容で本を検索")

# 🔍 ユーザー入力欄
query = st.text_input("🔎 検索キーワードを入力してください（例: Python, 哲学, 心理学）")
max_results = st.slider("📘 表示する本の数", 1, 20, 5)

# 🔍 検索ボタン
if st.button("📖 本を探す"):
    if query:
        books = search_books(query, books_api_key, max_results=max_results)
        if books:
            for book in books:
                info = book.get("volumeInfo", {})
                title = info.get("title", "タイトル不明")
                authors = ", ".join(info.get("authors", ["著者不明"]))
                description = info.get("description", "説明なし")
                thumbnail = info.get("imageLinks", {}).get("thumbnail", "")
                link = info.get("infoLink", "#")

                st.markdown("---")
                st.markdown(f"### 📘 [{title}]({link})", unsafe_allow_html=True)
                st.write(f"👤 著者: {authors}")
                st.write(f"📝 説明: {description[:300]}...")  # 長すぎる説明はカット
                if thumbnail:
                    st.image(thumbnail, width=120)
        else:
            st.warning("📭 検索結果が見つかりませんでした。キーワードを変えてみてください。")
    else:
        st.info("🔍 キーワードを入力してください。")
