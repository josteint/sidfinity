// Lean compiler output
// Module: State
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
static const lean_ctor_object lp_dasmodel_VoiceState_init___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_ctor_object) + sizeof(void*)*12 + 8, .m_other = 12, .m_tag = 0}, .m_objs = {((lean_object*)(((size_t)(1) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),((lean_object*)(((size_t)(0) << 1) | 1)),LEAN_SCALAR_PTR_LITERAL(0, 0, 0, 0, 0, 0, 0, 0)}};
static const lean_object* lp_dasmodel_VoiceState_init___closed__0 = (const lean_object*)&lp_dasmodel_VoiceState_init___closed__0_value;
LEAN_EXPORT const lean_object* lp_dasmodel_VoiceState_init = (const lean_object*)&lp_dasmodel_VoiceState_init___closed__0_value;
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__0(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__0___boxed(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__1(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__1___boxed(lean_object*, lean_object*);
static const lean_closure_object lp_dasmodel_EngineState_init___closed__0_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*0, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_EngineState_init___lam__0___boxed, .m_arity = 1, .m_num_fixed = 0, .m_objs = {} };
static const lean_object* lp_dasmodel_EngineState_init___closed__0 = (const lean_object*)&lp_dasmodel_EngineState_init___closed__0_value;
static const lean_closure_object lp_dasmodel_EngineState_init___closed__1_value = {.m_header = {.m_rc = 0, .m_cs_sz = sizeof(lean_closure_object) + sizeof(void*)*1, .m_other = 0, .m_tag = 245}, .m_fun = (void*)lp_dasmodel_EngineState_init___lam__1___boxed, .m_arity = 2, .m_num_fixed = 1, .m_objs = {((lean_object*)(((size_t)(0) << 1) | 1))} };
static const lean_object* lp_dasmodel_EngineState_init___closed__1 = (const lean_object*)&lp_dasmodel_EngineState_init___closed__1_value;
lean_object* l_List_replicateTR___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init(lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__0(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = ((lean_object*)(lp_dasmodel_VoiceState_init));
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__0___boxed(lean_object* x_1) {
_start:
{
lean_object* x_2; 
x_2 = lp_dasmodel_EngineState_init___lam__0(x_1);
lean_dec(x_1);
return x_2;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__1(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_inc(x_1);
return x_1;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init___lam__1___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; 
x_3 = lp_dasmodel_EngineState_init___lam__1(x_1, x_2);
lean_dec(x_2);
lean_dec(x_1);
return x_3;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_EngineState_init(lean_object* x_1) {
_start:
{
lean_object* x_2; lean_object* x_3; lean_object* x_4; lean_object* x_5; lean_object* x_6; lean_object* x_7; 
x_2 = ((lean_object*)(lp_dasmodel_EngineState_init___closed__0));
x_3 = lean_unsigned_to_nat(255u);
x_4 = lean_unsigned_to_nat(0u);
x_5 = ((lean_object*)(lp_dasmodel_EngineState_init___closed__1));
x_6 = l_List_replicateTR___redArg(x_1, x_4);
x_7 = lean_alloc_ctor(0, 4, 0);
lean_ctor_set(x_7, 0, x_3);
lean_ctor_set(x_7, 1, x_2);
lean_ctor_set(x_7, 2, x_6);
lean_ctor_set(x_7, 3, x_5);
return x_7;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_SID(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_State(uint8_t builtin) {
lean_object * res;
if (_G_initialized) return lean_io_result_mk_ok(lean_box(0));
_G_initialized = true;
res = initialize_Init(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_SID(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
