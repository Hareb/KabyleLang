# KabyleLang 🌍 — Transpilateur Kabyle → Python v1.0

> Un langage de programmation éducatif pour la communauté kabyle.  
> Même logique que Python, mots-clés en kabyle.

---

## 📂 Structure du projet

```
KabyleLang/
├── kabyle.lark    # Grammaire EBNF (Lark)
├── ameskar.py     # Transpilateur principal
├── test.kbl       # Programme de démonstration
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

```bash
pip install -r requirements.txt
```

---

## 🚀 Utilisation

### Exécuter un fichier `.kbl`
```bash
python ameskar.py test.kbl
```

### Afficher le code Python généré
```bash
python ameskar.py test.kbl --show
```

### Transpiler seulement (sans exécution)
```bash
python ameskar.py test.kbl --transpile-only
```

### Utilisation en API Python
```python
from ameskar import transpile, run

code = """
bnu bonjour(nom):
    aru("Azul,", nom)

bonjour("Amayas")
"""

# Obtenir le code Python
print(transpile(code))

# Ou exécuter directement
run(code)
```

---

## 📖 Dictionnaire des mots-clés

| Kabyle     | Python    | Description           |
|------------|-----------|-----------------------|
| `aru`      | `print`   | Afficher              |
| `ma`       | `if`      | Si                    |
| `ma_ulac`  | `else`    | Sinon                 |
| `yal`      | `for`     | Boucle pour           |
| `deg`      | `in`      | Dans                  |
| `skud`     | `while`   | Tant que              |
| `bnu`      | `def`     | Définir une fonction  |
| `erred`    | `return`  | Retourner             |
| `awid`     | `import`  | Importer              |
| `Ih`       | `True`    | Vrai                  |
| `Ala`      | `False`   | Faux                  |
| `akked`    | `and`     | Et                    |
| `negh`     | `or`      | Ou                    |
| `macci`    | `not`     | Non                   |
| `seqsi`    | `input`   | Entrée utilisateur    |
| `eldi`     | `open`    | Ouvrir fichier        |
| `amnar`    | `range`   | Range                 |
| `teghzi`   | `len`     | Longueur              |
| `ssenf`    | `type`    | Type                  |
| `uttu`     | `int`     | Entier                |
| `awal`      | `str`     | Chaîne                |
| `tabdart`  | `list`    | Liste                 |
| `ameqqran` | `max`     | Maximum               |
| `amectuh`  | `min`     | Minimum               |
| `rnu`      | `sum`     | Somme                 |
| `fakk`     | `quit`    | Quitter               |
| `gher`     | `read`    | Lire (fichier)        |
| `mdel`     | `close`   | Fermer (fichier)      |
| `rnu`      | `append`  | Ajouter (liste)       |
| `kkes`     | `remove`  | Supprimer (liste)     |
| `ssegem`   | `sort`    | Trier (liste)         |
| `tti`      | `reverse` | Inverser (liste)      |
| `bdu`      | `split`   | Découper (texte)      |
| `sdukkel`  | `join`    | Joindre (texte)       |
| `beddel`   | `replace` | Remplacer (texte)     |
| `ader`     | `lower`   | Minuscules            |
| `ali`      | `upper`   | Majuscules            |

---

## ✍️ Exemple de code Kabyle

```kabyle
# Définir une fonction
bnu tafat(n):
    ma n % 2 == 0:
        erred Ih
    ma_ulac:
        erred Ala

# Boucle for
yal i deg range(5):
    aru(i)

# Boucle while
x = 10
skud x > 0:
    aru(x)
    x -= 1
```

---

## 🔧 Ajouter un nouveau mot-clé

1. **`kabyle.lark`** — Ajouter le terminal :
   ```lark
   NOUVEAU_MOT.2: "nouveau_mot"
   ```
   Et la règle de grammaire si nécessaire.

2. **`ameskar.py`** — Ajouter dans `KEYWORDS_KABYLE_TO_PYTHON` :
   ```python
   "nouveau_mot": "python_equivalent",
   ```
   Et la méthode dans `TreeToPython` si le mot a une sémantique spéciale.

---

## 🏗️ Architecture interne

```
Code Kabyle (.kbl)
       │
       ▼
  Lark Parser  ←── kabyle.lark (grammaire EBNF)
  + KabyleIndenter (gestion INDENT/DEDENT)
       │
       ▼
    AST Lark
       │
       ▼
 TreeToPython (Transformer)
       │
       ▼
  Code Python (str)
       │
       ▼
    exec()  →  Résultat
```

---

## 📝 Licence

Projet éducatif open-source — Communauté Kabyle 🌿
