import os, pdb, datetime
from warnings import warn
from collections import defaultdict
import numpy as np
from collections import Counter
#ATTENTION ICI ON A UN PROBLEME D'IMPORT SI ON REGARDE CA DEPUIS FIJI POUR FAIRE L'EXTRACTION DES IMAGES. MAIS BON CA TOMBE BIEN ON VEUT PLUS TROP L'UTILISER
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from plates.models import Plate,Cond, Treatment, Well
from analyzer import CONTROLS
WELL_PARAMETERS = ['Name', 'Medium', 'Serum', 'Xenobiotic', 'Dose']

def readPlateSetting(plateL, confDir, startAtZero = False,
                     plateName=None, dateFormat='%d%m%y', defaultMedium = "Complet",
                     addPlateWellsToDB=False):
    '''
    Function to go from csv file describing plate setup to a dictionary
    
    The csv file should not contain spaces in the cells
    '''
    
    
    result = {}
    idL = {}
    well_lines=defaultdict(dict)
    for plate in plateL:
        result[plate]={}         
        idL[plate]={}
        filename = os.path.join(confDir, "%s.csv" % plate)
        try:
            f=open(filename)
            lines=f.readlines(); f.close()
        except IOError:
            r, currWell_lines, iL= readNewPlateSetting([plate], confDir, startAtZero,
                     plateName=plateName, dateFormat=dateFormat,
                     addPlateWellsToDB=addPlateWellsToDB)
            result.update(r)
            idL.update(iL)
            well_lines.update(currWell_lines)
        else:  
            lines=[line.strip("\n").split("\\") for line in lines]
            
            #loading experiment parameters

            try:
                a=int(lines[0][11])
            except:
                try:
                    a = int(lines[0][7])
                except:
                    raise AttributeError("Can't find the number of rows")
                else:
                    nb_col=8
            else:
                nb_col=12

            nb_row = len(lines)-1 #dire le nb de lignes dans le fichier - mais en fait on a toujours huit colonnes
            
            if addPlateWellsToDB:
                p = Plate(name = plateName, date = datetime.datetime.strptime(plate, dateFormat), nb_col=nb_col, nb_row=nb_row)
                p.save()
            
            params=lines[0][nb_col:]
            k=0 if startAtZero else 1
    
            for line in lines[1:nb_row+1]:
                for el in line[:nb_col]:
                    
                    result[plate][k]={'Name': el}
                    for i,param in enumerate(params):
                        result[plate][k][param]=line[nb_col+i]
                        
                        
                    if addPlateWellsToDB:
                        try:
                            medium = result[plate][k]['Medium']
                        except KeyError:
                            medium=defaultMedium
                        try:
                            serum = int(result[plate][k]['Serum'])
                        except KeyError:
                            serum = None
                        
                        conds = Cond.objects.filter(medium = medium)
                        if len(conds)==0:
                            cond = addConds(medium, serum) 
                        elif len(conds)==1:
                            if conds[0].serum!=serum:
                                cond =addConds(medium, serum)
                            else:
                                cond = conds[0]
                        else:
                            conds = conds.filter(serum =serum)
                            if len(conds)==0:
                                cond =addConds(medium, serum)
                            elif len(conds)>1:
                                raise
                            else:
                                cond = conds[0]
    
                    if addPlateWellsToDB and 'Xenobiotic' in params:
                        xb = result[plate][k]['Xenobiotic']
                        dose = int(result[plate][k]['Dose'])
                        
                        treatments = Treatment.objects.filter(xb = xb)
                        if len(treatments)==0:
                            treatment = addTreatment(xb, dose)
                        elif len(treatments)==1:
                            if treatments[0].dose != dose:
                                treatment = addTreatment(xb, dose)
                            else:
                                treatment =treatments[0]
                        else:
                            treatments = treatments.filter(dose =dose)
                            if len(treatments)==0:
                                treatment = addTreatment(xb, dose)
                            elif len(treatments)>1:
                                raise
                            else:
                                treatment =treatments[0]
                            
                    if addPlateWellsToDB:
                        try:
                            clone = result[plate][k]['Name'].split("_")[0]
                        except:
                            clone = None
                        w=Well(num=k, plate=p, treatment = treatment, clone = clone)
                        w.save()
                #this is how to add many to many relations
                        w.cond.add(cond); w.save()
                        idL[plate][k]=w.id
                    k+=1
    if addPlateWellsToDB:
        return result, WELL_PARAMETERS, well_lines, idL
    else:
        return result, WELL_PARAMETERS
    
def fromXBToWells(xbL,confDir='/media/lalil0u/New/projects/Xb_screen/protocols_etal/plate_setups',
                   dose_filter=None, plate=None):
    '''
    Getting information for which treatments are where in the data base
    confDir is the folder where the plate setups are
    dose_filter can be one dose (type int) or a list of int, or None in which case all doses are considered from 1 to 10
    '''
    plateL=[]; well_lines_dict = {}; result={}
    #in the db the well numbers are recalculated: each well, even the empty ones, have a number.
    for xb in xbL:
        if plate is None:
            result[xb]=Well.objects.filter(treatment__xb=xb, plate__date__gt=datetime.date(2014,11,10))
        else:
            p=datetime.date(2000+int(plate[-2:]), int(plate[2:4]), int(plate[:2]))
            result[xb]=Well.objects.filter(treatment__xb=xb, plate__date=p)
            
        if dose_filter is not None:
            if type(dose_filter)!=list:
                result[xb]={dose_filter :np.array([(el.plate.cosydate(), el.num) for el in result[xb].filter(treatment__dose=dose_filter)])}
                try:
                    plateL=list(result[xb][dose_filter][:,0])
                except IndexError:
                    pass
            else:
                r={xb:{}}
                for dose in dose_filter:
                    r[xb][dose]=np.array([(el.plate.cosydate(), el.num) for el in result[xb].filter(treatment__dose=dose)])
                    try:
                        plateL.extend(list(r[xb][dose][:,0]))
                    except IndexError:
                        pass
                result[xb]=r[xb]
        else:
            dose_filter = list(range(16))
            return fromXBToWells(xbL, confDir, dose_filter, plate)

    plateL=Counter(plateL).keys()
    
    #so now we need to recalculate the well numbers according to hdf5 and Zeiss numbering
    for plate in plateL:
        #getting where the existing wells are
        try:
            file_ =open(os.path.join(confDir,  "%s_Wells.csv" % plate))
            well_lines = file_.readlines(); file_.close()
        except OSError:
            nb_col = 12; nb_row=8
            well_lines = np.reshape(range(1,97),(8,12))
        else:
            well_lines=np.array([line.strip("\n").split(",") for line in well_lines[1:]], dtype=int)
            print well_lines
            well_lines_dict[plate]= {i+1:well_lines.ravel()[i] for i in range(well_lines.size)}
            
    r2={}; r1=defaultdict(dict)
    for xb in result:
        r2[xb]={}
        for dose in filter(lambda x: result[xb][x].shape[0]>0, result[xb]):
            r2[xb][dose]=[(plate, '{:>05}'.format( well_lines_dict[plate][int(num)])) for plate,num in result[xb][dose]]
            
            r1[xb][dose]=defaultdict(list)
            for plate, num in result[xb][dose]:
                r1[xb][dose][plate].append(well_lines_dict[plate][int(num)])
        
    return r2,r1
    
    
    
def readNewPlateSetting(plateL, confDir, startAtZero = False,
                     plateName=None, dateFormat='%d%m%y', 
                     default={'Name':"Cl1", 'Medium': "Indtp", "Serum":10},
                     addPlateWellsToDB=False):
    '''
    Function to go from as many csv files as there are parameters describing plate setup, to a dictionary
    
    The csv file should not contain spaces in the cells
    
    The file 'wells' should contain the information on where physically on the plate the wells with the numbers
    are located. The numbers are the numbers as the images are saved.
    '''
    result = defaultdict(dict)
    idL = {}
    well_lines_dict = {}
    for plate in plateL:
        result[plate]={}         
        idL[plate]={}
        #getting where the existing wells are
        try:
            file_ =open(os.path.join(confDir,  "%s_Wells.csv" % plate))
            well_lines = file_.readlines(); file_.close()
        except OSError:
            nb_col = 12; nb_row=8
            well_lines = np.reshape(range(1,97),(8,12))
        else:
            well_lines=np.array([line.strip("\n").split(",") for line in well_lines[1:]], dtype=int)
            print well_lines
            well_lines_dict[plate]=well_lines
            
            try:
                a=int(well_lines[0][11])
            except:
                try:
                    a = int(well_lines[0][7])
                except:
                    raise AttributeError("Can't find the number of rows")
                else:
                    nb_col=8
            else:
                nb_col=12
            nb_row = len(well_lines) #dire le nb de lignes dans le fichier - mais en fait on a toujours huit colonnes

#        #opening file with well names (clone name usually)
#        filename = os.path.join(confDir, "%s_Name.csv" % plate)
#        
#        f=open(filename)
#        lines=f.readlines(); f.close()
#        
#        lines=np.array([line.strip("\n").split(",") for line in lines][1:]).ravel()
#        lines = np.delete(lines, np.where(lines==''))
        
        if addPlateWellsToDB:
            p = Plate(name = plateName, date = datetime.datetime.strptime(plate.split('_')[0], dateFormat), nb_col=nb_col, nb_row=nb_row)
            p.save()
        
        current_parameters = defaultdict(list)
        for parameter in WELL_PARAMETERS:
            print 'Loading %s parameter'%parameter
            try:
                f=open(os.path.join(confDir, "%s_%s.csv" % (plate, parameter)))
                current_lines=f.readlines()[1:]; f.close()
            except IOError:
                pass
            else:
                current_parameters[parameter]=np.array([line.strip("\n").split(",") for line in current_lines]).ravel()
                current_parameters[parameter] = np.delete(current_parameters[parameter], 
                                        np.where(current_parameters[parameter]==''))
        for k in well_lines.ravel():
            result[plate][k]=defaultdict(dict)
            for i,param in enumerate(WELL_PARAMETERS):
                try:
                    result[plate][k][param]=current_parameters[param][k-1]
                except IndexError:
                    result[plate][k][param]=default[param]
            if addPlateWellsToDB:
                medium = result[plate][k]['Medium']
                serum = int(result[plate][k]['Serum'])
                
                conds = Cond.objects.filter(medium = medium)
                if len(conds)==0:
                    cond = addConds(medium, serum) 
                elif len(conds)==1:
                    if conds[0].serum!=serum:
                        cond =addConds(medium, serum)
                    else:
                        cond = conds[0]
                else:
                    conds = conds.filter(serum =serum)
                    if len(conds)==0:
                        cond =addConds(medium, serum)
                    elif len(conds)>1:
                        raise
                    else:
                        cond = conds[0]

            if addPlateWellsToDB and 'Xenobiotic' in WELL_PARAMETERS:
                xb = result[plate][k]['Xenobiotic']
                dose = int(result[plate][k]['Dose'])
                
                treatments = Treatment.objects.filter(xb = xb)
                if len(treatments)==0:
                    treatment = addTreatment(xb, dose)
                elif len(treatments)==1:
                    if treatments[0].dose != dose:
                        treatment = addTreatment(xb, dose)
                    else:
                        treatment =treatments[0]
                else:
                    treatments = treatments.filter(dose =dose)
                    if len(treatments)==0:
                        treatment = addTreatment(xb, dose)
                    elif len(treatments)>1:
                        raise
                    else:
                        treatment =treatments[0]
                    
            if addPlateWellsToDB:
                clone = result[plate][k]['Name'].split("_")[0]
                w=Well(num=k, plate=p, treatment = treatment, clone = clone)
                w.save()
        #this is how to add many to many relations
                w.cond.add(cond); w.save()
                idL[plate][k]=w.id
                
    if addPlateWellsToDB:
        return result, well_lines_dict, idL
    else:
        return result, {}

def addConds(medium, serum):
    cond = Cond(medium = medium, serum = serum)
    cond.save()
    return cond

def addTreatment(xb, dose):
    is_ctrl = xb in CONTROLS.values()
    c=None
    if not is_ctrl:
        if xb not in CONTROLS:
            warn('This xenobiotic {} has no control defined yet.'.format(xb))
        else:
            controls = Treatment.objects.filter(xb = CONTROLS[xb])#.get(dose =dose)
            if len(controls)==0:
                c=addTreatment(CONTROLS[xb], dose)
            elif len(controls)==1:
                if controls[0].dose==dose:
                    c=controls[0]
                else:
                    c=addTreatment(CONTROLS[xb], dose)
            else:
                controls = controls.filter(dose=dose)
                if len(controls)==0:
                    c=addTreatment(CONTROLS[xb], dose)
                elif len(controls)>1:
                    raise
                else:
                    c=controls[0]
        
    treatment = Treatment(xb=xb, dose = dose, is_ctrl = is_ctrl, ctrl = c)
    treatment.save()
    return treatment


