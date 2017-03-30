#!/bin/bash    
#cd /Users/lutz/Documents/data/FrontpageWebs/Content/LH_Home
cd /Users/lutz/Documents/data/web/hendri54.github.io/
echo "MMD batch conversion"

mmd *.mmd

cd research
mmd *.mmd
cd ..

cd econ520
mmd *.mmd
cd ..

#cd econ720
#mmd *.mmd
#cd ..

cd econ920
mmd *.mmd
cd ..

cd honors
mmd *.mmd
cd ..

cd private
mmd *.mmd
cd ..

#cd econ821
#mmd *.mmd

#cd growth
#mmd *.mmd

cd /Users/lutz/Documents/data/web/hendri54.github.io/

mmd teaching/*.mmd

mmd thoughts/*.mmd

cd /Users/lutz/Documents/data/web/hendri54.github.io/
