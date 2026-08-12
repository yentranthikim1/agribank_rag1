# 🚀 Quản lý Công việc - Quick Start Guide

## ⚡ Chạy Ngay

### Cách 1: Đơn giản nhất - Click vào file (khuyên dùng)
```
Chuột phải vào index.html → Open with → Chrome/Firefox/Edge
```
✅ Chạy ngay, không cần cài đặt gì

### Cách 2: Live Server trên VS Code
```bash
1. Cài extension "Live Server" trong VS Code
2. Chuột phải vào index.html
3. Chọn "Open with Live Server"
```

### Cách 3: Python
```bash
# Mở terminal trong thư mục agribank-todo
python -m http.server 8000

# Mở trình duyệt: http://localhost:8000
```

### Cách 4: Node.js
```bash
npm install -g http-server
http-server
# Mở: http://127.0.0.1:8080
```

---

## 📋 Các Tính Năng

✅ **Thêm công việc**: Nhập tên + người phụ trách  
✅ **Chỉnh sửa**: Nút sửa trên mỗi công việc  
✅ **Xóa**: Nút xóa với xác nhận  
✅ **Đánh dấu hoàn thành**: Checkbox bên trái  
✅ **Lọc**: Tất cả / Đang làm / Hoàn thành  
✅ **Lưu tự động**: Dữ liệu lưu trong localStorage  

---

## 📁 File cấu thành

| File | Mục đích |
|------|---------|
| `index.html` | Giao diện HTML |
| `style.css` | Styling & responsive design |
| `script.js` | Logic xử lý công việc |
| `SPEC.md` | Tài liệu chi tiết |
| `README.md` | File này |

---

## 🎯 Cách sử dụng

```
1. Điền tên công việc + người phụ trách
2. Nhấn "➕ Thêm Công việc"
3. Nhấn checkbox để đánh dấu hoàn thành
4. Sử dụng "✏️ Sửa" để chỉnh sửa
5. Sử dụng "🗑️ Xóa" để xóa công việc
6. Lọc theo nút trên cùng
```

---

## 💾 Dữ liệu được lưu đâu?

Dữ liệu được lưu trong **localStorage** của trình duyệt:
- Tự động lưu sau mỗi thay đổi
- Vẫn tồn tại khi đóng trình duyệt
- Xóa khi xóa dữ liệu trình duyệt

**Xóa dữ liệu:**
```javascript
// Mở F12 (Console) và gõ:
localStorage.removeItem('agribank_tasks');
location.reload();
```

---

## 🛠️ Công nghệ

- HTML5 + CSS3 + JavaScript (Vanilla)
- Không cần backend, chạy offline
- Responsive, tương thích tất cả trình duyệt

---

## 📱 Responsive

✅ Desktop (1024px+)  
✅ Tablet (768px-1023px)  
✅ Mobile (dưới 768px)

---

## 🎨 Theme

- Gradient: Tím → Xanh
- Màu chủ đạo: #667eea (xanh tím)
- Font: Segoe UI, Tahoma, Geneva, Verdana

---

## 📝 Mô tả công việc

Mỗi công việc gồm:
```
{
  id: 1,
  ten: "Tên công việc",
  nguoi_phu_trach: "Tên người",
  trang_thai: "pending" hoặc "completed"
}
```

---

## ❓ Troubleshooting

**Q: Không thể mở file?**  
A: Chạy bằng python hoặc live server thay vì mở file trực tiếp

**Q: Dữ liệu mất khi đóng trình duyệt?**  
A: Kiểm tra xem localStorage có bị tắt không, hoặc xóa dữ liệu trình duyệt

**Q: Ứng dụng chậm?**  
A: Xóa localStorage để reset dữ liệu cũ

**Q: Không có gì xảy ra khi thêm công việc?**  
A: Kiểm tra console (F12) để xem lỗi

---

## 📞 Liên hệ

Dự án: Agribank RAG - KTNB  
Phiên bản: 1.0.0  
Ngày: 12/08/2026

---

**Hướng dẫn chi tiết xem tại: [SPEC.md](SPEC.md)**
