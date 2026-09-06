async function greet() {
    const userInput = document.getElementById("userInput").value; // Get input
    console.log(userInput);
    const result = await fetch(`/greet/${userInput}`); // Send to server, get response
    console.log(result);
    const data = await result.json();
    document.getElementById("serverResponse").textContent = data.message; // Set placeholder element
}