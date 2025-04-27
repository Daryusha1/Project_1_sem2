import streamlit as st
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt
import random

# НАСТРОЙКИ СТРАНИЦЫ
st.set_page_config(page_title="Анализ комментариев", layout="wide")

data_files = {
    "с Блиновской": "data/sobchak_blinovskaya_ready_with_date.csv",
    "с Бузовой": "data/sobchak_buzova_ready_with_date.csv",
    "с Моргенштерном": "data/sobchak_morgenstern2_ready_with_date.csv",
}

# стиль
st.markdown("""
    <style>
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
    }
    h1, h2, h3, h4 {
        font-family: 'Poppins', sans-serif;
        font-weight: 700;
        color: #4B0082;
    }
    button {
        border-radius: 8px;
    }
    div.stButton > button:first-child {
        background-color: #e0c3fc;
        color: #4B0082;
        border: none;
        padding: 0.75em 1.5em;
        border-radius: 10px;
        font-weight: 600;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #d1b3ec;
        color: #38006b;
    }
    p {
        font-weight: 400;
    }
    </style>
""", unsafe_allow_html=True)

# ЗАГОЛОВОК
st.markdown("<h1 style='text-align: center; color: #6c5ce7;'>🎬 Анализ комментариев под тремя самыми популярными интервью Ксении Собчак</h1>", unsafe_allow_html=True)

# ВЫБОР ВИДЕО
video = st.selectbox("Выберите интервью:", list(data_files.keys()))

# загрузка данных
@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    if 'sentiment' in df.columns:
        df['sentiment'] = df['sentiment'].astype(str).str.upper().str.strip()
        df = df[df['sentiment'].isin(['POSITIVE', 'NEUTRAL', 'NEGATIVE'])]

    if 'publishedAt' in df.columns and 'published_at' not in df.columns:
        df['published_at'] = pd.to_datetime(df['publishedAt']).dt.date
    elif 'published_at' in df.columns:
        df['published_at'] = pd.to_datetime(df['published_at']).dt.date

    return df

try:
    df = load_data(data_files[video])
except FileNotFoundError:
    st.error(f"Файл не найден: {data_files[video]}")
    st.stop()

# СТОП-СЛОВА 
russian_stopwords = set(STOPWORDS)
russian_stopwords.update([
    "это", "как", "в", "на", "я", "с", "что", "он", "она", "мы", "вы", "у",
    "к", "от", "до", "за", "по", "из", "под", "без", "для", "и", "но", "да",
    "или", "то", "же", "бы", "быть", "их", "так", "тоже", "очень", "еще"
])

# цвета
pastel_colors = px.colors.qualitative.Pastel

# --- ВКЛАДКИ ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["📋 Сводка", "☁️ Облако слов", "📊 Тональность", "🏆 Топ комментариев", "📝 Лайки", "📅 Динамика", "🧠 Выводы"])

# СВОДКА 
with tab1:
    st.header("📋 Общая информация")
    st.subheader(f"Интервью: {video}")
    st.write(f"Количество анализируемых комментариев: {len(df)}")
    st.dataframe(df.head(10))

# ОБЛАКО СЛОВ 
with tab2:
    st.header("☁️ Облако слов из комментариев")
    text = " ".join(df['clean_text'].dropna())
    filtered_words = [word for word in text.split() if word.lower() not in russian_stopwords]
    filtered_text = " ".join(filtered_words)

    regenerate = st.button("🔄 Перегенерировать облако слов")

    if filtered_text and (regenerate or not regenerate):
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap=random.choice(['Pastel1', 'Pastel2', 'cool', 'spring']),
            max_words=200
        ).generate(filtered_text)

        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    else:
        st.warning("Нет текста для создания облака слов.")

# ТОНАЛЬНОСТЬ
with tab3:
    st.header("📊 Распределение тональности комментариев")
    if 'sentiment' in df.columns:
        fig = px.pie(df, names='sentiment', title="Тональность комментариев", hole=0.4, color_discrete_sequence=pastel_colors)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных о тональности.")

# ТОП КОММЕНТАРИЕВ 
with tab4:
    st.header("🏆 Топ-5 комментариев по лайкам")
    if 'likes' in df.columns:
        for sentiment in ['POSITIVE', 'NEUTRAL', 'NEGATIVE']:
            st.subheader(sentiment.capitalize())
            subset = df[df['sentiment'] == sentiment].sort_values(by='likes', ascending=False).head(5)
            if not subset.empty:
                for idx, row in subset.iterrows():
                    st.markdown(f"<div style='background-color: #dfe6e9; padding: 10px; border-radius: 5px; margin-bottom: 10px;'>"
                                f"<b>👍 {row['likes']} лайков</b><br>{row['text']}</div>", unsafe_allow_html=True)
            else:
                st.write("Нет комментариев для этой тональности.")
    else:
        st.warning("Нет данных о лайках.")

# ЛАЙКИ
with tab5:
    st.header("📝 Лайки по тональностям")
    if 'likes' in df.columns:
        likes_by_sentiment = df.groupby('sentiment')['likes'].sum().reset_index()
        fig = px.bar(likes_by_sentiment, x='sentiment', y='likes', color='sentiment', text='likes', color_discrete_sequence=pastel_colors)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных о лайках.")

# ДИНАМИКА 
with tab6:
    st.header("📅 Динамика тональности по дням")
    if 'published_at' in df.columns:
        daily_sentiment = df.groupby(['published_at', 'sentiment']).size().reset_index(name='counts')
        fig = px.line(daily_sentiment, x='published_at', y='counts', color='sentiment', markers=True,
                      title="Изменение тональности по дням", color_discrete_sequence=pastel_colors)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Нет данных о дате публикации.")

# ВЫВОДЫ
with tab7:
    st.header("Выводы по гостям")

    positive_count = (df['sentiment'] == 'POSITIVE').sum()
    neutral_count = (df['sentiment'] == 'NEUTRAL').sum()
    negative_count = (df['sentiment'] == 'NEGATIVE').sum()

    col1, col2, col3 = st.columns(3)
    col1.success(f"✅ Позитивных комментариев: {positive_count}")
    col2.info(f"➖ Нейтральных комментариев: {neutral_count}")
    col3.error(f"❌ Негативных комментариев: {negative_count}")

    st.markdown("---")

    max_sentiment = max(
        [('Позитивное', positive_count), ('Нейтральное', neutral_count), ('Негативное', negative_count)],
        key=lambda x: x[1]
    )[0]

    if max_sentiment == 'Позитивное':
        st.success("Итог: скорее позитивное восприятие гостя!")
    elif max_sentiment == 'Нейтральное':
        st.info("Итог: нейтральное восприятие гостя!")
    else:
        st.error("Итог: скорее негативное восприятие гостя...")
