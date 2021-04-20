#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

import re
import PyGnuplot as pg
from Globals import *
from collections import OrderedDict
from collections import Counter
import os
import fnmatch
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import shutil
import statistics

SOUBORU_CELKEM = 0
BEZ_POSKOZENI = 0
ITERACI = 0


# Počítá kolik souborů se nedekomprimovalo při určitém poškození
def agreguj_data_nedekomprimovatelnych_souboru( input_file, output_file ):
    ''' Počítá kolik souborů se nedekomprimovalo při určitém poškození '''

    d = dict()
    l = list()

    with open(input_file, "r") as input:
        for line in input:
            l.append(round(float(line),6))

    l.sort(key=float)
    d = Counter(l)

    d = OrderedDict(sorted(d.items()))
    print(d)
    SUM = 0
    max = 1

    with open(output_file, "w") as output:
        for item in d:
            max = int(d[item])

    print("MAX: ", max)
    with open(output_file, "w") as output:
        output.write(str(0.0) + " " + str(0.0) + "\n")
        for item in d:
            pocet_neuspesnych_souboru_v_procentech = round(100 * int(d[item]) /  max , 6)
            output.write(str(item) + " " + str(pocet_neuspesnych_souboru_v_procentech) + "\n")


# agreguje hodnoty v jednom slovniku a vrati ho
def agreguj_slovnik(slovnik, step):

    dictionary = dict()
    #print( 'agreguji jeden slovnik')
    #print(dictionary)

    for i in np.arange(0, 3 + step, step):
        tmp_list = list()
        #print(dict_sop_eph.keys())
        for hash in slovnik.keys():
            #print(hash)
            #print(dict_sop_eph[hash])
            try:
                for key, value in slovnik[hash].items():
                    if round(float(key), 3) > round(i, 3) and round(float(key), 3) < round(i, 3) + step:
                        tmp_list.append(float(value))
            except:
                pass

        # print(tmp_list)
        if len(tmp_list) > 0:
            dictionary[i] = tmp_list

    #print('zpracovavam: ', dictionary)
    for key, value in dictionary.items():
        if len(value) != 0:
            dictionary[ key ] = round( sum(value) / len(value), 3)


    dictionary = sorted(dictionary.items())

    #print('agrergoval jsem jeden slovnik')
    return dictionary

# zapise data z agreovaneho slovniku do vystupniho souboru .agreg
def zapis_agregovana_data(data, filename):
    '''zapise agregovana data do souboru'''
    with open( filename, 'w') as file:
        for record in data:
            file.write( str(record[0]) + " " + str(record[1]) + "\n")

# prumeruje rezii pouzitych kompresnich modu
def prumerna_rezie(data, type):
    '''zapise agregovana data do souboru'''
    #with open( filename, 'w') as file:

    number_of_Records = 0
    sum = 0

    for record in data:
        #file.write( str(record[0]) + " " + str(record[1]) + "\n")
        #print( str(type) + "\t=>\t" + str(record[0]) + " " + str(record[1]) + "\n")
        sum += record[1]
        number_of_Records += 1

    if number_of_Records:
        avg = sum / number_of_Records + 0.18108333333333337 # při použití bypass byl soubor o 0.18108333333333337 menší
        print(str(type) + "\t=>\t" + str(avg) )

# agrefuje data z datových souborů pro každý analyzovaný obraz, PRO MARKERY
def agreguj_data_rezie_markeru( step ):

    pocet_slozek = 0 # počet analyzovanych obrazů, pro každý je vytvořena jedna šložka s datovými soubory
    dict_sop = dict()
    dict_eph = dict()
    dict_sop_eph = dict()
    dict_segmark = dict()
    dict_sop_segmark = dict()
    dict_eph_segmark = dict()
    dict_sop_eph_segmark = dict()


    # ZJISTENI DAT
    for root_d, dirs, files in os.walk(directory_graphs_data):
        for dir_name in dirs:
            #print("Obsah slozky: ", dir_name)
            pocet_slozek += 1
            for root_d, dirs, files_in_dir in os.walk(directory_graphs_data + str(dir_name) + "/"):
                for filename in fnmatch.filter(files_in_dir, '*rezie*'):
                    tmp_dict = dict()
                    # ZJIŠTĚNÍ TYPU SOUBORU A ZÁPIS DO PATŘIČNÉHO SLOVNÍKU
                    if re.search(r"sop", filename):
                        if re.search(r"eph", filename):
                            if re.search(r"segmark", filename):
                                #print("SOP + EPH + SEGMARK: ", filename)
                                with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                                    for line in file:
                                        tmp = line.split()
                                        tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                                    dict_sop_eph_segmark[pocet_slozek] = tmp_dict

                            else:
                                #print("SOP + EPH: ", filename)
                                with open( str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                                    for line in file:
                                        tmp = line.split()
                                        tmp_dict[ str(round( float(tmp[0]), 3)) ] = str(round( float(tmp[1]), 3))
                                    dict_sop_eph[pocet_slozek] = tmp_dict

                        else:
                            if re.search(r"segmark", filename):
                                #print("SOP + SEGMARK: ", filename)
                                with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                                    for line in file:
                                        tmp = line.split()
                                        tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                                    dict_sop_segmark[pocet_slozek] = tmp_dict
                            else:
                                #print("SOP: ", filename)
                                with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                                    for line in file:
                                        tmp = line.split()
                                        tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                                    dict_sop[pocet_slozek] = tmp_dict

                    elif re.search(r"eph", filename):
                        if re.search(r"segmark", filename):
                            #print("EPH + SEGMARK: ", filename)
                            with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                                for line in file:
                                    tmp = line.split()
                                    tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                                dict_eph_segmark[pocet_slozek] = tmp_dict
                        else:
                            #print("EPH: ", filename)
                            with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                                for line in file:
                                    tmp = line.split()
                                    tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                                dict_eph[pocet_slozek] = tmp_dict

                    elif re.search(r"segmark", filename):
                        #print("SEGMARK: ", filename)
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_segmark[pocet_slozek] = tmp_dict

    dict_sop             = agreguj_slovnik( dict_sop, step)
    dict_eph             = agreguj_slovnik( dict_eph, step)
    dict_sop_eph         = agreguj_slovnik( dict_sop_eph, step)
    dict_segmark         = agreguj_slovnik( dict_segmark, step)
    dict_sop_segmark     = agreguj_slovnik( dict_sop_segmark, step)
    dict_eph_segmark     = agreguj_slovnik( dict_eph_segmark, step)
    dict_sop_eph_segmark = agreguj_slovnik( dict_sop_eph_segmark, step)

    # ZAPIS DO VYSTUPNIHO SOUBORU
    zapis_agregovana_data(dict_sop,             graphs_data_bitrate_rezie_sop_agreg_filename)
    zapis_agregovana_data(dict_eph,             graphs_data_bitrate_rezie_eph_agreg_filename)
    zapis_agregovana_data(dict_sop_eph,         graphs_data_bitrate_rezie_sop_eph_agreg_filename)
    zapis_agregovana_data(dict_segmark,         graphs_data_bitrate_rezie_segmark_agreg_filename)
    zapis_agregovana_data(dict_sop_segmark,     graphs_data_bitrate_rezie_sop_segmark_agreg_filename)
    zapis_agregovana_data(dict_eph_segmark,     graphs_data_bitrate_rezie_eph_segmark_agreg_filename)
    zapis_agregovana_data(dict_sop_eph_segmark, graphs_data_bitrate_rezie_sop_eph_segmark_agreg_filename)


# agrefuje data z datových souborů pro každý analyzovaný obraz, PRO MODY
def agreguj_data_rezie_modu( step ):

    pocet_slozek = 0 # počet analyzovanych obrazů, pro každý je vytvořena jedna šložka s datovými soubory
    dict_segmark = dict()
    dict_reset = dict()
    dict_restart = dict()
    dict_erterm = dict()
    dict_vsechny = dict()

    dict_all = dict()
    dict_bypass = dict()
    dict_bypasssegmark = dict()
    dict_ertermsegmark = dict()
    dict_lazyparallel = dict()
    dict_lazyparallelsegmark = dict()
    dict_none = dict()
    dict_parallel = dict()
    dict_parallelsegmark = dict()
    dict_segmark = dict()

    # ZJISTENI DAT
    for root_d, dirs, files in os.walk(directory_graphs_data):
        for dir_name in dirs:
            #print("Obsah slozky: ", dir_name)
            pocet_slozek += 1
            for root_d, dirs, files_in_dir in os.walk(directory_graphs_data + str(dir_name) + "/"):
                for filename in fnmatch.filter(files_in_dir, '*rezie*'):
                    tmp_dict = dict()
                    # ZJIŠTĚNÍ TYPU SOUBORU A ZÁPIS DO PATŘIČNÉHO SLOVNÍKU

                    if re.search(r"rezie_mode_all", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_all[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_bypass", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_bypass[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_bypasssegmark", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_bypasssegmark[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_ertermsegmark", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_ertermsegmark[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_lazyparallel", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_lazyparallel[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_lazyparallelsegmark", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_lazyparallelsegmark[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_none", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_none[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_parallel", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_parallel[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_parallelsegmark", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_parallelsegmark[pocet_slozek] = tmp_dict

                    if re.search(r"rezie_mode_segmark", filename):
                        with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                            for line in file:
                                tmp = line.split()
                                tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                            dict_segmark[pocet_slozek] = tmp_dict

    dict_all = agreguj_slovnik( dict_all, step)
    dict_bypass = agreguj_slovnik( dict_bypass, step)
    dict_bypasssegmark = agreguj_slovnik( dict_bypasssegmark, step)
    dict_ertermsegmark =agreguj_slovnik( dict_ertermsegmark, step)
    dict_lazyparallel = agreguj_slovnik( dict_lazyparallel, step)
    dict_lazyparallelsegmark = agreguj_slovnik( dict_lazyparallelsegmark, step)
    dict_parallel = agreguj_slovnik( dict_parallel, step)
    dict_parallelsegmark = agreguj_slovnik( dict_parallelsegmark, step)
    dict_segmark = agreguj_slovnik( dict_segmark, step)

    print("VSECHNY MODY: ", dict_vsechny)

    # ZAPIS DO VYSTUPNIHO SOUBORU
    prumerna_rezie(dict_all, 'vsechny mody')
    prumerna_rezie(dict_bypasssegmark, 'line zpracovani + segmark')
    prumerna_rezie(dict_ertermsegmark, 'erterm + segmark')
    prumerna_rezie(dict_lazyparallel, 'line paralelni')
    prumerna_rezie(dict_lazyparallelsegmark, 'line pralalelni + segmark')
    prumerna_rezie(dict_parallel, 'paralelni')
    prumerna_rezie(dict_parallelsegmark, 'paralelni + segmark')
    prumerna_rezie(dict_segmark, 'segmark')


# agrefuje data z datových souborů pro každý analyzovaný obraz, PRO MODY
def agreguj_data_rezie_modes_markers( step ):

    pocet_slozek = 0 # počet analyzovanych obrazů, pro každý je vytvořena jedna šložka s datovými soubory
    dict_modes_markers = dict()


    # ZJISTENI DAT
    for root_d, dirs, files in os.walk(directory_graphs_data):
        for dir_name in dirs:
            #print("Obsah slozky: ", dir_name)
            pocet_slozek += 1
            for root_d, dirs, files_in_dir in os.walk(directory_graphs_data + str(dir_name) + "/"):
                print(files_in_dir)
                for filename in fnmatch.filter(files_in_dir, '*bitrate_rezie_vsechny_mody_sop_eph*'):
                    print("snazim se agregovat: ", filename)
                    tmp_dict = dict()
                    with open(str(directory_graphs_data + str(dir_name) + "/" + filename), 'r') as file:
                        for line in file:
                            tmp = line.split()
                            tmp_dict[str(round(float(tmp[0]), 3))] = str(round(float(tmp[1]), 3))
                        dict_modes_markers[pocet_slozek] = tmp_dict


    dict_modes_markers  = agreguj_slovnik( dict_modes_markers, step)

    # ZAPIS DO VYSTUPNIHO SOUBORU
    zapis_agregovana_data(dict_modes_markers, graphs_data_bitrate_rezie_vsechny_mody_sop_eph_agreg_filename)
    print(dict_modes_markers)


# připraví datové soubory pro sloupcové grafy z již agregovaných datových souborů, PRO MARKERY
def priprav_data_pro_sloupcovy_graf_rezie_nizky_bitrate_markers():

    more_than = 0.16
    less_than = 0.18

    with open( "output/graphs_data/agreg/histogram_nizky_bitrate_rezie_markers.dat", 'w') as nizky_bitrate:
        nizky_bitrate.write("REZIE ZABEZPECENI\n")

        with open ( str(graphs_data_bitrate_rezie_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < less_than and float(tmp[0]) > more_than:
                    #print(tmp)
                    nizky_bitrate.write( "T1 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_eph_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < less_than and float(tmp[0]) > more_than:
                    #print(tmp)
                    nizky_bitrate.write( "T2 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_eph_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < less_than and float(tmp[0]) > more_than:
                    #print(tmp)
                    nizky_bitrate.write( "T3 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < less_than and float(tmp[0]) > more_than:
                    #print(tmp)
                    nizky_bitrate.write( "T4 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < less_than and float(tmp[0]) > more_than:
                    #print(tmp)
                    nizky_bitrate.write( "T5 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_eph_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < less_than and float(tmp[0]) > more_than:
                    #print(tmp)
                    nizky_bitrate.write( "T6 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_eph_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < less_than and float(tmp[0]) > more_than:
                    #print(tmp)
                    nizky_bitrate.write( "T7 "  + str(tmp[1]) + "\n")
                    break


# připraví datové soubory pro sloupcové grafy z již agregovaných datových souborů, PRO MARKERY
def priprav_data_pro_sloupcovy_graf_rezie_vysoky_bitrate_markers():

    more_than = 2.2
    less_than = 2.4

    with open( "output/graphs_data/agreg/histogram_vysoky_bitrate_rezie_markers.dat", 'w') as vysoky_bitrate:
        vysoky_bitrate.write("REZIE ZABEZPECENI\n")
        with open ( str(graphs_data_bitrate_rezie_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.4 and float(tmp[0]) > more_than:
                    #print(tmp)
                    vysoky_bitrate.write( "T1 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_eph_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.4 and float(tmp[0]) > more_than:
                    #print(tmp)
                    vysoky_bitrate.write( "T2 "  + str(tmp[1]) + "\n")
                    break


        with open ( str(graphs_data_bitrate_rezie_eph_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.4 and float(tmp[0]) > more_than:
                    #print(tmp)
                    vysoky_bitrate.write( "T3 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.4 and float(tmp[0]) > more_than:
                    #print(tmp)
                    vysoky_bitrate.write( "T4 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.4 and float(tmp[0]) > more_than:
                    #print(tmp)
                    vysoky_bitrate.write( "T5 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_eph_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.4 and float(tmp[0]) > more_than:
                    #print(tmp)
                    vysoky_bitrate.write( "T6 "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_sop_eph_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.4 and float(tmp[0]) > more_than:
                    #print(tmp)
                    vysoky_bitrate.write( "T7 "  + str(tmp[1]) + "\n")
                    break


# Funkce vykreslí grafy podle dat ve vstupních souborech a uloží je ve formátu PDF do složky output/graphs, PRO MARKERY
def plot_graphs_markers( agreg_step ):
    '''Funkce vykreslí grafy podle dat ve vstupních souborech a uloží je ve formátu PDF do složky output/graphs'''

    agreguj_data_rezie_markeru(agreg_step)
    '''priprav_data_pro_sloupcovy_graf_rezie_nizky_bitrate_markers()
    priprav_data_pro_sloupcovy_graf_rezie_vysoky_bitrate_markers()

    # histogram rezie pro nizky bitrate
    pg.c('set xlabel "ZABEZPEČENÍ"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('unset key; set style data histogram; set style fill solid border; set style histogram clustered')
    pg.c("plot for [COL=2:3] 'output/graphs_data/agreg/histogram_nizky_bitrate_rezie_markers.dat' using COL:xticlabels(1) title columnheader")
    pg.pdf('output/graphs/histogram_rezie_nizky_bitrate_markers.pdf')

    # histogram rezie pro vysoky bitrate
    pg.c('set xlabel "ZABEZPEČENÍ"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('unset key; set style data histogram; set style fill solid border; set style histogram clustered')
    pg.c("plot for [COL=2:3] 'output/graphs_data/agreg/histogram_vysoky_bitrate_rezie_markers.dat' using COL:xticlabels(1) title columnheader")
    pg.pdf('output/graphs/histogram_rezie_vysoky_bitrate_markers.pdf')'''


    # Kolik % velikosti souboru zabírají markery v závislosti na bitrate
    pg.c('set xlabel "BITRATE"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('set yrange [0:55]; set xrange [0:2.5]; set key right')
    pg.c("plot '"   + str(graphs_data_bitrate_rezie_sop_agreg_filename) + "' title 'SOP'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_bitrate_rezie_eph_agreg_filename) + "' title 'EPH'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_bitrate_rezie_sop_eph_agreg_filename) + "' title 'SOP + EPH'  with lines lw 3")
    #pg.c("replot '" + str(graphs_data_bitrate_rezie_segmark_agreg_filename) + "' title 'SEGMARK'  with lines linestyle 4")
    #pg.c("replot '" + str(graphs_data_bitrate_rezie_sop_segmark_agreg_filename) + "' title 'SOP + SEGMARK'  with lines linestyle 5")
    #pg.c("replot '" + str(graphs_data_bitrate_rezie_eph_segmark_agreg_filename) + "' title 'EPH + SEGMARK'  with lines linestyle 6")
    #pg.c("replot '" + str(graphs_data_bitrate_rezie_sop_eph_segmark_agreg_filename) + "' title 'SOP + EPH + SEGMARK'  with lines linestyle 7")
    pg.pdf('output/graphs/bitrate_rezie_zabezpeceni_markers.pdf')

    agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_bez_ochrany_filename,     graphs_data_failed_na_poskozeni_bez_ochrany_agreg_filename         )
    agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_sop_filename,             graphs_data_failed_na_poskozeni_sop_agreg_filename                )
    agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_eph_filename,             graphs_data_failed_na_poskozeni_eph_agreg_filename                 )
    agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_sop_eph_filename,         graphs_data_failed_na_poskozeni_sop_eph_agreg_filename             )
    #agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_segmark_filename,         graphs_data_failed_na_poskozeni_segmark_agreg_filename             )
    #agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_sop_segmark_filename,     graphs_data_failed_na_poskozeni_sop_segmark_agreg_filename         )
    #agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_eph_segmark_filename,     graphs_data_failed_na_poskozeni_eph_segmark_agreg_filename        )
    #agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_sop_eph_segmark_filename, graphs_data_failed_na_poskozeni_sop_eph_segmark_agreg_filename      )

    # Kolik % velikosti souboru zabírají markery v závislosti na bitrate a měnících se PRECINCTS a sop+eph pro layers=12
    pg.c('set key right bottom; set xlabel "POŠKOZENÍ [ % ]"; set ylabel "POČET NEDEKOMPRIMOVATELNÝCH SOUBORŮ [ % ]"')
    #pg.c('set yrange [0.5:1]; set xrange [0:0.1]; set key right')
    pg.c('set yrange [0:100]; set xrange [-0.00005:0.0205]; set key right')
    pg.c("plot '" + str(graphs_data_failed_na_poskozeni_sop_agreg_filename) + "' title 'SOP'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_failed_na_poskozeni_eph_agreg_filename) + "' title 'EPH'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_failed_na_poskozeni_sop_eph_agreg_filename) + "' title 'SOP + EPH'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_fails_mode_none_agreg_filename) + "' title 'Bez ochrany'  with lines lw 3")
    #pg.c("replot '" + str(graphs_data_failed_na_poskozeni_segmark_agreg_filename) + "' title 'SEGMARK'  with lines linestyle 4")
    #pg.c("replot '" + str(graphs_data_failed_na_poskozeni_sop_segmark_agreg_filename) + "' title 'SOP + SEGMARK'  with lines linestyle 5")
    #pg.c("replot '" + str(graphs_data_failed_na_poskozeni_eph_segmark_agreg_filename) + "' title 'EPH + SEGMARK'  with lines linestyle 6")
    #pg.c("replot '" + str(graphs_data_failed_na_poskozeni_sop_eph_segmark_agreg_filename) + "' title 'SOP + EPH + SEGMARK'  with lines linestyle 7")
    pg.pdf('output/graphs/poskozeni_neuspesne_soubory_markers.pdf')


# připraví datové soubory pro sloupcové grafy z již agregovaných datových souborů, PRO MODY
def priprav_data_pro_sloupcovy_graf_rezie_nizky_bitrate_modes():
    with open( "output/graphs_data/agreg/histogram_nizky_bitrate_rezie_modes.dat", 'w') as nizky_bitrate:
        nizky_bitrate.write("REZIE ZABEZPECENI\n")
        with open ( str(graphs_data_bitrate_rezie_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 0.18 and float(tmp[0]) > 0.15:
                    #print(tmp)
                    nizky_bitrate.write( "SEGMARK "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_reset_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 0.18 and float(tmp[0]) > 0.15:
                    #print(tmp)
                    nizky_bitrate.write( "RESET "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_restart_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 0.18 and float(tmp[0]) > 0.15:
                    #print(tmp)
                    nizky_bitrate.write( "RESTART "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_erterm_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 0.18 and float(tmp[0]) > 0.15:
                    #print(tmp)
                    nizky_bitrate.write( "ERTERM "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_vsechny_mody_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 0.18 and float(tmp[0]) > 0.15:
                    #print(tmp)
                    nizky_bitrate.write( "VSECHNY "  + str(tmp[1]) + "\n")
                    break


# připraví datové soubory pro sloupcové grafy z již agregovaných datových souborů, PRO MODY
def priprav_data_pro_sloupcovy_graf_rezie_vysoky_bitrate_modes():
    with open( "output/graphs_data/agreg/histogram_vysoky_bitrate_rezie_markers.dat", 'w') as vysoky_bitrate:
        vysoky_bitrate.write("REZIE ZABEZPECENI\n")
        with open ( str(graphs_data_bitrate_rezie_segmark_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.3 and float(tmp[0]) > 2.2:
                    #print(tmp)
                    vysoky_bitrate.write( "SEGMARK "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_reset_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.3 and float(tmp[0]) > 2.2:
                    #print(tmp)
                    vysoky_bitrate.write( "RESET "  + str(tmp[1]) + "\n")
                    break


        with open ( str(graphs_data_bitrate_rezie_restart_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.3 and float(tmp[0]) > 2.2:
                    #print(tmp)
                    vysoky_bitrate.write( "RESTART "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_erterm_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.3 and float(tmp[0]) > 2.2:
                    #print(tmp)
                    vysoky_bitrate.write( "ERTERM "  + str(tmp[1]) + "\n")
                    break

        with open ( str(graphs_data_bitrate_rezie_vsechny_mody_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.3 and float(tmp[0]) > 2.2:
                    #print(tmp)
                    vysoky_bitrate.write( "VSECHNY "  + str(tmp[1]) + "\n")
                    break


# Funkce vykreslí grafy podle dat ve vstupních souborech a uloží je ve formátu PDF do složky output/graphs, PRO MODY
def plot_graphs_modes( agreg_step ):
    '''Funkce vykreslí grafy podle dat ve vstupních souborech a uloží je ve formátu PDF do složky output/graphs'''

    agreguj_data_rezie_modu(agreg_step)
    #priprav_data_pro_sloupcovy_graf_rezie_nizky_bitrate_modes()
    #priprav_data_pro_sloupcovy_graf_rezie_vysoky_bitrate_modes()

    '''# histogram rezie pro nizky bitrate
    pg.c('set xlabel "ZABEZPEČENÍ"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('unset key; set style data histogram; set style fill solid border; set style histogram clustered')
    pg.c("plot for [COL=2:3] 'output/graphs_data/agreg/histogram_nizky_bitrate_rezie_modes.dat' using COL:xticlabels(1) title columnheader")
    pg.pdf('output/graphs/histogram_rezie_nizky_bitrate_modes.pdf')

    # histogram rezie pro vysoky bitrate
    pg.c('set xlabel "ZABEZPEČENÍ"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('unset key; set style data histogram; set style fill solid border; set style histogram clustered')
    pg.c("plot for [COL=2:3] 'output/graphs_data/agreg/histogram_vysoky_bitrate_rezie_modes.dat' using COL:xticlabels(1) title columnheader")
    pg.pdf('output/graphs/histogram_rezie_vysoky_bitrate_modes.pdf')'''

    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_all_filename,             graphs_data_fails_mode_all_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_none_filename,            graphs_data_fails_mode_none_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_bypass_filename,          graphs_data_fails_mode_bypass_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_parallel_filename,        graphs_data_fails_mode_parallel_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_lazyparallel_filename,    graphs_data_fails_mode_lazyparallel_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_ertermsegmark_filename,   graphs_data_fails_mode_ertermsegmark_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_segmark_filename,         graphs_data_fails_mode_segmark_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_bypasssegmark_filename,   graphs_data_fails_mode_bypasssegmark_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_parallelsegmark_filename, graphs_data_fails_mode_parallelsegmark_agreg_filename)
    agreguj_data_nedekomprimovatelnych_souboru(graphs_data_fails_mode_lazyparallelsegmark_filename, graphs_data_fails_mode_lazyparallelsegmark_agreg_filename)

    pg.c('set key right bottom; set xlabel "POŠKOZENÍ [ % ]"; set ylabel "POČET NEDEKOMPRIMOVATELNÝCH SOUBORŮ [ % ]"')
    # pg.c('set yrange [0.5:1]; set xrange [0:0.1]; set key right')
    pg.c('set yrange [0:100]; set xrange [-0.00005:0.0205]; set key right')

    pg.c("plot '" + str(graphs_data_fails_mode_none_agreg_filename) + "' title 'Žádný mód'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_fails_mode_bypass_agreg_filename) + "' title 'Liné zpracování'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_fails_mode_parallel_agreg_filename) + "' title 'Paralelní zpracování'  with lines lw 3")
    #pg.c("replot '" + str(graphs_data_fails_mode_lazyparallel_agreg_filename) + "' title 'Líné paralelní zpracování'  with lines linestyle 4")
    pg.c("replot '" + str(graphs_data_fails_mode_ertermsegmark_agreg_filename) + "' title 'ERTERM + SEGMARK'  with lines lw 3")
    #pg.c("replot '" + str(graphs_data_fails_mode_segmark_agreg_filename) + "' title 'SEGMARK'  with lines linestyle 6")
    #pg.c("replot '" + str(graphs_data_fails_mode_bypasssegmark_agreg_filename) + "' title 'BYPASS, SEGMARK'  with lines linestyle 7")
    #pg.c("replot '" + str(graphs_data_fails_mode_parallelsegmark_agreg_filename) + "' title 'Paralelní zpracování + SEGMARK'  with lines linestyle 8")
    pg.c("replot '" + str(graphs_data_fails_mode_lazyparallelsegmark_agreg_filename) + "' title 'Líné paralelní zpracování + SEGMARK' with lines lw 3")
    #pg.c("replot '" + str(graphs_data_fails_mode_all_agreg_filename) + "' title 'Všechny módy'  with lines linestyle 12")

    pg.pdf('output/graphs/poskozeni_neuspesne_soubory_modes.pdf')


# připraví datové soubory pro sloupcové grafy z již agregovaných datových souborů, PRO MODY + MARKERY
def priprav_data_pro_sloupcovy_graf_rezie_nizky_bitrate_modes_markers():
    with open( "output/graphs_data/agreg/histogram_nizky_bitrate_rezie_modes_markers.dat", 'w') as nizky_bitrate:
        nizky_bitrate.write("REZIE ZABEZPECENI\n")
        with open ( str(graphs_data_bitrate_rezie_vsechny_mody_sop_eph_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 0.23 and float(tmp[0]) > 0.15:
                    nizky_bitrate.write( "MODY+MARKERY "  + str(tmp[1]) + "\n")
                    break


# připraví datové soubory pro sloupcové grafy z již agregovaných datových souborů, PRO MODY + MARKERY
def priprav_data_pro_sloupcovy_graf_rezie_vysoky_bitrate_modes_markers():
    with open( "output/graphs_data/agreg/histogram_vysoky_bitrate_rezie_modes_markers.dat", 'w') as vysoky_bitrate:
        vysoky_bitrate.write("REZIE ZABEZPECENI\n")
        with open ( str(graphs_data_bitrate_rezie_vsechny_mody_sop_eph_agreg_filename), 'r') as file:
            for line in file:
                tmp = line.split()
                if float(tmp[0]) < 2.3 and float(tmp[0]) > 2.2:
                    vysoky_bitrate.write( "MODY+MARKERY "  + str(tmp[1]) + "\n")
                    break


# Funkce vykreslí grafy podle dat ve vstupních souborech a uloží je ve formátu PDF do složky output/graphs, PRO MODY
def plot_graphs_modes_markers( agreg_step ):
    '''Funkce vykreslí grafy podle dat ve vstupních souborech a uloží je ve formátu PDF do složky output/graphs'''

    agreguj_data_rezie_modes_markers(agreg_step)
    #priprav_data_pro_sloupcovy_graf_rezie_nizky_bitrate_modes_markers()
    #priprav_data_pro_sloupcovy_graf_rezie_vysoky_bitrate_modes_markers()

    '''# histogram rezie pro nizky bitrate
    pg.c('set xlabel "ZABEZPEČENÍ"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('unset key; set style data histogram; set style fill solid border; set style histogram clustered')
    pg.c("plot for [COL=2:3] 'output/graphs_data/agreg/histogram_nizky_bitrate_rezie_modes_markers.dat' using COL:xticlabels(1) title columnheader")
    pg.pdf('output/graphs/histogram_rezie_nizky_bitrate_modes_markers.pdf')

    # histogram rezie pro vysoky bitrate
    pg.c('set xlabel "ZABEZPEČENÍ"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('unset key; set style data histogram; set style fill solid border; set style histogram clustered')
    pg.c("plot for [COL=2:3] 'output/graphs_data/agreg/histogram_vysoky_bitrate_rezie_modes_markers.dat' using COL:xticlabels(1) title columnheader")
    pg.pdf('output/graphs/histogram_rezie_vysoky_bitrate_modes_markers.pdf')'''


    # Kolik % velikosti souboru zabírají markery v závislosti na bitrate
    pg.c('set xlabel "BITRATE"; set ylabel "REŽIE ZABEZPEČENÍ [ % ]"')
    pg.c('set yrange [0:65]; set xrange [0:2.5]; set key right top')
    pg.c("plot '"   + str(graphs_data_bitrate_rezie_sop_eph_agreg_filename) + "' title 'SOP + EPH'  with lines lw 3")
    pg.c("replot '"   + str(graphs_data_bitrate_rezie_vsechny_mody_sop_eph_agreg_filename) + "' title 'Líné paralelní zpracování + SEGMARK + SOP + EPH'  with lines lw 3")
    pg.pdf('output/graphs/bitrate_rezie_zabezpeceni_modes_markers.pdf')

    agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_bez_ochrany_filename,               graphs_data_failed_na_poskozeni_bez_ochrany_agreg_filename          )
    agreguj_data_nedekomprimovatelnych_souboru( graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph_filename,      graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph_agreg_filename )

    # Kolik % velikosti souboru zabírají markery v závislosti na bitrate a měnících se PRECINCTS a sop+eph pro layers=12
    pg.c('set key right bottom; set xlabel "POŠKOZENÍ [ % ]"; set ylabel "POČET NEDEKOMPRIMOVATELNÝCH SOUBORŮ [ % ]"')
    #pg.c('set yrange [0.5:1]; set xrange [0:0.1]; set key right')
    pg.c('set yrange [0:100]; set xrange [-0.00005:0.0205]; set key right')
    pg.c("plot '"   + str(graphs_data_fails_mode_none_agreg_filename) + "' title 'Bez ochrany'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_failed_na_poskozeni_sop_eph_agreg_filename) + "' title 'SOP + EPH'  with lines lw 3")
    #pg.c("replot '" + str(graphs_data_failed_na_poskozeni_sop_eph_segmark_agreg_filename) + "' title 'SOP, EPH, SEGMARK'  with lines linestyle 5")
    pg.c("replot '" + str(graphs_data_fails_mode_lazyparallelsegmark_agreg_filename) + "' title 'Líné paralelní zpracování + SEGMARK'  with lines lw 3")
    pg.c("replot '" + str(graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph_agreg_filename) + "' title 'Líné paralelní zpracování + SEGMARK + SOP + EPH'  with lines lw 3")
    pg.pdf('output/graphs/poskozeni_neuspesne_soubory_modes_markers.pdf')

# Funkce vrátí slovník s půrměrným počtem nedekomprimovatelných souborů, vyjádřen procentuálně pro každý typ zabezpečení
def prumerny_pocet_nedekomprimovatelnych_souboru():
    # spočítání průměrného počtu nedekomprimovatelných souborů v procentuálním vyjádření pro každý typ zabezpečení
    agregovane_soubory = [  { "0" : graphs_data_fails_mode_none_agreg_filename },                   # 0 => žádná ochrana
                            { "1" : graphs_data_fails_mode_bypass_agreg_filename },
                            { "2" : graphs_data_fails_mode_parallel_agreg_filename },
                            { "3" : graphs_data_fails_mode_ertermsegmark_agreg_filename },
                            { "4" : graphs_data_fails_mode_lazyparallelsegmark_agreg_filename },
                            { "5" : graphs_data_failed_na_poskozeni_sop_agreg_filename },
                            { "6" : graphs_data_failed_na_poskozeni_eph_agreg_filename },
                            { "7" : graphs_data_failed_na_poskozeni_sop_eph_agreg_filename },
                            { "8" : graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph_agreg_filename },
                        ]

    result = list()
    tmp = list()

    for el in agregovane_soubory:
        kind = list(el.keys())[0]
        file = list(el.values())[0]
        with open(file, "r") as input:
            for line in input:
                tmp.append(float(line.split()[1]))

        value = round(float(statistics.mean(tmp)),2)
        result.append(value)
        tmp = list()

        print("prumer fails => el:", el, " => ", value)

    return result


# Funkce vrátí slovník s půrměrným režií pro každý typ zabezpečení
def prumerna_rezie_zabezpeceni():
    # spočítání průměrnou režii použitého zabezpečení do 2.5 bit/pixel
    agregovane_soubory = [{"5": graphs_data_bitrate_rezie_sop_agreg_filename},
                          {"6": graphs_data_bitrate_rezie_eph_agreg_filename},
                          {"7": graphs_data_bitrate_rezie_sop_eph_agreg_filename},
                          {"8": graphs_data_bitrate_rezie_vsechny_mody_sop_eph_agreg_filename},
                          ]

    result = list()
    tmp = list()

    result.append(0) # nulová reřie zabezepčení pro T0 => žádná ochrana
    result.append(0)   # liné zpracování -0.181
    result.append(0.39)     # paralelní zpracování
    result.append(0.43)     # erterm, segmark
    result.append(0.53)     # lazy parallel + segmark


    for el in agregovane_soubory:
        kind = list(el.keys())[0]
        file = list(el.values())[0]
        with open(file, "r") as input:
            for line in input:
                tmp.append(float(line.split()[1]))

        value = round(float(statistics.mean(tmp)), 2)
        #print("el kind: ", kind, "\tel value:", value)
        result.append(value)
        tmp = list()

        print("prumer rezie => el:", el, " => ", value)

    return result

# Funkce vytvoří graf souvislostí použitého typu zabezpečení k režii a počtu nedekomprimovatelných souborů
def plot_graph_souvislosti():
    '''Funkce vytvoří graf souvislostí použitého typu zabezpečení k režii a počtu nedekomprimvoatelných souborů'''
    neuspesne = prumerny_pocet_nedekomprimovatelnych_souboru()
    rezie = prumerna_rezie_zabezpeceni()
    print("prumer rezie: ", rezie)
    print("prumer fails: ", neuspesne)

    N = 9
    ind = np.arange(N)  # the x locations for the groups
    width = 0.2  # the width of the bars: can also be len(x) sequence

    p1 = plt.bar(ind, neuspesne, width)
    #p2 = plt.bar(ind, rezie, width,bottom=neuspesne, color='#d62728') #opoznámkovat pro zobrazení neuspesnych a rezie nad sebou
    p2 = plt.bar(ind+0.2, rezie, width, color='#d62728') #opoznámkovat pro zobrazení neuspesnych a rezie vedle sebou

    plt.xlabel('Typ zabezpečení')
    plt.ylabel('Hodnocení')
    plt.xticks(ind, ('T0', 'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8'))
    plt.yticks(np.arange(0, 60, 10))
    plt.legend((p2[0], p1[0]), ('Režie', 'Neúspěšné'))

    best_resilience = min(neuspesne)

    plt.axhline(y=best_resilience, color='g', linestyle='-')

    plt.savefig( graphs_zabezpeceni_a_rezie_filename, format='pdf')


if __name__ == '__main__':

    with open( graphs_data_souboru_celkem_filename, "r") as file_souboru_celkem:
        SOUBORU_CELKEM = int(file_souboru_celkem.readline())
        BEZ_POSKOZENI = int(file_souboru_celkem.readline())
        ITERACI = int(file_souboru_celkem.readline())

    print("SOUBORU CELKEM:", SOUBORU_CELKEM)
    print("BEZ POSKOZENI:", BEZ_POSKOZENI)
    print("ITERACI:", ITERACI)

    try:
        shutil.rmtree(directory_graphs_data_agreg)
        os.makedirs(directory_graphs_data_agreg)
    except:
        os.makedirs(directory_graphs_data_agreg)


    # vykreslí grafy z existujících datových souborů
    plot_graphs_markers(agreg_step = 0.01)
    plot_graphs_modes(agreg_step = 0.01)
    plot_graphs_modes_markers(agreg_step=0.01)
    plot_graph_souvislosti()

