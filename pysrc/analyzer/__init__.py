import os, sys, pdb
import numpy as np
import cPickle as pickle

cecog_features = ['ch_acd',
                 'ch_area_ratio',
                 'ch_cc',
                 'ch_max_val_0',
                 'ch_max_val_1',
                 'ch_max_val_2',
                 'ch_mean_area',
                 'ch_rugosity',
                 'ch_thresh_cc',
                 'ch_variance_area',
                 'circularity',
                 'dist_max',
                 'dist_min',
                 'dist_ratio',
                 'dyn_distance_nb_max',
                 'dyn_distance_radius_0',
                 'dyn_distance_radius_1',
                 'dyn_distance_radius_2',
                 'dyn_distance_radius_3',
                 'eccentricity',
                 'ellip_axis_ratio',
                 'ellip_major_axis',
                 'ellip_minor_axis',
                 'granu_close_area_1',
                 'granu_close_area_2',
                 'granu_close_area_3',
                 'granu_close_area_5',
                 'granu_close_area_7',
                 'granu_close_volume_1',
                 'granu_close_volume_2',
                 'granu_close_volume_3',
                 'granu_close_volume_5',
                 'granu_close_volume_7',
                 'granu_open_area_1',
                 'granu_open_area_2',
                 'granu_open_area_3',
                 'granu_open_area_5',
                 'granu_open_area_7',
                 'granu_open_volume_1',
                 'granu_open_volume_2',
                 'granu_open_volume_3',
                 'granu_open_volume_5',
                 'granu_open_volume_7',
                 'gyration_radius',
                 'gyration_ratio',
                 'h1_2ASM',
                 'h1_2CON',
                 'h1_2COR',
                 'h1_2COV',
                 'h1_2DAV',
                 'h1_2ENT',
                 'h1_2IDM',
                 'h1_2PRO',
                 'h1_2SAV',
                 'h1_2SET',
                 'h1_2SHA',
                 'h1_2SVA',
                 'h1_2VAR',
                 'h1_2average',
                 'h1_2variance',
                 'h1_ASM',
                 'h1_CON',
                 'h1_COR',
                 'h1_COV',
                 'h1_DAV',
                 'h1_ENT',
                 'h1_IDM',
                 'h1_PRO',
                 'h1_SAV',
                 'h1_SET',
                 'h1_SHA',
                 'h1_SVA',
                 'h1_VAR',
                 'h1_average',
                 'h1_variance',
                 'h2_2ASM',
                 'h2_2CON',
                 'h2_2COR',
                 'h2_2COV',
                 'h2_2DAV',
                 'h2_2ENT',
                 'h2_2IDM',
                 'h2_2PRO',
                 'h2_2SAV',
                 'h2_2SET',
                 'h2_2SHA',
                 'h2_2SVA',
                 'h2_2VAR',
                 'h2_2average',
                 'h2_2variance',
                 'h2_ASM',
                 'h2_CON',
                 'h2_COR',
                 'h2_COV',
                 'h2_DAV',
                 'h2_ENT',
                 'h2_IDM',
                 'h2_PRO',
                 'h2_SAV',
                 'h2_SET',
                 'h2_SHA',
                 'h2_SVA',
                 'h2_VAR',
                 'h2_average',
                 'h2_variance',
                 'h4_2ASM',
                 'h4_2CON',
                 'h4_2COR',
                 'h4_2COV',
                 'h4_2DAV',
                 'h4_2ENT',
                 'h4_2IDM',
                 'h4_2PRO',
                 'h4_2SAV',
                 'h4_2SET',
                 'h4_2SHA',
                 'h4_2SVA',
                 'h4_2VAR',
                 'h4_2average',
                 'h4_2variance',
                 'h4_ASM',
                 'h4_CON',
                 'h4_COR',
                 'h4_COV',
                 'h4_DAV',
                 'h4_ENT',
                 'h4_IDM',
                 'h4_PRO',
                 'h4_SAV',
                 'h4_SET',
                 'h4_SHA',
                 'h4_SVA',
                 'h4_VAR',
                 'h4_average',
                 'h4_variance',
                 'h8_2ASM',
                 'h8_2CON',
                 'h8_2COR',
                 'h8_2COV',
                 'h8_2DAV',
                 'h8_2ENT',
                 'h8_2IDM',
                 'h8_2PRO',
                 'h8_2SAV',
                 'h8_2SET',
                 'h8_2SHA',
                 'h8_2SVA',
                 'h8_2VAR',
                 'h8_2average',
                 'h8_2variance',
                 'h8_ASM',
                 'h8_CON',
                 'h8_COR',
                 'h8_COV',
                 'h8_DAV',
                 'h8_ENT',
                 'h8_IDM',
                 'h8_PRO',
                 'h8_SAV',
                 'h8_SET',
                 'h8_SHA',
                 'h8_SVA',
                 'h8_VAR',
                 'h8_average',
                 'h8_variance',
                 'irregularity',
                 'irregularity2',
                 'ls0_CAREA_avg_value',
                 'ls0_CAREA_max_value',
                 'ls0_CAREA_sample_mean',
                 'ls0_CAREA_sample_sd',
                 'ls0_DISP_avg_value',
                 'ls0_DISP_max_value',
                 'ls0_DISP_sample_mean',
                 'ls0_DISP_sample_sd',
                 'ls0_INTERIA_avg_value',
                 'ls0_INTERIA_max_value',
                 'ls0_INTERIA_sample_mean',
                 'ls0_INTERIA_sample_sd',
                 'ls0_IRGL_avg_value',
                 'ls0_IRGL_max_value',
                 'ls0_IRGL_sample_mean',
                 'ls0_IRGL_sample_sd',
                 'ls0_NCA_avg_value',
                 'ls0_NCA_max_value',
                 'ls0_NCA_sample_mean',
                 'ls0_NCA_sample_sd',
                 'ls0_TAREA_avg_value',
                 'ls0_TAREA_max_value',
                 'ls0_TAREA_sample_mean',
                 'ls0_TAREA_sample_sd',
                 'ls1_CAREA_avg_value',
                 'ls1_CAREA_max_value',
                 'ls1_CAREA_sample_mean',
                 'ls1_CAREA_sample_sd',
                 'ls1_DISP_avg_value',
                 'ls1_DISP_max_value',
                 'ls1_DISP_sample_mean',
                 'ls1_DISP_sample_sd',
                 'ls1_INTERIA_avg_value',
                 'ls1_INTERIA_max_value',
                 'ls1_INTERIA_sample_mean',
                 'ls1_INTERIA_sample_sd',
                 'ls1_IRGL_avg_value',
                 'ls1_IRGL_max_value',
                 'ls1_IRGL_sample_mean',
                 'ls1_IRGL_sample_sd',
                 'ls1_NCA_avg_value',
                 'ls1_NCA_max_value',
                 'ls1_NCA_sample_mean',
                 'ls1_NCA_sample_sd',
                 'ls1_TAREA_avg_value',
                 'ls1_TAREA_max_value',
                 'ls1_TAREA_sample_mean',
                 'ls1_TAREA_sample_sd',
                 'moment_I1',
                 'moment_I2',
                 'moment_I3',
                 'moment_I4',
                 'moment_I5',
                 'moment_I6',
                 'moment_I7',
                 'n2_avg',
                 'n2_stddev',
                 'n2_wavg',
                 'n2_wdist',
                 'n2_wiavg',
                 'n_avg',
                 'n_stddev',
                 'n_wavg',
                 'n_wdist',
                 'n_wiavg',
                 'perimeter',
                 'princ_gyration_ratio',
                 'princ_gyration_x',
                 'princ_gyration_y',
                 'roisize',
                 'skewness_x',
                 'skewness_y']