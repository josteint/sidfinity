// Lean compiler output
// Module: CompareMain
// Imports: public import Init public import CPU6502 public import Codegen
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
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "=$"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__0 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__0_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "V"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__1 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__1_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "flo"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__2 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__2_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "fhi"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__3 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__3_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "plo"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__4 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__4_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "phi"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__5 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__5_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "ctl"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__6 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__6_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "ad"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__7 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__7_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "sr"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__8 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__8_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "Flo"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__9 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__9_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "Fhi"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__10 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__10_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "Fctl"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__11 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__11_value;
static const lean_string_object lp_dasmodel_cmpShowWrite___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "Vol"};
static const lean_object* lp_dasmodel_cmpShowWrite___closed__12 = (const lean_object*)&lp_dasmodel_cmpShowWrite___closed__12_value;
lean_object* lean_string_append(lean_object*, lean_object*);
lean_object* l_Nat_reprFast(lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_cmpShowWrite(lean_object*);
lean_object* l_List_reverse___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00cmpShowFrame_spec__0(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_cmpShowFrame___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = " "};
static const lean_object* lp_dasmodel_cmpShowFrame___closed__0 = (const lean_object*)&lp_dasmodel_cmpShowFrame___closed__0_value;
lean_object* l_String_intercalate(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_cmpShowFrame(lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel_writeEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_writeEq___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel_frameEq___lam__0(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_frameEq___lam__0___boxed(lean_object*);
static const lean_closure_object lp_dasmodel_frameEq___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_frameEq___lam__0___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_frameEq___closed__0 = (const lean_object*)&lp_dasmodel_frameEq___closed__0_value;
lean_object* l_List_lengthTR___redArg(lean_object*);
lean_object* l_List_zipWith___at___00List_zip_spec__0___redArg(lean_object*, lean_object*);
uint8_t l_List_all___redArg(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel_frameEq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_frameEq___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "F"};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__0 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__0_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = ": ORIG("};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__1 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__1_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = ") "};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__2 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__2_value;
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
static lean_once_cell_t lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__3;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "     LEAN("};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__4 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__4_value;
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
lean_object* l_List_get_x3fInternal___redArg(lean_object*, lean_object*);
lean_object* l___private_Init_Data_List_Impl_0__List_takeTR_go___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lp_dasmodel_IO_println___at___00commandoMain_spec__0(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_main___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 57, .m_capacity = 57, .m_length = 56, .m_data = "../../data/C64Music/MUSICIANS/H/Hubbard_Rob/Commando.sid"};
static const lean_object* lp_dasmodel_main___closed__0 = (const lean_object*)&lp_dasmodel_main___closed__0_value;
static const lean_string_object lp_dasmodel_main___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 11, .m_capacity = 11, .m_length = 10, .m_data = "Original: "};
static const lean_object* lp_dasmodel_main___closed__1 = (const lean_object*)&lp_dasmodel_main___closed__1_value;
static const lean_string_object lp_dasmodel_main___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = " bytes"};
static const lean_object* lp_dasmodel_main___closed__2 = (const lean_object*)&lp_dasmodel_main___closed__2_value;
extern lean_object* lp_dasmodel_commandoSong;
lean_object* lp_dasmodel_generateSID___redArg(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__3;
lean_object* lean_byte_array_mk(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__4;
static const lean_string_object lp_dasmodel_main___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "Generated: "};
static const lean_object* lp_dasmodel_main___closed__5 = (const lean_object*)&lp_dasmodel_main___closed__5_value;
lean_object* lean_byte_array_size(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__6;
static lean_once_cell_t lp_dasmodel_main___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__7;
static lean_once_cell_t lp_dasmodel_main___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__8;
static lean_once_cell_t lp_dasmodel_main___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__9;
static const lean_string_object lp_dasmodel_main___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = "Failed to load SIDs"};
static const lean_object* lp_dasmodel_main___closed__10 = (const lean_object*)&lp_dasmodel_main___closed__10_value;
lean_object* lp_dasmodel_loadSID(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__11;
static const lean_string_object lp_dasmodel_main___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 18, .m_capacity = 18, .m_length = 17, .m_data = "Original:  init=$"};
static const lean_object* lp_dasmodel_main___closed__12 = (const lean_object*)&lp_dasmodel_main___closed__12_value;
static const lean_string_object lp_dasmodel_main___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = " play=$"};
static const lean_object* lp_dasmodel_main___closed__13 = (const lean_object*)&lp_dasmodel_main___closed__13_value;
static const lean_string_object lp_dasmodel_main___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 18, .m_capacity = 18, .m_length = 17, .m_data = "Generated: init=$"};
static const lean_object* lp_dasmodel_main___closed__14 = (const lean_object*)&lp_dasmodel_main___closed__14_value;
static const lean_string_object lp_dasmodel_main___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "Original init: "};
static const lean_object* lp_dasmodel_main___closed__15 = (const lean_object*)&lp_dasmodel_main___closed__15_value;
static const lean_string_object lp_dasmodel_main___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = " writes, PC after=$"};
static const lean_object* lp_dasmodel_main___closed__16 = (const lean_object*)&lp_dasmodel_main___closed__16_value;
static const lean_string_object lp_dasmodel_main___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 17, .m_capacity = 17, .m_length = 16, .m_data = "Generated init: "};
static const lean_object* lp_dasmodel_main___closed__17 = (const lean_object*)&lp_dasmodel_main___closed__17_value;
static const lean_string_object lp_dasmodel_main___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 23, .m_capacity = 23, .m_length = 22, .m_data = "Original play[0..3]: $"};
static const lean_object* lp_dasmodel_main___closed__18 = (const lean_object*)&lp_dasmodel_main___closed__18_value;
static const lean_string_object lp_dasmodel_main___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " $"};
static const lean_object* lp_dasmodel_main___closed__19 = (const lean_object*)&lp_dasmodel_main___closed__19_value;
static const lean_string_object lp_dasmodel_main___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "Original F0: "};
static const lean_object* lp_dasmodel_main___closed__20 = (const lean_object*)&lp_dasmodel_main___closed__20_value;
static const lean_string_object lp_dasmodel_main___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = " SP=$"};
static const lean_object* lp_dasmodel_main___closed__21 = (const lean_object*)&lp_dasmodel_main___closed__21_value;
static const lean_string_object lp_dasmodel_main___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 20, .m_capacity = 20, .m_length = 19, .m_data = "  Halted at opcode="};
static const lean_object* lp_dasmodel_main___closed__22 = (const lean_object*)&lp_dasmodel_main___closed__22_value;
static const lean_string_object lp_dasmodel_main___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 1, .m_capacity = 1, .m_length = 0, .m_data = ""};
static const lean_object* lp_dasmodel_main___closed__23 = (const lean_object*)&lp_dasmodel_main___closed__23_value;
static const lean_string_object lp_dasmodel_main___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "Match: "};
static const lean_object* lp_dasmodel_main___closed__24 = (const lean_object*)&lp_dasmodel_main___closed__24_value;
static const lean_string_object lp_dasmodel_main___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "/"};
static const lean_object* lp_dasmodel_main___closed__25 = (const lean_object*)&lp_dasmodel_main___closed__25_value;
static const lean_string_object lp_dasmodel_main___closed__26_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " ("};
static const lean_object* lp_dasmodel_main___closed__26 = (const lean_object*)&lp_dasmodel_main___closed__26_value;
static const lean_string_object lp_dasmodel_main___closed__27_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "%)"};
static const lean_object* lp_dasmodel_main___closed__27 = (const lean_object*)&lp_dasmodel_main___closed__27_value;
static const lean_string_object lp_dasmodel_main___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "  First write: "};
static const lean_object* lp_dasmodel_main___closed__28 = (const lean_object*)&lp_dasmodel_main___closed__28_value;
lean_object* l_IO_FS_readBinFile(lean_object*);
lean_object* lean_uint16_to_nat(uint16_t);
lean_object* lp_dasmodel_execInit(lean_object*, uint16_t, uint8_t);
uint8_t lp_dasmodel_CPU_read(lean_object*, uint16_t);
lean_object* lean_uint8_to_nat(uint8_t);
uint16_t lean_uint16_add(uint16_t, uint16_t);
lean_object* lp_dasmodel_execCall(lean_object*, uint16_t);
lean_object* lean_nat_mul(lean_object*, lean_object*);
lean_object* lean_nat_div(lean_object*, lean_object*);
lean_object* lp_dasmodel_execFrames(lean_object*, uint16_t, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
LEAN_EXPORT lean_object* _lean_main();
LEAN_EXPORT lean_object* lp_dasmodel_main___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_cmpShowWrite(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_2 = lean_ctor_get(x_1, 0);
lean_inc(x_2);
x_3 = lean_ctor_get(x_1, 1);
lean_inc(x_3);
lean_dec_ref(x_1);
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_10 = lean_ctor_get(x_2, 0);
lean_inc(x_10);
lean_dec_ref(x_2);
x_11 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__1));
x_12 = lean_unsigned_to_nat(1u);
x_13 = lean_nat_add(x_10, x_12);
lean_dec(x_10);
x_14 = l_Nat_reprFast(x_13);
x_15 = lean_string_append(x_11, x_14);
lean_dec_ref(x_14);
x_16 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__2));
x_17 = lean_string_append(x_15, x_16);
x_4 = x_17;
goto block_9;
}
case 1:
{
lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_18 = lean_ctor_get(x_2, 0);
lean_inc(x_18);
lean_dec_ref(x_2);
x_19 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__1));
x_20 = lean_unsigned_to_nat(1u);
x_21 = lean_nat_add(x_18, x_20);
lean_dec(x_18);
x_22 = l_Nat_reprFast(x_21);
x_23 = lean_string_append(x_19, x_22);
lean_dec_ref(x_22);
x_24 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__3));
x_25 = lean_string_append(x_23, x_24);
x_4 = x_25;
goto block_9;
}
case 2:
{
lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; 
x_26 = lean_ctor_get(x_2, 0);
lean_inc(x_26);
lean_dec_ref(x_2);
x_27 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__1));
x_28 = lean_unsigned_to_nat(1u);
x_29 = lean_nat_add(x_26, x_28);
lean_dec(x_26);
x_30 = l_Nat_reprFast(x_29);
x_31 = lean_string_append(x_27, x_30);
lean_dec_ref(x_30);
x_32 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__4));
x_33 = lean_string_append(x_31, x_32);
x_4 = x_33;
goto block_9;
}
case 3:
{
lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; 
x_34 = lean_ctor_get(x_2, 0);
lean_inc(x_34);
lean_dec_ref(x_2);
x_35 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__1));
x_36 = lean_unsigned_to_nat(1u);
x_37 = lean_nat_add(x_34, x_36);
lean_dec(x_34);
x_38 = l_Nat_reprFast(x_37);
x_39 = lean_string_append(x_35, x_38);
lean_dec_ref(x_38);
x_40 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__5));
x_41 = lean_string_append(x_39, x_40);
x_4 = x_41;
goto block_9;
}
case 4:
{
lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; 
x_42 = lean_ctor_get(x_2, 0);
lean_inc(x_42);
lean_dec_ref(x_2);
x_43 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__1));
x_44 = lean_unsigned_to_nat(1u);
x_45 = lean_nat_add(x_42, x_44);
lean_dec(x_42);
x_46 = l_Nat_reprFast(x_45);
x_47 = lean_string_append(x_43, x_46);
lean_dec_ref(x_46);
x_48 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__6));
x_49 = lean_string_append(x_47, x_48);
x_4 = x_49;
goto block_9;
}
case 5:
{
lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; 
x_50 = lean_ctor_get(x_2, 0);
lean_inc(x_50);
lean_dec_ref(x_2);
x_51 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__1));
x_52 = lean_unsigned_to_nat(1u);
x_53 = lean_nat_add(x_50, x_52);
lean_dec(x_50);
x_54 = l_Nat_reprFast(x_53);
x_55 = lean_string_append(x_51, x_54);
lean_dec_ref(x_54);
x_56 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__7));
x_57 = lean_string_append(x_55, x_56);
x_4 = x_57;
goto block_9;
}
case 6:
{
lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; 
x_58 = lean_ctor_get(x_2, 0);
lean_inc(x_58);
lean_dec_ref(x_2);
x_59 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__1));
x_60 = lean_unsigned_to_nat(1u);
x_61 = lean_nat_add(x_58, x_60);
lean_dec(x_58);
x_62 = l_Nat_reprFast(x_61);
x_63 = lean_string_append(x_59, x_62);
lean_dec_ref(x_62);
x_64 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__8));
x_65 = lean_string_append(x_63, x_64);
x_4 = x_65;
goto block_9;
}
case 7:
{
lean_object* x_66; 
x_66 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__9));
x_4 = x_66;
goto block_9;
}
case 8:
{
lean_object* x_67; 
x_67 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__10));
x_4 = x_67;
goto block_9;
}
case 9:
{
lean_object* x_68; 
x_68 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__11));
x_4 = x_68;
goto block_9;
}
default: 
{
lean_object* x_69; 
x_69 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__12));
x_4 = x_69;
goto block_9;
}
}
block_9:
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_5 = ((lean_object*)(lp_dasmodel_cmpShowWrite___closed__0));
x_6 = lean_string_append(x_4, x_5);
x_7 = l_Nat_reprFast(x_3);
x_8 = lean_string_append(x_6, x_7);
lean_dec_ref(x_7);
return x_8;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00cmpShowFrame_spec__0(lean_object* x_1, lean_object* x_2) {
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
x_7 = lp_dasmodel_cmpShowWrite(x_5);
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
x_11 = lp_dasmodel_cmpShowWrite(x_9);
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
LEAN_EXPORT lean_object* lp_dasmodel_cmpShowFrame(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_2 = ((lean_object*)(lp_dasmodel_cmpShowFrame___closed__0));
x_3 = lean_box(0);
x_4 = lp_dasmodel_List_mapTR_loop___at___00cmpShowFrame_spec__0(x_1, x_3);
x_5 = l_String_intercalate(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT uint8_t lp_dasmodel_writeEq(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_8; lean_object* x_9; 
x_3 = lean_ctor_get(x_1, 0);
x_4 = lean_ctor_get(x_1, 1);
switch (lean_obj_tag(x_3)) {
case 0:
{
lean_object* x_14; 
x_14 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_14) == 0)
{
lean_object* x_15; lean_object* x_16; 
x_15 = lean_ctor_get(x_3, 0);
x_16 = lean_ctor_get(x_14, 0);
x_8 = x_15;
x_9 = x_16;
goto block_13;
}
else
{
uint8_t x_17; 
x_17 = 0;
return x_17;
}
}
case 1:
{
lean_object* x_18; 
x_18 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_18) == 1)
{
lean_object* x_19; lean_object* x_20; 
x_19 = lean_ctor_get(x_3, 0);
x_20 = lean_ctor_get(x_18, 0);
x_8 = x_19;
x_9 = x_20;
goto block_13;
}
else
{
uint8_t x_21; 
x_21 = 0;
return x_21;
}
}
case 2:
{
lean_object* x_22; 
x_22 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_22) == 2)
{
lean_object* x_23; lean_object* x_24; 
x_23 = lean_ctor_get(x_3, 0);
x_24 = lean_ctor_get(x_22, 0);
x_8 = x_23;
x_9 = x_24;
goto block_13;
}
else
{
uint8_t x_25; 
x_25 = 0;
return x_25;
}
}
case 3:
{
lean_object* x_26; 
x_26 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_26) == 3)
{
lean_object* x_27; lean_object* x_28; 
x_27 = lean_ctor_get(x_3, 0);
x_28 = lean_ctor_get(x_26, 0);
x_8 = x_27;
x_9 = x_28;
goto block_13;
}
else
{
uint8_t x_29; 
x_29 = 0;
return x_29;
}
}
case 4:
{
lean_object* x_30; 
x_30 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_30) == 4)
{
lean_object* x_31; lean_object* x_32; 
x_31 = lean_ctor_get(x_3, 0);
x_32 = lean_ctor_get(x_30, 0);
x_8 = x_31;
x_9 = x_32;
goto block_13;
}
else
{
uint8_t x_33; 
x_33 = 0;
return x_33;
}
}
case 5:
{
lean_object* x_34; 
x_34 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_34) == 5)
{
lean_object* x_35; lean_object* x_36; 
x_35 = lean_ctor_get(x_3, 0);
x_36 = lean_ctor_get(x_34, 0);
x_8 = x_35;
x_9 = x_36;
goto block_13;
}
else
{
uint8_t x_37; 
x_37 = 0;
return x_37;
}
}
case 6:
{
lean_object* x_38; 
x_38 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_38) == 6)
{
lean_object* x_39; lean_object* x_40; 
x_39 = lean_ctor_get(x_3, 0);
x_40 = lean_ctor_get(x_38, 0);
x_8 = x_39;
x_9 = x_40;
goto block_13;
}
else
{
uint8_t x_41; 
x_41 = 0;
return x_41;
}
}
case 7:
{
lean_object* x_42; 
x_42 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_42) == 7)
{
goto block_7;
}
else
{
uint8_t x_43; 
x_43 = 0;
return x_43;
}
}
case 8:
{
lean_object* x_44; 
x_44 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_44) == 8)
{
goto block_7;
}
else
{
uint8_t x_45; 
x_45 = 0;
return x_45;
}
}
case 9:
{
lean_object* x_46; 
x_46 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_46) == 9)
{
goto block_7;
}
else
{
uint8_t x_47; 
x_47 = 0;
return x_47;
}
}
default: 
{
lean_object* x_48; 
x_48 = lean_ctor_get(x_2, 0);
if (lean_obj_tag(x_48) == 10)
{
goto block_7;
}
else
{
uint8_t x_49; 
x_49 = 0;
return x_49;
}
}
}
block_7:
{
lean_object* x_5; uint8_t x_6; 
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_nat_dec_eq(x_4, x_5);
return x_6;
}
block_13:
{
uint8_t x_10; 
x_10 = lean_nat_dec_eq(x_8, x_9);
if (x_10 == 0)
{
return x_10;
}
else
{
lean_object* x_11; uint8_t x_12; 
x_11 = lean_ctor_get(x_2, 1);
x_12 = lean_nat_dec_eq(x_4, x_11);
return x_12;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_writeEq___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lp_dasmodel_writeEq(x_1, x_2);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
x_4 = lean_box(x_3);
return x_4;
}
}
LEAN_EXPORT uint8_t lp_dasmodel_frameEq___lam__0(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; uint8_t x_4; 
x_2 = lean_ctor_get(x_1, 0);
x_3 = lean_ctor_get(x_1, 1);
x_4 = lp_dasmodel_writeEq(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_frameEq___lam__0___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lp_dasmodel_frameEq___lam__0(x_1);
lean_dec_ref(x_1);
x_3 = lean_box(x_2);
return x_3;
}
}
LEAN_EXPORT uint8_t lp_dasmodel_frameEq(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; uint8_t x_5; 
x_3 = l_List_lengthTR___redArg(x_1);
x_4 = l_List_lengthTR___redArg(x_2);
x_5 = lean_nat_dec_eq(x_3, x_4);
lean_dec(x_4);
lean_dec(x_3);
if (x_5 == 0)
{
lean_dec(x_2);
lean_dec(x_1);
return x_5;
}
else
{
lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_6 = ((lean_object*)(lp_dasmodel_frameEq___closed__0));
x_7 = l_List_zipWith___at___00List_zip_spec__0___redArg(x_1, x_2);
x_8 = l_List_all___redArg(x_7, x_6);
return x_8;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_frameEq___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lp_dasmodel_frameEq(x_1, x_2);
x_4 = lean_box(x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__3(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
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
lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_22; 
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
lean_inc(x_5);
x_22 = l_List_get_x3fInternal___redArg(x_1, x_5);
if (lean_obj_tag(x_22) == 1)
{
lean_object* x_23; lean_object* x_24; 
x_23 = lean_ctor_get(x_22, 0);
lean_inc(x_23);
lean_dec_ref(x_22);
lean_inc(x_5);
x_24 = l_List_get_x3fInternal___redArg(x_2, x_5);
if (lean_obj_tag(x_24) == 1)
{
lean_object* x_25; lean_object* x_26; uint8_t x_27; 
lean_dec(x_18);
x_25 = lean_ctor_get(x_24, 0);
lean_inc(x_25);
lean_dec_ref(x_24);
x_26 = lean_unsigned_to_nat(1u);
lean_inc(x_25);
lean_inc(x_23);
x_27 = lp_dasmodel_frameEq(x_23, x_25);
if (x_27 == 0)
{
lean_object* x_28; uint8_t x_29; 
x_28 = lean_unsigned_to_nat(8u);
x_29 = lean_nat_dec_lt(x_16, x_28);
if (x_29 == 0)
{
lean_object* x_30; 
lean_dec(x_25);
lean_dec(x_23);
x_30 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_30, 0, x_16);
lean_ctor_set(x_30, 1, x_17);
x_9 = x_30;
x_10 = lean_box(0);
goto block_13;
}
else
{
lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; 
x_31 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__0));
lean_inc(x_5);
x_32 = l_Nat_reprFast(x_5);
x_33 = lean_string_append(x_31, x_32);
lean_dec_ref(x_32);
x_34 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__1));
x_35 = lean_string_append(x_33, x_34);
x_36 = l_List_lengthTR___redArg(x_23);
x_37 = l_Nat_reprFast(x_36);
x_38 = lean_string_append(x_35, x_37);
lean_dec_ref(x_37);
x_39 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__2));
x_40 = lean_string_append(x_38, x_39);
x_41 = lean_obj_once(&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__3, &lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__3_once, _init_lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__3);
lean_inc(x_23);
x_42 = l___private_Init_Data_List_Impl_0__List_takeTR_go___redArg(x_23, x_23, x_28, x_41);
lean_dec(x_23);
x_43 = lp_dasmodel_cmpShowFrame(x_42);
x_44 = lean_string_append(x_40, x_43);
lean_dec_ref(x_43);
x_45 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_44);
if (lean_obj_tag(x_45) == 0)
{
lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; 
lean_dec_ref(x_45);
x_46 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___closed__4));
x_47 = l_List_lengthTR___redArg(x_25);
x_48 = l_Nat_reprFast(x_47);
x_49 = lean_string_append(x_46, x_48);
lean_dec_ref(x_48);
x_50 = lean_string_append(x_49, x_39);
lean_inc(x_25);
x_51 = l___private_Init_Data_List_Impl_0__List_takeTR_go___redArg(x_25, x_25, x_28, x_41);
lean_dec(x_25);
x_52 = lp_dasmodel_cmpShowFrame(x_51);
x_53 = lean_string_append(x_50, x_52);
lean_dec_ref(x_52);
x_54 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_53);
if (lean_obj_tag(x_54) == 0)
{
lean_object* x_55; lean_object* x_56; 
lean_dec_ref(x_54);
x_55 = lean_nat_add(x_16, x_26);
lean_dec(x_16);
x_56 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_56, 0, x_55);
lean_ctor_set(x_56, 1, x_17);
x_9 = x_56;
x_10 = lean_box(0);
goto block_13;
}
else
{
uint8_t x_57; 
lean_dec(x_17);
lean_dec(x_16);
lean_dec(x_5);
x_57 = !lean_is_exclusive(x_54);
if (x_57 == 0)
{
return x_54;
}
else
{
lean_object* x_58; lean_object* x_59; 
x_58 = lean_ctor_get(x_54, 0);
lean_inc(x_58);
lean_dec(x_54);
x_59 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_59, 0, x_58);
return x_59;
}
}
}
else
{
uint8_t x_60; 
lean_dec(x_25);
lean_dec(x_17);
lean_dec(x_16);
lean_dec(x_5);
x_60 = !lean_is_exclusive(x_45);
if (x_60 == 0)
{
return x_45;
}
else
{
lean_object* x_61; lean_object* x_62; 
x_61 = lean_ctor_get(x_45, 0);
lean_inc(x_61);
lean_dec(x_45);
x_62 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_62, 0, x_61);
return x_62;
}
}
}
}
else
{
lean_object* x_63; lean_object* x_64; 
lean_dec(x_25);
lean_dec(x_23);
x_63 = lean_nat_add(x_17, x_26);
lean_dec(x_17);
x_64 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_64, 0, x_16);
lean_ctor_set(x_64, 1, x_63);
x_9 = x_64;
x_10 = lean_box(0);
goto block_13;
}
}
else
{
lean_dec(x_24);
lean_dec(x_23);
x_19 = lean_box(0);
goto block_21;
}
}
else
{
lean_dec(x_22);
x_19 = lean_box(0);
goto block_21;
}
block_21:
{
lean_object* x_20; 
if (lean_is_scalar(x_18)) {
 x_20 = lean_alloc_ctor(0, 2, 0);
} else {
 x_20 = x_18;
}
lean_ctor_set(x_20, 0, x_16);
lean_ctor_set(x_20, 1, x_17);
x_9 = x_20;
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
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_7;
}
}
static lean_object* _init_lp_dasmodel_main___closed__3(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lp_dasmodel_commandoSong;
x_2 = lp_dasmodel_generateSID___redArg(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__4(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__3, &lp_dasmodel_main___closed__3_once, _init_lp_dasmodel_main___closed__3);
x_2 = lean_byte_array_mk(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__6(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__4, &lp_dasmodel_main___closed__4_once, _init_lp_dasmodel_main___closed__4);
x_2 = lean_byte_array_size(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__6, &lp_dasmodel_main___closed__6_once, _init_lp_dasmodel_main___closed__6);
x_2 = l_Nat_reprFast(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__8(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__7, &lp_dasmodel_main___closed__7_once, _init_lp_dasmodel_main___closed__7);
x_2 = ((lean_object*)(lp_dasmodel_main___closed__5));
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__9(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_main___closed__2));
x_2 = lean_obj_once(&lp_dasmodel_main___closed__8, &lp_dasmodel_main___closed__8_once, _init_lp_dasmodel_main___closed__8);
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__11(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__4, &lp_dasmodel_main___closed__4_once, _init_lp_dasmodel_main___closed__4);
x_2 = lp_dasmodel_loadSID(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* _lean_main() {
_start:
{
lean_object* x_2; lean_object* x_3; 
x_2 = ((lean_object*)(lp_dasmodel_main___closed__0));
x_3 = l_IO_FS_readBinFile(x_2);
if (lean_obj_tag(x_3) == 0)
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_4 = lean_ctor_get(x_3, 0);
lean_inc(x_4);
lean_dec_ref(x_3);
x_5 = ((lean_object*)(lp_dasmodel_main___closed__1));
x_6 = lean_byte_array_size(x_4);
x_7 = l_Nat_reprFast(x_6);
x_8 = lean_string_append(x_5, x_7);
lean_dec_ref(x_7);
x_9 = ((lean_object*)(lp_dasmodel_main___closed__2));
x_10 = lean_string_append(x_8, x_9);
x_11 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_10);
if (lean_obj_tag(x_11) == 0)
{
lean_object* x_12; lean_object* x_13; 
lean_dec_ref(x_11);
x_12 = lean_obj_once(&lp_dasmodel_main___closed__9, &lp_dasmodel_main___closed__9_once, _init_lp_dasmodel_main___closed__9);
x_13 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_12);
if (lean_obj_tag(x_13) == 0)
{
lean_object* x_17; 
lean_dec_ref(x_13);
x_17 = lp_dasmodel_loadSID(x_4);
lean_dec(x_4);
if (lean_obj_tag(x_17) == 1)
{
lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; 
x_18 = lean_ctor_get(x_17, 0);
lean_inc(x_18);
lean_dec_ref(x_17);
x_19 = lean_ctor_get(x_18, 1);
lean_inc(x_19);
x_20 = lean_ctor_get(x_18, 0);
lean_inc(x_20);
lean_dec(x_18);
x_21 = lean_ctor_get(x_19, 0);
lean_inc(x_21);
x_22 = lean_ctor_get(x_19, 1);
lean_inc(x_22);
lean_dec(x_19);
x_23 = lean_obj_once(&lp_dasmodel_main___closed__11, &lp_dasmodel_main___closed__11_once, _init_lp_dasmodel_main___closed__11);
if (lean_obj_tag(x_23) == 1)
{
lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; uint16_t x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; uint16_t x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; 
x_24 = lean_ctor_get(x_23, 0);
lean_inc(x_24);
x_25 = lean_ctor_get(x_24, 1);
lean_inc(x_25);
x_26 = lean_ctor_get(x_24, 0);
lean_inc(x_26);
lean_dec(x_24);
x_27 = lean_ctor_get(x_25, 0);
lean_inc(x_27);
x_28 = lean_ctor_get(x_25, 1);
lean_inc(x_28);
lean_dec(x_25);
x_29 = ((lean_object*)(lp_dasmodel_main___closed__12));
x_30 = lean_unbox(x_21);
x_31 = lean_uint16_to_nat(x_30);
x_32 = l_Nat_reprFast(x_31);
x_33 = lean_string_append(x_29, x_32);
lean_dec_ref(x_32);
x_34 = ((lean_object*)(lp_dasmodel_main___closed__13));
x_35 = lean_string_append(x_33, x_34);
x_36 = lean_unbox(x_22);
x_37 = lean_uint16_to_nat(x_36);
x_38 = l_Nat_reprFast(x_37);
x_39 = lean_string_append(x_35, x_38);
lean_dec_ref(x_38);
x_40 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_39);
if (lean_obj_tag(x_40) == 0)
{
lean_object* x_41; uint16_t x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; uint16_t x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; 
lean_dec_ref(x_40);
x_41 = ((lean_object*)(lp_dasmodel_main___closed__14));
x_42 = lean_unbox(x_27);
x_43 = lean_uint16_to_nat(x_42);
x_44 = l_Nat_reprFast(x_43);
x_45 = lean_string_append(x_41, x_44);
lean_dec_ref(x_44);
x_46 = lean_string_append(x_45, x_34);
x_47 = lean_unbox(x_28);
x_48 = lean_uint16_to_nat(x_47);
x_49 = l_Nat_reprFast(x_48);
x_50 = lean_string_append(x_46, x_49);
lean_dec_ref(x_49);
x_51 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_50);
if (lean_obj_tag(x_51) == 0)
{
uint8_t x_52; uint16_t x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; uint16_t x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; 
lean_dec_ref(x_51);
x_52 = 0;
x_53 = lean_unbox(x_21);
lean_dec(x_21);
x_54 = lp_dasmodel_execInit(x_20, x_53, x_52);
x_55 = lean_ctor_get(x_54, 0);
lean_inc(x_55);
x_56 = lean_ctor_get(x_54, 1);
lean_inc(x_56);
lean_dec_ref(x_54);
x_57 = lean_ctor_get_uint16(x_55, sizeof(void*)*2);
x_58 = ((lean_object*)(lp_dasmodel_main___closed__15));
x_59 = l_List_lengthTR___redArg(x_56);
lean_dec(x_56);
x_60 = l_Nat_reprFast(x_59);
x_61 = lean_string_append(x_58, x_60);
lean_dec_ref(x_60);
x_62 = ((lean_object*)(lp_dasmodel_main___closed__16));
x_63 = lean_string_append(x_61, x_62);
x_64 = lean_uint16_to_nat(x_57);
x_65 = l_Nat_reprFast(x_64);
x_66 = lean_string_append(x_63, x_65);
lean_dec_ref(x_65);
x_67 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_66);
if (lean_obj_tag(x_67) == 0)
{
uint16_t x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; uint16_t x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; 
lean_dec_ref(x_67);
x_68 = lean_unbox(x_27);
lean_dec(x_27);
x_69 = lp_dasmodel_execInit(x_26, x_68, x_52);
x_70 = lean_ctor_get(x_69, 0);
lean_inc(x_70);
x_71 = lean_ctor_get(x_69, 1);
lean_inc(x_71);
lean_dec_ref(x_69);
x_72 = lean_ctor_get_uint16(x_70, sizeof(void*)*2);
x_73 = ((lean_object*)(lp_dasmodel_main___closed__17));
x_74 = l_List_lengthTR___redArg(x_71);
lean_dec(x_71);
x_75 = l_Nat_reprFast(x_74);
x_76 = lean_string_append(x_73, x_75);
lean_dec_ref(x_75);
x_77 = lean_string_append(x_76, x_62);
x_78 = lean_uint16_to_nat(x_72);
x_79 = l_Nat_reprFast(x_78);
x_80 = lean_string_append(x_77, x_79);
lean_dec_ref(x_79);
x_81 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_80);
if (lean_obj_tag(x_81) == 0)
{
lean_object* x_82; uint16_t x_83; uint8_t x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; lean_object* x_89; uint16_t x_90; uint16_t x_91; uint16_t x_92; uint8_t x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; uint16_t x_98; uint16_t x_99; uint16_t x_100; uint8_t x_101; lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; uint16_t x_106; uint16_t x_107; uint16_t x_108; uint8_t x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; 
lean_dec_ref(x_81);
x_82 = ((lean_object*)(lp_dasmodel_main___closed__18));
x_83 = lean_unbox(x_22);
x_84 = lp_dasmodel_CPU_read(x_55, x_83);
x_85 = lean_uint8_to_nat(x_84);
x_86 = l_Nat_reprFast(x_85);
x_87 = lean_string_append(x_82, x_86);
lean_dec_ref(x_86);
x_88 = ((lean_object*)(lp_dasmodel_main___closed__19));
x_89 = lean_string_append(x_87, x_88);
x_90 = 1;
x_91 = lean_unbox(x_22);
x_92 = lean_uint16_add(x_91, x_90);
x_93 = lp_dasmodel_CPU_read(x_55, x_92);
x_94 = lean_uint8_to_nat(x_93);
x_95 = l_Nat_reprFast(x_94);
x_96 = lean_string_append(x_89, x_95);
lean_dec_ref(x_95);
x_97 = lean_string_append(x_96, x_88);
x_98 = 2;
x_99 = lean_unbox(x_22);
x_100 = lean_uint16_add(x_99, x_98);
x_101 = lp_dasmodel_CPU_read(x_55, x_100);
x_102 = lean_uint8_to_nat(x_101);
x_103 = l_Nat_reprFast(x_102);
x_104 = lean_string_append(x_97, x_103);
lean_dec_ref(x_103);
x_105 = lean_string_append(x_104, x_88);
x_106 = 3;
x_107 = lean_unbox(x_22);
x_108 = lean_uint16_add(x_107, x_106);
x_109 = lp_dasmodel_CPU_read(x_55, x_108);
x_110 = lean_uint8_to_nat(x_109);
x_111 = l_Nat_reprFast(x_110);
x_112 = lean_string_append(x_105, x_111);
lean_dec_ref(x_111);
x_113 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_112);
if (lean_obj_tag(x_113) == 0)
{
uint16_t x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; uint8_t x_119; uint16_t x_120; lean_object* x_121; lean_object* x_122; lean_object* x_123; lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; lean_object* x_130; lean_object* x_131; lean_object* x_132; lean_object* x_133; lean_object* x_134; 
lean_dec_ref(x_113);
x_114 = lean_unbox(x_22);
lean_inc(x_55);
x_115 = lp_dasmodel_execCall(x_55, x_114);
x_116 = lean_ctor_get(x_115, 0);
lean_inc(x_116);
x_117 = lean_ctor_get(x_115, 1);
lean_inc(x_117);
if (lean_is_exclusive(x_115)) {
 lean_ctor_release(x_115, 0);
 lean_ctor_release(x_115, 1);
 x_118 = x_115;
} else {
 lean_dec_ref(x_115);
 x_118 = lean_box(0);
}
x_119 = lean_ctor_get_uint8(x_116, sizeof(void*)*2 + 5);
x_120 = lean_ctor_get_uint16(x_116, sizeof(void*)*2);
x_121 = ((lean_object*)(lp_dasmodel_main___closed__20));
x_122 = l_List_lengthTR___redArg(x_117);
x_123 = l_Nat_reprFast(x_122);
x_124 = lean_string_append(x_121, x_123);
lean_dec_ref(x_123);
x_125 = lean_string_append(x_124, x_62);
x_126 = lean_uint16_to_nat(x_120);
x_127 = l_Nat_reprFast(x_126);
x_128 = lean_string_append(x_125, x_127);
lean_dec_ref(x_127);
x_129 = ((lean_object*)(lp_dasmodel_main___closed__21));
x_130 = lean_string_append(x_128, x_129);
x_131 = lean_uint8_to_nat(x_119);
x_132 = l_Nat_reprFast(x_131);
x_133 = lean_string_append(x_130, x_132);
lean_dec_ref(x_132);
x_134 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_133);
if (lean_obj_tag(x_134) == 0)
{
uint8_t x_135; lean_object* x_136; lean_object* x_137; lean_object* x_138; lean_object* x_139; lean_object* x_140; 
lean_dec_ref(x_134);
x_135 = lp_dasmodel_CPU_read(x_116, x_120);
lean_dec(x_116);
x_136 = ((lean_object*)(lp_dasmodel_main___closed__22));
x_137 = lean_uint8_to_nat(x_135);
x_138 = l_Nat_reprFast(x_137);
x_139 = lean_string_append(x_136, x_138);
lean_dec_ref(x_138);
x_140 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_139);
if (lean_obj_tag(x_140) == 0)
{
lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; lean_object* x_146; lean_object* x_147; lean_object* x_176; 
lean_dec_ref(x_140);
x_141 = lean_unsigned_to_nat(20u);
x_142 = lean_unsigned_to_nat(1u);
if (lean_obj_tag(x_117) == 0)
{
x_176 = lean_box(0);
goto block_185;
}
else
{
lean_object* x_186; lean_object* x_187; lean_object* x_188; lean_object* x_189; lean_object* x_190; 
x_186 = lean_ctor_get(x_117, 0);
lean_inc(x_186);
lean_dec_ref(x_117);
x_187 = ((lean_object*)(lp_dasmodel_main___closed__28));
x_188 = lp_dasmodel_cmpShowWrite(x_186);
x_189 = lean_string_append(x_187, x_188);
lean_dec_ref(x_188);
x_190 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_189);
if (lean_obj_tag(x_190) == 0)
{
lean_dec_ref(x_190);
x_176 = lean_box(0);
goto block_185;
}
else
{
lean_dec(x_118);
lean_dec(x_70);
lean_dec(x_55);
lean_dec(x_28);
lean_dec(x_22);
return x_190;
}
}
block_175:
{
lean_object* x_148; lean_object* x_149; lean_object* x_150; 
lean_inc(x_147);
lean_inc(x_144);
x_148 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_148, 0, x_144);
lean_ctor_set(x_148, 1, x_147);
lean_ctor_set(x_148, 2, x_142);
lean_inc_n(x_144, 2);
if (lean_is_scalar(x_118)) {
 x_149 = lean_alloc_ctor(0, 2, 0);
} else {
 x_149 = x_118;
}
lean_ctor_set(x_149, 0, x_144);
lean_ctor_set(x_149, 1, x_144);
x_150 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg(x_143, x_145, x_148, x_149, x_144);
lean_dec_ref(x_148);
lean_dec(x_145);
lean_dec(x_143);
if (lean_obj_tag(x_150) == 0)
{
lean_object* x_151; lean_object* x_152; lean_object* x_153; lean_object* x_154; 
x_151 = lean_ctor_get(x_150, 0);
lean_inc(x_151);
lean_dec_ref(x_150);
x_152 = lean_ctor_get(x_151, 1);
lean_inc(x_152);
lean_dec(x_151);
x_153 = ((lean_object*)(lp_dasmodel_main___closed__23));
x_154 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_153);
if (lean_obj_tag(x_154) == 0)
{
lean_object* x_155; lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; lean_object* x_162; lean_object* x_163; lean_object* x_164; lean_object* x_165; lean_object* x_166; lean_object* x_167; lean_object* x_168; lean_object* x_169; lean_object* x_170; lean_object* x_171; 
lean_dec_ref(x_154);
x_155 = ((lean_object*)(lp_dasmodel_main___closed__24));
lean_inc(x_152);
x_156 = l_Nat_reprFast(x_152);
x_157 = lean_string_append(x_155, x_156);
lean_dec_ref(x_156);
x_158 = ((lean_object*)(lp_dasmodel_main___closed__25));
x_159 = lean_string_append(x_157, x_158);
lean_inc(x_147);
x_160 = l_Nat_reprFast(x_147);
x_161 = lean_string_append(x_159, x_160);
lean_dec_ref(x_160);
x_162 = ((lean_object*)(lp_dasmodel_main___closed__26));
x_163 = lean_string_append(x_161, x_162);
x_164 = lean_unsigned_to_nat(100u);
x_165 = lean_nat_mul(x_152, x_164);
lean_dec(x_152);
x_166 = lean_nat_div(x_165, x_147);
lean_dec(x_147);
lean_dec(x_165);
x_167 = l_Nat_reprFast(x_166);
x_168 = lean_string_append(x_163, x_167);
lean_dec_ref(x_167);
x_169 = ((lean_object*)(lp_dasmodel_main___closed__27));
x_170 = lean_string_append(x_168, x_169);
x_171 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_170);
return x_171;
}
else
{
lean_dec(x_152);
lean_dec(x_147);
return x_154;
}
}
else
{
uint8_t x_172; 
lean_dec(x_147);
x_172 = !lean_is_exclusive(x_150);
if (x_172 == 0)
{
return x_150;
}
else
{
lean_object* x_173; lean_object* x_174; 
x_173 = lean_ctor_get(x_150, 0);
lean_inc(x_173);
lean_dec(x_150);
x_174 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_174, 0, x_173);
return x_174;
}
}
}
block_185:
{
uint16_t x_177; lean_object* x_178; uint16_t x_179; lean_object* x_180; lean_object* x_181; lean_object* x_182; lean_object* x_183; uint8_t x_184; 
x_177 = lean_unbox(x_22);
lean_dec(x_22);
x_178 = lp_dasmodel_execFrames(x_55, x_177, x_141);
x_179 = lean_unbox(x_28);
lean_dec(x_28);
x_180 = lp_dasmodel_execFrames(x_70, x_179, x_141);
x_181 = lean_unsigned_to_nat(0u);
x_182 = l_List_lengthTR___redArg(x_178);
x_183 = l_List_lengthTR___redArg(x_180);
x_184 = lean_nat_dec_le(x_182, x_183);
if (x_184 == 0)
{
lean_dec(x_182);
x_143 = x_178;
x_144 = x_181;
x_145 = x_180;
x_146 = lean_box(0);
x_147 = x_183;
goto block_175;
}
else
{
lean_dec(x_183);
x_143 = x_178;
x_144 = x_181;
x_145 = x_180;
x_146 = lean_box(0);
x_147 = x_182;
goto block_175;
}
}
}
else
{
lean_dec(x_118);
lean_dec(x_117);
lean_dec(x_70);
lean_dec(x_55);
lean_dec(x_28);
lean_dec(x_22);
return x_140;
}
}
else
{
lean_dec(x_118);
lean_dec(x_117);
lean_dec(x_116);
lean_dec(x_70);
lean_dec(x_55);
lean_dec(x_28);
lean_dec(x_22);
return x_134;
}
}
else
{
lean_dec(x_70);
lean_dec(x_55);
lean_dec(x_28);
lean_dec(x_22);
return x_113;
}
}
else
{
lean_dec(x_70);
lean_dec(x_55);
lean_dec(x_28);
lean_dec(x_22);
return x_81;
}
}
else
{
lean_dec(x_55);
lean_dec(x_28);
lean_dec(x_27);
lean_dec(x_26);
lean_dec(x_22);
return x_67;
}
}
else
{
lean_dec(x_28);
lean_dec(x_27);
lean_dec(x_26);
lean_dec(x_22);
lean_dec(x_21);
lean_dec(x_20);
return x_51;
}
}
else
{
lean_dec(x_28);
lean_dec(x_27);
lean_dec(x_26);
lean_dec(x_22);
lean_dec(x_21);
lean_dec(x_20);
return x_40;
}
}
else
{
lean_dec(x_22);
lean_dec(x_21);
lean_dec(x_20);
goto block_16;
}
}
else
{
lean_dec(x_17);
goto block_16;
}
block_16:
{
lean_object* x_14; lean_object* x_15; 
x_14 = ((lean_object*)(lp_dasmodel_main___closed__10));
x_15 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_14);
return x_15;
}
}
else
{
lean_dec(x_4);
return x_13;
}
}
else
{
lean_dec(x_4);
return x_11;
}
}
else
{
uint8_t x_191; 
x_191 = !lean_is_exclusive(x_3);
if (x_191 == 0)
{
return x_3;
}
else
{
lean_object* x_192; lean_object* x_193; 
x_192 = lean_ctor_get(x_3, 0);
lean_inc(x_192);
lean_dec(x_3);
x_193 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_193, 0, x_192);
return x_193;
}
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
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___redArg(x_1, x_2, x_3, x_4, x_5);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__0(x_1, x_2, x_3, x_4, x_5, x_6, x_7);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_9;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_CPU6502(uint8_t builtin);
lean_object* initialize_dasmodel_Codegen(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_CompareMain(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_CPU6502(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_Codegen(builtin);
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
res = initialize_dasmodel_CompareMain(1 /* builtin */);
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
