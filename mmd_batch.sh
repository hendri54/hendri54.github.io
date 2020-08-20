#!/bin/bash    
#cd /Users/lutz/Documents/data/FrontpageWebs/Content/LH_Home
cd /Users/lutz/Documents/data/web/hendri54.github.io/
echo "MMD batch conversion"

mmd *.md

mmd research/*.md

#cd econ520
#mmd econ520/*.mmd
#cd ..

#cd econ720
mmd econ720/*.md
#cd ..

#cd econ920
#mmd *.mmd
#cd ..

#cd honors
# mmd honors/*.mmd
# mmd honors/instructions/*.mmd
#cd ..

#cd private
# mmd private/*.md
# mmd private/light_rail/*.md
#cd ..

mmd econ821/*.md

#cd growth
#mmd *.mmd

cd /Users/lutz/Documents/data/web/hendri54.github.io/

mmd teaching/*.md

mmd thoughts/*.md

cd /Users/lutz/Documents/data/web/hendri54.github.io/
