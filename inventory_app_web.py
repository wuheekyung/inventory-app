import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="철판 재고관리", layout="centered")
st.title("📦 철판 재고관리 웹앱")

filename = "재고장.xlsx"

def load_data(sheet):
    if os.path.exists(filename):
        try:
            return pd.read_excel(filename, sheet_name=sheet)
        except:
            return pd.DataFrame()
    return pd.DataFrame()

def save_data(sheet, df):
    with pd.ExcelWriter(filename, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
        df.to_excel(writer, sheet_name=sheet, index=False)

def calc_weight(thk, w, h, q):
    return round(thk * 7.85 * w / 1000 * h / 1000 * q, 0)

# ------------------- 입력 폼 -------------------
with st.form("entry_form"):
    col1, col2 = st.columns(2)
    with col1:
        product = st.text_input("제품명")
        thickness = st.number_input("두께 (mm)", min_value=0.0, format="%.2f")
        width = st.number_input("가로 (mm)", min_value=0.0)
    with col2:
        height = st.number_input("세로 (mm)", min_value=0.0)
        qty = st.number_input("수량", min_value=1, step=1)
        partner = st.text_input("매입처 / 매출처")

    action = st.radio("동작 선택", ["매입 등록", "매출 등록"])
    submitted = st.form_submit_button("실행")

# ------------------- 실행 처리 -------------------
if submitted:
    stock_df = load_data("재고장기록")
    if stock_df.empty:
        stock_df = pd.DataFrame(columns=['번호','품목','두께','가로','세로','수량','중량'])

    mask = (
        (stock_df['품목'] == product) &
        (stock_df['두께'] == thickness) &
        (stock_df['가로'] == width) &
        (stock_df['세로'] == height)
    )

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if action == "매입 등록":
        if stock_df[mask].empty:
            new_row = {
                '번호': len(stock_df) + 1,
                '품목': product,
                '두께': thickness,
                '가로': width,
                '세로': height,
                '수량': qty,
                '중량': calc_weight(thickness, width, height, qty)
            }
            stock_df = pd.concat([stock_df, pd.DataFrame([new_row])], ignore_index=True)
        else:
            stock_df.loc[mask, '수량'] += qty
            stock_df.loc[mask, '중량'] = calc_weight(thickness, width, height, stock_df.loc[mask, '수량'].values[0])
        
        buy_df = load_data("매입장")
        new_entry = pd.DataFrame([{
            '일시': now, '품목': product, '두께': thickness,
            '가로': width, '세로': height, '수량': qty,
            '중량': calc_weight(thickness, width, height, qty),
            '매입처': partner
        }])
        buy_df = pd.concat([buy_df, new_entry], ignore_index=True)
        save_data("매입장", buy_df)

        st.success("✅ 매입이 등록되었습니다.")

    elif action == "매출 등록":
        if stock_df[mask].empty:
            st.error("❌ 재고에 해당 품목이 없습니다.")
        elif stock_df.loc[mask, '수량'].values[0] < qty:
            st.error("❌ 재고 수량이 부족합니다.")
        else:
            stock_df.loc[mask, '수량'] -= qty
            stock_df.loc[mask, '중량'] = calc_weight(thickness, width, height, stock_df.loc[mask, '수량'].values[0])

            sell_df = load_data("매출장")
            new_entry = pd.DataFrame([{
                '일시': now, '품목': product, '두께': thickness,
                '가로': width, '세로': height, '수량': qty,
                '중량': calc_weight(thickness, width, height, qty),
                '매출처': partner
            }])
            sell_df = pd.concat([sell_df, new_entry], ignore_index=True)
            save_data("매출장", sell_df)

            st.success("✅ 매출이 등록되었습니다.")

    save_data("재고장기록", stock_df)

# ------------------- 재고 보기 -------------------
st.markdown("---")
st.subheader("📦 현재 재고 현황")

stock_df = load_data("재고장기록")
if not stock_df.empty:
    filter_name = st.text_input("🔍 품목명으로 필터", "")
    if filter_name:
        filtered = stock_df[stock_df["품목"].str.contains(filter_name, case=False)]
    else:
        filtered = stock_df
    st.dataframe(filtered[['품목','두께','가로','세로','수량','중량']], use_container_width=True)
else:
    st.info("재고 데이터가 없습니다.")

# ------------------- 히스토리 보기 -------------------
st.markdown("---")
st.subheader("📄 히스토리 보기")

col1, col2 = st.columns(2)

if col1.button("📄 매입장 보기"):
    df = load_data("매입장")
    if df.empty:
        st.warning("매입 기록이 없습니다.")
    else:
        with st.expander("🔍 필터"):
            p_name = st.text_input("품목명", key="buy_name")
            p_partner = st.text_input("매입처", key="buy_partner")
            start_date = st.date_input("시작일", key="buy_start")
            end_date = st.date_input("종료일", key="buy_end")
        
        if p_name:
            df = df[df["품목"].str.contains(p_name, case=False)]
        if p_partner:
            df = df[df["매입처"].str.contains(p_partner, case=False)]
        df["일시"] = pd.to_datetime(df["일시"])
        df = df[(df["일시"].dt.date >= start_date) & (df["일시"].dt.date <= end_date)]
        st.dataframe(df, use_container_width=True)

if col2.button("📄 매출장 보기"):
    df = load_data("매출장")
    if df.empty:
        st.warning("매출 기록이 없습니다.")
    else:
        with st.expander("🔍 필터"):
            p_name = st.text_input("품목명", key="sell_name")
            p_partner = st.text_input("매출처", key="sell_partner")
            start_date = st.date_input("시작일", key="sell_start")
            end_date = st.date_input("종료일", key="sell_end")
        
        if p_name:
            df = df[df["품목"].str.contains(p_name, case=False)]
        if p_partner:
            df = df[df["매출처"].str.contains(p_partner, case=False)]
        df["일시"] = pd.to_datetime(df["일시"])
        df = df[(df["일시"].dt.date >= start_date) & (df["일시"].dt.date <= end_date)]
        st.dataframe(df, use_container_width=True)
