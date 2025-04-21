import json

import numpy as np
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import torch

# Check if CUDA is available
if torch.cuda.is_available():
    print("GPU is available!")
    device = torch.device("cuda")
else:
    print("GPU is not available, using CPU.")
    device = torch.device("cpu")

print(f"Using device: {device}")

tables = json.load(open('../tabid2tables.json', 'r'))
papers = json.load(open('../FINAL_corpusID2paper_with_full_content_and_link_and_Arxiv_ACL_parsed.json', 'r'))
full_text_available_id = json.load(open('../FINAL_full_text_available_paper_id.json', 'r'))
full_text_available_tabid_list = json.load(open('../FINAL_table_full_ref_available_id.json', 'r'))

model_name = "sentence-t5-xxl"
model = SentenceTransformer(model_name, device="cuda")

caption_dict = {
    tabid: None for tabid in full_text_available_tabid_list
}

title_and_abstracts_dict = {
    paperid: None for paperid in full_text_available_id
}

computed_corpus_id_list = []

for tabid in tqdm(full_text_available_tabid_list):
    caption = tables[tabid]['caption']
    if not caption_dict[tabid]:
        caption_dict[tabid] = model.encode(caption)
    for p in tables[tabid]['row_bib_map']:
        if p['corpus_id'] not in computed_corpus_id_list:
            title_and_abstracts_dict[str(p['corpus_id'])] = model.encode(
                papers[str(p['corpus_id'])]['title'] + ' ' + papers[str(p['corpus_id'])]['abstract']
            )
            computed_corpus_id_list.append(p['corpus_id'])

np.save('caption_embedding.npy', caption_dict)
np.save('title_and_abstracts_embedding.npy', title_and_abstracts_dict)
