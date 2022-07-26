# pip install -U git+https://github.com/Rapptz/discord.py
import os, json, sys, mariadb, discord, socket, datetime, random, time, shutil
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.font_manager as fm
from typing import List
from discord import app_commands
from discord.ext import tasks

with open(os.path.join(os.path.dirname(__file__), 'apikey.json')) as f:
    secrets = json.loads(f.read())


# !rm -rf ~/.cache/matplotlib/*

class aclient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
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

intents = discord.Intents.default()
intents.members = True
client = aclient(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_member_remove(self, member):
    print(member)

@tasks.loop(minutes=1)
async def auto():
    now = datetime.datetime.now()
    print('현재', now.hour, '시', now.minute, '분 입니다.(', datetime.datetime.today().weekday(), ')')
    if datetime.datetime.today().weekday() == 0 and now.hour == 9 and now.minute == 9:
        day5 = now + datetime.timedelta(days=5)
        embed_one = discord.Embed(
            title=day5.strftime('%y년 %m월 %d일(토)'),
            description='오후 9:30시에 콘텐츠 진행합니다.\n참여 가능 하신 분들은 <#893485899961237595>에 이모지(반응) 한번씩 눌러주세요~\n참여 불가능 하신분들은 싫어요 누르신 다음 사유 적어주세요.\n\n(사유 없이 미참석시 패널티 부여됩니다!)',
            color=0x74BBFF
        )
        embed_one.set_author(name='정기컨텐츠 안내',
                             icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed_one.set_footer(text='moonlight ONE system')
        contechAlert = await client.get_channel(secrets.get('contect_alert')).send(embed=embed_one)
        embed = discord.Embed(title=day5.strftime('%y년 %m월 %d일(토)'), description='컨텐츠시간은  21시 30분  입니다.',
                              color=0x74BBFF)
        embed.set_author(name='정기컨텐츠 안내',
                         icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed.add_field(name='참여려면', value=':o: 이모지를 클릭', inline=False)
        embed.add_field(name='불참여라면', value=':x: 이모지를 클릭', inline=False)
        embed.add_field(name='[!]', value='불참여시 사유를 아래 작성해주세요.', inline=True)
        embed.set_footer(text='moonlight ONE system')
        contechChk = await client.get_channel(secrets.get('contect_chk')).send(embed=embed)
        await contechChk.add_reaction('⭕')
        await contechChk.add_reaction('❌')
    if now.hour == 9 and now.minute == 0:
        try:
            conn = mariadb.connect(
                user=secrets.get('sql_usr'),
                password=secrets.get('sql_pw'),
                host=secrets.get('sql_addr'),
                port=secrets.get('sql_port'),
                database=secrets.get('sql_usr')
            )
            cur = conn.cursor()
            cur.execute("""SELECT * FROM discord_birthday;""")
            rsu = cur.fetchall()
            birthplayer = ''
            if rsu:
                for bir in rsu:
                    if str(bir[2]) == str(
                            datetime.datetime.now().month):  # and str(bir[3]) == str(datetime.datetime.now().day):
                        birthplayer += '```' + str(bir[1]).rstrip("#") + '님```\n'
            if len(birthplayer) > 2:
                embed = discord.Embed(title='생일을 축하해주세요~')
                embed.set_footer(text='moonlight ONE system')
                embed.add_field(name='오늘 생일자', value=f'{birthplayer}', inline=False)
                embed.set_image(url='https://cdn.pixabay.com/photo/2016/11/18/15/46/birthday-1835443_960_720.jpg')
                await client.get_channel(secrets.get('defaultalk')).send(embed=embed)
        except mariadb.Error as e:
            print(f'Error connecting to MariaDB Platform: {e}')
        finally:
            cur.close()
            conn.close()
@auto.before_loop
async def before_auto():
    await client.wait_until_ready()


@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='출석체크', description='정기컨텐츠 참여 확인합니다.')
@app_commands.checks.has_permissions(manage_messages=True)
async def chkplayer(interaction: discord.Interaction, 콘텐츠명: str):
    await interaction.response.send_message('잠시 후 출석부를 출력합니다.', ephemeral=True)
    channel = client.get_channel(secrets.get('contect_chk'))
    embed = discord.Embed(title='정기컨텐츠 출석부')
    embed.set_footer(text='moonlight ONE system')
    yesterday = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) - datetime.timedelta(
        days=5)
    today = datetime.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    allplayers = [member.id for member in client.get_guild(secrets.get('discordsv')).members if not member.bot]
    noplayer = ''
    dbq = []
    if client.get_channel(secrets.get('voice_ch_all')).members:
        for i in client.get_channel(secrets.get('voice_ch_all')).members:
            uname = await client.fetch_user(i.id)
            noplayer += '```' + str(uname) + '```\n'
            allplayers.remove(i.id)
            dbq.append([int(i.id), uname.name, f'{콘텐츠명}', '참여'])
        embed.add_field(name='참여', value=f'{noplayer}', inline=True)
    noplayer = ''
    temp = []
    async for message in channel.history(limit=None, before=today, after=yesterday):
        temp.append(str(message.author.id))
        if str(message.author) == 'D-DAY#1973':
            for reaction in message.reactions:
                if str(reaction) == '❌':
                    async for user in reaction.users():
                        if not user.bot:
                            try:
                                allplayers.remove(user.id)
                                uname = await client.fetch_user(user.id)
                                noplayer += '```' + str(uname) + '```\n'
                                dbq.append([int(user.id), uname.name, f'{콘텐츠명}', '불참(작성)'])
                            except ValueError as e:
                                print(f'출석체크 X 후 참여 {user.name} : ' + str(e))
            embed.add_field(name='불참여(작성)', value=f'{noplayer}', inline=True)
    noplayer = ''
    if allplayers:
        for aname in allplayers:
            try:
                uname = await client.fetch_user(aname)
                noplayer += '```' + str(uname) + '```\n'
                dbq.append([int(aname), uname.name, f'{콘텐츠명}', '불참(미작성)'])
                time.sleep(0.26)
            except:
                print(f'{aname} 에서 오류')
        embed.add_field(name='불참여(미작성)', value=f'{noplayer}', inline=True)
    try:
        conn = mariadb.connect(
            user=secrets.get('sql_usr'),
            password=secrets.get('sql_pw'),
            host=secrets.get('sql_addr'),
            port=secrets.get('sql_port'),
            database=secrets.get('sql_usr')
        )
        cur = conn.cursor()
        query = """insert into discord_attendances (idx, diname, contentname, dstats) values (?, ?, ?, ?);"""
        cur.executemany(query, dbq)
        cur.execute("""insert into discord_contect (contectname) values (?);""", (콘텐츠명,))
        conn.commit()
    except mariadb.Error as e:
        print(f'Error connecting to MariaDB Platform: {e}')
    finally:
        cur.close()
        conn.close()
    await client.get_channel(secrets.get('attendance_ch')).send(embed=embed)
@chkplayer.error
async def on_chkplayer_error(interaction: discord.Interaction, error: discord.app_commands.errors.MissingPermissions):
    if isinstance(error, app_commands.errors.MissingPermissions):
        await interaction.response.send_message(f"명령어 사용권한이 없습니다.", ephemeral=True)

@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='참여도', description='정기컨텐츠 참여도를 확인합니다.')
@app_commands.checks.cooldown(1, 5, key=lambda i: (i.guild_id))
async def participation(interaction: discord.Interaction, 디코닉네임: discord.User):
    try:
        conn = mariadb.connect(
            user=secrets.get('sql_usr'),
            password=secrets.get('sql_pw'),
            host=secrets.get('sql_addr'),
            port=secrets.get('sql_port'),
            database=secrets.get('sql_usr')
        )
        cur = conn.cursor()
        cur.execute("""SELECT dstats FROM discord_attendances WHERE idx=(?);""", (str(디코닉네임.id),))
        rsu = cur.fetchall()
        if rsu is None:
            await interaction.response.send_message(f'존재하지 않는 디코닉네임입니다.')
        else:
            chk = {}
            ratio = []
            labels = []
            explode = [0.05, 0.05, 0.05]
            colors = ['#ff9999', '#ffc000', '#8fd9b6']
            for value in rsu:
                try:
                    chk[str(value).replace("('", "").replace("',)", "")] += 1
                except:
                    chk[str(value).replace("('", "").replace("',)", "")] = 1
            for key, value in chk.items():
                labels.append(key)
                ratio.append(value)
            if labels:
                if len(labels) == 1:
                    del colors[-1]
                    del explode[-1]
                    del colors[-1]
                    del explode[-1]
                elif len(labels) == 2:
                    del colors[-1]
                    del explode[-1]
                plt.rc('font', family='MaruBuri')
                # plt.rcParams["font.family"] = "MaruBuri"
                plt.pie(ratio, labels=labels, autopct='%.1f%%', startangle=260, counterclock=False, explode=explode,
                        shadow=True, colors=colors)
                plt.savefig('./public/참여현황.png', transparent=True)
                f = discord.File('./public/참여현황.png')
                await interaction.response.send_message(file=f)
                os.remove('./public/참여현황.png')
            else:
                await interaction.response.send_message('콘텐츠 참가이력이 없습니다.')
    except mariadb.Error as e:
        print(f'Error connecting to MariaDB Platform: {e}')
    finally:
        cur.close()
        conn.close()
@participation.error
async def on_participation_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)


@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='생일삭제', description='등록된 생일을 제거합니다.')
async def birthdaydel(interaction: discord.Interaction):
    try:
        conn = mariadb.connect(
            user=secrets.get('sql_usr'),
            password=secrets.get('sql_pw'),
            host=secrets.get('sql_addr'),
            port=secrets.get('sql_port'),
            database=secrets.get('sql_usr')
        )
        cur = conn.cursor()
        cur.execute("""SELECT idx FROM discord_birthday WHERE idx=(?);""", (int(interaction.user.id),))
        rsu = cur.fetchone()
        if rsu is None:
            await interaction.response.send_message(f'등록된 생일이 없습니다.')
        else:
            cur.execute("""DELETE FROM discord_birthday WHERE idx=(?);""", (int(interaction.user.id),))
            conn.commit()
            await interaction.response.send_message(f'등록된 생일을 삭제했습니다.')
    except mariadb.Error as e:
        print(f'Error connecting to MariaDB Platform: {e}')
    finally:
        cur.close()
        conn.close()


@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='생일등록', description='자신을 생일을 등록할 수 있습니다.')
async def birthdayset(interaction: discord.Interaction, 월: int, 일: int):
    if 월 > 12 or 월 < 1:
        await interaction.response.send_message(f'월은 1월~12월 까지만 등록할 수 있습니다.', ephemeral=True)
    elif 일 < 1 or 일 > 31:
        await interaction.response.send_message(f'일은 1일~31일 까지만 등록할 수 있습니다.', ephemeral=True)
    elif 월 == 2 and 일 > 28:
        await interaction.response.send_message(f'2월은 28일 까지만 등록할 수 있습니다.', ephemeral=True)
    elif 월 < 7 and 월 % 2 == 0 and 일 == 31:
        await interaction.response.send_message(f'{월}월은 30일 까지만 등록할 수 있습니다.', ephemeral=True)
    elif 월 > 8 and 월 % 2 == 1 and 일 == 31:
        await interaction.response.send_message(f'{월}월은 30일 까지만 등록할 수 있습니다.', ephemeral=True)
    else:
        try:
            conn = mariadb.connect(
                user=secrets.get('sql_usr'),
                password=secrets.get('sql_pw'),
                host=secrets.get('sql_addr'),
                port=secrets.get('sql_port'),
                database=secrets.get('sql_usr')
            )
            cur = conn.cursor()
            cur.execute("""SELECT bmonth, bday FROM discord_birthday WHERE idx=(?);""", (int(interaction.user.id),))
            rsu = cur.fetchone()
            if rsu is None:
                cur.execute("""insert into discord_birthday (idx, pname, bmonth, bday) values (?, ?, ?, ?);""",
                            (str(interaction.user.id), str(interaction.user), int(월), int(일)))
                conn.commit()
                await interaction.response.send_message(f'생일을 등록했습니다.')
            else:
                await interaction.response.send_message(
                    f'생일이 등록되어있습니다. ({rsu[0]}월 {rsu[1]}일)\n등록된 생일을 제거하려면 /생일삭제 를 이용해주세요')
        except mariadb.Error as e:
            print(f'Error connecting to MariaDB Platform: {e}')
        finally:
            cur.close()
            conn.close()


@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='랜덤팀', description='현재 통화중인 사람을 랜덤으로 팀을 배분합니다.')
async def randomTeamSet(interaction: discord.Interaction, 팀원수: int):
    try:
        randomlist = [i.name for i in client.get_channel(interaction.user.voice.channel.id).members if not i.bot]
        embed = discord.Embed(title='랜덤으로 팀을 뽑았습니다.')
        embed.set_footer(text='moonlight ONE system')
        b = 1
        lists = ''
        while randomlist:
            for a in range(1, 1 + int(팀원수)):
                if randomlist:
                    tem = random.choice(randomlist)
                    lists += str(tem) + '\n'
                    randomlist.remove(tem)
            embed.add_field(name=f'{b}팀', value=f'{lists}', inline=True)
            b += 1
            lists = ''
        await interaction.response.send_message(embed=embed)
    except AttributeError:
        await interaction.response.send_message('현재 접속중인 통화방이 없습니다.', ephemeral=True)


@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='생일목록', description='생일자 목록을 조회합니다.')
async def birthselect(interaction: discord.Interaction, 조회항목: str):
    try:
        conn = mariadb.connect(
            user=secrets.get('sql_usr'),
            password=secrets.get('sql_pw'),
            host=secrets.get('sql_addr'),
            port=secrets.get('sql_port'),
            database=secrets.get('sql_usr')
        )
        cur = conn.cursor()
        if 조회항목 == '지난 달':
            temmou = datetime.datetime.now().month - 1
        elif 조회항목 == '이번 달':
            temmou = datetime.datetime.now().month
        elif 조회항목 == '다음 달':
            temmou = datetime.datetime.now().month + 1
        elif int(조회항목) == range(1, 12):
            temmou = 조회항목
        if temmou:
            cur.execute("""SELECT pname FROM discord_birthday WHERE bmonth=(?);""", (temmou,))
            rsu = cur.fetchone()
            if rsu is None:
                embed = discord.Embed(title=f'{조회항목}의 생일자가 없습니다.')
            else:
                embed = discord.Embed(title=f'{조회항목}의 생일자입니다.')
                noplayer = ''
                for na in rsu:
                    noplayer += '```' + str(na) + '```\n'
                embed.add_field(name=str(len(rsu)) + '명', value=f'{noplayer.rstrip("#")}', inline=True)
            embed.set_footer(text='moonlight ONE system')
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message('잘못된 선택입니다.', ephemeral=True)
    except mariadb.Error as e:
        print(f'Error connecting to MariaDB Platform: {e}')
    finally:
        cur.close()
        conn.close()
@birthselect.autocomplete('조회항목')
async def birthselect_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> List[app_commands.Choice[str]]:
    birthselect = ['지난 달', '이번 달', '다음 달', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12']
    return [
        app_commands.Choice(name=birsel, value=birsel)
        for birsel in birthselect if current.lower() in birsel.lower()
    ]
@birthselect.error
async def on_birthselect_error(interaction: discord.Interaction, error: discord.app_commands.errors.CommandInvokeError):
    if isinstance(error, app_commands.errors.CommandInvokeError):
        await interaction.response.send_message(f"잘못된 항목을 입력하였습니다.", ephemeral=True)

@tree.command(guild=discord.Object(id=secrets.get('discordsv')), name='운영현황', description='디데이 운영현황도입니다.')
@app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id))
async def statistics(interaction: discord.Interaction, 조회항목: str):
    await interaction.response.send_message('잘못된 선택입니다.', ephemeral=True)
@statistics.autocomplete('조회항목')
async def statistics_autocomplete(
        interaction: discord.Interaction,
        current: str,
) -> List[app_commands.Choice[str]]:
    birthselect = ['플레이현황', '컨텐츠진행도']
    return [
        app_commands.Choice(name=birsel, value=birsel)
        for birsel in birthselect if current.lower() in birsel.lower()
    ]
@statistics.error
async def on_statistics_error(interaction: discord.Interaction, error: app_commands):
    if isinstance(error, app_commands.errors.CommandInvokeError):
        await interaction.response.send_message(f"잘못된 항목을 입력하였습니다.", ephemeral=True)
    elif isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(f"{int(error.retry_after)}초 후 명령어를 사용할 수 있습니다.", ephemeral=True)
    elif isinstance(error, app_commands.errors.CommandNotFound):
        print(f'다른 채널에서 명령어 사용됨')

client.run(secrets.get('discord_token'))
