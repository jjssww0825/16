import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import os

# ✅ 한글 폰트 설정
font_path = "NanumHumanRegular.ttf"  # 올바른 폰트 파일명
fontprop = fm.FontProperties(fname=font_path)
plt.rcParams['font.family'] = fontprop.get_name()
plt.rcParams['axes.unicode_minus'] = False

# ✅ 설정
DATA_FILE = "monthly_spending.csv"
categories = ["식비", "카페", "쇼핑", "교통", "여가"]

# ✅ 사이드바
st.sidebar.header("🔧 설정")
month = st.sidebar.selectbox("월 선택", [f"{i}월" for i in range(1, 13)])
monthly_budget = st.sidebar.slider("월 예산 (원)", 100000, 1000000, 300000, step=50000)

# ✅ 제목
st.title("💰 월간 소비 분석 자산 조언 시스템")
st.write(f"### {month} 예산: {monthly_budget:,}원")

# ✅ 사용자 입력
spending_data = []
st.subheader("📊 소비 내역 입력")
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

    # ✅ 월별 지출 그래프
    st.subheader("📊 월별 지출 비교")
    pivot = df_all.pivot_table(index="category", columns="month", values="amount", aggfunc="sum", fill_value=0)
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    pivot.plot(kind="bar", ax=ax1)
    ax1.set_ylabel("지출 금액", fontproperties=fontprop)
    ax1.set_xlabel("")  # ✅ 'category' 삭제
    ax1.set_title("월별 지출 비교", fontproperties=fontprop)
    plt.xticks(rotation=0, fontproperties=fontprop)
    plt.legend(prop=fontprop)
    st.pyplot(fig1)

    # ✅ 연간 평균 지출 그래프
    st.subheader("📊 연간 평균 지출")
    avg_df = df_all.groupby("category")["amount"].mean()
    fig2, ax2 = plt.subplots(figsize=(10, 5))
    avg_df.plot(kind="bar", ax=ax2, color="tomato")
    ax2.set_ylabel("지출 금액", fontproperties=fontprop)
    ax2.set_xlabel("")  # ✅ 'category' 삭제
    ax2.set_title("카테고리별 연간 평균 지출", fontproperties=fontprop)
    plt.xticks(rotation=0, fontproperties=fontprop)
    st.pyplot(fig2)

# ✅ 데이터 초기화
if st.button("초기화"):
    if os.path.exists(DATA_FILE):
        os.remove(DATA_FILE)
        st.success("데이터가 초기화되었습니다.")
