from scripts import installer, network, reports, utils, alerts
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

        if config["import"]["enabled"]:
            utils.log_info("Importing data from CSV...")
            print("Importing data from CSV...")
            installer.import_data(installer.database_path, config["import"]["csv_path"])
            
        if config["export"]["enabled"]:
            utils.log_info("Exporting data to CSV...")
            print("Exporting data to CSV...")
            installer.export_data(installer.database_path, config["export"]["csv_path"])

        error_count = 0
        MAX_ERRORS = 5

        while True:
            try:
                await network.scan_network(installer.database_path, config["alerts"]["enabled"])
                utils.log_info(f"[{utils.get_current_time()}] Network scan completed. Generating report...")

                report_response = reports.generate_report(installer.database_path)
                if report_response["success"]:
                    utils.log_info(f"Report generated successfully: {report_response['message']}")
                else:
                    utils.log_error(f"Report generation failed: {report_response['message']}")

                utils.log_info(f"[{utils.get_current_time()}] Network scan completed. Sleeping for {config['interval']} seconds...")
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