import discord
import json
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True  # 멤버 관련 이벤트 처리
intents.message_content = True  # 메시지 콘텐츠 처리

bot = commands.Bot(command_prefix="!", intents=intents)

# 정회원 기록을 저장할 JSON 파일 로드
def load_members():
    try:
        with open("members.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

# 정회원 기록을 저장
def save_members(data):
    with open("members.json", "w") as f:
        json.dump(data, f)

# 봇이 준비되었을 때
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

# 유저가 서버에 입장할 때 "준회원" 또는 "정회원" 역할 부여
@bot.event
async def on_member_join(member):
    try:
        # 준회원 역할 부여
        role = discord.utils.get(member.guild.roles, name='준회원')
        if role:
            await member.add_roles(role)

        # DM 보내기
        await member.send("환영합니다! 정회원 등록을 위해 닉네임과 휴대폰 번호를 입력해주세요.\n\n"
                          "입력 형식:\n"
                          "게임 닉네임과 휴대폰 번호를 공백으로 구분하여 입력해 주세요.\n"
                          "예시: 닉네임 01077778888")

        # 사용자 응답 기다리기
        def check(msg):
            return msg.author == member and isinstance(msg.channel, discord.DMChannel)

        try:
            msg = await bot.wait_for('message', timeout=300.0, check=check)
            content = msg.content.split()
            
            if len(content) == 2:
                닉네임 = content[0].strip()
                번호 = content[1].strip()

                if len(번호) == 11:  # 11자리 휴대폰 번호 검증
                    try:
                        await member.edit(nick=닉네임)  # 닉네임 변경
                        role = discord.utils.get(member.guild.roles, name="정회원")
                        준회원_role = discord.utils.get(member.guild.roles, name='준회원')

                        if role:
                            await member.add_roles(role)  # 정회원 역할 부여
                        if 준회원_role:
                            await member.remove_roles(준회원_role)  # 준회원 역할 제거

                        # 정회원으로 기록하기
                        members = load_members()
                        members[str(member.id)] = "정회원"
                        save_members(members)

                        await member.send(f"닉네임이 {닉네임}으로 변경되고 정회원으로 등록되었습니다!")

                        # 가입 인사 채널에 메시지 보내기
                        welcome_channel = discord.utils.get(member.guild.text_channels, name='╭🪪║가입인사')  # 채널 이름을 확인하세요
                        if welcome_channel:
                            await welcome_channel.send(
                                f"{member.mention}님 어서오세요! 정회원이 되신 걸 축하드립니다.\n\n"
                                "☆서버 정보☆\n"
                                "버프시간   : 10시간 유지\n"
                                "계정정보   : 9 계정 가능\n"
                                "서버정보   : IDC DDOS 방어존\n"
                                "서버특화   : 오전 12시, 오후 8시 핫타임 이벤트\n"
                                "서버드랍   : 20레벨 부터 S급 획득 (공지시스템)\n"
                                "서버이벤트 : 매일 6시간마다 랜덤 보스 이벤트\n"
                                "출석이벤트 : 매일매일 새로운 아이템 지급\n"
                                "접속이벤트 : 접속 코인으로 상품 구입 가능\n"
                                "클라이언트 : 다운로드널 통클라이언트&런처 다운 가능"
                            )
                    except discord.Forbidden:
                        await member.send("닉네임을 변경할 권한이 없습니다.")
                else:
                    await member.send("유효한 11자리 휴대폰 번호를 입력해주세요.")
            else:
                await member.send("입력 형식이 올바르지 않습니다. 예시 형식에 맞게 입력해 주세요.")
        except asyncio.TimeoutError:
            await member.send("시간 초과: 정회원 등록을 위한 정보 입력 시간이 초과되었습니다.")

    except discord.Forbidden:
        print(f"{member.name}님에게 DM을 보낼 수 없습니다.")

bot.run('MTI4MzM5Mjg0NTIzNDgzMTQzMg.G9qjHz.gnsUaGD8XoVQP2Rcw4nlU7ilClNJceVg4jdOmM')
