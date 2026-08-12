# 📋 SPEC - Ứng dụng Quản lý Công việc Agribank

## 🎯 Tổng quan dự án

**Tên dự án:** Agribank Task Management  
**Mục đích:** Ứng dụng quản lý công việc nội bộ nhóm KTNB  
**Phiên bản:** 1.0.0  
**Ngôn ngữ:** Tiếng Việt

---

## 📌 Yêu cầu chức năng

### 1. Quản lý Công việc
- ✅ **Xem danh sách công việc**: Hiển thị tất cả công việc dưới dạng danh sách
- ✅ **Thêm công việc mới**: Nhập tên, người phụ trách, tạo công việc
- ✅ **Chỉnh sửa công việc**: Cập nhật tên và người phụ trách
- ✅ **Xóa công việc**: Xóa công việc khỏi danh sách
- ✅ **Đánh dấu hoàn thành**: Checkbox để chuyển đổi trạng thái

### 2. Lọc và Tìm kiếm
- ✅ **Lọc theo trạng thái**:
  - Tất cả công việc
  - Công việc đang làm
  - Công việc đã hoàn thành
- ✅ **Thống kê**: Hiển thị tổng số công việc

### 3. Lưu trữ dữ liệu
- ✅ **Lưu tạm trong bộ nhớ**: Sử dụng localStorage (dữ liệu tồn tại sau khi đóng trình duyệt)
- ✅ **Dữ liệu mẫu**: App có sẵn 2 công việc mẫu khi chạy lần đầu

---

## 📊 Cấu trúc dữ liệu

Mỗi công việc gồm các thuộc tính:

```javascript
{
  id: number,              // ID duy nhất (tạo từ timestamp)
  ten: string,             // Tên công việc
  nguoi_phu_trach: string, // Người phụ trách
  trang_thai: string       // Trạng thái: 'pending' (đang làm) | 'completed' (hoàn thành)
}
```

---

## 📁 Cấu trúc thư mục

```
agribank-todo/
├── index.html      # Giao diện HTML (tiếng Việt)
├── style.css       # Styling CSS (responsive, gradient)
├── script.js       # Logic JavaScript (xử lý công việc)
├── SPEC.md         # Tài liệu spec này
└── README.md       # Hướng dẫn chạy
```

---

## 🚀 Hướng dẫn chạy

### Cách 1: Chạy trực tiếp trong trình duyệt (đơn giản nhất)

1. **Mở file `index.html`** trực tiếp bằng trình duyệt:
   - Double-click vào file `index.html`, hoặc
   - Chuột phải → Open with → Chrome/Firefox/Edge

2. **Ứng dụng sẽ tải và chạy ngay lập tức** 🎉

### Cách 2: Chạy bằng Live Server (nếu có VS Code)

1. Cài đặt extension "Live Server" trong VS Code
2. Chuột phải vào file `index.html` → "Open with Live Server"
3. Trình duyệt sẽ mở tự động tại `http://localhost:5500`

### Cách 3: Chạy bằng Python (nếu có Python)

```bash
# Python 3.x
python -m http.server 8000

# Hoặc Python 2.x
python -m SimpleHTTPServer 8000
```

Sau đó mở trình duyệt tại: `http://localhost:8000`

### Cách 4: Chạy bằng Node.js

```bash
# Cài đặt http-server toàn cục (lần đầu)
npm install -g http-server

# Chạy server
http-server

# Trình duyệt sẽ mở tại: http://127.0.0.1:8080
```

---

## 🎨 Tính năng giao diện

### Giao diện chính
- 🎨 **Gradient đẹp**: Nền tím-xanh modern
- 📱 **Responsive**: Tự động thích ứng với điện thoại, tablet, desktop
- 🌍 **Tiếng Việt**: Toàn bộ giao diện bằng tiếng Việt
- ⚡ **Nhanh**: Load ngay, không cần backend

### Các thành phần
1. **Header**: Logo, tiêu đề ứng dụng
2. **Form thêm công việc**: Input tên, người phụ trách + nút thêm
3. **Bộ lọc**: 3 nút lọc (Tất cả, Đang làm, Hoàn thành)
4. **Danh sách công việc**: Hiển thị công việc với checkbox, nút sửa/xóa
5. **Thống kê**: Tổng số công việc

---

## 💾 Lưu trữ dữ liệu

Ứng dụng sử dụng **localStorage** của trình duyệt:
- ✅ Dữ liệu **tự động lưu** sau mỗi thay đổi
- ✅ Dữ liệu **vẫn tồn tại** khi đóng/mở lại trình duyệt
- ✅ Dữ liệu lưu trong key: `agribank_tasks`

**Để xóa dữ liệu:**
```javascript
// Mở Console (F12) và chạy:
localStorage.removeItem('agribank_tasks');
location.reload();
```

---

## 📝 Hướng dẫn sử dụng

### ➕ Thêm công việc
1. Nhập **tên công việc** vào ô "Tên công việc"
2. Nhập **tên người phụ trách** vào ô "Người phụ trách"
3. Nhấn nút "➕ Thêm Công việc" hoặc phím Enter
4. Công việc mới sẽ hiển thị trong danh sách

### ✏️ Chỉnh sửa công việc
1. Nhấn nút "✏️ Sửa" trên công việc cần chỉnh sửa
2. Thông tin sẽ tự động fill vào form
3. Thay đổi thông tin và nhấn "✏️ Cập nhật Công việc"

### 🗑️ Xóa công việc
1. Nhấn nút "🗑️ Xóa" trên công việc
2. Xác nhận xóa trong hộp thoại
3. Công việc sẽ được xóa ngay lập tức

### ✓ Đánh dấu hoàn thành
1. Nhấn **checkbox** bên trái công việc
2. Công việc sẽ chuyển sang trạng thái "✓ Hoàn thành"
3. Text sẽ bị gạch ngang và mờ đi

### 🔍 Lọc công việc
1. Nhấn nút **"Tất cả"**: Xem tất cả công việc
2. Nhấn nút **"Đang làm"**: Xem chỉ công việc chưa hoàn thành
3. Nhấn nút **"Đã hoàn thành"**: Xem chỉ công việc đã hoàn thành

---

## 🛠️ Công nghệ sử dụng

| Công nghệ | Mục đích |
|-----------|---------|
| **HTML5** | Cấu trúc trang web |
| **CSS3** | Styling, animation, responsive |
| **JavaScript (Vanilla)** | Logic ứng dụng |
| **localStorage** | Lưu trữ dữ liệu |

---

## 📋 Code Quality

✅ **Code gọn, dễ đọc:**
- Mỗi hàm có chú thích rõ ràng
- Tên biến, hàm tiếng Việt dễ hiểu
- Có phân chia section rõ ràng

✅ **Không cần backend:**
- Tất cả logic xử lý phía client
- Không cần server hay database
- Chạy offline được

✅ **Dễ bảo trì:**
- Code modular, dễ sửa đổi
- Đơn giản hoá tối đa
- Dễ thêm tính năng mới

---

## 🎯 Tính năng có thể mở rộng

Các tính năng có thể thêm vào sau:
- 📅 Ngày hạn chót (deadline)
- 🏷️ Gán nhãn/tag cho công việc
- 👥 Chia sẻ công việc với đội
- 📊 Thống kê hoàn thành công việc
- 🔔 Thông báo nhắc nhở
- 🌙 Chế độ dark mode
- 🌐 Đồng bộ với server/database
- 📱 Native mobile app

---

## 📞 Liên hệ & Support

- **Nhóm phát triển:** KTNB
- **Dự án:** Agribank RAG
- **Phiên bản hiện tại:** 1.0.0

---

## 📄 Ghi chú

- Ứng dụng **không cần kết nối internet** để chạy
- Dữ liệu lưu **cục bộ trên máy tính** (localStorage)
- **Xóa dữ liệu trình duyệt** sẽ mất toàn bộ công việc
- **Tương thích với** Chrome, Firefox, Edge, Safari

---

**Ngày tạo:** 12/08/2026  
**Trạng thái:** ✅ Hoàn thành & sẵn sàng chạy

