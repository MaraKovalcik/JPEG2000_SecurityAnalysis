#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

####################################################################################################
# Globální proměnné
####################################################################################################

directory = '.'
directory_tmp = 'tmp'
directory_graphs_data = 'output/graphs_data/'
directory_graphs_data_agreg = 'output/graphs_data/agreg/'
directory_graphs = 'output/graphs/'
directory_graphs_inv_bits_psnr = 'output/graphs/inv_bits_psnr/'
directory_reference_kakadu = 'tmp/reference_kakadu/'
directory_compressed_kakadu = 'tmp/compressed_kakadu/'
directory_decompressed_kakadu = 'tmp/decompressed_kakadu/'
directory_output = 'output'
ppm_pattern = '*.ppm'
jp2_pattern = '*.jp2'


# Proměnné pro zjištění nastavení komprimace souboru podle jména
# příklad: *_SOP_EPH_ORDERRPCL_TILE1024_RATE1.2_LAYERS12_LEVELS5_MODEBYPASS_kakadu.jp2
SOP_USED = False
EPH_USED = False
SOP_EPH_USED = False
ORDER = 'X'
TILE = 1024
RATIO = 1
LAYERS = 1
LEVELS = 1
MODE = 'X'
BLOCK = '64x64'
FILESIZE = 1
ORIGINAL_FILESIZE = 1
POMER_ORGINAL_NEW = 1.0
BITRATE = 'X'
PACKETS = 0
PRECINTS = 0
procentualni_zmenseni = 0

# uchování jména a velikosti referečního souboru
reference_filesize_kakadu = 1
reference_filename_kakadu = None

####################################################################################################
# Pomocné funkce
####################################################################################################

# Resetuje stav proměnných pro získání informací o nastavení komprese
def reset_compression_details_variables():
    global SOP_USED, EPH_USED, ORDER, TILE, RATIO, LAYERS, LEVELS, MODE, BLOCK, procentualni_zmenseni, BITRATE
    SOP_USED = False
    EPH_USED = False
    ORDER = None
    TILE = None
    RATIO = None
    LAYERS = None
    LEVELS = None
    MODE = None
    BLOCK = None
    BITRATE = None
    PACKETS = 0
    procentualni_zmenseni = None

# Vrátí procentuální zvětšení soubrou filesize2 oproti filesize1
def get_procentualni_zmenseni(original, new):
    tmp = int(original) - int(new)
    result = round((100 * tmp) / float(original), 3)
    return abs(result)

# Vrátí procentuální zvětšení soubrou s markery oproti bez markerů
def get_procentualni_zvetseni(bezmarkeru, smarkery):
    rozdil = abs(int(smarkery) - int(bezmarkeru))
    result = round((100 * rozdil) / float(bezmarkeru), 3)
    return abs(result)

# zapíše hodnoty do výstupního souboru
def write_output(output_file, LIB, reference_filename_for_output, SOP_EPH_USED, COMPRESSED_FILESIZE, procentualni_zmenseni, DAMAGE_TYPE, pocet_invertovanych_bitu, BITRATE, finalPSNR):
    output_file.write(str(LIB) + " & " + str(reference_filename_for_output) + " & " + str(SOP_EPH_USED) + " & " + str(COMPRESSED_FILESIZE)+ " & " + str(procentualni_zmenseni) + " & " + str(DAMAGE_TYPE) + " & " + str(pocet_invertovanych_bitu) + " & " + str(BITRATE) + " & " + str(round(finalPSNR,3)) + "\\\\ \\hline\n")
    reset_compression_details_variables()


####################################################################################################
# DEFINICE VÝSTUPNÍCH DATOVÝCH SOURBOŮ GRAFŮ
####################################################################################################

# soubor obsahující název použité knihony
graphs_data_library_filename = 'output/library'

# datové soubory pro agregaci stupnování poškození, uložen je vždy počet bitů u kterého se nepovedla dekomprese
graphs_data_failed_na_poskozeni_bez_ochrany_filename          = 'output/graphs_data/poskozeni_bez_ochrany.dat'
graphs_data_failed_na_poskozeni_sop_filename                  = 'output/graphs_data/poskozeni_sop.dat'
graphs_data_failed_na_poskozeni_eph_filename                  = 'output/graphs_data/poskozeni_eph.dat'
graphs_data_failed_na_poskozeni_sop_eph_filename              = 'output/graphs_data/poskozeni_sop_eph.dat'
graphs_data_failed_na_poskozeni_segmark_filename              = 'output/graphs_data/poskozeni_segmark.dat'
graphs_data_failed_na_poskozeni_sop_segmark_filename          = 'output/graphs_data/poskozeni_sop_segmark.dat'
graphs_data_failed_na_poskozeni_eph_segmark_filename          = 'output/graphs_data/poskozeni_eph_segmark.dat'
graphs_data_failed_na_poskozeni_sop_eph_segmark_filename      = 'output/graphs_data/poskozeni_sop_eph_segmark.dat'

# datové soubory pro rezii a zvetseni souboru
bitrate_rezie_sop_filename              = 'bitrate_rezie_sop.dat'
bitrate_rezie_eph_filename              = 'bitrate_rezie_eph.dat'
bitrate_rezie_sop_eph_filename          = 'bitrate_rezie_sop_eph.dat'
bitrate_rezie_segmark_filename          = 'bitrate_rezie_segmark.dat'
bitrate_rezie_sop_segmark_filename      = 'bitrate_rezie_sop_segmark.dat'
bitrate_rezie_eph_segmark_filename      = 'bitrate_rezie_eph_segmark.dat'
bitrate_rezie_sop_eph_segmark_filename  = 'bitrate_rezie_sop_eph_segmark.dat'

# DATOVÉ SOUBORY S AGREGOVANÝMI VÝSLEDKY PRO POUŽITÍ S MARKERY

graphs_data_failed_na_poskozeni_bez_ochrany_agreg_filename          = 'output/graphs_data/agreg/poskozeni_bez_ochrany.agreg'
graphs_data_failed_na_poskozeni_sop_agreg_filename                  = 'output/graphs_data/agreg/poskozeni_sop.agreg'
graphs_data_failed_na_poskozeni_eph_agreg_filename                  = 'output/graphs_data/agreg/poskozeni_eph.agreg'
graphs_data_failed_na_poskozeni_sop_eph_agreg_filename              = 'output/graphs_data/agreg/poskozeni_sop_eph.agreg'
graphs_data_failed_na_poskozeni_segmark_agreg_filename              = 'output/graphs_data/agreg/poskozeni_segmark.agreg'
graphs_data_failed_na_poskozeni_sop_segmark_agreg_filename          = 'output/graphs_data/agreg/poskozeni_sop_segmark.agreg'
graphs_data_failed_na_poskozeni_eph_segmark_agreg_filename          = 'output/graphs_data/agreg/poskozeni_eph_segmark.agreg'
graphs_data_failed_na_poskozeni_sop_eph_segmark_agreg_filename      = 'output/graphs_data/agreg/poskozeni_sop_eph_segmark.agreg'

graphs_data_bitrate_rezie_sop_agreg_filename              = 'output/graphs_data/agreg/bitrate_rezie_sop.agreg'
graphs_data_bitrate_rezie_eph_agreg_filename              = 'output/graphs_data/agreg/bitrate_rezie_eph.agreg'
graphs_data_bitrate_rezie_sop_eph_agreg_filename          = 'output/graphs_data/agreg/bitrate_rezie_sop_eph.agreg'
graphs_data_bitrate_rezie_segmark_agreg_filename          = 'output/graphs_data/agreg/bitrate_rezie_segmark.agreg'
graphs_data_bitrate_rezie_sop_segmark_agreg_filename      = 'output/graphs_data/agreg/bitrate_rezie_sop_segmark.agreg'
graphs_data_bitrate_rezie_eph_segmark_agreg_filename      = 'output/graphs_data/agreg/bitrate_rezie_eph_segmark.agreg'
graphs_data_bitrate_rezie_sop_eph_segmark_agreg_filename  = 'output/graphs_data/agreg/bitrate_rezie_sop_eph_segmark.agreg'

# DATOVÉ SOUBORY S AGREGOVANÝMI VÝSLEDKY PRO POUŽITÍ S MODY

graphs_data_bitrate_rezie_reset_filename              = 'bitrate_rezie_reset.dat'
graphs_data_bitrate_rezie_restart_filename            = 'bitrate_rezie_restart.dat'
graphs_data_bitrate_rezie_segmark_filename            = 'bitrate_rezie_segmark.dat'
graphs_data_bitrate_rezie_erterm_filename             = 'bitrate_rezie_erterm.dat'
graphs_data_bitrate_rezie_vsechny_mody_filename       = 'bitrate_rezie_vsechny_mody.dat'

graphs_data_bitrate_rezie_reset_agreg_filename              = 'output/graphs_data/agreg/bitrate_rezie_reset.agreg'
graphs_data_bitrate_rezie_restart_agreg_filename            = 'output/graphs_data/agreg/bitrate_rezie_restart.agreg'
graphs_data_bitrate_rezie_segmark_agreg_filename            = 'output/graphs_data/agreg/bitrate_rezie_segmark.agreg'
graphs_data_bitrate_rezie_erterm_agreg_filename             = 'output/graphs_data/agreg/bitrate_rezie_erterm.agreg'
graphs_data_bitrate_rezie_vsechny_mody_agreg_filename       = 'output/graphs_data/agreg/bitrate_rezie_vsechny_mody.agreg'

graphs_data_failed_na_poskozeni_reset_filename              = 'output/graphs_data/poskozeni_reset.dat'
graphs_data_failed_na_poskozeni_restart_filename            = 'output/graphs_data/poskozeni_restart.dat'
graphs_data_failed_na_poskozeni_segmark_filename            = 'output/graphs_data/poskozeni_segmark.dat'
graphs_data_failed_na_poskozeni_erterm_filename             = 'output/graphs_data/poskozeni_erterm.dat'
graphs_data_failed_na_poskozeni_vsechny_mody_filename       = 'output/graphs_data/poskozeni_vsechny_mody.dat'

graphs_data_failed_na_poskozeni_reset_agreg_filename              = 'output/graphs_data/agreg/poskozeni_reset.agreg'
graphs_data_failed_na_poskozeni_restart_agreg_filename            = 'output/graphs_data/agreg/poskozeni_restart.agreg'
graphs_data_failed_na_poskozeni_segmark_agreg_filename            = 'output/graphs_data/agreg/poskozeni_segmark.agreg'
graphs_data_failed_na_poskozeni_erterm_agreg_filename             = 'output/graphs_data/agreg/poskozeni_erterm.agreg'
graphs_data_failed_na_poskozeni_vsechny_mody_agreg_filename       = 'output/graphs_data/agreg/poskozeni_vsechny_mody.agreg'

graphs_data_bitrate_rezie_vsechny_mody_sop_eph_filename           = 'bitrate_rezie_vsechny_mody_sop_eph.dat'
graphs_data_bitrate_rezie_vsechny_mody_sop_eph_agreg_filename     = 'output/graphs_data/agreg/bitrate_rezie_vsechny_mody_sop_eph.agreg'
graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph_filename           = 'output/graphs_data/poskozeni_vsechny_mody_sop_eph.dat'
graphs_data_failed_na_poskozeni_vsechny_mody_sop_eph_agreg_filename     = 'output/graphs_data/agreg/poskozeni_vsechny_mody_sop_eph.agreg'

graphs_zabezpeceni_a_rezie_filename   = 'output/graphs/zabezpeceni_a_rezie.pdf'

graphs_data_souboru_celkem_filename      = 'output/graphs_data/souboru_celkem.dat'


PARAMETRY_KOMPRESE = [
                        # 1. varianta
                        ('yes', 'no', 'BYPASS'), ('no', 'yes', 'BYPASS'), ('yes', 'yes', 'BYPASS'), ('yes', 'no',  'BYPASS|SEGMARK'),
                        ('no', 'yes', 'BYPASS|SEGMARK'), ('yes', 'yes', 'BYPASS|SEGMARK'),
                        # 2. varianta
                        ('no', 'no', 'BYPASS|RESET'),  ('no', 'no','BYPASS|RESTART'), ('no', 'no', 'BYPASS|SEGMARK'),
                        ('no', 'no', 'BYPASS|ERTERM'),
                        ('no', 'no', 'BYPASS|ERTERM|RESET|RESTART|SEGMARK'),
                        # 3. varianta
                        ('yes', 'yes', 'BYPASS|ERTERM|RESET|RESTART|SEGMARK')
                      ]

PARAMETRY_KOMPRESE1 = [
                        # 1. varianta
                        ('yes', 'no', 'BYPASS'), ('no', 'yes', 'BYPASS'), ('yes', 'yes', 'BYPASS'),
                        ('no', 'no',  'BYPASS|SEGMARK'), ('yes', 'no',  'BYPASS|SEGMARK'),
                        ('no', 'yes', 'BYPASS|SEGMARK'), ('yes', 'yes', 'BYPASS|SEGMARK'),

                      ]

PARAMETRY_KOMPRESE2 = [
                        # 2. varianta
                        ('no', 'no', 'BYPASS|RESET'),  ('no', 'no','BYPASS|RESTART'), ('no', 'no', 'BYPASS|SEGMARK'), ('no', 'no', 'BYPASS|ERTERM'),
                        ('no', 'no', 'BYPASS|ERTERM|RESET|RESTART|SEGMARK'),
                      ]

PARAMETRY_KOMPRESE3 = [
                        # 3. varianta
                        ('yes', 'yes', 'BYPASS|CAUSAL|RESET|RESTART|SEGMARK')
                      ]

PARAMETRY_KOMPRESE4 = [
                        ('no', 'no', 'no'),
                        ('no', 'no', 'BYPASS'),
                        ('no', 'no', 'RESET|RESTART|CAUSAL'),
                        ('no', 'no', 'BYPASS|RESET|RESTART|CAUSAL'),
                        ('no', 'no', 'SEGMARK'),
                        ('no', 'no', 'ERTERM|SEGMARK'),
                        ('no', 'no', 'RESET'),
                        ('no', 'no', 'RESET|RESTART|CAUSAL|SEGMARK'),
                        ('no', 'no', 'BYPASS|RESET|RESTART|CAUSAL|SEGMARK'),
                        ('no', 'no', 'BYPASS|RESET|RESTART|CAUSAL|SEGMARK|ERTERM')
                      ]

# Datové soubory pro analýzu módů
graphs_data_rezie_mode_none_filename = 'rezie_mode_none.dat'
graphs_data_rezie_mode_none_agreg_filename = 'output/graphs_data/agreg/rezie_mode_none.agreg'
graphs_data_fails_mode_none_filename = 'output/graphs_data/fails_mode_none.dat'
graphs_data_fails_mode_none_agreg_filename = 'output/graphs_data/agreg/fails_mode_none.agreg'

graphs_data_rezie_mode_bypass_filename = 'rezie_mode_bypass.dat'
graphs_data_rezie_mode_bypass_agreg_filename = 'output/graphs_data/agreg/rezie_mode_bypass.agreg'
graphs_data_fails_mode_bypass_filename = 'output/graphs_data/fails_mode_bypass.dat'
graphs_data_fails_mode_bypass_agreg_filename = 'output/graphs_data/agreg/fails_mode_bypass.agreg'

graphs_data_rezie_mode_parallel_filename = 'rezie_mode_parallel.dat'
graphs_data_rezie_mode_parallel_agreg_filename = 'output/graphs_data/agreg/rezie_mode_parallel.agreg'
graphs_data_fails_mode_parallel_filename = 'output/graphs_data/fails_mode_parallel.dat'
graphs_data_fails_mode_parallel_agreg_filename = 'output/graphs_data/agreg/fails_mode_parallel.agreg'

graphs_data_rezie_mode_lazyparallel_filename = 'rezie_mode_lazyparallel.dat'
graphs_data_rezie_mode_lazyparallel_agreg_filename = 'output/graphs_data/agreg/rezie_mode_lazyparallel.agreg'
graphs_data_fails_mode_lazyparallel_filename = 'output/graphs_data/fails_mode_lazyparallel.dat'
graphs_data_fails_mode_lazyparallel_agreg_filename= 'output/graphs_data/agreg/fails_mode_lazyparallel.agreg'

graphs_data_rezie_mode_ertermsegmark_filename = 'rezie_mode_ertermsegmark.dat'
graphs_data_rezie_mode_ertermsegmark_agreg_filename = 'output/graphs_data/agreg/rezie_mode_ertermsegmark.agreg'
graphs_data_fails_mode_ertermsegmark_filename = 'output/graphs_data/fails_mode_ertermsegmark.dat'
graphs_data_fails_mode_ertermsegmark_agreg_filename = 'output/graphs_data/agreg/fails_mode_ertermsegmark.agreg'

graphs_data_rezie_mode_segmark_filename = 'rezie_mode_segmark.dat'
graphs_data_rezie_mode_segmark_agreg_filename = 'output/graphs_data/agreg/rezie_mode_segmark.agreg'
graphs_data_fails_mode_segmark_filename = 'output/graphs_data/fails_mode_segmark.dat'
graphs_data_fails_mode_segmark_agreg_filename = 'output/graphs_data/agreg/fails_mode_segmark.agreg'

graphs_data_rezie_mode_bypasssegmark_filename = 'rezie_mode_bypasssegmark.dat'
graphs_data_rezie_mode_bypasssegmark_agreg_filename = 'output/graphs_data/agreg/rezie_mode_bypasssegmark.agreg'
graphs_data_fails_mode_bypasssegmark_filename = 'output/graphs_data/fails_mode_bypasssegmark.dat'
graphs_data_fails_mode_bypasssegmark_agreg_filename = 'output/graphs_data/agreg/fails_mode_bypasssegmark.agreg'

graphs_data_rezie_mode_parallelsegmark_filename = 'rezie_mode_parallelsegmark.dat'
graphs_data_rezie_mode_parallelsegmark_agreg_filename = 'output/graphs_data/agreg/rezie_mode_parallelsegmark.agreg'
graphs_data_fails_mode_parallelsegmark_filename = 'output/graphs_data/fails_mode_parallelsegmark.dat'
graphs_data_fails_mode_parallelsegmark_agreg_filename = 'output/graphs_data/agreg/fails_mode_parallelsegmark.agreg'

graphs_data_rezie_mode_lazyparallelsegmark_filename = 'rezie_mode_lazyparallelsegmark.dat'
graphs_data_rezie_mode_lazyparallelsegmark_agreg_filename = 'output/graphs_data/agreg/rezie_mode_lazyparallelsegmark.agreg'
graphs_data_fails_mode_lazyparallelsegmark_filename = 'output/graphs_data/fails_mode_lazyparallelsegmark.dat'
graphs_data_fails_mode_lazyparallelsegmark_agreg_filename = 'output/graphs_data/agreg/fails_mode_lazyparallelsegmark.agreg'

graphs_data_rezie_mode_all_filename = 'rezie_mode_all.dat'
graphs_data_rezie_mode_all_agreg_filename = 'output/graphs_data/agreg/rezie_mode_all.agreg'
graphs_data_fails_mode_all_filename = 'output/graphs_data/fails_mode_all.dat'
graphs_data_fails_mode_all_agreg_filename = 'output/graphs_data/agreg/fails_mode_all.agreg'