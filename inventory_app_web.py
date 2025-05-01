import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="철판 재고관리 앱", layout="centered")

st.title("📦 철판 재고관리 웹앱")

# 📥 입력창
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("제품명")
        thickness = st.number_input("두께 (mm)", min_value=0.0, format="%.2f")
        width = st.number_input("가로 (mm)", min_value=0.0)
    with col2:
        height = st.number_input("세로 (mm)", min_value=0.0)
        qty = st.number_input("수량", min_value=1, step=1)

    action = st.radio("동작 선택", ["매입 등록", "매출 등록"])
    submitted = st.form_submit_button("실행")

filename = "재고장.xlsx"

# 📊 데이터 불러오기
def load_data():
    if os.path.exists(filename):
        return pd.read_excel(filename, sheet_name="재고장기록")
    else:
        return pd.DataFrame(columns=['번호', '품목', '두께', '가로', '세로', '수량', '중량'])

# 💾 저장하기
def save_data(df):
    for i in range(len(df)):
        row_num = i + 2
        df.at[i, '중량'] = f"=ROUND(C{row_num}*7.85*D{row_num}/1000*E{row_num}/1000*F{row_num},0)"
    df.to_excel(filename, sheet_name="재고장기록", index=False)

# 🔄 동작 처리
if submitted:
    df = load_data()
    mask = (
        (df['품목'] == product) &
        (df['두께'] == thickness) &
        (df['가로'] == width) &
        (df['세로'] == height)
    )

    if action == "매입 등록":
        if df[mask].empty:
            new_row = {
                '번호': len(df)+1,
                '품목': product,
                '두께': thickness,
                '가로': width,
                '세로': height,
                '수량': qty,
                '중량': None
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            df.loc[mask, '수량'] += qty
        save_data(df)
        st.success("✅ 매입이 등록되었습니다.")

    elif action == "매출 등록":
        if df[mask].empty:
            st.error("❌ 재고에 해당 제품이 없습니다.")
        elif df.loc[mask, '수량'].values[0] < qty:
            st.error("❌ 재고 수량이 부족합니다.")
        else:
            df.loc[mask, '수량'] -= qty
            save_data(df)
            st.success("✅ 매출(출고)이 처리되었습니다.")

# 📋 재고 현황 표시
st.markdown("---")
st.subheader("📈 현재 재고 현황")
df = load_data()
if df.empty:
    st.info("재고 데이터가 없습니다.")
else:
    st.dataframe(df[['품목','두께','가로','세로','수량']], use_container_width=True)
