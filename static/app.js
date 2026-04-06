const analyzeBtn = document.getElementById("analyzeBtn");
const results = document.getElementById("results");
const clearBtn = document.getElementById("clearBtn");
const sampleButtons = document.querySelectorAll(".sample-btn[data-sample]");

const senderInput = document.getElementById("sender");
const subjectInput = document.getElementById("subject");
const urlInput = document.getElementById("url");
const bodyInput = document.getElementById("body");

const samples = {
    phishing: {
        sender: "support@micros0ft-login.com",
        subject: "Urgent: Verify your account now",
        url: "https://bit.ly/security-check",
        body: `Dear user,

Your account has been suspended due to unusual activity.
Verify your account immediately to avoid permanent closure.

Log in now and confirm your password.

Regards,
Support Team`
    },
    benign: {
        sender: "library@mit.edu.au",
        subject: "Reminder: Library book due next week",
        url: "",
        body: `Hi Siamul,

This is a reminder that your borrowed library book is due next Tuesday.

You can renew it through the official student portal if needed.

Thanks,
MIT Library Team`
    }
};

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#39;");
}

function renderLoading() {
    results.className = "";
    results.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p class="muted">Analyzing email with rules and AI...</p>
        </div>
    `;
}

function renderError(message) {
    results.className = "";
    results.innerHTML = `
        <div class="error-box">
            ${escapeHtml(message)}
        </div>
    `;
}

function renderResults(data) {
    const badgeClass = data.risk_level.toLowerCase();
    const flagsHtml = data.red_flags
        .map(flag => `<li>${escapeHtml(flag)}</li>`)
        .join("");

    results.className = "";
    results.innerHTML = `
        <div class="badge ${badgeClass}">${escapeHtml(data.risk_level)} Risk</div>

        <div class="score-row">
            <div>
                <div class="score">Score: ${escapeHtml(data.score)}/100</div>
                <div class="score-label">Rule-based phishing score</div>
            </div>
        </div>

        <div class="progress-wrap">
            <div class="progress-bar">
                <div class="progress-fill ${badgeClass}" style="width: ${Math.max(0, Math.min(100, data.score))}%"></div>
            </div>
        </div>

        <div class="result-block">
            <h3>Red Flags</h3>
            <ul class="flag-list">
                ${flagsHtml}
            </ul>
        </div>

        <div class="result-block">
            <h3>AI Explanation</h3>
            <div class="ai-box">${escapeHtml(data.ai_explanation)}</div>
        </div>

        <div class="result-block">
            <h3>Recommended Action</h3>
            <div class="action-box">${escapeHtml(data.recommended_action)}</div>
        </div>
    `;
}

sampleButtons.forEach(button => {
    button.addEventListener("click", () => {
        const sampleName = button.dataset.sample;
        const sample = samples[sampleName];
        if (!sample) return;

        senderInput.value = sample.sender;
        subjectInput.value = sample.subject;
        urlInput.value = sample.url;
        bodyInput.value = sample.body;
    });
});

clearBtn.addEventListener("click", () => {
    senderInput.value = "";
    subjectInput.value = "";
    urlInput.value = "";
    bodyInput.value = "";
    results.className = "results-empty";
    results.innerHTML = `<p class="muted">Your phishing analysis will appear here.</p>`;
});

analyzeBtn.addEventListener("click", async () => {
    const sender = senderInput.value.trim();
    const subject = subjectInput.value.trim();
    const body = bodyInput.value.trim();
    const url = urlInput.value.trim();

    if (!body) {
        renderError("Please paste an email body first.");
        return;
    }

    renderLoading();

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ sender, subject, body, url })
        });

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);
    } catch (error) {
        renderError("Something went wrong while analyzing the email.");
    }
});