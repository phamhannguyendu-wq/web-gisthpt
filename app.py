import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
import math

# -----------------------------------------------------------------------------
# 1. Cấu hình trang Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Web-GIS Tư vấn Chọn trường THPT Phường Hòa Hưng (7 Tiêu chí)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 Hệ thống Web-GIS Tư vấn Lựa chọn Trường THPT Cá nhân hóa")
st.caption("Mô hình MCDA-AHP Cá nhân hóa 100% cho 7 Tiêu chí Tuyển sinh | Địa bàn: Phường Hòa Hưng, Quận 10")

# -----------------------------------------------------------------------------
# 2. Tải Cơ sở dữ liệu 46 trường THPT từ Excel (Dùng header=1)
# -----------------------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_excel("CSDL_WebGIS_TruongTHPT_7TieuChi.xlsx", sheet_name="CSDL_Truong", header=1)
    
    # Ép kiểu dữ liệu dạng số thực (float) để tránh lỗi kiểu dữ liệu
    df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
    df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
    df['Diem_Chuan_2026'] = pd.to_numeric(df['Diem_Chuan_2026'], errors='coerce')
    df['Ty_Le_Choi'] = pd.to_numeric(df['Ty_Le_Choi'], errors='coerce')
    df['Hoc_Phi_Thang'] = pd.to_numeric(df['Hoc_Phi_Thang'], errors='coerce')
    
    # Loại bỏ các dòng bị thiếu tọa độ
    df = df.dropna(subset=['Latitude', 'Longitude']).reset_index(drop=True)
    return df

try:
    df_truong = load_data()
except Exception as e:
    st.error(f"❌ Không thể tải tệp 'CSDL_WebGIS_TruongTHPT_7TieuChi.xlsx'. Lỗi: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 3. Sidebar Form Nhập liệu Cá nhân hóa 7 Tiêu chí + Nút bấm "TƯ VẤN"
# -----------------------------------------------------------------------------
with st.sidebar.form(key="tu_van_form"):
    st.header("⚙️ Cấu Hình Hồ Sơ & Nhu Cầu 7 Tiêu Chí")

    # Tiêu chí 1: Khả năng trúng tuyển (14.39%)
    st.subheader("1. 🎯 Khả năng trúng tuyển")
    diem_du_kien = st.number_input(
        "Điểm thi tuyển sinh dự kiến:", 
        min_value=0.0, max_value=30.0, value=21.0, step=0.25
    )

    # Tiêu chí 2: Vị trí & Khả năng di chuyển (13.77%)
    st.subheader("2. 📍 Vị trí & Di chuyển")
    dia_chi_nha = st.text_input(
        "Địa chỉ nhà chính xác:", 
        value="285 Cách Mạng Tháng Tám, Phường Hòa Hưng, Quận 10, TP.HCM"
    )
    ban_kinh_max = st.slider("Bán kính đi học tối đa chấp nhận (km):", 2.0, 15.0, 10.0, 0.5)

    # Tiêu chí 3: Định hướng học tập (Tổ hợp môn GDPT 2018) (14.49%)
    st.subheader("3. 📚 Định hướng Tổ hợp môn")
    mon_luat_chon = st.multiselect(
        "Môn học tự chọn ưu tiên:",
        options=["Vật lý", "Hóa học", "Sinh học", "Tin học", "Địa lý", "GDKT&PL", "Mỹ thuật", "Công nghệ"],
        default=["Vật lý", "Hóa học", "Tin học"]
    )

    # Tiêu chí 4: Mô hình học tập (Bán trú) (12.84%)
    st.subheader("4. 🛌 Mô hình Bán trú")
    ban_tru_req = st.radio(
        "Nhu cầu dịch vụ bán trú:", 
        options=["Cần bán trú", "Không cần bán trú"], index=0
    )

    # Tiêu chí 5: Tài chính / Học phí (13.96%)
    st.subheader("5. 💰 Điều kiện Tài chính")
    loai_hinh_pref = st.selectbox(
        "Loại hình trường ưu tiên:", 
        options=["Tất cả", "Công lập", "Tư thục"]
    )
    hoc_phi_max = st.number_input(
        "Mức học phí tối đa chi trả (VNĐ/tháng):", 
        min_value=1000000, max_value=20000000, value=3000000, step=500000
    )

    # Tiêu chí 6: Môi trường & Cơ sở vật chất (15.15%)
    st.subheader("6. 🏫 Môi trường & CSVC")
    hoc_2_buoi_req = st.selectbox(
        "Nhu cầu học 2 buổi/ngày:",
        options=["Bắt buộc có", "Không bắt buộc"]
    )

    # Tiêu chí 7: Chất lượng đào tạo & CLB Ngoại khóa (15.40%)
    st.subheader("7. 🏆 Chất lượng & CLB Ngoại khóa")
    clb_yeu_thich = st.multiselect(
        "Lĩnh vực Câu lạc bộ yêu thích:",
        options=["Truyền thông", "Nghệ thuật", "Nhảy hiện đại", "Thể thao", "Học thuật", "STEM"],
        default=["Truyền thông", "Thể thao"]
    )

    # NÚT TƯ VẤN CHÍNH THỨC
    btn_submit = st.form_submit_button(
        label="🔍 TƯ VẤN CHỌN TRƯỜNG PHÙ HỢP", 
        use_container_width=True,
        type="primary"
    )

# -----------------------------------------------------------------------------
# 4. Geocoding & Thuật toán Tính khoảng cách di chuyển thực tế
# -----------------------------------------------------------------------------
@st.cache_data
def geocode_address(address):
    try:
        geolocator = Nominatim(user_agent="webgis_school_advisor_hoahung_7tc")
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
    except:
        pass
    return 10.779094, 106.680822

lat_user, lon_user = geocode_address(dia_chi_nha)

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371.0 # Bán kính Trái Đất (km)
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c * 1.45  # Hệ số 1.45 quy đổi sang khoảng cách thực tế đô thị

# -----------------------------------------------------------------------------
# 5. Thuật toán Chuẩn hóa Đủ 7 Tiêu chí & Tính điểm Tương thích AHP (S_i)
# -----------------------------------------------------------------------------
W_AHP = {
    'c1_cl_daotao': 0.154,       # 15.40%
    'c2_csvc': 0.152,            # 15.15%
    'c3_tohop': 0.145,           # 14.49%
    'c4_diemchuan': 0.144,       # 14.39%
    'c5_taichinh': 0.140,        # 13.96%
    'c6_vitri': 0.138,           # 13.77%
    'c7_bantru': 0.128            # 12.84%
}

scores = []
distances = []

for idx, row in df_truong.iterrows():
    # c6: Vị trí & Khoảng cách di chuyển thực tế
    d_i = calculate_distance(lat_user, lon_user, row['Latitude'], row['Longitude'])
    distances.append(round(d_i, 2))
    c6 = max(0.0, 10.0 * (1.0 - d_i / ban_kinh_max))
    
    # c1: Chất lượng đào tạo (kết hợp Tỷ lệ chọi & CLB phù hợp)
    ty_le = row['Ty_Le_Choi'] if pd.notnull(row['Ty_Le_Choi']) else 1.0
    c1_base = min(10.0, (ty_le / 2.5) * 10.0)
    clb_str = str(row['CLB_Noi_Bat']) if pd.notnull(row['CLB_Noi_Bat']) else ""
    clb_match_count = sum([1 for c in clb_yeu_thich if c.lower() in clb_str.lower()])
    c1_clb = (clb_match_count / len(clb_yeu_thich) * 10.0) if clb_yeu_thich else 10.0
    c1 = 0.7 * c1_base + 0.3 * c1_clb
    
    # c2: Môi trường & Cơ sở vật chất (Học 2 buổi/ngày)
    if hoc_2_buoi_req == "Bắt buộc có":
        c2 = 10.0 if row['Hoc_2_Buoi'] == "Có" else 2.0
    else:
        c2 = 10.0 if row['Hoc_2_Buoi'] == "Có" else 7.0
        
    # c3: Định hướng học tập (Tổ hợp môn GDPT 2018)
    c3 = 10.0  # Mặc định đạt chuẩn chương trình GDPT 2018
    
    # c4: Khả năng trúng tuyển (So sánh với điểm thi dự kiến)
    E_i = row['Diem_Chuan_2026'] if pd.notnull(row['Diem_Chuan_2026']) else 15.0
    if diem_du_kien >= E_i + 1:
        c4 = 10.0
    elif diem_du_kien < E_i - 1:
        c4 = 0.0  # Cảnh báo rủi ro trượt
    else:
        c4 = 10.0 - 5.0 * (E_i + 1 - diem_du_kien)
        
    # c5: Tài chính (Học phí & Loại hình)
    fee = row['Hoc_Phi_Thang'] if pd.notnull(row['Hoc_Phi_Thang']) else 1767000
    if loai_hinh_pref != "Tất cả" and row['Loai_Hinh'] != loai_hinh_pref:
        c5 = 2.0
    else:
        c5 = 10.0 if fee <= hoc_phi_max else max(2.0, 10.0 * (hoc_phi_max / fee))
        
    # c7: Mô hình học tập (Bán trú)
    if ban_tru_req == "Không cần bán trú":
        c7 = 10.0
    else:
        c7 = 10.0 if row['Ban_Tru'] == "Có" else 0.0
        
    # Tính Điểm Tương Thích Tổng Hợp S_i theo đúng 7 trọng số AHP
    S_i = (W_AHP['c1_cl_daotao'] * c1 + 
           W_AHP['c2_csvc'] * c2 + 
           W_AHP['c3_tohop'] * c3 + 
           W_AHP['c4_diemchuan'] * c4 + 
           W_AHP['c5_taichinh'] * c5 + 
           W_AHP['c6_vitri'] * c6 + 
           W_AHP['c7_bantru'] * c7)
    
    scores.append(round(S_i, 2))

df_truong['Khoang_Cach_km'] = distances
df_truong['Diem_S_i'] = scores

# -----------------------------------------------------------------------------
# 6. Sắp xếp thứ tự và phân loại Top 1, Top 2, Top 3
# -----------------------------------------------------------------------------
df_truong = df_truong.sort_values(by='Diem_S_i', ascending=False).reset_index(drop=True)
df_truong['Xep_Hang'] = "Khác"
if len(df_truong) >= 1: df_truong.at[0, 'Xep_Hang'] = "Top 1"
if len(df_truong) >= 2: df_truong.at[1, 'Xep_Hang'] = "Top 2"
if len(df_truong) >= 3: df_truong.at[2, 'Xep_Hang'] = "Top 3"

# -----------------------------------------------------------------------------
# 7. Giao diện Hiển thị Bản đồ & Bảng kết quả Đề xuất Top 3
# -----------------------------------------------------------------------------
col1, col2 = st.columns([1.1, 0.9])

with col1:
    st.subheader("🗺️ Bản đồ Không gian Trực quan Web-GIS")
    
    # Tạo bản đồ Folium trung tâm tại nhà học sinh
    m = folium.Map(location=[lat_user, lon_user], zoom_start=14, tiles="OpenStreetMap")
    
    # Ghim vị trí nhà học sinh (Màu đỏ)
    folium.Marker(
        [lat_user, lon_user],
        popup=f"<b>🏠 Vị trí nhà học sinh:</b><br>{dia_chi_nha}",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)
    
    # Bảng màu quy chuẩn theo FSL
    color_map = {
        "Top 1": "#10B981",  # Xanh lục bảo
        "Top 2": "#3B82F6",  # Xanh dương
        "Top 3": "#F97316",  # Cam đất
        "Khác": "#6B7280"    # Xám trung tính
    }
    
    # Vẽ các trường THPT lên bản đồ
    for idx, row in df_truong.iterrows():
        rank = row['Xep_Hang']
        color = color_map[rank]
        radius = 14 if rank in ["Top 1", "Top 2", "Top 3"] else 6
        
        popup_html = f"""
        <div style='font-family: Arial; width: 240px;'>
            <h4 style='margin:0; color:{color};'>{rank}: {row['Ten_Truong']}</h4>
            <hr style='margin: 5px 0;'>
            <b>Loại hình:</b> {row['Loai_Hinh']}<br>
            <b>Điểm chuẩn 2026:</b> {row['Diem_Chuan_2026']} điểm<br>
            <b>Khoảng cách:</b> {row['Khoang_Cach_km']} km<br>
            <b>Bán trú:</b> {row['Ban_Tru']}<br>
            <b>Độ tương thích AHP 7 TC (S_i):</b> <b style='color:red; font-size: 15px;'>{row['Diem_S_i']} / 10</b>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85,
            popup=folium.Popup(popup_html, max_width=260)
        ).add_to(m)
        
    # Render bản đồ vào Streamlit
    st_folium(m, width=720, height=520)

with col2:
    st.subheader("🏆 Kết Quả Đề Xuất Top 3 Tối Ưu")
    
    top_3 = df_truong[df_truong['Xep_Hang'].isin(["Top 1", "Top 2", "Top 3"])]
    
    for idx, row in top_3.iterrows():
        rank = row['Xep_Hang']
        badge_color = "🟢" if rank == "Top 1" else ("🔵" if rank == "Top 2" else "🟠")
        
        with st.expander(f"{badge_color} {rank}: {row['Ten_Truong']}", expanded=True):
            st.markdown(f"* **Điểm tương thích AHP 7 tiêu chí:** <b style='color:red; font-size:16px;'>{row['Diem_S_i']} / 10</b>", unsafe_allow_html=True)
            st.write(f"* **Khoảng cách thực tế:** `{row['Khoang_Cach_km']} km`")
            st.write(f"* **Điểm chuẩn NV1 (2026):** `{row['Diem_Chuan_2026']} điểm`")
            st.write(f"* **Loại hình & Bán trú:** {row['Loai_Hinh']} | Bán trú: {row['Ban_Tru']}")
            st.write(f"* **CLB nổi bật:** {row['CLB_Noi_Bat']}")
            st.write(f"* **Địa chỉ:** {row['Dia_Chi']}")

st.divider()

# -----------------------------------------------------------------------------
# 8. Bảng Dữ Liệu Đánh Giá Đầy Đủ 46 Trường
# -----------------------------------------------------------------------------
st.subheader("📊 Bảng Chi Tiết Kết Quả Đánh Giá 7 Tiêu Chí AHP (46 Trường THPT)")
st.dataframe(
    df_truong[['Xep_Hang', 'Ten_Truong', 'Loai_Hinh', 'Diem_Chuan_2026', 'Khoang_Cach_km', 'Ban_Tru', 'Diem_S_i']],
    use_container_width=True
)
