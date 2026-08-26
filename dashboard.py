import streamlit as st

st.title("🚗 AI Agent 실습")

st.write("GitHub + Streamlit 배포 테스트입니다.")

name = st.text_input("이름을 입력하세요")

if st.button("확인"):
    st.success(f"안녕하세요, {name}님!")