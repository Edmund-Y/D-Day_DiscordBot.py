import os, json
import discord
from discord import app_commands
from datetime import datetime, timedelta

from discord.ext import tasks

with open(os.path.join(os.path.dirname(__file__), 'apikey.json')) as f:
    secrets = json.loads(f.read())

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.added = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  # check if slash commands have been synced
            await tree.sync(guild=discord.Object(id=secrets.get('testGuild')))
            self.synced = True
        if not self.added:
            self.add_view(button_view())
            self.added = True
        print(f"We have logged in as {self.user}.")
        auto.start()

@tasks.loop(minutes=1)
async def auto():
    now = datetime.now()
    print('현재', now.hour, '시', now.minute, '분 입니다.(', datetime.today().weekday(), ')')
    if datetime.today().weekday() == 0 and now.hour == 9 and now.minute == 0:
        day5 = now + timedelta(days=5)
        embed_one = discord.Embed(
            title=day5.strftime('%y년 %m월 %d일(토)'),
            description='오후 9:30시에 콘텐츠 진행합니다.\n참여 가능 하신 분들은 <#893485899961237595>에 좋아요 한번씩 눌러주세요~\n참여 불가능 하신분들은 싫어요 누르신 다음 사유 적어주세요.\n\n(사유 없이 미참석시 패널티 부여됩니다!)',
            color=0x74BBFF
        )
        embed_one.set_author(name='정기컨텐츠 안내',icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed_one.add_field(name='참여라면', value=':o: 이모지를 클릭', inline=False)
        embed_one.add_field(name='불참여라면', value=':x: 이모지를 클릭', inline=False)
        embed_one.set_footer(text='@everyone')
        contechAlert = await client.get_channel(secrets.get('testChatOne')).send(embed=embed_one)

        embed = discord.Embed(title=day5.strftime('%y년 %m월 %d일(토)'), description='컨텐츠시간은  21시 30분  입니다.',color=0x74BBFF)
        embed.set_author(name='정기컨텐츠 안내',icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.set_thumbnail(url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.add_field(name='참여려면', value=':o: 이모지를 클릭', inline=False)
        embed.add_field(name='불참여라면', value=':x: 이모지를 클릭', inline=False)
        embed.set_footer(text='불참시 아래에 반드시 사유를 작성해주세요.')
        contechChk = await client.get_channel(secrets.get('testChatTwo')).send(embed=embed)
        await contechChk.add_reaction('⭕')
        await contechChk.add_reaction('❌')

@auto.before_loop
async def before_auto():
    await client.wait_until_ready()

class button_view(discord.ui.View):
    def __init__(self) -> None:
        super().__init__(timeout=None)

    @discord.ui.button(label='채석장', style=discord.ButtonStyle.gray, custom_id='role_button')
    async def quarry(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(f'공개예정 기능입니다.', ephemeral=True)

client = aclient()
tree = app_commands.CommandTree(client)

@tree.command(guild=discord.Object(id=secrets.get('testGuild')), name='서버구동', description='마인크래프트 서버를 구동합니다.')
@app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
async def serverstart(interaction: discord.Interaction):
    await interaction.response.send_message(view=button_view())
@serverstart.error
async def on_tester_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)

@tree.command(guild=discord.Object(id=secrets.get('testGuild')), name='콘텐츠서버종료', description='실행중인 콘텐츠 서버를 종료합니다.')
@app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
async def serverstop(interaction: discord.Interaction,):
    await interaction.response.send_message(f"콘텐츠서버에 서버종료 요청하였습니다.", ephemeral=True)
    embed = discord.Embed(title='모든 콘텐츠 서버가 종료되었습니다.')
    embed.set_author(name=str(interaction.user.name) + '님에 의해')
    await client.get_channel(interaction.channel_id).send(embed=embed)
@serverstop.error
async def on_tester_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)

client.run(secrets.get('discord_token'))
