import streamlit as st
import random

# ----------------------------
# 各分類ごとの勘定科目リスト
# ----------------------------

# ①資産（B/S）
asset_items = [
    "現金及び預金", "受取手形", "電子記録債権", "売掛金", "リース債権", "リース投資資産",
    "有価証券", "商品及び製品", "仕掛品", "原材料及び貯蔵品", "前渡金", "前払費用",
    "繰延税金資産", "消耗品", "未収収益", "短期貸付金", "建物", "構築物", "機械及び装置",
    "船舶及び水上運搬具", "車両及びその他の陸上運搬具", "工具，器具及び備品", "土地",
    "リース資産", "建設仮勘定", "のれん", "特許権", "借地権", "地上権", "商標権",
    "実用新案権", "意匠権", "鉱業権", "漁業権", "ソフトウエア", "リース資産",
    "投資有価証券", "関係会社株式", "関係会社社債", "その他の関係会社有価証券",
    "出資金", "関係会社出資金", "長期貸付金", "株主，役員又は従業員に対する長期貸付金，関係会社長期貸付金",
    "破産更生債権等", "長期前払費用", "繰延税金資産", "創立費", "開業費", "株式交付費",
    "社債発行費", "開発費"
]

# ②負債（B/S）
liability_items = [
    "支払手形", "買掛金", "短期借入金", "リース債務", "未払金", "未払費用", "未払法人税等",
    "繰延税金負債", "前受金", "預り金", "前受収益", "引当金", "資産除去債務", "社債",
    "長期借入金", "関係会社長期借入金", "リース債務", "繰延税金負債", "引当金", "資産除去債務",
    "退職給付に係る負債"
]

# ③収益（P/L）
revenue_items = [
    "売上高", "営業収益", "受取利息", "有価証券利息", "受取配当金",
    "仕入割引その他の金融上の収益", "有価証券売却益", "有価証券評価益", "不動産賃貸料",
    "固定資産売却益", "負ののれん発生益"
]

# ④純資産（P/L）
net_assets_items = [
    "資本金", "資本剰余金", "利益剰余金", "自己株式", "その他有価証券評価差額金",
    "繰延ヘッジ損益", "土地再評価差額金", "新株予約権"
]

# ⑤費用（P/L）
expense_items = [
    "売上原価", "販売手数料", "荷造費", "運搬費", "広告宣伝費", "見本費", "保管費",
    "納入試験費", "販売及び一般管理業務に従事する役員，従業員の給料", "賃金", "手当",
    "賞与", "福利厚生ならびに販売及び一般管理部門関係の交際費", "旅費", "交通費",
    "通信費", "光熱費", "消耗品費", "租税公課", "減価償却費", "修繕費", "保険料",
    "不動産賃借料", "のれんの償却額", "支払利息", "社債利息", "社債発行費償却",
    "創立費償却", "開業費償却", "貸倒引当金繰入額または貸倒損失", "有価証券売却損",
    "売上割引", "有価証券評価損", "原材料評価損", "固定資産売却損", "減損損失", "災害損失"
]

# 選択肢の表示用テキスト（キーはボタンに表示される内容）
options = {
    "①資産": "資産",
    "②負債": "負債",
    "③収益": "収益",
    "④純資産": "純資産",
    "⑤費用": "費用"
}

# ----------------------------
# セッションステートの初期化
# ----------------------------
if "question_history" not in st.session_state:
    st.session_state.question_history = []  # 過去の出題・回答履歴を記録
if "pending_incorrect" not in st.session_state:
    st.session_state.pending_incorrect = []  # 不正解問題（正解されるまで保持）
if "correct_count" not in st.session_state:
    st.session_state.correct_count = 0
if "total_count" not in st.session_state:
    st.session_state.total_count = 0
if "current_question" not in st.session_state:
    st.session_state.current_question = None

# ----------------------------
# 問題生成関数（新規作成）
# ----------------------------
def generate_question():
    # ランダムに分類を選択し、その分類から勘定科目をランダムに選ぶ
    category_key = random.choice(list(options.keys()))
    if category_key == "①資産":
        account_item = random.choice(asset_items)
    elif category_key == "②負債":
        account_item = random.choice(liability_items)
    elif category_key == "③収益":
        account_item = random.choice(revenue_items)
    elif category_key == "④純資産":
        account_item = random.choice(net_assets_items)
    else:  # "⑤費用"
        account_item = random.choice(expense_items)
    return account_item, category_key

def generate_new_question():
    """
    不正解の問題が記憶されている場合、50%の確率でその中から1問選び、
    それ以外の場合は新規問題を生成する。
    """
    if st.session_state.pending_incorrect and random.random() < 0.5:
        q = random.choice(st.session_state.pending_incorrect)
        q["source"] = "pending"
        return q
    else:
        account_item, category_key = generate_question()
        return {"question": account_item, "correct_category": category_key, "source": "new"}

def reset_quiz():
    st.session_state.question_history = []
    st.session_state.pending_incorrect = []
    st.session_state.correct_count = 0
    st.session_state.total_count = 0
    st.session_state.current_question = generate_new_question()

# ----------------------------
# アプリメイン表示
# ----------------------------
st.write("""
    ## GSSM-会計基礎対策：取引分類クイズ""")
st.write("""
    ##### 2025.04.12 S.ONIMARU""")
st.divider()

# 「問題をランダム生成して再チャレンジ」ボタン
if st.button("問題をランダム生成して再チャレンジ"):
    reset_quiz()
    st.rerun()

# 現在の問題がなければ生成する
if st.session_state.current_question is None:
    st.session_state.current_question = generate_new_question()

# ----------------------------
# これまでの回答履歴の表示
# ----------------------------
st.subheader("これまでの回答")
if st.session_state.question_history:
    for idx, record in enumerate(st.session_state.question_history, start=1):
        st.markdown(f"**{idx}. 問題:** 『{record['question']}』")
        st.write(f"　**あなたの回答:** {record['user_answer']}　|　**正解:** {record['correct_category']}　|　**結果:** {record['result']}")
        st.markdown("---")
else:
    st.write("まだ回答はありません。")

# 現在の正答率の表示
if st.session_state.total_count > 0:
    accuracy = st.session_state.correct_count / st.session_state.total_count * 100
else:
    accuracy = 0.0
st.write("現在の正答率: {:.2f}% ({} / {})".format(accuracy, st.session_state.correct_count, st.session_state.total_count))

# ----------------------------
# クイズ終了時の処理（10問正解で終了）
# ----------------------------
if st.session_state.correct_count >= 10:
    st.balloons()
    st.success("おめでとうございます！広島カープファンの先生対策が一歩前進しました")
    st.stop()

# ----------------------------
# 現在の問題の表示
# ----------------------------
st.subheader("現在の問題")
st.write("「{}が当てはまる分類を選んでください」".format(st.session_state.current_question["question"]))
user_answer = st.radio("選択してください", list(options.keys()), key="current_answer")

if st.button("回答する", key="submit_button"):
    st.session_state.total_count += 1
    # 回答結果の記録用辞書
    record = {
        "question": st.session_state.current_question["question"],
        "correct_category": st.session_state.current_question["correct_category"],
        "user_answer": user_answer,
        "result": "",
        "source": st.session_state.current_question["source"]
    }
    if user_answer == st.session_state.current_question["correct_category"]:
        record["result"] = "正解"
        st.success("正解！")
        st.session_state.correct_count += 1
        # もし出題中の問題が不正解リストから出題された場合はリストから削除
        if st.session_state.current_question["source"] == "pending":
            for q in st.session_state.pending_incorrect:
                if (q["question"] == st.session_state.current_question["question"] and 
                    q["correct_category"] == st.session_state.current_question["correct_category"]):
                    st.session_state.pending_incorrect.remove(q)
                    break
    else:
        record["result"] = "不正解"
        st.error("不正解。再度挑戦してください。")
        # 同じ問題が不正解リストに無い場合、追加
        if not any(q["question"] == st.session_state.current_question["question"] and 
                   q["correct_category"] == st.session_state.current_question["correct_category"]
                   for q in st.session_state.pending_incorrect):
            pending_question = st.session_state.current_question.copy()
            pending_question["source"] = "pending"
            st.session_state.pending_incorrect.append(pending_question)
    # 回答履歴に追加
    st.session_state.question_history.append(record)
    # 次の問題を生成して、履歴の下に表示させる
    st.session_state.current_question = generate_new_question()
    st.rerun()
