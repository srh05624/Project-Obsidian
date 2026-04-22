import asyncio
from scripts import network, utils, db
from win11toast import toast_async

seen_alerts = set()
pending_actions = {}


async def alert_user(msg):
    clicked = asyncio.get_running_loop().create_future()

    def on_click(args):
        try:
            print("raw args:", args)

            # win11toast often returns something like "http:Button A"
            raw = args.get("arguments", "")
            choice = raw.split(":", 1)[-1] if ":" in raw else raw

            if not clicked.done():
                clicked.set_result(choice)

        except Exception as e:
            if not clicked.done():
                clicked.set_exception(e)

    try:
        await toast_async(
            "Suspicious Process Found!",
            msg,
            buttons=["Whitelist", "Blacklist", "Kill Once"],
            on_click=on_click
        )

        response = await clicked
        utils.log_info(f"User interaction: {response}")
        return response

    except Exception as e:
        utils.log_error(f"Error showing alert: {e}")
        return None

async def main():
    while True:
        suspicious_connections = db.fetch_suspicious_connections(db_path=db.db_path)
        if suspicious_connections is not None and len(suspicious_connections) > 0:
            try:
                for process in suspicious_connections:
                    key = process["name"] + ":" + str(process["pid"])

                    if key in seen_alerts:
                        continue

                    seen_alerts.add(key)

                    msg = f"Suspicious connection detected**\n"
                    msg += f"Process: {process['name']}\n"
                    msg += f"PID: {process['pid']}\n"
                    msg += f"Path: `{process['path']}`\n"
                    msg += f"Remote: `{process['remote_ip']}:{process['remote_port']}`\n"

                    choice = await alert_user(msg)

                    if choice == "Whitelist":
                        db.update_connection(db.db_path, process["name"], blacklisted=0, whitelisted=1)
                    elif choice == "Blacklist":
                        db.update_connection(db.db_path, process["name"], blacklisted=1, whitelisted=0)
                    elif choice == "Kill Once":
                        db.update_connection(db.db_path, process["name"], blacklisted=0, whitelisted=0)
                        network.kill_process(process["pid"])

            except Exception as e:
                utils.log_error(f"Error in alert system: {str(e)}")
                print(f"Error in alert system: {str(e)}")
        await asyncio.sleep(300)