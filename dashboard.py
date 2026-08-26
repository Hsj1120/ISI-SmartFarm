import random
from datetime import datetime

import pandas as pd
import streamlit as st


# =========================================================
# Streamlit 기본 설정
# =========================================================
st.set_page_config(
    page_title="ISI Smart Farm Monitoring",
    page_icon="🌱",
    layout="wide",
)


# =========================================================
# 스마트팜 기본 데이터
# 실제 센서 연동 시 이 부분을 센서 API 데이터로 변경하면 됨
# =========================================================
FARMS = {
    "1조": {
        "crop": "상추",
        "temp": 23.4,
        "humidity": 61,
        "light": 720,
        "soil": 48,
        "led": True,
    },

    "2조": {
        "crop": "바질",
        "temp": 27.8,
        "humidity": 58,
        "light": 510,
        "soil": 39,
        "led": True,
    },

    "3조": {
        "crop": "딸기",
        "temp": 21.2,
        "humidity": 68,
        "light": 840,
        "soil": 55,
        "led": False,
    },

    "4조": {
        "crop": "토마토",
        "temp": 29.1,
        "humidity": 49,
        "light": 930,
        "soil": 34,
        "led": False,
    },

    "5조": {
        "crop": "루꼴라",
        "temp": 24.0,
        "humidity": 63,
        "light": 680,
        "soil": 51,
        "led": True,
    },
}


# =========================================================
# 스마트팜별 적정 환경
# =========================================================
TARGETS = {
    "상추": {
        "temp": "20 ~ 25 ℃",
        "humidity": "55 ~ 70 %",
        "light": "600 ~ 900 lx",
        "soil": "40 ~ 60 %",
    },

    "바질": {
        "temp": "20 ~ 26 ℃",
        "humidity": "50 ~ 70 %",
        "light": "600 ~ 1000 lx",
        "soil": "45 ~ 65 %",
    },

    "딸기": {
        "temp": "18 ~ 24 ℃",
        "humidity": "60 ~ 75 %",
        "light": "700 ~ 1000 lx",
        "soil": "45 ~ 65 %",
    },

    "토마토": {
        "temp": "20 ~ 27 ℃",
        "humidity": "55 ~ 70 %",
        "light": "700 ~ 1100 lx",
        "soil": "45 ~ 65 %",
    },

    "루꼴라": {
        "temp": "18 ~ 25 ℃",
        "humidity": "55 ~ 70 %",
        "light": "600 ~ 900 lx",
        "soil": "40 ~ 60 %",
    },
}


# =========================================================
# Session State 초기화
# =========================================================
if "farms" not in st.session_state:
    st.session_state.farms = FARMS.copy()


if "history" not in st.session_state:

    rows = []

    for farm_name, data in FARMS.items():

        for i in range(10):

            rows.append(
                {
                    "farm": farm_name,
                    "time": pd.Timestamp.now()
                    - pd.Timedelta(minutes=(9 - i) * 10),

                    "온도": data["temp"]
                    + random.uniform(-1, 1),

                    "습도": data["humidity"]
                    + random.uniform(-3, 3),

                    "조도": data["light"]
                    + random.uniform(-70, 70),

                    "토양습도": data["soil"]
                    + random.uniform(-4, 4),
                }
            )

    st.session_state.history = pd.DataFrame(rows)


# =========================================================
# Agent 판단 함수
# =========================================================
def analyze_farm(data):

    problems = []

    if data["temp"] > 27:
        problems.append("온도가 높습니다.")

    elif data["temp"] < 18:
        problems.append("온도가 낮습니다.")

    if data["humidity"] < 50:
        problems.append("습도가 낮습니다.")

    if data["soil"] < 40:
        problems.append("토양 수분이 부족합니다.")

    if data["light"] < 600:
        problems.append("조도가 부족합니다.")

    # 상태 판단
    if len(problems) == 0:

        status = "정상"

        message = (
            "현재 재배 환경은 안정적입니다. "
            "센서 데이터를 지속적으로 모니터링합니다."
        )

    elif len(problems) == 1:

        status = "주의"

        message = (
            problems[0]
            + " 환경 변화를 확인하고 필요 시 관리 조치를 수행하세요."
        )

    else:

        status = "관리 필요"

        message = (
            " ".join(problems)
            + " 우선순위를 판단하여 관리가 필요합니다."
        )

    return status, message


# =========================================================
# 가상 센서 데이터 업데이트
# 실제 장비에서는 이 함수를 센서 읽기 함수로 교체
# =========================================================
def update_sensor_data(farm_name):

    farm = st.session_state.farms[farm_name]

    farm["temp"] += random.uniform(-0.5, 0.5)
    farm["humidity"] += random.uniform(-2, 2)
    farm["light"] += random.uniform(-50, 50)
    farm["soil"] += random.uniform(-3, 3)

    # 범위 제한
    farm["humidity"] = max(
        0,
        min(100, farm["humidity"])
    )

    farm["soil"] = max(
        0,
        min(100, farm["soil"])
    )

    farm["light"] = max(
        0,
        farm["light"]
    )

    # 그래프 데이터 추가
    new_data = pd.DataFrame(
        [
            {
                "farm": farm_name,
                "time": pd.Timestamp.now(),
                "온도": farm["temp"],
                "습도": farm["humidity"],
                "조도": farm["light"],
                "토양습도": farm["soil"],
            }
        ]
    )

    st.session_state.history = pd.concat(
        [
            st.session_state.history,
            new_data,
        ],
        ignore_index=True,
    )


# =========================================================
# 사이드바
# =========================================================
st.sidebar.title("🌱 Smart Farm")

selected_farm = st.sidebar.selectbox(
    "모니터링할 스마트팜 선택",
    list(st.session_state.farms.keys()),
)


st.sidebar.divider()

st.sidebar.subheader("전체 스마트팜 상태")


for name, farm in st.session_state.farms.items():

    status, _ = analyze_farm(farm)

    if status == "정상":
        icon = "🟢"

    elif status == "주의":
        icon = "🟡"

    else:
        icon = "🔴"

    st.sidebar.write(
        f"{icon} {name} / {farm['crop']}"
    )


st.sidebar.divider()


if st.sidebar.button(
    "🔄 센서 데이터 갱신",
    use_container_width=True,
):

    update_sensor_data(selected_farm)

    st.rerun()


# =========================================================
# 선택 스마트팜 데이터
# =========================================================
farm = st.session_state.farms[selected_farm]

crop = farm["crop"]

status, agent_message = analyze_farm(farm)


# =========================================================
# 페이지 제목
# =========================================================
st.title(
    f"🌿 {selected_farm} 대시보드"
)

st.write(
    f"재배 작물 : **{crop}**"
)

st.caption(
    f"마지막 확인 시간 : "
    f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
)


st.divider()


# =========================================================
# 센서 데이터
# =========================================================
st.subheader("📡 환경 센서 데이터")


col1, col2, col3, col4 = st.columns(4)


with col1:

    st.metric(
        "🌡 온도",
        f"{farm['temp']:.1f} ℃"
    )


with col2:

    st.metric(
        "💧 습도",
        f"{farm['humidity']:.1f} %"
    )


with col3:

    st.metric(
        "☀️ 조도",
        f"{farm['light']:.0f} lx"
    )


with col4:

    st.metric(
        "🌱 토양 습도",
        f"{farm['soil']:.1f} %"
    )


st.divider()


# =========================================================
# Agent 판단 / 기준 / 제어
# =========================================================
col1, col2, col3 = st.columns(
    [1, 1.5, 1]
)


# ---------------------------------------------------------
# 현재 환경 상태
# ---------------------------------------------------------
with col1:

    st.subheader("환경 상태")

    if status == "정상":

        st.success(
            "🟢 정상"
        )

    elif status == "주의":

        st.warning(
            "🟡 주의"
        )

    else:

        st.error(
            "🔴 관리 필요"
        )


    st.markdown(
        "### 적정 환경 기준"
    )

    target = TARGETS[crop]

    st.write(
        f"🌡 온도 : {target['temp']}"
    )

    st.write(
        f"💧 습도 : {target['humidity']}"
    )

    st.write(
        f"☀️ 조도 : {target['light']}"
    )

    st.write(
        f"🌱 토양습도 : {target['soil']}"
    )


# ---------------------------------------------------------
# AI Agent
# ---------------------------------------------------------
with col2:

    st.subheader("🤖 AI Agent 판단")

    st.info(
        agent_message
    )


    st.markdown(
        "### Agent 관리 판단"
    )


    if status == "정상":

        st.write(
            "1. 현재 환경 유지"
        )

        st.write(
            "2. 환경 센서 지속 모니터링"
        )

        st.write(
            "3. 이상 발생 시 재판단"
        )


    else:

        priority = 1


        if farm["soil"] < 40:

            st.write(
                f"{priority}. 토양 수분 상태 확인"
            )

            priority += 1


        if farm["temp"] > 27:

            st.write(
                f"{priority}. 고온 상태 확인"
            )

            priority += 1


        if farm["humidity"] < 50:

            st.write(
                f"{priority}. 습도 상태 확인"
            )

            priority += 1


        if farm["light"] < 600:

            st.write(
                f"{priority}. LED 조명 제어 검토"
            )


# ---------------------------------------------------------
# LED 제어
# ---------------------------------------------------------
with col3:

    st.subheader("💡 LED 제어")


    led_state = st.toggle(
        "재배 LED",
        value=farm["led"],
    )


    if led_state != farm["led"]:

        farm["led"] = led_state


    if farm["led"]:

        st.success(
            "LED ON"
        )

    else:

        st.info(
            "LED OFF"
        )


st.divider()


# =========================================================
# 그래프
# =========================================================
st.subheader(
    "📊 환경 변화 모니터링"
)


history = st.session_state.history[
    st.session_state.history["farm"]
    == selected_farm
].copy()


history = history.sort_values(
    "time"
).tail(20)


tab1, tab2, tab3 = st.tabs(
    [
        "온도 / 습도",
        "조도 / 토양습도",
        "최근 센서 데이터",
    ]
)


# ---------------------------------------------------------
# 온도 습도 그래프
# ---------------------------------------------------------
with tab1:

    chart_data = history.set_index(
        "time"
    )[
        [
            "온도",
            "습도",
        ]
    ]

    st.line_chart(
        chart_data,
        use_container_width=True,
    )


# ---------------------------------------------------------
# 조도 토양습도
# ---------------------------------------------------------
with tab2:

    chart_data = history.set_index(
        "time"
    )[
        [
            "조도",
            "토양습도",
        ]
    ]

    st.line_chart(
        chart_data,
        use_container_width=True,
    )


# ---------------------------------------------------------
# 데이터 테이블
# ---------------------------------------------------------
with tab3:

    table_data = history[
        [
            "time",
            "온도",
            "습도",
            "조도",
            "토양습도",
        ]
    ].copy()


    table_data["time"] = (
        table_data["time"]
        .dt.strftime("%H:%M:%S")
    )


    st.dataframe(
        table_data.iloc[::-1],
        use_container_width=True,
        hide_index=True,
    )


st.divider()


# =========================================================
# 관리 결과
# =========================================================
st.subheader(
    "🔁 관리 결과 및 피드백"
)


col1, col2 = st.columns(
    [2, 1]
)


with col1:

    st.write(
        """
        센서 데이터 수집
        → AI Agent 판단
        → 관리 방법 결정
        → LED 제어
        → 환경 변화 확인
        → 재판단
        """
    )


with col2:

    if st.button(
        "🤖 Agent 재판단",
        use_container_width=True,
    ):

        status, message = analyze_farm(
            farm
        )


        if status == "정상":

            st.success(
                message
            )

        elif status == "주의":

            st.warning(
                message
            )

        else:

            st.error(
                message
            )


st.divider()