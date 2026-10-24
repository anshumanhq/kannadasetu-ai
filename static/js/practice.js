const reference = document.getElementById("reference");
const spoken = document.getElementById("spoken");
const listenBtn = document.getElementById("listen-btn");
const micBtn = document.getElementById("mic-btn");
const compareBtn = document.getElementById("compare-btn");
const result = document.getElementById("compare-result");

function speak(text) {
  if (!("speechSynthesis" in window)) {
    alert("Browser does not support speech synthesis.");
    return;
  }
  const utt = new SpeechSynthesisUtterance(text);
  utt.lang = "kn-IN";
  utt.rate = 0.85;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utt);
}

let recognition = null;
let listening = false;

function setupRecognition() {
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if (!SR) return null;
  const r = new SR();
  r.lang = "kn-IN";
  r.interimResults = false;
  r.maxAlternatives = 1;
  r.onresult = (event) => {
    spoken.value = event.results[0][0].transcript;
  };
  r.onerror = (e) => {
    alert("Voice recognition error: " + e.error);
  };
  r.onend = () => {
    listening = false;
    micBtn.textContent = "🎤 Record";
  };
  return r;
}

async function compare() {
  const ref = reference.value.trim();
  const spk = spoken.value.trim();
  if (!ref || !spk) {
    alert("Both fields are required.");
    return;
  }
  const res = await fetch("/api/compare", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ reference: ref, spoken: spk }),
  });
  const data = await res.json();
  if (!res.ok) {
    alert(data.error || "Error");
    return;
  }
  result.innerHTML = `
    <div class="score">${data.similarity}%</div>
    <div>Similarity to reference</div>
    <div class="note">${data.note}</div>
  `;
  result.classList.remove("hidden");
}

listenBtn.addEventListener("click", () => speak(reference.value.trim()));
micBtn.addEventListener("click", () => {
  if (!recognition) recognition = setupRecognition();
  if (!recognition) {
    alert("Browser does not support voice input. Please type instead.");
    return;
  }
  if (listening) {
    recognition.stop();
    listening = false;
    micBtn.textContent = "🎤 Record";
  } else {
    recognition.start();
    listening = true;
    micBtn.textContent = "⏹ Stop";
  }
});
compareBtn.addEventListener("click", compare);
