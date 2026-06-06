# GradingCopilot

GradingCopilot là ứng dụng AI hỗ trợ giáo viên chấm bài môn Ngữ văn cho học sinh phổ thông. Hệ thống giúp tạo rubric chấm điểm, chấm nháp bài làm, đưa ra nhận xét cho học sinh và cho phép giáo viên duyệt hoặc chỉnh sửa điểm cuối cùng trước khi lưu.

> AI chỉ đóng vai trò **trợ lý chấm bài**. Giáo viên luôn là người quyết định điểm cuối cùng.

---

## 1. Vấn đề

Giáo viên phổ thông thường phải chấm số lượng lớn bài tập, bài kiểm tra và bài văn. Việc chấm bài thủ công tốn nhiều thời gian, trong khi phản hồi cho học sinh thường chậm hoặc chưa đủ chi tiết.

GradingCopilot hướng tới việc hỗ trợ giáo viên:

* Giảm thời gian chấm bài.
* Tạo rubric chấm điểm rõ ràng.
* Chấm nháp bài làm theo từng tiêu chí.
* Gợi ý nhận xét mang tính khích lệ cho học sinh.
* Giữ giáo viên trong vai trò kiểm duyệt cuối cùng.

---

## 2. Tính năng chính

### Tạo rubric chấm điểm

Giáo viên nhập đề bài, thang điểm và khối lớp. AI tạo rubric chấm điểm gồm các tiêu chí, mô tả tiêu chí và điểm tối đa cho từng phần.

### Chấm nháp bài làm

Hệ thống chấm nháp bài làm của học sinh dựa trên rubric đã được giáo viên duyệt. Kết quả gồm:

* Điểm từng tiêu chí.
* Tổng điểm nháp.
* Nhận xét theo từng tiêu chí.
* Điểm mạnh của bài làm.
* Điểm cần cải thiện.
* Gợi ý để học sinh làm bài tốt hơn.
* Mức độ tin cậy của AI.

### Giáo viên duyệt điểm

Giáo viên xem lại kết quả AI, chỉnh sửa điểm hoặc nhận xét nếu cần, sau đó duyệt điểm cuối cùng.

### Quản lý bài nộp

Hệ thống hỗ trợ tạo bài nộp, xem chi tiết bài nộp, thu hồi bài nếu chưa duyệt và duyệt điểm cuối.

---

## 3. Công nghệ sử dụng

| Phần            | Công nghệ                |
| --------------- | ------------------------ |
| Giao diện       | HTML, CSS, JavaScript    |
| Backend         | Python, FastAPI          |
| AI              | Gemini API               |
| Dữ liệu đầu vào | File text / JSON request |
| Chạy server     | Uvicorn                  |

---

## 4. Cấu trúc thư mục

```text
GradingCopilot/
│
├── backend/
│   ├── app/
│   │   └── main.py
│   ├── data/
│   │   ├── de_bai.txt
│   │   └── bai_lam_hoc_sinh.txt
│   ├── .env.example
│   ├── requirements.txt
│   └── README.md
│
├── docs/
│
├── mvp.html
├── user_persona.html
├── user_persona, mvp, prd.html
├── user_stories.html
├── .gitignore
└── README.md
```

---

## 5. Cài đặt backend

### Bước 1: Đi vào thư mục backend

```bash
cd backend
```

### Bước 2: Cài thư viện

```bash
pip install -r requirements.txt
```

### Bước 3: Tạo file `.env`

Tạo file `.env` trong thư mục `backend/`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

### Bước 4: Chạy server

```bash
uvicorn app.main:app --reload
```

Server sẽ chạy tại:

```text
http://127.0.0.1:8000
```

---

## 6. Các API chính

### Kiểm tra trạng thái server

```http
GET /
```

Dùng để kiểm tra backend có đang hoạt động không.

---

### Tạo rubric

```http
POST /rubric/generate
```

Tạo rubric chấm điểm từ đề bài giáo viên nhập.

Ví dụ request:

```json
{
  "assignment_question": "Phân tích hình tượng người lính trong bài thơ Đồng chí của Chính Hữu.",
  "max_score": 10,
  "grade_level": "Lớp 9"
}
```

---

### Tạo rubric từ file

```http
POST /rubric/generate-from-files
```

Đọc đề bài từ file `.txt` trong thư mục `data/`, sau đó tạo rubric chấm điểm.

---

### Chấm bài làm học sinh

```http
POST /grade
```

Chấm bài làm của học sinh dựa trên rubric đã được duyệt.

---

### Chấm bài từ file

```http
POST /grade/from-files
```

Đọc đề bài và bài làm học sinh từ file `.txt`, sau đó trả về kết quả chấm nháp.

---

### Duyệt điểm

```http
POST /grade/approve
```

Cho phép giáo viên duyệt hoặc chỉnh sửa điểm cuối cùng và nhận xét.

---

### Tạo bài nộp

```http
POST /submissions
```

Tạo bài nộp của học sinh và cho AI chấm nháp.

---

### Xem chi tiết bài nộp

```http
GET /submissions/{id}
```

Trả về thông tin chi tiết của một bài nộp.

---

### Xóa hoặc thu hồi bài nộp

```http
DELETE /submissions/{id}
```

Xóa hoặc thu hồi bài nộp nếu giáo viên chưa duyệt điểm.

---

### Duyệt bài nộp

```http
PUT /submissions/{id}/approve
```

Cho phép giáo viên duyệt hoặc chỉnh sửa điểm cuối cùng của bài nộp.

---

## 7. Luồng hoạt động

```text
Giáo viên nhập đề bài
        ↓
AI tạo rubric chấm điểm
        ↓
Giáo viên xem và duyệt rubric
        ↓
Học sinh nộp bài
        ↓
AI chấm nháp theo rubric
        ↓
Giáo viên xem lại kết quả
        ↓
Giáo viên duyệt hoặc chỉnh sửa điểm
        ↓
Lưu điểm và nhận xét cuối cùng
```

---

## 8. Nguyên tắc giáo viên kiểm duyệt

GradingCopilot được thiết kế theo nguyên tắc giáo viên luôn là người kiểm duyệt cuối cùng:

* AI không thay thế giáo viên.
* AI chỉ tạo rubric nháp và điểm nháp.
* Giáo viên xem lại, chỉnh sửa và duyệt kết quả.
* Điểm cuối cùng thuộc quyền quyết định của giáo viên.

Điều này đặc biệt quan trọng vì chấm bài văn cần hiểu ngữ cảnh, sự công bằng và đánh giá chuyên môn từ giáo viên.

---

## 9. Thành viên nhóm

| Thành viên     | Vai trò            | Nhiệm vụ                                                                                                                                  |
| -------------- | ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------- |
| Hoàng Anh Thư  | PM / AI / Leader   | Lên kế hoạch sản phẩm, xác định phạm vi tính năng, thiết kế luồng chấm điểm bằng AI, xây dựng logic rubric, điều phối nhóm, viết tài liệu |
| Phí Đình Mạnh  | AI / Backend       | Xây dựng backend API, triển khai FastAPI, tích hợp Gemini, xây dựng các endpoint chấm điểm, xử lý dữ liệu                                 |
| Nguyễn Viết Du | Frontend / Backend | Xây dựng giao diện prototype, thiết kế luồng tương tác người dùng, hỗ trợ tích hợp frontend với backend                                   |

---

## 10. Mục tiêu MVP

MVP tập trung chứng minh luồng chấm bài cốt lõi:

1. Giáo viên có thể tạo hoặc cung cấp rubric.
2. AI có thể chấm bài học sinh dựa trên rubric.
3. Giáo viên có thể xem lại và duyệt điểm cuối cùng.
4. Học sinh nhận được phản hồi mang tính xây dựng.

Phiên bản hiện tại ưu tiên logic chấm điểm và luồng giáo viên duyệt trước khi mở rộng sang OCR và hạ tầng production.

---

## 11. Hướng phát triển tiếp theo

* OCR để đọc bài viết tay của học sinh.
* Upload ảnh hoặc PDF bài làm.
* Đăng nhập cho giáo viên và học sinh.
* Tích hợp database thật.
* Dashboard theo dõi cả lớp.
* Theo dõi tiến bộ của từng học sinh.
* Tổng hợp lỗi phổ biến của lớp.
* Xuất kết quả chấm điểm ra Excel hoặc PDF.
* Cải thiện prompt và pipeline đánh giá.
* Mở rộng sang các môn học khác ngoài Ngữ văn.

---

## 12. Lưu ý

Đây là sản phẩm MVP phục vụ mục đích học tập và thử nghiệm. Điểm số và nhận xét do AI tạo ra chỉ mang tính gợi ý. Giáo viên cần xem lại và duyệt toàn bộ kết quả trước khi sử dụng chính thức.
