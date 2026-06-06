const state = {
  rubric: [],
  criteriaScores: [],
};

const els = {
  assignmentFile: document.querySelector("#assignmentFile"),
  answerFile: document.querySelector("#answerFile"),
  maxScore: document.querySelector("#maxScore"),
  gradeLevel: document.querySelector("#gradeLevel"),
  generateRubricBtn: document.querySelector("#generateRubricBtn"),
  gradeBtn: document.querySelector("#gradeBtn"),
  addCriterionBtn: document.querySelector("#addCriterionBtn"),
  rubricRows: document.querySelector("#rubricRows"),
  result: document.querySelector("#result"),
  studentName: document.querySelector("#studentName"),
  finalFeedback: document.querySelector("#finalFeedback"),
  teacherNote: document.querySelector("#teacherNote"),
  approveBtn: document.querySelector("#approveBtn"),
  approvalResult: document.querySelector("#approvalResult"),
  toast: document.querySelector("#toast"),
};

function showToast(message) {
  els.toast.textContent = message;
  els.toast.hidden = false;
  window.clearTimeout(showToast.timer);
  showToast.timer = window.setTimeout(() => {
    els.toast.hidden = true;
  }, 4500);
}

async function postForm(url, formData) {
  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });
  const data = await response.json();
  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    throw new Error(detail || "Request failed");
  }
  return data;
}

async function postJson(url, body) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const data = await response.json();
  if (!response.ok) {
    const detail = typeof data.detail === "string" ? data.detail : JSON.stringify(data.detail);
    throw new Error(detail || "Request failed");
  }
  return data;
}

function requireFile(input, label) {
  if (!input.files || input.files.length === 0) {
    throw new Error(`Bạn cần chọn ${label}.`);
  }
  return input.files[0];
}

function baseForm() {
  const formData = new FormData();
  formData.append("max_score", els.maxScore.value);
  formData.append("grade_level", els.gradeLevel.value.trim());
  return formData;
}

function renderRubric() {
  els.rubricRows.innerHTML = "";
  els.rubricRows.classList.toggle("empty", state.rubric.length === 0);

  if (state.rubric.length === 0) {
    els.rubricRows.textContent = "Chưa có rubric.";
    els.gradeBtn.disabled = true;
    return;
  }

  state.rubric.forEach((item, index) => {
    const row = document.createElement("div");
    row.className = "row";
    row.innerHTML = `
      <label>Tiêu chí <input value="${escapeHtml(item.criterion)}" data-field="criterion" /></label>
      <label>Mô tả <input value="${escapeHtml(item.description)}" data-field="description" /></label>
      <label>Điểm tối đa <input type="number" min="0.25" step="0.25" value="${item.max_score}" data-field="max_score" /></label>
      <button class="remove-btn" title="Xóa tiêu chí">Xóa</button>
    `;

    row.querySelectorAll("input").forEach((input) => {
      input.addEventListener("input", () => {
        const field = input.dataset.field;
        state.rubric[index][field] = field === "max_score" ? Number(input.value) : input.value;
      });
    });

    row.querySelector(".remove-btn").addEventListener("click", () => {
      state.rubric.splice(index, 1);
      renderRubric();
    });

    els.rubricRows.appendChild(row);
  });

  els.gradeBtn.disabled = false;
}

function renderResult(data) {
  state.criteriaScores = data.criteria_scores;
  els.finalFeedback.value = data.student_feedback;
  els.approveBtn.disabled = false;

  const scores = data.criteria_scores
    .map((item, index) => `
      <div class="row score-row">
        <label>Tiêu chí <input value="${escapeHtml(item.criterion)}" readonly /></label>
        <label>Điểm <input type="number" min="0" step="0.25" value="${item.score}" data-score-index="${index}" data-field="score" /></label>
        <label>Điểm tối đa <input type="number" min="0.25" step="0.25" value="${item.max_score}" readonly /></label>
        <label>Nhận xét <input value="${escapeHtml(item.comment)}" data-score-index="${index}" data-field="comment" /></label>
      </div>
    `)
    .join("");

  els.result.classList.remove("empty");
  els.result.innerHTML = `
    <strong>Điểm nháp: ${data.draft_total_score} / ${data.max_score}</strong>
    <div class="rows">${scores}</div>
    ${listBlock("Điểm mạnh", data.strengths)}
    ${listBlock("Điểm cần cải thiện", data.weaknesses)}
    ${listBlock("Gợi ý cải thiện", data.improvement_suggestions)}
    <div class="result-block">
      <h3>Phản hồi cho học sinh</h3>
      <p>${escapeHtml(data.student_feedback)}</p>
    </div>
  `;

  els.result.querySelectorAll("input[data-score-index]").forEach((input) => {
    input.addEventListener("input", () => {
      const index = Number(input.dataset.scoreIndex);
      const field = input.dataset.field;
      state.criteriaScores[index][field] = field === "score" ? Number(input.value) : input.value;
    });
  });
}

function listBlock(title, items) {
  const list = (items || []).map((item) => `<li>${escapeHtml(item)}</li>`).join("");
  return `
    <div class="result-block">
      <h3>${title}</h3>
      <ul>${list || "<li>Không có dữ liệu.</li>"}</ul>
    </div>
  `;
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

els.generateRubricBtn.addEventListener("click", async () => {
  els.generateRubricBtn.disabled = true;
  try {
    const formData = baseForm();
    formData.append("assignment_file", requireFile(els.assignmentFile, "file đề bài"));
    const data = await postForm("/rubric/generate-upload", formData);
    state.rubric = data.draft_rubric;
    renderRubric();
    showToast("Đã tạo rubric. Bạn có thể chỉnh rubric rồi bấm Chấm bài.");
  } catch (error) {
    showToast(error.message);
  } finally {
    els.generateRubricBtn.disabled = false;
  }
});

els.addCriterionBtn.addEventListener("click", () => {
  state.rubric.push({
    criterion: "Tiêu chí mới",
    description: "Mô tả tiêu chí",
    max_score: 1,
  });
  renderRubric();
});

els.gradeBtn.addEventListener("click", async () => {
  els.gradeBtn.disabled = true;
  try {
    const formData = baseForm();
    formData.append("assignment_file", requireFile(els.assignmentFile, "file đề bài"));
    formData.append("student_answer_file", requireFile(els.answerFile, "file bài làm"));
    formData.append("approved_rubric", JSON.stringify(state.rubric));
    const data = await postForm("/grade/upload", formData);
    renderResult(data);
    showToast("Đã chấm nháp. Giáo viên có thể chỉnh điểm trước khi duyệt.");
  } catch (error) {
    showToast(error.message);
  } finally {
    els.gradeBtn.disabled = state.rubric.length === 0;
  }
});

els.approveBtn.addEventListener("click", async () => {
  els.approveBtn.disabled = true;
  try {
    const data = await postJson("/grade/approve", {
      student_name: els.studentName.value.trim(),
      assignment_question: "Đề bài lấy từ file upload",
      final_criteria_scores: state.criteriaScores,
      final_feedback: els.finalFeedback.value.trim(),
      teacher_note: els.teacherNote.value.trim() || null,
    });
    els.approvalResult.textContent = JSON.stringify(data, null, 2);
    showToast("Đã duyệt điểm cuối.");
  } catch (error) {
    showToast(error.message);
  } finally {
    els.approveBtn.disabled = state.criteriaScores.length === 0;
  }
});

renderRubric();
