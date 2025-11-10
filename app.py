import streamlit as st
import random
import time
import requests

# --- 色と言葉の設定 ---
colors = ["赤", "青", "緑", "黄"]
color_codes = {"赤": "red", "青": "blue", "緑": "green", "黄": "yellow"}

st.set_page_config(page_title="ストループ課題", layout="centered")

# --- Googleフォームの送信設定 ---
FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdF_9dHEMEPIYEWloJs0Reo9emmZq0rrjFB3oIKExmbJE7ORQ/formResponse"
ENTRY_NAME = "entry.19896881"
ENTRY_TEMP = "entry.665886500"
ENTRY_CORRECT = "entry.142247126"
ENTRY_TOTAL = "entry.2032695773"
ENTRY_ACC = "entry.566413443"

# --- セッション初期化 ---
if "phase" not in st.session_state:
    st.session_state.phase = "input"  # input → practice → wait → main → end
    st.session_state.correct = 0
    st.session_state.total = 0
    st.session_state.name = ""
    st.session_state.temp = ""
    st.session_state.start_time = None

practice_duration = 30
main_duration = 600  # 10分

# --- 1️⃣ 名前入力フェーズ ---
if st.session_state.phase == "input":
    st.markdown("<h2 style='text-align:center;'>ストループ課題 実験</h2>", unsafe_allow_html=True)
    st.text_input("氏名（フルネーム）を入力してください", key="name_input")
    st.text_input("現在の室温（例：23.5）", key="temp_input")

    if st.button("練習を開始する", use_container_width=True):
        if st.session_state.name_input.strip() == "":
            st.warning("氏名を入力してください。")
        else:
            st.session_state.name = st.session_state.name_input.strip()
            st.session_state.temp = st.session_state.temp_input.strip()
            st.session_state.phase = "practice"
            st.session_state.start_time = time.time()
            st.rerun()

# --- 2️⃣ 練習フェーズ ---
elif st.session_state.phase == "practice":
    elapsed = time.time() - st.session_state.start_time
    remaining = int(practice_duration - elapsed)

    st.markdown("<h3 style='text-align:center;'>練習中（30秒）</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>残り時間: {max(0, remaining)} 秒</p>", unsafe_allow_html=True)

    # 練習問題出題
    text = random.choice(colors)
    ink = random.choice(colors)
    mode = random.choice(["color", "word"])
    correct_answer = ink if mode == "color" else text

    st.markdown(
        f"<div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>{text}</div>",
        unsafe_allow_html=True
    )

    cols = st.columns(2)
    for i, c in enumerate(colors):
        if cols[i % 2].button(c, use_container_width=True):
            st.rerun()

    if remaining <= 0:
        st.session_state.phase = "wait"
        st.rerun()

# --- 3️⃣ 本番前待機フェーズ ---
elif st.session_state.phase == "wait":
    st.markdown("<h2 style='text-align:center;'>練習が終了しました</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>これから本番を開始します。準備ができたら「開始」ボタンを押してください。</p>", unsafe_allow_html=True)
    if st.button("開始", use_container_width=True):
        st.session_state.phase = "main"
        st.session_state.start_time = time.time()
        st.session_state.correct = 0
        st.session_state.total = 0
        st.rerun()

# --- 4️⃣ 本番フェーズ ---
elif st.session_state.phase == "main":
    elapsed = time.time() - st.session_state.start_time
    remaining = int(main_duration - elapsed)

    if remaining <= 0:
        st.session_state.phase = "end"
        st.rerun()
    else:
        st.markdown("<h3 style='text-align:center;'>本番</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>残り時間: {remaining} 秒</p>", unsafe_allow_html=True)

        text = random.choice(colors)
        ink = random.choice(colors)
        mode = random.choice(["color", "word"])
        correct_answer = ink if mode == "color" else text

        st.markdown(
            f"<div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>{text}</div>",
            unsafe_allow_html=True
        )

        if mode == "color":
            st.markdown("<h4 style='text-align:center;'>🖌 インクの色を選んでください</h4>", unsafe_allow_html=True)
        else:
            st.markdown("<h4 style='text-align:center;'>🔤 文字の意味を選んでください</h4>", unsafe_allow_html=True)

        cols = st.columns(2)
        for i, c in enumerate(colors):
            if cols[i % 2].button(c, use_container_width=True):
                st.session_state.total += 1
                if c == correct_answer:
                    st.session_state.correct += 1
                st.rerun()

        st.markdown(f"<p style='text-align:center;'>正答数: {st.session_state.correct} / {st.session_state.total}</p>", unsafe_allow_html=True)

# --- 5️⃣ 終了フェーズ ---
elif st.session_state.phase == "end":
    accuracy = round(st.session_state.correct / st.session_state.total * 100, 1) if st.session_state.total > 0 else 0
    st.markdown("<h2 style='text-align:center;'>実験終了！</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;'>お疲れさまでした。<br><br>"
        f"正答数：{st.session_state.correct} / {st.session_state.total}<br>"
        f"正答率：{accuracy}%</p>",
        unsafe_allow_html=True
    )
    st.balloons()

    # Googleフォーム送信
    try:
        data = {
            ENTRY_NAME: st.session_state.name,
            ENTRY_TEMP: st.session_state.temp,
            ENTRY_CORRECT: st.session_state.correct,
            ENTRY_TOTAL: st.session_state.total,
            ENTRY_ACC: accuracy
        }
        requests.post(FORM_URL, data=data)
        st.success("データを送信しました。")
    except Exception as e:
        st.warning("データ送信に失敗しました。")
