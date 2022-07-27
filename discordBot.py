#pip install -U git+https://github.com/Rapptz/discord.py
import os, json, sys, mariadb, discord
from typing import List
from discord import app_commands
import datetime
from discord.ext import tasks

with open(os.path.join(os.path.dirname(__file__), 'apikey.json')) as f:
    secrets = json.loads(f.read())

try:
    conn = mariadb.connect(
        user=secrets.get('sql_usr'),
        password=secrets.get('sql_pw'),
        host=secrets.get('sql_addr'),
        port=secrets.get('sql_port'),
        database=secrets.get('sql_usr')
    )
except mariadb.Error as e:
    print(f'Error connecting to MariaDB Platform: {e}')
    sys.exit(1)

cur = conn.cursor()

class aclient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.synced = False
        self.added = False

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.synced:  # check if slash commands have been synced
            await tree.sync(guild=discord.Object(id=secrets.get('discordsv')))
            self.synced = True
        if not self.added:
            self.add_view(button_view())
            self.added = True
        print(f"We have logged in as {self.user}.")
        auto.start()

@tasks.loop(minutes=1)
async def auto():
    now = datetime.datetime.now()
    print('현재', now.hour, '시', now.minute, '분 입니다.(', datetime.datetime.today().weekday(), ')')
    if datetime.datetime.today().weekday() == 0 and now.hour == 9 and now.minute == 0:
        day5 = now + datetime.datetime.timedelta(days=5)
        embed_one = discord.Embed(
            title=day5.strftime('%y년 %m월 %d일(토)'),
            description='오후 9:30시에 콘텐츠 진행합니다.\n참여 가능 하신 분들은 <#893485899961237595>에 좋아요 한번씩 눌러주세요~\n참여 불가능 하신분들은 싫어요 누르신 다음 사유 적어주세요.\n\n(사유 없이 미참석시 패널티 부여됩니다!)',
            color=0x74BBFF
        )
        embed_one.set_author(name='정기컨텐츠 안내',icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed_one.add_field(name='참여라면', value=':o: 이모지를 클릭', inline=False)
        embed_one.add_field(name='불참여라면', value=':x: 이모지를 클릭', inline=False)
        embed_one.set_footer(text='@everyone')
        contechAlert = await client.get_channel(secrets.get('contect_alert')).send(embed=embed_one)

        embed = discord.Embed(title=day5.strftime('%y년 %m월 %d일(토)'), description='컨텐츠시간은  21시 30분  입니다.',color=0x74BBFF)
        embed.set_author(name='정기컨텐츠 안내',icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.set_thumbnail(url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.add_field(name='참여려면', value=':o: 이모지를 클릭', inline=False)
        embed.add_field(name='불참여라면', value=':x: 이모지를 클릭', inline=False)
        embed.set_footer(text='불참시 아래에 반드시 사유를 작성해주세요.')
        contechChk = await client.get_channel(secrets.get('contect_chk')).send(embed=embed)
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

@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='서버구동', description='마인크래프트 서버를 구동합니다.')
async def serverstart(interaction: discord.Interaction, 서버이름: str):
    await interaction.response.send_message(f'{서버이름}를 실행합니다.')
@serverstart.autocomplete('서버이름')
async def serverstart_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    serverstart = ['현실경제', '채석장', '미니술래잡기']
    return [
        app_commands.Choice(name=selserver, value=selserver)
        for selserver in serverstart if current.lower() in selserver.lower()
    ]

@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='콘텐츠서버종료', description='실행중인 콘텐츠 서버를 종료합니다.')
@app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
async def serverstop(interaction: discord.Interaction,):
    await interaction.response.send_message(f"콘텐츠서버에 서버종료 요청하였습니다.", ephemeral=True)
    embed = discord.Embed(title='모든 콘텐츠 서버가 종료되었습니다.')
    embed.set_author(name=str(interaction.user.name) + '님에 의해')
    await client.get_channel(interaction.channel_id).send(embed=embed)
@serverstop.error
async def on_serverstop_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)
        
@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='출석체크', description='정기컨텐츠 참여 확인합니다.')
@app_commands.checks.has_permissions(manage_messages=True)
async def chkplayer(interaction: discord.Interaction):
    # msid = await client.get_channel(secrets.get('contect_chk')).fetch_message(client.get_channel(secrets.get('contect_chk')).last_message_id)
    await interaction.response.send_message(f"결과가 잠시후 출력됩니다.", ephemeral=True)
    
@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='플레이시간', description='현실경제서버 누적 접속시간을 조회합니다.')
async def playtime(interaction: discord.Interaction, 닉네임: str):
    cur.execute(f"SELECT time FROM realEconomy_playtime WHERE name = '{닉네임}'")
    rsu = cur.fetchone()
    if rsu is None:
        await interaction.response.send_message(f'{닉네임}은 없는 닉네임입니다.')
    else:
        await interaction.response.send_message(f'{닉네임}은 {rsu[0]}초 플레이하였습니다.')

client.run(secrets.get('discord_token'))