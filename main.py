import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울 연평균 기온 변화",
    page_icon="🌡️",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


st.title("🌡️ 서울의 100년간 연평균 기온 변화")
st.write("서울의 기온 데이터를 이용하여 연도별 평균기온의 변화를 나타낸 그래프입니다.")


@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름의 불필요한 공백 제거
    df.columns = df.columns.str.strip()

    # 날짜 변환
    df["날짜"] = pd.to_datetime(df["날짜"], errors="coerce")

    # 평균기온 숫자 변환
    df["평균기온"] = pd.to_numeric(
        df["평균기온"],
        errors="coerce"
    )

    # 사용할 수 없는 데이터 제거
    df = df.dropna(subset=["날짜", "평균기온"])

    return df


try:
    df = load_data()

    # 날짜에서 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온 계산
    yearly_temp = (
        df.groupby("연도")["평균기온"]
        .mean()
    )

    # 데이터가 존재하는 전체 연도 범위 생성
    first_year = int(yearly_temp.index.min())
    last_year = int(yearly_temp.index.max())

    all_years = range(first_year, last_year + 1)

    # 존재하지 않는 연도에는 NaN을 넣음
    yearly_temp = yearly_temp.reindex(all_years)

    # 그래프용 데이터
    chart_data = pd.DataFrame({
        "연도": list(all_years),
        "평균기온": yearly_temp.values
    })

    st.subheader(
        f"📈 {first_year}년 ~ {last_year}년 서울 연평균 기온"
    )

    # 꺾은선 그래프
    # NaN이 있는 부분은 선이 연결되지 않음
    st.line_chart(
        chart_data,
        x="연도",
        y="평균기온",
        height=500
    )

    st.caption(
        "※ 실제 관측 데이터가 없는 연도는 빈 구간으로 표시됩니다."
    )


    # 통계
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "최저 연평균 기온",
            f"{yearly_temp.min():.1f} ℃"
        )

    with col2:
        st.metric(
            "최고 연평균 기온",
            f"{yearly_temp.max():.1f} ℃"
        )

    with col3:
        st.metric(
            "관측 연도 수",
            f"{yearly_temp.notna().sum()}년"
        )


    # 연도별 데이터 확인
    with st.expander("연도별 평균기온 데이터 보기"):
        display_df = chart_data.copy()
        display_df["평균기온"] = display_df["평균기온"].round(2)

        st.dataframe(
            display_df,
            hide_index=True,
            use_container_width=True
        )


except Exception as e:
    st.error("데이터를 불러오는 중 문제가 발생했습니다.")
    st.code(str(e))
