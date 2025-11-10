import streamlit as st
import random
import requests
import time

# --- ページ設定 ---
st.set_page_config(page_title="ストループ課題（研究用）", layout="centered")

# --- 定数設定 ---
COLORS = ["赤", "青", "緑", "黄"]
COLOR_MAP = {"赤": "red", "青": "blue", "緑": "green", "黄": "gold"}

FORM_URL = "https://docs.google.com/forms/d/e/1FAIpQLSdF_9dHEMEPIYEWloJs0Reo9emmZq0rrjFB3oIKExmbJE7ORQ/formResponse"
ENTRIES = {
    "name": "entry.19896881",
    "temp": "entry.665886500",
    "correct": "entry.142247126",
    "total": "entry.2032695773",
    "accuracy": "entry.566413443"
}

# --- セッション状態初期化 ---
if "phase" not in st.session_state:
    st.session_state.phase = "input"  # input → practice → main → end
    st.session_state.correct = 0
    st.session_state.total = 0
    st.session_state.time_start = None
    st.session_state.practice_start = None
    st.session_state.username = ""
    st.session_state.temp = ""

# --- フェーズ① 名前・気温入力 ---
if st.session_state.phase == "input":
    st.title("ストループ課題（研究用）")

    st.session_state.username = st.text_input("名前を入力してください")
    st.session_state.temp = st.text_input("気温（℃）を入力してください")

    if st.button("練習を開始"):
        if st.session_state.username and st.session_state.temp:
            st.session_state.phase = "practice"
            st.session_state.practice_start = time.time()
            st.rerun()
        else:
            st.warning("名前と気温を入力してください。")

# --- フェーズ② 練習（30秒） ---
elif st.session_state.phase == "practice":
    elapsed = time.time() - st.session_state.practice_start
    remaining = 30 - int(elapsed)
    if remaining <= 0:
        st.session_state.phase = "message"
        st.rerun()

    st.header(f"練習残り時間: {remaining}秒")

    text = random.choice(COLORS)
    color = random.choice(COLORS)
    st.markdown(f"<h1 style='color:{COLOR_MAP[color]};font-size:60px;'>{text}</h1>", unsafe_allow_html=True)

    cols = st.columns(4)
    for c, name in zip(cols, COLORS):
        if c.button(name):
            st.rerun()

# --- フェーズ③ 練習終了メッセージ ---
elif st.session_state.phase == "message":
    st.header("✅ 練習が終わりました")
    st.write("ルールが理解できたら「本番を開始」ボタンを押してください。")
    if st.button("本番を開始"):
        st.session_state.phase = "main"
        st.session_state.time_start = time.time()
        st.session_state.correct = 0
        st.session_state.total = 0
        st.rerun()

# --- フェーズ④ 本番（10分） ---
elif st.session_state.phase == "main":
    elapsed = time.time() - st.session_state.time_start
    remaining = 600 - int(elapsed)
    if remaining <= 0:
        st.session_state.phase = "end"
        st.rerun()

    st.header(f"残り時間: {remaining//60}:{remaining%60:02d}")

    # 問題生成
    text = random.choice(COLORS)
    color = random.choice(COLORS)
    st.markdown(f"<h1 style='color:{COLOR_MAP[color]};font-size:60px;'>{text}</h1>", unsafe_allow_html=True)

    cols = st.columns(4)
    for c, name in zip(cols, COLORS):
        if c.button(name):
            st.session_state.total += 1
            if name == color:
                st.session_state.correct += 1
            else:
                st.warning("❌ 不正解！もう一度！")
            st.rerun()

# --- フェーズ⑤ 終了画面 ---
elif st.session_state.phase == "end":
    accuracy = (st.session_state.correct / st.session_state.total * 100) if st.session_state.total > 0 else 0
    st.header("🎉 お疲れさまでした！")
    st.write(f"正答数: {st.session_state.correct} / 問題数: {st.session_state.total}")
    st.write(f"正答率: {accuracy:.1f}%")

    data = {
        ENTRIES["name"]: st.session_state.username,
        ENTRIES["temp"]: st.session_state.temp,
        ENTRIES["correct"]: st.session_state.correct,
        ENTRIES["total"]: st.session_state.total,
        ENTRIES["accuracy"]: f"{accuracy:.1f}"
    }
    requests.post(FORM_URL, data=data)

    st.success("結果が自動送信されました ✅")
    st.write("この画面を閉じて終了です。")
