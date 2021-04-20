#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

from Globals import *
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