eel.expose(updateJavaStatus);

function updateJavaStatus(isInstalled) {
    let launchBtn = document.getElementById("launchBtn");
    let warningText = document.getElementById("warning");

    if (isInstalled) {
        launchBtn.disabled = false;
        launchBtn.style.background = "linear-gradient(to right, #4dd0e1, #5e35b1)";
        launchBtn.style.cursor = "pointer";
        warningText.style.display = "none";
        addLog("✅ Java встановлена, можна запускати гру!");
    } else {
        launchBtn.disabled = true;
        launchBtn.style.backgroundColor = "#ff215c";
        launchBtn.style.cursor = "not-allowed";
        warningText.style.display = "block";
        addLog("⚠️ Java не знайдено! Спочатку встановіть її.");
    }
}

// Викликати перевірку Java при завантаженні сторінки
// window.onload = function() {
//     eel.is_java_installed()(updateJavaStatus);
// };

// function launchGame() {
//     let username = document.getElementById('username').value;
//     if (!username) {
//         alert("Введи нік!");
//         return;
//     }

//     // Очищаємо старі логи
//     document.getElementById('log').innerHTML = "<h2>Логи:</h2>";

    
// }

function update_log(message) {
    let logDiv = document.getElementById('log');
    logDiv.innerHTML += `<p>${message}</p>`;
    logDiv.scrollTop = logDiv.scrollHeight;  // Прокручування до кінця
}
eel.expose(update_log);
