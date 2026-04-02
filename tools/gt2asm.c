/* Standalone wrapper for the GT2 assembler (Magnus Lind's assembler from Exomizer) */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../src/GoatTracker_2.77/src/asm/membuf.h"
#include "../src/GoatTracker_2.77/src/asm/parse.h"

int main(int argc, char *argv[]) {
    struct membuf src = STATIC_MEMBUF_INIT;
    struct membuf dest = STATIC_MEMBUF_INIT;
    FILE *f;
    long len;
    char *buf;

    if (argc != 3) {
        fprintf(stderr, "Usage: gt2asm input.s output.bin\n");
        return 1;
    }

    f = fopen(argv[1], "rb");
    if (!f) { fprintf(stderr, "Cannot open %s\n", argv[1]); return 1; }
    fseek(f, 0, SEEK_END);
    len = ftell(f);
    fseek(f, 0, SEEK_SET);
    buf = malloc(len);
    fread(buf, 1, len, f);
    fclose(f);

    membuf_init(&src);
    membuf_init(&dest);
    membuf_append(&src, buf, len);
    free(buf);

    if (assemble(&src, &dest) != 0) {
        fprintf(stderr, "Assembly failed\n");
        membuf_free(&src);
        membuf_free(&dest);
        return 2;
    }

    int size = membuf_get_size(&dest);
    f = fopen(argv[2], "wb");
    if (!f) { fprintf(stderr, "Cannot write %s\n", argv[2]); return 1; }
    fwrite(membuf_get(&dest), 1, size, f);
    fclose(f);

    fprintf(stderr, "Assembled: %d bytes\n", size);
    membuf_free(&src);
    membuf_free(&dest);
    return 0;
}
