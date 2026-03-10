
const pdfInput = document.getElementById("pdfInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const progressBar = document.getElementById("progressBar");
const progressContainer = document.getElementById("progressContainer");
const questionInput = document.getElementById("questionInput");
const sendBtn = document.getElementById("sendBtn");
const chat = document.getElementById("chat");
const statusDot = document.getElementById("statusDot");
const statusText = document.getElementById("statusText");

// 1. Handle PDF Upload & Indexing
uploadBtn.addEventListener("click", async () => {
    if (!pdfInput.files[0]) {
        uploadStatus.textContent = "Error: No file selected.";
        return;
    }

    const formData = new FormData();
    formData.append("file", pdfInput.files[0]);

    // UI Reset
    progressContainer.style.display = "block";
    progressBar.style.width = "0%";
    uploadStatus.textContent = "Scanning document layers...";
    uploadBtn.disabled = true;

    // Simulated progress for better UX
    let simProgress = 0;
    const progressTimer = setInterval(() => {
        if (simProgress < 90) {
            simProgress += Math.random() * 15;
            progressBar.style.width = Math.min(simProgress, 90) + "%";
        }
    }, 300);

    try {
        const res = await fetch("/upload", { method: "POST", body: formData });
        const data = await res.json();
        clearInterval(progressTimer);

        if (data.error) {
            uploadStatus.textContent = "Analysis Failed: " + data.error;
            progressBar.style.background = "var(--error)";
            uploadBtn.disabled = false;
        } else {
            progressBar.style.width = "100%";
            uploadStatus.textContent = "NEURAL INDEX COMPLETE.";
            statusDot.style.background = "var(--neon)";
            statusDot.style.boxShadow = "0 0 10px var(--neon)";
            statusText.textContent = "ONLINE";

            // UNLOCK INTERFACE
            questionInput.disabled = false;
            sendBtn.disabled = false;
            questionInput.placeholder = "Query the document structure...";
            questionInput.focus();
        }
    } catch (err) {
        clearInterval(progressTimer);
        uploadStatus.textContent = "Connection Terminated.";
    }
});

// 2. Handle Chat Queries (Streaming)
sendBtn.addEventListener("click", async () => {
    const query = questionInput.value.trim();
    if (!query) return;

    addMessage(query, "user");
    questionInput.value = "";
    const aiBubble = addMessage("Thinking...", "ai");

    try {
        const response = await fetch(`/query?q=${encodeURIComponent(query)}`);
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let fullText = "";

        while (true) {
            const { done, value } = await reader.read();
            if (done) break;
            
            fullText += decoder.decode(value, { stream: true });
            aiBubble.innerText = fullText;
            chat.scrollTop = chat.scrollHeight;
        }
    } catch (err) {
        aiBubble.textContent = "Critical Error: Could not reach LLM.";
    }
});

function addMessage(text, cls) {
    const div = document.createElement("div");
    div.classList.add("message", cls);
    div.textContent = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
    return div;
}

// Support Enter Key
questionInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter" && !questionInput.disabled) sendBtn.click();
});