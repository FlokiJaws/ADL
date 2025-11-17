document.addEventListener('DOMContentLoaded', () => {
    // Récupère les éléments HTML dont nous aurons besoin
    const form = document.getElementById('debate-form');
    const topicInput = document.getElementById('topic-input');
    const debateOutput = document.getElementById('debate-output');
    const loadingIndicator = document.getElementById('loading-indicator');

    // Ajoute un écouteur d'événement pour la soumission du formulaire
document.getElementById('debate-form').addEventListener('submit', async function(e) {
    e.preventDefault();

    const topic = document.getElementById('topic-input').value;
    const debateOutput = document.getElementById('debate-output');
    debateOutput.innerHTML = ''; // Clear previous debate

    // Display initial loading message
    const initialMessage = document.createElement('p');
    initialMessage.textContent = "Débat en cours de préparation...";
    initialMessage.classList.add('info-message');
    debateOutput.appendChild(initialMessage);

    const thinkingMessage = document.createElement('p');
    thinkingMessage.textContent = "L'autre IA réfléchit...";
    thinkingMessage.classList.add('info-message');
    thinkingMessage.style.display = 'none'; // Hidden initially
    debateOutput.appendChild(thinkingMessage);


    try {
        const response = await fetch('/debate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ topic: topic })
        });

        if (!response.ok) {
            initialMessage.remove(); // Remove initial message on error
            thinkingMessage.remove(); // Remove thinking message on error
            const errorData = await response.json(); // Still try to parse JSON for error details
            debateOutput.innerHTML = `<p class="error">Erreur: ${errorData.error || response.statusText}</p>`;
            return;
        }

        initialMessage.remove(); // Remove initial message once stream starts

        const reader = response.body.getReader();
        const decoder = new TextDecoder('utf-8');
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) {
                break;
            }

            buffer += decoder.decode(value, { stream: true });

            // Process complete messages (Server-Sent Events format: data: {json}\n\n)
            const messages = buffer.split('\n\n');
            buffer = messages.pop(); // Keep incomplete message in buffer

            for (const message of messages) {
                if (message.startsWith('data: ')) {
                    const jsonString = message.substring(6); // Remove 'data: '
                    try {
                        const item = JSON.parse(jsonString);
                        if (item.error) {
                            debateOutput.innerHTML += `<p class="error">Erreur du serveur: ${item.error}</p>`;
                            thinkingMessage.style.display = 'none';
                            return;
                        }
                        const messageDiv = document.createElement('div');
                        messageDiv.classList.add('debate-message');

                        // Determine speaker class based on speaker name
                        let speakerClass = '';
                        if (item.speaker.toLowerCase() === 'optimiste') {
                            speakerClass = 'optimist-message';
                        } else if (item.speaker.toLowerCase() === 'sceptique') {
                            speakerClass = 'sceptic-message';
                        }
                        if(speakerClass) messageDiv.classList.add(speakerClass);


                        const speakerName = document.createElement('strong');
                        speakerName.textContent = item.speaker;

                        messageDiv.appendChild(speakerName);
                        messageDiv.append(item.message); // Appends the message text after the <strong> tag

                        debateOutput.appendChild(messageDiv);
                        debateOutput.scrollTop = debateOutput.scrollHeight; // Scroll to bottom
                        thinkingMessage.style.display = 'block'; // Show thinking message after a response
                    } catch (parseError) {
                        console.error('Error parsing JSON:', parseError, jsonString);
                    }
                }
            }
        }
        thinkingMessage.remove(); // Remove thinking message at the end
        const endMessage = document.createElement('p');
        endMessage.textContent = "Fin du débat.";
        endMessage.classList.add('info-message');
        debateOutput.appendChild(endMessage);
        debateOutput.scrollTop = debateOutput.scrollHeight; // Scroll to bottom

    } catch (error) {
        initialMessage.remove(); // Remove initial message on unexpected error
        thinkingMessage.remove(); // Remove thinking message on unexpected error
        debateOutput.innerHTML += `<p class="error">Une erreur inattendue est survenue: ${error.message}</p>`;
    }
});
});