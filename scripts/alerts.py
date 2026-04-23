import asyncio
from scripts import utils
from win11toast import toast_async

seen_alerts = set()
pending_actions = {}


async def alert_user(msg):
    clicked = asyncio.get_running_loop().create_future()

    def on_click(args):
        try:
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