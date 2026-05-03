// Lean compiler output
// Module: Effects
// Imports: public import Init public import SID public import State
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
static const lean_ctor_object lp_dasmodel_lookupFreq___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_lookupFreq___closed__0 = (const lean_object*)&lp_dasmodel_lookupFreq___closed__0_value;
lean_object* l_List_get_x3fInternal___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_lookupFreq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_lookupFreq___boxed(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
lean_object* lean_nat_mod(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_byteAdd(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_byteAdd___boxed(lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_byteSub(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_byteSub___boxed(lean_object*, lean_object*);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
lean_object* lean_nat_shiftr(lean_object*, lean_object*);
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_triangleLFO(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_triangleLFO___boxed(lean_object*, lean_object*);
lean_object* lean_nat_pow(lean_object*, lean_object*);
lean_object* lean_nat_div(lean_object*, lean_object*);
lean_object* lean_nat_mul(lean_object*, lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalVibrato(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalVibrato___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* l_List_head_x3f___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide___redArg___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_to_int(lean_object*);
lean_object* lean_int_add(lean_object*, lean_object*);
lean_object* l_Int_toNat(lean_object*);
lean_object* l_List_lengthTR___redArg(lean_object*);
uint8_t l_List_isEmpty___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalArpeggio(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalArpeggio___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalPW(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalPW___boxed(lean_object*, lean_object*, lean_object*);
lean_object* l_List_appendTR___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalEffectChain(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_evalEffectChain___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_lookupFreq(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_ctor_get(x_1, 0);
x_4 = l_List_get_x3fInternal___redArg(x_3, x_2);
if (lean_obj_tag(x_4) == 0)
{
lean_object* x_5; 
x_5 = ((lean_object*)(lp_dasmodel_lookupFreq___closed__0));
return x_5;
}
else
{
lean_object* x_6; 
x_6 = lean_ctor_get(x_4, 0);
lean_inc(x_6);
lean_dec_ref(x_4);
return x_6;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_lookupFreq___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_lookupFreq(x_1, x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_byteAdd(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_3 = lean_unsigned_to_nat(256u);
x_4 = lean_nat_add(x_1, x_2);
x_5 = lean_nat_mod(x_4, x_3);
lean_dec(x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_byteAdd___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_byteAdd(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_byteSub(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_3 = lean_unsigned_to_nat(256u);
x_4 = lean_nat_add(x_1, x_3);
x_5 = lean_nat_sub(x_4, x_2);
lean_dec(x_4);
x_6 = lean_nat_mod(x_5, x_3);
lean_dec(x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_byteSub___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_byteSub(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_triangleLFO(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; uint8_t x_4; 
x_3 = lean_unsigned_to_nat(0u);
x_4 = lean_nat_dec_eq(x_1, x_3);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_5 = lean_nat_mod(x_2, x_1);
x_6 = lean_unsigned_to_nat(1u);
x_7 = lean_nat_shiftr(x_1, x_6);
x_8 = lean_nat_dec_lt(x_5, x_7);
lean_dec(x_7);
if (x_8 == 0)
{
lean_object* x_9; lean_object* x_10; 
x_9 = lean_nat_sub(x_1, x_6);
x_10 = lean_nat_sub(x_9, x_5);
lean_dec(x_5);
lean_dec(x_9);
return x_10;
}
else
{
return x_5;
}
}
else
{
return x_3;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_triangleLFO___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_triangleLFO(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalVibrato(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; uint8_t x_91; 
x_30 = lean_ctor_get(x_3, 0);
lean_inc(x_30);
x_31 = lean_ctor_get(x_3, 1);
lean_inc(x_31);
x_32 = lean_ctor_get(x_3, 11);
lean_inc(x_32);
lean_dec_ref(x_3);
x_91 = lean_nat_dec_le(x_30, x_31);
if (x_91 == 0)
{
lean_object* x_92; 
lean_dec(x_31);
lean_dec(x_30);
x_92 = lean_unsigned_to_nat(0u);
x_33 = x_92;
goto block_90;
}
else
{
lean_object* x_93; 
x_93 = lean_nat_sub(x_31, x_30);
lean_dec(x_30);
lean_dec(x_31);
x_33 = x_93;
goto block_90;
}
block_29:
{
lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; 
x_12 = lean_unsigned_to_nat(2u);
x_13 = lean_nat_add(x_8, x_6);
x_14 = lean_nat_pow(x_12, x_13);
lean_dec(x_13);
x_15 = lean_nat_div(x_11, x_14);
lean_dec(x_14);
lean_dec(x_11);
x_16 = lean_nat_mul(x_15, x_10);
lean_dec(x_10);
lean_dec(x_15);
x_17 = lean_nat_add(x_7, x_16);
lean_dec(x_16);
lean_dec(x_7);
x_18 = lean_unsigned_to_nat(8u);
x_19 = lean_nat_shiftr(x_17, x_18);
x_20 = lean_nat_mod(x_19, x_9);
lean_dec(x_19);
x_21 = lean_nat_mod(x_17, x_9);
lean_dec(x_17);
lean_inc(x_2);
x_22 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_22, 0, x_2);
x_23 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_23, 0, x_22);
lean_ctor_set(x_23, 1, x_21);
x_24 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_24, 0, x_2);
x_25 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_25, 0, x_24);
lean_ctor_set(x_25, 1, x_20);
x_26 = lean_box(0);
x_27 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_27, 0, x_25);
lean_ctor_set(x_27, 1, x_26);
x_28 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_28, 0, x_23);
lean_ctor_set(x_28, 1, x_27);
return x_28;
}
block_90:
{
lean_object* x_34; lean_object* x_35; lean_object* x_36; uint8_t x_37; 
x_34 = lean_ctor_get(x_1, 0);
x_35 = lean_ctor_get(x_1, 1);
x_36 = lean_ctor_get(x_1, 2);
x_37 = lean_nat_dec_lt(x_33, x_36);
lean_dec(x_33);
if (x_37 == 0)
{
lean_object* x_38; uint8_t x_39; 
lean_inc(x_32);
x_38 = lp_dasmodel_lookupFreq(x_5, x_32);
x_39 = !lean_is_exclusive(x_38);
if (x_39 == 0)
{
lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; uint8_t x_45; 
x_40 = lean_ctor_get(x_38, 0);
x_41 = lean_ctor_get(x_38, 1);
x_42 = lean_ctor_get(x_4, 0);
x_43 = lp_dasmodel_triangleLFO(x_34, x_42);
x_44 = lean_unsigned_to_nat(0u);
x_45 = lean_nat_dec_eq(x_43, x_44);
if (x_45 == 0)
{
lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; uint8_t x_56; 
lean_free_object(x_38);
x_46 = lean_unsigned_to_nat(1u);
x_47 = lean_nat_add(x_32, x_46);
lean_dec(x_32);
x_48 = lp_dasmodel_lookupFreq(x_5, x_47);
x_49 = lean_ctor_get(x_48, 0);
lean_inc(x_49);
x_50 = lean_ctor_get(x_48, 1);
lean_inc(x_50);
lean_dec_ref(x_48);
x_51 = lean_unsigned_to_nat(256u);
x_52 = lean_nat_mul(x_41, x_51);
lean_dec(x_41);
x_53 = lean_nat_add(x_52, x_40);
lean_dec(x_40);
lean_dec(x_52);
x_54 = lean_nat_mul(x_50, x_51);
lean_dec(x_50);
x_55 = lean_nat_add(x_54, x_49);
lean_dec(x_49);
lean_dec(x_54);
x_56 = lean_nat_dec_le(x_53, x_55);
if (x_56 == 0)
{
lean_dec(x_55);
x_6 = x_46;
x_7 = x_53;
x_8 = x_35;
x_9 = x_51;
x_10 = x_43;
x_11 = x_44;
goto block_29;
}
else
{
lean_object* x_57; 
x_57 = lean_nat_sub(x_55, x_53);
lean_dec(x_55);
x_6 = x_46;
x_7 = x_53;
x_8 = x_35;
x_9 = x_51;
x_10 = x_43;
x_11 = x_57;
goto block_29;
}
}
else
{
lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; 
lean_dec(x_43);
lean_dec(x_32);
lean_inc(x_2);
x_58 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_58, 0, x_2);
lean_ctor_set(x_38, 1, x_40);
lean_ctor_set(x_38, 0, x_58);
x_59 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_59, 0, x_2);
x_60 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_60, 0, x_59);
lean_ctor_set(x_60, 1, x_41);
x_61 = lean_box(0);
x_62 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_62, 0, x_60);
lean_ctor_set(x_62, 1, x_61);
x_63 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_63, 0, x_38);
lean_ctor_set(x_63, 1, x_62);
return x_63;
}
}
else
{
lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; uint8_t x_69; 
x_64 = lean_ctor_get(x_38, 0);
x_65 = lean_ctor_get(x_38, 1);
lean_inc(x_65);
lean_inc(x_64);
lean_dec(x_38);
x_66 = lean_ctor_get(x_4, 0);
x_67 = lp_dasmodel_triangleLFO(x_34, x_66);
x_68 = lean_unsigned_to_nat(0u);
x_69 = lean_nat_dec_eq(x_67, x_68);
if (x_69 == 0)
{
lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; uint8_t x_80; 
x_70 = lean_unsigned_to_nat(1u);
x_71 = lean_nat_add(x_32, x_70);
lean_dec(x_32);
x_72 = lp_dasmodel_lookupFreq(x_5, x_71);
x_73 = lean_ctor_get(x_72, 0);
lean_inc(x_73);
x_74 = lean_ctor_get(x_72, 1);
lean_inc(x_74);
lean_dec_ref(x_72);
x_75 = lean_unsigned_to_nat(256u);
x_76 = lean_nat_mul(x_65, x_75);
lean_dec(x_65);
x_77 = lean_nat_add(x_76, x_64);
lean_dec(x_64);
lean_dec(x_76);
x_78 = lean_nat_mul(x_74, x_75);
lean_dec(x_74);
x_79 = lean_nat_add(x_78, x_73);
lean_dec(x_73);
lean_dec(x_78);
x_80 = lean_nat_dec_le(x_77, x_79);
if (x_80 == 0)
{
lean_dec(x_79);
x_6 = x_70;
x_7 = x_77;
x_8 = x_35;
x_9 = x_75;
x_10 = x_67;
x_11 = x_68;
goto block_29;
}
else
{
lean_object* x_81; 
x_81 = lean_nat_sub(x_79, x_77);
lean_dec(x_79);
x_6 = x_70;
x_7 = x_77;
x_8 = x_35;
x_9 = x_75;
x_10 = x_67;
x_11 = x_81;
goto block_29;
}
}
else
{
lean_object* x_82; lean_object* x_83; lean_object* x_84; lean_object* x_85; lean_object* x_86; lean_object* x_87; lean_object* x_88; 
lean_dec(x_67);
lean_dec(x_32);
lean_inc(x_2);
x_82 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_82, 0, x_2);
x_83 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_83, 0, x_82);
lean_ctor_set(x_83, 1, x_64);
x_84 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_84, 0, x_2);
x_85 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_85, 0, x_84);
lean_ctor_set(x_85, 1, x_65);
x_86 = lean_box(0);
x_87 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_87, 0, x_85);
lean_ctor_set(x_87, 1, x_86);
x_88 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_88, 0, x_83);
lean_ctor_set(x_88, 1, x_87);
return x_88;
}
}
}
else
{
lean_object* x_89; 
lean_dec(x_32);
lean_dec(x_2);
x_89 = lean_box(0);
return x_89;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalVibrato___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_evalVibrato(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_5);
lean_dec_ref(x_4);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint8_t x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_37; uint8_t x_38; 
x_4 = lean_ctor_get(x_2, 0);
x_5 = lean_ctor_get(x_2, 1);
x_6 = lean_ctor_get(x_2, 2);
x_7 = lean_ctor_get(x_2, 3);
x_8 = lean_ctor_get(x_2, 4);
x_9 = lean_ctor_get(x_2, 5);
x_10 = lean_ctor_get(x_2, 6);
x_11 = lean_ctor_get_uint8(x_2, sizeof(void*)*12);
x_12 = lean_ctor_get(x_2, 7);
x_13 = lean_ctor_get(x_2, 8);
x_14 = lean_ctor_get(x_2, 9);
x_15 = lean_ctor_get(x_2, 10);
x_16 = lean_ctor_get(x_2, 11);
x_37 = lean_unsigned_to_nat(0u);
x_38 = lean_nat_dec_eq(x_14, x_37);
if (x_38 == 0)
{
lean_object* x_39; lean_object* x_40; 
lean_inc(x_16);
lean_inc(x_15);
lean_inc(x_14);
lean_inc(x_13);
lean_inc(x_12);
lean_inc(x_10);
lean_inc(x_9);
lean_inc(x_8);
lean_inc(x_7);
lean_inc(x_6);
lean_inc(x_5);
lean_inc(x_4);
lean_dec_ref(x_2);
x_39 = lean_ctor_get(x_3, 0);
x_40 = l_List_head_x3f___redArg(x_39);
if (lean_obj_tag(x_40) == 0)
{
x_17 = x_37;
goto block_36;
}
else
{
lean_object* x_41; 
x_41 = lean_ctor_get(x_40, 0);
lean_inc(x_41);
lean_dec_ref(x_40);
x_17 = x_41;
goto block_36;
}
}
else
{
lean_object* x_42; lean_object* x_43; 
lean_dec(x_1);
x_42 = lean_box(0);
x_43 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_43, 0, x_42);
lean_ctor_set(x_43, 1, x_2);
return x_43;
}
block_36:
{
lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; 
x_18 = lean_unsigned_to_nat(256u);
x_19 = lean_nat_mod(x_17, x_18);
lean_dec(x_17);
x_20 = lean_unsigned_to_nat(2u);
x_21 = lean_unsigned_to_nat(1u);
x_22 = lean_nat_shiftr(x_19, x_21);
lean_dec(x_19);
x_23 = lean_nat_mul(x_22, x_20);
lean_dec(x_22);
lean_inc(x_1);
x_24 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_24, 0, x_1);
lean_inc(x_14);
x_25 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_25, 0, x_24);
lean_ctor_set(x_25, 1, x_14);
x_26 = lean_alloc_ctor(4, 1, 0);
lean_ctor_set(x_26, 0, x_1);
x_27 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_27, 0, x_26);
lean_ctor_set(x_27, 1, x_23);
x_28 = lean_box(0);
x_29 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_29, 0, x_27);
lean_ctor_set(x_29, 1, x_28);
x_30 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_30, 0, x_25);
lean_ctor_set(x_30, 1, x_29);
x_31 = lean_unsigned_to_nat(255u);
x_32 = lean_nat_add(x_14, x_31);
lean_dec(x_14);
x_33 = lean_nat_mod(x_32, x_18);
lean_dec(x_32);
x_34 = lean_alloc_ctor(0, 12, 1);
lean_ctor_set(x_34, 0, x_4);
lean_ctor_set(x_34, 1, x_5);
lean_ctor_set(x_34, 2, x_6);
lean_ctor_set(x_34, 3, x_7);
lean_ctor_set(x_34, 4, x_8);
lean_ctor_set(x_34, 5, x_9);
lean_ctor_set(x_34, 6, x_10);
lean_ctor_set(x_34, 7, x_12);
lean_ctor_set(x_34, 8, x_13);
lean_ctor_set(x_34, 9, x_33);
lean_ctor_set(x_34, 10, x_15);
lean_ctor_set(x_34, 11, x_16);
lean_ctor_set_uint8(x_34, sizeof(void*)*12, x_11);
x_35 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_35, 0, x_30);
lean_ctor_set(x_35, 1, x_34);
return x_35;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_evalFreqSlide___redArg(x_1, x_2, x_3);
lean_dec_ref(x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_evalFreqSlide___redArg(x_2, x_3, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalFreqSlide___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_evalFreqSlide(x_1, x_2, x_3, x_4);
lean_dec_ref(x_4);
lean_dec_ref(x_1);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalArpeggio(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; lean_object* x_32; uint8_t x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_41; uint8_t x_48; 
x_32 = lean_ctor_get(x_1, 0);
x_33 = lean_ctor_get_uint8(x_1, sizeof(void*)*2);
x_34 = lean_ctor_get(x_1, 1);
x_48 = l_List_isEmpty___redArg(x_32);
if (x_48 == 0)
{
if (x_33 == 0)
{
lean_object* x_49; 
x_49 = lean_ctor_get(x_4, 0);
lean_inc(x_49);
lean_dec_ref(x_4);
x_41 = x_49;
goto block_47;
}
else
{
lean_object* x_50; 
lean_dec_ref(x_4);
x_50 = lean_ctor_get(x_3, 0);
lean_inc(x_50);
x_41 = x_50;
goto block_47;
}
}
else
{
lean_object* x_51; 
lean_dec_ref(x_4);
lean_dec_ref(x_3);
lean_dec(x_2);
x_51 = lean_box(0);
return x_51;
}
block_31:
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; uint8_t x_14; 
x_7 = lean_ctor_get(x_3, 11);
lean_inc(x_7);
lean_dec_ref(x_3);
x_8 = lean_nat_to_int(x_7);
x_9 = lean_int_add(x_8, x_6);
lean_dec(x_6);
lean_dec(x_8);
x_10 = l_Int_toNat(x_9);
lean_dec(x_9);
x_11 = lean_unsigned_to_nat(256u);
x_12 = lean_nat_mod(x_10, x_11);
lean_dec(x_10);
x_13 = lp_dasmodel_lookupFreq(x_5, x_12);
x_14 = !lean_is_exclusive(x_13);
if (x_14 == 0)
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_15 = lean_ctor_get(x_13, 0);
lean_inc(x_2);
x_16 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_16, 0, x_2);
lean_ctor_set(x_13, 0, x_16);
x_17 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_17, 0, x_2);
x_18 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_18, 0, x_17);
lean_ctor_set(x_18, 1, x_15);
x_19 = lean_box(0);
x_20 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_20, 0, x_18);
lean_ctor_set(x_20, 1, x_19);
x_21 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_21, 0, x_13);
lean_ctor_set(x_21, 1, x_20);
return x_21;
}
else
{
lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; 
x_22 = lean_ctor_get(x_13, 0);
x_23 = lean_ctor_get(x_13, 1);
lean_inc(x_23);
lean_inc(x_22);
lean_dec(x_13);
lean_inc(x_2);
x_24 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_24, 0, x_2);
x_25 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_25, 0, x_24);
lean_ctor_set(x_25, 1, x_23);
x_26 = lean_alloc_ctor(0, 1, 0);
lean_ctor_set(x_26, 0, x_2);
x_27 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_27, 0, x_26);
lean_ctor_set(x_27, 1, x_22);
x_28 = lean_box(0);
x_29 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_29, 0, x_27);
lean_ctor_set(x_29, 1, x_28);
x_30 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_30, 0, x_25);
lean_ctor_set(x_30, 1, x_29);
return x_30;
}
}
block_40:
{
lean_object* x_37; 
x_37 = l_List_get_x3fInternal___redArg(x_32, x_36);
if (lean_obj_tag(x_37) == 0)
{
lean_object* x_38; 
x_38 = lean_nat_to_int(x_35);
x_6 = x_38;
goto block_31;
}
else
{
lean_object* x_39; 
lean_dec(x_35);
x_39 = lean_ctor_get(x_37, 0);
lean_inc(x_39);
lean_dec_ref(x_37);
x_6 = x_39;
goto block_31;
}
}
block_47:
{
lean_object* x_42; uint8_t x_43; 
x_42 = lean_unsigned_to_nat(0u);
x_43 = lean_nat_dec_eq(x_34, x_42);
if (x_43 == 0)
{
lean_object* x_44; lean_object* x_45; lean_object* x_46; 
x_44 = lean_nat_div(x_41, x_34);
lean_dec(x_41);
x_45 = l_List_lengthTR___redArg(x_32);
x_46 = lean_nat_mod(x_44, x_45);
lean_dec(x_45);
lean_dec(x_44);
x_35 = x_42;
x_36 = x_46;
goto block_40;
}
else
{
lean_dec(x_41);
x_35 = x_42;
x_36 = x_42;
goto block_40;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalArpeggio___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_evalArpeggio(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_5);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalPW(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; uint8_t x_9; 
x_4 = lean_ctor_get_uint8(x_1, sizeof(void*)*6);
x_5 = lean_ctor_get(x_1, 0);
x_6 = lean_ctor_get(x_1, 1);
x_7 = lean_ctor_get(x_1, 2);
x_8 = lean_unsigned_to_nat(0u);
x_9 = lean_nat_dec_eq(x_5, x_8);
if (x_9 == 0)
{
switch (x_4) {
case 0:
{
uint8_t x_10; 
x_10 = !lean_is_exclusive(x_3);
if (x_10 == 0)
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_11 = lean_ctor_get(x_3, 5);
x_12 = lean_ctor_get(x_3, 6);
x_13 = lp_dasmodel_byteAdd(x_11, x_5);
lean_dec(x_11);
lean_inc(x_2);
x_14 = lean_alloc_ctor(2, 1, 0);
lean_ctor_set(x_14, 0, x_2);
lean_inc(x_13);
x_15 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_15, 0, x_14);
lean_ctor_set(x_15, 1, x_13);
x_16 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_16, 0, x_2);
lean_inc(x_12);
x_17 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_17, 0, x_16);
lean_ctor_set(x_17, 1, x_12);
x_18 = lean_box(0);
x_19 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_19, 0, x_17);
lean_ctor_set(x_19, 1, x_18);
x_20 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_20, 0, x_15);
lean_ctor_set(x_20, 1, x_19);
lean_ctor_set(x_3, 5, x_13);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_20);
lean_ctor_set(x_21, 1, x_3);
return x_21;
}
else
{
lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; uint8_t x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; 
x_22 = lean_ctor_get(x_3, 0);
x_23 = lean_ctor_get(x_3, 1);
x_24 = lean_ctor_get(x_3, 2);
x_25 = lean_ctor_get(x_3, 3);
x_26 = lean_ctor_get(x_3, 4);
x_27 = lean_ctor_get(x_3, 5);
x_28 = lean_ctor_get(x_3, 6);
x_29 = lean_ctor_get_uint8(x_3, sizeof(void*)*12);
x_30 = lean_ctor_get(x_3, 7);
x_31 = lean_ctor_get(x_3, 8);
x_32 = lean_ctor_get(x_3, 9);
x_33 = lean_ctor_get(x_3, 10);
x_34 = lean_ctor_get(x_3, 11);
lean_inc(x_34);
lean_inc(x_33);
lean_inc(x_32);
lean_inc(x_31);
lean_inc(x_30);
lean_inc(x_28);
lean_inc(x_27);
lean_inc(x_26);
lean_inc(x_25);
lean_inc(x_24);
lean_inc(x_23);
lean_inc(x_22);
lean_dec(x_3);
x_35 = lp_dasmodel_byteAdd(x_27, x_5);
lean_dec(x_27);
lean_inc(x_2);
x_36 = lean_alloc_ctor(2, 1, 0);
lean_ctor_set(x_36, 0, x_2);
lean_inc(x_35);
x_37 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_37, 0, x_36);
lean_ctor_set(x_37, 1, x_35);
x_38 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_38, 0, x_2);
lean_inc(x_28);
x_39 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_39, 0, x_38);
lean_ctor_set(x_39, 1, x_28);
x_40 = lean_box(0);
x_41 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_41, 0, x_39);
lean_ctor_set(x_41, 1, x_40);
x_42 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_42, 0, x_37);
lean_ctor_set(x_42, 1, x_41);
x_43 = lean_alloc_ctor(0, 12, 1);
lean_ctor_set(x_43, 0, x_22);
lean_ctor_set(x_43, 1, x_23);
lean_ctor_set(x_43, 2, x_24);
lean_ctor_set(x_43, 3, x_25);
lean_ctor_set(x_43, 4, x_26);
lean_ctor_set(x_43, 5, x_35);
lean_ctor_set(x_43, 6, x_28);
lean_ctor_set(x_43, 7, x_30);
lean_ctor_set(x_43, 8, x_31);
lean_ctor_set(x_43, 9, x_32);
lean_ctor_set(x_43, 10, x_33);
lean_ctor_set(x_43, 11, x_34);
lean_ctor_set_uint8(x_43, sizeof(void*)*12, x_29);
x_44 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_44, 0, x_42);
lean_ctor_set(x_44, 1, x_43);
return x_44;
}
}
case 1:
{
lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; uint8_t x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; uint8_t x_59; 
x_45 = lean_ctor_get(x_3, 0);
lean_inc(x_45);
x_46 = lean_ctor_get(x_3, 1);
lean_inc(x_46);
x_47 = lean_ctor_get(x_3, 2);
lean_inc(x_47);
x_48 = lean_ctor_get(x_3, 3);
lean_inc(x_48);
x_49 = lean_ctor_get(x_3, 4);
lean_inc(x_49);
x_50 = lean_ctor_get(x_3, 5);
lean_inc(x_50);
x_51 = lean_ctor_get(x_3, 6);
lean_inc(x_51);
x_52 = lean_ctor_get_uint8(x_3, sizeof(void*)*12);
x_53 = lean_ctor_get(x_3, 7);
lean_inc(x_53);
x_54 = lean_ctor_get(x_3, 8);
lean_inc(x_54);
x_55 = lean_ctor_get(x_3, 9);
lean_inc(x_55);
x_56 = lean_ctor_get(x_3, 10);
lean_inc(x_56);
x_57 = lean_ctor_get(x_3, 11);
lean_inc(x_57);
if (lean_is_exclusive(x_3)) {
 lean_ctor_release(x_3, 0);
 lean_ctor_release(x_3, 1);
 lean_ctor_release(x_3, 2);
 lean_ctor_release(x_3, 3);
 lean_ctor_release(x_3, 4);
 lean_ctor_release(x_3, 5);
 lean_ctor_release(x_3, 6);
 lean_ctor_release(x_3, 7);
 lean_ctor_release(x_3, 8);
 lean_ctor_release(x_3, 9);
 lean_ctor_release(x_3, 10);
 lean_ctor_release(x_3, 11);
 x_58 = x_3;
} else {
 lean_dec_ref(x_3);
 x_58 = lean_box(0);
}
x_59 = 1;
if (x_52 == 0)
{
lean_object* x_60; lean_object* x_61; lean_object* x_62; uint8_t x_63; lean_object* x_67; lean_object* x_77; lean_object* x_78; uint8_t x_79; 
x_60 = lp_dasmodel_byteAdd(x_50, x_5);
x_77 = lean_unsigned_to_nat(255u);
x_78 = lean_nat_add(x_50, x_5);
lean_dec(x_50);
x_79 = lean_nat_dec_lt(x_77, x_78);
lean_dec(x_78);
if (x_79 == 0)
{
x_67 = x_51;
goto block_76;
}
else
{
lean_object* x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; 
x_80 = lean_unsigned_to_nat(256u);
x_81 = lean_unsigned_to_nat(1u);
x_82 = lean_nat_add(x_51, x_81);
lean_dec(x_51);
x_83 = lean_nat_mod(x_82, x_80);
lean_dec(x_82);
x_67 = x_83;
goto block_76;
}
block_66:
{
lean_object* x_64; lean_object* x_65; 
if (lean_is_scalar(x_58)) {
 x_64 = lean_alloc_ctor(0, 12, 1);
} else {
 x_64 = x_58;
}
lean_ctor_set(x_64, 0, x_45);
lean_ctor_set(x_64, 1, x_46);
lean_ctor_set(x_64, 2, x_47);
lean_ctor_set(x_64, 3, x_48);
lean_ctor_set(x_64, 4, x_49);
lean_ctor_set(x_64, 5, x_60);
lean_ctor_set(x_64, 6, x_61);
lean_ctor_set(x_64, 7, x_53);
lean_ctor_set(x_64, 8, x_54);
lean_ctor_set(x_64, 9, x_55);
lean_ctor_set(x_64, 10, x_56);
lean_ctor_set(x_64, 11, x_57);
lean_ctor_set_uint8(x_64, sizeof(void*)*12, x_63);
x_65 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_65, 0, x_62);
lean_ctor_set(x_65, 1, x_64);
return x_65;
}
block_76:
{
uint8_t x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; lean_object* x_74; lean_object* x_75; 
x_68 = lean_nat_dec_eq(x_67, x_7);
lean_inc(x_2);
x_69 = lean_alloc_ctor(2, 1, 0);
lean_ctor_set(x_69, 0, x_2);
lean_inc(x_60);
x_70 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_70, 0, x_69);
lean_ctor_set(x_70, 1, x_60);
x_71 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_71, 0, x_2);
lean_inc(x_67);
x_72 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_72, 0, x_71);
lean_ctor_set(x_72, 1, x_67);
x_73 = lean_box(0);
x_74 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_74, 0, x_72);
lean_ctor_set(x_74, 1, x_73);
x_75 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_75, 0, x_70);
lean_ctor_set(x_75, 1, x_74);
if (x_68 == 0)
{
x_61 = x_67;
x_62 = x_75;
x_63 = x_52;
goto block_66;
}
else
{
x_61 = x_67;
x_62 = x_75;
x_63 = x_59;
goto block_66;
}
}
}
else
{
lean_object* x_84; lean_object* x_85; lean_object* x_86; uint8_t x_87; lean_object* x_91; uint8_t x_101; 
x_84 = lp_dasmodel_byteSub(x_50, x_5);
x_101 = lean_nat_dec_lt(x_50, x_5);
lean_dec(x_50);
if (x_101 == 0)
{
x_91 = x_51;
goto block_100;
}
else
{
lean_object* x_102; lean_object* x_103; lean_object* x_104; lean_object* x_105; 
x_102 = lean_unsigned_to_nat(256u);
x_103 = lean_unsigned_to_nat(255u);
x_104 = lean_nat_add(x_51, x_103);
lean_dec(x_51);
x_105 = lean_nat_mod(x_104, x_102);
lean_dec(x_104);
x_91 = x_105;
goto block_100;
}
block_90:
{
lean_object* x_88; lean_object* x_89; 
if (lean_is_scalar(x_58)) {
 x_88 = lean_alloc_ctor(0, 12, 1);
} else {
 x_88 = x_58;
}
lean_ctor_set(x_88, 0, x_45);
lean_ctor_set(x_88, 1, x_46);
lean_ctor_set(x_88, 2, x_47);
lean_ctor_set(x_88, 3, x_48);
lean_ctor_set(x_88, 4, x_49);
lean_ctor_set(x_88, 5, x_84);
lean_ctor_set(x_88, 6, x_86);
lean_ctor_set(x_88, 7, x_53);
lean_ctor_set(x_88, 8, x_54);
lean_ctor_set(x_88, 9, x_55);
lean_ctor_set(x_88, 10, x_56);
lean_ctor_set(x_88, 11, x_57);
lean_ctor_set_uint8(x_88, sizeof(void*)*12, x_87);
x_89 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_89, 0, x_85);
lean_ctor_set(x_89, 1, x_88);
return x_89;
}
block_100:
{
uint8_t x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; lean_object* x_98; lean_object* x_99; 
x_92 = lean_nat_dec_eq(x_91, x_6);
lean_inc(x_2);
x_93 = lean_alloc_ctor(2, 1, 0);
lean_ctor_set(x_93, 0, x_2);
lean_inc(x_84);
x_94 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_94, 0, x_93);
lean_ctor_set(x_94, 1, x_84);
x_95 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_95, 0, x_2);
lean_inc(x_91);
x_96 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_96, 0, x_95);
lean_ctor_set(x_96, 1, x_91);
x_97 = lean_box(0);
x_98 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_98, 0, x_96);
lean_ctor_set(x_98, 1, x_97);
x_99 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_99, 0, x_94);
lean_ctor_set(x_99, 1, x_98);
if (x_92 == 0)
{
x_85 = x_99;
x_86 = x_91;
x_87 = x_59;
goto block_90;
}
else
{
x_85 = x_99;
x_86 = x_91;
x_87 = x_9;
goto block_90;
}
}
}
}
default: 
{
lean_object* x_106; lean_object* x_107; 
lean_dec(x_2);
x_106 = lean_box(0);
x_107 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_107, 0, x_106);
lean_ctor_set(x_107, 1, x_3);
return x_107;
}
}
}
else
{
lean_object* x_108; lean_object* x_109; 
lean_dec(x_2);
x_108 = lean_box(0);
x_109 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_109, 0, x_108);
lean_ctor_set(x_109, 1, x_3);
return x_109;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalPW___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel_evalPW(x_1, x_2, x_3);
lean_dec_ref(x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalEffectChain(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_25; 
x_15 = lean_ctor_get(x_1, 0);
x_16 = lean_ctor_get(x_1, 1);
x_17 = lean_ctor_get(x_1, 2);
if (lean_obj_tag(x_15) == 0)
{
lean_object* x_31; 
x_31 = lean_box(0);
x_25 = x_31;
goto block_30;
}
else
{
lean_object* x_32; lean_object* x_33; 
x_32 = lean_ctor_get(x_15, 0);
lean_inc_ref(x_3);
lean_inc(x_2);
x_33 = lp_dasmodel_evalVibrato(x_32, x_2, x_3, x_4, x_5);
x_25 = x_33;
goto block_30;
}
block_14:
{
lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_11 = l_List_appendTR___redArg(x_8, x_7);
x_12 = l_List_appendTR___redArg(x_11, x_10);
x_13 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_13, 0, x_12);
lean_ctor_set(x_13, 1, x_9);
return x_13;
}
block_24:
{
if (lean_obj_tag(x_17) == 0)
{
lean_object* x_21; 
lean_dec_ref(x_4);
lean_dec(x_2);
x_21 = lean_box(0);
x_7 = x_19;
x_8 = x_18;
x_9 = x_20;
x_10 = x_21;
goto block_14;
}
else
{
lean_object* x_22; lean_object* x_23; 
x_22 = lean_ctor_get(x_17, 0);
lean_inc_ref(x_20);
x_23 = lp_dasmodel_evalArpeggio(x_22, x_2, x_20, x_4, x_5);
x_7 = x_19;
x_8 = x_18;
x_9 = x_20;
x_10 = x_23;
goto block_14;
}
}
block_30:
{
if (lean_obj_tag(x_16) == 0)
{
lean_object* x_26; 
x_26 = lean_box(0);
x_18 = x_25;
x_19 = x_26;
x_20 = x_3;
goto block_24;
}
else
{
lean_object* x_27; lean_object* x_28; lean_object* x_29; 
lean_inc(x_2);
x_27 = lp_dasmodel_evalFreqSlide___redArg(x_2, x_3, x_6);
x_28 = lean_ctor_get(x_27, 0);
lean_inc(x_28);
x_29 = lean_ctor_get(x_27, 1);
lean_inc(x_29);
lean_dec_ref(x_27);
x_18 = x_25;
x_19 = x_28;
x_20 = x_29;
goto block_24;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_evalEffectChain___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel_evalEffectChain(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_6);
lean_dec_ref(x_5);
lean_dec_ref(x_1);
return x_7;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_SID(uint8_t builtin);
lean_object* initialize_dasmodel_State(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_Effects(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_SID(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_State(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
