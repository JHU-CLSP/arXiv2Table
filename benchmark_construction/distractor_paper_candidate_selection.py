import numpy as np
import json

from tqdm import tqdm

tables = json.load(open('../tabid2tables.json', 'r'))
papers = json.load(open('../FINAL_corpusID2paper_with_full_content_and_link_and_Arxiv_ACL_parsed.json', 'r'))
full_text_available_id = json.load(open('../FINAL_full_text_available_paper_id.json', 'r'))
full_text_available_tabid_list = json.load(open('../FINAL_table_full_ref_available_id.json', 'r'))

table_captions = np.load('./caption_embedding.npy', allow_pickle=True).item()
title_abstracts = np.load('./title_and_abstracts_embedding.npy', allow_pickle=True).item()

tabid2corpusID_similarity = {tabid: {} for tabid in full_text_available_tabid_list}
tabid2corpusID_top50similarityCorpusId = {tabid: [] for tabid in full_text_available_tabid_list}

for tabid in tqdm(full_text_available_tabid_list):
    added_reference_papers = []
    for p in tables[tabid]['row_bib_map']:
        if str(p['corpus_id']) in added_reference_papers:
            continue
        added_reference_papers.append(str(p['corpus_id']))
    tab_embedding = [title_abstracts[p] for p in added_reference_papers]
    for i in title_abstracts.keys():
        if i not in added_reference_papers and title_abstracts[i] is not None:
            # cosine similarity
            similarity = np.dot(table_captions[tabid], title_abstracts[i]) / (
                    np.linalg.norm(table_captions[tabid]) * np.linalg.norm(title_abstracts[i]))
            tabid2corpusID_similarity[tabid][i] = float(similarity)

    tabid2corpusID_top50similarityCorpusId[tabid] = sorted(tabid2corpusID_similarity[tabid].items(),
                                                           key=lambda x: x[1], reverse=True)[:50]

# save both files into json
with open('tabid2corpusID_similarity.json', 'w') as f:
    json.dump(tabid2corpusID_similarity, f, indent=4)

with open('tabid2corpusID_top50similarity.json', 'w') as f:
    json.dump(tabid2corpusID_top50similarityCorpusId, f, indent=4)
