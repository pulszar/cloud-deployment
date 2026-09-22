async function login() {
    const username = document.getElementById("uname");
    const password = document.getElementById("psw");

    console.log("sending login detailss");

    const response = await fetch('/token', {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: JSON.stringify({ 
            "username": username,
            "password": password
        })
    });
    const data = await response.json();

    window.localStorage.setItem("access_token", data.access_token);
}