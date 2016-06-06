#!/bin/sh
sp=`ipa env | grep site_packages`
PLUGINS=src/plugins/*
PPATH=${sp##*:}/ipalib/plugins

for f in $PLUGINS
do
    fname=`basename $f`
    echo "Copying plugin $fname to $PPATH"
    cp $f $PPATH
done
ipactl restart
