"use strict";

const TASKS = {
  qa: {
    label: "Ask a question", blurb: "Quick, accurate answers",
    hint: "Ask anything from any subject. You get a short answer first, then the reasoning.",
    placeholder: "Which is the largest ocean?", button: "Get answer",
    examples: ["Which is the largest ocean?", "Why is the sky blue?", "What causes inflation?"],
    request: (v) => post("/qa", { question: v }),
    render: (d) => markdown(d.answer),
  },
  explain: {
    label: "Explain a concept", blurb: "Simple, beginner-friendly",
    hint: "Enter a concept and get an explanation written for a school student.",
    placeholder: "Photosynthesis", button: "Explain it",
    examples: ["Photosynthesis", "Gravity", "Fractions", "The water cycle"],
    request: (v) => post("/explain", { topic: v }),
    render: (d) => `<p class="meta">Explained by ${esc(d.engine)}</p>` + markdown(d.explanation),
    wait: "The first explanation can take a few minutes while the local model downloads.",
  },
  quiz: {
    label: "Generate a quiz", blurb: "3 multiple-choice questions",
    hint: "Enter a topic or paste a passage. Pick your answers and get instant feedback.",
    placeholder: "The Pythagoras Theorem", button: "Generate quiz",
    examples: ["The Pythagoras Theorem", "World War II", "Basic Python loops"],
    request: (v) => post("/quiz", { text: v }),
    render: renderQuiz,
  },
  summary: {
    label: "Summarize text", blurb: "Shorten long passages",
    hint: "Paste a long passage and get the key points for quick revision.",
    placeholder: "Paste the passage you want summarized here...", button: "Summarize",
    examples: [],
    request: (v) => post("/summarize", { text: v }),
    render: (d) => markdown(d.summary),
  },
  path: {
    label: "Learning path", blurb: "Beginner to advanced plan",
    hint: "Enter a subject and get a staged plan with timelines and resources.",
    placeholder: "SQL", button: "Build my path",
    examples: ["SQL", "Machine learning", "Organic chemistry", "Public speaking"],
    request: (v) => get("/learn/recommendations?topic=" + encodeURIComponent(v)),
    render: (d) => markdown(d.recommendation),
  },
};

const $ = (id) => document.getElementById(id);
const els = {
  list: $("task-list"), form: $("task-form"), title: $("task-title"), hint: $("task-hint"),
  input: $("user-input"), label: $("input-label"), examples: $("examples"),
  submit: $("submit-btn"), result: $("result"),
};
let current = "qa";
let running = false;

/* ---------- helpers ---------- */
function esc(s) {
  return String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

async function request(url, options) {
  let res;
  try {
    res = await fetch(url, options);
  } catch (e) {
    throw new Error("Could not reach the EduGenie server. Is it still running?");
  }
  let data = {};
  try { data = await res.json(); } catch (e) { /* non-JSON error page */ }
  if (!res.ok) throw new Error(data.error || `Request failed (HTTP ${res.status}).`);
  return data;
}
const post = (url, body) => request(url, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
const get = (url) => request(url);

/* Tiny, safe Markdown renderer: headings, bullets (nested by indent), numbered lists, **bold**, *italic*, `code`. */
function inline(s) {
  return esc(s)
    .replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>")
    .replace(/(^|[\s(])\*(?!\s)([^*]+?)\*(?=[\s).,;:!?]|$)/g, "$1<em>$2</em>");
}
function markdown(text) {
  const out = [];
  let inList = false;
  const closeList = () => { if (inList) { out.push("</ul>"); inList = false; } };
  for (const raw of String(text).replace(/\r/g, "").split("\n")) {
    const line = raw.replace(/\s+$/, "");
    if (!line.trim()) { closeList(); continue; }
    const heading = line.match(/^\s*(#{1,4})\s+(.*)$/);
    const bullet = line.match(/^(\s*)(?:[*\-+]|\d+[.)])\s+(.*)$/);
    if (heading) {
      closeList();
      out.push(`<h3>${inline(heading[2])}</h3>`);
    } else if (bullet) {
      if (!inList) { out.push("<ul>"); inList = true; }
      const level = Math.min(2, Math.floor(bullet[1].replace(/\t/g, "    ").length / 4));
      out.push(`<li class="lvl${level}">${inline(bullet[2])}</li>`);
    } else if (/^\s*\*\*[^*]+\*\*:?\s*$/.test(line) || /^\s*\*\*[IVX]+\./.test(line)) {
      closeList();
      out.push(`<h3>${inline(line.trim())}</h3>`);
    } else {
      closeList();
      out.push(`<p>${inline(line.trim())}</p>`);
    }
  }
  closeList();
  return out.join("");
}

/* ---------- quiz rendering ---------- */
function renderQuiz(data) {
  const box = document.createElement("div");
  let answered = 0, score = 0;
  const total = data.quiz.length;
  const scoreEl = document.createElement("p");
  scoreEl.className = "score";
  scoreEl.hidden = true;

  data.quiz.forEach((item, i) => {
    const q = document.createElement("div");
    q.className = "q";
    q.innerHTML = `<h4>${i + 1}. ${esc(item.question)}</h4>`;
    const opts = document.createElement("div");
    opts.className = "opts";
    const feedback = document.createElement("p");
    feedback.className = "feedback";

    item.options.forEach((option) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "opt";
      btn.textContent = option;
      btn.addEventListener("click", () => {
        const buttons = opts.querySelectorAll(".opt");
        buttons.forEach((b) => { b.disabled = true; if (b.textContent === item.answer) b.classList.add("correct"); });
        if (option === item.answer) {
          score++;
          feedback.textContent = "Correct!";
          feedback.classList.add("good");
        } else {
          btn.classList.add("wrong");
          feedback.textContent = `Not quite. The correct answer is: ${item.answer}`;
          feedback.classList.add("bad");
        }
        answered++;
        if (answered === total) { scoreEl.textContent = `You scored ${score} out of ${total}.`; scoreEl.hidden = false; }
      });
      opts.appendChild(btn);
    });
    q.append(opts, feedback);
    box.appendChild(q);
  });
  box.appendChild(scoreEl);
  return box;
}

/* ---------- UI wiring ---------- */
function selectTask(key) {
  current = key;
  const t = TASKS[key];
  els.list.querySelectorAll(".task-btn").forEach((b) => b.setAttribute("aria-current", String(b.dataset.key === key)));
  els.title.textContent = t.label;
  els.hint.textContent = t.hint;
  els.input.placeholder = t.placeholder;
  els.label.textContent = t.label + " - your input";
  els.submit.textContent = t.button;
  els.input.value = "";
  els.result.hidden = true;
  els.result.innerHTML = "";
  els.examples.innerHTML = "";
  t.examples.forEach((ex) => {
    const chip = document.createElement("button");
    chip.type = "button";
    chip.className = "chip";
    chip.textContent = ex;
    chip.addEventListener("click", () => { els.input.value = ex; els.input.focus(); });
    els.examples.appendChild(chip);
  });
  els.input.focus();
}

async function run(event) {
  event.preventDefault();
  const value = els.input.value.trim();
  if (!value || running) return;
  const t = TASKS[current];
  running = true;
  els.submit.disabled = true;
  els.result.hidden = false;
  els.result.innerHTML = `<p class="loading">Working on it${t.wait ? " - " + esc(t.wait) : ""}</p>`;
  try {
    const data = await t.request(value);
    const rendered = t.render(data);
    els.result.innerHTML = "";
    if (typeof rendered === "string") els.result.innerHTML = rendered; else els.result.appendChild(rendered);
  } catch (err) {
    els.result.innerHTML = `<p class="error" role="alert">${esc(err.message)}</p>`;
  } finally {
    running = false;
    els.submit.disabled = false;
    els.result.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }
}

Object.entries(TASKS).forEach(([key, t]) => {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "task-btn";
  btn.dataset.key = key;
  btn.innerHTML = `<strong>${esc(t.label)}</strong><span>${esc(t.blurb)}</span>`;
  btn.addEventListener("click", () => selectTask(key));
  els.list.appendChild(btn);
});
els.form.addEventListener("submit", run);
els.input.addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) els.form.requestSubmit(); });
selectTask("qa");
