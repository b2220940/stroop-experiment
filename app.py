import streamlit as st
import random
import time

# 色と言葉の対応
colors = ["赤", "青", "緑", "黄"]
color_codes = {"赤": "red", "青": "blue", "緑": "green", "黄": "yellow"}

# ページ設定
st.set_page_config(page_title="ストループ課題", layout="centered")

# セッション状態の初期化
if "started" not in st.session_state:
    st.session_state.started = False
    st.session_state.correct = 0
    st.session_state.total = 0
    st.session_state.start_time = None
    st.session_state.mode = None  # "color" or "word"
    st.session_state.practice = True
    st.session_state.practice_end_time = None

# タイトル
st.markdown("<h2 style='text-align:center;'>ストループ課題</h2>", unsafe_allow_html=True)

# 練習フェーズ
if st.session_state.practice:
    if st.session_state.practice_end_time is None:
        st.session_state.practice_end_time = time.time() + 30  # 30秒練習

    remaining = int(st.session_state.practice_end_time - time.time())
    if remaining <= 0:
        st.session_state.practice = False
        st.session_state.started = True
        st.session_state.start_time = time.time()
        st.experimental_rerun()

    st.markdown(f"<h4 style='text-align:center;'>練習中… 残り {remaining} 秒</h4>", unsafe_allow_html=True)
else:
    if not st.session_state.started:
        if st.button("開始する", use_container_width=True):
            st.session_state.started = True
            st.session_state.start_time = time.time()
            st.experimental_rerun()
    else:
        elapsed = time.time() - st.session_state.start_time
        duration = 600  # 10分
        remaining = int(duration - elapsed)

        if remaining <= 0:
            st.markdown(f"### 終了！お疲れさまでした 😌")
            st.write(f"正答率：{st.session_state.correct}/{st.session_state.total}")
        else:
            # ランダムに「色を答える」か「言葉を答える」かを選択
            st.session_state.mode = random.choice(["color", "word"])

            # 問題生成
            text = random.choice(colors)
            ink = random.choice(colors)
            st.session_state.answer = ink if st.session_state.mode == "color" else text

            # 中央に大きく表示
            st.markdown(
                f"""
                <div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>
                {text}
                </div>
                """,
                unsafe_allow_html=True
            )

            # 質問の種類を表示
            if st.session_state.mode == "color":
                st.markdown("<h4 style='text-align:center;'>🖌 インクの色を選んでください</h4>", unsafe_allow_html=True)
            else:
                st.markdown("<h4 style='text-align:center;'>🔤 文字の意味を選んでください</h4>", unsafe_allow_html=True)

            # 選択ボタン
            cols = st.columns(2)
            for i, c in enumerate(colors):
                if cols[i % 2].button(c, use_container_width=True):
                    st.session_state.total += 1
                    if c == st.session_state.answer:
                        st.session_state.correct += 1
                    st.experimental_rerun()

            # 残り時間と成績を表示
            st.markdown(f"<p style='text-align:center;'>残り時間: {remaining} 秒</p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align:center;'>正答数: {st.session_state.correct} / {st.session_state.total}</p>", unsafe_allow_html=True)
