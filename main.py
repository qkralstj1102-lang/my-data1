import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"

st.title("🌡️ 서울의 100년간 연평균 기온 변화")
st.write("각 연도의 평균기온을 점으로 표시하여 기온 변화를 확인합니다.")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름의 불필요한 공백 제거
    df.columns = df.columns.str.strip()

    return df


try:
    df = load_data()

    # 필요한 열 확인
    if "날짜" not in df.columns or "평균기온" not in df.columns:
        st.error("날짜 또는 평균기온 열을 찾을 수 없습니다.")
        st.write("현재 열 이름:", list(df.columns))
        st.stop()

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 평균기온 숫자로 변환
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

    # 제목
    first_year = int(yearly_temp["연도"].min())
    last_year = int(yearly_temp["연도"].max())

    st.subheader(
        f"📊 {first_year}년 ~ {last_year}년 서울 연평균 기온"
    )

    # 불연속적인 점 그래프
    st.scatter_chart(
        yearly_temp,
        x="연도",
        y="평균기온",
        x_label="연도",
        y_label="연평균 기온 (℃)",
        height=500
    )

    # 통계
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "최저 연평균 기온",
            f"{yearly_temp['평균기온'].min():.1f} ℃"
        )

    with col2:
        st.metric(
            "최고 연평균 기온",
            f"{yearly_temp['평균기온'].max():.1f} ℃"
        )

    with col3:
        st.metric(
            "측정 연도",
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
        "※ 각 점은 해당 연도의 평균기온을 의미하며, 점과 점은 선으로 연결하지 않았습니다."
    )

except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.code(str(e))
