# ClimateSOS

## Climate State Transition Model OS

**GitHub project:** https://github.com/hsbay/ClimateSOS
**Author / maintainer:** Shannon A. Fiume (@safiume)
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0), 2026
**Development note:** ClimateSOS was conceived, researched, directed, architected, and developed by Shannon A. Fiume through an iterative human–AI collaboration. OpenAI’s ChatGPT provided AI-assisted research support, drafting, code-generation, implementation assistance, and systems-design iteration under Shannon’s direction.

```text
A distributed synchronization model for rapid clean-energy transition,
fossil retirement, and biosphere stabilization.
```

ClimateSOS models the global transition as a distributed operating system composed of:

* identity tokens
* queues
* synchronization windows
* distributed fabrics
* weighted cascade attractors
* biosphere cycle buses
* binding states
* guardrail resolution states
* remedy buses
* planetary-boundary pressure accumulation
* transition failure modes

The system treats transition dynamics as synchronization problems across finance, energy, logistics, governance, workforce, institutional, justice, and biosphere layers.

Rather than assuming transitions occur automatically once technologies become cheap enough, ClimateSOS models:

* queue clearance
* delivery bottlenecks
* fossil fallback persistence
* timing failures
* synchronization loss
* unresolved guardrails
* corrective remedy pathways
* weighted pressure accumulation
* cascading Earth-system destabilization

The current implementation is a toy execution engine and ontology prototype intended for systems reasoning and stress testing.

It is not:

* operational infrastructure control software
* investment advice
* policy instruction
* a calibrated prediction system
* a substitute for public authority, community participation, qualified expertise, or accountable decision-making

---

# Core Concepts

## Identity Tokens

Identity tokens represent entities attempting to synchronize into a stable system state.

Examples:

* data-center load identities
* industrial load identities
* workforce identities
* restoration project identities
* fossil retirement pathway identities
* regional grid identities

Identity tokens can become:

```text
CleanBound
MixedBound
FossilBound
NoAck
HarmBound
BoundaryStress
```

They also maintain:

* TTL windows
* binding history
* synchronization outcomes
* temporal states
* guardrail resolution
* remedy history, where applicable

An IdentityToken is not merely a label. It is a state-bearing object whose outcome depends on whether required queues, fabrics, guardrails, and timing windows clear.

---

## Queues

Queues model real-world throughput, latency, or capacity constraints.

Examples:

```text
Project Finance Queue
Clean Supply Queue
Deliverability Queue
Adequacy Queue
Materials Queue
Workforce Throughput Queue
Permitting / Authorization Queue
Emerging Market De-risking Queue
Fossil Retirement Queue
Fossil Fallback Queue
```

Queues can enter states such as:

```text
Clear
Constrained
Blocked
Severely blocked
Expired
Closed
```

Queue clearance ratios model the fraction of demand that can clear during the synchronization window.

Example:

```text
clearance = capacity / demand
```

A queue with:

```text
clearance = 0.90
```

means roughly 90% of required throughput clears during the synchronization interval.

---

# Fabrics

Fabrics are distributed coordination layers composed of multiple queues.

Current fabrics include:

```text
Deliverability Fabric
Finance Fabric
Institutional Fabric
Procurement Synchronization Fabric
Fossil Constraint Fabric
BioFabric
```

Fabrics determine whether synchronized state transitions are possible.

Fabrics are not command structures. They are coordination surfaces that report readiness, blockage, starvation, closure, or partial synchronization.

Fabric readiness may resolve to:

```text
ready
partial
unready
closed
```

---

# Synchronization Scheduler

The Synchronization Scheduler evaluates:

* queue states
* fabric readiness
* synchronization timing
* bottlenecks
* closed pathways
* attractor activation
* pressure accumulation
* guardrail resolution
* RemedyBus status
* pathway availability

The scheduler is intentionally weaker than a centralized command-and-control planner.

It acts more like a distributed synchronization layer than a sovereign controller.

The scheduler may:

```text
detect desynchronization
identify bottlenecks
surface fallback risk
route tokens toward re-evaluation
trigger threshold checks
```

The scheduler may not:

```text
authorize permits
allocate real-world capital
force actors to execute
override guardrails
manufacture materials
command institutions
```

The ClimateSOS scheduler coordinates timing and arbitration among fabrics, queues, operators, and substrates, but it does not possess real-world command authority. Execution remains distributed across real-world institutions, communities, infrastructure operators, finance actors, workers, and ecological systems.

---

# Alignment Switch

The Alignment Switch determines whether an identity token becomes:

```text
CleanBound
MixedBound
FossilBound
NoAck
HarmBound
BoundaryStress
```

based on:

* temporal validity
* queue clearance
* fabric readiness
* fossil fallback availability
* guardrail resolution
* weighted attractor activation
* RemedyBus status, where applicable
* biosphere stress conditions

The Alignment Switch resolves identity tokens after queue, fabric, timing, guardrail, attractor, and remedy checks.

For v0.1, the Alignment Switch evaluates in this order:

```text
1. temporal validity
2. queue clearance
3. fabric readiness
4. fossil fallback availability
5. guardrail resolution
6. active attractor patterns
7. RemedyBus status, if applicable
8. resulting state
9. explanation trace
```

---

# Temporal States

ClimateSOS includes explicit temporal semantics.

Example states:

```text
Fresh
Aging
Near-timeout
Expired
Stale-success
```

“Stale-success” represents pathways that technically completed but failed to synchronize within the required transition window.

Stale-success is treated as failure, not success.

Example:

```text
A transmission corridor clears permitting,
but only after the clean-load synchronization window expires.
```

This may produce:

```text
NoAck
MixedBound
FossilBound
```

depending on whether fossil fallback, unresolved guardrails, or other binding pathways become active.

---

# Weighted Cascade Attractors

Weighted Cascade Attractors model recurring nonlinear system behaviors.

They model:

```text
pressure accumulation
threshold activation
cross-bus coupling
cascade activation
fallback dynamics
path-dependence
```

rather than simple binary failure states.

A weighted attractor activates when accumulated pressure exceeds a threshold.

Example:

```text
weighted_pressure >= threshold
→ attractor tips
→ cascade state activates
```

This allows ClimateSOS to model:

* fossil lock-in
* fossil fallback
* reliability panic
* finance stall
* transition destabilization
* biosphere-led cascades
* planetary-boundary stress accumulation
* coupled failure systems

Example attractors:

```text
Reliability Panic Attractor
Finance Stall Attractor
Transmission Failure Attractor
Workforce Bottleneck Attractor
Materials Shock Attractor
Utility Friction Attractor
Firm Clean Gap Attractor
Emerging Market Lock-in Attractor
Coordinated Fossil Retrenchment Attractor
```

Biosphere attractors include:

```text
Cryosphere albedo / ice-to-land cascade
Permafrost carbon and methane feedback
Amazon / tropical forest dieback
AMOC / ocean-circulation disruption
Freshwater-cycle / monsoon destabilization
Compound biosphere cascade
```

---

# Pressure Tokens

Pressure tokens represent accumulated stress applied to queues, fabrics, or biosphere buses.

Examples:

```text
fossil finance persistence
transmission congestion
storage duration gap
workforce shortage
materials fragility
utility revenue friction
cryosphere albedo loss
permafrost carbon feedback
water-cycle instability
ecosystem metabolism degradation
```

Pressure accumulation is one of the major conceptual upgrades in the ClimateSOS architecture.

Pressure is not merely binary. It accumulates until thresholds are crossed, at which point an attractor, fallback pathway, or boundary-stress state may activate.

---

# Guardrail Resolution

Guardrails define the valid operating envelope for ClimateSOS. They are not optimization preferences.

A technically synchronized pathway is not necessarily valid. It must also satisfy applicable guardrails.

Guardrail resolution may be:

```text
Pass
ConditionalPass
Unresolved
Invalid
```

## Pass

The pathway satisfies the relevant guardrail.

## ConditionalPass

The pathway satisfies the relevant guardrail only while declared safeguards, monitoring, rights protections, time limits, repair mechanisms, or operating constraints remain active and verified.

Examples:

```text
temporary fossil fallback allowed only under non-routine emergency conditions
project proceeds only with enforceable community governance
CDR pathway accepted only with verified MRV and ecosystem safeguards
data use accepted only with consent, audit, appeal, and deletion mechanisms
```

## Unresolved

Unresolved means the pathway cannot yet be classified as valid because required evidence, safeguards, consent, design detail, monitoring, or accountability conditions are incomplete or uncertain.

Unresolved does not mean probably valid.

It means:

```text
not valid yet
```

Examples:

```text
Indigenous consent not yet verified
community-control process incomplete
data-agency safeguards undocumented
ecological MRV pending
labor-transition plan missing detail
possible burden-shifting not yet assessed
```

Unresolved pathways may be routed to the RemedyBus for evidence gathering, redesign, verification, or re-evaluation.

## Invalid

Invalid means the pathway violates a hard guardrail under the current design.

Invalid pathways cannot proceed as valid. They must be rejected, halted, or redesigned.

Where remediation is possible, an invalid pathway may be routed to the RemedyBus only for corrective action and re-evaluation, not for continued authorization.

Examples:

```text
new fossil capacity for net load growth
non-consensual displacement
rights violation
irreversible ecosystem damage treated as acceptable tradeoff
fossil persistence hidden behind accounting claims
AI system replacing accountable public authority
```

---

# RemedyBus

The RemedyBus is a special-purpose corrective pathway.

It is not a normal transition fabric and does not produce clean transition output directly.

The RemedyBus carries unresolved, harmful, boundary-stressed, invalid-but-potentially-redesignable, or conditionally valid states through corrective action, evidence gathering, verification, and re-evaluation.

The RemedyBus may receive:

```text
HarmBound
BoundaryStress
Unresolved guardrails
ConditionalPass items requiring monitoring
Invalid but potentially redesignable pathways
```

The RemedyBus may carry:

```text
RemedyAction
RepairPlan
ConsentProcess
CompensationPlan
GovernanceFix
DesignChange
MonitoringEvidence
AppealRecord
VerificationRecord
ReEvaluationRequest
```

The RemedyBus may output:

```text
RemedyAccepted
RemedyRejected
RemedyIncomplete
RemedyExpired
RemedyConditioned
ReEvaluationEvent
```

The RemedyBus does not authorize continuation.

It only carries corrective action, evidence, and re-evaluation.

After RemedyBus processing, the token must be re-evaluated by the Alignment Switch.

A remediated pathway is not valid because remediation occurred. It is valid only if re-evaluation returns:

```text
Pass
ConditionalPass
```

and an acceptable ResultingState.

---

# BioFabric

BioFabric models the biosphere as nested interacting cycle buses.

Current buses include:

```text
Land Cycle Bus
Ocean Cycle Bus
Carbon-Cycle Bus
Water-Cycle Bus
Cryosphere Feedback Bus
Ecosystem Metabolism Bus
```

BioFabric does not treat biodiversity as a separate bus.

Instead, biodiversity is modeled as a characteristic of healthy productive BioNPUs.

BioFabric is not merely another clean-industry product lane. It is a boundary-condition fabric.

It evaluates whether transition pathways remain compatible with:

```text
planetary boundaries
ecosystem recovery
carbon-cycle repair
land-use integrity
water-cycle stability
biosphere integrity
non-harm constraints
```

Carbon success with ecosystem harm does not resolve to full success.

It may resolve to:

```text
HarmBound
BoundaryStress
NoAck
```

---

# BioNPUs

BioNPUs are biosphere processing nodes participating in multiple nested cycles.

Examples:

```text
Forest NPU
Peatland NPU
Wetland NPU
Watershed NPU
Mangrove NPU
Kelp / Ocean NPU
Glacier / Cryosphere NPU
```

BioNPUs can become:

```text
Productive
Recovering
Resilient
Degraded
Disconnected
Collapsed
```

Technical transition fabrics are packet / queue-like.

BioFabric is cycle / bus / metabolism-like.

Use packet logic at the human-interface boundary, such as:

```text
Finance Tokens
Stewardship Tokens
Auth Tokens
Restoration Work Tokens
MRV Tokens
CDR Product Tokens
Harm Tokens
```

But the biosphere itself should be modeled through:

```text
flows
cycles
coupling
degradation
recovery
population
resilience
metabolism
interdependence
```

---

# Biosphere-Led Failure Modes

One of the major realizations during v0.6 development was that biosphere systems can lead transition failure rather than merely react to it.

ClimateSOS therefore includes biosphere-leading cascade attractors.

Examples:

```text
Cryosphere albedo / ice-to-land cascade
Permafrost carbon and methane feedback
Amazon / tropical forest dieback
AMOC / ocean-circulation disruption
Freshwater-cycle / monsoon destabilization
Compound biosphere cascade
```

These are modeled as Weighted Cascade Attractors operating across multiple BioFabric buses.

---

# Worker Transition States

ClimateSOS explicitly models fossil worker transition outcomes.

Worker identities can become:

```text
Clean-attached
Transitioning
Retired
Protected-exit
Stranded
```

The system treats just transition logic as a first-class synchronization requirement.

Worker transition failure can produce:

```text
HarmBound
BoundaryStress
MixedBound
NoAck
```

depending on severity, remedy status, and whether credible transition protection is available.

---

# Dynamic Appendix C Ranking

Appendix C is no longer manually ranked.

Instead, rankings emerge dynamically from:

```text
likelihood
× consequence
× coupling
× irreversibility
× confidence
× pressure accumulation
```

This allows the system to generate scenario-sensitive rankings of:

* transition failures
* fossil persistence risks
* biosphere cascades
* planetary-boundary stressors

The ranking engine is heuristic and transparent rather than predictive.

---

# Resulting States

For v0.1, ClimateSOS uses the following ResultingState values:

```text
CleanBound
MixedBound
FossilBound
NoAck
HarmBound
BoundaryStress
```

## CleanBound

The identity token synchronized to clean supply, deliverability, and adequacy inside its TTL, without fossil fallback binding the result.

CleanBound is not automatically valid unless guardrails also resolve to Pass or ConditionalPass.

## MixedBound

The clean pathway partially cleared, but fossil fallback, unresolved guardrails, boundary stress, or structural dependency remain entangled.

MixedBound is not full transition success.

## FossilBound

The identity token became bound to fossil fallback, fossil persistence, fossil adequacy, or fossil lock-in.

This can occur through reliability panic, deliverability failure, emerging-market lock-in, fossil finance persistence, or retained fallback capacity.

## NoAck

The runtime failed to produce a synchronized valid binding inside the TTL.

Common causes include:

```text
expired TTL
stale-success
unresolved required queues
no valid fabric outcome
active attractor failure
unresolved remedy pathway
```

## HarmBound

The identity token became bound to a harm condition.

Examples:

```text
rights violation
avoidable burden-shifting
non-consensual impact
ecological harm
labor exploitation
data-agency violation
community-control failure
guardrail breach
```

HarmBound does not always mean permanent rejection forever.

Some HarmBound states may be routed to the RemedyBus for halt, redesign, repair, evidence gathering, verification, and re-evaluation.

But HarmBound does not authorize continuation.

## BoundaryStress

The identity token creates or worsens stress against a planetary, biosphere, justice, adequacy, or system-integrity boundary but has not necessarily resolved to final harm or failure.

BoundaryStress may route to:

```text
RemedyBus
HarmBound
NoAck
MixedBound
ConditionalPass
```

depending on corrective action and re-evaluation.

---

# Validity Rule

A pathway is valid only if:

```text
ResultingState is CleanBound
or another explicitly acceptable bound state in later versions

and

GuardrailResolution is Pass or ConditionalPass

and

all ConditionalPass requirements remain active, monitored, and verified.
```

A technically synchronized pathway with unresolved guardrails is not fully valid.

Example:

```text
ResultingState: CleanBound
GuardrailResolution: Unresolved
Explanation: clean supply, deliverability, and adequacy cleared, but community-control safeguards or data-agency safeguards remain unresolved.
Public interpretation: technically synchronized, but not valid pending guardrail resolution.
```

---

# Implementation Primitive Lock — v0.1

Before expanding the ontology, ClimateSOS should first be implemented as a minimal toy runtime using a small set of stable primitives.

The purpose of v0.1 is not to model the full transition system.

It is to test whether the core runtime semantics can evaluate one bounded case:

```text
a new data-center load seeking clean-aligned service
```

## v0.1 Toy Case

The first toy case is:

```text
DataCenterLoadToken
```

This token represents new large flexible or semi-flexible electricity demand.

The runtime evaluates whether the load can be served by clean supply inside the relevant time window without creating fossil fallback, unresolved guardrail violations, harm, or boundary stress.

## v0.1 Core Primitives

The v0.1 runtime should implement the following primitives before adding additional fabrics, actors, interfaces, or scenario complexity:

```text
IdentityToken
Queue
Fabric
Guardrail
AttractorPattern
Scheduler
AlignmentSwitch
ResultingState
GuardrailResolution
RemedyBus
ScenarioState
```

## IdentityToken Fields

For v0.1, an IdentityToken carries:

```text
name
created_year
ttl_years
required_queues
required_fabrics
guardrails
current_state
resulting_state
guardrail_resolution
history
notes
```

## Queue Fields

For v0.1, each Queue carries:

```text
capacity
demand
latency_years
ttl_years
status
clearance_ratio
```

## Fabric Fields

For v0.1, each Fabric carries:

```text
name
queues
status
readiness
notes
```

## ScenarioState Fields

For v0.1, ScenarioState carries:

```text
current_year
tokens
queues
fabrics
guardrails
attractors
remedy_bus
results
```

---

# v0.1 Data-Center Load Tests

The first toy engine should test both fossil fallback and unresolved guardrails.

## Test A — Fossil Fallback

Input:

```text
DataCenterLoadToken
Clean Supply Queue: Clear
Deliverability Queue: Blocked
Adequacy Queue: Blocked
Project Finance Queue: Clear
Permitting / Authorization Queue: Partial or Clear
Fossil fallback available: true
GuardrailResolution: Pass or ConditionalPass
```

Expected result:

```text
ResultingState: FossilBound
GuardrailResolution: Pass or ConditionalPass
Validity: not valid as clean transition success
Explanation: clean supply and finance cleared, but deliverability and adequacy did not clear inside the TTL; because fossil fallback remained available, the load bound to fossil-backed reliability.
```

This test catches the failure mode where clean supply exists but cannot serve load, so gas or other fossil fallback fills the gap.

## Test B — Technically Clean but Unresolved

Input:

```text
DataCenterLoadToken
Clean Supply Queue: Clear
Deliverability Queue: Clear
Adequacy Queue: Clear
Project Finance Queue: Clear
Permitting / Authorization Queue: Clear
Fossil fallback available: false
GuardrailResolution: Unresolved
```

Expected result:

```text
ResultingState: CleanBound
GuardrailResolution: Unresolved
Validity: not valid yet
Explanation: the load synchronized technically to clean supply, deliverability, and adequacy, but guardrail conditions remain unresolved; the pathway cannot be classified as fully valid until re-evaluation returns Pass or ConditionalPass.
```

This test catches the failure mode where technical synchronization is incorrectly treated as full validity.

## Test C — RemedyBus Re-Evaluation

Initial state:

```text
ResultingState: HarmBound
GuardrailResolution: Unresolved
```

RemedyBus process:

```text
RemedyAction submitted
VerificationRecord accepted
ReEvaluationEvent triggered
```

Expected result after re-evaluation:

```text
ResultingState: CleanBound or MixedBound
GuardrailResolution: ConditionalPass
Validity: valid only while conditions remain active and verified
```

This test ensures harm, unresolved status, or boundary stress can be corrected without treating remediation itself as a loophole.

---

# v0.1 Engine Output

The toy engine should emit:

```text
resulting_state
guardrail_resolution
validity
bottlenecks
closed_queues
fabric_status
remedy_bus_status
explanation_trace
```

The first engine should not merely answer:

```text
pass / fail
```

It should explain why a token bound to its resulting state.

---

# v0.1 Stop Rule

No additional runtime ontology should be added until the toy engine can evaluate the data-center load case and emit:

```text
ResultingState
GuardrailResolution
Validity
Bottleneck list
RemedyBus status, if applicable
Explanation trace
```

This stop rule is intended to prevent premature ontology expansion before the minimal runtime semantics are testable.

---

# Current Features

```text
✓ Transition-system failure modeling
✓ Queue synchronization logic
✓ Fossil fallback and lock-in dynamics
✓ Worker transition states
✓ Biosphere nested-cycle modeling
✓ Planetary-boundary pressure accumulation
✓ Dynamic Appendix C ranking generation
✓ Weighted cascade attractors
✓ Pressure accumulation semantics
✓ Temporal synchronization windows
✓ Stale-success and timeout logic
✓ Guardrail resolution states
✓ RemedyBus corrective pathway
✓ v0.1 primitive lock
✓ Data-center load toy-case definition
```

---

# Current Status

```text
Prototype ontology / toy execution engine.

Not calibrated.
Not predictive.
Not policy advice.
Not operational control software.

Designed for:
- systems reasoning
- synchronization analysis
- transition stress testing
- pathway consistency analysis
- guardrail validity checking
- planetary-boundary cascade modeling
```

---

# Development Notes

ClimateSOS evolved through iterative systems-design sessions focused on:

* synchronization failures
* fossil persistence dynamics
* transition timing windows
* pressure accumulation
* biosphere restoration
* planetary-boundary cascades
* distributed operating-system abstractions
* guardrail-bounded runtime validity
* corrective remedy pathways

A major architectural transition occurred during v0.6 development when the system moved from:

```text
static manually ranked failure modes
```

to:

```text
dynamic weighted cascade attractor ranking
```

This allowed biosphere systems to become upstream causal drivers rather than merely downstream consequences.

A second architectural transition occurred during v0.7 development when guardrail handling was separated from resulting states through:

```text
GuardrailResolution
RemedyBus
```

This allows ClimateSOS to distinguish:

```text
technical synchronization
```

from:

```text
valid transition success
```

A pathway can be technically CleanBound and still not valid if its guardrails remain unresolved.

---

# Philosophy

ClimateSOS assumes:

```text
The transition problem is not primarily a technology problem.

It is a synchronization problem.
```

The framework therefore focuses on:

* timing
* throughput
* coupled bottlenecks
* persistence pathways
* synchronization windows
* pressure accumulation
* cascading destabilization
* guardrail validity
* remedy and re-evaluation

rather than single-variable optimization.

ClimateSOS also assumes:

```text
Technical success is not enough.
```

A pathway is not valid merely because it reduces emissions, scales clean technology, or clears technical queues.

A valid pathway must also remain within planetary boundaries, protect biosphere integrity, avoid committing harm, preserve human dignity, maintain accountability, and avoid substituting success in one domain for failure in another.

---

# Version

```text
ClimateSOS Toy Engine v0.7
```

