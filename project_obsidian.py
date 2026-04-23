import asyncio
from dotenv import load_dotenv
from scripts import installer, network, reports, utils

load_dotenv()

async def main():
    current_time = utils.get_current_time()
    print(f"[{current_time}] Launching...")

    if not utils.is_admin():
        print("This application requires administrative privileges. Please run as administrator.")
        return

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
            installer.import_data(config["import"]["csv_path"])
            
        if config["export"]["enabled"]:
            utils.log_info("Exporting data to CSV...")
            print("Exporting data to CSV...")
            installer.export_data(config["export"]["csv_path"])

        error_count = 0
        MAX_ERRORS = 5

        while True:
            try:
                await network.scan_network(config)
                utils.log_info(f" Network scan completed. Generating report...")

                report_response = reports.generate_report()
                if report_response["success"]:
                    utils.log_info(f"Report generated successfully: {report_response['message']}")
                else:
                    utils.log_error(f"Report generation failed: {report_response['message']}")

                utils.log_info(f" Network scan completed. Sleeping for {config['interval']} seconds...")
                print(f"Sleeping for {config['interval']} seconds...")

                await asyncio.sleep(config["interval"])

            except Exception as e:
                utils.log_error(f"Error during main loop: {str(e)}")
                error_count += 1
                if error_count >= MAX_ERRORS:
                    utils.log_error("Maximum error limit reached. Exiting...")
                    break
            finally:
                utils.log_info(f" Main loop iteration completed.")

if __name__ == "__main__":
    asyncio.run(main())