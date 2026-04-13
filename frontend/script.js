const API_BASE = "http://localhost:8000";
let detail = "standard";
let summaryData = null;

function setDetail(d) {
  detail = d;
  document.querySelectorAll(".pill").forEach(p => p.classList.remove("active"));
  document.getElementById("pill-" + d).classList.add("active");
}

function showStatus(msg) {
  const el = document.getElementById("status");
  el.className = "status-bar";
  el.innerHTML = `<div class="spinner"></div><span>${msg}</span>`;
  document.getElementById("error").className = "hidden";
}

function showError(msg) {
  const el = document.getElementById("error");
  el.className = "error-bar";
  el.textContent = "× " + msg;
  document.getElementById("status").className = "hidden";
}

function hideStatus() {
  document.getElementById("status").className = "hidden";
}

function switchTab(tab) {
  document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"));
  document.getElementById("tab-" + tab).classList.add("active");
  document.querySelectorAll(".pane").forEach(p => p.classList.remove("active"));
  document.getElementById("pane-" + tab).classList.add("active");
}

async function summarize() {
  const url = document.getElementById("urlInput").value.trim();
  if (!url) return showError("Paste a YouTube URL first.");

  document.getElementById("btn").disabled = true;
  document.getElementById("result").innerHTML = "";
  showStatus("Fetching video info + transcript...");

  try {
    const res = await fetch(`${API_BASE}/summarize`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url, detail })
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || "Server error");
    }

    const data = await res.json();
    summaryData = data.summary;
    hideStatus();
    render(data);
  } catch (e) {
    showError(e.message);
  } finally {
    document.getElementById("btn").disabled = false;
  }
}
function downloadPDF() {
    window.print();
  }

function render(data) {
    const s = data.summary;
  
    function formatBold(text) {
      return String(text || "").replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
    }
  
    document.getElementById("result").innerHTML = `
      <div class="result-card">
        <div class="result-header">
          <img class="thumb" src="${data.thumbnail}" alt="thumbnail" onerror="this.style.display='none'" />
          <div>
            <div class="video-title">${esc(s.title)}</div>
            <div class="video-channel">${esc(data.meta.channel)}</div>
          </div>
        </div>
        <div class="tabs">
          <div class="tab active" id="tab-notes" onclick="switchTab('notes')">Study Notes</div>
          <div class="tab" id="tab-summary" onclick="switchTab('summary')">Quick Revision</div>
          <div class="tab" id="tab-questions" onclick="switchTab('questions')">Practice Q&A</div>
        </div>
        <div class="tab-content">
  
          <div class="pane active" id="pane-notes">
            <div class="tldr">${esc(s.introduction)}</div>
  
            ${s.sections.map(sec => `
              <div style="margin-top:1.5rem;">
                <div class="section-label">${esc(sec.heading)}</div>
                ${sec.subsections.map(sub => `
                  <div style="margin-bottom:1.25rem;padding:12px;background:#f9f8f5;border-radius:8px;">
                    <div style="font-size:14px;font-weight:700;margin-bottom:8px;">${esc(sub.subheading)}</div>
                    <div style="font-size:14px;line-height:1.8;">${formatBold(sub.content)}</div>
  
                    ${sub.keyTerms && sub.keyTerms.length ? `
                      <div style="margin-top:10px;">
                        <span style="font-size:11px;font-family:'DM Mono',monospace;color:#888;text-transform:uppercase;letter-spacing:0.08em;">Key Terms</span>
                        <ul style="margin-top:6px;padding-left:16px;">
                          ${sub.keyTerms.map(t => `<li style="font-size:13px;margin-bottom:4px;">${formatBold(t)}</li>`).join("")}
                        </ul>
                      </div>` : ""}
  
                    ${sub.example ? `
                      <div style="margin-top:10px;padding:8px 12px;border-left:3px solid #378add;background:#f0f6ff;border-radius:0 6px 6px 0;">
                        <span style="font-size:11px;font-family:'DM Mono',monospace;color:#1a5fb4;text-transform:uppercase;letter-spacing:0.08em;">Example</span>
                        <div style="font-size:13px;margin-top:4px;line-height:1.6;">${formatBold(sub.example)}</div>
                      </div>` : ""}
  
                    ${sub.mnemonic ? `
                      <div style="margin-top:10px;padding:8px 12px;border-left:3px solid #e9a800;background:#fffbeb;border-radius:0 6px 6px 0;">
                        <span style="font-size:11px;font-family:'DM Mono',monospace;color:#92600a;text-transform:uppercase;letter-spacing:0.08em;">Memory Trick</span>
                        <div style="font-size:13px;margin-top:4px;line-height:1.6;">${esc(sub.mnemonic)}</div>
                      </div>` : ""}
  
                    ${sub.examQuestion ? `
                      <div style="margin-top:10px;padding:8px 12px;border-left:3px solid #2a9d5c;background:#f0faf5;border-radius:0 6px 6px 0;">
                        <span style="font-size:11px;font-family:'DM Mono',monospace;color:#1e7a3c;text-transform:uppercase;letter-spacing:0.08em;">Exam Question</span>
                        <div style="font-size:13px;margin-top:4px;line-height:1.6;font-style:italic;">${esc(sub.examQuestion)}</div>
                      </div>` : ""}
                  </div>
                `).join("")}
              </div>
            `).join("")}
  
            ${s.commonMistakes && s.commonMistakes.length ? `
              <div style="margin-top:1.5rem;">
                <div class="section-label">Common Mistakes</div>
                <ul style="padding-left:16px;">
                  ${s.commonMistakes.map(m => `<li style="font-size:14px;margin-bottom:6px;line-height:1.6;">${esc(m)}</li>`).join("")}
                </ul>
              </div>` : ""}
  
            
          <button class="copy-btn no-print" onclick="copyText()">Copy notes to clipboard</button>
          <button class="copy-btn no-print" onclick="downloadPDF()">Download as PDF</button>
          <div class="pane" id="pane-summary">
            <div class="section-label">Key Concepts</div>
            <ul style="padding-left:16px;margin-bottom:1.25rem;">
              ${(s.keyConceptsSummary || []).map(c => `<li style="font-size:14px;margin-bottom:6px;line-height:1.6;">${esc(c)}</li>`).join("")}
            </ul>
            <div class="section-label">Quick Revision</div>
            <div class="tldr">${formatBold(s.quickRevisionSummary)}</div>
          </div>
  
          <div class="pane" id="pane-questions">
            <div class="section-label">Practice Q&A</div>
            ${(s.practiceQuestions || []).map((item, i) => `
              <div style="margin-bottom:1rem;padding:12px;background:#f9f8f5;border-radius:8px;">
                <div style="font-size:14px;font-weight:600;margin-bottom:6px;">Q${i+1}. ${esc(item.q)}</div>
                <div style="font-size:13px;color:#555;line-height:1.7;border-top:1px solid #e0dfd8;padding-top:6px;margin-top:6px;">${formatBold(item.a)}</div>
              </div>
            `).join("")}
          </div>
  
        </div>
      </div>`;
  }

function esc(str) {
  return String(str || "").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;");
}

function copyText() {
  if (!summaryData) return;
  const kps = summaryData.keyPoints.map(k => `${k.num}. ${k.point}`).join("\n");
  const text = `TL;DR:\n${summaryData.tldr}\n\nKey Points:\n${kps}`;
  navigator.clipboard.writeText(text).then(() => {
    const b = document.querySelector(".copy-btn");
    b.textContent = "Copied!";
    setTimeout(() => b.textContent = "Copy summary to clipboard", 1800);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("urlInput").addEventListener("keydown", e => {
    if (e.key === "Enter") summarize();
  });
});