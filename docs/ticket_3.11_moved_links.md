# Ticket 3.11: every In trials card whose Source record moves

The saved pages in tests/, old rule against new rule: 194 cards on 21 pages, plus hereditary angioedema (in no saved page; tested in tests/test_trial_link_this_disease.py). The same list is in tests/source_3_11.py.

Every new link is a ClinicalTrials.gov study that the disease's own list holds for that medicine, with a trial stage and the source "ClinicalTrials.gov". "Read by hand" means the study's conditions were read in the register on 25 Nov (fixtures/labels_read/2.49/registry/trial_reads.json) and name the disease. Lanreotide, Octreotide and Metformin on ADPKD were checked against the saved list only.

| page | medicine | old link | new link | read by hand |
|---|---|---|---|---|
| hereditary angioedema (MONDO_0019623) | Tranexamic Acid | https://clinicaltrials.gov/study/NCT00670345 | https://clinicaltrials.gov/study/NCT00500656 | yes |
| acute myeloid leukemia (MONDO_0018874) | Avapritinib | https://clinicaltrials.gov/study/NCT04825574 | https://clinicaltrials.gov/study/NCT05821738 |  |
| acute myeloid leukemia (MONDO_0018874) | Cediranib | https://www.whocc.no/atc_ddd_index/?code=L01EK02 | https://clinicaltrials.gov/study/NCT00321581 |  |
| acute myeloid leukemia (MONDO_0018874) | Crizotinib | https://clinicaltrials.gov/study/NCT02487316 | https://clinicaltrials.gov/study/NCT02638428 |  |
| acute myeloid leukemia (MONDO_0018874) | Dasatinib Anhydrous | https://www.ema.europa.eu/en/medicines/human/EPAR/dasatinib-accordpharma | https://clinicaltrials.gov/study/NCT02013648 |  |
| acute myeloid leukemia (MONDO_0018874) | Decitabine | https://clinicaltrials.gov/study/NCT01011283 | https://clinicaltrials.gov/study/NCT00260832 |  |
| acute myeloid leukemia (MONDO_0018874) | Imatinib | https://clinicaltrials.gov/study/NCT00171899 | https://clinicaltrials.gov/study/NCT00171249 |  |
| acute myeloid leukemia (MONDO_0018874) | Imetelstat | https://www.ema.europa.eu/en/medicines/human/EPAR/rytelo | https://clinicaltrials.gov/study/NCT05583552 |  |
| acute myeloid leukemia (MONDO_0018874) | Isotretinoin | https://clinicaltrials.gov/study/NCT01404130 | https://clinicaltrials.gov/study/NCT00003405 |  |
| acute myeloid leukemia (MONDO_0018874) | Lestaurtinib | https://ttd.idrblab.cn/data/drug/details/D0V9WF | https://clinicaltrials.gov/study/NCT00030186 |  |
| acute myeloid leukemia (MONDO_0018874) | Momelotinib | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html | https://clinicaltrials.gov/study/NCT06235801 |  |
| acute myeloid leukemia (MONDO_0018874) | Nintedanib | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html | https://clinicaltrials.gov/study/NCT02665143 |  |
| acute myeloid leukemia (MONDO_0018874) | Pacritinib | https://ttd.idrblab.cn/data/drug/details/D0PN8H | https://clinicaltrials.gov/study/NCT01620216 |  |
| acute myeloid leukemia (MONDO_0018874) | Pazopanib | https://clinicaltrials.gov/study/NCT01205230 | https://clinicaltrials.gov/study/NCT01361334 |  |
| acute myeloid leukemia (MONDO_0018874) | Pexidartinib | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=24c5a6f1-b640-4d14-b44b-dd293ed002b1 | https://clinicaltrials.gov/study/NCT01349049 |  |
| acute myeloid leukemia (MONDO_0018874) | Regorafenib | https://clinicaltrials.gov/study/NCT02287025 | https://clinicaltrials.gov/study/NCT03042689 |  |
| acute myeloid leukemia (MONDO_0018874) | Ruxolitinib | https://www.accessdata.fda.gov/drugsatfda_docs/label/2024/217900Orig1s000correctedlbl.pdf | https://clinicaltrials.gov/study/NCT00674479 |  |
| acute myeloid leukemia (MONDO_0018874) | Sorafenib | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html | https://clinicaltrials.gov/study/NCT01253070 |  |
| acute myeloid leukemia (MONDO_0018874) | Sunitinib | https://clinicaltrials.gov/study/NCT00930345 | https://clinicaltrials.gov/study/NCT00783653 |  |
| acute myeloid leukemia (MONDO_0018874) | Tretinoin | https://clinicaltrials.gov/study/NCT00240513 | https://clinicaltrials.gov/study/NCT00002658 |  |
| AL amyloidosis (MONDO_0019438) | Dexamethasone | https://clinicaltrials.gov/study/NCT00209495 | https://clinicaltrials.gov/study/NCT01277016 |  |
| asthma (MONDO_0004979) | Arformoterol | https://clinicaltrials.gov/study/NCT00571428 | https://clinicaltrials.gov/study/NCT00583947 |  |
| asthma (MONDO_0004979) | Betamethasone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT00272506 |  |
| asthma (MONDO_0004979) | Betamethasone Dipropionate | https://clinicaltrials.gov/study/NCT00216892 | https://clinicaltrials.gov/study/NCT00272506 |  |
| asthma (MONDO_0004979) | Betamethasone Phosphoric Acid | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT00272506 |  |
| asthma (MONDO_0004979) | Deflazacort | https://clinicaltrials.gov/study/NCT04365088 | https://clinicaltrials.gov/study/NCT04227483 |  |
| asthma (MONDO_0004979) | Lebrikizumab | https://clinicaltrials.gov/study/NCT06906497 | https://clinicaltrials.gov/study/NCT01867125 |  |
| asthma (MONDO_0004979) | Nadolol | https://clinicaltrials.gov/study/NCT00567216 | https://clinicaltrials.gov/study/NCT01804218 |  |
| asthma (MONDO_0004979) | Olodaterol | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=01e15aee-40e0-23f3-537f-c96dd63e2cb1 | https://clinicaltrials.gov/study/NCT00467740 |  |
| asthma (MONDO_0004979) | Propranolol | https://clinicaltrials.gov/study/NCT00862095 | https://clinicaltrials.gov/study/NCT01074853 |  |
| asthma (MONDO_0004979) | Tralokinumab | https://clinicaltrials.gov/study/NCT06773455 | https://clinicaltrials.gov/study/NCT02161757 |  |
| asthma (MONDO_0004979) | Triamcinolone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT00272506 |  |
| asthma (MONDO_0004979) | Triamcinolone Hexacetonide | https://clinicaltrials.gov/study/NCT00324168 | https://clinicaltrials.gov/study/NCT00272506 |  |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Everolimus | https://clinicaltrials.gov/study/NCT00154297 | https://clinicaltrials.gov/study/NCT02134899 | yes |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Lanreotide | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html | https://clinicaltrials.gov/study/NCT01616927 |  |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Lisinopril Anhydrous | https://clinicaltrials.gov/study/NCT00000542 | https://clinicaltrials.gov/study/NCT00283686 | yes |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Metformin | https://www.ema.europa.eu/en/medicines/human/EPAR/avandamet | https://clinicaltrials.gov/study/NCT03764605 |  |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Octreotide | https://www.ema.europa.eu/en/medicines/human/EPAR/mycapssa | https://clinicaltrials.gov/study/NCT01377246 |  |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Pasireotide | https://clinicaltrials.gov/study/NCT02527993 | https://clinicaltrials.gov/study/NCT01670110 | yes |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Sirolimus | https://clinicaltrials.gov/study/NCT00044720 | https://clinicaltrials.gov/study/NCT00346918 | yes |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Somatostatin | https://clinicaltrials.gov/study/NCT00863837 | https://clinicaltrials.gov/study/NCT00309283 | yes |
| autosomal dominant polycystic kidney disease (MONDO_0004691) | Telmisartan | https://www.ema.europa.eu/en/medicines/human/EPAR/telmisartan-teva | https://clinicaltrials.gov/study/NCT00283686 | yes |
| chronic myeloid leukemia (MONDO_0011996) | Clofarabine | https://www.ema.europa.eu/en/medicines/human/EPAR/ivozall | https://clinicaltrials.gov/study/NCT00067028 |  |
| chronic myeloid leukemia (MONDO_0011996) | Filgrastim | https://www.ema.europa.eu/en/medicines/human/EPAR/filgrastim-ratiopharm | https://clinicaltrials.gov/study/NCT00002789 |  |
| chronic myeloid leukemia (MONDO_0011996) | Fludarabine Phosphate | https://clinicaltrials.gov/study/NCT00220311 | https://clinicaltrials.gov/study/NCT00002833 |  |
| chronic myeloid leukemia (MONDO_0011996) | Gemcitabine | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=49f9e774-52f9-40af-aecf-217c11e243ce | https://clinicaltrials.gov/study/NCT00003727 |  |
| chronic myeloid leukemia (MONDO_0011996) | Interferon ALFA-2A | https://ttd.idrblab.cn/data/drug/details/D09PMV | https://clinicaltrials.gov/study/NCT02201459 |  |
| chronic myeloid leukemia (MONDO_0011996) | Lenograstim | https://clinicaltrials.gov/study/NCT06988826 | https://clinicaltrials.gov/study/NCT00001144 |  |
| chronic myeloid leukemia (MONDO_0011996) | Midostaurin | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=11fa3fc9-6776-49a6-b1c1-653f627c3e58 | https://clinicaltrials.gov/study/NCT02115295 |  |
| chronic myeloid leukemia (MONDO_0011996) | Pegfilgrastim | https://www.ema.europa.eu/en/medicines/human/EPAR/neupopeg | https://clinicaltrials.gov/study/NCT00001144 |  |
| chronic myeloid leukemia (MONDO_0011996) | Peginterferon ALFA-2A | https://clinicaltrials.gov/study/NCT00077636 | https://clinicaltrials.gov/study/NCT00050531 |  |
| chronic myeloid leukemia (MONDO_0011996) | Peginterferon ALFA-2B | https://www.ema.europa.eu/en/medicines/human/EPAR/pegintron | https://clinicaltrials.gov/study/NCT00037882 |  |
| chronic myeloid leukemia (MONDO_0011996) | Regramostim | https://clinicaltrials.gov/study/NCT01718210 | https://clinicaltrials.gov/study/NCT00267085 |  |
| chronic myeloid leukemia (MONDO_0011996) | Ropeginterferon ALFA-2B | https://clinicaltrials.gov/study/NCT06290765 | https://clinicaltrials.gov/study/NCT00037882 |  |
| chronic myeloid leukemia (MONDO_0011996) | Sorafenib | https://clinicaltrials.gov/study/NCT01203787 | https://clinicaltrials.gov/study/NCT00661180 |  |
| Cushing syndrome (MONDO_0018912) | Abiraterone Acetate | https://clinicaltrials.gov/study/NCT02485691 | https://clinicaltrials.gov/study/NCT03145285 |  |
| Cushing syndrome (MONDO_0018912) | Metyrapone | https://clinicaltrials.gov/study/NCT07268222 | https://clinicaltrials.gov/study/NCT02297945 |  |
| depressive disorder (MONDO_0002050) | Agomelatine | https://ttd.idrblab.cn/data/drug/details/D0Y8UB | https://clinicaltrials.gov/study/NCT01531309 |  |
| depressive disorder (MONDO_0002050) | Amphetamine | https://clinicaltrials.gov/study/NCT03945175 | https://clinicaltrials.gov/study/NCT00069927 |  |
| depressive disorder (MONDO_0002050) | Brexpiprazole | https://clinicaltrials.gov/study/NCT03526354 | https://clinicaltrials.gov/study/NCT03737474 |  |
| depressive disorder (MONDO_0002050) | Chlordiazepoxide | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=74c4320d-c90d-436b-97da-07496ba88aed | https://clinicaltrials.gov/study/NCT01109030 |  |
| depressive disorder (MONDO_0002050) | Cipepofol | https://clinicaltrials.gov/study/NCT05035069 | https://clinicaltrials.gov/study/NCT05266560 |  |
| depressive disorder (MONDO_0002050) | Clonazepam | https://clinicaltrials.gov/study/NCT00282828 | https://clinicaltrials.gov/study/NCT04884503 |  |
| depressive disorder (MONDO_0002050) | Desvenlafaxine | https://clinicaltrials.gov/study/NCT01056289 | https://clinicaltrials.gov/study/NCT04345471 |  |
| depressive disorder (MONDO_0002050) | Dextroamphetamine | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ffd56d70-d884-43be-a994-6e70a10e823e | https://clinicaltrials.gov/study/NCT00069927 |  |
| depressive disorder (MONDO_0002050) | Dextromethorphan | https://clinicaltrials.gov/study/NCT00605605 | https://clinicaltrials.gov/study/NCT02426983 |  |
| depressive disorder (MONDO_0002050) | Droxidopa | https://clinicaltrials.gov/study/NCT04510922 | https://clinicaltrials.gov/study/NCT00547911 |  |
| depressive disorder (MONDO_0002050) | Isoflurane | https://clinicaltrials.gov/study/NCT00144118 | https://clinicaltrials.gov/study/NCT04171193 |  |
| depressive disorder (MONDO_0002050) | Ketamine | https://clinicaltrials.gov/study/NCT00163969 | https://clinicaltrials.gov/study/NCT02299440 |  |
| depressive disorder (MONDO_0002050) | Lamotrigine | https://clinicaltrials.gov/study/NCT00043901 | https://clinicaltrials.gov/study/NCT00063362 |  |
| depressive disorder (MONDO_0002050) | Levodopa | https://www.ema.europa.eu/en/medicines/human/EPAR/numient | https://clinicaltrials.gov/study/NCT04469959 |  |
| depressive disorder (MONDO_0002050) | Lumateperone | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=db730b06-6351-47fd-8183-e61e61bbead5 | https://clinicaltrials.gov/study/NCT04985942 |  |
| depressive disorder (MONDO_0002050) | Lurasidone | https://clinicaltrials.gov/study/NCT03304457 | https://clinicaltrials.gov/study/NCT03396068 |  |
| depressive disorder (MONDO_0002050) | Memantine | https://clinicaltrials.gov/study/NCT03168997 | https://clinicaltrials.gov/study/NCT01188148 |  |
| depressive disorder (MONDO_0002050) | Methylphenidate | https://ttd.idrblab.cn/data/drug/details/D02PPN | https://clinicaltrials.gov/study/NCT00069927 |  |
| depressive disorder (MONDO_0002050) | Midazolam | https://clinicaltrials.gov/study/NCT00158873 | https://clinicaltrials.gov/study/NCT00221520 |  |
| depressive disorder (MONDO_0002050) | Modafinil | https://clinicaltrials.gov/study/NCT00102284 | https://clinicaltrials.gov/study/NCT03620253 |  |
| depressive disorder (MONDO_0002050) | Pimavanserin | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=1e6bea44-57d6-4bac-9328-46e1ee59f83b | https://clinicaltrials.gov/study/NCT03482882 |  |
| depressive disorder (MONDO_0002050) | Pramipexole | https://www.ema.europa.eu/en/medicines/human/EPAR/daquiran | https://clinicaltrials.gov/study/NCT05355337 |  |
| depressive disorder (MONDO_0002050) | Propofol | https://clinicaltrials.gov/study/NCT00158873 | https://clinicaltrials.gov/study/NCT03684447 |  |
| depressive disorder (MONDO_0002050) | Quetiapine | https://clinicaltrials.gov/study/NCT00034905 | https://clinicaltrials.gov/study/NCT00953108 |  |
| depressive disorder (MONDO_0002050) | Riluzole | https://clinicaltrials.gov/study/NCT00542412 | https://clinicaltrials.gov/study/NCT00054704 |  |
| depressive disorder (MONDO_0002050) | Risperidone | https://clinicaltrials.gov/study/NCT00000374 | https://clinicaltrials.gov/study/NCT00044681 |  |
| depressive disorder (MONDO_0002050) | Ropinirole | https://clinicaltrials.gov/study/NCT00485069 | https://clinicaltrials.gov/study/NCT00357097 |  |
| depressive disorder (MONDO_0002050) | Tranylcypromine | https://clinicaltrials.gov/study/NCT00177567 | https://clinicaltrials.gov/study/NCT00612807 |  |
| depressive disorder (MONDO_0002050) | Vilazodone | https://clinicaltrials.gov/study/NCT01473381 | https://clinicaltrials.gov/study/NCT00290914 |  |
| depressive disorder (MONDO_0002050) | Zaleplon | https://www.ema.europa.eu/en/medicines/human/EPAR/sonata | https://clinicaltrials.gov/study/NCT03489304 |  |
| depressive disorder (MONDO_0002050) | Ziprasidone | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=90f55022-8d58-4bfb-9464-9bf11395ae17 | https://clinicaltrials.gov/study/NCT00197951 |  |
| Duchenne muscular dystrophy (MONDO_0010679) | Eplerenone | https://clinicaltrials.gov/study/NCT00082589 | https://clinicaltrials.gov/study/NCT02354352 |  |
| Duchenne muscular dystrophy (MONDO_0010679) | Prednisolone | https://clinicaltrials.gov/study/NCT00138970 | https://clinicaltrials.gov/study/NCT03777319 |  |
| Duchenne muscular dystrophy (MONDO_0010679) | Prednisone | https://clinicaltrials.gov/study/NCT00195429 | https://clinicaltrials.gov/study/NCT00004646 |  |
| Duchenne muscular dystrophy (MONDO_0010679) | Spironolactone | https://clinicaltrials.gov/study/NCT00277693 | https://clinicaltrials.gov/study/NCT02354352 |  |
| epilepsy (MONDO_0005027) | Alprazolam | https://clinicaltrials.gov/study/NCT00634790 | https://clinicaltrials.gov/study/NCT03478982 |  |
| epilepsy (MONDO_0005027) | Ketamine | https://clinicaltrials.gov/study/NCT00163969 | https://clinicaltrials.gov/study/NCT05019885 |  |
| epilepsy (MONDO_0005027) | Memantine | https://clinicaltrials.gov/study/NCT03168997 | https://clinicaltrials.gov/study/NCT04417543 |  |
| essential tremor (MONDO_0003233) | Acamprosate | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html | https://clinicaltrials.gov/study/NCT06312800 |  |
| essential tremor (MONDO_0003233) | Brexanolone | https://clinicaltrials.gov/study/NCT04273191 | https://clinicaltrials.gov/study/NCT02277106 |  |
| essential tremor (MONDO_0003233) | Methazolamide | https://clinicaltrials.gov/study/NCT02760121 | https://clinicaltrials.gov/study/NCT06312800 |  |
| essential tremor (MONDO_0003233) | Pramipexole | https://www.ema.europa.eu/en/medicines/human/EPAR/daquiran | https://clinicaltrials.gov/study/NCT01441284 |  |
| essential tremor (MONDO_0003233) | Pregabalin | https://www.ema.europa.eu/en/medicines/human/EPAR/pregabalin-mylan-pharma | https://clinicaltrials.gov/study/NCT00646451 |  |
| essential tremor (MONDO_0003233) | Topiramate | https://clinicaltrials.gov/study/NCT00154076 | https://clinicaltrials.gov/study/NCT00236496 |  |
| essential tremor (MONDO_0003233) | Zonisamide | https://clinicaltrials.gov/study/NCT00154076 | https://clinicaltrials.gov/study/NCT00223743 |  |
| essential tremor (MONDO_0003233) | Zuranolone | https://ttd.idrblab.cn/data/drug/details/D0S5IR | https://clinicaltrials.gov/study/NCT02978781 |  |
| hemophilia A (MONDO_0010602) | Ataluren | https://www.ema.europa.eu/en/medicines/human/EPAR/translarna | https://clinicaltrials.gov/study/NCT00947193 |  |
| hemophilia A (MONDO_0010602) | Coagulation Factor Ix Recombinant Human | https://clinicaltrials.gov/study/NCT00581126 | https://clinicaltrials.gov/study/NCT03549871 |  |
| hemophilia A (MONDO_0010602) | Eftrenonacog Alfa | https://clinicaltrials.gov/study/NCT00749476 | https://clinicaltrials.gov/study/NCT03549871 |  |
| hemophilia A (MONDO_0010602) | Fitusiran | https://ttd.idrblab.cn/data/drug/details/D46RKC | https://clinicaltrials.gov/study/NCT03417102 |  |
| hemophilia A (MONDO_0010602) | Human Coagulation Factor Viii | https://clinicaltrials.gov/study/NCT02932618 | https://clinicaltrials.gov/study/NCT02954575 |  |
| hemophilia A (MONDO_0010602) | Interferon ALFA-2A | https://ttd.idrblab.cn/data/drug/details/D09PMV | https://clinicaltrials.gov/study/NCT05265286 |  |
| hemophilia A (MONDO_0010602) | Peginterferon ALFA-2A | https://clinicaltrials.gov/study/NCT00077636 | https://clinicaltrials.gov/study/NCT05265286 |  |
| hemophilia A (MONDO_0010602) | Peginterferon ALFA-2B | https://www.ema.europa.eu/en/medicines/human/EPAR/pegintron | https://clinicaltrials.gov/study/NCT05265286 |  |
| hemophilia A (MONDO_0010602) | Von Willebrand Factor Human | https://clinicaltrials.gov/study/NCT04555785 | https://clinicaltrials.gov/study/NCT02954575 |  |
| Huntington disease (MONDO_0007739) | Haloperidol | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=153e747c-861d-44c4-aef6-6c49f53ca34a | https://clinicaltrials.gov/study/NCT04071639 |  |
| Huntington disease (MONDO_0007739) | Metformin | https://www.ema.europa.eu/en/medicines/human/EPAR/qtrilmet | https://clinicaltrials.gov/study/NCT04826692 |  |
| Huntington disease (MONDO_0007739) | Olanzapine | https://www.ema.europa.eu/en/medicines/human/EPAR/olansek | https://clinicaltrials.gov/study/NCT00632645 |  |
| Huntington disease (MONDO_0007739) | Riluzole | https://clinicaltrials.gov/study/NCT00542412 | https://clinicaltrials.gov/study/NCT00277602 |  |
| Huntington disease (MONDO_0007739) | Risperidone | https://clinicaltrials.gov/study/NCT00000374 | https://clinicaltrials.gov/study/NCT04071639 |  |
| Huntington disease (MONDO_0007739) | Tiapride | https://ttd.idrblab.cn/data/drug/details/D02LCR | https://clinicaltrials.gov/study/NCT00632645 |  |
| hyperthyroidism (MONDO_0004425) | Thyrotropin | https://ttd.idrblab.cn/data/drug/details/D03EER | https://clinicaltrials.gov/study/NCT00145366 |  |
| narcolepsy (MONDO_0021107) | Armodafinil | https://clinicaltrials.gov/study/NCT01080807 | https://clinicaltrials.gov/study/NCT00078312 |  |
| narcolepsy (MONDO_0021107) | Mazindol | https://www.whocc.no/atc_ddd_index/?code=A08AA05 | https://clinicaltrials.gov/study/NCT04923594 |  |
| narcolepsy (MONDO_0021107) | Reboxetine | https://clinicaltrials.gov/study/NCT00209807 | https://clinicaltrials.gov/study/NCT05059223 |  |
| neuromyelitis optica (MONDO_0019100) | Azathioprine | https://clinicaltrials.gov/study/NCT00307671 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Belimumab | https://clinicaltrials.gov/study/NCT01632241 | https://clinicaltrials.gov/study/NCT05154734 |  |
| neuromyelitis optica (MONDO_0019100) | Betamethasone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Betamethasone Phosphoric Acid | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Daratumumab | https://clinicaltrials.gov/study/NCT03768960 | https://clinicaltrials.gov/study/NCT05403138 |  |
| neuromyelitis optica (MONDO_0019100) | Dexamethasone | https://clinicaltrials.gov/study/NCT00209495 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Filgrastim | https://www.ema.europa.eu/en/medicines/human/EPAR/filgrastim-ratiopharm | https://clinicaltrials.gov/study/NCT03829566 |  |
| neuromyelitis optica (MONDO_0019100) | Hydrocortisone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Lenograstim | https://clinicaltrials.gov/study/NCT06988826 | https://clinicaltrials.gov/study/NCT03829566 |  |
| neuromyelitis optica (MONDO_0019100) | Methylprednisolone | https://clinicaltrials.gov/study/NCT00037115 | https://clinicaltrials.gov/study/NCT02398994 |  |
| neuromyelitis optica (MONDO_0019100) | Mycophenolate Mofetil | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=32001417-130d-4c08-8e63-94ba3627ce5f | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Obinutuzumab | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=df12ceb2-5b4b-4ab5-a317-2a36bf2a3cda | https://clinicaltrials.gov/study/NCT05314010 |  |
| neuromyelitis optica (MONDO_0019100) | Ofatumumab | https://www.ema.europa.eu/en/medicines/human/EPAR/arzerra | https://clinicaltrials.gov/study/NCT05504694 |  |
| neuromyelitis optica (MONDO_0019100) | Pegfilgrastim | https://www.ema.europa.eu/en/medicines/human/EPAR/neupopeg | https://clinicaltrials.gov/study/NCT03829566 |  |
| neuromyelitis optica (MONDO_0019100) | Prednisolone | https://clinicaltrials.gov/study/NCT00138970 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Prednisone | https://clinicaltrials.gov/study/NCT00195429 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Rituximab | https://www.ema.europa.eu/en/medicines/human/EPAR/rituzena | https://clinicaltrials.gov/study/NCT05545384 |  |
| neuromyelitis optica (MONDO_0019100) | Tocilizumab | https://clinicaltrials.gov/study/NCT00996203 | https://clinicaltrials.gov/study/NCT03350633 |  |
| neuromyelitis optica (MONDO_0019100) | Triamcinolone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT04660539 |  |
| neuromyelitis optica (MONDO_0019100) | Ublituximab | https://clinicaltrials.gov/study/NCT07225361 | https://clinicaltrials.gov/study/NCT02276963 |  |
| neuromyelitis optica (MONDO_0019100) | Zanubrutinib | https://clinicaltrials.gov/study/NCT07169331 | https://clinicaltrials.gov/study/NCT05356858 |  |
| Parkinson disease (MONDO_0005180) | Benserazide | https://clinicaltrials.gov/study/NCT00144209 | https://clinicaltrials.gov/study/NCT01227655 |  |
| Parkinson disease (MONDO_0005180) | Clozapine | https://clinicaltrials.gov/study/NCT00001656 | https://clinicaltrials.gov/study/NCT07085195 |  |
| Parkinson disease (MONDO_0005180) | Dextromethorphan | https://clinicaltrials.gov/study/NCT00605605 | https://clinicaltrials.gov/study/NCT00001365 |  |
| Parkinson disease (MONDO_0005180) | Donepezil | https://clinicaltrials.gov/study/NCT00165724 | https://clinicaltrials.gov/study/NCT02206620 |  |
| Parkinson disease (MONDO_0005180) | Eladocagene Exuparvovec | https://www.ema.europa.eu/en/medicines/human/EPAR/upstaza | https://clinicaltrials.gov/study/NCT07267065 |  |
| Parkinson disease (MONDO_0005180) | Ketamine | https://clinicaltrials.gov/study/NCT03621085 | https://clinicaltrials.gov/study/NCT04912115 |  |
| Parkinson disease (MONDO_0005180) | Memantine | https://clinicaltrials.gov/study/NCT03168997 | https://clinicaltrials.gov/study/NCT03858270 |  |
| Parkinson disease (MONDO_0005180) | Quetiapine | https://clinicaltrials.gov/study/NCT00034905 | https://clinicaltrials.gov/study/NCT04164758 |  |
| primary biliary cholangitis (MONDO_0005388) | Bezafibrate | https://www.whocc.no/atc_ddd_index/?code=C10AB02 | https://clinicaltrials.gov/study/NCT01654731 |  |
| primary biliary cholangitis (MONDO_0005388) | Elafibranor | https://www.ema.europa.eu/en/medicines/human/EPAR/iqirvo | https://clinicaltrials.gov/study/NCT04526665 |  |
| primary biliary cholangitis (MONDO_0005388) | Fenofibrate | https://clinicaltrials.gov/study/NCT00745407 | https://clinicaltrials.gov/study/NCT02823353 |  |
| primary biliary cholangitis (MONDO_0005388) | Pemafibrate | https://www.whocc.no/atc_ddd_index/?code=C10AB12 | https://clinicaltrials.gov/study/NCT06247735 |  |
| primary biliary cholangitis (MONDO_0005388) | Saroglitazar | https://ttd.idrblab.cn/data/drug/details/D0E8LA | https://clinicaltrials.gov/study/NCT06427395 |  |
| primary biliary cholangitis (MONDO_0005388) | Ustekinumab | https://www.ema.europa.eu/en/medicines/human/EPAR/eksunbi | https://clinicaltrials.gov/study/NCT01389973 |  |
| pulmonary arterial hypertension (MONDO_0015924) | Sapropterin | https://clinicaltrials.gov/study/NCT01082328 | https://clinicaltrials.gov/study/NCT00435331 |  |
| pulmonary arterial hypertension (MONDO_0015924) | Sorafenib | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html | https://clinicaltrials.gov/study/NCT00452218 |  |
| rheumatoid arthritis (MONDO_0008383) | Belatacept | https://clinicaltrials.gov/study/NCT01953120 | https://clinicaltrials.gov/study/NCT00279760 |  |
| rheumatoid arthritis (MONDO_0008383) | Betamethasone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT00074438 |  |
| rheumatoid arthritis (MONDO_0008383) | Betamethasone Phosphoric Acid | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT00074438 |  |
| rheumatoid arthritis (MONDO_0008383) | Bimekizumab | https://clinicaltrials.gov/study/NCT04340076 | https://clinicaltrials.gov/study/NCT02430909 |  |
| rheumatoid arthritis (MONDO_0008383) | Guselkumab | https://clinicaltrials.gov/study/NCT03573323 | https://clinicaltrials.gov/study/NCT01645280 |  |
| rheumatoid arthritis (MONDO_0008383) | Ixekizumab | https://clinicaltrials.gov/study/NCT03151551 | https://clinicaltrials.gov/study/NCT00966875 |  |
| rheumatoid arthritis (MONDO_0008383) | Levilimab | https://www.whocc.no/atc_ddd_index/?code=L04AC25 | https://clinicaltrials.gov/study/NCT04227366 |  |
| rheumatoid arthritis (MONDO_0008383) | Loxoprofen | https://clinicaltrials.gov/study/NCT00994461 | https://clinicaltrials.gov/study/NCT02467504 |  |
| rheumatoid arthritis (MONDO_0008383) | Ritlecitinib | https://www.pmda.go.jp/english/review-services/reviews/approved-information/drugs/0001.html | https://clinicaltrials.gov/study/NCT02969044 |  |
| rheumatoid arthritis (MONDO_0008383) | Ruxolitinib | https://clinicaltrials.gov/study/NCT02386800 | https://clinicaltrials.gov/study/NCT00550043 |  |
| rheumatoid arthritis (MONDO_0008383) | Secukinumab | https://clinicaltrials.gov/study/NCT02547714 | https://clinicaltrials.gov/study/NCT01350804 |  |
| rheumatoid arthritis (MONDO_0008383) | Triamcinolone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT00074438 |  |
| rheumatoid arthritis (MONDO_0008383) | Triamcinolone Hexacetonide | https://clinicaltrials.gov/study/NCT00324168 | https://clinicaltrials.gov/study/NCT00660647 |  |
| rheumatoid arthritis (MONDO_0008383) | Ustekinumab | https://www.ema.europa.eu/en/medicines/human/EPAR/eksunbi | https://clinicaltrials.gov/study/NCT03148860 |  |
| sarcoidosis (MONDO_0019338) | Adalimumab | https://www.ema.europa.eu/en/medicines/human/EPAR/trudexa | https://clinicaltrials.gov/study/NCT00311246 |  |
| sarcoidosis (MONDO_0019338) | Betamethasone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Betamethasone Dipropionate | https://clinicaltrials.gov/study/NCT00216892 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Betamethasone Phosphoric Acid | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Cravacitinib | https://clinicaltrials.gov/study/NCT05478499 | https://clinicaltrials.gov/study/NCT06725264 |  |
| sarcoidosis (MONDO_0019338) | Golimumab | https://clinicaltrials.gov/study/NCT01212653 | https://clinicaltrials.gov/study/NCT00955279 |  |
| sarcoidosis (MONDO_0019338) | Infliximab | https://clinicaltrials.gov/study/NCT00216177 | https://clinicaltrials.gov/study/NCT00073437 |  |
| sarcoidosis (MONDO_0019338) | Methylprednisolone | https://clinicaltrials.gov/study/NCT00037115 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Methylprednisolone Acetate | https://clinicaltrials.gov/study/NCT00324168 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Tofacitinib | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=68e3d6b2-7838-4d2d-a417-09d919b43e13 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Triamcinolone | https://clinicaltrials.gov/study/NCT00231764 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Triamcinolone Acetonide | https://clinicaltrials.gov/study/NCT00324168 | https://clinicaltrials.gov/study/NCT03793439 |  |
| sarcoidosis (MONDO_0019338) | Triamcinolone Hexacetonide | https://clinicaltrials.gov/study/NCT00324168 | https://clinicaltrials.gov/study/NCT03793439 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Diazoxide | https://clinicaltrials.gov/study/NCT01488136 | https://clinicaltrials.gov/study/NCT03540758 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Dorzagliatin | https://www.whocc.no/atc_ddd_index/?code=A10BX18 | https://clinicaltrials.gov/study/NCT03141073 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Gliclazide | https://clinicaltrials.gov/study/NCT00780715 | https://clinicaltrials.gov/study/NCT00102388 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Insulin Aspart | https://www.ema.europa.eu/en/medicines/human/EPAR/truvelog-mix-30 | https://clinicaltrials.gov/study/NCT00097084 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Insulin Glulisine | https://clinicaltrials.gov/study/NCT01079364 | https://clinicaltrials.gov/study/NCT00135057 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Insulin HUMAN, Isophane | https://clinicaltrials.gov/study/NCT00694122 | https://clinicaltrials.gov/study/NCT06619301 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Insulin Lispro | https://www.ema.europa.eu/en/medicines/human/EPAR/liprolog-0 | https://clinicaltrials.gov/study/NCT00231725 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Insulin Pork | https://ttd.idrblab.cn/data/drug/details/D05ELO | https://clinicaltrials.gov/study/NCT00850096 |  |
| type 2 diabetes mellitus (MONDO_0005148) | Mitiglinide | https://www.whocc.no/atc_ddd_index/?code=A10BX08 | https://clinicaltrials.gov/study/NCT00461617 |  |
