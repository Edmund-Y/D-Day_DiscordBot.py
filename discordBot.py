#pip install -U git+https://github.com/Rapptz/discord.py
import os, json, sys, mariadb, discord, socket, datetime
import random
from typing import List
from discord import app_commands
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
            await tree.sync(guild=discord.Object(id=secrets.get('discordsv')))
            self.synced = True
        if not self.added:
            self.added = True
        print(f"We have logged in as {self.user}.")
        auto.start()
client = aclient()
tree = app_commands.CommandTree(client)



@tasks.loop(minutes=1)
async def auto():
    now = datetime.datetime.now()
    print('현재', now.hour, '시', now.minute, '분 입니다.(', datetime.datetime.today().weekday(), ')')
    if datetime.datetime.today().weekday() == 0 and now.hour == 9 and now.minute == 0:
        day5 = now + datetime.datetime.timedelta(days=5)
        embed_one = discord.Embed(
            title=day5.strftime('%y년 %m월 %d일(토)'),
            description='오후 9:30시에 콘텐츠 진행합니다.\n참여 가능 하신 분들은 <#893485899961237595>에 이모지(반응) 한번씩 눌러주세요~\n참여 불가능 하신분들은 싫어요 누르신 다음 사유 적어주세요.\n\n(사유 없이 미참석시 패널티 부여됩니다!)',
            color=0x74BBFF
        )
        embed_one.set_author(name='정기컨텐츠 안내',icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed_one.set_footer(text='moonlight ONE system')
        contechAlert = await client.get_channel(secrets.get('contect_alert')).send(embed=embed_one)
        embed = discord.Embed(title=day5.strftime('%y년 %m월 %d일(토)'), description='컨텐츠시간은  21시 30분  입니다.',color=0x74BBFF)
        embed.set_author(name='정기컨텐츠 안내',icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.set_thumbnail(url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.add_field(name='참여려면', value=':o: 이모지를 클릭', inline=False)
        embed.add_field(name='불참여라면', value=':x: 이모지를 클릭', inline=False)
        embed.add_field(name='[!]', value='불참여시 사유를 아래 작성해주세요.', inline=True)
        embed.set_footer(text='moonlight ONE system')
        contechChk = await client.get_channel(secrets.get('contect_chk')).send(embed=embed)
        await contechChk.add_reaction('⭕')
        await contechChk.add_reaction('❌')
@auto.before_loop
async def before_auto():
    await client.wait_until_ready()

def socketgo(stats, svname):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('3.37.210.15', 56895))
    client_socket.send(stats.encode()+svname.encode())
    client_socket.close()

@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='서버구동', description='마인크래프트 서버를 구동합니다.')
async def serverstart(interaction: discord.Interaction, 서버이름: str):
    embed = discord.Embed(title=f'{서버이름}를 실행합니다.')
    embed.set_author(name=str(interaction.user.name) + '님에 의해')
    embed.set_footer(text='moonlight ONE system')
    await interaction.response.send_message(embed=embed)
    socketgo('start/', str(서버이름))
@serverstart.autocomplete('서버이름')
async def serverstart_autocomplete(
    interaction: discord.Interaction,
    current: str,
) -> List[app_commands.Choice[str]]:
    serverstart = ['현실경제', '채석장']
    return [
        app_commands.Choice(name=selserver, value=selserver)
        for selserver in serverstart if current.lower() in selserver.lower()
    ]



@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='콘텐츠서버종료', description='실행중인 콘텐츠 서버를 종료합니다.')
@app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
async def serverstop(interaction: discord.Interaction,):
    embed = discord.Embed(title='모든 콘텐츠 서버가 종료되었습니다.')
    embed.set_author(name=str(interaction.user.name) + '님에 의해')
    embed.set_footer(text='moonlight ONE system')
    await interaction.response.send_message(embed=embed)
    socketgo('stop/', 'all')
@serverstop.error
async def on_serverstop_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)



@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='출석체크', description='정기컨텐츠 참여 확인합니다.')
@app_commands.checks.has_permissions(manage_messages=True)
async def chkplayer(interaction: discord.Interaction):
    channel = client.get_channel(secrets.get('contect_chk'))
    yesterday = datetime.datetime.utcnow() - datetime.timedelta(days=8)
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    embed = discord.Embed(title='정기컨텐츠 출석부')
    embed.set_footer(text='moonlight ONE system')
    allplayers = [member.name for member in client.get_all_members() if not member.bot]
    print(allplayers)
    noplayer = ''
    if client.get_channel(secrets.get('voice_ch_all')).members:
        for i in client.get_channel(secrets.get('voice_ch_all')).members:
            noplayer += str(i.name) + '\n'
            # allplayers.remove(i.name)
        embed.add_field(name='참여', value=f'{noplayer}', inline=True)
    noplayer = ''
    async for message in channel.history(limit=None, before=today, after=yesterday):
        if str(message.author) == 'D-DAY#1973':
            for reaction in message.reactions:
                if str(reaction) == '❌':
                    async for user in reaction.users():
                        if not user.bot:
                            noplayer += str(user.name)+'\n'
                            # allplayers.remove(user.name)
                    embed.add_field(name='불참여(작성)', value=f'{noplayer}', inline=True)
    embed.add_field(name='불참여(미작성)', value=f'추가중', inline=True)
    await interaction.response.send_message(embed=embed)

# @tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='플레이시간', description='현실경제서버 누적 접속시간을 조회합니다.')
# async def playtime(interaction: discord.Interaction, 닉네임: str):
#     try:
#         conn = mariadb.connect(
#             user=secrets.get('sql_usr'),
#             password=secrets.get('sql_pw'),
#             host=secrets.get('sql_addr'),
#             port=secrets.get('sql_port'),
#             database=secrets.get('sql_usr')
#         )
#         cur = conn.cursor()
#         cur.execute(f"SELECT time FROM realEconomy_playtime WHERE name = '{닉네임}'")
#         rsu = cur.fetchone()
#         if rsu is None:
#             await interaction.response.send_message(f'{닉네임}은 없는 닉네임입니다.')
#         else:
#             await interaction.response.send_message(f'{닉네임}은 {datetime.timedelta(milliseconds=int(rsu[0]))} 만큼 플레이하였습니다.')
#         conn.close()
#     except mariadb.Error as e:
#         print(f'Error connecting to MariaDB Platform: {e}')
#         sys.exit(1)



# @tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='현경실시간지도', description='현경서버의 실시간 지도를 표출합니다.')
# @app_commands.checks.cooldown(1, 30, key=lambda i: (i.guild_id))
# async def realEconomyLivemap(interaction: discord.Interaction,):
#     await interaction.response.send_message(f"http://map.d-day.moonlight.one/", ephemeral=True)
# @realEconomyLivemap.error
# async def on_realEconomyLivemap_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
#     if isinstance(error, app_commands.CommandOnCooldown):
#         await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)



@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='랜덤팀', description='현재 통화중인 사람을 랜덤으로 팀을 배분합니다.')
async def randomTeamSet(interaction: discord.Interaction, 팀원수: int):
    try:
        randomlist = [i.name for i in client.get_channel(interaction.user.voice.channel.id).members if not i.bot]
        embed = discord.Embed(title='랜덤으로 팀을 뽑았습니다.')
        embed.set_footer(text='moonlight ONE system')
        b = 1
        list = ''
        while randomlist:
            for a in range(1, 1+int(팀원수)):
                if randomlist:
                    tem = random.choice(randomlist)
                    list += str(tem)+'\n'
                    randomlist.remove(tem)
            embed.add_field(name=f'{b}팀', value=f'{list}', inline=True)
            b += 1
            list = ''
        await interaction.response.send_message(embed=embed)
    except AttributeError:
        await interaction.response.send_message('현재 접속중인 통화방이 없습니다.', ephemeral=True)



client.run(secrets.get('discord_token'))