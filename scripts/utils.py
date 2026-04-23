import os
import json
import logging
from datetime import datetime

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

def check_memory():
    memory_file = "memory.json"
    if not os.path.exists(memory_file):
        memory = {
            "whitelisted": [],
            "blacklisted": [],
            "unknown": []
        }
        with open(memory_file, 'w') as f:
            json.dump(memory, f, indent=4)
    else:
        with open(memory_file, 'r') as f:
            memory = json.load(f)
    return memory

def generate_report(dir ,data):
    report_dir = dir
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    file_path = os.path.join(report_dir, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")

    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

def is_windows_process(process_path):
    """
    Checks if a process path belongs to a core Windows system directory.
    """
    if not process_path:
        return False

    # Normalize the path for consistent comparison
    normalized_path = os.path.normcase(process_path)
    
    # Define common Windows system directories
    system_dirs = [
        os.path.normcase(r'C:\Windows\System32'),
        os.path.normcase(r'C:\Windows\SysWOW64'),
        os.path.normcase(r'C:\Windows\explorer.exe'), # Explorer is a core process
        os.path.normcase(r'C:\Windows\smss.exe'), # Session Manager Subsystem
        os.path.normcase(r'C:\Windows\csrss.exe'), # Client Server Runtime Process
        os.path.normcase(r'C:\Windows\wininit.exe'), # Windows Initialization Process
        os.path.normcase(r'C:\Windows\services.exe'), # Service Control Manager
        # Add other specific core processes if needed
    ]

    for directory in system_dirs:
        if normalized_path.startswith(directory):
            return True
            
    # Heuristic check for general program files location (likely not a core Windows process)
    if normalized_path.startswith(os.path.normcase(r'C:\Program Files')) or \
       normalized_path.startswith(os.path.normcase(r'C:\Program Files (x86)')) or \
       os.path.normcase(r'C:\Users') in normalized_path: # User-installed or background processes
        return False
        
    return False # Default to False if path doesn't clearly indicate system ownership