import streamlit as st
import requests
import datetime
import numpy as np
import pandas as pd
from openai import OpenAI # OpenAIのAPIを扱うためのライブラリをインポート

# StreamlitのSecretsからAPIキーを取得
# 生成AI
client = OpenAI(api_key = st.secrets["GPTAPI"].get("OPENAI_API_KEY"))
# google books
books_api_key = st.secrets["google"].get("books_api_key")

# `plotly` のインポートを試みる
try:
    import plotly.graph_objects as go
    plotly_available = True
except ImportError:
    plotly_available = False
    st.warning("⚠️ `plotly` がインストールされていません。以下のコマンドでインストールしてください。\n\n```sh\npip install plotly\n```")

# 生成AI活用
content_kind_of =[
    "中立的で客観的な文章",
    "分かりやすい、簡潔な文章",
    "親しみやすいトーンの文章",
    "専門用語をできるだけ使わない、一般読者向けの文章",
    "言葉の使い方にこだわり、正確な表現を心がけた文章",
    "ユーモアを交えた文章",
    "シンプルかつわかりやすい文法を使った文章",
    "面白く、興味深い内容を伝える文章",
    "具体的でイメージしやすい表現を使った文章",
    "人間味のある、感情や思いを表現する文章",
    "引用や参考文献を適切に挿入した、信頼性の高い文章",
    "読み手の興味を引きつけるタイトルやサブタイトルを使った文章",
    "統計データや図表を用いたわかりやすい文章",
    "独自の見解や考え方を示した、論理的な文章",
    "問題提起から解決策までを網羅した、解説的な文章",
    "ニュース性の高い、旬なトピックを取り上げた文章",
    "エンターテイメント性のある、軽快な文章",
    "読者の関心に合わせた、専門的な内容を深く掘り下げた文章",
    "人物紹介やインタビューを取り入れた、読み物的な文章",
]

# chatGPTにリクエストするためのメソッドを設定。引数には書いてほしい内容と文章のテイストと最大文字数を指定
def run_gpt(content_text_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt):
    # リクエスト内容を決める
    request_to_gpt = content_text_to_gpt + " また、これを記事として読めるように、記事のタイトル、目次、内容の順番で出力してください。内容は"+ content_maxStr_to_gpt + "文字以内で出力してください。" + "また、文章は" + content_kind_of_to_gpt + "にしてください。"
    
    # 決めた内容を元にclient.chat.completions.createでchatGPTにリクエスト。オプションとしてmodelにAIモデル、messagesに内容を指定
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": request_to_gpt },
        ],
    )

    # 返って来たレスポンスの内容はresponse.choices[0].message.content.strip()に格納されているので、これをoutput_contentに代入
    output_content = response.choices[0].message.content.strip()
    return output_content # 返って来たレスポンスの内容を返す


# タイトル
st.title('📚 学びたい内容に合った本をおすすめ！')

# 書かせたい内容
content_text_to_gpt = st.sidebar.text_input("書かせたい内容を入力してください！")
            
# 書かせたい内容のテイストを選択肢として表示する
content_kind_of_to_gpt = st.sidebar.selectbox("文章の種類",options=content_kind_of)

# chatGPTに出力させる文字数
content_maxStr_to_gpt = str(st.sidebar.slider('記事の最大文字数', 100,3000,1000))

output_content_text = run_gpt(content_text_to_gpt,content_kind_of_to_gpt,content_maxStr_to_gpt)
st.write(output_content_text)


# Google Books API検索関数
def search_books(query, category, api_key):
    base_url = "https://www.googleapis.com/books/v1/volumes"
    params = {
        "q": f"{category}:{query}",
        "maxResults": 16,
        "printType": "books",
        "key": api_key
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json().get("items", [])
    return []

# メイン関数
def main():
    st.title("Google Books 検索アプリ")
    # APIkey確認用
    st.text_input("現在設定されているGoogle Books APIキー", value=books_api_key, type="password")
        
    search_options = ["DX", "生成AI", "デジタルマーケティング", "Python", "プログラミング", "WEBアプリ開発"]
    search_type = st.radio("検索方法を選択", ["選択肢から検索", "自由入力"])
    
    query = ""
    if search_type == "選択肢から検索":
        selected_options = st.multiselect("検索ワードを選択（複数可）", search_options)
        query = " ".join(selected_options)
    else:
        query = st.text_input("検索ワードを入力してください")

    category_dict = {"タイトル": "intitle", "著者": "inauthor", "ジャンル": "subject"}
    category = st.selectbox("検索カテゴリを選択", list(category_dict.keys()))

    if "saved_books" not in st.session_state:
        st.session_state.saved_books = []

    if st.button("検索") and books_api_key and query:
        books = search_books(query, category_dict[category], books_api_key)
        if books:
            cols = st.columns(4)
            for i, book in enumerate(books):
                with cols[i % 4]:
                    volume_info = book.get("volumeInfo", {})
                    title = volume_info.get("title", "タイトル不明")
                    authors = ", ".join(volume_info.get("authors", ["著者不明"]))
                    thumbnail = volume_info.get("imageLinks", {}).get("thumbnail", "")
                    book_url = volume_info.get("infoLink", "#")

                    st.markdown(f"#### [{title}]({book_url})", unsafe_allow_html=True)
                    st.write(f"著者: {authors}")
                    if thumbnail:
                        st.image(thumbnail, width=150)

                    # ボタンのキーをユニークにする
                    if st.button(f"⭐ 気になる", key=f"save_{title}_{i}"):
                        new_book = {
                            "追加した日": datetime.datetime.now().strftime("books_addedtime"),
                            "タイトル": title,
                            "著者": authors,
                            "URL": book_url,
                            "サムネイル": thumbnail
                        }
                        if new_book not in st.session_state.saved_books:
                            st.session_state.saved_books.append(new_book)
                    st.markdown("---")
        else:
            st.write("該当する本が見つかりませんでした。")

    # 読みたい本の一覧を表形式で表示
    st.subheader("📚 読みたいに追加した本（表形式）")
    if st.session_state.saved_books:
        row = {"追加した日時":record["books_addedtime"]}
        row.update(record["new_book"])
        records_list.append(row)
        df = pd.DataFrame(st.session_state.saved_books)
        st.table(df)
    else:
        st.info("まだ記録がありません。")

if __name__ == "__main__":
    main()

# 6 つの分野
categories = ["Python", "生成AI", "BIツール", "自動化ツール", "デジタルマーケティング", "データ分析"]

# session_state に履歴がない場合は初期化
if "history" not in st.session_state:
    st.session_state.history = []

# 学習レベル入力フォーム
st.subheader("🔹 各分野のレベルを選択してください（1: 初心者 〜 5: マスター）")

with st.form("level_form"):
    levels = {category: st.slider(category, 1, 5, 3) for category in categories}
    submitted = st.form_submit_button("記録する")

    if submitted:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.history.append({"levels": levels.copy(), "time": timestamp})
        st.success("✅ 学習レベルを記録しました！")

# レーダーチャートを描画する関数
def draw_radar_chart(levels):
    if not plotly_available:
        return  # `plotly` がない場合はスキップ

    values = list(levels.values()) + [list(levels.values())[0]]  # 最後に最初の値を追加して閉じる
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories + [categories[0]],
        fill='toself',
        name='学習レベル'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[1, 5]
            )
        ),
        showlegend=False
    )
    
    st.plotly_chart(fig)

# # 過去の記録を表示
st.subheader("📜 学習履歴とレーダーチャート")

if st.session_state.history:
    # 最新のデータでレーダーチャートを描画
    latest_record = st.session_state.history[-1]
    draw_radar_chart(latest_record["levels"])
    
    # 過去の記録をDataFrameに変換
    records_list = []
    for record in st.session_state.history:
        row = {"日時": record["time"]}
        row.update(record["levels"])
        records_list.append(row)
    
    df = pd.DataFrame(records_list)
    
    st.write("### 🕒 過去の記録（表形式）")
    # st.write(df)  
    # st.dataframe(width=100, height=100) 
    st.table(df) # データフレームの表示（スタイルなし）
else:
    st.info("まだ記録がありません。")



st.write('DataFrame') # テキストの表示

df = pd.DataFrame(
    np.random.rand(20, 3),
    columns=['a', 'b', 'c']
)   # データフレームの作成

st.line_chart(df) # 折れ線グラフの表示

df = pd.DataFrame(
    np.random.rand(100, 2)/[50, 50] + [35.69, 139.70],
    columns=['lat', 'lon']
)



# メモ：img = Image.open('pic/img031.jpg') # 画像の読み込み
# メモ：st.image(img, caption='sample', use_column_width=True) # 画像の表示

st.write('Interactive Widgets') # ウィジェットの表示

text = st.sidebar.text_input('学びたい内容を入力してください') # テキスト入力
'あなたが学びたい内容：', text # テキスト表示

condition = st.sidebar.slider('あなたの今の調子は？', 0, 100, 50) # スライダー
'コンディション：', condition # テキスト表示
