def PDFGetter(PaperListTxT, WhereToSave):
    """
    PaperListTxT: Openacademic graf strukturajanak megfelelo strukturaju fajl, amibol az id es pdf attributumok vannak hasznalva.
    WhereToSave: A mappa utvonala, ahova a pdf-eket mentse a fuggveny. A mappanak leteznie kell.
    A fuggveny soronkent beolvassa a szoveges fajlt, minden sornal ha van pdf attributum, a linket kovetve letolti azt es egyelore
    a megadott helyre menti, nem az adatbazisba. A pdf fajlok a nevuket az id-juk alapjan kapjak.
    """
    import http.client
    import json
    with open(PaperListTxT,"r") as txt:
        #Cikkek szama
        nPapers = 0
        #Letoltott pdf-ek szama
        nPDFs = 0
        #HTTP 404 hibat adott pdf linkek szama
        notFounds = 0
        #Egyeb hibak szama
        otherFails = 0
        #Kapcsolatok nyilvantartasara hasznalt szotar
        conn = {}
        #A fajlban soronkent egy cikk szerepel
        for line in txt:
            paper = json.loads(line)
            if not paper is None:
                nPapers += 1
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
                                    f = open(WhereToSave+"\\"+paper.get("id")+".pdf","wb")
                                    f.write(data)
                                    f.close()
                                    nPDFs += 1
                                    break
                                else:
                                    raise http.client.ResponseNotReady
                            else:
                                notFounds += 1
                                break
                        except http.client.HTTPException:
                            #Hibakezeles: kapcsolat ujra felepitese. Nem probalkozik a vegtelensegig, erre szolgal az error valtozo
                            if(error > 5):
                                otherFails += 1
                                break
                            conn[host].close()
                            conn[host] = http.client.HTTPConnection(host)
                            error += 1
        #Nehany nagyon egyszeru statisztika kiirasa, nyugodtan kikommentelheto
        print("Papers: "+str(nPapers)+"; PDFs: "+str(nPDFs)+"; not found: "+str(notFounds)+"; unknown errors: "+str(otherFails))
#Pelda kod a fuggveny futtatasara
PDFGetter("c:\\Szakdoga\\aminer_papers_0.txt","c:\\Szakdoga")
