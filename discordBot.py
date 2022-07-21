import os, json
import discord
from discord.ext import tasks, commands
from datetime import datetime, timedelta

secret_file = os.path.join(os.path.dirname(__file__), 'apikey.json')

with open(secret_file) as f:
    secrets = json.loads(f.read())

intents = discord.Intents.default()
intents.members = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print('디스코드 봇 시작')
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
        embed_one.set_author(name='정기컨텐츠 안내', icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
        embed_one.add_field(name='참여라면', value=':o: 이모지를 클릭', inline=False)
        embed_one.add_field(name='불참여라면', value=':x: 이모지를 클릭', inline=False)
        embed_one.set_footer(text='@everyone')
        contechAlert = await client.get_channel(secrets.get('testChatOne')).send(embed=embed_one)

        embed = discord.Embed(title=day5.strftime('%y년 %m월 %d일(토)'), description='컨텐츠시간은  21시 30분  입니다.', color=0x74BBFF)
        embed.set_author(name='정기컨텐츠 안내', icon_url='https://cdn.discordapp.com/icons/875723042200911892/c3976639ca840916db9565567b8fb9d2.webp?size=256')
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

client.run(secrets.get('discord_token'))