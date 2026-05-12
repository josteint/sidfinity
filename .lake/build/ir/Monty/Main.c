// Lean compiler output
// Module: Monty.Main
// Imports: public import Init public import Monty.Codegen public import Monty.SongData
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
lean_object* lean_get_stdout();
LEAN_EXPORT lean_object* lp_sidfinity_IO_print___at___00IO_println___at___00main_spec__0_spec__0(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_IO_print___at___00IO_println___at___00main_spec__0_spec__0___boxed(lean_object*, lean_object*);
lean_object* lean_string_push(lean_object*, uint32_t);
LEAN_EXPORT lean_object* lp_sidfinity_IO_println___at___00main_spec__0(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_IO_println___at___00main_spec__0___boxed(lean_object*, lean_object*);
static const lean_string_object lp_sidfinity_main___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 10, .m_capacity = 10, .m_length = 9, .m_data = "monty.sid"};
static const lean_object* lp_sidfinity_main___closed__0 = (const lean_object*)&lp_sidfinity_main___closed__0_value;
extern lean_object* lp_sidfinity_montyV3;
lean_object* lp_sidfinity_MV3_generateSID___redArg(lean_object*);
static lean_once_cell_t lp_sidfinity_main___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_main___closed__1;
lean_object* lean_byte_array_mk(lean_object*);
static lean_once_cell_t lp_sidfinity_main___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_main___closed__2;
static const lean_string_object lp_sidfinity_main___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 22, .m_capacity = 22, .m_length = 21, .m_data = "Generated monty.sid ("};
static const lean_object* lp_sidfinity_main___closed__3 = (const lean_object*)&lp_sidfinity_main___closed__3_value;
lean_object* lean_array_get_size(lean_object*);
static lean_once_cell_t lp_sidfinity_main___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_main___closed__4;
lean_object* l_Nat_reprFast(lean_object*);
static lean_once_cell_t lp_sidfinity_main___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_main___closed__5;
lean_object* lean_string_append(lean_object*, lean_object*);
static lean_once_cell_t lp_sidfinity_main___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_main___closed__6;
static const lean_string_object lp_sidfinity_main___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = " bytes)"};
static const lean_object* lp_sidfinity_main___closed__7 = (const lean_object*)&lp_sidfinity_main___closed__7_value;
static lean_once_cell_t lp_sidfinity_main___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_sidfinity_main___closed__8;
static const lean_string_object lp_sidfinity_main___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 15, .m_capacity = 15, .m_length = 14, .m_data = "  Freq table: "};
static const lean_object* lp_sidfinity_main___closed__9 = (const lean_object*)&lp_sidfinity_main___closed__9_value;
static const lean_string_object lp_sidfinity_main___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = " entries"};
static const lean_object* lp_sidfinity_main___closed__10 = (const lean_object*)&lp_sidfinity_main___closed__10_value;
static const lean_string_object lp_sidfinity_main___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 16, .m_capacity = 16, .m_length = 15, .m_data = "  Instruments: "};
static const lean_object* lp_sidfinity_main___closed__11 = (const lean_object*)&lp_sidfinity_main___closed__11_value;
static const lean_string_object lp_sidfinity_main___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "  Patterns: "};
static const lean_object* lp_sidfinity_main___closed__12 = (const lean_object*)&lp_sidfinity_main___closed__12_value;
static const lean_string_object lp_sidfinity_main___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "  Subtunes: "};
static const lean_object* lp_sidfinity_main___closed__13 = (const lean_object*)&lp_sidfinity_main___closed__13_value;
lean_object* lean_io_prim_handle_mk(lean_object*, uint8_t);
lean_object* lean_io_prim_handle_write(lean_object*, lean_object*);
lean_object* l_List_lengthTR___redArg(lean_object*);
LEAN_EXPORT lean_object* _lean_main();
LEAN_EXPORT lean_object* lp_sidfinity_main___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_sidfinity_IO_print___at___00IO_println___at___00main_spec__0_spec__0(lean_object* x_1) {
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
LEAN_EXPORT lean_object* lp_sidfinity_IO_print___at___00IO_println___at___00main_spec__0_spec__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_IO_print___at___00IO_println___at___00main_spec__0_spec__0(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_IO_println___at___00main_spec__0(lean_object* x_1) {
_start:
{
uint32_t x_3; lean_object* x_4; lean_object* x_5; 
x_3 = 10;
x_4 = lean_string_push(x_1, x_3);
x_5 = lp_sidfinity_IO_print___at___00IO_println___at___00main_spec__0_spec__0(x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_sidfinity_IO_println___at___00main_spec__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_sidfinity_IO_println___at___00main_spec__0(x_1);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_main___closed__1(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lp_sidfinity_montyV3;
x_2 = lp_sidfinity_MV3_generateSID___redArg(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_main___closed__2(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_sidfinity_main___closed__1, &lp_sidfinity_main___closed__1_once, _init_lp_sidfinity_main___closed__1);
x_2 = lean_byte_array_mk(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_main___closed__4(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_sidfinity_main___closed__1, &lp_sidfinity_main___closed__1_once, _init_lp_sidfinity_main___closed__1);
x_2 = lean_array_get_size(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_main___closed__5(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_sidfinity_main___closed__4, &lp_sidfinity_main___closed__4_once, _init_lp_sidfinity_main___closed__4);
x_2 = l_Nat_reprFast(x_1);
return x_2;
}
}
static lean_object* _init_lp_sidfinity_main___closed__6(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = lean_obj_once(&lp_sidfinity_main___closed__5, &lp_sidfinity_main___closed__5_once, _init_lp_sidfinity_main___closed__5);
x_2 = ((lean_object*)(lp_sidfinity_main___closed__3));
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
static lean_object* _init_lp_sidfinity_main___closed__8(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; 
x_1 = ((lean_object*)(lp_sidfinity_main___closed__7));
x_2 = lean_obj_once(&lp_sidfinity_main___closed__6, &lp_sidfinity_main___closed__6_once, _init_lp_sidfinity_main___closed__6);
x_3 = lean_string_append(x_2, x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* _lean_main() {
_start:
{
lean_object* x_2; uint8_t x_3; lean_object* x_4; 
x_2 = ((lean_object*)(lp_sidfinity_main___closed__0));
x_3 = 1;
x_4 = lean_io_prim_handle_mk(x_2, x_3);
if (lean_obj_tag(x_4) == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; 
x_5 = lean_ctor_get(x_4, 0);
lean_inc(x_5);
lean_dec_ref(x_4);
x_6 = lp_sidfinity_montyV3;
x_7 = lean_obj_once(&lp_sidfinity_main___closed__2, &lp_sidfinity_main___closed__2_once, _init_lp_sidfinity_main___closed__2);
x_8 = lean_io_prim_handle_write(x_5, x_7);
lean_dec(x_5);
if (lean_obj_tag(x_8) == 0)
{
lean_object* x_9; lean_object* x_10; 
lean_dec_ref(x_8);
x_9 = lean_obj_once(&lp_sidfinity_main___closed__8, &lp_sidfinity_main___closed__8_once, _init_lp_sidfinity_main___closed__8);
x_10 = lp_sidfinity_IO_println___at___00main_spec__0(x_9);
if (lean_obj_tag(x_10) == 0)
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
lean_dec_ref(x_10);
x_11 = lean_ctor_get(x_6, 0);
lean_inc(x_11);
x_12 = lean_ctor_get(x_6, 1);
lean_inc(x_12);
x_13 = lean_ctor_get(x_6, 2);
lean_inc(x_13);
x_14 = lean_ctor_get(x_6, 3);
lean_inc(x_14);
x_15 = ((lean_object*)(lp_sidfinity_main___closed__9));
x_16 = l_List_lengthTR___redArg(x_11);
lean_dec(x_11);
x_17 = l_Nat_reprFast(x_16);
x_18 = lean_string_append(x_15, x_17);
lean_dec_ref(x_17);
x_19 = ((lean_object*)(lp_sidfinity_main___closed__10));
x_20 = lean_string_append(x_18, x_19);
x_21 = lp_sidfinity_IO_println___at___00main_spec__0(x_20);
if (lean_obj_tag(x_21) == 0)
{
lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; 
lean_dec_ref(x_21);
x_22 = ((lean_object*)(lp_sidfinity_main___closed__11));
x_23 = l_List_lengthTR___redArg(x_12);
lean_dec(x_12);
x_24 = l_Nat_reprFast(x_23);
x_25 = lean_string_append(x_22, x_24);
lean_dec_ref(x_24);
x_26 = lp_sidfinity_IO_println___at___00main_spec__0(x_25);
if (lean_obj_tag(x_26) == 0)
{
lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; 
lean_dec_ref(x_26);
x_27 = ((lean_object*)(lp_sidfinity_main___closed__12));
x_28 = l_List_lengthTR___redArg(x_13);
lean_dec(x_13);
x_29 = l_Nat_reprFast(x_28);
x_30 = lean_string_append(x_27, x_29);
lean_dec_ref(x_29);
x_31 = lp_sidfinity_IO_println___at___00main_spec__0(x_30);
if (lean_obj_tag(x_31) == 0)
{
lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; 
lean_dec_ref(x_31);
x_32 = ((lean_object*)(lp_sidfinity_main___closed__13));
x_33 = l_List_lengthTR___redArg(x_14);
lean_dec(x_14);
x_34 = l_Nat_reprFast(x_33);
x_35 = lean_string_append(x_32, x_34);
lean_dec_ref(x_34);
x_36 = lp_sidfinity_IO_println___at___00main_spec__0(x_35);
return x_36;
}
else
{
lean_dec(x_14);
return x_31;
}
}
else
{
lean_dec(x_14);
lean_dec(x_13);
return x_26;
}
}
else
{
lean_dec(x_14);
lean_dec(x_13);
lean_dec(x_12);
return x_21;
}
}
else
{
return x_10;
}
}
else
{
return x_8;
}
}
else
{
uint8_t x_37; 
x_37 = !lean_is_exclusive(x_4);
if (x_37 == 0)
{
return x_4;
}
else
{
lean_object* x_38; lean_object* x_39; 
x_38 = lean_ctor_get(x_4, 0);
lean_inc(x_38);
lean_dec(x_4);
x_39 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_39, 0, x_38);
return x_39;
}
}
}
}
LEAN_EXPORT lean_object* lp_sidfinity_main___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = _lean_main();
return x_2;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_sidfinity_Monty_Codegen(uint8_t builtin);
lean_object* initialize_sidfinity_Monty_SongData(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_sidfinity_Monty_Main(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_sidfinity_Monty_Codegen(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_sidfinity_Monty_SongData(builtin);
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
res = initialize_sidfinity_Monty_Main(1 /* builtin */);
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
