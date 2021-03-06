import os, sys, pdb, getpass, csv
import numpy as np
import cPickle as pickle
from collections import defaultdict
from optparse import OptionParser
from scipy.spatial.distance import squareform, pdist, cdist

from util.settings import Settings
from tracking.trajPack.thrivision import thrivisionExtraction
from vigra import impex as vi
from util.listFileManagement import correct_from_Nan, strToTuple, EnsemblEntrezTrad
from tracking.trajPack import featuresNumeriques, featuresSaved
from tracking.histograms import transportation
from scipy.stats.stats import scoreatpercentile
from sklearn.cluster.spectral import SpectralClustering

if getpass.getuser()=='lalil0u':
    import matplotlib.pyplot as p
    from util.plots import couleurs
    import networkx as nx

# 652 Loading error for  LT0159_17--ex2006_01_20--sp2006_01_10--tt17--c5 00134_01
# 654 Loading error for  LT0159_50--ex2006_02_01--sp2006_01_10--tt17--c5 00134_01
# 1150 Loading error for  LT0062_07--ex2006_03_08--sp2005_06_02--tt17--c3 00300_01
# 1151 Loading error for  LT0062_46--ex2005_07_08--sp2005_06_02--tt18--c4 00300_01
# 2675 Loading error for  LT0072_25--ex2005_07_15--sp2005_06_05--tt18--c2 00007_01
# 2676 Loading error for  LT0072_35--ex2007_10_24--sp2005_06_20--tt17--c5 00007_01
# 2677 Loading error for  LT0072_47--ex2005_09_30--sp2005_06_20--tt17--c5 00007_01
# 2678 Loading error for  LT0159_17--ex2006_01_20--sp2006_01_10--tt17--c5 00014_01
# 2679 Loading error for  LT0159_50--ex2006_02_01--sp2006_01_10--tt17--c5 00014_01
# 2698 Loading error for  LT0159_17--ex2006_01_20--sp2006_01_10--tt17--c5 00109_01
# 2699 Loading error for  LT0159_50--ex2006_02_01--sp2006_01_10--tt17--c5 00109_01
# 2865 Loading error for  LT0084_47--ex2005_08_03--sp2005_07_07--tt17--c5 00120_01

#to do jobs launch thrivision.scriptCommand(exp_list, baseName='pheno_seq', command="phenotypes/phenotype_seq.py")

def forMatthieu(file_='../resultData/features_on_films/labelsKM_whole_k8.pkl', out_file='../resultData/features_on_films/traj_cluster{}.csv'):
    order=[7,0,3,5,4,2,6,1]
    trad=EnsemblEntrezTrad('../data/mapping_2014/mitocheck_siRNAs_target_genes_Ens75.txt')
    trad['ctrl']='ctrl'
    f=open(file_, 'r')
    labels=pickle.load(f)
    f.close()
    #ATTENTION A L'ORDRE DES CLUSTERS POUR ETRE CORRECT PAR RAPPORT A LA HEATMAP
    percentages=labels[1][:,order]
    movie_perc=percentages[:2929]
    
    f=open('../resultData/features_on_films/labelsKM_whole_k8_NEWMODEL.pkl')
    new_labels=pickle.load(f)
    f.close()
    siRNAs=np.array(new_labels[4])
    genes=np.array(new_labels[5])

    d_percentages=getMedians(movie_perc, siRNAs[:2929], genes[:2929])
    d_genes=np.hstack((np.array(d_percentages[2]), genes[2929:]))
    d_siRNAs=np.hstack((np.array(d_percentages[1]), siRNAs[2929:]))
    
    d_percentages2=np.vstack((d_percentages[0], percentages[2929:]))
    
    fig,axes=p.subplots(4,2,sharex=True, figsize=(24,24))
    for k in range(8):
        f=open(out_file.format(k), 'w')
        writer=csv.writer(f)
        currGenes = d_genes[np.argsort(-d_percentages2[:,k])]
        currValues=d_percentages2[:,k][np.argsort(-d_percentages2[:,k])]
        currColors=[]
        for i in range(currGenes.shape[0]):
            writer.writerow([currGenes[i], currValues[i], trad[currGenes[i]]])
            if currGenes[i]=='ctrl':
                axes.flatten()[k].scatter(i,currValues[i], color='green', s=8)
            else:
                axes.flatten()[k].scatter(i,currValues[i], color='red', s=5, marker='+')
        f.close()
        
        axes.flatten()[k].set_title('Cluster {}'.format(k))
    fig.savefig('../resultData/features_on_films/traj_clusters.png')
        
        
    return

def forMatthieu2(file_features='../resultData/features_on_films/all_distances_whole_dataonly.pkl', file_labels='../resultData/features_on_films/labelsKM_whole_k8.pkl',
                 file_coordinates='../resultData/features_on_films/coordinates_1000first.pkl',
                 out_feature_file='../resultData/features_on_films/traj_cluster{}_trajectory_features.csv',
                 out_coordinate_file='../resultData/features_on_films/traj_cluster{}_trajectory_coordinates.csv'):
    
    small_nr=None; small_coordinates=None
    
    f=open(file_features)
    data=pickle.load(f); f.close()
    data=data[0][:356905]
    r=np.hstack((data[:,:len(featuresNumeriques)], data[:,featuresSaved.index('mean persistence'), np.newaxis], data[:, featuresSaved.index('mean straight'), np.newaxis]))
    
    f=open(file_labels)
    labels=pickle.load(f); f.close()
    labels=labels[0][:356905]
    
    f=open(file_coordinates)
    coordinates=np.array(pickle.load(f));f.close()
    i=0
    for k in [7,0,3,5,4,2,6,1]:#range(begin_, num_clusters):#ORDRE UTILISE POUR LE PAPIER ISBI 
        where_=np.where(np.array(labels)==k)[0]
        np.random.shuffle(where_)
        
        f=open(out_feature_file.format(i), 'w')
        writer=csv.writer(f)
        writer.writerows(r[where_[:1000]])
        f.close()
        
        f=open(out_coordinate_file.format(i), 'w')
        writer=csv.writer(f)
        for el in coordinates[where_[:1000]]:
            writer.writerow(zip(el[:,0], el[:,1]))
        f.close()
        
        i+=1
    
    


def computeIntersectionSC_pheno(medians, medGENES, medSI, delta_l, k_l, phenotypic_labels):
    result=np.empty(shape=(len(delta_l), len(k_l)), dtype=float)
    
    for j,delta in enumerate(delta_l):
        affinity=np.exp(-delta*medians**2)
        
        for i,k in enumerate(k_l):
            print '----', delta, k  
            model=SpectralClustering(affinity='precomputed', n_clusters=k)
            model.fit(affinity)
            
            result[j,i]=intersection(model.labels_, phenotypic_labels, medSI)
            
    return result
            
            
def intersection(model_labels, phenotypic_labels, medSI):
    count=np.zeros(shape=(len(set(model_labels)), 8))
    
    for i,siRNA in enumerate(medSI):
        spec=model_labels[i]
        
        for el in phenotypic_labels[siRNA]:
            count[spec, el]+=1
    print count
    return np.sum(np.max(count,0))/float(np.sum(count))
            

def getMedians(distances, siRNAs, genes):
    siRNA=np.array(siRNAs)
    distinct_siRNAs=list(set(siRNAs)); distinct_genes=[]
    if distances.shape[0]==distances.shape[1]:
        result=np.zeros(shape=(len(distinct_siRNAs), len(distinct_siRNAs)))
    else:
        result=np.zeros(shape=(len(distinct_siRNAs), distances.shape[1]))
    
    for i,siRNA in enumerate(distinct_siRNAs):
        where_=np.where(siRNAs==siRNA)
        distinct_genes.append(genes[where_[0][0]])
        
        if distances.shape[0]==distances.shape[1]:
            for j in range(i+1, len(distinct_siRNAs)):
                other_=np.where(siRNAs==distinct_siRNAs[j])
                
                result[i][j] = np.median(distances[where_][:,other_])
                result[j][i]=result[i][j]
        else:
            result[i]=np.median(distances[where_], 0)
            
    return result, distinct_siRNAs, distinct_genes 

def graphVisualClustering(genesTarget, mds_dist, genes, G):
    result=[[] for k in range(len(genesTarget))]
    arr=np.array([gene in genesTarget for gene in genes])
    degrees=np.array([float(G.degree(v)) for v in G])
    high_degrees=np.where(degrees>=scoreatpercentile(degrees, 90))[0]
    
    for el in high_degrees:
        gene=genes[el]
        distances=cdist(mds_dist[np.newaxis, el], mds_dist[np.where(arr)])
        print el, gene, np.argmax(distances)
        result[np.argmax(distances)].append(gene)
        
    return result

def graphWorking(trajdist, mds_transformed, genes=None, percentile=10, only_high_degree=True, clustering_labels=None):
    couleurs=['green', 'red', 'blue', 'orange', 'yellow', "white", 'purple', 'pink', 'grey']
    newtrajdist=np.array(trajdist)
    newtrajdist[np.where(newtrajdist>scoreatpercentile(newtrajdist.flatten(), percentile))]=0
    
    G=nx.from_numpy_matrix(newtrajdist); labels={}
    #maintenant les edges ont bien les poids que l'on voudrait mais on ne peut pas faire de plots pcq il faut donner les positions des noeuds. Utiliser les resultats MDS pr ca
    for el in G.nodes():
        G.node[el]['pos']=mds_transformed[el][:2]
        if genes is not None:
            labels[el]=genes[el]
    
    pos=nx.get_node_attributes(G,'pos')

    p.figure(figsize=(8,8))
    
    if not only_high_degree:
        nx.draw_networkx_edges(G,pos,alpha=0.4)
        node_color=[float(G.degree(v)) for v in G] if clustering_labels is None else [couleurs[k] for k in clustering_labels]
        nx.draw_networkx_nodes(G,pos,
                           node_size=60,
                           node_color=node_color,
                           cmap=p.cm.Reds_r)
    else:
        degrees=np.array([float(G.degree(v)) for v in G])
        wh_=np.where(degrees>=scoreatpercentile(degrees, 90))[0]
        
        pos={x:pos[x] for x in pos if x in wh_}
        labels={x:labels[x] for x in pos}
        
        for k in range(len(genes)):
            if k not in pos:
                G.remove_node(k)
        node_color=[float(G.degree(v)) for v in G]
        nx.draw_networkx_edges(G,pos,alpha=0.4)
        nx.draw_networkx_nodes(G,pos,
                           node_size=60,
                           node_color=node_color,
                           cmap=p.cm.Reds_r)
        
    
    nx.draw_networkx_labels(G, pos, labels, font_size=10)
    
    p.axis('off')
    p.show()
        
    return G

    
def collectingDistance(filename="pheno_distance", folder='/cbio/donnees/aschoenauer/projects/drug_screen/results/distances', len_=7786):
    missed=[]
    result=[np.zeros(shape=(len_, len_)) for k in range(5)]
    for i in range(len_):
        el='{}_{}.pkl'.format(filename, i)
        try:
            f=open(os.path.join(folder, el))
            d=pickle.load(f); f.close()
        except:
            print "Unopenable ", el
            missed.append(i)
        else:
            for k in range(len(d)):
                result[k][i, i+1:]=d[k]
                result[k][i+1:, i]= result[k][i,i+1:].T
            
    return result, missed


def computingDistance(percentages, who, distance='transport', M=None):
    '''
    To compute distances without parallelizing
    '''
    if len(set(who))!=len(who):
        unred_perc=[]; unred_who=[]
        for i,el in enumerate(who):
            if el not in unred_who:
                unred_perc.append(percentages[i])
                unred_who.append(el)
    
    if distance=='transport':
        result=np.zeros(shape=(percentages.shape[0], percentages.shape[0]))
        for i in range(percentages.shape[0]-1):
            print i,
            result[i, i+1:]=transportation.multSinkhorn(M, lamb=10, r=percentages[i], C=percentages[i+1:].T)
            result[i+1:, i]= result[i,i+1:].T
        return result
    try:
        result=squareform(pdist(percentages, metric=distance))
    except:
        print "Bad distance value"
        return None
    else:
        return result
    


def trajectory_phenotype_comparison(inputFolder, maskFile, inputData):
#     Ordre des phenotypes:
#     Grape
#     increased proliferation
#     Cell Death
#     Binuclear
#     Dynamic changes
#     Large
#     Polylobed
#     Mitotic delay/arrest

#     #i. How were the labels pre-computed?

    #Loading mask
    f=open(os.path.join(inputFolder, maskFile))
    _, mask=pickle.load(f); f.close()
    
    f=open(os.path.join('../data/mitocheck_exp_hitlist_perPheno.pkl'))
    hit_experiments=pickle.load(f); f.close()
    phenos=list(hit_experiments.keys())
    colors = dict(zip(hit_experiments.keys(), couleurs))
    
    new_hit_experiments=[]
    for el in hit_experiments:
        for exp in hit_experiments[el]:
            new_hit_experiments.append((exp, el))
            
    new_hit_experiments=np.array(new_hit_experiments)
    
    f,axes=p.subplots(4,2,sharex=True, sharey=True); k=0
    for i,el in enumerate(new_hit_experiments):
        if i not in mask:
            exp, pheno=el
            axes.flatten()[phenos.index(pheno)].scatter(inputData[k,0],inputData[k,1], color=colors[pheno])
            k+=1
        
    p.show()
    

class pheno_seq_extractor(thrivisionExtraction):
    def __init__(self, setting_file, plate, well):
        super(pheno_seq_extractor, self).__init__(setting_file, plate, well)
        if plate is not None:
            self.file_=os.path.join(self.settings.raw_result_dir, self.plate, 'hdf5', "{}_{{:>02}}.ch5".format(self.well))
            self.path_objects="/sample/0/plate/{}/experiment/{}/position/{{}}/object/primary__test".format(self.plate, self.well)
        return
    
    def DS_usable(self):
        '''
        Checking for over-exposed experiments or with low cell count
        '''
        #i. Opening file to see qc
        f=open(os.path.join(self.settings.result_dir, 'processedDictResult_P{}.pkl'.format(self.plate)))
        d=pickle.load(f); f.close()
        
        if int(self.well) not in d['FAILED QC']:
            return True
        
        if int(self.well) in d['FAILED QC'] and d[int(self.well)]['cell_count'][0]>50:
            print "Intensity QC failed"
            return False
        
        c=0
        for pos in [1,2]:
            tab=vi.readHDF5(self.file_.format(pos), self.path_objects.format(pos))
            c+=np.where(tab['time_idx']==0)[0].shape[0]
            
        if c<50:
            return False
        return True
        
    def classificationConcatenation(self):
        path_classif="/sample/0/plate/{}/experiment/{}/position/{{}}/feature/primary__test/object_classification/prediction".format(self.plate, self.well)
        
        result=None
        
        for pos in [1,2]:
            classification = vi.readHDF5(self.file_.format(pos), path_classif.format(pos))
            result = np.bincount(classification['label_idx'], minlength=18) if result == None\
                    else result + np.bincount(classification['label_idx'], minlength=18)
                    
        #putting UndefinedCondensed with Apoptosis
        result[11]+=result[16]
        result[16]=result[17]
        
        return result[:-1]
        

    def loadResults_Mitocheck(self,exp_list):
        '''
        Here we're loading results on a per experiment basis. This will be interesting to look at distances between experiments
        based on phenotypes, vs distances based on trajectory types.
        '''
        if len(exp_list[0])!=2:
            exp_list=strToTuple(exp_list, os.listdir(self.settings.outputFolder))
        result = None; i=0; missed=[]
        for pl,w in exp_list:
            print i,
            
            try:
                f=open(os.path.join(self.settings.outputFolder,pl, self.settings.outputFile.format(pl[:10], w)), 'r')
                pheno_seq_list, mask = pickle.load(f)
                f.close()
            except:
                print "Loading error for ", pl, w
                missed.append(i)
                continue
            else:
                pheno_seq_list = np.sum( np.array([np.bincount(pheno_seq_list[j], minlength=17) for j in range(len(pheno_seq_list)) if j not in mask]), 0)[:-2]
            #15 and 16 are respectively out of focus and artefact objects. We don't want them
                pheno_seq_list=pheno_seq_list/float(np.sum(pheno_seq_list))
                result = np.vstack((result, pheno_seq_list)) if result is not None else pheno_seq_list
            finally:
                i+=1
                
        print "Saving"
        
        f=open(os.path.join(self.settings.outputFolder,self.settings.outputFile.format("ALL", "hit_exp")), 'w')
        pickle.dump((result, missed),f); f.close()
        return
    
    def loadResults_DS(self,exp_list):
        '''
        Here we're loading results on a per experiment basis. This will be interesting to look at distances between experiments
        based on phenotypes, vs distances based on trajectory types.
        '''

        result = None; i=0; who=[]
        for pl,w in exp_list:
            print i,
            
            try:
                f=open(os.path.join(self.settings.outputFolder,pl, self.settings.outputFile.format(pl[:10], w)), 'r')
                pheno_seq_list= pickle.load(f)
                f.close()
            except:
                print "Loading error for ", pl, w
                continue
            else:
            #15 and 16 are respectively out of focus and artefact objects. We don't want them
                pheno_seq_list=pheno_seq_list[:15]/float(np.sum(pheno_seq_list[:15]))
                result = np.vstack((result, pheno_seq_list)) if result is not None else pheno_seq_list
                who.append('{}--{}'.format(pl[:10], w))
            finally:
                i+=1
                
        print "Saving"
        
        f=open(os.path.join(self.settings.outputFolder,self.settings.outputFile.format("ALL", "hit_exp")), 'w')
        pickle.dump((result, who),f); f.close()
        return
    
    def pheno_seq(self, tracklets,track_filter= (lambda x: x.fusion !=True and len(x.lstPoints)>11)):
        file_=os.path.join(self.settings.hdf5Folder, self.plate, 'hdf5', "{}.hdf5".format(self.well))
        path_objects="/sample/0/plate/{}/experiment/{}/position/1/object/primary__primary".format(self.plate, self.well.split('_')[0])
        path_classif="/sample/0/plate/{}/experiment/{}/position/1/feature/primary__primary/object_classification/prediction".format(self.plate, self.well.split('_')[0])
            
        objects = vi.readHDF5(file_, path_objects)
        classif = vi.readHDF5(file_, path_classif)
        result=[]
        
        for tracklet in filter(track_filter, tracklets):
            t=tracklet.lstPoints.keys(); t.sort(); 
            currR=[]
            for fr, cell_id in t:
                try:
                    where_=np.where((objects['time_idx']==fr)&(objects["obj_label_id"]==cell_id))[0]
                    currR.append(classif[where_])
                except IndexError:
                    currR.append(-1)
            currR = np.array(currR)['label_idx'][:,0]
            result.append(currR)
            
        return result
    
    def getMask(self):
        file_=os.path.join(self.settings.outputFolder, self.plate, self.settings.trajFeaturesFilename.format(self.well))
    
        f=open(file_, 'r')
        arr, _,__= pickle.load(f)
        f.close()
        
        _, toDel = correct_from_Nan(arr, perMovie=False)
        
        return toDel
    
    
    def __call__(self):
            #before anything checking that it passed the qc
        try:
            assert self._usable(check_size=False)
        except AssertionError:
            print "QC failed"
            return
        
        #i.load tracking info
        tracklets, _ = self.load()
        
        #ii. find their bounding boxes
        pheno_sequences=self.pheno_seq(tracklets)
        
        #iii. get the mask for those that are not considered in the feature array
        mask = self.getMask()

        if not os.path.isdir(self.settings.outputFolder):
            os.mkdir(self.settings.outputFolder)
        if not os.path.isdir(os.path.join(self.settings.outputFolder, self.plate)):
            os.mkdir(os.path.join(self.settings.outputFolder, self.plate))
        #iv. crop the boxes in the images
        self.save((pheno_sequences, mask))
        
        return
    
    def DS_call(self):
        try:
            assert self.DS_usable()
        except AssertionError:
            print "QC failed"
            return
        
        result = self.classificationConcatenation()
        
        if not os.path.isdir(os.path.join(self.settings.outputFolder, self.plate)):
            os.mkdir(os.path.join(self.settings.outputFolder, self.plate))
        
        self.save(result)
        
        return
    
    
if __name__ == '__main__':
    verbose=0
    description =\
'''
%prog - Computing phenotype sequences given tracklets
Input:
- plate, well: experiment of interest. Well under the form 00315_01
- settings file

'''
    #Surreal: apparently I need to do this because I changed the architecture of my code between the computation of the trajectories and now that I need to reopen the files
    from tracking import PyPack
    sys.modules['PyPack.fHacktrack2']=PyPack.fHacktrack2
    parser = OptionParser(usage="usage: %prog [options]",
                         description=description)
    
    parser.add_option("-f", "--settings_file", dest="settings_file", default='analyzer/settings/settings_drug_screen_thalassa.py',
                      help="Settings_file")

    parser.add_option("-p", "--plate", dest="plate",
                      help="The plate which you are interested in")
    
    parser.add_option("-w", "--well", dest="well",
                      help="The well which you are interested in")


    
    (options, args) = parser.parse_args()
    
    p=pheno_seq_extractor(options.settings_file, options.plate, options.well)
    p.DS_call()
    print "Done"
        
        
