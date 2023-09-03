from discord.ext.commands import Cog
from discord.ext.commands import command
from discord import Embed
from discord.ext.commands import is_owner
import time 
import asyncio
from discord.ext.menus import MenuPages, ListPageSource
from typing import Optional
from aiohttp import request
from asyncio import sleep
from datetime import datetime, timedelta


class Misc(Cog):
	def __init__(self, bot):
		self.bot = bot

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("misc")

	@command(name="greetings", aliases=["hi", "hey", "hello"], brief = "I say hello to you.",)
	async def greetings_command(self, ctx):
		await ctx.send(f"{choice(('Hello', 'Hi', 'Hey', 'Hiya'))} {ctx.author.mention}! {choice(('How you doin?', 'How are you today?', 'How you doin today?'))}")

def setup(bot):
	bot.add_cog(Misc(bot))