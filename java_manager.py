import os
import subprocess
import shutil
import zipfile
import requests
from logger import add_log

JAVA_URL = "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse?project=jdk"
JAVA_DIR = os.path.join(os.getcwd(), "jdk")  # Директорія для завантаження JDK

def get_java_path():
    """
    Повертає шлях до Java, якщо версія 21 встановлена.
    Спочатку перевіряє PATH, потім шукає в директорії лаунчера.
    """
    java_path = shutil.which("java")
    if java_path and check_java_version(java_path):
        add_log(f"✅ Java знайдена в PATH: {java_path}")
        return java_path

    try:
        jdk_subdir = next((name for name in os.listdir(JAVA_DIR) if name.startswith("jdk")), None)
        if jdk_subdir:
            potential_java = os.path.join(JAVA_DIR, jdk_subdir, "bin", "java.exe")
            if os.path.exists(potential_java) and check_java_version(potential_java):
                add_log(f"✅ Використовуємо Java з папки лаунчера: {potential_java}")
                return potential_java
    except FileNotFoundError:
        pass

    add_log("❌ Java 21 не знайдено!")
    return None

def check_java_version(java_path):
    """
    Перевіряє, чи відповідає версія Java потрібній (21).
    """
    try:
        result = subprocess.run(
            [java_path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output = result.stdout.strip() + result.stderr.strip()
        return "version \"21" in output  # Шукаємо рядок з "version 21"
    except FileNotFoundError:
        return False

def is_java_installed():
    """
    Експонується для Eel: перевіряє чи встановлена Java 21.
    """
    java_path = get_java_path()
    if java_path:
        add_log(f"✅ Java знайдено: {java_path}")
        return True
    add_log("❌ Java 21 не знайдено!")
    return False

def check_and_install_java():
    """
    Перевіряє наявність Java, а у разі її відсутності завантажує та встановлює OpenJDK.
    """
    if is_java_installed():
        add_log("✅ Java встановлена і працює.")
        try:
            import eel
            eel.updateJavaStatus(True)
        except Exception:
            pass
        return

    try:
        import eel
        eel.updateJavaStatus(False)
    except Exception:
        pass

    add_log("⚠️ Java не знайдено! Завантажуємо OpenJDK...")
    download_and_extract_java()

    if is_java_installed():
        add_log("✅ Java успішно встановлено!")
        try:
            import eel
            eel.updateJavaStatus(True)
        except Exception:
            pass
    else:
        add_log("❌ Помилка встановлення Java!")
        try:
            import eel
            eel.updateJavaStatus(False)
        except Exception:
            pass

def download_and_extract_java():
    """
    Завантажує архів з OpenJDK та розпаковує його у директорію JAVA_DIR.
    """
    java_zip = "java.zip"
    add_log(f"[INFO] Завантаження OpenJDK за адресою: {JAVA_URL}")

    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(JAVA_URL, headers=headers, stream=True)

    if response.status_code != 200:
        add_log(f"❌ Помилка завантаження JDK: {response.status_code} {response.reason}")
        return

    with open(java_zip, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
    add_log("[INFO] Завантажено!")

    add_log("[INFO] Розпаковка OpenJDK...")
    with zipfile.ZipFile(java_zip, "r") as zip_ref:
        zip_ref.extractall(JAVA_DIR)
    os.remove(java_zip)
    add_log(f"[INFO] OpenJDK розпаковано у: {JAVA_DIR}")

    # Додаємо Java до PATH
    jdk_subdir = next((name for name in os.listdir(JAVA_DIR) if name.startswith("jdk")), None)
    if not jdk_subdir:
        add_log(f"❌ Не знайдено підпапку JDK у: {JAVA_DIR}")
        return

    java_bin = os.path.join(JAVA_DIR, jdk_subdir, "bin")
    os.environ["PATH"] = java_bin + os.pathsep + os.environ["PATH"]
    add_log(f"✅ Java додано в PATH: {java_bin}")
