import streamlit as st 
import random
import math
import numpy as np
import matplotlib.pyplot as plt

# Streamlit UI 設定
st.write("### GSSM プログラミング関連授業におけるクラス全体で獲得するスキルレベルのシミュレーション")
st.sidebar.write("##### Created by Shohei ONIMARU(202540062)")
st.sidebar.write("#### パラメーター設定")

# パラメータ入力
num_trials = st.sidebar.slider("シミュレーション試行回数", 1, 100, 10)
num_students = st.sidebar.slider("学生数", 1, 32, 31)
num_sessions = st.sidebar.slider("授業コマ数（10回で1単位）", 1, 50, 30)
decay_rate = st.sidebar.slider("忘却率 λ (Ebbinghaus)", 0.05, 0.5, 0.3)
max_teach_count = st.sidebar.slider("1回の授業で教えられる最大回数", 1, 5, 3)
self_study_prob = st.sidebar.slider("自学確率", 0.0, 1.0, 0.3)
self_study_min = st.sidebar.slider("自学スキル上昇幅（最小値）", 1, 3, 1)
self_study_max = st.sidebar.slider("自学スキル上昇幅（最大値）", 1, 5, 2)

# 初期属性設定
st.sidebar.subheader("学生初期属性の比率（合計100％）")
exp_ratio = st.sidebar.slider("経験者（スキル55〜65）", 0, 100, 10)
semi_ratio = st.sidebar.slider("準経験者（スキル30〜40）", 0, 100 - exp_ratio, 10)
beg_ratio = 100 - exp_ratio - semi_ratio
st.sidebar.text(f"未経験者（スキル5〜15）: {beg_ratio}%")

# モデル定義
class Student:
    def __init__(self, skill_level, level_label, motivation):
        self.base_skill = skill_level
        self.level_label = level_label
        self.motivation = motivation
        self.teach_count = 0
        self.skill_gain_log = []
        self.current_session = 0

    def total_skill(self):
        return self.base_skill + self.get_retained_learned_skill()

    def get_retained_learned_skill(self):
        retained = 0
        for gain, session in self.skill_gain_log:
            t = self.current_session - session
            if t >= 0:
                retained += gain * math.exp(-decay_rate * t)
        return retained

    def solve_problems(self):
        skill = self.total_skill()
        if skill >= 80:
            return 0
        elif skill >= 60:
            return 1
        elif skill >= 40:
            return 2
        elif skill >= 20:
            return 3
        else:
            return 4

def initialize_students(n, exp_pct, semi_pct):
    num_exp = int(n * exp_pct / 100)
    num_semi = int(n * semi_pct / 100)
    num_beg = n - num_exp - num_semi
    return (
        [Student(random.randint(55, 65), 'Experienced', random.uniform(1.0, 1.5)) for _ in range(num_exp)] +
        [Student(random.randint(30, 40), 'Semi-Experienced', random.uniform(0.8, 1.2)) for _ in range(num_semi)] +
        [Student(random.randint(5, 15), 'Beginner', random.uniform(0.5, 1.0)) for _ in range(num_beg)]
    )

def run_simulation(students, num_rounds):
    skill_progression = []
    for session in range(num_rounds):
        random.shuffle(students)
        for s in students:
            s.teach_count = 0
            s.current_session = session

        interactions = []
        for i, student in enumerate(students):
            problems = student.solve_problems()
            for _ in range(problems):
                neighbors = []
                if i > 0:
                    neighbors.append((students[i - 1], i - 1))
                if i < len(students) - 1:
                    neighbors.append((students[i + 1], i + 1))
                better_neighbors = [(n, idx) for n, idx in neighbors if n.total_skill() > student.total_skill() and n.teach_count < max_teach_count]
                if better_neighbors:
                    teacher, teacher_idx = max(better_neighbors, key=lambda x: x[0].total_skill())
                    interactions.append((teacher_idx, i))
                    students[teacher_idx].teach_count += 1

        for teacher_idx, learner_idx in interactions:
            teacher = students[teacher_idx]
            learner = students[learner_idx]
            gap = teacher.total_skill() - learner.total_skill()
            t_gain = 0 if teacher.total_skill() <= 19 else (1 if teacher.total_skill() <= 39 else (2 if teacher.total_skill() <= 59 else 1))
            l_gain = 4 if gap >= 30 else 3 if gap >= 20 else 2 if gap >= 10 else 0

            if teacher.level_label != 'Experienced':
                teacher.skill_gain_log.append((t_gain * teacher.motivation, session))
            if learner.level_label != 'Experienced':
                learner.skill_gain_log.append((l_gain * learner.motivation, session))

        for i, s in enumerate(students):
            g = 0
            if random.random() < self_study_prob:
                g += random.randint(self_study_min, self_study_max)
            if (i > 0 and students[i - 1].level_label == 'Experienced') or (i < len(students) - 1 and students[i + 1].level_label == 'Experienced'):
                g += 1
            if s.level_label != 'Experienced' and g > 0:
                s.skill_gain_log.append((g, session))

        avg_skill = sum(s.total_skill() for s in students) / len(students)
        skill_progression.append(avg_skill)
    return skill_progression

# 複数試行平均の取得と描画
if st.sidebar.button("シミュレーション実行"):
    all_trials_progression = [0] * num_sessions
    for _ in range(num_trials):
        students = initialize_students(num_students, exp_ratio, semi_ratio)
        progression = run_simulation(students, num_sessions)
        all_trials_progression = [sum(x) for x in zip(all_trials_progression, progression)]
    avg_progression = [x / num_trials for x in all_trials_progression]

    st.write("#### 1｜クラスの平均スキルレベルの成長曲線")
    fig, ax = plt.subplots()
    ax.plot(range(1, num_sessions + 1), avg_progression, marker='o', color='#4b0082')
    ax.set_xlabel("Number of Lessons")
    ax.set_ylabel("Average Skill Level")
    ax.grid(True)
    st.pyplot(fig)

    # 平均スキル分布用のヒストグラム集計
    bins = np.arange(0, 105, 5)

    # ビンごとの人数を平均化するための累積配列を用意
    initial_hist_accum = np.zeros(len(bins) - 1)
    final_hist_accum = np.zeros(len(bins) - 1)

    for _ in range(num_trials):
        students = initialize_students(num_students, exp_ratio, semi_ratio)

        # 初期スキルヒストグラム（base_skill）
        initial_skills = [s.base_skill for s in students]
        initial_counts, _ = np.histogram(initial_skills, bins=bins)
        initial_hist_accum += initial_counts

        # 最終スキルヒストグラム（total_skill）
        run_simulation(students, num_sessions)
        final_skills = [s.total_skill() for s in students]
        final_counts, _ = np.histogram(final_skills, bins=bins)
        final_hist_accum += final_counts

    # 平均化
    initial_hist_avg = initial_hist_accum / num_trials
    final_hist_avg = final_hist_accum / num_trials

    # 描画
    st.write("#### 2｜プログラミング関連授業を通して獲得するスキル分布（Bin=5）")
    fig, ax = plt.subplots()

    # 最終スキル（濃い青）
    ax.bar(bins[:-1], final_hist_avg, width=5, align='edge',
        color='#4b0082', edgecolor='#dcdcdc', alpha=0.9, label="After Lecture")

    # 初期スキル（薄い灰色、半透明）
    ax.bar(bins[:-1], initial_hist_avg, width=5, align='edge',
        color='lightgray', edgecolor='#dcdcdc', alpha=0.6, label="Before Lecture")

    ax.set_xlabel("Skill Level")
    ax.set_ylabel("Number of Students")
    ax.legend(frameon=False)
    ax.grid(axis='y')
    st.pyplot(fig)
