// Lean compiler output
// Module: PSIDFile
// Imports: public import Init public import Asm6502
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
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
static lean_once_cell_t lp_dasmodel_writeBE16___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_writeBE16___closed__0;
uint16_t lean_uint16_shift_right(uint16_t, uint16_t);
uint8_t lean_uint16_to_uint8(uint16_t);
lean_object* lean_array_push(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_writeBE16(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_writeBE16___boxed(lean_object*);
static lean_once_cell_t lp_dasmodel_writeBE32___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_writeBE32___closed__0;
uint32_t lean_uint32_shift_right(uint32_t, uint32_t);
uint8_t lean_uint32_to_uint8(uint32_t);
LEAN_EXPORT lean_object* lp_dasmodel_writeBE32(uint32_t);
LEAN_EXPORT lean_object* lp_dasmodel_writeBE32___boxed(lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
uint8_t lean_byte_array_get(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___redArg(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_padString___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_padString___closed__0;
lean_object* lean_string_to_utf8(lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
lean_object* lean_byte_array_size(lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_padString(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_padString___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static lean_once_cell_t lp_dasmodel_serializeHeader___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_serializeHeader___closed__0;
static lean_once_cell_t lp_dasmodel_serializeHeader___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_serializeHeader___closed__1;
static lean_once_cell_t lp_dasmodel_serializeHeader___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_serializeHeader___closed__2;
static lean_once_cell_t lp_dasmodel_serializeHeader___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_serializeHeader___closed__3;
static lean_once_cell_t lp_dasmodel_serializeHeader___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_serializeHeader___closed__4;
static lean_once_cell_t lp_dasmodel_serializeHeader___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_serializeHeader___closed__5;
lean_object* l_Array_append___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_serializeHeader(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_serializeHeader___boxed(lean_object*);
uint8_t lean_uint16_dec_eq(uint16_t, uint16_t);
lean_object* lp_dasmodel_rawWord(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_buildSID(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_buildSID___boxed(lean_object*, lean_object*);
static lean_object* _init_lp_dasmodel_writeBE16___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_writeBE16(uint16_t x_1) {
_start:
{
uint16_t x_2; uint16_t x_3; uint8_t x_4; uint8_t x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_2 = 8;
x_3 = lean_uint16_shift_right(x_1, x_2);
x_4 = lean_uint16_to_uint8(x_3);
x_5 = lean_uint16_to_uint8(x_1);
x_6 = lean_obj_once(&lp_dasmodel_writeBE16___closed__0, &lp_dasmodel_writeBE16___closed__0_once, _init_lp_dasmodel_writeBE16___closed__0);
x_7 = lean_box(x_4);
x_8 = lean_array_push(x_6, x_7);
x_9 = lean_box(x_5);
x_10 = lean_array_push(x_8, x_9);
return x_10;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_writeBE16___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_writeBE16(x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_writeBE32___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(4u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_writeBE32(uint32_t x_1) {
_start:
{
uint32_t x_2; uint32_t x_3; uint8_t x_4; uint32_t x_5; uint32_t x_6; uint8_t x_7; uint32_t x_8; uint32_t x_9; uint8_t x_10; uint8_t x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; 
x_2 = 24;
x_3 = lean_uint32_shift_right(x_1, x_2);
x_4 = lean_uint32_to_uint8(x_3);
x_5 = 16;
x_6 = lean_uint32_shift_right(x_1, x_5);
x_7 = lean_uint32_to_uint8(x_6);
x_8 = 8;
x_9 = lean_uint32_shift_right(x_1, x_8);
x_10 = lean_uint32_to_uint8(x_9);
x_11 = lean_uint32_to_uint8(x_1);
x_12 = lean_obj_once(&lp_dasmodel_writeBE32___closed__0, &lp_dasmodel_writeBE32___closed__0_once, _init_lp_dasmodel_writeBE32___closed__0);
x_13 = lean_box(x_4);
x_14 = lean_array_push(x_12, x_13);
x_15 = lean_box(x_7);
x_16 = lean_array_push(x_14, x_15);
x_17 = lean_box(x_10);
x_18 = lean_array_push(x_16, x_17);
x_19 = lean_box(x_11);
x_20 = lean_array_push(x_18, x_19);
return x_20;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_writeBE32___boxed(lean_object* x_1) {
_start:
{
uint32_t x_2; lean_object* x_3; 
x_2 = lean_unbox_uint32(x_1);
lean_dec(x_1);
x_3 = lp_dasmodel_writeBE32(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; lean_object* x_6; uint8_t x_7; 
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_2, 2);
x_7 = lean_nat_dec_lt(x_4, x_5);
if (x_7 == 0)
{
lean_dec(x_4);
return x_3;
}
else
{
uint8_t x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_8 = lean_byte_array_get(x_1, x_4);
x_9 = lean_box(x_8);
x_10 = lean_array_push(x_3, x_9);
x_11 = lean_nat_add(x_4, x_6);
lean_dec(x_4);
x_3 = x_10;
x_4 = x_11;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___redArg(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
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
uint8_t x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_7 = 0;
x_8 = lean_box(x_7);
x_9 = lean_array_push(x_2, x_8);
x_10 = lean_nat_add(x_3, x_5);
lean_dec(x_3);
x_2 = x_9;
x_3 = x_10;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___redArg(x_1, x_2, x_3);
lean_dec_ref(x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_padString___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_padString(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_14; uint8_t x_15; 
x_3 = lean_string_to_utf8(x_1);
x_4 = lean_unsigned_to_nat(0u);
x_5 = lean_obj_once(&lp_dasmodel_padString___closed__0, &lp_dasmodel_padString___closed__0_once, _init_lp_dasmodel_padString___closed__0);
x_14 = lean_byte_array_size(x_3);
x_15 = lean_nat_dec_le(x_14, x_2);
if (x_15 == 0)
{
lean_inc(x_2);
x_6 = x_2;
goto block_13;
}
else
{
x_6 = x_14;
goto block_13;
}
block_13:
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_7 = lean_unsigned_to_nat(1u);
lean_inc(x_6);
x_8 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_8, 0, x_4);
lean_ctor_set(x_8, 1, x_6);
lean_ctor_set(x_8, 2, x_7);
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___redArg(x_3, x_8, x_5, x_4);
lean_dec_ref(x_8);
lean_dec_ref(x_3);
x_10 = lean_nat_sub(x_2, x_6);
lean_dec(x_6);
lean_dec(x_2);
x_11 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_11, 0, x_4);
lean_ctor_set(x_11, 1, x_10);
lean_ctor_set(x_11, 2, x_7);
x_12 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___redArg(x_11, x_9, x_4);
lean_dec_ref(x_11);
return x_12;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_padString___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_padString(x_1, x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___redArg(x_1, x_2, x_3, x_4);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__0(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___redArg(x_1, x_2, x_3);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00padString_spec__1(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_1);
return x_6;
}
}
static lean_object* _init_lp_dasmodel_serializeHeader___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 80;
x_2 = lean_obj_once(&lp_dasmodel_writeBE32___closed__0, &lp_dasmodel_writeBE32___closed__0_once, _init_lp_dasmodel_writeBE32___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_serializeHeader___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 83;
x_2 = lean_obj_once(&lp_dasmodel_serializeHeader___closed__0, &lp_dasmodel_serializeHeader___closed__0_once, _init_lp_dasmodel_serializeHeader___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_serializeHeader___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 73;
x_2 = lean_obj_once(&lp_dasmodel_serializeHeader___closed__1, &lp_dasmodel_serializeHeader___closed__1_once, _init_lp_dasmodel_serializeHeader___closed__1);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_serializeHeader___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 68;
x_2 = lean_obj_once(&lp_dasmodel_serializeHeader___closed__2, &lp_dasmodel_serializeHeader___closed__2_once, _init_lp_dasmodel_serializeHeader___closed__2);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_serializeHeader___closed__4(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_writeBE16___closed__0, &lp_dasmodel_writeBE16___closed__0_once, _init_lp_dasmodel_writeBE16___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_serializeHeader___closed__5(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = 0;
x_2 = lean_obj_once(&lp_dasmodel_serializeHeader___closed__4, &lp_dasmodel_serializeHeader___closed__4_once, _init_lp_dasmodel_serializeHeader___closed__4);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_serializeHeader(lean_object* x_1) {
_start:
{
uint16_t x_2; uint16_t x_3; uint16_t x_4; uint16_t x_5; uint16_t x_6; uint16_t x_7; uint16_t x_8; uint32_t x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; 
x_2 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 4);
x_3 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 6);
x_4 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 8);
x_5 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 10);
x_6 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 12);
x_7 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 14);
x_8 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 16);
x_9 = lean_ctor_get_uint32(x_1, sizeof(void*)*3);
x_10 = lean_ctor_get(x_1, 0);
x_11 = lean_ctor_get(x_1, 1);
x_12 = lean_ctor_get(x_1, 2);
x_13 = lean_obj_once(&lp_dasmodel_serializeHeader___closed__3, &lp_dasmodel_serializeHeader___closed__3_once, _init_lp_dasmodel_serializeHeader___closed__3);
x_14 = lp_dasmodel_writeBE16(x_2);
x_15 = l_Array_append___redArg(x_13, x_14);
lean_dec_ref(x_14);
x_16 = lp_dasmodel_writeBE16(x_3);
x_17 = l_Array_append___redArg(x_15, x_16);
lean_dec_ref(x_16);
x_18 = lp_dasmodel_writeBE16(x_4);
x_19 = l_Array_append___redArg(x_17, x_18);
lean_dec_ref(x_18);
x_20 = lp_dasmodel_writeBE16(x_5);
x_21 = l_Array_append___redArg(x_19, x_20);
lean_dec_ref(x_20);
x_22 = lp_dasmodel_writeBE16(x_6);
x_23 = l_Array_append___redArg(x_21, x_22);
lean_dec_ref(x_22);
x_24 = lp_dasmodel_writeBE16(x_7);
x_25 = l_Array_append___redArg(x_23, x_24);
lean_dec_ref(x_24);
x_26 = lp_dasmodel_writeBE16(x_8);
x_27 = l_Array_append___redArg(x_25, x_26);
lean_dec_ref(x_26);
x_28 = lp_dasmodel_writeBE32(x_9);
x_29 = l_Array_append___redArg(x_27, x_28);
lean_dec_ref(x_28);
x_30 = lean_unsigned_to_nat(32u);
x_31 = lp_dasmodel_padString(x_10, x_30);
x_32 = l_Array_append___redArg(x_29, x_31);
lean_dec_ref(x_31);
x_33 = lp_dasmodel_padString(x_11, x_30);
x_34 = l_Array_append___redArg(x_32, x_33);
lean_dec_ref(x_33);
x_35 = lp_dasmodel_padString(x_12, x_30);
x_36 = l_Array_append___redArg(x_34, x_35);
lean_dec_ref(x_35);
x_37 = lean_obj_once(&lp_dasmodel_serializeHeader___closed__5, &lp_dasmodel_serializeHeader___closed__5_once, _init_lp_dasmodel_serializeHeader___closed__5);
x_38 = l_Array_append___redArg(x_36, x_37);
x_39 = l_Array_append___redArg(x_38, x_37);
x_40 = l_Array_append___redArg(x_39, x_37);
return x_40;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_serializeHeader___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_serializeHeader(x_1);
lean_dec_ref(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_buildSID(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; uint16_t x_4; lean_object* x_5; uint16_t x_6; uint8_t x_7; 
x_3 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 8);
x_4 = lean_ctor_get_uint16(x_1, sizeof(void*)*3 + 10);
x_5 = lp_dasmodel_serializeHeader(x_1);
x_6 = 0;
x_7 = lean_uint16_dec_eq(x_3, x_6);
if (x_7 == 0)
{
lean_object* x_8; 
x_8 = l_Array_append___redArg(x_5, x_2);
return x_8;
}
else
{
lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_9 = lp_dasmodel_rawWord(x_4);
x_10 = l_Array_append___redArg(x_5, x_9);
lean_dec_ref(x_9);
x_11 = l_Array_append___redArg(x_10, x_2);
return x_11;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_buildSID___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_buildSID(x_1, x_2);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_Asm6502(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_PSIDFile(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_Asm6502(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
