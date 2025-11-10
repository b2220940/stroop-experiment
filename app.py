import streamlit as st
import random
import time

# --- 色と言葉の設定 ---
colors = ["赤", "青", "緑", "黄"]
color_codes = {"赤": "red", "青": "blue", "緑": "green", "黄": "yellow"}

st.set_page_config(page_title="ストループ課題", layout="centered")

# --- セッション初期化 ---
if "phase" not in st.session_state:
    st.session_state.phase = "practice"  # practice → main → end
    st.session_state.correct = 0
    st.session_state.total = 0
    st.session_state.start_time = time.time()

# --- 練習時間（秒）と本番時間（秒） ---
practice_duration = 30
main_duration = 600

# --- 練習フェーズ ---
if st.session_state.phase == "practice":
    elapsed = time.time() - st.session_state.start_time
    remaining = int(practice_duration - elapsed)

    st.markdown("<h2 style='text-align:center;'>ストループ課題（練習）</h2>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>練習残り時間: {max(0, remaining)} 秒</p>", unsafe_allow_html=True)

    # 問題を出す
    text = random.choice(colors)
    ink = random.choice(colors)
    mode = random.choice(["color", "word"])
    correct_answer = ink if mode == "color" else text

    st.markdown(
        f"""
        <div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>
        {text}
        </div>
        """,
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

    if remaining <= 0:
        st.session_state.phase = "main"
        st.session_state.start_time = time.time()
        st.rerun()

# --- 本番フェーズ ---
elif st.session_state.phase == "main":
    elapsed = time.time() - st.session_state.start_time
    remaining = int(main_duration - elapsed)

    if remaining <= 0:
        st.session_state.phase = "end"
        st.rerun()
    else:
        st.markdown("<h2 style='text-align:center;'>ストループ課題（本番）</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>残り時間: {remaining} 秒</p>", unsafe_allow_html=True)

        text = random.choice(colors)
        ink = random.choice(colors)
        mode = random.choice(["color", "word"])
        correct_answer = ink if mode == "color" else text

        st.markdown(
            f"""
            <div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>
            {text}
            </div>
            """,
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

# --- 終了フェーズ ---
elif st.session_state.phase == "end":
    accuracy = round(st.session_state.correct / st.session_state.total * 100, 1) if st.session_state.total > 0 else 0
    st.markdown("<h2 style='text-align:center;'>実験終了！</h2>", unsafe_allow_html=True)
    st.markdown(
        f"<p style='text-align:center;'>正答数：{st.session_state.correct} / {st.session_state.total}<br>正答率：{accuracy}%</p>",
        unsafe_allow_html=True
    )
    st.balloons()
