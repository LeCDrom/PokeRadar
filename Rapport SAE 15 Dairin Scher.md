# Projet SAE 05 - Traitement de données

```
TP 2.2
SCHER Florian
DAIRIN Côme
```

# - PokéRadar -

## PokéFiche et Pokéstats

### ▶ Fonctionnement en front-end :

L'utilisateur rentre un ID de Pokémon selon la syntaxe suivante : ```pokefiche.py --verbose=[y|n] <id_pokemon>```  
Le programme pokefiche.py retourne une liste de Pokémons pouvant être rencontrés ainsi qu'un diagramme circulaire présentant la répartition en pourcentage de leur types dans le lieu recherché.

- L'option --verbose=y affiche les informations de debug (création des répertoires, cache, récupération du cache).
- L'option --verbose=n n'affiche pas le debug.

### ▶ Fonctionnement en back-end :

#### ▷ Bibliothèques utilisées :

- Requests — Pour les requêtes vers l'API PokéAPI
- Markdown — Pour la présentation des données en Markdown
- MatPlotLib — Pour les diagrammes
- Json — Pour la conversion de XML à Json
- OS — Pour vérifier si le cache est présent
- Sys — Pour récupérer les arguments

#### ▷ Implémentation du cache :

Les programmes stats.py et pokefiche.py utilisent la fonction ```request_cached_data(url: str, filename: str, limit: int=0, offset: int=0, verbose: bool=False) -> dict```

Cette fonction permet de faire des requêtes seulement si le cache correspondant n'existe pas. Chaque nouvelle requête est ajoutée au cache.

#### ▷ Mise en forme :

Les deux programmes utilisent la fonction ```convert(input_f: str, output_f:str, page_name: str="Converted") -> None```  
Elle permet de convertir un fichier Markdown en HTML.

La mise en forme des données se fait alors en Markdown et en HTML.  
stats.py utilise mathplotlib pour générer un diagramme circulaire.

Les deux programmes traduisent les données en Français lorsque c'est possible.

## ▶ Choix techniques et difficultés

- PokéFiche et PokéStats stockent les documents générés dans des dossiers séparés. Cela permet un accès facile aux résultats. Les deux programmes créent leurs répertoires automatiquement.
- Des try-except ont été implémentés pour mieux gérer les erreurs en affichant à l'utilisateur des informations pertinentes sur les erreurs.
- PokéStats utilise un système de recherche pour trouver le lieu correspondant à l'entrée utilisateur. Si le lieu est incomplet, le programme propose à l'utilisateur de sélectionner un lieu parmi une liste de résultats possibles.
- L'option --verbose[y|n] permet d'afficher des messages de debug pour mieux suivre l'exécution du programme et les accès au cache.
- L'API est incomplet par rapport à certaines données les plus récentes. Pour cette raison, la traduction de certains éléments a été volontairement omise car manquante.
- Certains Pokémons ont des données inexistantes. C'est le cas pour les Pokémons légendaires qui n'ont généralement pas d'habitat ou les Ultra-Chimères qui n'ont pas de description. Les valeurs sont alors remplacées par "???" quand nécéssaire.
- Les deux programmes créent leurs répertoires automatiquement et y stockent les fichiers en sortie.
- Les documents générés contiennent une balise HTML de style pour changer la police de texte. Les tableaux sont également centrés et une marge a été ajoutée pour façiliter la lecture.