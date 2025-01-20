from pokefiche import request_data, request_cached_data
from md_to_html import convert
import sys
import os
import json
import matplotlib.pyplot as plt
from md_to_html import convert
import requests


def find_multiple_matches(name: str, data: dict) -> tuple:
    """
    Scanne chaque élément du cache jusqu'à trouver le nom
    correspondant à l'entrée utilisateur et renvoie l'url. Si aucun résultat exact n'est trouvé,
    un dictionnaire de tous les résultats ainsi que les urls est renvoyé.
    La fonction renvoie un tuple qui contient ce dictionnaire et un mot clé correspondant à
    l'état des résultats par rapport à l'entrée utilisateur (unknown, full et partial).

    - name : Entrée utilisateur [str]
    - data : Le fichier contenant tous les lieux [dict]
    """
    matches = {"results": [], "urls": []}
    count = data['count']

    for i in range(count):
        if name == data['results'][i]['name']:
            return ("full", data['results'][i]['url'])
        elif name in data['results'][i]['name']:
            matches['results'].append(data['results'][i]['name'])
            matches['urls'].append(data['results'][i]['url'])
    
    if not matches['results']:
        return "unknown", ""
    else:
        return ("partial", matches)

def get_pkmn_types(data: dict) -> list:
    """
    Récupère les types du Pokémon en français.

    - data : Données du Pokémon [dict]
    """    
    en_types = []
    fr_types = []
    url_types = ""

    for i in range(len(data['types'])):
        """current_type = data['types'][i]['type']['name']
        current_url = data['types'][i]['type']['url']
        pkmn_types = request_cached_data(current_url, f"type-{en_types[i]}.json", verbose=verbose_value)
        types_dict[current_type] = pkmn_types['names'][3]['name']"""

        en_types.append(data['types'][i]['type']['name'])
        url_types = data['types'][i]['type']['url']
        pkmn_types = request_cached_data(url_types, f"type-{en_types[i]}.json", verbose=verbose_value)

        fr_types.append(pkmn_types['names'][3]['name'])

    return fr_types

def get_pkmn_sprite(data: dict) -> str:
    """
    Récupère l'url du sprite du Pokémon.
    
    - data : Données du Pokémon [str]
    """
    return data['sprites']['other']['official-artwork']['front_default']

def get_pkmn_stats(data: dict) -> dict:
    """
    Affiche chaque stat d'un Pokémon en français.
    
    - data : Données du Pokémon [str]
    """
    stats_dict = {}

    for i in range(6):
        
        stat_value = data['stats'][i]['base_stat']
        en_stat_name = data['stats'][i]['stat']['name']
        
        url = data['stats'][i]['stat']['url']
        stat = request_cached_data(url, f"stat-{en_stat_name}.json", verbose=verbose_value)
        fr_stat_name = stat['names'][3]['name']

        # if en_stat_name not in stats_dict:      Initialisation du dictionnaire
        stats_dict[en_stat_name] = {'fr_name': "", 'stat_value': 0}

        stats_dict[en_stat_name]['fr_name'] = fr_stat_name
        stats_dict[en_stat_name]['stat_value'] = stat_value
        
        # print(f"{fr_stat_name} : {stat_value}")
    
    return stats_dict

def get_pkmn_name(data: dict) -> str:
    """
    Récupère le nom français d'un Pokémon.
    
    - data : données du Pokémon [dict]
    """
    en_name = data['name']
    url = data['species']['url']
    pkmn = request_cached_data(url, f"{en_name}-species.json", verbose=verbose_value)   # On fait une requête vers l'espèce pour
    fr_name = pkmn['names'][4]['name']                              # obtenir des données avancées -> la traduction en fr
                                                                    # du nom du Pokémon
    return fr_name

def get_area_name(data: dict) -> str:
    """
    Récupère le nom d'un lieu en français.
    L'emplacement du nom français peut varier et ne pas exister donc on veille à
    ce que dans le pire des cas, le nom anglais soit affiché.
    
    - data : données du lieu [str]
    """
    formatted_name = data['name']
    
    if len(data['names']) > 0:
        for i in range(len(data['names'])):
            if data['names'][i]['language']['name'] == "fr":
                fr_area_name = data['names'][i]['name']
                return fr_area_name
            elif data['names'][i]['language']['name'] == "en":
                en_area_name = data['names'][i]['name']
        
        return en_area_name

def get_encounter_method(data: dict, mode: str) -> str:
    """
    Récupère la méthode de rencontre du pokémon.

    - data : données du Pokémon
    - mode : Retourne le nom simple ou le nom complet en français
    """
    simple_encounter_method = data['pokemon_encounters'][0]['version_details'][-1]['encounter_details'][0]['method']['name']
    if mode == "simple":
        return simple_encounter_method
    else:
        encounter_method = request_cached_data(data['pokemon_encounters'][0]['version_details'][-1]['encounter_details'][0]['method']['url'], f"{simple_encounter_method}.json", verbose=verbose_value)

        for i in range(len(encounter_method['names'])):
            if encounter_method['names'][i]['language']['name'] == "fr":
                return encounter_method['names'][i]['name']     # Nom complet en français
            elif encounter_method['names'][i]['language']['name'] == "en":
                en_encounter_name = encounter_method['names'][i]['name']
        
        return en_encounter_name    # Si le nom complet français n'est pas trouvé, on renvoie le nom anglais

def get_dataset(name: str, root_data) -> dict:
    """
    Le fonction trouve tous les Pokémons rencontrables pour le lieu entré
    par l'utilisateur.
    Elle envoie poke_dict qui contient des noms de Pokémons, leur stats et leur méthode de rencontre.
    Ce dictionnaire est ensuite utilisé par compute_statistics(poke_dict) pour faire des statistiques.

    - name : le nom du lieu entré par l'utilisateur [str]
    - root_data : le fichier contenant le dictionnaire des lieux [dict]
    """
    formatted_place = name.replace(" ", "-").replace(".", "").lower()  # Formate le texte pour enlever les caractères génants
    place_url = find_multiple_matches(formatted_place, root_data)

    if place_url[0] == "unknown":
        print("❌ Lieu inconnu...")
        sys.exit()
    elif place_url[0] == "partial":
        
        url_count = len(place_url[1]['results'])
        print(f"📋 {url_count} Lieux trouvés\n")
        i = 1
        for name in place_url[1]['results']:  # Affichage des résultats possibles
            print(f"{i}: {name.replace('-', ' ')}")
            i += 1

        while 1:
            # Pour recommencer en cas de typo sur usr_choice (pas un entier, pas dans la plage autorisée)

            try:
                usr_choice = int(input("\n[int] Entrez le lieu souhaité : "))
            except ValueError:
                # L'entrée utilisateur n'est pas un entier
                print("\n❌ Entrez un entier")
            else:
                # Hors de la plage autorisée
                if not(1 <= usr_choice <= url_count):
                    print("\n❌ Entrée invalide")
                else:
                    # Tout va bien à bord, alors on remplace la saisie utilisateur et l'url par le lieu sélectionné
                    formatted_place = place_url[1]['results'][usr_choice-1]
                    place_url = place_url[1]['urls'][usr_choice-1]
                    break

    else:
        place_url = place_url[1]
        print("✅ Lieu trouvé !")
    print()

    # Le programme trouve le nom français et itère sur le sous-fichier pour trouver chaque zone (sous-lieu)

    place = request_cached_data(place_url, f"{formatted_place}.json", verbose=verbose_value)

    fr_place_name = get_area_name(place)
    print("==============================")
    print(fr_place_name)
    print("==============================\n")

    sub_area_list = []

    for i in range(len(place['areas'])):
        sub_area_list.append(place['areas'][i]['url'])

    # Récupère les infos sur les Pokémons en itérant sur la liste obtenue

    wait = input(f"[Entrée] Affichage des Pokémons de la zone...")
    print()

    poke_dict = {
        'pokemons': {},
        'place_info': {}
    }

    for i in range(len(place['areas'])):
        # Parcourt les sous-lieux
        sub_area_name = place['areas'][i]['name']
        sub_area_url = place['areas'][i]['url']
        sub_area = request_cached_data(sub_area_url, f"{sub_area_name}.json", verbose=verbose_value)

        for x in range(len(sub_area['pokemon_encounters'])):
            # Parcourt les pokémons rencontrables
            pkmn_name = sub_area['pokemon_encounters'][x]['pokemon']['name']
            pkmn_url = sub_area['pokemon_encounters'][x]['pokemon']['url']


            if pkmn_name not in poke_dict:
                # Si le Pokémon est déjà affiché, on l'ignore. Sinon, on l'affiche
                pkmn = request_cached_data(pkmn_url, f"{pkmn_name}.json", verbose=verbose_value)
                
                # On récupère les données

                region_name = place['region']['name']

                fr_pkmn_name = get_pkmn_name(pkmn)
                pkmn_types = get_pkmn_types(pkmn)
                pkmn_sprite = get_pkmn_sprite(pkmn)
                pkmn_encounter_simple = get_encounter_method(sub_area, "simple")
                pkmn_encounter_complete = get_encounter_method(sub_area, "complete")
                pkmn_stats = get_pkmn_stats(pkmn)
                pkmn_id = pkmn['id']

                poke_dict[pkmn_name] = {}

                # On affiche les données récupérées à l'utilisateur dans le terminal

                print(f"▶ {fr_pkmn_name}")
                print(pkmn_encounter_complete)
                print(f"Type(s) : ", end="")
                for _type in pkmn_types:
                    print(_type, end=" ")   # Pour que les types s'affichent sur une seule ligne (avec un espace)
                print()     # Pour sauter une ligne car les print précédents ne retournent pas à la ligne

                # On ajoute les données à poke_dict pour pouvoir les traiter par la suite

                poke_dict['place_info'] = [fr_place_name, region_name]

                if pkmn_name not in poke_dict['pokemons']:
                    poke_dict['pokemons'][pkmn_name] = {}
                
                poke_dict['pokemons'][pkmn_name]['id'] = pkmn_id
                poke_dict['pokemons'][pkmn_name]['fr_name'] = fr_pkmn_name
                poke_dict['pokemons'][pkmn_name]['types'] = pkmn_types
                poke_dict['pokemons'][pkmn_name]['sprite'] = pkmn_sprite
                poke_dict['pokemons'][pkmn_name]['encounter'] = pkmn_encounter_complete
                for stat_name, stat_data in pkmn_stats.items():
                    poke_dict['pokemons'][pkmn_name][stat_data['fr_name']] = stat_data['stat_value']
                    print(f"{stat_data['fr_name']} : {stat_data['stat_value']}")

                print("------------------------------")    # Séparateur

    print("\n✅ Recherche terminée !")
    if len(poke_dict['pokemons']) == 0:
        print(f"\n⚠️  Aucun Pokémon trouvé pour ce lieu.")
    else:
        print(f"\n{len(poke_dict['pokemons'])} Pokémons trouvés pour ce lieu.")
    
    return poke_dict

def compute_statistics(poke_dict: dict, filename: str) -> None:
    """
    Calcule des statistiques sur les Pokémon.

    - poke_dict : dictionnaire données Pokémon [dict]
    - filename : nom du fichier diagramme généré [str]
    """

    types_sorted = {
        'Insecte': 0,
        'Ténèbres': 0,
        'Dragon': 0,
        'Elektrik': 0,
        'Fée': 0,
        'Combat': 0,
        'Feu': 0,
        'Vol': 0,
        'Spectre': 0,
        'Plante': 0,
        'Sol': 0,
        'Glace': 0,
        'Normal': 0,
        'Poison': 0,
        'Psy': 0,
        'Roche': 0,
        'Acier': 0,
        'Eau': 0,
    }

    # Couleurs pour le diagramme circulaire
    color_map = {
    'Insecte': '#a8b820',  # Vert olive
    'Ténèbres': '#403934',  # Marron sombre (pâle)
    'Dragon': '#7038f8',  # Violet
    'Électrik': '#f8d030',  # Jaune
    'Fée': '#ee99ac',  # Rose clair
    'Combat': '#c03028',  # Maroon 
    'Feu': '#f08030',  # Orange
    'Vol': '#a890f0',  # Violet clair
    'Spectre': '#705898',  # Violet pâle
    'Plante': '#78C850',  # Vert
    'Sol': '#e0c068',  # Ocre
    'Glace': '#98d8d8',  # Bleu clair
    'Normal': '#b3b391',  # Beige
    'Poison': '#a040a0',  # Fuschia
    'Psy': '#f85888',  # Rose
    'Roche': '#b8a038',  # Marron clair
    'Acier': '#b8b8d0',  # Gris
    'Eau': '#6890f0'   # Bleu
    }
    
    for key, value in poke_dict['pokemons'].items():
    # Vérifier que 'types' existe dans l'entrée actuelle
        if 'types' in value and isinstance(value['types'], list):
            for type_ in value['types']:
                if type_ in types_sorted:
                    types_sorted[type_] += 1
                else:
                    # Si le type n'est pas dans types_sorted, l'initialiser à 1
                    types_sorted[type_] = 1

    # Création du diagramme circulaire présentant la répartition des types :

    filtered_types = {}
    for type_, value in types_sorted.items():   # Pour éliminer les types ayant un indice à 0 du diagramme
        if value > 0:
            filtered_types[type_] = value

    labels = list(filtered_types.keys())
    sizes = list(filtered_types.values())
    colors = [color_map[type_name] for type_name in labels]

    plt.figure(figsize=(7, 7))
    plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=45)

    plt.title("")
    plt.show
    plt.savefig(f'./pokestats/{filename}', dpi=300, bbox_inches='tight')


def dataset_to_md(poke_dict: dict, filename: str, diagram_name: str) -> None:
    """
    Génère un fichier Markdown pour les statistiques de répartition de types.
    
    - filename : nom du fichier Markdown [str]
    - poke_dict : toutes les données utiles [dict]
    - diagram_name : le nom du fichier diagramme [str]
    """

    with open(filename, 'w', encoding="utf-8") as md:
        md.write('# PokéRadar - PokéStats\n\n')
        md.write('\n[SAE 15] DAIRIN Côme | SCHER Florian\n\n')
        md.write(f'# {poke_dict['place_info'][0]}\n\n')
        md.write(f'### - Région : {poke_dict['place_info'][1].capitalize()}\n\n')
        md.write('## Pokémons capturables\n\n')
                
        for key, value in poke_dict['pokemons'].items():
            types_str = " ".join(poke_dict['pokemons'][key]['types'])
            
            md.write(f'### ▶ [{poke_dict['pokemons'][key]['id']}] {poke_dict['pokemons'][key]['fr_name']} :\n')
            md.write(f'| Pokémon | Type | PV | Attaque | Défense | Attaque Spé. | Défense Spé. | Vitesse | Capture |\n')
            md.write(f'| :-: | :-: | :-: | :-: | :-: | :-: | :-: | :-: | -: |\n')
            md.write(f"| <img src={poke_dict['pokemons'][key]['sprite']} width='100px'> | {types_str} | {poke_dict['pokemons'][key]['PV']} | {poke_dict['pokemons'][key]['Attaque']} | {poke_dict['pokemons'][key]['Défense']} | {poke_dict['pokemons'][key]['Attaque Spéciale']} | {poke_dict['pokemons'][key]['Défense Spéciale']} | {poke_dict['pokemons'][key]['Vitesse']} | {poke_dict['pokemons'][key]['encounter']} |\n\n")
        
        md.write('## Répartition des types\n\n')
        md.write(f"<img src='{diagram_name}' width='400px'>")
        

def infos_locales(en_place_name: str) -> None:
    """
    Génère un fichier Markdown et HTML des statistiques.

    - en_place_name : nom du lieu en anglais [str]
    """
    try:
        os.mkdir("cache")       # On crée le répertoire cache
        if verbose_value==True:
            print("Création du répertoire : cache")
    except FileExistsError:     # S'il existe déjà, on ignore l'erreur
        pass
    except PermissionError:
        print(f"❌  Permission non accordée. Ne peut pas créer le cache.\n")
    # On crée le répertoie pokestats
    try:
        os.mkdir("pokestats")
        if verbose_value==True:
            print("Création du répertoire : pokestats")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"❌ Erreur : permission non accordée. Ne peut pas créer le dossier pokefiche.")

    root_data = request_cached_data("https://pokeapi.co/api/v2/location/", "root_place_file.json", 9999, verbose=verbose_value)     # Dictionnaire des lieux
    poke_dict = get_dataset(en_place_name, root_data)

    stats = compute_statistics(poke_dict, f"diagram-{en_place_name.replace(" ", "_")}.png")
    diagram_name = f'diagram-{en_place_name.replace(" ", "_")}.png'
    md_filename, html_filename = f'{en_place_name.replace(" ", "_")}.md', f'{en_place_name.replace(" ", "_")}.html'
    
    dataset_to_md(poke_dict, f"./pokestats/{md_filename}", diagram_name)
    print(f"\nStatistiques générées : {md_filename}")
    convert( f"./pokestats/{md_filename}",  f"./pokestats/{html_filename}")
    print(f"Statistiques générées : {html_filename}\n")

if __name__ == "__main__":
    global verbose_value
    print(
"""
 __   __        ___  __   __   __   __   __  
|__) /  \\ |__/ |__  |__) |__| |  \\ |__| |__) 
|    \\__/ |  \\ |___ |  \\ |  | |__/ |  | |  \\
"""
    )

    print(r"\\\\\\\\\\\\\\\\\\\\\\ PokéRadar v1.0 Part 1")
    print("---------------------- SAE 15 [2.2]")
    print("////////////////////// Côme et Florian\n")

    print('Utilisation : python3 stats.py --verbose=[y|n] <pokemon_place>\n')

    place = " ".join(sys.argv[2:])      # On doit convertir tous les arguments après --verbose=[y|n] pour
                                        # obtenir le nom du lieu recherché
    if "--verbose=y" in sys.argv[1]:
        verbose_value = True
        try:
            infos_locales(place)
        except requests.exceptions.ConnectionError:
            print("❌ Connexion refusée.\n")
        except requests.exceptions.HTTPError:
            print("❌ La requête est invalide.\n")
        except requests.exceptions.Timeout:
            print("❌ La requête a expiré.\n")
        except json.decoder.JSONDecodeError:
            print("❌ Une erreur est survenue.\n")
            print("> Essayez de vider le cache\n")
    elif "--verbose=n" in sys.argv[1]:
        verbose_value = False
        try:
            infos_locales(place)
        except requests.exceptions.ConnectionError:
            print("❌ Connexion refusée.\n")
        except requests.exceptions.HTTPError:
            print("❌ La requête est invalide.\n")
        except requests.exceptions.Timeout:
            print("❌ La requête a expiré.\n")
        except json.decoder.JSONDecodeError:
            print("❌ Une erreur est survenue.\n")
            print("> Essayez de vider le cache\n")
    else:
        print(f'❌ Erreur : argument inattendu "{sys.argv[1]}"\n\nUtilisation : python3 stats.py --verbose=[y|n] <pokemon_place>\n')
