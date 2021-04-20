#!/bin/bash

# volání: ./compress_file_with_kakadu_v2.sh", str(filename), str(bitrate), str(sop), str(eph), str(modes)

filename=$1
bitrate=$2
sop=$3
eph=$4
modes=$5
directory_compressed_kakadu='tmp_jpeg2000/'

##
# KAKADU
##
#clear
#rm -rf $directory_compressed_kakadu
#mkdir $directory_compressed_kakadu
##

# Compress file
tmp=${filename%.ppm}
output_name=${filename%.ppm}

arguments='_PACKETS_SOP_EPH_SEGMARK_TILES_BITRATE_FILESIZE_MODES_kakadu.jp2'

if [ $sop == 'no' ] ; then
arguments=${arguments/_SOP/}
fi

if [ $eph == 'no' ] ; then
arguments=${arguments/_EPH/}
fi

if [[ $modes == *"BYPASS"* ]] ; then
arguments=${arguments/_MODES/_MODESBYPASS}
fi

if [[ $modes == *"RESET"* ]] ; then
arguments=${arguments/_MODES/_MODESRESET}
fi

if [[ $modes == *"CASUAL"* ]] ; then
arguments=${arguments/_MODES/_MODESCASUAL}
fi

if [[ $modes == *"RESTART"* ]] ; then
arguments=${arguments/_MODES/_MODESRESTART}
fi

if [[ $modes == *"ERTERM"* ]] ; then
arguments=${arguments/_MODES/_MODESERTERM}
fi

if [[ $modes != *"SEGMARK"* ]] ; then
arguments=${arguments/_SEGMARK/}
fi

output_name=$(grep -oP '[\w\d_]+$' <<< "$tmp")
output_name=$directory_compressed_kakadu$output_name$arguments
if [[ $modes == *"no"* ]]; then
# nejsou zapnuty cmodes
command='kdu_compress -i '$filename' -o '$output_name' Cuse_sop='$sop' Cuse_eph='$eph' -rate '$bitrate'
Creversible=no "Cblk={64,64}" Corder=RPCL "Stiles={1024,1024}" "Cprecincts={256,256},{256,256},{128,128}" ORGtparts=R Clayers=12 Clevels=5 '
else
# jsou zapnuty cmodes
command='kdu_compress -i '$filename' -o '$output_name' "Cmodes={'$modes'}" Cuse_sop='$sop' Cuse_eph='$eph' -rate '$bitrate'
Creversible=no "Cblk={64,64}" Corder=RPCL "Stiles={1024,1024}" "Cprecincts={256,256},{256,256},{128,128}" ORGtparts=R Clayers=12 Clevels=5 '
fi



echo $command
eval $command
FILESIZE=$(stat -c%s "$output_name")
tmp=$FILESIZE
FILESIZE=FILESIZE$FILESIZE
NEW_NAME=${output_name/FILESIZE/$FILESIZE}
mv $output_name $NEW_NAME
tmp_name=$NEW_NAME
width=$(identify -format "%w" $filename)
height=$(identify -format "%h" $filename)
bitrate="$(bc <<< "scale=6; ($tmp * 8 / $width / $height)" | tr . x)"
bitrate_for_name=BITRATE$bitrate
NEW_NAME=${NEW_NAME/BITRATE/$bitrate_for_name}
mv $tmp_name $NEW_NAME
echo Generated file: $NEW_NAME

decompressed_image=$directory_compressed_kakadu'decompressed.ppm'
packets=$(../lib/openjpeg/build/bin/opj_decompress -i $NEW_NAME -o $decompressed_image | grep "packets decoded" | awk '{print $5}')
echo $packets

tiles=$(../lib/openjpeg/build/bin/opj_decompress -i $NEW_NAME -o $decompressed_image | grep Tile | tail -1 | awk '{print $3}')
tiles=$(echo $tiles | sed -e 's/[1-9]\+\///')

# pridani poctu paketu do nazvu
tmp_name=$NEW_NAME
packets_for_name=PACKETS$packets
NEW_NAME=${NEW_NAME/PACKETS/$packets_for_name}
mv $tmp_name $NEW_NAME
echo Generated file with packets in name: $NEW_NAME

# pridani poctu tiles do nazvu
tmp_name=$NEW_NAME
tiles_for_name=TILES$tiles
NEW_NAME=${NEW_NAME/TILES/$tiles_for_name}
mv $tmp_name $NEW_NAME

echo Generated file with tiles in name: $NEW_NAME

echo "[INFO] bitrate : "$bitrate
echo "[INFO] tiles : "$tiles
echo "[INFO] pocet packetu : "$packets
echo "[INFO] velikost souboru : "$FILESIZE
rm $decompressed_image
echo "[INFO] soubor : "$decompressed_image" byl smazan"
echo $NEW_NAME