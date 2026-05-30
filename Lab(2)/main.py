from __future__ import annotations

from algorithms.minimizer import Minimizer
from models.boolean_function import BooleanFunction
from models.post_analyzer import PostAnalyzer

def show_tt(func: BooleanFunction) -> None:
    print("Таблица истинности:")
    print(func.truth_table())

def show_post(func: BooleanFunction) -> None:
    pa = PostAnalyzer(func.vector, func.variables)
    print("\nКлассы Поста:")
    print(f"T0: {'+' if pa.check_t0() else '-'}")
    print(f"T1: {'+' if pa.check_t1() else '-'}")
    print(f"S:  {'+' if pa.check_s() else '-'}")
    print(f"M:  {'+' if pa.check_m() else '-'}")
    print(f"L:  {'+' if pa.check_l() else '-'}")
    print(f"Полином Жегалкина: {pa.zhegalkin_polynomial()}")
    ess = pa.essential_variables()
    dummy = [v for v, ok in ess.items() if not ok]
    print("Фиктивные переменные:", ", ".join(dummy) if dummy else "нет")

def show_deriv(func: BooleanFunction) -> None:
    pa = PostAnalyzer(func.vector, func.variables)
    if not func.variables:
        return
    targets = func.variables[:min(4, len(func.variables))]
    res = pa.mixed_derivative(targets)
    print("\nБулева дифференциация:")
    print(f"∂/{','.join(targets)} = {PostAnalyzer.vector_to_sdnf(res.vector, res.variables)}")

def show_minimize(func: BooleanFunction) -> None:
    mz = Minimizer(func.vector, func.variables)
    for mode in ("DNF", "KNF"):
        calc = mz.calculation_method(mode)
        tbl = mz.table_method(mode)
        print(f"\nРасчетный метод ({mode}):")
        print("Этапы склеивания:")
        for st in calc["stages"]:
            print(f"  {st.stage_number}: {', '.join(st.terms)}")
        print(f"Результат: {calc['result']}")
        print(f"Расчетно-табличный метод ({mode}):")
        for row in tbl["coverage_table"]:
            print(f"  {row['expression']}: {row['coverage']}")
        print(f"Результат: {tbl['result']}")

    if len(func.variables) >= 2:
        k = mz.karnaugh_method()
        print("\nКарта Карно (ДНФ):")
        for layer in k["dnf"]["layers"]:
            if layer["extra_value"] is not None:
                extra_var = func.variables[4] if len(func.variables) == 5 else ""
                print(f"Слой {extra_var} = {layer['extra_value']}")
            print("    " + "  ".join(layer["col_codes"]))
            for code, row in layer["rows"]:
                print(f"{code} | " + "  ".join(str(v) for v in row))
        print("Минимизированная ДНФ:", k["dnf"]["result"])
        print("\nКарта Карно (КНФ):")
        for layer in k["knf"]["layers"]:
            if layer["extra_value"] is not None:
                extra_var = func.variables[4] if len(func.variables) == 5 else ""
                print(f"Слой {extra_var} = {layer['extra_value']}")
            print("    " + "  ".join(layer["col_codes"]))
            for code, row in layer["rows"]:
                print(f"{code} | " + "  ".join(str(v) for v in row))
        print("Минимизированная КНФ:", k["knf"]["result"])

def main():
    expr = input("Введите логическую функцию: ").strip()
    bf = BooleanFunction(expr)
    show_tt(bf)
    print("\nСДНФ:", bf.sdnf())
    print("СКНФ:", bf.sknf())
    print("Числовая форма СДНФ:", bf.numeric_sdnf())
    print("Числовая форма СКНФ:", bf.numeric_sknf())
    print("Индексная форма:", bf.vector_string(), f"(dec={bf.index_form()})")
    show_post(bf)
    show_deriv(bf)
    show_minimize(bf)

if __name__ == "__main__":
    main()