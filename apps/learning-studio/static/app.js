const STORAGE_KEY = "learning-studio-draft-v2";
const SESSION_ID = "learning-studio-g2-session";

const state = {
  lesson: null,
  catalog: null,
  surface: "session",
  selectedConcept: null,
  overlay: { title: "Exploration draft", concept_ids: [], package_version: null },
  studyTraces: [],
  routeProposals: [],
  phaseIndex: 0,
  answer: "",
  selectedOption: null,
  hintsUsed: 0,
  feedback: null,
  evidence: [],
  events: [],
  reviewScheduled: false,
};

const phaseLabels = {
  diagnose: "DIAGNOSE",
  teach: "TEACH",
  practice: "PRACTICE",
  verify: "VERIFY",
  review: "REVIEW",
};

const $ = (id) => document.getElementById(id);

function save() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify({
    answer: state.answer,
    selectedOption: state.selectedOption,
  }));
}

function restore() {
  try {
    const saved = JSON.parse(localStorage.getItem(STORAGE_KEY) || "null");
    if (!saved) return;
    Object.assign(state, saved);
  } catch {
    localStorage.removeItem(STORAGE_KEY);
  }
}

function applySession(snapshot) {
  const sessionState = snapshot.state || {};
  state.phaseIndex = sessionState.phase_index || 0;
  state.evidence = sessionState.evidence || [];
  state.hintsUsed = sessionState.hints_used || 0;
  state.reviewScheduled = Boolean(sessionState.review_scheduled);
  state.events = snapshot.events || [];
  state.overlay = sessionState.overlay || state.overlay;
  state.studyTraces = sessionState.study_traces || [];
  state.routeProposals = sessionState.route_proposals || [];
}

async function recordEvent(type, phase, data = {}) {
  try {
    const provenance = { actor: "learner-ui", package_version: state.lesson?.package_version };
    if (data.observation?.evaluator) provenance.evaluator = data.observation.evaluator;
    const response = await fetch("/api/events", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        session_id: SESSION_ID,
        type,
        phase,
        data,
        provenance,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || payload.error || "Event rejected");
    applySession(payload);
    if (["diagnostic.submitted", "activity.completed", "code.verified", "review.completed"].includes(type)) {
      state.answer = "";
      state.selectedOption = null;
    }
    save();
    return true;
  } catch {
    setFeedback("warning", "The session server could not record this action. Check that the local server is running, then try again.");
    return false;
  }
}

async function gradeActivity(mode, activityId, input = {}) {
  try {
    const response = await fetch("/api/grade", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        mode,
        activity_id: activityId,
        package_version: state.lesson?.package_version,
        ...input,
      }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || payload.error || "Grader rejected the activity");
    return payload.observation;
  } catch {
    setFeedback("warning", "The deterministic grader could not evaluate this response. Check that the local server is running, then try again.");
    return null;
  }
}

async function recordStudyTrace(type, data = {}) {
  return recordEvent(type, state.lesson.phases[state.phaseIndex], data);
}

function renderSkills() {
  $("skill-list").innerHTML = state.lesson.skills.map((skill) => `
    <div class="skill-row">
      <div class="skill-name"><span>${skill.label}</span><strong>${Math.round(skill.progress * 100)}%</strong></div>
      <div class="mini-track"><div class="mini-fill" style="width:${Math.round(skill.progress * 100)}%"></div></div>
    </div>
  `).join("");
}

function renderEvidence() {
  $("evidence-count").textContent = `${state.evidence.length} event${state.evidence.length === 1 ? "" : "s"}`;
  $("review-status").textContent = state.reviewScheduled ? "Due in 2 days" : "Not scheduled";
  const list = $("evidence-list");
  if (!state.evidence.length) {
    list.innerHTML = `<div class="empty-state">No evidence yet. The diagnostic will establish a baseline.</div>`;
  } else {
    list.innerHTML = state.evidence.map((item) => `
      <div class="evidence-item ${item.kind}">
        <strong>${item.title}</strong>
        <span>${item.detail}</span>
      </div>
    `).join("");
  }
}

function clusterName(clusterId) {
  return state.catalog?.clusters.find((cluster) => cluster.id === clusterId)?.name || "PyTorch foundations";
}

function visibleConcepts() {
  const search = ($("knowledge-search")?.value || "").trim().toLowerCase();
  const cluster = $("cluster-filter")?.value || "all";
  return state.catalog.concepts.filter((concept) => {
    const matchesSearch = !search || [concept.name, concept.summary, concept.plain, concept.misconception]
      .join(" ").toLowerCase().includes(search);
    return matchesSearch && (cluster === "all" || concept.cluster_id === cluster);
  });
}

function renderConceptGrid() {
  const concepts = visibleConcepts();
  $("knowledge-result-label").textContent = `${concepts.length} concept${concepts.length === 1 ? "" : "s"}`;
  $("concept-empty").hidden = concepts.length > 0;
  $("concept-grid").innerHTML = concepts.map((concept) => `
    <button class="concept-tile ${state.selectedConcept === concept.id ? "selected" : ""}" data-concept-id="${concept.id}">
      <span class="tile-cluster">${clusterName(concept.cluster_id)}</span>
      <strong>${concept.name}</strong>
      <span>${concept.summary}</span>
      <small>${concept.practice_refs.length} practice item${concept.practice_refs.length === 1 ? "" : "s"} · ${concept.related_ids.length} links</small>
    </button>
  `).join("");
}

function renderConceptDetail() {
  const concept = state.catalog.concepts.find((item) => item.id === state.selectedConcept);
  $("concept-detail-empty").hidden = Boolean(concept);
  $("concept-detail-content").hidden = !concept;
  if (!concept) return;
  $("detail-cluster").textContent = clusterName(concept.cluster_id);
  $("detail-type").textContent = concept.type;
  $("detail-title").textContent = concept.name;
  $("detail-summary").textContent = concept.summary;
  $("detail-plain").textContent = concept.plain;
  $("detail-precise").textContent = concept.precise;
  $("detail-example").textContent = concept.examples[0] || "No example recorded yet.";
  $("detail-counterexample").textContent = concept.counterexamples[0] || "No near miss recorded yet.";
  $("detail-misconception").textContent = concept.misconception;
  $("detail-related").innerHTML = concept.related_ids.map((id) => {
    const related = state.catalog.concepts.find((item) => item.id === id);
    return related ? `<button class="related-link" data-related-id="${related.id}">${related.name}</button>` : "";
  }).join("");
  $("flashcard-box").hidden = true;
  $("flashcard-reveal").hidden = true;
  $("flashcard-reveal").textContent = "";
  const saved = state.overlay.concept_ids.includes(concept.id);
  $("add-overlay").textContent = saved ? "Saved to exploration" : "Add to exploration";
  $("add-overlay").disabled = saved;
  const options = [
    {label: `Practice ${concept.name}`, action: "practice"},
    ...(concept.related_ids.slice(0, 1).map((id) => ({
      label: `Open ${state.catalog.concepts.find((item) => item.id === id)?.name || "related concept"}`,
      action: `related:${id}`,
    }))),
  ];
  $("route-options").innerHTML = `<div class="eyebrow">NEXT OPTIONS</div><div class="route-option-list">${options.map((option) => `<button class="route-option" data-route-action="${option.action}">${option.label}<span>→</span></button>`).join("")}</div>`;
}

function renderKnowledge() {
  if (!state.catalog) return;
  const filter = $("cluster-filter");
  if (filter && filter.options.length === 1) {
    filter.insertAdjacentHTML("beforeend", state.catalog.clusters.map((cluster) => `<option value="${cluster.id}">${cluster.name}</option>`).join(""));
  }
  renderConceptGrid();
  renderConceptDetail();
  $("study-trace-count").textContent = `${state.studyTraces.length} study action${state.studyTraces.length === 1 ? "" : "s"}`;
  bindKnowledge();
}

function renderReviewSurface() {
  $("review-evidence-count").textContent = `${state.evidence.length} event${state.evidence.length === 1 ? "" : "s"}`;
  $("review-study-count").textContent = `${state.studyTraces.length} action${state.studyTraces.length === 1 ? "" : "s"}`;
  $("review-next-status").textContent = state.reviewScheduled ? "Due in 2 days" : "Not scheduled";
}

async function selectConcept(conceptId, record = true) {
  state.selectedConcept = conceptId;
  renderKnowledge();
  if (record && await recordStudyTrace("concept.viewed", {concept_id: conceptId, trace_kind: "exposure"})) renderKnowledge();
}

async function saveConceptToOverlay() {
  const concept = state.catalog.concepts.find((item) => item.id === state.selectedConcept);
  if (!concept || state.overlay.concept_ids.includes(concept.id)) return;
  const overlay = {
    title: state.overlay.title || "Exploration draft",
    concept_ids: [...state.overlay.concept_ids, concept.id],
    package_version: state.lesson.package_version,
  };
  if (await recordStudyTrace("overlay.updated", { overlay })) {
    state.overlay = overlay;
    renderKnowledge();
  }
}

async function proposeRoute(action) {
  const concept = state.catalog.concepts.find((item) => item.id === state.selectedConcept);
  if (!concept) return;
  const proposal = {
    concept_id: concept.id,
    route_kind: action === "practice" ? "practice" : "related-concept",
    rationale: action === "practice" ? "The package has a practice item for this concept." : "The selected concept has a typed graph link to this neighboring concept.",
    options: [
      {type: "practice", refs: concept.practice_refs},
      {type: "related", refs: concept.related_ids.slice(0, 2)},
    ],
    package_version: state.lesson.package_version,
  };
  await recordStudyTrace("route.proposed", proposal);
  if (action === "practice") {
    setFeedback("success", `Added a practice route for ${concept.name}. The interactive session remains the place where this attempt becomes evidence.`);
    showSurface("session");
  } else {
    await selectConcept(action.slice("related:".length));
  }
}

function bindKnowledge() {
  if (!state.catalog) return;
  $("knowledge-search").oninput = () => renderKnowledge();
  $("cluster-filter").onchange = () => renderKnowledge();
  $("clear-knowledge").onclick = () => {
    $("knowledge-search").value = "";
    $("cluster-filter").value = "all";
    renderKnowledge();
  };
  document.querySelectorAll("[data-concept-id]").forEach((button) => {
    button.onclick = () => selectConcept(button.dataset.conceptId);
  });
  document.querySelectorAll("[data-related-id]").forEach((button) => {
    button.onclick = () => selectConcept(button.dataset.relatedId);
  });
  $("start-recall").onclick = () => { $("flashcard-box").hidden = false; $("reveal-card").focus(); };
  $("reveal-card").onclick = async () => {
    const concept = state.catalog.concepts.find((item) => item.id === state.selectedConcept);
    if (!concept) return;
    $("flashcard-reveal").textContent = `${concept.plain} ${concept.precise}`;
    $("flashcard-reveal").hidden = false;
    await recordStudyTrace("flashcard.attempted", {concept_id: concept.id, trace_kind: "retrieval_practice", revealed: true});
    renderKnowledge();
    $("flashcard-box").hidden = false;
    $("flashcard-reveal").hidden = false;
    $("flashcard-reveal").textContent = `${concept.plain} ${concept.precise}`;
  };
  $("practice-concept").onclick = () => proposeRoute("practice");
  $("add-overlay").onclick = saveConceptToOverlay;
  document.querySelectorAll("[data-route-action]").forEach((button) => {
    button.onclick = () => proposeRoute(button.dataset.routeAction);
  });
}

function showSurface(surface) {
  state.surface = surface;
  document.querySelectorAll(".surface").forEach((element) => {
    element.hidden = element.id !== `${surface}-surface`;
  });
  document.querySelectorAll("[data-surface]").forEach((button) => {
    button.classList.toggle("active", button.dataset.surface === surface);
  });
  if (surface === "knowledge") {
    renderKnowledge();
  } else if (surface === "review") {
    renderReviewSurface();
  } else {
    renderSession();
  }
}

function bindSurfaceNavigation() {
  document.querySelectorAll("[data-surface]").forEach((button) => {
    button.addEventListener("click", () => showSurface(button.dataset.surface));
  });
}

function setFeedback(kind, text) {
  state.feedback = { kind, text };
  save();
}

function feedbackHtml() {
  return state.feedback ? `<div class="feedback ${state.feedback.kind}">${state.feedback.text}</div>` : "";
}

function renderDiagnose() {
  const d = state.lesson.diagnostic;
  return `
    <div class="activity-topline"><div><div class="activity-kicker">Baseline check · 4 minutes</div><h2 class="activity-title">Show what you already understand</h2></div><div class="eyebrow">1 / 5</div></div>
    <p class="activity-copy">Before explaining anything, the tutor wants to see your current mental model. A partial answer is useful evidence too.</p>
    <div class="callout"><strong>Question</strong>${d.prompt}</div>
    <div class="answer-area"><textarea id="answer-box" placeholder="Write your best explanation, or say what feels uncertain."></textarea></div>
    ${state.hintsUsed ? `<div class="feedback warning"><strong>Hint used:</strong> ${d.hint}</div>` : ""}
    ${feedbackHtml()}
    <div class="button-row"><button class="hint-button" id="hint-button">Need a hint</button><button class="primary-button" id="submit-diagnose">Submit baseline</button></div>
  `;
}

function renderTeach() {
  return `
    <div class="activity-topline"><div><div class="activity-kicker">Targeted explanation · 5 minutes</div><h2 class="activity-title">Gradients accumulate by default</h2></div><div class="eyebrow">2 / 5</div></div>
    <p class="activity-copy">PyTorch adds new gradients to the existing <code>.grad</code> values on parameters. A normal training loop clears those values before computing the next batch's gradients.</p>
    <div class="callout"><strong>Core idea</strong><code>optimizer.zero_grad()</code> is not a cosmetic reset. It prevents the next update from mixing evidence from the current batch with gradients left over from earlier batches.</div>
    <div class="code-block">optimizer.zero_grad()\nlogits = model(X)\nloss = loss_fn(logits, y)\nloss.backward()\noptimizer.step()</div>
    <p class="activity-copy">The next activity asks you to recognize this pattern inside a real loop. You will get a test result, not just a model-generated opinion.</p>
    ${feedbackHtml()}
    <div class="button-row"><button class="primary-button" id="continue-teach">Try the repair task</button></div>
  `;
}

function renderPractice() {
  const p = state.lesson.practice;
  const letters = ["A", "B", "C", "D"];
  return `
    <div class="activity-topline"><div><div class="activity-kicker">Runnable reasoning · 8 minutes</div><h2 class="activity-title">Repair the missing training step</h2></div><div class="eyebrow">3 / 5</div></div>
    <p class="activity-copy">The code below runs forward and backward, but one training step is missing. Choose the line and place it before the forward pass.</p>
    <div class="code-block">${p.code}</div>
    <div class="option-list">${p.options.map((option, index) => `
      <button class="option ${state.selectedOption === index ? "selected" : ""}" data-option="${index}"><span class="option-mark">${letters[index]}</span><span>${option}</span></button>
    `).join("")}</div>
    ${feedbackHtml()}
    <div class="button-row"><button class="primary-button" id="submit-practice">Run verification</button></div>
  `;
}

function renderVerify() {
  return `
    <div class="activity-topline"><div><div class="activity-kicker">Ground-truth check · completed</div><h2 class="activity-title">The repair passed the test</h2></div><div class="eyebrow">4 / 5</div></div>
    <p class="activity-copy">The simulated runner checked the training loop contract. The missing reset was placed before the forward pass, so each update uses the current batch's gradients.</p>
    <div class="result-grid"><div class="result-box"><div class="eyebrow">Test result</div><strong>4 / 4 passed</strong></div><div class="result-box"><div class="eyebrow">Evidence</div><strong>Procedural success</strong></div><div class="result-box"><div class="eyebrow">Hints</div><strong>${state.hintsUsed} used</strong></div></div>
    <div class="callout"><strong>What this does not prove</strong>Passing one repair task does not yet prove independent mastery. The final review changes the wording and asks you to predict the failure mode.</div>
    ${feedbackHtml()}
    <div class="button-row"><button class="primary-button" id="continue-verify">Take the transfer review</button></div>
  `;
}

function renderReview() {
  const r = state.lesson.review;
  return `
    <div class="activity-topline"><div><div class="activity-kicker">Transfer review · 4 minutes</div><h2 class="activity-title">Explain the failure mode</h2></div><div class="eyebrow">5 / 5</div></div>
    <p class="activity-copy">This is a new prompt with the same underlying skill. Use your own words; a correct phrase without the mechanism is only partial evidence.</p>
    <div class="callout"><strong>Review question</strong>${r.prompt}</div>
    <div class="answer-area"><textarea id="review-box" placeholder="Explain what happens and why."></textarea></div>
    ${state.hintsUsed > 1 ? `<div class="feedback warning"><strong>Hint used:</strong> ${r.hint}</div>` : ""}
    ${feedbackHtml()}
    <div class="button-row"><button class="hint-button" id="review-hint">Need a hint</button><button class="primary-button" id="submit-review">Finish session</button></div>
  `;
}

function bindActivity() {
  const phase = state.lesson.phases[state.phaseIndex];
  if (phase === "diagnose") {
    const box = $("answer-box");
    box.value = state.answer;
    box.addEventListener("input", (e) => { state.answer = e.target.value; save(); });
    $("hint-button").addEventListener("click", async () => { if (await recordEvent("hint.used", phase, { hint: "gradient_accumulation" })) render(); });
    $("submit-diagnose").addEventListener("click", async () => {
      const answer = state.answer.trim();
      if (!answer) { setFeedback("warning", "Write a partial model or state what feels uncertain so the tutor has something to diagnose."); render(); return; }
      const observation = await gradeActivity("open_response", "diagnostic.gradient-accumulation.baseline", { response: answer });
      if (!observation) { render(); return; }
      if (await recordEvent("diagnostic.submitted", phase, { activity_id: "diagnostic.gradient-accumulation.baseline", answer, diagnosis: observation.label, observation })) render();
    });
  }
  if (phase === "teach") {
    $("continue-teach").addEventListener("click", async () => { if (await recordEvent("activity.completed", phase, { concept: "gradient_accumulation" })) render(); });
  }
  if (phase === "practice") {
    document.querySelectorAll("[data-option]").forEach((button) => button.addEventListener("click", () => { state.selectedOption = Number(button.dataset.option); save(); render(); }));
    $("submit-practice").addEventListener("click", async () => {
      if (state.selectedOption === null) { setFeedback("warning", "Choose the missing line before running verification."); render(); return; }
      const observation = await gradeActivity("choice", "practice.gradient-accumulation.repair", { selected_index: state.selectedOption });
      if (!observation) { render(); return; }
      if (observation.result !== "pass") {
        setFeedback("warning", observation.failure_type === "execution_slip" ? "Choose one of the listed operations before running verification." : "The deterministic check found a procedural mismatch. Ask which operation resets accumulated gradients, then try again.");
        await recordEvent("practice.failed", phase, { activity_id: "practice.gradient-accumulation.repair", selected: state.selectedOption, observation });
        render();
        return;
      }
      if (await recordEvent("code.verified", phase, { activity_id: "practice.gradient-accumulation.repair", selected: state.selectedOption, tests_passed: 4, tests_total: 4, observation })) render();
    });
  }
  if (phase === "verify") {
    $("continue-verify").addEventListener("click", async () => { if (await recordEvent("activity.completed", phase, { evidence: "procedural_success" })) render(); });
  }
  if (phase === "review") {
    const box = $("review-box");
    box.value = state.answer;
    box.addEventListener("input", (e) => { state.answer = e.target.value; save(); });
    $("review-hint").addEventListener("click", async () => { if (await recordEvent("hint.used", phase, { hint: "gradient_accumulation" })) render(); });
    $("submit-review").addEventListener("click", async () => {
      const answer = state.answer.trim();
      if (!answer) { setFeedback("warning", "Write your prediction before finishing the review."); render(); return; }
      const observation = await gradeActivity("open_response", "review.gradient-accumulation.transfer", { response: answer });
      if (!observation) { render(); return; }
      if (observation.result !== "pass") {
        setFeedback("warning", observation.failure_type === "transfer_failure" ? "Your answer names a related control but needs the mechanism that carries between batches." : "The grader abstained: describe what happens to .grad between batches.");
        await recordEvent("review.completed", phase, { activity_id: "review.gradient-accumulation.transfer", answer, result: "failed", observation });
        render();
        return;
      }
      if (await recordEvent("review.completed", phase, { activity_id: "review.gradient-accumulation.transfer", answer, result: "passed", next_review: "P2D", observation })) {
        setFeedback("success", "Session complete. The skill is now scheduled for a two-day review with a fresh variant.");
        render();
      }
    });
  }
}

function renderSession() {
  const phase = state.lesson.phases[state.phaseIndex];
  $("phase-label").textContent = phaseLabels[phase];
  $("progress-text").textContent = `${Math.min(state.phaseIndex + 1, state.lesson.phases.length)} / ${state.lesson.phases.length}`;
  $("session-progress").style.width = `${((state.phaseIndex + 1) / state.lesson.phases.length) * 100}%`;
  $("activity-card").innerHTML = phase === "diagnose" ? renderDiagnose() : phase === "teach" ? renderTeach() : phase === "practice" ? renderPractice() : phase === "verify" ? renderVerify() : renderReview();
  $("next-action").textContent = state.reviewScheduled ? "Return in two days for a fresh transfer item." : phase === "review" ? "Complete the transfer review to schedule the next check." : "Answer the current activity; the next step is gated by evidence.";
  renderEvidence();
  bindActivity();
}

function render() {
  if (state.surface === "knowledge") {
    renderKnowledge();
  } else if (state.surface === "review") {
    renderReviewSurface();
  } else {
    renderSession();
  }
}

async function boot() {
  const response = await fetch("/api/lesson");
  state.lesson = await response.json();
  const knowledgeResponse = await fetch("/api/knowledge");
  state.catalog = await knowledgeResponse.json();
  restore();
  $("lesson-title").textContent = state.lesson.title;
  $("lesson-objective").textContent = state.lesson.objective;
  renderSkills();
  const sessionResponse = await fetch(`/api/session?session_id=${encodeURIComponent(SESSION_ID)}`);
  const session = await sessionResponse.json();
  applySession(session);
  if (!session.exists) {
    await recordEvent("session.started", state.lesson.phases[0], { lesson_id: state.lesson.id });
  }
  bindSurfaceNavigation();
  render();
  $("reset-session").addEventListener("click", () => { localStorage.removeItem(STORAGE_KEY); window.location.reload(); });
}

boot().catch((error) => {
  document.body.innerHTML = `<main style="font-family:system-ui;padding:40px"><h1>Learning Studio could not start</h1><p>${error.message}</p></main>`;
});
