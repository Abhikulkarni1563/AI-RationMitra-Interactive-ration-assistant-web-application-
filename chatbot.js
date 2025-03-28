function sendMessage() {
    let userMessage = document.getElementById("userInput").value;
    fetch("/chatbot", {
        method: "POST",
        body: JSON.stringify({ message: userMessage }),
        headers: { "Content-Type": "application/json" }
    })
    .then(response => response.json())
    .then(data => {
        let chatbox = document.getElementById("chatbox");
        chatbox.innerHTML += `<p><strong>You:</strong> ${userMessage}</p>`;
        chatbox.innerHTML += `<p><strong>Bot:</strong> ${data.response}</p>`;
    });
}
