import bibtexparser
from bibtexparser.customization import convert_to_unicode
from munch import Munch

def get_author_last_name(auth_str):
    if "," in auth_str:
        return auth_str.split(",")[0].strip()
    if len(auth_str.split(" ")) > 1:
        return auth_str.split(" ")[1].strip()
    else:
        return auth_str.split(" ")[0].strip()


def format_reference(entry):
    authors = entry["author"].split(" and ")
    if len(authors) == 1:
        author_str = get_author_last_name(authors[0])
    elif len(authors) == 2:
        author_str = f"{get_author_last_name(authors[0])} & {get_author_last_name(authors[1])}"
    else:
        author_str = f"{get_author_last_name(authors[0])} et al."
    return f"{author_str} ({entry['year'].strip()})"

def parse_bibtext(bib_file: str) -> dict:
        # convert bibtex entries to author et al. (year) strings
        parser = bibtexparser.bparser.BibTexParser()
        parser.customization = bibtexparser.customization.convert_to_unicode
        with open(bib_file) as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file, parser=parser)
        year2entry = {}
        for entry in bib_database.entries:
            entry = bibtexparser.customization.author(entry)
            year2entry.setdefault(entry["year"], []).append(entry)
        return year2entry

def format_names(normalized_names):
    separated_names = [name.split(", ") for name in normalized_names]
    normalized_names = [f"{name[1]} {name[0]}" for name in separated_names]

    if len(normalized_names) == 1:
        return normalized_names[0]
    elif len(normalized_names) == 2:
        return " and ".join(normalized_names)
    else: # length >= 3
        allbutlast = ", ".join(normalized_names[:-1])
        return f"{allbutlast}, and {normalized_names[-1]}"

def get_author_list(entry):
    entry.author = format_names(entry.author)
    return entry.author

def get_venue(entry) -> str:
    if entry.ENTRYTYPE == "inproceedings":
        return entry.booktitle
    elif entry.ENTRYTYPE == "article":
        return entry.journal

def get_doi(doi: str) -> str:
    return f"https://doi.org/{doi}"


def format_entry(entry) -> str:
    link = get_doi(entry.doi) if 'doi' in entry else entry.url
    template = f"""
<div class="bibentry">
{get_author_list(entry)} <br>
<a href="{link}"><whitetext>{entry.title}</whitetext></a><br>
{get_venue(entry)}.<br>   
"""
    if 'award' in entry:
        template += f"""
<i class="fa-solid fa-trophy"></i> {entry.award}
"""
    return template + "</div>"


if __name__=="__main__":
    fname = '../publications.bib'
    year2entry = parse_bibtext(fname)
    for year, entries in year2entry.items():
        print(f"""<h2>{year}</h2>""")
        for entry in entries:
            print(format_entry(Munch(entry)))

