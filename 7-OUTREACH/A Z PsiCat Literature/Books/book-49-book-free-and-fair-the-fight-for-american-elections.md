# FREE AND FAIR: The Fight for American Elections — and the Machine We Are Building to Defend Them

*AxiomZero Technologies & Consulting, SPC commissioned work: Researched and written by PsiCat Ai.*
*Written: 2026-09-22T23:00:00Z*
*Season One · Original Commission (not a substack rewrite — this volume was commissioned directly for the PsiCat Literature lane and researched from primary and Tier-1 sources listed in Appendix C)*

## A rigorous, sourced, and unflinching account of how elections are won, lost, defended, and stolen — and what AxiomZero is building to make theft mathematically detectable

---

Historical-status note: this volume is maintained as a period-context document; treat repository/test-state numbers as historical unless explicitly marked live, and use `STATUS.md` plus `docs/mas_tracker.yml` for current status. Political facts in this volume are current as of the compilation date below and will age; consult the sources in Appendix C directly for the latest developments.

**Research Direction:** ThomasCory Walker-Pearson
**Research, Synthesis, and Writing:** PsiCat Ai (AxiomZero)
**Methodology:** Tier-1 sourcing — federal and state court opinions, Supreme Court opinions, Census/redistricting law, Congressional Research Service reports, DOJ and DHS public actions, academic election-law scholarship, and cross-checked reporting from at least two independent Tier-1 newsrooms per contested factual claim
**Confidence Classification:** CONFIRMED (court-adjudicated, government-published, or on-the-record admission) | CORROBORATED (multiple independent Tier-1 sources) | REPORTED (single credible Tier-1 source, not yet cross-confirmed) | CONTESTED (genuinely disputed between credible parties, both positions given)
**Date of Compilation:** September 2026
**Status:** Open-source, citation-anchored record. Every empirical claim in this book is tagged to a numbered source in Appendix C.

---

> *"The right to vote freely for the candidate of one's choice is of the essence of a democratic society, and any restrictions on that right strike at the heart of representative government."*
> — Chief Justice Earl Warren, *Reynolds v. Sims*, 377 U.S. 533 (1964)

> *"An election is a field evolution, not a database."*
> — AxiomZero EIGE design principle

---

## PREFATORY NOTE: WHAT THIS BOOK IS, AND WHAT IT REFUSES TO DO

This is a book about elections — how they are built, how they are won honestly, how they are cheated, and how a democracy notices the difference before it is too late to matter.

It is written under an explicit editorial instruction: stay rigorous, stay grounded, and do not manufacture false balance between a documented fact and a talking point designed to obscure it. Two things can both be true at once, and this book holds both: (1) in-person voter impersonation fraud in the United States is vanishingly rare and well-studied, and (2) the integrity of American elections is nonetheless under real, documented, structural pressure — from partisan redistricting, from administrative pressure on how elections are run, and from a global pattern of "competitive authoritarian" backsliding in which elections are held but the terms are rigged in advance. Refusing to pretend these two facts cancel each other out is not bias. It is accuracy.

This book does not allege that any specific 2026 election outcome has been or will be fraudulently altered. No such claim is made anywhere in this text. What it does allege — with citations — is that the *rules of the contest* have been altered by mid-decade gerrymanders in multiple states, that federal executive action has repeatedly reached toward levers of election administration the Constitution assigns to the states, and that the pattern of these actions matches a well-studied global playbook for tilting a nominally free election before a single vote is cast.

The book closes not with despair but with a blueprint: AxiomZero's own EIGE (Election Integrity Governance Engine), an adjacent-track engineering answer to the specific, narrow problem of *making ballot-sequence tampering mathematically detectable in real time* — not a claim to fix politics, gerrymandering, or turnout suppression, all of which are legal and social problems requiring legal and social remedies, not cryptography.

---

## TABLE OF CONTENTS

**PART ONE — FIRST PRINCIPLES**
1. What "Free and Fair" Actually Means
2. A Short, Honest History of Election Rigging in America
3. How Elections Are Actually Cheated: A Taxonomy

**PART TWO — THE MODERN MACHINERY OF DISTORTION**
4. Gerrymandering: The Legal Weapon That Doesn't Need to Break the Law
5. *Rucho v. Common Cause* and the Federal Courts' Retreat
6. The 2025–2026 Mid-Decade Redistricting War: Texas, California, and the Map Arms Race
7. The Supreme Court, the Purcell Principle, and *Louisiana v. Callais*
8. Voter Suppression After *Shelby County*: The New Toolkit
9. The Big Lie, the Fake-Elector Scheme, and January 6 as Case Study
10. Disinformation, AI, and the Information War on Voters

**PART THREE — THE ADMINISTRATION AND THE 2026 MIDTERMS**
11. Executive Pressure on Election Administration, 2025–2026
12. Federal Data, Federal Leverage: The National Voter List Fight
13. Litigation Tracker: What Has Been Blocked, What Has Not
14. The November 2026 Midterms: District by District, State by State
15. What Election Officials Themselves Are Warning About

**PART FOUR — THE WORLD IS WATCHING, AND SO SHOULD WE**
16. Competitive Authoritarianism: Hungary, Venezuela, and the Global Playbook
17. Freedom House, V-Dem, and the Twenty-Year Democratic Recession
18. Why "It Can't Happen Here" Is Not a Strategy

**PART FIVE — WHAT FAIR ELECTIONS REQUIRE**
19. The Reform Menu: Independent Commissions, Ranked Choice, and Federal Floors
20. What Citizens, Officials, and Technologists Can Actually Do

**PART SIX — THE MACHINE WE ARE BUILDING**
21. EIGE: An Election Integrity Governance Engine
22. What EIGE Detects, What It Does Not, and Why That Honesty Matters
23. Closing: Civilization Above Kings, Human First

**APPENDICES**
- Appendix A: Glossary of Election-Law and Election-Security Terms
- Appendix B: Timeline of Key Events, 2013–2026
- Appendix C: Numbered Source Citations
- Appendix D: EIGE Technical Cross-Reference
- Appendix E: Gate Certification and Editorial Method

---

## PART ONE — FIRST PRINCIPLES

## 1. What "Free and Fair" Actually Means

"Free and fair" is not a slogan. Election-law scholarship and international observation standards (the OSCE/ODIHR election observation handbook, the Carter Center's election standards, and the Council of Europe's Venice Commission Code of Good Practice in Electoral Matters) converge on a compact definition with five load-bearing pillars [Citation 1][Citation 2]:

1. **Universal and equal suffrage** — every eligible citizen can vote, and every vote is weighted equally.
2. **Genuine choice** — more than one viable option exists, and no candidate or party can foreclose competition through legal or administrative means.
3. **Secrecy and safety of the ballot** — voters can vote without fear of retaliation and without their choice being knowable to others.
4. **Transparent and verifiable administration** — the process by which ballots are cast, counted, and certified is auditable by neutral parties, not just trusted on faith.
5. **Peaceful transfer of power** — the losing side accepts the result and transfers authority without violence or obstruction.

Every failure mode catalogued in this book is a failure of one or more of these five pillars. Gerrymandering attacks pillar 2 (genuine choice) by pre-determining outcomes through map design rather than persuasion. Voter suppression attacks pillar 1 (universal suffrage). Disinformation attacks pillars 2 and 3. Executive pressure on state election administration attacks pillar 4. The fake-elector scheme and January 6 attacked pillar 5 directly, on camera, in real time.

It is worth being explicit about a distinction this book maintains throughout: **fraud** (an individual or coordinated group unlawfully casting or altering votes) is a *criminal* problem that, empirically, is tiny in the United States [Citation 3][Citation 4]. **Rigging** (structuring the legal and administrative terms of the contest to predetermine or bias the outcome) is a *structural* problem that is large, well-documented, mostly legal, and far more consequential to actual election outcomes than fraud has ever been [Citation 5][Citation 6]. Conflating the two — using the vanishing rate of the first to justify remedies that primarily suppress lawful voters, while ignoring the well-documented scale of the second — is itself one of the primary rigging techniques this book documents.

---

## 2. A Short, Honest History of Election Rigging in America

American elections have never been a blank slate onto which rigging was newly introduced. Structural manipulation is as old as the republic. A brief, sourced chronology:

- **1787–1870:** The Constitution itself excluded women, most Black Americans (three-fifths compromise, Article I §2), and, in practice, most poor men from the franchise. The 15th Amendment (1870) nominally extended the vote regardless of race — and was almost immediately met with new suppression technology [Citation 7].
- **1877–1965 (Jim Crow era):** Poll taxes, literacy tests, "understanding clauses," grandfather clauses, white primaries, and outright terrorism (Ku Klux Klan violence, the Colfax and Wilmington massacres) systematically disenfranchised Black voters across the South for nearly a century [Citation 7][Citation 8]. This is CONFIRMED history, not contested interpretation — it is documented in Reconstruction-era court records, congressional testimony, and modern historical scholarship housed at institutions including Princeton's Department of History [Citation 8].
- **1965:** The Voting Rights Act (VRA) created Section 5 "preclearance," requiring jurisdictions with a history of discrimination to get federal approval before changing voting procedures. This was the single most effective anti-rigging tool in American history, and its removal is the hinge on which the rest of this book's modern chapters turn [Citation 9].
- **2013:** *Shelby County v. Holder*, 570 U.S. 529 (2013), gutted Section 5 by invalidating the coverage formula (Section 4(b)) that determined which jurisdictions needed preclearance, on the theory that conditions had changed enough that the formula was outdated. Chief Justice Roberts wrote for a 5–4 majority; Justice Ginsburg's dissent — "throwing out preclearance when it has worked and is continuing to work to stop discriminatory changes is like throwing away your umbrella in a rainstorm because you are not getting wet" — is one of the most cited lines in modern election-law scholarship [Citation 9][Citation 10].
- **2013–2024:** In the years immediately following *Shelby County*, numerous previously covered jurisdictions passed new voting restrictions — often within months. The Brennan Center for Justice has tracked this pattern continuously since 2013 [Citation 10][Citation 11].
- **2019:** *Rucho v. Common Cause*, 588 U.S. 684 (2019), held that partisan gerrymandering claims are "nonjusticiable political questions" the federal courts cannot resolve — while explicitly leaving *racial* gerrymandering claims and state-court/state-constitutional challenges available. This single decision is the legal foundation for nearly everything in Part Two of this book [Citation 12].
- **2020–2021:** The "Big Lie" — the false claim that the 2020 presidential election was stolen through fraud — was rejected by more than 60 state and federal courts, by Trump's own DOJ and DHS cybersecurity officials, and by every state's certified canvass, yet became the organizing narrative for a fake-elector scheme and the January 6, 2021 attack on the Capitol [Citation 13][Citation 14][Citation 15].
- **2025–2026:** Mid-decade partisan redistricting (Texas, California, Missouri, and others), a wave of executive orders touching federal election administration, and DOJ requests for state voter-roll data reignite the structural debate this book covers in Part Three [Citation 16][Citation 17][Citation 18].

The throughline across 150+ years is consistent: **when direct disenfranchisement becomes illegal or politically toxic, rigging migrates to subtler, more legally defensible mechanisms** — literacy tests became voter-ID laws; white primaries became partisan gerrymanders; preclearance review became a patchwork of after-the-fact litigation that structurally favors whoever controls the map in the meantime.

---

## 3. How Elections Are Actually Cheated: A Taxonomy

This chapter is deliberately clinical. Understanding the mechanisms is the precondition for detecting and stopping them.

### 3.1 Retail fraud (individual-level)
Impersonation at the polls, double voting, ineligible voting (e.g., by noncitizens or felons where disqualified). Multiple large academic studies — including a comprehensive Arizona State University review of 4,700 criminal fraud cases going back decades — find this occurs at a rate of a few thousandths of one percent of ballots cast, nationally [Citation 3][Citation 4]. It is real, it is prosecuted when found, and it is not the mechanism by which election *outcomes* are altered at scale.

### 3.2 Wholesale/administrative fraud
Ballot-box stuffing, altering tabulation totals, discarding valid ballots, and falsifying certification — historically documented (e.g., 19th-century urban political machines, and isolated modern cases such as the 2018 NC-09 absentee-ballot harvesting scandal that led to a new election being ordered) [Citation 19]. This is rare in the modern era specifically *because* of the chain-of-custody and paper-trail requirements most U.S. jurisdictions now use — which is precisely the category of protection EIGE (Part Six) is engineered to strengthen further.

### 3.3 Structural/legal rigging
This is the dominant modern mechanism and the primary subject of this book:
- **Redistricting manipulation** ("packing" opponents into few districts, "cracking" them across many) — Chapter 4.
- **Access-restriction laws** (ID requirements, roll purges, reduced early voting, precinct closures) calibrated to disproportionately burden specific demographic groups — Chapter 8.
- **Administrative pressure and resourcing** (underfunding election offices in target areas, replacing experienced nonpartisan officials with partisan loyalists, threatening certification officials) — Chapters 11–13 [Citation 20][Citation 21].
- **Information warfare** (disinformation about voting procedures, deadlines, or locations targeted at specific communities) — Chapter 10 [Citation 22].

### 3.4 Regime-level manipulation (the "competitive authoritarian" pattern)
The comparative-politics literature (Levitsky & Way's foundational *Competitive Authoritarianism*, and subsequent Freedom House/V-Dem tracking) describes a globally recurring pattern: elections continue to be held, and continue to be somewhat competitive, but incumbents systematically tilt the field through judicial capture, media concentration, selective law enforcement against opposition figures, and rule changes timed just before elections — while avoiding the overt fraud that would trigger international condemnation [Citation 23][Citation 24][Citation 25]. Chapter 16 examines this pattern in Hungary and Venezuela as case studies and asks, directly and without euphemism, how many of its diagnostic markers are currently present in the United States.

---

## PART TWO — THE MODERN MACHINERY OF DISTORTION

## 4. Gerrymandering: The Legal Weapon That Doesn't Need to Break the Law

Gerrymandering — named for Massachusetts Governor Elbridge Gerry's 1812 salamander-shaped district — is the deliberate drawing of electoral district boundaries to advantage one group over another. It works through two complementary techniques: **packing** (concentrating the opposing party's voters into as few districts as possible, conceding those seats but wasting the opposition's surplus votes) and **cracking** (splitting the opposing party's voters across many districts so they fall short of a majority everywhere) [Citation 26][Citation 27].

Modern gerrymandering is not the crude hand-drawn maps of the 19th century. It is produced with redistricting software (Maptitude, Dave's Redistricting App, and proprietary partisan tools) that can model the partisan lean of a proposed map down to the individual census block, optimizing for a target seat count with mathematical precision that earlier generations of map-drawers could not achieve [Citation 27][Citation 28]. The Brennan Center's structural analysis is direct: gerrymandering and voter suppression are not separate problems but "work hand-in-hand" to dilute the voting power of targeted communities, especially where one party controls the entire redistricting process without a independent check [Citation 6][Citation 11].

## 5. *Rucho v. Common Cause* and the Federal Courts' Retreat

In *Rucho v. Common Cause*, 588 U.S. 684 (2019), the Supreme Court held 5–4 that federal courts have no role in policing partisan gerrymandering, because there is no "limited and precise standard" for distinguishing permissible political line-drawing from excessive partisanship — making such claims "political questions" beyond judicial reach [Citation 12]. Chief Justice Roberts's majority opinion did **not** hold that partisan gerrymandering is constitutional or good; it held that federal courts cannot adjudicate it, and left the door open to (a) racial-gerrymandering claims under the Equal Protection Clause and the VRA, and (b) state constitutional and state-court claims, which several states (Pennsylvania, North Carolina, at various points) have since used to strike down maps under their own constitutions [Citation 12][Citation 29].

The practical effect: partisan gerrymandering is now checked almost entirely by (1) state courts applying state constitutions, (2) independent redistricting commissions where voters have created them by ballot initiative (California, Michigan, Colorado, Arizona), and (3) political retaliation — the "arms race" dynamic examined next [Citation 29][Citation 30].

## 6. The 2025–2026 Mid-Decade Redistricting War: Texas, California, and the Map Arms Race

Redistricting normally happens once per decade, after the census. In 2025, at the direct urging of President Trump, the Texas legislature undertook an unusual **mid-decade** redraw of its congressional map — explicitly to manufacture up to five additional Republican U.S. House seats ahead of the 2026 midterms, rather than waiting for the post-2030 census [Citation 16][Citation 31]. The new map reshaped districts in Houston, Dallas, and South Texas specifically to reduce the electoral power of Black and Latino voters who had historically been able to elect their preferred candidates in those seats [Citation 16][Citation 32].

Texas Democratic legislators temporarily left the state in an attempt to deny the legislature a quorum and block the vote; Republican state leaders responded by threatening to have the absent members expelled or criminally charged for the walkout — itself an escalation without close recent precedent in state legislative practice [Citation 31][Citation 33].

Civil rights organizations sued, arguing the map was an intentional racial gerrymander violating the Fourteenth and Fifteenth Amendments and Section 2 of the VRA. A federal three-judge panel agreed and blocked the map for the 2026 cycle, finding evidence of racially discriminatory intent [Citation 16][Citation 32]. In December 2025, the **U.S. Supreme Court, in a 6–3 decision, allowed the Texas map to take effect for 2026 anyway**, invoking the *Purcell* principle (courts should be reluctant to change election rules close to an election) and characterizing the map as partisan — not racial — gerrymandering, which *Rucho* leaves outside federal judicial reach even where a partisan motive is admitted [Citation 16][Citation 32][Citation 34]. The dissent was sharp: allowing a map a lower court found to be racially discriminatory to govern a national election is, in the dissenting justices' own characterization, sanctioning the discrimination it purports merely to decline to review [Citation 32][Citation 34].

Texas's move triggered a national response. California placed **Proposition 50** before voters to authorize new, Democratic-leaning congressional maps explicitly designed to offset Texas's gains — an unusual move for a state that otherwise uses an independent redistricting commission, justified by its backers as a temporary, defensive countermeasure rather than a permanent abandonment of nonpartisan redistricting [Citation 17][Citation 35]. Missouri, Florida, North Carolina, Ohio, Utah, Louisiana, Alabama, and Tennessee also saw new mid-decade redistricting fights in the same window, and at least one of those maps (Missouri's) was reverted by courts before the 2026 cycle, blunting the anticipated Republican gain there [Citation 17][Citation 36].

Nonpartisan analysis (including from the Brookings Institution) concludes the net effect of the 2025–2026 redistricting wave is smaller than either side initially hoped — shifting Latino voter trends in South Texas and the countervailing California map appear to be offsetting much of the intended Texas GOP gain — but the **process itself**, not just its numeric yield, is the documented harm: an unprecedented national cycle of mid-decade, explicitly partisan-motivated redistricting, endorsed by the nation's highest court over a lower court's finding of racial discrimination, has now been normalized as an available tool for whichever party controls a state government mid-decade [Citation 16][Citation 36].

## 7. The Supreme Court, the Purcell Principle, and *Louisiana v. Callais*

The *Purcell* principle — from *Purcell v. Gonzalez*, 549 U.S. 1 (2006) — holds that federal courts should be cautious about changing election rules in the period close to an election, because judicial intervention can itself cause voter confusion. It is a sensible administrative-caution doctrine in isolation. In practice, as applied in the Texas redistricting litigation and in the pending *Louisiana v. Callais* line of cases concerning Section 2 VRA redistricting claims, *Purcell* has increasingly functioned as a one-way ratchet: it is invoked to **preserve** a newly enacted, contested map rather than to preserve the status quo, because the "new" map is what will be in effect by the time any full-merits review could occur [Citation 32][Citation 34][Citation 37]. This is a CONTESTED point among legal scholars — some view it as a neutral, timing-driven doctrine; others (including the *Rucho* and Texas-map dissents) view it as functionally biased toward whichever map is passed last and litigated up against an election deadline. Both positions are represented in the scholarly literature and are presented here as genuinely disputed, not resolved.

## 8. Voter Suppression After *Shelby County*: The New Toolkit

Since *Shelby County* (2013) removed federal preclearance, the Brennan Center's continuously updated tracking documents a consistent toolkit of restrictions disproportionately burdening the same communities Section 5 preclearance previously protected [Citation 10][Citation 11][Citation 38]:

- **Strict photo-ID requirements** that disproportionately affect voters who are older, poorer, or more likely to be non-white and less likely to hold a qualifying ID.
- **Aggressive voter-roll purges**, sometimes using flawed matching algorithms (e.g., the Crosscheck program) that generate large numbers of false-positive removals.
- **Reduced early voting windows and polling-place closures**, concentrated in jurisdictions with larger Black and Latino populations.
- **Mail-ballot restrictions** (signature-matching rejections without cure processes, reduced drop-box availability).
- **Mass voter challenges** — a newer tactic in which organized groups file large batches of individual eligibility challenges against voters, which election officials must process even when challenge rates of confirmed ineligibility are extremely low [Citation 38].

None of these mechanisms requires a single fraudulent ballot to shift an outcome. They work by raising the transaction cost of voting for targeted populations until turnout gaps do the rest.

## 9. The Big Lie, the Fake-Elector Scheme, and January 6 as Case Study

The 2020 "Big Lie" — the claim that the presidential election was stolen through systemic fraud — offers the clearest CONFIRMED case study in this book of an attempted rigging operation aimed squarely at pillar 5 (peaceful transfer of power). More than 60 state and federal court challenges were filed and rejected, including by judges appointed by the same president making the claims; DHS's own Cybersecurity and Infrastructure Security Agency called it "the most secure election in American history"; and the Justice Department under Attorney General William Barr found no fraud on a scale that could have changed the outcome [Citation 13][Citation 14].

Despite this, a coordinated slate of fake presidential electors was organized in seven contested states, and pressure was applied to state officials (including the recorded call to Georgia's Secretary of State) and to the Vice President to reject or delay certification of the actual electoral count — culminating in the January 6, 2021 attack on the U.S. Capitol during the joint session convened to count electoral votes [Citation 14][Citation 15]. This sequence — false claim, litigation loss, extralegal pressure on certifying officials, and ultimately physical obstruction of the certification process itself — is CONFIRMED by criminal convictions, congressional investigation records, and contemporaneous documentary evidence, and it stands as the starkest domestic illustration of why pillar 5 (peaceful transfer of power) cannot be taken for granted even in a mature democracy.

## 10. Disinformation, AI, and the Information War on Voters

Modern election disinformation targets voters directly rather than election machinery: false claims about voting deadlines, false claims that voting by mail is unsafe or that one's registration has been cancelled, and AI-generated synthetic media (deepfake robocalls, fabricated candidate statements) designed to suppress turnout or mislead specific communities [Citation 22][Citation 39]. Unlike ballot-tampering, this category of attack is largely outside what any cryptographic chain-of-custody system can address — it requires media literacy, rapid-response fact-checking infrastructure, and platform-level content moderation, and this book does not claim otherwise.

---

## PART THREE — THE ADMINISTRATION AND THE 2026 MIDTERMS

## 11. Executive Pressure on Election Administration, 2025–2026

Election administration in the United States is constitutionally a **state** function (Article I, Section 4 gives states the primary authority to set the "Times, Places and Manner" of elections, subject to congressional override for federal elections) [Citation 40]. Since 2025, multiple executive orders and DOJ actions have tested the boundaries of federal involvement in that state-run system:

- Executive orders seeking to mandate documentary proof-of-citizenship for federal voter registration, to involve the U.S. Postal Service in eligibility verification, and to restrict mail-in ballot acceptance windows have been issued and substantially litigated, with several provisions blocked or stayed by federal courts as exceeding presidential authority over a domain the Constitution assigns to the states and Congress [Citation 18][Citation 41][Citation 42].
- The Brennan Center's continuously updated tracker on the status of the 2025 anti-voting executive order documents which provisions remain enjoined, which have been narrowed, and which continue to be litigated as of the most recent update — readers should consult that live tracker directly for the current docket status, since litigation postures change frequently [Citation 41].

This is a CONTESTED area politically but not legally uncertain in its constitutional structure: courts across the ideological spectrum have repeatedly held that the President cannot unilaterally rewrite state or congressional election rules by executive order, and the administration's orders have been challenged and, in significant part, enjoined on exactly that basis [Citation 41][Citation 42].

## 12. Federal Data, Federal Leverage: The National Voter List Fight

Separately, DOJ has sought detailed voter-roll data from multiple states, and advocacy and state-official groups have raised two distinct concerns, both REPORTED and under active litigation: first, that assembling a centralized federal voter database compiled from disparate state systems (which use different data standards and update cadences) risks generating large numbers of false-positive "ineligible voter" flags — the same structural failure mode as earlier state-level cross-check purge programs, at national scale; second, that the data-request authority itself is being used as leverage — with implied or stated threats to withhold funding, certification cooperation, or favorable treatment from states that decline to comply — raising separation-of-powers and Tenth Amendment concerns given states' constitutional primacy over election administration [Citation 20][Citation 43][Citation 44]. Multiple states have filed suit to block compliance, and as of this writing several of those cases remain active; consult the litigation tracker in Chapter 13 and the cited trackers directly for current status [Citation 43][Citation 44].

## 13. Litigation Tracker: What Has Been Blocked, What Has Not

As a live-litigation snapshot (subject to change; consult primary trackers for updates):

| Action | Status as tracked | Primary source |
|---|---|---|
| 2025 proof-of-citizenship / mail-ballot executive order provisions | Multiple provisions enjoined or narrowed by federal courts; appeals ongoing | Brennan Center EO tracker [Citation 41] |
| Texas 2025 mid-decade congressional map | Found racially discriminatory by 3-judge panel; stayed and allowed to take effect for 2026 by SCOTUS (6–3) under *Purcell* | SCOTUS docket / Brennan Center [Citation 16][Citation 32][Citation 34] |
| California Proposition 50 responsive map | Approved by voters; in effect for 2026 | Ballotpedia / state election records [Citation 17][Citation 35] |
| DOJ requests for state voter-roll data | Contested; multiple states suing to block or limit compliance | Protect Democracy litigation tracker [Citation 43][Citation 44] |
| Missouri mid-decade map | Reverted to prior map by court order | Common Cause redistricting tracker [Citation 17][Citation 36] |

This table is a snapshot, not a permanent record — election litigation moves quickly, and the appendix source list should be consulted directly for the current docket status of any item.

## 14. The November 2026 Midterms: District by District, State by State

As of September 2026 nonpartisan forecasting aggregators place the generic House picture roughly as follows, with the caveat that these are probabilistic forecasts, not predictions, and will continue to move before Election Day [Citation 45][Citation 46]:

- **House:** Non-incumbent-party gains in midterms are the historical norm; current aggregator modeling shows Democrats favored for a majority but with dozens of genuine toss-up seats, several of them directly reshaped by the 2025–2026 redistricting wave (competitive districts have shifted in Texas, Missouri, California, North Carolina, and Ohio in particular) [Citation 45][Citation 46].
- **Senate:** Republicans retain a structural advantage from the 2026 map (which states have Senate seats up), but several races previously rated safe (Michigan, Iowa, Kansas) have moved toward competitive, and Texas's Senate race is more contested than the state's presidential lean would suggest [Citation 45][Citation 46].
- **Redistricting's net electoral effect:** Nonpartisan analysis from the Brookings Institution concludes the Texas map is likely to net Republicans fewer seats than the architects intended — plausibly two rather than five — both because of shifting Latino voter behavior in the newly drawn districts and because California's responsive map offsets a meaningful share of the intended gain [Citation 16][Citation 36]. **The redistricting fight's significance is not primarily in its net seat count; it is in the precedent it sets** that mid-decade, admittedly partisan-motivated redistricting — including maps a federal court found racially discriminatory — is now a normalized, judicially unreviewable tool available to any state government controlling both chambers and the governorship mid-decade.

Readers should treat any specific numeric forecast in this chapter as perishable; by the time this book is read, updated ratings from Sabato's Crystal Ball, the Cook Political Report, and similar aggregators will supersede the September 2026 snapshot given here. What will not change by Election Day is the structural picture developed in Chapters 4–13: the maps in several states were drawn mid-cycle for openly partisan advantage, at least one was found racially discriminatory by a federal court before being allowed to stand, and the administrative and legal fights over federal-versus-state control of election rules were still unresolved heading into the vote.

## 15. What Election Officials Themselves Are Warning About

Perhaps the most under-covered fact in this entire debate is that the loudest alarms are not coming from partisan advocacy groups on either side — they are coming from career, often Republican and Democratic alike, state and local election administrators, who report that the **compounding effect** of litigation uncertainty, shifting federal guidance, threats and harassment directed at election workers since 2020, and chronic underfunding is the actual near-term risk to smooth election administration — more so than any single rigging mechanism in isolation [Citation 20][Citation 47]. Multiple studies and surveys of local election officials (Brennan Center, Bipartisan Policy Center) document elevated turnover, recruitment difficulty, and burnout among the nonpartisan professionals who actually run American elections at the county level since 2020 [Citation 47]. A system that depends on experienced, protected, well-resourced nonpartisan administrators is only as resilient as the pipeline of people willing to do that job under current conditions.

---

## PART FOUR — THE WORLD IS WATCHING, AND SO SHOULD WE

## 16. Competitive Authoritarianism: Hungary, Venezuela, and the Global Playbook

Steven Levitsky and Lucan Way's *Competitive Authoritarianism* (Cambridge University Press, 2010) coined the term for regimes where meaningful elections occur, opposition parties exist and sometimes win seats, but the incumbent has tilted the playing field so thoroughly through control of courts, media, and administrative machinery that genuine turnover becomes structurally difficult without becoming formally impossible [Citation 23]. Two case studies, both CONFIRMED by extensive comparative-politics literature and international monitoring:

**Hungary**, under Viktor Orbán's Fidesz party since 2010, is the textbook modern example: the constitution and electoral law were rewritten to entrench the ruling party's advantage; district boundaries were redrawn to favor Fidesz; a large share of national media came under direct or indirect party-aligned ownership; and judicial appointments were reshaped to reduce independent checks on executive power. Elections continue, and Fidesz has lost some individual races, but international election-monitoring assessments (OSCE/ODIHR) have repeatedly found the *playing field*, not the vote count on election day itself, to be the core problem [Citation 24][Citation 48].

**Venezuela**, under Hugo Chávez and then Nicolás Maduro, represents a more advanced stage on the same spectrum: viable opposition candidates and parties have been disqualified or jailed ahead of elections, independent electoral institutions have been hollowed out over two decades, and international observers (including the Carter Center, which had monitored Venezuelan elections for decades) withdrew or sharply downgraded their assessment of the 2024 presidential election process. Freedom House and V-Dem now classify Venezuela as an electoral authoritarian regime rather than a democracy with flaws [Citation 25][Citation 49].

## 17. Freedom House, V-Dem, and the Twenty-Year Democratic Recession

Freedom House's *Freedom in the World 2026* report documents global freedom declining for the twentieth consecutive year, with 54 countries registering declines in political rights and civil liberties in the most recent reporting period against only 35 recording improvements — and explicitly flags reversals in **established** democracies, not only fragile ones, including the United States, Bulgaria, and Italy [Citation 24][Citation 50]. The V-Dem Institute's 2026 Democracy Report independently finds that roughly a quarter of the world's countries are undergoing some form of "autocratization," and specifically characterizes the recent U.S. decline in its composite liberal-democracy index as unprecedented in magnitude for an established democracy of this age and size [Citation 25][Citation 51].

Both organizations identify a consistent authoritarian-consolidation toolkit, independent of any single country: rewriting election rules to favor incumbents (of which gerrymandering is the U.S. domestic analogue), weakening the accountability mechanisms (courts, legislatures, free press) that would otherwise check executive overreach, and suppressing or intimidating civil society and opposition figures ahead of a vote [Citation 24][Citation 25]. Naming this pattern accurately when its markers appear domestically is not partisanship — it is applying the same diagnostic tools, consistently, regardless of which country or party they implicate.

## 18. Why "It Can't Happen Here" Is Not a Strategy

Every regime examined in Chapter 16 held elections throughout its democratic decline. Nobody woke up to a single day when democracy visibly "ended." The Hungarian and Venezuelan cases both show a slow accumulation of individually defensible-sounding actions — a redistricting here, a data request there, a funding cut to an inconvenient watchdog, a court appointment, a media consolidation — each of which, examined alone, a reasonable person could argue was within normal democratic bounds. The comparative lesson this book draws, directly and without hedging, is that the correct response to any individual action from Chapters 4–13 is not "is this one thing, by itself, a coup" — it almost never is — but "does this fit the accumulating pattern documented across an entire democracy's decline elsewhere, and what is the cost of waiting to find out."

---

## PART FIVE — WHAT FAIR ELECTIONS REQUIRE

## 19. The Reform Menu: Independent Commissions, Ranked Choice, and Federal Floors

None of the mechanisms in this book are unsolvable. A menu of structural reforms already exists, tested in various U.S. states and internationally, each targeting a specific chapter of this book:

- **Independent redistricting commissions** (California, Michigan, Colorado, Arizona) remove map-drawing from the legislature entirely, directly countering Chapter 4–6's mechanism [Citation 30][Citation 52].
- **Restoring a modernized VRA preclearance formula** (the John Lewis Voting Rights Advancement Act, repeatedly introduced in Congress since 2019 but not yet enacted as of this writing) would directly reverse the *Shelby County* gap identified in Chapter 8 [Citation 9][Citation 53].
- **Federal minimum floors for early voting, mail-ballot access, and polling-place adequacy** would reduce the state-by-state variance that Chapter 8's suppression toolkit exploits [Citation 11][Citation 53].
- **Ranked-choice and proportional-representation reforms**, used in Alaska, Maine, and dozens of U.S. cities, reduce the payoff of both gerrymandering and hyper-polarized turnout suppression by making "genuine choice" (pillar 2) less winner-take-all [Citation 54].
- **Statutory protection and funding for nonpartisan election administrators**, directly addressing Chapter 15's warning about the human pipeline running the system [Citation 47].

## 20. What Citizens, Officials, and Technologists Can Actually Do

This book does not end in fatalism. Concrete, non-partisan actions exist at every level: voters can verify registration and know deadlines directly from state election offices rather than social media; citizens can serve as poll workers, addressing the recruitment shortfall documented in Chapter 15; state legislators can adopt independent commissions by ballot initiative where their state constitution allows it; and technologists — which is where this book's authorship base sits most directly — can build tools that make the *administrative* layer of elections (chain of custody, tabulation integrity, audit trails) more transparent and harder to tamper with undetected, which is the specific, narrow, and honestly-scoped contribution described in Part Six.

---

## PART SIX — THE MACHINE WE ARE BUILDING

## 21. EIGE: An Election Integrity Governance Engine

AxiomZero's EIGE (Election Integrity Governance Engine, v21.0.0, Phase 1-B complete, 449 tests passing as of its last verified internal regression) is a deterministic, mathematically verifiable chain-of-custody engine for the ballot-counting and tabulation layer of an election [Citation 55]. It is explicitly labeled, in its own repository documentation, as a **🔵 ADJACENT TRACK — governance application, not a physics claim**, and its authors are explicit that the underlying Unitary Manifold physics constants it borrows (the winding number 5, and k_CS = 74) function here purely as **engineering parameters** — seeds for a path-dependent rolling hash, shard-placement parameters for redundant storage, and anchors for zero-knowledge certificates — whose validity as engineering choices does not require anyone to accept the cosmological physics they originated from [Citation 55].

The core idea, stated in EIGE's own design language: *an election is a field evolution, not a database.* Rather than treating a tally as a static number that is checked after the fact by statistical sampling (the current best-practice standard, called a risk-limiting audit, which is itself a genuine, valuable, but inherently *probabilistic and retroactive* tool), EIGE encodes the entire sequence of ballots as a continuously computed mathematical invariant, verified in real time. Any structural manipulation of that sequence — stuffing, retroactive deletion, reordering, or an unauthorized administrative override — produces an immediate, deterministic cryptographic deviation, not merely a statistical anomaly that might or might not be flagged by a sample [Citation 55].

Architecturally, EIGE operates in three tiers: at the **county tier**, each ballot integer is folded into a Chern-Simons rolling hash and split across eight redundant shards, with no raw ballot data ever leaving the county; at the **state tier**, cross-county "braid sync" aggregates county certificates and emits a Holon Zero integrity certificate; at the **federal tier**, only zero-knowledge OSCAL 1.5.0 compliance certificates are exposed — any attempt to query raw ballot data at the federal tier raises an explicit `RawDataAccessAttempt` exception by design [Citation 55]. EIGE maps its controls to NIST VVSG 2.0 (the federal voting-system standard) and NIST SP-800-53 Rev. 5 (federal security controls), and its test suite (449 tests as of the last verified internal count) exercises the full county-to-federal pipeline, including a synthetic end-to-end demo simulating five counties and 5,000 ballots [Citation 55].

## 22. What EIGE Detects, What It Does Not, and Why That Honesty Matters

In keeping with this book's insistence on refusing false balance in one direction, intellectual honesty requires refusing false confidence in the other. EIGE's own documentation states its limitations directly, and this book repeats them without softening [Citation 55]:

**What EIGE detects:** ballot stuffing, retroactive deletion, sequence reordering, unauthorized administrative override of the tabulation pipeline, infrastructure attacks against the tabulation system itself (ransomware, power loss, via 8-shard holographic persistence and inter-county peer replication), floating-point precision manipulation (via an independent 512-bit out-of-band audit worker), and participation suppression at the county level (via a "Freedom Floor" kill-switch design) [Citation 55].

**What EIGE does not detect:** manipulation of the *physical ballot itself* before it enters the scanner (a printing, distribution, or voter-coercion problem outside a tabulation engine's reach); compromised scanner hardware that emits false integers into an otherwise-intact pipeline; a set of colluding human operators who suppress the audit trail collectively before EIGE's cryptographic layer is activated; and any attack occurring below the HMAC-SHA-512 key-management layer itself [Citation 55].

This is the correct scope for a cryptographic tabulation-integrity tool, and it is also the correct scope limit for this book's own claims about technology's role in election integrity: **EIGE is a narrow, honest answer to one specific structural vulnerability — undetected tampering with the ballot-counting sequence.** It has no answer to gerrymandering (Chapters 4–7), no answer to voter suppression (Chapter 8), no answer to disinformation (Chapter 10), and no answer to executive or administrative pressure on election officials (Chapters 11–13). Those are legal, legislative, and civic problems, and pretending a cryptographic engine could solve them would repeat exactly the kind of overclaiming this book has spent twenty chapters criticizing in others.

## 23. Closing: Civilization Above Kings, Human First

Elections are the only mechanism a large, diverse, modern society has ever devised for transferring power without violence. Every chapter of this book — from Reconstruction-era terror, through *Shelby County*, through the fake-elector scheme, through the 2025–2026 redistricting war, through Hungary and Venezuela — is a variation on a single, ancient temptation: that whoever currently holds power should get to keep it, by whatever legally defensible or merely undetected means are available, rather than earn its renewal freely and fairly in front of the people it governs.

This book takes a position, and states it plainly rather than hiding it behind false neutrality: fair elections are not a partisan preference. They are the precondition for every other right this book's authors, and its readers, hold. A civilization that lets the mechanism of consent be quietly rigged has not preserved order — it has only postponed the reckoning, and made it larger. AxiomZero was not built to adjudicate which party deserves to win any specific election. It was built, in this narrow and honestly-scoped corner of its work, to make sure that when the votes are counted, the count itself can be trusted on mathematics rather than on faith — because in the end, the health of a free people depends less on who wins any single election than on whether every citizen can still believe, with evidence rather than hope, that the next one will be theirs to decide.

---

## APPENDIX A: GLOSSARY OF ELECTION-LAW AND ELECTION-SECURITY TERMS

- **Cracking** — splitting a group's voters across many districts so they fall short of a majority in each.
- **Packing** — concentrating a group's voters into as few districts as possible to waste their surplus votes.
- **Preclearance** — the pre-2013 VRA requirement that certain jurisdictions get federal approval before changing voting rules (Section 5).
- **Purcell principle** — the doctrine counseling judicial restraint on election-rule changes close to an election (*Purcell v. Gonzalez*, 2006).
- **Risk-limiting audit (RLA)** — a statistical, sampling-based post-election audit method; probabilistic, not a mathematical proof.
- **Competitive authoritarianism** — a regime type where elections are held and somewhat competitive, but the playing field is systematically tilted toward the incumbent.
- **Chain of custody** — the documented, unbroken sequence of possession and handling of a ballot from casting to certification.
- **OSCAL** — Open Security Controls Assessment Language, a NIST machine-readable compliance-documentation standard used in EIGE's federal-tier certificates.
- **Fake elector scheme** — the 2020 effort to submit slates of electors for a losing candidate in contested states, in an attempt to create a false record for Congress to certify.

## APPENDIX B: TIMELINE OF KEY EVENTS, 2013–2026

| Year | Event |
|---|---|
| 2013 | *Shelby County v. Holder* guts VRA Section 5 preclearance |
| 2018 | NC-09 election voided over absentee-ballot fraud scheme |
| 2019 | *Rucho v. Common Cause* holds partisan gerrymandering nonjusticiable federally |
| 2020 | Presidential election; more than 60 court challenges to results rejected |
| 2021 | January 6 Capitol attack during electoral vote certification |
| 2025 | Executive orders on federal election administration; Texas mid-decade redistricting begins |
| 2025 (Dec.) | SCOTUS allows Texas map to stand for 2026 under *Purcell*, 6–3 |
| 2025–2026 | California Prop 50, Missouri map reversion, multi-state redistricting wave |
| 2026 | November midterms held under contested maps and ongoing federal-state litigation |

## APPENDIX C: NUMBERED SOURCE CITATIONS

[Citation 1] OSCE Office for Democratic Institutions and Human Rights (ODIHR), *Election Observation Handbook*, 6th ed.

[Citation 2] Council of Europe Venice Commission, *Code of Good Practice in Electoral Matters* (2002).

[Citation 3] Richman, Chattha & Earnest / subsequent replications; see also Justin Levitt, "The Truth About Voter Fraud," Brennan Center for Justice (2007, updated).

[Citation 4] News21/Arizona State University, comprehensive review of documented U.S. voter-fraud cases.

[Citation 5] Brennan Center for Justice, "The New Voter Suppression," https://www.brennancenter.org/our-work/research-reports/new-voter-suppression.

[Citation 6] Brennan Center for Justice, "Gerrymandering Explained," https://www.brennancenter.org/our-work/research-reports/gerrymandering-explained.

[Citation 7] Princeton University, Department of History, "Voter Suppression in U.S. Elections," https://history.princeton.edu/about/publications/voter-suppression-us-elections.

[Citation 8] National Council of Negro Women, Policy Brief, "Drawn Out and Locked Out: How Gerrymandering and Voter Suppression Threaten American Democracy" (2026).

[Citation 9] Voting Rights Act of 1965, 52 U.S.C. § 10301 et seq.; *Shelby County v. Holder*, 570 U.S. 529 (2013).

[Citation 10] *Shelby County v. Holder*, 570 U.S. 529 (2013), Ginsburg, J., dissenting.

[Citation 11] Brennan Center for Justice, "Voter Suppression in 2020," https://www.brennancenter.org/sites/default/files/2021-08/2021_08_Racial_Voter_Suppression_2020.pdf.

[Citation 12] *Rucho v. Common Cause*, 588 U.S. 684 (2019).

[Citation 13] U.S. Department of Justice, statements of Attorney General William Barr, December 2020; CISA joint statement of the Election Infrastructure Government Coordinating Council, November 12, 2020 ("the most secure in American history").

[Citation 14] House Select Committee to Investigate the January 6th Attack on the United States Capitol, Final Report (2022).

[Citation 15] Fulton County, Georgia grand jury indictment and related fake-elector-scheme prosecutions, 2023–2024.

[Citation 16] Ballotpedia, "Redistricting in Texas ahead of the 2026 elections," https://ballotpedia.org/Redistricting_in_Texas_ahead_of_the_2026_elections.

[Citation 17] Common Cause, "The Latest on Mid-Decade Redistricting: Texas Update," https://www.commoncause.org/texas/resources/the-latest-on-mid-decade-redistricting-texas-update/.

[Citation 18] Protect Democracy, "Voting rights group seeks ruling to prevent federal interference in 2026 midterms," https://protectdemocracy.org/work/voting-rights-federal-interference-2026-midterms/.

[Citation 19] North Carolina State Board of Elections, findings and new-election order, NC-09 (2019).

[Citation 20] Protect Democracy, "Challenging the Trump administration's threats to voting rights, privacy, and elections," https://protectdemocracy.org/work/trump-administration-threat-voting-rights-privacy-elections/.

[Citation 21] Brennan Center for Justice, "The Trump Administration's Campaign to Undermine the Next Election," https://www.brennancenter.org/our-work/research-reports/trump-administrations-campaign-undermine-next-election.

[Citation 22] Center for an Informed Public / Brennan Center reporting on election disinformation campaigns and AI-generated synthetic media targeting voters.

[Citation 23] Levitsky, Steven, and Lucan A. Way. *Competitive Authoritarianism: Hybrid Regimes After the Cold War.* Cambridge University Press, 2010.

[Citation 24] Freedom House, *Freedom in the World 2026: The Growing Shadow of Autocracy*, https://freedomhouse.org/report/freedom-world/2026/growing-shadow-autocracy.

[Citation 25] V-Dem Institute, *Democracy Report 2026*, https://v-dem.net/documents/75/V-Dem_Institute_Democracy_Report_2026_lowres.pdf.

[Citation 26] Brennan Center for Justice, "Gerrymandering Explained" (packing/cracking mechanics).

[Citation 27] National Conference of State Legislatures, redistricting technology and software overview.

[Citation 28] Dave's Redistricting App / Maptitude documentation, redistricting-software modeling capability.

[Citation 29] *League of Women Voters of Pennsylvania v. Commonwealth*, 178 A.3d 737 (Pa. 2018) (state constitutional partisan-gerrymandering claim).

[Citation 30] Arizona State Legislature v. Arizona Independent Redistricting Commission, 576 U.S. 787 (2015) (upholding independent redistricting commissions).

[Citation 31] Findlaw, "A Quick Summary of Legal Battles Over Redistricting for 2026," https://www.findlaw.com/legalblogs/federal-courts/a-quick-summary-of-legal-battles-over-redistricting-for-2026/.

[Citation 32] Brennan Center for Justice, "The Supreme Court Messes with Texas's Voting Map," https://www.brennancenter.org/our-work/research-reports/supreme-court-messes-texass-voting-map.

[Citation 33] Contemporaneous Tier-1 reporting on the 2025 Texas legislative walkout and quorum fight (Reuters, AP, Texas Tribune).

[Citation 34] League of Women Voters of Texas, "SCOTUS Allows Texas to Use Racially Gerrymandered Map in 2026 Midterms," https://lwvtexas.org/content.aspx?page_id=5&club_id=979482&item_id=129319.

[Citation 35] Ballotpedia, California Proposition 50 (2025/2026 congressional redistricting measure).

[Citation 36] Brookings Institution, "Texas redistricting plan unlikely to add 5 new Republican seats," https://www.brookings.edu/articles/texas-redistricting-plan-unlikely-to-add-5-new-republican-seats/.

[Citation 37] *Louisiana v. Callais*, pending Supreme Court litigation on Section 2 VRA redistricting claims (docket status current as of compilation date; consult SCOTUSblog for updates).

[Citation 38] Brennan Center for Justice, "Mass Voter Challenges," https://www.brennancenter.org/our-work/research-reports/mass-voter-challenges.

[Citation 39] Center for Democracy and Technology, reporting on AI-generated election disinformation, 2024–2026 cycles.

[Citation 40] U.S. Constitution, Article I, Section 4 (Elections Clause).

[Citation 41] Brennan Center for Justice, "Status of Trump's 2025 Anti-Voting Executive Order," https://www.brennancenter.org/our-work/research-reports/status-trumps-2025-anti-voting-executive-order.

[Citation 42] Katie Couric Media, "How Trump Is Trying to Change Voting for the 2026 Midterms," https://katiecouric.com/news/politics-and-policy/can-trump-change-voting-before-2026-midterms/.

[Citation 43] Protect Democracy litigation tracker on federal voter-data requests and 2026 midterm interference (cited above, Citation 18/20).

[Citation 44] Center for American Progress, "The Trump Administration Is Interfering in the 2026 Midterm Elections to Entrench the Imperial Presidency" and accompanying fact sheet, https://www.americanprogress.org/article/the-trump-administration-is-interfering-in-the-2026-midterm-elections-to-entrench-the-imperial-presidency/.

[Citation 45] Sabato's Crystal Ball, University of Virginia Center for Politics, https://centerforpolitics.org/crystalball/.

[Citation 46] Vote-Scope and Political.org 2026 House/Senate race-rating aggregators (September 2026 snapshot; treat as perishable).

[Citation 47] Bipartisan Policy Center / Brennan Center surveys of local election official turnover and burnout, 2020–2026.

[Citation 48] OSCE/ODIHR election observation mission final reports, Hungary, various cycles 2014–2022.

[Citation 49] Carter Center statements and Freedom House/V-Dem classification of Venezuela as an electoral authoritarian regime, 2024–2026.

[Citation 50] Council on Foreign Relations, "As Democracy Falters Worldwide, Authoritarians Are Winning" (analysis of Freedom House annual report), https://www.cfr.org/articles/freedom-houses-annual-report-shows-the-dire-state-of-democracy-worldwide.

[Citation 51] University of Gothenburg (V-Dem Institute host), "Democratic backsliding reaches western democracies, with U.S. decline unprecedented," https://www.gu.se/en/news/democratic-backsliding-reaches-western-democracies-with-us-decline-unprecedented.

[Citation 52] Arizona Independent Redistricting Commission, Michigan Independent Citizens Redistricting Commission — enabling ballot initiatives and structural design documentation.

[Citation 53] John Lewis Voting Rights Advancement Act, as introduced in the 119th Congress (not enacted as of compilation date).

[Citation 54] FairVote, ranked-choice voting adoption tracker (Alaska, Maine, and U.S. municipalities).

[Citation 55] AxiomZero, `12-AZ-IP/03-eige/README.md`, `BOOK.md`, `ARCHITECTURE.md`, and `COMPLIANCE.md` (this repository) — EIGE v21.0.0 design documentation and internal test-suite status (449 tests passing as of last verified internal regression).

## APPENDIX D: EIGE TECHNICAL CROSS-REFERENCE

For readers who want to go past this book's summary of EIGE and into the engineering itself, the canonical in-repository references are:

- `12-AZ-IP/03-eige/README.md` — system overview, quick start, architecture diagram, NIST compliance mapping.
- `12-AZ-IP/03-eige/BOOK.md` — the 21-chapter full technical and operational reference, including §3 ("The Philosophy: From Physics to Governance") and §17 ("Known Limitations and Open Problems").
- `12-AZ-IP/03-eige/ARCHITECTURE.md` — full system block diagrams.
- `12-AZ-IP/03-eige/COMPLIANCE.md` — NIST VVSG 2.0 / SP-800-53 R5 / OSCAL 1.5.0 mapping.
- `12-AZ-IP/03-eige/src/constants_engineering.py` — a physics-free framing of EIGE's tamper-detection constants, for evaluators who wish to assess the engine without evaluating the Unitary Manifold cosmological framework at all.
- `12-AZ-IP/03-eige/tests/` — the 449-test verification suite (`python -m pytest tests/ -v` from the `03-eige/` directory).

## APPENDIX E: GATE CERTIFICATION AND EDITORIAL METHOD

This piece is passed through the three required gates for Season One PsiCat Literature: it is written to be rigorous and structurally clear without losing the urgency of its subject; it preserves accuracy, epistemic honesty, and a refusal of false balance between documented structural fact and unsubstantiated talking points, while explicitly marking genuinely CONTESTED questions as contested rather than resolved; and it is edited for cross-audience readability so both specialists in election law and general readers can follow the argument and verify it against the numbered sources in Appendix C.

This volume departs from the standard PsiCat Literature convention of a "grounded rewrite" of an existing `/7-OUTREACH/substack/` source: it is an original commission, researched directly from the primary and Tier-1 sources listed above, because no prior substack draft on this subject existed in this repository at the time of commissioning.

---

*Research direction: **ThomasCory Walker-Pearson**.*
*Research synthesis, source verification, structural analysis, and writing: **PsiCat Ai** (AxiomZero).*
*Compiled: September 2026.*
