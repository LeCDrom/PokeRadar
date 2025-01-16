import markdown


def md_to_html(filename: str):
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