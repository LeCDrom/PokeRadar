import markdown


def convert(input_f: str, output_f:str, page_name: str="Converted") -> None:
    """
    Convertit un fichier en entrée Markdown en HTML.

    - input_f : Nom du fichier Markdown [str]
    - output_f : Nom du fichier HTML [str]
    - page-name : Nom de la page (optionnel) [str]
    Valeur par défaut : "Converted"
    """    
    with open(input_f, "r") as md:
        text = md.read()
        content = markdown.markdown(text, extensions=['tables'])

    with open(output_f, "w") as html:
        # Applique la police Roboto Mono à la page
        html.write(f'<!DOCTYPE html>\n<html lang="fr">\n\n<head>\n<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0">\n<title>{page_name}</title>\n<link rel="preconnect" href="https://fonts.googleapis.com">\n<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>\n<link href="https://fonts.googleapis.com/css2?family=Roboto+Mono:ital,wght@0,100..700;1,100..700&display=swap" rel="stylesheet">\n</head>\n<style>\n')
        html.write('* { font-family: "Roboto Mono";}\nbody { padding-inline: 10% }\ntable { width: 100%; }\nimg { align-self: center; }\n</style>\n\n<body>\n')
        html.write(content)
        html.write('\n</body>\n</html>')


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3 or len(sys.argv) > 4:
        print("/\\ python md_to_html.py [input_file.md] [output_file.html] {page-name}")
    else:
        if len(sys.argv) == 4:
            convert(sys.argv[1], sys.argv[2], sys.argv[3])
        else:
            convert(sys.argv[1], sys.argv[2])
