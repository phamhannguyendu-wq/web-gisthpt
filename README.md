# 🎓 Web-GIS Tư Vấn Lựa Chọn Trường THPT Cá Nhân Hóa (Phường Hòa Hưng)

> **Dự án Nghiên cứu Khoa học Kỹ thuật (NCKH 2026)**  
> **Tên đề tài:** *Xây dựng hệ thống Web-GIS hỗ trợ tư vấn lựa chọn trường THPT cá nhân hóa theo độ tương thích tiêu chí tại Phường Hòa Hưng, Quận 10, TP. Hồ Chí Minh.*

---

## 📌 Giới Thiệu
Ứng dụng Web-GIS được xây dựng nhằm hỗ trợ phụ huynh và học sinh Lớp 9 giải quyết bài toán chọn trường THPT trong kỳ thi tuyển sinh Lớp 10. Thay vì chỉ dựa vào điểm chuẩn lịch sử đơn thuần, hệ thống tích hợp **mô hình quyết định đa tiêu chí (MCDA-AHP)** kết hợp với **phân tích không gian GIS** để tự động tính toán điểm tương thích (\\(S_i\\)) và đề xuất **Top 3 trường phù hợp nhất** theo thời gian thực.

---

## ✨ Tính Năng Nổi Bật
- **Cá nhân hóa 100% theo 7 Tiêu chí AHP:** Cho phép người dùng tùy chỉnh Điểm dự kiến, Vị trí nhà, Tổ hợp môn tự chọn GDPT 2018, Bán trú, Học phí tối đa, Học 2 buổi/ngày và Lĩnh vực Câu lạc bộ yêu thích.
- **Định tuyến giao thông thực tế:** Tự động quy đổi địa chỉ gõ tay thành tọa độ (Geocoding) và tính khoảng cách di chuyển thực tế.
- **Bản đồ không gian tương tác (Folium):** Trực quan hóa vị trí nhà học sinh và 46 trường THPT xung quanh; tự động đổi màu ký hiệu (*Top 1: Xanh lục bảo*, *Top 2: Xanh dương*, *Top 3: Cam đất*, *Khác: Xám*).
- **Giao diện phản hồi thời gian thực (Form Submit):** Thiết kế nút bấm **`🔍 TƯ VẤN CHỌN TRƯỜNG PHÙ HỢP`** giúp tối ưu hóa hiệu năng và tránh hiện tượng giật lag khi điều chỉnh thông tin.
- **Bảng dữ liệu tra cứu đầy đủ:** Cung cấp thông tin chi tiết về điểm chuẩn 2026, loại hình trường, dịch vụ bán trú, tuyến xe buýt và liên kết website chính thức của 46 trường.

---

## 🛠️ Công Nghệ Sử Dụng
* **Ngôn ngữ lập trình:** Python 3.12
* **Khung giao diện Web:** [Streamlit](https://streamlit.io/)
* **Bản đồ không gian:** [Folium](https://python-visualization.github.io/folium/) & `streamlit-folium`
* **Định vị & Geocoding:** `geopy` (Nominatim API)
* **Xử lý dữ liệu:** `pandas`, `openpyxl`
* **Tích hợp bản đồ Cloud:** Google Apps Script / Google Maps API & Felt.com

---

## 📊 Mô Hình Đánh Giá MCDA-AHP (7 Tiêu Chí)
Hệ thống áp dụng Ma trận so sánh cặp AHP đã qua kiểm định độ nhất quán (\\(CR = 0.0 < 0.1\\)):

| STT | Tiêu chí đánh giá (\\(C_i\\)) | Trọng số AHP (\\(w_i\\)) |
| :-: | :--- | :---: |
| 1 | **Chất lượng đào tạo & CLB** | **15.40%** |
| 2 | **Môi trường & Cơ sở vật chất** | **15.15%** |
| 3 | **Định hướng Tổ hợp môn GDPT 2018** | **14.49%** |
| 4 | **Khả năng trúng tuyển (Điểm chuẩn)** | **14.39%** |
| 5 | **Điều kiện Tài chính (Học phí)** | **13.96%** |
| 6 | **Vị trí & Khả năng di chuyển** | **13.77%** |
| 7 | **Mô hình học tập / Dịch vụ Bán trú** | **12.84%** |

---

## 📁 Cấu Trúc Thư Mục Dự Án
```text
webgis_thpt/
├── app.py                                   # Mã nguồn chính của ứng dụng Streamlit
├── CSDL_WebGIS_TruongTHPT_7TieuChi.xlsx     # Cơ sở dữ liệu 46 trường THPT chuẩn hóa
├── requirements.txt                         # Danh sách thư viện Python cần thiết
└── README.md                                # Tài liệu hướng dẫn dự án
🚀 Hướng Dẫn Cài Đặt & Chạy Cục Bộ (Local)
1. Yêu cầu tiền đề
Cài đặt Python 3.10+ trên máy tính.
2. Cài đặt thư viện phụ thuộc
Mở Terminal / Command Prompt tại thư mục dự án và chạy lệnh:
pip install streamlit folium streamlit-folium geopy pandas openpyxl
3. Khởi chạy ứng dụng Web-GIS
Chạy lệnh sau để bật giao diện Web-GIS trên trình duyệt:
python -m streamlit run app.py
Ứng dụng sẽ tự động mở tại địa chỉ: http://localhost:8501
