import re
import os
import shutil
import sys
import subprocess
from PSNRCalculator import calculate_psnr

'''Tento skript zkomprimuje soubor s nejlepším možným zabezpečením pro JPEG 2000 a CCSD, následně
provede velké poškození souboru. během tohoto poškození bude přepsán souvislý blok např nulami. Velikost tohoto bloku bude 
10 - 50 %. Bude zde analyzováno jak si s takto velkým poškozením poradí JPEG 2000 a knihovna Kakadu a formát CCSD'''

print("[INFO] Test JPEG 2000 ( Kakadu ) vs. CCSDS  122.0")

def compress_JP2(filename, bitrate ):
    '''zkomprimuje obrázek 'filename' knihovnou kakadu'''
    try:
        print("[INFO] KAKADU: Komprese pomocí skriptu 'compress_JP2.sh'")
        compressed_filename = subprocess.check_output(["./compress_JP2.sh", str(filename), str(bitrate), str("yes"), str("yes"), str('BYPASS|ERTERM|RESET|RESTART|SEGMARK')])
    except:
        print("[ERROR] Nepovedlo se zkomprimovat soubor '" + str(filename) + "' knihovnou KAKADU")
        compressed_filename = None
        exit()

    compressed_filename = compressed_filename.split()[-1]
    compressed_filename = str(compressed_filename)[2:]
    compressed_filename = compressed_filename[:-1]

    return str(compressed_filename)

def expand_JP2(filename, output_name):
    '''Dekomprimuje poškozený JP2 soubor'''
    try:
        subprocess.call(["kdu_expand", "-i", str(filename), "-o",str(output_name), "-resilient"])
    except:
        print("*" + str(filename) + "*[ERROR] Soubor nepodarilo dekomprimovat")
    return output_name

def bitstring_to_bytes(s):
    '''předělá proud bitů na byty, použito při poškození souboru'''
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

def damage_JP2(filename, size):
    '''přepíše souvislou část dat v souboru nulami, velikost této části je dána parametrem size (v % ), poškození začíná za polovinou souboru'''

    print("[INFO] poskozovani souboru ", filename)

    with open(filename, "rb") as img:
        byte = img.read(1)
        bytestream = bytearray()
        bitstream = list()
        new_bytestream = bytearray()
        new_bitstream = list()

        while byte:
            # print(byte)
            bytestream += byte
            bitstream.append(bin(int.from_bytes(byte, 'little')))
            byte = img.read(1)

        damaged_file_name = re.sub(r".jp2$", "_d" + str(size) + ".jp2", filename)

        with open(damaged_file_name, "wb") as img_damaged:

            for element in bitstream:
                new_bitstream.append(element[2:].zfill(8))

            # print(new_bitstream)

            bit_stream_string = ''.join(new_bitstream)
            bit_stream_string2 = bit_stream_string  # pro testování, zda proběhlo poškození
            # print(bit_stream_string)

            # počet vzorků je dán procentuálně parametrem size
            pocet_vzorku = round(int(len(bit_stream_string)) * size / 100)
            # začátek poškození je v polovině souboru
            zacatek_poskozeni = int(len(bit_stream_string)) / 2

            # print("typ: " +  str(type(bit_stream_string[55])) +  " hodnota: '" + str(bit_stream_string[55]) + "'")
            bit_stream_string_list = list(bit_stream_string)

            # přepis vzorku na nulu
            for el in range(0, pocet_vzorku):
                index = int(zacatek_poskozeni + el)
                #print(index)
                bit_stream_string_list[index] = '0'

            bit_stream_string = ''.join(bit_stream_string_list)

            if bit_stream_string != bit_stream_string2:

                tmp_bitstream = list(map(''.join, zip(*[iter(bit_stream_string)] * 8)))
                # print(tmp_bitstream)

                for element in tmp_bitstream:
                    # print(int.from_bytes(bitstring_to_bytes(element[2:]), "little"))
                    new_bytestream.append(int.from_bytes(bitstring_to_bytes(element), "little"))

                # print(new_bytestream)
                img_damaged.write(new_bytestream)
                print("[INFO] Uspesne poskozeno - ", pocet_vzorku, " bitu poskozeno")

            else:
                print("[ERROR] Chyba pri poskozovani")

            # print(randoms)
            return damaged_file_name

if __name__ == '__main__':

    if sys.argv[1] == '-h':
        print("""argv[1]\t = vstupni obraz ve formatu ppm ve stupnich sedi
                     *program je urcen k zakladnimu testovani, nekontroluje uzivatelsky vstup""")

    '''Zpracování obrazu = komprese, poškození, dekomprese, psnr'''
    try:
        shutil.rmtree('tmp_jpeg2000')
        shutil.makedirs('tmp_jpeg2000')
    except:
        os.makedirs('tmp_jpeg2000/')

    ORIGINAL = sys.argv[1]
    BITRATE = 1.0

    # JPEG 2000
    limit_jpeg2000 = 0

    img_jp2     = compress_JP2(ORIGINAL, BITRATE)
    img_jp2_dx1 = damage_JP2(img_jp2, 0.1)
    img_jp2_dx3 = damage_JP2(img_jp2, 0.3)
    img_jp2_dx5 = damage_JP2(img_jp2, 0.5)
    img_jp2_dx7 = damage_JP2(img_jp2, 0.7)
    img_jp2_dx8 = damage_JP2(img_jp2, 0.8)  # 0.7% poškození, experimentálně zjištěno jako hranice pro úspěšný výpočet PSNR ( pro bitrate = 1.0)
    img_jp2_d10 = damage_JP2(img_jp2, 10)   # 10% poškození
    img_jp2_d20 = damage_JP2(img_jp2, 20)   # 20% poškození
    img_jp2_d30 = damage_JP2(img_jp2, 30)   # 30% poškození
    img_jp2_d40 = damage_JP2(img_jp2, 40)   # 40% poškození

    img_jp2_dx1_decompressed = expand_JP2(img_jp2_dx1, 'tmp_jpeg2000/img_jp2_dx1.ppm')
    img_jp2_dx3_decompressed = expand_JP2(img_jp2_dx3, 'tmp_jpeg2000/img_jp2_dx3.ppm')
    img_jp2_dx5_decompressed = expand_JP2(img_jp2_dx5, 'tmp_jpeg2000/img_jp2_dx5.ppm')
    img_jp2_dx7_decompressed = expand_JP2(img_jp2_dx7, 'tmp_jpeg2000/img_jp2_dx7.ppm')
    img_jp2_dx8_decompressed = expand_JP2(img_jp2_dx8, 'tmp_jpeg2000/img_jp2_dx8.ppm')
    img_jp2_d10_decompressed = expand_JP2(img_jp2_d10, 'tmp_jpeg2000/img_jp2_d10.ppm')
    img_jp2_d20_decompressed = expand_JP2(img_jp2_d20, 'tmp_jpeg2000/img_jp2_d20.ppm')
    img_jp2_d30_decompressed = expand_JP2(img_jp2_d30, 'tmp_jpeg2000/img_jp2_d30.ppm')
    img_jp2_d40_decompressed = expand_JP2(img_jp2_d40, 'tmp_jpeg2000/img_jp2_d40.ppm')

    if calculate_psnr(ORIGINAL, img_jp2_dx1_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_dx1_decompressed))
        limit_jpeg2000 = 0.1
    if calculate_psnr(ORIGINAL, img_jp2_dx3_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_dx3_decompressed))
        limit_jpeg2000 = 0.3
    if calculate_psnr(ORIGINAL, img_jp2_dx5_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_dx5_decompressed))
        limit_jpeg2000 = 0.5
    if calculate_psnr(ORIGINAL, img_jp2_dx7_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_dx7_decompressed))
        limit_jpeg2000 = 0.7
    if calculate_psnr(ORIGINAL, img_jp2_dx8_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_dx8_decompressed))
        limit_jpeg2000 = 0.8
    if calculate_psnr(ORIGINAL, img_jp2_d10_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_d10_decompressed))
        limit_jpeg2000 = 10
    if calculate_psnr(ORIGINAL, img_jp2_d20_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_d20_decompressed))
        limit_jpeg2000 = 20
    if calculate_psnr(ORIGINAL, img_jp2_d30_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_d30_decompressed))
        limit_jpeg2000 = 30
    if calculate_psnr(ORIGINAL, img_jp2_d40_decompressed) > 0:
        print(calculate_psnr(ORIGINAL, img_jp2_d40_decompressed))
        limit_jpeg2000 = 40

    # Vysledky
    print(" *** KAKADU, jpeg 2000")
    print("Hranicni poskozeni = " + str(limit_jpeg2000) + " %")
