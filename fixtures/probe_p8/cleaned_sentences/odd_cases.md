# Study P8b: every flagged sentence

Written by recount.py. A flag means "a person should look", not "this is wrong".
My reading of each group is in REPORT.md.

## leftover_curly: 0

A curly brace is still in the sentence.


## leftover_eco: 0

The letters ECO: are still in the sentence.


## leftover_square_label: 0

A square-bracket label is still there ("]:" inside, or "[" at the front).


## no_final_stop: 0

The sentence does not end with a full stop (possible cut-off, or the text never had one).


## unbalanced_brackets: 0

Round or square brackets do not pair up (possible cut inside a bracket).


## ends_like_abbreviation: 5

The last word before the full stop is very short or a known abbreviation (the cut may be at an abbreviation, not a sentence end).

- **KCNJ5** (139): Inward rectifier potassium channels are characterized by a greater tendency to allow potassium to flow into the cell rather than out of it.
- **KCNJ3** (139): Inward rectifier potassium channels are characterized by a greater tendency to allow potassium to flow into the cell rather than out of it.
- **F8** (150): Factor VIII, along with calcium and phospholipid, acts as a cofactor for F9/factor IXa when it converts F10/factor X to the activated form, factor Xa.
- **F11** (106): Factor XI triggers the middle phase of the intrinsic pathway of blood coagulation by activating factor IX.
- **NDUFAF1** (85): As part of the MCIA complex, involved in the assembly of the mitochondrial complex I.

## inner_full_stop: 5

A full stop followed by a space is inside the sentence (a sentence end the rule did not take, or an abbreviation).

- **BAG3** (251): Co-chaperone and adapter protein that connects different classes of molecular chaperones including heat shock proteins 70 (HSP70s), e.g. HSPA1A/HSP70 or HSPA8/HSC70, and small heat shock proteins (sHSPs), e.g. HSPB8 (PubMed:27884606, PubMed:30559338).
- **GUCY1A1** (171): Alpha subunit of soluble guanylate cyclase (sGC), a key enzyme in nitric oxide (NO) signaling. sGC functions as a heterodimer consisting of one alpha and one beta subunit.
- **GUCY1B1** (170): Beta subunit of soluble guanylate cyclase (sGC), a key enzyme in nitric oxide (NO) signaling. sGC functions as a heterodimer consisting of one alpha and one beta subunit.
- **CHRNA4** (350): Component of neuronal acetylcholine receptors (nAChRs) that function as pentameric, ligand-gated cation channels with high calcium permeability among other activities. nAChRs are excitatory neurotrasnmitter receptors formed by a collection of nAChR subunits known to mediate synaptic transmission in the nervous system and the neuromuscular junction.
- **CHRNA3** (350): Component of neuronal acetylcholine receptors (nAChRs) that function as pentameric, ligand-gated cation channels with high calcium permeability among other activities. nAChRs are excitatory neurotrasnmitter receptors formed by a collection of nAChR subunits known to mediate synaptic transmission in the nervous system and the neuromuscular junction.

## cut_before_non_capital: 0

The sentence was cut at a full stop whose next character is a digit or a bracket, not a capital letter (the riskiest kind of cut).


## abbreviation_stop_skipped: 1

The rule saw a full stop, judged it an abbreviation, and carried on.

- **BAG3** (251) (skipped at: "ins 70 (HSP70s), e.g. HSPA1A/HSP7" | "roteins (sHSPs), e.g. HSPB8 (PubM"): Co-chaperone and adapter protein that connects different classes of molecular chaperones including heat shock proteins 70 (HSP70s), e.g. HSPA1A/HSP70 or HSPA8/HSC70, and small heat shock proteins (sHSPs), e.g. HSPB8 (PubMed:27884606, PubMed:30559338).

## starts_oddly: 2

The sentence does not start with a capital letter or a digit.

- **SECISBP2** (234): mRNA-binding protein that binds to the SECIS (selenocysteine insertion sequence) element present in the 3'-UTR of mRNAs encoding selenoproteins and facilitates the incorporation of the rare amino acid selenocysteine (PubMed:35709277).
- **CDK5R1** (43): p35 is a neuron specific activator of CDK5.

## hyphen_space_left: 23

A hyphen followed by a space is still there (a real hanging hyphen, or a line-wrap mark the rule left).

- **PRKCQ** (352): Calcium-independent, phospholipid- and diacylglycerol (DAG)-dependent serine/threonine-protein kinase that mediates non-redundant functions in T-cell receptor (TCR) signaling, including T-cells activation, proliferation, differentiation and survival, by mediating activation of multiple transcription factors such as NF-kappa-B, JUN, NFATC1 and NFATC2.
- **SLC6A2** (232): Mediates sodium- and chloride-dependent transport of norepinephrine (also known as noradrenaline), the primary signaling neurotransmitter in the autonomic sympathetic nervous system (PubMed:2008212, PubMed:8125921, PubMed:38750358).
- **TUBB** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBA1B** (171): Tubulin is the major constituent of microtubules, protein filaments consisting of alpha- and beta-tubulin heterodimers (PubMed:38305685, PubMed:34996871, PubMed:38609661).
- **TUBB4A** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBB1** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBA3C** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBB2B** (219): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers (PubMed:23001566, PubMed:26732629, PubMed:28013290).
- **TUBB4B** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBB6** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBB3** (171): Tubulin is the major constituent of microtubules, protein filaments consisting of alpha- and beta-tubulin heterodimers (PubMed:34996871, PubMed:38305685, PubMed:38609661).
- **TUBB2A** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBA4A** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBA3E** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBB8** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **TUBA1C** (167): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers.
- **SLC6A3** (214): Mediates sodium- and chloride-dependent transport of dopamine (PubMed:10375632, PubMed:11093780, PubMed:1406597, PubMed:15505207, PubMed:19478460, PubMed:39112701, PubMed:39112703, PubMed:39112705, PubMed:8302271).
- **CTSG** (98): Serine protease with trypsin- and chymotrypsin-like specificity (PubMed:29652924, PubMed:8194606).
- **PTEN** (162): Dual-specificity protein phosphatase, dephosphorylating tyrosine-, serine- and threonine-phosphorylated proteins (PubMed:9187108, PubMed:9256433, PubMed:9616126).
- **TLR4** (426): Transmembrane receptor that functions as a pattern recognition receptor recognizing pathogen- and damage-associated molecular patterns (PAMPs and DAMPs) to induce innate immune responses via downstream signaling pathways (PubMed:10835634, PubMed:15809303, PubMed:16622205, PubMed:17292937, PubMed:17478729, PubMed:20037584, PubMed:20711192, PubMed:23880187, PubMed:27022195, PubMed:29038465, PubMed:17803912, PubMed:15852007).
- **HR** (101): Histone demethylase that specifically demethylates both mono- and dimethylated 'Lys-9' of histone H3.
- **LAT** (163): Required for TCR (T-cell antigen receptor)- and pre-TCR-mediated signaling, both in mature T-cells and during their development (PubMed:23514740, PubMed:25907557).
- **FUT2** (408): Catalyzes the transfer of L-fucose, from a guanosine diphosphate-beta-L-fucose, to the terminal galactose on both O- and N-linked glycans chains of cell surface glycoproteins and glycolipids and the resulting epitope regulates several processes such as cell-cell interaction including host-microbe interaction, cell surface expression and cell proliferation (PubMed:12692541, PubMed:7876235, PubMed:8018146).

## slash_space_left: 0

A slash followed by a space is still there.


## space_before_hyphen: 4

A space sits in front of a hyphen ("14 -18"); this is how the text arrived.

- **PPT1** (212): Has thioesterase activity against fatty acid thioesters with 14 -18 carbons, including palmitoyl-CoA, S-palmitoyl-N-acetylcysteamine, and palmitoylated proteins (PubMed:12855696, PubMed:26731412, PubMed:8816748).
- **SSTR2** (37): Receptor for somatostatin-14 and -28.
- **SSTR1** (76): Receptor for somatostatin with higher affinity for somatostatin-14 than -28.
- **SSTR3** (37): Receptor for somatostatin-14 and -28.

## double_punctuation: 0

Two punctuation marks in a row that look like a slip ("..", ",,", " ,", "( ", " )").


## wrap_joined: 76

The line-wrap rule joined something in this sentence (check it was right to).

- **TSLP** (153) (joined at: "release of T-cell- attracting chemoki"): Cytokine that induces the release of T-cell-attracting chemokines from monocytes and, in particular, enhances the maturation of CD11c(+) dendritic cells.
- **ADRA2A** (320) (joined at: "ation, and voltage- gated calcium chan"): Alpha-2 adrenergic receptors are G protein-coupled receptors for catecholamines that activate the G(i/o) protein pathway, thereby promoting adenylyl cyclase inhibition, ERK1/2 stimulation, and voltage-gated calcium channels suppression (PubMed:2170371, PubMed:23105096, PubMed:2568356, PubMed:35245122, PubMed:27376152).
- **GLP1R** (180) (joined at: "ike peptide 1 (GLP- 1) (PubMed:1986172"): G protein-coupled receptor for glucagon-like peptide 1 (GLP-1) (PubMed:19861722, PubMed:26308095, PubMed:27196125, PubMed:28514449, PubMed:7517895, PubMed:8216285, PubMed:8405712).
- **GPD2** (153) (joined at: "he pancreatic beta- cell glucose-sensi"): Calcium-responsive mitochondrial glycerol-3-phosphate dehydrogenase which seems to be a key component of the pancreatic beta-cell glucose-sensing device.
- **CDKAL1** (221) (joined at: "ylthiolation of N6- threonylcarbamoyla" | "the formation of 2- methylthio-N6-thre"): Catalyzes the methylthiolation of N6-threonylcarbamoyladenosine (t(6)A), leading to the formation of 2-methylthio-N6-threonylcarbamoyladenosine (ms(2)t(6)A) at position 37 in tRNAs that read codons beginning with adenine.
- **KCNQ2** (200) (joined at: "d potassium (Kv) M- channel which is r"): Pore-forming subunit of the voltage-gated potassium (Kv) M-channel which is responsible for the M-current, a key controller of neuronal excitability (PubMed:24277843, PubMed:28793216, PubMed:9836639).
- **PPT1** (212) (joined at: "CoA, S-palmitoyl-N- acetylcysteamine,"): Has thioesterase activity against fatty acid thioesters with 14 -18 carbons, including palmitoyl-CoA, S-palmitoyl-N-acetylcysteamine, and palmitoylated proteins (PubMed:12855696, PubMed:26731412, PubMed:8816748).
- **JAK2** (376) (joined at: "pha, IFN-beta, IFN- gamma and multiple"): Non-membrane spanning protein tyrosine kinase that phosphorylates type I receptors such as growth hormone (GHR), prolactin (PRLR), leptin (LEPR), erythropoietin (EPOR), thrombopoietin receptor (MPL/TPOR); or type II receptors including IFN-alpha, IFN-beta, IFN-gamma and multiple interleukins (PubMed:15690087, PubMed:15899890, PubMed:7615558, PubMed:9188471, PubMed:9657743).
- **PTGS1** (271) (joined at: "e ((5Z,8Z,11Z,14Z)- eicosatetraenoate,"): Dual cyclooxygenase and peroxidase that plays an important role in the biosynthesis pathway of prostanoids, a class of C20 oxylipins mainly derived from arachidonate ((5Z,8Z,11Z,14Z)-eicosatetraenoate, AA, C20:4(n-6)), with a particular role in the inflammatory response.
- **PRKCQ** (352) (joined at: "acylglycerol (DAG)- dependent serine/t"): Calcium-independent, phospholipid- and diacylglycerol (DAG)-dependent serine/threonine-protein kinase that mediates non-redundant functions in T-cell receptor (TCR) signaling, including T-cells activation, proliferation, differentiation and survival, by mediating activation of multiple transcription factors such as NF-kappa-B, JUN, NFATC1 and NFATC2.
- **ALOX5** (455) (joined at: "e ((5Z,8Z,11Z,14Z)- eicosatetraenoate)" | "dehydration to 5,6- epoxyeicosatetraen"): Catalyzes the oxygenation of arachidonate ((5Z,8Z,11Z,14Z)-eicosatetraenoate) to 5-hydroperoxyeicosatetraenoate (5-HPETE) followed by the dehydration to 5,6-epoxyeicosatetraenoate (Leukotriene A4/LTA4), the first two steps in the biosynthesis of leukotrienes, which are potent mediators of inflammation (PubMed:19022417, PubMed:21233389, PubMed:22516296, PubMed:23246375, PubMed:24282679, PubMed:24893149, PubMed:31664810, PubMed:8615788, PubMed:8631361).
- **TNFRSF11A** (105) (joined at: "ssential for RANKL- mediated osteoclas"): Receptor for TNFSF11/RANKL/TRANCE/OPGL; essential for RANKL-mediated osteoclastogenesis (PubMed:9878548).
- **COPB2** (251) (joined at: "Golgi non-clathrin- coated vesicles, w"): The coatomer is a cytosolic protein complex that binds to dilysine motifs and reversibly associates with Golgi non-clathrin-coated vesicles, which further mediate biosynthetic protein transport from the ER, via the Golgi up to the trans Golgi network.
- **SH2B3** (107) (joined at: "to phospholipase C- gamma-1, GRB2 and"): Links T-cell receptor activation signal to phospholipase C-gamma-1, GRB2 and phosphatidylinositol 3-kinase.
- **ATP1A3** (213) (joined at: "of the Na(+)/K(+)- transporting ATPas"): Neuron-specific alpha catalytic component of the Na(+)/K(+)-transporting ATPase, which catalyzes the hydrolysis of ATP coupled with the exchange of Na(+) and K(+) ions across the plasma membrane (PubMed:36075933).
- **ATP1A4** (141) (joined at: "of the Na(+)/K(+)- ATPase responsible"): Sperm-specific catalytic alpha subunit of the Na(+)/K(+)-ATPase responsible for ATP-dependent Na(+)/K(+) exchange across the plasma membrane.
- **SCN10A** (114) (joined at: "diates the voltage- dependent sodium i"): Tetrodotoxin-resistant channel that mediates the voltage-dependent sodium ion permeability of excitable membranes.
- **EPOR** (196) (joined at: "tes erythropoietin- induced erythrobla"): Receptor for erythropoietin, which mediates erythropoietin-induced erythroblast proliferation and differentiation (PubMed:10388848, PubMed:2163695, PubMed:2163696, PubMed:8662939, PubMed:9774108).
- **P4HTM** (112) (joined at: "nal formation of 4- hydroxyproline in"): Catalyzes the post-translational formation of 4-hydroxyproline in hypoxia-inducible factor (HIF) alpha proteins.
- **IYD** (208) (joined at: "yrosines such as 3- bromo-L-tyrosine," | "L-tyrosine and 3,5- diiodo-L-tyrosine"): Catalyzes the dehalogenation of halotyrosines such as 3-bromo-L-tyrosine, 3-chloro-L-tyrosine, 3-iodo-L-tyrosine and 3,5-diiodo-L-tyrosine (PubMed:15289438, PubMed:18434651, PubMed:25395621, PubMed:28157283).
- **HTR3A** (157) (joined at: ")-activated cation- selective channel"): Forms serotonin (5-hydroxytryptamine/5-HT3)-activated cation-selective channel complexes, which when activated cause fast, depolarizing responses in neurons.
- **HTR3B** (157) (joined at: ")-activated cation- selective channel"): Forms serotonin (5-hydroxytryptamine/5-HT3)-activated cation-selective channel complexes, which when activated cause fast, depolarizing responses in neurons.
- **HTR3D** (157) (joined at: ")-activated cation- selective channel"): Forms serotonin (5-hydroxytryptamine/5-HT3)-activated cation-selective channel complexes, which when activated cause fast, depolarizing responses in neurons.
- **HTR3E** (157) (joined at: ")-activated cation- selective channel"): Forms serotonin (5-hydroxytryptamine/5-HT3)-activated cation-selective channel complexes, which when activated cause fast, depolarizing responses in neurons.
- **HTR3C** (157) (joined at: ")-activated cation- selective channel"): Forms serotonin (5-hydroxytryptamine/5-HT3)-activated cation-selective channel complexes, which when activated cause fast, depolarizing responses in neurons.
- **PARK7** (365) (joined at: "s sensor and redox- sensitive chaperon"): Multifunctional protein with controversial molecular function which plays an important role in cell protection against oxidative stress and cell death acting as oxidative stress sensor and redox-sensitive chaperone and protease (PubMed:12796482, PubMed:17015834, PubMed:18711745, PubMed:19229105, PubMed:20304780, PubMed:25416785, PubMed:26995087, PubMed:28993701).
- **GBA1** (317) (joined at: "Cers (such as beta- D-glucosyl-(1<->1'"): Glucosylceramidase that catalyzes, within the lysosomal compartment, the hydrolysis of glucosylceramides/GlcCers (such as beta-D-glucosyl-(1<->1')-N-acylsphing-4-enine) into free ceramides (such as N-acylsphing-4-enine) and glucose (PubMed:15916907, PubMed:24211208, PubMed:32144204, PubMed:39395789, PubMed:9201993).
- **MAOB** (482) (joined at: "l-4-phenyl-1,2,3,6- tetrahydropyridine"): Catalyzes the oxidative deamination of primary and some secondary amines such as neurotransmitters, and exogenous amines including the tertiary amine, neurotoxin 1-methyl-4-phenyl-1,2,3,6-tetrahydropyridine (MPTP), with concomitant reduction of oxygen to hydrogen peroxide and participates in the metabolism of neuroactive and vasoactive amines in the central nervous system and peripheral tissues (PubMed:11049757, PubMed:11134050, PubMed:20493079, PubMed:8316221, PubMed:8665924).
- **PSEN1** (450) (joined at: "s and APP (amyloid- beta precursor pro"): Catalytic subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:10206644, PubMed:10545183, PubMed:10593990, PubMed:10811883, PubMed:10899933, PubMed:12679784, PubMed:12740439, PubMed:15274632, PubMed:20460383, PubMed:25043039, PubMed:26280335, PubMed:28269784, PubMed:30598546, PubMed:30630874).
- **PSEN2** (297) (joined at: "s and APP (amyloid- beta precursor pro"): Catalytic subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:10497236, PubMed:10652302, PubMed:16752394, PubMed:27293189, PubMed:36272978).
- **EPHA1** (194) (joined at: "iscuously membrane- bound ephrin-A fam"): Receptor tyrosine kinase which binds promiscuously membrane-bound ephrin-A family ligands residing on adjacent cells, leading to contact-dependent bidirectional signaling into neighboring cells.
- **LMX1B** (111) (joined at: "lation of podocyte- expressed genes (P"): Transcription factor involved in the regulation of podocyte-expressed genes (PubMed:24042019, PubMed:28059119).
- **ADRA2C** (253) (joined at: "ation, and voltage- gated calcium chan"): Alpha-2 adrenergic receptors are G protein-coupled receptors for catecholamines that activate the G(i/o) protein pathway, thereby promoting adenylyl cyclase inhibition, ERK1/2 stimulation, and voltage-gated calcium channels suppression (PubMed:2842764).
- **ADRA2B** (316) (joined at: "ation, and voltage- gated calcium chan"): Alpha-2 adrenergic receptors are G protein-coupled receptors for catecholamines that activate G(i/o) protein pathway, thereby promoting adenylyl cyclase inhibition, ERK1/2 stimulation, and voltage-gated calcium channels suppression (PubMed:11056163, PubMed:2164221, PubMed:2172775, PubMed:23105096, PubMed:26811329).
- **PGK1** (187) (joined at: "conversion of 1,3- diphosphoglycerate"): Catalyzes one of the two ATP producing reactions in the glycolytic pathway via the reversible conversion of 1,3-diphosphoglycerate to 3-phosphoglycerate (PubMed:30323285, PubMed:7391028).
- **ELAC2** (94) (joined at: "ochondrial tRNA 3'- processing endonuc"): Zinc phosphodiesterase, which displays mitochondrial tRNA 3'-processing endonuclease activity.
- **RET** (432) (joined at: "to glia cell line- derived growth fam"): Receptor tyrosine-protein kinase involved in numerous cellular mechanisms including cell proliferation, neuronal navigation, cell migration, and cell differentiation in response to glia cell line-derived growth family factors (GDNF, NRTN, ARTN, PSPN and GDF15) (PubMed:20064382, PubMed:20616503, PubMed:20702524, PubMed:21357690, PubMed:21454698, PubMed:24560924, PubMed:28846097, PubMed:28846099, PubMed:28953886, PubMed:31118272).
- **EPHA2** (194) (joined at: "iscuously membrane- bound ephrin-A fam"): Receptor tyrosine kinase which binds promiscuously membrane-bound ephrin-A family ligands residing on adjacent cells, leading to contact-dependent bidirectional signaling into neighboring cells.
- **ERLIN1** (160) (joined at: "of inositol 1,4,5- trisphosphate rece"): Component of the ERLIN1/ERLIN2 complex which mediates the endoplasmic reticulum-associated degradation (ERAD) of inositol 1,4,5-trisphosphate receptors (IP3Rs).
- **ERLIN2** (209) (joined at: "of inositol 1,4,5- trisphosphate rece"): Component of the ERLIN1/ERLIN2 complex which mediates the endoplasmic reticulum-associated degradation (ERAD) of inositol 1,4,5-trisphosphate receptors (IP3Rs) such as ITPR1 (PubMed:17502376, PubMed:19240031).
- **DMD** (65) (joined at: "cytoskeleton via F- actin. Ligand for"): Anchors the extracellular matrix to the cytoskeleton via F-actin.
- **SMN1** (233) (joined at: "ng of cellular pre- mRNAs (PubMed:1898"): The SMN complex catalyzes the assembly of small nuclear ribonucleoproteins (snRNPs), the building blocks of the spliceosome, and thereby plays an important role in the splicing of cellular pre-mRNAs (PubMed:18984161, PubMed:9845364).
- **SMN2** (233) (joined at: "ng of cellular pre- mRNAs (PubMed:1898"): The SMN complex catalyzes the assembly of small nuclear ribonucleoproteins (snRNPs), the building blocks of the spliceosome, and thereby plays an important role in the splicing of cellular pre-mRNAs (PubMed:18984161, PubMed:9845364).
- **HSPB1** (170) (joined at: "teins in a folding- competent state (P"): Small heat shock protein which functions as a molecular chaperone probably maintaining denatured proteins in a folding-competent state (PubMed:10383393, PubMed:20178975).
- **SEPSECS** (103) (joined at: "to selenocysteinyl- tRNA(Sec) required"): Converts O-phosphoseryl-tRNA(Sec) to selenocysteinyl-tRNA(Sec) required for selenoprotein biosynthesis.
- **TSEN2** (174) (joined at: "ubunit of the tRNA- splicing endonucle"): Constitutes one of the two catalytic subunit of the tRNA-splicing endonuclease complex, a complex responsible for identification and cleavage of the splice sites in pre-tRNA.
- **TSEN34** (174) (joined at: "ubunit of the tRNA- splicing endonucle"): Constitutes one of the two catalytic subunit of the tRNA-splicing endonuclease complex, a complex responsible for identification and cleavage of the splice sites in pre-tRNA.
- **UBQLN2** (230) (joined at: "ncluding ubiquitin- proteasome system" | "oplasmic reticulum- associated protein"): Plays an important role in the regulation of different protein degradation mechanisms and pathways including ubiquitin-proteasome system (UPS), autophagy and the endoplasmic reticulum-associated protein degradation (ERAD) pathway.
- **UGCG** (174) (joined at: "e glucosylceramide- based glycosphingo"): Participates in the initial step of the glucosylceramide-based glycosphingolipid/GSL synthetic pathway at the cytosolic surface of the Golgi (PubMed:1532799, PubMed:8643456).
- **THBS3** (81) (joined at: "o-cell and cell-to- matrix interaction"): Adhesive glycoprotein that mediates cell-to-cell and cell-to-matrix interactions.
- **GNAS** (256) (joined at: "olled by G protein- coupled receptors"): Guanine nucleotide-binding proteins (G proteins) function as transducers in numerous signaling pathways controlled by G protein-coupled receptors (GPCRs) (PubMed:12391161, PubMed:17110384, PubMed:21488135, PubMed:26206488, PubMed:8702665, PubMed:10200251).
- **ADA** (155) (joined at: "of adenosine and 2- deoxyadenosine (Pu"): Catalyzes the hydrolytic deamination of adenosine and 2-deoxyadenosine (PubMed:16670267, PubMed:23193172, PubMed:26166670, PubMed:8452534, PubMed:9361033).
- **FDXR** (317) (joined at: "dney, and sterol C- 27 hydroxylation i"): Serves as the first electron transfer protein in all the mitochondrial P450 systems including cholesterol side chain cleavage in all steroidogenic tissues, steroid 11-beta hydroxylation in the adrenal cortex, 25-OH-vitamin D3-24 hydroxylation in the kidney, and sterol C-27 hydroxylation in the liver (By similarity).
- **PI4KA** (138) (joined at: "er inositol-1,4,5,- trisphosphate."): Acts on phosphatidylinositol (PtdIns) in the first committed step in the production of the second messenger inositol-1,4,5,-trisphosphate.
- **VWF** (228) (joined at: "atrix and platelet- surface receptor c"): Important in the maintenance of hemostasis, it promotes adhesion of platelets to the sites of vascular injury by forming a molecular bridge between sub-endothelial collagen matrix and platelet-surface receptor complex GPIb-IX-V.
- **FUNDC2** (283) (joined at: "iacyl-sn-glycero-3- phospho-(1'-myo-in"): Binds directly and specifically 1,2-Diacyl-sn-glycero-3-phospho-(1'-myo-inositol-3',4',5'-bisphosphate) (PIP3) leading to the recruitment of PIP3 to mitochondria and may play a role in the regulation of the platelet activation via AKT/GSK3B/cGMP signaling pathways (PubMed:29786068).
- **PRF1** (229) (joined at: "y role in granzyme- mediated programme"): Pore-forming protein that plays a key role in granzyme-mediated programmed cell death, and in defense against virus-infected or neoplastic cells (PubMed:20889983, PubMed:21037563, PubMed:24558045, PubMed:9058810, PubMed:9164947).
- **GRK6** (114) (joined at: "forms of G protein- coupled receptors"): Specifically phosphorylates the activated forms of G protein-coupled receptors (PubMed:19423652, PubMed:20048153).
- **RTEL1** (132) (joined at: "icated in telomere- length regulation,"): A probable ATP-dependent DNA helicase implicated in telomere-length regulation, DNA repair and the maintenance of genomic stability.
- **LAT** (163) (joined at: "ptor)- and pre-TCR- mediated signaling"): Required for TCR (T-cell antigen receptor)- and pre-TCR-mediated signaling, both in mature T-cells and during their development (PubMed:23514740, PubMed:25907557).
- **TNIP1** (228) (joined at: "induced NF-kappa-B- dependent gene exp" | "P1 and A20/TNFAIP3- mediated deubiquit"): Inhibits NF-kappa-B activation and TNF-induced NF-kappa-B-dependent gene expression by regulating TAX1BP1 and A20/TNFAIP3-mediated deubiquitination of IKBKG; proposed to link A20/TNFAIP3 to ubiquitinated IKBKG (PubMed:21885437).
- **CUL4A** (323) (joined at: "based E3 ubiquitin- protein ligase com"): Core component of multiple cullin-RING-based E3 ubiquitin-protein ligase complexes which mediate the ubiquitination of target proteins (PubMed:14578910, PubMed:14739464, PubMed:15448697, PubMed:15548678, PubMed:15811626, PubMed:16678110, PubMed:17041588, PubMed:24209620, PubMed:30166453, PubMed:33854232, PubMed:33854239).
- **TNFRSF1A** (66) (joined at: "TNFSF1/lymphotoxin- alpha. The adapter"): Receptor for TNFSF2/TNF and homotrimeric TNFSF1/lymphotoxin-alpha.
- **KCNQ3** (217) (joined at: "d potassium (Kv) M- channel which is r"): Pore-forming subunit of the voltage-gated potassium (Kv) M-channel which is responsible for the M-current, a key controller of neuronal excitability (PubMed:16319223, PubMed:27564677, PubMed:28793216, PubMed:9872318).
- **FUT2** (408) (joined at: "e on both O- and N- linked glycans cha"): Catalyzes the transfer of L-fucose, from a guanosine diphosphate-beta-L-fucose, to the terminal galactose on both O- and N-linked glycans chains of cell surface glycoproteins and glycolipids and the resulting epitope regulates several processes such as cell-cell interaction including host-microbe interaction, cell surface expression and cell proliferation (PubMed:12692541, PubMed:7876235, PubMed:8018146).
- **KLRK1** (219) (joined at: "us cellular stress- inducible ligands"): Functions as an activating and costimulatory receptor involved in immunosurveillance upon binding to various cellular stress-inducible ligands displayed at the surface of autologous tumor cells and virus-infected cells.
- **NCSTN** (314) (joined at: "s and APP (amyloid- beta precursor pro"): Essential subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:10993067, PubMed:12679784, PubMed:25043039, PubMed:26280335, PubMed:30598546, PubMed:30630874).
- **PSENEN** (331) (joined at: "s and APP (amyloid- beta precursor pro"): Essential subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:12522139, PubMed:12679784, PubMed:12740439, PubMed:12763021, PubMed:24941111, PubMed:30598546, PubMed:30630874).
- **CACNG2** (95) (joined at: "properties of AMPA- selective glutamat"): Regulates the trafficking and gating properties of AMPA-selective glutamate receptors (AMPARs).
- **SPRED1** (104) (joined at: "bits growth-factor- mediated activatio"): Tyrosine kinase substrate that inhibits growth-factor-mediated activation of MAP kinase (By similarity).
- **TFR2** (82) (joined at: "ound iron in a non- iron dependent man"): Mediates cellular uptake of transferrin-bound iron in a non-iron dependent manner.
- **CD79A** (264) (joined at: "f antigen to the B- cell antigen recep"): Required in cooperation with CD79B for initiation of the signal transduction cascade activated by binding of antigen to the B-cell antigen receptor complex (BCR) which leads to internalization of the complex, trafficking to late endosomes and antigen presentation.
- **ABCD1** (313) (joined at: "fatty acid (VLCFA)- CoA from the cytos"): ATP-dependent transporter of the ATP-binding cassette (ABC) family involved in the transport of very long chain fatty acid (VLCFA)-CoA from the cytosol to the peroxisome lumen (PubMed:11248239, PubMed:15682271, PubMed:16946495, PubMed:18757502, PubMed:21145416, PubMed:23671276, PubMed:29397936, PubMed:33500543).
- **AIRE** (306) (joined at: "ty of being tissue- restricted in thei"): Transcription factor playing an essential role to promote self-tolerance in the thymus by regulating the expression of a wide array of self-antigens that have the commonality of being tissue-restricted in their expression pattern in the periphery, called tissue restricted antigens (TRA) (PubMed:26084028).
- **THBS2** (81) (joined at: "o-cell and cell-to- matrix interaction"): Adhesive glycoprotein that mediates cell-to-cell and cell-to-matrix interactions.
- **PLCB1** (229) (joined at: "atidylinositol 4,5- bisphosphate into" | "tream of G protein- coupled receptors"): Catalyzes the hydrolysis of 1-phosphatidylinositol 4,5-bisphosphate into diacylglycerol (DAG) and inositol 1,4,5-trisphosphate (IP3) and mediates intracellular signaling downstream of G protein-coupled receptors (PubMed:9188725).

## label_removed: 14

A label such as [Isoform 1] was removed, so the sentence is about that form only.

- **TSLP** (153) (label: [Isoform 1]): Cytokine that induces the release of T-cell-attracting chemokines from monocytes and, in particular, enhances the maturation of CD11c(+) dendritic cells.
- **CLN5** (149) (label: [Bis(monoacylglycero)phosphate synthase CLN5, secreted form]): Catalyzes the synthesis of bis(monoacylglycero)phosphate (BMP) via transacylation of 2 molecules of lysophosphatidylglycerol (LPG) (PubMed:37708259).
- **UMOD** (272) (label: [Uromodulin]): Functions in biogenesis and organization of the apical membrane of epithelial cells of the thick ascending limb of Henle's loop (TALH), where it promotes formation of complex filamentous gel-like structure that may play a role in the water barrier permeability (Probable).
- **THRA** (83) (label: [Isoform Alpha-1]): Nuclear hormone receptor that can act as a repressor or activator of transcription.
- **UBC** (75) (label: [Ubiquitin]): Exists either covalently attached to another protein, or free (unanchored).
- **UBA52** (75) (label: [Ubiquitin]): Exists either covalently attached to another protein, or free (unanchored).
- **RPS27A** (75) (label: [Ubiquitin]): Exists either covalently attached to another protein, or free (unanchored).
- **UBB** (75) (label: [Ubiquitin]): Exists either covalently attached to another protein, or free (unanchored).
- **HTT** (70) (label: [Huntingtin]): May play a role in microtubule-mediated transport or vesicle function.
- **VEGFA** (148) (label: [N-VEGF]): Participates in the induction of key genes involved in the response to hypoxia and in the induction of angiogenesis such as HIF1A (PubMed:35455969).
- **PLG** (121) (label: [Plasmin]): Protease which primary function is to degrade fibrin, the main component of blood clots (PubMed:6094526, PubMed:6919539).
- **KCNA3** (81) (label: [Isoform 1]): Mediates the voltage-dependent potassium ion permeability of excitable membranes.
- **GCG** (55) (label: [Glucagon]): Plays a key role in glucose metabolism and homeostasis.
- **CACNA1F** (292) (label: [Isoform 1]): Voltage-sensitive calcium channels (VSCC) mediate the entry of calcium ions into excitable cells and are also involved in a variety of calcium-dependent processes, including muscle contraction, hormone or neurotransmitter release, gene expression, cell motility, cell division and cell death.

## under_25_chars: 8

Shorter than 25 characters.

- **ADORA2B** (23): Receptor for adenosine.
- **WWOX** (24): Putative oxidoreductase.
- **PLS3** (23): Actin-bundling protein.
- **MYH11** (19): Muscle contraction.
- **APC** (17): Tumor suppressor.
- **LMAN1** (24): Mannose-specific lectin.
- **BDKRB2** (24): Receptor for bradykinin.
- **LHX3** (21): Transcription factor.

## pubmed_citation: 456

A (PubMed:...) citation in round brackets is still there; the order did not ask to remove these.

- **IL4R** (69): Receptor for both interleukin 4 and interleukin 13 (PubMed:17030238).
- **ADORA1** (41): Receptor for adenosine (PubMed:29925945).
- **IL5** (201): Homodimeric cytokine expressed predominantly by T-lymphocytes and NK cells that plays an important role in the survival, differentiation, and chemotaxis of eosinophils (PubMed:2653458, PubMed:9010276).
- **IL33** (181): Cytokine that binds to and signals through the IL1RL1/ST2 receptor which in turn activates NF-kappa-B and MAPK signaling pathways in target cells (PubMed:16286016, PubMed:19841166).
- **IL13** (136): Cytokine that plays important roles in allergic inflammation and immune response to parasite infection (PubMed:8096327, PubMed:8097324).
- **NR3C1** (69): Receptor for glucocorticoids (GC) (PubMed:27120390, PubMed:37478846).
- **ADRB2** (165): G protein-coupled receptor for catecholamines that couples to both G(s) and G(i) proteins, activating bifurcated signaling pathways (PubMed:2831218, PubMed:7915137).
- **CHRM2** (179): Muscarinic receptor for acetylcholine, a neurotransmitter found in the brain, neuromuscular junctions and the autonomic ganglia (PubMed:24256733, PubMed:3443095, PubMed:36690613).
- **ADRA2A** (320): Alpha-2 adrenergic receptors are G protein-coupled receptors for catecholamines that activate the G(i/o) protein pathway, thereby promoting adenylyl cyclase inhibition, ERK1/2 stimulation, and voltage-gated calcium channels suppression (PubMed:2170371, PubMed:23105096, PubMed:2568356, PubMed:35245122, PubMed:27376152).
- **IL5RA** (132): Cell surface receptor that plays an important role in the survival, differentiation, and chemotaxis of eosinophils (PubMed:9378992).
- **IL33R** (220): Receptor for interleukin-33 (IL-33) which plays crucial roles in innate and adaptive immunity, contributing to tissue homeostasis and responses to environmental stresses together with coreceptor IL1RAP (PubMed:35238669).
- **PDE4B** (123): Hydrolyzes the second messenger cAMP, which is a key regulator of many important physiological processes (PubMed:15260978).
- **ADORA3** (229): G protein-coupled receptor (GPCR) for adenosine that plays significant roles in various physiological processes including immune regulation, cardioprotection and neuroprotection (PubMed:38627384, PubMed:40825947, PubMed:9837869).
- **PDE3B** (201): Cyclic nucleotide phosphodiesterase with a dual-specificity for the second messengers cAMP and cGMP, which are key regulators of many important physiological process (PubMed:14592490, PubMed:21393242).
- **PDE3A** (227): Cyclic nucleotide phosphodiesterase with specificity for the second messengers cAMP and cGMP, which are key regulators of many important physiological processes (PubMed:1315035, PubMed:25961942, PubMed:8155697, PubMed:8695850).
- **KCNJ11** (248): Inward rectifier potassium channel that forms the pore of ATP-sensitive potassium channels (KATP), regulating potassium permeability as a function of cytoplasmic ATP and ADP concentrations in many different cells (PubMed:29286281, PubMed:34815345).
- **GCK** (331): Catalyzes the phosphorylation of hexose, such as D-glucose, D-fructose and D-mannose, to hexose 6-phosphate (D-glucose 6-phosphate, D-fructose 6-phosphate and D-mannose 6-phosphate, respectively) (PubMed:11916951, PubMed:15277402, PubMed:17082186, PubMed:18322640, PubMed:19146401, PubMed:25015100, PubMed:7742312, PubMed:8325892).
- **PPARG** (363): Ligand-activated transcription factor that forms obligate heterodimers with the retinoic acid receptor and acts as a key regulator of biological processes, such as adipocyte differentiation, lipid metabolism, glucose homeostasis and beta-oxidation of fatty acids (PubMed:16150867, PubMed:20829347, PubMed:23525231, PubMed:8702406, PubMed:8706692, PubMed:9065481).
- **HNF4A** (238): Transcriptional regulator which controls the expression of hepatic genes during the transition of endodermal cells to hepatic progenitor cells, facilitating the recruitment of RNA pol II to the promoters of target genes (PubMed:30597922).
- **HNF1B** (113): Transcription factor that binds to the inverted palindrome 5'-GTTAATNATTAAC-3' (PubMed:17924661, PubMed:7900999).
- **GLP1R** (180): G protein-coupled receptor for glucagon-like peptide 1 (GLP-1) (PubMed:19861722, PubMed:26308095, PubMed:27196125, PubMed:28514449, PubMed:7517895, PubMed:8216285, PubMed:8405712).
- **WFS1** (172): Participates in the regulation of cellular Ca(2+) homeostasis, at least partly, by modulating the filling state of the endoplasmic reticulum Ca(2+) store (PubMed:16989814).
- **SLC2A2** (179): Facilitative hexose transporter that mediates the transport of glucose, fructose and galactose (PubMed:16186102, PubMed:23396969, PubMed:28083649, PubMed:8027028, PubMed:8457197).
- **IRS1** (238): Signaling adapter protein that participates in the signal transduction from two prominent receptor tyrosine kinases, insulin receptor/INSR and insulin-like growth factor I receptor/IGF1R (PubMed:7541045, PubMed:33991522, PubMed:38625937).
- **MT-ND1** (225): Core subunit of the mitochondrial membrane respiratory chain NADH dehydrogenase (Complex I) which catalyzes electron transfer from NADH through the respiratory chain, using ubiquinone as an electron acceptor (PubMed:1959619).
- **SCN8A** (379): Pore-forming subunit of a voltage-gated sodium channel complex assuming opened or closed conformations in response to the voltage difference across membranes and through which sodium ions selectively pass along their electrochemical gradient (PubMed:24874546, PubMed:25239001, PubMed:25725044, PubMed:26900580, PubMed:29726066, PubMed:33245860, PubMed:36696443, PubMed:36823201).
- **GABRG2** (294): Gamma subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:14993607, PubMed:16412217, PubMed:23909897, PubMed:2538761, PubMed:25489750, PubMed:27864268, PubMed:29950725, PubMed:30602789).
- **KCNQ2** (200): Pore-forming subunit of the voltage-gated potassium (Kv) M-channel which is responsible for the M-current, a key controller of neuronal excitability (PubMed:24277843, PubMed:28793216, PubMed:9836639).
- **SLC2A1** (216): Facilitative glucose transporter, which is responsible for constitutive or basal glucose uptake (PubMed:10227690, PubMed:10954735, PubMed:18245775, PubMed:19449892, PubMed:25982116, PubMed:27078104, PubMed:32860739).
- **GABRA1** (227): Alpha subunit of the heteropentameric ligand-gated chloride channel gated by Gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:23909897, PubMed:25489750, PubMed:29950725, PubMed:30602789).
- **GRIN2A** (380): Component of N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function as heterotetrameric, ligand-gated cation channels with high calcium permeability and voltage-dependent block by Mg(2+) (PubMed:20890276, PubMed:23933818, PubMed:23933819, PubMed:23933820, PubMed:24504326, PubMed:26875626, PubMed:26919761, PubMed:28242877, PubMed:36117210, PubMed:38538865, PubMed:8768735).
- **GABRB3** (277): Beta subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:14993607, PubMed:18514161, PubMed:22243422, PubMed:22303015, PubMed:24909990, PubMed:26950270, PubMed:30602789).
- **TPP1** (116): Lysosomal serine protease with tripeptidyl-peptidase I activity (PubMed:11054422, PubMed:19038966, PubMed:19038967).
- **KCNT1** (48): Sodium-activated K(+) channel (PubMed:37494189).
- **CDKL5** (69): Mediates phosphorylation of MECP2 (PubMed:15917271, PubMed:16935860).
- **GABRB2** (225): Beta subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:19763268, PubMed:27789573, PubMed:29950725, PubMed:8264558).
- **DEPDC5** (221): As a component of the GATOR1 complex functions as an inhibitor of the amino acid-sensing branch of the mTORC1 pathway (PubMed:23723238, PubMed:25457612, PubMed:29590090, PubMed:29769719, PubMed:31548394, PubMed:35338845).
- **PPT1** (212): Has thioesterase activity against fatty acid thioesters with 14 -18 carbons, including palmitoyl-CoA, S-palmitoyl-N-acetylcysteamine, and palmitoylated proteins (PubMed:12855696, PubMed:26731412, PubMed:8816748).
- **CLN5** (149): Catalyzes the synthesis of bis(monoacylglycero)phosphate (BMP) via transacylation of 2 molecules of lysophosphatidylglycerol (LPG) (PubMed:37708259).
- **TYK2** (274): Non-membrane spanning protein tyrosine kinase involved in numerous cytokines and interferons signaling, which regulates cell growth, development, cell migration, innate and adaptive immunity (PubMed:10542297, PubMed:10995743, PubMed:7657660, PubMed:7813427, PubMed:8232552).
- **JAK1** (333): Non-membrane spanning protein tyrosine kinase that phosphorylates signal-transducing subunits of cytokine receptor complexes like IL2RB, IL10RA, IFNAR2, IL6ST, LIFR, OSMR and IL31RA (PubMed:11909529, PubMed:12133952, PubMed:15194700, PubMed:16239216, PubMed:28111307, PubMed:32750333, PubMed:7615558, PubMed:8232552, PubMed:9188471).
- **TRAF3IP2** (164): E3 ubiquitin ligase that catalyzes 'Lys-63'-linked polyubiquitination of target protein, enhancing protein-protein interaction and cell signaling (PubMed:19825828).
- **PADI4** (278): Catalyzes the citrullination/deimination of arginine residues of proteins such as histones, thereby playing a key role in histone code and regulation of stem cell maintenance (PubMed:15339660, PubMed:15345777, PubMed:16567635, PubMed:19153223, PubMed:21245532, PubMed:25622091).
- **JAK2** (376): Non-membrane spanning protein tyrosine kinase that phosphorylates type I receptors such as growth hormone (GHR), prolactin (PRLR), leptin (LEPR), erythropoietin (EPOR), thrombopoietin receptor (MPL/TPOR); or type II receptors including IFN-alpha, IFN-beta, IFN-gamma and multiple interleukins (PubMed:15690087, PubMed:15899890, PubMed:7615558, PubMed:9188471, PubMed:9657743).
- **PTPN22** (258): Acts as a negative regulator of T-cell receptor (TCR) signaling by direct dephosphorylation of the Src family kinases LCK and FYN, ITAMs of the TCRz/CD3 complex, as well as ZAP70, VAV, VCP and other key signaling molecules (PubMed:16461343, PubMed:18056643).
- **MIF** (140): Pro-inflammatory cytokine involved in the innate immune response to bacterial pathogens (PubMed:15908412, PubMed:17443469, PubMed:23776208).
- **IRF5** (331): Transcription factor that plays a critical role in innate immunity by activating expression of type I interferon (IFN) IFNA and INFB and inflammatory cytokines downstream of endolysosomal toll-like receptors TLR7, TLR8 and TLR9 (PubMed:11303025, PubMed:15695821, PubMed:22412986, PubMed:25326418, PubMed:32433612, PubMed:40639948).
- **PTGS2** (410): Dual cyclooxygenase and peroxidase in the biosynthesis pathway of prostanoids, a class of C20 oxylipins mainly derived from arachidonate ((5Z,8Z,11Z,14Z)-eicosatetraenoate, AA, C20:4(n-6)), with a particular role in the inflammatory response (PubMed:11939906, PubMed:16373578, PubMed:17519235, PubMed:19540099, PubMed:22942274, PubMed:26859324, PubMed:27226593, PubMed:7592599, PubMed:7947975, PubMed:9261177).
- **IL17A** (148): Effector cytokine of innate and adaptive immune system involved in antimicrobial host defense and maintenance of tissue integrity (PubMed:24120361).
- **IL23A** (143): Associates with IL12B to form the pro-inflammatory cytokine IL-23 that plays different roles in innate and adaptive immunity (PubMed:11114383).
- **TLR7** (108): Endosomal receptor that plays a key role in innate and adaptive immunity (PubMed:14976261, PubMed:32433612).
- **CD80** (144): Costimulatory molecule that belongs to the immunoglobulin superfamily that plays an important role in T-lymphocyte activation (PubMed:38467718).
- **CD86** (160): Costimulatory molecule that belongs to the immunoglobulin superfamily that plays an important role in T-lymphocyte activation (PubMed:12196291, PubMed:7694363).
- **TLR9** (64): Key component of innate and adaptive immunity (PubMed:14716310).
- **DHFR** (226): Catalyzes the reduction of 7,8-dihydrofolate (DHF) to 5,6,7,8-tetrahydrofolate in a NADPH-dependent manner (PubMed:12096917, PubMed:15039552, PubMed:17569517, PubMed:19196009, PubMed:19478082, PubMed:21876184, PubMed:9719595).
- **CTLA4** (179): Inhibitory receptor acting as a major negative regulator of T-cell responses (PubMed:11279501, PubMed:11279502, PubMed:16551244, PubMed:1714933, PubMed:18641304, PubMed:28484017).
- **AP1S3** (190): Subunit of clathrin-associated adaptor protein complex 1 that plays a role in protein sorting in the late-Golgi/trans-Golgi network (TGN) and/or endosomes (PubMed:24791904, PubMed:36261523).
- **VDR** (200): Nuclear receptor for calcitriol, the active form of vitamin D3 which mediates the action of this vitamin on cells (PubMed:10678179, PubMed:15728261, PubMed:16913708, PubMed:28698609, PubMed:37478846).
- **AHR** (310): Ligand-activated transcription factor that enables cells to adapt to changing conditions by sensing compounds from the environment, diet, microbiome and cellular metabolism, and which plays important roles in development, immunity and cancer (PubMed:23275542, PubMed:30373764, PubMed:32818467, PubMed:7961644).
- **ITGB2** (113): Integrin ITGAL:ITGB2 is a receptor for ICAM1, ICAM2 and ICAM3 (PubMed:1676048, PubMed:23775590, PubMed:38195629).
- **IFIH1** (318): Innate immune receptor which acts as a cytoplasmic sensor of viral nucleic acids and plays a major role in sensing viral infection and in the activation of a cascade of antiviral responses including the induction of type I interferons and pro-inflammatory cytokines (PubMed:28594402, PubMed:32169843, PubMed:33727702).
- **IL12A** (133): Heterodimerizes with IL12B to form the IL-12 cytokine or with EBI3/IL27B to form the IL-35 cytokine (PubMed:8605935, PubMed:8943050).
- **RXRA** (132): Receptor for retinoic acid that acts as a transcription factor (PubMed:10874028, PubMed:11162439, PubMed:11915042, PubMed:37478846).
- **RARA** (113): Receptor for retinoic acid (PubMed:16417524, PubMed:19850744, PubMed:20215566, PubMed:21152046, PubMed:37478846).
- **HRH1** (154): G protein-coupled receptor for histamine, a biogenic amine that functions as an immune modulator and a neurotransmitter (PubMed:33828102, PubMed:8280179).
- **IL22** (105): Cytokine that plays a critical role in modulating tissue responses during inflammation (PubMed:17204547).
- **IL31RA** (197): Functions as a membrane-bound signal-transducing subunit of the IL31 receptor complex (heterodimer composed of OSMR and IL31RA) which binds IL31 (PubMed:15184896, PubMed:15194700, PubMed:15627637).
- **NLRP10** (173): Inhibits autoprocessing of CASP1, CASP1-dependent IL1B secretion, PYCARD aggregation and PYCARD-mediated apoptosis but not apoptosis induced by FAS or BID (PubMed:15096476).
- **SLC6A2** (232): Mediates sodium- and chloride-dependent transport of norepinephrine (also known as noradrenaline), the primary signaling neurotransmitter in the autonomic sympathetic nervous system (PubMed:2008212, PubMed:8125921, PubMed:38750358).
- **ALOX5** (455): Catalyzes the oxygenation of arachidonate ((5Z,8Z,11Z,14Z)-eicosatetraenoate) to 5-hydroperoxyeicosatetraenoate (5-HPETE) followed by the dehydration to 5,6-epoxyeicosatetraenoate (Leukotriene A4/LTA4), the first two steps in the biosynthesis of leukotrienes, which are potent mediators of inflammation (PubMed:19022417, PubMed:21233389, PubMed:22516296, PubMed:23246375, PubMed:24282679, PubMed:24893149, PubMed:31664810, PubMed:8615788, PubMed:8631361).
- **GPR35** (393): G protein-coupled receptor that binds to several ligands including the tryptophan metabolite kynurenic acid (KYNA), lysophosphatidic acid (LPA) or 5-hydroxyindoleacetic acid (5-HIAA) with high affinity, leading to rapid and transient activation of numerous intracellular signaling pathways (PubMed:16754668, PubMed:19473985, PubMed:20361937, PubMed:24347166, PubMed:35148838, PubMed:35926043).
- **TNFSF15** (66): Cytokine that signals through TNFRSF25 receptor (PubMed:11911831).
- **CXCR2** (94): Receptor for interleukin-8 which is a powerful neutrophil chemotactic factor (PubMed:1891716).
- **LRP5** (238): Acts as a coreceptor with members of the frizzled family of seven-transmembrane spanning receptors to transduce signal by Wnt proteins (PubMed:11336703, PubMed:11448771, PubMed:11719191, PubMed:15778503, PubMed:15908424, PubMed:16252235).
- **SLC34A1** (180): Involved in actively transporting phosphate into cells via Na(+) cotransport in the renal brush border membrane (PubMed:12324554, PubMed:20335586, PubMed:26047794, PubMed:8327470).
- **CALCR** (185): G protein-coupled receptor activated by ligand peptides amylin (IAPP), calcitonin (CT/CALCA) and calcitonin gene-related peptide type 1 (CGRP1/CALCA) (PubMed:35324283, PubMed:38603770).
- **PTH1R** (245): G protein-coupled receptor for parathyroid hormone (PTH) and for parathyroid hormone-related peptide (PTHLH) (PubMed:10913300, PubMed:11773434, PubMed:18375760, PubMed:19674967, PubMed:27160269, PubMed:30975883, PubMed:35932760, PubMed:8397094).
- **TNFRSF11A** (105): Receptor for TNFSF11/RANKL/TRANCE/OPGL; essential for RANKL-mediated osteoclastogenesis (PubMed:9878548).
- **AR** (200): Steroid hormone receptors are ligand-activated transcription factors that regulate eukaryotic gene expression and affect cellular proliferation and differentiation in target tissues (PubMed:19022849).
- **SLC22A12** (227): Electroneutral antiporter that translocates urate across the apical membrane of proximal tubular cells in exchange for monovalent organic or inorganic anions (PubMed:12024214, PubMed:22194875, PubMed:35144162, PubMed:35462902).
- **ABCG2** (323): Broad substrate specificity ATP-dependent transporter of the ATP-binding cassette (ABC) family that actively extrudes a wide variety of physiological compounds, dietary toxins and xenobiotics from cells (PubMed:11306452, PubMed:12958161, PubMed:19506252, PubMed:20705604, PubMed:28554189, PubMed:30405239, PubMed:31003562).
- **SLC22A11** (410): Antiporter that mediates the transport of conjugated steroids and other specific organic anions at the basal membrane of syncytiotrophoblast and at the apical membrane of proximal tubule epithelial cells, in exchange for anionic compounds (PubMed:10660625, PubMed:11907186, PubMed:15037815, PubMed:15102942, PubMed:15291761, PubMed:15576633, PubMed:17229912, PubMed:18501590, PubMed:26277985, PubMed:28027879).
- **SLC2A9** (187): High-capacity urate transporter, which may play a role in the urate reabsorption by proximal tubules (PubMed:18327257, PubMed:18701466, PubMed:22647630, PubMed:28083649, PubMed:36749388).
- **PKD2** (156): Forms a nonselective cation channel (PubMed:11854751, PubMed:11991947, PubMed:15692563, PubMed:26269590, PubMed:27071085, PubMed:31441214, PubMed:39009345).
- **SLC16A9** (89): Extracellular pH-and Na(+)-sensitive low-affinity creatine transporter (PubMed:31784090).
- **TUBA1B** (171): Tubulin is the major constituent of microtubules, protein filaments consisting of alpha- and beta-tubulin heterodimers (PubMed:38305685, PubMed:34996871, PubMed:38609661).
- **PKD1** (194): Component of a heteromeric calcium-permeable ion channel formed by PKD1 and PKD2 that is activated by interaction between PKD1 and a Wnt family member, such as WNT3A and WNT9B (PubMed:27214281).
- **TUBB2B** (219): Tubulin is the major constituent of microtubules, a cylinder consisting of laterally associated linear protofilaments composed of alpha- and beta-tubulin heterodimers (PubMed:23001566, PubMed:26732629, PubMed:28013290).
- **TUBB3** (171): Tubulin is the major constituent of microtubules, protein filaments consisting of alpha- and beta-tubulin heterodimers (PubMed:34996871, PubMed:38305685, PubMed:38609661).
- **HMGCR** (299): Catalyzes the conversion of (3S)-hydroxy-3-methylglutaryl-CoA (HMG-CoA) to mevalonic acid, the rate-limiting step in the synthesis of cholesterol and other isoprenoids, thus plays a critical role in cellular cholesterol homeostasis (PubMed:21357570, PubMed:2991281, PubMed:36745799, PubMed:6995544).
- **BAG3** (251): Co-chaperone and adapter protein that connects different classes of molecular chaperones including heat shock proteins 70 (HSP70s), e.g. HSPA1A/HSP70 or HSPA8/HSC70, and small heat shock proteins (sHSPs), e.g. HSPB8 (PubMed:27884606, PubMed:30559338).
- **SLC5A2** (232): Electrogenic Na(+)-coupled sugar symporter that actively transports D-glucose at the plasma membrane, with a Na(+) to sugar coupling ratio of 1:1 (PubMed:20980548, PubMed:28592437, PubMed:34880493, PubMed:37217492, PubMed:38057552).
- **ACE** (370): Dipeptidyl carboxypeptidase that removes dipeptides from the C-terminus of a variety of circulating hormones, such as angiotensin I, bradykinin or enkephalins, thereby playing a key role in the regulation of blood pressure, electrolyte homeostasis or synaptic plasticity (PubMed:15615692, PubMed:20826823, PubMed:2558109, PubMed:4322742, PubMed:7523412, PubMed:7683654).
- **AGTR1** (258): Receptor for angiotensin II, a vasoconstricting peptide, which acts as a key regulator of blood pressure and sodium retention by the kidney (PubMed:15611106, PubMed:1567413, PubMed:25913193, PubMed:26420482, PubMed:30639100, PubMed:32079768, PubMed:8987975).
- **ADRB3** (246): G protein-coupled receptor for catecholamines that couples to both G(s) and G(i) proteins, leading to either activation or inhibition of adenylate cyclase and cAMP-dependent pathway, respectively (PubMed:10188996, PubMed:2570461, PubMed:8641219).
- **MME** (169): Thermolysin-like specificity, but is almost confined on acting on polypeptides of up to 30 amino acids (PubMed:15283675, PubMed:6208535, PubMed:6349683, PubMed:8168535).
- **ADRB1** (185): G protein-coupled receptor for catecholamines that couples to G(s) proteins to activate adenylate cyclase and cAMP-dependent pathway (PubMed:10212248, PubMed:12391161, PubMed:15358775).
- **SLC12A1** (245): Renal sodium, potassium and chloride non-electrogenic ion symporter that mediates the transepithelial NaCl reabsorption in the thick ascending limb and plays an essential role in the urinary concentration and volume regulation (PubMed:21321328).
- **ATP1A1** (248): Catalytic subunit of the Na(+)/K(+)-ATPase pump that hydrolyzes ATP to exchange ions across the plasma membrane, exporting 3 Na(+) and importing 2 K(+) per cycle against electrochemical gradients (PubMed:29499166, PubMed:30388404, PubMed:35803952).
- **SLC12A3** (241): Electroneutral sodium and chloride ion cotransporter, which acts as a key mediator of sodium and chloride reabsorption in kidney distal convoluted tubules (PubMed:18270262, PubMed:21613606, PubMed:22009145, PubMed:36351028, PubMed:36792826).
- **ATP1A3** (213): Neuron-specific alpha catalytic component of the Na(+)/K(+)-transporting ATPase, which catalyzes the hydrolysis of ATP coupled with the exchange of Na(+) and K(+) ions across the plasma membrane (PubMed:36075933).
- **ATP1A2** (175): Catalytic subunit of the Na(+)/K(+)-ATPase that hydrolyzes ATP to exchange ions across the plasma membrane, exporting 3 Na(+) and importing 2 K(+) per cycle (PubMed:33880529).
- **SCN5A** (194): Pore-forming subunit of Nav1.5, a voltage-gated sodium (Nav) channel that directly mediates the depolarizing phase of action potentials in excitable membranes (PubMed:33712541, PubMed:40768348).
- **KCNJ2** (189): Inward rectifier potassium channels are characterized by a greater tendency to allow potassium to flow into the cell rather than out of it (PubMed:36149965, PubMed:7590287, PubMed:9490857).
- **KCNQ1** (251): Pore-forming subunit of the voltage-gated potassium (Kv) channel involved in the regulation of cardiomyocyte excitability and important in normal development and functions of myocardium, inner ear, stomach and colon (PubMed:10646604, PubMed:25441029).
- **KCNH2** (320): Pore-forming (alpha) subunit of voltage-gated inwardly rectifying potassium channel (PubMed:10219239, PubMed:10753933, PubMed:10790218, PubMed:10837251, PubMed:11997281, PubMed:12063277, PubMed:18559421, PubMed:22314138, PubMed:22359612, PubMed:26363003, PubMed:27916661, PubMed:9230439, PubMed:9351446, PubMed:9765245).
- **HCN4** (177): Hyperpolarization-activated ion channel that are permeable to Na(+) and K(+) ions with very slow activation and inactivation (PubMed:10228147, PubMed:10430953, PubMed:20829353).
- **SCN1B** (146): Regulatory subunit of multiple voltage-gated sodium (Nav) channels directly mediating the depolarization of excitable membranes (PubMed:40768348).
- **NKX2-5** (96): Transcription factor required for the development of the heart and the spleen (PubMed:22560297).
- **KCND3** (299): Pore-forming (alpha) subunit of voltage-gated A-type potassium channels that mediates transmembrane potassium transport in excitable membranes, in brain and heart (PubMed:10200233, PubMed:17187064, PubMed:21349352, PubMed:22457051, PubMed:23280837, PubMed:23280838, PubMed:34997220, PubMed:9843794).
- **F10** (198): Factor Xa is a vitamin K-dependent glycoprotein that converts prothrombin to thrombin in the presence of factor Va, calcium and phospholipid during blood clotting (PubMed:22409427, PubMed:39880037).
- **CACNA1C** (383): Pore-forming, alpha-1C subunit of the voltage-gated calcium channel that gives rise to L-type calcium currents (PubMed:12181424, PubMed:15454078, PubMed:15863612, PubMed:16299511, PubMed:17224476, PubMed:20953164, PubMed:23677916, PubMed:24728418, PubMed:26253506, PubMed:27218670, PubMed:29078335, PubMed:29742403, PubMed:30023270, PubMed:30172029, PubMed:34163037, PubMed:8099908).
- **SCNN1B** (231): This is one of the three pore-forming subunits of the heterotrimeric epithelial sodium channel (ENaC), a critical regulator of sodium balance and fluid homeostasis (PubMed:30251954, PubMed:32729833, PubMed:7762608, PubMed:9792722).
- **SCNN1A** (247): This is one of the three pore-forming subunits of the heterotrimeric epithelial sodium channel (ENaC), a critical regulator of sodium balance and fluid homeostasis (PubMed:30251954, PubMed:32729833, PubMed:8023962, PubMed:8278374, PubMed:9792722).
- **CFTR** (148): Epithelial ion channel that plays an important role in the regulation of epithelial ion and water transport and fluid homeostasis (PubMed:26823428).
- **SCNN1G** (247): This is one of the three pore-forming subunits of the heterotrimeric epithelial sodium channel (ENaC), a critical regulator of sodium balance and fluid homeostasis (PubMed:30251954, PubMed:32729833, PubMed:7550319, PubMed:7762608, PubMed:9792722).
- **ELANE** (114): Serine protease that modifies the functions of natural killer cells, monocytes and granulocytes (PubMed:15140022).
- **EGLN2** (228): Prolyl hydroxylase that mediates hydroxylation of proline residues in target proteins, such as ATF4, IKBKB, CEP192 and HIF1A (PubMed:11595184, PubMed:12039559, PubMed:15925519, PubMed:16509823, PubMed:17114296, PubMed:23932902).
- **EPOR** (196): Receptor for erythropoietin, which mediates erythropoietin-induced erythroblast proliferation and differentiation (PubMed:10388848, PubMed:2163695, PubMed:2163696, PubMed:8662939, PubMed:9774108).
- **FTO** (289): RNA demethylase that mediates oxidative demethylation of different RNA species, such as mRNAs, tRNAs and snRNAs, and acts as a regulator of fat mass, adipogenesis and energy homeostasis (PubMed:22002720, PubMed:25452335, PubMed:26457839, PubMed:26458103, PubMed:28002401, PubMed:30197295).
- **CASR** (457): G protein-coupled receptor that senses changes in the extracellular concentration of calcium ions and plays a key role in maintaining calcium homeostasis (PubMed:17555508, PubMed:19789209, PubMed:21566075, PubMed:22114145, PubMed:22789683, PubMed:23966241, PubMed:25104082, PubMed:25292184, PubMed:25766501, PubMed:26386835, PubMed:32817431, PubMed:33603117, PubMed:34194040, PubMed:34467854, PubMed:7759551, PubMed:8636323, PubMed:8702647, PubMed:8878438).
- **EGLN3** (248): Prolyl hydroxylase that mediates hydroxylation of proline residues in target proteins, such as PKM, TELO2, ATF4, GPX4 and HIF1A (PubMed:19584355, PubMed:20978507, PubMed:21483450, PubMed:21575608, PubMed:21620138, PubMed:22797300, PubMed:40281343).
- **GHR** (144): Receptor for pituitary gland growth hormone (GH1) involved in regulating postnatal body growth (PubMed:1549776, PubMed:2825030, PubMed:8943276).
- **LIPC** (385): Catalyzes the hydrolysis of triglycerides and phospholipids present in circulating plasma lipoproteins, including chylomicrons, intermediate density lipoproteins (IDL), low density lipoproteins (LDL) of large size and high density lipoproteins (HDL), releasing free fatty acids (FFA) and smaller lipoprotein particles (PubMed:12032167, PubMed:26193433, PubMed:7592706, PubMed:8798474).
- **WDR72** (83): Plays a major role in formation of tooth enamel (PubMed:19853237, PubMed:25008349).
- **TSHR** (101): Receptor for the thyroid-stimulating hormone (TSH) or thyrotropin (PubMed:11847099, PubMed:12045258).
- **SLC26A4** (140): Sodium-independent transporter of chloride and iodide (PubMed:10192399, PubMed:11932316, PubMed:12107249, PubMed:16684826, PubMed:24051746).
- **TG** (145): Acts as a substrate for the production of iodinated thyroid hormones thyroxine (T4) and triiodothyronine (T3) (PubMed:17532758, PubMed:32025030).
- **SLC5A5** (220): Sodium:iodide symporter that mediates the transport of iodide into the thyroid gland (PubMed:12488351, PubMed:18372236, PubMed:18708479, PubMed:20797386, PubMed:31310151, PubMed:32084174, PubMed:8806637, PubMed:9329364).
- **DUOX2** (131): Generates hydrogen peroxide which is required for the activity of thyroid peroxidase/TPO and lactoperoxidase/LPO (PubMed:15972824).
- **SECISBP2** (234): mRNA-binding protein that binds to the SECIS (selenocysteine insertion sequence) element present in the 3'-UTR of mRNAs encoding selenoproteins and facilitates the incorporation of the rare amino acid selenocysteine (PubMed:35709277).
- **DUOXA2** (134): Required for the maturation and transport of functional DUOX2 from the endoplasmic reticulum to the plasma membrane (PubMed:16651268).
- **IYD** (208): Catalyzes the dehalogenation of halotyrosines such as 3-bromo-L-tyrosine, 3-chloro-L-tyrosine, 3-iodo-L-tyrosine and 3,5-diiodo-L-tyrosine (PubMed:15289438, PubMed:18434651, PubMed:25395621, PubMed:28157283).
- **ADCY7** (149): Adenylate cyclase that mediates formation of both cyclic AMP (cAMP) and cyclic di-AMP (c-di-AMP) (PubMed:11113152, PubMed:18541530, PubMed:23229509).
- **DRD2** (307): G protein-coupled receptor for dopamine, a catecholamine neurotransmitter hormone that functions as the brain's 'reward chemical', driving motivation, reinforcement learning and pleasure (PubMed:21645528, PubMed:32103023, PubMed:32528175, PubMed:33353947, PubMed:33571431, PubMed:37221270, PubMed:39103320).
- **HTR2A** (182): G protein-coupled receptor for 5-hydroxytryptamine (serotonin) (PubMed:1330647, PubMed:18703043, PubMed:19057895, PubMed:21645528, PubMed:22300836, PubMed:35084960, PubMed:38552625).
- **HTR1A** (180): G protein-coupled receptor for 5-hydroxytryptamine (serotonin) (PubMed:22957663, PubMed:3138543, PubMed:33762731, PubMed:37935376, PubMed:37935377, PubMed:8138923, PubMed:8393041).
- **SLC6A3** (214): Mediates sodium- and chloride-dependent transport of dopamine (PubMed:10375632, PubMed:11093780, PubMed:1406597, PubMed:15505207, PubMed:19478460, PubMed:39112701, PubMed:39112703, PubMed:39112705, PubMed:8302271).
- **MAOA** (361): Catalyzes the oxidative deamination of primary and some secondary amine such as neurotransmitters, with concomitant reduction of oxygen to hydrogen peroxide and has important functions in the metabolism of neuroactive and vasoactive amines in the central nervous system and peripheral tissues (PubMed:18391214, PubMed:20493079, PubMed:24169519, PubMed:8316221).
- **GABRB1** (209): Beta subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:10449790, PubMed:16412217, PubMed:26950270).
- **GABRA6** (175): Alpha subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:8632757).
- **DRD3** (289): G protein-coupled receptor for dopamine, a catecholamine neurotransmitter hormone that functions as the brain's 'reward chemical', driving motivation, reinforcement learning and pleasure (PubMed:19520868, PubMed:33548201, PubMed:37221270, PubMed:39237617, PubMed:39984436, PubMed:8301582).
- **GRIN2B** (346): Component of N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function as heterotetrameric, ligand-gated cation channels with high calcium permeability and voltage-dependent block by Mg(2+) (PubMed:24272827, PubMed:24863970, PubMed:26875626, PubMed:26919761, PubMed:27839871, PubMed:28095420, PubMed:28126851, PubMed:38538865, PubMed:8768735).
- **DRD4** (336): G protein-coupled receptor for dopamine, a catecholamine neurotransmitter hormone that functions as the brain's 'reward chemical', driving motivation, reinforcement learning and pleasure (PubMed:16423344, PubMed:1840645, PubMed:27659709, PubMed:29051383, PubMed:37221270, PubMed:7512953, PubMed:7643093, PubMed:8078498, PubMed:8413587).
- **GRIN1** (344): Component of N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function as heterotetrameric, ligand-gated cation channels with high calcium permeability and voltage-dependent block by Mg(2+) (PubMed:21376300, PubMed:26875626, PubMed:26919761, PubMed:28126851, PubMed:28228639, PubMed:36959261, PubMed:7679115, PubMed:7681588, PubMed:7685113).
- **GABRA2** (210): Alpha subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:10449790, PubMed:29961870, PubMed:31032849).
- **HTR2C** (148): G protein-coupled receptor for 5-hydroxytryptamine (serotonin) (PubMed:12970106, PubMed:18703043, PubMed:19057895, PubMed:29398112, PubMed:7895773).
- **GABRA5** (227): Alpha subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:14993607, PubMed:29961870, PubMed:30140029, PubMed:31056671).
- **RTN4R** (168): Receptor for RTN4, OMG and MAG (PubMed:12037567, PubMed:12068310, PubMed:12089450, PubMed:12426574, PubMed:12839991, PubMed:16712417, PubMed:18411262, PubMed:19052207).
- **MTHFR** (165): Catalyzes the conversion of 5,10-methylenetetrahydrofolate to 5-methyltetrahydrofolate, a cosubstrate for homocysteine remethylation to methionine (PubMed:29891918).
- **HTR4** (213): G protein-coupled receptor for 5-hydroxytryptamine (serotonin), a biogenic hormone that functions as a neurotransmitter, a hormone and a mitogen (PubMed:10821780, PubMed:16102731, PubMed:35714614, PubMed:9603189).
- **HTR1B** (260): G protein-coupled receptor for 5-hydroxytryptamine (serotonin) (PubMed:10452531, PubMed:1315531, PubMed:1328844, PubMed:1348246, PubMed:1351684, PubMed:1559993, PubMed:1565658, PubMed:1610347, PubMed:23519210, PubMed:23519215, PubMed:29925951, PubMed:8218242).
- **HTR5A** (196): G protein-coupled receptor for 5-hydroxytryptamine (serotonin), a biogenic hormone that functions as a neurotransmitter, a hormone and a mitogen (PubMed:35610220, PubMed:35835867, PubMed:9865521).
- **HTR6** (213): G protein-coupled receptor for 5-hydroxytryptamine (serotonin), a biogenic hormone that functions as a neurotransmitter, a hormone and a mitogen (PubMed:35714614, PubMed:36989299, PubMed:37327704, PubMed:8522988).
- **HTR7** (179): G protein-coupled receptor for 5-hydroxytryptamine (serotonin), a biogenic hormone that functions as a neurotransmitter, a hormone and a mitogen (PubMed:35714614, PubMed:8226867).
- **SETD1A** (217): Histone methyltransferase that catalyzes methyl group transfer from S-adenosyl-L-methionine to the epsilon-amino group of 'Lys-4' of histone H3 (H3K4) via a non-processive mechanism (PubMed:12670868, PubMed:25561738).
- **HTR2B** (162): G protein-coupled receptor for 5-hydroxytryptamine (serotonin) (PubMed:18703043, PubMed:23519210, PubMed:7926008, PubMed:8078486, PubMed:8143856, PubMed:8882600).
- **HTR1F** (130): G protein-coupled receptor for 5-hydroxytryptamine (serotonin) (PubMed:21422162, PubMed:34239069, PubMed:8380639, PubMed:8384716).
- **HTR1D** (130): G protein-coupled receptor for 5-hydroxytryptamine (serotonin) (PubMed:10452531, PubMed:1565658, PubMed:1652050, PubMed:33762731).
- **GSK3B** (471): Constitutively active protein kinase that acts as a negative regulator in the hormonal control of glucose homeostasis, Wnt signaling and regulation of transcription factors and microtubules, by phosphorylating and inactivating glycogen synthase (GYS1 or GYS2), EIF2B, CTNNB1/beta-catenin, APC, AXIN1, DPYSL2/CRMP2, JUN, NFATC1/NFATC, MAPT/TAU and MACF1 (PubMed:11430833, PubMed:12554650, PubMed:14690523, PubMed:16484495, PubMed:1846781, PubMed:20937854, PubMed:9072970).
- **SCN9A** (194): Pore-forming subunit of Nav1.7, a voltage-gated sodium (Nav) channel that directly mediates the depolarizing phase of action potentials in excitable membranes (PubMed:38381792, PubMed:40768348).
- **IMPA1** (152): Phosphatase involved in the dephosphorylation of myo-inositol monophosphates to generate myo-inositol (PubMed:17068342, PubMed:8718889, PubMed:9462881).
- **GSK3A** (348): Constitutively active protein kinase that acts as a negative regulator in the hormonal control of glucose homeostasis, Wnt signaling and regulation of transcription factors and microtubules, by phosphorylating and inactivating glycogen synthase (GYS1 or GYS2), CTNNB1/beta-catenin, APC and AXIN1 (PubMed:11749387, PubMed:17478001, PubMed:19366350).
- **ANK3** (123): Required for the organization of specialized membrane domains by linking the membrane to the cytoskeleton (PubMed:7836469).
- **LRRK2** (464): Serine/threonine-protein kinase which phosphorylates a broad range of proteins involved in multiple processes such as neuronal plasticity, innate immunity, autophagy, and vesicle trafficking (PubMed:17114044, PubMed:20949042, PubMed:21850687, PubMed:22012985, PubMed:23395371, PubMed:24687852, PubMed:25201882, PubMed:26014385, PubMed:26824392, PubMed:27830463, PubMed:28720718, PubMed:29125462, PubMed:29127255, PubMed:29212815, PubMed:30398148, PubMed:30635421).
- **ATP13A2** (102): ATPase which acts as a lysosomal polyamine exporter with high affinity for spermine (PubMed:31996848).
- **SNCA** (223): Neuronal protein that plays several roles in synaptic activity such as regulation of synaptic vesicle trafficking and subsequent neurotransmitter release (PubMed:20798282, PubMed:26442590, PubMed:28288128, PubMed:30404828).
- **PRKN** (415): Functions within a multiprotein E3 ubiquitin ligase complex, catalyzing the covalent attachment of ubiquitin moieties onto substrate proteins (PubMed:10888878, PubMed:10973942, PubMed:11431533, PubMed:12150907, PubMed:12628165, PubMed:15105460, PubMed:16135753, PubMed:21376232, PubMed:21532592, PubMed:22396657, PubMed:23620051, PubMed:23754282, PubMed:24660806, PubMed:24751536, PubMed:29311685, PubMed:32047033).
- **PINK1** (167): Serine/threonine-protein kinase which acts as a sensor of mitochondrial damage and protects against mitochondrial dysfunction during cellular stress (PubMed:40080546).
- **PARK7** (365): Multifunctional protein with controversial molecular function which plays an important role in cell protection against oxidative stress and cell death acting as oxidative stress sensor and redox-sensitive chaperone and protease (PubMed:12796482, PubMed:17015834, PubMed:18711745, PubMed:19229105, PubMed:20304780, PubMed:25416785, PubMed:26995087, PubMed:28993701).
- **FBXO7** (358): Substrate recognition component of a SCF (SKP1-CUL1-F-box protein) E3 ubiquitin-protein ligase complex which mediates the ubiquitination and subsequent proteasomal degradation of target proteins and plays a role in several biological processes such as cell cycle, cell proliferation, or maintenance of chromosome stability (PubMed:15145941, PubMed:34791250).
- **GBA1** (317): Glucosylceramidase that catalyzes, within the lysosomal compartment, the hydrolysis of glucosylceramides/GlcCers (such as beta-D-glucosyl-(1<->1')-N-acylsphing-4-enine) into free ceramides (such as N-acylsphing-4-enine) and glucose (PubMed:15916907, PubMed:24211208, PubMed:32144204, PubMed:39395789, PubMed:9201993).
- **MAPT** (143): Promotes microtubule assembly and stability, and might be involved in the establishment and maintenance of neuronal polarity (PubMed:21985311).
- **DRD1** (324): G protein-coupled receptor for dopamine, a catecholamine neurotransmitter hormone that functions as the brain's 'reward chemical', driving motivation, reinforcement learning and pleasure (PubMed:11500503, PubMed:33571431, PubMed:33571432, PubMed:33750903, PubMed:34083522, PubMed:35676276, PubMed:35687690, PubMed:37221270).
- **MAOB** (482): Catalyzes the oxidative deamination of primary and some secondary amines such as neurotransmitters, and exogenous amines including the tertiary amine, neurotoxin 1-methyl-4-phenyl-1,2,3,6-tetrahydropyridine (MPTP), with concomitant reduction of oxygen to hydrogen peroxide and participates in the metabolism of neuroactive and vasoactive amines in the central nervous system and peripheral tissues (PubMed:11049757, PubMed:11134050, PubMed:20493079, PubMed:8316221, PubMed:8665924).
- **PSEN1** (450): Catalytic subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:10206644, PubMed:10545183, PubMed:10593990, PubMed:10811883, PubMed:10899933, PubMed:12679784, PubMed:12740439, PubMed:15274632, PubMed:20460383, PubMed:25043039, PubMed:26280335, PubMed:28269784, PubMed:30598546, PubMed:30630874).
- **PSEN2** (297): Catalytic subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:10497236, PubMed:10652302, PubMed:16752394, PubMed:27293189, PubMed:36272978).
- **APOE** (237): APOE is an apolipoprotein, a protein associating with lipid particles, that mainly functions in lipoprotein-mediated lipid transport between organs via the plasma and interstitial fluids (PubMed:14754908, PubMed:1911868, PubMed:6860692).
- **ABCA7** (175): Catalyzes the translocation of specific phospholipids from the cytoplasmic to the extracellular/lumenal leaflet of membrane coupled to the hydrolysis of ATP (PubMed:24097981).
- **ADAM10** (368): Transmembrane metalloprotease which mediates the ectodomain shedding of a myriad of transmembrane proteins, including adhesion proteins, growth factor precursors and cytokines being essential for development and tissue homeostasis (PubMed:11786905, PubMed:12475894, PubMed:20592283, PubMed:24990881, PubMed:26686862, PubMed:28600292, PubMed:31792032, PubMed:31792032).
- **GRN** (240): Secreted protein that acts as a key regulator of lysosomal function and as a growth factor involved in inflammation, wound healing and cell proliferation (PubMed:12526812, PubMed:18378771, PubMed:28073925, PubMed:28453791, PubMed:28541286).
- **CD33** (213): Sialic-acid-binding immunoglobulin-like lectin (Siglec) that plays a role in mediating cell-cell interactions and in maintaining immune cells in a resting state (PubMed:10611343, PubMed:11320212, PubMed:15597323).
- **GRIN2C** (228): Component of N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function as heterotetrameric, ligand-gated cation channels with high calcium permeability and voltage-dependent block by Mg(2+) (PubMed:26875626, PubMed:36309015).
- **GRIN2D** (261): Component of N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function as heterotetrameric, ligand-gated cation channels with high calcium permeability and voltage-dependent block by Mg(2+) (PubMed:26875626, PubMed:27616483, PubMed:28126851, PubMed:9489750).
- **CYP1B1** (232): A cytochrome P450 monooxygenase involved in the metabolism of various endogenous substrates, including fatty acids, steroid hormones and vitamins (PubMed:10681376, PubMed:11555828, PubMed:12865317, PubMed:15258110, PubMed:20972997).
- **OPTN** (171): Plays an important role in the maintenance of the Golgi complex, in membrane trafficking, in exocytosis, through its interaction with myosin VI and Rab8 (PubMed:27534431).
- **TMCO1** (173): Endoplasmic reticulum (ER) calcium-selective channel preventing intracellular Ca2(+) stores from overfilling and maintaining calcium homeostasis in the ER (PubMed:27212239).
- **CA2** (890): Catalyzes the reversible hydration of carbon dioxide (PubMed:11327835, PubMed:11802772, PubMed:11831900, PubMed:12056894, PubMed:12171926, PubMed:1336460, PubMed:14736236, PubMed:15300855, PubMed:15453828, PubMed:15667203, PubMed:15865431, PubMed:16106378, PubMed:16214338, PubMed:16290146, PubMed:16686544, PubMed:16759856, PubMed:16807956, PubMed:17127057, PubMed:17251017, PubMed:17314045, PubMed:17330962, PubMed:17346964, PubMed:17540563, PubMed:17588751, PubMed:17705204, PubMed:18024029, PubMed:18162396, PubMed:18266323, PubMed:18374572, PubMed:18481843, PubMed:18640037, PubMed:18942852, PubMed:1909891, PubMed:1910042, PubMed:19170619, PubMed:19186056, PubMed:19206230, PubMed:19520834, PubMed:19778001, PubMed:7761440, PubMed:7901850, PubMed:8218160, PubMed:8262987, PubMed:8399159, PubMed:8451242, PubMed:8485129, PubMed:8639494, PubMed:9265618, PubMed:9398308, PubMed:4994926).
- **ROCK1** (236): Protein kinase which is a key regulator of the actin cytoskeleton and cell polarity (PubMed:10436159, PubMed:10652353, PubMed:11018042, PubMed:11283607, PubMed:17158456, PubMed:18573880, PubMed:19131646, PubMed:8617235, PubMed:9722579).
- **LMX1B** (111): Transcription factor involved in the regulation of podocyte-expressed genes (PubMed:24042019, PubMed:28059119).
- **CA1** (223): Catalyzes the reversible hydration of carbon dioxide (PubMed:10550681, PubMed:16506782, PubMed:16686544, PubMed:16807956, PubMed:17127057, PubMed:17314045, PubMed:17407288, PubMed:19186056, PubMed:19206230, PubMed:4994926).
- **CA4** (340): Catalyzes the reversible hydration of carbon dioxide into bicarbonate and protons and thus is essential to maintaining intracellular and extracellular pH (PubMed:15563508, PubMed:16686544, PubMed:16807956, PubMed:17127057, PubMed:17314045, PubMed:17652713, PubMed:17705204, PubMed:19186056, PubMed:19206230, PubMed:7625839, PubMed:9054574).
- **ADRA2C** (253): Alpha-2 adrenergic receptors are G protein-coupled receptors for catecholamines that activate the G(i/o) protein pathway, thereby promoting adenylyl cyclase inhibition, ERK1/2 stimulation, and voltage-gated calcium channels suppression (PubMed:2842764).
- **ADRA2B** (316): Alpha-2 adrenergic receptors are G protein-coupled receptors for catecholamines that activate G(i/o) protein pathway, thereby promoting adenylyl cyclase inhibition, ERK1/2 stimulation, and voltage-gated calcium channels suppression (PubMed:11056163, PubMed:2164221, PubMed:2172775, PubMed:23105096, PubMed:26811329).
- **IL1A** (208): Cytokine constitutively present intracellularly in nearly all resting non-hematopoietic cells that plays an important role in inflammation and bridges the innate and adaptive immune systems (PubMed:26439902).
- **KPNA1** (135): Functions in nuclear protein import as an adapter protein for nuclear receptor KPNB1 (PubMed:27713473, PubMed:7892216, PubMed:8692858).
- **KPNB1** (376): Functions in nuclear protein import, either in association with an adapter protein, like an importin-alpha subunit, which binds to nuclear localization signals (NLS) in cargo substrates, or by acting as autonomous nuclear transport receptor (PubMed:10228156, PubMed:11682607, PubMed:11891849, PubMed:19386897, PubMed:20818336, PubMed:24699649, PubMed:7615630, PubMed:9687515).
- **MAPK3** (125): Serine/threonine kinase which acts as an essential component of the MAP kinase signal transduction pathway (PubMed:34497368).
- **CTSG** (98): Serine protease with trypsin- and chymotrypsin-like specificity (PubMed:29652924, PubMed:8194606).
- **TRIM27** (276): E3 ubiquitin-protein ligase that mediates ubiquitination of various substrates and thereby plays a role in diffent processes including proliferation, innate immunity, apoptosis, immune response or autophagy (PubMed:22829933, PubMed:24144979, PubMed:29688809, PubMed:36111389).
- **RNF213** (323): Atypical E3 ubiquitin ligase that can catalyze ubiquitination of both proteins and lipids, and which is involved in various processes, such as lipid metabolism, angiogenesis and cell-autonomous immunity (PubMed:21799892, PubMed:26126547, PubMed:26278786, PubMed:26766444, PubMed:30705059, PubMed:32139119, PubMed:34012115).
- **ENO1** (175): Enolase that catalyzes the conversion of 2-phosphoglycerate to phosphoenolpyruvate in glycolysis and the reverse reaction in gluconeogenesis (PubMed:1369209, PubMed:29775581).
- **PGK1** (187): Catalyzes one of the two ATP producing reactions in the glycolytic pathway via the reversible conversion of 1,3-diphosphoglycerate to 3-phosphoglycerate (PubMed:30323285, PubMed:7391028).
- **ATP6V1H** (222): Subunit of the V1 complex of vacuolar(H+)-ATPase (V-ATPase), a multisubunit enzyme composed of a peripheral complex (V1) that hydrolyzes ATP and a membrane integral complex (V0) that translocates protons (PubMed:33065002).
- **GYPA** (141): Component of the ankyrin-1 complex, a multiprotein complex involved in the stability and shape of the erythrocyte membrane (PubMed:35835865).
- **GABRQ** (193): Theta subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:10449790, PubMed:16412217).
- **GABRP** (123): Pi subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA) (PubMed:10462548).
- **GABRA3** (193): Alpha subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:16412217, PubMed:29053855).
- **GABRG1** (176): Gamma subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:10449790).
- **GABRE** (194): Epsilon subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:16412217, PubMed:9882711).
- **GABRA4** (176): Alpha subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (PubMed:35355020).
- **BRCA2** (420): Tumor suppressor protein that maintains genome stability primarily by repairing damaged DNA through homologous recombination (HR) (PubMed:11239456, PubMed:12442171, PubMed:15115758, PubMed:15199141, PubMed:15671039, PubMed:15937124, PubMed:17515903, PubMed:17515904, PubMed:18317453, PubMed:19303847, PubMed:20729832, PubMed:20729858, PubMed:20729859, PubMed:21719596, PubMed:27941124, PubMed:37499663, PubMed:37515771).
- **BRCA1** (316): E3 ubiquitin-protein ligase that specifically mediates the formation of 'Lys-6'-linked polyubiquitin chains and plays a central role in DNA repair by facilitating cellular responses to DNA damage (PubMed:10500182, PubMed:12887909, PubMed:12890688, PubMed:14976165, PubMed:16818604, PubMed:17525340, PubMed:19261748).
- **PALB2** (227): Plays a critical role in homologous recombination repair (HRR) through its ability to recruit BRCA2 and RAD51 to DNA breaks (PubMed:16793542, PubMed:19369211, PubMed:19423707, PubMed:22941656, PubMed:24141787, PubMed:28319063).
- **PIK3CA** (227): Phosphoinositide-3-kinase (PI3K) phosphorylates phosphatidylinositol (PI) and its phosphorylated derivatives at position 3 of the inositol ring to produce 3-phosphoinositides (PubMed:15135396, PubMed:23936502, PubMed:28676499).
- **ATM** (490): Serine/threonine protein kinase which activates checkpoint signaling upon double strand breaks (DSBs), apoptosis and genotoxic stresses such as ionizing ultraviolet A light (UVA), thereby acting as a DNA damage sensor (PubMed:10550055, PubMed:10839545, PubMed:10910365, PubMed:12556884, PubMed:14871926, PubMed:15064416, PubMed:15448695, PubMed:15456891, PubMed:15790808, PubMed:15916964, PubMed:17923702, PubMed:21757780, PubMed:24534091, PubMed:27941124, PubMed:35076389, PubMed:9733514).
- **TP53** (422): Multifunctional transcription factor that induces cell cycle arrest, DNA repair or apoptosis upon binding to its target DNA sequence (PubMed:11025664, PubMed:12524540, PubMed:12810724, PubMed:15186775, PubMed:15340061, PubMed:17317671, PubMed:17349958, PubMed:19556538, PubMed:20673990, PubMed:20959462, PubMed:22726440, PubMed:24051492, PubMed:24652652, PubMed:35618207, PubMed:36634798, PubMed:38653238, PubMed:9840937).
- **AKT1** (324): AKT1 is one of 3 closely related serine/threonine-protein kinases (AKT1, AKT2 and AKT3) called the AKT kinase, and which regulate many processes including metabolism, proliferation, cell survival, growth and angiogenesis (PubMed:11882383, PubMed:15526160, PubMed:15861136, PubMed:21432781, PubMed:21620960, PubMed:31204173).
- **BRIP1** (201): DNA-dependent ATPase and 5'-3' DNA helicase required for the maintenance of chromosomal stability (PubMed:11301010, PubMed:14983014, PubMed:16116421, PubMed:16153896, PubMed:17596542, PubMed:36608669).
- **CDH1** (73): Cadherins are calcium-dependent cell adhesion proteins (PubMed:11976333).
- **PTEN** (162): Dual-specificity protein phosphatase, dephosphorylating tyrosine-, serine- and threonine-phosphorylated proteins (PubMed:9187108, PubMed:9256433, PubMed:9616126).
- **MAP3K1** (75): Component of a protein kinase signal transduction cascade (PubMed:9808624).
- **EGFR** (387): Receptor tyrosine kinase binding ligands of the EGF family and activating several signaling cascades to convert extracellular cues into appropriate cellular responses (PubMed:10805725, PubMed:12297050, PubMed:12620237, PubMed:12873986, PubMed:15374980, PubMed:15590694, PubMed:17115032, PubMed:19560417, PubMed:21258366, PubMed:27153536, PubMed:2790960, PubMed:35538033, PubMed:9488479).
- **TBX3** (80): Transcriptional repressor involved in developmental processes (PubMed:10468588).
- **CCND1** (306): Regulatory component of the cyclin D1-CDK4 (DC) complex that phosphorylates and inhibits members of the retinoblastoma (RB) protein family including RB1 and regulates the cell-cycle during G(1)/S transition (PubMed:1827756, PubMed:1833066, PubMed:19412162, PubMed:33854235, PubMed:8114739, PubMed:8302605).
- **TMPRSS2** (144): Plasma membrane-anchored serine protease that cleaves at arginine residues (PubMed:32703818, PubMed:35676539, PubMed:37990007, PubMed:38964328).
- **CYP17A1** (148): A cytochrome P450 monooxygenase involved in corticoid and androgen biosynthesis (PubMed:22266943, PubMed:25301938, PubMed:27339894, PubMed:9452426).
- **KMT2C** (169): Histone methyltransferase that catalyzes methyl group transfer from S-adenosyl-L-methionine to the epsilon-amino group of 'Lys-4' of histone H3 (H3K4) (PubMed:25561738).
- **ACP3** (292): A non-specific tyrosine phosphatase that dephosphorylates a diverse number of substrates under acidic conditions (pH 4-6) including alkyl, aryl, and acyl orthophosphate monoesters and phosphorylated proteins (PubMed:10506173, PubMed:15280042, PubMed:20498373, PubMed:9584846, PubMed:8132635).
- **KMT2D** (169): Histone methyltransferase that catalyzes methyl group transfer from S-adenosyl-L-methionine to the epsilon-amino group of 'Lys-4' of histone H3 (H3K4) (PubMed:25561738).
- **PMS2** (102): Component of the post-replicative DNA mismatch repair system (MMR) (PubMed:30653781, PubMed:35189042).
- **KRAS** (134): Signal transducer in the Ras-MAPK signaling pathway that regulates cell proliferation and survival (PubMed:22711838, PubMed:23698361).
- **FBXO11** (397): Substrate recognition component of a SCF (SKP1-CUL1-F-box protein) E3 ubiquitin-protein ligase complex which mediates the ubiquitination and subsequent proteasomal degradation of target proteins, such as DTL/CDT2, BCL6, SNAI1 and PRDM1/BLIMP1 (PubMed:17098746, PubMed:22113614, PubMed:23478441, PubMed:23478445, PubMed:23892434, PubMed:24613396, PubMed:24968003, PubMed:25827072, PubMed:29059170).
- **POLE** (76): Catalytic component of the DNA polymerase epsilon complex (PubMed:10801849).
- **FBXW7** (298): Substrate recognition component of a SCF (SKP1-CUL1-F-box protein) E3 ubiquitin-protein ligase complex which mediates the ubiquitination and subsequent proteasomal degradation of target proteins (PubMed:17434132, PubMed:22748924, PubMed:26976582, PubMed:28727686, PubMed:34741373, PubMed:35395208).
- **POLD1** (343): As the catalytic component of the trimeric (Pol-delta3 complex) and tetrameric DNA polymerase delta complexes (Pol-delta4 complex), plays a crucial role in high fidelity genome replication, including in lagging strand synthesis, and repair (PubMed:16510448, PubMed:19074196, PubMed:20334433, PubMed:24022480, PubMed:24035200, PubMed:31449058).
- **ALK** (351): Neuronal receptor tyrosine kinase that is essentially and transiently expressed in specific regions of the central and peripheral nervous systems and plays an important role in the genesis and differentiation of the nervous system (PubMed:11121404, PubMed:11387242, PubMed:16317043, PubMed:17274988, PubMed:30061385, PubMed:34646012, PubMed:34819673).
- **RB1** (100): Tumor suppressor that is a key regulator of the G1/S transition of the cell cycle (PubMed:10499802).
- **RET** (432): Receptor tyrosine-protein kinase involved in numerous cellular mechanisms including cell proliferation, neuronal navigation, cell migration, and cell differentiation in response to glia cell line-derived growth family factors (GDNF, NRTN, ARTN, PSPN and GDF15) (PubMed:20064382, PubMed:20616503, PubMed:20702524, PubMed:21357690, PubMed:21454698, PubMed:24560924, PubMed:28846097, PubMed:28846099, PubMed:28953886, PubMed:31118272).
- **EML4** (99): Essential for the formation and stability of microtubules (MTs) (PubMed:16890222, PubMed:31409757).
- **STK11** (335): Tumor suppressor serine/threonine-protein kinase that controls the activity of AMP-activated protein kinase (AMPK) family members, thereby playing a role in various processes such as cell metabolism, cell polarity, apoptosis and DNA damage response (PubMed:12805220, PubMed:14517248, PubMed:14976552, PubMed:15016379, PubMed:15733851).
- **CCDC6** (178): Acts as a structural scaffold that organizes free PP2Ac into a configuration that FBXO42 can recognize and ubiquitinate, leading to its proteasomal degradation (PubMed:41986709).
- **BAP1** (200): Deubiquitinating enzyme that plays a key role in chromatin by mediating deubiquitination of histone H2A and HCFC1 (PubMed:12485996, PubMed:18757409, PubMed:20436459, PubMed:25451922, PubMed:35051358).
- **NRAS** (117): Signal transducer in the Ras-MAPK signaling pathway that regulates cell proliferation and survival (PubMed:30712867).
- **MITF** (197): Transcription factor that acts as a master regulator of melanocyte survival and differentiation as well as melanosome biogenesis (PubMed:10587587, PubMed:22647378, PubMed:27889061, PubMed:9647758).
- **GNAQ** (206): Guanine nucleotide-binding proteins (G proteins) function as transducers downstream of G protein-coupled receptors (GPCRs) in numerous signaling cascades (PubMed:34556863, PubMed:35672283, PubMed:37991948).
- **GNA11** (172): Guanine nucleotide-binding proteins (G proteins) function as transducers downstream of G protein-coupled receptors (GPCRs) in numerous signaling cascades (PubMed:31073061).
- **SF3B1** (226): Component of the 17S U2 SnRNP complex of the spliceosome, a large ribonucleoprotein complex that removes introns from transcribed pre-mRNAs (PubMed:12234937, PubMed:27720643, PubMed:32494006, PubMed:34822310, PubMed:36104565).
- **PPP6C** (101): Catalytic subunit of protein phosphatase 6 (PP6) (PubMed:17079228, PubMed:29053956, PubMed:32474700).
- **FYN** (370): Non-receptor tyrosine-protein kinase that plays a role in many biological processes including regulation of cell growth and survival, cell adhesion, integrin-mediated signaling, cytoskeletal remodeling, cell motility, immune response and axon guidance (PubMed:11536198, PubMed:15489916, PubMed:15557120, PubMed:16387660, PubMed:20100835, PubMed:7568038, PubMed:7822789).
- **SRC** (313): Non-receptor protein tyrosine kinase which is activated following engagement of many different classes of cellular receptors including immune response receptors, integrins and other adhesion receptors, receptor protein tyrosine kinases, G protein-coupled receptors as well as cytokine receptors (PubMed:34234773).
- **LCK** (189): Non-receptor tyrosine-protein kinase that plays an essential role in the selection and maturation of developing T-cells in the thymus and in the function of mature T-cells (PubMed:2470098).
- **SRMS** (102): Non-receptor tyrosine-protein kinase which phosphorylates DOK1 on tyrosine residues (PubMed:23822091).
- **GRB2** (254): Non-enzymatic adapter protein that plays a pivotal role in precisely regulated signaling cascades from cell surface receptors to cellular responses, including signaling transduction and gene expression (PubMed:11016927, PubMed:11726515, PubMed:37626338).
- **IFNAR2** (323): Together with IFNAR1, forms the heterodimeric receptor for type I interferons (including interferons alpha, beta, epsilon, omega and kappa) (PubMed:10049744, PubMed:10556041, PubMed:21854986, PubMed:26424569, PubMed:28165510, PubMed:32972995, PubMed:7665574, PubMed:7759950, PubMed:8181059, PubMed:8798579, PubMed:8969169).
- **IFNAR1** (309): Together with IFNAR2, forms the heterodimeric receptor for type I interferons (including interferons alpha, beta, epsilon, omega and kappa) (PubMed:10049744, PubMed:14532120, PubMed:15337770, PubMed:2153461, PubMed:21854986, PubMed:24075985, PubMed:31270247, PubMed:33252644, PubMed:35442418, PubMed:7813427).
- **DNMT3A** (183): Required for genome-wide de novo methylation and is essential for the establishment of DNA methylation patterns during development (PubMed:12138111, PubMed:16357870, PubMed:30478443).
- **IDH1** (238): Catalyzes the NADP(+)-dependent oxidative decarboxylation of isocitrate (D-threo-isocitrate) to 2-ketoglutarate (2-oxoglutarate), which is required by other enzymes such as the phytanoyl-CoA dioxygenase (PubMed:10521434, PubMed:19935646).
- **ASXL1** (247): Probable Polycomb group (PcG) protein involved in transcriptional regulation mediated by ligand-bound nuclear hormone receptors, such as retinoic acid receptors (RARs) and peroxisome proliferator-activated receptor gamma (PPARG) (PubMed:16606617).
- **IDH2** (97): Plays a role in intermediary metabolism and energy production (PubMed:19228619, PubMed:22416140).
- **GATA1** (123): Transcriptional activator or repressor which serves as a general switch factor for erythroid development (PubMed:35030251).
- **PTPN11** (276): Acts downstream of various receptor and cytoplasmic protein tyrosine kinases to participate in the signal transduction from the cell surface to the nucleus (PubMed:10655584, PubMed:14739280, PubMed:18559669, PubMed:18829466, PubMed:26742426, PubMed:28074573, PubMed:32184441).
- **RNF5** (177): Membrane-bound E3 ubiquitin-protein ligase that mediates ubiquitination of target proteins (PubMed:11329381, PubMed:12861019, PubMed:16176924, PubMed:19269966, PubMed:19285439).
- **RNF185** (152): E3 ubiquitin-protein ligase that regulates selective mitochondrial autophagy by mediating 'Lys-63'-linked polyubiquitination of BNIP1 (PubMed:21931693).
- **OS9** (240): Lectin component of the HRD1 complex, which functions in endoplasmic reticulum (ER) quality control and ER-associated degradation (ERAD) (PubMed:18264092, PubMed:18417469, PubMed:19084021, PubMed:19346256, PubMed:21172656, PubMed:24899641).
- **DERL1** (142): Functional component of endoplasmic reticulum-associated degradation (ERAD) for misfolded lumenal proteins (PubMed:15215856, PubMed:33658201).
- **ERLIN2** (209): Component of the ERLIN1/ERLIN2 complex which mediates the endoplasmic reticulum-associated degradation (ERAD) of inositol 1,4,5-trisphosphate receptors (IP3Rs) such as ITPR1 (PubMed:17502376, PubMed:19240031).
- **SEL1L** (274): Plays a role in the endoplasmic reticulum quality control (ERQC) system also called ER-associated degradation (ERAD) involved in ubiquitin-dependent degradation of misfolded endoplasmic reticulum proteins (PubMed:16186509, PubMed:29997207, PubMed:37943610, PubMed:37943617).
- **SLC26A9** (141): Ion transporter that can act both as an ion channel and anion exchanger (PubMed:15800055, PubMed:17673510, PubMed:26801567, PubMed:32818062).
- **SLC11A1** (261): Antiporter that transports metal ions against a proton gradient, and which promotes host resistance to infection against intracellular parasites, such as M.bovis, S.typhimurium and L.donovani (PubMed:11237855, PubMed:16103355, PubMed:16395392, PubMed:39824808).
- **IFNGR1** (210): Receptor subunit for interferon gamma/INFG that plays crucial roles in antimicrobial, antiviral, and antitumor responses by activating effector immune cells and enhancing antigen presentation (PubMed:20015550).
- **IFNGR2** (132): Associates with IFNGR1 to form a receptor for the cytokine interferon gamma (IFNG) (PubMed:7615558, PubMed:7673114, PubMed:8124716).
- **HDAC2** (156): Histone deacetylase that catalyzes the deacetylation of lysine residues on the N-terminal part of the core histones (H2A, H2B, H3 and H4) (PubMed:28497810).
- **HDAC8** (224): Histone deacetylase that catalyzes the deacetylation of lysine residues on the N-terminal part of the core histones (H2A, H2B, H3 and H4) (PubMed:10748112, PubMed:10922473, PubMed:10926844, PubMed:14701748, PubMed:28497810).
- **HDAC6** (223): Deacetylates a wide range of non-histone substrates (PubMed:12024216, PubMed:18606987, PubMed:20308065, PubMed:24882211, PubMed:26246421, PubMed:30538141, PubMed:31857589, PubMed:30770470, PubMed:38534334, PubMed:39567688).
- **HDAC5** (126): In vitro, it deacetylates lysine residues on the N-terminal part of the core histones (H2A, H2B, H3 and H4) (PubMed:10220385).
- **HDAC3** (314): Histone deacetylase that catalyzes the deacetylation of lysine residues on the N-terminal part of the core histones (H2A, H2B, H3 and H4), and some other non-histone substrates (PubMed:21030595, PubMed:21444723, PubMed:23911289, PubMed:25301942, PubMed:28167758, PubMed:28497810, PubMed:32404892, PubMed:22230954).
- **HDAC1** (190): Histone deacetylase that catalyzes the deacetylation of lysine residues on the N-terminal part of the core histones (H2A, H2B, H3 and H4) (PubMed:16762839, PubMed:17704056, PubMed:28497810).
- **HDAC10** (150): Polyamine deacetylase (PDAC), which acts preferentially on N(8)-acetylspermidine, and also on acetylcadaverine and acetylputrescine (PubMed:28516954).
- **RPS6** (79): Component of the 40S small ribosomal subunit (PubMed:23636399, PubMed:8706699).
- **RPL3** (110): Component of the large ribosomal subunit (PubMed:12962325, PubMed:23636399, PubMed:32669547, PubMed:35674491).
- **RPL30** (76): Component of the large ribosomal subunit (PubMed:23636399, PubMed:32669547).
- **RPS5** (59): Component of the small ribosomal subunit (PubMed:23636399).
- **RPL13A** (181): Associated with ribosomes but is not required for canonical ribosome function and has extra-ribosomal functions (PubMed:14567916, PubMed:17218275, PubMed:23636399, PubMed:32669547).
- **RPS19** (59): Component of the small ribosomal subunit (PubMed:23636399).
- **SMN1** (233): The SMN complex catalyzes the assembly of small nuclear ribonucleoproteins (snRNPs), the building blocks of the spliceosome, and thereby plays an important role in the splicing of cellular pre-mRNAs (PubMed:18984161, PubMed:9845364).
- **IGHMBP2** (132): 5' to 3' helicase that unwinds both RNA and DNA duplexes in an ATP-dependent reaction (Probable) (PubMed:19158098, PubMed:30218034).
- **SMN2** (233): The SMN complex catalyzes the assembly of small nuclear ribonucleoproteins (snRNPs), the building blocks of the spliceosome, and thereby plays an important role in the splicing of cellular pre-mRNAs (PubMed:18984161, PubMed:9845364).
- **HSPB1** (170): Small heat shock protein which functions as a molecular chaperone probably maintaining denatured proteins in a folding-competent state (PubMed:10383393, PubMed:20178975).
- **BSCL2** (183): Mediates the formation of lipid droplets during the differentiation and maturation of adipocytes (PubMed:19278620, PubMed:21533227, PubMed:27564575, PubMed:30293840, PubMed:31708432).
- **ASAH1** (229): Lysosomal ceramidase that hydrolyzes sphingolipid ceramides into sphingosine and free fatty acids at acidic pH (PubMed:10610716, PubMed:11451951, PubMed:15655246, PubMed:26898341, PubMed:36752535, PubMed:7744740, PubMed:7852294).
- **VRK1** (244): Serine/threonine kinase involved in the regulation of key cellular processes including the cell cycle, nuclear condensation, transcription regulation, and DNA damage response (PubMed:14645249, PubMed:18617507, PubMed:19103756, PubMed:33076429).
- **ATP7A** (156): ATP-driven copper (Cu(+)) ion pump that plays an important role in intracellular copper ion homeostasis (PubMed:10419525, PubMed:11092760, PubMed:28389643).
- **DNAJB2** (187): Functions as a co-chaperone, regulating the substrate binding and activating the ATPase activity of chaperones of the HSP70/heat shock protein 70 family (PubMed:22219199, PubMed:7957263).
- **GARS1** (202): Catalyzes the ATP-dependent ligation of glycine to the 3'-end of its cognate tRNA, via the formation of an aminoacyl-adenylate intermediate (Gly-AMP) (PubMed:17544401, PubMed:24898252, PubMed:28675565).
- **TRPV4** (204): Non-selective calcium permeant cation channel involved in osmotic sensitivity and mechanosensitivity (PubMed:16293632, PubMed:18695040, PubMed:18826956, PubMed:22526352, PubMed:23136043, PubMed:29899501).
- **UBA1** (182): Catalyzes the first step in ubiquitin conjugation to mark cellular proteins for degradation through the ubiquitin-proteasome system (PubMed:1447181, PubMed:1606621, PubMed:33108101).
- **SLC2A3** (84): Facilitative glucose transporter (PubMed:26176916, PubMed:32860739, PubMed:9477959).
- **MT-ND6** (242): Core subunit of the mitochondrial membrane respiratory chain NADH dehydrogenase (Complex I) which catalyzes electron transfer from NADH through the respiratory chain, using ubiquinone as an electron acceptor (PubMed:14595656, PubMed:8644732).
- **MT-ND2** (226): Core subunit of the mitochondrial membrane respiratory chain NADH dehydrogenase (Complex I) which catalyzes electron transfer from NADH through the respiratory chain, using ubiquinone as an electron acceptor (PubMed:16996290).
- **NDUFV1** (226): Core subunit of the mitochondrial membrane respiratory chain NADH dehydrogenase (Complex I) which catalyzes electron transfer from NADH through the respiratory chain, using ubiquinone as an electron acceptor (PubMed:28844695).
- **MT-ND5** (226): Core subunit of the mitochondrial membrane respiratory chain NADH dehydrogenase (Complex I) which catalyzes electron transfer from NADH through the respiratory chain, using ubiquinone as an electron acceptor (PubMed:15250827).
- **SOD1** (140): Destroys radicals which are normally produced within the cells and which are toxic to biological systems (PubMed:18948262, PubMed:24140062).
- **TARDBP** (105): RNA-binding protein that is involved in various steps of RNA biogenesis and processing (PubMed:23519609).
- **FUS** (184): DNA/RNA-binding protein that plays a role in various cellular processes such as transcription regulation, RNA splicing, RNA transport, DNA repair and damage response (PubMed:27731383).
- **TBK1** (398): Serine/threonine kinase that plays an essential role in regulating inflammatory responses to foreign agents (PubMed:10581243, PubMed:11839743, PubMed:12692549, PubMed:12702806, PubMed:14703513, PubMed:15367631, PubMed:15485837, PubMed:18583960, PubMed:21138416, PubMed:23453971, PubMed:23453972, PubMed:23746807, PubMed:25636800, PubMed:26611359, PubMed:32404352, PubMed:34363755, PubMed:32298923).
- **SQSTM1** (469): Molecular adapter required for selective macroautophagy (aggrephagy) by acting as a bridge between polyubiquitinated proteins and autophagosomes (PubMed:15340068, PubMed:15953362, PubMed:16286508, PubMed:17580304, PubMed:20168092, PubMed:22017874, PubMed:22622177, PubMed:24128730, PubMed:28404643, PubMed:29343546, PubMed:29507397, PubMed:31857589, PubMed:33509017, PubMed:34471133, PubMed:34893540, PubMed:35831301, PubMed:37306101, PubMed:37802024, PubMed:40542578).
- **ANG** (468): Secreted ribonuclease that can either promote or restrict cell proliferation of target cells, depending on the context (PubMed:12051708, PubMed:1400510, PubMed:19332886, PubMed:20129916, PubMed:21855800, PubMed:23047679, PubMed:23843625, PubMed:2424496, PubMed:2459697, PubMed:2730651, PubMed:27518564, PubMed:28176817, PubMed:29100074, PubMed:29748193, PubMed:3122207, PubMed:32510170, PubMed:38718836, PubMed:8159680, PubMed:8570639, PubMed:8622921, PubMed:9578571).
- **VAPB** (229): Endoplasmic reticulum (ER)-anchored protein that mediates the formation of contact sites between the ER and endosomes via interaction with FFAT motif-containing proteins such as STARD3 or WDR44 (PubMed:32344433, PubMed:33124732).
- **FIG4** (215): Dual specificity phosphatase component of the PI(3,5)P2 regulatory complex which regulates both the synthesis and turnover of phosphatidylinositol 3,5-bisphosphate (PtdIns(3,5)P2) (PubMed:17556371, PubMed:33098764).
- **SETX** (233): ATP-dependent 5'-3' helicase that preferentially unwinds RNA:DNA substrates over DNA:DNA substrates, playing a crucial role in resolving 5'-overhang RNA:DNA hybrids (R-loops) and promoting transcription termination (PubMed:36864660).
- **UGCG** (174): Participates in the initial step of the glucosylceramide-based glycosphingolipid/GSL synthetic pathway at the cytosolic surface of the Golgi (PubMed:1532799, PubMed:8643456).
- **SMPD1** (154): Converts sphingomyelin to ceramide (PubMed:12563314, PubMed:1840600, PubMed:18815062, PubMed:25339683, PubMed:25920558, PubMed:27659707, PubMed:33163980).
- **ELP1** (242): Component of the elongator complex which is required for multiple tRNA modifications, including mcm5U (5-methoxycarbonylmethyl uridine), mcm5s2U (5-methoxycarbonylmethyl-2-thiouridine), and ncm5U (5-carbamoylmethyl uridine) (PubMed:29332244).
- **FOXP3** (253): Transcriptional regulator which is crucial for the development and inhibitory function of regulatory T-cells (Treg) (PubMed:17377532, PubMed:21458306, PubMed:23947341, PubMed:24354325, PubMed:24722479, PubMed:24835996, PubMed:30513302, PubMed:32644293).
- **SIRT1** (1219): NAD-dependent protein deacetylase that links transcriptional regulation directly to intracellular energetics and participates in the coordination of several separated cellular functions such as cell cycle, response to DNA damage, metabolism, apoptosis and autophagy (PubMed:11672523, PubMed:12006491, PubMed:14976264, PubMed:14980222, PubMed:15126506, PubMed:15152190, PubMed:15205477, PubMed:15469825, PubMed:15692560, PubMed:16079181, PubMed:16166628, PubMed:16892051, PubMed:16998810, PubMed:17283066, PubMed:17290224, PubMed:17334224, PubMed:17505061, PubMed:17612497, PubMed:17620057, PubMed:17936707, PubMed:18203716, PubMed:18296641, PubMed:18662546, PubMed:18687677, PubMed:19188449, PubMed:19220062, PubMed:19364925, PubMed:19690166, PubMed:19934257, PubMed:20097625, PubMed:20100829, PubMed:20203304, PubMed:20375098, PubMed:20620956, PubMed:20670893, PubMed:20817729, PubMed:20955178, PubMed:21149730, PubMed:21245319, PubMed:21471201, PubMed:21504832, PubMed:21555002, PubMed:21698133, PubMed:21701047, PubMed:21775285, PubMed:21807113, PubMed:21841822, PubMed:21890893, PubMed:21947282, PubMed:22274616, PubMed:22918831, PubMed:24415752, PubMed:24824780, PubMed:29681526, PubMed:29765047, PubMed:30409912).
- **TLR4** (426): Transmembrane receptor that functions as a pattern recognition receptor recognizing pathogen- and damage-associated molecular patterns (PAMPs and DAMPs) to induce innate immune responses via downstream signaling pathways (PubMed:10835634, PubMed:15809303, PubMed:16622205, PubMed:17292937, PubMed:17478729, PubMed:20037584, PubMed:20711192, PubMed:23880187, PubMed:27022195, PubMed:29038465, PubMed:17803912, PubMed:15852007).
- **GALC** (138): Hydrolyzes the galactose ester bonds of glycolipids such as galactosylceramide and galactosylsphingosine (PubMed:8281145, PubMed:8399327).
- **VEGFA** (148): Participates in the induction of key genes involved in the response to hypoxia and in the induction of angiogenesis such as HIF1A (PubMed:35455969).
- **GNAS** (256): Guanine nucleotide-binding proteins (G proteins) function as transducers in numerous signaling pathways controlled by G protein-coupled receptors (GPCRs) (PubMed:12391161, PubMed:17110384, PubMed:21488135, PubMed:26206488, PubMed:8702665, PubMed:10200251).
- **C5AR1** (316): Receptor for the chemotactic and inflammatory peptide anaphylatoxin C5a, stimulating chemotaxis, granule enzyme release, intracellular calcium release and superoxide anion production (PubMed:10636859, PubMed:15153520, PubMed:1847994, PubMed:29300009, PubMed:36806352, PubMed:7622471, PubMed:8182049, PubMed:9553099).
- **KCNN4** (438): Intermediate conductance calcium-activated potassium channel that mediates the voltage-independent transmembrane transfer of potassium across the cell membrane through a constitutive interaction with calmodulin which binds the intracellular calcium allowing its opening (PubMed:10026195, PubMed:10961988, PubMed:11425865, PubMed:15831468, PubMed:17157250, PubMed:18796614, PubMed:26148990, PubMed:9326665, PubMed:9380751, PubMed:9407042).
- **C5** (312): Precursor of the C5a anaphylatoxin and complement C5b components of the complement pathways, which consist in a cascade of proteins that leads to phagocytosis and breakdown of pathogens and signaling that strengthens the adaptive immune system (PubMed:12878586, PubMed:18204047, PubMed:30643019, PubMed:6554279).
- **ADA** (155): Catalyzes the hydrolytic deamination of adenosine and 2-deoxyadenosine (PubMed:16670267, PubMed:23193172, PubMed:26166670, PubMed:8452534, PubMed:9361033).
- **TRPV1** (177): Non-selective calcium permeant cation channel involved in detection of noxious chemical and thermal stimuli (PubMed:11050376, PubMed:11243859, PubMed:11226139, PubMed:12077606).
- **NSUN2** (234): RNA cytosine C(5)-methyltransferase that methylates cytosine to 5-methylcytosine (m5C) in various RNAs, such as tRNAs, mRNAs and some long non-coding RNAs (lncRNAs) (PubMed:17071714, PubMed:22995836, PubMed:31199786, PubMed:31358969).
- **POMGNT1** (180): Participates in O-mannosyl glycosylation by catalyzing the addition of N-acetylglucosamine to O-linked mannose on glycoproteins (PubMed:11709191, PubMed:27493216, PubMed:28512129).
- **FOXE3** (160): Transcription factor that controls lens epithelial cell growth through regulation of proliferation, apoptosis and cell cycle (PubMed:22527307, PubMed:25504734).
- **GLI3** (321): Transcription factor that acts as a key effector of the smoothened signaling pathway, and which plays a role in the development and patterning of various body structures, including the brain and limbs (PubMed:10075717, PubMed:10375510, PubMed:10693759, PubMed:11238441, PubMed:17764085, PubMed:20154143, PubMed:27146893).
- **GLRA1** (124): Subunit of heteromeric glycine-gated chloride channels (PubMed:14551753, PubMed:23994010, PubMed:25730860, PubMed:37821459).
- **FOXC1** (413): DNA-binding transcriptional factor that plays a role in a broad range of cellular and developmental processes such as eye, bones, cardiovascular, kidney and skin development (PubMed:11782474, PubMed:14506133, PubMed:14578375, PubMed:15277473, PubMed:15299087, PubMed:15684392, PubMed:16449236, PubMed:16492674, PubMed:17210863, PubMed:19279310, PubMed:19793056, PubMed:25786029, PubMed:27804176, PubMed:27907090).
- **F9** (337): Factor IX is a vitamin K-dependent plasma protein that participates in the intrinsic pathway of blood coagulation by converting factor X to its active form in the presence of Ca(2+) ions, phospholipids, and factor VIIIa (PubMed:8295821, PubMed:2592373, PubMed:20121197, PubMed:20121198, PubMed:1730085, PubMed:19846852, PubMed:39880037).
- **PLG** (121): Protease which primary function is to degrade fibrin, the main component of blood clots (PubMed:6094526, PubMed:6919539).
- **SERPINC1** (131): Most important serine protease inhibitor in plasma that regulates the blood coagulation cascade (PubMed:15140129, PubMed:15853774).
- **FUNDC2** (283): Binds directly and specifically 1,2-Diacyl-sn-glycero-3-phospho-(1'-myo-inositol-3',4',5'-bisphosphate) (PIP3) leading to the recruitment of PIP3 to mitochondria and may play a role in the regulation of the platelet activation via AKT/GSK3B/cGMP signaling pathways (PubMed:29786068).
- **H2AB1** (158): Atypical histone H2A which can replace conventional H2A in some nucleosomes and is associated with active transcription and mRNA processing (PubMed:22795134).
- **RPS20** (59): Component of the small ribosomal subunit (PubMed:23636399).
- **RPL17** (93): Component of the large ribosomal subunit (PubMed:12962325, PubMed:23636399, PubMed:32669547).
- **RPS21** (93): Component of the small ribosomal subunit (PubMed:23636399, PubMed:25901680, PubMed:25957688).
- **RPL31** (76): Component of the large ribosomal subunit (PubMed:23636399, PubMed:32669547).
- **RPS10** (57): Component of the 40S ribosomal subunit (PubMed:23636399).
- **RPS17** (59): Component of the small ribosomal subunit (PubMed:23636399).
- **RPL36** (127): Component of the large ribosomal subunit (PubMed:12962325, PubMed:23636399, PubMed:25901680, PubMed:25957688, PubMed:32669547).
- **RPS15** (59): Component of the small ribosomal subunit (PubMed:23636399).
- **RPL13** (167): Component of the ribosome, a large ribonucleoprotein complex responsible for the synthesis of proteins in the cell (PubMed:23636399, PubMed:31630789, PubMed:32669547).
- **RPS9** (59): Component of the small ribosomal subunit (PubMed:23636399).
- **RPS7** (59): Component of the small ribosomal subunit (PubMed:23636399).
- **RPS3** (75): Component of the small ribosomal subunit (PubMed:23636399, PubMed:8706699).
- **RPL7** (93): Component of the large ribosomal subunit (PubMed:12962325, PubMed:23636399, PubMed:32669547).
- **RPL35** (93): Component of the large ribosomal subunit (PubMed:12962325, PubMed:23636399, PubMed:32669547).
- **RPL27** (127): Component of the large ribosomal subunit (PubMed:12962325, PubMed:23636399, PubMed:25901680, PubMed:25957688, PubMed:32669547).
- **RPL23A** (76): Component of the large ribosomal subunit (PubMed:23636399, PubMed:32669547).
- **RPS27** (75): Component of the small ribosomal subunit (PubMed:23636399, PubMed:8706699).
- **KCNH5** (282): Pore-forming (alpha) subunit of a voltage-gated delayed rectifier potassium channel that mediates outward-rectifying potassium currents which, on depolarization, reaches a steady-state level and do not inactivate (PubMed:11943152, PubMed:12135768, PubMed:24133262, PubMed:36928654).
- **KCNS3** (200): Potassium channel regulatory subunit that modulates the delayed rectifier potassium channel activity of KCNB1 by namely slowing down the deactivation and inactivation time constants (PubMed:10484328).
- **KCNA1** (216): Voltage-gated potassium channel that mediates transmembrane potassium transport in excitable membranes, primarily in the brain and the central nervous system, but also in the kidney (PubMed:19903818, PubMed:8845167).
- **KCNC4** (241): Voltage-gated potassium channel that opens in response to the voltage difference across the membrane, forming a potassium-selective channel through which potassium ions pass in accordance with their electrochemical gradient (PubMed:7993631).
- **KCNQ4** (172): Pore-forming subunit of the voltage-gated potassium (Kv) channel involved in the regulation of sensory cells excitability in the cochlea (PubMed:10025409, PubMed:34767770).
- **KCNG2** (186): Regulatory alpha-subunit of the voltage-gated potassium (Kv) channel which, when coassembled with KCNB1, can modulate the kinetics and conductance-voltage relationship (PubMed:10551266).
- **KCNH8** (154): Pore-forming (alpha) subunit of a voltage-gated delayed rectifier potassium channel that mediates outward-rectifying potassium currents (PubMed:11897058).
- **KCNH7** (102): Pore-forming (alpha) subunit of voltage-gated inwardly rectifying potassium channel (PubMed:32723862).
- **KCNH4** (84): Pore-forming (alpha) subunit of a voltage-gated delayed rectifier (PubMed:10455180).
- **KCNH3** (104): Pore-forming (alpha) subunit of a voltage-gated inwardly rectifying potassium channel (PubMed:10455180).
- **KCNG3** (263): Regulatory subunit of the voltage-gated potassium (Kv) channel which, when coassembled with KCNB1, modulates the kinetics parameters of the heterotetrameric channel namely the inactivation and deactivation rate (PubMed:11852086, PubMed:12060745, PubMed:19074135).
- **KCND1** (141): A-type voltage-gated potassium channel that mediates transmembrane potassium transport in excitable membranes in the brain (PubMed:15454437).
- **GABBR1** (212): Component of a heterodimeric G protein-coupled receptor for GABA, formed by GABBR1 and GABBR2 (PubMed:15617512, PubMed:18165688, PubMed:22660477, PubMed:24305054, PubMed:36103875, PubMed:9872316, PubMed:9872744).
- **GABBR2** (195): Component of a heterodimeric G protein-coupled receptor for GABA, formed by GABBR1 and GABBR2 (PubMed:15617512, PubMed:18165688, PubMed:22660477, PubMed:24305054, PubMed:9872316, PubMed:9872744).
- **EIF3G** (216): RNA-binding component of the eukaryotic translation initiation factor 3 (eIF-3) complex, which is required for several steps in the initiation of protein synthesis (PubMed:17581632, PubMed:25849773, PubMed:27462815).
- **PATJ** (139): Scaffolding protein that facilitates the localization of proteins to the cell membrane (PubMed:11927608, PubMed:16678097, PubMed:22006950).
- **PRF1** (229): Pore-forming protein that plays a key role in granzyme-mediated programmed cell death, and in defense against virus-infected or neoplastic cells (PubMed:20889983, PubMed:21037563, PubMed:24558045, PubMed:9058810, PubMed:9164947).
- **CTSC** (32): Thiol protease (PubMed:1586157).
- **ADO** (299): Plays a vital role in regulating thiol metabolism and preserving oxygen homeostasis by oxidizing the sulfur of cysteamine and N-terminal cysteine-containing proteins to their corresponding sulfinic acids using O2 as a cosubstrate (PubMed:17581819, PubMed:29752763, PubMed:31273118, PubMed:32601061).
- **MBD2** (127): Binds CpG islands in promoters where the DNA is methylated at position 5 of cytosine within CpG dinucleotides (PubMed:9774669).
- **DCT** (55): Plays a role in melanin biosynthesis (PubMed:33100333).
- **CYP11A1** (178): A cytochrome P450 monooxygenase that catalyzes the side-chain hydroxylation and cleavage of cholesterol to pregnenolone, the precursor of most steroid hormones (PubMed:21636783).
- **IL1B** (101): Potent pro-inflammatory cytokine (PubMed:10653850, PubMed:12794819, PubMed:28331908, PubMed:3920526).
- **BDNF** (101): Important signaling molecule that activates signaling cascades downstream of NTRK2 (PubMed:11152678).
- **GPT** (145): Pyridoxal enzyme tha catalyzes the reversible transamination between alanine and 2-oxoglutarate to form pyruvate and glutamate (PubMed:11863375).
- **SERPING1** (156): Serine protease inhibitor, which acrs as a regulator of the classical complement pathway (PubMed:10946292, PubMed:11527969, PubMed:3458172, PubMed:6416294).
- **C1S** (403): Component of the complement C1 complex, a multiprotein complex that initiates the classical pathway of the complement system, a cascade of proteins that leads to phagocytosis and breakdown of pathogens and signaling that strengthens the adaptive immune system (PubMed:11445589, PubMed:16169853, PubMed:417728, PubMed:467643, PubMed:6271784, PubMed:6282646, PubMed:6319179, PubMed:70787, PubMed:9422791).
- **GRK6** (114): Specifically phosphorylates the activated forms of G protein-coupled receptors (PubMed:19423652, PubMed:20048153).
- **IGFBP3** (307): Multifunctional protein that plays a critical role in regulating the availability of IGFs such as IGF1 and IGF2 to their receptors and thereby regulates IGF-mediated cellular processes including proliferation, differentiation, and apoptosis in a cell-type specific manner (PubMed:10874028, PubMed:19556345).
- **ARMC5** (218): Substrate-recognition component of a BCR (BTB-CUL3-RBX1) E3 ubiquitin ligase complex that terminates RNA polymerase II (Pol II) transcription in the promoter-proximal region of genes (PubMed:39504960, PubMed:39667934).
- **CYP11B1** (208): A cytochrome P450 monooxygenase mainly involved in the biosynthesis of adrenal corticoids (PubMed:12530636, PubMed:1518866, PubMed:1775135, PubMed:18215163, PubMed:23322723, PubMed:23685396, PubMed:29277707).
- **KDM1A** (294): Histone demethylase that can demethylate both 'Lys-4' (H3K4me) and 'Lys-9' (H3K9me) of histone H3, thereby acting as a coactivator or a corepressor, depending on the context (PubMed:15620353, PubMed:15811342, PubMed:16079794, PubMed:16079795, PubMed:16140033, PubMed:16223729, PubMed:27292636).
- **CYP11B2** (439): A cytochrome P450 monooxygenase that catalyzes the biosynthesis of aldosterone, the main mineralocorticoid in the human body responsible for salt and water homeostasis, thus involved in blood pressure regulation, arterial hypertension, and the development of heart failure (PubMed:11856349, PubMed:12530636, PubMed:1518866, PubMed:15356073, PubMed:1594605, PubMed:1775135, PubMed:22446688, PubMed:23322723, PubMed:9814482, PubMed:9814506).
- **PRKACA** (333): Phosphorylates a large number of substrates in the cytoplasm and the nucleus (PubMed:15642694, PubMed:15905176, PubMed:16387847, PubMed:17333334, PubMed:17565987, PubMed:17693412, PubMed:18836454, PubMed:19949837, PubMed:20356841, PubMed:21085490, PubMed:21514275, PubMed:21812984, PubMed:21852232, PubMed:31112131, PubMed:41652173).
- **NOD2** (301): Pattern recognition receptor (PRR) that detects bacterial peptidoglycan fragments and other danger signals and plays an important role in gastrointestinal immunity (PubMed:12514169, PubMed:12527755, PubMed:12626759, PubMed:15044951, PubMed:15998797, PubMed:27283905, PubMed:27748583, PubMed:31649195).
- **CCL24** (88): Chemotactic for resting T-lymphocytes, and eosinophils (PubMed:9104803, PubMed:9365122).
- **LAT** (163): Required for TCR (T-cell antigen receptor)- and pre-TCR-mediated signaling, both in mature T-cells and during their development (PubMed:23514740, PubMed:25907557).
- **STAT4** (200): Transcriptional regulator mainly expressed in hematopoietic cells that plays a critical role in cellular growth, differentiation and immune response (PubMed:10961885, PubMed:37256972, PubMed:8943379).
- **TNIP1** (228): Inhibits NF-kappa-B activation and TNF-induced NF-kappa-B-dependent gene expression by regulating TAX1BP1 and A20/TNFAIP3-mediated deubiquitination of IKBKG; proposed to link A20/TNFAIP3 to ubiquitinated IKBKG (PubMed:21885437).
- **DGKQ** (212): Diacylglycerol kinase that converts diacylglycerol/DAG into phosphatidic acid/phosphatidate/PA and regulates the respective levels of these two bioactive lipids (PubMed:11309392, PubMed:22627129, PubMed:9099683).
- **CUL4A** (323): Core component of multiple cullin-RING-based E3 ubiquitin-protein ligase complexes which mediate the ubiquitination of target proteins (PubMed:14578910, PubMed:14739464, PubMed:15448697, PubMed:15548678, PubMed:15811626, PubMed:16678110, PubMed:17041588, PubMed:24209620, PubMed:30166453, PubMed:33854232, PubMed:33854239).
- **CRBN** (274): Substrate recognition component of a DCX (DDB1-CUL4-X-box) E3 protein ligase complex that mediates the ubiquitination and subsequent proteasomal degradation of target proteins, such as MEIS2, ILF2, GLUL, IKZF1 and CSNK1A1 (PubMed:26990986, PubMed:33009960, PubMed:41565821).
- **DDB1** (285): Involved in DNA repair and protein ubiquitination, as part of the UV-DDB complex and DCX (DDB1-CUL4-X-box) complexes, respectively (PubMed:14739464, PubMed:15448697, PubMed:16260596, PubMed:16407242, PubMed:16407252, PubMed:16482215, PubMed:16940174, PubMed:17079684, PubMed:25970626).
- **RBX1** (647): E3 ubiquitin ligase component of multiple cullin-RING-based E3 ubiquitin-protein ligase (CRLs) complexes which mediate the ubiquitination and subsequent proteasomal degradation of target proteins, including proteins involved in cell cycle progression, signal transduction, transcription and transcription-coupled nucleotide excision repair (PubMed:10230407, PubMed:10579999, PubMed:11961546, PubMed:15983046, PubMed:16678110, PubMed:19112177, PubMed:19679664, PubMed:22748924, PubMed:23455478, PubMed:27565346, PubMed:29769719, PubMed:32355176, PubMed:33417871, PubMed:37844242, PubMed:38326650, PubMed:39504960, PubMed:39667934, PubMed:38316879).
- **IRF8** (202): Transcription factor that specifically binds to the upstream regulatory region of type I interferon (IFN) and IFN-inducible MHC class I genes (the interferon consensus sequence (ICS)) (PubMed:25122610).
- **MEFV** (311): Involved in the regulation of innate immunity and the inflammatory response in response to IFNG/IFN-gamma (PubMed:10807793, PubMed:11468188, PubMed:16037825, PubMed:16785446, PubMed:17431422, PubMed:17964261, PubMed:18577712, PubMed:19109554, PubMed:19584923, PubMed:26347139, PubMed:27030597, PubMed:28835462).
- **IL18R1** (208): Within the IL18 receptor complex, responsible for the binding of the pro-inflammatory cytokine IL18, but not IL1A nor IL1B (PubMed:14528293, PubMed:25261253, PubMed:25500532, PubMed:37993714, PubMed:8626725).
- **CCR1** (135): Chemokine receptor that plays a crucial role in regulating immune cell migration, inflammation, and immune responses (PubMed:14991608).
- **KCNQ3** (217): Pore-forming subunit of the voltage-gated potassium (Kv) M-channel which is responsible for the M-current, a key controller of neuronal excitability (PubMed:16319223, PubMed:27564677, PubMed:28793216, PubMed:9872318).
- **FUT2** (408): Catalyzes the transfer of L-fucose, from a guanosine diphosphate-beta-L-fucose, to the terminal galactose on both O- and N-linked glycans chains of cell surface glycoproteins and glycolipids and the resulting epitope regulates several processes such as cell-cell interaction including host-microbe interaction, cell surface expression and cell proliferation (PubMed:12692541, PubMed:7876235, PubMed:8018146).
- **KCNQ5** (217): Pore-forming subunit of the voltage-gated potassium (Kv) channel broadly expressed in brain and involved in the regulation of neuronal excitability (PubMed:10787416, PubMed:10816588, PubMed:11159685, PubMed:28669405).
- **CCR3** (185): G protein-coupled receptor (GPCR) that plays a key role in the immune system by regulating the migration and activation of white blood cells in response to chemokines (PubMed:28994588).
- **IL19** (91): Cytokine that functions as an anti-inflammatory and proangiogenic factor (PubMed:34932373).
- **NCSTN** (314): Essential subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:10993067, PubMed:12679784, PubMed:25043039, PubMed:26280335, PubMed:30598546, PubMed:30630874).
- **PSENEN** (331): Essential subunit of the gamma-secretase complex, an endoprotease complex that catalyzes the intramembrane cleavage of integral membrane proteins such as Notch receptors and APP (amyloid-beta precursor protein) (PubMed:12522139, PubMed:12679784, PubMed:12740439, PubMed:12763021, PubMed:24941111, PubMed:30598546, PubMed:30630874).
- **IL17F** (148): Effector cytokine of innate and adaptive immune system involved in antimicrobial host defense and maintenance of tissue integrity (PubMed:21350122).
- **NDUFAF4** (128): Involved in the assembly of mitochondrial NADH:ubiquinone oxidoreductase complex (complex I) (PubMed:18179882, PubMed:28853723).
- **NDUFAF2** (102): Acts as a molecular chaperone for mitochondrial complex I assembly (PubMed:16200211, PubMed:19384974).
- **NDUFA8** (199): Accessory subunit of the mitochondrial membrane respiratory chain NADH dehydrogenase (Complex I), that is believed not to be involved in catalysis (PubMed:27626371, PubMed:32385911, PubMed:33153867).
- **DCDC2** (97): Protein that plays a role in the inhibition of canonical Wnt signaling pathway (PubMed:25557784).
- **SEMA4D** (114): Cell surface receptor for PLXNB1 and PLXNB2 that plays an important role in cell-cell signaling (PubMed:20877282).
- **CD6** (227): Cell adhesion molecule that mediates cell-cell contacts and regulates T-cell responses via its interaction with ALCAM/CD166 (PubMed:15048703, PubMed:15294938, PubMed:16352806, PubMed:16914752, PubMed:24584089, PubMed:24945728).
- **PPARD** (109): Ligand-activated transcription factor key mediator of energy metabolism in adipose tissues (PubMed:35675826).
- **CD40** (45): Receptor for TNFSF5/CD40LG (PubMed:31331973).
- **INPP5D** (301): Phosphatidylinositol (PtdIns) phosphatase that specifically hydrolyzes the 5-phosphate of phosphatidylinositol-3,4,5-trisphosphate (PtdIns(3,4,5)P3) to produce PtdIns(3,4)P2, thereby negatively regulating the PI3K (phosphoinositide 3-kinase) pathways (PubMed:10764818, PubMed:8723348, PubMed:8769125).
- **CACNB3** (116): Regulatory subunit of the voltage-gated calcium channel that gives rise to L-type calcium currents (PubMed:8119293).
- **CACNG4** (113): Regulates the activity of L-type calcium channels that contain CACNA1C as pore-forming subunit (PubMed:21127204).
- **CACNB1** (96): Regulatory subunit of L-type calcium channels (PubMed:1309651, PubMed:15615847, PubMed:8107964).
- **CACNA2D1** (176): The alpha-2/delta subunit of voltage-dependent calcium channels regulates calcium current density and activation/inactivation kinetics of the calcium channel (PubMed:35293990).
- **TMEM163** (158): Zinc ion transporter that mediates zinc efflux and plays a crucial role in intracellular zinc homeostasis (PubMed:25130899, PubMed:31697912, PubMed:36204728).
- **CD226** (249): Cell surface receptor that plays an important role in the immune system, particularly in intercellular adhesion, lymphocyte signaling, cytotoxicity and lymphokine secretion mediated by cytotoxic T-cells and NK cells (PubMed:8673704, PubMed:9712030).
- **POU2AF1** (113): Transcriptional coactivator that specifically associates with either POU2F1/OCT1 or POU2F2/OCT2 (PubMed:7859290).
- **DENND1B** (199): Guanine nucleotide exchange factor (GEF) for RAB35 that acts as a regulator of T-cell receptor (TCR) internalization in TH2 cells (PubMed:20154091, PubMed:20937701, PubMed:24520163, PubMed:26774822).
- **ELMO1** (143): Regulates the activity of DOCK guanine nucleotide exchange factors (GEFs) (PubMed:11595183, PubMed:12134158, PubMed:32651375, PubMed:38857861).
- **RNF135** (286): E2-dependent E3 ubiquitin-protein ligase that functions as a RIGI coreceptor in the sensing of viral RNAs in cell cytoplasm and the activation of the antiviral innate immune response (PubMed:19017631, PubMed:19484123, PubMed:21147464, PubMed:23950712, PubMed:28469175, PubMed:31006531).
- **EXT1** (238): Glycosyltransferase forming with EXT2 the heterodimeric heparan sulfate polymerase which catalyzes the elongation of the heparan sulfate glycan backbone (PubMed:10639137, PubMed:22660413, PubMed:36402845, PubMed:36593275, PubMed:9620772).
- **ABCA1** (192): Catalyzes the translocation of specific phospholipids from the cytoplasmic to the extracellular/lumenal leaflet of membrane coupled to the hydrolysis of ATP (PubMed:24097981, PubMed:35974019).
- **IFNB1** (257): Type I interferon cytokine that plays a key role in the innate immune response to infection, developing tumors and other inflammatory stimuli (PubMed:10049744, PubMed:10556041, PubMed:6157094, PubMed:6171735, PubMed:7665574, PubMed:8027027, PubMed:8969169).
- **PPIA** (172): Catalyzes the cis-trans isomerization of proline imidic peptide bonds in oligopeptides (PubMed:2001362, PubMed:20676357, PubMed:21245143, PubMed:21593166, PubMed:25678563).
- **IL1R1** (68): Receptor for IL1A, IL1B and IL1RN (PubMed:2950091, PubMed:37315560).
- **TACR3** (175): Receptor for the tachykinin neuromedin-K (neurokinin B), also able to bind and respond to tachynins substance K/neurokinin A and substance P (PubMed:1312036, PubMed:37391393).
- **STAT1** (302): Signal transducer and transcription activator that mediates cellular responses to interferons (IFNs), cytokine KITLG/SCF and other cytokines and other growth factors (PubMed:12764129, PubMed:12855578, PubMed:15322115, PubMed:23940278, PubMed:34508746, PubMed:35568036, PubMed:9724754, PubMed:32814877).
- **RPGRIP1L** (112): Negatively regulates signaling through the G protein-coupled thromboxane A2 receptor (TBXA2R) (PubMed:19464661).
- **SLC33A1** (306): Acetyl-CoA transporter that mediates active acetyl-CoA import through the endoplasmic reticulum (ER) membrane into the ER lumen where specific ER-based acetyl-CoA:lysine acetyltransferases are responsible for the acetylation of ER-based protein substrates, such as BACE1 (PubMed:20826464, PubMed:24828632).
- **SLC40A1** (253): Transports Fe(2+) from the inside of a cell to the outside of the cell, playing a key role for maintaining systemic iron homeostasis (PubMed:15692071, PubMed:22178646, PubMed:22682227, PubMed:24304836, PubMed:29237594, PubMed:29599243, PubMed:30247984).
- **TFRC** (167): Cellular uptake of iron occurs via receptor-mediated endocytosis of ligand-occupied transferrin receptor into specialized endosomes (PubMed:26214738, PubMed:41772062).
- **BMP4** (196): Growth factor of the TGF-beta superfamily that plays essential roles in many developmental processes, including neurogenesis, vascular development, angiogenesis and osteogenesis (PubMed:31363885).
- **CD40LG** (81): Cytokine that acts as a ligand to CD40/TNFRSF5 (PubMed:1280226, PubMed:31331973).
- **HJV** (72): Acts as a bone morphogenetic protein (BMP) coreceptor (PubMed:18976966).
- **BMP6** (158): Growth factor of the TGF-beta superfamily that plays essential roles in many developmental processes including cartilage and bone formation (PubMed:31019025).
- **SLC46A1** (311): Proton-coupled folate symporter that mediates folate absorption using an H(+) gradient as a driving force (PubMed:17129779, PubMed:17446347, PubMed:17475902, PubMed:19389703, PubMed:19762432, PubMed:25504888, PubMed:29344585, PubMed:30858177, PubMed:31494288, PubMed:31792273, PubMed:32893190, PubMed:34619546).
- **SLC11A2** (196): Proton-coupled metal ion symporter operating with a proton to metal ion stoichiometry of 1:1 (PubMed:17109629, PubMed:17293870, PubMed:22736759, PubMed:25326704, PubMed:25491917, PubMed:39824808).
- **FBXL5** (219): Component of some SCF (SKP1-cullin-F-box) protein ligase complex that plays a central role in iron homeostasis by promoting the ubiquitination and subsequent degradation of IREB2/IRP2 (PubMed:19762596, PubMed:19762597).
- **NR0B1** (215): Nuclear receptor that lacks a DNA-binding domain and acts as a corepressor that inhibits the transcriptional activity of other nuclear receptors through heterodimeric interactions (PubMed:12482977, PubMed:32433991).
- **AAAS** (136): Plays a role in the normal development of the peripheral and central nervous system (PubMed:11062474, PubMed:11159947, PubMed:16022285).
- **MC2R** (211): G protein-coupled receptor for corticotropin/ACTH, primarily expressed in adrenal cortex where it plays a key role in the regulation of adrenocortical function (PubMed:1325670, PubMed:17596328, PubMed:36588120).
- **GMPPA** (187): Regulatory subunit of the GMPPA-GMPPB mannose-1-phosphate guanylyltransferase complex; reduces the catalytic activity of GMPPB when part of the complex (PubMed:24035193, PubMed:33986552).
- **CRHR1** (259): G protein-coupled receptor for CRH and UCN stress hormones, which plays a central role in whole body adaptation to stress (PubMed:18292205, PubMed:18801728, PubMed:20966082, PubMed:23576434, PubMed:23863939, PubMed:24290358, PubMed:32004469, PubMed:32004470).
- **TXNRD2** (130): Involved in the control of reactive oxygen species levels and the regulation of mitochondrial redox homeostasis (PubMed:24601690).
- **ABCD1** (313): ATP-dependent transporter of the ATP-binding cassette (ABC) family involved in the transport of very long chain fatty acid (VLCFA)-CoA from the cytosol to the peroxisome lumen (PubMed:11248239, PubMed:15682271, PubMed:16946495, PubMed:18757502, PubMed:21145416, PubMed:23671276, PubMed:29397936, PubMed:33500543).
- **AIRE** (306): Transcription factor playing an essential role to promote self-tolerance in the thymus by regulating the expression of a wide array of self-antigens that have the commonality of being tissue-restricted in their expression pattern in the periphery, called tissue restricted antigens (TRA) (PubMed:26084028).
- **FDX1** (91): Essential for the synthesis of various steroid hormones (PubMed:20547883, PubMed:21636783).
- **PLCB1** (229): Catalyzes the hydrolysis of 1-phosphatidylinositol 4,5-bisphosphate into diacylglycerol (DAG) and inositol 1,4,5-trisphosphate (IP3) and mediates intracellular signaling downstream of G protein-coupled receptors (PubMed:9188725).

## similarity_note: 34

A note such as (By similarity) or (Probable) is still there; the order did not ask to remove these.

- **ADORA2A** (39): Receptor for adenosine (By similarity).
- **HNF1A** (157): Transcriptional activator that regulates the tissue specific expression of multiple genes, especially in pancreatic islet cells and in liver (By similarity).
- **PAX4** (257): DNA-binding transcription factor that plays a central role in the differentiation and development of type B pancreatic cells, which are located within the pancreatic islets of Langerhans responsible for the production and release of insulin (By similarity).
- **ENPP1** (178): Nucleotide pyrophosphatase that generates diphosphate (PPi) and functions in bone mineralization and soft tissue calcification by regulating pyrophosphate levels (By similarity).
- **STXBP1** (132): Participates in the regulation of synaptic vesicle docking and fusion through interaction with GTP-binding proteins (By similarity).
- **TESPA1** (146): Required for the development and maturation of T-cells, its function being essential for the late stages of thymocyte development (By similarity).
- **ITGB7** (208): Integrin ITGA4/ITGB7 (alpha-4/beta-7) (Peyer patches-specific homing receptor LPAM-1) is an adhesion molecule that mediates lymphocyte migration and homing to gut-associated lymphoid tissue (GALT) (Probable).
- **WNT1** (86): Ligand for members of the frizzled family of seven transmembrane receptors (Probable).
- **UMOD** (272): Functions in biogenesis and organization of the apical membrane of epithelial cells of the thick ascending limb of Henle's loop (TALH), where it promotes formation of complex filamentous gel-like structure that may play a role in the water barrier permeability (Probable).
- **KCNJ10** (94): May be responsible for potassium buffering action of glial cells in the brain (By similarity).
- **GRIN3A** (231): Component of a non-conventional N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function as heterotetrameric, ligand-gated cation channels with low calcium permeability and low voltage-dependent block by Mg(2+) (By similarity).
- **GABRG3** (174): Gamma subunit of the heteropentameric ligand-gated chloride channel gated by gamma-aminobutyric acid (GABA), a major inhibitory neurotransmitter in the brain (By similarity).
- **VPS13C** (93): Mediates the transfer of lipids between membranes at organelle contact sites (By similarity).
- **SORL1** (100): Sorting receptor that directs several proteins to their correct location within the cell (Probable).
- **GRIN3B** (231): Component of a non-conventional N-methyl-D-aspartate (NMDA) receptors (NMDARs) that function as heterotetrameric, ligand-gated cation channels with low calcium permeability and low voltage-dependent block by Mg(2+) (By similarity).
- **LOXL1** (222): Catalyzes the oxidative deamination of lysine and hydroxylysine residues in collagen and elastin, resulting in the formation of covalent cross-linkages, and the stabilization of collagen and elastin fibers (By similarity).
- **WNT4** (86): Ligand for members of the frizzled family of seven transmembrane receptors (Probable).
- **BRAF** (114): Protein kinase involved in the transduction of mitogenic signals from the cell membrane to the nucleus (Probable).
- **BLK** (113): Non-receptor tyrosine kinase involved in B-lymphocyte development, differentiation and signaling (By similarity).
- **HDAC7** (135): Responsible for the deacetylation of lysine residues on the N-terminal part of the core histones (H2A, H2B, H3 and H4) (By similarity).
- **IGHMBP2** (132): 5' to 3' helicase that unwinds both RNA and DNA duplexes in an ATP-dependent reaction (Probable) (PubMed:19158098, PubMed:30218034).
- **PLEKHG5** (153): Functions as a guanine exchange factor (GEF) for RAB26 and thus regulates autophagy of synaptic vesicles in axon terminal of motoneurons (By similarity).
- **DCTN1** (137): Part of the dynactin complex that activates the molecular motor dynein for ultra-processive transport along microtubules (By similarity).
- **NDUFV2** (219): Core subunit of the mitochondrial membrane respiratory chain NADH dehydrogenase (Complex I) which catalyzes electron transfer from NADH through the respiratory chain, using ubiquinone as an electron acceptor (Probable).
- **ANXA11** (78): Binds specifically to calcyclin in a calcium-dependent manner (By similarity).
- **FDXR** (317): Serves as the first electron transfer protein in all the mitochondrial P450 systems including cholesterol side chain cleavage in all steroidogenic tissues, steroid 11-beta hydroxylation in the adrenal cortex, 25-OH-vitamin D3-24 hydroxylation in the kidney, and sterol C-27 hydroxylation in the liver (By similarity).
- **RPL41** (60): Component of the small ribosomal subunit (Probable) (Ref.8).
- **MOG** (55): Mediates homophilic cell-cell adhesion (By similarity).
- **SOX2** (203): Transcription factor that forms a trimeric complex with OCT4 on DNA and controls the expression of a number of genes involved in embryonic development such as YES1, FGF4, UTF1 and ZFP206 (By similarity).
- **BACH2** (80): Transcriptional regulator that acts as a repressor or activator (By similarity).
- **FOSL2** (54): Controls osteoclast survival and size (By similarity).
- **CACNB2** (159): Beta subunit of voltage-dependent calcium channels which contributes to the function of the calcium channel by increasing peak calcium current (By similarity).
- **SPRED1** (104): Tyrosine kinase substrate that inhibits growth-factor-mediated activation of MAP kinase (By similarity).
- **NNT** (157): The transhydrogenation between NADH and NADP is coupled to respiration and ATP hydrolysis and functions as a proton pump across the membrane (By similarity).

## no sentence at all: 17

Open Targets sent an empty functionDescriptions list.

- **CLN6** (ENSG00000128973), protein_coding, CLN6 transmembrane ER protein
- **FAM13A** (ENSG00000138640), protein_coding, family with sequence similarity 13 member A
- **SETBP1** (ENSG00000152217), protein_coding, SET binding protein 1
- **ADAMTS6** (ENSG00000049192), protein_coding, ADAM metallopeptidase with thrombospondin type 1 motif 6
- **RPS4Y1** (ENSG00000129824), protein_coding, ribosomal protein S4 Y-linked 1
- **RASSF3** (ENSG00000153179), protein_coding, Ras association domain family member 3
- **C1orf141** (ENSG00000203963), protein_coding, chromosome 1 open reading frame 141
- **FAM117B** (ENSG00000138439), protein_coding, family with sequence similarity 117 member B
- **ACOXL** (ENSG00000153093), protein_coding, acyl-CoA oxidase like
- **ACTL7B** (ENSG00000148156), protein_coding, actin like 7B
- **MST1** (ENSG00000173531), protein_coding, macrophage stimulating 1
- **EXOC3L4** (ENSG00000205436), protein_coding, exocyst complex component 3 like 4
- **MRPS9** (ENSG00000135972), protein_coding, mitochondrial ribosomal protein S9
- **VWA3B** (ENSG00000168658), protein_coding, von Willebrand factor A domain containing 3B
- **PHTF2** (ENSG00000006576), protein_coding, putative homeodomain transcription factor 2
- **HLA-H** (ENSG00000310469), lncRNA, major histocompatibility complex, class I, H (pseudogene) 
- **WBP1L** (ENSG00000166272), protein_coding, WW domain binding protein 1 like
