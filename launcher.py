import eel
import os
import json
import subprocess
import urllib.request
import requests

eel.init('web')

VERSION = "1.21.4"
FABRIC_LOADER = "0.16.10"
MINECRAFT_DIR = os.path.abspath(".")
VERSIONS_DIR = os.path.join(MINECRAFT_DIR, "versions")
LIBRARIES_DIR = os.path.join(MINECRAFT_DIR, "libraries")

# Функція для відправлення логів
@eel.expose
def add_log(message):
    print(message)  # Логування в консоль
    eel.update_log(message)  # Виклик функції з JS

# URL для отримання вмісту файлів з GitHub репозиторію
repo_url = "https://api.github.com/repos/Reiclid/HohloLauncher/contents/{folder}?ref=lib-msr"

def download_file(url, save_path):
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
            "-cp", classpath
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

        # Остаточна команда
        ARGS = ["java"] + JVM_ARGS + MC_ARGS

        add_log(f"Команда запуску: {' '.join(ARGS)}")

        subprocess.Popen(ARGS)
        add_log(f"✅ Гра запускається як {username}!")

    except Exception as e:
        add_log(f"❌ Сталася помилка: {str(e)}")

# Запуск GUI
eel.start('index.html', size=(700, 700))
