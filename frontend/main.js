var bearer = 'Bearer ' + localStorage.getItem('access_token')

getGroceryList()

getRecommendations()

async function login() {
    username = document.getElementById("username").value;
    password = document.getElementById("password").value;

    const formData = new URLSearchParams();

    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch ('/token', {
            method: "POST",
            body: formData,
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }

        const data = await response.json()
        window.localStorage.setItem('access_token', data.access_token);
        getGroceryList();
    } catch(e) {
        console.error(e);
        return null;
    }
}

async function register() {
    username = document.getElementById("regUsername").value;
    email = document.getElementById("regEmail").value;
    password = document.getElementById("regPassword").value;

    try {
        const response = await fetch ('/create_user', {
            method: "POST",
            body: JSON.stringify({
                "username": username,
                "email":  email,
                "password": password
            }),
            headers: {
                "Content-Type": "application/json; charset=UTF-8"
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP Error: ${response.status}`);
        }
    } catch(e) {
        console.error(e);
        return null;
    }
}

// TODO: Integrate these two functions together
async function sendToList(item) {
    var bearer = 'Bearer ' + localStorage.getItem('access_token')
    try {
        const response = await fetch("/notes", {
            method: "POST",
            body: JSON.stringify({message: item}),
            headers: {
                "Content-type": "application/json; charset=UTF-8",
                "Authorization": bearer,
            }
        })
        if (!response.ok) {
            window.alert("Error occured. You must be logged into create items");
            throw new Error(`HTTP error: ${response.status}`);
        }

        getGroceryList();
    } catch(e) {
        console.error(e);
        return null;
    }
}

async function sendToNotesTableUserInput() {
    const userNote = document.getElementById("userNote").value;
    sendToList(userNote);
}

async function getGroceryList() {
    var bearer = 'Bearer ' + localStorage.getItem('access_token')
    const response = await fetch("/notes", {
        headers: {
            "Authorization": bearer
        }
    });
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

        // ITEM COLUMN
        
        // Insert grocery item
        row.insertCell().textContent = `${itemName}`;

        // QUANTITY COLUMN

        const quantityInput = document.createElement("input"); // Child
        quantityInput.id = 'quantityInputId' + itemId;
        quantityInput.value = 1;
        quantityInput.classList.add("quantityInput");

        let quantityCell = row.insertCell(); // Parent
        quantityCell.appendChild(quantityInput);

        // OPTIONS COLUMN

        var optionsCol = row.insertCell();

        // Create delete button
        var deleteButton = document.createElement('button');
        deleteButton.textContent = "Delete";
        // Using setAttribute to set onClick because .onclick was doing the function upon button creation
        deleteButton.setAttribute("onClick", `deleteListId(${itemId})`);

        optionsCol.appendChild(deleteButton);

        // Create purchse button
        var purchaseButton = document.createElement('button');
        purchaseButton.textContent = "Purchase";
        purchaseButton.setAttribute("onClick", `purchaseListId(\`${itemName}\`, ${itemId});`);

        optionsCol.appendChild(purchaseButton);
    }
}

async function deleteListId(id) {
    var bearer = 'Bearer ' + localStorage.getItem('access_token')
    await fetch(`/grocerylist/${id}`, {
        method: "DELETE",
        headers: {
            "Authorization": bearer
        }
    });
    getGroceryList();
}

async function purchaseListId(itemName, itemId) {
    const date_purchased = new Date().toISOString();
    const quantity = document.getElementById(String('quantityInputId' + itemId)).value;
    const body = {
        "item": itemName,
        "quantity": quantity,
        "date_purchased": date_purchased
    };

    var bearer = 'Bearer ' + localStorage.getItem('access_token')
    await fetch("/purchase", {
        method: "POST",
        body: JSON.stringify(body),
        headers: {
            "Content-type": "application/json; charset=UTF-8",
            "Authorization": bearer
        }
    });

    deleteListId(itemId);
}

async function getRecommendations() {
    var bearer = 'Bearer ' + localStorage.getItem('access_token')
    const response = await fetch("/recommendations", {
        headers: {
            "Authorization": bearer
        }
    });
    const data = await response.json();

    for (let r = 0; r < data.length; r++) {
        const itemRecommendation = data[r].recommendation

        // Convert to local time
        var lastPurchased = new Date(data[r].last_purchased).toLocaleString() + " UTC";
        var lastPurchasedLocalTime = new Date(lastPurchased).toString();
        var dateObjLastPurchasedLocalTime = new Date(lastPurchasedLocalTime);

        const secondsBetweenPurchases = data[r].average_seconds_between_purchases

        lastPurchased = lastPurchased.toString(); 
        
        const recommendationListTbodyRef = document.getElementById('recommendationList').getElementsByTagName('tbody')[0];

        let row = recommendationListTbodyRef.insertRow()
        
        // COLUMN: RECOMMENDATION ITEM NAME
        row.insertCell().textContent = `${itemRecommendation}`;

        // COLUMN: AVERAGE QUANTITY
        row.insertCell().textContent = `${data[r].average_quantity}`

        // COLUMN: LAST TIME PURCHASED
        row.insertCell().textContent = `${dateObjLastPurchasedLocalTime.toLocaleString()}`;

        var d = Math.floor(secondsBetweenPurchases / (3600*24));
        var h = Math.floor(secondsBetweenPurchases % (3600*24) / 3600);
        var m = Math.floor(secondsBetweenPurchases % 3600 / 60);

        var dDisplay = d > 0 ? d + (d == 1 ? " day, " : " days, ") : "";
        var hDisplay = h > 0 ? h + (h == 1 ? " hour, " : " hours, ") : "";
        var mDisplay = m > 0 ? m + (m == 1 ? " minute " : " minutes ") : "";

        timeDisplay = dDisplay + hDisplay + mDisplay;

        // COLUMN: FREQUENCY
        row.insertCell().textContent = `Every ${timeDisplay}`;

        // COLUMN: OPTIONS
        var addCol = row.insertCell();
        var addButton = document.createElement("Button");
        addButton.innerHTML = "Add to List";
        addButton.setAttribute("onclick", `sendToList('${itemRecommendation}')`)

        addCol.appendChild(addButton);
    }
}