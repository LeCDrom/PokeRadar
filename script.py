import requests
import markdown
# import rapidfuzz
import json
import os
# import mathplotlib.pyplot as plt


def get_data(url: str, limit: int) -> dict:
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
        data = get_data(url, limit)
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
    i = 0

    while i < count:
        if root_file['results'][i]['name'] == name:
            return root_file['results'][i]['url']
        else:
            i += 1
    
    return "unknown"

def print_pokestats(data: dict) -> None:
    """
    Affiche chaque stat d'un Pokémon en français.
    
    - data : données de la requête
    """
    for i in range(6):
        
        stat_value = data['stats'][i]['base_stat']
        stat_name = data['stats'][i]['stat']['name']
        
        url = data['stats'][i]['stat']['url']
        stats_json = get_data_cached(url, 0, f"{stat_name}.json")
        fr_stat_name = stats_json['names'][3]['name']
        
        print(f"{fr_stat_name} : {stat_value}")

def print_pkmn_name(data: dict) -> None:
    """
    Affiche le nom d'un Pokémon en français.
    
    - data : données de la requête
    """
    en_name = data['name']
    url = data['species']['url']
    pkmn = get_data_cached(url, 0, f"{en_name}-species.json")
    fr_name = pkmn['names'][4]['name']

    print(fr_name)

def get_area_name(data: dict) -> None:
    """
    Affiche le nom d'un lieu en français.
    
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
    



# Initialisation des variables globales

global root_file

while 1:
    """
    Boucle infinie pour entrer des lieux à la chaîne
    """

    # On crée le cache principal

    root_file = get_data_cached("https://pokeapi.co/api/v2/location/", 1036, "root.json")

    # L'utilisateur entre un nom de lieu
    
    en_place_name = input("\nEntrez un nom de lieu : ")

    # Formate le texte pour enlever les caractères génants

    formatted_place = en_place_name.replace(" ", "-").replace(".", "").lower()

    # Le programme itère sur root_file['results'][i]['name'] pour trouver l'url

    place_url = find_place_url(formatted_place)

    print()
    if place_url != "unknown":
        print("✅ Lieu trouvé !")
    else:
        print("❌ Lieu inconnu...")
        continue    # Si le lieu est inconnu, on recommence
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

    poke_dict = {'pokemon': [], 'type': []}

    wait = input(f"[Entrée] Affichage des Pokémons de la zone...")
    print()

    for i in range(len(place['areas'])):
        # Parcourt les sous-lieux
        sub_area_name = place['areas'][i]['name']
        sub_area_url = place['areas'][i]['url']
        sub_area = get_data_cached(sub_area_url, 0, f"{sub_area_name}.json")

        for x in range(len(sub_area['pokemon_encounters'])):
            # Parcourt les pokémons rencontrables
            pkmn_name = sub_area['pokemon_encounters'][x]['pokemon']['name']
            pkmn_url = sub_area['pokemon_encounters'][x]['pokemon']['url']


            if pkmn_name not in poke_dict['pokemon']:
                # Si le Pokémon est déjà affiché, on l'ignore
                poke_dict['pokemon'].append(pkmn_name)
                pkmn = get_data_cached(pkmn_url, 0, f"{pkmn_name}.json")
                
                print("▶", end=" ")
                print_pkmn_name(pkmn)
                print_pokestats(pkmn)
                
                print("------------------------------")    # Séparateur

    if len(poke_dict['pokemon']) == 0:
        print("\n⚠️  Aucun Pokémon trouvé pour ce lieu.")
    else:
        print(f"\n{len(poke_dict['pokemon'])} Pokémons trouvés pour ce lieu.")

    print("\n✅ Terminé !")
