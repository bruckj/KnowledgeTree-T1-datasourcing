#Athelyezi a pdf-eket az almappakbol, majd torli az ures mappakat
import os
import time
startdir="c:/Szakdoga/testmove"
dirs = os.listdir(startdir)
moveCount = 0
idCollision = 0
#Fajlok athelyezese:
for dir in dirs:
    if(os.path.isdir(startdir+"/"+dir)):
        pdfs = os.listdir(startdir+"/"+dir)
        for pdf in pdfs:
            try:
                if(os.path.isdir(startdir+"/"+dir+"/"+pdf)):
                   continue
                #Az athelyezes itt tortenik
                os.rename(startdir+"/"+dir+"/"+pdf,startdir+"/"+pdf)
                moveCount += 1
            except BlockingIOError:
                time.sleep(5)
            except NotADirectoryError:
                continue
            except FileExistsError:
                #Ha mar letezik a fajl, akkor ket kulonbozo fajlnak egy id-je van (ugyanaz a neve)
                with open("./MoveLog.txt","a") as log:
                    log.write(dir+"/"+pdf+"\n")
                idCollision += 1
#Ures mappak torlese:
for dir in dirs:
    if(os.path.isdir(startdir+"/"+dir)):
        if(len(os.listdir(startdir+"/"+dir)) == 0):
            try:
                os.removedirs(startdir+"/"+dir)
            except FileNotFoundError:
                continue
print("Moved: "+str(moveCount)+" id collision: "+str(idCollision)+".")
if(idCollision > 0):
    print("See \"./MoveLog.txt\" for details.")
