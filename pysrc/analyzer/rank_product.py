import pdb
import numpy as np

from collections import Counter


from analyzer import plates
from _collections import defaultdict
#So that rank product values are not too small I multiply the values resulting both from real result and permutation by a factor
FACTOR=5

def XB_SC_rank_product(data, who, conditions, technical_replicates_key, batch_names, reverse):
    '''
    This function should compute the rank product of all conditions, as defined by Breitling et al 2004
    Given that on some plates the same condition may have been plated twice or thrice,
    technical_replicates_key says how to deal with that.
    
    Mode: reverse=True ie small ranks will correspond to big values in data.
    This is correct if data contains statistics BUT NOT distances. 

    Technical_replicates_key: should indicate which rank to give in this case: median,
    max, min. Min means that we take the smallest possible rank for this condition on the plate, very much too optimistic.
    Max means we take the biggest possible rank for this condition on the plate, conservative.
    '''
    if batch_names is None:
        batch_names =plates
    
    if reverse:
        factor_=-1
        print 'Considering that big data values are the more important. Relevant eg for statistics'
    else:
        factor_=1
        print 'Considering that small data values are the more important. Relevant eg for distances'
    
    all_conditions = Counter(conditions).keys()
    num_technical_replicates=defaultdict(list)
    ranks = np.zeros(shape=(len(all_conditions), len(batch_names)), dtype=float)
    
    
    for j,plate in enumerate(batch_names):
        local_cond=conditions[np.where(who[:,0]==plate)][np.argsort((factor_*data)[np.where(who[:,0]==plate)])]
        
        for i,condition in enumerate(all_conditions):
            ranks[i,j]=technical_replicates_key(np.where(local_cond==condition)[0]+1) if condition in local_cond else -1
        try:
            num_technical_replicates[plate]=[len(np.where((conditions==condition)&(who[:,0]==plate))[0]) for condition in all_conditions]
        except ValueError:
            num_technical_replicates[plate]=[1 for condition in all_conditions]
        ranks[np.where(ranks[:,j]<0),j]=len(np.where(who[:,0]==plate)[0])
        ranks[:,j]/=len(np.where(who[:,0]==plate)[0])
        
    return all_conditions,np.prod(ranks, axis=1, dtype=float),num_technical_replicates


def DS_rank_product(data, who, conditions, technical_replicates_key, batch_names, reverse):
    '''
    This function should compute the rank product of all conditions, as defined by Breitling et al 2004
    Given that on some plates the same condition may have been plated twice or thrice,
    technical_replicates_key says how to deal with that.
    
    Mode: reverse=True ie small ranks will correspond to big values in data.
    This is correct if data contains statistics BUT NOT distances. 

    Technical_replicates_key: should indicate which rank to give in this case: median,
    max, min. Min means that we take the smallest possible rank for this condition on the plate, very much too optimistic.
    Max means we take the biggest possible rank for this condition on the plate, conservative.
    '''
    if batch_names is None:
        batch_names =plates
    
    if reverse:
        factor_=-1
        print 'Considering that big data values are the more important. Relevant eg for statistics'
    else:
        factor_=1
        print 'Considering that small data values are the more important. Relevant eg for distances'
    
    all_conditions = Counter(conditions).keys()
    num_technical_replicates={batch:[] for batch in batch_names}; plate=sorted(batch_names)[0]
#Need to do that only once since we have the same thing for all batches
    num_technical_replicates[plate]=[len(np.where((conditions==condition)&(who[:,0]==plate))[0]) for condition in all_conditions]
    
    ranks = np.zeros(shape=(len(all_conditions), len(batch_names)), dtype=float)

    for j,plate in enumerate(batch_names):
        print plate
        local_cond=conditions[np.where(who[:,0]==plate)][np.argsort((factor_*data)[np.where(who[:,0]==plate)])]
        
        ranks[:,j]=np.array([technical_replicates_key(np.where(local_cond==condition)[0]+1) for condition in all_conditions], dtype=float)
        
        ranks[:,j]=ranks[:,j]/len(np.where(who[:,0]==plate)[0])*FACTOR
        
    return all_conditions,np.prod(ranks, axis=1, dtype=float),num_technical_replicates

def computeRPpvalues(data, who, conditions, technical_replicates_key, num_permutations, reverse, 
                     batch_names=None, random_result=None, signed=False, xb_screen=True):
    '''
    THE function to call to do both the rank product on your data and compute p-values by permutations.
    
    Arguments:
    - data: an np.array of float values, for all experiments. Size n_exp
    - who: an np.array of str values, indicating the experiment names under the following form: [(batch_name, experiment_number)]
        Same order as for the values in data. Size (n_exp,2)
    - conditions: an np.array of str values indicating the condition of each experiment. Size n_exp
    - technical_replicates_key: either np.median or np.max. Indicates how to deal with technical replicates values
    - num_permutations: int, number of permutation of computing p-values
    - batch_names : list of str with the names of your batches
    
    '''
    all_conditions,real_result, num_technical_replicates = DS_rank_product(data, who, conditions, technical_replicates_key, batch_names,
                                                                        reverse)
    if num_permutations is None:
        return zip(all_conditions, real_result)
    
    if random_result is None: 
        if xb_screen:
            rrp=XB_SC_randomRankProduct(num_permutations)
        else:
            rrp=DS_randomRankProduct(num_permutations)
            
        random_result = rrp(num_technical_replicates, technical_replicates_key)
    
    pvals_up=np.zeros(shape=len(all_conditions,), dtype=float)
    for i in range(real_result.shape[0]):
        pvals_up[i]=max(1, len(np.where(random_result<real_result[i])[0]))/float(num_permutations)
        
        
    if signed:
        pvals_down=np.zeros(shape=len(all_conditions,), dtype=float)
        for i in range(real_result.shape[0]):
            pvals_down[i]=max(1, len(np.where(random_result[:,i]>real_result[i])[0]))/float(num_permutations)
    
        return zip(all_conditions,real_result, pvals_up, pvals_down), random_result
    
    return zip(all_conditions,real_result, pvals_up), random_result

class DS_randomRankProduct(object):
    '''
   This a simplified hence faster version for the drug screen. Here, batches are experiments, and conditions are siRNAs:
   we're interested in looking at how the different siRNAs are consistently close for all experiments
   
   But so this means in particular that we have the same number of "conditions" for all batches, so we don't have to do the permutation
   for all batches
'''
    
    def __init__(self, num_permutations=1000):
        self.N = num_permutations
        print "DS RP"
        
    def __call__(self,num_technical_replicates, technical_replicates_key):
        self.batch_names = sorted(num_technical_replicates.keys())
        num_conditions = len(num_technical_replicates[self.batch_names[0]])
        
        result= np.hstack( (self.randomRankProduct(k, num_conditions,num_technical_replicates,technical_replicates_key) for k in range(self.N))) 
            
        return result
            

    def randomRankProduct(self,iter_,num_conditions,num_technical_replicates, technical_replicates_key):
        '''
        This function simulates rank products for random orders
        '''
        print iter_
        plate=self.batch_names[0]
        
        curr_num=np.sum(num_technical_replicates[plate])
        ranks = np.zeros(shape=(num_conditions, len(self.batch_names)), dtype=float)
        
        for i in range(len(self.batch_names)):
            local_cond=np.random.permutation(np.repeat(range(num_conditions), repeats=num_technical_replicates[plate]))
        
            ranks[:,i]=np.array([technical_replicates_key(np.where(local_cond==condition)[0]+1) for condition in range(num_conditions)], dtype=float)
        
        ranks=ranks/curr_num*FACTOR
            
        return np.prod(ranks, axis=1, dtype=float)
        
class XB_SC_randomRankProduct(object):
    '''
    For the xenobiotic screen it was important to take into account replicate numbers and also the fact that not all conditions were present
    in all batches
'''
    def __init__(self, num_permutations=1000):
        self.N = num_permutations
        
    def __call__(self,num_technical_replicates, technical_replicates_key):
        self.batch_names = num_technical_replicates.keys()
        num_conditions = len(num_technical_replicates[self.batch_names[0]])
        result = np.zeros(shape=(self.N,num_conditions), dtype=float)
        
        for k in range(self.N):
            result[k]=self.randomRankProduct(num_conditions,num_technical_replicates, technical_replicates_key)
            
        return result
            

    def randomRankProduct(self,num_conditions,num_technical_replicates, technical_replicates_key):
        '''
        This function simulates rank products for random orders, as close as possible to our experimental setting.
        '''
        ranks = np.zeros(shape=(num_conditions, len(self.batch_names)), dtype=float)
        
        for j,plate in enumerate(self.batch_names):
            curr_num=np.sum(num_technical_replicates[plate])
            
            local_cond=np.repeat(range(num_conditions), repeats=num_technical_replicates[plate])
            local_cond=np.random.permutation(local_cond)
            
            for condition in range(num_conditions):
                ranks[condition,j]=technical_replicates_key(np.where(local_cond==condition)[0]+1) if condition in local_cond else -1
            
            ranks[np.where(ranks[:,j]<0),j]=curr_num
            ranks[:,j]/=curr_num
            
        return np.prod(ranks, axis=1, dtype=float)
        
        
        