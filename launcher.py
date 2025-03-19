import threading
import eel
from java_manager import check_and_install_java, is_java_installed
from minecraft_manager import start_game
from logger import add_log

# Ініціалізація Eel з папки веб-ресурсів
eel.init('web')

# Експонуємо функцію запуску гри для JS
@eel.expose
def startGame(username):
    try:
        start_game(username)
        return {"status": "ok"}  # або просто True
    except Exception as e:
        add_log("❌ Помилка: " + str(e))
        return {"status": "error", "message": str(e)}

# Експонуємо функцію перевірки Java для JS
@eel.expose
def isJavaInstalled():
    return is_java_installed()

def main():
    # Запускаємо GUI Eel (не блокуючи основний потік)
    eel.start('index.html', size=(1100, 700), block=False)
    
    # Запускаємо перевірку та встановлення Java у фоновому потоці
    threading.Thread(target=check_and_install_java, daemon=True).start()

    # Основний цикл для підтримки роботи Python-процесу
    while True:
        eel.sleep(1)

if __name__ == '__main__':
    main()
