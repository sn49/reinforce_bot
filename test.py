import random
import time

grade=1
level=1

while (grade<11 or level<10):
    dice=random.random()*100
    success=95-(grade-1)*3.8-(level-1)*(3+(grade-1)*0.4)
    if dice<success:
        if level==10:
            grade+=1
            level=1
        else:
            level+=1
    else:
        dice=random.random()*10

        if dice<7:
            pass
        elif dice<9:
            if level!=1:
                level-=1
            else:
                pass
            
        else:
            grade=1
            level=1
    print(f"{grade} {level}")
    time.sleep(0.1)