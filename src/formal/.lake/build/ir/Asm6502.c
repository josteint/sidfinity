// Lean compiler output
// Module: Asm6502
// Imports: public import Init
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
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorIdx(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "AddrMode.acc"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__0 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__0_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__0_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__1 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__1_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "AddrMode.impl"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__2 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__2_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__2_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__3 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__3_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "AddrMode.imm"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__4 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__4_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__4_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__5 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__5_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__5_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__6 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__6_value;
lean_object* lean_nat_to_int(lean_object*);
static lean_once_cell_t lp_dasmodel_instReprAddrMode_repr___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprAddrMode_repr___closed__7;
static lean_once_cell_t lp_dasmodel_instReprAddrMode_repr___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprAddrMode_repr___closed__8;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 12, .m_capacity = 12, .m_length = 11, .m_data = "AddrMode.zp"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__9 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__9_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__9_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__10 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__10_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__10_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__11 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__11_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "AddrMode.zpX"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__12 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__12_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__12_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__13 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__13_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__13_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__14 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__14_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "AddrMode.zpY"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__15 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__15_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__15_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__16 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__16_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__16_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__17 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__17_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "AddrMode.abs"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__18 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__18_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__18_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__19 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__19_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__19_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__20 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__20_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "AddrMode.absX"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__21 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__21_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__21_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__22 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__22_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__22_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__23 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__23_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "AddrMode.absY"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__24 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__24_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__24_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__25 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__25_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__26_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__25_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__26 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__26_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__27_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "AddrMode.ind"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__27 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__27_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__27_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__28 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__28_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__28_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__29 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__29_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__30_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "AddrMode.indX"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__30 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__30_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__31_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__30_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__31 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__31_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__32_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__31_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__32 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__32_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__33_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 14, .m_capacity = 14, .m_length = 13, .m_data = "AddrMode.indY"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__33 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__33_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__34_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__33_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__34 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__34_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__35_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__34_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__35 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__35_value;
static const lean_string_object lp_dasmodel_instReprAddrMode_repr___closed__36_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "AddrMode.rel"};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__36 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__36_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__37_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__36_value)}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__37 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__37_value;
static const lean_ctor_object lp_dasmodel_instReprAddrMode_repr___closed__38_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__37_value),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_instReprAddrMode_repr___closed__38 = (const lean_object*)&lp_dasmodel_instReprAddrMode_repr___closed__38_value;
static lean_once_cell_t lp_dasmodel_instReprAddrMode_repr___closed__39_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprAddrMode_repr___closed__39;
lean_object* l_Repr_addAppParen(lean_object*, lean_object*);
lean_object* lean_uint8_to_nat(uint8_t);
lean_object* l_Nat_reprFast(lean_object*);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
lean_object* lean_uint16_to_nat(uint16_t);
lean_object* lean_int8_to_int(uint8_t);
uint8_t lean_int_dec_lt(lean_object*, lean_object*);
lean_object* l_Int_repr(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprAddrMode_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprAddrMode_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_instReprAddrMode___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_instReprAddrMode_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_instReprAddrMode___closed__0 = (const lean_object*)&lp_dasmodel_instReprAddrMode___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_instReprAddrMode = (const lean_object*)&lp_dasmodel_instReprAddrMode___closed__0_value;
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorIdx(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_toCtorIdx(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_toCtorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim(lean_object*, lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim(lean_object*, uint8_t, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.LDA"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__0 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__0_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__0_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__1 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__1_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.LDX"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__2 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__2_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__2_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__3 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__3_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.LDY"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__4 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__4_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__4_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__5 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__5_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.STA"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__6 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__6_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__6_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__7 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__7_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.STX"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__8 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__8_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__8_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__9 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__9_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.STY"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__10 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__10_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__10_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__11 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__11_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.ADC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__12 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__12_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__12_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__13 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__13_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.SBC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__14 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__14_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__14_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__15 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__15_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.AND"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__16 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__16_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__16_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__17 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__17_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.ORA"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__18 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__18_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__18_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__19 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__19_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.EOR"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__20 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__20_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__21_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__20_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__21 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__21_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.CMP"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__22 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__22_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__22_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__23 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__23_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.CPX"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__24 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__24_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__25_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__24_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__25 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__25_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__26_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.CPY"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__26 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__26_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__27_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__26_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__27 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__27_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.INC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__28 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__28_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__29_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__28_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__29 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__29_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__30_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.DEC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__30 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__30_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__31_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__30_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__31 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__31_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__32_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.INX"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__32 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__32_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__33_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__32_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__33 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__33_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__34_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.DEX"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__34 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__34_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__35_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__34_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__35 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__35_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__36_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.INY"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__36 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__36_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__37_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__36_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__37 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__37_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__38_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.DEY"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__38 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__38_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__39_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__38_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__39 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__39_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__40_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.ASL"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__40 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__40_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__41_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__40_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__41 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__41_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__42_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.LSR"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__42 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__42_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__43_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__42_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__43 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__43_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__44_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.ROL"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__44 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__44_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__45_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__44_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__45 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__45_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__46_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.ROR"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__46 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__46_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__47_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__46_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__47 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__47_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__48_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BCC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__48 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__48_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__49_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__48_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__49 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__49_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__50_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BCS"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__50 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__50_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__51_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__50_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__51 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__51_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__52_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BEQ"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__52 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__52_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__53_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__52_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__53 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__53_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__54_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BNE"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__54 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__54_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__55_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__54_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__55 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__55_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__56_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BMI"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__56 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__56_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__57_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__56_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__57 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__57_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__58_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BPL"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__58 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__58_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__59_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__58_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__59 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__59_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__60_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BVC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__60 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__60_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__61_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__60_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__61 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__61_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__62_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BVS"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__62 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__62_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__63_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__62_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__63 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__63_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__64_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.JMP"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__64 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__64_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__65_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__64_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__65 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__65_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__66_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.JSR"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__66 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__66_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__67_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__66_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__67 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__67_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__68_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.RTS"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__68 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__68_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__69_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__68_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__69 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__69_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__70_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.RTI"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__70 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__70_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__71_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__70_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__71 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__71_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__72_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.PHA"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__72 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__72_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__73_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__72_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__73 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__73_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__74_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.PLA"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__74 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__74_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__75_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__74_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__75 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__75_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__76_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.PHP"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__76 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__76_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__77_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__76_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__77 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__77_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__78_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.PLP"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__78 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__78_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__79_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__78_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__79 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__79_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__80_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.TAX"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__80 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__80_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__81_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__80_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__81 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__81_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__82_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.TAY"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__82 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__82_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__83_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__82_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__83 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__83_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__84_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.TXA"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__84 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__84_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__85_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__84_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__85 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__85_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__86_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.TYA"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__86 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__86_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__87_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__86_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__87 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__87_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__88_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.TXS"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__88 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__88_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__89_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__88_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__89 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__89_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__90_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.TSX"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__90 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__90_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__91_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__90_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__91 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__91_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__92_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.CLC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__92 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__92_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__93_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__92_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__93 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__93_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__94_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.SEC"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__94 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__94_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__95_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__94_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__95 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__95_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__96_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.CLI"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__96 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__96_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__97_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__96_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__97 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__97_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__98_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.SEI"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__98 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__98_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__99_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__98_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__99 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__99_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__100_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.CLV"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__100 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__100_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__101_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__100_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__101 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__101_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__102_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.CLD"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__102 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__102_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__103_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__102_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__103 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__103_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__104_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.SED"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__104 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__104_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__105_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__104_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__105 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__105_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__106_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BIT"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__106 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__106_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__107_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__106_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__107 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__107_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__108_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.NOP"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__108 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__108_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__109_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__108_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__109 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__109_value;
static const lean_string_object lp_dasmodel_instReprMnemonic_repr___closed__110_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 13, .m_capacity = 13, .m_length = 12, .m_data = "Mnemonic.BRK"};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__110 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__110_value;
static const lean_ctor_object lp_dasmodel_instReprMnemonic_repr___closed__111_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__110_value)}};
static const lean_object* lp_dasmodel_instReprMnemonic_repr___closed__111 = (const lean_object*)&lp_dasmodel_instReprMnemonic_repr___closed__111_value;
LEAN_EXPORT lean_object* lp_dasmodel_instReprMnemonic_repr(uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprMnemonic_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_instReprMnemonic___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_instReprMnemonic_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_instReprMnemonic___closed__0 = (const lean_object*)&lp_dasmodel_instReprMnemonic___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_instReprMnemonic = (const lean_object*)&lp_dasmodel_instReprMnemonic___closed__0_value;
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel_instBEqMnemonic_beq(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_instBEqMnemonic_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_instBEqMnemonic___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_instBEqMnemonic_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_instBEqMnemonic___closed__0 = (const lean_object*)&lp_dasmodel_instBEqMnemonic___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_instBEqMnemonic = (const lean_object*)&lp_dasmodel_instBEqMnemonic___closed__0_value;
static const lean_string_object lp_dasmodel_instReprInstruction_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "{ "};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__0 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__0_value;
static const lean_string_object lp_dasmodel_instReprInstruction_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "mnemonic"};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__1 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__1_value;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__1_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__2 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__2_value;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__2_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__3 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__3_value;
static const lean_string_object lp_dasmodel_instReprInstruction_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " := "};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__4 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__4_value;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__4_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__5 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__5_value;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__3_value),((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__5_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__6 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__6_value;
static lean_once_cell_t lp_dasmodel_instReprInstruction_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__7;
static const lean_string_object lp_dasmodel_instReprInstruction_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ","};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__8 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__8_value;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__8_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__9 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__9_value;
static const lean_string_object lp_dasmodel_instReprInstruction_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "mode"};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__10 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__10_value;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__10_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__11 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__11_value;
static lean_once_cell_t lp_dasmodel_instReprInstruction_repr___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__12;
static const lean_string_object lp_dasmodel_instReprInstruction_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " }"};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__13 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__13_value;
lean_object* lean_string_length(lean_object*);
static lean_once_cell_t lp_dasmodel_instReprInstruction_repr___redArg___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__14;
static lean_once_cell_t lp_dasmodel_instReprInstruction_repr___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__15;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__0_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__16 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__16_value;
static const lean_ctor_object lp_dasmodel_instReprInstruction_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__13_value)}};
static const lean_object* lp_dasmodel_instReprInstruction_repr___redArg___closed__17 = (const lean_object*)&lp_dasmodel_instReprInstruction_repr___redArg___closed__17_value;
LEAN_EXPORT lean_object* lp_dasmodel_instReprInstruction_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprInstruction_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprInstruction_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_instReprInstruction___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_instReprInstruction_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_instReprInstruction___closed__0 = (const lean_object*)&lp_dasmodel_instReprInstruction___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_instReprInstruction = (const lean_object*)&lp_dasmodel_instReprInstruction___closed__0_value;
static lean_once_cell_t lp_dasmodel_opcode___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__0;
static lean_once_cell_t lp_dasmodel_opcode___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__1;
static lean_once_cell_t lp_dasmodel_opcode___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__2;
static lean_once_cell_t lp_dasmodel_opcode___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__3;
static lean_once_cell_t lp_dasmodel_opcode___closed__4_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__4;
static lean_once_cell_t lp_dasmodel_opcode___closed__5_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__5;
static lean_once_cell_t lp_dasmodel_opcode___closed__6_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__6;
static lean_once_cell_t lp_dasmodel_opcode___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__7;
static lean_once_cell_t lp_dasmodel_opcode___closed__8_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__8;
static lean_once_cell_t lp_dasmodel_opcode___closed__9_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__9;
static lean_once_cell_t lp_dasmodel_opcode___closed__10_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__10;
static lean_once_cell_t lp_dasmodel_opcode___closed__11_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__11;
static lean_once_cell_t lp_dasmodel_opcode___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__12;
static lean_once_cell_t lp_dasmodel_opcode___closed__13_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__13;
static lean_once_cell_t lp_dasmodel_opcode___closed__14_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__14;
static lean_once_cell_t lp_dasmodel_opcode___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__15;
static lean_once_cell_t lp_dasmodel_opcode___closed__16_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__16;
static lean_once_cell_t lp_dasmodel_opcode___closed__17_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__17;
static lean_once_cell_t lp_dasmodel_opcode___closed__18_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__18;
static lean_once_cell_t lp_dasmodel_opcode___closed__19_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__19;
static lean_once_cell_t lp_dasmodel_opcode___closed__20_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__20;
static lean_once_cell_t lp_dasmodel_opcode___closed__21_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__21;
static lean_once_cell_t lp_dasmodel_opcode___closed__22_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__22;
static lean_once_cell_t lp_dasmodel_opcode___closed__23_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__23;
static lean_once_cell_t lp_dasmodel_opcode___closed__24_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__24;
static lean_once_cell_t lp_dasmodel_opcode___closed__25_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__25;
static lean_once_cell_t lp_dasmodel_opcode___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__26;
static lean_once_cell_t lp_dasmodel_opcode___closed__27_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__27;
static lean_once_cell_t lp_dasmodel_opcode___closed__28_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__28;
static lean_once_cell_t lp_dasmodel_opcode___closed__29_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__29;
static lean_once_cell_t lp_dasmodel_opcode___closed__30_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__30;
static lean_once_cell_t lp_dasmodel_opcode___closed__31_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__31;
static lean_once_cell_t lp_dasmodel_opcode___closed__32_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__32;
static lean_once_cell_t lp_dasmodel_opcode___closed__33_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__33;
static lean_once_cell_t lp_dasmodel_opcode___closed__34_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__34;
static lean_once_cell_t lp_dasmodel_opcode___closed__35_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__35;
static lean_once_cell_t lp_dasmodel_opcode___closed__36_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__36;
static lean_once_cell_t lp_dasmodel_opcode___closed__37_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__37;
static lean_once_cell_t lp_dasmodel_opcode___closed__38_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__38;
static lean_once_cell_t lp_dasmodel_opcode___closed__39_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__39;
static lean_once_cell_t lp_dasmodel_opcode___closed__40_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__40;
static lean_once_cell_t lp_dasmodel_opcode___closed__41_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__41;
static lean_once_cell_t lp_dasmodel_opcode___closed__42_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__42;
static lean_once_cell_t lp_dasmodel_opcode___closed__43_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__43;
static lean_once_cell_t lp_dasmodel_opcode___closed__44_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__44;
static lean_once_cell_t lp_dasmodel_opcode___closed__45_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__45;
static lean_once_cell_t lp_dasmodel_opcode___closed__46_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__46;
static lean_once_cell_t lp_dasmodel_opcode___closed__47_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__47;
static lean_once_cell_t lp_dasmodel_opcode___closed__48_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__48;
static lean_once_cell_t lp_dasmodel_opcode___closed__49_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__49;
static lean_once_cell_t lp_dasmodel_opcode___closed__50_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__50;
static lean_once_cell_t lp_dasmodel_opcode___closed__51_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__51;
static lean_once_cell_t lp_dasmodel_opcode___closed__52_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__52;
static lean_once_cell_t lp_dasmodel_opcode___closed__53_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__53;
static lean_once_cell_t lp_dasmodel_opcode___closed__54_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__54;
static lean_once_cell_t lp_dasmodel_opcode___closed__55_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__55;
static lean_once_cell_t lp_dasmodel_opcode___closed__56_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__56;
static lean_once_cell_t lp_dasmodel_opcode___closed__57_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__57;
static lean_once_cell_t lp_dasmodel_opcode___closed__58_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__58;
static lean_once_cell_t lp_dasmodel_opcode___closed__59_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__59;
static lean_once_cell_t lp_dasmodel_opcode___closed__60_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__60;
static lean_once_cell_t lp_dasmodel_opcode___closed__61_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__61;
static lean_once_cell_t lp_dasmodel_opcode___closed__62_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__62;
static lean_once_cell_t lp_dasmodel_opcode___closed__63_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__63;
static lean_once_cell_t lp_dasmodel_opcode___closed__64_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__64;
static lean_once_cell_t lp_dasmodel_opcode___closed__65_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__65;
static lean_once_cell_t lp_dasmodel_opcode___closed__66_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__66;
static lean_once_cell_t lp_dasmodel_opcode___closed__67_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__67;
static lean_once_cell_t lp_dasmodel_opcode___closed__68_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__68;
static lean_once_cell_t lp_dasmodel_opcode___closed__69_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__69;
static lean_once_cell_t lp_dasmodel_opcode___closed__70_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__70;
static lean_once_cell_t lp_dasmodel_opcode___closed__71_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__71;
static lean_once_cell_t lp_dasmodel_opcode___closed__72_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__72;
static lean_once_cell_t lp_dasmodel_opcode___closed__73_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__73;
static lean_once_cell_t lp_dasmodel_opcode___closed__74_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__74;
static lean_once_cell_t lp_dasmodel_opcode___closed__75_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__75;
static lean_once_cell_t lp_dasmodel_opcode___closed__76_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__76;
static lean_once_cell_t lp_dasmodel_opcode___closed__77_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__77;
static lean_once_cell_t lp_dasmodel_opcode___closed__78_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__78;
static lean_once_cell_t lp_dasmodel_opcode___closed__79_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__79;
static lean_once_cell_t lp_dasmodel_opcode___closed__80_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__80;
static lean_once_cell_t lp_dasmodel_opcode___closed__81_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__81;
static lean_once_cell_t lp_dasmodel_opcode___closed__82_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_opcode___closed__82;
LEAN_EXPORT lean_object* lp_dasmodel_opcode(uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_opcode___boxed(lean_object*, lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
static lean_once_cell_t lp_dasmodel_operandBytes___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_operandBytes___closed__0;
static lean_once_cell_t lp_dasmodel_operandBytes___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_operandBytes___closed__1;
static lean_once_cell_t lp_dasmodel_operandBytes___closed__2_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_operandBytes___closed__2;
lean_object* lean_array_push(lean_object*, lean_object*);
uint8_t lean_uint16_to_uint8(uint16_t);
uint16_t lean_uint16_shift_right(uint16_t, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_operandBytes(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_operandBytes___boxed(lean_object*);
lean_object* l_Array_append___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_assembleInst(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_assembleInst___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_foldlM___at___00assemble_spec__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_List_foldlM___at___00assemble_spec__0___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_assemble(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_assemble___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__abs(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__abs___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__abs(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__abs___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absX(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absX___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absY(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absY___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absX(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absX___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absY(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absY___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_inc__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_inc__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_dec__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_dec__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_cmp__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_cmp__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_and__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_and__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__imm___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_bne(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_bne___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_beq(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_beq___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_bmi(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_bmi___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_bpl(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_bpl___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_bcc(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_bcc___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_bcs(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_bcs___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_jmp(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_jmp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_jsr(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_jsr___boxed(lean_object*);
static const lean_ctor_object lp_dasmodel_I_rts___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(34, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_rts___closed__0 = (const lean_object*)&lp_dasmodel_I_rts___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_rts = (const lean_object*)&lp_dasmodel_I_rts___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_inx___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(16, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_inx___closed__0 = (const lean_object*)&lp_dasmodel_I_inx___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_inx = (const lean_object*)&lp_dasmodel_I_inx___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_dex___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(17, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_dex___closed__0 = (const lean_object*)&lp_dasmodel_I_dex___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_dex = (const lean_object*)&lp_dasmodel_I_dex___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_iny___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(18, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_iny___closed__0 = (const lean_object*)&lp_dasmodel_I_iny___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_iny = (const lean_object*)&lp_dasmodel_I_iny___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_dey___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(19, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_dey___closed__0 = (const lean_object*)&lp_dasmodel_I_dey___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_dey = (const lean_object*)&lp_dasmodel_I_dey___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_tax___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(40, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_tax___closed__0 = (const lean_object*)&lp_dasmodel_I_tax___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_tax = (const lean_object*)&lp_dasmodel_I_tax___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_tay___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(41, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_tay___closed__0 = (const lean_object*)&lp_dasmodel_I_tay___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_tay = (const lean_object*)&lp_dasmodel_I_tay___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_txa___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(42, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_txa___closed__0 = (const lean_object*)&lp_dasmodel_I_txa___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_txa = (const lean_object*)&lp_dasmodel_I_txa___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_tya___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(43, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_tya___closed__0 = (const lean_object*)&lp_dasmodel_I_tya___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_tya = (const lean_object*)&lp_dasmodel_I_tya___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_clc___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(46, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_clc___closed__0 = (const lean_object*)&lp_dasmodel_I_clc___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_clc = (const lean_object*)&lp_dasmodel_I_clc___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_sec___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(47, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_sec___closed__0 = (const lean_object*)&lp_dasmodel_I_sec___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_sec = (const lean_object*)&lp_dasmodel_I_sec___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_sei___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(49, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_sei___closed__0 = (const lean_object*)&lp_dasmodel_I_sei___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_sei = (const lean_object*)&lp_dasmodel_I_sei___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_pha___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(36, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_pha___closed__0 = (const lean_object*)&lp_dasmodel_I_pha___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_pha = (const lean_object*)&lp_dasmodel_I_pha___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_pla___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(37, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_pla___closed__0 = (const lean_object*)&lp_dasmodel_I_pla___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_pla = (const lean_object*)&lp_dasmodel_I_pla___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_nop___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(10) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(54, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_nop___closed__0 = (const lean_object*)&lp_dasmodel_I_nop___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_nop = (const lean_object*)&lp_dasmodel_I_nop___closed__0_value;
LEAN_EXPORT lean_object* lp_dasmodel_I_stx__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_stx__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_sty__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_sty__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__zp(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__zp___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_I_eor__imm(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_I_eor__imm___boxed(lean_object*);
static const lean_ctor_object lp_dasmodel_I_asl__a___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(11) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(20, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_asl__a___closed__0 = (const lean_object*)&lp_dasmodel_I_asl__a___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_asl__a = (const lean_object*)&lp_dasmodel_I_asl__a___closed__0_value;
static const lean_ctor_object lp_dasmodel_I_lsr__a___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 8, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(11) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(21, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_I_lsr__a___closed__0 = (const lean_object*)&lp_dasmodel_I_lsr__a___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_I_lsr__a = (const lean_object*)&lp_dasmodel_I_lsr__a___closed__0_value;
LEAN_EXPORT lean_object* lp_dasmodel_rawByte(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_rawByte___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_rawWord(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_rawWord___boxed(lean_object*);
lean_object* lean_array_mk(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_rawBytes(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorIdx(lean_object* x_1) {
_start:
{
switch (lean_obj_tag(x_1)) {
case 0:
{
lean_object* x_2; 
x_2 = lean_unsigned_to_nat(0u);
return x_2;
}
case 1:
{
lean_object* x_3; 
x_3 = lean_unsigned_to_nat(1u);
return x_3;
}
case 2:
{
lean_object* x_4; 
x_4 = lean_unsigned_to_nat(2u);
return x_4;
}
case 3:
{
lean_object* x_5; 
x_5 = lean_unsigned_to_nat(3u);
return x_5;
}
case 4:
{
lean_object* x_6; 
x_6 = lean_unsigned_to_nat(4u);
return x_6;
}
case 5:
{
lean_object* x_7; 
x_7 = lean_unsigned_to_nat(5u);
return x_7;
}
case 6:
{
lean_object* x_8; 
x_8 = lean_unsigned_to_nat(6u);
return x_8;
}
case 7:
{
lean_object* x_9; 
x_9 = lean_unsigned_to_nat(7u);
return x_9;
}
case 8:
{
lean_object* x_10; 
x_10 = lean_unsigned_to_nat(8u);
return x_10;
}
case 9:
{
lean_object* x_11; 
x_11 = lean_unsigned_to_nat(9u);
return x_11;
}
case 10:
{
lean_object* x_12; 
x_12 = lean_unsigned_to_nat(10u);
return x_12;
}
case 11:
{
lean_object* x_13; 
x_13 = lean_unsigned_to_nat(11u);
return x_13;
}
default: 
{
lean_object* x_14; 
x_14 = lean_unsigned_to_nat(12u);
return x_14;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorIdx___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_AddrMode_ctorIdx(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
switch (lean_obj_tag(x_1)) {
case 0:
{
uint8_t x_3; lean_object* x_4; lean_object* x_5; 
x_3 = lean_ctor_get_uint8(x_1, 0);
x_4 = lean_box(x_3);
x_5 = lean_apply_1(x_2, x_4);
return x_5;
}
case 1:
{
uint8_t x_6; lean_object* x_7; lean_object* x_8; 
x_6 = lean_ctor_get_uint8(x_1, 0);
x_7 = lean_box(x_6);
x_8 = lean_apply_1(x_2, x_7);
return x_8;
}
case 2:
{
uint8_t x_9; lean_object* x_10; lean_object* x_11; 
x_9 = lean_ctor_get_uint8(x_1, 0);
x_10 = lean_box(x_9);
x_11 = lean_apply_1(x_2, x_10);
return x_11;
}
case 3:
{
uint8_t x_12; lean_object* x_13; lean_object* x_14; 
x_12 = lean_ctor_get_uint8(x_1, 0);
x_13 = lean_box(x_12);
x_14 = lean_apply_1(x_2, x_13);
return x_14;
}
case 4:
{
uint16_t x_15; lean_object* x_16; lean_object* x_17; 
x_15 = lean_ctor_get_uint16(x_1, 0);
x_16 = lean_box(x_15);
x_17 = lean_apply_1(x_2, x_16);
return x_17;
}
case 5:
{
uint16_t x_18; lean_object* x_19; lean_object* x_20; 
x_18 = lean_ctor_get_uint16(x_1, 0);
x_19 = lean_box(x_18);
x_20 = lean_apply_1(x_2, x_19);
return x_20;
}
case 6:
{
uint16_t x_21; lean_object* x_22; lean_object* x_23; 
x_21 = lean_ctor_get_uint16(x_1, 0);
x_22 = lean_box(x_21);
x_23 = lean_apply_1(x_2, x_22);
return x_23;
}
case 7:
{
uint16_t x_24; lean_object* x_25; lean_object* x_26; 
x_24 = lean_ctor_get_uint16(x_1, 0);
x_25 = lean_box(x_24);
x_26 = lean_apply_1(x_2, x_25);
return x_26;
}
case 8:
{
uint8_t x_27; lean_object* x_28; lean_object* x_29; 
x_27 = lean_ctor_get_uint8(x_1, 0);
x_28 = lean_box(x_27);
x_29 = lean_apply_1(x_2, x_28);
return x_29;
}
case 9:
{
uint8_t x_30; lean_object* x_31; lean_object* x_32; 
x_30 = lean_ctor_get_uint8(x_1, 0);
x_31 = lean_box(x_30);
x_32 = lean_apply_1(x_2, x_31);
return x_32;
}
case 12:
{
uint8_t x_33; lean_object* x_34; lean_object* x_35; 
x_33 = lean_ctor_get_uint8(x_1, 0);
x_34 = lean_box(x_33);
x_35 = lean_apply_1(x_2, x_34);
return x_35;
}
default: 
{
return x_2;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_AddrMode_ctorElim___redArg(x_3, x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ctorElim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_AddrMode_ctorElim(x_1, x_2, x_3, x_4, x_5);
lean_dec(x_3);
lean_dec(x_2);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_imm_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_imm_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_imm_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_zp_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zp_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_zp_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_zpX_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_zpX_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_zpY_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_zpY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_zpY_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_abs_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_abs_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_abs_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_absX_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_absX_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_absY_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_absY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_absY_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ind_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_ind_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ind_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_indX_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_indX_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_indY_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_indY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_indY_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_impl_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_impl_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_impl_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_acc_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_acc_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_acc_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_AddrMode_rel_elim___redArg(x_1, x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_AddrMode_rel_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_AddrMode_rel_elim(x_1, x_2, x_3, x_4);
lean_dec(x_2);
return x_5;
}
}
static lean_object* _init_lp_dasmodel_instReprAddrMode_repr___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprAddrMode_repr___closed__8(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(1u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprAddrMode_repr___closed__39(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprAddrMode_repr(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_12; lean_object* x_19; 
switch (lean_obj_tag(x_1)) {
case 0:
{
uint8_t x_26; lean_object* x_27; lean_object* x_38; uint8_t x_39; 
x_26 = lean_ctor_get_uint8(x_1, 0);
x_38 = lean_unsigned_to_nat(1024u);
x_39 = lean_nat_dec_le(x_38, x_2);
if (x_39 == 0)
{
lean_object* x_40; 
x_40 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_27 = x_40;
goto block_37;
}
else
{
lean_object* x_41; 
x_41 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_27 = x_41;
goto block_37;
}
block_37:
{
lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; uint8_t x_34; lean_object* x_35; lean_object* x_36; 
x_28 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__6));
x_29 = lean_uint8_to_nat(x_26);
x_30 = l_Nat_reprFast(x_29);
x_31 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_31, 0, x_30);
x_32 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_32, 0, x_28);
lean_ctor_set(x_32, 1, x_31);
x_33 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_33, 0, x_27);
lean_ctor_set(x_33, 1, x_32);
x_34 = 0;
x_35 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_35, 0, x_33);
lean_ctor_set_uint8(x_35, sizeof(void*)*1, x_34);
x_36 = l_Repr_addAppParen(x_35, x_2);
return x_36;
}
}
case 1:
{
uint8_t x_42; lean_object* x_43; lean_object* x_54; uint8_t x_55; 
x_42 = lean_ctor_get_uint8(x_1, 0);
x_54 = lean_unsigned_to_nat(1024u);
x_55 = lean_nat_dec_le(x_54, x_2);
if (x_55 == 0)
{
lean_object* x_56; 
x_56 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_43 = x_56;
goto block_53;
}
else
{
lean_object* x_57; 
x_57 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_43 = x_57;
goto block_53;
}
block_53:
{
lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; uint8_t x_50; lean_object* x_51; lean_object* x_52; 
x_44 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__11));
x_45 = lean_uint8_to_nat(x_42);
x_46 = l_Nat_reprFast(x_45);
x_47 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_47, 0, x_46);
x_48 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_48, 0, x_44);
lean_ctor_set(x_48, 1, x_47);
x_49 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_49, 0, x_43);
lean_ctor_set(x_49, 1, x_48);
x_50 = 0;
x_51 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_51, 0, x_49);
lean_ctor_set_uint8(x_51, sizeof(void*)*1, x_50);
x_52 = l_Repr_addAppParen(x_51, x_2);
return x_52;
}
}
case 2:
{
uint8_t x_58; lean_object* x_59; lean_object* x_70; uint8_t x_71; 
x_58 = lean_ctor_get_uint8(x_1, 0);
x_70 = lean_unsigned_to_nat(1024u);
x_71 = lean_nat_dec_le(x_70, x_2);
if (x_71 == 0)
{
lean_object* x_72; 
x_72 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_59 = x_72;
goto block_69;
}
else
{
lean_object* x_73; 
x_73 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_59 = x_73;
goto block_69;
}
block_69:
{
lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; uint8_t x_66; lean_object* x_67; lean_object* x_68; 
x_60 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__14));
x_61 = lean_uint8_to_nat(x_58);
x_62 = l_Nat_reprFast(x_61);
x_63 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_63, 0, x_62);
x_64 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_64, 0, x_60);
lean_ctor_set(x_64, 1, x_63);
x_65 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_65, 0, x_59);
lean_ctor_set(x_65, 1, x_64);
x_66 = 0;
x_67 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_67, 0, x_65);
lean_ctor_set_uint8(x_67, sizeof(void*)*1, x_66);
x_68 = l_Repr_addAppParen(x_67, x_2);
return x_68;
}
}
case 3:
{
uint8_t x_74; lean_object* x_75; lean_object* x_86; uint8_t x_87; 
x_74 = lean_ctor_get_uint8(x_1, 0);
x_86 = lean_unsigned_to_nat(1024u);
x_87 = lean_nat_dec_le(x_86, x_2);
if (x_87 == 0)
{
lean_object* x_88; 
x_88 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_75 = x_88;
goto block_85;
}
else
{
lean_object* x_89; 
x_89 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_75 = x_89;
goto block_85;
}
block_85:
{
lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; lean_object* x_81; uint8_t x_82; lean_object* x_83; lean_object* x_84; 
x_76 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__17));
x_77 = lean_uint8_to_nat(x_74);
x_78 = l_Nat_reprFast(x_77);
x_79 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_79, 0, x_78);
x_80 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_80, 0, x_76);
lean_ctor_set(x_80, 1, x_79);
x_81 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_81, 0, x_75);
lean_ctor_set(x_81, 1, x_80);
x_82 = 0;
x_83 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_83, 0, x_81);
lean_ctor_set_uint8(x_83, sizeof(void*)*1, x_82);
x_84 = l_Repr_addAppParen(x_83, x_2);
return x_84;
}
}
case 4:
{
uint16_t x_90; lean_object* x_91; lean_object* x_102; uint8_t x_103; 
x_90 = lean_ctor_get_uint16(x_1, 0);
x_102 = lean_unsigned_to_nat(1024u);
x_103 = lean_nat_dec_le(x_102, x_2);
if (x_103 == 0)
{
lean_object* x_104; 
x_104 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_91 = x_104;
goto block_101;
}
else
{
lean_object* x_105; 
x_105 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_91 = x_105;
goto block_101;
}
block_101:
{
lean_object* x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; lean_object* x_96; lean_object* x_97; uint8_t x_98; lean_object* x_99; lean_object* x_100; 
x_92 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__20));
x_93 = lean_uint16_to_nat(x_90);
x_94 = l_Nat_reprFast(x_93);
x_95 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_95, 0, x_94);
x_96 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_96, 0, x_92);
lean_ctor_set(x_96, 1, x_95);
x_97 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_97, 0, x_91);
lean_ctor_set(x_97, 1, x_96);
x_98 = 0;
x_99 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_99, 0, x_97);
lean_ctor_set_uint8(x_99, sizeof(void*)*1, x_98);
x_100 = l_Repr_addAppParen(x_99, x_2);
return x_100;
}
}
case 5:
{
uint16_t x_106; lean_object* x_107; lean_object* x_118; uint8_t x_119; 
x_106 = lean_ctor_get_uint16(x_1, 0);
x_118 = lean_unsigned_to_nat(1024u);
x_119 = lean_nat_dec_le(x_118, x_2);
if (x_119 == 0)
{
lean_object* x_120; 
x_120 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_107 = x_120;
goto block_117;
}
else
{
lean_object* x_121; 
x_121 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_107 = x_121;
goto block_117;
}
block_117:
{
lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; uint8_t x_114; lean_object* x_115; lean_object* x_116; 
x_108 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__23));
x_109 = lean_uint16_to_nat(x_106);
x_110 = l_Nat_reprFast(x_109);
x_111 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_111, 0, x_110);
x_112 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_112, 0, x_108);
lean_ctor_set(x_112, 1, x_111);
x_113 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_113, 0, x_107);
lean_ctor_set(x_113, 1, x_112);
x_114 = 0;
x_115 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_115, 0, x_113);
lean_ctor_set_uint8(x_115, sizeof(void*)*1, x_114);
x_116 = l_Repr_addAppParen(x_115, x_2);
return x_116;
}
}
case 6:
{
uint16_t x_122; lean_object* x_123; lean_object* x_134; uint8_t x_135; 
x_122 = lean_ctor_get_uint16(x_1, 0);
x_134 = lean_unsigned_to_nat(1024u);
x_135 = lean_nat_dec_le(x_134, x_2);
if (x_135 == 0)
{
lean_object* x_136; 
x_136 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_123 = x_136;
goto block_133;
}
else
{
lean_object* x_137; 
x_137 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_123 = x_137;
goto block_133;
}
block_133:
{
lean_object* x_124; lean_object* x_125; lean_object* x_126; lean_object* x_127; lean_object* x_128; lean_object* x_129; uint8_t x_130; lean_object* x_131; lean_object* x_132; 
x_124 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__26));
x_125 = lean_uint16_to_nat(x_122);
x_126 = l_Nat_reprFast(x_125);
x_127 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_127, 0, x_126);
x_128 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_128, 0, x_124);
lean_ctor_set(x_128, 1, x_127);
x_129 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_129, 0, x_123);
lean_ctor_set(x_129, 1, x_128);
x_130 = 0;
x_131 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_131, 0, x_129);
lean_ctor_set_uint8(x_131, sizeof(void*)*1, x_130);
x_132 = l_Repr_addAppParen(x_131, x_2);
return x_132;
}
}
case 7:
{
uint16_t x_138; lean_object* x_139; lean_object* x_150; uint8_t x_151; 
x_138 = lean_ctor_get_uint16(x_1, 0);
x_150 = lean_unsigned_to_nat(1024u);
x_151 = lean_nat_dec_le(x_150, x_2);
if (x_151 == 0)
{
lean_object* x_152; 
x_152 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_139 = x_152;
goto block_149;
}
else
{
lean_object* x_153; 
x_153 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_139 = x_153;
goto block_149;
}
block_149:
{
lean_object* x_140; lean_object* x_141; lean_object* x_142; lean_object* x_143; lean_object* x_144; lean_object* x_145; uint8_t x_146; lean_object* x_147; lean_object* x_148; 
x_140 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__29));
x_141 = lean_uint16_to_nat(x_138);
x_142 = l_Nat_reprFast(x_141);
x_143 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_143, 0, x_142);
x_144 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_144, 0, x_140);
lean_ctor_set(x_144, 1, x_143);
x_145 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_145, 0, x_139);
lean_ctor_set(x_145, 1, x_144);
x_146 = 0;
x_147 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_147, 0, x_145);
lean_ctor_set_uint8(x_147, sizeof(void*)*1, x_146);
x_148 = l_Repr_addAppParen(x_147, x_2);
return x_148;
}
}
case 8:
{
uint8_t x_154; lean_object* x_155; lean_object* x_166; uint8_t x_167; 
x_154 = lean_ctor_get_uint8(x_1, 0);
x_166 = lean_unsigned_to_nat(1024u);
x_167 = lean_nat_dec_le(x_166, x_2);
if (x_167 == 0)
{
lean_object* x_168; 
x_168 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_155 = x_168;
goto block_165;
}
else
{
lean_object* x_169; 
x_169 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_155 = x_169;
goto block_165;
}
block_165:
{
lean_object* x_156; lean_object* x_157; lean_object* x_158; lean_object* x_159; lean_object* x_160; lean_object* x_161; uint8_t x_162; lean_object* x_163; lean_object* x_164; 
x_156 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__32));
x_157 = lean_uint8_to_nat(x_154);
x_158 = l_Nat_reprFast(x_157);
x_159 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_159, 0, x_158);
x_160 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_160, 0, x_156);
lean_ctor_set(x_160, 1, x_159);
x_161 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_161, 0, x_155);
lean_ctor_set(x_161, 1, x_160);
x_162 = 0;
x_163 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_163, 0, x_161);
lean_ctor_set_uint8(x_163, sizeof(void*)*1, x_162);
x_164 = l_Repr_addAppParen(x_163, x_2);
return x_164;
}
}
case 9:
{
uint8_t x_170; lean_object* x_171; lean_object* x_182; uint8_t x_183; 
x_170 = lean_ctor_get_uint8(x_1, 0);
x_182 = lean_unsigned_to_nat(1024u);
x_183 = lean_nat_dec_le(x_182, x_2);
if (x_183 == 0)
{
lean_object* x_184; 
x_184 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_171 = x_184;
goto block_181;
}
else
{
lean_object* x_185; 
x_185 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_171 = x_185;
goto block_181;
}
block_181:
{
lean_object* x_172; lean_object* x_173; lean_object* x_174; lean_object* x_175; lean_object* x_176; lean_object* x_177; uint8_t x_178; lean_object* x_179; lean_object* x_180; 
x_172 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__35));
x_173 = lean_uint8_to_nat(x_170);
x_174 = l_Nat_reprFast(x_173);
x_175 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_175, 0, x_174);
x_176 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_176, 0, x_172);
lean_ctor_set(x_176, 1, x_175);
x_177 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_177, 0, x_171);
lean_ctor_set(x_177, 1, x_176);
x_178 = 0;
x_179 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_179, 0, x_177);
lean_ctor_set_uint8(x_179, sizeof(void*)*1, x_178);
x_180 = l_Repr_addAppParen(x_179, x_2);
return x_180;
}
}
case 10:
{
lean_object* x_186; uint8_t x_187; 
x_186 = lean_unsigned_to_nat(1024u);
x_187 = lean_nat_dec_le(x_186, x_2);
if (x_187 == 0)
{
lean_object* x_188; 
x_188 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_19 = x_188;
goto block_25;
}
else
{
lean_object* x_189; 
x_189 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_19 = x_189;
goto block_25;
}
}
case 11:
{
lean_object* x_190; uint8_t x_191; 
x_190 = lean_unsigned_to_nat(1024u);
x_191 = lean_nat_dec_le(x_190, x_2);
if (x_191 == 0)
{
lean_object* x_192; 
x_192 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_12 = x_192;
goto block_18;
}
else
{
lean_object* x_193; 
x_193 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_12 = x_193;
goto block_18;
}
}
default: 
{
uint8_t x_194; lean_object* x_195; lean_object* x_207; uint8_t x_208; 
x_194 = lean_ctor_get_uint8(x_1, 0);
x_207 = lean_unsigned_to_nat(1024u);
x_208 = lean_nat_dec_le(x_207, x_2);
if (x_208 == 0)
{
lean_object* x_209; 
x_209 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_195 = x_209;
goto block_206;
}
else
{
lean_object* x_210; 
x_210 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_195 = x_210;
goto block_206;
}
block_206:
{
lean_object* x_196; lean_object* x_197; lean_object* x_198; uint8_t x_199; 
x_196 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__38));
x_197 = lean_int8_to_int(x_194);
x_198 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__39, &lp_dasmodel_instReprAddrMode_repr___closed__39_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__39);
x_199 = lean_int_dec_lt(x_197, x_198);
if (x_199 == 0)
{
lean_object* x_200; lean_object* x_201; 
x_200 = l_Int_repr(x_197);
x_201 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_201, 0, x_200);
x_3 = x_196;
x_4 = x_195;
x_5 = x_201;
goto block_11;
}
else
{
lean_object* x_202; lean_object* x_203; lean_object* x_204; lean_object* x_205; 
x_202 = lean_unsigned_to_nat(1024u);
x_203 = l_Int_repr(x_197);
x_204 = lean_alloc_ctor(3, 1, 0);
lean_ctor_set(x_204, 0, x_203);
x_205 = l_Repr_addAppParen(x_204, x_202);
x_3 = x_196;
x_4 = x_195;
x_5 = x_205;
goto block_11;
}
}
}
}
block_11:
{
lean_object* x_6; lean_object* x_7; uint8_t x_8; lean_object* x_9; lean_object* x_10; 
x_6 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_6, 0, x_3);
lean_ctor_set(x_6, 1, x_5);
x_7 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_7, 0, x_4);
lean_ctor_set(x_7, 1, x_6);
x_8 = 0;
x_9 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_9, 0, x_7);
lean_ctor_set_uint8(x_9, sizeof(void*)*1, x_8);
x_10 = l_Repr_addAppParen(x_9, x_2);
return x_10;
}
block_18:
{
lean_object* x_13; lean_object* x_14; uint8_t x_15; lean_object* x_16; lean_object* x_17; 
x_13 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__1));
x_14 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_14, 0, x_12);
lean_ctor_set(x_14, 1, x_13);
x_15 = 0;
x_16 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_16, 0, x_14);
lean_ctor_set_uint8(x_16, sizeof(void*)*1, x_15);
x_17 = l_Repr_addAppParen(x_16, x_2);
return x_17;
}
block_25:
{
lean_object* x_20; lean_object* x_21; uint8_t x_22; lean_object* x_23; lean_object* x_24; 
x_20 = ((lean_object*)(lp_dasmodel_instReprAddrMode_repr___closed__3));
x_21 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_21, 0, x_19);
lean_ctor_set(x_21, 1, x_20);
x_22 = 0;
x_23 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_23, 0, x_21);
lean_ctor_set_uint8(x_23, sizeof(void*)*1, x_22);
x_24 = l_Repr_addAppParen(x_23, x_2);
return x_24;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprAddrMode_repr___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_instReprAddrMode_repr(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorIdx(uint8_t x_1) {
_start:
{
switch (x_1) {
case 0:
{
lean_object* x_2; 
x_2 = lean_unsigned_to_nat(0u);
return x_2;
}
case 1:
{
lean_object* x_3; 
x_3 = lean_unsigned_to_nat(1u);
return x_3;
}
case 2:
{
lean_object* x_4; 
x_4 = lean_unsigned_to_nat(2u);
return x_4;
}
case 3:
{
lean_object* x_5; 
x_5 = lean_unsigned_to_nat(3u);
return x_5;
}
case 4:
{
lean_object* x_6; 
x_6 = lean_unsigned_to_nat(4u);
return x_6;
}
case 5:
{
lean_object* x_7; 
x_7 = lean_unsigned_to_nat(5u);
return x_7;
}
case 6:
{
lean_object* x_8; 
x_8 = lean_unsigned_to_nat(6u);
return x_8;
}
case 7:
{
lean_object* x_9; 
x_9 = lean_unsigned_to_nat(7u);
return x_9;
}
case 8:
{
lean_object* x_10; 
x_10 = lean_unsigned_to_nat(8u);
return x_10;
}
case 9:
{
lean_object* x_11; 
x_11 = lean_unsigned_to_nat(9u);
return x_11;
}
case 10:
{
lean_object* x_12; 
x_12 = lean_unsigned_to_nat(10u);
return x_12;
}
case 11:
{
lean_object* x_13; 
x_13 = lean_unsigned_to_nat(11u);
return x_13;
}
case 12:
{
lean_object* x_14; 
x_14 = lean_unsigned_to_nat(12u);
return x_14;
}
case 13:
{
lean_object* x_15; 
x_15 = lean_unsigned_to_nat(13u);
return x_15;
}
case 14:
{
lean_object* x_16; 
x_16 = lean_unsigned_to_nat(14u);
return x_16;
}
case 15:
{
lean_object* x_17; 
x_17 = lean_unsigned_to_nat(15u);
return x_17;
}
case 16:
{
lean_object* x_18; 
x_18 = lean_unsigned_to_nat(16u);
return x_18;
}
case 17:
{
lean_object* x_19; 
x_19 = lean_unsigned_to_nat(17u);
return x_19;
}
case 18:
{
lean_object* x_20; 
x_20 = lean_unsigned_to_nat(18u);
return x_20;
}
case 19:
{
lean_object* x_21; 
x_21 = lean_unsigned_to_nat(19u);
return x_21;
}
case 20:
{
lean_object* x_22; 
x_22 = lean_unsigned_to_nat(20u);
return x_22;
}
case 21:
{
lean_object* x_23; 
x_23 = lean_unsigned_to_nat(21u);
return x_23;
}
case 22:
{
lean_object* x_24; 
x_24 = lean_unsigned_to_nat(22u);
return x_24;
}
case 23:
{
lean_object* x_25; 
x_25 = lean_unsigned_to_nat(23u);
return x_25;
}
case 24:
{
lean_object* x_26; 
x_26 = lean_unsigned_to_nat(24u);
return x_26;
}
case 25:
{
lean_object* x_27; 
x_27 = lean_unsigned_to_nat(25u);
return x_27;
}
case 26:
{
lean_object* x_28; 
x_28 = lean_unsigned_to_nat(26u);
return x_28;
}
case 27:
{
lean_object* x_29; 
x_29 = lean_unsigned_to_nat(27u);
return x_29;
}
case 28:
{
lean_object* x_30; 
x_30 = lean_unsigned_to_nat(28u);
return x_30;
}
case 29:
{
lean_object* x_31; 
x_31 = lean_unsigned_to_nat(29u);
return x_31;
}
case 30:
{
lean_object* x_32; 
x_32 = lean_unsigned_to_nat(30u);
return x_32;
}
case 31:
{
lean_object* x_33; 
x_33 = lean_unsigned_to_nat(31u);
return x_33;
}
case 32:
{
lean_object* x_34; 
x_34 = lean_unsigned_to_nat(32u);
return x_34;
}
case 33:
{
lean_object* x_35; 
x_35 = lean_unsigned_to_nat(33u);
return x_35;
}
case 34:
{
lean_object* x_36; 
x_36 = lean_unsigned_to_nat(34u);
return x_36;
}
case 35:
{
lean_object* x_37; 
x_37 = lean_unsigned_to_nat(35u);
return x_37;
}
case 36:
{
lean_object* x_38; 
x_38 = lean_unsigned_to_nat(36u);
return x_38;
}
case 37:
{
lean_object* x_39; 
x_39 = lean_unsigned_to_nat(37u);
return x_39;
}
case 38:
{
lean_object* x_40; 
x_40 = lean_unsigned_to_nat(38u);
return x_40;
}
case 39:
{
lean_object* x_41; 
x_41 = lean_unsigned_to_nat(39u);
return x_41;
}
case 40:
{
lean_object* x_42; 
x_42 = lean_unsigned_to_nat(40u);
return x_42;
}
case 41:
{
lean_object* x_43; 
x_43 = lean_unsigned_to_nat(41u);
return x_43;
}
case 42:
{
lean_object* x_44; 
x_44 = lean_unsigned_to_nat(42u);
return x_44;
}
case 43:
{
lean_object* x_45; 
x_45 = lean_unsigned_to_nat(43u);
return x_45;
}
case 44:
{
lean_object* x_46; 
x_46 = lean_unsigned_to_nat(44u);
return x_46;
}
case 45:
{
lean_object* x_47; 
x_47 = lean_unsigned_to_nat(45u);
return x_47;
}
case 46:
{
lean_object* x_48; 
x_48 = lean_unsigned_to_nat(46u);
return x_48;
}
case 47:
{
lean_object* x_49; 
x_49 = lean_unsigned_to_nat(47u);
return x_49;
}
case 48:
{
lean_object* x_50; 
x_50 = lean_unsigned_to_nat(48u);
return x_50;
}
case 49:
{
lean_object* x_51; 
x_51 = lean_unsigned_to_nat(49u);
return x_51;
}
case 50:
{
lean_object* x_52; 
x_52 = lean_unsigned_to_nat(50u);
return x_52;
}
case 51:
{
lean_object* x_53; 
x_53 = lean_unsigned_to_nat(51u);
return x_53;
}
case 52:
{
lean_object* x_54; 
x_54 = lean_unsigned_to_nat(52u);
return x_54;
}
case 53:
{
lean_object* x_55; 
x_55 = lean_unsigned_to_nat(53u);
return x_55;
}
case 54:
{
lean_object* x_56; 
x_56 = lean_unsigned_to_nat(54u);
return x_56;
}
default: 
{
lean_object* x_57; 
x_57 = lean_unsigned_to_nat(55u);
return x_57;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorIdx___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_Mnemonic_ctorIdx(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_toCtorIdx(uint8_t x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_ctorIdx(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_toCtorIdx___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_Mnemonic_toCtorIdx(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_ctorElim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim(lean_object* x_1, lean_object* x_2, uint8_t x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_inc(x_5);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ctorElim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
uint8_t x_6; lean_object* x_7; 
x_6 = lean_unbox(x_3);
x_7 = lp_dasmodel_Mnemonic_ctorElim(x_1, x_2, x_6, x_4, x_5);
lean_dec(x_5);
lean_dec(x_2);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_LDA_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDA_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_LDA_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_LDX_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_LDX_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_LDY_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LDY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_LDY_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_STA_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STA_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_STA_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_STX_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_STX_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_STY_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_STY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_STY_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_ADC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ADC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_ADC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_SBC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SBC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_SBC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_AND_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_AND_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_AND_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_ORA_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ORA_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_ORA_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_EOR_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_EOR_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_EOR_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_CMP_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CMP_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_CMP_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_CPX_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_CPX_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_CPY_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CPY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_CPY_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_INC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_INC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_DEC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_DEC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_INX_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_INX_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_DEX_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_DEX_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_INY_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_INY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_INY_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_DEY_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_DEY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_DEY_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_ASL_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ASL_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_ASL_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_LSR_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_LSR_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_LSR_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_ROL_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROL_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_ROL_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_ROR_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_ROR_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_ROR_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BCC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BCC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BCS_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BCS_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BCS_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BEQ_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BEQ_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BEQ_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BNE_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BNE_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BNE_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BMI_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BMI_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BMI_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BPL_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BPL_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BPL_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BVC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BVC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BVS_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BVS_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BVS_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_JMP_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JMP_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_JMP_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_JSR_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_JSR_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_JSR_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_RTS_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTS_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_RTS_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_RTI_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_RTI_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_RTI_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_PHA_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHA_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_PHA_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_PLA_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLA_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_PLA_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_PHP_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PHP_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_PHP_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_PLP_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_PLP_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_PLP_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_TAX_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_TAX_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_TAY_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TAY_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_TAY_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_TXA_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXA_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_TXA_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_TYA_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TYA_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_TYA_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_TXS_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TXS_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_TXS_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_TSX_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_TSX_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_TSX_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_CLC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_CLC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_SEC_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEC_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_SEC_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_CLI_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLI_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_CLI_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_SEI_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SEI_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_SEI_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_CLV_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLV_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_CLV_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_CLD_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_CLD_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_CLD_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_SED_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_SED_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_SED_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BIT_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BIT_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BIT_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_NOP_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_NOP_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_NOP_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim___redArg(lean_object* x_1) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Mnemonic_BRK_elim___redArg(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim(lean_object* x_1, uint8_t x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_inc(x_4);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Mnemonic_BRK_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint8_t x_5; lean_object* x_6; 
x_5 = lean_unbox(x_2);
x_6 = lp_dasmodel_Mnemonic_BRK_elim(x_1, x_5, x_3, x_4);
lean_dec(x_4);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprMnemonic_repr(uint8_t x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_10; lean_object* x_17; lean_object* x_24; lean_object* x_31; lean_object* x_38; lean_object* x_45; lean_object* x_52; lean_object* x_59; lean_object* x_66; lean_object* x_73; lean_object* x_80; lean_object* x_87; lean_object* x_94; lean_object* x_101; lean_object* x_108; lean_object* x_115; lean_object* x_122; lean_object* x_129; lean_object* x_136; lean_object* x_143; lean_object* x_150; lean_object* x_157; lean_object* x_164; lean_object* x_171; lean_object* x_178; lean_object* x_185; lean_object* x_192; lean_object* x_199; lean_object* x_206; lean_object* x_213; lean_object* x_220; lean_object* x_227; lean_object* x_234; lean_object* x_241; lean_object* x_248; lean_object* x_255; lean_object* x_262; lean_object* x_269; lean_object* x_276; lean_object* x_283; lean_object* x_290; lean_object* x_297; lean_object* x_304; lean_object* x_311; lean_object* x_318; lean_object* x_325; lean_object* x_332; lean_object* x_339; lean_object* x_346; lean_object* x_353; lean_object* x_360; lean_object* x_367; lean_object* x_374; lean_object* x_381; lean_object* x_388; 
switch (x_1) {
case 0:
{
lean_object* x_395; uint8_t x_396; 
x_395 = lean_unsigned_to_nat(1024u);
x_396 = lean_nat_dec_le(x_395, x_2);
if (x_396 == 0)
{
lean_object* x_397; 
x_397 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_3 = x_397;
goto block_9;
}
else
{
lean_object* x_398; 
x_398 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_3 = x_398;
goto block_9;
}
}
case 1:
{
lean_object* x_399; uint8_t x_400; 
x_399 = lean_unsigned_to_nat(1024u);
x_400 = lean_nat_dec_le(x_399, x_2);
if (x_400 == 0)
{
lean_object* x_401; 
x_401 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_10 = x_401;
goto block_16;
}
else
{
lean_object* x_402; 
x_402 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_10 = x_402;
goto block_16;
}
}
case 2:
{
lean_object* x_403; uint8_t x_404; 
x_403 = lean_unsigned_to_nat(1024u);
x_404 = lean_nat_dec_le(x_403, x_2);
if (x_404 == 0)
{
lean_object* x_405; 
x_405 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_17 = x_405;
goto block_23;
}
else
{
lean_object* x_406; 
x_406 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_17 = x_406;
goto block_23;
}
}
case 3:
{
lean_object* x_407; uint8_t x_408; 
x_407 = lean_unsigned_to_nat(1024u);
x_408 = lean_nat_dec_le(x_407, x_2);
if (x_408 == 0)
{
lean_object* x_409; 
x_409 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_24 = x_409;
goto block_30;
}
else
{
lean_object* x_410; 
x_410 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_24 = x_410;
goto block_30;
}
}
case 4:
{
lean_object* x_411; uint8_t x_412; 
x_411 = lean_unsigned_to_nat(1024u);
x_412 = lean_nat_dec_le(x_411, x_2);
if (x_412 == 0)
{
lean_object* x_413; 
x_413 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_31 = x_413;
goto block_37;
}
else
{
lean_object* x_414; 
x_414 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_31 = x_414;
goto block_37;
}
}
case 5:
{
lean_object* x_415; uint8_t x_416; 
x_415 = lean_unsigned_to_nat(1024u);
x_416 = lean_nat_dec_le(x_415, x_2);
if (x_416 == 0)
{
lean_object* x_417; 
x_417 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_38 = x_417;
goto block_44;
}
else
{
lean_object* x_418; 
x_418 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_38 = x_418;
goto block_44;
}
}
case 6:
{
lean_object* x_419; uint8_t x_420; 
x_419 = lean_unsigned_to_nat(1024u);
x_420 = lean_nat_dec_le(x_419, x_2);
if (x_420 == 0)
{
lean_object* x_421; 
x_421 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_45 = x_421;
goto block_51;
}
else
{
lean_object* x_422; 
x_422 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_45 = x_422;
goto block_51;
}
}
case 7:
{
lean_object* x_423; uint8_t x_424; 
x_423 = lean_unsigned_to_nat(1024u);
x_424 = lean_nat_dec_le(x_423, x_2);
if (x_424 == 0)
{
lean_object* x_425; 
x_425 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_52 = x_425;
goto block_58;
}
else
{
lean_object* x_426; 
x_426 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_52 = x_426;
goto block_58;
}
}
case 8:
{
lean_object* x_427; uint8_t x_428; 
x_427 = lean_unsigned_to_nat(1024u);
x_428 = lean_nat_dec_le(x_427, x_2);
if (x_428 == 0)
{
lean_object* x_429; 
x_429 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_59 = x_429;
goto block_65;
}
else
{
lean_object* x_430; 
x_430 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_59 = x_430;
goto block_65;
}
}
case 9:
{
lean_object* x_431; uint8_t x_432; 
x_431 = lean_unsigned_to_nat(1024u);
x_432 = lean_nat_dec_le(x_431, x_2);
if (x_432 == 0)
{
lean_object* x_433; 
x_433 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_66 = x_433;
goto block_72;
}
else
{
lean_object* x_434; 
x_434 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_66 = x_434;
goto block_72;
}
}
case 10:
{
lean_object* x_435; uint8_t x_436; 
x_435 = lean_unsigned_to_nat(1024u);
x_436 = lean_nat_dec_le(x_435, x_2);
if (x_436 == 0)
{
lean_object* x_437; 
x_437 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_73 = x_437;
goto block_79;
}
else
{
lean_object* x_438; 
x_438 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_73 = x_438;
goto block_79;
}
}
case 11:
{
lean_object* x_439; uint8_t x_440; 
x_439 = lean_unsigned_to_nat(1024u);
x_440 = lean_nat_dec_le(x_439, x_2);
if (x_440 == 0)
{
lean_object* x_441; 
x_441 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_80 = x_441;
goto block_86;
}
else
{
lean_object* x_442; 
x_442 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_80 = x_442;
goto block_86;
}
}
case 12:
{
lean_object* x_443; uint8_t x_444; 
x_443 = lean_unsigned_to_nat(1024u);
x_444 = lean_nat_dec_le(x_443, x_2);
if (x_444 == 0)
{
lean_object* x_445; 
x_445 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_87 = x_445;
goto block_93;
}
else
{
lean_object* x_446; 
x_446 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_87 = x_446;
goto block_93;
}
}
case 13:
{
lean_object* x_447; uint8_t x_448; 
x_447 = lean_unsigned_to_nat(1024u);
x_448 = lean_nat_dec_le(x_447, x_2);
if (x_448 == 0)
{
lean_object* x_449; 
x_449 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_94 = x_449;
goto block_100;
}
else
{
lean_object* x_450; 
x_450 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_94 = x_450;
goto block_100;
}
}
case 14:
{
lean_object* x_451; uint8_t x_452; 
x_451 = lean_unsigned_to_nat(1024u);
x_452 = lean_nat_dec_le(x_451, x_2);
if (x_452 == 0)
{
lean_object* x_453; 
x_453 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_101 = x_453;
goto block_107;
}
else
{
lean_object* x_454; 
x_454 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_101 = x_454;
goto block_107;
}
}
case 15:
{
lean_object* x_455; uint8_t x_456; 
x_455 = lean_unsigned_to_nat(1024u);
x_456 = lean_nat_dec_le(x_455, x_2);
if (x_456 == 0)
{
lean_object* x_457; 
x_457 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_108 = x_457;
goto block_114;
}
else
{
lean_object* x_458; 
x_458 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_108 = x_458;
goto block_114;
}
}
case 16:
{
lean_object* x_459; uint8_t x_460; 
x_459 = lean_unsigned_to_nat(1024u);
x_460 = lean_nat_dec_le(x_459, x_2);
if (x_460 == 0)
{
lean_object* x_461; 
x_461 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_115 = x_461;
goto block_121;
}
else
{
lean_object* x_462; 
x_462 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_115 = x_462;
goto block_121;
}
}
case 17:
{
lean_object* x_463; uint8_t x_464; 
x_463 = lean_unsigned_to_nat(1024u);
x_464 = lean_nat_dec_le(x_463, x_2);
if (x_464 == 0)
{
lean_object* x_465; 
x_465 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_122 = x_465;
goto block_128;
}
else
{
lean_object* x_466; 
x_466 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_122 = x_466;
goto block_128;
}
}
case 18:
{
lean_object* x_467; uint8_t x_468; 
x_467 = lean_unsigned_to_nat(1024u);
x_468 = lean_nat_dec_le(x_467, x_2);
if (x_468 == 0)
{
lean_object* x_469; 
x_469 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_129 = x_469;
goto block_135;
}
else
{
lean_object* x_470; 
x_470 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_129 = x_470;
goto block_135;
}
}
case 19:
{
lean_object* x_471; uint8_t x_472; 
x_471 = lean_unsigned_to_nat(1024u);
x_472 = lean_nat_dec_le(x_471, x_2);
if (x_472 == 0)
{
lean_object* x_473; 
x_473 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_136 = x_473;
goto block_142;
}
else
{
lean_object* x_474; 
x_474 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_136 = x_474;
goto block_142;
}
}
case 20:
{
lean_object* x_475; uint8_t x_476; 
x_475 = lean_unsigned_to_nat(1024u);
x_476 = lean_nat_dec_le(x_475, x_2);
if (x_476 == 0)
{
lean_object* x_477; 
x_477 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_143 = x_477;
goto block_149;
}
else
{
lean_object* x_478; 
x_478 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_143 = x_478;
goto block_149;
}
}
case 21:
{
lean_object* x_479; uint8_t x_480; 
x_479 = lean_unsigned_to_nat(1024u);
x_480 = lean_nat_dec_le(x_479, x_2);
if (x_480 == 0)
{
lean_object* x_481; 
x_481 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_150 = x_481;
goto block_156;
}
else
{
lean_object* x_482; 
x_482 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_150 = x_482;
goto block_156;
}
}
case 22:
{
lean_object* x_483; uint8_t x_484; 
x_483 = lean_unsigned_to_nat(1024u);
x_484 = lean_nat_dec_le(x_483, x_2);
if (x_484 == 0)
{
lean_object* x_485; 
x_485 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_157 = x_485;
goto block_163;
}
else
{
lean_object* x_486; 
x_486 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_157 = x_486;
goto block_163;
}
}
case 23:
{
lean_object* x_487; uint8_t x_488; 
x_487 = lean_unsigned_to_nat(1024u);
x_488 = lean_nat_dec_le(x_487, x_2);
if (x_488 == 0)
{
lean_object* x_489; 
x_489 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_164 = x_489;
goto block_170;
}
else
{
lean_object* x_490; 
x_490 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_164 = x_490;
goto block_170;
}
}
case 24:
{
lean_object* x_491; uint8_t x_492; 
x_491 = lean_unsigned_to_nat(1024u);
x_492 = lean_nat_dec_le(x_491, x_2);
if (x_492 == 0)
{
lean_object* x_493; 
x_493 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_171 = x_493;
goto block_177;
}
else
{
lean_object* x_494; 
x_494 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_171 = x_494;
goto block_177;
}
}
case 25:
{
lean_object* x_495; uint8_t x_496; 
x_495 = lean_unsigned_to_nat(1024u);
x_496 = lean_nat_dec_le(x_495, x_2);
if (x_496 == 0)
{
lean_object* x_497; 
x_497 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_178 = x_497;
goto block_184;
}
else
{
lean_object* x_498; 
x_498 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_178 = x_498;
goto block_184;
}
}
case 26:
{
lean_object* x_499; uint8_t x_500; 
x_499 = lean_unsigned_to_nat(1024u);
x_500 = lean_nat_dec_le(x_499, x_2);
if (x_500 == 0)
{
lean_object* x_501; 
x_501 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_185 = x_501;
goto block_191;
}
else
{
lean_object* x_502; 
x_502 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_185 = x_502;
goto block_191;
}
}
case 27:
{
lean_object* x_503; uint8_t x_504; 
x_503 = lean_unsigned_to_nat(1024u);
x_504 = lean_nat_dec_le(x_503, x_2);
if (x_504 == 0)
{
lean_object* x_505; 
x_505 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_192 = x_505;
goto block_198;
}
else
{
lean_object* x_506; 
x_506 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_192 = x_506;
goto block_198;
}
}
case 28:
{
lean_object* x_507; uint8_t x_508; 
x_507 = lean_unsigned_to_nat(1024u);
x_508 = lean_nat_dec_le(x_507, x_2);
if (x_508 == 0)
{
lean_object* x_509; 
x_509 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_199 = x_509;
goto block_205;
}
else
{
lean_object* x_510; 
x_510 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_199 = x_510;
goto block_205;
}
}
case 29:
{
lean_object* x_511; uint8_t x_512; 
x_511 = lean_unsigned_to_nat(1024u);
x_512 = lean_nat_dec_le(x_511, x_2);
if (x_512 == 0)
{
lean_object* x_513; 
x_513 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_206 = x_513;
goto block_212;
}
else
{
lean_object* x_514; 
x_514 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_206 = x_514;
goto block_212;
}
}
case 30:
{
lean_object* x_515; uint8_t x_516; 
x_515 = lean_unsigned_to_nat(1024u);
x_516 = lean_nat_dec_le(x_515, x_2);
if (x_516 == 0)
{
lean_object* x_517; 
x_517 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_213 = x_517;
goto block_219;
}
else
{
lean_object* x_518; 
x_518 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_213 = x_518;
goto block_219;
}
}
case 31:
{
lean_object* x_519; uint8_t x_520; 
x_519 = lean_unsigned_to_nat(1024u);
x_520 = lean_nat_dec_le(x_519, x_2);
if (x_520 == 0)
{
lean_object* x_521; 
x_521 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_220 = x_521;
goto block_226;
}
else
{
lean_object* x_522; 
x_522 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_220 = x_522;
goto block_226;
}
}
case 32:
{
lean_object* x_523; uint8_t x_524; 
x_523 = lean_unsigned_to_nat(1024u);
x_524 = lean_nat_dec_le(x_523, x_2);
if (x_524 == 0)
{
lean_object* x_525; 
x_525 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_227 = x_525;
goto block_233;
}
else
{
lean_object* x_526; 
x_526 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_227 = x_526;
goto block_233;
}
}
case 33:
{
lean_object* x_527; uint8_t x_528; 
x_527 = lean_unsigned_to_nat(1024u);
x_528 = lean_nat_dec_le(x_527, x_2);
if (x_528 == 0)
{
lean_object* x_529; 
x_529 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_234 = x_529;
goto block_240;
}
else
{
lean_object* x_530; 
x_530 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_234 = x_530;
goto block_240;
}
}
case 34:
{
lean_object* x_531; uint8_t x_532; 
x_531 = lean_unsigned_to_nat(1024u);
x_532 = lean_nat_dec_le(x_531, x_2);
if (x_532 == 0)
{
lean_object* x_533; 
x_533 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_241 = x_533;
goto block_247;
}
else
{
lean_object* x_534; 
x_534 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_241 = x_534;
goto block_247;
}
}
case 35:
{
lean_object* x_535; uint8_t x_536; 
x_535 = lean_unsigned_to_nat(1024u);
x_536 = lean_nat_dec_le(x_535, x_2);
if (x_536 == 0)
{
lean_object* x_537; 
x_537 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_248 = x_537;
goto block_254;
}
else
{
lean_object* x_538; 
x_538 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_248 = x_538;
goto block_254;
}
}
case 36:
{
lean_object* x_539; uint8_t x_540; 
x_539 = lean_unsigned_to_nat(1024u);
x_540 = lean_nat_dec_le(x_539, x_2);
if (x_540 == 0)
{
lean_object* x_541; 
x_541 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_255 = x_541;
goto block_261;
}
else
{
lean_object* x_542; 
x_542 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_255 = x_542;
goto block_261;
}
}
case 37:
{
lean_object* x_543; uint8_t x_544; 
x_543 = lean_unsigned_to_nat(1024u);
x_544 = lean_nat_dec_le(x_543, x_2);
if (x_544 == 0)
{
lean_object* x_545; 
x_545 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_262 = x_545;
goto block_268;
}
else
{
lean_object* x_546; 
x_546 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_262 = x_546;
goto block_268;
}
}
case 38:
{
lean_object* x_547; uint8_t x_548; 
x_547 = lean_unsigned_to_nat(1024u);
x_548 = lean_nat_dec_le(x_547, x_2);
if (x_548 == 0)
{
lean_object* x_549; 
x_549 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_269 = x_549;
goto block_275;
}
else
{
lean_object* x_550; 
x_550 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_269 = x_550;
goto block_275;
}
}
case 39:
{
lean_object* x_551; uint8_t x_552; 
x_551 = lean_unsigned_to_nat(1024u);
x_552 = lean_nat_dec_le(x_551, x_2);
if (x_552 == 0)
{
lean_object* x_553; 
x_553 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_276 = x_553;
goto block_282;
}
else
{
lean_object* x_554; 
x_554 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_276 = x_554;
goto block_282;
}
}
case 40:
{
lean_object* x_555; uint8_t x_556; 
x_555 = lean_unsigned_to_nat(1024u);
x_556 = lean_nat_dec_le(x_555, x_2);
if (x_556 == 0)
{
lean_object* x_557; 
x_557 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_283 = x_557;
goto block_289;
}
else
{
lean_object* x_558; 
x_558 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_283 = x_558;
goto block_289;
}
}
case 41:
{
lean_object* x_559; uint8_t x_560; 
x_559 = lean_unsigned_to_nat(1024u);
x_560 = lean_nat_dec_le(x_559, x_2);
if (x_560 == 0)
{
lean_object* x_561; 
x_561 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_290 = x_561;
goto block_296;
}
else
{
lean_object* x_562; 
x_562 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_290 = x_562;
goto block_296;
}
}
case 42:
{
lean_object* x_563; uint8_t x_564; 
x_563 = lean_unsigned_to_nat(1024u);
x_564 = lean_nat_dec_le(x_563, x_2);
if (x_564 == 0)
{
lean_object* x_565; 
x_565 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_297 = x_565;
goto block_303;
}
else
{
lean_object* x_566; 
x_566 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_297 = x_566;
goto block_303;
}
}
case 43:
{
lean_object* x_567; uint8_t x_568; 
x_567 = lean_unsigned_to_nat(1024u);
x_568 = lean_nat_dec_le(x_567, x_2);
if (x_568 == 0)
{
lean_object* x_569; 
x_569 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_304 = x_569;
goto block_310;
}
else
{
lean_object* x_570; 
x_570 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_304 = x_570;
goto block_310;
}
}
case 44:
{
lean_object* x_571; uint8_t x_572; 
x_571 = lean_unsigned_to_nat(1024u);
x_572 = lean_nat_dec_le(x_571, x_2);
if (x_572 == 0)
{
lean_object* x_573; 
x_573 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_311 = x_573;
goto block_317;
}
else
{
lean_object* x_574; 
x_574 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_311 = x_574;
goto block_317;
}
}
case 45:
{
lean_object* x_575; uint8_t x_576; 
x_575 = lean_unsigned_to_nat(1024u);
x_576 = lean_nat_dec_le(x_575, x_2);
if (x_576 == 0)
{
lean_object* x_577; 
x_577 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_318 = x_577;
goto block_324;
}
else
{
lean_object* x_578; 
x_578 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_318 = x_578;
goto block_324;
}
}
case 46:
{
lean_object* x_579; uint8_t x_580; 
x_579 = lean_unsigned_to_nat(1024u);
x_580 = lean_nat_dec_le(x_579, x_2);
if (x_580 == 0)
{
lean_object* x_581; 
x_581 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_325 = x_581;
goto block_331;
}
else
{
lean_object* x_582; 
x_582 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_325 = x_582;
goto block_331;
}
}
case 47:
{
lean_object* x_583; uint8_t x_584; 
x_583 = lean_unsigned_to_nat(1024u);
x_584 = lean_nat_dec_le(x_583, x_2);
if (x_584 == 0)
{
lean_object* x_585; 
x_585 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_332 = x_585;
goto block_338;
}
else
{
lean_object* x_586; 
x_586 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_332 = x_586;
goto block_338;
}
}
case 48:
{
lean_object* x_587; uint8_t x_588; 
x_587 = lean_unsigned_to_nat(1024u);
x_588 = lean_nat_dec_le(x_587, x_2);
if (x_588 == 0)
{
lean_object* x_589; 
x_589 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_339 = x_589;
goto block_345;
}
else
{
lean_object* x_590; 
x_590 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_339 = x_590;
goto block_345;
}
}
case 49:
{
lean_object* x_591; uint8_t x_592; 
x_591 = lean_unsigned_to_nat(1024u);
x_592 = lean_nat_dec_le(x_591, x_2);
if (x_592 == 0)
{
lean_object* x_593; 
x_593 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_346 = x_593;
goto block_352;
}
else
{
lean_object* x_594; 
x_594 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_346 = x_594;
goto block_352;
}
}
case 50:
{
lean_object* x_595; uint8_t x_596; 
x_595 = lean_unsigned_to_nat(1024u);
x_596 = lean_nat_dec_le(x_595, x_2);
if (x_596 == 0)
{
lean_object* x_597; 
x_597 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_353 = x_597;
goto block_359;
}
else
{
lean_object* x_598; 
x_598 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_353 = x_598;
goto block_359;
}
}
case 51:
{
lean_object* x_599; uint8_t x_600; 
x_599 = lean_unsigned_to_nat(1024u);
x_600 = lean_nat_dec_le(x_599, x_2);
if (x_600 == 0)
{
lean_object* x_601; 
x_601 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_360 = x_601;
goto block_366;
}
else
{
lean_object* x_602; 
x_602 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_360 = x_602;
goto block_366;
}
}
case 52:
{
lean_object* x_603; uint8_t x_604; 
x_603 = lean_unsigned_to_nat(1024u);
x_604 = lean_nat_dec_le(x_603, x_2);
if (x_604 == 0)
{
lean_object* x_605; 
x_605 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_367 = x_605;
goto block_373;
}
else
{
lean_object* x_606; 
x_606 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_367 = x_606;
goto block_373;
}
}
case 53:
{
lean_object* x_607; uint8_t x_608; 
x_607 = lean_unsigned_to_nat(1024u);
x_608 = lean_nat_dec_le(x_607, x_2);
if (x_608 == 0)
{
lean_object* x_609; 
x_609 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_374 = x_609;
goto block_380;
}
else
{
lean_object* x_610; 
x_610 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_374 = x_610;
goto block_380;
}
}
case 54:
{
lean_object* x_611; uint8_t x_612; 
x_611 = lean_unsigned_to_nat(1024u);
x_612 = lean_nat_dec_le(x_611, x_2);
if (x_612 == 0)
{
lean_object* x_613; 
x_613 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_381 = x_613;
goto block_387;
}
else
{
lean_object* x_614; 
x_614 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_381 = x_614;
goto block_387;
}
}
default: 
{
lean_object* x_615; uint8_t x_616; 
x_615 = lean_unsigned_to_nat(1024u);
x_616 = lean_nat_dec_le(x_615, x_2);
if (x_616 == 0)
{
lean_object* x_617; 
x_617 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__7, &lp_dasmodel_instReprAddrMode_repr___closed__7_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__7);
x_388 = x_617;
goto block_394;
}
else
{
lean_object* x_618; 
x_618 = lean_obj_once(&lp_dasmodel_instReprAddrMode_repr___closed__8, &lp_dasmodel_instReprAddrMode_repr___closed__8_once, _init_lp_dasmodel_instReprAddrMode_repr___closed__8);
x_388 = x_618;
goto block_394;
}
}
}
block_9:
{
lean_object* x_4; lean_object* x_5; uint8_t x_6; lean_object* x_7; lean_object* x_8; 
x_4 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__1));
x_5 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_5, 0, x_3);
lean_ctor_set(x_5, 1, x_4);
x_6 = 0;
x_7 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_7, 0, x_5);
lean_ctor_set_uint8(x_7, sizeof(void*)*1, x_6);
x_8 = l_Repr_addAppParen(x_7, x_2);
return x_8;
}
block_16:
{
lean_object* x_11; lean_object* x_12; uint8_t x_13; lean_object* x_14; lean_object* x_15; 
x_11 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__3));
x_12 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_12, 0, x_10);
lean_ctor_set(x_12, 1, x_11);
x_13 = 0;
x_14 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_14, 0, x_12);
lean_ctor_set_uint8(x_14, sizeof(void*)*1, x_13);
x_15 = l_Repr_addAppParen(x_14, x_2);
return x_15;
}
block_23:
{
lean_object* x_18; lean_object* x_19; uint8_t x_20; lean_object* x_21; lean_object* x_22; 
x_18 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__5));
x_19 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_19, 0, x_17);
lean_ctor_set(x_19, 1, x_18);
x_20 = 0;
x_21 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_21, 0, x_19);
lean_ctor_set_uint8(x_21, sizeof(void*)*1, x_20);
x_22 = l_Repr_addAppParen(x_21, x_2);
return x_22;
}
block_30:
{
lean_object* x_25; lean_object* x_26; uint8_t x_27; lean_object* x_28; lean_object* x_29; 
x_25 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__7));
x_26 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_26, 0, x_24);
lean_ctor_set(x_26, 1, x_25);
x_27 = 0;
x_28 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_28, 0, x_26);
lean_ctor_set_uint8(x_28, sizeof(void*)*1, x_27);
x_29 = l_Repr_addAppParen(x_28, x_2);
return x_29;
}
block_37:
{
lean_object* x_32; lean_object* x_33; uint8_t x_34; lean_object* x_35; lean_object* x_36; 
x_32 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__9));
x_33 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_33, 0, x_31);
lean_ctor_set(x_33, 1, x_32);
x_34 = 0;
x_35 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_35, 0, x_33);
lean_ctor_set_uint8(x_35, sizeof(void*)*1, x_34);
x_36 = l_Repr_addAppParen(x_35, x_2);
return x_36;
}
block_44:
{
lean_object* x_39; lean_object* x_40; uint8_t x_41; lean_object* x_42; lean_object* x_43; 
x_39 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__11));
x_40 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_40, 0, x_38);
lean_ctor_set(x_40, 1, x_39);
x_41 = 0;
x_42 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_42, 0, x_40);
lean_ctor_set_uint8(x_42, sizeof(void*)*1, x_41);
x_43 = l_Repr_addAppParen(x_42, x_2);
return x_43;
}
block_51:
{
lean_object* x_46; lean_object* x_47; uint8_t x_48; lean_object* x_49; lean_object* x_50; 
x_46 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__13));
x_47 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_47, 0, x_45);
lean_ctor_set(x_47, 1, x_46);
x_48 = 0;
x_49 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_49, 0, x_47);
lean_ctor_set_uint8(x_49, sizeof(void*)*1, x_48);
x_50 = l_Repr_addAppParen(x_49, x_2);
return x_50;
}
block_58:
{
lean_object* x_53; lean_object* x_54; uint8_t x_55; lean_object* x_56; lean_object* x_57; 
x_53 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__15));
x_54 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_54, 0, x_52);
lean_ctor_set(x_54, 1, x_53);
x_55 = 0;
x_56 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_56, 0, x_54);
lean_ctor_set_uint8(x_56, sizeof(void*)*1, x_55);
x_57 = l_Repr_addAppParen(x_56, x_2);
return x_57;
}
block_65:
{
lean_object* x_60; lean_object* x_61; uint8_t x_62; lean_object* x_63; lean_object* x_64; 
x_60 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__17));
x_61 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_61, 0, x_59);
lean_ctor_set(x_61, 1, x_60);
x_62 = 0;
x_63 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_63, 0, x_61);
lean_ctor_set_uint8(x_63, sizeof(void*)*1, x_62);
x_64 = l_Repr_addAppParen(x_63, x_2);
return x_64;
}
block_72:
{
lean_object* x_67; lean_object* x_68; uint8_t x_69; lean_object* x_70; lean_object* x_71; 
x_67 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__19));
x_68 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_68, 0, x_66);
lean_ctor_set(x_68, 1, x_67);
x_69 = 0;
x_70 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_70, 0, x_68);
lean_ctor_set_uint8(x_70, sizeof(void*)*1, x_69);
x_71 = l_Repr_addAppParen(x_70, x_2);
return x_71;
}
block_79:
{
lean_object* x_74; lean_object* x_75; uint8_t x_76; lean_object* x_77; lean_object* x_78; 
x_74 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__21));
x_75 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_75, 0, x_73);
lean_ctor_set(x_75, 1, x_74);
x_76 = 0;
x_77 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_77, 0, x_75);
lean_ctor_set_uint8(x_77, sizeof(void*)*1, x_76);
x_78 = l_Repr_addAppParen(x_77, x_2);
return x_78;
}
block_86:
{
lean_object* x_81; lean_object* x_82; uint8_t x_83; lean_object* x_84; lean_object* x_85; 
x_81 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__23));
x_82 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_82, 0, x_80);
lean_ctor_set(x_82, 1, x_81);
x_83 = 0;
x_84 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_84, 0, x_82);
lean_ctor_set_uint8(x_84, sizeof(void*)*1, x_83);
x_85 = l_Repr_addAppParen(x_84, x_2);
return x_85;
}
block_93:
{
lean_object* x_88; lean_object* x_89; uint8_t x_90; lean_object* x_91; lean_object* x_92; 
x_88 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__25));
x_89 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_89, 0, x_87);
lean_ctor_set(x_89, 1, x_88);
x_90 = 0;
x_91 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_91, 0, x_89);
lean_ctor_set_uint8(x_91, sizeof(void*)*1, x_90);
x_92 = l_Repr_addAppParen(x_91, x_2);
return x_92;
}
block_100:
{
lean_object* x_95; lean_object* x_96; uint8_t x_97; lean_object* x_98; lean_object* x_99; 
x_95 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__27));
x_96 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_96, 0, x_94);
lean_ctor_set(x_96, 1, x_95);
x_97 = 0;
x_98 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_98, 0, x_96);
lean_ctor_set_uint8(x_98, sizeof(void*)*1, x_97);
x_99 = l_Repr_addAppParen(x_98, x_2);
return x_99;
}
block_107:
{
lean_object* x_102; lean_object* x_103; uint8_t x_104; lean_object* x_105; lean_object* x_106; 
x_102 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__29));
x_103 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_103, 0, x_101);
lean_ctor_set(x_103, 1, x_102);
x_104 = 0;
x_105 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_105, 0, x_103);
lean_ctor_set_uint8(x_105, sizeof(void*)*1, x_104);
x_106 = l_Repr_addAppParen(x_105, x_2);
return x_106;
}
block_114:
{
lean_object* x_109; lean_object* x_110; uint8_t x_111; lean_object* x_112; lean_object* x_113; 
x_109 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__31));
x_110 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_110, 0, x_108);
lean_ctor_set(x_110, 1, x_109);
x_111 = 0;
x_112 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_112, 0, x_110);
lean_ctor_set_uint8(x_112, sizeof(void*)*1, x_111);
x_113 = l_Repr_addAppParen(x_112, x_2);
return x_113;
}
block_121:
{
lean_object* x_116; lean_object* x_117; uint8_t x_118; lean_object* x_119; lean_object* x_120; 
x_116 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__33));
x_117 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_117, 0, x_115);
lean_ctor_set(x_117, 1, x_116);
x_118 = 0;
x_119 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_119, 0, x_117);
lean_ctor_set_uint8(x_119, sizeof(void*)*1, x_118);
x_120 = l_Repr_addAppParen(x_119, x_2);
return x_120;
}
block_128:
{
lean_object* x_123; lean_object* x_124; uint8_t x_125; lean_object* x_126; lean_object* x_127; 
x_123 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__35));
x_124 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_124, 0, x_122);
lean_ctor_set(x_124, 1, x_123);
x_125 = 0;
x_126 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_126, 0, x_124);
lean_ctor_set_uint8(x_126, sizeof(void*)*1, x_125);
x_127 = l_Repr_addAppParen(x_126, x_2);
return x_127;
}
block_135:
{
lean_object* x_130; lean_object* x_131; uint8_t x_132; lean_object* x_133; lean_object* x_134; 
x_130 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__37));
x_131 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_131, 0, x_129);
lean_ctor_set(x_131, 1, x_130);
x_132 = 0;
x_133 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_133, 0, x_131);
lean_ctor_set_uint8(x_133, sizeof(void*)*1, x_132);
x_134 = l_Repr_addAppParen(x_133, x_2);
return x_134;
}
block_142:
{
lean_object* x_137; lean_object* x_138; uint8_t x_139; lean_object* x_140; lean_object* x_141; 
x_137 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__39));
x_138 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_138, 0, x_136);
lean_ctor_set(x_138, 1, x_137);
x_139 = 0;
x_140 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_140, 0, x_138);
lean_ctor_set_uint8(x_140, sizeof(void*)*1, x_139);
x_141 = l_Repr_addAppParen(x_140, x_2);
return x_141;
}
block_149:
{
lean_object* x_144; lean_object* x_145; uint8_t x_146; lean_object* x_147; lean_object* x_148; 
x_144 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__41));
x_145 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_145, 0, x_143);
lean_ctor_set(x_145, 1, x_144);
x_146 = 0;
x_147 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_147, 0, x_145);
lean_ctor_set_uint8(x_147, sizeof(void*)*1, x_146);
x_148 = l_Repr_addAppParen(x_147, x_2);
return x_148;
}
block_156:
{
lean_object* x_151; lean_object* x_152; uint8_t x_153; lean_object* x_154; lean_object* x_155; 
x_151 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__43));
x_152 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_152, 0, x_150);
lean_ctor_set(x_152, 1, x_151);
x_153 = 0;
x_154 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_154, 0, x_152);
lean_ctor_set_uint8(x_154, sizeof(void*)*1, x_153);
x_155 = l_Repr_addAppParen(x_154, x_2);
return x_155;
}
block_163:
{
lean_object* x_158; lean_object* x_159; uint8_t x_160; lean_object* x_161; lean_object* x_162; 
x_158 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__45));
x_159 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_159, 0, x_157);
lean_ctor_set(x_159, 1, x_158);
x_160 = 0;
x_161 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_161, 0, x_159);
lean_ctor_set_uint8(x_161, sizeof(void*)*1, x_160);
x_162 = l_Repr_addAppParen(x_161, x_2);
return x_162;
}
block_170:
{
lean_object* x_165; lean_object* x_166; uint8_t x_167; lean_object* x_168; lean_object* x_169; 
x_165 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__47));
x_166 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_166, 0, x_164);
lean_ctor_set(x_166, 1, x_165);
x_167 = 0;
x_168 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_168, 0, x_166);
lean_ctor_set_uint8(x_168, sizeof(void*)*1, x_167);
x_169 = l_Repr_addAppParen(x_168, x_2);
return x_169;
}
block_177:
{
lean_object* x_172; lean_object* x_173; uint8_t x_174; lean_object* x_175; lean_object* x_176; 
x_172 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__49));
x_173 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_173, 0, x_171);
lean_ctor_set(x_173, 1, x_172);
x_174 = 0;
x_175 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_175, 0, x_173);
lean_ctor_set_uint8(x_175, sizeof(void*)*1, x_174);
x_176 = l_Repr_addAppParen(x_175, x_2);
return x_176;
}
block_184:
{
lean_object* x_179; lean_object* x_180; uint8_t x_181; lean_object* x_182; lean_object* x_183; 
x_179 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__51));
x_180 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_180, 0, x_178);
lean_ctor_set(x_180, 1, x_179);
x_181 = 0;
x_182 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_182, 0, x_180);
lean_ctor_set_uint8(x_182, sizeof(void*)*1, x_181);
x_183 = l_Repr_addAppParen(x_182, x_2);
return x_183;
}
block_191:
{
lean_object* x_186; lean_object* x_187; uint8_t x_188; lean_object* x_189; lean_object* x_190; 
x_186 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__53));
x_187 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_187, 0, x_185);
lean_ctor_set(x_187, 1, x_186);
x_188 = 0;
x_189 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_189, 0, x_187);
lean_ctor_set_uint8(x_189, sizeof(void*)*1, x_188);
x_190 = l_Repr_addAppParen(x_189, x_2);
return x_190;
}
block_198:
{
lean_object* x_193; lean_object* x_194; uint8_t x_195; lean_object* x_196; lean_object* x_197; 
x_193 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__55));
x_194 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_194, 0, x_192);
lean_ctor_set(x_194, 1, x_193);
x_195 = 0;
x_196 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_196, 0, x_194);
lean_ctor_set_uint8(x_196, sizeof(void*)*1, x_195);
x_197 = l_Repr_addAppParen(x_196, x_2);
return x_197;
}
block_205:
{
lean_object* x_200; lean_object* x_201; uint8_t x_202; lean_object* x_203; lean_object* x_204; 
x_200 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__57));
x_201 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_201, 0, x_199);
lean_ctor_set(x_201, 1, x_200);
x_202 = 0;
x_203 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_203, 0, x_201);
lean_ctor_set_uint8(x_203, sizeof(void*)*1, x_202);
x_204 = l_Repr_addAppParen(x_203, x_2);
return x_204;
}
block_212:
{
lean_object* x_207; lean_object* x_208; uint8_t x_209; lean_object* x_210; lean_object* x_211; 
x_207 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__59));
x_208 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_208, 0, x_206);
lean_ctor_set(x_208, 1, x_207);
x_209 = 0;
x_210 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_210, 0, x_208);
lean_ctor_set_uint8(x_210, sizeof(void*)*1, x_209);
x_211 = l_Repr_addAppParen(x_210, x_2);
return x_211;
}
block_219:
{
lean_object* x_214; lean_object* x_215; uint8_t x_216; lean_object* x_217; lean_object* x_218; 
x_214 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__61));
x_215 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_215, 0, x_213);
lean_ctor_set(x_215, 1, x_214);
x_216 = 0;
x_217 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_217, 0, x_215);
lean_ctor_set_uint8(x_217, sizeof(void*)*1, x_216);
x_218 = l_Repr_addAppParen(x_217, x_2);
return x_218;
}
block_226:
{
lean_object* x_221; lean_object* x_222; uint8_t x_223; lean_object* x_224; lean_object* x_225; 
x_221 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__63));
x_222 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_222, 0, x_220);
lean_ctor_set(x_222, 1, x_221);
x_223 = 0;
x_224 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_224, 0, x_222);
lean_ctor_set_uint8(x_224, sizeof(void*)*1, x_223);
x_225 = l_Repr_addAppParen(x_224, x_2);
return x_225;
}
block_233:
{
lean_object* x_228; lean_object* x_229; uint8_t x_230; lean_object* x_231; lean_object* x_232; 
x_228 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__65));
x_229 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_229, 0, x_227);
lean_ctor_set(x_229, 1, x_228);
x_230 = 0;
x_231 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_231, 0, x_229);
lean_ctor_set_uint8(x_231, sizeof(void*)*1, x_230);
x_232 = l_Repr_addAppParen(x_231, x_2);
return x_232;
}
block_240:
{
lean_object* x_235; lean_object* x_236; uint8_t x_237; lean_object* x_238; lean_object* x_239; 
x_235 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__67));
x_236 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_236, 0, x_234);
lean_ctor_set(x_236, 1, x_235);
x_237 = 0;
x_238 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_238, 0, x_236);
lean_ctor_set_uint8(x_238, sizeof(void*)*1, x_237);
x_239 = l_Repr_addAppParen(x_238, x_2);
return x_239;
}
block_247:
{
lean_object* x_242; lean_object* x_243; uint8_t x_244; lean_object* x_245; lean_object* x_246; 
x_242 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__69));
x_243 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_243, 0, x_241);
lean_ctor_set(x_243, 1, x_242);
x_244 = 0;
x_245 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_245, 0, x_243);
lean_ctor_set_uint8(x_245, sizeof(void*)*1, x_244);
x_246 = l_Repr_addAppParen(x_245, x_2);
return x_246;
}
block_254:
{
lean_object* x_249; lean_object* x_250; uint8_t x_251; lean_object* x_252; lean_object* x_253; 
x_249 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__71));
x_250 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_250, 0, x_248);
lean_ctor_set(x_250, 1, x_249);
x_251 = 0;
x_252 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_252, 0, x_250);
lean_ctor_set_uint8(x_252, sizeof(void*)*1, x_251);
x_253 = l_Repr_addAppParen(x_252, x_2);
return x_253;
}
block_261:
{
lean_object* x_256; lean_object* x_257; uint8_t x_258; lean_object* x_259; lean_object* x_260; 
x_256 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__73));
x_257 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_257, 0, x_255);
lean_ctor_set(x_257, 1, x_256);
x_258 = 0;
x_259 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_259, 0, x_257);
lean_ctor_set_uint8(x_259, sizeof(void*)*1, x_258);
x_260 = l_Repr_addAppParen(x_259, x_2);
return x_260;
}
block_268:
{
lean_object* x_263; lean_object* x_264; uint8_t x_265; lean_object* x_266; lean_object* x_267; 
x_263 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__75));
x_264 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_264, 0, x_262);
lean_ctor_set(x_264, 1, x_263);
x_265 = 0;
x_266 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_266, 0, x_264);
lean_ctor_set_uint8(x_266, sizeof(void*)*1, x_265);
x_267 = l_Repr_addAppParen(x_266, x_2);
return x_267;
}
block_275:
{
lean_object* x_270; lean_object* x_271; uint8_t x_272; lean_object* x_273; lean_object* x_274; 
x_270 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__77));
x_271 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_271, 0, x_269);
lean_ctor_set(x_271, 1, x_270);
x_272 = 0;
x_273 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_273, 0, x_271);
lean_ctor_set_uint8(x_273, sizeof(void*)*1, x_272);
x_274 = l_Repr_addAppParen(x_273, x_2);
return x_274;
}
block_282:
{
lean_object* x_277; lean_object* x_278; uint8_t x_279; lean_object* x_280; lean_object* x_281; 
x_277 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__79));
x_278 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_278, 0, x_276);
lean_ctor_set(x_278, 1, x_277);
x_279 = 0;
x_280 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_280, 0, x_278);
lean_ctor_set_uint8(x_280, sizeof(void*)*1, x_279);
x_281 = l_Repr_addAppParen(x_280, x_2);
return x_281;
}
block_289:
{
lean_object* x_284; lean_object* x_285; uint8_t x_286; lean_object* x_287; lean_object* x_288; 
x_284 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__81));
x_285 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_285, 0, x_283);
lean_ctor_set(x_285, 1, x_284);
x_286 = 0;
x_287 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_287, 0, x_285);
lean_ctor_set_uint8(x_287, sizeof(void*)*1, x_286);
x_288 = l_Repr_addAppParen(x_287, x_2);
return x_288;
}
block_296:
{
lean_object* x_291; lean_object* x_292; uint8_t x_293; lean_object* x_294; lean_object* x_295; 
x_291 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__83));
x_292 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_292, 0, x_290);
lean_ctor_set(x_292, 1, x_291);
x_293 = 0;
x_294 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_294, 0, x_292);
lean_ctor_set_uint8(x_294, sizeof(void*)*1, x_293);
x_295 = l_Repr_addAppParen(x_294, x_2);
return x_295;
}
block_303:
{
lean_object* x_298; lean_object* x_299; uint8_t x_300; lean_object* x_301; lean_object* x_302; 
x_298 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__85));
x_299 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_299, 0, x_297);
lean_ctor_set(x_299, 1, x_298);
x_300 = 0;
x_301 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_301, 0, x_299);
lean_ctor_set_uint8(x_301, sizeof(void*)*1, x_300);
x_302 = l_Repr_addAppParen(x_301, x_2);
return x_302;
}
block_310:
{
lean_object* x_305; lean_object* x_306; uint8_t x_307; lean_object* x_308; lean_object* x_309; 
x_305 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__87));
x_306 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_306, 0, x_304);
lean_ctor_set(x_306, 1, x_305);
x_307 = 0;
x_308 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_308, 0, x_306);
lean_ctor_set_uint8(x_308, sizeof(void*)*1, x_307);
x_309 = l_Repr_addAppParen(x_308, x_2);
return x_309;
}
block_317:
{
lean_object* x_312; lean_object* x_313; uint8_t x_314; lean_object* x_315; lean_object* x_316; 
x_312 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__89));
x_313 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_313, 0, x_311);
lean_ctor_set(x_313, 1, x_312);
x_314 = 0;
x_315 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_315, 0, x_313);
lean_ctor_set_uint8(x_315, sizeof(void*)*1, x_314);
x_316 = l_Repr_addAppParen(x_315, x_2);
return x_316;
}
block_324:
{
lean_object* x_319; lean_object* x_320; uint8_t x_321; lean_object* x_322; lean_object* x_323; 
x_319 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__91));
x_320 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_320, 0, x_318);
lean_ctor_set(x_320, 1, x_319);
x_321 = 0;
x_322 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_322, 0, x_320);
lean_ctor_set_uint8(x_322, sizeof(void*)*1, x_321);
x_323 = l_Repr_addAppParen(x_322, x_2);
return x_323;
}
block_331:
{
lean_object* x_326; lean_object* x_327; uint8_t x_328; lean_object* x_329; lean_object* x_330; 
x_326 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__93));
x_327 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_327, 0, x_325);
lean_ctor_set(x_327, 1, x_326);
x_328 = 0;
x_329 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_329, 0, x_327);
lean_ctor_set_uint8(x_329, sizeof(void*)*1, x_328);
x_330 = l_Repr_addAppParen(x_329, x_2);
return x_330;
}
block_338:
{
lean_object* x_333; lean_object* x_334; uint8_t x_335; lean_object* x_336; lean_object* x_337; 
x_333 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__95));
x_334 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_334, 0, x_332);
lean_ctor_set(x_334, 1, x_333);
x_335 = 0;
x_336 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_336, 0, x_334);
lean_ctor_set_uint8(x_336, sizeof(void*)*1, x_335);
x_337 = l_Repr_addAppParen(x_336, x_2);
return x_337;
}
block_345:
{
lean_object* x_340; lean_object* x_341; uint8_t x_342; lean_object* x_343; lean_object* x_344; 
x_340 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__97));
x_341 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_341, 0, x_339);
lean_ctor_set(x_341, 1, x_340);
x_342 = 0;
x_343 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_343, 0, x_341);
lean_ctor_set_uint8(x_343, sizeof(void*)*1, x_342);
x_344 = l_Repr_addAppParen(x_343, x_2);
return x_344;
}
block_352:
{
lean_object* x_347; lean_object* x_348; uint8_t x_349; lean_object* x_350; lean_object* x_351; 
x_347 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__99));
x_348 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_348, 0, x_346);
lean_ctor_set(x_348, 1, x_347);
x_349 = 0;
x_350 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_350, 0, x_348);
lean_ctor_set_uint8(x_350, sizeof(void*)*1, x_349);
x_351 = l_Repr_addAppParen(x_350, x_2);
return x_351;
}
block_359:
{
lean_object* x_354; lean_object* x_355; uint8_t x_356; lean_object* x_357; lean_object* x_358; 
x_354 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__101));
x_355 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_355, 0, x_353);
lean_ctor_set(x_355, 1, x_354);
x_356 = 0;
x_357 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_357, 0, x_355);
lean_ctor_set_uint8(x_357, sizeof(void*)*1, x_356);
x_358 = l_Repr_addAppParen(x_357, x_2);
return x_358;
}
block_366:
{
lean_object* x_361; lean_object* x_362; uint8_t x_363; lean_object* x_364; lean_object* x_365; 
x_361 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__103));
x_362 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_362, 0, x_360);
lean_ctor_set(x_362, 1, x_361);
x_363 = 0;
x_364 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_364, 0, x_362);
lean_ctor_set_uint8(x_364, sizeof(void*)*1, x_363);
x_365 = l_Repr_addAppParen(x_364, x_2);
return x_365;
}
block_373:
{
lean_object* x_368; lean_object* x_369; uint8_t x_370; lean_object* x_371; lean_object* x_372; 
x_368 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__105));
x_369 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_369, 0, x_367);
lean_ctor_set(x_369, 1, x_368);
x_370 = 0;
x_371 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_371, 0, x_369);
lean_ctor_set_uint8(x_371, sizeof(void*)*1, x_370);
x_372 = l_Repr_addAppParen(x_371, x_2);
return x_372;
}
block_380:
{
lean_object* x_375; lean_object* x_376; uint8_t x_377; lean_object* x_378; lean_object* x_379; 
x_375 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__107));
x_376 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_376, 0, x_374);
lean_ctor_set(x_376, 1, x_375);
x_377 = 0;
x_378 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_378, 0, x_376);
lean_ctor_set_uint8(x_378, sizeof(void*)*1, x_377);
x_379 = l_Repr_addAppParen(x_378, x_2);
return x_379;
}
block_387:
{
lean_object* x_382; lean_object* x_383; uint8_t x_384; lean_object* x_385; lean_object* x_386; 
x_382 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__109));
x_383 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_383, 0, x_381);
lean_ctor_set(x_383, 1, x_382);
x_384 = 0;
x_385 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_385, 0, x_383);
lean_ctor_set_uint8(x_385, sizeof(void*)*1, x_384);
x_386 = l_Repr_addAppParen(x_385, x_2);
return x_386;
}
block_394:
{
lean_object* x_389; lean_object* x_390; uint8_t x_391; lean_object* x_392; lean_object* x_393; 
x_389 = ((lean_object*)(lp_dasmodel_instReprMnemonic_repr___closed__111));
x_390 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_390, 0, x_388);
lean_ctor_set(x_390, 1, x_389);
x_391 = 0;
x_392 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_392, 0, x_390);
lean_ctor_set_uint8(x_392, sizeof(void*)*1, x_391);
x_393 = l_Repr_addAppParen(x_392, x_2);
return x_393;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprMnemonic_repr___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_1);
x_4 = lp_dasmodel_instReprMnemonic_repr(x_3, x_2);
lean_dec(x_2);
return x_4;
}
}
LEAN_EXPORT uint8_t lp_dasmodel_instBEqMnemonic_beq(uint8_t x_1, uint8_t x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; uint8_t x_5; 
x_3 = lp_dasmodel_Mnemonic_ctorIdx(x_1);
x_4 = lp_dasmodel_Mnemonic_ctorIdx(x_2);
x_5 = lean_nat_dec_eq(x_3, x_4);
lean_dec(x_4);
lean_dec(x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instBEqMnemonic_beq___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; uint8_t x_5; lean_object* x_6; 
x_3 = lean_unbox(x_1);
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel_instBEqMnemonic_beq(x_3, x_4);
x_6 = lean_box(x_5);
return x_6;
}
}
static lean_object* _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(12u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__12(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(8u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__14(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__0));
x_2 = lean_string_length(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__15(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_instReprInstruction_repr___redArg___closed__14, &lp_dasmodel_instReprInstruction_repr___redArg___closed__14_once, _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__14);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprInstruction_repr___redArg(lean_object* x_1) {
_start:
{
uint8_t x_2; 
x_2 = !lean_is_exclusive(x_1);
if (x_2 == 0)
{
uint8_t x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint8_t x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; 
x_3 = lean_ctor_get_uint8(x_1, sizeof(void*)*1);
x_4 = lean_ctor_get(x_1, 0);
x_5 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__5));
x_6 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__6));
x_7 = lean_obj_once(&lp_dasmodel_instReprInstruction_repr___redArg___closed__7, &lp_dasmodel_instReprInstruction_repr___redArg___closed__7_once, _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__7);
x_8 = lean_unsigned_to_nat(0u);
x_9 = lp_dasmodel_instReprMnemonic_repr(x_3, x_8);
x_10 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_10, 0, x_7);
lean_ctor_set(x_10, 1, x_9);
x_11 = 0;
lean_ctor_set_tag(x_1, 6);
lean_ctor_set(x_1, 0, x_10);
lean_ctor_set_uint8(x_1, sizeof(void*)*1, x_11);
x_12 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_12, 0, x_6);
lean_ctor_set(x_12, 1, x_1);
x_13 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__9));
x_14 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_14, 0, x_12);
lean_ctor_set(x_14, 1, x_13);
x_15 = lean_box(1);
x_16 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_16, 0, x_14);
lean_ctor_set(x_16, 1, x_15);
x_17 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__11));
x_18 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_18, 0, x_16);
lean_ctor_set(x_18, 1, x_17);
x_19 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_19, 0, x_18);
lean_ctor_set(x_19, 1, x_5);
x_20 = lean_obj_once(&lp_dasmodel_instReprInstruction_repr___redArg___closed__12, &lp_dasmodel_instReprInstruction_repr___redArg___closed__12_once, _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__12);
x_21 = lp_dasmodel_instReprAddrMode_repr(x_4, x_8);
lean_dec(x_4);
x_22 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_22, 0, x_20);
lean_ctor_set(x_22, 1, x_21);
x_23 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_23, 0, x_22);
lean_ctor_set_uint8(x_23, sizeof(void*)*1, x_11);
x_24 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_24, 0, x_19);
lean_ctor_set(x_24, 1, x_23);
x_25 = lean_obj_once(&lp_dasmodel_instReprInstruction_repr___redArg___closed__15, &lp_dasmodel_instReprInstruction_repr___redArg___closed__15_once, _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__15);
x_26 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__16));
x_27 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_27, 0, x_26);
lean_ctor_set(x_27, 1, x_24);
x_28 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__17));
x_29 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_29, 0, x_27);
lean_ctor_set(x_29, 1, x_28);
x_30 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_30, 0, x_25);
lean_ctor_set(x_30, 1, x_29);
x_31 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_31, 0, x_30);
lean_ctor_set_uint8(x_31, sizeof(void*)*1, x_11);
return x_31;
}
else
{
uint8_t x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; uint8_t x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; 
x_32 = lean_ctor_get_uint8(x_1, sizeof(void*)*1);
x_33 = lean_ctor_get(x_1, 0);
lean_inc(x_33);
lean_dec(x_1);
x_34 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__5));
x_35 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__6));
x_36 = lean_obj_once(&lp_dasmodel_instReprInstruction_repr___redArg___closed__7, &lp_dasmodel_instReprInstruction_repr___redArg___closed__7_once, _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__7);
x_37 = lean_unsigned_to_nat(0u);
x_38 = lp_dasmodel_instReprMnemonic_repr(x_32, x_37);
x_39 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_39, 0, x_36);
lean_ctor_set(x_39, 1, x_38);
x_40 = 0;
x_41 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_41, 0, x_39);
lean_ctor_set_uint8(x_41, sizeof(void*)*1, x_40);
x_42 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_42, 0, x_35);
lean_ctor_set(x_42, 1, x_41);
x_43 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__9));
x_44 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_44, 0, x_42);
lean_ctor_set(x_44, 1, x_43);
x_45 = lean_box(1);
x_46 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_46, 0, x_44);
lean_ctor_set(x_46, 1, x_45);
x_47 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__11));
x_48 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_48, 0, x_46);
lean_ctor_set(x_48, 1, x_47);
x_49 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_49, 0, x_48);
lean_ctor_set(x_49, 1, x_34);
x_50 = lean_obj_once(&lp_dasmodel_instReprInstruction_repr___redArg___closed__12, &lp_dasmodel_instReprInstruction_repr___redArg___closed__12_once, _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__12);
x_51 = lp_dasmodel_instReprAddrMode_repr(x_33, x_37);
lean_dec(x_33);
x_52 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_52, 0, x_50);
lean_ctor_set(x_52, 1, x_51);
x_53 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_53, 0, x_52);
lean_ctor_set_uint8(x_53, sizeof(void*)*1, x_40);
x_54 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_54, 0, x_49);
lean_ctor_set(x_54, 1, x_53);
x_55 = lean_obj_once(&lp_dasmodel_instReprInstruction_repr___redArg___closed__15, &lp_dasmodel_instReprInstruction_repr___redArg___closed__15_once, _init_lp_dasmodel_instReprInstruction_repr___redArg___closed__15);
x_56 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__16));
x_57 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_57, 0, x_56);
lean_ctor_set(x_57, 1, x_54);
x_58 = ((lean_object*)(lp_dasmodel_instReprInstruction_repr___redArg___closed__17));
x_59 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_59, 0, x_57);
lean_ctor_set(x_59, 1, x_58);
x_60 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_60, 0, x_55);
lean_ctor_set(x_60, 1, x_59);
x_61 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_61, 0, x_60);
lean_ctor_set_uint8(x_61, sizeof(void*)*1, x_40);
return x_61;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprInstruction_repr(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_instReprInstruction_repr___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprInstruction_repr___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_instReprInstruction_repr(x_1, x_2);
lean_dec(x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__0(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 169;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__1(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 165;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__2(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 181;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__3(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 173;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__4(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 189;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__5(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 185;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__6(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 177;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__7(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 162;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__8(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 166;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__9(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 174;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__10(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 160;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__11(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 164;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__12(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 172;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__13(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 133;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__14(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 149;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__15(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 141;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__16(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 157;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__17(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 153;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__18(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 145;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__19(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 134;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__20(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 142;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__21(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 132;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__22(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 140;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__23(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 105;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__24(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 101;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__25(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 109;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__26(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 121;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__27(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 233;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__28(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 229;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__29(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 41;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__30(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 37;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__31(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 9;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__32(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 5;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__33(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 73;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__34(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 201;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__35(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 197;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__36(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 221;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__37(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 217;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__38(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 224;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__39(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 192;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__40(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 230;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__41(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 246;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__42(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 238;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__43(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 198;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__44(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 214;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__45(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 206;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__46(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 232;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__47(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 202;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__48(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 200;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__49(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 136;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__50(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 10;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__51(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 6;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__52(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 74;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__53(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 70;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__54(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 42;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__55(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 106;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__56(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 102;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__57(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 144;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__58(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 176;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__59(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 240;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__60(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 208;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__61(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 48;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__62(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 16;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__63(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 80;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__64(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 112;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__65(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 76;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__66(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 32;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__67(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 96;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__68(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 64;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__69(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 72;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__70(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 104;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__71(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 170;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__72(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 168;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__73(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 138;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__74(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 152;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__75(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 24;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__76(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 56;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__77(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 120;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__78(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 88;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__79(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 36;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__80(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 44;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__81(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 234;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
static lean_object* _init_lp_dasmodel_opcode___closed__82(void) {
_start:
{
uint8_t x_1; lean_object* x_2; lean_object* x_3; 
x_1 = 0;
x_2 = lean_box(x_1);
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_opcode(uint8_t x_1, lean_object* x_2) {
_start:
{
switch (x_1) {
case 0:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_3; 
x_3 = lean_obj_once(&lp_dasmodel_opcode___closed__0, &lp_dasmodel_opcode___closed__0_once, _init_lp_dasmodel_opcode___closed__0);
return x_3;
}
case 1:
{
lean_object* x_4; 
x_4 = lean_obj_once(&lp_dasmodel_opcode___closed__1, &lp_dasmodel_opcode___closed__1_once, _init_lp_dasmodel_opcode___closed__1);
return x_4;
}
case 2:
{
lean_object* x_5; 
x_5 = lean_obj_once(&lp_dasmodel_opcode___closed__2, &lp_dasmodel_opcode___closed__2_once, _init_lp_dasmodel_opcode___closed__2);
return x_5;
}
case 4:
{
lean_object* x_6; 
x_6 = lean_obj_once(&lp_dasmodel_opcode___closed__3, &lp_dasmodel_opcode___closed__3_once, _init_lp_dasmodel_opcode___closed__3);
return x_6;
}
case 5:
{
lean_object* x_7; 
x_7 = lean_obj_once(&lp_dasmodel_opcode___closed__4, &lp_dasmodel_opcode___closed__4_once, _init_lp_dasmodel_opcode___closed__4);
return x_7;
}
case 6:
{
lean_object* x_8; 
x_8 = lean_obj_once(&lp_dasmodel_opcode___closed__5, &lp_dasmodel_opcode___closed__5_once, _init_lp_dasmodel_opcode___closed__5);
return x_8;
}
case 9:
{
lean_object* x_9; 
x_9 = lean_obj_once(&lp_dasmodel_opcode___closed__6, &lp_dasmodel_opcode___closed__6_once, _init_lp_dasmodel_opcode___closed__6);
return x_9;
}
default: 
{
lean_object* x_10; 
x_10 = lean_box(0);
return x_10;
}
}
}
case 1:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_11; 
x_11 = lean_obj_once(&lp_dasmodel_opcode___closed__7, &lp_dasmodel_opcode___closed__7_once, _init_lp_dasmodel_opcode___closed__7);
return x_11;
}
case 1:
{
lean_object* x_12; 
x_12 = lean_obj_once(&lp_dasmodel_opcode___closed__8, &lp_dasmodel_opcode___closed__8_once, _init_lp_dasmodel_opcode___closed__8);
return x_12;
}
case 4:
{
lean_object* x_13; 
x_13 = lean_obj_once(&lp_dasmodel_opcode___closed__9, &lp_dasmodel_opcode___closed__9_once, _init_lp_dasmodel_opcode___closed__9);
return x_13;
}
default: 
{
lean_object* x_14; 
x_14 = lean_box(0);
return x_14;
}
}
}
case 2:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_15; 
x_15 = lean_obj_once(&lp_dasmodel_opcode___closed__10, &lp_dasmodel_opcode___closed__10_once, _init_lp_dasmodel_opcode___closed__10);
return x_15;
}
case 1:
{
lean_object* x_16; 
x_16 = lean_obj_once(&lp_dasmodel_opcode___closed__11, &lp_dasmodel_opcode___closed__11_once, _init_lp_dasmodel_opcode___closed__11);
return x_16;
}
case 4:
{
lean_object* x_17; 
x_17 = lean_obj_once(&lp_dasmodel_opcode___closed__12, &lp_dasmodel_opcode___closed__12_once, _init_lp_dasmodel_opcode___closed__12);
return x_17;
}
default: 
{
lean_object* x_18; 
x_18 = lean_box(0);
return x_18;
}
}
}
case 3:
{
switch (lean_obj_tag(x_2)) {
case 1:
{
lean_object* x_19; 
x_19 = lean_obj_once(&lp_dasmodel_opcode___closed__13, &lp_dasmodel_opcode___closed__13_once, _init_lp_dasmodel_opcode___closed__13);
return x_19;
}
case 2:
{
lean_object* x_20; 
x_20 = lean_obj_once(&lp_dasmodel_opcode___closed__14, &lp_dasmodel_opcode___closed__14_once, _init_lp_dasmodel_opcode___closed__14);
return x_20;
}
case 4:
{
lean_object* x_21; 
x_21 = lean_obj_once(&lp_dasmodel_opcode___closed__15, &lp_dasmodel_opcode___closed__15_once, _init_lp_dasmodel_opcode___closed__15);
return x_21;
}
case 5:
{
lean_object* x_22; 
x_22 = lean_obj_once(&lp_dasmodel_opcode___closed__16, &lp_dasmodel_opcode___closed__16_once, _init_lp_dasmodel_opcode___closed__16);
return x_22;
}
case 6:
{
lean_object* x_23; 
x_23 = lean_obj_once(&lp_dasmodel_opcode___closed__17, &lp_dasmodel_opcode___closed__17_once, _init_lp_dasmodel_opcode___closed__17);
return x_23;
}
case 9:
{
lean_object* x_24; 
x_24 = lean_obj_once(&lp_dasmodel_opcode___closed__18, &lp_dasmodel_opcode___closed__18_once, _init_lp_dasmodel_opcode___closed__18);
return x_24;
}
default: 
{
lean_object* x_25; 
x_25 = lean_box(0);
return x_25;
}
}
}
case 4:
{
switch (lean_obj_tag(x_2)) {
case 1:
{
lean_object* x_26; 
x_26 = lean_obj_once(&lp_dasmodel_opcode___closed__19, &lp_dasmodel_opcode___closed__19_once, _init_lp_dasmodel_opcode___closed__19);
return x_26;
}
case 4:
{
lean_object* x_27; 
x_27 = lean_obj_once(&lp_dasmodel_opcode___closed__20, &lp_dasmodel_opcode___closed__20_once, _init_lp_dasmodel_opcode___closed__20);
return x_27;
}
default: 
{
lean_object* x_28; 
x_28 = lean_box(0);
return x_28;
}
}
}
case 5:
{
switch (lean_obj_tag(x_2)) {
case 1:
{
lean_object* x_29; 
x_29 = lean_obj_once(&lp_dasmodel_opcode___closed__21, &lp_dasmodel_opcode___closed__21_once, _init_lp_dasmodel_opcode___closed__21);
return x_29;
}
case 4:
{
lean_object* x_30; 
x_30 = lean_obj_once(&lp_dasmodel_opcode___closed__22, &lp_dasmodel_opcode___closed__22_once, _init_lp_dasmodel_opcode___closed__22);
return x_30;
}
default: 
{
lean_object* x_31; 
x_31 = lean_box(0);
return x_31;
}
}
}
case 6:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_32; 
x_32 = lean_obj_once(&lp_dasmodel_opcode___closed__23, &lp_dasmodel_opcode___closed__23_once, _init_lp_dasmodel_opcode___closed__23);
return x_32;
}
case 1:
{
lean_object* x_33; 
x_33 = lean_obj_once(&lp_dasmodel_opcode___closed__24, &lp_dasmodel_opcode___closed__24_once, _init_lp_dasmodel_opcode___closed__24);
return x_33;
}
case 4:
{
lean_object* x_34; 
x_34 = lean_obj_once(&lp_dasmodel_opcode___closed__25, &lp_dasmodel_opcode___closed__25_once, _init_lp_dasmodel_opcode___closed__25);
return x_34;
}
case 6:
{
lean_object* x_35; 
x_35 = lean_obj_once(&lp_dasmodel_opcode___closed__26, &lp_dasmodel_opcode___closed__26_once, _init_lp_dasmodel_opcode___closed__26);
return x_35;
}
default: 
{
lean_object* x_36; 
x_36 = lean_box(0);
return x_36;
}
}
}
case 7:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_37; 
x_37 = lean_obj_once(&lp_dasmodel_opcode___closed__27, &lp_dasmodel_opcode___closed__27_once, _init_lp_dasmodel_opcode___closed__27);
return x_37;
}
case 1:
{
lean_object* x_38; 
x_38 = lean_obj_once(&lp_dasmodel_opcode___closed__28, &lp_dasmodel_opcode___closed__28_once, _init_lp_dasmodel_opcode___closed__28);
return x_38;
}
default: 
{
lean_object* x_39; 
x_39 = lean_box(0);
return x_39;
}
}
}
case 8:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_40; 
x_40 = lean_obj_once(&lp_dasmodel_opcode___closed__29, &lp_dasmodel_opcode___closed__29_once, _init_lp_dasmodel_opcode___closed__29);
return x_40;
}
case 1:
{
lean_object* x_41; 
x_41 = lean_obj_once(&lp_dasmodel_opcode___closed__30, &lp_dasmodel_opcode___closed__30_once, _init_lp_dasmodel_opcode___closed__30);
return x_41;
}
default: 
{
lean_object* x_42; 
x_42 = lean_box(0);
return x_42;
}
}
}
case 9:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_43; 
x_43 = lean_obj_once(&lp_dasmodel_opcode___closed__31, &lp_dasmodel_opcode___closed__31_once, _init_lp_dasmodel_opcode___closed__31);
return x_43;
}
case 1:
{
lean_object* x_44; 
x_44 = lean_obj_once(&lp_dasmodel_opcode___closed__32, &lp_dasmodel_opcode___closed__32_once, _init_lp_dasmodel_opcode___closed__32);
return x_44;
}
default: 
{
lean_object* x_45; 
x_45 = lean_box(0);
return x_45;
}
}
}
case 10:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_46; 
x_46 = lean_obj_once(&lp_dasmodel_opcode___closed__33, &lp_dasmodel_opcode___closed__33_once, _init_lp_dasmodel_opcode___closed__33);
return x_46;
}
else
{
lean_object* x_47; 
x_47 = lean_box(0);
return x_47;
}
}
case 11:
{
switch (lean_obj_tag(x_2)) {
case 0:
{
lean_object* x_48; 
x_48 = lean_obj_once(&lp_dasmodel_opcode___closed__34, &lp_dasmodel_opcode___closed__34_once, _init_lp_dasmodel_opcode___closed__34);
return x_48;
}
case 1:
{
lean_object* x_49; 
x_49 = lean_obj_once(&lp_dasmodel_opcode___closed__35, &lp_dasmodel_opcode___closed__35_once, _init_lp_dasmodel_opcode___closed__35);
return x_49;
}
case 5:
{
lean_object* x_50; 
x_50 = lean_obj_once(&lp_dasmodel_opcode___closed__36, &lp_dasmodel_opcode___closed__36_once, _init_lp_dasmodel_opcode___closed__36);
return x_50;
}
case 6:
{
lean_object* x_51; 
x_51 = lean_obj_once(&lp_dasmodel_opcode___closed__37, &lp_dasmodel_opcode___closed__37_once, _init_lp_dasmodel_opcode___closed__37);
return x_51;
}
default: 
{
lean_object* x_52; 
x_52 = lean_box(0);
return x_52;
}
}
}
case 12:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_53; 
x_53 = lean_obj_once(&lp_dasmodel_opcode___closed__38, &lp_dasmodel_opcode___closed__38_once, _init_lp_dasmodel_opcode___closed__38);
return x_53;
}
else
{
lean_object* x_54; 
x_54 = lean_box(0);
return x_54;
}
}
case 13:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_55; 
x_55 = lean_obj_once(&lp_dasmodel_opcode___closed__39, &lp_dasmodel_opcode___closed__39_once, _init_lp_dasmodel_opcode___closed__39);
return x_55;
}
else
{
lean_object* x_56; 
x_56 = lean_box(0);
return x_56;
}
}
case 14:
{
switch (lean_obj_tag(x_2)) {
case 1:
{
lean_object* x_57; 
x_57 = lean_obj_once(&lp_dasmodel_opcode___closed__40, &lp_dasmodel_opcode___closed__40_once, _init_lp_dasmodel_opcode___closed__40);
return x_57;
}
case 2:
{
lean_object* x_58; 
x_58 = lean_obj_once(&lp_dasmodel_opcode___closed__41, &lp_dasmodel_opcode___closed__41_once, _init_lp_dasmodel_opcode___closed__41);
return x_58;
}
case 4:
{
lean_object* x_59; 
x_59 = lean_obj_once(&lp_dasmodel_opcode___closed__42, &lp_dasmodel_opcode___closed__42_once, _init_lp_dasmodel_opcode___closed__42);
return x_59;
}
default: 
{
lean_object* x_60; 
x_60 = lean_box(0);
return x_60;
}
}
}
case 15:
{
switch (lean_obj_tag(x_2)) {
case 1:
{
lean_object* x_61; 
x_61 = lean_obj_once(&lp_dasmodel_opcode___closed__43, &lp_dasmodel_opcode___closed__43_once, _init_lp_dasmodel_opcode___closed__43);
return x_61;
}
case 2:
{
lean_object* x_62; 
x_62 = lean_obj_once(&lp_dasmodel_opcode___closed__44, &lp_dasmodel_opcode___closed__44_once, _init_lp_dasmodel_opcode___closed__44);
return x_62;
}
case 4:
{
lean_object* x_63; 
x_63 = lean_obj_once(&lp_dasmodel_opcode___closed__45, &lp_dasmodel_opcode___closed__45_once, _init_lp_dasmodel_opcode___closed__45);
return x_63;
}
default: 
{
lean_object* x_64; 
x_64 = lean_box(0);
return x_64;
}
}
}
case 16:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_65; 
x_65 = lean_obj_once(&lp_dasmodel_opcode___closed__46, &lp_dasmodel_opcode___closed__46_once, _init_lp_dasmodel_opcode___closed__46);
return x_65;
}
else
{
lean_object* x_66; 
x_66 = lean_box(0);
return x_66;
}
}
case 17:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_67; 
x_67 = lean_obj_once(&lp_dasmodel_opcode___closed__47, &lp_dasmodel_opcode___closed__47_once, _init_lp_dasmodel_opcode___closed__47);
return x_67;
}
else
{
lean_object* x_68; 
x_68 = lean_box(0);
return x_68;
}
}
case 18:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_69; 
x_69 = lean_obj_once(&lp_dasmodel_opcode___closed__48, &lp_dasmodel_opcode___closed__48_once, _init_lp_dasmodel_opcode___closed__48);
return x_69;
}
else
{
lean_object* x_70; 
x_70 = lean_box(0);
return x_70;
}
}
case 19:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_71; 
x_71 = lean_obj_once(&lp_dasmodel_opcode___closed__49, &lp_dasmodel_opcode___closed__49_once, _init_lp_dasmodel_opcode___closed__49);
return x_71;
}
else
{
lean_object* x_72; 
x_72 = lean_box(0);
return x_72;
}
}
case 20:
{
switch (lean_obj_tag(x_2)) {
case 11:
{
lean_object* x_73; 
x_73 = lean_obj_once(&lp_dasmodel_opcode___closed__50, &lp_dasmodel_opcode___closed__50_once, _init_lp_dasmodel_opcode___closed__50);
return x_73;
}
case 1:
{
lean_object* x_74; 
x_74 = lean_obj_once(&lp_dasmodel_opcode___closed__51, &lp_dasmodel_opcode___closed__51_once, _init_lp_dasmodel_opcode___closed__51);
return x_74;
}
default: 
{
lean_object* x_75; 
x_75 = lean_box(0);
return x_75;
}
}
}
case 21:
{
switch (lean_obj_tag(x_2)) {
case 11:
{
lean_object* x_76; 
x_76 = lean_obj_once(&lp_dasmodel_opcode___closed__52, &lp_dasmodel_opcode___closed__52_once, _init_lp_dasmodel_opcode___closed__52);
return x_76;
}
case 1:
{
lean_object* x_77; 
x_77 = lean_obj_once(&lp_dasmodel_opcode___closed__53, &lp_dasmodel_opcode___closed__53_once, _init_lp_dasmodel_opcode___closed__53);
return x_77;
}
default: 
{
lean_object* x_78; 
x_78 = lean_box(0);
return x_78;
}
}
}
case 22:
{
if (lean_obj_tag(x_2) == 11)
{
lean_object* x_79; 
x_79 = lean_obj_once(&lp_dasmodel_opcode___closed__54, &lp_dasmodel_opcode___closed__54_once, _init_lp_dasmodel_opcode___closed__54);
return x_79;
}
else
{
lean_object* x_80; 
x_80 = lean_box(0);
return x_80;
}
}
case 23:
{
switch (lean_obj_tag(x_2)) {
case 11:
{
lean_object* x_81; 
x_81 = lean_obj_once(&lp_dasmodel_opcode___closed__55, &lp_dasmodel_opcode___closed__55_once, _init_lp_dasmodel_opcode___closed__55);
return x_81;
}
case 1:
{
lean_object* x_82; 
x_82 = lean_obj_once(&lp_dasmodel_opcode___closed__56, &lp_dasmodel_opcode___closed__56_once, _init_lp_dasmodel_opcode___closed__56);
return x_82;
}
default: 
{
lean_object* x_83; 
x_83 = lean_box(0);
return x_83;
}
}
}
case 24:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_84; 
x_84 = lean_obj_once(&lp_dasmodel_opcode___closed__57, &lp_dasmodel_opcode___closed__57_once, _init_lp_dasmodel_opcode___closed__57);
return x_84;
}
else
{
lean_object* x_85; 
x_85 = lean_box(0);
return x_85;
}
}
case 25:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_86; 
x_86 = lean_obj_once(&lp_dasmodel_opcode___closed__58, &lp_dasmodel_opcode___closed__58_once, _init_lp_dasmodel_opcode___closed__58);
return x_86;
}
else
{
lean_object* x_87; 
x_87 = lean_box(0);
return x_87;
}
}
case 26:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_88; 
x_88 = lean_obj_once(&lp_dasmodel_opcode___closed__59, &lp_dasmodel_opcode___closed__59_once, _init_lp_dasmodel_opcode___closed__59);
return x_88;
}
else
{
lean_object* x_89; 
x_89 = lean_box(0);
return x_89;
}
}
case 27:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_90; 
x_90 = lean_obj_once(&lp_dasmodel_opcode___closed__60, &lp_dasmodel_opcode___closed__60_once, _init_lp_dasmodel_opcode___closed__60);
return x_90;
}
else
{
lean_object* x_91; 
x_91 = lean_box(0);
return x_91;
}
}
case 28:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_92; 
x_92 = lean_obj_once(&lp_dasmodel_opcode___closed__61, &lp_dasmodel_opcode___closed__61_once, _init_lp_dasmodel_opcode___closed__61);
return x_92;
}
else
{
lean_object* x_93; 
x_93 = lean_box(0);
return x_93;
}
}
case 29:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_94; 
x_94 = lean_obj_once(&lp_dasmodel_opcode___closed__62, &lp_dasmodel_opcode___closed__62_once, _init_lp_dasmodel_opcode___closed__62);
return x_94;
}
else
{
lean_object* x_95; 
x_95 = lean_box(0);
return x_95;
}
}
case 30:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_96; 
x_96 = lean_obj_once(&lp_dasmodel_opcode___closed__63, &lp_dasmodel_opcode___closed__63_once, _init_lp_dasmodel_opcode___closed__63);
return x_96;
}
else
{
lean_object* x_97; 
x_97 = lean_box(0);
return x_97;
}
}
case 31:
{
if (lean_obj_tag(x_2) == 12)
{
lean_object* x_98; 
x_98 = lean_obj_once(&lp_dasmodel_opcode___closed__64, &lp_dasmodel_opcode___closed__64_once, _init_lp_dasmodel_opcode___closed__64);
return x_98;
}
else
{
lean_object* x_99; 
x_99 = lean_box(0);
return x_99;
}
}
case 32:
{
if (lean_obj_tag(x_2) == 4)
{
lean_object* x_100; 
x_100 = lean_obj_once(&lp_dasmodel_opcode___closed__65, &lp_dasmodel_opcode___closed__65_once, _init_lp_dasmodel_opcode___closed__65);
return x_100;
}
else
{
lean_object* x_101; 
x_101 = lean_box(0);
return x_101;
}
}
case 33:
{
if (lean_obj_tag(x_2) == 4)
{
lean_object* x_102; 
x_102 = lean_obj_once(&lp_dasmodel_opcode___closed__66, &lp_dasmodel_opcode___closed__66_once, _init_lp_dasmodel_opcode___closed__66);
return x_102;
}
else
{
lean_object* x_103; 
x_103 = lean_box(0);
return x_103;
}
}
case 34:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_104; 
x_104 = lean_obj_once(&lp_dasmodel_opcode___closed__67, &lp_dasmodel_opcode___closed__67_once, _init_lp_dasmodel_opcode___closed__67);
return x_104;
}
else
{
lean_object* x_105; 
x_105 = lean_box(0);
return x_105;
}
}
case 35:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_106; 
x_106 = lean_obj_once(&lp_dasmodel_opcode___closed__68, &lp_dasmodel_opcode___closed__68_once, _init_lp_dasmodel_opcode___closed__68);
return x_106;
}
else
{
lean_object* x_107; 
x_107 = lean_box(0);
return x_107;
}
}
case 36:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_108; 
x_108 = lean_obj_once(&lp_dasmodel_opcode___closed__69, &lp_dasmodel_opcode___closed__69_once, _init_lp_dasmodel_opcode___closed__69);
return x_108;
}
else
{
lean_object* x_109; 
x_109 = lean_box(0);
return x_109;
}
}
case 37:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_110; 
x_110 = lean_obj_once(&lp_dasmodel_opcode___closed__70, &lp_dasmodel_opcode___closed__70_once, _init_lp_dasmodel_opcode___closed__70);
return x_110;
}
else
{
lean_object* x_111; 
x_111 = lean_box(0);
return x_111;
}
}
case 40:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_112; 
x_112 = lean_obj_once(&lp_dasmodel_opcode___closed__71, &lp_dasmodel_opcode___closed__71_once, _init_lp_dasmodel_opcode___closed__71);
return x_112;
}
else
{
lean_object* x_113; 
x_113 = lean_box(0);
return x_113;
}
}
case 41:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_114; 
x_114 = lean_obj_once(&lp_dasmodel_opcode___closed__72, &lp_dasmodel_opcode___closed__72_once, _init_lp_dasmodel_opcode___closed__72);
return x_114;
}
else
{
lean_object* x_115; 
x_115 = lean_box(0);
return x_115;
}
}
case 42:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_116; 
x_116 = lean_obj_once(&lp_dasmodel_opcode___closed__73, &lp_dasmodel_opcode___closed__73_once, _init_lp_dasmodel_opcode___closed__73);
return x_116;
}
else
{
lean_object* x_117; 
x_117 = lean_box(0);
return x_117;
}
}
case 43:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_118; 
x_118 = lean_obj_once(&lp_dasmodel_opcode___closed__74, &lp_dasmodel_opcode___closed__74_once, _init_lp_dasmodel_opcode___closed__74);
return x_118;
}
else
{
lean_object* x_119; 
x_119 = lean_box(0);
return x_119;
}
}
case 46:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_120; 
x_120 = lean_obj_once(&lp_dasmodel_opcode___closed__75, &lp_dasmodel_opcode___closed__75_once, _init_lp_dasmodel_opcode___closed__75);
return x_120;
}
else
{
lean_object* x_121; 
x_121 = lean_box(0);
return x_121;
}
}
case 47:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_122; 
x_122 = lean_obj_once(&lp_dasmodel_opcode___closed__76, &lp_dasmodel_opcode___closed__76_once, _init_lp_dasmodel_opcode___closed__76);
return x_122;
}
else
{
lean_object* x_123; 
x_123 = lean_box(0);
return x_123;
}
}
case 49:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_124; 
x_124 = lean_obj_once(&lp_dasmodel_opcode___closed__77, &lp_dasmodel_opcode___closed__77_once, _init_lp_dasmodel_opcode___closed__77);
return x_124;
}
else
{
lean_object* x_125; 
x_125 = lean_box(0);
return x_125;
}
}
case 48:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_126; 
x_126 = lean_obj_once(&lp_dasmodel_opcode___closed__78, &lp_dasmodel_opcode___closed__78_once, _init_lp_dasmodel_opcode___closed__78);
return x_126;
}
else
{
lean_object* x_127; 
x_127 = lean_box(0);
return x_127;
}
}
case 53:
{
switch (lean_obj_tag(x_2)) {
case 1:
{
lean_object* x_128; 
x_128 = lean_obj_once(&lp_dasmodel_opcode___closed__79, &lp_dasmodel_opcode___closed__79_once, _init_lp_dasmodel_opcode___closed__79);
return x_128;
}
case 4:
{
lean_object* x_129; 
x_129 = lean_obj_once(&lp_dasmodel_opcode___closed__80, &lp_dasmodel_opcode___closed__80_once, _init_lp_dasmodel_opcode___closed__80);
return x_129;
}
default: 
{
lean_object* x_130; 
x_130 = lean_box(0);
return x_130;
}
}
}
case 54:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_131; 
x_131 = lean_obj_once(&lp_dasmodel_opcode___closed__81, &lp_dasmodel_opcode___closed__81_once, _init_lp_dasmodel_opcode___closed__81);
return x_131;
}
else
{
lean_object* x_132; 
x_132 = lean_box(0);
return x_132;
}
}
case 55:
{
if (lean_obj_tag(x_2) == 10)
{
lean_object* x_133; 
x_133 = lean_obj_once(&lp_dasmodel_opcode___closed__82, &lp_dasmodel_opcode___closed__82_once, _init_lp_dasmodel_opcode___closed__82);
return x_133;
}
else
{
lean_object* x_134; 
x_134 = lean_box(0);
return x_134;
}
}
default: 
{
lean_object* x_135; 
x_135 = lean_box(0);
return x_135;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_opcode___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_1);
x_4 = lp_dasmodel_opcode(x_3, x_2);
lean_dec(x_2);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_operandBytes___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(1u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_operandBytes___closed__1(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(2u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_operandBytes___closed__2(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_operandBytes(lean_object* x_1) {
_start:
{
uint8_t x_2; uint16_t x_7; 
switch (lean_obj_tag(x_1)) {
case 0:
{
uint8_t x_18; 
x_18 = lean_ctor_get_uint8(x_1, 0);
x_2 = x_18;
goto block_6;
}
case 1:
{
uint8_t x_19; 
x_19 = lean_ctor_get_uint8(x_1, 0);
x_2 = x_19;
goto block_6;
}
case 2:
{
uint8_t x_20; 
x_20 = lean_ctor_get_uint8(x_1, 0);
x_2 = x_20;
goto block_6;
}
case 3:
{
uint8_t x_21; 
x_21 = lean_ctor_get_uint8(x_1, 0);
x_2 = x_21;
goto block_6;
}
case 4:
{
uint16_t x_22; 
x_22 = lean_ctor_get_uint16(x_1, 0);
x_7 = x_22;
goto block_17;
}
case 5:
{
uint16_t x_23; 
x_23 = lean_ctor_get_uint16(x_1, 0);
x_7 = x_23;
goto block_17;
}
case 6:
{
uint16_t x_24; 
x_24 = lean_ctor_get_uint16(x_1, 0);
x_7 = x_24;
goto block_17;
}
case 7:
{
uint16_t x_25; 
x_25 = lean_ctor_get_uint16(x_1, 0);
x_7 = x_25;
goto block_17;
}
case 8:
{
uint8_t x_26; 
x_26 = lean_ctor_get_uint8(x_1, 0);
x_2 = x_26;
goto block_6;
}
case 9:
{
uint8_t x_27; 
x_27 = lean_ctor_get_uint8(x_1, 0);
x_2 = x_27;
goto block_6;
}
case 12:
{
uint8_t x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; 
x_28 = lean_ctor_get_uint8(x_1, 0);
x_29 = lean_obj_once(&lp_dasmodel_operandBytes___closed__0, &lp_dasmodel_operandBytes___closed__0_once, _init_lp_dasmodel_operandBytes___closed__0);
x_30 = lean_box(x_28);
x_31 = lean_array_push(x_29, x_30);
return x_31;
}
default: 
{
lean_object* x_32; 
x_32 = lean_obj_once(&lp_dasmodel_operandBytes___closed__2, &lp_dasmodel_operandBytes___closed__2_once, _init_lp_dasmodel_operandBytes___closed__2);
return x_32;
}
}
block_6:
{
lean_object* x_3; lean_object* x_4; lean_object* x_5; 
x_3 = lean_obj_once(&lp_dasmodel_operandBytes___closed__0, &lp_dasmodel_operandBytes___closed__0_once, _init_lp_dasmodel_operandBytes___closed__0);
x_4 = lean_box(x_2);
x_5 = lean_array_push(x_3, x_4);
return x_5;
}
block_17:
{
uint8_t x_8; uint16_t x_9; uint16_t x_10; uint8_t x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; 
x_8 = lean_uint16_to_uint8(x_7);
x_9 = 8;
x_10 = lean_uint16_shift_right(x_7, x_9);
x_11 = lean_uint16_to_uint8(x_10);
x_12 = lean_obj_once(&lp_dasmodel_operandBytes___closed__1, &lp_dasmodel_operandBytes___closed__1_once, _init_lp_dasmodel_operandBytes___closed__1);
x_13 = lean_box(x_8);
x_14 = lean_array_push(x_12, x_13);
x_15 = lean_box(x_11);
x_16 = lean_array_push(x_14, x_15);
return x_16;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_operandBytes___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_operandBytes(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_assembleInst(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = lean_ctor_get_uint8(x_1, sizeof(void*)*1);
x_3 = lean_ctor_get(x_1, 0);
x_4 = lp_dasmodel_opcode(x_2, x_3);
if (lean_obj_tag(x_4) == 0)
{
lean_object* x_5; 
x_5 = lean_box(0);
return x_5;
}
else
{
uint8_t x_6; 
x_6 = !lean_is_exclusive(x_4);
if (x_6 == 0)
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_7 = lean_ctor_get(x_4, 0);
x_8 = lean_obj_once(&lp_dasmodel_operandBytes___closed__0, &lp_dasmodel_operandBytes___closed__0_once, _init_lp_dasmodel_operandBytes___closed__0);
x_9 = lean_array_push(x_8, x_7);
x_10 = lp_dasmodel_operandBytes(x_3);
x_11 = l_Array_append___redArg(x_9, x_10);
lean_dec_ref(x_10);
lean_ctor_set(x_4, 0, x_11);
return x_4;
}
else
{
lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_12 = lean_ctor_get(x_4, 0);
lean_inc(x_12);
lean_dec(x_4);
x_13 = lean_obj_once(&lp_dasmodel_operandBytes___closed__0, &lp_dasmodel_operandBytes___closed__0_once, _init_lp_dasmodel_operandBytes___closed__0);
x_14 = lean_array_push(x_13, x_12);
x_15 = lp_dasmodel_operandBytes(x_3);
x_16 = l_Array_append___redArg(x_14, x_15);
lean_dec_ref(x_15);
x_17 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_17, 0, x_16);
return x_17;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_assembleInst___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_assembleInst(x_1);
lean_dec_ref(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_foldlM___at___00assemble_spec__0(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_2) == 0)
{
lean_object* x_3; 
x_3 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_3, 0, x_1);
return x_3;
}
else
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; 
x_4 = lean_ctor_get(x_2, 0);
x_5 = lean_ctor_get(x_2, 1);
x_6 = lp_dasmodel_assembleInst(x_4);
if (lean_obj_tag(x_6) == 0)
{
lean_dec_ref(x_1);
if (lean_obj_tag(x_6) == 0)
{
return x_6;
}
else
{
lean_object* x_7; 
x_7 = lean_ctor_get(x_6, 0);
lean_inc(x_7);
lean_dec_ref(x_6);
x_1 = x_7;
x_2 = x_5;
goto _start;
}
}
else
{
lean_object* x_9; lean_object* x_10; 
x_9 = lean_ctor_get(x_6, 0);
lean_inc(x_9);
lean_dec_ref(x_6);
x_10 = l_Array_append___redArg(x_1, x_9);
lean_dec(x_9);
x_1 = x_10;
x_2 = x_5;
goto _start;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_List_foldlM___at___00assemble_spec__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_List_foldlM___at___00assemble_spec__0(x_1, x_2);
lean_dec(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_assemble(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; 
x_2 = lean_obj_once(&lp_dasmodel_operandBytes___closed__2, &lp_dasmodel_operandBytes___closed__2_once, _init_lp_dasmodel_operandBytes___closed__2);
x_3 = lp_dasmodel_List_foldlM___at___00assemble_spec__0(x_2, x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_assemble___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_assemble(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 0;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_lda__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 1;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_ldx__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 2;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_ldy__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__abs(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 3;
x_3 = lean_alloc_ctor(4, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__abs___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_sta__abs(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 3;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_sta__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 0;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_lda__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__abs(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 0;
x_3 = lean_alloc_ctor(4, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__abs___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_lda__abs(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absX(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 0;
x_3 = lean_alloc_ctor(5, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absX___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_lda__absX(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absY(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 0;
x_3 = lean_alloc_ctor(6, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_lda__absY___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_lda__absY(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absX(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 3;
x_3 = lean_alloc_ctor(5, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absX___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_sta__absX(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absY(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 3;
x_3 = lean_alloc_ctor(6, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sta__absY___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_sta__absY(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_inc__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 14;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_inc__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_inc__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_dec__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 15;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_dec__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_dec__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_cmp__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 11;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_cmp__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_cmp__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 6;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_adc__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 7;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_sbc__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 7;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sbc__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_sbc__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_and__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 8;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_and__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_and__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 9;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_ora__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bne(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 27;
x_3 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bne___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_bne(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_beq(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 26;
x_3 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_beq___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_beq(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bmi(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 28;
x_3 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bmi___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_bmi(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bpl(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 29;
x_3 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bpl___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_bpl(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bcc(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 24;
x_3 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bcc___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_bcc(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bcs(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 25;
x_3 = lean_alloc_ctor(12, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_bcs___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_bcs(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_jmp(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 32;
x_3 = lean_alloc_ctor(4, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_jmp___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_jmp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_jsr(uint16_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 33;
x_3 = lean_alloc_ctor(4, 0, 2);
lean_ctor_set_uint16(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_jsr___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_jsr(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_stx__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 4;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_stx__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_stx__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 1;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldx__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_ldx__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 9;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ora__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_ora__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 6;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_adc__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_adc__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sty__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 5;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_sty__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_sty__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__zp(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 2;
x_3 = lean_alloc_ctor(1, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_ldy__zp___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_ldy__zp(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_eor__imm(uint8_t x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; lean_object* x_4; 
x_2 = 10;
x_3 = lean_alloc_ctor(0, 0, 1);
lean_ctor_set_uint8(x_3, 0, x_1);
x_4 = lean_alloc_ctor(0, 1, 1);
lean_ctor_set(x_4, 0, x_3);
lean_ctor_set_uint8(x_4, sizeof(void*)*1, x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_I_eor__imm___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_I_eor__imm(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_rawByte(uint8_t x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_2 = lean_obj_once(&lp_dasmodel_operandBytes___closed__0, &lp_dasmodel_operandBytes___closed__0_once, _init_lp_dasmodel_operandBytes___closed__0);
x_3 = lean_box(x_1);
x_4 = lean_array_push(x_2, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_rawByte___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_rawByte(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_rawWord(uint16_t x_1) {
_start:
{
uint8_t x_2; uint16_t x_3; uint16_t x_4; uint8_t x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_2 = lean_uint16_to_uint8(x_1);
x_3 = 8;
x_4 = lean_uint16_shift_right(x_1, x_3);
x_5 = lean_uint16_to_uint8(x_4);
x_6 = lean_obj_once(&lp_dasmodel_operandBytes___closed__1, &lp_dasmodel_operandBytes___closed__1_once, _init_lp_dasmodel_operandBytes___closed__1);
x_7 = lean_box(x_2);
x_8 = lean_array_push(x_6, x_7);
x_9 = lean_box(x_5);
x_10 = lean_array_push(x_8, x_9);
return x_10;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_rawWord___boxed(lean_object* x_1) {
_start:
{
uint16_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_rawWord(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_rawBytes(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lean_array_mk(x_1);
return x_2;
}
}
lean_object* initialize_Init(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_Asm6502(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
