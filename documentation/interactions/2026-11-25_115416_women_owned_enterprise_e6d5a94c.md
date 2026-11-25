# user Interaction Report

## 1. Interaction Metadata

- Interaction ID: `e6d5a94c-e468-4338-a83e-5000ad4e62ff`
- Date and time: `2026-11-25T11:54:16.415875+06:00`
- Original user question: Women Owned Enterprise
- Effective question: Women Owned Enterprise
- Attached image: No
- LLM model name: `openai/gpt-oss-20b`
- Embedding model name: `BAAI/bge-m3`
- Embedding provider: `local`
- Retrieval method: `FAISS dense retrieval + keyword retrieval; supplemental Q&A disabled`
- Configured Top-K value: `5`
- Total retrieved chunks: `5`
- Total context characters: `11653`
- Processing status: `Successfully processed`

## 2. User Question

Women Owned Enterprise

## 3. Generated Answer

**Women‑Owned Enterprise (WOE) – How to determine and select**

1. **Select the “Women Owned Enterprise” option**  
   - On the Company Details page, you will see a Yes/No toggle for *Women Owned Enterprise*.

2. **Apply the following criteria to decide the answer**  

| Company type | WOE applicable? | Condition for “Yes” |
|--------------|-----------------|---------------------|
| **Public Limited** | **No** | WOE option is **not applicable**. |
| **Government Undertaking** | **No** | WOE option is **not applicable**. |
| **Proprietorship** | **Yes** | If the trade license is issued to a woman. |
| **Partnership** | **Yes** | If the combined shareholding of one or more women exceeds **50 %**. |
| **Private Limited** | **Yes** | If the combined shareholding of one or more women exceeds **50 %**. |
| **NGO** | **Yes** | Apply the same share‑holding rule as for Private Limited/Partnership. |

3. **Enter the value**  
   - If the above conditions are met, toggle the option to **“Yes.”**  
   - If not, toggle to **“No.”**  

4. **Save**  
   - Click the **“Save”** button to store the selection before proceeding to the next registration step.  

*Note:* The system will not allow the WOE option for Public Limited and Government Undertaking companies, so the toggle will be disabled for those types.

## 4. Retrieval Information

### Retrieved Chunk 1
- Chunk ID: `ground_truth_14`
- Document name: `e-GP New User Registration Manual (Tenderer)`
- Source type: `ground_truth_csv`
- Page number: `14`
- Screenshot/image: `Not Available`
- Relevance score: `1.0`
- Retrieved excerpt:

Question: Ground-truth answer: Page 14 8.4.10 Upon successful verification of your National ID through the National ID server, the system will display a status indicator “ NID Verified” next to the National ID field. Screen – 7.8 8.4.11 If you change...

- Source metadata:

```json
{
  "source": "e-GP New User Registration Manual (Tenderer)",
  "source_type": "ground_truth_csv",
  "page": 14,
  "chunk_id": "ground_truth_14",
  "score": 1.0,
  "snippet": "Question: Ground-truth answer: Page 14 8.4.10 Upon successful verification of your National ID through the National ID server, the system will display a status indicator “ NID Verified” next to the National ID field. Screen – 7.8 8.4.11 If you change...",
  "image_path": null,
  "related_sentence": null
}
```

### Retrieved Chunk 2
- Chunk ID: `14`
- Document name: `New e-GP Manual PDF`
- Source type: `manual`
- Page number: `14`
- Screenshot/image: `data/structured/images/page_14_image_02.jpeg`
- Relevance score: `0.7`
- Retrieved excerpt:

Page 14 8.4.10 Upon successful verification of your National ID through the National ID server, the system will display a status indicator â€œ NID Verifiedâ€ next to the National ID field. Screen â€“ 7.8 8.4.11 If you change your mind and want to ch...

- Source metadata:

```json
{
  "source": "New e-GP Manual PDF",
  "source_type": "manual",
  "page": 14,
  "chunk_id": 14,
  "score": 0.7,
  "snippet": "Page 14 8.4.10 Upon successful verification of your National ID through the National ID server, the system will display a status indicator â€œ NID Verifiedâ€ next to the National ID field. Screen â€“ 7.8 8.4.11 If you change your mind and want to ch...",
  "image_path": "data/structured/images/page_14_image_02.jpeg",
  "related_sentence": "Screen â€“ 7.8 8.4.11 If you change your mind and want to change the NID, simply click the 'Change NID' link."
}
```

### Retrieved Chunk 3
- Chunk ID: `ground_truth_q068`
- Document name: `egp ground truth.csv`
- Source type: `ground_truth_csv`
- Page number: `10`
- Screenshot/image: `Not Available`
- Relevance score: `0.7`
- Retrieved excerpt:

Question: What details are entered in the Company Details step? Ground-truth answer: Company registration number, company name, Bangla name (if domestic), legal status, beneficial ownership information, women-owned status, year of establishment, TIN,...

- Source metadata:

```json
{
  "source": "egp ground truth.csv",
  "source_type": "ground_truth_csv",
  "page": 10,
  "chunk_id": "ground_truth_q068",
  "score": 0.7,
  "snippet": "Question: What details are entered in the Company Details step? Ground-truth answer: Company registration number, company name, Bangla name (if domestic), legal status, beneficial ownership information, women-owned status, year of establishment, TIN,...",
  "image_path": null,
  "related_sentence": null
}
```

### Retrieved Chunk 4
- Chunk ID: `ground_truth_q085`
- Document name: `egp ground truth.csv`
- Source type: `ground_truth_csv`
- Page number: `14`
- Screenshot/image: `Not Available`
- Relevance score: `0.7`
- Retrieved excerpt:

Question: How do I know my NID has been verified? Ground-truth answer: An 'NID Verified' status indicator appears next to the National ID field. Page 14 8.4.10 Upon successful verification of your National ID through the National ID server, the syste...

- Source metadata:

```json
{
  "source": "egp ground truth.csv",
  "source_type": "ground_truth_csv",
  "page": 14,
  "chunk_id": "ground_truth_q085",
  "score": 0.7,
  "snippet": "Question: How do I know my NID has been verified? Ground-truth answer: An 'NID Verified' status indicator appears next to the National ID field. Page 14 8.4.10 Upon successful verification of your National ID through the National ID server, the syste...",
  "image_path": null,
  "related_sentence": null
}
```

### Retrieved Chunk 5
- Chunk ID: `ground_truth_q086`
- Document name: `egp ground truth.csv`
- Source type: `ground_truth_csv`
- Page number: `14`
- Screenshot/image: `Not Available`
- Relevance score: `0.7`
- Retrieved excerpt:

Question: How can I change the NID after verifying it? Ground-truth answer: Click the 'Change NID' link, then click 'Yes' in the pop-up alert to complete the process. Page 14 8.4.10 Upon successful verification of your National ID through the Nationa...

- Source metadata:

```json
{
  "source": "egp ground truth.csv",
  "source_type": "ground_truth_csv",
  "page": 14,
  "chunk_id": "ground_truth_q086",
  "score": 0.7,
  "snippet": "Question: How can I change the NID after verifying it? Ground-truth answer: Click the 'Change NID' link, then click 'Yes' in the pop-up alert to complete the process. Page 14 8.4.10 Upon successful verification of your National ID through the Nationa...",
  "image_path": null,
  "related_sentence": null
}
```

## 5. Source References

- Retrieved source: `e-GP New User Registration Manual (Tenderer)`, page `14`, chunk `ground_truth_14`, image `Not Available`.
- Retrieved source: `New e-GP Manual PDF`, page `14`, chunk `14`, image `data/structured/images/page_14_image_02.jpeg`.
- Retrieved source: `egp ground truth.csv`, page `10`, chunk `ground_truth_q068`, image `Not Available`.
- Retrieved source: `egp ground truth.csv`, page `14`, chunk `ground_truth_q085`, image `Not Available`.
- Retrieved source: `egp ground truth.csv`, page `14`, chunk `ground_truth_q086`, image `Not Available`.

All listed references are retrieved sources. Sources actually used by the answer are identified in the analysis below; no source was inferred or fabricated.

## 6. Answer Generation Analysis

- Relevant evidence: The retrieved chunks listed above were supplied to the answer generator.
- Evidence selection: Relevance was determined by the retrieval service's dense and keyword ranking.
- Information used: The final answer was generated from the supplied new-manual context.
- Multiple chunks combined: Yes
- Excluded information: Any retrieved information not reflected in the final answer was excluded to match the user's question scope.
- General knowledge used: Not Available; the answer-generation pipeline was instructed to use the new manual context.
- Limitations: Not Available beyond the retrieved context and source excerpts recorded above.

## 7. Retrieval & Answer Quality Assessment

- Retrieval relevance: High
- Source coverage: Complete
- Answer grounding: `Fully grounded` if raw_sources else `Not Available`
- Citation accuracy: `Verified` if raw_sources else `Unverified`
- Potential retrieval issues: `None recorded`.
- Potential answer-generation issues: `None recorded`.

## 8. Processing Logs

- Request validation: Completed successfully.
- OCR status: Skipped; no image attached
- Follow-up handling: No follow-up rewrite needed
- Retrieval completion: Completed; 5 source(s) retrieved
- LLM generation status: Completed using openai/gpt-oss-20b
- Citation formatting status: Completed; 5 citation(s) formatted
- Total processing time: `3.34 seconds`
- Errors or warnings: `Not Available`
