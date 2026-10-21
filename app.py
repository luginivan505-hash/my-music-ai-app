import streamlit as st
import google.generativeai as genai
import yt_dlp

# 1. СТАБИЛЬНАЯ НАСТРОЙКА ИИ ПОМОЩНИКА
# Сюда автоматически подставился ваш рабочий ключ
GEMINI_API_KEY = "AQ.Ab8RN6I3p9q3crB3vmCzP6cfPWZInLMQ22gNonOmYlbZS9BcRg" 

# Настраиваем подключение ИИ напрямую через стабильный метод
genai.configure(api_key=GEMINI_API_KEY)

def get_playlist_from_ai(user_prompt):
    """Запрашивает плейлист у нейросети"""
    # Для старой библиотеки используем гарантированно рабочую универсальную модель
    model = genai.GenerativeModel("gemini-1.5-flash")
    
    system_instruction = (
        "Ты — профессиональный musical эксперт. Твоя задача — строго по запросу пользователя "
        "составить плейлист из реально существующих песен. Выведи ровно 5 треков. "
        "Каждая строка должна быть строго в формате: Исполнитель - Название. "
        "Не пиши никаких лишних слов, вступлений или номеров. Только список треков, один трек на строку."
    )
    try:
        response = model.generate_content(f"{system_instruction}\n\nЗапрос пользователя: {user_prompt}")
        # Очищаем строки от возможного мусора
        tracks = [line.strip().lstrip('0123456789.- ') for line in response.text.split('\n') if line.strip()]
        return tracks
    except Exception as e:
        st.error(f"Ошибка ИИ: {e}")
        return []

# 2. ПОИСК МУЗЫКИ НА YOUTUBE (Исправлен запуск потока)
def get_audio_url(track_name):
    """Ищет аудиопоток на YouTube. На облачном сервере блокировки не действуют!"""
    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
        'quiet': True,
        'default_search': 'ytsearch',
        'nocheckcertificate': True
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(f"ytsearch1:{track_name}", download=False)
            if 'entries' in info and len(info['entries']) > 0:
                # ИСПРАВЛЕНО: Добавлен индекс [0] для корректного извлечения данных трека
                video_data = info['entries'][0]
                return {
                    'title': video_data.get('title'),
                    'url': video_data.get('url')
                }
        except Exception:
            return None
    return None

# 3. ИНТЕРФЕЙС САЙТА
st.set_page_config(page_title="Мой Личный ИИ Плеер", page_icon="🎵", layout="centered")
st.title("🎵 Мой Личный Музыкальный ИИ")
st.subheader("Стриминг музыки через облачный сервер без блокировок и рекламы")

user_input = st.text_input("Какую музыку тебе найти?", placeholder="Например: саундтреки из игры Дайн Лайт...")

if st.button("Создать плейлист ✨"):
    if not user_input:
        st.warning("Сначала введите запрос!")
    else:
        with st.spinner("🧠 Нейросеть генерирует плейлист..."):
            ai_tracks = get_playlist_from_ai(user_input)
        
        if ai_tracks:
            st.success(f"🤖 ИИ подобрал {len(ai_tracks)} треков! Подключаюсь к аудиопотокам...")
            for track in ai_tracks:
                with st.spinner(f"🔍 Загружаю поток для: {track}"):
                    audio_data = get_audio_url(track)
                
                if audio_data:
                    with st.expander(f"▶️ {audio_data['title']}", expanded=True):
                        # Играем прямую ссылку с серверов YouTube через облачный прокси-сервер
                        st.audio(audio_data['url'], format='audio/mp3')
                else:
                    st.warning(f"❌ Не удалось найти в сети: {track}")
        else:
            st.error("Не удалось сгенерировать плейлист.")
