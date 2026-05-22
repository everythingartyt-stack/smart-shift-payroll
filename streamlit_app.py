import streamlit as st
import pandas as pd
import time

st.set_page_config(page_title="ระบบแดชบอร์ดกะเวร", layout="wide")

st.title("⚡ ระบบแดชบอร์ดสรุปงานกะเวรรายเดือน")
st.write("ตารางปฏิบัติงานและสรุปสถิติการเข้าเวรประจำเดือนจาก Google Sheets")

# 🔄 ปุ่มกดรีเฟรชอัปเดตข้อมูล
if st.button("🔄 อัปเดตข้อมูลล่าสุด", use_container_width=True):
    with st.spinner("กำลังดึงตารางเวรล่าสุด..."):
        st.cache_data.clear()
        time.sleep(1.0)
        st.rerun()

st.divider()

# ฟังก์ชันดึงข้อมูลตารางเวร (ใช้ ID ชีตใหม่ที่น้าส่งมาเรียบร้อยครับ)
def get_shift_data():
    spreadsheet_id = "1hVGvgnJ97xK3v6_wnwU01KS_XCTXg3jaC8aqxYZwcCQ"
    csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Sheet1&t={int(time.time())}"
    
    df_raw = pd.read_csv(csv_url)
    df_raw.columns = df_raw.columns.str.strip()
    return df_raw.fillna("")

try:
    df = get_shift_data()
except Exception as e:
    st.error("❌ ไม่สามารถดึงข้อมูลได้: กรุณาตรวจสอบการตั้งค่าแชร์ลิงก์ของ Google Sheets (ให้เป็น 'ทุกคนที่มีลิงก์')")
    st.stop()

if df.empty:
    st.warning("⚠️ ไม่พบข้อมูลในกูเกิลชีต กรุณากรอกข้อมูลตารางเวรก่อนครับ")
else:
    # 📌 รายชื่อพนักงานทั้ง 10 ท่านตามที่กำหนด
    staff_list = [
        "สุทธิโชค", "ศักดิ์ชาย", "ภิญโญ", "อภิวัฒน์", "อนุชิต", 
        "ศักรินทร์", "รุ่งโรจน์", "เวทิม", "คมสัน", "วรวัฒน์"
    ]
    
    # 🎯 1. ประมวลผลนับจำนวนกะแยกตามประเภทกะจริงในชีตของน้า
    summary_data = []
    
    for staff in staff_list:
        # นับกะ 1 (คอลัมน์ กะ1_คนที1 และ กะ1_คนที2)
        shift1 = 0
        if "กะ1_คนที1" in df.columns: shift1 += df["กะ1_คนที1"].astype(str).str.strip().eq(staff).sum()
        if "กะ1_คนที2" in df.columns: shift1 += df["กะ1_คนที2"].astype(str).str.strip().eq(staff).sum()
        
        # นับกะ 2 (คอลัมน์ กะ2_คนที1 และ กะ2_คนที2)
        shift2 = 0
        if "กะ2_คนที1" in df.columns: shift2 += df["กะ2_คนที1"].astype(str).str.strip().eq(staff).sum()
        if "กะ2_คนที2" in df.columns: shift2 += df["กะ2_คนที2"].astype(str).str.strip().eq(staff).sum()
        
        # นับกะ 3 (คอลัมน์ กะ3_คนที1 และ กะ3_คนที2)
        shift3 = 0
        if "กะ3_คนที1" in df.columns: shift3 += df["กะ3_คนที1"].astype(str).str.strip().eq(staff).sum()
        if "กะ3_คนที2" in df.columns: shift3 += df["กะ3_คนที2"].astype(str).str.strip().sum() if "กะ3_คนที2" in df.columns and type(df["กะ3_คนที2"])==bool else df["กะ3_คนที2"].astype(str).str.strip().eq(staff).sum()
        
        total = shift1 + shift2 + shift3
        
        summary_data.append({
            "รายชื่อพนักงาน": staff,
            "กะ 1 (ครั้ง)": shift1,
            "กะ 2 (ครั้ง)": shift2,
            "กะ 3 (ครั้ง)": shift3,
            "รวมทั้งหมด (ครั้ง)": total
        })
    
    df_summary = pd.DataFrame(summary_data)
    
    # แสดงยอดกะรวมทั้งเดือนที่ส่วนบนของแดชบอร์ด
    total_all_shifts = df_summary["รวมทั้งหมด (ครั้ง)"].sum()
    st.markdown(f"### 📈 จำนวนกะงานที่มีการปฏิบัติรวมทั้งเดือน: `{total_all_shifts}` ครั้ง")
    
    st.divider()
    
    # 🌟 แบ่งหน้าจอแสดงผล (ซ้าย: กราฟแท่งรวม / ขวา: ตารางสรุปตัวเลขแยกกะ)
    col1, col2 = st.columns([3, 2.5])
    with col1:
        st.subheader("📊 กราฟเปรียบเทียบภาระงานรายบุคคล (ยอดรวม)")
        st.bar_chart(data=df_summary, x="รายชื่อพนักงาน", y="รวมทั้งหมด (ครั้ง)", use_container_width=True)
        
    with col2:
        st.subheader("📋 ตารางสรุปจำนวนกะรายบุคคลเพื่อตั้งเบิก")
        st.dataframe(df_summary, use_container_width=True, hide_index=True)
        
    st.divider()
    
    # 🎯 2. จัดหน้าตาหัวตารางเวรให้ควบกลุ่มสวยงามตามใจน้า
    st.subheader("📅 ตารางเวรแก้กระแสไฟฟ้าขัดข้อง ประจำเดือน")
    
    try:
        header_tuples = [
            ("วัน/กะ", "วัน/กะ"),
            ("ช่วง 1 (00:30 - 08:30)", "คนที่ 1"),
            ("ช่วง 1 (00:30 - 08:30)", "คนที่ 2"),
            ("ช่วง 2 (08:30 - 16:30)", "คนที่ 1"),
            ("ช่วง 2 (08:30 - 16:30)", "คนที่ 2"),
            ("ช่วง 3 (16:30 - 00:30)", "คนที่ 1"),
            ("ช่วง 3 (16:30 - 00:30)", "คนที่ 2")
        ]
        
        df_display = df.copy()
        df_display.columns = pd.MultiIndex.from_tuples(header_tuples[:len(df_display.columns)])
        st.dataframe(df_display, use_container_width=True)
        
    except Exception as e:
        st.dataframe(df, use_container_width=True)
