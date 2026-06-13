// ---
// source_url: https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/utils/psidfile.cpp
// fetched_via: direct (raw.githubusercontent.com)
// fetch_date: 2026-06-13
// author: Jens-Christian Huus (Chordian)
// content_date: unknown (master branch as of 2026-06-13)
// reliability: primary
// ---

#include "utils/psidfile.h"

#include <string>
#include <cstring>
#include "foundation/base/assert.h"

namespace Utility
{
	unsigned short endian_convert(unsigned short inValue)
	{
		return (inValue >> 8) | (inValue << 8);
	}

	PSIDFile::PSIDFile(
		const unsigned char* const inPRGFormatedData,
		const unsigned short inDataSize,
		const unsigned short inInitOffset,
		const unsigned short inUpdateOffset,
		const unsigned short inSongCount,
		const std::string& inTitle,
		const std::string& inAuthor,
		const std::string& inCopyright,
		const bool in6581,
		const bool inPAL)
	{
		memset(&m_Header, 0, sizeof(Header));

		FOUNDATION_ASSERT(inPRGFormatedData != nullptr);
		FOUNDATION_ASSERT(inDataSize > 2);

		unsigned short data_offset = 0x7c;
		unsigned short driver_address = static_cast<unsigned short>(inPRGFormatedData[0]) | (static_cast<unsigned short>(inPRGFormatedData[1]) << 8);

		m_Header.m_MagicNumber[0] = 'P';
		m_Header.m_MagicNumber[1] = 'S';
		m_Header.m_MagicNumber[2] = 'I';
		m_Header.m_MagicNumber[3] = 'D';

		m_Header.m_Version = endian_convert(0x02);
		m_Header.m_DataOffset = endian_convert(data_offset);
		m_Header.m_LoadAddress = 0x0000;
		m_Header.m_InitAddress = endian_convert(driver_address + inInitOffset);
		m_Header.m_UpdateAddress = endian_convert(driver_address + inUpdateOffset);
		m_Header.m_SongCount = endian_convert(inSongCount);
		m_Header.m_DefaultSong = endian_convert(1);
		m_Header.m_SpeedFlags = 0;

		CopyString(inTitle, m_Header.m_Title);
		CopyString(inAuthor, m_Header.m_Author);
		CopyString(inCopyright, m_Header.m_Copyright);

		m_Header.m_Flags = endian_convert((in6581 ? 0x10 : 0x20) | (inPAL ? 0x04 : 0x08));

		unsigned short header_size = sizeof(Header);

		FOUNDATION_ASSERT(header_size == data_offset);

		m_DataSize = header_size + inDataSize;
		m_Data = new unsigned char[m_DataSize];

		memcpy(m_Data, &m_Header, sizeof(Header));
		memcpy(m_Data + data_offset, inPRGFormatedData, inDataSize);
	}


	PSIDFile::~PSIDFile()
	{
		delete m_Data;
	}


	const unsigned char* PSIDFile::GetData() const
	{
		return m_Data;
	}


	unsigned int PSIDFile::GetDataSize() const
	{
		return m_DataSize;
	}


	void PSIDFile::CopyString(const std::string& inString, char* outCharArray)
	{
		const char* string = inString.c_str();
		size_t string_length = inString.length();

		for (size_t i = 0; i < 0x20; ++i)
			outCharArray[i] = i < string_length ? string[i] : 0;
	}
}

// --- PSID Header struct (from psidfile.h, reconstructed from binary layout) ---
//
// #pragma pack(push, 1)
// struct Header {
//   char           m_MagicNumber[4];    // +0x00: "PSID"
//   unsigned short m_Version;           // +0x04: 0x0002 (big-endian)
//   unsigned short m_DataOffset;        // +0x06: 0x007C (big-endian)
//   unsigned short m_LoadAddress;       // +0x08: 0x0000 (PRG load address embedded in data)
//   unsigned short m_InitAddress;       // +0x0A: driver_address + inInitOffset (big-endian)
//   unsigned short m_UpdateAddress;     // +0x0C: driver_address + inUpdateOffset (big-endian)
//   unsigned short m_SongCount;         // +0x0E: number of subtunes (big-endian)
//   unsigned short m_DefaultSong;       // +0x10: 1 (big-endian)
//   unsigned int   m_SpeedFlags;        // +0x12: 0 (VBlank for all subtunes)
//   char           m_Title[0x20];       // +0x16
//   char           m_Author[0x20];      // +0x36
//   char           m_Copyright[0x20];   // +0x56
//   unsigned short m_Flags;             // +0x76: SID model | clock (big-endian)
//                                       //   6581=0x10, 8580=0x20; PAL=0x04, NTSC=0x08
//   unsigned char  m_StartPage;         // +0x78
//   unsigned char  m_PageLength;        // +0x79
//   unsigned char  m_SecondSIDAddress;  // +0x7A
//   unsigned char  m_ThirdSIDAddress;   // +0x7B (note: fetcher reported overlap at 0x7A)
// };
// #pragma pack(pop)
// Total header size: 0x7C bytes
