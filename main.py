import utils
import logger
import network
import time
from datetime import datetime

config = utils.load_config('config.json')
logging = logger.setup_logger(config["log_directory"] + utils.get_current_time().replace(":", "-") + '.log')

open_ports = []
connections = {}

whitelisted_ports = []
blacklisted_ports = []

known_connections = []
suspicious_connections = []

def monitor():
    while True:
        current = network.get_listeners()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        for item in current:
            key = (item["ip"], item["port"], item["pid"])
            if key not in known_connections:
                known_connections.append(key)

                suspicious = item["port"] not in whitelisted_ports
                tag = "SUSPICIOUS" if suspicious else "INFO"

                if utils.is_windows_process(item["exe"]):
                    tag = "WINDOWS_PROCESS"
                
                print(
                    f"[{now}] [{tag}] "
                    f"{item['ip']}:{item['port']} | PID={item['pid']} | "
                    f"{item['name']} | {item['exe']}"
                )
                if suspicious:
                    suspicious_connections.append(key)

        time.sleep(5)

if __name__ == "__main__":
    monitor()