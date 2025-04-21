import json
import os
import requests
from papermage.recipes import CoreRecipe
from tqdm import tqdm
import glob


def download_ACL_pdfs(ACL_ids, output_dir, paperId):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    base_url = "https://aclanthology.org/"

    for arxiv_id in ACL_ids:
        try:
            pdf_url = f"{base_url}{arxiv_id}.pdf"
            response = requests.get(pdf_url, stream=True)
            if response.status_code == 200:
                file_path = os.path.join(output_dir, f"{paperId}.pdf")
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            file.write(chunk)
                print(f"Downloaded: {arxiv_id}")
            else:
                print(f"Failed to download {arxiv_id}: {response.status_code}")
        except Exception as e:
            print(f"Error downloading {arxiv_id}: {e}")


# Example usage
if __name__ == "__main__":
    paper_list = json.load(open('../corpusID2paper_with_full_content_and_link_3rd_round_FINAL.json', 'r'))
    recipe = CoreRecipe()
    for p in tqdm(paper_list, desc="downloading all ACL papers"):
        if 'externalIds' not in paper_list[p]:
            continue
        if os.path.exists(f"../acl_papers/{p}.pdf"):
            continue
        if paper_list[p]['externalIds']:
            if 'ACL' in paper_list[p]['externalIds']:
                download_ACL_pdfs([paper_list[p]['externalIds']['ACL']], "../acl_papers/", p)
            else:
                print("No ACL ID found for paper", p)

    downloaded_papers = glob.glob('../acl_papers/*.pdf')
    for p in tqdm(downloaded_papers, desc="Parsing all ACL papers"):
        pdf_path = os.path.join(p)
        paper_id = p.split('/')[-1].split('.')[0]
        try:
            doc = recipe.run(pdf_path)
        except:
            print(f"Failed to extract text for {p}")
            continue
        cleaned_paragraphs = []
        for p in doc.paragraphs:
            p_text = p.text.replace("- ", "")
            if len(p_text) < 40:
                continue
            if len(cleaned_paragraphs) == 0:
                cleaned_paragraphs.append(p_text)
            elif not p_text[0].isupper():
                cleaned_paragraphs[-1] += " " + p_text
            else:
                cleaned_paragraphs.append(p_text)
        paper_list[paper_id]['full_text_parsed_ACL'] = "\n".join(cleaned_paragraphs)
        # print(f"Extracted text for {p}")
        # print("Parsed text:", paper_list[paper_id]['full_text_parsed'])
        # print(len(paper_list[paper_id]['full_text_parsed'].split()))
        # print(paper_id)

    json.dump(
        paper_list,
        open('../FINAL_corpusID2paper_with_full_content_and_link_and_ACL_parsed.json', 'w'),
        indent=4
    )
