getGroceryList()

getRecommendations()

// TODO: Integrate these two functions together
async function sendToList(item) {
    await fetch("/notes", {
        method: "POST",
        body: JSON.stringify({message: item}),
        headers: {
            "Content-type": "application/json; charset=UTF-8"
        }
    })
    getGroceryList();
}

async function sendToNotesTableUserInput() {
    const userNote = document.getElementById("userNote").value;
    sendToList(userNote);
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

        // Convert to local time
        var lastPurchased = new Date(data[r].last_purchased).toLocaleString() + " UTC";
        var lastPurchasedLocalTime = new Date(lastPurchased).toString();
        var dateObjLastPurchasedLocalTime = new Date(lastPurchasedLocalTime);

        const secondsBetweenPurchases = data[r].average_seconds_between_purchases

        lastPurchased = lastPurchased.toString(); 
        
        const recommendationListTbodyRef = document.getElementById('recommendationList').getElementsByTagName('tbody')[0];

        let row = recommendationListTbodyRef.insertRow()
        
        // Insert recommendation item
        row.insertCell().textContent = `${itemRecommendation}`;
        row.insertCell().textContent = `${dateObjLastPurchasedLocalTime.toLocaleString()}`;

        var d = Math.floor(secondsBetweenPurchases / (3600*24));
        var h = Math.floor(secondsBetweenPurchases % (3600*24) / 3600);
        var m = Math.floor(secondsBetweenPurchases % 3600 / 60);

        var dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
        var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
        var mDisplay = m > 0 ? m + (m == 1 ? " minute " : " minutes ") : "";

        timeDisplay = dDisplay + hDisplay + mDisplay;

        row.insertCell().textContent = `Every ${timeDisplay}`;

        var addCol = row.insertCell();
        var addButton = document.createElement("Button");
        addButton.innerHTML = "Add to List";
        addButton.setAttribute("onclick", `sendToList('${itemRecommendation}')`)

        addCol.appendChild(addButton);
    }
}