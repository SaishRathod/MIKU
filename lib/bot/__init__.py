from asyncio import sleep
from datetime import datetime
from glob import glob
from re import search
from discord import Intents
from discord.ext.commands import Cog
from better_profanity import profanity
from discord.errors import HTTPException, Forbidden
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord.ext.commands import Bot as Botbase
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument, CommandOnCooldown, CheckFailure, MissingPermissions, BotMissingPermissions)
from discord.ext.commands import NotOwner, MissingRole
from discord.ext.commands import Context
from discord.utils import find
from discord import Embed, File, DMChannel
from discord.ext.commands import when_mentioned_or
from discord.ext.commands import command
from discord.ext import commands
import random
import itertools

from ..db import db

OWNER_IDS = [424486126351417344]
COGS = [path.split("\\")[-1][:-3] for path in glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)


def get_prefix(bot, message):
    prefix = db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", message.guild.id)
    prefix = map("".join, itertools.product(*zip(prefix.lower(), prefix.upper())))
    return when_mentioned_or(*prefix)(bot, message)

class Ready(object):
    def __init__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True)
        print(f"--{cog} cog ready--")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(Botbase):
    def __init__(self):
        self.name = "MIKU"
        self.cogs_ready = Ready()
        self.ready = False
        self.scheduler = AsyncIOScheduler()
        self.owner = "<@424486126351417344>"
        self.miku = "<@814609281390215199>"
        self.VERSION = "2.0"
        # self._cogs = [p.stem for p in Path(".").glob("./bot/cogs/*.py")]

        db.autosave(self.scheduler)

        super().__init__(
            command_prefix = get_prefix,
            case_insensitive = True,
            owner_ids = OWNER_IDS, 
            intents = Intents.all()
            )


    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"--{cog} cog loaded--")

        print("--Setup complete--")

    def update_db(self):
        db.multiexec("INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                     ((guild.id,) for guild in self.guilds))

        db.commit()

    def run(self, version):
        self.VERSION = version

        print("Running setup...")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding = "utf-8") as tf:
            self.TOKEN = tf.read()

        print("Miku is running...")
        super().run(self.TOKEN, reconnect = True)

    async def on_connect(self):
        print(f"Miku is UP (latency: {self.latency*1000:,.0f} ms).")

    async def on_resumed(self):
        print("Miku resumed.")

    async def on_disconnect(self):
        print("Miku disconnected.")

    async def shutdown(self):
        print("Closing connection to Discord...")
        await super().close()

    async def close(self):
        print("Closing on keyboard interrupt...")
        await self.shutdown()


    # async def on_error(self, err, *args, **kwargs):
    #     raise

    # async def on_command_error(self, ctx, exc):
    #     raise getattr(exc, "original", exc)

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(774009780913045524)
            self.stdout = self.get_channel(830100610404581377)
            self.scheduler.start()
            self.update_db()
            self.client_id = (await self.application_info()).id

            meta = self.get_cog("Meta")
            await meta.set()


            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            await self.stdout.send(f"Ready to sing {self.owner}! Ready when you are.")
            
            self.ready = True
            print("Miku is UP and RUNNING.")

        else:
            print("Miku reconnected.")

    async def process_commands(self, msg):
        ctx = await self.get_context(msg, cls = commands.Context)

        if ctx.command is not None:
            await self.invoke(ctx)

    async def on_message(self, msg):
        if not msg.author.bot:
            await self.process_commands(msg)

bot = Bot()




















