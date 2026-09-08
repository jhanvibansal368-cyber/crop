import streamlit as st
from PIL import Image
import requests
from google import genai
from datetime import datetime
import time

# --- Your keys ---
WEATHER_API_KEY= st.secrets["WEATHER_API_KEY"]
GEMINI_API_KEY= st.secrets["GEMINI_API_KEY"]

# --- Translations dictionary ---
TEXT = {
    "English": {
        "title": "🌿 Crop Health Assistant",
        "caption": "Upload a leaf photo for disease/pest identification and localized advice",
        "city": "Enter your location (city):",
        "crop": "What crop is this?",
        "crop_options": ["Wheat", "Rice", "Cotton", "Sugarcane", "Maize", "Other"],
        "growth_stage": "Crop growth stage:",
        "growth_options": ["Seedling", "Vegetative", "Flowering", "Fruiting/Grain-filling", "Maturity"],
        "previous_crop": "What was the previous crop grown on this land?",
        "previous_options": ["None / First crop here", "Wheat", "Rice", "Cotton", "Sugarcane", "Maize", "Pulses/Legumes", "Other"],
        "soil_type": "Soil type:",
        "soil_options": ["Sandy", "Clay", "Loamy", "Silty", "Not sure"],
        "know_ph": "I know my soil pH",
        "ph_level": "Soil pH level:",
        "upload": "Upload a leaf photo",
        "button": "Analyze",
        "spinner": "Analyzing...",
        "result_header": "Analysis",
        "tab_analyze": "📸 Analyze",
        "tab_about": "ℹ️ About",
        "about_text": "This tool helps farmers identify crop diseases early using a photo, local weather, soil, and crop history — giving fast, localized advice in your own language.",
        "busy_retry": "Server busy, retrying...",
        "busy_final": "The AI service is temporarily unavailable. Please try again in a minute.",
    },
    "Hindi": {
        "title": "🌿 फसल स्वास्थ्य सहायक",
        "caption": "बीमारी/कीट पहचान और स्थानीय सलाह के लिए पत्ते की फोटो अपलोड करें",
        "city": "अपना स्थान (शहर) दर्ज करें:",
        "crop": "यह कौन सी फसल है?",
        "crop_options": ["गेहूं", "चावल", "कपास", "गन्ना", "मक्का", "अन्य"],
        "growth_stage": "फसल की वृद्धि अवस्था:",
        "growth_options": ["अंकुरण", "वानस्पतिक", "फूल आना", "फल/दाना भरना", "पकना"],
        "previous_crop": "इस भूमि पर पिछली फसल कौन सी थी?",
        "previous_options": ["कोई नहीं / पहली फसल", "गेहूं", "चावल", "कपास", "गन्ना", "मक्का", "दलहन", "अन्य"],
        "soil_type": "मिट्टी का प्रकार:",
        "soil_options": ["रेतीली", "चिकनी", "दोमट", "गादयुक्त", "पता नहीं"],
        "know_ph": "मुझे अपनी मिट्टी का pH पता है",
        "ph_level": "मिट्टी का pH स्तर:",
        "upload": "पत्ते की फोटो अपलोड करें",
        "button": "जांच करें",
        "spinner": "जांच हो रही है...",
        "result_header": "विश्लेषण",
        "tab_analyze": "📸 जांच करें",
        "tab_about": "ℹ️ जानकारी",
        "about_text": "यह उपकरण किसानों को फोटो, स्थानीय मौसम, मिट्टी और फसल इतिहास का उपयोग करके फसल की बीमारियों की जल्दी पहचान करने में मदद करता है — आपकी अपनी भाषा में त्वरित, स्थानीय सलाह के साथ।",
        "busy_retry": "सर्वर व्यस्त है, पुनः प्रयास हो रहा है...",
        "busy_final": "AI सेवा अस्थायी रूप से अनुपलब्ध है। कृपया एक मिनट में पुनः प्रयास करें।",
    },
    "Punjabi": {
        "title": "🌿 ਫਸਲ ਸਿਹਤ ਸਹਾਇਕ",
        "caption": "ਬਿਮਾਰੀ/ਕੀੜੇ ਦੀ ਪਛਾਣ ਅਤੇ ਸਥਾਨਕ ਸਲਾਹ ਲਈ ਪੱਤੇ ਦੀ ਫੋਟੋ ਅਪਲੋਡ ਕਰੋ",
        "city": "ਆਪਣਾ ਸਥਾਨ (ਸ਼ਹਿਰ) ਦਰਜ ਕਰੋ:",
        "crop": "ਇਹ ਕਿਹੜੀ ਫਸਲ ਹੈ?",
        "crop_options": ["ਕਣਕ", "ਚੌਲ", "ਕਪਾਹ", "ਗੰਨਾ", "ਮੱਕੀ", "ਹੋਰ"],
        "growth_stage": "ਫਸਲ ਦੀ ਵਾਧਾ ਅਵਸਥਾ:",
        "growth_options": ["ਅੰਕੁਰਣ", "ਬਨਸਪਤੀ", "ਫੁੱਲ ਆਉਣਾ", "ਦਾਣਾ ਭਰਨਾ", "ਪੱਕਣਾ"],
        "previous_crop": "ਇਸ ਜ਼ਮੀਨ 'ਤੇ ਪਿਛਲੀ ਫਸਲ ਕਿਹੜੀ ਸੀ?",
        "previous_options": ["ਕੋਈ ਨਹੀਂ / ਪਹਿਲੀ ਫਸਲ", "ਕਣਕ", "ਚੌਲ", "ਕਪਾਹ", "ਗੰਨਾ", "ਮੱਕੀ", "ਦਾਲਾਂ", "ਹੋਰ"],
        "soil_type": "ਮਿੱਟੀ ਦੀ ਕਿਸਮ:",
        "soil_options": ["ਰੇਤਲੀ", "ਚੀਕਣੀ", "ਦੋਮਟ", "ਗਾਦ ਵਾਲੀ", "ਪਤਾ ਨਹੀਂ"],
        "know_ph": "ਮੈਨੂੰ ਆਪਣੀ ਮਿੱਟੀ ਦਾ pH ਪਤਾ ਹੈ",
        "ph_level": "ਮਿੱਟੀ ਦਾ pH ਪੱਧਰ:",
        "upload": "ਪੱਤੇ ਦੀ ਫੋਟੋ ਅਪਲੋਡ ਕਰੋ",
        "button": "ਜਾਂਚ ਕਰੋ",
        "spinner": "ਜਾਂਚ ਹੋ ਰਹੀ ਹੈ...",
        "result_header": "ਵਿਸ਼ਲੇਸ਼ਣ",
        "tab_analyze": "📸 ਜਾਂਚ ਕਰੋ",
        "tab_about": "ℹ️ ਜਾਣਕਾਰੀ",
        "about_text": "ਇਹ ਟੂਲ ਕਿਸਾਨਾਂ ਨੂੰ ਫੋਟੋ, ਸਥਾਨਕ ਮੌਸਮ, ਮਿੱਟੀ ਅਤੇ ਫਸਲ ਦੇ ਇਤਿਹਾਸ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਫਸਲ ਦੀਆਂ ਬਿਮਾਰੀਆਂ ਦੀ ਜਲਦੀ ਪਛਾਣ ਕਰਨ ਵਿੱਚ ਮਦਦ ਕਰਦਾ ਹੈ — ਤੁਹਾਡੀ ਆਪਣੀ ਭਾਸ਼ਾ ਵਿੱਚ ਤੇਜ਼, ਸਥਾਨਕ ਸਲਾਹ ਨਾਲ।",
        "busy_retry": "ਸਰਵਰ ਰੁੱਝਿਆ ਹੋਇਆ ਹੈ, ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕੀਤੀ ਜਾ ਰਹੀ ਹੈ...",
        "busy_final": "AI ਸੇਵਾ ਅਸਥਾਈ ਤੌਰ 'ਤੇ ਉਪਲਬਧ ਨਹੀਂ ਹੈ। ਕਿਰਪਾ ਕਰਕੇ ਇੱਕ ਮਿੰਟ ਵਿੱਚ ਦੁਬਾਰਾ ਕੋਸ਼ਿਸ਼ ਕਰੋ।",
    },
}

# --- Language selector, before anything else ---
language = st.selectbox("Language / भाषा / ਭਾਸ਼ਾ", ["English", "Hindi", "Punjabi"])
t = TEXT[language]

st.title(t["title"])

tab1, tab2 = st.tabs([t["tab_analyze"], t["tab_about"]])

with tab1:
    st.caption(t["caption"])

    city = st.text_input(t["city"], "Patiala")
    crop = st.selectbox(t["crop"], t["crop_options"])
    growth_stage = st.selectbox(t["growth_stage"], t["growth_options"])
    previous_crop = st.selectbox(t["previous_crop"], t["previous_options"])
    soil_type = st.selectbox(t["soil_type"], t["soil_options"])

    know_ph = st.checkbox(t["know_ph"])
    if know_ph:
        soil_ph = st.slider(t["ph_level"], 3.0, 10.0, 6.5, step=0.1)
    else:
        soil_ph = None

    uploaded_file = st.file_uploader(t["upload"], type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, use_container_width=True)

        if st.button(t["button"]):
            with st.spinner(t["spinner"]):
                url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric"
                response = requests.get(url)
                data = response.json()

                temperature = data["main"]["temp"]
                humidity = data["main"]["humidity"]
                description = data["weather"][0]["description"]
                current_date = datetime.now().strftime("%d %B %Y")

                ph_line = f"Soil pH: {soil_ph}" if soil_ph else "Soil pH: Not known (assume typical range for this soil type)"

                prompt = f"""
                You are a crop health assistant helping a farmer.

                Date: {current_date}
                Crop: {crop}
                Growth stage: {growth_stage}
                Previous crop on this land: {previous_crop}
                Soil type: {soil_type}
                {ph_line}
                Weather: {description}, {temperature}°C, {humidity}% humidity

                Look at the attached leaf photo. Identify any visible disease or pest damage.
                Considering the crop's growth stage, soil conditions, current weather, and
                crop rotation history, provide:
                1. A short diagnosis of what you see in the photo
                2. A risk level (Low / Moderate / High) with a one-line reason
                3. A clear, practical next step the farmer should take

                Respond entirely in {language}. Use simple, clear language a farmer without
                technical background can easily understand.
                """

                client = genai.Client(api_key=GEMINI_API_KEY)

                ai_response = None
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        ai_response = client.models.generate_content(
                            model="gemini-3.6-flash",
                            contents=[prompt, image]
                        )
                        break
                    except Exception as e:
                        if attempt < max_retries - 1:
                            st.warning(f"{t['busy_retry']} ({attempt + 1}/{max_retries})")
                            time.sleep(3)
                        else:
                            st.error(t["busy_final"])
                            st.stop()

            st.subheader(t["result_header"])
            st.write(ai_response.text)
            st.balloons()

with tab2:
    st.write(t["about_text"])