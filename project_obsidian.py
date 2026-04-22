from scripts import installer, network, utils, alerts
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
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

        if config["alerts"]["enabled"]:
            utils.log_info("Starting alert system...")
            print("Starting alert system...")

            if config["alerts"]["discord"]["enabled"]:
                asyncio.create_task(alerts.main())
            else:
                utils.log_info("Discord alerts are disabled in the configuration.")

        error_count = 0
        MAX_ERRORS = 5

        while True:
            try:
                current_time = utils.get_current_time()
                utils.log_info(f"[{current_time}] Starting network scan...")
                network.scan_network(installer.database_path)

                utils.log_info(f"[{current_time}] Network scan completed. Sleeping for {config['interval']} seconds...")
                print(f"Sleeping for {config['interval']} seconds...")

                await asyncio.sleep(config["interval"])

            except Exception as e:
                utils.log_error(f"Error during main loop: {str(e)}")
                error_count += 1
                if error_count >= MAX_ERRORS:
                    utils.log_error("Maximum error limit reached. Exiting...")
                    break
            finally:
                utils.log_info(f"[{utils.get_current_time()}] Main loop iteration completed.")

            

if __name__ == "__main__":
    asyncio.run(main())