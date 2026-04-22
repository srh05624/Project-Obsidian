from scripts import db, utils
import os

local_path = str(os.getenv('APPDATA') or os.path.expanduser('~'))
install_path = os.path.join(local_path, "ProjectObsidian")
log_directory = os.path.join(install_path, "logs")
reports_path = os.path.join(install_path, "reports")
config_path = os.path.join(install_path, "config.json")
database_path = os.path.join(install_path, "connections.db")

default_config = {
    "paths": {
        "install_directory": install_path,
        "log_directory": log_directory,
        "reports_directory": reports_path,
        "database_path": database_path,
    },
    "logging": {
        "directory": log_directory,
        "level": "INFO",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    },
    "alerts": {
        "enabled": True,
        "desktop": {
            "enabled": True,
            "app_name": "Project Obsidian",
            "icon_path": ""
        },
        "discord": {
            "enabled": True,
            "mention_role_id": ""
        }
        
    },
    "scan_ports_range": [1, 1024],
    "interval": 3600,
    "max_threads": 100,
    "force_stop": False,
    "full_scan": True,
    "report": True
}

# =====================================================
# Installation and Setup Functions
# =====================================================
def create_install_directory():
    try:
        if not os.path.exists(install_path):
            os.makedirs(install_path)
            return f"Installation directory created at: {install_path}", True
        return f"Installation directory already exists at: {install_path}", True
    except Exception as e:
        return f"Error creating installation directory: {str(e)}", False

def create_log_directory():
    try:
        if not os.path.exists(log_directory):
            os.makedirs(log_directory)
            return f"Log directory created at: {log_directory}", True
        return f"Log directory already exists at: {log_directory}", True
    except Exception as e:
        return f"Error creating log directory: {str(e)}", False

def create_reports_directory():
    try:
        if not os.path.exists(reports_path):
            os.makedirs(reports_path)
            return f"Reports directory created at: {reports_path}", True
        return f"Reports directory already exists at: {reports_path}", True
    except Exception as e:
        return f"Error creating reports directory: {str(e)}", False

def create_config_file():
    try:
        if not os.path.exists(config_path):
            utils.save_config(config_path, default_config)
            return f"Config file created at: {config_path}", True
        return f"Config file already exists at: {config_path}", True
    except Exception as e:
        return f"Error creating config file: {str(e)}", False

def results(msg, success, data={"success": True, "messages": []}):
    if not success:
        data["success"] = False
    data["messages"].append(msg)
    return data

def install():
    data = {"success": True, "messages": []}
    results(*create_install_directory(), data)
    results(*create_log_directory(), data)
    results(*create_reports_directory(), data)
    results(*create_config_file(), data)
    results(*db.create_database(default_config["paths"]["database_path"]), data)

    return data