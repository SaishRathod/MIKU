from discord.ext.commands import Cog, command, has_permissions, CheckFailure
from discord import Embed
from apscheduler.triggers.cron import CronTrigger
from discord import Activity, ActivityType
from discord.ext.commands import is_owner
from time import time
from psutil import Process, virtual_memory
from platform import python_version
from discord import __version__ as discord_version
from datetime import datetime, timedelta


from ..db import db

class Meta(Cog):
	def __init__(self, bot):
		self.bot = bot

		self.message = f"listening songs with Nova-kun | v2.0 | IT ACTUALLY WORKED!"

		bot.scheduler.add_job(self.set, CronTrigger(second=0))

	@property
	def message(self):
		return self._message.format(users = len(self.bot.users), guilds = len(self.bot.guilds))

	@message.setter
	def message(self, value):
		if value.split(" ")[0] not in ("playing", "watching", "listening", "streaming"):
			raise ValueError("Invalid activity type.")

		self._message = value
		

	async def set(self):
		_type, _name = self.message.split(" ", maxsplit = 1)

		await self.bot.change_presence(activity = Activity(
			name = _name, type = getattr(ActivityType, _type, ActivityType.playing)))


	# @command(name = "change_prefix", aliases = ["set_prefix", "setprefix", "changeprefix"])
	# @is_owner()
	# @has_permissions(manage_guild = True)
	# async def change_prefix_command(self, ctx, new: str):
	# 	if len(new) > 5:
	# 		await ctx.send(f"The prefix cannot be more than 5 characters.")
	# 	else:
	# 		new = new + " "
	# 		db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", new, ctx.guild.id)
	# 		await ctx.send(f'Successfully changed the prefix to "{new}".')

	# @change_prefix_command.error
	# async def change_prefix_command_error(self, ctx, exc):
	# 	if isinstance(exc, CheckFailure):
	# 		await ctx.send(f"Could not change prefix. You require 'Manage Server' permission to execute changes.")


	@command(name = "setactivity", aliases = ["changepresence", "changeactivity"])
	@is_owner()
	async def set_activity_message(self, ctx, *, text: str):
		self.message = text
		await self.set()
		await ctx.send(f"Successfully set `{text}` as your present activity. Although I will still display the default activity the next time I restart.")

	@command(name = "ping", brief = "Check the server latency(ping). Defines bot's reaction speed.")
	async def server_ping(self, ctx):
		start = time()
		message = await ctx.send(f"Pong! `{round(self.bot.latency * 1000)}ms`")
		end = time()

		await message.edit(content=f"Pong! `{self.bot.latency*1000:,.0f} ms`. \nResponse time: `{(end - start)*1000:,.0f} ms.`")
	
	@command(name="stats")
	async def show_bot_stats(self, ctx):
		embed = Embed(title="Bot Stats:",
					  colour= (0xa451d8),
					  thumbnail=self.bot.user.avatar_url,
					  timestamp=datetime.utcnow())

		proc = Process()
		with proc.oneshot():
			uptime = timedelta(seconds=time()-proc.create_time())
			cpu_time = timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user)
			mem_total = virtual_memory().total / (1024**2)
			mem_of_total = proc.memory_percent()
			mem_usage = mem_total * (mem_of_total / 100)

		fields = [
			("Bot version", self.bot.VERSION, True),
			("Python version", python_version(), True),
			("discord.py version", discord_version, True),
			("Uptime", uptime, True),
			("CPU time", cpu_time, True),
			("Memory usage", f"{mem_usage:,.3f} / {mem_total:,.0f} MiB ({mem_of_total:.0f}%)", True),
			#("Users", f"{self.bot.guild.member_count:,}", True)
		]

		for name, value, inline in fields:
			embed.add_field(name=name, value=value, inline=inline)

		await ctx.send(embed=embed)

	@command(name = "shutdown")
	@has_permissions(administrator = True)
	@is_owner()
	async def shutdown(self, ctx):
		await ctx.send("Signing off, cya! \n\nYours Only:\n*Miku*")

		db.commit()
		self.bot.scheduler.shutdown()
		await self.bot.logout()
		

	@Cog.listener()
	async def on_ready(self):
		if not self.bot.ready:
			self.bot.cogs_ready.ready_up("meta")

def setup(bot):
	bot.add_cog(Meta(bot))