# ClimateSOS Product Pathway Adapter Specification

**GitHub project:** [https://github.com/hsbay/ClimateSOS](https://github.com/hsbay/ClimateSOS)
**Author / maintainer:** Shannon A. Fiume (@safiume)
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0), 2026
**Development note:** ClimateSOS was conceived, researched, directed, architected, and developed by Shannon A. Fiume through an iterative human–AI collaboration. OpenAI’s ChatGPT provided AI-assisted drafting, code-generation, implementation assistance, and systems-design iteration under Shannon’s direction.
**Status:** Draft product specification component

---

## 1. Purpose

This specification defines how ClimateSOS represents and evaluates customer/product pathways as structured transition-system inputs.

ClimateSOS must support evaluation of real-world product, company, technology, financial, infrastructure, and customer-decision pathways in addition to generic transition abstractions.

A customer/product pathway may involve a specific technology, industrial process, clean-fuel product, carbon product, methane-abatement pathway, load case, infrastructure service, prospective business logic, transition-finance instrument, fossil-retirement mechanism, or transition-enabling business model. These pathways may affect not only emissions intensity or carbon footprint, but also whether fossil assets, fuels, financing structures, workforce roles and transition pathways, reliability functions, and supply-chain dependencies can be wound down and replaced in time.

ClimateSOS purpose is to show whether a proposed pathway merely decarbonizes an activity in isolation, or whether it contributes to the synchronized transition conditions required for managed fossil exit and operational net zero.

The purpose of this adapter specification is to define how such pathways are translated into ClimateSOS inputs, identity tokens, queues, synchronization tests, guardrail checks, output states, evidence traces, and system-contribution diagnostics.

ClimateSOS must first evaluate the pathway against the ClimateSOS Foundational Charter and applicable guardrail domains. It must then evaluate how the pathway synchronizes with the broader transition system and record whether the pathway preserves, delays, constrains, or diverges from the Playbook’s accelerated ~2037/2038 operational net-zero window.

This adapter does not determine whether a company, product, financial instrument, or proprietary pathway is commercially valid, investment-worthy, policy-ready, or deployable. It structures the pathway for inspection, including whether the pathway supports fossil displacement, fossil retirement, reliability replacement, worker and community transition, and closure of fossil persistence pathways.

---

## 2. Scope

This pattern applies to customer/product pathways that support prospective customer, institutional, financial, workforce, sovereign, or system-decision logic affecting major net-zero pathway changes.

Examples include:

* aviation and transportation fuel production pathways
* methane-abatement pathways
* industrial product pathways
* carbon-storage or carbon-removal-adjacent product pathways
* industrial electrification products or services
* load coordination products
* grid-support or adequacy-support products
* transition-enabling infrastructure products
* circular-materials or waste-utilization products
* transition-finance instruments or financing structures
* fossil-retirement, refinancing-closure, or asset-winddown mechanisms
* workforce transition, retraining, redeployment, or regional just-transition pathways
* sovereign, regional, or municipal transition-planning pathways
* customer-specific deployment pathways that depend on finance, permitting, workforce, feedstock, offtake, or system integration
* other decision pathways that may materially affect a customer’s path to net zero or the global transition to net zero

This pattern applies where a pathway may affect emissions, fossil displacement, fossil retirement, reliability replacement, workforce transition, capital allocation, supply-chain conversion, or closure of fossil persistence pathways.

These patterns should remain abstract enough to avoid exposing proprietary details from any specific company, customer, partner, technology, financial structure, or transition plan.

---

## 3. Non-Scope

This adapter is not intended to:

* disclose proprietary process details
* model a company’s private technical design
* validate a specific commercial claim without evidence
* replace technical due diligence
* replace engineering review
* replace MRV, lifecycle analysis, financial diligence, community review, or regulatory review
* authorize deployment
* recommend investment
* provide procurement instruction

ClimateSOS structures and surfaces pathway evidence. The researcher, reviewer, customer, or domain expert conducts the investigation.

---

## 4. Core Design Principle

A product pathway is fundamentally a synchronization pathway evaluated in two stages:

1. **Foundational Charter Evaluation** — assesses whether the pathway remains inside ClimateSOS’s baseline operating envelope, including guardrails, evidence integrity, human accountability, and system relevance.
2. **System Synchronization Evaluation** — assesses whether the pathway aligns with, contributes to, or interferes with the broader transition system within the required time window.

A product pathway must be evaluated across:

inputs
→ intake identity token assignment
→ product pathway adaptation
→ foundational charter evaluation
→ guardrail checks
→ access queues
→ finance / revenue-certainty queues
→ permitting / authorization queues
→ workforce and execution queues
→ MRV / evidence queues
→ scale-up conditions
→ product outputs
→ system contributions
→ resulting state
→ evidence trace / state history

Identity token assignment is a traceability step, not a validity decision. The pathway becomes valid only after foundational charter evaluation, guardrail resolution, queue evaluation, and resulting-state assignment.

The central question is:

> Does this customer/product pathway, after foundational evaluation, synchronize with the broader transition system in a way that preserves or strengthens the accelerated operational net-zero window, or does it remain unresolved, delayed, harm-bound, weakly connected to fossil displacement, or otherwise unable to make a material system contribution?

---

                 PRODUCT PATHWAY

     Real-world product / customer / project
                      │
                      ▼
     ClimateSOS Intake & Identity Layer
      (identity, provenance, safeguards)
                      │
                      ▼
          Product Pathway Adapter
     (translate, normalize, structure)
                      │
                      ▼
          ClimateSOS Runtime
       (charter + synchronization)
                      │
         Product Output ───────────┐
                                   ▼
             Net Overall System Contribution
                      │
                      ▼
               Resulting State
              ╱       │        ╲
        Continue   Re-evaluate   Preserve

---

## 5. Product Pathway Adapter

A Product Pathway Adapter converts a real-world product, decision logic, or customer use case into ClimateSOS runtime objects.

It does not validate the pathway by itself. It structures the pathway as a traceable runtime object so ClimateSOS can evaluate charter alignment, guardrail resolution, queue status, synchronization, system contribution, resulting state, and re-evaluation history.

At minimum, the adapter should define:

**ProductPathway**

- pathway type
- anonymized identifier, if needed
- created date and year
- synchronization window / TTL
- assigned identity token
- foundational charter evaluation status
- guardrail resolution status
- required queues
- optional queues
- mapped fabrics and substrates
- evidence inputs
- product outputs
- system contribution claims
- risk flags
- resolution pathway
- remedy options, where available
- state history / failed-state history
- prior resulting states, where applicable
- re-evaluated resulting states, where applicable
- evidence trace

A ClimateSOS intake and identity layer assigns the pathway’s canonical identity token before adapter processing. The Product Pathway Adapter receives and preserves that token while translating external pathway information into ClimateSOS runtime objects. The adapter may request token assignment when invoked without a token, but it does not independently mint canonical identities. Upstream intake safeguards establish provenance, access, and evidence-integrity conditions. They do not replace Foundational Charter Evaluation, pathway-specific guardrail evaluation, or later synchronization evaluation.

Product pathways do not own fabrics. The adapter maps each pathway’s required queues, evidence requirements, and system contributions onto the relevant ClimateSOS fabrics and substrates, such as Finance Fabric, Institutional Fabric, Deliverability Fabric, Fossil Constraint Fabric, Biosphere Fabric, or Workforce / Execution substrates.

A resolution pathway records how the product pathway exits or continues through evaluation. It may resolve as valid, conditionally valid, limited, stale, unresolved, no-ack, fossil-bound, harm-bound, boundary-stressed, or remedy-eligible. Remedy is only one possible branch. Failed, harm-bound, boundary-stressed, stale, fossil-bound, no-ack, and unresolved pathways must be preserved in state history even when no remedy is available.

Where appropriate, a pathway should be anonymized as:

- Transportation Fuel Product Pathway A
- Methane Abatement Product Pathway B
- Industrial Carbon Product Pathway C
- Flexible Load Customer Pathway D

rather than using a company or customer name.

---

## 6. Required Queue Categories

A customer/product pathway may require some or all of the following queues.

### 6.1 Feedstock / Input-Output Access Queue

Represents access to required physical inputs and, where relevant, viable pathways for product output delivery or use.

This queue may apply to both sides of the pathway:

* **input access**, such as feedstock, energy, water, materials, CO₂ streams, waste streams, or methane sources
* **output access**, such as delivery of clean fuel, carbon product, industrial heat, grid service, or abatement value to the intended user or system function

Examples:

* waste stream access
* captured methane or gas stream access
* biomass or biogenic input access
* industrial byproduct access
* clean electricity access
* water access
* CO₂ stream access
* mineral or material input access
* output delivery access
* storage, transport, or utilization access

Evaluation questions:

* Is the input physically available?
* Is output delivery physically and institutionally available?
* Is access durable?
* Is access permitted?
* Is access local or transport-dependent?
* Does access create competing uses?
* Does access create ecological, justice, labor, or supply-chain concerns?
* Does input access or output delivery create a risk of hidden fossil dependence?

Possible failure labels:

* FeedstockAccessBlocked
* FeedstockAccessUnverified
* FeedstockAccessTooSmall
* FeedstockAccessConflict
* FeedstockAccessHarmBound
* OutputAccessBlocked
* OutputAccessUnverified

---

### 6.2 Bankability / Revenue-Certainty Queue

Represents whether the pathway has sufficient revenue certainty to support scale.

Examples:

* offtake agreements
* reserve contracts
* advance market commitments
* public procurement
* long-term service agreements
* clean-fuel purchase contracts
* carbon-product purchase contracts
* verified carbon-storage or carbon-removal revenue
* methane-abatement crediting, where valid and bounded
* guarantee-backed procurement
* contract-for-difference mechanisms
* clean infrastructure availability payments
* de-risked public or anchor-buyer demand

This queue should remain aligned with the Playbook’s finance architecture, including Chapter 2 and Appendices E and F.

Evaluation questions:

* Is there a buyer or anchor user?
* Is the buyer durable?
* Is revenue tied to verified system contribution?
* Is revenue speculative or contracted?
* Does revenue certainty improve project finance?
* Does the contract create real fossil displacement or only accounting value?
* Does the revenue model depend on continued fossil extraction, fossil infrastructure persistence, or fossil-linked accounting substitution?
* Does the revenue model improve transition-system bankability, or only private project bankability?

Possible failure labels:

* RevenueCertaintyMissing
* OfftakeTooWeak
* BankabilityUnresolved
* SpeculativeRevenueOnly
* FossilLinkedRevenueRisk
* AccountingValueOnly

---

### 6.3 Project Finance Queue

Represents whether the pathway can access sufficient capital to scale.

Examples:

* project finance
* infrastructure finance
* debt financing
* equity financing
* concessional finance
* blended finance
* guarantees
* insurance / underwriting
* first-loss capital
* public risk guarantees
* local-currency lending
* transition-finance instruments

Evaluation questions:

* Can the pathway finance pilot, first deployment, and scale-up?
* Is finance dependent on unverified claims?
* Does finance require fossil-linked revenue?
* Does finance improve clean-system buildout or preserve fossil dependence?
* Does financing reduce or increase transition risk for workers, communities, ratepayers, or host regions?
* Does the pathway require public or concessional capital before commercial finance can clear?

Possible failure labels:

* ProjectFinanceBlocked
* HighWACCRisk
* UnfinanceableAtScale
* FossilLinkedFinanceRisk
* PublicRiskSupportMissing
* FinanceEvidenceGap

---

### 6.4 Non-Dilutive Capital / Public Support Queue

Represents grants, public funding, philanthropic funding, or other early support that may help the pathway reach demonstrable maturity.

Examples:

* grants
* public demonstration funding
* prize funding
* philanthropic support
* public-interest R&D
* MRV support
* pilot deployment funding
* community-benefit funding
* first deployment support
* validation or testing support

Evaluation questions:

* Can non-dilutive capital support proof of concept?
* Can it support MRV or evidence generation?
* Can it de-risk first deployment?
* Does it avoid premature commercialization claims?
* Does public support create public-good value, or mainly subsidize private claims?
* Does the pathway require public support to resolve evidence, guardrail, or MRV gaps before scale?

Possible failure labels:

* PilotFundingMissing
* MRVFundingMissing
* DemonstrationGap
* PublicSupportUnresolved
* PublicGoodValueUnclear

---

### 6.5 Permitting / Authorization Queue

Represents legal, regulatory, siting, safety, environmental, or interconnection permissions.

Examples:

* facility permits
* environmental review
* local approvals
* grid interconnection
* air or water permits
* waste-handling permits
* land-use approvals
* safety certification
* community approval processes
* fuel certification
* product certification
* transport or storage authorization

Evaluation questions:

* Can the pathway be legally built and operated?
* Are required approvals identified?
* Are environmental and community safeguards active?
* Does permitting delay exceed the synchronization window?
* Are affected rights-holders, workers, host communities, or Indigenous peoples included where their rights or interests are implicated?
* Does authorization depend on weakened review, burden-shifting, or hidden harm?

Possible failure labels:

* PermittingBlocked
* AuthorizationUnresolved
* CommunityProcessIncomplete
* RightsProcessIncomplete
* StalePermitSuccess
* LegalBlocked

---

### 6.6 Workforce / Execution Queue

Represents the labor, technical, operational, construction, engineering, and maintenance capacity required.

Examples:

* engineers
* operators
* electricians
* technicians
* construction crews
* permitting staff
* MRV personnel
* safety specialists
* feedstock logistics workers
* operations and maintenance workers
* project finance and grant-administration staff
* community engagement and remedy-process staff

Evaluation questions:

* Can the pathway be built and operated with available workforce?
* Does it compete with other transition-critical labor?
* Does it require specialized skills?
* Is training or credentialing needed?
* Does scaling the product worsen workforce bottlenecks elsewhere?
* Does the pathway provide safe, fair, and non-exploitative labor conditions?
* Does the pathway support or undermine fossil-worker transition where relevant?

Possible failure labels:

* WorkforceBlocked
* SpecializedLaborGap
* ExecutionCapacityTooSmall
* TransitionLaborConflict
* WorkerProtectionUnresolved
* LaborStandardsRisk

---

### 6.7 MRV / Evidence Queue

Represents measurement, reporting, verification, lifecycle analysis, and claims integrity.

Examples:

* emissions measurement
* carbon dioxide measurement
* methane abatement measurement
* carbon storage durability evidence
* lifecycle assessment
* supply-chain traceability
* ecological monitoring
* safety monitoring
* independent verification
* auditability
* counterfactual baseline documentation
* uncertainty documentation

Evaluation questions:

* Are emissions reductions measured?
* Are carbon claims durable and verified?
* Are lifecycle harms included?
* Can claims be audited?
* Are uncertainties documented?
* Are baselines explicit?
* Are claimed system contributions distinguishable from accounting claims?
* Is evidence sufficient for the current evaluation stage?

Possible failure labels:

* MRVUnresolved
* LifecycleEvidenceGap
* ClaimsIntegrityRisk
* DurabilityUnverified
* BaselineUnclear
* AuditabilityGap

---

## 6.8 Fossil-Exit Finance / Persistence-Closure Queue

This queue evaluates whether the pathway contributes to fossil displacement, fossil retirement, refinancing closure, or reduced fossil fallback risk, rather than merely creating a parallel clean or lower-carbon activity.

It asks whether fossil assets, fuels, infrastructure, contracts, insurance, refinancing channels, capacity payments, or reliability roles remain protected despite the proposed pathway.

Key questions include:

* Does the pathway reduce fossil use, or only add a cleaner parallel product?
* Does it help retire, replace, or strand a fossil-dependent process?
* Does it depend on continued fossil extraction, fossil throughput, fossil infrastructure, or fossil-linked revenue?
* Does it reduce fossil refinancing, insurance, capacity-payment, or life-extension pathways?
* Does it replace a fossil reliability, feedstock, heat, fuel, or infrastructure role?
* Does it risk preserving fossil assets through utilization, blending, offsets, credits, or transitional exemptions?
* Does it close a fossil persistence pathway within the relevant synchronization window?

Diagnostic labels:

* FossilExitUnresolved
* FossilPersistenceRisk
* FossilLinkedRevenueRisk
* FossilRefinancingStillOpen
* FossilReliabilityRoleUnreplaced
* FossilThroughputDependence
* ParallelCleanActivityOnly
* RetirementContributionUnverified

---

## 7. Product Outputs vs. Net Overall System Contributions

ClimateSOS must distinguish between ProductOutput and NetOverallSystemContribution.

A product output is what the pathway produces.
A net overall system contribution is how that output affects the broader transition.

Examples:

* clean fuel
* hydrogen
* industrial heat
* carbon-rich material
* stored carbon
* methane utilization
* grid flexibility
* waste reduction
* industrial feedstock
* transport fuel
* clean infrastructure service
* verification or coordination service

A system contribution is how the output affects the global and local net-zero transition.

Examples:

* improves clean adequacy
* reduces methane emissions
* supports fossil asset retirement
* supports fossil workforce retirement and reskilling
* replaces fossil-derived fuel or feedstock
* supports clean-only growth
* reduces fossil fallback risk
* stores carbon under verified conditions
* reduces landfill or waste-sector emissions
* supports industrial electrification
* reduces grid stress
* improves transition timing
* closes a fossil persistence pathway
* reduces residual emissions without substituting for phaseout

A product output should not be treated as transition-valid unless the system contribution is defined, evidenced, bounded, and compatible with foundational charter evaluation.

Example rules:

* Clean fuel output does not automatically imply fossil displacement.
* Carbon product output does not automatically imply durable carbon storage.
* Methane utilization does not automatically imply net climate benefit.
* Revenue does not automatically imply transition contribution.
* Customer value does not automatically imply system value.
* Technical feasibility does not automatically imply guardrail validity.

---

## 8. Scale-Up Logic

A customer/product pathway may resolve into one of several scale diagnostics after foundational evaluation and synchronization testing.

### 8.1 Scale-Up Tipping State

The pathway reaches a scale-up tipping state when the necessary queues synchronize within the relevant window and foundational criteria are satisfied.

Criteria may include:

* foundational charter evaluation passes or conditionally passes
* feedstock / input-output access clears
* permitting clears
* workforce clears
* revenue certainty clears
* finance clears
* MRV clears
* guardrails pass or conditionally pass
* system contribution is credible
* state history does not contain unresolved prior harm or failed conditions requiring remedy

Suggested label:

**ScaleUpTippingState**

Meaning:

> The product pathway has passed foundational evaluation and has enough synchronized support to move from isolated deployment toward material system contribution within the required timeframe.

---

### 8.2 Scale-Up Bottleneck

The pathway enters a scale-up bottleneck when one or more required queues fail to clear or foundational criteria remain unresolved.

Possible causes:

* finance missing
* offtake missing
* feedstock access limited
* output access unresolved
* permitting delayed
* workforce constrained
* MRV unresolved
* guardrails unresolved
* system contribution unclear
* foundational charter evaluation incomplete
* prior failed state not yet remedied

Suggested label:

**ScaleUpBottleneck**

Meaning:

> The pathway may have technical or local value, but required queues or validity conditions have not cleared sufficiently for material contribution to the accelerated window.

---

### 8.3 Small-Node Persistence

The pathway remains in small-node persistence when it can operate locally or experimentally but does not reach material system scale.

Suggested label:

**SmallNodePersistence**

Meaning:

> The pathway may produce useful local benefits, pilot evidence, or limited abatement, but it does not materially alter the 2037/2038 pathway unless additional queues clear and synchronization improves.

Associated outputs:

* LimitedMethaneAbatement
* LimitedCleanFuelContribution
* LimitedCarbonStorageValue
* LimitedIndustrialConversionSupport
* LimitedSystemContribution
* LocalBenefitOnly
* PilotEvidenceOnly

---

### 8.4 Stale Success

The pathway enters stale success when required queues eventually clear, but too late to preserve the relevant synchronization window.

Suggested label:

**StaleSuccess**

Meaning:

> The pathway succeeds technically, commercially, or institutionally, but not in time to support the accelerated net-zero window.

Stale success must be preserved in state history. It should not be rewritten as full success unless the pathway is later re-evaluated under a different time window or system objective.

---

## 9. Guardrail Resolution

A technically synchronized product pathway is not necessarily valid.

Guardrails must be evaluated as part of foundational charter evaluation before synchronization assessment, and they may need to be evaluated again during or after synchronization if scale, siting, finance, output use, remedy, or system effects change the pathway’s risk profile.

Guardrail resolution may be:

* Pass
* ConditionalPass
* Unresolved
* Invalid

A product pathway may be invalid or unresolved even if it reaches technical or financial readiness.

Examples:

* carbon product has unverified durability
* feedstock creates ecological harm
* project shifts burden onto overburdened communities
* data use lacks consent or auditability
* worker transition plan is missing
* project depends on continued fossil extraction
* lifecycle emissions are unresolved
* scale-up changes the harm profile
* remedy evidence is incomplete

ClimateSOS must preserve the distinction between:

* technically possible
* commercially plausible
* systemically useful
* guardrail-valid

These are not the same thing.

---

## 10. Resolution Pathways and RemedyBus Use

Not every failed or unresolved pathway is remedy-eligible. ClimateSOS must first record the pathway’s resolution state, then determine whether RemedyBus routing is available.

If a product pathway is unresolved, harm-bound, boundary-stressed, stale, or invalid-but-redesignable, it may be routed to the RemedyBus.

The RemedyBus may carry:

* evidence gathering
* MRV design
* lifecycle analysis
* community process
* consent process
* compensation plan
* governance fix
* design change
* monitoring evidence
* appeal record
* verification record
* re-evaluation request

The RemedyBus does not authorize deployment or continuation.

It only carries corrective action, evidence, and re-evaluation.

After RemedyBus processing, the pathway must be re-evaluated beginning with foundational charter criteria. A remedy is successful only if the pathway returns with:

* Pass
* ConditionalPass

and an acceptable resulting state.

### 10.1 State History and Re-Evaluation Trace

ClimateSOS must preserve failed, unresolved, harm-bound, boundary-stressed, stale, or incomplete states in the pathway history.

A re-evaluation should not erase the prior state. It should compare:

* previous resulting state
* previous guardrail resolution
* previous failure label
* evidence supporting the previous state
* remedy action taken
* new evidence submitted
* re-evaluated guardrail resolution
* re-evaluated resulting state
* remaining conditions or monitoring requirements

Example trace:

* Previous resulting state: HarmBound
* Previous evidence: siting burdens increased for an already overburdened community
* Remedy action: redesign, community process, compensation plan, siting revision, monitoring plan
* New evidence: burden analysis updated; affected community process completed; monitoring mechanism established
* Re-evaluated guardrail resolution: ConditionalPass
* Re-evaluated resulting state: CleanBound or LimitedSystemContribution, depending on system contribution
* Remaining condition: monitoring and appeal mechanism required

Failed or incomplete states remain part of the state history even when remedy later succeeds.

---

## 11. Resulting States and Diagnostic Labels

The core ClimateSOS resulting states remain:

* CleanBound
* MixedBound
* FossilBound
* NoAck
* HarmBound
* BoundaryStress

Product-pathway diagnostics may add explanatory labels without necessarily becoming core resulting states:

* ScaleUpTippingState
* ScaleUpBottleneck
* SmallNodePersistence
* LimitedSystemContribution
* RevenueCertaintyMissing
* MRVUnresolved
* FeedstockAccessBlocked
* OutputAccessBlocked
* StaleSuccess
* PriorStateRemedied
* PriorStateUnresolved
* PriorStatePreserved

These diagnostics help explain how the pathway performs after foundational evaluation and whether it contributes materially to the accelerated net-zero window.

### 11.1 State Preservation Rule

ClimateSOS must preserve the pathway’s prior states, failure labels, remedy events, and evidence history.

A later valid or conditionally valid state does not delete earlier failures. It records that the pathway was re-evaluated after remedy, new evidence, redesign, or changed system conditions.

---

## 12. Evaluation Questions

For any customer/product pathway, ClimateSOS should surface a structured evaluation set. These questions are not all hard gates. They are evidence prompts used to determine guardrail status, queue status, diagnostic labels, resulting state, and remedy needs.

### 12.1 What does the pathway require?

* What feedstock, input, or physical access is required?
* What output delivery or utilization pathway is required?
* What finance is required?
* What revenue certainty is required?
* What permits are required?
* What workforce is required?
* What MRV is required?
* What infrastructure is required?
* What customer, institutional, or regulatory decisions are required?

### 12.2 What does the pathway produce?

* What physical product or service is produced?
* What emissions, carbon, methane, energy, reliability, or grid value is claimed?
* What is the unit of output?
* What is the expected scale?
* What is the timing?
* What is the useful life or durability of the output?
* What system condition must hold for the output to matter?

### 12.3 What system contribution is claimed?

* Does it reduce fossil use?
* Does it reduce methane?
* Does it improve clean adequacy?
* Does it support clean-only growth?
* Does it help close a fossil persistence pathway?
* Does it support industrial conversion?
* Does it create verified carbon storage/removal?
* Does it improve grid flexibility?
* Does it reduce residual emissions without substituting for phaseout?
* Does it shorten, preserve, or weaken the accelerated timeline?

### 12.4 What can fail?

* Which queues can block?
* Which guardrails can fail?
* Which evidence is missing?
* Which claims are unresolved?
* Which timeline slips create stale success?
* Which failure modes push the pathway into limited contribution?
* Which prior failed states must remain visible?
* Which scale effects could create new harms?
* Which dependencies could create hidden fossil persistence?

### 12.5 What would remedy require?

* What evidence would resolve uncertainty?
* What design change would avoid harm?
* What contract would improve bankability?
* What safeguard would allow ConditionalPass?
* What queue must clear to reach scale?
* What timing condition must hold to preserve the 2037/2038 window or shorten the timeline?
* What prior failed state is being remedied?
* What evidence demonstrates that the remedy changed the pathway state?
* What conditions must remain active after ConditionalPass?

---

## 13. Product-Spec Implementation Requirements

The product adapter should support, at minimum:

* ProductPathway
* ProductOutput
* NetOverallSystemContribution
* PathwayQueueBundle
* GuardrailRequirement
* EvidenceRequirement
* ScaleDiagnostic
* StateHistory
* RemedyTrace
* ReEvaluationEvent

Initial test cases should verify:

1. A product pathway that passes foundational charter evaluation and clears all required queues can reach ScaleUpTippingState.
2. A product pathway with missing revenue certainty remains ScaleUpBottleneck.
3. A product pathway with unresolved MRV cannot be valid even if finance and permitting clear.
4. A product pathway with accepted and verified remedy can re-evaluate to ConditionalPass.
5. A product pathway that clears too late becomes StaleSuccess or LimitedSystemContribution.
6. A product pathway that produces a useful output but does not affect fossil displacement remains LimitedSystemContribution.
7. A product pathway with a prior HarmBound state preserves the prior failed state in StateHistory after remedy.
8. A product pathway with ConditionalPass remains valid only while required conditions, monitoring, or safeguards remain active.
9. A product pathway with scale-up effects that create new guardrail concerns must be re-evaluated.
10. A product pathway with hidden fossil dependence resolves to FossilBound, MixedBound, Unresolved, or another appropriate non-valid state unless the dependence is bounded, temporary, and explicitly classified.

---

## 14. Pathway Evaluation Exit Criteria and State Preservation Requirements

This section defines when a product pathway can exit the adapter evaluation as a valid, conditionally valid, unresolved, limited, or failed pathway state.

The adapter is not merely gated at entry. It is a stateful evaluation process. It must preserve state history, including failed, unresolved, harm-bound, stale, or incomplete states, even when later remedy or re-evaluation changes the pathway’s current status.

For a product pathway to exit as valid or conditionally valid on a pathway to net zero, it must satisfy the criteria below.

### Criterion 1 — Defined system role

The pathway must identify what transition function it serves.

Examples:

* fossil displacement
* methane abatement
* clean adequacy
* clean growth
* industrial conversion
* carbon storage/removal
* waste-sector emissions reduction
* grid extension or modernization
* fossil exit, such as finance WACC rule change, refinancing closure, or retirement acceleration
* transition evidence, MRV, or coordination support

### Criterion 2 — Queue transparency

The pathway must identify the queues required for scale.

Examples:

* feedstock / input access
* output access
* finance
* permitting
* workforce
* offtake
* MRV
* infrastructure
* authorization
* customer decision
* institutional decision

### Criterion 3 — Timing relevance

The pathway must identify whether it can contribute within the relevant synchronization window.

A pathway that succeeds too late may still be useful, but it should not be counted as preserving the accelerated window.

If a pathway exits as StaleSuccess, that state must be preserved.

### Criterion 4 — Revenue and finance realism

The pathway must distinguish between technical potential and financeable scale.

Revenue certainty, offtake, reserve contracts, public procurement, guarantees, concessional finance, or other bankability mechanisms should be made explicit.

### Criterion 5 — Evidence and MRV

The pathway must provide or request evidence sufficient to evaluate its claims.

Unverified claims resolve to Unresolved, not assumed-valid.

### Criterion 6 — Guardrail validity

The pathway must be evaluated against all core guardrail domains: planetary boundaries, biosphere integrity, justice and harm avoidance, labor, lifecycle responsibility, governance, data agency, human accountability, and AI/accountability safeguards.

If a guardrail domain is not material to the pathway, ClimateSOS must record the reason it is not material. The domain must not be skipped by default.

### Criterion 7 — Product-output / system-contribution separation

A product output should not automatically be counted as a system contribution.

The pathway must show how the output changes transition dynamics.

### Criterion 8 — Resolution and remedy pathway

If the pathway is unresolved, failed, stale, harm-bound, boundary-stressed, fossil-bound, limited, or redesignable, ClimateSOS should record the resolution pathway and identify whether remedy or new evidence could permit re-evaluation.

The remedy pathway must preserve the prior failed or unresolved state and compare it with the re-evaluated state.

### Criterion 9 — Fossil dependence disclosure

The pathway must surface any fossil dependence.

It must not rely on continued fossil extraction, fossil infrastructure persistence, or fossil accounting substitution for a successful exit state unless the dependence is:

* explicitly classified
* bounded
* temporary
* justified by physical constraints
* not used to delay fossil exit
* compatible with foundational charter evaluation

Otherwise, the pathway should resolve to a non-valid or unresolved state.

### Criterion 10 — Human investigation preserved

ClimateSOS structures and surfaces the evidence.

It does not autonomously conclude that a proprietary product is valid, investment-worthy, policy-ready, or deployable.

---

## 15. Relationship to v0.7 Architecture

This specification extends the v0.7 architecture by defining a Product Pathway Adapter layer.

The v0.7 architecture defines the core runtime primitives and evaluation behavior. The Product Pathway Adapter defines how a real-world customer or product pathway is translated into those primitives.

External Pathway
      │
      ▼
Intake & Identity
      │
      ▼
Product Pathway Adapter
      │
      ▼
ClimateSOS Runtime

Core runtime objects

• IdentityToken
• ProductPathway
• PathwayQueueBundle
• GuardrailResolution
• ProductOutput
• NetOverallSystemContribution
• ResultingState
• ScaleDiagnostic
• StateHistory
• EvidenceTrace

The adapter is not a separate decision authority. It is responsible for intake, translation, normalization, and traceability before runtime evaluation.

---

## 16. Summary

The Product Pathway Adapter lets ClimateSOS evaluate real-world customer/product cases without exposing proprietary details.

The adapter preserves the original ClimateSOS purpose:

> A user or researcher inputs choices, assumptions, or pathway conditions; ClimateSOS structures those inputs against Playbook-derived synchronization criteria and Charter-derived guardrails, then surfaces whether the pathway appears aligned, fragile, delayed, divergent, unresolved, harmful, stale, or limited in system contribution.

This pattern is especially important for technologies or customer pathways that may produce useful outputs but depend on synchronized finance, permitting, feedstock, output access, workforce, offtake, MRV, guardrail validity, and remedy conditions before they can materially affect the accelerated ~2037/2038 operational net-zero window.

The adapter does not erase failed states. It records them, evaluates remedy, compares prior and re-evaluated states, and preserves the evidence trail needed for human investigation.

