from scripts import installer, network, utils
import time
from dotenv import load_dotenv

load_dotenv()

def main():
    current_time = utils.get_current_time()
    print(f"[{current_time}] Launching...")

    response = installer.install()
    config = utils.load_config(installer.config_path)
    
    for message in response["messages"]:
        if message:
            print("  > " + message)

    print(f"Installation {'succeeded' if response['success'] else 'failed'}.")
    
    if not response["success"]:
        print("Installation encountered errors, aborting.")
        return
    else:
        utils.setup_logging(installer.log_directory)
        utils.log_info("Installation completed successfully.")

        while True:
            current_time = utils.get_current_time()
            utils.log_info(f"[{current_time}] Starting network scan...")
            network.scan_network(installer.database_path)

            utils.log_info(f"[{current_time}] Network scan completed. Sleeping for {config['interval']} seconds...")
            print(f"Sleeping for {config['interval']} seconds...")
            time.sleep(config["interval"])

if __name__ == "__main__":
    main()