from tracking.trajPack import featuresNumeriques

#settings for aschoenauer@cbio


batch_size = 15000
init_size = 15000
#number of histogram features
num_features = 16
#number of numerical features
nb_feat_num = 0
n_init = 10
init = 'k-means++'
#folder for trajectory features data
data_folder = '/share/data20T/mitocheck/tracking_results'

#folder for output data
result_folder = '../resultData/experiment_clustering'
filename = "expClus_iter{}.pkl"

mitocheck_file = '../data/mitocheck_siRNAs_target_genes_Ens72.txt'

quality_control_file = '../data/qc_export.txt'

#fraction on which to check clustering stability
fraction = 0.8
num_iterations_stability = 20

#number of clusters to try
k_min = 4
k_max = 5

#number of trajectories to represent a cluster
n_representatives = 10

#list to take into account or not pca, and whitening
pcaParameters = [(0,0)]
#pcaParameters = [(0,0), (1,0), (1,1)]
#number of principal components that are retained to get approx 92% of the variance
nb_composantes = 6

#Fisher test or Kolmogorv-Smirnov ?
Fisher = True

#do you want to calculate all p-values from all parameter sets even if they have already been calculated?
redo = False