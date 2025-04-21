import json
import os.path

import numpy as np
import pandas as pd
from tqdm import trange, tqdm

tables = json.load(open('../tabid2tables.json', 'r'))
papers = json.load(open('../FINAL_corpusID2paper_with_full_content_and_link_and_Arxiv_ACL_parsed.json', 'r'))
full_text_available_id = json.load(open('../FINAL_full_text_available_paper_id.json', 'r'))
full_text_available_tabid_list = json.load(open('../FINAL_table_full_ref_available_id.json', 'r'))

PROMPT = """Given a literature review table, along with its caption, you are tasked with writing a user demand or intention for the creator of this table. The user demand should be written as though you are instructing an AI system to generate the table. Avoid directly mentioning column names in the table itself, but instead, focus on explaining why the table is needed and what information it should contain. You may include a description of the table’s structure, whether it requires detailed or summarized columns. Additionally, infer the user's intentions from the titles of the papers the table will include. Limit each user demand to 1-2 sentences.

Examples of good user demands are:

I need a table that outlines how each study conceptualizes the problem, categorizes the task, describes the data analyzed, and summarizes the main findings. The table should have detailed columns for each of these aspects.
Generate a detailed table comparing the theoretical background, research methodology, and key results of these papers. You can use several columns to capture these aspects for each paper.
I want to create a table that summarizes the datasets used to evaluate different GNN models, focusing on the common features and characteristics found across the papers listed below. The table should have concise columns to highlight these dataset attributes.

Now, write a user demand for the table below. The caption of the table is "{}". The table looks like this:
{}

The following papers are included in the table:
{}

Write the user demand for this table. Do not include the column names in the user demand. Write a concise and clear user demand covering the function, topic, and structure of the table with one or two sentences. The user demand is:"""

total_request = []
prompt_length = []

for tabid in full_text_available_tabid_list:
    caption = tables[tabid]['caption']
    table = pd.DataFrame.from_dict(tables[tabid]['table'])
    table_string = " | ".join(table.columns)
    for r in range(len(table)):
        table_string += "\n" + " | ".join([i[0] for i in table.iloc[r]])

    added_row_corpus_id = []
    titles = []
    for p in tables[tabid]['row_bib_map']:
        if p['corpus_id'] in added_row_corpus_id:
            continue
        added_row_corpus_id.append(p['corpus_id'])
        titles.append(papers[str(p['corpus_id'])]['title'])
    filled_prompt = PROMPT.format(caption, table_string, "\n".join(titles))
    total_request.append({
        "custom_id": "caption_rewriting_user_demand_tabid_{}".format(tabid),
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": filled_prompt
                },
            ],
            "max_tokens": 200,
            "temperature": 0.8
        }
    })
    prompt_length.append(len(filled_prompt.split()))

with open("caption_rewriting_user_demand_gpt4o.jsonl", 'w') as f:
    for j in total_request:
        f.write(json.dumps(j) + '\n')

if os.path.exists('./caption_rewriting_user_demand_gpt4o_output.jsonl'):
    generation = [json.loads(i) for i in open('./caption_rewriting_user_demand_gpt4o_output.jsonl').readlines()]

    for i in tqdm(generation):
        tabid = i['custom_id'].split('_')[-1]
        user_demand = i['response']['body']['choices'][0]['message']['content']
        tables[tabid]['user_demand'] = user_demand

    with open('../tabid2tables_with_user_demand.json', 'w') as f:
        json.dump(tables, f, indent=4)
