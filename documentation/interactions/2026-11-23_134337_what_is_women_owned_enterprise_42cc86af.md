# user Interaction Report

## 1. Interaction Metadata

- Interaction ID: `42cc86af-8963-4ad2-bd93-587727a94458`
- Date and time: `2026-11-23T13:43:37.478332+06:00`
- Original user question: what is Women Owned Enterprise?
- Effective question: what is Women Owned Enterprise?
- Attached image: No
- LLM model name: `openai/gpt-oss-20b`
- Embedding model name: `BAAI/bge-m3`
- Embedding provider: `local`
- Retrieval method: `FAISS dense retrieval + keyword retrieval; supplemental Q&A disabled`
- Configured Top-K value: `2`
- Total retrieved chunks: `2`
- Total context characters: `2111`
- Processing status: `Successfully processed`

## 2. User Question

what is Women Owned Enterprise?

## 3. Generated Answer

**Women Owned Enterprise (WOE)**  

In the e‑GP registration, a tenderer must indicate whether their company is a Women Owned Enterprise. The system applies the following criteria:

| Company type | WOE status | Conditions |
|--------------|------------|------------|
| **Public Limited** or **Government Undertaking** | **Not applicable** | These categories cannot be marked as WOE. |
| **Proprietorship** | **Yes** if the trade license is issued to a woman. | |
| **Partnership** or **Private Limited** | **Yes** if women hold **more than 50 %** of the company’s shares (one or more women in combination). | |

The tenderer selects “Yes” or “No” for the WOE option during the Company Details page of the registration process.

## 4. Retrieval Information

### Retrieved Chunk 1
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
  "page": 14,
  "chunk_id": 14,
  "score": 0.7,
  "snippet": "Page 14 8.4.10 Upon successful verification of your National ID through the National ID server, the system will display a status indicator â€œ NID Verifiedâ€ next to the National ID field. Screen â€“ 7.8 8.4.11 If you change your mind and want to ch...",
  "image_path": "data/structured/images/page_14_image_02.jpeg",
  "related_sentence": "Screen â€“ 7.8 8.4.11 If you change your mind and want to change the NID, simply click the 'Change NID' link."
}
```

### Retrieved Chunk 2
- Chunk ID: `1`
- Document name: `New e-GP Manual PDF`
- Source type: `manual`
- Page number: `1`
- Screenshot/image: `data/structured/images/page_01_image_01.jpeg`
- Relevance score: `0.47`
- Retrieved excerpt:

Page 1 Manual for Tenderers, Consultants, Government Owned Enterprise, Media On Registration Process For the e-GP System (https://eprocure.gov.bd) Bangladesh Public Procurement Authority (BPPA) IMED, Ministry of Planning Government of the People's Re...

- Source metadata:

```json
{
  "source": "New e-GP Manual PDF",
  "page": 1,
  "chunk_id": 1,
  "score": 0.47,
  "snippet": "Page 1 Manual for Tenderers, Consultants, Government Owned Enterprise, Media On Registration Process For the e-GP System (https://eprocure.gov.bd) Bangladesh Public Procurement Authority (BPPA) IMED, Ministry of Planning Government of the People's Re...",
  "image_path": "data/structured/images/page_01_image_01.jpeg",
  "related_sentence": "Page 1 Manual for Tenderers, Consultants, Government Owned Enterprise, Media On Registration Process For the e-GP System (https://eprocure.gov.bd) Bangladesh Public Procurement Authority (BPPA) IMED, Ministry of Planning Government of the People's Republic of Bangladesh BPPA Bhaban, Planning Commission Campus Sher-e-Bangla Nagar, Dhaka-1207, Bangladesh Phone: +88 02 48119400-1 | Fax: +88 02 9180968 Email: info@bppa.gov.bd | Web: www.bppa.gov.bd e-GP Help Desk Contact Details Phone: 16575, +8809677016575 | Email: helpdesk@eprocure.gov.bd Date: March 03, 2026"
}
```

## 5. Source References

- Retrieved source: `New e-GP Manual PDF`, page `14`, chunk `14`, image `data/structured/images/page_14_image_02.jpeg`.
- Retrieved source: `New e-GP Manual PDF`, page `1`, chunk `1`, image `data/structured/images/page_01_image_01.jpeg`.

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
- Retrieval completion: Completed; 2 source(s) retrieved
- LLM generation status: Completed using openai/gpt-oss-20b
- Citation formatting status: Completed; 2 citation(s) formatted
- Total processing time: `12.65 seconds`
- Errors or warnings: `Not Available`
