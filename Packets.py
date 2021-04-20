#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

import re
from subprocess import call, Popen, PIPE

def get_number_of_packets(filename):
    try:
        p = Popen(["./lib/openjpeg/build/bin/opj_decompress", "-i", str(filename), "-o", "tmp/tmp_to_calculate_packets.ppm"], stdin=PIPE, stdout=PIPE, stderr=PIPE)
        output, err = p.communicate()
        rc = p.returncode

        if (re.search(r"(?<= packets decoded = )\d+", str(output))):
            r = re.compile(r'(?<= packets decoded = )\d+')
            result = r.findall(str(output))[0]
            print("[INFO] Soubor obsahuje '" + str(result) + " paketu'\n")
            return result

        print("[INFO] Nepovedlo se ziskat pocet paketu\n")
        return 0

    except:
        print("[ERROR] Nepovedlo se ziskat pocet paketu v '" + str(filename) + "'\n")

if __name__ == '__main__':
    print(get_number_of_packets("test/bf01_rate02.jp2"))

    print(get_number_of_packets("/home/marek/Plocha/BAKALARKA/analyzator/test/0.02/bf01_PACKETS1440_SOPEPH_BITRATEx035074_FILESIZE13792_ORDERRPCL_PRECINTS512_TILE1024_LAYERS12_LEVELS5_MODEBYPASS_kakadu.jp2"))
