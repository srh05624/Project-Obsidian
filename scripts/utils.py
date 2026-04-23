import os, json, ctypes, logging
from datetime import datetime, timedelta

# ====================================================
# Administrative Privileges Check
# =====================================================
def is_admin():
    try:
        if os.name == 'nt':
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        else:
            return os.geteuid() == 0
    except Exception as e:
        logging.error(f"Admin check failed: {str(e)}")
        return False

# ====================================================
# Logging
# ====================================================
def setup_logging(log_dir):
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    log_file = os.path.join(log_dir, f"obsidian_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
    
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

def log_info(message):
    logging.info(message)

def log_warning(message):
    logging.warning(message)

def log_error(message):
    logging.error(message)

def log_debug(message):
    logging.debug(message)

# ====================================================
# Config Management
# ====================================================
def load_config(file_path):
    with open(file_path, 'r') as f:
        config = json.load(f)
    return config

def save_config(file_path, config):
    with open(file_path, 'w') as f:
        json.dump(config, f, indent=4)

# ====================================================
# Policy Management
# ====================================================
def load_policy(file_path):
    if not os.path.exists(file_path):
        return {"whitelist": [], "blacklist": []}
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_policy(file_path, data):
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

# ====================================================
# Utility Functions
# ====================================================
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_date():
    return datetime.now().strftime("%Y-%m-%d")

def get_time():
    return datetime.now().strftime("%H:%M:%S")

def get_deltatime():
    return datetime.now().isoformat()

def ignore_connection(ignored_on, offset_hours=1):
    if ignored_on:
        ignored_time = datetime.fromisoformat(ignored_on)
        if datetime.now() - ignored_time < timedelta(hours=offset_hours):
            log_info("  > Connection is currently ignored. Skipping alert.")
            return True
    return False

def directory_exists(path):
    return os.path.isdir(path)

def file_exists(path):
    return os.path.isfile(path)