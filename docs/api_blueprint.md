# Hợp đồng API (API Blueprint Specification) - v1

Tài liệu này định nghĩa chi tiết các API endpoints của hệ thống **AI Grading Copilot**, đóng vai trò là **Hợp đồng kỹ thuật (Contract)** giữa Frontend (Next.js) và Backend (FastAPI).

---

## 1. Quy chuẩn chung (Global Conventions)

* **Base URL:** `/api/v1`
* **Content-Type:** `application/json`
* **Authentication:** JWT Bearer Token gửi qua header: `Authorization: Bearer <token>` (hoặc Cookie bảo mật).
* **Định dạng lỗi (Error Response):**
  ```json
  {
    "detail": "Mô tả chi tiết lỗi xảy ra"
  }
  ```

---

## 2. Danh sách Endpoints chi tiết

```mermaid
tag DB
    subgraph Auth [Xác thực]
        POST_register[POST /auth/register]
        POST_login[POST /auth/login]
    end
    subgraph Classroom [Lớp học]
        POST_class[POST /classrooms]
        GET_classes[GET /classrooms]
        POST_join[POST /classrooms/join]
    end
    subgraph Assignment [Bài tập]
        POST_assign[POST /assignments]
        GET_assigns[GET /assignments/class/{id}]
    end
    subgraph Submission [Bài nộp & AI]
        POST_presign[POST /submissions/presign]
        POST_submit[POST /submissions]
        GET_sub_detail[GET /submissions/{id}]
    end
    subgraph Grading [Duyệt điểm]
        GET_grade[GET /grades/submission/{id}]
        PUT_approve[PUT /grades/submission/{id}/approve]
    end
```

---

### MÔ-ĐUN 1: XÁC THỰC (AUTHENTICATION)

#### 1. Đăng ký tài khoản
* **Endpoint:** `POST /auth/register`
* **Mô tả:** Đăng ký tài khoản cho Giáo viên hoặc Học sinh.
* **Payload:**
  ```json
  {
    "email": "teacher@school.edu.vn",
    "password": "SecurePassword123",
    "role": "teacher" // Hoặc "student"
  }
  ```
* **Phản hồi thành công (201 Created):**
  ```json
  {
    "id": "e838efca-8178-433a-bd1e-53c072d6279f",
    "email": "teacher@school.edu.vn",
    "role": "teacher",
    "created_at": "2026-06-05T08:00:00Z"
  }
  ```

#### 2. Đăng nhập
* **Endpoint:** `POST /auth/login`
* **Payload:**
  ```json
  {
    "email": "teacher@school.edu.vn",
    "password": "SecurePassword123"
  }
  ```
* **Phản hồi thành công (200 OK):**
  ```json
  {
    "access_token": "eyJhbGciOi...",
    "token_type": "bearer",
    "user": {
      "id": "e838efca-8178-433a-bd1e-53c072d6279f",
      "email": "teacher@school.edu.vn",
      "role": "teacher"
    }
  }
  ```

---

### MÔ-ĐUN 2: QUẢN LÝ LỚP HỌC (CLASSROOMS)

#### 1. Tạo lớp học mới (Chỉ dành cho Giáo viên)
* **Endpoint:** `POST /classrooms`
* **Payload:**
  ```json
  {
    "name": "Lớp 8A1 - Môn Văn"
  }
  ```
* **Phản hồi thành công (201 Created):**
  ```json
  {
    "id": "a90df12d-118c-4a30-9b48-1212abfde211",
    "name": "Lớp 8A1 - Môn Văn",
    "class_code": "VVAN8A1", // Sinh ngẫu nhiên và duy nhất để HS join
    "teacher_id": "e838efca-8178-433a-bd1e-53c072d6279f"
  }
  ```

#### 2. Học sinh tham gia lớp học bằng mã (Chỉ dành cho Học sinh)
* **Endpoint:** `POST /classrooms/join`
* **Payload:**
  ```json
  {
    "class_code": "VVAN8A1",
    "student_name": "Nguyễn Văn A" // Tên hiển thị của học sinh trong lớp này
  }
  ```
* **Phản hồi thành công (200 OK):**
  ```json
  {
    "student_id": "b1827cfd-11bb-4554-aa22-544bbddcc77b",
    "classroom_name": "Lớp 8A1 - Môn Văn"
  }
  ```

---

### MÔ-ĐUN 3: BÀI TẬP VỀ NHÀ (ASSIGNMENTS)

#### 1. Tạo bài tập về nhà mới (Chỉ dành cho Giáo viên)
* **Endpoint:** `POST /assignments`
* **Payload:**
  ```json
  {
    "title": "Bài viết Nghị luận xã hội số 1",
    "description": "Nêu suy nghĩ của em về lòng dũng cảm (viết đoạn văn 200 chữ).",
    "deadline": "2026-06-12T23:59:00Z",
    "classroom_id": "a90df12d-118c-4a30-9b48-1212abfde211",
    "answer_key_url": "https://r2.gradingapp.com/keys/dapan_bai1.txt", // Option
    "rubric": {
      "title": "Rubric NLXH 200 chữ",
      "criteria": [
        {
          "id": "c1",
          "name": "Bố cục & Lập luận",
          "max_points": 5.0,
          "description": "Mở đoạn rõ ràng, dẫn chứng thuyết phục."
        },
        {
          "id": "c2",
          "name": "Ngữ pháp & Chính tả",
          "max_points": 5.0,
          "description": "Không sai quá 2 lỗi chính tả/ngữ pháp."
        }
      ]
    }
  }
  ```
* **Phản hồi thành công (201 Created):**
  ```json
  {
    "id": "c567feab-129d-4001-ba81-1234abcdffee",
    "title": "Bài viết Nghị luận xã hội số 1",
    "classroom_id": "a90df12d-118c-4a30-9b48-1212abfde211",
    "created_at": "2026-06-05T08:15:00Z"
  }
  ```

---

### MÔ-ĐUN 4: BÀI NỘP HỌC SINH (SUBMISSIONS)

#### 1. Yêu cầu sinh Presigned URL upload ảnh (Chỉ dành cho Học sinh)
* **Endpoint:** `POST /submissions/presign`
* **Payload:**
  ```json
  {
    "file_name": "homework_page1.jpg",
    "content_type": "image/jpeg"
  }
  ```
* **Phản hồi thành công (200 OK):**
  ```json
  {
    "upload_url": "https://grading-copilot.r2.cloudflare.com/temp/uuid-file.jpg?X-Amz-Signature=...",
    "download_url": "https://grading-copilot.r2.cloudflare.com/temp/uuid-file.jpg"
  }
  ```

#### 2. Nộp bài tập (Chỉ dành cho Học sinh)
* **Endpoint:** `POST /submissions`
* **Mô tả:** Gọi sau khi học sinh đã upload thành công ảnh lên Cloudflare R2 bằng URL ở bước trước. Gọi API này sẽ kích hoạt tác vụ chấm điểm chạy ngầm.
* **Payload:**
  ```json
  {
    "assignment_id": "c567feab-129d-4001-ba81-1234abcdffee",
    "student_id": "b1827cfd-11bb-4554-aa22-544bbddcc77b",
    "image_url": "https://grading-copilot.r2.cloudflare.com/temp/uuid-file.jpg"
  }
  ```
* **Phản hồi thành công (202 Accepted):**
  ```json
  {
    "id": "f892ccdd-1234-abcd-5678-eeeeffffbbbb",
    "status": "processing", // Trạng thái ban đầu
    "message": "Nộp bài thành công. Tiến trình chấm điểm tự động đã bắt đầu."
  }
  ```

#### 3. Lấy chi tiết bài nộp và trạng thái chấm
* **Endpoint:** `GET /submissions/{id}`
* **Phản hồi thành công (200 OK):**
  ```json
  {
    "id": "f892ccdd-1234-abcd-5678-eeeeffffbbbb",
    "assignment_id": "c567feab-129d-4001-ba81-1234abcdffee",
    "student_name": "Nguyễn Văn A",
    "image_url": "https://...",
    "ocr_text": "Hôm nay em xin viết về lòng dũng cảm...", // Sẽ có dữ liệu sau khi OCR xong
    "status": "graded", // processing | graded | error
    "submitted_at": "2026-06-05T08:20:00Z"
  }
  ```

---

### MÔ-ĐUN 5: DUYỆT ĐIỂM (GRADING REVIEW)

#### 1. Lấy kết quả chấm chi tiết (AI chấm thô)
* **Endpoint:** `GET /grades/submission/{submission_id}`
* **Phản hồi thành công (200 OK):**
  ```json
  {
    "id": "g90df77a-abcd-1234-5678-999988887777",
    "submission_id": "f892ccdd-1234-abcd-5678-eeeeffffbbbb",
    "proposed_score": 7.5, // Điểm AI đề xuất
    "final_score": null, // Giáo viên chưa chốt
    "is_approved": false,
    "ai_feedback": "Bài viết trôi chảy, luận điểm dũng cảm tốt. Có 1 lỗi chính tả ở dòng 3.",
    "final_feedback": null,
    "grading_details": {
      "c1": {
        "score": 4.0,
        "max_points": 5.0,
        "reason": "Mở bài và thân bài tốt nhưng kết luận chưa đọng lại nhiều ý nghĩa."
      },
      "c2": {
        "score": 3.5,
        "max_points": 5.0,
        "reason": "Viết nhầm từ 'dũng cảm' thành 'dũng cãm' ở dòng thứ 3."
      }
    }
  }
  ```

#### 2. Phê duyệt hoặc sửa điểm (Chỉ dành cho Giáo viên)
* **Endpoint:** `PUT /grades/submission/{submission_id}/approve`
* **Payload:**
  ```json
  {
    "final_score": 8.0, // Giáo viên sửa lại điểm cao hơn hoặc giữ nguyên
    "final_feedback": "Thầy đồng ý với nhận xét của AI. Bài viết rất có cảm xúc, cố gắng khắc phục lỗi chính tả nhé em!",
    "grading_details": {
      "c1": { "score": 4.5, "reason": "Thầy cộng thêm 0.5 điểm khuyến khích vì ý tưởng sáng tạo." },
      "c2": { "score": 3.5, "reason": "Giữ nguyên lỗi chính tả." }
    }
  }
  ```
* **Phản hồi thành công (200 OK):**
  ```json
  {
    "submission_id": "f892ccdd-1234-abcd-5678-eeeeffffbbbb",
    "final_score": 8.0,
    "is_approved": true,
    "approved_at": "2026-06-05T08:30:00Z"
  }
  ```
