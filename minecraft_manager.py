import os
import json
import urllib.request
import requests
import shutil
from logger import add_log
from java_manager import get_java_path

# Константи для Minecraft
MINECRAFT_DIR = os.path.abspath(".")
VERSIONS_DIR = os.path.join(MINECRAFT_DIR, "versions")
LIBRARIES_DIR = os.path.join(MINECRAFT_DIR, "libraries")

VERSION = "1.21.4"
FABRIC_LOADER = "0.16.10"

def download_file(url, save_path):
    """
    Завантажує файл за вказаною URL та зберігає його за шляхом save_path.
    """
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    response = requests.get(url)
    with open(save_path, 'wb') as f:
        f.write(response.content)
    add_log(f"Завантажено {save_path}")

def download_folder(folder):
    """
    Завантажує вміст папки з GitHub репозиторію.
    """
    repo_url = "https://api.github.com/repos/Reiclid/HohloLauncher/contents/{folder}?ref=lib-msr"
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
    """
    Завантажує файли Minecraft (jar, json, бібліотеки) для вказаної версії.
    """
    version_manifest_path = os.path.join(MINECRAFT_DIR, "version_manifest_v2.json")
    with open(version_manifest_path, "r") as f:
        version_manifest = json.load(f)

    version_data = next(v for v in version_manifest["versions"] if v["id"] == VERSION)
    version_url = version_data["url"]

    add_log(f"Завантажую: {version_url}")
    version_dir = os.path.join(VERSIONS_DIR, VERSION)
    os.makedirs(version_dir, exist_ok=True)
    version_json_path = os.path.join(version_dir, f"{VERSION}.json")
    urllib.request.urlretrieve(version_url, version_json_path)

    with open(version_json_path, "r") as f:
        version_detail = json.load(f)

    client_url = version_detail["downloads"]["client"]["url"]
    download_file(client_url, os.path.join(version_dir, f"{VERSION}.jar"))

    # Завантаження бібліотек
    for lib in version_detail["libraries"]:
        artifact = lib.get("downloads", {}).get("artifact")
        if artifact:
            lib_path = os.path.join(LIBRARIES_DIR, artifact["path"])
            if not os.path.exists(lib_path):
                download_file(artifact["url"], lib_path)

def ensure_fabric_version():
    """
    Завантажує профіль Fabric Loader та відповідні бібліотеки.
    """
    fabric_version_name = f"fabric-loader-{FABRIC_LOADER}-{VERSION}"
    fabric_dir = os.path.join(VERSIONS_DIR, fabric_version_name)
    os.makedirs(fabric_dir, exist_ok=True)
    fabric_profile_path = os.path.join(fabric_dir, f"{fabric_version_name}.json")
    
    if not os.path.exists(fabric_profile_path):
        add_log("⚙️ Завантаження Fabric Loader...")
        fabric_meta_url = f"https://meta.fabricmc.net/v2/versions/loader/{VERSION}/{FABRIC_LOADER}/profile/json"
        with urllib.request.urlopen(fabric_meta_url) as response:
            fabric_meta = json.loads(response.read().decode())
        
        with open(fabric_profile_path, "w") as f:
            json.dump(fabric_meta, f, indent=4)
        
        # Завантаження бібліотек з профілю Fabric
        for lib in fabric_meta["libraries"]:
            artifact = lib.get("downloads", {}).get("artifact")
            if artifact:
                lib_path = os.path.join(LIBRARIES_DIR, artifact["path"])
                if not os.path.exists(lib_path):
                    download_file(artifact["url"], lib_path)
    
    return fabric_version_name, fabric_profile_path

def start_game(username):
    """
    Готує середовище та запускає гру.
    """
    add_log("Початок завантаження гри...")

    # Завантаження додаткових папок (mods, resourcepacks, shaderpacks)
    for folder in ["mods", "resourcepacks", "shaderpacks"]:
        os.makedirs(folder, exist_ok=True)
        download_folder(folder)

    # Записуємо конфігураційний файл
    config = {
        "server_ip": "play.example.com",
        "server_port": "25565"
    }
    with open('config.json', 'w') as f:
        json.dump(config, f)

    # Перевірка наявності Minecraft версії
    mc_version_dir = os.path.join(VERSIONS_DIR, VERSION)
    mc_jar_path = os.path.join(mc_version_dir, f"{VERSION}.jar")
    if not os.path.exists(mc_jar_path):
        ensure_minecraft_version()

    fabric_version_name, fabric_profile_path = ensure_fabric_version()

    # Збір бібліотек (включаючи Minecraft jar)
    all_libs = {}
    for root, _, files in os.walk(LIBRARIES_DIR):
        for file in files:
            if file.endswith(".jar"):
                name, _, ver = file.rpartition("-")
                ver = ver.replace(".jar", "")
                if name not in all_libs or ver > all_libs[name][1]:
                    all_libs[name] = (os.path.join(root, file), ver)

    libs = [item[0] for item in all_libs.values()]
    libs.append(mc_jar_path)
    classpath = ";".join(libs)

    # Завантаження головного класу з профілю Fabric Loader
    with open(fabric_profile_path, "r") as f:
        fabric_profile = json.load(f)
    main_class = fabric_profile["mainClass"]

    # Налаштування аргументів JVM та Minecraft
    JVM_ARGS = [
        "-Xmx8G", "-Xms2G",
        "-cp", classpath,
        "-Dlog4j2.formatMsgNoLookups=true",
        "-Dlog4j.configurationFile=log4j2.xml",
        "-Dlog4j2.level=ERROR"
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
        "--quickPlayMultiplayer", "51.195.61.129:25614"
    ]
    JVM_ARGS.append("-Dlog4j2.formatMsgNoLookups=true")
    MC_ARGS.append("--nogui")

    java_executable = get_java_path()
    if not java_executable:
        add_log("❌ Не вдалося знайти Java!")
        return
    args = [java_executable] + JVM_ARGS + MC_ARGS
    add_log(f"Команда запуску: {' '.join(args)}")

    # Запуск процесу гри
    import subprocess
    subprocess.Popen(args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                     creationflags=subprocess.CREATE_NO_WINDOW)
    add_log(f"✅ Гра запускається як {username}!")
