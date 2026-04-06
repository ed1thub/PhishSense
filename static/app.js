const analyzeBtn = document.getElementById("analyzeBtn");
const results = document.getElementById("results");

analyzeBtn.addEventListener("click", async () => {
    const sender = document.getElementById("sender").value.trim();
    const subject = document.getElementById("subject").value.trim();
    const body = document.getElementById("body").value.trim();
    const url = document.getElementById("url").value.trim();

    if (!body) {
        results.innerHTML = `<p class="muted">Please paste an email body first.</p>`;
        return;
    }

    results.innerHTML = `<p class="muted">Analyzing...</p>`;

    try {
        const response = await fetch("/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ sender, subject, body, url })
        });

        const data = await response.json();

        const badgeClass = data.risk_level.toLowerCase();

        results.innerHTML = `
            <div class="badge ${badgeClass}">${data.risk_level} Risk</div>
            <div class="score">Score: ${data.score}/100</div>

            <div class="result-block">
                <h3>Red Flags</h3>
                <ul>
                    ${data.red_flags.map(flag => `<li>${flag}</li>`).join("")}
                </ul>
            </div>

            <div class="result-block">
                <h3>AI Explanation</h3>
                <p>${data.ai_explanation}</p>
            </div>

            <div class="result-block">
                <h3>Recommended Action</h3>
                <p>${data.recommended_action}</p>
            </div>
        `;
    } catch (error) {
        results.innerHTML = `<p class="muted">Something went wrong while analyzing the email.</p>`;
    }
});