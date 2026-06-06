# Vietnamese Literature Grading Backend

FastAPI backend chấm nháp bài văn cho học sinh phổ thông bằng Gemini API. AI chỉ tạo rubric nháp hoặc điểm nháp; giáo viên luôn là người duyệt cuối cùng.

## Setup

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Tạo hoặc sửa `.env`:

```env
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-2.5-flash
```

## Endpoints

### `GET /`

```json
{
  "status": "ok",
  "message": "Grading backend is running"
}
```

## Data text files

Nếu không muốn nhập đề bài và bài làm trực tiếp trong JSON, đặt file `.txt` vào thư mục `data/`.

Ví dụ có sẵn:

```text
data/de_bai.txt
data/bai_lam_hoc_sinh.txt
```

Backend chỉ đọc file `.txt` trong thư mục `data/`.

### `POST /rubric/generate`

Request:

```json
{
  "assignment_question": "Phân tích hình tượng người lính trong bài thơ Đồng chí của Chính Hữu.",
  "max_score": 10,
  "grade_level": "Lớp 9"
}
```

Response:

```json
{
  "draft_rubric": [
    {
      "criterion": "Hiểu nội dung tác phẩm",
      "description": "Nêu đúng hoàn cảnh, chủ đề và hình tượng người lính trong bài thơ.",
      "max_score": 3
    }
  ],
  "total_score": 10,
  "teacher_review_required": true
}
```

### `POST /rubric/generate-from-files`

Request:

```json
{
  "assignment_file": "de_bai.txt",
  "max_score": 10,
  "grade_level": "Lớp 8"
}
```

Endpoint này đọc nội dung đề bài từ `data/de_bai.txt`, sau đó tạo rubric nháp. AI vẫn chưa chấm bài ở bước này.

### `POST /grade`

Request:

```json
{
  "assignment_question": "Phân tích hình tượng người lính trong bài thơ Đồng chí của Chính Hữu.",
  "student_answer_text": "Bài thơ Đồng chí thể hiện vẻ đẹp giản dị, chân thành của người lính trong kháng chiến...",
  "approved_rubric": [
    {
      "criterion": "Hiểu nội dung tác phẩm",
      "description": "Nêu đúng hoàn cảnh, chủ đề và hình tượng người lính trong bài thơ.",
      "max_score": 3
    },
    {
      "criterion": "Phân tích nghệ thuật",
      "description": "Phân tích được hình ảnh, ngôn ngữ, giọng điệu và biện pháp nghệ thuật.",
      "max_score": 3
    },
    {
      "criterion": "Lập luận và dẫn chứng",
      "description": "Bố cục rõ, lập luận mạch lạc, dẫn chứng phù hợp.",
      "max_score": 2
    },
    {
      "criterion": "Diễn đạt và chính tả",
      "description": "Diễn đạt trong sáng, ít lỗi dùng từ, ngữ pháp, chính tả.",
      "max_score": 2
    }
  ],
  "max_score": 10,
  "grade_level": "Lớp 9"
}
```

Response:

```json
{
  "draft_total_score": 7.5,
  "max_score": 10,
  "criteria_scores": [
    {
      "criterion": "Hiểu nội dung tác phẩm",
      "score": 2.5,
      "max_score": 3,
      "comment": "Bài làm nêu được vẻ đẹp giản dị và tình đồng đội của người lính."
    }
  ],
  "strengths": ["Có nhận xét đúng về chủ đề tình đồng chí."],
  "weaknesses": ["Phân tích nghệ thuật còn ngắn."],
  "improvement_suggestions": ["Bổ sung dẫn chứng thơ cụ thể hơn."],
  "student_feedback": "Em đã nắm được ý chính của tác phẩm. Hãy thêm dẫn chứng và phân tích sâu hơn để bài viết thuyết phục hơn.",
  "confidence": "medium",
  "teacher_review_required": true,
  "raw_model_output": {}
}
```

### `POST /grade/from-files`

Request:

```json
{
  "assignment_file": "de_bai.txt",
  "student_answer_file": "bai_lam_hoc_sinh.txt",
  "approved_rubric": [
    {
      "criterion": "Hiểu nội dung tác phẩm",
      "description": "Nêu đúng nhân vật, hoàn cảnh và phẩm chất của Lão Hạc.",
      "max_score": 4
    },
    {
      "criterion": "Phân tích và cảm nhận",
      "description": "Có nhận xét, phân tích về tình yêu thương con, lòng tự trọng và bi kịch của nhân vật.",
      "max_score": 3
    },
    {
      "criterion": "Dẫn chứng và lập luận",
      "description": "Dẫn chứng phù hợp, lập luận rõ ràng.",
      "max_score": 2
    },
    {
      "criterion": "Diễn đạt",
      "description": "Diễn đạt mạch lạc, ít lỗi chính tả và ngữ pháp.",
      "max_score": 1
    }
  ],
  "max_score": 10,
  "grade_level": "Lớp 8"
}
```

Endpoint này đọc đề bài từ `data/de_bai.txt`, đọc bài làm từ `data/bai_lam_hoc_sinh.txt`, rồi chấm nháp theo rubric giáo viên đã duyệt.

### `POST /grade/approve`

Request:

```json
{
  "student_name": "Nguyễn Văn A",
  "assignment_question": "Phân tích hình tượng người lính trong bài thơ Đồng chí của Chính Hữu.",
  "final_criteria_scores": [
    {
      "criterion": "Hiểu nội dung tác phẩm",
      "score": 2.5,
      "max_score": 3,
      "comment": "Nắm được ý chính và có nhận xét phù hợp."
    },
    {
      "criterion": "Phân tích nghệ thuật",
      "score": 2,
      "max_score": 3,
      "comment": "Có phân tích nhưng cần thêm dẫn chứng."
    }
  ],
  "final_feedback": "Bài làm có nền tảng tốt, cần phát triển dẫn chứng và phân tích nghệ thuật rõ hơn.",
  "teacher_note": "Đã chỉnh điểm theo nhận xét của giáo viên."
}
```

Response:

```json
{
  "student_name": "Nguyễn Văn A",
  "final_total_score": 4.5,
  "status": "approved",
  "final_criteria_scores": [],
  "final_feedback": "Bài làm có nền tảng tốt, cần phát triển dẫn chứng và phân tích nghệ thuật rõ hơn.",
  "teacher_note": "Đã chỉnh điểm theo nhận xét của giáo viên."
}
```
