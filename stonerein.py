import random
import time


class stone:
    def __init__(self): 
        self.dice=80
        self.limit=[12,12,12]
        self.suc=[0,0,0]
        self.fail=[0,0,0]
        

def trycut(index,stones):
    global dice
    
    stones.limit[index-1]-=1
    if random.random()*100<stones.dice:
        print("success\n")
        stones.suc[index-1]+=1

        if stones.dice!=0:
            stones.dice-=20
    else:
        print("fail\n")
        stones.fail[index-1]+=1
        if stones.dice!=100:
            stones.dice+=20

    return stones

def manual():
    stones=stone
    while sum(stones.limit)>0:
        try:
            printinfo()
            tryindex=int(input())
            
            if 1<=tryindex and tryindex<=3 and stones.limit[tryindex-1]==0:
                trycut(tryindex,stones)

            else:
                continue
        except:
            pass

def printinfo(stones):
    print(f"확률 : {stones.dice}%\n성공횟수 : {stones.suc}\n남은 횟수 : {stones.limit}")
    print(stones.suc[0]+stones.suc[1]-stones.suc[2])

def checktry(stones,index):
    if stones.limit[index-1]==0:
        return False
    else:
        return True

def auto():
    global dice

    stones=stone()
    while sum(stones.limit)>0:

        printinfo(stones)
        time.sleep(1)
        for i in range(3):
            if stones.dice>50:
                if stones.limit[i]>0:
                    trycut(i+1,stones)
                    break
            else:
                if stones.limit[2-i]>0:
                    trycut(2-i+1,stones)
                    break
        

def start():
    mode=input("mode입력")

    if mode=="auto":
        auto()
    elif mode=="manual":
        manual()
    else:
        exit()

