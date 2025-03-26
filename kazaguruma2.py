import streamlit as st
import requests

# Google Books API で本を検索する関数
def search_books(query, max_results=5):
    """Google Books API を使って本を検索する"""
    api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults={max_results}"
    response = requests.get(api_url)
    data = response.json()

    books = []
    if "items" in data:
        for item in data["items"]:
            volume_info = item["volumeInfo"]
            book = {
                "title": volume_info.get("title", "タイトル不明"),
                "authors": volume_info.get("authors", ["著者不明"]),
                "description": volume_info.get("description", "説明なし"),
                "link": volume_info.get("infoLink", "#"),
                "thumbnail": volume_info["imageLinks"]["thumbnail"] if "imageLinks" in volume_info else None
            }
            books.append(book)
    return books

# Streamlit アプリの UI
st.title('📚 学びたい内容に合った本をおすすめ！')

# ユーザーの入力
search_query = st.text_input("🔍 学びたい内容を入力してください（例: Python, 経済学, 心理学）")

# 検索ボタン
if st.button("おすすめの本を探す"):
    if search_query:
        books = search_books(search_query)
        if books:
            for book in books:
                st.subheader(book["title"])
                st.write(f'著者: {", ".join(book["authors"])}')
                st.write(book["description"])
                st.markdown(f'[📖 詳細を見る]({book["link"]})', unsafe_allow_html=True)
                if book["thumbnail"]:
                    st.image(book["thumbnail"], width=150)
                st.markdown("---")
        else:
            st.write("❌ 本が見つかりませんでした。別のキーワードを試してください。")
    else:
        st.write("⚠️ 検索ワードを入力してください。")
