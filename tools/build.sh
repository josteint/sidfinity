#!/bin/bash
# Build siddump and libsidplayfp from source
# Run from repo root: bash tools/build.sh
set -e
cd "$(dirname "$0")"

CXXFLAGS="-std=c++17 -O2 -DNDEBUG -DHAVE_CONFIG_H"
INCFLAGS="-I libsidplayfp/src -I libsidplayfp/src/builders/sidlite-builder"

# --- Step 1: Clone dependencies if needed ---

if [ ! -d "xa65/xa/Makefile" ] && [ ! -f "xa65/xa/xa" ]; then
    echo "Cloning and building xa65..."
    mkdir -p xa65
    git clone https://github.com/af65/xa65.git xa65/xa
    cd xa65/xa && make -j$(nproc) && cd ../..
fi

if [ ! -d "libsidplayfp/src" ]; then
    echo "Cloning libsidplayfp..."
    git clone https://github.com/libsidplayfp/libsidplayfp.git
fi

# sidid — HVSC playroutine identifier; produces tools/sidid_full.txt, the
# engine column of the catalogue. PATCHED: upstream truncates paths to 56
# chars for display, which silently drops 2.3% of HVSC from a dump consumed
# as a {path: engine} map. Re-cloning without the patch reintroduces that.
if [ ! -f "sidid/sidid" ]; then
    echo "Cloning and building sidid..."
    if [ ! -d "sidid/.git" ]; then
        git clone https://github.com/cadaver/sidid.git sidid
        (cd sidid && git apply ../sidid_no_truncate.patch)
    fi
    (cd sidid && gcc sidid.c -Wall -O3 -o sidid)
    echo "  Built tools/sidid/sidid"
fi

# --- Step 2: Apply overlay (our modifications) ---

echo "Applying overlay files..."
cp -r libsidplayfp-overlay/src/* libsidplayfp/src/

# --- Step 3: Build libsidplayfp ---

echo "Building libsidplayfp..."
mkdir -p libsidplayfp/build
cd libsidplayfp/build
SRCS=$(find ../src -name "*.cpp" | grep -v test | grep -v utils | grep -v exsid | grep -v residfp | grep -v usbsid | sort)
for f in $SRCS; do
    oname="$(echo $f | sed 's|^\.\./||; s|/|_|g; s|\.cpp$|.o|')"
    g++ $CXXFLAGS -I../src -I../src/builders/sidlite-builder -c "$f" -o "$oname"
done
rm -f libsidplayfp.a
ar rcs libsidplayfp.a *.o
echo "  Built $(ls *.o | wc -l) objects"
cd ../..

# --- Step 4: Build siddump ---

echo "Building siddump..."
g++ $CXXFLAGS $INCFLAGS siddump.cpp libsidplayfp/build/libsidplayfp.a -o siddump
echo "  Built tools/siddump"

echo "Done."
