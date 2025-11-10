import streamlit as st
import random
import time

# --- 色と言葉の設定 ---
colors = ["赤", "青", "緑", "黄"]
color_codes = {"赤": "red", "青": "blue", "緑": "green", "黄": "yellow"}

st.set_page_config(page_title="ストループ課題", layout="centered")

# --- セッション変数初期化 ---
if "phase" not in st.session_state:
    st.session_state.phase = "practice"  # practice → main → end
    st.session_state.correct = 0
    st.session_state.total = 0
    st.session_state.start_time = None
    st.session_state.mode = None

# --- 練習フェーズ ---
if st.session_state.phase == "practice":
    st.markdown("<h2 style='text-align:center;'>ストループ課題 練習</h2>", unsafe_allow_html=True)
    countdown = st.empty()

    for i in range(30, 0, -1):
        countdown.markdown(f"<h4 style='text-align:center;'>練習中… 残り {i} 秒</h4>", unsafe_allow_html=True)
        time.sleep(1)
    # 練習終了後に本番へ
    st.session_state.phase = "main"
    st.session_state.start_time = time.time()
    st.experimental_rerun()

# --- 本番フェーズ ---
elif st.session_state.phase == "main":
    duration = 600  # 10分（600秒）
    elapsed = time.time() - st.session_state.start_time
    remaining = int(duration - elapsed)

    if remaining <= 0:
        st.session_state.phase = "end"
        st.experimental_rerun()
    else:
        st.markdown("<h2 style='text-align:center;'>本番</h2>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>残り時間: {remaining} 秒</p>", unsafe_allow_html=True)

        # 出題：色と文字をランダムに選択
        text = random.choice(colors)
        ink = random.choice(colors)

        # どちらを答えるか（50%ずつ）
        st.session_state.mode = random.choice(["color", "word"])
        correct_answer = ink if st.session_state.mode == "color" else text

        # 問題を中央に大きく表示
        st.markdown(
            f"""
            <div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>
            {text}
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.mode == "color":
            st.markdown("<h4 style='text-align:center;'>🖌 インクの色を選んでください</h4>", unsafe_allow_html=True)
        else:
            st.markdown("<h4 style='text-align:center;'>🔤 文字の意味を選んでください</h4>", unsafe_allow_html=True)

        # ボタン（2列）
        cols = st.columns(2)
        for i, c in enumerate(colors):
            if cols[i % 2].button(c, use_container_width=True):
                st.session_state.total += 1
                if c == correct_answer:
                    st.session_state.correct += 1
                st.experimental_rerun()

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
