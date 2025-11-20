document.addEventListener('DOMContentLoaded', () => {
    const chatForm = document.getElementById('chat-form');
    const userInput = document.getElementById('user-input');
    const chatBox = document.getElementById('chat-box');

    function addMessage(text, sender) {
        const div = document.createElement('div');
        div.classList.add('message', sender);
        // Use innerHTML with pre tag for multi-line messages
        if (text.includes('\n')) {
            const pre = document.createElement('pre');
            pre.style.whiteSpace = 'pre-wrap';
            pre.style.margin = '0';
            pre.textContent = text;
            div.appendChild(pre);
        } else {
            div.textContent = text;
        }
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addTypingIndicator() {
        const div = document.createElement('div');
        div.classList.add('typing-indicator');
        div.id = 'typing-indicator';
        div.textContent = 'Tenker...';
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function removeTypingIndicator() {
        const indicator = document.getElementById('typing-indicator');
        if (indicator) {
            indicator.remove();
        }
    }

    async function checkStatus(runId) {
        try {
            const response = await fetch('api.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'checkStatus', run_id: runId })
            });
            const data = await response.json();

            if (data.status === 'completed') {
                removeTypingIndicator();
                addMessage(data.response, 'assistant');
            } else if (data.status === 'queued' || data.status === 'in_progress') {
                setTimeout(() => checkStatus(runId), 1000);
            } else {
                removeTypingIndicator();
                addMessage('Noe gikk galt: ' + data.status, 'assistant');
            }
        } catch (error) {
            removeTypingIndicator();
            addMessage('Feil ved kommunikasjon med serveren.', 'assistant');
        }
    }

    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const message = userInput.value.trim();
        if (!message) return;

        addMessage(message, 'user');
        userInput.value = '';
        addTypingIndicator();

        try {
            const response = await fetch('api.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ action: 'sendMessage', message: message })
            });
            const data = await response.json();

            if (data.error) {
                removeTypingIndicator();
                let errorMsg = 'Feil: ' + data.error;
                if (data.details) {
                    errorMsg += '\nDetaljer: ' + JSON.stringify(data.details, null, 2);
                }
                addMessage(errorMsg, 'assistant');
                console.error('API Error:', data);
            } else {
                checkStatus(data.run_id);
            }
        } catch (error) {
            removeTypingIndicator();
            addMessage('Kunne ikke sende melding.', 'assistant');
        }
    });
});
