import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(
    page_title="서울 기온 데이터 분석",
    page_icon="🌡️",
    layout="wide"
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/seoul.csv"


# -----------------------------
# 데이터 불러오기
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL)

    # 열 이름 공백 제거
    df.columns = df.columns.str.strip()

    # 날짜 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"],
        errors="coerce"
    )

    # 기온 데이터 숫자로 변환
    for column in ["평균기온", "최저기온", "최고기온"]:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    return df


# -----------------------------
# 데이터 분석
# -----------------------------
try:
    df = load_data()

    # 날짜가 정상적으로 입력된 데이터만 사용
    df = df.dropna(subset=["날짜"])

    # 연도 추출
    df["연도"] = df["날짜"].dt.year

    # 연도별 평균기온
    yearly_temp = df.groupby("연도")["평균기온"].mean()

    # 전체 연도 범위 생성
    first_year = int(yearly_temp.index.min())
    last_year = int(yearly_temp.index.max())

    all_years = range(first_year, last_year + 1)

    # 데이터가 없는 연도는 NaN으로 표시
    yearly_temp = yearly_temp.reindex(all_years)

    # -----------------------------
    # 제목
    # -----------------------------
    st.title("🌡️ 서울의 100년간 연평균 기온 변화")

    st.write(
        "서울의 일별 기온 데이터를 이용하여 연평균 기온의 변화를 확인하고, "
        "원본 데이터의 특성을 요약통계로 분석합니다."
    )

    # -----------------------------
    # 연평균 기온 그래프
    # -----------------------------
    st.subheader(
        f"📈 {first_year}년 ~ {last_year}년 연평균 기온 변화"
    )

    chart_df = pd.DataFrame({
        "연도": list(all_years),
        "평균기온": yearly_temp.values
    })

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df["연도"],
            y=chart_df["평균기온"],
            mode="lines+markers",
            connectgaps=False,
            name="연평균 기온"
        )
    )

    fig.update_layout(
        xaxis_title="연도",
        yaxis_title="평균기온 (℃)",
        hovermode="x unified",
        height=500
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )

    st.caption(
        "※ 관측 데이터가 없는 연도는 선으로 연결하지 않고 빈 구간으로 표시됩니다."
    )


    # -----------------------------
    # 원본 데이터 요약통계
    # -----------------------------
    st.subheader("📊 원본 데이터 요약통계")

    st.write(
        "원본 데이터에 포함된 일별 기온 자료의 개수, 평균, 최솟값, "
        "최댓값, 중앙값, 표준편차를 나타냅니다."
    )

    # 통계 대상 열
    stat_columns = [
        "평균기온",
        "최저기온",
        "최고기온"
    ]

    # 요약통계 계산
    summary = df[stat_columns].describe().T

    # 필요한 통계만 선택
    summary = summary[
        ["count", "mean", "min", "50%", "max", "std"]
    ]

    # 한글 이름으로 변경
    summary.columns = [
        "개수",
        "평균",
        "최솟값",
        "중앙값",
        "최댓값",
        "표준편차"
    ]

    summary.index = [
        "평균기온",
        "최저기온",
        "최고기온"
    ]

    # 소수점 둘째 자리까지 표시
    summary = summary.round(2)

    st.dataframe(
        summary,
        use_container_width=True
    )


    # -----------------------------
    # 데이터 개수
    # -----------------------------
    st.subheader("📋 원본 데이터 규모")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "전체 데이터 개수",
            f"{len(df):,}개"
        )

    with col2:
        st.metric(
            "관측 시작 연도",
            f"{first_year}년"
        )

    with col3:
        st.metric(
            "관측 종료 연도",
            f"{last_year}년"
        )


    # -----------------------------
    # 연평균 기온 통계
    # -----------------------------
    st.subheader("🌡️ 연평균 기온 통계")

    valid_yearly = yearly_temp.dropna()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "가장 낮은 연평균",
            f"{valid_yearly.min():.1f} ℃"
        )

    with col2:
        st.metric(
            "가장 높은 연평균",
            f"{valid_yearly.max():.1f} ℃"
        )

    with col3:
        st.metric(
            "연평균을 계산한 연도 수",
            f"{valid_yearly.count()}년"
        )


    # -----------------------------
    # 원본 데이터 보기
    # -----------------------------
    with st.expander("🔍 원본 데이터 확인하기"):
        st.dataframe(
            df.drop(columns=["연도"]),
            hide_index=True,
            use_container_width=True
        )


except Exception as e:
    st.error("데이터를 불러오거나 분석하는 중 문제가 발생했습니다.")
    st.code(str(e))
