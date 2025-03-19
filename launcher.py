import eel
import os
import json
import subprocess
import urllib.request
import requests
import zipfile
import shutil
import threading
import tkinter as tk
from ctypes import windll

eel.init('web')

# root = tk.Tk()
# root.withdraw()
# icon_path = os.path.abspath("icon.ico")

# # Перевіряємо, чи існує іконка
# if os.path.exists(icon_path):
#     root.iconbitmap(icon_path)  # Іконка для Tkinter
#     windll.shell32.SetCurrentProcessExplicitAppUserModelID("mycompany.myapp") 

VERSION = "1.21.4"
FABRIC_LOADER = "0.16.10"
MINECRAFT_DIR = os.path.abspath(".")
VERSIONS_DIR = os.path.join(MINECRAFT_DIR, "versions")
LIBRARIES_DIR = os.path.join(MINECRAFT_DIR, "libraries")

JAVA_URL = "https://api.adoptium.net/v3/binary/latest/21/ga/windows/x64/jdk/hotspot/normal/eclipse?project=jdk"
JAVA_DIR = os.path.join(os.getcwd(), "jdk")  # Куди розпаковувати JDK

def get_java_path():
    """Знаходить шлях до Java, якщо вона встановлена."""
    java_path = shutil.which("java")
    
    # Перевіряємо PATH, якщо java не знайдено, шукаємо в нашій теці JDK
    if not java_path:
        potential_java = os.path.join(JAVA_DIR, "jdk-21.0.6+7", "bin", "java.exe")
        if os.path.exists(potential_java):
            return potential_java
        return None
    return java_path

@eel.expose
def is_java_installed():
    """Перевіряє, чи встановлена Java та чи правильно працює."""
    java_path = get_java_path()

    if not java_path:
        print("❌ Java не знайдено у PATH.")
        return False

    try:
        result = subprocess.run(
            [java_path, "-version"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        output = result.stdout.strip() + result.stderr.strip()
        if "version" in output and "21" in output:
            add_log(f"✅ Java знайдено: {java_path}")
            add_log(f"📌 Версія: {output.splitlines()[0]}")
            return True
        else:
            add_log("⚠️ Java є, але версія не підходить!")
            add_log(f"🔍 Вивід: {output}")
            return False

    except FileNotFoundError:
        add_log("❌ Java не знайдено!")
        return False

@eel.expose
def check_and_install_java():
    """Перевіряє та встановлює Java після запуску вікна."""
    if is_java_installed():
        add_log("✅ Java встановлена і працює.")
        eel.updateJavaStatus(True)
        return
        
    eel.updateJavaStatus(False)
    add_log("⚠️ Java не знайдено! Завантажуємо OpenJDK...")
    download_and_extract_java()
    
    if is_java_installed():
        add_log("✅ Java успішно встановлено!")
        eel.updateJavaStatus(True)
    else:
        add_log("❌ Помилка встановлення Java!")
        eel.updateJavaStatus(False)

def download_and_extract_java():
    """Завантаження та встановлення OpenJDK."""
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

    # Пошук підпапки jdk-*
    jdk_subdir = next((name for name in os.listdir(JAVA_DIR) if name.startswith("jdk")), None)

    if not jdk_subdir:
        add_log("❌ Не знайдено підпапку JDK у:", JAVA_DIR)
        return

    java_bin = os.path.join(JAVA_DIR, jdk_subdir, "bin")
    os.environ["PATH"] = java_bin + os.pathsep + os.environ["PATH"]
    add_log(f"✅ Java додано в PATH: {java_bin}")


# Функція для відправлення логів
@eel.expose
def add_log(message):
    print(message)  # Логування в консоль
    eel.update_log(message)  # Виклик функції з JS

# URL для отримання вмісту файлів з GitHub репозиторію
repo_url = "https://api.github.com/repos/Reiclid/HohloLauncher/contents/{folder}?ref=lib-msr"

def download_file(url, save_path):
    os.makedirs(os.path.dirname(save_path), exist_ok=True)  # Створюємо всі потрібні папки
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    add_log(f"Завантажено {save_path}")  # Додаємо лог


def download_folder(folder):
    folder_url = repo_url.format(folder=folder)
    response = requests.get(folder_url)
    
    if response.status_code == 200:
        files = response.json()
        for file in files:
            if file['type'] == 'file':
                target = os.path.join(folder, file['name'])
                if os.path.exists(target):
                    add_log(f"{target} вже існує, пропускаю...")
                else:
                    download_file(file['download_url'], target)
            else:
                add_log(f"Пропущено {file['name']} (не файл).")
    else:
        add_log(f"❌ Помилка при отриманні вмісту для {folder}: {response.status_code}")

def ensure_minecraft_version():
    version_manifest_path = os.path.join(MINECRAFT_DIR, "version_manifest_v2.json")
    with open(version_manifest_path, "r") as f:
        version_manifest = json.load(f)

    version_data = next(v for v in version_manifest["versions"] if v["id"] == VERSION)
    version_url = version_data["url"]

    add_log(f"Завантажую: {version_url}")
    os.makedirs(os.path.join(VERSIONS_DIR, VERSION), exist_ok=True)
    urllib.request.urlretrieve(version_url, f"{VERSIONS_DIR}/{VERSION}/{VERSION}.json")

    with open(f"{VERSIONS_DIR}/{VERSION}/{VERSION}.json") as f:
        version_detail = json.load(f)

    client_url = version_detail["downloads"]["client"]["url"]
    download_file(client_url, f"{VERSIONS_DIR}/{VERSION}/{VERSION}.jar")

    # Завантаження бібліотек
    for lib in version_detail["libraries"]:
        artifact = lib.get("downloads", {}).get("artifact")
        if artifact:
            lib_path = os.path.join(LIBRARIES_DIR, artifact["path"])
            if not os.path.exists(lib_path):
                download_file(artifact["url"], lib_path)

def ensure_fabric_version():
    fabric_version_name = f"fabric-loader-{FABRIC_LOADER}-{VERSION}"
    fabric_profile_path = os.path.join(VERSIONS_DIR, fabric_version_name, f"{fabric_version_name}.json")
    
    if not os.path.exists(fabric_profile_path):
        add_log("⚙️ Завантаження Fabric Loader...")
        fabric_meta_url = f"https://meta.fabricmc.net/v2/versions/loader/{VERSION}/{FABRIC_LOADER}/profile/json"
        with urllib.request.urlopen(fabric_meta_url) as response:
            fabric_meta = json.loads(response.read().decode())

        os.makedirs(os.path.join(VERSIONS_DIR, fabric_version_name), exist_ok=True)
        with open(fabric_profile_path, "w") as f:
            json.dump(fabric_meta, f, indent=4)

        # Завантаження бібліотек
        for lib in fabric_meta["libraries"]:
            artifact = lib.get("downloads", {}).get("artifact")
            if artifact:
                lib_path = os.path.join(LIBRARIES_DIR, artifact["path"])
                if not os.path.exists(lib_path):
                    download_file(artifact["url"], lib_path)

    return fabric_version_name, fabric_profile_path  # Ім'я версії і шлях до профілю



@eel.expose
def start_game(username):
    try:

        add_log("Початок завантаження гри...")

        # Завантаження файлів з GitHub тільки при натисканні кнопки
        directories = ["mods", "resourcepacks", "shaderpacks"]
        for folder in directories:
            if not os.path.exists(folder):
                os.makedirs(folder)
            download_folder(folder)

        config = {
            "server_ip": "play.example.com",
            "server_port": "25565"
        }
        with open('config.json', 'w') as f:
            json.dump(config, f)

        # Перевірка Minecraft та Fabric
        mc_jar_path = os.path.join(VERSIONS_DIR, VERSION, f"{VERSION}.jar")
        if not os.path.exists(mc_jar_path):
            ensure_minecraft_version()

        fabric_version_name, fabric_profile_path = ensure_fabric_version()

        # Збір бібліотек
        all_libs = {}
        for root, _, files in os.walk(LIBRARIES_DIR):
            for file in files:
                if file.endswith(".jar"):
                    name = file.rsplit("-", 1)[0]
                    version = file.rsplit("-", 1)[1].replace(".jar", "")
                    if name not in all_libs or version > all_libs[name][1]:
                        all_libs[name] = (os.path.join(root, file), version)

        libs = [item[0] for item in all_libs.values()]
        libs.append(mc_jar_path)  # Додаємо лише Minecraft .jar

        # Classpath
        classpath = ";".join(libs)

        # Головний клас з профілю Fabric
        with open(fabric_profile_path, "r") as f:
            fabric_profile = json.load(f)
        main_class = fabric_profile["mainClass"]  # це net.fabricmc.loader.impl.launch.knot.KnotClient

        # JVM та Minecraft аргументи
        JVM_ARGS = [
            "-Xmx8G", "-Xms2G",
            "-cp", classpath,
            "-Dlog4j2.formatMsgNoLookups=true",  # ✅ Відключення зайвих логів
            "-Dlog4j.configurationFile=log4j2.xml",  # Додає конфігурацію log4j, якщо у тебе є такий файл
            "-Dlog4j2.level=ERROR"  # Зменшує рівень логування
        ]
        MC_ARGS = [
            main_class,
            "--username", username,
            "--version", fabric_version_name,
            "--gameDir", MINECRAFT_DIR,
            "--assetsDir", os.path.join(MINECRAFT_DIR, "assets"),
            "--assetIndex", "1.21",
            "--accessToken", "0",
            "--uuid", "0",
            "--userType", "legacy",
            "--quickPlayMultiplayer", "51.195.61.129:25614"  # ✅ Автопідключення
        ]

        JVM_ARGS.append("-Dlog4j2.formatMsgNoLookups=true")
        MC_ARGS.append("--nogui")


        # Остаточна команда
        ARGS = ["java"] + JVM_ARGS + MC_ARGS

        add_log(f"Команда запуску: {' '.join(ARGS)}")

        subprocess.Popen(ARGS, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, creationflags=subprocess.CREATE_NO_WINDOW)

        add_log(f"✅ Гра запускається як {username}!")

    except Exception as e:
        add_log(f"❌ Сталася помилка: {str(e)}")

# 🚀 Запускаємо GUI без блокування
eel.start('index.html', size=(1100, 700), block=False)

# ✅ Запускаємо перевірку Java у фоновому потоці
threading.Thread(target=check_and_install_java, daemon=True).start()

# 🎉 Основний цикл (щоб Python не закінчувався)
while True:
    eel.sleep(1)