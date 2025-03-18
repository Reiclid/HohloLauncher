// Language translations
const translations = {
    uk: {
        "server-title": "Наш ігровий сервер",
        "server-content-1": "Виживання в обмеженому світі з елементами політики та стратегії. Кожен гравець може зайняти одну територію, яку може розвивати, захищати та використовувати для дипломатичних або військових цілей.",
        "server-content-2": "Можливість створювати союзи та брати участь у територіальних конфліктах робить гру динамічною, а обмеженість ресурсів посилює конкуренцію та стратегічне планування.",
        "features-title": "Особливості сервера:",
        "feature-1": "Унікальні ігрові режими(война)",
        "feature-2": "Система досягнень та нагород(хахахаха мне лень делать)",
        "feature-3": "Дружня спільнота та активна команда модераторів(аххахахахахах)",
        "feature-4": "Спеціальні можливості для преміум-гравців(ДОНАТ!!!)",
        "username-placeholder": "Введи нік",
        "launch-btn": "Запуск гри",
        "java-warning": "⚠️ Java не знайдено! Дочекайтесь поки ми її встановимо.",
        "logs-title": "Логи:",
        "logs-ready": "Система готова до запуску..."
    },
    ru: {
        "server-title": "Наш игровой сервер",
        "server-content-1": "Выживание в ограниченном мире с элементами политики и стратегии. Каждый игрок может занять одну территорию, которую может развивать, защищать и использовать для дипломатических или военных целей.",
        "server-content-2": "Возможность создавать союзы и участвовать в территориальных конфликтах делает игру динамичной, а ограниченность ресурсов усиливает конкуренцию и стратегическое планирование.",
        "features-title": "Особенности сервера:",
        "feature-1": "Уникальные игровые режимы(война)",
        "feature-2": "Система достижений и наград(хахахаха мне лень делать)",
        "feature-3": "Дружественное сообщество и активная команда модераторов(аххахахахахах)",
        "feature-4": "Специальные возможности для премиум-игроков(ДОНАТ!!!)",
        "username-placeholder": "Введи ник",
        "launch-btn": "Запуск игры",
        "java-warning": "⚠️ Java не найдена! Дождитесь, пока мы её установим.",
        "logs-title": "Логи:",
        "logs-ready": "Система готова к запуску..."
    },
    en: {
        "server-title": "Our Game Server",
        "server-content-1": "Survival in a limited world with elements of politics and strategy. Each player can occupy one territory, which they can develop, protect, and use for diplomatic or military purposes.",
        "server-content-2": "The ability to create alliances and participate in territorial conflicts makes the game dynamic, while limited resources enhance competition and strategic planning.",
        "features-title": "Server Features:",
        "feature-1": "Unique game modes(war)",
        "feature-2": "Achievement and reward system(hahahaha I'm too lazy to make)",
        "feature-3": "Friendly community and active moderator team(ahhahahahahahah)",
        "feature-4": "Special features for premium players(DONATE!!!)",
        "username-placeholder": "Enter nickname",
        "launch-btn": "Launch Game",
        "java-warning": "⚠️ Java not found! Please wait while we install it.",
        "logs-title": "Logs:",
        "logs-ready": "System ready to launch..."
    },
    cs: {
        "server-title": "Náš herní server",
        "server-content-1": "Přežití v omezeném světě s prvky politiky a strategie. Každý hráč může obsadit jedno území, které může rozvíjet, chránit a používat pro diplomatické nebo vojenské účely.",
        "server-content-2": "Možnost vytvářet aliance a účastnit se územních konfliktů činí hru dynamickou, zatímco omezené zdroje zvyšují konkurenci a strategické plánování.",
        "features-title": "Funkce serveru:",
        "feature-1": "Unikátní herní režimy(válka)",
        "feature-2": "Systém úspěchů a odměn(hahahaha jsem příliš líný na to, abych to udělal)",
        "feature-3": "Přátelská komunita a aktivní tým moderátorů(ahhahahahahahah)",
        "feature-4": "Speciální funkce pro prémiové hráče(DAROVAT!!!)",
        "username-placeholder": "Zadejte přezdívku",
        "launch-btn": "Spustit hru",
        "java-warning": "⚠️ Java nebyla nalezena! Počkejte prosím, než ji nainstalujeme.",
        "logs-title": "Protokoly:",
        "logs-ready": "Systém připraven ke spuštění..."
    }
};

// Function to change language
function changeLanguage(lang) {
    // Save selected language to local storage
    localStorage.setItem('selectedLanguage', lang);
    
    // Update active button
    document.querySelectorAll('.lang-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('data-lang') === lang) {
            btn.classList.add('active');
        }
    });
    
    // Update text content for all elements with data-lang-key attribute
    document.querySelectorAll('[data-lang-key]').forEach(element => {
        const key = element.getAttribute('data-lang-key');
        if (translations[lang] && translations[lang][key]) {
            if (element.tagName === 'INPUT') {
                element.placeholder = translations[lang][key];
            } else {
                element.textContent = translations[lang][key];
            }
        }
    });
    
    // Set html lang attribute
    document.documentElement.lang = lang;
}

// Add click event listeners to language buttons
document.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', function() {
        const lang = this.getAttribute('data-lang');
        changeLanguage(lang);
    });
});

// Load saved language preference or default to Ukrainian
document.addEventListener('DOMContentLoaded', function() {
    const savedLang = localStorage.getItem('selectedLanguage') || 'uk';
    changeLanguage(savedLang);
});

// Your existing game launch function
function launchGame() {
    const username = document.getElementById('username').value;
    if (!username) {
        const lang = localStorage.getItem('selectedLanguage') || 'uk';
        let errorMsg = "Будь ласка, введіть нік!";
        
        if (lang === 'ru') errorMsg = "Пожалуйста, введите ник!";
        if (lang === 'en') errorMsg = "Please enter a nickname!";
        if (lang === 'cs') errorMsg = "Zadejte prosím přezdívku!";
        
        alert(errorMsg);
        return;
    }
    
    const log = document.getElementById('log');
    const logMsg = document.createElement('div');
    
    const lang = localStorage.getItem('selectedLanguage') || 'uk';
    let msg = "Запуск гри для користувача: " + username;
    
    if (lang === 'ru') msg = "Запуск игры для пользователя: " + username;
    if (lang === 'en') msg = "Launching game for user: " + username;
    if (lang === 'cs') msg = "Spouštění hry pro uživatele: " + username;
    
    logMsg.textContent = msg;
    log.appendChild(logMsg);
    
    // Your existing game launch code
    // eel.launch_game(username)...
}