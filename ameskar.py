"""
ameskar.py — Transpilateur Kabyle → Python v1.0
================================================
"Ameskar" signifie "programmeur" / "celui qui code" en kabyle.

ARCHITECTURE :
    1. KabyleIndenter  — PostLexer qui injecte INDENT/DEDENT
    2. build_parser()  — Construit le parser Lark à partir de kabyle.lark
    3. TreeToPython    — Transformer Lark qui visite l'AST et génère
                         du code Python sous forme de chaîne de caractères
    4. transpile()     — Fonction publique : Kabyle → Python str
    5. run()           — Fonction publique : transpile + exec()

EXTENSION FACILE — Pour ajouter un mot-clé, il suffit de :
    a) L'ajouter dans kabyle.lark (déclaration du terminal + règle)
       → structurel : préfixer par _ pour l'écarter de l'arbre
       → valeur/opérateur : garder sans préfixe pour le conserver
    b) Ajouter une méthode de transformation dans TreeToPython
       si c'est un token conservé.
    c) Mettre à jour KEYWORDS_KABYLE_TO_PYTHON (référence/doc).
"""

import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# DÉPENDANCE : lark-parser
# ──────────────────────────────────────────────────────────────────────────────
try:
    from lark import Lark, Transformer, Token, v_args
    from lark.indenter import Indenter
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "lark"])
    from lark import Lark, Transformer, Token, v_args
    from lark.indenter import Indenter


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — DICTIONNAIRE DES MOTS-CLÉS (référence / documentation)
# ══════════════════════════════════════════════════════════════════════════════
# La traduction réelle est faite dans TreeToPython, mais ce dictionnaire
# centralise la correspondance pour faciliter la maintenance.

KEYWORDS_KABYLE_TO_PYTHON: dict = {
    # Kabyle      Python
    "aru":      "print",
    "ma":       "if",
    "ma_ulac":  "else",
    "yal":      "for",
    "deg":      "in",
    "skud":     "while",
    "bnu":      "def",
    "erred":    "return",
    "awid":     "import",
    "Ih":       "True",
    "Ala":      "False",
    "akked":    "and",
    "negh":     "or",
    "macci":    "not",
    # Nouveaux mots-clés
    "seqsi":    "input",
    "eldi":     "open",
    "amnar":    "range",
    "teghzi":   "len",
    "ssenf":    "type",
    "uttu":     "int",
    "awal":     "str",
    "tabdart":  "list",
    "ameqqran": "max",
    "amectuh":  "min",
    "rnu":      "sum",
    "fakk":     "quit",
}

# Chemin vers la grammaire (même dossier que ce script)
_GRAMMAR_PATH = Path(__file__).parent / "kabyle.lark"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — INDENTEUR (PostLexer)
# ══════════════════════════════════════════════════════════════════════════════

class KabyleIndenter(Indenter):
    """
    PostLexer qui transforme les NEWLINE + espaces en tokens INDENT/DEDENT.
    Lark fournit la classe de base `Indenter` ; il suffit de déclarer les
    noms de tokens utilisés dans la grammaire.

    NB : lark >= 1.1 utilise des attributs en camelCase (NL_type, INDENT_type…)
    et non plus les constantes en MAJUSCULES des versions antérieures.
    """
    NL_type           = "_NEWLINE"   # token qui déclenche la vérification
    OPEN_PAREN_types  = []           # pas de continuation multi-ligne sur "("
    CLOSE_PAREN_types = []           # idem pour ")"
    INDENT_type       = "_INDENT"
    DEDENT_type       = "_DEDENT"
    tab_len           = 4            # taille d'un niveau d'indentation


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — CONSTRUCTION DU PARSER
# ══════════════════════════════════════════════════════════════════════════════

def build_parser() -> Lark:
    """
    Charge la grammaire depuis kabyle.lark et construit le parser Lark.

    Paramètres importants :
      - parser="lalr"       : l'Indenter est conçu pour LALR (plus rapide
                              et plus prédictible qu'Earley pour ce cas)
      - postlex             : notre KabyleIndenter pour gérer l'indentation
      - propagate_positions : numéros de ligne dans les nœuds (messages d'erreur)
      - maybe_placeholders  : False pour que les optionnels absents ne
                              produisent pas de None dans les enfants
    """
    grammar_text = _GRAMMAR_PATH.read_text(encoding="utf-8")

    return Lark(
        grammar_text,
        parser="lalr",
        postlex=KabyleIndenter(),
        propagate_positions=True,
        maybe_placeholders=False,
    )


# Instance globale du parser (singleton — évite de recharger la grammaire
# à chaque appel de transpile()).
_PARSER = None


def get_parser() -> Lark:
    """Retourne le parser singleton, le crée si nécessaire."""
    global _PARSER
    if _PARSER is None:
        _PARSER = build_parser()
    return _PARSER


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — TRANSFORMER : AST → CODE PYTHON
# ══════════════════════════════════════════════════════════════════════════════

@v_args(inline=True)
class TreeToPython(Transformer):
    """
    Visite l'AST produit par Lark et génère du code Python sous forme de
    chaîne de caractères.

    CONVENTION :
      - Chaque méthode correspond à une règle (ou à un alias de règle)
        de la grammaire (même nom).
      - Avec @v_args(inline=True), les enfants du nœud sont passés comme
        arguments positionnels individuels (et non comme une liste).
      - Les terminaux *conservés* dans l'arbre (ex: NEGH, AKKED, MACCI,
        IH, ALA, ARU, PLUS, MINUS…) sont transformés par une méthode
        du même nom et apparaissent ensuite comme arguments dans les
        règles parents.
      - Les terminaux *écartés* (préfixe _ dans la grammaire, ex: _MA,
        _YAL, _DEG…) n'apparaissent PAS dans les enfants et n'ont donc
        pas besoin de méthode.

    L'indentation est gérée ici manuellement via `_indent_level`.
    """

    def __init__(self):
        super().__init__()
        self._indent_level: int = 0     # niveau d'indentation courant
        self._indent_str: str  = "    " # 4 espaces par niveau

    # ── Utilitaires internes ──────────────────────────────────────────────────

    def _indent(self) -> str:
        """Retourne la chaîne d'indentation pour le niveau courant."""
        return self._indent_str * self._indent_level

    def _generate_block(self, statements) -> str:
        """
        Transforme une liste d'instructions en un bloc indenté.
        Incrémente/décrémente _indent_level autour du contenu.
        """
        self._indent_level += 1
        lines = []
        for stmt in statements:
            for line in stmt.splitlines():
                lines.append(self._indent() + line)
        self._indent_level -= 1
        return "\n".join(lines)

    # ── Point d'entrée ────────────────────────────────────────────────────────

    def start(self, *stmts) -> str:
        """Règle racine : concatène toutes les instructions de haut niveau."""
        return "\n".join(s for s in stmts if s and str(s).strip())

    # ── Wrappers de passthrough ───────────────────────────────────────────────

    def statement(self, stmt) -> str:
        return stmt

    def simple_stmt(self, stmt) -> str:
        return stmt

    def compound_stmt(self, stmt) -> str:
        return stmt

    def expr_stmt(self, expr) -> str:
        """Une expression seule (ex: appel de fonction comme aru(...))."""
        return expr

    # ── Import (awid) ─────────────────────────────────────────────────────────
    # Avec _AWID et _DEG écartés, on reçoit :
    #   - 1 arg : (nom_module,)                → import nom_module
    #   - 2 args: (nom_module, nom_symbol)     → from nom_module import nom_symbol

    def import_stmt(self, *args) -> str:
        if len(args) == 1:
            return f"import {args[0]}"
        if len(args) == 2:
            return f"from {args[0]} import {args[1]}"
        # Ne devrait pas arriver
        return f"import {' '.join(str(a) for a in args)}"

    # ── Définition de fonction (bnu) ──────────────────────────────────────────
    # Avec _BNU écarté, on reçoit :
    #   - 2 args : (nom, block)                → fonction sans paramètres
    #   - 3 args : (nom, parameters, block)    → fonction avec paramètres

    def funcdef(self, name, *rest) -> str:
        if len(rest) == 2:
            params_str, block_str = rest
        else:
            params_str = ""
            block_str = rest[0]
        header = f"def {name}({params_str}):"
        return f"{header}\n{block_str}"

    def parameters(self, *names) -> str:
        """Liste de paramètres séparés par des virgules."""
        return ", ".join(str(n) for n in names)

    # ── Retour (erred) ────────────────────────────────────────────────────────
    # Avec _ERRED écarté, on reçoit :
    #   - 0 arg  : return
    #   - 1 arg  : return <expr>

    def return_stmt(self, *args) -> str:
        if args:
            return f"return {args[0]}"
        return "return"

    # ── Assignation ───────────────────────────────────────────────────────────

    def assign_stmt(self, name, op, value) -> str:
        return f"{name} {op} {value}"

    # Opérateurs d'assignation — chaque alias retourne la chaîne Python
    def assign(self) -> str: return "="
    def iadd(self)   -> str: return "+="
    def isub(self)   -> str: return "-="
    def imul(self)   -> str: return "*="
    def idiv(self)   -> str: return "/="

    # ── Condition (ma / ma_ulac) ──────────────────────────────────────────────
    # Avec _MA et _MA_ULAC écartés, on reçoit :
    #   - 2 args : (cond, if_block)                → if seul
    #   - 3 args : (cond, if_block, else_block)    → if / else

    def if_stmt(self, *args) -> str:
        if len(args) == 2:
            cond, if_block = args
            return f"if {cond}:\n{if_block}"
        cond, if_block, else_block = args
        return f"if {cond}:\n{if_block}\nelse:\n{else_block}"

    # ── Boucle while (skud) ───────────────────────────────────────────────────
    # Avec _SKUD écarté : (cond, block)

    def while_stmt(self, cond, block) -> str:
        return f"while {cond}:\n{block}"

    # ── Boucle for (yal ... deg ...) ──────────────────────────────────────────
    # Avec _YAL et _DEG écartés : (var, iterable, block)

    def for_stmt(self, var, iterable, block) -> str:
        return f"for {var} in {iterable}:\n{block}"

    # ── Bloc indenté ──────────────────────────────────────────────────────────

    def block(self, *stmts) -> str:
        """Génère le corps indenté d'un bloc."""
        return self._generate_block([s for s in stmts if s and str(s).strip()])

    # ── Expressions logiques ──────────────────────────────────────────────────
    # Les règles `?or_expr` et `?and_expr` sont inlinées si un seul enfant.
    # Sinon, elles sont appelées avec une liste alternée :
    #   (expr, "or", expr, "or", expr, ...)  — car NEGH est conservé dans
    #   l'arbre et sa méthode NEGH() retourne "or".
    # Il suffit donc de joindre avec un simple espace.

    def or_expr(self, *args) -> str:
        return " ".join(str(a) for a in args)

    def and_expr(self, *args) -> str:
        return " ".join(str(a) for a in args)

    # Pour not_expr, la grammaire `?not_expr: MACCI not_expr | comparison`
    # n'appelle cette méthode QUE pour le cas MACCI (le cas comparison
    # est inliné grâce au '?'). On reçoit donc toujours 2 arguments :
    #   (macci_str="not", expr_str)
    def not_expr(self, _macci, e) -> str:
        return f"not {e}"

    # ── Comparaisons ──────────────────────────────────────────────────────────
    # `?comparison` : appelé uniquement si ≥ 2 opérandes.
    # args = (expr, op_str, expr [, op_str, expr …])
    # Les op_str sont déjà transformés ("==", "!=", etc.) par eq/ne/…

    def comparison(self, *args) -> str:
        return " ".join(str(a) for a in args)

    # Opérateurs de comparaison (aliases de comp_op)
    def eq(self) -> str: return "=="
    def ne(self) -> str: return "!="
    def lt(self) -> str: return "<"
    def le(self) -> str: return "<="
    def gt(self) -> str: return ">"
    def ge(self) -> str: return ">="

    # ── Arithmétique ──────────────────────────────────────────────────────────
    # `?arith_expr` et `?term` : appelés uniquement si ≥ 2 opérandes.
    # args = (expr, op_str, expr, …)  — les PLUS/MINUS/STAR/… sont
    # déjà transformés en "+", "-", "*", … par leurs méthodes.

    def arith_expr(self, *args) -> str:
        return " ".join(str(a) for a in args)

    def term(self, *args) -> str:
        return " ".join(str(a) for a in args)

    # Unaires : factor → PLUS factor | MINUS factor
    # On reçoit (sign_str, expr_str) ; on ignore le signe car il est
    # déterminé par l'alias (uplus/uminus).
    def uplus(self, _sign, e) -> str:
        return f"+{e}"

    def uminus(self, _sign, e) -> str:
        return f"-{e}"

    # `?power` : appelé uniquement si atom ** factor (2 enfants ; "**" anonyme)
    def power(self, base, exp) -> str:
        return f"{base} ** {exp}"

    # ── Terminaux opérateurs ──────────────────────────────────────────────────
    # Transforment les tokens conservés en leur équivalent Python (ici
    # identique mais on garde les méthodes pour rester explicite).

    def PLUS(self, _):        return "+"
    def MINUS(self, _):       return "-"
    def STAR(self, _):        return "*"
    def SLASH(self, _):       return "/"
    def PERCENT(self, _):     return "%"
    def DOUBLESLASH(self, _): return "//"

    # ── Atomes ────────────────────────────────────────────────────────────────

    def number(self, n) -> str:
        return str(n)

    def string(self, s) -> str:
        return str(s)

    def paren_expr(self, e) -> str:
        return f"({e})"

    def true_val(self, _=None) -> str:
        return "True"

    def false_val(self, _=None) -> str:
        return "False"

    def var(self, name) -> str:
        s = str(name)
        return KEYWORDS_KABYLE_TO_PYTHON.get(s, s)

    def list_literal(self, *args) -> str:
        return "[" + ", ".join(str(a) for a in args) + "]"

    # ── Dictionnaire des méthodes d'objets kabyles → Python ─────────────────
    # Distinct de KEYWORDS_KABYLE_TO_PYTHON car ce sont des noms de méthodes
    # qui ne sont valides QUE dans un contexte `obj.methode(...)`.
    # Pour ajouter une méthode kabyle (ex: f.rnu(x) → f.append(x)), il suffit
    # d'ajouter une entrée ici.
    METHODES_KABYLES = {
        "aru":  "write",   # f.aru("...")  → f.write("...")    (écrire)
        "gher": "read",    # f.gher()      → f.read()          (lire)
        "mdel": "close",   # f.mdel()      → f.close()         (fermer)
    }

    def attr_call(self, obj, method, *rest) -> str:
        """
        Appel de méthode / accès d'attribut : obj.methode(args).

        Trois cas d'arrivée pour `method` :
          1. Token NAME brut (ex: "read", "gher")  — méthode standard
          2. Chaîne "print" — si le token ARU a été capturé après le point
             (méthode ARU() l'a déjà traduit en "print")
          3. Nom kabyle dans METHODES_KABYLES (ex: "gher", "mdel")
        """
        method_name = str(method)

        # Cas spécial : si le parseur a capturé ARU après le point, la
        # méthode ARU() du transformer l'a déjà transformé en "print".
        # On le ramène à "write" puisque dans ce contexte, f.aru = f.write.
        if method_name == "print":
            method_name = "write"
        elif method_name in self.METHODES_KABYLES:
            method_name = self.METHODES_KABYLES[method_name]

        if rest:
            return f"{obj}.{method_name}({rest[0]})"
        return f"{obj}.{method_name}()"

    # ── Appel de fonction ─────────────────────────────────────────────────────
    # call_expr: (NAME | ARU) "(" [arguments] ")"
    # On reçoit :
    #   - 1 arg  : (fname,)            → appel sans arguments
    #   - 2 args : (fname, args_str)   → appel avec arguments
    # fname peut être un Token NAME ou déjà la chaîne "print" (si c'était ARU
    # et que la méthode ARU l'a transformé).

    def call_expr(self, name, *args) -> str:
        func_name = KEYWORDS_KABYLE_TO_PYTHON.get(str(name), str(name))
        args_str = ", ".join(str(a) for a in args)
        return f"{func_name}({args_str})"

    def arguments(self, *args) -> str:
        return ", ".join(str(a) for a in args)

    def pos_arg(self, e) -> str:
        return str(e)

    def keyword_arg(self, key, val) -> str:
        return f"{key}={val}"

    # ── Tokens terminaux : NAME reste tel quel ───────────────────────────────

    def NAME(self, token) -> str:
        return str(token)

    # ── Tokens "de valeur / opérateur" conservés dans l'arbre ────────────────
    # Chacun retourne son équivalent Python. Ces méthodes sont appelées
    # automatiquement par Lark lors de la remontée du transformer.

    def IH(self, _):    return "True"
    def ALA(self, _):   return "False"
    def AKKED(self, _): return "and"
    def NEGH(self, _):  return "or"
    def MACCI(self, _): return "not"
    def ARU(self, _):   return "print"
    def SEQSI(self, _): return "input"
    def ELDI(self, _):  return "open"
    def AMNAR(self, _): return "range"
    def TEGHZ(self, _): return "len"
    def SSENF(self, _): return "type"
    def UTTU(self, _):  return "int"
    def AWAL(self, _):  return "str"
    def TABDART(self, _): return "list"
    def AMEQQRAN(self, _): return "max"
    def AMECTUH(self, _): return "min"
    def RNU(self, _):   return "sum"
    def FAKK(self, _):  return "quit"


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — FONCTIONS PUBLIQUES
# ══════════════════════════════════════════════════════════════════════════════

def transpile(code_kabyle: str) -> str:
    """
    Transpile du code Kabyle en code Python valide.

    Args:
        code_kabyle: Chaîne contenant le programme kabyle.

    Returns:
        Chaîne contenant le code Python équivalent.

    Raises:
        lark.exceptions.UnexpectedInput en cas d'erreur de syntaxe.
    """
    # L'Indenter a besoin d'un retour à la ligne final pour fermer
    # correctement les derniers DEDENT.
    if not code_kabyle.endswith("\n"):
        code_kabyle = code_kabyle + "\n"

    parser      = get_parser()
    tree        = parser.parse(code_kabyle)
    transformer = TreeToPython()
    python_code = transformer.transform(tree)
    return str(python_code)


def run(code_kabyle: str, verbose: bool = False) -> None:
    """
    Transpile le code Kabyle puis l'exécute via exec().

    Args:
        code_kabyle : Le programme kabyle à exécuter.
        verbose     : Si True, affiche le code Python généré avant exécution.
    """
    python_code = transpile(code_kabyle)

    if verbose:
        sep = "─" * 60
        print(f"\n{sep}\nCODE KABYLE :\n{sep}")
        print(code_kabyle)
        print(f"\n{sep}\nCODE PYTHON GENERE :\n{sep}")
        print(python_code)
        print(f"\n{sep}\nRESULTAT D'EXECUTION :\n{sep}")

    # Namespace isolé pour l'exécution
    namespace: dict = {"__builtins__": __builtins__}
    exec(python_code, namespace)


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — CLI (Interface en ligne de commande)
# ══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Point d'entrée CLI.

    Usage :
        python ameskar.py programme.kbl           # exécute le fichier
        python ameskar.py programme.kbl --show    # + affiche le code généré
        python ameskar.py -t programme.kbl        # transpile seulement
    """
    import argparse

    parser_cli = argparse.ArgumentParser(
        prog="ameskar",
        description="Transpilateur Kabyle -> Python v1.0",
    )
    parser_cli.add_argument(
        "fichier",
        help="Fichier source kabyle (.kbl) a transpiler/executer",
    )
    parser_cli.add_argument(
        "--show", "-s",
        action="store_true",
        help="Affiche le code kabyle et le Python genere avant execution",
    )
    parser_cli.add_argument(
        "--transpile-only", "-t",
        action="store_true",
        dest="transpile_only",
        help="Affiche uniquement le code Python sans l'executer",
    )

    args = parser_cli.parse_args()

    source_path = Path(args.fichier)
    if not source_path.exists():
        print(f"Erreur : fichier introuvable -- {source_path}", file=sys.stderr)
        sys.exit(1)

    code_kabyle = source_path.read_text(encoding="utf-8")

    try:
        if args.transpile_only:
            print(transpile(code_kabyle))
        else:
            run(code_kabyle, verbose=args.show)
    except Exception as e:
        print(f"Erreur : {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
