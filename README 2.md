Voici un `README.md` complet, structuré professionnellement pour GitHub. Il met en valeur à la fois l'aspect symbolique (pour ta communauté) et l'aspect technique poussé (AST, Transpilation) pour les recruteurs.

***

# ⴰⵎⴻⵙⴽⴰⵔ - KabyleLang ⵣ
> **Le premier langage de programmation complet écrit en Kabyle.**

KabyleLang n'est pas un simple script de "Chercher/Remplacer". C'est un véritable **langage éducatif transpilé**, doté de sa propre grammaire EBNF, d'un analyseur lexical/syntaxique complet (AST) et d'un moteur d'exécution basé sur Python. 

Il a été conçu avec un double objectif :
1. **Éducatif** : Permettre aux jeunes Kabyles d'apprendre la logique algorithmique sans la barrière de la langue anglaise.
2. **Identitaire et Symbolique** : Démontrer que le lexique informatique kabyle (basé sur l'Amawal) est parfaitement adapté aux sciences dures et à l'ingénierie logicielle moderne.

***

## 🛠️ Architecture Technique
Sous le capot, KabyleLang fonctionne grâce à un pipeline de compilation en 3 étapes :
1. **Lexing / Parsing** : Utilisation de la librairie `Lark` avec une grammaire EBNF stricte (gestion native de l'indentation et support des caractères latins amazighs étendus).
2. **Transformation AST** : Parcours de l'Arbre Syntaxique Abstrait et traduction sémantique (via une classe Transformer) des concepts algorithmiques.
3. **Exécution dynamique** : Injection des variables globales traduites et appel de la fonction `exec()` dans un namespace Python isolé.

***

## 📝 Syntaxe et Lexique

Le langage est conçu pour être Turing-complet, minimaliste et immédiatement lisible. L'indentation suit les mêmes règles strictes que Python.

### 1. Variables et Types de données
```kabyle
x = 10                  # uṭṭun (int)
y = 3.14                # amur (float)
isem = "Arezki"         # awal (string)
hemlaghk = Ih             # tidet (booléen : Ih / Ala)
arraw = [1, 2, 3]        # tabdart (liste)
```

### 2. Logique Conditionnelle
L'opérateur de négation s'écrit `macci`, et les opérateurs logiques sont `akked` (and) et `negh` (or).
```kabyle
ma x > 5 akked y < 10:
    aru("X est grand")
ma_ulac:
    aru("X est petit")
```

### 3. Boucles et Itérations
L'utilisation de `yal ... deg` se traduit littéralement par "Chaque ... dans", offrant une lecture très naturelle de l'algorithme.
```kabyle
# Boucle For
yal i deg amnar(5):     # amnar = range()
    aru(i)

# Boucle While avec Break/Continue
skud Ih:                # skud = while
    hbes                # hbes = break
    kemmel              # kemmel = continue
```

### 4. Fonctions
```kabyle
bnu rnu_sin(a, b):      # bnu = def
    erred a + b         # erred = return
```

### 5. Gestion des Fichiers et Exceptions
```kabyle
jerreb:                 # jerreb = try
    afaylu = eldi("data.txt", "w")
    afaylu.aru("Azul!") # Les méthodes objets sont traduites (write)
    afaylu.mdel()
slek:                   # slek = except
    aru("Tuccḍa !")
```

***

## 📚 Dictionnaire des fonctions intégrées (Built-ins)

| Action | Mot-clé Kabyle | Python équivalent |
| :--- | :--- | :--- |
| Afficher | `aru()` | `print()` |
| Saisir | `seqsi()` | `input()` |
| Taille / Longueur | `teghzi()` | `len()` |
| Type | `ssenf()` | `type()` |
| Liste | `tabdart()` | `list()` |
| Dictionnaire | `amawal()` | `dict()` |
| Maximum / Minimum | `ameqqran()` / `amectuh()` | `max()` / `min()` |
| Arrondir | `qerreb()` | `round()` |
| Valeur absolue | `azal()` | `abs()` |
| Quitter | `fakk()` | `quit()` |

***

## 🚀 Installation et Utilisation

### Option 1 : Utilisation directe (Développeurs)
1. Clonez ce dépôt.
2. Installez le parseur : `pip install lark`
3. Exécutez un script : 
```bash
python ameskar.py programme.kbl
```
*Astuce : Utilisez le flag `--show` pour voir le code Python transpilé généré en arrière-plan.*

### Option 2 : Exécutable Autonome (Windows)
Pour les écoles ou les utilisateurs non-techniques, téléchargez simplement **`KabyleLang.exe`** dans la section "Releases". Aucune installation de Python requise !
```cmd
KabyleLang.exe mon_script.kbl
```

***

## 🎨 Coloration Syntaxique (VS Code)
Pour une expérience d'écriture optimale, une extension Visual Studio Code est fournie. 
1. Copiez le dossier `vscode-extension` dans `%USERPROFILE%\.vscode\extensions\kabyle-lang`.
2. Redémarrez VS Code. Vos fichiers `.kbl` seront désormais colorés professionnellement.

***

## 🤝 Contribution
Ce projet est open-source et ouvert aux contributions de la communauté (linguistes pour l'Amawal, ou développeurs pour l'ajout de fonctionnalités logiques). 
*Tudert i tmaziɣt !*

***
