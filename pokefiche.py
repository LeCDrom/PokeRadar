import requests
from md_to_html import convert
import json
import sys
import os


def request_data(url: str, limit: int=0, offset: int=0) -> dict:
    """
    Fait une requête simple vers l'API.
    Retourne les données récupérées au format json.

    - url : url vers la requête [str]
    - limit : limite d'affichage d'éléments [int]
    - offset : décalage de la requête [int]
    """
    url = f"{url}?limit={limit}?offset={offset}"
    
    response = requests.get(url)
    data = response.json()
    return data

def request_cached_data(url: str, filename: str, limit: int=0, offset: int=0, verbose: bool=False) -> dict:
    """
    Met en cache les données si elles ne y sont pas présentes.
    
    - url : url vers la requête [str]
    - filename : nom du fichier cache [str]
    - limit : limite d'affichage d'éléments [int]
    - offset : décalage de la requête [int]
    - verbose : affichage des informations debug sur la création des caches [bool]
    """
    if os.path.isfile(f'cache/{filename}'):
        # Si le cache est présent on charge les données
        if verbose == True:
            print(f"Récupération du cache : {filename}")
        with open(f'cache/{filename}', "r") as f:
            file_content = json.load(f)
        return file_content

    elif not os.path.isfile(f'cache/{filename}'):
        # Si le cache n'existe pas on le crée
        if verbose == True:
            print(f"Création du cache : {filename}")
        data = request_data(url, limit, offset)
        with open(f'cache/{filename}', "w") as f:
            file_content = json.dump(data, f)
        return data

def download_poke(id: int, filename: str) -> dict:
    """
    Récupère les données du Pokémon et les met en cache si besoin.

    - id : n° id du Pokémon [int]
    - filename : nom du fichier cache [str]
    """
    return request_cached_data(f"https://pokeapi.co/api/v2/pokemon/{id}", filename, verbose=verbose_value)

def get_poke_dict(data: dict) -> dict:
    """
    Récupère toutes les données du Pokémon servant à faire la Pokéfiche.
    Retourne le poke_dict.
    
    - data : données de la requête pkmn [dict]
    """
    poke_dict = {
        'fr_name': "",
        'sprite': {
            'static': {
                'normal': "",
                'shiny': ""
            },
            'anim': {
                'normal': "",
                'shiny': ""
            }
        },
        'POKEDEX': {
            'id': 0,
            'description': "",
            'types': [],
            'species': "",
            'height': 0,
            'weight': 0
        },
        'STATS': {
            'Total': 0
        },
        'ABILITIES': {
            'normal': {},
            'hidden': {},
        },
        'OTHER': {
            'habitat': "",
            'capt_rate': 0,
            'happiness': 0
        }
    }

    # Nom français :

    en_name = data['name']
    url = data['species']['url']
    data_species = request_cached_data(url, f"{en_name}-species.json", verbose=verbose_value)
    fr_name = data_species['names'][4]['name']
    poke_dict['fr_name'] = fr_name

    # Sprites :

    static_normal = data['sprites']['other']['official-artwork']['front_default']
    static_shiny = data['sprites']['other']['official-artwork']['front_shiny']
    if not data['sprites']['versions']['generation-v']['black-white']['animated']['front_default']:      # S'il n'existe aucun sprite de black & white,
        anim_normal = data['sprites']['front_default']                                      # on récupère les seconds sprites le plus simplement possible
        anim_shiny = data['sprites']['front_shiny']
    else:
        anim_normal = data['sprites']['versions']['generation-v']['black-white']['animated']['front_default']
        anim_shiny = data['sprites']['versions']['generation-v']['black-white']['animated']['front_shiny']
    poke_dict['sprite']['static']['normal'] = static_normal
    poke_dict['sprite']['static']['shiny'] = static_shiny
    poke_dict['sprite']['anim']['normal'] = anim_normal
    poke_dict['sprite']['anim']['shiny'] = anim_shiny

    # ID Pokémon :

    poke_dict['POKEDEX']['id'] = data['id']

    # Types :

    en_types = []
    fr_types = []
    url_types = ""

    for i in range(len(data['types'])):
        en_types.append(data['types'][i]['type']['name'])
        url_types = data['types'][i]['type']['url']
        pkmn_types = request_cached_data(url_types, f"type-{en_types[i]}.json", verbose=verbose_value)

        fr_types.append(pkmn_types['names'][3]['name'])
    
    poke_dict['POKEDEX']['types'] = fr_types

    # Espèce :

    url = data['species']['url']
    data_species =  request_cached_data(url, f"{en_name}-species.json", verbose=verbose_value)
    species = data_species['genera'][3]['genus']
    poke_dict['POKEDEX']['species'] = species

    # Description :

    for flavor_text_entry in reversed(data_species['flavor_text_entries']):       # On part de la dernière version et on récupère la description qui correspond au fr
        if flavor_text_entry['language']['name'] == 'fr':
            description = flavor_text_entry['flavor_text'].replace("\n", " ")
            break
    
    try:
        poke_dict['POKEDEX']['description'] = description
    except UnboundLocalError:
        poke_dict['POKEDEX']['description'] = "???"

    # Taille et poids :

    poke_dict['POKEDEX']['height'] = data['height'] / 100       # Divisé par 100 car affiché en décimètres
    poke_dict['POKEDEX']['weight'] = data['weight'] / 100       # Divisé par 100 car affiché en décigrammes

    # Stats de base et calcul total (somme) :

    for i in range(len(data['stats'])):
        
        stat_value = data['stats'][i]['base_stat']
        en_stat_name = data['stats'][i]['stat']['name']
        
        url = data['stats'][i]['stat']['url']
        stat = request_cached_data(url, f"stat-{en_stat_name}.json", verbose=verbose_value)
        fr_stat_name = stat['names'][3]['name']

        poke_dict['STATS'][fr_stat_name] = stat_value

        poke_dict['STATS']['Total'] += stat_value
    
    # Talents :

    for i in range(len(data['abilities'])):
        current_ability_name = data['abilities'][i]['ability']['name']
        current_ability = request_cached_data(data['abilities'][i]['ability']['url'], f"ability-{current_ability_name}.json", verbose=verbose_value)
        
        current_ability_fr_name = current_ability['names'][3]['name']
        
        for flavor_text_entry in reversed(current_ability['flavor_text_entries']):       # On part de la dernière version et on récupère la description qui correspond au fr
            if flavor_text_entry['language']['name'] == 'fr':
                # Enlever sauts de ligne ou \\n
                current_ability_descript = flavor_text_entry['flavor_text'].replace("\n", " ").replace("\\n", " ")
                break
        
        if data['abilities'][i]['is_hidden']:
            poke_dict['ABILITIES']['hidden'][current_ability_fr_name] = current_ability_descript
        else:
            poke_dict['ABILITIES']['normal'][current_ability_fr_name] = current_ability_descript
        
    # Autres (habitat, taux de capture, joie par défaut)

    try:
        data_habitat = request_cached_data(data_species['habitat']['url'], f"habitat-{data_species['habitat']['name']}.json", verbose=verbose_value)
        habitat = data_habitat['names'][0]['name']
    except TypeError:
        habitat = "???"
    except Exception:
        habitat = "???"
    capt_rate = data_species['capture_rate']
    base_happiness = data_species['base_happiness']

    poke_dict['OTHER']['habitat'] = habitat
    poke_dict['OTHER']['capt_rate'] = capt_rate
    poke_dict['OTHER']['happiness'] = base_happiness

    return poke_dict


def poke_to_md(poke_dict: dict, filename: str) -> None:
    """
    Génère la pokéfiche au format Markdown.
    
    - poke_dict : données Pokémon [dict]
    - filename : nom du fichier Markdown [str]
    """

    inline_types = ""
    for type_ in poke_dict['POKEDEX']['types']:     # Pour afficher les types sous forme de str (ex: Eau Poison)
        inline_types += f"{type_} "

    with open(filename, 'w', encoding="utf-8") as md:
        # Utilise poke_dict pour ajouter chaque information intéressante
        md.write('# PokéRadar - PokéFiche\n\n')
        md.write('\n[SAE 15] DAIRIN Côme | SCHER Florian\n\n')
        md.write(f'# No. {poke_dict['POKEDEX']['id']} • {poke_dict['fr_name']}\n\n')
        md.write('| Normal | Chromatique |\n')
        md.write('| :-: | :-: |\n')
        md.write(f'| <img src={poke_dict['sprite']['static']['normal']} width="250px"> | <img src={poke_dict['sprite']['static']['shiny']} width="250px"> |\n')
        md.write(f'| <img src={poke_dict['sprite']['anim']['normal']} height="150px"> | <img src={poke_dict['sprite']['anim']['shiny']} height="150px"> |\n\n')
        md.write('## Entrée Pokédex :\n\n')
        md.write(f'### \"{poke_dict['POKEDEX']['description']}\"\n\n')
        md.write(f'- ID : {poke_dict['POKEDEX']['id']}\n')
        md.write(f'- Type(s) : {inline_types}\n')
        md.write(f'- Espèce : {poke_dict['POKEDEX']['species']}\n')
        md.write(f'- Taille : {poke_dict['POKEDEX']['height']}m\n')
        md.write(f'- Poids : {poke_dict['POKEDEX']['weight']}kg\n')
        md.write('## Statistiques de base :\n\n')
        for key, value in poke_dict['STATS'].items():
            if key != "Total":
                md.write(f'- {key} : {value}\n')
        md.write(f"- **Total : {poke_dict['STATS']['Total']}**\n\n")
        md.write(f'\n## Talents Pokémon :\n\n')
        for normal_ability, description in poke_dict['ABILITIES']['normal'].items():     # Affiche tous les talents normaux sous forme de liste
            md.write(f'- {normal_ability} : {description}\n')
        for hidden_ability, description in poke_dict['ABILITIES']['hidden'].items():     # Affiche tous les talents cachés sous forme de liste
            md.write(f'- **{hidden_ability} : {description}** ***[Caché]***\n')
        md.write('\n## Autres informations :\n\n')
        md.write(f'- Habitat : {poke_dict['OTHER']['habitat'].capitalize()}\n')
        md.write(f'- Indice de capture *(0-255)* : {poke_dict['OTHER']['capt_rate']}\n')
        md.write(f'- Indice de Joie *(0-255)*: {poke_dict['OTHER']['happiness']}\n\n')

def fiche_pokemon(id: int) -> None:
    """
    Génère la fiche pokémon complète.
    Les fiches se situent dans le dossier pokefiche.

    - id : Numéro id du pokémon recherché [int]
    """
    # On crée le répertoire cache
    try:
        os.mkdir("cache")
        if verbose_value==True:
            print("Création du répertoire : cache")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"❌ Erreur : permission non accordée. Ne peut pas créer le cache.")
    # On crée le répertoie pokefiche
    try:
        os.mkdir("pokefiche")
        if verbose_value==True:
            print("Création du répertoire : pokefiche")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"❌ Erreur : permission non accordée. Ne peut pas créer le dossier pokefiche.")

    root_pkmn_file = request_cached_data("https://pokeapi.co/api/v2/pokemon", "root_pkmn.json", 9999, verbose=verbose_value)   # Récupération du fichier contenant tous les Pokémons
    print("Génération de la Pokéfiche en cours...")

    pkmn_name = root_pkmn_file['results'][id-1]['name']
    data = download_poke(id, f"{pkmn_name}.json")       # Récupération des données de base sur le Pokémon
    poke_dict = get_poke_dict(data)                     # Récupération des données poke_dict

    md_filename = f"pokefiche_{pkmn_name}.md"
    html_filename = f"pokefiche_{pkmn_name}.html"
    poke_to_md(poke_dict, f"./pokefiche/{md_filename}")
    print(f"\nFiche générée : {md_filename}")
    convert(f"./pokefiche/{md_filename}", f"./pokefiche/{html_filename}")
    print(f"Fiche générée : {html_filename}\n")


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

    print('Utilisation : python3 pokefiche.py --verbose=[y|n] <pokemon_id>\n')

    if "--verbose=y" == sys.argv[1]:
        verbose_value = True
        try:
            fiche_pokemon(int(sys.argv[2]))
        except requests.exceptions.ConnectionError:
            print("❌ Connexion refusée.\n")
        except requests.exceptions.HTTPError:
            print("❌ La requête est invalide.\n")
        except requests.exceptions.Timeout:
            print("❌ La requête a expiré.\n")
        except json.decoder.JSONDecodeError:
            print("❌ Une erreur est survenue.\n")
            print("> Essayez de vider le cache\n")

    elif "--verbose=n" == sys.argv[1]:
        verbose_value = False
        try:
            fiche_pokemon(int(sys.argv[2]))
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
        print(f'❌ Erreur : argument inattendu\n\nUtilisation : python3 pokefiche.py --verbose=[y|n] <pokemon_id>\n')
