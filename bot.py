import modules

import discord
import asyncio
from discord.ext import commands
import nest_asyncio

nest_asyncio.apply()

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
    await modules.get_popular_article(modules.bot)
    await msg.edit(content="업데이트 완료")

@modules.bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CheckFailure) or isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"오류 - `{error}`")

loop = asyncio.get_event_loop()

reddit = loop.run_until_complete(modules.reddit_session())

modules.update_task(modules.bot)

print('trying to run the bot')
modules.bot.run(modules.get_bot_setting("token"))
