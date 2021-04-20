#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

import os
import subprocess
import re
import shutil
import fnmatch
from ArgumentParser import *
from subprocess import call
from ImageDamager import *
from PSNRCalculator import *
from CompressionDetails import get_compression_details
from Globals import *
#from PlotGraphs import plot_graphs
from Packets import *
from PIL import *

LIBRARY = 'kakadu'
#LIBRARY = 'openjpeg'

# Maximální počet iterací pro hledání bitrate
POCET_ITERACI = 30
REZIE_SOP = 6       # 6 bytů
REZIE_EPH = 2       # 2 byty
REZIE_SEGMARK = 0.5 # 4 bity
IMAGE_COUNTER = 0
SOUBORU_CELKEM = 0
SOUBORU_NEDEKOMPRIMOVATELNYCH_BEZ_POSKOZENI = 0
EPSILON = 0.3
POCET_POSKOZENI = 13
MAX_POCET_HLEDANI_STEJNE_KVALITY = 30
BITOVA_HLOUBKA = 8
PRAH = 35 # PSNR pod ktere nesmi psnr dekomprimvoaneho klesnout aby byl brán jako uspěšně dekomprimovaný

mode_none = False
mode_lazy = False
mode_parallel = False
mode_lazy_parallel = False
mode_segmark = False
mode_bypass_segmark = False
mode_parallel_segmark = False
mode_lazy_parallel_segmark = False
mode_all = False

used_mode = None
# 1 = None
# 2 = BYPASS
# 3 = RESET, RESTART, CAUSAL
# 4 = BYPASS, RESET, RESTART, CAUSAL
# 5 = ERTERM, SEGMARK
# 6 = SEGMARK
# 7 = BYPASS, SEGMARK
# 8 = RESET, RESTART, CAUSAL, SEGMARK
# 9 = BYPASS, RESET, RESTART, CAUSAL, SEGMARK
# 10 = BYPASS, RESET, RESTART, CAUSAL, SEGMARK, ERTERM
# 11 = SOP, EPH, BYPASS, RESET, RESTART, CAUSAL, SEGMARK, ERTERM
# 12 = SOP
# 13 = EPH
# 14 = SOP, EPH

def compress_image(filename, bitrate, sop, eph, modes):

    if LIBRARY == 'kakadu':
        # KAKADU
        try:
            print("[INFO] KAKADU: Komprimace pomocí skriptu 'compress_file_with_kakadu.sh'")
            compressed_filename = subprocess.check_output(["./compress_file_with_kakadu.sh", str(filename), str(bitrate), str(sop), str(eph), str(modes)])
        except:
            print("[ERROR] Nepovedlo se zkomprimovat soubor '" + str(filename) + "' knihovnou KAKADU")
            compressed_filename = None
            exit()

        compressed_filename = compressed_filename.split()[-1]
        compressed_filename = str(compressed_filename)[2:]
        compressed_filename = compressed_filename[:-1]

        return str(compressed_filename)

    elif LIBRARY == 'openjpeg':
        # OPENJPEG

        # přepočet bitrate na kompresní poměr pro knihovnu openjpeg
        kompresni_pomer = round( 24 / bitrate )

        # 12x zadaváný kompresní poměr udává 12 vrstev kvality, každá vrstva má o 0.1 snížený kompresní poměr
        kompresni_pomer_pro_opj_compress = str(kompresni_pomer)+','+str(kompresni_pomer-0.1)+','+str(kompresni_pomer-0.2)+','+str(kompresni_pomer-0.3)+','+str(kompresni_pomer-0.4)+','+str(kompresni_pomer-0.5)+','+str(kompresni_pomer-0.6)+','+str(kompresni_pomer-0.7)+','+str(kompresni_pomer-0.8)+','+str(kompresni_pomer-0.9)+','+str(kompresni_pomer-1)+','+str(kompresni_pomer-1.1)

        try:
            print("[INFO] KAKADU: Komprimace pomocí skriptu 'compress_file_with_openjpeg.sh'")
            compressed_filename = subprocess.check_output(["./compress_file_with_openjpeg.sh", str(filename), str(kompresni_pomer_pro_opj_compress), str(sop), str(eph), str(modes)])
        except:
            print("[ERROR] Nepovedlo se zkomprimovat soubor '" + str(filename) + "' knihovnou OPENJPEG")
            compressed_filename = None
            exit()

        compressed_filename = compressed_filename.split()[-1]
        compressed_filename = str(compressed_filename)[2:]
        compressed_filename = compressed_filename[:-1]

        return str(compressed_filename)


# Hlavní smyčka programu
if __name__ == '__main__':

    # check arguments and get valid path to directory
    directory, lib = ArgumentParser.checkArguments(sys.argv)

    if lib:
        LIBRARY = lib

    print("*** Looking for files in directory '" + str(directory) + "' and compress them")
    print("*** Used library: " + str(LIBRARY))

    try:
        shutil.rmtree(directory_tmp)
    except:
        pass

    # create folder for output .tex document and grapfs
    try:
        shutil.rmtree(directory_output)
        os.makedirs(directory_output)
        os.makedirs(directory_graphs)
        os.makedirs(directory_graphs_data)

    except:
        os.makedirs(directory_output)
        os.makedirs(directory_graphs)
        os.makedirs(directory_graphs_data)


    ####################################################################################################
    # OTEVŘENÍ SOUBORŮ PRO ZÁPIS
    ####################################################################################################

    graphs_data_failed_na_poskozeni_bez_ochrany     = open(graphs_data_failed_na_poskozeni_bez_ochrany_filename, 'w')

    graphs_data_fails_mode_none = open(graphs_data_fails_mode_none_filename, 'w')
    graphs_data_fails_mode_bypass = open(graphs_data_fails_mode_bypass_filename, 'w')
    graphs_data_fails_mode_parallel = open(graphs_data_fails_mode_parallel_filename, 'w')
    graphs_data_fails_mode_lazyparallel = open(graphs_data_fails_mode_lazyparallel_filename, 'w')
    graphs_data_fails_mode_ertermsegmark = open(graphs_data_fails_mode_ertermsegmark_filename, 'w')
    graphs_data_fails_mode_segmark = open(graphs_data_fails_mode_segmark_filename, 'w')
    graphs_data_fails_mode_bypasssegmark = open(graphs_data_fails_mode_bypasssegmark_filename, 'w')
    graphs_data_fails_mode_parallelsegmark = open(graphs_data_fails_mode_parallelsegmark_filename, 'w')
    graphs_data_fails_mode_lazyparallelsegmark = open(graphs_data_fails_mode_lazyparallelsegmark_filename, 'w')
    graphs_data_fails_mode_all = open(graphs_data_fails_mode_all_filename, 'w')

    graphs_data_failed_na_poskozeni_sop = open(graphs_data_failed_na_poskozeni_sop_filename, 'w')
    graphs_data_failed_na_poskozeni_eph = open(graphs_data_failed_na_poskozeni_eph_filename, 'w')
    graphs_data_failed_na_poskozeni_sop_eph = open(graphs_data_failed_na_poskozeni_sop_eph_filename, 'w')
    graphs_data_failed_na_poskozeni_segmark = open(graphs_data_failed_na_poskozeni_segmark_filename, 'w')
    graphs_data_failed_na_poskozeni_sop_segmark = open(graphs_data_failed_na_poskozeni_sop_segmark_filename, 'w')
    graphs_data_failed_na_poskozeni_eph_segmark = open(graphs_data_failed_na_poskozeni_eph_segmark_filename, 'w')
    graphs_data_failed_na_poskozeni_sop_eph_segmark = open(graphs_data_failed_na_poskozeni_sop_eph_segmark_filename, 'w')

    graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph = open(graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph_filename, 'w')

    ####################################################################################################
    # WALK THROUGH THE DIRECTORY WITH TEST DATA
    ####################################################################################################
    for root_d, dirs, files in os.walk(directory):
        for filename in fnmatch.filter(files, ppm_pattern):
            IMAGE_COUNTER += 1

            ####################################################################################################
            # GET FILENAME AND ORIGINAL FILESIZE FOR OUTPUT FILE
            ####################################################################################################

            original_filename = str(os.path.join(root_d, filename))

            print( "/////////////////////////////////////////////////////////////////////////////////////////////////////////////\n"
                "File: " + str(original_filename) + " is going to be compressed in various modes")

            try:
                im = cv2.imread(original_filename, 0)
                original_file_height, original_file_width = im.shape[:2]
                original_filesize = os.path.getsize(original_filename)

                reference_filename_for_output = filename[:-4] + ".jp2"
            except:
                print("[ERROR] Tenhle obraz se nepodarilo zpracovat")
                break

            ####################################################################################################
            # VYTVOŘENÍ SLOŽKY PRO DATOVÉ SOUBORY K ANALYZOVANÉMU OBRAZU A OTEVŘENÍ DATOVÝCH SOUBORŮ
            ####################################################################################################

            os.makedirs(str(directory_graphs_data + str(IMAGE_COUNTER) + "/"))

            with open(str(directory_graphs_data + str(IMAGE_COUNTER) + "/filename"), 'w') as filename_dat:
                filename_dat.write(str(original_filename))

            graphs_data_rezie_mode_none                 = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_none_filename), 'w')
            graphs_data_rezie_mode_bypass               = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_bypass_filename), 'w')
            graphs_data_rezie_mode_parallel             = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_parallel_filename), 'w')
            graphs_data_rezie_mode_lazyparallel         = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_lazyparallel_filename), 'w')
            graphs_data_rezie_mode_ertermsegmark        = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_ertermsegmark_filename), 'w')
            graphs_data_rezie_mode_segmark              = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_segmark_filename), 'w')
            graphs_data_rezie_mode_bypasssegmark        = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_bypasssegmark_filename), 'w')
            graphs_data_rezie_mode_parallelsegmark      = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_parallelsegmark_filename), 'w')
            graphs_data_rezie_mode_lazyparallelsegmark  = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_lazyparallelsegmark_filename), 'w')
            graphs_data_rezie_mode_all                  = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_rezie_mode_all_filename), 'w')

            graphs_data_bitrate_rezie_sop = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(bitrate_rezie_sop_filename), 'w')
            graphs_data_bitrate_rezie_eph = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(bitrate_rezie_eph_filename), 'w')
            graphs_data_bitrate_rezie_sop_eph = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(bitrate_rezie_sop_eph_filename), 'w')
            graphs_data_bitrate_rezie_segmark = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(bitrate_rezie_segmark_filename), 'w')
            graphs_data_bitrate_rezie_sop_segmark = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(bitrate_rezie_sop_segmark_filename), 'w')
            graphs_data_bitrate_rezie_eph_segmark = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(bitrate_rezie_eph_segmark_filename), 'w')
            graphs_data_bitrate_rezie_sop_eph_segmark = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(bitrate_rezie_sop_eph_segmark_filename),'w')

            graphs_data_bitrate_rezie_vsechny_mody_sop_eph = open(str(directory_graphs_data) + str(IMAGE_COUNTER) + "/" + str(graphs_data_bitrate_rezie_vsechny_mody_sop_eph_filename), 'w')

            ####################################################################################################
            # COMPRESS FILE IN VARIOUS MODES
            ####################################################################################################
            for PARAMETRY in PARAMETRY_KOMPRESE:
                actual_bitrate = -0.025

                for i in range(0, POCET_ITERACI):
                    actual_bitrate += 0.050
                    ####################################################################################################
                    # CLEANING ALL TEMPORARY FILES
                    ####################################################################################################
                    print("*** Cleaning up ... deleting tmp folder")
                    try:
                        shutil.rmtree(directory_tmp)
                    except:
                        pass

                    ####################################################################################################
                    # CREATING DIRECTIORIES FOR TEMPORARY FILES - zapoznamkovat pro účely testování
                    ####################################################################################################
                    print("*** Creating tmp folder")
                    os.makedirs(directory_tmp)
                    os.makedirs(directory_compressed_kakadu)
                    os.makedirs(directory_reference_kakadu)
                    os.makedirs(directory_decompressed_kakadu)

                    actual_bitrate_no_markers = actual_bitrate
                    actual_bitrate_with_markers = actual_bitrate
                    psnr_image_no_markers = 0
                    psnr_image_with_markers = 100
                    pocet_hledani = 0

                    ####################################################################################################
                    # HLEDANI STEJNE KVALITY PRO RUZNE KOMPRIMOVANE SOUBORY
                    ####################################################################################################
                    while abs(psnr_image_no_markers - psnr_image_with_markers) > EPSILON or pocet_hledani == MAX_POCET_HLEDANI_STEJNE_KVALITY:
                        print("[ HLEDANI STEJNEHO PSNR ] hledani: " + str(pocet_hledani) + " \n")
                        ####################################################################################################
                        # COMPRESS NONDAMAGED FILES
                        ####################################################################################################
                        print("[INFO] komprese souboru bez zabezpeceni: no, no BYPASS \n")
                        image_no_markers = compress_image(original_filename, actual_bitrate_no_markers, 'no', 'no', 'BYPASS')
                        print("[INFO] vytvoren soubor:", image_no_markers, "\n")
                        print("[INFO] komprimovani souboru se zabezpecenim: = ",PARAMETRY[0], PARAMETRY[1], PARAMETRY[2], "\n")
                        image_with_markers = compress_image(original_filename, actual_bitrate_with_markers, PARAMETRY[0], PARAMETRY[1], PARAMETRY[2])
                        print("[INFO] vytvoren soubor:", image_with_markers, "\n")


                        ####################################################################################################
                        # DECOMPRESS NONDAMAGED FILES
                        ####################################################################################################

                        print("\n* *** Decompress NONDAMAGED FILES - compressed files by Kakadu")
                        image_no_markers_decompressed = re.search("[\w_.]+$", image_no_markers)
                        image_no_markers_decompressed = re.sub(r".jp2$", "_nondamaged_decompressed.ppm",image_no_markers_decompressed.group(0))

                        image_with_markers_decompressed = re.search("[\w_.]+$", image_with_markers)
                        image_with_markers_decompressed = re.sub(r".jp2$", "_nondamaged_decompressed.ppm",image_with_markers_decompressed.group(0))

                        # soubor bez zabezpeceni

                        if LIBRARY == 'kakadu':
                            try:
                                call(["kdu_expand", "-i", str(image_no_markers), "-o", str(directory_decompressed_kakadu + image_no_markers_decompressed), "-resilient"])
                            except:
                                print("*" + str(IMAGE_COUNTER) + "*[ERROR] Neposkozeny soubor bez zabezpeceni se nepodarilo dekomprimovat")

                            # soubor se zabezpecenim
                            try:
                                call(["kdu_expand", "-i", str(image_with_markers), "-o", str(directory_decompressed_kakadu + image_with_markers_decompressed), "-resilient"])
                            except:
                                print("*" + str(IMAGE_COUNTER) + "*[ERROR] Neposkozeny soubor se zabezpecenim se nepodarilo dekomprimovat")

                        elif LIBRARY == 'openjpeg':
                            try:
                                call(["./lib/openjpeg/build/bin/opj_decompress", "-i", str(image_no_markers), "-o",str(directory_decompressed_kakadu + image_no_markers_decompressed)])
                            except:
                                print("*" + str(IMAGE_COUNTER) + "*[ERROR] Neposkozeny soubor bez zabezpeceni se nepodarilo dekomprimovat")

                                # soubor se zabezpecenim
                            try:
                                call(["./lib/openjpeg/build/bin/opj_decompress", "-i", str(image_with_markers), "-o",str(directory_decompressed_kakadu + image_with_markers_decompressed)])
                            except:
                                print("*" + str(IMAGE_COUNTER) + "*[ERROR] Neposkozeny soubor se zabezpecenim se nepodarilo dekomprimovat")


                        psnr_image_no_markers = calculate_psnr( original_filename , str(directory_decompressed_kakadu + image_no_markers_decompressed))
                        psnr_image_with_markers = calculate_psnr(original_filename, str(directory_decompressed_kakadu + image_with_markers_decompressed))

                        print( "SOUBOR bez markeru: " + str(directory_decompressed_kakadu + image_no_markers_decompressed) )
                        print( "PSNR souboru bez markeru: " + str(psnr_image_no_markers) )
                        print("SOUBOR s markery: " + str(directory_decompressed_kakadu + image_with_markers_decompressed))
                        print("PSNR souboru bez markeru: " + str(psnr_image_with_markers))

                        if abs(psnr_image_no_markers - psnr_image_with_markers) < EPSILON:
                            break

                        if psnr_image_no_markers > psnr_image_with_markers:
                            actual_bitrate_with_markers += 0.05
                        else:
                            actual_bitrate_no_markers += 0.05

                        pocet_hledani += 1

                    ####################################################################################################
                    # SROVNANI KVALITY OBRAZU, POKUD JSOU STEJNE KVALITY, ZACNE SE ANALYZOVAT ZABEZPECENI
                    ####################################################################################################

                    if abs( psnr_image_no_markers - psnr_image_with_markers ) < EPSILON:
                        # ZACNE SE ANALYZOVAT ZABEZPECNI
                        print( "Zabezpecny soubor a nezapezpeceny jsou skoro stejne kvality, zacina analyza zabezpeceni.")

                        # ZJISTENI VLASTNOSTI SOUBORU
                        _SOP_no_markers, _EPH_no_markers, _SEGMARK_no_markers, _MODES_no_markers, _FILESIZE_no_markers, _BITRATE_no_markers, _PACKETS_no_markers, _TILES_no_markers, _MODES_TYPE = get_compression_details(image_no_markers)
                        _SOP_markers, _EPH_markers, _SEGMARK_markers, _MODES_markers, _FILESIZE_markers, _BITRATE_markers, _PACKETS_markers, _TILES_markers, _MODES_TYPE_markers = get_compression_details(image_with_markers)

                        rezie_zabezpeceni = int(_FILESIZE_markers) - int(_FILESIZE_no_markers)
                        if rezie_zabezpeceni < 0:
                            rezie_zabezpeceni = round( 100 * abs(rezie_zabezpeceni) / int(_FILESIZE_no_markers), 3) # rezie zabezpeceni v procentech
                            #rezie_zabezpeceni *= -1
                        else:
                            rezie_zabezpeceni = round( 100 * abs(rezie_zabezpeceni) / int(_FILESIZE_no_markers), 3) # rezie zabezpeceni v procentech

                        '''rezie_sop_with_markers = 0
                        rezie_eph_with_markers = 0
                        if _SOP_markers:
                            rezie_sop_with_markers = round(
                                (100 * int(_PACKETS_markers) * int(REZIE_SOP)) / int(_FILESIZE_markers), 3)
                        if _EPH_markers:
                            rezie_eph_with_markers = round(
                                (100 * int(_PACKETS_markers) * int(REZIE_EPH)) / int(_FILESIZE_markers), 3)
                        if _SEGMARK_markers:
                            # ZDROJ: ZALOŽKA VUT->BRP->BITPLANES STR 382
                            # POČET BITOVÝCH ROVIN = BITOVÁ HLOUBKA = 8
                            # počet bitových hloubek na code block se může lišit, 8 je nejhorší případ
                            # REŽIE = POČET PRECINCT * POČET CODE BLOCKS * POČET BITOVÝCH ROVIN * REZIE SEGMARK (4 BITY) = (4 * 4) * 4 * 8 * 0.5  =  256 / dlaždice
                            rezie_segmark_with_markers_byty = int(_TILES_markers) * 256
                            rezie_segmark_with_markers = round(100 * rezie_segmark_with_markers_byty / int(_FILESIZE_markers), 3)'''

                        # ZAZNAMENANI REZIE ZABEZPECOVACICH MECHANISMU
                        # 1 = None
                        # 2 = BYPASS
                        # 3 = RESET, RESTART, CAUSAL
                        # 4 = BYPASS, RESET, RESTART, CAUSAL
                        # 5 = ERTERM, SEGMARK
                        # 6 = SEGMARK
                        # 7 = BYPASS, SEGMARK
                        # 8 = RESET, RESTART, CAUSAL, SEGMARK
                        # 9 = BYPASS, RESET, RESTART, CAUSAL, SEGMARK
                        # 10 = BYPASS, RESET, RESTART, CAUSAL, SEGMARK, ERTERM
                        # 11 = SOP, EPH, BYPASS, RESET, RESTART, CAUSAL, SEGMARK
                        # 12 = SOP
                        # 13 = EPH
                        # 14 = SOP, EPH

                        if _MODES_TYPE_markers == 1:
                            graphs_data_rezie_mode_none.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 2:
                            graphs_data_rezie_mode_bypass.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 3:
                            graphs_data_rezie_mode_parallel.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 4:
                            graphs_data_rezie_mode_lazyparallel.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 5:
                            graphs_data_rezie_mode_ertermsegmark.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 6:
                            graphs_data_rezie_mode_segmark.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 7:
                            graphs_data_rezie_mode_bypasssegmark.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 8:
                            graphs_data_rezie_mode_parallelsegmark.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 9:
                            graphs_data_rezie_mode_lazyparallelsegmark.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 10:
                            graphs_data_rezie_mode_all.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 11:
                            graphs_data_rezie_mode_all.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 12:
                            graphs_data_bitrate_rezie_sop.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 13:
                            graphs_data_bitrate_rezie_eph.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")

                        elif _MODES_TYPE_markers == 14:
                            graphs_data_bitrate_rezie_sop_eph.write(str(_BITRATE_markers) + " " + str(rezie_zabezpeceni) + "\n")



                            ####################################################################################################
                        # POSKOZOVANI SOUBORU
                        ####################################################################################################

                        damage = 0.000005

                        for i in range(0, POCET_POSKOZENI):
                            SOUBORU_CELKEM += 2  # jeden s se zabezpečením a jeden bez zabezpečení
                            SOUBORU_NEDEKOMPRIMOVATELNYCH_BEZ_POSKOZENI += 1

                            chyba_pri_dekompresi_no_markers = False
                            chyba_pri_dekompresi_with_markers = False

                            print("[INFO][ ITERACE " + str(i) + " ] Poskozovani analyzovanych souboru")
                            print("* * [ NO MARKERS IMAGE ] " + str(image_no_markers))
                            print("* * [ WITH MARKERS IMAGE ] " + str(image_with_markers))

                            A_image_no_markers_damaged   = damage_image(image_no_markers, damage)
                            A_image_with_markers_damaged = damage_image(image_with_markers, damage)

                            ####################################################################################################
                            # DECOMPRESSE DAMAGED FILES
                            ####################################################################################################
                            if LIBRARY == 'kakadu':
                                # Dekomprimování poškozeného nezabezpečeného souboru
                                try:
                                    #call(["kdu_expand", "-i", str(A_image_no_markers_damaged), "-o", str(directory_decompressed_kakadu + "image_no_markers_damaged_decompressed.ppm"), "-resilient"])
                                    call(["kdu_expand", "-i", str(A_image_no_markers_damaged), "-o", str(directory_decompressed_kakadu + "image_no_markers_damaged_decompressed.ppm"), "-resilient"])
                                    A_image_no_markers_damaged_decompressed = str(directory_decompressed_kakadu + "image_no_markers_damaged_decompressed.ppm")
                                except:
                                    #graphs_data_failed_na_poskozeni_bez_ochrany.write( str(damaged_bits_image_no_markers) + "\n" )
                                    print("*[ERROR] Soubor " + str(A_image_no_markers_damaged) + " se nepodarilo dekomprimovat")

                                # Dekomprimování poškozeného zabezpečeného souboru
                                try:
                                    #call(["kdu_expand", "-i", str(A_image_with_markers_damaged), "-o", str(directory_decompressed_kakadu + "image_with_markers_damaged_decompressed.ppm"), "-resilient"])
                                    call(["kdu_expand", "-i", str(A_image_with_markers_damaged), "-o", str(directory_decompressed_kakadu + "image_with_markers_damaged_decompressed.ppm"), "-resilient"])
                                    A_image_with_markers_damaged_decompressed = str(directory_decompressed_kakadu + "image_with_markers_damaged_decompressed.ppm")
                                except:
                                    print("*[ERROR] Soubor " + str(A_image_with_markers_damaged) + " se nepodarilo dekomprimovat")

                            elif LIBRARY == 'openjpeg':
                                # Dekomprimování poškozeného nezabezpečeného souboru
                                try:
                                    call(["./lib/openjpeg/build/bin/opj_decompress", "-i", str(A_image_no_markers_damaged), "-o", str(directory_decompressed_kakadu + "image_no_markers_damaged_decompressed.ppm")])
                                    A_image_no_markers_damaged_decompressed = str(directory_decompressed_kakadu + "image_no_markers_damaged_decompressed.ppm")
                                except:
                                    print("*[ERROR] Soubor " + str(A_image_no_markers_damaged) + " se nepodarilo dekomprimovat")

                                # Dekomprimování poškozeného zabezpečeného souboru
                                try:
                                    call(["./lib/openjpeg/build/bin/opj_decompress", "-i", str(A_image_with_markers_damaged), "-o", str(directory_decompressed_kakadu + "image_with_markers_damaged_decompressed.ppm")])
                                    A_image_with_markers_damaged_decompressed = str(directory_decompressed_kakadu + "image_with_markers_damaged_decompressed.ppm")
                                except:
                                    print("*[ERROR] Soubor " + str(A_image_with_markers_damaged) + " se nepodarilo dekomprimovat")


                            # podařilo se poškozený soubor bez markerů dekomprimovat?
                            psnr_poskozeneho_bez_markeru = calculate_psnr(original_filename, str(directory_decompressed_kakadu + "image_no_markers_damaged_decompressed.ppm"))
                            if psnr_poskozeneho_bez_markeru < PRAH:
                                graphs_data_failed_na_poskozeni_bez_ochrany.write(str(damage) + "\n")
                                print("*[ERROR] Soubor " + str(A_image_no_markers_damaged) + " se nepodarilo dekomprimovat")

                            # podařilo se poškozený soubor s markery dekomprimovat?
                            psnr_poskozeneho_s_markery = calculate_psnr(original_filename, str(directory_decompressed_kakadu + "image_with_markers_damaged_decompressed.ppm"))
                            if psnr_poskozeneho_s_markery < PRAH:
                                # ZAZNAMENANI FAILS ZABEZPECOVACICH MECHANISMU
                                if _MODES_TYPE_markers == 1:
                                    graphs_data_fails_mode_none.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 2:
                                    graphs_data_fails_mode_bypass.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 3:
                                    graphs_data_fails_mode_parallel.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 4:
                                    graphs_data_fails_mode_lazyparallel.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 5:
                                    graphs_data_fails_mode_ertermsegmark.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 6:
                                    graphs_data_fails_mode_segmark.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 7:
                                    graphs_data_fails_mode_bypasssegmark.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 8:
                                    graphs_data_fails_mode_parallelsegmark.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 9:
                                    graphs_data_fails_mode_lazyparallelsegmark.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 10:
                                    graphs_data_fails_mode_all.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 11:
                                    graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 12:
                                    graphs_data_failed_na_poskozeni_sop.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 13:
                                    graphs_data_failed_na_poskozeni_eph.write(str(damage) + "\n")

                                elif _MODES_TYPE_markers == 14:
                                    graphs_data_failed_na_poskozeni_sop_eph.write(str(damage) + "\n")

                                print("*[ERROR] Soubor " + str(A_image_with_markers_damaged) + " se nepodarilo dekomprimovat")

                            try:
                                os.remove(A_image_no_markers_damaged_decompressed)
                            except:
                                print("*[ERROR] Soubor " + str(A_image_no_markers_damaged_decompressed) + " se nepodarilo odstranit")

                            try:
                                os.remove(A_image_with_markers_damaged_decompressed)
                            except:
                                print("*[ERROR] Soubor " + str(A_image_with_markers_damaged_decompressed) + " se nepodarilo odstranit")

                            damage = round( damage * 2, 6)

                    ####################################################################################################
                    # NEPODARILO SE NASTAVIT STEJNOU KVALITU PRO RUZNE ZKOMPRIMOVANE SOUBORY
                    ####################################################################################################
                    else:
                        print("*[ERROR] NEPODARILO SE NASTAVIT STEJNOU KVALITU PRO RUZNE ZKOMPRIMOVANE SOUBORY")
                        break

            ####################################################################################################
            # ZPRACOVAN SOUBOR, ZACNE SE ZPRACOVAVAT DALSI, VYTVORIM PRO NEJ SLOZKU A OTEVROU SE DATOVÉ SOUBORY
            ####################################################################################################

            graphs_data_rezie_mode_none.close()
            graphs_data_rezie_mode_bypass.close()
            graphs_data_rezie_mode_parallel.close()
            graphs_data_rezie_mode_lazyparallel.close()
            graphs_data_rezie_mode_ertermsegmark.close()
            graphs_data_rezie_mode_segmark.close()
            graphs_data_rezie_mode_bypasssegmark.close()
            graphs_data_rezie_mode_parallelsegmark.close()
            graphs_data_rezie_mode_lazyparallelsegmark.close()
            graphs_data_rezie_mode_all.close()
            graphs_data_bitrate_rezie_vsechny_mody_sop_eph.close()

            graphs_data_bitrate_rezie_sop.close()
            graphs_data_bitrate_rezie_eph.close()
            graphs_data_bitrate_rezie_sop_eph.close()
            graphs_data_bitrate_rezie_segmark.close()
            graphs_data_bitrate_rezie_sop_segmark.close()
            graphs_data_bitrate_rezie_eph_segmark.close()
            graphs_data_bitrate_rezie_sop_eph_segmark.close()

    print("*[FINISH] ANALYZA USPESNE DOKONCENA - ZPRACOVANO " + str(SOUBORU_CELKEM) + " SOUBORU")

    ####################################################################################################
    # DELETE ALL TEMPORARY FILES AND CLOSE FILES
    ####################################################################################################
    try:
        shutil.rmtree(directory_tmp)
    except:
        pass

    graphs_data_failed_na_poskozeni_bez_ochrany.close()

    graphs_data_fails_mode_none.close()
    graphs_data_fails_mode_bypass.close()
    graphs_data_fails_mode_parallel.close()
    graphs_data_fails_mode_lazyparallel.close()
    graphs_data_fails_mode_ertermsegmark.close()
    graphs_data_fails_mode_segmark.close()
    graphs_data_fails_mode_bypasssegmark.close()
    graphs_data_fails_mode_parallelsegmark.close()
    graphs_data_fails_mode_lazyparallelsegmark.close()
    graphs_data_fails_mode_all.close()
    graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph.close()

    graphs_data_failed_na_poskozeni_sop.close()
    graphs_data_failed_na_poskozeni_eph.close()
    graphs_data_failed_na_poskozeni_sop_eph.close()
    graphs_data_failed_na_poskozeni_segmark.close()
    graphs_data_failed_na_poskozeni_sop_segmark.close()
    graphs_data_failed_na_poskozeni_eph_segmark.close()
    graphs_data_failed_na_poskozeni_sop_eph_segmark.close()


    with open( graphs_data_souboru_celkem_filename, "w") as file_souboru_celkem:
        file_souboru_celkem.write(str(SOUBORU_CELKEM) + "\n")
        file_souboru_celkem.write(str(SOUBORU_NEDEKOMPRIMOVATELNYCH_BEZ_POSKOZENI) + "\n")
        file_souboru_celkem.write(str(POCET_ITERACI) + "\n")

    with open( graphs_data_library_filename, "w") as file_library:
        file_library.write(str(LIBRARY))

    ####################################################################################################
    # VYTVORENI GRAFU
    ####################################################################################################

    #plot_graphs()