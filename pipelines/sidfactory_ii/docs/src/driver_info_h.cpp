/*
source_url: https://raw.githubusercontent.com/Chordian/sidfactory2/master/SIDFactoryII/source/runtime/editor/driver/driver_info.h
fetched_via: direct
fetch_date: 2026-06-13
author: Thomas Egeskov Petersen (Laxity) et al.
content_date: 2020-2026
reliability: primary
*/

#pragma once

#include <string>
#include <vector>
#include <memory>

namespace Utility
{
class C64File;
class C64FileReader;
}

namespace Emulation
{
class CPUMemory;
}

namespace Editor
{
class IDriverArchitecture;
class AuxilaryDataCollection;

class DriverInfo final
{
static const unsigned short ExpectedFileIDNumber = 0x1337;
static const unsigned short AuxilaryDataPointerAddress = 0x0ffb;

public:

enum TableType : unsigned char
{
    Generic = 0x00,
    Instruments = 0x80,
    Commands = 0x81
};

enum HeaderBlockID : unsigned int
{
    ID_Descriptor = 1,
    ID_DriverCommon = 2,
    ID_DriverTables = 3,
    ID_DriverInstrumentDescriptor = 4,
    ID_MusicData = 5,
    ID_TableColorRules = 6,
    ID_TableInsertDeleteRules = 7,
    ID_TableActionRules = 8,
    ID_DriverInstrumentDataDescriptor = 9,
    _IDBlock_Count = 10,
    ID_End = 0xff
};

struct Descriptor
{
    unsigned char m_DriverType;
    unsigned short m_DriverSize;
    std::string m_DriverName;
    unsigned short m_DriverCodeTop;
    unsigned short m_DriverCodeSize;
    unsigned char m_DriverVersionMajor;
    unsigned char m_DriverVersionMinor;
    unsigned char m_DriverVersionRevision;
};

struct DriverCommon
{
    unsigned short m_InitAddress;
    unsigned short m_StopAddress;
    unsigned short m_UpdateAddress;
    unsigned short m_SIDChannelOffsetAddress;
    unsigned short m_DriverStateAddress;
    unsigned short m_TickCounterAddress;
    unsigned short m_OrderListIndexAddress;
    unsigned short m_SequenceIndexAddress;
    unsigned short m_SequenceInUseAddress;
    unsigned short m_CurrentSequenceAddress;
    unsigned short m_CurrentTransposeAddress;
    unsigned short m_CurrentSequenceEventDurationAddress;
    unsigned short m_NextInstrumentAddress;
    unsigned short m_NextCommandAddress;
    unsigned short m_NextNoteAddress;
    unsigned short m_NextNoteIsTiedAddress;
    unsigned short m_TempoCounterAddress;
    unsigned short m_TriggerSyncAddress;
    unsigned char m_NoteEventTriggerSyncValue;
    unsigned char m_ReservedByte;
    unsigned short m_ReservedWord;
};

struct MusicData
{
    unsigned char m_TrackCount;
    unsigned short m_TrackOrderListPointersLowAddress;
    unsigned short m_TrackOrderListPointersHighAddress;
    unsigned char m_SequenceCount;
    unsigned short m_SequencePointersLowAddress;
    unsigned short m_SequencePointersHighAddress;
    unsigned short m_OrderListSize;
    unsigned short m_OrderListTrack1Address;
    unsigned short m_SequenceSize;
    unsigned short m_Sequence00Address;
};

struct MusicDataMetaDataEmulationAddresses
{
    unsigned short m_EmulationAddressOfSequencePointersLowAddress;
    unsigned short m_EmulationAddressOfSequencePointersHighAddress;
    unsigned short m_EmulationAddressOfOrderListTrack1Address;
    unsigned short m_EmulationAddressOfSequence00Address;
};

struct TableDefinition
{
    enum DataLayout : unsigned char
    {
        RowMajor = 0,
        ColumnMajor = 1
    };

    enum Properties : unsigned char
    {
        EnableInsertDelete = 0x01,
        LayoutAddVertically = 0x02,
        IndexAsContinuousMemory = 0x04
    };

    unsigned char m_Type;
    unsigned char m_ID;
    unsigned char m_TextFieldSize;
    std::string m_Name;
    DataLayout m_DataLayout;
    bool m_PropertyEnabledInsertDelete;
    bool m_PropertyLayoutVertically;
    bool m_PropertyIndexAsContinuousMemory;
    unsigned char m_InsertDeleteRuleID;
    unsigned char m_EnterActionRuleID;
    unsigned char m_ColorRuleID;
    unsigned short m_Address;
    unsigned short m_ColumnCount;
    unsigned short m_RowCount;
    unsigned char m_VisibleRowCount;
};

struct InstrumentDescriptor
{
    std::vector<std::string> m_CellDescription;
};

struct TableColorRule
{
    unsigned char m_EvaluationCellIndex;
    unsigned char m_EvaluationCellMask;
    unsigned char m_EvaluationCellConditionalValue;
    unsigned char m_BackgroundColor;
};

struct TableColorRules
{
    std::vector<TableColorRule> m_Rules;
};

struct TableInsertDeleteRule
{
    unsigned char m_TargetTableID;
    unsigned char m_TargetCellIndex;
    unsigned char m_EvaluationCellIndex;
    unsigned char m_EvaluationCellMask;
    unsigned char m_EvaluationCellConditionalValue;
};

struct TableInsertDeleteRules
{
    std::vector<TableInsertDeleteRule> m_Rules;
};

struct TableActionRule
{
    unsigned char m_ApplicableCell;
    unsigned char m_TargetIndexCell;
    unsigned char m_TargetIndexMask;
    unsigned char m_TargetTableID;
    unsigned char m_EvaluationCellIndex;
    unsigned char m_EvaluationCellMask;
    unsigned char m_EvaluationCellConditionalValue;
};

struct TableActionRules
{
    std::vector<TableActionRule> m_Rules;
};

struct InstrumentDataPointerDescription
{
    unsigned char m_TableID;
    unsigned char m_InstrumentDataPointerPosition;
    unsigned char m_PointerAndValue;
    unsigned char m_InstrumentDataConditionalValuePosition;
    unsigned char m_ConditionValueAndValue;
    unsigned char m_ConditionEqualityValue;
    unsigned char m_TableDataType;
    unsigned char m_TableJumpMarkerValuePosition;
    unsigned char m_TableJumpMarkerValue;
    unsigned char m_TableJumpDestinationIndexPosition;
};

struct InstrumentDataDescription
{
    std::vector<InstrumentDataPointerDescription> m_InstrumentDataPointerDescriptions;
};

DriverInfo();
~DriverInfo();

void Parse(const Utility::C64File& inFile);
bool IsValid() const;
bool IsParticalyValid() const;
const Descriptor& GetDescriptor() const;
const DriverCommon& GetDriverCommon() const;
const MusicData& GetMusicData() const;
const std::vector<TableDefinition>& GetTableDefinitions() const;
const std::vector<TableColorRules>& GetTableColorRules() const;
const std::vector<TableInsertDeleteRules>& GetTableInsertDeleteRules() const;
const std::vector<TableActionRules>& GetTableActionRules() const;
const InstrumentDataDescription& GetInstrumentDataDescription() const;
unsigned short GetTopAddress() const;
IDriverArchitecture* const GetDriverArchitecture() const;
bool HasFoundHeaderBlock(HeaderBlockID inBlockID) const;
bool HasParsedHeaderBlock(HeaderBlockID inBlockID) const;
bool HasEditData() const;
AuxilaryDataCollection& GetAuxilaryDataCollection();
const AuxilaryDataCollection& GetAuxilaryDataCollection() const;
const MusicDataMetaDataEmulationAddresses& GetMusicDataMetaDataEmulationAddresses() const;
void RefreshMusicData(Emulation::CPUMemory& inCPUMemory);

private:

bool HasParsedRequiredBlocks() const;
void SetHasFoundHeaderBlock(HeaderBlockID inBlockID);
void SetHasParsedHeaderBlock(HeaderBlockID inBlockID);
bool ParseHeader(const Utility::C64File& inFile);
void ParseDescriptor(Utility::C64FileReader& inReader);
void ParseDriverCommon(Utility::C64FileReader& inReader);
void ParseDriverTables(Utility::C64FileReader& inReader);
void ParseDriverInstrumentDescriptor(Utility::C64FileReader& inReader);
void ParseMusicData(Utility::C64FileReader& inReader);
void ParseTableColorRules(Utility::C64FileReader& inReader);
void ParseTableInsDelRules(Utility::C64FileReader& inReader);
void ParseTableActionRules(Utility::C64FileReader& inReader);
void ParseDriverInstrumentDataDescriptor(Utility::C64FileReader& inReader);
bool ParseAuxilaryData(const Utility::C64File& inFile);

bool m_IsValid;
bool m_FoundRequiredTableInstruments;
bool m_FoundRequiredTableCommands;
bool m_HasEditData;
unsigned short m_TopAddress;
unsigned int m_FoundDescriptorBlocks;
unsigned int m_ParsedDescriptorBlocks;
std::unique_ptr<IDriverArchitecture> m_DriverArchitecture;
Descriptor m_Descriptor;
DriverCommon m_DriverCommon;
MusicData m_MusicData;
std::vector<TableDefinition> m_TableDefinitions;
std::vector<TableColorRules> m_TableColorRules;
std::vector<TableInsertDeleteRules> m_TableInsDelRules;
std::vector<TableActionRules> m_TableActionRules;
InstrumentDataDescription m_InstrumentDataDescription;
std::unique_ptr<AuxilaryDataCollection> m_AuxilaryDataCollection;
InstrumentDescriptor m_InstrumentDescriptor;
MusicDataMetaDataEmulationAddresses m_MusicDataMetaDataEmulationAddresses;
};

}
