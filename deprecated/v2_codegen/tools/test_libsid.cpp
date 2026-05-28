#include <iostream>
#include <fstream>
#include <vector>
#include <cstdint>

// Include libsidplayfp headers directly from source
#define SIDPLAYFP_H  // trick to allow including sidversion.h
#include "../tools/libsidplayfp/src/sidplayfp/sidversion.h"
#undef SIDPLAYFP_H

int main() {
    std::cout << "libsidplayfp version: "
              << LIBSIDPLAYFP_VERSION_MAJ << "."
              << LIBSIDPLAYFP_VERSION_MIN << "."
              << LIBSIDPLAYFP_VERSION_LEV << std::endl;
    std::cout << "Library test OK" << std::endl;
    return 0;
}
