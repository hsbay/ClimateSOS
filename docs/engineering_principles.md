# ClimateSOS Engineering Principles

**ClimateSOS is software in service of the climate transition.**

Its architecture should reflect the structure of the transition itself rather than contemporary software fashion.

These principles exist to preserve simplicity, transparency, extensibility, and long-term maintainability while remaining faithful to the ClimateSOS Charter.

## 1. The Runtime Serves the Charter

The runtime operates in accordance with the ClimateSOS Charter.

The software must never violate:

* planetary boundaries
* justice
* transparency
* human accountability
* scientific integrity

---

## 2. Model Reality Before Software

Software exists to represent the transition.

Do not invent software abstractions that do not correspond to real transition phenomena.

When in doubt, simplify until the software reflects the domain rather than the implementation.

---

## 3. Build Small Things That Compose

Each component should perform one responsibility well.

Compose systems from cooperating components rather than growing monolithic software.

Favor simple interfaces between components.

---

## 4. Design for Extension

New capabilities should be added without rewriting the existing system.

Favor stable interfaces, modular components, and incremental evolution over large rewrites.

Ask:

> *Can someone extend this without rewriting it?*

---

## 5. Prefer Open Systems

Avoid unnecessary lock-in.

Prefer:

* open standards
* open file formats
* documented interfaces
* portable implementations

Portability is preferred over vendor dependence.

---

## 6. Design for Many Users

ClimateSOS is intended to outlive its original author.

Design so that researchers, NGOs, utilities, governments, companies, and other institutions can use the runtime independently.

Maintain clear separation between:

* runtime
* configuration
* data
* plugins
* outputs

---

## 7. Secure by Default

Security and stability are architectural requirements, not afterthoughts.

New capabilities should be evaluated for correctness, misuse, resilience, and failure modes before they become part of the runtime.

Red-team architecture before declaring it complete.

---

## 8. Prefer Explicit Behavior

Explicit behavior is preferred over hidden magic.

Avoid unnecessary:

* factories
* dependency injection
* runtime reflection
* metaprogramming

unless there is a compelling architectural reason.

---

## 9. The Whatever Principle

> Before introducing a new abstraction, ask whether it represents something that actually exists in the transition or is required to support it.

If not...

**Don't build it.**

---

## 10. Preserve Provenance

Every result should be reproducible.

Every assumption should be traceable.

Every step in the logic chain must be explainable.

Nothing should appear simply because "the software said so."

The runtime should make its reasoning inspectable wherever practical.

---

## 11. Write for Humans

People read code far more often than they write it.

Choose names that are descriptive, memorable, and reflect the transition itself.

Prefer:

```
ProductQueueBundle
```

over

```
PQBundleMgrFactory
```

Computers do not care.

Future contributors do.

---

## 12. Name Things After the World

Prefer names that describe the transition rather than the implementation.

Good:

```
ProductQueue
TransitionPathway
BindingDecision
```

Less desirable:

```
QueueManager
TransitionProcessor
ExecutionController
```

The runtime vocabulary should describe the climate transition rather than the implementation.

---

## 13. Simplicity is a Feature

Complexity is a cost.

Prefer the simplest architecture that faithfully represents the transition.

Delete unnecessary concepts.

Reduce cognitive load.

Software should become easier to understand over time, not harder.

---
