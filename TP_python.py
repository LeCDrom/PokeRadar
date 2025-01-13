import markdown
import requests
import json
import os


# TELECHARGEMENT DES DONNEES PKMN.

def download_poke(id: int) -> dict:
    url = f"https://pokeapi.co/api/v2/pokemon/{id}?limit={id+2}"
    response = requests.get(url)
    data = response.json()
    return data

# MISE EN CACHE DU DICT

def poke_cached(id: int) -> dict:
    if os.path.isfile(f'cache/{id}.json'):
        with open(f'cache/{id}.json', "r") as f:
            file_content = json.load(f)
        f.close()
        return file_content
    elif not os.path.isfile(f'cache/{id}.json'):
        pkmn_data = download_poke(id)
        with open(f'cache/{id}.json', "w") as f:
            file_content = json.dump(pkmn_data, f)
        f.close()
        file_content = pkmn_data
        return file_content


file_content = poke_cached(77)
print(file_content["name"])

# ECRITURE EN MARKDOWN

def output_list_md(my_list: list[str], filename: str):
    with open(filename, "w") as f:
        f.write(f"# Test Markdown depuis Python\n\n")
        f.write(f"## Une liste de {len(my_list)} éléments :\n")
        for item in my_list:
            f.write(f"- {item}\n")
    f.close()

output_list_md(["Patate", "navet", "chou", "oignon"], "liste.md")

# CONVERSION MARKDOWN EN HTML

def markdown_to_html(filename: str):
    html = ""
    
    with open(filename, "r") as md:
        text = md.read()
        content = markdown.markdown(text)
    md.close()

    with open("index.html", "w") as html:
        html.write('<!DOCTYPE html>\n<html lang="fr">\n\n<head>\n\t<meta charset="UTF-8">\n\t<meta name="viewport" content="width=device-width, initial-scale=1.0">\n\t<title>Document</title>\n</head>\n\n<body>\n')
        html.write(content)
        html.write('\n</body>\n</html>')
    html.close()

markdown_to_html("liste.md")

# PRINT STATS EN FRANCAIS

def print_pokestats(data: dict):
    for i in range(6):
        
        stat_nb = data["stats"][i]["base_stat"]
        
        url = data["stats"][i]["stat"]["url"]
        response = requests.get(url)
        stats_json = response.json()
        stat_name = stats_json["names"][3]["name"]
        
        print(f"{stat_name} : {stat_nb}")
        
poke25 = download_poke(25)
print_pokestats(poke25)
