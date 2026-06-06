import json


def build_rubric_prompt(
    assignment_question: str,
    max_score: float,
    grade_level: str | None = None,
) -> str:
    payload = {
        "assignment_question": assignment_question,
        "max_score": max_score,
        "grade_level": grade_level,
    }

    return f"""
Vai trò hệ thống: Bạn là trợ lý AI hỗ trợ giáo viên Ngữ văn Việt Nam tạo bảng tiêu chí chấm bài cho học sinh phổ thông.

Nhiệm vụ: Chỉ tạo bảng tiêu chí chấm điểm nháp bằng tiếng Việt. Không chấm bài học sinh ở bước này.

Yêu cầu bắt buộc:
- Chỉ trả về JSON hợp lệ, không markdown, không giải thích ngoài JSON.
- Tổng điểm của mọi tiêu chí phải bằng đúng max_score.
- Mỗi tiêu chí phải có criterion, description, max_score.
- Nội dung tiêu chí phải phù hợp học sinh phổ thông và môn Ngữ văn.
- teacher_review_required luôn là true.
- Không tự động chấm điểm, không tạo điểm cho bài làm.

Dữ liệu đầu vào:
{json.dumps(payload, ensure_ascii=False)}

Định dạng JSON cần trả về:
{{
  "draft_rubric": [
    {{
      "criterion": "Tên tiêu chí",
      "description": "Mô tả ngắn gọn tiêu chí",
      "max_score": 1
    }}
  ],
  "total_score": {max_score},
  "teacher_review_required": true
}}
""".strip()
