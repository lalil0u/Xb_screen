#VARS FOR DRUG SCREEN PROJECT
import getpass
import cPickle as pickle
from collections import Counter

couleurs=['green', 'red', 'yellow', 'blue', 'purple', 'orange', 'black', 'cyan']
couleurs.append("#9e0142")
couleurs.append("#5e4fa2")
DRUGS=['Acyclovir',
     'Adenosine3',
     'Aminopurine6benzyl',
     'Anisomycin',
     'Azacytidine5',
     'Camptothecine(S,+)',
     'Daunorubicinhydrochloride',
     'Dexamethasoneacetate',
     'Doxorubicinhydrochloride',
     'Epiandrosterone',
     'Etoposide',
     'Hesperidin',
     'Idoxuridine',
     'JNJ7706621',
     'MLN8054',
     'Methotrexate',
     'Nocodazole',
     'Paclitaxel',
     'R763',
     'Ribavirin',
     'Sulfaguanidine',
     'Sulfathiazole',
     'Thalidomide',
     'VX680',
     'Zidovudine,AZT']

CLASSES=['Interphase',
     'Large',
     'Elongated',
     'Binucleated',
     'Polylobed',
     'Grape',
     'Metaphase',
     'Anaphase',
     'MetaphaseAlignment',
     'Prometaphase',
     'ADCCM',
     'Apoptosis',
     'Hole',
     'Folded',
     'SmallIrregular']

KNOWN_TARGETS = {'Anisomycin': ['RPL10L', 'RPL13A', 'RPL23',  'RPL15',
                          'RPL19','RPL23A','RSL24D1','RPL26L1','RPL8','RPL37','RPL3','RPL11','NHP2L1'],
           'Azacytidine5':['DNMT1'],
           'Camptothecine(S,+)':['TOP1'],
            'Daunorubicinhydrochloride':['TOP2A', 'TOP2B'],
            'Doxorubicinhydrochloride':['TOP2A', 'TOP2B'],
           'Etoposide':['TOP2A', 'TOP2B'],
           'JNJ7706621' : ['AURKA', 'AURKB', 'CDK1', 'CDK2', 'CDK3', 'CDK4', 'CDK6'],
           'MLN8054':['AURKA'],
           'Nocodazole':['HPGDS', 
                         'TUBB2A',
                        'TUBB4A',
                        'TUBB4B',
                        'TUBB6',],
           'Paclitaxel':['TUBB1', 'BCL2','NR1I2','MAPT','MAP4','MAP2'],
           'VX680':['AURKA', 'AURKB'],
           'R763':['AURKA', 'AURKB', 'FLT3', 'VEGFR2']
           }
DISTANCES = {'N_pheno_score':'Normalized\n phenotypic score distance',
 'nature':'Phenotypic\n trajectory distance',
 'ttransport_MAX':'Max time \n Sinkhorn div.',
 'U_pheno_score':'Phenotypic score distance',
 'ttransport_INT':'Sum of time\n Sinkhorn div.',
 'transport':'Global\n Sinkhorn div.'}

if getpass.getuser()=='lalil0u':
    f=open('/mnt/projects/drug_screen/results/DS_pheno_scores.pkl')
    _,_,_, exposure_=pickle.load(f); f.close()
    PASSED_QC_COND=Counter(exposure_)

right_hit_cond_order = [('Anisomycin', 1),
                         ('Anisomycin', 2),
                         ('Anisomycin', 3),
                         ('Anisomycin', 4),
                         ('Anisomycin', 5),
                         ('Anisomycin', 6),
                         ('Anisomycin', 7),
                         ('Anisomycin', 8),
                         ('Anisomycin', 10),
                         ('Azacytidine5', 8),
                         ('Azacytidine5', 9),
                         ('Azacytidine5', 10),
                         ('Camptothecine(S,+)', 0),
                         ('Camptothecine(S,+)', 1),
                         ('Camptothecine(S,+)', 2),
                         ('Camptothecine(S,+)', 3),
                         ('Camptothecine(S,+)', 4),
                         ('Camptothecine(S,+)', 5),
                         ('Camptothecine(S,+)', 6),
                         ('Camptothecine(S,+)', 7),
                         ('Camptothecine(S,+)', 8),
                         ('Camptothecine(S,+)', 9),
                         ('Camptothecine(S,+)', 10),
                         ('Daunorubicinhydrochloride', 0),
                         ('Daunorubicinhydrochloride', 1),
                         ('Daunorubicinhydrochloride', 2),
                         ('Daunorubicinhydrochloride', 3),
                         ('Daunorubicinhydrochloride', 4),
                         ('Daunorubicinhydrochloride', 5),
                         ('Daunorubicinhydrochloride', 6),
                         ('Daunorubicinhydrochloride', 7),
                         ('Doxorubicinhydrochloride', 1),
                         ('Doxorubicinhydrochloride', 2),
                         ('Doxorubicinhydrochloride', 3),
                         ('Doxorubicinhydrochloride', 4),
                         ('Doxorubicinhydrochloride', 5),
                         ('Doxorubicinhydrochloride', 6),
                         ('Doxorubicinhydrochloride', 7),
                         ('Doxorubicinhydrochloride', 8),
                         ('Etoposide', 4),
                         ('Etoposide', 5),
                         ('Etoposide', 6),
                         ('Etoposide', 7),
                         ('Etoposide', 8),
                         ('Etoposide', 9),
                         ('Etoposide', 10),
                         ('JNJ7706621', 8),
                         ('JNJ7706621', 9),
                         ('JNJ7706621', 10),
                         ('MLN8054', 9),
                         ('MLN8054', 10),
                         ('R763', 10),
                         ('VX680', 6),
                         ('VX680', 7),
                         ('VX680', 8),
                         ('VX680', 9),
                         ('VX680', 10),
                         ('Nocodazole', 6),
                         ('Nocodazole', 7),
                         ('Nocodazole', 8),
                         ('Nocodazole', 9),
                         ('Nocodazole', 10),
                         ('Paclitaxel', 3),
                         ('Paclitaxel', 4),
                         ('Paclitaxel', 5),
                         ('Paclitaxel', 6),
                         ('Paclitaxel', 7),
                         ('Paclitaxel', 8),
                         ('Paclitaxel', 9),
                         ('Paclitaxel', 10)]

CHOSEN_CONDITION_GROUPS = [
                           [('Nocodazole', range(8, 11))],
                           [('Paclitaxel', range(5,10))],
                           [('VX680', range(7, 11)), ('MLN8054', [10])],
                           [('Anisomycin', range(5, 9))],
                           [('Camptothecine(S,+)', range(6, 11))]
                           ]