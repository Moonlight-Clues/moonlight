# fixtures/labels_confirmed: official labels saved for ticket 2.42

Every entry in `moonlight/confirmed.json` is backed by one saved label
below. Fetched on 2026-11-24 from DailyMed (the SPL behind the link, read
through DailyMed's own services). Each `.txt` file holds, in this order,
as in `fixtures/labels_read/` (ticket 2.41):

1. the link that was fetched,
2. the date it was fetched,
3. the product name line ("NAME- medicine form"),
4. the whole INDICATIONS AND USAGE section, word for word.

Only the spacing was tidied (one line per paragraph or list item). No word
was changed. The one-line summary the label repeats in its Highlights box
is left out. These entries are proposals until MAIN 3 has read the saved
label text.

The question asked of each label: does the current label name the disease
as an indication? An entry is only written when it does. The quote is that
sentence.

card | change | quoted label sentence | link | value replaced
---|---|---|---|---
Omaveloxolone (CHEMBL4303525), Friedreich ataxia (MONDO_0100339) | confirmed: stays on the main Approved list, no grey line, label as source | SKYCLARYS is indicated for the treatment of Friedreich's ataxia in adults and adolescents aged 16 years and older. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2709e870-df3d-f30f-e063-6394a90aeda1 | "no regulator record" line; would have moved to the new box
Ursodiol (CHEMBL1551), primary biliary cholangitis (MONDO_0005388) | confirmed: stays on the main Approved list, no grey line, label as source | URSO 250 and URSO Forte (ursodiol) tablets are indicated for the treatment of patients with primary biliary cholangitis (PBC). | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=e8fc4fc2-fe5c-4cba-b6e0-5ceaf2157a61 | "no regulator record" line; would have moved to the new box
Dextroamphetamine (CHEMBL612), narcolepsy (MONDO_0021107) | confirmed: stays on the main Approved list, no grey line, label as source | Dextroamphetamine Sulfate Tablets are indicated for: Narcolepsy. | https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=ec2d13f3-d14f-47e4-abe9-7763f95a8e94 | "no regulator record" line; would have moved to the new box

Notes for MAIN 3:
- The SKYCLARYS label covers people aged 16 and older only. confirmed.json
  has no "limited" key (its keys are the four asked for), so the card does
  not say so.
- Ursodiol: many generic ursodiol capsule labels are for gallstones only.
  The URSO 250 / URSO Forte tablet label is the one that names primary
  biliary cholangitis, so it is the one saved.
- Dextroamphetamine: the single-medicine tablet label was read, not a
  mixed-amphetamine-salts label.
