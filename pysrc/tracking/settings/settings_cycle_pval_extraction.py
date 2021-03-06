result_folder = '../resultData/cell_cycle'
outputFile = 'incomp_length_5CtrlC_{}.pkl'
ctrl_exp_filename = 'ctrl_exp_{}.pkl'
data_folder = '/share/data20T/mitocheck/tracking_results'
mitocheck_file = '/cbio/donnees/aschoenauer/workspace2/Xb_screen/data/mitocheck_siRNAs_target_genes_Ens75.txt'
quality_control_file = '/cbio/donnees/aschoenauer/workspace2/Xb_screen/data/qc_export.txt'

##filename for trajectory features
inputFile="cell_cycle_cens_{}.pkl"
min_size=10 #minimum number of complete tracks to take the experiment into account

##filename format for the wells
#format_='{:>05}_01'

#Option to say that we're only dealing with numerical features for the moment
histDataAsWell=False

#Option to say if we want to redo experiments anyway
redo=True
#to tell it's not the xb screen
xb_screen=False