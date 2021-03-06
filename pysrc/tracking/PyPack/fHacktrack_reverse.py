import sys, os, os.path, random, csv
import vigra, numpy
from fHacktrack2 import ensTraj
from fHacktrack2 import trajectoire
from fHacktrack2 import coord

LENGTH = 93
EVENTS = []
EVENTS.append("move")
EVENTS.append("appear")
EVENTS.append("disappear")
EVENTS.append("merge")
EVENTS.append("split")

def lireTrajectoires(nomFichier, nomTxt):
    (X, Y, upX, upY, dX, dY) = coord(nomTxt)
    frameLabels = X.keys()

    fichierX =  open(nomFichier, "r")
    listK = []
    ensembleTraj = ensTraj()
    traj = trajectoire(0,0,0,0,0)
    k=0
    continuer = True
    mesLignes = fichierX.readlines()
    mesLignes.reverse()

    while continuer:
        ligneCourante = mesLignes.pop()
        #print ligneCourante
        if "<Type>" in ligneCourante:
            if not ensembleTraj.lstTraj==[]:
                traj.ajoutPoint(0, 0, frame+1, -2)

            ensembleTraj.ajouter(traj)
           # print ligneCourante
            k = int(ligneCourante[14:-8])
            #print k
            listK.append(k)
            nouveau = True

        elif "<MarkerX>" in ligneCourante:
            xi = int(ligneCourante[19:-11])
            ligne2 = mesLignes.pop()
            yi = int(ligne2[19:-11])
            ligne3 = mesLignes.pop()
            frame = int(ligne3[19:-11])-1
            #print xi, yi, frame

            for f in frameLabels:
                if int(f[0])==int(frame):
                    upxi =int(upX[f])
                    dxi=int(dX[f])
                    upyi = int(upY[f])
                    dyi=int(dY[f])
                    #print "ici", upxi, upyi, dxi, dyi
                    if int(dxi)>=int(xi) and int(xi)>=int(upxi) and int(dyi)>=int(yi) and int(yi)>=int(upyi):
                        l = f[1]
                        #if frame == 91 or frame==92: print "TROUVE "+ str(dxi), upxi, xi, dyi, upyi, yi, l, frame

            if nouveau:
              #  print "ajout de la trajectoire "+str(k)
                if int(frame)>0:
                    traj = trajectoire(k, 0, 0, frame-1, -1)
                    traj.ajoutPoint(xi, yi, frame, l)
                else: 
                    traj = trajectoire(k, xi, yi, frame, l)
               # ensembleTraj.ajouter(traj)

            else:
                #traj= ensembleTraj.trouver(k).lstTraj[0]
                traj.ajoutPoint(xi, yi, frame, l)

            nouveau = False

        elif "</Marker_Data>" in ligneCourante:
            traj.ajoutPoint(0, 0, frame+1, -2)
            ensembleTraj.ajouter(traj)
            continuer = False

 #   for traj in ensembleTraj.lstTraj: print traj.lstPoints

    fichierX.close()
    return ensembleTraj

def ecrireTraining(ensembleTraj, fileToSave):
    solutions = {}
#    solutions[0]={}
    fileS=open(fileToSave, "w")
    going = {}
    coming = {}
    appearCandidates = {}
    disappearCandidates = {}

    for trajectoire in ensembleTraj.lstTraj:
        frameLabels = sorted(trajectoire.lstPoints.iterkeys())
        lastLabels = []
        lastFrame = -1
        lastMoveSplit = [False for x in range(100)]

        for f in frameLabels:
            frame = int(f[0])
            nextFrame = frame+1

            if nextFrame==LENGTH:
                #if not nextFrame in coming:
                 #   coming[nextFrame]=[]
                # for label in lastLabels: 
                 #   coming[nextFrame].append(label)
                break

            if lastLabels == []:
                lastLabels=trajectoire.findFrame(frame)

            if frame == lastFrame:
                continue

 #           if frame > lastFrame+1:
  #             appearCandidates[lastLabels[0]]=frame

            nextLabels = trajectoire.findFrame(nextFrame)

            if not frame in solutions:
                solutions[frame]={}

            l = len(lastLabels)
            nextL = len(nextLabels)
            #print "FRAME :"+str(frame),l, nextL, lastLabels, nextLabels, trajectoire.numCellule


            if int(l)==int(nextL):
                if int(l)==1 and int(lastLabels[0])==-1:
                    appearing = nextLabels[0]
                    if not nextFrame in appearCandidates:
                        appearCandidates[nextFrame]=[]
                    appearCandidates[nextFrame].append(appearing)

                elif int(l)==1 and int(nextLabels[0])==-2:
                    disappearing = lastLabels[0]
                    if not frame in disappearCandidates:
                        disappearCandidates[frame]=[]
                    disappearCandidates[frame].append(disappearing)
                    #continue

                elif int(l)==1:
                    #print "MOVE"
                #lastMoveSplit = False
                
                    if not "move" in solutions[frame]:
                        solutions[frame]["move"]=[[], []]

                    solutions[frame]["move"][0].append(lastLabels)
                    solutions[frame]["move"][1].append(nextLabels)
                    if not nextFrame in coming:
                        coming[nextFrame]=[]
                    for label in nextLabels: 
                        coming[nextFrame].append(label)
                        
                    if not frame in going:
                        going[frame]=[]
                    for label in lastLabels:
                        going[frame].append(label)

                else:
                    print "problem", lastLabels, nextLabels, frame
                    raise

            else:
#             if int(nextL)==0:
                print "problem at frame "+str(frame), lastLabels, nextLabels
                raise

#                elif  int(nextL)>=2:
#                    lastMoveSplit[nextFrame] = True
#                    #print "SPLIT", lastMoveSplit[nextFrame]
#
#                    if not "split" in solutions[frame]:
#                        solutions[frame]["split"]=[[], []]
#
#                    solutions[frame]["split"][0].append(lastLabels)
#                    solutions[frame]["split"][1].append(nextLabels)
#                    if not nextFrame in coming:
#                        coming[nextFrame]=[]
#                    for label in nextLabels: 
#                        coming[nextFrame].append(label)
#                    if not frame in going:
#                        going[frame]=[]
#                    for label in lastLabels:
#                        going[frame].append(label)
#
#                else:
#                   print "one cell PBL at t="+str(frame)
#                  raise

#            elif int(l)>=2:
#                if int(nextL)==1:
#                    print "FRAME :"+str(frame), lastLabels, nextLabels, trajectoire.numCellule, lastMoveSplit[frame]
#                    if lastMoveSplit[frame]:
#                        xmin = 100
#                        ymin = 100
#                        labelmin = 0
#                        xf = trajectoire.lstPoints[(nextFrame, nextLabels[0])][0]
#                        yf = trajectoire.lstPoints[(nextFrame, nextLabels[0])][1]
#                        for label in lastLabels:
#                            x = abs(int(xf) - int(trajectoire.lstPoints[(frame, label)][0]))
#                            y = abs(int(yf) - int(trajectoire.lstPoints[(frame, label)][1]))
#                            if int(x)<int(xmin) and int(y)<int(ymin):
#                                labelmin = label
#                                xmin = x
#                                ymin = y
#
#                        if labelmin == 0:
#                            print "lastMoveSplit recognition problem at t="+str(frame)
#                            raise
#
#                        #print "MOVE"
#                        # lastMoveSplit = False
#                        if not "move" in solutions[frame]:
#                            solutions[frame]["move"]=[[], []]
#
#                        lastLabels = [labelmin]
#                        solutions[frame]["move"][0].append(lastLabels)
#                        solutions[frame]["move"][1].append(nextLabels)
#                       
#                        if not nextFrame in coming:
#                            coming[nextFrame]=[]
#                        for label in nextLabels: 
#                            coming[nextFrame].append(label)
#                        if not frame in going:
#                            going[frame]=[]
#                        for label in lastLabels:
#                            going[frame].append(label)
#
#                    else:
#                        print "problem"
#                        raise
#                        
                       # if not "merge" in solutions[frame]:
                        #    solutions[frame]["merge"]=[[], []]

                       # solutions[frame]["merge"][0].append(lastLabels)
                        #solutions[frame]["merge"][1].append(nextLabels)
   #                     if not frame in mergedLabels:
    #                        mergedLabels[frame]=[]
     #                   if not nextFrame in mergedLabels:
      #                      mergedLabels[nextFrame]=[]
       #                 for label in nextLabels:
        #                    mergedLabels[nextFrame].append(label)
         #               for label in lastLabels:
          #                  mergedLabels[frame].append(label)
                        #lastMoveSplit =False
#                else:
#                    print "two cells PBL at t="+str(frame)
#                    raise
#
#            elif int(l)==0:
#                print "problem at frame "+str(frame)
#                raise
#            elif int(nextL)==0:
#                print "last pbl at frame "+str(frame), lastLabels, nextLabels
#                raise
#
            lastFrame = frame
            if not lastMoveSplit[frame]:
                 lastLabels = nextLabels
            if int(lastLabels[0])==-2:
                break

    for f in solutions:
        if "move" not in solutions[f]:
            continue
        listeLabelsTargetMove = solutions[f]["move"][1]
        listeLabelsSourceMove = solutions[f]["move"][0]
        nextFrame = int(f+1)

        for label1 in listeLabelsTargetMove:
            label1=label1[0]
            count = 0
            for label2 in listeLabelsTargetMove:
                label2=label2[0]
                if int(label1)==int(label2):
                    count+=1

            if count>1:
                #print "label1 "+str(label1), count, f
                #print "MERGE ", label1, f
                lastLabels=[]
                nextLabels=[label1]

                while [label1] in listeLabelsTargetMove:
                    index = listeLabelsTargetMove.index([label1])
                    #print index, label1, listeLabelsSourceMove[index]
                    lastLabels.append(listeLabelsSourceMove[index][0])
                    
                    del listeLabelsTargetMove[index]
                    del listeLabelsSourceMove[index]
                    

                if not "merge" in solutions[f]:
                    solutions[f]["merge"]=[[], []]

                solutions[f]["merge"][0].append(lastLabels)
                solutions[f]["merge"][1].append(nextLabels)

                if not f in going:
                    going[f]=[]
                if not nextFrame in coming:
                    coming[nextFrame]=[]
                for label in nextLabels:
                    coming[nextFrame].append(label)
                for label in lastLabels:
                    going[f].append(label)

        for label1 in listeLabelsSourceMove:
            label1=label1[0]
            count = 0
            for label2 in listeLabelsSourceMove:
                label2=label2[0]
                if int(label1)==int(label2):
                    count+=1

            if count>1:
                #print "label1 "+str(label1), count, f
                #print "SPLIT ", label1, f
                lastLabels=[label1]
                nextLabels=[]

                while [label1] in listeLabelsSourceMove:
                    index = listeLabelsSourceMove.index([label1])
                    #print index, label1, listeLabelsSourceMove[index]
                    nextLabels.append(listeLabelsTargetMove[index][0])
                    
                    del listeLabelsTargetMove[index]
                    del listeLabelsSourceMove[index]
                    

                if not "split" in solutions[f]:
                    solutions[f]["split"]=[[], []]

                solutions[f]["split"][0].append(lastLabels)
                solutions[f]["split"][1].append(nextLabels)

                if not f in going:
                    going[f]=[]
                if not nextFrame in coming:
                    coming[nextFrame]=[]
                for label in nextLabels:
                    coming[nextFrame].append(label)
                for label in lastLabels:
                    going[f].append(label)
                                           

#appear candidates 
    for frame in appearCandidates.keys():
        appearlist = appearCandidates[frame]
        for label in appearlist:
            if frame not in coming.keys() or (frame in coming.keys() and label not in coming[frame]):
                print "APPEAR "+str(label)+" on frame "+str(frame)
                if not "appear" in solutions[frame-1]:
                    solutions[frame-1]["appear"]=[[], []]

                solutions[frame-1]["appear"][0].append([])
                solutions[frame-1]["appear"][1].append(label)

#disappear candidates
    for frame in disappearCandidates.keys():
        disappearlist = disappearCandidates[frame]
        for label in disappearlist:
            if frame not in going.keys() or (frame in going.keys() and label not in going[frame]):
                print "DISAPPEAR "+str(label)+" on frame "+str(frame)

                if not "disappear" in solutions[frame]:
                    solutions[frame]["disappear"]=[[], []]

                solutions[frame]["disappear"][0].append(label)
                solutions[frame]["disappear"][1].append([])

    count={}
    for e in EVENTS:
        count[e]=0

    for f in solutions:
        fileS.write("\n --------------------------FRAME "+str(f)+"------------------------------------")
        for e in solutions[f]:
            fileS.write("\n EVENT "+str(e)+"*******\n SOURCES :\n")
            for label in solutions[f][e][0]:
                fileS.write("\n label"+str(label))
                count[e]+=1
            fileS.write("\n TARGETS :\n")
            for label in solutions[f][e][1]:
                fileS.write("\n label"+str(label))
            if e <> "move":
                print e+str(solutions[f][e][0])+" on frame "+str(f)+" to "+str(solutions[f][e][1])
    print count
    fileS.close()
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


def HacktrackReverse(plaque, puits, dossierSauvegarde, boolean):
    if boolean:
        dossier = "/bioinfo/users/aschoena/projects/groundtruth/results/pheno/"+plaque+"/analyzed/"+puits+"/statistics"
        sauvegarde = "/pheno data/"
    else:
        dossier = "/bioinfo/users/aschoena/projects/groundtruth/results/controls/"+plaque+"/analyzed/"+puits+"/statistics"
        sauvegarde = "/controls data/"

    print "Pheno?"+str(boolean), "Numero de plaque :"+plaque+" numero de puits : "+ puits

#    nomDot = dossier + ("/tracking_graph___P%s.dot" % puits)    
    nomTxt =  dossier + ("/tracking_graph___P%s_features.txt" % puits)

    nomFichier = "PL"+plaque+"___P"+puits+"___T00000.xml"
    nomFichier = dossierSauvegarde+"/"+nomFichier
    print os.getcwd()

    print nomTxt, nomFichier

    ensembleTraj = lireTrajectoires(nomFichier, nomTxt)
    bim = ("savedAnnotations_L%s_P%s.txt" % (plaque, puits))
    fileToSave = sauvegarde + bim
    ecrireTraining(ensembleTraj, fileToSave)

  #      ensemTraj = lireDot(nomDot, X, Y)
   #     print ensemTraj.numMitoses
    #    sortiesCarre(nomFichier, ensemTraj)
   # except IOError as e :
    #    print "probleme fichier"+e.message


    return
