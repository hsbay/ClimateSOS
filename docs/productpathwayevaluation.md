# ClimateSOS Product Pathway Evaluation Specification

**GitHub project:** [https://github.com/hsbay/ClimateSOS](https://github.com/hsbay/ClimateSOS)  
**Author / maintainer:** Shannon A. Fiume (@safiume)  
**License:** Creative Commons Attribution 4.0 International (CC BY 4.0), 2026  
**Development note:** ClimateSOS was conceived, researched, directed, architected, and developed by Shannon A. Fiume through an iterative human–AI collaboration. OpenAI’s ChatGPT provided AI-assisted drafting, code-generation, implementation assistance, and systems-design iteration under Shannon’s direction.  
**Status:** Draft  

---

## 1. Purpose

This specification defines the ClimateSOS Product Pathway Evaluation Flow
used for both global and local pathway evaluations within the broader
ClimateSOS execution architecture.

ClimateSOS must support evaluation of real-world product, company, technology,
financial, infrastructure, and customer-decision pathways in addition to
generic transition abstractions.

A customer or product pathway may involve a specific technology, industrial
process, clean-fuel product, carbon product, methane-abatement pathway,
electric power load case, infrastructure service, prospective business logic,
transition-finance instrument, fossil-retirement mechanism, or
transition-enabling business model. These pathways may affect not only
emissions intensity or carbon footprint, but also whether fossil assets,
fuels, financing structures, workforce roles and transition pathways,
reliability functions, and supply-chain dependencies can be wound down and
replaced in time.

ClimateSOS is intended to enable anyone to examine whether a proposed pathway
decarbonizes an activity in isolation, contributes materially to the
synchronized transition conditions required for managed fossil exit and
operational net zero, or introduces dependencies, delays, risks, or harms
that weaken that transition.

This specification defines how proposed pathways are translated, represented,
assembled, evaluated, compared with the validated global net-zero transition,
and resolved into traceable results. Depending on the pathway, the
evaluation may use identity records, queues, and fabrics. It
incorporates Charter evaluations, evidence assessments, pathway comparisons,
system-contribution diagnostics, scale diagnostics, and transition-risk
assessments.

ClimateSOS first evaluates the pathway against the ClimateSOS Foundational
Charter and applicable guardrail domains. It then evaluates how the pathway
interacts and synchronizes with the broader transition system and records
whether the pathway preserves, strengthens, delays, constrains, or diverges
from the Playbook’s accelerated ~2037–2038 operational net-zero window.

The Product Pathway Evaluation Flow provides a common architecture for both
ordinary pathway evaluation and globally scoped pathway construction. Reusing
the same core components, interfaces, and result structures reduces duplicated
logic and helps ensure that ordinary and global evaluations do not develop
incompatible assumptions or behavior.

The flow also applies the ClimateSOS Foundational Charter consistently
across pathway types and evaluation contexts. Globally scoped pathways and
ordinary product pathways therefore pass through the same Charter-based
safeguards, guardrails, evidence requirements, and integrity checks. The
Charter is evaluated at three distinct stages: initially against the
normalized `ProductPathway`, again after pathway integration and assessment,
and finally after system-contribution, scale, and transition-risk evaluation.
Each pass examines the information available at that stage and produces a
separate immutable result.

The pathway evaluation architecture follows a compiler-like flow that separates intake, identity, internal representation objects, and the components that perform translation, assembly, evaluation, comparison, and resolution. Customer-supplied material is preserved in an immutable `ProductIntakeBundle` associated with an `IdentityToken`. The `ProductAdapter` translates that bundle into a normalized `ProductPathway` and returns a `ProductAdapterResult` that preserves the association between the pathway and its intake sources. Downstream components then assemble execution artifacts, evaluate the pathway, construct candidate transition effects, and produce immutable results. This separation keeps source materials, data models, and work-performing components distinct and makes each stage easier to inspect, test, reuse, and revise independently.

Product pathway evaluation does not determine whether a company, product,
financial instrument, or proprietary pathway is commercially valid,
investment-worthy, policy-ready, or deployable. It produces an inspectable,
evidence-linked evaluation for accountable human review.

---

## 2. Scope

This specification applies to product pathway evaluations that produce
`ProductPathway` representations supporting prospective customer,
institutional, financial, workforce, sovereign, or system-decision logic
affecting material net-zero pathway changes. It applies both to ordinary
product pathway evaluations and to globally scoped product pathways used to
construct or update the validated ClimateSOS `TransitionPathway`.

Examples include:

* aviation and transportation fuel production pathways
* methane-abatement pathways
* industrial product pathways
* carbon-storage or carbon-removal-adjacent product pathways
* industrial electrification products or services
* electric power load and load-coordination pathways
* grid-support or adequacy-support products
* transmission, interconnection, storage, or other transition-enabling
infrastructure pathways
* circular-materials or waste-utilization products
* transition-finance instruments or financing structures
* fossil-retirement, refinancing-closure, environmental-closure, or asset-winddown
mechanisms
* workforce transition, retraining, redeployment, or regional just-transition
pathways
* sovereign, regional, municipal, utility, or institutional transition-planning
pathways
* customer-specific deployment pathways that depend on finance, permitting,
workforce, feedstock, offtake, infrastructure, or system integration
* globally scoped pathways representing major transition components such as
renewable generation, grid expansion, storage, finance, workforce, fossil exit,
industrial conversion, or biosphere restoration
* other decision pathways that may materially affect a customer’s, institution’s,
region’s, or the global system’s path to operational net zero

This specification applies where a pathway may affect emissions, fossil
displacement, fossil retirement, reliability replacement, workforce transition,
capital allocation, infrastructure delivery, supply-chain conversion, biosphere
integrity, or closure of fossil persistence pathways.

The pathway representation and evaluation should remain abstract enough to
avoid exposing proprietary details from any specific company, customer, partner,
technology, financial structure, or transition plan, while preserving sufficient
operational detail, evidence, and provenance for meaningful evaluation.

---

## 3. Non-Scope

The Product Pathway Evaluation Flow is not intended to:

* disclose proprietary process details
* model a company’s private technical design
* validate a specific commercial claim without evidence
* replace technical due diligence
* replace engineering review
* replace MRV, lifecycle analysis, financial diligence, community review, or regulatory review
* authorize deployment
* recommend investment
* provide procurement instruction

ClimateSOS structures and surfaces pathway evidence and evaluation findings. The
researcher, reviewer, customer, or domain expert conducts the investigation
and retains accountable decision-making authority.

---

## 4. Core Design Principles

The Product Pathway Evaluation Flow uses a common architecture for user-submitted pathway evaluation and globally scoped net-zero transition construction. The same core components, intermediate representations, evaluator contracts, and evidence structures should be reused when functionally equivalent. This reduces duplicated logic and helps prevent the two flows from developing incompatible behavior.

### 4.1 Device-Driver-Like Translation Boundary

The `ProductAdapter` functions as a device-driver-like translation boundary between the ClimateSOS intake representation and the internal representation consumed by the evaluation system.

The ClimateSOS Identity Layer establishes and issues the canonical `IdentityToken`. The Intake Layer receives the token and the customer-supplied pathway material, preserves their immutable association, and produces a `ProductIntakeBundle`.

The `ProductAdapter` consumes the `ProductIntakeBundle` and translates its contents into a normalized `ProductPathway`, which represents the proposed pathway as an internal map or graph. It returns a `ProductAdapterResult` containing the completed `ProductPathway` and a reference to the associated `ProductIntakeBundle`.

The adapter translates and maps the pathway. It does not establish identity, modify the intake bundle, evaluate the pathway, assemble its objects into evaluation groups, compare it with the validated global transition, or assign a resulting state.

### 4.2 Compiler-Like Separation of Responsibilities

The architecture follows a compiler-like flow in which explicit components transform or evaluate explicit intermediate representations.

The principal stages are:

* identity-token establishment;
* creation of an immutable `ProductIntakeBundle`;
* adaptation into a `ProductAdapterResult` containing the normalized `ProductPathway` and a reference to its associated `ProductIntakeBundle`;
* initial Charter evaluation;
* assembly of pathway objects into `ProductQueueBundle` and `ProductFabric` groupings, as applicable;
* comparison of the pathway with the global `TransitionPathway`;
* pathway, documentation, contribution, scale, and system-risk evaluation;
* final Charter evaluation;
* binding into an applicable `[Foo]Bound` state; and
* validation and commitment of the global `TransitionPathway`, or result construction for a user-submitted pathway.

Models hold state and results. Adapters, assemblers, comparators, evaluators, validators, and handlers perform work.

### 4.3 Immutable State and Result Objects

Completed ClimateSOS pathway, assembly, evaluation, Charter, contribution, scale, risk, binding, and result objects are immutable.

Work-performing components may maintain transient state while executing, but once a canonical data object or result is produced, later stages do not modify it. They preserve references to prior objects and create new objects to represent subsequent assembly, evaluation, state transitions, or results.

This applies to objects such as `ProductIntakeBundle`, `ProductAdapterResult`, `ProductPathway`, `ProductQueueBundle`, `ProductFabric`, `QueueProgressRecord`, `QueueExecutionResult`, `QueueEvaluatorResult`, `FabricEvaluatorResult`, Charter results, pathway assessments, system-contribution and scale results, candidate or validated `TransitionPathway` snapshots, risk results, bound-state records, and `EvaluatedPathway`.

Where ClimateSOS models changing system state, each preserved state is represented as a new immutable snapshot or result rather than by rewriting a previously completed object.

Work-performing components such as adapters, assemblers, evaluators, validators, and handlers are not subject to this object-immutability rule merely because they produce immutable outputs.

### 4.4 Progressive Charter Evaluation

The ClimateSOS Foundational Charter is evaluated at three stages:

1. **Initial Charter Evaluation** — evaluates the `ProductPathway`, which is the normalized intake produced by the `ProductAdapter` as an internal map or graph, before assembly and pathway evaluation.
2. **Integrated Charter Evaluation** — evaluates findings revealed through pathway comparison, assembled-group evaluation, documentation assessment, and downstream propagation.
3. **Final Charter Evaluation** — evaluates the completed contribution, scale, candidate-transition, and global-system-risk findings before binding.

Each stage produces a separate immutable result. A later Charter result may reference, but must not overwrite, an earlier result.

Required Charter checks that are absent, null, malformed, overwritten, or unexecuted are recorded as `MISSING`. A required `MISSING` check forces the enclosing Charter result to `ERROR` and prevents normal progression.

Detailed Charter check statuses, blocking behavior, evaluator-integrity requirements, remedy eligibility, and re-evaluation rules are defined in a separate Charter Evaluation Flow document.

### 4.5 Global and User-Submitted Pathway Outcomes

The two flows share the same architecture until their final outcomes diverge.

The global context is used strictly to update the reference `TransitionPathway`. It occurs after the program starts and before a user can evaluate one or more product pathways. In this global evaluation context, one candidate global `TransitionPathway` is evaluated against one authoritative global reference `TransitionPathway` at a time. The candidate may represent a limited proposed delta or a prospective replacement for a larger portion of the global net-zero transition. The reference is either the Playbook-derived global pathway or the previously validated `TransitionPathway`.

After pathway evaluation, contribution analysis, scale diagnosis, global-system-risk evaluation, final Charter evaluation, and binding, the candidate must pass `TransitionPathwayValidator` before it can be atomically committed as the validated global `TransitionPathway`. Once committed, the newly validated global `TransitionPathway` replaces the previous reference pathway. It is preserved for use at the next startup and serves as the current reference pathway if the user proceeds with evaluation of a user-submitted `ProductPathway`.

In the user-submitted context, a user may provide one or more intake submissions, each of which generates a separate `ProductPathway` for evaluation against the current validated global `TransitionPathway`. In user-submitted mode, the global `TransitionPathway` is immutable. One or more user-submitted candidate pathways may be evaluated separately and do not modify the global `TransitionPathway`. Each candidate pathway’s modeled effects and evaluation findings are recorded in its `EvaluatedPathway`.

After global-system-risk evaluation, final Charter evaluation, and binding, each user-submitted pathway proceeds to construction of an `EvaluatedPathway`.

Completion of intake, adaptation, assembly, or an intermediate evaluation does not by itself establish pathway validity.

Together, these principles and the Product Pathway Evaluation Flow support the central evaluation question:

> Does this pathway preserve or strengthen the accelerated operational net-zero transition, and if so, how? Or does it remain unresolved, delayed, harm-bound, fossil-bound, weakly connected to material fossil displacement, or otherwise unable to make a credible net overall system contribution?

---

## Shared Product Pathway Evaluation Flow

```text
===============================================================================
                    SHARED PRODUCT PATHWAY EVALUATION FLOW
===============================================================================


External pathway material
    │
    ▼
Identity Gateway  ⥬  Identity Layer
    IdentityToken ⥫        ↲ 
    │
    │  Identity Layer Establishes and issues the canonical IdentityToken.
    │
    ▼
Intake Layer
    │
    │  Receives and preserves the customer-supplied material.
    │  Associates the material with the IdentityToken.
    │
    │  Produces an immutable ProductIntakeBundle.
    │
    ▼
ProductIntakeBundle
    │
    │  Immutable intake materials, metadata, documentation,
    │  evidence, provenance, and associated IdentityToken.
    │
    ▼
ProductAdapter
    │
    │  Device-driver-like translation boundary.
    │  Translates the ProductIntakeBundle into ClimateSOS's
    │  normalized internal pathway representation.
    │
    ▼
ProductAdapterResult
    ├── ProductPathway
    │       Normalized pathway represented as an internal map or graph.
    │
    ├── ProductIntakeBundle reference
    │       Preserves the pathway's association with its immutable
    │       intake materials and IdentityToken.
    │
    ▼
CharterEvaluator
    │
    │  INITIAL CHARTER PASS
    │
    ▼
InitialCharterResult
    │
    │  Separate immutable record of the initial Charter evaluation.
    │
    ▼
ProductAssembly
    │
    │  Groups eligible objects already represented on the
    │  ProductPathway into structures consumed by later stages.
    │
    ├── QueueBundler
    │       └── ProductQueueBundle(s)
    │
    ├── FabricAssembler, where applicable
    │       └── ProductFabric(s)
    │
    ▼
PathwayEvaluationEngine
    │
    ├── PathwayComparator
    │       ├── Direct Pathway Comparison
    │       │       └── identifies direct overlaps, dependencies, additions,
    │       │           replacements, and conflicts with the authoritative TransitionPathway
    │       ├── Substitution and Combination Evaluation
    │       │       └── evaluates displacement, coexistence, and coordinated operation
    │       └── Downstream Propagation
    │               └── evaluates material effects through connected transition
    │                   and system relationships
    │
    ├── QueueEvaluator
    │       ├── evaluates the ProductPathway queue family
    │       │       ├── ProductQueueBundle(s)
    │       │       └── applicable unbundled queue element(s)
    │       ├── QueueProgressRecord(s)
    │       ├── QueueExecutionResult(s)
    │       └── QueueEvaluatorResult(s)
    │
    ├── FabricEvaluator, where applicable
    │       └── evaluates ProductFabric(s)
    │
    └── DocumentationEvaluator
            └── evaluates evidence, provenance, uncertainty,
                methodology, and unresolved claims
    │
    ▼
PathwayAssessment
    │
    │  Consolidated immutable pathway-evaluation findings.
    │
    ▼
CharterEvaluator
    │
    │  INTEGRATED CHARTER PASS
    │
    ▼
IntegratedCharterResult
    │
    │  Separate immutable record that references but does not
    │  overwrite InitialCharterResult.
    │
    ▼
NetOverallSystemContributionEvaluator
    │
    ▼
NetOverallSystemContribution
    │
    ▼
ScaleDiagnosticEvaluator
    │
    ▼
ScaleDiagnosticResult
    │
    ▼
Construct Candidate or Prospective Candidate TransitionPathway
    │     Candidate here refers to the user-submitted candidate
    │     Prospective Candidate TransitionPathway refers to a
    │     possible future reference TransitionPathway.
    ▼
NetOverallSystemRiskEvaluator
    │
    ▼
NetOverallSystemRiskResult
    │
    ▼
CharterEvaluator
    │
    │  FINAL CHARTER PASS
    │
    ▼
FinalCharterResult
    │
    │  Separate immutable record that references but does not
    │  overwrite the earlier Charter results.
    │
    ▼
BindingHandler
    │
    ▼
Applicable ExampleBound State
    │
    ├─────────────────────────────────────────────────────────────┐
    │                                                             │
    ▼                                                             ▼
Global context                                         User-submitted context
    │                                                             │
    ▼                                                             ▼
TransitionPathwayValidator                              ResultEvaluator
    │                                                             │
    ▼                                                             ▼
Atomic immutable commitment                             EvaluationResult
```

## Global Boot and TransitionPathway Update Flow

```text
===============================================================================
             GLOBAL BOOT AND TRANSITIONPATHWAY UPDATE CONTEXT
===============================================================================

Program startup
    │
    ▼
Load global reference sources
    │
    ├── Playbook logic and net-zero pathway requirements
    ├── initialization records and startup configuration
    └── previous validated TransitionPathway, where available
    │
    ▼
Establish authoritative global reference TransitionPathway
    │
    ├── Playbook-derived reference pathway
    │       └── used when no prior validated TransitionPathway exists
    │
    └── previously validated TransitionPathway
            └── used as the current reference where available
    │
    ▼
Receive a single submission of proposed global candidate pathway or 
minor change
    │
    │  The proposal may represent:
    │  • a limited delta to the global transition; or
    │  • a prospective replacement.
    │
    Privileged Global Update Interface
      or authorized boot/update API
    │      ↓
Run the Shared Product Pathway Evaluation Flow
    │  Identity Gateway   =>   IdentityLayer
    │      IdentityToken  <=        -|
    │      ↓
    │  Global Intake Layer
    │      ↓
    │  ProductIntakeBundle
    │      ↓
    │  ProductAdapter
    │      ↓
    │  ProductAdapterResult
    │    ├── ProductPathway
    │    └── ProductIntakeBundle reference
    │      ↓
    │  InitialCharterResult
    │      ↓
    │  ProductAssembly
    │      ↓
    │  PathwayEvaluationEngine
    │      ↓
    │  PathwayAssessment
    │      ↓
    │  IntegratedCharterResult
    │      ↓
    │  NetOverallSystemContribution
    │      ↓
    │  ScaleDiagnosticResult
    │
    ▼
Construct Candidate Global TransitionPathway
    │
    │  Create new integrated Candidate global transition after applying 
    │  the candidate delta, but before validation and atomic commitment.
    │  This Candidate is separate from the global and current reference
    │  TransitionPathway.
    │
    ▼
NetOverallSystemRiskEvaluator
    │
    ▼
NetOverallSystemRiskResult
    │
    ▼
FinalCharterResult
    │
    ▼
BindingHandler
    │
    ▼
Applicable ExampleBound State
    │
    ▼
TransitionPathwayValidator
    │
    ├── validation does not permit commitment
    │       │
    │       ├── preserve the candidate, findings, Charter results,
    │       │   risk result, evidence, and bound state
    │       │
    │       └── retain the existing authoritative
    │           TransitionPathway unchanged
    │
    └── validation permits commitment
            │
            ▼
Atomic immutable commitment
            │
            ▼
New Validated Global TransitionPathway
            │
            ├── replaces the previous current reference
            │
            ├── is preserved for use at the next startup
            │
            └── becomes the immutable reference for any
                user-submitted evaluations in the current session
```

## User-Submitted Pathway Evaluation Context

```text
===============================================================================
                  USER-SUBMITTED PATHWAY EVALUATION CONTEXT
===============================================================================

Current validated global TransitionPathway
    │
    │  Immutable throughout user-submitted evaluation.
    │
User UI or public API gateway
    │
Run Shared Product Pathway Evaluation
    Identity Gateway => IdentityLayer
    │ IdentityToken  <=      -|
    │    
    ▼
User submits one or more separate pathway intakes
Continue with Shared Product Pathway for each submission
    │
    ├─────────────────────Intake Layer────────────────────────────┐
    │                                                             │
    ▼                                                             ▼
Submission A                                                  Submission B
    │                                                             │
    ▼                                                             ▼
ProductPathway A                                         ProductPathway B
ProductIntakeBundle A                                    ProductIntakeBundle B
    │                                                             │
    ▼                                                             ▼
Compare separately with the same current validated global TransitionPathway
    │                                                             │
    ▼                                                             ▼
PathwayAssessment A                                      PathwayAssessment B
    │                                                             │
    ▼                                                             ▼
IntegratedCharterResult A                              IntegratedCharterResult B
    │                                                             │
    ▼                                                             ▼
NetOverallSystemContribution A                      NetOverallSystemContribution B
    │                                                             │
    ▼                                                             ▼
ScaleDiagnosticResult A                                ScaleDiagnosticResult B
    │                                                             │
    ▼                                                             ▼
Prospective Candidate                                  Prospective Candidate
TransitionPathway A                                    TransitionPathway B
    │                                                             │
    ▼                                                             ▼
NetOverallSystemRiskResult A                        NetOverallSystemRiskResult B
    │                                                             │
    ▼                                                             ▼
FinalCharterResult A                                    FinalCharterResult B
    │                                                             │
    ▼                                                             ▼
BindingHandler                                           BindingHandler
    │                                                             │
    ▼                                                             ▼
Applicable ExampleBound State A                    Applicable ExampleBound State B
    │                                                             │
    ▼                                                             ▼
ResultEvaluator                                          ResultEvaluator
    │                                                             │
    ▼                                                             ▼
EvaluatedPathway A                                      EvaluatedPathway B

===============================================================================

User-submitted evaluation invariants:

• Each submission receives its own `IdentityToken` and produces its own immutable `ProductIntakeBundle`. Each `ProductIntakeBundle` is adapted into a separate `ProductAdapterResult`, `ProductPathway`, and evaluation history.

• Each ProductPathway is evaluated separately against the same current
  validated global TransitionPathway.

• Each prospective candidate TransitionPathway represents the modeled effect
  of that user-submitted ProductPathway on the global reference.

• A user-submitted candidate does not modify or replace the validated global
  TransitionPathway.

• Each `EvaluatedPathway` preserves that candidate pathway's findings, Charter results, contribution, scale, global-system risk, bound state, evidence, provenance, and state history, together with references sufficient to trace the evaluation back through the `ProductAdapterResult`, `ProductIntakeBundle`, and `IdentityToken`.

• Multiple user-submitted pathways may be evaluated during the same session,
  but they do not become one combined candidate unless a separate intake
  explicitly represents a combined pathway.
```

---

## 5. Product Pathway Adapter

The `ProductAdapter` translates a completed ClimateSOS intake representation into a normalized `ProductPathway`.

The `ProductPathway` is the internal map or graph of the proposed product, project, technology, policy, financial mechanism, customer decision, or other transition pathway. It preserves the operational elements, relationships, dependencies, claims, evidence references, identity references, and provenance needed by later evaluation stages.

The `ProductAdapter` is a translation and structural-mapping component. It may inspect and evaluate submitted pathway information as necessary to identify operational elements, queues, relationships, dependencies, fabrics, and other structures represented in the graph. It does not determine the pathway’s Charter status, net overall system contribution, scale, global-system risk, bound state, or final validity.

### 5.1 Input and Output

The `ProductAdapter` consumes one immutable `ProductIntakeBundle` from the Intake Layer.

The `ProductIntakeBundle` contains the customer-supplied pathway materials and preserves their association with the canonical `IdentityToken`, intake metadata, documentation, evidence, and provenance.

The `ProductAdapter` produces one immutable `ProductAdapterResult`.

```text
ProductIntakeBundle
        │
        ▼
ProductAdapter
        │
        ▼
ProductAdapterResult
    ├── ProductPathway
    └── ProductIntakeBundle reference
```

The `ProductAdapterResult` associates the `ProductPathway` with the `ProductIntakeBundle` from which it was derived. It does not duplicate or modify the bundle.

The `ProductAdapter` receives the canonical `IdentityToken` through the `ProductIntakeBundle` and preserves it unchanged.

When constructing the `ProductPathway`, the `ProductAdapter` preserves `user_id` and `pathway_id` on every atomic graph object it creates. Each node, relationship, dependency, claim, evidence reference, output, and other represented element remains attributable to the user and pathway from which it was derived.

The format of individual graph-object identifiers remains an implementation decision. An object created from one pathway must not be silently merged with or mistaken for an object created from another pathway.

### 5.2 Adapter Responsibilities

The `ProductAdapter` will:

* receive the immutable `ProductIntakeBundle`;
* preserve references to the canonical `IdentityToken` and any internal pathway or user identity references carried by the bundle;
* translate external terminology into canonical ClimateSOS terminology;
* identify the pathway’s operational elements;
* represent those elements as nodes or equivalent mapped objects;
* map relationships and dependencies between pathway elements;
* associate claims, documentation references, evidence references, and provenance with the relevant elements;
* preserve declared timing, geographic scope, system boundaries, assumptions, and uncertainties;
* identify declared product outputs without evaluating their validity or system contribution;
* construct the normalized mapping to produce the `ProductPathway`; and
* return an immutable `ProductAdapterResult` containing the `ProductPathway` and a reference to the associated `ProductIntakeBundle`.

The `ProductAdapter` will not modify the `ProductIntakeBundle`, the `IdentityToken`, or any customer-supplied source record. Normalized facts and pathway structures are written to the new `ProductPathway`. The supplied materials remain unchanged.

Where the pathway representation assigns identifiers to individual mapped elements, those identifiers must remain attributable to the originating user and pathway. They must not cause material from separate pathway intakes to be silently merged.

The adapter must preserve material uncertainty or incompleteness. It must not supply missing facts or convert unsupported claims into established pathway properties.

### 5.3 Responsibility Boundary

The `ProductAdapter` does not:

* establish, mint, authorize, replace, reinterpret, or modify the canonical `IdentityToken`;
* modify the `ProductIntakeBundle` or any customer-supplied source material;
* perform any Charter evaluation;
* determine guardrail status;
* create Charter results;
* assemble represented queues into `ProductQueueBundle` structures;
* assemble represented fabric elements into `ProductFabric` structures;
* assemble represented system-side bus elements into a bus fleet structure;
* evaluate assembled queue bundles, fabric bundles, or system-side bus fleets; or
* compare the completed pathway with the authoritative `TransitionPathway`.

The `ProductAdapter` may identify, inspect, and relate individual queues, fabric elements, and their interactions where required to construct the normalized `ProductPathway` graph.

This structural work ends with the completed `ProductAdapterResult`. The result contains the completed `ProductPathway` and preserves its association with the immutable `ProductIntakeBundle`.

Responsibilities downstream from the `ProductAdapterResult` belong to the components defined by the Product Pathway Evaluation Flow.

### 5.4 ProductPathway Representation

The `ProductPathway` is the normalized internal map or graph of the proposed pathway.

It represents the operational elements identified by the `ProductAdapter` and the relationships between them. The representation may be implemented as objects, records, graph structures, or another form suitable for inspection and downstream processing. Its serialized form does not change its architectural role.

At minimum, the `ProductPathway` represents:

* the pathway identity and provenance references carried into adaptation;
* the pathway type;
* the relevant time window;
* geographic and system scope;
* operational elements;
* required inputs and declared outputs;
* relationships and dependencies between represented elements;
* relevant actors, functions, or decision points, where supplied;
* declared assumptions and uncertainties;
* declared infrastructure, finance, workforce, permitting, authorization, and evidence requirements, where applicable;
* stable references to supporting documentation and evidence in the associated `ProductIntakeBundle`; and
* source references sufficient to trace each represented element to the material from which it was derived.

Each atomic graph object preserves `user_id` and `pathway_id`. Individual elements may also carry object identifiers where needed to distinguish nodes, relationships, claims, dependencies, or evidence references within the pathway.

Not every category applies to every pathway. The `ProductPathway` represents only the elements supported by the intake materials. The `ProductAdapter` does not create missing facts or convert unsupported claims into established pathway properties.

The graph preserves local pathway structure. It represents when an element produces an output, requires an input, depends on another element, or interacts with a declared actor or process. Later stages evaluate system-wide effects, substitutions, scale effects, and interactions with the global transition.

The `ProductAdapter` creates the immutable `ProductPathway` and `ProductAdapterResult`. Later stages produce separate evaluation and assembly objects. They do not write Charter results, queue states, pathway assessments, system contributions, scale results, risk results, bound states, remedy records, or evaluation history back into the `ProductPathway`.

### 5.5 Abstraction and Anonymization

The adapter should represent a pathway with enough operational detail for meaningful evaluation while avoiding unnecessary exposure of proprietary technical or commercial information.

Where appropriate, a pathway may be anonymized as:

* Transportation Fuel Product Pathway A
* Methane Abatement Product Pathway B
* Industrial Carbon Product Pathway C
* Flexible Load Customer Pathway D

Anonymization must not remove information necessary to evaluate material dependencies, evidence, timing, system contribution, Charter conditions, or transition risk.

---

## 6. Initial Charter Evaluation

The Initial Charter Evaluation is the first substantive evaluation performed on a completed `ProductAdapterResult` containing the `ProductPathway` and a reference to the associated `ProductIntakeBundle`.

It evaluates the pathway against the ClimateSOS Foundational Charter before downstream assembly and pathway evaluation. The evaluator follows references to the associated `ProductIntakeBundle` when a check requires source documentation, evidence, or provenance.

Every Initial Charter check defined for this evaluation stage is required. Each check executes independently, and a prior finding does not short-circuit or remove any remaining check.

The Initial Charter Evaluation distinguishes pathway findings from evaluator execution failures. A successfully executed check may return a failed, adverse, unresolved, not-applicable, or other valid Charter finding. Those findings remain part of the pathway evaluation record and may affect later evaluation and binding. They do not by themselves indicate that the ClimateSOS runtime failed.

The Initial Charter Evaluation completes only when every required check has executed and a valid immutable `InitialCharterResult` has been produced. An evaluator or result-integrity failure prevents the current pathway evaluation from proceeding.

```text
ProductAdapterResult
    ├── ProductPathway
    ├── ProductIntakeBundle reference
    │
    ▼
CharterEvaluator
   Initial Charter Pass
    │
    ▼
InitialCharterResult
```

### 6.1 Evaluation Boundary

The Initial Charter Evaluation examines the `ProductPathway` contained in the completed `ProductAdapterResult`. It accesses the associated `ProductIntakeBundle` when a required check depends on customer-supplied documentation, evidence, or provenance.

It evaluates:

* whether required identity and provenance information is represented and traceable;
* whether the documentation and evidence references needed for the initial evaluation are available;
* whether the pathway contains prohibited or disqualifying conditions visible before `ProductAssembly`;
* whether declared assumptions, uncertainties, dependencies, inputs, outputs, and system boundaries are sufficiently represented for the applicable checks;
* whether the pathway conflicts with, exceeds, or diverges from Foundational Charter safeguards or guardrails;
* whether every required Initial Charter check executed and produced a valid result; and
* whether the Initial Charter Evaluation completed without an execution or evaluator-integrity error.

The Initial Charter Evaluation does not determine whether the pathway successfully contributes to net zero, compare it with the authoritative `TransitionPathway`, or assign its binding state.

It does not perform downstream pathway assembly, synchronization comparison, scale evaluation, net overall system contribution evaluation, net overall system risk evaluation, candidate-transition construction, or final binding.

### 6.2 Initial Evaluation Inputs

The Initial Charter Evaluation receives the completed `ProductPathway`, the associated `ProductIntakeBundle`, and the Charter resources required to evaluate the pathway.

Its inputs include:

* the immutable `ProductPathway`;

  * the pathway identity and provenance references carried by the pathway;
  * the normalized internal representation of the pathway;

* the immutable `ProductIntakeBundle`;

  * the associated `IdentityToken`;
  * the documentation, evidence, and provenance available for each applicable check;

* the ClimateSOS Foundational Charter distributed with the ClimateSOS runtime;

  * the complete set of required Initial Charter checks;

* the evaluator version and Charter rule-set version; and

* any runtime configuration required to execute the Initial Charter Evaluation.

The evaluator uses the facts represented by the `ProductPathway` and the source material preserved in the associated `ProductIntakeBundle`. It does not add missing pathway facts, treat assumptions as established facts, or substitute inferred evidence for evidence that was not provided.

### 6.3 InitialCharterResult

The Initial Charter Evaluation produces one immutable `InitialCharterResult`.

The `InitialCharterResult` represents the complete outcome of the Initial Charter pass.

The immutable `InitialCharterResult` contains:

* a reference to the evaluated `ProductAdapterResult`, preserving its association with the evaluated `ProductPathway`, `ProductIntakeBundle`, and pathway identity;
* the result of every required Initial Charter check;
* findings, evidence references, and supporting provenance associated with each check;
* unresolved or not-applicable conditions returned by completed checks, where applicable;
* any execution error associated with an individual check or with the Initial Charter Evaluation;
* the evaluator version;
* the Charter rule-set version; and
* the resulting Initial Charter status.

A Charter check result records the outcome of the check that was actually executed. The evaluator does not infer the result of one check from another check or substitute an earlier finding for execution of a required check.

A successfully completed check may identify a Charter conflict, prohibited condition, unresolved condition, or other adverse finding. Such a finding is part of the pathway evaluation and does not by itself constitute an evaluator execution error.

The completed `InitialCharterResult` is immutable. Later evaluation stages may reference it and carry its findings forward, but they do not overwrite or replace the result of the Initial Charter Evaluation.

### 6.4 Execution Routing

Every Initial Charter check is required and executes before the Initial Charter Evaluation is complete. A prior finding does not short-circuit any remaining check.

When every required check has executed and the evaluator successfully produces a valid immutable `InitialCharterResult`, ClimateSOS preserves that result and continues the pathway through the Product Pathway Evaluation Flow.

A pathway may progress beyond the Initial Charter Evaluation while carrying failed, adverse, unresolved, not-applicable, or other valid Charter findings. Those findings remain part of the pathway evaluation record and are available to later evaluation stages and binding.

Progression does not erase, weaken, satisfy, or overwrite an earlier Charter finding. Later Charter evaluations examine information made available by subsequent stages and produce separate immutable results.

The product pathway evaluation does not proceed to `ProductAssembly` when the Initial Charter Evaluation cannot successfully complete or when a valid required check result or `InitialCharterResult` cannot be produced.

### 6.4.1 Missing, Unresolved, and Error Handling

`MISSING` indicates that a required Charter check did not produce a valid result. This occurs when the required check did not execute, timed out, executed without recording a result state, or produced a result that is absent, null, malformed, overwritten, or otherwise unavailable as a valid check result.

A required `MISSING` check is an evaluator-integrity failure. The enclosing `InitialCharterResult` is recorded as `ERROR`, and the current pathway evaluation does not proceed until the execution error is resolved.

`UNRESOLVED` is distinct from `MISSING`. An `UNRESOLVED` result means that the required check executed successfully but the available pathway information or evidence was insufficient to resolve the Charter question. The unresolved finding and its supporting information are preserved in the `InitialCharterResult` and carried forward.

`NOT_APPLICABLE` is also distinct from `MISSING`. Where a Charter check permits a legitimate not-applicable outcome, the check still executes and returns such a result.

A failed or adverse Charter finding is not an execution error when the evaluator successfully executes the check and produces a valid result.

An execution error must not be converted into `UNRESOLVED`, `NOT_APPLICABLE`, a failed Charter finding, or another ordinary evaluation state. Likewise, an adverse Charter finding must not be represented as a software failure.

When execution cannot proceed, ClimateSOS preserves the available pathway identity, evaluation state, error information, and supporting evidence needed to diagnose the failure. The pathway may be evaluated again in a separate execution of ClimateSOS after the execution error is resolved.

---

## 7. Product Assembly

`ProductAssembly` constructs the pathway-derived objects that are later consumed by downstream evaluators. It coordinates the assembly functions that group represented pathway structures into queue bundles and fabrics where grouping is applicable, while preserving unbundled queue elements that remain independently evaluable and the identity, relationships, provenance, and traceability established by the `ProductAdapter`.

Assembly begins only after the Initial Charter Evaluation has completed successfully and produced a valid immutable `InitialCharterResult`. `ProductAssembly` follows the result's reference to the evaluated `ProductAdapterResult`, which identifies the immutable `ProductPathway` and its associated `ProductIntakeBundle`. Assembly operates on the `ProductPathway`; the intake-bundle association remains available for traceability.

`ProductAssembly` creates `ProductQueueBundle` and, where applicable, `ProductFabric` objects by executing `QueueBundler` and subsequently `FabricAssembler`. `ProductFabric` objects are constructed only from applicable `ProductQueueBundle` objects. The constructed queue bundles and fabrics are passed to downstream evaluators.

```text
ProductAdapterResult
    ├── ProductPathway
    └── ProductIntakeBundle reference
            │
            ▼
InitialCharterResult
            │
            │ valid completion permits progression
            ▼
ProductAssembly
    │
    ▼
QueueBundler
    │
    └── ProductQueueBundle(s)
                │
                ▼
         FabricAssembler
                │
                └── ProductFabric(s)
```

### 7.1 Assembly Responsibilities and Boundary

`ProductAssembly` orchestrates pathway assembly.

It receives a valid completed `InitialCharterResult` and follows its reference to the evaluated `ProductAdapterResult` and associated immutable `ProductPathway`.

`ProductAssembly`:

* consumes a reference to the immutable `ProductPathway`;
* identifies the represented queue structures applicable to downstream evaluation;
* delegates queue grouping to `QueueBundler`;
* provides the resulting immutable `ProductQueueBundle` objects to `FabricAssembler` where fabric assembly is applicable;
* collects the immutable `ProductQueueBundle` and `ProductFabric` objects produced by those components; and
* makes the completed assembly products available to the `PathwayEvaluationEngine`.

`ProductAssembly` uses only structures already represented in the `ProductPathway`. It does not modify the pathway, add missing pathway facts, create new source evidence, or reinterpret unsupported claims as represented pathway structure.

It does not perform Charter evaluation, compare the pathway with the authoritative `TransitionPathway`, evaluate queue or fabric state, determine system contribution or scale, construct a candidate `TransitionPathway`, evaluate global-system risk, assign a bound state, or construct the final `EvaluatedPathway`.

Assembly omits creating a product grouping where the corresponding substructure is not present in the pathway. The absence of a `ProductFabric` is not an error when the pathway does not require applicable `ProductQueueBundle` objects to be grouped into a fabric.

### 7.2 QueueBundler

`QueueBundler` groups queue elements represented in the `ProductPathway` where their evaluable function and represented relationships require bundled execution and evaluation.

A `ProductPathway` may contain multiple queue elements representing distinct inputs, outputs, dependencies, constraints, access requirements, or execution conditions. Related queue elements may be grouped into one or more `ProductQueueBundle` objects according to their evaluable function and represented relationships. Queue elements that do not require grouping remain unbundled in the immutable `ProductPathway` and are evaluated directly by `QueueEvaluator`.

Queue-bundle boundaries are determined by evaluable function and represented relationships, and are irrespective of queue direction. A pathway may therefore contain separate bundles for input access, output delivery, finance, permitting, workforce, documentation, or other applicable queue functions, together with independently evaluable unbundled queue elements.

`QueueBundler` uses the relationships represented in the `ProductPathway` to determine which queue elements belong together. It preserves relevant ordering, dependency, timing, identity, and provenance relationships carried by those elements.

`QueueBundler` does not create a queue element or pathway fact absent from the `ProductPathway`, infer an unstated dependency, or determine whether a represented queue is clear, blocked, starved, expired, closed, delayed, stale, or otherwise successful or unsuccessful. Those determinations belong to downstream evaluation.

Each completed queue grouping is returned as an immutable `ProductQueueBundle`. Queue elements that remain unbundled retain their existing immutable representation in the `ProductPathway`.


### 7.3 ProductQueueBundle

A `ProductQueueBundle` is an immutable construct containing related queue elements from one `ProductPathway` that are grouped for evaluation according to a common evaluable function and their represented relationships.

A `ProductQueueBundle` contains:

* references to the queue elements included in the bundle;
* the `user_id` and `pathway_id` attribution preserved by those represented elements' references;
* the queue relationships and dependencies required for evaluation;
* relevant timing or ordering relationships represented by the pathway;
* source, evidence, and provenance references needed to trace the represented queue conditions; and
* assembly metadata required to preserve the structure of the grouping.

A `ProductQueueBundle` represents an assembled evaluation unit. It does not contain the result of evaluating that queue grouping.

The same represented queue element may participate in more than one downstream relationship where the `ProductPathway` explicitly represents those relationships. As the `ProductPathway` is immutable, assembly must not silently duplicate, merge, or reassign an element in a way that changes the pathway structure.

A completed `ProductQueueBundle` is immutable and is later consumed by `QueueEvaluator` and, where applicable, referenced by one or more `ProductFabric` objects.

### 7.4 FabricAssembler

`FabricAssembler` constructs operational coordination fabrics from applicable immutable `ProductQueueBundle` objects.

A fabric groups related queue bundles whose combined state must be evaluated for coordinated operation. Technical fabrics may represent functions such as deliverability, fossil constraint, procurement synchronization, institutional capacity, finance, or another pathway-specific coordination function.

`FabricAssembler` determines fabric membership from the functions and relationships preserved by the applicable `ProductQueueBundle` objects and their referenced queue elements. It constructs fabrics only where those represented relationships require multiple queue bundles to be evaluated together.

`FabricAssembler`:

* consumes applicable immutable `ProductQueueBundle` objects;
* identifies queue bundles whose represented functions and relationships require coordinated evaluation;
* groups those queue bundles into the applicable coordination fabric;
* preserves the relationships among those bundles required for fabric evaluation;
* preserves timing, identity, source, evidence, and provenance references;
* preserves the association between each fabric and the `ProductPathway` from which its queue bundles were derived; and
* returns each completed coordination layer as an immutable `ProductFabric`.

A `ProductQueueBundle` may be referenced by more than one `ProductFabric` where its represented functions and relationships require participation in multiple coordination fabrics. Fabric membership does not transfer `ProductPathway` ownership of the queue bundle or remove it from another fabric.

`FabricAssembler` does not create missing queue bundles or infer unsupported fabric membership. It does not evaluate the state of participating queues or determine fabric readiness; queue-level conditions are evaluated by `QueueEvaluator`, while fabric-level coordination and readiness are evaluated by `FabricEvaluator`.

### 7.5 ProductFabric

A `ProductFabric` is an immutable operational coordination layer composed of references to related `ProductQueueBundle` objects and the represented relationships required to evaluate their coordinated state.

A `ProductFabric` contains:

* the fabric's coordination function;
* references to the applicable `ProductQueueBundle` objects;
* relationships among those queue bundles required for evaluation;
* timing or synchronization relationships preserved through the referenced queue bundles;
* identity and pathway attribution preserved through the referenced queue bundles;
* source, evidence, and provenance references required for traceability; and
* assembly metadata required to preserve the fabric structure.

A `ProductFabric` is a coordination surface. It does not contain the result of fabric evaluation. A completed `ProductFabric` is immutable and is consumed by `FabricEvaluator`. 

When the pathway does not require a technical fabric structure, `FabricAssembler` is not executed and therefore cannot produce a `ProductFabric`.

Biosphere-related fabrics may incorporate buses, cycles, BioNPUs, or other domain-specific structures maintained by ClimateSOS system modeling. Those structures are not constructed by `ProductAssembly` or directly derived from a submitted `ProductPathway`. A submitted pathway may interact with those structures, but their definition and behavior remain part of the ClimateSOS system model. See the system-modeling architecture for the definition, ownership, and evaluation of biosphere and other Earth-system structures.

### 7.6 Assembly Integrity Requirements

Product assembly preserves the structure and attribution established by the `ProductAdapter`.

Assembly must satisfy the following requirements:

* assembled products retain `user_id` and `pathway_id` attribution through their contained objects or references;
* objects from separate pathway intakes must not be silently combined;
* the `ProductPathway` remains immutable throughout assembly;
* assembly products contain or retain references sufficient to trace represented elements back through the `ProductPathway`, `ProductAdapterResult`, and associated `ProductIntakeBundle`;
* source evidence and provenance remain traceable;
* assembly does not supply missing facts or relationships;
* assembly does not convert unsupported claims into represented pathway structure;
* queue elements are grouped into `ProductQueueBundle` objects only where their represented evaluable functions and relationships require grouping;
* applicable queue elements that do not require grouping remain independently evaluable from the `ProductPathway`;
* a queue bundle may participate in more than one fabric so long as doing so does not duplicate, reassign, or transfer the queue bundle between fabrics;
* fabric membership is derived only from functions and relationships preserved by the applicable queue bundles and their referenced elements;
* only applicable assembly products are constructed;
* absence of a fabric where none applies is not an error;
* completed assembly products are immutable; and
* later evaluators produce separate evaluation results rather than writing evaluation state back into the assembly products.

An assembly operation fails when a required represented structure cannot be grouped without losing identity, attribution, provenance, or a relationship required for downstream evaluation.

An assembly failure is an execution failure of the current pathway evaluation. It must not be represented as a pathway evaluation finding or outcome.

When assembly completes successfully, the resulting `ProductQueueBundle` objects and, where applicable, `ProductFabric` objects are passed to the `PathwayEvaluationEngine` for evaluation.

---

## 8. Product Queue Categories

A queue element represents a pathway function or requirement whose access, capacity, timing, availability, or throughput may affect how the pathway executes as represented. Queue elements are identified by the `ProductAdapter` from information supported by the `ProductIntakeBundle` and represented in the immutable `ProductPathway`.

Product queue categories classify functionality via the principal types of access, capacity, timing, throughput, and execution represented by those queue elements. They provide a common functional vocabulary for identifying what role a queue performs and for organizing related pathway structures for downstream evaluation.

Facts carried by a queue element describe the pathway's stated capacity, access, timing, throughput, availability, dependencies, and other applicable characteristics used downstream to identify constraints or bottlenecks. These facts originate in the submitted pathway material and remain attributable to their source, evidence, provenance, `user_id`, and `pathway_id`.

Accurate queue-category identification is required for correct downstream assembly and evaluation. A pathway therefore uses only the canonical queue categories applicable to its represented functions. A pathway may contain multiple queue elements within the same category. Where a valid queue element does not fit the current canonical taxonomy, it is preserved as `UNCLASSIFIED` rather than discarded or forced into an inapplicable category.

Queue classification does not determine operational state. Whether a queue is clear, constrained, blocked, expired, closed, delayed, stale, or otherwise successful or unsuccessful is determined later by `QueueEvaluator`.

Where available from the pathway material, a represented queue element preserves information needed to identify:

* the function or requirement represented by the queue;
* the applicable canonical queue category, or `UNCLASSIFIED` if none of the existing category types apply;
* the input, output, access, capacity, or execution function or requirement involved;
* relevant quantity, capacity, or bandwidth information;
* applicable timing, sequencing, throughput, latency, or availability information;
* geographic or other system scope;
* dependencies and relationships with other pathway elements;
* assumptions and uncertainties;
* source, documentation, evidence, and provenance references; and
* `user_id` and `pathway_id` attribution.

A queue category identifies the function represented by a queue element. It does not determine the queue's evaluated state or `ProductQueueBundle` membership.

### 8.1 Feedstock and Input Access

The Feedstock and Input Access category represents access to physical, energy, material, service, or other operational inputs that are consumed, altered, or transformed as part of the pathway’s execution.

Applicable queue elements may represent product pathway requirements such as:

* fuel or process feedstocks;
* electricity or other energy inputs;
* clean-power access;
* raw or processed materials;
* critical minerals or manufactured components;
* water or other required process inputs;
* biological feedstocks;
* equipment or specialized services; or
* another material or operational input required for construction, conversion, deployment, or operation.

A represented input requirement should preserve applicable quantity, quality, location, timing, sourcing, and dependency information where supplied.

Representation of an input does not establish that sufficient supply exists. Availability, competing demand, throughput, timing, and other constraints are evaluated downstream.

### 8.2 Production, Conversion, and Execution Capacity

The Production, Conversion, and Execution Capacity category represents the physical or operational capacity required to transform pathway inputs into the pathway's represented outputs or completed activities.

Applicable queue elements may include:

* manufacturing capacity;
* processing capacity;
* conversion capacity;
* generation capacity;
* construction or deployment capacity;
* facility throughput;
* equipment availability;
* operating capacity;
* commissioning capacity;
* process yield or utilization characteristics;
* ramp-up or expansion capacity; or
* another physical or operational capacity characteristic affecting production, conversion, construction, deployment, or operation.

This category represents the pathway's ability to perform the change or activity itself. It is distinct from access to the inputs required by that activity, access to infrastructure used to deliver its outputs, and access to the workforce required to execute it.

Where the pathway represents multiple construction, commissioning, operation, conversion, or production steps, including sequential or parallel steps, the relationships among them are preserved.

Representation of production or execution capacity does not establish that the pathway can operate at the required scale or within the required synchronization window. Those conditions are evaluated downstream.

### 8.3 Product Output and Delivery Access

The Product Output and Delivery Access category represents the infrastructure, network access, storage, market access, offtake, or delivery conditions required for a pathway's declared output to reach its intended destination or function.

Applicable queue elements may include:

* grid interconnection;
* transmission or distribution access;
* pipeline access;
* transport or logistics capacity;
* storage or terminal access;
* export or import infrastructure;
* customer connection;
* product offtake;
* injection or sequestration access; or
* another delivery pathway required to move, store, connect, transfer, or use the declared output.

Where infrastructure supports both product pathway inputs and outputs, materially distinct operational conditions may be represented as separate queue elements. Where the same infrastructure serves both directions under materially similar operational conditions, it may be represented as a single shared infrastructure queue. In all cases, the `ProductPathway` preserves the direction and relationships of every represented flow.

The queue represents access required for handling or delivery. It does not establish the climate or system value of the output, the validity of an offtake claim, or whether delivering the output produces a net overall system contribution.

### 8.4 Finance and Revenue

Finance and revenue queue categories represent distinct functions associated with establishing a pathway's revenue basis, obtaining debt, equity, or other private capital required for execution, and accessing applicable public or non-dilutive support. These functions remain separately classified because a pathway may satisfy one while remaining constrained by another.

### 8.4.1 Bankability and Revenue Certainty

The Bankability and Revenue Certainty category represents conditions required for a pathway to establish sufficiently durable expected revenue or economic support for execution.

Applicable queue elements may include:

* contracted offtake;
* long-term purchase commitments;
* regulated or contracted revenue;
* tariffs or other revenue-setting mechanisms;
* market arrangements that materially determine revenue certainty;
* price-support mechanisms;
* creditworthy counterparties;
* revenue guarantees;
* customer commitments; or
* other represented conditions affecting revenue certainty.

This category is distinct from Project Finance. Bankability and revenue certainty concern the conditions supporting expected cash flow or economic viability. Project Finance concerns access to the capital required to finance execution.

The presence of a represented revenue mechanism does not establish commercial validity or investment worthiness.

### 8.4.2 Project Finance

The Project Finance category represents access to capital required to construct, deploy, convert, expand, operate, refinance, or otherwise execute the represented pathway.

Applicable queue elements may include:

* debt;
* equity;
* project-finance capacity;
* construction finance;
* working capital;
* refinancing;
* guarantees or credit enhancement;
* risk allocation required for financing close;
* applicable cost-of-capital characteristics; or
* other financing conditions represented by the pathway.

Debt, equity, and other private-capital structures may be preserved as subtypes or properties of the represented finance requirement rather than requiring separate top-level queue categories.

Where financing depends on another pathway condition, such as permitting, contracted revenue, infrastructure availability, or public support, that dependency remains represented rather than being collapsed into the finance queue.

Project Finance does not determine whether a financing structure is appropriate, investable, or commercially advisable.

### 8.4.3 Non-Dilutive Capital and Public Support

The Non-Dilutive Capital and Public Support category represents grants, incentives, public programs, concessional support, or other non-dilutive mechanisms on which the represented pathway depends.

Applicable queue elements may include:

* grants;
* tax credits or rebates;
* public loan support;
* guarantees;
* contracts for difference;
* production or deployment incentives;
* public procurement support;
* demonstration or commercialization funding;
* sovereign or development-finance support; or
* other represented public or non-dilutive support.

The queue preserves dependencies on eligibility, authorization, availability, timing, appropriation, award, or disbursement where those conditions are represented.

Public support is represented as a pathway dependency when applicable. ClimateSOS does not assume that a proposed or available program will necessarily provide the required support.

### 8.5 Permitting and Authorization

The Permitting and Authorization category represents legal, regulatory, institutional, or other formal authorization required for pathway execution.

Applicable queue elements may include:

* construction or operating permits;
* environmental approvals;
* siting or land-use approvals;
* licenses;
* interconnection authorization;
* import or export authorization;
* required inspections, certifications, or authority signoffs;
* regulatory approval;
* public-agency authorization; or
* other legally required permissions.

A pathway may contain multiple Permitting and Authorization queue elements where distinct approvals apply at different execution stages. For example, an initial construction or installation permit, a post-construction inspection, and a final operating authorization may be represented as separate queue elements when they constitute materially distinct requirements.

Where the pathway identifies sequencing or timing relationships among authorizations, inspections, production or construction activity, commissioning, or operation, those relationships are preserved. Distinct Permitting and Authorization queue elements may therefore occur before, between, or after queue elements in other categories.

Permitting and authorization do not subsume Charter requirements concerning justice, rights, equitable durability, Indigenous Peoples' rights, community safeguards, or other normative constraints. Those conditions remain subject to the applicable Charter evaluation.

### 8.6 Workforce and Execution

The Workforce and Execution category represents human, organizational, contractor, and specialist capacity required to construct, deploy, operate, maintain, convert, retire, or close the represented pathway.

Applicable queue elements may include:

* skilled labor;
* specialized trades;
* engineering capacity;
* construction labor;
* installation personnel;
* operations and maintenance personnel;
* contractor or supplier execution capacity;
* training or retraining;
* workforce redeployment;
* fossil workforce transition, retraining, or redeployment requirements;
* fossil workforce capacity required for decommissioning, remediation, or closure;
* project-management capacity; or
* other human or organizational capability required by the pathway.

This category concerns the people and organizations required to execute the represented activity. Physical production, conversion, facility, or deployment throughput remains represented under Production, Conversion, and Execution Capacity.

Where workforce requirements depend on timing, geography, certification, training lead time, or competition with other transition activities, those relationships are preserved when represented by the pathway.

### 8.7 MRV

The MRV category represents measurement, reporting, and verification requirements necessary to support a represented pathway claim, transaction, authorization, accounting treatment, or operational function.

Applicable queue elements may include:

* measurement systems;
* monitoring requirements;
* reporting infrastructure;
* verification processes;
* audit or review processes required as part of an MRV regime;
* lifecycle, emissions, durability, storage, or performance monitoring; or
* other ongoing measurement, reporting, or verification functions required by the pathway.

An MRV queue represents the operational capability required to measure, monitor, report, or verify the applicable pathway condition over time. Representation of an MRV requirement does not establish that the resulting evidence is sufficient or that the associated claim is valid. Evidence quality, provenance, methodology, uncertainty, and unresolved claims are evaluated downstream.

### 8.8 Documentation and Evidence

The Documentation and Evidence category represents documentation, records, certifications, provenance, or other evidentiary material required to support a represented pathway claim, transaction, authorization, accounting treatment, or operational function.

Applicable queue elements may include:

* lifecycle or emissions documentation;
* chain-of-custody records;
* certifications;
* registry records;
* audit records;
* durability or storage evidence;
* test or inspection records;
* methodology documentation;
* provenance records;
* source documentation supporting material pathway claims; or
* other documentation or evidence required for the pathway to execute or substantiate a material claim.

Representation of documentation or evidence does not establish that it is sufficient, valid, complete, or applicable to the associated claim. `DocumentationEvaluator` evaluates the evidence, provenance, methodology, uncertainty, and unresolved claims downstream.

### 8.9 Fossil-Exit Finance and Persistence Closure

The Fossil-Exit Finance and Persistence Closure category represents requirements necessary to ensure that one or more transition activities result in durable fossil retirement, closure, or prevention of continued fossil dependence, including financial, institutional, governance, or other mechanisms that materially enable fossil phaseout.

Applicable queue elements may include:

* financing required for fossil-asset retirement;
* refinancing or debt restructuring associated with retirement;
* contractual termination or retirement mechanisms;
* compensation or liability arrangements required for closure;
* decommissioning finance;
* environmental-remediation funding;
* long-term closure or monitoring obligations;
* financial assurance for residual liabilities;
* infrastructure retirement or conversion requirements;
* mechanisms preventing retired capacity from returning to service; or
* other represented conditions required to close a fossil persistence pathway.

Where fossil retirement or closure depends on workforce transition, retraining, redeployment, decommissioning labor, or related execution capacity, those requirements are represented under Workforce and Execution and linked to the applicable fossil-exit queue elements.

This category is distinct from ordinary Project Finance. It represents requirements specifically associated with durable fossil exit, retirement, closure, or prevention of continued fossil fallback.

Operational cessation alone does not establish completion of fossil-exit obligations where the represented pathway also requires decommissioning, remediation, residual-emissions control, financial assurance, monitoring, or another durable closure condition.

### 8.10 Unclassified Queue Elements

A pathway may contain a valid queue function or requirement involving throughput, access, capacity, timing, or execution that is supported by the intake material but does not fit the current canonical queue taxonomy.

Such a queue element must not be discarded, forced into an inapplicable category, or converted into a different pathway fact solely to satisfy the taxonomy.

Where the `ProductAdapter` can establish that the represented condition functions as a queue but cannot assign an applicable canonical category, it preserves the queue element with the category `UNCLASSIFIED`.

An `UNCLASSIFIED` queue preserves the same information available for any other represented queue element, including:

* its represented operational function;
* applicable capacity, throughput, access, timing, or execution information;
* relationships and dependencies;
* assumptions and uncertainty;
* source, evidence, and provenance references; and
* `user_id` and `pathway_id` attribution.

`UNCLASSIFIED` indicates a taxonomy gap, not an absence of information and not an evaluator failure. The queue remains available to `QueueBundler`, `QueueEvaluator`, and other applicable downstream stages using the operational information and relationships that are represented.

Downstream evaluation must not treat an `UNCLASSIFIED` queue as clear, satisfied, or immaterial merely because a canonical category was not assigned.

Recurring unclassified queue functions should be reviewed for possible addition to the canonical taxonomy rather than being permanently accumulated under `UNCLASSIFIED`. Where review identifies a valid ClimateSOS functional gap, an implementation update may be submitted through the standard ClimateSOS open-source contribution and review process.

The queue taxonomy provides a common functional vocabulary without requiring the taxonomy to be complete before a represented pathway can proceed. Queue classification identifies the applicable functional category, or `UNCLASSIFIED` where no canonical category applies; it does not determine queue state, `ProductQueueBundle` membership, or pathway validity.

---

## 9. Pathway Evaluation Engine

The `PathwayEvaluationEngine` orchestrates several subevaluators that evaluate the represented pathway and its assembled queue and fabric structures against the current authoritative `TransitionPathway`.

Evaluation begins after `ProductAssembly` completes successfully. The engine receives the immutable pathway and assembly products created by earlier stages. After all required subevaluators complete successfully, the engine produces a consolidated immutable `PathwayAssessment`.

The evaluation engine determines how the represented pathway operates within the transition context. It identifies direct relationships with the reference transition, substitution or combination effects, downstream propagation, queue conditions, fabric coordination conditions, and the sufficiency and traceability of supporting documentation and evidence.

Evaluation does not modify the `ProductPathway`, `ProductQueueBundle`, `ProductFabric`, `ProductIntakeBundle`, or authoritative `TransitionPathway`. Evaluators produce separate immutable results or findings that preserve references to the objects and evidence from which they were derived.

```text
ProductAdapterResult
      │
      ├── ProductPathway
      ├── ProductIntakeBundle reference
      │
      ▼
CharterEvaluator
      │
      ▼
InitialCharterResult
      │
      │
ProductAssembly
      │
      ├── ProductQueueBundle(s)
      ├── ProductFabric(s), where applicable
      │
      ▼
PathwayEvaluationEngine
      │
      ├── PathwayComparator
      │      ├── Direct Pathway Comparison
      │      ├── Substitution and Combination Evaluation
      │      └── Downstream Propagation
      │
      ├── QueueEvaluator
      │      ├── evaluates the ProductPathway queue family
      │      │      ├── ProductQueueBundle(s)
      │      │      └── applicable unbundled queue element(s)
      │      ├── QueueProgressRecord(s)
      │      ├── QueueExecutionResult(s)
      │      └── QueueEvaluatorResult(s)
      │
      ├── FabricEvaluator, where applicable
      │      └── evaluates ProductFabric(s)
      │             └── FabricEvaluatorResult(s)
      │
      └── DocumentationEvaluator
             └── evaluates documentation, evidence, provenance,
                 methodology, uncertainty, and unresolved claims
      │
      ▼
PathwayAssessment
```

### 9.1 Evaluation Responsibilities and Boundary

The `PathwayEvaluationEngine` coordinates the evaluation functions required to determine how the represented pathway interacts with the current transition context.

It receives:

* the immutable `ProductAdapterResult` and its associated immutable `ProductPathway`;
* the completed `InitialCharterResult`;
* the immutable `ProductQueueBundle` objects produced by `ProductAssembly`;
* applicable immutable `ProductFabric` objects;
* the current authoritative `TransitionPathway`;
* references to the associated `ProductIntakeBundle` where documentation, evidence, or provenance is required; and
* the runtime configuration, evaluator versions, and applicable system-model resources required for evaluation.

The `PathwayEvaluationEngine`:

* compares the represented pathway with the authoritative `TransitionPathway`;
* identifies direct overlaps, dependencies, additions, replacements, and conflicts;
* evaluates represented substitution and combination relationships;
* evaluates downstream propagation from represented pathway changes;
* evaluates queue operational status, lifecycle state, ordering, synchronization, and other applicable findings from represented queue facts, relationships, and transition and system context;
* evaluates coordinated fabric conditions where a `ProductFabric` is present;
* evaluates documentation, evidence, provenance, methodology, uncertainty, and unresolved claims;
* preserves relationships among results and findings produced by the individual evaluators; and
* produces one consolidated immutable `PathwayAssessment`.

The engine does not modify any input or assembly object. It does not perform the Integrated Charter Evaluation, determine net overall system contribution, perform the Scale Diagnostic, construct a candidate `TransitionPathway`, evaluate net overall system risk, assign a bound state, or construct the final `EvaluatedPathway`.

An adverse, constrained, blocked, unresolved, or otherwise unsuccessful pathway finding produced by valid evaluator execution remains a valid evaluation finding. An evaluator execution failure occurs when a required evaluation cannot execute or cannot produce a valid required result.

### 9.2 PathwayComparator

`PathwayComparator` evaluates the relationship between the represented `ProductPathway` and the current authoritative `TransitionPathway`.

The comparator evaluates the pathway as represented. It does not silently rewrite the submitted pathway to make it consistent with the reference transition and does not modify the authoritative `TransitionPathway`.

`PathwayComparator` identifies applicable relationships between the `ProductPathway` and the authoritative `TransitionPathway`, including:

* overlap with functions already represented in the authoritative transition;
* addition of new functions introduced by the product pathway;
* replacement, reduction, expansion, retirement, or other alteration of existing transition functions;
* dependency on existing transition functions or infrastructure;
* competition or mutual exclusivity between functions;
* complementarity between functions;
* timing or sequencing interactions;
* geographic or system-scope interactions; and
* represented assumptions or uncertainties that materially affect those relationships.

Comparison findings preserve the pathway elements, transition elements, relationships, and supporting information used to produce the finding.

`PathwayComparator` coordinates Direct Pathway Comparison, Substitution and Combination Evaluation, and Downstream Propagation.

#### 9.2.1 Direct Pathway Comparison

Direct Pathway Comparison examines relationships that can be established directly between represented elements of the `ProductPathway` and the authoritative `TransitionPathway`.

Direct Pathway Comparison may identify:

* equivalent or overlapping functions;
* direct additions to an existing transition function;
* direct replacement or retirement relationships;
* direct dependencies;
* direct interaction with applicable ClimateSOS system-model functions or structures, including biosphere-related structures where applicable and represented;
* incompatible requirements;
* competing claims on represented capacity, infrastructure, inputs, finance, workforce, authorization, or other transition resources;
* differences in timing, scale, geography, or operational scope; and
* material gaps between the pathway as represented and the corresponding transition function.

A direct comparison finding preserves the objects and relationships on both sides of the comparison.

Similarity alone does not establish substitution, equivalence, or contribution. Those determinations require the applicable downstream evaluation.

Where no direct relationship exists, Direct Pathway Comparison records no direct relationship rather than creating one from unsupported similarity.

#### 9.2.2 Substitution and Combination Evaluation

Substitution and Combination Evaluation determines whether represented pathway functions may replace, combine with, depend on, complement, or operate alongside functions in the authoritative `TransitionPathway`.

A substitution relationship exists only where the represented pathway and transition context support displacement or replacement of an existing function. The presence of a cleaner, newer, or additional activity does not by itself establish that another activity is displaced.

Combination evaluation examines pathways whose effect depends on coordinated operation with one or more existing transition functions rather than direct replacement.

Evaluation may identify substitution or displacement relationships such as:

* full substitution;
* partial substitution;
* conditional substitution dependent on another pathway function;
* replacement that becomes effective only after another requirement is satisfied; or
* claimed substitution where the represented pathway instead operates in parallel without material displacement.

Evaluation may identify combination or additive relationships such as:

* complementary operation;
* required coexistence;
* coordinated operation with an existing transition function; or
* a proposed combination whose required relationship is unsupported or unresolved.

Evaluation may also determine that no material substitution, displacement, or combination relationship exists.

Where substitution or combination depends on timing, capacity, authorization, infrastructure, finance, workforce, queue condition, or another represented relationship, the evaluation preserves that dependency.

Substitution and combination findings describe the evaluated relationship. They do not themselves establish net overall system contribution or modify the authoritative `TransitionPathway`.

#### 9.2.3 Downstream Propagation

Downstream Propagation evaluates how a represented pathway change affects functions and dependencies connected to the directly affected pathway or transition elements.

Propagation begins from relationships established by the pathway comparison. It follows represented and system-supported dependencies far enough to identify material consequences required for pathway evaluation.

Applicable propagated effects may include changes to:

* input demand;
* production or conversion requirements;
* infrastructure use;
* delivery requirements;
* finance or revenue dependencies;
* permitting or authorization requirements;
* workforce requirements;
* MRV requirements;
* documentation or evidence requirements;
* fossil-retirement or persistence-closure requirements;
* timing and synchronization dependencies;
* preconditions required for downstream functions, cascades, or state changes to occur;
* cascade effects produced when a change propagates through multiple connected dependencies or functions;
* interactions that may reinforce, weaken, or alter an applicable system attractor or transition trajectory;
* interactions with applicable biosphere functions, cycles, buses, fabrics, or other system-model structures;
* propagated effects that alter biosphere integrity, resilience, restoration capacity, or other applicable planetary-boundary conditions; and
* other transition functions materially connected to the represented change.

Propagation preserves the distinction between a submitted pathway fact and a condition derived through ClimateSOS system-side evaluation. Where queue evaluation identifies a material interaction or propagated effect requiring additional system-side evaluation, `QueueEvaluator` returns that interaction to `PathwayEvaluationEngine` for routing to the applicable system-side function. Resulting system-side findings may be consumed by a subsequent evaluation pass of the affected queue within the same evaluation run.

A propagated effect must remain traceable to the relationships and system-model basis from which it was derived. The evaluator does not convert an unsupported possible effect into an established pathway condition.

Downstream Propagation does not recursively expand without an evaluation-relevant boundary. Propagation stops when the next relationship or effect is not relevant to the current pathway assessment or authoritative `TransitionPathway`, or is unsupported by the represented pathway or applicable system model.

### 9.3 QueueEvaluator

`QueueEvaluator` evaluates the queue family associated with one `ProductPathway`. Within this section, the *queue family* comprises the immutable `ProductQueueBundle` objects produced by `ProductAssembly` and any applicable unbundled queue elements remaining in that `ProductPathway`.

`QueueEvaluator` evaluates every member of the queue family associated with one `ProductPathway` at least once during each evaluation run. A queue-family member may complete after a single evaluation pass or may be re-evaluated within the same run when a material dependency, system-side condition, propagated effect, timing relationship, or other evaluation context changes. During that lifecycle, queue conditions emerge from represented queue facts and relationships together with the applicable pathway, reference transition, and system-side context.

Queue evaluation establishes and updates the evaluated queue's operational status, lifecycle state, and, where applicable, its ordering and synchronization status. These dimensions describe different aspects of queue execution and may change independently during the evaluation lifecycle.

Each queue-evaluation attempt performed by `QueueEvaluator` has an execution status separate from the queue's operational status and lifecycle state. A successfully completed evaluation attempt may still return an unresolved queue determination such as `NODETERMINATION`. If `QueueEvaluator` cannot successfully complete the required evaluation, the attempt is recorded with an execution status of `EVALUATION_FAILED`.

#### Queue Operational Status

Operational status describes the queue's current ability to perform its represented function. Applicable statuses may include:

* `CLEAR`;
* `CONSTRAINED`;
* `BLOCKED`;
* `DELAYED`; or
* another operational status defined by the applicable queue-evaluation rules.

`CLEAR` means that the represented queue function can proceed as intended under the currently evaluated conditions. It does not mean that the queue has completed or that its lifecycle is closed.

`CONSTRAINED` indicates that the queue can proceed, but a material condition limits its capacity, throughput, timing, availability, access, or another required operating characteristic.

`BLOCKED` indicates that a material dependency or condition prevents the represented queue function from proceeding.

`DELAYED` indicates that the represented queue function can or may proceed, but not within the required or expected timing under the currently evaluated conditions.

A change in operational status does not by itself change the queue's lifecycle state.

#### Queue Lifecycle State

Lifecycle state describes how the represented queue progresses from an active and current condition through closure or loss of current validity within the evaluation context. Applicable lifecycle states may include:

* `OPEN`;
* `CLOSED`;
* `EXPIRED`;
* `STALE`; or
* another lifecycle state defined by the applicable queue-evaluation rules.

The evaluated lifecycle begins when `QueueEvaluator` first evaluates the queue. A queue ordinarily enters evaluation as `OPEN` unless the applicable evidence, temporal context, or queue rules establish that it is already stale, expired, completed, or otherwise no longer active.

An `OPEN` queue represents a function or requirement whose evaluated lifecycle remains active because it is executing, waiting, progressing, recurring, or pending resolution. `QueueEvaluator` evaluates the queue at the applicable evaluation time and may revisit it within the same evaluation run when a material condition changes. Its operational status may change multiple times while its lifecycle state remains `OPEN`.

For example:

```text
OPEN + BLOCKED
        ↓
OPEN + CONSTRAINED
        ↓
OPEN + CLEAR
        ↓
CLOSED + CLEAR
```

The queue remains `OPEN` while a blocking dependency is unresolved, while execution is constrained, and after the constraint clears if the represented function still has work remaining. It becomes `CLOSED` when the represented function has completed, its requirement has been satisfied, or the applicable queue rules establish that continued queue execution is no longer required.

Some queues represent continuously operating or persistent real-world conditions rather than short execution steps. Such a queue remains `OPEN` while the represented requirement persists. For example, a queue representing methane control at an emitting well may remain `OPEN` while emissions continue and required control or closure has not been completed. Its operational status may change as control capacity, permits, equipment, workforce, or other dependencies become available. Closure occurs only when the represented requirement is satisfied under the applicable evaluation rules.

`STALE` indicates that the information or evaluated context required to rely on the queue condition is no longer sufficiently current. `EXPIRED` indicates that the time period applicable to the queue condition has ended. Neither state means that the underlying real-world requirement has necessarily completed.

TTL is temporal evaluation information rather than an operational status or lifecycle state. TTL, expiration time, age, last-verification time, and similar information are preserved as result context and may cause the evaluated lifecycle state to become `STALE` or `EXPIRED`.

#### Queue Ordering and Synchronization

Queue ordering and synchronization are evaluated independently of operational status and lifecycle state where applicable.

Ordering status may be:

* `ORDERED`;
* `MISORDERED`; or
* `NOT_APPLICABLE`.

`ORDERED` means that required sequencing relationships are satisfied. `MISORDERED` means that a required sequence exists but the represented or evaluated execution order is incorrect. `NOT_APPLICABLE` means that the queue does not have any material ordering requirements.

Synchronization status may be:

* `SYNCHRONIZED`;
* `UNSYNCHRONIZED`; or
* `NOT_REQUIRED`.

`SYNCHRONIZED` means that required timing or coordination relationships are satisfied. `UNSYNCHRONIZED` means that required coordination exists but the participating functions are not aligned within the applicable timing or operating conditions. `NOT_REQUIRED` means that coordinated timing is not required for the evaluated queue.

Evaluator execution, integrity errors, or failures are not represented as ordinary ordering, synchronization, operational, or lifecycle statuses.

#### Queue Evaluation Process

`QueueEvaluator` applies the applicable evaluation logic to each queue in the `ProductPathway` queue family, determines how the queue operates and changes under the pathway, transition, and relevant system context, and records the resulting changes to its operational status, lifecycle state, dependencies, timing, ordering, synchronization, and other relevant conditions over its evaluated lifecycle.

Evaluation may examine:

* the queue functions represented by the queue elements;
* access, capacity, throughput, bandwidth, and availability;
* timing, sequencing, latency, ordering, and synchronization relationships;
* dependencies internal to the queue;
* dependencies on other queues, pathway functions, or applicable system-side structures;
* geographic and system scope;
* competing demand or resource use;
* relevant pathway-comparison and downstream-propagation findings;
* applicable transition and system-side conditions;
* represented assumptions and uncertainties; and
* supporting source, evidence, and provenance references.

Where an evaluated queue participates in one or more `ProductFabric` objects, `QueueEvaluator` preserves the applicable fabric references and evaluates queue-level conditions that depend on that membership. Fabric coordination among queues participating in a `ProductFabric` remains the responsibility of `FabricEvaluator`.

Queue evaluation is not limited to conditions internal to the `ProductPathway`. Where a represented queue function depends on an applicable ClimateSOS system-side structure or function, `QueueEvaluator` identifies the required system-side evaluation context. `PathwayEvaluationEngine` coordinates access to the applicable system-side evaluation and provides the resulting state or findings to `QueueEvaluator` for use in determining the queue condition.

These interactions may include dependencies on, or effects associated with, infrastructure systems, system attractors, biosphere functions, cycles, buses, fabrics, BioNPUs, or other applicable ClimateSOS system-model structures.

`QueueEvaluator` does not take ownership of or directly modify those system-side structures. The applicable system-side evaluation function determines their state. `QueueEvaluator` consumes the resulting state or findings as evaluation context and determines their effect on the represented queue.

A material system-side change may therefore change the state of an `OPEN` queue during the same evaluation lifecycle. For example, a queue that is initially `BLOCKED` because required system capacity is unavailable may become `CONSTRAINED` or `CLEAR` when the applicable system-side evaluation establishes that sufficient capacity has become available.

Likewise, operation of the represented queue may produce a material effect that propagates into the system model. Where that effect results in new system-side findings relevant to the queue, those findings may be consumed by subsequent queue evaluation within the same evaluation lifecycle. Such feedback remains traceable to the queue relationship, propagated effect, and system-model basis from which it was derived.

#### Queue Progress Through the Lifecycle

A queue may pass through multiple evaluated conditions before its lifecycle completes. Material changes in operational status, lifecycle state, dependency state, timing, ordering, synchronization, or applicable system-side context are preserved as immutable `QueueProgressRecord` objects.

A new `QueueProgressRecord` is produced when a material change is required to explain the queue's progression or its downstream effects. The evaluator does not overwrite an earlier record.

A queue may therefore produce a progression such as:

```text
QueueProgressRecord 1
    lifecycle_state: OPEN
    operational_status: BLOCKED

QueueProgressRecord 2
    lifecycle_state: OPEN
    operational_status: CONSTRAINED

QueueProgressRecord 3
    lifecycle_state: OPEN
    operational_status: CLEAR

QueueProgressRecord 4
    lifecycle_state: CLOSED
    operational_status: CLEAR
```

The final queue condition does not erase earlier material conditions. A queue that eventually becomes `CLEAR` and `CLOSED` may still have produced delay, propagation, synchronization, capacity, or other consequences while it was blocked or constrained.

Where the available information does not support a required queue determination, `QueueEvaluator` records `NODETERMINATION`. This represents a successfully completed evaluation whose queue condition could not be resolved from the available information; it is distinct from `EVALUATION_FAILED`.

An `UNCLASSIFIED` queue remains evaluable from its represented operational facts and relationships.

Where multiple queue elements, queue bundles, or system relationships interact to produce a material condition that is not present in any one element by itself, `QueueEvaluator` preserves the relationships responsible for that finding.

#### Completion of Queue Evaluation

A completed queue evaluation represents the evaluation history of one queue for one evaluation run. It consists of the evaluated queue, one or more `QueueProgressRecord` objects preserving its material progression, exactly one `QueueExecutionResult` preserving the completed execution for that run, and the final immutable `QueueEvaluatorResult`.

The queue evaluation may conclude with any valid operational or lifecycle condition established by the completed execution, including an `OPEN`, `CLOSED`, `STALE`, or `EXPIRED` lifecycle state and an applicable operational status. It may also successfully complete an evaluation run with an operational status of `BLOCKED`, `CONSTRAINED`, or `DELAYED`, or with a `NODETERMINATION` determination.

Completion of `QueueEvaluator` means that the queue has been executed through the applicable evaluation for the current run and the required immutable results can be produced. It does not require the represented real-world queue function itself to have completed.

For each evaluated queue, `QueueEvaluator` produces exactly one immutable `QueueExecutionResult` and one immutable `QueueEvaluatorResult` for that evaluation run.

#### 9.3.1 QueueProgressRecord

A `QueueProgressRecord` is an immutable record of a material queue condition observed during one queue-evaluation run.

Every evaluated queue produces at least one `QueueProgressRecord`. Additional progress records are produced when a material change in operational status, lifecycle state, dependency state, timing, ordering, synchronization, or other applicable condition occurs during execution.

Additional progress records are produced when preserving a material state change is necessary to explain queue progression, delay, re-execution, resumption, completion, or a downstream effect. Routine transient implementation state that has no material evaluation significance does not require an additional progress record.

A `QueueProgressRecord` contains or references, as applicable:

* the evaluated queue;
* the applicable evaluation-run identity;
* the operational status at that point in the evaluation;
* the lifecycle state at that point in the evaluation;
* ordering or synchronization status, where applicable;
* applicable capacity, throughput, access, timing, or availability conditions;
* the event, dependency change, system-side change, or other material change responsible for the record, with supporting references only where not already preserved elsewhere;
* the evaluation time or ordering position of the record; and
* `user_id` and `pathway_id` attribution.

Multiple `QueueProgressRecord` objects may therefore represent the progression of the same queue during one evaluation run.

For example, a queue may progress from `BLOCKED` and `OPEN`, to `DELAYED` and `OPEN`, and later to `CLEAR` and `CLOSED`. The final queue condition does not erase the earlier material conditions or their downstream consequences.

A `QueueProgressRecord` does not replace the final `QueueExecutionResult` or `QueueEvaluatorResult`. It preserves the queue conditions and material progression required to explain the completed execution and final evaluation result.

Completed progress records are immutable. A later state change produces a new `QueueProgressRecord` rather than modifying an earlier record.

#### 9.3.2 QueueExecutionResult

A `QueueExecutionResult` is an immutable completion record of the represented queue function for one queue-evaluation run.

The result preserves the material work performed while the queue was active and the execution state in which the queue concluded. It references applicable `QueueProgressRecord` objects where recorded intermediate changes are necessary to explain that final execution state.

A `QueueExecutionResult` is distinct from a `QueueProgressRecord`, which preserves a material intermediate change in the queue's evaluated condition, and from a `QueueEvaluatorResult`, which records the evaluator's completed conclusion about the queue under the applicable pathway, transition, and system context.

Every evaluated queue produces at least one `QueueProgressRecord` and exactly one `QueueExecutionResult` for the evaluation run. Intermediate changes in queue condition are preserved through `QueueProgressRecord` objects.

The `QueueExecutionResult` preserves the material execution outcome needed to evaluate throughput, timing, ordering, synchronization, completion, propagation, fabric coordination, or another material pathway effect.

A `QueueExecutionResult` contains or references, as applicable:

* the evaluated queue;
* the applicable evaluation-run identity;
* the execution state reached by the represented queue function;
* the material work completed during execution;
* applicable timing, sequencing, duration, or completion information;
* represented input, output, quantity, capacity, throughput, or other execution information required by the applicable queue rules;
* dependencies or conditions materially affecting execution;
* references to applicable `QueueProgressRecord` objects;
* applicable source, evidence, and provenance references;
* the authoritative `TransitionPathway` or system context where required to interpret the execution result; and
* `user_id` and `pathway_id` attribution.

A `QueueExecutionResult` records the queue's completed execution but does not determine its final operational status, lifecycle state, or evaluation outcome. Those determinations remain the responsibility of `QueueEvaluator` and are recorded in the final `QueueEvaluatorResult`.

#### 9.3.3 QueueEvaluatorResult

A `QueueEvaluatorResult` records the evaluator's completed conclusion for one queue-family member during one evaluation run. A completed `QueueEvaluatorResult` is immutable. 

The result contains the final evaluated queue condition together with the material findings, progress history, temporal and evaluation context, and references to supporting documentation, evidence, and provenance.

A `QueueEvaluatorResult` contains or references, as applicable:

**Core evaluated state:**

* the evaluated queue;
* the final operational status;
* the final lifecycle state; and
* ordering or synchronization status, where applicable.

**Evaluated findings:**

* identified constraints or bottlenecks;
* material delays;
* applicable capacity, throughput, access, availability, or timing findings;
* material dependency findings;
* propagated effects that materially alter queue execution;
* tipping findings, where applicable;
* other material conditions derived during queue evaluation;
* a reference to the associated `QueueExecutionResult`; and
* references to applicable `QueueProgressRecord` objects.

Where tipping is material to the queue evaluation, the finding preserves the applicable threshold, whether the threshold was crossed, the crossing time or evaluation position where known, and the basis for the determination. *Tipping* is an evaluated finding and does not replace the queue's operational status or lifecycle state.

**Result context and integrity:**

* whether the required queue determination was resolved or remains unresolved;
* material assumptions;
* material uncertainties;
* the applicable methodology and queue-evaluation rules;
* source, evidence, and provenance references;
* evaluation time;
* applicable TTL, expiry, age, or last-verification information;
* the authoritative `TransitionPathway` and applicable system context used for evaluation;
* evaluator and rule-set versions;
* the evaluation-run identity; and
* `user_id` and `pathway_id` attribution.

A `QueueEvaluatorResult` is not a copy of the `QueueExecutionResult` or any individual `QueueProgressRecord`. It records the evaluator's completed conclusion from the queue's execution, final evaluated condition, material progression history, and applicable pathway, transition, and system context.

A queue that ultimately evaluates as `CLEAR` may therefore retain findings showing that it was previously `BLOCKED` or `DELAYED` and that the earlier condition produced a material timing or synchronization consequence.

Where the same queue is evaluated again in a new evaluation run or against a different authoritative transition or system context, the new execution produces a new immutable `QueueEvaluatorResult`. Earlier results remain preserved and distinguishable by their evaluation-run and context references.

### 9.4 FabricEvaluator

`FabricEvaluator` evaluates each applicable immutable `ProductFabric` produced by `FabricAssembler`.

Fabric evaluation examines the participating queue results and their relationships to determine whether the queues can operate together in the required coordination, timing, and dependency structure, and whether the represented fabric function can operate as required.

`FabricEvaluator` consumes:

* the immutable `ProductFabric`;
* the `ProductQueueBundle` objects referenced by the fabric;
* the applicable `QueueEvaluatorResult` objects;
* the associated `QueueExecutionResult` objects where completed queue execution is material to fabric coordination;
* the applicable `QueueProgressRecord` objects where material queue progression affects coordinated execution;
* relevant pathway-comparison and downstream-propagation findings; and
* the transition and system context required for the fabric's coordination function.

Where completed queue execution or material progression history affects fabric coordination, `FabricEvaluator` follows the applicable `QueueExecutionResult` and `QueueProgressRecord` references preserved by the associated `QueueEvaluatorResult`.

Fabric evaluation examines:

* the final operational and lifecycle conditions of participating queue bundles;
* material queue progression that affects coordinated execution;
* dependencies among participating queue bundles;
* required timing and synchronization;
* shared capacity or access relationships;
* coordination dependencies;
* propagation of queue conditions across the fabric; and
* whether the represented coordination function can operate as required.

A fabric may contain individually clear queues while remaining unable to coordinate because of timing, sequencing, dependency, or synchronization failure. Conversely, the presence of a constrained queue does not by itself determine the complete fabric condition; the effect of that constraint is evaluated in the context of the fabric's coordination function.

For each evaluated `ProductFabric`, `FabricEvaluator` produces one immutable `FabricEvaluatorResult`.

Biosphere buses, cycles, BioNPUs, and other ClimateSOS system-model structures are not evaluated by the `FabricEvaluator`. Their state and behavior are evaluated by the applicable ClimateSOS system-model functions.

#### 9.4.1 FabricEvaluatorResult

A `FabricEvaluatorResult` records the evaluated coordination condition of one `ProductFabric` without modifying the fabric or its referenced `ProductQueueBundle` objects.

A `FabricEvaluatorResult` contains or references, as applicable:

* the evaluated `ProductFabric`;
* the participating `ProductQueueBundle` objects;
* the applicable `QueueEvaluatorResult` objects;
* the evaluated fabric coordination condition;
* timing, sequencing, synchronization, dependency, or shared-capacity conditions material to the result;
* queue execution results, conditions, or progress histories that materially affect coordinated operation;
* coordination failures, constraints, or unresolved relationships identified during evaluation;
* relevant pathway-comparison and downstream-propagation findings;
* assumptions and uncertainties affecting the evaluation;
* source, evidence, and provenance references;
* the evaluator and applicable rule-set version;
* the evaluation-run identity; and
* `user_id` and `pathway_id` attribution.

Where a fabric condition emerges from relationships among individually viable queue bundles, the `FabricEvaluatorResult` preserves the coordination relationships responsible for that result.

A completed `FabricEvaluatorResult` is immutable. It remains traceable to the evaluated `ProductFabric`, its referenced queue bundles, applicable `QueueEvaluatorResult` and `QueueExecutionResult` objects, relevant queue-progress history, transition and system context, and supporting evidence.

`FabricEvaluatorResult` records the result of fabric evaluation. It does not modify the `ProductFabric`, participating queue bundles, queue-progress records, or queue-evaluation results.

### 9.5 DocumentationEvaluator

`DocumentationEvaluator` evaluates the documentation, evidence, provenance, methodology, and unresolved claims required to support material pathway facts and evaluation findings.

It follows references from the `ProductPathway`, queue elements, assembly products, comparison findings, evaluator results, and other applicable evaluation structures to the associated `ProductIntakeBundle` and preserved source material.

`DocumentationEvaluator` evaluates, where applicable:

* whether referenced documentation or evidence is present and traceable;
* whether the evidence supports the fact or claim to which it is attached;
* provenance and source attribution;
* methodology and stated assumptions;
* material uncertainty;
* consistency among related evidence;
* certification, registry, audit, inspection, or test records;
* lifecycle, emissions, durability, storage, or other supporting records;
* unresolved or conflicting claims; and
* limitations that materially affect interpretation of the represented pathway.

The evaluator distinguishes the existence of documentation from the sufficiency of that documentation.

`DocumentationEvaluator` does not treat the existence of an MRV system as proof that the measurements or evidence produced by that system are valid. Operational MRV capability is represented and evaluated through the applicable MRV queue; documentation and evidence produced by or supporting that capability are evaluated here.

Where evidence is missing, incomplete, conflicting, uncertain, or insufficient for a required determination, that condition is preserved in the documentation findings and made available to the consolidated pathway assessment.

`DocumentationEvaluator` does not modify source records, pathway facts, progress records, or prior evaluator results or findings.

### 9.6 PathwayAssessment

The `PathwayEvaluationEngine` produces one immutable `PathwayAssessment` after all required pathway-evaluation functions have completed successfully.

The `PathwayAssessment` consolidates the results and findings produced during pathway evaluation while preserving their separate provenance and evaluator ownership.

The assessment contains or references, as applicable:

* the evaluated `ProductPathway`;
* the authoritative `TransitionPathway` used for comparison;
* the completed `InitialCharterResult`;
* direct pathway-comparison findings;
* substitution and combination findings;
* downstream-propagation findings;
* all applicable `QueueEvaluatorResult` objects;
* all applicable `FabricEvaluatorResult` objects;
* documentation and evidence findings;
* material assumptions and uncertainties;
* unresolved evaluation conditions;
* evaluator and rule-set versions;
* evidence and provenance references; and
* `user_id` and `pathway_id` attribution.

Applicable `QueueExecutionResult` and `QueueProgressRecord` objects remain reachable through their associated `QueueEvaluatorResult` objects. `PathwayAssessment` does not duplicate queue execution results or queue-progress history.

The `PathwayAssessment` records the evaluated relationships and operational findings needed by later stages. It does not overwrite the objects, results, progress records, or findings from which it was constructed.

The assessment does not itself determine the final validity of the pathway, its net overall system contribution, required scale, global-system risk, bound state, or final evaluation result. Those determinations occur in subsequent stages.

A pathway evaluation completes only when every required evaluator has completed its applicable work for the represented pathway, including any required re-evaluation, and the engine can produce a valid immutable `PathwayAssessment`.

An evaluator or result-integrity failure prevents completion of the current `PathwayAssessment`. A valid adverse, constrained, blocked, delayed, unresolved, or otherwise unsuccessful pathway result or finding does not by itself constitute an execution failure and remains part of the completed assessment.

---

## 10. Integrated Charter Evaluation

### 10.1 Integrated Evaluation Inputs

### 10.2 Integrated Charter Result

### 10.3 Newly Revealed Charter Conditions

### 10.4 Relationship to the Initial Charter Result

## 11. Product Outputs and Net Overall System Contribution

### 11.1 Product Outputs

### 11.2 Product Output Is Not System Contribution

### 11.3 NetOverallSystemContributionEvaluator

### 11.4 NetOverallSystemContribution

### 11.5 Fossil Displacement and Persistence Closure

### 11.6 Reliability, Deliverability, and Transition Timing

### 11.7 Limited or Unresolved Contribution

This retains the archive’s important product-output/system-contribution distinction, but locates the contribution itself in its proper downstream stage rather than in `ProductPathway`.

## 12. Scale Diagnostic

### 12.1 ScaleDiagnosticEvaluator

### 12.2 ScaleDiagnosticResult

### 12.3 Material Scale Contribution

### 12.4 Scale-Up Bottleneck

### 12.5 Limited or Local Contribution

### 12.6 Stale Success

### 12.7 Scale-Dependent Harms and Constraints

The archive’s `ScaleUpTippingState`, `ScaleUpBottleneck`, `SmallNodePersistence`, and `StaleSuccess` material belongs here, although the exact names are subject to change.

## 13. Candidate TransitionPathway Construction

### 13.1 Candidate and Prospective Candidate TransitionPathways
### 13.2 Candidate Construction Inputs
### 13.3 Global Candidate TransitionPathway
### 13.4 User-Submitted Prospective Candidate TransitionPathway
### 13.5 Candidate Immutability, Identity, and Provenance

## 14. Final Charter Evaluation

### 14.1 Final Evaluation Inputs
### 14.2 Final Charter Result
### 14.3 Relationship to Earlier Charter Results
### 14.4 Charter Authority and Non-Supersession
### 14.5 Conditions Preventing Ordinary Binding

## 15. Net Overall System Risk Evaluation

The `NetOverallSystemRiskEvaluator` evaluates how a candidate or prospective candidate `TransitionPathway` changes the overall risk profile of the accelerated net-zero transition.

It applies the transition-risk, bottleneck, timeline, pitfall, and failure-mode logic used to develop Appendices A–C of the *2030s Net Zero Playbook*. Its purpose is to document how the candidate affects:

* the Net Zero ASAP timeline;
* critical transition bottlenecks;
* synchronization and sequencing risks;
* fossil fallback and persistence risks;
* infrastructure, finance, workforce, adequacy, and delivery constraints;
* potential pitfalls and failure modes; and
* risks that are introduced, increased, reduced, transferred, or left unresolved.

The evaluator may perform Charter-style checks where those checks are necessary to identify or characterize a system risk. These checks are independent risk-analysis operations. They do not replace, revise, override, or supersede the `InitialCharterResult`, `IntegratedCharterResult`, or `FinalCharterResult`.

The Foundational Charter remains the authoritative source of Charter validity. Where a risk finding and a Charter finding address overlapping subject matter, both results must be preserved and their distinct purposes must remain explicit.

The evaluator produces documentation in the form of one immutable `NetOverallSystemRiskResult`.

### 15.1 Evaluation Purpose and Boundary
### 15.2 Candidate-to-Reference Risk Comparison
### 15.3 Appendix A–C Risk Logic
### 15.4 Net-Zero Timeline Effects
### 15.5 Bottlenecks, Pitfalls, and Failure Modes
### 15.6 New, Increased, Reduced, Transferred, and Unresolved Risks
### 15.7 Charter-Style Risk Checks
### 15.8 Relationship to the Final Charter Result
### 15.9 NetOverallSystemRiskResult

## 16. Binding and Bound States

### 16.1 BindingHandler

### 16.2 Binding Inputs

### 16.3 Applicable Bound States

### 16.4 Binding Does Not Re-Evaluate the Pathway

### 16.5 Binding Evidence and Explanation

## 17. Global Context Outcome

### 17.1 TransitionPathwayValidator

### 17.2 Validation Requirements

### 17.3 Atomic Immutable Commitment

### 17.4 Validation Failure

### 17.5 Preservation of the Existing Reference Pathway

### 17.6 Use at the Next Startup

## 18. User-Submitted Context Outcome

### 18.1 Immutable Global Reference Pathway

### 18.2 Separate Evaluation of Multiple Submissions

### 18.3 Result Construction

### 18.4 No Mutation of the Global TransitionPathway

### 18.5 Combined Pathways as Separate Intakes

## 19. EvaluationResult and State Preservation

### 19.1 EvaluationResult

### 19.2 Required Result Contents

### 19.3 Evidence and Explanation Trace

### 19.4 Prior-State Preservation

### 19.5 Re-Evaluation and Successor Results

### 19.6 No Writeback into ProductPathway

## 20. Resolution and Remedy

### 20.1 Resolution Outcomes

### 20.2 Remedy Eligibility

### 20.3 Remedy Processing

### 20.4 Re-Evaluation After Remedy

### 20.5 Non-Remediable Outcomes

### 20.6 Preservation of Failed and Unresolved Results

This preserves the useful archive material on remedy and state history without treating every failure as remedy-eligible or writing those states back into the pathway.

## 21. Evaluation Questions

### 21.1 What Does the Pathway Require?

### 21.2 What Does the Pathway Produce?

### 21.3 What System Contribution Results?

### 21.4 What Can Fail?

### 21.5 What Risks Propagate?

### 21.6 What Resolution or Remedy Is Available?

## 22. Implementation Requirements

### 22.1 Required Data Models

```
IdentityToken
ProductIntakeBundle
ProductPathway
ProductAdapterResult
ProductQueueBundle
ProductFabric
QueueProgressRecord
QueueExecutionResult
QueueEvaluatorResult
FabricEvaluatorResult
EvaluationResult
InitialCharterResult
PathwayAssessment
IntegratedCharterResult
ScaleDiagnosticResult
FinalCharterResult
NetOverallSystemRiskResult
NetOverallSystemContribution
TransitionPathway
EvaluatedPathway
```

### 22.2 Required Evaluators, Assemblers and Services

```
ProductAdapter
ProductAssembly
QueueBundler
FabricAssembler
PathwayEvaluationEngine
QueueEvaluator
FabricEvaluator
DocumentationEvaluator
PathwayComparator
NetOverallSystemRiskEvaluator
TransitionPathwayValidator
CharterEvaluator
ScaleDiagnosticEvaluator
BindingHandler
```
### 22.3 Immutability and State-Integrity Requirements

### 22.4 Identity and Attribution Requirements

### 22.5 Error and Missing-Result Requirements

### 22.6 Minimum Test Cases

## 23. Relationship to the ClimateSOS Runtime Architecture

### 23.1 Shared Product Pathway Evaluation Flow

### 23.2 Global Boot Context

### 23.3 User-Submitted Context

### 23.4 Component Ownership Summary

## 24. Summary

