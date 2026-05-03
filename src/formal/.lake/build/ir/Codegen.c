// Lean compiler output
// Module: Codegen
// Imports: public import Init public import SID public import Asm6502 public import PSIDFile public import Compile public import CommandoData
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
LEAN_EXPORT uint16_t lp_dasmodel_SID__BASE;
lean_object* lean_array_get_size(lean_object*);
uint16_t lean_uint16_of_nat(lean_object*);
uint16_t lean_uint16_add(uint16_t, uint16_t);
LEAN_EXPORT uint16_t lp_dasmodel_CodeBuilder_currentAddr(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_currentAddr___boxed(lean_object*);
lean_object* l_Array_append___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emit(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emit___boxed(lean_object*, lean_object*);
lean_object* lp_dasmodel_assembleInst(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitInst(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitInst___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_label(lean_object*, lean_object*);
uint8_t lean_string_dec_eq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_lookupLabel(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_lookupLabel___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___boxed(lean_object*, lean_object*, lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitBranch___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitBranch___closed__0;
uint8_t lean_int8_of_nat(lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitBranch___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static uint8_t lp_dasmodel_CodeBuilder_emitBranch___closed__1;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitBranch___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitBranch___closed__2;
lean_object* lean_nat_add(lean_object*, lean_object*);
lean_object* lean_array_push(lean_object*, lean_object*);
lean_object* lp_dasmodel_opcode(uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitBranch(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitBranch___boxed(lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitJmpLabel(lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitJmpLabel___boxed(lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__0;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__1;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsX(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__0;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__1;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsY(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitStaAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitStaAbsX___closed__0;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitStaAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitStaAbsX___closed__1;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitStaAbsX(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitDecAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitDecAbsX___closed__0;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitDecAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitDecAbsX___closed__1;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitDecAbsX(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitIncAbsX___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitIncAbsX___closed__0;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitIncAbsX___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitIncAbsX___closed__1;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitIncAbsX(lean_object*, lean_object*);
lean_object* lean_nat_to_int(lean_object*);
static lean_once_cell_t lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0;
static lean_once_cell_t lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1;
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg(lean_object*, lean_object*, lean_object*);
uint8_t lean_uint16_to_uint8(uint16_t);
lean_object* lean_array_set(lean_object*, lean_object*, lean_object*);
uint16_t lean_uint16_shift_right(uint16_t, uint16_t);
lean_object* lean_uint16_to_nat(uint16_t);
lean_object* lean_int_add(lean_object*, lean_object*);
lean_object* lean_int_sub(lean_object*, lean_object*);
lean_object* lean_int_emod(lean_object*, lean_object*);
lean_object* l_Int_toNat(lean_object*);
uint8_t lean_uint8_of_nat(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_resolve(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_array_mk(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitData(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitByte___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitByte___closed__0;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitByte(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitByte___boxed(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitStaAbsY___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitStaAbsY___closed__0;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitStaAbsY___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitStaAbsY___closed__1;
static lean_once_cell_t lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2;
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitStaAbsY(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsYL(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_addAbsFixup(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "init"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__0 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__0_value;
lean_object* lp_dasmodel_I_lda__imm(uint8_t);
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1;
lean_object* lp_dasmodel_I_sta__abs(uint16_t);
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__2;
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__3;
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__4;
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__5;
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__6;
lean_object* lp_dasmodel_I_ldx__imm(uint8_t);
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__7;
static const lean_string_object lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "init_loop"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__8 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__8_value;
static const lean_string_object lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "v_dur"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9_value;
static const lean_string_object lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_olpos"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10_value;
static const lean_string_object lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_wptr"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11_value;
static const lean_string_object lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_pattlo"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12_value;
static const lean_string_object lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_patthi"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13_value;
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__14;
lean_object* lp_dasmodel_I_sta__zp(uint8_t);
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__15;
extern lean_object* lp_dasmodel_I_dex;
extern lean_object* lp_dasmodel_I_rts;
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitInit(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitInit___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "exec_voice"};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___closed__0 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___closed__0_value;
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
lean_object* l_List_get_x3fInternal___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_Codegen_0__emitPlay___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "play"};
static const lean_object* lp_dasmodel___private_Codegen_0__emitPlay___closed__0 = (const lean_object*)&lp_dasmodel___private_Codegen_0__emitPlay___closed__0_value;
lean_object* lp_dasmodel_I_inc__zp(uint8_t);
static lean_once_cell_t lp_dasmodel___private_Codegen_0__emitPlay___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Codegen_0__emitPlay___closed__1;
lean_object* l_List_lengthTR___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitPlay(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitPlay___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lp_dasmodel_I_adc__zp(uint8_t);
static lean_once_cell_t lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0;
extern lean_object* lp_dasmodel_I_clc;
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "note_load"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__0 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__0_value;
lean_object* lp_dasmodel_I_stx__zp(uint8_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__1;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__2;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__3;
lean_object* lp_dasmodel_I_ora__zp(uint8_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__4;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "ptr_ok"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__5 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__5_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "advance_order"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__6 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__6_value;
lean_object* lp_dasmodel_I_ldy__imm(uint8_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__7;
static const lean_ctor_object lp_dasmodel_emitNoteLoadPath___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 9}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(252, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__8 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__8_value;
static const lean_ctor_object lp_dasmodel_emitNoteLoadPath___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__8_value),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__9 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__9_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "has_note"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__10 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__10_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__11;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__12;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__13;
lean_object* lp_dasmodel_I_lda__zp(uint8_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__14;
lean_object* lp_dasmodel_I_adc__imm(uint8_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__15;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__16;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__17;
lean_object* lp_dasmodel_I_ldx__zp(uint8_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__18_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__18;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__19_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__19;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_inst"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__20 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__20_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "v_sidoff"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__21 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__21_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__22_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__22;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "freq_hi"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__23 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__23_value;
lean_object* lp_dasmodel_I_sta__absY(uint16_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__24_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__24;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "freq_lo"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__25 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__25_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__26;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__27_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__27;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_pitch"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__28 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__28_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "v_fhi"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__29 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__29_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__30_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__30;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__31_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_ctrl"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__31 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__31_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__32_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__32;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__33_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_pwlo"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__33 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__33_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__34_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__34;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__35_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_pwhi"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__35 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__35_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__36_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__36;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__37_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_pwhi"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__37 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__37_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__38_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_pwlo"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__38 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__38_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__39_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "v_pwdir"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__39 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__39_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__40_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "i_ad"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__40 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__40_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__41_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__41;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__42_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "i_sr"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__42 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__42_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__43_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__43;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__44_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "v_ctrl"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__44 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__44_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__45_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "ol_lo"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__45 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__45_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__46_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "ol_hi"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__46 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__46_value;
lean_object* lp_dasmodel_I_cmp__imm(uint8_t);
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__47_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__47;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__48_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "song_end"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__48 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__48_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__49_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "patt_ptr_lo"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__49 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__49_value;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__50_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "patt_ptr_hi"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__50 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__50_value;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__51_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__51;
static lean_once_cell_t lp_dasmodel_emitNoteLoadPath___closed__52_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitNoteLoadPath___closed__52;
static const lean_string_object lp_dasmodel_emitNoteLoadPath___closed__53_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "v_durfield"};
static const lean_object* lp_dasmodel_emitNoteLoadPath___closed__53 = (const lean_object*)&lp_dasmodel_emitNoteLoadPath___closed__53_value;
extern lean_object* lp_dasmodel_I_iny;
extern lean_object* lp_dasmodel_I_tay;
extern lean_object* lp_dasmodel_I_pha;
extern lean_object* lp_dasmodel_I_pla;
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
extern lean_object* lp_dasmodel_I_asl__a;
LEAN_EXPORT lean_object* lp_dasmodel_emitNoteLoadPath(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_emitNoteLoadPath___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_ctor_object lp_dasmodel_emitSustainEffects___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 6}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__0 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__0_value;
static const lean_ctor_object lp_dasmodel_emitSustainEffects___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_dasmodel_emitSustainEffects___closed__0_value),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__1 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__1_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "i_pwspeed"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__2 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__2_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "pw_has_speed"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__3 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__3_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "pw_done"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__4 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__4_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__5;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "i_pwmode"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__6 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__6_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__7;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "pw_bidir"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__8 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__8_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__9;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "pw_bidir_down"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__10 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__10_value;
lean_object* lp_dasmodel_I_and__imm(uint8_t);
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__11;
static const lean_ctor_object lp_dasmodel_emitSustainEffects___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_dasmodel_emitSustainEffects___closed__0_value),LEAN_SCALAR_PTR_LITERAL(11, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__12 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__12_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "i_pwmax"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__13 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__13_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "pw_bidir_write"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__14 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__14_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__15;
lean_object* lp_dasmodel_I_sbc__zp(uint8_t);
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__16;
lean_object* lp_dasmodel_I_sbc__imm(uint8_t);
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__17;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "i_pwmin"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__18 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__18_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "i_bit0"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__19 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__19_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "has_slide"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__20 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__20_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "no_slide"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__21 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__21_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "fhi_ok"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__22 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__22_value;
static const lean_ctor_object lp_dasmodel_emitSustainEffects___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 5}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__23 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__23_value;
static const lean_ctor_object lp_dasmodel_emitSustainEffects___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_dasmodel_emitSustainEffects___closed__23_value),LEAN_SCALAR_PTR_LITERAL(11, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__24 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__24_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "slide_path_b"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__25 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__25_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__26;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__27_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__27;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__28_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__28;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "slide_done"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__29 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__29_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__30_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__30;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__31_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "i_arp"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__31 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__31_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__32_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "has_arp"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__32 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__32_value;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__33_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "sustain_done"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__33 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__33_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__34_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__34;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__35_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__35;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__36_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "arp_base"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__36 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__36_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__37_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__37;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__38_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "arp_write"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__38 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__38_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__39_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__39;
static const lean_string_object lp_dasmodel_emitSustainEffects___closed__40_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "dur_ok"};
static const lean_object* lp_dasmodel_emitSustainEffects___closed__40 = (const lean_object*)&lp_dasmodel_emitSustainEffects___closed__40_value;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__41_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__41;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__42_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__42;
static lean_once_cell_t lp_dasmodel_emitSustainEffects___closed__43_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitSustainEffects___closed__43;
extern lean_object* lp_dasmodel_I_sec;
LEAN_EXPORT lean_object* lp_dasmodel_emitSustainEffects(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_emitSustainEffects___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "i_vib"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__0 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__0_value;
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "has_vib"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__1 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__1_value;
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "no_vib"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__2 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__2_value;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__3;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__4;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__5;
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "vib_phase_ok"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__6 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__6_value;
lean_object* lp_dasmodel_I_eor__imm(uint8_t);
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__7;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__8;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__9;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__10;
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "vib_shift"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__11 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__11_value;
static const lean_ctor_object lp_dasmodel_emitVibrato___redArg___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 1}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(245, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__12 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__12_value;
static const lean_ctor_object lp_dasmodel_emitVibrato___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__12_value),LEAN_SCALAR_PTR_LITERAL(23, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__13 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__13_value;
lean_object* lp_dasmodel_I_dec__zp(uint8_t);
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__14;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__15;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__16;
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "vib_onset_ok"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__17 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__17_value;
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "vib_write_base"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__18 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__18_value;
lean_object* lp_dasmodel_I_ldy__zp(uint8_t);
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__19_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__19;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__20_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__20;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__21_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__21;
static const lean_string_object lp_dasmodel_emitVibrato___redArg___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "vib_add_loop"};
static const lean_object* lp_dasmodel_emitVibrato___redArg___closed__22 = (const lean_object*)&lp_dasmodel_emitVibrato___redArg___closed__22_value;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__23_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__23;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__24_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__24;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__25_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__25;
static lean_once_cell_t lp_dasmodel_emitVibrato___redArg___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitVibrato___redArg___closed__26;
extern lean_object* lp_dasmodel_I_lsr__a;
extern lean_object* lp_dasmodel_I_dey;
LEAN_EXPORT lean_object* lp_dasmodel_emitVibrato___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_emitVibrato(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_emitVibrato___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_emitExecVoice___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "sustain"};
static const lean_object* lp_dasmodel_emitExecVoice___closed__0 = (const lean_object*)&lp_dasmodel_emitExecVoice___closed__0_value;
static lean_once_cell_t lp_dasmodel_emitExecVoice___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_emitExecVoice___closed__1;
static const lean_string_object lp_dasmodel_emitExecVoice___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "effects_start"};
static const lean_object* lp_dasmodel_emitExecVoice___closed__2 = (const lean_object*)&lp_dasmodel_emitExecVoice___closed__2_value;
LEAN_EXPORT lean_object* lp_dasmodel_emitExecVoice(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_emitExecVoice___boxed(lean_object*, lean_object*);
lean_object* l_List_reverse___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__15(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__9(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__13(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__12(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__18(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0;
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_List_appendTR___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__8(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__14(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__7(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__5(lean_object*, lean_object*);
lean_object* l_List_head_x3f___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__11(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__10(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__6(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__16(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__0;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__1;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__2;
static const lean_ctor_object lp_dasmodel_generateSID___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__3 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__3_value;
static const lean_ctor_object lp_dasmodel_generateSID___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_dasmodel_generateSID___redArg___closed__3_value)}};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__4 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__4_value;
static const lean_ctor_object lp_dasmodel_generateSID___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_dasmodel_generateSID___redArg___closed__4_value)}};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__5 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__5_value;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__6;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__7;
static const lean_string_object lp_dasmodel_generateSID___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "wave_data"};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__8 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__8_value;
static const lean_string_object lp_dasmodel_generateSID___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "i_wavebase"};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__9 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__9_value;
static const lean_string_object lp_dasmodel_generateSID___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "i_wavelen"};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__10 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__10_value;
static const lean_string_object lp_dasmodel_generateSID___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "i_waveloop"};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__11 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__11_value;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__12;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__13;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__14;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__15;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__16;
static lean_once_cell_t lp_dasmodel_generateSID___redArg___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_generateSID___redArg___closed__17;
static const lean_string_object lp_dasmodel_generateSID___redArg___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "Commando"};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__18 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__18_value;
static const lean_string_object lp_dasmodel_generateSID___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "Rob Hubbard"};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__19 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__19_value;
static const lean_string_object lp_dasmodel_generateSID___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "1985 Elite"};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__20 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__20_value;
static const lean_ctor_object lp_dasmodel_generateSID___redArg___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*3 + 24, .m_other = 3, .m_tag = 0}, .m_objs = {((lean_object*)&lp_dasmodel_generateSID___redArg___closed__18_value),((lean_object*)&lp_dasmodel_generateSID___redArg___closed__19_value),((lean_object*)&lp_dasmodel_generateSID___redArg___closed__20_value),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 2, 0, 124, 0),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 16, 3, 16, 1, 0),LEAN_SCALAR_PTR_LITERAL(1, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_generateSID___redArg___closed__21 = (const lean_object*)&lp_dasmodel_generateSID___redArg___closed__21_value;
lean_object* lp_dasmodel_buildSID(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_generateSID___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_generateSID(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_generateSID___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_io_prim_handle_mk(lean_object*, uint8_t);
lean_object* lean_byte_array_mk(lean_object*);
lean_object* lean_io_prim_handle_write(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_writeFile(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_writeFile___boxed(lean_object*, lean_object*, lean_object*);
extern lean_object* lp_dasmodel_commandoSong;
static lean_once_cell_t lp_dasmodel_sidgenMain___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_sidgenMain___closed__0;
static const lean_string_object lp_dasmodel_sidgenMain___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 18, .m_capacity = 18, .m_length = 17, .m_data = "commando_lean.sid"};
static const lean_object* lp_dasmodel_sidgenMain___closed__1 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__1_value;
static const lean_string_object lp_dasmodel_sidgenMain___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 30, .m_capacity = 30, .m_length = 29, .m_data = "Generated commando_lean.sid ("};
static const lean_object* lp_dasmodel_sidgenMain___closed__2 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__2_value;
static lean_once_cell_t lp_dasmodel_sidgenMain___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_sidgenMain___closed__3;
lean_object* l_Nat_reprFast(lean_object*);
static lean_once_cell_t lp_dasmodel_sidgenMain___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_sidgenMain___closed__4;
lean_object* lean_string_append(lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_sidgenMain___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_sidgenMain___closed__5;
static const lean_string_object lp_dasmodel_sidgenMain___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = " bytes)"};
static const lean_object* lp_dasmodel_sidgenMain___closed__6 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__6_value;
static lean_once_cell_t lp_dasmodel_sidgenMain___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_sidgenMain___closed__7;
static const lean_string_object lp_dasmodel_sidgenMain___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "  Freq table: "};
static const lean_object* lp_dasmodel_sidgenMain___closed__8 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__8_value;
static const lean_string_object lp_dasmodel_sidgenMain___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " entries"};
static const lean_object* lp_dasmodel_sidgenMain___closed__9 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__9_value;
static const lean_string_object lp_dasmodel_sidgenMain___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "  Instruments: "};
static const lean_object* lp_dasmodel_sidgenMain___closed__10 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__10_value;
static const lean_string_object lp_dasmodel_sidgenMain___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "  Patterns: "};
static const lean_object* lp_dasmodel_sidgenMain___closed__11 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__11_value;
static const lean_string_object lp_dasmodel_sidgenMain___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "  Voices: "};
static const lean_object* lp_dasmodel_sidgenMain___closed__12 = (const lean_object*)&lp_dasmodel_sidgenMain___closed__12_value;
lean_object* lp_dasmodel_IO_println___at___00commandoMain_spec__0(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_sidgenMain();
LEAN_EXPORT lean_object* lp_dasmodel_sidgenMain___boxed(lean_object*);
static uint16_t _init_lp_dasmodel_SID__BASE(void) {
_start:
{
uint16_t x_1; 
x_1 = 54272;
return x_1;
}
}
LEAN_EXPORT uint16_t lp_dasmodel_CodeBuilder_currentAddr(lean_object* x_1) {
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
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_currentAddr___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lp_dasmodel_CodeBuilder_currentAddr(x_1);
lean_dec_ref(x_1);
x_3 = lean_box(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emit(lean_object* x_1, lean_object* x_2) {
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
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emit___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_CodeBuilder_emit(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitInst(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_assembleInst(x_2);
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
x_5 = lp_dasmodel_CodeBuilder_emit(x_1, x_4);
lean_dec(x_4);
return x_5;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitInst___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_CodeBuilder_emitInst(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_label(lean_object* x_1, lean_object* x_2) {
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
x_8 = lp_dasmodel_CodeBuilder_currentAddr(x_1);
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
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___redArg(lean_object* x_1, lean_object* x_2) {
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
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___redArg(x_1, x_2);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_lookupLabel(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_ctor_get(x_1, 1);
x_4 = lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___redArg(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_lookupLabel___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_CodeBuilder_lookupLabel(x_1, x_2);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___redArg(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_List_lookup___at___00CodeBuilder_lookupLabel_spec__0(x_1, x_2, x_3);
lean_dec(x_3);
lean_dec_ref(x_2);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitBranch___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static uint8_t _init_lp_dasmodel_CodeBuilder_emitBranch___closed__1(void) {
_start:
{
lean_object* x_1; uint8_t x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_int8_of_nat(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitBranch___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = lean_uint8_once(&lp_dasmodel_CodeBuilder_emitBranch___closed__1, &lp_dasmodel_CodeBuilder_emitBranch___closed__1_once, _init_lp_dasmodel_CodeBuilder_emitBranch___closed__1);
x_2 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_2, 0, x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitBranch(lean_object* x_1, uint8_t x_2, lean_object* x_3) {
_start:
{
uint16_t x_4; uint8_t x_5; lean_object* x_42; lean_object* x_43; 
x_4 = lp_dasmodel_CodeBuilder_currentAddr(x_1);
x_42 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitBranch___closed__2, &lp_dasmodel_CodeBuilder_emitBranch___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitBranch___closed__2);
x_43 = lp_dasmodel_opcode(x_2, x_42);
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
x_15 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitBranch___closed__0, &lp_dasmodel_CodeBuilder_emitBranch___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitBranch___closed__0);
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
x_33 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitBranch___closed__0, &lp_dasmodel_CodeBuilder_emitBranch___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitBranch___closed__0);
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
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitBranch___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel_CodeBuilder_emitBranch(x_1, x_4, x_3);
return x_5;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(3u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitJmpLabel(lean_object* x_1, uint8_t x_2, lean_object* x_3) {
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
x_14 = lp_dasmodel_CodeBuilder_currentAddr(x_1);
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
x_22 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
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
x_33 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
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
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitJmpLabel___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1, x_4, x_3);
return x_5;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 189;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__0, &lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__1, &lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__1_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsX(lean_object* x_1, lean_object* x_2) {
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
x_10 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2);
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
x_22 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsX___closed__2);
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
static lean_object* _init_lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 185;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__0, &lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__1, &lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__1_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsY(lean_object* x_1, lean_object* x_2) {
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
x_10 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2, &lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2);
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
x_22 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2, &lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitLdaAbsY___closed__2);
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
static lean_object* _init_lp_dasmodel_CodeBuilder_emitStaAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 157;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitStaAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsX___closed__0, &lp_dasmodel_CodeBuilder_emitStaAbsX___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsX___closed__1, &lp_dasmodel_CodeBuilder_emitStaAbsX___closed__1_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitStaAbsX(lean_object* x_1, lean_object* x_2) {
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
x_10 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2);
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
x_22 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsX___closed__2);
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
static lean_object* _init_lp_dasmodel_CodeBuilder_emitDecAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 222;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitDecAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitDecAbsX___closed__0, &lp_dasmodel_CodeBuilder_emitDecAbsX___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitDecAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitDecAbsX___closed__1, &lp_dasmodel_CodeBuilder_emitDecAbsX___closed__1_once, _init_lp_dasmodel_CodeBuilder_emitDecAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitDecAbsX(lean_object* x_1, lean_object* x_2) {
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
x_10 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2);
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
x_22 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitDecAbsX___closed__2);
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
static lean_object* _init_lp_dasmodel_CodeBuilder_emitIncAbsX___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 254;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitIncAbsX___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitIncAbsX___closed__0, &lp_dasmodel_CodeBuilder_emitIncAbsX___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitIncAbsX___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitIncAbsX___closed__1, &lp_dasmodel_CodeBuilder_emitIncAbsX___closed__1_once, _init_lp_dasmodel_CodeBuilder_emitIncAbsX___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitIncAbsX(lean_object* x_1, lean_object* x_2) {
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
x_10 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2);
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
x_22 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2, &lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitIncAbsX___closed__2);
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
static lean_object* _init_lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(256u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
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
x_10 = lp_dasmodel_CodeBuilder_lookupLabel(x_1, x_7);
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
x_32 = lean_obj_once(&lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0, &lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0_once, _init_lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0);
x_33 = lean_int_add(x_31, x_32);
lean_dec(x_31);
x_34 = lean_int_sub(x_29, x_33);
lean_dec(x_33);
lean_dec(x_29);
x_35 = lean_obj_once(&lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1, &lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1_once, _init_lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1);
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
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_2, x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
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
x_11 = lp_dasmodel_CodeBuilder_lookupLabel(x_1, x_8);
if (lean_obj_tag(x_11) == 0)
{
lean_object* x_12; 
x_12 = lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_6, x_4);
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
x_26 = lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_6, x_25);
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
x_33 = lean_obj_once(&lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0, &lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0_once, _init_lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__0);
x_34 = lean_int_add(x_32, x_33);
lean_dec(x_32);
x_35 = lean_int_sub(x_30, x_34);
lean_dec(x_34);
lean_dec(x_30);
x_36 = lean_obj_once(&lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1, &lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1_once, _init_lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg___closed__1);
x_37 = lean_int_emod(x_35, x_36);
lean_dec(x_35);
x_38 = l_Int_toNat(x_37);
lean_dec(x_37);
x_39 = lean_uint8_of_nat(x_38);
lean_dec(x_38);
x_40 = lean_box(x_39);
x_41 = lean_array_set(x_4, x_7, x_40);
x_42 = lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_6, x_41);
return x_42;
}
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___redArg(x_1, x_2, x_3, x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
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
x_8 = lp_dasmodel_CodeBuilder_lookupLabel(x_1, x_7);
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
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___redArg(x_1, x_2, x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_resolve(lean_object* x_1) {
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
x_7 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___redArg(x_1, x_5, x_5, x_2);
x_8 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___redArg(x_1, x_6, x_7);
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
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___redArg(x_1, x_2, x_3, x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___redArg(x_1, x_3, x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__1(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___redArg(x_1, x_3, x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00List_forIn_x27_loop___at___00CodeBuilder_resolve_spec__0_spec__0(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_3);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitData(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_array_mk(x_2);
x_4 = lp_dasmodel_CodeBuilder_emit(x_1, x_3);
lean_dec_ref(x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitByte___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(1u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitByte(lean_object* x_1, uint8_t x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_3 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitByte___closed__0, &lp_dasmodel_CodeBuilder_emitByte___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitByte___closed__0);
x_4 = lean_box(x_2);
x_5 = lean_array_push(x_3, x_4);
x_6 = lp_dasmodel_CodeBuilder_emit(x_1, x_5);
lean_dec_ref(x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitByte___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_CodeBuilder_emitByte(x_1, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitStaAbsY___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 153;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0, &lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitJmpLabel___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitStaAbsY___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsY___closed__0, &lp_dasmodel_CodeBuilder_emitStaAbsY___closed__0_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsY___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsY___closed__1, &lp_dasmodel_CodeBuilder_emitStaAbsY___closed__1_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsY___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitStaAbsY(lean_object* x_1, lean_object* x_2) {
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
x_10 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2, &lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2);
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
x_22 = lean_obj_once(&lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2, &lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2_once, _init_lp_dasmodel_CodeBuilder_emitStaAbsY___closed__2);
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
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_emitLdaAbsYL(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CodeBuilder_addAbsFixup(lean_object* x_1, lean_object* x_2) {
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
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_dasmodel_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__2(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54276;
x_2 = lp_dasmodel_I_sta__abs(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__3(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54283;
x_2 = lp_dasmodel_I_sta__abs(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__4(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54290;
x_2 = lp_dasmodel_I_sta__abs(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__5(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 15;
x_2 = lp_dasmodel_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__6(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54296;
x_2 = lp_dasmodel_I_sta__abs(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 2;
x_2 = lp_dasmodel_I_ldx__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__14(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_dasmodel_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__15(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 80;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitInit___redArg(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; uint8_t x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; 
x_2 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__0));
x_3 = lp_dasmodel_CodeBuilder_label(x_1, x_2);
x_4 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_5 = lp_dasmodel_CodeBuilder_emitInst(x_3, x_4);
x_6 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__2, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__2_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__2);
x_7 = lp_dasmodel_CodeBuilder_emitInst(x_5, x_6);
x_8 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__3, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__3_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__3);
x_9 = lp_dasmodel_CodeBuilder_emitInst(x_7, x_8);
x_10 = lp_dasmodel_CodeBuilder_emitInst(x_9, x_6);
x_11 = lp_dasmodel_CodeBuilder_emitInst(x_10, x_8);
x_12 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__4, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__4_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__4);
x_13 = lp_dasmodel_CodeBuilder_emitInst(x_11, x_12);
x_14 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__5, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__5_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__5);
x_15 = lp_dasmodel_CodeBuilder_emitInst(x_13, x_14);
x_16 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__6, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__6_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__6);
x_17 = lp_dasmodel_CodeBuilder_emitInst(x_15, x_16);
x_18 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__7, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__7_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__7);
x_19 = lp_dasmodel_CodeBuilder_emitInst(x_17, x_18);
x_20 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__8));
x_21 = lp_dasmodel_CodeBuilder_label(x_19, x_20);
x_22 = lp_dasmodel_CodeBuilder_emitInst(x_21, x_4);
x_23 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_24 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_22, x_23);
x_25 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10));
x_26 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_24, x_25);
x_27 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11));
x_28 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_26, x_27);
x_29 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12));
x_30 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_28, x_29);
x_31 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13));
x_32 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_30, x_31);
x_33 = lp_dasmodel_I_dex;
x_34 = lp_dasmodel_CodeBuilder_emitInst(x_32, x_33);
x_35 = 29;
x_36 = lp_dasmodel_CodeBuilder_emitBranch(x_34, x_35, x_20);
x_37 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__14, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__14_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__14);
x_38 = lp_dasmodel_CodeBuilder_emitInst(x_36, x_37);
x_39 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__15, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__15_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__15);
x_40 = lp_dasmodel_CodeBuilder_emitInst(x_38, x_39);
x_41 = lp_dasmodel_I_rts;
x_42 = lp_dasmodel_CodeBuilder_emitInst(x_40, x_41);
return x_42;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitInit(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel___private_Codegen_0__emitInit___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitInit___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel___private_Codegen_0__emitInit(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; uint8_t x_12; 
x_6 = lean_ctor_get(x_3, 1);
x_7 = lean_ctor_get(x_3, 2);
x_12 = lean_nat_dec_lt(x_5, x_6);
if (x_12 == 0)
{
lean_dec(x_5);
return x_4;
}
else
{
lean_object* x_13; 
lean_inc(x_5);
x_13 = l_List_get_x3fInternal___redArg(x_1, x_5);
if (lean_obj_tag(x_13) == 0)
{
x_8 = x_4;
goto block_11;
}
else
{
lean_object* x_14; lean_object* x_15; uint8_t x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; uint8_t x_20; 
x_14 = lean_ctor_get(x_13, 0);
lean_inc(x_14);
lean_dec_ref(x_13);
x_15 = lean_unsigned_to_nat(1u);
x_16 = lean_uint8_of_nat(x_14);
lean_dec(x_14);
x_17 = lp_dasmodel_I_ldx__imm(x_16);
x_18 = lp_dasmodel_CodeBuilder_emitInst(x_4, x_17);
lean_dec_ref(x_17);
x_19 = lean_nat_add(x_5, x_15);
x_20 = lean_nat_dec_lt(x_19, x_2);
lean_dec(x_19);
if (x_20 == 0)
{
uint8_t x_21; lean_object* x_22; lean_object* x_23; 
x_21 = 32;
x_22 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___closed__0));
x_23 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_18, x_21, x_22);
x_8 = x_23;
goto block_11;
}
else
{
uint8_t x_24; lean_object* x_25; lean_object* x_26; 
x_24 = 33;
x_25 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___closed__0));
x_26 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_18, x_24, x_25);
x_8 = x_26;
goto block_11;
}
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
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_6;
}
}
static lean_object* _init_lp_dasmodel___private_Codegen_0__emitPlay___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 80;
x_2 = lp_dasmodel_I_inc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitPlay(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_3 = lean_ctor_get(x_2, 5);
x_4 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitPlay___closed__0));
x_5 = lp_dasmodel_CodeBuilder_label(x_1, x_4);
x_6 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitPlay___closed__1, &lp_dasmodel___private_Codegen_0__emitPlay___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitPlay___closed__1);
x_7 = lp_dasmodel_CodeBuilder_emitInst(x_5, x_6);
x_8 = l_List_lengthTR___redArg(x_3);
x_9 = lean_unsigned_to_nat(0u);
x_10 = lean_unsigned_to_nat(1u);
lean_inc(x_8);
x_11 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_11, 0, x_9);
lean_ctor_set(x_11, 1, x_8);
lean_ctor_set(x_11, 2, x_10);
x_12 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg(x_3, x_8, x_11, x_7, x_9);
lean_dec_ref(x_11);
lean_dec(x_8);
return x_12;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Codegen_0__emitPlay___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel___private_Codegen_0__emitPlay(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg(x_1, x_2, x_3, x_4, x_5);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_8;
}
}
static lean_object* _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_dasmodel_I_adc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_4 = lean_ctor_get(x_1, 1);
x_5 = lean_ctor_get(x_1, 2);
x_6 = lean_nat_dec_lt(x_3, x_4);
if (x_6 == 0)
{
lean_dec(x_3);
return x_2;
}
else
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_7 = lp_dasmodel_I_clc;
x_8 = lp_dasmodel_CodeBuilder_emitInst(x_2, x_7);
x_9 = lean_obj_once(&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0, &lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0_once, _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0);
x_10 = lp_dasmodel_CodeBuilder_emitInst(x_8, x_9);
x_11 = lean_nat_add(x_3, x_5);
lean_dec(x_3);
x_2 = x_10;
x_3 = x_11;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg(x_1, x_2, x_3);
lean_dec_ref(x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 250;
x_2 = lp_dasmodel_I_stx__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 252;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 253;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__4(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 252;
x_2 = lp_dasmodel_I_ora__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_dasmodel_I_ldy__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__11(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__12(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__13(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 251;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__14(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 252;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__15(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 3;
x_2 = lp_dasmodel_I_adc__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__16(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 253;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__17(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_dasmodel_I_adc__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__18(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 250;
x_2 = lp_dasmodel_I_ldx__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__19(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 251;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__22(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_dasmodel_I_ldx__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__24(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54273;
x_2 = lp_dasmodel_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__26(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54272;
x_2 = lp_dasmodel_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__27(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__30(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 251;
x_2 = lp_dasmodel_I_ldx__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__32(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54276;
x_2 = lp_dasmodel_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__34(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54274;
x_2 = lp_dasmodel_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__36(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54275;
x_2 = lp_dasmodel_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__41(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54277;
x_2 = lp_dasmodel_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__43(void) {
_start:
{
uint16_t x_1; lean_object* x_2; 
x_1 = 54278;
x_2 = lp_dasmodel_I_sta__absY(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__47(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_dasmodel_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__51(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 127;
x_2 = lp_dasmodel_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitNoteLoadPath___closed__52(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 255;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitNoteLoadPath(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; uint8_t x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; uint8_t x_179; 
x_3 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__0));
x_4 = lp_dasmodel_CodeBuilder_label(x_1, x_3);
x_5 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__1, &lp_dasmodel_emitNoteLoadPath___closed__1_once, _init_lp_dasmodel_emitNoteLoadPath___closed__1);
x_6 = lp_dasmodel_CodeBuilder_emitInst(x_4, x_5);
x_7 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12));
x_8 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_6, x_7);
x_9 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__2, &lp_dasmodel_emitNoteLoadPath___closed__2_once, _init_lp_dasmodel_emitNoteLoadPath___closed__2);
x_10 = lp_dasmodel_CodeBuilder_emitInst(x_8, x_9);
x_11 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13));
x_12 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_10, x_11);
x_13 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__3, &lp_dasmodel_emitNoteLoadPath___closed__3_once, _init_lp_dasmodel_emitNoteLoadPath___closed__3);
x_14 = lp_dasmodel_CodeBuilder_emitInst(x_12, x_13);
x_15 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__4, &lp_dasmodel_emitNoteLoadPath___closed__4_once, _init_lp_dasmodel_emitNoteLoadPath___closed__4);
x_16 = lp_dasmodel_CodeBuilder_emitInst(x_14, x_15);
x_17 = 27;
x_18 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__5));
x_19 = lp_dasmodel_CodeBuilder_emitBranch(x_16, x_17, x_18);
x_20 = lean_ctor_get(x_2, 4);
x_21 = 32;
x_22 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__6));
x_23 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_19, x_21, x_22);
x_24 = lp_dasmodel_CodeBuilder_label(x_23, x_18);
x_25 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__7, &lp_dasmodel_emitNoteLoadPath___closed__7_once, _init_lp_dasmodel_emitNoteLoadPath___closed__7);
x_26 = lp_dasmodel_CodeBuilder_emitInst(x_24, x_25);
x_27 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__9));
x_28 = lp_dasmodel_CodeBuilder_emitInst(x_26, x_27);
x_29 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__10));
x_30 = lp_dasmodel_CodeBuilder_emitBranch(x_28, x_17, x_29);
x_31 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__11, &lp_dasmodel_emitNoteLoadPath___closed__11_once, _init_lp_dasmodel_emitNoteLoadPath___closed__11);
x_32 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_30, x_21, x_22);
x_33 = lp_dasmodel_CodeBuilder_label(x_32, x_29);
x_34 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__12, &lp_dasmodel_emitNoteLoadPath___closed__12_once, _init_lp_dasmodel_emitNoteLoadPath___closed__12);
x_35 = lp_dasmodel_CodeBuilder_emitInst(x_33, x_34);
x_36 = lp_dasmodel_I_iny;
x_37 = lp_dasmodel_CodeBuilder_emitInst(x_35, x_36);
x_38 = lp_dasmodel_CodeBuilder_emitInst(x_37, x_27);
x_39 = lp_dasmodel_CodeBuilder_emitInst(x_38, x_31);
x_40 = lp_dasmodel_CodeBuilder_emitInst(x_39, x_36);
x_41 = lp_dasmodel_CodeBuilder_emitInst(x_40, x_27);
x_42 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_43 = lp_dasmodel_CodeBuilder_emitInst(x_41, x_42);
x_44 = lp_dasmodel_I_clc;
x_45 = lp_dasmodel_CodeBuilder_emitInst(x_43, x_44);
x_46 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__14, &lp_dasmodel_emitNoteLoadPath___closed__14_once, _init_lp_dasmodel_emitNoteLoadPath___closed__14);
x_47 = lp_dasmodel_CodeBuilder_emitInst(x_45, x_46);
x_48 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__15, &lp_dasmodel_emitNoteLoadPath___closed__15_once, _init_lp_dasmodel_emitNoteLoadPath___closed__15);
x_49 = lp_dasmodel_CodeBuilder_emitInst(x_47, x_48);
x_50 = lp_dasmodel_CodeBuilder_emitInst(x_49, x_9);
x_51 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__16, &lp_dasmodel_emitNoteLoadPath___closed__16_once, _init_lp_dasmodel_emitNoteLoadPath___closed__16);
x_52 = lp_dasmodel_CodeBuilder_emitInst(x_50, x_51);
x_53 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__17, &lp_dasmodel_emitNoteLoadPath___closed__17_once, _init_lp_dasmodel_emitNoteLoadPath___closed__17);
x_54 = lp_dasmodel_CodeBuilder_emitInst(x_52, x_53);
x_55 = lp_dasmodel_CodeBuilder_emitInst(x_54, x_13);
x_56 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_168 = lp_dasmodel_CodeBuilder_emitInst(x_55, x_56);
x_169 = lp_dasmodel_CodeBuilder_emitInst(x_168, x_46);
x_170 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_169, x_7);
x_171 = lp_dasmodel_CodeBuilder_emitInst(x_170, x_51);
x_172 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_171, x_11);
x_173 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__52, &lp_dasmodel_emitNoteLoadPath___closed__52_once, _init_lp_dasmodel_emitNoteLoadPath___closed__52);
x_174 = lp_dasmodel_CodeBuilder_emitInst(x_172, x_173);
x_175 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_176 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_174, x_175);
x_177 = lp_dasmodel_CodeBuilder_emitInst(x_176, x_173);
x_178 = lean_unsigned_to_nat(1u);
x_179 = lean_nat_dec_eq(x_20, x_178);
if (x_179 == 0)
{
lean_object* x_180; uint8_t x_181; 
x_180 = lean_unsigned_to_nat(3u);
x_181 = lean_nat_dec_eq(x_20, x_180);
if (x_181 == 0)
{
lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; lean_object* x_186; 
x_182 = lean_unsigned_to_nat(0u);
x_183 = lp_dasmodel_CodeBuilder_emitInst(x_177, x_31);
x_184 = lean_nat_sub(x_20, x_178);
x_185 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_185, 0, x_182);
lean_ctor_set(x_185, 1, x_184);
lean_ctor_set(x_185, 2, x_178);
x_186 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg(x_185, x_183, x_182);
lean_dec_ref(x_185);
x_57 = x_186;
goto block_167;
}
else
{
lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; lean_object* x_191; lean_object* x_192; 
x_187 = lp_dasmodel_CodeBuilder_emitInst(x_177, x_31);
x_188 = lp_dasmodel_I_asl__a;
x_189 = lp_dasmodel_CodeBuilder_emitInst(x_187, x_188);
x_190 = lp_dasmodel_CodeBuilder_emitInst(x_189, x_44);
x_191 = lean_obj_once(&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0, &lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0_once, _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg___closed__0);
x_192 = lp_dasmodel_CodeBuilder_emitInst(x_190, x_191);
x_57 = x_192;
goto block_167;
}
}
else
{
x_57 = x_177;
goto block_167;
}
block_167:
{
lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; lean_object* x_139; lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; uint8_t x_150; lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_154; lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; 
x_58 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_59 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_57, x_58);
x_60 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_61 = lp_dasmodel_CodeBuilder_emitInst(x_59, x_60);
x_62 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__20));
x_63 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_61, x_62);
x_64 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_65 = lp_dasmodel_CodeBuilder_emitInst(x_63, x_64);
x_66 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11));
x_67 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_65, x_66);
x_68 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_69 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_67, x_68);
x_70 = lp_dasmodel_I_tay;
x_71 = lp_dasmodel_CodeBuilder_emitInst(x_69, x_70);
x_72 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__22, &lp_dasmodel_emitNoteLoadPath___closed__22_once, _init_lp_dasmodel_emitNoteLoadPath___closed__22);
x_73 = lp_dasmodel_CodeBuilder_emitInst(x_71, x_72);
x_74 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_75 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_73, x_74);
x_76 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_77 = lp_dasmodel_CodeBuilder_emitInst(x_75, x_76);
x_78 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_79 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_77, x_78);
x_80 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_81 = lp_dasmodel_CodeBuilder_emitInst(x_79, x_80);
x_82 = lp_dasmodel_CodeBuilder_emitInst(x_81, x_56);
x_83 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__27, &lp_dasmodel_emitNoteLoadPath___closed__27_once, _init_lp_dasmodel_emitNoteLoadPath___closed__27);
x_84 = lp_dasmodel_CodeBuilder_emitInst(x_82, x_83);
x_85 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_86 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_84, x_85);
x_87 = lp_dasmodel_CodeBuilder_emitInst(x_86, x_72);
x_88 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_87, x_74);
x_89 = lp_dasmodel_CodeBuilder_emitInst(x_88, x_56);
x_90 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_91 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_89, x_90);
x_92 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__30, &lp_dasmodel_emitNoteLoadPath___closed__30_once, _init_lp_dasmodel_emitNoteLoadPath___closed__30);
x_93 = lp_dasmodel_CodeBuilder_emitInst(x_91, x_92);
x_94 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_95 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_93, x_94);
x_96 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_97 = lp_dasmodel_CodeBuilder_emitInst(x_95, x_96);
x_98 = lp_dasmodel_I_pha;
x_99 = lp_dasmodel_CodeBuilder_emitInst(x_97, x_98);
x_100 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__33));
x_101 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_99, x_100);
x_102 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__34, &lp_dasmodel_emitNoteLoadPath___closed__34_once, _init_lp_dasmodel_emitNoteLoadPath___closed__34);
x_103 = lp_dasmodel_CodeBuilder_emitInst(x_101, x_102);
x_104 = lp_dasmodel_CodeBuilder_emitInst(x_103, x_98);
x_105 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__35));
x_106 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_104, x_105);
x_107 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__36, &lp_dasmodel_emitNoteLoadPath___closed__36_once, _init_lp_dasmodel_emitNoteLoadPath___closed__36);
x_108 = lp_dasmodel_CodeBuilder_emitInst(x_106, x_107);
x_109 = lp_dasmodel_CodeBuilder_emitInst(x_108, x_98);
x_110 = lp_dasmodel_CodeBuilder_emitInst(x_109, x_56);
x_111 = lp_dasmodel_I_pla;
x_112 = lp_dasmodel_CodeBuilder_emitInst(x_110, x_111);
x_113 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__37));
x_114 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_112, x_113);
x_115 = lp_dasmodel_CodeBuilder_emitInst(x_114, x_111);
x_116 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__38));
x_117 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_115, x_116);
x_118 = lp_dasmodel_CodeBuilder_emitInst(x_117, x_64);
x_119 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__39));
x_120 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_118, x_119);
x_121 = lp_dasmodel_CodeBuilder_emitInst(x_120, x_92);
x_122 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__40));
x_123 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_121, x_122);
x_124 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__41, &lp_dasmodel_emitNoteLoadPath___closed__41_once, _init_lp_dasmodel_emitNoteLoadPath___closed__41);
x_125 = lp_dasmodel_CodeBuilder_emitInst(x_123, x_124);
x_126 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__42));
x_127 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_125, x_126);
x_128 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__43, &lp_dasmodel_emitNoteLoadPath___closed__43_once, _init_lp_dasmodel_emitNoteLoadPath___closed__43);
x_129 = lp_dasmodel_CodeBuilder_emitInst(x_127, x_128);
x_130 = lp_dasmodel_CodeBuilder_emitInst(x_129, x_111);
x_131 = lp_dasmodel_CodeBuilder_emitInst(x_130, x_56);
x_132 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__44));
x_133 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_131, x_132);
x_134 = lp_dasmodel_I_rts;
x_135 = lp_dasmodel_CodeBuilder_emitInst(x_133, x_134);
x_136 = lp_dasmodel_CodeBuilder_label(x_135, x_22);
x_137 = lp_dasmodel_CodeBuilder_emitInst(x_136, x_56);
x_138 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10));
x_139 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_137, x_138);
x_140 = lp_dasmodel_CodeBuilder_emitInst(x_139, x_70);
x_141 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__45));
x_142 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_140, x_141);
x_143 = lp_dasmodel_CodeBuilder_emitInst(x_142, x_9);
x_144 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__46));
x_145 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_143, x_144);
x_146 = lp_dasmodel_CodeBuilder_emitInst(x_145, x_13);
x_147 = lp_dasmodel_CodeBuilder_emitInst(x_146, x_27);
x_148 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__47, &lp_dasmodel_emitNoteLoadPath___closed__47_once, _init_lp_dasmodel_emitNoteLoadPath___closed__47);
x_149 = lp_dasmodel_CodeBuilder_emitInst(x_147, x_148);
x_150 = 26;
x_151 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__48));
x_152 = lp_dasmodel_CodeBuilder_emitBranch(x_149, x_150, x_151);
x_153 = lp_dasmodel_CodeBuilder_emitInst(x_152, x_70);
x_154 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__49));
x_155 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_153, x_154);
x_156 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_155, x_7);
x_157 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__50));
x_158 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_156, x_157);
x_159 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_158, x_11);
x_160 = lp_dasmodel_CodeBuilder_emitIncAbsX(x_159, x_138);
x_161 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_160, x_21, x_3);
x_162 = lp_dasmodel_CodeBuilder_label(x_161, x_151);
x_163 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__51, &lp_dasmodel_emitNoteLoadPath___closed__51_once, _init_lp_dasmodel_emitNoteLoadPath___closed__51);
x_164 = lp_dasmodel_CodeBuilder_emitInst(x_162, x_163);
x_165 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_164, x_58);
x_166 = lp_dasmodel_CodeBuilder_emitInst(x_165, x_134);
return x_166;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitNoteLoadPath___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_emitNoteLoadPath(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___redArg(x_1, x_2, x_3);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00emitNoteLoadPath_spec__0(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_1);
return x_6;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__5(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 2;
x_2 = lp_dasmodel_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__9(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_dasmodel_I_adc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__11(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 15;
x_2 = lp_dasmodel_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__15(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 1;
x_2 = lp_dasmodel_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__16(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_dasmodel_I_sbc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__17(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 0;
x_2 = lp_dasmodel_I_sbc__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__26(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__27(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__28(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 254;
x_2 = lp_dasmodel_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__30(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 128;
x_2 = lp_dasmodel_I_lda__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__34(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 80;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__35(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 1;
x_2 = lp_dasmodel_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__37(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_dasmodel_I_adc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__39(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 249;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__41(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 1;
x_2 = lp_dasmodel_I_sbc__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__42(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 241;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitSustainEffects___closed__43(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 241;
x_2 = lp_dasmodel_I_adc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitSustainEffects(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; uint8_t x_9; 
x_3 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__20));
x_4 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1, x_3);
x_5 = lp_dasmodel_I_tay;
x_6 = lp_dasmodel_CodeBuilder_emitInst(x_4, x_5);
x_7 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__1));
x_8 = lp_dasmodel_CodeBuilder_emitInst(x_6, x_7);
x_9 = !lean_is_exclusive(x_8);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; uint8_t x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; uint8_t x_28; 
x_10 = lean_ctor_get(x_8, 0);
x_11 = lean_ctor_get(x_8, 3);
x_12 = lean_array_get_size(x_10);
x_13 = lean_unsigned_to_nat(2u);
x_14 = lean_nat_sub(x_12, x_13);
x_15 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__2));
x_16 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_16, 0, x_14);
lean_ctor_set(x_16, 1, x_15);
x_17 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_11);
lean_ctor_set(x_8, 3, x_17);
x_18 = 27;
x_19 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__3));
x_20 = lp_dasmodel_CodeBuilder_emitBranch(x_8, x_18, x_19);
x_21 = 32;
x_22 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__4));
x_23 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_20, x_21, x_22);
x_24 = lp_dasmodel_CodeBuilder_label(x_23, x_19);
x_25 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__5, &lp_dasmodel_emitSustainEffects___closed__5_once, _init_lp_dasmodel_emitSustainEffects___closed__5);
x_26 = lp_dasmodel_CodeBuilder_emitInst(x_24, x_25);
x_27 = lp_dasmodel_CodeBuilder_emitInst(x_26, x_7);
x_28 = !lean_is_exclusive(x_27);
if (x_28 == 0)
{
lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; uint8_t x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; uint8_t x_76; 
x_29 = lean_ctor_get(x_27, 0);
x_30 = lean_ctor_get(x_27, 3);
x_31 = lean_array_get_size(x_29);
x_32 = lean_nat_sub(x_31, x_13);
x_33 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__6));
x_34 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_34, 0, x_32);
lean_ctor_set(x_34, 1, x_33);
x_35 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_35, 0, x_34);
lean_ctor_set(x_35, 1, x_30);
lean_ctor_set(x_27, 3, x_35);
x_36 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__7, &lp_dasmodel_emitSustainEffects___closed__7_once, _init_lp_dasmodel_emitSustainEffects___closed__7);
x_37 = lp_dasmodel_CodeBuilder_emitInst(x_27, x_36);
x_38 = 26;
x_39 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__8));
x_40 = lp_dasmodel_CodeBuilder_emitBranch(x_37, x_38, x_39);
x_41 = lp_dasmodel_I_clc;
x_42 = lp_dasmodel_CodeBuilder_emitInst(x_40, x_41);
x_43 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__38));
x_44 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_42, x_43);
x_45 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__9, &lp_dasmodel_emitSustainEffects___closed__9_once, _init_lp_dasmodel_emitSustainEffects___closed__9);
x_46 = lp_dasmodel_CodeBuilder_emitInst(x_44, x_45);
x_47 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_46, x_43);
x_48 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_49 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_47, x_48);
x_50 = lp_dasmodel_CodeBuilder_emitInst(x_49, x_5);
x_51 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_50, x_43);
x_52 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__34, &lp_dasmodel_emitNoteLoadPath___closed__34_once, _init_lp_dasmodel_emitNoteLoadPath___closed__34);
x_53 = lp_dasmodel_CodeBuilder_emitInst(x_51, x_52);
x_54 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_53, x_21, x_22);
x_55 = lp_dasmodel_CodeBuilder_label(x_54, x_39);
x_56 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__39));
x_57 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_55, x_56);
x_58 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__10));
x_59 = lp_dasmodel_CodeBuilder_emitBranch(x_57, x_18, x_58);
x_60 = lp_dasmodel_CodeBuilder_emitInst(x_59, x_41);
x_61 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_60, x_43);
x_62 = lp_dasmodel_CodeBuilder_emitInst(x_61, x_45);
x_63 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_62, x_43);
x_64 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__37));
x_65 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_63, x_64);
x_66 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__17, &lp_dasmodel_emitNoteLoadPath___closed__17_once, _init_lp_dasmodel_emitNoteLoadPath___closed__17);
x_67 = lp_dasmodel_CodeBuilder_emitInst(x_65, x_66);
x_68 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__11, &lp_dasmodel_emitSustainEffects___closed__11_once, _init_lp_dasmodel_emitSustainEffects___closed__11);
x_69 = lp_dasmodel_CodeBuilder_emitInst(x_67, x_68);
x_70 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_69, x_64);
x_71 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_70, x_3);
x_72 = lp_dasmodel_CodeBuilder_emitInst(x_71, x_5);
x_73 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_72, x_64);
x_74 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__12));
x_75 = lp_dasmodel_CodeBuilder_emitInst(x_73, x_74);
x_76 = !lean_is_exclusive(x_75);
if (x_76 == 0)
{
lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; uint8_t x_106; 
x_77 = lean_ctor_get(x_75, 0);
x_78 = lean_ctor_get(x_75, 3);
x_79 = lean_array_get_size(x_77);
x_80 = lean_nat_sub(x_79, x_13);
x_81 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__13));
x_82 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_82, 0, x_80);
lean_ctor_set(x_82, 1, x_81);
x_83 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_83, 0, x_82);
lean_ctor_set(x_83, 1, x_78);
lean_ctor_set(x_75, 3, x_83);
x_84 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__14));
x_85 = lp_dasmodel_CodeBuilder_emitBranch(x_75, x_18, x_84);
x_86 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__15, &lp_dasmodel_emitSustainEffects___closed__15_once, _init_lp_dasmodel_emitSustainEffects___closed__15);
x_87 = lp_dasmodel_CodeBuilder_emitInst(x_85, x_86);
x_88 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_87, x_56);
x_89 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_88, x_21, x_84);
x_90 = lp_dasmodel_CodeBuilder_label(x_89, x_58);
x_91 = lp_dasmodel_I_sec;
x_92 = lp_dasmodel_CodeBuilder_emitInst(x_90, x_91);
x_93 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_92, x_43);
x_94 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__16, &lp_dasmodel_emitSustainEffects___closed__16_once, _init_lp_dasmodel_emitSustainEffects___closed__16);
x_95 = lp_dasmodel_CodeBuilder_emitInst(x_93, x_94);
x_96 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_95, x_43);
x_97 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_96, x_64);
x_98 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__17, &lp_dasmodel_emitSustainEffects___closed__17_once, _init_lp_dasmodel_emitSustainEffects___closed__17);
x_99 = lp_dasmodel_CodeBuilder_emitInst(x_97, x_98);
x_100 = lp_dasmodel_CodeBuilder_emitInst(x_99, x_68);
x_101 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_100, x_64);
x_102 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_101, x_3);
x_103 = lp_dasmodel_CodeBuilder_emitInst(x_102, x_5);
x_104 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_103, x_64);
x_105 = lp_dasmodel_CodeBuilder_emitInst(x_104, x_74);
x_106 = !lean_is_exclusive(x_105);
if (x_106 == 0)
{
lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; uint8_t x_132; 
x_107 = lean_ctor_get(x_105, 0);
x_108 = lean_ctor_get(x_105, 3);
x_109 = lean_array_get_size(x_107);
x_110 = lean_nat_sub(x_109, x_13);
x_111 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__18));
x_112 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_112, 0, x_110);
lean_ctor_set(x_112, 1, x_111);
x_113 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_113, 0, x_112);
lean_ctor_set(x_113, 1, x_108);
lean_ctor_set(x_105, 3, x_113);
x_114 = lp_dasmodel_CodeBuilder_emitBranch(x_105, x_18, x_84);
x_115 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_116 = lp_dasmodel_CodeBuilder_emitInst(x_114, x_115);
x_117 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_116, x_56);
x_118 = lp_dasmodel_CodeBuilder_label(x_117, x_84);
x_119 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_118, x_48);
x_120 = lp_dasmodel_CodeBuilder_emitInst(x_119, x_5);
x_121 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_120, x_43);
x_122 = lp_dasmodel_CodeBuilder_emitInst(x_121, x_52);
x_123 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_122, x_64);
x_124 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__36, &lp_dasmodel_emitNoteLoadPath___closed__36_once, _init_lp_dasmodel_emitNoteLoadPath___closed__36);
x_125 = lp_dasmodel_CodeBuilder_emitInst(x_123, x_124);
x_126 = lp_dasmodel_CodeBuilder_label(x_125, x_22);
x_127 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_128 = lp_dasmodel_CodeBuilder_emitInst(x_126, x_127);
x_129 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_128, x_3);
x_130 = lp_dasmodel_CodeBuilder_emitInst(x_129, x_5);
x_131 = lp_dasmodel_CodeBuilder_emitInst(x_130, x_7);
x_132 = !lean_is_exclusive(x_131);
if (x_132 == 0)
{
lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; lean_object* x_139; lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; lean_object* x_150; lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_542; lean_object* x_543; lean_object* x_544; lean_object* x_545; lean_object* x_546; lean_object* x_547; lean_object* x_548; lean_object* x_549; lean_object* x_550; lean_object* x_551; lean_object* x_552; uint8_t x_553; 
x_133 = lean_ctor_get(x_131, 0);
x_134 = lean_ctor_get(x_131, 3);
x_135 = lean_array_get_size(x_133);
x_136 = lean_nat_sub(x_135, x_13);
x_137 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_138 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_138, 0, x_136);
lean_ctor_set(x_138, 1, x_137);
x_139 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_139, 0, x_138);
lean_ctor_set(x_139, 1, x_134);
lean_ctor_set(x_131, 3, x_139);
x_140 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__20));
x_141 = lp_dasmodel_CodeBuilder_emitBranch(x_131, x_18, x_140);
x_142 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__21));
x_143 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_141, x_21, x_142);
x_144 = lp_dasmodel_CodeBuilder_label(x_143, x_140);
x_145 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_146 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_144, x_145);
x_147 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__22));
x_148 = lp_dasmodel_CodeBuilder_emitBranch(x_146, x_18, x_147);
x_149 = lean_ctor_get(x_2, 4);
x_150 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_148, x_21, x_142);
x_151 = lp_dasmodel_CodeBuilder_label(x_150, x_147);
x_152 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_542 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_151, x_152);
x_543 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__40));
x_544 = lp_dasmodel_CodeBuilder_emitBranch(x_542, x_18, x_543);
x_545 = lean_unsigned_to_nat(3u);
x_546 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_544, x_21, x_142);
x_547 = lp_dasmodel_CodeBuilder_label(x_546, x_543);
x_548 = lp_dasmodel_CodeBuilder_emitInst(x_547, x_91);
x_549 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_550 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_548, x_549);
x_551 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__41, &lp_dasmodel_emitSustainEffects___closed__41_once, _init_lp_dasmodel_emitSustainEffects___closed__41);
x_552 = lp_dasmodel_CodeBuilder_emitInst(x_550, x_551);
x_553 = lean_nat_dec_eq(x_149, x_545);
if (x_553 == 0)
{
uint8_t x_554; 
x_554 = lean_nat_dec_eq(x_149, x_13);
if (x_554 == 0)
{
lean_object* x_555; uint8_t x_556; 
x_555 = lean_unsigned_to_nat(4u);
x_556 = lean_nat_dec_eq(x_149, x_555);
if (x_556 == 0)
{
x_153 = x_552;
goto block_541;
}
else
{
lean_object* x_557; lean_object* x_558; lean_object* x_559; 
x_557 = lp_dasmodel_I_asl__a;
x_558 = lp_dasmodel_CodeBuilder_emitInst(x_552, x_557);
x_559 = lp_dasmodel_CodeBuilder_emitInst(x_558, x_557);
x_153 = x_559;
goto block_541;
}
}
else
{
lean_object* x_560; lean_object* x_561; 
x_560 = lp_dasmodel_I_asl__a;
x_561 = lp_dasmodel_CodeBuilder_emitInst(x_552, x_560);
x_153 = x_561;
goto block_541;
}
}
else
{
lean_object* x_562; lean_object* x_563; lean_object* x_564; lean_object* x_565; lean_object* x_566; lean_object* x_567; lean_object* x_568; 
x_562 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__42, &lp_dasmodel_emitSustainEffects___closed__42_once, _init_lp_dasmodel_emitSustainEffects___closed__42);
x_563 = lp_dasmodel_CodeBuilder_emitInst(x_552, x_562);
x_564 = lp_dasmodel_I_asl__a;
x_565 = lp_dasmodel_CodeBuilder_emitInst(x_563, x_564);
x_566 = lp_dasmodel_CodeBuilder_emitInst(x_565, x_41);
x_567 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__43, &lp_dasmodel_emitSustainEffects___closed__43_once, _init_lp_dasmodel_emitSustainEffects___closed__43);
x_568 = lp_dasmodel_CodeBuilder_emitInst(x_566, x_567);
x_153 = x_568;
goto block_541;
}
block_541:
{
lean_object* x_154; lean_object* x_155; uint8_t x_156; 
x_154 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__24));
x_155 = lp_dasmodel_CodeBuilder_emitInst(x_153, x_154);
x_156 = !lean_is_exclusive(x_155);
if (x_156 == 0)
{
lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; lean_object* x_164; uint8_t x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; uint8_t x_172; 
x_157 = lean_ctor_get(x_155, 0);
x_158 = lean_ctor_get(x_155, 3);
x_159 = lean_array_get_size(x_157);
x_160 = lean_nat_sub(x_159, x_13);
x_161 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_161, 0, x_160);
lean_ctor_set(x_161, 1, x_152);
x_162 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_162, 0, x_161);
lean_ctor_set(x_162, 1, x_158);
lean_ctor_set(x_155, 3, x_162);
x_163 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_155, x_48);
x_164 = lp_dasmodel_CodeBuilder_emitInst(x_163, x_5);
x_165 = 24;
x_166 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__25));
x_167 = lp_dasmodel_CodeBuilder_emitBranch(x_164, x_165, x_166);
x_168 = lp_dasmodel_CodeBuilder_emitInst(x_167, x_127);
x_169 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_168, x_3);
x_170 = lp_dasmodel_CodeBuilder_emitInst(x_169, x_5);
x_171 = lp_dasmodel_CodeBuilder_emitInst(x_170, x_7);
x_172 = !lean_is_exclusive(x_171);
if (x_172 == 0)
{
lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; lean_object* x_191; lean_object* x_192; lean_object* x_193; lean_object* x_194; lean_object* x_195; lean_object* x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; lean_object* x_202; lean_object* x_203; lean_object* x_204; lean_object* x_205; lean_object* x_206; lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; lean_object* x_214; lean_object* x_215; uint8_t x_216; 
x_173 = lean_ctor_get(x_171, 0);
x_174 = lean_ctor_get(x_171, 3);
x_175 = lean_array_get_size(x_173);
x_176 = lean_nat_sub(x_175, x_13);
x_177 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_178 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_178, 0, x_176);
lean_ctor_set(x_178, 1, x_177);
x_179 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_179, 0, x_178);
lean_ctor_set(x_179, 1, x_174);
lean_ctor_set(x_171, 3, x_179);
x_180 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_181 = lp_dasmodel_CodeBuilder_emitInst(x_171, x_180);
x_182 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_181, x_145);
x_183 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_184 = lp_dasmodel_CodeBuilder_emitInst(x_182, x_183);
x_185 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_184, x_145);
x_186 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_185, x_48);
x_187 = lp_dasmodel_CodeBuilder_emitInst(x_186, x_5);
x_188 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_189 = lp_dasmodel_CodeBuilder_emitInst(x_187, x_188);
x_190 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_191 = lp_dasmodel_CodeBuilder_emitInst(x_189, x_190);
x_192 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_193 = lp_dasmodel_CodeBuilder_emitInst(x_191, x_192);
x_194 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_195 = lp_dasmodel_CodeBuilder_emitInst(x_193, x_194);
x_196 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_197 = lp_dasmodel_CodeBuilder_emitInst(x_195, x_196);
x_198 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_199 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_197, x_21, x_198);
x_200 = lp_dasmodel_CodeBuilder_label(x_199, x_166);
x_201 = lp_dasmodel_CodeBuilder_emitInst(x_200, x_127);
x_202 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_201, x_145);
x_203 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_202, x_48);
x_204 = lp_dasmodel_CodeBuilder_emitInst(x_203, x_5);
x_205 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_204, x_145);
x_206 = lp_dasmodel_CodeBuilder_emitInst(x_205, x_190);
x_207 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_208 = lp_dasmodel_CodeBuilder_emitInst(x_206, x_207);
x_209 = lp_dasmodel_CodeBuilder_emitInst(x_208, x_196);
x_210 = lp_dasmodel_CodeBuilder_label(x_209, x_198);
x_211 = lp_dasmodel_CodeBuilder_label(x_210, x_142);
x_212 = lp_dasmodel_CodeBuilder_emitInst(x_211, x_127);
x_213 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_212, x_3);
x_214 = lp_dasmodel_CodeBuilder_emitInst(x_213, x_5);
x_215 = lp_dasmodel_CodeBuilder_emitInst(x_214, x_7);
x_216 = !lean_is_exclusive(x_215);
if (x_216 == 0)
{
lean_object* x_217; lean_object* x_218; lean_object* x_219; lean_object* x_220; lean_object* x_221; lean_object* x_222; lean_object* x_223; lean_object* x_224; lean_object* x_225; lean_object* x_226; lean_object* x_227; lean_object* x_228; lean_object* x_229; lean_object* x_230; lean_object* x_231; lean_object* x_232; lean_object* x_233; lean_object* x_234; lean_object* x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; lean_object* x_239; lean_object* x_240; lean_object* x_241; lean_object* x_242; lean_object* x_243; lean_object* x_244; lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; lean_object* x_249; lean_object* x_250; lean_object* x_251; lean_object* x_252; lean_object* x_253; lean_object* x_254; lean_object* x_255; lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; lean_object* x_265; 
x_217 = lean_ctor_get(x_215, 0);
x_218 = lean_ctor_get(x_215, 3);
x_219 = lean_array_get_size(x_217);
x_220 = lean_nat_sub(x_219, x_13);
x_221 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_222 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_222, 0, x_220);
lean_ctor_set(x_222, 1, x_221);
x_223 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_223, 0, x_222);
lean_ctor_set(x_223, 1, x_218);
lean_ctor_set(x_215, 3, x_223);
x_224 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_225 = lp_dasmodel_CodeBuilder_emitBranch(x_215, x_18, x_224);
x_226 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_227 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_225, x_21, x_226);
x_228 = lp_dasmodel_CodeBuilder_label(x_227, x_224);
x_229 = lp_dasmodel_CodeBuilder_emitInst(x_228, x_183);
x_230 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_231 = lp_dasmodel_CodeBuilder_emitInst(x_229, x_230);
x_232 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_233 = lp_dasmodel_CodeBuilder_emitInst(x_231, x_232);
x_234 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_235 = lp_dasmodel_CodeBuilder_emitBranch(x_233, x_38, x_234);
x_236 = lp_dasmodel_CodeBuilder_emitInst(x_235, x_41);
x_237 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_238 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_236, x_237);
x_239 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_240 = lp_dasmodel_CodeBuilder_emitInst(x_238, x_239);
x_241 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_242 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_240, x_21, x_241);
x_243 = lp_dasmodel_CodeBuilder_label(x_242, x_234);
x_244 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_243, x_237);
x_245 = lp_dasmodel_CodeBuilder_label(x_244, x_241);
x_246 = lp_dasmodel_CodeBuilder_emitInst(x_245, x_5);
x_247 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_248 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_246, x_247);
x_249 = lp_dasmodel_CodeBuilder_emitInst(x_248, x_25);
x_250 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_251 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_249, x_250);
x_252 = lp_dasmodel_CodeBuilder_emitInst(x_251, x_183);
x_253 = lp_dasmodel_CodeBuilder_emitInst(x_252, x_127);
x_254 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_253, x_48);
x_255 = lp_dasmodel_CodeBuilder_emitInst(x_254, x_5);
x_256 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_257 = lp_dasmodel_CodeBuilder_emitInst(x_255, x_256);
x_258 = lp_dasmodel_CodeBuilder_emitInst(x_257, x_190);
x_259 = lp_dasmodel_CodeBuilder_emitInst(x_258, x_188);
x_260 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_261 = lp_dasmodel_CodeBuilder_emitInst(x_259, x_260);
x_262 = lp_dasmodel_CodeBuilder_label(x_261, x_226);
x_263 = lp_dasmodel_I_rts;
x_264 = lp_dasmodel_CodeBuilder_emitInst(x_262, x_263);
x_265 = lp_dasmodel_emitNoteLoadPath(x_264, x_2);
return x_265;
}
else
{
lean_object* x_266; uint16_t x_267; lean_object* x_268; lean_object* x_269; lean_object* x_270; lean_object* x_271; lean_object* x_272; lean_object* x_273; lean_object* x_274; lean_object* x_275; lean_object* x_276; lean_object* x_277; lean_object* x_278; lean_object* x_279; lean_object* x_280; lean_object* x_281; lean_object* x_282; lean_object* x_283; lean_object* x_284; lean_object* x_285; lean_object* x_286; lean_object* x_287; lean_object* x_288; lean_object* x_289; lean_object* x_290; lean_object* x_291; lean_object* x_292; lean_object* x_293; lean_object* x_294; lean_object* x_295; lean_object* x_296; lean_object* x_297; lean_object* x_298; lean_object* x_299; lean_object* x_300; lean_object* x_301; lean_object* x_302; lean_object* x_303; lean_object* x_304; lean_object* x_305; lean_object* x_306; lean_object* x_307; lean_object* x_308; lean_object* x_309; lean_object* x_310; lean_object* x_311; lean_object* x_312; lean_object* x_313; lean_object* x_314; lean_object* x_315; lean_object* x_316; lean_object* x_317; lean_object* x_318; 
x_266 = lean_ctor_get(x_215, 0);
x_267 = lean_ctor_get_uint16(x_215, sizeof(void*)*4);
x_268 = lean_ctor_get(x_215, 1);
x_269 = lean_ctor_get(x_215, 2);
x_270 = lean_ctor_get(x_215, 3);
lean_inc(x_270);
lean_inc(x_269);
lean_inc(x_268);
lean_inc(x_266);
lean_dec(x_215);
x_271 = lean_array_get_size(x_266);
x_272 = lean_nat_sub(x_271, x_13);
x_273 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_274 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_274, 0, x_272);
lean_ctor_set(x_274, 1, x_273);
x_275 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_275, 0, x_274);
lean_ctor_set(x_275, 1, x_270);
x_276 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_276, 0, x_266);
lean_ctor_set(x_276, 1, x_268);
lean_ctor_set(x_276, 2, x_269);
lean_ctor_set(x_276, 3, x_275);
lean_ctor_set_uint16(x_276, sizeof(void*)*4, x_267);
x_277 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_278 = lp_dasmodel_CodeBuilder_emitBranch(x_276, x_18, x_277);
x_279 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_280 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_278, x_21, x_279);
x_281 = lp_dasmodel_CodeBuilder_label(x_280, x_277);
x_282 = lp_dasmodel_CodeBuilder_emitInst(x_281, x_183);
x_283 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_284 = lp_dasmodel_CodeBuilder_emitInst(x_282, x_283);
x_285 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_286 = lp_dasmodel_CodeBuilder_emitInst(x_284, x_285);
x_287 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_288 = lp_dasmodel_CodeBuilder_emitBranch(x_286, x_38, x_287);
x_289 = lp_dasmodel_CodeBuilder_emitInst(x_288, x_41);
x_290 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_291 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_289, x_290);
x_292 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_293 = lp_dasmodel_CodeBuilder_emitInst(x_291, x_292);
x_294 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_295 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_293, x_21, x_294);
x_296 = lp_dasmodel_CodeBuilder_label(x_295, x_287);
x_297 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_296, x_290);
x_298 = lp_dasmodel_CodeBuilder_label(x_297, x_294);
x_299 = lp_dasmodel_CodeBuilder_emitInst(x_298, x_5);
x_300 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_301 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_299, x_300);
x_302 = lp_dasmodel_CodeBuilder_emitInst(x_301, x_25);
x_303 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_304 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_302, x_303);
x_305 = lp_dasmodel_CodeBuilder_emitInst(x_304, x_183);
x_306 = lp_dasmodel_CodeBuilder_emitInst(x_305, x_127);
x_307 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_306, x_48);
x_308 = lp_dasmodel_CodeBuilder_emitInst(x_307, x_5);
x_309 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_310 = lp_dasmodel_CodeBuilder_emitInst(x_308, x_309);
x_311 = lp_dasmodel_CodeBuilder_emitInst(x_310, x_190);
x_312 = lp_dasmodel_CodeBuilder_emitInst(x_311, x_188);
x_313 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_314 = lp_dasmodel_CodeBuilder_emitInst(x_312, x_313);
x_315 = lp_dasmodel_CodeBuilder_label(x_314, x_279);
x_316 = lp_dasmodel_I_rts;
x_317 = lp_dasmodel_CodeBuilder_emitInst(x_315, x_316);
x_318 = lp_dasmodel_emitNoteLoadPath(x_317, x_2);
return x_318;
}
}
else
{
lean_object* x_319; uint16_t x_320; lean_object* x_321; lean_object* x_322; lean_object* x_323; lean_object* x_324; lean_object* x_325; lean_object* x_326; lean_object* x_327; lean_object* x_328; lean_object* x_329; lean_object* x_330; lean_object* x_331; lean_object* x_332; lean_object* x_333; lean_object* x_334; lean_object* x_335; lean_object* x_336; lean_object* x_337; lean_object* x_338; lean_object* x_339; lean_object* x_340; lean_object* x_341; lean_object* x_342; lean_object* x_343; lean_object* x_344; lean_object* x_345; lean_object* x_346; lean_object* x_347; lean_object* x_348; lean_object* x_349; lean_object* x_350; lean_object* x_351; lean_object* x_352; lean_object* x_353; lean_object* x_354; lean_object* x_355; lean_object* x_356; lean_object* x_357; lean_object* x_358; lean_object* x_359; lean_object* x_360; lean_object* x_361; lean_object* x_362; lean_object* x_363; lean_object* x_364; lean_object* x_365; lean_object* x_366; uint16_t x_367; lean_object* x_368; lean_object* x_369; lean_object* x_370; lean_object* x_371; lean_object* x_372; lean_object* x_373; lean_object* x_374; lean_object* x_375; lean_object* x_376; lean_object* x_377; lean_object* x_378; lean_object* x_379; lean_object* x_380; lean_object* x_381; lean_object* x_382; lean_object* x_383; lean_object* x_384; lean_object* x_385; lean_object* x_386; lean_object* x_387; lean_object* x_388; lean_object* x_389; lean_object* x_390; lean_object* x_391; lean_object* x_392; lean_object* x_393; lean_object* x_394; lean_object* x_395; lean_object* x_396; lean_object* x_397; lean_object* x_398; lean_object* x_399; lean_object* x_400; lean_object* x_401; lean_object* x_402; lean_object* x_403; lean_object* x_404; lean_object* x_405; lean_object* x_406; lean_object* x_407; lean_object* x_408; lean_object* x_409; lean_object* x_410; lean_object* x_411; lean_object* x_412; lean_object* x_413; lean_object* x_414; lean_object* x_415; lean_object* x_416; lean_object* x_417; lean_object* x_418; lean_object* x_419; 
x_319 = lean_ctor_get(x_171, 0);
x_320 = lean_ctor_get_uint16(x_171, sizeof(void*)*4);
x_321 = lean_ctor_get(x_171, 1);
x_322 = lean_ctor_get(x_171, 2);
x_323 = lean_ctor_get(x_171, 3);
lean_inc(x_323);
lean_inc(x_322);
lean_inc(x_321);
lean_inc(x_319);
lean_dec(x_171);
x_324 = lean_array_get_size(x_319);
x_325 = lean_nat_sub(x_324, x_13);
x_326 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_327 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_327, 0, x_325);
lean_ctor_set(x_327, 1, x_326);
x_328 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_328, 0, x_327);
lean_ctor_set(x_328, 1, x_323);
x_329 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_329, 0, x_319);
lean_ctor_set(x_329, 1, x_321);
lean_ctor_set(x_329, 2, x_322);
lean_ctor_set(x_329, 3, x_328);
lean_ctor_set_uint16(x_329, sizeof(void*)*4, x_320);
x_330 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_331 = lp_dasmodel_CodeBuilder_emitInst(x_329, x_330);
x_332 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_331, x_145);
x_333 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_334 = lp_dasmodel_CodeBuilder_emitInst(x_332, x_333);
x_335 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_334, x_145);
x_336 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_335, x_48);
x_337 = lp_dasmodel_CodeBuilder_emitInst(x_336, x_5);
x_338 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_339 = lp_dasmodel_CodeBuilder_emitInst(x_337, x_338);
x_340 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_341 = lp_dasmodel_CodeBuilder_emitInst(x_339, x_340);
x_342 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_343 = lp_dasmodel_CodeBuilder_emitInst(x_341, x_342);
x_344 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_345 = lp_dasmodel_CodeBuilder_emitInst(x_343, x_344);
x_346 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_347 = lp_dasmodel_CodeBuilder_emitInst(x_345, x_346);
x_348 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_349 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_347, x_21, x_348);
x_350 = lp_dasmodel_CodeBuilder_label(x_349, x_166);
x_351 = lp_dasmodel_CodeBuilder_emitInst(x_350, x_127);
x_352 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_351, x_145);
x_353 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_352, x_48);
x_354 = lp_dasmodel_CodeBuilder_emitInst(x_353, x_5);
x_355 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_354, x_145);
x_356 = lp_dasmodel_CodeBuilder_emitInst(x_355, x_340);
x_357 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_358 = lp_dasmodel_CodeBuilder_emitInst(x_356, x_357);
x_359 = lp_dasmodel_CodeBuilder_emitInst(x_358, x_346);
x_360 = lp_dasmodel_CodeBuilder_label(x_359, x_348);
x_361 = lp_dasmodel_CodeBuilder_label(x_360, x_142);
x_362 = lp_dasmodel_CodeBuilder_emitInst(x_361, x_127);
x_363 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_362, x_3);
x_364 = lp_dasmodel_CodeBuilder_emitInst(x_363, x_5);
x_365 = lp_dasmodel_CodeBuilder_emitInst(x_364, x_7);
x_366 = lean_ctor_get(x_365, 0);
lean_inc_ref(x_366);
x_367 = lean_ctor_get_uint16(x_365, sizeof(void*)*4);
x_368 = lean_ctor_get(x_365, 1);
lean_inc(x_368);
x_369 = lean_ctor_get(x_365, 2);
lean_inc(x_369);
x_370 = lean_ctor_get(x_365, 3);
lean_inc(x_370);
if (lean_is_exclusive(x_365)) {
 lean_ctor_release(x_365, 0);
 lean_ctor_release(x_365, 1);
 lean_ctor_release(x_365, 2);
 lean_ctor_release(x_365, 3);
 x_371 = x_365;
} else {
 lean_dec_ref(x_365);
 x_371 = lean_box(0);
}
x_372 = lean_array_get_size(x_366);
x_373 = lean_nat_sub(x_372, x_13);
x_374 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_375 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_375, 0, x_373);
lean_ctor_set(x_375, 1, x_374);
x_376 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_376, 0, x_375);
lean_ctor_set(x_376, 1, x_370);
if (lean_is_scalar(x_371)) {
 x_377 = lean_alloc_ctor(0, 4, 2);
} else {
 x_377 = x_371;
}
lean_ctor_set(x_377, 0, x_366);
lean_ctor_set(x_377, 1, x_368);
lean_ctor_set(x_377, 2, x_369);
lean_ctor_set(x_377, 3, x_376);
lean_ctor_set_uint16(x_377, sizeof(void*)*4, x_367);
x_378 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_379 = lp_dasmodel_CodeBuilder_emitBranch(x_377, x_18, x_378);
x_380 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_381 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_379, x_21, x_380);
x_382 = lp_dasmodel_CodeBuilder_label(x_381, x_378);
x_383 = lp_dasmodel_CodeBuilder_emitInst(x_382, x_333);
x_384 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_385 = lp_dasmodel_CodeBuilder_emitInst(x_383, x_384);
x_386 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_387 = lp_dasmodel_CodeBuilder_emitInst(x_385, x_386);
x_388 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_389 = lp_dasmodel_CodeBuilder_emitBranch(x_387, x_38, x_388);
x_390 = lp_dasmodel_CodeBuilder_emitInst(x_389, x_41);
x_391 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_392 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_390, x_391);
x_393 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_394 = lp_dasmodel_CodeBuilder_emitInst(x_392, x_393);
x_395 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_396 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_394, x_21, x_395);
x_397 = lp_dasmodel_CodeBuilder_label(x_396, x_388);
x_398 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_397, x_391);
x_399 = lp_dasmodel_CodeBuilder_label(x_398, x_395);
x_400 = lp_dasmodel_CodeBuilder_emitInst(x_399, x_5);
x_401 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_402 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_400, x_401);
x_403 = lp_dasmodel_CodeBuilder_emitInst(x_402, x_25);
x_404 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_405 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_403, x_404);
x_406 = lp_dasmodel_CodeBuilder_emitInst(x_405, x_333);
x_407 = lp_dasmodel_CodeBuilder_emitInst(x_406, x_127);
x_408 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_407, x_48);
x_409 = lp_dasmodel_CodeBuilder_emitInst(x_408, x_5);
x_410 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_411 = lp_dasmodel_CodeBuilder_emitInst(x_409, x_410);
x_412 = lp_dasmodel_CodeBuilder_emitInst(x_411, x_340);
x_413 = lp_dasmodel_CodeBuilder_emitInst(x_412, x_338);
x_414 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_415 = lp_dasmodel_CodeBuilder_emitInst(x_413, x_414);
x_416 = lp_dasmodel_CodeBuilder_label(x_415, x_380);
x_417 = lp_dasmodel_I_rts;
x_418 = lp_dasmodel_CodeBuilder_emitInst(x_416, x_417);
x_419 = lp_dasmodel_emitNoteLoadPath(x_418, x_2);
return x_419;
}
}
else
{
lean_object* x_420; uint16_t x_421; lean_object* x_422; lean_object* x_423; lean_object* x_424; lean_object* x_425; lean_object* x_426; lean_object* x_427; lean_object* x_428; lean_object* x_429; lean_object* x_430; lean_object* x_431; uint8_t x_432; lean_object* x_433; lean_object* x_434; lean_object* x_435; lean_object* x_436; lean_object* x_437; lean_object* x_438; lean_object* x_439; uint16_t x_440; lean_object* x_441; lean_object* x_442; lean_object* x_443; lean_object* x_444; lean_object* x_445; lean_object* x_446; lean_object* x_447; lean_object* x_448; lean_object* x_449; lean_object* x_450; lean_object* x_451; lean_object* x_452; lean_object* x_453; lean_object* x_454; lean_object* x_455; lean_object* x_456; lean_object* x_457; lean_object* x_458; lean_object* x_459; lean_object* x_460; lean_object* x_461; lean_object* x_462; lean_object* x_463; lean_object* x_464; lean_object* x_465; lean_object* x_466; lean_object* x_467; lean_object* x_468; lean_object* x_469; lean_object* x_470; lean_object* x_471; lean_object* x_472; lean_object* x_473; lean_object* x_474; lean_object* x_475; lean_object* x_476; lean_object* x_477; lean_object* x_478; lean_object* x_479; lean_object* x_480; lean_object* x_481; lean_object* x_482; lean_object* x_483; lean_object* x_484; lean_object* x_485; lean_object* x_486; lean_object* x_487; uint16_t x_488; lean_object* x_489; lean_object* x_490; lean_object* x_491; lean_object* x_492; lean_object* x_493; lean_object* x_494; lean_object* x_495; lean_object* x_496; lean_object* x_497; lean_object* x_498; lean_object* x_499; lean_object* x_500; lean_object* x_501; lean_object* x_502; lean_object* x_503; lean_object* x_504; lean_object* x_505; lean_object* x_506; lean_object* x_507; lean_object* x_508; lean_object* x_509; lean_object* x_510; lean_object* x_511; lean_object* x_512; lean_object* x_513; lean_object* x_514; lean_object* x_515; lean_object* x_516; lean_object* x_517; lean_object* x_518; lean_object* x_519; lean_object* x_520; lean_object* x_521; lean_object* x_522; lean_object* x_523; lean_object* x_524; lean_object* x_525; lean_object* x_526; lean_object* x_527; lean_object* x_528; lean_object* x_529; lean_object* x_530; lean_object* x_531; lean_object* x_532; lean_object* x_533; lean_object* x_534; lean_object* x_535; lean_object* x_536; lean_object* x_537; lean_object* x_538; lean_object* x_539; lean_object* x_540; 
x_420 = lean_ctor_get(x_155, 0);
x_421 = lean_ctor_get_uint16(x_155, sizeof(void*)*4);
x_422 = lean_ctor_get(x_155, 1);
x_423 = lean_ctor_get(x_155, 2);
x_424 = lean_ctor_get(x_155, 3);
lean_inc(x_424);
lean_inc(x_423);
lean_inc(x_422);
lean_inc(x_420);
lean_dec(x_155);
x_425 = lean_array_get_size(x_420);
x_426 = lean_nat_sub(x_425, x_13);
x_427 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_427, 0, x_426);
lean_ctor_set(x_427, 1, x_152);
x_428 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_428, 0, x_427);
lean_ctor_set(x_428, 1, x_424);
x_429 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_429, 0, x_420);
lean_ctor_set(x_429, 1, x_422);
lean_ctor_set(x_429, 2, x_423);
lean_ctor_set(x_429, 3, x_428);
lean_ctor_set_uint16(x_429, sizeof(void*)*4, x_421);
x_430 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_429, x_48);
x_431 = lp_dasmodel_CodeBuilder_emitInst(x_430, x_5);
x_432 = 24;
x_433 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__25));
x_434 = lp_dasmodel_CodeBuilder_emitBranch(x_431, x_432, x_433);
x_435 = lp_dasmodel_CodeBuilder_emitInst(x_434, x_127);
x_436 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_435, x_3);
x_437 = lp_dasmodel_CodeBuilder_emitInst(x_436, x_5);
x_438 = lp_dasmodel_CodeBuilder_emitInst(x_437, x_7);
x_439 = lean_ctor_get(x_438, 0);
lean_inc_ref(x_439);
x_440 = lean_ctor_get_uint16(x_438, sizeof(void*)*4);
x_441 = lean_ctor_get(x_438, 1);
lean_inc(x_441);
x_442 = lean_ctor_get(x_438, 2);
lean_inc(x_442);
x_443 = lean_ctor_get(x_438, 3);
lean_inc(x_443);
if (lean_is_exclusive(x_438)) {
 lean_ctor_release(x_438, 0);
 lean_ctor_release(x_438, 1);
 lean_ctor_release(x_438, 2);
 lean_ctor_release(x_438, 3);
 x_444 = x_438;
} else {
 lean_dec_ref(x_438);
 x_444 = lean_box(0);
}
x_445 = lean_array_get_size(x_439);
x_446 = lean_nat_sub(x_445, x_13);
x_447 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_448 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_448, 0, x_446);
lean_ctor_set(x_448, 1, x_447);
x_449 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_449, 0, x_448);
lean_ctor_set(x_449, 1, x_443);
if (lean_is_scalar(x_444)) {
 x_450 = lean_alloc_ctor(0, 4, 2);
} else {
 x_450 = x_444;
}
lean_ctor_set(x_450, 0, x_439);
lean_ctor_set(x_450, 1, x_441);
lean_ctor_set(x_450, 2, x_442);
lean_ctor_set(x_450, 3, x_449);
lean_ctor_set_uint16(x_450, sizeof(void*)*4, x_440);
x_451 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_452 = lp_dasmodel_CodeBuilder_emitInst(x_450, x_451);
x_453 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_452, x_145);
x_454 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_455 = lp_dasmodel_CodeBuilder_emitInst(x_453, x_454);
x_456 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_455, x_145);
x_457 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_456, x_48);
x_458 = lp_dasmodel_CodeBuilder_emitInst(x_457, x_5);
x_459 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_460 = lp_dasmodel_CodeBuilder_emitInst(x_458, x_459);
x_461 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_462 = lp_dasmodel_CodeBuilder_emitInst(x_460, x_461);
x_463 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_464 = lp_dasmodel_CodeBuilder_emitInst(x_462, x_463);
x_465 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_466 = lp_dasmodel_CodeBuilder_emitInst(x_464, x_465);
x_467 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_468 = lp_dasmodel_CodeBuilder_emitInst(x_466, x_467);
x_469 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_470 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_468, x_21, x_469);
x_471 = lp_dasmodel_CodeBuilder_label(x_470, x_433);
x_472 = lp_dasmodel_CodeBuilder_emitInst(x_471, x_127);
x_473 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_472, x_145);
x_474 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_473, x_48);
x_475 = lp_dasmodel_CodeBuilder_emitInst(x_474, x_5);
x_476 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_475, x_145);
x_477 = lp_dasmodel_CodeBuilder_emitInst(x_476, x_461);
x_478 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_479 = lp_dasmodel_CodeBuilder_emitInst(x_477, x_478);
x_480 = lp_dasmodel_CodeBuilder_emitInst(x_479, x_467);
x_481 = lp_dasmodel_CodeBuilder_label(x_480, x_469);
x_482 = lp_dasmodel_CodeBuilder_label(x_481, x_142);
x_483 = lp_dasmodel_CodeBuilder_emitInst(x_482, x_127);
x_484 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_483, x_3);
x_485 = lp_dasmodel_CodeBuilder_emitInst(x_484, x_5);
x_486 = lp_dasmodel_CodeBuilder_emitInst(x_485, x_7);
x_487 = lean_ctor_get(x_486, 0);
lean_inc_ref(x_487);
x_488 = lean_ctor_get_uint16(x_486, sizeof(void*)*4);
x_489 = lean_ctor_get(x_486, 1);
lean_inc(x_489);
x_490 = lean_ctor_get(x_486, 2);
lean_inc(x_490);
x_491 = lean_ctor_get(x_486, 3);
lean_inc(x_491);
if (lean_is_exclusive(x_486)) {
 lean_ctor_release(x_486, 0);
 lean_ctor_release(x_486, 1);
 lean_ctor_release(x_486, 2);
 lean_ctor_release(x_486, 3);
 x_492 = x_486;
} else {
 lean_dec_ref(x_486);
 x_492 = lean_box(0);
}
x_493 = lean_array_get_size(x_487);
x_494 = lean_nat_sub(x_493, x_13);
x_495 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_496 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_496, 0, x_494);
lean_ctor_set(x_496, 1, x_495);
x_497 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_497, 0, x_496);
lean_ctor_set(x_497, 1, x_491);
if (lean_is_scalar(x_492)) {
 x_498 = lean_alloc_ctor(0, 4, 2);
} else {
 x_498 = x_492;
}
lean_ctor_set(x_498, 0, x_487);
lean_ctor_set(x_498, 1, x_489);
lean_ctor_set(x_498, 2, x_490);
lean_ctor_set(x_498, 3, x_497);
lean_ctor_set_uint16(x_498, sizeof(void*)*4, x_488);
x_499 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_500 = lp_dasmodel_CodeBuilder_emitBranch(x_498, x_18, x_499);
x_501 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_502 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_500, x_21, x_501);
x_503 = lp_dasmodel_CodeBuilder_label(x_502, x_499);
x_504 = lp_dasmodel_CodeBuilder_emitInst(x_503, x_454);
x_505 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_506 = lp_dasmodel_CodeBuilder_emitInst(x_504, x_505);
x_507 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_508 = lp_dasmodel_CodeBuilder_emitInst(x_506, x_507);
x_509 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_510 = lp_dasmodel_CodeBuilder_emitBranch(x_508, x_38, x_509);
x_511 = lp_dasmodel_CodeBuilder_emitInst(x_510, x_41);
x_512 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_513 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_511, x_512);
x_514 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_515 = lp_dasmodel_CodeBuilder_emitInst(x_513, x_514);
x_516 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_517 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_515, x_21, x_516);
x_518 = lp_dasmodel_CodeBuilder_label(x_517, x_509);
x_519 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_518, x_512);
x_520 = lp_dasmodel_CodeBuilder_label(x_519, x_516);
x_521 = lp_dasmodel_CodeBuilder_emitInst(x_520, x_5);
x_522 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_523 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_521, x_522);
x_524 = lp_dasmodel_CodeBuilder_emitInst(x_523, x_25);
x_525 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_526 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_524, x_525);
x_527 = lp_dasmodel_CodeBuilder_emitInst(x_526, x_454);
x_528 = lp_dasmodel_CodeBuilder_emitInst(x_527, x_127);
x_529 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_528, x_48);
x_530 = lp_dasmodel_CodeBuilder_emitInst(x_529, x_5);
x_531 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_532 = lp_dasmodel_CodeBuilder_emitInst(x_530, x_531);
x_533 = lp_dasmodel_CodeBuilder_emitInst(x_532, x_461);
x_534 = lp_dasmodel_CodeBuilder_emitInst(x_533, x_459);
x_535 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_536 = lp_dasmodel_CodeBuilder_emitInst(x_534, x_535);
x_537 = lp_dasmodel_CodeBuilder_label(x_536, x_501);
x_538 = lp_dasmodel_I_rts;
x_539 = lp_dasmodel_CodeBuilder_emitInst(x_537, x_538);
x_540 = lp_dasmodel_emitNoteLoadPath(x_539, x_2);
return x_540;
}
}
}
else
{
lean_object* x_569; uint16_t x_570; lean_object* x_571; lean_object* x_572; lean_object* x_573; lean_object* x_574; lean_object* x_575; lean_object* x_576; lean_object* x_577; lean_object* x_578; lean_object* x_579; lean_object* x_580; lean_object* x_581; lean_object* x_582; lean_object* x_583; lean_object* x_584; lean_object* x_585; lean_object* x_586; lean_object* x_587; lean_object* x_588; lean_object* x_589; lean_object* x_590; lean_object* x_591; lean_object* x_592; lean_object* x_593; lean_object* x_719; lean_object* x_720; lean_object* x_721; lean_object* x_722; lean_object* x_723; lean_object* x_724; lean_object* x_725; lean_object* x_726; lean_object* x_727; lean_object* x_728; lean_object* x_729; uint8_t x_730; 
x_569 = lean_ctor_get(x_131, 0);
x_570 = lean_ctor_get_uint16(x_131, sizeof(void*)*4);
x_571 = lean_ctor_get(x_131, 1);
x_572 = lean_ctor_get(x_131, 2);
x_573 = lean_ctor_get(x_131, 3);
lean_inc(x_573);
lean_inc(x_572);
lean_inc(x_571);
lean_inc(x_569);
lean_dec(x_131);
x_574 = lean_array_get_size(x_569);
x_575 = lean_nat_sub(x_574, x_13);
x_576 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_577 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_577, 0, x_575);
lean_ctor_set(x_577, 1, x_576);
x_578 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_578, 0, x_577);
lean_ctor_set(x_578, 1, x_573);
x_579 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_579, 0, x_569);
lean_ctor_set(x_579, 1, x_571);
lean_ctor_set(x_579, 2, x_572);
lean_ctor_set(x_579, 3, x_578);
lean_ctor_set_uint16(x_579, sizeof(void*)*4, x_570);
x_580 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__20));
x_581 = lp_dasmodel_CodeBuilder_emitBranch(x_579, x_18, x_580);
x_582 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__21));
x_583 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_581, x_21, x_582);
x_584 = lp_dasmodel_CodeBuilder_label(x_583, x_580);
x_585 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_586 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_584, x_585);
x_587 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__22));
x_588 = lp_dasmodel_CodeBuilder_emitBranch(x_586, x_18, x_587);
x_589 = lean_ctor_get(x_2, 4);
x_590 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_588, x_21, x_582);
x_591 = lp_dasmodel_CodeBuilder_label(x_590, x_587);
x_592 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_719 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_591, x_592);
x_720 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__40));
x_721 = lp_dasmodel_CodeBuilder_emitBranch(x_719, x_18, x_720);
x_722 = lean_unsigned_to_nat(3u);
x_723 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_721, x_21, x_582);
x_724 = lp_dasmodel_CodeBuilder_label(x_723, x_720);
x_725 = lp_dasmodel_CodeBuilder_emitInst(x_724, x_91);
x_726 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_727 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_725, x_726);
x_728 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__41, &lp_dasmodel_emitSustainEffects___closed__41_once, _init_lp_dasmodel_emitSustainEffects___closed__41);
x_729 = lp_dasmodel_CodeBuilder_emitInst(x_727, x_728);
x_730 = lean_nat_dec_eq(x_589, x_722);
if (x_730 == 0)
{
uint8_t x_731; 
x_731 = lean_nat_dec_eq(x_589, x_13);
if (x_731 == 0)
{
lean_object* x_732; uint8_t x_733; 
x_732 = lean_unsigned_to_nat(4u);
x_733 = lean_nat_dec_eq(x_589, x_732);
if (x_733 == 0)
{
x_593 = x_729;
goto block_718;
}
else
{
lean_object* x_734; lean_object* x_735; lean_object* x_736; 
x_734 = lp_dasmodel_I_asl__a;
x_735 = lp_dasmodel_CodeBuilder_emitInst(x_729, x_734);
x_736 = lp_dasmodel_CodeBuilder_emitInst(x_735, x_734);
x_593 = x_736;
goto block_718;
}
}
else
{
lean_object* x_737; lean_object* x_738; 
x_737 = lp_dasmodel_I_asl__a;
x_738 = lp_dasmodel_CodeBuilder_emitInst(x_729, x_737);
x_593 = x_738;
goto block_718;
}
}
else
{
lean_object* x_739; lean_object* x_740; lean_object* x_741; lean_object* x_742; lean_object* x_743; lean_object* x_744; lean_object* x_745; 
x_739 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__42, &lp_dasmodel_emitSustainEffects___closed__42_once, _init_lp_dasmodel_emitSustainEffects___closed__42);
x_740 = lp_dasmodel_CodeBuilder_emitInst(x_729, x_739);
x_741 = lp_dasmodel_I_asl__a;
x_742 = lp_dasmodel_CodeBuilder_emitInst(x_740, x_741);
x_743 = lp_dasmodel_CodeBuilder_emitInst(x_742, x_41);
x_744 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__43, &lp_dasmodel_emitSustainEffects___closed__43_once, _init_lp_dasmodel_emitSustainEffects___closed__43);
x_745 = lp_dasmodel_CodeBuilder_emitInst(x_743, x_744);
x_593 = x_745;
goto block_718;
}
block_718:
{
lean_object* x_594; lean_object* x_595; lean_object* x_596; uint16_t x_597; lean_object* x_598; lean_object* x_599; lean_object* x_600; lean_object* x_601; lean_object* x_602; lean_object* x_603; lean_object* x_604; lean_object* x_605; lean_object* x_606; lean_object* x_607; lean_object* x_608; uint8_t x_609; lean_object* x_610; lean_object* x_611; lean_object* x_612; lean_object* x_613; lean_object* x_614; lean_object* x_615; lean_object* x_616; uint16_t x_617; lean_object* x_618; lean_object* x_619; lean_object* x_620; lean_object* x_621; lean_object* x_622; lean_object* x_623; lean_object* x_624; lean_object* x_625; lean_object* x_626; lean_object* x_627; lean_object* x_628; lean_object* x_629; lean_object* x_630; lean_object* x_631; lean_object* x_632; lean_object* x_633; lean_object* x_634; lean_object* x_635; lean_object* x_636; lean_object* x_637; lean_object* x_638; lean_object* x_639; lean_object* x_640; lean_object* x_641; lean_object* x_642; lean_object* x_643; lean_object* x_644; lean_object* x_645; lean_object* x_646; lean_object* x_647; lean_object* x_648; lean_object* x_649; lean_object* x_650; lean_object* x_651; lean_object* x_652; lean_object* x_653; lean_object* x_654; lean_object* x_655; lean_object* x_656; lean_object* x_657; lean_object* x_658; lean_object* x_659; lean_object* x_660; lean_object* x_661; lean_object* x_662; lean_object* x_663; lean_object* x_664; uint16_t x_665; lean_object* x_666; lean_object* x_667; lean_object* x_668; lean_object* x_669; lean_object* x_670; lean_object* x_671; lean_object* x_672; lean_object* x_673; lean_object* x_674; lean_object* x_675; lean_object* x_676; lean_object* x_677; lean_object* x_678; lean_object* x_679; lean_object* x_680; lean_object* x_681; lean_object* x_682; lean_object* x_683; lean_object* x_684; lean_object* x_685; lean_object* x_686; lean_object* x_687; lean_object* x_688; lean_object* x_689; lean_object* x_690; lean_object* x_691; lean_object* x_692; lean_object* x_693; lean_object* x_694; lean_object* x_695; lean_object* x_696; lean_object* x_697; lean_object* x_698; lean_object* x_699; lean_object* x_700; lean_object* x_701; lean_object* x_702; lean_object* x_703; lean_object* x_704; lean_object* x_705; lean_object* x_706; lean_object* x_707; lean_object* x_708; lean_object* x_709; lean_object* x_710; lean_object* x_711; lean_object* x_712; lean_object* x_713; lean_object* x_714; lean_object* x_715; lean_object* x_716; lean_object* x_717; 
x_594 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__24));
x_595 = lp_dasmodel_CodeBuilder_emitInst(x_593, x_594);
x_596 = lean_ctor_get(x_595, 0);
lean_inc_ref(x_596);
x_597 = lean_ctor_get_uint16(x_595, sizeof(void*)*4);
x_598 = lean_ctor_get(x_595, 1);
lean_inc(x_598);
x_599 = lean_ctor_get(x_595, 2);
lean_inc(x_599);
x_600 = lean_ctor_get(x_595, 3);
lean_inc(x_600);
if (lean_is_exclusive(x_595)) {
 lean_ctor_release(x_595, 0);
 lean_ctor_release(x_595, 1);
 lean_ctor_release(x_595, 2);
 lean_ctor_release(x_595, 3);
 x_601 = x_595;
} else {
 lean_dec_ref(x_595);
 x_601 = lean_box(0);
}
x_602 = lean_array_get_size(x_596);
x_603 = lean_nat_sub(x_602, x_13);
x_604 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_604, 0, x_603);
lean_ctor_set(x_604, 1, x_592);
x_605 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_605, 0, x_604);
lean_ctor_set(x_605, 1, x_600);
if (lean_is_scalar(x_601)) {
 x_606 = lean_alloc_ctor(0, 4, 2);
} else {
 x_606 = x_601;
}
lean_ctor_set(x_606, 0, x_596);
lean_ctor_set(x_606, 1, x_598);
lean_ctor_set(x_606, 2, x_599);
lean_ctor_set(x_606, 3, x_605);
lean_ctor_set_uint16(x_606, sizeof(void*)*4, x_597);
x_607 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_606, x_48);
x_608 = lp_dasmodel_CodeBuilder_emitInst(x_607, x_5);
x_609 = 24;
x_610 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__25));
x_611 = lp_dasmodel_CodeBuilder_emitBranch(x_608, x_609, x_610);
x_612 = lp_dasmodel_CodeBuilder_emitInst(x_611, x_127);
x_613 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_612, x_3);
x_614 = lp_dasmodel_CodeBuilder_emitInst(x_613, x_5);
x_615 = lp_dasmodel_CodeBuilder_emitInst(x_614, x_7);
x_616 = lean_ctor_get(x_615, 0);
lean_inc_ref(x_616);
x_617 = lean_ctor_get_uint16(x_615, sizeof(void*)*4);
x_618 = lean_ctor_get(x_615, 1);
lean_inc(x_618);
x_619 = lean_ctor_get(x_615, 2);
lean_inc(x_619);
x_620 = lean_ctor_get(x_615, 3);
lean_inc(x_620);
if (lean_is_exclusive(x_615)) {
 lean_ctor_release(x_615, 0);
 lean_ctor_release(x_615, 1);
 lean_ctor_release(x_615, 2);
 lean_ctor_release(x_615, 3);
 x_621 = x_615;
} else {
 lean_dec_ref(x_615);
 x_621 = lean_box(0);
}
x_622 = lean_array_get_size(x_616);
x_623 = lean_nat_sub(x_622, x_13);
x_624 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_625 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_625, 0, x_623);
lean_ctor_set(x_625, 1, x_624);
x_626 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_626, 0, x_625);
lean_ctor_set(x_626, 1, x_620);
if (lean_is_scalar(x_621)) {
 x_627 = lean_alloc_ctor(0, 4, 2);
} else {
 x_627 = x_621;
}
lean_ctor_set(x_627, 0, x_616);
lean_ctor_set(x_627, 1, x_618);
lean_ctor_set(x_627, 2, x_619);
lean_ctor_set(x_627, 3, x_626);
lean_ctor_set_uint16(x_627, sizeof(void*)*4, x_617);
x_628 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_629 = lp_dasmodel_CodeBuilder_emitInst(x_627, x_628);
x_630 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_629, x_585);
x_631 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_632 = lp_dasmodel_CodeBuilder_emitInst(x_630, x_631);
x_633 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_632, x_585);
x_634 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_633, x_48);
x_635 = lp_dasmodel_CodeBuilder_emitInst(x_634, x_5);
x_636 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_637 = lp_dasmodel_CodeBuilder_emitInst(x_635, x_636);
x_638 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_639 = lp_dasmodel_CodeBuilder_emitInst(x_637, x_638);
x_640 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_641 = lp_dasmodel_CodeBuilder_emitInst(x_639, x_640);
x_642 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_643 = lp_dasmodel_CodeBuilder_emitInst(x_641, x_642);
x_644 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_645 = lp_dasmodel_CodeBuilder_emitInst(x_643, x_644);
x_646 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_647 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_645, x_21, x_646);
x_648 = lp_dasmodel_CodeBuilder_label(x_647, x_610);
x_649 = lp_dasmodel_CodeBuilder_emitInst(x_648, x_127);
x_650 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_649, x_585);
x_651 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_650, x_48);
x_652 = lp_dasmodel_CodeBuilder_emitInst(x_651, x_5);
x_653 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_652, x_585);
x_654 = lp_dasmodel_CodeBuilder_emitInst(x_653, x_638);
x_655 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_656 = lp_dasmodel_CodeBuilder_emitInst(x_654, x_655);
x_657 = lp_dasmodel_CodeBuilder_emitInst(x_656, x_644);
x_658 = lp_dasmodel_CodeBuilder_label(x_657, x_646);
x_659 = lp_dasmodel_CodeBuilder_label(x_658, x_582);
x_660 = lp_dasmodel_CodeBuilder_emitInst(x_659, x_127);
x_661 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_660, x_3);
x_662 = lp_dasmodel_CodeBuilder_emitInst(x_661, x_5);
x_663 = lp_dasmodel_CodeBuilder_emitInst(x_662, x_7);
x_664 = lean_ctor_get(x_663, 0);
lean_inc_ref(x_664);
x_665 = lean_ctor_get_uint16(x_663, sizeof(void*)*4);
x_666 = lean_ctor_get(x_663, 1);
lean_inc(x_666);
x_667 = lean_ctor_get(x_663, 2);
lean_inc(x_667);
x_668 = lean_ctor_get(x_663, 3);
lean_inc(x_668);
if (lean_is_exclusive(x_663)) {
 lean_ctor_release(x_663, 0);
 lean_ctor_release(x_663, 1);
 lean_ctor_release(x_663, 2);
 lean_ctor_release(x_663, 3);
 x_669 = x_663;
} else {
 lean_dec_ref(x_663);
 x_669 = lean_box(0);
}
x_670 = lean_array_get_size(x_664);
x_671 = lean_nat_sub(x_670, x_13);
x_672 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_673 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_673, 0, x_671);
lean_ctor_set(x_673, 1, x_672);
x_674 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_674, 0, x_673);
lean_ctor_set(x_674, 1, x_668);
if (lean_is_scalar(x_669)) {
 x_675 = lean_alloc_ctor(0, 4, 2);
} else {
 x_675 = x_669;
}
lean_ctor_set(x_675, 0, x_664);
lean_ctor_set(x_675, 1, x_666);
lean_ctor_set(x_675, 2, x_667);
lean_ctor_set(x_675, 3, x_674);
lean_ctor_set_uint16(x_675, sizeof(void*)*4, x_665);
x_676 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_677 = lp_dasmodel_CodeBuilder_emitBranch(x_675, x_18, x_676);
x_678 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_679 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_677, x_21, x_678);
x_680 = lp_dasmodel_CodeBuilder_label(x_679, x_676);
x_681 = lp_dasmodel_CodeBuilder_emitInst(x_680, x_631);
x_682 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_683 = lp_dasmodel_CodeBuilder_emitInst(x_681, x_682);
x_684 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_685 = lp_dasmodel_CodeBuilder_emitInst(x_683, x_684);
x_686 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_687 = lp_dasmodel_CodeBuilder_emitBranch(x_685, x_38, x_686);
x_688 = lp_dasmodel_CodeBuilder_emitInst(x_687, x_41);
x_689 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_690 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_688, x_689);
x_691 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_692 = lp_dasmodel_CodeBuilder_emitInst(x_690, x_691);
x_693 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_694 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_692, x_21, x_693);
x_695 = lp_dasmodel_CodeBuilder_label(x_694, x_686);
x_696 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_695, x_689);
x_697 = lp_dasmodel_CodeBuilder_label(x_696, x_693);
x_698 = lp_dasmodel_CodeBuilder_emitInst(x_697, x_5);
x_699 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_700 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_698, x_699);
x_701 = lp_dasmodel_CodeBuilder_emitInst(x_700, x_25);
x_702 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_703 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_701, x_702);
x_704 = lp_dasmodel_CodeBuilder_emitInst(x_703, x_631);
x_705 = lp_dasmodel_CodeBuilder_emitInst(x_704, x_127);
x_706 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_705, x_48);
x_707 = lp_dasmodel_CodeBuilder_emitInst(x_706, x_5);
x_708 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_709 = lp_dasmodel_CodeBuilder_emitInst(x_707, x_708);
x_710 = lp_dasmodel_CodeBuilder_emitInst(x_709, x_638);
x_711 = lp_dasmodel_CodeBuilder_emitInst(x_710, x_636);
x_712 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_713 = lp_dasmodel_CodeBuilder_emitInst(x_711, x_712);
x_714 = lp_dasmodel_CodeBuilder_label(x_713, x_678);
x_715 = lp_dasmodel_I_rts;
x_716 = lp_dasmodel_CodeBuilder_emitInst(x_714, x_715);
x_717 = lp_dasmodel_emitNoteLoadPath(x_716, x_2);
return x_717;
}
}
}
else
{
lean_object* x_746; uint16_t x_747; lean_object* x_748; lean_object* x_749; lean_object* x_750; lean_object* x_751; lean_object* x_752; lean_object* x_753; lean_object* x_754; lean_object* x_755; lean_object* x_756; lean_object* x_757; lean_object* x_758; lean_object* x_759; lean_object* x_760; lean_object* x_761; lean_object* x_762; lean_object* x_763; lean_object* x_764; lean_object* x_765; lean_object* x_766; lean_object* x_767; lean_object* x_768; lean_object* x_769; lean_object* x_770; lean_object* x_771; lean_object* x_772; lean_object* x_773; lean_object* x_774; lean_object* x_775; uint16_t x_776; lean_object* x_777; lean_object* x_778; lean_object* x_779; lean_object* x_780; lean_object* x_781; lean_object* x_782; lean_object* x_783; lean_object* x_784; lean_object* x_785; lean_object* x_786; lean_object* x_787; lean_object* x_788; lean_object* x_789; lean_object* x_790; lean_object* x_791; lean_object* x_792; lean_object* x_793; lean_object* x_794; lean_object* x_795; lean_object* x_796; lean_object* x_797; lean_object* x_798; lean_object* x_799; lean_object* x_800; lean_object* x_926; lean_object* x_927; lean_object* x_928; lean_object* x_929; lean_object* x_930; lean_object* x_931; lean_object* x_932; lean_object* x_933; lean_object* x_934; lean_object* x_935; lean_object* x_936; uint8_t x_937; 
x_746 = lean_ctor_get(x_105, 0);
x_747 = lean_ctor_get_uint16(x_105, sizeof(void*)*4);
x_748 = lean_ctor_get(x_105, 1);
x_749 = lean_ctor_get(x_105, 2);
x_750 = lean_ctor_get(x_105, 3);
lean_inc(x_750);
lean_inc(x_749);
lean_inc(x_748);
lean_inc(x_746);
lean_dec(x_105);
x_751 = lean_array_get_size(x_746);
x_752 = lean_nat_sub(x_751, x_13);
x_753 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__18));
x_754 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_754, 0, x_752);
lean_ctor_set(x_754, 1, x_753);
x_755 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_755, 0, x_754);
lean_ctor_set(x_755, 1, x_750);
x_756 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_756, 0, x_746);
lean_ctor_set(x_756, 1, x_748);
lean_ctor_set(x_756, 2, x_749);
lean_ctor_set(x_756, 3, x_755);
lean_ctor_set_uint16(x_756, sizeof(void*)*4, x_747);
x_757 = lp_dasmodel_CodeBuilder_emitBranch(x_756, x_18, x_84);
x_758 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_759 = lp_dasmodel_CodeBuilder_emitInst(x_757, x_758);
x_760 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_759, x_56);
x_761 = lp_dasmodel_CodeBuilder_label(x_760, x_84);
x_762 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_761, x_48);
x_763 = lp_dasmodel_CodeBuilder_emitInst(x_762, x_5);
x_764 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_763, x_43);
x_765 = lp_dasmodel_CodeBuilder_emitInst(x_764, x_52);
x_766 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_765, x_64);
x_767 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__36, &lp_dasmodel_emitNoteLoadPath___closed__36_once, _init_lp_dasmodel_emitNoteLoadPath___closed__36);
x_768 = lp_dasmodel_CodeBuilder_emitInst(x_766, x_767);
x_769 = lp_dasmodel_CodeBuilder_label(x_768, x_22);
x_770 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_771 = lp_dasmodel_CodeBuilder_emitInst(x_769, x_770);
x_772 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_771, x_3);
x_773 = lp_dasmodel_CodeBuilder_emitInst(x_772, x_5);
x_774 = lp_dasmodel_CodeBuilder_emitInst(x_773, x_7);
x_775 = lean_ctor_get(x_774, 0);
lean_inc_ref(x_775);
x_776 = lean_ctor_get_uint16(x_774, sizeof(void*)*4);
x_777 = lean_ctor_get(x_774, 1);
lean_inc(x_777);
x_778 = lean_ctor_get(x_774, 2);
lean_inc(x_778);
x_779 = lean_ctor_get(x_774, 3);
lean_inc(x_779);
if (lean_is_exclusive(x_774)) {
 lean_ctor_release(x_774, 0);
 lean_ctor_release(x_774, 1);
 lean_ctor_release(x_774, 2);
 lean_ctor_release(x_774, 3);
 x_780 = x_774;
} else {
 lean_dec_ref(x_774);
 x_780 = lean_box(0);
}
x_781 = lean_array_get_size(x_775);
x_782 = lean_nat_sub(x_781, x_13);
x_783 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_784 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_784, 0, x_782);
lean_ctor_set(x_784, 1, x_783);
x_785 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_785, 0, x_784);
lean_ctor_set(x_785, 1, x_779);
if (lean_is_scalar(x_780)) {
 x_786 = lean_alloc_ctor(0, 4, 2);
} else {
 x_786 = x_780;
}
lean_ctor_set(x_786, 0, x_775);
lean_ctor_set(x_786, 1, x_777);
lean_ctor_set(x_786, 2, x_778);
lean_ctor_set(x_786, 3, x_785);
lean_ctor_set_uint16(x_786, sizeof(void*)*4, x_776);
x_787 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__20));
x_788 = lp_dasmodel_CodeBuilder_emitBranch(x_786, x_18, x_787);
x_789 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__21));
x_790 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_788, x_21, x_789);
x_791 = lp_dasmodel_CodeBuilder_label(x_790, x_787);
x_792 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_793 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_791, x_792);
x_794 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__22));
x_795 = lp_dasmodel_CodeBuilder_emitBranch(x_793, x_18, x_794);
x_796 = lean_ctor_get(x_2, 4);
x_797 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_795, x_21, x_789);
x_798 = lp_dasmodel_CodeBuilder_label(x_797, x_794);
x_799 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_926 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_798, x_799);
x_927 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__40));
x_928 = lp_dasmodel_CodeBuilder_emitBranch(x_926, x_18, x_927);
x_929 = lean_unsigned_to_nat(3u);
x_930 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_928, x_21, x_789);
x_931 = lp_dasmodel_CodeBuilder_label(x_930, x_927);
x_932 = lp_dasmodel_CodeBuilder_emitInst(x_931, x_91);
x_933 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_934 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_932, x_933);
x_935 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__41, &lp_dasmodel_emitSustainEffects___closed__41_once, _init_lp_dasmodel_emitSustainEffects___closed__41);
x_936 = lp_dasmodel_CodeBuilder_emitInst(x_934, x_935);
x_937 = lean_nat_dec_eq(x_796, x_929);
if (x_937 == 0)
{
uint8_t x_938; 
x_938 = lean_nat_dec_eq(x_796, x_13);
if (x_938 == 0)
{
lean_object* x_939; uint8_t x_940; 
x_939 = lean_unsigned_to_nat(4u);
x_940 = lean_nat_dec_eq(x_796, x_939);
if (x_940 == 0)
{
x_800 = x_936;
goto block_925;
}
else
{
lean_object* x_941; lean_object* x_942; lean_object* x_943; 
x_941 = lp_dasmodel_I_asl__a;
x_942 = lp_dasmodel_CodeBuilder_emitInst(x_936, x_941);
x_943 = lp_dasmodel_CodeBuilder_emitInst(x_942, x_941);
x_800 = x_943;
goto block_925;
}
}
else
{
lean_object* x_944; lean_object* x_945; 
x_944 = lp_dasmodel_I_asl__a;
x_945 = lp_dasmodel_CodeBuilder_emitInst(x_936, x_944);
x_800 = x_945;
goto block_925;
}
}
else
{
lean_object* x_946; lean_object* x_947; lean_object* x_948; lean_object* x_949; lean_object* x_950; lean_object* x_951; lean_object* x_952; 
x_946 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__42, &lp_dasmodel_emitSustainEffects___closed__42_once, _init_lp_dasmodel_emitSustainEffects___closed__42);
x_947 = lp_dasmodel_CodeBuilder_emitInst(x_936, x_946);
x_948 = lp_dasmodel_I_asl__a;
x_949 = lp_dasmodel_CodeBuilder_emitInst(x_947, x_948);
x_950 = lp_dasmodel_CodeBuilder_emitInst(x_949, x_41);
x_951 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__43, &lp_dasmodel_emitSustainEffects___closed__43_once, _init_lp_dasmodel_emitSustainEffects___closed__43);
x_952 = lp_dasmodel_CodeBuilder_emitInst(x_950, x_951);
x_800 = x_952;
goto block_925;
}
block_925:
{
lean_object* x_801; lean_object* x_802; lean_object* x_803; uint16_t x_804; lean_object* x_805; lean_object* x_806; lean_object* x_807; lean_object* x_808; lean_object* x_809; lean_object* x_810; lean_object* x_811; lean_object* x_812; lean_object* x_813; lean_object* x_814; lean_object* x_815; uint8_t x_816; lean_object* x_817; lean_object* x_818; lean_object* x_819; lean_object* x_820; lean_object* x_821; lean_object* x_822; lean_object* x_823; uint16_t x_824; lean_object* x_825; lean_object* x_826; lean_object* x_827; lean_object* x_828; lean_object* x_829; lean_object* x_830; lean_object* x_831; lean_object* x_832; lean_object* x_833; lean_object* x_834; lean_object* x_835; lean_object* x_836; lean_object* x_837; lean_object* x_838; lean_object* x_839; lean_object* x_840; lean_object* x_841; lean_object* x_842; lean_object* x_843; lean_object* x_844; lean_object* x_845; lean_object* x_846; lean_object* x_847; lean_object* x_848; lean_object* x_849; lean_object* x_850; lean_object* x_851; lean_object* x_852; lean_object* x_853; lean_object* x_854; lean_object* x_855; lean_object* x_856; lean_object* x_857; lean_object* x_858; lean_object* x_859; lean_object* x_860; lean_object* x_861; lean_object* x_862; lean_object* x_863; lean_object* x_864; lean_object* x_865; lean_object* x_866; lean_object* x_867; lean_object* x_868; lean_object* x_869; lean_object* x_870; lean_object* x_871; uint16_t x_872; lean_object* x_873; lean_object* x_874; lean_object* x_875; lean_object* x_876; lean_object* x_877; lean_object* x_878; lean_object* x_879; lean_object* x_880; lean_object* x_881; lean_object* x_882; lean_object* x_883; lean_object* x_884; lean_object* x_885; lean_object* x_886; lean_object* x_887; lean_object* x_888; lean_object* x_889; lean_object* x_890; lean_object* x_891; lean_object* x_892; lean_object* x_893; lean_object* x_894; lean_object* x_895; lean_object* x_896; lean_object* x_897; lean_object* x_898; lean_object* x_899; lean_object* x_900; lean_object* x_901; lean_object* x_902; lean_object* x_903; lean_object* x_904; lean_object* x_905; lean_object* x_906; lean_object* x_907; lean_object* x_908; lean_object* x_909; lean_object* x_910; lean_object* x_911; lean_object* x_912; lean_object* x_913; lean_object* x_914; lean_object* x_915; lean_object* x_916; lean_object* x_917; lean_object* x_918; lean_object* x_919; lean_object* x_920; lean_object* x_921; lean_object* x_922; lean_object* x_923; lean_object* x_924; 
x_801 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__24));
x_802 = lp_dasmodel_CodeBuilder_emitInst(x_800, x_801);
x_803 = lean_ctor_get(x_802, 0);
lean_inc_ref(x_803);
x_804 = lean_ctor_get_uint16(x_802, sizeof(void*)*4);
x_805 = lean_ctor_get(x_802, 1);
lean_inc(x_805);
x_806 = lean_ctor_get(x_802, 2);
lean_inc(x_806);
x_807 = lean_ctor_get(x_802, 3);
lean_inc(x_807);
if (lean_is_exclusive(x_802)) {
 lean_ctor_release(x_802, 0);
 lean_ctor_release(x_802, 1);
 lean_ctor_release(x_802, 2);
 lean_ctor_release(x_802, 3);
 x_808 = x_802;
} else {
 lean_dec_ref(x_802);
 x_808 = lean_box(0);
}
x_809 = lean_array_get_size(x_803);
x_810 = lean_nat_sub(x_809, x_13);
x_811 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_811, 0, x_810);
lean_ctor_set(x_811, 1, x_799);
x_812 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_812, 0, x_811);
lean_ctor_set(x_812, 1, x_807);
if (lean_is_scalar(x_808)) {
 x_813 = lean_alloc_ctor(0, 4, 2);
} else {
 x_813 = x_808;
}
lean_ctor_set(x_813, 0, x_803);
lean_ctor_set(x_813, 1, x_805);
lean_ctor_set(x_813, 2, x_806);
lean_ctor_set(x_813, 3, x_812);
lean_ctor_set_uint16(x_813, sizeof(void*)*4, x_804);
x_814 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_813, x_48);
x_815 = lp_dasmodel_CodeBuilder_emitInst(x_814, x_5);
x_816 = 24;
x_817 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__25));
x_818 = lp_dasmodel_CodeBuilder_emitBranch(x_815, x_816, x_817);
x_819 = lp_dasmodel_CodeBuilder_emitInst(x_818, x_770);
x_820 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_819, x_3);
x_821 = lp_dasmodel_CodeBuilder_emitInst(x_820, x_5);
x_822 = lp_dasmodel_CodeBuilder_emitInst(x_821, x_7);
x_823 = lean_ctor_get(x_822, 0);
lean_inc_ref(x_823);
x_824 = lean_ctor_get_uint16(x_822, sizeof(void*)*4);
x_825 = lean_ctor_get(x_822, 1);
lean_inc(x_825);
x_826 = lean_ctor_get(x_822, 2);
lean_inc(x_826);
x_827 = lean_ctor_get(x_822, 3);
lean_inc(x_827);
if (lean_is_exclusive(x_822)) {
 lean_ctor_release(x_822, 0);
 lean_ctor_release(x_822, 1);
 lean_ctor_release(x_822, 2);
 lean_ctor_release(x_822, 3);
 x_828 = x_822;
} else {
 lean_dec_ref(x_822);
 x_828 = lean_box(0);
}
x_829 = lean_array_get_size(x_823);
x_830 = lean_nat_sub(x_829, x_13);
x_831 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_832 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_832, 0, x_830);
lean_ctor_set(x_832, 1, x_831);
x_833 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_833, 0, x_832);
lean_ctor_set(x_833, 1, x_827);
if (lean_is_scalar(x_828)) {
 x_834 = lean_alloc_ctor(0, 4, 2);
} else {
 x_834 = x_828;
}
lean_ctor_set(x_834, 0, x_823);
lean_ctor_set(x_834, 1, x_825);
lean_ctor_set(x_834, 2, x_826);
lean_ctor_set(x_834, 3, x_833);
lean_ctor_set_uint16(x_834, sizeof(void*)*4, x_824);
x_835 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_836 = lp_dasmodel_CodeBuilder_emitInst(x_834, x_835);
x_837 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_836, x_792);
x_838 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_839 = lp_dasmodel_CodeBuilder_emitInst(x_837, x_838);
x_840 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_839, x_792);
x_841 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_840, x_48);
x_842 = lp_dasmodel_CodeBuilder_emitInst(x_841, x_5);
x_843 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_844 = lp_dasmodel_CodeBuilder_emitInst(x_842, x_843);
x_845 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_846 = lp_dasmodel_CodeBuilder_emitInst(x_844, x_845);
x_847 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_848 = lp_dasmodel_CodeBuilder_emitInst(x_846, x_847);
x_849 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_850 = lp_dasmodel_CodeBuilder_emitInst(x_848, x_849);
x_851 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_852 = lp_dasmodel_CodeBuilder_emitInst(x_850, x_851);
x_853 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_854 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_852, x_21, x_853);
x_855 = lp_dasmodel_CodeBuilder_label(x_854, x_817);
x_856 = lp_dasmodel_CodeBuilder_emitInst(x_855, x_770);
x_857 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_856, x_792);
x_858 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_857, x_48);
x_859 = lp_dasmodel_CodeBuilder_emitInst(x_858, x_5);
x_860 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_859, x_792);
x_861 = lp_dasmodel_CodeBuilder_emitInst(x_860, x_845);
x_862 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_863 = lp_dasmodel_CodeBuilder_emitInst(x_861, x_862);
x_864 = lp_dasmodel_CodeBuilder_emitInst(x_863, x_851);
x_865 = lp_dasmodel_CodeBuilder_label(x_864, x_853);
x_866 = lp_dasmodel_CodeBuilder_label(x_865, x_789);
x_867 = lp_dasmodel_CodeBuilder_emitInst(x_866, x_770);
x_868 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_867, x_3);
x_869 = lp_dasmodel_CodeBuilder_emitInst(x_868, x_5);
x_870 = lp_dasmodel_CodeBuilder_emitInst(x_869, x_7);
x_871 = lean_ctor_get(x_870, 0);
lean_inc_ref(x_871);
x_872 = lean_ctor_get_uint16(x_870, sizeof(void*)*4);
x_873 = lean_ctor_get(x_870, 1);
lean_inc(x_873);
x_874 = lean_ctor_get(x_870, 2);
lean_inc(x_874);
x_875 = lean_ctor_get(x_870, 3);
lean_inc(x_875);
if (lean_is_exclusive(x_870)) {
 lean_ctor_release(x_870, 0);
 lean_ctor_release(x_870, 1);
 lean_ctor_release(x_870, 2);
 lean_ctor_release(x_870, 3);
 x_876 = x_870;
} else {
 lean_dec_ref(x_870);
 x_876 = lean_box(0);
}
x_877 = lean_array_get_size(x_871);
x_878 = lean_nat_sub(x_877, x_13);
x_879 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_880 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_880, 0, x_878);
lean_ctor_set(x_880, 1, x_879);
x_881 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_881, 0, x_880);
lean_ctor_set(x_881, 1, x_875);
if (lean_is_scalar(x_876)) {
 x_882 = lean_alloc_ctor(0, 4, 2);
} else {
 x_882 = x_876;
}
lean_ctor_set(x_882, 0, x_871);
lean_ctor_set(x_882, 1, x_873);
lean_ctor_set(x_882, 2, x_874);
lean_ctor_set(x_882, 3, x_881);
lean_ctor_set_uint16(x_882, sizeof(void*)*4, x_872);
x_883 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_884 = lp_dasmodel_CodeBuilder_emitBranch(x_882, x_18, x_883);
x_885 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_886 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_884, x_21, x_885);
x_887 = lp_dasmodel_CodeBuilder_label(x_886, x_883);
x_888 = lp_dasmodel_CodeBuilder_emitInst(x_887, x_838);
x_889 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_890 = lp_dasmodel_CodeBuilder_emitInst(x_888, x_889);
x_891 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_892 = lp_dasmodel_CodeBuilder_emitInst(x_890, x_891);
x_893 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_894 = lp_dasmodel_CodeBuilder_emitBranch(x_892, x_38, x_893);
x_895 = lp_dasmodel_CodeBuilder_emitInst(x_894, x_41);
x_896 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_897 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_895, x_896);
x_898 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_899 = lp_dasmodel_CodeBuilder_emitInst(x_897, x_898);
x_900 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_901 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_899, x_21, x_900);
x_902 = lp_dasmodel_CodeBuilder_label(x_901, x_893);
x_903 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_902, x_896);
x_904 = lp_dasmodel_CodeBuilder_label(x_903, x_900);
x_905 = lp_dasmodel_CodeBuilder_emitInst(x_904, x_5);
x_906 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_907 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_905, x_906);
x_908 = lp_dasmodel_CodeBuilder_emitInst(x_907, x_25);
x_909 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_910 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_908, x_909);
x_911 = lp_dasmodel_CodeBuilder_emitInst(x_910, x_838);
x_912 = lp_dasmodel_CodeBuilder_emitInst(x_911, x_770);
x_913 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_912, x_48);
x_914 = lp_dasmodel_CodeBuilder_emitInst(x_913, x_5);
x_915 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_916 = lp_dasmodel_CodeBuilder_emitInst(x_914, x_915);
x_917 = lp_dasmodel_CodeBuilder_emitInst(x_916, x_845);
x_918 = lp_dasmodel_CodeBuilder_emitInst(x_917, x_843);
x_919 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_920 = lp_dasmodel_CodeBuilder_emitInst(x_918, x_919);
x_921 = lp_dasmodel_CodeBuilder_label(x_920, x_885);
x_922 = lp_dasmodel_I_rts;
x_923 = lp_dasmodel_CodeBuilder_emitInst(x_921, x_922);
x_924 = lp_dasmodel_emitNoteLoadPath(x_923, x_2);
return x_924;
}
}
}
else
{
lean_object* x_953; uint16_t x_954; lean_object* x_955; lean_object* x_956; lean_object* x_957; lean_object* x_958; lean_object* x_959; lean_object* x_960; lean_object* x_961; lean_object* x_962; lean_object* x_963; lean_object* x_964; lean_object* x_965; lean_object* x_966; lean_object* x_967; lean_object* x_968; lean_object* x_969; lean_object* x_970; lean_object* x_971; lean_object* x_972; lean_object* x_973; lean_object* x_974; lean_object* x_975; lean_object* x_976; lean_object* x_977; lean_object* x_978; lean_object* x_979; lean_object* x_980; lean_object* x_981; lean_object* x_982; lean_object* x_983; lean_object* x_984; lean_object* x_985; lean_object* x_986; uint16_t x_987; lean_object* x_988; lean_object* x_989; lean_object* x_990; lean_object* x_991; lean_object* x_992; lean_object* x_993; lean_object* x_994; lean_object* x_995; lean_object* x_996; lean_object* x_997; lean_object* x_998; lean_object* x_999; lean_object* x_1000; lean_object* x_1001; lean_object* x_1002; lean_object* x_1003; lean_object* x_1004; lean_object* x_1005; lean_object* x_1006; lean_object* x_1007; lean_object* x_1008; lean_object* x_1009; lean_object* x_1010; lean_object* x_1011; lean_object* x_1012; lean_object* x_1013; lean_object* x_1014; lean_object* x_1015; lean_object* x_1016; uint16_t x_1017; lean_object* x_1018; lean_object* x_1019; lean_object* x_1020; lean_object* x_1021; lean_object* x_1022; lean_object* x_1023; lean_object* x_1024; lean_object* x_1025; lean_object* x_1026; lean_object* x_1027; lean_object* x_1028; lean_object* x_1029; lean_object* x_1030; lean_object* x_1031; lean_object* x_1032; lean_object* x_1033; lean_object* x_1034; lean_object* x_1035; lean_object* x_1036; lean_object* x_1037; lean_object* x_1038; lean_object* x_1039; lean_object* x_1040; lean_object* x_1041; lean_object* x_1167; lean_object* x_1168; lean_object* x_1169; lean_object* x_1170; lean_object* x_1171; lean_object* x_1172; lean_object* x_1173; lean_object* x_1174; lean_object* x_1175; lean_object* x_1176; lean_object* x_1177; uint8_t x_1178; 
x_953 = lean_ctor_get(x_75, 0);
x_954 = lean_ctor_get_uint16(x_75, sizeof(void*)*4);
x_955 = lean_ctor_get(x_75, 1);
x_956 = lean_ctor_get(x_75, 2);
x_957 = lean_ctor_get(x_75, 3);
lean_inc(x_957);
lean_inc(x_956);
lean_inc(x_955);
lean_inc(x_953);
lean_dec(x_75);
x_958 = lean_array_get_size(x_953);
x_959 = lean_nat_sub(x_958, x_13);
x_960 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__13));
x_961 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_961, 0, x_959);
lean_ctor_set(x_961, 1, x_960);
x_962 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_962, 0, x_961);
lean_ctor_set(x_962, 1, x_957);
x_963 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_963, 0, x_953);
lean_ctor_set(x_963, 1, x_955);
lean_ctor_set(x_963, 2, x_956);
lean_ctor_set(x_963, 3, x_962);
lean_ctor_set_uint16(x_963, sizeof(void*)*4, x_954);
x_964 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__14));
x_965 = lp_dasmodel_CodeBuilder_emitBranch(x_963, x_18, x_964);
x_966 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__15, &lp_dasmodel_emitSustainEffects___closed__15_once, _init_lp_dasmodel_emitSustainEffects___closed__15);
x_967 = lp_dasmodel_CodeBuilder_emitInst(x_965, x_966);
x_968 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_967, x_56);
x_969 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_968, x_21, x_964);
x_970 = lp_dasmodel_CodeBuilder_label(x_969, x_58);
x_971 = lp_dasmodel_I_sec;
x_972 = lp_dasmodel_CodeBuilder_emitInst(x_970, x_971);
x_973 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_972, x_43);
x_974 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__16, &lp_dasmodel_emitSustainEffects___closed__16_once, _init_lp_dasmodel_emitSustainEffects___closed__16);
x_975 = lp_dasmodel_CodeBuilder_emitInst(x_973, x_974);
x_976 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_975, x_43);
x_977 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_976, x_64);
x_978 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__17, &lp_dasmodel_emitSustainEffects___closed__17_once, _init_lp_dasmodel_emitSustainEffects___closed__17);
x_979 = lp_dasmodel_CodeBuilder_emitInst(x_977, x_978);
x_980 = lp_dasmodel_CodeBuilder_emitInst(x_979, x_68);
x_981 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_980, x_64);
x_982 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_981, x_3);
x_983 = lp_dasmodel_CodeBuilder_emitInst(x_982, x_5);
x_984 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_983, x_64);
x_985 = lp_dasmodel_CodeBuilder_emitInst(x_984, x_74);
x_986 = lean_ctor_get(x_985, 0);
lean_inc_ref(x_986);
x_987 = lean_ctor_get_uint16(x_985, sizeof(void*)*4);
x_988 = lean_ctor_get(x_985, 1);
lean_inc(x_988);
x_989 = lean_ctor_get(x_985, 2);
lean_inc(x_989);
x_990 = lean_ctor_get(x_985, 3);
lean_inc(x_990);
if (lean_is_exclusive(x_985)) {
 lean_ctor_release(x_985, 0);
 lean_ctor_release(x_985, 1);
 lean_ctor_release(x_985, 2);
 lean_ctor_release(x_985, 3);
 x_991 = x_985;
} else {
 lean_dec_ref(x_985);
 x_991 = lean_box(0);
}
x_992 = lean_array_get_size(x_986);
x_993 = lean_nat_sub(x_992, x_13);
x_994 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__18));
x_995 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_995, 0, x_993);
lean_ctor_set(x_995, 1, x_994);
x_996 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_996, 0, x_995);
lean_ctor_set(x_996, 1, x_990);
if (lean_is_scalar(x_991)) {
 x_997 = lean_alloc_ctor(0, 4, 2);
} else {
 x_997 = x_991;
}
lean_ctor_set(x_997, 0, x_986);
lean_ctor_set(x_997, 1, x_988);
lean_ctor_set(x_997, 2, x_989);
lean_ctor_set(x_997, 3, x_996);
lean_ctor_set_uint16(x_997, sizeof(void*)*4, x_987);
x_998 = lp_dasmodel_CodeBuilder_emitBranch(x_997, x_18, x_964);
x_999 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_1000 = lp_dasmodel_CodeBuilder_emitInst(x_998, x_999);
x_1001 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1000, x_56);
x_1002 = lp_dasmodel_CodeBuilder_label(x_1001, x_964);
x_1003 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1002, x_48);
x_1004 = lp_dasmodel_CodeBuilder_emitInst(x_1003, x_5);
x_1005 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1004, x_43);
x_1006 = lp_dasmodel_CodeBuilder_emitInst(x_1005, x_52);
x_1007 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1006, x_64);
x_1008 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__36, &lp_dasmodel_emitNoteLoadPath___closed__36_once, _init_lp_dasmodel_emitNoteLoadPath___closed__36);
x_1009 = lp_dasmodel_CodeBuilder_emitInst(x_1007, x_1008);
x_1010 = lp_dasmodel_CodeBuilder_label(x_1009, x_22);
x_1011 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_1012 = lp_dasmodel_CodeBuilder_emitInst(x_1010, x_1011);
x_1013 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1012, x_3);
x_1014 = lp_dasmodel_CodeBuilder_emitInst(x_1013, x_5);
x_1015 = lp_dasmodel_CodeBuilder_emitInst(x_1014, x_7);
x_1016 = lean_ctor_get(x_1015, 0);
lean_inc_ref(x_1016);
x_1017 = lean_ctor_get_uint16(x_1015, sizeof(void*)*4);
x_1018 = lean_ctor_get(x_1015, 1);
lean_inc(x_1018);
x_1019 = lean_ctor_get(x_1015, 2);
lean_inc(x_1019);
x_1020 = lean_ctor_get(x_1015, 3);
lean_inc(x_1020);
if (lean_is_exclusive(x_1015)) {
 lean_ctor_release(x_1015, 0);
 lean_ctor_release(x_1015, 1);
 lean_ctor_release(x_1015, 2);
 lean_ctor_release(x_1015, 3);
 x_1021 = x_1015;
} else {
 lean_dec_ref(x_1015);
 x_1021 = lean_box(0);
}
x_1022 = lean_array_get_size(x_1016);
x_1023 = lean_nat_sub(x_1022, x_13);
x_1024 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_1025 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1025, 0, x_1023);
lean_ctor_set(x_1025, 1, x_1024);
x_1026 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1026, 0, x_1025);
lean_ctor_set(x_1026, 1, x_1020);
if (lean_is_scalar(x_1021)) {
 x_1027 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1027 = x_1021;
}
lean_ctor_set(x_1027, 0, x_1016);
lean_ctor_set(x_1027, 1, x_1018);
lean_ctor_set(x_1027, 2, x_1019);
lean_ctor_set(x_1027, 3, x_1026);
lean_ctor_set_uint16(x_1027, sizeof(void*)*4, x_1017);
x_1028 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__20));
x_1029 = lp_dasmodel_CodeBuilder_emitBranch(x_1027, x_18, x_1028);
x_1030 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__21));
x_1031 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1029, x_21, x_1030);
x_1032 = lp_dasmodel_CodeBuilder_label(x_1031, x_1028);
x_1033 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_1034 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1032, x_1033);
x_1035 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__22));
x_1036 = lp_dasmodel_CodeBuilder_emitBranch(x_1034, x_18, x_1035);
x_1037 = lean_ctor_get(x_2, 4);
x_1038 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1036, x_21, x_1030);
x_1039 = lp_dasmodel_CodeBuilder_label(x_1038, x_1035);
x_1040 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_1167 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1039, x_1040);
x_1168 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__40));
x_1169 = lp_dasmodel_CodeBuilder_emitBranch(x_1167, x_18, x_1168);
x_1170 = lean_unsigned_to_nat(3u);
x_1171 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1169, x_21, x_1030);
x_1172 = lp_dasmodel_CodeBuilder_label(x_1171, x_1168);
x_1173 = lp_dasmodel_CodeBuilder_emitInst(x_1172, x_971);
x_1174 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_1175 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1173, x_1174);
x_1176 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__41, &lp_dasmodel_emitSustainEffects___closed__41_once, _init_lp_dasmodel_emitSustainEffects___closed__41);
x_1177 = lp_dasmodel_CodeBuilder_emitInst(x_1175, x_1176);
x_1178 = lean_nat_dec_eq(x_1037, x_1170);
if (x_1178 == 0)
{
uint8_t x_1179; 
x_1179 = lean_nat_dec_eq(x_1037, x_13);
if (x_1179 == 0)
{
lean_object* x_1180; uint8_t x_1181; 
x_1180 = lean_unsigned_to_nat(4u);
x_1181 = lean_nat_dec_eq(x_1037, x_1180);
if (x_1181 == 0)
{
x_1041 = x_1177;
goto block_1166;
}
else
{
lean_object* x_1182; lean_object* x_1183; lean_object* x_1184; 
x_1182 = lp_dasmodel_I_asl__a;
x_1183 = lp_dasmodel_CodeBuilder_emitInst(x_1177, x_1182);
x_1184 = lp_dasmodel_CodeBuilder_emitInst(x_1183, x_1182);
x_1041 = x_1184;
goto block_1166;
}
}
else
{
lean_object* x_1185; lean_object* x_1186; 
x_1185 = lp_dasmodel_I_asl__a;
x_1186 = lp_dasmodel_CodeBuilder_emitInst(x_1177, x_1185);
x_1041 = x_1186;
goto block_1166;
}
}
else
{
lean_object* x_1187; lean_object* x_1188; lean_object* x_1189; lean_object* x_1190; lean_object* x_1191; lean_object* x_1192; lean_object* x_1193; 
x_1187 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__42, &lp_dasmodel_emitSustainEffects___closed__42_once, _init_lp_dasmodel_emitSustainEffects___closed__42);
x_1188 = lp_dasmodel_CodeBuilder_emitInst(x_1177, x_1187);
x_1189 = lp_dasmodel_I_asl__a;
x_1190 = lp_dasmodel_CodeBuilder_emitInst(x_1188, x_1189);
x_1191 = lp_dasmodel_CodeBuilder_emitInst(x_1190, x_41);
x_1192 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__43, &lp_dasmodel_emitSustainEffects___closed__43_once, _init_lp_dasmodel_emitSustainEffects___closed__43);
x_1193 = lp_dasmodel_CodeBuilder_emitInst(x_1191, x_1192);
x_1041 = x_1193;
goto block_1166;
}
block_1166:
{
lean_object* x_1042; lean_object* x_1043; lean_object* x_1044; uint16_t x_1045; lean_object* x_1046; lean_object* x_1047; lean_object* x_1048; lean_object* x_1049; lean_object* x_1050; lean_object* x_1051; lean_object* x_1052; lean_object* x_1053; lean_object* x_1054; lean_object* x_1055; lean_object* x_1056; uint8_t x_1057; lean_object* x_1058; lean_object* x_1059; lean_object* x_1060; lean_object* x_1061; lean_object* x_1062; lean_object* x_1063; lean_object* x_1064; uint16_t x_1065; lean_object* x_1066; lean_object* x_1067; lean_object* x_1068; lean_object* x_1069; lean_object* x_1070; lean_object* x_1071; lean_object* x_1072; lean_object* x_1073; lean_object* x_1074; lean_object* x_1075; lean_object* x_1076; lean_object* x_1077; lean_object* x_1078; lean_object* x_1079; lean_object* x_1080; lean_object* x_1081; lean_object* x_1082; lean_object* x_1083; lean_object* x_1084; lean_object* x_1085; lean_object* x_1086; lean_object* x_1087; lean_object* x_1088; lean_object* x_1089; lean_object* x_1090; lean_object* x_1091; lean_object* x_1092; lean_object* x_1093; lean_object* x_1094; lean_object* x_1095; lean_object* x_1096; lean_object* x_1097; lean_object* x_1098; lean_object* x_1099; lean_object* x_1100; lean_object* x_1101; lean_object* x_1102; lean_object* x_1103; lean_object* x_1104; lean_object* x_1105; lean_object* x_1106; lean_object* x_1107; lean_object* x_1108; lean_object* x_1109; lean_object* x_1110; lean_object* x_1111; lean_object* x_1112; uint16_t x_1113; lean_object* x_1114; lean_object* x_1115; lean_object* x_1116; lean_object* x_1117; lean_object* x_1118; lean_object* x_1119; lean_object* x_1120; lean_object* x_1121; lean_object* x_1122; lean_object* x_1123; lean_object* x_1124; lean_object* x_1125; lean_object* x_1126; lean_object* x_1127; lean_object* x_1128; lean_object* x_1129; lean_object* x_1130; lean_object* x_1131; lean_object* x_1132; lean_object* x_1133; lean_object* x_1134; lean_object* x_1135; lean_object* x_1136; lean_object* x_1137; lean_object* x_1138; lean_object* x_1139; lean_object* x_1140; lean_object* x_1141; lean_object* x_1142; lean_object* x_1143; lean_object* x_1144; lean_object* x_1145; lean_object* x_1146; lean_object* x_1147; lean_object* x_1148; lean_object* x_1149; lean_object* x_1150; lean_object* x_1151; lean_object* x_1152; lean_object* x_1153; lean_object* x_1154; lean_object* x_1155; lean_object* x_1156; lean_object* x_1157; lean_object* x_1158; lean_object* x_1159; lean_object* x_1160; lean_object* x_1161; lean_object* x_1162; lean_object* x_1163; lean_object* x_1164; lean_object* x_1165; 
x_1042 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__24));
x_1043 = lp_dasmodel_CodeBuilder_emitInst(x_1041, x_1042);
x_1044 = lean_ctor_get(x_1043, 0);
lean_inc_ref(x_1044);
x_1045 = lean_ctor_get_uint16(x_1043, sizeof(void*)*4);
x_1046 = lean_ctor_get(x_1043, 1);
lean_inc(x_1046);
x_1047 = lean_ctor_get(x_1043, 2);
lean_inc(x_1047);
x_1048 = lean_ctor_get(x_1043, 3);
lean_inc(x_1048);
if (lean_is_exclusive(x_1043)) {
 lean_ctor_release(x_1043, 0);
 lean_ctor_release(x_1043, 1);
 lean_ctor_release(x_1043, 2);
 lean_ctor_release(x_1043, 3);
 x_1049 = x_1043;
} else {
 lean_dec_ref(x_1043);
 x_1049 = lean_box(0);
}
x_1050 = lean_array_get_size(x_1044);
x_1051 = lean_nat_sub(x_1050, x_13);
x_1052 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1052, 0, x_1051);
lean_ctor_set(x_1052, 1, x_1040);
x_1053 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1053, 0, x_1052);
lean_ctor_set(x_1053, 1, x_1048);
if (lean_is_scalar(x_1049)) {
 x_1054 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1054 = x_1049;
}
lean_ctor_set(x_1054, 0, x_1044);
lean_ctor_set(x_1054, 1, x_1046);
lean_ctor_set(x_1054, 2, x_1047);
lean_ctor_set(x_1054, 3, x_1053);
lean_ctor_set_uint16(x_1054, sizeof(void*)*4, x_1045);
x_1055 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1054, x_48);
x_1056 = lp_dasmodel_CodeBuilder_emitInst(x_1055, x_5);
x_1057 = 24;
x_1058 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__25));
x_1059 = lp_dasmodel_CodeBuilder_emitBranch(x_1056, x_1057, x_1058);
x_1060 = lp_dasmodel_CodeBuilder_emitInst(x_1059, x_1011);
x_1061 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1060, x_3);
x_1062 = lp_dasmodel_CodeBuilder_emitInst(x_1061, x_5);
x_1063 = lp_dasmodel_CodeBuilder_emitInst(x_1062, x_7);
x_1064 = lean_ctor_get(x_1063, 0);
lean_inc_ref(x_1064);
x_1065 = lean_ctor_get_uint16(x_1063, sizeof(void*)*4);
x_1066 = lean_ctor_get(x_1063, 1);
lean_inc(x_1066);
x_1067 = lean_ctor_get(x_1063, 2);
lean_inc(x_1067);
x_1068 = lean_ctor_get(x_1063, 3);
lean_inc(x_1068);
if (lean_is_exclusive(x_1063)) {
 lean_ctor_release(x_1063, 0);
 lean_ctor_release(x_1063, 1);
 lean_ctor_release(x_1063, 2);
 lean_ctor_release(x_1063, 3);
 x_1069 = x_1063;
} else {
 lean_dec_ref(x_1063);
 x_1069 = lean_box(0);
}
x_1070 = lean_array_get_size(x_1064);
x_1071 = lean_nat_sub(x_1070, x_13);
x_1072 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_1073 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1073, 0, x_1071);
lean_ctor_set(x_1073, 1, x_1072);
x_1074 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1074, 0, x_1073);
lean_ctor_set(x_1074, 1, x_1068);
if (lean_is_scalar(x_1069)) {
 x_1075 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1075 = x_1069;
}
lean_ctor_set(x_1075, 0, x_1064);
lean_ctor_set(x_1075, 1, x_1066);
lean_ctor_set(x_1075, 2, x_1067);
lean_ctor_set(x_1075, 3, x_1074);
lean_ctor_set_uint16(x_1075, sizeof(void*)*4, x_1065);
x_1076 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_1077 = lp_dasmodel_CodeBuilder_emitInst(x_1075, x_1076);
x_1078 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1077, x_1033);
x_1079 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_1080 = lp_dasmodel_CodeBuilder_emitInst(x_1078, x_1079);
x_1081 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_1080, x_1033);
x_1082 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1081, x_48);
x_1083 = lp_dasmodel_CodeBuilder_emitInst(x_1082, x_5);
x_1084 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_1085 = lp_dasmodel_CodeBuilder_emitInst(x_1083, x_1084);
x_1086 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_1087 = lp_dasmodel_CodeBuilder_emitInst(x_1085, x_1086);
x_1088 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_1089 = lp_dasmodel_CodeBuilder_emitInst(x_1087, x_1088);
x_1090 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_1091 = lp_dasmodel_CodeBuilder_emitInst(x_1089, x_1090);
x_1092 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_1093 = lp_dasmodel_CodeBuilder_emitInst(x_1091, x_1092);
x_1094 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_1095 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1093, x_21, x_1094);
x_1096 = lp_dasmodel_CodeBuilder_label(x_1095, x_1058);
x_1097 = lp_dasmodel_CodeBuilder_emitInst(x_1096, x_1011);
x_1098 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1097, x_1033);
x_1099 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1098, x_48);
x_1100 = lp_dasmodel_CodeBuilder_emitInst(x_1099, x_5);
x_1101 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1100, x_1033);
x_1102 = lp_dasmodel_CodeBuilder_emitInst(x_1101, x_1086);
x_1103 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_1104 = lp_dasmodel_CodeBuilder_emitInst(x_1102, x_1103);
x_1105 = lp_dasmodel_CodeBuilder_emitInst(x_1104, x_1092);
x_1106 = lp_dasmodel_CodeBuilder_label(x_1105, x_1094);
x_1107 = lp_dasmodel_CodeBuilder_label(x_1106, x_1030);
x_1108 = lp_dasmodel_CodeBuilder_emitInst(x_1107, x_1011);
x_1109 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1108, x_3);
x_1110 = lp_dasmodel_CodeBuilder_emitInst(x_1109, x_5);
x_1111 = lp_dasmodel_CodeBuilder_emitInst(x_1110, x_7);
x_1112 = lean_ctor_get(x_1111, 0);
lean_inc_ref(x_1112);
x_1113 = lean_ctor_get_uint16(x_1111, sizeof(void*)*4);
x_1114 = lean_ctor_get(x_1111, 1);
lean_inc(x_1114);
x_1115 = lean_ctor_get(x_1111, 2);
lean_inc(x_1115);
x_1116 = lean_ctor_get(x_1111, 3);
lean_inc(x_1116);
if (lean_is_exclusive(x_1111)) {
 lean_ctor_release(x_1111, 0);
 lean_ctor_release(x_1111, 1);
 lean_ctor_release(x_1111, 2);
 lean_ctor_release(x_1111, 3);
 x_1117 = x_1111;
} else {
 lean_dec_ref(x_1111);
 x_1117 = lean_box(0);
}
x_1118 = lean_array_get_size(x_1112);
x_1119 = lean_nat_sub(x_1118, x_13);
x_1120 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_1121 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1121, 0, x_1119);
lean_ctor_set(x_1121, 1, x_1120);
x_1122 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1122, 0, x_1121);
lean_ctor_set(x_1122, 1, x_1116);
if (lean_is_scalar(x_1117)) {
 x_1123 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1123 = x_1117;
}
lean_ctor_set(x_1123, 0, x_1112);
lean_ctor_set(x_1123, 1, x_1114);
lean_ctor_set(x_1123, 2, x_1115);
lean_ctor_set(x_1123, 3, x_1122);
lean_ctor_set_uint16(x_1123, sizeof(void*)*4, x_1113);
x_1124 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_1125 = lp_dasmodel_CodeBuilder_emitBranch(x_1123, x_18, x_1124);
x_1126 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_1127 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1125, x_21, x_1126);
x_1128 = lp_dasmodel_CodeBuilder_label(x_1127, x_1124);
x_1129 = lp_dasmodel_CodeBuilder_emitInst(x_1128, x_1079);
x_1130 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_1131 = lp_dasmodel_CodeBuilder_emitInst(x_1129, x_1130);
x_1132 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_1133 = lp_dasmodel_CodeBuilder_emitInst(x_1131, x_1132);
x_1134 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_1135 = lp_dasmodel_CodeBuilder_emitBranch(x_1133, x_38, x_1134);
x_1136 = lp_dasmodel_CodeBuilder_emitInst(x_1135, x_41);
x_1137 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_1138 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1136, x_1137);
x_1139 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_1140 = lp_dasmodel_CodeBuilder_emitInst(x_1138, x_1139);
x_1141 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_1142 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1140, x_21, x_1141);
x_1143 = lp_dasmodel_CodeBuilder_label(x_1142, x_1134);
x_1144 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1143, x_1137);
x_1145 = lp_dasmodel_CodeBuilder_label(x_1144, x_1141);
x_1146 = lp_dasmodel_CodeBuilder_emitInst(x_1145, x_5);
x_1147 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_1148 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_1146, x_1147);
x_1149 = lp_dasmodel_CodeBuilder_emitInst(x_1148, x_25);
x_1150 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_1151 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_1149, x_1150);
x_1152 = lp_dasmodel_CodeBuilder_emitInst(x_1151, x_1079);
x_1153 = lp_dasmodel_CodeBuilder_emitInst(x_1152, x_1011);
x_1154 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1153, x_48);
x_1155 = lp_dasmodel_CodeBuilder_emitInst(x_1154, x_5);
x_1156 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_1157 = lp_dasmodel_CodeBuilder_emitInst(x_1155, x_1156);
x_1158 = lp_dasmodel_CodeBuilder_emitInst(x_1157, x_1086);
x_1159 = lp_dasmodel_CodeBuilder_emitInst(x_1158, x_1084);
x_1160 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_1161 = lp_dasmodel_CodeBuilder_emitInst(x_1159, x_1160);
x_1162 = lp_dasmodel_CodeBuilder_label(x_1161, x_1126);
x_1163 = lp_dasmodel_I_rts;
x_1164 = lp_dasmodel_CodeBuilder_emitInst(x_1162, x_1163);
x_1165 = lp_dasmodel_emitNoteLoadPath(x_1164, x_2);
return x_1165;
}
}
}
else
{
lean_object* x_1194; uint16_t x_1195; lean_object* x_1196; lean_object* x_1197; lean_object* x_1198; lean_object* x_1199; lean_object* x_1200; lean_object* x_1201; lean_object* x_1202; lean_object* x_1203; lean_object* x_1204; lean_object* x_1205; lean_object* x_1206; uint8_t x_1207; lean_object* x_1208; lean_object* x_1209; lean_object* x_1210; lean_object* x_1211; lean_object* x_1212; lean_object* x_1213; lean_object* x_1214; lean_object* x_1215; lean_object* x_1216; lean_object* x_1217; lean_object* x_1218; lean_object* x_1219; lean_object* x_1220; lean_object* x_1221; lean_object* x_1222; lean_object* x_1223; lean_object* x_1224; lean_object* x_1225; lean_object* x_1226; lean_object* x_1227; lean_object* x_1228; lean_object* x_1229; lean_object* x_1230; lean_object* x_1231; lean_object* x_1232; lean_object* x_1233; lean_object* x_1234; lean_object* x_1235; lean_object* x_1236; lean_object* x_1237; lean_object* x_1238; lean_object* x_1239; lean_object* x_1240; lean_object* x_1241; lean_object* x_1242; lean_object* x_1243; lean_object* x_1244; lean_object* x_1245; uint16_t x_1246; lean_object* x_1247; lean_object* x_1248; lean_object* x_1249; lean_object* x_1250; lean_object* x_1251; lean_object* x_1252; lean_object* x_1253; lean_object* x_1254; lean_object* x_1255; lean_object* x_1256; lean_object* x_1257; lean_object* x_1258; lean_object* x_1259; lean_object* x_1260; lean_object* x_1261; lean_object* x_1262; lean_object* x_1263; lean_object* x_1264; lean_object* x_1265; lean_object* x_1266; lean_object* x_1267; lean_object* x_1268; lean_object* x_1269; lean_object* x_1270; lean_object* x_1271; lean_object* x_1272; lean_object* x_1273; lean_object* x_1274; lean_object* x_1275; lean_object* x_1276; lean_object* x_1277; lean_object* x_1278; lean_object* x_1279; uint16_t x_1280; lean_object* x_1281; lean_object* x_1282; lean_object* x_1283; lean_object* x_1284; lean_object* x_1285; lean_object* x_1286; lean_object* x_1287; lean_object* x_1288; lean_object* x_1289; lean_object* x_1290; lean_object* x_1291; lean_object* x_1292; lean_object* x_1293; lean_object* x_1294; lean_object* x_1295; lean_object* x_1296; lean_object* x_1297; lean_object* x_1298; lean_object* x_1299; lean_object* x_1300; lean_object* x_1301; lean_object* x_1302; lean_object* x_1303; lean_object* x_1304; lean_object* x_1305; lean_object* x_1306; lean_object* x_1307; lean_object* x_1308; lean_object* x_1309; uint16_t x_1310; lean_object* x_1311; lean_object* x_1312; lean_object* x_1313; lean_object* x_1314; lean_object* x_1315; lean_object* x_1316; lean_object* x_1317; lean_object* x_1318; lean_object* x_1319; lean_object* x_1320; lean_object* x_1321; lean_object* x_1322; lean_object* x_1323; lean_object* x_1324; lean_object* x_1325; lean_object* x_1326; lean_object* x_1327; lean_object* x_1328; lean_object* x_1329; lean_object* x_1330; lean_object* x_1331; lean_object* x_1332; lean_object* x_1333; lean_object* x_1334; lean_object* x_1460; lean_object* x_1461; lean_object* x_1462; lean_object* x_1463; lean_object* x_1464; lean_object* x_1465; lean_object* x_1466; lean_object* x_1467; lean_object* x_1468; lean_object* x_1469; lean_object* x_1470; uint8_t x_1471; 
x_1194 = lean_ctor_get(x_27, 0);
x_1195 = lean_ctor_get_uint16(x_27, sizeof(void*)*4);
x_1196 = lean_ctor_get(x_27, 1);
x_1197 = lean_ctor_get(x_27, 2);
x_1198 = lean_ctor_get(x_27, 3);
lean_inc(x_1198);
lean_inc(x_1197);
lean_inc(x_1196);
lean_inc(x_1194);
lean_dec(x_27);
x_1199 = lean_array_get_size(x_1194);
x_1200 = lean_nat_sub(x_1199, x_13);
x_1201 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__6));
x_1202 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1202, 0, x_1200);
lean_ctor_set(x_1202, 1, x_1201);
x_1203 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1203, 0, x_1202);
lean_ctor_set(x_1203, 1, x_1198);
x_1204 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_1204, 0, x_1194);
lean_ctor_set(x_1204, 1, x_1196);
lean_ctor_set(x_1204, 2, x_1197);
lean_ctor_set(x_1204, 3, x_1203);
lean_ctor_set_uint16(x_1204, sizeof(void*)*4, x_1195);
x_1205 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__7, &lp_dasmodel_emitSustainEffects___closed__7_once, _init_lp_dasmodel_emitSustainEffects___closed__7);
x_1206 = lp_dasmodel_CodeBuilder_emitInst(x_1204, x_1205);
x_1207 = 26;
x_1208 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__8));
x_1209 = lp_dasmodel_CodeBuilder_emitBranch(x_1206, x_1207, x_1208);
x_1210 = lp_dasmodel_I_clc;
x_1211 = lp_dasmodel_CodeBuilder_emitInst(x_1209, x_1210);
x_1212 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__38));
x_1213 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1211, x_1212);
x_1214 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__9, &lp_dasmodel_emitSustainEffects___closed__9_once, _init_lp_dasmodel_emitSustainEffects___closed__9);
x_1215 = lp_dasmodel_CodeBuilder_emitInst(x_1213, x_1214);
x_1216 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1215, x_1212);
x_1217 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_1218 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1216, x_1217);
x_1219 = lp_dasmodel_CodeBuilder_emitInst(x_1218, x_5);
x_1220 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1219, x_1212);
x_1221 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__34, &lp_dasmodel_emitNoteLoadPath___closed__34_once, _init_lp_dasmodel_emitNoteLoadPath___closed__34);
x_1222 = lp_dasmodel_CodeBuilder_emitInst(x_1220, x_1221);
x_1223 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1222, x_21, x_22);
x_1224 = lp_dasmodel_CodeBuilder_label(x_1223, x_1208);
x_1225 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__39));
x_1226 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1224, x_1225);
x_1227 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__10));
x_1228 = lp_dasmodel_CodeBuilder_emitBranch(x_1226, x_18, x_1227);
x_1229 = lp_dasmodel_CodeBuilder_emitInst(x_1228, x_1210);
x_1230 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1229, x_1212);
x_1231 = lp_dasmodel_CodeBuilder_emitInst(x_1230, x_1214);
x_1232 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1231, x_1212);
x_1233 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__37));
x_1234 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1232, x_1233);
x_1235 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__17, &lp_dasmodel_emitNoteLoadPath___closed__17_once, _init_lp_dasmodel_emitNoteLoadPath___closed__17);
x_1236 = lp_dasmodel_CodeBuilder_emitInst(x_1234, x_1235);
x_1237 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__11, &lp_dasmodel_emitSustainEffects___closed__11_once, _init_lp_dasmodel_emitSustainEffects___closed__11);
x_1238 = lp_dasmodel_CodeBuilder_emitInst(x_1236, x_1237);
x_1239 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1238, x_1233);
x_1240 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1239, x_3);
x_1241 = lp_dasmodel_CodeBuilder_emitInst(x_1240, x_5);
x_1242 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1241, x_1233);
x_1243 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__12));
x_1244 = lp_dasmodel_CodeBuilder_emitInst(x_1242, x_1243);
x_1245 = lean_ctor_get(x_1244, 0);
lean_inc_ref(x_1245);
x_1246 = lean_ctor_get_uint16(x_1244, sizeof(void*)*4);
x_1247 = lean_ctor_get(x_1244, 1);
lean_inc(x_1247);
x_1248 = lean_ctor_get(x_1244, 2);
lean_inc(x_1248);
x_1249 = lean_ctor_get(x_1244, 3);
lean_inc(x_1249);
if (lean_is_exclusive(x_1244)) {
 lean_ctor_release(x_1244, 0);
 lean_ctor_release(x_1244, 1);
 lean_ctor_release(x_1244, 2);
 lean_ctor_release(x_1244, 3);
 x_1250 = x_1244;
} else {
 lean_dec_ref(x_1244);
 x_1250 = lean_box(0);
}
x_1251 = lean_array_get_size(x_1245);
x_1252 = lean_nat_sub(x_1251, x_13);
x_1253 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__13));
x_1254 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1254, 0, x_1252);
lean_ctor_set(x_1254, 1, x_1253);
x_1255 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1255, 0, x_1254);
lean_ctor_set(x_1255, 1, x_1249);
if (lean_is_scalar(x_1250)) {
 x_1256 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1256 = x_1250;
}
lean_ctor_set(x_1256, 0, x_1245);
lean_ctor_set(x_1256, 1, x_1247);
lean_ctor_set(x_1256, 2, x_1248);
lean_ctor_set(x_1256, 3, x_1255);
lean_ctor_set_uint16(x_1256, sizeof(void*)*4, x_1246);
x_1257 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__14));
x_1258 = lp_dasmodel_CodeBuilder_emitBranch(x_1256, x_18, x_1257);
x_1259 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__15, &lp_dasmodel_emitSustainEffects___closed__15_once, _init_lp_dasmodel_emitSustainEffects___closed__15);
x_1260 = lp_dasmodel_CodeBuilder_emitInst(x_1258, x_1259);
x_1261 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1260, x_1225);
x_1262 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1261, x_21, x_1257);
x_1263 = lp_dasmodel_CodeBuilder_label(x_1262, x_1227);
x_1264 = lp_dasmodel_I_sec;
x_1265 = lp_dasmodel_CodeBuilder_emitInst(x_1263, x_1264);
x_1266 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1265, x_1212);
x_1267 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__16, &lp_dasmodel_emitSustainEffects___closed__16_once, _init_lp_dasmodel_emitSustainEffects___closed__16);
x_1268 = lp_dasmodel_CodeBuilder_emitInst(x_1266, x_1267);
x_1269 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1268, x_1212);
x_1270 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1269, x_1233);
x_1271 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__17, &lp_dasmodel_emitSustainEffects___closed__17_once, _init_lp_dasmodel_emitSustainEffects___closed__17);
x_1272 = lp_dasmodel_CodeBuilder_emitInst(x_1270, x_1271);
x_1273 = lp_dasmodel_CodeBuilder_emitInst(x_1272, x_1237);
x_1274 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1273, x_1233);
x_1275 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1274, x_3);
x_1276 = lp_dasmodel_CodeBuilder_emitInst(x_1275, x_5);
x_1277 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1276, x_1233);
x_1278 = lp_dasmodel_CodeBuilder_emitInst(x_1277, x_1243);
x_1279 = lean_ctor_get(x_1278, 0);
lean_inc_ref(x_1279);
x_1280 = lean_ctor_get_uint16(x_1278, sizeof(void*)*4);
x_1281 = lean_ctor_get(x_1278, 1);
lean_inc(x_1281);
x_1282 = lean_ctor_get(x_1278, 2);
lean_inc(x_1282);
x_1283 = lean_ctor_get(x_1278, 3);
lean_inc(x_1283);
if (lean_is_exclusive(x_1278)) {
 lean_ctor_release(x_1278, 0);
 lean_ctor_release(x_1278, 1);
 lean_ctor_release(x_1278, 2);
 lean_ctor_release(x_1278, 3);
 x_1284 = x_1278;
} else {
 lean_dec_ref(x_1278);
 x_1284 = lean_box(0);
}
x_1285 = lean_array_get_size(x_1279);
x_1286 = lean_nat_sub(x_1285, x_13);
x_1287 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__18));
x_1288 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1288, 0, x_1286);
lean_ctor_set(x_1288, 1, x_1287);
x_1289 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1289, 0, x_1288);
lean_ctor_set(x_1289, 1, x_1283);
if (lean_is_scalar(x_1284)) {
 x_1290 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1290 = x_1284;
}
lean_ctor_set(x_1290, 0, x_1279);
lean_ctor_set(x_1290, 1, x_1281);
lean_ctor_set(x_1290, 2, x_1282);
lean_ctor_set(x_1290, 3, x_1289);
lean_ctor_set_uint16(x_1290, sizeof(void*)*4, x_1280);
x_1291 = lp_dasmodel_CodeBuilder_emitBranch(x_1290, x_18, x_1257);
x_1292 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_1293 = lp_dasmodel_CodeBuilder_emitInst(x_1291, x_1292);
x_1294 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1293, x_1225);
x_1295 = lp_dasmodel_CodeBuilder_label(x_1294, x_1257);
x_1296 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1295, x_1217);
x_1297 = lp_dasmodel_CodeBuilder_emitInst(x_1296, x_5);
x_1298 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1297, x_1212);
x_1299 = lp_dasmodel_CodeBuilder_emitInst(x_1298, x_1221);
x_1300 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1299, x_1233);
x_1301 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__36, &lp_dasmodel_emitNoteLoadPath___closed__36_once, _init_lp_dasmodel_emitNoteLoadPath___closed__36);
x_1302 = lp_dasmodel_CodeBuilder_emitInst(x_1300, x_1301);
x_1303 = lp_dasmodel_CodeBuilder_label(x_1302, x_22);
x_1304 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_1305 = lp_dasmodel_CodeBuilder_emitInst(x_1303, x_1304);
x_1306 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1305, x_3);
x_1307 = lp_dasmodel_CodeBuilder_emitInst(x_1306, x_5);
x_1308 = lp_dasmodel_CodeBuilder_emitInst(x_1307, x_7);
x_1309 = lean_ctor_get(x_1308, 0);
lean_inc_ref(x_1309);
x_1310 = lean_ctor_get_uint16(x_1308, sizeof(void*)*4);
x_1311 = lean_ctor_get(x_1308, 1);
lean_inc(x_1311);
x_1312 = lean_ctor_get(x_1308, 2);
lean_inc(x_1312);
x_1313 = lean_ctor_get(x_1308, 3);
lean_inc(x_1313);
if (lean_is_exclusive(x_1308)) {
 lean_ctor_release(x_1308, 0);
 lean_ctor_release(x_1308, 1);
 lean_ctor_release(x_1308, 2);
 lean_ctor_release(x_1308, 3);
 x_1314 = x_1308;
} else {
 lean_dec_ref(x_1308);
 x_1314 = lean_box(0);
}
x_1315 = lean_array_get_size(x_1309);
x_1316 = lean_nat_sub(x_1315, x_13);
x_1317 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_1318 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1318, 0, x_1316);
lean_ctor_set(x_1318, 1, x_1317);
x_1319 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1319, 0, x_1318);
lean_ctor_set(x_1319, 1, x_1313);
if (lean_is_scalar(x_1314)) {
 x_1320 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1320 = x_1314;
}
lean_ctor_set(x_1320, 0, x_1309);
lean_ctor_set(x_1320, 1, x_1311);
lean_ctor_set(x_1320, 2, x_1312);
lean_ctor_set(x_1320, 3, x_1319);
lean_ctor_set_uint16(x_1320, sizeof(void*)*4, x_1310);
x_1321 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__20));
x_1322 = lp_dasmodel_CodeBuilder_emitBranch(x_1320, x_18, x_1321);
x_1323 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__21));
x_1324 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1322, x_21, x_1323);
x_1325 = lp_dasmodel_CodeBuilder_label(x_1324, x_1321);
x_1326 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_1327 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1325, x_1326);
x_1328 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__22));
x_1329 = lp_dasmodel_CodeBuilder_emitBranch(x_1327, x_18, x_1328);
x_1330 = lean_ctor_get(x_2, 4);
x_1331 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1329, x_21, x_1323);
x_1332 = lp_dasmodel_CodeBuilder_label(x_1331, x_1328);
x_1333 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_1460 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1332, x_1333);
x_1461 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__40));
x_1462 = lp_dasmodel_CodeBuilder_emitBranch(x_1460, x_18, x_1461);
x_1463 = lean_unsigned_to_nat(3u);
x_1464 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1462, x_21, x_1323);
x_1465 = lp_dasmodel_CodeBuilder_label(x_1464, x_1461);
x_1466 = lp_dasmodel_CodeBuilder_emitInst(x_1465, x_1264);
x_1467 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_1468 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1466, x_1467);
x_1469 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__41, &lp_dasmodel_emitSustainEffects___closed__41_once, _init_lp_dasmodel_emitSustainEffects___closed__41);
x_1470 = lp_dasmodel_CodeBuilder_emitInst(x_1468, x_1469);
x_1471 = lean_nat_dec_eq(x_1330, x_1463);
if (x_1471 == 0)
{
uint8_t x_1472; 
x_1472 = lean_nat_dec_eq(x_1330, x_13);
if (x_1472 == 0)
{
lean_object* x_1473; uint8_t x_1474; 
x_1473 = lean_unsigned_to_nat(4u);
x_1474 = lean_nat_dec_eq(x_1330, x_1473);
if (x_1474 == 0)
{
x_1334 = x_1470;
goto block_1459;
}
else
{
lean_object* x_1475; lean_object* x_1476; lean_object* x_1477; 
x_1475 = lp_dasmodel_I_asl__a;
x_1476 = lp_dasmodel_CodeBuilder_emitInst(x_1470, x_1475);
x_1477 = lp_dasmodel_CodeBuilder_emitInst(x_1476, x_1475);
x_1334 = x_1477;
goto block_1459;
}
}
else
{
lean_object* x_1478; lean_object* x_1479; 
x_1478 = lp_dasmodel_I_asl__a;
x_1479 = lp_dasmodel_CodeBuilder_emitInst(x_1470, x_1478);
x_1334 = x_1479;
goto block_1459;
}
}
else
{
lean_object* x_1480; lean_object* x_1481; lean_object* x_1482; lean_object* x_1483; lean_object* x_1484; lean_object* x_1485; lean_object* x_1486; 
x_1480 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__42, &lp_dasmodel_emitSustainEffects___closed__42_once, _init_lp_dasmodel_emitSustainEffects___closed__42);
x_1481 = lp_dasmodel_CodeBuilder_emitInst(x_1470, x_1480);
x_1482 = lp_dasmodel_I_asl__a;
x_1483 = lp_dasmodel_CodeBuilder_emitInst(x_1481, x_1482);
x_1484 = lp_dasmodel_CodeBuilder_emitInst(x_1483, x_1210);
x_1485 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__43, &lp_dasmodel_emitSustainEffects___closed__43_once, _init_lp_dasmodel_emitSustainEffects___closed__43);
x_1486 = lp_dasmodel_CodeBuilder_emitInst(x_1484, x_1485);
x_1334 = x_1486;
goto block_1459;
}
block_1459:
{
lean_object* x_1335; lean_object* x_1336; lean_object* x_1337; uint16_t x_1338; lean_object* x_1339; lean_object* x_1340; lean_object* x_1341; lean_object* x_1342; lean_object* x_1343; lean_object* x_1344; lean_object* x_1345; lean_object* x_1346; lean_object* x_1347; lean_object* x_1348; lean_object* x_1349; uint8_t x_1350; lean_object* x_1351; lean_object* x_1352; lean_object* x_1353; lean_object* x_1354; lean_object* x_1355; lean_object* x_1356; lean_object* x_1357; uint16_t x_1358; lean_object* x_1359; lean_object* x_1360; lean_object* x_1361; lean_object* x_1362; lean_object* x_1363; lean_object* x_1364; lean_object* x_1365; lean_object* x_1366; lean_object* x_1367; lean_object* x_1368; lean_object* x_1369; lean_object* x_1370; lean_object* x_1371; lean_object* x_1372; lean_object* x_1373; lean_object* x_1374; lean_object* x_1375; lean_object* x_1376; lean_object* x_1377; lean_object* x_1378; lean_object* x_1379; lean_object* x_1380; lean_object* x_1381; lean_object* x_1382; lean_object* x_1383; lean_object* x_1384; lean_object* x_1385; lean_object* x_1386; lean_object* x_1387; lean_object* x_1388; lean_object* x_1389; lean_object* x_1390; lean_object* x_1391; lean_object* x_1392; lean_object* x_1393; lean_object* x_1394; lean_object* x_1395; lean_object* x_1396; lean_object* x_1397; lean_object* x_1398; lean_object* x_1399; lean_object* x_1400; lean_object* x_1401; lean_object* x_1402; lean_object* x_1403; lean_object* x_1404; lean_object* x_1405; uint16_t x_1406; lean_object* x_1407; lean_object* x_1408; lean_object* x_1409; lean_object* x_1410; lean_object* x_1411; lean_object* x_1412; lean_object* x_1413; lean_object* x_1414; lean_object* x_1415; lean_object* x_1416; lean_object* x_1417; lean_object* x_1418; lean_object* x_1419; lean_object* x_1420; lean_object* x_1421; lean_object* x_1422; lean_object* x_1423; lean_object* x_1424; lean_object* x_1425; lean_object* x_1426; lean_object* x_1427; lean_object* x_1428; lean_object* x_1429; lean_object* x_1430; lean_object* x_1431; lean_object* x_1432; lean_object* x_1433; lean_object* x_1434; lean_object* x_1435; lean_object* x_1436; lean_object* x_1437; lean_object* x_1438; lean_object* x_1439; lean_object* x_1440; lean_object* x_1441; lean_object* x_1442; lean_object* x_1443; lean_object* x_1444; lean_object* x_1445; lean_object* x_1446; lean_object* x_1447; lean_object* x_1448; lean_object* x_1449; lean_object* x_1450; lean_object* x_1451; lean_object* x_1452; lean_object* x_1453; lean_object* x_1454; lean_object* x_1455; lean_object* x_1456; lean_object* x_1457; lean_object* x_1458; 
x_1335 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__24));
x_1336 = lp_dasmodel_CodeBuilder_emitInst(x_1334, x_1335);
x_1337 = lean_ctor_get(x_1336, 0);
lean_inc_ref(x_1337);
x_1338 = lean_ctor_get_uint16(x_1336, sizeof(void*)*4);
x_1339 = lean_ctor_get(x_1336, 1);
lean_inc(x_1339);
x_1340 = lean_ctor_get(x_1336, 2);
lean_inc(x_1340);
x_1341 = lean_ctor_get(x_1336, 3);
lean_inc(x_1341);
if (lean_is_exclusive(x_1336)) {
 lean_ctor_release(x_1336, 0);
 lean_ctor_release(x_1336, 1);
 lean_ctor_release(x_1336, 2);
 lean_ctor_release(x_1336, 3);
 x_1342 = x_1336;
} else {
 lean_dec_ref(x_1336);
 x_1342 = lean_box(0);
}
x_1343 = lean_array_get_size(x_1337);
x_1344 = lean_nat_sub(x_1343, x_13);
x_1345 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1345, 0, x_1344);
lean_ctor_set(x_1345, 1, x_1333);
x_1346 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1346, 0, x_1345);
lean_ctor_set(x_1346, 1, x_1341);
if (lean_is_scalar(x_1342)) {
 x_1347 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1347 = x_1342;
}
lean_ctor_set(x_1347, 0, x_1337);
lean_ctor_set(x_1347, 1, x_1339);
lean_ctor_set(x_1347, 2, x_1340);
lean_ctor_set(x_1347, 3, x_1346);
lean_ctor_set_uint16(x_1347, sizeof(void*)*4, x_1338);
x_1348 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1347, x_1217);
x_1349 = lp_dasmodel_CodeBuilder_emitInst(x_1348, x_5);
x_1350 = 24;
x_1351 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__25));
x_1352 = lp_dasmodel_CodeBuilder_emitBranch(x_1349, x_1350, x_1351);
x_1353 = lp_dasmodel_CodeBuilder_emitInst(x_1352, x_1304);
x_1354 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1353, x_3);
x_1355 = lp_dasmodel_CodeBuilder_emitInst(x_1354, x_5);
x_1356 = lp_dasmodel_CodeBuilder_emitInst(x_1355, x_7);
x_1357 = lean_ctor_get(x_1356, 0);
lean_inc_ref(x_1357);
x_1358 = lean_ctor_get_uint16(x_1356, sizeof(void*)*4);
x_1359 = lean_ctor_get(x_1356, 1);
lean_inc(x_1359);
x_1360 = lean_ctor_get(x_1356, 2);
lean_inc(x_1360);
x_1361 = lean_ctor_get(x_1356, 3);
lean_inc(x_1361);
if (lean_is_exclusive(x_1356)) {
 lean_ctor_release(x_1356, 0);
 lean_ctor_release(x_1356, 1);
 lean_ctor_release(x_1356, 2);
 lean_ctor_release(x_1356, 3);
 x_1362 = x_1356;
} else {
 lean_dec_ref(x_1356);
 x_1362 = lean_box(0);
}
x_1363 = lean_array_get_size(x_1357);
x_1364 = lean_nat_sub(x_1363, x_13);
x_1365 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_1366 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1366, 0, x_1364);
lean_ctor_set(x_1366, 1, x_1365);
x_1367 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1367, 0, x_1366);
lean_ctor_set(x_1367, 1, x_1361);
if (lean_is_scalar(x_1362)) {
 x_1368 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1368 = x_1362;
}
lean_ctor_set(x_1368, 0, x_1357);
lean_ctor_set(x_1368, 1, x_1359);
lean_ctor_set(x_1368, 2, x_1360);
lean_ctor_set(x_1368, 3, x_1367);
lean_ctor_set_uint16(x_1368, sizeof(void*)*4, x_1358);
x_1369 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_1370 = lp_dasmodel_CodeBuilder_emitInst(x_1368, x_1369);
x_1371 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1370, x_1326);
x_1372 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_1373 = lp_dasmodel_CodeBuilder_emitInst(x_1371, x_1372);
x_1374 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_1373, x_1326);
x_1375 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1374, x_1217);
x_1376 = lp_dasmodel_CodeBuilder_emitInst(x_1375, x_5);
x_1377 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_1378 = lp_dasmodel_CodeBuilder_emitInst(x_1376, x_1377);
x_1379 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_1380 = lp_dasmodel_CodeBuilder_emitInst(x_1378, x_1379);
x_1381 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_1382 = lp_dasmodel_CodeBuilder_emitInst(x_1380, x_1381);
x_1383 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_1384 = lp_dasmodel_CodeBuilder_emitInst(x_1382, x_1383);
x_1385 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_1386 = lp_dasmodel_CodeBuilder_emitInst(x_1384, x_1385);
x_1387 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_1388 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1386, x_21, x_1387);
x_1389 = lp_dasmodel_CodeBuilder_label(x_1388, x_1351);
x_1390 = lp_dasmodel_CodeBuilder_emitInst(x_1389, x_1304);
x_1391 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1390, x_1326);
x_1392 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1391, x_1217);
x_1393 = lp_dasmodel_CodeBuilder_emitInst(x_1392, x_5);
x_1394 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1393, x_1326);
x_1395 = lp_dasmodel_CodeBuilder_emitInst(x_1394, x_1379);
x_1396 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_1397 = lp_dasmodel_CodeBuilder_emitInst(x_1395, x_1396);
x_1398 = lp_dasmodel_CodeBuilder_emitInst(x_1397, x_1385);
x_1399 = lp_dasmodel_CodeBuilder_label(x_1398, x_1387);
x_1400 = lp_dasmodel_CodeBuilder_label(x_1399, x_1323);
x_1401 = lp_dasmodel_CodeBuilder_emitInst(x_1400, x_1304);
x_1402 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1401, x_3);
x_1403 = lp_dasmodel_CodeBuilder_emitInst(x_1402, x_5);
x_1404 = lp_dasmodel_CodeBuilder_emitInst(x_1403, x_7);
x_1405 = lean_ctor_get(x_1404, 0);
lean_inc_ref(x_1405);
x_1406 = lean_ctor_get_uint16(x_1404, sizeof(void*)*4);
x_1407 = lean_ctor_get(x_1404, 1);
lean_inc(x_1407);
x_1408 = lean_ctor_get(x_1404, 2);
lean_inc(x_1408);
x_1409 = lean_ctor_get(x_1404, 3);
lean_inc(x_1409);
if (lean_is_exclusive(x_1404)) {
 lean_ctor_release(x_1404, 0);
 lean_ctor_release(x_1404, 1);
 lean_ctor_release(x_1404, 2);
 lean_ctor_release(x_1404, 3);
 x_1410 = x_1404;
} else {
 lean_dec_ref(x_1404);
 x_1410 = lean_box(0);
}
x_1411 = lean_array_get_size(x_1405);
x_1412 = lean_nat_sub(x_1411, x_13);
x_1413 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_1414 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1414, 0, x_1412);
lean_ctor_set(x_1414, 1, x_1413);
x_1415 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1415, 0, x_1414);
lean_ctor_set(x_1415, 1, x_1409);
if (lean_is_scalar(x_1410)) {
 x_1416 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1416 = x_1410;
}
lean_ctor_set(x_1416, 0, x_1405);
lean_ctor_set(x_1416, 1, x_1407);
lean_ctor_set(x_1416, 2, x_1408);
lean_ctor_set(x_1416, 3, x_1415);
lean_ctor_set_uint16(x_1416, sizeof(void*)*4, x_1406);
x_1417 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_1418 = lp_dasmodel_CodeBuilder_emitBranch(x_1416, x_18, x_1417);
x_1419 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_1420 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1418, x_21, x_1419);
x_1421 = lp_dasmodel_CodeBuilder_label(x_1420, x_1417);
x_1422 = lp_dasmodel_CodeBuilder_emitInst(x_1421, x_1372);
x_1423 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_1424 = lp_dasmodel_CodeBuilder_emitInst(x_1422, x_1423);
x_1425 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_1426 = lp_dasmodel_CodeBuilder_emitInst(x_1424, x_1425);
x_1427 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_1428 = lp_dasmodel_CodeBuilder_emitBranch(x_1426, x_1207, x_1427);
x_1429 = lp_dasmodel_CodeBuilder_emitInst(x_1428, x_1210);
x_1430 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_1431 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1429, x_1430);
x_1432 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_1433 = lp_dasmodel_CodeBuilder_emitInst(x_1431, x_1432);
x_1434 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_1435 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1433, x_21, x_1434);
x_1436 = lp_dasmodel_CodeBuilder_label(x_1435, x_1427);
x_1437 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1436, x_1430);
x_1438 = lp_dasmodel_CodeBuilder_label(x_1437, x_1434);
x_1439 = lp_dasmodel_CodeBuilder_emitInst(x_1438, x_5);
x_1440 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_1441 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_1439, x_1440);
x_1442 = lp_dasmodel_CodeBuilder_emitInst(x_1441, x_25);
x_1443 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_1444 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_1442, x_1443);
x_1445 = lp_dasmodel_CodeBuilder_emitInst(x_1444, x_1372);
x_1446 = lp_dasmodel_CodeBuilder_emitInst(x_1445, x_1304);
x_1447 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1446, x_1217);
x_1448 = lp_dasmodel_CodeBuilder_emitInst(x_1447, x_5);
x_1449 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_1450 = lp_dasmodel_CodeBuilder_emitInst(x_1448, x_1449);
x_1451 = lp_dasmodel_CodeBuilder_emitInst(x_1450, x_1379);
x_1452 = lp_dasmodel_CodeBuilder_emitInst(x_1451, x_1377);
x_1453 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_1454 = lp_dasmodel_CodeBuilder_emitInst(x_1452, x_1453);
x_1455 = lp_dasmodel_CodeBuilder_label(x_1454, x_1419);
x_1456 = lp_dasmodel_I_rts;
x_1457 = lp_dasmodel_CodeBuilder_emitInst(x_1455, x_1456);
x_1458 = lp_dasmodel_emitNoteLoadPath(x_1457, x_2);
return x_1458;
}
}
}
else
{
lean_object* x_1487; uint16_t x_1488; lean_object* x_1489; lean_object* x_1490; lean_object* x_1491; lean_object* x_1492; lean_object* x_1493; lean_object* x_1494; lean_object* x_1495; lean_object* x_1496; lean_object* x_1497; lean_object* x_1498; uint8_t x_1499; lean_object* x_1500; lean_object* x_1501; uint8_t x_1502; lean_object* x_1503; lean_object* x_1504; lean_object* x_1505; lean_object* x_1506; lean_object* x_1507; lean_object* x_1508; lean_object* x_1509; uint16_t x_1510; lean_object* x_1511; lean_object* x_1512; lean_object* x_1513; lean_object* x_1514; lean_object* x_1515; lean_object* x_1516; lean_object* x_1517; lean_object* x_1518; lean_object* x_1519; lean_object* x_1520; lean_object* x_1521; lean_object* x_1522; uint8_t x_1523; lean_object* x_1524; lean_object* x_1525; lean_object* x_1526; lean_object* x_1527; lean_object* x_1528; lean_object* x_1529; lean_object* x_1530; lean_object* x_1531; lean_object* x_1532; lean_object* x_1533; lean_object* x_1534; lean_object* x_1535; lean_object* x_1536; lean_object* x_1537; lean_object* x_1538; lean_object* x_1539; lean_object* x_1540; lean_object* x_1541; lean_object* x_1542; lean_object* x_1543; lean_object* x_1544; lean_object* x_1545; lean_object* x_1546; lean_object* x_1547; lean_object* x_1548; lean_object* x_1549; lean_object* x_1550; lean_object* x_1551; lean_object* x_1552; lean_object* x_1553; lean_object* x_1554; lean_object* x_1555; lean_object* x_1556; lean_object* x_1557; lean_object* x_1558; lean_object* x_1559; lean_object* x_1560; lean_object* x_1561; uint16_t x_1562; lean_object* x_1563; lean_object* x_1564; lean_object* x_1565; lean_object* x_1566; lean_object* x_1567; lean_object* x_1568; lean_object* x_1569; lean_object* x_1570; lean_object* x_1571; lean_object* x_1572; lean_object* x_1573; lean_object* x_1574; lean_object* x_1575; lean_object* x_1576; lean_object* x_1577; lean_object* x_1578; lean_object* x_1579; lean_object* x_1580; lean_object* x_1581; lean_object* x_1582; lean_object* x_1583; lean_object* x_1584; lean_object* x_1585; lean_object* x_1586; lean_object* x_1587; lean_object* x_1588; lean_object* x_1589; lean_object* x_1590; lean_object* x_1591; lean_object* x_1592; lean_object* x_1593; lean_object* x_1594; lean_object* x_1595; uint16_t x_1596; lean_object* x_1597; lean_object* x_1598; lean_object* x_1599; lean_object* x_1600; lean_object* x_1601; lean_object* x_1602; lean_object* x_1603; lean_object* x_1604; lean_object* x_1605; lean_object* x_1606; lean_object* x_1607; lean_object* x_1608; lean_object* x_1609; lean_object* x_1610; lean_object* x_1611; lean_object* x_1612; lean_object* x_1613; lean_object* x_1614; lean_object* x_1615; lean_object* x_1616; lean_object* x_1617; lean_object* x_1618; lean_object* x_1619; lean_object* x_1620; lean_object* x_1621; lean_object* x_1622; lean_object* x_1623; lean_object* x_1624; lean_object* x_1625; uint16_t x_1626; lean_object* x_1627; lean_object* x_1628; lean_object* x_1629; lean_object* x_1630; lean_object* x_1631; lean_object* x_1632; lean_object* x_1633; lean_object* x_1634; lean_object* x_1635; lean_object* x_1636; lean_object* x_1637; lean_object* x_1638; lean_object* x_1639; lean_object* x_1640; lean_object* x_1641; lean_object* x_1642; lean_object* x_1643; lean_object* x_1644; lean_object* x_1645; lean_object* x_1646; lean_object* x_1647; lean_object* x_1648; lean_object* x_1649; lean_object* x_1650; lean_object* x_1776; lean_object* x_1777; lean_object* x_1778; lean_object* x_1779; lean_object* x_1780; lean_object* x_1781; lean_object* x_1782; lean_object* x_1783; lean_object* x_1784; lean_object* x_1785; lean_object* x_1786; uint8_t x_1787; 
x_1487 = lean_ctor_get(x_8, 0);
x_1488 = lean_ctor_get_uint16(x_8, sizeof(void*)*4);
x_1489 = lean_ctor_get(x_8, 1);
x_1490 = lean_ctor_get(x_8, 2);
x_1491 = lean_ctor_get(x_8, 3);
lean_inc(x_1491);
lean_inc(x_1490);
lean_inc(x_1489);
lean_inc(x_1487);
lean_dec(x_8);
x_1492 = lean_array_get_size(x_1487);
x_1493 = lean_unsigned_to_nat(2u);
x_1494 = lean_nat_sub(x_1492, x_1493);
x_1495 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__2));
x_1496 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1496, 0, x_1494);
lean_ctor_set(x_1496, 1, x_1495);
x_1497 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1497, 0, x_1496);
lean_ctor_set(x_1497, 1, x_1491);
x_1498 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_1498, 0, x_1487);
lean_ctor_set(x_1498, 1, x_1489);
lean_ctor_set(x_1498, 2, x_1490);
lean_ctor_set(x_1498, 3, x_1497);
lean_ctor_set_uint16(x_1498, sizeof(void*)*4, x_1488);
x_1499 = 27;
x_1500 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__3));
x_1501 = lp_dasmodel_CodeBuilder_emitBranch(x_1498, x_1499, x_1500);
x_1502 = 32;
x_1503 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__4));
x_1504 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1501, x_1502, x_1503);
x_1505 = lp_dasmodel_CodeBuilder_label(x_1504, x_1500);
x_1506 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__5, &lp_dasmodel_emitSustainEffects___closed__5_once, _init_lp_dasmodel_emitSustainEffects___closed__5);
x_1507 = lp_dasmodel_CodeBuilder_emitInst(x_1505, x_1506);
x_1508 = lp_dasmodel_CodeBuilder_emitInst(x_1507, x_7);
x_1509 = lean_ctor_get(x_1508, 0);
lean_inc_ref(x_1509);
x_1510 = lean_ctor_get_uint16(x_1508, sizeof(void*)*4);
x_1511 = lean_ctor_get(x_1508, 1);
lean_inc(x_1511);
x_1512 = lean_ctor_get(x_1508, 2);
lean_inc(x_1512);
x_1513 = lean_ctor_get(x_1508, 3);
lean_inc(x_1513);
if (lean_is_exclusive(x_1508)) {
 lean_ctor_release(x_1508, 0);
 lean_ctor_release(x_1508, 1);
 lean_ctor_release(x_1508, 2);
 lean_ctor_release(x_1508, 3);
 x_1514 = x_1508;
} else {
 lean_dec_ref(x_1508);
 x_1514 = lean_box(0);
}
x_1515 = lean_array_get_size(x_1509);
x_1516 = lean_nat_sub(x_1515, x_1493);
x_1517 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__6));
x_1518 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1518, 0, x_1516);
lean_ctor_set(x_1518, 1, x_1517);
x_1519 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1519, 0, x_1518);
lean_ctor_set(x_1519, 1, x_1513);
if (lean_is_scalar(x_1514)) {
 x_1520 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1520 = x_1514;
}
lean_ctor_set(x_1520, 0, x_1509);
lean_ctor_set(x_1520, 1, x_1511);
lean_ctor_set(x_1520, 2, x_1512);
lean_ctor_set(x_1520, 3, x_1519);
lean_ctor_set_uint16(x_1520, sizeof(void*)*4, x_1510);
x_1521 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__7, &lp_dasmodel_emitSustainEffects___closed__7_once, _init_lp_dasmodel_emitSustainEffects___closed__7);
x_1522 = lp_dasmodel_CodeBuilder_emitInst(x_1520, x_1521);
x_1523 = 26;
x_1524 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__8));
x_1525 = lp_dasmodel_CodeBuilder_emitBranch(x_1522, x_1523, x_1524);
x_1526 = lp_dasmodel_I_clc;
x_1527 = lp_dasmodel_CodeBuilder_emitInst(x_1525, x_1526);
x_1528 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__38));
x_1529 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1527, x_1528);
x_1530 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__9, &lp_dasmodel_emitSustainEffects___closed__9_once, _init_lp_dasmodel_emitSustainEffects___closed__9);
x_1531 = lp_dasmodel_CodeBuilder_emitInst(x_1529, x_1530);
x_1532 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1531, x_1528);
x_1533 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_1534 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1532, x_1533);
x_1535 = lp_dasmodel_CodeBuilder_emitInst(x_1534, x_5);
x_1536 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1535, x_1528);
x_1537 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__34, &lp_dasmodel_emitNoteLoadPath___closed__34_once, _init_lp_dasmodel_emitNoteLoadPath___closed__34);
x_1538 = lp_dasmodel_CodeBuilder_emitInst(x_1536, x_1537);
x_1539 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1538, x_1502, x_1503);
x_1540 = lp_dasmodel_CodeBuilder_label(x_1539, x_1524);
x_1541 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__39));
x_1542 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1540, x_1541);
x_1543 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__10));
x_1544 = lp_dasmodel_CodeBuilder_emitBranch(x_1542, x_1499, x_1543);
x_1545 = lp_dasmodel_CodeBuilder_emitInst(x_1544, x_1526);
x_1546 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1545, x_1528);
x_1547 = lp_dasmodel_CodeBuilder_emitInst(x_1546, x_1530);
x_1548 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1547, x_1528);
x_1549 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__37));
x_1550 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1548, x_1549);
x_1551 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__17, &lp_dasmodel_emitNoteLoadPath___closed__17_once, _init_lp_dasmodel_emitNoteLoadPath___closed__17);
x_1552 = lp_dasmodel_CodeBuilder_emitInst(x_1550, x_1551);
x_1553 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__11, &lp_dasmodel_emitSustainEffects___closed__11_once, _init_lp_dasmodel_emitSustainEffects___closed__11);
x_1554 = lp_dasmodel_CodeBuilder_emitInst(x_1552, x_1553);
x_1555 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1554, x_1549);
x_1556 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1555, x_3);
x_1557 = lp_dasmodel_CodeBuilder_emitInst(x_1556, x_5);
x_1558 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1557, x_1549);
x_1559 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__12));
x_1560 = lp_dasmodel_CodeBuilder_emitInst(x_1558, x_1559);
x_1561 = lean_ctor_get(x_1560, 0);
lean_inc_ref(x_1561);
x_1562 = lean_ctor_get_uint16(x_1560, sizeof(void*)*4);
x_1563 = lean_ctor_get(x_1560, 1);
lean_inc(x_1563);
x_1564 = lean_ctor_get(x_1560, 2);
lean_inc(x_1564);
x_1565 = lean_ctor_get(x_1560, 3);
lean_inc(x_1565);
if (lean_is_exclusive(x_1560)) {
 lean_ctor_release(x_1560, 0);
 lean_ctor_release(x_1560, 1);
 lean_ctor_release(x_1560, 2);
 lean_ctor_release(x_1560, 3);
 x_1566 = x_1560;
} else {
 lean_dec_ref(x_1560);
 x_1566 = lean_box(0);
}
x_1567 = lean_array_get_size(x_1561);
x_1568 = lean_nat_sub(x_1567, x_1493);
x_1569 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__13));
x_1570 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1570, 0, x_1568);
lean_ctor_set(x_1570, 1, x_1569);
x_1571 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1571, 0, x_1570);
lean_ctor_set(x_1571, 1, x_1565);
if (lean_is_scalar(x_1566)) {
 x_1572 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1572 = x_1566;
}
lean_ctor_set(x_1572, 0, x_1561);
lean_ctor_set(x_1572, 1, x_1563);
lean_ctor_set(x_1572, 2, x_1564);
lean_ctor_set(x_1572, 3, x_1571);
lean_ctor_set_uint16(x_1572, sizeof(void*)*4, x_1562);
x_1573 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__14));
x_1574 = lp_dasmodel_CodeBuilder_emitBranch(x_1572, x_1499, x_1573);
x_1575 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__15, &lp_dasmodel_emitSustainEffects___closed__15_once, _init_lp_dasmodel_emitSustainEffects___closed__15);
x_1576 = lp_dasmodel_CodeBuilder_emitInst(x_1574, x_1575);
x_1577 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1576, x_1541);
x_1578 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1577, x_1502, x_1573);
x_1579 = lp_dasmodel_CodeBuilder_label(x_1578, x_1543);
x_1580 = lp_dasmodel_I_sec;
x_1581 = lp_dasmodel_CodeBuilder_emitInst(x_1579, x_1580);
x_1582 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1581, x_1528);
x_1583 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__16, &lp_dasmodel_emitSustainEffects___closed__16_once, _init_lp_dasmodel_emitSustainEffects___closed__16);
x_1584 = lp_dasmodel_CodeBuilder_emitInst(x_1582, x_1583);
x_1585 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1584, x_1528);
x_1586 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1585, x_1549);
x_1587 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__17, &lp_dasmodel_emitSustainEffects___closed__17_once, _init_lp_dasmodel_emitSustainEffects___closed__17);
x_1588 = lp_dasmodel_CodeBuilder_emitInst(x_1586, x_1587);
x_1589 = lp_dasmodel_CodeBuilder_emitInst(x_1588, x_1553);
x_1590 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1589, x_1549);
x_1591 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1590, x_3);
x_1592 = lp_dasmodel_CodeBuilder_emitInst(x_1591, x_5);
x_1593 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1592, x_1549);
x_1594 = lp_dasmodel_CodeBuilder_emitInst(x_1593, x_1559);
x_1595 = lean_ctor_get(x_1594, 0);
lean_inc_ref(x_1595);
x_1596 = lean_ctor_get_uint16(x_1594, sizeof(void*)*4);
x_1597 = lean_ctor_get(x_1594, 1);
lean_inc(x_1597);
x_1598 = lean_ctor_get(x_1594, 2);
lean_inc(x_1598);
x_1599 = lean_ctor_get(x_1594, 3);
lean_inc(x_1599);
if (lean_is_exclusive(x_1594)) {
 lean_ctor_release(x_1594, 0);
 lean_ctor_release(x_1594, 1);
 lean_ctor_release(x_1594, 2);
 lean_ctor_release(x_1594, 3);
 x_1600 = x_1594;
} else {
 lean_dec_ref(x_1594);
 x_1600 = lean_box(0);
}
x_1601 = lean_array_get_size(x_1595);
x_1602 = lean_nat_sub(x_1601, x_1493);
x_1603 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__18));
x_1604 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1604, 0, x_1602);
lean_ctor_set(x_1604, 1, x_1603);
x_1605 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1605, 0, x_1604);
lean_ctor_set(x_1605, 1, x_1599);
if (lean_is_scalar(x_1600)) {
 x_1606 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1606 = x_1600;
}
lean_ctor_set(x_1606, 0, x_1595);
lean_ctor_set(x_1606, 1, x_1597);
lean_ctor_set(x_1606, 2, x_1598);
lean_ctor_set(x_1606, 3, x_1605);
lean_ctor_set_uint16(x_1606, sizeof(void*)*4, x_1596);
x_1607 = lp_dasmodel_CodeBuilder_emitBranch(x_1606, x_1499, x_1573);
x_1608 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_1609 = lp_dasmodel_CodeBuilder_emitInst(x_1607, x_1608);
x_1610 = lp_dasmodel_CodeBuilder_emitStaAbsX(x_1609, x_1541);
x_1611 = lp_dasmodel_CodeBuilder_label(x_1610, x_1573);
x_1612 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1611, x_1533);
x_1613 = lp_dasmodel_CodeBuilder_emitInst(x_1612, x_5);
x_1614 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1613, x_1528);
x_1615 = lp_dasmodel_CodeBuilder_emitInst(x_1614, x_1537);
x_1616 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1615, x_1549);
x_1617 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__36, &lp_dasmodel_emitNoteLoadPath___closed__36_once, _init_lp_dasmodel_emitNoteLoadPath___closed__36);
x_1618 = lp_dasmodel_CodeBuilder_emitInst(x_1616, x_1617);
x_1619 = lp_dasmodel_CodeBuilder_label(x_1618, x_1503);
x_1620 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_1621 = lp_dasmodel_CodeBuilder_emitInst(x_1619, x_1620);
x_1622 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1621, x_3);
x_1623 = lp_dasmodel_CodeBuilder_emitInst(x_1622, x_5);
x_1624 = lp_dasmodel_CodeBuilder_emitInst(x_1623, x_7);
x_1625 = lean_ctor_get(x_1624, 0);
lean_inc_ref(x_1625);
x_1626 = lean_ctor_get_uint16(x_1624, sizeof(void*)*4);
x_1627 = lean_ctor_get(x_1624, 1);
lean_inc(x_1627);
x_1628 = lean_ctor_get(x_1624, 2);
lean_inc(x_1628);
x_1629 = lean_ctor_get(x_1624, 3);
lean_inc(x_1629);
if (lean_is_exclusive(x_1624)) {
 lean_ctor_release(x_1624, 0);
 lean_ctor_release(x_1624, 1);
 lean_ctor_release(x_1624, 2);
 lean_ctor_release(x_1624, 3);
 x_1630 = x_1624;
} else {
 lean_dec_ref(x_1624);
 x_1630 = lean_box(0);
}
x_1631 = lean_array_get_size(x_1625);
x_1632 = lean_nat_sub(x_1631, x_1493);
x_1633 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_1634 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1634, 0, x_1632);
lean_ctor_set(x_1634, 1, x_1633);
x_1635 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1635, 0, x_1634);
lean_ctor_set(x_1635, 1, x_1629);
if (lean_is_scalar(x_1630)) {
 x_1636 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1636 = x_1630;
}
lean_ctor_set(x_1636, 0, x_1625);
lean_ctor_set(x_1636, 1, x_1627);
lean_ctor_set(x_1636, 2, x_1628);
lean_ctor_set(x_1636, 3, x_1635);
lean_ctor_set_uint16(x_1636, sizeof(void*)*4, x_1626);
x_1637 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__20));
x_1638 = lp_dasmodel_CodeBuilder_emitBranch(x_1636, x_1499, x_1637);
x_1639 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__21));
x_1640 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1638, x_1502, x_1639);
x_1641 = lp_dasmodel_CodeBuilder_label(x_1640, x_1637);
x_1642 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_1643 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1641, x_1642);
x_1644 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__22));
x_1645 = lp_dasmodel_CodeBuilder_emitBranch(x_1643, x_1499, x_1644);
x_1646 = lean_ctor_get(x_2, 4);
x_1647 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1645, x_1502, x_1639);
x_1648 = lp_dasmodel_CodeBuilder_label(x_1647, x_1644);
x_1649 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_1776 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1648, x_1649);
x_1777 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__40));
x_1778 = lp_dasmodel_CodeBuilder_emitBranch(x_1776, x_1499, x_1777);
x_1779 = lean_unsigned_to_nat(3u);
x_1780 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1778, x_1502, x_1639);
x_1781 = lp_dasmodel_CodeBuilder_label(x_1780, x_1777);
x_1782 = lp_dasmodel_CodeBuilder_emitInst(x_1781, x_1580);
x_1783 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_1784 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1782, x_1783);
x_1785 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__41, &lp_dasmodel_emitSustainEffects___closed__41_once, _init_lp_dasmodel_emitSustainEffects___closed__41);
x_1786 = lp_dasmodel_CodeBuilder_emitInst(x_1784, x_1785);
x_1787 = lean_nat_dec_eq(x_1646, x_1779);
if (x_1787 == 0)
{
uint8_t x_1788; 
x_1788 = lean_nat_dec_eq(x_1646, x_1493);
if (x_1788 == 0)
{
lean_object* x_1789; uint8_t x_1790; 
x_1789 = lean_unsigned_to_nat(4u);
x_1790 = lean_nat_dec_eq(x_1646, x_1789);
if (x_1790 == 0)
{
x_1650 = x_1786;
goto block_1775;
}
else
{
lean_object* x_1791; lean_object* x_1792; lean_object* x_1793; 
x_1791 = lp_dasmodel_I_asl__a;
x_1792 = lp_dasmodel_CodeBuilder_emitInst(x_1786, x_1791);
x_1793 = lp_dasmodel_CodeBuilder_emitInst(x_1792, x_1791);
x_1650 = x_1793;
goto block_1775;
}
}
else
{
lean_object* x_1794; lean_object* x_1795; 
x_1794 = lp_dasmodel_I_asl__a;
x_1795 = lp_dasmodel_CodeBuilder_emitInst(x_1786, x_1794);
x_1650 = x_1795;
goto block_1775;
}
}
else
{
lean_object* x_1796; lean_object* x_1797; lean_object* x_1798; lean_object* x_1799; lean_object* x_1800; lean_object* x_1801; lean_object* x_1802; 
x_1796 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__42, &lp_dasmodel_emitSustainEffects___closed__42_once, _init_lp_dasmodel_emitSustainEffects___closed__42);
x_1797 = lp_dasmodel_CodeBuilder_emitInst(x_1786, x_1796);
x_1798 = lp_dasmodel_I_asl__a;
x_1799 = lp_dasmodel_CodeBuilder_emitInst(x_1797, x_1798);
x_1800 = lp_dasmodel_CodeBuilder_emitInst(x_1799, x_1526);
x_1801 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__43, &lp_dasmodel_emitSustainEffects___closed__43_once, _init_lp_dasmodel_emitSustainEffects___closed__43);
x_1802 = lp_dasmodel_CodeBuilder_emitInst(x_1800, x_1801);
x_1650 = x_1802;
goto block_1775;
}
block_1775:
{
lean_object* x_1651; lean_object* x_1652; lean_object* x_1653; uint16_t x_1654; lean_object* x_1655; lean_object* x_1656; lean_object* x_1657; lean_object* x_1658; lean_object* x_1659; lean_object* x_1660; lean_object* x_1661; lean_object* x_1662; lean_object* x_1663; lean_object* x_1664; lean_object* x_1665; uint8_t x_1666; lean_object* x_1667; lean_object* x_1668; lean_object* x_1669; lean_object* x_1670; lean_object* x_1671; lean_object* x_1672; lean_object* x_1673; uint16_t x_1674; lean_object* x_1675; lean_object* x_1676; lean_object* x_1677; lean_object* x_1678; lean_object* x_1679; lean_object* x_1680; lean_object* x_1681; lean_object* x_1682; lean_object* x_1683; lean_object* x_1684; lean_object* x_1685; lean_object* x_1686; lean_object* x_1687; lean_object* x_1688; lean_object* x_1689; lean_object* x_1690; lean_object* x_1691; lean_object* x_1692; lean_object* x_1693; lean_object* x_1694; lean_object* x_1695; lean_object* x_1696; lean_object* x_1697; lean_object* x_1698; lean_object* x_1699; lean_object* x_1700; lean_object* x_1701; lean_object* x_1702; lean_object* x_1703; lean_object* x_1704; lean_object* x_1705; lean_object* x_1706; lean_object* x_1707; lean_object* x_1708; lean_object* x_1709; lean_object* x_1710; lean_object* x_1711; lean_object* x_1712; lean_object* x_1713; lean_object* x_1714; lean_object* x_1715; lean_object* x_1716; lean_object* x_1717; lean_object* x_1718; lean_object* x_1719; lean_object* x_1720; lean_object* x_1721; uint16_t x_1722; lean_object* x_1723; lean_object* x_1724; lean_object* x_1725; lean_object* x_1726; lean_object* x_1727; lean_object* x_1728; lean_object* x_1729; lean_object* x_1730; lean_object* x_1731; lean_object* x_1732; lean_object* x_1733; lean_object* x_1734; lean_object* x_1735; lean_object* x_1736; lean_object* x_1737; lean_object* x_1738; lean_object* x_1739; lean_object* x_1740; lean_object* x_1741; lean_object* x_1742; lean_object* x_1743; lean_object* x_1744; lean_object* x_1745; lean_object* x_1746; lean_object* x_1747; lean_object* x_1748; lean_object* x_1749; lean_object* x_1750; lean_object* x_1751; lean_object* x_1752; lean_object* x_1753; lean_object* x_1754; lean_object* x_1755; lean_object* x_1756; lean_object* x_1757; lean_object* x_1758; lean_object* x_1759; lean_object* x_1760; lean_object* x_1761; lean_object* x_1762; lean_object* x_1763; lean_object* x_1764; lean_object* x_1765; lean_object* x_1766; lean_object* x_1767; lean_object* x_1768; lean_object* x_1769; lean_object* x_1770; lean_object* x_1771; lean_object* x_1772; lean_object* x_1773; lean_object* x_1774; 
x_1651 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__24));
x_1652 = lp_dasmodel_CodeBuilder_emitInst(x_1650, x_1651);
x_1653 = lean_ctor_get(x_1652, 0);
lean_inc_ref(x_1653);
x_1654 = lean_ctor_get_uint16(x_1652, sizeof(void*)*4);
x_1655 = lean_ctor_get(x_1652, 1);
lean_inc(x_1655);
x_1656 = lean_ctor_get(x_1652, 2);
lean_inc(x_1656);
x_1657 = lean_ctor_get(x_1652, 3);
lean_inc(x_1657);
if (lean_is_exclusive(x_1652)) {
 lean_ctor_release(x_1652, 0);
 lean_ctor_release(x_1652, 1);
 lean_ctor_release(x_1652, 2);
 lean_ctor_release(x_1652, 3);
 x_1658 = x_1652;
} else {
 lean_dec_ref(x_1652);
 x_1658 = lean_box(0);
}
x_1659 = lean_array_get_size(x_1653);
x_1660 = lean_nat_sub(x_1659, x_1493);
x_1661 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1661, 0, x_1660);
lean_ctor_set(x_1661, 1, x_1649);
x_1662 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1662, 0, x_1661);
lean_ctor_set(x_1662, 1, x_1657);
if (lean_is_scalar(x_1658)) {
 x_1663 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1663 = x_1658;
}
lean_ctor_set(x_1663, 0, x_1653);
lean_ctor_set(x_1663, 1, x_1655);
lean_ctor_set(x_1663, 2, x_1656);
lean_ctor_set(x_1663, 3, x_1662);
lean_ctor_set_uint16(x_1663, sizeof(void*)*4, x_1654);
x_1664 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1663, x_1533);
x_1665 = lp_dasmodel_CodeBuilder_emitInst(x_1664, x_5);
x_1666 = 24;
x_1667 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__25));
x_1668 = lp_dasmodel_CodeBuilder_emitBranch(x_1665, x_1666, x_1667);
x_1669 = lp_dasmodel_CodeBuilder_emitInst(x_1668, x_1620);
x_1670 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1669, x_3);
x_1671 = lp_dasmodel_CodeBuilder_emitInst(x_1670, x_5);
x_1672 = lp_dasmodel_CodeBuilder_emitInst(x_1671, x_7);
x_1673 = lean_ctor_get(x_1672, 0);
lean_inc_ref(x_1673);
x_1674 = lean_ctor_get_uint16(x_1672, sizeof(void*)*4);
x_1675 = lean_ctor_get(x_1672, 1);
lean_inc(x_1675);
x_1676 = lean_ctor_get(x_1672, 2);
lean_inc(x_1676);
x_1677 = lean_ctor_get(x_1672, 3);
lean_inc(x_1677);
if (lean_is_exclusive(x_1672)) {
 lean_ctor_release(x_1672, 0);
 lean_ctor_release(x_1672, 1);
 lean_ctor_release(x_1672, 2);
 lean_ctor_release(x_1672, 3);
 x_1678 = x_1672;
} else {
 lean_dec_ref(x_1672);
 x_1678 = lean_box(0);
}
x_1679 = lean_array_get_size(x_1673);
x_1680 = lean_nat_sub(x_1679, x_1493);
x_1681 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_1682 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1682, 0, x_1680);
lean_ctor_set(x_1682, 1, x_1681);
x_1683 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1683, 0, x_1682);
lean_ctor_set(x_1683, 1, x_1677);
if (lean_is_scalar(x_1678)) {
 x_1684 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1684 = x_1678;
}
lean_ctor_set(x_1684, 0, x_1673);
lean_ctor_set(x_1684, 1, x_1675);
lean_ctor_set(x_1684, 2, x_1676);
lean_ctor_set(x_1684, 3, x_1683);
lean_ctor_set_uint16(x_1684, sizeof(void*)*4, x_1674);
x_1685 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__13, &lp_dasmodel_emitNoteLoadPath___closed__13_once, _init_lp_dasmodel_emitNoteLoadPath___closed__13);
x_1686 = lp_dasmodel_CodeBuilder_emitInst(x_1684, x_1685);
x_1687 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1686, x_1642);
x_1688 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_1689 = lp_dasmodel_CodeBuilder_emitInst(x_1687, x_1688);
x_1690 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_1689, x_1642);
x_1691 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1690, x_1533);
x_1692 = lp_dasmodel_CodeBuilder_emitInst(x_1691, x_5);
x_1693 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_1694 = lp_dasmodel_CodeBuilder_emitInst(x_1692, x_1693);
x_1695 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_1696 = lp_dasmodel_CodeBuilder_emitInst(x_1694, x_1695);
x_1697 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__19, &lp_dasmodel_emitNoteLoadPath___closed__19_once, _init_lp_dasmodel_emitNoteLoadPath___closed__19);
x_1698 = lp_dasmodel_CodeBuilder_emitInst(x_1696, x_1697);
x_1699 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_1700 = lp_dasmodel_CodeBuilder_emitInst(x_1698, x_1699);
x_1701 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_1702 = lp_dasmodel_CodeBuilder_emitInst(x_1700, x_1701);
x_1703 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__29));
x_1704 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1702, x_1502, x_1703);
x_1705 = lp_dasmodel_CodeBuilder_label(x_1704, x_1667);
x_1706 = lp_dasmodel_CodeBuilder_emitInst(x_1705, x_1620);
x_1707 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1706, x_1642);
x_1708 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1707, x_1533);
x_1709 = lp_dasmodel_CodeBuilder_emitInst(x_1708, x_5);
x_1710 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1709, x_1642);
x_1711 = lp_dasmodel_CodeBuilder_emitInst(x_1710, x_1695);
x_1712 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__30, &lp_dasmodel_emitSustainEffects___closed__30_once, _init_lp_dasmodel_emitSustainEffects___closed__30);
x_1713 = lp_dasmodel_CodeBuilder_emitInst(x_1711, x_1712);
x_1714 = lp_dasmodel_CodeBuilder_emitInst(x_1713, x_1701);
x_1715 = lp_dasmodel_CodeBuilder_label(x_1714, x_1703);
x_1716 = lp_dasmodel_CodeBuilder_label(x_1715, x_1639);
x_1717 = lp_dasmodel_CodeBuilder_emitInst(x_1716, x_1620);
x_1718 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1717, x_3);
x_1719 = lp_dasmodel_CodeBuilder_emitInst(x_1718, x_5);
x_1720 = lp_dasmodel_CodeBuilder_emitInst(x_1719, x_7);
x_1721 = lean_ctor_get(x_1720, 0);
lean_inc_ref(x_1721);
x_1722 = lean_ctor_get_uint16(x_1720, sizeof(void*)*4);
x_1723 = lean_ctor_get(x_1720, 1);
lean_inc(x_1723);
x_1724 = lean_ctor_get(x_1720, 2);
lean_inc(x_1724);
x_1725 = lean_ctor_get(x_1720, 3);
lean_inc(x_1725);
if (lean_is_exclusive(x_1720)) {
 lean_ctor_release(x_1720, 0);
 lean_ctor_release(x_1720, 1);
 lean_ctor_release(x_1720, 2);
 lean_ctor_release(x_1720, 3);
 x_1726 = x_1720;
} else {
 lean_dec_ref(x_1720);
 x_1726 = lean_box(0);
}
x_1727 = lean_array_get_size(x_1721);
x_1728 = lean_nat_sub(x_1727, x_1493);
x_1729 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_1730 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_1730, 0, x_1728);
lean_ctor_set(x_1730, 1, x_1729);
x_1731 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_1731, 0, x_1730);
lean_ctor_set(x_1731, 1, x_1725);
if (lean_is_scalar(x_1726)) {
 x_1732 = lean_alloc_ctor(0, 4, 2);
} else {
 x_1732 = x_1726;
}
lean_ctor_set(x_1732, 0, x_1721);
lean_ctor_set(x_1732, 1, x_1723);
lean_ctor_set(x_1732, 2, x_1724);
lean_ctor_set(x_1732, 3, x_1731);
lean_ctor_set_uint16(x_1732, sizeof(void*)*4, x_1722);
x_1733 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__32));
x_1734 = lp_dasmodel_CodeBuilder_emitBranch(x_1732, x_1499, x_1733);
x_1735 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__33));
x_1736 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1734, x_1502, x_1735);
x_1737 = lp_dasmodel_CodeBuilder_label(x_1736, x_1733);
x_1738 = lp_dasmodel_CodeBuilder_emitInst(x_1737, x_1688);
x_1739 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_1740 = lp_dasmodel_CodeBuilder_emitInst(x_1738, x_1739);
x_1741 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__35, &lp_dasmodel_emitSustainEffects___closed__35_once, _init_lp_dasmodel_emitSustainEffects___closed__35);
x_1742 = lp_dasmodel_CodeBuilder_emitInst(x_1740, x_1741);
x_1743 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__36));
x_1744 = lp_dasmodel_CodeBuilder_emitBranch(x_1742, x_1523, x_1743);
x_1745 = lp_dasmodel_CodeBuilder_emitInst(x_1744, x_1526);
x_1746 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_1747 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1745, x_1746);
x_1748 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__37, &lp_dasmodel_emitSustainEffects___closed__37_once, _init_lp_dasmodel_emitSustainEffects___closed__37);
x_1749 = lp_dasmodel_CodeBuilder_emitInst(x_1747, x_1748);
x_1750 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__38));
x_1751 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_1749, x_1502, x_1750);
x_1752 = lp_dasmodel_CodeBuilder_label(x_1751, x_1743);
x_1753 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1752, x_1746);
x_1754 = lp_dasmodel_CodeBuilder_label(x_1753, x_1750);
x_1755 = lp_dasmodel_CodeBuilder_emitInst(x_1754, x_5);
x_1756 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_1757 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_1755, x_1756);
x_1758 = lp_dasmodel_CodeBuilder_emitInst(x_1757, x_1506);
x_1759 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_1760 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_1758, x_1759);
x_1761 = lp_dasmodel_CodeBuilder_emitInst(x_1760, x_1688);
x_1762 = lp_dasmodel_CodeBuilder_emitInst(x_1761, x_1620);
x_1763 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1762, x_1533);
x_1764 = lp_dasmodel_CodeBuilder_emitInst(x_1763, x_5);
x_1765 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_1766 = lp_dasmodel_CodeBuilder_emitInst(x_1764, x_1765);
x_1767 = lp_dasmodel_CodeBuilder_emitInst(x_1766, x_1695);
x_1768 = lp_dasmodel_CodeBuilder_emitInst(x_1767, x_1693);
x_1769 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_1770 = lp_dasmodel_CodeBuilder_emitInst(x_1768, x_1769);
x_1771 = lp_dasmodel_CodeBuilder_label(x_1770, x_1735);
x_1772 = lp_dasmodel_I_rts;
x_1773 = lp_dasmodel_CodeBuilder_emitInst(x_1771, x_1772);
x_1774 = lp_dasmodel_emitNoteLoadPath(x_1773, x_2);
return x_1774;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitSustainEffects___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_emitSustainEffects(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 247;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__4(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 7;
x_2 = lp_dasmodel_I_and__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__5(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 4;
x_2 = lp_dasmodel_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 7;
x_2 = lp_dasmodel_I_eor__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__8(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 246;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__9(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 245;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__10(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 248;
x_2 = lp_dasmodel_I_sbc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__14(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 247;
x_2 = lp_dasmodel_I_dec__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__15(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 244;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__16(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 6;
x_2 = lp_dasmodel_I_cmp__imm(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__19(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 246;
x_2 = lp_dasmodel_I_ldy__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__20(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 242;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__21(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 243;
x_2 = lp_dasmodel_I_sta__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__23(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 242;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__24(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 245;
x_2 = lp_dasmodel_I_adc__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__25(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 243;
x_2 = lp_dasmodel_I_lda__zp(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_emitVibrato___redArg___closed__26(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 244;
x_2 = lp_dasmodel_I_adc__zp(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitVibrato___redArg(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_2 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__20));
x_3 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_1, x_2);
x_4 = lp_dasmodel_I_tay;
x_5 = lp_dasmodel_CodeBuilder_emitInst(x_3, x_4);
x_6 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__1));
x_7 = lp_dasmodel_CodeBuilder_emitInst(x_5, x_6);
x_8 = !lean_is_exclusive(x_7);
if (x_8 == 0)
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; uint8_t x_17; lean_object* x_18; lean_object* x_19; uint8_t x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; uint8_t x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; uint8_t x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; uint8_t x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; uint8_t x_91; lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; 
x_9 = lean_ctor_get(x_7, 0);
x_10 = lean_ctor_get(x_7, 3);
x_11 = lean_array_get_size(x_9);
x_12 = lean_unsigned_to_nat(2u);
x_13 = lean_nat_sub(x_11, x_12);
x_14 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__0));
x_15 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_15, 0, x_13);
lean_ctor_set(x_15, 1, x_14);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_15);
lean_ctor_set(x_16, 1, x_10);
lean_ctor_set(x_7, 3, x_16);
x_17 = 27;
x_18 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__1));
x_19 = lp_dasmodel_CodeBuilder_emitBranch(x_7, x_17, x_18);
x_20 = 32;
x_21 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__2));
x_22 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_19, x_20, x_21);
x_23 = lp_dasmodel_CodeBuilder_label(x_22, x_18);
x_24 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__3, &lp_dasmodel_emitVibrato___redArg___closed__3_once, _init_lp_dasmodel_emitVibrato___redArg___closed__3);
x_25 = lp_dasmodel_CodeBuilder_emitInst(x_23, x_24);
x_26 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_27 = lp_dasmodel_CodeBuilder_emitInst(x_25, x_26);
x_28 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__4, &lp_dasmodel_emitVibrato___redArg___closed__4_once, _init_lp_dasmodel_emitVibrato___redArg___closed__4);
x_29 = lp_dasmodel_CodeBuilder_emitInst(x_27, x_28);
x_30 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__5, &lp_dasmodel_emitVibrato___redArg___closed__5_once, _init_lp_dasmodel_emitVibrato___redArg___closed__5);
x_31 = lp_dasmodel_CodeBuilder_emitInst(x_29, x_30);
x_32 = 24;
x_33 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__6));
x_34 = lp_dasmodel_CodeBuilder_emitBranch(x_31, x_32, x_33);
x_35 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__7, &lp_dasmodel_emitVibrato___redArg___closed__7_once, _init_lp_dasmodel_emitVibrato___redArg___closed__7);
x_36 = lp_dasmodel_CodeBuilder_emitInst(x_34, x_35);
x_37 = lp_dasmodel_CodeBuilder_label(x_36, x_33);
x_38 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__8, &lp_dasmodel_emitVibrato___redArg___closed__8_once, _init_lp_dasmodel_emitVibrato___redArg___closed__8);
x_39 = lp_dasmodel_CodeBuilder_emitInst(x_37, x_38);
x_40 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_41 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_39, x_40);
x_42 = lp_dasmodel_CodeBuilder_emitInst(x_41, x_4);
x_43 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_44 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_42, x_43);
x_45 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_46 = lp_dasmodel_CodeBuilder_emitInst(x_44, x_45);
x_47 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_48 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_46, x_47);
x_49 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__5, &lp_dasmodel_emitSustainEffects___closed__5_once, _init_lp_dasmodel_emitSustainEffects___closed__5);
x_50 = lp_dasmodel_CodeBuilder_emitInst(x_48, x_49);
x_51 = lp_dasmodel_I_iny;
x_52 = lp_dasmodel_CodeBuilder_emitInst(x_50, x_51);
x_53 = lp_dasmodel_I_sec;
x_54 = lp_dasmodel_CodeBuilder_emitInst(x_52, x_53);
x_55 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_54, x_47);
x_56 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__16, &lp_dasmodel_emitSustainEffects___closed__16_once, _init_lp_dasmodel_emitSustainEffects___closed__16);
x_57 = lp_dasmodel_CodeBuilder_emitInst(x_55, x_56);
x_58 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__9, &lp_dasmodel_emitVibrato___redArg___closed__9_once, _init_lp_dasmodel_emitVibrato___redArg___closed__9);
x_59 = lp_dasmodel_CodeBuilder_emitInst(x_57, x_58);
x_60 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_59, x_43);
x_61 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__10, &lp_dasmodel_emitVibrato___redArg___closed__10_once, _init_lp_dasmodel_emitVibrato___redArg___closed__10);
x_62 = lp_dasmodel_CodeBuilder_emitInst(x_60, x_61);
x_63 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__11));
x_64 = lp_dasmodel_CodeBuilder_label(x_62, x_63);
x_65 = lp_dasmodel_I_lsr__a;
x_66 = lp_dasmodel_CodeBuilder_emitInst(x_64, x_65);
x_67 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__13));
x_68 = lp_dasmodel_CodeBuilder_emitInst(x_66, x_67);
x_69 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__14, &lp_dasmodel_emitVibrato___redArg___closed__14_once, _init_lp_dasmodel_emitVibrato___redArg___closed__14);
x_70 = lp_dasmodel_CodeBuilder_emitInst(x_68, x_69);
x_71 = 29;
x_72 = lp_dasmodel_CodeBuilder_emitBranch(x_70, x_71, x_63);
x_73 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__15, &lp_dasmodel_emitVibrato___redArg___closed__15_once, _init_lp_dasmodel_emitVibrato___redArg___closed__15);
x_74 = lp_dasmodel_CodeBuilder_emitInst(x_72, x_73);
x_75 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_76 = lp_dasmodel_CodeBuilder_emitInst(x_74, x_75);
x_77 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_78 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_76, x_77);
x_79 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__16, &lp_dasmodel_emitVibrato___redArg___closed__16_once, _init_lp_dasmodel_emitVibrato___redArg___closed__16);
x_80 = lp_dasmodel_CodeBuilder_emitInst(x_78, x_79);
x_81 = 25;
x_82 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__17));
x_83 = lp_dasmodel_CodeBuilder_emitBranch(x_80, x_81, x_82);
x_84 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__18));
x_85 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_83, x_20, x_84);
x_86 = lp_dasmodel_CodeBuilder_label(x_85, x_82);
x_87 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__19, &lp_dasmodel_emitVibrato___redArg___closed__19_once, _init_lp_dasmodel_emitVibrato___redArg___closed__19);
x_88 = lp_dasmodel_CodeBuilder_emitInst(x_86, x_87);
x_89 = lp_dasmodel_I_dey;
x_90 = lp_dasmodel_CodeBuilder_emitInst(x_88, x_89);
x_91 = 28;
x_92 = lp_dasmodel_CodeBuilder_emitBranch(x_90, x_91, x_84);
x_93 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_94 = lp_dasmodel_CodeBuilder_emitInst(x_92, x_93);
x_95 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__20, &lp_dasmodel_emitVibrato___redArg___closed__20_once, _init_lp_dasmodel_emitVibrato___redArg___closed__20);
x_96 = lp_dasmodel_CodeBuilder_emitInst(x_94, x_95);
x_97 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_98 = lp_dasmodel_CodeBuilder_emitInst(x_96, x_97);
x_99 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__21, &lp_dasmodel_emitVibrato___redArg___closed__21_once, _init_lp_dasmodel_emitVibrato___redArg___closed__21);
x_100 = lp_dasmodel_CodeBuilder_emitInst(x_98, x_99);
x_101 = lp_dasmodel_CodeBuilder_emitInst(x_100, x_51);
x_102 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__22));
x_103 = lp_dasmodel_CodeBuilder_label(x_101, x_102);
x_104 = lp_dasmodel_I_clc;
x_105 = lp_dasmodel_CodeBuilder_emitInst(x_103, x_104);
x_106 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__23, &lp_dasmodel_emitVibrato___redArg___closed__23_once, _init_lp_dasmodel_emitVibrato___redArg___closed__23);
x_107 = lp_dasmodel_CodeBuilder_emitInst(x_105, x_106);
x_108 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__24, &lp_dasmodel_emitVibrato___redArg___closed__24_once, _init_lp_dasmodel_emitVibrato___redArg___closed__24);
x_109 = lp_dasmodel_CodeBuilder_emitInst(x_107, x_108);
x_110 = lp_dasmodel_CodeBuilder_emitInst(x_109, x_95);
x_111 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__25, &lp_dasmodel_emitVibrato___redArg___closed__25_once, _init_lp_dasmodel_emitVibrato___redArg___closed__25);
x_112 = lp_dasmodel_CodeBuilder_emitInst(x_110, x_111);
x_113 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__26, &lp_dasmodel_emitVibrato___redArg___closed__26_once, _init_lp_dasmodel_emitVibrato___redArg___closed__26);
x_114 = lp_dasmodel_CodeBuilder_emitInst(x_112, x_113);
x_115 = lp_dasmodel_CodeBuilder_emitInst(x_114, x_99);
x_116 = lp_dasmodel_CodeBuilder_emitInst(x_115, x_89);
x_117 = lp_dasmodel_CodeBuilder_emitBranch(x_116, x_71, x_102);
x_118 = lp_dasmodel_CodeBuilder_emitInst(x_117, x_75);
x_119 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_120 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_118, x_119);
x_121 = lp_dasmodel_CodeBuilder_emitInst(x_120, x_4);
x_122 = lp_dasmodel_CodeBuilder_emitInst(x_121, x_106);
x_123 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_124 = lp_dasmodel_CodeBuilder_emitInst(x_122, x_123);
x_125 = lp_dasmodel_CodeBuilder_emitInst(x_124, x_111);
x_126 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_127 = lp_dasmodel_CodeBuilder_emitInst(x_125, x_126);
x_128 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_127, x_20, x_21);
x_129 = lp_dasmodel_CodeBuilder_label(x_128, x_84);
x_130 = lp_dasmodel_CodeBuilder_emitInst(x_129, x_75);
x_131 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_130, x_119);
x_132 = lp_dasmodel_CodeBuilder_emitInst(x_131, x_4);
x_133 = lp_dasmodel_CodeBuilder_emitInst(x_132, x_93);
x_134 = lp_dasmodel_CodeBuilder_emitInst(x_133, x_123);
x_135 = lp_dasmodel_CodeBuilder_emitInst(x_134, x_97);
x_136 = lp_dasmodel_CodeBuilder_emitInst(x_135, x_126);
x_137 = lp_dasmodel_CodeBuilder_label(x_136, x_21);
x_138 = lp_dasmodel_CodeBuilder_emitInst(x_137, x_75);
return x_138;
}
else
{
lean_object* x_139; uint16_t x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; lean_object* x_150; uint8_t x_151; lean_object* x_152; lean_object* x_153; uint8_t x_154; lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; lean_object* x_164; lean_object* x_165; uint8_t x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; lean_object* x_191; lean_object* x_192; lean_object* x_193; lean_object* x_194; lean_object* x_195; lean_object* x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; lean_object* x_202; lean_object* x_203; lean_object* x_204; uint8_t x_205; lean_object* x_206; lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; lean_object* x_214; uint8_t x_215; lean_object* x_216; lean_object* x_217; lean_object* x_218; lean_object* x_219; lean_object* x_220; lean_object* x_221; lean_object* x_222; lean_object* x_223; lean_object* x_224; uint8_t x_225; lean_object* x_226; lean_object* x_227; lean_object* x_228; lean_object* x_229; lean_object* x_230; lean_object* x_231; lean_object* x_232; lean_object* x_233; lean_object* x_234; lean_object* x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; lean_object* x_239; lean_object* x_240; lean_object* x_241; lean_object* x_242; lean_object* x_243; lean_object* x_244; lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; lean_object* x_249; lean_object* x_250; lean_object* x_251; lean_object* x_252; lean_object* x_253; lean_object* x_254; lean_object* x_255; lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; lean_object* x_265; lean_object* x_266; lean_object* x_267; lean_object* x_268; lean_object* x_269; lean_object* x_270; lean_object* x_271; lean_object* x_272; 
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
x_147 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__0));
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
x_151 = 27;
x_152 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__1));
x_153 = lp_dasmodel_CodeBuilder_emitBranch(x_150, x_151, x_152);
x_154 = 32;
x_155 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__2));
x_156 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_153, x_154, x_155);
x_157 = lp_dasmodel_CodeBuilder_label(x_156, x_152);
x_158 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__3, &lp_dasmodel_emitVibrato___redArg___closed__3_once, _init_lp_dasmodel_emitVibrato___redArg___closed__3);
x_159 = lp_dasmodel_CodeBuilder_emitInst(x_157, x_158);
x_160 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__34, &lp_dasmodel_emitSustainEffects___closed__34_once, _init_lp_dasmodel_emitSustainEffects___closed__34);
x_161 = lp_dasmodel_CodeBuilder_emitInst(x_159, x_160);
x_162 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__4, &lp_dasmodel_emitVibrato___redArg___closed__4_once, _init_lp_dasmodel_emitVibrato___redArg___closed__4);
x_163 = lp_dasmodel_CodeBuilder_emitInst(x_161, x_162);
x_164 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__5, &lp_dasmodel_emitVibrato___redArg___closed__5_once, _init_lp_dasmodel_emitVibrato___redArg___closed__5);
x_165 = lp_dasmodel_CodeBuilder_emitInst(x_163, x_164);
x_166 = 24;
x_167 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__6));
x_168 = lp_dasmodel_CodeBuilder_emitBranch(x_165, x_166, x_167);
x_169 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__7, &lp_dasmodel_emitVibrato___redArg___closed__7_once, _init_lp_dasmodel_emitVibrato___redArg___closed__7);
x_170 = lp_dasmodel_CodeBuilder_emitInst(x_168, x_169);
x_171 = lp_dasmodel_CodeBuilder_label(x_170, x_167);
x_172 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__8, &lp_dasmodel_emitVibrato___redArg___closed__8_once, _init_lp_dasmodel_emitVibrato___redArg___closed__8);
x_173 = lp_dasmodel_CodeBuilder_emitInst(x_171, x_172);
x_174 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_175 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_173, x_174);
x_176 = lp_dasmodel_CodeBuilder_emitInst(x_175, x_4);
x_177 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_178 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_176, x_177);
x_179 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__26, &lp_dasmodel_emitSustainEffects___closed__26_once, _init_lp_dasmodel_emitSustainEffects___closed__26);
x_180 = lp_dasmodel_CodeBuilder_emitInst(x_178, x_179);
x_181 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_182 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_180, x_181);
x_183 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__5, &lp_dasmodel_emitSustainEffects___closed__5_once, _init_lp_dasmodel_emitSustainEffects___closed__5);
x_184 = lp_dasmodel_CodeBuilder_emitInst(x_182, x_183);
x_185 = lp_dasmodel_I_iny;
x_186 = lp_dasmodel_CodeBuilder_emitInst(x_184, x_185);
x_187 = lp_dasmodel_I_sec;
x_188 = lp_dasmodel_CodeBuilder_emitInst(x_186, x_187);
x_189 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_188, x_181);
x_190 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__16, &lp_dasmodel_emitSustainEffects___closed__16_once, _init_lp_dasmodel_emitSustainEffects___closed__16);
x_191 = lp_dasmodel_CodeBuilder_emitInst(x_189, x_190);
x_192 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__9, &lp_dasmodel_emitVibrato___redArg___closed__9_once, _init_lp_dasmodel_emitVibrato___redArg___closed__9);
x_193 = lp_dasmodel_CodeBuilder_emitInst(x_191, x_192);
x_194 = lp_dasmodel_CodeBuilder_emitLdaAbsY(x_193, x_177);
x_195 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__10, &lp_dasmodel_emitVibrato___redArg___closed__10_once, _init_lp_dasmodel_emitVibrato___redArg___closed__10);
x_196 = lp_dasmodel_CodeBuilder_emitInst(x_194, x_195);
x_197 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__11));
x_198 = lp_dasmodel_CodeBuilder_label(x_196, x_197);
x_199 = lp_dasmodel_I_lsr__a;
x_200 = lp_dasmodel_CodeBuilder_emitInst(x_198, x_199);
x_201 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__13));
x_202 = lp_dasmodel_CodeBuilder_emitInst(x_200, x_201);
x_203 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__14, &lp_dasmodel_emitVibrato___redArg___closed__14_once, _init_lp_dasmodel_emitVibrato___redArg___closed__14);
x_204 = lp_dasmodel_CodeBuilder_emitInst(x_202, x_203);
x_205 = 29;
x_206 = lp_dasmodel_CodeBuilder_emitBranch(x_204, x_205, x_197);
x_207 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__15, &lp_dasmodel_emitVibrato___redArg___closed__15_once, _init_lp_dasmodel_emitVibrato___redArg___closed__15);
x_208 = lp_dasmodel_CodeBuilder_emitInst(x_206, x_207);
x_209 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__18, &lp_dasmodel_emitNoteLoadPath___closed__18_once, _init_lp_dasmodel_emitNoteLoadPath___closed__18);
x_210 = lp_dasmodel_CodeBuilder_emitInst(x_208, x_209);
x_211 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_212 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_210, x_211);
x_213 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__16, &lp_dasmodel_emitVibrato___redArg___closed__16_once, _init_lp_dasmodel_emitVibrato___redArg___closed__16);
x_214 = lp_dasmodel_CodeBuilder_emitInst(x_212, x_213);
x_215 = 25;
x_216 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__17));
x_217 = lp_dasmodel_CodeBuilder_emitBranch(x_214, x_215, x_216);
x_218 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__18));
x_219 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_217, x_154, x_218);
x_220 = lp_dasmodel_CodeBuilder_label(x_219, x_216);
x_221 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__19, &lp_dasmodel_emitVibrato___redArg___closed__19_once, _init_lp_dasmodel_emitVibrato___redArg___closed__19);
x_222 = lp_dasmodel_CodeBuilder_emitInst(x_220, x_221);
x_223 = lp_dasmodel_I_dey;
x_224 = lp_dasmodel_CodeBuilder_emitInst(x_222, x_223);
x_225 = 28;
x_226 = lp_dasmodel_CodeBuilder_emitBranch(x_224, x_225, x_218);
x_227 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__27, &lp_dasmodel_emitSustainEffects___closed__27_once, _init_lp_dasmodel_emitSustainEffects___closed__27);
x_228 = lp_dasmodel_CodeBuilder_emitInst(x_226, x_227);
x_229 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__20, &lp_dasmodel_emitVibrato___redArg___closed__20_once, _init_lp_dasmodel_emitVibrato___redArg___closed__20);
x_230 = lp_dasmodel_CodeBuilder_emitInst(x_228, x_229);
x_231 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__39, &lp_dasmodel_emitSustainEffects___closed__39_once, _init_lp_dasmodel_emitSustainEffects___closed__39);
x_232 = lp_dasmodel_CodeBuilder_emitInst(x_230, x_231);
x_233 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__21, &lp_dasmodel_emitVibrato___redArg___closed__21_once, _init_lp_dasmodel_emitVibrato___redArg___closed__21);
x_234 = lp_dasmodel_CodeBuilder_emitInst(x_232, x_233);
x_235 = lp_dasmodel_CodeBuilder_emitInst(x_234, x_185);
x_236 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__22));
x_237 = lp_dasmodel_CodeBuilder_label(x_235, x_236);
x_238 = lp_dasmodel_I_clc;
x_239 = lp_dasmodel_CodeBuilder_emitInst(x_237, x_238);
x_240 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__23, &lp_dasmodel_emitVibrato___redArg___closed__23_once, _init_lp_dasmodel_emitVibrato___redArg___closed__23);
x_241 = lp_dasmodel_CodeBuilder_emitInst(x_239, x_240);
x_242 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__24, &lp_dasmodel_emitVibrato___redArg___closed__24_once, _init_lp_dasmodel_emitVibrato___redArg___closed__24);
x_243 = lp_dasmodel_CodeBuilder_emitInst(x_241, x_242);
x_244 = lp_dasmodel_CodeBuilder_emitInst(x_243, x_229);
x_245 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__25, &lp_dasmodel_emitVibrato___redArg___closed__25_once, _init_lp_dasmodel_emitVibrato___redArg___closed__25);
x_246 = lp_dasmodel_CodeBuilder_emitInst(x_244, x_245);
x_247 = lean_obj_once(&lp_dasmodel_emitVibrato___redArg___closed__26, &lp_dasmodel_emitVibrato___redArg___closed__26_once, _init_lp_dasmodel_emitVibrato___redArg___closed__26);
x_248 = lp_dasmodel_CodeBuilder_emitInst(x_246, x_247);
x_249 = lp_dasmodel_CodeBuilder_emitInst(x_248, x_233);
x_250 = lp_dasmodel_CodeBuilder_emitInst(x_249, x_223);
x_251 = lp_dasmodel_CodeBuilder_emitBranch(x_250, x_205, x_236);
x_252 = lp_dasmodel_CodeBuilder_emitInst(x_251, x_209);
x_253 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_254 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_252, x_253);
x_255 = lp_dasmodel_CodeBuilder_emitInst(x_254, x_4);
x_256 = lp_dasmodel_CodeBuilder_emitInst(x_255, x_240);
x_257 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__26, &lp_dasmodel_emitNoteLoadPath___closed__26_once, _init_lp_dasmodel_emitNoteLoadPath___closed__26);
x_258 = lp_dasmodel_CodeBuilder_emitInst(x_256, x_257);
x_259 = lp_dasmodel_CodeBuilder_emitInst(x_258, x_245);
x_260 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__24, &lp_dasmodel_emitNoteLoadPath___closed__24_once, _init_lp_dasmodel_emitNoteLoadPath___closed__24);
x_261 = lp_dasmodel_CodeBuilder_emitInst(x_259, x_260);
x_262 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_261, x_154, x_155);
x_263 = lp_dasmodel_CodeBuilder_label(x_262, x_218);
x_264 = lp_dasmodel_CodeBuilder_emitInst(x_263, x_209);
x_265 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_264, x_253);
x_266 = lp_dasmodel_CodeBuilder_emitInst(x_265, x_4);
x_267 = lp_dasmodel_CodeBuilder_emitInst(x_266, x_227);
x_268 = lp_dasmodel_CodeBuilder_emitInst(x_267, x_257);
x_269 = lp_dasmodel_CodeBuilder_emitInst(x_268, x_231);
x_270 = lp_dasmodel_CodeBuilder_emitInst(x_269, x_260);
x_271 = lp_dasmodel_CodeBuilder_label(x_270, x_155);
x_272 = lp_dasmodel_CodeBuilder_emitInst(x_271, x_209);
return x_272;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitVibrato(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_emitVibrato___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitVibrato___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_emitVibrato(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_emitExecVoice___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; 
x_1 = 3;
x_2 = lp_dasmodel_I_cmp__imm(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitExecVoice(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; uint8_t x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; 
x_3 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00__private_Codegen_0__emitPlay_spec__0___redArg___closed__0));
x_4 = lp_dasmodel_CodeBuilder_label(x_1, x_3);
x_5 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_6 = lp_dasmodel_CodeBuilder_emitDecAbsX(x_4, x_5);
x_7 = 29;
x_8 = ((lean_object*)(lp_dasmodel_emitExecVoice___closed__0));
x_9 = lp_dasmodel_CodeBuilder_emitBranch(x_6, x_7, x_8);
x_10 = 32;
x_11 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__0));
x_12 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_9, x_10, x_11);
x_13 = lp_dasmodel_CodeBuilder_label(x_12, x_8);
x_14 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__1, &lp_dasmodel_emitNoteLoadPath___closed__1_once, _init_lp_dasmodel_emitNoteLoadPath___closed__1);
x_15 = lp_dasmodel_CodeBuilder_emitInst(x_13, x_14);
x_16 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_15, x_5);
x_17 = lean_obj_once(&lp_dasmodel_emitExecVoice___closed__1, &lp_dasmodel_emitExecVoice___closed__1_once, _init_lp_dasmodel_emitExecVoice___closed__1);
x_18 = lp_dasmodel_CodeBuilder_emitInst(x_16, x_17);
x_19 = 27;
x_20 = ((lean_object*)(lp_dasmodel_emitExecVoice___closed__2));
x_21 = lp_dasmodel_CodeBuilder_emitBranch(x_18, x_19, x_20);
x_22 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_23 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_21, x_22);
x_24 = lp_dasmodel_I_tay;
x_25 = lp_dasmodel_CodeBuilder_emitInst(x_23, x_24);
x_26 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__44));
x_27 = lp_dasmodel_CodeBuilder_emitLdaAbsX(x_25, x_26);
x_28 = lean_obj_once(&lp_dasmodel_emitSustainEffects___closed__28, &lp_dasmodel_emitSustainEffects___closed__28_once, _init_lp_dasmodel_emitSustainEffects___closed__28);
x_29 = lp_dasmodel_CodeBuilder_emitInst(x_27, x_28);
x_30 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__32, &lp_dasmodel_emitNoteLoadPath___closed__32_once, _init_lp_dasmodel_emitNoteLoadPath___closed__32);
x_31 = lp_dasmodel_CodeBuilder_emitInst(x_29, x_30);
x_32 = lean_obj_once(&lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1, &lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1_once, _init_lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__1);
x_33 = lp_dasmodel_CodeBuilder_emitInst(x_31, x_32);
x_34 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__41, &lp_dasmodel_emitNoteLoadPath___closed__41_once, _init_lp_dasmodel_emitNoteLoadPath___closed__41);
x_35 = lp_dasmodel_CodeBuilder_emitInst(x_33, x_34);
x_36 = lean_obj_once(&lp_dasmodel_emitNoteLoadPath___closed__43, &lp_dasmodel_emitNoteLoadPath___closed__43_once, _init_lp_dasmodel_emitNoteLoadPath___closed__43);
x_37 = lp_dasmodel_CodeBuilder_emitInst(x_35, x_36);
x_38 = lp_dasmodel_I_rts;
x_39 = lp_dasmodel_CodeBuilder_emitInst(x_37, x_38);
x_40 = lp_dasmodel_CodeBuilder_label(x_39, x_20);
x_41 = lp_dasmodel_emitVibrato___redArg(x_40);
x_42 = lp_dasmodel_emitSustainEffects(x_41, x_2);
return x_42;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_emitExecVoice___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_emitExecVoice(x_1, x_2);
lean_dec_ref(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__15(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; lean_object* x_13; 
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
x_12 = lean_ctor_get(x_4, 2);
lean_inc_ref(x_12);
lean_dec(x_4);
x_13 = lean_ctor_get(x_12, 2);
lean_inc(x_13);
lean_dec_ref(x_12);
if (lean_obj_tag(x_13) == 0)
{
uint8_t x_14; 
x_14 = 0;
x_7 = x_14;
goto block_11;
}
else
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; 
x_15 = lean_ctor_get(x_13, 0);
lean_inc(x_15);
lean_dec_ref(x_13);
x_16 = lean_ctor_get(x_15, 0);
lean_inc(x_16);
lean_dec(x_15);
x_17 = lean_unsigned_to_nat(1u);
x_18 = l_List_get_x3fInternal___redArg(x_16, x_17);
lean_dec(x_16);
if (lean_obj_tag(x_18) == 0)
{
uint8_t x_19; 
x_19 = 0;
x_7 = x_19;
goto block_11;
}
else
{
lean_object* x_20; lean_object* x_21; uint8_t x_22; 
x_20 = lean_ctor_get(x_18, 0);
lean_inc(x_20);
lean_dec_ref(x_18);
x_21 = l_Int_toNat(x_20);
lean_dec(x_20);
x_22 = lean_uint8_of_nat(x_21);
lean_dec(x_21);
x_7 = x_22;
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
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_11; uint8_t x_14; 
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_2, 2);
x_14 = lean_nat_dec_lt(x_4, x_5);
if (x_14 == 0)
{
lean_dec(x_4);
return x_3;
}
else
{
lean_object* x_15; 
lean_inc(x_4);
x_15 = l_List_get_x3fInternal___redArg(x_1, x_4);
if (lean_obj_tag(x_15) == 0)
{
uint8_t x_16; lean_object* x_17; 
x_16 = 0;
x_17 = lp_dasmodel_CodeBuilder_emitByte(x_3, x_16);
x_7 = x_17;
goto block_10;
}
else
{
lean_object* x_18; lean_object* x_19; uint8_t x_20; 
x_18 = lean_ctor_get(x_15, 0);
lean_inc(x_18);
lean_dec_ref(x_15);
x_19 = lean_unsigned_to_nat(104u);
x_20 = lean_nat_dec_eq(x_4, x_19);
if (x_20 == 0)
{
lean_object* x_21; uint8_t x_22; 
x_21 = lean_ctor_get(x_18, 0);
lean_inc(x_21);
lean_dec(x_18);
x_22 = lean_uint8_of_nat(x_21);
lean_dec(x_21);
x_11 = x_22;
goto block_13;
}
else
{
uint8_t x_23; 
lean_dec(x_18);
x_23 = 0;
x_11 = x_23;
goto block_13;
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
block_13:
{
lean_object* x_12; 
x_12 = lp_dasmodel_CodeBuilder_emitByte(x_3, x_11);
x_7 = x_12;
goto block_10;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__9(lean_object* x_1, lean_object* x_2) {
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
x_7 = lean_ctor_get(x_5, 6);
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
x_13 = lean_ctor_get(x_11, 6);
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
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_11; uint8_t x_14; 
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_2, 2);
x_14 = lean_nat_dec_lt(x_4, x_5);
if (x_14 == 0)
{
lean_dec(x_4);
return x_3;
}
else
{
lean_object* x_15; 
lean_inc(x_4);
x_15 = l_List_get_x3fInternal___redArg(x_1, x_4);
if (lean_obj_tag(x_15) == 0)
{
uint8_t x_16; lean_object* x_17; 
x_16 = 0;
x_17 = lp_dasmodel_CodeBuilder_emitByte(x_3, x_16);
x_7 = x_17;
goto block_10;
}
else
{
lean_object* x_18; lean_object* x_19; uint8_t x_20; 
x_18 = lean_ctor_get(x_15, 0);
lean_inc(x_18);
lean_dec_ref(x_15);
x_19 = lean_unsigned_to_nat(104u);
x_20 = lean_nat_dec_eq(x_4, x_19);
if (x_20 == 0)
{
lean_object* x_21; uint8_t x_22; 
x_21 = lean_ctor_get(x_18, 1);
lean_inc(x_21);
lean_dec(x_18);
x_22 = lean_uint8_of_nat(x_21);
lean_dec(x_21);
x_11 = x_22;
goto block_13;
}
else
{
uint8_t x_23; 
lean_dec(x_18);
x_23 = 0;
x_11 = x_23;
goto block_13;
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
block_13:
{
lean_object* x_12; 
x_12 = lp_dasmodel_CodeBuilder_emitByte(x_3, x_11);
x_7 = x_12;
goto block_10;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__13(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_4, 3);
lean_inc_ref(x_5);
x_6 = !lean_is_exclusive(x_1);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; 
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_ctor_get(x_1, 0);
lean_dec(x_8);
x_9 = lean_ctor_get(x_5, 2);
lean_inc(x_9);
lean_dec_ref(x_5);
x_10 = lean_uint8_of_nat(x_9);
lean_dec(x_9);
x_11 = lean_box(x_10);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_11);
{
lean_object* _tmp_0 = x_7;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; 
x_13 = lean_ctor_get(x_1, 1);
lean_inc(x_13);
lean_dec(x_1);
x_14 = lean_ctor_get(x_5, 2);
lean_inc(x_14);
lean_dec_ref(x_5);
x_15 = lean_uint8_of_nat(x_14);
lean_dec(x_14);
x_16 = lean_box(x_15);
x_17 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_2);
x_1 = x_13;
x_2 = x_17;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__12(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_4, 3);
lean_inc_ref(x_5);
x_6 = !lean_is_exclusive(x_1);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; 
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_ctor_get(x_1, 0);
lean_dec(x_8);
x_9 = lean_ctor_get(x_5, 1);
lean_inc(x_9);
lean_dec_ref(x_5);
x_10 = lean_uint8_of_nat(x_9);
lean_dec(x_9);
x_11 = lean_box(x_10);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_11);
{
lean_object* _tmp_0 = x_7;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; 
x_13 = lean_ctor_get(x_1, 1);
lean_inc(x_13);
lean_dec(x_1);
x_14 = lean_ctor_get(x_5, 1);
lean_inc(x_14);
lean_dec_ref(x_5);
x_15 = lean_uint8_of_nat(x_14);
lean_dec(x_14);
x_16 = lean_box(x_15);
x_17 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_2);
x_1 = x_13;
x_2 = x_17;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__18(lean_object* x_1, lean_object* x_2) {
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
static lean_object* _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0(void) {
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
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
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
uint8_t x_12; 
x_12 = !lean_is_exclusive(x_3);
if (x_12 == 0)
{
lean_object* x_13; uint8_t x_14; 
x_13 = lean_ctor_get(x_3, 1);
x_14 = !lean_is_exclusive(x_13);
if (x_14 == 0)
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; 
x_15 = lean_ctor_get(x_3, 0);
x_16 = lean_ctor_get(x_13, 0);
x_17 = lean_ctor_get(x_13, 1);
x_18 = lean_box(0);
lean_inc(x_4);
x_19 = l_List_get_x3fInternal___redArg(x_1, x_4);
if (lean_obj_tag(x_19) == 0)
{
lean_object* x_20; lean_object* x_21; lean_object* x_22; 
x_20 = lean_obj_once(&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0, &lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0_once, _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0);
x_21 = l_List_appendTR___redArg(x_17, x_20);
x_22 = l_List_appendTR___redArg(x_16, x_20);
lean_ctor_set(x_13, 1, x_21);
lean_ctor_set(x_13, 0, x_22);
x_7 = x_3;
goto block_10;
}
else
{
lean_object* x_23; uint8_t x_24; 
x_23 = lean_ctor_get(x_19, 0);
lean_inc(x_23);
lean_dec_ref(x_19);
x_24 = !lean_is_exclusive(x_23);
if (x_24 == 0)
{
lean_object* x_25; lean_object* x_26; uint16_t x_27; uint8_t x_28; lean_object* x_29; lean_object* x_30; uint16_t x_31; uint16_t x_32; uint8_t x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; uint8_t x_39; lean_object* x_40; 
x_25 = lean_ctor_get(x_23, 0);
x_26 = lean_ctor_get(x_23, 1);
lean_dec(x_26);
x_27 = lp_dasmodel_CodeBuilder_currentAddr(x_15);
x_28 = lean_uint16_to_uint8(x_27);
x_29 = lean_box(x_28);
lean_ctor_set_tag(x_23, 1);
lean_ctor_set(x_23, 1, x_18);
lean_ctor_set(x_23, 0, x_29);
x_30 = l_List_appendTR___redArg(x_17, x_23);
x_31 = 8;
x_32 = lean_uint16_shift_right(x_27, x_31);
x_33 = lean_uint16_to_uint8(x_32);
x_34 = lean_box(x_33);
x_35 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_35, 0, x_34);
lean_ctor_set(x_35, 1, x_18);
x_36 = l_List_appendTR___redArg(x_16, x_35);
x_37 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__18(x_25, x_18);
x_38 = lp_dasmodel_CodeBuilder_emitData(x_15, x_37);
x_39 = 255;
x_40 = lp_dasmodel_CodeBuilder_emitByte(x_38, x_39);
lean_ctor_set(x_13, 1, x_30);
lean_ctor_set(x_13, 0, x_36);
lean_ctor_set(x_3, 0, x_40);
x_7 = x_3;
goto block_10;
}
else
{
lean_object* x_41; uint16_t x_42; uint8_t x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; uint16_t x_47; uint16_t x_48; uint8_t x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; uint8_t x_55; lean_object* x_56; 
x_41 = lean_ctor_get(x_23, 0);
lean_inc(x_41);
lean_dec(x_23);
x_42 = lp_dasmodel_CodeBuilder_currentAddr(x_15);
x_43 = lean_uint16_to_uint8(x_42);
x_44 = lean_box(x_43);
x_45 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_45, 0, x_44);
lean_ctor_set(x_45, 1, x_18);
x_46 = l_List_appendTR___redArg(x_17, x_45);
x_47 = 8;
x_48 = lean_uint16_shift_right(x_42, x_47);
x_49 = lean_uint16_to_uint8(x_48);
x_50 = lean_box(x_49);
x_51 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_51, 0, x_50);
lean_ctor_set(x_51, 1, x_18);
x_52 = l_List_appendTR___redArg(x_16, x_51);
x_53 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__18(x_41, x_18);
x_54 = lp_dasmodel_CodeBuilder_emitData(x_15, x_53);
x_55 = 255;
x_56 = lp_dasmodel_CodeBuilder_emitByte(x_54, x_55);
lean_ctor_set(x_13, 1, x_46);
lean_ctor_set(x_13, 0, x_52);
lean_ctor_set(x_3, 0, x_56);
x_7 = x_3;
goto block_10;
}
}
}
else
{
lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; 
x_57 = lean_ctor_get(x_3, 0);
x_58 = lean_ctor_get(x_13, 0);
x_59 = lean_ctor_get(x_13, 1);
lean_inc(x_59);
lean_inc(x_58);
lean_dec(x_13);
x_60 = lean_box(0);
lean_inc(x_4);
x_61 = l_List_get_x3fInternal___redArg(x_1, x_4);
if (lean_obj_tag(x_61) == 0)
{
lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; 
x_62 = lean_obj_once(&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0, &lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0_once, _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0);
x_63 = l_List_appendTR___redArg(x_59, x_62);
x_64 = l_List_appendTR___redArg(x_58, x_62);
x_65 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_65, 0, x_64);
lean_ctor_set(x_65, 1, x_63);
lean_ctor_set(x_3, 1, x_65);
x_7 = x_3;
goto block_10;
}
else
{
lean_object* x_66; lean_object* x_67; lean_object* x_68; uint16_t x_69; uint8_t x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; uint16_t x_74; uint16_t x_75; uint8_t x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; uint8_t x_82; lean_object* x_83; lean_object* x_84; 
x_66 = lean_ctor_get(x_61, 0);
lean_inc(x_66);
lean_dec_ref(x_61);
x_67 = lean_ctor_get(x_66, 0);
lean_inc(x_67);
if (lean_is_exclusive(x_66)) {
 lean_ctor_release(x_66, 0);
 lean_ctor_release(x_66, 1);
 x_68 = x_66;
} else {
 lean_dec_ref(x_66);
 x_68 = lean_box(0);
}
x_69 = lp_dasmodel_CodeBuilder_currentAddr(x_57);
x_70 = lean_uint16_to_uint8(x_69);
x_71 = lean_box(x_70);
if (lean_is_scalar(x_68)) {
 x_72 = lean_alloc_ctor(1, 2, 0);
} else {
 x_72 = x_68;
 lean_ctor_set_tag(x_72, 1);
}
lean_ctor_set(x_72, 0, x_71);
lean_ctor_set(x_72, 1, x_60);
x_73 = l_List_appendTR___redArg(x_59, x_72);
x_74 = 8;
x_75 = lean_uint16_shift_right(x_69, x_74);
x_76 = lean_uint16_to_uint8(x_75);
x_77 = lean_box(x_76);
x_78 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_78, 0, x_77);
lean_ctor_set(x_78, 1, x_60);
x_79 = l_List_appendTR___redArg(x_58, x_78);
x_80 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__18(x_67, x_60);
x_81 = lp_dasmodel_CodeBuilder_emitData(x_57, x_80);
x_82 = 255;
x_83 = lp_dasmodel_CodeBuilder_emitByte(x_81, x_82);
x_84 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_84, 0, x_79);
lean_ctor_set(x_84, 1, x_73);
lean_ctor_set(x_3, 1, x_84);
lean_ctor_set(x_3, 0, x_83);
x_7 = x_3;
goto block_10;
}
}
}
else
{
lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; 
x_85 = lean_ctor_get(x_3, 1);
x_86 = lean_ctor_get(x_3, 0);
lean_inc(x_85);
lean_inc(x_86);
lean_dec(x_3);
x_87 = lean_ctor_get(x_85, 0);
lean_inc(x_87);
x_88 = lean_ctor_get(x_85, 1);
lean_inc(x_88);
if (lean_is_exclusive(x_85)) {
 lean_ctor_release(x_85, 0);
 lean_ctor_release(x_85, 1);
 x_89 = x_85;
} else {
 lean_dec_ref(x_85);
 x_89 = lean_box(0);
}
x_90 = lean_box(0);
lean_inc(x_4);
x_91 = l_List_get_x3fInternal___redArg(x_1, x_4);
if (lean_obj_tag(x_91) == 0)
{
lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; 
x_92 = lean_obj_once(&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0, &lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0_once, _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___closed__0);
x_93 = l_List_appendTR___redArg(x_88, x_92);
x_94 = l_List_appendTR___redArg(x_87, x_92);
if (lean_is_scalar(x_89)) {
 x_95 = lean_alloc_ctor(0, 2, 0);
} else {
 x_95 = x_89;
}
lean_ctor_set(x_95, 0, x_94);
lean_ctor_set(x_95, 1, x_93);
x_96 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_96, 0, x_86);
lean_ctor_set(x_96, 1, x_95);
x_7 = x_96;
goto block_10;
}
else
{
lean_object* x_97; lean_object* x_98; lean_object* x_99; uint16_t x_100; uint8_t x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; uint16_t x_105; uint16_t x_106; uint8_t x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; uint8_t x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; 
x_97 = lean_ctor_get(x_91, 0);
lean_inc(x_97);
lean_dec_ref(x_91);
x_98 = lean_ctor_get(x_97, 0);
lean_inc(x_98);
if (lean_is_exclusive(x_97)) {
 lean_ctor_release(x_97, 0);
 lean_ctor_release(x_97, 1);
 x_99 = x_97;
} else {
 lean_dec_ref(x_97);
 x_99 = lean_box(0);
}
x_100 = lp_dasmodel_CodeBuilder_currentAddr(x_86);
x_101 = lean_uint16_to_uint8(x_100);
x_102 = lean_box(x_101);
if (lean_is_scalar(x_99)) {
 x_103 = lean_alloc_ctor(1, 2, 0);
} else {
 x_103 = x_99;
 lean_ctor_set_tag(x_103, 1);
}
lean_ctor_set(x_103, 0, x_102);
lean_ctor_set(x_103, 1, x_90);
x_104 = l_List_appendTR___redArg(x_88, x_103);
x_105 = 8;
x_106 = lean_uint16_shift_right(x_100, x_105);
x_107 = lean_uint16_to_uint8(x_106);
x_108 = lean_box(x_107);
x_109 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_109, 0, x_108);
lean_ctor_set(x_109, 1, x_90);
x_110 = l_List_appendTR___redArg(x_87, x_109);
x_111 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__18(x_98, x_90);
x_112 = lp_dasmodel_CodeBuilder_emitData(x_86, x_111);
x_113 = 255;
x_114 = lp_dasmodel_CodeBuilder_emitByte(x_112, x_113);
if (lean_is_scalar(x_89)) {
 x_115 = lean_alloc_ctor(0, 2, 0);
} else {
 x_115 = x_89;
}
lean_ctor_set(x_115, 0, x_110);
lean_ctor_set(x_115, 1, x_104);
x_116 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_116, 0, x_114);
lean_ctor_set(x_116, 1, x_115);
x_7 = x_116;
goto block_10;
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
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__8(lean_object* x_1, lean_object* x_2) {
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
x_7 = lean_ctor_get(x_5, 5);
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
x_13 = lean_ctor_get(x_11, 5);
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
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__14(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; lean_object* x_13; 
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
x_12 = lean_ctor_get(x_4, 2);
lean_inc_ref(x_12);
lean_dec(x_4);
x_13 = lean_ctor_get(x_12, 0);
lean_inc(x_13);
lean_dec_ref(x_12);
if (lean_obj_tag(x_13) == 0)
{
uint8_t x_14; 
x_14 = 0;
x_7 = x_14;
goto block_11;
}
else
{
lean_object* x_15; lean_object* x_16; uint8_t x_17; 
x_15 = lean_ctor_get(x_13, 0);
lean_inc(x_15);
lean_dec_ref(x_13);
x_16 = lean_ctor_get(x_15, 1);
lean_inc(x_16);
lean_dec(x_15);
x_17 = lean_uint8_of_nat(x_16);
lean_dec(x_16);
x_7 = x_17;
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
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__1(lean_object* x_1, lean_object* x_2) {
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
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4___redArg(lean_object* x_1, lean_object* x_2) {
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
x_17 = lean_ctor_get(x_7, 0);
lean_inc(x_17);
x_18 = lean_ctor_get(x_7, 1);
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
x_33 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__1(x_17, x_19);
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
x_38 = lean_ctor_get(x_7, 0);
lean_inc(x_38);
x_39 = lean_ctor_get(x_7, 1);
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
x_54 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__1(x_38, x_40);
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
x_62 = lean_ctor_get(x_7, 0);
lean_inc(x_62);
x_63 = lean_ctor_get(x_7, 1);
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
x_78 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__1(x_62, x_64);
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
x_91 = lean_ctor_get(x_83, 0);
lean_inc(x_91);
x_92 = lean_ctor_get(x_83, 1);
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
x_107 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__1(x_91, x_93);
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
x_122 = lean_ctor_get(x_113, 0);
lean_inc(x_122);
x_123 = lean_ctor_get(x_113, 1);
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
x_139 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__1(x_122, x_124);
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
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__7(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_4, 3);
lean_inc_ref(x_5);
x_6 = !lean_is_exclusive(x_1);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; 
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_ctor_get(x_1, 0);
lean_dec(x_8);
x_9 = lean_ctor_get(x_5, 5);
lean_inc(x_9);
lean_dec_ref(x_5);
x_10 = lean_uint8_of_nat(x_9);
lean_dec(x_9);
x_11 = lean_box(x_10);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_11);
{
lean_object* _tmp_0 = x_7;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; 
x_13 = lean_ctor_get(x_1, 1);
lean_inc(x_13);
lean_dec(x_1);
x_14 = lean_ctor_get(x_5, 5);
lean_inc(x_14);
lean_dec_ref(x_5);
x_15 = lean_uint8_of_nat(x_14);
lean_dec(x_14);
x_16 = lean_box(x_15);
x_17 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_2);
x_1 = x_13;
x_2 = x_17;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__5(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_13; lean_object* x_14; 
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
x_13 = lean_ctor_get(x_4, 0);
lean_inc(x_13);
lean_dec(x_4);
x_14 = l_List_head_x3f___redArg(x_13);
lean_dec(x_13);
if (lean_obj_tag(x_14) == 0)
{
lean_object* x_15; 
x_15 = lean_unsigned_to_nat(0u);
x_7 = x_15;
goto block_12;
}
else
{
lean_object* x_16; 
x_16 = lean_ctor_get(x_14, 0);
lean_inc(x_16);
lean_dec_ref(x_14);
x_7 = x_16;
goto block_12;
}
block_12:
{
uint8_t x_8; lean_object* x_9; lean_object* x_10; 
x_8 = lean_uint8_of_nat(x_7);
lean_dec(x_7);
x_9 = lean_box(x_8);
if (lean_is_scalar(x_6)) {
 x_10 = lean_alloc_ctor(1, 2, 0);
} else {
 x_10 = x_6;
}
lean_ctor_set(x_10, 0, x_9);
lean_ctor_set(x_10, 1, x_2);
x_1 = x_5;
x_2 = x_10;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
return x_2;
}
else
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; 
x_3 = lean_ctor_get(x_1, 0);
x_4 = lean_ctor_get(x_1, 1);
x_5 = lean_ctor_get(x_3, 0);
x_6 = lean_ctor_get(x_3, 1);
x_7 = lean_ctor_get(x_3, 2);
x_8 = lean_uint8_of_nat(x_5);
x_9 = lp_dasmodel_CodeBuilder_emitByte(x_2, x_8);
x_10 = lean_uint8_of_nat(x_6);
x_11 = lp_dasmodel_CodeBuilder_emitByte(x_9, x_10);
x_12 = lean_uint8_of_nat(x_7);
x_13 = lp_dasmodel_CodeBuilder_emitByte(x_11, x_12);
x_1 = x_4;
x_2 = x_13;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17___redArg(lean_object* x_1, lean_object* x_2) {
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
x_14 = lp_dasmodel_CodeBuilder_currentAddr(x_8);
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
x_24 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(x_6, x_8);
lean_dec(x_6);
x_25 = 0;
x_26 = lp_dasmodel_CodeBuilder_emitByte(x_24, x_25);
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
x_31 = lp_dasmodel_CodeBuilder_currentAddr(x_8);
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
x_41 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(x_6, x_8);
lean_dec(x_6);
x_42 = 0;
x_43 = lp_dasmodel_CodeBuilder_emitByte(x_41, x_42);
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
x_53 = lp_dasmodel_CodeBuilder_currentAddr(x_48);
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
x_63 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(x_46, x_48);
lean_dec(x_46);
x_64 = 0;
x_65 = lp_dasmodel_CodeBuilder_emitByte(x_63, x_64);
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
x_77 = lp_dasmodel_CodeBuilder_currentAddr(x_71);
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
x_88 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(x_69, x_71);
lean_dec(x_69);
x_89 = 0;
x_90 = lp_dasmodel_CodeBuilder_emitByte(x_88, x_89);
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
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__11(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; uint8_t x_13; 
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
x_12 = lean_ctor_get(x_4, 3);
lean_inc_ref(x_12);
lean_dec(x_4);
x_13 = lean_ctor_get_uint8(x_12, sizeof(void*)*6);
switch (x_13) {
case 0:
{
lean_object* x_14; lean_object* x_15; uint8_t x_16; 
x_14 = lean_ctor_get(x_12, 0);
lean_inc(x_14);
lean_dec_ref(x_12);
x_15 = lean_unsigned_to_nat(0u);
x_16 = lean_nat_dec_eq(x_14, x_15);
lean_dec(x_14);
if (x_16 == 0)
{
uint8_t x_17; 
x_17 = 1;
x_7 = x_17;
goto block_11;
}
else
{
uint8_t x_18; 
x_18 = 0;
x_7 = x_18;
goto block_11;
}
}
case 1:
{
uint8_t x_19; 
lean_dec_ref(x_12);
x_19 = 2;
x_7 = x_19;
goto block_11;
}
default: 
{
uint8_t x_20; 
lean_dec_ref(x_12);
x_20 = 0;
x_7 = x_20;
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
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__10(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_4, 3);
lean_inc_ref(x_5);
x_6 = !lean_is_exclusive(x_1);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; 
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_ctor_get(x_1, 0);
lean_dec(x_8);
x_9 = lean_ctor_get(x_5, 0);
lean_inc(x_9);
lean_dec_ref(x_5);
x_10 = lean_uint8_of_nat(x_9);
lean_dec(x_9);
x_11 = lean_box(x_10);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_11);
{
lean_object* _tmp_0 = x_7;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; 
x_13 = lean_ctor_get(x_1, 1);
lean_inc(x_13);
lean_dec(x_1);
x_14 = lean_ctor_get(x_5, 0);
lean_inc(x_14);
lean_dec_ref(x_5);
x_15 = lean_uint8_of_nat(x_14);
lean_dec(x_14);
x_16 = lean_box(x_15);
x_17 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_2);
x_1 = x_13;
x_2 = x_17;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__6(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_4, 3);
lean_inc_ref(x_5);
x_6 = !lean_is_exclusive(x_1);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; 
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_ctor_get(x_1, 0);
lean_dec(x_8);
x_9 = lean_ctor_get(x_5, 4);
lean_inc(x_9);
lean_dec_ref(x_5);
x_10 = lean_uint8_of_nat(x_9);
lean_dec(x_9);
x_11 = lean_box(x_10);
lean_ctor_set(x_1, 1, x_2);
lean_ctor_set(x_1, 0, x_11);
{
lean_object* _tmp_0 = x_7;
lean_object* _tmp_1 = x_1;
x_1 = _tmp_0;
x_2 = _tmp_1;
}
goto _start;
}
else
{
lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; 
x_13 = lean_ctor_get(x_1, 1);
lean_inc(x_13);
lean_dec(x_1);
x_14 = lean_ctor_get(x_5, 4);
lean_inc(x_14);
lean_dec_ref(x_5);
x_15 = lean_uint8_of_nat(x_14);
lean_dec(x_14);
x_16 = lean_box(x_15);
x_17 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_2);
x_1 = x_13;
x_2 = x_17;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__16(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; lean_object* x_12; lean_object* x_13; 
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
x_12 = lean_ctor_get(x_4, 2);
lean_inc_ref(x_12);
lean_dec(x_4);
x_13 = lean_ctor_get(x_12, 1);
lean_inc(x_13);
lean_dec_ref(x_12);
if (lean_obj_tag(x_13) == 0)
{
uint8_t x_14; 
x_14 = 0;
x_7 = x_14;
goto block_11;
}
else
{
uint8_t x_15; 
lean_dec_ref(x_13);
x_15 = 1;
x_7 = x_15;
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
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__1(void) {
_start:
{
lean_object* x_1; uint16_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_box(0);
x_2 = 4096;
x_3 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__0, &lp_dasmodel_generateSID___redArg___closed__0_once, _init_lp_dasmodel_generateSID___redArg___closed__0);
x_4 = lean_alloc_ctor(0, 4, 2);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
lean_ctor_set(x_4, 2, x_1);
lean_ctor_set(x_4, 3, x_1);
lean_ctor_set_uint16(x_4, sizeof(void*)*4, x_2);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__2(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__0));
x_2 = 32;
x_3 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__1, &lp_dasmodel_generateSID___redArg___closed__1_once, _init_lp_dasmodel_generateSID___redArg___closed__1);
x_4 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_3, x_2, x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__6(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitPlay___closed__0));
x_2 = 32;
x_3 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__2, &lp_dasmodel_generateSID___redArg___closed__2_once, _init_lp_dasmodel_generateSID___redArg___closed__2);
x_4 = lp_dasmodel_CodeBuilder_emitJmpLabel(x_3, x_2, x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__6, &lp_dasmodel_generateSID___redArg___closed__6_once, _init_lp_dasmodel_generateSID___redArg___closed__6);
x_2 = lp_dasmodel___private_Codegen_0__emitInit___redArg(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__12(void) {
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
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__13(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__12, &lp_dasmodel_generateSID___redArg___closed__12_once, _init_lp_dasmodel_generateSID___redArg___closed__12);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__14(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__13, &lp_dasmodel_generateSID___redArg___closed__13_once, _init_lp_dasmodel_generateSID___redArg___closed__13);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__15(void) {
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
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__16(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__15, &lp_dasmodel_generateSID___redArg___closed__15_once, _init_lp_dasmodel_generateSID___redArg___closed__15);
x_2 = 7;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_generateSID___redArg___closed__17(void) {
_start:
{
lean_object* x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__16, &lp_dasmodel_generateSID___redArg___closed__16_once, _init_lp_dasmodel_generateSID___redArg___closed__16);
x_2 = 0;
x_3 = lean_box(x_2);
x_4 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set(x_4, 1, x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_generateSID___redArg(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; uint8_t x_18; 
x_2 = lean_ctor_get(x_1, 0);
lean_inc(x_2);
x_3 = lean_ctor_get(x_1, 1);
lean_inc(x_3);
x_4 = lean_ctor_get(x_1, 2);
lean_inc(x_4);
x_5 = lean_ctor_get(x_1, 3);
lean_inc(x_5);
x_6 = lean_unsigned_to_nat(0u);
x_7 = lean_box(0);
x_8 = l_List_lengthTR___redArg(x_2);
x_9 = lean_unsigned_to_nat(1u);
x_10 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_10, 0, x_6);
lean_ctor_set(x_10, 1, x_8);
lean_ctor_set(x_10, 2, x_9);
x_11 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__3));
x_12 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__5));
lean_inc(x_3);
x_13 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4___redArg(x_3, x_12);
x_14 = lean_ctor_get(x_13, 1);
lean_inc(x_14);
x_15 = lean_ctor_get(x_14, 1);
lean_inc(x_15);
x_16 = lean_ctor_get(x_13, 0);
lean_inc(x_16);
lean_dec_ref(x_13);
x_17 = lean_ctor_get(x_14, 0);
lean_inc(x_17);
lean_dec(x_14);
x_18 = !lean_is_exclusive(x_15);
if (x_18 == 0)
{
lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; uint8_t x_93; 
x_19 = lean_ctor_get(x_15, 0);
x_20 = lean_ctor_get(x_15, 1);
x_21 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__7, &lp_dasmodel_generateSID___redArg___closed__7_once, _init_lp_dasmodel_generateSID___redArg___closed__7);
x_22 = lp_dasmodel___private_Codegen_0__emitPlay(x_21, x_1);
x_23 = lp_dasmodel_emitExecVoice(x_22, x_1);
lean_dec_ref(x_1);
x_24 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_25 = lp_dasmodel_CodeBuilder_label(x_23, x_24);
x_26 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg(x_2, x_10, x_25, x_6);
x_27 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_28 = lp_dasmodel_CodeBuilder_label(x_26, x_27);
x_29 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg(x_2, x_10, x_28, x_6);
lean_dec_ref(x_10);
lean_dec(x_2);
x_30 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__8));
x_31 = lp_dasmodel_CodeBuilder_label(x_29, x_30);
x_32 = lp_dasmodel_CodeBuilder_emitData(x_31, x_17);
x_33 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__9));
x_34 = lp_dasmodel_CodeBuilder_label(x_32, x_33);
x_35 = lp_dasmodel_CodeBuilder_emitData(x_34, x_16);
x_36 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__10));
x_37 = lp_dasmodel_CodeBuilder_label(x_35, x_36);
x_38 = lp_dasmodel_CodeBuilder_emitData(x_37, x_19);
x_39 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__11));
x_40 = lp_dasmodel_CodeBuilder_label(x_38, x_39);
x_41 = lp_dasmodel_CodeBuilder_emitData(x_40, x_20);
x_42 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_43 = lp_dasmodel_CodeBuilder_label(x_41, x_42);
lean_inc(x_3);
x_44 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__5(x_3, x_7);
x_45 = lp_dasmodel_CodeBuilder_emitData(x_43, x_44);
x_46 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__33));
x_47 = lp_dasmodel_CodeBuilder_label(x_45, x_46);
lean_inc(x_3);
x_48 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__6(x_3, x_7);
x_49 = lp_dasmodel_CodeBuilder_emitData(x_47, x_48);
x_50 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__35));
x_51 = lp_dasmodel_CodeBuilder_label(x_49, x_50);
lean_inc(x_3);
x_52 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__7(x_3, x_7);
x_53 = lp_dasmodel_CodeBuilder_emitData(x_51, x_52);
x_54 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__40));
x_55 = lp_dasmodel_CodeBuilder_label(x_53, x_54);
lean_inc(x_3);
x_56 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__8(x_3, x_7);
x_57 = lp_dasmodel_CodeBuilder_emitData(x_55, x_56);
x_58 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__42));
x_59 = lp_dasmodel_CodeBuilder_label(x_57, x_58);
lean_inc(x_3);
x_60 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__9(x_3, x_7);
x_61 = lp_dasmodel_CodeBuilder_emitData(x_59, x_60);
x_62 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__2));
x_63 = lp_dasmodel_CodeBuilder_label(x_61, x_62);
lean_inc(x_3);
x_64 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__10(x_3, x_7);
x_65 = lp_dasmodel_CodeBuilder_emitData(x_63, x_64);
x_66 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__6));
x_67 = lp_dasmodel_CodeBuilder_label(x_65, x_66);
lean_inc(x_3);
x_68 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__11(x_3, x_7);
x_69 = lp_dasmodel_CodeBuilder_emitData(x_67, x_68);
x_70 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__18));
x_71 = lp_dasmodel_CodeBuilder_label(x_69, x_70);
lean_inc(x_3);
x_72 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__12(x_3, x_7);
x_73 = lp_dasmodel_CodeBuilder_emitData(x_71, x_72);
x_74 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__13));
x_75 = lp_dasmodel_CodeBuilder_label(x_73, x_74);
lean_inc(x_3);
x_76 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__13(x_3, x_7);
x_77 = lp_dasmodel_CodeBuilder_emitData(x_75, x_76);
x_78 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__0));
x_79 = lp_dasmodel_CodeBuilder_label(x_77, x_78);
lean_inc(x_3);
x_80 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__14(x_3, x_7);
x_81 = lp_dasmodel_CodeBuilder_emitData(x_79, x_80);
x_82 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_83 = lp_dasmodel_CodeBuilder_label(x_81, x_82);
lean_inc(x_3);
x_84 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__15(x_3, x_7);
x_85 = lp_dasmodel_CodeBuilder_emitData(x_83, x_84);
x_86 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_87 = lp_dasmodel_CodeBuilder_label(x_85, x_86);
x_88 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__16(x_3, x_7);
x_89 = lp_dasmodel_CodeBuilder_emitData(x_87, x_88);
lean_ctor_set(x_15, 1, x_11);
lean_ctor_set(x_15, 0, x_89);
x_90 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17___redArg(x_5, x_15);
x_91 = lean_ctor_get(x_90, 1);
lean_inc(x_91);
x_92 = lean_ctor_get(x_90, 0);
lean_inc(x_92);
lean_dec_ref(x_90);
x_93 = !lean_is_exclusive(x_91);
if (x_93 == 0)
{
lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; lean_object* x_139; lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; lean_object* x_150; lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_154; lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; 
x_94 = lean_ctor_get(x_91, 0);
x_95 = lean_ctor_get(x_91, 1);
x_96 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__49));
x_97 = lp_dasmodel_CodeBuilder_label(x_92, x_96);
x_98 = lp_dasmodel_CodeBuilder_emitData(x_97, x_95);
x_99 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__50));
x_100 = lp_dasmodel_CodeBuilder_label(x_98, x_99);
x_101 = lp_dasmodel_CodeBuilder_emitData(x_100, x_94);
x_102 = l_List_lengthTR___redArg(x_4);
x_103 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_103, 0, x_6);
lean_ctor_set(x_103, 1, x_102);
lean_ctor_set(x_103, 2, x_9);
lean_ctor_set(x_91, 1, x_11);
lean_ctor_set(x_91, 0, x_101);
x_104 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg(x_4, x_103, x_91, x_6);
lean_dec_ref(x_103);
lean_dec(x_4);
x_105 = lean_ctor_get(x_104, 1);
lean_inc(x_105);
x_106 = lean_ctor_get(x_104, 0);
lean_inc(x_106);
lean_dec_ref(x_104);
x_107 = lean_ctor_get(x_105, 0);
lean_inc(x_107);
x_108 = lean_ctor_get(x_105, 1);
lean_inc(x_108);
lean_dec(x_105);
x_109 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_110 = lp_dasmodel_CodeBuilder_label(x_106, x_109);
x_111 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__14, &lp_dasmodel_generateSID___redArg___closed__14_once, _init_lp_dasmodel_generateSID___redArg___closed__14);
x_112 = lp_dasmodel_CodeBuilder_emitData(x_110, x_111);
x_113 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12));
x_114 = lp_dasmodel_CodeBuilder_label(x_112, x_113);
x_115 = lp_dasmodel_CodeBuilder_emitData(x_114, x_111);
x_116 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13));
x_117 = lp_dasmodel_CodeBuilder_label(x_115, x_116);
x_118 = lp_dasmodel_CodeBuilder_emitData(x_117, x_111);
x_119 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10));
x_120 = lp_dasmodel_CodeBuilder_label(x_118, x_119);
x_121 = lp_dasmodel_CodeBuilder_emitData(x_120, x_111);
x_122 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__44));
x_123 = lp_dasmodel_CodeBuilder_label(x_121, x_122);
x_124 = lp_dasmodel_CodeBuilder_emitData(x_123, x_111);
x_125 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11));
x_126 = lp_dasmodel_CodeBuilder_label(x_124, x_125);
x_127 = lp_dasmodel_CodeBuilder_emitData(x_126, x_111);
x_128 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__20));
x_129 = lp_dasmodel_CodeBuilder_label(x_127, x_128);
x_130 = lp_dasmodel_CodeBuilder_emitData(x_129, x_111);
x_131 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_132 = lp_dasmodel_CodeBuilder_label(x_130, x_131);
x_133 = lp_dasmodel_CodeBuilder_emitData(x_132, x_111);
x_134 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_135 = lp_dasmodel_CodeBuilder_label(x_133, x_134);
x_136 = lp_dasmodel_CodeBuilder_emitData(x_135, x_111);
x_137 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_138 = lp_dasmodel_CodeBuilder_label(x_136, x_137);
x_139 = lp_dasmodel_CodeBuilder_emitData(x_138, x_111);
x_140 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__38));
x_141 = lp_dasmodel_CodeBuilder_label(x_139, x_140);
x_142 = lp_dasmodel_CodeBuilder_emitData(x_141, x_111);
x_143 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__37));
x_144 = lp_dasmodel_CodeBuilder_label(x_142, x_143);
x_145 = lp_dasmodel_CodeBuilder_emitData(x_144, x_111);
x_146 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__39));
x_147 = lp_dasmodel_CodeBuilder_label(x_145, x_146);
x_148 = lp_dasmodel_CodeBuilder_emitData(x_147, x_111);
x_149 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_150 = lp_dasmodel_CodeBuilder_label(x_148, x_149);
x_151 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__17, &lp_dasmodel_generateSID___redArg___closed__17_once, _init_lp_dasmodel_generateSID___redArg___closed__17);
x_152 = lp_dasmodel_CodeBuilder_emitData(x_150, x_151);
x_153 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__45));
x_154 = lp_dasmodel_CodeBuilder_label(x_152, x_153);
x_155 = lp_dasmodel_CodeBuilder_emitData(x_154, x_108);
x_156 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__46));
x_157 = lp_dasmodel_CodeBuilder_label(x_155, x_156);
x_158 = lp_dasmodel_CodeBuilder_emitData(x_157, x_107);
x_159 = lp_dasmodel_CodeBuilder_resolve(x_158);
x_160 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__21));
x_161 = lean_ctor_get(x_159, 0);
lean_inc_ref(x_161);
lean_dec_ref(x_159);
x_162 = lp_dasmodel_buildSID(x_160, x_161);
lean_dec_ref(x_161);
return x_162;
}
else
{
lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; lean_object* x_191; lean_object* x_192; lean_object* x_193; lean_object* x_194; lean_object* x_195; lean_object* x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; lean_object* x_202; lean_object* x_203; lean_object* x_204; lean_object* x_205; lean_object* x_206; lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; lean_object* x_214; lean_object* x_215; lean_object* x_216; lean_object* x_217; lean_object* x_218; lean_object* x_219; lean_object* x_220; lean_object* x_221; lean_object* x_222; lean_object* x_223; lean_object* x_224; lean_object* x_225; lean_object* x_226; lean_object* x_227; lean_object* x_228; lean_object* x_229; lean_object* x_230; lean_object* x_231; lean_object* x_232; 
x_163 = lean_ctor_get(x_91, 0);
x_164 = lean_ctor_get(x_91, 1);
lean_inc(x_164);
lean_inc(x_163);
lean_dec(x_91);
x_165 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__49));
x_166 = lp_dasmodel_CodeBuilder_label(x_92, x_165);
x_167 = lp_dasmodel_CodeBuilder_emitData(x_166, x_164);
x_168 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__50));
x_169 = lp_dasmodel_CodeBuilder_label(x_167, x_168);
x_170 = lp_dasmodel_CodeBuilder_emitData(x_169, x_163);
x_171 = l_List_lengthTR___redArg(x_4);
x_172 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_172, 0, x_6);
lean_ctor_set(x_172, 1, x_171);
lean_ctor_set(x_172, 2, x_9);
x_173 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_173, 0, x_170);
lean_ctor_set(x_173, 1, x_11);
x_174 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg(x_4, x_172, x_173, x_6);
lean_dec_ref(x_172);
lean_dec(x_4);
x_175 = lean_ctor_get(x_174, 1);
lean_inc(x_175);
x_176 = lean_ctor_get(x_174, 0);
lean_inc(x_176);
lean_dec_ref(x_174);
x_177 = lean_ctor_get(x_175, 0);
lean_inc(x_177);
x_178 = lean_ctor_get(x_175, 1);
lean_inc(x_178);
lean_dec(x_175);
x_179 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_180 = lp_dasmodel_CodeBuilder_label(x_176, x_179);
x_181 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__14, &lp_dasmodel_generateSID___redArg___closed__14_once, _init_lp_dasmodel_generateSID___redArg___closed__14);
x_182 = lp_dasmodel_CodeBuilder_emitData(x_180, x_181);
x_183 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12));
x_184 = lp_dasmodel_CodeBuilder_label(x_182, x_183);
x_185 = lp_dasmodel_CodeBuilder_emitData(x_184, x_181);
x_186 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13));
x_187 = lp_dasmodel_CodeBuilder_label(x_185, x_186);
x_188 = lp_dasmodel_CodeBuilder_emitData(x_187, x_181);
x_189 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10));
x_190 = lp_dasmodel_CodeBuilder_label(x_188, x_189);
x_191 = lp_dasmodel_CodeBuilder_emitData(x_190, x_181);
x_192 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__44));
x_193 = lp_dasmodel_CodeBuilder_label(x_191, x_192);
x_194 = lp_dasmodel_CodeBuilder_emitData(x_193, x_181);
x_195 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11));
x_196 = lp_dasmodel_CodeBuilder_label(x_194, x_195);
x_197 = lp_dasmodel_CodeBuilder_emitData(x_196, x_181);
x_198 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__20));
x_199 = lp_dasmodel_CodeBuilder_label(x_197, x_198);
x_200 = lp_dasmodel_CodeBuilder_emitData(x_199, x_181);
x_201 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_202 = lp_dasmodel_CodeBuilder_label(x_200, x_201);
x_203 = lp_dasmodel_CodeBuilder_emitData(x_202, x_181);
x_204 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_205 = lp_dasmodel_CodeBuilder_label(x_203, x_204);
x_206 = lp_dasmodel_CodeBuilder_emitData(x_205, x_181);
x_207 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_208 = lp_dasmodel_CodeBuilder_label(x_206, x_207);
x_209 = lp_dasmodel_CodeBuilder_emitData(x_208, x_181);
x_210 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__38));
x_211 = lp_dasmodel_CodeBuilder_label(x_209, x_210);
x_212 = lp_dasmodel_CodeBuilder_emitData(x_211, x_181);
x_213 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__37));
x_214 = lp_dasmodel_CodeBuilder_label(x_212, x_213);
x_215 = lp_dasmodel_CodeBuilder_emitData(x_214, x_181);
x_216 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__39));
x_217 = lp_dasmodel_CodeBuilder_label(x_215, x_216);
x_218 = lp_dasmodel_CodeBuilder_emitData(x_217, x_181);
x_219 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_220 = lp_dasmodel_CodeBuilder_label(x_218, x_219);
x_221 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__17, &lp_dasmodel_generateSID___redArg___closed__17_once, _init_lp_dasmodel_generateSID___redArg___closed__17);
x_222 = lp_dasmodel_CodeBuilder_emitData(x_220, x_221);
x_223 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__45));
x_224 = lp_dasmodel_CodeBuilder_label(x_222, x_223);
x_225 = lp_dasmodel_CodeBuilder_emitData(x_224, x_178);
x_226 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__46));
x_227 = lp_dasmodel_CodeBuilder_label(x_225, x_226);
x_228 = lp_dasmodel_CodeBuilder_emitData(x_227, x_177);
x_229 = lp_dasmodel_CodeBuilder_resolve(x_228);
x_230 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__21));
x_231 = lean_ctor_get(x_229, 0);
lean_inc_ref(x_231);
lean_dec_ref(x_229);
x_232 = lp_dasmodel_buildSID(x_230, x_231);
lean_dec_ref(x_231);
return x_232;
}
}
else
{
lean_object* x_233; lean_object* x_234; lean_object* x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; lean_object* x_239; lean_object* x_240; lean_object* x_241; lean_object* x_242; lean_object* x_243; lean_object* x_244; lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; lean_object* x_249; lean_object* x_250; lean_object* x_251; lean_object* x_252; lean_object* x_253; lean_object* x_254; lean_object* x_255; lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; lean_object* x_265; lean_object* x_266; lean_object* x_267; lean_object* x_268; lean_object* x_269; lean_object* x_270; lean_object* x_271; lean_object* x_272; lean_object* x_273; lean_object* x_274; lean_object* x_275; lean_object* x_276; lean_object* x_277; lean_object* x_278; lean_object* x_279; lean_object* x_280; lean_object* x_281; lean_object* x_282; lean_object* x_283; lean_object* x_284; lean_object* x_285; lean_object* x_286; lean_object* x_287; lean_object* x_288; lean_object* x_289; lean_object* x_290; lean_object* x_291; lean_object* x_292; lean_object* x_293; lean_object* x_294; lean_object* x_295; lean_object* x_296; lean_object* x_297; lean_object* x_298; lean_object* x_299; lean_object* x_300; lean_object* x_301; lean_object* x_302; lean_object* x_303; lean_object* x_304; lean_object* x_305; lean_object* x_306; lean_object* x_307; lean_object* x_308; lean_object* x_309; lean_object* x_310; lean_object* x_311; lean_object* x_312; lean_object* x_313; lean_object* x_314; lean_object* x_315; lean_object* x_316; lean_object* x_317; lean_object* x_318; lean_object* x_319; lean_object* x_320; lean_object* x_321; lean_object* x_322; lean_object* x_323; lean_object* x_324; lean_object* x_325; lean_object* x_326; lean_object* x_327; lean_object* x_328; lean_object* x_329; lean_object* x_330; lean_object* x_331; lean_object* x_332; lean_object* x_333; lean_object* x_334; lean_object* x_335; lean_object* x_336; lean_object* x_337; lean_object* x_338; lean_object* x_339; lean_object* x_340; lean_object* x_341; lean_object* x_342; lean_object* x_343; lean_object* x_344; lean_object* x_345; lean_object* x_346; lean_object* x_347; lean_object* x_348; lean_object* x_349; lean_object* x_350; lean_object* x_351; lean_object* x_352; lean_object* x_353; lean_object* x_354; lean_object* x_355; lean_object* x_356; lean_object* x_357; lean_object* x_358; lean_object* x_359; lean_object* x_360; lean_object* x_361; lean_object* x_362; lean_object* x_363; lean_object* x_364; lean_object* x_365; lean_object* x_366; lean_object* x_367; lean_object* x_368; lean_object* x_369; lean_object* x_370; lean_object* x_371; lean_object* x_372; lean_object* x_373; lean_object* x_374; lean_object* x_375; lean_object* x_376; lean_object* x_377; lean_object* x_378; 
x_233 = lean_ctor_get(x_15, 0);
x_234 = lean_ctor_get(x_15, 1);
lean_inc(x_234);
lean_inc(x_233);
lean_dec(x_15);
x_235 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__7, &lp_dasmodel_generateSID___redArg___closed__7_once, _init_lp_dasmodel_generateSID___redArg___closed__7);
x_236 = lp_dasmodel___private_Codegen_0__emitPlay(x_235, x_1);
x_237 = lp_dasmodel_emitExecVoice(x_236, x_1);
lean_dec_ref(x_1);
x_238 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__25));
x_239 = lp_dasmodel_CodeBuilder_label(x_237, x_238);
x_240 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg(x_2, x_10, x_239, x_6);
x_241 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__23));
x_242 = lp_dasmodel_CodeBuilder_label(x_240, x_241);
x_243 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg(x_2, x_10, x_242, x_6);
lean_dec_ref(x_10);
lean_dec(x_2);
x_244 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__8));
x_245 = lp_dasmodel_CodeBuilder_label(x_243, x_244);
x_246 = lp_dasmodel_CodeBuilder_emitData(x_245, x_17);
x_247 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__9));
x_248 = lp_dasmodel_CodeBuilder_label(x_246, x_247);
x_249 = lp_dasmodel_CodeBuilder_emitData(x_248, x_16);
x_250 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__10));
x_251 = lp_dasmodel_CodeBuilder_label(x_249, x_250);
x_252 = lp_dasmodel_CodeBuilder_emitData(x_251, x_233);
x_253 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__11));
x_254 = lp_dasmodel_CodeBuilder_label(x_252, x_253);
x_255 = lp_dasmodel_CodeBuilder_emitData(x_254, x_234);
x_256 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__31));
x_257 = lp_dasmodel_CodeBuilder_label(x_255, x_256);
lean_inc(x_3);
x_258 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__5(x_3, x_7);
x_259 = lp_dasmodel_CodeBuilder_emitData(x_257, x_258);
x_260 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__33));
x_261 = lp_dasmodel_CodeBuilder_label(x_259, x_260);
lean_inc(x_3);
x_262 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__6(x_3, x_7);
x_263 = lp_dasmodel_CodeBuilder_emitData(x_261, x_262);
x_264 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__35));
x_265 = lp_dasmodel_CodeBuilder_label(x_263, x_264);
lean_inc(x_3);
x_266 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__7(x_3, x_7);
x_267 = lp_dasmodel_CodeBuilder_emitData(x_265, x_266);
x_268 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__40));
x_269 = lp_dasmodel_CodeBuilder_label(x_267, x_268);
lean_inc(x_3);
x_270 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__8(x_3, x_7);
x_271 = lp_dasmodel_CodeBuilder_emitData(x_269, x_270);
x_272 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__42));
x_273 = lp_dasmodel_CodeBuilder_label(x_271, x_272);
lean_inc(x_3);
x_274 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__9(x_3, x_7);
x_275 = lp_dasmodel_CodeBuilder_emitData(x_273, x_274);
x_276 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__2));
x_277 = lp_dasmodel_CodeBuilder_label(x_275, x_276);
lean_inc(x_3);
x_278 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__10(x_3, x_7);
x_279 = lp_dasmodel_CodeBuilder_emitData(x_277, x_278);
x_280 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__6));
x_281 = lp_dasmodel_CodeBuilder_label(x_279, x_280);
lean_inc(x_3);
x_282 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__11(x_3, x_7);
x_283 = lp_dasmodel_CodeBuilder_emitData(x_281, x_282);
x_284 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__18));
x_285 = lp_dasmodel_CodeBuilder_label(x_283, x_284);
lean_inc(x_3);
x_286 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__12(x_3, x_7);
x_287 = lp_dasmodel_CodeBuilder_emitData(x_285, x_286);
x_288 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__13));
x_289 = lp_dasmodel_CodeBuilder_label(x_287, x_288);
lean_inc(x_3);
x_290 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__13(x_3, x_7);
x_291 = lp_dasmodel_CodeBuilder_emitData(x_289, x_290);
x_292 = ((lean_object*)(lp_dasmodel_emitVibrato___redArg___closed__0));
x_293 = lp_dasmodel_CodeBuilder_label(x_291, x_292);
lean_inc(x_3);
x_294 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__14(x_3, x_7);
x_295 = lp_dasmodel_CodeBuilder_emitData(x_293, x_294);
x_296 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__31));
x_297 = lp_dasmodel_CodeBuilder_label(x_295, x_296);
lean_inc(x_3);
x_298 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__15(x_3, x_7);
x_299 = lp_dasmodel_CodeBuilder_emitData(x_297, x_298);
x_300 = ((lean_object*)(lp_dasmodel_emitSustainEffects___closed__19));
x_301 = lp_dasmodel_CodeBuilder_label(x_299, x_300);
x_302 = lp_dasmodel_List_mapTR_loop___at___00generateSID_spec__16(x_3, x_7);
x_303 = lp_dasmodel_CodeBuilder_emitData(x_301, x_302);
x_304 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_304, 0, x_303);
lean_ctor_set(x_304, 1, x_11);
x_305 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17___redArg(x_5, x_304);
x_306 = lean_ctor_get(x_305, 1);
lean_inc(x_306);
x_307 = lean_ctor_get(x_305, 0);
lean_inc(x_307);
lean_dec_ref(x_305);
x_308 = lean_ctor_get(x_306, 0);
lean_inc(x_308);
x_309 = lean_ctor_get(x_306, 1);
lean_inc(x_309);
if (lean_is_exclusive(x_306)) {
 lean_ctor_release(x_306, 0);
 lean_ctor_release(x_306, 1);
 x_310 = x_306;
} else {
 lean_dec_ref(x_306);
 x_310 = lean_box(0);
}
x_311 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__49));
x_312 = lp_dasmodel_CodeBuilder_label(x_307, x_311);
x_313 = lp_dasmodel_CodeBuilder_emitData(x_312, x_309);
x_314 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__50));
x_315 = lp_dasmodel_CodeBuilder_label(x_313, x_314);
x_316 = lp_dasmodel_CodeBuilder_emitData(x_315, x_308);
x_317 = l_List_lengthTR___redArg(x_4);
x_318 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_318, 0, x_6);
lean_ctor_set(x_318, 1, x_317);
lean_ctor_set(x_318, 2, x_9);
if (lean_is_scalar(x_310)) {
 x_319 = lean_alloc_ctor(0, 2, 0);
} else {
 x_319 = x_310;
}
lean_ctor_set(x_319, 0, x_316);
lean_ctor_set(x_319, 1, x_11);
x_320 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg(x_4, x_318, x_319, x_6);
lean_dec_ref(x_318);
lean_dec(x_4);
x_321 = lean_ctor_get(x_320, 1);
lean_inc(x_321);
x_322 = lean_ctor_get(x_320, 0);
lean_inc(x_322);
lean_dec_ref(x_320);
x_323 = lean_ctor_get(x_321, 0);
lean_inc(x_323);
x_324 = lean_ctor_get(x_321, 1);
lean_inc(x_324);
lean_dec(x_321);
x_325 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__9));
x_326 = lp_dasmodel_CodeBuilder_label(x_322, x_325);
x_327 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__14, &lp_dasmodel_generateSID___redArg___closed__14_once, _init_lp_dasmodel_generateSID___redArg___closed__14);
x_328 = lp_dasmodel_CodeBuilder_emitData(x_326, x_327);
x_329 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__12));
x_330 = lp_dasmodel_CodeBuilder_label(x_328, x_329);
x_331 = lp_dasmodel_CodeBuilder_emitData(x_330, x_327);
x_332 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__13));
x_333 = lp_dasmodel_CodeBuilder_label(x_331, x_332);
x_334 = lp_dasmodel_CodeBuilder_emitData(x_333, x_327);
x_335 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__10));
x_336 = lp_dasmodel_CodeBuilder_label(x_334, x_335);
x_337 = lp_dasmodel_CodeBuilder_emitData(x_336, x_327);
x_338 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__44));
x_339 = lp_dasmodel_CodeBuilder_label(x_337, x_338);
x_340 = lp_dasmodel_CodeBuilder_emitData(x_339, x_327);
x_341 = ((lean_object*)(lp_dasmodel___private_Codegen_0__emitInit___redArg___closed__11));
x_342 = lp_dasmodel_CodeBuilder_label(x_340, x_341);
x_343 = lp_dasmodel_CodeBuilder_emitData(x_342, x_327);
x_344 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__20));
x_345 = lp_dasmodel_CodeBuilder_label(x_343, x_344);
x_346 = lp_dasmodel_CodeBuilder_emitData(x_345, x_327);
x_347 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__28));
x_348 = lp_dasmodel_CodeBuilder_label(x_346, x_347);
x_349 = lp_dasmodel_CodeBuilder_emitData(x_348, x_327);
x_350 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__29));
x_351 = lp_dasmodel_CodeBuilder_label(x_349, x_350);
x_352 = lp_dasmodel_CodeBuilder_emitData(x_351, x_327);
x_353 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__53));
x_354 = lp_dasmodel_CodeBuilder_label(x_352, x_353);
x_355 = lp_dasmodel_CodeBuilder_emitData(x_354, x_327);
x_356 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__38));
x_357 = lp_dasmodel_CodeBuilder_label(x_355, x_356);
x_358 = lp_dasmodel_CodeBuilder_emitData(x_357, x_327);
x_359 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__37));
x_360 = lp_dasmodel_CodeBuilder_label(x_358, x_359);
x_361 = lp_dasmodel_CodeBuilder_emitData(x_360, x_327);
x_362 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__39));
x_363 = lp_dasmodel_CodeBuilder_label(x_361, x_362);
x_364 = lp_dasmodel_CodeBuilder_emitData(x_363, x_327);
x_365 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__21));
x_366 = lp_dasmodel_CodeBuilder_label(x_364, x_365);
x_367 = lean_obj_once(&lp_dasmodel_generateSID___redArg___closed__17, &lp_dasmodel_generateSID___redArg___closed__17_once, _init_lp_dasmodel_generateSID___redArg___closed__17);
x_368 = lp_dasmodel_CodeBuilder_emitData(x_366, x_367);
x_369 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__45));
x_370 = lp_dasmodel_CodeBuilder_label(x_368, x_369);
x_371 = lp_dasmodel_CodeBuilder_emitData(x_370, x_324);
x_372 = ((lean_object*)(lp_dasmodel_emitNoteLoadPath___closed__46));
x_373 = lp_dasmodel_CodeBuilder_label(x_371, x_372);
x_374 = lp_dasmodel_CodeBuilder_emitData(x_373, x_323);
x_375 = lp_dasmodel_CodeBuilder_resolve(x_374);
x_376 = ((lean_object*)(lp_dasmodel_generateSID___redArg___closed__21));
x_377 = lean_ctor_get(x_375, 0);
lean_inc_ref(x_377);
lean_dec_ref(x_375);
x_378 = lp_dasmodel_buildSID(x_376, x_377);
lean_dec_ref(x_377);
return x_378;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_generateSID(lean_object* x_1, uint8_t x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_generateSID___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_generateSID___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_generateSID(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___redArg(x_2, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__0(x_1, x_2, x_3, x_4);
lean_dec(x_2);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___redArg(x_1, x_2, x_3, x_4);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__2(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___redArg(x_1, x_2, x_3, x_4);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__3(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4___redArg(x_2, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__4(x_1, x_2, x_3, x_4);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17___redArg(x_2, x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00generateSID_spec__17(x_1, x_2, x_3, x_4);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___redArg(x_1, x_2, x_3, x_4);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00generateSID_spec__19(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_writeFile(lean_object* x_1, lean_object* x_2) {
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
LEAN_EXPORT lean_object* lp_dasmodel_writeFile___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_writeFile(x_1, x_2);
lean_dec_ref(x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_sidgenMain___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lp_dasmodel_commandoSong;
x_2 = lp_dasmodel_generateSID___redArg(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_sidgenMain___closed__3(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_sidgenMain___closed__0, &lp_dasmodel_sidgenMain___closed__0_once, _init_lp_dasmodel_sidgenMain___closed__0);
x_2 = lean_array_get_size(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_sidgenMain___closed__4(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_sidgenMain___closed__3, &lp_dasmodel_sidgenMain___closed__3_once, _init_lp_dasmodel_sidgenMain___closed__3);
x_2 = l_Nat_reprFast(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_sidgenMain___closed__5(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lean_obj_once(&lp_dasmodel_sidgenMain___closed__4, &lp_dasmodel_sidgenMain___closed__4_once, _init_lp_dasmodel_sidgenMain___closed__4);
x_2 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__2));
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_sidgenMain___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__6));
x_2 = lean_obj_once(&lp_dasmodel_sidgenMain___closed__5, &lp_dasmodel_sidgenMain___closed__5_once, _init_lp_dasmodel_sidgenMain___closed__5);
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_sidgenMain() {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_2 = lp_dasmodel_commandoSong;
x_3 = lean_obj_once(&lp_dasmodel_sidgenMain___closed__0, &lp_dasmodel_sidgenMain___closed__0_once, _init_lp_dasmodel_sidgenMain___closed__0);
x_4 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__1));
x_5 = lp_dasmodel_writeFile(x_4, x_3);
if (lean_obj_tag(x_5) == 0)
{
lean_object* x_6; lean_object* x_7; 
lean_dec_ref(x_5);
x_6 = lean_obj_once(&lp_dasmodel_sidgenMain___closed__7, &lp_dasmodel_sidgenMain___closed__7_once, _init_lp_dasmodel_sidgenMain___closed__7);
x_7 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_6);
if (lean_obj_tag(x_7) == 0)
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; 
lean_dec_ref(x_7);
x_8 = lean_ctor_get(x_2, 0);
lean_inc(x_8);
x_9 = lean_ctor_get(x_2, 1);
lean_inc(x_9);
x_10 = lean_ctor_get(x_2, 2);
lean_inc(x_10);
x_11 = lean_ctor_get(x_2, 3);
lean_inc(x_11);
x_12 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__8));
x_13 = l_List_lengthTR___redArg(x_8);
lean_dec(x_8);
x_14 = l_Nat_reprFast(x_13);
x_15 = lean_string_append(x_12, x_14);
lean_dec_ref(x_14);
x_16 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__9));
x_17 = lean_string_append(x_15, x_16);
x_18 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_17);
if (lean_obj_tag(x_18) == 0)
{
lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; 
lean_dec_ref(x_18);
x_19 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__10));
x_20 = l_List_lengthTR___redArg(x_9);
lean_dec(x_9);
x_21 = l_Nat_reprFast(x_20);
x_22 = lean_string_append(x_19, x_21);
lean_dec_ref(x_21);
x_23 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_22);
if (lean_obj_tag(x_23) == 0)
{
lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; 
lean_dec_ref(x_23);
x_24 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__11));
x_25 = l_List_lengthTR___redArg(x_11);
lean_dec(x_11);
x_26 = l_Nat_reprFast(x_25);
x_27 = lean_string_append(x_24, x_26);
lean_dec_ref(x_26);
x_28 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_27);
if (lean_obj_tag(x_28) == 0)
{
lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; 
lean_dec_ref(x_28);
x_29 = ((lean_object*)(lp_dasmodel_sidgenMain___closed__12));
x_30 = l_List_lengthTR___redArg(x_10);
lean_dec(x_10);
x_31 = l_Nat_reprFast(x_30);
x_32 = lean_string_append(x_29, x_31);
lean_dec_ref(x_31);
x_33 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_32);
return x_33;
}
else
{
lean_dec(x_10);
return x_28;
}
}
else
{
lean_dec(x_11);
lean_dec(x_10);
return x_23;
}
}
else
{
lean_dec(x_11);
lean_dec(x_10);
lean_dec(x_9);
return x_18;
}
}
else
{
return x_7;
}
}
else
{
return x_5;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_sidgenMain___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_sidgenMain();
return x_2;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_SID(uint8_t builtin);
lean_object* initialize_dasmodel_Asm6502(uint8_t builtin);
lean_object* initialize_dasmodel_PSIDFile(uint8_t builtin);
lean_object* initialize_dasmodel_Compile(uint8_t builtin);
lean_object* initialize_dasmodel_CommandoData(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_Codegen(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_SID(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_Asm6502(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_PSIDFile(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_Compile(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_CommandoData(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_dasmodel_SID__BASE = _init_lp_dasmodel_SID__BASE();
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
