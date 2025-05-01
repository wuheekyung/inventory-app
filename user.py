import streamlit as st
import pandas as pd
import os
from datetime import datetime

# -------- 사용자 정보 --------
USERS = {
    "admin@example.com": {"password": "admin123", "role": "관리자"},
    "user1@example.com": {"password": "user123", "role": "매입전용"},
    "user2@example.com": {"password": "user456", "role": "매출전용"},
}

# -------- 로그인 함수 --------
def login():
    st.title("🔐 로그인")
    email = st.text_input("이메일")
    password = st.text_input("비밀번호", type="password")

    if st.button("로그인"):
        user = USERS.get(email)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            st.session_state.user_email = email
            st.session_state.role = user["role"]
            st.experimental_rerun()
        else:
            st.error("이메일 또는 비밀번호가 틀렸습니다.")

# -------- 로그아웃 함수 --------
def logout():
    for key in ["logged_in", "user_email", "role"]:
        st.session_state.pop(key, None)
    st.experimental_rerun()

# -------- 매입 입력 폼 --------
def purchase_form():
    st.subheader("📥 매입 입력")
    supplier = st.text_input("매입처")
    product = st.text_input("제품명")
    thickness = st.number_input("두께 (mm)", min_value=0.0, step=0.1)
    width = st.number_input("가로 (mm)", min_value=0.0)
    height = st.number_input("세로 (mm)", min_value=0.0)
    qty = st.number_input("수량", min_value=1, step=1)
    date = st.date_input("매입일", value=datetime.today())

    if st.button("매입 등록"):
        row = {
            "일자": date,
            "매입처": supplier,
            "제품명": product,
            "두께": thickness,
            "가로": width,
            "세로": height,
            "수량": qty
        }
        save_to_excel("매입기록.xlsx", row)
        st.success("매입 정보가 저장되었습니다.")

# -------- 매출 입력 폼 --------
def sales_form():
    st.subheader("📤 매출 입력")
    customer = st.text_input("매출처")
    product = st.text_input("제품명")
    thickness = st.number_input("두께 (mm)", min_value=0.0, step=0.1, key="sales_thick")
    width = st.number_input("가로 (mm)", min_value=0.0, key="sales_width")
    height = st.number_input("세로 (mm)", min_value=0.0, key="sales_height")
    qty = st.number_input("수량", min_value=1, step=1, key="sales_qty")
    date = st.date_input("매출일", value=datetime.today(), key="sales_date")

    if st.button("매출 등록"):
        row = {
            "일자": date,
            "매출처": customer,
            "제품명": product,
            "두께": thickness,
            "가로": width,
            "세로": height,
            "수량": qty
        }
        save_to_excel("매출기록.xlsx", row)
        st.success("매출 정보가 저장되었습니다.")

# -------- 엑셀 저장 함수 --------
def save_to_excel(filename, row):
    df = pd.DataFrame([row])
    if os.path.exists(filename):
        existing = pd.read_excel(filename)
        df = pd.concat([existing, df], ignore_index=True)
    df.to_excel(filename, index=False)

# -------- 앱 시작 --------
if "logged_in" not in st.session_state:
    login()
else:
    st.sidebar.write(f"👤 로그인: {st.session_state.user_email}")
    st.sidebar.write(f"📌 권한: {st.session_state.role}")
    st.sidebar.button("로그아웃", on_click=logout)

    st.title("📦 재고관리 앱")

    role = st.session_state.role

    if role == "관리자":
        tab1, tab2 = st.tabs(["📥 매입", "📤 매출"])
        with tab1:
            purchase_form()
        with tab2:
            sales_form()

    elif role == "매입전용":
        purchase_form()

    elif role == "매출전용":
        sales_form()

    else:
        st.warning("권한이 없습니다.")
