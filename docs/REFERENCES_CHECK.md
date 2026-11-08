# Reference verification table (2026-11-08, overnight; all pages fetched on that date)

Rule (execution plan, review #12): no reference enters the manuscript unless its bibliographic fields were read from the
publisher / ACL Anthology / arXiv / proceedings page, and no paper is cited for a detail that was not read in its abstract or body.
"Cited for" states the only use the manuscript makes of each reference.

| key | verified at | fields checked | cited for | notes / corrections |
|---|---|---|---|---|
| elyaniv2010foundations | jmlr.org/papers/v11/el-yaniv10a.html | authors, title, JMLR 11(53):1605–1641, 2010 | definition of the risk–coverage trade-off (reject option) | added on review #12 |
| geifman2017selective | nips.cc poster 9264; mlanthology (pp. 4878–4887) | authors, title, NeurIPS 2017, pages | selective classification with a confidence threshold on deep networks | — |
| jones2021selective | arxiv.org/abs/2010.14134v3; ICLR 2021 listing | authors, title, arXiv id; venue ICLR 2021 | selective classification can magnify accuracy disparities between groups; group-conditional analysis | novelty positioning: our contribution is the transfer of an MSA-calibrated policy to dialectal phrasings of the same items, its adaptation and the paired evaluation — not the disparity phenomenon itself |
| kamath2020selective | aclanthology.org/2020.acl-main.503 | authors, title, ACL 2020 pp. 5684–5696, DOI | selective QA under domain shift: softmax confidence abstains poorly out of domain; a trained calibrator helps | cited for the domain-shift framing only |
| traub2024overcoming | proceedings.neurips.cc (NeurIPS 2024 main track) | authors, title, venue | AUGRC definition ("average risk of undetected failures") | — |
| vovk2005algorithmic | link.springer.com/10.1007/b106715 | authors, title, Springer 2005, DOI | conformal prediction, exchangeability | — |
| vovk2012conditional | proceedings.mlr.press/v25/vovk12.html | author, title, ACML 2012, PMLR 25:475–490 | conditional (group/label-conditional, "Mondrian") validity of inductive conformal predictors | — |
| angelopoulos2023conformal | mlanthology (FnT ML 16(4):494–591, DOI 10.1561/2200000101) | authors, title, journal, volume, pages, DOI | split-conformal recipe and the ⌈(n+1)(1−α)⌉ quantile; marginal coverage under exchangeability | issue number inferred from the PDF path (16/4) |
| guo2017calibration | proceedings.mlr.press/v70/guo17a.html | authors, title, ICML 2017, PMLR 70:1321–1330 | ECE definition (Appendix D, S3) | — |
| zheng2024robust | arxiv.org/abs/2309.03882v4; iclr.cc poster 17638 | authors, title, arXiv id; venue ICLR 2024 | option-order sensitivity / token bias toward option IDs | — |
| pezeshkpour2024sensitivity | aclanthology.org/2024.findings-naacl.130.bib | authors, title, Findings NAACL 2024 pp. 2006–2017, DOI | option-order sensitivity of LLMs in MCQ | — |
| wang2024myanswer | aclanthology.org/2024.findings-acl.441.bib | full BibTeX | first-token probabilities vs text answers in instruction-tuned models | motivates the G1/G2 generation checks |
| robinson2023leveraging | arxiv.org/abs/2210.12353; iclr.cc poster 10737 | authors, title, arXiv id; venue ICLR 2023 | option-letter ("multiple choice prompting") scoring of MCQ | — |
| zheng2023judging | proceedings.neurips.cc (NeurIPS 2023 D&B) | authors, title, venue | known biases of LLM judges (position, verbosity, self-enhancement) — limits of the model-assisted screen | — |
| altakrori2026dialectalarabicmmlu | arxiv.org/abs/2510.27543v1 + html body; ACL Anthology ingest preview 2026.lrec-main.251 (LREC 2026, pp. 3199–3219) | authors (order per LREC listing), title, venue, pages, arXiv id | DialectalArabicMMLU resource: 3,135 items × {MSA, EGY, SYR, KSA, UAE, MAG, ENG}; manual translation by a language-service provider with translator/reviewer/adjudicator per dialect; 32-item Likert check per dialect, "about 5% of the translations contained some inaccuracies"; UAE and SYR had a second review round; extends MMLU-Redux | **CORRECTIONS to v0.2:** v0.2 cited this as "Robinson et al., 2025" and said it extends ArabicMMLU — wrong on both counts. The resource's label MAG denotes the **Moroccan** dialect; v0.3 writes "Moroccan (MAG)". The LREC canonical URL should be re-checked before submission (preview host). |
| mousi2025aradice | aclanthology.org/2025.coling-main.283 | authors, title, COLING 2025 pp. 4186–4218 | AraDiCE: machine translation with human post-editing; EGY/LEV versions of ArabicMMLU items (dataset QCRI/AraDiCE) | the EGY/LEV ArabicMMLU subsets are those used in L4 (data/aradice_items.json) |
| koto2024arabicmmlu | aclanthology.org/2024.findings-acl.334 | authors, title, Findings ACL 2024 pp. 5622–5640, DOI | ArabicMMLU (MSA originals paired with AraDiCE) | — |
| gema2025mmluredux | aclanthology.org/2025.naacl-long.262 | first authors, title, NAACL 2025 pp. 5069–5096, DOI | MMLU-Redux, the source DialectalArabicMMLU extends | 16 authors; "and others" in the .bib |
| hendrycks2021mmlu | arxiv.org/abs/2009.03300; ICLR 2021 | authors, title, venue | MMLU origin of the items | — |
| allaith2025calibration | aclanthology.org/2025.wacl-1.8 | authors, title, WACL-4 2025 pp. 68–76 | calibration (ECE) of eight pre-trained models on Arabic dialect identification varies substantially across dialects | the related-work sentence: that work concerns the calibration of dialect classifiers, not the transfer of an answer policy across parallel phrasings |
| ifm2026verified | HF dataset card not reachable from this workspace (client error); description taken from ANALYSIS_PLAN Addendum 4 §L1 as recorded when the file was downloaded (2026-11-06) | id, counts (935; EGY 180, KSA 175, MAG 195, SYR 184, UAE 201), judge rule | external three-judge filter (L1) | **RE-CHECK the dataset card (judge models, license, citation request) before submission** |
| bari2025allam | proceedings.iclr.cc (ICLR 2025, pp. 34179–34214) | authors, title, venue, pages | ALLaM-7B-Instruct-preview | arXiv id 2407.15390 from the search listing |
| fanar2025 | arxiv.org/abs/2501.13944v1 + PDF body | title, team authorship, arXiv id; model description | Fanar-1-9B (= Fanar Prime, ≈9B) | **NEW FACT for the manuscript:** Fanar Prime "uses continual pre-training to build upon the Gemma-2-9B base model" — so Fanar-1-9B and gemma-2-9b share a base; the four checkpoints come from three base families (ALLaM, Qwen3, Gemma-2 ⟶ Fanar). Stated in Methods and Limitations of v0.3. |
| qwen3 | arxiv.org/abs/2505.09388 (listing) | title, team authorship, arXiv id | Qwen3-8B-Base | — |
| gemma2 | arxiv.org/abs/2408.00118 (listing) | title, team authorship, arXiv id | gemma-2-9b | — |
| wang2024multilinguale5 | arxiv.org/abs/2402.05672 (listing) | authors, title, arXiv id | multilingual-e5-large (L2 similarity covariate) | — |
| nosek2018preregistration | bibbase record (PNAS 115(11):2600–2606, DOI 10.1073/pnas.1708274114) | authors, title, journal, volume, pages, DOI | pre-specification / registration framing | PMC page blocked by a browser check; fields from the bibbase record |
| efron1993bootstrap | library records (Chapman & Hall 1993, Monographs 57) | authors, title, publisher, year | percentile bootstrap intervals | — |
| cohen1960kappa | scilit / GESIS records | author, title, journal 20(1):37–46, 1960 | κ for the screen's within-model consistency | — |

## Entries added for manuscript v0.4 (expanded Related Work), verified 2026-11-08

| key | verified on | fields confirmed | cited for | note |
|---|---|---|---|---|
| ahuja2022calibration | aclanthology.org/2022.emnlp-main.290 | authors, title, EMNLP 2022 pp. 4310–4323, DOI | calibration of massively multilingual models under zero-shot transfer: poor on low-resource / typologically distant languages; a few target-language examples reduce it | wording in §2 and §5.1 matched to the abstract (not "degrades on lower-resource languages" in general) |
| tibshirani2019conformal | papers.nips.cc/paper/8522 | authors, title, NeurIPS 2019 | conformal prediction under covariate shift (weighted exchangeability) | pages 2530–2540 from the proceedings listing |
| barber2023conformal | arxiv.org/abs/2202.13415; Annals record (pp. 816–845, DOI 10.1214/23-AOS2276) | authors, title, journal, pages, DOI | coverage under departures from exchangeability | projecteuclid page blocked by a bot check; fields from the arXiv page and an indexing record |
| romano2020malice | DOAJ record (HDSR, MIT Press, 2020-04-01, DOI 10.1162/99608f92.03f00592) | authors, title, journal, year, DOI | equalised coverage across groups as a fairness requirement | volume/issue 2(2) from the HDSR listing |
| kadavath2022language | arxiv.org/abs/2207.05221 | first authors, title, arXiv id | token-level self-knowledge / P(True) | "and others" in the .bib (long author list) |
| xiong2024can | arxiv.org/abs/2306.13063 (v2); ICLR 2024 listing | authors, title, arXiv id | verbalised confidence elicitation | venue ICLR 2024 from the conference listing |
| kuhn2023semantic | iclr.cc/virtual/2023/poster/11013 | authors, title, ICLR 2023 | semantic uncertainty over sampled answers | — |
| varshney2022investigating | aclanthology.org/2022.findings-acl.158 | authors, title, Findings ACL 2022 pp. 1995–2002, DOI | selective prediction across tasks and shifts | — |
| chen2023adaptation | aclanthology.org/2023.findings-emnlp.345 | authors, title, Findings EMNLP 2023 pp. 5190–5213, DOI | selective prediction in LLMs (self-evaluation) | — |
| wen2025know | TACL 13:529–556 PDF (Anthology ingest); arxiv.org/abs/2407.18418 | authors, title, journal, volume, pages, DOI | survey of abstention policies and failure modes | — |
| lee2021fair | proceedings.mlr.press/v139/lee21b.html | authors, title, ICML 2021, PMLR 139:6076–6086 | selective classification under fairness constraints | — |
| shah2022selective | proceedings.mlr.press/v162/shah22a.html | authors, title, ICML 2022, PMLR 162:19598–19615 | selective **regression** under fairness criteria | §2 wording changed to "selective classification and regression under explicit fairness constraints" |
| kumar2023conformal | arxiv.org/abs/2305.18404 | authors, title, workshop note | conformal prediction for LLM multiple choice | ICML 2023 TEACH workshop (per the paper) |
| ye2024benchmarking | papers.neurips.cc (NeurIPS 2024 D&B) | authors, title, venue | conformal sets for LLM benchmarks (MCQA) | — |
| quach2024conformal | proceedings.iclr.cc (ICLR 2024) | authors, title, venue, pages | conformal guarantees for generation | pages from the proceedings metadata |
| mohri2024conformal | proceedings.mlr.press/v235/mohri24a.html | authors, title, ICML 2024, PMLR 235:36029–36047 | conformal factuality for generation | — |
| su2024api | aclanthology.org/2024.findings-emnlp.54 | authors, title, Findings EMNLP 2024 pp. 979–995, DOI | conformal prediction without logit access | — |
| campos2024conformal | aclanthology.org/2024.tacl-1.82 | authors, title, TACL 12:1497–1516, DOI | survey of conformal prediction in NLP | — |
| ziems2022value | aclanthology.org/2022.acl-long.258 | authors, title, ACL 2022 pp. 3701–3720, DOI | dialect disparity in NLU via transformation rules (English) | — |
| ziems2023multivalue | aclanthology.org/2023.acl-long.44 | authors, title, ACL 2023 pp. 744–768, DOI | cross-dialectal English framework | — |
| kantharuban2023quantifying | aclanthology.org/2023.findings-emnlp.481 | authors, title, Findings EMNLP 2023 pp. 7226–7245, DOI | dialect gap across languages and its economic, social and linguistic correlates | §5.1 wording: "among economic and social factors, with the linguistic distance" |
| faisal2024dialectbench | aclanthology.org/2024.acl-long.777 | authors, title, ACL 2024 pp. 14412–14454, DOI; abstract: 281 varieties | dialectal benchmark aggregation | Arabic is not named on the Anthology page, so the clause "Arabic among them" was removed from §2 |
| hofmann2024dialect | indexing record (Nature, 2024-09-05, pp. 147–, DOI 10.1038/s41586-024-07856-5) | authors, title, journal, year, DOI | dialect-conditioned judgements as a harm | volume/issue 633(8028), pp. 147–154 from the journal listing; PMC blocked by a browser check |
| bouamor2018madar | aclanthology.org/L18-1535 | 11 authors, title, LREC 2018, Miyazaki, ELRA | parallel dialectal corpus (background) | — |
| abdulmageed2021nadi | aclanthology.org/2021.wanlp-1.28 | authors, title, WANLP 2021 pp. 244–259 | dialect-identification shared task (background) | no DOI on the Anthology page |
| keleg2023aldi | aclanthology.org/2023.emnlp-main.655 | authors, title, EMNLP 2023 pp. 10597–10611, DOI | continuous level-of-dialectness measure | — |
| huang2024acegpt | aclanthology.org/2024.naacl-long.450 | 19 authors, title, NAACL 2024 pp. 8139–8163, DOI | Arabic-centric model evaluation incl. dialects | venue is NAACL 2024 (not EMNLP) |
| abdelali2024larabench | aclanthology.org/2024.eacl-long.30 | 17 authors, title, EACL 2024 pp. 487–520, DOI | LLM benchmarking on Arabic incl. dialectal tasks | — |
| robinson2025alqasida | aclanthology.org/2025.findings-acl.1137 | authors, title, Findings ACL 2025 pp. 22048–22065, DOI | LLM quality on eight Arabic dialects: comprehension better than generation | — |
| holtzman2021surface | aclanthology.org/2021.emnlp-main.564 | authors, title, EMNLP 2021 pp. 7038–7051, DOI | surface-form competition | — |
| alzahrani2024benchmarks | aclanthology.org/2024.acl-long.744 | 12 authors, title, ACL 2024 pp. 13787–13805, DOI | leaderboard sensitivity to option order / format | — |
| lyu2024beyond | aclanthology.org/2024.knowllm-1.10 | authors, title, KnowLLM 2024 pp. 109–131, DOI | probability-based vs generation-based evaluation disagree | workshop paper |
| balepur2024artifacts | aclanthology.org/2024.acl-long.555 | authors, title, ACL 2024 pp. 10308–10330, DOI | MCQ items answerable without the question | — |
| artetxe2020translation | aclanthology.org/2020.emnlp-main.618 | authors, title, EMNLP 2020 pp. 7674–7684, DOI | translation artefacts in cross-lingual evaluation | — |
| singh2024global | aclanthology.org/2025.acl-long.919 | 23 authors, title, ACL 2025 pp. 18761–18799, DOI | errors and cultural mismatch in translated MMLU variants | key keeps the arXiv year (2024); published ACL 2025 |
| chiang2023can | aclanthology.org/2023.acl-long.870 | authors, title, ACL 2023 pp. 15607–15631, DOI | LLMs as evaluators (limits) | — |
| koehn2004statistical | aclanthology.org/W04-3250 | author, title, EMNLP 2004 pp. 388–395 | paired bootstrap resampling in NLP evaluation | — |
| dror2018hitchhiker | aclanthology.org/P18-1128 | authors, title, ACL 2018 pp. 1383–1392, DOI | significance testing practice in NLP | — |
| vanmiltenburg2021preregistering | aclanthology.org/2021.naacl-main.51 (XML) | authors, title, NAACL 2021 pp. 613–623, DOI | pre-registration in NLP | — |

Cite-key check (2026-11-08): 68 keys cited in `paper/manuscript_v0.4.md`, 68 entries in `paper/references.bib`, no key missing and none unused.
