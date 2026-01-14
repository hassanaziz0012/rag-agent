const textarea = document.getElementById("message-input");
const submitBtn = document.getElementById("submit-btn");
const sendIcon = document.getElementById("send-icon");
const loadingIcon = document.getElementById("loading-icon");
const chatMessages = document.getElementById("chat-messages");

// WebSocket connection
let ws = null;
let currentAiBubble = null;
let currentFullText = "";
let currentRewrittenQuery = null;
let currentSearchResults = null;

let currentResponseContainer = null;

function connectWebSocket() {
    const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
    ws = new WebSocket(`${protocol}//${window.location.host}/ws/ask-agent`);

    ws.onopen = () => {
        console.log("WebSocket connected");
    };

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleWebSocketMessage(data);
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected, reconnecting...");
        setTimeout(connectWebSocket, 1000);
    };

    ws.onerror = (error) => {
        console.error("WebSocket error:", error);
    };
}

function handleWebSocketMessage(data) {
    switch (data.type) {
        case "rewritten_query":
            const containerRq = ensureResponseContainer();
            containerRq.appendChild(createRewrittenQuery(data.query));
            break;

        case "search_results":
            const containerSr = ensureResponseContainer();
            if (data.results && data.results.length > 0) {
                containerSr.appendChild(createSearchCards(data.results));
            }
            break;

        case "chunk":
            if (data.content) {
                if (!currentAiBubble) {
                    const containerChunk = ensureResponseContainer();
                    const bubbleDiv = document.createElement("div");
                    bubbleDiv.className = STYLES.aiBubble;
                    containerChunk.appendChild(bubbleDiv);
                    currentAiBubble = bubbleDiv;
                }
                currentFullText += data.content;
                currentAiBubble.innerHTML = marked.parse(currentFullText);
                currentAiBubble.scrollIntoView({ behavior: "smooth", block: "end" });
            }
            break;

        case "done":
            console.log("Stream complete. Success:", data.success);
            setLoading(false);
            resetCurrentResponse();
            break;

        case "error":
            hideTypingIndicator();
            addMessage(data.message, false);
            setLoading(false);
            resetCurrentResponse();
            break;
    }
}

function resetCurrentResponse() {
    currentAiBubble = null;
    currentFullText = "";
    currentResponseContainer = null;
}

function ensureResponseContainer() {
    if (!currentResponseContainer) {
        hideTypingIndicator();
        
        const containerDiv = document.createElement("div");
        containerDiv.className = STYLES.containerDiv;

        const responseWrapper = document.createElement("div");
        responseWrapper.className = STYLES.responseWrapper;

        containerDiv.appendChild(responseWrapper);
        chatMessages.appendChild(containerDiv);
        
        currentResponseContainer = responseWrapper;
    }
    return currentResponseContainer;
}

function createRewrittenQuery(query) {
    const wrapper = document.createElement("div");
    wrapper.className = STYLES.rewrittenQueryWrapper;
    
    wrapper.innerHTML = `
        <svg class="${STYLES.rewrittenQueryIcon}" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"/>
        </svg>
        <div class="${STYLES.rewrittenQueryText}">
            ${escapeHtml(query)}
        </div>
    `;
    return wrapper;
}

function createSearchCards(results) {
    const cardsContainer = document.createElement("div");
    cardsContainer.className = STYLES.searchCardsContainer;

    for (const result of results) {
        const card = document.createElement("div");
        card.className = STYLES.searchCard;
        card.innerHTML = `
            <div class="${STYLES.searchCardHeader}">
                <span class="${STYLES.searchCardSource}">Source #${result.id + 1}</span>
                <span class="${STYLES.searchCardScore}">${result.score.toFixed(2)}</span>
            </div>
            <p class="${STYLES.searchCardText}">${escapeHtml(result.paragraph)}</p>
        `;
        cardsContainer.appendChild(card);
    }
    return cardsContainer;
}

// Auto-resize textarea
textarea.addEventListener("input", function () {
    this.style.height = "auto";
    this.style.height = Math.min(this.scrollHeight, 200) + "px";
});

// Show typing indicator
function showTypingIndicator() {
    const typingDiv = document.createElement("div");
    typingDiv.id = "typing-indicator";
    typingDiv.className = "flex justify-start";
    typingDiv.innerHTML = `
            <div class="max-w-[80%] px-5 py-3 rounded-[18px] rounded-bl-[4px] bg-white text-gray-800 border border-gray-200 shadow-[0_2px_12px_rgba(0,0,0,0.08)]">
                <div class="flex items-center gap-1">
                    <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                    <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                    <span class="typing-dot w-2 h-2 bg-gray-400 rounded-full"></span>
                </div>
            </div>
        `;
    chatMessages.appendChild(typingDiv);
    typingDiv.scrollIntoView({ behavior: "smooth", block: "end" });
}

// Hide typing indicator
function hideTypingIndicator() {
    const typingDiv = document.getElementById("typing-indicator");
    if (typingDiv) {
        typingDiv.remove();
    }
}

// Hide welcome header
function hideWelcomeHeader() {
    const header = document.getElementById("welcome-header");
    if (header) {
        header.style.display = "none";
    }
}

// Set loading state
function setLoading(isLoading) {
    submitBtn.disabled = isLoading;
    textarea.disabled = isLoading;
    if (isLoading) {
        sendIcon.classList.add("hidden");
        loadingIcon.classList.remove("hidden");
        showTypingIndicator();
    } else {
        sendIcon.classList.remove("hidden");
        loadingIcon.classList.add("hidden");
        hideTypingIndicator();
    }
}

// Add message to chat (for user messages and error messages)
function addMessage(content, isUser) {
    if (isUser) {
        hideWelcomeHeader();
    }

    const messageDiv = document.createElement("div");
    messageDiv.className = `flex ${isUser ? "justify-end" : "justify-start"}`;

    const bubbleDiv = document.createElement("div");
    bubbleDiv.className = isUser ? STYLES.userBubble : STYLES.aiBubble;

    if (isUser) {
        // User messages: plain text, escaped
        bubbleDiv.innerHTML = `<p class="text-[15px] leading-relaxed whitespace-pre-wrap">${escapeHtml(content)}</p>`;
    } else {
        // AI messages: render as markdown
        bubbleDiv.innerHTML = marked.parse(content);
    }
    messageDiv.appendChild(bubbleDiv);
    chatMessages.appendChild(messageDiv);

    // Scroll to bottom
    messageDiv.scrollIntoView({ behavior: "smooth", block: "end" });

    return bubbleDiv;
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

// Handle form submission
document.getElementById("chat-form").addEventListener("submit", function (e) {
    e.preventDefault();
    const message = textarea.value.trim();
    if (message && !submitBtn.disabled) {
        // Add user message
        addMessage(message, true);

        // Clear input
        textarea.value = "";
        textarea.style.height = "auto";

        // Set loading state
        setLoading(true);

        // Send message via WebSocket
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ query: message }));
        } else {
            console.error("WebSocket not connected");
            addMessage("Connection error. Please refresh the page.", false);
            setLoading(false);
        }
    }
});

// Submit on Enter (Shift+Enter for new line)
textarea.addEventListener("keydown", function (e) {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        document.getElementById("chat-form").dispatchEvent(new Event("submit"));
    }
});

// Initialize WebSocket connection on page load
connectWebSocket();
