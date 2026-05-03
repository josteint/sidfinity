// Lean compiler output
// Module: CPU6502
// Imports: public import Init public import SID
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
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = "{ "};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__0 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__0_value;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 6, .m_capacity = 6, .m_length = 5, .m_data = "carry"};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__1 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__1_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__1_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__2 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__2_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__2_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__3 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__3_value;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = " := "};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__4 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__4_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__4_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__5 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__5_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*2 + 0, .m_other = 2, .m_tag = 5}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__3_value),((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__5_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__6 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__6_value;
lean_object* lean_nat_to_int(lean_object*);
static lean_once_cell_t lp_dasmodel_instReprFlags_repr___redArg___closed__7_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__7;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = ","};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__8 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__8_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__8_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__9 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__9_value;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 5, .m_capacity = 5, .m_length = 4, .m_data = "zero"};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__10 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__10_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__10_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__11 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__11_value;
static lean_once_cell_t lp_dasmodel_instReprFlags_repr___redArg___closed__12_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__12;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 7, .m_capacity = 7, .m_length = 6, .m_data = "irqDis"};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__13 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__13_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__13_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__14 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__14_value;
static lean_once_cell_t lp_dasmodel_instReprFlags_repr___redArg___closed__15_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__15;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 8, .m_capacity = 8, .m_length = 7, .m_data = "decimal"};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__16 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__16_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__16_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__17 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__17_value;
static lean_once_cell_t lp_dasmodel_instReprFlags_repr___redArg___closed__18_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__18;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "overflow"};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__19 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__19_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__19_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__20 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__20_value;
static lean_once_cell_t lp_dasmodel_instReprFlags_repr___redArg___closed__21_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__21;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__22_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 9, .m_capacity = 9, .m_length = 8, .m_data = "negative"};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__22 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__22_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__23_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__22_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__23 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__23_value;
static const lean_string_object lp_dasmodel_instReprFlags_repr___redArg___closed__24_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 3, .m_capacity = 3, .m_length = 2, .m_data = " }"};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__24 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__24_value;
lean_object* lean_string_length(lean_object*);
static lean_once_cell_t lp_dasmodel_instReprFlags_repr___redArg___closed__25_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__25;
static lean_once_cell_t lp_dasmodel_instReprFlags_repr___redArg___closed__26_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__26;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__27_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__0_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__27 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__27_value;
static const lean_ctor_object lp_dasmodel_instReprFlags_repr___redArg___closed__28_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__24_value)}};
static const lean_object* lp_dasmodel_instReprFlags_repr___redArg___closed__28 = (const lean_object*)&lp_dasmodel_instReprFlags_repr___redArg___closed__28_value;
lean_object* l_Bool_repr___redArg(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr___redArg(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_instReprFlags___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_instReprFlags_repr___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_instReprFlags___closed__0 = (const lean_object*)&lp_dasmodel_instReprFlags___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_instReprFlags = (const lean_object*)&lp_dasmodel_instReprFlags___closed__0_value;
LEAN_EXPORT uint8_t lp_dasmodel_instBEqFlags_beq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_instBEqFlags_beq___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_instBEqFlags___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_instBEqFlags_beq___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_instBEqFlags___closed__0 = (const lean_object*)&lp_dasmodel_instBEqFlags___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_instBEqFlags = (const lean_object*)&lp_dasmodel_instBEqFlags___closed__0_value;
lean_object* lean_uint16_to_nat(uint16_t);
uint8_t lean_byte_array_get(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel_CPU_read(lean_object*, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_read___boxed(lean_object*, lean_object*);
uint16_t lean_uint16_add(uint16_t, uint16_t);
uint16_t lean_uint8_to_uint16(uint8_t);
uint16_t lean_uint16_shift_left(uint16_t, uint16_t);
uint16_t lean_uint16_lor(uint16_t, uint16_t);
LEAN_EXPORT uint16_t lp_dasmodel_CPU_read16(lean_object*, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_read16___boxed(lean_object*, lean_object*);
uint8_t lean_uint8_add(uint8_t, uint8_t);
uint8_t lean_uint8_land(uint8_t, uint8_t);
LEAN_EXPORT uint16_t lp_dasmodel_CPU_readZP16(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_readZP16___boxed(lean_object*, lean_object*);
static const lean_ctor_object lp_dasmodel_CPU_write___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 6}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__0 = (const lean_object*)&lp_dasmodel_CPU_write___closed__0_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__1 = (const lean_object*)&lp_dasmodel_CPU_write___closed__1_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 4}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__2 = (const lean_object*)&lp_dasmodel_CPU_write___closed__2_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__3 = (const lean_object*)&lp_dasmodel_CPU_write___closed__3_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 2}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__4 = (const lean_object*)&lp_dasmodel_CPU_write___closed__4_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__5 = (const lean_object*)&lp_dasmodel_CPU_write___closed__5_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(2) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__6 = (const lean_object*)&lp_dasmodel_CPU_write___closed__6_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__7_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 6}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__7 = (const lean_object*)&lp_dasmodel_CPU_write___closed__7_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__8_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__8 = (const lean_object*)&lp_dasmodel_CPU_write___closed__8_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__9_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 4}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__9 = (const lean_object*)&lp_dasmodel_CPU_write___closed__9_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__10_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__10 = (const lean_object*)&lp_dasmodel_CPU_write___closed__10_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__11_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 2}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__11 = (const lean_object*)&lp_dasmodel_CPU_write___closed__11_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__12_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__12 = (const lean_object*)&lp_dasmodel_CPU_write___closed__12_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__13_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__13 = (const lean_object*)&lp_dasmodel_CPU_write___closed__13_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__14_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 6}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__14 = (const lean_object*)&lp_dasmodel_CPU_write___closed__14_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__15_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 5}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__15 = (const lean_object*)&lp_dasmodel_CPU_write___closed__15_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__16_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 4}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__16 = (const lean_object*)&lp_dasmodel_CPU_write___closed__16_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__17_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 3}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__17 = (const lean_object*)&lp_dasmodel_CPU_write___closed__17_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__18_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 2}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__18 = (const lean_object*)&lp_dasmodel_CPU_write___closed__18_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__19_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 1}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__19 = (const lean_object*)&lp_dasmodel_CPU_write___closed__19_value;
static const lean_ctor_object lp_dasmodel_CPU_write___closed__20_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*1 + 0, .m_other = 1, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))}};
static const lean_object* lp_dasmodel_CPU_write___closed__20 = (const lean_object*)&lp_dasmodel_CPU_write___closed__20_value;
lean_object* lean_byte_array_set(lean_object*, lean_object*, uint8_t);
lean_object* lean_uint8_to_nat(uint8_t);
lean_object* lean_nat_mod(lean_object*, lean_object*);
uint16_t lean_uint16_sub(uint16_t, uint16_t);
uint8_t lean_nat_dec_eq(lean_object*, lean_object*);
uint8_t lean_uint16_dec_le(uint16_t, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_write(lean_object*, uint16_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_write___boxed(lean_object*, lean_object*, lean_object*);
uint8_t lean_uint8_dec_eq(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_updateNZ(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_updateNZ___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorIdx(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorIdx___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim___redArg___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchOperand(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchOperand___boxed(lean_object*, lean_object*);
uint16_t lean_uint16_land(uint16_t, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchAddr(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchAddr___boxed(lean_object*, lean_object*);
uint8_t lean_uint8_sub(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push___boxed(lean_object*, lean_object*);
lean_object* lean_nat_add(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_pull(lean_object*);
uint16_t lean_uint16_shift_right(uint16_t, uint16_t);
uint8_t lean_uint16_to_uint8(uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push16(lean_object*, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push16___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_CPU_pull16(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doBranch(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doBranch___boxed(lean_object*, lean_object*);
static const lean_string_object lp_dasmodel___private_CPU6502_0__doLoad___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "a"};
static const lean_object* lp_dasmodel___private_CPU6502_0__doLoad___closed__0 = (const lean_object*)&lp_dasmodel___private_CPU6502_0__doLoad___closed__0_value;
static const lean_string_object lp_dasmodel___private_CPU6502_0__doLoad___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "x"};
static const lean_object* lp_dasmodel___private_CPU6502_0__doLoad___closed__1 = (const lean_object*)&lp_dasmodel___private_CPU6502_0__doLoad___closed__1_value;
static const lean_string_object lp_dasmodel___private_CPU6502_0__doLoad___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = 0, .m_other = 0, .m_tag = 249}, .m_size = 2, .m_capacity = 2, .m_length = 1, .m_data = "y"};
static const lean_object* lp_dasmodel___private_CPU6502_0__doLoad___closed__2 = (const lean_object*)&lp_dasmodel___private_CPU6502_0__doLoad___closed__2_value;
uint8_t lean_string_dec_eq(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doLoad(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doLoad___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doStore(lean_object*, lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doStore___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doALU(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doALU___boxed(lean_object*, lean_object*, lean_object*);
lean_object* lean_nat_sub(lean_object*, lean_object*);
uint8_t lean_uint8_of_nat(lean_object*);
uint8_t lean_uint8_dec_le(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doCMP(lean_object*, lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doCMP___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doShiftMem(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doShiftMem___boxed(lean_object*, lean_object*, lean_object*);
uint8_t lean_uint8_shift_left(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp___redArg(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp___boxed(lean_object*, lean_object*);
uint8_t lean_uint8_shift_right(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp___redArg(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp___redArg___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp___boxed(lean_object*, lean_object*);
uint8_t lean_uint8_lor(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rolOp(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rolOp___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rorOp(uint8_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rorOp___boxed(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel___private_CPU6502_0__flagsToByte(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__flagsToByte___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__byteToFlags(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__byteToFlags___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_opcodeCycles(uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_opcodeCycles___boxed(lean_object*);
static const lean_closure_object lp_dasmodel_stepRaw___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel___private_CPU6502_0__rorOp___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_stepRaw___closed__0 = (const lean_object*)&lp_dasmodel_stepRaw___closed__0_value;
static const lean_closure_object lp_dasmodel_stepRaw___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel___private_CPU6502_0__rolOp___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_stepRaw___closed__1 = (const lean_object*)&lp_dasmodel_stepRaw___closed__1_value;
static const lean_closure_object lp_dasmodel_stepRaw___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel___private_CPU6502_0__lsrOp___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_stepRaw___closed__2 = (const lean_object*)&lp_dasmodel_stepRaw___closed__2_value;
static const lean_closure_object lp_dasmodel_stepRaw___closed__3_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel___private_CPU6502_0__aslOp___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_stepRaw___closed__3 = (const lean_object*)&lp_dasmodel_stepRaw___closed__3_value;
lean_object* l_UInt8_xor___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_stepRaw___closed__4_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_UInt8_xor___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_stepRaw___closed__4 = (const lean_object*)&lp_dasmodel_stepRaw___closed__4_value;
lean_object* l_UInt8_lor___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_stepRaw___closed__5_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_UInt8_lor___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_stepRaw___closed__5 = (const lean_object*)&lp_dasmodel_stepRaw___closed__5_value;
lean_object* l_UInt8_land___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_stepRaw___closed__6_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)l_UInt8_land___boxed, .m_arity = 2, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_stepRaw___closed__6 = (const lean_object*)&lp_dasmodel_stepRaw___closed__6_value;
uint8_t lean_nat_dec_lt(lean_object*, lean_object*);
uint8_t lean_uint8_xor(uint8_t, uint8_t);
uint8_t lean_nat_dec_le(lean_object*, lean_object*);
uint8_t lean_uint16_dec_eq(uint16_t, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_stepRaw(lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel___private_CPU6502_0__pageCross(uint16_t, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__pageCross___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__0(uint16_t, lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__1(uint16_t, lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__2(uint16_t, lean_object*, uint8_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__2___boxed(lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_step(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execUntilPC(lean_object*, uint16_t, lean_object*);
lean_object* l_List_appendTR___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execUntilPC___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execCall(lean_object*, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_execCall___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execInit(lean_object*, uint16_t, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel_execInit___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execPlay(lean_object*, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_execPlay___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execFrames(lean_object*, uint16_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execFrames___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_PAL__CYCLES__PER__FRAME;
LEAN_EXPORT lean_object* lp_dasmodel_execFrameCycleAccurate(lean_object*, uint16_t);
LEAN_EXPORT lean_object* lp_dasmodel_execFrameCycleAccurate___boxed(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execFramesCycleAccurate(lean_object*, uint16_t, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_execFramesCycleAccurate___boxed(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___redArg(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___redArg___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
lean_object* lean_byte_array_push(lean_object*, uint8_t);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___redArg(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___redArg___boxed(lean_object*, lean_object*, lean_object*);
lean_object* lean_mk_empty_array_with_capacity(lean_object*);
static lean_once_cell_t lp_dasmodel_loadSID___closed__0_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_loadSID___closed__0;
lean_object* lean_byte_array_mk(lean_object*);
static lean_once_cell_t lp_dasmodel_loadSID___closed__1_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_loadSID___closed__1;
static const lean_ctor_object lp_dasmodel_loadSID___closed__2_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*3 + 0, .m_other = 3, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(65536) << 1) | 1)),((lean_object*)(((size_t)(1) << 1) | 1))}};
static const lean_object* lp_dasmodel_loadSID___closed__2 = (const lean_object*)&lp_dasmodel_loadSID___closed__2_value;
static lean_once_cell_t lp_dasmodel_loadSID___closed__3_once = LEAN_ONCE_CELL_INITIALIZER;
static lean_object* lp_dasmodel_loadSID___closed__3;
lean_object* lean_byte_array_size(lean_object*);
lean_object* lean_nat_mul(lean_object*, lean_object*);
uint16_t lean_uint16_of_nat(lean_object*);
lean_object* l_ByteArray_extract(lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_loadSID(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_loadSID___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___boxed(lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*, lean_object*);
static lean_object* _init_lp_dasmodel_instReprFlags_repr___redArg___closed__7(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(9u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprFlags_repr___redArg___closed__12(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(8u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprFlags_repr___redArg___closed__15(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(10u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprFlags_repr___redArg___closed__18(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(11u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprFlags_repr___redArg___closed__21(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(12u);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprFlags_repr___redArg___closed__25(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__0));
x_2 = lean_string_length(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_instReprFlags_repr___redArg___closed__26(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_instReprFlags_repr___redArg___closed__25, &lp_dasmodel_instReprFlags_repr___redArg___closed__25_once, _init_lp_dasmodel_instReprFlags_repr___redArg___closed__25);
x_2 = lean_nat_to_int(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr___redArg(lean_object* x_1) {
_start:
{
uint8_t x_2; uint8_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; uint8_t x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; lean_object* x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; lean_object* x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; lean_object* x_59; lean_object* x_60; lean_object* x_61; lean_object* x_62; lean_object* x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; 
x_2 = lean_ctor_get_uint8(x_1, 0);
x_3 = lean_ctor_get_uint8(x_1, 1);
x_4 = lean_ctor_get_uint8(x_1, 2);
x_5 = lean_ctor_get_uint8(x_1, 3);
x_6 = lean_ctor_get_uint8(x_1, 4);
x_7 = lean_ctor_get_uint8(x_1, 5);
x_8 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__5));
x_9 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__6));
x_10 = lean_obj_once(&lp_dasmodel_instReprFlags_repr___redArg___closed__7, &lp_dasmodel_instReprFlags_repr___redArg___closed__7_once, _init_lp_dasmodel_instReprFlags_repr___redArg___closed__7);
x_11 = l_Bool_repr___redArg(x_2);
x_12 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_12, 0, x_10);
lean_ctor_set(x_12, 1, x_11);
x_13 = 0;
x_14 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_14, 0, x_12);
lean_ctor_set_uint8(x_14, sizeof(void*)*1, x_13);
x_15 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_15, 0, x_9);
lean_ctor_set(x_15, 1, x_14);
x_16 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__9));
x_17 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_17, 0, x_15);
lean_ctor_set(x_17, 1, x_16);
x_18 = lean_box(1);
x_19 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_19, 0, x_17);
lean_ctor_set(x_19, 1, x_18);
x_20 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__11));
x_21 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_21, 0, x_19);
lean_ctor_set(x_21, 1, x_20);
x_22 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_22, 0, x_21);
lean_ctor_set(x_22, 1, x_8);
x_23 = lean_obj_once(&lp_dasmodel_instReprFlags_repr___redArg___closed__12, &lp_dasmodel_instReprFlags_repr___redArg___closed__12_once, _init_lp_dasmodel_instReprFlags_repr___redArg___closed__12);
x_24 = l_Bool_repr___redArg(x_3);
x_25 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_24);
x_26 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_26, 0, x_25);
lean_ctor_set_uint8(x_26, sizeof(void*)*1, x_13);
x_27 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_27, 0, x_22);
lean_ctor_set(x_27, 1, x_26);
x_28 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_28, 0, x_27);
lean_ctor_set(x_28, 1, x_16);
x_29 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_29, 0, x_28);
lean_ctor_set(x_29, 1, x_18);
x_30 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__14));
x_31 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_31, 0, x_29);
lean_ctor_set(x_31, 1, x_30);
x_32 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_32, 0, x_31);
lean_ctor_set(x_32, 1, x_8);
x_33 = lean_obj_once(&lp_dasmodel_instReprFlags_repr___redArg___closed__15, &lp_dasmodel_instReprFlags_repr___redArg___closed__15_once, _init_lp_dasmodel_instReprFlags_repr___redArg___closed__15);
x_34 = l_Bool_repr___redArg(x_4);
x_35 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_35, 0, x_33);
lean_ctor_set(x_35, 1, x_34);
x_36 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_36, 0, x_35);
lean_ctor_set_uint8(x_36, sizeof(void*)*1, x_13);
x_37 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_37, 0, x_32);
lean_ctor_set(x_37, 1, x_36);
x_38 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_38, 0, x_37);
lean_ctor_set(x_38, 1, x_16);
x_39 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_39, 0, x_38);
lean_ctor_set(x_39, 1, x_18);
x_40 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__17));
x_41 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_41, 0, x_39);
lean_ctor_set(x_41, 1, x_40);
x_42 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_42, 0, x_41);
lean_ctor_set(x_42, 1, x_8);
x_43 = lean_obj_once(&lp_dasmodel_instReprFlags_repr___redArg___closed__18, &lp_dasmodel_instReprFlags_repr___redArg___closed__18_once, _init_lp_dasmodel_instReprFlags_repr___redArg___closed__18);
x_44 = l_Bool_repr___redArg(x_5);
x_45 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_45, 0, x_43);
lean_ctor_set(x_45, 1, x_44);
x_46 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_46, 0, x_45);
lean_ctor_set_uint8(x_46, sizeof(void*)*1, x_13);
x_47 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_47, 0, x_42);
lean_ctor_set(x_47, 1, x_46);
x_48 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_48, 0, x_47);
lean_ctor_set(x_48, 1, x_16);
x_49 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_49, 0, x_48);
lean_ctor_set(x_49, 1, x_18);
x_50 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__20));
x_51 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_51, 0, x_49);
lean_ctor_set(x_51, 1, x_50);
x_52 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_52, 0, x_51);
lean_ctor_set(x_52, 1, x_8);
x_53 = lean_obj_once(&lp_dasmodel_instReprFlags_repr___redArg___closed__21, &lp_dasmodel_instReprFlags_repr___redArg___closed__21_once, _init_lp_dasmodel_instReprFlags_repr___redArg___closed__21);
x_54 = l_Bool_repr___redArg(x_6);
x_55 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_55, 0, x_53);
lean_ctor_set(x_55, 1, x_54);
x_56 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_56, 0, x_55);
lean_ctor_set_uint8(x_56, sizeof(void*)*1, x_13);
x_57 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_57, 0, x_52);
lean_ctor_set(x_57, 1, x_56);
x_58 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_58, 0, x_57);
lean_ctor_set(x_58, 1, x_16);
x_59 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_59, 0, x_58);
lean_ctor_set(x_59, 1, x_18);
x_60 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__23));
x_61 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_61, 0, x_59);
lean_ctor_set(x_61, 1, x_60);
x_62 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_62, 0, x_61);
lean_ctor_set(x_62, 1, x_8);
x_63 = l_Bool_repr___redArg(x_7);
x_64 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_64, 0, x_53);
lean_ctor_set(x_64, 1, x_63);
x_65 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_65, 0, x_64);
lean_ctor_set_uint8(x_65, sizeof(void*)*1, x_13);
x_66 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_66, 0, x_62);
lean_ctor_set(x_66, 1, x_65);
x_67 = lean_obj_once(&lp_dasmodel_instReprFlags_repr___redArg___closed__26, &lp_dasmodel_instReprFlags_repr___redArg___closed__26_once, _init_lp_dasmodel_instReprFlags_repr___redArg___closed__26);
x_68 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__27));
x_69 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_69, 0, x_68);
lean_ctor_set(x_69, 1, x_66);
x_70 = ((lean_object*)(lp_dasmodel_instReprFlags_repr___redArg___closed__28));
x_71 = lean_alloc_ctor(5, 2, 0);
lean_ctor_set(x_71, 0, x_69);
lean_ctor_set(x_71, 1, x_70);
x_72 = lean_alloc_ctor(4, 2, 0);
lean_ctor_set(x_72, 0, x_67);
lean_ctor_set(x_72, 1, x_71);
x_73 = lean_alloc_ctor(6, 1, 1);
lean_ctor_set(x_73, 0, x_72);
lean_ctor_set_uint8(x_73, sizeof(void*)*1, x_13);
return x_73;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr___redArg___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_instReprFlags_repr___redArg(x_1);
lean_dec_ref(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_instReprFlags_repr___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instReprFlags_repr___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_instReprFlags_repr(x_1, x_2);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT uint8_t lp_dasmodel_instBEqFlags_beq(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; uint8_t x_9; uint8_t x_10; uint8_t x_11; uint8_t x_12; uint8_t x_13; uint8_t x_14; uint8_t x_15; uint8_t x_17; uint8_t x_19; uint8_t x_21; uint8_t x_23; 
x_3 = lean_ctor_get_uint8(x_1, 0);
x_4 = lean_ctor_get_uint8(x_1, 1);
x_5 = lean_ctor_get_uint8(x_1, 2);
x_6 = lean_ctor_get_uint8(x_1, 3);
x_7 = lean_ctor_get_uint8(x_1, 4);
x_8 = lean_ctor_get_uint8(x_1, 5);
x_9 = lean_ctor_get_uint8(x_2, 0);
x_10 = lean_ctor_get_uint8(x_2, 1);
x_11 = lean_ctor_get_uint8(x_2, 2);
x_12 = lean_ctor_get_uint8(x_2, 3);
x_13 = lean_ctor_get_uint8(x_2, 4);
x_14 = lean_ctor_get_uint8(x_2, 5);
if (x_3 == 0)
{
if (x_9 == 0)
{
uint8_t x_25; 
x_25 = 1;
x_23 = x_25;
goto block_24;
}
else
{
return x_3;
}
}
else
{
if (x_9 == 0)
{
return x_9;
}
else
{
x_23 = x_9;
goto block_24;
}
}
block_16:
{
if (x_8 == 0)
{
if (x_14 == 0)
{
return x_15;
}
else
{
return x_8;
}
}
else
{
return x_14;
}
}
block_18:
{
if (x_7 == 0)
{
if (x_13 == 0)
{
x_15 = x_17;
goto block_16;
}
else
{
return x_7;
}
}
else
{
if (x_13 == 0)
{
return x_13;
}
else
{
x_15 = x_13;
goto block_16;
}
}
}
block_20:
{
if (x_6 == 0)
{
if (x_12 == 0)
{
x_17 = x_19;
goto block_18;
}
else
{
return x_6;
}
}
else
{
if (x_12 == 0)
{
return x_12;
}
else
{
x_17 = x_12;
goto block_18;
}
}
}
block_22:
{
if (x_5 == 0)
{
if (x_11 == 0)
{
x_19 = x_21;
goto block_20;
}
else
{
return x_5;
}
}
else
{
if (x_11 == 0)
{
return x_11;
}
else
{
x_19 = x_11;
goto block_20;
}
}
}
block_24:
{
if (x_4 == 0)
{
if (x_10 == 0)
{
x_21 = x_23;
goto block_22;
}
else
{
return x_4;
}
}
else
{
if (x_10 == 0)
{
return x_10;
}
else
{
x_21 = x_10;
goto block_22;
}
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_instBEqFlags_beq___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lp_dasmodel_instBEqFlags_beq(x_1, x_2);
lean_dec_ref(x_2);
lean_dec_ref(x_1);
x_4 = lean_box(x_3);
return x_4;
}
}
LEAN_EXPORT uint8_t lp_dasmodel_CPU_read(lean_object* x_1, uint16_t x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; uint8_t x_5; 
x_3 = lean_ctor_get(x_1, 1);
x_4 = lean_uint16_to_nat(x_2);
x_5 = lean_byte_array_get(x_3, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_read___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; uint8_t x_4; lean_object* x_5; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_CPU_read(x_1, x_3);
lean_dec_ref(x_1);
x_5 = lean_box(x_4);
return x_5;
}
}
LEAN_EXPORT uint16_t lp_dasmodel_CPU_read16(lean_object* x_1, uint16_t x_2) {
_start:
{
uint8_t x_3; uint16_t x_4; uint16_t x_5; uint8_t x_6; uint16_t x_7; uint16_t x_8; uint16_t x_9; uint16_t x_10; uint16_t x_11; 
x_3 = lp_dasmodel_CPU_read(x_1, x_2);
x_4 = 1;
x_5 = lean_uint16_add(x_2, x_4);
x_6 = lp_dasmodel_CPU_read(x_1, x_5);
x_7 = lean_uint8_to_uint16(x_3);
x_8 = lean_uint8_to_uint16(x_6);
x_9 = 8;
x_10 = lean_uint16_shift_left(x_8, x_9);
x_11 = lean_uint16_lor(x_7, x_10);
return x_11;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_read16___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; uint16_t x_4; lean_object* x_5; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_CPU_read16(x_1, x_3);
lean_dec_ref(x_1);
x_5 = lean_box(x_4);
return x_5;
}
}
LEAN_EXPORT uint16_t lp_dasmodel_CPU_readZP16(lean_object* x_1, uint8_t x_2) {
_start:
{
uint16_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; uint16_t x_9; uint8_t x_10; uint16_t x_11; uint16_t x_12; uint16_t x_13; uint16_t x_14; uint16_t x_15; 
x_3 = lean_uint8_to_uint16(x_2);
x_4 = lp_dasmodel_CPU_read(x_1, x_3);
x_5 = 1;
x_6 = lean_uint8_add(x_2, x_5);
x_7 = 255;
x_8 = lean_uint8_land(x_6, x_7);
x_9 = lean_uint8_to_uint16(x_8);
x_10 = lp_dasmodel_CPU_read(x_1, x_9);
x_11 = lean_uint8_to_uint16(x_4);
x_12 = lean_uint8_to_uint16(x_10);
x_13 = 8;
x_14 = lean_uint16_shift_left(x_12, x_13);
x_15 = lean_uint16_lor(x_11, x_14);
return x_15;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_readZP16___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint16_t x_4; lean_object* x_5; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_CPU_readZP16(x_1, x_3);
lean_dec_ref(x_1);
x_5 = lean_box(x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_write(lean_object* x_1, uint16_t x_2, uint8_t x_3) {
_start:
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; lean_object* x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; uint16_t x_19; uint8_t x_20; uint8_t x_99; 
x_5 = lean_ctor_get(x_1, 1);
x_6 = lean_ctor_get(x_1, 2);
x_7 = lean_uint16_to_nat(x_2);
x_8 = lean_byte_array_set(x_5, x_7, x_3);
lean_inc(x_6);
lean_ctor_set(x_1, 1, x_8);
x_19 = 54272;
x_99 = lean_uint16_dec_le(x_19, x_2);
if (x_99 == 0)
{
x_20 = x_99;
goto block_98;
}
else
{
uint16_t x_100; uint8_t x_101; 
x_100 = 54300;
x_101 = lean_uint16_dec_le(x_2, x_100);
x_20 = x_101;
goto block_98;
}
block_18:
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_10 = lean_unsigned_to_nat(256u);
x_11 = lean_uint8_to_nat(x_3);
x_12 = lean_nat_mod(x_11, x_10);
x_13 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_13, 0, x_9);
lean_ctor_set(x_13, 1, x_12);
x_14 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_14, 0, x_6);
lean_ctor_set(x_14, 1, x_13);
x_15 = lean_box(0);
x_16 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_16, 0, x_14);
lean_ctor_set(x_16, 1, x_15);
x_17 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_17, 0, x_1);
lean_ctor_set(x_17, 1, x_16);
return x_17;
}
block_98:
{
if (x_20 == 0)
{
lean_object* x_21; lean_object* x_22; 
lean_dec(x_6);
x_21 = lean_box(0);
x_22 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_22, 0, x_1);
lean_ctor_set(x_22, 1, x_21);
return x_22;
}
else
{
uint16_t x_23; lean_object* x_24; lean_object* x_25; uint8_t x_26; 
x_23 = lean_uint16_sub(x_2, x_19);
x_24 = lean_uint16_to_nat(x_23);
x_25 = lean_unsigned_to_nat(0u);
x_26 = lean_nat_dec_eq(x_24, x_25);
if (x_26 == 0)
{
lean_object* x_27; uint8_t x_28; 
x_27 = lean_unsigned_to_nat(1u);
x_28 = lean_nat_dec_eq(x_24, x_27);
if (x_28 == 0)
{
lean_object* x_29; uint8_t x_30; 
x_29 = lean_unsigned_to_nat(2u);
x_30 = lean_nat_dec_eq(x_24, x_29);
if (x_30 == 0)
{
lean_object* x_31; uint8_t x_32; 
x_31 = lean_unsigned_to_nat(3u);
x_32 = lean_nat_dec_eq(x_24, x_31);
if (x_32 == 0)
{
lean_object* x_33; uint8_t x_34; 
x_33 = lean_unsigned_to_nat(4u);
x_34 = lean_nat_dec_eq(x_24, x_33);
if (x_34 == 0)
{
lean_object* x_35; uint8_t x_36; 
x_35 = lean_unsigned_to_nat(5u);
x_36 = lean_nat_dec_eq(x_24, x_35);
if (x_36 == 0)
{
lean_object* x_37; uint8_t x_38; 
x_37 = lean_unsigned_to_nat(6u);
x_38 = lean_nat_dec_eq(x_24, x_37);
if (x_38 == 0)
{
lean_object* x_39; uint8_t x_40; 
x_39 = lean_unsigned_to_nat(7u);
x_40 = lean_nat_dec_eq(x_24, x_39);
if (x_40 == 0)
{
lean_object* x_41; uint8_t x_42; 
x_41 = lean_unsigned_to_nat(8u);
x_42 = lean_nat_dec_eq(x_24, x_41);
if (x_42 == 0)
{
lean_object* x_43; uint8_t x_44; 
x_43 = lean_unsigned_to_nat(9u);
x_44 = lean_nat_dec_eq(x_24, x_43);
if (x_44 == 0)
{
lean_object* x_45; uint8_t x_46; 
x_45 = lean_unsigned_to_nat(10u);
x_46 = lean_nat_dec_eq(x_24, x_45);
if (x_46 == 0)
{
lean_object* x_47; uint8_t x_48; 
x_47 = lean_unsigned_to_nat(11u);
x_48 = lean_nat_dec_eq(x_24, x_47);
if (x_48 == 0)
{
lean_object* x_49; uint8_t x_50; 
x_49 = lean_unsigned_to_nat(12u);
x_50 = lean_nat_dec_eq(x_24, x_49);
if (x_50 == 0)
{
lean_object* x_51; uint8_t x_52; 
x_51 = lean_unsigned_to_nat(13u);
x_52 = lean_nat_dec_eq(x_24, x_51);
if (x_52 == 0)
{
lean_object* x_53; uint8_t x_54; 
x_53 = lean_unsigned_to_nat(14u);
x_54 = lean_nat_dec_eq(x_24, x_53);
if (x_54 == 0)
{
lean_object* x_55; uint8_t x_56; 
x_55 = lean_unsigned_to_nat(15u);
x_56 = lean_nat_dec_eq(x_24, x_55);
if (x_56 == 0)
{
lean_object* x_57; uint8_t x_58; 
x_57 = lean_unsigned_to_nat(16u);
x_58 = lean_nat_dec_eq(x_24, x_57);
if (x_58 == 0)
{
lean_object* x_59; uint8_t x_60; 
x_59 = lean_unsigned_to_nat(17u);
x_60 = lean_nat_dec_eq(x_24, x_59);
if (x_60 == 0)
{
lean_object* x_61; uint8_t x_62; 
x_61 = lean_unsigned_to_nat(18u);
x_62 = lean_nat_dec_eq(x_24, x_61);
if (x_62 == 0)
{
lean_object* x_63; uint8_t x_64; 
x_63 = lean_unsigned_to_nat(19u);
x_64 = lean_nat_dec_eq(x_24, x_63);
if (x_64 == 0)
{
lean_object* x_65; uint8_t x_66; 
x_65 = lean_unsigned_to_nat(20u);
x_66 = lean_nat_dec_eq(x_24, x_65);
if (x_66 == 0)
{
lean_object* x_67; uint8_t x_68; 
x_67 = lean_unsigned_to_nat(21u);
x_68 = lean_nat_dec_eq(x_24, x_67);
if (x_68 == 0)
{
lean_object* x_69; uint8_t x_70; 
x_69 = lean_unsigned_to_nat(22u);
x_70 = lean_nat_dec_eq(x_24, x_69);
if (x_70 == 0)
{
lean_object* x_71; uint8_t x_72; 
x_71 = lean_unsigned_to_nat(23u);
x_72 = lean_nat_dec_eq(x_24, x_71);
if (x_72 == 0)
{
lean_object* x_73; 
x_73 = lean_box(10);
x_9 = x_73;
goto block_18;
}
else
{
lean_object* x_74; 
x_74 = lean_box(9);
x_9 = x_74;
goto block_18;
}
}
else
{
lean_object* x_75; 
x_75 = lean_box(8);
x_9 = x_75;
goto block_18;
}
}
else
{
lean_object* x_76; 
x_76 = lean_box(7);
x_9 = x_76;
goto block_18;
}
}
else
{
lean_object* x_77; 
x_77 = ((lean_object*)(lp_dasmodel_CPU_write___closed__0));
x_9 = x_77;
goto block_18;
}
}
else
{
lean_object* x_78; 
x_78 = ((lean_object*)(lp_dasmodel_CPU_write___closed__1));
x_9 = x_78;
goto block_18;
}
}
else
{
lean_object* x_79; 
x_79 = ((lean_object*)(lp_dasmodel_CPU_write___closed__2));
x_9 = x_79;
goto block_18;
}
}
else
{
lean_object* x_80; 
x_80 = ((lean_object*)(lp_dasmodel_CPU_write___closed__3));
x_9 = x_80;
goto block_18;
}
}
else
{
lean_object* x_81; 
x_81 = ((lean_object*)(lp_dasmodel_CPU_write___closed__4));
x_9 = x_81;
goto block_18;
}
}
else
{
lean_object* x_82; 
x_82 = ((lean_object*)(lp_dasmodel_CPU_write___closed__5));
x_9 = x_82;
goto block_18;
}
}
else
{
lean_object* x_83; 
x_83 = ((lean_object*)(lp_dasmodel_CPU_write___closed__6));
x_9 = x_83;
goto block_18;
}
}
else
{
lean_object* x_84; 
x_84 = ((lean_object*)(lp_dasmodel_CPU_write___closed__7));
x_9 = x_84;
goto block_18;
}
}
else
{
lean_object* x_85; 
x_85 = ((lean_object*)(lp_dasmodel_CPU_write___closed__8));
x_9 = x_85;
goto block_18;
}
}
else
{
lean_object* x_86; 
x_86 = ((lean_object*)(lp_dasmodel_CPU_write___closed__9));
x_9 = x_86;
goto block_18;
}
}
else
{
lean_object* x_87; 
x_87 = ((lean_object*)(lp_dasmodel_CPU_write___closed__10));
x_9 = x_87;
goto block_18;
}
}
else
{
lean_object* x_88; 
x_88 = ((lean_object*)(lp_dasmodel_CPU_write___closed__11));
x_9 = x_88;
goto block_18;
}
}
else
{
lean_object* x_89; 
x_89 = ((lean_object*)(lp_dasmodel_CPU_write___closed__12));
x_9 = x_89;
goto block_18;
}
}
else
{
lean_object* x_90; 
x_90 = ((lean_object*)(lp_dasmodel_CPU_write___closed__13));
x_9 = x_90;
goto block_18;
}
}
else
{
lean_object* x_91; 
x_91 = ((lean_object*)(lp_dasmodel_CPU_write___closed__14));
x_9 = x_91;
goto block_18;
}
}
else
{
lean_object* x_92; 
x_92 = ((lean_object*)(lp_dasmodel_CPU_write___closed__15));
x_9 = x_92;
goto block_18;
}
}
else
{
lean_object* x_93; 
x_93 = ((lean_object*)(lp_dasmodel_CPU_write___closed__16));
x_9 = x_93;
goto block_18;
}
}
else
{
lean_object* x_94; 
x_94 = ((lean_object*)(lp_dasmodel_CPU_write___closed__17));
x_9 = x_94;
goto block_18;
}
}
else
{
lean_object* x_95; 
x_95 = ((lean_object*)(lp_dasmodel_CPU_write___closed__18));
x_9 = x_95;
goto block_18;
}
}
else
{
lean_object* x_96; 
x_96 = ((lean_object*)(lp_dasmodel_CPU_write___closed__19));
x_9 = x_96;
goto block_18;
}
}
else
{
lean_object* x_97; 
x_97 = ((lean_object*)(lp_dasmodel_CPU_write___closed__20));
x_9 = x_97;
goto block_18;
}
}
}
}
else
{
uint8_t x_102; uint8_t x_103; uint8_t x_104; uint8_t x_105; uint16_t x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; lean_object* x_110; lean_object* x_111; lean_object* x_112; lean_object* x_113; uint16_t x_123; uint8_t x_124; uint8_t x_203; 
x_102 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_103 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_104 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_105 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_106 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_107 = lean_ctor_get(x_1, 0);
x_108 = lean_ctor_get(x_1, 1);
x_109 = lean_ctor_get(x_1, 2);
lean_inc(x_109);
lean_inc(x_108);
lean_inc(x_107);
lean_dec(x_1);
x_110 = lean_uint16_to_nat(x_2);
x_111 = lean_byte_array_set(x_108, x_110, x_3);
lean_inc(x_109);
x_112 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_112, 0, x_107);
lean_ctor_set(x_112, 1, x_111);
lean_ctor_set(x_112, 2, x_109);
lean_ctor_set_uint8(x_112, sizeof(void*)*3 + 2, x_102);
lean_ctor_set_uint8(x_112, sizeof(void*)*3 + 3, x_103);
lean_ctor_set_uint8(x_112, sizeof(void*)*3 + 4, x_104);
lean_ctor_set_uint8(x_112, sizeof(void*)*3 + 5, x_105);
lean_ctor_set_uint16(x_112, sizeof(void*)*3, x_106);
x_123 = 54272;
x_203 = lean_uint16_dec_le(x_123, x_2);
if (x_203 == 0)
{
x_124 = x_203;
goto block_202;
}
else
{
uint16_t x_204; uint8_t x_205; 
x_204 = 54300;
x_205 = lean_uint16_dec_le(x_2, x_204);
x_124 = x_205;
goto block_202;
}
block_122:
{
lean_object* x_114; lean_object* x_115; lean_object* x_116; lean_object* x_117; lean_object* x_118; lean_object* x_119; lean_object* x_120; lean_object* x_121; 
x_114 = lean_unsigned_to_nat(256u);
x_115 = lean_uint8_to_nat(x_3);
x_116 = lean_nat_mod(x_115, x_114);
x_117 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_117, 0, x_113);
lean_ctor_set(x_117, 1, x_116);
x_118 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_118, 0, x_109);
lean_ctor_set(x_118, 1, x_117);
x_119 = lean_box(0);
x_120 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_120, 0, x_118);
lean_ctor_set(x_120, 1, x_119);
x_121 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_121, 0, x_112);
lean_ctor_set(x_121, 1, x_120);
return x_121;
}
block_202:
{
if (x_124 == 0)
{
lean_object* x_125; lean_object* x_126; 
lean_dec(x_109);
x_125 = lean_box(0);
x_126 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_126, 0, x_112);
lean_ctor_set(x_126, 1, x_125);
return x_126;
}
else
{
uint16_t x_127; lean_object* x_128; lean_object* x_129; uint8_t x_130; 
x_127 = lean_uint16_sub(x_2, x_123);
x_128 = lean_uint16_to_nat(x_127);
x_129 = lean_unsigned_to_nat(0u);
x_130 = lean_nat_dec_eq(x_128, x_129);
if (x_130 == 0)
{
lean_object* x_131; uint8_t x_132; 
x_131 = lean_unsigned_to_nat(1u);
x_132 = lean_nat_dec_eq(x_128, x_131);
if (x_132 == 0)
{
lean_object* x_133; uint8_t x_134; 
x_133 = lean_unsigned_to_nat(2u);
x_134 = lean_nat_dec_eq(x_128, x_133);
if (x_134 == 0)
{
lean_object* x_135; uint8_t x_136; 
x_135 = lean_unsigned_to_nat(3u);
x_136 = lean_nat_dec_eq(x_128, x_135);
if (x_136 == 0)
{
lean_object* x_137; uint8_t x_138; 
x_137 = lean_unsigned_to_nat(4u);
x_138 = lean_nat_dec_eq(x_128, x_137);
if (x_138 == 0)
{
lean_object* x_139; uint8_t x_140; 
x_139 = lean_unsigned_to_nat(5u);
x_140 = lean_nat_dec_eq(x_128, x_139);
if (x_140 == 0)
{
lean_object* x_141; uint8_t x_142; 
x_141 = lean_unsigned_to_nat(6u);
x_142 = lean_nat_dec_eq(x_128, x_141);
if (x_142 == 0)
{
lean_object* x_143; uint8_t x_144; 
x_143 = lean_unsigned_to_nat(7u);
x_144 = lean_nat_dec_eq(x_128, x_143);
if (x_144 == 0)
{
lean_object* x_145; uint8_t x_146; 
x_145 = lean_unsigned_to_nat(8u);
x_146 = lean_nat_dec_eq(x_128, x_145);
if (x_146 == 0)
{
lean_object* x_147; uint8_t x_148; 
x_147 = lean_unsigned_to_nat(9u);
x_148 = lean_nat_dec_eq(x_128, x_147);
if (x_148 == 0)
{
lean_object* x_149; uint8_t x_150; 
x_149 = lean_unsigned_to_nat(10u);
x_150 = lean_nat_dec_eq(x_128, x_149);
if (x_150 == 0)
{
lean_object* x_151; uint8_t x_152; 
x_151 = lean_unsigned_to_nat(11u);
x_152 = lean_nat_dec_eq(x_128, x_151);
if (x_152 == 0)
{
lean_object* x_153; uint8_t x_154; 
x_153 = lean_unsigned_to_nat(12u);
x_154 = lean_nat_dec_eq(x_128, x_153);
if (x_154 == 0)
{
lean_object* x_155; uint8_t x_156; 
x_155 = lean_unsigned_to_nat(13u);
x_156 = lean_nat_dec_eq(x_128, x_155);
if (x_156 == 0)
{
lean_object* x_157; uint8_t x_158; 
x_157 = lean_unsigned_to_nat(14u);
x_158 = lean_nat_dec_eq(x_128, x_157);
if (x_158 == 0)
{
lean_object* x_159; uint8_t x_160; 
x_159 = lean_unsigned_to_nat(15u);
x_160 = lean_nat_dec_eq(x_128, x_159);
if (x_160 == 0)
{
lean_object* x_161; uint8_t x_162; 
x_161 = lean_unsigned_to_nat(16u);
x_162 = lean_nat_dec_eq(x_128, x_161);
if (x_162 == 0)
{
lean_object* x_163; uint8_t x_164; 
x_163 = lean_unsigned_to_nat(17u);
x_164 = lean_nat_dec_eq(x_128, x_163);
if (x_164 == 0)
{
lean_object* x_165; uint8_t x_166; 
x_165 = lean_unsigned_to_nat(18u);
x_166 = lean_nat_dec_eq(x_128, x_165);
if (x_166 == 0)
{
lean_object* x_167; uint8_t x_168; 
x_167 = lean_unsigned_to_nat(19u);
x_168 = lean_nat_dec_eq(x_128, x_167);
if (x_168 == 0)
{
lean_object* x_169; uint8_t x_170; 
x_169 = lean_unsigned_to_nat(20u);
x_170 = lean_nat_dec_eq(x_128, x_169);
if (x_170 == 0)
{
lean_object* x_171; uint8_t x_172; 
x_171 = lean_unsigned_to_nat(21u);
x_172 = lean_nat_dec_eq(x_128, x_171);
if (x_172 == 0)
{
lean_object* x_173; uint8_t x_174; 
x_173 = lean_unsigned_to_nat(22u);
x_174 = lean_nat_dec_eq(x_128, x_173);
if (x_174 == 0)
{
lean_object* x_175; uint8_t x_176; 
x_175 = lean_unsigned_to_nat(23u);
x_176 = lean_nat_dec_eq(x_128, x_175);
if (x_176 == 0)
{
lean_object* x_177; 
x_177 = lean_box(10);
x_113 = x_177;
goto block_122;
}
else
{
lean_object* x_178; 
x_178 = lean_box(9);
x_113 = x_178;
goto block_122;
}
}
else
{
lean_object* x_179; 
x_179 = lean_box(8);
x_113 = x_179;
goto block_122;
}
}
else
{
lean_object* x_180; 
x_180 = lean_box(7);
x_113 = x_180;
goto block_122;
}
}
else
{
lean_object* x_181; 
x_181 = ((lean_object*)(lp_dasmodel_CPU_write___closed__0));
x_113 = x_181;
goto block_122;
}
}
else
{
lean_object* x_182; 
x_182 = ((lean_object*)(lp_dasmodel_CPU_write___closed__1));
x_113 = x_182;
goto block_122;
}
}
else
{
lean_object* x_183; 
x_183 = ((lean_object*)(lp_dasmodel_CPU_write___closed__2));
x_113 = x_183;
goto block_122;
}
}
else
{
lean_object* x_184; 
x_184 = ((lean_object*)(lp_dasmodel_CPU_write___closed__3));
x_113 = x_184;
goto block_122;
}
}
else
{
lean_object* x_185; 
x_185 = ((lean_object*)(lp_dasmodel_CPU_write___closed__4));
x_113 = x_185;
goto block_122;
}
}
else
{
lean_object* x_186; 
x_186 = ((lean_object*)(lp_dasmodel_CPU_write___closed__5));
x_113 = x_186;
goto block_122;
}
}
else
{
lean_object* x_187; 
x_187 = ((lean_object*)(lp_dasmodel_CPU_write___closed__6));
x_113 = x_187;
goto block_122;
}
}
else
{
lean_object* x_188; 
x_188 = ((lean_object*)(lp_dasmodel_CPU_write___closed__7));
x_113 = x_188;
goto block_122;
}
}
else
{
lean_object* x_189; 
x_189 = ((lean_object*)(lp_dasmodel_CPU_write___closed__8));
x_113 = x_189;
goto block_122;
}
}
else
{
lean_object* x_190; 
x_190 = ((lean_object*)(lp_dasmodel_CPU_write___closed__9));
x_113 = x_190;
goto block_122;
}
}
else
{
lean_object* x_191; 
x_191 = ((lean_object*)(lp_dasmodel_CPU_write___closed__10));
x_113 = x_191;
goto block_122;
}
}
else
{
lean_object* x_192; 
x_192 = ((lean_object*)(lp_dasmodel_CPU_write___closed__11));
x_113 = x_192;
goto block_122;
}
}
else
{
lean_object* x_193; 
x_193 = ((lean_object*)(lp_dasmodel_CPU_write___closed__12));
x_113 = x_193;
goto block_122;
}
}
else
{
lean_object* x_194; 
x_194 = ((lean_object*)(lp_dasmodel_CPU_write___closed__13));
x_113 = x_194;
goto block_122;
}
}
else
{
lean_object* x_195; 
x_195 = ((lean_object*)(lp_dasmodel_CPU_write___closed__14));
x_113 = x_195;
goto block_122;
}
}
else
{
lean_object* x_196; 
x_196 = ((lean_object*)(lp_dasmodel_CPU_write___closed__15));
x_113 = x_196;
goto block_122;
}
}
else
{
lean_object* x_197; 
x_197 = ((lean_object*)(lp_dasmodel_CPU_write___closed__16));
x_113 = x_197;
goto block_122;
}
}
else
{
lean_object* x_198; 
x_198 = ((lean_object*)(lp_dasmodel_CPU_write___closed__17));
x_113 = x_198;
goto block_122;
}
}
else
{
lean_object* x_199; 
x_199 = ((lean_object*)(lp_dasmodel_CPU_write___closed__18));
x_113 = x_199;
goto block_122;
}
}
else
{
lean_object* x_200; 
x_200 = ((lean_object*)(lp_dasmodel_CPU_write___closed__19));
x_113 = x_200;
goto block_122;
}
}
else
{
lean_object* x_201; 
x_201 = ((lean_object*)(lp_dasmodel_CPU_write___closed__20));
x_113 = x_201;
goto block_122;
}
}
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_write___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint16_t x_4; uint8_t x_5; lean_object* x_6; 
x_4 = lean_unbox(x_2);
x_5 = lean_unbox(x_3);
x_6 = lp_dasmodel_CPU_write(x_1, x_4, x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_updateNZ(lean_object* x_1, uint8_t x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; 
x_4 = 0;
x_5 = lean_uint8_dec_eq(x_2, x_4);
x_6 = 128;
x_7 = lean_uint8_land(x_2, x_6);
x_8 = lean_uint8_dec_eq(x_7, x_4);
if (x_8 == 0)
{
uint8_t x_9; 
x_9 = 1;
lean_ctor_set_uint8(x_1, 1, x_5);
lean_ctor_set_uint8(x_1, 5, x_9);
return x_1;
}
else
{
uint8_t x_10; 
x_10 = 0;
lean_ctor_set_uint8(x_1, 1, x_5);
lean_ctor_set_uint8(x_1, 5, x_10);
return x_1;
}
}
else
{
uint8_t x_11; uint8_t x_12; uint8_t x_13; uint8_t x_14; uint8_t x_15; uint8_t x_16; uint8_t x_17; uint8_t x_18; uint8_t x_19; 
x_11 = lean_ctor_get_uint8(x_1, 0);
x_12 = lean_ctor_get_uint8(x_1, 2);
x_13 = lean_ctor_get_uint8(x_1, 3);
x_14 = lean_ctor_get_uint8(x_1, 4);
lean_dec(x_1);
x_15 = 0;
x_16 = lean_uint8_dec_eq(x_2, x_15);
x_17 = 128;
x_18 = lean_uint8_land(x_2, x_17);
x_19 = lean_uint8_dec_eq(x_18, x_15);
if (x_19 == 0)
{
uint8_t x_20; lean_object* x_21; 
x_20 = 1;
x_21 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_21, 0, x_11);
lean_ctor_set_uint8(x_21, 1, x_16);
lean_ctor_set_uint8(x_21, 2, x_12);
lean_ctor_set_uint8(x_21, 3, x_13);
lean_ctor_set_uint8(x_21, 4, x_14);
lean_ctor_set_uint8(x_21, 5, x_20);
return x_21;
}
else
{
uint8_t x_22; lean_object* x_23; 
x_22 = 0;
x_23 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_23, 0, x_11);
lean_ctor_set_uint8(x_23, 1, x_16);
lean_ctor_set_uint8(x_23, 2, x_12);
lean_ctor_set_uint8(x_23, 3, x_13);
lean_ctor_set_uint8(x_23, 4, x_14);
lean_ctor_set_uint8(x_23, 5, x_22);
return x_23;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_updateNZ___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_updateNZ(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorIdx(lean_object* x_1) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
lean_object* x_2; 
x_2 = lean_unsigned_to_nat(0u);
return x_2;
}
else
{
lean_object* x_3; 
x_3 = lean_unsigned_to_nat(1u);
return x_3;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorIdx___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_Operand_ctorIdx(x_1);
lean_dec_ref(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
if (lean_obj_tag(x_1) == 0)
{
uint8_t x_3; lean_object* x_4; lean_object* x_5; 
x_3 = lean_ctor_get_uint8(x_1, 0);
x_4 = lean_box(x_3);
x_5 = lean_apply_1(x_2, x_4);
return x_5;
}
else
{
uint16_t x_6; lean_object* x_7; lean_object* x_8; 
x_6 = lean_ctor_get_uint16(x_1, 0);
x_7 = lean_box(x_6);
x_8 = lean_apply_1(x_2, x_7);
return x_8;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_Operand_ctorElim___redArg(x_1, x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_Operand_ctorElim___redArg(x_3, x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_ctorElim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel_Operand_ctorElim(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_3);
lean_dec(x_2);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_Operand_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_Operand_value_elim___redArg(x_1, x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_Operand_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_value_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_Operand_value_elim(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim___redArg(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_Operand_ctorElim___redArg(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim___redArg___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_Operand_addr_elim___redArg(x_1, x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_Operand_ctorElim___redArg(x_2, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_Operand_addr_elim___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
lean_object* x_5; 
x_5 = lp_dasmodel_Operand_addr_elim(x_1, x_2, x_3, x_4);
lean_dec_ref(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchOperand(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; uint16_t x_5; uint16_t x_6; uint16_t x_7; lean_object* x_8; uint8_t x_9; 
x_3 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_4 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_5 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_6 = 1;
x_7 = lean_uint16_add(x_5, x_6);
x_8 = lean_unsigned_to_nat(0u);
x_9 = lean_nat_dec_eq(x_2, x_8);
if (x_9 == 0)
{
lean_object* x_10; uint8_t x_11; 
x_10 = lean_unsigned_to_nat(1u);
x_11 = lean_nat_dec_eq(x_2, x_10);
if (x_11 == 0)
{
lean_object* x_12; uint8_t x_13; 
x_12 = lean_unsigned_to_nat(2u);
x_13 = lean_nat_dec_eq(x_2, x_12);
if (x_13 == 0)
{
lean_object* x_14; uint8_t x_15; 
x_14 = lean_unsigned_to_nat(3u);
x_15 = lean_nat_dec_eq(x_2, x_14);
if (x_15 == 0)
{
lean_object* x_16; uint8_t x_17; 
x_16 = lean_unsigned_to_nat(4u);
x_17 = lean_nat_dec_eq(x_2, x_16);
if (x_17 == 0)
{
lean_object* x_18; uint8_t x_19; 
x_18 = lean_unsigned_to_nat(5u);
x_19 = lean_nat_dec_eq(x_2, x_18);
if (x_19 == 0)
{
lean_object* x_20; uint8_t x_21; 
x_20 = lean_unsigned_to_nat(6u);
x_21 = lean_nat_dec_eq(x_2, x_20);
if (x_21 == 0)
{
lean_object* x_22; uint8_t x_23; 
x_22 = lean_unsigned_to_nat(7u);
x_23 = lean_nat_dec_eq(x_2, x_22);
if (x_23 == 0)
{
lean_object* x_24; uint8_t x_25; 
x_24 = lean_unsigned_to_nat(8u);
x_25 = lean_nat_dec_eq(x_2, x_24);
if (x_25 == 0)
{
uint8_t x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; 
x_26 = 0;
x_27 = lean_box(x_26);
x_28 = lean_box(x_7);
x_29 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_29, 0, x_27);
lean_ctor_set(x_29, 1, x_28);
return x_29;
}
else
{
uint8_t x_30; uint16_t x_31; uint16_t x_32; uint16_t x_33; uint8_t x_34; uint16_t x_35; uint16_t x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; 
x_30 = lp_dasmodel_CPU_read(x_1, x_7);
x_31 = lp_dasmodel_CPU_readZP16(x_1, x_30);
x_32 = lean_uint8_to_uint16(x_4);
x_33 = lean_uint16_add(x_31, x_32);
x_34 = lp_dasmodel_CPU_read(x_1, x_33);
x_35 = 2;
x_36 = lean_uint16_add(x_5, x_35);
x_37 = lean_box(x_34);
x_38 = lean_box(x_36);
x_39 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_39, 0, x_37);
lean_ctor_set(x_39, 1, x_38);
return x_39;
}
}
else
{
uint8_t x_40; uint8_t x_41; uint16_t x_42; uint8_t x_43; uint16_t x_44; uint16_t x_45; lean_object* x_46; lean_object* x_47; lean_object* x_48; 
x_40 = lp_dasmodel_CPU_read(x_1, x_7);
x_41 = lean_uint8_add(x_40, x_3);
x_42 = lp_dasmodel_CPU_readZP16(x_1, x_41);
x_43 = lp_dasmodel_CPU_read(x_1, x_42);
x_44 = 2;
x_45 = lean_uint16_add(x_5, x_44);
x_46 = lean_box(x_43);
x_47 = lean_box(x_45);
x_48 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_48, 0, x_46);
lean_ctor_set(x_48, 1, x_47);
return x_48;
}
}
else
{
uint16_t x_49; uint16_t x_50; uint16_t x_51; uint8_t x_52; uint16_t x_53; uint16_t x_54; lean_object* x_55; lean_object* x_56; lean_object* x_57; 
x_49 = lp_dasmodel_CPU_read16(x_1, x_7);
x_50 = lean_uint8_to_uint16(x_4);
x_51 = lean_uint16_add(x_49, x_50);
x_52 = lp_dasmodel_CPU_read(x_1, x_51);
x_53 = 3;
x_54 = lean_uint16_add(x_5, x_53);
x_55 = lean_box(x_52);
x_56 = lean_box(x_54);
x_57 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_57, 0, x_55);
lean_ctor_set(x_57, 1, x_56);
return x_57;
}
}
else
{
uint16_t x_58; uint16_t x_59; uint16_t x_60; uint8_t x_61; uint16_t x_62; uint16_t x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; 
x_58 = lp_dasmodel_CPU_read16(x_1, x_7);
x_59 = lean_uint8_to_uint16(x_3);
x_60 = lean_uint16_add(x_58, x_59);
x_61 = lp_dasmodel_CPU_read(x_1, x_60);
x_62 = 3;
x_63 = lean_uint16_add(x_5, x_62);
x_64 = lean_box(x_61);
x_65 = lean_box(x_63);
x_66 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_66, 0, x_64);
lean_ctor_set(x_66, 1, x_65);
return x_66;
}
}
else
{
uint16_t x_67; uint8_t x_68; uint16_t x_69; uint16_t x_70; lean_object* x_71; lean_object* x_72; lean_object* x_73; 
x_67 = lp_dasmodel_CPU_read16(x_1, x_7);
x_68 = lp_dasmodel_CPU_read(x_1, x_67);
x_69 = 3;
x_70 = lean_uint16_add(x_5, x_69);
x_71 = lean_box(x_68);
x_72 = lean_box(x_70);
x_73 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_73, 0, x_71);
lean_ctor_set(x_73, 1, x_72);
return x_73;
}
}
else
{
uint8_t x_74; uint8_t x_75; uint8_t x_76; uint8_t x_77; uint16_t x_78; uint8_t x_79; uint16_t x_80; uint16_t x_81; lean_object* x_82; lean_object* x_83; lean_object* x_84; 
x_74 = lp_dasmodel_CPU_read(x_1, x_7);
x_75 = lean_uint8_add(x_74, x_4);
x_76 = 255;
x_77 = lean_uint8_land(x_75, x_76);
x_78 = lean_uint8_to_uint16(x_77);
x_79 = lp_dasmodel_CPU_read(x_1, x_78);
x_80 = 2;
x_81 = lean_uint16_add(x_5, x_80);
x_82 = lean_box(x_79);
x_83 = lean_box(x_81);
x_84 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_84, 0, x_82);
lean_ctor_set(x_84, 1, x_83);
return x_84;
}
}
else
{
uint8_t x_85; uint8_t x_86; uint8_t x_87; uint8_t x_88; uint16_t x_89; uint8_t x_90; uint16_t x_91; uint16_t x_92; lean_object* x_93; lean_object* x_94; lean_object* x_95; 
x_85 = lp_dasmodel_CPU_read(x_1, x_7);
x_86 = lean_uint8_add(x_85, x_3);
x_87 = 255;
x_88 = lean_uint8_land(x_86, x_87);
x_89 = lean_uint8_to_uint16(x_88);
x_90 = lp_dasmodel_CPU_read(x_1, x_89);
x_91 = 2;
x_92 = lean_uint16_add(x_5, x_91);
x_93 = lean_box(x_90);
x_94 = lean_box(x_92);
x_95 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_95, 0, x_93);
lean_ctor_set(x_95, 1, x_94);
return x_95;
}
}
else
{
uint8_t x_96; uint16_t x_97; uint8_t x_98; uint16_t x_99; uint16_t x_100; lean_object* x_101; lean_object* x_102; lean_object* x_103; 
x_96 = lp_dasmodel_CPU_read(x_1, x_7);
x_97 = lean_uint8_to_uint16(x_96);
x_98 = lp_dasmodel_CPU_read(x_1, x_97);
x_99 = 2;
x_100 = lean_uint16_add(x_5, x_99);
x_101 = lean_box(x_98);
x_102 = lean_box(x_100);
x_103 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_103, 0, x_101);
lean_ctor_set(x_103, 1, x_102);
return x_103;
}
}
else
{
uint8_t x_104; uint16_t x_105; uint16_t x_106; lean_object* x_107; lean_object* x_108; lean_object* x_109; 
x_104 = lp_dasmodel_CPU_read(x_1, x_7);
x_105 = 2;
x_106 = lean_uint16_add(x_5, x_105);
x_107 = lean_box(x_104);
x_108 = lean_box(x_106);
x_109 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_109, 0, x_107);
lean_ctor_set(x_109, 1, x_108);
return x_109;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchOperand___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_CPU_fetchOperand(x_1, x_2);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchAddr(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; uint16_t x_5; lean_object* x_6; uint16_t x_7; uint16_t x_8; uint8_t x_9; 
x_3 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_4 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_5 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_6 = lean_unsigned_to_nat(1u);
x_7 = 1;
x_8 = lean_uint16_add(x_5, x_7);
x_9 = lean_nat_dec_eq(x_2, x_6);
if (x_9 == 0)
{
lean_object* x_10; uint8_t x_11; 
x_10 = lean_unsigned_to_nat(2u);
x_11 = lean_nat_dec_eq(x_2, x_10);
if (x_11 == 0)
{
lean_object* x_12; uint8_t x_13; 
x_12 = lean_unsigned_to_nat(3u);
x_13 = lean_nat_dec_eq(x_2, x_12);
if (x_13 == 0)
{
lean_object* x_14; uint8_t x_15; 
x_14 = lean_unsigned_to_nat(4u);
x_15 = lean_nat_dec_eq(x_2, x_14);
if (x_15 == 0)
{
lean_object* x_16; uint8_t x_17; 
x_16 = lean_unsigned_to_nat(5u);
x_17 = lean_nat_dec_eq(x_2, x_16);
if (x_17 == 0)
{
lean_object* x_18; uint8_t x_19; 
x_18 = lean_unsigned_to_nat(6u);
x_19 = lean_nat_dec_eq(x_2, x_18);
if (x_19 == 0)
{
lean_object* x_20; uint8_t x_21; 
x_20 = lean_unsigned_to_nat(8u);
x_21 = lean_nat_dec_eq(x_2, x_20);
if (x_21 == 0)
{
uint16_t x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; 
x_22 = 0;
x_23 = lean_box(x_22);
x_24 = lean_box(x_8);
x_25 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_25, 0, x_23);
lean_ctor_set(x_25, 1, x_24);
return x_25;
}
else
{
uint8_t x_26; uint16_t x_27; uint16_t x_28; uint16_t x_29; uint16_t x_30; uint16_t x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; 
x_26 = lp_dasmodel_CPU_read(x_1, x_8);
x_27 = lp_dasmodel_CPU_readZP16(x_1, x_26);
x_28 = lean_uint8_to_uint16(x_4);
x_29 = lean_uint16_add(x_27, x_28);
x_30 = 2;
x_31 = lean_uint16_add(x_5, x_30);
x_32 = lean_box(x_29);
x_33 = lean_box(x_31);
x_34 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_34, 0, x_32);
lean_ctor_set(x_34, 1, x_33);
return x_34;
}
}
else
{
uint16_t x_35; uint16_t x_36; uint16_t x_37; uint16_t x_38; uint16_t x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; 
x_35 = lp_dasmodel_CPU_read16(x_1, x_8);
x_36 = lean_uint8_to_uint16(x_4);
x_37 = lean_uint16_add(x_35, x_36);
x_38 = 3;
x_39 = lean_uint16_add(x_5, x_38);
x_40 = lean_box(x_37);
x_41 = lean_box(x_39);
x_42 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_42, 0, x_40);
lean_ctor_set(x_42, 1, x_41);
return x_42;
}
}
else
{
uint16_t x_43; uint16_t x_44; uint16_t x_45; uint16_t x_46; uint16_t x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; 
x_43 = lp_dasmodel_CPU_read16(x_1, x_8);
x_44 = lean_uint8_to_uint16(x_3);
x_45 = lean_uint16_add(x_43, x_44);
x_46 = 3;
x_47 = lean_uint16_add(x_5, x_46);
x_48 = lean_box(x_45);
x_49 = lean_box(x_47);
x_50 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_50, 0, x_48);
lean_ctor_set(x_50, 1, x_49);
return x_50;
}
}
else
{
uint16_t x_51; uint16_t x_52; uint16_t x_53; lean_object* x_54; lean_object* x_55; lean_object* x_56; 
x_51 = lp_dasmodel_CPU_read16(x_1, x_8);
x_52 = 3;
x_53 = lean_uint16_add(x_5, x_52);
x_54 = lean_box(x_51);
x_55 = lean_box(x_53);
x_56 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_56, 0, x_54);
lean_ctor_set(x_56, 1, x_55);
return x_56;
}
}
else
{
uint8_t x_57; uint8_t x_58; uint16_t x_59; uint16_t x_60; uint16_t x_61; uint16_t x_62; uint16_t x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; 
x_57 = lp_dasmodel_CPU_read(x_1, x_8);
x_58 = lean_uint8_add(x_57, x_4);
x_59 = lean_uint8_to_uint16(x_58);
x_60 = 255;
x_61 = lean_uint16_land(x_59, x_60);
x_62 = 2;
x_63 = lean_uint16_add(x_5, x_62);
x_64 = lean_box(x_61);
x_65 = lean_box(x_63);
x_66 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_66, 0, x_64);
lean_ctor_set(x_66, 1, x_65);
return x_66;
}
}
else
{
uint8_t x_67; uint8_t x_68; uint16_t x_69; uint16_t x_70; uint16_t x_71; uint16_t x_72; uint16_t x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; 
x_67 = lp_dasmodel_CPU_read(x_1, x_8);
x_68 = lean_uint8_add(x_67, x_3);
x_69 = lean_uint8_to_uint16(x_68);
x_70 = 255;
x_71 = lean_uint16_land(x_69, x_70);
x_72 = 2;
x_73 = lean_uint16_add(x_5, x_72);
x_74 = lean_box(x_71);
x_75 = lean_box(x_73);
x_76 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_76, 0, x_74);
lean_ctor_set(x_76, 1, x_75);
return x_76;
}
}
else
{
uint8_t x_77; uint16_t x_78; uint16_t x_79; uint16_t x_80; lean_object* x_81; lean_object* x_82; lean_object* x_83; 
x_77 = lp_dasmodel_CPU_read(x_1, x_8);
x_78 = lean_uint8_to_uint16(x_77);
x_79 = 2;
x_80 = lean_uint16_add(x_5, x_79);
x_81 = lean_box(x_78);
x_82 = lean_box(x_80);
x_83 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_83, 0, x_81);
lean_ctor_set(x_83, 1, x_82);
return x_83;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_fetchAddr___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_CPU_fetchAddr(x_1, x_2);
lean_dec(x_2);
lean_dec_ref(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push(lean_object* x_1, uint8_t x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
uint8_t x_4; lean_object* x_5; uint16_t x_6; uint16_t x_7; uint16_t x_8; lean_object* x_9; lean_object* x_10; uint8_t x_11; uint8_t x_12; 
x_4 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_5 = lean_ctor_get(x_1, 1);
x_6 = 256;
x_7 = lean_uint8_to_uint16(x_4);
x_8 = lean_uint16_add(x_6, x_7);
x_9 = lean_uint16_to_nat(x_8);
x_10 = lean_byte_array_set(x_5, x_9, x_2);
x_11 = 1;
x_12 = lean_uint8_sub(x_4, x_11);
lean_ctor_set(x_1, 1, x_10);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 5, x_12);
return x_1;
}
else
{
uint8_t x_13; uint8_t x_14; uint8_t x_15; uint8_t x_16; uint16_t x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; uint16_t x_21; uint16_t x_22; uint16_t x_23; lean_object* x_24; lean_object* x_25; uint8_t x_26; uint8_t x_27; lean_object* x_28; 
x_13 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_14 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_15 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_16 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_17 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_18 = lean_ctor_get(x_1, 0);
x_19 = lean_ctor_get(x_1, 1);
x_20 = lean_ctor_get(x_1, 2);
lean_inc(x_20);
lean_inc(x_19);
lean_inc(x_18);
lean_dec(x_1);
x_21 = 256;
x_22 = lean_uint8_to_uint16(x_16);
x_23 = lean_uint16_add(x_21, x_22);
x_24 = lean_uint16_to_nat(x_23);
x_25 = lean_byte_array_set(x_19, x_24, x_2);
x_26 = 1;
x_27 = lean_uint8_sub(x_16, x_26);
x_28 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_28, 0, x_18);
lean_ctor_set(x_28, 1, x_25);
lean_ctor_set(x_28, 2, x_20);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 2, x_13);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 3, x_14);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 4, x_15);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 5, x_27);
lean_ctor_set_uint16(x_28, sizeof(void*)*3, x_17);
return x_28;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_CPU_push(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_pull(lean_object* x_1) {
_start:
{
uint8_t x_2; 
x_2 = !lean_is_exclusive(x_1);
if (x_2 == 0)
{
uint8_t x_3; lean_object* x_4; uint8_t x_5; uint8_t x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; 
x_3 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_4 = lean_ctor_get(x_1, 1);
x_5 = 1;
x_6 = lean_uint8_add(x_3, x_5);
x_7 = lean_unsigned_to_nat(256u);
x_8 = lean_uint8_to_nat(x_6);
x_9 = lean_nat_add(x_7, x_8);
x_10 = lean_byte_array_get(x_4, x_9);
lean_dec(x_9);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 5, x_6);
x_11 = lean_box(x_10);
x_12 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_12, 0, x_1);
lean_ctor_set(x_12, 1, x_11);
return x_12;
}
else
{
uint8_t x_13; uint8_t x_14; uint8_t x_15; uint8_t x_16; uint16_t x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; uint8_t x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; uint8_t x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; 
x_13 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_14 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_15 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_16 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_17 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_18 = lean_ctor_get(x_1, 0);
x_19 = lean_ctor_get(x_1, 1);
x_20 = lean_ctor_get(x_1, 2);
lean_inc(x_20);
lean_inc(x_19);
lean_inc(x_18);
lean_dec(x_1);
x_21 = 1;
x_22 = lean_uint8_add(x_16, x_21);
x_23 = lean_unsigned_to_nat(256u);
x_24 = lean_uint8_to_nat(x_22);
x_25 = lean_nat_add(x_23, x_24);
x_26 = lean_byte_array_get(x_19, x_25);
lean_dec(x_25);
x_27 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_27, 0, x_18);
lean_ctor_set(x_27, 1, x_19);
lean_ctor_set(x_27, 2, x_20);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 2, x_13);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 3, x_14);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 4, x_15);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 5, x_22);
lean_ctor_set_uint16(x_27, sizeof(void*)*3, x_17);
x_28 = lean_box(x_26);
x_29 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_29, 0, x_27);
lean_ctor_set(x_29, 1, x_28);
return x_29;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push16(lean_object* x_1, uint16_t x_2) {
_start:
{
uint16_t x_3; uint16_t x_4; uint8_t x_5; lean_object* x_6; uint8_t x_7; lean_object* x_8; 
x_3 = 8;
x_4 = lean_uint16_shift_right(x_2, x_3);
x_5 = lean_uint16_to_uint8(x_4);
x_6 = lp_dasmodel_CPU_push(x_1, x_5);
x_7 = lean_uint16_to_uint8(x_2);
x_8 = lp_dasmodel_CPU_push(x_6, x_7);
return x_8;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_push16___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_CPU_push16(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_CPU_pull16(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_2 = lp_dasmodel_CPU_pull(x_1);
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
x_4 = lean_ctor_get(x_2, 1);
lean_inc(x_4);
lean_dec_ref(x_2);
x_5 = lp_dasmodel_CPU_pull(x_3);
x_6 = !lean_is_exclusive(x_5);
if (x_6 == 0)
{
lean_object* x_7; uint8_t x_8; uint16_t x_9; uint8_t x_10; uint16_t x_11; uint16_t x_12; uint16_t x_13; uint16_t x_14; lean_object* x_15; 
x_7 = lean_ctor_get(x_5, 1);
x_8 = lean_unbox(x_4);
lean_dec(x_4);
x_9 = lean_uint8_to_uint16(x_8);
x_10 = lean_unbox(x_7);
lean_dec(x_7);
x_11 = lean_uint8_to_uint16(x_10);
x_12 = 8;
x_13 = lean_uint16_shift_left(x_11, x_12);
x_14 = lean_uint16_lor(x_9, x_13);
x_15 = lean_box(x_14);
lean_ctor_set(x_5, 1, x_15);
return x_5;
}
else
{
lean_object* x_16; lean_object* x_17; uint8_t x_18; uint16_t x_19; uint8_t x_20; uint16_t x_21; uint16_t x_22; uint16_t x_23; uint16_t x_24; lean_object* x_25; lean_object* x_26; 
x_16 = lean_ctor_get(x_5, 0);
x_17 = lean_ctor_get(x_5, 1);
lean_inc(x_17);
lean_inc(x_16);
lean_dec(x_5);
x_18 = lean_unbox(x_4);
lean_dec(x_4);
x_19 = lean_uint8_to_uint16(x_18);
x_20 = lean_unbox(x_17);
lean_dec(x_17);
x_21 = lean_uint8_to_uint16(x_20);
x_22 = 8;
x_23 = lean_uint16_shift_left(x_21, x_22);
x_24 = lean_uint16_lor(x_19, x_23);
x_25 = lean_box(x_24);
x_26 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_26, 0, x_16);
lean_ctor_set(x_26, 1, x_25);
return x_26;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doBranch(lean_object* x_1, uint8_t x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; uint16_t x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint16_t x_11; uint16_t x_17; uint16_t x_18; uint16_t x_19; uint16_t x_20; 
x_3 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_4 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_5 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_6 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_7 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_8 = lean_ctor_get(x_1, 0);
lean_inc_ref(x_8);
x_9 = lean_ctor_get(x_1, 1);
lean_inc_ref(x_9);
x_10 = lean_ctor_get(x_1, 2);
lean_inc(x_10);
x_17 = 1;
x_18 = lean_uint16_add(x_7, x_17);
x_19 = 2;
x_20 = lean_uint16_add(x_7, x_19);
if (x_2 == 0)
{
uint8_t x_21; 
x_21 = !lean_is_exclusive(x_1);
if (x_21 == 0)
{
lean_object* x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; 
x_22 = lean_ctor_get(x_1, 2);
lean_dec(x_22);
x_23 = lean_ctor_get(x_1, 1);
lean_dec(x_23);
x_24 = lean_ctor_get(x_1, 0);
lean_dec(x_24);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_20);
x_25 = lean_box(0);
x_26 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_26, 0, x_1);
lean_ctor_set(x_26, 1, x_25);
lean_ctor_set_uint8(x_26, sizeof(void*)*2, x_2);
return x_26;
}
else
{
lean_object* x_27; lean_object* x_28; lean_object* x_29; 
lean_dec(x_1);
x_27 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_27, 0, x_8);
lean_ctor_set(x_27, 1, x_9);
lean_ctor_set(x_27, 2, x_10);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 2, x_3);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 3, x_4);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 4, x_5);
lean_ctor_set_uint8(x_27, sizeof(void*)*3 + 5, x_6);
lean_ctor_set_uint16(x_27, sizeof(void*)*3, x_20);
x_28 = lean_box(0);
x_29 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_29, 0, x_27);
lean_ctor_set(x_29, 1, x_28);
lean_ctor_set_uint8(x_29, sizeof(void*)*2, x_2);
return x_29;
}
}
else
{
uint8_t x_30; uint8_t x_31; uint8_t x_32; uint8_t x_33; uint8_t x_34; 
x_30 = lp_dasmodel_CPU_read(x_1, x_18);
lean_dec_ref(x_1);
x_31 = 128;
x_32 = lean_uint8_land(x_30, x_31);
x_33 = 0;
x_34 = lean_uint8_dec_eq(x_32, x_33);
if (x_34 == 0)
{
uint16_t x_35; uint16_t x_36; uint16_t x_37; uint16_t x_38; 
x_35 = 256;
x_36 = lean_uint8_to_uint16(x_30);
x_37 = lean_uint16_sub(x_35, x_36);
x_38 = lean_uint16_sub(x_20, x_37);
x_11 = x_38;
goto block_16;
}
else
{
uint16_t x_39; uint16_t x_40; 
x_39 = lean_uint8_to_uint16(x_30);
x_40 = lean_uint16_add(x_20, x_39);
x_11 = x_40;
goto block_16;
}
}
block_16:
{
lean_object* x_12; lean_object* x_13; uint8_t x_14; lean_object* x_15; 
x_12 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_12, 0, x_8);
lean_ctor_set(x_12, 1, x_9);
lean_ctor_set(x_12, 2, x_10);
lean_ctor_set_uint8(x_12, sizeof(void*)*3 + 2, x_3);
lean_ctor_set_uint8(x_12, sizeof(void*)*3 + 3, x_4);
lean_ctor_set_uint8(x_12, sizeof(void*)*3 + 4, x_5);
lean_ctor_set_uint8(x_12, sizeof(void*)*3 + 5, x_6);
lean_ctor_set_uint16(x_12, sizeof(void*)*3, x_11);
x_13 = lean_box(0);
x_14 = 0;
x_15 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_15, 0, x_12);
lean_ctor_set(x_15, 1, x_13);
lean_ctor_set_uint8(x_15, sizeof(void*)*2, x_14);
return x_15;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doBranch___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doLoad(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; 
x_4 = lp_dasmodel_CPU_fetchOperand(x_1, x_2);
x_5 = lean_ctor_get(x_4, 0);
lean_inc(x_5);
x_6 = lean_ctor_get(x_4, 1);
lean_inc(x_6);
lean_dec_ref(x_4);
x_7 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_8 = lean_string_dec_eq(x_3, x_7);
if (x_8 == 0)
{
lean_object* x_9; uint8_t x_10; 
x_9 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__1));
x_10 = lean_string_dec_eq(x_3, x_9);
if (x_10 == 0)
{
lean_object* x_11; uint8_t x_12; 
x_11 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__2));
x_12 = lean_string_dec_eq(x_3, x_11);
if (x_12 == 0)
{
lean_object* x_13; uint8_t x_14; lean_object* x_15; 
lean_dec(x_6);
lean_dec(x_5);
x_13 = lean_box(0);
x_14 = 1;
x_15 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_15, 0, x_1);
lean_ctor_set(x_15, 1, x_13);
lean_ctor_set_uint8(x_15, sizeof(void*)*2, x_14);
return x_15;
}
else
{
uint8_t x_16; 
x_16 = !lean_is_exclusive(x_1);
if (x_16 == 0)
{
lean_object* x_17; uint8_t x_18; lean_object* x_19; uint8_t x_20; uint16_t x_21; lean_object* x_22; lean_object* x_23; 
x_17 = lean_ctor_get(x_1, 0);
x_18 = lean_unbox(x_5);
x_19 = lp_dasmodel_updateNZ(x_17, x_18);
lean_ctor_set(x_1, 0, x_19);
x_20 = lean_unbox(x_5);
lean_dec(x_5);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 4, x_20);
x_21 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_21);
x_22 = lean_box(0);
x_23 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_23, 0, x_1);
lean_ctor_set(x_23, 1, x_22);
lean_ctor_set_uint8(x_23, sizeof(void*)*2, x_10);
return x_23;
}
else
{
uint8_t x_24; uint8_t x_25; uint8_t x_26; lean_object* x_27; lean_object* x_28; lean_object* x_29; uint8_t x_30; lean_object* x_31; lean_object* x_32; uint8_t x_33; uint16_t x_34; lean_object* x_35; lean_object* x_36; 
x_24 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_25 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_26 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_27 = lean_ctor_get(x_1, 0);
x_28 = lean_ctor_get(x_1, 1);
x_29 = lean_ctor_get(x_1, 2);
lean_inc(x_29);
lean_inc(x_28);
lean_inc(x_27);
lean_dec(x_1);
x_30 = lean_unbox(x_5);
x_31 = lp_dasmodel_updateNZ(x_27, x_30);
x_32 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_32, 0, x_31);
lean_ctor_set(x_32, 1, x_28);
lean_ctor_set(x_32, 2, x_29);
lean_ctor_set_uint8(x_32, sizeof(void*)*3 + 2, x_24);
lean_ctor_set_uint8(x_32, sizeof(void*)*3 + 3, x_25);
x_33 = lean_unbox(x_5);
lean_dec(x_5);
lean_ctor_set_uint8(x_32, sizeof(void*)*3 + 4, x_33);
lean_ctor_set_uint8(x_32, sizeof(void*)*3 + 5, x_26);
x_34 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_32, sizeof(void*)*3, x_34);
x_35 = lean_box(0);
x_36 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_36, 0, x_32);
lean_ctor_set(x_36, 1, x_35);
lean_ctor_set_uint8(x_36, sizeof(void*)*2, x_10);
return x_36;
}
}
}
else
{
uint8_t x_37; 
x_37 = !lean_is_exclusive(x_1);
if (x_37 == 0)
{
lean_object* x_38; uint8_t x_39; lean_object* x_40; uint8_t x_41; uint16_t x_42; lean_object* x_43; lean_object* x_44; 
x_38 = lean_ctor_get(x_1, 0);
x_39 = lean_unbox(x_5);
x_40 = lp_dasmodel_updateNZ(x_38, x_39);
lean_ctor_set(x_1, 0, x_40);
x_41 = lean_unbox(x_5);
lean_dec(x_5);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 3, x_41);
x_42 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_42);
x_43 = lean_box(0);
x_44 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_44, 0, x_1);
lean_ctor_set(x_44, 1, x_43);
lean_ctor_set_uint8(x_44, sizeof(void*)*2, x_8);
return x_44;
}
else
{
uint8_t x_45; uint8_t x_46; uint8_t x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; uint8_t x_51; lean_object* x_52; lean_object* x_53; uint8_t x_54; uint16_t x_55; lean_object* x_56; lean_object* x_57; 
x_45 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_46 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_47 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_48 = lean_ctor_get(x_1, 0);
x_49 = lean_ctor_get(x_1, 1);
x_50 = lean_ctor_get(x_1, 2);
lean_inc(x_50);
lean_inc(x_49);
lean_inc(x_48);
lean_dec(x_1);
x_51 = lean_unbox(x_5);
x_52 = lp_dasmodel_updateNZ(x_48, x_51);
x_53 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_53, 0, x_52);
lean_ctor_set(x_53, 1, x_49);
lean_ctor_set(x_53, 2, x_50);
lean_ctor_set_uint8(x_53, sizeof(void*)*3 + 2, x_45);
x_54 = lean_unbox(x_5);
lean_dec(x_5);
lean_ctor_set_uint8(x_53, sizeof(void*)*3 + 3, x_54);
lean_ctor_set_uint8(x_53, sizeof(void*)*3 + 4, x_46);
lean_ctor_set_uint8(x_53, sizeof(void*)*3 + 5, x_47);
x_55 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_53, sizeof(void*)*3, x_55);
x_56 = lean_box(0);
x_57 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_57, 0, x_53);
lean_ctor_set(x_57, 1, x_56);
lean_ctor_set_uint8(x_57, sizeof(void*)*2, x_8);
return x_57;
}
}
}
else
{
uint8_t x_58; 
x_58 = !lean_is_exclusive(x_1);
if (x_58 == 0)
{
lean_object* x_59; uint8_t x_60; lean_object* x_61; uint8_t x_62; uint16_t x_63; lean_object* x_64; uint8_t x_65; lean_object* x_66; 
x_59 = lean_ctor_get(x_1, 0);
x_60 = lean_unbox(x_5);
x_61 = lp_dasmodel_updateNZ(x_59, x_60);
lean_ctor_set(x_1, 0, x_61);
x_62 = lean_unbox(x_5);
lean_dec(x_5);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_62);
x_63 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_63);
x_64 = lean_box(0);
x_65 = 0;
x_66 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_66, 0, x_1);
lean_ctor_set(x_66, 1, x_64);
lean_ctor_set_uint8(x_66, sizeof(void*)*2, x_65);
return x_66;
}
else
{
uint8_t x_67; uint8_t x_68; uint8_t x_69; lean_object* x_70; lean_object* x_71; lean_object* x_72; uint8_t x_73; lean_object* x_74; lean_object* x_75; uint8_t x_76; uint16_t x_77; lean_object* x_78; uint8_t x_79; lean_object* x_80; 
x_67 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_68 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_69 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_70 = lean_ctor_get(x_1, 0);
x_71 = lean_ctor_get(x_1, 1);
x_72 = lean_ctor_get(x_1, 2);
lean_inc(x_72);
lean_inc(x_71);
lean_inc(x_70);
lean_dec(x_1);
x_73 = lean_unbox(x_5);
x_74 = lp_dasmodel_updateNZ(x_70, x_73);
x_75 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_75, 0, x_74);
lean_ctor_set(x_75, 1, x_71);
lean_ctor_set(x_75, 2, x_72);
x_76 = lean_unbox(x_5);
lean_dec(x_5);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 2, x_76);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 3, x_67);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 4, x_68);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 5, x_69);
x_77 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_75, sizeof(void*)*3, x_77);
x_78 = lean_box(0);
x_79 = 0;
x_80 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_80, 0, x_75);
lean_ctor_set(x_80, 1, x_78);
lean_ctor_set_uint8(x_80, sizeof(void*)*2, x_79);
return x_80;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doLoad___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_2, x_3);
lean_dec_ref(x_3);
lean_dec(x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doStore(lean_object* x_1, lean_object* x_2, uint8_t x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint16_t x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; uint8_t x_11; 
x_4 = lp_dasmodel_CPU_fetchAddr(x_1, x_2);
x_5 = lean_ctor_get(x_4, 0);
lean_inc(x_5);
x_6 = lean_ctor_get(x_4, 1);
lean_inc(x_6);
lean_dec_ref(x_4);
x_7 = lean_unbox(x_5);
lean_dec(x_5);
x_8 = lp_dasmodel_CPU_write(x_1, x_7, x_3);
x_9 = lean_ctor_get(x_8, 0);
lean_inc(x_9);
x_10 = lean_ctor_get(x_8, 1);
lean_inc(x_10);
lean_dec_ref(x_8);
x_11 = !lean_is_exclusive(x_9);
if (x_11 == 0)
{
uint16_t x_12; uint8_t x_13; lean_object* x_14; 
x_12 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_9, sizeof(void*)*3, x_12);
x_13 = 0;
x_14 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_14, 0, x_9);
lean_ctor_set(x_14, 1, x_10);
lean_ctor_set_uint8(x_14, sizeof(void*)*2, x_13);
return x_14;
}
else
{
uint8_t x_15; uint8_t x_16; uint8_t x_17; uint8_t x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; uint16_t x_23; uint8_t x_24; lean_object* x_25; 
x_15 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 2);
x_16 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 3);
x_17 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 4);
x_18 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 5);
x_19 = lean_ctor_get(x_9, 0);
x_20 = lean_ctor_get(x_9, 1);
x_21 = lean_ctor_get(x_9, 2);
lean_inc(x_21);
lean_inc(x_20);
lean_inc(x_19);
lean_dec(x_9);
x_22 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_22, 0, x_19);
lean_ctor_set(x_22, 1, x_20);
lean_ctor_set(x_22, 2, x_21);
lean_ctor_set_uint8(x_22, sizeof(void*)*3 + 2, x_15);
lean_ctor_set_uint8(x_22, sizeof(void*)*3 + 3, x_16);
lean_ctor_set_uint8(x_22, sizeof(void*)*3 + 4, x_17);
lean_ctor_set_uint8(x_22, sizeof(void*)*3 + 5, x_18);
x_23 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_22, sizeof(void*)*3, x_23);
x_24 = 0;
x_25 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_25, 0, x_22);
lean_ctor_set(x_25, 1, x_10);
lean_ctor_set_uint8(x_25, sizeof(void*)*2, x_24);
return x_25;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doStore___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_3);
x_5 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_2, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doALU(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; 
x_4 = lp_dasmodel_CPU_fetchOperand(x_1, x_2);
x_5 = lean_ctor_get(x_4, 0);
lean_inc(x_5);
x_6 = lean_ctor_get(x_4, 1);
lean_inc(x_6);
lean_dec_ref(x_4);
x_7 = !lean_is_exclusive(x_1);
if (x_7 == 0)
{
uint8_t x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; uint8_t x_14; uint16_t x_15; lean_object* x_16; uint8_t x_17; lean_object* x_18; 
x_8 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_9 = lean_ctor_get(x_1, 0);
x_10 = lean_box(x_8);
x_11 = lean_apply_2(x_3, x_10, x_5);
x_12 = lean_unbox(x_11);
x_13 = lp_dasmodel_updateNZ(x_9, x_12);
lean_ctor_set(x_1, 0, x_13);
x_14 = lean_unbox(x_11);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_14);
x_15 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_15);
x_16 = lean_box(0);
x_17 = 0;
x_18 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_18, 0, x_1);
lean_ctor_set(x_18, 1, x_16);
lean_ctor_set_uint8(x_18, sizeof(void*)*2, x_17);
return x_18;
}
else
{
uint8_t x_19; uint8_t x_20; uint8_t x_21; uint8_t x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; uint8_t x_28; lean_object* x_29; lean_object* x_30; uint8_t x_31; uint16_t x_32; lean_object* x_33; uint8_t x_34; lean_object* x_35; 
x_19 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_20 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_21 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_22 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_23 = lean_ctor_get(x_1, 0);
x_24 = lean_ctor_get(x_1, 1);
x_25 = lean_ctor_get(x_1, 2);
lean_inc(x_25);
lean_inc(x_24);
lean_inc(x_23);
lean_dec(x_1);
x_26 = lean_box(x_19);
x_27 = lean_apply_2(x_3, x_26, x_5);
x_28 = lean_unbox(x_27);
x_29 = lp_dasmodel_updateNZ(x_23, x_28);
x_30 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_30, 0, x_29);
lean_ctor_set(x_30, 1, x_24);
lean_ctor_set(x_30, 2, x_25);
x_31 = lean_unbox(x_27);
lean_ctor_set_uint8(x_30, sizeof(void*)*3 + 2, x_31);
lean_ctor_set_uint8(x_30, sizeof(void*)*3 + 3, x_20);
lean_ctor_set_uint8(x_30, sizeof(void*)*3 + 4, x_21);
lean_ctor_set_uint8(x_30, sizeof(void*)*3 + 5, x_22);
x_32 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_30, sizeof(void*)*3, x_32);
x_33 = lean_box(0);
x_34 = 0;
x_35 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_35, 0, x_30);
lean_ctor_set(x_35, 1, x_33);
lean_ctor_set_uint8(x_35, sizeof(void*)*2, x_34);
return x_35;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doALU___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_2, x_3);
lean_dec(x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doCMP(lean_object* x_1, lean_object* x_2, uint8_t x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; uint8_t x_7; 
x_4 = lp_dasmodel_CPU_fetchOperand(x_1, x_2);
x_5 = lean_ctor_get(x_4, 0);
lean_inc(x_5);
x_6 = lean_ctor_get(x_4, 1);
lean_inc(x_6);
lean_dec_ref(x_4);
x_7 = !lean_is_exclusive(x_1);
if (x_7 == 0)
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; uint8_t x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; uint8_t x_16; lean_object* x_17; uint8_t x_18; 
x_8 = lean_ctor_get(x_1, 0);
x_9 = lean_uint8_to_nat(x_3);
x_10 = lean_unsigned_to_nat(256u);
x_11 = lean_nat_add(x_9, x_10);
x_12 = lean_unbox(x_5);
x_13 = lean_uint8_to_nat(x_12);
x_14 = lean_nat_sub(x_11, x_13);
lean_dec(x_11);
x_15 = lean_nat_mod(x_14, x_10);
lean_dec(x_14);
x_16 = lean_uint8_of_nat(x_15);
lean_dec(x_15);
x_17 = lp_dasmodel_updateNZ(x_8, x_16);
x_18 = !lean_is_exclusive(x_17);
if (x_18 == 0)
{
uint8_t x_19; uint8_t x_20; uint16_t x_21; lean_object* x_22; uint8_t x_23; lean_object* x_24; 
x_19 = lean_unbox(x_5);
lean_dec(x_5);
x_20 = lean_uint8_dec_le(x_19, x_3);
lean_ctor_set_uint8(x_17, 0, x_20);
lean_ctor_set(x_1, 0, x_17);
x_21 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_21);
x_22 = lean_box(0);
x_23 = 0;
x_24 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_24, 0, x_1);
lean_ctor_set(x_24, 1, x_22);
lean_ctor_set_uint8(x_24, sizeof(void*)*2, x_23);
return x_24;
}
else
{
uint8_t x_25; uint8_t x_26; uint8_t x_27; uint8_t x_28; uint8_t x_29; uint8_t x_30; uint8_t x_31; lean_object* x_32; uint16_t x_33; lean_object* x_34; uint8_t x_35; lean_object* x_36; 
x_25 = lean_ctor_get_uint8(x_17, 1);
x_26 = lean_ctor_get_uint8(x_17, 2);
x_27 = lean_ctor_get_uint8(x_17, 3);
x_28 = lean_ctor_get_uint8(x_17, 4);
x_29 = lean_ctor_get_uint8(x_17, 5);
lean_dec(x_17);
x_30 = lean_unbox(x_5);
lean_dec(x_5);
x_31 = lean_uint8_dec_le(x_30, x_3);
x_32 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_32, 0, x_31);
lean_ctor_set_uint8(x_32, 1, x_25);
lean_ctor_set_uint8(x_32, 2, x_26);
lean_ctor_set_uint8(x_32, 3, x_27);
lean_ctor_set_uint8(x_32, 4, x_28);
lean_ctor_set_uint8(x_32, 5, x_29);
lean_ctor_set(x_1, 0, x_32);
x_33 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_33);
x_34 = lean_box(0);
x_35 = 0;
x_36 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_36, 0, x_1);
lean_ctor_set(x_36, 1, x_34);
lean_ctor_set_uint8(x_36, sizeof(void*)*2, x_35);
return x_36;
}
}
else
{
uint8_t x_37; uint8_t x_38; uint8_t x_39; uint8_t x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; uint8_t x_47; lean_object* x_48; lean_object* x_49; lean_object* x_50; uint8_t x_51; lean_object* x_52; uint8_t x_53; uint8_t x_54; uint8_t x_55; uint8_t x_56; uint8_t x_57; lean_object* x_58; uint8_t x_59; uint8_t x_60; lean_object* x_61; lean_object* x_62; uint16_t x_63; lean_object* x_64; uint8_t x_65; lean_object* x_66; 
x_37 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_38 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_39 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_40 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_41 = lean_ctor_get(x_1, 0);
x_42 = lean_ctor_get(x_1, 1);
x_43 = lean_ctor_get(x_1, 2);
lean_inc(x_43);
lean_inc(x_42);
lean_inc(x_41);
lean_dec(x_1);
x_44 = lean_uint8_to_nat(x_3);
x_45 = lean_unsigned_to_nat(256u);
x_46 = lean_nat_add(x_44, x_45);
x_47 = lean_unbox(x_5);
x_48 = lean_uint8_to_nat(x_47);
x_49 = lean_nat_sub(x_46, x_48);
lean_dec(x_46);
x_50 = lean_nat_mod(x_49, x_45);
lean_dec(x_49);
x_51 = lean_uint8_of_nat(x_50);
lean_dec(x_50);
x_52 = lp_dasmodel_updateNZ(x_41, x_51);
x_53 = lean_ctor_get_uint8(x_52, 1);
x_54 = lean_ctor_get_uint8(x_52, 2);
x_55 = lean_ctor_get_uint8(x_52, 3);
x_56 = lean_ctor_get_uint8(x_52, 4);
x_57 = lean_ctor_get_uint8(x_52, 5);
if (lean_is_exclusive(x_52)) {
 x_58 = x_52;
} else {
 lean_dec_ref(x_52);
 x_58 = lean_box(0);
}
x_59 = lean_unbox(x_5);
lean_dec(x_5);
x_60 = lean_uint8_dec_le(x_59, x_3);
if (lean_is_scalar(x_58)) {
 x_61 = lean_alloc_ctor(0, 0, 6);
} else {
 x_61 = x_58;
}
lean_ctor_set_uint8(x_61, 0, x_60);
lean_ctor_set_uint8(x_61, 1, x_53);
lean_ctor_set_uint8(x_61, 2, x_54);
lean_ctor_set_uint8(x_61, 3, x_55);
lean_ctor_set_uint8(x_61, 4, x_56);
lean_ctor_set_uint8(x_61, 5, x_57);
x_62 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_62, 0, x_61);
lean_ctor_set(x_62, 1, x_42);
lean_ctor_set(x_62, 2, x_43);
lean_ctor_set_uint8(x_62, sizeof(void*)*3 + 2, x_37);
lean_ctor_set_uint8(x_62, sizeof(void*)*3 + 3, x_38);
lean_ctor_set_uint8(x_62, sizeof(void*)*3 + 4, x_39);
lean_ctor_set_uint8(x_62, sizeof(void*)*3 + 5, x_40);
x_63 = lean_unbox(x_6);
lean_dec(x_6);
lean_ctor_set_uint16(x_62, sizeof(void*)*3, x_63);
x_64 = lean_box(0);
x_65 = 0;
x_66 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_66, 0, x_62);
lean_ctor_set(x_66, 1, x_64);
lean_ctor_set_uint8(x_66, sizeof(void*)*2, x_65);
return x_66;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doCMP___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint8_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_3);
x_5 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_2, x_4);
lean_dec(x_2);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doShiftMem(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; uint8_t x_8; uint16_t x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; uint16_t x_16; uint8_t x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; uint8_t x_21; 
x_4 = lp_dasmodel_CPU_fetchAddr(x_1, x_2);
x_5 = lean_ctor_get(x_1, 0);
lean_inc_ref(x_5);
x_6 = lean_ctor_get(x_4, 0);
lean_inc(x_6);
x_7 = lean_ctor_get(x_4, 1);
lean_inc(x_7);
lean_dec_ref(x_4);
x_8 = lean_ctor_get_uint8(x_5, 0);
x_9 = lean_unbox(x_6);
x_10 = lp_dasmodel_CPU_read(x_1, x_9);
x_11 = lean_box(x_10);
x_12 = lean_box(x_8);
x_13 = lean_apply_2(x_3, x_11, x_12);
x_14 = lean_ctor_get(x_13, 0);
lean_inc(x_14);
x_15 = lean_ctor_get(x_13, 1);
lean_inc(x_15);
lean_dec_ref(x_13);
x_16 = lean_unbox(x_6);
lean_dec(x_6);
x_17 = lean_unbox(x_14);
x_18 = lp_dasmodel_CPU_write(x_1, x_16, x_17);
x_19 = lean_ctor_get(x_18, 0);
lean_inc(x_19);
x_20 = lean_ctor_get(x_18, 1);
lean_inc(x_20);
lean_dec_ref(x_18);
x_21 = !lean_is_exclusive(x_19);
if (x_21 == 0)
{
lean_object* x_22; uint8_t x_23; lean_object* x_24; uint8_t x_25; 
x_22 = lean_ctor_get(x_19, 0);
lean_dec(x_22);
x_23 = lean_unbox(x_14);
lean_dec(x_14);
x_24 = lp_dasmodel_updateNZ(x_5, x_23);
x_25 = !lean_is_exclusive(x_24);
if (x_25 == 0)
{
uint8_t x_26; uint16_t x_27; uint8_t x_28; lean_object* x_29; 
x_26 = lean_unbox(x_15);
lean_dec(x_15);
lean_ctor_set_uint8(x_24, 0, x_26);
lean_ctor_set(x_19, 0, x_24);
x_27 = lean_unbox(x_7);
lean_dec(x_7);
lean_ctor_set_uint16(x_19, sizeof(void*)*3, x_27);
x_28 = 0;
x_29 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_29, 0, x_19);
lean_ctor_set(x_29, 1, x_20);
lean_ctor_set_uint8(x_29, sizeof(void*)*2, x_28);
return x_29;
}
else
{
uint8_t x_30; uint8_t x_31; uint8_t x_32; uint8_t x_33; uint8_t x_34; lean_object* x_35; uint8_t x_36; uint16_t x_37; uint8_t x_38; lean_object* x_39; 
x_30 = lean_ctor_get_uint8(x_24, 1);
x_31 = lean_ctor_get_uint8(x_24, 2);
x_32 = lean_ctor_get_uint8(x_24, 3);
x_33 = lean_ctor_get_uint8(x_24, 4);
x_34 = lean_ctor_get_uint8(x_24, 5);
lean_dec(x_24);
x_35 = lean_alloc_ctor(0, 0, 6);
x_36 = lean_unbox(x_15);
lean_dec(x_15);
lean_ctor_set_uint8(x_35, 0, x_36);
lean_ctor_set_uint8(x_35, 1, x_30);
lean_ctor_set_uint8(x_35, 2, x_31);
lean_ctor_set_uint8(x_35, 3, x_32);
lean_ctor_set_uint8(x_35, 4, x_33);
lean_ctor_set_uint8(x_35, 5, x_34);
lean_ctor_set(x_19, 0, x_35);
x_37 = lean_unbox(x_7);
lean_dec(x_7);
lean_ctor_set_uint16(x_19, sizeof(void*)*3, x_37);
x_38 = 0;
x_39 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_39, 0, x_19);
lean_ctor_set(x_39, 1, x_20);
lean_ctor_set_uint8(x_39, sizeof(void*)*2, x_38);
return x_39;
}
}
else
{
uint8_t x_40; uint8_t x_41; uint8_t x_42; uint8_t x_43; lean_object* x_44; lean_object* x_45; uint8_t x_46; lean_object* x_47; uint8_t x_48; uint8_t x_49; uint8_t x_50; uint8_t x_51; uint8_t x_52; lean_object* x_53; lean_object* x_54; uint8_t x_55; lean_object* x_56; uint16_t x_57; uint8_t x_58; lean_object* x_59; 
x_40 = lean_ctor_get_uint8(x_19, sizeof(void*)*3 + 2);
x_41 = lean_ctor_get_uint8(x_19, sizeof(void*)*3 + 3);
x_42 = lean_ctor_get_uint8(x_19, sizeof(void*)*3 + 4);
x_43 = lean_ctor_get_uint8(x_19, sizeof(void*)*3 + 5);
x_44 = lean_ctor_get(x_19, 1);
x_45 = lean_ctor_get(x_19, 2);
lean_inc(x_45);
lean_inc(x_44);
lean_dec(x_19);
x_46 = lean_unbox(x_14);
lean_dec(x_14);
x_47 = lp_dasmodel_updateNZ(x_5, x_46);
x_48 = lean_ctor_get_uint8(x_47, 1);
x_49 = lean_ctor_get_uint8(x_47, 2);
x_50 = lean_ctor_get_uint8(x_47, 3);
x_51 = lean_ctor_get_uint8(x_47, 4);
x_52 = lean_ctor_get_uint8(x_47, 5);
if (lean_is_exclusive(x_47)) {
 x_53 = x_47;
} else {
 lean_dec_ref(x_47);
 x_53 = lean_box(0);
}
if (lean_is_scalar(x_53)) {
 x_54 = lean_alloc_ctor(0, 0, 6);
} else {
 x_54 = x_53;
}
x_55 = lean_unbox(x_15);
lean_dec(x_15);
lean_ctor_set_uint8(x_54, 0, x_55);
lean_ctor_set_uint8(x_54, 1, x_48);
lean_ctor_set_uint8(x_54, 2, x_49);
lean_ctor_set_uint8(x_54, 3, x_50);
lean_ctor_set_uint8(x_54, 4, x_51);
lean_ctor_set_uint8(x_54, 5, x_52);
x_56 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_56, 0, x_54);
lean_ctor_set(x_56, 1, x_44);
lean_ctor_set(x_56, 2, x_45);
lean_ctor_set_uint8(x_56, sizeof(void*)*3 + 2, x_40);
lean_ctor_set_uint8(x_56, sizeof(void*)*3 + 3, x_41);
lean_ctor_set_uint8(x_56, sizeof(void*)*3 + 4, x_42);
lean_ctor_set_uint8(x_56, sizeof(void*)*3 + 5, x_43);
x_57 = lean_unbox(x_7);
lean_dec(x_7);
lean_ctor_set_uint16(x_56, sizeof(void*)*3, x_57);
x_58 = 0;
x_59 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_59, 0, x_56);
lean_ctor_set(x_59, 1, x_20);
lean_ctor_set_uint8(x_59, sizeof(void*)*2, x_58);
return x_59;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__doShiftMem___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_2, x_3);
lean_dec(x_2);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp___redArg(uint8_t x_1) {
_start:
{
uint8_t x_2; uint8_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; 
x_2 = 1;
x_3 = lean_uint8_shift_left(x_1, x_2);
x_4 = 128;
x_5 = lean_uint8_land(x_1, x_4);
x_6 = 0;
x_7 = lean_uint8_dec_eq(x_5, x_6);
if (x_7 == 0)
{
uint8_t x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; 
x_8 = 1;
x_9 = lean_box(x_3);
x_10 = lean_box(x_8);
x_11 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_11, 0, x_9);
lean_ctor_set(x_11, 1, x_10);
return x_11;
}
else
{
uint8_t x_12; lean_object* x_13; lean_object* x_14; lean_object* x_15; 
x_12 = 0;
x_13 = lean_box(x_3);
x_14 = lean_box(x_12);
x_15 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_15, 0, x_13);
lean_ctor_set(x_15, 1, x_14);
return x_15;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp___redArg___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel___private_CPU6502_0__aslOp___redArg(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp(uint8_t x_1, uint8_t x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel___private_CPU6502_0__aslOp___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__aslOp___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; lean_object* x_5; 
x_3 = lean_unbox(x_1);
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel___private_CPU6502_0__aslOp(x_3, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp___redArg(uint8_t x_1) {
_start:
{
uint8_t x_2; uint8_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; 
x_2 = 1;
x_3 = lean_uint8_shift_right(x_1, x_2);
x_4 = lean_uint8_land(x_1, x_2);
x_5 = 0;
x_6 = lean_uint8_dec_eq(x_4, x_5);
if (x_6 == 0)
{
uint8_t x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_7 = 1;
x_8 = lean_box(x_3);
x_9 = lean_box(x_7);
x_10 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_10, 0, x_8);
lean_ctor_set(x_10, 1, x_9);
return x_10;
}
else
{
uint8_t x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_11 = 0;
x_12 = lean_box(x_3);
x_13 = lean_box(x_11);
x_14 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_14, 0, x_12);
lean_ctor_set(x_14, 1, x_13);
return x_14;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp___redArg___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel___private_CPU6502_0__lsrOp___redArg(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp(uint8_t x_1, uint8_t x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel___private_CPU6502_0__lsrOp___redArg(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__lsrOp___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; lean_object* x_5; 
x_3 = lean_unbox(x_1);
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel___private_CPU6502_0__lsrOp(x_3, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rolOp(uint8_t x_1, uint8_t x_2) {
_start:
{
uint8_t x_3; 
if (x_2 == 0)
{
uint8_t x_20; 
x_20 = 0;
x_3 = x_20;
goto block_19;
}
else
{
uint8_t x_21; 
x_21 = 1;
x_3 = x_21;
goto block_19;
}
block_19:
{
uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; uint8_t x_9; uint8_t x_10; 
x_4 = 1;
x_5 = lean_uint8_shift_left(x_1, x_4);
x_6 = lean_uint8_lor(x_5, x_3);
x_7 = 128;
x_8 = lean_uint8_land(x_1, x_7);
x_9 = 0;
x_10 = lean_uint8_dec_eq(x_8, x_9);
if (x_10 == 0)
{
uint8_t x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_11 = 1;
x_12 = lean_box(x_6);
x_13 = lean_box(x_11);
x_14 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_14, 0, x_12);
lean_ctor_set(x_14, 1, x_13);
return x_14;
}
else
{
uint8_t x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; 
x_15 = 0;
x_16 = lean_box(x_6);
x_17 = lean_box(x_15);
x_18 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_18, 0, x_16);
lean_ctor_set(x_18, 1, x_17);
return x_18;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rolOp___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; lean_object* x_5; 
x_3 = lean_unbox(x_1);
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel___private_CPU6502_0__rolOp(x_3, x_4);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rorOp(uint8_t x_1, uint8_t x_2) {
_start:
{
uint8_t x_3; 
if (x_2 == 0)
{
uint8_t x_19; 
x_19 = 0;
x_3 = x_19;
goto block_18;
}
else
{
uint8_t x_20; 
x_20 = 128;
x_3 = x_20;
goto block_18;
}
block_18:
{
uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; uint8_t x_9; 
x_4 = 1;
x_5 = lean_uint8_shift_right(x_1, x_4);
x_6 = lean_uint8_lor(x_5, x_3);
x_7 = lean_uint8_land(x_1, x_4);
x_8 = 0;
x_9 = lean_uint8_dec_eq(x_7, x_8);
if (x_9 == 0)
{
uint8_t x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; 
x_10 = 1;
x_11 = lean_box(x_6);
x_12 = lean_box(x_10);
x_13 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_13, 0, x_11);
lean_ctor_set(x_13, 1, x_12);
return x_13;
}
else
{
uint8_t x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_14 = 0;
x_15 = lean_box(x_6);
x_16 = lean_box(x_14);
x_17 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_17, 0, x_15);
lean_ctor_set(x_17, 1, x_16);
return x_17;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__rorOp___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; uint8_t x_4; lean_object* x_5; 
x_3 = lean_unbox(x_1);
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel___private_CPU6502_0__rorOp(x_3, x_4);
return x_5;
}
}
LEAN_EXPORT uint8_t lp_dasmodel___private_CPU6502_0__flagsToByte(lean_object* x_1) {
_start:
{
uint8_t x_2; uint8_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; uint8_t x_9; uint8_t x_16; uint8_t x_17; uint8_t x_24; uint8_t x_25; uint8_t x_30; uint8_t x_31; uint8_t x_36; 
x_2 = lean_ctor_get_uint8(x_1, 0);
x_3 = lean_ctor_get_uint8(x_1, 1);
x_4 = lean_ctor_get_uint8(x_1, 2);
x_5 = lean_ctor_get_uint8(x_1, 3);
x_6 = lean_ctor_get_uint8(x_1, 4);
x_7 = lean_ctor_get_uint8(x_1, 5);
if (x_2 == 0)
{
uint8_t x_40; 
x_40 = 0;
x_36 = x_40;
goto block_39;
}
else
{
uint8_t x_41; 
x_41 = 1;
x_36 = x_41;
goto block_39;
}
block_15:
{
uint8_t x_10; 
x_10 = lean_uint8_lor(x_8, x_9);
if (x_7 == 0)
{
uint8_t x_11; uint8_t x_12; 
x_11 = 0;
x_12 = lean_uint8_lor(x_10, x_11);
return x_12;
}
else
{
uint8_t x_13; uint8_t x_14; 
x_13 = 128;
x_14 = lean_uint8_lor(x_10, x_13);
return x_14;
}
}
block_23:
{
uint8_t x_18; uint8_t x_19; uint8_t x_20; 
x_18 = lean_uint8_lor(x_16, x_17);
x_19 = 48;
x_20 = lean_uint8_lor(x_18, x_19);
if (x_6 == 0)
{
uint8_t x_21; 
x_21 = 0;
x_8 = x_20;
x_9 = x_21;
goto block_15;
}
else
{
uint8_t x_22; 
x_22 = 64;
x_8 = x_20;
x_9 = x_22;
goto block_15;
}
}
block_29:
{
uint8_t x_26; 
x_26 = lean_uint8_lor(x_24, x_25);
if (x_5 == 0)
{
uint8_t x_27; 
x_27 = 0;
x_16 = x_26;
x_17 = x_27;
goto block_23;
}
else
{
uint8_t x_28; 
x_28 = 8;
x_16 = x_26;
x_17 = x_28;
goto block_23;
}
}
block_35:
{
uint8_t x_32; 
x_32 = lean_uint8_lor(x_30, x_31);
if (x_4 == 0)
{
uint8_t x_33; 
x_33 = 0;
x_24 = x_32;
x_25 = x_33;
goto block_29;
}
else
{
uint8_t x_34; 
x_34 = 4;
x_24 = x_32;
x_25 = x_34;
goto block_29;
}
}
block_39:
{
if (x_3 == 0)
{
uint8_t x_37; 
x_37 = 0;
x_30 = x_36;
x_31 = x_37;
goto block_35;
}
else
{
uint8_t x_38; 
x_38 = 2;
x_30 = x_36;
x_31 = x_38;
goto block_35;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__flagsToByte___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lp_dasmodel___private_CPU6502_0__flagsToByte(x_1);
lean_dec_ref(x_1);
x_3 = lean_box(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__byteToFlags(uint8_t x_1) {
_start:
{
uint8_t x_2; uint8_t x_3; uint8_t x_4; uint8_t x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; uint8_t x_9; uint8_t x_18; uint8_t x_19; uint8_t x_20; uint8_t x_21; uint8_t x_28; uint8_t x_29; uint8_t x_30; uint8_t x_37; uint8_t x_38; uint8_t x_45; uint8_t x_52; 
x_2 = 1;
x_3 = lean_uint8_land(x_1, x_2);
x_4 = 0;
x_52 = lean_uint8_dec_eq(x_3, x_4);
if (x_52 == 0)
{
uint8_t x_53; 
x_53 = 1;
x_45 = x_53;
goto block_51;
}
else
{
uint8_t x_54; 
x_54 = 0;
x_45 = x_54;
goto block_51;
}
block_17:
{
uint8_t x_10; uint8_t x_11; uint8_t x_12; 
x_10 = 128;
x_11 = lean_uint8_land(x_1, x_10);
x_12 = lean_uint8_dec_eq(x_11, x_4);
if (x_12 == 0)
{
uint8_t x_13; lean_object* x_14; 
x_13 = 1;
x_14 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_14, 0, x_8);
lean_ctor_set_uint8(x_14, 1, x_5);
lean_ctor_set_uint8(x_14, 2, x_7);
lean_ctor_set_uint8(x_14, 3, x_6);
lean_ctor_set_uint8(x_14, 4, x_9);
lean_ctor_set_uint8(x_14, 5, x_13);
return x_14;
}
else
{
uint8_t x_15; lean_object* x_16; 
x_15 = 0;
x_16 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_16, 0, x_8);
lean_ctor_set_uint8(x_16, 1, x_5);
lean_ctor_set_uint8(x_16, 2, x_7);
lean_ctor_set_uint8(x_16, 3, x_6);
lean_ctor_set_uint8(x_16, 4, x_9);
lean_ctor_set_uint8(x_16, 5, x_15);
return x_16;
}
}
block_27:
{
uint8_t x_22; uint8_t x_23; uint8_t x_24; 
x_22 = 64;
x_23 = lean_uint8_land(x_1, x_22);
x_24 = lean_uint8_dec_eq(x_23, x_4);
if (x_24 == 0)
{
uint8_t x_25; 
x_25 = 1;
x_5 = x_18;
x_6 = x_21;
x_7 = x_19;
x_8 = x_20;
x_9 = x_25;
goto block_17;
}
else
{
uint8_t x_26; 
x_26 = 0;
x_5 = x_18;
x_6 = x_21;
x_7 = x_19;
x_8 = x_20;
x_9 = x_26;
goto block_17;
}
}
block_36:
{
uint8_t x_31; uint8_t x_32; uint8_t x_33; 
x_31 = 8;
x_32 = lean_uint8_land(x_1, x_31);
x_33 = lean_uint8_dec_eq(x_32, x_4);
if (x_33 == 0)
{
uint8_t x_34; 
x_34 = 1;
x_18 = x_28;
x_19 = x_30;
x_20 = x_29;
x_21 = x_34;
goto block_27;
}
else
{
uint8_t x_35; 
x_35 = 0;
x_18 = x_28;
x_19 = x_30;
x_20 = x_29;
x_21 = x_35;
goto block_27;
}
}
block_44:
{
uint8_t x_39; uint8_t x_40; uint8_t x_41; 
x_39 = 4;
x_40 = lean_uint8_land(x_1, x_39);
x_41 = lean_uint8_dec_eq(x_40, x_4);
if (x_41 == 0)
{
uint8_t x_42; 
x_42 = 1;
x_28 = x_38;
x_29 = x_37;
x_30 = x_42;
goto block_36;
}
else
{
uint8_t x_43; 
x_43 = 0;
x_28 = x_38;
x_29 = x_37;
x_30 = x_43;
goto block_36;
}
}
block_51:
{
uint8_t x_46; uint8_t x_47; uint8_t x_48; 
x_46 = 2;
x_47 = lean_uint8_land(x_1, x_46);
x_48 = lean_uint8_dec_eq(x_47, x_4);
if (x_48 == 0)
{
uint8_t x_49; 
x_49 = 1;
x_37 = x_45;
x_38 = x_49;
goto block_44;
}
else
{
uint8_t x_50; 
x_50 = 0;
x_37 = x_45;
x_38 = x_50;
goto block_44;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__byteToFlags___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel___private_CPU6502_0__byteToFlags(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_opcodeCycles(uint8_t x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; uint8_t x_4; 
x_2 = lean_uint8_to_nat(x_1);
x_3 = lean_unsigned_to_nat(169u);
x_4 = lean_nat_dec_eq(x_2, x_3);
if (x_4 == 0)
{
lean_object* x_5; uint8_t x_6; 
x_5 = lean_unsigned_to_nat(162u);
x_6 = lean_nat_dec_eq(x_2, x_5);
if (x_6 == 0)
{
lean_object* x_7; uint8_t x_8; 
x_7 = lean_unsigned_to_nat(160u);
x_8 = lean_nat_dec_eq(x_2, x_7);
if (x_8 == 0)
{
lean_object* x_9; uint8_t x_10; 
x_9 = lean_unsigned_to_nat(105u);
x_10 = lean_nat_dec_eq(x_2, x_9);
if (x_10 == 0)
{
lean_object* x_11; uint8_t x_12; 
x_11 = lean_unsigned_to_nat(233u);
x_12 = lean_nat_dec_eq(x_2, x_11);
if (x_12 == 0)
{
lean_object* x_13; uint8_t x_14; 
x_13 = lean_unsigned_to_nat(41u);
x_14 = lean_nat_dec_eq(x_2, x_13);
if (x_14 == 0)
{
lean_object* x_15; uint8_t x_16; 
x_15 = lean_unsigned_to_nat(9u);
x_16 = lean_nat_dec_eq(x_2, x_15);
if (x_16 == 0)
{
lean_object* x_17; uint8_t x_18; 
x_17 = lean_unsigned_to_nat(73u);
x_18 = lean_nat_dec_eq(x_2, x_17);
if (x_18 == 0)
{
lean_object* x_19; uint8_t x_20; 
x_19 = lean_unsigned_to_nat(201u);
x_20 = lean_nat_dec_eq(x_2, x_19);
if (x_20 == 0)
{
lean_object* x_21; uint8_t x_22; 
x_21 = lean_unsigned_to_nat(224u);
x_22 = lean_nat_dec_eq(x_2, x_21);
if (x_22 == 0)
{
lean_object* x_23; uint8_t x_24; 
x_23 = lean_unsigned_to_nat(192u);
x_24 = lean_nat_dec_eq(x_2, x_23);
if (x_24 == 0)
{
lean_object* x_25; uint8_t x_26; 
x_25 = lean_unsigned_to_nat(165u);
x_26 = lean_nat_dec_eq(x_2, x_25);
if (x_26 == 0)
{
lean_object* x_27; uint8_t x_28; 
x_27 = lean_unsigned_to_nat(166u);
x_28 = lean_nat_dec_eq(x_2, x_27);
if (x_28 == 0)
{
lean_object* x_29; uint8_t x_30; 
x_29 = lean_unsigned_to_nat(164u);
x_30 = lean_nat_dec_eq(x_2, x_29);
if (x_30 == 0)
{
lean_object* x_31; uint8_t x_32; 
x_31 = lean_unsigned_to_nat(101u);
x_32 = lean_nat_dec_eq(x_2, x_31);
if (x_32 == 0)
{
lean_object* x_33; uint8_t x_34; 
x_33 = lean_unsigned_to_nat(229u);
x_34 = lean_nat_dec_eq(x_2, x_33);
if (x_34 == 0)
{
lean_object* x_35; uint8_t x_36; 
x_35 = lean_unsigned_to_nat(37u);
x_36 = lean_nat_dec_eq(x_2, x_35);
if (x_36 == 0)
{
lean_object* x_37; uint8_t x_38; 
x_37 = lean_unsigned_to_nat(5u);
x_38 = lean_nat_dec_eq(x_2, x_37);
if (x_38 == 0)
{
lean_object* x_39; uint8_t x_40; 
x_39 = lean_unsigned_to_nat(69u);
x_40 = lean_nat_dec_eq(x_2, x_39);
if (x_40 == 0)
{
lean_object* x_41; uint8_t x_42; 
x_41 = lean_unsigned_to_nat(197u);
x_42 = lean_nat_dec_eq(x_2, x_41);
if (x_42 == 0)
{
lean_object* x_43; uint8_t x_44; 
x_43 = lean_unsigned_to_nat(228u);
x_44 = lean_nat_dec_eq(x_2, x_43);
if (x_44 == 0)
{
lean_object* x_45; uint8_t x_46; 
x_45 = lean_unsigned_to_nat(196u);
x_46 = lean_nat_dec_eq(x_2, x_45);
if (x_46 == 0)
{
lean_object* x_47; uint8_t x_48; 
x_47 = lean_unsigned_to_nat(36u);
x_48 = lean_nat_dec_eq(x_2, x_47);
if (x_48 == 0)
{
lean_object* x_49; uint8_t x_50; 
x_49 = lean_unsigned_to_nat(133u);
x_50 = lean_nat_dec_eq(x_2, x_49);
if (x_50 == 0)
{
lean_object* x_51; uint8_t x_52; 
x_51 = lean_unsigned_to_nat(134u);
x_52 = lean_nat_dec_eq(x_2, x_51);
if (x_52 == 0)
{
lean_object* x_53; uint8_t x_54; 
x_53 = lean_unsigned_to_nat(132u);
x_54 = lean_nat_dec_eq(x_2, x_53);
if (x_54 == 0)
{
lean_object* x_55; uint8_t x_56; 
x_55 = lean_unsigned_to_nat(181u);
x_56 = lean_nat_dec_eq(x_2, x_55);
if (x_56 == 0)
{
lean_object* x_57; uint8_t x_58; 
x_57 = lean_unsigned_to_nat(180u);
x_58 = lean_nat_dec_eq(x_2, x_57);
if (x_58 == 0)
{
lean_object* x_59; uint8_t x_60; 
x_59 = lean_unsigned_to_nat(182u);
x_60 = lean_nat_dec_eq(x_2, x_59);
if (x_60 == 0)
{
lean_object* x_61; uint8_t x_62; 
x_61 = lean_unsigned_to_nat(117u);
x_62 = lean_nat_dec_eq(x_2, x_61);
if (x_62 == 0)
{
lean_object* x_63; uint8_t x_64; 
x_63 = lean_unsigned_to_nat(245u);
x_64 = lean_nat_dec_eq(x_2, x_63);
if (x_64 == 0)
{
lean_object* x_65; uint8_t x_66; 
x_65 = lean_unsigned_to_nat(53u);
x_66 = lean_nat_dec_eq(x_2, x_65);
if (x_66 == 0)
{
lean_object* x_67; uint8_t x_68; 
x_67 = lean_unsigned_to_nat(21u);
x_68 = lean_nat_dec_eq(x_2, x_67);
if (x_68 == 0)
{
lean_object* x_69; uint8_t x_70; 
x_69 = lean_unsigned_to_nat(85u);
x_70 = lean_nat_dec_eq(x_2, x_69);
if (x_70 == 0)
{
lean_object* x_71; uint8_t x_72; 
x_71 = lean_unsigned_to_nat(213u);
x_72 = lean_nat_dec_eq(x_2, x_71);
if (x_72 == 0)
{
lean_object* x_73; uint8_t x_74; 
x_73 = lean_unsigned_to_nat(149u);
x_74 = lean_nat_dec_eq(x_2, x_73);
if (x_74 == 0)
{
lean_object* x_75; uint8_t x_76; 
x_75 = lean_unsigned_to_nat(148u);
x_76 = lean_nat_dec_eq(x_2, x_75);
if (x_76 == 0)
{
lean_object* x_77; uint8_t x_78; 
x_77 = lean_unsigned_to_nat(150u);
x_78 = lean_nat_dec_eq(x_2, x_77);
if (x_78 == 0)
{
lean_object* x_79; uint8_t x_80; 
x_79 = lean_unsigned_to_nat(173u);
x_80 = lean_nat_dec_eq(x_2, x_79);
if (x_80 == 0)
{
lean_object* x_81; uint8_t x_82; 
x_81 = lean_unsigned_to_nat(174u);
x_82 = lean_nat_dec_eq(x_2, x_81);
if (x_82 == 0)
{
lean_object* x_83; uint8_t x_84; 
x_83 = lean_unsigned_to_nat(172u);
x_84 = lean_nat_dec_eq(x_2, x_83);
if (x_84 == 0)
{
lean_object* x_85; uint8_t x_86; 
x_85 = lean_unsigned_to_nat(109u);
x_86 = lean_nat_dec_eq(x_2, x_85);
if (x_86 == 0)
{
lean_object* x_87; uint8_t x_88; 
x_87 = lean_unsigned_to_nat(237u);
x_88 = lean_nat_dec_eq(x_2, x_87);
if (x_88 == 0)
{
lean_object* x_89; uint8_t x_90; 
x_89 = lean_unsigned_to_nat(45u);
x_90 = lean_nat_dec_eq(x_2, x_89);
if (x_90 == 0)
{
lean_object* x_91; uint8_t x_92; 
x_91 = lean_unsigned_to_nat(13u);
x_92 = lean_nat_dec_eq(x_2, x_91);
if (x_92 == 0)
{
lean_object* x_93; uint8_t x_94; 
x_93 = lean_unsigned_to_nat(77u);
x_94 = lean_nat_dec_eq(x_2, x_93);
if (x_94 == 0)
{
lean_object* x_95; uint8_t x_96; 
x_95 = lean_unsigned_to_nat(205u);
x_96 = lean_nat_dec_eq(x_2, x_95);
if (x_96 == 0)
{
lean_object* x_97; uint8_t x_98; 
x_97 = lean_unsigned_to_nat(236u);
x_98 = lean_nat_dec_eq(x_2, x_97);
if (x_98 == 0)
{
lean_object* x_99; uint8_t x_100; 
x_99 = lean_unsigned_to_nat(204u);
x_100 = lean_nat_dec_eq(x_2, x_99);
if (x_100 == 0)
{
lean_object* x_101; uint8_t x_102; 
x_101 = lean_unsigned_to_nat(44u);
x_102 = lean_nat_dec_eq(x_2, x_101);
if (x_102 == 0)
{
lean_object* x_103; uint8_t x_104; 
x_103 = lean_unsigned_to_nat(141u);
x_104 = lean_nat_dec_eq(x_2, x_103);
if (x_104 == 0)
{
lean_object* x_105; uint8_t x_106; 
x_105 = lean_unsigned_to_nat(142u);
x_106 = lean_nat_dec_eq(x_2, x_105);
if (x_106 == 0)
{
lean_object* x_107; uint8_t x_108; 
x_107 = lean_unsigned_to_nat(140u);
x_108 = lean_nat_dec_eq(x_2, x_107);
if (x_108 == 0)
{
lean_object* x_109; uint8_t x_110; 
x_109 = lean_unsigned_to_nat(189u);
x_110 = lean_nat_dec_eq(x_2, x_109);
if (x_110 == 0)
{
lean_object* x_111; uint8_t x_112; 
x_111 = lean_unsigned_to_nat(188u);
x_112 = lean_nat_dec_eq(x_2, x_111);
if (x_112 == 0)
{
lean_object* x_113; uint8_t x_114; 
x_113 = lean_unsigned_to_nat(190u);
x_114 = lean_nat_dec_eq(x_2, x_113);
if (x_114 == 0)
{
lean_object* x_115; uint8_t x_116; 
x_115 = lean_unsigned_to_nat(125u);
x_116 = lean_nat_dec_eq(x_2, x_115);
if (x_116 == 0)
{
lean_object* x_117; uint8_t x_118; 
x_117 = lean_unsigned_to_nat(253u);
x_118 = lean_nat_dec_eq(x_2, x_117);
if (x_118 == 0)
{
lean_object* x_119; uint8_t x_120; 
x_119 = lean_unsigned_to_nat(61u);
x_120 = lean_nat_dec_eq(x_2, x_119);
if (x_120 == 0)
{
lean_object* x_121; uint8_t x_122; 
x_121 = lean_unsigned_to_nat(29u);
x_122 = lean_nat_dec_eq(x_2, x_121);
if (x_122 == 0)
{
lean_object* x_123; uint8_t x_124; 
x_123 = lean_unsigned_to_nat(93u);
x_124 = lean_nat_dec_eq(x_2, x_123);
if (x_124 == 0)
{
lean_object* x_125; uint8_t x_126; 
x_125 = lean_unsigned_to_nat(221u);
x_126 = lean_nat_dec_eq(x_2, x_125);
if (x_126 == 0)
{
lean_object* x_127; uint8_t x_128; 
x_127 = lean_unsigned_to_nat(185u);
x_128 = lean_nat_dec_eq(x_2, x_127);
if (x_128 == 0)
{
lean_object* x_129; uint8_t x_130; 
x_129 = lean_unsigned_to_nat(121u);
x_130 = lean_nat_dec_eq(x_2, x_129);
if (x_130 == 0)
{
lean_object* x_131; uint8_t x_132; 
x_131 = lean_unsigned_to_nat(249u);
x_132 = lean_nat_dec_eq(x_2, x_131);
if (x_132 == 0)
{
lean_object* x_133; uint8_t x_134; 
x_133 = lean_unsigned_to_nat(57u);
x_134 = lean_nat_dec_eq(x_2, x_133);
if (x_134 == 0)
{
lean_object* x_135; uint8_t x_136; 
x_135 = lean_unsigned_to_nat(25u);
x_136 = lean_nat_dec_eq(x_2, x_135);
if (x_136 == 0)
{
lean_object* x_137; uint8_t x_138; 
x_137 = lean_unsigned_to_nat(89u);
x_138 = lean_nat_dec_eq(x_2, x_137);
if (x_138 == 0)
{
lean_object* x_139; uint8_t x_140; 
x_139 = lean_unsigned_to_nat(217u);
x_140 = lean_nat_dec_eq(x_2, x_139);
if (x_140 == 0)
{
lean_object* x_141; uint8_t x_142; 
x_141 = lean_unsigned_to_nat(157u);
x_142 = lean_nat_dec_eq(x_2, x_141);
if (x_142 == 0)
{
lean_object* x_143; uint8_t x_144; 
x_143 = lean_unsigned_to_nat(153u);
x_144 = lean_nat_dec_eq(x_2, x_143);
if (x_144 == 0)
{
lean_object* x_145; uint8_t x_146; 
x_145 = lean_unsigned_to_nat(161u);
x_146 = lean_nat_dec_eq(x_2, x_145);
if (x_146 == 0)
{
lean_object* x_147; uint8_t x_148; 
x_147 = lean_unsigned_to_nat(97u);
x_148 = lean_nat_dec_eq(x_2, x_147);
if (x_148 == 0)
{
lean_object* x_149; uint8_t x_150; 
x_149 = lean_unsigned_to_nat(225u);
x_150 = lean_nat_dec_eq(x_2, x_149);
if (x_150 == 0)
{
lean_object* x_151; uint8_t x_152; 
x_151 = lean_unsigned_to_nat(33u);
x_152 = lean_nat_dec_eq(x_2, x_151);
if (x_152 == 0)
{
lean_object* x_153; uint8_t x_154; 
x_153 = lean_unsigned_to_nat(1u);
x_154 = lean_nat_dec_eq(x_2, x_153);
if (x_154 == 0)
{
lean_object* x_155; uint8_t x_156; 
x_155 = lean_unsigned_to_nat(65u);
x_156 = lean_nat_dec_eq(x_2, x_155);
if (x_156 == 0)
{
lean_object* x_157; uint8_t x_158; 
x_157 = lean_unsigned_to_nat(193u);
x_158 = lean_nat_dec_eq(x_2, x_157);
if (x_158 == 0)
{
lean_object* x_159; uint8_t x_160; 
x_159 = lean_unsigned_to_nat(129u);
x_160 = lean_nat_dec_eq(x_2, x_159);
if (x_160 == 0)
{
lean_object* x_161; uint8_t x_162; 
x_161 = lean_unsigned_to_nat(177u);
x_162 = lean_nat_dec_eq(x_2, x_161);
if (x_162 == 0)
{
lean_object* x_163; uint8_t x_164; 
x_163 = lean_unsigned_to_nat(113u);
x_164 = lean_nat_dec_eq(x_2, x_163);
if (x_164 == 0)
{
lean_object* x_165; uint8_t x_166; 
x_165 = lean_unsigned_to_nat(241u);
x_166 = lean_nat_dec_eq(x_2, x_165);
if (x_166 == 0)
{
lean_object* x_167; uint8_t x_168; 
x_167 = lean_unsigned_to_nat(49u);
x_168 = lean_nat_dec_eq(x_2, x_167);
if (x_168 == 0)
{
lean_object* x_169; uint8_t x_170; 
x_169 = lean_unsigned_to_nat(17u);
x_170 = lean_nat_dec_eq(x_2, x_169);
if (x_170 == 0)
{
lean_object* x_171; uint8_t x_172; 
x_171 = lean_unsigned_to_nat(81u);
x_172 = lean_nat_dec_eq(x_2, x_171);
if (x_172 == 0)
{
lean_object* x_173; uint8_t x_174; 
x_173 = lean_unsigned_to_nat(209u);
x_174 = lean_nat_dec_eq(x_2, x_173);
if (x_174 == 0)
{
lean_object* x_175; uint8_t x_176; 
x_175 = lean_unsigned_to_nat(145u);
x_176 = lean_nat_dec_eq(x_2, x_175);
if (x_176 == 0)
{
lean_object* x_177; uint8_t x_178; 
x_177 = lean_unsigned_to_nat(230u);
x_178 = lean_nat_dec_eq(x_2, x_177);
if (x_178 == 0)
{
lean_object* x_179; uint8_t x_180; 
x_179 = lean_unsigned_to_nat(198u);
x_180 = lean_nat_dec_eq(x_2, x_179);
if (x_180 == 0)
{
lean_object* x_181; uint8_t x_182; 
x_181 = lean_unsigned_to_nat(246u);
x_182 = lean_nat_dec_eq(x_2, x_181);
if (x_182 == 0)
{
lean_object* x_183; uint8_t x_184; 
x_183 = lean_unsigned_to_nat(214u);
x_184 = lean_nat_dec_eq(x_2, x_183);
if (x_184 == 0)
{
lean_object* x_185; uint8_t x_186; 
x_185 = lean_unsigned_to_nat(238u);
x_186 = lean_nat_dec_eq(x_2, x_185);
if (x_186 == 0)
{
lean_object* x_187; uint8_t x_188; 
x_187 = lean_unsigned_to_nat(206u);
x_188 = lean_nat_dec_eq(x_2, x_187);
if (x_188 == 0)
{
lean_object* x_189; uint8_t x_190; 
x_189 = lean_unsigned_to_nat(254u);
x_190 = lean_nat_dec_eq(x_2, x_189);
if (x_190 == 0)
{
lean_object* x_191; uint8_t x_192; 
x_191 = lean_unsigned_to_nat(222u);
x_192 = lean_nat_dec_eq(x_2, x_191);
if (x_192 == 0)
{
lean_object* x_193; uint8_t x_194; 
x_193 = lean_unsigned_to_nat(232u);
x_194 = lean_nat_dec_eq(x_2, x_193);
if (x_194 == 0)
{
lean_object* x_195; uint8_t x_196; 
x_195 = lean_unsigned_to_nat(202u);
x_196 = lean_nat_dec_eq(x_2, x_195);
if (x_196 == 0)
{
lean_object* x_197; uint8_t x_198; 
x_197 = lean_unsigned_to_nat(200u);
x_198 = lean_nat_dec_eq(x_2, x_197);
if (x_198 == 0)
{
lean_object* x_199; uint8_t x_200; 
x_199 = lean_unsigned_to_nat(136u);
x_200 = lean_nat_dec_eq(x_2, x_199);
if (x_200 == 0)
{
lean_object* x_201; uint8_t x_202; 
x_201 = lean_unsigned_to_nat(170u);
x_202 = lean_nat_dec_eq(x_2, x_201);
if (x_202 == 0)
{
lean_object* x_203; uint8_t x_204; 
x_203 = lean_unsigned_to_nat(168u);
x_204 = lean_nat_dec_eq(x_2, x_203);
if (x_204 == 0)
{
lean_object* x_205; uint8_t x_206; 
x_205 = lean_unsigned_to_nat(138u);
x_206 = lean_nat_dec_eq(x_2, x_205);
if (x_206 == 0)
{
lean_object* x_207; uint8_t x_208; 
x_207 = lean_unsigned_to_nat(152u);
x_208 = lean_nat_dec_eq(x_2, x_207);
if (x_208 == 0)
{
lean_object* x_209; uint8_t x_210; 
x_209 = lean_unsigned_to_nat(186u);
x_210 = lean_nat_dec_eq(x_2, x_209);
if (x_210 == 0)
{
lean_object* x_211; uint8_t x_212; 
x_211 = lean_unsigned_to_nat(154u);
x_212 = lean_nat_dec_eq(x_2, x_211);
if (x_212 == 0)
{
lean_object* x_213; uint8_t x_214; 
x_213 = lean_unsigned_to_nat(24u);
x_214 = lean_nat_dec_eq(x_2, x_213);
if (x_214 == 0)
{
lean_object* x_215; uint8_t x_216; 
x_215 = lean_unsigned_to_nat(56u);
x_216 = lean_nat_dec_eq(x_2, x_215);
if (x_216 == 0)
{
lean_object* x_217; uint8_t x_218; 
x_217 = lean_unsigned_to_nat(88u);
x_218 = lean_nat_dec_eq(x_2, x_217);
if (x_218 == 0)
{
lean_object* x_219; uint8_t x_220; 
x_219 = lean_unsigned_to_nat(120u);
x_220 = lean_nat_dec_eq(x_2, x_219);
if (x_220 == 0)
{
lean_object* x_221; uint8_t x_222; 
x_221 = lean_unsigned_to_nat(184u);
x_222 = lean_nat_dec_eq(x_2, x_221);
if (x_222 == 0)
{
lean_object* x_223; uint8_t x_224; 
x_223 = lean_unsigned_to_nat(216u);
x_224 = lean_nat_dec_eq(x_2, x_223);
if (x_224 == 0)
{
lean_object* x_225; uint8_t x_226; 
x_225 = lean_unsigned_to_nat(248u);
x_226 = lean_nat_dec_eq(x_2, x_225);
if (x_226 == 0)
{
lean_object* x_227; uint8_t x_228; 
x_227 = lean_unsigned_to_nat(234u);
x_228 = lean_nat_dec_eq(x_2, x_227);
if (x_228 == 0)
{
lean_object* x_229; uint8_t x_230; 
x_229 = lean_unsigned_to_nat(10u);
x_230 = lean_nat_dec_eq(x_2, x_229);
if (x_230 == 0)
{
lean_object* x_231; uint8_t x_232; 
x_231 = lean_unsigned_to_nat(74u);
x_232 = lean_nat_dec_eq(x_2, x_231);
if (x_232 == 0)
{
lean_object* x_233; uint8_t x_234; 
x_233 = lean_unsigned_to_nat(42u);
x_234 = lean_nat_dec_eq(x_2, x_233);
if (x_234 == 0)
{
lean_object* x_235; uint8_t x_236; 
x_235 = lean_unsigned_to_nat(106u);
x_236 = lean_nat_dec_eq(x_2, x_235);
if (x_236 == 0)
{
lean_object* x_237; uint8_t x_238; 
x_237 = lean_unsigned_to_nat(6u);
x_238 = lean_nat_dec_eq(x_2, x_237);
if (x_238 == 0)
{
lean_object* x_239; uint8_t x_240; 
x_239 = lean_unsigned_to_nat(70u);
x_240 = lean_nat_dec_eq(x_2, x_239);
if (x_240 == 0)
{
lean_object* x_241; uint8_t x_242; 
x_241 = lean_unsigned_to_nat(38u);
x_242 = lean_nat_dec_eq(x_2, x_241);
if (x_242 == 0)
{
lean_object* x_243; uint8_t x_244; 
x_243 = lean_unsigned_to_nat(102u);
x_244 = lean_nat_dec_eq(x_2, x_243);
if (x_244 == 0)
{
lean_object* x_245; uint8_t x_246; 
x_245 = lean_unsigned_to_nat(22u);
x_246 = lean_nat_dec_eq(x_2, x_245);
if (x_246 == 0)
{
lean_object* x_247; uint8_t x_248; 
x_247 = lean_unsigned_to_nat(86u);
x_248 = lean_nat_dec_eq(x_2, x_247);
if (x_248 == 0)
{
lean_object* x_249; uint8_t x_250; 
x_249 = lean_unsigned_to_nat(54u);
x_250 = lean_nat_dec_eq(x_2, x_249);
if (x_250 == 0)
{
lean_object* x_251; uint8_t x_252; 
x_251 = lean_unsigned_to_nat(118u);
x_252 = lean_nat_dec_eq(x_2, x_251);
if (x_252 == 0)
{
lean_object* x_253; uint8_t x_254; 
x_253 = lean_unsigned_to_nat(14u);
x_254 = lean_nat_dec_eq(x_2, x_253);
if (x_254 == 0)
{
lean_object* x_255; uint8_t x_256; 
x_255 = lean_unsigned_to_nat(78u);
x_256 = lean_nat_dec_eq(x_2, x_255);
if (x_256 == 0)
{
lean_object* x_257; uint8_t x_258; 
x_257 = lean_unsigned_to_nat(46u);
x_258 = lean_nat_dec_eq(x_2, x_257);
if (x_258 == 0)
{
lean_object* x_259; uint8_t x_260; 
x_259 = lean_unsigned_to_nat(110u);
x_260 = lean_nat_dec_eq(x_2, x_259);
if (x_260 == 0)
{
lean_object* x_261; uint8_t x_262; 
x_261 = lean_unsigned_to_nat(30u);
x_262 = lean_nat_dec_eq(x_2, x_261);
if (x_262 == 0)
{
lean_object* x_263; uint8_t x_264; 
x_263 = lean_unsigned_to_nat(94u);
x_264 = lean_nat_dec_eq(x_2, x_263);
if (x_264 == 0)
{
lean_object* x_265; uint8_t x_266; 
x_265 = lean_unsigned_to_nat(62u);
x_266 = lean_nat_dec_eq(x_2, x_265);
if (x_266 == 0)
{
lean_object* x_267; uint8_t x_268; 
x_267 = lean_unsigned_to_nat(126u);
x_268 = lean_nat_dec_eq(x_2, x_267);
if (x_268 == 0)
{
lean_object* x_269; uint8_t x_270; 
x_269 = lean_unsigned_to_nat(144u);
x_270 = lean_nat_dec_eq(x_2, x_269);
if (x_270 == 0)
{
lean_object* x_271; uint8_t x_272; 
x_271 = lean_unsigned_to_nat(176u);
x_272 = lean_nat_dec_eq(x_2, x_271);
if (x_272 == 0)
{
lean_object* x_273; uint8_t x_274; 
x_273 = lean_unsigned_to_nat(240u);
x_274 = lean_nat_dec_eq(x_2, x_273);
if (x_274 == 0)
{
lean_object* x_275; uint8_t x_276; 
x_275 = lean_unsigned_to_nat(208u);
x_276 = lean_nat_dec_eq(x_2, x_275);
if (x_276 == 0)
{
lean_object* x_277; uint8_t x_278; 
x_277 = lean_unsigned_to_nat(48u);
x_278 = lean_nat_dec_eq(x_2, x_277);
if (x_278 == 0)
{
lean_object* x_279; uint8_t x_280; 
x_279 = lean_unsigned_to_nat(16u);
x_280 = lean_nat_dec_eq(x_2, x_279);
if (x_280 == 0)
{
lean_object* x_281; uint8_t x_282; 
x_281 = lean_unsigned_to_nat(80u);
x_282 = lean_nat_dec_eq(x_2, x_281);
if (x_282 == 0)
{
lean_object* x_283; uint8_t x_284; 
x_283 = lean_unsigned_to_nat(112u);
x_284 = lean_nat_dec_eq(x_2, x_283);
if (x_284 == 0)
{
lean_object* x_285; uint8_t x_286; 
x_285 = lean_unsigned_to_nat(76u);
x_286 = lean_nat_dec_eq(x_2, x_285);
if (x_286 == 0)
{
lean_object* x_287; uint8_t x_288; 
x_287 = lean_unsigned_to_nat(108u);
x_288 = lean_nat_dec_eq(x_2, x_287);
if (x_288 == 0)
{
lean_object* x_289; uint8_t x_290; 
x_289 = lean_unsigned_to_nat(32u);
x_290 = lean_nat_dec_eq(x_2, x_289);
if (x_290 == 0)
{
lean_object* x_291; uint8_t x_292; 
x_291 = lean_unsigned_to_nat(96u);
x_292 = lean_nat_dec_eq(x_2, x_291);
if (x_292 == 0)
{
lean_object* x_293; uint8_t x_294; 
x_293 = lean_unsigned_to_nat(64u);
x_294 = lean_nat_dec_eq(x_2, x_293);
if (x_294 == 0)
{
lean_object* x_295; uint8_t x_296; 
x_295 = lean_unsigned_to_nat(72u);
x_296 = lean_nat_dec_eq(x_2, x_295);
if (x_296 == 0)
{
lean_object* x_297; uint8_t x_298; 
x_297 = lean_unsigned_to_nat(8u);
x_298 = lean_nat_dec_eq(x_2, x_297);
if (x_298 == 0)
{
lean_object* x_299; uint8_t x_300; 
x_299 = lean_unsigned_to_nat(104u);
x_300 = lean_nat_dec_eq(x_2, x_299);
if (x_300 == 0)
{
lean_object* x_301; uint8_t x_302; 
x_301 = lean_unsigned_to_nat(40u);
x_302 = lean_nat_dec_eq(x_2, x_301);
if (x_302 == 0)
{
lean_object* x_303; uint8_t x_304; 
x_303 = lean_unsigned_to_nat(0u);
x_304 = lean_nat_dec_eq(x_2, x_303);
if (x_304 == 0)
{
lean_object* x_305; 
x_305 = lean_unsigned_to_nat(2u);
return x_305;
}
else
{
lean_object* x_306; 
x_306 = lean_unsigned_to_nat(7u);
return x_306;
}
}
else
{
lean_object* x_307; 
x_307 = lean_unsigned_to_nat(4u);
return x_307;
}
}
else
{
lean_object* x_308; 
x_308 = lean_unsigned_to_nat(4u);
return x_308;
}
}
else
{
lean_object* x_309; 
x_309 = lean_unsigned_to_nat(3u);
return x_309;
}
}
else
{
lean_object* x_310; 
x_310 = lean_unsigned_to_nat(3u);
return x_310;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_37;
}
}
else
{
lean_object* x_311; 
x_311 = lean_unsigned_to_nat(3u);
return x_311;
}
}
else
{
lean_object* x_312; 
x_312 = lean_unsigned_to_nat(2u);
return x_312;
}
}
else
{
lean_object* x_313; 
x_313 = lean_unsigned_to_nat(2u);
return x_313;
}
}
else
{
lean_object* x_314; 
x_314 = lean_unsigned_to_nat(2u);
return x_314;
}
}
else
{
lean_object* x_315; 
x_315 = lean_unsigned_to_nat(2u);
return x_315;
}
}
else
{
lean_object* x_316; 
x_316 = lean_unsigned_to_nat(2u);
return x_316;
}
}
else
{
lean_object* x_317; 
x_317 = lean_unsigned_to_nat(2u);
return x_317;
}
}
else
{
lean_object* x_318; 
x_318 = lean_unsigned_to_nat(2u);
return x_318;
}
}
else
{
lean_object* x_319; 
x_319 = lean_unsigned_to_nat(2u);
return x_319;
}
}
else
{
lean_object* x_320; 
x_320 = lean_unsigned_to_nat(7u);
return x_320;
}
}
else
{
lean_object* x_321; 
x_321 = lean_unsigned_to_nat(7u);
return x_321;
}
}
else
{
lean_object* x_322; 
x_322 = lean_unsigned_to_nat(7u);
return x_322;
}
}
else
{
lean_object* x_323; 
x_323 = lean_unsigned_to_nat(7u);
return x_323;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_237;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
lean_object* x_324; 
x_324 = lean_unsigned_to_nat(2u);
return x_324;
}
}
else
{
lean_object* x_325; 
x_325 = lean_unsigned_to_nat(2u);
return x_325;
}
}
else
{
lean_object* x_326; 
x_326 = lean_unsigned_to_nat(2u);
return x_326;
}
}
else
{
lean_object* x_327; 
x_327 = lean_unsigned_to_nat(2u);
return x_327;
}
}
else
{
lean_object* x_328; 
x_328 = lean_unsigned_to_nat(2u);
return x_328;
}
}
else
{
lean_object* x_329; 
x_329 = lean_unsigned_to_nat(2u);
return x_329;
}
}
else
{
lean_object* x_330; 
x_330 = lean_unsigned_to_nat(2u);
return x_330;
}
}
else
{
lean_object* x_331; 
x_331 = lean_unsigned_to_nat(2u);
return x_331;
}
}
else
{
lean_object* x_332; 
x_332 = lean_unsigned_to_nat(2u);
return x_332;
}
}
else
{
lean_object* x_333; 
x_333 = lean_unsigned_to_nat(2u);
return x_333;
}
}
else
{
lean_object* x_334; 
x_334 = lean_unsigned_to_nat(2u);
return x_334;
}
}
else
{
lean_object* x_335; 
x_335 = lean_unsigned_to_nat(2u);
return x_335;
}
}
else
{
lean_object* x_336; 
x_336 = lean_unsigned_to_nat(2u);
return x_336;
}
}
else
{
lean_object* x_337; 
x_337 = lean_unsigned_to_nat(2u);
return x_337;
}
}
else
{
lean_object* x_338; 
x_338 = lean_unsigned_to_nat(2u);
return x_338;
}
}
else
{
lean_object* x_339; 
x_339 = lean_unsigned_to_nat(2u);
return x_339;
}
}
else
{
lean_object* x_340; 
x_340 = lean_unsigned_to_nat(2u);
return x_340;
}
}
else
{
lean_object* x_341; 
x_341 = lean_unsigned_to_nat(2u);
return x_341;
}
}
else
{
lean_object* x_342; 
x_342 = lean_unsigned_to_nat(2u);
return x_342;
}
}
else
{
lean_object* x_343; 
x_343 = lean_unsigned_to_nat(2u);
return x_343;
}
}
else
{
lean_object* x_344; 
x_344 = lean_unsigned_to_nat(2u);
return x_344;
}
}
else
{
lean_object* x_345; 
x_345 = lean_unsigned_to_nat(2u);
return x_345;
}
}
else
{
lean_object* x_346; 
x_346 = lean_unsigned_to_nat(7u);
return x_346;
}
}
else
{
lean_object* x_347; 
x_347 = lean_unsigned_to_nat(7u);
return x_347;
}
}
else
{
lean_object* x_348; 
x_348 = lean_unsigned_to_nat(6u);
return x_348;
}
}
else
{
lean_object* x_349; 
x_349 = lean_unsigned_to_nat(6u);
return x_349;
}
}
else
{
lean_object* x_350; 
x_350 = lean_unsigned_to_nat(6u);
return x_350;
}
}
else
{
lean_object* x_351; 
x_351 = lean_unsigned_to_nat(6u);
return x_351;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
lean_object* x_352; 
x_352 = lean_unsigned_to_nat(6u);
return x_352;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
lean_object* x_353; 
x_353 = lean_unsigned_to_nat(6u);
return x_353;
}
}
else
{
lean_object* x_354; 
x_354 = lean_unsigned_to_nat(6u);
return x_354;
}
}
else
{
lean_object* x_355; 
x_355 = lean_unsigned_to_nat(6u);
return x_355;
}
}
else
{
lean_object* x_356; 
x_356 = lean_unsigned_to_nat(6u);
return x_356;
}
}
else
{
lean_object* x_357; 
x_357 = lean_unsigned_to_nat(6u);
return x_357;
}
}
else
{
lean_object* x_358; 
x_358 = lean_unsigned_to_nat(6u);
return x_358;
}
}
else
{
lean_object* x_359; 
x_359 = lean_unsigned_to_nat(6u);
return x_359;
}
}
else
{
lean_object* x_360; 
x_360 = lean_unsigned_to_nat(6u);
return x_360;
}
}
else
{
return x_37;
}
}
else
{
return x_37;
}
}
else
{
lean_object* x_361; 
x_361 = lean_unsigned_to_nat(4u);
return x_361;
}
}
else
{
lean_object* x_362; 
x_362 = lean_unsigned_to_nat(4u);
return x_362;
}
}
else
{
lean_object* x_363; 
x_363 = lean_unsigned_to_nat(4u);
return x_363;
}
}
else
{
lean_object* x_364; 
x_364 = lean_unsigned_to_nat(4u);
return x_364;
}
}
else
{
lean_object* x_365; 
x_365 = lean_unsigned_to_nat(4u);
return x_365;
}
}
else
{
lean_object* x_366; 
x_366 = lean_unsigned_to_nat(4u);
return x_366;
}
}
else
{
lean_object* x_367; 
x_367 = lean_unsigned_to_nat(4u);
return x_367;
}
}
else
{
lean_object* x_368; 
x_368 = lean_unsigned_to_nat(4u);
return x_368;
}
}
else
{
lean_object* x_369; 
x_369 = lean_unsigned_to_nat(4u);
return x_369;
}
}
else
{
lean_object* x_370; 
x_370 = lean_unsigned_to_nat(4u);
return x_370;
}
}
else
{
lean_object* x_371; 
x_371 = lean_unsigned_to_nat(4u);
return x_371;
}
}
else
{
lean_object* x_372; 
x_372 = lean_unsigned_to_nat(4u);
return x_372;
}
}
else
{
lean_object* x_373; 
x_373 = lean_unsigned_to_nat(4u);
return x_373;
}
}
else
{
lean_object* x_374; 
x_374 = lean_unsigned_to_nat(4u);
return x_374;
}
}
else
{
lean_object* x_375; 
x_375 = lean_unsigned_to_nat(4u);
return x_375;
}
}
else
{
lean_object* x_376; 
x_376 = lean_unsigned_to_nat(4u);
return x_376;
}
}
else
{
lean_object* x_377; 
x_377 = lean_unsigned_to_nat(4u);
return x_377;
}
}
else
{
lean_object* x_378; 
x_378 = lean_unsigned_to_nat(4u);
return x_378;
}
}
else
{
lean_object* x_379; 
x_379 = lean_unsigned_to_nat(4u);
return x_379;
}
}
else
{
lean_object* x_380; 
x_380 = lean_unsigned_to_nat(4u);
return x_380;
}
}
else
{
lean_object* x_381; 
x_381 = lean_unsigned_to_nat(4u);
return x_381;
}
}
else
{
lean_object* x_382; 
x_382 = lean_unsigned_to_nat(4u);
return x_382;
}
}
else
{
lean_object* x_383; 
x_383 = lean_unsigned_to_nat(4u);
return x_383;
}
}
else
{
lean_object* x_384; 
x_384 = lean_unsigned_to_nat(4u);
return x_384;
}
}
else
{
lean_object* x_385; 
x_385 = lean_unsigned_to_nat(4u);
return x_385;
}
}
else
{
lean_object* x_386; 
x_386 = lean_unsigned_to_nat(4u);
return x_386;
}
}
else
{
lean_object* x_387; 
x_387 = lean_unsigned_to_nat(4u);
return x_387;
}
}
else
{
lean_object* x_388; 
x_388 = lean_unsigned_to_nat(4u);
return x_388;
}
}
else
{
lean_object* x_389; 
x_389 = lean_unsigned_to_nat(4u);
return x_389;
}
}
else
{
lean_object* x_390; 
x_390 = lean_unsigned_to_nat(4u);
return x_390;
}
}
else
{
lean_object* x_391; 
x_391 = lean_unsigned_to_nat(4u);
return x_391;
}
}
else
{
lean_object* x_392; 
x_392 = lean_unsigned_to_nat(4u);
return x_392;
}
}
else
{
lean_object* x_393; 
x_393 = lean_unsigned_to_nat(4u);
return x_393;
}
}
else
{
lean_object* x_394; 
x_394 = lean_unsigned_to_nat(4u);
return x_394;
}
}
else
{
lean_object* x_395; 
x_395 = lean_unsigned_to_nat(4u);
return x_395;
}
}
else
{
lean_object* x_396; 
x_396 = lean_unsigned_to_nat(4u);
return x_396;
}
}
else
{
lean_object* x_397; 
x_397 = lean_unsigned_to_nat(4u);
return x_397;
}
}
else
{
lean_object* x_398; 
x_398 = lean_unsigned_to_nat(4u);
return x_398;
}
}
else
{
lean_object* x_399; 
x_399 = lean_unsigned_to_nat(4u);
return x_399;
}
}
else
{
lean_object* x_400; 
x_400 = lean_unsigned_to_nat(4u);
return x_400;
}
}
else
{
lean_object* x_401; 
x_401 = lean_unsigned_to_nat(4u);
return x_401;
}
}
else
{
lean_object* x_402; 
x_402 = lean_unsigned_to_nat(4u);
return x_402;
}
}
else
{
lean_object* x_403; 
x_403 = lean_unsigned_to_nat(4u);
return x_403;
}
}
else
{
lean_object* x_404; 
x_404 = lean_unsigned_to_nat(3u);
return x_404;
}
}
else
{
lean_object* x_405; 
x_405 = lean_unsigned_to_nat(3u);
return x_405;
}
}
else
{
lean_object* x_406; 
x_406 = lean_unsigned_to_nat(3u);
return x_406;
}
}
else
{
lean_object* x_407; 
x_407 = lean_unsigned_to_nat(3u);
return x_407;
}
}
else
{
lean_object* x_408; 
x_408 = lean_unsigned_to_nat(3u);
return x_408;
}
}
else
{
lean_object* x_409; 
x_409 = lean_unsigned_to_nat(3u);
return x_409;
}
}
else
{
lean_object* x_410; 
x_410 = lean_unsigned_to_nat(3u);
return x_410;
}
}
else
{
lean_object* x_411; 
x_411 = lean_unsigned_to_nat(3u);
return x_411;
}
}
else
{
lean_object* x_412; 
x_412 = lean_unsigned_to_nat(3u);
return x_412;
}
}
else
{
lean_object* x_413; 
x_413 = lean_unsigned_to_nat(3u);
return x_413;
}
}
else
{
lean_object* x_414; 
x_414 = lean_unsigned_to_nat(3u);
return x_414;
}
}
else
{
lean_object* x_415; 
x_415 = lean_unsigned_to_nat(3u);
return x_415;
}
}
else
{
lean_object* x_416; 
x_416 = lean_unsigned_to_nat(3u);
return x_416;
}
}
else
{
lean_object* x_417; 
x_417 = lean_unsigned_to_nat(3u);
return x_417;
}
}
else
{
lean_object* x_418; 
x_418 = lean_unsigned_to_nat(3u);
return x_418;
}
}
else
{
lean_object* x_419; 
x_419 = lean_unsigned_to_nat(2u);
return x_419;
}
}
else
{
lean_object* x_420; 
x_420 = lean_unsigned_to_nat(2u);
return x_420;
}
}
else
{
lean_object* x_421; 
x_421 = lean_unsigned_to_nat(2u);
return x_421;
}
}
else
{
lean_object* x_422; 
x_422 = lean_unsigned_to_nat(2u);
return x_422;
}
}
else
{
lean_object* x_423; 
x_423 = lean_unsigned_to_nat(2u);
return x_423;
}
}
else
{
lean_object* x_424; 
x_424 = lean_unsigned_to_nat(2u);
return x_424;
}
}
else
{
lean_object* x_425; 
x_425 = lean_unsigned_to_nat(2u);
return x_425;
}
}
else
{
lean_object* x_426; 
x_426 = lean_unsigned_to_nat(2u);
return x_426;
}
}
else
{
lean_object* x_427; 
x_427 = lean_unsigned_to_nat(2u);
return x_427;
}
}
else
{
lean_object* x_428; 
x_428 = lean_unsigned_to_nat(2u);
return x_428;
}
}
else
{
lean_object* x_429; 
x_429 = lean_unsigned_to_nat(2u);
return x_429;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_opcodeCycles___boxed(lean_object* x_1) {
_start:
{
uint8_t x_2; lean_object* x_3; 
x_2 = lean_unbox(x_1);
x_3 = lp_dasmodel_opcodeCycles(x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_stepRaw(lean_object* x_1) {
_start:
{
uint8_t x_2; uint8_t x_3; uint8_t x_4; uint8_t x_5; uint16_t x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_10; lean_object* x_11; lean_object* x_12; uint8_t x_13; 
x_2 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_3 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_4 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_5 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_6 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_7 = lean_ctor_get(x_1, 0);
lean_inc_ref(x_7);
x_8 = lean_ctor_get(x_1, 1);
x_9 = lean_ctor_get(x_1, 2);
x_10 = lp_dasmodel_CPU_read(x_1, x_6);
x_11 = lean_uint8_to_nat(x_10);
x_12 = lean_unsigned_to_nat(169u);
x_13 = lean_nat_dec_eq(x_11, x_12);
if (x_13 == 0)
{
lean_object* x_14; uint8_t x_15; 
x_14 = lean_unsigned_to_nat(165u);
x_15 = lean_nat_dec_eq(x_11, x_14);
if (x_15 == 0)
{
lean_object* x_16; uint8_t x_17; 
x_16 = lean_unsigned_to_nat(181u);
x_17 = lean_nat_dec_eq(x_11, x_16);
if (x_17 == 0)
{
lean_object* x_18; uint8_t x_19; 
x_18 = lean_unsigned_to_nat(173u);
x_19 = lean_nat_dec_eq(x_11, x_18);
if (x_19 == 0)
{
lean_object* x_20; uint8_t x_21; 
x_20 = lean_unsigned_to_nat(189u);
x_21 = lean_nat_dec_eq(x_11, x_20);
if (x_21 == 0)
{
lean_object* x_22; uint8_t x_23; 
x_22 = lean_unsigned_to_nat(185u);
x_23 = lean_nat_dec_eq(x_11, x_22);
if (x_23 == 0)
{
lean_object* x_24; uint8_t x_25; 
x_24 = lean_unsigned_to_nat(161u);
x_25 = lean_nat_dec_eq(x_11, x_24);
if (x_25 == 0)
{
lean_object* x_26; uint8_t x_27; 
x_26 = lean_unsigned_to_nat(177u);
x_27 = lean_nat_dec_eq(x_11, x_26);
if (x_27 == 0)
{
lean_object* x_28; uint8_t x_29; 
x_28 = lean_unsigned_to_nat(162u);
x_29 = lean_nat_dec_eq(x_11, x_28);
if (x_29 == 0)
{
lean_object* x_30; uint8_t x_31; 
x_30 = lean_unsigned_to_nat(166u);
x_31 = lean_nat_dec_eq(x_11, x_30);
if (x_31 == 0)
{
lean_object* x_32; uint8_t x_33; 
x_32 = lean_unsigned_to_nat(182u);
x_33 = lean_nat_dec_eq(x_11, x_32);
if (x_33 == 0)
{
lean_object* x_34; uint8_t x_35; 
x_34 = lean_unsigned_to_nat(174u);
x_35 = lean_nat_dec_eq(x_11, x_34);
if (x_35 == 0)
{
lean_object* x_36; uint8_t x_37; 
x_36 = lean_unsigned_to_nat(190u);
x_37 = lean_nat_dec_eq(x_11, x_36);
if (x_37 == 0)
{
lean_object* x_38; uint8_t x_39; 
x_38 = lean_unsigned_to_nat(160u);
x_39 = lean_nat_dec_eq(x_11, x_38);
if (x_39 == 0)
{
lean_object* x_40; uint8_t x_41; 
x_40 = lean_unsigned_to_nat(164u);
x_41 = lean_nat_dec_eq(x_11, x_40);
if (x_41 == 0)
{
lean_object* x_42; uint8_t x_43; 
x_42 = lean_unsigned_to_nat(180u);
x_43 = lean_nat_dec_eq(x_11, x_42);
if (x_43 == 0)
{
lean_object* x_44; uint8_t x_45; 
x_44 = lean_unsigned_to_nat(172u);
x_45 = lean_nat_dec_eq(x_11, x_44);
if (x_45 == 0)
{
lean_object* x_46; uint8_t x_47; 
x_46 = lean_unsigned_to_nat(188u);
x_47 = lean_nat_dec_eq(x_11, x_46);
if (x_47 == 0)
{
lean_object* x_48; uint8_t x_49; 
x_48 = lean_unsigned_to_nat(133u);
x_49 = lean_nat_dec_eq(x_11, x_48);
if (x_49 == 0)
{
lean_object* x_50; uint8_t x_51; 
x_50 = lean_unsigned_to_nat(149u);
x_51 = lean_nat_dec_eq(x_11, x_50);
if (x_51 == 0)
{
lean_object* x_52; uint8_t x_53; 
x_52 = lean_unsigned_to_nat(141u);
x_53 = lean_nat_dec_eq(x_11, x_52);
if (x_53 == 0)
{
lean_object* x_54; uint8_t x_55; 
x_54 = lean_unsigned_to_nat(157u);
x_55 = lean_nat_dec_eq(x_11, x_54);
if (x_55 == 0)
{
lean_object* x_56; uint8_t x_57; 
x_56 = lean_unsigned_to_nat(153u);
x_57 = lean_nat_dec_eq(x_11, x_56);
if (x_57 == 0)
{
lean_object* x_58; uint8_t x_59; 
x_58 = lean_unsigned_to_nat(129u);
x_59 = lean_nat_dec_eq(x_11, x_58);
if (x_59 == 0)
{
lean_object* x_60; uint8_t x_61; 
x_60 = lean_unsigned_to_nat(145u);
x_61 = lean_nat_dec_eq(x_11, x_60);
if (x_61 == 0)
{
lean_object* x_62; uint8_t x_63; 
x_62 = lean_unsigned_to_nat(134u);
x_63 = lean_nat_dec_eq(x_11, x_62);
if (x_63 == 0)
{
lean_object* x_64; uint8_t x_65; 
x_64 = lean_unsigned_to_nat(150u);
x_65 = lean_nat_dec_eq(x_11, x_64);
if (x_65 == 0)
{
lean_object* x_66; uint8_t x_67; 
x_66 = lean_unsigned_to_nat(142u);
x_67 = lean_nat_dec_eq(x_11, x_66);
if (x_67 == 0)
{
lean_object* x_68; uint8_t x_69; 
x_68 = lean_unsigned_to_nat(132u);
x_69 = lean_nat_dec_eq(x_11, x_68);
if (x_69 == 0)
{
lean_object* x_70; uint8_t x_71; 
x_70 = lean_unsigned_to_nat(148u);
x_71 = lean_nat_dec_eq(x_11, x_70);
if (x_71 == 0)
{
lean_object* x_72; uint8_t x_73; uint8_t x_74; uint8_t x_75; uint8_t x_76; uint8_t x_77; uint8_t x_78; uint8_t x_79; lean_object* x_80; uint16_t x_81; uint8_t x_82; uint8_t x_83; lean_object* x_84; uint8_t x_85; uint8_t x_86; uint8_t x_92; lean_object* x_93; lean_object* x_94; uint8_t x_95; uint8_t x_96; lean_object* x_97; uint8_t x_98; uint16_t x_99; lean_object* x_100; uint8_t x_101; lean_object* x_102; lean_object* x_123; 
x_72 = lean_unsigned_to_nat(140u);
x_73 = lean_nat_dec_eq(x_11, x_72);
if (x_73 == 0)
{
lean_object* x_165; uint8_t x_166; 
x_165 = lean_unsigned_to_nat(105u);
x_166 = lean_nat_dec_eq(x_11, x_165);
if (x_166 == 0)
{
lean_object* x_167; uint8_t x_168; 
x_167 = lean_unsigned_to_nat(101u);
x_168 = lean_nat_dec_eq(x_11, x_167);
if (x_168 == 0)
{
lean_object* x_169; uint8_t x_170; 
x_169 = lean_unsigned_to_nat(117u);
x_170 = lean_nat_dec_eq(x_11, x_169);
if (x_170 == 0)
{
lean_object* x_171; uint8_t x_172; 
x_171 = lean_unsigned_to_nat(109u);
x_172 = lean_nat_dec_eq(x_11, x_171);
if (x_172 == 0)
{
lean_object* x_173; uint8_t x_174; 
x_173 = lean_unsigned_to_nat(125u);
x_174 = lean_nat_dec_eq(x_11, x_173);
if (x_174 == 0)
{
lean_object* x_175; uint8_t x_176; 
x_175 = lean_unsigned_to_nat(121u);
x_176 = lean_nat_dec_eq(x_11, x_175);
if (x_176 == 0)
{
lean_object* x_177; uint8_t x_178; 
x_177 = lean_unsigned_to_nat(97u);
x_178 = lean_nat_dec_eq(x_11, x_177);
if (x_178 == 0)
{
lean_object* x_179; uint8_t x_180; uint8_t x_181; uint8_t x_182; lean_object* x_183; uint16_t x_184; uint8_t x_185; uint8_t x_186; lean_object* x_187; uint8_t x_188; uint8_t x_189; uint8_t x_190; uint8_t x_191; uint8_t x_192; uint8_t x_193; lean_object* x_199; uint8_t x_200; lean_object* x_201; uint16_t x_202; uint8_t x_203; uint8_t x_204; lean_object* x_205; lean_object* x_206; uint8_t x_207; uint8_t x_208; lean_object* x_209; lean_object* x_210; lean_object* x_231; 
x_179 = lean_unsigned_to_nat(113u);
x_180 = lean_nat_dec_eq(x_11, x_179);
if (x_180 == 0)
{
lean_object* x_275; uint8_t x_276; 
x_275 = lean_unsigned_to_nat(233u);
x_276 = lean_nat_dec_eq(x_11, x_275);
if (x_276 == 0)
{
lean_object* x_277; uint8_t x_278; 
x_277 = lean_unsigned_to_nat(229u);
x_278 = lean_nat_dec_eq(x_11, x_277);
if (x_278 == 0)
{
lean_object* x_279; uint8_t x_280; 
x_279 = lean_unsigned_to_nat(245u);
x_280 = lean_nat_dec_eq(x_11, x_279);
if (x_280 == 0)
{
lean_object* x_281; uint8_t x_282; 
x_281 = lean_unsigned_to_nat(237u);
x_282 = lean_nat_dec_eq(x_11, x_281);
if (x_282 == 0)
{
lean_object* x_283; uint8_t x_284; 
x_283 = lean_unsigned_to_nat(253u);
x_284 = lean_nat_dec_eq(x_11, x_283);
if (x_284 == 0)
{
lean_object* x_285; uint8_t x_286; 
x_285 = lean_unsigned_to_nat(249u);
x_286 = lean_nat_dec_eq(x_11, x_285);
if (x_286 == 0)
{
lean_object* x_287; uint8_t x_288; 
x_287 = lean_unsigned_to_nat(225u);
x_288 = lean_nat_dec_eq(x_11, x_287);
if (x_288 == 0)
{
lean_object* x_289; uint8_t x_290; 
x_289 = lean_unsigned_to_nat(241u);
x_290 = lean_nat_dec_eq(x_11, x_289);
if (x_290 == 0)
{
lean_object* x_291; uint8_t x_292; 
x_291 = lean_unsigned_to_nat(41u);
x_292 = lean_nat_dec_eq(x_11, x_291);
if (x_292 == 0)
{
lean_object* x_293; uint8_t x_294; 
x_293 = lean_unsigned_to_nat(37u);
x_294 = lean_nat_dec_eq(x_11, x_293);
if (x_294 == 0)
{
lean_object* x_295; uint8_t x_296; 
x_295 = lean_unsigned_to_nat(53u);
x_296 = lean_nat_dec_eq(x_11, x_295);
if (x_296 == 0)
{
lean_object* x_297; uint8_t x_298; 
x_297 = lean_unsigned_to_nat(45u);
x_298 = lean_nat_dec_eq(x_11, x_297);
if (x_298 == 0)
{
lean_object* x_299; uint8_t x_300; 
x_299 = lean_unsigned_to_nat(61u);
x_300 = lean_nat_dec_eq(x_11, x_299);
if (x_300 == 0)
{
lean_object* x_301; uint8_t x_302; 
x_301 = lean_unsigned_to_nat(57u);
x_302 = lean_nat_dec_eq(x_11, x_301);
if (x_302 == 0)
{
lean_object* x_303; uint8_t x_304; 
x_303 = lean_unsigned_to_nat(33u);
x_304 = lean_nat_dec_eq(x_11, x_303);
if (x_304 == 0)
{
lean_object* x_305; uint8_t x_306; 
x_305 = lean_unsigned_to_nat(49u);
x_306 = lean_nat_dec_eq(x_11, x_305);
if (x_306 == 0)
{
lean_object* x_307; uint8_t x_308; 
x_307 = lean_unsigned_to_nat(9u);
x_308 = lean_nat_dec_eq(x_11, x_307);
if (x_308 == 0)
{
lean_object* x_309; uint8_t x_310; 
x_309 = lean_unsigned_to_nat(5u);
x_310 = lean_nat_dec_eq(x_11, x_309);
if (x_310 == 0)
{
lean_object* x_311; uint8_t x_312; 
x_311 = lean_unsigned_to_nat(21u);
x_312 = lean_nat_dec_eq(x_11, x_311);
if (x_312 == 0)
{
lean_object* x_313; uint8_t x_314; 
x_313 = lean_unsigned_to_nat(13u);
x_314 = lean_nat_dec_eq(x_11, x_313);
if (x_314 == 0)
{
lean_object* x_315; uint8_t x_316; 
x_315 = lean_unsigned_to_nat(29u);
x_316 = lean_nat_dec_eq(x_11, x_315);
if (x_316 == 0)
{
lean_object* x_317; uint8_t x_318; 
x_317 = lean_unsigned_to_nat(25u);
x_318 = lean_nat_dec_eq(x_11, x_317);
if (x_318 == 0)
{
lean_object* x_319; uint8_t x_320; 
x_319 = lean_unsigned_to_nat(1u);
x_320 = lean_nat_dec_eq(x_11, x_319);
if (x_320 == 0)
{
lean_object* x_321; uint8_t x_322; 
x_321 = lean_unsigned_to_nat(17u);
x_322 = lean_nat_dec_eq(x_11, x_321);
if (x_322 == 0)
{
lean_object* x_323; uint8_t x_324; 
x_323 = lean_unsigned_to_nat(73u);
x_324 = lean_nat_dec_eq(x_11, x_323);
if (x_324 == 0)
{
lean_object* x_325; uint8_t x_326; 
x_325 = lean_unsigned_to_nat(69u);
x_326 = lean_nat_dec_eq(x_11, x_325);
if (x_326 == 0)
{
lean_object* x_327; uint8_t x_328; 
x_327 = lean_unsigned_to_nat(85u);
x_328 = lean_nat_dec_eq(x_11, x_327);
if (x_328 == 0)
{
lean_object* x_329; uint8_t x_330; 
x_329 = lean_unsigned_to_nat(77u);
x_330 = lean_nat_dec_eq(x_11, x_329);
if (x_330 == 0)
{
lean_object* x_331; uint8_t x_332; 
x_331 = lean_unsigned_to_nat(93u);
x_332 = lean_nat_dec_eq(x_11, x_331);
if (x_332 == 0)
{
lean_object* x_333; uint8_t x_334; 
x_333 = lean_unsigned_to_nat(89u);
x_334 = lean_nat_dec_eq(x_11, x_333);
if (x_334 == 0)
{
lean_object* x_335; uint8_t x_336; 
x_335 = lean_unsigned_to_nat(65u);
x_336 = lean_nat_dec_eq(x_11, x_335);
if (x_336 == 0)
{
lean_object* x_337; uint8_t x_338; 
x_337 = lean_unsigned_to_nat(81u);
x_338 = lean_nat_dec_eq(x_11, x_337);
if (x_338 == 0)
{
lean_object* x_339; uint8_t x_340; 
x_339 = lean_unsigned_to_nat(201u);
x_340 = lean_nat_dec_eq(x_11, x_339);
if (x_340 == 0)
{
lean_object* x_341; uint8_t x_342; 
x_341 = lean_unsigned_to_nat(197u);
x_342 = lean_nat_dec_eq(x_11, x_341);
if (x_342 == 0)
{
lean_object* x_343; uint8_t x_344; 
x_343 = lean_unsigned_to_nat(213u);
x_344 = lean_nat_dec_eq(x_11, x_343);
if (x_344 == 0)
{
lean_object* x_345; uint8_t x_346; 
x_345 = lean_unsigned_to_nat(205u);
x_346 = lean_nat_dec_eq(x_11, x_345);
if (x_346 == 0)
{
lean_object* x_347; uint8_t x_348; 
x_347 = lean_unsigned_to_nat(221u);
x_348 = lean_nat_dec_eq(x_11, x_347);
if (x_348 == 0)
{
lean_object* x_349; uint8_t x_350; 
x_349 = lean_unsigned_to_nat(217u);
x_350 = lean_nat_dec_eq(x_11, x_349);
if (x_350 == 0)
{
lean_object* x_351; uint8_t x_352; 
x_351 = lean_unsigned_to_nat(193u);
x_352 = lean_nat_dec_eq(x_11, x_351);
if (x_352 == 0)
{
lean_object* x_353; uint8_t x_354; 
x_353 = lean_unsigned_to_nat(209u);
x_354 = lean_nat_dec_eq(x_11, x_353);
if (x_354 == 0)
{
lean_object* x_355; uint8_t x_356; 
x_355 = lean_unsigned_to_nat(224u);
x_356 = lean_nat_dec_eq(x_11, x_355);
if (x_356 == 0)
{
lean_object* x_357; uint8_t x_358; 
x_357 = lean_unsigned_to_nat(228u);
x_358 = lean_nat_dec_eq(x_11, x_357);
if (x_358 == 0)
{
lean_object* x_359; uint8_t x_360; 
x_359 = lean_unsigned_to_nat(236u);
x_360 = lean_nat_dec_eq(x_11, x_359);
if (x_360 == 0)
{
lean_object* x_361; uint8_t x_362; 
x_361 = lean_unsigned_to_nat(192u);
x_362 = lean_nat_dec_eq(x_11, x_361);
if (x_362 == 0)
{
lean_object* x_363; uint8_t x_364; 
x_363 = lean_unsigned_to_nat(196u);
x_364 = lean_nat_dec_eq(x_11, x_363);
if (x_364 == 0)
{
lean_object* x_365; uint8_t x_366; lean_object* x_367; 
x_365 = lean_unsigned_to_nat(204u);
x_366 = lean_nat_dec_eq(x_11, x_365);
if (x_366 == 0)
{
lean_object* x_406; uint8_t x_407; 
x_406 = lean_unsigned_to_nat(230u);
x_407 = lean_nat_dec_eq(x_11, x_406);
if (x_407 == 0)
{
lean_object* x_408; uint8_t x_409; 
x_408 = lean_unsigned_to_nat(246u);
x_409 = lean_nat_dec_eq(x_11, x_408);
if (x_409 == 0)
{
lean_object* x_410; uint8_t x_411; 
x_410 = lean_unsigned_to_nat(238u);
x_411 = lean_nat_dec_eq(x_11, x_410);
if (x_411 == 0)
{
lean_object* x_412; uint8_t x_413; lean_object* x_414; 
x_412 = lean_unsigned_to_nat(254u);
x_413 = lean_nat_dec_eq(x_11, x_412);
if (x_413 == 0)
{
lean_object* x_453; uint8_t x_454; 
x_453 = lean_unsigned_to_nat(198u);
x_454 = lean_nat_dec_eq(x_11, x_453);
if (x_454 == 0)
{
lean_object* x_455; uint8_t x_456; 
x_455 = lean_unsigned_to_nat(214u);
x_456 = lean_nat_dec_eq(x_11, x_455);
if (x_456 == 0)
{
lean_object* x_457; uint8_t x_458; 
x_457 = lean_unsigned_to_nat(206u);
x_458 = lean_nat_dec_eq(x_11, x_457);
if (x_458 == 0)
{
lean_object* x_459; uint8_t x_460; 
x_459 = lean_unsigned_to_nat(222u);
x_460 = lean_nat_dec_eq(x_11, x_459);
if (x_460 == 0)
{
lean_object* x_461; uint8_t x_462; 
x_461 = lean_unsigned_to_nat(232u);
x_462 = lean_nat_dec_eq(x_11, x_461);
if (x_462 == 0)
{
lean_object* x_463; uint8_t x_464; 
x_463 = lean_unsigned_to_nat(202u);
x_464 = lean_nat_dec_eq(x_11, x_463);
if (x_464 == 0)
{
lean_object* x_465; uint8_t x_466; 
x_465 = lean_unsigned_to_nat(200u);
x_466 = lean_nat_dec_eq(x_11, x_465);
if (x_466 == 0)
{
lean_object* x_467; uint8_t x_468; 
x_467 = lean_unsigned_to_nat(136u);
x_468 = lean_nat_dec_eq(x_11, x_467);
if (x_468 == 0)
{
lean_object* x_469; uint8_t x_470; 
x_469 = lean_unsigned_to_nat(10u);
x_470 = lean_nat_dec_eq(x_11, x_469);
if (x_470 == 0)
{
lean_object* x_471; uint8_t x_472; 
x_471 = lean_unsigned_to_nat(6u);
x_472 = lean_nat_dec_eq(x_11, x_471);
if (x_472 == 0)
{
lean_object* x_473; uint8_t x_474; 
x_473 = lean_unsigned_to_nat(22u);
x_474 = lean_nat_dec_eq(x_11, x_473);
if (x_474 == 0)
{
lean_object* x_475; uint8_t x_476; 
x_475 = lean_unsigned_to_nat(14u);
x_476 = lean_nat_dec_eq(x_11, x_475);
if (x_476 == 0)
{
lean_object* x_477; uint8_t x_478; 
x_477 = lean_unsigned_to_nat(30u);
x_478 = lean_nat_dec_eq(x_11, x_477);
if (x_478 == 0)
{
lean_object* x_479; uint8_t x_480; 
x_479 = lean_unsigned_to_nat(74u);
x_480 = lean_nat_dec_eq(x_11, x_479);
if (x_480 == 0)
{
lean_object* x_481; uint8_t x_482; 
x_481 = lean_unsigned_to_nat(70u);
x_482 = lean_nat_dec_eq(x_11, x_481);
if (x_482 == 0)
{
lean_object* x_483; uint8_t x_484; 
x_483 = lean_unsigned_to_nat(86u);
x_484 = lean_nat_dec_eq(x_11, x_483);
if (x_484 == 0)
{
lean_object* x_485; uint8_t x_486; 
x_485 = lean_unsigned_to_nat(78u);
x_486 = lean_nat_dec_eq(x_11, x_485);
if (x_486 == 0)
{
lean_object* x_487; uint8_t x_488; 
x_487 = lean_unsigned_to_nat(94u);
x_488 = lean_nat_dec_eq(x_11, x_487);
if (x_488 == 0)
{
lean_object* x_489; uint8_t x_490; 
x_489 = lean_unsigned_to_nat(42u);
x_490 = lean_nat_dec_eq(x_11, x_489);
if (x_490 == 0)
{
lean_object* x_491; uint8_t x_492; 
x_491 = lean_unsigned_to_nat(38u);
x_492 = lean_nat_dec_eq(x_11, x_491);
if (x_492 == 0)
{
lean_object* x_493; uint8_t x_494; 
x_493 = lean_unsigned_to_nat(54u);
x_494 = lean_nat_dec_eq(x_11, x_493);
if (x_494 == 0)
{
lean_object* x_495; uint8_t x_496; 
x_495 = lean_unsigned_to_nat(46u);
x_496 = lean_nat_dec_eq(x_11, x_495);
if (x_496 == 0)
{
lean_object* x_497; uint8_t x_498; 
x_497 = lean_unsigned_to_nat(62u);
x_498 = lean_nat_dec_eq(x_11, x_497);
if (x_498 == 0)
{
lean_object* x_499; uint8_t x_500; 
x_499 = lean_unsigned_to_nat(106u);
x_500 = lean_nat_dec_eq(x_11, x_499);
if (x_500 == 0)
{
lean_object* x_501; uint8_t x_502; 
x_501 = lean_unsigned_to_nat(102u);
x_502 = lean_nat_dec_eq(x_11, x_501);
if (x_502 == 0)
{
lean_object* x_503; uint8_t x_504; 
x_503 = lean_unsigned_to_nat(118u);
x_504 = lean_nat_dec_eq(x_11, x_503);
if (x_504 == 0)
{
lean_object* x_505; uint8_t x_506; 
x_505 = lean_unsigned_to_nat(110u);
x_506 = lean_nat_dec_eq(x_11, x_505);
if (x_506 == 0)
{
lean_object* x_507; uint8_t x_508; uint8_t x_509; lean_object* x_510; uint8_t x_511; uint8_t x_512; uint8_t x_513; uint8_t x_514; uint16_t x_515; uint8_t x_516; uint8_t x_517; lean_object* x_518; uint8_t x_519; uint8_t x_520; uint8_t x_521; uint8_t x_527; lean_object* x_528; uint8_t x_529; uint8_t x_530; uint8_t x_531; uint16_t x_532; uint8_t x_533; lean_object* x_534; uint8_t x_535; uint8_t x_536; uint8_t x_537; uint8_t x_538; uint8_t x_539; uint8_t x_540; lean_object* x_546; 
x_507 = lean_unsigned_to_nat(126u);
x_508 = lean_nat_dec_eq(x_11, x_507);
if (x_508 == 0)
{
lean_object* x_571; uint8_t x_572; 
x_571 = lean_unsigned_to_nat(36u);
x_572 = lean_nat_dec_eq(x_11, x_571);
if (x_572 == 0)
{
lean_object* x_573; uint8_t x_574; 
x_573 = lean_unsigned_to_nat(44u);
x_574 = lean_nat_dec_eq(x_11, x_573);
if (x_574 == 0)
{
lean_object* x_575; uint8_t x_576; 
x_575 = lean_unsigned_to_nat(144u);
x_576 = lean_nat_dec_eq(x_11, x_575);
if (x_576 == 0)
{
lean_object* x_577; uint8_t x_578; 
x_577 = lean_unsigned_to_nat(176u);
x_578 = lean_nat_dec_eq(x_11, x_577);
if (x_578 == 0)
{
lean_object* x_579; uint8_t x_580; 
x_579 = lean_unsigned_to_nat(240u);
x_580 = lean_nat_dec_eq(x_11, x_579);
if (x_580 == 0)
{
lean_object* x_581; uint8_t x_582; 
x_581 = lean_unsigned_to_nat(208u);
x_582 = lean_nat_dec_eq(x_11, x_581);
if (x_582 == 0)
{
lean_object* x_583; uint8_t x_584; 
x_583 = lean_unsigned_to_nat(48u);
x_584 = lean_nat_dec_eq(x_11, x_583);
if (x_584 == 0)
{
lean_object* x_585; uint8_t x_586; 
x_585 = lean_unsigned_to_nat(16u);
x_586 = lean_nat_dec_eq(x_11, x_585);
if (x_586 == 0)
{
lean_object* x_587; uint8_t x_588; 
x_587 = lean_unsigned_to_nat(80u);
x_588 = lean_nat_dec_eq(x_11, x_587);
if (x_588 == 0)
{
lean_object* x_589; uint8_t x_590; 
x_589 = lean_unsigned_to_nat(112u);
x_590 = lean_nat_dec_eq(x_11, x_589);
if (x_590 == 0)
{
lean_object* x_591; uint8_t x_592; 
x_591 = lean_unsigned_to_nat(76u);
x_592 = lean_nat_dec_eq(x_11, x_591);
if (x_592 == 0)
{
lean_object* x_593; uint8_t x_594; 
x_593 = lean_unsigned_to_nat(108u);
x_594 = lean_nat_dec_eq(x_11, x_593);
if (x_594 == 0)
{
lean_object* x_595; uint8_t x_596; 
x_595 = lean_unsigned_to_nat(32u);
x_596 = lean_nat_dec_eq(x_11, x_595);
if (x_596 == 0)
{
lean_object* x_597; uint8_t x_598; 
x_597 = lean_unsigned_to_nat(96u);
x_598 = lean_nat_dec_eq(x_11, x_597);
if (x_598 == 0)
{
lean_object* x_599; uint8_t x_600; 
x_599 = lean_unsigned_to_nat(64u);
x_600 = lean_nat_dec_eq(x_11, x_599);
if (x_600 == 0)
{
lean_object* x_601; uint8_t x_602; 
x_601 = lean_unsigned_to_nat(72u);
x_602 = lean_nat_dec_eq(x_11, x_601);
if (x_602 == 0)
{
lean_object* x_603; uint8_t x_604; 
x_603 = lean_unsigned_to_nat(104u);
x_604 = lean_nat_dec_eq(x_11, x_603);
if (x_604 == 0)
{
lean_object* x_605; uint8_t x_606; 
x_605 = lean_unsigned_to_nat(8u);
x_606 = lean_nat_dec_eq(x_11, x_605);
if (x_606 == 0)
{
lean_object* x_607; uint8_t x_608; 
x_607 = lean_unsigned_to_nat(40u);
x_608 = lean_nat_dec_eq(x_11, x_607);
if (x_608 == 0)
{
lean_object* x_609; uint8_t x_610; 
x_609 = lean_unsigned_to_nat(170u);
x_610 = lean_nat_dec_eq(x_11, x_609);
if (x_610 == 0)
{
lean_object* x_611; uint8_t x_612; 
x_611 = lean_unsigned_to_nat(168u);
x_612 = lean_nat_dec_eq(x_11, x_611);
if (x_612 == 0)
{
lean_object* x_613; uint8_t x_614; 
x_613 = lean_unsigned_to_nat(138u);
x_614 = lean_nat_dec_eq(x_11, x_613);
if (x_614 == 0)
{
lean_object* x_615; uint8_t x_616; 
x_615 = lean_unsigned_to_nat(152u);
x_616 = lean_nat_dec_eq(x_11, x_615);
if (x_616 == 0)
{
lean_object* x_617; uint8_t x_618; 
x_617 = lean_unsigned_to_nat(186u);
x_618 = lean_nat_dec_eq(x_11, x_617);
if (x_618 == 0)
{
lean_object* x_619; uint8_t x_620; 
x_619 = lean_unsigned_to_nat(154u);
x_620 = lean_nat_dec_eq(x_11, x_619);
if (x_620 == 0)
{
lean_object* x_621; uint8_t x_622; 
x_621 = lean_unsigned_to_nat(24u);
x_622 = lean_nat_dec_eq(x_11, x_621);
if (x_622 == 0)
{
lean_object* x_623; uint8_t x_624; 
x_623 = lean_unsigned_to_nat(56u);
x_624 = lean_nat_dec_eq(x_11, x_623);
if (x_624 == 0)
{
lean_object* x_625; uint8_t x_626; 
x_625 = lean_unsigned_to_nat(88u);
x_626 = lean_nat_dec_eq(x_11, x_625);
if (x_626 == 0)
{
lean_object* x_627; uint8_t x_628; 
x_627 = lean_unsigned_to_nat(120u);
x_628 = lean_nat_dec_eq(x_11, x_627);
if (x_628 == 0)
{
lean_object* x_629; uint8_t x_630; 
x_629 = lean_unsigned_to_nat(184u);
x_630 = lean_nat_dec_eq(x_11, x_629);
if (x_630 == 0)
{
lean_object* x_631; uint8_t x_632; 
x_631 = lean_unsigned_to_nat(216u);
x_632 = lean_nat_dec_eq(x_11, x_631);
if (x_632 == 0)
{
lean_object* x_633; uint8_t x_634; 
x_633 = lean_unsigned_to_nat(248u);
x_634 = lean_nat_dec_eq(x_11, x_633);
if (x_634 == 0)
{
lean_object* x_635; uint8_t x_636; 
x_635 = lean_unsigned_to_nat(234u);
x_636 = lean_nat_dec_eq(x_11, x_635);
if (x_636 == 0)
{
lean_object* x_637; uint8_t x_638; 
x_637 = lean_unsigned_to_nat(0u);
x_638 = lean_nat_dec_eq(x_11, x_637);
if (x_638 == 0)
{
lean_object* x_639; uint8_t x_640; lean_object* x_641; 
lean_dec_ref(x_7);
x_639 = lean_box(0);
x_640 = 1;
x_641 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_641, 0, x_1);
lean_ctor_set(x_641, 1, x_639);
lean_ctor_set_uint8(x_641, sizeof(void*)*2, x_640);
return x_641;
}
else
{
uint8_t x_642; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_642 = !lean_is_exclusive(x_1);
if (x_642 == 0)
{
lean_object* x_643; lean_object* x_644; lean_object* x_645; uint16_t x_646; uint16_t x_647; lean_object* x_648; lean_object* x_649; 
x_643 = lean_ctor_get(x_1, 2);
lean_dec(x_643);
x_644 = lean_ctor_get(x_1, 1);
lean_dec(x_644);
x_645 = lean_ctor_get(x_1, 0);
lean_dec(x_645);
x_646 = 1;
x_647 = lean_uint16_add(x_6, x_646);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_647);
x_648 = lean_box(0);
x_649 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_649, 0, x_1);
lean_ctor_set(x_649, 1, x_648);
lean_ctor_set_uint8(x_649, sizeof(void*)*2, x_638);
return x_649;
}
else
{
uint16_t x_650; uint16_t x_651; lean_object* x_652; lean_object* x_653; lean_object* x_654; 
lean_dec(x_1);
x_650 = 1;
x_651 = lean_uint16_add(x_6, x_650);
x_652 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_652, 0, x_7);
lean_ctor_set(x_652, 1, x_8);
lean_ctor_set(x_652, 2, x_9);
lean_ctor_set_uint8(x_652, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_652, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_652, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_652, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_652, sizeof(void*)*3, x_651);
x_653 = lean_box(0);
x_654 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_654, 0, x_652);
lean_ctor_set(x_654, 1, x_653);
lean_ctor_set_uint8(x_654, sizeof(void*)*2, x_638);
return x_654;
}
}
}
else
{
uint8_t x_655; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_655 = !lean_is_exclusive(x_1);
if (x_655 == 0)
{
lean_object* x_656; lean_object* x_657; lean_object* x_658; uint16_t x_659; uint16_t x_660; lean_object* x_661; lean_object* x_662; 
x_656 = lean_ctor_get(x_1, 2);
lean_dec(x_656);
x_657 = lean_ctor_get(x_1, 1);
lean_dec(x_657);
x_658 = lean_ctor_get(x_1, 0);
lean_dec(x_658);
x_659 = 1;
x_660 = lean_uint16_add(x_6, x_659);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_660);
x_661 = lean_box(0);
x_662 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_662, 0, x_1);
lean_ctor_set(x_662, 1, x_661);
lean_ctor_set_uint8(x_662, sizeof(void*)*2, x_634);
return x_662;
}
else
{
uint16_t x_663; uint16_t x_664; lean_object* x_665; lean_object* x_666; lean_object* x_667; 
lean_dec(x_1);
x_663 = 1;
x_664 = lean_uint16_add(x_6, x_663);
x_665 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_665, 0, x_7);
lean_ctor_set(x_665, 1, x_8);
lean_ctor_set(x_665, 2, x_9);
lean_ctor_set_uint8(x_665, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_665, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_665, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_665, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_665, sizeof(void*)*3, x_664);
x_666 = lean_box(0);
x_667 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_667, 0, x_665);
lean_ctor_set(x_667, 1, x_666);
lean_ctor_set_uint8(x_667, sizeof(void*)*2, x_634);
return x_667;
}
}
}
else
{
uint8_t x_668; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_668 = !lean_is_exclusive(x_1);
if (x_668 == 0)
{
lean_object* x_669; lean_object* x_670; lean_object* x_671; uint8_t x_672; 
x_669 = lean_ctor_get(x_1, 2);
lean_dec(x_669);
x_670 = lean_ctor_get(x_1, 1);
lean_dec(x_670);
x_671 = lean_ctor_get(x_1, 0);
lean_dec(x_671);
x_672 = !lean_is_exclusive(x_7);
if (x_672 == 0)
{
uint16_t x_673; uint16_t x_674; lean_object* x_675; lean_object* x_676; 
x_673 = 1;
x_674 = lean_uint16_add(x_6, x_673);
lean_ctor_set_uint8(x_7, 3, x_634);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_674);
x_675 = lean_box(0);
x_676 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_676, 0, x_1);
lean_ctor_set(x_676, 1, x_675);
lean_ctor_set_uint8(x_676, sizeof(void*)*2, x_632);
return x_676;
}
else
{
uint8_t x_677; uint8_t x_678; uint8_t x_679; uint8_t x_680; uint8_t x_681; uint16_t x_682; uint16_t x_683; lean_object* x_684; lean_object* x_685; lean_object* x_686; 
x_677 = lean_ctor_get_uint8(x_7, 0);
x_678 = lean_ctor_get_uint8(x_7, 1);
x_679 = lean_ctor_get_uint8(x_7, 2);
x_680 = lean_ctor_get_uint8(x_7, 4);
x_681 = lean_ctor_get_uint8(x_7, 5);
lean_dec(x_7);
x_682 = 1;
x_683 = lean_uint16_add(x_6, x_682);
x_684 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_684, 0, x_677);
lean_ctor_set_uint8(x_684, 1, x_678);
lean_ctor_set_uint8(x_684, 2, x_679);
lean_ctor_set_uint8(x_684, 3, x_634);
lean_ctor_set_uint8(x_684, 4, x_680);
lean_ctor_set_uint8(x_684, 5, x_681);
lean_ctor_set(x_1, 0, x_684);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_683);
x_685 = lean_box(0);
x_686 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_686, 0, x_1);
lean_ctor_set(x_686, 1, x_685);
lean_ctor_set_uint8(x_686, sizeof(void*)*2, x_632);
return x_686;
}
}
else
{
uint8_t x_687; uint8_t x_688; uint8_t x_689; uint8_t x_690; uint8_t x_691; lean_object* x_692; uint16_t x_693; uint16_t x_694; lean_object* x_695; lean_object* x_696; lean_object* x_697; lean_object* x_698; 
lean_dec(x_1);
x_687 = lean_ctor_get_uint8(x_7, 0);
x_688 = lean_ctor_get_uint8(x_7, 1);
x_689 = lean_ctor_get_uint8(x_7, 2);
x_690 = lean_ctor_get_uint8(x_7, 4);
x_691 = lean_ctor_get_uint8(x_7, 5);
if (lean_is_exclusive(x_7)) {
 x_692 = x_7;
} else {
 lean_dec_ref(x_7);
 x_692 = lean_box(0);
}
x_693 = 1;
x_694 = lean_uint16_add(x_6, x_693);
if (lean_is_scalar(x_692)) {
 x_695 = lean_alloc_ctor(0, 0, 6);
} else {
 x_695 = x_692;
}
lean_ctor_set_uint8(x_695, 0, x_687);
lean_ctor_set_uint8(x_695, 1, x_688);
lean_ctor_set_uint8(x_695, 2, x_689);
lean_ctor_set_uint8(x_695, 3, x_634);
lean_ctor_set_uint8(x_695, 4, x_690);
lean_ctor_set_uint8(x_695, 5, x_691);
x_696 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_696, 0, x_695);
lean_ctor_set(x_696, 1, x_8);
lean_ctor_set(x_696, 2, x_9);
lean_ctor_set_uint8(x_696, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_696, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_696, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_696, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_696, sizeof(void*)*3, x_694);
x_697 = lean_box(0);
x_698 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_698, 0, x_696);
lean_ctor_set(x_698, 1, x_697);
lean_ctor_set_uint8(x_698, sizeof(void*)*2, x_632);
return x_698;
}
}
}
else
{
uint8_t x_699; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_699 = !lean_is_exclusive(x_1);
if (x_699 == 0)
{
lean_object* x_700; lean_object* x_701; lean_object* x_702; uint8_t x_703; 
x_700 = lean_ctor_get(x_1, 2);
lean_dec(x_700);
x_701 = lean_ctor_get(x_1, 1);
lean_dec(x_701);
x_702 = lean_ctor_get(x_1, 0);
lean_dec(x_702);
x_703 = !lean_is_exclusive(x_7);
if (x_703 == 0)
{
uint16_t x_704; uint16_t x_705; lean_object* x_706; lean_object* x_707; 
x_704 = 1;
x_705 = lean_uint16_add(x_6, x_704);
lean_ctor_set_uint8(x_7, 3, x_630);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_705);
x_706 = lean_box(0);
x_707 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_707, 0, x_1);
lean_ctor_set(x_707, 1, x_706);
lean_ctor_set_uint8(x_707, sizeof(void*)*2, x_630);
return x_707;
}
else
{
uint8_t x_708; uint8_t x_709; uint8_t x_710; uint8_t x_711; uint8_t x_712; uint16_t x_713; uint16_t x_714; lean_object* x_715; lean_object* x_716; lean_object* x_717; 
x_708 = lean_ctor_get_uint8(x_7, 0);
x_709 = lean_ctor_get_uint8(x_7, 1);
x_710 = lean_ctor_get_uint8(x_7, 2);
x_711 = lean_ctor_get_uint8(x_7, 4);
x_712 = lean_ctor_get_uint8(x_7, 5);
lean_dec(x_7);
x_713 = 1;
x_714 = lean_uint16_add(x_6, x_713);
x_715 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_715, 0, x_708);
lean_ctor_set_uint8(x_715, 1, x_709);
lean_ctor_set_uint8(x_715, 2, x_710);
lean_ctor_set_uint8(x_715, 3, x_630);
lean_ctor_set_uint8(x_715, 4, x_711);
lean_ctor_set_uint8(x_715, 5, x_712);
lean_ctor_set(x_1, 0, x_715);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_714);
x_716 = lean_box(0);
x_717 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_717, 0, x_1);
lean_ctor_set(x_717, 1, x_716);
lean_ctor_set_uint8(x_717, sizeof(void*)*2, x_630);
return x_717;
}
}
else
{
uint8_t x_718; uint8_t x_719; uint8_t x_720; uint8_t x_721; uint8_t x_722; lean_object* x_723; uint16_t x_724; uint16_t x_725; lean_object* x_726; lean_object* x_727; lean_object* x_728; lean_object* x_729; 
lean_dec(x_1);
x_718 = lean_ctor_get_uint8(x_7, 0);
x_719 = lean_ctor_get_uint8(x_7, 1);
x_720 = lean_ctor_get_uint8(x_7, 2);
x_721 = lean_ctor_get_uint8(x_7, 4);
x_722 = lean_ctor_get_uint8(x_7, 5);
if (lean_is_exclusive(x_7)) {
 x_723 = x_7;
} else {
 lean_dec_ref(x_7);
 x_723 = lean_box(0);
}
x_724 = 1;
x_725 = lean_uint16_add(x_6, x_724);
if (lean_is_scalar(x_723)) {
 x_726 = lean_alloc_ctor(0, 0, 6);
} else {
 x_726 = x_723;
}
lean_ctor_set_uint8(x_726, 0, x_718);
lean_ctor_set_uint8(x_726, 1, x_719);
lean_ctor_set_uint8(x_726, 2, x_720);
lean_ctor_set_uint8(x_726, 3, x_630);
lean_ctor_set_uint8(x_726, 4, x_721);
lean_ctor_set_uint8(x_726, 5, x_722);
x_727 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_727, 0, x_726);
lean_ctor_set(x_727, 1, x_8);
lean_ctor_set(x_727, 2, x_9);
lean_ctor_set_uint8(x_727, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_727, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_727, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_727, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_727, sizeof(void*)*3, x_725);
x_728 = lean_box(0);
x_729 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_729, 0, x_727);
lean_ctor_set(x_729, 1, x_728);
lean_ctor_set_uint8(x_729, sizeof(void*)*2, x_630);
return x_729;
}
}
}
else
{
uint8_t x_730; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_730 = !lean_is_exclusive(x_1);
if (x_730 == 0)
{
lean_object* x_731; lean_object* x_732; lean_object* x_733; uint8_t x_734; 
x_731 = lean_ctor_get(x_1, 2);
lean_dec(x_731);
x_732 = lean_ctor_get(x_1, 1);
lean_dec(x_732);
x_733 = lean_ctor_get(x_1, 0);
lean_dec(x_733);
x_734 = !lean_is_exclusive(x_7);
if (x_734 == 0)
{
uint16_t x_735; uint16_t x_736; lean_object* x_737; lean_object* x_738; 
x_735 = 1;
x_736 = lean_uint16_add(x_6, x_735);
lean_ctor_set_uint8(x_7, 4, x_628);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_736);
x_737 = lean_box(0);
x_738 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_738, 0, x_1);
lean_ctor_set(x_738, 1, x_737);
lean_ctor_set_uint8(x_738, sizeof(void*)*2, x_628);
return x_738;
}
else
{
uint8_t x_739; uint8_t x_740; uint8_t x_741; uint8_t x_742; uint8_t x_743; uint16_t x_744; uint16_t x_745; lean_object* x_746; lean_object* x_747; lean_object* x_748; 
x_739 = lean_ctor_get_uint8(x_7, 0);
x_740 = lean_ctor_get_uint8(x_7, 1);
x_741 = lean_ctor_get_uint8(x_7, 2);
x_742 = lean_ctor_get_uint8(x_7, 3);
x_743 = lean_ctor_get_uint8(x_7, 5);
lean_dec(x_7);
x_744 = 1;
x_745 = lean_uint16_add(x_6, x_744);
x_746 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_746, 0, x_739);
lean_ctor_set_uint8(x_746, 1, x_740);
lean_ctor_set_uint8(x_746, 2, x_741);
lean_ctor_set_uint8(x_746, 3, x_742);
lean_ctor_set_uint8(x_746, 4, x_628);
lean_ctor_set_uint8(x_746, 5, x_743);
lean_ctor_set(x_1, 0, x_746);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_745);
x_747 = lean_box(0);
x_748 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_748, 0, x_1);
lean_ctor_set(x_748, 1, x_747);
lean_ctor_set_uint8(x_748, sizeof(void*)*2, x_628);
return x_748;
}
}
else
{
uint8_t x_749; uint8_t x_750; uint8_t x_751; uint8_t x_752; uint8_t x_753; lean_object* x_754; uint16_t x_755; uint16_t x_756; lean_object* x_757; lean_object* x_758; lean_object* x_759; lean_object* x_760; 
lean_dec(x_1);
x_749 = lean_ctor_get_uint8(x_7, 0);
x_750 = lean_ctor_get_uint8(x_7, 1);
x_751 = lean_ctor_get_uint8(x_7, 2);
x_752 = lean_ctor_get_uint8(x_7, 3);
x_753 = lean_ctor_get_uint8(x_7, 5);
if (lean_is_exclusive(x_7)) {
 x_754 = x_7;
} else {
 lean_dec_ref(x_7);
 x_754 = lean_box(0);
}
x_755 = 1;
x_756 = lean_uint16_add(x_6, x_755);
if (lean_is_scalar(x_754)) {
 x_757 = lean_alloc_ctor(0, 0, 6);
} else {
 x_757 = x_754;
}
lean_ctor_set_uint8(x_757, 0, x_749);
lean_ctor_set_uint8(x_757, 1, x_750);
lean_ctor_set_uint8(x_757, 2, x_751);
lean_ctor_set_uint8(x_757, 3, x_752);
lean_ctor_set_uint8(x_757, 4, x_628);
lean_ctor_set_uint8(x_757, 5, x_753);
x_758 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_758, 0, x_757);
lean_ctor_set(x_758, 1, x_8);
lean_ctor_set(x_758, 2, x_9);
lean_ctor_set_uint8(x_758, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_758, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_758, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_758, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_758, sizeof(void*)*3, x_756);
x_759 = lean_box(0);
x_760 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_760, 0, x_758);
lean_ctor_set(x_760, 1, x_759);
lean_ctor_set_uint8(x_760, sizeof(void*)*2, x_628);
return x_760;
}
}
}
else
{
uint8_t x_761; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_761 = !lean_is_exclusive(x_1);
if (x_761 == 0)
{
lean_object* x_762; lean_object* x_763; lean_object* x_764; uint8_t x_765; 
x_762 = lean_ctor_get(x_1, 2);
lean_dec(x_762);
x_763 = lean_ctor_get(x_1, 1);
lean_dec(x_763);
x_764 = lean_ctor_get(x_1, 0);
lean_dec(x_764);
x_765 = !lean_is_exclusive(x_7);
if (x_765 == 0)
{
uint16_t x_766; uint16_t x_767; lean_object* x_768; lean_object* x_769; 
x_766 = 1;
x_767 = lean_uint16_add(x_6, x_766);
lean_ctor_set_uint8(x_7, 2, x_628);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_767);
x_768 = lean_box(0);
x_769 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_769, 0, x_1);
lean_ctor_set(x_769, 1, x_768);
lean_ctor_set_uint8(x_769, sizeof(void*)*2, x_626);
return x_769;
}
else
{
uint8_t x_770; uint8_t x_771; uint8_t x_772; uint8_t x_773; uint8_t x_774; uint16_t x_775; uint16_t x_776; lean_object* x_777; lean_object* x_778; lean_object* x_779; 
x_770 = lean_ctor_get_uint8(x_7, 0);
x_771 = lean_ctor_get_uint8(x_7, 1);
x_772 = lean_ctor_get_uint8(x_7, 3);
x_773 = lean_ctor_get_uint8(x_7, 4);
x_774 = lean_ctor_get_uint8(x_7, 5);
lean_dec(x_7);
x_775 = 1;
x_776 = lean_uint16_add(x_6, x_775);
x_777 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_777, 0, x_770);
lean_ctor_set_uint8(x_777, 1, x_771);
lean_ctor_set_uint8(x_777, 2, x_628);
lean_ctor_set_uint8(x_777, 3, x_772);
lean_ctor_set_uint8(x_777, 4, x_773);
lean_ctor_set_uint8(x_777, 5, x_774);
lean_ctor_set(x_1, 0, x_777);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_776);
x_778 = lean_box(0);
x_779 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_779, 0, x_1);
lean_ctor_set(x_779, 1, x_778);
lean_ctor_set_uint8(x_779, sizeof(void*)*2, x_626);
return x_779;
}
}
else
{
uint8_t x_780; uint8_t x_781; uint8_t x_782; uint8_t x_783; uint8_t x_784; lean_object* x_785; uint16_t x_786; uint16_t x_787; lean_object* x_788; lean_object* x_789; lean_object* x_790; lean_object* x_791; 
lean_dec(x_1);
x_780 = lean_ctor_get_uint8(x_7, 0);
x_781 = lean_ctor_get_uint8(x_7, 1);
x_782 = lean_ctor_get_uint8(x_7, 3);
x_783 = lean_ctor_get_uint8(x_7, 4);
x_784 = lean_ctor_get_uint8(x_7, 5);
if (lean_is_exclusive(x_7)) {
 x_785 = x_7;
} else {
 lean_dec_ref(x_7);
 x_785 = lean_box(0);
}
x_786 = 1;
x_787 = lean_uint16_add(x_6, x_786);
if (lean_is_scalar(x_785)) {
 x_788 = lean_alloc_ctor(0, 0, 6);
} else {
 x_788 = x_785;
}
lean_ctor_set_uint8(x_788, 0, x_780);
lean_ctor_set_uint8(x_788, 1, x_781);
lean_ctor_set_uint8(x_788, 2, x_628);
lean_ctor_set_uint8(x_788, 3, x_782);
lean_ctor_set_uint8(x_788, 4, x_783);
lean_ctor_set_uint8(x_788, 5, x_784);
x_789 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_789, 0, x_788);
lean_ctor_set(x_789, 1, x_8);
lean_ctor_set(x_789, 2, x_9);
lean_ctor_set_uint8(x_789, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_789, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_789, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_789, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_789, sizeof(void*)*3, x_787);
x_790 = lean_box(0);
x_791 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_791, 0, x_789);
lean_ctor_set(x_791, 1, x_790);
lean_ctor_set_uint8(x_791, sizeof(void*)*2, x_626);
return x_791;
}
}
}
else
{
uint8_t x_792; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_792 = !lean_is_exclusive(x_1);
if (x_792 == 0)
{
lean_object* x_793; lean_object* x_794; lean_object* x_795; uint8_t x_796; 
x_793 = lean_ctor_get(x_1, 2);
lean_dec(x_793);
x_794 = lean_ctor_get(x_1, 1);
lean_dec(x_794);
x_795 = lean_ctor_get(x_1, 0);
lean_dec(x_795);
x_796 = !lean_is_exclusive(x_7);
if (x_796 == 0)
{
uint16_t x_797; uint16_t x_798; lean_object* x_799; lean_object* x_800; 
x_797 = 1;
x_798 = lean_uint16_add(x_6, x_797);
lean_ctor_set_uint8(x_7, 2, x_624);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_798);
x_799 = lean_box(0);
x_800 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_800, 0, x_1);
lean_ctor_set(x_800, 1, x_799);
lean_ctor_set_uint8(x_800, sizeof(void*)*2, x_624);
return x_800;
}
else
{
uint8_t x_801; uint8_t x_802; uint8_t x_803; uint8_t x_804; uint8_t x_805; uint16_t x_806; uint16_t x_807; lean_object* x_808; lean_object* x_809; lean_object* x_810; 
x_801 = lean_ctor_get_uint8(x_7, 0);
x_802 = lean_ctor_get_uint8(x_7, 1);
x_803 = lean_ctor_get_uint8(x_7, 3);
x_804 = lean_ctor_get_uint8(x_7, 4);
x_805 = lean_ctor_get_uint8(x_7, 5);
lean_dec(x_7);
x_806 = 1;
x_807 = lean_uint16_add(x_6, x_806);
x_808 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_808, 0, x_801);
lean_ctor_set_uint8(x_808, 1, x_802);
lean_ctor_set_uint8(x_808, 2, x_624);
lean_ctor_set_uint8(x_808, 3, x_803);
lean_ctor_set_uint8(x_808, 4, x_804);
lean_ctor_set_uint8(x_808, 5, x_805);
lean_ctor_set(x_1, 0, x_808);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_807);
x_809 = lean_box(0);
x_810 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_810, 0, x_1);
lean_ctor_set(x_810, 1, x_809);
lean_ctor_set_uint8(x_810, sizeof(void*)*2, x_624);
return x_810;
}
}
else
{
uint8_t x_811; uint8_t x_812; uint8_t x_813; uint8_t x_814; uint8_t x_815; lean_object* x_816; uint16_t x_817; uint16_t x_818; lean_object* x_819; lean_object* x_820; lean_object* x_821; lean_object* x_822; 
lean_dec(x_1);
x_811 = lean_ctor_get_uint8(x_7, 0);
x_812 = lean_ctor_get_uint8(x_7, 1);
x_813 = lean_ctor_get_uint8(x_7, 3);
x_814 = lean_ctor_get_uint8(x_7, 4);
x_815 = lean_ctor_get_uint8(x_7, 5);
if (lean_is_exclusive(x_7)) {
 x_816 = x_7;
} else {
 lean_dec_ref(x_7);
 x_816 = lean_box(0);
}
x_817 = 1;
x_818 = lean_uint16_add(x_6, x_817);
if (lean_is_scalar(x_816)) {
 x_819 = lean_alloc_ctor(0, 0, 6);
} else {
 x_819 = x_816;
}
lean_ctor_set_uint8(x_819, 0, x_811);
lean_ctor_set_uint8(x_819, 1, x_812);
lean_ctor_set_uint8(x_819, 2, x_624);
lean_ctor_set_uint8(x_819, 3, x_813);
lean_ctor_set_uint8(x_819, 4, x_814);
lean_ctor_set_uint8(x_819, 5, x_815);
x_820 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_820, 0, x_819);
lean_ctor_set(x_820, 1, x_8);
lean_ctor_set(x_820, 2, x_9);
lean_ctor_set_uint8(x_820, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_820, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_820, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_820, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_820, sizeof(void*)*3, x_818);
x_821 = lean_box(0);
x_822 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_822, 0, x_820);
lean_ctor_set(x_822, 1, x_821);
lean_ctor_set_uint8(x_822, sizeof(void*)*2, x_624);
return x_822;
}
}
}
else
{
uint8_t x_823; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_823 = !lean_is_exclusive(x_1);
if (x_823 == 0)
{
lean_object* x_824; lean_object* x_825; lean_object* x_826; uint8_t x_827; 
x_824 = lean_ctor_get(x_1, 2);
lean_dec(x_824);
x_825 = lean_ctor_get(x_1, 1);
lean_dec(x_825);
x_826 = lean_ctor_get(x_1, 0);
lean_dec(x_826);
x_827 = !lean_is_exclusive(x_7);
if (x_827 == 0)
{
uint16_t x_828; uint16_t x_829; lean_object* x_830; lean_object* x_831; 
x_828 = 1;
x_829 = lean_uint16_add(x_6, x_828);
lean_ctor_set_uint8(x_7, 0, x_624);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_829);
x_830 = lean_box(0);
x_831 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_831, 0, x_1);
lean_ctor_set(x_831, 1, x_830);
lean_ctor_set_uint8(x_831, sizeof(void*)*2, x_622);
return x_831;
}
else
{
uint8_t x_832; uint8_t x_833; uint8_t x_834; uint8_t x_835; uint8_t x_836; uint16_t x_837; uint16_t x_838; lean_object* x_839; lean_object* x_840; lean_object* x_841; 
x_832 = lean_ctor_get_uint8(x_7, 1);
x_833 = lean_ctor_get_uint8(x_7, 2);
x_834 = lean_ctor_get_uint8(x_7, 3);
x_835 = lean_ctor_get_uint8(x_7, 4);
x_836 = lean_ctor_get_uint8(x_7, 5);
lean_dec(x_7);
x_837 = 1;
x_838 = lean_uint16_add(x_6, x_837);
x_839 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_839, 0, x_624);
lean_ctor_set_uint8(x_839, 1, x_832);
lean_ctor_set_uint8(x_839, 2, x_833);
lean_ctor_set_uint8(x_839, 3, x_834);
lean_ctor_set_uint8(x_839, 4, x_835);
lean_ctor_set_uint8(x_839, 5, x_836);
lean_ctor_set(x_1, 0, x_839);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_838);
x_840 = lean_box(0);
x_841 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_841, 0, x_1);
lean_ctor_set(x_841, 1, x_840);
lean_ctor_set_uint8(x_841, sizeof(void*)*2, x_622);
return x_841;
}
}
else
{
uint8_t x_842; uint8_t x_843; uint8_t x_844; uint8_t x_845; uint8_t x_846; lean_object* x_847; uint16_t x_848; uint16_t x_849; lean_object* x_850; lean_object* x_851; lean_object* x_852; lean_object* x_853; 
lean_dec(x_1);
x_842 = lean_ctor_get_uint8(x_7, 1);
x_843 = lean_ctor_get_uint8(x_7, 2);
x_844 = lean_ctor_get_uint8(x_7, 3);
x_845 = lean_ctor_get_uint8(x_7, 4);
x_846 = lean_ctor_get_uint8(x_7, 5);
if (lean_is_exclusive(x_7)) {
 x_847 = x_7;
} else {
 lean_dec_ref(x_7);
 x_847 = lean_box(0);
}
x_848 = 1;
x_849 = lean_uint16_add(x_6, x_848);
if (lean_is_scalar(x_847)) {
 x_850 = lean_alloc_ctor(0, 0, 6);
} else {
 x_850 = x_847;
}
lean_ctor_set_uint8(x_850, 0, x_624);
lean_ctor_set_uint8(x_850, 1, x_842);
lean_ctor_set_uint8(x_850, 2, x_843);
lean_ctor_set_uint8(x_850, 3, x_844);
lean_ctor_set_uint8(x_850, 4, x_845);
lean_ctor_set_uint8(x_850, 5, x_846);
x_851 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_851, 0, x_850);
lean_ctor_set(x_851, 1, x_8);
lean_ctor_set(x_851, 2, x_9);
lean_ctor_set_uint8(x_851, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_851, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_851, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_851, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_851, sizeof(void*)*3, x_849);
x_852 = lean_box(0);
x_853 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_853, 0, x_851);
lean_ctor_set(x_853, 1, x_852);
lean_ctor_set_uint8(x_853, sizeof(void*)*2, x_622);
return x_853;
}
}
}
else
{
uint8_t x_854; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_854 = !lean_is_exclusive(x_1);
if (x_854 == 0)
{
lean_object* x_855; lean_object* x_856; lean_object* x_857; uint8_t x_858; 
x_855 = lean_ctor_get(x_1, 2);
lean_dec(x_855);
x_856 = lean_ctor_get(x_1, 1);
lean_dec(x_856);
x_857 = lean_ctor_get(x_1, 0);
lean_dec(x_857);
x_858 = !lean_is_exclusive(x_7);
if (x_858 == 0)
{
uint16_t x_859; uint16_t x_860; lean_object* x_861; lean_object* x_862; 
x_859 = 1;
x_860 = lean_uint16_add(x_6, x_859);
lean_ctor_set_uint8(x_7, 0, x_620);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_860);
x_861 = lean_box(0);
x_862 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_862, 0, x_1);
lean_ctor_set(x_862, 1, x_861);
lean_ctor_set_uint8(x_862, sizeof(void*)*2, x_620);
return x_862;
}
else
{
uint8_t x_863; uint8_t x_864; uint8_t x_865; uint8_t x_866; uint8_t x_867; uint16_t x_868; uint16_t x_869; lean_object* x_870; lean_object* x_871; lean_object* x_872; 
x_863 = lean_ctor_get_uint8(x_7, 1);
x_864 = lean_ctor_get_uint8(x_7, 2);
x_865 = lean_ctor_get_uint8(x_7, 3);
x_866 = lean_ctor_get_uint8(x_7, 4);
x_867 = lean_ctor_get_uint8(x_7, 5);
lean_dec(x_7);
x_868 = 1;
x_869 = lean_uint16_add(x_6, x_868);
x_870 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_870, 0, x_620);
lean_ctor_set_uint8(x_870, 1, x_863);
lean_ctor_set_uint8(x_870, 2, x_864);
lean_ctor_set_uint8(x_870, 3, x_865);
lean_ctor_set_uint8(x_870, 4, x_866);
lean_ctor_set_uint8(x_870, 5, x_867);
lean_ctor_set(x_1, 0, x_870);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_869);
x_871 = lean_box(0);
x_872 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_872, 0, x_1);
lean_ctor_set(x_872, 1, x_871);
lean_ctor_set_uint8(x_872, sizeof(void*)*2, x_620);
return x_872;
}
}
else
{
uint8_t x_873; uint8_t x_874; uint8_t x_875; uint8_t x_876; uint8_t x_877; lean_object* x_878; uint16_t x_879; uint16_t x_880; lean_object* x_881; lean_object* x_882; lean_object* x_883; lean_object* x_884; 
lean_dec(x_1);
x_873 = lean_ctor_get_uint8(x_7, 1);
x_874 = lean_ctor_get_uint8(x_7, 2);
x_875 = lean_ctor_get_uint8(x_7, 3);
x_876 = lean_ctor_get_uint8(x_7, 4);
x_877 = lean_ctor_get_uint8(x_7, 5);
if (lean_is_exclusive(x_7)) {
 x_878 = x_7;
} else {
 lean_dec_ref(x_7);
 x_878 = lean_box(0);
}
x_879 = 1;
x_880 = lean_uint16_add(x_6, x_879);
if (lean_is_scalar(x_878)) {
 x_881 = lean_alloc_ctor(0, 0, 6);
} else {
 x_881 = x_878;
}
lean_ctor_set_uint8(x_881, 0, x_620);
lean_ctor_set_uint8(x_881, 1, x_873);
lean_ctor_set_uint8(x_881, 2, x_874);
lean_ctor_set_uint8(x_881, 3, x_875);
lean_ctor_set_uint8(x_881, 4, x_876);
lean_ctor_set_uint8(x_881, 5, x_877);
x_882 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_882, 0, x_881);
lean_ctor_set(x_882, 1, x_8);
lean_ctor_set(x_882, 2, x_9);
lean_ctor_set_uint8(x_882, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_882, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_882, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_882, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_882, sizeof(void*)*3, x_880);
x_883 = lean_box(0);
x_884 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_884, 0, x_882);
lean_ctor_set(x_884, 1, x_883);
lean_ctor_set_uint8(x_884, sizeof(void*)*2, x_620);
return x_884;
}
}
}
else
{
uint8_t x_885; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_885 = !lean_is_exclusive(x_1);
if (x_885 == 0)
{
lean_object* x_886; lean_object* x_887; lean_object* x_888; uint16_t x_889; uint16_t x_890; lean_object* x_891; lean_object* x_892; 
x_886 = lean_ctor_get(x_1, 2);
lean_dec(x_886);
x_887 = lean_ctor_get(x_1, 1);
lean_dec(x_887);
x_888 = lean_ctor_get(x_1, 0);
lean_dec(x_888);
x_889 = 1;
x_890 = lean_uint16_add(x_6, x_889);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 5, x_3);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_890);
x_891 = lean_box(0);
x_892 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_892, 0, x_1);
lean_ctor_set(x_892, 1, x_891);
lean_ctor_set_uint8(x_892, sizeof(void*)*2, x_618);
return x_892;
}
else
{
uint16_t x_893; uint16_t x_894; lean_object* x_895; lean_object* x_896; lean_object* x_897; 
lean_dec(x_1);
x_893 = 1;
x_894 = lean_uint16_add(x_6, x_893);
x_895 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_895, 0, x_7);
lean_ctor_set(x_895, 1, x_8);
lean_ctor_set(x_895, 2, x_9);
lean_ctor_set_uint8(x_895, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_895, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_895, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_895, sizeof(void*)*3 + 5, x_3);
lean_ctor_set_uint16(x_895, sizeof(void*)*3, x_894);
x_896 = lean_box(0);
x_897 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_897, 0, x_895);
lean_ctor_set(x_897, 1, x_896);
lean_ctor_set_uint8(x_897, sizeof(void*)*2, x_618);
return x_897;
}
}
}
else
{
uint8_t x_898; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_898 = !lean_is_exclusive(x_1);
if (x_898 == 0)
{
lean_object* x_899; lean_object* x_900; lean_object* x_901; uint16_t x_902; uint16_t x_903; lean_object* x_904; lean_object* x_905; lean_object* x_906; 
x_899 = lean_ctor_get(x_1, 2);
lean_dec(x_899);
x_900 = lean_ctor_get(x_1, 1);
lean_dec(x_900);
x_901 = lean_ctor_get(x_1, 0);
lean_dec(x_901);
x_902 = 1;
x_903 = lean_uint16_add(x_6, x_902);
x_904 = lp_dasmodel_updateNZ(x_7, x_5);
lean_ctor_set(x_1, 0, x_904);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 3, x_5);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_903);
x_905 = lean_box(0);
x_906 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_906, 0, x_1);
lean_ctor_set(x_906, 1, x_905);
lean_ctor_set_uint8(x_906, sizeof(void*)*2, x_616);
return x_906;
}
else
{
uint16_t x_907; uint16_t x_908; lean_object* x_909; lean_object* x_910; lean_object* x_911; lean_object* x_912; 
lean_dec(x_1);
x_907 = 1;
x_908 = lean_uint16_add(x_6, x_907);
x_909 = lp_dasmodel_updateNZ(x_7, x_5);
x_910 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_910, 0, x_909);
lean_ctor_set(x_910, 1, x_8);
lean_ctor_set(x_910, 2, x_9);
lean_ctor_set_uint8(x_910, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_910, sizeof(void*)*3 + 3, x_5);
lean_ctor_set_uint8(x_910, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_910, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_910, sizeof(void*)*3, x_908);
x_911 = lean_box(0);
x_912 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_912, 0, x_910);
lean_ctor_set(x_912, 1, x_911);
lean_ctor_set_uint8(x_912, sizeof(void*)*2, x_616);
return x_912;
}
}
}
else
{
uint8_t x_913; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_913 = !lean_is_exclusive(x_1);
if (x_913 == 0)
{
lean_object* x_914; lean_object* x_915; lean_object* x_916; uint16_t x_917; uint16_t x_918; lean_object* x_919; lean_object* x_920; lean_object* x_921; 
x_914 = lean_ctor_get(x_1, 2);
lean_dec(x_914);
x_915 = lean_ctor_get(x_1, 1);
lean_dec(x_915);
x_916 = lean_ctor_get(x_1, 0);
lean_dec(x_916);
x_917 = 1;
x_918 = lean_uint16_add(x_6, x_917);
x_919 = lp_dasmodel_updateNZ(x_7, x_4);
lean_ctor_set(x_1, 0, x_919);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_4);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_918);
x_920 = lean_box(0);
x_921 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_921, 0, x_1);
lean_ctor_set(x_921, 1, x_920);
lean_ctor_set_uint8(x_921, sizeof(void*)*2, x_614);
return x_921;
}
else
{
uint16_t x_922; uint16_t x_923; lean_object* x_924; lean_object* x_925; lean_object* x_926; lean_object* x_927; 
lean_dec(x_1);
x_922 = 1;
x_923 = lean_uint16_add(x_6, x_922);
x_924 = lp_dasmodel_updateNZ(x_7, x_4);
x_925 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_925, 0, x_924);
lean_ctor_set(x_925, 1, x_8);
lean_ctor_set(x_925, 2, x_9);
lean_ctor_set_uint8(x_925, sizeof(void*)*3 + 2, x_4);
lean_ctor_set_uint8(x_925, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_925, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_925, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_925, sizeof(void*)*3, x_923);
x_926 = lean_box(0);
x_927 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_927, 0, x_925);
lean_ctor_set(x_927, 1, x_926);
lean_ctor_set_uint8(x_927, sizeof(void*)*2, x_614);
return x_927;
}
}
}
else
{
uint8_t x_928; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_928 = !lean_is_exclusive(x_1);
if (x_928 == 0)
{
lean_object* x_929; lean_object* x_930; lean_object* x_931; uint16_t x_932; uint16_t x_933; lean_object* x_934; lean_object* x_935; lean_object* x_936; 
x_929 = lean_ctor_get(x_1, 2);
lean_dec(x_929);
x_930 = lean_ctor_get(x_1, 1);
lean_dec(x_930);
x_931 = lean_ctor_get(x_1, 0);
lean_dec(x_931);
x_932 = 1;
x_933 = lean_uint16_add(x_6, x_932);
x_934 = lp_dasmodel_updateNZ(x_7, x_3);
lean_ctor_set(x_1, 0, x_934);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_3);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_933);
x_935 = lean_box(0);
x_936 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_936, 0, x_1);
lean_ctor_set(x_936, 1, x_935);
lean_ctor_set_uint8(x_936, sizeof(void*)*2, x_612);
return x_936;
}
else
{
uint16_t x_937; uint16_t x_938; lean_object* x_939; lean_object* x_940; lean_object* x_941; lean_object* x_942; 
lean_dec(x_1);
x_937 = 1;
x_938 = lean_uint16_add(x_6, x_937);
x_939 = lp_dasmodel_updateNZ(x_7, x_3);
x_940 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_940, 0, x_939);
lean_ctor_set(x_940, 1, x_8);
lean_ctor_set(x_940, 2, x_9);
lean_ctor_set_uint8(x_940, sizeof(void*)*3 + 2, x_3);
lean_ctor_set_uint8(x_940, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_940, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_940, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_940, sizeof(void*)*3, x_938);
x_941 = lean_box(0);
x_942 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_942, 0, x_940);
lean_ctor_set(x_942, 1, x_941);
lean_ctor_set_uint8(x_942, sizeof(void*)*2, x_612);
return x_942;
}
}
}
else
{
uint8_t x_943; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_943 = !lean_is_exclusive(x_1);
if (x_943 == 0)
{
lean_object* x_944; lean_object* x_945; lean_object* x_946; uint16_t x_947; uint16_t x_948; lean_object* x_949; lean_object* x_950; lean_object* x_951; 
x_944 = lean_ctor_get(x_1, 2);
lean_dec(x_944);
x_945 = lean_ctor_get(x_1, 1);
lean_dec(x_945);
x_946 = lean_ctor_get(x_1, 0);
lean_dec(x_946);
x_947 = 1;
x_948 = lean_uint16_add(x_6, x_947);
x_949 = lp_dasmodel_updateNZ(x_7, x_2);
lean_ctor_set(x_1, 0, x_949);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 4, x_2);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_948);
x_950 = lean_box(0);
x_951 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_951, 0, x_1);
lean_ctor_set(x_951, 1, x_950);
lean_ctor_set_uint8(x_951, sizeof(void*)*2, x_610);
return x_951;
}
else
{
uint16_t x_952; uint16_t x_953; lean_object* x_954; lean_object* x_955; lean_object* x_956; lean_object* x_957; 
lean_dec(x_1);
x_952 = 1;
x_953 = lean_uint16_add(x_6, x_952);
x_954 = lp_dasmodel_updateNZ(x_7, x_2);
x_955 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_955, 0, x_954);
lean_ctor_set(x_955, 1, x_8);
lean_ctor_set(x_955, 2, x_9);
lean_ctor_set_uint8(x_955, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_955, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_955, sizeof(void*)*3 + 4, x_2);
lean_ctor_set_uint8(x_955, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_955, sizeof(void*)*3, x_953);
x_956 = lean_box(0);
x_957 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_957, 0, x_955);
lean_ctor_set(x_957, 1, x_956);
lean_ctor_set_uint8(x_957, sizeof(void*)*2, x_610);
return x_957;
}
}
}
else
{
uint8_t x_958; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_958 = !lean_is_exclusive(x_1);
if (x_958 == 0)
{
lean_object* x_959; lean_object* x_960; lean_object* x_961; uint16_t x_962; uint16_t x_963; lean_object* x_964; lean_object* x_965; lean_object* x_966; 
x_959 = lean_ctor_get(x_1, 2);
lean_dec(x_959);
x_960 = lean_ctor_get(x_1, 1);
lean_dec(x_960);
x_961 = lean_ctor_get(x_1, 0);
lean_dec(x_961);
x_962 = 1;
x_963 = lean_uint16_add(x_6, x_962);
x_964 = lp_dasmodel_updateNZ(x_7, x_2);
lean_ctor_set(x_1, 0, x_964);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 3, x_2);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_963);
x_965 = lean_box(0);
x_966 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_966, 0, x_1);
lean_ctor_set(x_966, 1, x_965);
lean_ctor_set_uint8(x_966, sizeof(void*)*2, x_608);
return x_966;
}
else
{
uint16_t x_967; uint16_t x_968; lean_object* x_969; lean_object* x_970; lean_object* x_971; lean_object* x_972; 
lean_dec(x_1);
x_967 = 1;
x_968 = lean_uint16_add(x_6, x_967);
x_969 = lp_dasmodel_updateNZ(x_7, x_2);
x_970 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_970, 0, x_969);
lean_ctor_set(x_970, 1, x_8);
lean_ctor_set(x_970, 2, x_9);
lean_ctor_set_uint8(x_970, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_970, sizeof(void*)*3 + 3, x_2);
lean_ctor_set_uint8(x_970, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_970, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_970, sizeof(void*)*3, x_968);
x_971 = lean_box(0);
x_972 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_972, 0, x_970);
lean_ctor_set(x_972, 1, x_971);
lean_ctor_set_uint8(x_972, sizeof(void*)*2, x_608);
return x_972;
}
}
}
else
{
lean_object* x_973; lean_object* x_974; lean_object* x_975; uint8_t x_976; 
lean_dec_ref(x_7);
x_973 = lp_dasmodel_CPU_pull(x_1);
x_974 = lean_ctor_get(x_973, 0);
lean_inc(x_974);
x_975 = lean_ctor_get(x_973, 1);
lean_inc(x_975);
lean_dec_ref(x_973);
x_976 = !lean_is_exclusive(x_974);
if (x_976 == 0)
{
uint16_t x_977; lean_object* x_978; uint16_t x_979; uint16_t x_980; uint8_t x_981; lean_object* x_982; lean_object* x_983; lean_object* x_984; 
x_977 = lean_ctor_get_uint16(x_974, sizeof(void*)*3);
x_978 = lean_ctor_get(x_974, 0);
lean_dec(x_978);
x_979 = 1;
x_980 = lean_uint16_add(x_977, x_979);
x_981 = lean_unbox(x_975);
lean_dec(x_975);
x_982 = lp_dasmodel___private_CPU6502_0__byteToFlags(x_981);
lean_ctor_set(x_974, 0, x_982);
lean_ctor_set_uint16(x_974, sizeof(void*)*3, x_980);
x_983 = lean_box(0);
x_984 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_984, 0, x_974);
lean_ctor_set(x_984, 1, x_983);
lean_ctor_set_uint8(x_984, sizeof(void*)*2, x_606);
return x_984;
}
else
{
uint8_t x_985; uint8_t x_986; uint8_t x_987; uint8_t x_988; uint16_t x_989; lean_object* x_990; lean_object* x_991; uint16_t x_992; uint16_t x_993; uint8_t x_994; lean_object* x_995; lean_object* x_996; lean_object* x_997; lean_object* x_998; 
x_985 = lean_ctor_get_uint8(x_974, sizeof(void*)*3 + 2);
x_986 = lean_ctor_get_uint8(x_974, sizeof(void*)*3 + 3);
x_987 = lean_ctor_get_uint8(x_974, sizeof(void*)*3 + 4);
x_988 = lean_ctor_get_uint8(x_974, sizeof(void*)*3 + 5);
x_989 = lean_ctor_get_uint16(x_974, sizeof(void*)*3);
x_990 = lean_ctor_get(x_974, 1);
x_991 = lean_ctor_get(x_974, 2);
lean_inc(x_991);
lean_inc(x_990);
lean_dec(x_974);
x_992 = 1;
x_993 = lean_uint16_add(x_989, x_992);
x_994 = lean_unbox(x_975);
lean_dec(x_975);
x_995 = lp_dasmodel___private_CPU6502_0__byteToFlags(x_994);
x_996 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_996, 0, x_995);
lean_ctor_set(x_996, 1, x_990);
lean_ctor_set(x_996, 2, x_991);
lean_ctor_set_uint8(x_996, sizeof(void*)*3 + 2, x_985);
lean_ctor_set_uint8(x_996, sizeof(void*)*3 + 3, x_986);
lean_ctor_set_uint8(x_996, sizeof(void*)*3 + 4, x_987);
lean_ctor_set_uint8(x_996, sizeof(void*)*3 + 5, x_988);
lean_ctor_set_uint16(x_996, sizeof(void*)*3, x_993);
x_997 = lean_box(0);
x_998 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_998, 0, x_996);
lean_ctor_set(x_998, 1, x_997);
lean_ctor_set_uint8(x_998, sizeof(void*)*2, x_606);
return x_998;
}
}
}
else
{
uint8_t x_999; lean_object* x_1000; uint8_t x_1001; 
x_999 = lp_dasmodel___private_CPU6502_0__flagsToByte(x_7);
lean_dec_ref(x_7);
x_1000 = lp_dasmodel_CPU_push(x_1, x_999);
x_1001 = !lean_is_exclusive(x_1000);
if (x_1001 == 0)
{
uint16_t x_1002; uint16_t x_1003; lean_object* x_1004; lean_object* x_1005; 
x_1002 = 1;
x_1003 = lean_uint16_add(x_6, x_1002);
lean_ctor_set_uint16(x_1000, sizeof(void*)*3, x_1003);
x_1004 = lean_box(0);
x_1005 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1005, 0, x_1000);
lean_ctor_set(x_1005, 1, x_1004);
lean_ctor_set_uint8(x_1005, sizeof(void*)*2, x_604);
return x_1005;
}
else
{
uint8_t x_1006; uint8_t x_1007; uint8_t x_1008; uint8_t x_1009; lean_object* x_1010; lean_object* x_1011; lean_object* x_1012; uint16_t x_1013; uint16_t x_1014; lean_object* x_1015; lean_object* x_1016; lean_object* x_1017; 
x_1006 = lean_ctor_get_uint8(x_1000, sizeof(void*)*3 + 2);
x_1007 = lean_ctor_get_uint8(x_1000, sizeof(void*)*3 + 3);
x_1008 = lean_ctor_get_uint8(x_1000, sizeof(void*)*3 + 4);
x_1009 = lean_ctor_get_uint8(x_1000, sizeof(void*)*3 + 5);
x_1010 = lean_ctor_get(x_1000, 0);
x_1011 = lean_ctor_get(x_1000, 1);
x_1012 = lean_ctor_get(x_1000, 2);
lean_inc(x_1012);
lean_inc(x_1011);
lean_inc(x_1010);
lean_dec(x_1000);
x_1013 = 1;
x_1014 = lean_uint16_add(x_6, x_1013);
x_1015 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1015, 0, x_1010);
lean_ctor_set(x_1015, 1, x_1011);
lean_ctor_set(x_1015, 2, x_1012);
lean_ctor_set_uint8(x_1015, sizeof(void*)*3 + 2, x_1006);
lean_ctor_set_uint8(x_1015, sizeof(void*)*3 + 3, x_1007);
lean_ctor_set_uint8(x_1015, sizeof(void*)*3 + 4, x_1008);
lean_ctor_set_uint8(x_1015, sizeof(void*)*3 + 5, x_1009);
lean_ctor_set_uint16(x_1015, sizeof(void*)*3, x_1014);
x_1016 = lean_box(0);
x_1017 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1017, 0, x_1015);
lean_ctor_set(x_1017, 1, x_1016);
lean_ctor_set_uint8(x_1017, sizeof(void*)*2, x_604);
return x_1017;
}
}
}
else
{
lean_object* x_1018; lean_object* x_1019; lean_object* x_1020; uint8_t x_1021; 
lean_dec_ref(x_7);
x_1018 = lp_dasmodel_CPU_pull(x_1);
x_1019 = lean_ctor_get(x_1018, 0);
lean_inc(x_1019);
x_1020 = lean_ctor_get(x_1018, 1);
lean_inc(x_1020);
lean_dec_ref(x_1018);
x_1021 = !lean_is_exclusive(x_1019);
if (x_1021 == 0)
{
uint16_t x_1022; lean_object* x_1023; uint16_t x_1024; uint16_t x_1025; uint8_t x_1026; lean_object* x_1027; uint8_t x_1028; lean_object* x_1029; lean_object* x_1030; 
x_1022 = lean_ctor_get_uint16(x_1019, sizeof(void*)*3);
x_1023 = lean_ctor_get(x_1019, 0);
x_1024 = 1;
x_1025 = lean_uint16_add(x_1022, x_1024);
x_1026 = lean_unbox(x_1020);
x_1027 = lp_dasmodel_updateNZ(x_1023, x_1026);
lean_ctor_set(x_1019, 0, x_1027);
x_1028 = lean_unbox(x_1020);
lean_dec(x_1020);
lean_ctor_set_uint8(x_1019, sizeof(void*)*3 + 2, x_1028);
lean_ctor_set_uint16(x_1019, sizeof(void*)*3, x_1025);
x_1029 = lean_box(0);
x_1030 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1030, 0, x_1019);
lean_ctor_set(x_1030, 1, x_1029);
lean_ctor_set_uint8(x_1030, sizeof(void*)*2, x_602);
return x_1030;
}
else
{
uint8_t x_1031; uint8_t x_1032; uint8_t x_1033; uint16_t x_1034; lean_object* x_1035; lean_object* x_1036; lean_object* x_1037; uint16_t x_1038; uint16_t x_1039; uint8_t x_1040; lean_object* x_1041; lean_object* x_1042; uint8_t x_1043; lean_object* x_1044; lean_object* x_1045; 
x_1031 = lean_ctor_get_uint8(x_1019, sizeof(void*)*3 + 3);
x_1032 = lean_ctor_get_uint8(x_1019, sizeof(void*)*3 + 4);
x_1033 = lean_ctor_get_uint8(x_1019, sizeof(void*)*3 + 5);
x_1034 = lean_ctor_get_uint16(x_1019, sizeof(void*)*3);
x_1035 = lean_ctor_get(x_1019, 0);
x_1036 = lean_ctor_get(x_1019, 1);
x_1037 = lean_ctor_get(x_1019, 2);
lean_inc(x_1037);
lean_inc(x_1036);
lean_inc(x_1035);
lean_dec(x_1019);
x_1038 = 1;
x_1039 = lean_uint16_add(x_1034, x_1038);
x_1040 = lean_unbox(x_1020);
x_1041 = lp_dasmodel_updateNZ(x_1035, x_1040);
x_1042 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1042, 0, x_1041);
lean_ctor_set(x_1042, 1, x_1036);
lean_ctor_set(x_1042, 2, x_1037);
x_1043 = lean_unbox(x_1020);
lean_dec(x_1020);
lean_ctor_set_uint8(x_1042, sizeof(void*)*3 + 2, x_1043);
lean_ctor_set_uint8(x_1042, sizeof(void*)*3 + 3, x_1031);
lean_ctor_set_uint8(x_1042, sizeof(void*)*3 + 4, x_1032);
lean_ctor_set_uint8(x_1042, sizeof(void*)*3 + 5, x_1033);
lean_ctor_set_uint16(x_1042, sizeof(void*)*3, x_1039);
x_1044 = lean_box(0);
x_1045 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1045, 0, x_1042);
lean_ctor_set(x_1045, 1, x_1044);
lean_ctor_set_uint8(x_1045, sizeof(void*)*2, x_602);
return x_1045;
}
}
}
else
{
lean_object* x_1046; uint8_t x_1047; 
lean_dec_ref(x_7);
x_1046 = lp_dasmodel_CPU_push(x_1, x_2);
x_1047 = !lean_is_exclusive(x_1046);
if (x_1047 == 0)
{
uint16_t x_1048; uint16_t x_1049; lean_object* x_1050; lean_object* x_1051; 
x_1048 = 1;
x_1049 = lean_uint16_add(x_6, x_1048);
lean_ctor_set_uint16(x_1046, sizeof(void*)*3, x_1049);
x_1050 = lean_box(0);
x_1051 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1051, 0, x_1046);
lean_ctor_set(x_1051, 1, x_1050);
lean_ctor_set_uint8(x_1051, sizeof(void*)*2, x_600);
return x_1051;
}
else
{
uint8_t x_1052; uint8_t x_1053; uint8_t x_1054; uint8_t x_1055; lean_object* x_1056; lean_object* x_1057; lean_object* x_1058; uint16_t x_1059; uint16_t x_1060; lean_object* x_1061; lean_object* x_1062; lean_object* x_1063; 
x_1052 = lean_ctor_get_uint8(x_1046, sizeof(void*)*3 + 2);
x_1053 = lean_ctor_get_uint8(x_1046, sizeof(void*)*3 + 3);
x_1054 = lean_ctor_get_uint8(x_1046, sizeof(void*)*3 + 4);
x_1055 = lean_ctor_get_uint8(x_1046, sizeof(void*)*3 + 5);
x_1056 = lean_ctor_get(x_1046, 0);
x_1057 = lean_ctor_get(x_1046, 1);
x_1058 = lean_ctor_get(x_1046, 2);
lean_inc(x_1058);
lean_inc(x_1057);
lean_inc(x_1056);
lean_dec(x_1046);
x_1059 = 1;
x_1060 = lean_uint16_add(x_6, x_1059);
x_1061 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1061, 0, x_1056);
lean_ctor_set(x_1061, 1, x_1057);
lean_ctor_set(x_1061, 2, x_1058);
lean_ctor_set_uint8(x_1061, sizeof(void*)*3 + 2, x_1052);
lean_ctor_set_uint8(x_1061, sizeof(void*)*3 + 3, x_1053);
lean_ctor_set_uint8(x_1061, sizeof(void*)*3 + 4, x_1054);
lean_ctor_set_uint8(x_1061, sizeof(void*)*3 + 5, x_1055);
lean_ctor_set_uint16(x_1061, sizeof(void*)*3, x_1060);
x_1062 = lean_box(0);
x_1063 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1063, 0, x_1061);
lean_ctor_set(x_1063, 1, x_1062);
lean_ctor_set_uint8(x_1063, sizeof(void*)*2, x_600);
return x_1063;
}
}
}
else
{
lean_object* x_1064; lean_object* x_1065; lean_object* x_1066; lean_object* x_1067; lean_object* x_1068; lean_object* x_1069; uint8_t x_1070; 
lean_dec_ref(x_7);
x_1064 = lp_dasmodel_CPU_pull(x_1);
x_1065 = lean_ctor_get(x_1064, 0);
lean_inc(x_1065);
x_1066 = lean_ctor_get(x_1064, 1);
lean_inc(x_1066);
lean_dec_ref(x_1064);
x_1067 = lp_dasmodel_CPU_pull16(x_1065);
x_1068 = lean_ctor_get(x_1067, 0);
lean_inc(x_1068);
x_1069 = lean_ctor_get(x_1067, 1);
lean_inc(x_1069);
lean_dec_ref(x_1067);
x_1070 = !lean_is_exclusive(x_1068);
if (x_1070 == 0)
{
lean_object* x_1071; uint8_t x_1072; lean_object* x_1073; uint16_t x_1074; lean_object* x_1075; lean_object* x_1076; 
x_1071 = lean_ctor_get(x_1068, 0);
lean_dec(x_1071);
x_1072 = lean_unbox(x_1066);
lean_dec(x_1066);
x_1073 = lp_dasmodel___private_CPU6502_0__byteToFlags(x_1072);
lean_ctor_set(x_1068, 0, x_1073);
x_1074 = lean_unbox(x_1069);
lean_dec(x_1069);
lean_ctor_set_uint16(x_1068, sizeof(void*)*3, x_1074);
x_1075 = lean_box(0);
x_1076 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1076, 0, x_1068);
lean_ctor_set(x_1076, 1, x_1075);
lean_ctor_set_uint8(x_1076, sizeof(void*)*2, x_598);
return x_1076;
}
else
{
uint8_t x_1077; uint8_t x_1078; uint8_t x_1079; uint8_t x_1080; lean_object* x_1081; lean_object* x_1082; uint8_t x_1083; lean_object* x_1084; lean_object* x_1085; uint16_t x_1086; lean_object* x_1087; lean_object* x_1088; 
x_1077 = lean_ctor_get_uint8(x_1068, sizeof(void*)*3 + 2);
x_1078 = lean_ctor_get_uint8(x_1068, sizeof(void*)*3 + 3);
x_1079 = lean_ctor_get_uint8(x_1068, sizeof(void*)*3 + 4);
x_1080 = lean_ctor_get_uint8(x_1068, sizeof(void*)*3 + 5);
x_1081 = lean_ctor_get(x_1068, 1);
x_1082 = lean_ctor_get(x_1068, 2);
lean_inc(x_1082);
lean_inc(x_1081);
lean_dec(x_1068);
x_1083 = lean_unbox(x_1066);
lean_dec(x_1066);
x_1084 = lp_dasmodel___private_CPU6502_0__byteToFlags(x_1083);
x_1085 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1085, 0, x_1084);
lean_ctor_set(x_1085, 1, x_1081);
lean_ctor_set(x_1085, 2, x_1082);
lean_ctor_set_uint8(x_1085, sizeof(void*)*3 + 2, x_1077);
lean_ctor_set_uint8(x_1085, sizeof(void*)*3 + 3, x_1078);
lean_ctor_set_uint8(x_1085, sizeof(void*)*3 + 4, x_1079);
lean_ctor_set_uint8(x_1085, sizeof(void*)*3 + 5, x_1080);
x_1086 = lean_unbox(x_1069);
lean_dec(x_1069);
lean_ctor_set_uint16(x_1085, sizeof(void*)*3, x_1086);
x_1087 = lean_box(0);
x_1088 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1088, 0, x_1085);
lean_ctor_set(x_1088, 1, x_1087);
lean_ctor_set_uint8(x_1088, sizeof(void*)*2, x_598);
return x_1088;
}
}
}
else
{
lean_object* x_1089; lean_object* x_1090; lean_object* x_1091; uint8_t x_1092; 
lean_dec_ref(x_7);
x_1089 = lp_dasmodel_CPU_pull16(x_1);
x_1090 = lean_ctor_get(x_1089, 0);
lean_inc(x_1090);
x_1091 = lean_ctor_get(x_1089, 1);
lean_inc(x_1091);
lean_dec_ref(x_1089);
x_1092 = !lean_is_exclusive(x_1090);
if (x_1092 == 0)
{
uint16_t x_1093; uint16_t x_1094; uint16_t x_1095; lean_object* x_1096; lean_object* x_1097; 
x_1093 = 1;
x_1094 = lean_unbox(x_1091);
lean_dec(x_1091);
x_1095 = lean_uint16_add(x_1094, x_1093);
lean_ctor_set_uint16(x_1090, sizeof(void*)*3, x_1095);
x_1096 = lean_box(0);
x_1097 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1097, 0, x_1090);
lean_ctor_set(x_1097, 1, x_1096);
lean_ctor_set_uint8(x_1097, sizeof(void*)*2, x_596);
return x_1097;
}
else
{
uint8_t x_1098; uint8_t x_1099; uint8_t x_1100; uint8_t x_1101; lean_object* x_1102; lean_object* x_1103; lean_object* x_1104; uint16_t x_1105; uint16_t x_1106; uint16_t x_1107; lean_object* x_1108; lean_object* x_1109; lean_object* x_1110; 
x_1098 = lean_ctor_get_uint8(x_1090, sizeof(void*)*3 + 2);
x_1099 = lean_ctor_get_uint8(x_1090, sizeof(void*)*3 + 3);
x_1100 = lean_ctor_get_uint8(x_1090, sizeof(void*)*3 + 4);
x_1101 = lean_ctor_get_uint8(x_1090, sizeof(void*)*3 + 5);
x_1102 = lean_ctor_get(x_1090, 0);
x_1103 = lean_ctor_get(x_1090, 1);
x_1104 = lean_ctor_get(x_1090, 2);
lean_inc(x_1104);
lean_inc(x_1103);
lean_inc(x_1102);
lean_dec(x_1090);
x_1105 = 1;
x_1106 = lean_unbox(x_1091);
lean_dec(x_1091);
x_1107 = lean_uint16_add(x_1106, x_1105);
x_1108 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1108, 0, x_1102);
lean_ctor_set(x_1108, 1, x_1103);
lean_ctor_set(x_1108, 2, x_1104);
lean_ctor_set_uint8(x_1108, sizeof(void*)*3 + 2, x_1098);
lean_ctor_set_uint8(x_1108, sizeof(void*)*3 + 3, x_1099);
lean_ctor_set_uint8(x_1108, sizeof(void*)*3 + 4, x_1100);
lean_ctor_set_uint8(x_1108, sizeof(void*)*3 + 5, x_1101);
lean_ctor_set_uint16(x_1108, sizeof(void*)*3, x_1107);
x_1109 = lean_box(0);
x_1110 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1110, 0, x_1108);
lean_ctor_set(x_1110, 1, x_1109);
lean_ctor_set_uint8(x_1110, sizeof(void*)*2, x_596);
return x_1110;
}
}
}
else
{
uint16_t x_1111; uint16_t x_1112; uint16_t x_1113; uint16_t x_1114; uint16_t x_1115; lean_object* x_1116; uint8_t x_1117; 
lean_dec_ref(x_7);
x_1111 = 1;
x_1112 = lean_uint16_add(x_6, x_1111);
x_1113 = lp_dasmodel_CPU_read16(x_1, x_1112);
x_1114 = 2;
x_1115 = lean_uint16_add(x_6, x_1114);
x_1116 = lp_dasmodel_CPU_push16(x_1, x_1115);
x_1117 = !lean_is_exclusive(x_1116);
if (x_1117 == 0)
{
lean_object* x_1118; lean_object* x_1119; 
lean_ctor_set_uint16(x_1116, sizeof(void*)*3, x_1113);
x_1118 = lean_box(0);
x_1119 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1119, 0, x_1116);
lean_ctor_set(x_1119, 1, x_1118);
lean_ctor_set_uint8(x_1119, sizeof(void*)*2, x_594);
return x_1119;
}
else
{
uint8_t x_1120; uint8_t x_1121; uint8_t x_1122; uint8_t x_1123; lean_object* x_1124; lean_object* x_1125; lean_object* x_1126; lean_object* x_1127; lean_object* x_1128; lean_object* x_1129; 
x_1120 = lean_ctor_get_uint8(x_1116, sizeof(void*)*3 + 2);
x_1121 = lean_ctor_get_uint8(x_1116, sizeof(void*)*3 + 3);
x_1122 = lean_ctor_get_uint8(x_1116, sizeof(void*)*3 + 4);
x_1123 = lean_ctor_get_uint8(x_1116, sizeof(void*)*3 + 5);
x_1124 = lean_ctor_get(x_1116, 0);
x_1125 = lean_ctor_get(x_1116, 1);
x_1126 = lean_ctor_get(x_1116, 2);
lean_inc(x_1126);
lean_inc(x_1125);
lean_inc(x_1124);
lean_dec(x_1116);
x_1127 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1127, 0, x_1124);
lean_ctor_set(x_1127, 1, x_1125);
lean_ctor_set(x_1127, 2, x_1126);
lean_ctor_set_uint8(x_1127, sizeof(void*)*3 + 2, x_1120);
lean_ctor_set_uint8(x_1127, sizeof(void*)*3 + 3, x_1121);
lean_ctor_set_uint8(x_1127, sizeof(void*)*3 + 4, x_1122);
lean_ctor_set_uint8(x_1127, sizeof(void*)*3 + 5, x_1123);
lean_ctor_set_uint16(x_1127, sizeof(void*)*3, x_1113);
x_1128 = lean_box(0);
x_1129 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1129, 0, x_1127);
lean_ctor_set(x_1129, 1, x_1128);
lean_ctor_set_uint8(x_1129, sizeof(void*)*2, x_594);
return x_1129;
}
}
}
else
{
uint16_t x_1130; uint16_t x_1131; uint16_t x_1132; uint8_t x_1133; uint16_t x_1134; uint16_t x_1156; uint16_t x_1157; uint8_t x_1158; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1130 = 1;
x_1131 = lean_uint16_add(x_6, x_1130);
x_1132 = lp_dasmodel_CPU_read16(x_1, x_1131);
x_1133 = lp_dasmodel_CPU_read(x_1, x_1132);
x_1156 = 255;
x_1157 = lean_uint16_land(x_1132, x_1156);
x_1158 = lean_uint16_dec_eq(x_1157, x_1156);
if (x_1158 == 0)
{
uint16_t x_1159; 
x_1159 = lean_uint16_add(x_1132, x_1130);
x_1134 = x_1159;
goto block_1155;
}
else
{
uint16_t x_1160; uint16_t x_1161; 
x_1160 = 65280;
x_1161 = lean_uint16_land(x_1132, x_1160);
x_1134 = x_1161;
goto block_1155;
}
block_1155:
{
uint8_t x_1135; uint8_t x_1136; 
x_1135 = lp_dasmodel_CPU_read(x_1, x_1134);
x_1136 = !lean_is_exclusive(x_1);
if (x_1136 == 0)
{
lean_object* x_1137; lean_object* x_1138; lean_object* x_1139; uint16_t x_1140; uint16_t x_1141; uint16_t x_1142; uint16_t x_1143; uint16_t x_1144; lean_object* x_1145; lean_object* x_1146; 
x_1137 = lean_ctor_get(x_1, 2);
lean_dec(x_1137);
x_1138 = lean_ctor_get(x_1, 1);
lean_dec(x_1138);
x_1139 = lean_ctor_get(x_1, 0);
lean_dec(x_1139);
x_1140 = lean_uint8_to_uint16(x_1133);
x_1141 = lean_uint8_to_uint16(x_1135);
x_1142 = 8;
x_1143 = lean_uint16_shift_left(x_1141, x_1142);
x_1144 = lean_uint16_lor(x_1140, x_1143);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1144);
x_1145 = lean_box(0);
x_1146 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1146, 0, x_1);
lean_ctor_set(x_1146, 1, x_1145);
lean_ctor_set_uint8(x_1146, sizeof(void*)*2, x_592);
return x_1146;
}
else
{
uint16_t x_1147; uint16_t x_1148; uint16_t x_1149; uint16_t x_1150; uint16_t x_1151; lean_object* x_1152; lean_object* x_1153; lean_object* x_1154; 
lean_dec(x_1);
x_1147 = lean_uint8_to_uint16(x_1133);
x_1148 = lean_uint8_to_uint16(x_1135);
x_1149 = 8;
x_1150 = lean_uint16_shift_left(x_1148, x_1149);
x_1151 = lean_uint16_lor(x_1147, x_1150);
x_1152 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1152, 0, x_7);
lean_ctor_set(x_1152, 1, x_8);
lean_ctor_set(x_1152, 2, x_9);
lean_ctor_set_uint8(x_1152, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_1152, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1152, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1152, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1152, sizeof(void*)*3, x_1151);
x_1153 = lean_box(0);
x_1154 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1154, 0, x_1152);
lean_ctor_set(x_1154, 1, x_1153);
lean_ctor_set_uint8(x_1154, sizeof(void*)*2, x_592);
return x_1154;
}
}
}
}
else
{
uint16_t x_1162; uint16_t x_1163; uint16_t x_1164; uint8_t x_1165; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1162 = 1;
x_1163 = lean_uint16_add(x_6, x_1162);
x_1164 = lp_dasmodel_CPU_read16(x_1, x_1163);
x_1165 = !lean_is_exclusive(x_1);
if (x_1165 == 0)
{
lean_object* x_1166; lean_object* x_1167; lean_object* x_1168; lean_object* x_1169; lean_object* x_1170; 
x_1166 = lean_ctor_get(x_1, 2);
lean_dec(x_1166);
x_1167 = lean_ctor_get(x_1, 1);
lean_dec(x_1167);
x_1168 = lean_ctor_get(x_1, 0);
lean_dec(x_1168);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1164);
x_1169 = lean_box(0);
x_1170 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1170, 0, x_1);
lean_ctor_set(x_1170, 1, x_1169);
lean_ctor_set_uint8(x_1170, sizeof(void*)*2, x_590);
return x_1170;
}
else
{
lean_object* x_1171; lean_object* x_1172; lean_object* x_1173; 
lean_dec(x_1);
x_1171 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1171, 0, x_7);
lean_ctor_set(x_1171, 1, x_8);
lean_ctor_set(x_1171, 2, x_9);
lean_ctor_set_uint8(x_1171, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_1171, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1171, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1171, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1171, sizeof(void*)*3, x_1164);
x_1172 = lean_box(0);
x_1173 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1173, 0, x_1171);
lean_ctor_set(x_1173, 1, x_1172);
lean_ctor_set_uint8(x_1173, sizeof(void*)*2, x_590);
return x_1173;
}
}
}
else
{
uint8_t x_1174; lean_object* x_1175; 
x_1174 = lean_ctor_get_uint8(x_7, 4);
lean_dec_ref(x_7);
x_1175 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_1174);
return x_1175;
}
}
else
{
uint8_t x_1176; 
x_1176 = lean_ctor_get_uint8(x_7, 4);
lean_dec_ref(x_7);
if (x_1176 == 0)
{
lean_object* x_1177; 
x_1177 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_588);
return x_1177;
}
else
{
lean_object* x_1178; 
x_1178 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_586);
return x_1178;
}
}
}
else
{
uint8_t x_1179; 
x_1179 = lean_ctor_get_uint8(x_7, 5);
lean_dec_ref(x_7);
if (x_1179 == 0)
{
lean_object* x_1180; 
x_1180 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_586);
return x_1180;
}
else
{
lean_object* x_1181; 
x_1181 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_584);
return x_1181;
}
}
}
else
{
uint8_t x_1182; lean_object* x_1183; 
x_1182 = lean_ctor_get_uint8(x_7, 5);
lean_dec_ref(x_7);
x_1183 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_1182);
return x_1183;
}
}
else
{
uint8_t x_1184; 
x_1184 = lean_ctor_get_uint8(x_7, 1);
lean_dec_ref(x_7);
if (x_1184 == 0)
{
lean_object* x_1185; 
x_1185 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_582);
return x_1185;
}
else
{
lean_object* x_1186; 
x_1186 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_580);
return x_1186;
}
}
}
else
{
uint8_t x_1187; lean_object* x_1188; 
x_1187 = lean_ctor_get_uint8(x_7, 1);
lean_dec_ref(x_7);
x_1188 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_1187);
return x_1188;
}
}
else
{
uint8_t x_1189; lean_object* x_1190; 
x_1189 = lean_ctor_get_uint8(x_7, 0);
lean_dec_ref(x_7);
x_1190 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_1189);
return x_1190;
}
}
else
{
uint8_t x_1191; 
x_1191 = lean_ctor_get_uint8(x_7, 0);
lean_dec_ref(x_7);
if (x_1191 == 0)
{
lean_object* x_1192; 
x_1192 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_576);
return x_1192;
}
else
{
lean_object* x_1193; 
x_1193 = lp_dasmodel___private_CPU6502_0__doBranch(x_1, x_574);
return x_1193;
}
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_570;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_570;
}
}
else
{
lean_object* x_1194; lean_object* x_1195; 
lean_dec_ref(x_7);
x_1194 = ((lean_object*)(lp_dasmodel_stepRaw___closed__0));
x_1195 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_309, x_1194);
return x_1195;
}
block_526:
{
lean_object* x_522; lean_object* x_523; lean_object* x_524; lean_object* x_525; 
x_522 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_522, 0, x_512);
lean_ctor_set_uint8(x_522, 1, x_514);
lean_ctor_set_uint8(x_522, 2, x_520);
lean_ctor_set_uint8(x_522, 3, x_517);
lean_ctor_set_uint8(x_522, 4, x_516);
lean_ctor_set_uint8(x_522, 5, x_521);
x_523 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_523, 0, x_522);
lean_ctor_set(x_523, 1, x_510);
lean_ctor_set(x_523, 2, x_518);
lean_ctor_set_uint8(x_523, sizeof(void*)*3 + 2, x_513);
lean_ctor_set_uint8(x_523, sizeof(void*)*3 + 3, x_509);
lean_ctor_set_uint8(x_523, sizeof(void*)*3 + 4, x_511);
lean_ctor_set_uint8(x_523, sizeof(void*)*3 + 5, x_519);
lean_ctor_set_uint16(x_523, sizeof(void*)*3, x_515);
x_524 = lean_box(0);
x_525 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_525, 0, x_523);
lean_ctor_set(x_525, 1, x_524);
lean_ctor_set_uint8(x_525, sizeof(void*)*2, x_508);
return x_525;
}
block_545:
{
uint8_t x_541; uint8_t x_542; uint8_t x_543; 
x_541 = 128;
x_542 = lean_uint8_land(x_531, x_541);
x_543 = lean_uint8_dec_eq(x_542, x_538);
if (x_543 == 0)
{
uint8_t x_544; 
x_544 = 1;
x_509 = x_527;
x_510 = x_528;
x_511 = x_529;
x_512 = x_536;
x_513 = x_530;
x_514 = x_537;
x_515 = x_532;
x_516 = x_540;
x_517 = x_533;
x_518 = x_534;
x_519 = x_535;
x_520 = x_539;
x_521 = x_544;
goto block_526;
}
else
{
x_509 = x_527;
x_510 = x_528;
x_511 = x_529;
x_512 = x_536;
x_513 = x_530;
x_514 = x_537;
x_515 = x_532;
x_516 = x_540;
x_517 = x_533;
x_518 = x_534;
x_519 = x_535;
x_520 = x_539;
x_521 = x_508;
goto block_526;
}
}
block_566:
{
lean_object* x_547; lean_object* x_548; lean_object* x_549; uint8_t x_550; uint8_t x_551; uint8_t x_552; uint8_t x_553; uint8_t x_554; uint8_t x_555; uint8_t x_556; uint8_t x_557; uint8_t x_558; uint8_t x_559; uint8_t x_560; 
x_547 = lp_dasmodel_CPU_fetchOperand(x_1, x_546);
lean_dec_ref(x_1);
x_548 = lean_ctor_get(x_547, 0);
lean_inc(x_548);
x_549 = lean_ctor_get(x_547, 1);
lean_inc(x_549);
lean_dec_ref(x_547);
x_550 = lean_ctor_get_uint8(x_7, 0);
x_551 = lean_ctor_get_uint8(x_7, 2);
x_552 = lean_ctor_get_uint8(x_7, 3);
lean_dec_ref(x_7);
x_553 = lean_unbox(x_548);
x_554 = lean_uint8_land(x_2, x_553);
x_555 = 0;
x_556 = lean_uint8_dec_eq(x_554, x_555);
x_557 = 64;
x_558 = lean_unbox(x_548);
x_559 = lean_uint8_land(x_558, x_557);
x_560 = lean_uint8_dec_eq(x_559, x_555);
if (x_560 == 0)
{
uint8_t x_561; uint8_t x_562; uint16_t x_563; 
x_561 = 1;
x_562 = lean_unbox(x_548);
lean_dec(x_548);
x_563 = lean_unbox(x_549);
lean_dec(x_549);
x_527 = x_3;
x_528 = x_8;
x_529 = x_4;
x_530 = x_2;
x_531 = x_562;
x_532 = x_563;
x_533 = x_552;
x_534 = x_9;
x_535 = x_5;
x_536 = x_550;
x_537 = x_556;
x_538 = x_555;
x_539 = x_551;
x_540 = x_561;
goto block_545;
}
else
{
uint8_t x_564; uint16_t x_565; 
x_564 = lean_unbox(x_548);
lean_dec(x_548);
x_565 = lean_unbox(x_549);
lean_dec(x_549);
x_527 = x_3;
x_528 = x_8;
x_529 = x_4;
x_530 = x_2;
x_531 = x_564;
x_532 = x_565;
x_533 = x_552;
x_534 = x_9;
x_535 = x_5;
x_536 = x_550;
x_537 = x_556;
x_538 = x_555;
x_539 = x_551;
x_540 = x_508;
goto block_545;
}
}
block_570:
{
uint8_t x_567; uint8_t x_568; 
x_567 = 36;
x_568 = lean_uint8_dec_eq(x_10, x_567);
if (x_568 == 0)
{
lean_object* x_569; 
x_569 = lean_unsigned_to_nat(4u);
x_546 = x_569;
goto block_566;
}
else
{
x_546 = x_319;
goto block_566;
}
}
}
else
{
lean_object* x_1196; lean_object* x_1197; lean_object* x_1198; 
lean_dec_ref(x_7);
x_1196 = lean_unsigned_to_nat(4u);
x_1197 = ((lean_object*)(lp_dasmodel_stepRaw___closed__0));
x_1198 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1196, x_1197);
return x_1198;
}
}
else
{
lean_object* x_1199; lean_object* x_1200; lean_object* x_1201; 
lean_dec_ref(x_7);
x_1199 = lean_unsigned_to_nat(2u);
x_1200 = ((lean_object*)(lp_dasmodel_stepRaw___closed__0));
x_1201 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1199, x_1200);
return x_1201;
}
}
else
{
lean_object* x_1202; lean_object* x_1203; 
lean_dec_ref(x_7);
x_1202 = ((lean_object*)(lp_dasmodel_stepRaw___closed__0));
x_1203 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_319, x_1202);
return x_1203;
}
}
else
{
uint8_t x_1204; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1204 = !lean_is_exclusive(x_1);
if (x_1204 == 0)
{
lean_object* x_1205; lean_object* x_1206; lean_object* x_1207; uint8_t x_1208; lean_object* x_1209; lean_object* x_1210; lean_object* x_1211; uint8_t x_1212; lean_object* x_1213; uint8_t x_1214; 
x_1205 = lean_ctor_get(x_1, 2);
lean_dec(x_1205);
x_1206 = lean_ctor_get(x_1, 1);
lean_dec(x_1206);
x_1207 = lean_ctor_get(x_1, 0);
lean_dec(x_1207);
x_1208 = lean_ctor_get_uint8(x_7, 0);
x_1209 = lp_dasmodel___private_CPU6502_0__rorOp(x_2, x_1208);
x_1210 = lean_ctor_get(x_1209, 0);
lean_inc(x_1210);
x_1211 = lean_ctor_get(x_1209, 1);
lean_inc(x_1211);
lean_dec_ref(x_1209);
x_1212 = lean_unbox(x_1210);
x_1213 = lp_dasmodel_updateNZ(x_7, x_1212);
x_1214 = !lean_is_exclusive(x_1213);
if (x_1214 == 0)
{
uint16_t x_1215; uint16_t x_1216; uint8_t x_1217; uint8_t x_1218; lean_object* x_1219; lean_object* x_1220; 
x_1215 = 1;
x_1216 = lean_uint16_add(x_6, x_1215);
x_1217 = lean_unbox(x_1211);
lean_dec(x_1211);
lean_ctor_set_uint8(x_1213, 0, x_1217);
lean_ctor_set(x_1, 0, x_1213);
x_1218 = lean_unbox(x_1210);
lean_dec(x_1210);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1218);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1216);
x_1219 = lean_box(0);
x_1220 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1220, 0, x_1);
lean_ctor_set(x_1220, 1, x_1219);
lean_ctor_set_uint8(x_1220, sizeof(void*)*2, x_498);
return x_1220;
}
else
{
uint8_t x_1221; uint8_t x_1222; uint8_t x_1223; uint8_t x_1224; uint8_t x_1225; uint16_t x_1226; uint16_t x_1227; lean_object* x_1228; uint8_t x_1229; uint8_t x_1230; lean_object* x_1231; lean_object* x_1232; 
x_1221 = lean_ctor_get_uint8(x_1213, 1);
x_1222 = lean_ctor_get_uint8(x_1213, 2);
x_1223 = lean_ctor_get_uint8(x_1213, 3);
x_1224 = lean_ctor_get_uint8(x_1213, 4);
x_1225 = lean_ctor_get_uint8(x_1213, 5);
lean_dec(x_1213);
x_1226 = 1;
x_1227 = lean_uint16_add(x_6, x_1226);
x_1228 = lean_alloc_ctor(0, 0, 6);
x_1229 = lean_unbox(x_1211);
lean_dec(x_1211);
lean_ctor_set_uint8(x_1228, 0, x_1229);
lean_ctor_set_uint8(x_1228, 1, x_1221);
lean_ctor_set_uint8(x_1228, 2, x_1222);
lean_ctor_set_uint8(x_1228, 3, x_1223);
lean_ctor_set_uint8(x_1228, 4, x_1224);
lean_ctor_set_uint8(x_1228, 5, x_1225);
lean_ctor_set(x_1, 0, x_1228);
x_1230 = lean_unbox(x_1210);
lean_dec(x_1210);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1230);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1227);
x_1231 = lean_box(0);
x_1232 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1232, 0, x_1);
lean_ctor_set(x_1232, 1, x_1231);
lean_ctor_set_uint8(x_1232, sizeof(void*)*2, x_498);
return x_1232;
}
}
else
{
uint8_t x_1233; lean_object* x_1234; lean_object* x_1235; lean_object* x_1236; uint8_t x_1237; lean_object* x_1238; uint8_t x_1239; uint8_t x_1240; uint8_t x_1241; uint8_t x_1242; uint8_t x_1243; lean_object* x_1244; uint16_t x_1245; uint16_t x_1246; lean_object* x_1247; uint8_t x_1248; lean_object* x_1249; uint8_t x_1250; lean_object* x_1251; lean_object* x_1252; 
lean_dec(x_1);
x_1233 = lean_ctor_get_uint8(x_7, 0);
x_1234 = lp_dasmodel___private_CPU6502_0__rorOp(x_2, x_1233);
x_1235 = lean_ctor_get(x_1234, 0);
lean_inc(x_1235);
x_1236 = lean_ctor_get(x_1234, 1);
lean_inc(x_1236);
lean_dec_ref(x_1234);
x_1237 = lean_unbox(x_1235);
x_1238 = lp_dasmodel_updateNZ(x_7, x_1237);
x_1239 = lean_ctor_get_uint8(x_1238, 1);
x_1240 = lean_ctor_get_uint8(x_1238, 2);
x_1241 = lean_ctor_get_uint8(x_1238, 3);
x_1242 = lean_ctor_get_uint8(x_1238, 4);
x_1243 = lean_ctor_get_uint8(x_1238, 5);
if (lean_is_exclusive(x_1238)) {
 x_1244 = x_1238;
} else {
 lean_dec_ref(x_1238);
 x_1244 = lean_box(0);
}
x_1245 = 1;
x_1246 = lean_uint16_add(x_6, x_1245);
if (lean_is_scalar(x_1244)) {
 x_1247 = lean_alloc_ctor(0, 0, 6);
} else {
 x_1247 = x_1244;
}
x_1248 = lean_unbox(x_1236);
lean_dec(x_1236);
lean_ctor_set_uint8(x_1247, 0, x_1248);
lean_ctor_set_uint8(x_1247, 1, x_1239);
lean_ctor_set_uint8(x_1247, 2, x_1240);
lean_ctor_set_uint8(x_1247, 3, x_1241);
lean_ctor_set_uint8(x_1247, 4, x_1242);
lean_ctor_set_uint8(x_1247, 5, x_1243);
x_1249 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1249, 0, x_1247);
lean_ctor_set(x_1249, 1, x_8);
lean_ctor_set(x_1249, 2, x_9);
x_1250 = lean_unbox(x_1235);
lean_dec(x_1235);
lean_ctor_set_uint8(x_1249, sizeof(void*)*3 + 2, x_1250);
lean_ctor_set_uint8(x_1249, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1249, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1249, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1249, sizeof(void*)*3, x_1246);
x_1251 = lean_box(0);
x_1252 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1252, 0, x_1249);
lean_ctor_set(x_1252, 1, x_1251);
lean_ctor_set_uint8(x_1252, sizeof(void*)*2, x_498);
return x_1252;
}
}
}
else
{
lean_object* x_1253; lean_object* x_1254; 
lean_dec_ref(x_7);
x_1253 = ((lean_object*)(lp_dasmodel_stepRaw___closed__1));
x_1254 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_309, x_1253);
return x_1254;
}
}
else
{
lean_object* x_1255; lean_object* x_1256; lean_object* x_1257; 
lean_dec_ref(x_7);
x_1255 = lean_unsigned_to_nat(4u);
x_1256 = ((lean_object*)(lp_dasmodel_stepRaw___closed__1));
x_1257 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1255, x_1256);
return x_1257;
}
}
else
{
lean_object* x_1258; lean_object* x_1259; lean_object* x_1260; 
lean_dec_ref(x_7);
x_1258 = lean_unsigned_to_nat(2u);
x_1259 = ((lean_object*)(lp_dasmodel_stepRaw___closed__1));
x_1260 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1258, x_1259);
return x_1260;
}
}
else
{
lean_object* x_1261; lean_object* x_1262; 
lean_dec_ref(x_7);
x_1261 = ((lean_object*)(lp_dasmodel_stepRaw___closed__1));
x_1262 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_319, x_1261);
return x_1262;
}
}
else
{
uint8_t x_1263; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1263 = !lean_is_exclusive(x_1);
if (x_1263 == 0)
{
lean_object* x_1264; lean_object* x_1265; lean_object* x_1266; uint8_t x_1267; lean_object* x_1268; lean_object* x_1269; lean_object* x_1270; uint8_t x_1271; lean_object* x_1272; uint8_t x_1273; 
x_1264 = lean_ctor_get(x_1, 2);
lean_dec(x_1264);
x_1265 = lean_ctor_get(x_1, 1);
lean_dec(x_1265);
x_1266 = lean_ctor_get(x_1, 0);
lean_dec(x_1266);
x_1267 = lean_ctor_get_uint8(x_7, 0);
x_1268 = lp_dasmodel___private_CPU6502_0__rolOp(x_2, x_1267);
x_1269 = lean_ctor_get(x_1268, 0);
lean_inc(x_1269);
x_1270 = lean_ctor_get(x_1268, 1);
lean_inc(x_1270);
lean_dec_ref(x_1268);
x_1271 = lean_unbox(x_1269);
x_1272 = lp_dasmodel_updateNZ(x_7, x_1271);
x_1273 = !lean_is_exclusive(x_1272);
if (x_1273 == 0)
{
uint16_t x_1274; uint16_t x_1275; uint8_t x_1276; uint8_t x_1277; lean_object* x_1278; lean_object* x_1279; 
x_1274 = 1;
x_1275 = lean_uint16_add(x_6, x_1274);
x_1276 = lean_unbox(x_1270);
lean_dec(x_1270);
lean_ctor_set_uint8(x_1272, 0, x_1276);
lean_ctor_set(x_1, 0, x_1272);
x_1277 = lean_unbox(x_1269);
lean_dec(x_1269);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1277);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1275);
x_1278 = lean_box(0);
x_1279 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1279, 0, x_1);
lean_ctor_set(x_1279, 1, x_1278);
lean_ctor_set_uint8(x_1279, sizeof(void*)*2, x_488);
return x_1279;
}
else
{
uint8_t x_1280; uint8_t x_1281; uint8_t x_1282; uint8_t x_1283; uint8_t x_1284; uint16_t x_1285; uint16_t x_1286; lean_object* x_1287; uint8_t x_1288; uint8_t x_1289; lean_object* x_1290; lean_object* x_1291; 
x_1280 = lean_ctor_get_uint8(x_1272, 1);
x_1281 = lean_ctor_get_uint8(x_1272, 2);
x_1282 = lean_ctor_get_uint8(x_1272, 3);
x_1283 = lean_ctor_get_uint8(x_1272, 4);
x_1284 = lean_ctor_get_uint8(x_1272, 5);
lean_dec(x_1272);
x_1285 = 1;
x_1286 = lean_uint16_add(x_6, x_1285);
x_1287 = lean_alloc_ctor(0, 0, 6);
x_1288 = lean_unbox(x_1270);
lean_dec(x_1270);
lean_ctor_set_uint8(x_1287, 0, x_1288);
lean_ctor_set_uint8(x_1287, 1, x_1280);
lean_ctor_set_uint8(x_1287, 2, x_1281);
lean_ctor_set_uint8(x_1287, 3, x_1282);
lean_ctor_set_uint8(x_1287, 4, x_1283);
lean_ctor_set_uint8(x_1287, 5, x_1284);
lean_ctor_set(x_1, 0, x_1287);
x_1289 = lean_unbox(x_1269);
lean_dec(x_1269);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1289);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1286);
x_1290 = lean_box(0);
x_1291 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1291, 0, x_1);
lean_ctor_set(x_1291, 1, x_1290);
lean_ctor_set_uint8(x_1291, sizeof(void*)*2, x_488);
return x_1291;
}
}
else
{
uint8_t x_1292; lean_object* x_1293; lean_object* x_1294; lean_object* x_1295; uint8_t x_1296; lean_object* x_1297; uint8_t x_1298; uint8_t x_1299; uint8_t x_1300; uint8_t x_1301; uint8_t x_1302; lean_object* x_1303; uint16_t x_1304; uint16_t x_1305; lean_object* x_1306; uint8_t x_1307; lean_object* x_1308; uint8_t x_1309; lean_object* x_1310; lean_object* x_1311; 
lean_dec(x_1);
x_1292 = lean_ctor_get_uint8(x_7, 0);
x_1293 = lp_dasmodel___private_CPU6502_0__rolOp(x_2, x_1292);
x_1294 = lean_ctor_get(x_1293, 0);
lean_inc(x_1294);
x_1295 = lean_ctor_get(x_1293, 1);
lean_inc(x_1295);
lean_dec_ref(x_1293);
x_1296 = lean_unbox(x_1294);
x_1297 = lp_dasmodel_updateNZ(x_7, x_1296);
x_1298 = lean_ctor_get_uint8(x_1297, 1);
x_1299 = lean_ctor_get_uint8(x_1297, 2);
x_1300 = lean_ctor_get_uint8(x_1297, 3);
x_1301 = lean_ctor_get_uint8(x_1297, 4);
x_1302 = lean_ctor_get_uint8(x_1297, 5);
if (lean_is_exclusive(x_1297)) {
 x_1303 = x_1297;
} else {
 lean_dec_ref(x_1297);
 x_1303 = lean_box(0);
}
x_1304 = 1;
x_1305 = lean_uint16_add(x_6, x_1304);
if (lean_is_scalar(x_1303)) {
 x_1306 = lean_alloc_ctor(0, 0, 6);
} else {
 x_1306 = x_1303;
}
x_1307 = lean_unbox(x_1295);
lean_dec(x_1295);
lean_ctor_set_uint8(x_1306, 0, x_1307);
lean_ctor_set_uint8(x_1306, 1, x_1298);
lean_ctor_set_uint8(x_1306, 2, x_1299);
lean_ctor_set_uint8(x_1306, 3, x_1300);
lean_ctor_set_uint8(x_1306, 4, x_1301);
lean_ctor_set_uint8(x_1306, 5, x_1302);
x_1308 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1308, 0, x_1306);
lean_ctor_set(x_1308, 1, x_8);
lean_ctor_set(x_1308, 2, x_9);
x_1309 = lean_unbox(x_1294);
lean_dec(x_1294);
lean_ctor_set_uint8(x_1308, sizeof(void*)*3 + 2, x_1309);
lean_ctor_set_uint8(x_1308, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1308, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1308, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1308, sizeof(void*)*3, x_1305);
x_1310 = lean_box(0);
x_1311 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1311, 0, x_1308);
lean_ctor_set(x_1311, 1, x_1310);
lean_ctor_set_uint8(x_1311, sizeof(void*)*2, x_488);
return x_1311;
}
}
}
else
{
lean_object* x_1312; lean_object* x_1313; 
lean_dec_ref(x_7);
x_1312 = ((lean_object*)(lp_dasmodel_stepRaw___closed__2));
x_1313 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_309, x_1312);
return x_1313;
}
}
else
{
lean_object* x_1314; lean_object* x_1315; lean_object* x_1316; 
lean_dec_ref(x_7);
x_1314 = lean_unsigned_to_nat(4u);
x_1315 = ((lean_object*)(lp_dasmodel_stepRaw___closed__2));
x_1316 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1314, x_1315);
return x_1316;
}
}
else
{
lean_object* x_1317; lean_object* x_1318; lean_object* x_1319; 
lean_dec_ref(x_7);
x_1317 = lean_unsigned_to_nat(2u);
x_1318 = ((lean_object*)(lp_dasmodel_stepRaw___closed__2));
x_1319 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1317, x_1318);
return x_1319;
}
}
else
{
lean_object* x_1320; lean_object* x_1321; 
lean_dec_ref(x_7);
x_1320 = ((lean_object*)(lp_dasmodel_stepRaw___closed__2));
x_1321 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_319, x_1320);
return x_1321;
}
}
else
{
uint8_t x_1322; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1322 = !lean_is_exclusive(x_1);
if (x_1322 == 0)
{
lean_object* x_1323; lean_object* x_1324; lean_object* x_1325; lean_object* x_1326; lean_object* x_1327; lean_object* x_1328; uint8_t x_1329; lean_object* x_1330; uint8_t x_1331; 
x_1323 = lean_ctor_get(x_1, 2);
lean_dec(x_1323);
x_1324 = lean_ctor_get(x_1, 1);
lean_dec(x_1324);
x_1325 = lean_ctor_get(x_1, 0);
lean_dec(x_1325);
x_1326 = lp_dasmodel___private_CPU6502_0__lsrOp___redArg(x_2);
x_1327 = lean_ctor_get(x_1326, 0);
lean_inc(x_1327);
x_1328 = lean_ctor_get(x_1326, 1);
lean_inc(x_1328);
lean_dec_ref(x_1326);
x_1329 = lean_unbox(x_1327);
x_1330 = lp_dasmodel_updateNZ(x_7, x_1329);
x_1331 = !lean_is_exclusive(x_1330);
if (x_1331 == 0)
{
uint16_t x_1332; uint16_t x_1333; uint8_t x_1334; uint8_t x_1335; lean_object* x_1336; lean_object* x_1337; 
x_1332 = 1;
x_1333 = lean_uint16_add(x_6, x_1332);
x_1334 = lean_unbox(x_1328);
lean_dec(x_1328);
lean_ctor_set_uint8(x_1330, 0, x_1334);
lean_ctor_set(x_1, 0, x_1330);
x_1335 = lean_unbox(x_1327);
lean_dec(x_1327);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1335);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1333);
x_1336 = lean_box(0);
x_1337 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1337, 0, x_1);
lean_ctor_set(x_1337, 1, x_1336);
lean_ctor_set_uint8(x_1337, sizeof(void*)*2, x_478);
return x_1337;
}
else
{
uint8_t x_1338; uint8_t x_1339; uint8_t x_1340; uint8_t x_1341; uint8_t x_1342; uint16_t x_1343; uint16_t x_1344; lean_object* x_1345; uint8_t x_1346; uint8_t x_1347; lean_object* x_1348; lean_object* x_1349; 
x_1338 = lean_ctor_get_uint8(x_1330, 1);
x_1339 = lean_ctor_get_uint8(x_1330, 2);
x_1340 = lean_ctor_get_uint8(x_1330, 3);
x_1341 = lean_ctor_get_uint8(x_1330, 4);
x_1342 = lean_ctor_get_uint8(x_1330, 5);
lean_dec(x_1330);
x_1343 = 1;
x_1344 = lean_uint16_add(x_6, x_1343);
x_1345 = lean_alloc_ctor(0, 0, 6);
x_1346 = lean_unbox(x_1328);
lean_dec(x_1328);
lean_ctor_set_uint8(x_1345, 0, x_1346);
lean_ctor_set_uint8(x_1345, 1, x_1338);
lean_ctor_set_uint8(x_1345, 2, x_1339);
lean_ctor_set_uint8(x_1345, 3, x_1340);
lean_ctor_set_uint8(x_1345, 4, x_1341);
lean_ctor_set_uint8(x_1345, 5, x_1342);
lean_ctor_set(x_1, 0, x_1345);
x_1347 = lean_unbox(x_1327);
lean_dec(x_1327);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1347);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1344);
x_1348 = lean_box(0);
x_1349 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1349, 0, x_1);
lean_ctor_set(x_1349, 1, x_1348);
lean_ctor_set_uint8(x_1349, sizeof(void*)*2, x_478);
return x_1349;
}
}
else
{
lean_object* x_1350; lean_object* x_1351; lean_object* x_1352; uint8_t x_1353; lean_object* x_1354; uint8_t x_1355; uint8_t x_1356; uint8_t x_1357; uint8_t x_1358; uint8_t x_1359; lean_object* x_1360; uint16_t x_1361; uint16_t x_1362; lean_object* x_1363; uint8_t x_1364; lean_object* x_1365; uint8_t x_1366; lean_object* x_1367; lean_object* x_1368; 
lean_dec(x_1);
x_1350 = lp_dasmodel___private_CPU6502_0__lsrOp___redArg(x_2);
x_1351 = lean_ctor_get(x_1350, 0);
lean_inc(x_1351);
x_1352 = lean_ctor_get(x_1350, 1);
lean_inc(x_1352);
lean_dec_ref(x_1350);
x_1353 = lean_unbox(x_1351);
x_1354 = lp_dasmodel_updateNZ(x_7, x_1353);
x_1355 = lean_ctor_get_uint8(x_1354, 1);
x_1356 = lean_ctor_get_uint8(x_1354, 2);
x_1357 = lean_ctor_get_uint8(x_1354, 3);
x_1358 = lean_ctor_get_uint8(x_1354, 4);
x_1359 = lean_ctor_get_uint8(x_1354, 5);
if (lean_is_exclusive(x_1354)) {
 x_1360 = x_1354;
} else {
 lean_dec_ref(x_1354);
 x_1360 = lean_box(0);
}
x_1361 = 1;
x_1362 = lean_uint16_add(x_6, x_1361);
if (lean_is_scalar(x_1360)) {
 x_1363 = lean_alloc_ctor(0, 0, 6);
} else {
 x_1363 = x_1360;
}
x_1364 = lean_unbox(x_1352);
lean_dec(x_1352);
lean_ctor_set_uint8(x_1363, 0, x_1364);
lean_ctor_set_uint8(x_1363, 1, x_1355);
lean_ctor_set_uint8(x_1363, 2, x_1356);
lean_ctor_set_uint8(x_1363, 3, x_1357);
lean_ctor_set_uint8(x_1363, 4, x_1358);
lean_ctor_set_uint8(x_1363, 5, x_1359);
x_1365 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1365, 0, x_1363);
lean_ctor_set(x_1365, 1, x_8);
lean_ctor_set(x_1365, 2, x_9);
x_1366 = lean_unbox(x_1351);
lean_dec(x_1351);
lean_ctor_set_uint8(x_1365, sizeof(void*)*3 + 2, x_1366);
lean_ctor_set_uint8(x_1365, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1365, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1365, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1365, sizeof(void*)*3, x_1362);
x_1367 = lean_box(0);
x_1368 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1368, 0, x_1365);
lean_ctor_set(x_1368, 1, x_1367);
lean_ctor_set_uint8(x_1368, sizeof(void*)*2, x_478);
return x_1368;
}
}
}
else
{
lean_object* x_1369; lean_object* x_1370; 
lean_dec_ref(x_7);
x_1369 = ((lean_object*)(lp_dasmodel_stepRaw___closed__3));
x_1370 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_309, x_1369);
return x_1370;
}
}
else
{
lean_object* x_1371; lean_object* x_1372; lean_object* x_1373; 
lean_dec_ref(x_7);
x_1371 = lean_unsigned_to_nat(4u);
x_1372 = ((lean_object*)(lp_dasmodel_stepRaw___closed__3));
x_1373 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1371, x_1372);
return x_1373;
}
}
else
{
lean_object* x_1374; lean_object* x_1375; lean_object* x_1376; 
lean_dec_ref(x_7);
x_1374 = lean_unsigned_to_nat(2u);
x_1375 = ((lean_object*)(lp_dasmodel_stepRaw___closed__3));
x_1376 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_1374, x_1375);
return x_1376;
}
}
else
{
lean_object* x_1377; lean_object* x_1378; 
lean_dec_ref(x_7);
x_1377 = ((lean_object*)(lp_dasmodel_stepRaw___closed__3));
x_1378 = lp_dasmodel___private_CPU6502_0__doShiftMem(x_1, x_319, x_1377);
return x_1378;
}
}
else
{
uint8_t x_1379; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1379 = !lean_is_exclusive(x_1);
if (x_1379 == 0)
{
lean_object* x_1380; lean_object* x_1381; lean_object* x_1382; lean_object* x_1383; lean_object* x_1384; lean_object* x_1385; uint8_t x_1386; lean_object* x_1387; uint8_t x_1388; 
x_1380 = lean_ctor_get(x_1, 2);
lean_dec(x_1380);
x_1381 = lean_ctor_get(x_1, 1);
lean_dec(x_1381);
x_1382 = lean_ctor_get(x_1, 0);
lean_dec(x_1382);
x_1383 = lp_dasmodel___private_CPU6502_0__aslOp___redArg(x_2);
x_1384 = lean_ctor_get(x_1383, 0);
lean_inc(x_1384);
x_1385 = lean_ctor_get(x_1383, 1);
lean_inc(x_1385);
lean_dec_ref(x_1383);
x_1386 = lean_unbox(x_1384);
x_1387 = lp_dasmodel_updateNZ(x_7, x_1386);
x_1388 = !lean_is_exclusive(x_1387);
if (x_1388 == 0)
{
uint16_t x_1389; uint16_t x_1390; uint8_t x_1391; uint8_t x_1392; lean_object* x_1393; lean_object* x_1394; 
x_1389 = 1;
x_1390 = lean_uint16_add(x_6, x_1389);
x_1391 = lean_unbox(x_1385);
lean_dec(x_1385);
lean_ctor_set_uint8(x_1387, 0, x_1391);
lean_ctor_set(x_1, 0, x_1387);
x_1392 = lean_unbox(x_1384);
lean_dec(x_1384);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1392);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1390);
x_1393 = lean_box(0);
x_1394 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1394, 0, x_1);
lean_ctor_set(x_1394, 1, x_1393);
lean_ctor_set_uint8(x_1394, sizeof(void*)*2, x_468);
return x_1394;
}
else
{
uint8_t x_1395; uint8_t x_1396; uint8_t x_1397; uint8_t x_1398; uint8_t x_1399; uint16_t x_1400; uint16_t x_1401; lean_object* x_1402; uint8_t x_1403; uint8_t x_1404; lean_object* x_1405; lean_object* x_1406; 
x_1395 = lean_ctor_get_uint8(x_1387, 1);
x_1396 = lean_ctor_get_uint8(x_1387, 2);
x_1397 = lean_ctor_get_uint8(x_1387, 3);
x_1398 = lean_ctor_get_uint8(x_1387, 4);
x_1399 = lean_ctor_get_uint8(x_1387, 5);
lean_dec(x_1387);
x_1400 = 1;
x_1401 = lean_uint16_add(x_6, x_1400);
x_1402 = lean_alloc_ctor(0, 0, 6);
x_1403 = lean_unbox(x_1385);
lean_dec(x_1385);
lean_ctor_set_uint8(x_1402, 0, x_1403);
lean_ctor_set_uint8(x_1402, 1, x_1395);
lean_ctor_set_uint8(x_1402, 2, x_1396);
lean_ctor_set_uint8(x_1402, 3, x_1397);
lean_ctor_set_uint8(x_1402, 4, x_1398);
lean_ctor_set_uint8(x_1402, 5, x_1399);
lean_ctor_set(x_1, 0, x_1402);
x_1404 = lean_unbox(x_1384);
lean_dec(x_1384);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_1404);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1401);
x_1405 = lean_box(0);
x_1406 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1406, 0, x_1);
lean_ctor_set(x_1406, 1, x_1405);
lean_ctor_set_uint8(x_1406, sizeof(void*)*2, x_468);
return x_1406;
}
}
else
{
lean_object* x_1407; lean_object* x_1408; lean_object* x_1409; uint8_t x_1410; lean_object* x_1411; uint8_t x_1412; uint8_t x_1413; uint8_t x_1414; uint8_t x_1415; uint8_t x_1416; lean_object* x_1417; uint16_t x_1418; uint16_t x_1419; lean_object* x_1420; uint8_t x_1421; lean_object* x_1422; uint8_t x_1423; lean_object* x_1424; lean_object* x_1425; 
lean_dec(x_1);
x_1407 = lp_dasmodel___private_CPU6502_0__aslOp___redArg(x_2);
x_1408 = lean_ctor_get(x_1407, 0);
lean_inc(x_1408);
x_1409 = lean_ctor_get(x_1407, 1);
lean_inc(x_1409);
lean_dec_ref(x_1407);
x_1410 = lean_unbox(x_1408);
x_1411 = lp_dasmodel_updateNZ(x_7, x_1410);
x_1412 = lean_ctor_get_uint8(x_1411, 1);
x_1413 = lean_ctor_get_uint8(x_1411, 2);
x_1414 = lean_ctor_get_uint8(x_1411, 3);
x_1415 = lean_ctor_get_uint8(x_1411, 4);
x_1416 = lean_ctor_get_uint8(x_1411, 5);
if (lean_is_exclusive(x_1411)) {
 x_1417 = x_1411;
} else {
 lean_dec_ref(x_1411);
 x_1417 = lean_box(0);
}
x_1418 = 1;
x_1419 = lean_uint16_add(x_6, x_1418);
if (lean_is_scalar(x_1417)) {
 x_1420 = lean_alloc_ctor(0, 0, 6);
} else {
 x_1420 = x_1417;
}
x_1421 = lean_unbox(x_1409);
lean_dec(x_1409);
lean_ctor_set_uint8(x_1420, 0, x_1421);
lean_ctor_set_uint8(x_1420, 1, x_1412);
lean_ctor_set_uint8(x_1420, 2, x_1413);
lean_ctor_set_uint8(x_1420, 3, x_1414);
lean_ctor_set_uint8(x_1420, 4, x_1415);
lean_ctor_set_uint8(x_1420, 5, x_1416);
x_1422 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1422, 0, x_1420);
lean_ctor_set(x_1422, 1, x_8);
lean_ctor_set(x_1422, 2, x_9);
x_1423 = lean_unbox(x_1408);
lean_dec(x_1408);
lean_ctor_set_uint8(x_1422, sizeof(void*)*3 + 2, x_1423);
lean_ctor_set_uint8(x_1422, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1422, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1422, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1422, sizeof(void*)*3, x_1419);
x_1424 = lean_box(0);
x_1425 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1425, 0, x_1422);
lean_ctor_set(x_1425, 1, x_1424);
lean_ctor_set_uint8(x_1425, sizeof(void*)*2, x_468);
return x_1425;
}
}
}
else
{
uint8_t x_1426; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1426 = !lean_is_exclusive(x_1);
if (x_1426 == 0)
{
lean_object* x_1427; lean_object* x_1428; lean_object* x_1429; uint8_t x_1430; uint8_t x_1431; uint16_t x_1432; uint16_t x_1433; lean_object* x_1434; lean_object* x_1435; lean_object* x_1436; 
x_1427 = lean_ctor_get(x_1, 2);
lean_dec(x_1427);
x_1428 = lean_ctor_get(x_1, 1);
lean_dec(x_1428);
x_1429 = lean_ctor_get(x_1, 0);
lean_dec(x_1429);
x_1430 = 1;
x_1431 = lean_uint8_sub(x_4, x_1430);
x_1432 = 1;
x_1433 = lean_uint16_add(x_6, x_1432);
x_1434 = lp_dasmodel_updateNZ(x_7, x_1431);
lean_ctor_set(x_1, 0, x_1434);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 4, x_1431);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1433);
x_1435 = lean_box(0);
x_1436 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1436, 0, x_1);
lean_ctor_set(x_1436, 1, x_1435);
lean_ctor_set_uint8(x_1436, sizeof(void*)*2, x_466);
return x_1436;
}
else
{
uint8_t x_1437; uint8_t x_1438; uint16_t x_1439; uint16_t x_1440; lean_object* x_1441; lean_object* x_1442; lean_object* x_1443; lean_object* x_1444; 
lean_dec(x_1);
x_1437 = 1;
x_1438 = lean_uint8_sub(x_4, x_1437);
x_1439 = 1;
x_1440 = lean_uint16_add(x_6, x_1439);
x_1441 = lp_dasmodel_updateNZ(x_7, x_1438);
x_1442 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1442, 0, x_1441);
lean_ctor_set(x_1442, 1, x_8);
lean_ctor_set(x_1442, 2, x_9);
lean_ctor_set_uint8(x_1442, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_1442, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1442, sizeof(void*)*3 + 4, x_1438);
lean_ctor_set_uint8(x_1442, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1442, sizeof(void*)*3, x_1440);
x_1443 = lean_box(0);
x_1444 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1444, 0, x_1442);
lean_ctor_set(x_1444, 1, x_1443);
lean_ctor_set_uint8(x_1444, sizeof(void*)*2, x_466);
return x_1444;
}
}
}
else
{
uint8_t x_1445; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1445 = !lean_is_exclusive(x_1);
if (x_1445 == 0)
{
lean_object* x_1446; lean_object* x_1447; lean_object* x_1448; uint8_t x_1449; uint8_t x_1450; uint16_t x_1451; uint16_t x_1452; lean_object* x_1453; lean_object* x_1454; lean_object* x_1455; 
x_1446 = lean_ctor_get(x_1, 2);
lean_dec(x_1446);
x_1447 = lean_ctor_get(x_1, 1);
lean_dec(x_1447);
x_1448 = lean_ctor_get(x_1, 0);
lean_dec(x_1448);
x_1449 = 1;
x_1450 = lean_uint8_add(x_4, x_1449);
x_1451 = 1;
x_1452 = lean_uint16_add(x_6, x_1451);
x_1453 = lp_dasmodel_updateNZ(x_7, x_1450);
lean_ctor_set(x_1, 0, x_1453);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 4, x_1450);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1452);
x_1454 = lean_box(0);
x_1455 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1455, 0, x_1);
lean_ctor_set(x_1455, 1, x_1454);
lean_ctor_set_uint8(x_1455, sizeof(void*)*2, x_464);
return x_1455;
}
else
{
uint8_t x_1456; uint8_t x_1457; uint16_t x_1458; uint16_t x_1459; lean_object* x_1460; lean_object* x_1461; lean_object* x_1462; lean_object* x_1463; 
lean_dec(x_1);
x_1456 = 1;
x_1457 = lean_uint8_add(x_4, x_1456);
x_1458 = 1;
x_1459 = lean_uint16_add(x_6, x_1458);
x_1460 = lp_dasmodel_updateNZ(x_7, x_1457);
x_1461 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1461, 0, x_1460);
lean_ctor_set(x_1461, 1, x_8);
lean_ctor_set(x_1461, 2, x_9);
lean_ctor_set_uint8(x_1461, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_1461, sizeof(void*)*3 + 3, x_3);
lean_ctor_set_uint8(x_1461, sizeof(void*)*3 + 4, x_1457);
lean_ctor_set_uint8(x_1461, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1461, sizeof(void*)*3, x_1459);
x_1462 = lean_box(0);
x_1463 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1463, 0, x_1461);
lean_ctor_set(x_1463, 1, x_1462);
lean_ctor_set_uint8(x_1463, sizeof(void*)*2, x_464);
return x_1463;
}
}
}
else
{
uint8_t x_1464; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1464 = !lean_is_exclusive(x_1);
if (x_1464 == 0)
{
lean_object* x_1465; lean_object* x_1466; lean_object* x_1467; uint8_t x_1468; uint8_t x_1469; uint16_t x_1470; uint16_t x_1471; lean_object* x_1472; lean_object* x_1473; lean_object* x_1474; 
x_1465 = lean_ctor_get(x_1, 2);
lean_dec(x_1465);
x_1466 = lean_ctor_get(x_1, 1);
lean_dec(x_1466);
x_1467 = lean_ctor_get(x_1, 0);
lean_dec(x_1467);
x_1468 = 1;
x_1469 = lean_uint8_sub(x_3, x_1468);
x_1470 = 1;
x_1471 = lean_uint16_add(x_6, x_1470);
x_1472 = lp_dasmodel_updateNZ(x_7, x_1469);
lean_ctor_set(x_1, 0, x_1472);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 3, x_1469);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1471);
x_1473 = lean_box(0);
x_1474 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1474, 0, x_1);
lean_ctor_set(x_1474, 1, x_1473);
lean_ctor_set_uint8(x_1474, sizeof(void*)*2, x_462);
return x_1474;
}
else
{
uint8_t x_1475; uint8_t x_1476; uint16_t x_1477; uint16_t x_1478; lean_object* x_1479; lean_object* x_1480; lean_object* x_1481; lean_object* x_1482; 
lean_dec(x_1);
x_1475 = 1;
x_1476 = lean_uint8_sub(x_3, x_1475);
x_1477 = 1;
x_1478 = lean_uint16_add(x_6, x_1477);
x_1479 = lp_dasmodel_updateNZ(x_7, x_1476);
x_1480 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1480, 0, x_1479);
lean_ctor_set(x_1480, 1, x_8);
lean_ctor_set(x_1480, 2, x_9);
lean_ctor_set_uint8(x_1480, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_1480, sizeof(void*)*3 + 3, x_1476);
lean_ctor_set_uint8(x_1480, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1480, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1480, sizeof(void*)*3, x_1478);
x_1481 = lean_box(0);
x_1482 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1482, 0, x_1480);
lean_ctor_set(x_1482, 1, x_1481);
lean_ctor_set_uint8(x_1482, sizeof(void*)*2, x_462);
return x_1482;
}
}
}
else
{
uint8_t x_1483; 
lean_inc(x_9);
lean_inc_ref(x_8);
x_1483 = !lean_is_exclusive(x_1);
if (x_1483 == 0)
{
lean_object* x_1484; lean_object* x_1485; lean_object* x_1486; uint8_t x_1487; uint8_t x_1488; uint16_t x_1489; uint16_t x_1490; lean_object* x_1491; lean_object* x_1492; lean_object* x_1493; 
x_1484 = lean_ctor_get(x_1, 2);
lean_dec(x_1484);
x_1485 = lean_ctor_get(x_1, 1);
lean_dec(x_1485);
x_1486 = lean_ctor_get(x_1, 0);
lean_dec(x_1486);
x_1487 = 1;
x_1488 = lean_uint8_add(x_3, x_1487);
x_1489 = 1;
x_1490 = lean_uint16_add(x_6, x_1489);
x_1491 = lp_dasmodel_updateNZ(x_7, x_1488);
lean_ctor_set(x_1, 0, x_1491);
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 3, x_1488);
lean_ctor_set_uint16(x_1, sizeof(void*)*3, x_1490);
x_1492 = lean_box(0);
x_1493 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1493, 0, x_1);
lean_ctor_set(x_1493, 1, x_1492);
lean_ctor_set_uint8(x_1493, sizeof(void*)*2, x_460);
return x_1493;
}
else
{
uint8_t x_1494; uint8_t x_1495; uint16_t x_1496; uint16_t x_1497; lean_object* x_1498; lean_object* x_1499; lean_object* x_1500; lean_object* x_1501; 
lean_dec(x_1);
x_1494 = 1;
x_1495 = lean_uint8_add(x_3, x_1494);
x_1496 = 1;
x_1497 = lean_uint16_add(x_6, x_1496);
x_1498 = lp_dasmodel_updateNZ(x_7, x_1495);
x_1499 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_1499, 0, x_1498);
lean_ctor_set(x_1499, 1, x_8);
lean_ctor_set(x_1499, 2, x_9);
lean_ctor_set_uint8(x_1499, sizeof(void*)*3 + 2, x_2);
lean_ctor_set_uint8(x_1499, sizeof(void*)*3 + 3, x_1495);
lean_ctor_set_uint8(x_1499, sizeof(void*)*3 + 4, x_4);
lean_ctor_set_uint8(x_1499, sizeof(void*)*3 + 5, x_5);
lean_ctor_set_uint16(x_1499, sizeof(void*)*3, x_1497);
x_1500 = lean_box(0);
x_1501 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_1501, 0, x_1499);
lean_ctor_set(x_1501, 1, x_1500);
lean_ctor_set_uint8(x_1501, sizeof(void*)*2, x_460);
return x_1501;
}
}
}
else
{
goto block_452;
}
}
else
{
goto block_452;
}
}
else
{
goto block_452;
}
}
else
{
goto block_452;
}
}
else
{
goto block_405;
}
block_441:
{
lean_object* x_415; lean_object* x_416; lean_object* x_417; uint16_t x_418; uint8_t x_419; uint8_t x_420; uint8_t x_421; uint16_t x_422; lean_object* x_423; lean_object* x_424; lean_object* x_425; uint8_t x_426; 
x_415 = lp_dasmodel_CPU_fetchAddr(x_1, x_414);
x_416 = lean_ctor_get(x_415, 0);
lean_inc(x_416);
x_417 = lean_ctor_get(x_415, 1);
lean_inc(x_417);
lean_dec_ref(x_415);
x_418 = lean_unbox(x_416);
x_419 = lp_dasmodel_CPU_read(x_1, x_418);
x_420 = 1;
x_421 = lean_uint8_sub(x_419, x_420);
x_422 = lean_unbox(x_416);
lean_dec(x_416);
x_423 = lp_dasmodel_CPU_write(x_1, x_422, x_421);
x_424 = lean_ctor_get(x_423, 0);
lean_inc(x_424);
x_425 = lean_ctor_get(x_423, 1);
lean_inc(x_425);
lean_dec_ref(x_423);
x_426 = !lean_is_exclusive(x_424);
if (x_426 == 0)
{
lean_object* x_427; lean_object* x_428; uint16_t x_429; lean_object* x_430; 
x_427 = lean_ctor_get(x_424, 0);
lean_dec(x_427);
x_428 = lp_dasmodel_updateNZ(x_7, x_421);
lean_ctor_set(x_424, 0, x_428);
x_429 = lean_unbox(x_417);
lean_dec(x_417);
lean_ctor_set_uint16(x_424, sizeof(void*)*3, x_429);
x_430 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_430, 0, x_424);
lean_ctor_set(x_430, 1, x_425);
lean_ctor_set_uint8(x_430, sizeof(void*)*2, x_413);
return x_430;
}
else
{
uint8_t x_431; uint8_t x_432; uint8_t x_433; uint8_t x_434; lean_object* x_435; lean_object* x_436; lean_object* x_437; lean_object* x_438; uint16_t x_439; lean_object* x_440; 
x_431 = lean_ctor_get_uint8(x_424, sizeof(void*)*3 + 2);
x_432 = lean_ctor_get_uint8(x_424, sizeof(void*)*3 + 3);
x_433 = lean_ctor_get_uint8(x_424, sizeof(void*)*3 + 4);
x_434 = lean_ctor_get_uint8(x_424, sizeof(void*)*3 + 5);
x_435 = lean_ctor_get(x_424, 1);
x_436 = lean_ctor_get(x_424, 2);
lean_inc(x_436);
lean_inc(x_435);
lean_dec(x_424);
x_437 = lp_dasmodel_updateNZ(x_7, x_421);
x_438 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_438, 0, x_437);
lean_ctor_set(x_438, 1, x_435);
lean_ctor_set(x_438, 2, x_436);
lean_ctor_set_uint8(x_438, sizeof(void*)*3 + 2, x_431);
lean_ctor_set_uint8(x_438, sizeof(void*)*3 + 3, x_432);
lean_ctor_set_uint8(x_438, sizeof(void*)*3 + 4, x_433);
lean_ctor_set_uint8(x_438, sizeof(void*)*3 + 5, x_434);
x_439 = lean_unbox(x_417);
lean_dec(x_417);
lean_ctor_set_uint16(x_438, sizeof(void*)*3, x_439);
x_440 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_440, 0, x_438);
lean_ctor_set(x_440, 1, x_425);
lean_ctor_set_uint8(x_440, sizeof(void*)*2, x_413);
return x_440;
}
}
block_452:
{
lean_object* x_442; uint8_t x_443; 
x_442 = lean_unsigned_to_nat(198u);
x_443 = lean_nat_dec_eq(x_11, x_442);
if (x_443 == 0)
{
lean_object* x_444; uint8_t x_445; 
x_444 = lean_unsigned_to_nat(214u);
x_445 = lean_nat_dec_eq(x_11, x_444);
if (x_445 == 0)
{
lean_object* x_446; uint8_t x_447; 
x_446 = lean_unsigned_to_nat(206u);
x_447 = lean_nat_dec_eq(x_11, x_446);
if (x_447 == 0)
{
lean_object* x_448; uint8_t x_449; 
x_448 = lean_unsigned_to_nat(222u);
x_449 = lean_nat_dec_eq(x_11, x_448);
if (x_449 == 0)
{
x_414 = x_319;
goto block_441;
}
else
{
x_414 = x_309;
goto block_441;
}
}
else
{
lean_object* x_450; 
x_450 = lean_unsigned_to_nat(4u);
x_414 = x_450;
goto block_441;
}
}
else
{
lean_object* x_451; 
x_451 = lean_unsigned_to_nat(2u);
x_414 = x_451;
goto block_441;
}
}
else
{
x_414 = x_319;
goto block_441;
}
}
}
else
{
goto block_405;
}
}
else
{
goto block_405;
}
}
else
{
goto block_405;
}
}
else
{
lean_object* x_1502; lean_object* x_1503; 
lean_dec_ref(x_7);
x_1502 = lean_unsigned_to_nat(4u);
x_1503 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1502, x_4);
return x_1503;
}
block_394:
{
lean_object* x_368; lean_object* x_369; lean_object* x_370; uint16_t x_371; uint8_t x_372; uint8_t x_373; uint8_t x_374; uint16_t x_375; lean_object* x_376; lean_object* x_377; lean_object* x_378; uint8_t x_379; 
x_368 = lp_dasmodel_CPU_fetchAddr(x_1, x_367);
x_369 = lean_ctor_get(x_368, 0);
lean_inc(x_369);
x_370 = lean_ctor_get(x_368, 1);
lean_inc(x_370);
lean_dec_ref(x_368);
x_371 = lean_unbox(x_369);
x_372 = lp_dasmodel_CPU_read(x_1, x_371);
x_373 = 1;
x_374 = lean_uint8_add(x_372, x_373);
x_375 = lean_unbox(x_369);
lean_dec(x_369);
x_376 = lp_dasmodel_CPU_write(x_1, x_375, x_374);
x_377 = lean_ctor_get(x_376, 0);
lean_inc(x_377);
x_378 = lean_ctor_get(x_376, 1);
lean_inc(x_378);
lean_dec_ref(x_376);
x_379 = !lean_is_exclusive(x_377);
if (x_379 == 0)
{
lean_object* x_380; lean_object* x_381; uint16_t x_382; lean_object* x_383; 
x_380 = lean_ctor_get(x_377, 0);
lean_dec(x_380);
x_381 = lp_dasmodel_updateNZ(x_7, x_374);
lean_ctor_set(x_377, 0, x_381);
x_382 = lean_unbox(x_370);
lean_dec(x_370);
lean_ctor_set_uint16(x_377, sizeof(void*)*3, x_382);
x_383 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_383, 0, x_377);
lean_ctor_set(x_383, 1, x_378);
lean_ctor_set_uint8(x_383, sizeof(void*)*2, x_366);
return x_383;
}
else
{
uint8_t x_384; uint8_t x_385; uint8_t x_386; uint8_t x_387; lean_object* x_388; lean_object* x_389; lean_object* x_390; lean_object* x_391; uint16_t x_392; lean_object* x_393; 
x_384 = lean_ctor_get_uint8(x_377, sizeof(void*)*3 + 2);
x_385 = lean_ctor_get_uint8(x_377, sizeof(void*)*3 + 3);
x_386 = lean_ctor_get_uint8(x_377, sizeof(void*)*3 + 4);
x_387 = lean_ctor_get_uint8(x_377, sizeof(void*)*3 + 5);
x_388 = lean_ctor_get(x_377, 1);
x_389 = lean_ctor_get(x_377, 2);
lean_inc(x_389);
lean_inc(x_388);
lean_dec(x_377);
x_390 = lp_dasmodel_updateNZ(x_7, x_374);
x_391 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_391, 0, x_390);
lean_ctor_set(x_391, 1, x_388);
lean_ctor_set(x_391, 2, x_389);
lean_ctor_set_uint8(x_391, sizeof(void*)*3 + 2, x_384);
lean_ctor_set_uint8(x_391, sizeof(void*)*3 + 3, x_385);
lean_ctor_set_uint8(x_391, sizeof(void*)*3 + 4, x_386);
lean_ctor_set_uint8(x_391, sizeof(void*)*3 + 5, x_387);
x_392 = lean_unbox(x_370);
lean_dec(x_370);
lean_ctor_set_uint16(x_391, sizeof(void*)*3, x_392);
x_393 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_393, 0, x_391);
lean_ctor_set(x_393, 1, x_378);
lean_ctor_set_uint8(x_393, sizeof(void*)*2, x_366);
return x_393;
}
}
block_405:
{
lean_object* x_395; uint8_t x_396; 
x_395 = lean_unsigned_to_nat(230u);
x_396 = lean_nat_dec_eq(x_11, x_395);
if (x_396 == 0)
{
lean_object* x_397; uint8_t x_398; 
x_397 = lean_unsigned_to_nat(246u);
x_398 = lean_nat_dec_eq(x_11, x_397);
if (x_398 == 0)
{
lean_object* x_399; uint8_t x_400; 
x_399 = lean_unsigned_to_nat(238u);
x_400 = lean_nat_dec_eq(x_11, x_399);
if (x_400 == 0)
{
lean_object* x_401; uint8_t x_402; 
x_401 = lean_unsigned_to_nat(254u);
x_402 = lean_nat_dec_eq(x_11, x_401);
if (x_402 == 0)
{
x_367 = x_319;
goto block_394;
}
else
{
x_367 = x_309;
goto block_394;
}
}
else
{
lean_object* x_403; 
x_403 = lean_unsigned_to_nat(4u);
x_367 = x_403;
goto block_394;
}
}
else
{
lean_object* x_404; 
x_404 = lean_unsigned_to_nat(2u);
x_367 = x_404;
goto block_394;
}
}
else
{
x_367 = x_319;
goto block_394;
}
}
}
else
{
lean_object* x_1504; 
lean_dec_ref(x_7);
x_1504 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_319, x_4);
return x_1504;
}
}
else
{
lean_object* x_1505; lean_object* x_1506; 
lean_dec_ref(x_7);
x_1505 = lean_unsigned_to_nat(0u);
x_1506 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1505, x_4);
return x_1506;
}
}
else
{
lean_object* x_1507; lean_object* x_1508; 
lean_dec_ref(x_7);
x_1507 = lean_unsigned_to_nat(4u);
x_1508 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1507, x_3);
return x_1508;
}
}
else
{
lean_object* x_1509; 
lean_dec_ref(x_7);
x_1509 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_319, x_3);
return x_1509;
}
}
else
{
lean_object* x_1510; lean_object* x_1511; 
lean_dec_ref(x_7);
x_1510 = lean_unsigned_to_nat(0u);
x_1511 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1510, x_3);
return x_1511;
}
}
else
{
lean_object* x_1512; lean_object* x_1513; 
lean_dec_ref(x_7);
x_1512 = lean_unsigned_to_nat(8u);
x_1513 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1512, x_2);
return x_1513;
}
}
else
{
lean_object* x_1514; lean_object* x_1515; 
lean_dec_ref(x_7);
x_1514 = lean_unsigned_to_nat(7u);
x_1515 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1514, x_2);
return x_1515;
}
}
else
{
lean_object* x_1516; lean_object* x_1517; 
lean_dec_ref(x_7);
x_1516 = lean_unsigned_to_nat(6u);
x_1517 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1516, x_2);
return x_1517;
}
}
else
{
lean_object* x_1518; 
lean_dec_ref(x_7);
x_1518 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_309, x_2);
return x_1518;
}
}
else
{
lean_object* x_1519; lean_object* x_1520; 
lean_dec_ref(x_7);
x_1519 = lean_unsigned_to_nat(4u);
x_1520 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1519, x_2);
return x_1520;
}
}
else
{
lean_object* x_1521; lean_object* x_1522; 
lean_dec_ref(x_7);
x_1521 = lean_unsigned_to_nat(2u);
x_1522 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1521, x_2);
return x_1522;
}
}
else
{
lean_object* x_1523; 
lean_dec_ref(x_7);
x_1523 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_319, x_2);
return x_1523;
}
}
else
{
lean_object* x_1524; lean_object* x_1525; 
lean_dec_ref(x_7);
x_1524 = lean_unsigned_to_nat(0u);
x_1525 = lp_dasmodel___private_CPU6502_0__doCMP(x_1, x_1524, x_2);
return x_1525;
}
}
else
{
lean_object* x_1526; lean_object* x_1527; lean_object* x_1528; 
lean_dec_ref(x_7);
x_1526 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1527 = lean_unsigned_to_nat(8u);
x_1528 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1527, x_1526);
return x_1528;
}
}
else
{
lean_object* x_1529; lean_object* x_1530; lean_object* x_1531; 
lean_dec_ref(x_7);
x_1529 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1530 = lean_unsigned_to_nat(7u);
x_1531 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1530, x_1529);
return x_1531;
}
}
else
{
lean_object* x_1532; lean_object* x_1533; lean_object* x_1534; 
lean_dec_ref(x_7);
x_1532 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1533 = lean_unsigned_to_nat(6u);
x_1534 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1533, x_1532);
return x_1534;
}
}
else
{
lean_object* x_1535; lean_object* x_1536; 
lean_dec_ref(x_7);
x_1535 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1536 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_309, x_1535);
return x_1536;
}
}
else
{
lean_object* x_1537; lean_object* x_1538; lean_object* x_1539; 
lean_dec_ref(x_7);
x_1537 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1538 = lean_unsigned_to_nat(4u);
x_1539 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1538, x_1537);
return x_1539;
}
}
else
{
lean_object* x_1540; lean_object* x_1541; lean_object* x_1542; 
lean_dec_ref(x_7);
x_1540 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1541 = lean_unsigned_to_nat(2u);
x_1542 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1541, x_1540);
return x_1542;
}
}
else
{
lean_object* x_1543; lean_object* x_1544; 
lean_dec_ref(x_7);
x_1543 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1544 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_319, x_1543);
return x_1544;
}
}
else
{
lean_object* x_1545; lean_object* x_1546; lean_object* x_1547; 
lean_dec_ref(x_7);
x_1545 = ((lean_object*)(lp_dasmodel_stepRaw___closed__4));
x_1546 = lean_unsigned_to_nat(0u);
x_1547 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1546, x_1545);
return x_1547;
}
}
else
{
lean_object* x_1548; lean_object* x_1549; lean_object* x_1550; 
lean_dec_ref(x_7);
x_1548 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1549 = lean_unsigned_to_nat(8u);
x_1550 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1549, x_1548);
return x_1550;
}
}
else
{
lean_object* x_1551; lean_object* x_1552; lean_object* x_1553; 
lean_dec_ref(x_7);
x_1551 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1552 = lean_unsigned_to_nat(7u);
x_1553 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1552, x_1551);
return x_1553;
}
}
else
{
lean_object* x_1554; lean_object* x_1555; lean_object* x_1556; 
lean_dec_ref(x_7);
x_1554 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1555 = lean_unsigned_to_nat(6u);
x_1556 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1555, x_1554);
return x_1556;
}
}
else
{
lean_object* x_1557; lean_object* x_1558; 
lean_dec_ref(x_7);
x_1557 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1558 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_309, x_1557);
return x_1558;
}
}
else
{
lean_object* x_1559; lean_object* x_1560; lean_object* x_1561; 
lean_dec_ref(x_7);
x_1559 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1560 = lean_unsigned_to_nat(4u);
x_1561 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1560, x_1559);
return x_1561;
}
}
else
{
lean_object* x_1562; lean_object* x_1563; lean_object* x_1564; 
lean_dec_ref(x_7);
x_1562 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1563 = lean_unsigned_to_nat(2u);
x_1564 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1563, x_1562);
return x_1564;
}
}
else
{
lean_object* x_1565; lean_object* x_1566; lean_object* x_1567; 
lean_dec_ref(x_7);
x_1565 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1566 = lean_unsigned_to_nat(1u);
x_1567 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1566, x_1565);
return x_1567;
}
}
else
{
lean_object* x_1568; lean_object* x_1569; lean_object* x_1570; 
lean_dec_ref(x_7);
x_1568 = ((lean_object*)(lp_dasmodel_stepRaw___closed__5));
x_1569 = lean_unsigned_to_nat(0u);
x_1570 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1569, x_1568);
return x_1570;
}
}
else
{
lean_object* x_1571; lean_object* x_1572; lean_object* x_1573; 
lean_dec_ref(x_7);
x_1571 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1572 = lean_unsigned_to_nat(8u);
x_1573 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1572, x_1571);
return x_1573;
}
}
else
{
lean_object* x_1574; lean_object* x_1575; lean_object* x_1576; 
lean_dec_ref(x_7);
x_1574 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1575 = lean_unsigned_to_nat(7u);
x_1576 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1575, x_1574);
return x_1576;
}
}
else
{
lean_object* x_1577; lean_object* x_1578; lean_object* x_1579; 
lean_dec_ref(x_7);
x_1577 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1578 = lean_unsigned_to_nat(6u);
x_1579 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1578, x_1577);
return x_1579;
}
}
else
{
lean_object* x_1580; lean_object* x_1581; lean_object* x_1582; 
lean_dec_ref(x_7);
x_1580 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1581 = lean_unsigned_to_nat(5u);
x_1582 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1581, x_1580);
return x_1582;
}
}
else
{
lean_object* x_1583; lean_object* x_1584; lean_object* x_1585; 
lean_dec_ref(x_7);
x_1583 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1584 = lean_unsigned_to_nat(4u);
x_1585 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1584, x_1583);
return x_1585;
}
}
else
{
lean_object* x_1586; lean_object* x_1587; lean_object* x_1588; 
lean_dec_ref(x_7);
x_1586 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1587 = lean_unsigned_to_nat(2u);
x_1588 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1587, x_1586);
return x_1588;
}
}
else
{
lean_object* x_1589; lean_object* x_1590; lean_object* x_1591; 
lean_dec_ref(x_7);
x_1589 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1590 = lean_unsigned_to_nat(1u);
x_1591 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1590, x_1589);
return x_1591;
}
}
else
{
lean_object* x_1592; lean_object* x_1593; lean_object* x_1594; 
lean_dec_ref(x_7);
x_1592 = ((lean_object*)(lp_dasmodel_stepRaw___closed__6));
x_1593 = lean_unsigned_to_nat(0u);
x_1594 = lp_dasmodel___private_CPU6502_0__doALU(x_1, x_1593, x_1592);
return x_1594;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_274;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
block_198:
{
lean_object* x_194; lean_object* x_195; lean_object* x_196; lean_object* x_197; 
x_194 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_194, 0, x_192);
lean_ctor_set_uint8(x_194, 1, x_181);
lean_ctor_set_uint8(x_194, 2, x_185);
lean_ctor_set_uint8(x_194, 3, x_182);
lean_ctor_set_uint8(x_194, 4, x_193);
lean_ctor_set_uint8(x_194, 5, x_189);
x_195 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_195, 0, x_194);
lean_ctor_set(x_195, 1, x_183);
lean_ctor_set(x_195, 2, x_187);
lean_ctor_set_uint8(x_195, sizeof(void*)*3 + 2, x_188);
lean_ctor_set_uint8(x_195, sizeof(void*)*3 + 3, x_190);
lean_ctor_set_uint8(x_195, sizeof(void*)*3 + 4, x_186);
lean_ctor_set_uint8(x_195, sizeof(void*)*3 + 5, x_191);
lean_ctor_set_uint16(x_195, sizeof(void*)*3, x_184);
x_196 = lean_box(0);
x_197 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_197, 0, x_195);
lean_ctor_set(x_197, 1, x_196);
lean_ctor_set_uint8(x_197, sizeof(void*)*2, x_180);
return x_197;
}
block_230:
{
lean_object* x_211; lean_object* x_212; uint8_t x_213; lean_object* x_214; uint8_t x_215; uint8_t x_216; uint8_t x_217; uint8_t x_218; uint8_t x_219; uint8_t x_220; uint8_t x_221; uint8_t x_222; uint8_t x_223; uint8_t x_224; uint8_t x_225; uint8_t x_226; uint8_t x_227; uint8_t x_228; 
x_211 = lean_nat_sub(x_205, x_210);
lean_dec(x_205);
x_212 = lean_nat_mod(x_211, x_199);
x_213 = lean_uint8_of_nat(x_212);
lean_dec(x_212);
x_214 = lp_dasmodel_updateNZ(x_209, x_213);
x_215 = lean_ctor_get_uint8(x_214, 1);
x_216 = lean_ctor_get_uint8(x_214, 2);
x_217 = lean_ctor_get_uint8(x_214, 3);
x_218 = lean_ctor_get_uint8(x_214, 5);
lean_dec_ref(x_214);
x_219 = lean_nat_dec_le(x_199, x_211);
lean_dec(x_211);
x_220 = lean_uint8_xor(x_204, x_213);
x_221 = 255;
x_222 = lean_uint8_sub(x_221, x_200);
x_223 = lean_uint8_xor(x_222, x_213);
x_224 = lean_uint8_land(x_220, x_223);
x_225 = 128;
x_226 = lean_uint8_land(x_224, x_225);
x_227 = 0;
x_228 = lean_uint8_dec_eq(x_226, x_227);
if (x_228 == 0)
{
uint8_t x_229; 
x_229 = 1;
x_181 = x_215;
x_182 = x_217;
x_183 = x_201;
x_184 = x_202;
x_185 = x_216;
x_186 = x_203;
x_187 = x_206;
x_188 = x_213;
x_189 = x_218;
x_190 = x_207;
x_191 = x_208;
x_192 = x_219;
x_193 = x_229;
goto block_198;
}
else
{
x_181 = x_215;
x_182 = x_217;
x_183 = x_201;
x_184 = x_202;
x_185 = x_216;
x_186 = x_203;
x_187 = x_206;
x_188 = x_213;
x_189 = x_218;
x_190 = x_207;
x_191 = x_208;
x_192 = x_219;
x_193 = x_180;
goto block_198;
}
}
block_248:
{
lean_object* x_232; lean_object* x_233; lean_object* x_234; uint8_t x_235; lean_object* x_236; lean_object* x_237; lean_object* x_238; uint8_t x_239; lean_object* x_240; lean_object* x_241; 
x_232 = lp_dasmodel_CPU_fetchOperand(x_1, x_231);
lean_dec_ref(x_1);
x_233 = lean_ctor_get(x_232, 0);
lean_inc(x_233);
x_234 = lean_ctor_get(x_232, 1);
lean_inc(x_234);
lean_dec_ref(x_232);
x_235 = lean_ctor_get_uint8(x_7, 0);
x_236 = lean_uint8_to_nat(x_2);
x_237 = lean_unsigned_to_nat(256u);
x_238 = lean_nat_add(x_236, x_237);
x_239 = lean_unbox(x_233);
x_240 = lean_uint8_to_nat(x_239);
x_241 = lean_nat_sub(x_238, x_240);
lean_dec(x_238);
if (x_235 == 0)
{
lean_object* x_242; uint8_t x_243; uint16_t x_244; 
x_242 = lean_unsigned_to_nat(1u);
x_243 = lean_unbox(x_233);
lean_dec(x_233);
x_244 = lean_unbox(x_234);
lean_dec(x_234);
x_199 = x_237;
x_200 = x_243;
x_201 = x_8;
x_202 = x_244;
x_203 = x_4;
x_204 = x_2;
x_205 = x_241;
x_206 = x_9;
x_207 = x_3;
x_208 = x_5;
x_209 = x_7;
x_210 = x_242;
goto block_230;
}
else
{
lean_object* x_245; uint8_t x_246; uint16_t x_247; 
x_245 = lean_unsigned_to_nat(0u);
x_246 = lean_unbox(x_233);
lean_dec(x_233);
x_247 = lean_unbox(x_234);
lean_dec(x_234);
x_199 = x_237;
x_200 = x_246;
x_201 = x_8;
x_202 = x_247;
x_203 = x_4;
x_204 = x_2;
x_205 = x_241;
x_206 = x_9;
x_207 = x_3;
x_208 = x_5;
x_209 = x_7;
x_210 = x_245;
goto block_230;
}
}
block_274:
{
lean_object* x_249; uint8_t x_250; 
x_249 = lean_unsigned_to_nat(233u);
x_250 = lean_nat_dec_eq(x_11, x_249);
if (x_250 == 0)
{
lean_object* x_251; uint8_t x_252; 
x_251 = lean_unsigned_to_nat(229u);
x_252 = lean_nat_dec_eq(x_11, x_251);
if (x_252 == 0)
{
lean_object* x_253; uint8_t x_254; 
x_253 = lean_unsigned_to_nat(245u);
x_254 = lean_nat_dec_eq(x_11, x_253);
if (x_254 == 0)
{
lean_object* x_255; uint8_t x_256; 
x_255 = lean_unsigned_to_nat(237u);
x_256 = lean_nat_dec_eq(x_11, x_255);
if (x_256 == 0)
{
lean_object* x_257; uint8_t x_258; 
x_257 = lean_unsigned_to_nat(253u);
x_258 = lean_nat_dec_eq(x_11, x_257);
if (x_258 == 0)
{
lean_object* x_259; uint8_t x_260; 
x_259 = lean_unsigned_to_nat(249u);
x_260 = lean_nat_dec_eq(x_11, x_259);
if (x_260 == 0)
{
lean_object* x_261; uint8_t x_262; 
x_261 = lean_unsigned_to_nat(225u);
x_262 = lean_nat_dec_eq(x_11, x_261);
if (x_262 == 0)
{
lean_object* x_263; uint8_t x_264; 
x_263 = lean_unsigned_to_nat(241u);
x_264 = lean_nat_dec_eq(x_11, x_263);
if (x_264 == 0)
{
lean_object* x_265; 
x_265 = lean_unsigned_to_nat(0u);
x_231 = x_265;
goto block_248;
}
else
{
lean_object* x_266; 
x_266 = lean_unsigned_to_nat(8u);
x_231 = x_266;
goto block_248;
}
}
else
{
lean_object* x_267; 
x_267 = lean_unsigned_to_nat(7u);
x_231 = x_267;
goto block_248;
}
}
else
{
lean_object* x_268; 
x_268 = lean_unsigned_to_nat(6u);
x_231 = x_268;
goto block_248;
}
}
else
{
lean_object* x_269; 
x_269 = lean_unsigned_to_nat(5u);
x_231 = x_269;
goto block_248;
}
}
else
{
lean_object* x_270; 
x_270 = lean_unsigned_to_nat(4u);
x_231 = x_270;
goto block_248;
}
}
else
{
lean_object* x_271; 
x_271 = lean_unsigned_to_nat(2u);
x_231 = x_271;
goto block_248;
}
}
else
{
lean_object* x_272; 
x_272 = lean_unsigned_to_nat(1u);
x_231 = x_272;
goto block_248;
}
}
else
{
lean_object* x_273; 
x_273 = lean_unsigned_to_nat(0u);
x_231 = x_273;
goto block_248;
}
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
}
else
{
lean_inc(x_9);
lean_inc_ref(x_8);
goto block_164;
}
}
else
{
lean_object* x_1595; lean_object* x_1596; 
lean_dec_ref(x_7);
x_1595 = lean_unsigned_to_nat(4u);
x_1596 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1595, x_4);
return x_1596;
}
block_91:
{
lean_object* x_87; lean_object* x_88; lean_object* x_89; lean_object* x_90; 
x_87 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_87, 0, x_83);
lean_ctor_set_uint8(x_87, 1, x_76);
lean_ctor_set_uint8(x_87, 2, x_77);
lean_ctor_set_uint8(x_87, 3, x_75);
lean_ctor_set_uint8(x_87, 4, x_86);
lean_ctor_set_uint8(x_87, 5, x_74);
x_88 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_88, 0, x_87);
lean_ctor_set(x_88, 1, x_80);
lean_ctor_set(x_88, 2, x_84);
lean_ctor_set_uint8(x_88, sizeof(void*)*3 + 2, x_85);
lean_ctor_set_uint8(x_88, sizeof(void*)*3 + 3, x_82);
lean_ctor_set_uint8(x_88, sizeof(void*)*3 + 4, x_79);
lean_ctor_set_uint8(x_88, sizeof(void*)*3 + 5, x_78);
lean_ctor_set_uint16(x_88, sizeof(void*)*3, x_81);
x_89 = lean_box(0);
x_90 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_90, 0, x_88);
lean_ctor_set(x_90, 1, x_89);
lean_ctor_set_uint8(x_90, sizeof(void*)*2, x_73);
return x_90;
}
block_122:
{
lean_object* x_103; lean_object* x_104; lean_object* x_105; uint8_t x_106; lean_object* x_107; uint8_t x_108; uint8_t x_109; uint8_t x_110; uint8_t x_111; lean_object* x_112; uint8_t x_113; uint8_t x_114; uint8_t x_115; uint8_t x_116; uint8_t x_117; uint8_t x_118; uint8_t x_119; uint8_t x_120; 
x_103 = lean_nat_add(x_93, x_102);
lean_dec(x_93);
x_104 = lean_unsigned_to_nat(256u);
x_105 = lean_nat_mod(x_103, x_104);
x_106 = lean_uint8_of_nat(x_105);
lean_dec(x_105);
x_107 = lp_dasmodel_updateNZ(x_94, x_106);
x_108 = lean_ctor_get_uint8(x_107, 1);
x_109 = lean_ctor_get_uint8(x_107, 2);
x_110 = lean_ctor_get_uint8(x_107, 3);
x_111 = lean_ctor_get_uint8(x_107, 5);
lean_dec_ref(x_107);
x_112 = lean_unsigned_to_nat(255u);
x_113 = lean_nat_dec_lt(x_112, x_103);
lean_dec(x_103);
x_114 = lean_uint8_xor(x_101, x_106);
x_115 = lean_uint8_xor(x_92, x_106);
x_116 = lean_uint8_land(x_114, x_115);
x_117 = 128;
x_118 = lean_uint8_land(x_116, x_117);
x_119 = 0;
x_120 = lean_uint8_dec_eq(x_118, x_119);
if (x_120 == 0)
{
uint8_t x_121; 
x_121 = 1;
x_74 = x_111;
x_75 = x_110;
x_76 = x_108;
x_77 = x_109;
x_78 = x_96;
x_79 = x_95;
x_80 = x_97;
x_81 = x_99;
x_82 = x_98;
x_83 = x_113;
x_84 = x_100;
x_85 = x_106;
x_86 = x_121;
goto block_91;
}
else
{
x_74 = x_111;
x_75 = x_110;
x_76 = x_108;
x_77 = x_109;
x_78 = x_96;
x_79 = x_95;
x_80 = x_97;
x_81 = x_99;
x_82 = x_98;
x_83 = x_113;
x_84 = x_100;
x_85 = x_106;
x_86 = x_73;
goto block_91;
}
}
block_138:
{
lean_object* x_124; lean_object* x_125; lean_object* x_126; uint8_t x_127; lean_object* x_128; uint8_t x_129; lean_object* x_130; lean_object* x_131; 
x_124 = lp_dasmodel_CPU_fetchOperand(x_1, x_123);
lean_dec_ref(x_1);
x_125 = lean_ctor_get(x_124, 0);
lean_inc(x_125);
x_126 = lean_ctor_get(x_124, 1);
lean_inc(x_126);
lean_dec_ref(x_124);
x_127 = lean_ctor_get_uint8(x_7, 0);
x_128 = lean_uint8_to_nat(x_2);
x_129 = lean_unbox(x_125);
x_130 = lean_uint8_to_nat(x_129);
x_131 = lean_nat_add(x_128, x_130);
if (x_127 == 0)
{
lean_object* x_132; uint8_t x_133; uint16_t x_134; 
x_132 = lean_unsigned_to_nat(0u);
x_133 = lean_unbox(x_125);
lean_dec(x_125);
x_134 = lean_unbox(x_126);
lean_dec(x_126);
x_92 = x_133;
x_93 = x_131;
x_94 = x_7;
x_95 = x_4;
x_96 = x_5;
x_97 = x_8;
x_98 = x_3;
x_99 = x_134;
x_100 = x_9;
x_101 = x_2;
x_102 = x_132;
goto block_122;
}
else
{
lean_object* x_135; uint8_t x_136; uint16_t x_137; 
x_135 = lean_unsigned_to_nat(1u);
x_136 = lean_unbox(x_125);
lean_dec(x_125);
x_137 = lean_unbox(x_126);
lean_dec(x_126);
x_92 = x_136;
x_93 = x_131;
x_94 = x_7;
x_95 = x_4;
x_96 = x_5;
x_97 = x_8;
x_98 = x_3;
x_99 = x_137;
x_100 = x_9;
x_101 = x_2;
x_102 = x_135;
goto block_122;
}
}
block_164:
{
lean_object* x_139; uint8_t x_140; 
x_139 = lean_unsigned_to_nat(105u);
x_140 = lean_nat_dec_eq(x_11, x_139);
if (x_140 == 0)
{
lean_object* x_141; uint8_t x_142; 
x_141 = lean_unsigned_to_nat(101u);
x_142 = lean_nat_dec_eq(x_11, x_141);
if (x_142 == 0)
{
lean_object* x_143; uint8_t x_144; 
x_143 = lean_unsigned_to_nat(117u);
x_144 = lean_nat_dec_eq(x_11, x_143);
if (x_144 == 0)
{
lean_object* x_145; uint8_t x_146; 
x_145 = lean_unsigned_to_nat(109u);
x_146 = lean_nat_dec_eq(x_11, x_145);
if (x_146 == 0)
{
lean_object* x_147; uint8_t x_148; 
x_147 = lean_unsigned_to_nat(125u);
x_148 = lean_nat_dec_eq(x_11, x_147);
if (x_148 == 0)
{
lean_object* x_149; uint8_t x_150; 
x_149 = lean_unsigned_to_nat(121u);
x_150 = lean_nat_dec_eq(x_11, x_149);
if (x_150 == 0)
{
lean_object* x_151; uint8_t x_152; 
x_151 = lean_unsigned_to_nat(97u);
x_152 = lean_nat_dec_eq(x_11, x_151);
if (x_152 == 0)
{
lean_object* x_153; uint8_t x_154; 
x_153 = lean_unsigned_to_nat(113u);
x_154 = lean_nat_dec_eq(x_11, x_153);
if (x_154 == 0)
{
lean_object* x_155; 
x_155 = lean_unsigned_to_nat(0u);
x_123 = x_155;
goto block_138;
}
else
{
lean_object* x_156; 
x_156 = lean_unsigned_to_nat(8u);
x_123 = x_156;
goto block_138;
}
}
else
{
lean_object* x_157; 
x_157 = lean_unsigned_to_nat(7u);
x_123 = x_157;
goto block_138;
}
}
else
{
lean_object* x_158; 
x_158 = lean_unsigned_to_nat(6u);
x_123 = x_158;
goto block_138;
}
}
else
{
lean_object* x_159; 
x_159 = lean_unsigned_to_nat(5u);
x_123 = x_159;
goto block_138;
}
}
else
{
lean_object* x_160; 
x_160 = lean_unsigned_to_nat(4u);
x_123 = x_160;
goto block_138;
}
}
else
{
lean_object* x_161; 
x_161 = lean_unsigned_to_nat(2u);
x_123 = x_161;
goto block_138;
}
}
else
{
lean_object* x_162; 
x_162 = lean_unsigned_to_nat(1u);
x_123 = x_162;
goto block_138;
}
}
else
{
lean_object* x_163; 
x_163 = lean_unsigned_to_nat(0u);
x_123 = x_163;
goto block_138;
}
}
}
else
{
lean_object* x_1597; lean_object* x_1598; 
lean_dec_ref(x_7);
x_1597 = lean_unsigned_to_nat(2u);
x_1598 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1597, x_4);
return x_1598;
}
}
else
{
lean_object* x_1599; lean_object* x_1600; 
lean_dec_ref(x_7);
x_1599 = lean_unsigned_to_nat(1u);
x_1600 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1599, x_4);
return x_1600;
}
}
else
{
lean_object* x_1601; lean_object* x_1602; 
lean_dec_ref(x_7);
x_1601 = lean_unsigned_to_nat(4u);
x_1602 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1601, x_3);
return x_1602;
}
}
else
{
lean_object* x_1603; lean_object* x_1604; 
lean_dec_ref(x_7);
x_1603 = lean_unsigned_to_nat(3u);
x_1604 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1603, x_3);
return x_1604;
}
}
else
{
lean_object* x_1605; lean_object* x_1606; 
lean_dec_ref(x_7);
x_1605 = lean_unsigned_to_nat(1u);
x_1606 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1605, x_3);
return x_1606;
}
}
else
{
lean_object* x_1607; lean_object* x_1608; 
lean_dec_ref(x_7);
x_1607 = lean_unsigned_to_nat(8u);
x_1608 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1607, x_2);
return x_1608;
}
}
else
{
lean_object* x_1609; lean_object* x_1610; 
lean_dec_ref(x_7);
x_1609 = lean_unsigned_to_nat(7u);
x_1610 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1609, x_2);
return x_1610;
}
}
else
{
lean_object* x_1611; lean_object* x_1612; 
lean_dec_ref(x_7);
x_1611 = lean_unsigned_to_nat(6u);
x_1612 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1611, x_2);
return x_1612;
}
}
else
{
lean_object* x_1613; lean_object* x_1614; 
lean_dec_ref(x_7);
x_1613 = lean_unsigned_to_nat(5u);
x_1614 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1613, x_2);
return x_1614;
}
}
else
{
lean_object* x_1615; lean_object* x_1616; 
lean_dec_ref(x_7);
x_1615 = lean_unsigned_to_nat(4u);
x_1616 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1615, x_2);
return x_1616;
}
}
else
{
lean_object* x_1617; lean_object* x_1618; 
lean_dec_ref(x_7);
x_1617 = lean_unsigned_to_nat(2u);
x_1618 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1617, x_2);
return x_1618;
}
}
else
{
lean_object* x_1619; lean_object* x_1620; 
lean_dec_ref(x_7);
x_1619 = lean_unsigned_to_nat(1u);
x_1620 = lp_dasmodel___private_CPU6502_0__doStore(x_1, x_1619, x_2);
return x_1620;
}
}
else
{
lean_object* x_1621; lean_object* x_1622; lean_object* x_1623; 
lean_dec_ref(x_7);
x_1621 = lean_unsigned_to_nat(5u);
x_1622 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__2));
x_1623 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1621, x_1622);
return x_1623;
}
}
else
{
lean_object* x_1624; lean_object* x_1625; lean_object* x_1626; 
lean_dec_ref(x_7);
x_1624 = lean_unsigned_to_nat(4u);
x_1625 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__2));
x_1626 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1624, x_1625);
return x_1626;
}
}
else
{
lean_object* x_1627; lean_object* x_1628; lean_object* x_1629; 
lean_dec_ref(x_7);
x_1627 = lean_unsigned_to_nat(2u);
x_1628 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__2));
x_1629 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1627, x_1628);
return x_1629;
}
}
else
{
lean_object* x_1630; lean_object* x_1631; lean_object* x_1632; 
lean_dec_ref(x_7);
x_1630 = lean_unsigned_to_nat(1u);
x_1631 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__2));
x_1632 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1630, x_1631);
return x_1632;
}
}
else
{
lean_object* x_1633; lean_object* x_1634; lean_object* x_1635; 
lean_dec_ref(x_7);
x_1633 = lean_unsigned_to_nat(0u);
x_1634 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__2));
x_1635 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1633, x_1634);
return x_1635;
}
}
else
{
lean_object* x_1636; lean_object* x_1637; lean_object* x_1638; 
lean_dec_ref(x_7);
x_1636 = lean_unsigned_to_nat(6u);
x_1637 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__1));
x_1638 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1636, x_1637);
return x_1638;
}
}
else
{
lean_object* x_1639; lean_object* x_1640; lean_object* x_1641; 
lean_dec_ref(x_7);
x_1639 = lean_unsigned_to_nat(4u);
x_1640 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__1));
x_1641 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1639, x_1640);
return x_1641;
}
}
else
{
lean_object* x_1642; lean_object* x_1643; lean_object* x_1644; 
lean_dec_ref(x_7);
x_1642 = lean_unsigned_to_nat(3u);
x_1643 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__1));
x_1644 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1642, x_1643);
return x_1644;
}
}
else
{
lean_object* x_1645; lean_object* x_1646; lean_object* x_1647; 
lean_dec_ref(x_7);
x_1645 = lean_unsigned_to_nat(1u);
x_1646 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__1));
x_1647 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1645, x_1646);
return x_1647;
}
}
else
{
lean_object* x_1648; lean_object* x_1649; lean_object* x_1650; 
lean_dec_ref(x_7);
x_1648 = lean_unsigned_to_nat(0u);
x_1649 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__1));
x_1650 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1648, x_1649);
return x_1650;
}
}
else
{
lean_object* x_1651; lean_object* x_1652; lean_object* x_1653; 
lean_dec_ref(x_7);
x_1651 = lean_unsigned_to_nat(8u);
x_1652 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1653 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1651, x_1652);
return x_1653;
}
}
else
{
lean_object* x_1654; lean_object* x_1655; lean_object* x_1656; 
lean_dec_ref(x_7);
x_1654 = lean_unsigned_to_nat(7u);
x_1655 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1656 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1654, x_1655);
return x_1656;
}
}
else
{
lean_object* x_1657; lean_object* x_1658; lean_object* x_1659; 
lean_dec_ref(x_7);
x_1657 = lean_unsigned_to_nat(6u);
x_1658 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1659 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1657, x_1658);
return x_1659;
}
}
else
{
lean_object* x_1660; lean_object* x_1661; lean_object* x_1662; 
lean_dec_ref(x_7);
x_1660 = lean_unsigned_to_nat(5u);
x_1661 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1662 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1660, x_1661);
return x_1662;
}
}
else
{
lean_object* x_1663; lean_object* x_1664; lean_object* x_1665; 
lean_dec_ref(x_7);
x_1663 = lean_unsigned_to_nat(4u);
x_1664 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1665 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1663, x_1664);
return x_1665;
}
}
else
{
lean_object* x_1666; lean_object* x_1667; lean_object* x_1668; 
lean_dec_ref(x_7);
x_1666 = lean_unsigned_to_nat(2u);
x_1667 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1668 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1666, x_1667);
return x_1668;
}
}
else
{
lean_object* x_1669; lean_object* x_1670; lean_object* x_1671; 
lean_dec_ref(x_7);
x_1669 = lean_unsigned_to_nat(1u);
x_1670 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1671 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1669, x_1670);
return x_1671;
}
}
else
{
lean_object* x_1672; lean_object* x_1673; lean_object* x_1674; 
lean_dec_ref(x_7);
x_1672 = lean_unsigned_to_nat(0u);
x_1673 = ((lean_object*)(lp_dasmodel___private_CPU6502_0__doLoad___closed__0));
x_1674 = lp_dasmodel___private_CPU6502_0__doLoad(x_1, x_1672, x_1673);
return x_1674;
}
}
}
LEAN_EXPORT uint8_t lp_dasmodel___private_CPU6502_0__pageCross(uint16_t x_1, uint16_t x_2) {
_start:
{
uint16_t x_3; uint16_t x_4; uint16_t x_5; uint8_t x_6; 
x_3 = 65280;
x_4 = lean_uint16_land(x_1, x_3);
x_5 = lean_uint16_land(x_2, x_3);
x_6 = lean_uint16_dec_eq(x_4, x_5);
if (x_6 == 0)
{
uint8_t x_7; 
x_7 = 1;
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
LEAN_EXPORT lean_object* lp_dasmodel___private_CPU6502_0__pageCross___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; uint16_t x_4; uint8_t x_5; lean_object* x_6; 
x_3 = lean_unbox(x_1);
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel___private_CPU6502_0__pageCross(x_3, x_4);
x_6 = lean_box(x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__0(uint16_t x_1, lean_object* x_2, uint8_t x_3, lean_object* x_4) {
_start:
{
uint16_t x_5; uint16_t x_6; uint8_t x_7; uint16_t x_8; uint16_t x_9; uint16_t x_10; uint8_t x_11; 
x_5 = 1;
x_6 = lean_uint16_add(x_1, x_5);
x_7 = lp_dasmodel_CPU_read(x_2, x_6);
x_8 = lp_dasmodel_CPU_readZP16(x_2, x_7);
x_9 = lean_uint8_to_uint16(x_3);
x_10 = lean_uint16_add(x_8, x_9);
x_11 = lp_dasmodel___private_CPU6502_0__pageCross(x_8, x_10);
if (x_11 == 0)
{
lean_object* x_12; 
x_12 = lean_unsigned_to_nat(0u);
return x_12;
}
else
{
lean_object* x_13; 
x_13 = lean_unsigned_to_nat(1u);
return x_13;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint16_t x_5; uint8_t x_6; lean_object* x_7; 
x_5 = lean_unbox(x_1);
x_6 = lean_unbox(x_3);
x_7 = lp_dasmodel_step___lam__0(x_5, x_2, x_6, x_4);
lean_dec_ref(x_2);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__1(uint16_t x_1, lean_object* x_2, uint8_t x_3, lean_object* x_4) {
_start:
{
uint16_t x_5; uint16_t x_6; uint16_t x_7; uint16_t x_8; uint16_t x_9; uint8_t x_10; 
x_5 = 1;
x_6 = lean_uint16_add(x_1, x_5);
x_7 = lp_dasmodel_CPU_read16(x_2, x_6);
x_8 = lean_uint8_to_uint16(x_3);
x_9 = lean_uint16_add(x_7, x_8);
x_10 = lp_dasmodel___private_CPU6502_0__pageCross(x_7, x_9);
if (x_10 == 0)
{
lean_object* x_11; 
x_11 = lean_unsigned_to_nat(0u);
return x_11;
}
else
{
lean_object* x_12; 
x_12 = lean_unsigned_to_nat(1u);
return x_12;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint16_t x_5; uint8_t x_6; lean_object* x_7; 
x_5 = lean_unbox(x_1);
x_6 = lean_unbox(x_3);
x_7 = lp_dasmodel_step___lam__1(x_5, x_2, x_6, x_4);
lean_dec_ref(x_2);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__2(uint16_t x_1, lean_object* x_2, uint8_t x_3, lean_object* x_4) {
_start:
{
uint16_t x_5; uint16_t x_6; uint16_t x_7; uint16_t x_8; uint16_t x_9; uint8_t x_10; 
x_5 = 1;
x_6 = lean_uint16_add(x_1, x_5);
x_7 = lp_dasmodel_CPU_read16(x_2, x_6);
x_8 = lean_uint8_to_uint16(x_3);
x_9 = lean_uint16_add(x_7, x_8);
x_10 = lp_dasmodel___private_CPU6502_0__pageCross(x_7, x_9);
if (x_10 == 0)
{
lean_object* x_11; 
x_11 = lean_unsigned_to_nat(0u);
return x_11;
}
else
{
lean_object* x_12; 
x_12 = lean_unsigned_to_nat(1u);
return x_12;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_step___lam__2___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4) {
_start:
{
uint16_t x_5; uint8_t x_6; lean_object* x_7; 
x_5 = lean_unbox(x_1);
x_6 = lean_unbox(x_3);
x_7 = lp_dasmodel_step___lam__2(x_5, x_2, x_6, x_4);
lean_dec_ref(x_2);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_step(lean_object* x_1) {
_start:
{
uint8_t x_2; uint8_t x_3; uint16_t x_4; lean_object* x_5; uint8_t x_6; lean_object* x_7; lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_46; lean_object* x_47; uint8_t x_153; lean_object* x_167; uint8_t x_168; 
x_2 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_3 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_4 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_5 = lean_ctor_get(x_1, 2);
lean_inc(x_5);
x_6 = lp_dasmodel_CPU_read(x_1, x_4);
lean_inc_ref(x_1);
x_7 = lp_dasmodel_stepRaw(x_1);
x_8 = lp_dasmodel_opcodeCycles(x_6);
x_46 = lean_uint8_to_nat(x_6);
x_167 = lean_unsigned_to_nat(144u);
x_168 = lean_nat_dec_eq(x_46, x_167);
if (x_168 == 0)
{
lean_object* x_169; uint8_t x_170; 
x_169 = lean_unsigned_to_nat(176u);
x_170 = lean_nat_dec_eq(x_46, x_169);
x_153 = x_170;
goto block_166;
}
else
{
x_153 = x_168;
goto block_166;
}
block_45:
{
uint8_t x_11; 
x_11 = !lean_is_exclusive(x_7);
if (x_11 == 0)
{
lean_object* x_12; uint8_t x_13; 
x_12 = lean_ctor_get(x_7, 0);
x_13 = !lean_is_exclusive(x_12);
if (x_13 == 0)
{
lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; 
x_14 = lean_ctor_get(x_12, 2);
lean_dec(x_14);
x_15 = lean_nat_add(x_8, x_9);
lean_dec(x_8);
x_16 = lean_nat_add(x_15, x_10);
lean_dec(x_10);
lean_dec(x_15);
x_17 = lean_nat_add(x_5, x_16);
lean_dec(x_16);
lean_dec(x_5);
lean_ctor_set(x_12, 2, x_17);
return x_7;
}
else
{
uint8_t x_18; uint8_t x_19; uint8_t x_20; uint8_t x_21; uint16_t x_22; lean_object* x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; lean_object* x_27; lean_object* x_28; 
x_18 = lean_ctor_get_uint8(x_12, sizeof(void*)*3 + 2);
x_19 = lean_ctor_get_uint8(x_12, sizeof(void*)*3 + 3);
x_20 = lean_ctor_get_uint8(x_12, sizeof(void*)*3 + 4);
x_21 = lean_ctor_get_uint8(x_12, sizeof(void*)*3 + 5);
x_22 = lean_ctor_get_uint16(x_12, sizeof(void*)*3);
x_23 = lean_ctor_get(x_12, 0);
x_24 = lean_ctor_get(x_12, 1);
lean_inc(x_24);
lean_inc(x_23);
lean_dec(x_12);
x_25 = lean_nat_add(x_8, x_9);
lean_dec(x_8);
x_26 = lean_nat_add(x_25, x_10);
lean_dec(x_10);
lean_dec(x_25);
x_27 = lean_nat_add(x_5, x_26);
lean_dec(x_26);
lean_dec(x_5);
x_28 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_28, 0, x_23);
lean_ctor_set(x_28, 1, x_24);
lean_ctor_set(x_28, 2, x_27);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 2, x_18);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 3, x_19);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 4, x_20);
lean_ctor_set_uint8(x_28, sizeof(void*)*3 + 5, x_21);
lean_ctor_set_uint16(x_28, sizeof(void*)*3, x_22);
lean_ctor_set(x_7, 0, x_28);
return x_7;
}
}
else
{
lean_object* x_29; lean_object* x_30; uint8_t x_31; uint8_t x_32; uint8_t x_33; uint8_t x_34; uint8_t x_35; uint16_t x_36; lean_object* x_37; lean_object* x_38; lean_object* x_39; lean_object* x_40; lean_object* x_41; lean_object* x_42; lean_object* x_43; lean_object* x_44; 
x_29 = lean_ctor_get(x_7, 0);
x_30 = lean_ctor_get(x_7, 1);
x_31 = lean_ctor_get_uint8(x_7, sizeof(void*)*2);
lean_inc(x_30);
lean_inc(x_29);
lean_dec(x_7);
x_32 = lean_ctor_get_uint8(x_29, sizeof(void*)*3 + 2);
x_33 = lean_ctor_get_uint8(x_29, sizeof(void*)*3 + 3);
x_34 = lean_ctor_get_uint8(x_29, sizeof(void*)*3 + 4);
x_35 = lean_ctor_get_uint8(x_29, sizeof(void*)*3 + 5);
x_36 = lean_ctor_get_uint16(x_29, sizeof(void*)*3);
x_37 = lean_ctor_get(x_29, 0);
lean_inc_ref(x_37);
x_38 = lean_ctor_get(x_29, 1);
lean_inc_ref(x_38);
if (lean_is_exclusive(x_29)) {
 lean_ctor_release(x_29, 0);
 lean_ctor_release(x_29, 1);
 lean_ctor_release(x_29, 2);
 x_39 = x_29;
} else {
 lean_dec_ref(x_29);
 x_39 = lean_box(0);
}
x_40 = lean_nat_add(x_8, x_9);
lean_dec(x_8);
x_41 = lean_nat_add(x_40, x_10);
lean_dec(x_10);
lean_dec(x_40);
x_42 = lean_nat_add(x_5, x_41);
lean_dec(x_41);
lean_dec(x_5);
if (lean_is_scalar(x_39)) {
 x_43 = lean_alloc_ctor(0, 3, 6);
} else {
 x_43 = x_39;
}
lean_ctor_set(x_43, 0, x_37);
lean_ctor_set(x_43, 1, x_38);
lean_ctor_set(x_43, 2, x_42);
lean_ctor_set_uint8(x_43, sizeof(void*)*3 + 2, x_32);
lean_ctor_set_uint8(x_43, sizeof(void*)*3 + 3, x_33);
lean_ctor_set_uint8(x_43, sizeof(void*)*3 + 4, x_34);
lean_ctor_set_uint8(x_43, sizeof(void*)*3 + 5, x_35);
lean_ctor_set_uint16(x_43, sizeof(void*)*3, x_36);
x_44 = lean_alloc_ctor(0, 2, 1);
lean_ctor_set(x_44, 0, x_43);
lean_ctor_set(x_44, 1, x_30);
lean_ctor_set_uint8(x_44, sizeof(void*)*2, x_31);
return x_44;
}
}
block_141:
{
lean_object* x_48; uint8_t x_49; 
x_48 = lean_unsigned_to_nat(189u);
x_49 = lean_nat_dec_eq(x_46, x_48);
if (x_49 == 0)
{
lean_object* x_50; uint8_t x_51; 
x_50 = lean_unsigned_to_nat(188u);
x_51 = lean_nat_dec_eq(x_46, x_50);
if (x_51 == 0)
{
lean_object* x_52; uint8_t x_53; 
x_52 = lean_unsigned_to_nat(125u);
x_53 = lean_nat_dec_eq(x_46, x_52);
if (x_53 == 0)
{
lean_object* x_54; uint8_t x_55; 
x_54 = lean_unsigned_to_nat(253u);
x_55 = lean_nat_dec_eq(x_46, x_54);
if (x_55 == 0)
{
lean_object* x_56; uint8_t x_57; 
x_56 = lean_unsigned_to_nat(61u);
x_57 = lean_nat_dec_eq(x_46, x_56);
if (x_57 == 0)
{
lean_object* x_58; uint8_t x_59; 
x_58 = lean_unsigned_to_nat(29u);
x_59 = lean_nat_dec_eq(x_46, x_58);
if (x_59 == 0)
{
lean_object* x_60; uint8_t x_61; 
x_60 = lean_unsigned_to_nat(93u);
x_61 = lean_nat_dec_eq(x_46, x_60);
if (x_61 == 0)
{
lean_object* x_62; uint8_t x_63; 
x_62 = lean_unsigned_to_nat(221u);
x_63 = lean_nat_dec_eq(x_46, x_62);
if (x_63 == 0)
{
lean_object* x_64; uint8_t x_65; 
x_64 = lean_unsigned_to_nat(185u);
x_65 = lean_nat_dec_eq(x_46, x_64);
if (x_65 == 0)
{
lean_object* x_66; uint8_t x_67; 
x_66 = lean_unsigned_to_nat(190u);
x_67 = lean_nat_dec_eq(x_46, x_66);
if (x_67 == 0)
{
lean_object* x_68; uint8_t x_69; 
x_68 = lean_unsigned_to_nat(121u);
x_69 = lean_nat_dec_eq(x_46, x_68);
if (x_69 == 0)
{
lean_object* x_70; uint8_t x_71; 
x_70 = lean_unsigned_to_nat(249u);
x_71 = lean_nat_dec_eq(x_46, x_70);
if (x_71 == 0)
{
lean_object* x_72; uint8_t x_73; 
x_72 = lean_unsigned_to_nat(57u);
x_73 = lean_nat_dec_eq(x_46, x_72);
if (x_73 == 0)
{
lean_object* x_74; uint8_t x_75; 
x_74 = lean_unsigned_to_nat(25u);
x_75 = lean_nat_dec_eq(x_46, x_74);
if (x_75 == 0)
{
lean_object* x_76; uint8_t x_77; 
x_76 = lean_unsigned_to_nat(89u);
x_77 = lean_nat_dec_eq(x_46, x_76);
if (x_77 == 0)
{
lean_object* x_78; uint8_t x_79; 
x_78 = lean_unsigned_to_nat(217u);
x_79 = lean_nat_dec_eq(x_46, x_78);
if (x_79 == 0)
{
lean_object* x_80; uint8_t x_81; 
x_80 = lean_unsigned_to_nat(177u);
x_81 = lean_nat_dec_eq(x_46, x_80);
if (x_81 == 0)
{
lean_object* x_82; uint8_t x_83; 
x_82 = lean_unsigned_to_nat(113u);
x_83 = lean_nat_dec_eq(x_46, x_82);
if (x_83 == 0)
{
lean_object* x_84; uint8_t x_85; 
x_84 = lean_unsigned_to_nat(241u);
x_85 = lean_nat_dec_eq(x_46, x_84);
if (x_85 == 0)
{
lean_object* x_86; uint8_t x_87; 
x_86 = lean_unsigned_to_nat(49u);
x_87 = lean_nat_dec_eq(x_46, x_86);
if (x_87 == 0)
{
lean_object* x_88; uint8_t x_89; 
x_88 = lean_unsigned_to_nat(17u);
x_89 = lean_nat_dec_eq(x_46, x_88);
if (x_89 == 0)
{
lean_object* x_90; uint8_t x_91; 
x_90 = lean_unsigned_to_nat(81u);
x_91 = lean_nat_dec_eq(x_46, x_90);
if (x_91 == 0)
{
lean_object* x_92; uint8_t x_93; 
x_92 = lean_unsigned_to_nat(209u);
x_93 = lean_nat_dec_eq(x_46, x_92);
if (x_93 == 0)
{
lean_object* x_94; 
lean_dec_ref(x_1);
x_94 = lean_unsigned_to_nat(0u);
x_9 = x_47;
x_10 = x_94;
goto block_45;
}
else
{
lean_object* x_95; lean_object* x_96; 
x_95 = lean_box(0);
x_96 = lp_dasmodel_step___lam__0(x_4, x_1, x_3, x_95);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_96;
goto block_45;
}
}
else
{
lean_object* x_97; lean_object* x_98; 
x_97 = lean_box(0);
x_98 = lp_dasmodel_step___lam__0(x_4, x_1, x_3, x_97);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_98;
goto block_45;
}
}
else
{
lean_object* x_99; lean_object* x_100; 
x_99 = lean_box(0);
x_100 = lp_dasmodel_step___lam__0(x_4, x_1, x_3, x_99);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_100;
goto block_45;
}
}
else
{
lean_object* x_101; lean_object* x_102; 
x_101 = lean_box(0);
x_102 = lp_dasmodel_step___lam__0(x_4, x_1, x_3, x_101);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_102;
goto block_45;
}
}
else
{
lean_object* x_103; lean_object* x_104; 
x_103 = lean_box(0);
x_104 = lp_dasmodel_step___lam__0(x_4, x_1, x_3, x_103);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_104;
goto block_45;
}
}
else
{
lean_object* x_105; lean_object* x_106; 
x_105 = lean_box(0);
x_106 = lp_dasmodel_step___lam__0(x_4, x_1, x_3, x_105);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_106;
goto block_45;
}
}
else
{
lean_object* x_107; lean_object* x_108; 
x_107 = lean_box(0);
x_108 = lp_dasmodel_step___lam__0(x_4, x_1, x_3, x_107);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_108;
goto block_45;
}
}
else
{
lean_object* x_109; lean_object* x_110; 
x_109 = lean_box(0);
x_110 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_109);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_110;
goto block_45;
}
}
else
{
lean_object* x_111; lean_object* x_112; 
x_111 = lean_box(0);
x_112 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_111);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_112;
goto block_45;
}
}
else
{
lean_object* x_113; lean_object* x_114; 
x_113 = lean_box(0);
x_114 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_113);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_114;
goto block_45;
}
}
else
{
lean_object* x_115; lean_object* x_116; 
x_115 = lean_box(0);
x_116 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_115);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_116;
goto block_45;
}
}
else
{
lean_object* x_117; lean_object* x_118; 
x_117 = lean_box(0);
x_118 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_117);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_118;
goto block_45;
}
}
else
{
lean_object* x_119; lean_object* x_120; 
x_119 = lean_box(0);
x_120 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_119);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_120;
goto block_45;
}
}
else
{
lean_object* x_121; lean_object* x_122; 
x_121 = lean_box(0);
x_122 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_121);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_122;
goto block_45;
}
}
else
{
lean_object* x_123; lean_object* x_124; 
x_123 = lean_box(0);
x_124 = lp_dasmodel_step___lam__1(x_4, x_1, x_3, x_123);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_124;
goto block_45;
}
}
else
{
lean_object* x_125; lean_object* x_126; 
x_125 = lean_box(0);
x_126 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_125);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_126;
goto block_45;
}
}
else
{
lean_object* x_127; lean_object* x_128; 
x_127 = lean_box(0);
x_128 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_127);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_128;
goto block_45;
}
}
else
{
lean_object* x_129; lean_object* x_130; 
x_129 = lean_box(0);
x_130 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_129);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_130;
goto block_45;
}
}
else
{
lean_object* x_131; lean_object* x_132; 
x_131 = lean_box(0);
x_132 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_131);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_132;
goto block_45;
}
}
else
{
lean_object* x_133; lean_object* x_134; 
x_133 = lean_box(0);
x_134 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_133);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_134;
goto block_45;
}
}
else
{
lean_object* x_135; lean_object* x_136; 
x_135 = lean_box(0);
x_136 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_135);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_136;
goto block_45;
}
}
else
{
lean_object* x_137; lean_object* x_138; 
x_137 = lean_box(0);
x_138 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_137);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_138;
goto block_45;
}
}
else
{
lean_object* x_139; lean_object* x_140; 
x_139 = lean_box(0);
x_140 = lp_dasmodel_step___lam__2(x_4, x_1, x_2, x_139);
lean_dec_ref(x_1);
x_9 = x_47;
x_10 = x_140;
goto block_45;
}
}
block_143:
{
lean_object* x_142; 
x_142 = lean_unsigned_to_nat(0u);
x_47 = x_142;
goto block_141;
}
block_152:
{
lean_object* x_144; uint16_t x_145; uint16_t x_146; uint16_t x_147; uint8_t x_148; 
x_144 = lean_ctor_get(x_7, 0);
lean_inc_ref(x_144);
x_145 = lean_ctor_get_uint16(x_144, sizeof(void*)*3);
lean_dec_ref(x_144);
x_146 = 2;
x_147 = lean_uint16_add(x_4, x_146);
x_148 = lean_uint16_dec_eq(x_145, x_147);
if (x_148 == 0)
{
uint8_t x_149; 
x_149 = lp_dasmodel___private_CPU6502_0__pageCross(x_147, x_145);
if (x_149 == 0)
{
lean_object* x_150; 
x_150 = lean_unsigned_to_nat(1u);
x_47 = x_150;
goto block_141;
}
else
{
lean_object* x_151; 
x_151 = lean_unsigned_to_nat(2u);
x_47 = x_151;
goto block_141;
}
}
else
{
goto block_143;
}
}
block_166:
{
if (x_153 == 0)
{
lean_object* x_154; uint8_t x_155; 
x_154 = lean_unsigned_to_nat(240u);
x_155 = lean_nat_dec_eq(x_46, x_154);
if (x_155 == 0)
{
lean_object* x_156; uint8_t x_157; 
x_156 = lean_unsigned_to_nat(208u);
x_157 = lean_nat_dec_eq(x_46, x_156);
if (x_157 == 0)
{
lean_object* x_158; uint8_t x_159; 
x_158 = lean_unsigned_to_nat(48u);
x_159 = lean_nat_dec_eq(x_46, x_158);
if (x_159 == 0)
{
lean_object* x_160; uint8_t x_161; 
x_160 = lean_unsigned_to_nat(16u);
x_161 = lean_nat_dec_eq(x_46, x_160);
if (x_161 == 0)
{
lean_object* x_162; uint8_t x_163; 
x_162 = lean_unsigned_to_nat(80u);
x_163 = lean_nat_dec_eq(x_46, x_162);
if (x_163 == 0)
{
lean_object* x_164; uint8_t x_165; 
x_164 = lean_unsigned_to_nat(112u);
x_165 = lean_nat_dec_eq(x_46, x_164);
if (x_165 == 0)
{
goto block_143;
}
else
{
goto block_152;
}
}
else
{
goto block_152;
}
}
else
{
goto block_152;
}
}
else
{
goto block_152;
}
}
else
{
goto block_152;
}
}
else
{
goto block_152;
}
}
else
{
goto block_152;
}
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execUntilPC(lean_object* x_1, uint16_t x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; uint8_t x_5; 
x_4 = lean_unsigned_to_nat(0u);
x_5 = lean_nat_dec_eq(x_3, x_4);
if (x_5 == 0)
{
uint16_t x_6; uint8_t x_7; 
x_6 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_7 = lean_uint16_dec_eq(x_6, x_2);
if (x_7 == 0)
{
lean_object* x_8; uint8_t x_9; 
x_8 = lp_dasmodel_step(x_1);
x_9 = lean_ctor_get_uint8(x_8, sizeof(void*)*2);
if (x_9 == 0)
{
lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; uint8_t x_15; 
x_10 = lean_ctor_get(x_8, 0);
lean_inc_ref(x_10);
x_11 = lean_ctor_get(x_8, 1);
lean_inc(x_11);
lean_dec_ref(x_8);
x_12 = lean_unsigned_to_nat(1u);
x_13 = lean_nat_sub(x_3, x_12);
x_14 = lp_dasmodel_execUntilPC(x_10, x_2, x_13);
lean_dec(x_13);
x_15 = !lean_is_exclusive(x_14);
if (x_15 == 0)
{
lean_object* x_16; lean_object* x_17; 
x_16 = lean_ctor_get(x_14, 1);
x_17 = l_List_appendTR___redArg(x_11, x_16);
lean_ctor_set(x_14, 1, x_17);
return x_14;
}
else
{
lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; 
x_18 = lean_ctor_get(x_14, 0);
x_19 = lean_ctor_get(x_14, 1);
lean_inc(x_19);
lean_inc(x_18);
lean_dec(x_14);
x_20 = l_List_appendTR___redArg(x_11, x_19);
x_21 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_21, 0, x_18);
lean_ctor_set(x_21, 1, x_20);
return x_21;
}
}
else
{
lean_object* x_22; lean_object* x_23; lean_object* x_24; 
x_22 = lean_ctor_get(x_8, 0);
lean_inc_ref(x_22);
x_23 = lean_ctor_get(x_8, 1);
lean_inc(x_23);
lean_dec_ref(x_8);
x_24 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_24, 0, x_22);
lean_ctor_set(x_24, 1, x_23);
return x_24;
}
}
else
{
lean_object* x_25; lean_object* x_26; 
x_25 = lean_box(0);
x_26 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_26, 0, x_1);
lean_ctor_set(x_26, 1, x_25);
return x_26;
}
}
else
{
lean_object* x_27; lean_object* x_28; 
x_27 = lean_box(0);
x_28 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_28, 0, x_1);
lean_ctor_set(x_28, 1, x_27);
return x_28;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execUntilPC___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint16_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel_execUntilPC(x_1, x_4, x_3);
lean_dec(x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execCall(lean_object* x_1, uint16_t x_2) {
_start:
{
uint8_t x_3; 
x_3 = !lean_is_exclusive(x_1);
if (x_3 == 0)
{
lean_object* x_4; lean_object* x_5; uint8_t x_6; lean_object* x_7; uint16_t x_8; lean_object* x_9; uint8_t x_10; 
x_4 = lean_ctor_get(x_1, 1);
x_5 = lean_unsigned_to_nat(65520u);
x_6 = 0;
x_7 = lean_byte_array_set(x_4, x_5, x_6);
lean_ctor_set(x_1, 1, x_7);
x_8 = 65519;
x_9 = lp_dasmodel_CPU_push16(x_1, x_8);
x_10 = !lean_is_exclusive(x_9);
if (x_10 == 0)
{
uint16_t x_11; lean_object* x_12; lean_object* x_13; 
lean_ctor_set_uint16(x_9, sizeof(void*)*3, x_2);
x_11 = 65520;
x_12 = lean_unsigned_to_nat(500000u);
x_13 = lp_dasmodel_execUntilPC(x_9, x_11, x_12);
return x_13;
}
else
{
uint8_t x_14; uint8_t x_15; uint8_t x_16; uint8_t x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; uint16_t x_22; lean_object* x_23; lean_object* x_24; 
x_14 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 2);
x_15 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 3);
x_16 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 4);
x_17 = lean_ctor_get_uint8(x_9, sizeof(void*)*3 + 5);
x_18 = lean_ctor_get(x_9, 0);
x_19 = lean_ctor_get(x_9, 1);
x_20 = lean_ctor_get(x_9, 2);
lean_inc(x_20);
lean_inc(x_19);
lean_inc(x_18);
lean_dec(x_9);
x_21 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_21, 0, x_18);
lean_ctor_set(x_21, 1, x_19);
lean_ctor_set(x_21, 2, x_20);
lean_ctor_set_uint8(x_21, sizeof(void*)*3 + 2, x_14);
lean_ctor_set_uint8(x_21, sizeof(void*)*3 + 3, x_15);
lean_ctor_set_uint8(x_21, sizeof(void*)*3 + 4, x_16);
lean_ctor_set_uint8(x_21, sizeof(void*)*3 + 5, x_17);
lean_ctor_set_uint16(x_21, sizeof(void*)*3, x_2);
x_22 = 65520;
x_23 = lean_unsigned_to_nat(500000u);
x_24 = lp_dasmodel_execUntilPC(x_21, x_22, x_23);
return x_24;
}
}
else
{
uint8_t x_25; uint8_t x_26; uint8_t x_27; uint8_t x_28; uint16_t x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; uint8_t x_34; lean_object* x_35; lean_object* x_36; uint16_t x_37; lean_object* x_38; uint8_t x_39; uint8_t x_40; uint8_t x_41; uint8_t x_42; lean_object* x_43; lean_object* x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; uint16_t x_48; lean_object* x_49; lean_object* x_50; 
x_25 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 2);
x_26 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_27 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_28 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_29 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_30 = lean_ctor_get(x_1, 0);
x_31 = lean_ctor_get(x_1, 1);
x_32 = lean_ctor_get(x_1, 2);
lean_inc(x_32);
lean_inc(x_31);
lean_inc(x_30);
lean_dec(x_1);
x_33 = lean_unsigned_to_nat(65520u);
x_34 = 0;
x_35 = lean_byte_array_set(x_31, x_33, x_34);
x_36 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_36, 0, x_30);
lean_ctor_set(x_36, 1, x_35);
lean_ctor_set(x_36, 2, x_32);
lean_ctor_set_uint8(x_36, sizeof(void*)*3 + 2, x_25);
lean_ctor_set_uint8(x_36, sizeof(void*)*3 + 3, x_26);
lean_ctor_set_uint8(x_36, sizeof(void*)*3 + 4, x_27);
lean_ctor_set_uint8(x_36, sizeof(void*)*3 + 5, x_28);
lean_ctor_set_uint16(x_36, sizeof(void*)*3, x_29);
x_37 = 65519;
x_38 = lp_dasmodel_CPU_push16(x_36, x_37);
x_39 = lean_ctor_get_uint8(x_38, sizeof(void*)*3 + 2);
x_40 = lean_ctor_get_uint8(x_38, sizeof(void*)*3 + 3);
x_41 = lean_ctor_get_uint8(x_38, sizeof(void*)*3 + 4);
x_42 = lean_ctor_get_uint8(x_38, sizeof(void*)*3 + 5);
x_43 = lean_ctor_get(x_38, 0);
lean_inc_ref(x_43);
x_44 = lean_ctor_get(x_38, 1);
lean_inc_ref(x_44);
x_45 = lean_ctor_get(x_38, 2);
lean_inc(x_45);
if (lean_is_exclusive(x_38)) {
 lean_ctor_release(x_38, 0);
 lean_ctor_release(x_38, 1);
 lean_ctor_release(x_38, 2);
 x_46 = x_38;
} else {
 lean_dec_ref(x_38);
 x_46 = lean_box(0);
}
if (lean_is_scalar(x_46)) {
 x_47 = lean_alloc_ctor(0, 3, 6);
} else {
 x_47 = x_46;
}
lean_ctor_set(x_47, 0, x_43);
lean_ctor_set(x_47, 1, x_44);
lean_ctor_set(x_47, 2, x_45);
lean_ctor_set_uint8(x_47, sizeof(void*)*3 + 2, x_39);
lean_ctor_set_uint8(x_47, sizeof(void*)*3 + 3, x_40);
lean_ctor_set_uint8(x_47, sizeof(void*)*3 + 4, x_41);
lean_ctor_set_uint8(x_47, sizeof(void*)*3 + 5, x_42);
lean_ctor_set_uint16(x_47, sizeof(void*)*3, x_2);
x_48 = 65520;
x_49 = lean_unsigned_to_nat(500000u);
x_50 = lp_dasmodel_execUntilPC(x_47, x_48, x_49);
return x_50;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execCall___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_execCall(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execInit(lean_object* x_1, uint16_t x_2, uint8_t x_3) {
_start:
{
uint8_t x_4; 
x_4 = !lean_is_exclusive(x_1);
if (x_4 == 0)
{
lean_object* x_5; 
lean_ctor_set_uint8(x_1, sizeof(void*)*3 + 2, x_3);
x_5 = lp_dasmodel_execCall(x_1, x_2);
return x_5;
}
else
{
uint8_t x_6; uint8_t x_7; uint8_t x_8; uint16_t x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; lean_object* x_13; lean_object* x_14; 
x_6 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 3);
x_7 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 4);
x_8 = lean_ctor_get_uint8(x_1, sizeof(void*)*3 + 5);
x_9 = lean_ctor_get_uint16(x_1, sizeof(void*)*3);
x_10 = lean_ctor_get(x_1, 0);
x_11 = lean_ctor_get(x_1, 1);
x_12 = lean_ctor_get(x_1, 2);
lean_inc(x_12);
lean_inc(x_11);
lean_inc(x_10);
lean_dec(x_1);
x_13 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_13, 0, x_10);
lean_ctor_set(x_13, 1, x_11);
lean_ctor_set(x_13, 2, x_12);
lean_ctor_set_uint8(x_13, sizeof(void*)*3 + 2, x_3);
lean_ctor_set_uint8(x_13, sizeof(void*)*3 + 3, x_6);
lean_ctor_set_uint8(x_13, sizeof(void*)*3 + 4, x_7);
lean_ctor_set_uint8(x_13, sizeof(void*)*3 + 5, x_8);
lean_ctor_set_uint16(x_13, sizeof(void*)*3, x_9);
x_14 = lp_dasmodel_execCall(x_13, x_2);
return x_14;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execInit___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint16_t x_4; uint8_t x_5; lean_object* x_6; 
x_4 = lean_unbox(x_2);
x_5 = lean_unbox(x_3);
x_6 = lp_dasmodel_execInit(x_1, x_4, x_5);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execPlay(lean_object* x_1, uint16_t x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_execCall(x_1, x_2);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execPlay___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_execPlay(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execFrames(lean_object* x_1, uint16_t x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; uint8_t x_5; 
x_4 = lean_unsigned_to_nat(0u);
x_5 = lean_nat_dec_eq(x_3, x_4);
if (x_5 == 0)
{
lean_object* x_6; uint8_t x_7; 
x_6 = lp_dasmodel_execCall(x_1, x_2);
x_7 = !lean_is_exclusive(x_6);
if (x_7 == 0)
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_8 = lean_ctor_get(x_6, 0);
x_9 = lean_ctor_get(x_6, 1);
x_10 = lean_unsigned_to_nat(1u);
x_11 = lean_nat_sub(x_3, x_10);
x_12 = lp_dasmodel_execFrames(x_8, x_2, x_11);
lean_dec(x_11);
lean_ctor_set_tag(x_6, 1);
lean_ctor_set(x_6, 1, x_12);
lean_ctor_set(x_6, 0, x_9);
return x_6;
}
else
{
lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; 
x_13 = lean_ctor_get(x_6, 0);
x_14 = lean_ctor_get(x_6, 1);
lean_inc(x_14);
lean_inc(x_13);
lean_dec(x_6);
x_15 = lean_unsigned_to_nat(1u);
x_16 = lean_nat_sub(x_3, x_15);
x_17 = lp_dasmodel_execFrames(x_13, x_2, x_16);
lean_dec(x_16);
x_18 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_18, 0, x_14);
lean_ctor_set(x_18, 1, x_17);
return x_18;
}
}
else
{
lean_object* x_19; 
lean_dec_ref(x_1);
x_19 = lean_box(0);
return x_19;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execFrames___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint16_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel_execFrames(x_1, x_4, x_3);
lean_dec(x_3);
return x_5;
}
}
static lean_object* _init_lp_dasmodel_PAL__CYCLES__PER__FRAME(void) {
_start:
{
lean_object* x_1; 
x_1 = lean_unsigned_to_nat(19688u);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execFrameCycleAccurate(lean_object* x_1, uint16_t x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; uint8_t x_5; 
x_3 = lean_ctor_get(x_1, 2);
lean_inc(x_3);
x_4 = lp_dasmodel_execCall(x_1, x_2);
x_5 = !lean_is_exclusive(x_4);
if (x_5 == 0)
{
lean_object* x_6; uint8_t x_7; 
x_6 = lean_ctor_get(x_4, 0);
x_7 = !lean_is_exclusive(x_6);
if (x_7 == 0)
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; 
x_8 = lean_ctor_get(x_6, 2);
lean_dec(x_8);
x_9 = lean_unsigned_to_nat(19688u);
x_10 = lean_nat_add(x_3, x_9);
lean_dec(x_3);
lean_ctor_set(x_6, 2, x_10);
return x_4;
}
else
{
uint8_t x_11; uint8_t x_12; uint8_t x_13; uint8_t x_14; uint16_t x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; lean_object* x_19; lean_object* x_20; 
x_11 = lean_ctor_get_uint8(x_6, sizeof(void*)*3 + 2);
x_12 = lean_ctor_get_uint8(x_6, sizeof(void*)*3 + 3);
x_13 = lean_ctor_get_uint8(x_6, sizeof(void*)*3 + 4);
x_14 = lean_ctor_get_uint8(x_6, sizeof(void*)*3 + 5);
x_15 = lean_ctor_get_uint16(x_6, sizeof(void*)*3);
x_16 = lean_ctor_get(x_6, 0);
x_17 = lean_ctor_get(x_6, 1);
lean_inc(x_17);
lean_inc(x_16);
lean_dec(x_6);
x_18 = lean_unsigned_to_nat(19688u);
x_19 = lean_nat_add(x_3, x_18);
lean_dec(x_3);
x_20 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_20, 0, x_16);
lean_ctor_set(x_20, 1, x_17);
lean_ctor_set(x_20, 2, x_19);
lean_ctor_set_uint8(x_20, sizeof(void*)*3 + 2, x_11);
lean_ctor_set_uint8(x_20, sizeof(void*)*3 + 3, x_12);
lean_ctor_set_uint8(x_20, sizeof(void*)*3 + 4, x_13);
lean_ctor_set_uint8(x_20, sizeof(void*)*3 + 5, x_14);
lean_ctor_set_uint16(x_20, sizeof(void*)*3, x_15);
lean_ctor_set(x_4, 0, x_20);
return x_4;
}
}
else
{
lean_object* x_21; lean_object* x_22; uint8_t x_23; uint8_t x_24; uint8_t x_25; uint8_t x_26; uint16_t x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; lean_object* x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; 
x_21 = lean_ctor_get(x_4, 0);
x_22 = lean_ctor_get(x_4, 1);
lean_inc(x_22);
lean_inc(x_21);
lean_dec(x_4);
x_23 = lean_ctor_get_uint8(x_21, sizeof(void*)*3 + 2);
x_24 = lean_ctor_get_uint8(x_21, sizeof(void*)*3 + 3);
x_25 = lean_ctor_get_uint8(x_21, sizeof(void*)*3 + 4);
x_26 = lean_ctor_get_uint8(x_21, sizeof(void*)*3 + 5);
x_27 = lean_ctor_get_uint16(x_21, sizeof(void*)*3);
x_28 = lean_ctor_get(x_21, 0);
lean_inc_ref(x_28);
x_29 = lean_ctor_get(x_21, 1);
lean_inc_ref(x_29);
if (lean_is_exclusive(x_21)) {
 lean_ctor_release(x_21, 0);
 lean_ctor_release(x_21, 1);
 lean_ctor_release(x_21, 2);
 x_30 = x_21;
} else {
 lean_dec_ref(x_21);
 x_30 = lean_box(0);
}
x_31 = lean_unsigned_to_nat(19688u);
x_32 = lean_nat_add(x_3, x_31);
lean_dec(x_3);
if (lean_is_scalar(x_30)) {
 x_33 = lean_alloc_ctor(0, 3, 6);
} else {
 x_33 = x_30;
}
lean_ctor_set(x_33, 0, x_28);
lean_ctor_set(x_33, 1, x_29);
lean_ctor_set(x_33, 2, x_32);
lean_ctor_set_uint8(x_33, sizeof(void*)*3 + 2, x_23);
lean_ctor_set_uint8(x_33, sizeof(void*)*3 + 3, x_24);
lean_ctor_set_uint8(x_33, sizeof(void*)*3 + 4, x_25);
lean_ctor_set_uint8(x_33, sizeof(void*)*3 + 5, x_26);
lean_ctor_set_uint16(x_33, sizeof(void*)*3, x_27);
x_34 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_34, 0, x_33);
lean_ctor_set(x_34, 1, x_22);
return x_34;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execFrameCycleAccurate___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint16_t x_3; lean_object* x_4; 
x_3 = lean_unbox(x_2);
x_4 = lp_dasmodel_execFrameCycleAccurate(x_1, x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execFramesCycleAccurate(lean_object* x_1, uint16_t x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; uint8_t x_5; 
x_4 = lean_unsigned_to_nat(0u);
x_5 = lean_nat_dec_eq(x_3, x_4);
if (x_5 == 0)
{
lean_object* x_6; uint8_t x_7; 
x_6 = lp_dasmodel_execFrameCycleAccurate(x_1, x_2);
x_7 = !lean_is_exclusive(x_6);
if (x_7 == 0)
{
lean_object* x_8; lean_object* x_9; lean_object* x_10; lean_object* x_11; lean_object* x_12; 
x_8 = lean_ctor_get(x_6, 0);
x_9 = lean_ctor_get(x_6, 1);
x_10 = lean_unsigned_to_nat(1u);
x_11 = lean_nat_sub(x_3, x_10);
x_12 = lp_dasmodel_execFramesCycleAccurate(x_8, x_2, x_11);
lean_dec(x_11);
lean_ctor_set_tag(x_6, 1);
lean_ctor_set(x_6, 1, x_12);
lean_ctor_set(x_6, 0, x_9);
return x_6;
}
else
{
lean_object* x_13; lean_object* x_14; lean_object* x_15; lean_object* x_16; lean_object* x_17; lean_object* x_18; 
x_13 = lean_ctor_get(x_6, 0);
x_14 = lean_ctor_get(x_6, 1);
lean_inc(x_14);
lean_inc(x_13);
lean_dec(x_6);
x_15 = lean_unsigned_to_nat(1u);
x_16 = lean_nat_sub(x_3, x_15);
x_17 = lp_dasmodel_execFramesCycleAccurate(x_13, x_2, x_16);
lean_dec(x_16);
x_18 = lean_alloc_ctor(1, 2, 0);
lean_ctor_set(x_18, 0, x_14);
lean_ctor_set(x_18, 1, x_17);
return x_18;
}
}
else
{
lean_object* x_19; 
lean_dec_ref(x_1);
x_19 = lean_box(0);
return x_19;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_execFramesCycleAccurate___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
uint16_t x_4; lean_object* x_5; 
x_4 = lean_unbox(x_2);
x_5 = lp_dasmodel_execFramesCycleAccurate(x_1, x_4, x_3);
lean_dec(x_3);
return x_5;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; lean_object* x_8; lean_object* x_9; uint8_t x_13; 
x_7 = lean_ctor_get(x_4, 1);
x_8 = lean_ctor_get(x_4, 2);
x_13 = lean_nat_dec_lt(x_6, x_7);
if (x_13 == 0)
{
lean_object* x_14; 
lean_dec(x_6);
x_14 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_14, 0, x_5);
return x_14;
}
else
{
lean_object* x_15; lean_object* x_16; uint8_t x_17; 
x_15 = lean_unsigned_to_nat(65536u);
x_16 = lean_nat_add(x_1, x_6);
x_17 = lean_nat_dec_lt(x_16, x_15);
if (x_17 == 0)
{
lean_dec(x_16);
x_9 = x_5;
goto block_12;
}
else
{
lean_object* x_18; uint8_t x_19; lean_object* x_20; 
x_18 = lean_nat_add(x_2, x_6);
x_19 = lean_byte_array_get(x_3, x_18);
lean_dec(x_18);
x_20 = lean_byte_array_set(x_5, x_16, x_19);
lean_dec(x_16);
x_9 = x_20;
goto block_12;
}
}
block_12:
{
lean_object* x_10; 
x_10 = lean_nat_add(x_6, x_8);
lean_dec(x_6);
x_5 = x_9;
x_6 = x_10;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6) {
_start:
{
lean_object* x_7; 
x_7 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___redArg(x_1, x_2, x_3, x_4, x_5, x_6);
lean_dec_ref(x_4);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_7;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___redArg(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; lean_object* x_5; uint8_t x_6; 
x_4 = lean_ctor_get(x_1, 1);
x_5 = lean_ctor_get(x_1, 2);
x_6 = lean_nat_dec_lt(x_3, x_4);
if (x_6 == 0)
{
lean_object* x_7; 
lean_dec(x_3);
x_7 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_7, 0, x_2);
return x_7;
}
else
{
uint8_t x_8; lean_object* x_9; lean_object* x_10; 
x_8 = 0;
x_9 = lean_byte_array_push(x_2, x_8);
x_10 = lean_nat_add(x_3, x_5);
lean_dec(x_3);
x_2 = x_9;
x_3 = x_10;
goto _start;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___redArg___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3) {
_start:
{
lean_object* x_4; 
x_4 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___redArg(x_1, x_2, x_3);
lean_dec_ref(x_1);
return x_4;
}
}
static lean_object* _init_lp_dasmodel_loadSID___closed__0(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_mk_empty_array_with_capacity(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_loadSID___closed__1(void) {
_start:
{
lean_object* x_1; lean_object* x_2; 
x_1 = lean_obj_once(&lp_dasmodel_loadSID___closed__0, &lp_dasmodel_loadSID___closed__0_once, _init_lp_dasmodel_loadSID___closed__0);
x_2 = lean_byte_array_mk(x_1);
return x_2;
}
}
static lean_object* _init_lp_dasmodel_loadSID___closed__3(void) {
_start:
{
lean_object* x_1; lean_object* x_2; lean_object* x_3; lean_object* x_4; 
x_1 = lean_unsigned_to_nat(0u);
x_2 = lean_obj_once(&lp_dasmodel_loadSID___closed__1, &lp_dasmodel_loadSID___closed__1_once, _init_lp_dasmodel_loadSID___closed__1);
x_3 = ((lean_object*)(lp_dasmodel_loadSID___closed__2));
x_4 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___redArg(x_3, x_2, x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_loadSID(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; uint8_t x_4; 
x_2 = lean_byte_array_size(x_1);
x_3 = lean_unsigned_to_nat(126u);
x_4 = lean_nat_dec_lt(x_2, x_3);
if (x_4 == 0)
{
lean_object* x_5; uint8_t x_6; uint8_t x_7; uint8_t x_8; 
x_5 = lean_unsigned_to_nat(0u);
x_6 = lean_byte_array_get(x_1, x_5);
x_7 = 80;
x_8 = lean_uint8_dec_eq(x_6, x_7);
if (x_8 == 0)
{
lean_object* x_9; 
x_9 = lean_box(0);
return x_9;
}
else
{
lean_object* x_10; uint8_t x_11; uint8_t x_12; uint8_t x_13; 
x_10 = lean_unsigned_to_nat(1u);
x_11 = lean_byte_array_get(x_1, x_10);
x_12 = 83;
x_13 = lean_uint8_dec_eq(x_11, x_12);
if (x_13 == 0)
{
lean_object* x_14; 
x_14 = lean_box(0);
return x_14;
}
else
{
lean_object* x_15; lean_object* x_16; lean_object* x_17; uint8_t x_18; lean_object* x_19; lean_object* x_20; lean_object* x_21; lean_object* x_22; uint8_t x_23; lean_object* x_24; lean_object* x_25; lean_object* x_26; uint8_t x_27; lean_object* x_28; lean_object* x_29; lean_object* x_30; uint8_t x_31; lean_object* x_32; lean_object* x_33; lean_object* x_34; uint8_t x_35; lean_object* x_36; lean_object* x_37; lean_object* x_38; uint8_t x_39; lean_object* x_40; lean_object* x_41; uint16_t x_42; lean_object* x_43; uint8_t x_44; lean_object* x_45; lean_object* x_46; lean_object* x_47; uint8_t x_48; lean_object* x_49; lean_object* x_50; uint16_t x_51; lean_object* x_52; lean_object* x_53; lean_object* x_54; uint8_t x_82; lean_object* x_83; 
x_15 = lean_obj_once(&lp_dasmodel_loadSID___closed__3, &lp_dasmodel_loadSID___closed__3_once, _init_lp_dasmodel_loadSID___closed__3);
x_16 = lean_ctor_get(x_15, 0);
lean_inc(x_16);
x_17 = lean_unsigned_to_nat(6u);
x_18 = lean_byte_array_get(x_1, x_17);
x_19 = lean_uint8_to_nat(x_18);
x_20 = lean_unsigned_to_nat(256u);
x_21 = lean_nat_mul(x_19, x_20);
x_22 = lean_unsigned_to_nat(7u);
x_23 = lean_byte_array_get(x_1, x_22);
x_24 = lean_uint8_to_nat(x_23);
x_25 = lean_nat_add(x_21, x_24);
lean_dec(x_21);
x_26 = lean_unsigned_to_nat(8u);
x_27 = lean_byte_array_get(x_1, x_26);
x_28 = lean_uint8_to_nat(x_27);
x_29 = lean_nat_mul(x_28, x_20);
x_30 = lean_unsigned_to_nat(9u);
x_31 = lean_byte_array_get(x_1, x_30);
x_32 = lean_uint8_to_nat(x_31);
x_33 = lean_nat_add(x_29, x_32);
lean_dec(x_29);
x_34 = lean_unsigned_to_nat(10u);
x_35 = lean_byte_array_get(x_1, x_34);
x_36 = lean_uint8_to_nat(x_35);
x_37 = lean_nat_mul(x_36, x_20);
x_38 = lean_unsigned_to_nat(11u);
x_39 = lean_byte_array_get(x_1, x_38);
x_40 = lean_uint8_to_nat(x_39);
x_41 = lean_nat_add(x_37, x_40);
lean_dec(x_37);
x_42 = lean_uint16_of_nat(x_41);
lean_dec(x_41);
x_43 = lean_unsigned_to_nat(12u);
x_44 = lean_byte_array_get(x_1, x_43);
x_45 = lean_uint8_to_nat(x_44);
x_46 = lean_nat_mul(x_45, x_20);
x_47 = lean_unsigned_to_nat(13u);
x_48 = lean_byte_array_get(x_1, x_47);
x_49 = lean_uint8_to_nat(x_48);
x_50 = lean_nat_add(x_46, x_49);
lean_dec(x_46);
x_51 = lean_uint16_of_nat(x_50);
lean_dec(x_50);
x_52 = l_ByteArray_extract(x_1, x_25, x_2);
x_82 = lean_nat_dec_eq(x_33, x_5);
if (x_82 == 0)
{
x_83 = x_33;
goto block_85;
}
else
{
uint8_t x_86; lean_object* x_87; uint8_t x_88; lean_object* x_89; lean_object* x_90; lean_object* x_91; 
lean_dec(x_33);
x_86 = lean_byte_array_get(x_52, x_5);
x_87 = lean_uint8_to_nat(x_86);
x_88 = lean_byte_array_get(x_52, x_10);
x_89 = lean_uint8_to_nat(x_88);
x_90 = lean_nat_mul(x_89, x_20);
x_91 = lean_nat_add(x_87, x_90);
lean_dec(x_90);
x_83 = x_91;
goto block_85;
}
block_81:
{
lean_object* x_55; lean_object* x_56; lean_object* x_57; lean_object* x_58; uint8_t x_59; 
x_55 = lean_byte_array_size(x_52);
x_56 = lean_nat_sub(x_55, x_54);
x_57 = lean_alloc_ctor(0, 3, 0);
lean_ctor_set(x_57, 0, x_5);
lean_ctor_set(x_57, 1, x_56);
lean_ctor_set(x_57, 2, x_10);
x_58 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___redArg(x_53, x_54, x_52, x_57, x_16, x_5);
lean_dec_ref(x_57);
lean_dec_ref(x_52);
lean_dec(x_54);
lean_dec(x_53);
x_59 = !lean_is_exclusive(x_58);
if (x_59 == 0)
{
lean_object* x_60; uint8_t x_61; uint8_t x_62; uint16_t x_63; lean_object* x_64; lean_object* x_65; lean_object* x_66; lean_object* x_67; lean_object* x_68; lean_object* x_69; 
x_60 = lean_ctor_get(x_58, 0);
x_61 = 0;
x_62 = 253;
x_63 = 0;
x_64 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_64, 0, x_4);
lean_ctor_set_uint8(x_64, 1, x_13);
lean_ctor_set_uint8(x_64, 2, x_13);
lean_ctor_set_uint8(x_64, 3, x_4);
lean_ctor_set_uint8(x_64, 4, x_4);
lean_ctor_set_uint8(x_64, 5, x_4);
x_65 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_65, 0, x_64);
lean_ctor_set(x_65, 1, x_60);
lean_ctor_set(x_65, 2, x_5);
lean_ctor_set_uint8(x_65, sizeof(void*)*3 + 2, x_61);
lean_ctor_set_uint8(x_65, sizeof(void*)*3 + 3, x_61);
lean_ctor_set_uint8(x_65, sizeof(void*)*3 + 4, x_61);
lean_ctor_set_uint8(x_65, sizeof(void*)*3 + 5, x_62);
lean_ctor_set_uint16(x_65, sizeof(void*)*3, x_63);
x_66 = lean_box(x_42);
x_67 = lean_box(x_51);
x_68 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_68, 0, x_66);
lean_ctor_set(x_68, 1, x_67);
x_69 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_69, 0, x_65);
lean_ctor_set(x_69, 1, x_68);
lean_ctor_set(x_58, 0, x_69);
return x_58;
}
else
{
lean_object* x_70; uint8_t x_71; uint8_t x_72; uint16_t x_73; lean_object* x_74; lean_object* x_75; lean_object* x_76; lean_object* x_77; lean_object* x_78; lean_object* x_79; lean_object* x_80; 
x_70 = lean_ctor_get(x_58, 0);
lean_inc(x_70);
lean_dec(x_58);
x_71 = 0;
x_72 = 253;
x_73 = 0;
x_74 = lean_alloc_ctor(0, 0, 6);
lean_ctor_set_uint8(x_74, 0, x_4);
lean_ctor_set_uint8(x_74, 1, x_13);
lean_ctor_set_uint8(x_74, 2, x_13);
lean_ctor_set_uint8(x_74, 3, x_4);
lean_ctor_set_uint8(x_74, 4, x_4);
lean_ctor_set_uint8(x_74, 5, x_4);
x_75 = lean_alloc_ctor(0, 3, 6);
lean_ctor_set(x_75, 0, x_74);
lean_ctor_set(x_75, 1, x_70);
lean_ctor_set(x_75, 2, x_5);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 2, x_71);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 3, x_71);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 4, x_71);
lean_ctor_set_uint8(x_75, sizeof(void*)*3 + 5, x_72);
lean_ctor_set_uint16(x_75, sizeof(void*)*3, x_73);
x_76 = lean_box(x_42);
x_77 = lean_box(x_51);
x_78 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_78, 0, x_76);
lean_ctor_set(x_78, 1, x_77);
x_79 = lean_alloc_ctor(0, 2, 0);
lean_ctor_set(x_79, 0, x_75);
lean_ctor_set(x_79, 1, x_78);
x_80 = lean_alloc_ctor(1, 1, 0);
lean_ctor_set(x_80, 0, x_79);
return x_80;
}
}
block_85:
{
if (x_82 == 0)
{
x_53 = x_83;
x_54 = x_5;
goto block_81;
}
else
{
lean_object* x_84; 
x_84 = lean_unsigned_to_nat(2u);
x_53 = x_83;
x_54 = x_84;
goto block_81;
}
}
}
}
}
else
{
lean_object* x_92; 
x_92 = lean_box(0);
return x_92;
}
}
}
LEAN_EXPORT lean_object* lp_dasmodel_loadSID___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_loadSID(x_1);
lean_dec_ref(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___redArg(x_1, x_2, x_3);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5) {
_start:
{
lean_object* x_6; 
x_6 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__0(x_1, x_2, x_3, x_4, x_5);
lean_dec_ref(x_1);
return x_6;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___redArg(x_1, x_2, x_3, x_4, x_5, x_6);
return x_9;
}
}
LEAN_EXPORT lean_object* lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1___boxed(lean_object* x_1, lean_object* x_2, lean_object* x_3, lean_object* x_4, lean_object* x_5, lean_object* x_6, lean_object* x_7, lean_object* x_8) {
_start:
{
lean_object* x_9; 
x_9 = lp_dasmodel___private_Init_Data_Range_Basic_0__Std_Legacy_Range_forIn_x27_loop___at___00loadSID_spec__1(x_1, x_2, x_3, x_4, x_5, x_6, x_7, x_8);
lean_dec_ref(x_4);
lean_dec_ref(x_3);
lean_dec(x_2);
lean_dec(x_1);
return x_9;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_SID(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_CPU6502(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_SID(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
lp_dasmodel_PAL__CYCLES__PER__FRAME = _init_lp_dasmodel_PAL__CYCLES__PER__FRAME();
lean_mark_persistent(lp_dasmodel_PAL__CYCLES__PER__FRAME);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
