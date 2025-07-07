import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ✅ 한글 폰트 설정 (같은 폴더 내 NanumGothic-Bold.ttf)
font_path = "NanumGothic-Bold.ttf"
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['axes.unicode_minus'] = False

# ✅ 데이터 파일 경로
DATA_FILE = "monthly_spending.csv"

# ✅ 소비 조언 생성 함수
def analyze_spending(spending_data, monthly_budget):
    total_spent = sum(item['amount'] for item in spending_data)
    tips = []

    if total_spent > monthly_budget:
        tips.append(f"예산 초과! 설정한 월 예산({monthly_budget:,}원)을 {total_spent - monthly_budget:,}원 초과했습니다.")
    elif total_spent > monthly_budget * 0.9:
        tips.append("예산의 90% 이상을 지출했습니다. 남은 기간 동안 지출을 줄이는 것이 좋습니다.")
    elif total_spent < monthly_budget * 0.5:
        tips.append("예산의 절반 이하만 지출 중입니다. 너무 과도한 절약은 스트레스를 유발할 수 있어요.")
    else:
        tips.append("예산 내에서 잘 지출하고 있습니다. 좋은 소비 습관을 유지하세요!")

    for item in spending_data:
        category = item['category']
        amount = item['amount']

        if category == "카페" and amount > 70000:
            tips.append("카페 소비가 많습니다. 일주일 1~2회로 줄이면 절약에 도움이 됩니다.")
        elif category == "쇼핑" and amount > 100000:
            tips.append("쇼핑 지출이 높습니다. 충동구매를 줄이도록 노력해보세요.")
        elif category == "식비" and amount > 200000:
            tips.append("식비가 많은 편입니다. 외식보다는 집밥을 고려해보세요.")
        elif category == "여가" and amount > 100000:
            tips.append("여가 활동 지출이 높습니다. 무료 또는 저비용 활동도 고려해보세요.")
        elif category == "교통" and amount > 100000:
            tips.append("교통비가 높습니다. 대중교통 정기권이나 자전거 이용도 고려해보세요.")
        elif category == "기타" and amount > 150000:
            tips.append("기타 지출이 많습니다. 필요하지 않은 지출은 줄이는 것이 좋습니다.")

    saving_score = max(0, min(100, int((1 - total_spent / monthly_budget) * 100)))
    tips.append(f"📊 절약 점수: {saving_score}/100")
    recommended_saving = int(monthly_budget * 0.2)
    tips.append(f"💡 이번 달 최소 저축 권장액은 {recommended_saving:,}원입니다.")

    return tips

# ✅ Streamlit 시작
st.title("월간 소비 분석 자산 조언 시스템")

# ✅ 사용자 설정
st.sidebar.header("🔧 설정")
month = st.sidebar.selectbox("분석할 월을 선택하세요", [f"{i}월" for i in range(1, 13)])
monthly_budget = st.sidebar.slider("월 예산 설정 (원)", 100000, 1000000, 300000, step=50000)
st.write(f"### 💰 {month} 예산: {monthly_budget:,}원")

# ✅ 소비 내역 입력
st.subheader("📊 소비 내역 입력")
categories = ["식비", "카페", "쇼핑", "교통", "여가", "기타"]
spending_data = []
for category in categories:
    amount = st.number_input(f"{category} 지출 (원)", min_value=0, step=1000, key=category)
    spending_data.append({"month": month, "category": category, "amount": amount})

# ✅ 저장 및 분석
if st.button("저장 및 분석"):
    df_new = pd.DataFrame(spending_data)
    if os.path.exists(DATA_FILE):
        df_old = pd.read_csv(DATA_FILE)
        df_all = pd.concat([df_old, df_new], ignore_index=True)
    else:
        df_all = df_new
    df_all.to_csv(DATA_FILE, index=False)
    st.success(f"{month} 데이터가 저장되었습니다!")

    # ✅ 월별 지출 비교 시각화
    st.subheader("월별 지출 비교")
    pivot = df_all.pivot_table(index="category", columns="month", values="amount", aggfunc="sum", fill_value=0)
    fig, ax = plt.subplots(figsize=(10, 4))
    pivot.plot(kind="bar", ax=ax)
    plt.xticks(rotation=0, fontproperties=fontprop)
    plt.yticks(fontproperties=fontprop)
    ax.set_title("월별 지출 비교", fontproperties=fontprop)
    ax.set_ylabel("지출 금액", fontproperties=fontprop)
    ax.set_xlabel("")  # ✅ category 라벨 제거
    plt.legend(prop=fontprop)
    st.pyplot(fig)

    # ✅ 연간 평균 지출 시각화
    st.subheader("연간 평균 지출")
    avg_df = df_all.groupby("category")["amount"].mean()
    fig_avg, ax_avg = plt.subplots(figsize=(10, 4))
    avg_df.plot(kind="bar", ax=ax_avg, color="tomato")
    plt.xticks(rotation=0, fontproperties=fontprop)
    plt.yticks(fontproperties=fontprop)
    ax_avg.set_title("카테고리별 연간 평균 지출", fontproperties=fontprop)
    ax_avg.set_ylabel("지출 금액", fontproperties=fontprop)
    ax_avg.set_xlabel("")  # ✅ x축 라벨 제거
    st.pyplot(fig_avg)

# ✅ 지출 비율 원형 그래프
st.subheader("지출 비율 시각화")
if spending_data and sum([item['amount'] for item in spending_data]) > 0:
    df = pd.DataFrame(spending_data)
    df = df[df['amount'] > 0]
    fig_pie, ax_pie = plt.subplots()
    wedges, texts, autotexts = ax_pie.pie(
        df['amount'],
        labels=df['category'],
        autopct='%1.1f%%',
        startangle=90,
        textprops={'fontproperties': fontprop, 'fontsize': 12}
    )
    for text in texts + autotexts:
        text.set_fontproperties(fontprop)
    ax_pie.axis('equal')
    st.pyplot(fig_pie)
else:
    st.info("지출 금액을 입력하면 그래프가 표시됩니다.")

# ✅ 소비 조언
st.subheader("소비 조언")
total_spent = sum([item['amount'] for item in spending_data])
st.markdown(f"### 🧾 총 소비 합계: **{total_spent:,}원**")

if spending_data:
    tips = analyze_spending(spending_data, monthly_budget)
    for tip in tips:
        st.success(tip)

# ✅ 초기화 버튼
if st.button("초기화"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("데이터가 초기화되었습니다.")
