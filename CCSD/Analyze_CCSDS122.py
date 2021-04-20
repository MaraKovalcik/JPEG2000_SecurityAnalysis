import os
import sys

# zobrazeni napovedy k programu
if sys.argv[1] == '-h':
    print("""argv[1]\t = vstupni zakodovany soubor
             argv[2]\t = zacatek poskozeni (pocet v bytech)
             argv[3]\t = velikost poskozeni v bytech
             *program je urcen k zakladnimu testovani, nekontroluje uzivatelsky vstup""")

else:
    input_file = sys.argv[1]
    offset = int(sys.argv[2])
    damage = int(sys.argv[3])

    file = open(input_file, "r+b" )
    corrupted_file = open( "tmp_ccsds122/damaged/offset"+str(offset)+"_damaged"+str(damage), "w+b" )

    offset_content = file.read(offset)
    corrupted_file.write(offset_content)

    input_filesize = os.path.getsize(input_file)
    #size_of_damage = round(input_filesize * damage / 100)
    size_of_damage = damage

    tmp = file.read(size_of_damage)
    for i in range(0, size_of_damage):
        corrupted_file.write(bytes(1))

    rest = file.read()
    corrupted_file.write(rest)
    corrupted_file.close()



