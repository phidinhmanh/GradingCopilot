import json

from app.schemas.rubric_schema import RubricCriterion


def build_grading_prompt(
    assignment_question: str,
    student_answer_text: str,
    approved_rubric: list[RubricCriterion],
    max_score: float,
    grade_level: str | None = None,
) -> str:
    payload = {
        "assignment_question": assignment_question,
        "student_answer_text": student_answer_text,
        "approved_rubric": [item.model_dump() for item in approved_rubric],
        "max_score": max_score,
        "grade_level": grade_level,
    }

    return f"""
Vai trò hệ thống: Bạn là trợ lý AI chấm nháp bài văn cho giáo viên Ngữ văn Việt Nam.

Nhiệm vụ: Chấm bài làm của học sinh chỉ dựa trên approved_rubric đã được giáo viên duyệt.

Yêu cầu bắt buộc:
- Chỉ trả về JSON hợp lệ, không markdown, không giải thích ngoài JSON.
- Ngôn ngữ phản hồi là tiếng Việt.
- Đây chỉ là điểm nháp để giáo viên xem xét; không được nói đây là điểm cuối cùng.
- Không dùng rubric ẩn, rubric mặc định, hoặc tiêu chí ngoài approved_rubric.
- Không bịa chi tiết không có trong bài làm của học sinh.
- Cho điểm theo từng tiêu chí, kèm nhận xét ngắn gọn.
- Điểm của từng tiêu chí không được vượt quá max_score của tiêu chí đó.
- Feedback phải mang tính khích lệ, phù hợp học sinh phổ thông.
- teacher_review_required luôn là true.

Dữ liệu đầu vào:
{json.dumps(payload, ensure_ascii=False)}

Định dạng JSON cần trả về:
{{
  "draft_total_score": 0,
  "max_score": {max_score},
  "criteria_scores": [
    {{
      "criterion": "Tên tiêu chí đúng như rubric",
      "score": 0,
      "max_score": 1,
      "comment": "Nhận xét ngắn gọn theo tiêu chí"
    }}
  ],
  "strengths": ["Điểm mạnh cụ thể trong bài làm"],
  "weaknesses": ["Điểm cần cải thiện cụ thể trong bài làm"],
  "improvement_suggestions": ["Gợi ý cải thiện cụ thể, khả thi"],
  "student_feedback": "Phản hồi ngắn gọn, khích lệ, phù hợp học sinh phổ thông.",
  "confidence": "medium",
  "teacher_review_required": true
}}
""".strip()
