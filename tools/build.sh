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

# --- Step 5: Build sidrender (PCM renderer for audio comparison) ---

echo "Building sidrender..."
g++ $CXXFLAGS $INCFLAGS sidrender.cpp libsidplayfp/build/libsidplayfp.a -o sidrender
echo "  Built tools/sidrender"

echo "Done."
