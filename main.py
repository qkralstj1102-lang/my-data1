import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

st.title("🌡️ 서울의 100년간 연평균 기온 변화")
st.write("서울의 기온 데이터를 이용하여 연도별 평균기온의 변화를 확인합니다.")


@st.cache_data
def load_data():
    # CSV 불러오기
    df = pd.read_csv(DATA_URL)

    # 열 이름 앞뒤의 공백 제거
    df.columns = df.columns.str.strip()

    return df


try:
    df = load_data()

    # 날짜 열 확인
    if "날짜" not in df.columns:
        st.error("날짜 열을 찾을 수 없습니다.")
        st.write("현재 데이터의 열 이름:", list(df.columns))
        st.stop()

    # 평균기온 열 확인
    if "평균기온" not in df.columns:
        st.error("평균기온 열을 찾을 수 없습니다.")
        st.write("현재 데이터의 열 이름:", list(df.columns))
        st.stop()

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 평균기온을 숫자로 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 잘못된 데이터 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
        .reset_index()
        .sort_values("연도")
    )

    if len(yearly_temp) == 0:
        st.error("분석할 기온 데이터가 없습니다.")
        st.stop()

    # 기간
    first_year = int(yearly_temp["연도"].min())
    last_year = int(yearly_temp["연도"].max())

    st.subheader(
        f"📈 {first_year}년 ~ {last_year}년 서울 연평균 기온 변화"
    )

    # 그래프
    chart_data = yearly_temp.set_index("연도")

    st.line_chart(
        chart_data["평균기온"],
        height=500
    )

    # 통계
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

    # 데이터 확인
    with st.expander("연도별 평균기온 데이터 보기"):
        display_df = yearly_temp.copy()
        display_df["평균기온"] = display_df["평균기온"].round(2)

        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True
        )

    st.caption(
        "※ 연평균 기온은 각 연도의 일별 평균기온을 평균하여 계산했습니다."
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.write("오류 내용:")
    st.code(str(e))

    st.info(
        "위에 표시된 오류 내용을 확인하면 정확한 원인을 찾을 수 있습니다."
    )
