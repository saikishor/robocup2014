#!/bin/bash

dev=$(readlink -f /media/CHANG)
echo $dev
grep -q ^$dev /proc/mounts && umount $dev
umount $dev
