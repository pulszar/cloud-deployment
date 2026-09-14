getGroceryList()

getRecommendations()

async function sendToNotesTable() {
    const userNote = document.getElementById("userNote").value;
    await fetch("/notes", {
        method: "POST",
        body: JSON.stringify({message: userNote}),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
    getGroceryList()
}

async function getGroceryList() {
    const response = await fetch("/notes");
    const data = await response.json();

    // Delete all rows first for refreshing purposes
    $('#groceryList tbody').empty();
    // Fill in HTML table with 2d loop  
    for (let r = 0; r < data.length; r++) {
        const itemId = data[r][0]
        const itemName = data[r][1]
        
        const groceryListTbodyRef = document.getElementById('groceryList').getElementsByTagName('tbody')[0];

        let row = groceryListTbodyRef.insertRow()
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

        // Create purchse button
        var purchaseButton = document.createElement('button');
        purchaseButton.textContent = "Purchase";
        purchaseButton.setAttribute("onClick", `purchaseListId('${itemName}', ${itemId});`);

        col2.appendChild(purchaseButton);
    }
}

async function deleteListId(id) {
    await fetch(`/grocerylist/${id}`, {
        method: "DELETE"
    });
    getGroceryList();
}

async function purchaseListId(itemName, itemId) {
    const date_purchased = new Date().toISOString();
    const body = {
        "item": itemName,
        "date_purchased": date_purchased
    };

    await fetch("/purchase", {
        method: "POST",
        body: JSON.stringify(body),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    });

    deleteListId(itemId);
}

async function getRecommendations() {
    const response = await fetch("/recommendations");
    const data = await response.json();

    console.log(data);
    console.log(data.length);

    for (let r = 0; r < data.length; r++) {
        console.log(data[r]);
        const itemRecommendation = data[r].recommendation
        
        const recommendationListTbodyRef = document.getElementById('recommendationList').getElementsByTagName('tbody')[0];

        let row = recommendationListTbodyRef.insertRow()
        
        // Insert recommendation item
        row.insertCell().textContent = `${itemRecommendation}`;
    }
}