from __future__ import annotations

from core.truth_analyzer import TruthAnalyzer
from core.func_checker import BoolFuncChecker
from core.qmc_kernel import QMCKernel


def show_tt(func: TruthAnalyzer) -> None:
    print("Таблица истинности:")
    print(func.to_table_str())


def show_post(func: TruthAnalyzer) -> None:
    pa = BoolFuncChecker(func.vector, func.variables)
    print("\nКлассы Поста:")
    print(f"T0: {'+' if pa.is_const0() else '-'}")
    print(f"T1: {'+' if pa.is_const1() else '-'}")
    print(f"S:  {'+' if pa.is_selfdual() else '-'}")
    print(f"M:  {'+' if pa.is_monotone() else '-'}")
    print(f"L:  {'+' if pa.is_affine() else '-'}")
    print(f"Полином Жегалкина: {pa.anf_str()}")
    ess = pa.essential()
    dummy = [v for v, ok in ess.items() if not ok]
    print("Фиктивные переменные:", ", ".join(dummy) if dummy else "нет")


def show_deriv(func: TruthAnalyzer) -> None:
    pa = BoolFuncChecker(func.vector, func.variables)
    if not func.variables:
        return
    targets = func.variables[:min(4, len(func.variables))]
    res_vec, res_vars = pa.multi_derivative(targets)
    print("\nБулева дифференциация:")
    print(f"∂/{','.join(targets)} = {BoolFuncChecker.to_sop(res_vec, res_vars)}")


def show_minimize(func: TruthAnalyzer) -> None:
    mz = QMCKernel(func.vector, func.variables)
    for mode in ("SOP", "POS"):
        calc = mz.run(mode)
        tbl = mz.with_coverage_table(mode)
        print(f"\nРасчетный метод ({mode}):")
        print("Этапы склеивания:")
        for st in calc["steps"]:
            print(f"  {st.level}: {', '.join(st.cubes)}")
        print(f"Результат: {calc['result']}")
        print(f"Расчетно-табличный метод ({mode}):")
        for row in tbl["table"]:
            print(f"  {row['expr']}: {row['covers']}")
        print(f"Результат: {tbl['result']}")

    if len(func.variables) >= 2:
        k = mz.karnaugh_maps()
        print("\nКарта Карно (ДНФ):")
        for layer in k["SOP"]["layers"]:
            if layer["extra"] is not None:
                extra_var = func.variables[4] if len(func.variables) == 5 else ""
                print(f"Слой {extra_var} = {layer['extra']}")
            print("    " + "  ".join(layer["col_codes"]))
            for code, row in layer["grid"]:
                print(f"{code} | " + "  ".join(str(v) for v in row))
        print("Минимизированная ДНФ:", k["SOP"]["result"])
        print("\nКарта Карно (КНФ):")
        for layer in k["POS"]["layers"]:
            if layer["extra"] is not None:
                extra_var = func.variables[4] if len(func.variables) == 5 else ""
                print(f"Слой {extra_var} = {layer['extra']}")
            print("    " + "  ".join(layer["col_codes"]))
            for code, row in layer["grid"]:
                print(f"{code} | " + "  ".join(str(v) for v in row))
        print("Минимизированная КНФ:", k["POS"]["result"])


def main():
    expr = input("Введите логическую функцию: ").strip()
    bf = TruthAnalyzer(expr)
    show_tt(bf)
    print("\nСДНФ:", bf.to_sop())
    print("СКНФ:", bf.to_pos())
    print("Числовая форма СДНФ:", bf.minterms_repr())
    print("Числовая форма СКНФ:", bf.maxterms_repr())
    print("Индексная форма:", bf.to_bin(), f"(dec={bf.to_int()})")
    show_post(bf)
    show_deriv(bf)
    show_minimize(bf)


if __name__ == "__main__":
    main()
