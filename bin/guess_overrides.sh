#!/bin/sh

# script to guess overrides in skins stuff in a product with respect to all
# others.
# useful for migration tasks etc.
#
# This script could probably be very much optimized (not a subtle way of doing)
# It displays all files under $1/'skins' subdir that bare the same name as
# a file in another product.
#
# Execute from your instance home. Sample invocation:
#
# Products/CPUtil/bin/guess_overrides.sh Products/MyProject

for x in `find Products/$1/skins -type f -printf '%f\n'`; do
    find Products -name $1 -prune -or -name $x -print;
done
