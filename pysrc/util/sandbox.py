import os, pdb, shutil, sys
from collections import defaultdict
from operator import itemgetter
import cPickle as pickle
import numpy as np
from PIL import Image
from scipy.stats import ks_2samp, scoreatpercentile
from numpy import nanmean, nanmedian
#import vigra.impex as vi
import matplotlib.pyplot as p

from tracking.trajPack import featuresSaved, histLogTrsf,\
    histLogTrsf_meanHistFeat
#from tracking.plots import plotTraj3d
from tracking.histograms import *
from util.listFileManagement import expSi
from util import jobSize, scriptFolder, path_command, pbsOutDir, pbsArrayEnvVar, pbsErrDir

def findingMeans(exp_list, feature1, feature2, folder= '/share/data20T/mitocheck/tracking_results/', filename="hist_tabFeatures_{}.pkl", plot=True, result=None):
    '''
    For interesting plots: getting means and medians for a couple of features, then getting wells for extreme values
    '''
    if result is None:
        result=np.zeros(shape=len(exp_list, 4))
        for k, exp in enumerate(exp_list):
            pl,w=exp; print k
        try:
            f=open(os.path.join(folder, pl, filename.format(w)))
            arr,_,_=pickle.load(f)
            f.close()
        except OSError:
            print "no ", pl, w
        else:                 
            result[k]=[nanmean(arr[:,featuresSaved.index(feature1)]), nanmedian(arr[:,featuresSaved.index(feature1)]),\
                        nanmean(arr[:,featuresSaved.index(feature2)]), nanmedian(arr[:,featuresSaved.index(feature2)])]
            
        f=open('result__{}{}.pkl'.format(feature1, feature2), 'w')
        pickle.dump(result, f); f.close()
    
    if plot:
        f=p.figure()
        ax=f.add_subplot(121)
        ax.scatter(result[:,0], result[:,2]); ax.set_title('Means'); ax.set_xlabel(feature1); ax.set_ylabel(feature2)
        ax.axhline(scoreatpercentile(result[:,2],90)); ax.axhline(scoreatpercentile(result[:,2],10))
        ax.axvline(scoreatpercentile(result[:,0],90)); ax.axvline(scoreatpercentile(result[:,0],10))
        
        ax=f.add_subplot(122)
        ax.scatter(result[:,1], result[:,3]); ax.set_title('Medians'); ax.set_xlabel(feature1); ax.set_ylabel(feature2)
        ax.axhline(scoreatpercentile(result[:,3],90)); ax.axhline(scoreatpercentile(result[:,3],10))
        ax.axvline(scoreatpercentile(result[:,1],90)); ax.axvline(scoreatpercentile(result[:,1],10))
        p.show()
    mean_result=[0,0,0,0]
    mean_result[1] = exp_list[np.where((result[:,0]>scoreatpercentile(result[:,0],90)) & ((result[:,2])>scoreatpercentile(result[:,2],90)))]
    mean_result[2] = exp_list[np.where((result[:,0]>scoreatpercentile(result[:,0],90)) & ((result[:,2])<scoreatpercentile(result[:,2],10)))]
    mean_result[0] = exp_list[np.where((result[:,0]<scoreatpercentile(result[:,0],10)) & ((result[:,2])>scoreatpercentile(result[:,2],90)))]
    mean_result[3] = exp_list[np.where((result[:,0]<scoreatpercentile(result[:,0],10)) & ((result[:,2])<scoreatpercentile(result[:,2],10)))]
    
    return mean_result
        
def generic_single_script(name, text,folder='../scripts', *args):
    '''
    This enables one to generate scripts with or without custom arguments. *args can be None
    
    Warning!! One should be careful: no blanks before the first line, and one line between PBS/OUT PBS/ERR directory declaration
    and the rest of the instructions
    '''
    print text%args
    
    main_content = """#!/bin/sh
%s
#$ -o %s
#$ -e %s

""" % (path_command,
           pbsOutDir,  
           pbsErrDir)
    main_content+= """cd %s
""" %progFolder
    cmd = text%args
    
    script_name = os.path.join(scriptFolder, name+'.sh')
    script_file = file(script_name, "w")
    script_file.write(main_content + cmd)
    script_file.close()
    
            # make the script executable (without this, the cluster node cannot call it)
    os.system('chmod a+x %s' % script_name)
    
    sub_cmd = 'qsub ~/workspace2/Xb_screen/scripts/%s' % (name+'.sh')
    print sub_cmd
    return

    

def accuracy_precision(normals, truth, predicted):
    true_pos=len([el for el in predicted if el in truth])
    
    false_pos=len(predicted) - true_pos
    
    false_neg=len([el for el in truth if el not in predicted])
    true_neg= normals - false_neg
    
    accuracy = float(true_pos+true_neg)/(len(predicted)+normals)
    precision=float(true_pos)/(true_pos+false_pos)
    print "Accuracy ", accuracy
    print "Precision ", precision

def countingFluoAlamar(rawFolder="/media/lalil0u/FREECOM HDD/Alice/300714_wells", 
                        filename= "P300714--W%05i--P0001_t%05i_c00002.tif"):
    nb_wells = 47; blanc=None
    arr = np.zeros(shape = (95, nb_wells))
    for tour in range(1,96):
        for well in range(1,nb_wells+1):
            file_= os.path.join("W%05i"%well, filename %(well, tour))
            
            print file_, tour, well
            try:
                image = vi.readImage(os.path.join(rawFolder, file_))
            except:
                print "Pas d'images ", os.path.join(rawFolder, file_)
                continue
            if well==1:
                blanc = np.mean(image)
                print "Blanc, tour ", tour, blanc
                arr[tour-1, well-1]=blanc
            else:
                fluo = np.mean(image)
                arr[tour-1, well-1] = fluo - blanc #on soustrait le blanc = milieu + Alamar sans cellules
            
    f=open('%s/fluoValues.pkl'%rawFolder, 'w')
    pickle.dump(arr, f); f.close()
    return arr


def dependentJobs(debut, filename):
    f=open(filename, 'r')
    lines = f.readlines()
    f.close()
    for line in lines:
        print line.split(' ')[0], line.split(' ')[1], line.split(" ")[2], '-hold_jid {}'.format(debut), line.split(' ')[-1]
        debut+=1
        
    return

def homeMadeGraphLaplacian(W, normed = True):
    n_nodes = W.shape[0]
    lap = -np.asarray(W) # minus sign leads to a copy

    # set diagonal to zero WHY ???
#    lap.flat[::n_nodes + 1] = 0
    w = -lap.sum(axis=0) #matrice D
    if normed:#I choose to compute Lrw = inv(D)*(D-W)
        #w = np.sqrt(w)
        w_zeros = (w == 0)
        w[w_zeros] = 1
        #lap /= w
        #We multiply by inv(D) on the left
        lap /= w[:, np.newaxis]
        lap.flat[::n_nodes + 1] = (1 - w_zeros).astype(lap.dtype)+lap.flat[::n_nodes + 1]
    else:
        print "pbl"
        sys.exit()
    return lap

def pointsCommuns(filename, div_name = 'transportation_exact', iteration = 5, ddimensional = False,
                 folder = "/media/lalil0u/New/workspace2/Xb_screen/resultData/sinkhornKMeans/results_PCA_MAR1"):
    
    datasize=29600
    weights = WEIGHTS if not ddimensional else ddWEIGHTS
    range_=range(2,15)
    filename=filename+'_a1_k{}_d{}_w{}_bt{}_bs{}_ct{}_{}.pkl' if not ddimensional else 'dd_'+filename+'_a1_k{}_d{}_w{}_bt{}_bs{}_ct{}_{}.pkl'
    pairs = [(0,1), (2,3), (4,0)]
    result = {}
    
    for bt in ['minmax']:
        print bt
        result[bt]={}
        cost_choices=["num"]
        for cost_type in cost_choices:
            print cost_type
            result[bt][cost_type]={}
            for bs in [10]:
                result[bt][cost_type][bs]={k:np.zeros(shape=(len(range_)), dtype=list) for k in range(len(WEIGHTS))}
                for k in range(len(weights)):
                    print k
                    result[bt][cost_type][bs][k].fill([0])
                    for pair in pairs:
                        seedname = 'seeds' if not ddimensional else 'dd_seeds'
                        seeds = '{}_{}_{}_s{}_{}_w{}_{}_{}.pkl'.format(seedname, cost_type[:3],bt, bs,div_name[:5],k,datasize, pair[0])
                        f=open(os.path.join(folder, seeds))
                        set1, _ = pickle.load(f)
                        f.close()
                        seeds = '{}_{}_{}_s{}_{}_w{}_{}_{}.pkl'.format(seedname, cost_type[:3],bt, bs,div_name[:5],k,datasize, pair[1])
                        f=open(os.path.join(folder, seeds))
                        set2, _ = pickle.load(f)
                        f.close()
                        l = np.array([el in set1 for el in set2], dtype=int)
                        print np.sum(l)/29600.0


def modifInertia(filename, div_name = 'transportation_exact', iteration = 5,
                 folder = "/media/lalil0u/New/workspace2/Xb_screen/resultData/sinkhornKMeans/results_PCA_MAR1"):
    
#INUTILE PARCE QUE L'ALLURE DE LA COURBE DEMEURE LA MEME    

    datasize=29600
    range_=range(2,15)
    filename2=filename+'_a1_k{}_d{}_w{}_bt{}_bs{}_ct{}_{}.pkl'
    filename3 = 'm'+filename2
    for iter_ in range(iteration):
        for bt in ['quantile', 'minmax']:
            if bt=='quantile': cost_choices=['num', 'val']
            else: cost_choices=["num"]
            for cost_type in cost_choices:
                for bs in [10]:
                    for k in range(3):
                        try:
                            seeds = 'dd_seeds_{}_{}_s{}_{}_w{}_{}_{}.pkl'.format(cost_type[:3],bt, bs,div_name[:5],k,datasize, iter_)
                            f=open(os.path.join(folder, seeds))
                            set_, total_squared_dist = pickle.load(f)
                            f.close()
                        except IOError:
                            continue
                        else:
                            for l in range_:
                                try:
                                    f=open(os.path.join(folder, filename2.format(l,div_name[:5], k, bt[:3], bs, cost_type, iter_)))
                                    centers,labels,inertia=pickle.load(f); f.close()
                                except IOError:
                                    print 'pas {},{}, iter {}'.format(l,k, iter_)
                                else:
                                    f=open(os.path.join(folder, filename3.format(l,div_name[:5], k, bt[:3], bs, cost_type, iter_)), 'w')
                                    pickle.dump([centers,labels,inertia*total_squared_dist], f); f.close()
    
    return

def distributionLongueurs(folder, exp_list, qc):
    R=[]
    yqualDict=expSi(qc)

    print "loading from experiments list"
    i=0
    for pl, w in exp_list:
        print i,
        i+=1
        result = []
        try:
            f=open(os.path.join(folder, pl, 'hist_tabFeatures_{}.pkl'.format(w)), 'r')
            arr, _, _= pickle.load(f)
            f.close()
        except IOError:
            print "Pas de fichier {}".format(os.path.join(pl, 'hist_tabFeatures_{}.pkl'.format(w)))
        except EOFError:
            print "Probleme EOFError d'ouverture du fichier {}".format(os.path.join(pl, 'hist_tabFeatures_{}.pkl'.format(w)))
            pdb.set_trace()
        else:
    #pdb.set_trace()
            if arr==None:
                print "Array {} is None".format(os.path.join(pl, 'hist_tabFeatures_{}.pkl'.format(w)))
                pdb.set_trace()
            elif pl[:9]+'--'+w[2:5] not in yqualDict:
                print "Quality control not passed", pl[:9], w[2:5]   
    
            else:
                try:
                    #result.extend([len(coord[k][0]) for k in range(len(coord))])
                    result.append(arr.shape[0])
                except (TypeError, EOFError, ValueError, AttributeError):
                    print "Probleme avec le fichier {}".format(os.path.join(pl, 'hist_tabFeatures_{}.pkl'.format(w)))
                    pdb.set_trace()
        try:
            f=open(os.path.join(folder, pl, 'traj_noF_densities_w{}.hdf5.pkl'.format(w)))
            d=pickle.load(f); f.close()
        except:
            print 'Pbl trajectory file'
            pdb.set_trace()
        else:
            result.append(d['movie_length'])
            result.append(len(d["tracklets dictionary"][pl][w].lstTraj))
            result.append(np.mean([len(el.lstPoints) for el in d['tracklets dictionary'][pl][w].lstTraj]))
        R.append(result)
                    
    return R


def findMovieForFeature(nr, ctrlStatus, length, who,features1):
    #ww=['00074_01', '00315_01']
    ctrldata=np.vstack((nr[np.sum(length[:k]):np.sum(length[:k+1])] for k in np.where(np.array(ctrlStatus)==0)[0]))
    result_med=np.zeros(shape=(len(ctrlStatus), len(features1)), dtype=float); result_stat=np.zeros(shape=(len(ctrlStatus), len(features1)), dtype=float)
    
    for featNumber in range(len(features1)):
        print features1[featNumber]
        for i,el in enumerate(ctrlStatus):
            if el==1:
                ltab=nr[np.sum(length[:i]):np.sum(length[:i+1])]
                result_med[i,featNumber]=np.abs(np.median(ctrldata[:,featNumber])-np.median(ltab[:,featNumber]))
                
                result_stat[i,featNumber]=ks_2samp(ctrldata[:,featNumber], ltab[:,featNumber])[0]    
            
    return result_med, result_stat

def makeImagesFromExpDict(dicti, lab, length, genes, who):
    #k=np.bincount(lab).shape[0]
    colors=['red', 'blue', 'green', 'orange']
    for el in dicti:
        for pl,w in dicti[el]:
            f=open(os.path.join(el, pl, 'd_tabFeatures_{}.pkl'.format(w)), 'r')
            tab, coord=pickle.load(f); f.close()
            ou=who.index((pl,w)); print el, genes[ou]
            labCour = lab[np.sum(length[:ou]):np.sum(length[:ou+1])]
            plotTraj3d(coord, pl, w, 100, [colors[k] for k in labCour], os.path.join('{}_traj3D_{}_{}_{}.png'.format(el,genes[ou], pl, w)))
    return

def returnCoordFromExpDict(dicti, lab, length, genes, who):
    #k=np.bincount(lab).shape[0]
    colors=['red', 'blue', 'green', 'orange']; coordTotal=[]; labTotal=[]
    for el in dicti:
        for pl,w in dicti[el]:
            f=open(os.path.join(el, pl, 'd_tabFeatures_{}.pkl'.format(w)), 'r')
            tab, coord=pickle.load(f); f.close()
            ou=who.index((pl,w)); print el, genes[ou]; print length[ou], len(coord)
            if length[ou]!=len(coord):
                print "NO"
                continue
            labC=lab[np.sum(length[:ou]):np.sum(length[:ou+1])]
            labTotal.extend(labC)
            print np.bincount(labC)
            coordTotal.extend(coord)
            #plots.plotTraj3d(coord, pl, w, 100, [colors[k] for k in labCour], os.path.join('{}_traj3D_{}_{}_{}.png'.format(el,genes[ou], pl, w)))
    result=[np.array(coordTotal)[np.where(np.array(labTotal)==k)] for k in range(4)]
    return coordTotal, labTotal

## The similarity function BUT it would be worth trying another one. What about longest common subsequence mais est-ce que ca s'applique vmt ici ?
def dist(x,y, sig):
    return np.exp( -sig*np.sum((x-y)**2) )

def histLogTrsforming(r, plus=1.0, verbose=0):
    result = np.array(r)
    print r.shape
    allLogTrsf = histLogTrsf; allLogTrsf.extend(histLogTrsf_meanHistFeat)
    if verbose>0:
        print "Dealing with {} features".format(len(featuresSaved[:19]))
#    if r.shape[1]>len(histLogTrsf)+1:
#        raise AttributeError
    for k in range(len(featuresSaved[:19])):
        plus_=plus
        if allLogTrsf[k]==1:
            if np.min(r[:,k])<0:
                plus_ -= np.min(r[:,k])
            result[:,k]=np.log(result[:,k]+plus_)
    
    return result

def logTrsforming(r, plus=1.0):
    result = np.array(r)
    print r.shape
    print "we suppose that only the relevant features are left"
    if r.shape[1]>len(logTrsf)+1:
        raise AttributeError
    for k in range(len(sdFeatures1)):
        plus_=plus
        if logTrsf[k]==1:
            plus_ -= np.min(r[:,k])
            result[:,k]=np.log(result[:,k]+plus_)
    
    return result

def subsampling (data, labels=None):
    if labels is not None:
        repartition = np.bincount(labels)/float(len(labels))*10000
    #    print "Cluster repartition", repartition/100
        k = len(repartition)
        pick=[]
        for p in range(k):
    #        print p
            l=np.where(labels==p)[0]
            pick.extend(l[np.random.randint(0, len(l), repartition[p])])
            
        pick.sort()
        return data[pick], labels[pick]
    else:
        #np.random.shuffle(data)
        return data[np.random.randint(0, data.shape[0], 10000)]

def cleaningLength(traj_indices, length):
    allIndices = []
    newl = list(length)
    for k in range(len(length)):
        l=traj_indices[np.where(traj_indices<np.sum(length[:k+1]))[0]]
        ll = l[np.where(l>=np.sum(length[:k]))[0]]
        newl[k]-= len(ll)
    return newl

def concatCtrl(data, ctrl, length, N, ind=False):
    p=np.where(np.array(ctrl)==0)[0][0]
    index=[]
    if p==0:
        datactrl=data[:length[0]]
        index.extend(range(0, length[0]))
    else:
        datactrl=data[np.sum(length[:p]):np.sum(length[:p+1])]
        index.extend(range(np.sum(length[:p]), np.sum(length[:p+1])))
    p+=1; N-=1
    while N>0:
        if ctrl[p]==0:
            N-=1
            datactrl=np.vstack((datactrl, data[np.sum(length[:p]):np.sum(length[:p+1])]))
            index.extend(range(np.sum(length[:p]),np.sum(length[:p+1])))
        p+=1
    if ind:
        return datactrl, index
    else:
        return datactrl

def returnPheno(data, ctrl, length, N, ind=False):
    p=0
    datapheno=[]
    index=[]
    while N>0:
        if ctrl[p]==1:
            N-=1 
            datapheno.append(data[np.sum(length[:p]):np.sum(length[:p+1])])
            index.extend(range(int(np.sum(length[:p])),np.sum(length[:p+1])))
        p+=1
    if ind:
        return datapheno, index
    else:
        return datapheno

    
if __name__ == '__main__':
    pass