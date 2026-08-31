import streamlit as st
import pandas as pd

# 페이지 설정
st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

# 데이터 주소
DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

# 제목
st.title("🌡️ 서울의 100년간 연평균 기온 변화")
st.write("서울의 일별 기온 데이터를 이용해 연도별 평균기온의 변화를 나타낸 그래프입니다.")

# 데이터 불러오기
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="cp949")

    # 날짜를 날짜 형식으로 변환
    df["날짜"] = pd.to_datetime(df["날짜"])

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(df["평균기온"], errors="coerce")

    return df


try:
    df = load_data()

    # 연도별 평균기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
        .dropna()
    )

    # 너무 최근의 불완전한 연도가 있다면 제외
    # 100년 정도의 흐름을 보기 위해 데이터가 충분한 연도만 사용
    yearly_temp = yearly_temp.sort_values("연도")

    # 전체 데이터 기간 표시
    if not yearly_temp.empty:
        first_year = int(yearly_temp["연도"].min())
        last_year = int(yearly_temp["연도"].max())

        st.subheader(f"📈 {first_year}년 ~ {last_year}년 서울 연평균 기온")

        # 그래프용 데이터
        chart_data = yearly_temp.set_index("연도")

        st.line_chart(
            chart_data,
            y="평균기온",
            x_label="연도",
            y_label="평균기온 (℃)",
            height=500
        )

        # 간단한 통계
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric(
                "가장 낮은 연평균 기온",
                f"{yearly_temp['평균기온'].min():.1f} ℃"
            )

        with col2:
            st.metric(
                "가장 높은 연평균 기온",
                f"{yearly_temp['평균기온'].max():.1f} ℃"
            )

        with col3:
            st.metric(
                "측정 연도 수",
                f"{len(yearly_temp)}년"
            )

        # 데이터 표
        with st.expander("연도별 평균기온 데이터 보기"):
            display_df = yearly_temp.copy()
            display_df["평균기온"] = display_df["평균기온"].round(2)
            st.dataframe(
                display_df,
                hide_index=True,
                use_container_width=True
            )

        st.caption(
            "※ 연평균 기온은 해당 연도의 일별 평균기온을 평균하여 계산했습니다."
        )

    else:
        st.error("기온 데이터를 불러왔지만 분석할 데이터가 없습니다.")

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.info("인터넷 연결이나 데이터 주소를 확인해 주세요.")
