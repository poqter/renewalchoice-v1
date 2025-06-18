import streamlit as st
import pandas as pd

st.set_page_config(page_title="갱신 vs 비갱신 보험 비교", layout="wide")

st.title("📊 갱신형 vs 비갱신형 보험 납입금 비교")

# 👉 입력 영역을 왼쪽과 오른쪽으로 나눔
col_left, col_right = st.columns(2)

with col_left:
    st.header("🌀 갱신형 보험 입력")
    start_year = st.number_input("가입 연도", min_value=1900, max_value=2100, value=None, step=1)
    start_age = st.number_input("가입 당시 나이", min_value=0, max_value=100, value=None, step=1)
    renewal_cycle = st.selectbox("갱신 주기", [10, 20])
    monthly_payment = st.number_input("현재 월 납입금액 (원)", min_value=0, value=None, step=1000)

with col_right:
    st.header("🌱 비갱신형 보험 입력")
    nonrenew_monthly = st.number_input("비갱신형 월 납입금액 (원)", min_value=0, value=None, step=1000)
    nonrenew_years = st.selectbox("납입기간", [10, 15, 20, 25, 30])

# 📌 갱신형 계산 함수

def calculate_renewal_payment(age_at_start, monthly_payment, renewal_cycle):
    max_age = 90
    current_age = age_at_start
    payments = []

    if renewal_cycle == 10:
        increase_rates = [2.5166, 2.311, 1.8959, 1.3226, 1.083, 1.0624, 1.0388]
    else:
        increase_rates = [4.82, 1.5, 1.08]

    cycle = renewal_cycle
    idx = 0

    while current_age < max_age:
        years = min(cycle, max_age - current_age)
        months = years * 12

        payment = monthly_payment
        total = payment * months

        payments.append({
            "시작나이": current_age,
            "종료나이": current_age + years,
            "월납입금": round(payment),
            "기간(개월)": months,
            "기간 총액": round(total)
        })

        if idx < len(increase_rates):
            monthly_payment *= increase_rates[idx]
        else:
            monthly_payment *= increase_rates[-1]

        current_age += years
        idx += 1

    return payments

# 📌 비갱신형 계산 함수
def calculate_nonrenewal_payment(monthly_payment, pay_years):
    months = pay_years * 12
    total = monthly_payment * months
    return {
        "납입기간": f"{pay_years}년",
        "월납입금": round(monthly_payment),
        "기간(개월)": months,
        "총 납입금액": round(total)
    }

# ✅ 조건 충족 시 계산 수행
if None not in (start_year, start_age, monthly_payment, nonrenew_monthly):
    renewal_results = calculate_renewal_payment(start_age, monthly_payment, renewal_cycle)
    df_renew = pd.DataFrame(renewal_results)
    nonrenew_result = calculate_nonrenewal_payment(nonrenew_monthly, nonrenew_years)
    df_nonrenew = pd.DataFrame([nonrenew_result])

    st.subheader("🔹 갱신형 보험 납입 내역")
    st.dataframe(df_renew, use_container_width=True)

    st.subheader("🔹 비갱신형 보험 납입 내역")
    st.dataframe(df_nonrenew, use_container_width=True)

    # 비교
    total_renew = df_renew["기간 총액"].sum()
    total_nonrenew = df_nonrenew["총 납입금액"].iloc[0]
    diff = total_renew - total_nonrenew

    st.markdown("### 💰 총 납입금 비교")
    col1, col2, col3 = st.columns(3)
    col1.metric("갱신형 총액", f"{total_renew:,.0f} 원")
    col2.metric("비갱신형 총액", f"{total_nonrenew:,.0f} 원")
    col3.metric("차이", f"{diff:,.0f} 원", delta=f"{diff:,.0f} 원")

else:
    st.info("📥 모든 입력값을 채우면 자동으로 결과가 계산됩니다.")
