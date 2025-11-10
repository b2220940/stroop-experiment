import streamlit as st
import random
import time
import requests

# --- 色と言葉の設定 ---
colors = ["赤", "青", "緑", "黄"]
color_codes = {"赤": "red", "青": "blue", "緑": "green", "黄": "yellow"}

st.set_page_config(page_title="ストループ課題", layout="centered")

# --- Googleフォームの送信設定（変更不要） ---
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
    st.session_state.q_start_time = None
    st.session_state.current_question = None
    st.session_state.mode = None
    st.session_state.correct_answer = None
    st.session_state.last_incorrect = 0.0  # タイムスタンプ（不正解フィードバック用）

practice_duration = 30
main_duration = 600  # 10分
question_time_limit = 10  # 各問題の制限時間（秒）

# --- ヘルパー ---
def generate_question():
    text = random.choice(colors)
    ink = random.choice(colors)
    mode = random.choice(["color", "word"])
    correct_answer = ink if mode == "color" else text
    return text, ink, mode, correct_answer

def new_question():
    text, ink, mode, correct_answer = generate_question()
    st.session_state.current_question = (text, ink, mode, correct_answer)
    st.session_state.q_start_time = time.time()

# メタリフレッシュ（1秒おき） — タイマーを確実に減らすため
# リフレッシュはすべてのページで有効にしてOK（session_stateは維持される）
st.markdown('<meta http-equiv="refresh" content="1">', unsafe_allow_html=True)

# --- 1️⃣ 名前入力フェーズ ---
if st.session_state.phase == "input":
    st.markdown("<h2 style='text-align:center;'>ストループ課題（実験）</h2>", unsafe_allow_html=True)
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
            new_question()
            st.experimental_rerun()

# --- 2️⃣ 練習フェーズ ---
elif st.session_state.phase == "practice":
    elapsed = time.time() - st.session_state.start_time
    remaining = int(practice_duration - elapsed)

    st.markdown("<h3 style='text-align:center;'>練習中（30秒）</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='text-align:center;'>練習残り時間: {max(0, remaining)} 秒</p>", unsafe_allow_html=True)

    # 練習問題は本番と同様に表示するが、集計はしない
    text, ink, mode, correct_answer = st.session_state.current_question

    st.markdown(
        f"<div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>{text}</div>",
        unsafe_allow_html=True
    )

    st.markdown(
        f"<p style='text-align:center;'>{'🖌 インクの色を選んでください' if mode=='color' else '🔤 文字の意味を選んでください'}</p>",
        unsafe_allow_html=True
    )

    cols = st.columns(2)
    for i, c in enumerate(colors):
        if cols[i % 2].button(c, use_container_width=True):
            # 練習では不正解でも次へ（フィードバックは軽め）
            if c == correct_answer:
                new_question()
            else:
                st.warning("練習：不正解です。次の問題を表示します。")
                new_question()
            st.experimental_rerun()

    if remaining <= 0:
        st.session_state.phase = "wait"
        st.experimental_rerun()

# --- 3️⃣ 本番前待機フェーズ ---
elif st.session_state.phase == "wait":
    st.markdown("<h2 style='text-align:center;'>練習が終了しました</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align:center;'>これから本番を開始します。準備ができたら「開始」ボタンを押してください。</p>", unsafe_allow_html=True)
    if st.button("開始", use_container_width=True):
        st.session_state.phase = "main"
        st.session_state.start_time = time.time()
        st.session_state.correct = 0
        st.session_state.total = 0
        new_question()
        st.experimental_rerun()

# --- 4️⃣ 本番フェーズ ---
elif st.session_state.phase == "main":
    elapsed = time.time() - st.session_state.start_time
    remaining = int(main_duration - elapsed)

    if remaining <= 0:
        st.session_state.phase = "end"
        st.experimental_rerun()
    else:
        # show header/timers
        st.markdown("<h3 style='text-align:center;'>本番</h3>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align:center;'>残り時間: {remaining} 秒</p>", unsafe_allow_html=True)

        # current question
        text, ink, mode, correct_answer = st.session_state.current_question
        q_elapsed = time.time() - st.session_state.q_start_time
        q_remaining = max(0, int(question_time_limit - q_elapsed))

        # main problem display
        st.markdown(
            f"<div style='text-align:center; font-size:70px; font-weight:bold; color:{color_codes[ink]};'>{text}</div>",
            unsafe_allow_html=True
        )

        st.markdown(
            f"<h4 style='text-align:center;'>{'🖌 インクの色を選んでください' if mode=='color' else '🔤 文字の意味を選んでください'}</h4>",
            unsafe_allow_html=True
        )

        # show this-question remaining
        st.markdown(f"<p style='text-align:center;'>この問題の残り時間: {q_remaining} 秒</p>", unsafe_allow_html=True)

        # buttons
        cols = st.columns(2)
        answered_now = False
        for i, c in enumerate(colors):
            if cols[i % 2].button(c, use_container_width=True):
                # mark that participant attempted this question
                st.session_state.total += 1
                answered_now = True
                if c == correct_answer:
                    st.session_state.correct += 1
                    new_question()  # advance to next question
                else:
                    # incorrect: count it (we already incremented total), but do NOT advance
                    st.session_state.last_incorrect = time.time()
                st.experimental_rerun()

        # timeout handling: if q_elapsed exceeds limit, count as incorrect and advance
        if q_elapsed > question_time_limit:
            st.session_state.total += 1
            st.session_state.last_incorrect = time.time()
            st.warning("時間切れ！次の問題に進みます。")
            new_question()
            st.experimental_rerun()

        # show counts
        st.markdown(f"<p style='text-align:center;'>正答数: {st.session_state.correct} / {st.session_state.total}</p>", unsafe_allow_html=True)

        # --- 不正解フィードバックオーバーレイ（1秒だけ表示） ---
        if time.time() - st.session_state.last_incorrect < 1.0:
            # big red banner / overlay
            st.markdown(
                """
                <div style="
                  position:fixed;
                  top:20%;
                  left:50%;
                  transform:translate(-50%, -50%);
                  background-color: rgba(220,20,60,0.95);
                  color: white;
                  padding: 20px 30px;
                  font-size: 28px;
                  border-radius: 12px;
                  z-index: 9999;
                  text-align:center;
                ">
                ❌ 不正解！もう一度（または時間切れで次へ） 
                </div>
                """,
                unsafe_allow_html=True
            )

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
    except Exception:
        st.warning("データ送信に失敗しました。")
