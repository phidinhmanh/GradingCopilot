# Tài liệu Cơ sở Hạ tầng & Triển khai (Infrastructure & Deployment) - Render Free Tier

Tài liệu này hướng dẫn cách cấu hình và triển khai dự án **AI Grading Copilot** dạng **Monorepo** lên các dịch vụ đám mây miễn phí (Render, Vercel, Neon, Cloudflare R2).

---

## 1. Bản đồ Phân bổ Dịch vụ Miễn phí (Zero-Cost Hosting Stack)

Để chạy dự án hoàn toàn miễn phí mà vẫn đảm bảo tính ổn định bền vững, hệ thống được cấu hình phân tán như sau:

| Thành phần | Dịch vụ đề xuất | Cấu hình & Lợi ích |
| :--- | :--- | :--- |
| **Frontend** (Next.js) | **Vercel** (Free Tier) | • Chạy dạng Serverless, tốc độ phản hồi cực nhanh tại VN.<br>• **Không bị ngủ đông** (khác với Render Free Web Service).<br>• Cấu hình deploy từ monorepo folder `/frontend`. |
| **Backend API** (FastAPI) | **Render** (Free Web Service) | • CPU dùng chung, 512MB RAM.<br>• Có cơ chế ngủ đông (cold-start) sau 15 phút idle (mất 50s để khởi động lại).<br>• Cấu hình deploy từ monorepo folder `/backend`. |
| **Database** (PostgreSQL) | **Neon.tech** hoặc **Supabase** | • Cung cấp PostgreSQL miễn phí vĩnh viễn.<br>• Tự động sao lưu dữ liệu.<br>• Tránh giới hạn 90 ngày của Render Database. |
| **Object Storage** (Ảnh bài làm) | **Cloudflare R2** | • Miễn phí 10GB lưu trữ và không tính tiền băng thông (0$ Egress fee). |

---

## 2. Hướng dẫn Cấu hình Supabase PostgreSQL (Free Tier)

Hệ thống sử dụng Supabase thuần túy như một **Managed PostgreSQL Database** để lưu trữ dữ liệu bền vững (tránh giới hạn hết hạn 90 ngày của database mặc định trên Render).

### Các bước lấy Connection String:
1. Đăng ký tài khoản tại [Supabase](https://supabase.com) và tạo một Project mới (chọn Region **Singapore** để giảm độ trễ về Việt Nam).
2. Vào **Project Settings** -> chọn tab **Database**.
3. Kéo xuống mục **Connection String**, chọn tab **URI** (định dạng URL kết nối).
4. Sao chép chuỗi kết nối và thay thế `[YOUR-PASSWORD]` bằng mật khẩu database của bạn.
   * *Định dạng mẫu:* `postgresql://postgres:MySecurePassword123@db.abcxyz.supabase.co:6543/postgres?pgbouncer=true`

### Lưu ý quan trọng khi chạy Production:
* **Sử dụng cổng 6543 (PgBouncer):** Vì FastAPI chạy async có thể sinh ra lượng kết nối đồng thời vượt giới hạn của Supabase Free Tier (tối đa 60 connections), bạn **bắt buộc** phải sử dụng cổng **6543** (PgBouncer connection pooler) thay vì cổng Postgres mặc định `5432` và thêm đuôi `?pgbouncer=true` vào URL kết nối.
* **Database Tự ngủ đông (Auto-pause):** Nếu database không nhận truy vấn trong vòng 1 tuần, Supabase sẽ tạm ngừng (pause) dịch vụ để tiết kiệm tài nguyên. Nếu gặp lỗi kết nối API Backend, bạn chỉ cần vào Supabase Dashboard bấm nút **Resume** để phục hồi.

---

## 3. File cấu hình Render Blueprint (`render.yaml`)

Để tự động thiết lập toàn bộ hạ tầng backend chỉ với 1 click từ Git Monorepo, chúng ta sử dụng **Render Blueprint**. Hãy tạo file `render.yaml` ở thư mục gốc của dự án:

```yaml
services:
  # 1. Backend API Service
  - type: web
    name: grading-copilot-backend
    env: python
    plan: free # Sử dụng gói miễn phí
    rootDir: backend # Trỏ thư mục gốc của backend trong Monorepo
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn src.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        sync: false # Điền link kết nối PostgreSQL lấy từ Supabase (Bước 2)
      - key: CLOUDFLARE_R2_BUCKET
        sync: false
      - key: CLOUDFLARE_R2_ACCESS_KEY
        sync: false
      - key: CLOUDFLARE_R2_SECRET_KEY
        sync: false
      - key: OCR_PROVIDER_CREDENTIALS
        sync: false # Thông tin cấu hình/API key của bên cung cấp OCR
      - key: AI_MODEL_API_KEY
        sync: false # API key của bên cung cấp mô hình ngôn ngữ lớn (LLM)
      - key: JWT_SECRET
        generateValue: true # Tự động tạo mã JWT ngẫu nhiên bảo mật
```

---

## 4. Quy trình Deploy Frontend lên Vercel từ Monorepo

Vercel là lựa chọn tối ưu nhất cho Next.js Frontend để tránh việc trang web bị tải chậm do cold-start của Render.

### Các bước cấu hình trên Vercel Dashboard:
1. Nhập repository Git của dự án.
2. Tại màn hình cấu hình dự án, mở phần **Framework Preset** chọn **Next.js**.
3. **Root Directory:** Điền `frontend` (để Vercel biết chỉ build code trong thư mục frontend).
4. **Environment Variables:** Điền các biến môi trường kết nối API:
   * `NEXT_PUBLIC_API_URL`: Trỏ đến URL của Render Backend (Ví dụ: `https://grading-copilot-backend.onrender.com`).
5. Nhấn **Deploy**. Vercel sẽ tự động build và cấp phát domain miễn phí dạng `*.vercel.app`.

---

## 5. Cấu hình Cloudflare R2 cho việc Học sinh nộp ảnh di động

Vì học sinh sẽ sử dụng điện thoại di động để chụp ảnh bài tập và tải trực tiếp lên Cloudflare R2, cấu hình CORS cần cho phép các yêu cầu kết nối từ các thiết bị di động truy cập domain frontend.

### Các bước thiết lập trên Cloudflare R2:
1. Tạo một bucket tên là `grading-copilot-submissions`.
2. Truy cập vào mục **Settings** của Bucket -> **CORS Policy** -> Thêm cấu hình CORS:
   ```json
   [
     {
       "AllowedOrigins": ["https://*.vercel.app", "http://localhost:3000"],
       "AllowedMethods": ["GET", "PUT", "POST"],
       "AllowedHeaders": ["*"],
       "ExposeHeaders": []
     }
   ]
   ```
3. Tạo API Token của Cloudflare R2 với quyền **Edit** để lấy `Access Key ID` và `Secret Access Key` điền vào biến môi trường của Render Backend.

---

## 6. Giải pháp khắc phục nhược điểm "Ngủ đông" của Render Free Tier

Render Free Web Service sẽ tự động tắt (sleep) nếu không có truy cập trong 15 phút. Khi học sinh mở điện thoại để nộp bài tập, sẽ mất khoảng 50 giây để API khởi động lại (Cold Start), gây cảm giác bị đơ.

### Cách giải quyết (Workarounds):
1. **Frontend Handling (Loading UI):**
   * Trên giao diện nộp bài của học sinh (`frontend/src/app/student/upload`), khi bấm nút "Nộp bài", nếu phát hiện API Backend chưa sẵn sàng, hiển thị một spinner Loading trực quan kèm lời nhắn: *"Hệ thống đang kết nối máy chủ nhận diện bài làm (mất khoảng 30-40 giây), xin vui lòng không đóng trình duyệt..."*
2. **Ping Service tự động (Tùy chọn):**
   * Có thể sử dụng các dịch vụ cronjob miễn phí bên ngoài (như **UptimeRobot** hoặc **Cron-Job.org**) để gửi một request GET rỗng `/health` đến API Backend 14 phút một lần trong khung giờ học sinh thường làm bài tập (ví dụ: 19h tối - 23h đêm) để giữ cho Render Backend luôn "thức".

