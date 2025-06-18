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
    end_age = st.number_input("갱신 종료 나이", min_value=0, max_value=100, value=None, step=1)
    monthly_payment = st.number_input("현재 월 납입금액 (원)", min_value=0, value=None, step=1000)

with col_right:
    st.header("🌱 비갱신형 보험 입력 (선택)")
    nonrenew_monthly = st.number_input("비갱신형 월 납입금액 (원)", min_value=0, value=None, step=1000)
    nonrenew_years = st.selectbox("납입기간", [10, 15, 20, 25, 30])

# 📌 갱신형 계산 함수
def calculate_renewal_payment(age_at_start, monthly_payment, renewal_cycle, end_age):
    current_age = age_at_start
    payments = []

    if renewal_cycle == 10:
        increase_rates = [2.5166, 2.311, 1.8959, 1.3226, 1.083, 1.0624, 1.0388]
    else:
        increase_rates = [4.82, 1.5, 1.08]

    cycle = renewal_cycle
    idx = 0

    while current_age < end_age:
        years = min(cycle, end_age - current_age)
        months = years * 12
        payment = monthly_payment
        total = payment * months

        payments.append({
            "시작나이": f"{int(current_age)}세",
            "월납입금": f"{int(round(payment)):,}원",
            "기간": f"{years}년",
            "기간 총액": f"{int(round(total)):,}원"
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
    total = monthly_payment * pay_years * 12
    return {
        "납입기간": f"{pay_years}년",
        "월납입금": f"{int(round(monthly_payment)):,}원",
        "총 납입금액": f"{int(round(total)):,}원"
    }

# ✅ 결과 보기 버튼 클릭 시 계산 수행
if st.button("📊 결과 보기"):
    if None not in (start_year, start_age, end_age, monthly_payment):
        # 갱신형 계산 및 출력
        renewal_results = calculate_renewal_payment(start_age, monthly_payment, renewal_cycle, end_age)
        df_renew = pd.DataFrame(renewal_results)
        df_renew.index = df_renew.index + 1

        st.subheader("🔹 갱신형 보험 납입 내역")
        st.dataframe(df_renew, use_container_width=True)

        total_renew = sum([int(r["기간 총액"].replace(",", "").replace("원", "")) for r in renewal_results])

        if nonrenew_monthly is not None and nonrenew_monthly > 0:
            # 비갱신형 계산 및 출력
            nonrenew_result = calculate_nonrenewal_payment(nonrenew_monthly, nonrenew_years)
            df_nonrenew = pd.DataFrame([nonrenew_result])
            df_nonrenew.index = df_nonrenew.index + 1

            st.subheader("🔹 비갱신형 보험 납입 내역")
            st.dataframe(df_nonrenew, use_container_width=True)

            total_nonrenew = int(nonrenew_result["총 납입금액"].replace(",", "").replace("원", ""))
            diff = total_renew - total_nonrenew

            # 💰 총 납입금 비교
            st.markdown("### 💰 총 납입금 비교")
            col1, col2, col3 = st.columns(3)
            col1.metric("갱신형 총액", f"{total_renew:,.0f} 원")
            col2.metric("비갱신형 총액", f"{total_nonrenew:,.0f} 원")

            # ✅ 차이 항목 - 크기 키우고 색상 반영
            with col3:
                st.markdown("**차이**")
                if diff > 0:
                    st.markdown(
                        f"<span style='color:red; font-size:1.5rem; font-weight:bold;'>-{abs(diff):,} 원</span>",
                        unsafe_allow_html=True
                    )
                else:
                    st.markdown(
                        f"<span style='font-size:1.5rem; font-weight:bold;'>{abs(diff):,} 원</span>",
                        unsafe_allow_html=True
                    )

            st.success("✅ 추천: 비갱신형 전환 시 총 납입금이 절감되어 장기적으로 유리할 수 있습니다.")
        else:
            # 비갱신형 입력 없을 경우
            st.markdown("### 💰 총 납입금")
            st.metric("갱신형 총액", f"{total_renew:,.0f} 원")
    else:
        st.warning("❗ 갱신형 보험 입력값을 모두 입력해주세요.")
