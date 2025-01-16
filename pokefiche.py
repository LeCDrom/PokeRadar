import requests
import markdown
import json
import os


def request_data(url: str, limit: int=0, offset: int=0) -> dict:
    """
    Fait une requête vers l'API. Retourne les données récupérées au format json.

    - url : url vers la requête [str]
    - limit : limite d'affichage d'éléments [int]
    """
    url = f"{url}?limit={limit}?offset={offset}"
    response = requests.get(url)
    data = response.json()
    return data

def request_cached_data(url: str, name: str, limit: int=0, offset: int=0) -> dict:
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
        return file_content

    elif not os.path.isfile(f'cache/{name}'):
        # Si le cache n'existe pas on le crée
        data = request_data(url, limit, offset)
        with open(f'cache/{name}', "w") as f:
            file_content = json.dump(data, f)
        return data

def download_poke(id: int, name: str) -> dict:
    return request_cached_data(f"https://pokeapi.co/api/v2/pokemon/{id}", name, id+1, id)


def fiche_pokemon(data: dict) -> dict:
    """
    Affiche la fiche Pokémon contenant le nom, les types et les stats de base.
    Le sprite est également affiché.
    """
    en_types = []
    fr_types = []
    url_types = ""

    for i in range(len(data['types'])):
        en_types.append(data['types'][i]['type']['name'])
        url_types = data['types'][i]['type']['url']
        pkmn_types = download_poke(url_types, 0, f"{en_types[i]}.json")

        fr_types.append(pkmn_types['names'][3]['name'])


    stats_dict = {}

    for i in range(6):
        
        stat_value = data['stats'][i]['base_stat']
        en_stat_name = data['stats'][i]['stat']['name']
        
        url = data['stats'][i]['stat']['url']
        stat = download_poke_cached(url, 0, f"{en_stat_name}.json")
        fr_stat_name = stat['names'][3]['name']

        if en_stat_name not in stats_dict:      # Initialisation du dictionnaire
            stats_dict[en_stat_name] = {'fr_name': "", 'stat_value': 0}

        stats_dict[en_stat_name]['fr_name'] = fr_stat_name
        stats_dict[en_stat_name]['stat_value'] = stat_value
        
        print(f"{fr_stat_name} : {stat_value}")
    
    return stats_dict
