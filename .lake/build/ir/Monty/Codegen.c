// Lean compiler output
// Module: Monty.Codegen
// Imports: public import Init public import Monty.SID public import Monty.Asm6502 public import Monty.PSIDFile public import Monty.USF
#include <lean/lean.h>
#if defined(__clang__)
#pragma clang diagnostic ignored "-Wunused-parameter"
#pragma clang diagnostic ignored "-Wunused-label"
#elif defined(__GNUC__) && !defined(__CLANG__)
#pragma GCC diagnostic ignored "-Wunused-parameter"
#pragma GCC diagnostic ignored "-Wunused-label"
#pragma GCC diagnostic ignored "-Wunused-but-set-variable"
#endif
#ifdef __cplusplus
extern "C" {
#endif
LEAN_EXPORT uint16_t lp_sidfinity_MV3_SID__BASE;
lean_object* lean_array_get_size(lean_object*);
uint16_t lean_uint16_of_nat(lean_object*);
uint16_t lean_uint16_add(uint16_t, uint16_t);
LEAN_EXPORT uint16_t lp_sidfinity_MV3_CodeBuilder_currentAddr(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_currentAddr___boxed(lean_object*);
lean_object* l_Array_append___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emit(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emit___boxed(lean_object*, lean_object*);
lean_object* lp_sidfinity_assembleInst(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitInst(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitInst___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_label(lean_object*, lean_object*);
uint8_t lean_string_dec_eq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_lookupLabel(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_lookupLabel___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___boxed(lean_object*, lean_object*, lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0;
uint8_t lean_int8_of_nat(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static uint8_t lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__2;
lean_object* lean_nat_add(lean_object*, lean_object*);
lean_object* lean_array_push(lean_object*, lean_object*);
lean_object* lp_sidfinity_opcode(uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitBranch(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitBranch___boxed(lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___boxed(lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitIncAbsX(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___redArg(lean_object*, lean_object*, lean_object*);
uint8_t lean_uint16_to_uint8(uint16_t);
lean_object* lean_array_set(lean_object*, lean_object*, lean_object*);
uint16_t lean_uint16_shift_right(uint16_t, uint16_t);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_to_int(lean_object*);
static lean_once_cell_t lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0;
static lean_once_cell_t lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1;
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg(lean_object*, lean_object*, lean_object*);
lean_object* lean_uint16_to_nat(uint16_t);
lean_object* lean_int_add(lean_object*, lean_object*);
lean_object* lean_int_sub(lean_object*, lean_object*);
lean_object* lean_int_emod(lean_object*, lean_object*);
lean_object* l_Int_toNat(lean_object*);
uint8_t lean_uint8_of_nat(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_resolve(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_array_mk(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitData(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitByte___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitByte___closed__0;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitByte(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitByte___boxed(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsYL(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbs(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbs(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_addAbsFixup(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitDynRefLoad___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "v_scratch_s"};
static const lean_object* lp_sidfinity_MV3_emitDynRefLoad___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitDynRefLoad___closed__0_value;
static const lean_string_object lp_sidfinity_MV3_emitDynRefLoad___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "_v"};
static const lean_object* lp_sidfinity_MV3_emitDynRefLoad___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitDynRefLoad___closed__1_value;
static const lean_string_object lp_sidfinity_MV3_emitDynRefLoad___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_ctrl_"};
static const lean_object* lp_sidfinity_MV3_emitDynRefLoad___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitDynRefLoad___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitDynRefLoad___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "v_pitch_v"};
static const lean_object* lp_sidfinity_MV3_emitDynRefLoad___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitDynRefLoad___closed__3_value;
static const lean_string_object lp_sidfinity_MV3_emitDynRefLoad___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_inst_v"};
static const lean_object* lp_sidfinity_MV3_emitDynRefLoad___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitDynRefLoad___closed__4_value;
lean_object* lp_sidfinity_I_lda__imm(uint8_t);
lean_object* l_Nat_reprFast(lean_object*);
lean_object* lean_string_append(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynRefLoad(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitFreqSlotStore___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "freq_hi_"};
static const lean_object* lp_sidfinity_MV3_emitFreqSlotStore___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitFreqSlotStore___closed__0_value;
static const lean_string_object lp_sidfinity_MV3_emitFreqSlotStore___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "freq_lo_"};
static const lean_object* lp_sidfinity_MV3_emitFreqSlotStore___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitFreqSlotStore___closed__1_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFreqSlotStore(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFreqSlotStore___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicFreqEntry(lean_object*, lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_sidfinity_MV3_phaseMatches(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_phaseMatches___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicEntryIfPhase(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicEntryIfPhase___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicUpdatesForPhase(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicUpdatesForPhase___boxed(lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitFlagRule___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "nload_op"};
static const lean_object* lp_sidfinity_MV3_emitFlagRule___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitFlagRule___closed__0_value;
static const lean_string_object lp_sidfinity_MV3_emitFlagRule___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "_r"};
static const lean_object* lp_sidfinity_MV3_emitFlagRule___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitFlagRule___closed__1_value;
lean_object* lp_sidfinity_I_lda__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitFlagRule___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitFlagRule___closed__2;
lean_object* lp_sidfinity_I_sta__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitFlagRule___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitFlagRule___closed__3;
lean_object* lp_sidfinity_I_and__imm(uint8_t);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFlagRule(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFlagRule___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOp_spec__0(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOp_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNoteLoadOp___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "_done"};
static const lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNoteLoadOp___closed__0_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__1;
lean_object* lp_sidfinity_I_adc__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__2;
static const lean_string_object lp_sidfinity_MV3_emitNoteLoadOp___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "_noreset"};
static const lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitNoteLoadOp___closed__3_value;
lean_object* lp_sidfinity_I_ldy__imm(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitNoteLoadOp___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__4;
static const lean_ctor_object lp_sidfinity_MV3_emitNoteLoadOp___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 9}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(252, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__5 = (const lean_object*)&lp_sidfinity_MV3_emitNoteLoadOp___closed__5_value;
static const lean_ctor_object lp_sidfinity_MV3_emitNoteLoadOp___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitNoteLoadOp___closed__5_value),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__6 = (const lean_object*)&lp_sidfinity_MV3_emitNoteLoadOp___closed__6_value;
static const lean_string_object lp_sidfinity_MV3_emitNoteLoadOp___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "_noinc"};
static const lean_object* lp_sidfinity_MV3_emitNoteLoadOp___closed__7 = (const lean_object*)&lp_sidfinity_MV3_emitNoteLoadOp___closed__7_value;
extern lean_object* lp_sidfinity_I_clc;
lean_object* lp_sidfinity_I_adc__imm(uint8_t);
lean_object* l_List_lengthTR___redArg(lean_object*);
lean_object* l_List_range(lean_object*);
lean_object* l_List_zipWith___at___00List_zip_spec__0___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNoteLoadOp(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOps_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNoteLoadOps(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPatternEndOp(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitPatternEndOps_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPatternEndOps(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitInitSubtuneClamp___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 17, .m_capacity = 17, .m_length = 16, .m_data = "subtune_in_range"};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneClamp___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__0_value;
static lean_once_cell_t lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_emitInitSubtuneClamp___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSubtuneClamp___closed__2;
lean_object* lp_sidfinity_I_cmp__imm(uint8_t);
extern lean_object* lp_sidfinity_I_asl__a;
extern lean_object* lp_sidfinity_I_tay;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSubtuneClamp(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSubtuneClamp___boxed(lean_object*, lean_object*);
lean_object* lp_sidfinity_I_ldx__imm(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitInitSubtuneCopy___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__0;
static const lean_string_object lp_sidfinity_MV3_emitInitSubtuneCopy___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "subtune_copy"};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__1_value;
static const lean_string_object lp_sidfinity_MV3_emitInitSubtuneCopy___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "ol_subtune_lo"};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "ol_lo"};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3_value;
static const lean_string_object lp_sidfinity_MV3_emitInitSubtuneCopy___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "ol_subtune_hi"};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__4_value;
static const lean_string_object lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "ol_hi"};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5_value;
static const lean_ctor_object lp_sidfinity_MV3_emitInitSubtuneCopy___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 0}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(3, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__6 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__6_value;
static const lean_ctor_object lp_sidfinity_MV3_emitInitSubtuneCopy___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__6_value),LEAN_SCALAR_PTR_LITERAL(12, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy___closed__7 = (const lean_object*)&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__7_value;
extern lean_object* lp_sidfinity_I_iny;
extern lean_object* lp_sidfinity_I_inx;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy(lean_object*);
lean_object* lp_sidfinity_I_sta__abs(uint16_t);
static lean_once_cell_t lp_sidfinity_MV3_emitInitSidSilence___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSidSilence___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_emitInitSidSilence___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSidSilence___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_emitInitSidSilence___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSidSilence___closed__2;
static lean_once_cell_t lp_sidfinity_MV3_emitInitSidSilence___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSidSilence___closed__3;
static lean_once_cell_t lp_sidfinity_MV3_emitInitSidSilence___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitSidSilence___closed__4;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSidSilence(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitInitVoiceState___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitVoiceState___closed__0;
static const lean_string_object lp_sidfinity_MV3_emitInitVoiceState___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "init_loop"};
static const lean_object* lp_sidfinity_MV3_emitInitVoiceState___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitInitVoiceState___closed__1_value;
static const lean_string_object lp_sidfinity_MV3_emitInitVoiceState___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "v_dur"};
static const lean_object* lp_sidfinity_MV3_emitInitVoiceState___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitInitVoiceState___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitInitVoiceState___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_olpos"};
static const lean_object* lp_sidfinity_MV3_emitInitVoiceState___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitInitVoiceState___closed__3_value;
static const lean_string_object lp_sidfinity_MV3_emitInitVoiceState___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_wptr"};
static const lean_object* lp_sidfinity_MV3_emitInitVoiceState___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitInitVoiceState___closed__4_value;
static const lean_string_object lp_sidfinity_MV3_emitInitVoiceState___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_pattlo"};
static const lean_object* lp_sidfinity_MV3_emitInitVoiceState___closed__5 = (const lean_object*)&lp_sidfinity_MV3_emitInitVoiceState___closed__5_value;
static const lean_string_object lp_sidfinity_MV3_emitInitVoiceState___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_patthi"};
static const lean_object* lp_sidfinity_MV3_emitInitVoiceState___closed__6 = (const lean_object*)&lp_sidfinity_MV3_emitInitVoiceState___closed__6_value;
extern lean_object* lp_sidfinity_I_dex;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitVoiceState(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitInitFrameCounter___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitFrameCounter___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_emitInitFrameCounter___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitInitFrameCounter___closed__1;
extern lean_object* lp_sidfinity_I_rts;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitFrameCounter(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitInit___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "init"};
static const lean_object* lp_sidfinity_MV3_emitInit___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitInit___closed__0_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInit(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInit___boxed(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitPlayHeader___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "play"};
static const lean_object* lp_sidfinity_MV3_emitPlayHeader___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitPlayHeader___closed__0_value;
lean_object* lp_sidfinity_I_inc__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitPlayHeader___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitPlayHeader___closed__1;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlayHeader(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitPlayVoiceStep___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "exec_voice"};
static const lean_object* lp_sidfinity_MV3_emitPlayVoiceStep___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitPlayVoiceStep___closed__0_value;
lean_object* l_List_get_x3fInternal___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlayVoiceStep(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitPlayVoiceLoop_spec__1(lean_object*, lean_object*, lean_object*);
lean_object* l_List_reverse___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_emitPlayVoiceLoop_spec__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_emitPlayVoiceLoop_spec__0___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlayVoiceLoop(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlay(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__Header___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "note_load"};
static const lean_object* lp_sidfinity_MV3_emitNL__Header___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__Header___closed__0_value;
lean_object* lp_sidfinity_I_stx__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__Header___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__Header___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__Header___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__Header___closed__2;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__Header___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__Header___closed__3;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__Header(lean_object*);
lean_object* lp_sidfinity_I_ora__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PtrCheck___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PtrCheck___closed__0;
static const lean_string_object lp_sidfinity_MV3_emitNL__PtrCheck___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "ptr_ok"};
static const lean_object* lp_sidfinity_MV3_emitNL__PtrCheck___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PtrCheck___closed__1_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__PtrCheck___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "advance_order"};
static const lean_object* lp_sidfinity_MV3_emitNL__PtrCheck___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PtrCheck___closed__2_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PtrCheck(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__ReadPitch___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "has_note"};
static const lean_object* lp_sidfinity_MV3_emitNL__ReadPitch___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ReadPitch___closed__0_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__ReadPitch___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__ReadPitch___closed__1;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ReadPitch(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__0;
lean_object* lp_sidfinity_I_ldx__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1;
static const lean_string_object lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_porta"};
static const lean_object* lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ReadDurInstPorta(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_filterTR_loop___at___00MV3_emitNL__PreAdvanceOps_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PreAdvanceOps(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__ExtractFlags___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__ExtractFlags___closed__0;
static const lean_string_object lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "v_no_release"};
static const lean_object* lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__ExtractFlags___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__ExtractFlags___closed__2;
static const lean_string_object lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "v_no_inst_byte"};
static const lean_object* lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ExtractFlags(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PreserveMask___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PreserveMask___closed__0;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PreserveMask(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PreserveMask___boxed(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__AdvancePtr___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__AdvancePtr___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__AdvancePtr___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__AdvancePtr___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__AdvancePtr___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__AdvancePtr___closed__2;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__AdvancePtr(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_filterTR_loop___at___00MV3_emitNL__PostAdvanceOps_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PostAdvanceOps(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__DurField___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__DurField___closed__0;
static const lean_string_object lp_sidfinity_MV3_emitNL__DurField___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_durfield"};
static const lean_object* lp_sidfinity_MV3_emitNL__DurField___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__DurField___closed__1_value;
lean_object* lp_sidfinity_I_sbc__imm(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__DurField___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__DurField___closed__2;
extern lean_object* lp_sidfinity_I_sec;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__DurField(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1;
static const lean_string_object lp_sidfinity_MV3_emitNL__UpdateVInst___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 19, .m_capacity = 19, .m_length = 18, .m_data = "skip_v_inst_update"};
static const lean_object* lp_sidfinity_MV3_emitNL__UpdateVInst___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_inst"};
static const lean_object* lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__UpdateVInst(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_sidoff"};
static const lean_object* lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ResetAndSidoff(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__TieCheck___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "tie_skip_pitch"};
static const lean_object* lp_sidfinity_MV3_emitNL__TieCheck___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__TieCheck___closed__0_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__TieCheck(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__FreqWrite___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__FreqWrite___closed__0;
static const lean_string_object lp_sidfinity_MV3_emitNL__FreqWrite___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "freq_hi"};
static const lean_object* lp_sidfinity_MV3_emitNL__FreqWrite___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__FreqWrite___closed__1_value;
lean_object* lp_sidfinity_I_sta__absY(uint16_t);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__FreqWrite___closed__2;
static const lean_string_object lp_sidfinity_MV3_emitNL__FreqWrite___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "freq_lo"};
static const lean_object* lp_sidfinity_MV3_emitNL__FreqWrite___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitNL__FreqWrite___closed__3_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__FreqWrite___closed__4;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__FreqWrite(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PortaInit___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PortaInit___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PortaInit___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PortaInit___closed__1;
static const lean_string_object lp_sidfinity_MV3_emitNL__PortaInit___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_porta_lo"};
static const lean_object* lp_sidfinity_MV3_emitNL__PortaInit___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PortaInit___closed__2_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PortaInit___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PortaInit___closed__3;
static const lean_string_object lp_sidfinity_MV3_emitNL__PortaInit___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_porta_hi"};
static const lean_object* lp_sidfinity_MV3_emitNL__PortaInit___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PortaInit___closed__4_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PortaInit(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__RestoreXY(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_pitch"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0_value;
static const lean_ctor_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 0}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__1_value;
static const lean_ctor_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__1_value),LEAN_SCALAR_PTR_LITERAL(12, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "alias_v1_v2"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__3_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "freq_hi_105"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__4_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "alias_done"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__5 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__5_value;
static const lean_ctor_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 0}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(1, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__6 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__6_value;
static const lean_ctor_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__6_value),LEAN_SCALAR_PTR_LITERAL(12, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__7 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__7_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "alias_v2"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__8 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__8_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "freq_lo_106"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__9 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__9_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "freq_hi_106"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__10 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__10_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "v_fhi"};
static const lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi(lean_object*);
extern lean_object* lp_sidfinity_I_tax;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__TieSkipLabel(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_ctrl"};
static const lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1;
static const lean_string_object lp_sidfinity_MV3_emitNL__CtrlWrite___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "ctrl_no_tie"};
static const lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__2_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5;
extern lean_object* lp_sidfinity_I_pha;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_pwlo"};
static const lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1;
static const lean_string_object lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_pwhi"};
static const lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3;
static const lean_string_object lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "i_ad"};
static const lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__4_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5;
static const lean_string_object lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "i_sr"};
static const lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__6 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__6_value;
static lean_once_cell_t lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "i_pwspeed"};
static const lean_object* lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_pwperiod"};
static const lean_object* lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PwperiodInit(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_ctrl"};
static const lean_object* lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "noteload_done"};
static const lean_object* lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__1_value;
extern lean_object* lp_sidfinity_I_pla;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__AdvanceOrderHeader(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__LookupOL(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0;
static const lean_string_object lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "ol_end_or_loop"};
static const lean_object* lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__1_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "patt_ptr_lo"};
static const lean_object* lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "patt_ptr_hi"};
static const lean_object* lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__3_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ReadAndDispatch(lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitNL__OLEndOrLoop___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "song_end"};
static const lean_object* lp_sidfinity_MV3_emitNL__OLEndOrLoop___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitNL__OLEndOrLoop___closed__0_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__OLEndOrLoop(lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_emitNL__SongEnd___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitNL__SongEnd___closed__0;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__SongEnd(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNoteLoadPath(lean_object*, lean_object*);
static const lean_ctor_object lp_sidfinity_MV3_emitSustainEffects___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 6}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__0_value;
static const lean_ctor_object lp_sidfinity_MV3_emitSustainEffects___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__0_value),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__1_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "pw_has_speed"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "pw_done"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__3_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "i_pwmode"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__4_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "pw_linear"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__5 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__5_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "pw_bidir"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__6 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__6_value;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__7;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__8;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_pwdir"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__9 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__9_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "pw_bidir_down"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__10 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__10_value;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__11;
static const lean_ctor_object lp_sidfinity_MV3_emitSustainEffects___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__0_value),LEAN_SCALAR_PTR_LITERAL(11, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__12 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__12_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "i_pwmax"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__13 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__13_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "pw_bidir_write"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__14 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__14_value;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__15;
lean_object* lp_sidfinity_I_sbc__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__16;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__17;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "i_pwmin"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__18 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__18_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_bit0"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__19 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__19_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "has_slide"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__20 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__20_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "no_slide"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__21 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__21_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "fhi_ok"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__22 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__22_value;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__23_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__23;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "dur_ok"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__24 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__24_value;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__25_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__25;
static const lean_ctor_object lp_sidfinity_MV3_emitSustainEffects___closed__26_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 5}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__26 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__26_value;
static const lean_ctor_object lp_sidfinity_MV3_emitSustainEffects___closed__27_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__26_value),LEAN_SCALAR_PTR_LITERAL(11, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__27 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__27_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "slide_path_b"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__28 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__28_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "slide_done"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__29 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__29_value;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__30_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__30;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__31_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "i_skydive"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__31 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__31_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__32_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "no_sky"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__32 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__32_value;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__33_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__33;
static lean_once_cell_t lp_sidfinity_MV3_emitSustainEffects___closed__34_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__34;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__35_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "i_arp"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__35 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__35_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__36_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "has_arp"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__36 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__36_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__37_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "sustain_done"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__37 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__37_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__38_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "arp_base"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__38 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__38_value;
static const lean_string_object lp_sidfinity_MV3_emitSustainEffects___closed__39_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "arp_write"};
static const lean_object* lp_sidfinity_MV3_emitSustainEffects___closed__39 = (const lean_object*)&lp_sidfinity_MV3_emitSustainEffects___closed__39_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitSustainEffects(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "i_vib"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__0_value;
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "has_vib"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__1 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__1_value;
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "no_vib"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__2_value;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__3;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__4;
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "vib_phase_ok"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__5 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__5_value;
lean_object* lp_sidfinity_I_eor__imm(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__6;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__7;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__8;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__9;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__10;
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "vib_shift"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__11 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__11_value;
static const lean_ctor_object lp_sidfinity_MV3_emitVibrato___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 1}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(245, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__12 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__12_value;
static const lean_ctor_object lp_sidfinity_MV3_emitVibrato___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__12_value),LEAN_SCALAR_PTR_LITERAL(21, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__13 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__13_value;
static const lean_ctor_object lp_sidfinity_MV3_emitVibrato___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 1}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(244, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__14 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__14_value;
static const lean_ctor_object lp_sidfinity_MV3_emitVibrato___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__14_value),LEAN_SCALAR_PTR_LITERAL(23, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__15 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__15_value;
lean_object* lp_sidfinity_I_dec__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__16;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__17;
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "vib_onset_ok"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__18 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__18_value;
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "vib_write_base"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__19 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__19_value;
lean_object* lp_sidfinity_I_ldy__zp(uint8_t);
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__20_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__20;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__21_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__21;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__22_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__22;
static const lean_string_object lp_sidfinity_MV3_emitVibrato___redArg___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "vib_add_loop"};
static const lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__23 = (const lean_object*)&lp_sidfinity_MV3_emitVibrato___redArg___closed__23_value;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__24_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__24;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__25_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__25;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__26;
static lean_once_cell_t lp_sidfinity_MV3_emitVibrato___redArg___closed__27_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitVibrato___redArg___closed__27;
extern lean_object* lp_sidfinity_I_dey;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitVibrato___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitVibrato(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitVibrato___boxed(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_MV3_emitExecVoice___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "sustain"};
static const lean_object* lp_sidfinity_MV3_emitExecVoice___closed__0 = (const lean_object*)&lp_sidfinity_MV3_emitExecVoice___closed__0_value;
static lean_once_cell_t lp_sidfinity_MV3_emitExecVoice___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitExecVoice___closed__1;
static const lean_string_object lp_sidfinity_MV3_emitExecVoice___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "effects_start"};
static const lean_object* lp_sidfinity_MV3_emitExecVoice___closed__2 = (const lean_object*)&lp_sidfinity_MV3_emitExecVoice___closed__2_value;
static const lean_string_object lp_sidfinity_MV3_emitExecVoice___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "porta_active"};
static const lean_object* lp_sidfinity_MV3_emitExecVoice___closed__3 = (const lean_object*)&lp_sidfinity_MV3_emitExecVoice___closed__3_value;
static const lean_string_object lp_sidfinity_MV3_emitExecVoice___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "no_porta"};
static const lean_object* lp_sidfinity_MV3_emitExecVoice___closed__4 = (const lean_object*)&lp_sidfinity_MV3_emitExecVoice___closed__4_value;
static lean_once_cell_t lp_sidfinity_MV3_emitExecVoice___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitExecVoice___closed__5;
static const lean_string_object lp_sidfinity_MV3_emitExecVoice___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "porta_down"};
static const lean_object* lp_sidfinity_MV3_emitExecVoice___closed__6 = (const lean_object*)&lp_sidfinity_MV3_emitExecVoice___closed__6_value;
static lean_once_cell_t lp_sidfinity_MV3_emitExecVoice___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitExecVoice___closed__7;
static const lean_string_object lp_sidfinity_MV3_emitExecVoice___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "porta_write"};
static const lean_object* lp_sidfinity_MV3_emitExecVoice___closed__8 = (const lean_object*)&lp_sidfinity_MV3_emitExecVoice___closed__8_value;
static lean_once_cell_t lp_sidfinity_MV3_emitExecVoice___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_emitExecVoice___closed__9;
static const lean_string_object lp_sidfinity_MV3_emitExecVoice___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "porta_done"};
static const lean_object* lp_sidfinity_MV3_emitExecVoice___closed__10 = (const lean_object*)&lp_sidfinity_MV3_emitExecVoice___closed__10_value;
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitExecVoice(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__19(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
uint8_t l_List_elem___at___00Lean_Meta_Occurrences_contains_spec__0(lean_object*, lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__17(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__14(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__24(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__8(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__3(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___closed__0;
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_List_appendTR___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_ctor_object lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*3 + 0, .m_other = 3, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(3) << 1) | 1)),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___closed__0 = (const lean_object*)&lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___closed__0_value;
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__10(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__16(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__11(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7___redArg(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "_v0"};
static const lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__0 = (const lean_object*)&lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__0_value;
static const lean_string_object lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "_v1"};
static const lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__1 = (const lean_object*)&lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__1_value;
static const lean_string_object lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "_v2"};
static const lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__2 = (const lean_object*)&lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__2_value;
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__20(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__15(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__13(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__12(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__9(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__18(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__2(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__0;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__1;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__2;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__3;
static const lean_ctor_object lp_sidfinity_MV3_generateSID___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__4 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__4_value;
static const lean_ctor_object lp_sidfinity_MV3_generateSID___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__4_value)}};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__5 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__5_value;
static const lean_ctor_object lp_sidfinity_MV3_generateSID___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__5_value)}};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__6 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__6_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "wave_data"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__7 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__7_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "i_wavebase"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__8 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__8_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "i_wavelen"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__9 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__9_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "i_waveloop"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__10 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__10_value;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__11;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__12;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__13;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_ctrl_0"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__14 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__14_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_ctrl_1"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__15 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__15_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_ctrl_2"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__16 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__16_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "v_inst_v0"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__17 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__17_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "v_inst_v1"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__18 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__18_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "v_inst_v2"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__19 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__19_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_pitch_v0"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__20 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__20_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_pitch_v1"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__21 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__21_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_pitch_v2"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__22 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__22_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_pwlo"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__23 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__23_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_pwhi"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__24 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__24_value;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__25_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__25;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__26;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__27_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__27;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__28_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__28;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__29_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__29;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__30_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__30;
static lean_once_cell_t lp_sidfinity_MV3_generateSID___redArg___closed__31_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__31;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__32_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "tempo_subtune"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__32 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__32_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__33_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "Commando"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__33 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__33_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__34_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "Rob Hubbard"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__34 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__34_value;
static const lean_string_object lp_sidfinity_MV3_generateSID___redArg___closed__35_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "1985 Elite"};
static const lean_object* lp_sidfinity_MV3_generateSID___redArg___closed__35 = (const lean_object*)&lp_sidfinity_MV3_generateSID___redArg___closed__35_value;
lean_object* lp_sidfinity_buildSID(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_generateSID___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_generateSID(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_generateSID___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_io_prim_handle_mk(lean_object*, uint8_t);
lean_object* lean_byte_array_mk(lean_object*);
lean_object* lean_io_prim_handle_write(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_writeFile(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_MV3_writeFile___boxed(lean_object*, lean_object*, lean_object*);
static uint16_t _init_lp_sidfinity_MV3_SID__BASE(void) {
_start:
{
uint16_t x_1; 
x_1 = 54272;
return x_1;
}
}
LEAN_EXPORT uint16_t lp_sidfinity_MV3_CodeBuilder_currentAddr(lean_object* x_1) {
_start:
{
lean_object* x_2; uint16_t x_3; lean_object* x_4; uint16_t x_5; uint16_t x_6; 
x_2 = lean_ctor_get(x_1, 0);
x_3 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_4 = lean_array_get_size(x_2);
x_5 = lean_uint16_of_nat(x_4);
x_6 = lean_uint16_add(x_3, x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_currentAddr___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_1);
lean_dec_ref(x_1);
x_3 = lean_box(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emit(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = l_Array_append___redArg(x_4, x_2);
lean_ctor_set(x_1, 0, x_5);
return x_1;
}
else
{
lean_object* x_6; uint16_t x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_6 = lean_ctor_get(x_1, 0);
x_7 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_8 = lean_ctor_get(x_1, 1);
x_9 = lean_ctor_get(x_1, 2);
x_10 = lean_ctor_get(x_1, 3);
lean_inc(x_10);
lean_inc(x_9);
lean_inc(x_8);
lean_inc(x_6);
lean_dec(x_1);
x_11 = l_Array_append___redArg(x_6, x_2);
x_12 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_12, 0, x_11);
lean_ctor_set(x_12, 1, x_8);
lean_ctor_set(x_12, 2, x_9);
lean_ctor_set(x_12, 3, x_10);
lean_ctor_set_uint16(x_12, sizeof(void*)*4, x_7);
return x_12;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emit___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_CodeBuilder_emit(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitInst(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_assembleInst(x_2);
if (lean_obj_tag(x_3) == 0)
{
return x_1;
}
else
{
lean_object* x_4; lean_object* x_5; 
x_4 = lean_ctor_get(x_3, 0);
lean_inc(x_4);
lean_dec_ref(x_3);
x_5 = lp_sidfinity_MV3_CodeBuilder_emit(x_1, x_4);
lean_dec(x_4);
return x_5;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitInst___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_label(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; uint16_t x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint16_t x_8; uint8_t x_9; 
x_3 = lean_ctor_get(x_1, 0);
lean_inc_ref(x_3);
x_4 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
x_6 = lean_ctor_get(x_1, 2);
lean_inc(x_6);
x_7 = lean_ctor_get(x_1, 3);
lean_inc(x_7);
x_8 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_1);
x_9 = !lean_is_exclusive(x_1);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; 
x_10 = lean_ctor_get(x_1, 3);
lean_dec(x_10);
x_11 = lean_ctor_get(x_1, 2);
lean_dec(x_11);
x_12 = lean_ctor_get(x_1, 1);
lean_dec(x_12);
x_13 = lean_ctor_get(x_1, 0);
lean_dec(x_13);
x_14 = lean_box(x_8);
x_15 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_15, 0, x_2);
lean_ctor_set(x_15, 1, x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_5);
lean_ctor_set(x_1, 1, x_16);
return x_1;
}
else
{
lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; 
lean_dec(x_1);
x_17 = lean_box(x_8);
x_18 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_18, 0, x_2);
lean_ctor_set(x_18, 1, x_17);
x_19 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_19, 0, x_18);
lean_ctor_set(x_19, 1, x_5);
x_20 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_20, 0, x_3);
lean_ctor_set(x_20, 1, x_19);
lean_ctor_set(x_20, 2, x_6);
lean_ctor_set(x_20, 3, x_7);
lean_ctor_set_uint16(x_20, sizeof(void*)*4, x_4);
return x_20;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_3; 
x_3 = lean_box(0);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_4 = lean_ctor_get(x_2, 0);
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_4, 0);
x_7 = lean_ctor_get(x_4, 1);
x_8 = lean_string_dec_eq(x_1, x_6);
if (x_8 == 0)
{
x_2 = x_5;
goto _start;
}
else
{
lean_object* x_10; 
lean_inc(x_7);
x_10 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_10, 0, x_7);
return x_10;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___redArg(x_1, x_2);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_lookupLabel(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_ctor_get(x_1, 1);
x_4 = lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___redArg(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_lookupLabel___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_CodeBuilder_lookupLabel(x_1, x_2);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___redArg(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_List_lookup___at___00MV3_CodeBuilder_lookupLabel_spec__0(x_1, x_2, x_3);
lean_dec(x_3);
lean_dec_ref(x_2);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static uint8_t _init_lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__1(void) {
_start:
{
lean_object* x_1; uint8_t x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_int8_of_nat(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = lean_uint8_once(&lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__1);
x_2 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_2, 0, x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitBranch(lean_object* x_1, uint8_t x_2, lean_object* x_3) {
_start:
{
uint16_t x_4; uint8_t x_5; lean_object* x_42; lean_object* x_43; 
x_4 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_1);
x_42 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__2);
x_43 = lp_sidfinity_opcode(x_2, x_42);
if (lean_obj_tag(x_43) == 0)
{
uint8_t x_44; 
x_44 = 0;
x_5 = x_44;
goto block_41;
}
else
{
lean_object* x_45; uint8_t x_46; 
x_45 = lean_ctor_get(x_43, 0);
lean_inc(x_45);
lean_dec_ref(x_43);
x_46 = lean_unbox(x_45);
lean_dec(x_45);
x_5 = x_46;
goto block_41;
}
block_41:
{
uint8_t x_6; 
x_6 = !lean_is_exclusive(x_1);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_7 = lean_ctor_get(x_1, 0);
x_8 = lean_ctor_get(x_1, 2);
x_9 = lean_array_get_size(x_7);
x_10 = lean_unsigned_to_nat(1u);
x_11 = lean_nat_add(x_9, x_10);
x_12 = 1;
x_13 = lean_alloc_ctor(0, 2, 3);
lean_ctor_set(x_13, 0, x_11);
lean_ctor_set(x_13, 1, x_3);
lean_ctor_set_uint8(x_13, sizeof(void*)*2 + 2, x_12);
lean_ctor_set_uint16(x_13, sizeof(void*)*2, x_4);
x_14 = 0;
x_15 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0);
x_16 = lean_box(x_5);
x_17 = lean_array_push(x_15, x_16);
x_18 = lean_box(x_14);
x_19 = lean_array_push(x_17, x_18);
x_20 = l_Array_append___redArg(x_7, x_19);
lean_dec_ref(x_19);
x_21 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_21, 0, x_13);
lean_ctor_set(x_21, 1, x_8);
lean_ctor_set(x_1, 2, x_21);
lean_ctor_set(x_1, 0, x_20);
return x_1;
}
else
{
lean_object* x_22; uint16_t x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; uint8_t x_30; lean_object* x_31; uint8_t x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; 
x_22 = lean_ctor_get(x_1, 0);
x_23 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_24 = lean_ctor_get(x_1, 1);
x_25 = lean_ctor_get(x_1, 2);
x_26 = lean_ctor_get(x_1, 3);
lean_inc(x_26);
lean_inc(x_25);
lean_inc(x_24);
lean_inc(x_22);
lean_dec(x_1);
x_27 = lean_array_get_size(x_22);
x_28 = lean_unsigned_to_nat(1u);
x_29 = lean_nat_add(x_27, x_28);
x_30 = 1;
x_31 = lean_alloc_ctor(0, 2, 3);
lean_ctor_set(x_31, 0, x_29);
lean_ctor_set(x_31, 1, x_3);
lean_ctor_set_uint8(x_31, sizeof(void*)*2 + 2, x_30);
lean_ctor_set_uint16(x_31, sizeof(void*)*2, x_4);
x_32 = 0;
x_33 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitBranch___closed__0);
x_34 = lean_box(x_5);
x_35 = lean_array_push(x_33, x_34);
x_36 = lean_box(x_32);
x_37 = lean_array_push(x_35, x_36);
x_38 = l_Array_append___redArg(x_22, x_37);
lean_dec_ref(x_37);
x_39 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_39, 0, x_31);
lean_ctor_set(x_39, 1, x_25);
x_40 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_40, 0, x_38);
lean_ctor_set(x_40, 1, x_24);
lean_ctor_set(x_40, 2, x_39);
lean_ctor_set(x_40, 3, x_26);
lean_ctor_set_uint16(x_40, sizeof(void*)*4, x_23);
return x_40;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitBranch___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1, x_4, x_3);
return x_5;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(3u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(lean_object* x_1, uint8_t x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; 
switch (x_2) {
case 32:
{
uint8_t x_44; 
x_44 = 76;
x_4 = x_44;
goto block_43;
}
case 33:
{
uint8_t x_45; 
x_45 = 32;
x_4 = x_45;
goto block_43;
}
default: 
{
uint8_t x_46; 
x_46 = 76;
x_4 = x_46;
goto block_43;
}
}
block_43:
{
lean_object* x_5; uint16_t x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; uint8_t x_13; uint16_t x_14; uint8_t x_15; 
x_5 = lean_ctor_get(x_1, 0);
lean_inc_ref(x_5);
x_6 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_7 = lean_ctor_get(x_1, 1);
lean_inc(x_7);
x_8 = lean_ctor_get(x_1, 2);
lean_inc(x_8);
x_9 = lean_ctor_get(x_1, 3);
lean_inc(x_9);
x_10 = lean_array_get_size(x_5);
x_11 = lean_unsigned_to_nat(1u);
x_12 = lean_nat_add(x_10, x_11);
x_13 = 0;
x_14 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_1);
x_15 = !lean_is_exclusive(x_1);
if (x_15 == 0)
{
lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; 
x_16 = lean_ctor_get(x_1, 3);
lean_dec(x_16);
x_17 = lean_ctor_get(x_1, 2);
lean_dec(x_17);
x_18 = lean_ctor_get(x_1, 1);
lean_dec(x_18);
x_19 = lean_ctor_get(x_1, 0);
lean_dec(x_19);
x_20 = lean_alloc_ctor(0, 2, 3);
lean_ctor_set(x_20, 0, x_12);
lean_ctor_set(x_20, 1, x_3);
lean_ctor_set_uint8(x_20, sizeof(void*)*2 + 2, x_13);
lean_ctor_set_uint16(x_20, sizeof(void*)*2, x_14);
x_21 = 0;
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_23 = lean_box(x_4);
x_24 = lean_array_push(x_22, x_23);
x_25 = lean_box(x_21);
x_26 = lean_array_push(x_24, x_25);
x_27 = lean_box(x_21);
x_28 = lean_array_push(x_26, x_27);
x_29 = l_Array_append___redArg(x_5, x_28);
lean_dec_ref(x_28);
x_30 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_30, 0, x_20);
lean_ctor_set(x_30, 1, x_8);
lean_ctor_set(x_1, 2, x_30);
lean_ctor_set(x_1, 0, x_29);
return x_1;
}
else
{
lean_object* x_31; uint8_t x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; 
lean_dec(x_1);
x_31 = lean_alloc_ctor(0, 2, 3);
lean_ctor_set(x_31, 0, x_12);
lean_ctor_set(x_31, 1, x_3);
lean_ctor_set_uint8(x_31, sizeof(void*)*2 + 2, x_13);
lean_ctor_set_uint16(x_31, sizeof(void*)*2, x_14);
x_32 = 0;
x_33 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_34 = lean_box(x_4);
x_35 = lean_array_push(x_33, x_34);
x_36 = lean_box(x_32);
x_37 = lean_array_push(x_35, x_36);
x_38 = lean_box(x_32);
x_39 = lean_array_push(x_37, x_38);
x_40 = l_Array_append___redArg(x_5, x_39);
lean_dec_ref(x_39);
x_41 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_41, 0, x_31);
lean_ctor_set(x_41, 1, x_8);
x_42 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_42, 0, x_40);
lean_ctor_set(x_42, 1, x_7);
lean_ctor_set(x_42, 2, x_41);
lean_ctor_set(x_42, 3, x_9);
lean_ctor_set_uint16(x_42, sizeof(void*)*4, x_6);
return x_42;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1, x_4, x_3);
return x_5;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 189;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 185;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 157;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsX___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 222;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitDecAbsX___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 254;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitIncAbsX(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitIncAbsX___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_4 = lean_ctor_get(x_2, 0);
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_4, 0);
x_7 = lean_ctor_get(x_4, 1);
x_8 = lp_sidfinity_MV3_CodeBuilder_lookupLabel(x_1, x_7);
if (lean_obj_tag(x_8) == 0)
{
x_2 = x_5;
goto _start;
}
else
{
lean_object* x_10; uint16_t x_11; uint8_t x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; uint16_t x_17; uint16_t x_18; uint16_t x_19; uint8_t x_20; lean_object* x_21; lean_object* x_22; 
x_10 = lean_ctor_get(x_8, 0);
lean_inc(x_10);
lean_dec_ref(x_8);
x_11 = lean_unbox(x_10);
x_12 = lean_uint16_to_uint8(x_11);
x_13 = lean_box(x_12);
x_14 = lean_array_set(x_3, x_6, x_13);
x_15 = lean_unsigned_to_nat(1u);
x_16 = lean_nat_add(x_6, x_15);
x_17 = 8;
x_18 = lean_unbox(x_10);
lean_dec(x_10);
x_19 = lean_uint16_shift_right(x_18, x_17);
x_20 = lean_uint16_to_uint8(x_19);
x_21 = lean_box(x_20);
x_22 = lean_array_set(x_14, x_16, x_21);
lean_dec(x_16);
x_2 = x_5;
x_3 = x_22;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___redArg(x_1, x_2, x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(256u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; uint16_t x_9; lean_object* x_10; 
x_4 = lean_ctor_get(x_2, 0);
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_4, 0);
x_7 = lean_ctor_get(x_4, 1);
x_8 = lean_ctor_get_uint8(x_4, sizeof(void*)*2 + 2);
x_9 = lean_ctor_get_uint16(x_4, sizeof(void*)*2);
x_10 = lp_sidfinity_MV3_CodeBuilder_lookupLabel(x_1, x_7);
if (lean_obj_tag(x_10) == 0)
{
x_2 = x_5;
goto _start;
}
else
{
if (x_8 == 0)
{
lean_object* x_12; uint16_t x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; uint16_t x_19; uint16_t x_20; uint16_t x_21; uint8_t x_22; lean_object* x_23; lean_object* x_24; 
x_12 = lean_ctor_get(x_10, 0);
lean_inc(x_12);
lean_dec_ref(x_10);
x_13 = lean_unbox(x_12);
x_14 = lean_uint16_to_uint8(x_13);
x_15 = lean_box(x_14);
x_16 = lean_array_set(x_3, x_6, x_15);
x_17 = lean_unsigned_to_nat(1u);
x_18 = lean_nat_add(x_6, x_17);
x_19 = 8;
x_20 = lean_unbox(x_12);
lean_dec(x_12);
x_21 = lean_uint16_shift_right(x_20, x_19);
x_22 = lean_uint16_to_uint8(x_21);
x_23 = lean_box(x_22);
x_24 = lean_array_set(x_16, x_18, x_23);
lean_dec(x_18);
x_2 = x_5;
x_3 = x_24;
goto _start;
}
else
{
lean_object* x_26; uint16_t x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; uint8_t x_38; lean_object* x_39; lean_object* x_40; 
x_26 = lean_ctor_get(x_10, 0);
lean_inc(x_26);
lean_dec_ref(x_10);
x_27 = lean_unbox(x_26);
lean_dec(x_26);
x_28 = lean_uint16_to_nat(x_27);
x_29 = lean_nat_to_int(x_28);
x_30 = lean_uint16_to_nat(x_9);
x_31 = lean_nat_to_int(x_30);
x_32 = lean_obj_once(&lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0, &lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0_once, _init_lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0);
x_33 = lean_int_add(x_31, x_32);
lean_dec(x_31);
x_34 = lean_int_sub(x_29, x_33);
lean_dec(x_33);
lean_dec(x_29);
x_35 = lean_obj_once(&lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1, &lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1_once, _init_lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1);
x_36 = lean_int_emod(x_34, x_35);
lean_dec(x_34);
x_37 = l_Int_toNat(x_36);
lean_dec(x_36);
x_38 = lean_uint8_of_nat(x_37);
lean_dec(x_37);
x_39 = lean_box(x_38);
x_40 = lean_array_set(x_3, x_6, x_39);
x_2 = x_5;
x_3 = x_40;
goto _start;
}
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_2, x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
if (lean_obj_tag(x_3) == 0)
{
return x_4;
}
else
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; uint8_t x_9; uint16_t x_10; lean_object* x_11; 
x_5 = lean_ctor_get(x_3, 0);
x_6 = lean_ctor_get(x_3, 1);
x_7 = lean_ctor_get(x_5, 0);
x_8 = lean_ctor_get(x_5, 1);
x_9 = lean_ctor_get_uint8(x_5, sizeof(void*)*2 + 2);
x_10 = lean_ctor_get_uint16(x_5, sizeof(void*)*2);
x_11 = lp_sidfinity_MV3_CodeBuilder_lookupLabel(x_1, x_8);
if (lean_obj_tag(x_11) == 0)
{
lean_object* x_12; 
x_12 = lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_6, x_4);
return x_12;
}
else
{
if (x_9 == 0)
{
lean_object* x_13; uint16_t x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; uint16_t x_20; uint16_t x_21; uint16_t x_22; uint8_t x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; 
x_13 = lean_ctor_get(x_11, 0);
lean_inc(x_13);
lean_dec_ref(x_11);
x_14 = lean_unbox(x_13);
x_15 = lean_uint16_to_uint8(x_14);
x_16 = lean_box(x_15);
x_17 = lean_array_set(x_4, x_7, x_16);
x_18 = lean_unsigned_to_nat(1u);
x_19 = lean_nat_add(x_7, x_18);
x_20 = 8;
x_21 = lean_unbox(x_13);
lean_dec(x_13);
x_22 = lean_uint16_shift_right(x_21, x_20);
x_23 = lean_uint16_to_uint8(x_22);
x_24 = lean_box(x_23);
x_25 = lean_array_set(x_17, x_19, x_24);
lean_dec(x_19);
x_26 = lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_6, x_25);
return x_26;
}
else
{
lean_object* x_27; uint16_t x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; uint8_t x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; 
x_27 = lean_ctor_get(x_11, 0);
lean_inc(x_27);
lean_dec_ref(x_11);
x_28 = lean_unbox(x_27);
lean_dec(x_27);
x_29 = lean_uint16_to_nat(x_28);
x_30 = lean_nat_to_int(x_29);
x_31 = lean_uint16_to_nat(x_10);
x_32 = lean_nat_to_int(x_31);
x_33 = lean_obj_once(&lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0, &lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0_once, _init_lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0);
x_34 = lean_int_add(x_32, x_33);
lean_dec(x_32);
x_35 = lean_int_sub(x_30, x_34);
lean_dec(x_34);
lean_dec(x_30);
x_36 = lean_obj_once(&lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1, &lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1_once, _init_lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1);
x_37 = lean_int_emod(x_35, x_36);
lean_dec(x_35);
x_38 = l_Int_toNat(x_37);
lean_dec(x_37);
x_39 = lean_uint8_of_nat(x_38);
lean_dec(x_38);
x_40 = lean_box(x_39);
x_41 = lean_array_set(x_4, x_7, x_40);
x_42 = lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_6, x_41);
return x_42;
}
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___redArg(x_1, x_2, x_3, x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_resolve(lean_object* x_1) {
_start:
{
lean_object* x_2; uint16_t x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; uint8_t x_9; 
x_2 = lean_ctor_get(x_1, 0);
x_3 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_4 = lean_ctor_get(x_1, 1);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 2);
x_6 = lean_ctor_get(x_1, 3);
lean_inc_ref(x_2);
x_7 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___redArg(x_1, x_5, x_5, x_2);
x_8 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___redArg(x_1, x_6, x_7);
x_9 = !lean_is_exclusive(x_1);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_10 = lean_ctor_get(x_1, 3);
lean_dec(x_10);
x_11 = lean_ctor_get(x_1, 2);
lean_dec(x_11);
x_12 = lean_ctor_get(x_1, 1);
lean_dec(x_12);
x_13 = lean_ctor_get(x_1, 0);
lean_dec(x_13);
x_14 = lean_box(0);
lean_ctor_set(x_1, 3, x_14);
lean_ctor_set(x_1, 2, x_14);
lean_ctor_set(x_1, 0, x_8);
return x_1;
}
else
{
lean_object* x_15; lean_object* x_16; 
lean_dec(x_1);
x_15 = lean_box(0);
x_16 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_16, 0, x_8);
lean_ctor_set(x_16, 1, x_4);
lean_ctor_set(x_16, 2, x_15);
lean_ctor_set(x_16, 3, x_15);
lean_ctor_set_uint16(x_16, sizeof(void*)*4, x_3);
return x_16;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___redArg(x_1, x_2, x_3, x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___redArg(x_1, x_3, x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__1(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_3, x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00MV3_CodeBuilder_resolve_spec__0_spec__0(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitData(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_array_mk(x_2);
x_4 = lp_sidfinity_MV3_CodeBuilder_emit(x_1, x_3);
lean_dec_ref(x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitByte___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(1u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitByte(lean_object* x_1, uint8_t x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_3 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitByte___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitByte___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitByte___closed__0);
x_4 = lean_box(x_2);
x_5 = lean_array_push(x_3, x_4);
x_6 = lp_sidfinity_MV3_CodeBuilder_emit(x_1, x_5);
lean_dec_ref(x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitByte___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_1, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 153;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbsY___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbsYL(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1, x_2);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 173;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitLdaAbs(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitLdaAbs___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 141;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitStaAbs(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitStaAbs___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 221;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsX___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 217;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__0, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__0_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__1, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__1_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(1u);
x_8 = lean_nat_add(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2);
x_11 = l_Array_append___redArg(x_4, x_10);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_9);
lean_ctor_set(x_12, 1, x_5);
lean_ctor_set(x_1, 3, x_12);
lean_ctor_set(x_1, 0, x_11);
return x_1;
}
else
{
lean_object* x_13; uint16_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_13 = lean_ctor_get(x_1, 0);
x_14 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_15 = lean_ctor_get(x_1, 1);
x_16 = lean_ctor_get(x_1, 2);
x_17 = lean_ctor_get(x_1, 3);
lean_inc(x_17);
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_13);
lean_dec(x_1);
x_18 = lean_array_get_size(x_13);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_2);
x_22 = lean_obj_once(&lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2, &lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2_once, _init_lp_sidfinity_MV3_CodeBuilder_emitCmpAbsY___closed__2);
x_23 = l_Array_append___redArg(x_13, x_22);
x_24 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_24, 0, x_21);
lean_ctor_set(x_24, 1, x_17);
x_25 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_15);
lean_ctor_set(x_25, 2, x_16);
lean_ctor_set(x_25, 3, x_24);
lean_ctor_set_uint16(x_25, sizeof(void*)*4, x_14);
return x_25;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_CodeBuilder_addAbsFixup(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 3);
x_6 = lean_array_get_size(x_4);
x_7 = lean_unsigned_to_nat(2u);
x_8 = lean_nat_sub(x_6, x_7);
x_9 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_10 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_10, 0, x_9);
lean_ctor_set(x_10, 1, x_5);
lean_ctor_set(x_1, 3, x_10);
return x_1;
}
else
{
lean_object* x_11; uint16_t x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_11 = lean_ctor_get(x_1, 0);
x_12 = lean_ctor_get_uint16(x_1, sizeof(void*)*4);
x_13 = lean_ctor_get(x_1, 1);
x_14 = lean_ctor_get(x_1, 2);
x_15 = lean_ctor_get(x_1, 3);
lean_inc(x_15);
lean_inc(x_14);
lean_inc(x_13);
lean_inc(x_11);
lean_dec(x_1);
x_16 = lean_array_get_size(x_11);
x_17 = lean_unsigned_to_nat(2u);
x_18 = lean_nat_sub(x_16, x_17);
x_19 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_19, 0, x_18);
lean_ctor_set(x_19, 1, x_2);
x_20 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_20, 0, x_19);
lean_ctor_set(x_20, 1, x_15);
x_21 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_21, 0, x_11);
lean_ctor_set(x_21, 1, x_13);
lean_ctor_set(x_21, 2, x_14);
lean_ctor_set(x_21, 3, x_20);
lean_ctor_set_uint16(x_21, sizeof(void*)*4, x_12);
return x_21;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynRefLoad(lean_object* x_1, lean_object* x_2) {
_start:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_3; uint8_t x_4; lean_object* x_5; lean_object* x_6; 
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
lean_dec_ref(x_2);
x_4 = lean_uint8_of_nat(x_3);
lean_dec(x_3);
x_5 = lp_sidfinity_I_lda__imm(x_4);
x_6 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_5);
lean_dec_ref(x_5);
return x_6;
}
case 1:
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; 
x_7 = lean_ctor_get(x_2, 0);
lean_inc(x_7);
x_8 = lean_ctor_get(x_2, 1);
lean_inc(x_8);
lean_dec_ref(x_2);
x_9 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_10 = l_Nat_reprFast(x_8);
x_11 = lean_string_append(x_9, x_10);
lean_dec_ref(x_10);
x_12 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__1));
x_13 = lean_string_append(x_11, x_12);
x_14 = l_Nat_reprFast(x_7);
x_15 = lean_string_append(x_13, x_14);
lean_dec_ref(x_14);
x_16 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbs(x_1, x_15);
return x_16;
}
case 2:
{
lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_17 = lean_ctor_get(x_2, 0);
lean_inc(x_17);
lean_dec_ref(x_2);
x_18 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__2));
x_19 = l_Nat_reprFast(x_17);
x_20 = lean_string_append(x_18, x_19);
lean_dec_ref(x_19);
x_21 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbs(x_1, x_20);
return x_21;
}
case 3:
{
lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; 
x_22 = lean_ctor_get(x_2, 0);
lean_inc(x_22);
lean_dec_ref(x_2);
x_23 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__3));
x_24 = l_Nat_reprFast(x_22);
x_25 = lean_string_append(x_23, x_24);
lean_dec_ref(x_24);
x_26 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbs(x_1, x_25);
return x_26;
}
default: 
{
lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; 
x_27 = lean_ctor_get(x_2, 0);
lean_inc(x_27);
lean_dec_ref(x_2);
x_28 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__4));
x_29 = l_Nat_reprFast(x_27);
x_30 = lean_string_append(x_28, x_29);
lean_dec_ref(x_29);
x_31 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbs(x_1, x_30);
return x_31;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFreqSlotStore(lean_object* x_1, uint8_t x_2, lean_object* x_3) {
_start:
{
if (x_2 == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitFreqSlotStore___closed__0));
x_5 = l_Nat_reprFast(x_3);
x_6 = lean_string_append(x_4, x_5);
lean_dec_ref(x_5);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitStaAbs(x_1, x_6);
return x_7;
}
else
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitFreqSlotStore___closed__1));
x_9 = l_Nat_reprFast(x_3);
x_10 = lean_string_append(x_8, x_9);
lean_dec_ref(x_9);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitStaAbs(x_1, x_10);
return x_11;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFreqSlotStore___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_sidfinity_MV3_emitFreqSlotStore(x_1, x_4, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicFreqEntry(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; 
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
x_4 = lean_ctor_get(x_2, 1);
lean_inc_ref(x_4);
x_5 = lean_ctor_get(x_2, 2);
lean_inc_ref(x_5);
lean_dec_ref(x_2);
x_6 = lp_sidfinity_MV3_emitDynRefLoad(x_1, x_4);
x_7 = 1;
lean_inc(x_3);
x_8 = lp_sidfinity_MV3_emitFreqSlotStore(x_6, x_7, x_3);
x_9 = lp_sidfinity_MV3_emitDynRefLoad(x_8, x_5);
x_10 = 0;
x_11 = lp_sidfinity_MV3_emitFreqSlotStore(x_9, x_10, x_3);
return x_11;
}
}
LEAN_EXPORT uint8_t lp_sidfinity_MV3_phaseMatches(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
if (lean_obj_tag(x_2) == 0)
{
uint8_t x_3; 
x_3 = 1;
return x_3;
}
else
{
uint8_t x_4; 
x_4 = 0;
return x_4;
}
}
else
{
if (lean_obj_tag(x_2) == 1)
{
lean_object* x_5; lean_object* x_6; uint8_t x_7; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_2, 0);
x_7 = lean_nat_dec_eq(x_5, x_6);
return x_7;
}
else
{
uint8_t x_8; 
x_8 = 0;
return x_8;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_phaseMatches___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lp_sidfinity_MV3_phaseMatches(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
x_4 = lean_box(x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicEntryIfPhase(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; uint8_t x_5; 
x_4 = lean_ctor_get(x_3, 3);
x_5 = lp_sidfinity_MV3_phaseMatches(x_4, x_1);
if (x_5 == 0)
{
lean_dec_ref(x_3);
return x_2;
}
else
{
lean_object* x_6; 
x_6 = lp_sidfinity_MV3_emitDynamicFreqEntry(x_2, x_3);
return x_6;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicEntryIfPhase___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_MV3_emitDynamicEntryIfPhase(x_1, x_2, x_3);
lean_dec(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
if (lean_obj_tag(x_3) == 0)
{
return x_2;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_4 = lean_ctor_get(x_3, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_3, 1);
lean_inc(x_5);
lean_dec_ref(x_3);
x_6 = lp_sidfinity_MV3_emitDynamicEntryIfPhase(x_1, x_2, x_4);
x_2 = x_6;
x_3 = x_5;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0(x_1, x_2, x_3);
lean_dec(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicUpdatesForPhase(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0(x_3, x_1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitDynamicUpdatesForPhase___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_MV3_emitDynamicUpdatesForPhase(x_1, x_2, x_3);
lean_dec(x_3);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitFlagRule___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 251;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitFlagRule___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFlagRule(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; uint8_t x_22; lean_object* x_23; lean_object* x_24; uint8_t x_25; uint8_t x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; uint8_t x_30; lean_object* x_31; uint8_t x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; uint8_t x_37; lean_object* x_38; lean_object* x_39; 
x_5 = lean_ctor_get(x_4, 0);
x_6 = lean_ctor_get(x_5, 1);
x_7 = lean_ctor_get(x_4, 1);
x_8 = lean_ctor_get(x_5, 0);
x_9 = lean_ctor_get(x_6, 0);
x_10 = lean_ctor_get(x_6, 1);
x_11 = ((lean_object*)(lp_sidfinity_MV3_emitFlagRule___closed__0));
x_12 = l_Nat_reprFast(x_1);
x_13 = lean_string_append(x_11, x_12);
lean_dec_ref(x_12);
x_14 = ((lean_object*)(lp_sidfinity_MV3_emitFlagRule___closed__1));
x_15 = lean_string_append(x_13, x_14);
x_16 = lean_unsigned_to_nat(1u);
x_17 = lean_nat_add(x_7, x_16);
x_18 = l_Nat_reprFast(x_17);
x_19 = lean_string_append(x_15, x_18);
lean_dec_ref(x_18);
x_20 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_21 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_20);
x_22 = lean_uint8_of_nat(x_8);
x_23 = lp_sidfinity_I_and__imm(x_22);
x_24 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_21, x_23);
lean_dec_ref(x_23);
x_25 = 11;
x_26 = lean_uint8_of_nat(x_9);
x_27 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_27, 0, x_26);
x_28 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_28, 0, x_27);
lean_ctor_set_uint8(x_28, sizeof(void*)*1, x_25);
x_29 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_24, x_28);
lean_dec_ref(x_28);
x_30 = 27;
lean_inc_ref(x_19);
x_31 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_29, x_30, x_19);
x_32 = lean_uint8_of_nat(x_10);
x_33 = lp_sidfinity_I_lda__imm(x_32);
x_34 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_31, x_33);
lean_dec_ref(x_33);
x_35 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_36 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_34, x_35);
x_37 = 32;
x_38 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_36, x_37, x_2);
x_39 = lp_sidfinity_MV3_CodeBuilder_label(x_38, x_19);
return x_39;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitFlagRule___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_MV3_emitFlagRule(x_1, x_2, x_3, x_4);
lean_dec_ref(x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOp_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
if (lean_obj_tag(x_4) == 0)
{
lean_dec_ref(x_2);
lean_dec(x_1);
return x_3;
}
else
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_5 = lean_ctor_get(x_4, 0);
x_6 = lean_ctor_get(x_4, 1);
lean_inc_ref(x_2);
lean_inc(x_1);
x_7 = lp_sidfinity_MV3_emitFlagRule(x_1, x_2, x_3, x_5);
x_3 = x_7;
x_4 = x_6;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOp_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOp_spec__0(x_1, x_2, x_3, x_4);
lean_dec(x_4);
return x_5;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_sidfinity_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_sidfinity_I_adc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__4(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_sidfinity_I_ldy__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNoteLoadOp(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; 
lean_dec(x_3);
x_4 = lean_ctor_get(x_2, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_2, 1);
lean_inc(x_5);
lean_dec_ref(x_2);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_7 = l_Nat_reprFast(x_4);
x_8 = lean_string_append(x_6, x_7);
lean_dec_ref(x_7);
x_9 = lp_sidfinity_I_clc;
x_10 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_9);
lean_inc_ref(x_8);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_10, x_8);
x_12 = lean_uint8_of_nat(x_5);
lean_dec(x_5);
x_13 = lp_sidfinity_I_adc__imm(x_12);
x_14 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_13);
lean_dec_ref(x_13);
x_15 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_14, x_8);
return x_15;
}
case 1:
{
lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; 
x_16 = lean_ctor_get(x_2, 0);
lean_inc(x_16);
x_17 = lean_ctor_get(x_2, 1);
lean_inc(x_17);
lean_dec_ref(x_2);
x_18 = ((lean_object*)(lp_sidfinity_MV3_emitFlagRule___closed__0));
lean_inc(x_3);
x_19 = l_Nat_reprFast(x_3);
x_20 = lean_string_append(x_18, x_19);
lean_dec_ref(x_19);
x_21 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__0));
x_22 = lean_string_append(x_20, x_21);
x_23 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_24 = l_Nat_reprFast(x_16);
x_25 = lean_string_append(x_23, x_24);
lean_dec_ref(x_24);
x_26 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_27 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_26);
x_28 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_29 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_27, x_28);
x_30 = l_List_lengthTR___redArg(x_17);
x_31 = l_List_range(x_30);
x_32 = l_List_zipWith___at___00List_zip_spec__0___redArg(x_17, x_31);
lean_inc_ref(x_22);
x_33 = lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOp_spec__0(x_3, x_22, x_29, x_32);
lean_dec(x_32);
x_34 = lp_sidfinity_MV3_CodeBuilder_label(x_33, x_22);
x_35 = lp_sidfinity_I_clc;
x_36 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_34, x_35);
lean_inc_ref(x_25);
x_37 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_36, x_25);
x_38 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_39 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_37, x_38);
x_40 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_39, x_25);
return x_40;
}
case 2:
{
lean_object* x_41; lean_object* x_42; uint8_t x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; 
lean_dec(x_3);
x_41 = lean_ctor_get(x_2, 0);
lean_inc(x_41);
x_42 = lean_ctor_get(x_2, 1);
lean_inc(x_42);
lean_dec_ref(x_2);
x_43 = lean_uint8_of_nat(x_42);
lean_dec(x_42);
x_44 = lp_sidfinity_I_lda__imm(x_43);
x_45 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_44);
lean_dec_ref(x_44);
x_46 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_47 = l_Nat_reprFast(x_41);
x_48 = lean_string_append(x_46, x_47);
lean_dec_ref(x_47);
x_49 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_45, x_48);
return x_49;
}
case 3:
{
lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; uint8_t x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; 
x_50 = lean_ctor_get(x_2, 0);
lean_inc(x_50);
lean_dec_ref(x_2);
x_51 = ((lean_object*)(lp_sidfinity_MV3_emitFlagRule___closed__0));
x_52 = l_Nat_reprFast(x_3);
x_53 = lean_string_append(x_51, x_52);
lean_dec_ref(x_52);
x_54 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__3));
x_55 = lean_string_append(x_53, x_54);
x_56 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__4, &lp_sidfinity_MV3_emitNoteLoadOp___closed__4_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__4);
x_57 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_56);
x_58 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__6));
x_59 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_57, x_58);
x_60 = 27;
lean_inc_ref(x_55);
x_61 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_59, x_60, x_55);
x_62 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_63 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_61, x_62);
x_64 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_65 = l_Nat_reprFast(x_50);
x_66 = lean_string_append(x_64, x_65);
lean_dec_ref(x_65);
x_67 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_63, x_66);
x_68 = lp_sidfinity_MV3_CodeBuilder_label(x_67, x_55);
return x_68;
}
default: 
{
lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; uint8_t x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; uint8_t x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; 
x_69 = lean_ctor_get(x_2, 0);
lean_inc(x_69);
x_70 = lean_ctor_get(x_2, 1);
lean_inc(x_70);
lean_dec_ref(x_2);
x_71 = ((lean_object*)(lp_sidfinity_MV3_emitFlagRule___closed__0));
x_72 = l_Nat_reprFast(x_3);
x_73 = lean_string_append(x_71, x_72);
lean_dec_ref(x_72);
x_74 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__7));
x_75 = lean_string_append(x_73, x_74);
x_76 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__4, &lp_sidfinity_MV3_emitNoteLoadOp___closed__4_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__4);
x_77 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_76);
x_78 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__6));
x_79 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_77, x_78);
x_80 = 27;
lean_inc_ref(x_75);
x_81 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_79, x_80, x_75);
x_82 = lp_sidfinity_I_clc;
x_83 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_81, x_82);
x_84 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_85 = l_Nat_reprFast(x_69);
x_86 = lean_string_append(x_84, x_85);
lean_dec_ref(x_85);
lean_inc_ref(x_86);
x_87 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_83, x_86);
x_88 = lean_uint8_of_nat(x_70);
lean_dec(x_70);
x_89 = lp_sidfinity_I_adc__imm(x_88);
x_90 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_87, x_89);
lean_dec_ref(x_89);
x_91 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_90, x_86);
x_92 = lp_sidfinity_MV3_CodeBuilder_label(x_91, x_75);
return x_92;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOps_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
return x_1;
}
else
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
x_4 = lean_ctor_get(x_2, 1);
lean_inc(x_4);
lean_dec_ref(x_2);
x_5 = lean_ctor_get(x_3, 0);
lean_inc(x_5);
x_6 = lean_ctor_get(x_3, 1);
lean_inc(x_6);
lean_dec(x_3);
x_7 = lp_sidfinity_MV3_emitNoteLoadOp(x_1, x_5, x_6);
x_1 = x_7;
x_2 = x_4;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNoteLoadOps(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_3 = l_List_lengthTR___redArg(x_2);
x_4 = l_List_range(x_3);
x_5 = l_List_zipWith___at___00List_zip_spec__0___redArg(x_2, x_4);
x_6 = lp_sidfinity_List_foldl___at___00MV3_emitNoteLoadOps_spec__0(x_1, x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPatternEndOp(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; 
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
lean_dec_ref(x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_7 = l_Nat_reprFast(x_3);
x_8 = lean_string_append(x_6, x_7);
lean_dec_ref(x_7);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_5, x_8);
return x_9;
}
else
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; uint8_t x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_10 = lean_ctor_get(x_2, 0);
lean_inc(x_10);
x_11 = lean_ctor_get(x_2, 1);
lean_inc(x_11);
lean_dec_ref(x_2);
x_12 = lp_sidfinity_I_clc;
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_12);
x_14 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
x_15 = l_Nat_reprFast(x_10);
x_16 = lean_string_append(x_14, x_15);
lean_dec_ref(x_15);
lean_inc_ref(x_16);
x_17 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_13, x_16);
x_18 = lean_uint8_of_nat(x_11);
lean_dec(x_11);
x_19 = lp_sidfinity_I_adc__imm(x_18);
x_20 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_17, x_19);
lean_dec_ref(x_19);
x_21 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_20, x_16);
return x_21;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitPatternEndOps_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
return x_1;
}
else
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
x_4 = lean_ctor_get(x_2, 1);
lean_inc(x_4);
lean_dec_ref(x_2);
x_5 = lp_sidfinity_MV3_emitPatternEndOp(x_1, x_3);
x_1 = x_5;
x_2 = x_4;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPatternEndOps(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_List_foldl___at___00MV3_emitPatternEndOps_spec__0(x_1, x_2);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 251;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 251;
x_2 = lp_sidfinity_I_adc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSubtuneClamp(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; uint8_t x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; 
x_3 = lean_ctor_get(x_2, 3);
x_4 = l_List_lengthTR___redArg(x_3);
x_5 = lean_uint8_of_nat(x_4);
lean_dec(x_4);
x_6 = lp_sidfinity_I_cmp__imm(x_5);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_6);
lean_dec_ref(x_6);
x_8 = 24;
x_9 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneClamp___closed__0));
x_10 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_7, x_8, x_9);
x_11 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_12 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_10, x_11);
x_13 = lp_sidfinity_MV3_CodeBuilder_label(x_12, x_9);
x_14 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_15 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_13, x_14);
x_16 = lp_sidfinity_I_asl__a;
x_17 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_15, x_16);
x_18 = lp_sidfinity_I_clc;
x_19 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_17, x_18);
x_20 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__2, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__2_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__2);
x_21 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_19, x_20);
x_22 = lp_sidfinity_I_tay;
x_23 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_21, x_22);
return x_23;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSubtuneClamp___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_emitInitSubtuneClamp(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSubtuneCopy___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_sidfinity_I_ldx__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSubtuneCopy(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; uint8_t x_20; lean_object* x_21; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneCopy___closed__0, &lp_sidfinity_MV3_emitInitSubtuneCopy___closed__0_once, _init_lp_sidfinity_MV3_emitInitSubtuneCopy___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__1));
x_5 = lp_sidfinity_MV3_CodeBuilder_label(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__2));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_5, x_6);
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_7, x_8);
x_10 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__4));
x_11 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_9, x_10);
x_12 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5));
x_13 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_11, x_12);
x_14 = lp_sidfinity_I_iny;
x_15 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_13, x_14);
x_16 = lp_sidfinity_I_inx;
x_17 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_15, x_16);
x_18 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__7));
x_19 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_17, x_18);
x_20 = 27;
x_21 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_19, x_20, x_4);
return x_21;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSidSilence___closed__0(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54276;
x_2 = lp_sidfinity_I_sta__abs(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSidSilence___closed__1(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54283;
x_2 = lp_sidfinity_I_sta__abs(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSidSilence___closed__2(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54290;
x_2 = lp_sidfinity_I_sta__abs(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSidSilence___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 15;
x_2 = lp_sidfinity_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitSidSilence___closed__4(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54296;
x_2 = lp_sidfinity_I_sta__abs(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitSidSilence(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitInitSidSilence___closed__0, &lp_sidfinity_MV3_emitInitSidSilence___closed__0_once, _init_lp_sidfinity_MV3_emitInitSidSilence___closed__0);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitInitSidSilence___closed__1, &lp_sidfinity_MV3_emitInitSidSilence___closed__1_once, _init_lp_sidfinity_MV3_emitInitSidSilence___closed__1);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_4);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_8, x_6);
x_10 = lean_obj_once(&lp_sidfinity_MV3_emitInitSidSilence___closed__2, &lp_sidfinity_MV3_emitInitSidSilence___closed__2_once, _init_lp_sidfinity_MV3_emitInitSidSilence___closed__2);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
x_12 = lean_obj_once(&lp_sidfinity_MV3_emitInitSidSilence___closed__3, &lp_sidfinity_MV3_emitInitSidSilence___closed__3_once, _init_lp_sidfinity_MV3_emitInitSidSilence___closed__3);
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_12);
x_14 = lean_obj_once(&lp_sidfinity_MV3_emitInitSidSilence___closed__4, &lp_sidfinity_MV3_emitInitSidSilence___closed__4_once, _init_lp_sidfinity_MV3_emitInitSidSilence___closed__4);
x_15 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_13, x_14);
return x_15;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitVoiceState___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 2;
x_2 = lp_sidfinity_I_ldx__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitVoiceState(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; uint8_t x_20; lean_object* x_21; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitInitVoiceState___closed__0, &lp_sidfinity_MV3_emitInitVoiceState___closed__0_once, _init_lp_sidfinity_MV3_emitInitVoiceState___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__1));
x_5 = lp_sidfinity_MV3_CodeBuilder_label(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_7, x_8);
x_10 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__3));
x_11 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_9, x_10);
x_12 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__4));
x_13 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_11, x_12);
x_14 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__5));
x_15 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_13, x_14);
x_16 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__6));
x_17 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_15, x_16);
x_18 = lp_sidfinity_I_dex;
x_19 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_17, x_18);
x_20 = 29;
x_21 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_19, x_20, x_4);
return x_21;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitFrameCounter___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_sidfinity_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitInitFrameCounter___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 80;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInitFrameCounter(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitInitFrameCounter___closed__0, &lp_sidfinity_MV3_emitInitFrameCounter___closed__0_once, _init_lp_sidfinity_MV3_emitInitFrameCounter___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitInitFrameCounter___closed__1, &lp_sidfinity_MV3_emitInitFrameCounter___closed__1_once, _init_lp_sidfinity_MV3_emitInitFrameCounter___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lp_sidfinity_I_rts;
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInit(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; 
x_3 = ((lean_object*)(lp_sidfinity_MV3_emitInit___closed__0));
x_4 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_3);
x_5 = lp_sidfinity_MV3_emitInitSubtuneClamp(x_4, x_2);
x_6 = lp_sidfinity_MV3_emitInitSubtuneCopy(x_5);
x_7 = lp_sidfinity_MV3_emitInitSidSilence(x_6);
x_8 = lp_sidfinity_MV3_emitInitVoiceState(x_7);
x_9 = lp_sidfinity_MV3_emitInitFrameCounter(x_8);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitInit___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_emitInit(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitPlayHeader___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 80;
x_2 = lp_sidfinity_I_inc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlayHeader(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitPlayHeader___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitPlayHeader___closed__1, &lp_sidfinity_MV3_emitPlayHeader___closed__1_once, _init_lp_sidfinity_MV3_emitPlayHeader___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlayVoiceStep(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_4 = lean_ctor_get(x_1, 4);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 7);
lean_inc_ref(x_5);
lean_dec_ref(x_1);
x_6 = lean_ctor_get(x_3, 0);
lean_inc(x_6);
x_7 = lean_ctor_get(x_3, 1);
lean_inc(x_7);
lean_dec_ref(x_3);
x_8 = l_List_get_x3fInternal___redArg(x_4, x_6);
lean_dec(x_4);
if (lean_obj_tag(x_8) == 0)
{
lean_dec(x_7);
lean_dec_ref(x_5);
return x_2;
}
else
{
uint8_t x_9; 
x_9 = !lean_is_exclusive(x_8);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; uint8_t x_13; lean_object* x_14; lean_object* x_15; uint8_t x_16; 
x_10 = lean_ctor_get(x_8, 0);
x_11 = lean_ctor_get(x_5, 3);
lean_inc(x_11);
lean_dec_ref(x_5);
lean_inc(x_10);
x_12 = lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0(x_8, x_2, x_11);
lean_dec_ref(x_8);
x_13 = lean_uint8_of_nat(x_10);
lean_dec(x_10);
x_14 = lp_sidfinity_I_ldx__imm(x_13);
x_15 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_12, x_14);
lean_dec_ref(x_14);
x_16 = lean_unbox(x_7);
lean_dec(x_7);
if (x_16 == 0)
{
uint8_t x_17; lean_object* x_18; lean_object* x_19; 
x_17 = 33;
x_18 = ((lean_object*)(lp_sidfinity_MV3_emitPlayVoiceStep___closed__0));
x_19 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_15, x_17, x_18);
return x_19;
}
else
{
uint8_t x_20; lean_object* x_21; lean_object* x_22; 
x_20 = 32;
x_21 = ((lean_object*)(lp_sidfinity_MV3_emitPlayVoiceStep___closed__0));
x_22 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_15, x_20, x_21);
return x_22;
}
}
else
{
lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; uint8_t x_27; lean_object* x_28; lean_object* x_29; uint8_t x_30; 
x_23 = lean_ctor_get(x_8, 0);
lean_inc(x_23);
lean_dec(x_8);
x_24 = lean_ctor_get(x_5, 3);
lean_inc(x_24);
lean_dec_ref(x_5);
lean_inc(x_23);
x_25 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_25, 0, x_23);
x_26 = lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0(x_25, x_2, x_24);
lean_dec_ref(x_25);
x_27 = lean_uint8_of_nat(x_23);
lean_dec(x_23);
x_28 = lp_sidfinity_I_ldx__imm(x_27);
x_29 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_26, x_28);
lean_dec_ref(x_28);
x_30 = lean_unbox(x_7);
lean_dec(x_7);
if (x_30 == 0)
{
uint8_t x_31; lean_object* x_32; lean_object* x_33; 
x_31 = 33;
x_32 = ((lean_object*)(lp_sidfinity_MV3_emitPlayVoiceStep___closed__0));
x_33 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_29, x_31, x_32);
return x_33;
}
else
{
uint8_t x_34; lean_object* x_35; lean_object* x_36; 
x_34 = 32;
x_35 = ((lean_object*)(lp_sidfinity_MV3_emitPlayVoiceStep___closed__0));
x_36 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_29, x_34, x_35);
return x_36;
}
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_foldl___at___00MV3_emitPlayVoiceLoop_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
if (lean_obj_tag(x_3) == 0)
{
lean_dec_ref(x_1);
return x_2;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_4 = lean_ctor_get(x_3, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_3, 1);
lean_inc(x_5);
lean_dec_ref(x_3);
lean_inc_ref(x_1);
x_6 = lp_sidfinity_MV3_emitPlayVoiceStep(x_1, x_2, x_4);
x_2 = x_6;
x_3 = x_5;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_emitPlayVoiceLoop_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_4; 
x_4 = l_List_reverse___redArg(x_3);
return x_4;
}
else
{
uint8_t x_5; 
x_5 = !lean_is_exclusive(x_2);
if (x_5 == 0)
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; 
x_6 = lean_ctor_get(x_2, 0);
x_7 = lean_ctor_get(x_2, 1);
x_8 = lean_unsigned_to_nat(1u);
x_9 = lean_nat_add(x_6, x_8);
x_10 = lean_nat_dec_eq(x_9, x_1);
lean_dec(x_9);
x_11 = lean_box(x_10);
x_12 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_12, 0, x_6);
lean_ctor_set(x_12, 1, x_11);
lean_ctor_set(x_2, 1, x_3);
lean_ctor_set(x_2, 0, x_12);
{
lean_object* _tmp_1 = x_7;
lean_object* _tmp_2 = x_2;
x_2 = _tmp_1;
x_3 = _tmp_2;
}
goto _start;
}
else
{
lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; uint8_t x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_14 = lean_ctor_get(x_2, 0);
x_15 = lean_ctor_get(x_2, 1);
lean_inc(x_15);
lean_inc(x_14);
lean_dec(x_2);
x_16 = lean_unsigned_to_nat(1u);
x_17 = lean_nat_add(x_14, x_16);
x_18 = lean_nat_dec_eq(x_17, x_1);
lean_dec(x_17);
x_19 = lean_box(x_18);
x_20 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_20, 0, x_14);
lean_ctor_set(x_20, 1, x_19);
x_21 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_3);
x_2 = x_15;
x_3 = x_21;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_emitPlayVoiceLoop_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_List_mapTR_loop___at___00MV3_emitPlayVoiceLoop_spec__0(x_1, x_2, x_3);
lean_dec(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlayVoiceLoop(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_3 = lean_ctor_get(x_2, 4);
x_4 = l_List_lengthTR___redArg(x_3);
lean_inc(x_4);
x_5 = l_List_range(x_4);
x_6 = lean_box(0);
x_7 = lp_sidfinity_List_mapTR_loop___at___00MV3_emitPlayVoiceLoop_spec__0(x_4, x_5, x_6);
lean_dec(x_4);
x_8 = lp_sidfinity_List_foldl___at___00MV3_emitPlayVoiceLoop_spec__1(x_2, x_1, x_7);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitPlay(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_3 = lean_ctor_get(x_2, 7);
x_4 = lean_ctor_get(x_3, 3);
x_5 = lp_sidfinity_MV3_emitPlayHeader(x_1);
x_6 = lean_box(0);
lean_inc(x_4);
x_7 = lp_sidfinity_List_foldl___at___00MV3_emitDynamicUpdatesForPhase_spec__0(x_6, x_5, x_4);
x_8 = lp_sidfinity_MV3_emitPlayVoiceLoop(x_7, x_2);
return x_8;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__Header___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 250;
x_2 = lp_sidfinity_I_stx__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__Header___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 252;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__Header___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 253;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__Header(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__Header___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__1, &lp_sidfinity_MV3_emitNL__Header___closed__1_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__5));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__2, &lp_sidfinity_MV3_emitNL__Header___closed__2_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__2);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__6));
x_11 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_9, x_10);
x_12 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__3, &lp_sidfinity_MV3_emitNL__Header___closed__3_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__3);
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_12);
return x_13;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PtrCheck___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 252;
x_2 = lp_sidfinity_I_ora__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PtrCheck(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; uint8_t x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PtrCheck___closed__0, &lp_sidfinity_MV3_emitNL__PtrCheck___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PtrCheck___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = 27;
x_5 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PtrCheck___closed__1));
x_6 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_3, x_4, x_5);
x_7 = 32;
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PtrCheck___closed__2));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_6, x_7, x_8);
x_10 = lp_sidfinity_MV3_CodeBuilder_label(x_9, x_5);
return x_10;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__ReadPitch___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ReadPitch(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; uint8_t x_6; lean_object* x_7; lean_object* x_8; uint8_t x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__4, &lp_sidfinity_MV3_emitNoteLoadOp___closed__4_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__4);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__6));
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = 27;
x_7 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadPitch___closed__0));
x_8 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_5, x_6, x_7);
x_9 = 32;
x_10 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PtrCheck___closed__2));
x_11 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_8, x_9, x_10);
x_12 = lp_sidfinity_MV3_CodeBuilder_label(x_11, x_7);
x_13 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadPitch___closed__1, &lp_sidfinity_MV3_emitNL__ReadPitch___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadPitch___closed__1);
x_14 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_12, x_13);
return x_14;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 250;
x_2 = lp_sidfinity_I_ldx__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ReadDurInstPorta(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_2 = lp_sidfinity_I_iny;
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__6));
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__0, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__0_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__0);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_2);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_8, x_4);
x_10 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
x_12 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_2);
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_12, x_4);
x_14 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_15 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_13, x_14);
x_16 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2));
x_17 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_15, x_16);
return x_17;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_filterTR_loop___at___00MV3_emitNL__PreAdvanceOps_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; 
x_4 = lean_ctor_get(x_1, 0);
switch (lean_obj_tag(x_4)) {
case 3:
{
lean_object* x_5; 
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
lean_dec_ref(x_1);
x_1 = x_5;
goto _start;
}
case 4:
{
lean_object* x_7; 
x_7 = lean_ctor_get(x_1, 1);
lean_inc(x_7);
lean_dec_ref(x_1);
x_1 = x_7;
goto _start;
}
default: 
{
uint8_t x_9; 
lean_inc(x_4);
x_9 = !lean_is_exclusive(x_1);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; 
x_10 = lean_ctor_get(x_1, 1);
x_11 = lean_ctor_get(x_1, 0);
lean_dec(x_11);
lean_ctor_set(x_1, 1, x_2);
{
lean_object* _tmp_0 = x_10;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_13; lean_object* x_14; 
x_13 = lean_ctor_get(x_1, 1);
lean_inc(x_13);
lean_dec(x_1);
x_14 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_14, 0, x_4);
lean_ctor_set(x_14, 1, x_2);
x_1 = x_13;
x_2 = x_14;
goto _start;
}
}
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PreAdvanceOps(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_3 = lean_ctor_get(x_2, 7);
lean_inc_ref(x_3);
lean_dec_ref(x_2);
x_4 = lean_ctor_get(x_3, 1);
lean_inc(x_4);
lean_dec_ref(x_3);
x_5 = lean_box(0);
x_6 = lp_sidfinity_List_filterTR_loop___at___00MV3_emitNL__PreAdvanceOps_spec__0(x_4, x_5);
x_7 = lp_sidfinity_MV3_emitNoteLoadOps(x_1, x_6);
return x_7;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__ExtractFlags___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 32;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__ExtractFlags___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 128;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ExtractFlags(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ExtractFlags___closed__0, &lp_sidfinity_MV3_emitNL__ExtractFlags___closed__0_once, _init_lp_sidfinity_MV3_emitNL__ExtractFlags___closed__0);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_7, x_8);
x_10 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_2);
x_11 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ExtractFlags___closed__2, &lp_sidfinity_MV3_emitNL__ExtractFlags___closed__2_once, _init_lp_sidfinity_MV3_emitNL__ExtractFlags___closed__2);
x_12 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_10, x_11);
x_13 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3));
x_14 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_12, x_13);
return x_14;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PreserveMask___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 31;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PreserveMask(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; uint8_t x_4; 
x_3 = lean_ctor_get(x_2, 7);
x_4 = lean_ctor_get_uint8(x_3, sizeof(void*)*4);
if (x_4 == 0)
{
return x_1;
}
else
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_5 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_6 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_5);
x_7 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PreserveMask___closed__0, &lp_sidfinity_MV3_emitNL__PreserveMask___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PreserveMask___closed__0);
x_8 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_6, x_7);
x_9 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_10 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_8, x_9);
return x_10;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PreserveMask___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_emitNL__PreserveMask(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 252;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 4;
x_2 = lp_sidfinity_I_adc__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 253;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_sidfinity_I_adc__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__AdvancePtr(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; 
x_2 = lp_sidfinity_I_clc;
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__0, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__0_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__0);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__1, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__1_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__1);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__2, &lp_sidfinity_MV3_emitNL__Header___closed__2_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__2);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__2, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__2_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__2);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
x_12 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3);
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_12);
x_14 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__3, &lp_sidfinity_MV3_emitNL__Header___closed__3_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__3);
x_15 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_13, x_14);
x_16 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_17 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_15, x_16);
x_18 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_17, x_4);
x_19 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__5));
x_20 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_18, x_19);
x_21 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_20, x_10);
x_22 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__6));
x_23 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_21, x_22);
return x_23;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_filterTR_loop___at___00MV3_emitNL__PostAdvanceOps_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
switch (lean_obj_tag(x_4)) {
case 3:
{
goto block_9;
}
case 4:
{
goto block_9;
}
default: 
{
lean_dec(x_6);
lean_dec(x_4);
x_1 = x_5;
goto _start;
}
}
block_9:
{
lean_object* x_7; 
if (lean_is_scalar(x_6)) {
 x_7 = lean_alloc_ctor(1, 2, 0);
} else {
 x_7 = x_6;
}
lean_ctor_set(x_7, 0, x_4);
lean_ctor_set(x_7, 1, x_2);
x_1 = x_5;
x_2 = x_7;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PostAdvanceOps(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_3 = lean_ctor_get(x_2, 7);
lean_inc_ref(x_3);
lean_dec_ref(x_2);
x_4 = lean_ctor_get(x_3, 1);
lean_inc(x_4);
lean_dec_ref(x_3);
x_5 = lean_box(0);
x_6 = lp_sidfinity_List_filterTR_loop___at___00MV3_emitNL__PostAdvanceOps_spec__0(x_4, x_5);
x_7 = lp_sidfinity_MV3_emitNoteLoadOps(x_1, x_6);
return x_7;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__DurField___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__DurField___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 1;
x_2 = lp_sidfinity_I_sbc__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__DurField(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNL__DurField___closed__0, &lp_sidfinity_MV3_emitNL__DurField___closed__0_once, _init_lp_sidfinity_MV3_emitNL__DurField___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_5 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_3, x_4);
x_6 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_2);
x_7 = lp_sidfinity_I_sec;
x_8 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_6, x_7);
x_9 = lean_obj_once(&lp_sidfinity_MV3_emitNL__DurField___closed__2, &lp_sidfinity_MV3_emitNL__DurField___closed__2_once, _init_lp_sidfinity_MV3_emitNL__DurField___closed__2);
x_10 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_8, x_9);
x_11 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_12 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_10, x_11);
return x_12;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 253;
x_2 = lp_sidfinity_I_cmp__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__UpdateVInst(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; uint8_t x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint8_t x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0, &lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0_once, _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1, &lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1_once, _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = 26;
x_7 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__2));
x_8 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_5, x_6, x_7);
x_9 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3));
x_10 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_8, x_9);
x_11 = 27;
x_12 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_10, x_11, x_7);
x_13 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_14 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_12, x_13);
x_15 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3));
x_16 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_14, x_15);
x_17 = lp_sidfinity_MV3_CodeBuilder_label(x_16, x_7);
return x_17;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ResetAndSidoff(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__4));
x_5 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_5, x_6);
x_8 = lp_sidfinity_I_tay;
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__TieCheck(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; uint8_t x_6; lean_object* x_7; lean_object* x_8; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0, &lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0_once, _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1, &lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1_once, _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = 26;
x_7 = ((lean_object*)(lp_sidfinity_MV3_emitNL__TieCheck___closed__0));
x_8 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_5, x_6, x_7);
return x_8;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_sidfinity_I_ldx__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54273;
x_2 = lp_sidfinity_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54272;
x_2 = lp_sidfinity_I_sta__absY(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__FreqWrite(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__0, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__0_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__0);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_5 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_7, x_8);
x_10 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
return x_11;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PortaInit(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__0, &lp_sidfinity_MV3_emitNL__PortaInit___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__0);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
x_12 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__1, &lp_sidfinity_MV3_emitNL__PortaInit___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__1);
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_12);
x_14 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__2));
x_15 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_13, x_14);
x_16 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__3, &lp_sidfinity_MV3_emitNL__PortaInit___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__3);
x_17 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_15, x_16);
x_18 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__4));
x_19 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_17, x_18);
return x_19;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__RestoreXY(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lp_sidfinity_I_tay;
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__0, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__0_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__0);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__SavePitchFhi(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; 
x_2 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0, &lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0_once, _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_5, x_6);
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__2));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = 27;
x_11 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__3));
x_12 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_9, x_10, x_11);
x_13 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__4));
x_14 = lp_sidfinity_MV3_CodeBuilder_emitStaAbs(x_12, x_13);
x_15 = 32;
x_16 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__5));
x_17 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_14, x_15, x_16);
x_18 = lp_sidfinity_MV3_CodeBuilder_label(x_17, x_11);
x_19 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__7));
x_20 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_18, x_19);
x_21 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__8));
x_22 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_20, x_10, x_21);
x_23 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__9));
x_24 = lp_sidfinity_MV3_CodeBuilder_emitStaAbs(x_22, x_23);
x_25 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_24, x_15, x_16);
x_26 = lp_sidfinity_MV3_CodeBuilder_label(x_25, x_21);
x_27 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__10));
x_28 = lp_sidfinity_MV3_CodeBuilder_emitStaAbs(x_26, x_27);
x_29 = lp_sidfinity_MV3_CodeBuilder_label(x_28, x_16);
x_30 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__0, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__0_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__0);
x_31 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_29, x_30);
x_32 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_33 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_31, x_32);
x_34 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_33, x_2);
x_35 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_36 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_34, x_35);
return x_36;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__TieSkipLabel(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__TieCheck___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = lp_sidfinity_I_tax;
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
return x_11;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 247;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 247;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54276;
x_2 = lp_sidfinity_I_sta__absY(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__CtrlWrite(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lp_sidfinity_I_pha;
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0, &lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0_once, _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__0);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = lean_obj_once(&lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1, &lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1_once, _init_lp_sidfinity_MV3_emitNL__UpdateVInst___closed__1);
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
x_12 = 27;
x_13 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__2));
x_14 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_11, x_12, x_13);
x_15 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3);
x_16 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_14, x_15);
x_17 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_18 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_16, x_17);
x_19 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_18, x_6);
x_20 = lp_sidfinity_MV3_CodeBuilder_label(x_19, x_13);
x_21 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_20, x_15);
x_22 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_23 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_21, x_22);
return x_23;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54274;
x_2 = lp_sidfinity_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54275;
x_2 = lp_sidfinity_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54277;
x_2 = lp_sidfinity_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54278;
x_2 = lp_sidfinity_I_sta__absY(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PWADSRWrite(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__4));
x_11 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_9, x_10);
x_12 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5);
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_12);
x_14 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__6));
x_15 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_13, x_14);
x_16 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7);
x_17 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_15, x_16);
return x_17;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__PwperiodInit(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PreserveMask___closed__0, &lp_sidfinity_MV3_emitNL__PreserveMask___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PreserveMask___closed__0);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_7, x_8);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_2 = lp_sidfinity_I_pla;
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_5, x_6);
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__1));
x_9 = lp_sidfinity_MV3_CodeBuilder_label(x_7, x_8);
x_10 = lp_sidfinity_I_rts;
x_11 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_9, x_10);
return x_11;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__AdvanceOrderHeader(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; 
x_3 = lean_ctor_get(x_2, 7);
lean_inc_ref(x_3);
lean_dec_ref(x_2);
x_4 = lean_ctor_get(x_3, 2);
lean_inc(x_4);
lean_dec_ref(x_3);
x_5 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PtrCheck___closed__2));
x_6 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_5);
x_7 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_8 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_6, x_7);
x_9 = lp_sidfinity_List_foldl___at___00MV3_emitPatternEndOps_spec__0(x_8, x_4);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__LookupOL(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__3));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lp_sidfinity_I_tay;
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__2, &lp_sidfinity_MV3_emitNL__Header___closed__2_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__2);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5));
x_11 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_9, x_10);
x_12 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__3, &lp_sidfinity_MV3_emitNL__Header___closed__3_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__3);
x_13 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_11, x_12);
return x_13;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_sidfinity_I_cmp__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__ReadAndDispatch(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; uint8_t x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; lean_object* x_22; lean_object* x_23; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__6));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0, &lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0_once, _init_lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = 26;
x_7 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__1));
x_8 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_5, x_6, x_7);
x_9 = lp_sidfinity_I_tay;
x_10 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_8, x_9);
x_11 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__2));
x_12 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_10, x_11);
x_13 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__5));
x_14 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_12, x_13);
x_15 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__3));
x_16 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_14, x_15);
x_17 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__6));
x_18 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_16, x_17);
x_19 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__3));
x_20 = lp_sidfinity_MV3_CodeBuilder_emitIncAbsX(x_18, x_19);
x_21 = 32;
x_22 = ((lean_object*)(lp_sidfinity_MV3_emitNL__Header___closed__0));
x_23 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_20, x_21, x_22);
return x_23;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__OLEndOrLoop(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__1));
x_3 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_2);
x_4 = lp_sidfinity_I_iny;
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitNoteLoadOp___closed__6));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0, &lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0_once, _init_lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__0);
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
x_10 = 26;
x_11 = ((lean_object*)(lp_sidfinity_MV3_emitNL__OLEndOrLoop___closed__0));
x_12 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_9, x_10, x_11);
x_13 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__3));
x_14 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_12, x_13);
x_15 = 32;
x_16 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PtrCheck___closed__2));
x_17 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_14, x_15, x_16);
return x_17;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitNL__SongEnd___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 127;
x_2 = lp_sidfinity_I_lda__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNL__SongEnd(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__OLEndOrLoop___closed__0));
x_3 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_2);
x_4 = lean_obj_once(&lp_sidfinity_MV3_emitNL__SongEnd___closed__0, &lp_sidfinity_MV3_emitNL__SongEnd___closed__0_once, _init_lp_sidfinity_MV3_emitNL__SongEnd___closed__0);
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_5, x_6);
x_8 = lp_sidfinity_I_rts;
x_9 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_8);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitNoteLoadPath(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; 
x_3 = lp_sidfinity_MV3_emitNL__Header(x_1);
x_4 = lp_sidfinity_MV3_emitNL__PtrCheck(x_3);
x_5 = lp_sidfinity_MV3_emitNL__ReadPitch(x_4);
x_6 = lp_sidfinity_MV3_emitNL__ReadDurInstPorta(x_5);
lean_inc_ref(x_2);
x_7 = lp_sidfinity_MV3_emitNL__PreAdvanceOps(x_6, x_2);
x_8 = lp_sidfinity_MV3_emitNL__ExtractFlags(x_7);
x_9 = lp_sidfinity_MV3_emitNL__PreserveMask(x_8, x_2);
x_10 = lp_sidfinity_MV3_emitNL__AdvancePtr(x_9);
lean_inc_ref(x_2);
x_11 = lp_sidfinity_MV3_emitNL__PostAdvanceOps(x_10, x_2);
x_12 = lp_sidfinity_MV3_emitNL__DurField(x_11);
x_13 = lp_sidfinity_MV3_emitNL__UpdateVInst(x_12);
x_14 = lp_sidfinity_MV3_emitNL__ResetAndSidoff(x_13);
x_15 = lp_sidfinity_MV3_emitNL__TieCheck(x_14);
x_16 = lp_sidfinity_MV3_emitNL__FreqWrite(x_15);
x_17 = lp_sidfinity_MV3_emitNL__PortaInit(x_16);
x_18 = lp_sidfinity_MV3_emitNL__RestoreXY(x_17);
x_19 = lp_sidfinity_MV3_emitNL__SavePitchFhi(x_18);
x_20 = lp_sidfinity_MV3_emitNL__TieSkipLabel(x_19);
x_21 = lp_sidfinity_MV3_emitNL__CtrlWrite(x_20);
x_22 = lp_sidfinity_MV3_emitNL__PWADSRWrite(x_21);
x_23 = lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn(x_22);
x_24 = lp_sidfinity_MV3_emitNL__AdvanceOrderHeader(x_23, x_2);
x_25 = lp_sidfinity_MV3_emitNL__LookupOL(x_24);
x_26 = lp_sidfinity_MV3_emitNL__ReadAndDispatch(x_25);
x_27 = lp_sidfinity_MV3_emitNL__OLEndOrLoop(x_26);
x_28 = lp_sidfinity_MV3_emitNL__SongEnd(x_27);
return x_28;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_sidfinity_I_adc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__8(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 224;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__11(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 15;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__15(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 1;
x_2 = lp_sidfinity_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__16(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_sidfinity_I_sbc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__17(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_sidfinity_I_sbc__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__23(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 3;
x_2 = lp_sidfinity_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__25(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 4;
x_2 = lp_sidfinity_I_sbc__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__30(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 128;
x_2 = lp_sidfinity_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__33(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 80;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitSustainEffects___closed__34(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 1;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitSustainEffects(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; uint8_t x_9; 
x_3 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3));
x_4 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_3);
x_5 = lp_sidfinity_I_tay;
x_6 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_4, x_5);
x_7 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__1));
x_8 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_6, x_7);
x_9 = !lean_is_exclusive(x_8);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; uint8_t x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; uint8_t x_28; 
x_10 = lean_ctor_get(x_8, 0);
x_11 = lean_ctor_get(x_8, 3);
x_12 = lean_array_get_size(x_10);
x_13 = lean_unsigned_to_nat(2u);
x_14 = lean_nat_sub(x_12, x_13);
x_15 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0));
x_16 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_16, 0, x_14);
lean_ctor_set(x_16, 1, x_15);
x_17 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_11);
lean_ctor_set(x_8, 3, x_17);
x_18 = 27;
x_19 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__2));
x_20 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_8, x_18, x_19);
x_21 = 32;
x_22 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__3));
x_23 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_20, x_21, x_22);
x_24 = lp_sidfinity_MV3_CodeBuilder_label(x_23, x_19);
x_25 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__0, &lp_sidfinity_MV3_emitNL__PortaInit___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__0);
x_26 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_24, x_25);
x_27 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_26, x_7);
x_28 = !lean_is_exclusive(x_27);
if (x_28 == 0)
{
lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; uint8_t x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; uint8_t x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; uint8_t x_93; 
x_29 = lean_ctor_get(x_27, 0);
x_30 = lean_ctor_get(x_27, 3);
x_31 = lean_array_get_size(x_29);
x_32 = lean_nat_sub(x_31, x_13);
x_33 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__4));
x_34 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_34, 0, x_32);
lean_ctor_set(x_34, 1, x_33);
x_35 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_35, 0, x_34);
lean_ctor_set(x_35, 1, x_30);
lean_ctor_set(x_27, 3, x_35);
x_36 = 28;
x_37 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__5));
x_38 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_27, x_36, x_37);
x_39 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__6));
x_40 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_38, x_21, x_39);
x_41 = lp_sidfinity_MV3_CodeBuilder_label(x_40, x_37);
x_42 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_43 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_41, x_42);
x_44 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_43, x_3);
x_45 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_44, x_5);
x_46 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0));
x_47 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_45, x_46);
x_48 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__7, &lp_sidfinity_MV3_emitSustainEffects___closed__7_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__7);
x_49 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_47, x_48);
x_50 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_49, x_46);
x_51 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_52 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_50, x_51);
x_53 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_54 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_52, x_53);
x_55 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_54, x_5);
x_56 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__1, &lp_sidfinity_MV3_emitNL__PortaInit___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__1);
x_57 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_55, x_56);
x_58 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1);
x_59 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_57, x_58);
x_60 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_59, x_21, x_22);
x_61 = lp_sidfinity_MV3_CodeBuilder_label(x_60, x_39);
x_62 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1));
x_63 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_61, x_62);
x_64 = 29;
x_65 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_63, x_64, x_22);
x_66 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__3, &lp_sidfinity_MV3_emitNL__PortaInit___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__3);
x_67 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_65, x_66);
x_68 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PreserveMask___closed__0, &lp_sidfinity_MV3_emitNL__PreserveMask___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PreserveMask___closed__0);
x_69 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_67, x_68);
x_70 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_69, x_62);
x_71 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_70, x_66);
x_72 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__8, &lp_sidfinity_MV3_emitSustainEffects___closed__8_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__8);
x_73 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_71, x_72);
x_74 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_73, x_25);
x_75 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__9));
x_76 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_74, x_75);
x_77 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__10));
x_78 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_76, x_18, x_77);
x_79 = lp_sidfinity_I_clc;
x_80 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_78, x_79);
x_81 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_80, x_46);
x_82 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_81, x_48);
x_83 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_82, x_46);
x_84 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2));
x_85 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_83, x_84);
x_86 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3);
x_87 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_85, x_86);
x_88 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__11, &lp_sidfinity_MV3_emitSustainEffects___closed__11_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__11);
x_89 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_87, x_88);
x_90 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_89, x_84);
x_91 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__12));
x_92 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_90, x_91);
x_93 = !lean_is_exclusive(x_92);
if (x_93 == 0)
{
lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; uint8_t x_120; 
x_94 = lean_ctor_get(x_92, 0);
x_95 = lean_ctor_get(x_92, 3);
x_96 = lean_array_get_size(x_94);
x_97 = lean_nat_sub(x_96, x_13);
x_98 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__13));
x_99 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_99, 0, x_97);
lean_ctor_set(x_99, 1, x_98);
x_100 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_100, 0, x_99);
lean_ctor_set(x_100, 1, x_95);
lean_ctor_set(x_92, 3, x_100);
x_101 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__14));
x_102 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_92, x_18, x_101);
x_103 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__15, &lp_sidfinity_MV3_emitSustainEffects___closed__15_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__15);
x_104 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_102, x_103);
x_105 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_104, x_75);
x_106 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_105, x_21, x_101);
x_107 = lp_sidfinity_MV3_CodeBuilder_label(x_106, x_77);
x_108 = lp_sidfinity_I_sec;
x_109 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_107, x_108);
x_110 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_109, x_46);
x_111 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__16, &lp_sidfinity_MV3_emitSustainEffects___closed__16_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__16);
x_112 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_110, x_111);
x_113 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_112, x_46);
x_114 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_113, x_84);
x_115 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__17, &lp_sidfinity_MV3_emitSustainEffects___closed__17_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__17);
x_116 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_114, x_115);
x_117 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_116, x_88);
x_118 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_117, x_84);
x_119 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_118, x_91);
x_120 = !lean_is_exclusive(x_119);
if (x_120 == 0)
{
lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; lean_object* x_139; lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; lean_object* x_150; uint8_t x_151; 
x_121 = lean_ctor_get(x_119, 0);
x_122 = lean_ctor_get(x_119, 3);
x_123 = lean_array_get_size(x_121);
x_124 = lean_nat_sub(x_123, x_13);
x_125 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__18));
x_126 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_126, 0, x_124);
lean_ctor_set(x_126, 1, x_125);
x_127 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_127, 0, x_126);
lean_ctor_set(x_127, 1, x_122);
lean_ctor_set(x_119, 3, x_127);
x_128 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_119, x_18, x_101);
x_129 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_130 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_128, x_129);
x_131 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_130, x_75);
x_132 = lp_sidfinity_MV3_CodeBuilder_label(x_131, x_101);
x_133 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_132, x_46);
x_134 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_133, x_51);
x_135 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_134, x_84);
x_136 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_137 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_135, x_136);
x_138 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_137, x_53);
x_139 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_138, x_5);
x_140 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_139, x_56);
x_141 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_140, x_58);
x_142 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3);
x_143 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_141, x_142);
x_144 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3);
x_145 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_143, x_144);
x_146 = lp_sidfinity_MV3_CodeBuilder_label(x_145, x_22);
x_147 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_146, x_42);
x_148 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_147, x_3);
x_149 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_148, x_5);
x_150 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_149, x_7);
x_151 = !lean_is_exclusive(x_150);
if (x_151 == 0)
{
lean_object* x_152; lean_object* x_153; lean_object* x_154; lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; uint8_t x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; uint8_t x_186; 
x_152 = lean_ctor_get(x_150, 0);
x_153 = lean_ctor_get(x_150, 3);
x_154 = lean_array_get_size(x_152);
x_155 = lean_nat_sub(x_154, x_13);
x_156 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_157 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_157, 0, x_155);
lean_ctor_set(x_157, 1, x_156);
x_158 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_158, 0, x_157);
lean_ctor_set(x_158, 1, x_153);
lean_ctor_set(x_150, 3, x_158);
x_159 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__20));
x_160 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_150, x_18, x_159);
x_161 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__21));
x_162 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_160, x_21, x_161);
x_163 = lp_sidfinity_MV3_CodeBuilder_label(x_162, x_159);
x_164 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_165 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_163, x_164);
x_166 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__22));
x_167 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_165, x_18, x_166);
x_168 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_167, x_21, x_161);
x_169 = lp_sidfinity_MV3_CodeBuilder_label(x_168, x_166);
x_170 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_171 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_169, x_170);
x_172 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__23, &lp_sidfinity_MV3_emitSustainEffects___closed__23_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__23);
x_173 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_171, x_172);
x_174 = 25;
x_175 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__24));
x_176 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_173, x_174, x_175);
x_177 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_176, x_21, x_161);
x_178 = lp_sidfinity_MV3_CodeBuilder_label(x_177, x_175);
x_179 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_178, x_108);
x_180 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_181 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_179, x_180);
x_182 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__25, &lp_sidfinity_MV3_emitSustainEffects___closed__25_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__25);
x_183 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_181, x_182);
x_184 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__27));
x_185 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_183, x_184);
x_186 = !lean_is_exclusive(x_185);
if (x_186 == 0)
{
lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; lean_object* x_191; lean_object* x_192; lean_object* x_193; lean_object* x_194; uint8_t x_195; lean_object* x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; uint8_t x_202; 
x_187 = lean_ctor_get(x_185, 0);
x_188 = lean_ctor_get(x_185, 3);
x_189 = lean_array_get_size(x_187);
x_190 = lean_nat_sub(x_189, x_13);
x_191 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_191, 0, x_190);
lean_ctor_set(x_191, 1, x_170);
x_192 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_192, 0, x_191);
lean_ctor_set(x_192, 1, x_188);
lean_ctor_set(x_185, 3, x_192);
x_193 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_185, x_53);
x_194 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_193, x_5);
x_195 = 24;
x_196 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__28));
x_197 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_194, x_195, x_196);
x_198 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_197, x_42);
x_199 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_198, x_3);
x_200 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_199, x_5);
x_201 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_200, x_7);
x_202 = !lean_is_exclusive(x_201);
if (x_202 == 0)
{
lean_object* x_203; lean_object* x_204; lean_object* x_205; lean_object* x_206; lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; lean_object* x_214; lean_object* x_215; lean_object* x_216; lean_object* x_217; lean_object* x_218; lean_object* x_219; lean_object* x_220; lean_object* x_221; lean_object* x_222; lean_object* x_223; lean_object* x_224; lean_object* x_225; lean_object* x_226; lean_object* x_227; lean_object* x_228; lean_object* x_229; lean_object* x_230; lean_object* x_231; lean_object* x_232; lean_object* x_233; lean_object* x_234; lean_object* x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; lean_object* x_239; lean_object* x_240; lean_object* x_241; lean_object* x_242; lean_object* x_243; uint8_t x_244; 
x_203 = lean_ctor_get(x_201, 0);
x_204 = lean_ctor_get(x_201, 3);
x_205 = lean_array_get_size(x_203);
x_206 = lean_nat_sub(x_205, x_13);
x_207 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_208 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_208, 0, x_206);
lean_ctor_set(x_208, 1, x_207);
x_209 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_209, 0, x_208);
lean_ctor_set(x_209, 1, x_204);
lean_ctor_set(x_201, 3, x_209);
x_210 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_211 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_201, x_210);
x_212 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_211, x_164);
x_213 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_212, x_51);
x_214 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_213, x_164);
x_215 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_214, x_53);
x_216 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_215, x_5);
x_217 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_216, x_56);
x_218 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_219 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_217, x_218);
x_220 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_221 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_219, x_220);
x_222 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_223 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_221, x_222);
x_224 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_225 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_223, x_224);
x_226 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_227 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_225, x_21, x_226);
x_228 = lp_sidfinity_MV3_CodeBuilder_label(x_227, x_196);
x_229 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_228, x_42);
x_230 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_229, x_164);
x_231 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_230, x_53);
x_232 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_231, x_5);
x_233 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_232, x_164);
x_234 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_233, x_218);
x_235 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_236 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_234, x_235);
x_237 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_236, x_224);
x_238 = lp_sidfinity_MV3_CodeBuilder_label(x_237, x_226);
x_239 = lp_sidfinity_MV3_CodeBuilder_label(x_238, x_161);
x_240 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_239, x_42);
x_241 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_240, x_3);
x_242 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_241, x_5);
x_243 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_242, x_7);
x_244 = !lean_is_exclusive(x_243);
if (x_244 == 0)
{
lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; lean_object* x_249; lean_object* x_250; lean_object* x_251; uint8_t x_252; lean_object* x_253; lean_object* x_254; lean_object* x_255; lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; lean_object* x_265; lean_object* x_266; lean_object* x_267; lean_object* x_268; lean_object* x_269; lean_object* x_270; lean_object* x_271; lean_object* x_272; lean_object* x_273; uint8_t x_274; 
x_245 = lean_ctor_get(x_243, 0);
x_246 = lean_ctor_get(x_243, 3);
x_247 = lean_array_get_size(x_245);
x_248 = lean_nat_sub(x_247, x_13);
x_249 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_250 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_250, 0, x_248);
lean_ctor_set(x_250, 1, x_249);
x_251 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_251, 0, x_250);
lean_ctor_set(x_251, 1, x_246);
lean_ctor_set(x_243, 3, x_251);
x_252 = 26;
x_253 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_254 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_243, x_252, x_253);
x_255 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_256 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_254, x_255);
x_257 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_258 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_256, x_257);
x_259 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_258, x_252, x_253);
x_260 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_259, x_42);
x_261 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_260, x_164);
x_262 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_261, x_252, x_253);
x_263 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_262, x_51);
x_264 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_263, x_164);
x_265 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_264, x_53);
x_266 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_265, x_5);
x_267 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_266, x_56);
x_268 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_267, x_218);
x_269 = lp_sidfinity_MV3_CodeBuilder_label(x_268, x_253);
x_270 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_269, x_42);
x_271 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_270, x_3);
x_272 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_271, x_5);
x_273 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_272, x_7);
x_274 = !lean_is_exclusive(x_273);
if (x_274 == 0)
{
lean_object* x_275; lean_object* x_276; lean_object* x_277; lean_object* x_278; lean_object* x_279; lean_object* x_280; lean_object* x_281; lean_object* x_282; lean_object* x_283; lean_object* x_284; lean_object* x_285; lean_object* x_286; lean_object* x_287; lean_object* x_288; lean_object* x_289; lean_object* x_290; lean_object* x_291; lean_object* x_292; lean_object* x_293; lean_object* x_294; lean_object* x_295; lean_object* x_296; lean_object* x_297; lean_object* x_298; lean_object* x_299; lean_object* x_300; lean_object* x_301; lean_object* x_302; lean_object* x_303; lean_object* x_304; lean_object* x_305; lean_object* x_306; lean_object* x_307; lean_object* x_308; lean_object* x_309; lean_object* x_310; lean_object* x_311; lean_object* x_312; lean_object* x_313; lean_object* x_314; lean_object* x_315; lean_object* x_316; lean_object* x_317; lean_object* x_318; lean_object* x_319; lean_object* x_320; 
x_275 = lean_ctor_get(x_273, 0);
x_276 = lean_ctor_get(x_273, 3);
x_277 = lean_array_get_size(x_275);
x_278 = lean_nat_sub(x_277, x_13);
x_279 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_280 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_280, 0, x_278);
lean_ctor_set(x_280, 1, x_279);
x_281 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_281, 0, x_280);
lean_ctor_set(x_281, 1, x_276);
lean_ctor_set(x_273, 3, x_281);
x_282 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_283 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_273, x_18, x_282);
x_284 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_285 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_283, x_21, x_284);
x_286 = lp_sidfinity_MV3_CodeBuilder_label(x_285, x_282);
x_287 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_286, x_51);
x_288 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_287, x_255);
x_289 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_288, x_257);
x_290 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_291 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_289, x_252, x_290);
x_292 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_291, x_79);
x_293 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_294 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_292, x_293);
x_295 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_296 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_294, x_295);
x_297 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_298 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_296, x_21, x_297);
x_299 = lp_sidfinity_MV3_CodeBuilder_label(x_298, x_290);
x_300 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_299, x_293);
x_301 = lp_sidfinity_MV3_CodeBuilder_label(x_300, x_297);
x_302 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_301, x_5);
x_303 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_304 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_302, x_303);
x_305 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_304, x_25);
x_306 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_307 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_305, x_306);
x_308 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_307, x_51);
x_309 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_308, x_42);
x_310 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_309, x_53);
x_311 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_310, x_5);
x_312 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_311, x_66);
x_313 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_312, x_218);
x_314 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_313, x_56);
x_315 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_316 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_314, x_315);
x_317 = lp_sidfinity_MV3_CodeBuilder_label(x_316, x_284);
x_318 = lp_sidfinity_I_rts;
x_319 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_317, x_318);
x_320 = lp_sidfinity_MV3_emitNoteLoadPath(x_319, x_2);
return x_320;
}
else
{
lean_object* x_321; uint16_t x_322; lean_object* x_323; lean_object* x_324; lean_object* x_325; lean_object* x_326; lean_object* x_327; lean_object* x_328; lean_object* x_329; lean_object* x_330; lean_object* x_331; lean_object* x_332; lean_object* x_333; lean_object* x_334; lean_object* x_335; lean_object* x_336; lean_object* x_337; lean_object* x_338; lean_object* x_339; lean_object* x_340; lean_object* x_341; lean_object* x_342; lean_object* x_343; lean_object* x_344; lean_object* x_345; lean_object* x_346; lean_object* x_347; lean_object* x_348; lean_object* x_349; lean_object* x_350; lean_object* x_351; lean_object* x_352; lean_object* x_353; lean_object* x_354; lean_object* x_355; lean_object* x_356; lean_object* x_357; lean_object* x_358; lean_object* x_359; lean_object* x_360; lean_object* x_361; lean_object* x_362; lean_object* x_363; lean_object* x_364; lean_object* x_365; lean_object* x_366; lean_object* x_367; lean_object* x_368; lean_object* x_369; lean_object* x_370; 
x_321 = lean_ctor_get(x_273, 0);
x_322 = lean_ctor_get_uint16(x_273, sizeof(void*)*4);
x_323 = lean_ctor_get(x_273, 1);
x_324 = lean_ctor_get(x_273, 2);
x_325 = lean_ctor_get(x_273, 3);
lean_inc(x_325);
lean_inc(x_324);
lean_inc(x_323);
lean_inc(x_321);
lean_dec(x_273);
x_326 = lean_array_get_size(x_321);
x_327 = lean_nat_sub(x_326, x_13);
x_328 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_329 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_329, 0, x_327);
lean_ctor_set(x_329, 1, x_328);
x_330 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_330, 0, x_329);
lean_ctor_set(x_330, 1, x_325);
x_331 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_331, 0, x_321);
lean_ctor_set(x_331, 1, x_323);
lean_ctor_set(x_331, 2, x_324);
lean_ctor_set(x_331, 3, x_330);
lean_ctor_set_uint16(x_331, sizeof(void*)*4, x_322);
x_332 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_333 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_331, x_18, x_332);
x_334 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_335 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_333, x_21, x_334);
x_336 = lp_sidfinity_MV3_CodeBuilder_label(x_335, x_332);
x_337 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_336, x_51);
x_338 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_337, x_255);
x_339 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_338, x_257);
x_340 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_341 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_339, x_252, x_340);
x_342 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_341, x_79);
x_343 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_344 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_342, x_343);
x_345 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_346 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_344, x_345);
x_347 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_348 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_346, x_21, x_347);
x_349 = lp_sidfinity_MV3_CodeBuilder_label(x_348, x_340);
x_350 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_349, x_343);
x_351 = lp_sidfinity_MV3_CodeBuilder_label(x_350, x_347);
x_352 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_351, x_5);
x_353 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_354 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_352, x_353);
x_355 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_354, x_25);
x_356 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_357 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_355, x_356);
x_358 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_357, x_51);
x_359 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_358, x_42);
x_360 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_359, x_53);
x_361 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_360, x_5);
x_362 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_361, x_66);
x_363 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_362, x_218);
x_364 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_363, x_56);
x_365 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_366 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_364, x_365);
x_367 = lp_sidfinity_MV3_CodeBuilder_label(x_366, x_334);
x_368 = lp_sidfinity_I_rts;
x_369 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_367, x_368);
x_370 = lp_sidfinity_MV3_emitNoteLoadPath(x_369, x_2);
return x_370;
}
}
else
{
lean_object* x_371; uint16_t x_372; lean_object* x_373; lean_object* x_374; lean_object* x_375; lean_object* x_376; lean_object* x_377; lean_object* x_378; lean_object* x_379; lean_object* x_380; lean_object* x_381; uint8_t x_382; lean_object* x_383; lean_object* x_384; lean_object* x_385; lean_object* x_386; lean_object* x_387; lean_object* x_388; lean_object* x_389; lean_object* x_390; lean_object* x_391; lean_object* x_392; lean_object* x_393; lean_object* x_394; lean_object* x_395; lean_object* x_396; lean_object* x_397; lean_object* x_398; lean_object* x_399; lean_object* x_400; lean_object* x_401; lean_object* x_402; lean_object* x_403; lean_object* x_404; uint16_t x_405; lean_object* x_406; lean_object* x_407; lean_object* x_408; lean_object* x_409; lean_object* x_410; lean_object* x_411; lean_object* x_412; lean_object* x_413; lean_object* x_414; lean_object* x_415; lean_object* x_416; lean_object* x_417; lean_object* x_418; lean_object* x_419; lean_object* x_420; lean_object* x_421; lean_object* x_422; lean_object* x_423; lean_object* x_424; lean_object* x_425; lean_object* x_426; lean_object* x_427; lean_object* x_428; lean_object* x_429; lean_object* x_430; lean_object* x_431; lean_object* x_432; lean_object* x_433; lean_object* x_434; lean_object* x_435; lean_object* x_436; lean_object* x_437; lean_object* x_438; lean_object* x_439; lean_object* x_440; lean_object* x_441; lean_object* x_442; lean_object* x_443; lean_object* x_444; lean_object* x_445; lean_object* x_446; lean_object* x_447; lean_object* x_448; lean_object* x_449; lean_object* x_450; lean_object* x_451; lean_object* x_452; lean_object* x_453; lean_object* x_454; 
x_371 = lean_ctor_get(x_243, 0);
x_372 = lean_ctor_get_uint16(x_243, sizeof(void*)*4);
x_373 = lean_ctor_get(x_243, 1);
x_374 = lean_ctor_get(x_243, 2);
x_375 = lean_ctor_get(x_243, 3);
lean_inc(x_375);
lean_inc(x_374);
lean_inc(x_373);
lean_inc(x_371);
lean_dec(x_243);
x_376 = lean_array_get_size(x_371);
x_377 = lean_nat_sub(x_376, x_13);
x_378 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_379 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_379, 0, x_377);
lean_ctor_set(x_379, 1, x_378);
x_380 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_380, 0, x_379);
lean_ctor_set(x_380, 1, x_375);
x_381 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_381, 0, x_371);
lean_ctor_set(x_381, 1, x_373);
lean_ctor_set(x_381, 2, x_374);
lean_ctor_set(x_381, 3, x_380);
lean_ctor_set_uint16(x_381, sizeof(void*)*4, x_372);
x_382 = 26;
x_383 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_384 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_381, x_382, x_383);
x_385 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_386 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_384, x_385);
x_387 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_388 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_386, x_387);
x_389 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_388, x_382, x_383);
x_390 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_389, x_42);
x_391 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_390, x_164);
x_392 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_391, x_382, x_383);
x_393 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_392, x_51);
x_394 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_393, x_164);
x_395 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_394, x_53);
x_396 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_395, x_5);
x_397 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_396, x_56);
x_398 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_397, x_218);
x_399 = lp_sidfinity_MV3_CodeBuilder_label(x_398, x_383);
x_400 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_399, x_42);
x_401 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_400, x_3);
x_402 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_401, x_5);
x_403 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_402, x_7);
x_404 = lean_ctor_get(x_403, 0);
lean_inc_ref(x_404);
x_405 = lean_ctor_get_uint16(x_403, sizeof(void*)*4);
x_406 = lean_ctor_get(x_403, 1);
lean_inc(x_406);
x_407 = lean_ctor_get(x_403, 2);
lean_inc(x_407);
x_408 = lean_ctor_get(x_403, 3);
lean_inc(x_408);
if (lean_is_exclusive(x_403)) {
 lean_ctor_release(x_403, 0);
 lean_ctor_release(x_403, 1);
 lean_ctor_release(x_403, 2);
 lean_ctor_release(x_403, 3);
 x_409 = x_403;
} else {
 lean_dec_ref(x_403);
 x_409 = lean_box(0);
}
x_410 = lean_array_get_size(x_404);
x_411 = lean_nat_sub(x_410, x_13);
x_412 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_413 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_413, 0, x_411);
lean_ctor_set(x_413, 1, x_412);
x_414 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_414, 0, x_413);
lean_ctor_set(x_414, 1, x_408);
if (lean_is_scalar(x_409)) {
 x_415 = lean_alloc_ctor(0, 4, 2);
} else {
 x_415 = x_409;
}
lean_ctor_set(x_415, 0, x_404);
lean_ctor_set(x_415, 1, x_406);
lean_ctor_set(x_415, 2, x_407);
lean_ctor_set(x_415, 3, x_414);
lean_ctor_set_uint16(x_415, sizeof(void*)*4, x_405);
x_416 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_417 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_415, x_18, x_416);
x_418 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_419 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_417, x_21, x_418);
x_420 = lp_sidfinity_MV3_CodeBuilder_label(x_419, x_416);
x_421 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_420, x_51);
x_422 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_421, x_385);
x_423 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_422, x_387);
x_424 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_425 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_423, x_382, x_424);
x_426 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_425, x_79);
x_427 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_428 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_426, x_427);
x_429 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_430 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_428, x_429);
x_431 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_432 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_430, x_21, x_431);
x_433 = lp_sidfinity_MV3_CodeBuilder_label(x_432, x_424);
x_434 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_433, x_427);
x_435 = lp_sidfinity_MV3_CodeBuilder_label(x_434, x_431);
x_436 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_435, x_5);
x_437 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_438 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_436, x_437);
x_439 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_438, x_25);
x_440 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_441 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_439, x_440);
x_442 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_441, x_51);
x_443 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_442, x_42);
x_444 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_443, x_53);
x_445 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_444, x_5);
x_446 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_445, x_66);
x_447 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_446, x_218);
x_448 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_447, x_56);
x_449 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_450 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_448, x_449);
x_451 = lp_sidfinity_MV3_CodeBuilder_label(x_450, x_418);
x_452 = lp_sidfinity_I_rts;
x_453 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_451, x_452);
x_454 = lp_sidfinity_MV3_emitNoteLoadPath(x_453, x_2);
return x_454;
}
}
else
{
lean_object* x_455; uint16_t x_456; lean_object* x_457; lean_object* x_458; lean_object* x_459; lean_object* x_460; lean_object* x_461; lean_object* x_462; lean_object* x_463; lean_object* x_464; lean_object* x_465; lean_object* x_466; lean_object* x_467; lean_object* x_468; lean_object* x_469; lean_object* x_470; lean_object* x_471; lean_object* x_472; lean_object* x_473; lean_object* x_474; lean_object* x_475; lean_object* x_476; lean_object* x_477; lean_object* x_478; lean_object* x_479; lean_object* x_480; lean_object* x_481; lean_object* x_482; lean_object* x_483; lean_object* x_484; lean_object* x_485; lean_object* x_486; lean_object* x_487; lean_object* x_488; lean_object* x_489; lean_object* x_490; lean_object* x_491; lean_object* x_492; lean_object* x_493; lean_object* x_494; lean_object* x_495; lean_object* x_496; lean_object* x_497; lean_object* x_498; lean_object* x_499; lean_object* x_500; uint16_t x_501; lean_object* x_502; lean_object* x_503; lean_object* x_504; lean_object* x_505; lean_object* x_506; lean_object* x_507; lean_object* x_508; lean_object* x_509; lean_object* x_510; lean_object* x_511; uint8_t x_512; lean_object* x_513; lean_object* x_514; lean_object* x_515; lean_object* x_516; lean_object* x_517; lean_object* x_518; lean_object* x_519; lean_object* x_520; lean_object* x_521; lean_object* x_522; lean_object* x_523; lean_object* x_524; lean_object* x_525; lean_object* x_526; lean_object* x_527; lean_object* x_528; lean_object* x_529; lean_object* x_530; lean_object* x_531; lean_object* x_532; lean_object* x_533; lean_object* x_534; uint16_t x_535; lean_object* x_536; lean_object* x_537; lean_object* x_538; lean_object* x_539; lean_object* x_540; lean_object* x_541; lean_object* x_542; lean_object* x_543; lean_object* x_544; lean_object* x_545; lean_object* x_546; lean_object* x_547; lean_object* x_548; lean_object* x_549; lean_object* x_550; lean_object* x_551; lean_object* x_552; lean_object* x_553; lean_object* x_554; lean_object* x_555; lean_object* x_556; lean_object* x_557; lean_object* x_558; lean_object* x_559; lean_object* x_560; lean_object* x_561; lean_object* x_562; lean_object* x_563; lean_object* x_564; lean_object* x_565; lean_object* x_566; lean_object* x_567; lean_object* x_568; lean_object* x_569; lean_object* x_570; lean_object* x_571; lean_object* x_572; lean_object* x_573; lean_object* x_574; lean_object* x_575; lean_object* x_576; lean_object* x_577; lean_object* x_578; lean_object* x_579; lean_object* x_580; lean_object* x_581; lean_object* x_582; lean_object* x_583; lean_object* x_584; 
x_455 = lean_ctor_get(x_201, 0);
x_456 = lean_ctor_get_uint16(x_201, sizeof(void*)*4);
x_457 = lean_ctor_get(x_201, 1);
x_458 = lean_ctor_get(x_201, 2);
x_459 = lean_ctor_get(x_201, 3);
lean_inc(x_459);
lean_inc(x_458);
lean_inc(x_457);
lean_inc(x_455);
lean_dec(x_201);
x_460 = lean_array_get_size(x_455);
x_461 = lean_nat_sub(x_460, x_13);
x_462 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_463 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_463, 0, x_461);
lean_ctor_set(x_463, 1, x_462);
x_464 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_464, 0, x_463);
lean_ctor_set(x_464, 1, x_459);
x_465 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_465, 0, x_455);
lean_ctor_set(x_465, 1, x_457);
lean_ctor_set(x_465, 2, x_458);
lean_ctor_set(x_465, 3, x_464);
lean_ctor_set_uint16(x_465, sizeof(void*)*4, x_456);
x_466 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_467 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_465, x_466);
x_468 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_467, x_164);
x_469 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_468, x_51);
x_470 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_469, x_164);
x_471 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_470, x_53);
x_472 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_471, x_5);
x_473 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_472, x_56);
x_474 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_475 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_473, x_474);
x_476 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_477 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_475, x_476);
x_478 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_479 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_477, x_478);
x_480 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_481 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_479, x_480);
x_482 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_483 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_481, x_21, x_482);
x_484 = lp_sidfinity_MV3_CodeBuilder_label(x_483, x_196);
x_485 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_484, x_42);
x_486 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_485, x_164);
x_487 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_486, x_53);
x_488 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_487, x_5);
x_489 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_488, x_164);
x_490 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_489, x_474);
x_491 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_492 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_490, x_491);
x_493 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_492, x_480);
x_494 = lp_sidfinity_MV3_CodeBuilder_label(x_493, x_482);
x_495 = lp_sidfinity_MV3_CodeBuilder_label(x_494, x_161);
x_496 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_495, x_42);
x_497 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_496, x_3);
x_498 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_497, x_5);
x_499 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_498, x_7);
x_500 = lean_ctor_get(x_499, 0);
lean_inc_ref(x_500);
x_501 = lean_ctor_get_uint16(x_499, sizeof(void*)*4);
x_502 = lean_ctor_get(x_499, 1);
lean_inc(x_502);
x_503 = lean_ctor_get(x_499, 2);
lean_inc(x_503);
x_504 = lean_ctor_get(x_499, 3);
lean_inc(x_504);
if (lean_is_exclusive(x_499)) {
 lean_ctor_release(x_499, 0);
 lean_ctor_release(x_499, 1);
 lean_ctor_release(x_499, 2);
 lean_ctor_release(x_499, 3);
 x_505 = x_499;
} else {
 lean_dec_ref(x_499);
 x_505 = lean_box(0);
}
x_506 = lean_array_get_size(x_500);
x_507 = lean_nat_sub(x_506, x_13);
x_508 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_509 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_509, 0, x_507);
lean_ctor_set(x_509, 1, x_508);
x_510 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_510, 0, x_509);
lean_ctor_set(x_510, 1, x_504);
if (lean_is_scalar(x_505)) {
 x_511 = lean_alloc_ctor(0, 4, 2);
} else {
 x_511 = x_505;
}
lean_ctor_set(x_511, 0, x_500);
lean_ctor_set(x_511, 1, x_502);
lean_ctor_set(x_511, 2, x_503);
lean_ctor_set(x_511, 3, x_510);
lean_ctor_set_uint16(x_511, sizeof(void*)*4, x_501);
x_512 = 26;
x_513 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_514 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_511, x_512, x_513);
x_515 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_516 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_514, x_515);
x_517 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_518 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_516, x_517);
x_519 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_518, x_512, x_513);
x_520 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_519, x_42);
x_521 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_520, x_164);
x_522 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_521, x_512, x_513);
x_523 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_522, x_51);
x_524 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_523, x_164);
x_525 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_524, x_53);
x_526 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_525, x_5);
x_527 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_526, x_56);
x_528 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_527, x_474);
x_529 = lp_sidfinity_MV3_CodeBuilder_label(x_528, x_513);
x_530 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_529, x_42);
x_531 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_530, x_3);
x_532 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_531, x_5);
x_533 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_532, x_7);
x_534 = lean_ctor_get(x_533, 0);
lean_inc_ref(x_534);
x_535 = lean_ctor_get_uint16(x_533, sizeof(void*)*4);
x_536 = lean_ctor_get(x_533, 1);
lean_inc(x_536);
x_537 = lean_ctor_get(x_533, 2);
lean_inc(x_537);
x_538 = lean_ctor_get(x_533, 3);
lean_inc(x_538);
if (lean_is_exclusive(x_533)) {
 lean_ctor_release(x_533, 0);
 lean_ctor_release(x_533, 1);
 lean_ctor_release(x_533, 2);
 lean_ctor_release(x_533, 3);
 x_539 = x_533;
} else {
 lean_dec_ref(x_533);
 x_539 = lean_box(0);
}
x_540 = lean_array_get_size(x_534);
x_541 = lean_nat_sub(x_540, x_13);
x_542 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_543 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_543, 0, x_541);
lean_ctor_set(x_543, 1, x_542);
x_544 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_544, 0, x_543);
lean_ctor_set(x_544, 1, x_538);
if (lean_is_scalar(x_539)) {
 x_545 = lean_alloc_ctor(0, 4, 2);
} else {
 x_545 = x_539;
}
lean_ctor_set(x_545, 0, x_534);
lean_ctor_set(x_545, 1, x_536);
lean_ctor_set(x_545, 2, x_537);
lean_ctor_set(x_545, 3, x_544);
lean_ctor_set_uint16(x_545, sizeof(void*)*4, x_535);
x_546 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_547 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_545, x_18, x_546);
x_548 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_549 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_547, x_21, x_548);
x_550 = lp_sidfinity_MV3_CodeBuilder_label(x_549, x_546);
x_551 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_550, x_51);
x_552 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_551, x_515);
x_553 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_552, x_517);
x_554 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_555 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_553, x_512, x_554);
x_556 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_555, x_79);
x_557 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_558 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_556, x_557);
x_559 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_560 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_558, x_559);
x_561 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_562 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_560, x_21, x_561);
x_563 = lp_sidfinity_MV3_CodeBuilder_label(x_562, x_554);
x_564 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_563, x_557);
x_565 = lp_sidfinity_MV3_CodeBuilder_label(x_564, x_561);
x_566 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_565, x_5);
x_567 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_568 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_566, x_567);
x_569 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_568, x_25);
x_570 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_571 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_569, x_570);
x_572 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_571, x_51);
x_573 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_572, x_42);
x_574 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_573, x_53);
x_575 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_574, x_5);
x_576 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_575, x_66);
x_577 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_576, x_474);
x_578 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_577, x_56);
x_579 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_580 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_578, x_579);
x_581 = lp_sidfinity_MV3_CodeBuilder_label(x_580, x_548);
x_582 = lp_sidfinity_I_rts;
x_583 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_581, x_582);
x_584 = lp_sidfinity_MV3_emitNoteLoadPath(x_583, x_2);
return x_584;
}
}
else
{
lean_object* x_585; uint16_t x_586; lean_object* x_587; lean_object* x_588; lean_object* x_589; lean_object* x_590; lean_object* x_591; lean_object* x_592; lean_object* x_593; lean_object* x_594; lean_object* x_595; lean_object* x_596; uint8_t x_597; lean_object* x_598; lean_object* x_599; lean_object* x_600; lean_object* x_601; lean_object* x_602; lean_object* x_603; lean_object* x_604; uint16_t x_605; lean_object* x_606; lean_object* x_607; lean_object* x_608; lean_object* x_609; lean_object* x_610; lean_object* x_611; lean_object* x_612; lean_object* x_613; lean_object* x_614; lean_object* x_615; lean_object* x_616; lean_object* x_617; lean_object* x_618; lean_object* x_619; lean_object* x_620; lean_object* x_621; lean_object* x_622; lean_object* x_623; lean_object* x_624; lean_object* x_625; lean_object* x_626; lean_object* x_627; lean_object* x_628; lean_object* x_629; lean_object* x_630; lean_object* x_631; lean_object* x_632; lean_object* x_633; lean_object* x_634; lean_object* x_635; lean_object* x_636; lean_object* x_637; lean_object* x_638; lean_object* x_639; lean_object* x_640; lean_object* x_641; lean_object* x_642; lean_object* x_643; lean_object* x_644; lean_object* x_645; lean_object* x_646; lean_object* x_647; lean_object* x_648; lean_object* x_649; lean_object* x_650; uint16_t x_651; lean_object* x_652; lean_object* x_653; lean_object* x_654; lean_object* x_655; lean_object* x_656; lean_object* x_657; lean_object* x_658; lean_object* x_659; lean_object* x_660; lean_object* x_661; uint8_t x_662; lean_object* x_663; lean_object* x_664; lean_object* x_665; lean_object* x_666; lean_object* x_667; lean_object* x_668; lean_object* x_669; lean_object* x_670; lean_object* x_671; lean_object* x_672; lean_object* x_673; lean_object* x_674; lean_object* x_675; lean_object* x_676; lean_object* x_677; lean_object* x_678; lean_object* x_679; lean_object* x_680; lean_object* x_681; lean_object* x_682; lean_object* x_683; lean_object* x_684; uint16_t x_685; lean_object* x_686; lean_object* x_687; lean_object* x_688; lean_object* x_689; lean_object* x_690; lean_object* x_691; lean_object* x_692; lean_object* x_693; lean_object* x_694; lean_object* x_695; lean_object* x_696; lean_object* x_697; lean_object* x_698; lean_object* x_699; lean_object* x_700; lean_object* x_701; lean_object* x_702; lean_object* x_703; lean_object* x_704; lean_object* x_705; lean_object* x_706; lean_object* x_707; lean_object* x_708; lean_object* x_709; lean_object* x_710; lean_object* x_711; lean_object* x_712; lean_object* x_713; lean_object* x_714; lean_object* x_715; lean_object* x_716; lean_object* x_717; lean_object* x_718; lean_object* x_719; lean_object* x_720; lean_object* x_721; lean_object* x_722; lean_object* x_723; lean_object* x_724; lean_object* x_725; lean_object* x_726; lean_object* x_727; lean_object* x_728; lean_object* x_729; lean_object* x_730; lean_object* x_731; lean_object* x_732; lean_object* x_733; lean_object* x_734; 
x_585 = lean_ctor_get(x_185, 0);
x_586 = lean_ctor_get_uint16(x_185, sizeof(void*)*4);
x_587 = lean_ctor_get(x_185, 1);
x_588 = lean_ctor_get(x_185, 2);
x_589 = lean_ctor_get(x_185, 3);
lean_inc(x_589);
lean_inc(x_588);
lean_inc(x_587);
lean_inc(x_585);
lean_dec(x_185);
x_590 = lean_array_get_size(x_585);
x_591 = lean_nat_sub(x_590, x_13);
x_592 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_592, 0, x_591);
lean_ctor_set(x_592, 1, x_170);
x_593 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_593, 0, x_592);
lean_ctor_set(x_593, 1, x_589);
x_594 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_594, 0, x_585);
lean_ctor_set(x_594, 1, x_587);
lean_ctor_set(x_594, 2, x_588);
lean_ctor_set(x_594, 3, x_593);
lean_ctor_set_uint16(x_594, sizeof(void*)*4, x_586);
x_595 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_594, x_53);
x_596 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_595, x_5);
x_597 = 24;
x_598 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__28));
x_599 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_596, x_597, x_598);
x_600 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_599, x_42);
x_601 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_600, x_3);
x_602 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_601, x_5);
x_603 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_602, x_7);
x_604 = lean_ctor_get(x_603, 0);
lean_inc_ref(x_604);
x_605 = lean_ctor_get_uint16(x_603, sizeof(void*)*4);
x_606 = lean_ctor_get(x_603, 1);
lean_inc(x_606);
x_607 = lean_ctor_get(x_603, 2);
lean_inc(x_607);
x_608 = lean_ctor_get(x_603, 3);
lean_inc(x_608);
if (lean_is_exclusive(x_603)) {
 lean_ctor_release(x_603, 0);
 lean_ctor_release(x_603, 1);
 lean_ctor_release(x_603, 2);
 lean_ctor_release(x_603, 3);
 x_609 = x_603;
} else {
 lean_dec_ref(x_603);
 x_609 = lean_box(0);
}
x_610 = lean_array_get_size(x_604);
x_611 = lean_nat_sub(x_610, x_13);
x_612 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_613 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_613, 0, x_611);
lean_ctor_set(x_613, 1, x_612);
x_614 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_614, 0, x_613);
lean_ctor_set(x_614, 1, x_608);
if (lean_is_scalar(x_609)) {
 x_615 = lean_alloc_ctor(0, 4, 2);
} else {
 x_615 = x_609;
}
lean_ctor_set(x_615, 0, x_604);
lean_ctor_set(x_615, 1, x_606);
lean_ctor_set(x_615, 2, x_607);
lean_ctor_set(x_615, 3, x_614);
lean_ctor_set_uint16(x_615, sizeof(void*)*4, x_605);
x_616 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_617 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_615, x_616);
x_618 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_617, x_164);
x_619 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_618, x_51);
x_620 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_619, x_164);
x_621 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_620, x_53);
x_622 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_621, x_5);
x_623 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_622, x_56);
x_624 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_625 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_623, x_624);
x_626 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_627 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_625, x_626);
x_628 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_629 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_627, x_628);
x_630 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_631 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_629, x_630);
x_632 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_633 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_631, x_21, x_632);
x_634 = lp_sidfinity_MV3_CodeBuilder_label(x_633, x_598);
x_635 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_634, x_42);
x_636 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_635, x_164);
x_637 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_636, x_53);
x_638 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_637, x_5);
x_639 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_638, x_164);
x_640 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_639, x_624);
x_641 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_642 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_640, x_641);
x_643 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_642, x_630);
x_644 = lp_sidfinity_MV3_CodeBuilder_label(x_643, x_632);
x_645 = lp_sidfinity_MV3_CodeBuilder_label(x_644, x_161);
x_646 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_645, x_42);
x_647 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_646, x_3);
x_648 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_647, x_5);
x_649 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_648, x_7);
x_650 = lean_ctor_get(x_649, 0);
lean_inc_ref(x_650);
x_651 = lean_ctor_get_uint16(x_649, sizeof(void*)*4);
x_652 = lean_ctor_get(x_649, 1);
lean_inc(x_652);
x_653 = lean_ctor_get(x_649, 2);
lean_inc(x_653);
x_654 = lean_ctor_get(x_649, 3);
lean_inc(x_654);
if (lean_is_exclusive(x_649)) {
 lean_ctor_release(x_649, 0);
 lean_ctor_release(x_649, 1);
 lean_ctor_release(x_649, 2);
 lean_ctor_release(x_649, 3);
 x_655 = x_649;
} else {
 lean_dec_ref(x_649);
 x_655 = lean_box(0);
}
x_656 = lean_array_get_size(x_650);
x_657 = lean_nat_sub(x_656, x_13);
x_658 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_659 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_659, 0, x_657);
lean_ctor_set(x_659, 1, x_658);
x_660 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_660, 0, x_659);
lean_ctor_set(x_660, 1, x_654);
if (lean_is_scalar(x_655)) {
 x_661 = lean_alloc_ctor(0, 4, 2);
} else {
 x_661 = x_655;
}
lean_ctor_set(x_661, 0, x_650);
lean_ctor_set(x_661, 1, x_652);
lean_ctor_set(x_661, 2, x_653);
lean_ctor_set(x_661, 3, x_660);
lean_ctor_set_uint16(x_661, sizeof(void*)*4, x_651);
x_662 = 26;
x_663 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_664 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_661, x_662, x_663);
x_665 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_666 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_664, x_665);
x_667 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_668 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_666, x_667);
x_669 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_668, x_662, x_663);
x_670 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_669, x_42);
x_671 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_670, x_164);
x_672 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_671, x_662, x_663);
x_673 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_672, x_51);
x_674 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_673, x_164);
x_675 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_674, x_53);
x_676 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_675, x_5);
x_677 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_676, x_56);
x_678 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_677, x_624);
x_679 = lp_sidfinity_MV3_CodeBuilder_label(x_678, x_663);
x_680 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_679, x_42);
x_681 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_680, x_3);
x_682 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_681, x_5);
x_683 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_682, x_7);
x_684 = lean_ctor_get(x_683, 0);
lean_inc_ref(x_684);
x_685 = lean_ctor_get_uint16(x_683, sizeof(void*)*4);
x_686 = lean_ctor_get(x_683, 1);
lean_inc(x_686);
x_687 = lean_ctor_get(x_683, 2);
lean_inc(x_687);
x_688 = lean_ctor_get(x_683, 3);
lean_inc(x_688);
if (lean_is_exclusive(x_683)) {
 lean_ctor_release(x_683, 0);
 lean_ctor_release(x_683, 1);
 lean_ctor_release(x_683, 2);
 lean_ctor_release(x_683, 3);
 x_689 = x_683;
} else {
 lean_dec_ref(x_683);
 x_689 = lean_box(0);
}
x_690 = lean_array_get_size(x_684);
x_691 = lean_nat_sub(x_690, x_13);
x_692 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_693 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_693, 0, x_691);
lean_ctor_set(x_693, 1, x_692);
x_694 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_694, 0, x_693);
lean_ctor_set(x_694, 1, x_688);
if (lean_is_scalar(x_689)) {
 x_695 = lean_alloc_ctor(0, 4, 2);
} else {
 x_695 = x_689;
}
lean_ctor_set(x_695, 0, x_684);
lean_ctor_set(x_695, 1, x_686);
lean_ctor_set(x_695, 2, x_687);
lean_ctor_set(x_695, 3, x_694);
lean_ctor_set_uint16(x_695, sizeof(void*)*4, x_685);
x_696 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_697 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_695, x_18, x_696);
x_698 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_699 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_697, x_21, x_698);
x_700 = lp_sidfinity_MV3_CodeBuilder_label(x_699, x_696);
x_701 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_700, x_51);
x_702 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_701, x_665);
x_703 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_702, x_667);
x_704 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_705 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_703, x_662, x_704);
x_706 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_705, x_79);
x_707 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_708 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_706, x_707);
x_709 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_710 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_708, x_709);
x_711 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_712 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_710, x_21, x_711);
x_713 = lp_sidfinity_MV3_CodeBuilder_label(x_712, x_704);
x_714 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_713, x_707);
x_715 = lp_sidfinity_MV3_CodeBuilder_label(x_714, x_711);
x_716 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_715, x_5);
x_717 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_718 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_716, x_717);
x_719 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_718, x_25);
x_720 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_721 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_719, x_720);
x_722 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_721, x_51);
x_723 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_722, x_42);
x_724 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_723, x_53);
x_725 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_724, x_5);
x_726 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_725, x_66);
x_727 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_726, x_624);
x_728 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_727, x_56);
x_729 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_730 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_728, x_729);
x_731 = lp_sidfinity_MV3_CodeBuilder_label(x_730, x_698);
x_732 = lp_sidfinity_I_rts;
x_733 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_731, x_732);
x_734 = lp_sidfinity_MV3_emitNoteLoadPath(x_733, x_2);
return x_734;
}
}
else
{
lean_object* x_735; uint16_t x_736; lean_object* x_737; lean_object* x_738; lean_object* x_739; lean_object* x_740; lean_object* x_741; lean_object* x_742; lean_object* x_743; lean_object* x_744; lean_object* x_745; lean_object* x_746; lean_object* x_747; lean_object* x_748; lean_object* x_749; lean_object* x_750; lean_object* x_751; lean_object* x_752; lean_object* x_753; lean_object* x_754; lean_object* x_755; lean_object* x_756; lean_object* x_757; lean_object* x_758; lean_object* x_759; lean_object* x_760; uint8_t x_761; lean_object* x_762; lean_object* x_763; lean_object* x_764; lean_object* x_765; lean_object* x_766; lean_object* x_767; lean_object* x_768; lean_object* x_769; lean_object* x_770; lean_object* x_771; lean_object* x_772; lean_object* x_773; uint16_t x_774; lean_object* x_775; lean_object* x_776; lean_object* x_777; lean_object* x_778; lean_object* x_779; lean_object* x_780; lean_object* x_781; lean_object* x_782; lean_object* x_783; lean_object* x_784; lean_object* x_785; uint8_t x_786; lean_object* x_787; lean_object* x_788; lean_object* x_789; lean_object* x_790; lean_object* x_791; lean_object* x_792; lean_object* x_793; uint16_t x_794; lean_object* x_795; lean_object* x_796; lean_object* x_797; lean_object* x_798; lean_object* x_799; lean_object* x_800; lean_object* x_801; lean_object* x_802; lean_object* x_803; lean_object* x_804; lean_object* x_805; lean_object* x_806; lean_object* x_807; lean_object* x_808; lean_object* x_809; lean_object* x_810; lean_object* x_811; lean_object* x_812; lean_object* x_813; lean_object* x_814; lean_object* x_815; lean_object* x_816; lean_object* x_817; lean_object* x_818; lean_object* x_819; lean_object* x_820; lean_object* x_821; lean_object* x_822; lean_object* x_823; lean_object* x_824; lean_object* x_825; lean_object* x_826; lean_object* x_827; lean_object* x_828; lean_object* x_829; lean_object* x_830; lean_object* x_831; lean_object* x_832; lean_object* x_833; lean_object* x_834; lean_object* x_835; lean_object* x_836; lean_object* x_837; lean_object* x_838; lean_object* x_839; uint16_t x_840; lean_object* x_841; lean_object* x_842; lean_object* x_843; lean_object* x_844; lean_object* x_845; lean_object* x_846; lean_object* x_847; lean_object* x_848; lean_object* x_849; lean_object* x_850; uint8_t x_851; lean_object* x_852; lean_object* x_853; lean_object* x_854; lean_object* x_855; lean_object* x_856; lean_object* x_857; lean_object* x_858; lean_object* x_859; lean_object* x_860; lean_object* x_861; lean_object* x_862; lean_object* x_863; lean_object* x_864; lean_object* x_865; lean_object* x_866; lean_object* x_867; lean_object* x_868; lean_object* x_869; lean_object* x_870; lean_object* x_871; lean_object* x_872; lean_object* x_873; uint16_t x_874; lean_object* x_875; lean_object* x_876; lean_object* x_877; lean_object* x_878; lean_object* x_879; lean_object* x_880; lean_object* x_881; lean_object* x_882; lean_object* x_883; lean_object* x_884; lean_object* x_885; lean_object* x_886; lean_object* x_887; lean_object* x_888; lean_object* x_889; lean_object* x_890; lean_object* x_891; lean_object* x_892; lean_object* x_893; lean_object* x_894; lean_object* x_895; lean_object* x_896; lean_object* x_897; lean_object* x_898; lean_object* x_899; lean_object* x_900; lean_object* x_901; lean_object* x_902; lean_object* x_903; lean_object* x_904; lean_object* x_905; lean_object* x_906; lean_object* x_907; lean_object* x_908; lean_object* x_909; lean_object* x_910; lean_object* x_911; lean_object* x_912; lean_object* x_913; lean_object* x_914; lean_object* x_915; lean_object* x_916; lean_object* x_917; lean_object* x_918; lean_object* x_919; lean_object* x_920; lean_object* x_921; lean_object* x_922; lean_object* x_923; 
x_735 = lean_ctor_get(x_150, 0);
x_736 = lean_ctor_get_uint16(x_150, sizeof(void*)*4);
x_737 = lean_ctor_get(x_150, 1);
x_738 = lean_ctor_get(x_150, 2);
x_739 = lean_ctor_get(x_150, 3);
lean_inc(x_739);
lean_inc(x_738);
lean_inc(x_737);
lean_inc(x_735);
lean_dec(x_150);
x_740 = lean_array_get_size(x_735);
x_741 = lean_nat_sub(x_740, x_13);
x_742 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_743 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_743, 0, x_741);
lean_ctor_set(x_743, 1, x_742);
x_744 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_744, 0, x_743);
lean_ctor_set(x_744, 1, x_739);
x_745 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_745, 0, x_735);
lean_ctor_set(x_745, 1, x_737);
lean_ctor_set(x_745, 2, x_738);
lean_ctor_set(x_745, 3, x_744);
lean_ctor_set_uint16(x_745, sizeof(void*)*4, x_736);
x_746 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__20));
x_747 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_745, x_18, x_746);
x_748 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__21));
x_749 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_747, x_21, x_748);
x_750 = lp_sidfinity_MV3_CodeBuilder_label(x_749, x_746);
x_751 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_752 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_750, x_751);
x_753 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__22));
x_754 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_752, x_18, x_753);
x_755 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_754, x_21, x_748);
x_756 = lp_sidfinity_MV3_CodeBuilder_label(x_755, x_753);
x_757 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_758 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_756, x_757);
x_759 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__23, &lp_sidfinity_MV3_emitSustainEffects___closed__23_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__23);
x_760 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_758, x_759);
x_761 = 25;
x_762 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__24));
x_763 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_760, x_761, x_762);
x_764 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_763, x_21, x_748);
x_765 = lp_sidfinity_MV3_CodeBuilder_label(x_764, x_762);
x_766 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_765, x_108);
x_767 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_768 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_766, x_767);
x_769 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__25, &lp_sidfinity_MV3_emitSustainEffects___closed__25_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__25);
x_770 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_768, x_769);
x_771 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__27));
x_772 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_770, x_771);
x_773 = lean_ctor_get(x_772, 0);
lean_inc_ref(x_773);
x_774 = lean_ctor_get_uint16(x_772, sizeof(void*)*4);
x_775 = lean_ctor_get(x_772, 1);
lean_inc(x_775);
x_776 = lean_ctor_get(x_772, 2);
lean_inc(x_776);
x_777 = lean_ctor_get(x_772, 3);
lean_inc(x_777);
if (lean_is_exclusive(x_772)) {
 lean_ctor_release(x_772, 0);
 lean_ctor_release(x_772, 1);
 lean_ctor_release(x_772, 2);
 lean_ctor_release(x_772, 3);
 x_778 = x_772;
} else {
 lean_dec_ref(x_772);
 x_778 = lean_box(0);
}
x_779 = lean_array_get_size(x_773);
x_780 = lean_nat_sub(x_779, x_13);
x_781 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_781, 0, x_780);
lean_ctor_set(x_781, 1, x_757);
x_782 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_782, 0, x_781);
lean_ctor_set(x_782, 1, x_777);
if (lean_is_scalar(x_778)) {
 x_783 = lean_alloc_ctor(0, 4, 2);
} else {
 x_783 = x_778;
}
lean_ctor_set(x_783, 0, x_773);
lean_ctor_set(x_783, 1, x_775);
lean_ctor_set(x_783, 2, x_776);
lean_ctor_set(x_783, 3, x_782);
lean_ctor_set_uint16(x_783, sizeof(void*)*4, x_774);
x_784 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_783, x_53);
x_785 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_784, x_5);
x_786 = 24;
x_787 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__28));
x_788 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_785, x_786, x_787);
x_789 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_788, x_42);
x_790 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_789, x_3);
x_791 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_790, x_5);
x_792 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_791, x_7);
x_793 = lean_ctor_get(x_792, 0);
lean_inc_ref(x_793);
x_794 = lean_ctor_get_uint16(x_792, sizeof(void*)*4);
x_795 = lean_ctor_get(x_792, 1);
lean_inc(x_795);
x_796 = lean_ctor_get(x_792, 2);
lean_inc(x_796);
x_797 = lean_ctor_get(x_792, 3);
lean_inc(x_797);
if (lean_is_exclusive(x_792)) {
 lean_ctor_release(x_792, 0);
 lean_ctor_release(x_792, 1);
 lean_ctor_release(x_792, 2);
 lean_ctor_release(x_792, 3);
 x_798 = x_792;
} else {
 lean_dec_ref(x_792);
 x_798 = lean_box(0);
}
x_799 = lean_array_get_size(x_793);
x_800 = lean_nat_sub(x_799, x_13);
x_801 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_802 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_802, 0, x_800);
lean_ctor_set(x_802, 1, x_801);
x_803 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_803, 0, x_802);
lean_ctor_set(x_803, 1, x_797);
if (lean_is_scalar(x_798)) {
 x_804 = lean_alloc_ctor(0, 4, 2);
} else {
 x_804 = x_798;
}
lean_ctor_set(x_804, 0, x_793);
lean_ctor_set(x_804, 1, x_795);
lean_ctor_set(x_804, 2, x_796);
lean_ctor_set(x_804, 3, x_803);
lean_ctor_set_uint16(x_804, sizeof(void*)*4, x_794);
x_805 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_806 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_804, x_805);
x_807 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_806, x_751);
x_808 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_807, x_51);
x_809 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_808, x_751);
x_810 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_809, x_53);
x_811 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_810, x_5);
x_812 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_811, x_56);
x_813 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_814 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_812, x_813);
x_815 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_816 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_814, x_815);
x_817 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_818 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_816, x_817);
x_819 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_820 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_818, x_819);
x_821 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_822 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_820, x_21, x_821);
x_823 = lp_sidfinity_MV3_CodeBuilder_label(x_822, x_787);
x_824 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_823, x_42);
x_825 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_824, x_751);
x_826 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_825, x_53);
x_827 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_826, x_5);
x_828 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_827, x_751);
x_829 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_828, x_813);
x_830 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_831 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_829, x_830);
x_832 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_831, x_819);
x_833 = lp_sidfinity_MV3_CodeBuilder_label(x_832, x_821);
x_834 = lp_sidfinity_MV3_CodeBuilder_label(x_833, x_748);
x_835 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_834, x_42);
x_836 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_835, x_3);
x_837 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_836, x_5);
x_838 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_837, x_7);
x_839 = lean_ctor_get(x_838, 0);
lean_inc_ref(x_839);
x_840 = lean_ctor_get_uint16(x_838, sizeof(void*)*4);
x_841 = lean_ctor_get(x_838, 1);
lean_inc(x_841);
x_842 = lean_ctor_get(x_838, 2);
lean_inc(x_842);
x_843 = lean_ctor_get(x_838, 3);
lean_inc(x_843);
if (lean_is_exclusive(x_838)) {
 lean_ctor_release(x_838, 0);
 lean_ctor_release(x_838, 1);
 lean_ctor_release(x_838, 2);
 lean_ctor_release(x_838, 3);
 x_844 = x_838;
} else {
 lean_dec_ref(x_838);
 x_844 = lean_box(0);
}
x_845 = lean_array_get_size(x_839);
x_846 = lean_nat_sub(x_845, x_13);
x_847 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_848 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_848, 0, x_846);
lean_ctor_set(x_848, 1, x_847);
x_849 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_849, 0, x_848);
lean_ctor_set(x_849, 1, x_843);
if (lean_is_scalar(x_844)) {
 x_850 = lean_alloc_ctor(0, 4, 2);
} else {
 x_850 = x_844;
}
lean_ctor_set(x_850, 0, x_839);
lean_ctor_set(x_850, 1, x_841);
lean_ctor_set(x_850, 2, x_842);
lean_ctor_set(x_850, 3, x_849);
lean_ctor_set_uint16(x_850, sizeof(void*)*4, x_840);
x_851 = 26;
x_852 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_853 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_850, x_851, x_852);
x_854 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_855 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_853, x_854);
x_856 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_857 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_855, x_856);
x_858 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_857, x_851, x_852);
x_859 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_858, x_42);
x_860 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_859, x_751);
x_861 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_860, x_851, x_852);
x_862 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_861, x_51);
x_863 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_862, x_751);
x_864 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_863, x_53);
x_865 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_864, x_5);
x_866 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_865, x_56);
x_867 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_866, x_813);
x_868 = lp_sidfinity_MV3_CodeBuilder_label(x_867, x_852);
x_869 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_868, x_42);
x_870 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_869, x_3);
x_871 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_870, x_5);
x_872 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_871, x_7);
x_873 = lean_ctor_get(x_872, 0);
lean_inc_ref(x_873);
x_874 = lean_ctor_get_uint16(x_872, sizeof(void*)*4);
x_875 = lean_ctor_get(x_872, 1);
lean_inc(x_875);
x_876 = lean_ctor_get(x_872, 2);
lean_inc(x_876);
x_877 = lean_ctor_get(x_872, 3);
lean_inc(x_877);
if (lean_is_exclusive(x_872)) {
 lean_ctor_release(x_872, 0);
 lean_ctor_release(x_872, 1);
 lean_ctor_release(x_872, 2);
 lean_ctor_release(x_872, 3);
 x_878 = x_872;
} else {
 lean_dec_ref(x_872);
 x_878 = lean_box(0);
}
x_879 = lean_array_get_size(x_873);
x_880 = lean_nat_sub(x_879, x_13);
x_881 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_882 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_882, 0, x_880);
lean_ctor_set(x_882, 1, x_881);
x_883 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_883, 0, x_882);
lean_ctor_set(x_883, 1, x_877);
if (lean_is_scalar(x_878)) {
 x_884 = lean_alloc_ctor(0, 4, 2);
} else {
 x_884 = x_878;
}
lean_ctor_set(x_884, 0, x_873);
lean_ctor_set(x_884, 1, x_875);
lean_ctor_set(x_884, 2, x_876);
lean_ctor_set(x_884, 3, x_883);
lean_ctor_set_uint16(x_884, sizeof(void*)*4, x_874);
x_885 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_886 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_884, x_18, x_885);
x_887 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_888 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_886, x_21, x_887);
x_889 = lp_sidfinity_MV3_CodeBuilder_label(x_888, x_885);
x_890 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_889, x_51);
x_891 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_890, x_854);
x_892 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_891, x_856);
x_893 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_894 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_892, x_851, x_893);
x_895 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_894, x_79);
x_896 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_897 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_895, x_896);
x_898 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_899 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_897, x_898);
x_900 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_901 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_899, x_21, x_900);
x_902 = lp_sidfinity_MV3_CodeBuilder_label(x_901, x_893);
x_903 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_902, x_896);
x_904 = lp_sidfinity_MV3_CodeBuilder_label(x_903, x_900);
x_905 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_904, x_5);
x_906 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_907 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_905, x_906);
x_908 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_907, x_25);
x_909 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_910 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_908, x_909);
x_911 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_910, x_51);
x_912 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_911, x_42);
x_913 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_912, x_53);
x_914 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_913, x_5);
x_915 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_914, x_66);
x_916 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_915, x_813);
x_917 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_916, x_56);
x_918 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_919 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_917, x_918);
x_920 = lp_sidfinity_MV3_CodeBuilder_label(x_919, x_887);
x_921 = lp_sidfinity_I_rts;
x_922 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_920, x_921);
x_923 = lp_sidfinity_MV3_emitNoteLoadPath(x_922, x_2);
return x_923;
}
}
else
{
lean_object* x_924; uint16_t x_925; lean_object* x_926; lean_object* x_927; lean_object* x_928; lean_object* x_929; lean_object* x_930; lean_object* x_931; lean_object* x_932; lean_object* x_933; lean_object* x_934; lean_object* x_935; lean_object* x_936; lean_object* x_937; lean_object* x_938; lean_object* x_939; lean_object* x_940; lean_object* x_941; lean_object* x_942; lean_object* x_943; lean_object* x_944; lean_object* x_945; lean_object* x_946; lean_object* x_947; lean_object* x_948; lean_object* x_949; lean_object* x_950; lean_object* x_951; lean_object* x_952; lean_object* x_953; lean_object* x_954; lean_object* x_955; lean_object* x_956; lean_object* x_957; lean_object* x_958; uint16_t x_959; lean_object* x_960; lean_object* x_961; lean_object* x_962; lean_object* x_963; lean_object* x_964; lean_object* x_965; lean_object* x_966; lean_object* x_967; lean_object* x_968; lean_object* x_969; lean_object* x_970; lean_object* x_971; lean_object* x_972; lean_object* x_973; lean_object* x_974; lean_object* x_975; lean_object* x_976; lean_object* x_977; lean_object* x_978; lean_object* x_979; lean_object* x_980; lean_object* x_981; lean_object* x_982; lean_object* x_983; lean_object* x_984; uint8_t x_985; lean_object* x_986; lean_object* x_987; lean_object* x_988; lean_object* x_989; lean_object* x_990; lean_object* x_991; lean_object* x_992; lean_object* x_993; lean_object* x_994; lean_object* x_995; lean_object* x_996; lean_object* x_997; uint16_t x_998; lean_object* x_999; lean_object* x_1000; lean_object* x_1001; lean_object* x_1002; lean_object* x_1003; lean_object* x_1004; lean_object* x_1005; lean_object* x_1006; lean_object* x_1007; lean_object* x_1008; lean_object* x_1009; uint8_t x_1010; lean_object* x_1011; lean_object* x_1012; lean_object* x_1013; lean_object* x_1014; lean_object* x_1015; lean_object* x_1016; lean_object* x_1017; uint16_t x_1018; lean_object* x_1019; lean_object* x_1020; lean_object* x_1021; lean_object* x_1022; lean_object* x_1023; lean_object* x_1024; lean_object* x_1025; lean_object* x_1026; lean_object* x_1027; lean_object* x_1028; lean_object* x_1029; lean_object* x_1030; lean_object* x_1031; lean_object* x_1032; lean_object* x_1033; lean_object* x_1034; lean_object* x_1035; lean_object* x_1036; lean_object* x_1037; lean_object* x_1038; lean_object* x_1039; lean_object* x_1040; lean_object* x_1041; lean_object* x_1042; lean_object* x_1043; lean_object* x_1044; lean_object* x_1045; lean_object* x_1046; lean_object* x_1047; lean_object* x_1048; lean_object* x_1049; lean_object* x_1050; lean_object* x_1051; lean_object* x_1052; lean_object* x_1053; lean_object* x_1054; lean_object* x_1055; lean_object* x_1056; lean_object* x_1057; lean_object* x_1058; lean_object* x_1059; lean_object* x_1060; lean_object* x_1061; lean_object* x_1062; lean_object* x_1063; uint16_t x_1064; lean_object* x_1065; lean_object* x_1066; lean_object* x_1067; lean_object* x_1068; lean_object* x_1069; lean_object* x_1070; lean_object* x_1071; lean_object* x_1072; lean_object* x_1073; lean_object* x_1074; uint8_t x_1075; lean_object* x_1076; lean_object* x_1077; lean_object* x_1078; lean_object* x_1079; lean_object* x_1080; lean_object* x_1081; lean_object* x_1082; lean_object* x_1083; lean_object* x_1084; lean_object* x_1085; lean_object* x_1086; lean_object* x_1087; lean_object* x_1088; lean_object* x_1089; lean_object* x_1090; lean_object* x_1091; lean_object* x_1092; lean_object* x_1093; lean_object* x_1094; lean_object* x_1095; lean_object* x_1096; lean_object* x_1097; uint16_t x_1098; lean_object* x_1099; lean_object* x_1100; lean_object* x_1101; lean_object* x_1102; lean_object* x_1103; lean_object* x_1104; lean_object* x_1105; lean_object* x_1106; lean_object* x_1107; lean_object* x_1108; lean_object* x_1109; lean_object* x_1110; lean_object* x_1111; lean_object* x_1112; lean_object* x_1113; lean_object* x_1114; lean_object* x_1115; lean_object* x_1116; lean_object* x_1117; lean_object* x_1118; lean_object* x_1119; lean_object* x_1120; lean_object* x_1121; lean_object* x_1122; lean_object* x_1123; lean_object* x_1124; lean_object* x_1125; lean_object* x_1126; lean_object* x_1127; lean_object* x_1128; lean_object* x_1129; lean_object* x_1130; lean_object* x_1131; lean_object* x_1132; lean_object* x_1133; lean_object* x_1134; lean_object* x_1135; lean_object* x_1136; lean_object* x_1137; lean_object* x_1138; lean_object* x_1139; lean_object* x_1140; lean_object* x_1141; lean_object* x_1142; lean_object* x_1143; lean_object* x_1144; lean_object* x_1145; lean_object* x_1146; lean_object* x_1147; 
x_924 = lean_ctor_get(x_119, 0);
x_925 = lean_ctor_get_uint16(x_119, sizeof(void*)*4);
x_926 = lean_ctor_get(x_119, 1);
x_927 = lean_ctor_get(x_119, 2);
x_928 = lean_ctor_get(x_119, 3);
lean_inc(x_928);
lean_inc(x_927);
lean_inc(x_926);
lean_inc(x_924);
lean_dec(x_119);
x_929 = lean_array_get_size(x_924);
x_930 = lean_nat_sub(x_929, x_13);
x_931 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__18));
x_932 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_932, 0, x_930);
lean_ctor_set(x_932, 1, x_931);
x_933 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_933, 0, x_932);
lean_ctor_set(x_933, 1, x_928);
x_934 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_934, 0, x_924);
lean_ctor_set(x_934, 1, x_926);
lean_ctor_set(x_934, 2, x_927);
lean_ctor_set(x_934, 3, x_933);
lean_ctor_set_uint16(x_934, sizeof(void*)*4, x_925);
x_935 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_934, x_18, x_101);
x_936 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_937 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_935, x_936);
x_938 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_937, x_75);
x_939 = lp_sidfinity_MV3_CodeBuilder_label(x_938, x_101);
x_940 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_939, x_46);
x_941 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_940, x_51);
x_942 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_941, x_84);
x_943 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_944 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_942, x_943);
x_945 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_944, x_53);
x_946 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_945, x_5);
x_947 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_946, x_56);
x_948 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_947, x_58);
x_949 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3);
x_950 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_948, x_949);
x_951 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3);
x_952 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_950, x_951);
x_953 = lp_sidfinity_MV3_CodeBuilder_label(x_952, x_22);
x_954 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_953, x_42);
x_955 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_954, x_3);
x_956 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_955, x_5);
x_957 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_956, x_7);
x_958 = lean_ctor_get(x_957, 0);
lean_inc_ref(x_958);
x_959 = lean_ctor_get_uint16(x_957, sizeof(void*)*4);
x_960 = lean_ctor_get(x_957, 1);
lean_inc(x_960);
x_961 = lean_ctor_get(x_957, 2);
lean_inc(x_961);
x_962 = lean_ctor_get(x_957, 3);
lean_inc(x_962);
if (lean_is_exclusive(x_957)) {
 lean_ctor_release(x_957, 0);
 lean_ctor_release(x_957, 1);
 lean_ctor_release(x_957, 2);
 lean_ctor_release(x_957, 3);
 x_963 = x_957;
} else {
 lean_dec_ref(x_957);
 x_963 = lean_box(0);
}
x_964 = lean_array_get_size(x_958);
x_965 = lean_nat_sub(x_964, x_13);
x_966 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_967 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_967, 0, x_965);
lean_ctor_set(x_967, 1, x_966);
x_968 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_968, 0, x_967);
lean_ctor_set(x_968, 1, x_962);
if (lean_is_scalar(x_963)) {
 x_969 = lean_alloc_ctor(0, 4, 2);
} else {
 x_969 = x_963;
}
lean_ctor_set(x_969, 0, x_958);
lean_ctor_set(x_969, 1, x_960);
lean_ctor_set(x_969, 2, x_961);
lean_ctor_set(x_969, 3, x_968);
lean_ctor_set_uint16(x_969, sizeof(void*)*4, x_959);
x_970 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__20));
x_971 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_969, x_18, x_970);
x_972 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__21));
x_973 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_971, x_21, x_972);
x_974 = lp_sidfinity_MV3_CodeBuilder_label(x_973, x_970);
x_975 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_976 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_974, x_975);
x_977 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__22));
x_978 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_976, x_18, x_977);
x_979 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_978, x_21, x_972);
x_980 = lp_sidfinity_MV3_CodeBuilder_label(x_979, x_977);
x_981 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_982 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_980, x_981);
x_983 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__23, &lp_sidfinity_MV3_emitSustainEffects___closed__23_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__23);
x_984 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_982, x_983);
x_985 = 25;
x_986 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__24));
x_987 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_984, x_985, x_986);
x_988 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_987, x_21, x_972);
x_989 = lp_sidfinity_MV3_CodeBuilder_label(x_988, x_986);
x_990 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_989, x_108);
x_991 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_992 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_990, x_991);
x_993 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__25, &lp_sidfinity_MV3_emitSustainEffects___closed__25_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__25);
x_994 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_992, x_993);
x_995 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__27));
x_996 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_994, x_995);
x_997 = lean_ctor_get(x_996, 0);
lean_inc_ref(x_997);
x_998 = lean_ctor_get_uint16(x_996, sizeof(void*)*4);
x_999 = lean_ctor_get(x_996, 1);
lean_inc(x_999);
x_1000 = lean_ctor_get(x_996, 2);
lean_inc(x_1000);
x_1001 = lean_ctor_get(x_996, 3);
lean_inc(x_1001);
if (lean_is_exclusive(x_996)) {
 lean_ctor_release(x_996, 0);
 lean_ctor_release(x_996, 1);
 lean_ctor_release(x_996, 2);
 lean_ctor_release(x_996, 3);
 x_1002 = x_996;
} else {
 lean_dec_ref(x_996);
 x_1002 = lean_box(0);
}
x_1003 = lean_array_get_size(x_997);
x_1004 = lean_nat_sub(x_1003, x_13);
x_1005 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1005, 0, x_1004);
lean_ctor_set(x_1005, 1, x_981);
x_1006 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1006, 0, x_1005);
lean_ctor_set(x_1006, 1, x_1001);
if (lean_is_scalar(x_1002)) {
 x_1007 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1007 = x_1002;
}
lean_ctor_set(x_1007, 0, x_997);
lean_ctor_set(x_1007, 1, x_999);
lean_ctor_set(x_1007, 2, x_1000);
lean_ctor_set(x_1007, 3, x_1006);
lean_ctor_set_uint16(x_1007, sizeof(void*)*4, x_998);
x_1008 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1007, x_53);
x_1009 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1008, x_5);
x_1010 = 24;
x_1011 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__28));
x_1012 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1009, x_1010, x_1011);
x_1013 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1012, x_42);
x_1014 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1013, x_3);
x_1015 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1014, x_5);
x_1016 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1015, x_7);
x_1017 = lean_ctor_get(x_1016, 0);
lean_inc_ref(x_1017);
x_1018 = lean_ctor_get_uint16(x_1016, sizeof(void*)*4);
x_1019 = lean_ctor_get(x_1016, 1);
lean_inc(x_1019);
x_1020 = lean_ctor_get(x_1016, 2);
lean_inc(x_1020);
x_1021 = lean_ctor_get(x_1016, 3);
lean_inc(x_1021);
if (lean_is_exclusive(x_1016)) {
 lean_ctor_release(x_1016, 0);
 lean_ctor_release(x_1016, 1);
 lean_ctor_release(x_1016, 2);
 lean_ctor_release(x_1016, 3);
 x_1022 = x_1016;
} else {
 lean_dec_ref(x_1016);
 x_1022 = lean_box(0);
}
x_1023 = lean_array_get_size(x_1017);
x_1024 = lean_nat_sub(x_1023, x_13);
x_1025 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_1026 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1026, 0, x_1024);
lean_ctor_set(x_1026, 1, x_1025);
x_1027 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1027, 0, x_1026);
lean_ctor_set(x_1027, 1, x_1021);
if (lean_is_scalar(x_1022)) {
 x_1028 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1028 = x_1022;
}
lean_ctor_set(x_1028, 0, x_1017);
lean_ctor_set(x_1028, 1, x_1019);
lean_ctor_set(x_1028, 2, x_1020);
lean_ctor_set(x_1028, 3, x_1027);
lean_ctor_set_uint16(x_1028, sizeof(void*)*4, x_1018);
x_1029 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_1030 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1028, x_1029);
x_1031 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1030, x_975);
x_1032 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1031, x_51);
x_1033 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1032, x_975);
x_1034 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1033, x_53);
x_1035 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1034, x_5);
x_1036 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1035, x_56);
x_1037 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_1038 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1036, x_1037);
x_1039 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_1040 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1038, x_1039);
x_1041 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_1042 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1040, x_1041);
x_1043 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_1044 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1042, x_1043);
x_1045 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_1046 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1044, x_21, x_1045);
x_1047 = lp_sidfinity_MV3_CodeBuilder_label(x_1046, x_1011);
x_1048 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1047, x_42);
x_1049 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1048, x_975);
x_1050 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1049, x_53);
x_1051 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1050, x_5);
x_1052 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1051, x_975);
x_1053 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1052, x_1037);
x_1054 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_1055 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1053, x_1054);
x_1056 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1055, x_1043);
x_1057 = lp_sidfinity_MV3_CodeBuilder_label(x_1056, x_1045);
x_1058 = lp_sidfinity_MV3_CodeBuilder_label(x_1057, x_972);
x_1059 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1058, x_42);
x_1060 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1059, x_3);
x_1061 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1060, x_5);
x_1062 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1061, x_7);
x_1063 = lean_ctor_get(x_1062, 0);
lean_inc_ref(x_1063);
x_1064 = lean_ctor_get_uint16(x_1062, sizeof(void*)*4);
x_1065 = lean_ctor_get(x_1062, 1);
lean_inc(x_1065);
x_1066 = lean_ctor_get(x_1062, 2);
lean_inc(x_1066);
x_1067 = lean_ctor_get(x_1062, 3);
lean_inc(x_1067);
if (lean_is_exclusive(x_1062)) {
 lean_ctor_release(x_1062, 0);
 lean_ctor_release(x_1062, 1);
 lean_ctor_release(x_1062, 2);
 lean_ctor_release(x_1062, 3);
 x_1068 = x_1062;
} else {
 lean_dec_ref(x_1062);
 x_1068 = lean_box(0);
}
x_1069 = lean_array_get_size(x_1063);
x_1070 = lean_nat_sub(x_1069, x_13);
x_1071 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_1072 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1072, 0, x_1070);
lean_ctor_set(x_1072, 1, x_1071);
x_1073 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1073, 0, x_1072);
lean_ctor_set(x_1073, 1, x_1067);
if (lean_is_scalar(x_1068)) {
 x_1074 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1074 = x_1068;
}
lean_ctor_set(x_1074, 0, x_1063);
lean_ctor_set(x_1074, 1, x_1065);
lean_ctor_set(x_1074, 2, x_1066);
lean_ctor_set(x_1074, 3, x_1073);
lean_ctor_set_uint16(x_1074, sizeof(void*)*4, x_1064);
x_1075 = 26;
x_1076 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_1077 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1074, x_1075, x_1076);
x_1078 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_1079 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1077, x_1078);
x_1080 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_1081 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1079, x_1080);
x_1082 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1081, x_1075, x_1076);
x_1083 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1082, x_42);
x_1084 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1083, x_975);
x_1085 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1084, x_1075, x_1076);
x_1086 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1085, x_51);
x_1087 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1086, x_975);
x_1088 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1087, x_53);
x_1089 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1088, x_5);
x_1090 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1089, x_56);
x_1091 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1090, x_1037);
x_1092 = lp_sidfinity_MV3_CodeBuilder_label(x_1091, x_1076);
x_1093 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1092, x_42);
x_1094 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1093, x_3);
x_1095 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1094, x_5);
x_1096 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1095, x_7);
x_1097 = lean_ctor_get(x_1096, 0);
lean_inc_ref(x_1097);
x_1098 = lean_ctor_get_uint16(x_1096, sizeof(void*)*4);
x_1099 = lean_ctor_get(x_1096, 1);
lean_inc(x_1099);
x_1100 = lean_ctor_get(x_1096, 2);
lean_inc(x_1100);
x_1101 = lean_ctor_get(x_1096, 3);
lean_inc(x_1101);
if (lean_is_exclusive(x_1096)) {
 lean_ctor_release(x_1096, 0);
 lean_ctor_release(x_1096, 1);
 lean_ctor_release(x_1096, 2);
 lean_ctor_release(x_1096, 3);
 x_1102 = x_1096;
} else {
 lean_dec_ref(x_1096);
 x_1102 = lean_box(0);
}
x_1103 = lean_array_get_size(x_1097);
x_1104 = lean_nat_sub(x_1103, x_13);
x_1105 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_1106 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1106, 0, x_1104);
lean_ctor_set(x_1106, 1, x_1105);
x_1107 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1107, 0, x_1106);
lean_ctor_set(x_1107, 1, x_1101);
if (lean_is_scalar(x_1102)) {
 x_1108 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1108 = x_1102;
}
lean_ctor_set(x_1108, 0, x_1097);
lean_ctor_set(x_1108, 1, x_1099);
lean_ctor_set(x_1108, 2, x_1100);
lean_ctor_set(x_1108, 3, x_1107);
lean_ctor_set_uint16(x_1108, sizeof(void*)*4, x_1098);
x_1109 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_1110 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1108, x_18, x_1109);
x_1111 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_1112 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1110, x_21, x_1111);
x_1113 = lp_sidfinity_MV3_CodeBuilder_label(x_1112, x_1109);
x_1114 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1113, x_51);
x_1115 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1114, x_1078);
x_1116 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1115, x_1080);
x_1117 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_1118 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1116, x_1075, x_1117);
x_1119 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1118, x_79);
x_1120 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_1121 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1119, x_1120);
x_1122 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_1123 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1121, x_1122);
x_1124 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_1125 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1123, x_21, x_1124);
x_1126 = lp_sidfinity_MV3_CodeBuilder_label(x_1125, x_1117);
x_1127 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1126, x_1120);
x_1128 = lp_sidfinity_MV3_CodeBuilder_label(x_1127, x_1124);
x_1129 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1128, x_5);
x_1130 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_1131 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1129, x_1130);
x_1132 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1131, x_25);
x_1133 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_1134 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1132, x_1133);
x_1135 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1134, x_51);
x_1136 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1135, x_42);
x_1137 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1136, x_53);
x_1138 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1137, x_5);
x_1139 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1138, x_66);
x_1140 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1139, x_1037);
x_1141 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1140, x_56);
x_1142 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_1143 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1141, x_1142);
x_1144 = lp_sidfinity_MV3_CodeBuilder_label(x_1143, x_1111);
x_1145 = lp_sidfinity_I_rts;
x_1146 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1144, x_1145);
x_1147 = lp_sidfinity_MV3_emitNoteLoadPath(x_1146, x_2);
return x_1147;
}
}
else
{
lean_object* x_1148; uint16_t x_1149; lean_object* x_1150; lean_object* x_1151; lean_object* x_1152; lean_object* x_1153; lean_object* x_1154; lean_object* x_1155; lean_object* x_1156; lean_object* x_1157; lean_object* x_1158; lean_object* x_1159; lean_object* x_1160; lean_object* x_1161; lean_object* x_1162; lean_object* x_1163; lean_object* x_1164; lean_object* x_1165; lean_object* x_1166; lean_object* x_1167; lean_object* x_1168; lean_object* x_1169; lean_object* x_1170; lean_object* x_1171; lean_object* x_1172; lean_object* x_1173; lean_object* x_1174; lean_object* x_1175; lean_object* x_1176; lean_object* x_1177; lean_object* x_1178; uint16_t x_1179; lean_object* x_1180; lean_object* x_1181; lean_object* x_1182; lean_object* x_1183; lean_object* x_1184; lean_object* x_1185; lean_object* x_1186; lean_object* x_1187; lean_object* x_1188; lean_object* x_1189; lean_object* x_1190; lean_object* x_1191; lean_object* x_1192; lean_object* x_1193; lean_object* x_1194; lean_object* x_1195; lean_object* x_1196; lean_object* x_1197; lean_object* x_1198; lean_object* x_1199; lean_object* x_1200; lean_object* x_1201; lean_object* x_1202; lean_object* x_1203; lean_object* x_1204; lean_object* x_1205; lean_object* x_1206; lean_object* x_1207; lean_object* x_1208; lean_object* x_1209; lean_object* x_1210; lean_object* x_1211; lean_object* x_1212; lean_object* x_1213; uint16_t x_1214; lean_object* x_1215; lean_object* x_1216; lean_object* x_1217; lean_object* x_1218; lean_object* x_1219; lean_object* x_1220; lean_object* x_1221; lean_object* x_1222; lean_object* x_1223; lean_object* x_1224; lean_object* x_1225; lean_object* x_1226; lean_object* x_1227; lean_object* x_1228; lean_object* x_1229; lean_object* x_1230; lean_object* x_1231; lean_object* x_1232; lean_object* x_1233; lean_object* x_1234; lean_object* x_1235; lean_object* x_1236; lean_object* x_1237; lean_object* x_1238; lean_object* x_1239; uint8_t x_1240; lean_object* x_1241; lean_object* x_1242; lean_object* x_1243; lean_object* x_1244; lean_object* x_1245; lean_object* x_1246; lean_object* x_1247; lean_object* x_1248; lean_object* x_1249; lean_object* x_1250; lean_object* x_1251; lean_object* x_1252; uint16_t x_1253; lean_object* x_1254; lean_object* x_1255; lean_object* x_1256; lean_object* x_1257; lean_object* x_1258; lean_object* x_1259; lean_object* x_1260; lean_object* x_1261; lean_object* x_1262; lean_object* x_1263; lean_object* x_1264; uint8_t x_1265; lean_object* x_1266; lean_object* x_1267; lean_object* x_1268; lean_object* x_1269; lean_object* x_1270; lean_object* x_1271; lean_object* x_1272; uint16_t x_1273; lean_object* x_1274; lean_object* x_1275; lean_object* x_1276; lean_object* x_1277; lean_object* x_1278; lean_object* x_1279; lean_object* x_1280; lean_object* x_1281; lean_object* x_1282; lean_object* x_1283; lean_object* x_1284; lean_object* x_1285; lean_object* x_1286; lean_object* x_1287; lean_object* x_1288; lean_object* x_1289; lean_object* x_1290; lean_object* x_1291; lean_object* x_1292; lean_object* x_1293; lean_object* x_1294; lean_object* x_1295; lean_object* x_1296; lean_object* x_1297; lean_object* x_1298; lean_object* x_1299; lean_object* x_1300; lean_object* x_1301; lean_object* x_1302; lean_object* x_1303; lean_object* x_1304; lean_object* x_1305; lean_object* x_1306; lean_object* x_1307; lean_object* x_1308; lean_object* x_1309; lean_object* x_1310; lean_object* x_1311; lean_object* x_1312; lean_object* x_1313; lean_object* x_1314; lean_object* x_1315; lean_object* x_1316; lean_object* x_1317; lean_object* x_1318; uint16_t x_1319; lean_object* x_1320; lean_object* x_1321; lean_object* x_1322; lean_object* x_1323; lean_object* x_1324; lean_object* x_1325; lean_object* x_1326; lean_object* x_1327; lean_object* x_1328; lean_object* x_1329; uint8_t x_1330; lean_object* x_1331; lean_object* x_1332; lean_object* x_1333; lean_object* x_1334; lean_object* x_1335; lean_object* x_1336; lean_object* x_1337; lean_object* x_1338; lean_object* x_1339; lean_object* x_1340; lean_object* x_1341; lean_object* x_1342; lean_object* x_1343; lean_object* x_1344; lean_object* x_1345; lean_object* x_1346; lean_object* x_1347; lean_object* x_1348; lean_object* x_1349; lean_object* x_1350; lean_object* x_1351; lean_object* x_1352; uint16_t x_1353; lean_object* x_1354; lean_object* x_1355; lean_object* x_1356; lean_object* x_1357; lean_object* x_1358; lean_object* x_1359; lean_object* x_1360; lean_object* x_1361; lean_object* x_1362; lean_object* x_1363; lean_object* x_1364; lean_object* x_1365; lean_object* x_1366; lean_object* x_1367; lean_object* x_1368; lean_object* x_1369; lean_object* x_1370; lean_object* x_1371; lean_object* x_1372; lean_object* x_1373; lean_object* x_1374; lean_object* x_1375; lean_object* x_1376; lean_object* x_1377; lean_object* x_1378; lean_object* x_1379; lean_object* x_1380; lean_object* x_1381; lean_object* x_1382; lean_object* x_1383; lean_object* x_1384; lean_object* x_1385; lean_object* x_1386; lean_object* x_1387; lean_object* x_1388; lean_object* x_1389; lean_object* x_1390; lean_object* x_1391; lean_object* x_1392; lean_object* x_1393; lean_object* x_1394; lean_object* x_1395; lean_object* x_1396; lean_object* x_1397; lean_object* x_1398; lean_object* x_1399; lean_object* x_1400; lean_object* x_1401; lean_object* x_1402; 
x_1148 = lean_ctor_get(x_92, 0);
x_1149 = lean_ctor_get_uint16(x_92, sizeof(void*)*4);
x_1150 = lean_ctor_get(x_92, 1);
x_1151 = lean_ctor_get(x_92, 2);
x_1152 = lean_ctor_get(x_92, 3);
lean_inc(x_1152);
lean_inc(x_1151);
lean_inc(x_1150);
lean_inc(x_1148);
lean_dec(x_92);
x_1153 = lean_array_get_size(x_1148);
x_1154 = lean_nat_sub(x_1153, x_13);
x_1155 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__13));
x_1156 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1156, 0, x_1154);
lean_ctor_set(x_1156, 1, x_1155);
x_1157 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1157, 0, x_1156);
lean_ctor_set(x_1157, 1, x_1152);
x_1158 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_1158, 0, x_1148);
lean_ctor_set(x_1158, 1, x_1150);
lean_ctor_set(x_1158, 2, x_1151);
lean_ctor_set(x_1158, 3, x_1157);
lean_ctor_set_uint16(x_1158, sizeof(void*)*4, x_1149);
x_1159 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__14));
x_1160 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1158, x_18, x_1159);
x_1161 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__15, &lp_sidfinity_MV3_emitSustainEffects___closed__15_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__15);
x_1162 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1160, x_1161);
x_1163 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1162, x_75);
x_1164 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1163, x_21, x_1159);
x_1165 = lp_sidfinity_MV3_CodeBuilder_label(x_1164, x_77);
x_1166 = lp_sidfinity_I_sec;
x_1167 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1165, x_1166);
x_1168 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1167, x_46);
x_1169 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__16, &lp_sidfinity_MV3_emitSustainEffects___closed__16_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__16);
x_1170 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1168, x_1169);
x_1171 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1170, x_46);
x_1172 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1171, x_84);
x_1173 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__17, &lp_sidfinity_MV3_emitSustainEffects___closed__17_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__17);
x_1174 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1172, x_1173);
x_1175 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1174, x_88);
x_1176 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1175, x_84);
x_1177 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1176, x_91);
x_1178 = lean_ctor_get(x_1177, 0);
lean_inc_ref(x_1178);
x_1179 = lean_ctor_get_uint16(x_1177, sizeof(void*)*4);
x_1180 = lean_ctor_get(x_1177, 1);
lean_inc(x_1180);
x_1181 = lean_ctor_get(x_1177, 2);
lean_inc(x_1181);
x_1182 = lean_ctor_get(x_1177, 3);
lean_inc(x_1182);
if (lean_is_exclusive(x_1177)) {
 lean_ctor_release(x_1177, 0);
 lean_ctor_release(x_1177, 1);
 lean_ctor_release(x_1177, 2);
 lean_ctor_release(x_1177, 3);
 x_1183 = x_1177;
} else {
 lean_dec_ref(x_1177);
 x_1183 = lean_box(0);
}
x_1184 = lean_array_get_size(x_1178);
x_1185 = lean_nat_sub(x_1184, x_13);
x_1186 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__18));
x_1187 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1187, 0, x_1185);
lean_ctor_set(x_1187, 1, x_1186);
x_1188 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1188, 0, x_1187);
lean_ctor_set(x_1188, 1, x_1182);
if (lean_is_scalar(x_1183)) {
 x_1189 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1189 = x_1183;
}
lean_ctor_set(x_1189, 0, x_1178);
lean_ctor_set(x_1189, 1, x_1180);
lean_ctor_set(x_1189, 2, x_1181);
lean_ctor_set(x_1189, 3, x_1188);
lean_ctor_set_uint16(x_1189, sizeof(void*)*4, x_1179);
x_1190 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1189, x_18, x_1159);
x_1191 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_1192 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1190, x_1191);
x_1193 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1192, x_75);
x_1194 = lp_sidfinity_MV3_CodeBuilder_label(x_1193, x_1159);
x_1195 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1194, x_46);
x_1196 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1195, x_51);
x_1197 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1196, x_84);
x_1198 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_1199 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1197, x_1198);
x_1200 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1199, x_53);
x_1201 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1200, x_5);
x_1202 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1201, x_56);
x_1203 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1202, x_58);
x_1204 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3);
x_1205 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1203, x_1204);
x_1206 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3);
x_1207 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1205, x_1206);
x_1208 = lp_sidfinity_MV3_CodeBuilder_label(x_1207, x_22);
x_1209 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1208, x_42);
x_1210 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1209, x_3);
x_1211 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1210, x_5);
x_1212 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1211, x_7);
x_1213 = lean_ctor_get(x_1212, 0);
lean_inc_ref(x_1213);
x_1214 = lean_ctor_get_uint16(x_1212, sizeof(void*)*4);
x_1215 = lean_ctor_get(x_1212, 1);
lean_inc(x_1215);
x_1216 = lean_ctor_get(x_1212, 2);
lean_inc(x_1216);
x_1217 = lean_ctor_get(x_1212, 3);
lean_inc(x_1217);
if (lean_is_exclusive(x_1212)) {
 lean_ctor_release(x_1212, 0);
 lean_ctor_release(x_1212, 1);
 lean_ctor_release(x_1212, 2);
 lean_ctor_release(x_1212, 3);
 x_1218 = x_1212;
} else {
 lean_dec_ref(x_1212);
 x_1218 = lean_box(0);
}
x_1219 = lean_array_get_size(x_1213);
x_1220 = lean_nat_sub(x_1219, x_13);
x_1221 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_1222 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1222, 0, x_1220);
lean_ctor_set(x_1222, 1, x_1221);
x_1223 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1223, 0, x_1222);
lean_ctor_set(x_1223, 1, x_1217);
if (lean_is_scalar(x_1218)) {
 x_1224 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1224 = x_1218;
}
lean_ctor_set(x_1224, 0, x_1213);
lean_ctor_set(x_1224, 1, x_1215);
lean_ctor_set(x_1224, 2, x_1216);
lean_ctor_set(x_1224, 3, x_1223);
lean_ctor_set_uint16(x_1224, sizeof(void*)*4, x_1214);
x_1225 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__20));
x_1226 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1224, x_18, x_1225);
x_1227 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__21));
x_1228 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1226, x_21, x_1227);
x_1229 = lp_sidfinity_MV3_CodeBuilder_label(x_1228, x_1225);
x_1230 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_1231 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1229, x_1230);
x_1232 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__22));
x_1233 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1231, x_18, x_1232);
x_1234 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1233, x_21, x_1227);
x_1235 = lp_sidfinity_MV3_CodeBuilder_label(x_1234, x_1232);
x_1236 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_1237 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1235, x_1236);
x_1238 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__23, &lp_sidfinity_MV3_emitSustainEffects___closed__23_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__23);
x_1239 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1237, x_1238);
x_1240 = 25;
x_1241 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__24));
x_1242 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1239, x_1240, x_1241);
x_1243 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1242, x_21, x_1227);
x_1244 = lp_sidfinity_MV3_CodeBuilder_label(x_1243, x_1241);
x_1245 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1244, x_1166);
x_1246 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_1247 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1245, x_1246);
x_1248 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__25, &lp_sidfinity_MV3_emitSustainEffects___closed__25_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__25);
x_1249 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1247, x_1248);
x_1250 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__27));
x_1251 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1249, x_1250);
x_1252 = lean_ctor_get(x_1251, 0);
lean_inc_ref(x_1252);
x_1253 = lean_ctor_get_uint16(x_1251, sizeof(void*)*4);
x_1254 = lean_ctor_get(x_1251, 1);
lean_inc(x_1254);
x_1255 = lean_ctor_get(x_1251, 2);
lean_inc(x_1255);
x_1256 = lean_ctor_get(x_1251, 3);
lean_inc(x_1256);
if (lean_is_exclusive(x_1251)) {
 lean_ctor_release(x_1251, 0);
 lean_ctor_release(x_1251, 1);
 lean_ctor_release(x_1251, 2);
 lean_ctor_release(x_1251, 3);
 x_1257 = x_1251;
} else {
 lean_dec_ref(x_1251);
 x_1257 = lean_box(0);
}
x_1258 = lean_array_get_size(x_1252);
x_1259 = lean_nat_sub(x_1258, x_13);
x_1260 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1260, 0, x_1259);
lean_ctor_set(x_1260, 1, x_1236);
x_1261 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1261, 0, x_1260);
lean_ctor_set(x_1261, 1, x_1256);
if (lean_is_scalar(x_1257)) {
 x_1262 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1262 = x_1257;
}
lean_ctor_set(x_1262, 0, x_1252);
lean_ctor_set(x_1262, 1, x_1254);
lean_ctor_set(x_1262, 2, x_1255);
lean_ctor_set(x_1262, 3, x_1261);
lean_ctor_set_uint16(x_1262, sizeof(void*)*4, x_1253);
x_1263 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1262, x_53);
x_1264 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1263, x_5);
x_1265 = 24;
x_1266 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__28));
x_1267 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1264, x_1265, x_1266);
x_1268 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1267, x_42);
x_1269 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1268, x_3);
x_1270 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1269, x_5);
x_1271 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1270, x_7);
x_1272 = lean_ctor_get(x_1271, 0);
lean_inc_ref(x_1272);
x_1273 = lean_ctor_get_uint16(x_1271, sizeof(void*)*4);
x_1274 = lean_ctor_get(x_1271, 1);
lean_inc(x_1274);
x_1275 = lean_ctor_get(x_1271, 2);
lean_inc(x_1275);
x_1276 = lean_ctor_get(x_1271, 3);
lean_inc(x_1276);
if (lean_is_exclusive(x_1271)) {
 lean_ctor_release(x_1271, 0);
 lean_ctor_release(x_1271, 1);
 lean_ctor_release(x_1271, 2);
 lean_ctor_release(x_1271, 3);
 x_1277 = x_1271;
} else {
 lean_dec_ref(x_1271);
 x_1277 = lean_box(0);
}
x_1278 = lean_array_get_size(x_1272);
x_1279 = lean_nat_sub(x_1278, x_13);
x_1280 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_1281 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1281, 0, x_1279);
lean_ctor_set(x_1281, 1, x_1280);
x_1282 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1282, 0, x_1281);
lean_ctor_set(x_1282, 1, x_1276);
if (lean_is_scalar(x_1277)) {
 x_1283 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1283 = x_1277;
}
lean_ctor_set(x_1283, 0, x_1272);
lean_ctor_set(x_1283, 1, x_1274);
lean_ctor_set(x_1283, 2, x_1275);
lean_ctor_set(x_1283, 3, x_1282);
lean_ctor_set_uint16(x_1283, sizeof(void*)*4, x_1273);
x_1284 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_1285 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1283, x_1284);
x_1286 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1285, x_1230);
x_1287 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1286, x_51);
x_1288 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1287, x_1230);
x_1289 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1288, x_53);
x_1290 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1289, x_5);
x_1291 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1290, x_56);
x_1292 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_1293 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1291, x_1292);
x_1294 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_1295 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1293, x_1294);
x_1296 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_1297 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1295, x_1296);
x_1298 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_1299 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1297, x_1298);
x_1300 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_1301 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1299, x_21, x_1300);
x_1302 = lp_sidfinity_MV3_CodeBuilder_label(x_1301, x_1266);
x_1303 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1302, x_42);
x_1304 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1303, x_1230);
x_1305 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1304, x_53);
x_1306 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1305, x_5);
x_1307 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1306, x_1230);
x_1308 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1307, x_1292);
x_1309 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_1310 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1308, x_1309);
x_1311 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1310, x_1298);
x_1312 = lp_sidfinity_MV3_CodeBuilder_label(x_1311, x_1300);
x_1313 = lp_sidfinity_MV3_CodeBuilder_label(x_1312, x_1227);
x_1314 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1313, x_42);
x_1315 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1314, x_3);
x_1316 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1315, x_5);
x_1317 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1316, x_7);
x_1318 = lean_ctor_get(x_1317, 0);
lean_inc_ref(x_1318);
x_1319 = lean_ctor_get_uint16(x_1317, sizeof(void*)*4);
x_1320 = lean_ctor_get(x_1317, 1);
lean_inc(x_1320);
x_1321 = lean_ctor_get(x_1317, 2);
lean_inc(x_1321);
x_1322 = lean_ctor_get(x_1317, 3);
lean_inc(x_1322);
if (lean_is_exclusive(x_1317)) {
 lean_ctor_release(x_1317, 0);
 lean_ctor_release(x_1317, 1);
 lean_ctor_release(x_1317, 2);
 lean_ctor_release(x_1317, 3);
 x_1323 = x_1317;
} else {
 lean_dec_ref(x_1317);
 x_1323 = lean_box(0);
}
x_1324 = lean_array_get_size(x_1318);
x_1325 = lean_nat_sub(x_1324, x_13);
x_1326 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_1327 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1327, 0, x_1325);
lean_ctor_set(x_1327, 1, x_1326);
x_1328 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1328, 0, x_1327);
lean_ctor_set(x_1328, 1, x_1322);
if (lean_is_scalar(x_1323)) {
 x_1329 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1329 = x_1323;
}
lean_ctor_set(x_1329, 0, x_1318);
lean_ctor_set(x_1329, 1, x_1320);
lean_ctor_set(x_1329, 2, x_1321);
lean_ctor_set(x_1329, 3, x_1328);
lean_ctor_set_uint16(x_1329, sizeof(void*)*4, x_1319);
x_1330 = 26;
x_1331 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_1332 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1329, x_1330, x_1331);
x_1333 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_1334 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1332, x_1333);
x_1335 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_1336 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1334, x_1335);
x_1337 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1336, x_1330, x_1331);
x_1338 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1337, x_42);
x_1339 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1338, x_1230);
x_1340 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1339, x_1330, x_1331);
x_1341 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1340, x_51);
x_1342 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1341, x_1230);
x_1343 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1342, x_53);
x_1344 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1343, x_5);
x_1345 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1344, x_56);
x_1346 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1345, x_1292);
x_1347 = lp_sidfinity_MV3_CodeBuilder_label(x_1346, x_1331);
x_1348 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1347, x_42);
x_1349 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1348, x_3);
x_1350 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1349, x_5);
x_1351 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1350, x_7);
x_1352 = lean_ctor_get(x_1351, 0);
lean_inc_ref(x_1352);
x_1353 = lean_ctor_get_uint16(x_1351, sizeof(void*)*4);
x_1354 = lean_ctor_get(x_1351, 1);
lean_inc(x_1354);
x_1355 = lean_ctor_get(x_1351, 2);
lean_inc(x_1355);
x_1356 = lean_ctor_get(x_1351, 3);
lean_inc(x_1356);
if (lean_is_exclusive(x_1351)) {
 lean_ctor_release(x_1351, 0);
 lean_ctor_release(x_1351, 1);
 lean_ctor_release(x_1351, 2);
 lean_ctor_release(x_1351, 3);
 x_1357 = x_1351;
} else {
 lean_dec_ref(x_1351);
 x_1357 = lean_box(0);
}
x_1358 = lean_array_get_size(x_1352);
x_1359 = lean_nat_sub(x_1358, x_13);
x_1360 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_1361 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1361, 0, x_1359);
lean_ctor_set(x_1361, 1, x_1360);
x_1362 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1362, 0, x_1361);
lean_ctor_set(x_1362, 1, x_1356);
if (lean_is_scalar(x_1357)) {
 x_1363 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1363 = x_1357;
}
lean_ctor_set(x_1363, 0, x_1352);
lean_ctor_set(x_1363, 1, x_1354);
lean_ctor_set(x_1363, 2, x_1355);
lean_ctor_set(x_1363, 3, x_1362);
lean_ctor_set_uint16(x_1363, sizeof(void*)*4, x_1353);
x_1364 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_1365 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1363, x_18, x_1364);
x_1366 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_1367 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1365, x_21, x_1366);
x_1368 = lp_sidfinity_MV3_CodeBuilder_label(x_1367, x_1364);
x_1369 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1368, x_51);
x_1370 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1369, x_1333);
x_1371 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1370, x_1335);
x_1372 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_1373 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1371, x_1330, x_1372);
x_1374 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1373, x_79);
x_1375 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_1376 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1374, x_1375);
x_1377 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_1378 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1376, x_1377);
x_1379 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_1380 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1378, x_21, x_1379);
x_1381 = lp_sidfinity_MV3_CodeBuilder_label(x_1380, x_1372);
x_1382 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1381, x_1375);
x_1383 = lp_sidfinity_MV3_CodeBuilder_label(x_1382, x_1379);
x_1384 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1383, x_5);
x_1385 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_1386 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1384, x_1385);
x_1387 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1386, x_25);
x_1388 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_1389 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1387, x_1388);
x_1390 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1389, x_51);
x_1391 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1390, x_42);
x_1392 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1391, x_53);
x_1393 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1392, x_5);
x_1394 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1393, x_66);
x_1395 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1394, x_1292);
x_1396 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1395, x_56);
x_1397 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_1398 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1396, x_1397);
x_1399 = lp_sidfinity_MV3_CodeBuilder_label(x_1398, x_1366);
x_1400 = lp_sidfinity_I_rts;
x_1401 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1399, x_1400);
x_1402 = lp_sidfinity_MV3_emitNoteLoadPath(x_1401, x_2);
return x_1402;
}
}
else
{
lean_object* x_1403; uint16_t x_1404; lean_object* x_1405; lean_object* x_1406; lean_object* x_1407; lean_object* x_1408; lean_object* x_1409; lean_object* x_1410; lean_object* x_1411; lean_object* x_1412; lean_object* x_1413; uint8_t x_1414; lean_object* x_1415; lean_object* x_1416; lean_object* x_1417; lean_object* x_1418; lean_object* x_1419; lean_object* x_1420; lean_object* x_1421; lean_object* x_1422; lean_object* x_1423; lean_object* x_1424; lean_object* x_1425; lean_object* x_1426; lean_object* x_1427; lean_object* x_1428; lean_object* x_1429; lean_object* x_1430; lean_object* x_1431; lean_object* x_1432; lean_object* x_1433; lean_object* x_1434; lean_object* x_1435; lean_object* x_1436; lean_object* x_1437; lean_object* x_1438; lean_object* x_1439; lean_object* x_1440; lean_object* x_1441; uint8_t x_1442; lean_object* x_1443; lean_object* x_1444; lean_object* x_1445; lean_object* x_1446; lean_object* x_1447; lean_object* x_1448; lean_object* x_1449; lean_object* x_1450; lean_object* x_1451; lean_object* x_1452; lean_object* x_1453; lean_object* x_1454; lean_object* x_1455; lean_object* x_1456; lean_object* x_1457; lean_object* x_1458; lean_object* x_1459; lean_object* x_1460; lean_object* x_1461; lean_object* x_1462; lean_object* x_1463; lean_object* x_1464; lean_object* x_1465; lean_object* x_1466; lean_object* x_1467; lean_object* x_1468; lean_object* x_1469; lean_object* x_1470; lean_object* x_1471; uint16_t x_1472; lean_object* x_1473; lean_object* x_1474; lean_object* x_1475; lean_object* x_1476; lean_object* x_1477; lean_object* x_1478; lean_object* x_1479; lean_object* x_1480; lean_object* x_1481; lean_object* x_1482; lean_object* x_1483; lean_object* x_1484; lean_object* x_1485; lean_object* x_1486; lean_object* x_1487; lean_object* x_1488; lean_object* x_1489; lean_object* x_1490; lean_object* x_1491; lean_object* x_1492; lean_object* x_1493; lean_object* x_1494; lean_object* x_1495; lean_object* x_1496; lean_object* x_1497; lean_object* x_1498; lean_object* x_1499; lean_object* x_1500; lean_object* x_1501; lean_object* x_1502; uint16_t x_1503; lean_object* x_1504; lean_object* x_1505; lean_object* x_1506; lean_object* x_1507; lean_object* x_1508; lean_object* x_1509; lean_object* x_1510; lean_object* x_1511; lean_object* x_1512; lean_object* x_1513; lean_object* x_1514; lean_object* x_1515; lean_object* x_1516; lean_object* x_1517; lean_object* x_1518; lean_object* x_1519; lean_object* x_1520; lean_object* x_1521; lean_object* x_1522; lean_object* x_1523; lean_object* x_1524; lean_object* x_1525; lean_object* x_1526; lean_object* x_1527; lean_object* x_1528; lean_object* x_1529; lean_object* x_1530; lean_object* x_1531; lean_object* x_1532; lean_object* x_1533; lean_object* x_1534; lean_object* x_1535; lean_object* x_1536; lean_object* x_1537; uint16_t x_1538; lean_object* x_1539; lean_object* x_1540; lean_object* x_1541; lean_object* x_1542; lean_object* x_1543; lean_object* x_1544; lean_object* x_1545; lean_object* x_1546; lean_object* x_1547; lean_object* x_1548; lean_object* x_1549; lean_object* x_1550; lean_object* x_1551; lean_object* x_1552; lean_object* x_1553; lean_object* x_1554; lean_object* x_1555; lean_object* x_1556; lean_object* x_1557; lean_object* x_1558; lean_object* x_1559; lean_object* x_1560; lean_object* x_1561; lean_object* x_1562; lean_object* x_1563; uint8_t x_1564; lean_object* x_1565; lean_object* x_1566; lean_object* x_1567; lean_object* x_1568; lean_object* x_1569; lean_object* x_1570; lean_object* x_1571; lean_object* x_1572; lean_object* x_1573; lean_object* x_1574; lean_object* x_1575; lean_object* x_1576; uint16_t x_1577; lean_object* x_1578; lean_object* x_1579; lean_object* x_1580; lean_object* x_1581; lean_object* x_1582; lean_object* x_1583; lean_object* x_1584; lean_object* x_1585; lean_object* x_1586; lean_object* x_1587; lean_object* x_1588; uint8_t x_1589; lean_object* x_1590; lean_object* x_1591; lean_object* x_1592; lean_object* x_1593; lean_object* x_1594; lean_object* x_1595; lean_object* x_1596; uint16_t x_1597; lean_object* x_1598; lean_object* x_1599; lean_object* x_1600; lean_object* x_1601; lean_object* x_1602; lean_object* x_1603; lean_object* x_1604; lean_object* x_1605; lean_object* x_1606; lean_object* x_1607; lean_object* x_1608; lean_object* x_1609; lean_object* x_1610; lean_object* x_1611; lean_object* x_1612; lean_object* x_1613; lean_object* x_1614; lean_object* x_1615; lean_object* x_1616; lean_object* x_1617; lean_object* x_1618; lean_object* x_1619; lean_object* x_1620; lean_object* x_1621; lean_object* x_1622; lean_object* x_1623; lean_object* x_1624; lean_object* x_1625; lean_object* x_1626; lean_object* x_1627; lean_object* x_1628; lean_object* x_1629; lean_object* x_1630; lean_object* x_1631; lean_object* x_1632; lean_object* x_1633; lean_object* x_1634; lean_object* x_1635; lean_object* x_1636; lean_object* x_1637; lean_object* x_1638; lean_object* x_1639; lean_object* x_1640; lean_object* x_1641; lean_object* x_1642; uint16_t x_1643; lean_object* x_1644; lean_object* x_1645; lean_object* x_1646; lean_object* x_1647; lean_object* x_1648; lean_object* x_1649; lean_object* x_1650; lean_object* x_1651; lean_object* x_1652; lean_object* x_1653; uint8_t x_1654; lean_object* x_1655; lean_object* x_1656; lean_object* x_1657; lean_object* x_1658; lean_object* x_1659; lean_object* x_1660; lean_object* x_1661; lean_object* x_1662; lean_object* x_1663; lean_object* x_1664; lean_object* x_1665; lean_object* x_1666; lean_object* x_1667; lean_object* x_1668; lean_object* x_1669; lean_object* x_1670; lean_object* x_1671; lean_object* x_1672; lean_object* x_1673; lean_object* x_1674; lean_object* x_1675; lean_object* x_1676; uint16_t x_1677; lean_object* x_1678; lean_object* x_1679; lean_object* x_1680; lean_object* x_1681; lean_object* x_1682; lean_object* x_1683; lean_object* x_1684; lean_object* x_1685; lean_object* x_1686; lean_object* x_1687; lean_object* x_1688; lean_object* x_1689; lean_object* x_1690; lean_object* x_1691; lean_object* x_1692; lean_object* x_1693; lean_object* x_1694; lean_object* x_1695; lean_object* x_1696; lean_object* x_1697; lean_object* x_1698; lean_object* x_1699; lean_object* x_1700; lean_object* x_1701; lean_object* x_1702; lean_object* x_1703; lean_object* x_1704; lean_object* x_1705; lean_object* x_1706; lean_object* x_1707; lean_object* x_1708; lean_object* x_1709; lean_object* x_1710; lean_object* x_1711; lean_object* x_1712; lean_object* x_1713; lean_object* x_1714; lean_object* x_1715; lean_object* x_1716; lean_object* x_1717; lean_object* x_1718; lean_object* x_1719; lean_object* x_1720; lean_object* x_1721; lean_object* x_1722; lean_object* x_1723; lean_object* x_1724; lean_object* x_1725; lean_object* x_1726; 
x_1403 = lean_ctor_get(x_27, 0);
x_1404 = lean_ctor_get_uint16(x_27, sizeof(void*)*4);
x_1405 = lean_ctor_get(x_27, 1);
x_1406 = lean_ctor_get(x_27, 2);
x_1407 = lean_ctor_get(x_27, 3);
lean_inc(x_1407);
lean_inc(x_1406);
lean_inc(x_1405);
lean_inc(x_1403);
lean_dec(x_27);
x_1408 = lean_array_get_size(x_1403);
x_1409 = lean_nat_sub(x_1408, x_13);
x_1410 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__4));
x_1411 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1411, 0, x_1409);
lean_ctor_set(x_1411, 1, x_1410);
x_1412 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1412, 0, x_1411);
lean_ctor_set(x_1412, 1, x_1407);
x_1413 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_1413, 0, x_1403);
lean_ctor_set(x_1413, 1, x_1405);
lean_ctor_set(x_1413, 2, x_1406);
lean_ctor_set(x_1413, 3, x_1412);
lean_ctor_set_uint16(x_1413, sizeof(void*)*4, x_1404);
x_1414 = 28;
x_1415 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__5));
x_1416 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1413, x_1414, x_1415);
x_1417 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__6));
x_1418 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1416, x_21, x_1417);
x_1419 = lp_sidfinity_MV3_CodeBuilder_label(x_1418, x_1415);
x_1420 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_1421 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1419, x_1420);
x_1422 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1421, x_3);
x_1423 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1422, x_5);
x_1424 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0));
x_1425 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1423, x_1424);
x_1426 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__7, &lp_sidfinity_MV3_emitSustainEffects___closed__7_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__7);
x_1427 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1425, x_1426);
x_1428 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1427, x_1424);
x_1429 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_1430 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1428, x_1429);
x_1431 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_1432 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1430, x_1431);
x_1433 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1432, x_5);
x_1434 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__1, &lp_sidfinity_MV3_emitNL__PortaInit___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__1);
x_1435 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1433, x_1434);
x_1436 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1);
x_1437 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1435, x_1436);
x_1438 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1437, x_21, x_22);
x_1439 = lp_sidfinity_MV3_CodeBuilder_label(x_1438, x_1417);
x_1440 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1));
x_1441 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1439, x_1440);
x_1442 = 29;
x_1443 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1441, x_1442, x_22);
x_1444 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__3, &lp_sidfinity_MV3_emitNL__PortaInit___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__3);
x_1445 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1443, x_1444);
x_1446 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PreserveMask___closed__0, &lp_sidfinity_MV3_emitNL__PreserveMask___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PreserveMask___closed__0);
x_1447 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1445, x_1446);
x_1448 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1447, x_1440);
x_1449 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1448, x_1444);
x_1450 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__8, &lp_sidfinity_MV3_emitSustainEffects___closed__8_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__8);
x_1451 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1449, x_1450);
x_1452 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1451, x_25);
x_1453 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__9));
x_1454 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1452, x_1453);
x_1455 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__10));
x_1456 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1454, x_18, x_1455);
x_1457 = lp_sidfinity_I_clc;
x_1458 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1456, x_1457);
x_1459 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1458, x_1424);
x_1460 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1459, x_1426);
x_1461 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1460, x_1424);
x_1462 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2));
x_1463 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1461, x_1462);
x_1464 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3);
x_1465 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1463, x_1464);
x_1466 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__11, &lp_sidfinity_MV3_emitSustainEffects___closed__11_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__11);
x_1467 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1465, x_1466);
x_1468 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1467, x_1462);
x_1469 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__12));
x_1470 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1468, x_1469);
x_1471 = lean_ctor_get(x_1470, 0);
lean_inc_ref(x_1471);
x_1472 = lean_ctor_get_uint16(x_1470, sizeof(void*)*4);
x_1473 = lean_ctor_get(x_1470, 1);
lean_inc(x_1473);
x_1474 = lean_ctor_get(x_1470, 2);
lean_inc(x_1474);
x_1475 = lean_ctor_get(x_1470, 3);
lean_inc(x_1475);
if (lean_is_exclusive(x_1470)) {
 lean_ctor_release(x_1470, 0);
 lean_ctor_release(x_1470, 1);
 lean_ctor_release(x_1470, 2);
 lean_ctor_release(x_1470, 3);
 x_1476 = x_1470;
} else {
 lean_dec_ref(x_1470);
 x_1476 = lean_box(0);
}
x_1477 = lean_array_get_size(x_1471);
x_1478 = lean_nat_sub(x_1477, x_13);
x_1479 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__13));
x_1480 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1480, 0, x_1478);
lean_ctor_set(x_1480, 1, x_1479);
x_1481 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1481, 0, x_1480);
lean_ctor_set(x_1481, 1, x_1475);
if (lean_is_scalar(x_1476)) {
 x_1482 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1482 = x_1476;
}
lean_ctor_set(x_1482, 0, x_1471);
lean_ctor_set(x_1482, 1, x_1473);
lean_ctor_set(x_1482, 2, x_1474);
lean_ctor_set(x_1482, 3, x_1481);
lean_ctor_set_uint16(x_1482, sizeof(void*)*4, x_1472);
x_1483 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__14));
x_1484 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1482, x_18, x_1483);
x_1485 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__15, &lp_sidfinity_MV3_emitSustainEffects___closed__15_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__15);
x_1486 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1484, x_1485);
x_1487 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1486, x_1453);
x_1488 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1487, x_21, x_1483);
x_1489 = lp_sidfinity_MV3_CodeBuilder_label(x_1488, x_1455);
x_1490 = lp_sidfinity_I_sec;
x_1491 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1489, x_1490);
x_1492 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1491, x_1424);
x_1493 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__16, &lp_sidfinity_MV3_emitSustainEffects___closed__16_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__16);
x_1494 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1492, x_1493);
x_1495 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1494, x_1424);
x_1496 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1495, x_1462);
x_1497 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__17, &lp_sidfinity_MV3_emitSustainEffects___closed__17_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__17);
x_1498 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1496, x_1497);
x_1499 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1498, x_1466);
x_1500 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1499, x_1462);
x_1501 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1500, x_1469);
x_1502 = lean_ctor_get(x_1501, 0);
lean_inc_ref(x_1502);
x_1503 = lean_ctor_get_uint16(x_1501, sizeof(void*)*4);
x_1504 = lean_ctor_get(x_1501, 1);
lean_inc(x_1504);
x_1505 = lean_ctor_get(x_1501, 2);
lean_inc(x_1505);
x_1506 = lean_ctor_get(x_1501, 3);
lean_inc(x_1506);
if (lean_is_exclusive(x_1501)) {
 lean_ctor_release(x_1501, 0);
 lean_ctor_release(x_1501, 1);
 lean_ctor_release(x_1501, 2);
 lean_ctor_release(x_1501, 3);
 x_1507 = x_1501;
} else {
 lean_dec_ref(x_1501);
 x_1507 = lean_box(0);
}
x_1508 = lean_array_get_size(x_1502);
x_1509 = lean_nat_sub(x_1508, x_13);
x_1510 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__18));
x_1511 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1511, 0, x_1509);
lean_ctor_set(x_1511, 1, x_1510);
x_1512 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1512, 0, x_1511);
lean_ctor_set(x_1512, 1, x_1506);
if (lean_is_scalar(x_1507)) {
 x_1513 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1513 = x_1507;
}
lean_ctor_set(x_1513, 0, x_1502);
lean_ctor_set(x_1513, 1, x_1504);
lean_ctor_set(x_1513, 2, x_1505);
lean_ctor_set(x_1513, 3, x_1512);
lean_ctor_set_uint16(x_1513, sizeof(void*)*4, x_1503);
x_1514 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1513, x_18, x_1483);
x_1515 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_1516 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1514, x_1515);
x_1517 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1516, x_1453);
x_1518 = lp_sidfinity_MV3_CodeBuilder_label(x_1517, x_1483);
x_1519 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1518, x_1424);
x_1520 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1519, x_1429);
x_1521 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1520, x_1462);
x_1522 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_1523 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1521, x_1522);
x_1524 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1523, x_1431);
x_1525 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1524, x_5);
x_1526 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1525, x_1434);
x_1527 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1526, x_1436);
x_1528 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3);
x_1529 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1527, x_1528);
x_1530 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3);
x_1531 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1529, x_1530);
x_1532 = lp_sidfinity_MV3_CodeBuilder_label(x_1531, x_22);
x_1533 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1532, x_1420);
x_1534 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1533, x_3);
x_1535 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1534, x_5);
x_1536 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1535, x_7);
x_1537 = lean_ctor_get(x_1536, 0);
lean_inc_ref(x_1537);
x_1538 = lean_ctor_get_uint16(x_1536, sizeof(void*)*4);
x_1539 = lean_ctor_get(x_1536, 1);
lean_inc(x_1539);
x_1540 = lean_ctor_get(x_1536, 2);
lean_inc(x_1540);
x_1541 = lean_ctor_get(x_1536, 3);
lean_inc(x_1541);
if (lean_is_exclusive(x_1536)) {
 lean_ctor_release(x_1536, 0);
 lean_ctor_release(x_1536, 1);
 lean_ctor_release(x_1536, 2);
 lean_ctor_release(x_1536, 3);
 x_1542 = x_1536;
} else {
 lean_dec_ref(x_1536);
 x_1542 = lean_box(0);
}
x_1543 = lean_array_get_size(x_1537);
x_1544 = lean_nat_sub(x_1543, x_13);
x_1545 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_1546 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1546, 0, x_1544);
lean_ctor_set(x_1546, 1, x_1545);
x_1547 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1547, 0, x_1546);
lean_ctor_set(x_1547, 1, x_1541);
if (lean_is_scalar(x_1542)) {
 x_1548 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1548 = x_1542;
}
lean_ctor_set(x_1548, 0, x_1537);
lean_ctor_set(x_1548, 1, x_1539);
lean_ctor_set(x_1548, 2, x_1540);
lean_ctor_set(x_1548, 3, x_1547);
lean_ctor_set_uint16(x_1548, sizeof(void*)*4, x_1538);
x_1549 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__20));
x_1550 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1548, x_18, x_1549);
x_1551 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__21));
x_1552 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1550, x_21, x_1551);
x_1553 = lp_sidfinity_MV3_CodeBuilder_label(x_1552, x_1549);
x_1554 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_1555 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1553, x_1554);
x_1556 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__22));
x_1557 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1555, x_18, x_1556);
x_1558 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1557, x_21, x_1551);
x_1559 = lp_sidfinity_MV3_CodeBuilder_label(x_1558, x_1556);
x_1560 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_1561 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1559, x_1560);
x_1562 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__23, &lp_sidfinity_MV3_emitSustainEffects___closed__23_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__23);
x_1563 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1561, x_1562);
x_1564 = 25;
x_1565 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__24));
x_1566 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1563, x_1564, x_1565);
x_1567 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1566, x_21, x_1551);
x_1568 = lp_sidfinity_MV3_CodeBuilder_label(x_1567, x_1565);
x_1569 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1568, x_1490);
x_1570 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_1571 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1569, x_1570);
x_1572 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__25, &lp_sidfinity_MV3_emitSustainEffects___closed__25_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__25);
x_1573 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1571, x_1572);
x_1574 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__27));
x_1575 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1573, x_1574);
x_1576 = lean_ctor_get(x_1575, 0);
lean_inc_ref(x_1576);
x_1577 = lean_ctor_get_uint16(x_1575, sizeof(void*)*4);
x_1578 = lean_ctor_get(x_1575, 1);
lean_inc(x_1578);
x_1579 = lean_ctor_get(x_1575, 2);
lean_inc(x_1579);
x_1580 = lean_ctor_get(x_1575, 3);
lean_inc(x_1580);
if (lean_is_exclusive(x_1575)) {
 lean_ctor_release(x_1575, 0);
 lean_ctor_release(x_1575, 1);
 lean_ctor_release(x_1575, 2);
 lean_ctor_release(x_1575, 3);
 x_1581 = x_1575;
} else {
 lean_dec_ref(x_1575);
 x_1581 = lean_box(0);
}
x_1582 = lean_array_get_size(x_1576);
x_1583 = lean_nat_sub(x_1582, x_13);
x_1584 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1584, 0, x_1583);
lean_ctor_set(x_1584, 1, x_1560);
x_1585 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1585, 0, x_1584);
lean_ctor_set(x_1585, 1, x_1580);
if (lean_is_scalar(x_1581)) {
 x_1586 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1586 = x_1581;
}
lean_ctor_set(x_1586, 0, x_1576);
lean_ctor_set(x_1586, 1, x_1578);
lean_ctor_set(x_1586, 2, x_1579);
lean_ctor_set(x_1586, 3, x_1585);
lean_ctor_set_uint16(x_1586, sizeof(void*)*4, x_1577);
x_1587 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1586, x_1431);
x_1588 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1587, x_5);
x_1589 = 24;
x_1590 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__28));
x_1591 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1588, x_1589, x_1590);
x_1592 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1591, x_1420);
x_1593 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1592, x_3);
x_1594 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1593, x_5);
x_1595 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1594, x_7);
x_1596 = lean_ctor_get(x_1595, 0);
lean_inc_ref(x_1596);
x_1597 = lean_ctor_get_uint16(x_1595, sizeof(void*)*4);
x_1598 = lean_ctor_get(x_1595, 1);
lean_inc(x_1598);
x_1599 = lean_ctor_get(x_1595, 2);
lean_inc(x_1599);
x_1600 = lean_ctor_get(x_1595, 3);
lean_inc(x_1600);
if (lean_is_exclusive(x_1595)) {
 lean_ctor_release(x_1595, 0);
 lean_ctor_release(x_1595, 1);
 lean_ctor_release(x_1595, 2);
 lean_ctor_release(x_1595, 3);
 x_1601 = x_1595;
} else {
 lean_dec_ref(x_1595);
 x_1601 = lean_box(0);
}
x_1602 = lean_array_get_size(x_1596);
x_1603 = lean_nat_sub(x_1602, x_13);
x_1604 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_1605 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1605, 0, x_1603);
lean_ctor_set(x_1605, 1, x_1604);
x_1606 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1606, 0, x_1605);
lean_ctor_set(x_1606, 1, x_1600);
if (lean_is_scalar(x_1601)) {
 x_1607 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1607 = x_1601;
}
lean_ctor_set(x_1607, 0, x_1596);
lean_ctor_set(x_1607, 1, x_1598);
lean_ctor_set(x_1607, 2, x_1599);
lean_ctor_set(x_1607, 3, x_1606);
lean_ctor_set_uint16(x_1607, sizeof(void*)*4, x_1597);
x_1608 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_1609 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1607, x_1608);
x_1610 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1609, x_1554);
x_1611 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1610, x_1429);
x_1612 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1611, x_1554);
x_1613 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1612, x_1431);
x_1614 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1613, x_5);
x_1615 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1614, x_1434);
x_1616 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_1617 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1615, x_1616);
x_1618 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_1619 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1617, x_1618);
x_1620 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_1621 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1619, x_1620);
x_1622 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_1623 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1621, x_1622);
x_1624 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_1625 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1623, x_21, x_1624);
x_1626 = lp_sidfinity_MV3_CodeBuilder_label(x_1625, x_1590);
x_1627 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1626, x_1420);
x_1628 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1627, x_1554);
x_1629 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1628, x_1431);
x_1630 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1629, x_5);
x_1631 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1630, x_1554);
x_1632 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1631, x_1616);
x_1633 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_1634 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1632, x_1633);
x_1635 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1634, x_1622);
x_1636 = lp_sidfinity_MV3_CodeBuilder_label(x_1635, x_1624);
x_1637 = lp_sidfinity_MV3_CodeBuilder_label(x_1636, x_1551);
x_1638 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1637, x_1420);
x_1639 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1638, x_3);
x_1640 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1639, x_5);
x_1641 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1640, x_7);
x_1642 = lean_ctor_get(x_1641, 0);
lean_inc_ref(x_1642);
x_1643 = lean_ctor_get_uint16(x_1641, sizeof(void*)*4);
x_1644 = lean_ctor_get(x_1641, 1);
lean_inc(x_1644);
x_1645 = lean_ctor_get(x_1641, 2);
lean_inc(x_1645);
x_1646 = lean_ctor_get(x_1641, 3);
lean_inc(x_1646);
if (lean_is_exclusive(x_1641)) {
 lean_ctor_release(x_1641, 0);
 lean_ctor_release(x_1641, 1);
 lean_ctor_release(x_1641, 2);
 lean_ctor_release(x_1641, 3);
 x_1647 = x_1641;
} else {
 lean_dec_ref(x_1641);
 x_1647 = lean_box(0);
}
x_1648 = lean_array_get_size(x_1642);
x_1649 = lean_nat_sub(x_1648, x_13);
x_1650 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_1651 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1651, 0, x_1649);
lean_ctor_set(x_1651, 1, x_1650);
x_1652 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1652, 0, x_1651);
lean_ctor_set(x_1652, 1, x_1646);
if (lean_is_scalar(x_1647)) {
 x_1653 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1653 = x_1647;
}
lean_ctor_set(x_1653, 0, x_1642);
lean_ctor_set(x_1653, 1, x_1644);
lean_ctor_set(x_1653, 2, x_1645);
lean_ctor_set(x_1653, 3, x_1652);
lean_ctor_set_uint16(x_1653, sizeof(void*)*4, x_1643);
x_1654 = 26;
x_1655 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_1656 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1653, x_1654, x_1655);
x_1657 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_1658 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1656, x_1657);
x_1659 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_1660 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1658, x_1659);
x_1661 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1660, x_1654, x_1655);
x_1662 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1661, x_1420);
x_1663 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1662, x_1554);
x_1664 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1663, x_1654, x_1655);
x_1665 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1664, x_1429);
x_1666 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1665, x_1554);
x_1667 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1666, x_1431);
x_1668 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1667, x_5);
x_1669 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1668, x_1434);
x_1670 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1669, x_1616);
x_1671 = lp_sidfinity_MV3_CodeBuilder_label(x_1670, x_1655);
x_1672 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1671, x_1420);
x_1673 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1672, x_3);
x_1674 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1673, x_5);
x_1675 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1674, x_7);
x_1676 = lean_ctor_get(x_1675, 0);
lean_inc_ref(x_1676);
x_1677 = lean_ctor_get_uint16(x_1675, sizeof(void*)*4);
x_1678 = lean_ctor_get(x_1675, 1);
lean_inc(x_1678);
x_1679 = lean_ctor_get(x_1675, 2);
lean_inc(x_1679);
x_1680 = lean_ctor_get(x_1675, 3);
lean_inc(x_1680);
if (lean_is_exclusive(x_1675)) {
 lean_ctor_release(x_1675, 0);
 lean_ctor_release(x_1675, 1);
 lean_ctor_release(x_1675, 2);
 lean_ctor_release(x_1675, 3);
 x_1681 = x_1675;
} else {
 lean_dec_ref(x_1675);
 x_1681 = lean_box(0);
}
x_1682 = lean_array_get_size(x_1676);
x_1683 = lean_nat_sub(x_1682, x_13);
x_1684 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_1685 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1685, 0, x_1683);
lean_ctor_set(x_1685, 1, x_1684);
x_1686 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1686, 0, x_1685);
lean_ctor_set(x_1686, 1, x_1680);
if (lean_is_scalar(x_1681)) {
 x_1687 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1687 = x_1681;
}
lean_ctor_set(x_1687, 0, x_1676);
lean_ctor_set(x_1687, 1, x_1678);
lean_ctor_set(x_1687, 2, x_1679);
lean_ctor_set(x_1687, 3, x_1686);
lean_ctor_set_uint16(x_1687, sizeof(void*)*4, x_1677);
x_1688 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_1689 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1687, x_18, x_1688);
x_1690 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_1691 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1689, x_21, x_1690);
x_1692 = lp_sidfinity_MV3_CodeBuilder_label(x_1691, x_1688);
x_1693 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1692, x_1429);
x_1694 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1693, x_1657);
x_1695 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1694, x_1659);
x_1696 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_1697 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1695, x_1654, x_1696);
x_1698 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1697, x_1457);
x_1699 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_1700 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1698, x_1699);
x_1701 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_1702 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1700, x_1701);
x_1703 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_1704 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1702, x_21, x_1703);
x_1705 = lp_sidfinity_MV3_CodeBuilder_label(x_1704, x_1696);
x_1706 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1705, x_1699);
x_1707 = lp_sidfinity_MV3_CodeBuilder_label(x_1706, x_1703);
x_1708 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1707, x_5);
x_1709 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_1710 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1708, x_1709);
x_1711 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1710, x_25);
x_1712 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_1713 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1711, x_1712);
x_1714 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1713, x_1429);
x_1715 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1714, x_1420);
x_1716 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1715, x_1431);
x_1717 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1716, x_5);
x_1718 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1717, x_1444);
x_1719 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1718, x_1616);
x_1720 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1719, x_1434);
x_1721 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_1722 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1720, x_1721);
x_1723 = lp_sidfinity_MV3_CodeBuilder_label(x_1722, x_1690);
x_1724 = lp_sidfinity_I_rts;
x_1725 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1723, x_1724);
x_1726 = lp_sidfinity_MV3_emitNoteLoadPath(x_1725, x_2);
return x_1726;
}
}
else
{
lean_object* x_1727; uint16_t x_1728; lean_object* x_1729; lean_object* x_1730; lean_object* x_1731; lean_object* x_1732; lean_object* x_1733; lean_object* x_1734; lean_object* x_1735; lean_object* x_1736; lean_object* x_1737; lean_object* x_1738; uint8_t x_1739; lean_object* x_1740; lean_object* x_1741; uint8_t x_1742; lean_object* x_1743; lean_object* x_1744; lean_object* x_1745; lean_object* x_1746; lean_object* x_1747; lean_object* x_1748; lean_object* x_1749; uint16_t x_1750; lean_object* x_1751; lean_object* x_1752; lean_object* x_1753; lean_object* x_1754; lean_object* x_1755; lean_object* x_1756; lean_object* x_1757; lean_object* x_1758; lean_object* x_1759; lean_object* x_1760; uint8_t x_1761; lean_object* x_1762; lean_object* x_1763; lean_object* x_1764; lean_object* x_1765; lean_object* x_1766; lean_object* x_1767; lean_object* x_1768; lean_object* x_1769; lean_object* x_1770; lean_object* x_1771; lean_object* x_1772; lean_object* x_1773; lean_object* x_1774; lean_object* x_1775; lean_object* x_1776; lean_object* x_1777; lean_object* x_1778; lean_object* x_1779; lean_object* x_1780; lean_object* x_1781; lean_object* x_1782; lean_object* x_1783; lean_object* x_1784; lean_object* x_1785; lean_object* x_1786; lean_object* x_1787; lean_object* x_1788; uint8_t x_1789; lean_object* x_1790; lean_object* x_1791; lean_object* x_1792; lean_object* x_1793; lean_object* x_1794; lean_object* x_1795; lean_object* x_1796; lean_object* x_1797; lean_object* x_1798; lean_object* x_1799; lean_object* x_1800; lean_object* x_1801; lean_object* x_1802; lean_object* x_1803; lean_object* x_1804; lean_object* x_1805; lean_object* x_1806; lean_object* x_1807; lean_object* x_1808; lean_object* x_1809; lean_object* x_1810; lean_object* x_1811; lean_object* x_1812; lean_object* x_1813; lean_object* x_1814; lean_object* x_1815; lean_object* x_1816; lean_object* x_1817; lean_object* x_1818; uint16_t x_1819; lean_object* x_1820; lean_object* x_1821; lean_object* x_1822; lean_object* x_1823; lean_object* x_1824; lean_object* x_1825; lean_object* x_1826; lean_object* x_1827; lean_object* x_1828; lean_object* x_1829; lean_object* x_1830; lean_object* x_1831; lean_object* x_1832; lean_object* x_1833; lean_object* x_1834; lean_object* x_1835; lean_object* x_1836; lean_object* x_1837; lean_object* x_1838; lean_object* x_1839; lean_object* x_1840; lean_object* x_1841; lean_object* x_1842; lean_object* x_1843; lean_object* x_1844; lean_object* x_1845; lean_object* x_1846; lean_object* x_1847; lean_object* x_1848; lean_object* x_1849; uint16_t x_1850; lean_object* x_1851; lean_object* x_1852; lean_object* x_1853; lean_object* x_1854; lean_object* x_1855; lean_object* x_1856; lean_object* x_1857; lean_object* x_1858; lean_object* x_1859; lean_object* x_1860; lean_object* x_1861; lean_object* x_1862; lean_object* x_1863; lean_object* x_1864; lean_object* x_1865; lean_object* x_1866; lean_object* x_1867; lean_object* x_1868; lean_object* x_1869; lean_object* x_1870; lean_object* x_1871; lean_object* x_1872; lean_object* x_1873; lean_object* x_1874; lean_object* x_1875; lean_object* x_1876; lean_object* x_1877; lean_object* x_1878; lean_object* x_1879; lean_object* x_1880; lean_object* x_1881; lean_object* x_1882; lean_object* x_1883; lean_object* x_1884; uint16_t x_1885; lean_object* x_1886; lean_object* x_1887; lean_object* x_1888; lean_object* x_1889; lean_object* x_1890; lean_object* x_1891; lean_object* x_1892; lean_object* x_1893; lean_object* x_1894; lean_object* x_1895; lean_object* x_1896; lean_object* x_1897; lean_object* x_1898; lean_object* x_1899; lean_object* x_1900; lean_object* x_1901; lean_object* x_1902; lean_object* x_1903; lean_object* x_1904; lean_object* x_1905; lean_object* x_1906; lean_object* x_1907; lean_object* x_1908; lean_object* x_1909; lean_object* x_1910; uint8_t x_1911; lean_object* x_1912; lean_object* x_1913; lean_object* x_1914; lean_object* x_1915; lean_object* x_1916; lean_object* x_1917; lean_object* x_1918; lean_object* x_1919; lean_object* x_1920; lean_object* x_1921; lean_object* x_1922; lean_object* x_1923; uint16_t x_1924; lean_object* x_1925; lean_object* x_1926; lean_object* x_1927; lean_object* x_1928; lean_object* x_1929; lean_object* x_1930; lean_object* x_1931; lean_object* x_1932; lean_object* x_1933; lean_object* x_1934; lean_object* x_1935; uint8_t x_1936; lean_object* x_1937; lean_object* x_1938; lean_object* x_1939; lean_object* x_1940; lean_object* x_1941; lean_object* x_1942; lean_object* x_1943; uint16_t x_1944; lean_object* x_1945; lean_object* x_1946; lean_object* x_1947; lean_object* x_1948; lean_object* x_1949; lean_object* x_1950; lean_object* x_1951; lean_object* x_1952; lean_object* x_1953; lean_object* x_1954; lean_object* x_1955; lean_object* x_1956; lean_object* x_1957; lean_object* x_1958; lean_object* x_1959; lean_object* x_1960; lean_object* x_1961; lean_object* x_1962; lean_object* x_1963; lean_object* x_1964; lean_object* x_1965; lean_object* x_1966; lean_object* x_1967; lean_object* x_1968; lean_object* x_1969; lean_object* x_1970; lean_object* x_1971; lean_object* x_1972; lean_object* x_1973; lean_object* x_1974; lean_object* x_1975; lean_object* x_1976; lean_object* x_1977; lean_object* x_1978; lean_object* x_1979; lean_object* x_1980; lean_object* x_1981; lean_object* x_1982; lean_object* x_1983; lean_object* x_1984; lean_object* x_1985; lean_object* x_1986; lean_object* x_1987; lean_object* x_1988; lean_object* x_1989; uint16_t x_1990; lean_object* x_1991; lean_object* x_1992; lean_object* x_1993; lean_object* x_1994; lean_object* x_1995; lean_object* x_1996; lean_object* x_1997; lean_object* x_1998; lean_object* x_1999; lean_object* x_2000; uint8_t x_2001; lean_object* x_2002; lean_object* x_2003; lean_object* x_2004; lean_object* x_2005; lean_object* x_2006; lean_object* x_2007; lean_object* x_2008; lean_object* x_2009; lean_object* x_2010; lean_object* x_2011; lean_object* x_2012; lean_object* x_2013; lean_object* x_2014; lean_object* x_2015; lean_object* x_2016; lean_object* x_2017; lean_object* x_2018; lean_object* x_2019; lean_object* x_2020; lean_object* x_2021; lean_object* x_2022; lean_object* x_2023; uint16_t x_2024; lean_object* x_2025; lean_object* x_2026; lean_object* x_2027; lean_object* x_2028; lean_object* x_2029; lean_object* x_2030; lean_object* x_2031; lean_object* x_2032; lean_object* x_2033; lean_object* x_2034; lean_object* x_2035; lean_object* x_2036; lean_object* x_2037; lean_object* x_2038; lean_object* x_2039; lean_object* x_2040; lean_object* x_2041; lean_object* x_2042; lean_object* x_2043; lean_object* x_2044; lean_object* x_2045; lean_object* x_2046; lean_object* x_2047; lean_object* x_2048; lean_object* x_2049; lean_object* x_2050; lean_object* x_2051; lean_object* x_2052; lean_object* x_2053; lean_object* x_2054; lean_object* x_2055; lean_object* x_2056; lean_object* x_2057; lean_object* x_2058; lean_object* x_2059; lean_object* x_2060; lean_object* x_2061; lean_object* x_2062; lean_object* x_2063; lean_object* x_2064; lean_object* x_2065; lean_object* x_2066; lean_object* x_2067; lean_object* x_2068; lean_object* x_2069; lean_object* x_2070; lean_object* x_2071; lean_object* x_2072; lean_object* x_2073; 
x_1727 = lean_ctor_get(x_8, 0);
x_1728 = lean_ctor_get_uint16(x_8, sizeof(void*)*4);
x_1729 = lean_ctor_get(x_8, 1);
x_1730 = lean_ctor_get(x_8, 2);
x_1731 = lean_ctor_get(x_8, 3);
lean_inc(x_1731);
lean_inc(x_1730);
lean_inc(x_1729);
lean_inc(x_1727);
lean_dec(x_8);
x_1732 = lean_array_get_size(x_1727);
x_1733 = lean_unsigned_to_nat(2u);
x_1734 = lean_nat_sub(x_1732, x_1733);
x_1735 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0));
x_1736 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1736, 0, x_1734);
lean_ctor_set(x_1736, 1, x_1735);
x_1737 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1737, 0, x_1736);
lean_ctor_set(x_1737, 1, x_1731);
x_1738 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_1738, 0, x_1727);
lean_ctor_set(x_1738, 1, x_1729);
lean_ctor_set(x_1738, 2, x_1730);
lean_ctor_set(x_1738, 3, x_1737);
lean_ctor_set_uint16(x_1738, sizeof(void*)*4, x_1728);
x_1739 = 27;
x_1740 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__2));
x_1741 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1738, x_1739, x_1740);
x_1742 = 32;
x_1743 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__3));
x_1744 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1741, x_1742, x_1743);
x_1745 = lp_sidfinity_MV3_CodeBuilder_label(x_1744, x_1740);
x_1746 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__0, &lp_sidfinity_MV3_emitNL__PortaInit___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__0);
x_1747 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1745, x_1746);
x_1748 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1747, x_7);
x_1749 = lean_ctor_get(x_1748, 0);
lean_inc_ref(x_1749);
x_1750 = lean_ctor_get_uint16(x_1748, sizeof(void*)*4);
x_1751 = lean_ctor_get(x_1748, 1);
lean_inc(x_1751);
x_1752 = lean_ctor_get(x_1748, 2);
lean_inc(x_1752);
x_1753 = lean_ctor_get(x_1748, 3);
lean_inc(x_1753);
if (lean_is_exclusive(x_1748)) {
 lean_ctor_release(x_1748, 0);
 lean_ctor_release(x_1748, 1);
 lean_ctor_release(x_1748, 2);
 lean_ctor_release(x_1748, 3);
 x_1754 = x_1748;
} else {
 lean_dec_ref(x_1748);
 x_1754 = lean_box(0);
}
x_1755 = lean_array_get_size(x_1749);
x_1756 = lean_nat_sub(x_1755, x_1733);
x_1757 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__4));
x_1758 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1758, 0, x_1756);
lean_ctor_set(x_1758, 1, x_1757);
x_1759 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1759, 0, x_1758);
lean_ctor_set(x_1759, 1, x_1753);
if (lean_is_scalar(x_1754)) {
 x_1760 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1760 = x_1754;
}
lean_ctor_set(x_1760, 0, x_1749);
lean_ctor_set(x_1760, 1, x_1751);
lean_ctor_set(x_1760, 2, x_1752);
lean_ctor_set(x_1760, 3, x_1759);
lean_ctor_set_uint16(x_1760, sizeof(void*)*4, x_1750);
x_1761 = 28;
x_1762 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__5));
x_1763 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1760, x_1761, x_1762);
x_1764 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__6));
x_1765 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1763, x_1742, x_1764);
x_1766 = lp_sidfinity_MV3_CodeBuilder_label(x_1765, x_1762);
x_1767 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_1768 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1766, x_1767);
x_1769 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1768, x_3);
x_1770 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1769, x_5);
x_1771 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0));
x_1772 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1770, x_1771);
x_1773 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__7, &lp_sidfinity_MV3_emitSustainEffects___closed__7_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__7);
x_1774 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1772, x_1773);
x_1775 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1774, x_1771);
x_1776 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_1777 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1775, x_1776);
x_1778 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_1779 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1777, x_1778);
x_1780 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1779, x_5);
x_1781 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__1, &lp_sidfinity_MV3_emitNL__PortaInit___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__1);
x_1782 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1780, x_1781);
x_1783 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__1);
x_1784 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1782, x_1783);
x_1785 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1784, x_1742, x_1743);
x_1786 = lp_sidfinity_MV3_CodeBuilder_label(x_1785, x_1764);
x_1787 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1));
x_1788 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1786, x_1787);
x_1789 = 29;
x_1790 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1788, x_1789, x_1743);
x_1791 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__3, &lp_sidfinity_MV3_emitNL__PortaInit___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__3);
x_1792 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1790, x_1791);
x_1793 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PreserveMask___closed__0, &lp_sidfinity_MV3_emitNL__PreserveMask___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PreserveMask___closed__0);
x_1794 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1792, x_1793);
x_1795 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1794, x_1787);
x_1796 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1795, x_1791);
x_1797 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__8, &lp_sidfinity_MV3_emitSustainEffects___closed__8_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__8);
x_1798 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1796, x_1797);
x_1799 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1798, x_1746);
x_1800 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__9));
x_1801 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1799, x_1800);
x_1802 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__10));
x_1803 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1801, x_1739, x_1802);
x_1804 = lp_sidfinity_I_clc;
x_1805 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1803, x_1804);
x_1806 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1805, x_1771);
x_1807 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1806, x_1773);
x_1808 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1807, x_1771);
x_1809 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2));
x_1810 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1808, x_1809);
x_1811 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3);
x_1812 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1810, x_1811);
x_1813 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__11, &lp_sidfinity_MV3_emitSustainEffects___closed__11_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__11);
x_1814 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1812, x_1813);
x_1815 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1814, x_1809);
x_1816 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__12));
x_1817 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1815, x_1816);
x_1818 = lean_ctor_get(x_1817, 0);
lean_inc_ref(x_1818);
x_1819 = lean_ctor_get_uint16(x_1817, sizeof(void*)*4);
x_1820 = lean_ctor_get(x_1817, 1);
lean_inc(x_1820);
x_1821 = lean_ctor_get(x_1817, 2);
lean_inc(x_1821);
x_1822 = lean_ctor_get(x_1817, 3);
lean_inc(x_1822);
if (lean_is_exclusive(x_1817)) {
 lean_ctor_release(x_1817, 0);
 lean_ctor_release(x_1817, 1);
 lean_ctor_release(x_1817, 2);
 lean_ctor_release(x_1817, 3);
 x_1823 = x_1817;
} else {
 lean_dec_ref(x_1817);
 x_1823 = lean_box(0);
}
x_1824 = lean_array_get_size(x_1818);
x_1825 = lean_nat_sub(x_1824, x_1733);
x_1826 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__13));
x_1827 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1827, 0, x_1825);
lean_ctor_set(x_1827, 1, x_1826);
x_1828 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1828, 0, x_1827);
lean_ctor_set(x_1828, 1, x_1822);
if (lean_is_scalar(x_1823)) {
 x_1829 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1829 = x_1823;
}
lean_ctor_set(x_1829, 0, x_1818);
lean_ctor_set(x_1829, 1, x_1820);
lean_ctor_set(x_1829, 2, x_1821);
lean_ctor_set(x_1829, 3, x_1828);
lean_ctor_set_uint16(x_1829, sizeof(void*)*4, x_1819);
x_1830 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__14));
x_1831 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1829, x_1739, x_1830);
x_1832 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__15, &lp_sidfinity_MV3_emitSustainEffects___closed__15_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__15);
x_1833 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1831, x_1832);
x_1834 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1833, x_1800);
x_1835 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1834, x_1742, x_1830);
x_1836 = lp_sidfinity_MV3_CodeBuilder_label(x_1835, x_1802);
x_1837 = lp_sidfinity_I_sec;
x_1838 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1836, x_1837);
x_1839 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1838, x_1771);
x_1840 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__16, &lp_sidfinity_MV3_emitSustainEffects___closed__16_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__16);
x_1841 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1839, x_1840);
x_1842 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1841, x_1771);
x_1843 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1842, x_1809);
x_1844 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__17, &lp_sidfinity_MV3_emitSustainEffects___closed__17_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__17);
x_1845 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1843, x_1844);
x_1846 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1845, x_1813);
x_1847 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsY(x_1846, x_1809);
x_1848 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1847, x_1816);
x_1849 = lean_ctor_get(x_1848, 0);
lean_inc_ref(x_1849);
x_1850 = lean_ctor_get_uint16(x_1848, sizeof(void*)*4);
x_1851 = lean_ctor_get(x_1848, 1);
lean_inc(x_1851);
x_1852 = lean_ctor_get(x_1848, 2);
lean_inc(x_1852);
x_1853 = lean_ctor_get(x_1848, 3);
lean_inc(x_1853);
if (lean_is_exclusive(x_1848)) {
 lean_ctor_release(x_1848, 0);
 lean_ctor_release(x_1848, 1);
 lean_ctor_release(x_1848, 2);
 lean_ctor_release(x_1848, 3);
 x_1854 = x_1848;
} else {
 lean_dec_ref(x_1848);
 x_1854 = lean_box(0);
}
x_1855 = lean_array_get_size(x_1849);
x_1856 = lean_nat_sub(x_1855, x_1733);
x_1857 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__18));
x_1858 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1858, 0, x_1856);
lean_ctor_set(x_1858, 1, x_1857);
x_1859 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1859, 0, x_1858);
lean_ctor_set(x_1859, 1, x_1853);
if (lean_is_scalar(x_1854)) {
 x_1860 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1860 = x_1854;
}
lean_ctor_set(x_1860, 0, x_1849);
lean_ctor_set(x_1860, 1, x_1851);
lean_ctor_set(x_1860, 2, x_1852);
lean_ctor_set(x_1860, 3, x_1859);
lean_ctor_set_uint16(x_1860, sizeof(void*)*4, x_1850);
x_1861 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1860, x_1739, x_1830);
x_1862 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_1863 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1861, x_1862);
x_1864 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_1863, x_1800);
x_1865 = lp_sidfinity_MV3_CodeBuilder_label(x_1864, x_1830);
x_1866 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1865, x_1771);
x_1867 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1866, x_1776);
x_1868 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_1867, x_1809);
x_1869 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_1870 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1868, x_1869);
x_1871 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1870, x_1778);
x_1872 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1871, x_5);
x_1873 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1872, x_1781);
x_1874 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1873, x_1783);
x_1875 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__3);
x_1876 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1874, x_1875);
x_1877 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__3);
x_1878 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1876, x_1877);
x_1879 = lp_sidfinity_MV3_CodeBuilder_label(x_1878, x_1743);
x_1880 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1879, x_1767);
x_1881 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1880, x_3);
x_1882 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1881, x_5);
x_1883 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1882, x_7);
x_1884 = lean_ctor_get(x_1883, 0);
lean_inc_ref(x_1884);
x_1885 = lean_ctor_get_uint16(x_1883, sizeof(void*)*4);
x_1886 = lean_ctor_get(x_1883, 1);
lean_inc(x_1886);
x_1887 = lean_ctor_get(x_1883, 2);
lean_inc(x_1887);
x_1888 = lean_ctor_get(x_1883, 3);
lean_inc(x_1888);
if (lean_is_exclusive(x_1883)) {
 lean_ctor_release(x_1883, 0);
 lean_ctor_release(x_1883, 1);
 lean_ctor_release(x_1883, 2);
 lean_ctor_release(x_1883, 3);
 x_1889 = x_1883;
} else {
 lean_dec_ref(x_1883);
 x_1889 = lean_box(0);
}
x_1890 = lean_array_get_size(x_1884);
x_1891 = lean_nat_sub(x_1890, x_1733);
x_1892 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_1893 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1893, 0, x_1891);
lean_ctor_set(x_1893, 1, x_1892);
x_1894 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1894, 0, x_1893);
lean_ctor_set(x_1894, 1, x_1888);
if (lean_is_scalar(x_1889)) {
 x_1895 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1895 = x_1889;
}
lean_ctor_set(x_1895, 0, x_1884);
lean_ctor_set(x_1895, 1, x_1886);
lean_ctor_set(x_1895, 2, x_1887);
lean_ctor_set(x_1895, 3, x_1894);
lean_ctor_set_uint16(x_1895, sizeof(void*)*4, x_1885);
x_1896 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__20));
x_1897 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1895, x_1739, x_1896);
x_1898 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__21));
x_1899 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1897, x_1742, x_1898);
x_1900 = lp_sidfinity_MV3_CodeBuilder_label(x_1899, x_1896);
x_1901 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_1902 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1900, x_1901);
x_1903 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__22));
x_1904 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1902, x_1739, x_1903);
x_1905 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1904, x_1742, x_1898);
x_1906 = lp_sidfinity_MV3_CodeBuilder_label(x_1905, x_1903);
x_1907 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_1908 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1906, x_1907);
x_1909 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__23, &lp_sidfinity_MV3_emitSustainEffects___closed__23_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__23);
x_1910 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1908, x_1909);
x_1911 = 25;
x_1912 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__24));
x_1913 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1910, x_1911, x_1912);
x_1914 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1913, x_1742, x_1898);
x_1915 = lp_sidfinity_MV3_CodeBuilder_label(x_1914, x_1912);
x_1916 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1915, x_1837);
x_1917 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_1918 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1916, x_1917);
x_1919 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__25, &lp_sidfinity_MV3_emitSustainEffects___closed__25_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__25);
x_1920 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1918, x_1919);
x_1921 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__27));
x_1922 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1920, x_1921);
x_1923 = lean_ctor_get(x_1922, 0);
lean_inc_ref(x_1923);
x_1924 = lean_ctor_get_uint16(x_1922, sizeof(void*)*4);
x_1925 = lean_ctor_get(x_1922, 1);
lean_inc(x_1925);
x_1926 = lean_ctor_get(x_1922, 2);
lean_inc(x_1926);
x_1927 = lean_ctor_get(x_1922, 3);
lean_inc(x_1927);
if (lean_is_exclusive(x_1922)) {
 lean_ctor_release(x_1922, 0);
 lean_ctor_release(x_1922, 1);
 lean_ctor_release(x_1922, 2);
 lean_ctor_release(x_1922, 3);
 x_1928 = x_1922;
} else {
 lean_dec_ref(x_1922);
 x_1928 = lean_box(0);
}
x_1929 = lean_array_get_size(x_1923);
x_1930 = lean_nat_sub(x_1929, x_1733);
x_1931 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1931, 0, x_1930);
lean_ctor_set(x_1931, 1, x_1907);
x_1932 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1932, 0, x_1931);
lean_ctor_set(x_1932, 1, x_1927);
if (lean_is_scalar(x_1928)) {
 x_1933 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1933 = x_1928;
}
lean_ctor_set(x_1933, 0, x_1923);
lean_ctor_set(x_1933, 1, x_1925);
lean_ctor_set(x_1933, 2, x_1926);
lean_ctor_set(x_1933, 3, x_1932);
lean_ctor_set_uint16(x_1933, sizeof(void*)*4, x_1924);
x_1934 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1933, x_1778);
x_1935 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1934, x_5);
x_1936 = 24;
x_1937 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__28));
x_1938 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_1935, x_1936, x_1937);
x_1939 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1938, x_1767);
x_1940 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1939, x_3);
x_1941 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1940, x_5);
x_1942 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1941, x_7);
x_1943 = lean_ctor_get(x_1942, 0);
lean_inc_ref(x_1943);
x_1944 = lean_ctor_get_uint16(x_1942, sizeof(void*)*4);
x_1945 = lean_ctor_get(x_1942, 1);
lean_inc(x_1945);
x_1946 = lean_ctor_get(x_1942, 2);
lean_inc(x_1946);
x_1947 = lean_ctor_get(x_1942, 3);
lean_inc(x_1947);
if (lean_is_exclusive(x_1942)) {
 lean_ctor_release(x_1942, 0);
 lean_ctor_release(x_1942, 1);
 lean_ctor_release(x_1942, 2);
 lean_ctor_release(x_1942, 3);
 x_1948 = x_1942;
} else {
 lean_dec_ref(x_1942);
 x_1948 = lean_box(0);
}
x_1949 = lean_array_get_size(x_1943);
x_1950 = lean_nat_sub(x_1949, x_1733);
x_1951 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_1952 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1952, 0, x_1950);
lean_ctor_set(x_1952, 1, x_1951);
x_1953 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1953, 0, x_1952);
lean_ctor_set(x_1953, 1, x_1947);
if (lean_is_scalar(x_1948)) {
 x_1954 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1954 = x_1948;
}
lean_ctor_set(x_1954, 0, x_1943);
lean_ctor_set(x_1954, 1, x_1945);
lean_ctor_set(x_1954, 2, x_1946);
lean_ctor_set(x_1954, 3, x_1953);
lean_ctor_set_uint16(x_1954, sizeof(void*)*4, x_1944);
x_1955 = lean_obj_once(&lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1, &lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1_once, _init_lp_sidfinity_MV3_emitInitSubtuneClamp___closed__1);
x_1956 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1954, x_1955);
x_1957 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1956, x_1901);
x_1958 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1957, x_1776);
x_1959 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_1958, x_1901);
x_1960 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1959, x_1778);
x_1961 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1960, x_5);
x_1962 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1961, x_1781);
x_1963 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_1964 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1962, x_1963);
x_1965 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__2, &lp_sidfinity_MV3_emitFlagRule___closed__2_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__2);
x_1966 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1964, x_1965);
x_1967 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_1968 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1966, x_1967);
x_1969 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_1970 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1968, x_1969);
x_1971 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__29));
x_1972 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_1970, x_1742, x_1971);
x_1973 = lp_sidfinity_MV3_CodeBuilder_label(x_1972, x_1937);
x_1974 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1973, x_1767);
x_1975 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1974, x_1901);
x_1976 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1975, x_1778);
x_1977 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1976, x_5);
x_1978 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1977, x_1901);
x_1979 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1978, x_1963);
x_1980 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__30, &lp_sidfinity_MV3_emitSustainEffects___closed__30_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__30);
x_1981 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1979, x_1980);
x_1982 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1981, x_1969);
x_1983 = lp_sidfinity_MV3_CodeBuilder_label(x_1982, x_1971);
x_1984 = lp_sidfinity_MV3_CodeBuilder_label(x_1983, x_1898);
x_1985 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1984, x_1767);
x_1986 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1985, x_3);
x_1987 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1986, x_5);
x_1988 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_1987, x_7);
x_1989 = lean_ctor_get(x_1988, 0);
lean_inc_ref(x_1989);
x_1990 = lean_ctor_get_uint16(x_1988, sizeof(void*)*4);
x_1991 = lean_ctor_get(x_1988, 1);
lean_inc(x_1991);
x_1992 = lean_ctor_get(x_1988, 2);
lean_inc(x_1992);
x_1993 = lean_ctor_get(x_1988, 3);
lean_inc(x_1993);
if (lean_is_exclusive(x_1988)) {
 lean_ctor_release(x_1988, 0);
 lean_ctor_release(x_1988, 1);
 lean_ctor_release(x_1988, 2);
 lean_ctor_release(x_1988, 3);
 x_1994 = x_1988;
} else {
 lean_dec_ref(x_1988);
 x_1994 = lean_box(0);
}
x_1995 = lean_array_get_size(x_1989);
x_1996 = lean_nat_sub(x_1995, x_1733);
x_1997 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_1998 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1998, 0, x_1996);
lean_ctor_set(x_1998, 1, x_1997);
x_1999 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1999, 0, x_1998);
lean_ctor_set(x_1999, 1, x_1993);
if (lean_is_scalar(x_1994)) {
 x_2000 = lean_alloc_ctor(0, 4, 2);
} else {
 x_2000 = x_1994;
}
lean_ctor_set(x_2000, 0, x_1989);
lean_ctor_set(x_2000, 1, x_1991);
lean_ctor_set(x_2000, 2, x_1992);
lean_ctor_set(x_2000, 3, x_1999);
lean_ctor_set_uint16(x_2000, sizeof(void*)*4, x_1990);
x_2001 = 26;
x_2002 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__32));
x_2003 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_2000, x_2001, x_2002);
x_2004 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_2005 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2003, x_2004);
x_2006 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_2007 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2005, x_2006);
x_2008 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_2007, x_2001, x_2002);
x_2009 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2008, x_1767);
x_2010 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_2009, x_1901);
x_2011 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_2010, x_2001, x_2002);
x_2012 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2011, x_1776);
x_2013 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_2012, x_1901);
x_2014 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_2013, x_1778);
x_2015 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2014, x_5);
x_2016 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2015, x_1781);
x_2017 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2016, x_1963);
x_2018 = lp_sidfinity_MV3_CodeBuilder_label(x_2017, x_2002);
x_2019 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2018, x_1767);
x_2020 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_2019, x_3);
x_2021 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2020, x_5);
x_2022 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2021, x_7);
x_2023 = lean_ctor_get(x_2022, 0);
lean_inc_ref(x_2023);
x_2024 = lean_ctor_get_uint16(x_2022, sizeof(void*)*4);
x_2025 = lean_ctor_get(x_2022, 1);
lean_inc(x_2025);
x_2026 = lean_ctor_get(x_2022, 2);
lean_inc(x_2026);
x_2027 = lean_ctor_get(x_2022, 3);
lean_inc(x_2027);
if (lean_is_exclusive(x_2022)) {
 lean_ctor_release(x_2022, 0);
 lean_ctor_release(x_2022, 1);
 lean_ctor_release(x_2022, 2);
 lean_ctor_release(x_2022, 3);
 x_2028 = x_2022;
} else {
 lean_dec_ref(x_2022);
 x_2028 = lean_box(0);
}
x_2029 = lean_array_get_size(x_2023);
x_2030 = lean_nat_sub(x_2029, x_1733);
x_2031 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_2032 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_2032, 0, x_2030);
lean_ctor_set(x_2032, 1, x_2031);
x_2033 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_2033, 0, x_2032);
lean_ctor_set(x_2033, 1, x_2027);
if (lean_is_scalar(x_2028)) {
 x_2034 = lean_alloc_ctor(0, 4, 2);
} else {
 x_2034 = x_2028;
}
lean_ctor_set(x_2034, 0, x_2023);
lean_ctor_set(x_2034, 1, x_2025);
lean_ctor_set(x_2034, 2, x_2026);
lean_ctor_set(x_2034, 3, x_2033);
lean_ctor_set_uint16(x_2034, sizeof(void*)*4, x_2024);
x_2035 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__36));
x_2036 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_2034, x_1739, x_2035);
x_2037 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__37));
x_2038 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_2036, x_1742, x_2037);
x_2039 = lp_sidfinity_MV3_CodeBuilder_label(x_2038, x_2035);
x_2040 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2039, x_1776);
x_2041 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2040, x_2004);
x_2042 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2041, x_2006);
x_2043 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__38));
x_2044 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_2042, x_2001, x_2043);
x_2045 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2044, x_1804);
x_2046 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_2047 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_2045, x_2046);
x_2048 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__2, &lp_sidfinity_MV3_emitNoteLoadOp___closed__2_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__2);
x_2049 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2047, x_2048);
x_2050 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__39));
x_2051 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_2049, x_1742, x_2050);
x_2052 = lp_sidfinity_MV3_CodeBuilder_label(x_2051, x_2043);
x_2053 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_2052, x_2046);
x_2054 = lp_sidfinity_MV3_CodeBuilder_label(x_2053, x_2050);
x_2055 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2054, x_5);
x_2056 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_2057 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_2055, x_2056);
x_2058 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2057, x_1746);
x_2059 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_2060 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_2058, x_2059);
x_2061 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2060, x_1776);
x_2062 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2061, x_1767);
x_2063 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_2062, x_1778);
x_2064 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2063, x_5);
x_2065 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2064, x_1791);
x_2066 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2065, x_1963);
x_2067 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2066, x_1781);
x_2068 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_2069 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2067, x_2068);
x_2070 = lp_sidfinity_MV3_CodeBuilder_label(x_2069, x_2037);
x_2071 = lp_sidfinity_I_rts;
x_2072 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_2070, x_2071);
x_2073 = lp_sidfinity_MV3_emitNoteLoadPath(x_2072, x_2);
return x_2073;
}
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 7;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__4(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 4;
x_2 = lp_sidfinity_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__6(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 7;
x_2 = lp_sidfinity_I_eor__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 246;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__8(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_sidfinity_I_sbc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__9(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 244;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__10(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 245;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__16(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 247;
x_2 = lp_sidfinity_I_dec__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__17(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 21;
x_2 = lp_sidfinity_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__20(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 246;
x_2 = lp_sidfinity_I_ldy__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__21(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 242;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__22(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 243;
x_2 = lp_sidfinity_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__24(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 242;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__25(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 244;
x_2 = lp_sidfinity_I_adc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__26(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 243;
x_2 = lp_sidfinity_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__27(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 245;
x_2 = lp_sidfinity_I_adc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitVibrato___redArg(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_2 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3));
x_3 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lp_sidfinity_I_tay;
x_5 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__1));
x_7 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_5, x_6);
x_8 = !lean_is_exclusive(x_7);
if (x_8 == 0)
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; uint8_t x_19; lean_object* x_20; lean_object* x_21; uint8_t x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; uint8_t x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; uint8_t x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; uint8_t x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; uint8_t x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; 
x_9 = lean_ctor_get(x_7, 0);
x_10 = lean_ctor_get(x_7, 3);
x_11 = lean_array_get_size(x_9);
x_12 = lean_unsigned_to_nat(2u);
x_13 = lean_nat_sub(x_11, x_12);
x_14 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__0));
x_15 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_15, 0, x_13);
lean_ctor_set(x_15, 1, x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_10);
lean_ctor_set(x_7, 3, x_16);
x_17 = lp_sidfinity_I_clc;
x_18 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_7, x_17);
x_19 = 27;
x_20 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__1));
x_21 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_18, x_19, x_20);
x_22 = 32;
x_23 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__2));
x_24 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_21, x_22, x_23);
x_25 = lp_sidfinity_MV3_CodeBuilder_label(x_24, x_20);
x_26 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_27 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_25, x_26);
x_28 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_29 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_27, x_28);
x_30 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__3, &lp_sidfinity_MV3_emitVibrato___redArg___closed__3_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__3);
x_31 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_29, x_30);
x_32 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__4, &lp_sidfinity_MV3_emitVibrato___redArg___closed__4_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__4);
x_33 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_31, x_32);
x_34 = 24;
x_35 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__5));
x_36 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_33, x_34, x_35);
x_37 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__6, &lp_sidfinity_MV3_emitVibrato___redArg___closed__6_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__6);
x_38 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_36, x_37);
x_39 = lp_sidfinity_MV3_CodeBuilder_label(x_38, x_35);
x_40 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__7, &lp_sidfinity_MV3_emitVibrato___redArg___closed__7_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__7);
x_41 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_39, x_40);
x_42 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_43 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_41, x_42);
x_44 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_43, x_4);
x_45 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_46 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_44, x_45);
x_47 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_48 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_46, x_47);
x_49 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_50 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_48, x_49);
x_51 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__0, &lp_sidfinity_MV3_emitNL__PortaInit___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__0);
x_52 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_50, x_51);
x_53 = lp_sidfinity_I_iny;
x_54 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_52, x_53);
x_55 = lp_sidfinity_I_sec;
x_56 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_54, x_55);
x_57 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_56, x_45);
x_58 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__8, &lp_sidfinity_MV3_emitVibrato___redArg___closed__8_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__8);
x_59 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_57, x_58);
x_60 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__9, &lp_sidfinity_MV3_emitVibrato___redArg___closed__9_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__9);
x_61 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_59, x_60);
x_62 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_61, x_49);
x_63 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__16, &lp_sidfinity_MV3_emitSustainEffects___closed__16_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__16);
x_64 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_62, x_63);
x_65 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__10, &lp_sidfinity_MV3_emitVibrato___redArg___closed__10_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__10);
x_66 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_64, x_65);
x_67 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__11));
x_68 = lp_sidfinity_MV3_CodeBuilder_label(x_66, x_67);
x_69 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__13));
x_70 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_68, x_69);
x_71 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__15));
x_72 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_70, x_71);
x_73 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__16, &lp_sidfinity_MV3_emitVibrato___redArg___closed__16_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__16);
x_74 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_72, x_73);
x_75 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_74, x_19, x_67);
x_76 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_77 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_75, x_76);
x_78 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_79 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_77, x_78);
x_80 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__17, &lp_sidfinity_MV3_emitVibrato___redArg___closed__17_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__17);
x_81 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_79, x_80);
x_82 = 25;
x_83 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__18));
x_84 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_81, x_82, x_83);
x_85 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__19));
x_86 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_84, x_22, x_85);
x_87 = lp_sidfinity_MV3_CodeBuilder_label(x_86, x_83);
x_88 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__20, &lp_sidfinity_MV3_emitVibrato___redArg___closed__20_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__20);
x_89 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_87, x_88);
x_90 = lp_sidfinity_I_dey;
x_91 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_89, x_90);
x_92 = 28;
x_93 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_91, x_92, x_85);
x_94 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__1, &lp_sidfinity_MV3_emitNL__PortaInit___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__1);
x_95 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_93, x_94);
x_96 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__21, &lp_sidfinity_MV3_emitVibrato___redArg___closed__21_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__21);
x_97 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_95, x_96);
x_98 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__3, &lp_sidfinity_MV3_emitNL__PortaInit___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__3);
x_99 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_97, x_98);
x_100 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__22, &lp_sidfinity_MV3_emitVibrato___redArg___closed__22_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__22);
x_101 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_99, x_100);
x_102 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__23));
x_103 = lp_sidfinity_MV3_CodeBuilder_label(x_101, x_102);
x_104 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_103, x_17);
x_105 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__24, &lp_sidfinity_MV3_emitVibrato___redArg___closed__24_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__24);
x_106 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_104, x_105);
x_107 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__25, &lp_sidfinity_MV3_emitVibrato___redArg___closed__25_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__25);
x_108 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_106, x_107);
x_109 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_108, x_96);
x_110 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__26, &lp_sidfinity_MV3_emitVibrato___redArg___closed__26_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__26);
x_111 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_109, x_110);
x_112 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__27, &lp_sidfinity_MV3_emitVibrato___redArg___closed__27_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__27);
x_113 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_111, x_112);
x_114 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_113, x_100);
x_115 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_114, x_90);
x_116 = 29;
x_117 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_115, x_116, x_102);
x_118 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_117, x_76);
x_119 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_120 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_118, x_119);
x_121 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_120, x_4);
x_122 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_121, x_105);
x_123 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_124 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_122, x_123);
x_125 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_124, x_110);
x_126 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_127 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_125, x_126);
x_128 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_127, x_22, x_23);
x_129 = lp_sidfinity_MV3_CodeBuilder_label(x_128, x_85);
x_130 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_129, x_76);
x_131 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_130, x_119);
x_132 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_131, x_4);
x_133 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_132, x_94);
x_134 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_133, x_123);
x_135 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_134, x_98);
x_136 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_135, x_126);
x_137 = lp_sidfinity_MV3_CodeBuilder_label(x_136, x_23);
x_138 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_137, x_76);
return x_138;
}
else
{
lean_object* x_139; uint16_t x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; lean_object* x_150; lean_object* x_151; lean_object* x_152; uint8_t x_153; lean_object* x_154; lean_object* x_155; uint8_t x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; uint8_t x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; lean_object* x_191; lean_object* x_192; lean_object* x_193; lean_object* x_194; lean_object* x_195; lean_object* x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; lean_object* x_202; lean_object* x_203; lean_object* x_204; lean_object* x_205; lean_object* x_206; lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; lean_object* x_214; lean_object* x_215; uint8_t x_216; lean_object* x_217; lean_object* x_218; lean_object* x_219; lean_object* x_220; lean_object* x_221; lean_object* x_222; lean_object* x_223; lean_object* x_224; lean_object* x_225; uint8_t x_226; lean_object* x_227; lean_object* x_228; lean_object* x_229; lean_object* x_230; lean_object* x_231; lean_object* x_232; lean_object* x_233; lean_object* x_234; lean_object* x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; lean_object* x_239; lean_object* x_240; lean_object* x_241; lean_object* x_242; lean_object* x_243; lean_object* x_244; lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; lean_object* x_249; uint8_t x_250; lean_object* x_251; lean_object* x_252; lean_object* x_253; lean_object* x_254; lean_object* x_255; lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; lean_object* x_265; lean_object* x_266; lean_object* x_267; lean_object* x_268; lean_object* x_269; lean_object* x_270; lean_object* x_271; lean_object* x_272; 
x_139 = lean_ctor_get(x_7, 0);
x_140 = lean_ctor_get_uint16(x_7, sizeof(void*)*4);
x_141 = lean_ctor_get(x_7, 1);
x_142 = lean_ctor_get(x_7, 2);
x_143 = lean_ctor_get(x_7, 3);
lean_inc(x_143);
lean_inc(x_142);
lean_inc(x_141);
lean_inc(x_139);
lean_dec(x_7);
x_144 = lean_array_get_size(x_139);
x_145 = lean_unsigned_to_nat(2u);
x_146 = lean_nat_sub(x_144, x_145);
x_147 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__0));
x_148 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_148, 0, x_146);
lean_ctor_set(x_148, 1, x_147);
x_149 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_149, 0, x_148);
lean_ctor_set(x_149, 1, x_143);
x_150 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_150, 0, x_139);
lean_ctor_set(x_150, 1, x_141);
lean_ctor_set(x_150, 2, x_142);
lean_ctor_set(x_150, 3, x_149);
lean_ctor_set_uint16(x_150, sizeof(void*)*4, x_140);
x_151 = lp_sidfinity_I_clc;
x_152 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_150, x_151);
x_153 = 27;
x_154 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__1));
x_155 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_152, x_153, x_154);
x_156 = 32;
x_157 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__2));
x_158 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_155, x_156, x_157);
x_159 = lp_sidfinity_MV3_CodeBuilder_label(x_158, x_154);
x_160 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__1);
x_161 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_159, x_160);
x_162 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__33, &lp_sidfinity_MV3_emitSustainEffects___closed__33_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__33);
x_163 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_161, x_162);
x_164 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__3, &lp_sidfinity_MV3_emitVibrato___redArg___closed__3_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__3);
x_165 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_163, x_164);
x_166 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__4, &lp_sidfinity_MV3_emitVibrato___redArg___closed__4_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__4);
x_167 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_165, x_166);
x_168 = 24;
x_169 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__5));
x_170 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_167, x_168, x_169);
x_171 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__6, &lp_sidfinity_MV3_emitVibrato___redArg___closed__6_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__6);
x_172 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_170, x_171);
x_173 = lp_sidfinity_MV3_CodeBuilder_label(x_172, x_169);
x_174 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__7, &lp_sidfinity_MV3_emitVibrato___redArg___closed__7_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__7);
x_175 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_173, x_174);
x_176 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_177 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_175, x_176);
x_178 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_177, x_4);
x_179 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_180 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_178, x_179);
x_181 = lean_obj_once(&lp_sidfinity_MV3_emitFlagRule___closed__3, &lp_sidfinity_MV3_emitFlagRule___closed__3_once, _init_lp_sidfinity_MV3_emitFlagRule___closed__3);
x_182 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_180, x_181);
x_183 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_184 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_182, x_183);
x_185 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__0, &lp_sidfinity_MV3_emitNL__PortaInit___closed__0_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__0);
x_186 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_184, x_185);
x_187 = lp_sidfinity_I_iny;
x_188 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_186, x_187);
x_189 = lp_sidfinity_I_sec;
x_190 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_188, x_189);
x_191 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_190, x_179);
x_192 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__8, &lp_sidfinity_MV3_emitVibrato___redArg___closed__8_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__8);
x_193 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_191, x_192);
x_194 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__9, &lp_sidfinity_MV3_emitVibrato___redArg___closed__9_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__9);
x_195 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_193, x_194);
x_196 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsY(x_195, x_183);
x_197 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__16, &lp_sidfinity_MV3_emitSustainEffects___closed__16_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__16);
x_198 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_196, x_197);
x_199 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__10, &lp_sidfinity_MV3_emitVibrato___redArg___closed__10_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__10);
x_200 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_198, x_199);
x_201 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__11));
x_202 = lp_sidfinity_MV3_CodeBuilder_label(x_200, x_201);
x_203 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__13));
x_204 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_202, x_203);
x_205 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__15));
x_206 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_204, x_205);
x_207 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__16, &lp_sidfinity_MV3_emitVibrato___redArg___closed__16_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__16);
x_208 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_206, x_207);
x_209 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_208, x_153, x_201);
x_210 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_211 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_209, x_210);
x_212 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_213 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_211, x_212);
x_214 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__17, &lp_sidfinity_MV3_emitVibrato___redArg___closed__17_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__17);
x_215 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_213, x_214);
x_216 = 25;
x_217 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__18));
x_218 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_215, x_216, x_217);
x_219 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__19));
x_220 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_218, x_156, x_219);
x_221 = lp_sidfinity_MV3_CodeBuilder_label(x_220, x_217);
x_222 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__20, &lp_sidfinity_MV3_emitVibrato___redArg___closed__20_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__20);
x_223 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_221, x_222);
x_224 = lp_sidfinity_I_dey;
x_225 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_223, x_224);
x_226 = 28;
x_227 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_225, x_226, x_219);
x_228 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__1, &lp_sidfinity_MV3_emitNL__PortaInit___closed__1_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__1);
x_229 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_227, x_228);
x_230 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__21, &lp_sidfinity_MV3_emitVibrato___redArg___closed__21_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__21);
x_231 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_229, x_230);
x_232 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PortaInit___closed__3, &lp_sidfinity_MV3_emitNL__PortaInit___closed__3_once, _init_lp_sidfinity_MV3_emitNL__PortaInit___closed__3);
x_233 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_231, x_232);
x_234 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__22, &lp_sidfinity_MV3_emitVibrato___redArg___closed__22_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__22);
x_235 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_233, x_234);
x_236 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__23));
x_237 = lp_sidfinity_MV3_CodeBuilder_label(x_235, x_236);
x_238 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_237, x_151);
x_239 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__24, &lp_sidfinity_MV3_emitVibrato___redArg___closed__24_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__24);
x_240 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_238, x_239);
x_241 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__25, &lp_sidfinity_MV3_emitVibrato___redArg___closed__25_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__25);
x_242 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_240, x_241);
x_243 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_242, x_230);
x_244 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__26, &lp_sidfinity_MV3_emitVibrato___redArg___closed__26_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__26);
x_245 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_243, x_244);
x_246 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__27, &lp_sidfinity_MV3_emitVibrato___redArg___closed__27_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__27);
x_247 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_245, x_246);
x_248 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_247, x_234);
x_249 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_248, x_224);
x_250 = 29;
x_251 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_249, x_250, x_236);
x_252 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_251, x_210);
x_253 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_254 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_252, x_253);
x_255 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_254, x_4);
x_256 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_255, x_239);
x_257 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_258 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_256, x_257);
x_259 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_258, x_244);
x_260 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_261 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_259, x_260);
x_262 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_261, x_156, x_157);
x_263 = lp_sidfinity_MV3_CodeBuilder_label(x_262, x_219);
x_264 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_263, x_210);
x_265 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_264, x_253);
x_266 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_265, x_4);
x_267 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_266, x_228);
x_268 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_267, x_257);
x_269 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_268, x_232);
x_270 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_269, x_260);
x_271 = lp_sidfinity_MV3_CodeBuilder_label(x_270, x_157);
x_272 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_271, x_210);
return x_272;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitVibrato(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_emitVibrato___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitVibrato___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_emitVibrato(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitExecVoice___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 1;
x_2 = lp_sidfinity_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitExecVoice___closed__5(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 126;
x_2 = lp_sidfinity_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitExecVoice___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 246;
x_2 = lp_sidfinity_I_adc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_emitExecVoice___closed__9(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 246;
x_2 = lp_sidfinity_I_sbc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_emitExecVoice(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; uint8_t x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; 
x_3 = ((lean_object*)(lp_sidfinity_MV3_emitPlayVoiceStep___closed__0));
x_4 = lp_sidfinity_MV3_CodeBuilder_label(x_1, x_3);
x_5 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_6 = lp_sidfinity_MV3_CodeBuilder_emitDecAbsX(x_4, x_5);
x_7 = 29;
x_8 = ((lean_object*)(lp_sidfinity_MV3_emitExecVoice___closed__0));
x_9 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_6, x_7, x_8);
x_10 = 32;
x_11 = ((lean_object*)(lp_sidfinity_MV3_emitNL__Header___closed__0));
x_12 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_9, x_10, x_11);
x_13 = lp_sidfinity_MV3_CodeBuilder_label(x_12, x_8);
x_14 = lean_obj_once(&lp_sidfinity_MV3_emitNL__Header___closed__1, &lp_sidfinity_MV3_emitNL__Header___closed__1_once, _init_lp_sidfinity_MV3_emitNL__Header___closed__1);
x_15 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_13, x_14);
x_16 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_15, x_5);
x_17 = lean_obj_once(&lp_sidfinity_MV3_emitExecVoice___closed__1, &lp_sidfinity_MV3_emitExecVoice___closed__1_once, _init_lp_sidfinity_MV3_emitExecVoice___closed__1);
x_18 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_16, x_17);
x_19 = 27;
x_20 = ((lean_object*)(lp_sidfinity_MV3_emitExecVoice___closed__2));
x_21 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_18, x_19, x_20);
x_22 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1));
x_23 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_21, x_22);
x_24 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_23, x_19, x_20);
x_25 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_26 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_24, x_25);
x_27 = lp_sidfinity_I_tay;
x_28 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_26, x_27);
x_29 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0));
x_30 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_28, x_29);
x_31 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__4);
x_32 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_30, x_31);
x_33 = lean_obj_once(&lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5, &lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__CtrlWrite___closed__5);
x_34 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_32, x_33);
x_35 = lean_obj_once(&lp_sidfinity_MV3_emitNoteLoadOp___closed__1, &lp_sidfinity_MV3_emitNoteLoadOp___closed__1_once, _init_lp_sidfinity_MV3_emitNoteLoadOp___closed__1);
x_36 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_34, x_35);
x_37 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__5);
x_38 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_36, x_37);
x_39 = lean_obj_once(&lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7, &lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7_once, _init_lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__7);
x_40 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_38, x_39);
x_41 = lp_sidfinity_MV3_CodeBuilder_label(x_40, x_20);
x_42 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2));
x_43 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_41, x_42);
x_44 = ((lean_object*)(lp_sidfinity_MV3_emitExecVoice___closed__3));
x_45 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_43, x_19, x_44);
x_46 = ((lean_object*)(lp_sidfinity_MV3_emitExecVoice___closed__4));
x_47 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_45, x_10, x_46);
x_48 = lp_sidfinity_MV3_CodeBuilder_label(x_47, x_44);
x_49 = lean_obj_once(&lp_sidfinity_MV3_emitExecVoice___closed__5, &lp_sidfinity_MV3_emitExecVoice___closed__5_once, _init_lp_sidfinity_MV3_emitExecVoice___closed__5);
x_50 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_48, x_49);
x_51 = lean_obj_once(&lp_sidfinity_MV3_emitVibrato___redArg___closed__7, &lp_sidfinity_MV3_emitVibrato___redArg___closed__7_once, _init_lp_sidfinity_MV3_emitVibrato___redArg___closed__7);
x_52 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_50, x_51);
x_53 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_52, x_42);
x_54 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__34, &lp_sidfinity_MV3_emitSustainEffects___closed__34_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__34);
x_55 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_53, x_54);
x_56 = ((lean_object*)(lp_sidfinity_MV3_emitExecVoice___closed__6));
x_57 = lp_sidfinity_MV3_CodeBuilder_emitBranch(x_55, x_19, x_56);
x_58 = lp_sidfinity_I_clc;
x_59 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_57, x_58);
x_60 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__2));
x_61 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_59, x_60);
x_62 = lean_obj_once(&lp_sidfinity_MV3_emitExecVoice___closed__7, &lp_sidfinity_MV3_emitExecVoice___closed__7_once, _init_lp_sidfinity_MV3_emitExecVoice___closed__7);
x_63 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_61, x_62);
x_64 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_63, x_60);
x_65 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__4));
x_66 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_64, x_65);
x_67 = lean_obj_once(&lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3, &lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3_once, _init_lp_sidfinity_MV3_emitNL__AdvancePtr___closed__3);
x_68 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_66, x_67);
x_69 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_68, x_65);
x_70 = ((lean_object*)(lp_sidfinity_MV3_emitExecVoice___closed__8));
x_71 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_69, x_10, x_70);
x_72 = lp_sidfinity_MV3_CodeBuilder_label(x_71, x_56);
x_73 = lp_sidfinity_I_sec;
x_74 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_72, x_73);
x_75 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_74, x_60);
x_76 = lean_obj_once(&lp_sidfinity_MV3_emitExecVoice___closed__9, &lp_sidfinity_MV3_emitExecVoice___closed__9_once, _init_lp_sidfinity_MV3_emitExecVoice___closed__9);
x_77 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_75, x_76);
x_78 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_77, x_60);
x_79 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_78, x_65);
x_80 = lean_obj_once(&lp_sidfinity_MV3_emitSustainEffects___closed__17, &lp_sidfinity_MV3_emitSustainEffects___closed__17_once, _init_lp_sidfinity_MV3_emitSustainEffects___closed__17);
x_81 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_79, x_80);
x_82 = lp_sidfinity_MV3_CodeBuilder_emitStaAbsX(x_81, x_65);
x_83 = lp_sidfinity_MV3_CodeBuilder_label(x_82, x_70);
x_84 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_83, x_25);
x_85 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_84, x_27);
x_86 = lean_obj_once(&lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1, &lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1_once, _init_lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__1);
x_87 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_85, x_86);
x_88 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_87, x_60);
x_89 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__4, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__4_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__4);
x_90 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_88, x_89);
x_91 = lp_sidfinity_MV3_CodeBuilder_emitLdaAbsX(x_90, x_65);
x_92 = lean_obj_once(&lp_sidfinity_MV3_emitNL__FreqWrite___closed__2, &lp_sidfinity_MV3_emitNL__FreqWrite___closed__2_once, _init_lp_sidfinity_MV3_emitNL__FreqWrite___closed__2);
x_93 = lp_sidfinity_MV3_CodeBuilder_emitInst(x_91, x_92);
x_94 = ((lean_object*)(lp_sidfinity_MV3_emitExecVoice___closed__10));
x_95 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_93, x_10, x_94);
x_96 = lp_sidfinity_MV3_CodeBuilder_label(x_95, x_46);
x_97 = lp_sidfinity_MV3_emitVibrato___redArg(x_96);
x_98 = lp_sidfinity_MV3_CodeBuilder_label(x_97, x_94);
x_99 = lp_sidfinity_MV3_emitSustainEffects(x_98, x_2);
return x_99;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__19(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get(x_4, 10);
lean_inc(x_12);
lean_dec(x_4);
if (lean_obj_tag(x_12) == 0)
{
uint8_t x_13; 
x_13 = 0;
x_7 = x_13;
goto block_11;
}
else
{
uint8_t x_14; 
lean_dec_ref(x_12);
x_14 = 1;
x_7 = x_14;
goto block_11;
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_12; uint8_t x_13; lean_object* x_16; lean_object* x_26; uint8_t x_32; 
x_6 = lean_ctor_get(x_3, 1);
x_7 = lean_ctor_get(x_3, 2);
x_32 = lean_nat_dec_lt(x_5, x_6);
if (x_32 == 0)
{
lean_dec(x_5);
return x_4;
}
else
{
uint8_t x_33; 
x_33 = l_List_elem___at___00Lean_Meta_Occurrences_contains_spec__0(x_5, x_2);
if (x_33 == 0)
{
x_26 = x_4;
goto block_31;
}
else
{
lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; 
x_34 = ((lean_object*)(lp_sidfinity_MV3_emitFreqSlotStore___closed__1));
lean_inc(x_5);
x_35 = l_Nat_reprFast(x_5);
x_36 = lean_string_append(x_34, x_35);
lean_dec_ref(x_35);
x_37 = lp_sidfinity_MV3_CodeBuilder_label(x_4, x_36);
x_26 = x_37;
goto block_31;
}
}
block_11:
{
lean_object* x_9; 
x_9 = lean_nat_add(x_5, x_7);
lean_dec(x_5);
x_4 = x_8;
x_5 = x_9;
goto _start;
}
block_15:
{
lean_object* x_14; 
x_14 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_12, x_13);
x_8 = x_14;
goto block_11;
}
block_25:
{
lean_object* x_17; 
lean_inc(x_5);
x_17 = l_List_get_x3fInternal___redArg(x_1, x_5);
if (lean_obj_tag(x_17) == 0)
{
uint8_t x_18; lean_object* x_19; 
x_18 = 0;
x_19 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_16, x_18);
x_8 = x_19;
goto block_11;
}
else
{
lean_object* x_20; uint8_t x_21; 
x_20 = lean_ctor_get(x_17, 0);
lean_inc(x_20);
lean_dec_ref(x_17);
x_21 = l_List_elem___at___00Lean_Meta_Occurrences_contains_spec__0(x_5, x_2);
if (x_21 == 0)
{
lean_object* x_22; uint8_t x_23; 
x_22 = lean_ctor_get(x_20, 0);
lean_inc(x_22);
lean_dec(x_20);
x_23 = lean_uint8_of_nat(x_22);
lean_dec(x_22);
x_12 = x_16;
x_13 = x_23;
goto block_15;
}
else
{
uint8_t x_24; 
lean_dec(x_20);
x_24 = 0;
x_12 = x_16;
x_13 = x_24;
goto block_15;
}
}
}
block_31:
{
lean_object* x_27; uint8_t x_28; 
x_27 = lean_unsigned_to_nat(106u);
x_28 = lean_nat_dec_eq(x_5, x_27);
if (x_28 == 0)
{
x_16 = x_26;
goto block_25;
}
else
{
lean_object* x_29; lean_object* x_30; 
x_29 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__9));
x_30 = lp_sidfinity_MV3_CodeBuilder_label(x_26, x_29);
x_16 = x_30;
goto block_25;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__17(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get(x_4, 9);
lean_inc(x_12);
lean_dec(x_4);
if (lean_obj_tag(x_12) == 0)
{
uint8_t x_13; 
x_13 = 0;
x_7 = x_13;
goto block_11;
}
else
{
lean_object* x_14; lean_object* x_15; uint8_t x_16; 
x_14 = lean_ctor_get(x_12, 0);
lean_inc(x_14);
lean_dec_ref(x_12);
x_15 = lean_ctor_get(x_14, 1);
lean_inc(x_15);
lean_dec(x_14);
x_16 = lean_uint8_of_nat(x_15);
lean_dec(x_15);
x_7 = x_16;
goto block_11;
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__14(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get(x_4, 8);
lean_inc(x_12);
lean_dec(x_4);
if (lean_obj_tag(x_12) == 0)
{
uint8_t x_13; 
x_13 = 0;
x_7 = x_13;
goto block_11;
}
else
{
lean_object* x_14; lean_object* x_15; 
x_14 = lean_ctor_get(x_12, 0);
lean_inc(x_14);
lean_dec_ref(x_12);
x_15 = lean_ctor_get(x_14, 0);
lean_inc_ref(x_15);
lean_dec(x_14);
switch (lean_obj_tag(x_15)) {
case 0:
{
uint8_t x_16; 
lean_dec_ref(x_15);
x_16 = 128;
x_7 = x_16;
goto block_11;
}
case 1:
{
uint8_t x_17; 
lean_dec_ref(x_15);
x_17 = 1;
x_7 = x_17;
goto block_11;
}
default: 
{
uint8_t x_18; 
lean_dec_ref(x_15);
x_18 = 0;
x_7 = x_18;
goto block_11;
}
}
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__24(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_5, 1);
lean_inc(x_7);
lean_dec(x_5);
x_8 = lean_uint8_of_nat(x_7);
lean_dec(x_7);
x_9 = lean_box(x_8);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_9);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; 
x_11 = lean_ctor_get(x_1, 0);
x_12 = lean_ctor_get(x_1, 1);
lean_inc(x_12);
lean_inc(x_11);
lean_dec(x_1);
x_13 = lean_ctor_get(x_11, 1);
lean_inc(x_13);
lean_dec(x_11);
x_14 = lean_uint8_of_nat(x_13);
lean_dec(x_13);
x_15 = lean_box(x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_2);
x_1 = x_12;
x_2 = x_16;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__8(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_5, 0);
lean_inc(x_7);
lean_dec(x_5);
x_8 = lean_uint8_of_nat(x_7);
lean_dec(x_7);
x_9 = lean_box(x_8);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_9);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; 
x_11 = lean_ctor_get(x_1, 0);
x_12 = lean_ctor_get(x_1, 1);
lean_inc(x_12);
lean_inc(x_11);
lean_dec(x_1);
x_13 = lean_ctor_get(x_11, 0);
lean_inc(x_13);
lean_dec(x_11);
x_14 = lean_uint8_of_nat(x_13);
lean_dec(x_13);
x_15 = lean_box(x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_2);
x_1 = x_12;
x_2 = x_16;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__3(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_8; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_uint8_of_nat(x_5);
lean_dec(x_5);
x_8 = lean_box(x_7);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_8);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; lean_object* x_14; 
x_10 = lean_ctor_get(x_1, 0);
x_11 = lean_ctor_get(x_1, 1);
lean_inc(x_11);
lean_inc(x_10);
lean_dec(x_1);
x_12 = lean_uint8_of_nat(x_10);
lean_dec(x_10);
x_13 = lean_box(x_12);
x_14 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_14, 0, x_13);
lean_ctor_set(x_14, 1, x_2);
x_1 = x_11;
x_2 = x_14;
goto _start;
}
}
}
}
static lean_object* _init_lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___closed__0(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_box(0);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_11; 
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_2, 2);
x_11 = lean_nat_dec_lt(x_4, x_5);
if (x_11 == 0)
{
lean_dec(x_4);
return x_3;
}
else
{
lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; 
x_12 = lean_ctor_get(x_3, 1);
lean_inc(x_12);
x_13 = lean_ctor_get(x_3, 0);
lean_inc(x_13);
if (lean_is_exclusive(x_3)) {
 lean_ctor_release(x_3, 0);
 lean_ctor_release(x_3, 1);
 x_14 = x_3;
} else {
 lean_dec_ref(x_3);
 x_14 = lean_box(0);
}
x_15 = lean_ctor_get(x_12, 0);
lean_inc(x_15);
x_16 = lean_ctor_get(x_12, 1);
lean_inc(x_16);
if (lean_is_exclusive(x_12)) {
 lean_ctor_release(x_12, 0);
 lean_ctor_release(x_12, 1);
 x_17 = x_12;
} else {
 lean_dec_ref(x_12);
 x_17 = lean_box(0);
}
x_18 = lean_ctor_get(x_1, 0);
x_19 = lean_box(0);
lean_inc(x_4);
x_20 = l_List_get_x3fInternal___redArg(x_18, x_4);
if (lean_obj_tag(x_20) == 0)
{
lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_21 = lean_obj_once(&lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___closed__0, &lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___closed__0_once, _init_lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___closed__0);
x_22 = l_List_appendTR___redArg(x_16, x_21);
x_23 = l_List_appendTR___redArg(x_15, x_21);
if (lean_is_scalar(x_17)) {
 x_24 = lean_alloc_ctor(0, 2, 0);
} else {
 x_24 = x_17;
}
lean_ctor_set(x_24, 0, x_23);
lean_ctor_set(x_24, 1, x_22);
if (lean_is_scalar(x_14)) {
 x_25 = lean_alloc_ctor(0, 2, 0);
} else {
 x_25 = x_14;
}
lean_ctor_set(x_25, 0, x_13);
lean_ctor_set(x_25, 1, x_24);
x_7 = x_25;
goto block_10;
}
else
{
lean_object* x_26; uint8_t x_27; 
x_26 = lean_ctor_get(x_20, 0);
lean_inc(x_26);
lean_dec_ref(x_20);
x_27 = !lean_is_exclusive(x_26);
if (x_27 == 0)
{
lean_object* x_28; lean_object* x_29; uint16_t x_30; uint8_t x_31; lean_object* x_32; lean_object* x_33; uint16_t x_34; uint16_t x_35; uint8_t x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; uint8_t x_42; lean_object* x_43; uint8_t x_44; 
x_28 = lean_ctor_get(x_26, 0);
x_29 = lean_ctor_get(x_26, 1);
x_30 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_13);
x_31 = lean_uint16_to_uint8(x_30);
x_32 = lean_box(x_31);
lean_ctor_set_tag(x_26, 1);
lean_ctor_set(x_26, 1, x_19);
lean_ctor_set(x_26, 0, x_32);
x_33 = l_List_appendTR___redArg(x_16, x_26);
x_34 = 8;
x_35 = lean_uint16_shift_right(x_30, x_34);
x_36 = lean_uint16_to_uint8(x_35);
x_37 = lean_box(x_36);
x_38 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_38, 0, x_37);
lean_ctor_set(x_38, 1, x_19);
x_39 = l_List_appendTR___redArg(x_15, x_38);
x_40 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__3(x_28, x_19);
x_41 = lp_sidfinity_MV3_CodeBuilder_emitData(x_13, x_40);
x_42 = 255;
x_43 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_41, x_42);
if (lean_obj_tag(x_29) == 0)
{
x_44 = x_42;
goto block_48;
}
else
{
lean_object* x_49; uint8_t x_50; 
x_49 = lean_ctor_get(x_29, 0);
lean_inc(x_49);
lean_dec_ref(x_29);
x_50 = lean_uint8_of_nat(x_49);
lean_dec(x_49);
x_44 = x_50;
goto block_48;
}
block_48:
{
lean_object* x_45; lean_object* x_46; lean_object* x_47; 
x_45 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_43, x_44);
if (lean_is_scalar(x_17)) {
 x_46 = lean_alloc_ctor(0, 2, 0);
} else {
 x_46 = x_17;
}
lean_ctor_set(x_46, 0, x_39);
lean_ctor_set(x_46, 1, x_33);
if (lean_is_scalar(x_14)) {
 x_47 = lean_alloc_ctor(0, 2, 0);
} else {
 x_47 = x_14;
}
lean_ctor_set(x_47, 0, x_45);
lean_ctor_set(x_47, 1, x_46);
x_7 = x_47;
goto block_10;
}
}
else
{
lean_object* x_51; lean_object* x_52; uint16_t x_53; uint8_t x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; uint16_t x_58; uint16_t x_59; uint8_t x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; uint8_t x_66; lean_object* x_67; uint8_t x_68; 
x_51 = lean_ctor_get(x_26, 0);
x_52 = lean_ctor_get(x_26, 1);
lean_inc(x_52);
lean_inc(x_51);
lean_dec(x_26);
x_53 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_13);
x_54 = lean_uint16_to_uint8(x_53);
x_55 = lean_box(x_54);
x_56 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_56, 0, x_55);
lean_ctor_set(x_56, 1, x_19);
x_57 = l_List_appendTR___redArg(x_16, x_56);
x_58 = 8;
x_59 = lean_uint16_shift_right(x_53, x_58);
x_60 = lean_uint16_to_uint8(x_59);
x_61 = lean_box(x_60);
x_62 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_62, 0, x_61);
lean_ctor_set(x_62, 1, x_19);
x_63 = l_List_appendTR___redArg(x_15, x_62);
x_64 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__3(x_51, x_19);
x_65 = lp_sidfinity_MV3_CodeBuilder_emitData(x_13, x_64);
x_66 = 255;
x_67 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_65, x_66);
if (lean_obj_tag(x_52) == 0)
{
x_68 = x_66;
goto block_72;
}
else
{
lean_object* x_73; uint8_t x_74; 
x_73 = lean_ctor_get(x_52, 0);
lean_inc(x_73);
lean_dec_ref(x_52);
x_74 = lean_uint8_of_nat(x_73);
lean_dec(x_73);
x_68 = x_74;
goto block_72;
}
block_72:
{
lean_object* x_69; lean_object* x_70; lean_object* x_71; 
x_69 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_67, x_68);
if (lean_is_scalar(x_17)) {
 x_70 = lean_alloc_ctor(0, 2, 0);
} else {
 x_70 = x_17;
}
lean_ctor_set(x_70, 0, x_63);
lean_ctor_set(x_70, 1, x_57);
if (lean_is_scalar(x_14)) {
 x_71 = lean_alloc_ctor(0, 2, 0);
} else {
 x_71 = x_14;
}
lean_ctor_set(x_71, 0, x_69);
lean_ctor_set(x_71, 1, x_70);
x_7 = x_71;
goto block_10;
}
}
}
}
block_10:
{
lean_object* x_8; 
x_8 = lean_nat_add(x_4, x_6);
lean_dec(x_4);
x_3 = x_7;
x_4 = x_8;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
return x_2;
}
else
{
lean_object* x_3; uint8_t x_4; 
x_3 = lean_ctor_get(x_2, 1);
lean_inc(x_3);
x_4 = !lean_is_exclusive(x_2);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_2, 1);
lean_dec(x_7);
x_8 = !lean_is_exclusive(x_3);
if (x_8 == 0)
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_9 = lean_unsigned_to_nat(0u);
x_10 = ((lean_object*)(lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___closed__0));
x_11 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg(x_5, x_10, x_2, x_9);
x_1 = x_6;
x_2 = x_11;
goto _start;
}
else
{
lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; 
x_13 = lean_ctor_get(x_3, 0);
x_14 = lean_ctor_get(x_3, 1);
lean_inc(x_14);
lean_inc(x_13);
lean_dec(x_3);
x_15 = lean_unsigned_to_nat(0u);
x_16 = ((lean_object*)(lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___closed__0));
x_17 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_17, 0, x_13);
lean_ctor_set(x_17, 1, x_14);
lean_ctor_set(x_2, 1, x_17);
x_18 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg(x_5, x_16, x_2, x_15);
x_1 = x_6;
x_2 = x_18;
goto _start;
}
}
else
{
lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; 
x_20 = lean_ctor_get(x_1, 0);
x_21 = lean_ctor_get(x_1, 1);
x_22 = lean_ctor_get(x_2, 0);
lean_inc(x_22);
lean_dec(x_2);
x_23 = lean_ctor_get(x_3, 0);
lean_inc(x_23);
x_24 = lean_ctor_get(x_3, 1);
lean_inc(x_24);
if (lean_is_exclusive(x_3)) {
 lean_ctor_release(x_3, 0);
 lean_ctor_release(x_3, 1);
 x_25 = x_3;
} else {
 lean_dec_ref(x_3);
 x_25 = lean_box(0);
}
x_26 = lean_unsigned_to_nat(0u);
x_27 = ((lean_object*)(lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___closed__0));
if (lean_is_scalar(x_25)) {
 x_28 = lean_alloc_ctor(0, 2, 0);
} else {
 x_28 = x_25;
}
lean_ctor_set(x_28, 0, x_23);
lean_ctor_set(x_28, 1, x_24);
x_29 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_29, 0, x_22);
lean_ctor_set(x_29, 1, x_28);
x_30 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg(x_20, x_27, x_29, x_26);
x_1 = x_21;
x_2 = x_30;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__10(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_5, 2);
lean_inc(x_7);
lean_dec(x_5);
x_8 = lean_uint8_of_nat(x_7);
lean_dec(x_7);
x_9 = lean_box(x_8);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_9);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; 
x_11 = lean_ctor_get(x_1, 0);
x_12 = lean_ctor_get(x_1, 1);
lean_inc(x_12);
lean_inc(x_11);
lean_dec(x_1);
x_13 = lean_ctor_get(x_11, 2);
lean_inc(x_13);
lean_dec(x_11);
x_14 = lean_uint8_of_nat(x_13);
lean_dec(x_13);
x_15 = lean_box(x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_2);
x_1 = x_12;
x_2 = x_16;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__16(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get(x_4, 8);
lean_inc(x_12);
lean_dec(x_4);
if (lean_obj_tag(x_12) == 1)
{
lean_object* x_13; lean_object* x_14; 
x_13 = lean_ctor_get(x_12, 0);
lean_inc(x_13);
lean_dec_ref(x_12);
x_14 = lean_ctor_get(x_13, 0);
lean_inc_ref(x_14);
lean_dec(x_13);
if (lean_obj_tag(x_14) == 1)
{
lean_object* x_15; uint8_t x_16; 
x_15 = lean_ctor_get(x_14, 2);
lean_inc(x_15);
lean_dec_ref(x_14);
x_16 = lean_uint8_of_nat(x_15);
lean_dec(x_15);
x_7 = x_16;
goto block_11;
}
else
{
uint8_t x_17; 
lean_dec_ref(x_14);
x_17 = 0;
x_7 = x_17;
goto block_11;
}
}
else
{
uint8_t x_18; 
lean_dec(x_12);
x_18 = 0;
x_7 = x_18;
goto block_11;
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
return x_2;
}
else
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; uint8_t x_9; 
x_3 = lean_ctor_get(x_1, 0);
x_4 = lean_ctor_get(x_1, 1);
x_5 = lean_ctor_get(x_3, 0);
x_6 = lean_ctor_get(x_3, 1);
x_7 = lean_ctor_get(x_3, 2);
x_8 = lean_ctor_get(x_3, 3);
switch (lean_obj_tag(x_5)) {
case 0:
{
lean_object* x_19; uint8_t x_20; 
x_19 = lean_ctor_get(x_5, 0);
x_20 = lean_uint8_of_nat(x_19);
x_9 = x_20;
goto block_18;
}
case 1:
{
uint8_t x_21; 
x_21 = 104;
x_9 = x_21;
goto block_18;
}
case 2:
{
uint8_t x_22; 
x_22 = 254;
x_9 = x_22;
goto block_18;
}
default: 
{
uint8_t x_23; 
x_23 = 253;
x_9 = x_23;
goto block_18;
}
}
block_18:
{
lean_object* x_10; uint8_t x_11; lean_object* x_12; uint8_t x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; 
x_10 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_2, x_9);
x_11 = lean_uint8_of_nat(x_6);
x_12 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_10, x_11);
x_13 = lean_uint8_of_nat(x_7);
x_14 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_12, x_13);
x_15 = lean_uint8_of_nat(x_8);
x_16 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_14, x_15);
x_1 = x_4;
x_2 = x_16;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
return x_2;
}
else
{
lean_object* x_3; uint8_t x_4; 
x_3 = lean_ctor_get(x_2, 1);
lean_inc(x_3);
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
uint8_t x_5; 
x_5 = !lean_is_exclusive(x_2);
if (x_5 == 0)
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; 
x_6 = lean_ctor_get(x_1, 0);
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_ctor_get(x_2, 0);
x_9 = lean_ctor_get(x_2, 1);
lean_dec(x_9);
x_10 = !lean_is_exclusive(x_3);
if (x_10 == 0)
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; uint16_t x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; uint16_t x_18; uint16_t x_19; uint8_t x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; uint8_t x_25; lean_object* x_26; 
x_11 = lean_ctor_get(x_3, 0);
x_12 = lean_ctor_get(x_3, 1);
x_13 = lean_box(0);
x_14 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_8);
x_15 = lean_uint16_to_uint8(x_14);
x_16 = lean_box(x_15);
lean_ctor_set(x_1, 1, x_13);
lean_ctor_set(x_1, 0, x_16);
x_17 = l_List_appendTR___redArg(x_12, x_1);
x_18 = 8;
x_19 = lean_uint16_shift_right(x_14, x_18);
x_20 = lean_uint16_to_uint8(x_19);
x_21 = lean_box(x_20);
x_22 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_22, 0, x_21);
lean_ctor_set(x_22, 1, x_13);
x_23 = l_List_appendTR___redArg(x_11, x_22);
x_24 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(x_6, x_8);
lean_dec(x_6);
x_25 = 0;
x_26 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_24, x_25);
lean_ctor_set(x_3, 1, x_17);
lean_ctor_set(x_3, 0, x_23);
lean_ctor_set(x_2, 0, x_26);
x_1 = x_7;
goto _start;
}
else
{
lean_object* x_28; lean_object* x_29; lean_object* x_30; uint16_t x_31; uint8_t x_32; lean_object* x_33; lean_object* x_34; uint16_t x_35; uint16_t x_36; uint8_t x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; uint8_t x_42; lean_object* x_43; lean_object* x_44; 
x_28 = lean_ctor_get(x_3, 0);
x_29 = lean_ctor_get(x_3, 1);
lean_inc(x_29);
lean_inc(x_28);
lean_dec(x_3);
x_30 = lean_box(0);
x_31 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_8);
x_32 = lean_uint16_to_uint8(x_31);
x_33 = lean_box(x_32);
lean_ctor_set(x_1, 1, x_30);
lean_ctor_set(x_1, 0, x_33);
x_34 = l_List_appendTR___redArg(x_29, x_1);
x_35 = 8;
x_36 = lean_uint16_shift_right(x_31, x_35);
x_37 = lean_uint16_to_uint8(x_36);
x_38 = lean_box(x_37);
x_39 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_39, 0, x_38);
lean_ctor_set(x_39, 1, x_30);
x_40 = l_List_appendTR___redArg(x_28, x_39);
x_41 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(x_6, x_8);
lean_dec(x_6);
x_42 = 0;
x_43 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_41, x_42);
x_44 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_44, 0, x_40);
lean_ctor_set(x_44, 1, x_34);
lean_ctor_set(x_2, 1, x_44);
lean_ctor_set(x_2, 0, x_43);
x_1 = x_7;
goto _start;
}
}
else
{
lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; uint16_t x_53; uint8_t x_54; lean_object* x_55; lean_object* x_56; uint16_t x_57; uint16_t x_58; uint8_t x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; uint8_t x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; 
x_46 = lean_ctor_get(x_1, 0);
x_47 = lean_ctor_get(x_1, 1);
x_48 = lean_ctor_get(x_2, 0);
lean_inc(x_48);
lean_dec(x_2);
x_49 = lean_ctor_get(x_3, 0);
lean_inc(x_49);
x_50 = lean_ctor_get(x_3, 1);
lean_inc(x_50);
if (lean_is_exclusive(x_3)) {
 lean_ctor_release(x_3, 0);
 lean_ctor_release(x_3, 1);
 x_51 = x_3;
} else {
 lean_dec_ref(x_3);
 x_51 = lean_box(0);
}
x_52 = lean_box(0);
x_53 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_48);
x_54 = lean_uint16_to_uint8(x_53);
x_55 = lean_box(x_54);
lean_ctor_set(x_1, 1, x_52);
lean_ctor_set(x_1, 0, x_55);
x_56 = l_List_appendTR___redArg(x_50, x_1);
x_57 = 8;
x_58 = lean_uint16_shift_right(x_53, x_57);
x_59 = lean_uint16_to_uint8(x_58);
x_60 = lean_box(x_59);
x_61 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_61, 0, x_60);
lean_ctor_set(x_61, 1, x_52);
x_62 = l_List_appendTR___redArg(x_49, x_61);
x_63 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(x_46, x_48);
lean_dec(x_46);
x_64 = 0;
x_65 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_63, x_64);
if (lean_is_scalar(x_51)) {
 x_66 = lean_alloc_ctor(0, 2, 0);
} else {
 x_66 = x_51;
}
lean_ctor_set(x_66, 0, x_62);
lean_ctor_set(x_66, 1, x_56);
x_67 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_67, 0, x_65);
lean_ctor_set(x_67, 1, x_66);
x_1 = x_47;
x_2 = x_67;
goto _start;
}
}
else
{
lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; uint16_t x_77; uint8_t x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; uint16_t x_82; uint16_t x_83; uint8_t x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; uint8_t x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; 
x_69 = lean_ctor_get(x_1, 0);
x_70 = lean_ctor_get(x_1, 1);
lean_inc(x_70);
lean_inc(x_69);
lean_dec(x_1);
x_71 = lean_ctor_get(x_2, 0);
lean_inc(x_71);
if (lean_is_exclusive(x_2)) {
 lean_ctor_release(x_2, 0);
 lean_ctor_release(x_2, 1);
 x_72 = x_2;
} else {
 lean_dec_ref(x_2);
 x_72 = lean_box(0);
}
x_73 = lean_ctor_get(x_3, 0);
lean_inc(x_73);
x_74 = lean_ctor_get(x_3, 1);
lean_inc(x_74);
if (lean_is_exclusive(x_3)) {
 lean_ctor_release(x_3, 0);
 lean_ctor_release(x_3, 1);
 x_75 = x_3;
} else {
 lean_dec_ref(x_3);
 x_75 = lean_box(0);
}
x_76 = lean_box(0);
x_77 = lp_sidfinity_MV3_CodeBuilder_currentAddr(x_71);
x_78 = lean_uint16_to_uint8(x_77);
x_79 = lean_box(x_78);
x_80 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_80, 0, x_79);
lean_ctor_set(x_80, 1, x_76);
x_81 = l_List_appendTR___redArg(x_74, x_80);
x_82 = 8;
x_83 = lean_uint16_shift_right(x_77, x_82);
x_84 = lean_uint16_to_uint8(x_83);
x_85 = lean_box(x_84);
x_86 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_86, 0, x_85);
lean_ctor_set(x_86, 1, x_76);
x_87 = l_List_appendTR___redArg(x_73, x_86);
x_88 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(x_69, x_71);
lean_dec(x_69);
x_89 = 0;
x_90 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_88, x_89);
if (lean_is_scalar(x_75)) {
 x_91 = lean_alloc_ctor(0, 2, 0);
} else {
 x_91 = x_75;
}
lean_ctor_set(x_91, 0, x_87);
lean_ctor_set(x_91, 1, x_81);
if (lean_is_scalar(x_72)) {
 x_92 = lean_alloc_ctor(0, 2, 0);
} else {
 x_92 = x_72;
}
lean_ctor_set(x_92, 0, x_90);
lean_ctor_set(x_92, 1, x_91);
x_1 = x_70;
x_2 = x_92;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__11(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_5, 3);
lean_inc(x_7);
lean_dec(x_5);
x_8 = lean_uint8_of_nat(x_7);
lean_dec(x_7);
x_9 = lean_box(x_8);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_9);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; 
x_11 = lean_ctor_get(x_1, 0);
x_12 = lean_ctor_get(x_1, 1);
lean_inc(x_12);
lean_inc(x_11);
lean_dec(x_1);
x_13 = lean_ctor_get(x_11, 3);
lean_inc(x_13);
lean_dec(x_11);
x_14 = lean_uint8_of_nat(x_13);
lean_dec(x_13);
x_15 = lean_box(x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_2);
x_1 = x_12;
x_2 = x_16;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_8; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_uint8_of_nat(x_5);
lean_dec(x_5);
x_8 = lean_box(x_7);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_8);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; lean_object* x_14; 
x_10 = lean_ctor_get(x_1, 0);
x_11 = lean_ctor_get(x_1, 1);
lean_inc(x_11);
lean_inc(x_10);
lean_dec(x_1);
x_12 = lean_uint8_of_nat(x_10);
lean_dec(x_10);
x_13 = lean_box(x_12);
x_14 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_14, 0, x_13);
lean_ctor_set(x_14, 1, x_2);
x_1 = x_11;
x_2 = x_14;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
return x_2;
}
else
{
lean_object* x_3; lean_object* x_4; uint8_t x_5; 
x_3 = lean_ctor_get(x_2, 1);
lean_inc(x_3);
x_4 = lean_ctor_get(x_3, 1);
lean_inc(x_4);
x_5 = !lean_is_exclusive(x_1);
if (x_5 == 0)
{
uint8_t x_6; 
x_6 = !lean_is_exclusive(x_2);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint8_t x_11; 
x_7 = lean_ctor_get(x_1, 0);
x_8 = lean_ctor_get(x_1, 1);
x_9 = lean_ctor_get(x_2, 0);
x_10 = lean_ctor_get(x_2, 1);
lean_dec(x_10);
x_11 = !lean_is_exclusive(x_3);
if (x_11 == 0)
{
lean_object* x_12; lean_object* x_13; uint8_t x_14; 
x_12 = lean_ctor_get(x_3, 0);
x_13 = lean_ctor_get(x_3, 1);
lean_dec(x_13);
x_14 = !lean_is_exclusive(x_4);
if (x_14 == 0)
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; uint8_t x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; uint8_t x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; 
x_15 = lean_ctor_get(x_4, 0);
x_16 = lean_ctor_get(x_4, 1);
x_17 = lean_ctor_get(x_7, 5);
lean_inc(x_17);
x_18 = lean_ctor_get(x_7, 6);
lean_inc(x_18);
lean_dec(x_7);
x_19 = lean_box(0);
x_20 = l_List_lengthTR___redArg(x_12);
x_21 = lean_uint8_of_nat(x_20);
lean_dec(x_20);
x_22 = lean_box(x_21);
lean_ctor_set(x_1, 1, x_19);
lean_ctor_set(x_1, 0, x_22);
x_23 = l_List_appendTR___redArg(x_9, x_1);
x_24 = l_List_lengthTR___redArg(x_17);
x_25 = lean_uint8_of_nat(x_24);
lean_dec(x_24);
x_26 = lean_box(x_25);
x_27 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_27, 0, x_26);
lean_ctor_set(x_27, 1, x_19);
x_28 = l_List_appendTR___redArg(x_15, x_27);
x_29 = lean_uint8_of_nat(x_18);
lean_dec(x_18);
x_30 = lean_box(x_29);
x_31 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_31, 0, x_30);
lean_ctor_set(x_31, 1, x_19);
x_32 = l_List_appendTR___redArg(x_16, x_31);
x_33 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__0(x_17, x_19);
x_34 = l_List_appendTR___redArg(x_12, x_33);
lean_ctor_set(x_4, 1, x_32);
lean_ctor_set(x_4, 0, x_28);
lean_ctor_set(x_3, 0, x_34);
lean_ctor_set(x_2, 0, x_23);
x_1 = x_8;
goto _start;
}
else
{
lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; uint8_t x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; uint8_t x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; uint8_t x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; 
x_36 = lean_ctor_get(x_4, 0);
x_37 = lean_ctor_get(x_4, 1);
lean_inc(x_37);
lean_inc(x_36);
lean_dec(x_4);
x_38 = lean_ctor_get(x_7, 5);
lean_inc(x_38);
x_39 = lean_ctor_get(x_7, 6);
lean_inc(x_39);
lean_dec(x_7);
x_40 = lean_box(0);
x_41 = l_List_lengthTR___redArg(x_12);
x_42 = lean_uint8_of_nat(x_41);
lean_dec(x_41);
x_43 = lean_box(x_42);
lean_ctor_set(x_1, 1, x_40);
lean_ctor_set(x_1, 0, x_43);
x_44 = l_List_appendTR___redArg(x_9, x_1);
x_45 = l_List_lengthTR___redArg(x_38);
x_46 = lean_uint8_of_nat(x_45);
lean_dec(x_45);
x_47 = lean_box(x_46);
x_48 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_48, 0, x_47);
lean_ctor_set(x_48, 1, x_40);
x_49 = l_List_appendTR___redArg(x_36, x_48);
x_50 = lean_uint8_of_nat(x_39);
lean_dec(x_39);
x_51 = lean_box(x_50);
x_52 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_52, 0, x_51);
lean_ctor_set(x_52, 1, x_40);
x_53 = l_List_appendTR___redArg(x_37, x_52);
x_54 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__0(x_38, x_40);
x_55 = l_List_appendTR___redArg(x_12, x_54);
x_56 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_56, 0, x_49);
lean_ctor_set(x_56, 1, x_53);
lean_ctor_set(x_3, 1, x_56);
lean_ctor_set(x_3, 0, x_55);
lean_ctor_set(x_2, 0, x_44);
x_1 = x_8;
goto _start;
}
}
else
{
lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; uint8_t x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; uint8_t x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; uint8_t x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; 
x_58 = lean_ctor_get(x_3, 0);
lean_inc(x_58);
lean_dec(x_3);
x_59 = lean_ctor_get(x_4, 0);
lean_inc(x_59);
x_60 = lean_ctor_get(x_4, 1);
lean_inc(x_60);
if (lean_is_exclusive(x_4)) {
 lean_ctor_release(x_4, 0);
 lean_ctor_release(x_4, 1);
 x_61 = x_4;
} else {
 lean_dec_ref(x_4);
 x_61 = lean_box(0);
}
x_62 = lean_ctor_get(x_7, 5);
lean_inc(x_62);
x_63 = lean_ctor_get(x_7, 6);
lean_inc(x_63);
lean_dec(x_7);
x_64 = lean_box(0);
x_65 = l_List_lengthTR___redArg(x_58);
x_66 = lean_uint8_of_nat(x_65);
lean_dec(x_65);
x_67 = lean_box(x_66);
lean_ctor_set(x_1, 1, x_64);
lean_ctor_set(x_1, 0, x_67);
x_68 = l_List_appendTR___redArg(x_9, x_1);
x_69 = l_List_lengthTR___redArg(x_62);
x_70 = lean_uint8_of_nat(x_69);
lean_dec(x_69);
x_71 = lean_box(x_70);
x_72 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_72, 0, x_71);
lean_ctor_set(x_72, 1, x_64);
x_73 = l_List_appendTR___redArg(x_59, x_72);
x_74 = lean_uint8_of_nat(x_63);
lean_dec(x_63);
x_75 = lean_box(x_74);
x_76 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_76, 0, x_75);
lean_ctor_set(x_76, 1, x_64);
x_77 = l_List_appendTR___redArg(x_60, x_76);
x_78 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__0(x_62, x_64);
x_79 = l_List_appendTR___redArg(x_58, x_78);
if (lean_is_scalar(x_61)) {
 x_80 = lean_alloc_ctor(0, 2, 0);
} else {
 x_80 = x_61;
}
lean_ctor_set(x_80, 0, x_73);
lean_ctor_set(x_80, 1, x_77);
x_81 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_81, 0, x_79);
lean_ctor_set(x_81, 1, x_80);
lean_ctor_set(x_2, 1, x_81);
lean_ctor_set(x_2, 0, x_68);
x_1 = x_8;
goto _start;
}
}
else
{
lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; lean_object* x_93; lean_object* x_94; uint8_t x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; uint8_t x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; uint8_t x_103; lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; 
x_83 = lean_ctor_get(x_1, 0);
x_84 = lean_ctor_get(x_1, 1);
x_85 = lean_ctor_get(x_2, 0);
lean_inc(x_85);
lean_dec(x_2);
x_86 = lean_ctor_get(x_3, 0);
lean_inc(x_86);
if (lean_is_exclusive(x_3)) {
 lean_ctor_release(x_3, 0);
 lean_ctor_release(x_3, 1);
 x_87 = x_3;
} else {
 lean_dec_ref(x_3);
 x_87 = lean_box(0);
}
x_88 = lean_ctor_get(x_4, 0);
lean_inc(x_88);
x_89 = lean_ctor_get(x_4, 1);
lean_inc(x_89);
if (lean_is_exclusive(x_4)) {
 lean_ctor_release(x_4, 0);
 lean_ctor_release(x_4, 1);
 x_90 = x_4;
} else {
 lean_dec_ref(x_4);
 x_90 = lean_box(0);
}
x_91 = lean_ctor_get(x_83, 5);
lean_inc(x_91);
x_92 = lean_ctor_get(x_83, 6);
lean_inc(x_92);
lean_dec(x_83);
x_93 = lean_box(0);
x_94 = l_List_lengthTR___redArg(x_86);
x_95 = lean_uint8_of_nat(x_94);
lean_dec(x_94);
x_96 = lean_box(x_95);
lean_ctor_set(x_1, 1, x_93);
lean_ctor_set(x_1, 0, x_96);
x_97 = l_List_appendTR___redArg(x_85, x_1);
x_98 = l_List_lengthTR___redArg(x_91);
x_99 = lean_uint8_of_nat(x_98);
lean_dec(x_98);
x_100 = lean_box(x_99);
x_101 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_101, 0, x_100);
lean_ctor_set(x_101, 1, x_93);
x_102 = l_List_appendTR___redArg(x_88, x_101);
x_103 = lean_uint8_of_nat(x_92);
lean_dec(x_92);
x_104 = lean_box(x_103);
x_105 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_105, 0, x_104);
lean_ctor_set(x_105, 1, x_93);
x_106 = l_List_appendTR___redArg(x_89, x_105);
x_107 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__0(x_91, x_93);
x_108 = l_List_appendTR___redArg(x_86, x_107);
if (lean_is_scalar(x_90)) {
 x_109 = lean_alloc_ctor(0, 2, 0);
} else {
 x_109 = x_90;
}
lean_ctor_set(x_109, 0, x_102);
lean_ctor_set(x_109, 1, x_106);
if (lean_is_scalar(x_87)) {
 x_110 = lean_alloc_ctor(0, 2, 0);
} else {
 x_110 = x_87;
}
lean_ctor_set(x_110, 0, x_108);
lean_ctor_set(x_110, 1, x_109);
x_111 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_111, 0, x_97);
lean_ctor_set(x_111, 1, x_110);
x_1 = x_84;
x_2 = x_111;
goto _start;
}
}
else
{
lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; uint8_t x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; uint8_t x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; uint8_t x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; lean_object* x_139; lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; 
x_113 = lean_ctor_get(x_1, 0);
x_114 = lean_ctor_get(x_1, 1);
lean_inc(x_114);
lean_inc(x_113);
lean_dec(x_1);
x_115 = lean_ctor_get(x_2, 0);
lean_inc(x_115);
if (lean_is_exclusive(x_2)) {
 lean_ctor_release(x_2, 0);
 lean_ctor_release(x_2, 1);
 x_116 = x_2;
} else {
 lean_dec_ref(x_2);
 x_116 = lean_box(0);
}
x_117 = lean_ctor_get(x_3, 0);
lean_inc(x_117);
if (lean_is_exclusive(x_3)) {
 lean_ctor_release(x_3, 0);
 lean_ctor_release(x_3, 1);
 x_118 = x_3;
} else {
 lean_dec_ref(x_3);
 x_118 = lean_box(0);
}
x_119 = lean_ctor_get(x_4, 0);
lean_inc(x_119);
x_120 = lean_ctor_get(x_4, 1);
lean_inc(x_120);
if (lean_is_exclusive(x_4)) {
 lean_ctor_release(x_4, 0);
 lean_ctor_release(x_4, 1);
 x_121 = x_4;
} else {
 lean_dec_ref(x_4);
 x_121 = lean_box(0);
}
x_122 = lean_ctor_get(x_113, 5);
lean_inc(x_122);
x_123 = lean_ctor_get(x_113, 6);
lean_inc(x_123);
lean_dec(x_113);
x_124 = lean_box(0);
x_125 = l_List_lengthTR___redArg(x_117);
x_126 = lean_uint8_of_nat(x_125);
lean_dec(x_125);
x_127 = lean_box(x_126);
x_128 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_128, 0, x_127);
lean_ctor_set(x_128, 1, x_124);
x_129 = l_List_appendTR___redArg(x_115, x_128);
x_130 = l_List_lengthTR___redArg(x_122);
x_131 = lean_uint8_of_nat(x_130);
lean_dec(x_130);
x_132 = lean_box(x_131);
x_133 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_133, 0, x_132);
lean_ctor_set(x_133, 1, x_124);
x_134 = l_List_appendTR___redArg(x_119, x_133);
x_135 = lean_uint8_of_nat(x_123);
lean_dec(x_123);
x_136 = lean_box(x_135);
x_137 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_137, 0, x_136);
lean_ctor_set(x_137, 1, x_124);
x_138 = l_List_appendTR___redArg(x_120, x_137);
x_139 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__0(x_122, x_124);
x_140 = l_List_appendTR___redArg(x_117, x_139);
if (lean_is_scalar(x_121)) {
 x_141 = lean_alloc_ctor(0, 2, 0);
} else {
 x_141 = x_121;
}
lean_ctor_set(x_141, 0, x_134);
lean_ctor_set(x_141, 1, x_138);
if (lean_is_scalar(x_118)) {
 x_142 = lean_alloc_ctor(0, 2, 0);
} else {
 x_142 = x_118;
}
lean_ctor_set(x_142, 0, x_140);
lean_ctor_set(x_142, 1, x_141);
if (lean_is_scalar(x_116)) {
 x_143 = lean_alloc_ctor(0, 2, 0);
} else {
 x_143 = x_116;
}
lean_ctor_set(x_143, 0, x_129);
lean_ctor_set(x_143, 1, x_142);
x_1 = x_114;
x_2 = x_143;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_11; 
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_2, 2);
x_11 = lean_nat_dec_lt(x_4, x_5);
if (x_11 == 0)
{
lean_dec(x_4);
return x_3;
}
else
{
lean_object* x_12; 
lean_inc(x_4);
x_12 = l_List_get_x3fInternal___redArg(x_1, x_4);
if (lean_obj_tag(x_12) == 0)
{
x_7 = x_3;
goto block_10;
}
else
{
lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; 
x_13 = lean_ctor_get(x_12, 0);
lean_inc(x_13);
lean_dec_ref(x_12);
x_14 = lean_ctor_get(x_13, 1);
lean_inc(x_14);
lean_dec(x_13);
x_15 = lean_uint8_of_nat(x_14);
lean_dec(x_14);
x_16 = ((lean_object*)(lp_sidfinity_MV3_emitDynRefLoad___closed__0));
lean_inc(x_4);
x_17 = l_Nat_reprFast(x_4);
x_18 = lean_string_append(x_16, x_17);
lean_dec_ref(x_17);
lean_inc_ref(x_18);
x_19 = lp_sidfinity_MV3_CodeBuilder_label(x_3, x_18);
x_20 = ((lean_object*)(lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__0));
lean_inc_ref(x_18);
x_21 = lean_string_append(x_18, x_20);
x_22 = lp_sidfinity_MV3_CodeBuilder_label(x_19, x_21);
x_23 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_22, x_15);
x_24 = ((lean_object*)(lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__1));
lean_inc_ref(x_18);
x_25 = lean_string_append(x_18, x_24);
x_26 = lp_sidfinity_MV3_CodeBuilder_label(x_23, x_25);
x_27 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_26, x_15);
x_28 = ((lean_object*)(lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___closed__2));
x_29 = lean_string_append(x_18, x_28);
x_30 = lp_sidfinity_MV3_CodeBuilder_label(x_27, x_29);
x_31 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_30, x_15);
x_7 = x_31;
goto block_10;
}
}
block_10:
{
lean_object* x_8; 
x_8 = lean_nat_add(x_4, x_6);
lean_dec(x_4);
x_3 = x_7;
x_4 = x_8;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__20(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; uint8_t x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get_uint8(x_4, sizeof(void*)*14 + 2);
lean_dec(x_4);
if (x_12 == 0)
{
uint8_t x_13; 
x_13 = 0;
x_7 = x_13;
goto block_11;
}
else
{
uint8_t x_14; 
x_14 = 1;
x_7 = x_14;
goto block_11;
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__15(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get(x_4, 8);
lean_inc(x_12);
lean_dec(x_4);
if (lean_obj_tag(x_12) == 1)
{
lean_object* x_13; lean_object* x_14; 
x_13 = lean_ctor_get(x_12, 0);
lean_inc(x_13);
lean_dec_ref(x_12);
x_14 = lean_ctor_get(x_13, 0);
lean_inc_ref(x_14);
lean_dec(x_13);
if (lean_obj_tag(x_14) == 1)
{
lean_object* x_15; uint8_t x_16; 
x_15 = lean_ctor_get(x_14, 1);
lean_inc(x_15);
lean_dec_ref(x_14);
x_16 = lean_uint8_of_nat(x_15);
lean_dec(x_15);
x_7 = x_16;
goto block_11;
}
else
{
uint8_t x_17; 
lean_dec_ref(x_14);
x_17 = 0;
x_7 = x_17;
goto block_11;
}
}
else
{
uint8_t x_18; 
lean_dec(x_12);
x_18 = 0;
x_7 = x_18;
goto block_11;
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__13(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get(x_4, 8);
lean_inc(x_12);
lean_dec(x_4);
if (lean_obj_tag(x_12) == 0)
{
uint8_t x_13; 
x_13 = 0;
x_7 = x_13;
goto block_11;
}
else
{
lean_object* x_14; lean_object* x_15; 
x_14 = lean_ctor_get(x_12, 0);
lean_inc(x_14);
lean_dec_ref(x_12);
x_15 = lean_ctor_get(x_14, 0);
lean_inc_ref(x_15);
lean_dec(x_14);
if (lean_obj_tag(x_15) == 2)
{
uint8_t x_16; 
lean_dec_ref(x_15);
x_16 = 0;
x_7 = x_16;
goto block_11;
}
else
{
lean_object* x_17; uint8_t x_18; 
x_17 = lean_ctor_get(x_15, 0);
lean_inc(x_17);
lean_dec_ref(x_15);
x_18 = lean_uint8_of_nat(x_17);
lean_dec(x_17);
x_7 = x_18;
goto block_11;
}
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__12(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_5, 4);
lean_inc(x_7);
lean_dec(x_5);
x_8 = lean_uint8_of_nat(x_7);
lean_dec(x_7);
x_9 = lean_box(x_8);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_9);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; 
x_11 = lean_ctor_get(x_1, 0);
x_12 = lean_ctor_get(x_1, 1);
lean_inc(x_12);
lean_inc(x_11);
lean_dec(x_1);
x_13 = lean_ctor_get(x_11, 4);
lean_inc(x_13);
lean_dec(x_11);
x_14 = lean_uint8_of_nat(x_13);
lean_dec(x_13);
x_15 = lean_box(x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_2);
x_1 = x_12;
x_2 = x_16;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__9(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_5, 1);
lean_inc(x_7);
lean_dec(x_5);
x_8 = lean_uint8_of_nat(x_7);
lean_dec(x_7);
x_9 = lean_box(x_8);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_9);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; lean_object* x_16; 
x_11 = lean_ctor_get(x_1, 0);
x_12 = lean_ctor_get(x_1, 1);
lean_inc(x_12);
lean_inc(x_11);
lean_dec(x_1);
x_13 = lean_ctor_get(x_11, 1);
lean_inc(x_13);
lean_dec(x_11);
x_14 = lean_uint8_of_nat(x_13);
lean_dec(x_13);
x_15 = lean_box(x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_2);
x_1 = x_12;
x_2 = x_16;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__18(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; 
x_4 = lean_ctor_get(x_1, 0);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 1);
lean_inc(x_5);
if (lean_is_exclusive(x_1)) {
 lean_ctor_release(x_1, 0);
 lean_ctor_release(x_1, 1);
 x_6 = x_1;
} else {
 lean_dec_ref(x_1);
 x_6 = lean_box(0);
}
x_12 = lean_ctor_get(x_4, 11);
lean_inc(x_12);
lean_dec(x_4);
if (lean_obj_tag(x_12) == 0)
{
uint8_t x_13; 
x_13 = 0;
x_7 = x_13;
goto block_11;
}
else
{
lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_14 = lean_ctor_get(x_12, 0);
lean_inc(x_14);
lean_dec_ref(x_12);
x_15 = lean_ctor_get(x_14, 0);
lean_inc(x_15);
lean_dec(x_14);
x_16 = lean_unsigned_to_nat(1u);
x_17 = l_List_get_x3fInternal___redArg(x_15, x_16);
lean_dec(x_15);
if (lean_obj_tag(x_17) == 0)
{
uint8_t x_18; 
x_18 = 0;
x_7 = x_18;
goto block_11;
}
else
{
lean_object* x_19; lean_object* x_20; uint8_t x_21; 
x_19 = lean_ctor_get(x_17, 0);
lean_inc(x_19);
lean_dec_ref(x_17);
x_20 = l_Int_toNat(x_19);
lean_dec(x_19);
x_21 = lean_uint8_of_nat(x_20);
lean_dec(x_20);
x_7 = x_21;
goto block_11;
}
}
block_11:
{
lean_object* x_8; lean_object* x_9; 
x_8 = lean_box(x_7);
if (lean_is_scalar(x_6)) {
 x_9 = lean_alloc_ctor(1, 2, 0);
} else {
 x_9 = x_6;
}
lean_ctor_set(x_9, 0, x_8);
lean_ctor_set(x_9, 1, x_2);
x_1 = x_5;
x_2 = x_9;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_12; uint8_t x_13; lean_object* x_16; lean_object* x_26; lean_object* x_32; uint8_t x_38; 
x_6 = lean_ctor_get(x_3, 1);
x_7 = lean_ctor_get(x_3, 2);
x_38 = lean_nat_dec_lt(x_5, x_6);
if (x_38 == 0)
{
lean_dec(x_5);
return x_4;
}
else
{
uint8_t x_39; 
x_39 = l_List_elem___at___00Lean_Meta_Occurrences_contains_spec__0(x_5, x_2);
if (x_39 == 0)
{
x_32 = x_4;
goto block_37;
}
else
{
lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; 
x_40 = ((lean_object*)(lp_sidfinity_MV3_emitFreqSlotStore___closed__0));
lean_inc(x_5);
x_41 = l_Nat_reprFast(x_5);
x_42 = lean_string_append(x_40, x_41);
lean_dec_ref(x_41);
x_43 = lp_sidfinity_MV3_CodeBuilder_label(x_4, x_42);
x_32 = x_43;
goto block_37;
}
}
block_11:
{
lean_object* x_9; 
x_9 = lean_nat_add(x_5, x_7);
lean_dec(x_5);
x_4 = x_8;
x_5 = x_9;
goto _start;
}
block_15:
{
lean_object* x_14; 
x_14 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_12, x_13);
x_8 = x_14;
goto block_11;
}
block_25:
{
lean_object* x_17; 
lean_inc(x_5);
x_17 = l_List_get_x3fInternal___redArg(x_1, x_5);
if (lean_obj_tag(x_17) == 0)
{
uint8_t x_18; lean_object* x_19; 
x_18 = 0;
x_19 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_16, x_18);
x_8 = x_19;
goto block_11;
}
else
{
lean_object* x_20; uint8_t x_21; 
x_20 = lean_ctor_get(x_17, 0);
lean_inc(x_20);
lean_dec_ref(x_17);
x_21 = l_List_elem___at___00Lean_Meta_Occurrences_contains_spec__0(x_5, x_2);
if (x_21 == 0)
{
lean_object* x_22; uint8_t x_23; 
x_22 = lean_ctor_get(x_20, 1);
lean_inc(x_22);
lean_dec(x_20);
x_23 = lean_uint8_of_nat(x_22);
lean_dec(x_22);
x_12 = x_16;
x_13 = x_23;
goto block_15;
}
else
{
uint8_t x_24; 
lean_dec(x_20);
x_24 = 0;
x_12 = x_16;
x_13 = x_24;
goto block_15;
}
}
}
block_31:
{
lean_object* x_27; uint8_t x_28; 
x_27 = lean_unsigned_to_nat(106u);
x_28 = lean_nat_dec_eq(x_5, x_27);
if (x_28 == 0)
{
x_16 = x_26;
goto block_25;
}
else
{
lean_object* x_29; lean_object* x_30; 
x_29 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__10));
x_30 = lp_sidfinity_MV3_CodeBuilder_label(x_26, x_29);
x_16 = x_30;
goto block_25;
}
}
block_37:
{
lean_object* x_33; uint8_t x_34; 
x_33 = lean_unsigned_to_nat(105u);
x_34 = lean_nat_dec_eq(x_5, x_33);
if (x_34 == 0)
{
x_26 = x_32;
goto block_31;
}
else
{
lean_object* x_35; lean_object* x_36; 
x_35 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__4));
x_36 = lp_sidfinity_MV3_CodeBuilder_label(x_32, x_35);
x_26 = x_36;
goto block_31;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__2(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = l_List_reverse___redArg(x_2);
return x_3;
}
else
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_5, 0);
lean_inc(x_7);
lean_dec(x_5);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_7);
{
lean_object* _tmp_0 = x_6;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_9 = lean_ctor_get(x_1, 0);
x_10 = lean_ctor_get(x_1, 1);
lean_inc(x_10);
lean_inc(x_9);
lean_dec(x_1);
x_11 = lean_ctor_get(x_9, 0);
lean_inc(x_11);
lean_dec(x_9);
x_12 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_12, 0, x_11);
lean_ctor_set(x_12, 1, x_2);
x_1 = x_10;
x_2 = x_12;
goto _start;
}
}
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__1(void) {
_start:
{
lean_object* x_1; uint16_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_box(0);
x_2 = 4096;
x_3 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__0, &lp_sidfinity_MV3_generateSID___redArg___closed__0_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__0);
x_4 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
lean_ctor_set(x_4, 2, x_1);
lean_ctor_set(x_4, 3, x_1);
lean_ctor_set_uint16(x_4, sizeof(void*)*4, x_2);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__2(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = ((lean_object*)(lp_sidfinity_MV3_emitInit___closed__0));
x_2 = 32;
x_3 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__1, &lp_sidfinity_MV3_generateSID___redArg___closed__1_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__1);
x_4 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_3, x_2, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__3(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = ((lean_object*)(lp_sidfinity_MV3_emitPlayHeader___closed__0));
x_2 = 32;
x_3 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__2, &lp_sidfinity_MV3_generateSID___redArg___closed__2_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__2);
x_4 = lp_sidfinity_MV3_CodeBuilder_emitJmpLabel(x_3, x_2, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__11(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_box(0);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__12(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__11, &lp_sidfinity_MV3_generateSID___redArg___closed__11_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__11);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__13(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__12, &lp_sidfinity_MV3_generateSID___redArg___closed__12_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__12);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__25(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__12, &lp_sidfinity_MV3_generateSID___redArg___closed__12_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__12);
x_2 = 1;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__26(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_box(0);
x_2 = 29;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__27(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__26, &lp_sidfinity_MV3_generateSID___redArg___closed__26_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__26);
x_2 = 1;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__28(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__27, &lp_sidfinity_MV3_generateSID___redArg___closed__27_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__27);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__29(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_box(0);
x_2 = 14;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__30(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__29, &lp_sidfinity_MV3_generateSID___redArg___closed__29_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__29);
x_2 = 7;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_sidfinity_MV3_generateSID___redArg___closed__31(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__30, &lp_sidfinity_MV3_generateSID___redArg___closed__30_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__30);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_generateSID___redArg(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; uint8_t x_25; 
x_2 = 4096;
x_3 = lean_unsigned_to_nat(0u);
x_4 = lean_box(0);
x_5 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__3, &lp_sidfinity_MV3_generateSID___redArg___closed__3_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__3);
x_6 = lp_sidfinity_MV3_emitInit(x_5, x_1);
x_7 = lean_ctor_get(x_1, 7);
x_8 = lean_ctor_get(x_1, 0);
lean_inc(x_8);
x_9 = lean_ctor_get(x_1, 1);
lean_inc(x_9);
x_10 = lean_ctor_get(x_1, 2);
lean_inc(x_10);
x_11 = lean_ctor_get(x_1, 3);
lean_inc(x_11);
x_12 = lean_ctor_get(x_7, 0);
lean_inc(x_12);
x_13 = lean_ctor_get(x_7, 3);
lean_inc(x_13);
lean_inc_ref(x_1);
x_14 = lp_sidfinity_MV3_emitPlay(x_6, x_1);
x_15 = l_List_lengthTR___redArg(x_8);
x_16 = lean_unsigned_to_nat(1u);
x_17 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_17, 0, x_3);
lean_ctor_set(x_17, 1, x_15);
lean_ctor_set(x_17, 2, x_16);
x_18 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__4));
x_19 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__6));
lean_inc(x_9);
x_20 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7___redArg(x_9, x_19);
x_21 = lean_ctor_get(x_20, 1);
lean_inc(x_21);
x_22 = lean_ctor_get(x_21, 1);
lean_inc(x_22);
x_23 = lean_ctor_get(x_20, 0);
lean_inc(x_23);
lean_dec_ref(x_20);
x_24 = lean_ctor_get(x_21, 0);
lean_inc(x_24);
lean_dec(x_21);
x_25 = !lean_is_exclusive(x_22);
if (x_25 == 0)
{
lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; uint8_t x_103; 
x_26 = lean_ctor_get(x_22, 0);
x_27 = lean_ctor_get(x_22, 1);
x_28 = lp_sidfinity_MV3_emitExecVoice(x_14, x_1);
x_29 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__2(x_13, x_4);
x_30 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_31 = lp_sidfinity_MV3_CodeBuilder_label(x_28, x_30);
x_32 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg(x_8, x_29, x_17, x_31, x_3);
x_33 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_34 = lp_sidfinity_MV3_CodeBuilder_label(x_32, x_33);
x_35 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg(x_8, x_29, x_17, x_34, x_3);
lean_dec_ref(x_17);
lean_dec(x_29);
lean_dec(x_8);
x_36 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__7));
x_37 = lp_sidfinity_MV3_CodeBuilder_label(x_35, x_36);
x_38 = lp_sidfinity_MV3_CodeBuilder_emitData(x_37, x_24);
x_39 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__8));
x_40 = lp_sidfinity_MV3_CodeBuilder_label(x_38, x_39);
x_41 = lp_sidfinity_MV3_CodeBuilder_emitData(x_40, x_23);
x_42 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__9));
x_43 = lp_sidfinity_MV3_CodeBuilder_label(x_41, x_42);
x_44 = lp_sidfinity_MV3_CodeBuilder_emitData(x_43, x_26);
x_45 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__10));
x_46 = lp_sidfinity_MV3_CodeBuilder_label(x_44, x_45);
x_47 = lp_sidfinity_MV3_CodeBuilder_emitData(x_46, x_27);
x_48 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_49 = lp_sidfinity_MV3_CodeBuilder_label(x_47, x_48);
lean_inc(x_9);
x_50 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__8(x_9, x_4);
x_51 = lp_sidfinity_MV3_CodeBuilder_emitData(x_49, x_50);
x_52 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0));
x_53 = lp_sidfinity_MV3_CodeBuilder_label(x_51, x_52);
lean_inc(x_9);
x_54 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__9(x_9, x_4);
x_55 = lp_sidfinity_MV3_CodeBuilder_emitData(x_53, x_54);
x_56 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2));
x_57 = lp_sidfinity_MV3_CodeBuilder_label(x_55, x_56);
lean_inc(x_9);
x_58 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__10(x_9, x_4);
x_59 = lp_sidfinity_MV3_CodeBuilder_emitData(x_57, x_58);
x_60 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__4));
x_61 = lp_sidfinity_MV3_CodeBuilder_label(x_59, x_60);
lean_inc(x_9);
x_62 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__11(x_9, x_4);
x_63 = lp_sidfinity_MV3_CodeBuilder_emitData(x_61, x_62);
x_64 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__6));
x_65 = lp_sidfinity_MV3_CodeBuilder_label(x_63, x_64);
lean_inc(x_9);
x_66 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__12(x_9, x_4);
x_67 = lp_sidfinity_MV3_CodeBuilder_emitData(x_65, x_66);
x_68 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0));
x_69 = lp_sidfinity_MV3_CodeBuilder_label(x_67, x_68);
lean_inc(x_9);
x_70 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__13(x_9, x_4);
x_71 = lp_sidfinity_MV3_CodeBuilder_emitData(x_69, x_70);
x_72 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__4));
x_73 = lp_sidfinity_MV3_CodeBuilder_label(x_71, x_72);
lean_inc(x_9);
x_74 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__14(x_9, x_4);
x_75 = lp_sidfinity_MV3_CodeBuilder_emitData(x_73, x_74);
x_76 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__18));
x_77 = lp_sidfinity_MV3_CodeBuilder_label(x_75, x_76);
lean_inc(x_9);
x_78 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__15(x_9, x_4);
x_79 = lp_sidfinity_MV3_CodeBuilder_emitData(x_77, x_78);
x_80 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__13));
x_81 = lp_sidfinity_MV3_CodeBuilder_label(x_79, x_80);
lean_inc(x_9);
x_82 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__16(x_9, x_4);
x_83 = lp_sidfinity_MV3_CodeBuilder_emitData(x_81, x_82);
x_84 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__0));
x_85 = lp_sidfinity_MV3_CodeBuilder_label(x_83, x_84);
lean_inc(x_9);
x_86 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__17(x_9, x_4);
x_87 = lp_sidfinity_MV3_CodeBuilder_emitData(x_85, x_86);
x_88 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_89 = lp_sidfinity_MV3_CodeBuilder_label(x_87, x_88);
lean_inc(x_9);
x_90 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__18(x_9, x_4);
x_91 = lp_sidfinity_MV3_CodeBuilder_emitData(x_89, x_90);
x_92 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_93 = lp_sidfinity_MV3_CodeBuilder_label(x_91, x_92);
lean_inc(x_9);
x_94 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__19(x_9, x_4);
x_95 = lp_sidfinity_MV3_CodeBuilder_emitData(x_93, x_94);
x_96 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_97 = lp_sidfinity_MV3_CodeBuilder_label(x_95, x_96);
x_98 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__20(x_9, x_4);
x_99 = lp_sidfinity_MV3_CodeBuilder_emitData(x_97, x_98);
lean_ctor_set(x_22, 1, x_18);
lean_ctor_set(x_22, 0, x_99);
x_100 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21___redArg(x_10, x_22);
x_101 = lean_ctor_get(x_100, 1);
lean_inc(x_101);
x_102 = lean_ctor_get(x_100, 0);
lean_inc(x_102);
lean_dec_ref(x_100);
x_103 = !lean_is_exclusive(x_101);
if (x_103 == 0)
{
lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; uint8_t x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; lean_object* x_139; lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; lean_object* x_150; lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_154; lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; lean_object* x_191; lean_object* x_192; lean_object* x_193; lean_object* x_194; lean_object* x_195; lean_object* x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; lean_object* x_202; lean_object* x_203; lean_object* x_204; lean_object* x_205; lean_object* x_206; lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; lean_object* x_214; lean_object* x_215; lean_object* x_216; lean_object* x_217; lean_object* x_218; lean_object* x_219; lean_object* x_220; lean_object* x_221; lean_object* x_222; lean_object* x_223; lean_object* x_224; lean_object* x_225; lean_object* x_226; uint16_t x_227; uint16_t x_228; uint16_t x_229; uint16_t x_230; lean_object* x_231; uint16_t x_232; uint16_t x_233; uint32_t x_234; lean_object* x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; lean_object* x_239; 
x_104 = lean_ctor_get(x_101, 0);
x_105 = lean_ctor_get(x_101, 1);
x_106 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__2));
x_107 = lp_sidfinity_MV3_CodeBuilder_label(x_102, x_106);
x_108 = lp_sidfinity_MV3_CodeBuilder_emitData(x_107, x_105);
x_109 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__3));
x_110 = lp_sidfinity_MV3_CodeBuilder_label(x_108, x_109);
x_111 = lp_sidfinity_MV3_CodeBuilder_emitData(x_110, x_104);
lean_ctor_set(x_101, 1, x_18);
lean_ctor_set(x_101, 0, x_111);
x_112 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg(x_11, x_101);
x_113 = lean_ctor_get(x_112, 1);
lean_inc(x_113);
x_114 = lean_ctor_get(x_112, 0);
lean_inc(x_114);
lean_dec_ref(x_112);
x_115 = lean_ctor_get(x_113, 0);
lean_inc(x_115);
x_116 = lean_ctor_get(x_113, 1);
lean_inc(x_116);
lean_dec(x_113);
x_117 = 0;
x_118 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__13, &lp_sidfinity_MV3_generateSID___redArg___closed__13_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__13);
x_119 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_120 = lp_sidfinity_MV3_CodeBuilder_label(x_114, x_119);
x_121 = lp_sidfinity_MV3_CodeBuilder_emitData(x_120, x_118);
x_122 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__5));
x_123 = lp_sidfinity_MV3_CodeBuilder_label(x_121, x_122);
x_124 = lp_sidfinity_MV3_CodeBuilder_emitData(x_123, x_118);
x_125 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__6));
x_126 = lp_sidfinity_MV3_CodeBuilder_label(x_124, x_125);
x_127 = lp_sidfinity_MV3_CodeBuilder_emitData(x_126, x_118);
x_128 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__3));
x_129 = lp_sidfinity_MV3_CodeBuilder_label(x_127, x_128);
x_130 = lp_sidfinity_MV3_CodeBuilder_emitData(x_129, x_118);
x_131 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0));
x_132 = lp_sidfinity_MV3_CodeBuilder_label(x_130, x_131);
x_133 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__14));
x_134 = lp_sidfinity_MV3_CodeBuilder_label(x_132, x_133);
x_135 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_134, x_117);
x_136 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__15));
x_137 = lp_sidfinity_MV3_CodeBuilder_label(x_135, x_136);
x_138 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_137, x_117);
x_139 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__16));
x_140 = lp_sidfinity_MV3_CodeBuilder_label(x_138, x_139);
x_141 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_140, x_117);
x_142 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__4));
x_143 = lp_sidfinity_MV3_CodeBuilder_label(x_141, x_142);
x_144 = lp_sidfinity_MV3_CodeBuilder_emitData(x_143, x_118);
x_145 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3));
x_146 = lp_sidfinity_MV3_CodeBuilder_label(x_144, x_145);
x_147 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__17));
x_148 = lp_sidfinity_MV3_CodeBuilder_label(x_146, x_147);
x_149 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_148, x_117);
x_150 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__18));
x_151 = lp_sidfinity_MV3_CodeBuilder_label(x_149, x_150);
x_152 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_151, x_117);
x_153 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__19));
x_154 = lp_sidfinity_MV3_CodeBuilder_label(x_152, x_153);
x_155 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_154, x_117);
x_156 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_157 = lp_sidfinity_MV3_CodeBuilder_label(x_155, x_156);
x_158 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__20));
x_159 = lp_sidfinity_MV3_CodeBuilder_label(x_157, x_158);
x_160 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_159, x_117);
x_161 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__21));
x_162 = lp_sidfinity_MV3_CodeBuilder_label(x_160, x_161);
x_163 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_162, x_117);
x_164 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__22));
x_165 = lp_sidfinity_MV3_CodeBuilder_label(x_163, x_164);
x_166 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_165, x_117);
x_167 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_168 = lp_sidfinity_MV3_CodeBuilder_label(x_166, x_167);
x_169 = lp_sidfinity_MV3_CodeBuilder_emitData(x_168, x_118);
x_170 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_171 = lp_sidfinity_MV3_CodeBuilder_label(x_169, x_170);
x_172 = lp_sidfinity_MV3_CodeBuilder_emitData(x_171, x_118);
x_173 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__23));
x_174 = lp_sidfinity_MV3_CodeBuilder_label(x_172, x_173);
x_175 = lp_sidfinity_MV3_CodeBuilder_emitData(x_174, x_118);
x_176 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__24));
x_177 = lp_sidfinity_MV3_CodeBuilder_label(x_175, x_176);
x_178 = lp_sidfinity_MV3_CodeBuilder_emitData(x_177, x_118);
x_179 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__9));
x_180 = lp_sidfinity_MV3_CodeBuilder_label(x_178, x_179);
x_181 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__25, &lp_sidfinity_MV3_generateSID___redArg___closed__25_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__25);
x_182 = lp_sidfinity_MV3_CodeBuilder_emitData(x_180, x_181);
x_183 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1));
x_184 = lp_sidfinity_MV3_CodeBuilder_label(x_182, x_183);
x_185 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__28, &lp_sidfinity_MV3_generateSID___redArg___closed__28_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__28);
x_186 = lp_sidfinity_MV3_CodeBuilder_emitData(x_184, x_185);
x_187 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1));
x_188 = lp_sidfinity_MV3_CodeBuilder_label(x_186, x_187);
x_189 = lp_sidfinity_MV3_CodeBuilder_emitData(x_188, x_118);
x_190 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3));
x_191 = lp_sidfinity_MV3_CodeBuilder_label(x_189, x_190);
x_192 = lp_sidfinity_MV3_CodeBuilder_emitData(x_191, x_118);
x_193 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2));
x_194 = lp_sidfinity_MV3_CodeBuilder_label(x_192, x_193);
x_195 = lp_sidfinity_MV3_CodeBuilder_emitData(x_194, x_118);
x_196 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__2));
x_197 = lp_sidfinity_MV3_CodeBuilder_label(x_195, x_196);
x_198 = lp_sidfinity_MV3_CodeBuilder_emitData(x_197, x_118);
x_199 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__4));
x_200 = lp_sidfinity_MV3_CodeBuilder_label(x_198, x_199);
x_201 = lp_sidfinity_MV3_CodeBuilder_emitData(x_200, x_118);
x_202 = l_List_lengthTR___redArg(x_12);
x_203 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_203, 0, x_3);
lean_ctor_set(x_203, 1, x_202);
lean_ctor_set(x_203, 2, x_16);
x_204 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg(x_12, x_203, x_201, x_3);
lean_dec_ref(x_203);
lean_dec(x_12);
x_205 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_206 = lp_sidfinity_MV3_CodeBuilder_label(x_204, x_205);
x_207 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__31, &lp_sidfinity_MV3_generateSID___redArg___closed__31_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__31);
x_208 = lp_sidfinity_MV3_CodeBuilder_emitData(x_206, x_207);
x_209 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3));
x_210 = lp_sidfinity_MV3_CodeBuilder_label(x_208, x_209);
x_211 = lp_sidfinity_MV3_CodeBuilder_emitData(x_210, x_118);
x_212 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5));
x_213 = lp_sidfinity_MV3_CodeBuilder_label(x_211, x_212);
x_214 = lp_sidfinity_MV3_CodeBuilder_emitData(x_213, x_118);
x_215 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__2));
x_216 = lp_sidfinity_MV3_CodeBuilder_label(x_214, x_215);
x_217 = lp_sidfinity_MV3_CodeBuilder_emitData(x_216, x_116);
x_218 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__4));
x_219 = lp_sidfinity_MV3_CodeBuilder_label(x_217, x_218);
x_220 = lp_sidfinity_MV3_CodeBuilder_emitData(x_219, x_115);
x_221 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__32));
x_222 = lp_sidfinity_MV3_CodeBuilder_label(x_220, x_221);
lean_inc(x_11);
x_223 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__24(x_11, x_4);
x_224 = lp_sidfinity_MV3_CodeBuilder_emitData(x_222, x_223);
x_225 = lp_sidfinity_MV3_CodeBuilder_resolve(x_224);
x_226 = lean_ctor_get(x_225, 0);
lean_inc_ref(x_226);
lean_dec_ref(x_225);
x_227 = 2;
x_228 = 124;
x_229 = 0;
x_230 = 4099;
x_231 = l_List_lengthTR___redArg(x_11);
lean_dec(x_11);
x_232 = lean_uint16_of_nat(x_231);
lean_dec(x_231);
x_233 = 1;
x_234 = 0;
x_235 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__33));
x_236 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__34));
x_237 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__35));
x_238 = lean_alloc_ctor(0, 3, 18);
lean_ctor_set(x_238, 0, x_235);
lean_ctor_set(x_238, 1, x_236);
lean_ctor_set(x_238, 2, x_237);
lean_ctor_set_uint16(x_238, sizeof(void*)*3 + 4, x_227);
lean_ctor_set_uint16(x_238, sizeof(void*)*3 + 6, x_228);
lean_ctor_set_uint16(x_238, sizeof(void*)*3 + 8, x_229);
lean_ctor_set_uint16(x_238, sizeof(void*)*3 + 10, x_2);
lean_ctor_set_uint16(x_238, sizeof(void*)*3 + 12, x_230);
lean_ctor_set_uint16(x_238, sizeof(void*)*3 + 14, x_232);
lean_ctor_set_uint16(x_238, sizeof(void*)*3 + 16, x_233);
lean_ctor_set_uint32(x_238, sizeof(void*)*3, x_234);
x_239 = lp_sidfinity_buildSID(x_238, x_226);
lean_dec_ref(x_226);
lean_dec_ref(x_238);
return x_239;
}
else
{
lean_object* x_240; lean_object* x_241; lean_object* x_242; lean_object* x_243; lean_object* x_244; lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; lean_object* x_249; lean_object* x_250; lean_object* x_251; lean_object* x_252; lean_object* x_253; uint8_t x_254; lean_object* x_255; lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; lean_object* x_265; lean_object* x_266; lean_object* x_267; lean_object* x_268; lean_object* x_269; lean_object* x_270; lean_object* x_271; lean_object* x_272; lean_object* x_273; lean_object* x_274; lean_object* x_275; lean_object* x_276; lean_object* x_277; lean_object* x_278; lean_object* x_279; lean_object* x_280; lean_object* x_281; lean_object* x_282; lean_object* x_283; lean_object* x_284; lean_object* x_285; lean_object* x_286; lean_object* x_287; lean_object* x_288; lean_object* x_289; lean_object* x_290; lean_object* x_291; lean_object* x_292; lean_object* x_293; lean_object* x_294; lean_object* x_295; lean_object* x_296; lean_object* x_297; lean_object* x_298; lean_object* x_299; lean_object* x_300; lean_object* x_301; lean_object* x_302; lean_object* x_303; lean_object* x_304; lean_object* x_305; lean_object* x_306; lean_object* x_307; lean_object* x_308; lean_object* x_309; lean_object* x_310; lean_object* x_311; lean_object* x_312; lean_object* x_313; lean_object* x_314; lean_object* x_315; lean_object* x_316; lean_object* x_317; lean_object* x_318; lean_object* x_319; lean_object* x_320; lean_object* x_321; lean_object* x_322; lean_object* x_323; lean_object* x_324; lean_object* x_325; lean_object* x_326; lean_object* x_327; lean_object* x_328; lean_object* x_329; lean_object* x_330; lean_object* x_331; lean_object* x_332; lean_object* x_333; lean_object* x_334; lean_object* x_335; lean_object* x_336; lean_object* x_337; lean_object* x_338; lean_object* x_339; lean_object* x_340; lean_object* x_341; lean_object* x_342; lean_object* x_343; lean_object* x_344; lean_object* x_345; lean_object* x_346; lean_object* x_347; lean_object* x_348; lean_object* x_349; lean_object* x_350; lean_object* x_351; lean_object* x_352; lean_object* x_353; lean_object* x_354; lean_object* x_355; lean_object* x_356; lean_object* x_357; lean_object* x_358; lean_object* x_359; lean_object* x_360; lean_object* x_361; lean_object* x_362; lean_object* x_363; uint16_t x_364; uint16_t x_365; uint16_t x_366; uint16_t x_367; lean_object* x_368; uint16_t x_369; uint16_t x_370; uint32_t x_371; lean_object* x_372; lean_object* x_373; lean_object* x_374; lean_object* x_375; lean_object* x_376; 
x_240 = lean_ctor_get(x_101, 0);
x_241 = lean_ctor_get(x_101, 1);
lean_inc(x_241);
lean_inc(x_240);
lean_dec(x_101);
x_242 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__2));
x_243 = lp_sidfinity_MV3_CodeBuilder_label(x_102, x_242);
x_244 = lp_sidfinity_MV3_CodeBuilder_emitData(x_243, x_241);
x_245 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__3));
x_246 = lp_sidfinity_MV3_CodeBuilder_label(x_244, x_245);
x_247 = lp_sidfinity_MV3_CodeBuilder_emitData(x_246, x_240);
x_248 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_248, 0, x_247);
lean_ctor_set(x_248, 1, x_18);
x_249 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg(x_11, x_248);
x_250 = lean_ctor_get(x_249, 1);
lean_inc(x_250);
x_251 = lean_ctor_get(x_249, 0);
lean_inc(x_251);
lean_dec_ref(x_249);
x_252 = lean_ctor_get(x_250, 0);
lean_inc(x_252);
x_253 = lean_ctor_get(x_250, 1);
lean_inc(x_253);
lean_dec(x_250);
x_254 = 0;
x_255 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__13, &lp_sidfinity_MV3_generateSID___redArg___closed__13_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__13);
x_256 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_257 = lp_sidfinity_MV3_CodeBuilder_label(x_251, x_256);
x_258 = lp_sidfinity_MV3_CodeBuilder_emitData(x_257, x_255);
x_259 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__5));
x_260 = lp_sidfinity_MV3_CodeBuilder_label(x_258, x_259);
x_261 = lp_sidfinity_MV3_CodeBuilder_emitData(x_260, x_255);
x_262 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__6));
x_263 = lp_sidfinity_MV3_CodeBuilder_label(x_261, x_262);
x_264 = lp_sidfinity_MV3_CodeBuilder_emitData(x_263, x_255);
x_265 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__3));
x_266 = lp_sidfinity_MV3_CodeBuilder_label(x_264, x_265);
x_267 = lp_sidfinity_MV3_CodeBuilder_emitData(x_266, x_255);
x_268 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0));
x_269 = lp_sidfinity_MV3_CodeBuilder_label(x_267, x_268);
x_270 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__14));
x_271 = lp_sidfinity_MV3_CodeBuilder_label(x_269, x_270);
x_272 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_271, x_254);
x_273 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__15));
x_274 = lp_sidfinity_MV3_CodeBuilder_label(x_272, x_273);
x_275 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_274, x_254);
x_276 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__16));
x_277 = lp_sidfinity_MV3_CodeBuilder_label(x_275, x_276);
x_278 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_277, x_254);
x_279 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__4));
x_280 = lp_sidfinity_MV3_CodeBuilder_label(x_278, x_279);
x_281 = lp_sidfinity_MV3_CodeBuilder_emitData(x_280, x_255);
x_282 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3));
x_283 = lp_sidfinity_MV3_CodeBuilder_label(x_281, x_282);
x_284 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__17));
x_285 = lp_sidfinity_MV3_CodeBuilder_label(x_283, x_284);
x_286 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_285, x_254);
x_287 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__18));
x_288 = lp_sidfinity_MV3_CodeBuilder_label(x_286, x_287);
x_289 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_288, x_254);
x_290 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__19));
x_291 = lp_sidfinity_MV3_CodeBuilder_label(x_289, x_290);
x_292 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_291, x_254);
x_293 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_294 = lp_sidfinity_MV3_CodeBuilder_label(x_292, x_293);
x_295 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__20));
x_296 = lp_sidfinity_MV3_CodeBuilder_label(x_294, x_295);
x_297 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_296, x_254);
x_298 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__21));
x_299 = lp_sidfinity_MV3_CodeBuilder_label(x_297, x_298);
x_300 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_299, x_254);
x_301 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__22));
x_302 = lp_sidfinity_MV3_CodeBuilder_label(x_300, x_301);
x_303 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_302, x_254);
x_304 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_305 = lp_sidfinity_MV3_CodeBuilder_label(x_303, x_304);
x_306 = lp_sidfinity_MV3_CodeBuilder_emitData(x_305, x_255);
x_307 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_308 = lp_sidfinity_MV3_CodeBuilder_label(x_306, x_307);
x_309 = lp_sidfinity_MV3_CodeBuilder_emitData(x_308, x_255);
x_310 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__23));
x_311 = lp_sidfinity_MV3_CodeBuilder_label(x_309, x_310);
x_312 = lp_sidfinity_MV3_CodeBuilder_emitData(x_311, x_255);
x_313 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__24));
x_314 = lp_sidfinity_MV3_CodeBuilder_label(x_312, x_313);
x_315 = lp_sidfinity_MV3_CodeBuilder_emitData(x_314, x_255);
x_316 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__9));
x_317 = lp_sidfinity_MV3_CodeBuilder_label(x_315, x_316);
x_318 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__25, &lp_sidfinity_MV3_generateSID___redArg___closed__25_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__25);
x_319 = lp_sidfinity_MV3_CodeBuilder_emitData(x_317, x_318);
x_320 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1));
x_321 = lp_sidfinity_MV3_CodeBuilder_label(x_319, x_320);
x_322 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__28, &lp_sidfinity_MV3_generateSID___redArg___closed__28_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__28);
x_323 = lp_sidfinity_MV3_CodeBuilder_emitData(x_321, x_322);
x_324 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1));
x_325 = lp_sidfinity_MV3_CodeBuilder_label(x_323, x_324);
x_326 = lp_sidfinity_MV3_CodeBuilder_emitData(x_325, x_255);
x_327 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3));
x_328 = lp_sidfinity_MV3_CodeBuilder_label(x_326, x_327);
x_329 = lp_sidfinity_MV3_CodeBuilder_emitData(x_328, x_255);
x_330 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2));
x_331 = lp_sidfinity_MV3_CodeBuilder_label(x_329, x_330);
x_332 = lp_sidfinity_MV3_CodeBuilder_emitData(x_331, x_255);
x_333 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__2));
x_334 = lp_sidfinity_MV3_CodeBuilder_label(x_332, x_333);
x_335 = lp_sidfinity_MV3_CodeBuilder_emitData(x_334, x_255);
x_336 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__4));
x_337 = lp_sidfinity_MV3_CodeBuilder_label(x_335, x_336);
x_338 = lp_sidfinity_MV3_CodeBuilder_emitData(x_337, x_255);
x_339 = l_List_lengthTR___redArg(x_12);
x_340 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_340, 0, x_3);
lean_ctor_set(x_340, 1, x_339);
lean_ctor_set(x_340, 2, x_16);
x_341 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg(x_12, x_340, x_338, x_3);
lean_dec_ref(x_340);
lean_dec(x_12);
x_342 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_343 = lp_sidfinity_MV3_CodeBuilder_label(x_341, x_342);
x_344 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__31, &lp_sidfinity_MV3_generateSID___redArg___closed__31_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__31);
x_345 = lp_sidfinity_MV3_CodeBuilder_emitData(x_343, x_344);
x_346 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3));
x_347 = lp_sidfinity_MV3_CodeBuilder_label(x_345, x_346);
x_348 = lp_sidfinity_MV3_CodeBuilder_emitData(x_347, x_255);
x_349 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5));
x_350 = lp_sidfinity_MV3_CodeBuilder_label(x_348, x_349);
x_351 = lp_sidfinity_MV3_CodeBuilder_emitData(x_350, x_255);
x_352 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__2));
x_353 = lp_sidfinity_MV3_CodeBuilder_label(x_351, x_352);
x_354 = lp_sidfinity_MV3_CodeBuilder_emitData(x_353, x_253);
x_355 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__4));
x_356 = lp_sidfinity_MV3_CodeBuilder_label(x_354, x_355);
x_357 = lp_sidfinity_MV3_CodeBuilder_emitData(x_356, x_252);
x_358 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__32));
x_359 = lp_sidfinity_MV3_CodeBuilder_label(x_357, x_358);
lean_inc(x_11);
x_360 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__24(x_11, x_4);
x_361 = lp_sidfinity_MV3_CodeBuilder_emitData(x_359, x_360);
x_362 = lp_sidfinity_MV3_CodeBuilder_resolve(x_361);
x_363 = lean_ctor_get(x_362, 0);
lean_inc_ref(x_363);
lean_dec_ref(x_362);
x_364 = 2;
x_365 = 124;
x_366 = 0;
x_367 = 4099;
x_368 = l_List_lengthTR___redArg(x_11);
lean_dec(x_11);
x_369 = lean_uint16_of_nat(x_368);
lean_dec(x_368);
x_370 = 1;
x_371 = 0;
x_372 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__33));
x_373 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__34));
x_374 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__35));
x_375 = lean_alloc_ctor(0, 3, 18);
lean_ctor_set(x_375, 0, x_372);
lean_ctor_set(x_375, 1, x_373);
lean_ctor_set(x_375, 2, x_374);
lean_ctor_set_uint16(x_375, sizeof(void*)*3 + 4, x_364);
lean_ctor_set_uint16(x_375, sizeof(void*)*3 + 6, x_365);
lean_ctor_set_uint16(x_375, sizeof(void*)*3 + 8, x_366);
lean_ctor_set_uint16(x_375, sizeof(void*)*3 + 10, x_2);
lean_ctor_set_uint16(x_375, sizeof(void*)*3 + 12, x_367);
lean_ctor_set_uint16(x_375, sizeof(void*)*3 + 14, x_369);
lean_ctor_set_uint16(x_375, sizeof(void*)*3 + 16, x_370);
lean_ctor_set_uint32(x_375, sizeof(void*)*3, x_371);
x_376 = lp_sidfinity_buildSID(x_375, x_363);
lean_dec_ref(x_363);
lean_dec_ref(x_375);
return x_376;
}
}
else
{
lean_object* x_377; lean_object* x_378; lean_object* x_379; lean_object* x_380; lean_object* x_381; lean_object* x_382; lean_object* x_383; lean_object* x_384; lean_object* x_385; lean_object* x_386; lean_object* x_387; lean_object* x_388; lean_object* x_389; lean_object* x_390; lean_object* x_391; lean_object* x_392; lean_object* x_393; lean_object* x_394; lean_object* x_395; lean_object* x_396; lean_object* x_397; lean_object* x_398; lean_object* x_399; lean_object* x_400; lean_object* x_401; lean_object* x_402; lean_object* x_403; lean_object* x_404; lean_object* x_405; lean_object* x_406; lean_object* x_407; lean_object* x_408; lean_object* x_409; lean_object* x_410; lean_object* x_411; lean_object* x_412; lean_object* x_413; lean_object* x_414; lean_object* x_415; lean_object* x_416; lean_object* x_417; lean_object* x_418; lean_object* x_419; lean_object* x_420; lean_object* x_421; lean_object* x_422; lean_object* x_423; lean_object* x_424; lean_object* x_425; lean_object* x_426; lean_object* x_427; lean_object* x_428; lean_object* x_429; lean_object* x_430; lean_object* x_431; lean_object* x_432; lean_object* x_433; lean_object* x_434; lean_object* x_435; lean_object* x_436; lean_object* x_437; lean_object* x_438; lean_object* x_439; lean_object* x_440; lean_object* x_441; lean_object* x_442; lean_object* x_443; lean_object* x_444; lean_object* x_445; lean_object* x_446; lean_object* x_447; lean_object* x_448; lean_object* x_449; lean_object* x_450; lean_object* x_451; lean_object* x_452; lean_object* x_453; lean_object* x_454; lean_object* x_455; lean_object* x_456; lean_object* x_457; lean_object* x_458; lean_object* x_459; lean_object* x_460; lean_object* x_461; lean_object* x_462; lean_object* x_463; lean_object* x_464; lean_object* x_465; lean_object* x_466; lean_object* x_467; lean_object* x_468; lean_object* x_469; uint8_t x_470; lean_object* x_471; lean_object* x_472; lean_object* x_473; lean_object* x_474; lean_object* x_475; lean_object* x_476; lean_object* x_477; lean_object* x_478; lean_object* x_479; lean_object* x_480; lean_object* x_481; lean_object* x_482; lean_object* x_483; lean_object* x_484; lean_object* x_485; lean_object* x_486; lean_object* x_487; lean_object* x_488; lean_object* x_489; lean_object* x_490; lean_object* x_491; lean_object* x_492; lean_object* x_493; lean_object* x_494; lean_object* x_495; lean_object* x_496; lean_object* x_497; lean_object* x_498; lean_object* x_499; lean_object* x_500; lean_object* x_501; lean_object* x_502; lean_object* x_503; lean_object* x_504; lean_object* x_505; lean_object* x_506; lean_object* x_507; lean_object* x_508; lean_object* x_509; lean_object* x_510; lean_object* x_511; lean_object* x_512; lean_object* x_513; lean_object* x_514; lean_object* x_515; lean_object* x_516; lean_object* x_517; lean_object* x_518; lean_object* x_519; lean_object* x_520; lean_object* x_521; lean_object* x_522; lean_object* x_523; lean_object* x_524; lean_object* x_525; lean_object* x_526; lean_object* x_527; lean_object* x_528; lean_object* x_529; lean_object* x_530; lean_object* x_531; lean_object* x_532; lean_object* x_533; lean_object* x_534; lean_object* x_535; lean_object* x_536; lean_object* x_537; lean_object* x_538; lean_object* x_539; lean_object* x_540; lean_object* x_541; lean_object* x_542; lean_object* x_543; lean_object* x_544; lean_object* x_545; lean_object* x_546; lean_object* x_547; lean_object* x_548; lean_object* x_549; lean_object* x_550; lean_object* x_551; lean_object* x_552; lean_object* x_553; lean_object* x_554; lean_object* x_555; lean_object* x_556; lean_object* x_557; lean_object* x_558; lean_object* x_559; lean_object* x_560; lean_object* x_561; lean_object* x_562; lean_object* x_563; lean_object* x_564; lean_object* x_565; lean_object* x_566; lean_object* x_567; lean_object* x_568; lean_object* x_569; lean_object* x_570; lean_object* x_571; lean_object* x_572; lean_object* x_573; lean_object* x_574; lean_object* x_575; lean_object* x_576; lean_object* x_577; lean_object* x_578; lean_object* x_579; uint16_t x_580; uint16_t x_581; uint16_t x_582; uint16_t x_583; lean_object* x_584; uint16_t x_585; uint16_t x_586; uint32_t x_587; lean_object* x_588; lean_object* x_589; lean_object* x_590; lean_object* x_591; lean_object* x_592; 
x_377 = lean_ctor_get(x_22, 0);
x_378 = lean_ctor_get(x_22, 1);
lean_inc(x_378);
lean_inc(x_377);
lean_dec(x_22);
x_379 = lp_sidfinity_MV3_emitExecVoice(x_14, x_1);
x_380 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__2(x_13, x_4);
x_381 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__3));
x_382 = lp_sidfinity_MV3_CodeBuilder_label(x_379, x_381);
x_383 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg(x_8, x_380, x_17, x_382, x_3);
x_384 = ((lean_object*)(lp_sidfinity_MV3_emitNL__FreqWrite___closed__1));
x_385 = lp_sidfinity_MV3_CodeBuilder_label(x_383, x_384);
x_386 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg(x_8, x_380, x_17, x_385, x_3);
lean_dec_ref(x_17);
lean_dec(x_380);
lean_dec(x_8);
x_387 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__7));
x_388 = lp_sidfinity_MV3_CodeBuilder_label(x_386, x_387);
x_389 = lp_sidfinity_MV3_CodeBuilder_emitData(x_388, x_24);
x_390 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__8));
x_391 = lp_sidfinity_MV3_CodeBuilder_label(x_389, x_390);
x_392 = lp_sidfinity_MV3_CodeBuilder_emitData(x_391, x_23);
x_393 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__9));
x_394 = lp_sidfinity_MV3_CodeBuilder_label(x_392, x_393);
x_395 = lp_sidfinity_MV3_CodeBuilder_emitData(x_394, x_377);
x_396 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__10));
x_397 = lp_sidfinity_MV3_CodeBuilder_label(x_395, x_396);
x_398 = lp_sidfinity_MV3_CodeBuilder_emitData(x_397, x_378);
x_399 = ((lean_object*)(lp_sidfinity_MV3_emitNL__CtrlWrite___closed__0));
x_400 = lp_sidfinity_MV3_CodeBuilder_label(x_398, x_399);
lean_inc(x_9);
x_401 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__8(x_9, x_4);
x_402 = lp_sidfinity_MV3_CodeBuilder_emitData(x_400, x_401);
x_403 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__0));
x_404 = lp_sidfinity_MV3_CodeBuilder_label(x_402, x_403);
lean_inc(x_9);
x_405 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__9(x_9, x_4);
x_406 = lp_sidfinity_MV3_CodeBuilder_emitData(x_404, x_405);
x_407 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__2));
x_408 = lp_sidfinity_MV3_CodeBuilder_label(x_406, x_407);
lean_inc(x_9);
x_409 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__10(x_9, x_4);
x_410 = lp_sidfinity_MV3_CodeBuilder_emitData(x_408, x_409);
x_411 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__4));
x_412 = lp_sidfinity_MV3_CodeBuilder_label(x_410, x_411);
lean_inc(x_9);
x_413 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__11(x_9, x_4);
x_414 = lp_sidfinity_MV3_CodeBuilder_emitData(x_412, x_413);
x_415 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PWADSRWrite___closed__6));
x_416 = lp_sidfinity_MV3_CodeBuilder_label(x_414, x_415);
lean_inc(x_9);
x_417 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__12(x_9, x_4);
x_418 = lp_sidfinity_MV3_CodeBuilder_emitData(x_416, x_417);
x_419 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__0));
x_420 = lp_sidfinity_MV3_CodeBuilder_label(x_418, x_419);
lean_inc(x_9);
x_421 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__13(x_9, x_4);
x_422 = lp_sidfinity_MV3_CodeBuilder_emitData(x_420, x_421);
x_423 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__4));
x_424 = lp_sidfinity_MV3_CodeBuilder_label(x_422, x_423);
lean_inc(x_9);
x_425 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__14(x_9, x_4);
x_426 = lp_sidfinity_MV3_CodeBuilder_emitData(x_424, x_425);
x_427 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__18));
x_428 = lp_sidfinity_MV3_CodeBuilder_label(x_426, x_427);
lean_inc(x_9);
x_429 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__15(x_9, x_4);
x_430 = lp_sidfinity_MV3_CodeBuilder_emitData(x_428, x_429);
x_431 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__13));
x_432 = lp_sidfinity_MV3_CodeBuilder_label(x_430, x_431);
lean_inc(x_9);
x_433 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__16(x_9, x_4);
x_434 = lp_sidfinity_MV3_CodeBuilder_emitData(x_432, x_433);
x_435 = ((lean_object*)(lp_sidfinity_MV3_emitVibrato___redArg___closed__0));
x_436 = lp_sidfinity_MV3_CodeBuilder_label(x_434, x_435);
lean_inc(x_9);
x_437 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__17(x_9, x_4);
x_438 = lp_sidfinity_MV3_CodeBuilder_emitData(x_436, x_437);
x_439 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__35));
x_440 = lp_sidfinity_MV3_CodeBuilder_label(x_438, x_439);
lean_inc(x_9);
x_441 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__18(x_9, x_4);
x_442 = lp_sidfinity_MV3_CodeBuilder_emitData(x_440, x_441);
x_443 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__19));
x_444 = lp_sidfinity_MV3_CodeBuilder_label(x_442, x_443);
lean_inc(x_9);
x_445 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__19(x_9, x_4);
x_446 = lp_sidfinity_MV3_CodeBuilder_emitData(x_444, x_445);
x_447 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__31));
x_448 = lp_sidfinity_MV3_CodeBuilder_label(x_446, x_447);
x_449 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__20(x_9, x_4);
x_450 = lp_sidfinity_MV3_CodeBuilder_emitData(x_448, x_449);
x_451 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_451, 0, x_450);
lean_ctor_set(x_451, 1, x_18);
x_452 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21___redArg(x_10, x_451);
x_453 = lean_ctor_get(x_452, 1);
lean_inc(x_453);
x_454 = lean_ctor_get(x_452, 0);
lean_inc(x_454);
lean_dec_ref(x_452);
x_455 = lean_ctor_get(x_453, 0);
lean_inc(x_455);
x_456 = lean_ctor_get(x_453, 1);
lean_inc(x_456);
if (lean_is_exclusive(x_453)) {
 lean_ctor_release(x_453, 0);
 lean_ctor_release(x_453, 1);
 x_457 = x_453;
} else {
 lean_dec_ref(x_453);
 x_457 = lean_box(0);
}
x_458 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__2));
x_459 = lp_sidfinity_MV3_CodeBuilder_label(x_454, x_458);
x_460 = lp_sidfinity_MV3_CodeBuilder_emitData(x_459, x_456);
x_461 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadAndDispatch___closed__3));
x_462 = lp_sidfinity_MV3_CodeBuilder_label(x_460, x_461);
x_463 = lp_sidfinity_MV3_CodeBuilder_emitData(x_462, x_455);
if (lean_is_scalar(x_457)) {
 x_464 = lean_alloc_ctor(0, 2, 0);
} else {
 x_464 = x_457;
}
lean_ctor_set(x_464, 0, x_463);
lean_ctor_set(x_464, 1, x_18);
x_465 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg(x_11, x_464);
x_466 = lean_ctor_get(x_465, 1);
lean_inc(x_466);
x_467 = lean_ctor_get(x_465, 0);
lean_inc(x_467);
lean_dec_ref(x_465);
x_468 = lean_ctor_get(x_466, 0);
lean_inc(x_468);
x_469 = lean_ctor_get(x_466, 1);
lean_inc(x_469);
lean_dec(x_466);
x_470 = 0;
x_471 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__13, &lp_sidfinity_MV3_generateSID___redArg___closed__13_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__13);
x_472 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__2));
x_473 = lp_sidfinity_MV3_CodeBuilder_label(x_467, x_472);
x_474 = lp_sidfinity_MV3_CodeBuilder_emitData(x_473, x_471);
x_475 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__5));
x_476 = lp_sidfinity_MV3_CodeBuilder_label(x_474, x_475);
x_477 = lp_sidfinity_MV3_CodeBuilder_emitData(x_476, x_471);
x_478 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__6));
x_479 = lp_sidfinity_MV3_CodeBuilder_label(x_477, x_478);
x_480 = lp_sidfinity_MV3_CodeBuilder_emitData(x_479, x_471);
x_481 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__3));
x_482 = lp_sidfinity_MV3_CodeBuilder_label(x_480, x_481);
x_483 = lp_sidfinity_MV3_CodeBuilder_emitData(x_482, x_471);
x_484 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SaveCtrlAndReturn___closed__0));
x_485 = lp_sidfinity_MV3_CodeBuilder_label(x_483, x_484);
x_486 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__14));
x_487 = lp_sidfinity_MV3_CodeBuilder_label(x_485, x_486);
x_488 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_487, x_470);
x_489 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__15));
x_490 = lp_sidfinity_MV3_CodeBuilder_label(x_488, x_489);
x_491 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_490, x_470);
x_492 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__16));
x_493 = lp_sidfinity_MV3_CodeBuilder_label(x_491, x_492);
x_494 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_493, x_470);
x_495 = ((lean_object*)(lp_sidfinity_MV3_emitInitVoiceState___closed__4));
x_496 = lp_sidfinity_MV3_CodeBuilder_label(x_494, x_495);
x_497 = lp_sidfinity_MV3_CodeBuilder_emitData(x_496, x_471);
x_498 = ((lean_object*)(lp_sidfinity_MV3_emitNL__UpdateVInst___closed__3));
x_499 = lp_sidfinity_MV3_CodeBuilder_label(x_497, x_498);
x_500 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__17));
x_501 = lp_sidfinity_MV3_CodeBuilder_label(x_499, x_500);
x_502 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_501, x_470);
x_503 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__18));
x_504 = lp_sidfinity_MV3_CodeBuilder_label(x_502, x_503);
x_505 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_504, x_470);
x_506 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__19));
x_507 = lp_sidfinity_MV3_CodeBuilder_label(x_505, x_506);
x_508 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_507, x_470);
x_509 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__0));
x_510 = lp_sidfinity_MV3_CodeBuilder_label(x_508, x_509);
x_511 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__20));
x_512 = lp_sidfinity_MV3_CodeBuilder_label(x_510, x_511);
x_513 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_512, x_470);
x_514 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__21));
x_515 = lp_sidfinity_MV3_CodeBuilder_label(x_513, x_514);
x_516 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_515, x_470);
x_517 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__22));
x_518 = lp_sidfinity_MV3_CodeBuilder_label(x_516, x_517);
x_519 = lp_sidfinity_MV3_CodeBuilder_emitByte(x_518, x_470);
x_520 = ((lean_object*)(lp_sidfinity_MV3_emitNL__SavePitchFhi___closed__11));
x_521 = lp_sidfinity_MV3_CodeBuilder_label(x_519, x_520);
x_522 = lp_sidfinity_MV3_CodeBuilder_emitData(x_521, x_471);
x_523 = ((lean_object*)(lp_sidfinity_MV3_emitNL__DurField___closed__1));
x_524 = lp_sidfinity_MV3_CodeBuilder_label(x_522, x_523);
x_525 = lp_sidfinity_MV3_CodeBuilder_emitData(x_524, x_471);
x_526 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__23));
x_527 = lp_sidfinity_MV3_CodeBuilder_label(x_525, x_526);
x_528 = lp_sidfinity_MV3_CodeBuilder_emitData(x_527, x_471);
x_529 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__24));
x_530 = lp_sidfinity_MV3_CodeBuilder_label(x_528, x_529);
x_531 = lp_sidfinity_MV3_CodeBuilder_emitData(x_530, x_471);
x_532 = ((lean_object*)(lp_sidfinity_MV3_emitSustainEffects___closed__9));
x_533 = lp_sidfinity_MV3_CodeBuilder_label(x_531, x_532);
x_534 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__25, &lp_sidfinity_MV3_generateSID___redArg___closed__25_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__25);
x_535 = lp_sidfinity_MV3_CodeBuilder_emitData(x_533, x_534);
x_536 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PwperiodInit___closed__1));
x_537 = lp_sidfinity_MV3_CodeBuilder_label(x_535, x_536);
x_538 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__28, &lp_sidfinity_MV3_generateSID___redArg___closed__28_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__28);
x_539 = lp_sidfinity_MV3_CodeBuilder_emitData(x_537, x_538);
x_540 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__1));
x_541 = lp_sidfinity_MV3_CodeBuilder_label(x_539, x_540);
x_542 = lp_sidfinity_MV3_CodeBuilder_emitData(x_541, x_471);
x_543 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ExtractFlags___closed__3));
x_544 = lp_sidfinity_MV3_CodeBuilder_label(x_542, x_543);
x_545 = lp_sidfinity_MV3_CodeBuilder_emitData(x_544, x_471);
x_546 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ReadDurInstPorta___closed__2));
x_547 = lp_sidfinity_MV3_CodeBuilder_label(x_545, x_546);
x_548 = lp_sidfinity_MV3_CodeBuilder_emitData(x_547, x_471);
x_549 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__2));
x_550 = lp_sidfinity_MV3_CodeBuilder_label(x_548, x_549);
x_551 = lp_sidfinity_MV3_CodeBuilder_emitData(x_550, x_471);
x_552 = ((lean_object*)(lp_sidfinity_MV3_emitNL__PortaInit___closed__4));
x_553 = lp_sidfinity_MV3_CodeBuilder_label(x_551, x_552);
x_554 = lp_sidfinity_MV3_CodeBuilder_emitData(x_553, x_471);
x_555 = l_List_lengthTR___redArg(x_12);
x_556 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_556, 0, x_3);
lean_ctor_set(x_556, 1, x_555);
lean_ctor_set(x_556, 2, x_16);
x_557 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg(x_12, x_556, x_554, x_3);
lean_dec_ref(x_556);
lean_dec(x_12);
x_558 = ((lean_object*)(lp_sidfinity_MV3_emitNL__ResetAndSidoff___closed__0));
x_559 = lp_sidfinity_MV3_CodeBuilder_label(x_557, x_558);
x_560 = lean_obj_once(&lp_sidfinity_MV3_generateSID___redArg___closed__31, &lp_sidfinity_MV3_generateSID___redArg___closed__31_once, _init_lp_sidfinity_MV3_generateSID___redArg___closed__31);
x_561 = lp_sidfinity_MV3_CodeBuilder_emitData(x_559, x_560);
x_562 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__3));
x_563 = lp_sidfinity_MV3_CodeBuilder_label(x_561, x_562);
x_564 = lp_sidfinity_MV3_CodeBuilder_emitData(x_563, x_471);
x_565 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__5));
x_566 = lp_sidfinity_MV3_CodeBuilder_label(x_564, x_565);
x_567 = lp_sidfinity_MV3_CodeBuilder_emitData(x_566, x_471);
x_568 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__2));
x_569 = lp_sidfinity_MV3_CodeBuilder_label(x_567, x_568);
x_570 = lp_sidfinity_MV3_CodeBuilder_emitData(x_569, x_469);
x_571 = ((lean_object*)(lp_sidfinity_MV3_emitInitSubtuneCopy___closed__4));
x_572 = lp_sidfinity_MV3_CodeBuilder_label(x_570, x_571);
x_573 = lp_sidfinity_MV3_CodeBuilder_emitData(x_572, x_468);
x_574 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__32));
x_575 = lp_sidfinity_MV3_CodeBuilder_label(x_573, x_574);
lean_inc(x_11);
x_576 = lp_sidfinity_List_mapTR_loop___at___00MV3_generateSID_spec__24(x_11, x_4);
x_577 = lp_sidfinity_MV3_CodeBuilder_emitData(x_575, x_576);
x_578 = lp_sidfinity_MV3_CodeBuilder_resolve(x_577);
x_579 = lean_ctor_get(x_578, 0);
lean_inc_ref(x_579);
lean_dec_ref(x_578);
x_580 = 2;
x_581 = 124;
x_582 = 0;
x_583 = 4099;
x_584 = l_List_lengthTR___redArg(x_11);
lean_dec(x_11);
x_585 = lean_uint16_of_nat(x_584);
lean_dec(x_584);
x_586 = 1;
x_587 = 0;
x_588 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__33));
x_589 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__34));
x_590 = ((lean_object*)(lp_sidfinity_MV3_generateSID___redArg___closed__35));
x_591 = lean_alloc_ctor(0, 3, 18);
lean_ctor_set(x_591, 0, x_588);
lean_ctor_set(x_591, 1, x_589);
lean_ctor_set(x_591, 2, x_590);
lean_ctor_set_uint16(x_591, sizeof(void*)*3 + 4, x_580);
lean_ctor_set_uint16(x_591, sizeof(void*)*3 + 6, x_581);
lean_ctor_set_uint16(x_591, sizeof(void*)*3 + 8, x_582);
lean_ctor_set_uint16(x_591, sizeof(void*)*3 + 10, x_2);
lean_ctor_set_uint16(x_591, sizeof(void*)*3 + 12, x_583);
lean_ctor_set_uint16(x_591, sizeof(void*)*3 + 14, x_585);
lean_ctor_set_uint16(x_591, sizeof(void*)*3 + 16, x_586);
lean_ctor_set_uint32(x_591, sizeof(void*)*3, x_587);
x_592 = lp_sidfinity_buildSID(x_591, x_579);
lean_dec_ref(x_579);
lean_dec_ref(x_591);
return x_592;
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_generateSID(lean_object* x_1, uint8_t x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_MV3_generateSID___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_generateSID___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_sidfinity_MV3_generateSID(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___redArg(x_2, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__1(x_1, x_2, x_3, x_4);
lean_dec(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___redArg(x_1, x_2, x_3, x_4);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__4(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___redArg(x_1, x_2, x_3, x_4, x_5);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__5(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___redArg(x_1, x_2, x_3, x_4, x_5);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__6(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7___redArg(x_2, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__7(x_1, x_2, x_3, x_4);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21___redArg(x_2, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__21(x_1, x_2, x_3, x_4);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___redArg(x_2, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_sidfinity_List_forIn_x27_loop___at___00MV3_generateSID_spec__22(x_1, x_2, x_3, x_4);
lean_dec(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___redArg(x_1, x_2, x_3, x_4);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_sidfinity___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00MV3_generateSID_spec__23(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_writeFile(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = 1;
x_5 = lean_io_prim_handle_mk(x_1, x_4);
if (lean_obj_tag(x_5) == 0)
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_6 = lean_ctor_get(x_5, 0);
lean_inc(x_6);
lean_dec_ref(x_5);
x_7 = lean_byte_array_mk(x_2);
x_8 = lean_io_prim_handle_write(x_6, x_7);
lean_dec_ref(x_7);
lean_dec(x_6);
return x_8;
}
else
{
uint8_t x_9; 
lean_dec_ref(x_2);
x_9 = !lean_is_exclusive(x_5);
if (x_9 == 0)
{
return x_5;
}
else
{
lean_object* x_10; lean_object* x_11; 
x_10 = lean_ctor_get(x_5, 0);
lean_inc(x_10);
lean_dec(x_5);
x_11 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_11, 0, x_10);
return x_11;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_MV3_writeFile___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_sidfinity_MV3_writeFile(x_1, x_2);
lean_dec_ref(x_1);
return x_4;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_sidfinity_Monty_SID(uint8_t builtin);
lean_object* initialize_sidfinity_Monty_Asm6502(uint8_t builtin);
lean_object* initialize_sidfinity_Monty_PSIDFile(uint8_t builtin);
lean_object* initialize_sidfinity_Monty_USF(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_sidfinity_Monty_Codegen(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_sidfinity_Monty_SID(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_sidfinity_Monty_Asm6502(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_sidfinity_Monty_PSIDFile(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_sidfinity_Monty_USF(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_sidfinity_MV3_SID__BASE = _init_lp_sidfinity_MV3_SID__BASE();
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
