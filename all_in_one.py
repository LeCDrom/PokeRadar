import requests
import markdown
import json
import os
import matplotlib.pyplot as plt


def get_dataset(url: str, limit: int) -> dict:
    """
    Fait une requête vers l'API. Retourne les données récupérées au format json.

    - url : url vers la requête [str]
    - limit : limite d'affichage d'éléments [int]
    """
    url = f"{url}?limit={limit}"
    response = requests.get(url)
    data = response.json()
    return data


def get_data_cached(url: str, limit: int, name: str) -> dict:
    """
    Met en cache les données si elles ne sont pas dans le cache.
    
    - url : url vers la requête [str]
    - limit : limite d'affichage d'éléments [int]
    - name : nom du fichier cache [str]
    """
    if os.path.isfile(f'cache/{name}'):
        # Si le cache est présent on charge les données
        with open(f'cache/{name}', "r") as f:
            file_content = json.load(f)
        f.close()
        return file_content

    elif not os.path.isfile(f'cache/{name}'):
        # Si le cache n'existe pas on le crée
        data = get_dataset(url, limit)
        with open(f'cache/{name}', "w") as f:
            file_content = json.dump(data, f)
        f.close()
        return data

def find_place_url(name) -> str:
    """
    Scanne chaque élément du cache jusqu'à trouver le nom
    correspondant à l'entrée utilisateur. L'url est renvoyée.

    - name : entrée utilisateur
    """
    count = root_file['count']

    for i in range(count):
        if root_file['results'][i]['name'] == name:
            return root_file['results'][i]['url']
    
    return "unknown"

def find_multiple_matches(name: str) -> tuple:
    """
    Scanne chaque élément du cache jusqu'à trouver le nom
    correspondant à l'entrée utilisateur et renvoie l'url. Si aucun résultat exact n'est trouvé,
    un dictionnaire de tous les résultats ainsi que les urls est renvoyé.
    La fonction renvoie un tuple qui contient ce dictionnaire et un mot clé correspondant à
    l'état des résultats par rapport à l'entrée utilisateur (unknown, full et partial).

    - name : entrée utilisateur
    """
    matches = {"results": [], "urls": []}
    count = root_file['count']

    for i in range(count):
        if name == root_file['results'][i]['name']:
            return ("full", root_file['results'][i]['url'])
        elif name in root_file['results'][i]['name']:
            matches['results'].append(root_file['results'][i]['name'])
            matches['urls'].append(root_file['results'][i]['url'])
    
    if not matches['results']:
        return "unknown", ""
    else:
        return ("partial", matches)

def get_encounter_method(data: dict, index: int, mode: str) -> str:
    """
    Récupère la méthode de rencontre du pokémon.

    - data : données du Pokémon
    - index : index du Pokémon dans data['pokemon_encounters']
    - mode : Retourne le nom simple ou le nom complet en français
    """
    simple_encounter_method = data['pokemon_encounters'][index]['version_details'][-1]['encounter_details'][0]['method']['name']
    if mode == "simple":
        return simple_encounter_method
    else:
        encounter_method = get_data_cached(data['pokemon_encounters'][index]['version_details'][-1]['encounter_details'][0]['method']['url'], 0, f"{simple_encounter_method}.json")

        for i in range(len(encounter_method['names'])):
            if encounter_method['names'][i]['language']['name'] == "en":
                en_encounter_name = encounter_method['names'][i]['name']
            elif encounter_method['names'][i]['language']['name'] == "fr":
                return encounter_method['names'][i]['name']     # Nom complet en français
        
        return en_encounter_name    # Si le nom complet français n'est pas trouvé, on renvoie le nom anglais

def get_pkmn_types(data: dict) -> list:
    """
    Récupère le type du Pokémon en français.
    Le cache attendu est celui du Pokémon.

    """
    en_types = []
    fr_types = []
    url_types = ""
    for i in range(len(data['types'])):
        en_types.append(data['types'][i]['type']['name'])
        url_types = data['types'][i]['type']['url']
        pkmn_types = get_data_cached(url_types, 0, f"{en_types[i]}.json")

        fr_types.append(pkmn_types['names'][3]['name'])

    return fr_types

def get_pkmn_sprite(data: dict) -> str:
    """
    Récupère l'url du sprite du Pokémon.
    Le cache attendu est celui du Pokémon.
    """
    return data['sprites']['other']['official-artwork']['front_default']

def get_pkmn_stats(data: dict) -> dict:
    """
    Affiche chaque stat d'un Pokémon en français.
    Le cache attendu est celui du Pokémon.
    """
    stats_dict = {}

    for i in range(6):
        
        stat_value = data['stats'][i]['base_stat']
        en_stat_name = data['stats'][i]['stat']['name']
        
        url = data['stats'][i]['stat']['url']
        stat = get_data_cached(url, 0, f"{en_stat_name}.json")
        fr_stat_name = stat['names'][3]['name']

        if en_stat_name not in stats_dict:      # Initialisation du dictionnaire
            stats_dict[en_stat_name] = {'fr_name': "", 'stat_value': 0}

        stats_dict[en_stat_name]['fr_name'] = fr_stat_name
        stats_dict[en_stat_name]['stat_value'] = stat_value
        
        # print(f"{fr_stat_name} : {stat_value}")
    
    return stats_dict

def get_pkmn_name(data: dict) -> str:
    """
    Récupère le nom d'un Pokémon en français.
    
    - data : données de la requête
    """
    en_name = data['name']
    url = data['species']['url']
    pkmn = get_data_cached(url, 0, f"{en_name}-species.json")
    fr_name = pkmn['names'][4]['name']

    return fr_name

def get_area_name(data: dict) -> None:
    """
    Affiche le nom d'un lieu en français.
    L'emplacement du nom français peut varier et ne pas exister donc on veille à
    ce que, dans le pire des cas, le nom anglais soit affiché.
    
    - data : données de la requête
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
    
    return formatted_name.replace("-", " ")

def dataset_to_md(data: dict, filename: str) -> None:
    """
    Crée un fichier Markdown.

    - data : données
    - filename : nom du fichier à créer
    """
    with open(filename, "w") as md:
        md.write()


# Affichage sympa lors du lancement

print(
    """
 __   __        ___  __   __   __   __   __  
|__) /  \ |__/ |__  |__) |__| |  \ |__| |__) 
|    \__/ |  \ |___ |  \ |  | |__/ |  | |  \\
    """
    )

print(r"\\\\\\\\\\\\\\\\\\\\\\ PokéRadar v1.0")
print("---------------------- SAE 15 [2.2]")
print(r"////////////////////// Côme et Florian")
print()

# Initialisation des variables globales

global root_file

while 1:
    """
    Boucle infinie pour entrer des lieux à la chaîne
    """

    # On crée le répertoire cache
    try:
        os.mkdir("cache")
    except FileExistsError:
        pass
    except PermissionError:
        print(f"⚠️ Permission non accordée. Ne peut pas créer le cache")
    except Exception as e:
        pass

    # On crée le cache principal

    root_file = get_data_cached("https://pokeapi.co/api/v2/location/", 1036, "root.json")

    # L'utilisateur entre un nom de lieu
    
    en_place_name = input("\nEntrez un nom de lieu : ")

    # Formate le texte pour enlever les caractères génants

    formatted_place = en_place_name.replace(" ", "-").replace(".", "").lower()

    # Le programme itère sur root_file['results'][i]['name'] pour trouver l'url exacte ou une liste de résultats
    
    place_url = find_multiple_matches(formatted_place)

    print()
    if place_url[0] == "unknown":
        print("❌ Lieu inconnu...")
        continue    # Si le lieu est inconnu, on redemande un lieu
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

    place = get_data_cached(place_url, 0, f"{formatted_place}.json")

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

    poke_dict = {}

    for i in range(len(place['areas'])):
        # Parcourt les sous-lieux
        sub_area_name = place['areas'][i]['name']
        sub_area_url = place['areas'][i]['url']
        sub_area = get_data_cached(sub_area_url, 0, f"{sub_area_name}.json")

        for x in range(len(sub_area['pokemon_encounters'])):
            # Parcourt les pokémons rencontrables
            pkmn_name = sub_area['pokemon_encounters'][x]['pokemon']['name']
            pkmn_url = sub_area['pokemon_encounters'][x]['pokemon']['url']


            if pkmn_name not in poke_dict:
                # Si le Pokémon est déjà affiché, on l'ignore. Sinon, on l'affiche
                pkmn = get_data_cached(pkmn_url, 0, f"{pkmn_name}.json")
                
                fr_pkmn_name = get_pkmn_name(pkmn)
                pkmn_types = get_pkmn_types(pkmn)
                pkmn_sprite = get_pkmn_sprite(pkmn)
                pkmn_encounter_simple = get_encounter_method(sub_area, 0, "simple")
                pkmn_encounter_complete = get_encounter_method(sub_area, 0, "complete")
                pkmn_stats = get_pkmn_stats(pkmn)

                poke_dict[pkmn_name] = {}

                print("▶", end=" ")
                print(fr_pkmn_name)
                print(pkmn_encounter_complete)
                print(f"Type(s) : ", end="")
                for _type in pkmn_types:
                    print(_type, end=" ")    # Pour que les types s'affichent sur une seule ligne (avec un espace)
                print()     # Pour sauter une ligne car les print précédents ne retournent pas à la ligne

                poke_dict[pkmn_name]['fr_name'] = fr_pkmn_name
                poke_dict[pkmn_name]['types'] = pkmn_types
                poke_dict[pkmn_name]['sprite'] = pkmn_sprite
                poke_dict[pkmn_name]['encounter'] = pkmn_encounter_simple
                for stat_name, stat_data in pkmn_stats.items():
                    poke_dict[pkmn_name][stat_data['fr_name']] = stat_data['stat_value']
                    print(f"{stat_data['fr_name']} : {stat_data['stat_value']}")


                # stats_dict[en_stat_name]['fr_name'] = fr_stat_name
                # stats_dict[en_stat_name]['stat_value'] = stat_value

                print("------------------------------")    # Séparateur

    if len(poke_dict) == 0:
        print(f"\n⚠️  Aucun Pokémon trouvé pour ce lieu.")
    else:
        print(f"\n{len(poke_dict)} Pokémons trouvés pour ce lieu.")
        
    print("\n✅ Terminé !")

    with open(f"fiche-{formatted_place}.md", "w") as md:
        md.write("# Fiche PokéRadar\n")
        md.write("```\n[SAE 15]\nDAIRIN Côme\nSCHER Florian\n```\n")
        md.write(f"## {fr_place_name}\n")
        md.write(f"Région : {place['region']['name']}\n")
