#!/bin/bash

current_datetime=$date
year=$(date -d "$current_datetime" +"%Y")
#$(/usr/bin/date '+%Y')
month=$(date -d "$current_datetime" +"%m")
#(/usr/bin/date '+%m')
day=$(date -d "$current_datetime" +"%d")
#$(/usr/bin/date '+%d')
hourmin=$(date -d "$current_datetime" +"%H%M")
#echo $hourmin
#echo $current_datetime
#$(/usr/bin/date '+%H%M')

timestamp=$(date +'%Y%m%d%H%M')
echo --- $timestamp ---

url="http://192.168.211.21/record/current.jpg"

archivePath="/home/mirac/mobotix/data"
#C:/Users/Mirac/Documents/vampire/mobotix/data"
programDir="/home/mirac/mobotix" 
tmpDir="/home/mirac/mobotix/downloads"
#"C:/Users/Mirac/Downloads"

localFullPath="$archivePath/$year/$month/$day"

prefix="ps_144_skycam_"
fileName=$prefix$timestamp.jpg

/bin/mkdir -p $localFullPath
/home/mirac/anaconda3/bin/curl -s $url --connect-timeout 5 > $tmpDir/current1.jpg
if [ $? -eq 0 ]
then
	if [[ $(file -b $tmpDir/current1.jpg |awk '{print $1}') == "JPEG" ]]
	then
		echo "picture downloaded"
		/bin/mv $tmpDir/current1.jpg $localFullPath/$fileName
	else
		echo "file downloaded but not an image"
                /bin/cp $programDir/no-image.jpg $localFullPath/$fileName
	fi
else
	echo "cannot connect to camera"
	/bin/cp $programDir/no-image.jpg $localFullPath/$fileName
fi

echo done.
