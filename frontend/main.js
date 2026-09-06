async function greet() {
    const greetUserInput = document.getElementById("greetUserInput").value; // Get input
    const result = await fetch(`/greet/${greetUserInput}`); // Send to server, get response
    const data = await result.json();
    document.getElementById("greetServerResponse").textContent = data.message; // Set placeholder element
}

async function initializeDb() {
    await fetch(`/initiate`, {
        method: "POST"
    });
}

async function sendToNotesTable() {
    const userNote = document.getElementById("userNote").value;
    await fetch("/notes", {
        method: "POST",
        body: JSON.stringify({message: userNote}),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
}