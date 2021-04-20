#usr/bin/python3

#
#   Author: Marek Kovalčík, xkoval14@stud.fit.vutbr.cz
#   Bachelor thesis - Error Resilience Analysis for JPEG 2000
#   2019
#

import re
import sys
import random

# 1. Model poškození - poškození náhodně rozmístěných bitů  pocet pokoszenych bitů = velikost souboru v bitech / 50 000)
def damage_image_randomly(image, increased):
    '''Nahodne poskodi 50ti-tisicinu bitů v souboru'''

    with open(image, "rb") as img:
        byte = img.read(1)
        bytestream = bytearray()
        bitstream = list()
        new_bytestream = bytearray()
        new_bitstream = list()
        randoms = []

        while byte:
            #print(byte)
            bytestream += byte
            bitstream.append(bin(int.from_bytes(byte, 'little')))
            byte = img.read(1)

        damaged_file_name = re.sub(r".jp2$", "_d1.jp2", image)

        with open(damaged_file_name, "wb") as img_damaged:

            for element in bitstream:
                new_bitstream.append(element[2:].zfill(8))

            #print(new_bitstream)

            bit_stream_string = ''.join(new_bitstream)
            bit_stream_string2 = bit_stream_string # pro testování, zda proběhlo poškození
            #print(bit_stream_string)

            # náhodné vzorky k převrácení hodnoty
            pocet_vzorku = int(len(bit_stream_string)/10000) + 2 + increased
            #pocet_vzorku = int(len(bit_stream_string)/90000) + 2 + increased
            #pocet_vzorku = 30 + increased
            #pocet_vzorku = 10
            randoms = random.sample(range(10000, len(bit_stream_string)), pocet_vzorku)


            #print("typ: " +  str(type(bit_stream_string[55])) +  " hodnota: '" + str(bit_stream_string[55]) + "'")
            bit_stream_string_list = list(bit_stream_string)

            for index in randoms:
                if bit_stream_string_list[index] == '0':
                    #print("budu preklapet nulu na jednicku")
                    bit_stream_string_list[index] = '1'
                elif bit_stream_string_list[index] == '1':
                    bit_stream_string_list[index] = '0'
                    #print("budu preklapet jednicku na nulu")
                else:
                    pass
            bit_stream_string = ''.join(bit_stream_string_list)

            if bit_stream_string != bit_stream_string2:

                # TODO v bit_stream_string je teď poškozený soubor bitů

                tmp_bitstream = list(map(''.join, zip(*[iter(bit_stream_string)]*8)))
                #print(tmp_bitstream)

                for element in tmp_bitstream:
                  # print(int.from_bytes(bitstring_to_bytes(element[2:]), "little"))
                    new_bytestream.append(int.from_bytes(bitstring_to_bytes(element), "little"))

                #print(new_bytestream)
                img_damaged.write(new_bytestream)
                print("Succesfully damaged - ", pocet_vzorku, " bits were inverted")

            else:
                print("[ERROR] Error while damaging")

            #print(randoms)
            return damaged_file_name, pocet_vzorku

# 2. Model poškození - poškodí procentuální množství bitů dané, velikost poškození je dána parametrem size, vrací poškozený soubor
def damage_image(image, size):
    '''poškodí procentuální množství bitů dané, velikost poškození je dána parametrem size, vrací poškozený soubor'''

    with open(image, "rb") as img:
        byte = img.read(1)
        bytestream = bytearray()
        bitstream = list()
        new_bytestream = bytearray()
        new_bitstream = list()
        randoms = []

        while byte:
            # print(byte)
            bytestream += byte
            bitstream.append(bin(int.from_bytes(byte, 'little')))
            byte = img.read(1)

        damaged_file_name = re.sub(r".jp2$", "_d1.jp2", image)

        with open(damaged_file_name, "wb") as img_damaged:

            for element in bitstream:
                new_bitstream.append(element[2:].zfill(8))

            # print(new_bitstream)

            bit_stream_string = ''.join(new_bitstream)
            bit_stream_string2 = bit_stream_string  # pro testování, zda proběhlo poškození
            # print(bit_stream_string)

            # náhodné vzorky k převrácení hodnoty
            pocet_vzorku = round( int(len(bit_stream_string)) * size / 100 ) + 1
            #pocet_vzorku = 0

            randoms = random.sample(range(10000, len(bit_stream_string)), pocet_vzorku)

            # print("typ: " +  str(type(bit_stream_string[55])) +  " hodnota: '" + str(bit_stream_string[55]) + "'")
            bit_stream_string_list = list(bit_stream_string)

            for index in randoms:
                if bit_stream_string_list[index] == '0':
                    # print("budu preklapet nulu na jednicku")
                    bit_stream_string_list[index] = '1'
                elif bit_stream_string_list[index] == '1':
                    bit_stream_string_list[index] = '0'
                    # print("budu preklapet jednicku na nulu")
                else:
                    pass
            bit_stream_string = ''.join(bit_stream_string_list)

            if bit_stream_string != bit_stream_string2:

                tmp_bitstream = list(map(''.join, zip(*[iter(bit_stream_string)] * 8)))
                # print(tmp_bitstream)

                for element in tmp_bitstream:
                    # print(int.from_bytes(bitstring_to_bytes(element[2:]), "little"))
                    new_bytestream.append(int.from_bytes(bitstring_to_bytes(element), "little"))

                # print(new_bytestream)
                img_damaged.write(new_bytestream)
                print("Succesfully damaged - ", pocet_vzorku, " bits were inverted")

            else:
                print("[ERROR] Error while damaging")

            # print(randoms)
            return damaged_file_name


def bitstring_to_bytes(s):
    '''converts string of bits to bytes'''
    v = int(s, 2)
    b = bytearray()
    while v:
        b.append(v & 0xff)
        v >>= 8
    return bytes(b[::-1])

if __name__ == '__main__':
    print("File: " + str(sys.argv[1]))
    print("Damage: " + str(float(sys.argv[2])))
    damaged_file= damage_image(sys.argv[1], float(sys.argv[2]))
    print(damaged_file)

