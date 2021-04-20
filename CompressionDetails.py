#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

import re

def get_compression_details(string):
    #print("[INFO] Getting compression details about: ", string)

    string = re.sub('_', '\_', string)

    _SOP = False
    _EPH = False
    _SEGMARK = False
    _MODES = []
    _FILESIZE = 1
    _BITRATE = 1
    _PACKETS = 0
    _TILES = 0
    _MODE_TYPE = 1
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


    if(re.search(r"_MODES", string)):

        used_bypass = re.search(r"BYPASS", string)
        used_reset = re.search(r"RESET", string)
        used_restart = re.search(r"RESTART", string)
        used_causal = re.search(r"CAUSAL", string)
        used_segmark = re.search(r"SEGMARK", string)
        used_erterm = re.search(r"ERTERM", string)
        used_sop = re.search(r"SOP", string)
        used_eph = re.search(r"EPH", string)


        print("used bypass:", used_bypass)
        print("used reset:", used_reset)
        print("used restart:", used_restart)
        print("used causal:", used_causal)
        print("used segmark:", used_segmark)
        print("used erterm:", used_erterm)
        print("used sop:", used_sop)
        print("used eph:", used_eph)

        if (re.search(r"SOP", string) and re.search(r"EPH", string) and re.search(r"BYPASS", string) and re.search(r"RESET", string) and re.search(r"RESTART", string) and re.search(r"CAUSAL", string) and re.search(r"SEGMARK", string)):
            _MODES.append("BYPASS")
            _MODES.append("RESET")
            _MODES.append("RESTART")
            _MODES.append("CAUSAL")
            _MODES.append("SEGMARK")
            _MODES.append("ERTERM")
            _SOP, _EPH = True, True
            _MODE_TYPE = 11

        elif (re.search(r"BYPASS", string) and re.search(r"RESET", string) and re.search(r"RESTART", string) and re.search(r"CAUSAL", string) and re.search(r"SEGMARK", string) and re.search(r"ERTERM", string)):
            _MODES.append("BYPASS")
            _MODES.append("RESET")
            _MODES.append("RESTART")
            _MODES.append("CAUSAL")
            _MODES.append("SEGMARK")
            _MODES.append("ERTERM")
            _MODE_TYPE = 10

        elif (re.search(r"BYPASS", string) and re.search(r"RESET", string) and re.search(r"RESTART", string) and re.search(r"CAUSAL", string) and re.search(r"SEGMARK", string)):
            _MODES.append("BYPASS")
            _MODES.append("RESET")
            _MODES.append("RESTART")
            _MODES.append("CAUSAL")
            _MODES.append("SEGMARK")
            _MODE_TYPE = 9

        elif (re.search(r"RESET", string) and re.search(r"RESTART", string) and re.search(r"CAUSAL", string) and re.search(r"SEGMARK", string)):
            _MODES.append("RESET")
            _MODES.append("RESTART")
            _MODES.append("CAUSAL")
            _MODES.append("SEGMARK")
            _MODE_TYPE = 8

        elif (re.search(r"BYPASS", string) and re.search(r"RESET", string) and re.search(r"RESTART", string) and re.search(r"CAUSAL", string)):
            _MODES.append("BYPASS")
            _MODES.append("RESET")
            _MODES.append("RESTART")
            _MODES.append("CAUSAL")
            _MODE_TYPE = 4

        elif (re.search(r"RESET", string) and re.search(r"RESTART", string) and re.search(r"CAUSAL", string)):
            _MODES.append("RESET")
            _MODES.append("RESTART")
            _MODES.append("CAUSAL")
            _MODE_TYPE = 3

        elif (re.search(r"ERTERM", string) and re.search(r"SEGMARK", string)):
            _MODES.append("ERTERM")
            _MODES.append("SEGMARK")
            _MODE_TYPE = 5

        elif (re.search(r"BYPASS", string) and re.search(r"SEGMARK", string)):
            _MODES.append("BYPASS")
            _MODES.append("SEGMARK")
            _MODE_TYPE = 7

        elif (re.search(r"SEGMARK", string)):
            _MODES.append("SEGMARK")
            _MODE_TYPE = 6

        elif (re.search(r"BYPASS", string)):
            _MODES.append("BYPASS")
            _MODE_TYPE = 2

        else:
            _MODE_TYPE = 1

    if _MODE_TYPE != 11:
        if (re.search(r"SOP", string) and re.search(r"EPH", string)):
            _SOP, _EPH = True, True
            _MODE_TYPE = 14
        elif (re.search(r"SOP", string)):
            _SOP = True
            _MODE_TYPE = 12
        elif (re.search(r"EPH", string)):
            _EPH = True
            _MODE_TYPE = 13

    if (re.search(r"_FILESIZE", string)):
        r = re.compile(r'(?<=_FILESIZE)\d+')
        _FILESIZE = r.findall(string)[0]
    if (re.search(r"_BITRATE", string)):
        r = re.compile(r'(?<=_BITRATE)[0-9x]+')
        _BITRATE = r.findall(string)[0]
        if _BITRATE[0] == 'x':
            _BITRATE = re.sub("x", "0.", _BITRATE)
        if re.search("x", _BITRATE):
            _BITRATE = re.sub("x", ".", _BITRATE)

    if (re.search(r"_PACKETS", string)):
        try:
            r = re.compile(r'(?<=_PACKETS)\d+')
            _PACKETS = r.findall(string)[0]
        except:
            _PACKETS = 0
    if (re.search(r"_TILES", string)):
        try:
            r = re.compile(r'(?<=_TILES)\d+')
            _TILES = r.findall(string)[0]
        except:
            _TILES = 0

    return _SOP,_EPH, _SEGMARK, _MODES, _FILESIZE, _BITRATE, _PACKETS, _TILES, _MODE_TYPE



if __name__ == '__main__':
    string = "tmp/compressed_kakadu/bf01_PACKETS3024_SOP_SEGMARK_TILES4_BITRATE1x171585_FILESIZE460686_MODESBYPASS_kakadu_d1.jp2"

    _SOP,_EPH, _SEGMARK, _MODES, _FILESIZE, _BITRATE, _PACKETS, _TILES, _MODE_TYPE = get_compression_details(string)

    print("SOP: " + str(_SOP))
    print("EPH: " + str(_EPH))
    print("SEGMARK: " + str(_SEGMARK))
    print("MODES: " + str(_MODES))
    print("POCET MODU: " + str(len(_MODES)))
    if 'SEGMARK' in _MODES:
        print("POUZITY SEGMARK: YES")
    print("FILESIZE: " + str(_FILESIZE))
    print("BITRATE: " + str(_BITRATE))
    print("PACKETS: " + str(_PACKETS))
    print("TILES: " + str(_TILES))
    print("MODE TYPE: " + str(_MODE_TYPE))