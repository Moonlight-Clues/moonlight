# Night watch P3: how strong is the proof behind "approved"?

Read-only study. Open Targets only, data release 26.09. Asked 2026-11-17T13:29:29Z to 2026-11-17T13:39:55Z (UTC). No file in moonlight/, web/ or tests/ was changed. Moonlight's site and Gemini were not called.

Everything below is counted by `analyse.py` and `report.py` from the raw answers saved in `responses/`. No id and no number was typed by hand.

## The short answer

- 124 diseases were studied. Together they have 2096 items on Moonlight's Approved list today.
- 1372 of those items (65.5%) have at least one approval report from DailyMed, FDA or EMA (group A). 724 (34.5%) do not (groups B to F).
- **100 of the 124 diseases** have at least one item outside group A. Kashish predicted **fewer than 15**.
- This says how strong the attached proof is. It does not say any item is right or wrong.

## Words used in this report

- **Item**: a medicine and its forms together, Kashish's rule. The item's id is the parent medicine's id.
- **Approved item**: an item Moonlight counts as approved for the disease today. That is `fetch.py`'s test, which `engine.py` uses for the Approved tab: one of the item's rows on the disease's own list has `maxClinicalStage` = `APPROVAL`, and that form's own `maximumClinicalStage` is `APPROVAL` too. The test does not look at the reports at all.
- **On the Approved list today**: an approved item that Moonlight does not leave out as withdrawn. Moonlight leaves an item out when one of its forms carries a `Withdrawn` drug warning. That is a different field from a report whose `clinicalStage` is `WITHDRAWAL`.
- **Approval report**: one entry of `clinicalReports` whose `clinicalStage` is `APPROVAL`.
- The main numbers count the items **on the Approved list today**. A second column also counts the approved items Moonlight already leaves out as withdrawn.
- Moonlight's own `fetch_approved` and `fetch_withdrawn` were run on every saved answer, offline, and gave exactly the same items as this study for every disease.

## 1. Diseases asked, found and skipped

| Set | Asked | Found (in the study) | Skipped |
|---|---|---|---|
| All diseases | 149 | 124 | 25 |
| Common | 30 | 23 | 7 |
| Cancer | 20 | 15 | 5 |
| Rare | 40 | 36 | 4 |
| Agent's choice | 59 | 50 | 9 |

A name is **found** only if a search hit has exactly that name (capitals ignored). Nothing was matched by hand, so some very common diseases were skipped because Open Targets files them under another name.

### Skipped names in the three given sets

| Set | Name asked | Why skipped | First three hits Open Targets gave instead |
|---|---|---|---|
| Common | hypertension | no hit with exactly this name | hypertensive disorder (MONDO_0005044); pulmonary arterial hypertension (MONDO_0015924); essential hypertension, genetic (MONDO_0007781) |
| Common | migraine | no hit with exactly this name | migraine disorder (MONDO_0005277); familial or sporadic hemiplegic migraine (MONDO_0018925); hemiplegic migraine-developmental and epileptic encephalopathy spectrum (MONDO_0100539) |
| Common | Crohn's disease | no hit with exactly this name | Crohn disease (MONDO_0005011); inflammatory bowel disease (MONDO_0005265); Crohn's colitis (MONDO_0005532) |
| Common | multiple sclerosis | no hit with exactly this name | multiple sclerosis symptom measurement (EFO_0803536); chronic progressive multiple sclerosis (MONDO_0005284); relapsing-remitting multiple sclerosis (MONDO_0005314) |
| Common | HIV infection | no hit with exactly this name | HIV infectious disease (MONDO_0005109); HIV-1 infection (EFO_0000180); HIV-associated neurocognitive disorder (EFO_0007948) |
| Common | hepatitis B | no hit with exactly this name | hepatitis B virus infection (MONDO_0005344) |
| Common | hepatitis C | no hit with exactly this name | hepatitis C virus infection (MONDO_0005231) |
| Cancer | multiple myeloma | no hit with exactly this name | plasma cell myeloma (MONDO_0009693); smoldering plasma cell myeloma (MONDO_0005235); ovarian endometrioid adenocarcinoma with squamous differentiation (MONDO_0006336) |
| Cancer | chronic lymphocytic leukemia | no hit with exactly this name | B-cell chronic lymphocytic leukemia (MONDO_0004948); chronic leukemia (MONDO_0001014); lymphoid leukemia (MONDO_0005402) |
| Cancer | Hodgkin lymphoma | no hit with exactly this name | Hodgkins lymphoma (MONDO_0004952); classic Hodgkin lymphoma (MONDO_0009348); nodular sclerosis classical Hodgkin lymphoma (MONDO_0004665) |
| Cancer | pancreatic cancer | no hit with exactly this name | pancreatic neoplasm (MONDO_0021040); exocrine pancreatic carcinoma (MONDO_0005192); malignant pancreatic neoplasm (MONDO_0009831) |
| Cancer | bladder cancer | no hit with exactly this name | urinary bladder carcinoma (MONDO_0004986); urinary bladder cancer (MONDO_0001187); bladder urachal carcinoma (MONDO_0003715) |
| Rare | Pompe disease | no hit with exactly this name | glycogen storage disease II (MONDO_0009290); muscular disease (EFO_0002970); carbohydrate metabolism disease (MONDO_0037792) |
| Rare | sickle cell anemia | no hit with exactly this name | sickle cell disease (MONDO_0011382); sickle cell-hemoglobin c disease syndrome (MONDO_0016669); sickle cell-beta-thalassemia disease syndrome (MONDO_0016668) |
| Rare | beta-thalassemia | no hit with exactly this name | beta thalassemia (MONDO_0019402) |
| Rare | immune thrombocytopenia | no hit with exactly this name | autoimmune thrombocytopenic purpura (MONDO_0008558); immune system disorder (MONDO_0005046); Abnormality of the immune system (HP_0002715) |

### Agent's choice: how the 50 were chosen

Before any answer was seen, the agent wrote a pool of everyday disease names it believed have an approved medicine, in 14 body-system groups (the list is in `probe.py`). The names were tried one group after another, round and round, so the set is spread out. A name was taken only if (1) Open Targets has exactly that name, (2) it is not already in the study, and (3) its answer holds at least one approved item. The first 50 taken are the set. Because of test (3), no disease in this set can have an empty approved list, which the other three sets can.

Taken per body system: heart and blood vessels 5, lungs and airways 4, stomach, gut and liver 4, kidney and bladder 4, hormones and metabolism 3, brain and nerves 3, mind 3, eye and ear 3, skin 4, bones, joints and muscles 4, blood 3, infections 4, women's and men's health 2, more cancers 4.

Candidates not taken:

| Name | Body system | Why not taken |
|---|---|---|
| obesity | hormones and metabolism | no hit with exactly this name |
| attention deficit hyperactivity disorder | mind | no hit with exactly this name |
| uterine fibroid | women's and men's health | no hit with exactly this name |
| influenza | lungs and airways | no hit with exactly this name |
| constipation | stomach, gut and liver | no hit with exactly this name |
| essential tremor | brain and nerves | exact name found, but no approved item on its list |
| allergic conjunctivitis | eye and ear | no hit with exactly this name |
| polycythemia vera | blood | no hit with exactly this name |
| pre-eclampsia | women's and men's health | no hit with exactly this name |
| nephrotic syndrome | kidney and bladder | not tried: 50 were already taken |
| growth hormone deficiency | hormones and metabolism | not tried: 50 were already taken |
| trigeminal neuralgia | brain and nerves | not tried: 50 were already taken |
| post-traumatic stress disorder | mind | not tried: 50 were already taken |
| diabetic retinopathy | eye and ear | not tried: 50 were already taken |
| seborrheic dermatitis | skin | not tried: 50 were already taken |
| Paget's disease of bone | bones, joints and muscles | not tried: 50 were already taken |
| myelofibrosis | blood | not tried: 50 were already taken |
| Lyme disease | infections | not tried: 50 were already taken |
| hypogonadism | women's and men's health | not tried: 50 were already taken |
| follicular lymphoma | more cancers | not tried: 50 were already taken |
| stroke | heart and blood vessels | not tried: 50 were already taken |
| pancreatitis | stomach, gut and liver | not tried: 50 were already taken |
| urinary incontinence | kidney and bladder | not tried: 50 were already taken |
| familial hypercholesterolemia | hormones and metabolism | not tried: 50 were already taken |
| cluster headache | brain and nerves | not tried: 50 were already taken |
| alcohol dependence | mind | not tried: 50 were already taken |
| Meniere disease | eye and ear | not tried: 50 were already taken |
| pemphigus vulgaris | skin | not tried: 50 were already taken |
| polymyalgia rheumatica | bones, joints and muscles | not tried: 50 were already taken |
| aplastic anemia | blood | not tried: 50 were already taken |
| schistosomiasis | infections | not tried: 50 were already taken |
| menopause | women's and men's health | not tried: 50 were already taken |
| mesothelioma | more cancers | not tried: 50 were already taken |
| onchocerciasis | infections | not tried: 50 were already taken |
| cytomegalovirus infection | infections | not tried: 50 were already taken |

### The diseases in the study

| Set | Disease | Id | Items on its list | Approved items | On the Approved list today | Times asked |
|---|---|---|---|---|---|---|
| Common | asthma | MONDO_0004979 | 392 | 74 | 70 | 2 |
| Common | type 2 diabetes mellitus | MONDO_0005148 | 582 | 60 | 59 | 2 |
| Common | epilepsy | MONDO_0005027 | 133 | 56 | 54 | 2 |
| Common | rheumatoid arthritis | MONDO_0008383 | 437 | 72 | 69 | 2 |
| Common | psoriasis | MONDO_0005083 | 190 | 45 | 43 | 2 |
| Common | atopic eczema | MONDO_0004980 | 231 | 41 | 41 | 2 |
| Common | ulcerative colitis | MONDO_0005101 | 232 | 28 | 28 | 2 |
| Common | osteoporosis | MONDO_0005298 | 111 | 34 | 33 | 2 |
| Common | gout | MONDO_0005393 | 61 | 24 | 21 | 2 |
| Common | heart failure | MONDO_0005252 | 295 | 43 | 43 | 2 |
| Common | atrial fibrillation | MONDO_0004981 | 124 | 18 | 17 | 2 |
| Common | chronic obstructive pulmonary disease | MONDO_0005002 | 306 | 31 | 29 | 2 |
| Common | chronic kidney disease | MONDO_0005300 | 334 | 51 | 51 | 2 |
| Common | hypothyroidism | MONDO_0005420 | 16 | 8 | 8 | 2 |
| Common | depressive disorder | MONDO_0002050 | 279 | 39 | 33 | 2 |
| Common | schizophrenia | MONDO_0005090 | 319 | 48 | 45 | 2 |
| Common | bipolar disorder | MONDO_0004985 | 158 | 19 | 19 | 2 |
| Common | Parkinson disease | MONDO_0005180 | 309 | 45 | 43 | 2 |
| Common | Alzheimer disease | MONDO_0004975 | 417 | 21 | 21 | 2 |
| Common | glaucoma | MONDO_0005041 | 84 | 40 | 39 | 2 |
| Common | endometriosis | MONDO_0005133 | 84 | 10 | 10 | 2 |
| Common | tuberculosis | MONDO_0018076 | 128 | 22 | 22 | 2 |
| Common | malaria | MONDO_0005136 | 90 | 30 | 29 | 2 |
| Cancer | breast cancer | MONDO_0007254 | 983 | 74 | 73 | 2 |
| Cancer | prostate cancer | MONDO_0008315 | 717 | 30 | 30 | 2 |
| Cancer | colorectal cancer | MONDO_0005575 | 722 | 19 | 19 | 2 |
| Cancer | lung cancer | MONDO_0008903 | 253 | 8 | 8 | 2 |
| Cancer | melanoma | MONDO_0005105 | 571 | 20 | 20 | 2 |
| Cancer | chronic myeloid leukemia | MONDO_0011996 | 166 | 9 | 9 | 2 |
| Cancer | acute myeloid leukemia | MONDO_0018874 | 554 | 16 | 15 | 2 |
| Cancer | acute lymphoblastic leukemia | MONDO_0004967 | 287 | 15 | 15 | 2 |
| Cancer | ovarian cancer | MONDO_0008170 | 545 | 14 | 13 | 2 |
| Cancer | glioblastoma | MONDO_0018177 | 432 | 3 | 3 | 2 |
| Cancer | hepatocellular carcinoma | MONDO_0007256 | 450 | 8 | 8 | 2 |
| Cancer | renal cell carcinoma | MONDO_0005086 | 328 | 16 | 16 | 2 |
| Cancer | thyroid cancer | MONDO_0002108 | 88 | 5 | 5 | 2 |
| Cancer | neuroblastoma | MONDO_0005072 | 165 | 5 | 5 | 2 |
| Cancer | osteosarcoma | MONDO_0009807 | 133 | 3 | 3 | 2 |
| Rare | cystic fibrosis | MONDO_0009061 | 142 | 15 | 15 | 2 |
| Rare | Duchenne muscular dystrophy | MONDO_0010679 | 60 | 8 | 8 | 2 |
| Rare | spinal muscular atrophy | MONDO_0001516 | 20 | 4 | 4 | 2 |
| Rare | Huntington disease | MONDO_0007739 | 56 | 5 | 5 | 2 |
| Rare | amyotrophic lateral sclerosis | MONDO_0004976 | 177 | 5 | 5 | 2 |
| Rare | Gaucher disease | MONDO_0018150 | 12 | 6 | 6 | 2 |
| Rare | Fabry disease | MONDO_0010526 | 17 | 4 | 4 | 2 |
| Rare | phenylketonuria | MONDO_0009861 | 7 | 3 | 3 | 2 |
| Rare | hemophilia A | MONDO_0010602 | 42 | 18 | 18 | 2 |
| Rare | hemophilia B | MONDO_0010604 | 23 | 11 | 11 | 2 |
| Rare | myasthenia gravis | MONDO_0009688 | 73 | 12 | 12 | 2 |
| Rare | narcolepsy | MONDO_0021107 | 16 | 5 | 5 | 2 |
| Rare | Wilson disease | MONDO_0010200 | 12 | 4 | 4 | 2 |
| Rare | hereditary angioedema | MONDO_0019623 | 16 | 9 | 9 | 2 |
| Rare | acromegaly | MONDO_0019933 | 21 | 6 | 6 | 2 |
| Rare | Cushing syndrome | MONDO_0018912 | 13 | 4 | 3 | 2 |
| Rare | sarcoidosis | MONDO_0019338 | 44 | 5 | 5 | 2 |
| Rare | systemic sclerosis | MONDO_0005100 | 110 | 4 | 4 | 2 |
| Rare | Behcet disease | MONDO_0007191 | 40 | 2 | 2 | 2 |
| Rare | hidradenitis suppurativa | MONDO_0006559 | 76 | 1 | 1 | 2 |
| Rare | idiopathic pulmonary fibrosis | EFO_0000768 | 129 | 4 | 4 | 2 |
| Rare | pulmonary arterial hypertension | MONDO_0015924 | 109 | 14 | 13 | 2 |
| Rare | amyloidosis | MONDO_0019065 | 51 | 5 | 5 | 2 |
| Rare | Friedreich ataxia | MONDO_0100339 | 25 | 2 | 2 | 2 |
| Rare | Rett syndrome | MONDO_0010726 | 21 | 1 | 1 | 2 |
| Rare | Dravet syndrome | MONDO_0100135 | 10 | 3 | 2 | 2 |
| Rare | tuberous sclerosis | MONDO_0001734 | 12 | 2 | 2 | 2 |
| Rare | neurofibromatosis type 1 | MONDO_0018975 | 38 | 2 | 2 | 2 |
| Rare | retinitis pigmentosa | MONDO_0019200 | 31 | 1 | 1 | 2 |
| Rare | achondroplasia | MONDO_0007037 | 6 | 1 | 1 | 2 |
| Rare | osteogenesis imperfecta | MONDO_0019019 | 17 | 1 | 1 | 2 |
| Rare | paroxysmal nocturnal hemoglobinuria | MONDO_0100244 | 31 | 6 | 6 | 2 |
| Rare | systemic lupus erythematosus | MONDO_0007915 | 203 | 8 | 8 | 2 |
| Rare | ankylosing spondylitis | MONDO_0005306 | 64 | 19 | 19 | 2 |
| Rare | vitiligo | MONDO_0008661 | 61 | 3 | 3 | 2 |
| Rare | alopecia areata | MONDO_0005340 | 69 | 2 | 2 | 2 |
| Agent's choice | angina pectoris | EFO_0003913 | 99 | 33 | 32 | 2 |
| Agent's choice | allergic rhinitis | MONDO_0011786 | 111 | 45 | 44 | 2 |
| Agent's choice | gastroesophageal reflux disease | MONDO_0007186 | 88 | 39 | 36 | 2 |
| Agent's choice | overactive bladder | MONDO_0006624 | 69 | 12 | 12 | 2 |
| Agent's choice | type 1 diabetes mellitus | MONDO_0005147 | 302 | 7 | 7 | 2 |
| Agent's choice | insomnia | MONDO_0013600 | 111 | 38 | 31 | 2 |
| Agent's choice | anxiety disorder | MONDO_0005618 | 125 | 39 | 35 | 2 |
| Agent's choice | age-related macular degeneration | MONDO_0005150 | 126 | 1 | 1 | 2 |
| Agent's choice | acne | MONDO_0011438 | 129 | 53 | 51 | 2 |
| Agent's choice | osteoarthritis | MONDO_0005178 | 200 | 49 | 45 | 2 |
| Agent's choice | Iron deficiency anemia | HP_0001891 | 54 | 31 | 31 | 2 |
| Agent's choice | herpes zoster | MONDO_0005609 | 29 | 5 | 5 | 2 |
| Agent's choice | polycystic ovary syndrome | MONDO_0008487 | 114 | 2 | 2 | 2 |
| Agent's choice | basal cell carcinoma | MONDO_0020804 | 54 | 6 | 6 | 2 |
| Agent's choice | myocardial infarction | MONDO_0005068 | 227 | 49 | 49 | 2 |
| Agent's choice | pneumonia | MONDO_0005249 | 183 | 47 | 47 | 2 |
| Agent's choice | irritable bowel syndrome | MONDO_0005052 | 109 | 20 | 18 | 2 |
| Agent's choice | benign prostatic hyperplasia | MONDO_0010811 | 58 | 11 | 11 | 2 |
| Agent's choice | restless legs syndrome | MONDO_0005391 | 45 | 5 | 5 | 2 |
| Agent's choice | dry eye syndrome | MONDO_0006733 | 88 | 5 | 5 | 2 |
| Agent's choice | rosacea | MONDO_0006604 | 45 | 10 | 10 | 2 |
| Agent's choice | psoriatic arthritis | MONDO_0011849 | 76 | 25 | 25 | 2 |
| Agent's choice | neutropenia | MONDO_0001475 | 67 | 4 | 4 | 2 |
| Agent's choice | candidiasis | MONDO_0002026 | 34 | 18 | 18 | 2 |
| Agent's choice | gastric cancer | MONDO_0001056 | 361 | 11 | 11 | 2 |
| Agent's choice | deep vein thrombosis | EFO_0003907 | 45 | 13 | 13 | 2 |
| Agent's choice | peptic ulcer disease | MONDO_0004247 | 73 | 54 | 53 | 2 |
| Agent's choice | urinary tract infection | MONDO_0100338 | 90 | 51 | 50 | 2 |
| Agent's choice | hyperthyroidism | MONDO_0004425 | 12 | 5 | 5 | 2 |
| Agent's choice | neuropathic pain | EFO_0005762 | 148 | 5 | 5 | 2 |
| Agent's choice | obsessive-compulsive disorder | MONDO_0008114 | 62 | 5 | 5 | 2 |
| Agent's choice | uveitis | MONDO_0020283 | 60 | 6 | 6 | 2 |
| Agent's choice | urticaria | MONDO_0005492 | 34 | 18 | 17 | 2 |
| Agent's choice | fibromyalgia | MONDO_0005546 | 95 | 8 | 8 | 2 |
| Agent's choice | venous thromboembolism | MONDO_0005399 | 31 | 9 | 9 | 2 |
| Agent's choice | leprosy | MONDO_0005124 | 4 | 3 | 3 | 2 |
| Agent's choice | Infertility | HP_0000789 | 107 | 6 | 5 | 2 |
| Agent's choice | cervical cancer | MONDO_0002974 | 225 | 6 | 6 | 2 |
| Agent's choice | Hypercholesterolemia | HP_0003124 | 83 | 22 | 22 | 2 |
| Agent's choice | COVID-19 | MONDO_0100096 | 525 | 1 | 1 | 2 |
| Agent's choice | erectile dysfunction | MONDO_0005362 | 66 | 11 | 10 | 2 |
| Agent's choice | Graves disease | MONDO_0005364 | 24 | 2 | 2 | 2 |
| Agent's choice | panic disorder | MONDO_0005383 | 31 | 5 | 5 | 2 |
| Agent's choice | actinic keratosis | MONDO_0005173 | 29 | 5 | 4 | 2 |
| Agent's choice | juvenile idiopathic arthritis | MONDO_0011429 | 51 | 24 | 24 | 2 |
| Agent's choice | toxoplasmosis | MONDO_0005989 | 8 | 3 | 3 | 2 |
| Agent's choice | mantle cell lymphoma | MONDO_0018876 | 182 | 11 | 11 | 2 |
| Agent's choice | pulmonary embolism | MONDO_0005279 | 40 | 13 | 13 | 2 |
| Agent's choice | bronchiectasis | MONDO_0004822 | 34 | 2 | 2 | 2 |
| Agent's choice | primary biliary cholangitis | MONDO_0005388 | 50 | 3 | 2 | 2 |

Each list was asked twice, as `fetch.py` does. For all 124 diseases the two answers were exactly the same, so no third ask was needed.

One more answer is saved in `responses/` and is not in the study: essential tremor (MONDO_0003233), an agent's-choice candidate whose list held no approved item.

## 2. Every distinct `source` value

Counted over every report of every row in the saved answers (a report on two forms' rows is counted twice here).

| source | Reports | of them APPROVAL | of them WITHDRAWAL | Other stages | One example link |
|---|---|---|---|---|---|
| `ClinicalTrials.gov` | 93970 | 75 | 0 | EARLY_PHASE_1 1211, PHASE_1 12201, PHASE_1_2 8001, PHASE_2 33232, PHASE_2_3 2528, PHASE_3 19736, PHASE_4 5006, UNKNOWN 11980 | https://clinicaltrials.gov/study/NCT02059434 |
| `DailyMed` | 11196 | 11196 | 0 | - | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=0016c77a-64fa-45a1-8721-4fd3a826a885 |
| `TTD` | 3775 | 911 | 28 | EARLY_PHASE_1 1, IND 115, PHASE_1 487, PHASE_1_2 144, PHASE_2 1293, PHASE_2_3 56, PHASE_3 557, PHASE_4 5, PREAPPROVAL 31, PRECLINICAL 50, UNKNOWN 97 | https://ttd.idrblab.cn/data/drug/details/D07FUP |
| `EMA Human Drugs` | 1280 | 954 | 208 | PREAPPROVAL 13, UNKNOWN 105 | https://www.ema.europa.eu/en/medicines/human/EPAR/dupixent |
| `PMDA` | 603 | 603 | 0 | - | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html |
| `USAN` | 426 | 0 | 0 | UNKNOWN 426 | https://searchusan.ama-assn.org/finder/usan/search/VEREKITUG/relevant/1/ |
| `ATC` | 362 | 362 | 0 | - | https://www.whocc.no/atc_ddd_index/?code=N03AC02 |
| `FDA` | 218 | 218 | 0 | - | http://www.accessdata.fda.gov/drugsatfda_docs/label/2010/021959s004lbl.pdf |
| `INN` | 25 | 0 | 0 | UNKNOWN 25 | https://www.who.int/publications/m/item/inn-pl-127 |

How the values were matched to the names in the task: `DailyMed`, `FDA` and `EMA Human Drugs` are group A's three. `TTD`, `PMDA` and `ATC` are matched only when the value is exactly that word. Every other value goes to group F and is named there.

Values the briefing did not name: `ClinicalTrials.gov` (75 of its reports are APPROVAL), `USAN` (0 of its reports are APPROVAL), `INN` (0 of its reports are APPROVAL). `ClinicalTrials.gov` is a list of trials, yet a few of its reports carry the stage `APPROVAL`. An item whose only approval reports are those is in group F.

## 3. Approved items by group

- **A**: at least one approval report from DailyMed, FDA or EMA
- **B**: approval reports only from TTD
- **C**: approval reports only from PMDA
- **D**: approval reports only from ATC
- **E**: no APPROVAL report at all
- **F**: anything else

### All diseases

| Group | On the Approved list today | Share | Also counting those left out as withdrawn | Share |
|---|---|---|---|---|
| A | 1372 | 65.5% | 1387 | 64.1% |
| B | 378 | 18.0% | 405 | 18.7% |
| C | 109 | 5.2% | 109 | 5.0% |
| D | 140 | 6.7% | 147 | 6.8% |
| E | 20 | 1.0% | 34 | 1.6% |
| F | 77 | 3.7% | 83 | 3.8% |
| Total | 2096 | 100.0% | 2165 | 100.0% |

### Common

| Group | On the Approved list today | Share | Also counting those left out as withdrawn | Share |
|---|---|---|---|---|
| A | 532 | 64.3% | 537 | 62.5% |
| B | 129 | 15.6% | 142 | 16.5% |
| C | 44 | 5.3% | 44 | 5.1% |
| D | 66 | 8.0% | 69 | 8.0% |
| E | 8 | 1.0% | 15 | 1.7% |
| F | 48 | 5.8% | 52 | 6.1% |
| Total | 827 | 100.0% | 859 | 100.0% |

### Cancer

| Group | On the Approved list today | Share | Also counting those left out as withdrawn | Share |
|---|---|---|---|---|
| A | 153 | 63.2% | 154 | 62.9% |
| B | 67 | 27.7% | 67 | 27.3% |
| C | 9 | 3.7% | 9 | 3.7% |
| D | 0 | 0.0% | 0 | 0.0% |
| E | 3 | 1.2% | 5 | 2.0% |
| F | 10 | 4.1% | 10 | 4.1% |
| Total | 242 | 100.0% | 245 | 100.0% |

### Rare

| Group | On the Approved list today | Share | Also counting those left out as withdrawn | Share |
|---|---|---|---|---|
| A | 168 | 83.2% | 169 | 82.4% |
| B | 19 | 9.4% | 19 | 9.3% |
| C | 7 | 3.5% | 7 | 3.4% |
| D | 0 | 0.0% | 0 | 0.0% |
| E | 5 | 2.5% | 6 | 2.9% |
| F | 3 | 1.5% | 4 | 2.0% |
| Total | 202 | 100.0% | 205 | 100.0% |

### Agent's choice

| Group | On the Approved list today | Share | Also counting those left out as withdrawn | Share |
|---|---|---|---|---|
| A | 519 | 62.9% | 527 | 61.6% |
| B | 163 | 19.8% | 177 | 20.7% |
| C | 49 | 5.9% | 49 | 5.7% |
| D | 74 | 9.0% | 78 | 9.1% |
| E | 4 | 0.5% | 8 | 0.9% |
| F | 16 | 1.9% | 17 | 2.0% |
| Total | 825 | 100.0% | 856 | 100.0% |

Group F, which sources (all approved items): `ATC + TTD` 45, `PMDA + TTD` 12, `ClinicalTrials.gov` 10, `ATC + PMDA` 8, `ATC + PMDA + TTD` 3, `ClinicalTrials.gov + PMDA` 3, `ATC + ClinicalTrials.gov` 1, `ClinicalTrials.gov + PMDA + TTD` 1.

Group E, a closer look (all 34 approved items): 29 have a WITHDRAWAL report, 2 have no report of any kind on their rows, and 3 have only trial or `PREAPPROVAL` reports. For every one of them the row's stage word still says `APPROVAL`.

## 4. Diseases with at least one approved item outside group A

Kashish predicted: **fewer than 15**.

| Set | Diseases in the study | With an item outside A on the Approved list today | Also counting items left out as withdrawn | Kashish's prediction |
|---|---|---|---|---|
| All diseases | 124 | 100 | 100 | fewer than 15 |
| Common | 23 | 23 | 23 |  |
| Cancer | 15 | 11 | 11 |  |
| Rare | 36 | 22 | 22 |  |
| Agent's choice | 50 | 44 | 44 |  |

The diseases, counting only items on the Approved list today:

| Set | Disease | Id | On the Approved list today | Outside A | Which groups |
|---|---|---|---|---|---|
| Common | asthma | MONDO_0004979 | 70 | 20 | B 19, E 1 |
| Common | type 2 diabetes mellitus | MONDO_0005148 | 59 | 10 | B 2, C 6, F 2 |
| Common | epilepsy | MONDO_0005027 | 54 | 32 | B 3, C 1, D 13, F 15 |
| Common | rheumatoid arthritis | MONDO_0008383 | 69 | 14 | B 11, C 2, F 1 |
| Common | psoriasis | MONDO_0005083 | 43 | 7 | D 7 |
| Common | atopic eczema | MONDO_0004980 | 41 | 17 | B 2, C 12, D 2, F 1 |
| Common | ulcerative colitis | MONDO_0005101 | 28 | 2 | B 1, C 1 |
| Common | osteoporosis | MONDO_0005298 | 33 | 16 | B 12, C 4 |
| Common | gout | MONDO_0005393 | 21 | 7 | C 2, D 4, F 1 |
| Common | heart failure | MONDO_0005252 | 43 | 10 | B 9, F 1 |
| Common | atrial fibrillation | MONDO_0004981 | 17 | 3 | B 3 |
| Common | chronic obstructive pulmonary disease | MONDO_0005002 | 29 | 7 | B 7 |
| Common | chronic kidney disease | MONDO_0005300 | 51 | 5 | B 1, C 2, E 2 |
| Common | hypothyroidism | MONDO_0005420 | 8 | 2 | B 2 |
| Common | depressive disorder | MONDO_0002050 | 33 | 29 | B 23, C 2, E 1, F 3 |
| Common | schizophrenia | MONDO_0005090 | 45 | 20 | B 16, C 1, E 3 |
| Common | bipolar disorder | MONDO_0004985 | 19 | 3 | B 2, E 1 |
| Common | Parkinson disease | MONDO_0005180 | 43 | 24 | B 4, C 2, D 10, F 8 |
| Common | Alzheimer disease | MONDO_0004975 | 21 | 9 | B 5, C 4 |
| Common | glaucoma | MONDO_0005041 | 39 | 28 | C 1, D 21, F 6 |
| Common | endometriosis | MONDO_0005133 | 10 | 5 | B 1, C 3, F 1 |
| Common | tuberculosis | MONDO_0018076 | 22 | 11 | D 8, F 3 |
| Common | malaria | MONDO_0005136 | 29 | 14 | B 6, C 1, D 1, F 6 |
| Cancer | breast cancer | MONDO_0007254 | 73 | 35 | B 27, C 5, E 1, F 2 |
| Cancer | prostate cancer | MONDO_0008315 | 30 | 14 | B 11, C 1, E 1, F 1 |
| Cancer | colorectal cancer | MONDO_0005575 | 19 | 15 | B 11, C 2, F 2 |
| Cancer | lung cancer | MONDO_0008903 | 8 | 3 | B 3 |
| Cancer | melanoma | MONDO_0005105 | 20 | 4 | B 4 |
| Cancer | chronic myeloid leukemia | MONDO_0011996 | 9 | 1 | E 1 |
| Cancer | acute lymphoblastic leukemia | MONDO_0004967 | 15 | 1 | B 1 |
| Cancer | ovarian cancer | MONDO_0008170 | 13 | 7 | B 6, F 1 |
| Cancer | hepatocellular carcinoma | MONDO_0007256 | 8 | 5 | C 1, F 4 |
| Cancer | renal cell carcinoma | MONDO_0005086 | 16 | 2 | B 2 |
| Cancer | thyroid cancer | MONDO_0002108 | 5 | 2 | B 2 |
| Rare | cystic fibrosis | MONDO_0009061 | 15 | 1 | B 1 |
| Rare | Duchenne muscular dystrophy | MONDO_0010679 | 8 | 1 | E 1 |
| Rare | spinal muscular atrophy | MONDO_0001516 | 4 | 1 | B 1 |
| Rare | Huntington disease | MONDO_0007739 | 5 | 4 | C 4 |
| Rare | amyotrophic lateral sclerosis | MONDO_0004976 | 5 | 2 | C 1, F 1 |
| Rare | Gaucher disease | MONDO_0018150 | 6 | 1 | B 1 |
| Rare | hemophilia B | MONDO_0010604 | 11 | 2 | E 2 |
| Rare | myasthenia gravis | MONDO_0009688 | 12 | 2 | B 2 |
| Rare | narcolepsy | MONDO_0021107 | 5 | 2 | B 1, F 1 |
| Rare | hereditary angioedema | MONDO_0019623 | 9 | 1 | B 1 |
| Rare | sarcoidosis | MONDO_0019338 | 5 | 1 | B 1 |
| Rare | systemic sclerosis | MONDO_0005100 | 4 | 1 | B 1 |
| Rare | Behcet disease | MONDO_0007191 | 2 | 1 | B 1 |
| Rare | idiopathic pulmonary fibrosis | EFO_0000768 | 4 | 1 | B 1 |
| Rare | pulmonary arterial hypertension | MONDO_0015924 | 13 | 1 | C 1 |
| Rare | amyloidosis | MONDO_0019065 | 5 | 2 | B 2 |
| Rare | Friedreich ataxia | MONDO_0100339 | 2 | 2 | E 2 |
| Rare | Dravet syndrome | MONDO_0100135 | 2 | 2 | B 1, F 1 |
| Rare | osteogenesis imperfecta | MONDO_0019019 | 1 | 1 | B 1 |
| Rare | systemic lupus erythematosus | MONDO_0007915 | 8 | 1 | C 1 |
| Rare | ankylosing spondylitis | MONDO_0005306 | 19 | 2 | B 2 |
| Rare | vitiligo | MONDO_0008661 | 3 | 2 | B 2 |
| Agent's choice | angina pectoris | EFO_0003913 | 32 | 17 | B 12, C 5 |
| Agent's choice | allergic rhinitis | MONDO_0011786 | 44 | 20 | B 15, C 4, F 1 |
| Agent's choice | gastroesophageal reflux disease | MONDO_0007186 | 36 | 29 | D 28, F 1 |
| Agent's choice | overactive bladder | MONDO_0006624 | 12 | 3 | B 2, C 1 |
| Agent's choice | type 1 diabetes mellitus | MONDO_0005147 | 7 | 3 | B 1, E 1, F 1 |
| Agent's choice | insomnia | MONDO_0013600 | 31 | 17 | B 17 |
| Agent's choice | anxiety disorder | MONDO_0005618 | 35 | 20 | B 20 |
| Agent's choice | age-related macular degeneration | MONDO_0005150 | 1 | 1 | B 1 |
| Agent's choice | acne | MONDO_0011438 | 51 | 27 | B 10, C 1, D 12, F 4 |
| Agent's choice | osteoarthritis | MONDO_0005178 | 45 | 10 | B 7, C 3 |
| Agent's choice | Iron deficiency anemia | HP_0001891 | 31 | 6 | B 6 |
| Agent's choice | herpes zoster | MONDO_0005609 | 5 | 2 | B 1, C 1 |
| Agent's choice | polycystic ovary syndrome | MONDO_0008487 | 2 | 1 | B 1 |
| Agent's choice | myocardial infarction | MONDO_0005068 | 49 | 8 | B 6, C 1, E 1 |
| Agent's choice | pneumonia | MONDO_0005249 | 47 | 7 | C 7 |
| Agent's choice | irritable bowel syndrome | MONDO_0005052 | 18 | 12 | B 11, C 1 |
| Agent's choice | benign prostatic hyperplasia | MONDO_0010811 | 11 | 3 | B 1, D 2 |
| Agent's choice | dry eye syndrome | MONDO_0006733 | 5 | 1 | C 1 |
| Agent's choice | rosacea | MONDO_0006604 | 10 | 3 | B 3 |
| Agent's choice | psoriatic arthritis | MONDO_0011849 | 25 | 1 | C 1 |
| Agent's choice | neutropenia | MONDO_0001475 | 4 | 1 | B 1 |
| Agent's choice | candidiasis | MONDO_0002026 | 18 | 4 | B 3, C 1 |
| Agent's choice | gastric cancer | MONDO_0001056 | 11 | 11 | B 2, C 9 |
| Agent's choice | deep vein thrombosis | EFO_0003907 | 13 | 3 | B 3 |
| Agent's choice | peptic ulcer disease | MONDO_0004247 | 53 | 40 | B 8, D 27, F 5 |
| Agent's choice | urinary tract infection | MONDO_0100338 | 50 | 12 | B 10, E 2 |
| Agent's choice | hyperthyroidism | MONDO_0004425 | 5 | 2 | B 2 |
| Agent's choice | uveitis | MONDO_0020283 | 6 | 1 | B 1 |
| Agent's choice | urticaria | MONDO_0005492 | 17 | 3 | C 3 |
| Agent's choice | fibromyalgia | MONDO_0005546 | 8 | 4 | B 4 |
| Agent's choice | venous thromboembolism | MONDO_0005399 | 9 | 2 | C 2 |
| Agent's choice | leprosy | MONDO_0005124 | 3 | 3 | D 3 |
| Agent's choice | Infertility | HP_0000789 | 5 | 4 | B 2, C 2 |
| Agent's choice | cervical cancer | MONDO_0002974 | 6 | 3 | B 2, C 1 |
| Agent's choice | Hypercholesterolemia | HP_0003124 | 22 | 2 | C 2 |
| Agent's choice | erectile dysfunction | MONDO_0005362 | 10 | 5 | B 1, D 2, F 2 |
| Agent's choice | Graves disease | MONDO_0005364 | 2 | 2 | B 2 |
| Agent's choice | panic disorder | MONDO_0005383 | 5 | 1 | B 1 |
| Agent's choice | juvenile idiopathic arthritis | MONDO_0011429 | 24 | 1 | C 1 |
| Agent's choice | toxoplasmosis | MONDO_0005989 | 3 | 2 | B 1, C 1 |
| Agent's choice | mantle cell lymphoma | MONDO_0018876 | 11 | 3 | C 1, F 2 |
| Agent's choice | pulmonary embolism | MONDO_0005279 | 13 | 3 | B 3 |
| Agent's choice | bronchiectasis | MONDO_0004822 | 2 | 1 | B 1 |
| Agent's choice | primary biliary cholangitis | MONDO_0005388 | 2 | 2 | B 2 |

## 5. Every approved item in groups B, C, D, E and F (the main result)

The full list holds 778 items and is not shortened. It is long, so it is printed **at the end of this file**, after section 9. Nothing else was moved.

## 6. Every approved item with a WITHDRAWAL report

136 approved items have at least one report whose `clinicalStage` is `WITHDRAWAL`. Moonlight leaves out 17 of them today and shows 119. Moonlight decides from the `Withdrawn` drug warning, not from these reports.

In these answers no row's own stage word (`maxClinicalStage`) is ever `WITHDRAWAL`. Every item that has a WITHDRAWAL report passes Moonlight's approved test: 0 items with a WITHDRAWAL report are not approved items.

| Set | Disease | Medicine | Group | Moonlight leaves it out today | Its WITHDRAWAL reports |
|---|---|---|---|---|---|
| Common | asthma (MONDO_0004979) | FLUTICASONE PROPIONATE (CHEMBL1473) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/aerivio-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/airexar-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/bropair-spiromax |
| Common | asthma (MONDO_0004979) | FORMOTEROL (CHEMBL1256786) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/budesonide-formoterol-teva-pharma-bv<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/budesonide-formoterol-teva<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/vylaer-spiromax |
| Common | asthma (MONDO_0004979) | SALMETEROL (CHEMBL1263) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/airexar-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/aerivio-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/bropair-spiromax |
| Common | asthma (MONDO_0004979) | BITOLTEROL (CHEMBL1201295) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D06RUL |
| Common | asthma (MONDO_0004979) | BUDESONIDE (CHEMBL1370) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/budesonide-formoterol-teva<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/vylaer-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/budesonide-formoterol-teva-pharma-bv |
| Common | type 2 diabetes mellitus (MONDO_0005148) | PIOGLITAZONE (CHEMBL595) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/glustin<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/glubrava<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/sepioglin<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pioglitazone-teva<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/paglitaz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pioglitazone-teva-pharma<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pioglitazone-krka<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/glidipion |
| Common | type 2 diabetes mellitus (MONDO_0005148) | SITAGLIPTIN (CHEMBL1422) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/sitagliptin-metformin-hydrochloride-accord |
| Common | type 2 diabetes mellitus (MONDO_0005148) | ALBIGLUTIDE (CHEMBL2107841) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/eperzan |
| Common | type 2 diabetes mellitus (MONDO_0005148) | ROSIGLITAZONE (CHEMBL121) | A | yes | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/avandia<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/nyracta<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/venvia<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/avandamet<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/avaglim |
| Common | type 2 diabetes mellitus (MONDO_0005148) | LIXISENATIDE (CHEMBL2108336) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/lyxumia |
| Common | type 2 diabetes mellitus (MONDO_0005148) | METFORMIN (CHEMBL1431) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/qtrilmet<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/sitagliptin-metformin-hydrochloride-accord<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/avandamet<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/glubrava |
| Common | type 2 diabetes mellitus (MONDO_0005148) | GLIMEPIRIDE (CHEMBL1481) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/avaglim |
| Common | type 2 diabetes mellitus (MONDO_0005148) | DAPAGLIFLOZIN (CHEMBL429910) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/qtrilmet |
| Common | type 2 diabetes mellitus (MONDO_0005148) | SAXAGLIPTIN ANHYDROUS (CHEMBL385517) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/qtrilmet |
| Common | type 2 diabetes mellitus (MONDO_0005148) | NATEGLINIDE (CHEMBL783) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/starlix<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/trazec |
| Common | epilepsy (MONDO_0005027) | ESLICARBAZEPINE ACETATE (CHEMBL87992) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/exalief |
| Common | epilepsy (MONDO_0005027) | EZOGABINE (CHEMBL41355) | D | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0X7GL<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/trobalt |
| Common | epilepsy (MONDO_0005027) | PREGABALIN (CHEMBL1059) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pregabalin-mylan-pharma<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pregabalin-sandoz-gmbh<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pregabalin-zentiva-ks |
| Common | rheumatoid arthritis (MONDO_0008383) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/trudexa<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/solymbic<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/halimatoz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kromeya |
| Common | rheumatoid arthritis (MONDO_0008383) | LEFLUNOMIDE (CHEMBL960) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/repso<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/leflunomide-teva |
| Common | rheumatoid arthritis (MONDO_0008383) | VALDECOXIB (CHEMBL865) | E | yes | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/bextra<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn-0 |
| Common | psoriasis (MONDO_0005083) | USTEKINUMAB (CHEMBL1201835) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/eksunbi |
| Common | psoriasis (MONDO_0005083) | EFALIZUMAB (CHEMBL1201575) | E | yes | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/raptiva |
| Common | psoriasis (MONDO_0005083) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/solymbic<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/halimatoz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kromeya |
| Common | psoriasis (MONDO_0005083) | ETANERCEPT (CHEMBL1201572) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/lifmior |
| Common | atopic eczema (MONDO_0004980) | CRISABOROLE (CHEMBL484785) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/staquis |
| Common | atopic eczema (MONDO_0004980) | TACROLIMUS ANHYDROUS (CHEMBL269732) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/protopy |
| Common | ulcerative colitis (MONDO_0005101) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/solymbic<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kromeya |
| Common | ulcerative colitis (MONDO_0005101) | USTEKINUMAB (CHEMBL1201835) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/eksunbi<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/absimky |
| Common | osteoporosis (MONDO_0005298) | TERIPARATIDE (CHEMBL525610) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/qutavina |
| Common | osteoporosis (MONDO_0005298) | ZOLEDRONIC ACID ANHYDROUS (CHEMBL924) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/zoledronic-acid-teva-pharma<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/zoledronic-acid-teva-generics |
| Common | gout (MONDO_0005393) | PEGLOTICASE (CHEMBL1237025) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/krystexxa |
| Common | gout (MONDO_0005393) | INDOPROFEN (CHEMBL15870) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D0Q5PL |
| Common | gout (MONDO_0005393) | LESINURAD (CHEMBL2105720) | D | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/duzallo |
| Common | gout (MONDO_0005393) | ALLOPURINOL (CHEMBL1467) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/duzallo |
| Common | heart failure (MONDO_0005252) | IVABRADINE (CHEMBL471737) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/ivabradine-jensonr |
| Common | atrial fibrillation (MONDO_0004981) | DOFETILIDE (CHEMBL473) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/tikosyn |
| Common | atrial fibrillation (MONDO_0004981) | DRONEDARONE (CHEMBL184412) | A | no | TTD: https://ttd.idrblab.cn/data/drug/details/D05CPV |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | FORMOTEROL (CHEMBL1256786) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/budesonide-formoterol-teva<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/vylaer-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/riarify |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | BECLOMETHASONE (CHEMBL1586) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/riarify |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | SALMETEROL (CHEMBL1263) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/aerivio-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/airexar-spiromax |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | UMECLIDINIUM (CHEMBL1187833) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/temybric-ellipta |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | ROFLUMILAST (CHEMBL193240) | A | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0R4UW<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/daliresp<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/libertek |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | BUDESONIDE (CHEMBL1370) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/budesonide-formoterol-teva<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/vylaer-spiromax |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | FLUTICASONE PROPIONATE (CHEMBL1473) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/aerivio-spiromax<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/airexar-spiromax |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | BECLOMETHASONE DIPROPIONATE (CHEMBL1200500) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/riarify |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | VILANTEROL (CHEMBL1198857) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/temybric-ellipta |
| Common | chronic obstructive pulmonary disease (MONDO_0005002) | FLUTICASONE FUROATE (CHEMBL1676) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/temybric-ellipta |
| Common | chronic kidney disease (MONDO_0005300) | DARBEPOETIN ALFA (CHEMBL1201566) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/nespo |
| Common | chronic kidney disease (MONDO_0005300) | EPOETIN DELTA (CHEMBL2109093) | E | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/dynepo |
| Common | chronic kidney disease (MONDO_0005300) | FERUMOXYTOL (CHEMBL1201867) | B | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/rienso |
| Common | depressive disorder (MONDO_0002050) | NEFAZODONE (CHEMBL623) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D0X7DE |
| Common | depressive disorder (MONDO_0002050) | BENACTYZINE (CHEMBL70352) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D07KYU |
| Common | depressive disorder (MONDO_0002050) | ZIMELDINE (CHEMBL37744) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D0C1XS |
| Common | schizophrenia (MONDO_0005090) | OLANZAPINE (CHEMBL715) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/olansek<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/olanzapine-cipla<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/olanzapine-apotex |
| Common | schizophrenia (MONDO_0005090) | CHLORPROMAZINE (CHEMBL71) | A | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0V6GN |
| Common | schizophrenia (MONDO_0005090) | TRIFLUPROMAZINE (CHEMBL570) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0DG0P |
| Common | schizophrenia (MONDO_0005090) | REMOXIPRIDE (CHEMBL22242) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D01PIL |
| Common | schizophrenia (MONDO_0005090) | CARPHENAZINE (CHEMBL1201328) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D01QML |
| Common | schizophrenia (MONDO_0005090) | SERTINDOLE (CHEMBL12713) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D0OS6O |
| Common | schizophrenia (MONDO_0005090) | FLUPENTIXOL (CHEMBL6066864) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0OC3J |
| Common | bipolar disorder (MONDO_0004985) | OLANZAPINE (CHEMBL715) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/olansek<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/olanzapine-cipla<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/olanzapine-apotex |
| Common | Parkinson disease (MONDO_0005180) | RIVASTIGMINE (CHEMBL636) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/rivastigmine-teva |
| Common | Parkinson disease (MONDO_0005180) | PRAMIPEXOLE (CHEMBL301265) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/daquiran<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pramipexole-accord |
| Common | Parkinson disease (MONDO_0005180) | CARBIDOPA ANHYDROUS (CHEMBL1201236) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/numient |
| Common | Parkinson disease (MONDO_0005180) | ROTIGOTINE (CHEMBL1303) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/leganto |
| Common | Parkinson disease (MONDO_0005180) | OPICAPONE (CHEMBL1089318) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/ontilyv |
| Common | Parkinson disease (MONDO_0005180) | LEVODOPA (CHEMBL1009) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/numient |
| Common | Alzheimer disease (MONDO_0004975) | MEMANTINE (CHEMBL807) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/memantine-lek |
| Common | Alzheimer disease (MONDO_0004975) | RIVASTIGMINE (CHEMBL636) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/rivastigmine-teva<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/rivastigmine-3m-health-care-ltd |
| Common | tuberculosis (MONDO_0018076) | AMINOSALICYLIC ACID (CHEMBL1169) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/granupas |
| Common | malaria (MONDO_0005136) | CHLOROQUINE (CHEMBL76) | A | no | TTD: https://ttd.idrblab.cn/data/drug/details/D07QYQ |
| Common | malaria (MONDO_0005136) | AMODIAQUINE (CHEMBL682) | F | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0YQ9P |
| Cancer | breast cancer (MONDO_0007254) | FORMESTANE (CHEMBL132530) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0B6PZ |
| Cancer | breast cancer (MONDO_0007254) | NOMIFENSINE (CHEMBL273575) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D06BPG |
| Cancer | prostate cancer (MONDO_0008315) | ATRASENTAN (CHEMBL9194) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0Y6UU |
| Cancer | melanoma (MONDO_0005105) | INTERFERON ALFA-2B (CHEMBL1201558) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/introna |
| Cancer | chronic myeloid leukemia (MONDO_0011996) | INTERFERON ALFA-2B (CHEMBL1201558) | E | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/introna |
| Cancer | chronic myeloid leukemia (MONDO_0011996) | DASATINIB ANHYDROUS (CHEMBL1421) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/dasatinib-accordpharma<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/dasatinib-accord |
| Cancer | chronic myeloid leukemia (MONDO_0011996) | IMATINIB (CHEMBL941) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/imatinib-actavis<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/imatinib-medac<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/imatinib-teva-bv<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/imatinib-koanaa |
| Cancer | acute myeloid leukemia (MONDO_0018874) | AZACITIDINE (CHEMBL1489) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/azacitidine-celgene |
| Cancer | ovarian cancer (MONDO_0008170) | MIBEFRADIL (CHEMBL45816) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D0W8XT |
| Cancer | renal cell carcinoma (MONDO_0005086) | BEVACIZUMAB (CHEMBL1201583) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/equidacent<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/lextemy<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/onbevzi |
| Cancer | neuroblastoma (MONDO_0005072) | DINUTUXIMAB (CHEMBL3137342) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/unituxin |
| Rare | cystic fibrosis (MONDO_0009061) | TOBRAMYCIN (CHEMBL1747) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/vantobra |
| Rare | Duchenne muscular dystrophy (MONDO_0010679) | ATALUREN (CHEMBL256997) | E | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/translarna |
| Rare | hemophilia A (MONDO_0010602) | OCTOCOG ALFA (CHEMBL4297873) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kogenate-bayer<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/helixate-nexgen<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/iblias |
| Rare | hemophilia B (MONDO_0010604) | COAGULATION FACTOR IX HUMAN (CHEMBL4297986) | E | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/nonafact |
| Rare | hemophilia B (MONDO_0010604) | FIDANACOGENE ELAPARVOVEC (CHEMBL3990034) | E | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/beqvez |
| Rare | acromegaly (MONDO_0019933) | OCTREOTIDE (CHEMBL1680) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/mycapssa |
| Rare | hidradenitis suppurativa (MONDO_0006559) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/solymbic<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/halimatoz |
| Rare | pulmonary arterial hypertension (MONDO_0015924) | SITAXENTAN (CHEMBL282724) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D02EAS<br>TTD: https://ttd.idrblab.cn/data/drug/details/D0T1RG |
| Rare | ankylosing spondylitis (MONDO_0005306) | ETANERCEPT (CHEMBL1201572) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/lifmior |
| Rare | ankylosing spondylitis (MONDO_0005306) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/trudexa<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/solymbic<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/halimatoz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kromeya |
| Agent's choice | angina pectoris (EFO_0003913) | IVABRADINE (CHEMBL471737) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/ivabradine-jensonr |
| Agent's choice | allergic rhinitis (MONDO_0011786) | ASTEMIZOLE (CHEMBL296419) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D0Y2HR |
| Agent's choice | gastroesophageal reflux disease (MONDO_0007186) | TEGASEROD (CHEMBL76370) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D00XWD |
| Agent's choice | gastroesophageal reflux disease (MONDO_0007186) | PANTOPRAZOLE (CHEMBL1502) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pantecta-control<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pantoloc-control |
| Agent's choice | type 1 diabetes mellitus (MONDO_0005147) | SOTAGLIFLOZIN (CHEMBL3039507) | E | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/zynquista |
| Agent's choice | insomnia (MONDO_0013600) | METHAQUALONE (CHEMBL282052) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D0T7XI |
| Agent's choice | anxiety disorder (MONDO_0005618) | DULOXETINE (CHEMBL1175) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/nodetrip |
| Agent's choice | anxiety disorder (MONDO_0005618) | PREGABALIN (CHEMBL1059) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pregabalin-mylan-pharma<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pregabalin-sandoz-gmbh<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pregabalin-zentiva-ks |
| Agent's choice | osteoarthritis (MONDO_0005178) | ISOXICAM (CHEMBL53292) | E | yes | TTD: https://ttd.idrblab.cn/data/drug/details/D03JPH |
| Agent's choice | osteoarthritis (MONDO_0005178) | VALDECOXIB (CHEMBL865) | B | yes | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/bextra<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn-0 |
| Agent's choice | myocardial infarction (MONDO_0005068) | ASPIRIN (CHEMBL25) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-acetylsalicylic-acid-teva |
| Agent's choice | myocardial infarction (MONDO_0005068) | RETEPLASE (CHEMBL2107885) | B | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/rapilysin<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/ecokinase |
| Agent's choice | myocardial infarction (MONDO_0005068) | EPTIFIBATIDE (CHEMBL1174) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/integrilin |
| Agent's choice | myocardial infarction (MONDO_0005068) | FONDAPARINUX (CHEMBL1201202) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/quixidar |
| Agent's choice | myocardial infarction (MONDO_0005068) | VORAPAXAR (CHEMBL493982) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/zontivity |
| Agent's choice | myocardial infarction (MONDO_0005068) | CLOPIDOGREL (CHEMBL1771) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-bms<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-dura<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-teva-pharma-0<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-qualimed<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-hexal<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-ratiopharm-gmbh<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-acino<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-acino-pharma<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-ratiopharm-0<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-sandoz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-acino-pharma-gmbh<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-teva-pharma-bv<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-teva-generics-bv<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/clopidogrel-acetylsalicylic-acid-teva |
| Agent's choice | myocardial infarction (MONDO_0005068) | TENECTEPLASE (CHEMBL2108791) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/tenecteplase-boehringer-ingelheim-pharma-gmbh-co-kg |
| Agent's choice | pneumonia (MONDO_0005249) | TELITHROMYCIN (CHEMBL1136) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/levviax |
| Agent's choice | irritable bowel syndrome (MONDO_0005052) | ELUXADOLINE (CHEMBL2159122) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/truberzi |
| Agent's choice | restless legs syndrome (MONDO_0005391) | PRAMIPEXOLE (CHEMBL301265) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/pramipexole-accord |
| Agent's choice | restless legs syndrome (MONDO_0005391) | ROTIGOTINE (CHEMBL1303) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/leganto |
| Agent's choice | psoriatic arthritis (MONDO_0011849) | USTEKINUMAB (CHEMBL1201835) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/eksunbi |
| Agent's choice | psoriatic arthritis (MONDO_0011849) | LEFLUNOMIDE (CHEMBL960) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/repso |
| Agent's choice | psoriatic arthritis (MONDO_0011849) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/trudexa<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/solymbic<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/halimatoz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kromeya |
| Agent's choice | psoriatic arthritis (MONDO_0011849) | ETANERCEPT (CHEMBL1201572) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/lifmior |
| Agent's choice | candidiasis (MONDO_0002026) | CASPOFUNGIN (CHEMBL1630575) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/caspofungin-accord |
| Agent's choice | candidiasis (MONDO_0002026) | POSACONAZOLE (CHEMBL1397) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/posaconazole-sp |
| Agent's choice | urinary tract infection (MONDO_0100338) | SULFALENE (CHEMBL1525826) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D0F0OK |
| Agent's choice | urinary tract infection (MONDO_0100338) | PIDOTIMOD (CHEMBL1488165) | E | no | TTD: https://ttd.idrblab.cn/data/drug/details/D04YCE |
| Agent's choice | urinary tract infection (MONDO_0100338) | DORIPENEM (CHEMBL491571) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/doribax |
| Agent's choice | uveitis (MONDO_0020283) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/halimatoz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kromeya |
| Agent's choice | urticaria (MONDO_0005492) | DESLORATADINE (CHEMBL1172) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/opulis<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/allex |
| Agent's choice | venous thromboembolism (MONDO_0005399) | ENOXAPARIN SODIUM (CHEMBL1201476) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/thorinane |
| Agent's choice | Infertility (HP_0000789) | FOLLITROPIN BETA (CHEMBL5315126) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/fertavid |
| Agent's choice | cervical cancer (MONDO_0002974) | TOPOTECAN (CHEMBL84) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/topotecan-actavis<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/topotecan-teva |
| Agent's choice | cervical cancer (MONDO_0002974) | BEVACIZUMAB (CHEMBL1201583) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/lextemy<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/onbevzi |
| Agent's choice | erectile dysfunction (MONDO_0005362) | SILDENAFIL (CHEMBL192) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/patrex |
| Agent's choice | erectile dysfunction (MONDO_0005362) | VARDENAFIL (CHEMBL1520) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/vivanza |
| Agent's choice | erectile dysfunction (MONDO_0005362) | APOMORPHINE (CHEMBL53) | D | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/uprima<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/ixense<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/taluvian |
| Agent's choice | actinic keratosis (MONDO_0005173) | INGENOL MEBUTATE (CHEMBL1863513) | A | yes | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/picato |
| Agent's choice | juvenile idiopathic arthritis (MONDO_0011429) | ADALIMUMAB (CHEMBL1201580) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/cyltezo<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/halimatoz<br>EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/kromeya |
| Agent's choice | pulmonary embolism (MONDO_0005279) | FONDAPARINUX (CHEMBL1201202) | A | no | EMA Human Drugs: https://www.ema.europa.eu/en/medicines/human/EPAR/quixidar |

The other way round: 52 approved items are left out today as withdrawn (drug warning) and have **no** WITHDRAWAL report on this disease's list. They are in `items.json` (`left_out_as_withdrawn_today` true, `has_withdrawal_report` false).

Approved items Moonlight leaves out today as withdrawn, by group:

| Set | Left out as withdrawn | A | B | C | D | E | F |
|---|---|---|---|---|---|---|---|
| All diseases | 69 | 15 | 27 | 0 | 7 | 14 | 6 |
| Common | 32 | 5 | 13 | 0 | 3 | 7 | 4 |
| Cancer | 3 | 1 | 0 | 0 | 0 | 2 | 0 |
| Rare | 3 | 1 | 0 | 0 | 0 | 1 | 1 |
| Agent's choice | 31 | 8 | 14 | 0 | 4 | 4 | 1 |

## 7. Counts for Kashish's two possible rules

**Rule 1**: approved items with no DailyMed, FDA or EMA approval report (groups B to F). The second pair of columns counts PMDA as a regulator too, so an item with a PMDA approval report is no longer counted.

| Set | On the Approved list today | Rule 1 | Rule 1, PMDA is a regulator | Also counting left out as withdrawn | Rule 1 | Rule 1, PMDA is a regulator |
|---|---|---|---|---|---|---|
| All diseases | 2096 | 724 (34.5%) | 590 (28.1%) | 2165 | 778 (35.9%) | 642 (29.7%) |
| Common | 827 | 295 (35.7%) | 236 (28.5%) | 859 | 322 (37.5%) | 262 (30.5%) |
| Cancer | 242 | 89 (36.8%) | 75 (31.0%) | 245 | 91 (37.1%) | 77 (31.4%) |
| Rare | 202 | 34 (16.8%) | 25 (12.4%) | 205 | 36 (17.6%) | 26 (12.7%) |
| Agent's choice | 825 | 306 (37.1%) | 254 (30.8%) | 856 | 329 (38.4%) | 277 (32.4%) |

**Rule 2**: items with a WITHDRAWAL report and no APPROVAL report. Counted two ways: among approved items (these are all in group E), and among the items on the lists that Moonlight does not count as approved for the disease anyway.

| Set | Rule 2, approved items | of them on the Approved list today | of them already left out as withdrawn | Rule 2, items not approved for the disease |
|---|---|---|---|---|
| All diseases | 29 | 15 | 14 | 0 |
| Common | 13 | 6 | 7 | 0 |
| Cancer | 5 | 3 | 2 | 0 |
| Rare | 4 | 3 | 1 | 0 |
| Agent's choice | 7 | 3 | 4 | 0 |

The approved items Rule 2 would catch:

| Set | Disease | Medicine | On the Approved list today |
|---|---|---|---|
| Common | asthma (MONDO_0004979) | BITOLTEROL (CHEMBL1201295) | yes |
| Common | rheumatoid arthritis (MONDO_0008383) | VALDECOXIB (CHEMBL865) | no |
| Common | psoriasis (MONDO_0005083) | EFALIZUMAB (CHEMBL1201575) | no |
| Common | gout (MONDO_0005393) | INDOPROFEN (CHEMBL15870) | no |
| Common | chronic kidney disease (MONDO_0005300) | EPOETIN DELTA (CHEMBL2109093) | yes |
| Common | depressive disorder (MONDO_0002050) | NEFAZODONE (CHEMBL623) | no |
| Common | depressive disorder (MONDO_0002050) | BENACTYZINE (CHEMBL70352) | yes |
| Common | depressive disorder (MONDO_0002050) | ZIMELDINE (CHEMBL37744) | no |
| Common | schizophrenia (MONDO_0005090) | TRIFLUPROMAZINE (CHEMBL570) | yes |
| Common | schizophrenia (MONDO_0005090) | REMOXIPRIDE (CHEMBL22242) | no |
| Common | schizophrenia (MONDO_0005090) | CARPHENAZINE (CHEMBL1201328) | yes |
| Common | schizophrenia (MONDO_0005090) | SERTINDOLE (CHEMBL12713) | no |
| Common | schizophrenia (MONDO_0005090) | FLUPENTIXOL (CHEMBL6066864) | yes |
| Cancer | breast cancer (MONDO_0007254) | FORMESTANE (CHEMBL132530) | yes |
| Cancer | breast cancer (MONDO_0007254) | NOMIFENSINE (CHEMBL273575) | no |
| Cancer | prostate cancer (MONDO_0008315) | ATRASENTAN (CHEMBL9194) | yes |
| Cancer | chronic myeloid leukemia (MONDO_0011996) | INTERFERON ALFA-2B (CHEMBL1201558) | yes |
| Cancer | ovarian cancer (MONDO_0008170) | MIBEFRADIL (CHEMBL45816) | no |
| Rare | Duchenne muscular dystrophy (MONDO_0010679) | ATALUREN (CHEMBL256997) | yes |
| Rare | hemophilia B (MONDO_0010604) | COAGULATION FACTOR IX HUMAN (CHEMBL4297986) | yes |
| Rare | hemophilia B (MONDO_0010604) | FIDANACOGENE ELAPARVOVEC (CHEMBL3990034) | yes |
| Rare | pulmonary arterial hypertension (MONDO_0015924) | SITAXENTAN (CHEMBL282724) | no |
| Agent's choice | allergic rhinitis (MONDO_0011786) | ASTEMIZOLE (CHEMBL296419) | no |
| Agent's choice | gastroesophageal reflux disease (MONDO_0007186) | TEGASEROD (CHEMBL76370) | no |
| Agent's choice | type 1 diabetes mellitus (MONDO_0005147) | SOTAGLIFLOZIN (CHEMBL3039507) | yes |
| Agent's choice | insomnia (MONDO_0013600) | METHAQUALONE (CHEMBL282052) | no |
| Agent's choice | osteoarthritis (MONDO_0005178) | ISOXICAM (CHEMBL53292) | no |
| Agent's choice | urinary tract infection (MONDO_0100338) | SULFALENE (CHEMBL1525826) | yes |
| Agent's choice | urinary tract infection (MONDO_0100338) | PIDOTIMOD (CHEMBL1488165) | yes |

## 8. Diseases whose Approved list would become empty if groups B to F were hidden

8 diseases have items on the Approved list today, and every one of them is in groups B to F:

| Set | Disease | Id | Items that would be hidden | Their groups |
|---|---|---|---|---|
| Rare | Friedreich ataxia | MONDO_0100339 | 2 | E 2 |
| Rare | Dravet syndrome | MONDO_0100135 | 2 | B 1, F 1 |
| Rare | osteogenesis imperfecta | MONDO_0019019 | 1 | B 1 |
| Agent's choice | age-related macular degeneration | MONDO_0005150 | 1 | B 1 |
| Agent's choice | gastric cancer | MONDO_0001056 | 11 | B 2, C 9 |
| Agent's choice | leprosy | MONDO_0005124 | 3 | D 3 |
| Agent's choice | Graves disease | MONDO_0005364 | 2 | B 2 |
| Agent's choice | primary biliary cholangitis | MONDO_0005388 | 2 | B 2 |

If PMDA counted as a regulator too, the list would still become empty for 6 of them: Friedreich ataxia (MONDO_0100339), osteogenesis imperfecta (MONDO_0019019), age-related macular degeneration (MONDO_0005150), leprosy (MONDO_0005124), Graves disease (MONDO_0005364), primary biliary cholangitis (MONDO_0005388).

0 diseases have nothing on the Approved list today, before any new rule.

Only the disease's own list was read. In Moonlight a disease can also show approved medicines in the narrower and wider-group boxes; those were not studied here.

## 9. Extra: where the medicines already on Moonlight's corrections list land

Not asked for, but it costs nothing and may help Kashish judge the groups. `moonlight/corrections.json` (read, not changed) holds 12 medicine and disease pairs. All of their diseases are in this study.

| Disease id | Medicine id | Disease | Medicine | Group | Approval report sources |
|---|---|---|---|---|---|
| MONDO_0004975 | CHEMBL1201222 | Alzheimer disease | LISDEXAMFETAMINE | C | PMDA |
| MONDO_0004980 | CHEMBL1201222 | atopic eczema | LISDEXAMFETAMINE | C | PMDA |
| MONDO_0007739 | CHEMBL1201222 | Huntington disease | LISDEXAMFETAMINE | C | PMDA |
| MONDO_0004975 | CHEMBL641 | Alzheimer disease | ATOMOXETINE | C | PMDA |
| MONDO_0004980 | CHEMBL641 | atopic eczema | ATOMOXETINE | C | PMDA |
| MONDO_0007739 | CHEMBL641 | Huntington disease | ATOMOXETINE | C | PMDA |
| MONDO_0004975 | CHEMBL796 | Alzheimer disease | METHYLPHENIDATE | C | PMDA |
| MONDO_0004980 | CHEMBL796 | atopic eczema | METHYLPHENIDATE | C | PMDA |
| MONDO_0007739 | CHEMBL796 | Huntington disease | METHYLPHENIDATE | C | PMDA |
| MONDO_0004975 | CHEMBL862 | Alzheimer disease | GUANFACINE | C | PMDA |
| MONDO_0004980 | CHEMBL862 | atopic eczema | GUANFACINE | C | PMDA |
| MONDO_0007739 | CHEMBL862 | Huntington disease | GUANFACINE | C | PMDA |

## What was not verified

- **Whether any approval is really right or wrong.** This study cannot tell. A group only says which kind of source Open Targets attached. No item in this report is labelled right or wrong, and group A is not a promise that an item is right.
- **The links were not opened.** The grouping uses the `source` word only. It was not checked that a DailyMed, FDA or EMA page really is about this disease, or that a TTD, PMDA or ATC page is not.
- **Which sources are regulators.** That DailyMed, FDA, EMA Human Drugs and PMDA are regulator sources and TTD and ATC are secondary is taken from what the Open Targets team told us. It was not checked here.
- **Only each disease's own list was read.** Moonlight's Approved tab also uses the medicines found through the disease's proteins, the withdrawn notes on those paths, and the lists of the parent and child diseases. None of those were asked. So "on the Approved list today" here means: passes `fetch_approved` on the disease's own list. The real tab can differ a little for a disease.
- **The skipped names.** 16 given names had no exact match and were not studied, though Open Targets has those diseases under other names (the table in section 1 shows them).
- **These are not a fair sample of all diseases.** The four sets were picked by people and by the agent. The shares describe these 124 diseases only.
- **One day, one data release.** Every answer came the same day from one release. Each was asked twice and matched. Some rows hold no reports at all; it is not known whether that is how the data is or an incomplete answer.
- **No Moonlight code was changed**, so the test suite proves nothing about this study. It was run once at the end only to see that the new folder breaks no test.

---

## Section 5 in full: every approved item in groups B, C, D, E and F

778 items. Not shortened. For each item: its group, the sources of its approval reports, whether it is on the Approved list today, and then **every** report on its rows, written `stage | source | link`, approval reports first. No item here is labelled right or wrong: this study cannot tell.

### Common (322 items)

#### asthma (MONDO_0004979)

- **BAMBUTEROL** (CHEMBL521589) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07XYV
- **BECLOMETHASONE** (CHEMBL1586) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07DVK
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02063139
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06482294
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00476268
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00861926
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03834012
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00250341
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02294279
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02345993
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00402207
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06100042
- **CHYMOTRYPSIN** (CHEMBL1201465) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08NAB
- **CINALUKAST** (CHEMBL283754) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06PEB
- **DOXOFYLLINE** (CHEMBL1527608) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07NCN
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03879590
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01055041
- **ENPROFYLLINE** (CHEMBL279898) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09AMZ
- **FENOTEROL** (CHEMBL32800) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04XEG
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01440335
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01095016
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02177370
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02182479
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02182505
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00460577
- **FLUPREDNISOLONE** (CHEMBL1200774) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V9DZ
- **GLYCEROL, IODINATED** (CHEMBL2105827) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01JQJ
- **ISOETHARINE** (CHEMBL1201213) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08HUC
- **KHELLIN** (CHEMBL44746) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G4KG
- **KRYPTON KR 81M** (CHEMBL1201096) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0KL9X
- **LODOXAMIDE** (CHEMBL1201266) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0OG3K
- **OXITROPIUM BROMIDE** (CHEMBL4297109) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0D4IH
- **PRANLUKAST** (CHEMBL21333) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08QIP
- **PROCATEROL** (CHEMBL160519) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z1WA
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02165046
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02162784
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00990847
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01076322
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01095016
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01091337
- **PROTOKYLOL** (CHEMBL1201273) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02FCQ
- **REPIRINAST** (CHEMBL2105300) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O6KE
- **RIMITEROL** (CHEMBL88055) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03NOS
- **ROFLUMILAST** (CHEMBL193240) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R4UW
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04108377
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01365533
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01765192
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03532490
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00242307
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00073177
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00076076
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00163475
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00163527
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00246922
- **THEOBROMINE** (CHEMBL1114) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I0DS
- **BITOLTEROL** (CHEMBL1201295) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06RUL

#### type 2 diabetes mellitus (MONDO_0005148)

- **GLISOXEPIDE** (CHEMBL2106618) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04NTJ
- **LOBEGLITAZONE** (CHEMBL3585580) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04BCB
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01030679
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01001611
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01106131
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03627182
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03641352
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03739125
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02315287
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02338921
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02480465
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03770052
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05915949
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07108985
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05043467
- **CETILISTAT** (CHEMBL2103825) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00156897
- **IPRAGLIFLOZIN L-PROLINE** (CHEMBL4297658) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **MITIGLINIDE CALCIUM DIHYDRATE** (CHEMBL4298005) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01333592
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02154347
- **OMARIGLIPTIN** (CHEMBL2105762) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01088711
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01217073
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01682759
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01697592
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01698775
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01703221
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01704261
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01717313
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01755156
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01814748
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01841697
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01863667
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D0M3XR
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02906709
- **TRELAGLIPTIN** (CHEMBL1650443) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - IND | TTD | https://ttd.idrblab.cn/data/drug/details/D0N6SO
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00653185
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00760344
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01431807
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01632007
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02324569
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02512068
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03940183
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07073768
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03555591
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04285983
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06889909
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06913101
- **VOGLIBOSE** (CHEMBL476960) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01263470
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01263496
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01263483
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01263509
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00411554
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00654381
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00837577
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05688332
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00970528
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01309698
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02049814
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02097342
- **ANAGLIPTIN** (CHEMBL1929396) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T8XB
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00532506
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01169090
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02330406
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04810507
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07442006
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04267601
- **TOFOGLIFLOZIN ANHYDROUS** (CHEMBL2110731) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04DXA
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00682097
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00933972
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01044017
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00800176
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05469659
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D0U7SR
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02201004
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02537834

#### epilepsy (MONDO_0005027)

- **CLOBAZAM** (CHEMBL70418) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0S9MC
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02565108
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01932502
- **ETEROBARB** (CHEMBL327407) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E3WQ
- **NITRAZEPAM** (CHEMBL13209) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T5WK
- **IOMAZENIL** (CHEMBL2110679) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **AMINO(DIPHENYLHYDANTOIN) VALERIC ACID** (CHEMBL3707389) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AB03
- **BARBEXACLONE** (CHEMBL3833301) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AA04
- **BECLAMIDE** (CHEMBL64195) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX30
- **CARISBAMATE** (CHEMBL2087003) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX19
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00210522
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D0S0FZ
- **ETHADIONE** (CHEMBL93047) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AC03
- **ETHOTOIN** (CHEMBL1095) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AB01
- **EZOGABINE** (CHEMBL41355) | group **D** | approval report sources: ATC | on the Approved list today; has a WITHDRAWAL report
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX21
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00232596
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00235755
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01462656
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01587339
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/trobalt
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X7GL
- **GAMMA-AMINOBUTYRIC ACID** (CHEMBL96) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AG03
- **MEPHOBARBITAL** (CHEMBL45029) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AA01
- **PHENETURIDE** (CHEMBL2107062) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX13
- **PROGABIDE** (CHEMBL287631) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AG05
- **SULTHIAME** (CHEMBL328560) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX03
- **VALPROMIDE** (CHEMBL93836) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AG02
- **CANNABIDIOL** (CHEMBL190461) | group **F** | approval report sources: ATC, ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX24
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02660255
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03877991
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02695537
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02700412
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02983695
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02324673
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02332655
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02565108
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02607891
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02607904
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02987114
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04406948
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05803434
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07023744
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D0O1UZ
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02783092
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03808935
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02397863
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02461706
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02556008
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03014440
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03196934
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03676049
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05772429
- **CLONAZEPAM** (CHEMBL452) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AE01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0CP4E
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00594945
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D0CP4E
- **ESLICARBAZEPINE** (CHEMBL315985) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AF04
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04QZD
- **FENFLURAMINE** (CHEMBL87493) | group **F** | approval report sources: ATC, PMDA | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX26
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05560282
- **FOSPHENYTOIN** (CHEMBL1201336) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AB05
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0J5YC
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00908453
- **GANAXOLONE** (CHEMBL1568698) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX27
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X0CH
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00465517
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02358538
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04285346
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05323734
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05604170
- **MEPHENYTOIN** (CHEMBL861) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AB04
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AB54
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07RGW
- **METHARBITAL** (CHEMBL450) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AA30
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02OZY
- **METHSUXIMIDE** (CHEMBL697) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AD03
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08EOD
- **PARAMETHADIONE** (CHEMBL1100) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AC01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09JBP
- **PHENACEMIDE** (CHEMBL918) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX07
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07ONP
- **PHENOBARBITAL** (CHEMBL40) | group **F** | approval report sources: ATC, TTD | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AA02
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y7RW
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00381537
- **PHENSUXIMIDE** (CHEMBL797) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AD02
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06BYV
- **STIRIPENTOL** (CHEMBL1983350) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AX17
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02XSA
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02607891
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01533506
- **TIAGABINE** (CHEMBL1027) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AG06
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0ED7U
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01587339
- **TRIMETHADIONE** (CHEMBL695) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AC02
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U4VT
- **VIGABATRIN** (CHEMBL89598) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N03AG04
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R3QY

#### rheumatoid arthritis (MONDO_0008383)

- **ALCLOFENAC** (CHEMBL94081) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0C6OQ
- **CANAKINUMAB** (CHEMBL1201834) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0TD2G
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00505089
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00619905
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00424346
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00487825
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00504595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00554606
- **CERTOLIZUMAB** (CHEMBL4297565) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0CA0P
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06028438
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03414502
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01098201
- **DIMETHYL SULFOXIDE** (CHEMBL504) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08HVE
- **ETOFENAMATE** (CHEMBL1451633) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09YVX
- **ETORICOXIB** (CHEMBL416146) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09MGR
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00264147
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00250445
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01208181
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01067430
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04144101
- **FLURBIPROFEN** (CHEMBL563) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0A1PX
- **GOLD SODIUM THIOMALATE** (CHEMBL306043) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0FH7C
- **INOSINE** (CHEMBL1556) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Q2QU
- **NIFLUMIC ACID** (CHEMBL63323) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00HGB
- **SALSALATE** (CHEMBL154111) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y0JH
- **TENOXICAM** (CHEMBL302795) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I6IB
- **OZORALIZUMAB** (CHEMBL1743054) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00959036
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01007175
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01063803
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D05EPV
- **PEFICITINIB** (CHEMBL3137308) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01754805
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01554696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01565655
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01649999
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01711814
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D06EIC
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01638013
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02305849
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02308163
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03660059
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03971253
- **VALDECOXIB** (CHEMBL865) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/bextra
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn-0
- **IGURATIMOD** (CHEMBL2107455) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0B8MZ
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00965757
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01548001
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01554917
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01893151
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02275299
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04928066
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05803135
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06146972
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06945666
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01850966
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07115641

#### psoriasis (MONDO_0005083)

- **ANTHRALIN** (CHEMBL46469) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05AC01
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05AC51
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03348462
- **BERGAPTEN** (CHEMBL24171) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05BA03
- **ETRETINATE** (CHEMBL464) | group **D** | approval report sources: ATC | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05BB01
- **FUMARIC ACID** (CHEMBL503160) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05AX01
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01321164
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02634801
- **METHOXSALEN** (CHEMBL416) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05AD02
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05BA02
- **ROFLUMILAST** (CHEMBL193240) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05AX06
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04279119
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07340216
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00746434
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04128007
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04655313
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04746911
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07543640
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05684744
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04211363
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04286607
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05028582
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05763082
- **TACALCITOL** (CHEMBL2105611) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05AX04
- **TRIOXSALEN** (CHEMBL1475) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05AD01
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D05BA01
- **EFALIZUMAB** (CHEMBL1201575) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00382512
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00368654
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00256139
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00442650
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/raptiva

#### atopic eczema (MONDO_0004980)

- **CORTISONE** (CHEMBL1499) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0IX6I
- **JUNIPER TAR** (CHEMBL2108383) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K6VD
- **ATOMOXETINE** (CHEMBL641) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **BARICITINIB** (CHEMBL2105759) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07262983
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02576938
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03334396
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03334422
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03334435
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03428100
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03435081
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03559270
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03733301
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03952559
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03358693
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05969730
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06882148
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07448363
- **BILASTINE** (CHEMBL1742423) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **DESLORATADINE** (CHEMBL1172) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00817076
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01916980
- **EPINASTINE** (CHEMBL1106) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02182557
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02182570
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02238223
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02238236
- **FEXOFENADINE** (CHEMBL914) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05461456
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01244230
- **GUANFACINE** (CHEMBL862) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **LEVOCETIRIZINE** (CHEMBL1201191) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00375713
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00884325
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01445262
- **LISDEXAMFETAMINE** (CHEMBL1201222) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **METHYLPHENIDATE** (CHEMBL796) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **OLOPATADINE** (CHEMBL1189432) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **TAPINAROF** (CHEMBL259571) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02466152
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00837551
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01098734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02564055
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05186805
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D03DMB
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05014568
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05032859
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05142774
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05172726
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05326672
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07265479
- **ALITRETINOIN** (CHEMBL705) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D11AH04
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03026907
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03026946
- **RUXOLITINIB** (CHEMBL1789941) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D11AH09
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03257644
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03920852
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05034822
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06673654
    - PHASE_1_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D04LKS
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03011892
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04839380
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05127421
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05906628
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06923228
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03745638
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03745651
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04921969
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05456529
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06238817
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06832618
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05696392
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06627335
- **CROMOLYN** (CHEMBL428880) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D11AH03
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G7IY

#### ulcerative colitis (MONDO_0005101)

- **CORTICOTROPIN ZINC HYDROXIDE** (CHEMBL1201609) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0D0BM
- **AZATHIOPRINE** (CHEMBL1542) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00537316
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00984568
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03101800
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02425852
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02579733
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03151525
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07235904
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04882683

#### osteoporosis (MONDO_0005298)

- **CALCITONIN** (CHEMBL4594242) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I1XG
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00411125
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00525798
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00542984
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00543023
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00543218
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00959764
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00114803
- **CALCIUM** (CHEMBL1200496) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0PJ4K
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02854722
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04321837
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00172172
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00670501
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00757393
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05970250
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06022237
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07334626
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07364279
- **ESTROGENS, CONJUGATED SYNTHETIC A** (CHEMBL1201466) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0N6YV
- **ETIDRONIC ACID** (CHEMBL871) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00XUN
- **IPRIFLAVONE** (CHEMBL165790) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R2OA
- **LASOFOXIFENE** (CHEMBL328190) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09NMD
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00143273
- **MINODRONIC ACID** (CHEMBL319144) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00NPT
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00794443
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212628
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212667
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212719
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05305183
- **NANDROLONE** (CHEMBL757) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00YWP
- **SMC021** (CHEMBL3545415) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I1XG
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00411125
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00525798
- **SODIUM FLUORIDE** (CHEMBL1528) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02IUD
- **STRONTIUM RANELATE** (CHEMBL3707306) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X7KZ
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00239629
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01544894
- **TESTOSTERONE** (CHEMBL386630) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06XMU
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080483
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07254429
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182871
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06247267
- **TILUDRONIC ACID** (CHEMBL1350) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Q8CS
- **BAZEDOXIFENE** (CHEMBL46740) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00238745
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00205777
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00384072
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00808132
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01416194
- **ELDECALCITOL** (CHEMBL4297608) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02306187
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03755193
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05884372
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01974167
- **LEVONORGESTREL** (CHEMBL1389) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02475265
- **TERIPARATIDE ACETATE** (CHEMBL1201549) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html

#### gout (MONDO_0005393)

- **DOTINURAD** (CHEMBL4594446) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03375632
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06056570
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02344862
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02416167
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07535034
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03006445
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03100318
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03372200
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05007392
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07089888
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/DA29IM
- **TOPIROXOSTAT** (CHEMBL1078685) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D0WK0P
- **CINCHOPHEN** (CHEMBL348000) | group **D** | approval report sources: ATC | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=M04AC02
- **ISOBROMINDIONE** (CHEMBL2104325) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=M04AB04
- **LESINURAD** (CHEMBL2105720) | group **D** | approval report sources: ATC | on the Approved list today; has a WITHDRAWAL report
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=M04AB05
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01001338
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01493531
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01508702
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01510158
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01510769
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01650246
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01808144
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/duzallo
- **RASBURICASE** (CHEMBL1201594) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=M04AX01
- **TISOPURINE** (CHEMBL119423) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=M04AA02
- **INDOPROFEN** (CHEMBL15870) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Q5PL
- **BENZBROMARONE** (CHEMBL388590) | group **F** | approval report sources: ATC, TTD | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=M04AB03
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z3DY
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02317861
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03100318
- **SULFINPYRAZONE** (CHEMBL832) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=M04AB02
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03DEI

#### heart failure (MONDO_0005252)

- **DESLANOSIDE** (CHEMBL1614) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07TGN
- **DIGITOXIN** (CHEMBL254219) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0M3QP
- **DOBUTAMINE** (CHEMBL926) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0J7RK
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01930734
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02888561
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06462313
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07186062
- **DOPEXAMINE** (CHEMBL77622) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V7XF
- **HYDRALAZINE** (CHEMBL276832) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05JFY
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02522208
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01255475
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01822808
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02343393
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02305095
- **ISOSORBIDE DINITRATE** (CHEMBL6622) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05JFY
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02522208
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01822808
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02343393
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02305095
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02649998
- **OLPRINONE** (CHEMBL1474900) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03ZBN
- **OUABAIN** (CHEMBL222863) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0AR3J
- **VESNARINONE** (CHEMBL17423) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L0ZF
- **DEFERIPRONE** (CHEMBL70927) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00293098

#### atrial fibrillation (MONDO_0004981)

- **AJMALINE** (CHEMBL5314404) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02GUG
- **IBUTILIDE** (CHEMBL533) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02MLW
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00589992
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01014741
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03370536
- **NEBACUMAB** (CHEMBL2109181) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00EIB
- **OUABAIN** (CHEMBL222863) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0AR3J

#### chronic obstructive pulmonary disease (MONDO_0005002)

- **ALMITRINE** (CHEMBL1183717) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0D9NA
- **BAMIFYLLINE** (CHEMBL2110760) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O7SP
- **BITOLTEROL** (CHEMBL1201295) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06RUL
- **CARBOCYSTEINE** (CHEMBL396416) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X5SI
- **FLUOROMETHOLONE** (CHEMBL1200600) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P0HT
- **MEPREDNISONE** (CHEMBL1201148) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I5DS
- **PRASTERONE** (CHEMBL90593) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K0EK
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00581087
- **PREGABALIN** (CHEMBL1059) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00WUF
- **THEOPHYLLINE ANHYDROUS** (CHEMBL190) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0F8RA
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00241631
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00634413
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00299858
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01599871
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02340520
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03984188
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00671151
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00893009
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02001935
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02257463
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03015090
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05738135
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06125665

#### chronic kidney disease (MONDO_0005300)

- **FERUMOXYTOL** (CHEMBL1201867) | group **B** | approval report sources: TTD | on the Approved list today; has a WITHDRAWAL report
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06CTM
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00255424
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00255450
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155388
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01264679
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03619850
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/rienso
- **BIXALOMER** (CHEMBL4297202) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00505037
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00892749
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01017276
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01742585
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01742611
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02805348
- **TENAPANOR** (CHEMBL3304485) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01764854
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03824587
- **EPOETIN DELTA** (CHEMBL2109093) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00664066
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/dynepo
- **FUROSEMIDE** (CHEMBL35) | group **E** | approval report sources: none | on the Approved list today
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01977430
    - PREAPPROVAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/bopediat
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00962286
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01146288
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03082742

#### hypothyroidism (MONDO_0005420)

- **THYROGLOBULIN** (CHEMBL1201650) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0QD9R
- **THYROTROPIN** (CHEMBL1201532) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03EER

#### depressive disorder (MONDO_0002050)

- **AMITRIPTYLINE** (CHEMBL629) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y5UG
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01049347
- **APREPITANT** (CHEMBL1471) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0GU4K
- **BREXANOLONE** (CHEMBL207538) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00VZZ
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01336413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04003285
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05329779
- **CITALOPRAM** (CHEMBL549) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y5DO
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03282110
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01032018
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02000726
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00018902
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080158
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00962039
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01109030
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00044681
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00044798
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254007
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254020
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01796132
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00188396
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00876226
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00896441
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00930293
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01153165
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02262156
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04145076
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05588102
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05850572
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05957094
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07399795
- **CLOMIPRAMINE** (CHEMBL415) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0ZS8P
- **CYCLOBENZAPRINE** (CHEMBL669) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01KHH
- **DESIPRAMINE** (CHEMBL72) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01UTL
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00338962
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00000376
- **DOXEPIN** (CHEMBL1628227) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06FES
- **FLUOXETINE** (CHEMBL41) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01VJN
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0TR5X
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05789186
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00296725
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01802437
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02017535
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00338767
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01635218
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04850222
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05002309
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05431413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07007221
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00018902
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080158
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01687478
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02751632
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05944926
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06153004
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00061113
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00573547
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01796132
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02916238
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03390933
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05458479
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05976347
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01022632
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01740726
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03436173
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05127369
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05361330
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05588102
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05850572
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06384209
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025590
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07048938
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07456501
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07521358
- **FLUVOXAMINE** (CHEMBL814) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03HFG
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01796132
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05588102
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05850572
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025590
- **GLAZIOVINE** (CHEMBL1980854) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0J4IX
- **IMIPRAMINE** (CHEMBL11) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06ZUK
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00745017
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00296725
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00000390
- **ISOCARBOXAZID** (CHEMBL1201168) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I2VK
- **MIANSERIN** (CHEMBL6437) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R6RO
- **MILNACIPRAN** (CHEMBL259209) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09VGC
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02783430
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00225511
- **MINAPRINE** (CHEMBL278819) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0W8SJ
- **MOCLOBEMIDE** (CHEMBL86304) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01ZSO
- **NORTRIPTYLINE** (CHEMBL445) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04WFD
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00612807
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00062738
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03652870
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07527481
- **OLANZAPINE** (CHEMBL715) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01VJN
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01282632
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00273624
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01687478
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00520507
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01427608
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01057329
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06581302
- **PAROXETINE** (CHEMBL490) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06GDY
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00062738
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00086190
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00338962
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01049347
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00259883
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01796132
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00188396
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01371461
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01371474
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05588102
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05850572
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025590
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318181
- **PHENELZINE** (CHEMBL1089) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P9AC
- **PROGABIDE** (CHEMBL287631) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O5LA
- **REBOXETINE** (CHEMBL14370) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0N8FQ
- **SERTRALINE** (CHEMBL809) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K0TC
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00581009
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00612807
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01032018
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02917122
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00000458
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00232284
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00510822
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00602355
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00654953
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04171193
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05002309
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00078286
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080158
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00086138
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02565316
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00026637
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00066859
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00158990
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00302068
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00331305
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00946998
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01098318
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02358343
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02417064
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02422186
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02497287
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00226642
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01427608
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01796132
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01896934
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02042573
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02185547
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06124417
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00045773
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00208585
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00245557
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00339066
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01302080
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01437189
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01751828
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02262156
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02955719
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03126188
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03841474
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03920475
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05210153
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05588102
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05850572
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06384209
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06840379
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025590
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318181
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07387120
- **TRAZODONE** (CHEMBL621) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00USF
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01524497
- **TRYPTOPHAN** (CHEMBL54976) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05EJG
- **URIDINE** (CHEMBL100259) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y7DP
- **ESCITALOPRAM** (CHEMBL1508) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03623711
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03887624
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070694
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00343070
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00566202
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01103180
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01368432
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02407821
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03388164
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05002309
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070941
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080158
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00215228
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01876823
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02674529
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03909217
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00610506
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642694
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00668525
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00953108
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02153567
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02246244
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02417064
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02422186
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02497287
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03652870
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04973930
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00194948
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00220480
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00277108
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416221
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00643162
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00703742
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00754936
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00935246
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02423694
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02553161
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03460379
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03841474
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04156425
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05210140
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05588102
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05818735
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05850572
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06325605
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025590
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07074652
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07077291
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07274241
- **VORTIOXETINE** (CHEMBL2104993) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01607125
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01491035
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01255787
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00672958
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00811252
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02845349
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04818099
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05932407
    - UNKNOWN | USAN | https://searchusan.ama-assn.org/finder/usan/search/VORTIOXETINE%20HEMIHYDROBROMIDE/relevant/1/
- **BENACTYZINE** (CHEMBL70352) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07KYU
- **NEFAZODONE** (CHEMBL623) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00015210
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X7DE
- **ZIMELDINE** (CHEMBL37744) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0C1XS
- **DULOXETINE** (CHEMBL1175) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01AXB
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03623711
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00215228
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00191594
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00811252
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02417064
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02422186
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02443194
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02497287
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03315793
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03395353
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00406848
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00422162
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00494377
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00532480
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00658931
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00696774
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01051466
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01391221
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01796132
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02229825
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05976347
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00596986
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01057329
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04847245
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025590
- **MIRTAZAPINE** (CHEMBL654) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05ZIK
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00249444
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00322309
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00488072
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00832520
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02650544
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03935685
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080158
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01598584
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00150839
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01119924
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01465919
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01601002
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01039740
- **VENLAFAXINE** (CHEMBL637) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P1UX
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00612807
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02181231
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02263248
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00131456
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00249483
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00018902
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080158
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00086190
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00225511
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00789854
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02417064
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02422186
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02497287
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04973930
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00150839
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00401726
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00546494
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00634283
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00792168
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01796132
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04207385
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00186264
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00735670
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01609348
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02955719
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03126188
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03920475
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025590

#### schizophrenia (MONDO_0005090)

- **AMISULPRIDE** (CHEMBL243712) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03ELL
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04533724
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02051387
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00628290
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07152184
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03510325
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00245674
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00256997
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00304616
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00331981
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00419653
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00436371
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00761670
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01105481
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01246232
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01248195
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01615185
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01795183
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02095938
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03802838
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04446234
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01029769
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01448499
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03451734
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05956600
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06040944
- **BENPERIDOL** (CHEMBL297302) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X7QQ
- **BROMPERIDOL** (CHEMBL28218) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00SHQ
- **CLOTHIAPINE** (CHEMBL304902) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0PX8L
- **FLUPHENAZINE DECANOATE** (CHEMBL1200854) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03NTJ
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00014001
- **FLUSPIRILENE** (CHEMBL46516) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U5FS
- **GADOBENATE DIMEGLUMINE** (CHEMBL1200571) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01OIL
- **GLUTAMIC ACID** (CHEMBL575060) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00ENY
- **MESORIDAZINE** (CHEMBL1088) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04AAN
- **NEMONAPRIDE** (CHEMBL20734) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0IN7I
- **PENFLURIDOL** (CHEMBL47050) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0CQ0Z
- **PIMOZIDE** (CHEMBL1423) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00KHM
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00374244
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00158223
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02600741
- **PIPERACETAZINE** (CHEMBL1584) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0AO6B
- **PIPOTIAZINE** (CHEMBL398880) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z6QG
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07152184
- **SULPIRIDE** (CHEMBL26) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03QGM
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00654576
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01615185
- **THIORIDAZINE** (CHEMBL479) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U1OE
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02600741
- **ZUCLOPENTHIXOL** (CHEMBL53904) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I8LU
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07152184
- **BLONANSERIN** (CHEMBL178803) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01516424
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02335658
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D08GJH
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03784222
- **CARPHENAZINE** (CHEMBL1201328) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01QML
- **FLUPENTIXOL** (CHEMBL6066864) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07152184
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0OC3J
- **REMOXIPRIDE** (CHEMBL22242) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01PIL
- **SERTINDOLE** (CHEMBL12713) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00654706
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00759421
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00759460
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00856583
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00864045
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345982
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00629252
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00885690
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0OS6O
- **TRIFLUPROMAZINE** (CHEMBL570) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0DG0P

#### bipolar disorder (MONDO_0004985)

- **ACETOPHENAZINE** (CHEMBL1085) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L0MB
- **LEVOMEPROMAZINE** (CHEMBL1764) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09LZT
- **ILOPERIDONE** (CHEMBL14376) | group **E** | approval report sources: none | on the Approved list today
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04819776
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02413918
    - PREAPPROVAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/iloperidone-vanda-pharmaceuticals

#### Parkinson disease (MONDO_0005180)

- **CYCRIMINE** (CHEMBL1201227) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02LRQ
- **DOPAMINE** (CHEMBL59) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T7OW
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04802733
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06422208
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06821529
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07212088
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01860794
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03295786
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03775538
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04332276
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05887466
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02233023
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03151460
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03665493
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03918616
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06477744
- **LISURIDE** (CHEMBL157138) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X7KB
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00089622
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408915
- **RIMABOTULINUMTOXINB** (CHEMBL1201569) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02FXK
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00515437
- **FOSLEVODOPA** (CHEMBL4594379) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03033498
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03374917
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05094050
    - PHASE_1 | TTD | https://ttd.idrblab.cn/data/drug/details/D08NXP
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03781167
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/DP7GK8
    - UNKNOWN | USAN | https://searchusan.ama-assn.org/finder/usan/search/FOSLEVODOPA/relevant/1/
- **ZONISAMIDE** (CHEMBL750) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01766128
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04182399
- **BUDIPINE** (CHEMBL334491) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04BX03
- **CABERGOLINE** (CHEMBL1201087) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04BC06
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00153972
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00174239
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01270711
- **DEXETIMIDE** (CHEMBL1908364) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA08
- **DIHYDROERGOCRYPTINE** (CHEMBL1743263) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04BC03
- **ETANAUTINE** (CHEMBL3707215) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AB01
- **ETHYBENZTROPINE** (CHEMBL2104273) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AC30
- **MAZATICOL** (CHEMBL2105187) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA10
- **PHENGLUTARIMIDE** (CHEMBL1096643) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA09
- **PIRIBEDIL** (CHEMBL1371770) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04BC08
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01007864
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00725478
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01519856
- **TROPATEPINE** (CHEMBL2107294) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA12
- **BIPERIDEN** (CHEMBL1101) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA02
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0B4TN
- **BORNAPRINE** (CHEMBL4297087) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA11
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05MPX
- **ETHOPROPAZINE** (CHEMBL1206) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA05
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Q0RC
- **MELEVODOPA** (CHEMBL1328898) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04BA04
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U0OT
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00491998
- **METHIXENE** (CHEMBL1201342) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA03
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0NF0W
- **ORPHENADRINE** (CHEMBL900) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AB02
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0D9FV
- **PERGOLIDE** (CHEMBL531) | group **F** | approval report sources: ATC, TTD | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04BC02
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04JCN
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00624741
- **PROCYCLIDINE** (CHEMBL86715) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA04
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R1WR
- **TRIHEXYPHENIDYL** (CHEMBL1490) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=N04AA01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09GFL

#### Alzheimer disease (MONDO_0004975)

- **GV-971** (CHEMBL4650397) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0FS5O
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01453569
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02293915
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04520412
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D1KR3N
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05058040
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05181475
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05430867
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05908695
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05114499
- **HUMAN IMMUNOGLOBULIN G** (CHEMBL1201599) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01OWB
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00299988
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00812565
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01300728
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01561053
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00818662
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01524887
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01736579
- **HUPERZINE A** (CHEMBL395280) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06XWB
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00083590
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01282619
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07066826
- **TACRINE** (CHEMBL95) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E6YQ
- **THIAZOLIDINEDIONE** (CHEMBL85398) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K8IX
- **ATOMOXETINE** (CHEMBL641) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00191009
- **GUANFACINE** (CHEMBL862) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03116126
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D8NY3J
- **LISDEXAMFETAMINE** (CHEMBL1201222) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **METHYLPHENIDATE** (CHEMBL796) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01117181
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02346201

#### glaucoma (MONDO_0005041)

- **OMIDENEPAG ISOPROPYL** (CHEMBL4297666) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03691649
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03691662
- **ACECLIDINE** (CHEMBL20835) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB08
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB58
- **ACETYLCHOLINE** (CHEMBL667) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB09
- **APRACLONIDINE** (CHEMBL647) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EA03
- **BEFUNOLOL** (CHEMBL153984) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01ED06
- **BETAXOLOL** (CHEMBL423) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01ED02
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01ED52
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00061542
- **CARBAMOYLCHOLINE** (CHEMBL965) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB02
- **CLONIDINE** (CHEMBL134) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EA04
- **DAPIPRAZOLE** (CHEMBL1201216) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EX02
- **DEMECARIUM** (CHEMBL1201229) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB04
- **DICHLORPHENAMIDE** (CHEMBL17) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EC02
- **DIPIVEFRIN** (CHEMBL1201262) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EA02
- **ECHOTHIOPHATE** (CHEMBL1201341) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB03
- **GUANETHIDINE** (CHEMBL765) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EX01
- **ISOFLUROPHATE** (CHEMBL1025) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB07
- **LATANOPROSTENE BUNOD** (CHEMBL2364612) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EE06
- **METIPRANOLOL** (CHEMBL1291) | group **D** | approval report sources: ATC | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01ED04
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01ED54
- **NEOSTIGMINE** (CHEMBL278020) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB06
- **NETARSUDIL** (CHEMBL4594250) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EX05
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06960629
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05283395
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06969586
- **OMIDENEPAG** (CHEMBL3707245) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EX06
- **PARAOXON** (CHEMBL23838) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB10
- **PHYSOSTIGMINE** (CHEMBL94) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EB05
- **UNOPROSTONE** (CHEMBL1201407) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EE02
- **BIMATOPROST** (CHEMBL1200963) | group **F** | approval report sources: ATC, PMDA | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EE03
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00538304
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00652496
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01863953
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01915940
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02143843
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00300443
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00332059
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00332072
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00332540
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01099774
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01177098
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01216943
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01426113
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01830140
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02154217
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02390284
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03825380
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04898387
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05397600
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00347802
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00348023
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00440011
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00541242
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01170884
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01298700
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01547598
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02471105
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06761313
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01206361
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04896125
- **BRINZOLAMIDE** (CHEMBL220491) | group **F** | approval report sources: ATC, PMDA | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EC04
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EC54
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00061516
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02390284
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00300079
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00372827
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00440141
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00471380
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00869141
- **CARTEOLOL** (CHEMBL839) | group **F** | approval report sources: ATC, PMDA | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01ED05
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01ED55
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **RIPASUDIL** (CHEMBL3426621) | group **F** | approval report sources: ATC, PMDA | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EX07
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **TAFLUPROST** (CHEMBL1963683) | group **F** | approval report sources: ATC, PMDA | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EE05
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02102750
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04455126
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00596791
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01433900
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02471105
- **TRAVOPROST** (CHEMBL1200799) | group **F** | approval report sources: ATC, PMDA | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=S01EE04
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01658839
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01652664
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02390284
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00347802
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00348023
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00440011
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00471380
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00508469
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00798694
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00799682
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01315574
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01493427
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01547598
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01206361
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01485822
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07400926

#### endometriosis (MONDO_0005133)

- **HISTRELIN** (CHEMBL1201255) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O7DG
- **DROSPIRENONE** (CHEMBL1509) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01697111
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04333576
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02237131
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00675779
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07204093
- **ETHINYL ESTRADIOL** (CHEMBL691) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02599077
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04256200
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01697111
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04333576
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01056042
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02237131
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00675779
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02400801
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03126747
- **NORETHINDRONE** (CHEMBL1162) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **DIENOGEST** (CHEMBL1201864) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04CBI
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04374006
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01283724
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02599077
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04256200
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00225186
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00225199
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01822080
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05697471
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06145438
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07164183
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01595724
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01788722
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02400801
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02425462
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03142035
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03778359
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04306276
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04495855
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04500743
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05272930
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05476172
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06414720
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07204093

#### tuberculosis (MONDO_0018076)

- **AMITHIOZONE** (CHEMBL375492) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AK07
- **DELAMANID** (CHEMBL218650) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AK06
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01856634
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03141060
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00685360
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01131351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01859923
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02573350
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02583048
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03828201
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04550832
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05221502
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05971602
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06114628
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07129629
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07170800
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02975570
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04062201
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06649721
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05871489
- **ENVIOMYCIN** (CHEMBL2146142) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AB06
- **FTIVAZIDE** (CHEMBL2105120) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AC02
- **MORINAMIDE** (CHEMBL1697759) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AK04
- **RIFAMYCIN** (CHEMBL437765) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AB03
- **TERIZIDONE** (CHEMBL2107553) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AK03
- **TIOCARLIDE** (CHEMBL214920) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AD02
- **CYCLOSERINE** (CHEMBL771) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AB01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02WFK
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00000796
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04545788
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05871489
- **PROTIONAMIDE** (CHEMBL1378024) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AD01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L7UQ
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02409290
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03057756
- **RIFABUTIN** (CHEMBL444633) | group **F** | approval report sources: ATC, PMDA, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04AB04
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05CHI
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004736
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00877591
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01259219
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00023413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00640887
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00651066
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01601626
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01663168
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02415985
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00023348
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00018083
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00023361
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01344148

#### malaria (MONDO_0005136)

- **CHLORPROGUANIL** (CHEMBL1213553) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y2DI
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00126971
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118794
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00146731
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00361114
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00393679
- **FOSMIDOMYCIN** (CHEMBL203125) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09UXE
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00217451
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01002183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01361269
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01464125
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01464138
- **MEPROBAMATE** (CHEMBL979) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y4AW
- **OZ277** (CHEMBL404431) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00ZTD
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00362050
- **PYRONARIDINE** (CHEMBL35228) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E0KQ
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05287893
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05929157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00331136
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01594931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02389439
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03814616
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04264130
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05192265
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00541385
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04695197
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03201770
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04778813
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07060794
- **SULPHADOXINE** (CHEMBL244800) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07PAO
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00146718
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00259142
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01707199
- **TRICLOSAN** (CHEMBL849) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00CSQ
- **LUMEFANTRINE CO-ARTEMETHER** (CHEMBL4297927) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03797989
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01103830
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04310085
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01603251
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03334747
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01935882
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118794
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00406146
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01054248
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01374581
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01845701
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01916954
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01939886
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02348788
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03939104
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04695197
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00426439
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00529867
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01038063
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01075945
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01599000
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03241901
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04767217
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04829695
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04897919
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05340153
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00127998
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00203801
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00513500
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00720811
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00725777
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01043744
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01967472
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02213211
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02600767
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03387631
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06970600
- **CYCLOGUANIL** (CHEMBL747) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=P01BB02
    - IND | TTD | https://ttd.idrblab.cn/data/drug/details/D0O9YG
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01442168
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00084227
- **AMODIAQUINE** (CHEMBL682) | group **F** | approval report sources: ATC, TTD | on the Approved list today; has a WITHDRAWAL report
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=P01BA06
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04NQI
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00894660
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00261222
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01955382
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00146718
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05764746
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118807
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00123552
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00131703
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00146731
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00297882
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00378625
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00393679
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00406146
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00852423
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01152931
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01231113
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01374581
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01845701
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03923725
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03939104
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00425763
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00465257
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00699920
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00808951
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01017770
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01697787
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01703884
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02168569
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02637128
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02940756
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03764527
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03768908
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03773536
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04370977
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04618523
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04829695
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04877626
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05343312
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06076213
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06300970
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00127998
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00356824
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00612547
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01567423
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01967472
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03387631
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04301531
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05354258
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0YQ9P
- **ARTEMISININ** (CHEMBL269671) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=P01BE01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0S3WH
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04020653
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01930331
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06928207
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04167566
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04301531
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06806956
- **ARTEMOTIL** (CHEMBL301267) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=P01BE04
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y5ZA
- **HALOFANTRINE** (CHEMBL1107) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=P01BX01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07MVK
- **PRIMAQUINE** (CHEMBL506) | group **F** | approval report sources: ATC, PMDA, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=P01BA03
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T1LK
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04280692
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01743820
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01935882
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02654730
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02691910
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07060404
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00330902
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01838902
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02348788
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05690841
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01389557
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01878357
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02610686
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02793388
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03241901
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03773536
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03783299
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01849640
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01872702
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02043652
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05753150
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05874271
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05879224
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07389057
- **QUININE** (CHEMBL170) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=P01BC01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03DDR
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00123552
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00124267
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00527800
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01374581
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02563704
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00495508
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00540202
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01805232
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06472258

### Cancer (91 items)

#### breast cancer (MONDO_0007254)

- **ARCITUMOMAB** (CHEMBL2108253) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06URS
- **ARZOXIFENE** (CHEMBL226267) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06LOQ
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005886
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003428
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00034125
- **BOSUTINIB** (CHEMBL288441) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0OB0F
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03854903
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00959946
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00319254
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00793546
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00880009
- **CABAZITAXEL** (CHEMBL1201748) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02HSB
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01693549
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02166658
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03048942
- **DROMOSTANOLONE** (CHEMBL1582) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09NNA
- **ELACESTRANT** (CHEMBL4297509) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07KUN
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04797728
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02338349
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02650817
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06120283
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06638307
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06691035
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04791384
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05386108
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05563220
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05573126
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05618613
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05963997
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06938711
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07198724
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05596409
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05982093
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06062498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06201234
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06923527
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07005882
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07159451
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07222215
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07395336
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03778931
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05512364
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06382948
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07242352
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06544577
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07563595
- **FADROZOLE** (CHEMBL9298) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0ZX1P
- **FLUOXYMESTERONE** (CHEMBL1445) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L2LS
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00303615
- **GESTRINONE** (CHEMBL1868702) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0M5RF
- **GOSERELIN** (CHEMBL1201247) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00BCG
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01149356
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01240928
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02333370
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05755581
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07310420
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00010010
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00186121
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00217659
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00235937
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00303524
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00322348
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00432172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00532272
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01013506
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01205685
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01240941
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01266213
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01368263
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01776008
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01989780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02072512
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02313051
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02476786
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02592083
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02603679
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02624973
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03065621
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03573648
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03628066
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03822468
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03839823
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04551495
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05004142
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05582499
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05594095
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05607004
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05720260
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225284
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06953882
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07158021
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07179939
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07287098
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07460752
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03373708
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05253066
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06009627
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002460
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002580
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002582
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00047099
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00053911
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00309478
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00912548
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01073865
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01352091
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01674140
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01712893
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02003209
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02132390
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02278120
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02344472
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02518191
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02535221
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02914158
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03423199
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03658213
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03664895
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03701334
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03936933
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05110170
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05438810
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05439499
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05827081
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03591549
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00488722
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00827307
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02430103
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05131893
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05800197
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06636591
- **INDIUM IN 111 SATUMOMAB PENDETIDE** (CHEMBL1743091) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V6RC
- **LEVORMELOXIFENE** (CHEMBL301327) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0W9GA
- **LOBAPLATIN** (CHEMBL4594256) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0S4QZ
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01483300
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05546255
- **MEGESTROL ACETATE** (CHEMBL1201139) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02IRD
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04GJN
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02269670
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03024580
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03306472
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01237327
- **MERIMEPODIB** (CHEMBL304087) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0F0ZE
- **MITOMYCIN** (CHEMBL105) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y0GH
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01196455
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02299999
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003893
- **NOMEGESTROL ACETATE** (CHEMBL1476022) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V2JK
- **OXIDIZED GLUTATHIONE** (CHEMBL2074781) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V4TY
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00499122
- **PEPLOMYCIN** (CHEMBL3990196) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08HJT
- **PIRARUBICIN** (CHEMBL2354444) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T8EH
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05558722
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02613026
- **PRALATREXATE** (CHEMBL1201746) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02LWU
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01118624
- **QUINESTROL** (CHEMBL1201165) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04UZT
- **RIVOCERANIB** (CHEMBL3186534) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0SZ6E
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03075462
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03945604
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05019690
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01653561
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02768415
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02878057
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03086785
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03457467
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03535961
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03650738
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03775928
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03982485
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05192798
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05447702
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05582499
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05594095
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05759572
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06339281
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03580395
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04296370
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04335006
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05889871
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06255392
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06447623
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06913777
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07371910
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03925233
- **TALAPORFIN** (CHEMBL2111186) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04WJO
- **TECHNETIUM TC 99M TETROFOSMIN** (CHEMBL1200857) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05HFN
- **TESTOLACTONE** (CHEMBL1571) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0C7JF
- **THIOTEPA** (CHEMBL671) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00YZA
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002616
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004174
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002780
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003086
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003877
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006123
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00001498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003068
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003199
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004092
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004900
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004906
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005798
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00012311
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00020722
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00060255
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182793
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00429182
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00851110
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06543992
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07263425
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00448266
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01057069
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002755
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002772
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002836
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002870
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003680
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003972
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00008203
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01646034
- **ATEZOLIZUMAB** (CHEMBL3707227) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03802604
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04102618
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04630210
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05238831
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02605915
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02914470
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03170960
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03650348
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05581004
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03280563
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03566485
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03568656
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03881878
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04802759
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05253053
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06067061
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00781612
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02322814
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02693535
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02849496
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02883062
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02924883
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03125928
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03164993
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03202316
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03206203
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03395899
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03417544
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03483012
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03894007
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03915678
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03952325
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04273061
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04434040
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04591431
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04690855
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04759248
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04819243
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05180006
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05266937
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05332561
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06793553
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03199885
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03498716
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03595592
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03726879
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04732598
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04740918
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04873362
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D0YM2K
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05609903
- **BEVACIZUMAB** (CHEMBL1201583) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00949247
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02802098
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02806817
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05238831
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00543504
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00732056
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00960960
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01197170
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01254526
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01803282
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06307249
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318805
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00095706
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00368875
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00468585
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00691379
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00705315
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02734004
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03175666
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03387085
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05792410
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06718933
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00017394
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00027885
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00054132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00055861
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00083031
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00088998
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00119262
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00161291
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00203372
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00203502
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00217672
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254592
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00281528
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00305825
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00320541
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00356681
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00364611
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00365365
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00365417
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00370552
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00378638
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00392392
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00394082
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00394251
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00403130
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00404404
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00405938
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00423917
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00428922
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00434356
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444535
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00445406
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00446030
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00461773
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00462865
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00464646
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00467012
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00472693
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00476827
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00479674
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00503906
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00511459
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00517361
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00530868
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00536939
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00546156
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559754
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559845
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00576901
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00580333
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00608972
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00618657
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00618826
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00623233
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00632541
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00654836
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00662129
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00670982
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00675259
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00679029
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00694200
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00717405
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00723125
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00733408
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00754351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00773695
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00811135
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00820547
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00830544
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00845910
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00846027
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00856492
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00861705
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00915603
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00925652
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00957125
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00964704
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00979641
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01004172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01025349
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01069796
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01120158
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01142778
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01186991
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01190345
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01195298
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01201265
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01208480
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01281696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01321775
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01367028
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01658033
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01690325
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01722968
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01959490
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01985841
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01989780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02005549
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02175446
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02299999
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02436993
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02456857
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02829008
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03395899
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03577743
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04303988
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04389073
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05180006
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05192798
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05357417
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05398861
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05594095
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05769010
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06152822
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06210438
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06361979
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06539559
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06793553
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06976944
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07065435
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07150208
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07351487
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07359404
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07446452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07449481
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01426880
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00028990
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00109239
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00262067
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00281697
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00333775
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00391092
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408408
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00433511
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00448591
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00520975
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00528567
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00545077
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00567554
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00600340
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00601900
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00625898
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00785291
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00868634
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00929240
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01093235
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01131195
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01200212
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01250379
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01303679
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01663727
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01935492
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03462251
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04732598
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D04SLF
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00121836
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00774241
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01094184
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01156961
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02248571
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05525767
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00121134
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00436709
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00537173
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00911716
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01159236
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01215123
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01652560
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01745757
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03925233
- **DATOPOTAMAB DERUXTECAN** (CHEMBL4297939) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06244485
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05417594
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06176261
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06533826
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06954480
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05104866
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07205822
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/DP41HV
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07582887
- **LEUPROLIDE** (CHEMBL1201199) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01823835
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02990845
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00903162
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01989780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02344550
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02592746
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02689921
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03272477
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03497702
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03573648
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03879577
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03900637
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03944434
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06001762
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225284
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07158021
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07159451
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07179939
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002580
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002582
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01546649
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01674140
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02344472
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02914158
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02980965
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03664895
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04906395
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05827081
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05891093
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06065748
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06449027
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02134977
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02154139
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03209518
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04891731
- **PAMIDRONIC ACID** (CHEMBL834) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004092
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01067989
- **FORMESTANE** (CHEMBL132530) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0B6PZ
- **NOMIFENSINE** (CHEMBL273575) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06BPG
- **CAPIVASERTIB** (CHEMBL2325741) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01ZAQ
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01226316
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02208375
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03310541
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03616587
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04556773
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01992952
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05455619
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05563220
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02077569
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02299999
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02423603
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03182634
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05720260
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06607757
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06613516
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06837792
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07426822
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04305496
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04862663
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06635447
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06764186
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07281833
- **TALAZOPARIB** (CHEMBL3137320) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0GV8J
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02358200
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02627430
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03343054
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04134884
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04635631
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04703920
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01989546
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03911973
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03964532
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04039230
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05035745
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02034916
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02282345
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02401347
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02693535
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03499353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03565991
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03990896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04591431
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04690855
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04755868
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04756765
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04819243
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04849364
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04892693
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05288127
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06193525
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01945775
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04982848
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04987931
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05141708

#### prostate cancer (MONDO_0008315)

- **ABARELIX** (CHEMBL1252) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01AHO
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00100243
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00841113
- **ABIRATERONE** (CHEMBL254328) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02STN
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01574937
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02380313
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03110588
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03150056
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03569280
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04087174
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04108247
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04179396
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04221542
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04296578
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04628988
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04666129
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04677855
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05177042
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05733351
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07140900
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07570979
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01485861
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02049190
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03480646
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04179864
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04631601
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04839055
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06863272
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07190300
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07226986
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01553188
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01677897
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01828476
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01972217
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01995058
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02254785
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02429193
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02758132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02789878
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02867020
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03298087
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03414034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03418324
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03696186
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03770455
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03934840
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04748042
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04926155
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05189457
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05361915
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05705700
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06060587
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06134271
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06173362
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06378866
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06505278
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06655259
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06818682
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06832774
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06991556
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07093866
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07237269
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07299292
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07553988
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03348670
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04787744
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01949337
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02043678
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03072238
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03678025
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04647526
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04689828
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05204927
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05288166
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06520345
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06592924
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06764485
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01995513
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02366494
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03325127
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03896984
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034095
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04983095
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05188911
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05701007
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05707468
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06072196
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06151418
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07154914
- **BICALUTAMIDE** (CHEMBL409) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V9BD
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01050842
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03358563
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00026377
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00099086
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00328614
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00512668
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00631527
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702923
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00943956
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01420250
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02064036
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02458716
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02487823
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04284761
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04943536
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00075192
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00669162
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00878436
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01020305
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03553602
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03587285
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006359
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00031889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00086736
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00103376
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00108732
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00165399
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00170157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00298155
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00319787
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00348998
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00349557
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00418080
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00430235
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00486642
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00500110
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00528866
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00544830
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00554086
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00586898
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00589472
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00630344
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00658697
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00659438
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00666666
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00684905
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00685633
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00757692
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00769795
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00771017
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00776594
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00777959
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00814788
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00866554
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01120236
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01200810
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01250717
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01251861
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01288911
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01658527
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01664923
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01786265
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02058706
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02582749
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02614859
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02678520
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02716974
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02742675
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03043807
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03147196
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03541850
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03541928
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04734730
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06528210
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07455903
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00421694
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03070886
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03348670
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04787744
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002651
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002874
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003026
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003653
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004054
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004124
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005044
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00014586
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00021450
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00023829
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00030654
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00055731
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00067015
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00138008
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00243646
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00288080
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00388804
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00541047
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00567580
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00651326
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00657904
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00672282
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00673205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00831233
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00833248
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00841113
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00846976
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00884273
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00936390
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00949962
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01368588
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01809691
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02085252
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02382094
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03119857
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03520478
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03678025
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04513717
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05019846
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05050084
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00536653
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00551044
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00636259
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01342367
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02346253
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02366494
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02605226
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02615223
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034095
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06198387
- **CAPROMAB** (CHEMBL2108285) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09PGL
- **CYPROTERONE** (CHEMBL142130) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06AEO
- **ESTRAMUSTINE** (CHEMBL1575) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03SRY
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002721
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005627
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00038246
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00132756
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00151086
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003084
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003614
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005810
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005847
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00016913
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00028769
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00165399
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00183924
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00193271
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00541281
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01250717
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02494713
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02560051
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004001
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00027859
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00030654
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00705822
- **FLUCICLOVINE** (CHEMBL1908917) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03QIP
- **FLUTAMIDE** (CHEMBL806) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y0SW
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03507608
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00026377
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00054106
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00512668
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03553602
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003124
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003323
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006359
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00103376
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00170157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00223665
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00450463
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00528866
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00817739
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01786265
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02346578
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02742675
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03541850
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03070886
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04787744
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06601205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002881
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003026
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003645
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003653
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003734
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004054
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005044
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00023829
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00030654
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00104741
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00116220
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00288080
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00388804
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00567580
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00651326
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00936390
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00949962
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01122121
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01368588
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03678025
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04513717
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05050084
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02918968
- **HYDROXYFLUTAMIDE** (CHEMBL491) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0BC2E
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00913263
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02341404
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03348527
- **MASOPROCOL** (CHEMBL313972) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U3YB
- **POLYESTRADIOL PHOSPHATE** (CHEMBL1201477) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03DXN
- **TALAZOPARIB** (CHEMBL3137320) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04635631
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04703920
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04846478
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05425862
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03330405
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03553602
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04019327
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04052204
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03148795
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03541850
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03565991
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04332744
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04734730
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04824937
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05873192
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06582628
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06844383
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00949962
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05650476
- **ATRASENTAN** (CHEMBL9194) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00038662
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00181558
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00127478
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00036543
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00036556
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00046943
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00134056
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y6UU
- **PREDNISONE** (CHEMBL635) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01217697
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511196
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003633
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00419536
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00910754
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00916123
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01017939
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01054313
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01378091
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01385228
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01400555
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01594918
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02123758
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02182622
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02913196
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02924766
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03110588
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04291664
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04421222
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04577833
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04628988
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04662580
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04666129
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04729114
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06099990
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00137436
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00293371
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00331344
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00459186
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00503984
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00770848
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00879619
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00996502
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01084655
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01234025
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01468532
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01511536
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01683994
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01688492
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01717898
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01848067
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02494921
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02861573
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03480646
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04060394
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04179864
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05405439
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06689163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00072930
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00087165
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00089609
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182741
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00258388
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00268593
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00313482
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00313781
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00348816
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00350051
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00385827
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00411528
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416533
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00436956
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00452387
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00466440
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00527124
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00537381
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00541281
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00544440
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00571675
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00598858
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00634647
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00683475
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00734851
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00811031
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00924469
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00942578
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01023061
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01051570
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01087580
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01088529
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01120470
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01145508
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01254513
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01254864
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01309672
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01314118
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01424930
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01469338
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01478308
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01553188
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01576172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01619813
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01637402
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01717053
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01750866
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01786265
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01867710
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01940276
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01946165
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02077634
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02217566
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02268175
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02429193
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02685267
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02703623
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02758132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02789878
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02807805
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02844582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02849990
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02903368
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02928432
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02949284
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02960022
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03007732
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03230734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03263650
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03279250
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03356912
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03414034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03419234
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03565835
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03649841
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03696186
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03764540
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03821792
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03833921
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04175431
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04267887
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04356430
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04734730
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04748042
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04812366
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04947254
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04992026
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05156450
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05167175
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05489211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05689021
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05848011
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06173362
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06378866
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06384222
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06527690
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06890832
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06971211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07005154
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07237269
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004071
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03348670
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03706365
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04787744
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003232
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003343
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004124
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00024167
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00069745
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00089856
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00110214
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00132301
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00134056
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00255606
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00288080
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00417079
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00436839
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00519285
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00638690
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00676650
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00988208
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01188187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01193257
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01308567
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01308580
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01578655
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01695135
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01715285
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01949337
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02043678
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02257736
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02961257
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03072238
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03678025
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03748641
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04056754
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04497844
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04691804
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06470243
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06650579
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01649635
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01995513
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01834209
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01961843
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02208583
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03449719
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05188911
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06652607

#### colorectal cancer (MONDO_0005575)

- **CAPECITABINE** (CHEMBL1773) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00HCQ
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003704
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00019773
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00084643
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00291486
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00296062
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00353262
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00387387
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00532909
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00536809
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00777478
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01158274
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01306630
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01493336
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01705002
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01843725
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01846650
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02009449
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02210364
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02720926
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02892123
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03153280
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04420871
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05464030
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06065371
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06621563
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06825624
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06848465
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06963502
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07453875
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004187
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00081536
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00087334
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00217711
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345761
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444041
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00496704
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00784446
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00819754
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01193517
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01661972
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01955629
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02393755
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02861300
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03169777
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03470350
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03564912
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03904537
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04008511
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04031872
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04227041
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04380103
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04564898
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04751955
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04753203
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04940546
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05016869
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05093907
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05289076
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05700656
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05775900
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05990543
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06324357
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06394791
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07283367
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07365592
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00022698
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00030797
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00048126
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00048139
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00049335
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070265
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00104689
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00107315
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118105
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118755
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00120172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00123851
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00159432
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00159445
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00165217
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00177307
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00203411
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00205322
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00215982
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00220116
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00227734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00230399
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00251186
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00258232
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00290615
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00303745
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00314353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00321100
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00378066
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00398879
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408772
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416494
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00423696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444678
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00459901
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00483834
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00506168
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00514761
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00531115
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00538291
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00551213
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00574171
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00640081
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642603
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00659022
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00675012
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00677144
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00700570
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00717990
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755534
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00853684
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00875771
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00950820
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00954876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00961571
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01022541
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01024504
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01071655
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01077739
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01131078
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01135498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01159171
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01215539
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01290926
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01293942
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322152
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01409005
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01471353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01472770
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01508000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01511146
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01531595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01632722
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01668680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01677884
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01679327
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718808
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01722162
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01729923
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01736904
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01759238
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01765582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01776307
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01845337
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01880658
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01993472
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02027363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02068131
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02075086
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02079220
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02083653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02085005
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02119026
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02271464
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02280694
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02414009
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02415829
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02595320
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02688023
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02780700
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02829385
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02842580
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02870153
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02873195
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03050814
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03132025
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03146377
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03396926
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03485027
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511170
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03645876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03748680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03792269
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03813641
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03854799
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03929666
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03984578
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034459
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04097444
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04160416
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04247984
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04262687
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04301557
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04310176
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04324476
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04425564
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04508452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04534218
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04659382
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04733963
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04866108
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05022030
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05068206
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05092880
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05136326
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05262335
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05375708
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05438108
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05451719
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05489211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05578287
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05648006
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05659290
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05799820
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05985707
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06014372
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06148402
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06192680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06206096
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06332079
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06405139
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06425133
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06490913
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06493760
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06555133
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06593548
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06850103
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06858969
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06881537
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06885385
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06888843
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06949982
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07007728
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07051785
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07215936
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07229846
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07233850
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07243938
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07395063
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07407465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07478731
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07503639
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07512674
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562503
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562659
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562711
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212615
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00294359
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01196260
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01646554
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02529774
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02893540
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03158610
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03577392
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05141721
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05409417
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05673512
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07462143
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00062426
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00064181
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00069095
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00069108
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070122
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070213
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101686
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00112918
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00126256
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182715
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00202774
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212589
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00268463
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00312000
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00335595
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00349336
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00394992
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00396487
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00442637
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00469443
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00482222
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00484939
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00630045
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00677443
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00700102
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00749450
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00797485
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00905047
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00973609
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01080547
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01097018
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01229813
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01249638
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01279681
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01606098
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718873
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01918852
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01996306
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02060669
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02316535
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02355379
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03300609
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03389659
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03448549
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03828227
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03950154
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04188145
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04607421
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04854668
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05008809
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05074966
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05171660
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05236972
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05327751
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05699746
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06275958
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06616259
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025239
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07132008
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07340567
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07528209
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00577031
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02567331
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02575378
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03465202
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00250029
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01280643
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01311050
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01399190
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01664494
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01696695
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01792934
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02043821
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03228043
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03451370
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04131803
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04718038
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05544812
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05742620
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05832398
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06115733
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06169202
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06504875
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06504901
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07494578
- **CETUXIMAB** (CHEMBL1201577) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0N5OV
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00835679
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06011772
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318389
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00134069
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00207051
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00207155
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00397384
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00403052
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00436072
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00497497
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00501410
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00540943
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00543504
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00593060
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00719199
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00820417
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00925015
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01198535
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01254617
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01287130
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01294826
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01871311
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01973868
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02095054
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02110082
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02124148
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02205398
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02215720
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02573220
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02630420
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02675946
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02845999
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03290937
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03319459
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03356158
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03491709
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03774680
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04449874
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04485013
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04929223
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05019534
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05040568
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05155124
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05355701
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05497336
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05674526
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05722327
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05743036
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05954871
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05985954
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06102902
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225622
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06358430
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06585488
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06917079
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318805
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07535112
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101348
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00361244
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00422773
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00522665
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00551421
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00594984
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00778830
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00908024
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01008475
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01086267
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01166035
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01252628
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01960023
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02117466
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02278133
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02318901
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02713373
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02826837
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02953782
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03169777
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03428958
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03785249
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04017650
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04495621
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04585035
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04616183
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04790448
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05009329
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05039177
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05194995
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05200442
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05289076
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05410145
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05775900
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05786924
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06024174
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06379399
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06412198
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06776757
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07012954
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07204574
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07411599
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005076
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00020917
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00020930
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00055419
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00077298
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00100841
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00125034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00193219
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00202787
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00215722
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00227734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00251186
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00251485
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00271011
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00286130
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00290615
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00309179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00321100
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00326495
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00336856
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00437268
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00438737
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00439517
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444678
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00466505
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00479752
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00503685
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00513266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00531115
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00537823
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00538291
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00544349
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00551213
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00556413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00557102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559741
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00571740
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00577109
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00598975
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00614393
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00637091
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00640081
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00660582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00681876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00689624
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00743678
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755118
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755534
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00766142
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00766220
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00784667
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00803647
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00845039
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00852228
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00954876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01004159
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01032291
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01051167
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01060423
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01068132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01079780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01152437
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01161316
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01190462
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01225744
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01251536
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01276379
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01281761
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322178
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01387880
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01442935
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01450319
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01511146
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01522612
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01523639
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01524978
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01540344
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01703390
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718808
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01719380
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01776307
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01802645
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01832467
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01836653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01867697
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01892527
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01919879
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02063529
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02071069
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02164916
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02292758
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02316496
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02515734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03391843
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03446157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03524820
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03608046
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03693170
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03727763
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03874026
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034459
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04117945
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04160416
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04189055
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04224415
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04241731
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04466254
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04513951
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04515394
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04554836
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04587128
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04595266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04745130
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04833036
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04853043
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04984369
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05004350
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05022030
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05103020
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05104567
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05143099
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05160896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05167409
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05217069
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05217446
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05278351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05308446
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05312398
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05510895
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05576896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05619172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05694936
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05725200
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05774964
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05799443
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05959356
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05962502
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06207656
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06231017
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06279351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06321081
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06369259
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06411600
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06490913
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06525428
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06540326
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06547203
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06575127
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06578559
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06603376
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06640166
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06763029
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06959589
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06967155
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06978400
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07000305
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07044921
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07059338
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07070713
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07253896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07381764
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07415031
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07446270
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07474727
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07490119
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07503639
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07506109
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07515963
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07559760
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01550055
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02942706
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02978313
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05409417
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00077233
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00145314
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00154102
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182715
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00252564
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00265850
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00433927
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00482222
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00499369
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01001377
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01030042
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01228734
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01338558
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01878422
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02563002
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02934529
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03426371
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04607421
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04687631
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04793958
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05074966
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05239741
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05540951
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05863195
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06226857
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06616259
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06997497
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07004413
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07389265
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07595276
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00327093
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01074333
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01134666
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01280643
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01631539
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01834014
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01943786
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02831842
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03263663
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03286738
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03914170
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04131803
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04718038
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04831528
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05424692
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05544812
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05963087
- **EDRECOLOMAB** (CHEMBL2108955) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09MVZ
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002664
- **FLOXURIDINE** (CHEMBL917) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0TS1Z
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00001576
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00008294
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00059930
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00695201
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00645710
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002842
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004142
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00019760
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00063960
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00200200
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408551
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00449163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00492999
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01312857
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01815359
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03069950
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02529774
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002716
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00020501
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00268463
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03500874
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05863195
- **FRUQUINTINIB** (CHEMBL4303214) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03JTG
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06347198
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06380309
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03251378
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03977090
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01975077
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04577963
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05016869
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05522738
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06195670
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06980532
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025850
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07491159
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07591597
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02196688
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04179084
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04296019
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04582981
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04716634
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04733963
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04866108
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04866862
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04924179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04948034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05004441
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05004831
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05025631
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05279677
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05435313
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05447715
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05451719
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05555901
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05634590
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05659290
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05690035
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05771181
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05842525
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05954429
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06010888
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06148402
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06168786
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06218888
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06255379
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06356584
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06356597
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06423937
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06427005
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06484153
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06685276
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06746545
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06856837
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06979908
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06992258
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07003022
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07011576
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07042685
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07051785
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07130903
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07136077
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07150403
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07229872
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07257653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07261709
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07286695
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07353268
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07502014
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07510932
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07515820
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06441565
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02314819
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04322539
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06199973
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07362836
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06562543
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04431791
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05928312
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05993702
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06011330
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06031376
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06099314
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06115733
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06169202
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06202417
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06221423
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06470178
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06551207
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06613113
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06985316
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07124858
- **IRINOTECAN** (CHEMBL481) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07HOB
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06011772
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318389
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003427
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00026364
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00084721
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101894
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00134069
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00296062
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00403052
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00436072
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00497497
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00535353
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00540943
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00563316
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00695201
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00719199
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00777478
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00780169
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00921661
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00925015
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00934882
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01124630
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01183494
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01189942
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01205022
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01274624
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01285102
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01304602
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01347866
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01383343
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01520389
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01605344
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01643499
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01803282
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01859858
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01923337
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02110953
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02453464
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02482441
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02573220
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02588105
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02640365
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02641873
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02720068
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02726334
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02833753
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02906059
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03035253
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03250832
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03290937
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03380689
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03692429
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04485013
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04535401
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04627142
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04929223
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05087992
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05722327
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06143774
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225622
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06509906
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06621563
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06663319
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06833866
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06867822
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06963502
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07363408
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07543744
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003225
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004870
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005818
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00034502
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209625
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00217711
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00361244
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00422773
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00522665
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00551421
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00594984
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00778830
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00816777
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00819754
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00838578
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00932438
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00989469
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01008475
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01085331
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01133990
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01139138
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01394939
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01550510
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01675128
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01896856
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01937715
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01941316
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02244632
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02568046
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02785068
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03076957
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03184870
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03368963
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03428958
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03454620
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03545711
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03795311
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03828799
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03829410
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04247256
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04256707
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04337879
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04368507
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04380103
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04492033
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04689347
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04790448
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04929652
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04988191
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05278728
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05289076
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05522738
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05786924
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06202001
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06341309
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06434090
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06936527
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07204574
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07391566
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002933
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003544
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003950
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003995
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005076
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006037
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006115
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006786
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00016952
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00020917
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00022698
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00027833
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00030563
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00030797
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00039208
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00048126
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00048139
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00052585
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00063960
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00066274
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00075595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00077298
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080951
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00098787
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00111761
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00191984
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00200200
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209651
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00215982
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00230399
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00233623
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00258232
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00271011
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00286000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00286130
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00303745
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00313859
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00314353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00320320
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00323011
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00332163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00336856
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00354978
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408551
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00411450
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00423696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00437268
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00449163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00454116
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00467142
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00475293
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00483834
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00492999
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00493857
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00506168
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00506571
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00508404
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00513266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00551213
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00556413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00557102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559741
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00569335
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00569790
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00577109
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00588900
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00614393
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00615056
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00628810
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00637091
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642603
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642746
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00655499
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00668863
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00681876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00689624
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00717990
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755118
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755534
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00766220
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00778102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00792363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00806663
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00827684
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00839111
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00845039
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00851045
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00852228
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00856375
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00875771
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00885885
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00940303
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00940316
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00958386
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00969033
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00972465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01004159
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01060423
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01068132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01071655
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01079780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01116271
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01131078
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01144195
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01163396
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01205711
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01225744
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01226719
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01251536
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01276379
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01281761
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01293942
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01298570
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01312857
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01321957
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322152
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322178
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01326000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01328171
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01358812
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01367275
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01374425
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01375816
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01387880
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01417494
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01442935
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01523639
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01531595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01632722
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01639326
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01652482
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01677884
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01703390
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01704703
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01715441
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01736904
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01765582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01802645
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01814501
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01839877
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01853813
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01858649
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01862003
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01867697
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01882868
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01925274
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01930864
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01963182
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02015754
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02045030
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02046538
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02063529
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02071069
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02075086
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02119026
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02128425
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02129257
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02138617
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02164916
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02173990
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02181556
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02246049
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02292758
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02305758
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02316496
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02376452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02439385
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02497157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02508077
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02515734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02624726
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02688023
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02842580
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02970916
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02980510
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03053167
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03069950
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03126071
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03142516
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03146377
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03185988
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03193814
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03222089
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03279289
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03329183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03368859
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03391843
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03401294
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03412994
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03485027
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03487939
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511170
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03567629
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03608046
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03641976
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03678883
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03721653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03751176
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03792269
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03874026
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03880877
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03940131
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034173
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034459
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04072198
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04097444
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04109924
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04117945
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04160416
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04189055
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04215159
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04224415
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04247984
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04324476
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04499586
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04508452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04513951
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04595266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04734249
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04833036
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05004441
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05018182
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05031975
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05035381
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05039944
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05103020
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05143099
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05160727
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05160896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05200299
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05217069
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05229003
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05278351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05312398
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05354817
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05435313
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05453825
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05462236
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05593328
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05634590
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05678257
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05684211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05727163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05732129
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05797883
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05799443
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05806931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05839470
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05843188
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05854498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05959356
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05962502
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05969899
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05983367
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06010888
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06071052
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06089330
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06106308
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06184698
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06192680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06242067
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06279351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06321081
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06341296
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06403709
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06405139
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06525428
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06540326
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06547203
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06575127
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06603376
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06640166
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06643793
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06652412
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06665087
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06714357
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06763029
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06792695
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06835179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06855849
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06907342
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06959589
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06967155
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07011576
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07042685
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07044921
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07047560
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07051785
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07059338
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07070713
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07106034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07123441
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07150247
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07150403
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07229846
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07253896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07359456
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07381764
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07395063
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07415031
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07441369
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07446322
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07515963
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07559760
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00284258
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00952029
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01523431
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01550055
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07221357
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07585279
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003260
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003594
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004885
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005036
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006103
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00008060
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00012389
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00020501
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00021281
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00023868
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00026273
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00064181
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00077233
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101686
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00115765
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00126256
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00143403
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00154102
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00265850
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00268398
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00303771
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00312000
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00316745
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00389870
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00396487
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00433927
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00440310
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00457691
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00469443
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00499369
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642577
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00719797
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00720512
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00797485
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01030042
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01183780
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01219920
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01249638
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01290783
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01566942
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01571284
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01640405
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01670721
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01878422
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01996306
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02087475
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02162563
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02563002
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02605044
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02753127
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02885753
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02934529
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02935764
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03288987
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03303495
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03500874
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03522649
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03829462
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04094688
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04230187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04338191
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04392479
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04607421
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04687631
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04781270
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04861558
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05008809
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05239741
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05362617
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05427669
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05540951
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05863195
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05954078
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06197425
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06252649
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06509126
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06662786
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06733038
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06750094
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06951503
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07004413
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07134205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07271355
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07340567
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07362836
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07389265
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00510627
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003843
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00173472
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00507143
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01039506
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01280643
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01311050
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01533740
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01631539
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01847495
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01941173
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01943786
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02256800
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03369041
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03730558
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03914170
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04131803
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05362825
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05391126
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05424692
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05832398
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06169202
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06177288
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06443307
- **NECITUMUMAB** (CHEMBL1743047) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03WPP
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00835185
- **NINTEDANIB** (CHEMBL502835) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09HNV
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02835833
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02393755
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00801294
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00904839
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01362361
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02780700
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02149108
- **OXALIPLATIN** (CHEMBL414804) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y3ME
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06011772
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318389
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07328087
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003427
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00008294
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00019773
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00059930
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00060411
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00081237
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00084643
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00098982
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101894
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118261
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00138177
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00199797
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00296062
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00343408
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00353262
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00387387
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00458809
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00501410
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00532909
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00536809
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00599924
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00631410
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00660153
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00695201
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00779311
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00851136
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00873275
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00873756
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00934882
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01164215
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01420874
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01643499
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01803282
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02009449
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02041481
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02384850
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02720068
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02720926
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02833753
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02848443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03035253
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03153280
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03172416
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03176264
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03250832
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03626922
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03692429
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03720678
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04158349
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04329494
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04761614
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04929223
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04991948
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225622
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06269978
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06621563
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06663319
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06696768
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06743867
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06825624
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06963502
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318805
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07453875
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004187
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005050
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00026299
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00049101
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00055822
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00087334
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00166465
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00217711
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345761
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00422773
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444041
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00494221
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00496704
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00524706
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00531245
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00625651
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00778830
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00784446
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00819754
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00932438
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01047293
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01110941
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01193517
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01206530
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01490996
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01955629
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02102022
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02244632
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02826837
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02848079
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03169777
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03202758
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03294252
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03428958
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03564912
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03795311
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03828799
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03904537
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04008511
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04337879
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04380103
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04940546
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05289076
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05627635
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06324357
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06922383
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06936527
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07204574
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07283367
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07365592
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003834
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006050
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006115
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00017082
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00034619
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00039208
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00051688
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00065117
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00066274
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070265
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00072553
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080951
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00098787
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00100841
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00103298
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00104689
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00116506
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118105
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118755
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00120172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00123851
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00125034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00159432
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00177307
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00192075
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00193219
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00200200
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00202787
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00205322
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209703
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00215982
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00220116
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00227734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00251485
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00268333
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00286130
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00290615
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00314353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00321100
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00378066
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00385021
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00399750
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408551
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408772
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416494
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00438737
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00439517
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444678
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00479752
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00492999
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00500292
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00506571
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00508872
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00513266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00531115
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00537823
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00544349
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00551213
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00556413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00609622
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00615056
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00640081
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642603
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642746
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00659022
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00660582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00675012
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00677144
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00689624
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00700570
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00707889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00721916
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00743678
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755118
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755534
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00766142
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00778102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00803647
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00813137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00819780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00835185
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00851084
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00852228
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00853684
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00862784
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00865709
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00885885
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00904839
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00940303
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00950820
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00988897
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01022541
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01024504
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01051167
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01071655
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01077739
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01111604
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01135498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01159171
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01161316
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01163396
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01198548
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01215539
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01225744
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01226719
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01270438
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01288339
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01289821
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01293942
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01321957
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322178
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01328171
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01348412
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01358812
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01362361
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01374425
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01383707
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01384994
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01399684
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01417494
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01418222
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01442935
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01478594
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01508000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01511146
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01529164
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01531595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01532804
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01540344
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01632722
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01652196
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01679327
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01703390
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01715363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01765582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01802645
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01832948
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01836653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01839877
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01858649
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01867697
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01889680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02046538
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02063529
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02079220
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02085005
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02119026
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02128425
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02141295
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02246049
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02345746
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02375672
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02413853
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02415829
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02476045
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02497157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02515734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02688023
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02821559
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02829385
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02842580
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02870153
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02904031
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02980510
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03043729
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03050814
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03126071
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03146377
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03193814
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03222089
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03287375
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03377842
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03388190
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03391843
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03401294
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03412994
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03485027
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03487939
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03530267
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03547999
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03567629
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03641976
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03645876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03721653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03748680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03792269
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03929666
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03940131
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03984578
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034459
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04072198
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04097444
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04145193
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04160416
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04169347
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04262687
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04301557
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04310176
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04324476
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04425564
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04430985
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04508452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04513951
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04595266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04659382
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04734249
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04894123
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04895137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05004441
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05018182
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05022030
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05039944
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05068206
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05077839
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05103020
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05200299
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05239650
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05262335
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05312398
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05354817
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05378919
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05480280
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05504252
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05634590
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05727163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05774964
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05797883
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05799820
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05806931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05839470
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05959356
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05985707
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06002789
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06010888
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06014372
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06106308
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06154538
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06206096
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06218810
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225843
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06268015
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06279351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06367270
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06405139
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06415851
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06490913
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06491355
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06575127
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06652412
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06665087
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06820463
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06835179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06881537
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06885385
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06888843
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06907342
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06948448
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06978400
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07000305
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07007728
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07042685
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07070713
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07106034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07150403
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07229846
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07233850
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07243938
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07415031
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07441369
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07478731
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07503639
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07542262
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562490
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562503
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562711
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212615
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00274872
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00384176
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01196260
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01646554
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02415699
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02529774
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03414983
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03577392
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05409417
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05673512
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05945901
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06441565
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06509880
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07221357
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07462143
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003260
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003287
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003594
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005036
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006468
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00008060
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00012389
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00025337
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00056459
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00062426
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00069095
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00069108
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070122
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070213
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00077233
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00112918
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00115765
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00126256
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00145314
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182715
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00202774
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00252564
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00265850
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00268398
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00268463
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00312000
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00316745
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00335595
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00349336
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00364013
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00394992
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00440310
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00482222
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00630045
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00677443
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00719797
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00720512
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00749450
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01030042
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01035385
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01080547
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01219920
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01228734
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01279681
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01566942
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01640405
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718873
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01786538
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01878422
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02162563
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02355379
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02394795
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02503150
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02563002
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02785146
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02885753
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02965248
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02969681
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02997228
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03028155
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03300609
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03365765
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03389659
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03448549
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03500874
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03950154
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04094688
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04230187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04233151
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04338191
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04607421
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04687631
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04781270
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04854668
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04861558
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05008809
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05074966
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05171660
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05236972
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05239741
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05253651
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05362617
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05378867
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05427669
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05699746
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05797467
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05863195
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05954078
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06275958
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06293625
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06616259
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06662786
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06733038
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06791512
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06951503
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06997497
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025239
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07132008
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07228832
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07284394
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07340567
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07362836
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07389265
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00129870
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00510627
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00577031
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00039611
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00040820
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00173472
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00250029
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00724503
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00846482
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01280643
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01311050
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01399190
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01792934
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01834014
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02394834
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03451370
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03914170
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04131803
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05362825
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05424692
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05544812
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05742620
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05832398
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06504901
- **TECHNETIUM** (CHEMBL1201315) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X2RJ
- **VOTUMUMAB** (CHEMBL2108157) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X2RJ
- **ANAMORELIN** (CHEMBL2110579) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **BEVACIZUMAB** (CHEMBL1201583) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06011772
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318389
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00047762
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00060411
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118261
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00296062
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00353262
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00543504
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00586443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00779311
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00851136
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00873275
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00873756
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01183494
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01205022
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01274624
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01383343
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01705002
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01803282
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02069704
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02640365
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02641873
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02835833
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02848443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02876224
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03176264
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03250832
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03380689
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04761614
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04929223
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05070104
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05087992
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05464030
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05824559
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225622
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06307249
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06448364
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06663319
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06696768
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06717880
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06825624
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06838338
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06867822
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318805
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07500298
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101348
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345761
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444041
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00460603
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00625651
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00784446
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00819754
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00932438
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01047293
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01133990
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01206530
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02826837
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03169777
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03428958
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03555149
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03795311
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03829410
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04380103
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04564898
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04689347
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04940546
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04988191
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05289076
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05589597
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05627635
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06202001
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06341309
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06373133
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06434090
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06873763
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06922383
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06936527
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07012954
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07204574
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07244705
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07283367
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07391566
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006786
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00066846
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00077298
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00098787
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00100841
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00107315
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00109226
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00116506
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118105
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00118755
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00120172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00159432
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00177307
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00192075
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00193219
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00200200
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00203411
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00278889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00290615
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00314353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00321100
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00323011
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00354978
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00378066
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00385021
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00388700
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00399750
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408772
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416494
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00423696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00438737
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00449163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00467142
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00483834
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00508872
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00513266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00537823
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00569335
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00569699
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00569790
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00571740
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00577109
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00612586
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00615056
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00628810
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642603
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00659022
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00681876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00700570
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00717990
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00755118
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00778102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00826540
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00862342
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00875771
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00940303
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00974389
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00988897
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01022541
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01024504
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01057017
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01071655
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01077739
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01131078
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01135498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01159171
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01163396
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01198548
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01249521
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01270438
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01293942
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01321957
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322815
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01374425
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01383707
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01399684
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01417494
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01418222
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01442935
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01508000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01531595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01532804
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01540435
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01622543
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01632722
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01677884
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01679327
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01722162
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01759238
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01765582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01802645
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01836653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01853813
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01858649
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02075086
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02119026
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02138617
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02226289
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02246049
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02271464
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02292758
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02305758
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02413853
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02439385
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02487992
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02497157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02515734
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02654639
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02743221
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02821559
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02842580
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02873195
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02982694
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03050814
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03126071
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03271255
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03396926
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03401294
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03641976
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03645876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03721653
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03843853
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03929666
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034459
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04072198
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04097444
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04109924
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04160416
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04245865
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04247984
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04262687
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04310176
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04324476
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04508452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04527068
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04595266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04659382
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04683965
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04724239
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04895137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05007132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05035381
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05077839
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05092880
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05103020
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05160896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05330429
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05375708
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05438108
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05480306
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05489211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05555901
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05593328
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05659290
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05678257
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05727163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05785325
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05799820
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05806931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05843188
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05854498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05969899
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05983367
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05999812
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06060704
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06092242
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06106308
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06107413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06184698
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06192680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06206096
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06218810
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06229340
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06242067
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06268015
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06293014
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06332079
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06341296
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06363552
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06403709
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06411600
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06415851
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06491355
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06513221
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06522919
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06525428
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06540326
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06563986
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06575127
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06607458
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06643793
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06679673
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06699836
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06764680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06792695
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06835179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06856187
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06858969
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06881537
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06948448
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06949982
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06973343
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07003022
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07007728
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07007767
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07011550
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07044921
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07047560
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07070713
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07071714
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07085169
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07106034
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07116577
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07123441
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07150247
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07229846
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07233850
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07253896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07323576
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07337551
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07355764
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07381764
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07395063
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07407465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07446322
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07474727
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07512674
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07515963
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07527858
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07535632
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07559760
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562490
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00294359
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00952029
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03414983
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05141721
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05409417
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05945901
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06958419
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07585279
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00025337
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00062426
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00069095
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070122
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101686
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00109070
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00112918
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00115765
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00252564
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00265824
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00265850
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00335595
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00349336
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00394992
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00433927
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00442637
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00469443
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00484939
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00499369
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00544700
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00598156
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00642577
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00700102
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00719797
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00720512
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00797485
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00973609
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01229813
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01249638
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01279681
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01338558
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01606098
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01640405
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718873
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01878422
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01996306
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02162563
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02394795
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02563002
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02776683
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02885753
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02969681
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02997228
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03288987
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03303495
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511963
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03635021
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03828227
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03869892
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04094688
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04188145
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04230187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04456699
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04607421
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04687631
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04737187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04781270
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05171660
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05239741
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05378867
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05482516
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05768503
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05797467
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05863195
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06497985
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06566755
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06614192
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06642844
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06733038
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06791512
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06992648
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07025239
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07222800
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07271355
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07389265
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07525206
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D04KBL
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00114946
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00327093
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00577031
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01695772
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06843954
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00537901
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00740168
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01089413
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01280643
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01311050
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01343901
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01399190
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01533740
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01712347
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01775644
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01792934
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01834014
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01860144
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01912443
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02256800
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02612077
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02623621
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02831842
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02842294
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03286738
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03451370
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03743428
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04131803
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04397601
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04446793
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04788381
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04831528
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05009017
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05544812
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05869097
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06031376
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06124729
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06177288
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06682247
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06849362
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06858956
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07494578
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07527832
- **PANITUMUMAB** (CHEMBL1201827) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0HU9H
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06011772
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318389
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004879
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00101894
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00563316
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00586443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00879385
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01791309
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02008383
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02199223
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04185883
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06194877
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07094204
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07543744
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00630786
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00788957
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00867334
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01139138
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01504477
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01591421
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01750918
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01927341
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02613221
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03263429
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03428958
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05786924
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00039273
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00083616
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00089635
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00111761
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00111774
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00113776
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00327119
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00332163
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00411450
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00475293
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00508404
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00655499
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00792363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00819780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00842257
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00885885
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00940316
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00950820
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00958386
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01057017
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01110785
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01126112
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01144195
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01215539
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01226719
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01288339
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01312857
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01328171
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01358812
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01384994
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01508000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01704703
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01776307
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01801904
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01814501
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02399943
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02448810
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02476045
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02508077
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02904031
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02980510
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03069950
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03087071
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03142516
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03227926
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03311750
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03751176
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03940131
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03983993
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03992456
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04034173
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04117945
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04587128
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04595266
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05007132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05576896
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05694936
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05845450
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05993455
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06268015
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06332079
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06575127
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06714357
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06967155
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06978400
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07124884
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00113763
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00115765
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00364013
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00389870
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01001377
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01412957
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02162563
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02394795
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02885753
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03300609
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03635021
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05198934
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05863195
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06252649
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06509126
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02301962
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00853931
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02089737
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02394834
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02831842
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05030493
- **TIPIRACIL** (CHEMBL235668) | group **F** | approval report sources: ClinicalTrials.gov, PMDA | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02286492
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07318389
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02602327
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02848443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03031691
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03305913
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03317119
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03974594
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04511039
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05130060
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05155124
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02613221
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02848079
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03368963
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04564898
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05201352
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06202001
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06379399
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06873763
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07012954
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07044908
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07491159
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02654639
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02743221
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02860546
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03274882
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03844620
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04109924
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04166604
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04683965
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04894123
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05004831
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05007132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05077839
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05343013
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05356897
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05806931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05854498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05970705
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06060704
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06092242
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06293014
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06403709
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06485713
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06522919
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06563986
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06607458
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06699836
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06764680
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06856187
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06992258
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07011550
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07085169
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07116577
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07261709
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07286695
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07381764
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07527858
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01607957
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01955837
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03306394
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03520946
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03869892
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04457297
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04737187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06199973
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06343116
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06614192
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06992648
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07361003
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D04CDO
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03665506
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04965870
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05869097
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05993702
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06031376
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06099314
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06195111
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06495463
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06936488

#### lung cancer (MONDO_0008903)

- **ALECTINIB** (CHEMBL1738797) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U3SY
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05987644
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05770037
- **OLMUTINIB** (CHEMBL3786343) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05NUH
- **PRINOMASTAT** (CHEMBL75094) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00MDP

#### melanoma (MONDO_0005105)

- **DACARBAZINE** (CHEMBL476) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y7ZU
    - IND | TTD | https://ttd.idrblab.cn/data/drug/details/D0XU1I
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00179608
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00412581
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00498979
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00516802
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00542893
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559026
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00580320
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00796991
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00246012
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00327600
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00496223
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00597038
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02076646
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02994498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002669
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004141
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006200
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00066196
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070642
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00099970
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00110994
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00130442
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00308607
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00492297
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00533702
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00553618
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00794235
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00813449
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00911443
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00936221
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01028222
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01055522
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01152788
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01164007
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01376713
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01542255
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01681212
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01692691
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01705392
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01835145
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02190838
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03095079
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04200040
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04225390
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05466474
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06703398
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002882
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003027
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003647
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006237
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00016263
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00072124
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00087776
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00091572
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00257205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00324155
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395070
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00518895
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00779714
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00864253
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01006980
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01227889
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01280565
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01359956
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01721746
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01721772
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01763164
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02545075
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03430297
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070343
- **TILMANOCEPT** (CHEMBL5315077) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09XVS
- **TORIPALIMAB** (CHEMBL4297843) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D92OCI
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02836795
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03086174
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04072900
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04137900
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04197882
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04640545
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04727164
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05451407
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07562841
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04481009
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05148533
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05539118
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05576961
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05723432
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07099430
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03013101
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04248387
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04884997
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05031494
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05274438
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05827770
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05907512
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06965231
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03430297
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04234620
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05478473
- **TREOSULFAN** (CHEMBL455186) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04YPN
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00168870
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00779714

#### chronic myeloid leukemia (MONDO_0011996)

- **INTERFERON ALFA-2B** (CHEMBL1201558) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00303290
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00037882
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00511121
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00573378
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01227356
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01725204
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01866553
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02001818
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03547154
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00219739
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00297570
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00333840
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01490853
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/introna

#### acute lymphoblastic leukemia (MONDO_0004967)

- **THIOGUANINE** (CHEMBL727) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0BK1N
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00439296
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02912676
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002531
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002665
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003671
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00022126
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00109837
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00176462
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00184041
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00558519
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00866749
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01451515
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02419469
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02660762
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02828358
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06124157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06336395
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01228331
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002514
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002744
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002812
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002816
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003437
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003728
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005585
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005596
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005603
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005945
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00075725
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00103285
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00408005
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00430118
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00549848
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00613457
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00671034
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00764907
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01117441
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01190930
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02101853
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02883049
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03007147
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00016302
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00343369
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00550992
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01156883

#### ovarian cancer (MONDO_0008170)

- **ALTRETAMINE** (CHEMBL1455) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02LPF
- **CARBOPLATIN** (CHEMBL1351) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X7HM
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05238831
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05415709
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006155
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006235
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00059618
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00407407
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00652119
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00652691
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00672295
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00877253
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01000896
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01004380
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01016054
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01063816
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01177501
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01237067
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01256268
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01293630
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01314105
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01329549
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01419548
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01445418
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01459380
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01542047
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01930292
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01970722
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01995188
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02050009
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02069158
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02092363
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02199171
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02269293
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02303912
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02476955
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02483104
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02627443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02672098
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02728492
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03056833
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03607955
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03704467
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04516447
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05942300
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06107868
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00032162
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00228319
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00316407
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00421889
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00477386
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00489359
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00562185
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00750386
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00886717
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00910000
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01133756
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01188876
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01618136
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01624493
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01637532
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01650376
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01653912
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01663857
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01690468
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01705158
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02726997
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02756130
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02941523
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03029598
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03249142
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03462212
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04493619
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04954599
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05739981
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05965141
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06087289
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07322094
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003560
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003732
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003733
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003944
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004221
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00021385
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00030446
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00063401
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00069901
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00090610
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00112086
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00127920
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00129727
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00170664
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00181701
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00189566
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00230542
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00247988
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00267696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00316173
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00322881
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00325351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345540
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00373217
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00401674
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00466986
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00490711
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00501644
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00583622
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00698451
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00838656
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00929162
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00945191
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01001910
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01033123
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01033292
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01081951
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01097746
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01124435
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01146795
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01164995
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01332656
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01357161
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01388621
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01462149
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01570582
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01616303
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01696032
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01735071
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01739218
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01767675
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01838538
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01867086
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02001272
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02004093
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02107950
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02122185
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02124421
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02489903
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02520154
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02756013
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02822157
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03025477
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03029611
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03095001
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03188432
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03321188
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03410784
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03467178
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03678883
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03783949
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03983226
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04261465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04282356
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04387227
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04415944
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04661696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04807166
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04815408
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05145569
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05183984
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05201001
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05316376
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05430906
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05460000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05489211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05605535
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06437353
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06446206
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06522828
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06574763
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06964165
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07059845
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07125391
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07285941
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07311577
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07401654
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07407452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07432594
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07448922
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01506856
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02159820
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003214
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003644
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004921
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00102375
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00102414
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00102973
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00189371
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00326456
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00382811
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00660842
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00849667
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01015118
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01837251
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02681432
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02903004
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03038100
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03598270
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03737643
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04337632
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04498117
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05009082
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05255471
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05281471
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05371301
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06980545
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00452985
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01040312
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01606358
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02393898
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02828618
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03562533
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05300828
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05410938
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05921149
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06466382
- **INFLUENZA VIRUS VACCINE** (CHEMBL2109042) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09FHM
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00478387
- **KU-0058948** (CHEMBL380648) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09LSX
- **MELPHALAN** (CHEMBL852) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06XES
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003080
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00583622
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004921
- **MIRVETUXIMAB SORAVTANSINE** (CHEMBL3545132) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0RP2W
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01609556
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02996825
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03552471
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05483933
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06390995
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04274426
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05041257
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05887609
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07059845
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02631876
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04209855
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05445778
- **MIBEFRADIL** (CHEMBL45816) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0W8XT
- **NIRAPARIB** (CHEMBL1094636) | group **F** | approval report sources: ClinicalTrials.gov, PMDA | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03025867
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05238831
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00749502
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01227941
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03154281
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03551171
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03586661
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03695380
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03895788
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03944902
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04149145
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04235101
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04267939
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04502602
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04673448
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05694715
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06161493
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02657889
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04826198
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05198804
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05672095
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06594679
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02354586
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03326193
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03574779
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03759587
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03759600
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03783949
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03891576
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03955471
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03983226
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04217798
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04284852
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04376073
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04392102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04507841
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04556071
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04734665
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05065021
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05126342
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05183984
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05311579
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05335993
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05385068
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05460000
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05523440
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05751629
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05961124
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05990192
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06180356
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06964165
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01847274
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02655016
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03598270
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03705156
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03709316
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03806049
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04679064
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05009082
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05659381
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D00BMF
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03752216
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04861181
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05187208
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04724031
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04785716
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04986371
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05021562
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05734911
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06614790
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06827353
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07059676

#### hepatocellular carcinoma (MONDO_0007256)

- **ALCOHOL** (CHEMBL545) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02338297
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01489410
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04553458
- **DURVALUMAB** (CHEMBL3301587) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05345678
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02572687
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03257761
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04605731
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05155189
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05701488
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06218511
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06470256
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06710223
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07391670
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03942328
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03970616
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04124991
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06027086
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06111326
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06608940
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06911255
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02519348
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02821754
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03482102
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03638141
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03899428
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03937830
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04294498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04430452
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04522544
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04913480
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04945720
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04988945
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05027425
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05063565
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05194293
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05312216
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05440864
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05451043
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05733598
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05809869
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05844046
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05864755
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06040099
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06045975
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06364007
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06482801
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06492408
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06526104
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06698250
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06880523
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06994299
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06999694
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06999707
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07012798
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07081633
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07122089
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07168668
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07174570
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07175441
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07226063
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07489976
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07511504
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06904170
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03298451
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03778957
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03847428
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05301842
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05557838
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05883644
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07027436
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07166406
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D0LS9E
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04443322
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04517227
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06117891
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07607769
- **FLUOROURACIL** (CHEMBL185) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02436044
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05007587
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00264472
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02069041
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02715531
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00319683
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00933816
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02102022
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03563170
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06741020
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07522411
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00471484
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00524498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559455
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00619541
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00849264
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01055743
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01171482
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01775501
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01834963
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01953406
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02426450
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02452853
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02967887
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02981498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02987699
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03009461
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03722498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03803254
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03812770
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03812783
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04135690
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04170179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04191889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04627363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04814030
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04945720
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04962958
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04994236
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05040438
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05099848
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05214339
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05355155
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05412589
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05493332
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05821361
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05886465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06607107
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06632717
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06904183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07192185
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07337421
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07337460
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07363356
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02527772
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02534337
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02584556
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05171166
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00238160
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00471965
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01088581
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01214343
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01327521
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02738697
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02755311
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02774187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03017326
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03164382
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192618
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192644
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03468231
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03469479
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03533582
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03605706
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04667351
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04687163
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05313282
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05476432
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06041477
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06172205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06201065
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06492395
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00644020
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04521491
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04618367
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05121571
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05718492
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06519578
- **LEUCOVORIN** (CHEMBL1679) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02436044
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02715531
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03563170
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06741020
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07522411
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559455
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01533324
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01775501
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02426450
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02452853
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02981498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02987699
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03722498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03803254
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03812770
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03812783
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04135690
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04170179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04191889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04627363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04945720
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04962958
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04994236
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05099848
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05214339
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05493332
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05821361
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05886465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06904183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07192185
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07337421
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07337460
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07363356
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02527772
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02534337
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02584556
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05171166
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00471965
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02738697
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02774187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03164382
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192618
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192644
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03468231
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03469479
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03605706
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04667351
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04687163
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05313282
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06172205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06201065
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06492395
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04521491
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04618367
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05121571
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05718492
- **OXALIPLATIN** (CHEMBL414804) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02436044
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05007587
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00861783
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02069041
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02403544
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02715531
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02102022
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06741020
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07522411
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00052364
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00142467
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00250822
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00280618
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00351195
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00471484
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00483405
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559455
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00752063
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00941967
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01429961
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01775501
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02089633
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02426450
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02452853
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02716766
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02981498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02987699
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03009461
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03026803
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03578874
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03722498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03803254
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03812770
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03812783
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04135690
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04170179
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04191889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04518852
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04597970
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04627363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04814030
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04850040
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04945720
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04962958
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04994236
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05003700
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05099848
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05214339
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05355155
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05493332
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05517239
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05821361
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05886465
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06285019
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06397235
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06441019
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06607107
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06904183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07012798
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07192185
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07328009
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07337421
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07337460
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07351513
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07363356
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02527772
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02534337
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02584556
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02585479
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05033522
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05171166
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05976568
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06904170
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07392866
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00471965
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01245582
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02109146
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02738697
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02774187
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03017326
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03164382
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192618
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192644
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03468231
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03469479
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03533582
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03605706
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04667351
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04687163
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05313282
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05476432
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06041477
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06172205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06201065
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06492395
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04521491
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04618367
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05121571
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05718492
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06818097
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06893887

#### renal cell carcinoma (MONDO_0005086)

- **ALDESLEUKIN** (CHEMBL1201438) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05PUD
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00276835
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00278369
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00304460
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00418496
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02867332
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02926053
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03260504
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03354390
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04596033
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06626256
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003585
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00197860
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00277017
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00588913
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01038778
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01550367
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02989714
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03111901
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03474497
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002589
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002733
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002846
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00002847
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003091
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003181
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005038
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00031564
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00032188
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080977
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00083941
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00085436
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00089778
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00203866
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00226798
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00301990
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00440973
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00485563
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00554515
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00582790
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00609401
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00913913
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01176552
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01274273
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01925118
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03226236
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03501381
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03991130
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05155033
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D04OJM
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003126
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00018941
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00053807
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00053820
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00291369
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00311467
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416429
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416871
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00502034
- **SIFALIMUMAB** (CHEMBL1743069) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05NDR

#### thyroid cancer (MONDO_0002108)

- **CABOZANTINIB** (CHEMBL2105717) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0IQ6P
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03170960
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03630120
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04400474
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05660954
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06482086
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03690388
- **THYROTROPIN ALFA** (CHEMBL1201533) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0H4TQ
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02145143
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04447183
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00295763

### Rare (36 items)

#### cystic fibrosis (MONDO_0009061)

- **INTERFERON GAMMA-1B** (CHEMBL1201564) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U9EN
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00043316
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00043342

#### Duchenne muscular dystrophy (MONDO_0010679)

- **ATALUREN** (CHEMBL256997) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00264888
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00592553
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00759876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00847379
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01009294
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02819557
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03796637
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04336826
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01247207
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01557400
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01826487
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02090959
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03179631
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/translarna

#### spinal muscular atrophy (MONDO_0001516)

- **PHENYLBUTANOIC ACID** (CHEMBL1469) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P2GK
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00439218
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00439569

#### Huntington disease (MONDO_0007739)

- **ATOMOXETINE** (CHEMBL641) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00368849
- **GUANFACINE** (CHEMBL862) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **LISDEXAMFETAMINE** (CHEMBL1201222) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **METHYLPHENIDATE** (CHEMBL796) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html

#### amyotrophic lateral sclerosis (MONDO_0004976)

- **MECOBALAMIN** (CHEMBL2359370) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00444613
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00445172
- **PHENYLBUTANOIC ACID** (CHEMBL1469) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05286372
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00107770
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04987671
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03127514
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03488524
    - PHASE_2 | TTD | https://ttd.idrblab.cn/data/drug/details/D03QSS
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04516096
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05021536
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05619783
    - UNKNOWN | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/albrioza

#### Gaucher disease (MONDO_0018150)

- **OLIPUDASE ALFA** (CHEMBL3707358) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0YX3D

#### hemophilia B (MONDO_0010604)

- **COAGULATION FACTOR IX HUMAN** (CHEMBL4297986) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/nonafact
- **FIDANACOGENE ELAPARVOVEC** (CHEMBL3990034) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02484092
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03307980
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03861273
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/beqvez

#### myasthenia gravis (MONDO_0009688)

- **AMBENONIUM** (CHEMBL1652) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06IAQ
- **EDROPHONIUM** (CHEMBL1104) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0S5LH

#### narcolepsy (MONDO_0021107)

- **DEXTROAMPHETAMINE** (CHEMBL612) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T3LF
- **MODAFINIL** (CHEMBL1373) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07HQC
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03182413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00424931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02821715
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00066170
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00107796
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00107848
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00214968
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01067222
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01067235
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00174174

#### hereditary angioedema (MONDO_0019623)

- **STANOZOLOL** (CHEMBL2079587) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08QKJ

#### sarcoidosis (MONDO_0019338)

- **COLLAGENASE CLOSTRIDIUM HISTOLYTICUM** (CHEMBL2108709) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I4ZQ

#### systemic sclerosis (MONDO_0005100)

- **POMALIDOMIDE** (CHEMBL43452) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0A3ZU
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01559129

#### Behcet disease (MONDO_0007191)

- **EZOGABINE** (CHEMBL41355) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X7GL

#### idiopathic pulmonary fibrosis (EFO_0000768)

- **INTERFERON GAMMA-1B** (CHEMBL1201564) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U9EN
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00563212
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00047658
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00052052
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00047645
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00052039
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00075998
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00076635

#### pulmonary arterial hypertension (MONDO_0015924)

- **BERAPROST** (CHEMBL1207745) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00781885
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00792571
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00989963
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00990314
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01966302
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01458236
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01908699
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D0LA6Z
- **SITAXENTAN** (CHEMBL282724) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01100736
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00034307
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080457
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00795639
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00796510
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00796666
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00811018
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01204853
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01210443
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00593905
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01445873
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02EAS
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T1RG

#### amyloidosis (MONDO_0019065)

- **IXAZOMIB CITRATE** (CHEMBL3545432) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01MML
- **PATISIRAN** (CHEMBL3989987) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02UYB
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05023889
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02510261

#### Friedreich ataxia (MONDO_0100339)

- **IDEBENONE** (CHEMBL252556) | group **E** | approval report sources: none | on the Approved list today
    - (this item's rows hold no reports at all)
- **OMAVELOXOLONE** (CHEMBL4303525) | group **E** | approval report sources: none | on the Approved list today
    - (this item's rows hold no reports at all)

#### Dravet syndrome (MONDO_0100135)

- **CANNABIDIOL** (CHEMBL190461) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O1UZ
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06738732
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02318602
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03808935
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04485104
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06924827
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05485831
- **FENFLURAMINE** (CHEMBL87493) | group **F** | approval report sources: ClinicalTrials.gov, PMDA | left out today as withdrawn
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03780127
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04437004
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02682927
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02823145
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02926898
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03936777
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05560282
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06118255
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D09WNK
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06598449
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07112365
- **STIRIPENTOL** (CHEMBL1983350) | group **F** | approval report sources: ClinicalTrials.gov, PMDA, TTD | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01983722
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02XSA
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01835314
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02239276

#### osteogenesis imperfecta (MONDO_0019019)

- **TERIPARATIDE** (CHEMBL525610) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0YA2L
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01679080
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00131469

#### systemic lupus erythematosus (MONDO_0007915)

- **HYDROXYCHLOROQUINE** (CHEMBL1535) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01946880
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01551069
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02444728
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05799378
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03180190
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04389320
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04918524

#### ankylosing spondylitis (MONDO_0005306)

- **DEXIBUPROFEN** (CHEMBL175) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06YPU
- **MECLOFENAMIC ACID** (CHEMBL509) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08IFL

#### vitiligo (MONDO_0008661)

- **MONOBENZONE** (CHEMBL1388) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0H6TP
- **TRIOXSALEN** (CHEMBL1475) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0FA2O

### Agent's choice (329 items)

#### angina pectoris (EFO_0003913)

- **ABCIXIMAB** (CHEMBL1201584) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P3TX
- **AMYL NITRITE** (CHEMBL6195748) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01QLH
- **DRONEDARONE** (CHEMBL184412) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05CPV
- **ERYTHRITYL TETRANITRATE** (CHEMBL2107583) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06IZM
- **LIDOFLAZINE** (CHEMBL92870) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L7VL
- **MEPINDOLOL** (CHEMBL65717) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O5YZ
- **MOLSIDOMINE** (CHEMBL1329455) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08VXL
- **NICORANDIL** (CHEMBL284906) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O2SR
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01185015
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01397994
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00424801
- **NIFEDIPINE** (CHEMBL193) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04OSE
- **NIPRADILOL** (CHEMBL155622) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09SSC
- **PENTAERYTHRITOL TETRANITRATE** (CHEMBL466659) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0W9TE
- **PERHEXILINE** (CHEMBL75880) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00SBN
- **TRIMETAZIDINE** (CHEMBL203266) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Q4YI
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07074834
- **ASPIRIN** (CHEMBL25) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07378228
- **CLOPIDOGREL** (CHEMBL1771) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00821834
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01779401
- **LANSOPRAZOLE** (CHEMBL480) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **PRASUGREL** (CHEMBL1201772) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **VONOPRAZAN** (CHEMBL2079130) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html

#### allergic rhinitis (MONDO_0011786)

- **ACRIVASTINE** (CHEMBL1224) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O4EU
- **AZATADINE** (CHEMBL946) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0N7AD
- **BECLOMETHASONE** (CHEMBL1586) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07DVK
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02133053
- **BEPOTASTINE** (CHEMBL1201758) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U5VZ
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01425632
- **BROMPHENIRAMINE** (CHEMBL811) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08VXO
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01393548
- **CHLORPHENIRAMINE** (CHEMBL505) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0B7NG
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04790487
- **DIPHENYLPYRALINE** (CHEMBL1492) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0W6DY
- **FLUNISOLIDE** (CHEMBL1512) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0FM2P
- **FLUTICASONE** (CHEMBL1201396) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0LC6K
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02885025
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00783458
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00817050
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00513487
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01376206
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01420822
- **ISOPROPAMIDE** (CHEMBL1201232) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z9PX
- **MEQUITAZINE** (CHEMBL73451) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09IMS
- **METHDILAZINE** (CHEMBL1200959) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0LR0R
- **METHYLPROMAZINE** (CHEMBL829) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08HZL
- **MIZOLASTINE** (CHEMBL94454) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06MAJ
- **TRIAMCINOLONE** (CHEMBL1451) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03BLF
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06272032
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00032526
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01839851
- **BILASTINE** (CHEMBL1742423) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02513290
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02576041
- **EMEDASTINE** (CHEMBL594) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **EPINASTINE** (CHEMBL1106) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02238223
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02238236
- **OLOPATADINE** (CHEMBL1189432) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **ASTEMIZOLE** (CHEMBL296419) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y2HR
- **LEVOCETIRIZINE** (CHEMBL1201191) | group **F** | approval report sources: PMDA, TTD | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0M8PW
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00152412
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00619801
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00628108
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00789152
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01000792
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01563081
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02552667
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05637710
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01445262
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03673384
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05348148

#### gastroesophageal reflux disease (MONDO_0007186)

- **CISAPRIDE** (CHEMBL1729) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0BD8D
- **ABEPRAZAN** (CHEMBL4594445) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC10
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03184324
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03811080
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07326904
- **ACETOXOLONE** (CHEMBL207413) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX09
- **ALGINIC ACID** (CHEMBL2108894) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX13
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01878526
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02277886
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05629143
- **BISMUTH SUBCITRATE POTASSIUM** (CHEMBL1201186) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX05
- **BISMUTH SUBNITRATE** (CHEMBL3833348) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX12
- **CARBENOXOLONE** (CHEMBL499915) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX01
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX51
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX71
- **CIMETIDINE** (CHEMBL30) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA01
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA51
- **DEXRABEPRAZOLE** (CHEMBL1615209) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC07
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02689999
- **ENPROSTIL** (CHEMBL2104194) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BB02
- **FAMOTIDINE** (CHEMBL902) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA03
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA53
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01499368
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01079052
- **GEFARNATE** (CHEMBL2105085) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX07
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX77
- **ILAPRAZOLE** (CHEMBL2106370) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC11
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01107938
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01509261
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02860624
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03444883
- **IRSOGLADINE** (CHEMBL136497) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX16
- **LAFUTIDINE** (CHEMBL1742461) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA08
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01499368
- **METHYLMETHIONINE SULFONIUM CHLORIDE** (CHEMBL1797128) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX04
- **MISOPROSTOL** (CHEMBL606) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BB01
- **NIPEROTIDINE** (CHEMBL1909284) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA05
- **NIZATIDINE** (CHEMBL3183075) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA04
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00373334
- **PIRENZEPINE** (CHEMBL9967) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX03
- **PROGLUMIDE** (CHEMBL316561) | group **D** | approval report sources: ATC | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX06
- **RANITIDINE** (CHEMBL1790041) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA02
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA07
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00131248
- **REBAMIPIDE** (CHEMBL1697771) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX14
- **ROXATIDINE** (CHEMBL4802233) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA06
- **SUCRALFATE** (CHEMBL6067980) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX02
- **SULGLICOTIDE** (CHEMBL2108085) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX08
- **TEGOPRAZAN** (CHEMBL4297583) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC09
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02028663
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02456935
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02556021
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03006874
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03591653
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05701540
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06991348
- **TEPRENONE** (CHEMBL5314356) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX15
- **TROXIPIDE** (CHEMBL1566956) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX11
- **ZOLIMIDINE** (CHEMBL2105534) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX10
- **TEGASEROD** (CHEMBL76370) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00149851
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00171418
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00171483
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00XWD
- **VONOPRAZAN** (CHEMBL2079130) | group **F** | approval report sources: ATC, PMDA | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC08
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05343364
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06106022
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02743949
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01452698
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01452776
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01459367
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01474369
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01630746
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02388724
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02388737
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02954848
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04124926
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D02CPP
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02679508
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04028466
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06564246
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06778395
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03214081
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03214952
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06953986
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06955520
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07437768
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07563491

#### overactive bladder (MONDO_0006624)

- **MANGANESE CHLORIDE** (CHEMBL5314371) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02QPR
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0C6QG
- **MANGANESE SULFATE** (CHEMBL2103742) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0VB3Y
- **IMIDAFENACIN** (CHEMBL53366) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212706
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00212732
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00512785
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03575702
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01578304
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03572231

#### type 1 diabetes mellitus (MONDO_0005147)

- **EMPAGLIFLOZIN** (CHEMBL2107830) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06ALD
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04201496
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04450563
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05960656
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06753994
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01392560
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01969747
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02632747
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02702011
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06762314
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02414958
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02580591
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03979352
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06894784
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04917692
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06021145
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03510000
- **SOTAGLIFLOZIN** (CHEMBL3039507) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05696366
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01742208
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02383940
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02459899
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06435156
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07325201
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02384941
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02421510
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02531035
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07211802
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D0U7IL
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/zynquista
- **DONISLECEL** (CHEMBL4594332) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03791567
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D5Y3NP
    - UNKNOWN | USAN | https://searchusan.ama-assn.org/finder/usan/search/DONISLECEL/relevant/1/

#### insomnia (MONDO_0013600)

- **AMOBARBITAL** (CHEMBL267894) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R6BR
- **APROBARBITAL** (CHEMBL7863) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05TMQ
- **BARBITAL** (CHEMBL444) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E0WQ
- **BUTABARBITAL** (CHEMBL449) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0A4JK
- **BUTETHAL** (CHEMBL404422) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O3AB
- **CARPHENAZINE** (CHEMBL1201328) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01QML
- **ETHCHLORVYNOL** (CHEMBL591) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03VZH
- **ETHINAMATE** (CHEMBL1576) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0CK3G
- **FLUNITRAZEPAM** (CHEMBL13280) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0W2NM
- **GABOXADOL** (CHEMBL312443) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00EEL
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00266344
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00266357
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00094627
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00094666
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00095043
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00095069
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00102154
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00102167
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00103818
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209846
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209924
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209937
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209950
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209963
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00420810
- **GLUTETHIMIDE** (CHEMBL1102) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z9NZ
- **INDIPLON** (CHEMBL262075) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0GA5T
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00232167
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00525941
- **MELATONIN** (CHEMBL45) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0AN7B
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06801379
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06802913
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00230737
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00816673
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00869128
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01993251
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06404086
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02798367
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06062953
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00388661
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00397189
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00404456
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01161108
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01450228
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01906866
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06476392
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06380491
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05440734
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06236191
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06996171
- **METHYPRYLON** (CHEMBL1200790) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05OQJ
- **NABILONE** (CHEMBL2218896) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L7AS
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00384410
- **NITRAZEPAM** (CHEMBL13209) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T5WK
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00374777
- **PARALDEHYDE** (CHEMBL1410743) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P9EA
- **PROPIOMAZINE** (CHEMBL1201210) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R9ZB
- **TASIMELTEON** (CHEMBL2103822) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Q5MQ
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00490945
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00548340
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03373201
- **TRICLOFOS** (CHEMBL1201317) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0B2DP
- **ZOPICLONE** (CHEMBL135400) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0ZB7K
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01489982
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03339583
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00699608
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01100164
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02732912
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00295386
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02807922
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05277038
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05618002
- **METHAQUALONE** (CHEMBL282052) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T7XI

#### anxiety disorder (MONDO_0005618)

- **ADINAZOLAM** (CHEMBL328250) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E7FS
- **ALPIDEM** (CHEMBL54349) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01XOD
- **BENTAZEPAM** (CHEMBL1521495) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0N8DP
- **BROMAZEPAM** (CHEMBL277062) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E3FD
- **BUTALBITAL** (CHEMBL454) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05BQK
- **CHLORMEZANONE** (CHEMBL1200714) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0S1OE
- **CLOBAZAM** (CHEMBL70418) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0S9MC
- **CLOTIAZEPAM** (CHEMBL1697737) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R4DP
- **DELORAZEPAM** (CHEMBL268254) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z5OV
- **DIBENZEPIN** (CHEMBL1442422) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P8AY
- **DIXYRAZINE** (CHEMBL3275586) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0RU6U
- **FLUDIAZEPAM** (CHEMBL13291) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06FWC
- **FLUVOXAMINE** (CHEMBL814) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0M5JI
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00012584
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00395213
- **HALAZEPAM** (CHEMBL970) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z9VB
- **MEBUTAMATE** (CHEMBL1200922) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02KBD
- **MEPHOBARBITAL** (CHEMBL45029) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08UMH
- **NITROUS OXIDE** (CHEMBL1234579) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O8DI
- **OPIPRAMOL** (CHEMBL370753) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0D7TB
- **PINAZEPAM** (CHEMBL1213352) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0XM9Y
- **PRAZEPAM** (CHEMBL969) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G3AQ
- **TANDOSPIRONE** (CHEMBL274047) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06OSM
- **TETRAHYDROPALMATINE** (CHEMBL487182) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01FFA
- **ZOTEPINE** (CHEMBL285802) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T6QX

#### age-related macular degeneration (MONDO_0005150)

- **ECULIZUMAB** (CHEMBL1201828) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01RQV
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00935883

#### acne (MONDO_0011438)

- **AMINOLEVULINIC ACID** (CHEMBL601) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y7ZD
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01689935
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04044898
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04018885
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00706433
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01245946
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05080764
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00814918
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04167982
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04631250
- **DEMECLOCYCLINE** (CHEMBL1591) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R9WP
- **GREEN SOAP** (CHEMBL2108601) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0D7DH
- **METHYL AMINOLEVULINATE** (CHEMBL1096562) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0OL6O
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00594425
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00673933
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00933543
- **PROMESTRIENE** (CHEMBL2105394) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0C4NY
- **RIBOFLAVIN** (CHEMBL1534) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04QST
- **ROLITETRACYCLINE** (CHEMBL1237046) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05AFR
- **SUCRALFATE** (CHEMBL6067980) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06ULU
- **ZINC ACETATE ANHYDROUS** (CHEMBL1200928) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K0DY
- **ZINC SULFATE** (CHEMBL1200929) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K0DY
- **OZENOXACIN** (CHEMBL3990047) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **ALUMINIUM OXIDE** (CHEMBL4594252) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AX04
- **ALUMINUM CHLORIDE ANHYDROUS** (CHEMBL3833401) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AX01
- **BITHIONOL** (CHEMBL290106) | group **D** | approval report sources: ATC | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AB01
- **CHLORAMPHENICOL** (CHEMBL130) | group **D** | approval report sources: ATC | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AF03
- **DEXAMETHASONE** (CHEMBL384467) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AA03
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04118296
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07504822
- **FLUOROMETHOLONE** (CHEMBL1200600) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AA01
- **MECLOCYCLINE** (CHEMBL1237124) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AF04
- **MESULFEN** (CHEMBL2106968) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AB05
- **METHYLPREDNISOLONE** (CHEMBL650) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AA02
- **MOTRETINIDE** (CHEMBL519260) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AD05
- **RESORCINOL** (CHEMBL24147) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AX02
- **RETINOL** (CHEMBL986) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AD02
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03090048
- **SULFUR** (CHEMBL1235452) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AB02
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00877409
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01260571
- **TIOXOLONE** (CHEMBL442687) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AB03
- **AZELAIC ACID** (CHEMBL1238) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AX03
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E4WR
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00031096
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03071549
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01038869
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01387048
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02058628
- **CLINDAMYCIN** (CHEMBL1753) | group **F** | approval report sources: ATC, PMDA, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AF01
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G2ZG
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R0ZL
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01132443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01769664
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02578043
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02595034
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03653403
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04134273
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02593383
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04118296
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07504822
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00713609
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04892706
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00663286
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00689117
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00776919
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01138514
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01445301
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01915732
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02005666
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02465632
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02515305
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02616614
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03522441
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03615768
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00671749
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00757523
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00837213
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00887484
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00964223
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00964366
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01047189
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01206348
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01231334
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02058628
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02557399
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02721173
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02731105
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03883269
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01044264
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01052246
- **ISOTRETINOIN** (CHEMBL547) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AD04
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AD54
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10BA01
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00DKK
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02620813
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06225570
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00416585
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02498288
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04594759
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06242288
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06447480
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06451237
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01404130
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04940767
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05316675
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07228481
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02180425
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04156815
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04204304
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04660916
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05413200
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05869188
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05903716
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06378983
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06483971
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07054398
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07309341
- **NADIFLOXACIN** (CHEMBL363449) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=D10AF05
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I0RB
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00869492
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00219570

#### osteoarthritis (MONDO_0005178)

- **CANAKINUMAB** (CHEMBL1201834) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y8KN
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01160822
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04814368
- **CHOLINE MAGNESIUM TRISALICYLATE** (CHEMBL4297727) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0I2VR
- **GLUCOSAMINE** (CHEMBL493287) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07NSU
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00833157
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00032890
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00110474
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00955552
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01293305
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02448199
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02830919
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02178137
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03743896
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05321836
- **GUGGULSTERONE** (CHEMBL410683) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G8BV
- **NEPAFENAC** (CHEMBL1021) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02IHW
- **PROGLUMETACIN** (CHEMBL2105825) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0BD0Q
- **PROQUAZONE** (CHEMBL268501) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0J6WW
- **ROFECOXIB** (CHEMBL122) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05VLS
- **VALDECOXIB** (CHEMBL865) | group **B** | approval report sources: TTD | left out today as withdrawn; has a WITHDRAWAL report
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L6DA
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00648258
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/bextra
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/valdyn-0
- **ACETAMINOPHEN** (CHEMBL112) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00371696
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02845271
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03570554
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04676802
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00000425
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00110474
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00736853
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01420666
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01722864
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02311881
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06863636
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00324038
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00510536
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01105936
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01604382
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01782885
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02091830
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02237989
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02262702
- **BUPRENORPHINE** (CHEMBL511142) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01643759
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00312221
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00312572
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00313846
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00314652
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00315848
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00531427
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01135524
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00324038
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00399178
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01276431
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03947125
- **ESFLURBIPROFEN** (CHEMBL435298) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03434197
- **ISOXICAM** (CHEMBL53292) | group **E** | approval report sources: none | left out today as withdrawn; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03JPH

#### Iron deficiency anemia (HP_0001891)

- **FERRIC OXYHYDROXIDE** (CHEMBL4802224) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y3TM
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02005588
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01700426
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07384663
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02656225
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02957643
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07110935
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00386074
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02038023
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02469480
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05913414
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00223977
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00318812
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06527391
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00994318
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01017614
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155375
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155388
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04587141
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05225545
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06366698
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07556731
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00746551
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01865175
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01904864
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01950247
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02086838
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02086968
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04975074
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05804071
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07308769
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00198848
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00213161
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00392418
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00655408
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01129843
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01823029
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03156725
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03888768
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05151679
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05165680
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05581420
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06148545
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06875947
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07163390
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07366502
- **FERRIC PYROPHOSPHATE CITRATE** (CHEMBL3833317) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03BDP
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02905981
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05110768
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y2JM
- **FERROUS SULFATE** (CHEMBL1200830) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y3TM
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02005588
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01700426
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01757119
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02518568
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07384663
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02656225
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02957643
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07110935
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00386074
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01438372
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02038023
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02469480
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02499354
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03232554
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03481790
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05544513
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05913414
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00223977
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00318812
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02998697
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03940430
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06527391
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00354484
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00364104
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00994318
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01017614
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01131624
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155375
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155388
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02541708
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03523117
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03657433
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03725384
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04087993
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04253626
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04268849
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04371536
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04587141
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04976179
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05126901
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05225545
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05304442
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05462704
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06366698
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07267975
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07556731
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00199277
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00746551
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01865175
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01904864
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01950247
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02086838
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02086968
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03438227
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03524651
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04278651
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04594070
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04975074
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05007899
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05804071
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06492512
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07308769
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07414199
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07605676
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00198848
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00213161
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00276224
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00284700
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00392418
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00655408
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00701246
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01129843
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01590134
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01823029
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02076828
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02558725
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02839096
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03156725
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03777514
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03888768
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05151679
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05165680
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05581420
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06148545
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06742528
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06875947
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07163390
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07366502
- **FERUMOXYTOL** (CHEMBL1201867) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y1KF
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01052779
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02499354
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01114139
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01114204
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01114217
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155375
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155388
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01264679
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02694978
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03619850
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03657433
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03893045
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04253626
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04268849
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01148745
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01227616
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01942460
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04080908
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04278651
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01374919
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03777514
    - UNKNOWN | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/feraheme
- **IRON ISOMALTOSIDE 1000** (CHEMBL4298046) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D05SPL
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y3TM
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02005588
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01700426
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03013439
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07384663
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02656225
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02957643
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07110935
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00386074
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02038023
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02469480
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05913414
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00223977
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00318812
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06527391
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00994318
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01017614
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01102413
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155375
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01155388
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01410435
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01599702
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01895205
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02130063
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02172001
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02940860
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02940886
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03237065
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03238911
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03565354
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04587141
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05225545
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05251493
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06366698
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07556731
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00746551
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01865175
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01904864
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01950247
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02086838
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02086968
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02905539
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03188445
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04975074
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05258825
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05804071
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07308769
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00198848
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00213161
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00392418
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00655408
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01129843
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01823029
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01900197
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02546154
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03156725
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03610230
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03888768
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04318405
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05151679
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05165680
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05504863
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05545527
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05581420
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06148545
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06875947
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07163390
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07366502
- **SODIUM FERRIC GLUCONATE COMPLEX** (CHEMBL1201494) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0VM8K
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00223977

#### herpes zoster (MONDO_0005609)

- **VARICELLA ZOSTER VIRUS ENVELOPE GLYCOPROTEIN E** (CHEMBL4297975) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/DF2C7K
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07285265
- **AMENAMEVIR** (CHEMBL4297592) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00487682
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01959841

#### polycystic ovary syndrome (MONDO_0008487)

- **HISTRELIN** (CHEMBL1201255) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O7DG

#### myocardial infarction (MONDO_0005068)

- **GADOVERSETAMIDE** (CHEMBL1200457) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X0GI
- **IMCIROMAB** (CHEMBL2108283) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02JRT
- **NATEPLASE** (CHEMBL2108513) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0B1EM
- **NITROUS ACID** (CHEMBL1161681) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0MA7C
- **RETEPLASE** (CHEMBL2107885) | group **B** | approval report sources: TTD | on the Approved list today; has a WITHDRAWAL report
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T1UJ
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00046228
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04571580
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/ecokinase
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/rapilysin
- **UROKINASE** (CHEMBL1201420) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E8UO
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01642667
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01568931
- **VONOPRAZAN** (CHEMBL2079130) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **COLCHICINE** (CHEMBL107) | group **E** | approval report sources: none | on the Approved list today
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07143136
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03156816
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03048825
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04181996
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06469528
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01709981
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01936285
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02995512
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05200052
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05709509
    - PREAPPROVAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/colchicine-agepha-pharma
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02095522
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04303689
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05956145

#### pneumonia (MONDO_0005249)

- **ARBEKACIN** (CHEMBL426926) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **GARENOXACIN** (CHEMBL215303) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - UNKNOWN | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/garenoxacin-mesylate
- **LASCUFLOXACIN** (CHEMBL6068006) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **SITAFLOXACIN ANHYDROUS** (CHEMBL108821) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **TEBIPENEM PIVOXIL** (CHEMBL2107486) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **TOSUFLOXACIN** (CHEMBL273348) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **VANCOMYCIN** (CHEMBL262777) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00543608
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01570192
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01363271

#### irritable bowel syndrome (MONDO_0005052)

- **CALCIUM POLYCARBOPHIL** (CHEMBL2109032) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07IRG
- **CHARCOAL, ACTIVATED** (CHEMBL2106049) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06ZVG
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00583128
- **CLIDINIUM** (CHEMBL620) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Q1BT
- **DROTAVERINE** (CHEMBL551978) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06XAE
- **MEBEVERINE** (CHEMBL282121) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0VU8Q
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05815602
- **METHANTHELINE** (CHEMBL1201264) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0JY5S
- **PLECANATIDE** (CHEMBL2103867) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07FEC
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03596905
- **PRIFINIUM** (CHEMBL1229214) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E8LT
- **PRUCALOPRIDE** (CHEMBL117287) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04QSJ
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04757493
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04985669
- **SULFASALAZINE** (CHEMBL421) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02ZTJ
- **TRIMEBUTINE** (CHEMBL190044) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E0CT
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06268964
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03359499
- **RAMOSETRON** (CHEMBL1643895) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00189696

#### benign prostatic hyperplasia (MONDO_0010811)

- **PRAZOSIN** (CHEMBL2) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0WV3U
- **FEXAPOTIDE** (CHEMBL3545061) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04CX04
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00759135
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00918983
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00945490
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01438775
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01846793
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02003742
- **MEPARTRICIN** (CHEMBL3989893) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04CX03

#### dry eye syndrome (MONDO_0006733)

- **REBAMIPIDE** (CHEMBL1697771) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00234078
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00475319
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01027013
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00201955
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00201981
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00818324
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00885079
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01632137
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01660256

#### rosacea (MONDO_0006604)

- **CLOBETASOL** (CHEMBL1201362) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0FL5V
- **CLOCORTOLONE ACETATE** (CHEMBL2106011) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00GOS
- **DIFLORASONE DIACETATE** (CHEMBL1200545) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G7KJ

#### psoriatic arthritis (MONDO_0011849)

- **BRODALUMAB** (CHEMBL1742996) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01516957
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01748539
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02024646
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02029495
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02052609
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04183881

#### neutropenia (MONDO_0001475)

- **EFLAPEGRASTIM** (CHEMBL3833384) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04CKG
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01724866
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02643420
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02953340
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05949333

#### candidiasis (MONDO_0002026)

- **BUTOCONAZOLE** (CHEMBL1295) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0N3SP
- **HALOPROGIN** (CHEMBL1289) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06ZAY
- **TERCONAZOLE** (CHEMBL1714574) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01AQT
- **MICONAZOLE** (CHEMBL91) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html

#### gastric cancer (MONDO_0001056)

- **LENIOLISIB** (CHEMBL3643413) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/DGO2C1
- **TEBENTAFUSP** (CHEMBL4297990) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0S0BJ
- **ANAMORELIN** (CHEMBL2110579) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
- **ESOMEPRAZOLE** (CHEMBL1201320) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02894892
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04810793
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04991584
- **GIMERACIL** (CHEMBL1730601) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00553696
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00960349
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01291407
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03162510
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05867121
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00072787
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209638
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01783951
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04781413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00088816
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00134095
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209664
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00278863
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00985556
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01679340
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01747707
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01824004
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02090153
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02229058
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02296658
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02504229
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02725424
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03007446
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03137004
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192735
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03382600
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03718624
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04152889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04694183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04982939
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05627414
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05853172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06196697
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06341595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06451211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07315854
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01516944
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02442362
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02817425
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03607656
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05699655
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00150670
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182611
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00195572
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00202969
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00252161
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01671449
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01761461
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02008422
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02114359
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02338518
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03006705
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03615326
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05144854
- **NIVOLUMAB** (CHEMBL2108738) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03155061
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03172416
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03335540
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03406871
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03511222
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03784040
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04130763
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04902443
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05187182
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05802056
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05867121
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01928394
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01968109
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02341625
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02488759
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02983045
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02999295
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03453164
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04180371
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04495296
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05175235
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05322577
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05535569
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06008925
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02935634
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03259867
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03342417
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03704077
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04062656
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04757363
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04908566
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05859477
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06253611
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06256328
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06685887
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07542262
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02746796
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07000253
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02267343
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02872116
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03006705
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05111626
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05144854
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05001360
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06158919
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06235164
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06452329
- **RAMUCIRUMAB** (CHEMBL1743062) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01285037
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02970539
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05365581
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06675136
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02999295
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03008278
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03739801
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04888663
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05927857
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01983878
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02628951
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02726399
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03766607
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06038578
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06564298
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02898077
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02934464
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06490055
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06666582
- **TEGAFUR** (CHEMBL20883) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00553696
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00960349
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01096199
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01269255
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01291407
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03162510
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05867121
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00072787
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209638
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01783951
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04781413
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00088816
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00134095
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00154778
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209664
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00278863
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00985556
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01100801
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01679340
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01747707
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01824004
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02090153
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02229058
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02296658
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02504229
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02725424
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02903498
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03007446
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03137004
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03192735
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03382600
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03604614
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03718624
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04152889
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04694183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04908566
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04982939
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05052931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05070598
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05223088
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05524974
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05545436
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05627414
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05853172
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06196697
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06341595
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06451211
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07315854
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07353684
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01516944
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02442362
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02817425
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03607656
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05325528
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05699655
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00150670
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00182611
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00195572
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00202969
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00252161
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00287768
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01671449
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01761461
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02008422
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02114359
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02338518
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03006705
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03475615
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03615326
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04135781
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05144854
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05813015
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05914610
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05800080
- **TRASTUZUMAB** (CHEMBL1201585) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06098898
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01602406
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01705340
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03319459
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05274048
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01746771
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02030561
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02318901
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02805829
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02901301
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04888663
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05640830
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06572319
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06650332
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01228045
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01359397
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01364493
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01402401
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01503983
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01736410
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01928290
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02004769
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02005484
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02205047
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02250209
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02725424
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02726399
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03239015
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03766607
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04168931
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04309578
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04661150
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04908813
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04960943
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05311189
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05515796
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05975749
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05997524
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06427252
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06881017
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06998771
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07000253
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01041404
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01774786
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02721641
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03615326
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06532006
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01295086
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01839500
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03024450
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04181333
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07009600
- **VONOPRAZAN** (CHEMBL2079130) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04810793
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04991584
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05189444
- **ZOLBETUXIMAB** (CHEMBL2109427) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06732856
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06881017
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07000253
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03504397
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06902545

#### deep vein thrombosis (EFO_0003907)

- **CERTOPARIN SODIUM** (CHEMBL2109012) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0U7HJ
- **DERMATAN SULFATE** (CHEMBL3707304) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02LTL
- **FIBRINOGEN, HUMAN** (CHEMBL2109072) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V4JR

#### peptic ulcer disease (MONDO_0004247)

- **ANISOTROPINE** (CHEMBL1186610) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07CNL
- **CETRAXATE** (CHEMBL1187445) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V9ZG
- **DIPHEMANIL** (CHEMBL1201340) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0OK5Q
- **HOMATROPINE METHYLBROMIDE** (CHEMBL1200851) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O5SZ
- **MEPENZOLATE** (CHEMBL524004) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0FV3V
- **METHANTHELINE** (CHEMBL1201264) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0JY5S
- **METHSCOPOLAMINE** (CHEMBL376897) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0M6VK
- **OXYPHENCYCLIMINE** (CHEMBL1495) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0H5DU
- **ABEPRAZAN** (CHEMBL4594445) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC10
- **ACETOXOLONE** (CHEMBL207413) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX09
- **ALGINIC ACID** (CHEMBL2108894) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX13
- **BISMUTH SUBCITRATE POTASSIUM** (CHEMBL1201186) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX05
- **BISMUTH SUBNITRATE** (CHEMBL3833348) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX12
- **CARBENOXOLONE** (CHEMBL499915) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX01
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX51
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX71
- **CIMETIDINE** (CHEMBL30) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA01
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA51
- **DEXRABEPRAZOLE** (CHEMBL1615209) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC07
- **ENPROSTIL** (CHEMBL2104194) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BB02
- **GEFARNATE** (CHEMBL2105085) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX07
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX77
- **ILAPRAZOLE** (CHEMBL2106370) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC11
- **IRSOGLADINE** (CHEMBL136497) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX16
- **LAFUTIDINE** (CHEMBL1742461) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA08
- **LANSOPRAZOLE** (CHEMBL480) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC03
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC53
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06894992
- **METHYLMETHIONINE SULFONIUM CHLORIDE** (CHEMBL1797128) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX04
- **NIPEROTIDINE** (CHEMBL1909284) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA05
- **NIZATIDINE** (CHEMBL3183075) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA04
- **PANTOPRAZOLE** (CHEMBL1502) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC02
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00261300
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00374101
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01214408
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02235311
- **PROGLUMIDE** (CHEMBL316561) | group **D** | approval report sources: ATC | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX06
- **RABEPRAZOLE** (CHEMBL1219) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC04
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC54
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01037491
- **REBAMIPIDE** (CHEMBL1697771) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX14
    - PHASE_3 | TTD | https://ttd.idrblab.cn/data/drug/details/D03BQP
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04550858
- **ROXATIDINE** (CHEMBL4802233) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA06
- **SUCRALFATE** (CHEMBL6067980) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX02
- **SULGLICOTIDE** (CHEMBL2108085) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX08
- **TEGOPRAZAN** (CHEMBL4297583) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC09
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06894992
- **TROXIPIDE** (CHEMBL1566956) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX11
- **VONOPRAZAN** (CHEMBL2079130) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC08
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04810793
- **ZOLIMIDINE** (CHEMBL2105534) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX10
- **DEXLANSOPRAZOLE** (CHEMBL1201863) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BC06
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06YYD
- **FAMOTIDINE** (CHEMBL902) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA03
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA53
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K0OZ
- **PIRENZEPINE** (CHEMBL9967) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX03
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T0LM
- **RANITIDINE** (CHEMBL1790041) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA02
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BA07
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0B8WN
- **TEPRENONE** (CHEMBL5314356) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=A02BX15
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09XWD

#### urinary tract infection (MONDO_0100338)

- **AMMONIUM CHLORIDE** (CHEMBL1200939) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06WEK
- **CEFTEZOLE** (CHEMBL1697829) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D03PIR
- **CINOXACIN** (CHEMBL1208) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07UXP
- **ENOXACIN** (CHEMBL826) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0R8ER
- **FINAFLOXACIN** (CHEMBL1908370) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01IXD
- **MEZLOCILLIN** (CHEMBL1731) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D00NJJ
- **NALIDIXIC ACID** (CHEMBL5) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07JGT
- **PRULIFLOXACIN** (CHEMBL422648) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/DR36YB
- **SULFACYTINE** (CHEMBL1201056) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0T1GT
- **SULFAMETHIZOLE** (CHEMBL1191) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D07JJS
- **SULFISOXAZOLE** (CHEMBL453) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D09TBD
- **PIDOTIMOD** (CHEMBL1488165) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04YCE
- **SULFALENE** (CHEMBL1525826) | group **E** | approval report sources: none | on the Approved list today; has a WITHDRAWAL report
    - WITHDRAWAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0F0OK

#### hyperthyroidism (MONDO_0004425)

- **CARBIMAZOLE** (CHEMBL508102) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02CKX
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03064542
- **POTASSIUM PERCHLORATE** (CHEMBL1200696) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0MF9G

#### uveitis (MONDO_0020283)

- **HOMATROPINE METHYLBROMIDE** (CHEMBL1200851) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0O5SZ

#### urticaria (MONDO_0005492)

- **BILASTINE** (CHEMBL1742423) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01081574
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04967092
- **EPINASTINE** (CHEMBL1106) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02238223
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02238236
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02238249
- **OLOPATADINE** (CHEMBL1189432) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html

#### fibromyalgia (MONDO_0005546)

- **IBUTAMOREN** (CHEMBL13817) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D02NEH
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00116129
- **INDIPLON** (CHEMBL262075) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0GA5T
- **LEVETIRACETAM** (CHEMBL1286) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E1XL
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00254657
- **TROPISETRON** (CHEMBL56564) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0K0KH

#### venous thromboembolism (MONDO_0005399)

- **FONDAPARINUX** (CHEMBL1201202) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00423683
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01004939
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01390883
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01390896
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01428531
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01428544
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01727427
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04359212
- **PROTEIN C CONCENTRATE (HUMAN)** (CHEMBL5315087) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html

#### leprosy (MONDO_0005124)

- **CLOFAZIMINE** (CHEMBL1292) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04BA01
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01290744
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00852345
- **DAPSONE** (CHEMBL1043) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04BA02
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06819449
- **SULFOXONE** (CHEMBL1570) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=J04BA03

#### Infertility (HP_0000789)

- **CORIFOLLITROPIN ALFA** (CHEMBL2108185) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0L1QF
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02448459
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00598208
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702351
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00696800
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00696878
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02046655
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03846544
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702195
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702234
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702273
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702520
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702546
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00703014
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01408615
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03555942
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03816670
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04142190
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04416607
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04482751
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06193135
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06635538
- **CYCLOFENIL** (CHEMBL141305) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0X1EZ
- **IDURSULFASE** (CHEMBL1201826) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06CZJ
- **CHORIOGONADOTROPIN ALFA** (CHEMBL1201464) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01414673
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00823121
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00844350
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03564509
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04850261
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00954265
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01507376
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02355925
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02862782
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03803228
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04064840
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06725004
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702234
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702273
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00809107
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01152866
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01668056
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01810601
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01933126
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01986374
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02368964
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02865681
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02979886
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03098199
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03825445
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03904368
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04704141
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04855383
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05076981
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05370794
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06142708
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06577181
- **PROGESTERONE** (CHEMBL103) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01483365
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00377923
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02510534
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05969795
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02677259
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03440359
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05758064
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00827983
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00828191
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01710514
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01863680
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02491437
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03565211
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04087408
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04537078
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06644794
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00345306
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01940653
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02032797
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03040830
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03795220
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05080569
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07508657
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00700492
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702234
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702273
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00702546
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01046708
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01178931
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01356524
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01367912
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718444
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01780558
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01780610
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01790282
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01810601
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02492451
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03098199
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03470610
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03734770
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03965949
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03998761
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04052607
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04108039
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04248309
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04278508
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04408144
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04722471
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04733235
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04837768
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05089383
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05189145
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05276531
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05484193
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05825885
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06928844
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07003373
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07409792

#### cervical cancer (MONDO_0002974)

- **ABOBOTULINUMTOXINA** (CHEMBL2108570) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0M7IH
- **INCOBOTULINUMTOXINA** (CHEMBL2108035) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0H3AB
- **CEMIPLIMAB** (CHEMBL4297723) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04646005
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03257267
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06945601

#### Hypercholesterolemia (HP_0003124)

- **ALIROCUMAB** (CHEMBL2109540) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01723735
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01785329
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01288443
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01288469
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07477704
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01507831
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01644175
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01644188
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01644474
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01730040
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01730053
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02023879
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02107898
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02289963
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02584504
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02585778
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02715726
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03415178
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03480568
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03379558
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07375225
- **INCLISIRAN SODIUM** (CHEMBL5095052) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06386419

#### erectile dysfunction (MONDO_0005362)

- **CONESTAT ALFA** (CHEMBL2108350) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Z7ZM
- **APOMORPHINE** (CHEMBL53) | group **D** | approval report sources: ATC | on the Approved list today; has a WITHDRAWAL report
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04BE07
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/ixense
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/taluvian
    - WITHDRAWAL | EMA Human Drugs | https://www.ema.europa.eu/en/medicines/human/EPAR/uprima
- **PAPAVERINE** (CHEMBL19224) | group **D** | approval report sources: ATC | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04BE02
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04BE52
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00080808
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00955929
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03033537
- **MOXISYLYTE** (CHEMBL159226) | group **F** | approval report sources: ATC, TTD | left out today as withdrawn
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04BE06
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0A7QN
- **UDENAFIL** (CHEMBL2103849) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04BE11
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D01GUS
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01230541
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00282607
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00607282
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01967251
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01037218
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01037244
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01065012
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01305083
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01774864
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01901640
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01421940
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03142542
- **YOHIMBINE** (CHEMBL15245) | group **F** | approval report sources: ATC, TTD | on the Approved list today
    - APPROVAL | ATC | https://www.whocc.no/atc_ddd_index/?code=G04BE04
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0H4JM
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00042536

#### Graves disease (MONDO_0005364)

- **IPODATE** (CHEMBL1201243) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D06AAP
- **TEPROTUMUMAB** (CHEMBL1743079) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0EN0W

#### panic disorder (MONDO_0005383)

- **BROMAZEPAM** (CHEMBL277062) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0E3FD

#### juvenile idiopathic arthritis (MONDO_0011429)

- **BARICITINIB** (CHEMBL2105759) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03773965

#### toxoplasmosis (MONDO_0005989)

- **TRIMETREXATE** (CHEMBL119) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0Y7TS
- **SPIRAMYCIN** (CHEMBL6195749) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html

#### mantle cell lymphoma (MONDO_0018876)

- **BENDAMUSTINE** (CHEMBL487253) | group **C** | approval report sources: PMDA | on the Approved list today
    - APPROVAL | PMDA | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03295240
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00389051
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01088048
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01410513
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01479842
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02257242
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02717624
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02728531
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00963534
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01078142
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01170052
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01221103
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01326702
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03900377
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00612183
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00891839
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00992134
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01412879
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01415752
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01437709
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01457144
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01661881
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01662050
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01718691
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01737177
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02747732
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03311126
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03567876
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03623373
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03834688
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03872180
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04115631
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04792489
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04913103
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05245656
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05249959
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05868395
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06136351
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06854003
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07206264
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02793583
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00877006
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00991211
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01073163
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01456351
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01776840
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02972840
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04849715
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06363994
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06496308
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04127916
- **CYCLOPHOSPHAMIDE ANHYDROUS** (CHEMBL88) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04162756
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01184885
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00012207
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00621452
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01569750
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05694364
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06251180
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07444710
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003541
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00151320
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00295932
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00477412
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322776
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01389427
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03676504
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05110742
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06564038
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00003311
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004231
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00005780
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006252
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00020943
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00022945
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00041132
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00053092
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00070447
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00114738
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00151281
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00278161
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00285389
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00305682
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00376961
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00433537
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00450801
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00513955
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00559104
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00581776
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00581854
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00711828
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00878254
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00946374
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00958256
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00992992
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01144403
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01412879
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01527149
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02601313
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02633137
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03710772
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04566887
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04626791
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04736914
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04792489
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04880434
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05283720
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07569965
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00641095
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00016887
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209209
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209222
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00317096
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00722137
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01865110
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05051891
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00525876
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04666168
- **FLUDARABINE** (CHEMBL1568) | group **F** | approval report sources: ClinicalTrials.gov | on the Approved list today
    - APPROVAL | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04162756
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01088048
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05694364
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01322776
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01389427
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03676504
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006252
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00053092
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00119730
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00183989
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00305682
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00577278
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00875667
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00946374
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01144403
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01578343
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02601313
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03016988
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04792489
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04880434
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07569965
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00641095
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00209209
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00317096
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00525876
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04666168

#### pulmonary embolism (MONDO_0005279)

- **FIBRINOGEN, HUMAN** (CHEMBL2109072) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0V4JR
- **PHENINDIONE** (CHEMBL711) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D08FTG
- **STREPTOKINASE** (CHEMBL2108147) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D04URO
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03595085
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06545864
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07374978

#### bronchiectasis (MONDO_0004822)

- **MANNITOL** (CHEMBL689) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0P7EK
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00730977
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01076491
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00277537
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00669331

#### primary biliary cholangitis (MONDO_0005388)

- **OBETICHOLIC ACID** (CHEMBL566315) | group **B** | approval report sources: TTD | left out today as withdrawn
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0M4WA
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03253276
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00550862
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00570765
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01865812
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04594694
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05239468
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01473524
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04956328
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05450887
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06488911
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06715319
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02308111
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03633227
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04076527
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05293938
- **TAURURSODIOL** (CHEMBL272427) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G3SH
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06591455
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00529009
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02965911
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00550862
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03476993
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05749822
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06174402
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06591468
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004784
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006168
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00746486
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01829698
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01857284
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02823353
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02823366
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02916290
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02916641
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06443606
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06715319
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06755541
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07296458
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01510860
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03345589
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02931513
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03188146
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03489889
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03665519
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04076527
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05812612
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06309589
- **URSODIOL** (CHEMBL1551) | group **B** | approval report sources: TTD | on the Approved list today
    - APPROVAL | TTD | https://ttd.idrblab.cn/data/drug/details/D0G3SH
    - EARLY_PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06591455
    - PHASE_1 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00529009
    - PHASE_1_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02965911
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00550862
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01899703
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01904058
    - PHASE_2 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03476993
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05749822
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06174402
    - PHASE_2_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06591468
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00004784
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00006168
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT00746486
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01829698
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01857284
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02823353
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02823366
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02916290
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02916641
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02937012
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04751188
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06443606
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06715319
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06755541
    - PHASE_3 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT07296458
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT01510860
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03345589
    - PHASE_4 | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04650243
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT02931513
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03188146
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03489889
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT03665519
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT04076527
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT05812612
    - UNKNOWN | ClinicalTrials.gov | https://clinicaltrials.gov/study/NCT06309589

