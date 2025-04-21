from bs4 import BeautifulSoup
import requests
import json
import re
import warnings
from collections import OrderedDict

from tqdm import tqdm

warnings.filterwarnings("ignore")


def parse_table(table):
    rows = table.find_all("tr")
    table_data = {
        "table_column_names": [],
        "table_content_values": []
    }
    content_rows = []
    for row in rows:
        row_text = row.text
        row_text = row_text.strip("\n").strip()
        if row_text == "":
            continue
        row_text = row_text.split("\n")
        row_text = [text for text in row_text if text != ""]
        content_rows.append(row_text)
    assert len(content_rows) > 1, "Table is empty"
    table_data["table_column_names"] = content_rows[0]
    table_data["table_content_values"] = content_rows[1:]

    return table_data


def parsing_ar5iv(link):
    response = requests.get(link, verify=False)
    html = response.text

    # Parse the HTML content
    soup = BeautifulSoup(html, "html.parser")

    # Find all sections with an id attribute that contains the letter "S"
    raw_abstract = soup.find_all("div", "ltx_abstract")
    try:
        abstract = ''.join(raw_abstract[0].text.split("\n")[2:])
    except:
        print("Failed to parse abstract for paper " + link)
        abstract = ""

    try:
        sections = soup.find_all("section", {"class": "ltx_section"})  # attrs={"id": re.compile(r"^S\d+$")})
    except:
        raise Exception("Failed to parse sections for paper " + link)
    subsections = soup.find_all(class_='ltx_para', id=re.compile(r"^S\d+\.+(p|S)"))

    # find all the figures with captions
    figures = soup.find_all(class_='ltx_figure')
    figure_sources = []
    figure_captions = []
    for figure in figures:
        try:
            figure_src = figure.find_all("img")[0].get("src")
        except:
            figure_src = None
        if not figure_src:
            continue
        figure_sources.append(requests.compat.urljoin(link, figure_src))
        try:
            figure_caption = figure.find_all("figcaption")[0].text
        except:
            figure_caption = ""
        figure_captions.append(figure_caption)

    # find all the tables with captions
    tables = soup.find_all(class_='ltx_table')
    linearized_tables = []
    table_captions = []
    for table in tables:
        try:
            table_caption = table.find_all("figcaption")[0].text
        except:
            table_caption = ""
        try:
            table_data = parse_table(table.find_all("table")[0])
        except:
            table_data = {
                "table_column_names": [],
                "table_content_values": [],
            }
        linearized_tables.append(table_data)
        table_captions.append(table_caption)

    # Count the number of sections
    count = len(subsections)

    full_text = []
    named_sections = OrderedDict()

    for section in sections:
        try:
            section_title = section.find("h2").text.strip("\n")
        except:
            section_title = section.text.split(' ')[0]
        named_sections[section_title] = section.text
    for i in range(count):
        full_text.append(re.sub(r"\n", "", subsections[i].text))

    # # extracted all related papers
    # refs = soup.find_all("a", class_="ltx_ref")
    # bib_ids = [x['href'].strip("#") for x in refs]
    # bib_ids = [x for x in bib_ids if x.startswith("bib.bib")]
    # bib_ids = list(set(bib_ids))
    # ref_titles = []
    # for bid in bib_ids:
    #     ref_titles.append(soup.find_all("li", id=bid)[0].text)
    # if "2403.09338" in link:
    #     ref_titles = [x.strip("\n\n\n").split(".:")[1] for x in ref_titles]
    # else:
    #     ref_titles = [x.split("\n\n\n")[1] for x in ref_titles]
    # ref_titles = [ref_title.split(".")[0].strip("\n").replace("\n", " ") for ref_title in ref_titles]
    return abstract, full_text, named_sections, figure_sources, figure_captions, linearized_tables, table_captions, None


if __name__ == "__main__":
    # """arxiv_ids = ['1611.04684v1']
    # ar5iv_links = []
    # for arxiv_id in arxiv_ids:
    #     ar5iv_links.append(f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}")
    # paragraphs, named_sections = parsing_ar5iv(ar5iv_links[0])
    # print(paragraphs)"""
    paper_list = json.load(open('../corpusID2paper_with_full_content_and_link_3rd_round_FINAL.json', 'r'))
    for p in tqdm(paper_list, desc="parsing Arxiv papers"):
        if 'externalIds' not in paper_list[p]:
            continue
        if paper_list[p]['externalIds']:
            if 'ArXiv' in paper_list[p]['externalIds']:
                arxiv_id = paper_list[p]['externalIds']['ArXiv']
                ar5iv_link = f"https://ar5iv.labs.arxiv.org/html/{arxiv_id}"
                abstract, full_text, named_sections, figure_sources, figure_captions, linearized_tables, table_captions, ref_titles = parsing_ar5iv(
                    ar5iv_link)
                paper_list[p]['full_text_parsed_Arxiv'] = '\n'.join(full_text)
                # print('\n'.join(full_text))
                # print(len('\n'.join(full_text).split()))
            else:
                continue
        else:
            continue
    json.dump(
        paper_list,
        open('../FINAL_corpusID2paper_with_full_content_and_link_and_Arxiv_parsed.json', 'w'),
        indent=4
    )
