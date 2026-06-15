/*
  freqtab - generate frequency table for C64 music player.

  argv[1]: frequency of A-4 in Hz. (usually 440)
  argv[2]: C64 clock speed (985248 for PAL C64, 1022700 for NTSC)
*/

#include <stdlib.h>
#include <stdio.h>
#include <math.h>

#ifndef M_LN2
#define M_LN2       0.693147180559945309417
#endif


long sidf[8*12];


void makeFreqTable(double a4, double Fclk)
{
  int o, n;

  double c7=exp(27.0*M_LN2/12.0)*a4;
  for (o=0; o<8; o++) {
    double od=1<<(7-o);
    for (n=0; n<12; n++) {
      double f=exp(n*M_LN2/12.0)*c7/od;
      sidf[o*12+n]=(long)(f*16777216.0/Fclk+0.5);
      if (sidf[o*12+n]>0xffff) sidf[o*12+n]=0xffff;     // Clip to 16 bit.
    }
  }

  printf("; Fclk=%.0lf Hz.\n\n", Fclk);
  printf("; Note 0 is the default as long as no note has been started in a given channel.\n");
  printf("; The expected initial frequency for all channels is supposed to be 0.\n");
  printf("; That is why the 0th element in the frequency table is 0.\n\n");

  printf("freqtablelo:\n");
  printf("        .byte 0\n");
  for (o=0; o<8; o++) {
    printf("        .byte ");
    for (n=0; n<12; n++) {
      int t=(int)(sidf[o*12+n]&0xff);
      printf("$%02x", t);
      if (n!=11) printf(",");
      else printf("   ; octave %d\n", o);
    }
  }

  printf("\nfreqtablehi:\n");
  printf("        .byte 0\n");
  for (o=0; o<8; o++) {
    printf("        .byte ");
    for (n=0; n<12; n++) {
      int t=(int)(sidf[o*12+n]>>8);
      printf("$%02x", t);
      if (n!=11) printf(",");
      else printf("   ; octave %d\n", o);
    }
  }
}


int main(int argc, char *argv[])
{
  double a4 = 440.0;
  double Fclk = 985248.0;

  switch (argc) {
    case 3: sscanf(argv[2], "%lf", &Fclk);
    case 2: sscanf(argv[1], "%lf", &a4);
            makeFreqTable(a4, Fclk);
            break;
    default:
      fprintf(stderr, "freqtab [middleA] [C64clock]\n\n");
      fprintf(stderr, "Dumps a frequency table for C64 music player to stdout.\n\n");
      fprintf(stderr, " middleA: frequency of middle A, default is 440.\n");
      fprintf(stderr, "C64clock: C64 clock speed, use 985248 for PAL C64 (default), 1022700 for NTSC.\n");
  }
  return EXIT_SUCCESS;
}
