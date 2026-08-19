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
* assembly of pathway objects into `ProductQueueBundle`, and `ProductFabricBundle` groupings, as applicable;
* comparison of the pathway with the global `TransitionPathway`;
* pathway, documentation, contribution, scale, and system-risk evaluation;
* final Charter evaluation;
* binding into an applicable `[Foo]Bound` state; and
* validation and commitment of the global `TransitionPathway`, or result construction for a user-submitted pathway.

Models hold state and results. Adapters, assemblers, comparators, evaluators, validators, and handlers perform work.

### 4.3 Immutable State and Result Objects

Completed ClimateSOS pathway, assembly, evaluation, Charter, contribution, scale, risk, binding, and result objects are immutable.

Work-performing components may maintain transient state while executing, but once a canonical data object or result is produced, later stages do not modify it. They preserve references to prior objects and create new objects to represent subsequent assembly, evaluation, state transitions, or results.

This applies to objects such as `ProductIntakeBundle`, `ProductAdapterResult`, `ProductPathway`, `ProductQueueBundle`, `ProductFabric`, Charter results, pathway assessments, system-contribution and scale results, candidate or validated `TransitionPathway` snapshots, risk results, bound-state records, and `EvaluationResult`.

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

In the user-submitted context, a user may provide one or more intake submissions, each of which generates a separate `ProductPathway` for evaluation against the current validated global `TransitionPathway`. In user-submitted mode, the global `TransitionPathway` is immutable. One or more user-submitted candidate pathways may be evaluated separately and do not modify the global `TransitionPathway`. Each candidate pathway’s modeled effects and evaluation findings are recorded in its `EvaluationResult`.

After global-system-risk evaluation, final Charter evaluation, and binding, each user-submitted pathway proceeds to construction of an `EvaluationResult`.

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
Identity Gateway  => Identity Layer
    IdentityToken <=      -|
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
    │
    ├── ProductPathway
    │       Normalized pathway represented as an internal map or graph.
    │
    └── ProductIntakeBundle reference
            Preserves the pathway's association with its immutable
            intake materials and IdentityToken.
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
    ├── FabricStitcher, where applicable
    │       └── ProductFabricBundle(s)
    │
    ▼
PathwayEvaluationEngine
    │
    ├── PathwayComparator
    │       └── compares the ProductPathway with the current
    │           authoritative TransitionPathway
    │      ├── synchronization
    │      ├── substitutions
    │      ├── downstream propagation
    │      └── transition interactions   
    │
    ├── QueueEvaluator
    │       └── evaluates ProductQueueBundle(s)
    │
    ├── FabricEvaluator, where applicable
    │       └── evaluates ProductFabricBundle(s)
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
    |     Prospective Candidate TransitionPathway refers to a
    |     possible future reference TransitionPathway.
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
    |      ↓
Run the Shared Product Pathway Evaluation Flow
    |  Identity Gateway   =>   IdentityLayer
    |      IdentityToken  <=        -|
    |      ↓
    │  Global Intake Layer
    |      ↓
    |  ProductIntakeBundle
    │      ↓
    │  ProductAdapter
    │      ↓
    │  ProductAdapterResult
    |      ↓
    |  ProductAdapter
    |      ↓
    |  ProductAdapterResult
    |    ├── ProductPathway
    |    └── ProductIntakeBundle reference
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
    |  the candidate delta, but before validation and atomic commitment.
    │  This Candidate is separate from the global and current reference
    |  TransitionPathway.
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
    |
Run Shared Product Pathway Evalaution
    Identity Gateway => IdentityLayer
    | IdentityToken  <=      -|
    |    
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
EvaluationResult A                                      EvaluationResult B

===============================================================================

User-submitted evaluation invariants:

• Each submission receives its own `IdentityToken` and produces its own immutable `ProductIntakeBundle`. Each `ProductIntakeBundle` is adapted into a separate `ProductAdapterResult`, `ProductPathway`, and evaluation history.

• Each ProductPathway is evaluated separately against the same current
  validated global TransitionPathway.

• Each prospective candidate TransitionPathway represents the modeled effect
  of that user-submitted ProductPathway on the global reference.

• A user-submitted candidate does not modify or replace the validated global
  TransitionPathway.

• Each `EvaluationResult` preserves that candidate pathway's findings, Charter results, contribution, scale, global-system risk, bound state, evidence, provenance, and state history, together with references sufficient to trace the evaluation back through the `ProductAdapterResult`, `ProductIntakeBundle`, and `IdentityToken`.

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
* assemble represented fabric elements into `ProductFabricBundle` structures;
* assemble represented bus elements into a `ProductBusFleet`;
* evaluate assembled queue bundles, fabric bundles, or bus fleets; or
* compare the completed pathway with the athoritative `TransitionPathway`.

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

`ProductAssembly` constructs the pathway-derived objects that are later consumed by downstream evaluators. It coordinates the assembly functions that group represented pathway structures into queue bundles and fabrics while preserving the identity, relationships, provenance, and traceability established by the `ProductAdapter`.

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

It does not perform Charter evaluation, compare the pathway with the authoritative `TransitionPathway`, evaluate queue or fabric state, determine system contribution or scale, construct a candidate `TransitionPathway`, evaluate global-system risk, assign a bound state, or construct the final `EvaluationResult`.

Assembly omits creating a product grouping where the corresponding substructure is not present in the pathway. The absence of a `ProductFabric` is not an error when the pathway does not require applicable `ProductQueueBundle` objects to be grouped into a fabric.

### 7.2 QueueBundler

`QueueBundler` groups applicable queue elements represented in the `ProductPathway` and constructs one or more `ProductQueueBundle` objects.

A `ProductPathway` may contain multiple queue elements representing distinct inputs, outputs, dependencies, constraints, access requirements, or execution conditions. `QueueBundler` groups related queue elements into one or more `ProductQueueBundle` objects according to their evaluable function and represented relationships.

Queue-bundle boundaries are determined by evaluable function and represented relationships, not merely by pathway direction. A pathway may therefore contain separate bundles for input access, output delivery, finance, permitting, workforce, documentation, or other applicable queue functions.

`QueueBundler` uses the relationships represented in the `ProductPathway` to determine which queue elements belong together. It preserves relevant ordering, dependency, timing, identity, and provenance relationships carried by those elements.

`QueueBundler` does not create a queue condition absent from the `ProductPathway`, infer an unstated dependency, or determine whether a represented queue is clear, blocked, starved, expired, closed, delayed, stale, or otherwise successful or unsuccessful. Those determinations belong to downstream evaluation.

Each completed queue grouping is returned as an immutable `ProductQueueBundle`.

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

FabricAssembler does not create missing queue bundles or infer unsupported fabric membership. It does not evaluate queue state or determine fabric readiness; queue-state and fabric-readiness evaluation belong to FabricEvaluator.

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
* queue bundles are grouped according to represented evaluable functions and relationships;
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

### 8.1 Feedstock and Input Access

### 8.2 Product Output and Delivery Access

### 8.3 Bankability and Revenue Certainty

### 8.4 Project Finance

### 8.5 Non-Dilutive Capital and Public Support

### 8.6 Permitting and Authorization

### 8.7 Workforce and Execution

### 8.8 MRV, Documentation, and Evidence

### 8.9 Fossil-Exit Finance and Persistence Closure

### 8.10 Other Pathway-Specific Queues

The archive treated these as “required queue categories,” but its underlying text already acknowledged that a pathway may require only some of them. I would therefore use **Product Queue Categories**, not **Required Queue Categories**. 

## 9. Pathway Evaluation Engine

### 9.1 Evaluation Responsibilities and Boundary

### 9.2 PathwayComparator

### 9.3 Direct Pathway Comparison

### 9.4 Substitution and Combination Evaluation

### 9.5 Downstream Propagation

### 9.6 QueueEvaluator

### 9.7 FabricEvaluator

### 9.8 BusEvaluator

### 9.9 DocumentationEvaluator

### 9.10 PathwayAssessment

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
```

### 22.2 Required Evaluators and Services

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

