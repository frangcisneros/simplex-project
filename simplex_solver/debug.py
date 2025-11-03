#!/usr/bin/env python3

class Debug:
    def __init__(self, level='NONE', out_file=None, step=False):
        self.level = level  # 'L', 'M', 'XL'
        self.trace = []     # Lista de dicts por iteración
        self.out_file = out_file
        self.step = step

    def log_iteration(self, iteration:int, tableau:list, entering:str, leaving:str, pivot:float, ratios:list, z:float, msg:str=None):
        entry = {
            "iteration": iteration,
            "tableau": tableau,     # Tabla como lista de listas (números)
            "entering": entering,
            "leaving": leaving,
            "pivot": pivot,
            "ratios": ratios,
            "z": z,
            "msg": msg
        }
        self.trace.append(entry)
        if self.level in ('L','M','XL'):
            self._print_summary(entry)
        if self.step:
            self._interactive_prompt()

    def dump_json(self, path):
        import json
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.trace, f, indent=2, ensure_ascii=False)

    def _print_summary(self, entry):
        # Dependiendo del nivel imprime más/menos detalle
        print(f"=== Iter {entry['iteration']} | enter={entry['entering']} leave={entry['leaving']} pivot={entry['pivot']} z={entry['z']} ===")
        if self.level in ('M','XL'):
            # Imprimir ratios y tabla completa
            print("Ratios:", entry['ratios'])
            print("Tableau:")
            for row in entry['tableau']:
                print("  ", " ".join(f"{x:.3g}" for x in row))
