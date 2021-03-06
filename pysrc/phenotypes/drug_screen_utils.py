import matplotlib.pyplot as p
import matplotlib as mpl
import numpy as np
import pdb,os
from _collections import defaultdict

from util.listFileManagement import expSi, siEntrez
from util.make_movies_mito_cbio import ColorMap
from scipy.stats.stats import scoreatpercentile

from phenotypes import *

from phenotype_seq import pheno_seq_extractor
from operator import itemgetter

def plotClusteredTogether(distance_name, folder='/media/lalil0u/New/projects/drug_screen/results/',filename='Clusters_{}_{}.pkl',level_row=0.2,
                          cmap=mpl.cm.Greys):
    f=open(os.path.join(folder, 'inference_Freplicates', filename.format(distance_name, level_row)))
    clusters=pickle.load(f); f.close()
    reverse_clusters={}
    for k in clusters:
        for el in clusters[k]:
            reverse_clusters[el]=k
    
    comb=right_hit_cond_order
    
    mat=np.zeros(shape=(len(comb), len(comb)))
    
    for i,el in enumerate(comb):
        mat[i,i]=1
        for j in range(i+1, len(comb)):
            el2=comb[j]
            if reverse_clusters['{}--{}'.format(*el)]==reverse_clusters['{}--{}'.format(*el2)]:
                mat[i,j]=1
                mat[j,i]=1
                
    labels=['{} {}'.format(*el) for el in comb]
    
    f=p.figure(figsize=(20,20))
    ax=f.add_subplot(111)
    ax.matshow(mat, cmap=cmap)
    ax.set_yticks(range(len(comb)))
    ax.set_yticklabels(labels, fontsize='small')#
    ax.set_xticks(range(len(comb)))
    ax.set_xticklabels(labels, fontsize='small', rotation='vertical')
    p.savefig(os.path.join(folder, 'inference_Freplicates', 'cond_clustering_{}.png'.format(distance_name)))
    
    return
    

def plotProlifResult(ctrl_res, res, folder='/media/lalil0u/New/projects/drug_screen/results/'):
    if ctrl_res ==None or res==None:
        res, ctrl_res = pheno_seq_extractor.load_proliferation()
        
    f=open(os.path.join(folder, 'DS_hits_1.5IQR.pkl'))
    _, who_hits,_=pickle.load(f)
    f.close()
        
    prolif = np.array([el[1] for el in res])
    who=np.array([el[0] for el in res])
    x=np.random.normal(1, 0.05, size=prolif.shape[0])
    
    
    f=p.figure()
    ax=f.add_subplot(111)
    ctrl_prolif=np.hstack((ctrl_res[el] for el in ctrl_res))
    ax.boxplot(ctrl_prolif)
    ax.scatter(x, prolif,alpha=0.5, s=5)
    for i,el in enumerate(who):
        if el not in who_hits:
            ax.text(x[i], prolif[i], who[i], fontsize='small')
    
    p.show()
    
    return pheno_seq_extractor.hit_detection_proliferation(prolif, who, who_hits, ctrl_prolif, whis=1.5)


def plotInferenceResult(distance_name_list, result, cmap):
    '''
   Manque la legende 
'''
    norm=mpl.colors.Normalize(0,0.5)
    
    num_cond=len(result[distance_name_list[0]])
    
    arr=None
    for dist in filter(lambda x: x in result, ['N_pheno_score','U_pheno_score','transport','nature','ttransport_INT','ttransport_MAX']):
        
        curr_arr=None
        cond_labels=[]
        for cond in sorted(filter(lambda x: result[dist][x]['genes']!=[], result[dist])):
            cond_labels.extend(['{}{:>10}'.format(cond, result[dist][cond]['gene_list'][k]) for k in range(len(result[dist][cond]['genes']))])
            curr_arr=result[dist][cond]['genes'] if curr_arr == None else np.hstack((curr_arr, result[dist][cond]['genes']))
        arr=curr_arr[:,np.newaxis] if arr is None else np.hstack((arr, curr_arr[:,np.newaxis]))
    arr2=np.array(arr, dtype=float)/2452
    f=p.figure()
    ax=f.add_subplot(111)
    
    ax.matshow(arr2,cmap=cmap, norm=norm, aspect='auto')

    ax.set_yticks(range(len(cond_labels)))
    ax.set_yticklabels(cond_labels)
    ax.set_xticks(range(len(result)))
    xlabels=[DISTANCES[el] for el in filter(lambda x: x in result, ['N_pheno_score','U_pheno_score','transport','nature','ttransport_INT','ttransport_MAX'])]
    ax.set_xticklabels(xlabels)
    ticks=ax.get_yticks()

    ax2=ax.twiny()
    ax2.set_xlim(0, len(result)+1)
    for i in range(arr.shape[0]):
        for j in range(arr.shape[1]):
            ax2.text(j+1,ticks[i]+0.45,arr[i,j], fontsize=10)
    ax2.set_xticks([])
    # axcb - placement of the color legend
    [axcb_x, axcb_y, axcb_w, axcb_h] = [0.07,0.93,0.18,0.02]
    axcb = f.add_axes([axcb_x, axcb_y, axcb_w, axcb_h], frame_on=False)  # axes for colorbar
    axcb.set_title('Legend', fontsize=15)
    cb = mpl.colorbar.ColorbarBase(axcb, cmap=cmap,norm=norm, orientation='horizontal',
                                   )
 #   cb.ax.set_xticklabels([0, 0.5], fontsize=15)
    
    p.show()
    
    return xlabels,arr
    
    

def selecting_right_Mito_exp(folder='/media/lalil0u/New/projects/drug_screen/results/'):
    f=open('../data/ANCIENTmitocheck_exp_hitlist.pkl')
    mito_hitexp=list(set(pickle.load(f)))
    f.close()
    
    f=open(os.path.join(folder, 'MITO_pheno_scores_NOTVAL.pkl'))
    r=pickle.load(f);f.close()
    big_phenoscore=dict(zip(r[1], r[0]))

    f=open(os.path.join(folder, 'MITO_pheno_scores_VAL.pkl'))
    r=pickle.load(f);f.close()
    val_phenoscore=dict(zip(r[1], r[0]))

    yqualdict=expSi('/media/lalil0u/New/workspace2/Xb_screen/data/mapping_2014/qc_export.txt')
    dictSiEntrez=siEntrez('/media/lalil0u/New/workspace2/Xb_screen/data/mapping_2014/mitocheck_siRNAs_target_genes_Ens75.txt')
    genes_big=[]
    gene_si=defaultdict(list)
    res_siRNA=defaultdict(list)
    si_exp=defaultdict(list)
    
    unmapped_si=[]
    
    for exp in mito_hitexp:
        try:
            currSi=yqualdict[exp]; currGene = dictSiEntrez[currSi]
            
        except KeyError:
            #print "{} siRNA not in mapping file anymore".format(yqualdict[exp]),
            unmapped_si.append(yqualdict[exp])
        else:
            if exp in big_phenoscore:
                genes_big.append(currGene)
                gene_si[currGene].append(currSi)
                res_siRNA[currSi].append(big_phenoscore[exp][0])
                si_exp[currSi].append(exp)
            else:
                print "{} no data".format(exp)
                continue
    print "------------------------------------------------------Youpi next step looking at validation experiments"
    genes_big=sorted(list(set(genes_big)))
            
    yqualdict2=expSi('/media/lalil0u/New/workspace2/Xb_screen/data/mapping_2014/qc_validation_exp.txt', primary_screen=False)
    genes_big2=[]
    for exp in yqualdict2:
        try:
            currSi=yqualdict2[exp]; currGene = dictSiEntrez[currSi]
        except KeyError:
            if yqualdict2[exp]!='empty':
#                print "{} siRNA not in mapping file anymore".format(yqualdict2[exp]),
                unmapped_si.append(yqualdict2[exp])
        else:
            if exp in val_phenoscore:
                genes_big2.append(currGene)
                gene_si[currGene].append(currSi)
                res_siRNA[currSi].append(val_phenoscore[exp][0])
                si_exp[currSi].append(exp)
            else:
                print "{} no data".format(exp)
                continue
            
    genes_big2=sorted(list(set(genes_big2)))
    
    print "Unmapped siRNAs ", len(unmapped_si)
    
    print "How many genes do we gain by using validation experiments?"
    print len([el for el in genes_big if el not in genes_big2])
    
    genes_big.extend(genes_big2)
    genes_big=sorted(list(set(genes_big)))
    print "How many genes finally ", len(genes_big)
    final_siRNA_list=[]
    final_exp_list=[]
    genesL=[]
    count_siRNA_total=0
    for gene in genes_big:
        currSiL=gene_si[gene]
        counts=Counter(currSiL)
        count_siRNA_total+=len(counts)
        currRes=[]; siL=[]
        for siRNA in filter(lambda x: counts[x]>=2, counts):
            currRes.append(np.median(res_siRNA[siRNA]))
            siL.append(siRNA)

        if currRes!=[]: 
            choice=np.array(siL)[np.argmin(np.array(currRes))]
            final_exp_list.extend(si_exp[choice])
            final_siRNA_list.extend([choice for k in range(counts[choice])])
            genesL.extend([gene for k in range(counts[choice])])
    print "How many siRNAs in total ", count_siRNA_total
    return genesL, final_exp_list, final_siRNA_list

def from_geneL_to_phenoHit(geneL,hitFile='../data/mitocheck_exp_hitlist_perPheno.pkl'):
    f=open(hitFile)
    expPerPheno=pickle.load(f); f.close()
    yqualdict=expSi('/media/lalil0u/New/workspace2/Xb_screen/data/mapping_2014/qc_export.txt')
    dictSiEntrez=siEntrez('/media/lalil0u/New/workspace2/Xb_screen/data/mapping_2014/mitocheck_siRNAs_target_genes_Ens75.txt')
    
    res=defaultdict(list)
    
    for pheno in expPerPheno:
        for exp in expPerPheno[pheno]:
            if yqualdict[exp] in dictSiEntrez:
                res[dictSiEntrez[yqualdict[exp]]].append(pheno)
                
    for gene in res:   
        res[gene]=sorted(list(set(res[gene])))
        
    return res

def plotSeparability2D(result, result2, name_result, name_result2):
    
    f=p.figure()
    ax=f.add_subplot(111)
    ax.grid(True)
    for i,el in enumerate(DISTANCES):
        ax.errorbar(np.nanmean(result[el]), np.nanmean(result2[el]), 
               xerr=np.std(result[el][~np.isnan(result[el])]) ,
               yerr=np.std(result2[el][~np.isnan(result2[el])]), fmt='o', color=couleurs[i], label=DISTANCES[el])
    ax.legend()
        
#     ax.set_xticklabels([])
    ax.set_xlabel(name_result)
    ax.set_ylabel(name_result2)
#     ax.set_title('Replicate separability score')
        
    p.show()


def plotSeparability(result, result2):
    
    m=np.min(result.values())
    res_=[(el, result[el]) for el in np.array(result.keys())[np.argsort(result.values())]]
    
    f=p.figure()
    ax=f.add_subplot(121)
    ax.grid(True)
    ax.bar(range(len(result)), [m/el[1] for el in res_], alpha=0.7, color='blue')
    
    for i,el in enumerate(res_):
        ax.text(i, el[1], DISTANCES[el[0]])
    
    ax.set_xticklabels([])
    ax.set_xlabel('Distances')
    ax.set_ylabel('Arbitrary units')
    ax.set_title('Replicate separability score')
    
    ax=f.add_subplot(122)
    m=np.max(result2.values())
    ax.grid(True)
    ax.bar(range(len(result2)), [result2[el[0]]/m for el in res_], alpha=0.7, color='blue')
    
    for i,el in enumerate(res_):
        ax.text(i, el[1], DISTANCES[el[0]])
    
    ax.set_xticklabels([])
    ax.set_xlabel('Distances')
    ax.set_ylabel('Arbitrary units')
    ax.set_title('Replicate correlation score')
    
    p.show()

    
def plotExternalConsistency(corr_dict, labels, cmap=mpl.cm.bwr):
    norm = mpl.colors.Normalize(0.5,1)
    corr=np.vstack((corr_dict[el] for el in sorted(corr_dict.keys())))
    
    f=p.figure()
    ax=f.add_subplot(111)
    ax.matshow(corr, cmap=cmap, norm=norm)
    p.xticks(range(len(labels)), labels, rotation='vertical')
    p.yticks(range(len(corr_dict)), [DISTANCES[el].replace('\n', '') for el in sorted(corr_dict)])
    
    p.show()


def plotInternalConsistency(M, tick_labels, cmap=mpl.cm.bwr, second_labels=None):
    
    norm = mpl.colors.Normalize(0,scoreatpercentile(M.flatten(), 95))
    f=p.figure()
    ax=f.add_subplot(111)
    ax.matshow(M, cmap=cmap, norm=norm)
    p.yticks(range(0,M.shape[0],15),tick_labels[::15])
    ax.tick_params(labelsize=6)
#     if second_labels is not None:
#         ax_=ax.twinx()
#         ax_.set_yticks(range(M.shape[0]))
#         ax_.set_yticklabels(second_labels)
#         ax_.tick_params(labelsize=4)
#         ax_.set_yscale(ax.get_yscale())
    p.show()
    
    return

def plotPrep(file_='/media/lalil0u/New/projects/drug_screen/results/MDS_Mitocheck_DS_distances_0.1.pkl'):
    '''
    File without plate 4
'''
    f=open(file_, 'r')
    r,who=pickle.load(f); f.close()
    
    f=open('../data/mitocheck_exp_hitlist_perPheno.pkl')
    hitlistperpheno=pickle.load(f)
    f.close()
    
    colors=[]
    type_=defaultdict(list)
    for phenotype in hitlistperpheno:
        for el in hitlistperpheno[phenotype]:
            type_[el].append(phenotype)
            
    phenotypes=hitlistperpheno.keys()
    for el in who[:lim_Mito]:
        colors.append(couleurs[phenotypes.index(type_[el][0])])
        
    f=open('/media/lalil0u/New/projects/drug_screen/results/well_drug_dose.pkl')
    genes, drugs, doses, doses_cont, _=pickle.load(f)
    f.close()
    
    exposure=[]
    ord_doses=[]
    for exp in who[:lim_Mito]:
        if len(type_[exp])<2:
            exposure.append(type_[exp][0])
        else:
            exposure.append('NO')
    for exp in who[lim_Mito:]:
        e='{}--{:>05}'.format(exp.split('--')[0], int(exp.split('--')[1]))
        exposure.append(drugs[e])
        ord_doses.append(doses_cont[e])
        
        if drugs[e]=='empty':
            colors.append('green')
        else:
            colors.append('red')
        
    return colors, drugs, r, who, phenotypes, np.array(exposure), np.array(ord_doses)


def globalPlot(colors, exposure,r, who, phenotypes):
    '''
   MDS visu 
'''
    f,axes=p.subplots(1,2,sharex=True, sharey=True)
    for i in range(lim_Mito):
        axes[0].scatter(r[i,0], r[i,1],color=colors[i], s=5)
    for i in range(lim_Mito, r.shape[0]):
        if exposure[i]=='empty':
            axes[0].scatter(r[i,0], r[i,1],color='grey', s=5, marker='+')
    axes[0].scatter(0,0,color='grey',label='DS control',marker='+')
    for pheno in phenotypes:
        axes[0].scatter(0,0,color=couleurs[phenotypes.index(pheno)], label=pheno, s=5)
    for i in range(lim_Mito, r.shape[0]):
        axes[1].scatter(r[i,0], r[i,1],color=colors[i], s=5)
    axes[1].scatter(0,0,color='red',label='DS')
    axes[1].scatter(0,0,color='green',label='DS ctrl')
    axes[1].legend()
    axes[0].legend()
    p.show()

def distinctDrugPlots(colors, r, who, phenotypes, exposure):
    '''
       MDS visu 
'''
    f,axes=p.subplots(3,5)
    for i in range(lim_Mito):
        if exposure[i] in phenotypes[:5]:
            axes[0,phenotypes.index(exposure[i])].scatter(r[i,0], r[i,1],color=colors[i], s=5)
        elif exposure[i] in phenotypes[5:]:
            axes[1,phenotypes.index(exposure[i])-5].scatter(r[i,0], r[i,1],color=colors[i], s=5)
    
    for i,pheno in enumerate(phenotypes):
        if i<5:
            axes[0,i].scatter(0,0,color=couleurs[phenotypes.index(pheno)], label=pheno, s=5)
        else:
            axes[1,i-5].scatter(0,0,color=couleurs[phenotypes.index(pheno)], label=pheno, s=5)
    
    for i,el in enumerate(who[lim_Mito:]):
        j=i+lim_Mito
        if exposure[j] in DRUGS[:7]:
            axes[2,1].scatter(r[j,0], r[j,1],color=couleurs[DRUGS.index(exposure[j])], s=5)
        elif exposure[j] in DRUGS[7:14]:
            axes[2,2].scatter(r[j,0], r[j,1],color=couleurs[DRUGS.index(exposure[j])-7], s=5)
        elif exposure[j] in DRUGS[14:21]:
            axes[2,3].scatter(r[j,0], r[j,1],color=couleurs[DRUGS.index(exposure[j])-14], s=5)
        elif exposure[j] in DRUGS[21:]:
            axes[2,4].scatter(r[j,0], r[j,1],color=couleurs[DRUGS.index(exposure[j])-21], s=5)
        else:
            axes[2,0].scatter(r[i,0], r[i,1],color='grey', s=5, marker='+')
            
    for i,drug in enumerate(DRUGS):
        if i<7:
            axes[2,1].scatter(0,0, color=couleurs[i], s=5, label=drug)
        elif i>=21:
            axes[2,4].scatter(0,0, color=couleurs[i-21], s=5, label=drug)
        elif i>=7 and i<14:
            axes[2,2].scatter(0,0, color=couleurs[i-7], s=5, label=drug)
        else:
            axes[2,3].scatter(0,0, color=couleurs[i-14], s=5, label=drug)
            
    for ax in axes:
        for el in ax:
            el.legend(prop={'size':8})
    p.show()
    
def distinctDrugBoxplots_PERC(who, exposure,doses, perc, phenotypes):
    '''
    We suppose that plate 4 is already removed from r and who
    Here we're directly looking at phenotypes percentages over the whole movie, compared with controls and Mitocheck hits
    Percentages are in the file /media/lalil0u/New/projects/drug_screen/results/all_Mitocheck_DS_phenohit.pkl
'''
    cm = ColorMap()
    cr = cm.makeColorRamp(256, ["#FFFF00", "#FF0000"])
    degrade = [cm.getColorFromMap(x, cr, 0, 10) for x in range(11)]
    
    f,axes=p.subplots(4,9, sharex=True, sharey=True)
    
    for i, pheno in enumerate(phenotypes):
        axes.flatten()[i].boxplot([perc[np.where(exposure==pheno),k] for k in range(perc.shape[1])])
        axes.flatten()[i].set_title(pheno)
        axes.flatten()[i].set_ylim(-0.05,0.9)
        
    dd=np.zeros(shape=lim_Mito); dd.fill(-1)
    doses=np.hstack((dd, doses))
    
    for j, drug in enumerate(DRUGS):
        for dose in range(10):
            where_=np.where((exposure==drug)&(doses==dose))[0]
            if where_.shape[0]>0: 
                for k in range(perc.shape[1]):
                    axes.flatten()[8+j].scatter([k+1 for x in range(where_.shape[0])], perc[where_,k], color=degrade[dose], alpha=0.5, s=5)
        axes.flatten()[8+j].set_title(drug)
    print pheno
    where_=np.where(exposure=='empty')[0]
    axes.flatten()[8+j+1].boxplot([perc[where_,k] for k in range(perc.shape[1])])
    axes.flatten()[8+j+1].set_title('Control')
    axes.flatten()[8+j+1].set_xticklabels(CLASSES, rotation='vertical')
    p.show()
    
def mito_PHENOSCORE(file_='MITO_pheno_scores.pkl', 
                    folder='/media/lalil0u/New/projects/drug_screen/results/'):
    f=open('../data/mitocheck_exp_hitlist_perPheno.pkl')
    hitlistperpheno=pickle.load(f)
    f.close()
    
    f=open(os.path.join(folder, file_), 'r')
    scores, who=pickle.load(f); f.close()
    norm = mpl.colors.Normalize(-0.2,0.6)
    yqualdict=expSi('../data/mapping_2014/qc_export.txt')
    dictSiEntrez=siEntrez('../data/mapping_2014/mitocheck_siRNAs_target_genes_Ens75.txt')
    
    bigGenesL=np.array([dictSiEntrez[yqualdict[e]] for e in who])
    
    for pheno in hitlistperpheno:
        expL=hitlistperpheno[pheno]
        genesL=np.array([dictSiEntrez[yqualdict[e]] for e in filter(lambda x: yqualdict[x] in dictSiEntrez, expL)])
        distinct_genes = sorted(list(set(genesL)))
        ind=np.hstack((np.where(bigGenesL==gene)[0] for gene in distinct_genes))
        print pheno, 
        
        currscores=scores[ind]
        print currscores.shape
        f=p.figure()
        ax=f.add_subplot(111)
        ax.matshow(currscores.T, cmap=mpl.cm.YlOrRd, norm=norm, aspect='auto')
        ax.set_title(pheno)
        ax.set_yticks(range(15))
        ax.set_yticklabels(CLASSES)
        
#        p.show()
        p.savefig(os.path.join(folder, 'pheno_score_MITO_{}.png'.format(pheno[:10])))
    return
    
def distinctDrug_PHENOSCORE(who_ps, res, folder='/media/lalil0u/New/projects/drug_screen/results/'):
    '''
    Here we're looking at phenotypic scores, compared with controls
'''
    
    norm = mpl.colors.Normalize(-0.2,0.6)
    
    cm = ColorMap()
    cr = cm.makeColorRamp(256, ["#FFFF00", "#FF0000"])
    degrade = [cm.getColorFromMap(x, cr, 0, 10) for x in range(11)]

    f=open('/media/lalil0u/New/projects/drug_screen/results/well_drug_dose.pkl')
    _, drugs, _, doses_cont, _=pickle.load(f)
    f.close()
    
    exposure=[]
    doses=[]
    plates=np.array([el.split('--')[0] for el in who_ps])

    for exp in who_ps:
        exposure.append(drugs["{}--{:>05}".format(exp.split('--')[0], int(exp.split('--')[1]))])
        doses.append(doses_cont["{}--{:>05}".format(exp.split('--')[0], int(exp.split('--')[1]))])
    exposure=np.array(exposure); doses=np.array(doses)
    for drug in DRUGS:
        f,axes=p.subplots(1,3, figsize=(24,12))
        for i in range(3):
            currPl='LT0900_0{}'.format(i+1)
            range_dose=sorted(list(set(doses[np.where((plates==currPl)&(exposure==drug))])))
            currM=np.array([[res[np.where((plates==currPl)&(exposure==drug)&(doses==dose))[0], k] for dose in range_dose] for k in range(len(CLASSES))])[:,:,0]
            print currM.shape, drug
            axes.flatten()[i].matshow(currM, cmap=mpl.cm.YlOrRd, norm=norm)
            axes.flatten()[i].set_title(currPl)
            axes.flatten()[i].set_xticks(range(11))
            axes.flatten()[i].set_yticks(range(15))
            axes.flatten()[i].set_yticklabels(CLASSES)
        
        f.suptitle(drug)
        p.savefig(os.path.join(folder, 'phenoscore_nice_{}.png'.format(drug)))
        
    p.close('all')
    
def distinctDrugBoxplots_PHENOSCORE(who_ps, res, ctrl_points, folder='/media/lalil0u/New/projects/drug_screen/results/'):
    '''
    Here we're looking at phenotypic scores, compared with controls
'''
    cm = ColorMap()
    cr = cm.makeColorRamp(256, ["#FFFF00", "#FF0000"])
    degrade = [cm.getColorFromMap(x, cr, 0, 10) for x in range(11)]

    f=open('/media/lalil0u/New/projects/drug_screen/results/well_drug_dose.pkl')
    _, drugs, _, doses_cont, _=pickle.load(f)
    f.close()
    
    exposure=[]
    doses=[]

    for exp in who_ps:
        exposure.append(drugs["{}--{:>05}".format(exp.split('--')[0], int(exp.split('--')[1]))])
        doses.append(doses_cont["{}--{:>05}".format(exp.split('--')[0], int(exp.split('--')[1]))])
    exposure=np.array(exposure); doses=np.array(doses)
    for drug in DRUGS:
        f,axes=p.subplots(4,4, sharex=True, figsize=(24,12))
        for k,class_ in enumerate(CLASSES):
            axes.flatten()[k].boxplot(ctrl_points[:,k])
            for dose in range(10):
                where_=np.where((exposure==drug)&(doses==dose))[0]
                x=np.random.normal(1, 0.05, size=where_.shape[0])
                if where_.shape[0]>0: 
                    axes.flatten()[k].scatter(x, res[where_,k], color=degrade[dose], alpha=0.8, s=6)
            
            axes.flatten()[k].set_title(class_)
        
        p.title(drug)
        p.savefig(os.path.join(folder, 'phenoscore_{}.png'.format(drug)))
        
    p.close('all')
        
def distinctPhenoPlot(res, ctrl_points):
    '''
   Quick plots to see distributions of phenotypic scores as a function of phenotype, with different colors for control and experiment 
'''
    
    colors=['red' for k in range(res.shape[0])]
    colors.extend(['green' for k in range(ctrl_points.shape[0])]); colors=np.array(colors)
    res=np.vstack((res, ctrl_points))
    
    f,axes=p.subplots(4,4)
    for k in range(res.shape[1]):
        ord=np.argsort(res[:,k])
        loc_col=colors[ord]
        axes.flatten()[k].boxplot(res[ord, k][np.where(loc_col=='green')])
        x=np.random.normal(1, 0.08, size=np.where(loc_col=='red')[0].shape[0])
        axes.flatten()[k].plot(x, res[ord, k][np.where(loc_col=='red')],'r.', color='red', alpha=0.2)
        
        axes.flatten()[k].set_title(CLASSES[k])
        
    p.show()
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
            
        