const analyzeBtn = document.getElementById("analyzeBtn");
const results = document.getElementById("results");
const clearBtn = document.getElementById("clearBtn");
const sampleButtons = document.querySelectorAll(".sample-btn[data-sample]");

const senderInput = document.getElementById("sender");
const subjectInput = document.getElementById("subject");
const urlInput = document.getElementById("url");
const bodyInput = document.getElementById("body");

const fieldMap = {
    sender: senderInput,
    subject: subjectInput,
    url: urlInput,
    body: bodyInput,
};

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
        body: `Hi Jeorge,

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

function clearFieldErrors() {
    Object.values(fieldMap).forEach(input => {
        input.classList.remove("field-invalid");
        input.removeAttribute("aria-invalid");

        const feedback = document.getElementById(`${input.id}-error`);
        if (feedback) {
            feedback.remove();
        }
    });
}

function renderFieldError(fieldName, message) {
    const input = fieldMap[fieldName];
    if (!input) {
        return;
    }

    input.classList.add("field-invalid");
    input.setAttribute("aria-invalid", "true");

    const feedback = document.createElement("p");
    feedback.id = `${input.id}-error`;
    feedback.className = "field-error";
    feedback.textContent = message;

    input.insertAdjacentElement("afterend", feedback);
}

function parseValidationErrors(detail) {
    if (!Array.isArray(detail)) {
        return [];
    }

    return detail
        .map(item => {
            if (!item || !Array.isArray(item.loc) || item.loc.length < 2) {
                return null;
            }

            const fieldName = item.loc[item.loc.length - 1];
            if (typeof fieldName !== "string" || !fieldMap[fieldName]) {
                return null;
            }

            const message = typeof item.msg === "string"
                ? item.msg.replace(/^Value error,\s*/i, "")
                : "Invalid value";

            return { fieldName, message };
        })
        .filter(Boolean);
}

function classifyFlag(flag) {
    const value = String(flag || "").toLowerCase();

    if (/(credential|password|verify|account|suspended|login|domain does not match)/.test(value)) {
        return { level: "high", label: "Critical" };
    }

    if (/(shortened|lookalike|unusual|urgent|financial|download|attachment)/.test(value)) {
        return { level: "medium", label: "Warning" };
    }

    return { level: "low", label: "Notice" };
}

function summarizeFlags(flags) {
    return flags.reduce(
        (summary, flag) => {
            const severity = classifyFlag(flag).level;
            summary[severity] += 1;
            return summary;
        },
        { high: 0, medium: 0, low: 0 }
    );
}

function renderResults(data) {
    const badgeClass = data.risk_level.toLowerCase();
    const score = Number(data.score) || 0;
    const flags = Array.isArray(data.red_flags) ? data.red_flags : [];
    const flagSummary = summarizeFlags(flags);

    const indicatorSummaryHtml = `
        <div class="indicator-grid" aria-label="Flag indicator summary">
            <article class="indicator-card high">
                <p class="indicator-label">Critical Indicators</p>
                <p class="indicator-count">${flagSummary.high}</p>
            </article>
            <article class="indicator-card medium">
                <p class="indicator-label">Warning Indicators</p>
                <p class="indicator-count">${flagSummary.medium}</p>
            </article>
            <article class="indicator-card low">
                <p class="indicator-label">Notice Indicators</p>
                <p class="indicator-count">${flagSummary.low}</p>
            </article>
        </div>
    `;

    const flagsHtml = flags.length
        ? flags
            .map(flag => {
                const severity = classifyFlag(flag);
                return `
                    <article class="flag-item ${severity.level}">
                        <span class="flag-level">${escapeHtml(severity.label)}</span>
                        <p class="flag-text">${escapeHtml(flag)}</p>
                    </article>
                `;
            })
            .join("")
        : `
            <div class="flag-empty">No specific red flags were detected for this message.</div>
        `;

    results.className = "";
    results.innerHTML = `
        <div class="badge ${badgeClass}">${escapeHtml(data.risk_level)} Risk</div>

        <div class="score-row">
            <div>
                <div class="score">Score: ${score}/100</div>
                <div class="score-label">Phishing score</div>
            </div>
        </div>

        <div class="progress-wrap">
            <div class="progress-bar">
                <div class="progress-fill ${badgeClass}" style="width: ${Math.max(0, Math.min(100, score))}%"></div>
            </div>
        </div>

        ${indicatorSummaryHtml}

        <div class="result-block">
            <h3>Flagged Indicators</h3>
            <div class="flag-grid">
                ${flagsHtml}
            </div>
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
    clearFieldErrors();
    senderInput.value = "";
    subjectInput.value = "";
    urlInput.value = "";
    bodyInput.value = "";
    results.className = "results-empty";
    results.innerHTML = `<p class="muted">Your phishing analysis will appear here.</p>`;
});

analyzeBtn.addEventListener("click", async () => {
    clearFieldErrors();

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

        if (response.status === 422) {
            const validationPayload = await response.json();
            const validationErrors = parseValidationErrors(validationPayload.detail);

            if (validationErrors.length) {
                validationErrors.forEach(({ fieldName, message }) => {
                    renderFieldError(fieldName, message);
                });

                renderError("Please fix the highlighted fields and try again.");
                return;
            }

            renderError("Your input contains invalid values.");
            return;
        }

        if (!response.ok) {
            throw new Error(`Request failed with status ${response.status}`);
        }

        const data = await response.json();
        renderResults(data);
    } catch (error) {
        renderError("Something went wrong while analyzing the email.");
    }
});