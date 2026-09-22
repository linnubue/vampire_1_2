#!/bin/bash
# @author:       Mario Mech
# @description:  
# The script mirrors files and directories from uSonic-3 Cage MP 
# ftp server as operated during the VAMPIRE cruise. It is controlled 
# by cron and gets the data very night at 00:15. 
#
# FTP LOGIN
HOST='192.168.211.23'
USER='data'
PASSWORD='****'

YYYY=`date +%Y`
MM=`date +%m`
DD=`date +%d`

# REMOTE DIRECTORY
REMOTE_DIR='/DATA'

#LOCAL DIRECTORY
LOCAL_DIR='/mnt/c/Users/mirac/Documents/vampire/data/usonic'

# checking existence of daily directories

if [ ! -d $LOCAL_DIR/INSTANT/$YYYY/$MM/$DD ];then
	mkdir -p $LOCAL_DIR/INSTANT/$YYYY/$MM/$DD/
fi

if [ ! -d $LOCAL_DIR/AVERAGED/$YYYY/$MM/$DD ];then
	mkdir -p $LOCAL_DIR/AVERAGED/$YYYY/$MM/$DD
fi

# RUNTIME!
echo
echo "Starting download $REMOTE_DIR from $HOST to $LOCAL_DIR"
date

lftp -u "$USER","$PASSWORD" $HOST <<EOF
mirror  $REMOTE_DIR/INSTANT/$YYYY/$YYYY$MM/$YYYY$MM$DD/ $LOCAL_DIR/INSTANT/$YYYY/$MM/$DD/
mirror  $REMOTE_DIR/AVERAGED/$YYYY/$YYYY$MM/$YYYY$MM$DD/ $LOCAL_DIR/AVERAGED/$YYYY/$MM/$DD/
exit
EOF
echo
echo "Transfer finished"
date
