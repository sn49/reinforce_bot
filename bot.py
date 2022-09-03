import os
from discord.ext import commands
import discord
import pymysql
import random
import json
import datetime
import math
import re
import stonerein

bot=commands.Bot(command_prefix="r!",intents=discord.Intents.all())
token=open("token.txt").read()


sqlinfo = open("mysql.json", "r")
sqlcon = json.load(sqlinfo)

testinput=input("test모드 > test 입력")
dbname=""
if testinput=="test":
    dbname="testdb"
    print()
    print("test모드")
else:
    dbname="db"
    
database = pymysql.connect(
    user=sqlcon["user"],
    host=sqlcon["host"],
    db=sqlcon[dbname],
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
async def checklotto(ctx):
    print(bot.owner_id)
    if ctx.author.id==sqlcon["owner"]:
        numlist=list(range(1,9))
        result=random.sample(numlist,3)

        price=[]
        getprice={}

        sql=f"select * from lotto"
        cur.execute(sql)
        alldata=cur.fetchall()

        print(result)

        for i in alldata:
            templist=[i[1],i[2],i[3]]

            print(templist)
            print(result)
            
            same=list(set(templist).intersection(result))
            print(same)

            if len(same)>1:
                if not i[0] in price:
                    price.extend([i[0],[0,0,0]])
                index=price.index(i[0])
                price[index+1][len(same)-1]+=1
        
        print(price)
        
        sql=f"select sum from sumstats where name='lotto'"
        cur.execute(sql)
        sumlotto=cur.fetchone()[0]
        totalprice=[math.floor(sumlotto*0.1),math.floor(sumlotto*0.2),math.floor(sumlotto*0.6)]
        givetotal=0

        getamount=[0,0,0]
        getid=""
        for i in range(len(price)):
            if i%2==0:
                getid=str(price[i])
                getprice[getid]=0
            else:
                for j in range(3):
                    getamount[j]+=price[i][j]
        print(getamount)

        for i in range(len(price)):
            if i%2==0:
                getid=str(price[i])
            else:
                for j in range(3):
                    if getamount[j]!=0:
                        getprice[getid]+=totalprice[j]//getamount[j]*price[i][j]
                        givetotal+=totalprice[j]//getamount[j]*price[i][j]

        print(getprice)
        print(givetotal)

        for k,v in getprice.items():
            sql=f"update info set money=money+{v} where userid={int(k)}"
            cur.execute(sql)

            
            await bot.get_user(int(k)).send(f"{v}money 획득! 3등,2등,1등 {price[price.index(int(k))+1]}")

        sql=f"truncate lotto"
        sql2=f"update sumstats set sum=sum-{givetotal} where name='lotto'"

        cur.execute(sql)
        cur.execute(sql2)

        await ctx.send(f"당첨 번호 : {result}")

tempresult=""

@bot.command()
async def checkbet(ctx,filename=None,result=None):
    global tempresult
    if ctx.author.id==sqlcon["owner"]:
        totalbetinfo=[]
        pick=[]
        sendtext=""
        filename=f"betinfo - {filename}.txt"
        if os.path.isfile(filename):
            bf=open(filename,"r",encoding="UTF-8")
            info=bf.readlines()
            bf.close()
            subject=info[0].split(',')
            pick=subject[1:]
            sumpick={}
            sumbet=0
            betinfo={}
            sendtext+=f"{subject[0]}\n{info[1]}까지\n"
            for i in pick:
                print(i)
                sumpick[i]=0

            

            if tempresult=="":
                tempresult=result
                await ctx.send(f"{pick[int(tempresult)-1]}이 맞다면 한번더 입력")
            elif tempresult==result:
                tempresult=""
                pass
            else:
                tempresult=""
                await ctx.send("다시 결과 입력")
                return
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
                cid=int(beti[0])
                cpick=int(beti[1])
                camount=int(beti[2])
                if cid in totalbetinfo:

                    index=totalbetinfo.index(cid)
                    totalbetinfo[index+1][1]+=camount
                else:
                    totalbetinfo.extend([cid,[cpick,camount]])
                    
                
            sumbet=sum(sumpick.values())

            for k in sumpick.keys():
                if k=="\n":
                    continue
                if sumpick[k]==0:
                    sendtext+=f"{k} : {sumpick[k]}, ??배\n"
                else:
                    sendtext+=f"{k} : {sumpick[k]}, {sumbet/sumpick[k]}배\n"


            print(totalbetinfo)
            await ctx.send(sendtext)

    
            result=int(result)
            correct=[]
            
            for i in range(len(totalbetinfo)//2):
                if totalbetinfo[i*2+1][0]==result:
                    gop=sumbet/list(sumpick.values())[result-1]
                    getmoney=totalbetinfo[i*2+1][1]*gop
                    sql=f"update info set money=money+{getmoney} where userid={totalbetinfo[i*2]}"
                    cur.execute(sql)
            os.remove(filename)


class userstone:
    def __init__(self) :
        self.stoneinfo=stonerein.stone()
        self.stonemsg=None
        self.sumcost=0
totalinfo={}
stonemessage={}


def checkmoney(ctx,cost):
    sql=f"select money from info where userid={ctx.author.id}"
    cur.execute(sql)
    result=cur.fetchone()
    if result[0]>=cost:
        return True
    
    return False

@bot.command()
async def stone(ctx,index=None,cost=0):
    global totalinfo
    global stonemessage


    userid=str(ctx.author.id)
    if userid in totalinfo.keys():
        if index==None:
            await ctx.send("깎을 줄 번호를 입력")
            return
        else:
            index=int(index)

            if 1<=index and index<=3:
                if int(cost)%1000==0 and int(cost)>=0:
                    canstone=checkmoney(ctx,int(cost))
                    if canstone:
                        
                        if stonerein.checktry(totalinfo[userid].stoneinfo,int(index)):
                            sql=f"update info set money=money-{cost} where userid={ctx.author.id}"
                            cur.execute(sql)
                            totalinfo[userid].sumcost+=int(cost)
                            stonerein.trycut(index,totalinfo[userid].stoneinfo)
                else:
                    await ctx.send("0이상 1000단위 입력")
    else:
        totalinfo[str(ctx.author.id)]=userstone()

    sendtext=f"{ctx.author.display_name}의 돌(누적 비용 : {totalinfo[userid].sumcost})\n확률 : {totalinfo[userid].stoneinfo.dice}%\n"
    for i in range(3):
        for j in range(12):
            if j < totalinfo[userid].stoneinfo.suc[i]:
                if i<=1:
                    sendtext+="🔵"
                else:
                    sendtext+="🔴"
            elif j < totalinfo[userid].stoneinfo.suc[i]+totalinfo[userid].stoneinfo.fail[i]:
                sendtext+="⚫"
            else:
                sendtext+="⚪"
                    
            
        sendtext+=f"   {totalinfo[userid].stoneinfo.limit[i]}회 남음\n"
    sendtext+=f"{totalinfo[userid].stoneinfo.suc[0]+totalinfo[userid].stoneinfo.suc[1]-totalinfo[userid].stoneinfo.suc[2]}점({checkstone(totalinfo[userid])})"

    
    if totalinfo[str(ctx.author.id)].stonemsg!=None:
        await totalinfo[userid].stonemsg.edit(content=sendtext)
    else:
        totalinfo[userid].stonemsg = await ctx.send(sendtext)

    
    await ctx.message.delete()

    if sum(totalinfo[userid].stoneinfo.limit)==0:
        getmoney=checkstone(totalinfo[userid])
        await ctx.send(f"getmoney : {getmoney}")
        sql=f"update info set money=money+{getmoney} where userid={ctx.author.id}"
        cur.execute(sql)
        del totalinfo[userid]

def checkstone(userinfo):
    score=userinfo.stoneinfo.suc[0]+userinfo.stoneinfo.suc[1]-userinfo.stoneinfo.suc[2]

    getmoney=0

    if score>=20:
        getmoney=userinfo.sumcost*2.6
    elif score>=18:
        getmoney=userinfo.sumcost*2.1
    elif score>=16:
        getmoney=userinfo.sumcost*1.7
    elif score>=14:
        getmoney=userinfo.sumcost*1.4
    elif score>=12:
        getmoney=userinfo.sumcost*1.2
    elif score>=10:
        getmoney=userinfo.sumcost*1.1

    if userinfo.stoneinfo.suc[0]>=9:
        getmoney*=1.3
    
    if userinfo.stoneinfo.suc[1]>=9:
        getmoney*=1.3

    return getmoney
    

@bot.command()
async def lotto(ctx,num1=100,num2=100,num3=100):
    #숫자 범위 1~8
    price=100000
    numlist=list(range(1,9))
    

    submitlist=[int(num1),int(num2),int(num3)]
    index=0
    for i in submitlist:
        pickn=0
        if i==100:
            pickn=random.choice(numlist)
            submitlist[index]=pickn
        
        else:
            pickn=i
            pass
        numlist.remove(pickn)
        print(numlist)
        index+=1
    if len(numlist)==5:
        sql=f"select money from info where userid={ctx.author.id}"
        cur.execute(sql)
        result=cur.fetchone()
        if result[0]>=price:
            sql=f"insert into lotto values ({ctx.author.id},{submitlist[0]},{submitlist[1]},{submitlist[2]})"
            sql2=f"update info set money=money-{price} where userid={ctx.author.id}"
            sql3=f"update sumstats set sum=sum+{price} where name='lotto'"
            cur.execute(sql)
            cur.execute(sql2)
            cur.execute(sql3)
            await ctx.send(f"구매 완료 {submitlist}")
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
        bf.close()
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
                    if 1<=amount and amount<=result[0]:
                        if str(ctx.author.id) in betinfo.keys():
                            if betinfo[str(ctx.author.id)][0]==betno:
                                bf=open("betinfo.txt","a",encoding="UTF-8")
                                bf.write(f"\n{ctx.author.id},{betno},{amount},")
                                bf.close()
                                
                            else:
                                await ctx.send("1개에만 걸 수 있습니다.")
                        else:
                            bf=open("betinfo.txt","a",encoding="UTF-8")
                            bf.write(f"\n{ctx.author.id},{betno},{amount},")
                            bf.close()
                        sql=f"update info set money=money-{amount} where userid={ctx.author.id}"
                        cur.execute(sql)
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
async def rank(ctx):
    sql=f"select * from info order by level desc"
    cur.execute(sql)
    result=cur.fetchall()
    sendtext=""

    for r in result:
        username=bot.get_user(r[0]).display_name
        sendtext+=f"{username} : {r[1]}level {r[3]}money\n"

    await ctx.send(sendtext)

@bot.command()
async def regist(ctx):
    userid=ctx.author.id
    sql=f"select * from info where userid={userid}"
    cur.execute(sql)
    result=cur.fetchone()
    print(result)

    startmoney=3000000

    if result==None:
        sql=f"insert into info (userid,level,money) values ({userid},1,{startmoney})"
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
async def lottostat(ctx):
    sql=f"select sum from sumstats where name='lotto'"
    cur.execute(sql)
    result=cur.fetchone()

    await ctx.send(f"누적액 : {result[0]}, 1등 당첨시 {result[0]*0.6}, 2등 당첨시 {result[0]*0.2}, 3등 당첨시 {result[0]*0.1}")
            
@bot.command()
async def stat(ctx):
    sql="select count(userid),max(level), sum(money) from info"
    cur.execute(sql)
    result=cur.fetchone()

    await ctx.send(f"{result[0]}계정 사용중, 최대레벨 {result[1]}, 총 규모 : {result[2]}money")



bot.run(token)