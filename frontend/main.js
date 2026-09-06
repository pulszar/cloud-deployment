async function greet() {
    const greetUserInput = document.getElementById("greetUserInput").value; // Get input
    const result = await fetch(`/greet/${greetUserInput}`); // Send to server, get response
    const data = await result.json();
    document.getElementById("greetServerResponse").textContent = data.message; // Set placeholder element
}

async function initializeDb() {
    const result = await fetch(`/initiate`, {
        method: "POST"
    });
    const data = await result.json();
    document.getElementById("dbInitializeServerResponse").textContent = data.message; // Set placeholder element
}