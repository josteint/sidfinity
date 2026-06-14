#include <stdio.h>
#include <string.h>

// for c
typedef int bool;
#define true 1
#define false 0

// internal variables for player
bool useVars=false;
bool useAllVars=false;
bool useGlideSlide=false;
bool useFade=false;
bool useAd=false;
bool useSr=false;
bool useAdn=false;
bool useSrn=false;
bool useAgate=false;
bool useSetp=false;
bool useSetff=false;
bool useSetft=false;
bool useFvol=false;
bool useSetrlen=false;
bool useRestart0=false;
bool useNopulse=false;
bool useNoflt=false;
bool useSwitch=false;
bool useVol=false;
bool useVibdepth=false;
bool useVibspeed=false;
bool useSetspeed=false;
bool useControl=false;
bool useComplexFilter=false;
bool useComplexPulse=false;

int numSectors;
int sectors[128][255];
unsigned char packedData[65536];
int numWaves;
int waveTab1[255];
int waveTab2[255];
int numPulse;
int pulseTab[255];
int numFilter;
int filterTab[255];
int packedSize;
int psetup[16];
int numSectors;
int orders[3][255];
int numOrders[3];
int numSounds;
int sounds[32][8];
int gvol;
int spd;

int readByte(int byteNum)
{
	byteNum-=0x1000;
	byteNum+=2;
	return packedData[byteNum];
}

int readWord(int byteNum)
{
	return readByte(byteNum)+(readByte(byteNum+1)<<8);
}

int getSectorLen(int s)
{
	int sl=0;
	while(sectors[s][sl]!=0xff)
		sl++;
	return sl;
}

void printTable(FILE *o, char *name, int *table, int entries)
{
	fprintf(o, "%s\t.byte ", name);
	for(int x=0;x<entries-1;x++)
		fprintf(o, "$%x, ", table[x]);
	fprintf(o, "$%x\n", table[entries-1]);
}

void printBoolean(FILE *o, char *name, bool val)
{
	fprintf(o, "%s = %d\n", name, val);
}

void writeAsm()
{
	FILE *c=fopen("config.ass", "wt");
	fprintf(c, "debugplr = 0\n");
	fprintf(c, "usingEditor = 0\n");
	
	// FIXME: be smart about this...
	printBoolean(c, "useFxTable", 0);
	printBoolean(c, "useVibrato", 1);
	printBoolean(c, "useRestart0", 1);
	
	// internal player commands
	printBoolean(c, "useVariables", useVars);
	printBoolean(c, "useAllVariables", useAllVars);
	printBoolean(c, "useGlideSlide", useGlideSlide);
	printBoolean(c, "useFade", useFade);
	printBoolean(c, "useAd", useAd);
	printBoolean(c, "useSr", useSr);
	printBoolean(c, "useAdn", useAdn);
	printBoolean(c, "useSrn", useSrn);
	printBoolean(c, "useAgate", useAgate);
	printBoolean(c, "useSetp", useSetp);
	printBoolean(c, "useSetff", useSetff);
	printBoolean(c, "useSetft", useSetft);
	printBoolean(c, "useFvol", useFvol);

	printBoolean(c, "useSetrlen", useSetrlen);
	printBoolean(c, "useNopulse", useNopulse);
	printBoolean(c, "useNoflt", useNoflt);
	printBoolean(c, "useSwitch", useSwitch);
	printBoolean(c, "useVol", useVol);
	printBoolean(c, "useVibdepth", useVibdepth);
	printBoolean(c, "useVibspeed", useVibspeed);
	printBoolean(c, "useSetspeed", useSetspeed);
	printBoolean(c, "useControl", useControl);
	printBoolean(c, "useComplexPulse", useComplexPulse);
	printBoolean(c, "useComplexFilter", useComplexFilter);

	
	FILE *o=fopen("song.ass", "wt");
	printTable(o, "wavetab1", waveTab1, numWaves);
	printTable(o, "wavetab2", waveTab2, numWaves);
	printTable(o, "pulse", pulseTab, numPulse);
	printTable(o, "filter", filterTab, numFilter);

	// sector list comes next
	fprintf(o, "sledy\n");
	fprintf(o, "\t.byte <orderList1");
	fprintf(o, ", <orderList2");
	fprintf(o, ", <orderList3");
	fprintf(o, ", >orderList1");
	fprintf(o, ", >orderList2");
	fprintf(o, ", >orderList3");
	fprintf(o, ", $%x", spd);
	fprintf(o, ", $%x\n", gvol);

	printTable(o, "orderList1", orders[0], numOrders[0]);
	printTable(o, "orderList2", orders[1], numOrders[1]);
	printTable(o, "orderList3", orders[2], numOrders[2]);
	
	// then tracksHi
	fprintf(o, "sectorsl\t.byte ");
	for(int s=0;s<numSectors;s++)
	{
		char sectorName[1000];
		sprintf(sectorName, "sector%d", s);
		if(s!=0)
			fprintf(o, ", ");
		fprintf(o, "<%s", sectorName);
	}
	fprintf(o, "\n");
	
	// then tracksLo
	fprintf(o, "sectorsh\t.byte ");
	for(int s=0;s<numSectors;s++)
	{
		char sectorName[1000];
		sprintf(sectorName, "sector%d", s);
		if(s!=0)
			fprintf(o, ", ");
		fprintf(o, ">%s", sectorName);
	}
	fprintf(o, "\n");

	// then sounds
	fprintf(o, "sounds\n");
	for(int s=0;s<numSounds;s++)
	{
		printTable(o, "", sounds[s], 8);
	}
	
	// then the actual sectors themselves
	for(int s=0;s<numSectors;s++)
	{
		char sectorName[1000];
		sprintf(sectorName, "sector%d", s);
		int slen=getSectorLen(s);
		fprintf(o, "; Sector $%x len: %d\n", s, slen);
		printTable(o, sectorName, sectors[s], slen+1);
	}
	fclose(o);
}

#define checkCommand(commandName, value, inc) \
	if(sectors[s][x]==(value)) { \
	    if(commandName==false) \
	    { \
		    printf("command %x use detected!\n", value); \
	            commandName=true; \
		    inc; \
	    } \
	}


void detectFeatures()
{
	for(int s=0;s<numSectors;s++)
	{
		int slen=getSectorLen(s);
		printf("Sector $%x len: %d\n", s, slen);
		int x=0;
		while(x<slen)
		{
			if(sectors[s][x]<0xc0 || sectors[s][x]>=0xfd)
			{
				// i'm just a note... or an in-stru-ment
				// or some other arbitary thing
			}
			else if(sectors[s][x]>=0xc0 && sectors[s][x]<=0xcf)
			{
				if(useVol==false)
				{
					printf("Volume use detected!\n");
					useVol=true;
				}
				
			}
			else if(sectors[s][x]>=0xe0 && sectors[s][x]<=0xe6)
			{
				if(useVars==false)
				{
					printf("Variable use detected!\n");
					useVars=true;
					x++;
				}
				
			}
			else checkCommand(useNopulse, 0xe8, x++)
			else checkCommand(useVibdepth, 0xe9, x++)
			else checkCommand(useVibspeed, 0xea, x++)
			else checkCommand(useSetspeed, 0xeb, x++)
			else checkCommand(useSetrlen, 0xec, x++)
			else checkCommand(useControl, 0xed, x++)
			else checkCommand(useGlideSlide, 0xee, x++)
			else checkCommand(useGlideSlide, 0xef, x++)
			else checkCommand(useFade, 0xf0, x++)
			else checkCommand(useFade, 0xf1, x++)
			else checkCommand(useAd, 0xf2, x++)
			else checkCommand(useSr, 0xf3, x++)
			else checkCommand(useAdn, 0xf4, x++)
			else checkCommand(useSrn, 0xf5, x++)
			else checkCommand(useAgate, 0xf6, x++)
			else checkCommand(useNoflt, 0xf7, x++)
			else checkCommand(useSetff, 0xf8, x++)
			else checkCommand(useSetft, 0xf9, x++)
			else checkCommand(useSetp, 0xfa, x++)
			else checkCommand(useFvol, 0xfb, x++)
			else checkCommand(useSwitch, 0xfc, )
			else
			{
				printf("Unhandled effect: $%02x\n", sectors[s][x]);
			}
			x++;
		}
	}

	if(useVars==true)
	{
		for(int x=0;x<numPulse;x++)
			if(pulseTab[x]==0xa3)
				useAllVars=true;
		for(int x=0;x<numFilter;x++)
			if(filterTab[x]==0xa3)
				useAllVars=true;
	}
}

int getOrderCount(int which)
{
	int oc=0;
	for(int c=0;c<3;c++)
	{
		for(int x=0;x<numOrders[c];x++)
		{
			if(orders[c][x]==which)
				oc++;
		}
	}
	return oc;
}

void crunchSectors()
{
	printf("WARNING!  WARNING!  WARNING!!! crunchSectors() DOESN'T WORK!!!\n");
	abort();

	int movements[128][1000];
	int oldTotal=0;
	int newTotal=0;
	
	// convert into a set of movements
	for(int s=0;s<numSectors;s++)
	{
		int oldLen=getSectorLen(s);
		int lastNote= -1;
		for(int x=0;x<=oldLen;x++)
		{
			int myByte=sectors[s][x];
			if(myByte>=0x60)
				movements[s][x]=myByte;
			else
			{
				if(lastNote== -1)
					movements[s][x]=0;
				else
				{
					movements[s][x]=sectors[s][x]-lastNote;
				}
				lastNote=sectors[s][x];
			}
		}
		oldTotal+=getSectorLen(s);
	}

	int maxi,maxx,maxj,maxy,maxmatch=0;

	// find matching windows
	for(int i=0;i<numSectors;i++)
	{
		for(int x=0;x<getSectorLen(i);x++)
		{
			for(int j=0;j<numSectors;j++)
			{
				for(int y=0;y<getSectorLen(j);y++)
				{
					if(i!=j)
					{
						int matchLen=0;
						while(movements[i][x+matchLen]==movements[j][y+matchLen] && movements[i][x+matchLen]!=0xff && movements[j][y+matchLen]!=0xff)
							matchLen++;
						if(matchLen>10)
						{
							// we have a win, scan how often these appear in the order list
							int orderCount=getOrderCount(i);
							orderCount+=getOrderCount(j);
							//printf("Orders appear %d times\n", orderCount);
							matchLen-=(orderCount*3);
							if(matchLen>maxmatch)
							{
								printf("Match %d: %d, %d vs. %d, %d\n", matchLen, i, x, j, y);
								maxx=x;
								maxi=i;
								maxy=y;
								maxj=j;
								maxmatch=matchLen;

								// create new world order
							}
						}
					}
				}
			}
		}
	}
	
	printf("Old total: %d\n", oldTotal);
}

void packSectors()
{
	int oldTotal=0;
	int newTotal=0;
	for(int s=0;s<numSectors;s++)
	{
		int oldLen=getSectorLen(s);
		int newLen=0;
		int newSector[1000];
		printf("old: Sector $%x len: %d\n", s, oldLen+1);
	
		for(int x=0;x<=oldLen;x++)
		{
			int myByte=sectors[s][x];
			int rept=1;
			if(myByte==0xfd)
			{
				while(myByte==sectors[s][x+rept])
				{
					rept++;
				}
			}
			if(rept>2)
			{
				printf("Repeating 0xfd: %d\n", rept);
				x+=(rept-1);
				newSector[newLen++]=0xe6;
				newSector[newLen++]=(rept-1);
			}
			else
				newSector[newLen++]=myByte;
		}
		
		printf("new: Sector $%x len: %d\n", s, newLen);
		oldTotal+=getSectorLen(s);
		for(int x=0;x<=newLen;x++)
		{
			sectors[s][x]=newSector[x];
		}
		newTotal+=getSectorLen(s);
	}
	printf("%d vs. %d\n", oldTotal, newTotal);
}

void tfxDepack()
{
	numSectors=0;
	int waveTable=readWord(readWord(0x1009)+1);
	int waveEntries=readWord(readWord(0x1009+2)+1);
	int pulseTable=readWord(readWord(0x1009+4)+1);
	int fltTable=readWord(readWord(0x1009+6)+1);
	int soundTable=readWord(readWord(0x1009+8)+1);
	int sectorList=readWord(readWord(0x1009+16)+1);
	int psetupLoc=readWord(readWord(0x1009+30)+1);
	int tracksLo=readWord(readWord(0x1009+32)+1);
	int tracksHi=readWord(readWord(0x1009+34)+1);

	numWaves=waveEntries-waveTable;
	for(int j=0;j<numWaves;j++)
	{
		waveTab1[j]=readByte(waveTable+j);
		waveTab2[j]=readByte(waveEntries+j);
	}

	printf("Read $%x wavetable entries\n", numWaves);

	numPulse=fltTable-pulseTable;
	for(int j=0;j<numPulse;j++)
	{
		pulseTab[j]=readByte(pulseTable+j);
		if(pulseTab[j]==0xd3)
			useComplexPulse=true;
	}
	printf("Read $%x pulsetable entries\n", numPulse);

	numFilter=sectorList-fltTable;
	for(int j=0;j<numFilter;j++)
	{
		filterTab[j]=readByte(fltTable+j);
		if(filterTab[j]==0xd3)
			useComplexFilter=true;
	}
	printf("Read $%x filtertable entries\n", numFilter);

	for(int j=0;j<16;j++)
	{
		psetup[j]=readByte(psetupLoc+j);
	}
	printf("Read psetup\n");


	numSectors=tracksHi-tracksLo;
	printf("%x, %x, %x\n", tracksHi, tracksLo, numSectors);
	for(int x=0;x<numSectors;x++)
	{
		int offset=(readByte(tracksHi+x)<<8)+readByte(tracksLo+x);
		int co=0;
		int thisByte;
		if(readByte(offset)!=0)
		{
			do
			{
				thisByte=readByte(offset);
				sectors[x][co]=thisByte;
				offset++;
				co++;
			} while(thisByte!=0xff);
			printf("Sector %x: %x bytes\n", x, co);
		}
		else
		{
			printf("Empty sector: %x\n", x);
			sectors[x][0]=0xff;
			offset++;
		}
	}
	printf("Read $%x sectors\n", numSectors);

	spd=readByte(sectorList+6);
	gvol=readByte(sectorList+7);
	for(int c=0;c<3;c++)
	{
		int offset=readByte(sectorList+c)+(readByte(sectorList+c+3)<<8);
		int thisByte;
		int co=0;
		do
		{
			thisByte=readByte(offset);
			orders[c][co]=thisByte;
			offset++;
			co++;
		} while(thisByte!=0x7f);
		numOrders[c]=co;
		printf("Read $%x tracks\n", numOrders[c]);
	}
	
	numSounds=((int)waveTable-(int)soundTable)/8;

	printf("%d\n", numSounds);
	for(int c=0;c<numSounds;c++)
	{
		printf("sound %d: %x\n", c, readWord(soundTable+c*8));
		for(int x=0;x<8;x++)
		{
			sounds[c][x]=readByte(soundTable+c*8+x);
		}
	}
}

int main(int argc, char **argv)
{
	printf("TFX2 Hyper Packer v0.1 by Jaymz\n");
	printf("(c) 2004, Unreal\n");

	if(argc<2)
	{
		printf("Usage: %s in.prg\n", argv[0]);
		printf("Usage: %s in-patterns-a.prg in-patterns-b.prg in-tracks.prg in-instruments.prg\n", argv[0]);
		return -1;
	}


	if(argc==2)
	{
		FILE *i=fopen(argv[1], "rb");
		if(i==NULL)
		{
			printf("Couldn't read file %s\n", argv[1]);
			return -1;
		}

		packedSize=fread(packedData, 1, 8194, i);
		printf("Read %d bytes\n", packedSize);

		tfxDepack();
	}
	else
	{
		FILE *i=fopen(argv[1], "rb");
		printf("Reading patterns a\n");
		packedSize=fread(packedData, 1, 64000, i);
		printf("Size: %d, Load: %x\n", packedSize, packedData[0]+packedData[1]<<8);
		fclose(i);

		for(int c=0;c<53;c++)
		{
			for(int d=0;d<256;d++)
			{
				sectors[c][d]=packedData[(c*256)+d+2];
			}
		}


		i=fopen(argv[2], "rb");
		printf("Reading patterns b\n");
		packedSize=fread(packedData, 1, 64000, i);
		printf("Size: %d\n", packedSize);
		fclose(i);
		
		for(int c=0;c<27;c++)
		{
			for(int d=0;d<256;d++)
			{
				sectors[c+53][d]=packedData[(c*256)+d+2];
			}
		}

		numSectors=80;

		i=fopen(argv[3], "rb");
		printf("Reading tracks\n");
		packedSize=fread(packedData, 1, 64000, i);
		printf("Size: %d\n", packedSize);
		fclose(i);

		for(int c=0;c<3;c++)
		{
			numOrders[c]=0x80;
			for(int x=0;x<0x80;x++)
			{
				orders[c][x]=packedData[0x100*c+x+2];
			}
		}
		
		i=fopen(argv[4], "rb");
		printf("Reading instruments\n");
		packedSize=fread(packedData, 1, 64000, i);
		printf("Size: %d\n", packedSize);
		fclose(i);

		numSounds=0;
		numWaves=0;
		numPulse=0;
		numFilter=0;
	}
	
	detectFeatures();
	packSectors();
	//crunchSectors();

	writeAsm();
}
