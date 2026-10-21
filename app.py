import streamlit as st
import urllib.request
import urllib.parse
import json

# НАДЕЖНЫЙ ДВИЖОК ОНЛАЙН-ПОИСКА МУЗЫКИ
def search_music_online(query_text):
    """Ищет музыку напрямую в открытой европейской базе Deezer (100% стабильно без VPN)"""
    try:
        # Кодируем запрос (например, "dying light") для безопасного URL
        encoded_query = urllib.parse.quote(query_text)
        # Запрашиваем сразу 10 лучших треков по этому запросу
        url = f"https://deezer.com{encoded_query}&limit=10"
        
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            
            tracks_list = []
            if 'data' in res_data and len(res_data['data']) > 0:
                for track in res_data['data']:
                    # Проверяем, есть ли живой аудиопоток для стриминга
                    if 'preview' in track and track['preview']:
                        tracks_list.append({
                            'title': track['title_short'],
                            'artist': track['artist']['name'],
                            'url': track['preview'],
                            'cover': track['album']['cover_medium']
                        })
                return tracks_list
    except Exception as e:
        st.error(f"Ошибка поиска: {e}")
    return []

# ИНТЕРФЕЙС САЙТА (Streamlit)
st.set_page_config(page_title="Мой Личный Плеер", page_icon="🎵", layout="centered")

st.title("🎵 Мой Личный Музыкальный ИИ-Поиск")
st.subheader("Слушай любую музыку онлайн без рекламы, VPN и блокировок")

# Поисковая строка
user_query = st.text_input("Какую музыку или исполнителя тебе найти?", placeholder="Например: Dying Light, Linkin Park, фонк...")

if st.button("Найти музыку 🚀"):
    if not user_query:
        st.warning("Сначала введи название или группу!")
    else:
        with st.spinner("🔍 Обыскиваю глобальные музыкальные сервера..."):
            found_tracks = search_music_online(user_query)
        
        if found_tracks:
            st.success(f"🔥 Успешно найдено {len(found_tracks)} треков! Приятного прослушивания:")
            
            for track in found_tracks:
                # Создаем красивую карточку для каждой песни с обложкой альбома
                with st.container():
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        st.image(track['cover'], width=100)
                    with col2:
                        st.markdown(f"### {track['artist']} — {track['title']}")
                        # Проигрываем чистый онлайн-поток mp3 напрямую
                        st.audio(track['url'], format='audio/mp3')
                    st.markdown("---") # Разделительная полоса
        else:
            st.error("❌ Ничего не нашлось. Попробуй ввести название точнее (например, на английском).")
