import json
import asyncio
import aiohttp
import discord
import aiosqlite
import datetime
from operator import eq
import asyncpraw

from discord.ext import commands

bot = None
reddit = None

def get_bot_setting(key):
    with open("bot_settings.json", "r", encoding="UTF-8") as f:
        settings = json.load(f)
    try:
        return settings[key]
    except KeyError:
        update_bot_setting(key, None)
        return None

def update_bot_setting(key, val):
    with open("bot_settings.json", "r", encoding="UTF-8") as f:
        settings = json.load(f)
    settings[key] = val
    with open("bot_settings.json", "w", encoding="UTF-8") as f:
        json.dump(settings, f, indent=4, ensure_ascii=False)

async def update_task(bot: commands.Bot):
    while True:
        await get_new_article(bot)
        await get_popular_article(bot)
        await asyncio.sleep(300)


async def confirm(bot: commands.Bot, ctx: commands.Context, msg: discord.Message, time: int = 30):
    emoji_list = ["⭕", "❌"]
    await msg.add_reaction("⭕")
    await msg.add_reaction("❌")

    def check(reaction, user):
        return str(reaction.emoji) in emoji_list and user == ctx.author

    try:
        reaction, user = await bot.wait_for("reaction_add", timeout=time, check=check)
        if str(reaction.emoji) == emoji_list[0]:
            return True
        elif str(reaction.emoji) == emoji_list[1]:
            return False
    except asyncio.TimeoutError:
        return None

def reddit_session():
    d = get_bot_setting("reddit")
    return asyncpraw.Reddit(client_id=d["client_id"],
                     client_secret=d["client_secret"],
                     username=d["username"],
                     password=d["password"],
                     user_agent="HoDdit by /u/Penta0308")