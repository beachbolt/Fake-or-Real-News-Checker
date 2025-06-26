// ✅ content.js is running!
console.log("✅ content.js loaded");

chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === "highlight") {
    console.log("📩 Received highlight data:", request.data);
    highlightFromPopup(request.data);
  }
});

function highlightFromPopup(verdicts) {
  console.log("🔍 Starting highlightFromPopup with", verdicts.length, "verdicts");

  verdicts.forEach(({ sentence, verdict }, index) => {
    const color =
      verdict === "FAKE"
        ? "rgba(255, 0, 0, 0.3)"      // Red
        : verdict === "UNCERTAIN" || verdict === "NEUTRAL" || verdict === "SUSPICIOUS"
        ? "rgba(255, 255, 0, 0.3)"    // Yellow
        : null;

    if (!color) {
      console.log(`⚠️ Skipping sentence [${index}]: "${sentence}" — verdict is "${verdict}"`);
      return;
    }

    console.log(`🎯 Processing [${index}]: "${sentence}" with verdict "${verdict}" and color ${color}`);

    const escaped = sentence.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    const regex = new RegExp(escaped, "gi");

    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    let matched = false;

    while (walker.nextNode()) {
      const node = walker.currentNode;
      const match = node.nodeValue.match(regex);

      if (match) {
        console.log(`✅ Found match in text node: "${node.nodeValue.trim().slice(0, 80)}..."`);

        const span = document.createElement("mark");
        span.style.backgroundColor = color;
        span.style.borderRadius = "4px";
        span.textContent = match[0];

        const range = document.createRange();
        const start = node.nodeValue.indexOf(match[0]);
        range.setStart(node, start);
        range.setEnd(node, start + match[0].length);
        range.deleteContents();
        range.insertNode(span);

        matched = true;
        break;
      }
    }

    if (!matched) {
      console.log(`❌ No match found for: "${sentence}"`);
    }
  });

  console.log("✅ highlightFromPopup finished");
}