import datetime
import html
import re

import aiosqlite
import asyncpraw

import modules

try:
    import os
    import nest_asyncio
    import discord
    import asyncio
    import aiohttp
    import json
    from discord.ext import commands
    from operator import eq
    import nest_asyncio
    from aiohttp import web
except ImportError:
    import os

    os.system("pip install -r requirements.txt")
    import nest_asyncio
    import discord
    import asyncio
    import aiohttp
    import json
    from discord.ext import commands
    from operator import eq
    from aiohttp import web

nest_asyncio.apply()

redditbot_working = False
# init_flag = True

modules.bot = commands.Bot(command_prefix="!", help_command=None)


def is_authorized(ctx):
    return modules.bot.get_guild(518791611048525852).get_role(
        721776076430377142) in ctx.author.roles or ctx.author.id == 278170182227066880


def is_dm(ctx):
    return isinstance(ctx.channel, discord.channel.DMChannel)


@modules.bot.event
async def on_ready():
    print("running")
    await modules.bot.change_presence(activity=discord.Game(modules.get_bot_setting("presence")))
    # global init_flag
    # if init_flag:
    #    init_flag = False
    #    print("calling __ai_update()")
    #    await __ai_update(None)
    global redditbot_working
    if not redditbot_working:
        redditbot_working = True
        await asyncio.create_task(modules.update_task(modules.bot))


@modules.bot.command(name="핑")
async def _ping(ctx):
    bot_latency = round(modules.bot.latency * 1000)
    await ctx.send(f":ping_pong: 퐁! ({bot_latency}ms)")


@modules.bot.command(name="업데이트")
@commands.check(is_authorized)
async def _new_article(ctx):
    msg = await ctx.send("정말로 수동으로 업데이트 할까요?")
    res = await modules.confirm(modules.bot, ctx, msg)
    if res is not True:
        return await msg.edit(content="수동 업데이트를 취소했습니다.")
    await modules.get_new_article(modules.bot)
    await msg.edit(content="업데이트 완료")

@modules.bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure) or isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"오류 - `{error}`")

loop = asyncio.get_event_loop()

reddit = modules.reddit_session()

print('trying to run the bot')
modules.bot.run(modules.get_bot_setting("token"))
