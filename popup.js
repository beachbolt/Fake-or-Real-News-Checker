let lastResults = [];

document.getElementById("check").addEventListener("click", () => {
  document.getElementById("summary").textContent = "Analyzing...";
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    const tabId = tabs[0].id;

    chrome.scripting.executeScript(
      {
        target: { tabId },
        func: () => document.body.innerText
      },
      async (results) => {
        const text = results[0].result;
        try {
          const res = await fetch("http://127.0.0.1:5000/analyze", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ text })
          });

          const data = await res.json();
          lastResults = data.results;

          const summaryBlock = document.getElementById("summary");
          summaryBlock.innerHTML = `<strong>📰 Summary:</strong><br>` +
            data.summary.map(s => `<div>• ${s}</div>`).join("");

          const resultBlock = document.getElementById("results");
          resultBlock.innerHTML = `<strong>🧪 Sentence Verdicts:</strong><br>`;
          data.results.forEach((item) => {
            resultBlock.innerHTML += `
              <div class="sentence ${item.verdict}">
                ${item.sentence}
                <div class="confidence">[${item.verdict}, confidence: ${item.confidence}]</div>
              </div>`;
          });

          document.getElementById("highlight").style.display = "block";
          document.getElementById("disagree").style.display = "block";

          const sourceRes = await fetch("http://127.0.0.1:5000/sources");
          const sourceData = await sourceRes.json();
          const sourceBlock = document.getElementById("sources");
          sourceBlock.innerHTML = `<strong>📚 Related Sources:</strong><div class="link-list">` +
            sourceData.links.map(url => `<a href="${url}" target="_blank">${url}</a>`).join("") +
            `</div>`;

        } catch (err) {
          document.getElementById("summary").textContent = "⚠️ Error connecting to backend.";
        }
      }
    );
  });
});

// ✅ FIXED: Send verdicts to content.js via message instead of executing script directly
document.getElementById("highlight").addEventListener("click", () => {
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    chrome.tabs.sendMessage(tabs[0].id, {
      action: "highlight",
      data: lastResults.map(r => ({
        sentence: r.sentence,
        verdict: r.verdict
      }))
    });
  });
});

document.getElementById("disagree").addEventListener("click", async () => {
  await fetch("http://127.0.0.1:5000/feedback", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ feedback: "User disagreed with analysis", data: lastResults })
  });
  alert("✅ Thanks for the feedback!");
});