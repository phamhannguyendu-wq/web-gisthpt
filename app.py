import pandas as pd
import streamlit as st
import folium
from streamlit_folium import st_folium
from folium.plugins import Fullscreen
from geopy.geocoders import Nominatim
import math

# -----------------------------------------------------------------------------
# 1. Cấu hình trang Streamlit
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Web-GIS Tư vấn Chọn trường THPT Phường Hòa Hưng (2 Tầng Lọc - 7 Tiêu chí)",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🎓 Hệ thống Web-GIS Tư vấn Lựa chọn Trường THPT Cá nhân hóa")
st.caption("Mô hình Lọc 2 Tầng (Lọc Điều kiện Cứng -> Thuật toán MCDA-AHP 7 Tiêu chí) | Địa bàn: Phường Hòa Hưng, Quận 10")

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
# 3. Sidebar Form Nhập liệu Cá nhân hóa 7 Tiêu chí + Điều kiện Bắt buộc
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
        options=["Cần bán trú (Bắt buộc)", "Không bắt buộc bán trú"], index=0
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
        geolocator = Nominatim(user_agent="webgis_school_advisor_hoahung_7tc_v3")
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
# 5. THUẬT TOÁN 4 BƯỚC: LỌC CỨNG (STEP 1) -> TÍNH ĐIỂM MCDA (STEP 2)
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

df_work = df_truong.copy()

# BƯỚC 1: LỌC ĐIỀU KIỆN BẮT BUỘC (HARD CONSTRAINTS FILTERING)
reasons_rejected = []
distances = []
passed_hard_filter = []

for idx, row in df_work.iterrows():
    d_i = calculate_distance(lat_user, lon_user, row['Latitude'], row['Longitude'])
    distances.append(round(d_i, 2))
    
    is_valid = True
    reject_reasons = []
    
    # 1.1 Lọc cứng: Bán trú
    if ban_tru_req == "Cần bán trú (Bắt buộc)" and str(row['Ban_Tru']).strip() != "Có":
        is_valid = False
        reject_reasons.append("Không có dịch vụ Bán trú")
        
    # 1.2 Lọc cứng: Học phí tối đa
    fee = row['Hoc_Phi_Thang'] if pd.notnull(row['Hoc_Phi_Thang']) else 1767000
    if fee > hoc_phi_max:
        is_valid = False
        reject_reasons.append(f"Học phí ({fee:,.0f} đ) vượt ngân sách tối đa ({hoc_phi_max:,.0f} đ)")
        
    # 1.3 Lọc cứng: Học 2 buổi/ngày
    if hoc_2_buoi_req == "Bắt buộc có" and str(row['Hoc_2_Buoi']).strip() != "Có":
        is_valid = False
        reject_reasons.append("Không tổ chức học 2 buổi/ngày")
        
    # 1.4 Lọc cứng: Loại hình trường
    if loai_hinh_pref != "Tất cả" and str(row['Loai_Hinh']).strip() != loai_hinh_pref:
        is_valid = False
        reject_reasons.append(f"Không thuộc loại hình {loai_hinh_pref}")
        
    # 1.5 Lọc cứng: Điểm chuẩn trúng tuyển
    E_i = row['Diem_Chuan_2026'] if pd.notnull(row['Diem_Chuan_2026']) else 15.0
    if diem_du_kien < E_i - 2.0:
        is_valid = False
        reject_reasons.append(f"Điểm dự kiến ({diem_du_kien}) quá thấp so với điểm chuẩn ({E_i})")
        
    passed_hard_filter.append(is_valid)
    reasons_rejected.append("; ".join(reject_reasons) if reject_reasons else "Đạt điều kiện cứng")

df_work['Khoang_Cach_km'] = distances
df_work['Dat_Dieu_Kien_Cung'] = passed_hard_filter
df_work['Ly_Do_Loc'] = reasons_rejected

# BƯỚC 2: TÍNH ĐIỂM MCDA/AHP
scores = []
for idx, row in df_work.iterrows():
    d_i = row['Khoang_Cach_km']
    c6 = max(0.0, 10.0 * (1.0 - d_i / ban_kinh_max))
    
    ty_le = row['Ty_Le_Choi'] if pd.notnull(row['Ty_Le_Choi']) else 1.0
    c1_base = min(10.0, (ty_le / 2.5) * 10.0)
    clb_str = str(row['CLB_Noi_Bat']) if pd.notnull(row['CLB_Noi_Bat']) else ""
    clb_match_count = sum([1 for c in clb_yeu_thich if c.lower() in clb_str.lower()])
    c1_clb = (clb_match_count / len(clb_yeu_thich) * 10.0) if clb_yeu_thich else 10.0
    c1 = 0.7 * c1_base + 0.3 * c1_clb
    
    c2 = 10.0 if str(row['Hoc_2_Buoi']).strip() == "Có" else 5.0
    c3 = 10.0  # Đạt chuẩn GDPT 2018
    
    E_i = row['Diem_Chuan_2026'] if pd.notnull(row['Diem_Chuan_2026']) else 15.0
    if diem_du_kien >= E_i + 1:
        c4 = 10.0
    elif diem_du_kien < E_i - 2:
        c4 = 0.0
    else:
        c4 = max(0.0, 10.0 - 3.33 * (E_i + 1 - diem_du_kien))
        
    fee = row['Hoc_Phi_Thang'] if pd.notnull(row['Hoc_Phi_Thang']) else 1767000
    c5 = 10.0 if fee <= hoc_phi_max else max(1.0, 10.0 * (hoc_phi_max / fee))
    c7 = 10.0 if str(row['Ban_Tru']).strip() == "Có" else 0.0
    
    S_i = (W_AHP['c1_cl_daotao'] * c1 + 
           W_AHP['c2_csvc'] * c2 + 
           W_AHP['c3_tohop'] * c3 + 
           W_AHP['c4_diemchuan'] * c4 + 
           W_AHP['c5_taichinh'] * c5 + 
           W_AHP['c6_vitri'] * c6 + 
           W_AHP['c7_bantru'] * c7)
    
    scores.append(round(S_i, 2))

df_work['Diem_S_i'] = scores

# BƯỚC 3: XẾP HẠNG (RANKING)
df_passed = df_work[df_work['Dat_Dieu_Kien_Cung'] == True].sort_values(by='Diem_S_i', ascending=False).reset_index(drop=True)
df_rejected = df_work[df_work['Dat_Dieu_Kien_Cung'] == False].sort_values(by='Diem_S_i', ascending=False).reset_index(drop=True)

df_passed['Xep_Hang'] = "Khác"
if len(df_passed) >= 1: df_passed.at[0, 'Xep_Hang'] = "Top 1"
if len(df_passed) >= 2: df_passed.at[1, 'Xep_Hang'] = "Top 2"
if len(df_passed) >= 3: df_passed.at[2, 'Xep_Hang'] = "Top 3"

df_rejected['Xep_Hang'] = "Không đạt điều kiện cứng"

df_final = pd.concat([df_passed, df_rejected], ignore_index=True)

# -----------------------------------------------------------------------------
# 6. Giao diện Hiển thị Bản đồ & Bảng kết quả Đề xuất Top 3
# -----------------------------------------------------------------------------
col1, col2 = st.columns([1.6, 1.0])

with col1:
    st.subheader("🗺️ Bản đồ Không gian Trực quan Web-GIS")
    st.caption("💡 *Mẹo: Bấm vào biểu tượng ⛶ (góc trên bên trái bản đồ) để phóng toàn màn hình.*")
    
    st.info(f"💡 **Kết quả Lọc 2 Tầng:** Đã vượt qua vòng Lọc Cứng: **{len(df_passed)} / {len(df_work)} trường**. Loại bỏ **{len(df_rejected)} trường** vi phạm điều kiện bắt buộc.")
    
    # Tạo bản đồ Folium trung tâm tại nhà học sinh
    m = folium.Map(location=[lat_user, lon_user], zoom_start=14, tiles="OpenStreetMap")
    
    # Nút Phóng to Toàn Màn Hình
    Fullscreen(
        position="topleft",
        title="Phóng toàn màn hình",
        title_cancel="Thoát toàn màn hình",
        force_separate_button=True
    ).add_to(m)
    
    # Ghim vị trí nhà học sinh (Màu đỏ)
    folium.Marker(
        [lat_user, lon_user],
        popup=f"<b>🏠 Vị trí nhà học sinh:</b><br>{dia_chi_nha}",
        icon=folium.Icon(color="red", icon="home", prefix="fa")
    ).add_to(m)
    
    # Bảng màu quy chuẩn theo FSL
    color_map = {
        "Top 1": "#10B981",                   # Xanh lục bảo
        "Top 2": "#3B82F6",                   # Xanh dương
        "Top 3": "#F97316",                   # Cam đất
        "Khác": "#6B7280",                    # Xám trung tính (Trường hợp lệ)
        "Không đạt điều kiện cứng": "#EF4444"  # Đỏ (Trường bị loại bởi Lọc Cứng)
    }
    
    # Vẽ các trường THPT lên bản đồ
    for idx, row in df_final.iterrows():
        rank = row['Xep_Hang']
        color = color_map.get(rank, "#6B7280")
        radius = 14 if rank in ["Top 1", "Top 2", "Top 3"] else (8 if row['Dat_Dieu_Kien_Cung'] else 5)
        web_url = str(row['Website_Truong']) if pd.notnull(row['Website_Truong']) else "#"
        
        status_text = f"<b style='color:green;'>✅ Đạt điều kiện cứng</b>" if row['Dat_Dieu_Kien_Cung'] else f"<b style='color:red;'>❌ Bị loại: {row['Ly_Do_Loc']}</b>"
        
        popup_html = f"""
        <div style='font-family: Arial; width: 250px;'>
            <h4 style='margin:0; color:{color};'>{rank if rank in ['Top 1', 'Top 2', 'Top 3'] else row['Ten_Truong']}</h4>
            <small><b>Trường:</b> {row['Ten_Truong']}</small><br>
            <hr style='margin: 5px 0;'>
            {status_text}<br>
            <b>Loại hình:</b> {row['Loai_Hinh']}<br>
            <b>Điểm chuẩn 2026:</b> {row['Diem_Chuan_2026']} điểm<br>
            <b>Khoảng cách:</b> {row['Khoang_Cach_km']} km<br>
            <b>Bán trú:</b> {row['Ban_Tru']}<br>
            <b>Điểm AHP 7 TC (S_i):</b> <b style='color:red; font-size: 14px;'>{row['Diem_S_i']} / 10</b><br>
            🌐 <a href='{web_url}' target='_blank' style='color:#2563EB; font-weight:bold;'>Truy cập website trường</a>
        </div>
        """
        
        folium.CircleMarker(
            location=[row['Latitude'], row['Longitude']],
            radius=radius,
            color=color,
            fill=True,
            fill_color=color,
            fill_opacity=0.85 if row['Dat_Dieu_Kien_Cung'] else 0.35,
            popup=folium.Popup(popup_html, max_width=270)
        ).add_to(m)
        
    # Render bản đồ vào Streamlit với chiều cao 680px
    st_folium(m, height=680, use_container_width=True)

with col2:
    st.subheader("🏆 Kết Quả Đề Xuất Top 3 Tối Ưu")
    
    top_3 = df_passed[df_passed['Xep_Hang'].isin(["Top 1", "Top 2", "Top 3"])]
    
    if len(top_3) == 0:
        st.warning("⚠️ Không có trường nào vượt qua toàn bộ điều kiện cứng bạn thiết lập! Vui lòng nới lỏng ngân sách học phí, bán kính hoặc yêu cầu bán trú trên Sidebar.")
    else:
        for idx, row in top_3.iterrows():
            rank = row['Xep_Hang']
            badge_color = "🟢" if rank == "Top 1" else ("🔵" if rank == "Top 2" else "🟠")
            web_url = str(row['Website_Truong']) if pd.notnull(row['Website_Truong']) else ""
            
            with st.expander(f"{badge_color} {rank}: {row['Ten_Truong']}", expanded=True):
                st.markdown(f"* **Trạng thái:** <b style='color:green;'>✅ Đã vượt qua điều kiện lọc cứng</b>", unsafe_allow_html=True)
                st.markdown(f"* **Điểm tương thích AHP 7 tiêu chí:** <b style='color:red; font-size:16px;'>{row['Diem_S_i']} / 10</b>", unsafe_allow_html=True)
                st.write(f"* **Khoảng cách thực tế:** `{row['Khoang_Cach_km']} km`")
                st.write(f"* **Điểm chuẩn NV1 (2026):** `{row['Diem_Chuan_2026']} điểm`")
                st.write(f"* **Loại hình & Bán trú:** {row['Loai_Hinh']} | Bán trú: {row['Ban_Tru']}")
                st.write(f"* **CLB nổi bật:** {row['CLB_Noi_Bat']}")
                st.write(f"* **Địa chỉ:** {row['Dia_Chi']}")
                if web_url and web_url != "nan" and web_url != "#":
                    st.markdown(f"* **Website chính thức:** 🌐 [{web_url}]({web_url})")

st.divider()

# -----------------------------------------------------------------------------
# 7. Bảng Dữ Liệu Tra Cứu Toàn Bộ 46 Trường (Phân loại Đạt/Không đạt điều kiện cứng)
# -----------------------------------------------------------------------------
st.subheader("📊 Bảng Chi Tiết Đánh Giá 2 Tầng Lọc (46 Trường THPT)")
st.dataframe(
    df_final[['Xep_Hang', 'Ten_Truong', 'Dat_Dieu_Kien_Cung', 'Ly_Do_Loc', 'Loai_Hinh', 'Diem_Chuan_2026', 'Khoang_Cach_km', 'Ban_Tru', 'Diem_S_i', 'Website_Truong']],
    column_config={
        "Dat_Dieu_Kien_Cung": st.column_config.CheckboxColumn("Đạt Lọc Cứng"),
        "Website_Truong": st.column_config.LinkColumn(
            "Website chính thức",
            display_text="🌐 Link Website"
        )
    },
    use_container_width=True
)
# NỔI BẬT RANH GIỚI HÀNH CHÍNH PHƯỜNG HÒA HƯNG (QUẬN 10)
hoahung_polygon = [
    [10.7865, 106.6605],  # Ngã tư Bắc Hải - Cách Mạng Tháng Tám
    [10.7885, 106.6685],  # Cư xá Bắc Hải - Công viên Lê Thị Riêng
    [10.7825, 106.6745],  # Đường CMT8 - Tô Hiến Thành
    [10.7725, 106.6725],  # Vòng xoay Dân Chủ (Đường 3/2 - CMT8)
    [10.7680, 106.6625],  # Đường 3/2 - Thành Thái
    [10.7735, 106.6565],  # Đường Lý Thường Kiệt - Tô Hiến Thành
    [10.7865, 106.6605],  # Khép kín polygon
]

folium.Polygon(
    locations=hoahung_polygon,
    color="#2563EB",  # Đường viền màu Xanh dương đậm
    weight=3.5,  # Độ dày đường viền
    dash_array="6, 6",  # Nét đứt nổi bật
    fill=True,
    fill_color="#3B82F6",  # Phủ màu xanh nhạt
    fill_opacity=0.18,  # Lớp phủ mờ nhẹ
    popup=folium.Popup(
        "<b>🏛️ RANH GIỚI HÀNH CHÍNH PHƯỜNG HÒA HƯNG (MỚI SÁP NHẬP)</b><br>"
        "<hr style='margin:3px 0;'>"
        "<b>Đơn vị sáp nhập:</b> Phường 12, 13, 15 & 14 (cũ)<br>"
        "<b>Diện tích:</b> ~2.54 km² | <b>Dân số:</b> ~157.865 người<br>"
        "<i>Vùng địa bàn nghiên cứu trung tâm đề tài NCKH 2026</i>",
        max_width=280,
    ),
    tooltip="📍 Ranh giới Hành chính Phường Hòa Hưng (Quận 10)",
).add_to(m)
