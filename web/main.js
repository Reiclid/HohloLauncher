function launchGame() {
    let username = document.getElementById('username').value;
    if (!username) {
        alert("Введи нік!");
        return;
    }

    eel.start_game(username)(function(response) {
        alert(response);
    });
}
