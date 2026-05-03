// Lean compiler output
// Module: VerifyMain
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
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "=$"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__0 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__0_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "V"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "flo"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__2 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__2_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "fhi"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__3 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__3_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "plo"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__4 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__4_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "phi"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__5 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__5_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "ctl"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__6 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__6_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "ad"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__7 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__7_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "sr"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__8 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__8_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "Flo"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__9 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__9_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "Fhi"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__10 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__10_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "Fctl"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__11 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__11_value;
static const lean_string_object lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "Vol"};
static const lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__12 = (const lean_object*)&lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__12_value;
lean_object* l_List_reverse___redArg(lean_object*);
lean_object* lean_string_append(lean_object*, lean_object*);
lean_object* l_Nat_reprFast(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 4, .m_capacity = 4, .m_length = 3, .m_data = "  F"};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__0 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__0_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = ": "};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__1 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__1_value;
static const lean_string_object lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = " "};
static const lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__2 = (const lean_object*)&lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__2_value;
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_List_get_x3fInternal___redArg(lean_object*, lean_object*);
lean_object* l_String_intercalate(lean_object*, lean_object*);
lean_object* lp_dasmodel_IO_println___at___00commandoMain_spec__0(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
extern lean_object* lp_dasmodel_commandoSong;
lean_object* lp_dasmodel_generateSID___redArg(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__0;
static const lean_string_object lp_dasmodel_main___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "Generated SID: "};
static const lean_object* lp_dasmodel_main___closed__1 = (const lean_object*)&lp_dasmodel_main___closed__1_value;
lean_object* lean_array_get_size(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__2;
static lean_once_cell_t lp_dasmodel_main___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__3;
static lean_once_cell_t lp_dasmodel_main___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__4;
static const lean_string_object lp_dasmodel_main___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = " bytes"};
static const lean_object* lp_dasmodel_main___closed__5 = (const lean_object*)&lp_dasmodel_main___closed__5_value;
static lean_once_cell_t lp_dasmodel_main___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__6;
lean_object* lean_byte_array_mk(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__7;
lean_object* lp_dasmodel_loadSID(lean_object*);
static lean_once_cell_t lp_dasmodel_main___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_main___closed__8;
static const lean_string_object lp_dasmodel_main___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 19, .m_capacity = 19, .m_length = 18, .m_data = "Failed to load SID"};
static const lean_object* lp_dasmodel_main___closed__9 = (const lean_object*)&lp_dasmodel_main___closed__9_value;
static const lean_string_object lp_dasmodel_main___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "Loaded: init=$"};
static const lean_object* lp_dasmodel_main___closed__10 = (const lean_object*)&lp_dasmodel_main___closed__10_value;
static const lean_string_object lp_dasmodel_main___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = " play=$"};
static const lean_object* lp_dasmodel_main___closed__11 = (const lean_object*)&lp_dasmodel_main___closed__11_value;
static const lean_string_object lp_dasmodel_main___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "Init: "};
static const lean_object* lp_dasmodel_main___closed__12 = (const lean_object*)&lp_dasmodel_main___closed__12_value;
static const lean_string_object lp_dasmodel_main___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = " SID writes"};
static const lean_object* lp_dasmodel_main___closed__13 = (const lean_object*)&lp_dasmodel_main___closed__13_value;
static const lean_string_object lp_dasmodel_main___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "Executed "};
static const lean_object* lp_dasmodel_main___closed__14 = (const lean_object*)&lp_dasmodel_main___closed__14_value;
static const lean_string_object lp_dasmodel_main___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = " frames"};
static const lean_object* lp_dasmodel_main___closed__15 = (const lean_object*)&lp_dasmodel_main___closed__15_value;
lean_object* lean_uint16_to_nat(uint16_t);
lean_object* lp_dasmodel_execInit(lean_object*, uint16_t);
lean_object* l_List_lengthTR___redArg(lean_object*);
lean_object* lp_dasmodel_execFrames(lean_object*, uint16_t, lean_object*);
LEAN_EXPORT lean_object* _lean_main();
LEAN_EXPORT lean_object* lp_dasmodel_main___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_mapTR_loop___at___00main_spec__0(lean_object* x_1, lean_object* x_2) {
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
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_17; 
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
x_7 = lean_ctor_get(x_4, 0);
lean_inc(x_7);
x_8 = lean_ctor_get(x_4, 1);
lean_inc(x_8);
lean_dec(x_4);
x_17 = lean_unsigned_to_nat(1u);
switch (lean_obj_tag(x_7)) {
case 0:
{
lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; 
x_18 = lean_ctor_get(x_7, 0);
lean_inc(x_18);
lean_dec_ref(x_7);
x_19 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1));
x_20 = lean_nat_add(x_18, x_17);
lean_dec(x_18);
x_21 = l_Nat_reprFast(x_20);
x_22 = lean_string_append(x_19, x_21);
lean_dec_ref(x_21);
x_23 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__2));
x_24 = lean_string_append(x_22, x_23);
x_9 = x_24;
goto block_16;
}
case 1:
{
lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; 
x_25 = lean_ctor_get(x_7, 0);
lean_inc(x_25);
lean_dec_ref(x_7);
x_26 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1));
x_27 = lean_nat_add(x_25, x_17);
lean_dec(x_25);
x_28 = l_Nat_reprFast(x_27);
x_29 = lean_string_append(x_26, x_28);
lean_dec_ref(x_28);
x_30 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__3));
x_31 = lean_string_append(x_29, x_30);
x_9 = x_31;
goto block_16;
}
case 2:
{
lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; 
x_32 = lean_ctor_get(x_7, 0);
lean_inc(x_32);
lean_dec_ref(x_7);
x_33 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1));
x_34 = lean_nat_add(x_32, x_17);
lean_dec(x_32);
x_35 = l_Nat_reprFast(x_34);
x_36 = lean_string_append(x_33, x_35);
lean_dec_ref(x_35);
x_37 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__4));
x_38 = lean_string_append(x_36, x_37);
x_9 = x_38;
goto block_16;
}
case 3:
{
lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; 
x_39 = lean_ctor_get(x_7, 0);
lean_inc(x_39);
lean_dec_ref(x_7);
x_40 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1));
x_41 = lean_nat_add(x_39, x_17);
lean_dec(x_39);
x_42 = l_Nat_reprFast(x_41);
x_43 = lean_string_append(x_40, x_42);
lean_dec_ref(x_42);
x_44 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__5));
x_45 = lean_string_append(x_43, x_44);
x_9 = x_45;
goto block_16;
}
case 4:
{
lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; 
x_46 = lean_ctor_get(x_7, 0);
lean_inc(x_46);
lean_dec_ref(x_7);
x_47 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1));
x_48 = lean_nat_add(x_46, x_17);
lean_dec(x_46);
x_49 = l_Nat_reprFast(x_48);
x_50 = lean_string_append(x_47, x_49);
lean_dec_ref(x_49);
x_51 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__6));
x_52 = lean_string_append(x_50, x_51);
x_9 = x_52;
goto block_16;
}
case 5:
{
lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; 
x_53 = lean_ctor_get(x_7, 0);
lean_inc(x_53);
lean_dec_ref(x_7);
x_54 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1));
x_55 = lean_nat_add(x_53, x_17);
lean_dec(x_53);
x_56 = l_Nat_reprFast(x_55);
x_57 = lean_string_append(x_54, x_56);
lean_dec_ref(x_56);
x_58 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__7));
x_59 = lean_string_append(x_57, x_58);
x_9 = x_59;
goto block_16;
}
case 6:
{
lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; 
x_60 = lean_ctor_get(x_7, 0);
lean_inc(x_60);
lean_dec_ref(x_7);
x_61 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__1));
x_62 = lean_nat_add(x_60, x_17);
lean_dec(x_60);
x_63 = l_Nat_reprFast(x_62);
x_64 = lean_string_append(x_61, x_63);
lean_dec_ref(x_63);
x_65 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__8));
x_66 = lean_string_append(x_64, x_65);
x_9 = x_66;
goto block_16;
}
case 7:
{
lean_object* x_67; 
x_67 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__9));
x_9 = x_67;
goto block_16;
}
case 8:
{
lean_object* x_68; 
x_68 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__10));
x_9 = x_68;
goto block_16;
}
case 9:
{
lean_object* x_69; 
x_69 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__11));
x_9 = x_69;
goto block_16;
}
default: 
{
lean_object* x_70; 
x_70 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__12));
x_9 = x_70;
goto block_16;
}
}
block_16:
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_10 = ((lean_object*)(lp_dasmodel_List_mapTR_loop___at___00main_spec__0___closed__0));
x_11 = lean_string_append(x_9, x_10);
x_12 = l_Nat_reprFast(x_8);
x_13 = lean_string_append(x_11, x_12);
lean_dec_ref(x_12);
if (lean_is_scalar(x_6)) {
 x_14 = lean_alloc_ctor(1, 2, 0);
} else {
 x_14 = x_6;
}
lean_ctor_set(x_14, 0, x_13);
lean_ctor_set(x_14, 1, x_2);
x_1 = x_5;
x_2 = x_14;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_6 = lean_ctor_get(x_2, 1);
x_7 = lean_ctor_get(x_2, 2);
x_8 = lean_nat_dec_lt(x_4, x_6);
if (x_8 == 0)
{
lean_object* x_9; 
lean_dec(x_4);
x_9 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_9, 0, x_3);
return x_9;
}
else
{
lean_object* x_10; lean_object* x_11; lean_object* x_15; 
x_10 = lean_box(0);
lean_inc(x_4);
x_15 = l_List_get_x3fInternal___redArg(x_1, x_4);
if (lean_obj_tag(x_15) == 0)
{
x_11 = lean_box(0);
goto block_14;
}
else
{
lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; 
x_16 = lean_ctor_get(x_15, 0);
lean_inc(x_16);
lean_dec_ref(x_15);
x_17 = lean_box(0);
x_18 = lp_dasmodel_List_mapTR_loop___at___00main_spec__0(x_16, x_17);
x_19 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__0));
lean_inc(x_4);
x_20 = l_Nat_reprFast(x_4);
x_21 = lean_string_append(x_19, x_20);
lean_dec_ref(x_20);
x_22 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__1));
x_23 = lean_string_append(x_21, x_22);
x_24 = ((lean_object*)(lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___closed__2));
x_25 = l_String_intercalate(x_24, x_18);
x_26 = lean_string_append(x_23, x_25);
lean_dec_ref(x_25);
x_27 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_26);
if (lean_obj_tag(x_27) == 0)
{
lean_dec_ref(x_27);
x_11 = lean_box(0);
goto block_14;
}
else
{
lean_dec(x_4);
return x_27;
}
}
block_14:
{
lean_object* x_12; 
x_12 = lean_nat_add(x_4, x_7);
lean_dec(x_4);
x_3 = x_10;
x_4 = x_12;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_6;
}
}
static lean_object* _init_lp_dasmodel_main___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lp_dasmodel_commandoSong;
x_2 = lp_dasmodel_generateSID___redArg(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__2(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__0, &lp_dasmodel_main___closed__0_once, _init_lp_dasmodel_main___closed__0);
x_2 = lean_array_get_size(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__3(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__2, &lp_dasmodel_main___closed__2_once, _init_lp_dasmodel_main___closed__2);
x_2 = l_Nat_reprFast(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__4(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__3, &lp_dasmodel_main___closed__3_once, _init_lp_dasmodel_main___closed__3);
x_2 = ((lean_object*)(lp_dasmodel_main___closed__1));
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__6(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_dasmodel_main___closed__5));
x_2 = lean_obj_once(&lp_dasmodel_main___closed__4, &lp_dasmodel_main___closed__4_once, _init_lp_dasmodel_main___closed__4);
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_main___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__0, &lp_dasmodel_main___closed__0_once, _init_lp_dasmodel_main___closed__0);
x_2 = lean_byte_array_mk(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_main___closed__8(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_main___closed__7, &lp_dasmodel_main___closed__7_once, _init_lp_dasmodel_main___closed__7);
x_2 = lp_dasmodel_loadSID(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* _lean_main() {
_start:
{
lean_object* x_2; lean_object* x_3; 
x_2 = lean_obj_once(&lp_dasmodel_main___closed__6, &lp_dasmodel_main___closed__6_once, _init_lp_dasmodel_main___closed__6);
x_3 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_2);
if (lean_obj_tag(x_3) == 0)
{
lean_object* x_4; 
lean_dec_ref(x_3);
x_4 = lean_obj_once(&lp_dasmodel_main___closed__8, &lp_dasmodel_main___closed__8_once, _init_lp_dasmodel_main___closed__8);
if (lean_obj_tag(x_4) == 0)
{
lean_object* x_5; lean_object* x_6; 
x_5 = ((lean_object*)(lp_dasmodel_main___closed__9));
x_6 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_5);
return x_6;
}
else
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; uint16_t x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; uint16_t x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; 
x_7 = lean_ctor_get(x_4, 0);
lean_inc(x_7);
x_8 = lean_ctor_get(x_7, 1);
lean_inc(x_8);
x_9 = lean_ctor_get(x_7, 0);
lean_inc(x_9);
lean_dec(x_7);
x_10 = lean_ctor_get(x_8, 0);
lean_inc(x_10);
x_11 = lean_ctor_get(x_8, 1);
lean_inc(x_11);
lean_dec(x_8);
x_12 = ((lean_object*)(lp_dasmodel_main___closed__10));
x_13 = lean_unbox(x_10);
x_14 = lean_uint16_to_nat(x_13);
x_15 = l_Nat_reprFast(x_14);
x_16 = lean_string_append(x_12, x_15);
lean_dec_ref(x_15);
x_17 = ((lean_object*)(lp_dasmodel_main___closed__11));
x_18 = lean_string_append(x_16, x_17);
x_19 = lean_unbox(x_11);
x_20 = lean_uint16_to_nat(x_19);
x_21 = l_Nat_reprFast(x_20);
x_22 = lean_string_append(x_18, x_21);
lean_dec_ref(x_21);
x_23 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_22);
if (lean_obj_tag(x_23) == 0)
{
uint16_t x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; 
lean_dec_ref(x_23);
x_24 = lean_unbox(x_10);
lean_dec(x_10);
x_25 = lp_dasmodel_execInit(x_9, x_24);
x_26 = lean_ctor_get(x_25, 0);
lean_inc(x_26);
x_27 = lean_ctor_get(x_25, 1);
lean_inc(x_27);
lean_dec_ref(x_25);
x_28 = ((lean_object*)(lp_dasmodel_main___closed__12));
x_29 = l_List_lengthTR___redArg(x_27);
lean_dec(x_27);
x_30 = l_Nat_reprFast(x_29);
x_31 = lean_string_append(x_28, x_30);
lean_dec_ref(x_30);
x_32 = ((lean_object*)(lp_dasmodel_main___closed__13));
x_33 = lean_string_append(x_31, x_32);
x_34 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_33);
if (lean_obj_tag(x_34) == 0)
{
lean_object* x_35; uint16_t x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; 
lean_dec_ref(x_34);
x_35 = lean_unsigned_to_nat(10u);
x_36 = lean_unbox(x_11);
lean_dec(x_11);
x_37 = lp_dasmodel_execFrames(x_26, x_36, x_35);
x_38 = ((lean_object*)(lp_dasmodel_main___closed__14));
x_39 = l_List_lengthTR___redArg(x_37);
lean_inc(x_39);
x_40 = l_Nat_reprFast(x_39);
x_41 = lean_string_append(x_38, x_40);
lean_dec_ref(x_40);
x_42 = ((lean_object*)(lp_dasmodel_main___closed__15));
x_43 = lean_string_append(x_41, x_42);
x_44 = lp_dasmodel_IO_println___at___00commandoMain_spec__0(x_43);
if (lean_obj_tag(x_44) == 0)
{
lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; 
lean_dec_ref(x_44);
x_45 = lean_unsigned_to_nat(0u);
x_46 = lean_unsigned_to_nat(1u);
x_47 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_47, 0, x_45);
lean_ctor_set(x_47, 1, x_39);
lean_ctor_set(x_47, 2, x_46);
x_48 = lean_box(0);
x_49 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg(x_37, x_47, x_48, x_45);
lean_dec_ref(x_47);
lean_dec(x_37);
if (lean_obj_tag(x_49) == 0)
{
uint8_t x_50; 
x_50 = !lean_is_exclusive(x_49);
if (x_50 == 0)
{
lean_object* x_51; 
x_51 = lean_ctor_get(x_49, 0);
lean_dec(x_51);
lean_ctor_set(x_49, 0, x_48);
return x_49;
}
else
{
lean_object* x_52; 
lean_dec(x_49);
x_52 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_52, 0, x_48);
return x_52;
}
}
else
{
return x_49;
}
}
else
{
lean_dec(x_39);
lean_dec(x_37);
return x_44;
}
}
else
{
lean_dec(x_26);
lean_dec(x_11);
return x_34;
}
}
else
{
lean_dec(x_11);
lean_dec(x_10);
lean_dec(x_9);
return x_23;
}
}
}
else
{
return x_3;
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
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_8; 
x_8 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___redArg(x_1, x_2, x_3, x_4);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7) {
_start:
{
lean_object* x_8; 
x_8 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00main_spec__1(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_2);
lean_dec(x_1);
return x_8;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_CPU6502(uint8_t builtin);
lean_object* initialize_dasmodel_Codegen(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_VerifyMain(uint8_t builtin) {
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
res = initialize_dasmodel_VerifyMain(1 /* builtin */);
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
