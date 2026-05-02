// Lean compiler output
// Module: Properties
// Imports: public import Init public import SID public import State public import Effects public import Compile
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
uint8_t lp_dasmodel_instDecidableEqSIDReg_decEq(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel_findWriteIdx___lam__0(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_findWriteIdx___lam__0___boxed(lean_object*, lean_object*);
lean_object* l_List_findIdx_x3f___redArg(lean_object*, lean_object*);
LEAN_EXPORT lean_object* lp_dasmodel_findWriteIdx(lean_object*, lean_object*);
LEAN_EXPORT uint8_t lp_dasmodel_findWriteIdx___lam__0(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; uint8_t x_4; 
x_3 = lean_ctor_get(x_2, 0);
lean_inc(x_3);
lean_dec_ref(x_2);
x_4 = lp_dasmodel_instDecidableEqSIDReg_decEq(x_3, x_1);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_findWriteIdx___lam__0___boxed(lean_object* x_1, lean_object* x_2) {
_start:
{
uint8_t x_3; lean_object* x_4; 
x_3 = lp_dasmodel_findWriteIdx___lam__0(x_1, x_2);
x_4 = lean_box(x_3);
return x_4;
}
}
LEAN_EXPORT lean_object* lp_dasmodel_findWriteIdx(lean_object* x_1, lean_object* x_2) {
_start:
{
lean_object* x_3; lean_object* x_4; 
x_3 = lean_alloc_closure((void*)(lp_dasmodel_findWriteIdx___lam__0___boxed), 2, 1);
lean_closure_set(x_3, 0, x_2);
x_4 = l_List_findIdx_x3f___redArg(x_3, x_1);
return x_4;
}
}
lean_object* initialize_Init(uint8_t builtin);
lean_object* initialize_dasmodel_SID(uint8_t builtin);
lean_object* initialize_dasmodel_State(uint8_t builtin);
lean_object* initialize_dasmodel_Effects(uint8_t builtin);
lean_object* initialize_dasmodel_Compile(uint8_t builtin);
static bool _G_initialized = false;
LEAN_EXPORT lean_object* initialize_dasmodel_Properties(uint8_t builtin) {
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
res = initialize_dasmodel_Effects(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
res = initialize_dasmodel_Compile(builtin);
if (lean_io_result_is_error(res)) return res;
lean_dec_ref(res);
return lean_io_result_mk_ok(lean_box(0));
}
#ifdef __cplusplus
}
#endif
