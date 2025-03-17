
function launchGame() {
    let username = document.getElementById('username').value;
    if (!username) {
        alert("Введи нік!");
        return;
    }

    // Очищаємо старі логи
    document.getElementById('log').innerHTML = "<h2>Логи:</h2>";

    // Викликаємо Python-функцію
    eel.start_game(username)(function(response) {
        // Показуємо відповідь від Python
        addLog(response);
    });
}

function update_log(message) {
    let logDiv = document.getElementById('log');
    logDiv.innerHTML += `<p>${message}</p>`;
    logDiv.scrollTop = logDiv.scrollHeight;  // Прокручування до кінця
}
eel.expose(update_log);