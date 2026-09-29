const task = document.getElementById("task");
const inputText = document.getElementById("inputText");
const result = document.getElementById("result");
const status = document.getElementById("status");
const submitBtn = document.getElementById("submitBtn");

const examples = {
  qa: "Which is the largest ocean?",
  explain: "Explain the Pythagoras theorem to a beginner.",
  quiz: "The Earth revolves around the Sun once approximately every 365 days.",
  summarize: "Paste a long educational passage here.",
  learn: "SQL"
};

task.addEventListener("change", () => {
  inputText.placeholder = examples[task.value];
});

async function runTask() {
  const text = inputText.value.trim();
  if (!text) {
    result.textContent = "Please enter some text first.";
    return;
  }

  const endpoints = {
    qa: "/qa",
    explain: "/explain",
    quiz: "/quiz",
    summarize: "/summarize",
    learn: "/learn/recommendations"
  };

  submitBtn.disabled = true;
  status.textContent = "EduGenie is thinking...";
  result.textContent = "";

  try {
    const response = await fetch(endpoints[task.value], {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({text})
    });

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail || "Request failed.");
    }

    if (task.value === "quiz") {
      renderQuiz(data.questions || [], data.error);
    } else {
      result.textContent = data.result || data.error || "No result returned.";
    }
    status.textContent = "Done.";
  } catch (error) {
    result.textContent = "Error: " + error.message;
    status.textContent = "Request failed.";
  } finally {
    submitBtn.disabled = false;
  }
}

function renderQuiz(questions, error) {
  result.innerHTML = "";
  if (error) {
    result.textContent = "Quiz error: " + error;
    return;
  }

  questions.forEach((q, index) => {
    const card = document.createElement("div");
    card.className = "quiz-card";

    const heading = document.createElement("h3");
    heading.textContent = `${index + 1}. ${q.question}`;
    card.appendChild(heading);

    q.options.forEach((option, optionIndex) => {
      const letter = String.fromCharCode(65 + optionIndex);
      const button = document.createElement("button");
      button.className = "option";
      button.textContent = `${letter}. ${option}`;

      button.onclick = () => {
        const correct = q.answer === letter;
        button.classList.add(correct ? "correct" : "wrong");
        if (!correct) {
          button.textContent += ` — Correct answer: ${q.answer}`;
        }
      };

      card.appendChild(button);
    });

    result.appendChild(card);
  });
}

async function copyResult() {
  const text = result.innerText;
  await navigator.clipboard.writeText(text);
  status.textContent = "Copied to clipboard.";
}
