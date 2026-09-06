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
* system-side determination of the applicable `[Foo]Bound` state;
* binding of the completed `FinalPathwayResult` and applicable bound state
  into an immutable `BoundPathway`; and
* construction of the final `PathwayAssessment` before the global-context or
  user-submitted-context outcome flow.

Models hold state and results. Adapters, assemblers, comparators, evaluators, validators, and handlers perform work.

### 4.3 Immutable State and Result Objects

Completed ClimateSOS pathway, assembly, evaluation, Charter, contribution, scale, risk, binding, and result objects are immutable.

Work-performing components may maintain transient state while executing, but once a canonical data object or result is produced, later stages do not modify it. They preserve references to prior objects and create new objects to represent subsequent assembly, evaluation, state transitions, or results.

This applies to objects such as `ProductIntakeBundle`, `ProductAdapterResult`,
`ProductPathway`, `ProductQueueBundle`, `ProductFabric`,
`QueueProgressRecord`, `QueueExecutionResult`, `QueueEvaluatorResult`,
`FabricEvaluatorResult`, Charter results, system-contribution and scale
results, candidate or validated `TransitionPathway` snapshots, risk results,
`FinalPathwayResult`, bound-state records, `BoundPathway`, and
`PathwayAssessment`.

Where ClimateSOS models changing system state, each preserved state is represented as a new immutable snapshot or result rather than by rewriting a previously completed object.

Work-performing components such as adapters, assemblers, evaluators, validators, and handlers are not subject to this object-immutability rule merely because they produce immutable outputs.

### 4.4 Progressive Charter Evaluation

The ClimateSOS Foundational Charter is evaluated at three stages:

1. **Initial Charter Evaluation** — evaluates the `ProductPathway`, which is the normalized intake produced by the `ProductAdapter` as an internal map or graph, before assembly and pathway evaluation.
2. **Integrated Charter Evaluation** — evaluates findings revealed through pathway comparison, assembled-group evaluation, documentation assessment, and downstream propagation.
3. **Final Charter Evaluation** — evaluates the completed contribution, scale, candidate-transition, and global-system-risk findings before binding.

Each stage produces a separate immutable result. A later Charter result may reference, but must not overwrite, an earlier result.

Required Charter checks that are absent, null, malformed, overwritten, or unexecuted are recorded as `MISSING`. A `MISSING` check forces the enclosing Charter result to `ERROR` and prevents normal progression.

Detailed Charter check statuses, blocking behavior, evaluator-integrity requirements, remedy eligibility, and re-evaluation rules are defined in a separate Charter Evaluation Flow document.

### 4.5 Global and User-Submitted Pathway Outcomes

The two flows share the same architecture until their final outcomes diverge.

The global context is used strictly to update the reference `TransitionPathway`. It occurs after the program starts and before a user can evaluate one or more product pathways. In this global evaluation context, one candidate global `TransitionPathway` is evaluated against one authoritative global reference `TransitionPathway` at a time. The candidate may represent a limited proposed delta or a prospective replacement for a larger portion of the global net-zero transition. The reference is either the Playbook-derived global pathway or the previously validated `TransitionPathway`.

After pathway evaluation, contribution analysis, scale diagnosis, global-system-risk evaluation, final Charter evaluation, and binding, the candidate must pass `TransitionPathwayValidator` before it can be atomically committed as the validated global `TransitionPathway`. Once committed, the newly validated global `TransitionPathway` replaces the previous reference pathway. It is preserved for use at the next startup and serves as the current reference pathway if the user proceeds with evaluation of a user-submitted `ProductPathway`.

In the user-submitted context, a user may provide one or more intake submissions, each of which generates a separate `ProductPathway` for evaluation against the current validated global `TransitionPathway`. In user-submitted mode, the global `TransitionPathway` is immutable. One or more user-submitted candidate pathways may be evaluated separately and do not modify the global `TransitionPathway`. Each candidate pathway’s modeled effects and evaluation findings are recorded in its `PathwayAssessment`.

After global-system-risk evaluation, Final Charter Evaluation, and binding,
each user-submitted pathway produces an immutable `BoundPathway`, which then
proceeds to construction of a `PathwayAssessment`.

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
PathwayEngineResult
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
TransitionPathwayCompiler
    │  Construct Candidate or Prospective Candidate TransitionPathway
    │  Global context: Candidate TransitionPathway
    │  User-submitted context: Prospective Candidate TransitionPathway
    │
    ▼
NetOverallSystemRiskEvaluator
    │
    ▼
NetOverallSystemRiskResult
    │
    ▼
FinalPathwayAssembly
    │
    ▼
FinalPathwayResult ───────────────────────────────────────┐
    │                                                     │
    ▼                                                     │
CharterEvaluator                                          │
    │                                                     │
    │  FINAL CHARTER PASS                                 │
    ▼                                                     │
FinalCharterResult                                        │
    │                                                     │
    │  Separate immutable record that references but      │
    │  does not overwrite the earlier Charter results.    │
    ▼                                                     │
System bound-state determination                          │
    │                                                     │
    ▼                                                     │
Applicable [foo]Bound ────────────────────────────────────┤
                                                          ▼
                                                    BindingHandler
                                                          │
                                                          ▼
                                                     BoundPathway
                                                          │
                                                          ▼
                                                   PathwayAssessment
                                                          │
                              ┌───────────────────────────┴───────────────────────────┐
                              │                                                       │
                              ▼                                                       ▼
                       Global context                                        User-submitted context
                              │                                                       │
                              ▼                                                       ▼
                   TransitionPathwayValidator                                      return
                              │
                              │  privileged global-context operation
                              ▼
                   Atomic immutable commitment
                              │
                              ▼
                      TransitionPathway

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
    │  PathwayEngineResult
    │      ↓
    │  IntegratedCharterResult
    │      ↓
    │  NetOverallSystemContribution
    │      ↓
    │  ScaleDiagnosticResult
    │
    ▼
TransitionPathwayCompiler
    │  Construct Candidate or Prospective Candidate TransitionPathway
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
FinalPathwayAssembly
    │
    ▼
FinalPathwayResult
    │
    ▼
CharterEvaluator
    │  FINAL CHARTER PASS
    │
    ▼
FinalCharterResult
    │
    ▼
System bound-state determination
    │
    ▼
Applicable ExampleBound State
    │
    ▼
BindingHandler
    │
    ▼
BoundPathway
    │
    ▼
PathwayAssessment
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
PathwayEngineResult A                                     PathwayEngineResult B
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
FinalPathwayResult A                                    FinalPathwayResult B
    │                                                             │
    ▼                                                             ▼
FinalCharterResult A                                    FinalCharterResult B
    │                                                             │
    ▼                                                             ▼
System bound-state determination A               System bound-state determination B
    │                                                             │
    ▼                                                             ▼
Applicable ExampleBound State A                     Applicable ExampleBound State B
    │                                                             │
    ▼                                                             ▼
BindingHandler                                              BindingHandler
    │                                                             │
    ▼                                                             ▼
BoundPathway                                                 BoundPathway 
    │                                                             │
    ▼                                                             ▼
PathwayAssessment A                                       PathwayAssessment B

===============================================================================

User-submitted evaluation invariants:

• Each submission receives its own `IdentityToken` and produces its own immutable `ProductIntakeBundle`. Each `ProductIntakeBundle` is adapted into a separate `ProductAdapterResult`, `ProductPathway`, and evaluation history.

• Each ProductPathway is evaluated separately against the same current
  validated global TransitionPathway.

• Each prospective candidate TransitionPathway represents the modeled effect
  of that user-submitted ProductPathway on the global reference.

• A user-submitted candidate does not modify or replace the validated global
  TransitionPathway.

• Each `PathwayAssessment` preserves that candidate pathway's findings, Charter results, contribution, scale, global-system risk, bound state, evidence, provenance, and state history, together with references sufficient to trace the evaluation back through the `ProductAdapterResult`, `ProductIntakeBundle`, and `IdentityToken`.

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

All Charter checks are required. The Initial Charter Evaluation executes every Charter check using the information available at the Initial Charter stage. Each check executes independently, and a prior finding does not short-circuit or remove any remaining check.

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

`MISSING` indicates that a Charter check did not produce a valid result. This occurs when the required check did not execute, timed out, executed without recording a result state, or produced a result that is absent, null, malformed, overwritten, or otherwise unavailable as a valid check result.

A `MISSING` check is an evaluator-integrity failure. The enclosing `InitialCharterResult` is recorded as `ERROR`, and the current pathway evaluation does not proceed until the execution error is resolved.

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

It does not perform Charter evaluation, compare the pathway with the authoritative `TransitionPathway`, evaluate queue or fabric state, determine system contribution or scale, construct a candidate `TransitionPathway`, evaluate global-system risk, assign a bound state, or construct the final `PathwayAssessment`.

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

Evaluation begins after `ProductAssembly` completes successfully. The engine receives the immutable pathway and assembly products created by earlier stages. After all required subevaluators complete successfully, the engine produces a consolidated immutable `PathwayEngineResult`.

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
PathwayEngineResult
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
* produces one consolidated immutable `PathwayEngineResult`.

The engine does not modify any input or assembly object. It does not perform the Integrated Charter Evaluation, determine net overall system contribution, perform the Scale Diagnostic, construct a candidate `TransitionPathway`, evaluate net overall system risk, assign a bound state, or construct the final `PathwayAssessment`.

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

### 9.6 PathwayEngineResult

The `PathwayEvaluationEngine` produces one immutable `PathwayEngineResult` after all required pathway-evaluation functions have completed successfully.

The `PathwayEngineResult` consolidates the results and findings produced during pathway evaluation while preserving their separate provenance and evaluator ownership.

The `PathwayEngineResult` contains or references, as applicable:

* the evaluated `ProductPathway`;
* a reference to the authoritative `TransitionPathway` used for comparison;
* the completed `InitialCharterResult`;
* direct pathway-comparison findings;
* substitution and combination findings;
* downstream-propagation findings;
* all applicable `QueueEvaluatorResult` objects;
* all applicable `FabricEvaluatorResult` objects;
* documentation and evidence findings;
* material assumptions and uncertainties;
* unresolved evaluation conditions;
* applicable transition and system context;
* evaluator and rule-set versions;
* evidence and provenance references; and
* `user_id` and `pathway_id` attribution.

Applicable `QueueExecutionResult` and `QueueProgressRecord` objects remain reachable through their associated `QueueEvaluatorResult` objects. `PathwayEngineResult` does not duplicate queue execution results or queue-progress history.

The `PathwayEngineResult` records the evaluated relationships and operational findings needed by later stages. It does not overwrite the objects, results, progress records, or findings from which it was constructed.

The `PathwayEngineResult` does not itself determine the final validity of the pathway, its net overall system contribution, required scale, global-system risk, bound state, or final evaluation result. Those determinations occur in subsequent stages.

A pathway evaluation completes only when every required evaluator has completed its applicable work for the represented pathway, including any required re-evaluation, and the engine can produce a valid immutable `PathwayEngineResult`.

An evaluator or result-integrity failure prevents completion of the current `PathwayEngineResult`. A valid adverse, constrained, blocked, delayed, unresolved, or otherwise unsuccessful pathway result or finding does not by itself constitute an execution failure and remains part of the completed assessment.

---

## 10. CharterEvaluator — Integrated Charter Evaluation

The `CharterEvaluator` performs the Integrated Charter Evaluation after pathway assembly and pathway evaluation have completed.

At this stage, the completed `PathwayEngineResult` contains operational, relational, transition, and system-context findings that were not available during the Initial Charter Evaluation. These findings may reveal emergent behavior, propagated effects, dependencies, interactions, or other conditions that change the Charter evaluation of the pathway.

As all Charter checks are required, the `CharterEvaluator` reruns every Charter check using the information available at the Integrated Charter stage. Each check executes independently, and a finding from the Initial Charter Evaluation does not short-circuit, satisfy, or remove any remaining check.

The `CharterEvaluator` distinguishes Charter findings from evaluator execution failures. A successfully executed check may return a failed, adverse, unresolved, not-applicable, or other valid Charter finding. Those findings remain part of the pathway evaluation record and may affect later evaluation and binding.

The Integrated Charter Evaluation completes only when every Charter check has executed and the `CharterEvaluator` has produced a valid immutable `IntegratedCharterResult`. An evaluator or result-integrity failure prevents the current pathway evaluation from proceeding.

```text
PathwayEngineResult
    ├── InitialCharterResult reference
    ├── pathway-comparison findings
    ├── queue and fabric evaluation results
    ├── downstream-propagation findings
    ├── documentation and evidence findings
    ├── assumptions and uncertainties
    └── applicable transition and system context
            │
            ▼
      CharterEvaluator
 Integrated Charter Evaluation
            │
            ▼
   IntegratedCharterResult
```

### 10.1 Integrated Charter Inputs

The `CharterEvaluator` receives the completed immutable `PathwayEngineResult` and the Charter resources required to perform the Integrated Charter Evaluation.

Its inputs include:

* the immutable `PathwayEngineResult`;
  * the evaluated `ProductPathway`;
  * the authoritative `TransitionPathway` used during pathway evaluation;
  * the completed `InitialCharterResult`;
  * direct pathway-comparison findings;
  * substitution and combination findings;
  * downstream-propagation findings;
  * applicable `QueueEvaluatorResult` objects;
  * applicable `FabricEvaluatorResult` objects;
  * documentation and evidence findings;
  * material assumptions and uncertainties;
  * unresolved evaluation conditions;
  * applicable transition and system-side findings; and
  * supporting evidence and provenance references;
* the ClimateSOS Foundational Charter distributed with the ClimateSOS runtime;
* the complete set of Charter checks;
* the evaluator version and Charter rule-set version; and
* any runtime configuration required to perform the Integrated Charter Evaluation.

The `CharterEvaluator` follows references preserved by the `PathwayEngineResult` when a Charter check requires the underlying pathway structure, evaluation result, source documentation, evidence, provenance, or system-side finding.

The `CharterEvaluator` evaluates the pathway against the Foundational Charter by running every Charter check against the completed `PathwayEngineResult` and its referenced evaluation results. It does not add missing pathway facts, convert unresolved conditions into established facts, or treat an unsupported possible effect as an established pathway condition.

### 10.2 Integrated Charter Result

The `CharterEvaluator` produces one immutable `IntegratedCharterResult`.

The `IntegratedCharterResult` records the complete outcome of the Integrated Charter Evaluation using the pathway, transition, and system information available after completion of the `PathwayEngineResult`.

The `IntegratedCharterResult` contains:

* a reference to the evaluated `PathwayEngineResult`;
* a reference to the associated `InitialCharterResult`;
* the result of every Charter check;
* findings, evidence references, and supporting provenance associated with each check;
* applicable pathway-evaluation or system-side findings supporting each check;
* unresolved or not-applicable conditions returned by completed checks, where applicable;
* any execution error associated with an individual check or with the Integrated Charter Evaluation;
* the evaluator version;
* the Charter rule-set version; and
* the resulting Integrated Charter status.

Each Charter check records its result at the Integrated Charter stage.

If a Charter check does not execute, does not complete, times out, produces no valid result, or produces a result that is absent, null, malformed, overwritten, or otherwise unavailable, the check is `MISSING`.

A `MISSING` check is an evaluator-integrity failure. The `IntegratedCharterResult` is recorded as `ERROR`, and the current pathway evaluation does not proceed until the execution error is resolved.

`UNRESOLVED` and `NOT_APPLICABLE` remain distinct from `MISSING`. A successfully executed check may return either state where permitted by the applicable Charter rule.

The completed `IntegratedCharterResult` is immutable. Later stages may reference it and carry its findings forward, but they do not overwrite or replace it.

### 10.3 Newly Revealed Charter Findings

The Integrated Charter Evaluation may identify pathway findings relevant to Charter evaluation that were not observable during the Initial Charter Evaluation.

Pathway evaluation may reveal findings arising from:

* interactions among represented pathway elements, including emergent behavior not apparent from any one element in isolation;
* queue execution, dependency, timing, ordering, or synchronization behavior;
* coordination among applicable `ProductFabric` objects;
* comparison with the authoritative `TransitionPathway`;
* substitution or combination effects;
* downstream propagation through connected transition or system relationships;
* applicable system-side evaluation;
* documentation or evidence findings;
* newly exposed assumptions, uncertainties, or unresolved dependencies; or
* another material condition established during construction of the `PathwayEngineResult`.

These findings may change the result of a Charter check that was previously clear, adverse, unresolved, not applicable, or otherwise valid at the Initial Charter stage. They may also expose a Charter-relevant pathway finding that could not previously be evaluated from the information available at that earlier stage.

Where an Integrated Charter finding differs from the corresponding Initial Charter finding, the `IntegratedCharterResult` preserves the pathway findings, evidence, system context, or other material information supporting the changed determination. The evaluation history must remain sufficient to identify what changed between the two Charter evaluations.

### 10.4 Relationship to the Initial Charter Result

The `InitialCharterResult` and `IntegratedCharterResult` are separate immutable records produced by the `CharterEvaluator` at different points in the Product Pathway Evaluation Flow.

The `InitialCharterResult` records the complete Charter evaluation performed before `ProductAssembly` and downstream pathway evaluation. The `IntegratedCharterResult` records the complete Charter evaluation performed after those stages have produced the `PathwayEngineResult`.

The `CharterEvaluator` reruns every Charter check during the Integrated Charter Evaluation. It does not update the `InitialCharterResult`, reuse its individual check results as current results, or treat successful completion of the Initial Charter Evaluation as satisfaction of a later Charter check.

A Charter finding may remain unchanged between the two evaluations or may change because additional information, emergent behavior, propagated effects, or system context has become available. Both results remain part of the pathway evaluation history.

Successful completion of the Integrated Charter Evaluation produces a valid immutable `IntegratedCharterResult` and permits progression to Net Overall System Contribution evaluation. Failed, adverse, unresolved, not-applicable, or other valid Charter findings remain in the evaluation history and continue downstream. An evaluator or result-integrity failure prevents the current pathway evaluation from proceeding.

---

## 11. Product Outputs and Net Overall System Contribution

Evaluation of the `ProductPathway` by the `PathwayEvaluationEngine` and its related
subcomponents, including pathway comparison, queue and fabric evaluation, and
documentation evaluation, produces a `PathwayEngineResult` containing the pathway's
outputs and associated evaluation state.

After the Integrated Charter Evaluation, the data available from `PathwayEngineResult`
and `IntegratedCharterResult` are ready for processing by the
NetOverallSystemContributionEvaluator` to determine the pathway's evaluated
effect on the broader net-zero transition.

The outputs produced or enabled by the `ProductPathway` do not in themselves
establish their broader or global contribution to the accelerated net-zero
transition. ClimateSOS therefore evaluates how those outputs affect the broader
transition beyond the pathway itself.

The `NetOverallSystemContributionEvaluator` evaluates the pathway's net effect
on the broader net-zero transition using the completed pathway evaluation, its
established interactions with the authoritative `TransitionPathway`, and the
applicable global transition context. It records the contribution substantiated
by that evaluation.

The evaluator produces one immutable `NetOverallSystemContribution`.

The contribution result does not determine scale, construct a candidate
`TransitionPathway`, perform net-overall-system-risk evaluation, perform the
Final Charter Evaluation, assign a bound state, or authorize commitment or
deployment. Those operations occur in later stages.

### 11.1 Product Outputs

The `ProductPathway` may produce or enable one or more outputs. Evaluation by the
`PathwayEvaluationEngine` records those outputs together with their associated
evaluation state in `PathwayEngineResult`, as defined in
[Section 9.6](#96-pathwayengineresult).

See [Section 9.6](#96-pathwayengineresult) for the detailed specification of
product outputs within `PathwayEngineResult`.

An output may be technically useful, commercially valuable, locally beneficial, or
operationally feasible without making a material net overall system contribution
to the net-zero transition.

### 11.2 Product Output Is Not System Contribution

A pathway can produce useful, beneficial, or transition-relevant outputs at many
scales. Those outputs are recorded in `PathwayEngineResult` together with their
associated evaluation state and are carried forward for subsequent evaluation.

The outputs represented in `PathwayEngineResult` and the resulting
`NetOverallSystemContribution` describe different properties of a pathway.

A product output answers:

> What does the pathway produce or enable?

A net overall system contribution answers:

> What does the evaluated pathway change in the broader net-zero transition?

Together `PathwayEngineResult` and `NetOverallSystemContribution` show effects
at different scales and through different mechanisms. Some effects may remain
local, enable other transition activity, reduce a material constraint, influence
or replace a system function, or contribute to broader change across the net-zero
transition.

Depending on the represented pathway and its evaluated relationships, an output may:

* provide value primarily within the pathway, project, customer, or local context;
* produce a local or regional transition benefit;
* enable or strengthen a broader transition function;
* reduce a material transition constraint or dependency;
* substitute for a fossil-dependent product, process, service, or system function;
* support retirement or displacement of fossil-dependent capacity;
* propagate effects through connected infrastructure, supply chains, finance, workforce,
  or other parts of the broader transition, or
* contribute to a material change in the broader global net-zero transition.

These forms of contribution are not interchangeable. A locally beneficial
output may remain locally bounded, while another pathway may provide an enabling
function whose effects propagate across multiple parts of the broader transition.
A pathway may also contribute through direct replacement of an existing
fossil-dependent function.

### 11.3 NetOverallSystemContributionEvaluator

The `NetOverallSystemContributionEvaluator` evaluates the pathway's effects on
the broader net-zero transition using the completed upstream evaluation record.
It examines the scope of those effects, the established mechanisms through which
they propagate, the dependencies and substitutions they rely on, the system
functions they influence or replace, and their downstream consequences.

Its inputs are:

* the completed `PathwayEngineResult`; and
* the completed `IntegratedCharterResult`.

`PathwayEngineResult` provides the consolidated pathway-evaluation state required
by the `NetOverallSystemContributionEvaluator`, including the evaluated
`ProductPathway`, references identifying the authoritative `TransitionPathway`
and applicable system context used during evaluation, the resulting evaluation
findings and results, assumptions and uncertainties, evidence and provenance,
and pathway attribution, as specified in
[Section 9.6](#96-pathwayengineresult).

The evaluator uses these inputs to determine the pathway's net overall system
contribution, including whether and how the pathway:

* replaces, reduces, retires, or avoids fossil-dependent activity;
* supports clean-only growth rather than parallel clean-and-fossil growth;
* replaces a fossil reliability, adequacy, feedstock, fuel, heat, transport,
  infrastructure, or other system function;
* reduces fossil fallback or persistence risk;
* contributes to emissions reduction;
* advances verified durable CDR and movement down its learning curve without
  counting removals toward net-zero emissions abatement or required
  source-emissions elimination;
* preserves, restores, strengthens, degrades, or otherwise materially affects
  biosphere integrity, ecological function, or resilience;
* improves transition adequacy, deliverability, or synchronization;
* supports infrastructure, finance, workforce, industrial conversion, or other
  transition-enabling capacity;
* resolves or reduces a material net-zero transition dependency or unconstrains
  one or more transition bottlenecks;
* adds, reduces, shifts, or otherwise materially affects energy, resource,
  infrastructure, or other demand on the broader transition;
* introduces, removes, reduces, or transfers material emissions, resource,
  infrastructure, ecological, or other system burdens that affect its net contribution;
* shortens, preserves, delays, or extends the time required to reach accelerated
  operational net zero;
* introduces effects that depend on unresolved downstream conditions; or
* provides local, limited, indirect, conditional, or presently unresolved
  system value.

Where a supported contribution depends on an upstream comparison finding,
queue result, fabric result, documentation finding, system-model relationship,
or evidence source, the resulting `NetOverallSystemContribution` preserves
references sufficient to trace that dependency.

The evaluator does not infer contribution from a product label, technology
class, commercial claim, emissions claim, or declared pathway purpose. It
evaluates the effects supported by the completed record.

The evaluator does not modify the `ProductPathway`, `PathwayEngineResult`,
`IntegratedCharterResult`, `TransitionPathway`, or any upstream result. It
constructs one new immutable `NetOverallSystemContribution`.

### 11.4 NetOverallSystemContribution

`NetOverallSystemContribution` is the immutable result of the
`NetOverallSystemContributionEvaluator`.

It records the supported effects of the pathway on the broader net-zero
transition.

The result contains or references, as applicable:

* the evaluated `ProductPathway`;
* the `PathwayEngineResult` from which the contribution evaluation was derived;
* the associated `IntegratedCharterResult`;
* a reference to the authoritative `TransitionPathway` used during system evaluation;
* the evaluated system-contribution findings;
* the pathway outputs associated with those contributions;
* contribution findings and supporting attribution for effects that materially
  affect the net-zero transition;
* contribution findings and supporting attribution for effects that materially
  affect transition timing;
* material dependencies and conditions affecting contribution;
* limited, indirect, conditional, or unresolved contribution findings;
* material assumptions and uncertainties;
* supporting comparison, queue, fabric, and documentation findings;
* evidence and provenance references;
* evaluator and rule-set versions; and
* `user_id` and `pathway_id` attribution.

The result preserves the distinction between supported contribution findings
and contribution claims that remain conditional, unresolved, or unsupported by
the completed evaluation record. Absence of sufficient evidence for a
particular contribution does not cause the evaluator to create one from pathway
intent.

The result may contain more than one contribution when a pathway affects
multiple transition functions.

`NetOverallSystemContribution` is not a scalar score of pathway goodness and
does not rank otherwise incomparable forms of contribution onto a single
numerical axis.

The contribution result does not determine whether the pathway can reach
material scale. Scale is evaluated separately by the `ScaleDiagnosticEvaluator`.

#### 11.4.1 Fossil Displacement and Persistence Closure

A clean, lower-carbon, or transition-enabling output does not qualify as fossil
displacement unless the evaluated pathway reduces, substitutes for, retires,
avoids, or otherwise materially changes a fossil-dependent activity, asset,
flow, financial pathway, or system function.

The contribution evaluation therefore distinguishes between:

* additional clean activity operating alongside continuing fossil activity;
* reduction in fossil fuel, feedstock, throughput, or utilization;
* substitution for a fossil product or process;
* replacement of a fossil reliability or adequacy function;
* retirement or avoidance of a fossil asset or capability;
* closure of refinancing, insurance, contracting, capacity-payment, or other
  mechanisms that would otherwise extend fossil operation;
* reduction of credible fossil fallback pathways; and
* closure of a material fossil-persistence pathway.

Where fossil displacement affects fossil-dependent workers or communities,
the associated workforce retirement, transition, redeployment, closure, or
other material transition conditions remain explicit in the contribution
findings.

Where continued fossil operation is required for the evaluated contribution,
that dependency remains explicit in the result.

A pathway must not be credited with fossil displacement merely because its
output could theoretically replace a fossil function. The relevant
substitution, retirement, or persistence-closure relationship must be supported
by the pathway evaluation and available evidence. The completed contribution
is subsequently included in the Final Charter Evaluation, which determines
whether the resulting pathway state conforms to the Charter safeguards and
guardrails.

Where displacement is partial, conditional, delayed, indirect, or unresolved,
the contribution result records that condition rather than representing full
displacement.

Fossil displacement also requires that any required system function performed
by the displaced fossil activity be replaced, eliminated, or otherwise rendered
unnecessary. This applies to reliability, adequacy, feedstock, heat, transport,
industrial, infrastructure, and other required system functions. Nominal
retirement while a required function remains unresolved does not by itself
establish durable fossil displacement.

#### 11.4.2 Reliability, Deliverability, and Transition Timing

A pathway may make a real system contribution, while that contribution may or
may not be sufficiently reliable, deliverable, or timely for the transition
function. The contribution may support, replace, render unnecessary, or
otherwise affect a required system function.

Reliability, deliverability, and timing are evaluated separately because they
determine whether an identified contribution can actually perform its required
role within the broader net-zero transition.

A contribution may be technically valid but unavailable at the required time,
dependent on unresolved infrastructure, unable to satisfy a reliability or
adequacy requirement, or sequenced incorrectly relative to dependent transition
activities.

The `NetOverallSystemContributionEvaluator` therefore evaluates whether the
contribution can perform the required function in the required system context
and within the required transition window.

The evaluator uses the completed pathway evaluation, established transition
interactions, and relevant system context to determine whether the evaluated
contribution is consistent with:

* the reliability or adequacy function being supported, replaced, eliminated,
  or otherwise rendered unnecessary;
* required infrastructure and delivery relationships;
* sequencing with dependent transition activities;
* permitting, finance, workforce, supply-chain, and execution conditions;
* the geographic and system scope of the pathway;
* the pathway's stated time window;
* the timing represented by the authoritative `TransitionPathway`; and
* the accelerated operational net-zero transition window.

A technically valid contribution that cannot be delivered within the relevant
transition window is recorded with its relevant timing constraint rather than
as a fully available contribution.

Similarly, a pathway that produces useful capacity but depends on an unresolved
reliability replacement, infrastructure dependency, or synchronization
condition retains that dependency in its contribution result.

The contribution evaluation records the reliability, deliverability, timing, and
system conditions attached to the contribution. It does not determine whether
the pathway can achieve material scale. Scale, scale-up constraints, stale
success, and other scale-dependent effects are evaluated separately by the
`ScaleDiagnosticEvaluator` in Section 12.

### 11.5 Limited or Unresolved Contribution

A pathway may complete contribution evaluation without demonstrating an
unconditional or fully resolved contribution.

A completed `NetOverallSystemContribution` may therefore record one or more
limiting or unresolved conditions, including contribution that is:

* local rather than system-wide;
* limited in magnitude or scope;
* indirect;
* conditional on identified dependencies;
* time-limited; or
* unresolved because available evidence or relationships within the broader
  net-zero transition do not support a stronger conclusion.

A limited or unresolved contribution is not an evaluator-integrity failure.

Where the evaluator has successfully completed its work, the result preserves
the supported finding and the conditions that limit it. Later stages shall use
that information when evaluating scale, constructing a candidate or a prospective
candidate `TransitionPathway`, evaluating net overall system risk, and
performing the Final Charter Evaluation.

An evaluator-integrity failure is distinct from an unresolved contribution. If
the evaluator cannot produce a structurally valid contribution result, the
current evaluation does not proceed.

---

## 12. Scale Diagnostic

Scale diagnosis evaluates whether the pathway's supported contribution can
expand, replicate, deploy, or otherwise operate at a materially relevant scale
within the required transition window. It also evaluates whether the conditions
required for that scale are available, constrained, delayed, unresolved, or
likely to change the pathway's contribution as scale increases.

The `ScaleDiagnosticEvaluator` consumes the completed
`NetOverallSystemContribution` together with the pathway and system information
required to evaluate scale. It produces one immutable `ScaleDiagnosticResult`.

Scale diagnosis is necessary because a pathway may make a supported net overall
system contribution at its evaluated scope while remaining unable to reach a
scale sufficient to materially affect the broader net-zero transition.

Scale diagnosis does not replace the contribution evaluation established in
Section 11.

The scale result is carried forward into construction of the candidate or
prospective candidate `TransitionPathway`, net overall system risk evaluation,
Final Charter Evaluation, and subsequent pathway resolution.

### 12.1 ScaleDiagnosticEvaluator

The `ScaleDiagnosticEvaluator` evaluates the pathway's ability to realize its
supported contribution at a materially relevant scale.

Its inputs include:

* the completed `NetOverallSystemContribution`;
* a reference to the evaluated `ProductPathway`;
* a reference to the authoritative `TransitionPathway`;
* relevant transition and system context;
* material assumptions and uncertainties;
* evidence and provenance required to support the scale evaluation; and
* `user_id` and `pathway_id` attribution.

The evaluator determines, as supported by the completed `NetOverallSystemContribution`
record, whether scale depends on conditions such as:

* production, construction, conversion, or deployment capacity;
* feedstock, energy, material, water, or other input availability;
* infrastructure, interconnection, transmission, transport, storage, or other
  delivery capacity;
* finance, bankability, public support, or capital availability;
* workforce, organizational, contractor, or specialist capacity;
* permitting, siting, authorization, or other execution requirements;
* supply-chain capacity and critical component availability;
* geographic replication, access, or expansion across regions or jurisdictions;
* expansion across sectors, system functions, or other relevant operating
  contexts;
* customer, market, or offtake adoption where required for pathway execution;
* learning-curve progression, cumulative deployment, manufacturing expansion,
  or cost reduction required for further scale;
* the rate at which capacity, deployment, replication, or adoption can increase;
* the duration for which the required level of scale can be sustained;
* operation across differing temporal, geographic, or jurisdictional conditions;
* dependencies on other transition pathways or system functions;
* timing and sequencing constraints;
* competition with other transition requirements for scarce resources;
* unresolved conditions identified in upstream evaluation; or
* other material increases in or constraints on expansion, replication, throughput,
  capacity, coverage, or deployment.

The evaluator preserves the relationship between each scale finding and the
contribution it affects. Where the available evidence does not establish whether a
constraint or bottleneck can be resolved within the required transition window,
that condition remains unresolved and is recorded in the `ScaleDiagnosticResult`.

The evaluator does not assume that a technically feasible pathway can scale
merely because additional deployment is physically conceivable. Scale findings
must be supported by the completed `NetOverallSystemContribution`, relevant
transition relationships and system context, and available evidence.

The evaluator produces one new immutable `ScaleDiagnosticResult`.

### 12.2 ScaleDiagnosticResult

All scale findings produced by the `ScaleDiagnosticEvaluator` are recorded in the
immutable `ScaleDiagnosticResult`.

The result contains or references, as applicable:

* the evaluated `ProductPathway`;
* the `NetOverallSystemContribution` being evaluated for scale;
* a reference to the authoritative `TransitionPathway`;
* the material-scale and scaling-condition findings;
* the transition functions and contributions to which those findings apply;
* the geographic and system scope of the scale findings;
* relevant quantity, capacity, throughput, coverage, replication, or deployment
  findings;
* scale-rate, duration, learning-curve progression, or other scale-progression findings;
* timing and sequencing conditions;
* identified scale constraints and bottlenecks;
* identified scale increases, unblocks, constraint mitigations, workarounds, or
  resolution conditions;
* scale-dependent effects;
* unresolved scale conditions;
* material assumptions and uncertainties;
* supporting evidence and provenance references;
* evaluator and rule-set versions; and
* `user_id` and `pathway_id` attribution.

The result preserves the distinction between demonstrated scale, supported
prospective scale, conditional scale, constrained scale, and unresolved scale,
together with the conditions associated with each finding.

An evaluator-integrity failure is distinct from an adverse or unresolved scale
finding. If the evaluator cannot produce a structurally valid
`ScaleDiagnosticResult`, the current evaluation does not proceed.

`ScaleDiagnosticResult` does not construct the candidate or prospective
candidate `TransitionPathway`, determine net overall system risk, perform the
Final Charter Evaluation, assign a bound state, or authorize commitment or
deployment. Those operations occur in later stages.

### 12.3 Material Scale Contribution

Material scale is the scale at which a pathway's evaluated contribution becomes
large enough, broad enough, or sufficiently replicated to materially affect the
transition function or broader net-zero transition.

Material scale is pathway- and function-dependent and is not represented by one
universal quantity or threshold. For one pathway, material scale may depend
primarily on deployed physical capacity. For another, it may depend on
geographic reach, throughput, workforce availability, infrastructure coverage,
financing capacity, fossil displacement, replication across many actors, or
another function-specific measure.

The `ScaleDiagnosticEvaluator` evaluates material scale relative to:

* the contribution recorded in `NetOverallSystemContribution`;
* the transition function or functions affected by that contribution;
* the geographic and system scope in which the contribution operates;
* the quantity, capacity, throughput, coverage, or replication required for the
  contribution to become materially relevant;
* the timing required by the authoritative `TransitionPathway`;
* the accelerated operational net-zero transition window; and
* the dependencies and conditions required to reach that scale.

A contribution may be material within a local or bounded system without being
material to the broader global transition. The scale result preserves that
scope and does not treat local, regional, sectoral, and global scale as
interchangeable.

### 12.4 Scale Constraints and Bottlenecks

A supported contribution may encounter one or more constraints as it expands.
Some constraints may cause bottlenecks to scaling when their limiting effects
materially change the rate, throughput, timing, geographic reach, or
achievable scale of the contribution.

Scale constraints may affect:

* the maximum scale that can be reached;
* the rate at which scale can increase;
* the locations in which scale can occur;
* the sequence in which deployment can proceed;
* the duration for which the contribution can be sustained;
* the resources required for further expansion;
* the transition functions that can be served at increased scale;
* the functional performance or contribution that can be sustained as scale
  increases; or
* another material dimension of pathway scale.

A scale constraint may be pathway-specific or may arise from a shared transition
condition affecting multiple pathways. A shared constraint may therefore create
a bottleneck across more than one pathway or transition function.

Where a material scale constraint or bottleneck is identified, the
`ScaleDiagnosticResult` records the underlying constraint, any resulting
bottleneck or other constrained pathway behavior, its relationship to the
contribution, the evidence supporting the finding, and any identified
conditions, mitigations, workarounds, or resolutions that may reduce or remove it.

### 12.5 Scale-Dependent Effects

Scaling a pathway may change the net-zero transition system effects recorded
at smaller scale.

The `ScaleDiagnosticEvaluator` therefore evaluates whether increasing pathway
scale materially changes the conditions underlying the
`NetOverallSystemContribution`.

Scale-dependent effects may include:

* changes in energy, material, water, land, infrastructure, or other resource
  demand;
* emergence, reduction, or worsening of infrastructure or supply-chain
  constraints;
* changes in reliability, adequacy, or delivery requirements;
* changes in competition for or availability of resources shared with other
  transition pathways;
* changes in fossil displacement, substitution, or fallback behavior;
* changes in emissions or other material system burdens;
* changes in biosphere effects or ecological pressures;
* changes in workforce, permitting, finance, or execution requirements;
* changes in timing or synchronization with other transition activities;
* threshold conditions at which the pathway's scaling behavior, constraints,
  or rate of expansion materially changes; or
* other effects that become material only at increased scale.

Where scaling crosses a material threshold that changes the pathway's subsequent
ability to expand, the `ScaleDiagnosticResult` records the threshold and the
resulting change in scaling conditions.

Where scale materially changes the contribution itself, the
`ScaleDiagnosticResult` records the affected contribution and the scale
conditions.

### 12.6 Limited or Local Contribution

A pathway may make a supported contribution that contribution reaching material
scale beyond its local or otherwise bounded scope.

The `ScaleDiagnosticEvaluator` records when the contribution remains limited by
scope, geography, capacity, replication, duration, transition function, or
another material scaling dimension. A contribution may therefore be meaningful
within a local, regional, sectoral, institutional, or otherwise bounded context
while remaining insufficient to materially affect the broader net-zero
transition. A contribution may also remain intentionally distributed across many
small or local instances where persistence or replication of those instances is
itself part of the pathway's material-scale contribution.

A limited or local contribution supported by the available evidence is a valid
scale finding. The `ScaleDiagnosticResult` preserves:

* the scope within which the contribution is demonstrated or supported;
* the scale dimensions that remain limited;
* the transition functions affected within that scope;
* any conditions required for broader replication or expansion;
* any constraints or bottlenecks preventing broader scale;
* any scale-dependent effects associated with expansion beyond the supported
  scope; and
* unresolved conditions affecting whether broader scale can be achieved.

Where broader scale remains possible but depends on unresolved conditions, the
evaluator records the contribution as limited or local together with those
conditions rather than treating broader scale as established.

### 12.7 Stale Success

A pathway may demonstrate successful deployment, operation, or contribution at
one point in time while the conditions supporting that success later change.

Scale diagnosis therefore distinguishes demonstrated historical success from
current or future scale. A scale finding contains stale success when the
conditions that enabled prior success no longer match the conditions under
which the pathway must now scale, and those changes materially affect whether
that success can be reproduced or expanded.

A prior successful deployment does not by itself establish that the pathway can
be reproduced or expanded at the required scale and time. Relevant inputs,
infrastructure, finance, workforce, permitting, supply chains, transition
relationships, or other conditions may have changed.

Historical evidence remains preserved as evidence.

---

## 13. Candidate TransitionPathway and Its Construction

After contribution and scale evaluation complete, the evaluated pathway and its
supported effects are compiled into one of two transition representations. In
the global context, the result is a complete candidate mapping of the global
net-zero transition. That candidate may be constructed as an entirely new
net-zero transition pathway or by applying the evaluated pathway and its
supported effects to the existing authoritative `TransitionPathway`. In the
user-submitted context, the result is a prospective mapping of how the
existing net-zero transition would change if the evaluated pathway's supported
effects were incorporated. In this section, `net-zero transition` and
`net-zero transition state` may be abbreviated as `transition` and
`transition state`.

This intermediate representation allows ClimateSOS to evaluate the combined
transition state.

These two transition representations are produced by the
`TransitionPathwayCompiler`:

* a candidate `TransitionPathway` in the global evaluation context; or
* a prospective candidate `TransitionPathway` in the user-submitted context.

Both transition mappings are constructed from the evaluated pathway, its
supported contribution and scale findings, and the authoritative
`TransitionPathway` used as the reference state.

The constructed pathway proceeds to `NetOverallSystemRiskEvaluator`. Candidate
transition construction does not make the resulting pathway authoritative.

### 13.1 TransitionPathwayCompiler

The `TransitionPathwayCompiler` compiles the evaluated pathway and its supported
system effects into a candidate transition representation suitable for
downstream stages including net overall system risk evaluation, final pathway
assembly, Final Charter Evaluation, and, in the global context, transition
validation.

The compiler uses the authoritative `TransitionPathway` as the reference state
and incorporates the supported changes established through pathway,
contribution, and scale evaluation. These changes may include additions,
replacements, displacement, retirement, changed dependencies, changed timing or
sequencing, changed capacity or scale, enabling effects, constrained effects, or
other represented changes to the broader net-zero transition.

The compiler preserves the distinction between:

* transition state already represented by the authoritative
  `TransitionPathway`;
* changes supported by the evaluated pathway;
* conditions or dependencies attached to those changes;
* conflicts or incompatibilities between supported changes and existing
  transition state;
* limited, constrained, conditional, or unresolved findings;
* evaluated findings that do not produce a transition-state change; and
* transition relationships that remain unchanged.

The compiler does not convert an unresolved, conditional, constrained, local,
or otherwise limited finding into an unconditional transition change. The
candidate representation preserves those conditions where they materially
affect the compiled transition state.

The compiler produces a new immutable candidate or prospective candidate
`TransitionPathway`.

A compiler-integrity failure occurs when the compiler cannot produce a
structurally valid candidate representation while preserving the required
identity, transition relationships, evaluated findings, and provenance. The
current evaluation does not proceed when candidate construction fails.

### 13.2 Candidate and Prospective Candidate TransitionPathways

A candidate or prospective candidate `TransitionPathway` represents the
transition state produced from the evaluated pathway and its supported
effects. In the global context, the candidate may represent an entirely new
global transition pathway or incorporate supported changes into the
authoritative `TransitionPathway`. In the user-submitted context, the
prospective candidate represents the effects of the evaluated pathway
incorporated into the authoritative `TransitionPathway`.

The two forms serve different evaluation contexts.

A **candidate `TransitionPathway`** is produced in the global context. It
represents a proposed new global transition state that may later become the
authoritative `TransitionPathway` if it completes all remaining evaluation,
Charter, binding, validation, and commitment stages.

A **prospective candidate `TransitionPathway`** is produced in the
user-submitted context. It represents the transition state that would result
from incorporation of the evaluated user pathway, but it cannot replace,
modify, or become the authoritative global `TransitionPathway` through the
user-submitted evaluation flow.

Both forms allow downstream evaluation to examine the consequences of the
pathway within a combined transition state.

Neither candidate form is authoritative merely because construction completes.

### 13.3 Candidate Construction Inputs

The `TransitionPathwayCompiler` begins from the authoritative
`TransitionPathway` used during evaluation and the completed evaluation state
for the pathway being compiled.

Its inputs include:

* the `ProductPathway` under evaluation;
* the completed `NetOverallSystemContribution`;
* the completed `ScaleDiagnosticResult`;
* a reference to the authoritative `TransitionPathway`;
* applicable transition and system context;
* conditions, dependencies, assumptions, and uncertainties required to
  preserve the evaluated findings;
* evidence and provenance references required to trace the compiled changes;
  and
* `user_id` and `pathway_id` attribution.

The compiler uses the completed contribution and scale findings to determine
which evaluated pathway effects are represented in the candidate transition
state and the conditions under which those effects apply.

Candidate construction preserves references to the evaluation state from which
each material transition change was derived.

### 13.4 Global Candidate TransitionPathway

In the global evaluation context, the `TransitionPathwayCompiler` produces a
candidate `TransitionPathway`.

The compiler uses the authoritative global `TransitionPathway` as the
reference state and constructs a complete candidate mapping of the global
net-zero transition. The candidate may represent an entirely new transition
pathway, a limited change to the existing transition, or a prospective
replacement of a larger portion of the represented global pathway. The
authoritative reference `TransitionPathway` remains unchanged during
construction and subsequent evaluation.

A completed global candidate preserves:

* a reference to the authoritative `TransitionPathway` used as the reference
  state;
* the evaluated changes incorporated into the candidate;
* transition functions, relationships, dependencies, timing, and sequencing
  affected by those changes;
* contribution and scale conditions attached to the incorporated effects;
* unchanged transition state required to preserve the surrounding global
  pathway;
* unresolved or constrained conditions that remain material to the candidate;
* evidence and provenance supporting the incorporated changes; and
* the identity and version information required to distinguish the candidate
  from both its source pathway and the authoritative reference state.

The candidate is complete when the compiler can represent the supported pathway
effects and their material conditions without corrupting or losing the
transition state required for downstream evaluation.

Candidate construction fails when the compiler cannot produce a structurally
valid transition representation, cannot preserve required attribution or
provenance, or cannot maintain the required relationship between the candidate
and the authoritative reference `TransitionPathway`.

A completed global candidate proceeds to `NetOverallSystemRiskEvaluator`.

It remains non-authoritative until the later global flow permits validation and
atomic immutable commitment.

### 13.5 User-Submitted Prospective Candidate TransitionPathway

In the user-submitted evaluation context, the `TransitionPathwayCompiler`
produces a prospective candidate `TransitionPathway`.

The compiler begins with the current authoritative `TransitionPathway` and
constructs a new prospective transition representation containing the supported
effects of the evaluated user-submitted pathway.

The prospective candidate allows ClimateSOS to evaluate what the broader
transition would look like if the pathway's supported effects occurred while
leaving the authoritative global `TransitionPathway` unchanged.

A completed prospective candidate preserves:

* a reference to the authoritative `TransitionPathway` used as the reference
  state for construction;
* the evaluated user-submitted pathway;
* the supported changes represented in the prospective transition state;
* transition functions, relationships, dependencies, timing, and sequencing
  affected by those changes;
* contribution and scale conditions attached to the represented effects;
* unchanged transition state required to preserve the surrounding global
  pathway;
* unresolved or constrained conditions that remain material to the prospective
  candidate;
* evidence and provenance supporting the represented changes; and
* `user_id` and `pathway_id` attribution.

The prospective candidate is complete when the compiler can represent the
supported pathway effects and their material conditions without modifying the
authoritative global transition state.

Construction fails when the compiler cannot produce a structurally valid
prospective candidate, cannot preserve required attribution or provenance, or
cannot maintain separation between the prospective candidate and the
authoritative `TransitionPathway`.

A completed prospective candidate proceeds to
`NetOverallSystemRiskEvaluator`.

A completed prospective candidate and its subsequent evaluation remain
user-evaluation artifacts outside the privileged global commitment path.

### 13.6 Candidate Immutability, Identity, and Provenance

Each candidate or prospective candidate `TransitionPathway` is immutable once
constructed.

The candidate preserves the identity of the evaluated pathway, the
authoritative `TransitionPathway` used as its reference state, and the
evaluation results from which its material changes were derived.

Candidate construction must preserve sufficient provenance to determine:

* which transition state existed before compilation;
* which evaluated pathway introduced each material change;
* which contribution and scale findings support that change;
* which conditions, dependencies, assumptions, or uncertainties remain
  attached to it;
* which transition relationships were changed and which were preserved;
* which evidence supports the represented change; and
* which evaluator, compiler, model, or rule-set versions produced the
  applicable evaluation and construction state.

A candidate does not overwrite or mutate the authoritative
`TransitionPathway`. Later evaluation stages create new immutable results that
reference the candidate rather than modifying it.

For global evaluation, a new authoritative `TransitionPathway` may be
established only through the privileged validation and atomic commitment path.
For user-submitted evaluation, the prospective candidate remains separate from
the authoritative global pathway for the duration of the evaluation.

---

## 14. Net Overall System Risk Evaluation

After candidate transition construction, the `NetOverallSystemRiskEvaluator`
evaluates how the candidate or prospective candidate `TransitionPathway` changes
the risk profile of the accelerated net-zero transition.

The evaluator compares the candidate transition state with the authoritative
`TransitionPathway` used as its reference state. It evaluates whether the
candidate introduces, increases, reduces, transfers, resolves, or leaves
unresolved systemic risks that may materially affect the transition.

Risk evaluation includes analysis of transition timing, synchronization,
bottlenecks, failure modes, fossil persistence and fallback, infrastructure
and delivery constraints, and other conditions that may affect whether the
combined transition can reach operational net zero within the required
transition window.

The evaluator applies transition-risk logic developed through Appendices A–C
of the *2030s Net Zero Playbook*, together with the candidate transition
state, relevant system context, and available evidence.

The evaluator produces one new immutable `NetOverallSystemRiskResult`.

### 14.1 Evaluation Purpose and Boundary

The `NetOverallSystemRiskEvaluator` evaluates risks, including systemic risks,
created or changed by the candidate transition as a whole.

Its primary input is the candidate or prospective candidate
`TransitionPathway`. The evaluator also uses:

* a reference to the authoritative `TransitionPathway` against which the
  candidate was constructed;
* relevant transition and system context;
* contribution, scale, dependency, constraint, and unresolved-condition
  findings referenced by the candidate;
* evidence and provenance required to support the risk evaluation;
* material assumptions and uncertainties; and
* `user_id` and `pathway_id` attribution.

The evaluator examines the candidate as an integrated transition state,
including interactions among pathways, dependencies, and shared
transition functions. A change that is beneficial or low-risk in
isolation may create, shift, amplify, or reduce systemic risk elsewhere
in the transition.

Risk evaluation does not determine Charter validity, assign a bound state,
validate a global `TransitionPathway`, or authorize commitment or deployment.

A supported adverse or unresolved risk finding is a completed evaluation
finding. It is distinct from evaluator-integrity failure.

### 14.2 Candidate-to-Reference Risk Comparison

Net overall system risk is evaluated relative to the authoritative
`TransitionPathway`.

The evaluator compares the candidate transition state with the reference state
to identify material changes in transition risk. The comparison preserves the
distinction between:

* risks already present in the authoritative transition;
* risks introduced by the candidate;
* existing risks increased by the candidate;
* existing risks reduced or resolved by the candidate;
* risks transferred between transition functions, locations, actors, resources,
  or time periods;
* risks whose character or consequences change because of the candidate;
* risks that remain materially unchanged; and
* risks that cannot be resolved from the available evidence.

The evaluator preserves the transition relationships through which a given
risk arises or propagates.

A reduction in one risk does not offset a materially comparable or greater
risk created or transferred elsewhere in the transition. Any such transferred
or newly created risk remains explicit in the result.

### 14.3 Appendix A–C Risk Logic

The risk evaluation incorporates the transition-risk, bottleneck, timeline,
and pitfall logic used by ClimateSOS, together with the additional failure-mode
logic developed through Appendices A–C of the *2030s Net Zero Playbook*.

This logic is applied to the candidate transition state rather than treating
the Appendices as a fixed checklist of pathway labels.

The evaluator examines whether the candidate changes conditions associated
with:

* delivery of required clean-energy, infrastructure, industrial, workforce,
  finance, and other transition functions;
* synchronization between dependent transition activities;
* fossil retirement, displacement, persistence, and fallback;
* reliability and adequacy replacement;
* infrastructure, interconnection, transmission, storage, transport, and other
  delivery requirements;
* finance, bankability, public support, and capital availability;
* workforce and execution capacity;
* supply-chain and material availability;
* permitting, authorization, and institutional execution;
* timing and sequencing of dependent activities;
* transition bottlenecks and shared constraints;
* systemic risks arising from interactions among transition functions,
  dependencies, constraints, and pathway effects;
* propagation, amplification, or cascading of risk across the transition;
* biosphere and climate-system risks affected by the transition, including
  feedbacks, threshold behavior, and tipping-point risks;
* compound or interacting biosphere and transition risks;
* implementation pitfalls and failure modes; and
* other represented conditions that may materially alter transition success,
  failure, or systemic risk.

The evaluator preserves new risk conditions revealed by the candidate even
where they are not represented by an existing Appendix category.

### 14.4 Net-Zero Timeline Effects

Net-zero transition risk, abbreviated in this section as transition
risk, includes whether the candidate changes the ability of the
combined transition to complete required functions within the
accelerated operational net-zero window.

The evaluator determines whether candidate changes:

* advance or delay required transition activity;
* change the sequence in which dependent functions must occur;
* create or remove timing dependencies;
* increase or reduce schedule margin for critical transition functions;
* cause a required function to become unavailable when needed;
* extend fossil operation or fallback beyond its required retirement window;
* accelerate or delay infrastructure, workforce, finance, supply-chain, or
  other enabling capacity;
* change the duration of a material transition bottleneck; or
* otherwise change the probability that required transition functions can be
  completed in time.

A timing effect remains associated with the transition function, dependency,
constraint, or risk that produces it.

The evaluator does not treat eventual technical feasibility as equivalent to
availability within the required transition window.

### 14.5 Bottlenecks, Pitfalls, and Failure Modes

The evaluator identifies candidate changes that create, worsen, relieve,
remove, shift, or expose transition bottlenecks, pitfalls, and failure modes.

A bottleneck emerges where one or more constraints materially govern the rate,
throughput, timing, geographic reach, or achievable scale of a required
transition function.

A pitfall or failure mode arises where the candidate creates conditions
under which an otherwise supported transition pathway can fail to produce its
required system effect.

The evaluator examines the candidate transition state for conditions that
create, worsen, relieve, remove, shift, or expose transition bottlenecks,
pitfalls, failure modes, and other emergent system risks. It evaluates how
those conditions affect required transition functions, biosphere and
climate-system stability, and whether their effects propagate through
dependencies, shared constraints, feedbacks, or threshold behavior.

Relevant findings may include:

* creation or removal of shared transition bottlenecks;
* concentration of dependency on scarce infrastructure, materials, finance,
  workforce, suppliers, institutions, or other resources;
* loss of redundancy or creation of single points of transition failure;
* sequencing failures between dependent transition functions;
* insufficient replacement of reliability, adequacy, or other required system
  functions;
* fossil fallback or persistence created by incomplete replacement or closure;
* delay or failure propagated through dependent pathways;
* scale-dependent constraints or effects that become material in the combined
  transition state;
* interactions between individually viable pathways that create an aggregate
  constraint or failure mode;
* emergence or intensification of climate or biosphere tipping-point risks;
* threshold behavior in which incremental transition changes produce nonlinear
  system effects;
* reinforcing feedbacks that amplify climate, ecological, or transition risk;
* compound interactions between transition failures and biosphere degradation;
* cascading effects in which one material failure or threshold crossing alters
  multiple transition or biosphere functions; or
* other conditions capable of materially preventing or delaying a required
  transition function.

### 14.6 Risk State Classification

Risk classification preserves scope, timing, affected transition functions,
dependencies, and material conditions.

A risk may be:

* **new** when the candidate introduces a material risk not present in the
  authoritative reference state;
* **increased** when the candidate materially worsens the likelihood,
  consequence, scope, duration, or propagation of an existing risk;
* **reduced** when the candidate materially lowers an existing risk;
* **resolved** when the candidate removes the material condition producing an
  existing risk;
* **transferred** when the candidate reduces or removes risk in one part of the
  transition while creating or increasing related risk elsewhere; or
* **unresolved** when available evidence or transition relationships do not
  support a stronger risk determination.

A transferred risk remains explicit even where the candidate produces a net
benefit elsewhere in the transition.

An unresolved risk is not an evaluator-integrity failure.

### 14.7 Charter-Style Risk Checks

The `NetOverallSystemRiskEvaluator` may perform Charter-style checks where a
Charter safeguard or guardrail provides information necessary to identify or
characterize a transition risk.

These checks are risk-analysis operations performed within the system-risk
evaluation. They may identify risks involving rights, accountability,
scientific integrity, biosphere integrity, planetary boundaries, equitable
durability, or other Charter-governed conditions where those conditions
affect the transition risk being evaluated.

The Foundational Charter remains the authoritative source of Charter validity.
Charter-style risk checks performed by the `NetOverallSystemRiskEvaluator`
provide risk findings only.

A Charter-style risk check does not constitute a Charter evaluation and does
not produce or modify a Charter result.

The checks do not replace, revise, override, or supersede the
`InitialCharterResult` or `IntegratedCharterResult`, and they do not substitute
for the subsequent Final Charter Evaluation.

Where a risk finding and a Charter finding address overlapping subject matter,
both remain preserved with their separate evaluator ownership and purpose.

### 14.8 Relationship to the Final Charter Result

`NetOverallSystemRiskResult` precedes Final Charter Evaluation and is preserved
through `FinalPathwayAssembly` as part of the completed pathway evaluation state.

Risk findings do not determine Charter validity. Where a system-risk finding
and a Final Charter finding concern overlapping conditions, both findings remain
preserved with their distinct evaluator ownership, purpose, evidence, and
provenance.

The subsequent `FinalCharterResult` does not revise or replace the
`NetOverallSystemRiskResult`.

### 14.9 NetOverallSystemRiskResult

All completed system risk findings are recorded in one immutable
`NetOverallSystemRiskResult`. The result preserves the causes, affected
transition functions, propagation relationships, and supporting evidence
associated with each material finding, either directly or by reference.

The result contains or references, as applicable:

* the candidate or prospective candidate `TransitionPathway` evaluated for
  risk;
* a reference to the authoritative `TransitionPathway` used for comparison;
* the evaluated risk findings;
* the transition functions and relationships to which those findings apply;
* new, increased, reduced, resolved, transferred, and unresolved risks;
* timeline and sequencing effects;
* identified bottlenecks, pitfalls, and failure modes;
* fossil fallback and persistence risks;
* infrastructure, finance, workforce, adequacy, delivery, supply-chain, and
  other material transition constraints;
* risk propagation relationships;
* Charter-style risk findings;
* material assumptions and uncertainties;
* supporting evidence and provenance references;
* evaluator and rule-set versions; and
* `user_id` and `pathway_id` attribution.

The result preserves the distinction between an adverse risk finding, an
unresolved risk finding, and evaluator-integrity failure.

Where the evaluator completes successfully, adverse and unresolved risks remain
part of the completed result and proceed to `FinalPathwayAssembly`.

If the evaluator cannot produce a structurally valid
`NetOverallSystemRiskResult`, the current evaluation does not proceed.

`NetOverallSystemRiskResult` does not perform final pathway assembly, determine
Charter validity, assign a bound state, validate the global transition, or
authorize commitment or deployment.

---

## 15. Final Pathway Assembly

After net overall system risk evaluation completes, `FinalPathwayAssembly`
constructs the completed pathway-evaluation artifact, `FinalPathwayResult`,
used by Final Charter Evaluation and the later binding flow.

The assembly combines the candidate or prospective candidate
`TransitionPathway` with the completed evaluation state and preserves the
relationships among the pathway, its primary evaluation results, and its
evaluation lineage in one immutable `FinalPathwayResult`.

`FinalPathwayAssembly` does not perform substantive evaluation. It assembles
and verifies the completed evaluation state without revising, resolving, or
replacing findings produced by their owning evaluators.

### 15.1 FinalPathwayAssembly

`FinalPathwayAssembly` receives the completed candidate transition and its
associated evaluation state after `NetOverallSystemRiskEvaluator` completes.

Its responsibility is to construct a coherent final pathway-evaluation
representation in which the evaluated pathway, reference and candidate
transition states, completed system-risk result, and upstream evaluation
lineage remain identifiable and traceable.

The assembler preserves evaluator ownership of each finding. A finding produced
by an upstream evaluator remains attributable to that evaluator and is not
reinterpreted as an assembly finding.

The assembler shall verify structural consistency, identity, attribution,
provenance, and required relationships among its inputs to construct the
result. Structural verification does not constitute re-evaluation of the
pathway or its findings.

### 15.2 Assembly Inputs

`FinalPathwayAssembly` uses the completed evaluation state available at the end
of net overall system risk evaluation.

Its primary assembly inputs include:

* the `ProductPathway` under evaluation;
* a reference to the authoritative `TransitionPathway` used during evaluation;
* the candidate or prospective candidate `TransitionPathway`;
* the completed `NetOverallSystemRiskResult`; and
* `user_id` and `pathway_id` attribution.

The assembler also receives the completed upstream evaluation artifacts required
to construct and validate the `evaluation_trace`, including:

* the `InitialCharterResult`;
* the `PathwayEngineResult`;
* the `IntegratedCharterResult`;
* the `NetOverallSystemContribution`; and
* the `ScaleDiagnosticResult`.

Material conditions, dependencies, assumptions, uncertainties, unresolved
findings, evidence, and provenance remain associated with the evaluator results
that produced them. `FinalPathwayAssembly` preserves those relationships rather
than copying their contents into a new assembly-owned representation.

Assembly does not convert conditional, constrained, adverse, unresolved, or
limited findings into resolved findings.

### 15.3 Evaluation Trace

The `evaluation_trace` is an internal structure that preserves immutable
artifact references to completed upstream evaluation results. It contains
results required for provenance or downstream inspection that are not exposed
as semantically primary references on `FinalPathwayResult`.

For maintainability and extensibility, `FinalPathwayResult` separates referenced
state into two levels.

Semantically primary references are exposed directly on `FinalPathwayResult`.
These include the `ProductPathway`, the authoritative `TransitionPathway`, the
candidate or prospective candidate `TransitionPathway`, and the completed
`NetOverallSystemRiskResult`.

Completed upstream evaluation artifacts that remain necessary for provenance,
inspection, or downstream evaluation are preserved through the
`evaluation_trace`. These include:

* the `InitialCharterResult`;
* the `PathwayEngineResult`;
* the `IntegratedCharterResult`;
* the `NetOverallSystemContribution`; and
* the `ScaleDiagnosticResult`.

An artifact is exposed as a semantically primary reference when it forms part of
the direct identity or immediate downstream contract of `FinalPathwayResult`.
Other completed upstream evaluation artifacts remain available through the
`evaluation_trace`.

The `evaluation_trace` does not duplicate referenced artifact contents. Each
reference preserves sufficient artifact identity, type, version, attribution,
and provenance to validate the referenced artifact and its relationship to the
evaluation being assembled.

Future evaluator results may be added to the `evaluation_trace` without
requiring changes to the primary structural contract of `FinalPathwayResult`
unless that result becomes semantically primary to the assembled pathway state.

### 15.4 FinalPathwayResult

`FinalPathwayResult` is the preliminary end product of ProductPathway
evaluation and final pathway assembly. It represents the completed
pathway-evaluation state available before Final Charter Evaluation.

`FinalPathwayAssembly` produces one immutable `FinalPathwayResult`.

The result exposes semantically primary references to:

* the `ProductPathway` under evaluation;
* the authoritative `TransitionPathway` used as the evaluation reference;
* the candidate or prospective candidate `TransitionPathway`;
* the completed `NetOverallSystemRiskResult`; and
* `user_id` and `pathway_id` attribution.

The result also contains the `evaluation_trace`, which preserves immutable
artifact references to completed upstream evaluation results that remain
necessary for provenance, inspection, or downstream evaluation.

Material transition relationships, contribution, scale, Charter, and risk
findings, unresolved or constrained conditions, assumptions, uncertainties,
evidence, provenance, and applicable evaluator, compiler, model, and rule-set
versions remain associated with their owning artifacts and are reachable through
the primary references or `evaluation_trace`.

It does not determine final Charter validity, assign a bound state, validate or
commit a global `TransitionPathway`, or authorize deployment.

### 15.5 Preservation of Prior Evaluation State

Final pathway assembly preserves the completed evaluation lineage represented
by `FinalPathwayResult`.

The assembler does not overwrite upstream result objects, duplicate their
contents, or collapse findings from different evaluators into an
indistinguishable aggregate state.

Where multiple findings concern the same transition condition,
`FinalPathwayResult` preserves their separate evaluator ownership, purpose,
evidence, provenance, and relationships to the evaluated transition state.

Semantically primary artifacts remain directly referenced. Other completed
upstream evaluation artifacts remain available through the `evaluation_trace`.

A later evaluation stage creates a new result that references
`FinalPathwayResult`; it does not modify the assembled result.

### 15.6 Assembly Integrity and Failure

Final pathway assembly completes only when it can construct a structurally valid
`FinalPathwayResult` and preserve the required identity, attribution,
relationships, findings, and provenance.

`FinalPathwayAssembly` shall validate the semantically primary references and
each artifact reference included in the `evaluation_trace`.

Assembly integrity fails when required evaluation state or an artifact reference
is missing, malformed, inconsistently attributed, incorrectly typed, or cannot
be validated as part of the evaluation being assembled.

An adverse, constrained, conditional, limited, or unresolved upstream finding
is not an assembly-integrity failure when the finding is part of a valid
completed result.

If `FinalPathwayAssembly` cannot construct a valid `FinalPathwayResult`, the
current evaluation does not proceed to Final Charter Evaluation.

A completed `FinalPathwayResult` proceeds unchanged to
`CharterEvaluator — FINAL`.

---

## 16. Final Charter Evaluation

After `FinalPathwayAssembly` completes, the `CharterEvaluator` performs the
Final Charter Evaluation using the completed immutable `FinalPathwayResult`.

The Final Charter Evaluation is the third Charter evaluation in the Product
Pathway Evaluation Flow. The Initial Charter Evaluation evaluates the pathway
before pathway assembly and downstream evaluation. The Integrated Charter
Evaluation reevaluates the pathway after `PathwayEvaluationEngine` has produced
the completed `PathwayEngineResult`. The Final Charter Evaluation occurs after
net overall system contribution, scale evaluation, candidate transition
construction, net overall system risk evaluation, and final pathway assembly
have completed.

Each Charter evaluation evaluates the pathway using the information available at
that stage. The purpose of repeating Charter evaluation across the lifecycle is
to detect Charter-relevant conditions that become visible only after additional
pathway relationships, system effects, dependencies, scale effects, risks, or
other material state have been evaluated.

The Final Charter Evaluation therefore evaluates the pathway and assembled
candidate transition state against the ClimateSOS Foundational Charter using the
most complete evaluation state available before binding. This state includes
the completed system-risk evaluation and the upstream evaluation artifacts
preserved by the `evaluation_trace`.

As all Charter checks are required, the `CharterEvaluator` reruns every Charter
check using the information available at the Final Charter stage. Each check
executes independently. Findings from the Initial or Integrated Charter
Evaluations do not short-circuit, satisfy, or remove a Final Charter check.

The `CharterEvaluator` produces one immutable `FinalCharterResult`.

A completed Final Charter Evaluation records Charter validity using the most
complete evaluated pathway and transition state available before bound-state
determination and binding.

### 16.1 Final Evaluation Inputs

The `CharterEvaluator` receives the completed immutable `FinalPathwayResult`
and the Charter resources required to perform the Final Charter Evaluation.

The `FinalPathwayResult` provides direct access to:

* the `ProductPathway` under evaluation;
* the authoritative `TransitionPathway` used as the evaluation reference;
* the candidate or prospective candidate `TransitionPathway`;
* the completed `NetOverallSystemRiskResult`;
* the `evaluation_trace`; and
* `user_id` and `pathway_id` attribution.

Through the `evaluation_trace`, the evaluator also has access to:

* the `InitialCharterResult`;
* the `PathwayEngineResult`;
* the `IntegratedCharterResult`;
* the `NetOverallSystemContribution`; and
* the `ScaleDiagnosticResult`.

The Final Charter Evaluation also receives:

* the ClimateSOS Foundational Charter distributed with the ClimateSOS runtime;
* the complete set of Charter checks;
* the evaluator version and Charter rule-set version; and
* any runtime configuration required to perform the Final Charter Evaluation.

The evaluator shall validate the identity, attribution, required provenance
references, and relationships of the `FinalPathwayResult` and referenced
evaluation artifacts before using them in Charter evaluation. This validation
establishes structural consistency and traceability; it does not independently
establish the truth of the referenced provenance.

The `CharterEvaluator` runs every Charter check against the completed
`FinalPathwayResult` and the evaluation state available through its primary
references and `evaluation_trace`.

It does not add missing pathway facts, convert unresolved conditions into
established facts, or treat unsupported possible effects as established
conditions.

### 16.2 Final Charter Result

The `CharterEvaluator` produces one immutable `FinalCharterResult`.

The `FinalCharterResult` records the complete outcome of the Final Charter
Evaluation using the pathway, candidate transition, contribution, scale, system
risk, and other evaluation state available after `FinalPathwayAssembly`.

The `FinalCharterResult` contains or references, as applicable:

* the evaluated `FinalPathwayResult`;
* the associated `InitialCharterResult`;
* the associated `IntegratedCharterResult`;
* the result of every Charter check;
* findings, evidence references, and supporting provenance associated with each
  check;
* pathway, transition, contribution, scale, or system-risk findings supporting
  each check;
* unresolved or not-applicable conditions returned by completed checks, where
  permitted by the applicable Charter rule;
* any execution error associated with an individual check or with the Final
  Charter Evaluation;
* the evaluator version;
* the Charter rule-set version; and
* the resulting Final Charter status.

Every Charter check produces one explicit Final-stage result that remains
individually identifiable within `FinalCharterResult` and contributes to the
resulting Final Charter status according to the applicable Charter rule.

If a Charter check does not execute, does not complete, times out, does not
produce a valid result, or produces a result that is absent, null, malformed,
overwritten, or otherwise unavailable, the check is `MISSING`.

A `MISSING` check is an evaluator-integrity failure. The `FinalCharterResult`
is recorded as `ERROR`, and the current pathway evaluation does not proceed to
ordinary bound-state determination or binding until the execution error is
resolved.

`UNRESOLVED` and `NOT_APPLICABLE` remain distinct from `MISSING`. A successfully
executed check may return either state where permitted by the applicable Charter
rule.

A completed `FinalCharterResult` is immutable. Later stages reference it but do
not revise or replace it.

### 16.3 Relationship to Earlier Charter Results

The `InitialCharterResult`, `IntegratedCharterResult`, and `FinalCharterResult`
are separate immutable records produced by the `CharterEvaluator` at different
points in the Product Pathway Evaluation Flow.

The Initial Charter Evaluation evaluates the pathway before ProductAssembly and
pathway evaluation.

The Integrated Charter Evaluation evaluates the pathway after
`PathwayEvaluationEngine` has produced the completed `PathwayEngineResult`.

The Final Charter Evaluation evaluates the completed `FinalPathwayResult` after
contribution, scale, candidate construction, system-risk evaluation, and final
pathway assembly have completed.

The `CharterEvaluator` reruns every Charter check during the Final Charter
Evaluation. It does not update an earlier Charter result, reuse an earlier
individual check result as the current result, or treat successful completion
of an earlier Charter Evaluation as satisfaction of a Final Charter check.

A Charter finding may remain unchanged across evaluations or may change when
additional pathway state, transition relationships, scale effects, systemic
risks, biosphere or climate-system effects, evidence, or other material
information becomes available.

Where a Final Charter finding differs from an earlier Charter finding, the
`FinalCharterResult` preserves the material findings, evidence, and evaluation
state supporting the changed determination.

All three Charter results remain part of the immutable evaluation lineage.

### 16.4 Charter Authority and Non-Supersession

The ClimateSOS Foundational Charter is the authoritative source of Charter
validity throughout Product Pathway Evaluation.

No pathway evaluator, system-risk evaluator, assembler, compiler, binding
component, or other downstream component may replace, revise, weaken, or
supersede a Charter determination.

The `FinalCharterResult` is the current Charter evaluation for the assembled
pathway state at the Final Charter stage. It does not erase or modify the
`InitialCharterResult` or `IntegratedCharterResult`.

Likewise, the Final Charter Evaluation does not revise or replace findings owned
by other evaluators. Where a Charter finding overlaps with a contribution,
scale, system-risk, documentation, or other evaluation finding, each finding
remains preserved with its separate ownership, purpose, evidence, and
provenance.

A later stage may use the `FinalCharterResult` to determine whether ordinary
progression is permitted, but it does not reinterpret Charter validity.

### 16.5 Conditions Governing Further Progression

Final Charter Evaluation completes when every Charter check has executed and
the `CharterEvaluator` has produced a valid immutable `FinalCharterResult`.

A completed Final Charter Evaluation may contain adverse, failed, unresolved,
not-applicable, or other valid Charter findings. These findings remain part of
the completed result and are distinct from evaluator-integrity failure.

The `FinalCharterResult` shall preserve every Charter condition that constrains
or prevents further runtime progression.

A Charter condition must be positively established where the applicable Charter
rule requires positive validity. Absence of an identified violation, absence of
a STOP condition, or incomplete evidence does not by itself establish permission
to proceed.

An evaluator-integrity failure, including any `MISSING` Charter check, prevents
further runtime progression. The failure and all available evaluation state,
evidence, provenance, and attribution are preserved.

A completed Final Charter finding may also prohibit further runtime progression
where the applicable Charter safeguard or guardrail requires that outcome. In
that case, the `FinalCharterResult` records the substantive Charter
determination and its supporting evidence, provenance, and conditions, and the
current pathway does not proceed to bound-state determination, binding,
transition validation, commitment, deployment, or another ordinary downstream
runtime stage.

A substantive Charter prohibition remains distinct from evaluator-integrity
failure. The former is a completed Charter determination; the latter means the
required Charter evaluation could not be validly completed.

Where the completed `FinalCharterResult` permits further controlled progression,
the result proceeds with the existing `FinalPathwayResult` to bound-state
determination.

The `CharterEvaluator` determines Charter validity and records the conditions
governing progression. It does not determine the applicable bound state and does
not perform binding or enforcement. Those responsibilities belong to subsequent
runtime components.

---

## 17. Binding and Bound States

After Final Charter Evaluation completes and continued progression is permitted,
a system-side function within the runtime determines the bound state of the
completed pathway evaluation.

The bound state is the final state determination of a completed `ProductPathway`
evaluation. It records the pathway’s validity or type of failure based on the
completed system-side progression, including its relationship to the
`TransitionPathway` and ultimately to achieving accelerated operational net
zero. The bound state preserves any restrictions, unresolved conditions,
obligations, and other limits established by the evaluation without altering the
findings that produced them.

Bound-state determination operates only on completed evaluation state.
Only evaluator-integrity failures and substantive Charter prohibitions that
terminate runtime progression under Section 16.5 do not progress to ordinary
binding flow.

Once the applicable bound state has been determined, `BindingHandler` combines
that state with the existing immutable `FinalPathwayResult` to produce a new
immutable `BoundPathway`.

`BindingHandler` does not modify the `FinalPathwayResult`. The `BoundPathway`
preserves a reference to that completed evaluation result and records the
applicable bound state as the subsequent runtime state of that evaluation.

### 17.1 BindingHandler

`BindingHandler` receives a completed pathway evaluation only after Final
Charter Evaluation has permitted further progression and an applicable bound
state has been determined.

Its responsibility is to attach the applicable bound state to the completed
pathway evaluation while preserving the identity, findings, evaluator ownership,
evidence, provenance, restrictions, and other conditions already established
upstream.

`BindingHandler` shall verify that the bound state belongs to the same
evaluation lineage represented by the `FinalPathwayResult` and
`FinalCharterResult`.

The handler does not decide whether a Charter condition is valid, whether a
pathway finding is correct, or whether a substantive bound state would be more
appropriate. Those determinations are made by prior product-pathway evaluation
or system-side functions. Where the runtime does not return a usable result,
`BindingHandler` produces a `BoundPathway` containing `NoAck`. That
`BoundPathway` terminates the current evaluation flow before `PathwayAssessment`.

Binding produces one immutable `BoundPathway`.

The `BoundPathway` contains or references the immutable
`FinalPathwayResult` and its applicable bound state. It does not replace,
modify, or reinterpret the `FinalPathwayResult`.

A successfully bound `BoundPathway` is consumed by the later
`PathwayAssessment` stage.

### 17.2 Binding Inputs

`BindingHandler` receives, as applicable:

* the completed immutable `FinalPathwayResult`;
* the applicable bound state returned from runtime evaluation;
* the identity and version of the rule or mechanism that determined the bound
  state; and
* `user_id` and `pathway_id` attribution.

Where the runtime does not return a usable result, `BindingHandler` produces a
`BoundPathway` containing `NoAck` as defined in Section 17.4.1.

Binding makes no changes to the completed immutable `FinalPathwayResult`.
The `FinalPathwayResult` remains the authoritative completed pathway-evaluation
artifact.

`BindingHandler` creates a new immutable `BoundPathway` that references the
`FinalPathwayResult` and records the applicable bound state.

`BindingHandler` shall validate that the `FinalPathwayResult`, applicable bound
state, and any required evaluation-lineage references identify the same
pathway and evaluation state before constructing the `BoundPathway`.

A missing, malformed, stale, mismatched, or otherwise invalid binding input does
not create permission to proceed.

### 17.3 Binding Outputs

`BoundPathway` is the immutable output of `BindingHandler`.

`BoundPathway` contains the association of one completed immutable
`FinalPathwayResult` with one applicable bound state for the evaluated instance.

At minimum, `BoundPathway` preserves:

* a reference to the completed `FinalPathwayResult`;
* the applicable bound state;
* `user_id` and `pathway_id` attribution; and
* the binding-rule or mechanism identity and version required to identify how
  the state was attached.

`BoundPathway` does not copy or modify the findings contained in the
`FinalPathwayResult`. Binding adds the runtime state association while leaving
the completed evaluation artifact unchanged.

Where the runtime does not return a usable result, `BindingHandler` produces a
`BoundPathway` containing `NoAck`. The resulting `BoundPathway` is invalid for
downstream progression and terminates the current evaluation flow before
`PathwayAssessment`.

### 17.4 Applicable Bound States

Every pathway entering ordinary binding receives one explicit bound state.

A bound state is the final runtime state determination of the completed pathway
evaluation after Final Charter Evaluation. It records the pathway's validity or
type of failure in relation to the evaluated `ProductPathway`, its system-side
progression, its relationship to the applicable `TransitionPathway`, and
ultimately the accelerated net-zero transition.

Where applicable, a bound state such as `FossilBound`, `HarmBound`, or
`BoundaryStress` records restrictions, unresolved conditions, obligations, or
other limits established by the completed evaluation.

The bound-state model distinguishes among:

* states permitting ordinary downstream progression;
* states permitting progression only under explicit conditions, restrictions,
  monitoring, or other requirements established by the completed evaluation;
* states limiting progression to remedy, resolution, review, redesign,
  evidence gathering, re-evaluation, or another non-ordinary flow; and
* states indicating that the runtime successfully completed evaluation but
  could not determine an applicable ordinary bound state.

The bound-state vocabulary shall preserve materially different runtime
outcomes instead of collapsing them into generic pass, fail, conditional,
or restricted statuses.

This distinction is necessary because different runtime outcomes may produce
the same immediate restriction while carrying different meanings, evidence
histories, risks, and valid next actions. Collapsing those differences would
discard information needed to determine why progression was restricted and
what must happen before that restriction can change.

Preserving these distinctions also helps protect against false-green states,
where a system appears valid, authorized, entrusted, complete, or
operationally sound only because a required condition was missing, stale,
mismatched, unresolved, incompletely evaluated, or improperly established
rather than actually satisfied. Keeping those conditions distinct prevents
them from being treated as interchangeable or silently converted into a more
permissive state.

The same principle requires action validity, authorization validity, outcome
quality, actor entrustment, culpability, evidentiary sufficiency, and system
integrity to remain distinguishable where they materially affect the result.
One cannot substitute for another solely because they lead to the same
immediate restriction.

Preserving these distinctions also allows downstream components to apply the
appropriate resolution, remedy, review, monitoring, evidence-gathering, or
re-evaluation flow without reconstructing or reinterpreting the upstream
evaluation.

A bound state is immutable. If a later change in pathway state, evidence,
Charter status, authorization, or another material condition requires
re-evaluation, the completed re-evaluation produces a new applicable bound
state rather than modifying the existing state.

#### 17.4.1 Bound-State Definitions

ClimateSOS defines the following bound states.

**`CleanBound`**

The pathway completed evaluations successfully, resulting in clean
deliverability. During evaluation the required queues cleared, and the
resulting pathway successfully synchronized the applicable clean-transition
requirements within the required timing window, without fossil fallback.

`CleanBound` permits ordinary downstream progression. Any conditions or
restrictions established upstream remain attached to the evaluation and
continue to govern downstream use.

**`MixedBound`**

The pathway has satisfied some or all applicable clean-transition
requirements, but a material fossil dependency, fallback pathway, unresolved
system condition, or other restricting condition remains entangled with the
resulting state.

`MixedBound` does not represent full transition success. Downstream
progression is limited by the specific restrictions and conditions preserved
from the completed evaluation.

**`FossilBound`**

The pathway has become bound to fossil fallback, fossil persistence, fossil
adequacy, fossil lock-in, or another fossil-dependent resulting state.

`FossilBound` does not permit the pathway to proceed as a valid
clean-transition pathway. Further progression is limited to an applicable
remedy, resolution, review, redesign, or re-evaluation flow.

**`NoAck`**

`NoAck` indicates that the runtime did not return a usable result for binding.

This includes a result that is not returned within the applicable runtime
period or a returned result that is malformed, invalid, or otherwise unusable.

When this occurs, `BindingHandler` produces a `BoundPathway` containing
`NoAck`. The resulting `BoundPathway` is invalid for downstream progression
and terminates the current evaluation flow before `PathwayAssessment`.

**`Unbound`**

The runtime completed the applicable pathway and system-side evaluations
successfully but could not determine which ordinary or restricted bound state
correctly applies.

`Unbound` may result when the pathway, its documentation, evidence, or
completed evaluations do not provide enough information to support a
defensible bound-state determination, even though evaluation completed
successfully.

`Unbound` is therefore distinct from `NoAck`.

```text
NoAck
    runtime did not return a usable result for binding
    BoundPathway is invalid and evaluation stops

Unbound
    runtime completed successfully
    but no defensible bound state could be determined
```

An `Unbound` pathway may proceed only into the applicable evidence, review,
resolution, or re-evaluation flow needed to establish a bindable state.

**`HarmBound`**

The completed pathway evaluation has established that the pathway is bound to
some condition or conditions that cause material harm.

Such conditions may include harm to people, communities, workers, ecosystems,
rights, agency, sovereignty, data integrity, or other Charter-protected
interests.

`HarmBound` does not authorize ordinary continuation of the pathway as
evaluated. Where correction remains possible, further progression is limited
to halt, remedy, repair, redesign, verification, review, or re-evaluation.

**`BoundaryStress`**

The pathway creates or worsens material pressure against an applicable
planetary, biosphere, justice, adequacy, or system-integrity boundary without
necessarily having resolved to final harm or system failure.

`BoundaryStress` preserves the identified boundary pressure and any associated
constraints. Depending on the completed evaluation, progression may require
monitoring, additional evidence, mitigation, remedy, redesign, or re-evaluation.

**`BioBound`**

The pathway contributions are exclusively Nature-Based, or primarily
Nature-Based with other interventions that don't produce any harm or fossil
fallback. It has completed evaluation in a state consistent with the applicable
biosphere-integrity requirements and remains within the modeled functional
resilience conditions of the Biosphere Fabric.

`BioBound` is a biosphere-specific resulting state. It records that the
pathway's evaluated interaction with relevant ecological systems is compatible
with the required biosphere conditions rather than merely achieving a carbon
or technical transition outcome.

The detailed runtime semantics of `BioBound` remain subject to further
Biosphere Fabric implementation.

**`RestorationBound`**

The pathway has completed evaluation as a valid biosphere-restoration pathway
under the applicable ecological, Charter, evidence, and system-side
conditions.

`RestorationBound` is distinct from general `BioBound` because it records an
affirmative restoration function rather than only compatibility with biosphere
integrity.

The detailed runtime semantics of `RestorationBound`, including restoration
thresholds, ecological recovery conditions, and required evidence, remain
subject to further Biosphere Fabric implementation.

#### 17.4.2 Reserved Bound States

The following names are reserved for future use and are not yet part of the
ordinary binding contract:

**`CDRBound` — reserved**

Reserved for a future carbon-dioxide-removal-specific state if implementation
shows that CDR pathways require a distinct bound state rather than
representation through existing pathway, biosphere, contribution, and risk
results.

No current pathway may infer `CDRBound` semantics merely from the reserved name.

**`WaterBound` — reserved**

Reserved for a future water-cycle or hydrological resulting state if
implementation of the Biosphere Fabric demonstrates a need for an independently
bound water-system outcome.

No current pathway may infer `WaterBound` semantics merely from the reserved
name.

The reserved states exist to preserve architectural space already identified in
earlier ClimateSOS design work without prematurely fixing runtime behavior that
has not yet been implemented.

### 17.5 Binding Does Not Re-Evaluate the Pathway

`BindingHandler` does not rerun pathway evaluation, Charter evaluation, net
overall system contribution evaluation, scale diagnostics, candidate transition
construction, or net overall system risk evaluation.

It does not convert an adverse, unresolved, constrained, limited, or conditional
finding into a more permissive finding.

It does not infer that absence of a newly identified restriction establishes
permission beyond the authority represented by the applicable bound state.

Where multiple upstream findings contribute to the same bound condition, those
findings remain separately identifiable with their original evaluator
ownership, evidence, provenance, and purpose.

Successful binding records the state determined by the runtime in a new
immutable `BoundPathway`.

---

## 18. PathwayAssessment and State Preservation

`PathwayAssessment` is the final immutable assessment of one completed
`ProductPathway` evaluation run.

It is constructed after binding is complete and the immutable `BoundPathway`
has been produced from the `FinalPathwayResult` and applicable bound state.
It does not perform another evaluation, revise an upstream finding, or replace
previously evaluated result objects.

`PathwayAssessment` marks the final stage of the shared product-pathway flow
when further re-evaluation is not required. If resolution, remedy, or another
condition requires re-evaluation, that process proceeds from this state before
the pathway enters either the global-context or user-submitted-context outcome
flow.

The completed `ProductPathway` and prior evaluation results remain immutable;
later assessment, remedy, and re-evaluation state is recorded in new runtime
objects rather than written back into the earlier evaluation state.

### 18.1 PathwayAssessment

Each completed evaluation run produces one `PathwayAssessment`.

The assessment records the completed evaluation state for the specific
`ProductPathway`, evaluation run, and transition context that were evaluated.
It provides the runtime with one stable object from which the permitted next
flow can be determined without changing or reconstructing the evaluations that
produced it.

A `PathwayAssessment` shall represent a successful, conditional, restricted,
failed, unresolved, or other successfully completed bound outcome.

### 18.2 Required Assessment Contents

`PathwayAssessment` has its own immutable assessment identity and identifies the
evaluation run that produced it.

At minimum, it shall include or reference, as applicable:

* `pathway_assessment_id`;
* `pathway_id`;
* `evaluation_run_id`;
* `InitialCharterResult`;
* `IntegratedCharterResult`;
* `FinalCharterResult`;
* `BoundPathway`; and
* the identity and version of the validated `TransitionPathway` used as the
  reference for the evaluation.

The assessment may carry additional references required for provenance,
methodology, runtime-version, rules-version, or other implementation integrity,
but those references do not transfer ownership of the underlying records to
`PathwayAssessment`.

### 18.3 Evaluation Trace and Evidence

Through its `BoundPathway` reference, `PathwayAssessment` retains access to the
`evaluation_trace` on `FinalPathwayResult` and the documentation, evidence,
findings, methods, provenance, and evaluation context preserved by the
referenced upstream results.

A reviewer or downstream runtime component shall be able to follow the
assessment references through the evaluation lineage sufficiently to determine:

* what pathway and transition state were evaluated;
* which evaluation run produced the assessment;
* which evaluator produced each material finding;
* what evidence, provenance, methodology, or unresolved condition supports that
  finding; and
* how the completed findings relate to the resulting bound state.

Missing, conflicting, unresolved, or insufficient evidence remains represented
by the upstream results that established those conditions and recorded them in
their respective immutable results.

### 18.4 Prior-State Preservation

Where a pathway is re-evaluated, ClimateSOS preserves each evaluation run in
an append-only evaluation history.

A `pathway_id` identifies one `ProductPathway` and its associated pathway
evaluation lineage. Each complete attempt to evaluate that pathway receives
a distinct `evaluation_run_id`, and each completed assessment receives a
distinct `pathway_assessment_id`.

Results belonging to one evaluation run shall not overwrite, replace, or be
substituted for results belonging to another run.

Where a later evaluation follows an earlier evaluation of the same pathway
lineage, the later run shall reference the prior run sufficiently to preserve
the sequence of evaluation history.

Conceptually:

```text
pathway_id = P123

evaluation_run_id = R001
    PathwayAssessment = A001

evaluation_run_id = R002
    prior_evaluation_run_id = R001
    PathwayAssessment = A002
```text

`A002` does not replace or mutate `A001`. Both remain part of the pathway's
evaluation history.

### 18.5 Re-Evaluation and Successor Results

Pathway re-evaluation creates a new evaluation run.

The new run receives a new `evaluation_run_id` and produces new result objects
through each successfully completed evaluation stage.

The successor run shall preserve a reference to the prior evaluation run and
the reason the new evaluation was initiated.

The stable `pathway_id` may continue across evaluation runs where the system is
evaluating the same pathway lineage. A materially separate intake or separately
defined pathway receives its own pathway identity as defined in Section 5.

A remedy, new evidence, corrected documentation, changed authorization, material
pathway change, changed Charter condition, changed transition reference, or
another condition requiring re-evaluation produces a successor run and does not
modify the completed results or `PathwayAssessment` from the prior run.

---

## 19. Resolution and Remedy

### 19.1 Resolution Outcomes

### 19.2 Remedy Eligibility

### 19.3 Remedy Processing

### 19.4 Re-Evaluation After Remedy

### 19.5 Non-Remediable Outcomes

### 19.6 Preservation of Failed and Unresolved Results

This preserves the useful archive material on remedy and state history without treating every failure as remedy-eligible or writing those states back into the pathway.

---

## 20. Global Context Outcome

### 20.1 TransitionPathwayValidator

### 20.2 Validation Requirements

### 20.3 Atomic Immutable Commitment

### 20.4 Validation Failure

### 20.5 Preservation of the Existing Reference Pathway

### 20.6 Use at the Next Startup

---

## 21. User-Submitted Context Outcome

### 21.1 Immutable Global Reference Pathway

### 21.2 Separate Evaluation of Multiple Submissions

### 21.3 Result Construction

### 21.4 No Mutation of the Global TransitionPathway

### 21.5 Combined Pathways as Separate Intakes

---

## 22. Evaluation Questions

### 22.1 What Does the Pathway Require?

### 22.2 What Does the Pathway Produce?

### 22.3 What System Contribution Results?

### 22.4 What Can Fail?

### 22.5 What Risks Propagate?

### 22.6 What Resolution or Remedy Is Available?

---

## 23. Implementation Requirements

### 23.1 Required Data Models

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
InitialCharterResult
PathwayEngineResult
IntegratedCharterResult
ScaleDiagnosticResult
FinalPathwayResult
FinalCharterResult
NetOverallSystemRiskResult
NetOverallSystemContribution
BoundPathway
PathwayAssessment
TransitionPathway
```

### 23.2 Required Evaluators, Assemblers and Services

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
NetOverallSystemContributionEvaluator
ScaleDiagnosticEvaluator
TransitionPathwayCompiler
NetOverallSystemRiskEvaluator
FinalPathwayAssembly
CharterEvaluator
BindingHandler
TransitionPathwayValidator
```

### 23.3 Immutability and State-Integrity Requirements

### 23.4 Identity and Attribution Requirements

### 23.5 Error and Missing-Result Requirements

### 23.6 Minimum Test Cases

---

## 24. Relationship to the ClimateSOS Runtime Architecture

### 24.1 Shared Product Pathway Evaluation Flow

### 24.2 Global Boot Context

### 24.3 User-Submitted Context

### 24.4 Component Ownership Summary

---

## 25. Summary

