import asyncio
from scripts import utils
from win11toast import toast_async

seen_alerts = set()
last_alert_time = {}

timer = 600 # Time to wait before allowing another alert for the same process (in seconds)

async def alert_user(msg):
    clicked = asyncio.get_running_loop().create_future()

    if msg in seen_alerts and msg in last_alert_time:
        elapsed_time = asyncio.get_event_loop().time() - last_alert_time[msg]
        if elapsed_time < timer:
            utils.log_info(f"Alert for '{msg}' already shown. Waiting for {timer - elapsed_time} seconds before allowing another alert.")
            return None
        else:
            seen_alerts.remove(msg)
            last_alert_time.pop(msg, None)
            utils.log_info(f"Alert for '{msg}' is now allowed again.")
    
    seen_alerts.add(msg)
    last_alert_time[msg] = asyncio.get_event_loop().time()

    def on_click(args):
        try:
            raw = args.get("arguments", "")
            choice = raw.split(":", 1)[-1] if ":" in raw else raw

            if not clicked.done():
                clicked.set_result(choice)

        except Exception as e:
            if not clicked.done():
                utils.log_error(f"Error in on_click handler: {e}")
                clicked.set_exception(e)

    try:
        await toast_async(
            "Suspicious Process Found!",
            msg,
            buttons=["Whitelist", "Blacklist", "Kill Once", "Ignore"],
            on_click=on_click
        )
        
        if not clicked.done():
            clicked.set_result("TIMED_OUT")

        response = await asyncio.wait_for(clicked, timeout=10)
        utils.log_info(f"User interaction: {response}")
        return response

    except Exception as e:
        utils.log_error(f"Error showing alert: {e}")
        return None