import sys, os, os.path, random, csv

couleurs = []
couleurs.append("A50026")
couleurs.append("D73027")
couleurs.append("F46D43")
couleurs.append("FDAE61")
couleurs.append("FEE090")
couleurs.append("FFFFBF")
couleurs.append("E0F3F8")
couleurs.append("ABD9E9")
couleurs.append("74ADD1")
couleurs.append("4575B4")
couleurs.append("ABDDA4")

def coord(nomTxt):
    #print repr(fTxt)
    fTxt = open(nomTxt, "r")
    fTxt.readline()
    X = {}
    Y = {}
    upX = {}
    upY = {} 
    dX = {}
    dY = {}
    entier = 0
    for line in fTxt.readlines():
    #print line
        maLigne = line.split("\t")
       # print maLigne
#ATTENTION CES PARAM DEPENDENT DES DONNEES QUI ONT ETE EXPORTEES
        X[(int(maLigne[0]), int(maLigne[1]))]=int(maLigne[-6])
        Y[(int(maLigne[0]), int(maLigne[1]))]=int(maLigne[-5])
        upX[(int(maLigne[0]), int(maLigne[1]))]=int(maLigne[-4])
        upY[(int(maLigne[0]), int(maLigne[1]))]=int(maLigne[-3])
        dX[(int(maLigne[0]), int(maLigne[1]))]=int(maLigne[-2])
        dY[(int(maLigne[0]), int(maLigne[1]))]=int(maLigne[-1])
 #       print Y
 #       entier +=1
 #       if entier > 9: break
    fTxt.close()
    return (X,Y, upX, upY, dX, dY)

def lireDot(nomDot, X, Y):
    fDot = open(nomDot, "r")

    mesLignes=fDot.readlines()
    fDot.close()
    del mesLignes[0:3]
    mesLignes.reverse()

    continuer = True
    ensembleTraj = ensTraj()
    print ensembleTraj.numMitoses
    print ensembleTraj.lstTraj

    trajCourante = trajectoire(0,0,0,0,0)
    frameSuivante =-1
    idSuivante =-1

    while continuer:
        ligneCourante=mesLignes.pop()
        if ("#AAAAAA" in ligneCourante):
            continuer = False
            continue

        decomp = ligneCourante.split(" ")
        decomp[0]=decomp[0][1:-1]

        frameCourante = int(decomp[0].split("_")[0])
        idCourante = int(decomp[0].split("_")[1])
        decomp[2]=decomp[2][1:-1]

   
        if (int(frameCourante) != int(frameSuivante) or int(idCourante) != int(idSuivante)):
            trajectoires = ensembleTraj.trouver(trajCourante.numCellule)
            lstPointsTotale = []
            for trajec in trajectoires.lstTraj:
                for element in trajec.lstPoints.keys():
                    #print element
                    lstPointsTotale.append(element)

            #if lstPointsTotale <> []: print lstPointsTotale
            if (frameCourante, idCourante) in lstPointsTotale or (frameCourante, idCourante) in trajCourante.lstPoints.keys():
                print "mitose", frameCourante, idCourante
                trajCourante.mitose = 1
                ensembleTraj.numMitoses +=1
                ensembleTraj.ajouter(trajCourante)
                num = trajCourante.numCellule
  #              print num
                trajCourante.supp()
                trajCourante = trajectoire(X[(frameCourante, idCourante)], Y[(frameCourante, idCourante)], frameCourante, num, idCourante)
                trajCourante.mitose = 1

            else:
   #             print "nouvelle trajectoire", frameCourante, idCourante
                ensembleTraj.ajouter(trajCourante)
                num = trajCourante.numCellule+1

                trajCourante.supp()

                trajCourante = trajectoire(X[(frameCourante, idCourante)], Y[(frameCourante, idCourante)], frameCourante, num, idCourante)             
#                print trajCourante.lstPoints

        else:
 #           print "ajout point"
            trajCourante.ajoutPoint(X[(frameCourante, idCourante)], Y[(frameCourante, idCourante)], frameCourante, idCourante)
  #          print trajCourante.lstPoints
     

        frameSuivante = decomp[2].split("_")[0]
        idSuivante = decomp[2].split("_")[1]

    ensembleTraj.ajouter(trajCourante)

    return ensembleTraj

def ecrireClassDef():
    fichierT = open("class_definition.txt", "w")
    ecrivain = csv.writer(fichierT, delimiter='\t', quoting=csv.QUOTE_NONE)
    
    for i in range(5):
        ecrivain.writerow([i+1, "MCellule"+str(i), "#"+couleurs[i]])

    for j in range(6):
        ecrivain.writerow([j+6, "Cellule"+str(j), "#"+couleurs[j+5]])
    fichierT.close()
    return



def sortiesCarre(nomFichier, ensembleTraj):

    compteur = 11
    MIN = 200
    absmax=300
    ordmax = 300
    MAX = 1000
    PAS = 150
    iterationX = 0
    iterationY=0

    fichierX = open(nomFichier, "w")
    fichierX.write(initXml())
 
    nbDansBoiteMax = 0
    absFinale = 0
    ordFinale = 0

    while absmax <= MAX:
        absmin = MIN + iterationX*PAS
        absmax = MIN + (iterationX+1)*PAS
        while ordmax<=MAX:
            ordmin = MIN + iterationY*PAS
            ordmax = MIN + (iterationY+1)*PAS
            nbDansBoite = 0
            listeCellulesVues = []
                
            for trajectoire in ensembleTraj.lstTraj:
                keyList = trajectoire.lstPoints.keys()
        #try:
                debutFrame =100
                (xi, yi)=(0,0)
                for i in keyList:
                    if int(i[0])<=debutFrame:
                        debutFrame = int(i[0])
                        debutId = i[1]
                        (xi, yi)=trajectoire.lstPoints[(debutFrame, debutId)]

                    if xi>absmin and xi<absmax and yi>ordmin and yi<ordmax and trajectoire.numCellule not in listeCellulesVues:
                        #print "Cellule numero "+str(trajectoire.numCellule)+" dans la boite ("+str(absmin)+", "+str(ordmin)+")"
                        nbDansBoite +=1
                        listeCellulesVues.append(trajectoire.numCellule)
           # print listeCellulesVues
               
            if nbDansBoite > nbDansBoiteMax:
                absFinale = absmin
                ordFinale = ordmin
                #print listeCellulesVues
                listeCellulesVuesMax = []
                for num in listeCellulesVues : listeCellulesVuesMax.append(num)
 #               listeCelluleVuesMax = listeCellulesVues
                #print listeCellulesVuesMax
                nbDansBoiteMax = nbDansBoite
            iterationY+=1
        iterationY=0
        ordmax = 300
        iterationX+=1

    print "Finalement : "+str(nbDansBoiteMax)+" dans la boite ("+str(absFinale)+", "+str(ordFinale)+")"
    print listeCellulesVuesMax

   
    for numCellule in listeCellulesVuesMax:
        if compteur<=0:
            break
        else:
            print numCellule
            trajectoires = ensembleTraj.trouver(numCellule)
            try:
                for trajectoire in trajectoires.lstTraj:
                    if trajectoire.mitose == 1:
                        fichierX.write(ecrireXmlM(trajectoire.numCellule, compteur, ensembleTraj))
                        break
                    else:
                        fichierX.write(ecrireXml(compteur,trajectoire))
                compteur-=1
            except:
                print "il y a un probleme entre les numeros des cellules trouvees et les cellules presentes dans la liste de trajectoires."

        #except:
         #   print keyList
    fichierX.write(finirXml())
    fichierX.close()
    return


def sortiesRandom(nomFichier, ensembleTraj):

    compteurM = 5
    compteurN = 6
    listeCellulesMitosesVues = []

    fichierX = open(nomFichier, "w")
    fichierX.write(initXml())

    for trajectoire in ensembleTraj.lstTraj:

        if trajectoire.mitose == 1 and trajectoire.numCellule not in listeCellulesMitosesVues and compteurM>0:
            randM = random.randint(1,10)
            if randM == 1:

                fichierX.write(ecrireXmlM(trajectoire.numCellule, compteurM, ensembleTraj))
                #fichierX.write(ecrireXml(compteurM,trajectoire))

                listeCellulesMitosesVues.append(trajectoire.numCellule)
                compteurM -=1

        elif trajectoire.numCellule not in listeCellulesMitosesVues and compteurN>0:
            randN = random.randint(1,10)
            if randN == 1:
                fichierX.write(ecrireXml(compteurN+5,trajectoire))

                compteurN -=1

    fichierX.write(finirXml())
    fichierX.close()
    return

   


def initXml():
    return "<?xml version=\"1.0\" encoding=\"utf8\"?>\n  <CellCounter_Marker_File>\n    <Marker_Data>"

def finirXml():
    return "\n    </Marker_Data>\n  </CellCounter_Marker_File> "

def ecrireXml(ligne, trajectoire):
    result = "\n      <Marker_Type>\n        <Type>{0}</Type>".format(ligne)
    
    for point in trajectoire.lstPoints:
        numFramePourXml = point[0]+1
        
        result+="\n        <Marker>\n          <MarkerX>{1}</MarkerX>\n          <MarkerY>{2}</MarkerY>\n          <MarkerZ>{0}</MarkerZ>\n        </Marker>".format(numFramePourXml, trajectoire.lstPoints[point][0], trajectoire.lstPoints[point][1])
        
    result+="\n      </Marker_Type>"
    return result

def trouverCellulesFilles(num, ensemTraj):
        sousEns = ensTraj()
        print num
        print len(ensemTraj.lstTraj)
        for trajectoire in ensemTraj.lstTraj:
            print len(ensemTraj.lstTraj)
           # print "premiereboucle"
            print trajectoire.numCellule
            if int(trajectoire.numCellule) == int(num):
                print "seconde boucle"
                sousEns.ajouter(trajectoire)

        return sousEns

def ecrireXmlM(num, ligne, ensembleTraj):
    result = ""
    for traj in ensembleTraj.lstTraj:
#        print traj.numCellule
        if int(traj.numCellule) == int(num):
    #        print "ici"
            result += ecrireXml(ligne, traj)

    return result

class trajectoire():
    mitose = -1

    def __init__(self, xi, yi, frame, num, idC):
   #     print "creation d'une trajectoire"
        self.numCellule = num
        self.lstPoints = {}
        self.lstPoints[(frame, idC)]=(xi, yi)

    def ajoutPoint(self, x, y, frame, idC):
        self.lstPoints[(frame, idC)]=(x,y)

    def findFrame(self, frame):
        result = []
        for point in self.lstPoints:
            if int(point[0])==int(frame):
                result.append(point[1])
        return result
            
    def supp(self):
    #    print "suppression de trajectoire"
        self.lstPoints = {}
        self.mitose = -1
        

class ensTraj(object):
    def __init__(self):
        self.numMitoses = 0
        self.lstTraj = []

    def ajouter(self, traj):
     #   print "ajout d'une trajectoire"
        mit = traj.mitose
        num = traj.numCellule
        points = traj.lstPoints
        copieTraj = trajectoire(0,0,0,num,0)
        copieTraj.mitose = mit
        for point in points:
            copieTraj.lstPoints[point]=points[point]
        del copieTraj.lstPoints[(0,0)]
       # liste
        self.lstTraj.append(copieTraj)

    def trouver(self, numC):
        result = ensTraj()
        for traj in self.lstTraj:
            if traj.numCellule ==numC:
                #print "c'est fait de trouver la cellule "+str(numC)
                result.ajouter(traj)
        return result


        #    def get(self, num): COMPRENDRE POURQUOI CELA FAIT UNE BOUCLE INFINIE DANS LE IF !!
#        sousEns = ensTraj()
 #       print num
  #      print len(self.lstTraj)
   #     for trajectoire in self.lstTraj:
           # print "premiereboucle"
            #print trajectoire.numCellule
    #        if int(trajectoire.numCellule) == int(num):
     #           print "seconde boucle"
               # sousEns.ajouter(trajectoire)

      #  return sousEns


def Hacktrack(plaque, puits, dossierSauvegarde):
    dossier = "/bioinfo/users/aschoena/projects/groundtruth/results/controls/"+plaque+"/analyzed/"+puits+"/statistics"
    print "Numero de plaque :"+plaque+" numero de puits : "+ puits

    nomDot = dossier + ("/tracking_graph___P%s.dot" % puits)    
    nomTxt =  dossier + ("/tracking_graph___P%s_features.txt" % puits)

    nomFichier = "PL"+plaque+"___P"+puits+"___T00000.xml"
    nomFichier = dossierSauvegarde+"/"+nomFichier

    try:
        (X,Y) = (coord(nomTxt)[0],coord(nomTxt)[1])
        ensemTraj = lireDot(nomDot, X, Y)
        print ensemTraj.numMitoses
        sortiesCarre(nomFichier, ensemTraj)
    except IOError as e :
        print "probleme fichier"+e.message


    ecrireClassDef()
    return
