from plyer import notification
import discord, os
from discord.ext import commands

TOKEN = os.getenv("DISCORD_BOT_TOKEN")
CHANNEL_ID = 123456789012345678

INTENTS = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=INTENTS)

POLICY_FILE = "policy.json"



policy = load_policy()
seen_alerts = set()
pending_actions = {}
