#IMPORT
import pdb, os, time, sys
import numpy as np
import cPickle as pickle
from optparse import OptionParser
import matplotlib
from tracking.PyPack.fHacktrack2 import trajectoire, ensTraj
import getpass
matplotlib.use('Agg')

from tracking.importPack import FEATURE_NUMBER
from tracking.test import gettingRaw, j
from tracking.dataPack import treatments
from tracking.trajPack import densities, time_windows
from trajFeatures import trackletBuilder, histogramPreparationFromTracklets
from tracking.trackingF import sousProcessClassify
from util import settings

'''
    To perform trajectory extraction and trajectory feature extraction on a cluster node.
    Relevant information should be passed on the command line, cf infra
'''

    
def gettingSolu(plate, w, loadingFolder, dataFolder, outputFolder, training = False, first=True, new_cecog_files=False, intensity_qc_dict=None,
                separating_function=None):
    global FEATURE_NUMBER
    
    tabF = None
    #tableau qui contiendra toutes les features de tlm pr voir lesquelles contiennent des NaN

    fichier = open(os.path.join(loadingFolder,"featuresToDelete.pkl"), 'r')
    f = pickle.load(fichier)
    fichier.close()
    newFrameLot = None
    listP = os.listdir(dataFolder)
    if w is not None:
        listP = [w] 
    for well in listP:
        filename = os.path.join(dataFolder, well)
        name_primary_channel='primary__primary' if not new_cecog_files else 'primary__primary3'
        
        well=well.split('.')[0]    
        if training:
            filenameT = '/media/lalil0u/New/workspace2/Tracking/data/trainingset/PL'+plate+"___P"+well+"___T00000.xml"
        else:
            filenameT = None
            
        if intensity_qc_dict is not None and int(well) in intensity_qc_dict and intensity_qc_dict[int(well)].shape[0]>0:
            frames_to_skip=intensity_qc_dict[int(well)]
            for el in frames_to_skip:
                if el+1 in frames_to_skip:
                    ind=np.where(frames_to_skip==el)
                    print "Issue with {}, {} in frames_to_skip".format(el, el+1)
                    pdb.set_trace()
                    #frames_to_skip=np.delete(frames_to_skip, [ind, ind+1])
        else:
            frames_to_skip=None
        
        frameLotC, tabFC = gettingRaw(filename, filenameT, plate, well, name_primary_channel=name_primary_channel, frames_to_skip=frames_to_skip, 
                                      separating_function=separating_function)
        if newFrameLot == None:
            newFrameLot = frameLotC 
        else: newFrameLot.addFrameLot(frameLotC)
        tabF = tabFC if tabF == None else np.vstack((tabF, tabFC))
    
    #en ce qui concerne le nettoyage des NaN
    c, f2 = treatments.whichAreNan(tabF)
    #print len(f2.keys()), len(f)
    #if there are features with NaN entries in the predict data but not in the training data
    toZeros = filter(lambda x: x not in f, f2.keys())
    if toZeros !=[]:
        sys.stderr.write("Attention attention, plate {}, some features here have NaN entries, and this was not the case in the training set. They are put to 0".format(plate))
        newFrameLot.zeros(toZeros)

    newFrameLot.clean(f) ##np.delete(X, f, 1)
    if first:
        FEATURE_NUMBER -=len(f)
   
    #ICI ON RECUPERE DONC LES SINGLETS ET DOUBLETS AVEC LA VALEUR DU TRAINING DANS CELL.TO SI ILS Y SONT, NONE SINON
    #POUR LE CENTRE ET LES FEATURES C'EST LA MOYENNE DES OBJETS DU SINGLET
    if training == False:
        singlets, doublets = newFrameLot.getAllUplets(outputFolder)
    else:
        singlets, doublets = newFrameLot.getTrainingUplets(outputFolder)
   # print "TIME TIME TIME after getting all uplets", time.clock()
    print "joining uplets now"

    solutions = j(singlets, doublets, FEATURE_NUMBER, training)
    #print "TIME TIME TIME after joining", time.clock()
    print "normalization"
    
    fichier = open(os.path.join(loadingFolder,"minMax_data_all.pkl"), "r")  
    minMax = pickle.load(fichier)
    fichier.close()
    try:
        solutions.normalisation(minMax)
    except AttributeError:
        sys.stderr.write('No tracking hypotheses could be computed for this video. It is very likely that there is only one frame.')
        sys.exit()
    #print "TIME TIME TIME after normalization", time.clock()
    
    return solutions

def output(plate,  well, allDataFolder, outputFolder, training_only=True, new_cecog_files= False,
           separating_function=None):
    #listD = os.listdir('/media/lalil0u/New/workspace2/Tracking/data/raw')
    first = True; 
    dataFolder = os.path.join(allDataFolder, plate, 'hdf5')
    loadingFolder = "../prediction"
    if 'LT' in plate:
        intensity_qc_dict=None
    else:
        w=int(well.split('_')[0])
        print "Loading manual and out of focus qc files"
        f=open('../data/xb_manual_qc.pkl', 'r')
        d1=pickle.load(f); f.close()
        if plate in d1 and w in d1[plate]:
            print "This well failed the manual quality control."
            return
        f=open('../data/xb_focus_qc.pkl', 'r')
        d2=pickle.load(f); f.close()
        if plate in d2 and w in d2[plate]:
            print "This well failed the focus/cell count quality control."
            return
        
        print 'Loading intensity qc file'
        intensity_qc_file=open('../data/xb_intensity_qc.pkl', 'r')
        intensity_qc_dict=pickle.load(intensity_qc_file); intensity_qc_file.close()    
        intensity_qc_dict=intensity_qc_dict[plate] if plate in intensity_qc_dict else None
        
    tSol=gettingSolu(plate, well, loadingFolder, dataFolder, outputFolder, training_only, first, new_cecog_files = new_cecog_files, intensity_qc_dict=intensity_qc_dict,
                     separating_function=separating_function)
    first=False
    new_sol = sousProcessClassify(tSol, loadingFolder)
    print "Building trajectories for predicted data"
    dicTraj, conn, movie_length =trackletBuilder(new_sol, outputFolder, training=False)
##        del new_sol;del tSol;
    return dicTraj, conn, movie_length

if __name__ == '__main__':
    verbose=0
    description =\
'''
%prog - Parallel cell tracking
Performs trajectory extraction and trajectory feature extraction on data as contained in hdf5 files produced by 
CellCognition.

Input:
- plate, well: experiment of interest
- dataFolder: folder containing hdf5 files
- choice: if the goal is to extract trajectories or trajectory features
- name: generic filename for trajectory features
- repeat: if existing files should be overwritten

Note: there is a strange thing with the way iPython parses options. If you say
>>>ww="00020_01.hdf5"
>>>%run tracking/trajPack/parallel_trajFeatures -p 271114 -w $ww -d /media/lalil0u/New/projects/Xb_screen/plates__all_features_2 -c 1 --ff 0 -n features_intQC_{}.pkl
THEN it doesn't replace the first $ww with

'''
    initTime=time.clock()
    parser = OptionParser(usage="usage: %prog [options]",
                         description=description)
    
    parser.add_option("-f", "--settings_file", dest="settings_file", default='tracking/settings/settings_trajFeatures.py',
                      help="Settings_file")

    parser.add_option("-p", "--plate", dest="plate",
                      help="The plate which you are interested in")
    
    parser.add_option("-w", "--well", dest="well",
                      help="The well which you are interested in")

    parser.add_option("-t", "--time_window", dest="time_window", default=None, type=int,
                      help="Choose time window index in settings file list")
    
    parser.add_option("-c", "--choice", dest="choice", default = False, 
                      help="False to build trajectories and true to compute features from existing trajectories")

    parser.add_option("-s", "--simulated", dest="simulated", default = 0, type=int, 
                      help="Use of simulated trajectories or no")
    parser.add_option("--cecog_file", dest="cecog_file", default = False, type=int, 
                       help="True for new type, False for old")    
#     parser.add_option("-r", "--repeat", dest="repeat", default = False, 
#                       help="False to do only videos that haven't been treated yet and true to compute features even if already computed")
#     
#     parser.add_option("--ff", type=int, dest="filtering_fusion", default = 1, 
#                       help="False to take into account all tracklets, even those resulting from a fusion")
    
    (options, args) = parser.parse_args()
    
    if options.well==None:
        print "You need to specify which well to treat. Pgm exiting"
        sys.exit()
    if type(options.choice)!=bool: options.choice=int(options.choice)
    
    settings = settings.Settings(options.settings_file, globals())
    outputFolder = os.path.join(settings.outputFolder, options.plate)
    fi=settings.traj_filename.format(options.well)
    
    if options.time_window is not None:
        fi_trajfeatures = settings.feature_filename.format(options.well[:-5], options.time_window)
        time_window=time_windows[options.time_window]
    else:
        fi_trajfeatures = settings.feature_filename.format(options.well[:-5],'N')
        time_window=None
        
    if options.simulated:
        training=True
        outputFolder = os.path.join('../resultData/simulated_traj/simres/plates', options.plate)
        fi='{}--{}.pickle'.format(options.plate, options.well)
    
    try:
        os.mkdir(outputFolder)
    except OSError:
        print "Folder ", outputFolder, 'already created'
    
    if not settings.repeat:
        if not options.choice and fi in os.listdir(outputFolder):
            print "Trajectories already generated"
            sys.exit()
        elif options.choice and fi_trajfeatures in os.listdir(outputFolder):
            print "Trajectories features already calculated"
            sys.exit()
    
    print options.cecog_file
    if not options.choice: 
        print '### \n # \n ###\n We are going to predict trajectories for plate {}, well {}'.format(options.plate, options.well)
        print 'Densities distance ', densities
#FOR PREDICTED DATA
        d, c, movie_length=output(options.plate,options.well, settings.dataFolder,outputFolder, settings.training, 
                                  new_cecog_files=bool(options.cecog_file), separating_function=settings.separating_function) 

        if d is not None:
            #saving results
            
            f=open(os.path.join(outputFolder, fi), 'w')
            pickle.dump(dict(zip(['tracklets dictionary', 'connexions between tracklets', 'movie_length'], [d, c, movie_length])), f)
            f.close()
    #    pickle.dump(dict(zip(['tracklets dictionary', 'connexions between tracklets', 'tracklets features', 'tracklets coordinates'], 
    #                         [d, c, features, coordonnees])), f); f.close()
        else:
            sys.stderr.write('No output for plate {}, well {}'.format(options.plate, options.well))
    else:
        print "### \n # \n ###\n  We are going to compute features from existing trajectories for plate {}\n Adding density information".format(options.plate)
        try:
            filename = os.path.join(outputFolder, fi); print filename
            f=open(filename, 'r')
            dataDict = pickle.load(f)
            f.close()
        except:
            sys.stderr.write('Folder {} does not contain densities trajectories file.'.format(outputFolder))
            sys.exit()
                    
        else:
            if not options.simulated:
                d,c, movie_length = dataDict['tracklets dictionary'], dataDict['connexions between tracklets'], dataDict['movie_length']
                res = histogramPreparationFromTracklets(d, c, outputFolder, False, verbose, movie_length, name=fi_trajfeatures,
                                                        filtering_fusion=settings.filtering_fusion,
                                                        time_window=time_window) 
            else:
                d=ensTraj()
                for traj in dataDict:
                    t = trajectoire(1, xi=None, yi=None, frame=None, idC=None, id=1)
                    t.lstPoints = traj
                    d.lstTraj.append(t)
                res=histogramPreparationFromTracklets({options.plate : {options.well : d}}, None, 
                                                      outputFolder,training =True, verbose=verbose, movie_length={options.plate : {options.well :99}}, 
                                                      name=fi_trajfeatures)  #(d,c, outputFolder, False, verbose, tab=True, length=movie_length)
    
    final = time.clock() - initTime
    print "##################TEMPS FINAL {}".format(final)
    
    
    
    
