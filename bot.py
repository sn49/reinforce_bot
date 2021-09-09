import os
from discord.ext import commands
import discord
import pymysql
import random
import json
import datetime
import math
import re

bot=commands.Bot(command_prefix="r!",intents=discord.Intents.all())
token=open("token.txt").read()


sqlinfo = open("mysql.json", "r")
sqlcon = json.load(sqlinfo)
database = pymysql.connect(
    user=sqlcon["user"],
    host=sqlcon["host"],
    db=sqlcon["db"],
    charset=sqlcon["charset"],
    password=sqlcon["password"],
    autocommit=True,
)
cur = database.cursor()

@bot.command()
async def donate(ctx,user=None,amount=None):
    userid = int(re.sub(r'[^0-9]', '', user))

    sql=f"select money from info where userid={ctx.author.id}"
    cur.execute(sql)
    result=cur.fetchone()[0]

    if userid==ctx.author.id:
        await ctx.send("자기 자신에게 기부 불가")
        return

    if result>=int(amount):
        sql=f"select count(money) from info where userid={userid}"
        cur.execute(sql)
        result=cur.fetchone()[0]

        if result!=0:
            sql=f"update info set money=money-{amount} where userid={ctx.author.id}"
            sql2=f"update info set money=money+{amount} where userid={userid}"
            cur.execute(sql)
            cur.execute(sql2)
            await ctx.send(f"{ctx.author.display_name} > {bot.get_user(userid).display_name}  {amount}money 기부 완료")
        else:
            await ctx.send("존재하지 않는 유저")
    else:
        await ctx.send("기부 할 금액이 보유 금액을 초과함")

@bot.command()
async def lotto(ctx,num1=100,num2=100,num3=100):
    #숫자 범위 1~8
    price=100000
    numlist=list(range(1,9))
    

    submitlist=[int(num1),int(num2),int(num3)]

    for i in submitlist:
        if i in numlist:
            numlist.remove(i)
            print(numlist)
        else:
            pass
    if len(numlist)==5:
        sql=f"select money from info where userid={ctx.author.id}"
        cur.execute(sql)
        result=cur.fetchone()
        if result[0]>=price:
            sql=f"insert into lotto values ({ctx.author.id},{num1},{num2},{num3})"
            sql2=f"update info set money=money-{price} where userid={ctx.author.id}"
            sql3=f"update sumstats set sum=sum+{price} where name='lotto'"
            cur.execute(sql)
            cur.execute(sql2)
            cur.execute(sql3)
            await ctx.send("구매 완료")
            return
        else:
            await ctx.send("복권 구매에 10만 money 팔요")
            return
    else:
        await ctx.send("잘못 입력했습니다. 1~8 0~3개 입력, 중복 X")
        return

@bot.command()
async def bet(ctx,betno=None,amount=None):
    pick=[]
    sendtext=""
    if os.path.isfile("betinfo.txt"):
        bf=open("betinfo.txt","r",encoding="UTF-8")
        info=bf.readlines()
        subject=info[0].split(',')
        pick=subject[1:]
        sumpick={}
        sumbet=0
        betinfo={}
        sendtext+=f"{subject[0]}\n{info[1]}까지\n"
        for i in pick:
            print(i)
            sumpick[i]=0
        beter=info[2:]
        print(f"{beter}  beter")
        for j in beter:
            beti=j.split(',')
            print(f"{beti}  222222222222")
            print(f"{sumpick}  3333333333")
            sumpick[pick[int(beti[1])-1]]+=int(beti[2])

            if beti[0] in betinfo.keys():
                betinfo[beti[0]][1]+=int(beti[2])
            else:
                betinfo[beti[0]]=[int(beti[1]),int(beti[2])]
                
            
            sumbet=sum(sumpick.values())
        if betno==None:
            
            for k in sumpick.keys():
                if k=="\n":
                    continue
                if sumpick[k]==0:
                    sendtext+=f"{k} : {sumpick[k]}, ??배\n"
                else:
                    sendtext+=f"{k} : {sumpick[k]}, {sumbet/sumpick[k]}배\n"
        else:
            sumbet=sum(sumpick.values())
            try:
                betno=int(betno)
            except:
                await ctx.send("걸 번호를 입력하지 않음")
            
            if betno>len(pick) or betno<1:
                return
            else:         
                if amount==None:
                    

                    if sumpick[pick[betno-1]]==0:
                        sendtext+=f"{pick[betno-1]} : {sumpick[pick[betno-1]]}, ??배\n"
                    else:
                        sendtext+=f"{pick[betno-1]} : {sumpick[pick[betno-1]]}, {sumbet/sumpick[pick[betno-1]]}배\n"
                    sendtext+="r!bet (번호) (금액)"
                else:
                    try:
                        amount=int(amount)
                    except:
                        await ctx.send("걸 금액을 입력하지 않음")
                        return

                    sql=f"select money from info where userid={ctx.author.id}"
                    cur.execute(sql)
                    result=cur.fetchone()
                    if result[0]>=1 and result[0]<=amount:
                        if str(ctx.author.id) in betinfo.keys():
                            if betinfo[str(ctx.author.id)][0]==betno:
                                bf=open("betinfo.txt","a",encoding="UTF-8")
                                bf.write(f"\n{ctx.author.id},{betno},{amount},")
                                bf.close()
                                sql=f"update info set money=money-{amount} where userid={ctx.author.id}"
                                cur.execute(sql)
                            else:
                                await ctx.send("1개에만 걸 수 있습니다.")
                        else:
                            bf=open("betinfo.txt","a",encoding="UTF-8")
                            bf.write(f"\n{ctx.author.id},{betno},{amount},")
                            bf.close()
                    else:
                        await ctx.send("걸수없는 금액")
                        return
                    
                    

                
        await ctx.send(sendtext)
    
        
    else:
        await ctx.send("진행중인 베팅이 없습니다.")
        


@bot.command()
async def profile(ctx):
    userid=ctx.author.id
    sql=f"select * from info where userid={userid}"
    cur.execute(sql)
    result=cur.fetchone()
    sendtext=f"{ctx.author.display_name}\nlevel : {result[1]}\nmoney : {result[3]}"
    await ctx.send(sendtext)

@bot.command()
async def regist(ctx):
    userid=ctx.author.id
    sql=f"select * from info where userid={userid}"
    cur.execute(sql)
    result=cur.fetchone()
    print(result)


    if result==None:
        sql=f"insert into info (userid,level,money) values ({userid},1,1000000)"
        cur.execute(sql)
        await ctx.send(f"가입 완료")
    else:
        return

@bot.command()
async def get(ctx):
    sql=f"select lastdate from info where userid={ctx.author.id}"
    cur.execute(sql)
    result=cur.fetchone()

    now=datetime.datetime.now()
    year=now.year
    month=now.month
    day=now.day

    if result[0]==f"{year}{month}{day}":
        await ctx.send("하루 1회 가능")
        return
    else:
        getm=random.randint(500000,1100000)
        sql=f"update info set money=money+{getm},lastdate='{year}{month}{day}' where userid={ctx.author.id}"

        cur.execute(sql)
        await ctx.send(f"{getm}money 획득!")


@bot.command()
async def go(ctx):
    userid=ctx.author.id
    sql=f"select * from info where userid={userid}"
    cur.execute(sql)
    result=cur.fetchone()
    maxlevel=26
    level=result[1]

    print(level)

    if level==maxlevel:
        await ctx.send("강화를 할 수 없는 최고 레벨입니다.")
        return
    dice=random.random()*100
    
    percent=100

    need=30000+(level-1)*15000

    need=math.floor(1000*(10*level)**(0.08*level))

    if need>int(result[3]):
        await ctx.send("money가 부족합니다.")
        return
    else:
        for i in range(level):
            percent=math.floor(percent-1.8**((i+1)//6))
        success=percent
        print(success)

        if dice<success:
            sql=f"update info set level=level+1 where userid={userid}"
            await ctx.send(f"레벨이 증가하였습니다.({success}%) {level} >> {level+1}")
            cur.execute(sql)
        else:
            await ctx.send(f"아무 변화가 없었습니다.({success}%)")
        
        sql=f"update info set money=money-{need} where userid={userid}"
        cur.execute(sql)
        
            
@bot.command()
async def stat(ctx):
    sql="select count(userid),max(level), sum(money) from info"
    cur.execute(sql)
    result=cur.fetchone()

    await ctx.send(f"{result[0]}계정 사용중, 최대레벨 {result[1]}, 총 규모 : {result[2]}money")



bot.run(token)