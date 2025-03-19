import eel

def add_log(message):
    """
    Логування повідомлень у консоль та відправка їх у JS.
    """
    print(message)
    try:
        eel.update_log(message)
    except Exception:
        pass
