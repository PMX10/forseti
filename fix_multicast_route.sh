#!/bin/bash
#
# fix_multicast_route.sh
#
# Fixes the route for UDP Multicast to go to eth0 rather than wlan0 (would be used for airbears)

sudo route add -net 239.255.76.67 netmask 255.255.255.255 dev eth0

