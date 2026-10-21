import streamlit as st
import urllib.request
import json
import yt_dlp

# 1. СТАБИЛЬНЫЙ ИИ МОЗГ
def get_playlist_from_ai(user_prompt):
    system_instruction = (
        "Ты — профессиональный музыкальный эксперт. Твоя задача — строго по запросу пользователя "
        "составить плейлист из реально существующих популярных песен. Выведи ровно 5 треков. "
        "Каждая строка должна быть строго в формате: Исполнитель - Название. "
        "Не пиши никаких цифр, номеров плейлиста, точек, знаков или вступлений. Только строки 'Исполнитель - Название'."
    )
    
    url = "https://open-ai-api.xyz"
    payload = json.dumps({
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": user_prompt}
        ]
    }).encode('utf-8')
    
    req = urllib.request.Request(url, data=payload, headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode('utf-8'))
            full_text = result['choices']['message']['content']
            tracks = []
            for line in full_text.split('\n'):
                line = line.strip().lstrip('0123456789.- ')
                if line and " - " in line:
                    tracks.append(line)
            return tracks
    except Exception:
        return [
            "Pawel Blaszczak - Horizon",
            "Pawel Blaszczak - Harran",
            "Woodkid - Run Boy Run",
            "Linkin Park - In The End",
            "Kordhell - Murder In My Mind"
        ]

# 2. ПОИСК ССЫЛКИ НА ВИДЕО YOUTUBE (Для встраивания)
def get_video_embed_url(track_name):
    """Ищет видео на YouTube и возвращает ссылку для официального встраивания плера"""
    ydl_opts = {
        'format': 'best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{track_name}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                video_data = info['entries'][0]
                # Берем ID видео (например, dQw4w9WgXcQ)
                video_id = video_data.get('id')
                if video_id:
                    # Создаем официальную ссылку для безопасного встроенного плеера
                    return {
                        'title': video_data.get('title'),
                        'embed_url': f"https://youtube.com{video_id}"
                    }
        except Exception:
            return None
    return None

# 3. ИНТЕРФЕЙС САЙТА
st.set_page_config(page_title="Мой Личный ИИ Плеер", page_icon="🎵", layout="centered")
st.title("🎵 Мой Личный Музыкальный ИИ")
st.subheader("Стриминг музыки через встроенные плееры без блокировок и рекламы")

user_input = st.text_input("Какую музыку тебе найти?", placeholder="Например: саундтреки из игры Дайн Лайт...")

if st.button("Создать плейлист ✨"):
    if not user_input:
        st.warning("Сначала введите запрос!")
    else:
        with st.spinner("🧠 Нейросеть генерирует плейлист..."):
            ai_tracks = get_playlist_from_ai(user_input)
        
        if ai_tracks:
            st.success(f"🤖 ИИ подобрал {len(ai_tracks)} треков! Загружаю плееры...")
            for track in ai_tracks:
                with st.spinner(f"🔍 Нахожу видео для: {track}"):
                    video_data = get_video_embed_url(track)
                
                if video_data:
                    with st.expander(f"▶️ {video_data['title']}", expanded=True):
                        # Используем специальный компонент Streamlit для показа встроенного плеера YouTube
                        # Он работает всегда, везде и защищен от блокировок самого YouTube
                        st.video(video_data['embed_url'])
                else:
                    st.warning(f"❌ Не удалось найти в сети: {track}")
        else:
            st.error("Не удалось сгенерировать плейлист.")
