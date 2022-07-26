import os, json
import discord
from discord import app_commands

with open(os.path.join(os.path.dirname(__file__), 'apikey.json')) as f:
    secrets = json.loads(f.read())

# revised/fixed version from https://youtu.be/xrHOqasnoyA

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False  # we use this so the bot doesn't sync commands more than once

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  # check if slash commands have been synced
            await tree.sync(guild=discord.Object(id=secrets.get('testGuild')))
            self.synced = True
        print(f"We have logged in as {self.user}.")

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(guild=discord.Object(id=secrets.get('testGuild')), name='콘텐츠서버종료', description='실행중인 콘텐츠 서버를 종료합니다.')
@app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
async def tester(interaction: discord.Interaction):
    await interaction.response.send_message(f"서버를 종료합니다.", ephemeral=True)

@tester.error
async def on_tester_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)

client.run(secrets.get('discord_token'))
