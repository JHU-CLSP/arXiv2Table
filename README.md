# Can LLMs Generate Tabular Summaries of Science Papers? Rethinking the Evaluation Protocol

[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)

This is the official data and code repository for the paper [Can LLMs Generate Tabular Summaries of Science Papers? Rethinking the Evaluation Protocol](https://arxiv.org/pdf/2504.10284).

## arXiv2Table Benchmark
The full benchmark is available in the `data` directory. Full text of the papers can be downloaded at [this link](https://hkustconnect-my.sharepoint.com/:u:/g/personal/wwangbw_connect_ust_hk/EeMgL0XuJeNKlMCZnGUZu6AB_D1Swe0Wz1DxnFeNpUP-PQ?e=SEfPcP).

### Data Format
Each data entry looks like:
```json
{
  "table_id": "...",
  "table_query_id": ...,
  "table_caption": "...",
  "user_demand": "...",
  "table": {
    "MR": {...},
    "NLG": {...}
  },
  "input_references_id": [...],
  "input_references_label": [...],
  "table_references": [...],
  "sampled_noisy_paper": [...]
}
```
- `table_id`: A unique identifier for this specific table instance.
- `table_query_id`: An integer representing the ID of the user query or information need. Multiple entries can share the same query ID if they stem from the same user instruction.
- `table_caption`: A human-readable caption that describes the table content or theme. Mimics captions typically found in research papers.
- `user_demand`: The detailed user intent in natural language. It specifies what the table should demonstrate or convey.
- `table`: The core content of the benchmark entry, can be loaded via pandas.DataFrame.
- `input_references_id`: A list of all paper reference IDs retrieved or considered for the table construction.
- `input_references_label`: A list of binary labels (1 for relevant, 0 for irrelevant) corresponding to `input_references_id`, indicating whether each paper was selected for table inclusion.
- `table_references`: A subset of `input_references_id` that were included in the final table (i.e., where the label is 1).
- `sampled_noisy_paper`: A sample of papers labeled as irrelevant (0) included to simulate distractor papers. Useful for evaluating the robustness of LLM-based table generation against noisy retrieval results.

### Benchmark Construction
Code for constructing the benchmark is available in the `benchmark_construction` directory.
To reproduce the benchmark:
1. Download the [arxivDIGESTables](https://aclanthology.org/2024.emnlp-main.538.pdf) dataset, which is available at [this link](https://huggingface.co/datasets/blnewman/arxivDIGESTables).
2. Collect user demands of generating the tables based on table caption via `user_intention_rewriting.py`.
3. Run `distractor_paper_embedding.py` to generate embeddings for the papers in the dataset.
4. Run `distractor_paper_candidate_selection.py` to select distractor paper candidates.
5. Annotate them via human experts to determine their relevance, then merge the labels into the benchmark.

Code for parsing papers from arXiv and ACL Anthology are also made available as `parse_arxiv_paper.py` and `parse_acl_paper.py`, respectively.

## Methods
We also release the code to reproduce all baselines and our proposed method. The code is organized into two main directories:
- `baseline`: Code for reproducing the baselines.
- `method`: Code for our proposed iterative batch-based method.

## Evaluation
To evaluate the generated tables, we provide a script to synthesize QA pairs from a table and ask LLMs to answer them based on the other table.
The evaluation script is located in the `evaluation` directory.

## References
If you wish to use our code or data, please cite our paper at:
```bibtex
@misc{wang2025llmsgeneratetabularsummaries,
      title={Can LLMs Generate Tabular Summaries of Science Papers? Rethinking the Evaluation Protocol}, 
      author={Weiqi Wang and Jiefu Ou and Yangqiu Song and Benjamin Van Durme and Daniel Khashabi},
      year={2025},
      eprint={2504.10284},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2504.10284}, 
}
```