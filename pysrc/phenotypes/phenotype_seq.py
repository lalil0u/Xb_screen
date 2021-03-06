import os, sys, pdb, getpass, csv
import numpy as np
from collections import defaultdict
from optparse import OptionParser
from scipy.spatial.distance import squareform, pdist, cdist
import statsmodels.api as sm

from util.settings import Settings
from tracking.trajPack.thrivision import thrivisionExtraction
from vigra import impex as vi
from util.listFileManagement import expSi, is_ctrl_mitocheck, siEntrez, EnsemblEntrezTrad
from tracking.trajPack import featuresNumeriques, featuresSaved

from scipy.stats.stats import scoreatpercentile
from sklearn.cluster.spectral import SpectralClustering
from phenotypes import *

if getpass.getuser()=='lalil0u':
    from tracking.histograms import transportation
    import matplotlib.pyplot as p
    from util.plots import couleurs
    import networkx as nx

# # 652 Loading error for  LT0159_17--ex2006_01_20--sp2006_01_10--tt17--c5 00134_01
# # 654 Loading error for  LT0159_50--ex2006_02_01--sp2006_01_10--tt17--c5 00134_01
# # 1150 Loading error for  LT0062_07--ex2006_03_08--sp2005_06_02--tt17--c3 00300_01
# # 1151 Loading error for  LT0062_46--ex2005_07_08--sp2005_06_02--tt18--c4 00300_01
# # 2675 Loading error for  LT0072_25--ex2005_07_15--sp2005_06_05--tt18--c2 00007_01
# # 2676 Loading error for  LT0072_35--ex2007_10_24--sp2005_06_20--tt17--c5 00007_01
# # 2677 Loading error for  LT0072_47--ex2005_09_30--sp2005_06_20--tt17--c5 00007_01
# # 2678 Loading error for  LT0159_17--ex2006_01_20--sp2006_01_10--tt17--c5 00014_01
# # 2679 Loading error for  LT0159_50--ex2006_02_01--sp2006_01_10--tt17--c5 00014_01
# # 2698 Loading error for  LT0159_17--ex2006_01_20--sp2006_01_10--tt17--c5 00109_01
# # 2699 Loading error for  LT0159_50--ex2006_02_01--sp2006_01_10--tt17--c5 00109_01
# # 2865 Loading error for  LT0084_47--ex2005_08_03--sp2005_07_07--tt17--c5 00120_01
# 
# #to do jobs launch thrivision.scriptCommand(exp_list, baseName='pheno_seq', command="phenotypes/phenotype_seq.py")
# 
# def forMatthieu(file_='../resultData/features_on_films/labelsKM_whole_k8.pkl', out_file='../resultData/features_on_films/traj_cluster{}.csv'):
#     order=[7,0,3,5,4,2,6,1]
#     trad=EnsemblEntrezTrad('../data/mapping_2014/mitocheck_siRNAs_target_genes_Ens75.txt')
#     trad['ctrl']='ctrl'
#     f=open(file_, 'r')
#     labels=pickle.load(f)
#     f.close()
#     #ATTENTION A L'ORDRE DES CLUSTERS POUR ETRE CORRECT PAR RAPPORT A LA HEATMAP
#     percentages=labels[1][:,order]
#     movie_perc=percentages[:2929]
#     
#     f=open('../resultData/features_on_films/labelsKM_whole_k8_NEWMODEL.pkl')
#     new_labels=pickle.load(f)
#     f.close()
#     siRNAs=np.array(new_labels[4])
#     genes=np.array(new_labels[5])
# 
#     d_percentages=getMedians(movie_perc, siRNAs[:2929], genes[:2929])
#     d_genes=np.hstack((np.array(d_percentages[2]), genes[2929:]))
#     d_siRNAs=np.hstack((np.array(d_percentages[1]), siRNAs[2929:]))
#     
#     d_percentages2=np.vstack((d_percentages[0], percentages[2929:]))
#     
#     fig,axes=p.subplots(4,2,sharex=True, figsize=(24,24))
#     for k in range(8):
#         f=open(out_file.format(k), 'w')
#         writer=csv.writer(f)
#         currGenes = d_genes[np.argsort(-d_percentages2[:,k])]
#         currValues=d_percentages2[:,k][np.argsort(-d_percentages2[:,k])]
#         currColors=[]
#         for i in range(currGenes.shape[0]):
#             writer.writerow([currGenes[i], currValues[i], trad[currGenes[i]]])
#             if currGenes[i]=='ctrl':
#                 axes.flatten()[k].scatter(i,currValues[i], color='green', s=8)
#             else:
#                 axes.flatten()[k].scatter(i,currValues[i], color='red', s=5, marker='+')
#         f.close()
#         
#         axes.flatten()[k].set_title('Cluster {}'.format(k))
#     fig.savefig('../resultData/features_on_films/traj_clusters.png')
#         
#         
#     return
# 
# def forMatthieu2(file_features='../resultData/features_on_films/all_distances_whole_dataonly.pkl', file_labels='../resultData/features_on_films/labelsKM_whole_k8.pkl',
#                  file_coordinates='../resultData/features_on_films/coordinates_1000first.pkl',
#                  out_feature_file='../resultData/features_on_films/traj_cluster{}_trajectory_features.csv',
#                  out_coordinate_file='../resultData/features_on_films/traj_cluster{}_trajectory_coordinates.csv'):
#     
#     small_nr=None; small_coordinates=None
#     
#     f=open(file_features)
#     data=pickle.load(f); f.close()
#     data=data[0][:356905]
#     r=np.hstack((data[:,:len(featuresNumeriques)], data[:,featuresSaved.index('mean persistence'), np.newaxis], data[:, featuresSaved.index('mean straight'), np.newaxis]))
#     
#     f=open(file_labels)
#     labels=pickle.load(f); f.close()
#     labels=labels[0][:356905]
#     
#     f=open(file_coordinates)
#     coordinates=np.array(pickle.load(f));f.close()
#     i=0
#     for k in [7,0,3,5,4,2,6,1]:#range(begin_, num_clusters):#ORDRE UTILISE POUR LE PAPIER ISBI 
#         where_=np.where(np.array(labels)==k)[0]
#         np.random.shuffle(where_)
#         
#         f=open(out_feature_file.format(i), 'w')
#         writer=csv.writer(f)
#         writer.writerows(r[where_[:1000]])
#         f.close()
#         
#         f=open(out_coordinate_file.format(i), 'w')
#         writer=csv.writer(f)
#         for el in coordinates[where_[:1000]]:
#             writer.writerow(zip(el[:,0], el[:,1]))
#         f.close()
#         
#         i+=1
#     
#     
# 
# 
# def computeIntersectionSC_pheno(medians, medGENES, medSI, delta_l, k_l, phenotypic_labels):
#     result=np.empty(shape=(len(delta_l), len(k_l)), dtype=float)
#     
#     for j,delta in enumerate(delta_l):
#         affinity=np.exp(-delta*medians**2)
#         
#         for i,k in enumerate(k_l):
#             print '----', delta, k  
#             model=SpectralClustering(affinity='precomputed', n_clusters=k)
#             model.fit(affinity)
#             
#             result[j,i]=intersection(model.labels_, phenotypic_labels, medSI)
#             
#     return result
#             
#             
# def intersection(model_labels, phenotypic_labels, medSI):
#     count=np.zeros(shape=(len(set(model_labels)), 8))
#     
#     for i,siRNA in enumerate(medSI):
#         spec=model_labels[i]
#         
#         for el in phenotypic_labels[siRNA]:
#             count[spec, el]+=1
#     print count
#     return np.sum(np.max(count,0))/float(np.sum(count))
            

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
        '''
        Use well='CTRL' for setting ctrl things for each plate
        For each well we'll save the non-time-aggregated pheno count information independently if they're ctrl or not
        
        We can use the same code for the new h5 files concerning Mitocheck (OLD SEGMENTATION is what we want) because
        it's the same architecture in h5 files
'''
        super(pheno_seq_extractor, self).__init__(setting_file, plate, well)
        if plate is not None:
            self.pos_list=[1,2]
            if plate not in self.settings.plates:
                #then we need to set some things for Mitocheck
                self.settings.raw_result_dir=self.settings.raw_result_dir_Mitocheck
                self.pos_list=[1]
             
            if well!='CTRL':
                self.file_=os.path.join(self.settings.raw_result_dir, self.plate, 'hdf5', "{:>05}_{{:>02}}.ch5".format(self.well))
                self.path_objects="/sample/0/plate/{}/experiment/{:>05}/position/{{}}/object/primary__test".format(self.plate, self.well)
            
            else:
                self.file_=os.path.join(self.settings.raw_result_dir, self.plate, 'hdf5', "{:>05}_{:>02}.ch5")
                self.path_objects="/sample/0/plate/{}/experiment/{{:>05}}/position/{{}}/object/primary__test".format(self.plate)
                
        return
    
    @staticmethod
    def hit_detection_proliferation(res, who, who_mitotic_hits, ctrl_points, whis=1.5):
        q3=scoreatpercentile(ctrl_points, per=75)
        q1=scoreatpercentile(ctrl_points, per=25)
        
        val=q1-whis*(q3-q1)
        
        hits=np.where(res<=val)[0]
        
        return filter(lambda x: x not in who_mitotic_hits, np.array(who)[hits])
    
    @staticmethod
    def hit_detection_pheno_score(res, who, ctrl_points, whis=1.5):
        '''
       Permissive hit detection taking experiments where Interphase phenotypic score is under the bottom whisker,
       which is 1.5*IQR
'''
        q3=scoreatpercentile(ctrl_points[:,CLASSES.index('Interphase')], per=75)
        q1=scoreatpercentile(ctrl_points[:,CLASSES.index('Interphase')], per=25)
        
        val=q1-whis*(q3-q1)
        
        hits=np.where(res[:,CLASSES.index('Interphase')]<=val)[0]
        
        return res[hits], np.array(who)[hits]
        
    
    def DS_usable(self):
        '''
        Checking for over-exposed experiments or with low cell count
        '''
        #i. Opening file to see qc
        f=open(os.path.join(self.settings.result_dir, 'processedDictResult_P{}.pkl'.format(self.plate)))
        d=pickle.load(f); f.close()
        
        if int(self.well) not in d['FAILED QC']:
            return True
        
        if d[int(self.well)]['cell_count'][0]>50:
            print "Intensity QC failed"
        else:
            print "Low cell count"
        return False
            
    def MITO_usable(self, yqualDict=None, dictSiEntrez=None):
        if yqualDict==None:
            dictSiEntrez=siEntrez(self.settings.mitocheck_mapping_file)
            
            if 'LTValidMitosis' in self.plate:
                yqualDict=expSi(self.settings.valid_qc_file, primary_screen=False)
                test0='{}--{:>03}'.format(self.plate.split('--')[0], self.well) not in yqualDict
                test=yqualDict['{}--{:>03}'.format(self.plate.split('--')[0], self.well)] not in dictSiEntrez
            else:
                yqualDict=expSi(self.settings.mitocheck_qc_file)
                test0='{}--{:>03}'.format(self.plate[:9], self.well) not in yqualDict
                test=not is_ctrl_mitocheck((self.plate[:9], '{:>05}'.format(self.well))) and yqualDict['{}--{:>03}'.format(self.plate[:9], self.well)] not in dictSiEntrez
            

        if test0:
    #i. checking if quality control passed
            sys.stderr.write("Quality control not passed {} {} \n".format(self.plate, self.well))
            return False
        if test:
    #ii.checking if siRNA corresponds to a single target in the current state of knowledge
            sys.stderr.write( "SiRNA having no target or multiple target {} {}\n".format(self.plate, self.well))
            return False
        return True
    
    def check_qc(self):
        '''
        checking quality control: different if it's Mitocheck or DS
'''
        if self.plate in self.settings.plates:
            return self.DS_usable()
        return self.MITO_usable()
        
    def classificationPerFrame(self):
        #if already computed I return it
        if self.settings.outputFile.format(self.plate[:10], self.well) in os.listdir(os.path.join(self.settings.outputFolder,self.plate)):
            f=open(os.path.join(self.settings.outputFolder,self.plate, self.settings.outputFile.format(self.plate[:10], self.well)))
            result = pickle.load(f); f.close()
            return result
        
        #if not I load it
        
        path_classif="/sample/0/plate/{}/experiment/{:>05}/position/{{}}/feature/primary__test/object_classification/prediction".format(self.plate, self.well)
        
        result=None
        
        for pos in self.pos_list:
            classification = vi.readHDF5(self.file_.format(pos), path_classif.format(pos))
            objects=vi.readHDF5(self.file_.format(pos), self.path_objects.format(pos))
            
            frames = sorted(list(set(objects['time_idx'])))
            if result is None:
                result=np.zeros(shape=(np.max(frames)+1, 18), dtype=float)
                
            for frame in frames:
                result[frame]+= np.bincount(classification['label_idx'][np.where(objects['time_idx']==frame)], minlength=18)
                    
        #putting UndefinedCondensed with Apoptosis
        result[:,11]+=result[:,16]
        result[:,16]=result[:,17]
        
        r=result[:,:-3]
        
        print r.shape
        
        return r
    
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
    
    @staticmethod
    def load_result(thing, setting_file='analyzer/settings/settings_drug_screen_thalassa.py', **kwargs):
        if thing=='transport':
            return pheno_seq_extractor._load_transport_distance(**kwargs)
        
        if thing=='ttransport':
            return pheno_seq_extractor._load_Ttransport_distance(**kwargs)
        
        if thing=='pheno_score_DS':
            p=pheno_seq_extractor(setting_file, plate=None, well=None)
            return p.load_pheno_score_DS()

        if thing=='pheno_score_MITO':
            p=pheno_seq_extractor(setting_file, plate=None, well=None)
            return p.load_pheno_score_MITO(**kwargs)
        
        if thing=='nature':
            return pheno_seq_extractor._load_nature_distance(**kwargs)
        
        if thing=='pheno_seq_MITO':
            p=pheno_seq_extractor(setting_file, plate=None, well=None )
            return p.load_pheno_seq_results_MITO(**kwargs)
        
        if thing=='pheno_seq_DS':
            p=pheno_seq_extractor(setting_file, plate=None, well=None )
            return p.load_pheno_seq_results_DS(**kwargs)
        
    @staticmethod
    def _load_nature_distance(filename='nature', folder='/cbio/donnees/aschoenauer/projects/drug_screen/results/distance_nature', 
                              len_=7527):
        missed=[]
        result=np.zeros(shape=(len_, len_))
        for i in range(len_):
            el='{}_{}.pkl'.format(filename, i)
            try:
                f=open(os.path.join(folder, el))
                d=pickle.load(f); f.close()
            except:
                print "Unopenable ", el
                missed.append(i)
            else:
                result[i, i+1:]=d
                result[i+1:, i]= result[i,i+1:].T
                
        return result, missed

        
        
    @staticmethod
    def _load_transport_distance(filename="pheno_distance", folder='/cbio/donnees/aschoenauer/projects/drug_screen/results/distances_pheno_cost2', len_=7526,
                       num_lambda=5):
        '''
       Loading transport distance, time-aggregated. Mitocheck experiments are at the beginning
'''
        missed=[]
        if num_lambda>1:
            result=[np.zeros(shape=(len_, len_)) for k in range(num_lambda)]
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
        else:
            result=np.zeros(shape=(len_, len_))
            for i in range(len_):
                el='{}_{}.pkl'.format(filename, i)
                try:
                    f=open(os.path.join(folder, el))
                    d=pickle.load(f); f.close()
                except:
                    print "Unopenable ", el
                    missed.append(i)
                else:
                    result[i, i+1:]=d
                    result[i+1:, i]= result[i,i+1:].T
                
        return result, missed

    @staticmethod
    def _load_Ttransport_distance(filename="pheno_distance", 
                                 folder='/cbio/donnees/aschoenauer/projects/drug_screen/results/distances_pheno_cost2_unagg', len_=7526,
                                 num_timepoints=18
                                 ):
        '''
        Loading transport distance, for different timepoints. Mitocheck experiments are at the end
'''
        missed=[]
        result=np.zeros(shape=(len_, len_, num_timepoints))
        for i in range(len_):
            el='{}_{}.pkl'.format(filename, i)
            
            try:
                f=open(os.path.join(folder, el))
                d=pickle.load(f); f.close()
            except:
                print "Unopenable ", el
                missed.append(i)
            else:
                local_arr=np.vstack((d[time_point] for time_point in d))
#                local_arr=np.max(local_arr, 0)

                result[i, i+1:]=local_arr.T
                for k in range(num_timepoints):
                    result[i+1:, i, k]= result[i,i+1:,k].T
        
        return result, missed
    
    @staticmethod
    def load_pheno_score_MITO(exp_list, folder='/media/lalil0u/New/projects/drug_screen/results/'):
        f=open(os.path.join(folder, 'MITO_results_phenoscores.pickle'))
        pheno_scores_dict=pickle.load(f); f.close()
        f=open(os.path.join(folder, 'MITO_pheno_scores_VALIDATION_EXP.pickle'))
        pheno_scores_dict.update(pickle.load(f)); f.close()
        
        r=np.zeros(shape=(len(exp_list), len(CLASSES)))
        
        for i,exp in enumerate(exp_list):
            for j, class_ in enumerate(CLASSES):
                if class_=='Binucleated':
                    r[i,j]=pheno_scores_dict[exp]['max_{}'.format('Shape1')]
                elif class_=='Polylobed':
                    r[i,j]=pheno_scores_dict[exp]['max_{}'.format('Shape3')]
                else:
                    r[i,j]=pheno_scores_dict[exp]['max_{}'.format(class_)]
                    
        return r
    
    @staticmethod
    def load_proliferation():
        result=[]; ctrl_result=defaultdict(list)
        f=open('../data/expL_DS_PASSED_QC.pkl')
        expl=pickle.load(f); f.close()
        
        expl=np.array([(int(el.split('--')[0].split('_')[1]), int(el.split('--')[1])) for el in expl])
        
        for k in range(1,4):
            f=open('/media/lalil0u/New/projects/drug_screen/results/processedDictResult_PLT0900_0{}.pkl'.format(k))
            d=pickle.load(f); f.close()
            
            for exp_num in expl[np.where(expl[:,0]==k)][:,1]:
                if d[exp_num]['Xenobiotic']=='empty':
                    ctrl_result[k].append(d[exp_num]['proliferation'][0])
                else:
                    result.append(("LT0900_0{}--{:>03}".format(k,exp_num),d[exp_num]['proliferation'][0]))
        
        for k in range(1,4):
            ctrl_result[k]=np.array(ctrl_result[k])
        
        return result, ctrl_result
    
    
    def load_pheno_score_DS(self):
        res=None; who=[]
        ctrl_points=None
        
        for plate in self.settings.plates:
            phenotypic_scores=filter(lambda x: 'pheno_score' in x, os.listdir(os.path.join(self.settings.outputFolder, plate)))
            
            for file_ in phenotypic_scores:
                f=open(os.path.join(self.settings.outputFolder, plate, file_))
                scores=pickle.load(f); f.close()
                if scores.shape[0]==15:
                    ctrl_points=scores[np.newaxis,:] if ctrl_points is None else np.vstack((ctrl_points, scores[np.newaxis,:]))
                else:
                    res=scores[0][np.newaxis,:] if res is None else np.vstack((res, scores[0][np.newaxis,:]))
                    who.append('{}--{:>03}'.format(plate, int(file_.split('_')[-1].split('.')[0])))
                    
        return res, who, ctrl_points
    
    def load_pheno_seq_results_MITO(self,exp_list, time_aggregated=False):
        '''
        Here we're loading results from per frame files (pheno_count) on a per experiment basis. This will be interesting to look at distances between experiments
        based on phenotypes, aggregated on time
        '''
        missed=[]
        yqualDict=expSi(self.settings.mitocheck_qc_file)
        dictSiEntrez=siEntrez(self.settings.mitocheck_mapping_file)
        result = None; i=0; who=[]
        for pl,w in exp_list:
            print i,
            
            try:
                f=open(os.path.join(self.settings.outputFolder,pl, self.settings.outputFile.format(pl[:9], w)), 'r')
                pheno_seq_per_frame= pickle.load(f)
                f.close()
            except:
                print "Loading error for ", pl, w
                self.plate=pl; self.well=w
                if self.MITO_usable():
                    missed.append((pl,w))
                continue
            else:
            #15 and 16 are respectively out of focus and artefact objects. We don't want them
                if time_aggregated:
                    pheno_seq_per_frame=np.sum(pheno_seq_per_frame, 0)
                    pheno_seq_list=pheno_seq_per_frame/float(np.sum(pheno_seq_per_frame))
                    result = np.vstack((result, pheno_seq_list)) if result is not None else pheno_seq_list
                else:
                    pheno_seq_per_frame=np.vstack((np.sum(pheno_seq_per_frame[self.settings.time_agg*k:self.settings.time_agg*(k+1)],0) 
                                                   for k in range(pheno_seq_per_frame.shape[0]/self.settings.time_agg)))
                    if result is not None:
                        shape_=min(result.shape[1], pheno_seq_per_frame.shape[0])
                        result = np.vstack((result[:,:shape_], pheno_seq_per_frame[np.newaxis][:,:shape_]))
                    else:
                        result= pheno_seq_per_frame[np.newaxis]
                    
        #ATTENTION gros bug avec LTValidMItosis si on limite a la taille et non pas au split de -- le nom de la plaque...
                who.append('{}--{:>03}'.format(pl.split('--')[0], w))
            finally:
                i+=1
        
        _name='time' if not time_aggregated else ''
                
        print "Saving to ",self.settings.outputFile.format("ALL", "MITO_{}".format(_name))
        
        f=open(os.path.join(self.settings.outputFolder,self.settings.outputFile.format("ALL", "MITO_{}".format(_name))), 'w')
        pickle.dump((result, who),f); f.close()
        return missed
    
    def load_pheno_seq_results_DS(self,exp_list, time_aggregated=False):
        '''
        Here we're loading results on a per experiment basis. This will be interesting to look at distances between experiments
        based on phenotypes, vs distances based on trajectory types.
        FOR THE DRUG SCREEN
        PER FRAME
        '''

        result = None; i=0; who=[]; missed=[]
        for pl,w in exp_list:
            print i,
            
            try:
                f=open(os.path.join(self.settings.outputFolder,pl, self.settings.outputFile.format(pl[:9], w)), 'r')
                pheno_seq_per_frame= pickle.load(f)
                f.close()
            except:
                print "Loading error for ", pl, w
                self.plate=pl; self.well=w
                if self.DS_usable():
                    missed.append((pl,w))
                continue
            else:
            #15 and 16 are respectively out of focus and artefact objects. We don't want them
                if time_aggregated:
                    pheno_seq_per_frame=np.sum(pheno_seq_per_frame, 0)
                    pheno_seq_list=pheno_seq_per_frame/float(np.sum(pheno_seq_per_frame))
                    result = np.vstack((result, pheno_seq_list)) if result is not None else pheno_seq_list
                else:
                    pheno_seq_per_frame=np.vstack((np.sum(pheno_seq_per_frame[self.settings.time_agg*k:self.settings.time_agg*(k+1)],0) 
                                                   for k in range(pheno_seq_per_frame.shape[0]/self.settings.time_agg)))
                    result = np.vstack((result, pheno_seq_per_frame[np.newaxis])) if result is not None else pheno_seq_per_frame[np.newaxis]
                who.append('{}--{:>03}'.format(pl, w))
            finally:
                i+=1
                
        print "Saving"
        
        f=open(os.path.join(self.settings.outputFolder,self.settings.outputFile.format("ALL", "DS_time")), 'w')
        pickle.dump((result, who),f); f.close()
        return missed
    
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
    
    def _ctrl_usable(self):
        #i. Opening file to see qc
        f=open(os.path.join(self.settings.result_dir, 'processedDictResult_P{}.pkl'.format(self.plate)))
        d=pickle.load(f); f.close()
        
        possible_ctrl=[el for el in d if 'Xenobiotic' in d[el] and d[el]['Xenobiotic']=='empty']
        
        return [each for each in possible_ctrl if each not in d['FAILED QC']]
    
    def _ctrl_groups(self, ctrl_wells):
        permutations = np.random.permutation(len(ctrl_wells))
        
        return np.array(ctrl_wells)[permutations]
    
    def load_ctrl_well_list(self):
        f=open(os.path.join(self.settings.outputFolder,self.plate, self.settings.outputFile.format(self.plate[:10], 'CTRL')))
        ctrl_wells=pickle.load(f)
        f.close()
        
        return ctrl_wells

    def _smooth(self, X):
                # lowess
        lowess = sm.nonparametric.lowess
        Xsmooth = None
        
        for j in range(X.shape[1]):
            reg = np.array([x[1] for x in lowess(X[:,j], range(X.shape[0]), frac=0.5)])
            Xsmooth = reg if Xsmooth is None else np.vstack((Xsmooth, reg))
        
        return Xsmooth.T
    
    def phenotypic_score(self, well_count, ctrl_count):
        ctrl_count/=np.sum(ctrl_count,1)[:,np.newaxis]
        well_count/=np.sum(well_count,1)[:,np.newaxis]
        
        if self.settings.smooth:
            ctrl_count=self._smooth(ctrl_count)
            well_count=self._smooth(well_count)

        size_=min(well_count.shape[0], ctrl_count.shape[0])
        
        diff=well_count[:size_]-ctrl_count[:size_]
        return np.diag(diff[np.argmax(np.abs(diff), 0)])
    
    def load_ctrl_well_dict(self, c_wells):
        if type(c_wells)!=np.int64:
            result={}
            for c_well in c_wells:
                result[c_well]=self.load_ctrl_well_dict(c_well)
            return result
        else:
            try:
                f=open(os.path.join(self.settings.outputFolder,self.plate, self.settings.outputFile.format(self.plate[:10], c_wells)))
                counts=pickle.load(f); f.close()
                print "Loading pheno counts for ctrl well {} from file ".format(c_wells),
            except IOError:
                print "Computing pheno counts for ctrl well {} ".format(c_wells),
                p=pheno_seq_extractor(setting_file=self.settings_file, plate=self.plate, well=c_wells)
                counts= p(time_pheno_count_only=True)
                
            return counts
    
    def __call__(self,time_pheno_count_only=False, action='pheno_score'):
        if not os.path.isdir(os.path.join(self.settings.outputFolder, self.plate)):
            os.mkdir(os.path.join(self.settings.outputFolder, self.plate))
        
        if self.well=='CTRL':
            #i.see how many ctrl wells there are for this plate
            #ii. separate them into three groups
            #iii. write those in some files for further computation
            ctrl_wells=self._ctrl_usable()
            self.save(self._ctrl_groups(ctrl_wells))
        else:            
            #i. check qc
            try:
                assert self.check_qc()
            except AssertionError:
                print "QC failed"
                return
            
        #ii. load classification per frame
            well_count=self.classificationPerFrame()
        #iii. save it for further use    
            self.save(well_count)   
            if time_pheno_count_only:
                return well_count 
        #iv. now compute distance to controls
        
            if action == 'pheno_score':
                #load ctrl lists
                ctrl_wells=self.load_ctrl_well_list()
                #load ctrl pheno counts
                ctrl_count_dict= self.load_ctrl_well_dict(ctrl_wells)
                
                cut=len(ctrl_wells)/3
                scores=None
                for k in range(3):
                    curr_ctrl=filter(lambda x: x not in ctrl_wells[k*cut:(k+1)*cut], ctrl_wells)
                    if self.well in curr_ctrl:
                        continue
                    
                    ctrl_count=np.zeros(shape=ctrl_count_dict[curr_ctrl[0]].shape)
                    for c_well in curr_ctrl:
                        ctrl_count+=ctrl_count_dict[c_well]
                    curr_r=self.phenotypic_score(well_count, ctrl_count)
                    scores= curr_r if scores is None else np.vstack((scores, curr_r))
            elif action=='pheno_dist':
                pass
            elif action =='time_transport_dist':
                pass
            self.save(scores, filename=self.settings.outputFile_[action])
            
        return
    
    
if __name__ == '__main__':
    verbose=0
    description =\
'''
%prog - Computing phenotype sequences given tracklets
Input:
- plate, well: experiment of interest. Well under the form 315
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

    parser.add_option("-c", dest="count_only",type=int,default=0,
                      help="For ctrl DS and Mitocheck, do the aggregated pheno count only")

    
    (options, args) = parser.parse_args()
    if options.well!='CTRL':
        if len(options.well)>3:
            well=int(options.well.split('_')[0])
        else:
            well=int(options.well)
    else:
        well='CTRL'
    
    p=pheno_seq_extractor(options.settings_file, options.plate,well)
    p(time_pheno_count_only=options.count_only)
    print "Done"
        
        
