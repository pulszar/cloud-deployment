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

async function getGroceryList() {
    const response = await fetch("/notes");
    const data = await response.json();

    // Fill in HTML table with 2d loop
    const groceryList = document.querySelector('table');
    for (let r = 0; r < data.length; r++) {
        let row = groceryList.insertRow()
        for (c = 0;c < 1; c++) {
            row.insertCell().textContent = `${data[r][1]}`
        }
    }
}
