import json
import asyncio
import discord
import aiosqlite
import asyncpraw
import time

from discord.ext import commands

bot = None
reddit = None
subreddit = None


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


async def update_loop(bot: commands.Bot):
    while True:
        try:
            await asyncio.sleep(300)
            await get_popular_article(bot)
        except KeyboardInterrupt:
            break
        except:
            continue


def update_task(bot: commands.Bot):
    asyncio.ensure_future(update_loop(bot))


async def get_popular_article(bot: commands.Bot):
    async with aiosqlite.connect('article.db') as db:
        await db.execute(
            "CREATE TABLE IF NOT EXISTS populararticle (id INTEGER NOT NULL UNIQUE, timestamp INTEGER NOT NULL)")
        await db.commit()
        await db.execute("DELETE FROM populararticle WHERE timestamp < ?", (time.time() - 605105,))
        await db.commit()
        async for s in subreddit.top("day"):
            if s.score < 1000:
                continue
            async with db.execute("SELECT COUNT(*) FROM populararticle WHERE id = ?", (s.id,)) as cursor:
                if (await cursor.fetchone())[0] > 0:
                    continue

            await db.execute("INSERT INTO populararticle VALUES (?, ?)", (s.id, s.created_utc))
            ann = []
            for c in get_bot_setting("redditpostchannels"):
                ann.append(bot.get_guild(518791611048525852).get_channel(c))
            for a in ann:
                await a.send(f"https://www.reddit.com{s.permalink}")
        await db.commit()


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


async def reddit_session():
    d = get_bot_setting("reddit")
    global reddit
    reddit = asyncpraw.Reddit(client_id=d["client_id"],
                              client_secret=d["client_secret"],
                              username=d["username"],
                              password=d["password"],
                              user_agent="HoDdit by /u/Penta0308")
    reddit.read_only = True
    global subreddit
    subreddit = await reddit.subreddit("KerbalSpaceProgram")
