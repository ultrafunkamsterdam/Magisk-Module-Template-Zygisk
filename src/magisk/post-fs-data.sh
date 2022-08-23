#!/system/bin/sh

MODDIR=${0%/*}

ui_print "***********************************************"
ui_print "$0 POST-FS-DATA RUNNING"
ui_print "***********************************************"

# setprop service.adb.tcp.port 5555
# stop adbd
# start adbd

log -t Magisk "$0 POST-FS-DATA RUNNING"