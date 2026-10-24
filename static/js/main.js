const inputText = document.getElementById("input-text");
const translateBtn = document.getElementById("translate-btn");
const errorEl = document.getElementById("error");
const resultCard = document.getElementById("result-card");
const kannadaText = document.getElementById("kannada-text");
const transliteration = document.getElementById("transliteration");
const meaning = document.getElementById("meaning");
const sourceBadge = document.getElementById("source-badge");
const followUpsEl = document.getElementById("follow-ups");
const playBtn = document.getElementById("play-btn");
const copyBtn = document.getElementById("copy-btn");

let currentKannada = "";

function showError(msg) {
  errorEl.textContent = msg;
  errorEl.classList.remove("hidden");
}

function hideError() {
  errorEl.classList.add("hidden");
}

function badgeFor(source) {
  if (source === "verified_phrase") return "✓ Verified phrase";
  if (source === "api") return "⚡ AI-translated";
  return "⚠ Fallback — not verified";
}

function badgeClass(source) {
  if (source === "verified_phrase") return "source-badge verified";
  if (source === "api") return "source-badge";
  return "source-badge fallback";
}

async function translate() {
  hideError();
  const text = inputText.value.trim();
  if (!text) {
    showError("Please enter something to translate.");
    return;
  }

  translateBtn.disabled = true;
  translateBtn.textContent = "Translating…";

  try {
    const res = await fetch("/api/translate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        text,
        source_lang: document.getElementById("source-lang").value,
        situation: document.getElementById("situation").value,
      }),
    });
    const data = await res.json();
    if (!res.ok) {
      showError(data.error || "Something went wrong.");
      return;
    }

    currentKannada = data.kannada;
    kannadaText.textContent = data.kannada;
    transliteration.textContent = data.transliteration || "";
    meaning.textContent = data.meaning || "";
    sourceBadge.textContent = badgeFor(data.source);
    sourceBadge.className = badgeClass(data.source);

    followUpsEl.innerHTML = "";
    (data.follow_ups || []).forEach((f) => {
      const li = document.createElement("li");
      li.innerHTML = `<span class="kn">${f.kn}</span><span class="en">${f.en}</span>`;
      li.addEventListener("click", () => {
        inputText.value = f.en;
        translate();
      });
      followUpsEl.appendChild(li);
    });

    resultCard.classList.remove("hidden");
  } catch (e) {
    showError("Network error: " + e.message);
  } finally {
    translateBtn.disabled = false;
    translateBtn.textContent = "Translate to Kannada";
  }
}

function speak(text) {
  if (!text) return;
  if ("speechSynthesis" in window) {
    const utt = new SpeechSynthesisUtterance(text);
    utt.lang = "kn-IN";
    utt.rate = 0.9;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utt);
  } else {
    alert("Browser does not support speech synthesis.");
  }
}

async function copyKannada() {
  if (!currentKannada) return;
  try {
    await navigator.clipboard.writeText(currentKannada);
    copyBtn.textContent = "✓ Copied";
    setTimeout(() => (copyBtn.textContent = "📋 Copy"), 1500);
  } catch {
    alert("Copy failed.");
  }
}

translateBtn.addEventListener("click", translate);
inputText.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) translate();
});
playBtn.addEventListener("click", () => speak(currentKannada));
copyBtn.addEventListener("click", copyKannada);
