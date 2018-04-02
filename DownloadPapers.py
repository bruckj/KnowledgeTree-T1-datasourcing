def PDFGetter(PaperListTxT, WhereToSave, logFile):
    """
    PaperListTxT: Openacademic graf strukturajanak megfelelo strukturaju fajl, amibol az id es pdf attributumok vannak hasznalva.
    WhereToSave: A mappa utvonala, ahova a pdf-eket mentse a fuggveny. A mappanak leteznie kell.
    A fuggveny soronkent beolvassa a szoveges fajlt, minden sornal ha van pdf attributum, a linket kovetve letolti azt es egyelore
    a megadott helyre menti, nem az adatbazisba. A pdf fajlok a nevuket az id-juk alapjan kapjak.
    """
    import http.client
    import json
    import os
    import datetime
    #Cikkek szama
    nPapers = 0
    #Letoltott pdf-ek szama
    nPDFs = 0
    #HTTP 404 hibat adott pdf linkek szama
    notFounds = 0
    #Egyeb hibak szama
    otherFails = 0
    with open(PaperListTxT,"r") as txt:
        #Kapcsolatok nyilvantartasara hasznalt szotar
        conn = {}
        #Mar letezo fajlok listaja
        files = os.listdir(WhereToSave)
        #A fajlban soronkent egy cikk szerepel
        for line in txt:
            paper = json.loads(line)
            if not paper is None:
                nPapers += 1
                if paper.get("id")+".pdf" not in files:
                    PDF = paper.get("pdf")
                    if not PDF is None:
                        error = 0
                        while True:
                            #A linkek //valami.org/cikk.pdf alakuak
                            host = PDF.split("/")[2]
                            try:
                                if not host in conn:
                                    #A kapcsolat a fuggveny futasa alatt fenall
                                    conn[host] = http.client.HTTPConnection(host)
                                #A pdf letoltese HTTP GET uzenettel
                                conn[host].request("GET",PDF[2+len(host):])
                                res = conn[host].getresponse()
                                if(res.status != 404):
                                    data = res.read()
                                    #static.aminer.org helyrol letoltott pdf-eknel elofordul, hogy egy -napi limit betelt- uzenetet ad vissza a pdf
                                    #helyett, ezek az uzenetek 206 meretuek es mndig ugyanannal a linknel fordulnak elo
                                    if(len(data)>0 and len(data) != 206):
                                        f = open(WhereToSave+"/"+paper.get("id")+".pdf","wb")
                                        f.write(data)
                                        f.close()
                                        nPDFs += 1
                                        break
                                    else:
                                        raise http.client.ResponseNotReady
                                else:
                                    notFounds += 1
                                    break
                            except (http.client.HTTPException,ConnectionResetError):
                                #Hibakezeles: kapcsolat ujra felepitese. Nem probalkozik a vegtelensegig, erre szolgal az error valtozo
                                if(error > 5):
                                    otherFails += 1
                                    break
                                conn[host].close()
                                conn[host] = http.client.HTTPConnection(host)
                                error += 1
                #Mar levan toltve a fajl
                else:
                    nPDFs += 1
        #Nehany nagyon statisztika kiirasa (kikommentelheto)
        stats = str(datetime.datetime.now())+" "+PaperListTxT+": Papers: "+str(nPapers)+"; PDFs: "+str(nPDFs)+"; not found: "+str(notFounds)+"; unknown errors: "+str(otherFails)
        print(stats)
        with open(logFile,"a") as log:
            log.write(stats+"\n")
    return nPapers, nPDFs, notFounds, otherFails
def DownloadPapers(textDir, PDFDir, logFile):
    """
    textDir: A text fajlok helye.
    PDFDir: A mappa, ahova a PDF-ek keruljenek (ezen belul text fajlokent lesz egy almappa).
    Beolvassa a text fajlokat sorban es meghivja veluk a PDFGetter()-t
    """
    import os
    import time
    start = time.time()
    os.makedirs(name=PDFDir, exist_ok=True)
    files = os.listdir(textDir)
    #Cikkek szama
    nPapers = 0
    #Letoltott pdf-ek szama
    nPDFs = 0
    #HTTP 404 hibat adott pdf linkek szama
    notFounds = 0
    #Egyeb hibak szama
    otherFails = 0
    for elem in files:
        #csak a .txt fajlok kellenek
        if(elem.rsplit(".")[-1] == "txt"):
            dirname = elem[0:len(elem)-4]
            #mappa letrehozasa a text fajl nevevel
            os.makedirs(name=PDFDir+"/"+dirname, exist_ok=True)
            #PDF-ek letoltese
            nPapersT, nPDFsT, notFoundsT, otherFailsT = PDFGetter(textDir+"/"+elem,PDFDir+"/"+dirname,logFile)
            nPapers += nPapersT
            nPDFs += nPDFsT
            notFounds += notFoundsT
            otherFails += otherFailsT
    #Globalis statisztika kiirasa (kikommentelheto)
    stats = "Done! Statistics:\nPapers: "+str(nPapers)+"; PDFs: "+str(nPDFs)+"; not found: "+str(notFounds)+"; unknown errors: "+str(otherFails) +"\nTime [s]: "+str(time.time()-start)
    print(stats)
    with open(logFile,"a") as log:
        log.write(stats+"\n")
#A fuggveny meghivasa:
DownloadPapers("/mnt/datasharepoint/graph","/mnt/datasharepoint-pdf","./log.txt")
