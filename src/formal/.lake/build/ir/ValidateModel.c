// Lean compiler output
// Module: ValidateModel
// Imports: public import Init public import CPU6502
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
lean_object* lean_nat_sub(lean_object*, lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
uint32_t lean_string_utf8_get_fast(lean_object*, lean_object*);
lean_object* lean_string_utf8_next_fast(lean_object*, lean_object*);
lean_object* lean_nat_mul(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_uint32_to_nat(uint32_t);
lean_object* lean_nat_add(lean_object*, lean_object*);
uint8_t lean_uint32_dec_le(uint32_t, uint32_t);
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_string_utf8_byte_size(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_parseHex_x27(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_While_0__Lean_Loop_forIn_loop___at___00parseWrites_spec__0(lean_object*, lean_object*);
lean_object* l_List_lengthTR___redArg(lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
lean_object* l_List_get_x3fInternal___redArg(lean_object*, lean_object*);
uint8_t lean_uint8_of_nat(lean_object*);
lean_object* l_List_appendTR___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_While_0__Lean_Loop_forIn_loop___at___00parseWrites_spec__0___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_parseWrites___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ":"};
static const lean_object* lp_dasmodel_parseWrites___closed__0 = (const lean_object*)&lp_dasmodel_parseWrites___closed__0_value;
static const lean_ctor_object lp_dasmodel_parseWrites___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_parseWrites___closed__1 = (const lean_object*)&lp_dasmodel_parseWrites___closed__1_value;
lean_object* l_String_splitOnAux(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_parseWrites(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_parseWrites___boxed(lean_object*);
static const lean_string_object lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "V1_"};
static const lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__0 = (const lean_object*)&lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__0_value;
static lean_once_cell_t lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__1;
static const lean_string_object lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "|W:"};
static const lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__2 = (const lean_object*)&lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__2_value;
static const lean_string_object lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "{"};
static const lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__3 = (const lean_object*)&lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__3_value;
static lean_once_cell_t lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__4;
lean_object* lean_array_to_list(lean_object*);
lean_object* lean_array_push(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0(lean_object*, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
uint8_t lean_string_memcmp(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_string_length(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_parseLog___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "\n"};
static const lean_object* lp_dasmodel_parseLog___closed__0 = (const lean_object*)&lp_dasmodel_parseLog___closed__0_value;
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
static lean_once_cell_t lp_dasmodel_parseLog___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_parseLog___closed__1;
LEAN_EXPORT lean_object* lp_dasmodel_parseLog(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_parseLog___boxed(lean_object*);
lean_object* lean_nat_mod(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_twToRegVal(lean_object*);
lean_object* lean_get_stdout();
LEAN_EXPORT lean_object* lp_dasmodel_IO_print___at___00IO_println___at___00main_spec__0_spec__0(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_IO_print___at___00IO_println___at___00main_spec__0_spec__0___boxed(lean_object*, lean_object*);
lean_object* lean_string_push(lean_object*, uint32_t);
LEAN_EXPORT lean_object* lp_dasmodel_IO_println___at___00main_spec__0(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_IO_println___at___00main_spec__0___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 28, .m_capacity = 28, .m_length = 27, .m_data = "First divergence at write #"};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__0 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__0_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "  Lean: cycle="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__1 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__1_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = " reg="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__2 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__2_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = " val="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__3 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__3_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "  SPFP: cycle="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__4 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__4_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = "  Prev Lean: cycle="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__5 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__5_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = "  Prev SPFP: cycle="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__6 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__6_value;
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_Nat_reprFast(lean_object*);
lean_object* lean_string_append(lean_object*, lean_object*);
lean_object* lean_uint8_to_nat(uint8_t);
uint8_t lean_uint8_dec_eq(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___redArg___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg___boxed(lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 26, .m_capacity = 26, .m_length = 25, .m_data = "  Offset fails at write #"};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__0 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__0_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = ": Lean+"};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__1 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__1_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__2 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__2_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = " vs SPFP="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__3 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__3_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " (drift="};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__4 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__4_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ")"};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__5 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__5_value;
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_Int_toNat(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg___boxed(lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_main___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 57, .m_capacity = 57, .m_length = 56, .m_data = "../../data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid"};
static const lean_object* lp_dasmodel_main___closed__0 = (const lean_object*)&lp_dasmodel_main___closed__0_value;
static const lean_string_object lp_dasmodel_main___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 21, .m_capacity = 21, .m_length = 20, .m_data = "Running sidplayfp..."};
static const lean_object* lp_dasmodel_main___closed__1 = (const lean_object*)&lp_dasmodel_main___closed__1_value;
static const lean_ctor_object lp_dasmodel_main___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*0 + 8, .m_other = 0, .m_tag = 0}, .m_objs = {LEAN_SCALAR_PTR_LITERAL(1, 1, 1, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_main___closed__2 = (const lean_object*)&lp_dasmodel_main___closed__2_value;
static const lean_string_object lp_dasmodel_main___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = "../../tools/siddump"};
static const lean_object* lp_dasmodel_main___closed__3 = (const lean_object*)&lp_dasmodel_main___closed__3_value;
static const lean_string_object lp_dasmodel_main___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "--subtune"};
static const lean_object* lp_dasmodel_main___closed__4 = (const lean_object*)&lp_dasmodel_main___closed__4_value;
static const lean_string_object lp_dasmodel_main___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "1"};
static const lean_object* lp_dasmodel_main___closed__5 = (const lean_object*)&lp_dasmodel_main___closed__5_value;
static const lean_string_object lp_dasmodel_main___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "--duration"};
static const lean_object* lp_dasmodel_main___closed__6 = (const lean_object*)&lp_dasmodel_main___closed__6_value;
static lean_once_cell_t lp_dasmodel_main___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__7;
static const lean_string_object lp_dasmodel_main___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "--writelog"};
static const lean_object* lp_dasmodel_main___closed__8 = (const lean_object*)&lp_dasmodel_main___closed__8_value;
static lean_once_cell_t lp_dasmodel_main___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__9;
static lean_once_cell_t lp_dasmodel_main___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__10;
static lean_once_cell_t lp_dasmodel_main___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__11;
static lean_once_cell_t lp_dasmodel_main___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__12;
static lean_once_cell_t lp_dasmodel_main___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__13;
static lean_once_cell_t lp_dasmodel_main___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__14;
static lean_once_cell_t lp_dasmodel_main___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__15;
static const lean_string_object lp_dasmodel_main___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "  With offset: "};
static const lean_object* lp_dasmodel_main___closed__16 = (const lean_object*)&lp_dasmodel_main___closed__16_value;
static const lean_string_object lp_dasmodel_main___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 42, .m_capacity = 42, .m_length = 41, .m_data = "PERFECT MATCH with constant cycle offset!"};
static const lean_object* lp_dasmodel_main___closed__17 = (const lean_object*)&lp_dasmodel_main___closed__17_value;
static lean_once_cell_t lp_dasmodel_main___closed__18_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__18;
static lean_once_cell_t lp_dasmodel_main___closed__19_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__19;
static const lean_string_object lp_dasmodel_main___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "sidplayfp: "};
static const lean_object* lp_dasmodel_main___closed__20 = (const lean_object*)&lp_dasmodel_main___closed__20_value;
static const lean_string_object lp_dasmodel_main___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = " frames"};
static const lean_object* lp_dasmodel_main___closed__21 = (const lean_object*)&lp_dasmodel_main___closed__21_value;
static const lean_string_object lp_dasmodel_main___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 19, .m_capacity = 19, .m_length = 18, .m_data = "Failed to load SID"};
static const lean_object* lp_dasmodel_main___closed__22 = (const lean_object*)&lp_dasmodel_main___closed__22_value;
static const lean_string_object lp_dasmodel_main___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 18, .m_capacity = 18, .m_length = 17, .m_data = "Lean 6502: init=$"};
static const lean_object* lp_dasmodel_main___closed__23 = (const lean_object*)&lp_dasmodel_main___closed__23_value;
static const lean_string_object lp_dasmodel_main___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = " play=$"};
static const lean_object* lp_dasmodel_main___closed__24 = (const lean_object*)&lp_dasmodel_main___closed__24_value;
static lean_once_cell_t lp_dasmodel_main___closed__25_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__25;
static const lean_string_object lp_dasmodel_main___closed__26_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "Reg+Val match: "};
static const lean_object* lp_dasmodel_main___closed__26 = (const lean_object*)&lp_dasmodel_main___closed__26_value;
static const lean_string_object lp_dasmodel_main___closed__27_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "/"};
static const lean_object* lp_dasmodel_main___closed__27 = (const lean_object*)&lp_dasmodel_main___closed__27_value;
static lean_once_cell_t lp_dasmodel_main___closed__28_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__28;
static const lean_string_object lp_dasmodel_main___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 29, .m_capacity = 29, .m_length = 28, .m_data = "Full match (cycle+reg+val): "};
static const lean_object* lp_dasmodel_main___closed__29 = (const lean_object*)&lp_dasmodel_main___closed__29_value;
static const lean_string_object lp_dasmodel_main___closed__30_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 31, .m_capacity = 31, .m_length = 30, .m_data = "Trying constant cycle offset: "};
static const lean_object* lp_dasmodel_main___closed__30 = (const lean_object*)&lp_dasmodel_main___closed__30_value;
lean_object* lean_nat_to_int(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__31_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__31;
static const lean_string_object lp_dasmodel_main___closed__32_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "-"};
static const lean_object* lp_dasmodel_main___closed__32 = (const lean_object*)&lp_dasmodel_main___closed__32_value;
static const lean_string_object lp_dasmodel_main___closed__33_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "Lean: "};
static const lean_object* lp_dasmodel_main___closed__33 = (const lean_object*)&lp_dasmodel_main___closed__33_value;
static const lean_ctor_object lp_dasmodel_main___closed__34_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_main___closed__34 = (const lean_object*)&lp_dasmodel_main___closed__34_value;
static const lean_string_object lp_dasmodel_main___closed__35_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = "Total writes: Lean="};
static const lean_object* lp_dasmodel_main___closed__35 = (const lean_object*)&lp_dasmodel_main___closed__35_value;
static const lean_string_object lp_dasmodel_main___closed__36_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = " SPFP="};
static const lean_object* lp_dasmodel_main___closed__36 = (const lean_object*)&lp_dasmodel_main___closed__36_value;
lean_object* l_IO_FS_readBinFile(lean_object*);
lean_object* l_IO_Process_output(lean_object*, lean_object*);
lean_object* lp_dasmodel_loadSID(lean_object*);
lean_object* lean_uint16_to_nat(uint16_t);
lean_object* lp_dasmodel_CPU_write(lean_object*, uint16_t, uint8_t);
lean_object* lp_dasmodel_execInit(lean_object*, uint16_t, uint8_t);
lean_object* lean_int_sub(lean_object*, lean_object*);
uint8_t lean_int_dec_lt(lean_object*, lean_object*);
lean_object* lean_nat_abs(lean_object*);
lean_object* lean_string_append(lean_object*, lean_object*);
lean_object* lp_dasmodel_execFrames(lean_object*, uint16_t, lean_object*);
LEAN_EXPORT lean_object* _lean_main();
LEAN_EXPORT lean_object* lp_dasmodel_main___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_5 = lean_ctor_get(x_1, 1);
x_6 = lean_ctor_get(x_1, 2);
x_7 = lean_nat_sub(x_6, x_5);
x_8 = lean_nat_dec_eq(x_3, x_7);
lean_dec(x_7);
if (x_8 == 0)
{
uint32_t x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; uint8_t x_13; uint8_t x_23; uint8_t x_36; uint32_t x_47; uint8_t x_48; 
x_9 = lean_string_utf8_get_fast(x_2, x_3);
x_10 = lean_string_utf8_next_fast(x_2, x_3);
lean_dec(x_3);
x_11 = lean_unsigned_to_nat(16u);
x_12 = lean_nat_mul(x_4, x_11);
lean_dec(x_4);
x_47 = 48;
x_48 = lean_uint32_dec_le(x_47, x_9);
if (x_48 == 0)
{
x_36 = x_48;
goto block_46;
}
else
{
uint32_t x_49; uint8_t x_50; 
x_49 = 57;
x_50 = lean_uint32_dec_le(x_9, x_49);
x_36 = x_50;
goto block_46;
}
block_22:
{
if (x_13 == 0)
{
x_3 = x_10;
x_4 = x_12;
goto _start;
}
else
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; 
x_15 = lean_uint32_to_nat(x_9);
x_16 = lean_unsigned_to_nat(65u);
x_17 = lean_nat_sub(x_15, x_16);
lean_dec(x_15);
x_18 = lean_unsigned_to_nat(10u);
x_19 = lean_nat_add(x_17, x_18);
lean_dec(x_17);
x_20 = lean_nat_add(x_12, x_19);
lean_dec(x_19);
lean_dec(x_12);
x_3 = x_10;
x_4 = x_20;
goto _start;
}
}
block_35:
{
if (x_23 == 0)
{
uint32_t x_24; uint8_t x_25; 
x_24 = 65;
x_25 = lean_uint32_dec_le(x_24, x_9);
if (x_25 == 0)
{
x_13 = x_25;
goto block_22;
}
else
{
uint32_t x_26; uint8_t x_27; 
x_26 = 70;
x_27 = lean_uint32_dec_le(x_9, x_26);
x_13 = x_27;
goto block_22;
}
}
else
{
lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; 
x_28 = lean_uint32_to_nat(x_9);
x_29 = lean_unsigned_to_nat(97u);
x_30 = lean_nat_sub(x_28, x_29);
lean_dec(x_28);
x_31 = lean_unsigned_to_nat(10u);
x_32 = lean_nat_add(x_30, x_31);
lean_dec(x_30);
x_33 = lean_nat_add(x_12, x_32);
lean_dec(x_32);
lean_dec(x_12);
x_3 = x_10;
x_4 = x_33;
goto _start;
}
}
block_46:
{
if (x_36 == 0)
{
uint32_t x_37; uint8_t x_38; 
x_37 = 97;
x_38 = lean_uint32_dec_le(x_37, x_9);
if (x_38 == 0)
{
x_23 = x_38;
goto block_35;
}
else
{
uint32_t x_39; uint8_t x_40; 
x_39 = 102;
x_40 = lean_uint32_dec_le(x_9, x_39);
x_23 = x_40;
goto block_35;
}
}
else
{
lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; 
x_41 = lean_uint32_to_nat(x_9);
x_42 = lean_unsigned_to_nat(48u);
x_43 = lean_nat_sub(x_41, x_42);
lean_dec(x_41);
x_44 = lean_nat_add(x_12, x_43);
lean_dec(x_43);
lean_dec(x_12);
x_3 = x_10;
x_4 = x_44;
goto _start;
}
}
}
else
{
lean_dec(x_3);
return x_4;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_parseHex_x27(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_2 = lean_unsigned_to_nat(0u);
x_3 = lean_string_utf8_byte_size(x_1);
lean_inc_ref(x_1);
x_4 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_4, 0, x_1);
lean_ctor_set(x_4, 1, x_2);
lean_ctor_set(x_4, 2, x_3);
x_5 = lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___redArg(x_4, x_1, x_2, x_2);
lean_dec_ref(x_1);
lean_dec_ref(x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___redArg(x_1, x_2, x_5, x_6);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_dasmodel_WellFounded_opaqueFix_u2083___at___00parseHex_x27_spec__0(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_While_0__Lean_Loop_forIn_loop___at___00parseWrites_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; uint8_t x_10; 
x_10 = !lean_is_exclusive(x_2);
if (x_10 == 0)
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; uint8_t x_16; 
x_11 = lean_ctor_get(x_2, 0);
x_12 = lean_ctor_get(x_2, 1);
x_13 = lean_unsigned_to_nat(2u);
x_14 = lean_nat_add(x_11, x_13);
x_15 = l_List_lengthTR___redArg(x_1);
x_16 = lean_nat_dec_lt(x_14, x_15);
lean_dec(x_15);
if (x_16 == 0)
{
lean_dec(x_14);
return x_2;
}
else
{
lean_object* x_17; 
lean_free_object(x_2);
lean_inc(x_11);
x_17 = l_List_get_x3fInternal___redArg(x_1, x_11);
if (lean_obj_tag(x_17) == 1)
{
lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_18 = lean_ctor_get(x_17, 0);
lean_inc(x_18);
lean_dec_ref(x_17);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_11, x_19);
x_21 = l_List_get_x3fInternal___redArg(x_1, x_20);
if (lean_obj_tag(x_21) == 1)
{
lean_object* x_22; lean_object* x_23; 
x_22 = lean_ctor_get(x_21, 0);
lean_inc(x_22);
lean_dec_ref(x_21);
x_23 = l_List_get_x3fInternal___redArg(x_1, x_14);
if (lean_obj_tag(x_23) == 1)
{
lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; uint8_t x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; 
x_24 = lean_ctor_get(x_23, 0);
lean_inc(x_24);
lean_dec_ref(x_23);
x_25 = lean_box(0);
x_26 = lp_dasmodel_parseHex_x27(x_18);
x_27 = lp_dasmodel_parseHex_x27(x_22);
x_28 = lp_dasmodel_parseHex_x27(x_24);
x_29 = lean_uint8_of_nat(x_28);
lean_dec(x_28);
x_30 = lean_box(x_29);
x_31 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_31, 0, x_27);
lean_ctor_set(x_31, 1, x_30);
x_32 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_32, 0, x_26);
lean_ctor_set(x_32, 1, x_31);
x_33 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_33, 0, x_32);
lean_ctor_set(x_33, 1, x_25);
x_34 = l_List_appendTR___redArg(x_12, x_33);
x_3 = x_11;
x_4 = x_34;
goto block_9;
}
else
{
lean_dec(x_23);
lean_dec(x_22);
lean_dec(x_18);
x_3 = x_11;
x_4 = x_12;
goto block_9;
}
}
else
{
lean_dec(x_21);
lean_dec(x_18);
lean_dec(x_14);
x_3 = x_11;
x_4 = x_12;
goto block_9;
}
}
else
{
lean_dec(x_17);
lean_dec(x_14);
x_3 = x_11;
x_4 = x_12;
goto block_9;
}
}
}
else
{
lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; uint8_t x_40; 
x_35 = lean_ctor_get(x_2, 0);
x_36 = lean_ctor_get(x_2, 1);
lean_inc(x_36);
lean_inc(x_35);
lean_dec(x_2);
x_37 = lean_unsigned_to_nat(2u);
x_38 = lean_nat_add(x_35, x_37);
x_39 = l_List_lengthTR___redArg(x_1);
x_40 = lean_nat_dec_lt(x_38, x_39);
lean_dec(x_39);
if (x_40 == 0)
{
lean_object* x_41; 
lean_dec(x_38);
x_41 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_41, 0, x_35);
lean_ctor_set(x_41, 1, x_36);
return x_41;
}
else
{
lean_object* x_42; 
lean_inc(x_35);
x_42 = l_List_get_x3fInternal___redArg(x_1, x_35);
if (lean_obj_tag(x_42) == 1)
{
lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; 
x_43 = lean_ctor_get(x_42, 0);
lean_inc(x_43);
lean_dec_ref(x_42);
x_44 = lean_unsigned_to_nat(1u);
x_45 = lean_nat_add(x_35, x_44);
x_46 = l_List_get_x3fInternal___redArg(x_1, x_45);
if (lean_obj_tag(x_46) == 1)
{
lean_object* x_47; lean_object* x_48; 
x_47 = lean_ctor_get(x_46, 0);
lean_inc(x_47);
lean_dec_ref(x_46);
x_48 = l_List_get_x3fInternal___redArg(x_1, x_38);
if (lean_obj_tag(x_48) == 1)
{
lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; uint8_t x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; 
x_49 = lean_ctor_get(x_48, 0);
lean_inc(x_49);
lean_dec_ref(x_48);
x_50 = lean_box(0);
x_51 = lp_dasmodel_parseHex_x27(x_43);
x_52 = lp_dasmodel_parseHex_x27(x_47);
x_53 = lp_dasmodel_parseHex_x27(x_49);
x_54 = lean_uint8_of_nat(x_53);
lean_dec(x_53);
x_55 = lean_box(x_54);
x_56 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_56, 0, x_52);
lean_ctor_set(x_56, 1, x_55);
x_57 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_57, 0, x_51);
lean_ctor_set(x_57, 1, x_56);
x_58 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_58, 0, x_57);
lean_ctor_set(x_58, 1, x_50);
x_59 = l_List_appendTR___redArg(x_36, x_58);
x_3 = x_35;
x_4 = x_59;
goto block_9;
}
else
{
lean_dec(x_48);
lean_dec(x_47);
lean_dec(x_43);
x_3 = x_35;
x_4 = x_36;
goto block_9;
}
}
else
{
lean_dec(x_46);
lean_dec(x_43);
lean_dec(x_38);
x_3 = x_35;
x_4 = x_36;
goto block_9;
}
}
else
{
lean_dec(x_42);
lean_dec(x_38);
x_3 = x_35;
x_4 = x_36;
goto block_9;
}
}
}
block_9:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_5 = lean_unsigned_to_nat(3u);
x_6 = lean_nat_add(x_3, x_5);
lean_dec(x_3);
x_7 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_7, 0, x_6);
lean_ctor_set(x_7, 1, x_4);
x_2 = x_7;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_While_0__Lean_Loop_forIn_loop___at___00parseWrites_spec__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel___private_Init_While_0__Lean_Loop_forIn_loop___at___00parseWrites_spec__0(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_parseWrites(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_2 = ((lean_object*)(lp_dasmodel_parseWrites___closed__0));
x_3 = lean_unsigned_to_nat(0u);
x_4 = lean_box(0);
x_5 = l_String_splitOnAux(x_1, x_2, x_3, x_3, x_3, x_4);
x_6 = ((lean_object*)(lp_dasmodel_parseWrites___closed__1));
x_7 = lp_dasmodel___private_Init_While_0__Lean_Loop_forIn_loop___at___00parseWrites_spec__0(x_5, x_6);
lean_dec(x_5);
x_8 = lean_ctor_get(x_7, 1);
lean_inc(x_8);
lean_dec_ref(x_7);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_parseWrites___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_parseWrites(x_1);
lean_dec_ref(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__1(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = ((lean_object*)(lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__0));
x_2 = lean_string_utf8_byte_size(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__4(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = ((lean_object*)(lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__3));
x_2 = lean_string_utf8_byte_size(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_3; 
x_3 = lean_array_to_list(x_2);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_12; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; uint8_t x_28; 
x_4 = lean_ctor_get(x_1, 0);
x_5 = lean_ctor_get(x_1, 1);
x_22 = lean_unsigned_to_nat(1u);
x_23 = ((lean_object*)(lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__2));
x_24 = lean_unsigned_to_nat(0u);
x_25 = lean_box(0);
x_26 = l_String_splitOnAux(x_4, x_23, x_24, x_24, x_24, x_25);
x_27 = l_List_lengthTR___redArg(x_26);
x_28 = lean_nat_dec_lt(x_22, x_27);
lean_dec(x_27);
if (x_28 == 0)
{
lean_object* x_29; lean_object* x_30; uint8_t x_31; 
lean_dec(x_26);
x_29 = lean_unsigned_to_nat(10u);
x_30 = lean_string_length(x_4);
x_31 = lean_nat_dec_lt(x_29, x_30);
if (x_31 == 0)
{
x_12 = x_31;
goto block_21;
}
else
{
lean_object* x_32; lean_object* x_33; lean_object* x_34; uint8_t x_35; 
x_32 = ((lean_object*)(lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__3));
x_33 = lean_string_utf8_byte_size(x_4);
x_34 = lean_obj_once(&lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__4, &lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__4_once, _init_lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__4);
x_35 = lean_nat_dec_le(x_34, x_33);
if (x_35 == 0)
{
x_12 = x_31;
goto block_21;
}
else
{
uint8_t x_36; 
x_36 = lean_string_memcmp(x_4, x_32, x_24, x_24, x_34);
if (x_36 == 0)
{
x_12 = x_31;
goto block_21;
}
else
{
x_1 = x_5;
goto _start;
}
}
}
}
else
{
lean_object* x_38; 
x_38 = l_List_get_x3fInternal___redArg(x_26, x_22);
lean_dec(x_26);
if (lean_obj_tag(x_38) == 0)
{
x_6 = x_25;
goto block_9;
}
else
{
lean_object* x_39; lean_object* x_40; 
x_39 = lean_ctor_get(x_38, 0);
lean_inc(x_39);
lean_dec_ref(x_38);
x_40 = lp_dasmodel_parseWrites(x_39);
lean_dec(x_39);
x_6 = x_40;
goto block_9;
}
}
block_9:
{
lean_object* x_7; 
x_7 = lean_array_push(x_2, x_6);
x_1 = x_5;
x_2 = x_7;
goto _start;
}
block_11:
{
lean_object* x_10; 
x_10 = lean_box(0);
x_6 = x_10;
goto block_9;
}
block_21:
{
if (x_12 == 0)
{
x_1 = x_5;
goto _start;
}
else
{
lean_object* x_14; lean_object* x_15; lean_object* x_16; uint8_t x_17; 
x_14 = ((lean_object*)(lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__0));
x_15 = lean_string_utf8_byte_size(x_4);
x_16 = lean_obj_once(&lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__1, &lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__1_once, _init_lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___closed__1);
x_17 = lean_nat_dec_le(x_16, x_15);
if (x_17 == 0)
{
goto block_11;
}
else
{
lean_object* x_18; uint8_t x_19; 
x_18 = lean_unsigned_to_nat(0u);
x_19 = lean_string_memcmp(x_4, x_14, x_18, x_18, x_16);
if (x_19 == 0)
{
goto block_11;
}
else
{
x_1 = x_5;
goto _start;
}
}
}
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_parseLog___closed__1(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_parseLog(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_2 = ((lean_object*)(lp_dasmodel_parseLog___closed__0));
x_3 = lean_unsigned_to_nat(0u);
x_4 = lean_box(0);
x_5 = l_String_splitOnAux(x_1, x_2, x_3, x_3, x_3, x_4);
x_6 = lean_obj_once(&lp_dasmodel_parseLog___closed__1, &lp_dasmodel_parseLog___closed__1_once, _init_lp_dasmodel_parseLog___closed__1);
x_7 = lp_dasmodel_List_filterMapTR_go___at___00parseLog_spec__0(x_5, x_6);
lean_dec(x_5);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_parseLog___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_parseLog(x_1);
lean_dec_ref(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_twToRegVal(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_2 = lean_ctor_get(x_1, 1);
lean_inc_ref(x_2);
lean_dec_ref(x_1);
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
x_4 = lean_ctor_get(x_2, 1);
lean_inc(x_4);
if (lean_is_exclusive(x_2)) {
 lean_ctor_release(x_2, 0);
 lean_ctor_release(x_2, 1);
 x_5 = x_2;
} else {
 lean_dec_ref(x_2);
 x_5 = lean_box(0);
}
switch (lean_obj_tag(x_3)) {
case 0:
{
lean_object* x_13; lean_object* x_14; lean_object* x_15; 
x_13 = lean_ctor_get(x_3, 0);
lean_inc(x_13);
lean_dec_ref(x_3);
x_14 = lean_unsigned_to_nat(7u);
x_15 = lean_nat_mul(x_13, x_14);
lean_dec(x_13);
x_6 = x_15;
goto block_12;
}
case 1:
{
lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; 
x_16 = lean_ctor_get(x_3, 0);
lean_inc(x_16);
lean_dec_ref(x_3);
x_17 = lean_unsigned_to_nat(7u);
x_18 = lean_nat_mul(x_16, x_17);
lean_dec(x_16);
x_19 = lean_unsigned_to_nat(1u);
x_20 = lean_nat_add(x_18, x_19);
lean_dec(x_18);
x_6 = x_20;
goto block_12;
}
case 2:
{
lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_21 = lean_ctor_get(x_3, 0);
lean_inc(x_21);
lean_dec_ref(x_3);
x_22 = lean_unsigned_to_nat(7u);
x_23 = lean_nat_mul(x_21, x_22);
lean_dec(x_21);
x_24 = lean_unsigned_to_nat(2u);
x_25 = lean_nat_add(x_23, x_24);
lean_dec(x_23);
x_6 = x_25;
goto block_12;
}
case 3:
{
lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; 
x_26 = lean_ctor_get(x_3, 0);
lean_inc(x_26);
lean_dec_ref(x_3);
x_27 = lean_unsigned_to_nat(7u);
x_28 = lean_nat_mul(x_26, x_27);
lean_dec(x_26);
x_29 = lean_unsigned_to_nat(3u);
x_30 = lean_nat_add(x_28, x_29);
lean_dec(x_28);
x_6 = x_30;
goto block_12;
}
case 4:
{
lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; 
x_31 = lean_ctor_get(x_3, 0);
lean_inc(x_31);
lean_dec_ref(x_3);
x_32 = lean_unsigned_to_nat(7u);
x_33 = lean_nat_mul(x_31, x_32);
lean_dec(x_31);
x_34 = lean_unsigned_to_nat(4u);
x_35 = lean_nat_add(x_33, x_34);
lean_dec(x_33);
x_6 = x_35;
goto block_12;
}
case 5:
{
lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; 
x_36 = lean_ctor_get(x_3, 0);
lean_inc(x_36);
lean_dec_ref(x_3);
x_37 = lean_unsigned_to_nat(7u);
x_38 = lean_nat_mul(x_36, x_37);
lean_dec(x_36);
x_39 = lean_unsigned_to_nat(5u);
x_40 = lean_nat_add(x_38, x_39);
lean_dec(x_38);
x_6 = x_40;
goto block_12;
}
case 6:
{
lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; 
x_41 = lean_ctor_get(x_3, 0);
lean_inc(x_41);
lean_dec_ref(x_3);
x_42 = lean_unsigned_to_nat(7u);
x_43 = lean_nat_mul(x_41, x_42);
lean_dec(x_41);
x_44 = lean_unsigned_to_nat(6u);
x_45 = lean_nat_add(x_43, x_44);
lean_dec(x_43);
x_6 = x_45;
goto block_12;
}
case 7:
{
lean_object* x_46; 
x_46 = lean_unsigned_to_nat(21u);
x_6 = x_46;
goto block_12;
}
case 8:
{
lean_object* x_47; 
x_47 = lean_unsigned_to_nat(22u);
x_6 = x_47;
goto block_12;
}
case 9:
{
lean_object* x_48; 
x_48 = lean_unsigned_to_nat(23u);
x_6 = x_48;
goto block_12;
}
default: 
{
lean_object* x_49; 
x_49 = lean_unsigned_to_nat(24u);
x_6 = x_49;
goto block_12;
}
}
block_12:
{
lean_object* x_7; lean_object* x_8; uint8_t x_9; lean_object* x_10; lean_object* x_11; 
x_7 = lean_unsigned_to_nat(256u);
x_8 = lean_nat_mod(x_4, x_7);
lean_dec(x_4);
x_9 = lean_uint8_of_nat(x_8);
lean_dec(x_8);
x_10 = lean_box(x_9);
if (lean_is_scalar(x_5)) {
 x_11 = lean_alloc_ctor(0, 2, 0);
} else {
 x_11 = x_5;
}
lean_ctor_set(x_11, 0, x_6);
lean_ctor_set(x_11, 1, x_10);
return x_11;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_IO_print___at___00IO_println___at___00main_spec__0_spec__0(lean_object* x_1) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_3 = lean_get_stdout();
x_4 = lean_ctor_get(x_3, 4);
lean_inc_ref(x_4);
lean_dec_ref(x_3);
x_5 = lean_apply_2(x_4, x_1, lean_box(0));
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_IO_print___at___00IO_println___at___00main_spec__0_spec__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_IO_print___at___00IO_println___at___00main_spec__0_spec__0(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_IO_println___at___00main_spec__0(lean_object* x_1) {
_start:
{
uint32_t x_3; lean_object* x_4; lean_object* x_5; 
x_3 = 10;
x_4 = lean_string_push(x_1, x_3);
x_5 = lp_dasmodel_IO_print___at___00IO_println___at___00main_spec__0_spec__0(x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_IO_println___at___00main_spec__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_IO_println___at___00main_spec__0(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint8_t x_14; 
x_7 = lean_ctor_get(x_3, 1);
x_8 = lean_ctor_get(x_3, 2);
x_14 = lean_nat_dec_lt(x_5, x_7);
if (x_14 == 0)
{
lean_object* x_15; 
lean_dec(x_5);
x_15 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_15, 0, x_4);
return x_15;
}
else
{
lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_27; lean_object* x_28; uint8_t x_33; 
x_16 = lean_ctor_get(x_4, 1);
lean_inc(x_16);
x_17 = lean_ctor_get(x_4, 0);
lean_inc(x_17);
if (lean_is_exclusive(x_4)) {
 lean_ctor_release(x_4, 0);
 lean_ctor_release(x_4, 1);
 x_18 = x_4;
} else {
 lean_dec_ref(x_4);
 x_18 = lean_box(0);
}
x_19 = lean_ctor_get(x_16, 0);
lean_inc(x_19);
x_20 = lean_ctor_get(x_16, 1);
lean_inc(x_20);
if (lean_is_exclusive(x_16)) {
 lean_ctor_release(x_16, 0);
 lean_ctor_release(x_16, 1);
 x_21 = x_16;
} else {
 lean_dec_ref(x_16);
 x_21 = lean_box(0);
}
x_33 = lean_unbox(x_20);
if (x_33 == 0)
{
lean_object* x_34; 
lean_inc(x_5);
x_34 = l_List_get_x3fInternal___redArg(x_1, x_5);
if (lean_obj_tag(x_34) == 1)
{
lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; 
x_35 = lean_ctor_get(x_34, 0);
lean_inc(x_35);
lean_dec_ref(x_34);
x_36 = lean_ctor_get(x_35, 1);
lean_inc(x_36);
x_37 = lean_ctor_get(x_35, 0);
lean_inc(x_37);
lean_dec(x_35);
x_38 = lean_ctor_get(x_36, 0);
lean_inc(x_38);
x_39 = lean_ctor_get(x_36, 1);
lean_inc(x_39);
lean_dec(x_36);
lean_inc(x_5);
x_40 = l_List_get_x3fInternal___redArg(x_2, x_5);
if (lean_obj_tag(x_40) == 1)
{
lean_object* x_41; uint8_t x_42; 
lean_dec(x_21);
lean_dec(x_18);
x_41 = lean_ctor_get(x_40, 0);
lean_inc(x_41);
lean_dec_ref(x_40);
x_42 = !lean_is_exclusive(x_41);
if (x_42 == 0)
{
lean_object* x_43; uint8_t x_44; 
x_43 = lean_ctor_get(x_41, 1);
x_44 = !lean_is_exclusive(x_43);
if (x_44 == 0)
{
lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; uint8_t x_137; 
x_45 = lean_ctor_get(x_41, 0);
x_46 = lean_ctor_get(x_43, 0);
x_47 = lean_ctor_get(x_43, 1);
x_48 = lean_unsigned_to_nat(0u);
x_49 = lean_unsigned_to_nat(1u);
x_137 = lean_nat_dec_eq(x_37, x_45);
if (x_137 == 0)
{
lean_free_object(x_43);
lean_free_object(x_41);
lean_dec(x_20);
goto block_136;
}
else
{
uint8_t x_138; 
x_138 = lean_nat_dec_eq(x_38, x_46);
if (x_138 == 0)
{
lean_free_object(x_43);
lean_free_object(x_41);
lean_dec(x_20);
goto block_136;
}
else
{
uint8_t x_139; uint8_t x_140; uint8_t x_141; 
x_139 = lean_unbox(x_39);
x_140 = lean_unbox(x_47);
x_141 = lean_uint8_dec_eq(x_139, x_140);
if (x_141 == 0)
{
lean_free_object(x_43);
lean_free_object(x_41);
lean_dec(x_20);
goto block_136;
}
else
{
lean_object* x_142; 
lean_dec(x_47);
lean_dec(x_46);
lean_dec(x_45);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
x_142 = lean_nat_add(x_19, x_49);
lean_dec(x_19);
lean_ctor_set(x_43, 1, x_20);
lean_ctor_set(x_43, 0, x_142);
lean_ctor_set(x_41, 0, x_17);
x_9 = x_41;
x_10 = lean_box(0);
goto block_13;
}
}
}
block_136:
{
uint8_t x_50; 
x_50 = lean_nat_dec_eq(x_17, x_48);
if (x_50 == 0)
{
lean_dec(x_47);
lean_dec(x_46);
lean_dec(x_45);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
x_27 = x_17;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; 
lean_dec(x_17);
x_51 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__0));
lean_inc(x_5);
x_52 = l_Nat_reprFast(x_5);
x_53 = lean_string_append(x_51, x_52);
lean_dec_ref(x_52);
x_54 = ((lean_object*)(lp_dasmodel_parseWrites___closed__0));
x_55 = lean_string_append(x_53, x_54);
x_56 = lp_dasmodel_IO_println___at___00main_spec__0(x_55);
if (lean_obj_tag(x_56) == 0)
{
lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; uint8_t x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; 
lean_dec_ref(x_56);
x_57 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__1));
x_58 = l_Nat_reprFast(x_37);
x_59 = lean_string_append(x_57, x_58);
lean_dec_ref(x_58);
x_60 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__2));
x_61 = lean_string_append(x_59, x_60);
x_62 = l_Nat_reprFast(x_38);
x_63 = lean_string_append(x_61, x_62);
lean_dec_ref(x_62);
x_64 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__3));
x_65 = lean_string_append(x_63, x_64);
x_66 = lean_unbox(x_39);
lean_dec(x_39);
x_67 = lean_uint8_to_nat(x_66);
x_68 = l_Nat_reprFast(x_67);
x_69 = lean_string_append(x_65, x_68);
lean_dec_ref(x_68);
x_70 = lp_dasmodel_IO_println___at___00main_spec__0(x_69);
if (lean_obj_tag(x_70) == 0)
{
lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; uint8_t x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; 
lean_dec_ref(x_70);
x_71 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__4));
x_72 = l_Nat_reprFast(x_45);
x_73 = lean_string_append(x_71, x_72);
lean_dec_ref(x_72);
x_74 = lean_string_append(x_73, x_60);
x_75 = l_Nat_reprFast(x_46);
x_76 = lean_string_append(x_74, x_75);
lean_dec_ref(x_75);
x_77 = lean_string_append(x_76, x_64);
x_78 = lean_unbox(x_47);
lean_dec(x_47);
x_79 = lean_uint8_to_nat(x_78);
x_80 = l_Nat_reprFast(x_79);
x_81 = lean_string_append(x_77, x_80);
lean_dec_ref(x_80);
x_82 = lp_dasmodel_IO_println___at___00main_spec__0(x_81);
if (lean_obj_tag(x_82) == 0)
{
uint8_t x_83; 
lean_dec_ref(x_82);
x_83 = lean_nat_dec_lt(x_48, x_5);
if (x_83 == 0)
{
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_84; lean_object* x_85; 
x_84 = lean_nat_sub(x_5, x_49);
lean_inc(x_84);
x_85 = l_List_get_x3fInternal___redArg(x_1, x_84);
if (lean_obj_tag(x_85) == 1)
{
lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; 
x_86 = lean_ctor_get(x_85, 0);
lean_inc(x_86);
lean_dec_ref(x_85);
x_87 = lean_ctor_get(x_86, 1);
lean_inc(x_87);
x_88 = lean_ctor_get(x_86, 0);
lean_inc(x_88);
lean_dec(x_86);
x_89 = lean_ctor_get(x_87, 0);
lean_inc(x_89);
x_90 = lean_ctor_get(x_87, 1);
lean_inc(x_90);
lean_dec(x_87);
x_91 = l_List_get_x3fInternal___redArg(x_2, x_84);
if (lean_obj_tag(x_91) == 1)
{
lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; uint8_t x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; 
x_92 = lean_ctor_get(x_91, 0);
lean_inc(x_92);
lean_dec_ref(x_91);
x_93 = lean_ctor_get(x_92, 1);
lean_inc(x_93);
x_94 = lean_ctor_get(x_92, 0);
lean_inc(x_94);
lean_dec(x_92);
x_95 = lean_ctor_get(x_93, 0);
lean_inc(x_95);
x_96 = lean_ctor_get(x_93, 1);
lean_inc(x_96);
lean_dec(x_93);
x_97 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__5));
x_98 = l_Nat_reprFast(x_88);
x_99 = lean_string_append(x_97, x_98);
lean_dec_ref(x_98);
x_100 = lean_string_append(x_99, x_60);
x_101 = l_Nat_reprFast(x_89);
x_102 = lean_string_append(x_100, x_101);
lean_dec_ref(x_101);
x_103 = lean_string_append(x_102, x_64);
x_104 = lean_unbox(x_90);
lean_dec(x_90);
x_105 = lean_uint8_to_nat(x_104);
x_106 = l_Nat_reprFast(x_105);
x_107 = lean_string_append(x_103, x_106);
lean_dec_ref(x_106);
x_108 = lp_dasmodel_IO_println___at___00main_spec__0(x_107);
if (lean_obj_tag(x_108) == 0)
{
lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; uint8_t x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; 
lean_dec_ref(x_108);
x_109 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__6));
x_110 = l_Nat_reprFast(x_94);
x_111 = lean_string_append(x_109, x_110);
lean_dec_ref(x_110);
x_112 = lean_string_append(x_111, x_60);
x_113 = l_Nat_reprFast(x_95);
x_114 = lean_string_append(x_112, x_113);
lean_dec_ref(x_113);
x_115 = lean_string_append(x_114, x_64);
x_116 = lean_unbox(x_96);
lean_dec(x_96);
x_117 = lean_uint8_to_nat(x_116);
x_118 = l_Nat_reprFast(x_117);
x_119 = lean_string_append(x_115, x_118);
lean_dec_ref(x_118);
x_120 = lp_dasmodel_IO_println___at___00main_spec__0(x_119);
if (lean_obj_tag(x_120) == 0)
{
lean_dec_ref(x_120);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
else
{
uint8_t x_121; 
lean_dec(x_19);
lean_dec(x_5);
x_121 = !lean_is_exclusive(x_120);
if (x_121 == 0)
{
return x_120;
}
else
{
lean_object* x_122; lean_object* x_123; 
x_122 = lean_ctor_get(x_120, 0);
lean_inc(x_122);
lean_dec(x_120);
x_123 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_123, 0, x_122);
return x_123;
}
}
}
else
{
uint8_t x_124; 
lean_dec(x_96);
lean_dec(x_95);
lean_dec(x_94);
lean_dec(x_19);
lean_dec(x_5);
x_124 = !lean_is_exclusive(x_108);
if (x_124 == 0)
{
return x_108;
}
else
{
lean_object* x_125; lean_object* x_126; 
x_125 = lean_ctor_get(x_108, 0);
lean_inc(x_125);
lean_dec(x_108);
x_126 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_126, 0, x_125);
return x_126;
}
}
}
else
{
lean_dec(x_91);
lean_dec(x_90);
lean_dec(x_89);
lean_dec(x_88);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
}
else
{
lean_dec(x_85);
lean_dec(x_84);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
}
}
else
{
uint8_t x_127; 
lean_dec(x_19);
lean_dec(x_5);
x_127 = !lean_is_exclusive(x_82);
if (x_127 == 0)
{
return x_82;
}
else
{
lean_object* x_128; lean_object* x_129; 
x_128 = lean_ctor_get(x_82, 0);
lean_inc(x_128);
lean_dec(x_82);
x_129 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_129, 0, x_128);
return x_129;
}
}
}
else
{
uint8_t x_130; 
lean_dec(x_47);
lean_dec(x_46);
lean_dec(x_45);
lean_dec(x_19);
lean_dec(x_5);
x_130 = !lean_is_exclusive(x_70);
if (x_130 == 0)
{
return x_70;
}
else
{
lean_object* x_131; lean_object* x_132; 
x_131 = lean_ctor_get(x_70, 0);
lean_inc(x_131);
lean_dec(x_70);
x_132 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_132, 0, x_131);
return x_132;
}
}
}
else
{
uint8_t x_133; 
lean_dec(x_47);
lean_dec(x_46);
lean_dec(x_45);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
lean_dec(x_19);
lean_dec(x_5);
x_133 = !lean_is_exclusive(x_56);
if (x_133 == 0)
{
return x_56;
}
else
{
lean_object* x_134; lean_object* x_135; 
x_134 = lean_ctor_get(x_56, 0);
lean_inc(x_134);
lean_dec(x_56);
x_135 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_135, 0, x_134);
return x_135;
}
}
}
}
}
else
{
lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; uint8_t x_235; 
x_143 = lean_ctor_get(x_41, 0);
x_144 = lean_ctor_get(x_43, 0);
x_145 = lean_ctor_get(x_43, 1);
lean_inc(x_145);
lean_inc(x_144);
lean_dec(x_43);
x_146 = lean_unsigned_to_nat(0u);
x_147 = lean_unsigned_to_nat(1u);
x_235 = lean_nat_dec_eq(x_37, x_143);
if (x_235 == 0)
{
lean_free_object(x_41);
lean_dec(x_20);
goto block_234;
}
else
{
uint8_t x_236; 
x_236 = lean_nat_dec_eq(x_38, x_144);
if (x_236 == 0)
{
lean_free_object(x_41);
lean_dec(x_20);
goto block_234;
}
else
{
uint8_t x_237; uint8_t x_238; uint8_t x_239; 
x_237 = lean_unbox(x_39);
x_238 = lean_unbox(x_145);
x_239 = lean_uint8_dec_eq(x_237, x_238);
if (x_239 == 0)
{
lean_free_object(x_41);
lean_dec(x_20);
goto block_234;
}
else
{
lean_object* x_240; lean_object* x_241; 
lean_dec(x_145);
lean_dec(x_144);
lean_dec(x_143);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
x_240 = lean_nat_add(x_19, x_147);
lean_dec(x_19);
x_241 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_241, 0, x_240);
lean_ctor_set(x_241, 1, x_20);
lean_ctor_set(x_41, 1, x_241);
lean_ctor_set(x_41, 0, x_17);
x_9 = x_41;
x_10 = lean_box(0);
goto block_13;
}
}
}
block_234:
{
uint8_t x_148; 
x_148 = lean_nat_dec_eq(x_17, x_146);
if (x_148 == 0)
{
lean_dec(x_145);
lean_dec(x_144);
lean_dec(x_143);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
x_27 = x_17;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_149; lean_object* x_150; lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_154; 
lean_dec(x_17);
x_149 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__0));
lean_inc(x_5);
x_150 = l_Nat_reprFast(x_5);
x_151 = lean_string_append(x_149, x_150);
lean_dec_ref(x_150);
x_152 = ((lean_object*)(lp_dasmodel_parseWrites___closed__0));
x_153 = lean_string_append(x_151, x_152);
x_154 = lp_dasmodel_IO_println___at___00main_spec__0(x_153);
if (lean_obj_tag(x_154) == 0)
{
lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; uint8_t x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; 
lean_dec_ref(x_154);
x_155 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__1));
x_156 = l_Nat_reprFast(x_37);
x_157 = lean_string_append(x_155, x_156);
lean_dec_ref(x_156);
x_158 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__2));
x_159 = lean_string_append(x_157, x_158);
x_160 = l_Nat_reprFast(x_38);
x_161 = lean_string_append(x_159, x_160);
lean_dec_ref(x_160);
x_162 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__3));
x_163 = lean_string_append(x_161, x_162);
x_164 = lean_unbox(x_39);
lean_dec(x_39);
x_165 = lean_uint8_to_nat(x_164);
x_166 = l_Nat_reprFast(x_165);
x_167 = lean_string_append(x_163, x_166);
lean_dec_ref(x_166);
x_168 = lp_dasmodel_IO_println___at___00main_spec__0(x_167);
if (lean_obj_tag(x_168) == 0)
{
lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; uint8_t x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; 
lean_dec_ref(x_168);
x_169 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__4));
x_170 = l_Nat_reprFast(x_143);
x_171 = lean_string_append(x_169, x_170);
lean_dec_ref(x_170);
x_172 = lean_string_append(x_171, x_158);
x_173 = l_Nat_reprFast(x_144);
x_174 = lean_string_append(x_172, x_173);
lean_dec_ref(x_173);
x_175 = lean_string_append(x_174, x_162);
x_176 = lean_unbox(x_145);
lean_dec(x_145);
x_177 = lean_uint8_to_nat(x_176);
x_178 = l_Nat_reprFast(x_177);
x_179 = lean_string_append(x_175, x_178);
lean_dec_ref(x_178);
x_180 = lp_dasmodel_IO_println___at___00main_spec__0(x_179);
if (lean_obj_tag(x_180) == 0)
{
uint8_t x_181; 
lean_dec_ref(x_180);
x_181 = lean_nat_dec_lt(x_146, x_5);
if (x_181 == 0)
{
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_182; lean_object* x_183; 
x_182 = lean_nat_sub(x_5, x_147);
lean_inc(x_182);
x_183 = l_List_get_x3fInternal___redArg(x_1, x_182);
if (lean_obj_tag(x_183) == 1)
{
lean_object* x_184; lean_object* x_185; lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; 
x_184 = lean_ctor_get(x_183, 0);
lean_inc(x_184);
lean_dec_ref(x_183);
x_185 = lean_ctor_get(x_184, 1);
lean_inc(x_185);
x_186 = lean_ctor_get(x_184, 0);
lean_inc(x_186);
lean_dec(x_184);
x_187 = lean_ctor_get(x_185, 0);
lean_inc(x_187);
x_188 = lean_ctor_get(x_185, 1);
lean_inc(x_188);
lean_dec(x_185);
x_189 = l_List_get_x3fInternal___redArg(x_2, x_182);
if (lean_obj_tag(x_189) == 1)
{
lean_object* x_190; lean_object* x_191; lean_object* x_192; lean_object* x_193; lean_object* x_194; lean_object* x_195; lean_object* x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; uint8_t x_202; lean_object* x_203; lean_object* x_204; lean_object* x_205; lean_object* x_206; 
x_190 = lean_ctor_get(x_189, 0);
lean_inc(x_190);
lean_dec_ref(x_189);
x_191 = lean_ctor_get(x_190, 1);
lean_inc(x_191);
x_192 = lean_ctor_get(x_190, 0);
lean_inc(x_192);
lean_dec(x_190);
x_193 = lean_ctor_get(x_191, 0);
lean_inc(x_193);
x_194 = lean_ctor_get(x_191, 1);
lean_inc(x_194);
lean_dec(x_191);
x_195 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__5));
x_196 = l_Nat_reprFast(x_186);
x_197 = lean_string_append(x_195, x_196);
lean_dec_ref(x_196);
x_198 = lean_string_append(x_197, x_158);
x_199 = l_Nat_reprFast(x_187);
x_200 = lean_string_append(x_198, x_199);
lean_dec_ref(x_199);
x_201 = lean_string_append(x_200, x_162);
x_202 = lean_unbox(x_188);
lean_dec(x_188);
x_203 = lean_uint8_to_nat(x_202);
x_204 = l_Nat_reprFast(x_203);
x_205 = lean_string_append(x_201, x_204);
lean_dec_ref(x_204);
x_206 = lp_dasmodel_IO_println___at___00main_spec__0(x_205);
if (lean_obj_tag(x_206) == 0)
{
lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; uint8_t x_214; lean_object* x_215; lean_object* x_216; lean_object* x_217; lean_object* x_218; 
lean_dec_ref(x_206);
x_207 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__6));
x_208 = l_Nat_reprFast(x_192);
x_209 = lean_string_append(x_207, x_208);
lean_dec_ref(x_208);
x_210 = lean_string_append(x_209, x_158);
x_211 = l_Nat_reprFast(x_193);
x_212 = lean_string_append(x_210, x_211);
lean_dec_ref(x_211);
x_213 = lean_string_append(x_212, x_162);
x_214 = lean_unbox(x_194);
lean_dec(x_194);
x_215 = lean_uint8_to_nat(x_214);
x_216 = l_Nat_reprFast(x_215);
x_217 = lean_string_append(x_213, x_216);
lean_dec_ref(x_216);
x_218 = lp_dasmodel_IO_println___at___00main_spec__0(x_217);
if (lean_obj_tag(x_218) == 0)
{
lean_dec_ref(x_218);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_219; lean_object* x_220; lean_object* x_221; 
lean_dec(x_19);
lean_dec(x_5);
x_219 = lean_ctor_get(x_218, 0);
lean_inc(x_219);
if (lean_is_exclusive(x_218)) {
 lean_ctor_release(x_218, 0);
 x_220 = x_218;
} else {
 lean_dec_ref(x_218);
 x_220 = lean_box(0);
}
if (lean_is_scalar(x_220)) {
 x_221 = lean_alloc_ctor(1, 1, 0);
} else {
 x_221 = x_220;
}
lean_ctor_set(x_221, 0, x_219);
return x_221;
}
}
else
{
lean_object* x_222; lean_object* x_223; lean_object* x_224; 
lean_dec(x_194);
lean_dec(x_193);
lean_dec(x_192);
lean_dec(x_19);
lean_dec(x_5);
x_222 = lean_ctor_get(x_206, 0);
lean_inc(x_222);
if (lean_is_exclusive(x_206)) {
 lean_ctor_release(x_206, 0);
 x_223 = x_206;
} else {
 lean_dec_ref(x_206);
 x_223 = lean_box(0);
}
if (lean_is_scalar(x_223)) {
 x_224 = lean_alloc_ctor(1, 1, 0);
} else {
 x_224 = x_223;
}
lean_ctor_set(x_224, 0, x_222);
return x_224;
}
}
else
{
lean_dec(x_189);
lean_dec(x_188);
lean_dec(x_187);
lean_dec(x_186);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
}
else
{
lean_dec(x_183);
lean_dec(x_182);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
}
}
else
{
lean_object* x_225; lean_object* x_226; lean_object* x_227; 
lean_dec(x_19);
lean_dec(x_5);
x_225 = lean_ctor_get(x_180, 0);
lean_inc(x_225);
if (lean_is_exclusive(x_180)) {
 lean_ctor_release(x_180, 0);
 x_226 = x_180;
} else {
 lean_dec_ref(x_180);
 x_226 = lean_box(0);
}
if (lean_is_scalar(x_226)) {
 x_227 = lean_alloc_ctor(1, 1, 0);
} else {
 x_227 = x_226;
}
lean_ctor_set(x_227, 0, x_225);
return x_227;
}
}
else
{
lean_object* x_228; lean_object* x_229; lean_object* x_230; 
lean_dec(x_145);
lean_dec(x_144);
lean_dec(x_143);
lean_dec(x_19);
lean_dec(x_5);
x_228 = lean_ctor_get(x_168, 0);
lean_inc(x_228);
if (lean_is_exclusive(x_168)) {
 lean_ctor_release(x_168, 0);
 x_229 = x_168;
} else {
 lean_dec_ref(x_168);
 x_229 = lean_box(0);
}
if (lean_is_scalar(x_229)) {
 x_230 = lean_alloc_ctor(1, 1, 0);
} else {
 x_230 = x_229;
}
lean_ctor_set(x_230, 0, x_228);
return x_230;
}
}
else
{
lean_object* x_231; lean_object* x_232; lean_object* x_233; 
lean_dec(x_145);
lean_dec(x_144);
lean_dec(x_143);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
lean_dec(x_19);
lean_dec(x_5);
x_231 = lean_ctor_get(x_154, 0);
lean_inc(x_231);
if (lean_is_exclusive(x_154)) {
 lean_ctor_release(x_154, 0);
 x_232 = x_154;
} else {
 lean_dec_ref(x_154);
 x_232 = lean_box(0);
}
if (lean_is_scalar(x_232)) {
 x_233 = lean_alloc_ctor(1, 1, 0);
} else {
 x_233 = x_232;
}
lean_ctor_set(x_233, 0, x_231);
return x_233;
}
}
}
}
}
else
{
lean_object* x_242; lean_object* x_243; lean_object* x_244; lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; uint8_t x_336; 
x_242 = lean_ctor_get(x_41, 1);
x_243 = lean_ctor_get(x_41, 0);
lean_inc(x_242);
lean_inc(x_243);
lean_dec(x_41);
x_244 = lean_ctor_get(x_242, 0);
lean_inc(x_244);
x_245 = lean_ctor_get(x_242, 1);
lean_inc(x_245);
if (lean_is_exclusive(x_242)) {
 lean_ctor_release(x_242, 0);
 lean_ctor_release(x_242, 1);
 x_246 = x_242;
} else {
 lean_dec_ref(x_242);
 x_246 = lean_box(0);
}
x_247 = lean_unsigned_to_nat(0u);
x_248 = lean_unsigned_to_nat(1u);
x_336 = lean_nat_dec_eq(x_37, x_243);
if (x_336 == 0)
{
lean_dec(x_246);
lean_dec(x_20);
goto block_335;
}
else
{
uint8_t x_337; 
x_337 = lean_nat_dec_eq(x_38, x_244);
if (x_337 == 0)
{
lean_dec(x_246);
lean_dec(x_20);
goto block_335;
}
else
{
uint8_t x_338; uint8_t x_339; uint8_t x_340; 
x_338 = lean_unbox(x_39);
x_339 = lean_unbox(x_245);
x_340 = lean_uint8_dec_eq(x_338, x_339);
if (x_340 == 0)
{
lean_dec(x_246);
lean_dec(x_20);
goto block_335;
}
else
{
lean_object* x_341; lean_object* x_342; lean_object* x_343; 
lean_dec(x_245);
lean_dec(x_244);
lean_dec(x_243);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
x_341 = lean_nat_add(x_19, x_248);
lean_dec(x_19);
if (lean_is_scalar(x_246)) {
 x_342 = lean_alloc_ctor(0, 2, 0);
} else {
 x_342 = x_246;
}
lean_ctor_set(x_342, 0, x_341);
lean_ctor_set(x_342, 1, x_20);
x_343 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_343, 0, x_17);
lean_ctor_set(x_343, 1, x_342);
x_9 = x_343;
x_10 = lean_box(0);
goto block_13;
}
}
}
block_335:
{
uint8_t x_249; 
x_249 = lean_nat_dec_eq(x_17, x_247);
if (x_249 == 0)
{
lean_dec(x_245);
lean_dec(x_244);
lean_dec(x_243);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
x_27 = x_17;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_250; lean_object* x_251; lean_object* x_252; lean_object* x_253; lean_object* x_254; lean_object* x_255; 
lean_dec(x_17);
x_250 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__0));
lean_inc(x_5);
x_251 = l_Nat_reprFast(x_5);
x_252 = lean_string_append(x_250, x_251);
lean_dec_ref(x_251);
x_253 = ((lean_object*)(lp_dasmodel_parseWrites___closed__0));
x_254 = lean_string_append(x_252, x_253);
x_255 = lp_dasmodel_IO_println___at___00main_spec__0(x_254);
if (lean_obj_tag(x_255) == 0)
{
lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; uint8_t x_265; lean_object* x_266; lean_object* x_267; lean_object* x_268; lean_object* x_269; 
lean_dec_ref(x_255);
x_256 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__1));
x_257 = l_Nat_reprFast(x_37);
x_258 = lean_string_append(x_256, x_257);
lean_dec_ref(x_257);
x_259 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__2));
x_260 = lean_string_append(x_258, x_259);
x_261 = l_Nat_reprFast(x_38);
x_262 = lean_string_append(x_260, x_261);
lean_dec_ref(x_261);
x_263 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__3));
x_264 = lean_string_append(x_262, x_263);
x_265 = lean_unbox(x_39);
lean_dec(x_39);
x_266 = lean_uint8_to_nat(x_265);
x_267 = l_Nat_reprFast(x_266);
x_268 = lean_string_append(x_264, x_267);
lean_dec_ref(x_267);
x_269 = lp_dasmodel_IO_println___at___00main_spec__0(x_268);
if (lean_obj_tag(x_269) == 0)
{
lean_object* x_270; lean_object* x_271; lean_object* x_272; lean_object* x_273; lean_object* x_274; lean_object* x_275; lean_object* x_276; uint8_t x_277; lean_object* x_278; lean_object* x_279; lean_object* x_280; lean_object* x_281; 
lean_dec_ref(x_269);
x_270 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__4));
x_271 = l_Nat_reprFast(x_243);
x_272 = lean_string_append(x_270, x_271);
lean_dec_ref(x_271);
x_273 = lean_string_append(x_272, x_259);
x_274 = l_Nat_reprFast(x_244);
x_275 = lean_string_append(x_273, x_274);
lean_dec_ref(x_274);
x_276 = lean_string_append(x_275, x_263);
x_277 = lean_unbox(x_245);
lean_dec(x_245);
x_278 = lean_uint8_to_nat(x_277);
x_279 = l_Nat_reprFast(x_278);
x_280 = lean_string_append(x_276, x_279);
lean_dec_ref(x_279);
x_281 = lp_dasmodel_IO_println___at___00main_spec__0(x_280);
if (lean_obj_tag(x_281) == 0)
{
uint8_t x_282; 
lean_dec_ref(x_281);
x_282 = lean_nat_dec_lt(x_247, x_5);
if (x_282 == 0)
{
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_283; lean_object* x_284; 
x_283 = lean_nat_sub(x_5, x_248);
lean_inc(x_283);
x_284 = l_List_get_x3fInternal___redArg(x_1, x_283);
if (lean_obj_tag(x_284) == 1)
{
lean_object* x_285; lean_object* x_286; lean_object* x_287; lean_object* x_288; lean_object* x_289; lean_object* x_290; 
x_285 = lean_ctor_get(x_284, 0);
lean_inc(x_285);
lean_dec_ref(x_284);
x_286 = lean_ctor_get(x_285, 1);
lean_inc(x_286);
x_287 = lean_ctor_get(x_285, 0);
lean_inc(x_287);
lean_dec(x_285);
x_288 = lean_ctor_get(x_286, 0);
lean_inc(x_288);
x_289 = lean_ctor_get(x_286, 1);
lean_inc(x_289);
lean_dec(x_286);
x_290 = l_List_get_x3fInternal___redArg(x_2, x_283);
if (lean_obj_tag(x_290) == 1)
{
lean_object* x_291; lean_object* x_292; lean_object* x_293; lean_object* x_294; lean_object* x_295; lean_object* x_296; lean_object* x_297; lean_object* x_298; lean_object* x_299; lean_object* x_300; lean_object* x_301; lean_object* x_302; uint8_t x_303; lean_object* x_304; lean_object* x_305; lean_object* x_306; lean_object* x_307; 
x_291 = lean_ctor_get(x_290, 0);
lean_inc(x_291);
lean_dec_ref(x_290);
x_292 = lean_ctor_get(x_291, 1);
lean_inc(x_292);
x_293 = lean_ctor_get(x_291, 0);
lean_inc(x_293);
lean_dec(x_291);
x_294 = lean_ctor_get(x_292, 0);
lean_inc(x_294);
x_295 = lean_ctor_get(x_292, 1);
lean_inc(x_295);
lean_dec(x_292);
x_296 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__5));
x_297 = l_Nat_reprFast(x_287);
x_298 = lean_string_append(x_296, x_297);
lean_dec_ref(x_297);
x_299 = lean_string_append(x_298, x_259);
x_300 = l_Nat_reprFast(x_288);
x_301 = lean_string_append(x_299, x_300);
lean_dec_ref(x_300);
x_302 = lean_string_append(x_301, x_263);
x_303 = lean_unbox(x_289);
lean_dec(x_289);
x_304 = lean_uint8_to_nat(x_303);
x_305 = l_Nat_reprFast(x_304);
x_306 = lean_string_append(x_302, x_305);
lean_dec_ref(x_305);
x_307 = lp_dasmodel_IO_println___at___00main_spec__0(x_306);
if (lean_obj_tag(x_307) == 0)
{
lean_object* x_308; lean_object* x_309; lean_object* x_310; lean_object* x_311; lean_object* x_312; lean_object* x_313; lean_object* x_314; uint8_t x_315; lean_object* x_316; lean_object* x_317; lean_object* x_318; lean_object* x_319; 
lean_dec_ref(x_307);
x_308 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___closed__6));
x_309 = l_Nat_reprFast(x_293);
x_310 = lean_string_append(x_308, x_309);
lean_dec_ref(x_309);
x_311 = lean_string_append(x_310, x_259);
x_312 = l_Nat_reprFast(x_294);
x_313 = lean_string_append(x_311, x_312);
lean_dec_ref(x_312);
x_314 = lean_string_append(x_313, x_263);
x_315 = lean_unbox(x_295);
lean_dec(x_295);
x_316 = lean_uint8_to_nat(x_315);
x_317 = l_Nat_reprFast(x_316);
x_318 = lean_string_append(x_314, x_317);
lean_dec_ref(x_317);
x_319 = lp_dasmodel_IO_println___at___00main_spec__0(x_318);
if (lean_obj_tag(x_319) == 0)
{
lean_dec_ref(x_319);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
else
{
lean_object* x_320; lean_object* x_321; lean_object* x_322; 
lean_dec(x_19);
lean_dec(x_5);
x_320 = lean_ctor_get(x_319, 0);
lean_inc(x_320);
if (lean_is_exclusive(x_319)) {
 lean_ctor_release(x_319, 0);
 x_321 = x_319;
} else {
 lean_dec_ref(x_319);
 x_321 = lean_box(0);
}
if (lean_is_scalar(x_321)) {
 x_322 = lean_alloc_ctor(1, 1, 0);
} else {
 x_322 = x_321;
}
lean_ctor_set(x_322, 0, x_320);
return x_322;
}
}
else
{
lean_object* x_323; lean_object* x_324; lean_object* x_325; 
lean_dec(x_295);
lean_dec(x_294);
lean_dec(x_293);
lean_dec(x_19);
lean_dec(x_5);
x_323 = lean_ctor_get(x_307, 0);
lean_inc(x_323);
if (lean_is_exclusive(x_307)) {
 lean_ctor_release(x_307, 0);
 x_324 = x_307;
} else {
 lean_dec_ref(x_307);
 x_324 = lean_box(0);
}
if (lean_is_scalar(x_324)) {
 x_325 = lean_alloc_ctor(1, 1, 0);
} else {
 x_325 = x_324;
}
lean_ctor_set(x_325, 0, x_323);
return x_325;
}
}
else
{
lean_dec(x_290);
lean_dec(x_289);
lean_dec(x_288);
lean_dec(x_287);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
}
else
{
lean_dec(x_284);
lean_dec(x_283);
lean_inc(x_5);
x_27 = x_5;
x_28 = lean_box(0);
goto block_32;
}
}
}
else
{
lean_object* x_326; lean_object* x_327; lean_object* x_328; 
lean_dec(x_19);
lean_dec(x_5);
x_326 = lean_ctor_get(x_281, 0);
lean_inc(x_326);
if (lean_is_exclusive(x_281)) {
 lean_ctor_release(x_281, 0);
 x_327 = x_281;
} else {
 lean_dec_ref(x_281);
 x_327 = lean_box(0);
}
if (lean_is_scalar(x_327)) {
 x_328 = lean_alloc_ctor(1, 1, 0);
} else {
 x_328 = x_327;
}
lean_ctor_set(x_328, 0, x_326);
return x_328;
}
}
else
{
lean_object* x_329; lean_object* x_330; lean_object* x_331; 
lean_dec(x_245);
lean_dec(x_244);
lean_dec(x_243);
lean_dec(x_19);
lean_dec(x_5);
x_329 = lean_ctor_get(x_269, 0);
lean_inc(x_329);
if (lean_is_exclusive(x_269)) {
 lean_ctor_release(x_269, 0);
 x_330 = x_269;
} else {
 lean_dec_ref(x_269);
 x_330 = lean_box(0);
}
if (lean_is_scalar(x_330)) {
 x_331 = lean_alloc_ctor(1, 1, 0);
} else {
 x_331 = x_330;
}
lean_ctor_set(x_331, 0, x_329);
return x_331;
}
}
else
{
lean_object* x_332; lean_object* x_333; lean_object* x_334; 
lean_dec(x_245);
lean_dec(x_244);
lean_dec(x_243);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
lean_dec(x_19);
lean_dec(x_5);
x_332 = lean_ctor_get(x_255, 0);
lean_inc(x_332);
if (lean_is_exclusive(x_255)) {
 lean_ctor_release(x_255, 0);
 x_333 = x_255;
} else {
 lean_dec_ref(x_255);
 x_333 = lean_box(0);
}
if (lean_is_scalar(x_333)) {
 x_334 = lean_alloc_ctor(1, 1, 0);
} else {
 x_334 = x_333;
}
lean_ctor_set(x_334, 0, x_332);
return x_334;
}
}
}
}
}
else
{
lean_dec(x_40);
lean_dec(x_39);
lean_dec(x_38);
lean_dec(x_37);
lean_dec(x_20);
x_22 = lean_box(0);
goto block_26;
}
}
else
{
lean_dec(x_34);
lean_dec(x_20);
x_22 = lean_box(0);
goto block_26;
}
}
else
{
lean_object* x_344; lean_object* x_345; 
lean_dec(x_21);
lean_dec(x_18);
x_344 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_344, 0, x_19);
lean_ctor_set(x_344, 1, x_20);
x_345 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_345, 0, x_17);
lean_ctor_set(x_345, 1, x_344);
x_9 = x_345;
x_10 = lean_box(0);
goto block_13;
}
block_26:
{
lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_23 = lean_box(x_14);
if (lean_is_scalar(x_21)) {
 x_24 = lean_alloc_ctor(0, 2, 0);
} else {
 x_24 = x_21;
}
lean_ctor_set(x_24, 0, x_19);
lean_ctor_set(x_24, 1, x_23);
if (lean_is_scalar(x_18)) {
 x_25 = lean_alloc_ctor(0, 2, 0);
} else {
 x_25 = x_18;
}
lean_ctor_set(x_25, 0, x_17);
lean_ctor_set(x_25, 1, x_24);
x_9 = x_25;
x_10 = lean_box(0);
goto block_13;
}
block_32:
{
lean_object* x_29; lean_object* x_30; lean_object* x_31; 
x_29 = lean_box(x_14);
x_30 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_30, 0, x_19);
lean_ctor_set(x_30, 1, x_29);
x_31 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_31, 0, x_27);
lean_ctor_set(x_31, 1, x_30);
x_9 = x_31;
x_10 = lean_box(0);
goto block_13;
}
}
block_13:
{
lean_object* x_11; 
x_11 = lean_nat_add(x_5, x_8);
lean_dec(x_5);
x_4 = x_9;
x_5 = x_11;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_4; 
x_4 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_4, 0, x_2);
return x_4;
}
else
{
uint8_t x_5; 
x_5 = !lean_is_exclusive(x_1);
if (x_5 == 0)
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_6 = lean_ctor_get(x_1, 0);
x_7 = lean_ctor_get(x_1, 1);
x_8 = lean_ctor_get(x_6, 0);
lean_inc(x_8);
x_9 = lean_box(0);
x_10 = lp_dasmodel_twToRegVal(x_6);
x_11 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_11, 0, x_8);
lean_ctor_set(x_11, 1, x_10);
lean_ctor_set(x_1, 1, x_9);
lean_ctor_set(x_1, 0, x_11);
x_12 = l_List_appendTR___redArg(x_2, x_1);
x_1 = x_7;
x_2 = x_12;
goto _start;
}
else
{
lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_14 = lean_ctor_get(x_1, 0);
x_15 = lean_ctor_get(x_1, 1);
lean_inc(x_15);
lean_inc(x_14);
lean_dec(x_1);
x_16 = lean_ctor_get(x_14, 0);
lean_inc(x_16);
x_17 = lean_box(0);
x_18 = lp_dasmodel_twToRegVal(x_14);
x_19 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_19, 0, x_16);
lean_ctor_set(x_19, 1, x_18);
x_20 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_20, 0, x_19);
lean_ctor_set(x_20, 1, x_17);
x_21 = l_List_appendTR___redArg(x_2, x_20);
x_1 = x_15;
x_2 = x_21;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___redArg(x_1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_4; 
x_4 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_4, 0, x_2);
return x_4;
}
else
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_5 = lean_ctor_get(x_1, 0);
lean_inc(x_5);
x_6 = lean_ctor_get(x_1, 1);
lean_inc(x_6);
lean_dec_ref(x_1);
x_7 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___redArg(x_5, x_2);
x_8 = lean_ctor_get(x_7, 0);
lean_inc(x_8);
lean_dec_ref(x_7);
x_1 = x_6;
x_2 = x_8;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg(x_1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; uint8_t x_16; 
x_9 = lean_ctor_get(x_5, 1);
x_10 = lean_ctor_get(x_5, 2);
x_16 = lean_nat_dec_lt(x_7, x_9);
if (x_16 == 0)
{
lean_object* x_17; 
lean_dec(x_7);
x_17 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_17, 0, x_6);
return x_17;
}
else
{
lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; uint8_t x_29; 
x_18 = lean_ctor_get(x_6, 1);
lean_inc(x_18);
x_19 = lean_ctor_get(x_6, 0);
lean_inc(x_19);
if (lean_is_exclusive(x_6)) {
 lean_ctor_release(x_6, 0);
 lean_ctor_release(x_6, 1);
 x_20 = x_6;
} else {
 lean_dec_ref(x_6);
 x_20 = lean_box(0);
}
x_21 = lean_ctor_get(x_18, 0);
lean_inc(x_21);
x_22 = lean_ctor_get(x_18, 1);
lean_inc(x_22);
if (lean_is_exclusive(x_18)) {
 lean_ctor_release(x_18, 0);
 lean_ctor_release(x_18, 1);
 x_23 = x_18;
} else {
 lean_dec_ref(x_18);
 x_23 = lean_box(0);
}
x_29 = lean_unbox(x_22);
if (x_29 == 0)
{
lean_object* x_30; 
lean_inc(x_7);
x_30 = l_List_get_x3fInternal___redArg(x_1, x_7);
if (lean_obj_tag(x_30) == 1)
{
lean_object* x_31; uint8_t x_32; 
x_31 = lean_ctor_get(x_30, 0);
lean_inc(x_31);
lean_dec_ref(x_30);
x_32 = !lean_is_exclusive(x_31);
if (x_32 == 0)
{
lean_object* x_33; uint8_t x_34; 
x_33 = lean_ctor_get(x_31, 1);
x_34 = !lean_is_exclusive(x_33);
if (x_34 == 0)
{
lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; 
x_35 = lean_ctor_get(x_31, 0);
x_36 = lean_ctor_get(x_33, 0);
x_37 = lean_ctor_get(x_33, 1);
lean_inc(x_7);
x_38 = l_List_get_x3fInternal___redArg(x_2, x_7);
if (lean_obj_tag(x_38) == 1)
{
lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; uint8_t x_82; 
lean_dec(x_23);
lean_dec(x_20);
x_39 = lean_ctor_get(x_38, 0);
lean_inc(x_39);
lean_dec_ref(x_38);
x_40 = lean_ctor_get(x_39, 1);
lean_inc(x_40);
x_41 = lean_ctor_get(x_39, 0);
lean_inc(x_41);
if (lean_is_exclusive(x_39)) {
 lean_ctor_release(x_39, 0);
 lean_ctor_release(x_39, 1);
 x_42 = x_39;
} else {
 lean_dec_ref(x_39);
 x_42 = lean_box(0);
}
x_43 = lean_ctor_get(x_40, 0);
lean_inc(x_43);
x_44 = lean_ctor_get(x_40, 1);
lean_inc(x_44);
if (lean_is_exclusive(x_40)) {
 lean_ctor_release(x_40, 0);
 lean_ctor_release(x_40, 1);
 x_45 = x_40;
} else {
 lean_dec_ref(x_40);
 x_45 = lean_box(0);
}
x_46 = lean_unsigned_to_nat(0u);
x_47 = l_Int_toNat(x_3);
x_48 = lean_nat_add(x_35, x_47);
x_82 = lean_nat_dec_eq(x_48, x_41);
if (x_82 == 0)
{
lean_dec(x_44);
lean_dec(x_43);
lean_free_object(x_33);
lean_dec(x_37);
lean_dec(x_36);
lean_free_object(x_31);
goto block_81;
}
else
{
uint8_t x_83; 
x_83 = lean_nat_dec_eq(x_36, x_43);
lean_dec(x_43);
lean_dec(x_36);
if (x_83 == 0)
{
lean_dec(x_44);
lean_free_object(x_33);
lean_dec(x_37);
lean_free_object(x_31);
goto block_81;
}
else
{
uint8_t x_84; uint8_t x_85; uint8_t x_86; 
x_84 = lean_unbox(x_37);
lean_dec(x_37);
x_85 = lean_unbox(x_44);
lean_dec(x_44);
x_86 = lean_uint8_dec_eq(x_84, x_85);
if (x_86 == 0)
{
lean_free_object(x_33);
lean_free_object(x_31);
goto block_81;
}
else
{
lean_object* x_87; lean_object* x_88; 
lean_dec(x_48);
lean_dec(x_47);
lean_dec(x_45);
lean_dec(x_42);
lean_dec(x_41);
lean_dec(x_35);
x_87 = lean_unsigned_to_nat(1u);
x_88 = lean_nat_add(x_21, x_87);
lean_dec(x_21);
lean_ctor_set(x_33, 1, x_22);
lean_ctor_set(x_33, 0, x_88);
lean_ctor_set(x_31, 0, x_19);
x_11 = x_31;
x_12 = lean_box(0);
goto block_15;
}
}
}
block_81:
{
uint8_t x_49; 
x_49 = lean_nat_dec_eq(x_19, x_46);
if (x_49 == 0)
{
lean_object* x_50; lean_object* x_51; 
lean_dec(x_48);
lean_dec(x_47);
lean_dec(x_41);
lean_dec(x_35);
if (lean_is_scalar(x_45)) {
 x_50 = lean_alloc_ctor(0, 2, 0);
} else {
 x_50 = x_45;
}
lean_ctor_set(x_50, 0, x_21);
lean_ctor_set(x_50, 1, x_22);
if (lean_is_scalar(x_42)) {
 x_51 = lean_alloc_ctor(0, 2, 0);
} else {
 x_51 = x_42;
}
lean_ctor_set(x_51, 0, x_19);
lean_ctor_set(x_51, 1, x_50);
x_11 = x_51;
x_12 = lean_box(0);
goto block_15;
}
else
{
lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; 
lean_dec(x_22);
lean_dec(x_19);
x_52 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__0));
lean_inc(x_7);
x_53 = l_Nat_reprFast(x_7);
x_54 = lean_string_append(x_52, x_53);
lean_dec_ref(x_53);
x_55 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__1));
x_56 = lean_string_append(x_54, x_55);
x_57 = lean_string_append(x_56, x_4);
x_58 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__2));
x_59 = lean_string_append(x_57, x_58);
x_60 = l_Nat_reprFast(x_48);
x_61 = lean_string_append(x_59, x_60);
lean_dec_ref(x_60);
x_62 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__3));
x_63 = lean_string_append(x_61, x_62);
lean_inc(x_41);
x_64 = l_Nat_reprFast(x_41);
x_65 = lean_string_append(x_63, x_64);
lean_dec_ref(x_64);
x_66 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__4));
x_67 = lean_string_append(x_65, x_66);
x_68 = lean_nat_sub(x_41, x_35);
lean_dec(x_35);
lean_dec(x_41);
x_69 = lean_nat_sub(x_68, x_47);
lean_dec(x_47);
lean_dec(x_68);
x_70 = l_Nat_reprFast(x_69);
x_71 = lean_string_append(x_67, x_70);
lean_dec_ref(x_70);
x_72 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__5));
x_73 = lean_string_append(x_71, x_72);
x_74 = lp_dasmodel_IO_println___at___00main_spec__0(x_73);
if (lean_obj_tag(x_74) == 0)
{
lean_object* x_75; lean_object* x_76; lean_object* x_77; 
lean_dec_ref(x_74);
x_75 = lean_box(x_16);
if (lean_is_scalar(x_45)) {
 x_76 = lean_alloc_ctor(0, 2, 0);
} else {
 x_76 = x_45;
}
lean_ctor_set(x_76, 0, x_21);
lean_ctor_set(x_76, 1, x_75);
lean_inc(x_7);
if (lean_is_scalar(x_42)) {
 x_77 = lean_alloc_ctor(0, 2, 0);
} else {
 x_77 = x_42;
}
lean_ctor_set(x_77, 0, x_7);
lean_ctor_set(x_77, 1, x_76);
x_11 = x_77;
x_12 = lean_box(0);
goto block_15;
}
else
{
uint8_t x_78; 
lean_dec(x_45);
lean_dec(x_42);
lean_dec(x_21);
lean_dec(x_7);
x_78 = !lean_is_exclusive(x_74);
if (x_78 == 0)
{
return x_74;
}
else
{
lean_object* x_79; lean_object* x_80; 
x_79 = lean_ctor_get(x_74, 0);
lean_inc(x_79);
lean_dec(x_74);
x_80 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_80, 0, x_79);
return x_80;
}
}
}
}
}
else
{
lean_dec(x_38);
lean_free_object(x_33);
lean_dec(x_37);
lean_dec(x_36);
lean_free_object(x_31);
lean_dec(x_35);
lean_dec(x_22);
x_24 = lean_box(0);
goto block_28;
}
}
else
{
lean_object* x_89; lean_object* x_90; lean_object* x_91; lean_object* x_92; 
x_89 = lean_ctor_get(x_31, 0);
x_90 = lean_ctor_get(x_33, 0);
x_91 = lean_ctor_get(x_33, 1);
lean_inc(x_91);
lean_inc(x_90);
lean_dec(x_33);
lean_inc(x_7);
x_92 = l_List_get_x3fInternal___redArg(x_2, x_7);
if (lean_obj_tag(x_92) == 1)
{
lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_102; uint8_t x_136; 
lean_dec(x_23);
lean_dec(x_20);
x_93 = lean_ctor_get(x_92, 0);
lean_inc(x_93);
lean_dec_ref(x_92);
x_94 = lean_ctor_get(x_93, 1);
lean_inc(x_94);
x_95 = lean_ctor_get(x_93, 0);
lean_inc(x_95);
if (lean_is_exclusive(x_93)) {
 lean_ctor_release(x_93, 0);
 lean_ctor_release(x_93, 1);
 x_96 = x_93;
} else {
 lean_dec_ref(x_93);
 x_96 = lean_box(0);
}
x_97 = lean_ctor_get(x_94, 0);
lean_inc(x_97);
x_98 = lean_ctor_get(x_94, 1);
lean_inc(x_98);
if (lean_is_exclusive(x_94)) {
 lean_ctor_release(x_94, 0);
 lean_ctor_release(x_94, 1);
 x_99 = x_94;
} else {
 lean_dec_ref(x_94);
 x_99 = lean_box(0);
}
x_100 = lean_unsigned_to_nat(0u);
x_101 = l_Int_toNat(x_3);
x_102 = lean_nat_add(x_89, x_101);
x_136 = lean_nat_dec_eq(x_102, x_95);
if (x_136 == 0)
{
lean_dec(x_98);
lean_dec(x_97);
lean_dec(x_91);
lean_dec(x_90);
lean_free_object(x_31);
goto block_135;
}
else
{
uint8_t x_137; 
x_137 = lean_nat_dec_eq(x_90, x_97);
lean_dec(x_97);
lean_dec(x_90);
if (x_137 == 0)
{
lean_dec(x_98);
lean_dec(x_91);
lean_free_object(x_31);
goto block_135;
}
else
{
uint8_t x_138; uint8_t x_139; uint8_t x_140; 
x_138 = lean_unbox(x_91);
lean_dec(x_91);
x_139 = lean_unbox(x_98);
lean_dec(x_98);
x_140 = lean_uint8_dec_eq(x_138, x_139);
if (x_140 == 0)
{
lean_free_object(x_31);
goto block_135;
}
else
{
lean_object* x_141; lean_object* x_142; lean_object* x_143; 
lean_dec(x_102);
lean_dec(x_101);
lean_dec(x_99);
lean_dec(x_96);
lean_dec(x_95);
lean_dec(x_89);
x_141 = lean_unsigned_to_nat(1u);
x_142 = lean_nat_add(x_21, x_141);
lean_dec(x_21);
x_143 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_143, 0, x_142);
lean_ctor_set(x_143, 1, x_22);
lean_ctor_set(x_31, 1, x_143);
lean_ctor_set(x_31, 0, x_19);
x_11 = x_31;
x_12 = lean_box(0);
goto block_15;
}
}
}
block_135:
{
uint8_t x_103; 
x_103 = lean_nat_dec_eq(x_19, x_100);
if (x_103 == 0)
{
lean_object* x_104; lean_object* x_105; 
lean_dec(x_102);
lean_dec(x_101);
lean_dec(x_95);
lean_dec(x_89);
if (lean_is_scalar(x_99)) {
 x_104 = lean_alloc_ctor(0, 2, 0);
} else {
 x_104 = x_99;
}
lean_ctor_set(x_104, 0, x_21);
lean_ctor_set(x_104, 1, x_22);
if (lean_is_scalar(x_96)) {
 x_105 = lean_alloc_ctor(0, 2, 0);
} else {
 x_105 = x_96;
}
lean_ctor_set(x_105, 0, x_19);
lean_ctor_set(x_105, 1, x_104);
x_11 = x_105;
x_12 = lean_box(0);
goto block_15;
}
else
{
lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; 
lean_dec(x_22);
lean_dec(x_19);
x_106 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__0));
lean_inc(x_7);
x_107 = l_Nat_reprFast(x_7);
x_108 = lean_string_append(x_106, x_107);
lean_dec_ref(x_107);
x_109 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__1));
x_110 = lean_string_append(x_108, x_109);
x_111 = lean_string_append(x_110, x_4);
x_112 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__2));
x_113 = lean_string_append(x_111, x_112);
x_114 = l_Nat_reprFast(x_102);
x_115 = lean_string_append(x_113, x_114);
lean_dec_ref(x_114);
x_116 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__3));
x_117 = lean_string_append(x_115, x_116);
lean_inc(x_95);
x_118 = l_Nat_reprFast(x_95);
x_119 = lean_string_append(x_117, x_118);
lean_dec_ref(x_118);
x_120 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__4));
x_121 = lean_string_append(x_119, x_120);
x_122 = lean_nat_sub(x_95, x_89);
lean_dec(x_89);
lean_dec(x_95);
x_123 = lean_nat_sub(x_122, x_101);
lean_dec(x_101);
lean_dec(x_122);
x_124 = l_Nat_reprFast(x_123);
x_125 = lean_string_append(x_121, x_124);
lean_dec_ref(x_124);
x_126 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__5));
x_127 = lean_string_append(x_125, x_126);
x_128 = lp_dasmodel_IO_println___at___00main_spec__0(x_127);
if (lean_obj_tag(x_128) == 0)
{
lean_object* x_129; lean_object* x_130; lean_object* x_131; 
lean_dec_ref(x_128);
x_129 = lean_box(x_16);
if (lean_is_scalar(x_99)) {
 x_130 = lean_alloc_ctor(0, 2, 0);
} else {
 x_130 = x_99;
}
lean_ctor_set(x_130, 0, x_21);
lean_ctor_set(x_130, 1, x_129);
lean_inc(x_7);
if (lean_is_scalar(x_96)) {
 x_131 = lean_alloc_ctor(0, 2, 0);
} else {
 x_131 = x_96;
}
lean_ctor_set(x_131, 0, x_7);
lean_ctor_set(x_131, 1, x_130);
x_11 = x_131;
x_12 = lean_box(0);
goto block_15;
}
else
{
lean_object* x_132; lean_object* x_133; lean_object* x_134; 
lean_dec(x_99);
lean_dec(x_96);
lean_dec(x_21);
lean_dec(x_7);
x_132 = lean_ctor_get(x_128, 0);
lean_inc(x_132);
if (lean_is_exclusive(x_128)) {
 lean_ctor_release(x_128, 0);
 x_133 = x_128;
} else {
 lean_dec_ref(x_128);
 x_133 = lean_box(0);
}
if (lean_is_scalar(x_133)) {
 x_134 = lean_alloc_ctor(1, 1, 0);
} else {
 x_134 = x_133;
}
lean_ctor_set(x_134, 0, x_132);
return x_134;
}
}
}
}
else
{
lean_dec(x_92);
lean_dec(x_91);
lean_dec(x_90);
lean_free_object(x_31);
lean_dec(x_89);
lean_dec(x_22);
x_24 = lean_box(0);
goto block_28;
}
}
}
else
{
lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_148; lean_object* x_149; 
x_144 = lean_ctor_get(x_31, 1);
x_145 = lean_ctor_get(x_31, 0);
lean_inc(x_144);
lean_inc(x_145);
lean_dec(x_31);
x_146 = lean_ctor_get(x_144, 0);
lean_inc(x_146);
x_147 = lean_ctor_get(x_144, 1);
lean_inc(x_147);
if (lean_is_exclusive(x_144)) {
 lean_ctor_release(x_144, 0);
 lean_ctor_release(x_144, 1);
 x_148 = x_144;
} else {
 lean_dec_ref(x_144);
 x_148 = lean_box(0);
}
lean_inc(x_7);
x_149 = l_List_get_x3fInternal___redArg(x_2, x_7);
if (lean_obj_tag(x_149) == 1)
{
lean_object* x_150; lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_154; lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; uint8_t x_193; 
lean_dec(x_23);
lean_dec(x_20);
x_150 = lean_ctor_get(x_149, 0);
lean_inc(x_150);
lean_dec_ref(x_149);
x_151 = lean_ctor_get(x_150, 1);
lean_inc(x_151);
x_152 = lean_ctor_get(x_150, 0);
lean_inc(x_152);
if (lean_is_exclusive(x_150)) {
 lean_ctor_release(x_150, 0);
 lean_ctor_release(x_150, 1);
 x_153 = x_150;
} else {
 lean_dec_ref(x_150);
 x_153 = lean_box(0);
}
x_154 = lean_ctor_get(x_151, 0);
lean_inc(x_154);
x_155 = lean_ctor_get(x_151, 1);
lean_inc(x_155);
if (lean_is_exclusive(x_151)) {
 lean_ctor_release(x_151, 0);
 lean_ctor_release(x_151, 1);
 x_156 = x_151;
} else {
 lean_dec_ref(x_151);
 x_156 = lean_box(0);
}
x_157 = lean_unsigned_to_nat(0u);
x_158 = l_Int_toNat(x_3);
x_159 = lean_nat_add(x_145, x_158);
x_193 = lean_nat_dec_eq(x_159, x_152);
if (x_193 == 0)
{
lean_dec(x_155);
lean_dec(x_154);
lean_dec(x_148);
lean_dec(x_147);
lean_dec(x_146);
goto block_192;
}
else
{
uint8_t x_194; 
x_194 = lean_nat_dec_eq(x_146, x_154);
lean_dec(x_154);
lean_dec(x_146);
if (x_194 == 0)
{
lean_dec(x_155);
lean_dec(x_148);
lean_dec(x_147);
goto block_192;
}
else
{
uint8_t x_195; uint8_t x_196; uint8_t x_197; 
x_195 = lean_unbox(x_147);
lean_dec(x_147);
x_196 = lean_unbox(x_155);
lean_dec(x_155);
x_197 = lean_uint8_dec_eq(x_195, x_196);
if (x_197 == 0)
{
lean_dec(x_148);
goto block_192;
}
else
{
lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; 
lean_dec(x_159);
lean_dec(x_158);
lean_dec(x_156);
lean_dec(x_153);
lean_dec(x_152);
lean_dec(x_145);
x_198 = lean_unsigned_to_nat(1u);
x_199 = lean_nat_add(x_21, x_198);
lean_dec(x_21);
if (lean_is_scalar(x_148)) {
 x_200 = lean_alloc_ctor(0, 2, 0);
} else {
 x_200 = x_148;
}
lean_ctor_set(x_200, 0, x_199);
lean_ctor_set(x_200, 1, x_22);
x_201 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_201, 0, x_19);
lean_ctor_set(x_201, 1, x_200);
x_11 = x_201;
x_12 = lean_box(0);
goto block_15;
}
}
}
block_192:
{
uint8_t x_160; 
x_160 = lean_nat_dec_eq(x_19, x_157);
if (x_160 == 0)
{
lean_object* x_161; lean_object* x_162; 
lean_dec(x_159);
lean_dec(x_158);
lean_dec(x_152);
lean_dec(x_145);
if (lean_is_scalar(x_156)) {
 x_161 = lean_alloc_ctor(0, 2, 0);
} else {
 x_161 = x_156;
}
lean_ctor_set(x_161, 0, x_21);
lean_ctor_set(x_161, 1, x_22);
if (lean_is_scalar(x_153)) {
 x_162 = lean_alloc_ctor(0, 2, 0);
} else {
 x_162 = x_153;
}
lean_ctor_set(x_162, 0, x_19);
lean_ctor_set(x_162, 1, x_161);
x_11 = x_162;
x_12 = lean_box(0);
goto block_15;
}
else
{
lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; lean_object* x_178; lean_object* x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; lean_object* x_184; lean_object* x_185; 
lean_dec(x_22);
lean_dec(x_19);
x_163 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__0));
lean_inc(x_7);
x_164 = l_Nat_reprFast(x_7);
x_165 = lean_string_append(x_163, x_164);
lean_dec_ref(x_164);
x_166 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__1));
x_167 = lean_string_append(x_165, x_166);
x_168 = lean_string_append(x_167, x_4);
x_169 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__2));
x_170 = lean_string_append(x_168, x_169);
x_171 = l_Nat_reprFast(x_159);
x_172 = lean_string_append(x_170, x_171);
lean_dec_ref(x_171);
x_173 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__3));
x_174 = lean_string_append(x_172, x_173);
lean_inc(x_152);
x_175 = l_Nat_reprFast(x_152);
x_176 = lean_string_append(x_174, x_175);
lean_dec_ref(x_175);
x_177 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__4));
x_178 = lean_string_append(x_176, x_177);
x_179 = lean_nat_sub(x_152, x_145);
lean_dec(x_145);
lean_dec(x_152);
x_180 = lean_nat_sub(x_179, x_158);
lean_dec(x_158);
lean_dec(x_179);
x_181 = l_Nat_reprFast(x_180);
x_182 = lean_string_append(x_178, x_181);
lean_dec_ref(x_181);
x_183 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___closed__5));
x_184 = lean_string_append(x_182, x_183);
x_185 = lp_dasmodel_IO_println___at___00main_spec__0(x_184);
if (lean_obj_tag(x_185) == 0)
{
lean_object* x_186; lean_object* x_187; lean_object* x_188; 
lean_dec_ref(x_185);
x_186 = lean_box(x_16);
if (lean_is_scalar(x_156)) {
 x_187 = lean_alloc_ctor(0, 2, 0);
} else {
 x_187 = x_156;
}
lean_ctor_set(x_187, 0, x_21);
lean_ctor_set(x_187, 1, x_186);
lean_inc(x_7);
if (lean_is_scalar(x_153)) {
 x_188 = lean_alloc_ctor(0, 2, 0);
} else {
 x_188 = x_153;
}
lean_ctor_set(x_188, 0, x_7);
lean_ctor_set(x_188, 1, x_187);
x_11 = x_188;
x_12 = lean_box(0);
goto block_15;
}
else
{
lean_object* x_189; lean_object* x_190; lean_object* x_191; 
lean_dec(x_156);
lean_dec(x_153);
lean_dec(x_21);
lean_dec(x_7);
x_189 = lean_ctor_get(x_185, 0);
lean_inc(x_189);
if (lean_is_exclusive(x_185)) {
 lean_ctor_release(x_185, 0);
 x_190 = x_185;
} else {
 lean_dec_ref(x_185);
 x_190 = lean_box(0);
}
if (lean_is_scalar(x_190)) {
 x_191 = lean_alloc_ctor(1, 1, 0);
} else {
 x_191 = x_190;
}
lean_ctor_set(x_191, 0, x_189);
return x_191;
}
}
}
}
else
{
lean_dec(x_149);
lean_dec(x_148);
lean_dec(x_147);
lean_dec(x_146);
lean_dec(x_145);
lean_dec(x_22);
x_24 = lean_box(0);
goto block_28;
}
}
}
else
{
lean_dec(x_30);
lean_dec(x_22);
x_24 = lean_box(0);
goto block_28;
}
}
else
{
lean_object* x_202; lean_object* x_203; 
lean_dec(x_23);
lean_dec(x_20);
x_202 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_202, 0, x_21);
lean_ctor_set(x_202, 1, x_22);
x_203 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_203, 0, x_19);
lean_ctor_set(x_203, 1, x_202);
x_11 = x_203;
x_12 = lean_box(0);
goto block_15;
}
block_28:
{
lean_object* x_25; lean_object* x_26; lean_object* x_27; 
x_25 = lean_box(x_16);
if (lean_is_scalar(x_23)) {
 x_26 = lean_alloc_ctor(0, 2, 0);
} else {
 x_26 = x_23;
}
lean_ctor_set(x_26, 0, x_21);
lean_ctor_set(x_26, 1, x_25);
if (lean_is_scalar(x_20)) {
 x_27 = lean_alloc_ctor(0, 2, 0);
} else {
 x_27 = x_20;
}
lean_ctor_set(x_27, 0, x_19);
lean_ctor_set(x_27, 1, x_26);
x_11 = x_27;
x_12 = lean_box(0);
goto block_15;
}
}
block_15:
{
lean_object* x_13; 
x_13 = lean_nat_add(x_7, x_10);
lean_dec(x_7);
x_6 = x_11;
x_7 = x_13;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_5);
lean_dec_ref(x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint8_t x_14; 
x_7 = lean_ctor_get(x_3, 1);
x_8 = lean_ctor_get(x_3, 2);
x_14 = lean_nat_dec_lt(x_5, x_7);
if (x_14 == 0)
{
lean_object* x_15; 
lean_dec(x_5);
x_15 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_15, 0, x_4);
return x_15;
}
else
{
lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_22; uint8_t x_26; 
x_16 = lean_ctor_get(x_4, 0);
lean_inc(x_16);
x_17 = lean_ctor_get(x_4, 1);
lean_inc(x_17);
if (lean_is_exclusive(x_4)) {
 lean_ctor_release(x_4, 0);
 lean_ctor_release(x_4, 1);
 x_18 = x_4;
} else {
 lean_dec_ref(x_4);
 x_18 = lean_box(0);
}
x_26 = lean_unbox(x_17);
if (x_26 == 0)
{
lean_object* x_27; 
lean_inc(x_5);
x_27 = l_List_get_x3fInternal___redArg(x_1, x_5);
if (lean_obj_tag(x_27) == 1)
{
lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; 
x_28 = lean_ctor_get(x_27, 0);
lean_inc(x_28);
lean_dec_ref(x_27);
x_29 = lean_ctor_get(x_28, 1);
lean_inc(x_29);
lean_dec(x_28);
x_30 = lean_ctor_get(x_29, 0);
lean_inc(x_30);
x_31 = lean_ctor_get(x_29, 1);
lean_inc(x_31);
lean_dec(x_29);
lean_inc(x_5);
x_32 = l_List_get_x3fInternal___redArg(x_2, x_5);
if (lean_obj_tag(x_32) == 1)
{
lean_object* x_33; lean_object* x_34; uint8_t x_35; 
x_33 = lean_ctor_get(x_32, 0);
lean_inc(x_33);
lean_dec_ref(x_32);
x_34 = lean_ctor_get(x_33, 1);
lean_inc(x_34);
lean_dec(x_33);
x_35 = !lean_is_exclusive(x_34);
if (x_35 == 0)
{
lean_object* x_36; lean_object* x_37; uint8_t x_38; 
x_36 = lean_ctor_get(x_34, 0);
x_37 = lean_ctor_get(x_34, 1);
x_38 = lean_nat_dec_eq(x_30, x_36);
lean_dec(x_36);
lean_dec(x_30);
if (x_38 == 0)
{
lean_free_object(x_34);
lean_dec(x_37);
lean_dec(x_31);
lean_dec(x_17);
goto block_21;
}
else
{
uint8_t x_39; uint8_t x_40; uint8_t x_41; 
x_39 = lean_unbox(x_31);
lean_dec(x_31);
x_40 = lean_unbox(x_37);
lean_dec(x_37);
x_41 = lean_uint8_dec_eq(x_39, x_40);
if (x_41 == 0)
{
lean_free_object(x_34);
lean_dec(x_17);
goto block_21;
}
else
{
lean_object* x_42; lean_object* x_43; 
lean_dec(x_18);
x_42 = lean_unsigned_to_nat(1u);
x_43 = lean_nat_add(x_16, x_42);
lean_dec(x_16);
lean_ctor_set(x_34, 1, x_17);
lean_ctor_set(x_34, 0, x_43);
x_9 = x_34;
x_10 = lean_box(0);
goto block_13;
}
}
}
else
{
lean_object* x_44; lean_object* x_45; uint8_t x_46; 
x_44 = lean_ctor_get(x_34, 0);
x_45 = lean_ctor_get(x_34, 1);
lean_inc(x_45);
lean_inc(x_44);
lean_dec(x_34);
x_46 = lean_nat_dec_eq(x_30, x_44);
lean_dec(x_44);
lean_dec(x_30);
if (x_46 == 0)
{
lean_dec(x_45);
lean_dec(x_31);
lean_dec(x_17);
goto block_21;
}
else
{
uint8_t x_47; uint8_t x_48; uint8_t x_49; 
x_47 = lean_unbox(x_31);
lean_dec(x_31);
x_48 = lean_unbox(x_45);
lean_dec(x_45);
x_49 = lean_uint8_dec_eq(x_47, x_48);
if (x_49 == 0)
{
lean_dec(x_17);
goto block_21;
}
else
{
lean_object* x_50; lean_object* x_51; lean_object* x_52; 
lean_dec(x_18);
x_50 = lean_unsigned_to_nat(1u);
x_51 = lean_nat_add(x_16, x_50);
lean_dec(x_16);
x_52 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_52, 0, x_51);
lean_ctor_set(x_52, 1, x_17);
x_9 = x_52;
x_10 = lean_box(0);
goto block_13;
}
}
}
}
else
{
lean_dec(x_32);
lean_dec(x_31);
lean_dec(x_30);
lean_dec(x_18);
lean_dec(x_17);
x_22 = lean_box(0);
goto block_25;
}
}
else
{
lean_dec(x_27);
lean_dec(x_18);
lean_dec(x_17);
x_22 = lean_box(0);
goto block_25;
}
}
else
{
lean_object* x_53; 
lean_dec(x_18);
x_53 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_53, 0, x_16);
lean_ctor_set(x_53, 1, x_17);
x_9 = x_53;
x_10 = lean_box(0);
goto block_13;
}
block_21:
{
lean_object* x_19; lean_object* x_20; 
x_19 = lean_box(x_14);
if (lean_is_scalar(x_18)) {
 x_20 = lean_alloc_ctor(0, 2, 0);
} else {
 x_20 = x_18;
}
lean_ctor_set(x_20, 0, x_16);
lean_ctor_set(x_20, 1, x_19);
x_9 = x_20;
x_10 = lean_box(0);
goto block_13;
}
block_25:
{
lean_object* x_23; lean_object* x_24; 
x_23 = lean_box(x_14);
x_24 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_24, 0, x_16);
lean_ctor_set(x_24, 1, x_23);
x_9 = x_24;
x_10 = lean_box(0);
goto block_13;
}
}
block_13:
{
lean_object* x_11; 
x_11 = lean_nat_add(x_5, x_8);
lean_dec(x_5);
x_4 = x_9;
x_5 = x_11;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_5; 
x_5 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_5, 0, x_3);
return x_5;
}
else
{
uint8_t x_6; 
x_6 = !lean_is_exclusive(x_2);
if (x_6 == 0)
{
lean_object* x_7; uint8_t x_8; 
x_7 = lean_ctor_get(x_2, 0);
x_8 = !lean_is_exclusive(x_7);
if (x_8 == 0)
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_9 = lean_ctor_get(x_2, 1);
x_10 = lean_ctor_get(x_7, 0);
x_11 = lean_box(0);
x_12 = lean_nat_add(x_1, x_10);
lean_dec(x_10);
lean_ctor_set(x_7, 0, x_12);
lean_ctor_set(x_2, 1, x_11);
x_13 = l_List_appendTR___redArg(x_3, x_2);
x_2 = x_9;
x_3 = x_13;
goto _start;
}
else
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_15 = lean_ctor_get(x_2, 1);
x_16 = lean_ctor_get(x_7, 0);
x_17 = lean_ctor_get(x_7, 1);
lean_inc(x_17);
lean_inc(x_16);
lean_dec(x_7);
x_18 = lean_box(0);
x_19 = lean_nat_add(x_1, x_16);
lean_dec(x_16);
x_20 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_20, 0, x_19);
lean_ctor_set(x_20, 1, x_17);
lean_ctor_set(x_2, 1, x_18);
lean_ctor_set(x_2, 0, x_20);
x_21 = l_List_appendTR___redArg(x_3, x_2);
x_2 = x_15;
x_3 = x_21;
goto _start;
}
}
else
{
lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; 
x_23 = lean_ctor_get(x_2, 0);
x_24 = lean_ctor_get(x_2, 1);
lean_inc(x_24);
lean_inc(x_23);
lean_dec(x_2);
x_25 = lean_ctor_get(x_23, 0);
lean_inc(x_25);
x_26 = lean_ctor_get(x_23, 1);
lean_inc(x_26);
if (lean_is_exclusive(x_23)) {
 lean_ctor_release(x_23, 0);
 lean_ctor_release(x_23, 1);
 x_27 = x_23;
} else {
 lean_dec_ref(x_23);
 x_27 = lean_box(0);
}
x_28 = lean_box(0);
x_29 = lean_nat_add(x_1, x_25);
lean_dec(x_25);
if (lean_is_scalar(x_27)) {
 x_30 = lean_alloc_ctor(0, 2, 0);
} else {
 x_30 = x_27;
}
lean_ctor_set(x_30, 0, x_29);
lean_ctor_set(x_30, 1, x_26);
x_31 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_31, 0, x_30);
lean_ctor_set(x_31, 1, x_28);
x_32 = l_List_appendTR___redArg(x_3, x_31);
x_2 = x_24;
x_3 = x_32;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg(x_1, x_2, x_3);
lean_dec(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_4; 
x_4 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_4, 0, x_2);
return x_4;
}
else
{
lean_object* x_5; lean_object* x_6; uint8_t x_7; 
x_5 = lean_ctor_get(x_1, 0);
lean_inc(x_5);
x_6 = lean_ctor_get(x_1, 1);
lean_inc(x_6);
lean_dec_ref(x_1);
x_7 = !lean_is_exclusive(x_2);
if (x_7 == 0)
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_8 = lean_ctor_get(x_2, 0);
x_9 = lean_ctor_get(x_2, 1);
x_10 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg(x_9, x_5, x_8);
x_11 = lean_ctor_get(x_10, 0);
lean_inc(x_11);
lean_dec_ref(x_10);
x_12 = lean_unsigned_to_nat(19688u);
x_13 = lean_nat_add(x_9, x_12);
lean_dec(x_9);
lean_ctor_set(x_2, 1, x_13);
lean_ctor_set(x_2, 0, x_11);
x_1 = x_6;
goto _start;
}
else
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_15 = lean_ctor_get(x_2, 0);
x_16 = lean_ctor_get(x_2, 1);
lean_inc(x_16);
lean_inc(x_15);
lean_dec(x_2);
x_17 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg(x_16, x_5, x_15);
x_18 = lean_ctor_get(x_17, 0);
lean_inc(x_18);
lean_dec_ref(x_17);
x_19 = lean_unsigned_to_nat(19688u);
x_20 = lean_nat_add(x_16, x_19);
lean_dec(x_16);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_18);
lean_ctor_set(x_21, 1, x_20);
x_1 = x_6;
x_2 = x_21;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg(x_1, x_2);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_main___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(11u);
x_2 = l_Nat_reprFast(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__9(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(6u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__10(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_main___closed__0));
x_2 = lean_obj_once(&lp_dasmodel_main___closed__9, &lp_dasmodel_main___closed__9_once, _init_lp_dasmodel_main___closed__9);
x_3 = lean_array_push(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__11(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_main___closed__4));
x_2 = lean_obj_once(&lp_dasmodel_main___closed__10, &lp_dasmodel_main___closed__10_once, _init_lp_dasmodel_main___closed__10);
x_3 = lean_array_push(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__12(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_main___closed__5));
x_2 = lean_obj_once(&lp_dasmodel_main___closed__11, &lp_dasmodel_main___closed__11_once, _init_lp_dasmodel_main___closed__11);
x_3 = lean_array_push(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__13(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_main___closed__6));
x_2 = lean_obj_once(&lp_dasmodel_main___closed__12, &lp_dasmodel_main___closed__12_once, _init_lp_dasmodel_main___closed__12);
x_3 = lean_array_push(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__14(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__7, &lp_dasmodel_main___closed__7_once, _init_lp_dasmodel_main___closed__7);
x_2 = lean_obj_once(&lp_dasmodel_main___closed__13, &lp_dasmodel_main___closed__13_once, _init_lp_dasmodel_main___closed__13);
x_3 = lean_array_push(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__15(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_main___closed__8));
x_2 = lean_obj_once(&lp_dasmodel_main___closed__14, &lp_dasmodel_main___closed__14_once, _init_lp_dasmodel_main___closed__14);
x_3 = lean_array_push(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__18(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__19(void) {
_start:
{
uint8_t x_1; uint8_t x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_1 = 0;
x_2 = 1;
x_3 = lean_obj_once(&lp_dasmodel_main___closed__18, &lp_dasmodel_main___closed__18_once, _init_lp_dasmodel_main___closed__18);
x_4 = lean_box(0);
x_5 = lean_obj_once(&lp_dasmodel_main___closed__15, &lp_dasmodel_main___closed__15_once, _init_lp_dasmodel_main___closed__15);
x_6 = ((lean_object*)(lp_dasmodel_main___closed__3));
x_7 = ((lean_object*)(lp_dasmodel_main___closed__2));
x_8 = lean_alloc_ctor(0, 5, 2);
lean_ctor_set(x_8, 0, x_7);
lean_ctor_set(x_8, 1, x_6);
lean_ctor_set(x_8, 2, x_5);
lean_ctor_set(x_8, 3, x_4);
lean_ctor_set(x_8, 4, x_3);
lean_ctor_set_uint8(x_8, sizeof(void*)*5, x_2);
lean_ctor_set_uint8(x_8, sizeof(void*)*5 + 1, x_1);
return x_8;
}
}
static lean_object* _init_lp_dasmodel_main___closed__25(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_unsigned_to_nat(0u);
x_3 = lean_box(x_1);
x_4 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_4, 0, x_2);
lean_ctor_set(x_4, 1, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_main___closed__28(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__25, &lp_dasmodel_main___closed__25_once, _init_lp_dasmodel_main___closed__25);
x_2 = lean_unsigned_to_nat(0u);
x_3 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_3, 0, x_2);
lean_ctor_set(x_3, 1, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__31(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* _lean_main() {
_start:
{
lean_object* x_2; lean_object* x_6; lean_object* x_7; 
x_6 = ((lean_object*)(lp_dasmodel_main___closed__0));
x_7 = l_IO_FS_readBinFile(x_6);
if (lean_obj_tag(x_7) == 0)
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_8 = lean_ctor_get(x_7, 0);
lean_inc(x_8);
lean_dec_ref(x_7);
x_9 = ((lean_object*)(lp_dasmodel_main___closed__1));
x_10 = lp_dasmodel_IO_println___at___00main_spec__0(x_9);
if (lean_obj_tag(x_10) == 0)
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_51; lean_object* x_52; 
lean_dec_ref(x_10);
x_11 = lean_box(0);
x_12 = lean_unsigned_to_nat(0u);
x_51 = lean_obj_once(&lp_dasmodel_main___closed__19, &lp_dasmodel_main___closed__19_once, _init_lp_dasmodel_main___closed__19);
x_52 = l_IO_Process_output(x_51, x_11);
if (lean_obj_tag(x_52) == 0)
{
lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; 
x_53 = lean_ctor_get(x_52, 0);
lean_inc(x_53);
lean_dec_ref(x_52);
x_54 = lean_ctor_get(x_53, 0);
lean_inc_ref(x_54);
lean_dec(x_53);
x_55 = lp_dasmodel_parseLog(x_54);
lean_dec_ref(x_54);
x_56 = ((lean_object*)(lp_dasmodel_main___closed__20));
x_57 = l_List_lengthTR___redArg(x_55);
x_58 = l_Nat_reprFast(x_57);
x_59 = lean_string_append(x_56, x_58);
lean_dec_ref(x_58);
x_60 = ((lean_object*)(lp_dasmodel_main___closed__21));
x_61 = lean_string_append(x_59, x_60);
x_62 = lp_dasmodel_IO_println___at___00main_spec__0(x_61);
if (lean_obj_tag(x_62) == 0)
{
lean_object* x_63; 
lean_dec_ref(x_62);
x_63 = lp_dasmodel_loadSID(x_8);
lean_dec(x_8);
if (lean_obj_tag(x_63) == 0)
{
lean_object* x_64; lean_object* x_65; 
lean_dec(x_55);
x_64 = ((lean_object*)(lp_dasmodel_main___closed__22));
x_65 = lp_dasmodel_IO_println___at___00main_spec__0(x_64);
return x_65;
}
else
{
lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; uint16_t x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; uint16_t x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; lean_object* x_82; 
x_66 = lean_ctor_get(x_63, 0);
lean_inc(x_66);
lean_dec_ref(x_63);
x_67 = lean_ctor_get(x_66, 1);
lean_inc(x_67);
x_68 = lean_ctor_get(x_66, 0);
lean_inc(x_68);
lean_dec(x_66);
x_69 = lean_ctor_get(x_67, 0);
lean_inc(x_69);
x_70 = lean_ctor_get(x_67, 1);
lean_inc(x_70);
lean_dec(x_67);
x_71 = ((lean_object*)(lp_dasmodel_main___closed__23));
x_72 = lean_unbox(x_69);
x_73 = lean_uint16_to_nat(x_72);
x_74 = l_Nat_reprFast(x_73);
x_75 = lean_string_append(x_71, x_74);
lean_dec_ref(x_74);
x_76 = ((lean_object*)(lp_dasmodel_main___closed__24));
x_77 = lean_string_append(x_75, x_76);
x_78 = lean_unbox(x_70);
x_79 = lean_uint16_to_nat(x_78);
x_80 = l_Nat_reprFast(x_79);
x_81 = lean_string_append(x_77, x_80);
lean_dec_ref(x_80);
x_82 = lp_dasmodel_IO_println___at___00main_spec__0(x_81);
if (lean_obj_tag(x_82) == 0)
{
uint16_t x_83; uint8_t x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; uint8_t x_88; uint16_t x_89; lean_object* x_90; uint8_t x_91; 
lean_dec_ref(x_82);
x_83 = 54296;
x_84 = 15;
x_85 = lp_dasmodel_CPU_write(x_68, x_83, x_84);
x_86 = lean_ctor_get(x_85, 0);
lean_inc(x_86);
x_87 = lean_ctor_get(x_85, 1);
lean_inc(x_87);
lean_dec_ref(x_85);
x_88 = 0;
x_89 = lean_unbox(x_69);
lean_dec(x_69);
x_90 = lp_dasmodel_execInit(x_86, x_89, x_88);
x_91 = !lean_is_exclusive(x_90);
if (x_91 == 0)
{
lean_object* x_92; uint8_t x_93; 
x_92 = lean_ctor_get(x_90, 0);
x_93 = !lean_is_exclusive(x_92);
if (x_93 == 0)
{
lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; lean_object* x_100; lean_object* x_101; lean_object* x_150; uint16_t x_179; lean_object* x_180; 
x_94 = lean_ctor_get(x_90, 1);
x_95 = lean_ctor_get(x_92, 2);
lean_dec(x_95);
x_96 = lean_unsigned_to_nat(500u);
x_97 = lean_unsigned_to_nat(1u);
lean_ctor_set(x_92, 2, x_12);
x_179 = lean_unbox(x_70);
lean_dec(x_70);
x_180 = lp_dasmodel_execFrames(x_92, x_179, x_96);
if (lean_obj_tag(x_180) == 0)
{
lean_object* x_181; 
x_181 = l_List_appendTR___redArg(x_87, x_94);
lean_ctor_set_tag(x_90, 1);
lean_ctor_set(x_90, 1, x_180);
lean_ctor_set(x_90, 0, x_181);
x_150 = x_90;
goto block_178;
}
else
{
uint8_t x_182; 
lean_free_object(x_90);
x_182 = !lean_is_exclusive(x_180);
if (x_182 == 0)
{
lean_object* x_183; lean_object* x_184; lean_object* x_185; 
x_183 = lean_ctor_get(x_180, 0);
x_184 = l_List_appendTR___redArg(x_87, x_94);
x_185 = l_List_appendTR___redArg(x_184, x_183);
lean_ctor_set(x_180, 0, x_185);
x_150 = x_180;
goto block_178;
}
else
{
lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; 
x_186 = lean_ctor_get(x_180, 0);
x_187 = lean_ctor_get(x_180, 1);
lean_inc(x_187);
lean_inc(x_186);
lean_dec(x_180);
x_188 = l_List_appendTR___redArg(x_87, x_94);
x_189 = l_List_appendTR___redArg(x_188, x_186);
x_190 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_190, 0, x_189);
lean_ctor_set(x_190, 1, x_187);
x_150 = x_190;
goto block_178;
}
}
block_149:
{
lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; lean_object* x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; lean_object* x_114; 
lean_inc(x_101);
x_102 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_102, 0, x_12);
lean_ctor_set(x_102, 1, x_101);
lean_ctor_set(x_102, 2, x_97);
x_103 = lean_obj_once(&lp_dasmodel_main___closed__25, &lp_dasmodel_main___closed__25_once, _init_lp_dasmodel_main___closed__25);
x_104 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg(x_100, x_98, x_102, x_103, x_12);
x_105 = lean_ctor_get(x_104, 0);
lean_inc(x_105);
lean_dec_ref(x_104);
x_106 = lean_ctor_get(x_105, 0);
lean_inc(x_106);
lean_dec(x_105);
x_107 = ((lean_object*)(lp_dasmodel_main___closed__26));
x_108 = l_Nat_reprFast(x_106);
x_109 = lean_string_append(x_107, x_108);
lean_dec_ref(x_108);
x_110 = ((lean_object*)(lp_dasmodel_main___closed__27));
x_111 = lean_string_append(x_109, x_110);
lean_inc(x_101);
x_112 = l_Nat_reprFast(x_101);
x_113 = lean_string_append(x_111, x_112);
x_114 = lp_dasmodel_IO_println___at___00main_spec__0(x_113);
if (lean_obj_tag(x_114) == 0)
{
lean_object* x_115; lean_object* x_116; 
lean_dec_ref(x_114);
x_115 = lean_obj_once(&lp_dasmodel_main___closed__28, &lp_dasmodel_main___closed__28_once, _init_lp_dasmodel_main___closed__28);
x_116 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg(x_100, x_98, x_102, x_115, x_12);
if (lean_obj_tag(x_116) == 0)
{
lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; 
x_117 = lean_ctor_get(x_116, 0);
lean_inc(x_117);
lean_dec_ref(x_116);
x_118 = lean_ctor_get(x_117, 1);
lean_inc(x_118);
lean_dec(x_117);
x_119 = lean_ctor_get(x_118, 0);
lean_inc(x_119);
lean_dec(x_118);
x_120 = ((lean_object*)(lp_dasmodel_main___closed__29));
x_121 = l_Nat_reprFast(x_119);
x_122 = lean_string_append(x_120, x_121);
lean_dec_ref(x_121);
x_123 = lean_string_append(x_122, x_110);
x_124 = lean_string_append(x_123, x_112);
x_125 = lp_dasmodel_IO_println___at___00main_spec__0(x_124);
if (lean_obj_tag(x_125) == 0)
{
lean_object* x_126; 
lean_dec_ref(x_125);
x_126 = l_List_get_x3fInternal___redArg(x_100, x_12);
if (lean_obj_tag(x_126) == 1)
{
lean_object* x_127; lean_object* x_128; lean_object* x_129; 
x_127 = lean_ctor_get(x_126, 0);
lean_inc(x_127);
lean_dec_ref(x_126);
x_128 = lean_ctor_get(x_127, 0);
lean_inc(x_128);
lean_dec(x_127);
x_129 = l_List_get_x3fInternal___redArg(x_98, x_12);
if (lean_obj_tag(x_129) == 1)
{
lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; lean_object* x_135; lean_object* x_136; uint8_t x_137; 
x_130 = lean_ctor_get(x_129, 0);
lean_inc(x_130);
lean_dec_ref(x_129);
x_131 = lean_ctor_get(x_130, 0);
lean_inc(x_131);
lean_dec(x_130);
x_132 = lean_nat_to_int(x_131);
x_133 = lean_nat_to_int(x_128);
x_134 = lean_int_sub(x_132, x_133);
lean_dec(x_133);
lean_dec(x_132);
x_135 = ((lean_object*)(lp_dasmodel_main___closed__30));
x_136 = lean_obj_once(&lp_dasmodel_main___closed__31, &lp_dasmodel_main___closed__31_once, _init_lp_dasmodel_main___closed__31);
x_137 = lean_int_dec_lt(x_134, x_136);
if (x_137 == 0)
{
lean_object* x_138; lean_object* x_139; 
x_138 = lean_nat_abs(x_134);
x_139 = l_Nat_reprFast(x_138);
x_13 = lean_box(0);
x_14 = x_135;
x_15 = x_101;
x_16 = x_98;
x_17 = x_102;
x_18 = x_110;
x_19 = x_115;
x_20 = x_134;
x_21 = x_112;
x_22 = x_100;
x_23 = x_139;
goto block_50;
}
else
{
lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; 
x_140 = lean_nat_abs(x_134);
x_141 = lean_nat_sub(x_140, x_97);
lean_dec(x_140);
x_142 = ((lean_object*)(lp_dasmodel_main___closed__32));
x_143 = lean_nat_add(x_141, x_97);
lean_dec(x_141);
x_144 = l_Nat_reprFast(x_143);
x_145 = lean_string_append(x_142, x_144);
lean_dec_ref(x_144);
x_13 = lean_box(0);
x_14 = x_135;
x_15 = x_101;
x_16 = x_98;
x_17 = x_102;
x_18 = x_110;
x_19 = x_115;
x_20 = x_134;
x_21 = x_112;
x_22 = x_100;
x_23 = x_145;
goto block_50;
}
}
else
{
lean_dec(x_129);
lean_dec(x_128);
lean_dec_ref(x_112);
lean_dec_ref(x_102);
lean_dec(x_101);
lean_dec(x_100);
lean_dec(x_98);
x_2 = lean_box(0);
goto block_5;
}
}
else
{
lean_dec(x_126);
lean_dec_ref(x_112);
lean_dec_ref(x_102);
lean_dec(x_101);
lean_dec(x_100);
lean_dec(x_98);
x_2 = lean_box(0);
goto block_5;
}
}
else
{
lean_dec_ref(x_112);
lean_dec_ref(x_102);
lean_dec(x_101);
lean_dec(x_100);
lean_dec(x_98);
return x_125;
}
}
else
{
uint8_t x_146; 
lean_dec_ref(x_112);
lean_dec_ref(x_102);
lean_dec(x_101);
lean_dec(x_100);
lean_dec(x_98);
x_146 = !lean_is_exclusive(x_116);
if (x_146 == 0)
{
return x_116;
}
else
{
lean_object* x_147; lean_object* x_148; 
x_147 = lean_ctor_get(x_116, 0);
lean_inc(x_147);
lean_dec(x_116);
x_148 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_148, 0, x_147);
return x_148;
}
}
}
else
{
lean_dec_ref(x_112);
lean_dec_ref(x_102);
lean_dec(x_101);
lean_dec(x_100);
lean_dec(x_98);
return x_114;
}
}
block_178:
{
lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_154; lean_object* x_155; lean_object* x_156; 
x_151 = ((lean_object*)(lp_dasmodel_main___closed__33));
x_152 = l_List_lengthTR___redArg(x_150);
x_153 = l_Nat_reprFast(x_152);
x_154 = lean_string_append(x_151, x_153);
lean_dec_ref(x_153);
x_155 = lean_string_append(x_154, x_60);
x_156 = lp_dasmodel_IO_println___at___00main_spec__0(x_155);
if (lean_obj_tag(x_156) == 0)
{
lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; 
lean_dec_ref(x_156);
x_157 = lean_box(0);
x_158 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg(x_150, x_157);
x_159 = lean_ctor_get(x_158, 0);
lean_inc(x_159);
lean_dec_ref(x_158);
x_160 = ((lean_object*)(lp_dasmodel_main___closed__34));
x_161 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg(x_55, x_160);
if (lean_obj_tag(x_161) == 0)
{
lean_object* x_162; lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; lean_object* x_172; lean_object* x_173; 
x_162 = lean_ctor_get(x_161, 0);
lean_inc(x_162);
lean_dec_ref(x_161);
x_163 = lean_ctor_get(x_162, 0);
lean_inc(x_163);
lean_dec(x_162);
x_164 = ((lean_object*)(lp_dasmodel_main___closed__35));
x_165 = l_List_lengthTR___redArg(x_159);
lean_inc(x_165);
x_166 = l_Nat_reprFast(x_165);
x_167 = lean_string_append(x_164, x_166);
lean_dec_ref(x_166);
x_168 = ((lean_object*)(lp_dasmodel_main___closed__36));
x_169 = lean_string_append(x_167, x_168);
x_170 = l_List_lengthTR___redArg(x_163);
lean_inc(x_170);
x_171 = l_Nat_reprFast(x_170);
x_172 = lean_string_append(x_169, x_171);
lean_dec_ref(x_171);
x_173 = lp_dasmodel_IO_println___at___00main_spec__0(x_172);
if (lean_obj_tag(x_173) == 0)
{
uint8_t x_174; 
lean_dec_ref(x_173);
x_174 = lean_nat_dec_le(x_165, x_170);
if (x_174 == 0)
{
lean_dec(x_165);
x_98 = x_163;
x_99 = lean_box(0);
x_100 = x_159;
x_101 = x_170;
goto block_149;
}
else
{
lean_dec(x_170);
x_98 = x_163;
x_99 = lean_box(0);
x_100 = x_159;
x_101 = x_165;
goto block_149;
}
}
else
{
lean_dec(x_170);
lean_dec(x_165);
lean_dec(x_163);
lean_dec(x_159);
return x_173;
}
}
else
{
uint8_t x_175; 
lean_dec(x_159);
x_175 = !lean_is_exclusive(x_161);
if (x_175 == 0)
{
return x_161;
}
else
{
lean_object* x_176; lean_object* x_177; 
x_176 = lean_ctor_get(x_161, 0);
lean_inc(x_176);
lean_dec(x_161);
x_177 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_177, 0, x_176);
return x_177;
}
}
}
else
{
lean_dec(x_150);
lean_dec(x_55);
return x_156;
}
}
}
else
{
lean_object* x_191; uint8_t x_192; uint8_t x_193; uint8_t x_194; uint8_t x_195; uint16_t x_196; lean_object* x_197; lean_object* x_198; lean_object* x_199; lean_object* x_200; lean_object* x_201; lean_object* x_202; lean_object* x_203; lean_object* x_204; lean_object* x_253; lean_object* x_282; uint16_t x_283; lean_object* x_284; 
x_191 = lean_ctor_get(x_90, 1);
x_192 = lean_ctor_get_uint8(x_92, sizeof(void*)*3 + 2);
x_193 = lean_ctor_get_uint8(x_92, sizeof(void*)*3 + 3);
x_194 = lean_ctor_get_uint8(x_92, sizeof(void*)*3 + 4);
x_195 = lean_ctor_get_uint8(x_92, sizeof(void*)*3 + 5);
x_196 = lean_ctor_get_uint16(x_92, sizeof(void*)*3);
x_197 = lean_ctor_get(x_92, 0);
x_198 = lean_ctor_get(x_92, 1);
lean_inc(x_198);
lean_inc(x_197);
lean_dec(x_92);
x_199 = lean_unsigned_to_nat(500u);
x_200 = lean_unsigned_to_nat(1u);
x_282 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_282, 0, x_197);
lean_ctor_set(x_282, 1, x_198);
lean_ctor_set(x_282, 2, x_12);
lean_ctor_set_uint8(x_282, sizeof(void*)*3 + 2, x_192);
lean_ctor_set_uint8(x_282, sizeof(void*)*3 + 3, x_193);
lean_ctor_set_uint8(x_282, sizeof(void*)*3 + 4, x_194);
lean_ctor_set_uint8(x_282, sizeof(void*)*3 + 5, x_195);
lean_ctor_set_uint16(x_282, sizeof(void*)*3, x_196);
x_283 = lean_unbox(x_70);
lean_dec(x_70);
x_284 = lp_dasmodel_execFrames(x_282, x_283, x_199);
if (lean_obj_tag(x_284) == 0)
{
lean_object* x_285; 
x_285 = l_List_appendTR___redArg(x_87, x_191);
lean_ctor_set_tag(x_90, 1);
lean_ctor_set(x_90, 1, x_284);
lean_ctor_set(x_90, 0, x_285);
x_253 = x_90;
goto block_281;
}
else
{
lean_object* x_286; lean_object* x_287; lean_object* x_288; lean_object* x_289; lean_object* x_290; lean_object* x_291; 
lean_free_object(x_90);
x_286 = lean_ctor_get(x_284, 0);
lean_inc(x_286);
x_287 = lean_ctor_get(x_284, 1);
lean_inc(x_287);
if (lean_is_exclusive(x_284)) {
 lean_ctor_release(x_284, 0);
 lean_ctor_release(x_284, 1);
 x_288 = x_284;
} else {
 lean_dec_ref(x_284);
 x_288 = lean_box(0);
}
x_289 = l_List_appendTR___redArg(x_87, x_191);
x_290 = l_List_appendTR___redArg(x_289, x_286);
if (lean_is_scalar(x_288)) {
 x_291 = lean_alloc_ctor(1, 2, 0);
} else {
 x_291 = x_288;
}
lean_ctor_set(x_291, 0, x_290);
lean_ctor_set(x_291, 1, x_287);
x_253 = x_291;
goto block_281;
}
block_252:
{
lean_object* x_205; lean_object* x_206; lean_object* x_207; lean_object* x_208; lean_object* x_209; lean_object* x_210; lean_object* x_211; lean_object* x_212; lean_object* x_213; lean_object* x_214; lean_object* x_215; lean_object* x_216; lean_object* x_217; 
lean_inc(x_204);
x_205 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_205, 0, x_12);
lean_ctor_set(x_205, 1, x_204);
lean_ctor_set(x_205, 2, x_200);
x_206 = lean_obj_once(&lp_dasmodel_main___closed__25, &lp_dasmodel_main___closed__25_once, _init_lp_dasmodel_main___closed__25);
x_207 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg(x_203, x_201, x_205, x_206, x_12);
x_208 = lean_ctor_get(x_207, 0);
lean_inc(x_208);
lean_dec_ref(x_207);
x_209 = lean_ctor_get(x_208, 0);
lean_inc(x_209);
lean_dec(x_208);
x_210 = ((lean_object*)(lp_dasmodel_main___closed__26));
x_211 = l_Nat_reprFast(x_209);
x_212 = lean_string_append(x_210, x_211);
lean_dec_ref(x_211);
x_213 = ((lean_object*)(lp_dasmodel_main___closed__27));
x_214 = lean_string_append(x_212, x_213);
lean_inc(x_204);
x_215 = l_Nat_reprFast(x_204);
x_216 = lean_string_append(x_214, x_215);
x_217 = lp_dasmodel_IO_println___at___00main_spec__0(x_216);
if (lean_obj_tag(x_217) == 0)
{
lean_object* x_218; lean_object* x_219; 
lean_dec_ref(x_217);
x_218 = lean_obj_once(&lp_dasmodel_main___closed__28, &lp_dasmodel_main___closed__28_once, _init_lp_dasmodel_main___closed__28);
x_219 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg(x_203, x_201, x_205, x_218, x_12);
if (lean_obj_tag(x_219) == 0)
{
lean_object* x_220; lean_object* x_221; lean_object* x_222; lean_object* x_223; lean_object* x_224; lean_object* x_225; lean_object* x_226; lean_object* x_227; lean_object* x_228; 
x_220 = lean_ctor_get(x_219, 0);
lean_inc(x_220);
lean_dec_ref(x_219);
x_221 = lean_ctor_get(x_220, 1);
lean_inc(x_221);
lean_dec(x_220);
x_222 = lean_ctor_get(x_221, 0);
lean_inc(x_222);
lean_dec(x_221);
x_223 = ((lean_object*)(lp_dasmodel_main___closed__29));
x_224 = l_Nat_reprFast(x_222);
x_225 = lean_string_append(x_223, x_224);
lean_dec_ref(x_224);
x_226 = lean_string_append(x_225, x_213);
x_227 = lean_string_append(x_226, x_215);
x_228 = lp_dasmodel_IO_println___at___00main_spec__0(x_227);
if (lean_obj_tag(x_228) == 0)
{
lean_object* x_229; 
lean_dec_ref(x_228);
x_229 = l_List_get_x3fInternal___redArg(x_203, x_12);
if (lean_obj_tag(x_229) == 1)
{
lean_object* x_230; lean_object* x_231; lean_object* x_232; 
x_230 = lean_ctor_get(x_229, 0);
lean_inc(x_230);
lean_dec_ref(x_229);
x_231 = lean_ctor_get(x_230, 0);
lean_inc(x_231);
lean_dec(x_230);
x_232 = l_List_get_x3fInternal___redArg(x_201, x_12);
if (lean_obj_tag(x_232) == 1)
{
lean_object* x_233; lean_object* x_234; lean_object* x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; lean_object* x_239; uint8_t x_240; 
x_233 = lean_ctor_get(x_232, 0);
lean_inc(x_233);
lean_dec_ref(x_232);
x_234 = lean_ctor_get(x_233, 0);
lean_inc(x_234);
lean_dec(x_233);
x_235 = lean_nat_to_int(x_234);
x_236 = lean_nat_to_int(x_231);
x_237 = lean_int_sub(x_235, x_236);
lean_dec(x_236);
lean_dec(x_235);
x_238 = ((lean_object*)(lp_dasmodel_main___closed__30));
x_239 = lean_obj_once(&lp_dasmodel_main___closed__31, &lp_dasmodel_main___closed__31_once, _init_lp_dasmodel_main___closed__31);
x_240 = lean_int_dec_lt(x_237, x_239);
if (x_240 == 0)
{
lean_object* x_241; lean_object* x_242; 
x_241 = lean_nat_abs(x_237);
x_242 = l_Nat_reprFast(x_241);
x_13 = lean_box(0);
x_14 = x_238;
x_15 = x_204;
x_16 = x_201;
x_17 = x_205;
x_18 = x_213;
x_19 = x_218;
x_20 = x_237;
x_21 = x_215;
x_22 = x_203;
x_23 = x_242;
goto block_50;
}
else
{
lean_object* x_243; lean_object* x_244; lean_object* x_245; lean_object* x_246; lean_object* x_247; lean_object* x_248; 
x_243 = lean_nat_abs(x_237);
x_244 = lean_nat_sub(x_243, x_200);
lean_dec(x_243);
x_245 = ((lean_object*)(lp_dasmodel_main___closed__32));
x_246 = lean_nat_add(x_244, x_200);
lean_dec(x_244);
x_247 = l_Nat_reprFast(x_246);
x_248 = lean_string_append(x_245, x_247);
lean_dec_ref(x_247);
x_13 = lean_box(0);
x_14 = x_238;
x_15 = x_204;
x_16 = x_201;
x_17 = x_205;
x_18 = x_213;
x_19 = x_218;
x_20 = x_237;
x_21 = x_215;
x_22 = x_203;
x_23 = x_248;
goto block_50;
}
}
else
{
lean_dec(x_232);
lean_dec(x_231);
lean_dec_ref(x_215);
lean_dec_ref(x_205);
lean_dec(x_204);
lean_dec(x_203);
lean_dec(x_201);
x_2 = lean_box(0);
goto block_5;
}
}
else
{
lean_dec(x_229);
lean_dec_ref(x_215);
lean_dec_ref(x_205);
lean_dec(x_204);
lean_dec(x_203);
lean_dec(x_201);
x_2 = lean_box(0);
goto block_5;
}
}
else
{
lean_dec_ref(x_215);
lean_dec_ref(x_205);
lean_dec(x_204);
lean_dec(x_203);
lean_dec(x_201);
return x_228;
}
}
else
{
lean_object* x_249; lean_object* x_250; lean_object* x_251; 
lean_dec_ref(x_215);
lean_dec_ref(x_205);
lean_dec(x_204);
lean_dec(x_203);
lean_dec(x_201);
x_249 = lean_ctor_get(x_219, 0);
lean_inc(x_249);
if (lean_is_exclusive(x_219)) {
 lean_ctor_release(x_219, 0);
 x_250 = x_219;
} else {
 lean_dec_ref(x_219);
 x_250 = lean_box(0);
}
if (lean_is_scalar(x_250)) {
 x_251 = lean_alloc_ctor(1, 1, 0);
} else {
 x_251 = x_250;
}
lean_ctor_set(x_251, 0, x_249);
return x_251;
}
}
else
{
lean_dec_ref(x_215);
lean_dec_ref(x_205);
lean_dec(x_204);
lean_dec(x_203);
lean_dec(x_201);
return x_217;
}
}
block_281:
{
lean_object* x_254; lean_object* x_255; lean_object* x_256; lean_object* x_257; lean_object* x_258; lean_object* x_259; 
x_254 = ((lean_object*)(lp_dasmodel_main___closed__33));
x_255 = l_List_lengthTR___redArg(x_253);
x_256 = l_Nat_reprFast(x_255);
x_257 = lean_string_append(x_254, x_256);
lean_dec_ref(x_256);
x_258 = lean_string_append(x_257, x_60);
x_259 = lp_dasmodel_IO_println___at___00main_spec__0(x_258);
if (lean_obj_tag(x_259) == 0)
{
lean_object* x_260; lean_object* x_261; lean_object* x_262; lean_object* x_263; lean_object* x_264; 
lean_dec_ref(x_259);
x_260 = lean_box(0);
x_261 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg(x_253, x_260);
x_262 = lean_ctor_get(x_261, 0);
lean_inc(x_262);
lean_dec_ref(x_261);
x_263 = ((lean_object*)(lp_dasmodel_main___closed__34));
x_264 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg(x_55, x_263);
if (lean_obj_tag(x_264) == 0)
{
lean_object* x_265; lean_object* x_266; lean_object* x_267; lean_object* x_268; lean_object* x_269; lean_object* x_270; lean_object* x_271; lean_object* x_272; lean_object* x_273; lean_object* x_274; lean_object* x_275; lean_object* x_276; 
x_265 = lean_ctor_get(x_264, 0);
lean_inc(x_265);
lean_dec_ref(x_264);
x_266 = lean_ctor_get(x_265, 0);
lean_inc(x_266);
lean_dec(x_265);
x_267 = ((lean_object*)(lp_dasmodel_main___closed__35));
x_268 = l_List_lengthTR___redArg(x_262);
lean_inc(x_268);
x_269 = l_Nat_reprFast(x_268);
x_270 = lean_string_append(x_267, x_269);
lean_dec_ref(x_269);
x_271 = ((lean_object*)(lp_dasmodel_main___closed__36));
x_272 = lean_string_append(x_270, x_271);
x_273 = l_List_lengthTR___redArg(x_266);
lean_inc(x_273);
x_274 = l_Nat_reprFast(x_273);
x_275 = lean_string_append(x_272, x_274);
lean_dec_ref(x_274);
x_276 = lp_dasmodel_IO_println___at___00main_spec__0(x_275);
if (lean_obj_tag(x_276) == 0)
{
uint8_t x_277; 
lean_dec_ref(x_276);
x_277 = lean_nat_dec_le(x_268, x_273);
if (x_277 == 0)
{
lean_dec(x_268);
x_201 = x_266;
x_202 = lean_box(0);
x_203 = x_262;
x_204 = x_273;
goto block_252;
}
else
{
lean_dec(x_273);
x_201 = x_266;
x_202 = lean_box(0);
x_203 = x_262;
x_204 = x_268;
goto block_252;
}
}
else
{
lean_dec(x_273);
lean_dec(x_268);
lean_dec(x_266);
lean_dec(x_262);
return x_276;
}
}
else
{
lean_object* x_278; lean_object* x_279; lean_object* x_280; 
lean_dec(x_262);
x_278 = lean_ctor_get(x_264, 0);
lean_inc(x_278);
if (lean_is_exclusive(x_264)) {
 lean_ctor_release(x_264, 0);
 x_279 = x_264;
} else {
 lean_dec_ref(x_264);
 x_279 = lean_box(0);
}
if (lean_is_scalar(x_279)) {
 x_280 = lean_alloc_ctor(1, 1, 0);
} else {
 x_280 = x_279;
}
lean_ctor_set(x_280, 0, x_278);
return x_280;
}
}
else
{
lean_dec(x_253);
lean_dec(x_55);
return x_259;
}
}
}
}
else
{
lean_object* x_292; lean_object* x_293; uint8_t x_294; uint8_t x_295; uint8_t x_296; uint8_t x_297; uint16_t x_298; lean_object* x_299; lean_object* x_300; lean_object* x_301; lean_object* x_302; lean_object* x_303; lean_object* x_304; lean_object* x_305; lean_object* x_306; lean_object* x_307; lean_object* x_356; lean_object* x_385; uint16_t x_386; lean_object* x_387; 
x_292 = lean_ctor_get(x_90, 0);
x_293 = lean_ctor_get(x_90, 1);
lean_inc(x_293);
lean_inc(x_292);
lean_dec(x_90);
x_294 = lean_ctor_get_uint8(x_292, sizeof(void*)*3 + 2);
x_295 = lean_ctor_get_uint8(x_292, sizeof(void*)*3 + 3);
x_296 = lean_ctor_get_uint8(x_292, sizeof(void*)*3 + 4);
x_297 = lean_ctor_get_uint8(x_292, sizeof(void*)*3 + 5);
x_298 = lean_ctor_get_uint16(x_292, sizeof(void*)*3);
x_299 = lean_ctor_get(x_292, 0);
lean_inc_ref(x_299);
x_300 = lean_ctor_get(x_292, 1);
lean_inc_ref(x_300);
if (lean_is_exclusive(x_292)) {
 lean_ctor_release(x_292, 0);
 lean_ctor_release(x_292, 1);
 lean_ctor_release(x_292, 2);
 x_301 = x_292;
} else {
 lean_dec_ref(x_292);
 x_301 = lean_box(0);
}
x_302 = lean_unsigned_to_nat(500u);
x_303 = lean_unsigned_to_nat(1u);
if (lean_is_scalar(x_301)) {
 x_385 = lean_alloc_ctor(0, 3, 6);
} else {
 x_385 = x_301;
}
lean_ctor_set(x_385, 0, x_299);
lean_ctor_set(x_385, 1, x_300);
lean_ctor_set(x_385, 2, x_12);
lean_ctor_set_uint8(x_385, sizeof(void*)*3 + 2, x_294);
lean_ctor_set_uint8(x_385, sizeof(void*)*3 + 3, x_295);
lean_ctor_set_uint8(x_385, sizeof(void*)*3 + 4, x_296);
lean_ctor_set_uint8(x_385, sizeof(void*)*3 + 5, x_297);
lean_ctor_set_uint16(x_385, sizeof(void*)*3, x_298);
x_386 = lean_unbox(x_70);
lean_dec(x_70);
x_387 = lp_dasmodel_execFrames(x_385, x_386, x_302);
if (lean_obj_tag(x_387) == 0)
{
lean_object* x_388; lean_object* x_389; 
x_388 = l_List_appendTR___redArg(x_87, x_293);
x_389 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_389, 0, x_388);
lean_ctor_set(x_389, 1, x_387);
x_356 = x_389;
goto block_384;
}
else
{
lean_object* x_390; lean_object* x_391; lean_object* x_392; lean_object* x_393; lean_object* x_394; lean_object* x_395; 
x_390 = lean_ctor_get(x_387, 0);
lean_inc(x_390);
x_391 = lean_ctor_get(x_387, 1);
lean_inc(x_391);
if (lean_is_exclusive(x_387)) {
 lean_ctor_release(x_387, 0);
 lean_ctor_release(x_387, 1);
 x_392 = x_387;
} else {
 lean_dec_ref(x_387);
 x_392 = lean_box(0);
}
x_393 = l_List_appendTR___redArg(x_87, x_293);
x_394 = l_List_appendTR___redArg(x_393, x_390);
if (lean_is_scalar(x_392)) {
 x_395 = lean_alloc_ctor(1, 2, 0);
} else {
 x_395 = x_392;
}
lean_ctor_set(x_395, 0, x_394);
lean_ctor_set(x_395, 1, x_391);
x_356 = x_395;
goto block_384;
}
block_355:
{
lean_object* x_308; lean_object* x_309; lean_object* x_310; lean_object* x_311; lean_object* x_312; lean_object* x_313; lean_object* x_314; lean_object* x_315; lean_object* x_316; lean_object* x_317; lean_object* x_318; lean_object* x_319; lean_object* x_320; 
lean_inc(x_307);
x_308 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_308, 0, x_12);
lean_ctor_set(x_308, 1, x_307);
lean_ctor_set(x_308, 2, x_303);
x_309 = lean_obj_once(&lp_dasmodel_main___closed__25, &lp_dasmodel_main___closed__25_once, _init_lp_dasmodel_main___closed__25);
x_310 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg(x_306, x_304, x_308, x_309, x_12);
x_311 = lean_ctor_get(x_310, 0);
lean_inc(x_311);
lean_dec_ref(x_310);
x_312 = lean_ctor_get(x_311, 0);
lean_inc(x_312);
lean_dec(x_311);
x_313 = ((lean_object*)(lp_dasmodel_main___closed__26));
x_314 = l_Nat_reprFast(x_312);
x_315 = lean_string_append(x_313, x_314);
lean_dec_ref(x_314);
x_316 = ((lean_object*)(lp_dasmodel_main___closed__27));
x_317 = lean_string_append(x_315, x_316);
lean_inc(x_307);
x_318 = l_Nat_reprFast(x_307);
x_319 = lean_string_append(x_317, x_318);
x_320 = lp_dasmodel_IO_println___at___00main_spec__0(x_319);
if (lean_obj_tag(x_320) == 0)
{
lean_object* x_321; lean_object* x_322; 
lean_dec_ref(x_320);
x_321 = lean_obj_once(&lp_dasmodel_main___closed__28, &lp_dasmodel_main___closed__28_once, _init_lp_dasmodel_main___closed__28);
x_322 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg(x_306, x_304, x_308, x_321, x_12);
if (lean_obj_tag(x_322) == 0)
{
lean_object* x_323; lean_object* x_324; lean_object* x_325; lean_object* x_326; lean_object* x_327; lean_object* x_328; lean_object* x_329; lean_object* x_330; lean_object* x_331; 
x_323 = lean_ctor_get(x_322, 0);
lean_inc(x_323);
lean_dec_ref(x_322);
x_324 = lean_ctor_get(x_323, 1);
lean_inc(x_324);
lean_dec(x_323);
x_325 = lean_ctor_get(x_324, 0);
lean_inc(x_325);
lean_dec(x_324);
x_326 = ((lean_object*)(lp_dasmodel_main___closed__29));
x_327 = l_Nat_reprFast(x_325);
x_328 = lean_string_append(x_326, x_327);
lean_dec_ref(x_327);
x_329 = lean_string_append(x_328, x_316);
x_330 = lean_string_append(x_329, x_318);
x_331 = lp_dasmodel_IO_println___at___00main_spec__0(x_330);
if (lean_obj_tag(x_331) == 0)
{
lean_object* x_332; 
lean_dec_ref(x_331);
x_332 = l_List_get_x3fInternal___redArg(x_306, x_12);
if (lean_obj_tag(x_332) == 1)
{
lean_object* x_333; lean_object* x_334; lean_object* x_335; 
x_333 = lean_ctor_get(x_332, 0);
lean_inc(x_333);
lean_dec_ref(x_332);
x_334 = lean_ctor_get(x_333, 0);
lean_inc(x_334);
lean_dec(x_333);
x_335 = l_List_get_x3fInternal___redArg(x_304, x_12);
if (lean_obj_tag(x_335) == 1)
{
lean_object* x_336; lean_object* x_337; lean_object* x_338; lean_object* x_339; lean_object* x_340; lean_object* x_341; lean_object* x_342; uint8_t x_343; 
x_336 = lean_ctor_get(x_335, 0);
lean_inc(x_336);
lean_dec_ref(x_335);
x_337 = lean_ctor_get(x_336, 0);
lean_inc(x_337);
lean_dec(x_336);
x_338 = lean_nat_to_int(x_337);
x_339 = lean_nat_to_int(x_334);
x_340 = lean_int_sub(x_338, x_339);
lean_dec(x_339);
lean_dec(x_338);
x_341 = ((lean_object*)(lp_dasmodel_main___closed__30));
x_342 = lean_obj_once(&lp_dasmodel_main___closed__31, &lp_dasmodel_main___closed__31_once, _init_lp_dasmodel_main___closed__31);
x_343 = lean_int_dec_lt(x_340, x_342);
if (x_343 == 0)
{
lean_object* x_344; lean_object* x_345; 
x_344 = lean_nat_abs(x_340);
x_345 = l_Nat_reprFast(x_344);
x_13 = lean_box(0);
x_14 = x_341;
x_15 = x_307;
x_16 = x_304;
x_17 = x_308;
x_18 = x_316;
x_19 = x_321;
x_20 = x_340;
x_21 = x_318;
x_22 = x_306;
x_23 = x_345;
goto block_50;
}
else
{
lean_object* x_346; lean_object* x_347; lean_object* x_348; lean_object* x_349; lean_object* x_350; lean_object* x_351; 
x_346 = lean_nat_abs(x_340);
x_347 = lean_nat_sub(x_346, x_303);
lean_dec(x_346);
x_348 = ((lean_object*)(lp_dasmodel_main___closed__32));
x_349 = lean_nat_add(x_347, x_303);
lean_dec(x_347);
x_350 = l_Nat_reprFast(x_349);
x_351 = lean_string_append(x_348, x_350);
lean_dec_ref(x_350);
x_13 = lean_box(0);
x_14 = x_341;
x_15 = x_307;
x_16 = x_304;
x_17 = x_308;
x_18 = x_316;
x_19 = x_321;
x_20 = x_340;
x_21 = x_318;
x_22 = x_306;
x_23 = x_351;
goto block_50;
}
}
else
{
lean_dec(x_335);
lean_dec(x_334);
lean_dec_ref(x_318);
lean_dec_ref(x_308);
lean_dec(x_307);
lean_dec(x_306);
lean_dec(x_304);
x_2 = lean_box(0);
goto block_5;
}
}
else
{
lean_dec(x_332);
lean_dec_ref(x_318);
lean_dec_ref(x_308);
lean_dec(x_307);
lean_dec(x_306);
lean_dec(x_304);
x_2 = lean_box(0);
goto block_5;
}
}
else
{
lean_dec_ref(x_318);
lean_dec_ref(x_308);
lean_dec(x_307);
lean_dec(x_306);
lean_dec(x_304);
return x_331;
}
}
else
{
lean_object* x_352; lean_object* x_353; lean_object* x_354; 
lean_dec_ref(x_318);
lean_dec_ref(x_308);
lean_dec(x_307);
lean_dec(x_306);
lean_dec(x_304);
x_352 = lean_ctor_get(x_322, 0);
lean_inc(x_352);
if (lean_is_exclusive(x_322)) {
 lean_ctor_release(x_322, 0);
 x_353 = x_322;
} else {
 lean_dec_ref(x_322);
 x_353 = lean_box(0);
}
if (lean_is_scalar(x_353)) {
 x_354 = lean_alloc_ctor(1, 1, 0);
} else {
 x_354 = x_353;
}
lean_ctor_set(x_354, 0, x_352);
return x_354;
}
}
else
{
lean_dec_ref(x_318);
lean_dec_ref(x_308);
lean_dec(x_307);
lean_dec(x_306);
lean_dec(x_304);
return x_320;
}
}
block_384:
{
lean_object* x_357; lean_object* x_358; lean_object* x_359; lean_object* x_360; lean_object* x_361; lean_object* x_362; 
x_357 = ((lean_object*)(lp_dasmodel_main___closed__33));
x_358 = l_List_lengthTR___redArg(x_356);
x_359 = l_Nat_reprFast(x_358);
x_360 = lean_string_append(x_357, x_359);
lean_dec_ref(x_359);
x_361 = lean_string_append(x_360, x_60);
x_362 = lp_dasmodel_IO_println___at___00main_spec__0(x_361);
if (lean_obj_tag(x_362) == 0)
{
lean_object* x_363; lean_object* x_364; lean_object* x_365; lean_object* x_366; lean_object* x_367; 
lean_dec_ref(x_362);
x_363 = lean_box(0);
x_364 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg(x_356, x_363);
x_365 = lean_ctor_get(x_364, 0);
lean_inc(x_365);
lean_dec_ref(x_364);
x_366 = ((lean_object*)(lp_dasmodel_main___closed__34));
x_367 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg(x_55, x_366);
if (lean_obj_tag(x_367) == 0)
{
lean_object* x_368; lean_object* x_369; lean_object* x_370; lean_object* x_371; lean_object* x_372; lean_object* x_373; lean_object* x_374; lean_object* x_375; lean_object* x_376; lean_object* x_377; lean_object* x_378; lean_object* x_379; 
x_368 = lean_ctor_get(x_367, 0);
lean_inc(x_368);
lean_dec_ref(x_367);
x_369 = lean_ctor_get(x_368, 0);
lean_inc(x_369);
lean_dec(x_368);
x_370 = ((lean_object*)(lp_dasmodel_main___closed__35));
x_371 = l_List_lengthTR___redArg(x_365);
lean_inc(x_371);
x_372 = l_Nat_reprFast(x_371);
x_373 = lean_string_append(x_370, x_372);
lean_dec_ref(x_372);
x_374 = ((lean_object*)(lp_dasmodel_main___closed__36));
x_375 = lean_string_append(x_373, x_374);
x_376 = l_List_lengthTR___redArg(x_369);
lean_inc(x_376);
x_377 = l_Nat_reprFast(x_376);
x_378 = lean_string_append(x_375, x_377);
lean_dec_ref(x_377);
x_379 = lp_dasmodel_IO_println___at___00main_spec__0(x_378);
if (lean_obj_tag(x_379) == 0)
{
uint8_t x_380; 
lean_dec_ref(x_379);
x_380 = lean_nat_dec_le(x_371, x_376);
if (x_380 == 0)
{
lean_dec(x_371);
x_304 = x_369;
x_305 = lean_box(0);
x_306 = x_365;
x_307 = x_376;
goto block_355;
}
else
{
lean_dec(x_376);
x_304 = x_369;
x_305 = lean_box(0);
x_306 = x_365;
x_307 = x_371;
goto block_355;
}
}
else
{
lean_dec(x_376);
lean_dec(x_371);
lean_dec(x_369);
lean_dec(x_365);
return x_379;
}
}
else
{
lean_object* x_381; lean_object* x_382; lean_object* x_383; 
lean_dec(x_365);
x_381 = lean_ctor_get(x_367, 0);
lean_inc(x_381);
if (lean_is_exclusive(x_367)) {
 lean_ctor_release(x_367, 0);
 x_382 = x_367;
} else {
 lean_dec_ref(x_367);
 x_382 = lean_box(0);
}
if (lean_is_scalar(x_382)) {
 x_383 = lean_alloc_ctor(1, 1, 0);
} else {
 x_383 = x_382;
}
lean_ctor_set(x_383, 0, x_381);
return x_383;
}
}
else
{
lean_dec(x_356);
lean_dec(x_55);
return x_362;
}
}
}
}
else
{
lean_dec(x_70);
lean_dec(x_69);
lean_dec(x_68);
lean_dec(x_55);
return x_82;
}
}
}
else
{
lean_dec(x_55);
lean_dec(x_8);
return x_62;
}
}
else
{
uint8_t x_396; 
lean_dec(x_8);
x_396 = !lean_is_exclusive(x_52);
if (x_396 == 0)
{
return x_52;
}
else
{
lean_object* x_397; lean_object* x_398; 
x_397 = lean_ctor_get(x_52, 0);
lean_inc(x_397);
lean_dec(x_52);
x_398 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_398, 0, x_397);
return x_398;
}
}
block_50:
{
lean_object* x_24; lean_object* x_25; 
x_24 = lean_string_append(x_14, x_23);
x_25 = lp_dasmodel_IO_println___at___00main_spec__0(x_24);
if (lean_obj_tag(x_25) == 0)
{
lean_object* x_26; 
lean_dec_ref(x_25);
x_26 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg(x_22, x_16, x_20, x_23, x_17, x_19, x_12);
lean_dec_ref(x_17);
lean_dec_ref(x_23);
lean_dec(x_20);
lean_dec(x_16);
lean_dec(x_22);
if (lean_obj_tag(x_26) == 0)
{
lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; 
x_27 = lean_ctor_get(x_26, 0);
lean_inc(x_27);
lean_dec_ref(x_26);
x_28 = lean_ctor_get(x_27, 1);
lean_inc(x_28);
lean_dec(x_27);
x_29 = lean_ctor_get(x_28, 0);
lean_inc(x_29);
lean_dec(x_28);
x_30 = ((lean_object*)(lp_dasmodel_main___closed__16));
lean_inc(x_29);
x_31 = l_Nat_reprFast(x_29);
x_32 = lean_string_append(x_30, x_31);
lean_dec_ref(x_31);
x_33 = lean_string_append(x_32, x_18);
lean_dec_ref(x_18);
x_34 = lean_string_append(x_33, x_21);
lean_dec_ref(x_21);
x_35 = lp_dasmodel_IO_println___at___00main_spec__0(x_34);
if (lean_obj_tag(x_35) == 0)
{
uint8_t x_36; 
x_36 = !lean_is_exclusive(x_35);
if (x_36 == 0)
{
lean_object* x_37; uint8_t x_38; 
x_37 = lean_ctor_get(x_35, 0);
lean_dec(x_37);
x_38 = lean_nat_dec_eq(x_29, x_15);
lean_dec(x_15);
lean_dec(x_29);
if (x_38 == 0)
{
lean_object* x_39; 
x_39 = lean_box(0);
lean_ctor_set(x_35, 0, x_39);
return x_35;
}
else
{
lean_object* x_40; lean_object* x_41; 
lean_free_object(x_35);
x_40 = ((lean_object*)(lp_dasmodel_main___closed__17));
x_41 = lp_dasmodel_IO_println___at___00main_spec__0(x_40);
return x_41;
}
}
else
{
uint8_t x_42; 
lean_dec(x_35);
x_42 = lean_nat_dec_eq(x_29, x_15);
lean_dec(x_15);
lean_dec(x_29);
if (x_42 == 0)
{
lean_object* x_43; lean_object* x_44; 
x_43 = lean_box(0);
x_44 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_44, 0, x_43);
return x_44;
}
else
{
lean_object* x_45; lean_object* x_46; 
x_45 = ((lean_object*)(lp_dasmodel_main___closed__17));
x_46 = lp_dasmodel_IO_println___at___00main_spec__0(x_45);
return x_46;
}
}
}
else
{
lean_dec(x_29);
lean_dec(x_15);
return x_35;
}
}
else
{
uint8_t x_47; 
lean_dec_ref(x_21);
lean_dec_ref(x_18);
lean_dec(x_15);
x_47 = !lean_is_exclusive(x_26);
if (x_47 == 0)
{
return x_26;
}
else
{
lean_object* x_48; lean_object* x_49; 
x_48 = lean_ctor_get(x_26, 0);
lean_inc(x_48);
lean_dec(x_26);
x_49 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_49, 0, x_48);
return x_49;
}
}
}
else
{
lean_dec_ref(x_23);
lean_dec(x_22);
lean_dec_ref(x_21);
lean_dec(x_20);
lean_dec_ref(x_19);
lean_dec_ref(x_18);
lean_dec_ref(x_17);
lean_dec(x_16);
lean_dec(x_15);
return x_25;
}
}
}
else
{
lean_dec(x_8);
return x_10;
}
}
else
{
uint8_t x_399; 
x_399 = !lean_is_exclusive(x_7);
if (x_399 == 0)
{
return x_7;
}
else
{
lean_object* x_400; lean_object* x_401; 
x_400 = lean_ctor_get(x_7, 0);
lean_inc(x_400);
lean_dec(x_7);
x_401 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_401, 0, x_400);
return x_401;
}
}
block_5:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_box(0);
x_4 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_4, 0, x_3);
return x_4;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_main___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = _lean_main();
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___redArg(x_1, x_3, x_4);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__1(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___redArg(x_2, x_3);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__2(x_1, x_2, x_3, x_4);
lean_dec(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___redArg(x_2, x_3);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__3(x_1, x_2, x_3, x_4);
lean_dec(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___redArg(x_2, x_3);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_List_forIn_x27_loop___at___00main_spec__4(x_1, x_2, x_3, x_4);
lean_dec(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___redArg(x_1, x_2, x_3, x_4, x_5);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__5(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___redArg(x_1, x_2, x_3, x_4, x_5);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__6(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8, lean_object* x_9) {
_start:
{
lean_object* x_11; 
x_11 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___redArg(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
return x_11;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8, lean_object* x_9, lean_object* x_10) {
_start:
{
lean_object* x_11; 
x_11 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__7(x_1, x_2, x_3, x_4, x_5, x_6, x_7, x_8, x_9);
lean_dec_ref(x_5);
lean_dec_ref(x_4);
lean_dec(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_11;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_CPU6502(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_ValidateModel(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_CPU6502(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
char ** lean_setup_args(int argc, char ** argv);
void lean_initialize_runtime_module();

  #if defined(WIN32) || defined(_WIN32)
  #include <windows.h>
  #endif

  int main(int argc, char ** argv) {
  #if defined(WIN32) || defined(_WIN32)
  SetErrorMode(SEM_FAILCRITICALERRORS);
  SetConsoleOutputCP(CP_UTF8);
  #endif
  lean_object* in; lean_object* res;
argv = lean_setup_args(argc, argv);
lean_initialize_runtime_module();
lean_set_panic_messages(false);
res = initialize_dasmodel_ValidateModel(1 /* builtin */);
lean_set_panic_messages(true);
lean_io_mark_end_initialization();
if (lean_io_result_is_ok(res)) {
lean_dec_ref(res);
lean_init_task_manager();
res = _lean_main();
}
lean_finalize_task_manager();
if (lean_io_result_is_ok(res)) {
  int ret = 0;
  lean_dec_ref(res);
  return ret;
} else {
  lean_io_result_show_error(res);
  lean_dec_ref(res);
  return 1;
}
}
#ifdef __cplusplus
}
#endif
