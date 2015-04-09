import os, sys
import numpy as np
import cPickle as pickle
from collections import defaultdict
from optparse import OptionParser

from util.settings import Settings
from tracking.trajPack.thrivision import thrivisionExtraction
from vigra import impex as vi
from util.listFileManagement import correct_from_Nan


#to do jobs launch thrivision.scriptThrivision(exp_list, baseName='pheno_seq', command="phenotypes/phenotype_seq.py")

class pheno_seq_extractor(thrivisionExtraction):
    def __init__(self, setting_file, plate, well):
        super(pheno_seq_extractor, self).__init__(setting_file, plate, well)
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
            assert self._usable()
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
    
    
if __name__ == '__main__':
    verbose=0
    description =\
'''
%prog - Computing phenotype sequences given tracklets
Input:
- plate, well: experiment of interest
- settings file

'''
    #Surreal: apparently I need to do this because I changed the architecture of my code between the computation of the trajectories and now that I need to reopen the files
    from tracking import PyPack
    sys.modules['PyPack.fHacktrack2']=PyPack.fHacktrack2
    parser = OptionParser(usage="usage: %prog [options]",
                         description=description)
    
    parser.add_option("-f", "--settings_file", dest="settings_file", default='phenotypes/settings/settings_pheno_seq.py',
                      help="Settings_file")

    parser.add_option("-p", "--plate", dest="plate",
                      help="The plate which you are interested in")
    
    parser.add_option("-w", "--well", dest="well",
                      help="The well which you are interested in")


    
    (options, args) = parser.parse_args()
    
    p=pheno_seq_extractor(options.settings_file, options.plate, options.well)
    p()
    print "Done"
        
        