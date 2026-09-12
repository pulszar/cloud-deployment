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
        const itemId = data[r][0]
        const itemName = data[r][1]
        
        let row = groceryList.insertRow()
        row.id = itemId
        
        // Insert grocery item
        row.insertCell().textContent = `${itemName}`;

        var col2 = row.insertCell();

        // Create delete button
        var deleteButton = document.createElement('button');
        deleteButton.textContent = "Delete";
        // Using setAttribute to set onClick because .onclick was doing the function upon button creation
        deleteButton.setAttribute("onClick", `deleteListId(${itemId})`);

        col2.appendChild(deleteButton);

    }
}
