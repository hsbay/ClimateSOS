# ClimateSOS Product Pathway Adapter Glossary

## Runtime Objects

These are persistent runtime objects created, stored, or referenced by ClimateSOS.

| Canonical name                   | Meaning                                                                                           | Acceptable prose                                     |
| -------------------------------- | ------------------------------------------------------------------------------------------------- | ---------------------------------------------------- |
| **IdentityToken**                | Canonical identifier assigned during intake.                                                      | identity token                                       |
| **ProductPathway**               | Runtime representation of an external product or customer pathway.                                | product pathway, pathway                             |
| **ProductOutput**                | What the pathway physically or functionally produces.                                             | product output, output                               |
| **NetOverallSystemContribution** | The pathway's net contribution to the overall transition system after synchronization evaluation. | net overall system contribution, system contribution |
| **PathwayQueueBundle**           | Collection of input and output queues associated with and evaluated for a ProductPathway.         | required queues                                      |
| **StateHistory**                 | Persistent history of previous evaluations and resulting states.                                  | state history                                        |
| **EvidenceTrace**                | Evidence supporting evaluations, remedies, and resulting states.                                  | evidence trace                                       |
| **RemedyTrace**                  | Record of remedy actions and re-evaluation history.                                               | remedy trace                                         |
| **ReEvaluationEvent**            | Record describing a completed re-evaluation.                                                      | re-evaluation event                                  |

---

## Runtime Processes

These are evaluation processes performed by ClimateSOS.

| Canonical name                      | Meaning                                                                   |
| ----------------------------------- | ------------------------------------------------------------------------- |
| **FoundationalCharterEvaluation**   | Evaluates Charter compliance before synchronization.                      |
| **GuardrailEvaluation**             | Evaluates applicable guardrail domains.                                   |
| **SystemSynchronizationEvaluation** | Evaluates synchronization with the broader transition system.             |
| **QueueEvaluation**                 | Evaluates required queue readiness, dependencies, and blocking conditions.|
| **RemedyBus**                       | Carries evidence, redesigns, and corrective actions before re-evaluation. |
| **ProductPathwayAdapter**           | Translates and normalizes external pathways into ClimateSOS runtime objects.|
| **IntakeAndIdentityLayer**          | Assigns identity, provenance, and intake safeguards.                      |

---

## Runtime Evaluation Outputs

These are canonical evaluation results produced by ClimateSOS runtime processes.

| Canonical name          | Meaning                                                                                 |
| ----------------------- | --------------------------------------------------------------------------------------- |
| **GuardrailResolution** | Outcome of GuardrailEvaluation.                                                         |
| **ResultingState**      | Overall evaluated state assigned by ClimateSOS.                                         |
| **ScaleDiagnostic**     | Explains scale readiness or bottlenecks.                                                |
| **ResolutionPathway**   | Describes how the pathway proceeds after evaluation (continue, preserve, remedy, etc.). |

---

## Design Conventions

Throughout the ClimateSOS specifications:

* **CamelCase** (`ProductPathway`, `ResultingState`) denotes a canonical runtime object, process, or evaluation record.
* **Natural language** ("product pathway", "resulting state", "system contribution") is used in explanatory prose unless referring to the canonical runtime concept.
* Canonical names should be defined when first introduced. Subsequent explanatory text may use the natural-language form so long as the meaning remains unambiguous.
* Canonical names should remain stable across specifications whenever practical.
* Enumeration values (for example, `CleanBound` or `ScaleUpTippingState`) are defined in their respective specifications rather than in this glossary.

---


