# Climate State transition model OS
# Github Project Code: https://github.com/hsbay/ClimateSOS, CC-BY 4.0 2026 @safiume

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

class BoundOutcome(str, Enum):
    CLEAN_BOUND="CleanBound"; FOSSIL_BOUND="FossilBound"; MIXED_BOUND="MixedBound"; NOACK="NoAck"; UNBOUND="Unbound"
class TemporalState(str, Enum):
    FRESH="Fresh"; AGING="Aging"; NEAR_TIMEOUT="Near-timeout"; EXPIRED="Expired"; STALE_SUCCESS="Stale-success"
class QueueStatus(str, Enum):
    CLEAR="Clear"; BLOCKED="Blocked"; STARVED="Starved"; EXPIRED="Expired"; CLOSED="Closed"
class AlignmentState(str, Enum):
    CLEAN_DELIVERABLE="Clean-deliverable state"; FOSSIL_LOCK_IN="Fossil lock-in state"; MIXED_DELIVERY="Mixed-bound delivery state"; TIMEOUT="Timeout / failed-sync state"; PENDING="Pending"
class BindingEvent(str, Enum):
    ACK="ACK"; REVOKE="REVOKE"; NONE="NONE"
class BioNPUState(str, Enum):
    PRODUCTIVE="Productive"; DEGRADED="Degraded"; DISCONNECTED="Disconnected"; RECOVERING="Recovering"; COLLAPSED="Collapsed"; RESILIENT="Resilient"
class BioOutcome(str, Enum):
    BIO_BOUND="BioBound"; RESTORATION_BOUND="RestorationBound"; CARBON_REMOVAL_BOUND="CarbonRemovalBound"; WATER_CYCLE_BOUND="WaterCycleBound"; HARM_BOUND="HarmBound"; NOACK="NoAck"
class WorkerState(str, Enum):
    FOSSIL_ATTACHED="Fossil-attached"; TRANSITIONING="Transitioning"; CLEAN_ATTACHED="Clean-attached"; RETIRED="Retired"; STRANDED="Stranded"; PROTECTED_EXIT="Protected-exit"

@dataclass
class IdentityToken:
    name: str
    ttl_years: int
    created_year: int
    required_queues: List[str]
    outcome: BoundOutcome = BoundOutcome.UNBOUND
    state: AlignmentState = AlignmentState.PENDING
    binding_event: BindingEvent = BindingEvent.NONE
    notes: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    def temporal_state(self, year:int, required_clear:bool=False)->TemporalState:
        age = year - self.created_year
        if age > self.ttl_years:
            return TemporalState.STALE_SUCCESS if required_clear else TemporalState.EXPIRED
        if age == self.ttl_years: return TemporalState.NEAR_TIMEOUT
        if age >= max(1, int(self.ttl_years * 0.6)): return TemporalState.AGING
        return TemporalState.FRESH
    def record(self, event:str)->None: self.history.append(event)

@dataclass
class Queue:
    name: str
    capacity: float
    demand: float
    latency_years: int
    ttl_years: int
    bound_type: str
    intentionally_closed: bool = False
    def status(self)->QueueStatus:
        if self.intentionally_closed: return QueueStatus.CLOSED
        if self.latency_years > self.ttl_years: return QueueStatus.EXPIRED
        if self.capacity <= 0: return QueueStatus.STARVED
        if self.demand > self.capacity: return QueueStatus.BLOCKED
        return QueueStatus.CLEAR
    def clearance_ratio(self)->float:
        return 1.0 if self.demand <= 0 else min(1.0, self.capacity / self.demand)

@dataclass
class Fabric:
    name: str
    queue_names: List[str]
    def report(self, queues:Dict[str, Queue])->Dict[str, QueueStatus]:
        return {n: queues[n].status() for n in self.queue_names if n in queues}
    def all_clear(self, queues:Dict[str, Queue])->bool:
        r = self.report(queues); return bool(r) and all(s == QueueStatus.CLEAR for s in r.values())
    def any_clear(self, queues:Dict[str, Queue])->bool:
        r = self.report(queues); return bool(r) and any(s == QueueStatus.CLEAR for s in r.values())

@dataclass
class ShockOperator:
    name: str
    target_queue: str
    demand_multiplier: float = 1.0
    capacity_multiplier: float = 1.0
    latency_delta: int = 0
    def apply(self, queues:Dict[str, Queue])->None:
        q = queues.get(self.target_queue)
        if q:
            q.demand *= self.demand_multiplier
            q.capacity *= self.capacity_multiplier
            q.latency_years += self.latency_delta

@dataclass
class AttractorPattern:
    name: str
    trigger_queue: str
    blocked_outcome: BoundOutcome
    def evaluate(self, queues:Dict[str, Queue])->Optional[BoundOutcome]:
        q = queues.get(self.trigger_queue)
        if q and q.status() in {QueueStatus.BLOCKED, QueueStatus.STARVED, QueueStatus.EXPIRED}: return self.blocked_outcome
        return None

@dataclass
class SynchronizationScheduler:
    queues: Dict[str, Queue]
    fabrics: Dict[str, Fabric]
    attractors: List[AttractorPattern]
    def bottlenecks(self):
        rows = [(n, q.status(), q.clearance_ratio()) for n, q in self.queues.items() if q.status() not in {QueueStatus.CLEAR, QueueStatus.CLOSED}]
        return sorted(rows, key=lambda x: x[2])
    def closed_queues(self): return [n for n, q in self.queues.items() if q.status() == QueueStatus.CLOSED]
    def required_clear(self, names): return all(self.queues[n].status() == QueueStatus.CLEAR for n in names)
    def fabric_ready(self, name): return self.fabrics[name].all_clear(self.queues)
    def fabric_partial(self, name):
        f = self.fabrics[name]; return f.any_clear(self.queues) and not f.all_clear(self.queues)
    def attractor_outcome(self):
        for a in self.attractors:
            out = a.evaluate(self.queues)
            if out: return out
        return None

@dataclass
class DeliveryAlignmentSwitch:
    scheduler: SynchronizationScheduler
    clean_fabric: str = "Deliverability Fabric"
    fossil_fabric: str = "Fossil Constraint Fabric"
    def revoke(self, token, reason):
        token.binding_event = BindingEvent.REVOKE
        token.notes.append(f"Binding revoked: {reason}")
        token.record(f"REVOKE {token.outcome.value}: {reason}")
        token.outcome = BoundOutcome.UNBOUND; token.state = AlignmentState.PENDING
        return token
    def _finish(self, token, outcome, state, event, note, hist):
        token.outcome = outcome; token.state = state; token.binding_event = event
        token.notes.append(note); token.record(hist); return token
    def bind(self, token, year):
        clear = self.scheduler.required_clear(token.required_queues)
        temporal = token.temporal_state(year, clear)
        if temporal == TemporalState.STALE_SUCCESS:
            return self._finish(token, BoundOutcome.NOACK, AlignmentState.TIMEOUT, BindingEvent.NONE, "Stale-success: queues cleared, but after TTL.", "NOACK Stale-success")
        if temporal == TemporalState.EXPIRED:
            return self._finish(token, BoundOutcome.NOACK, AlignmentState.TIMEOUT, BindingEvent.NONE, "TTL expired before synchronization.", "NOACK Expired")
        attracted = self.scheduler.attractor_outcome()
        if attracted == BoundOutcome.FOSSIL_BOUND:
            return self._finish(token, BoundOutcome.FOSSIL_BOUND, AlignmentState.FOSSIL_LOCK_IN, BindingEvent.ACK, "Captured by fossil/fallback attractor pattern.", "ACK FossilBound via attractor")
        if attracted == BoundOutcome.MIXED_BOUND:
            return self._finish(token, BoundOutcome.MIXED_BOUND, AlignmentState.MIXED_DELIVERY, BindingEvent.ACK, "Captured by mixed-bound attractor pattern.", "ACK MixedBound via attractor")
        if attracted == BoundOutcome.NOACK:
            return self._finish(token, BoundOutcome.NOACK, AlignmentState.TIMEOUT, BindingEvent.NONE, "Captured by NoAck attractor pattern.", "NOACK via attractor")
        unresolved = [q for q in token.required_queues if self.scheduler.queues[q].status() != QueueStatus.CLEAR]
        if unresolved:
            if self.scheduler.fabric_ready(self.fossil_fabric):
                return self._finish(token, BoundOutcome.FOSSIL_BOUND, AlignmentState.FOSSIL_LOCK_IN, BindingEvent.ACK, f"Clean path unresolved ({', '.join(unresolved)}); fossil fallback available.", "ACK FossilBound via fallback")
            return self._finish(token, BoundOutcome.NOACK, AlignmentState.TIMEOUT, BindingEvent.NONE, f"Unresolved required queues: {', '.join(unresolved)}.", "NOACK unresolved queues")
        clean_ready = self.scheduler.fabric_ready(self.clean_fabric)
        fossil_ready = self.scheduler.fabric_ready(self.fossil_fabric)
        clean_partial = self.scheduler.fabric_partial(self.clean_fabric)
        fossil_partial = self.scheduler.fabric_partial(self.fossil_fabric)
        if clean_ready and not fossil_ready:
            return self._finish(token, BoundOutcome.CLEAN_BOUND, AlignmentState.CLEAN_DELIVERABLE, BindingEvent.ACK, "Clean deliverability fabric cleared; identity bound to clean state.", "ACK CleanBound")
        if clean_ready and fossil_ready:
            return self._finish(token, BoundOutcome.MIXED_BOUND, AlignmentState.MIXED_DELIVERY, BindingEvent.ACK, "Clean path cleared, but fossil fallback remains available; identity is mixed-bound.", "ACK MixedBound")
        if clean_partial and fossil_ready:
            return self._finish(token, BoundOutcome.MIXED_BOUND, AlignmentState.MIXED_DELIVERY, BindingEvent.ACK, "Partial clean deliverability plus fossil fallback produced mixed-bound state.", "ACK MixedBound partial clean")
        if fossil_ready or fossil_partial:
            return self._finish(token, BoundOutcome.FOSSIL_BOUND, AlignmentState.FOSSIL_LOCK_IN, BindingEvent.ACK, "Fossil fallback pathway cleared; identity bound to fossil state.", "ACK FossilBound")
        return self._finish(token, BoundOutcome.NOACK, AlignmentState.TIMEOUT, BindingEvent.NONE, "No fabric produced a synchronized outcome.", "NOACK no fabric")

@dataclass
class BioNPU:
    name: str
    cycle_buses: List[str]
    state: BioNPUState
    biodiversity_index: float
    carbon_function: float
    water_function: float
    resilience: float
    def harmed(self): return self.state in {BioNPUState.DEGRADED, BioNPUState.DISCONNECTED, BioNPUState.COLLAPSED}

@dataclass
class BiosphereFabric:
    npus: List[BioNPU]
    required_buses: List[str]
    min_biodiversity: float = 0.60
    min_resilience: float = 0.60
    min_carbon: float = 0.50
    min_water: float = 0.50
    def evaluate(self):
        if not self.npus: return BioOutcome.NOACK
        if any(n.harmed() for n in self.npus): return BioOutcome.HARM_BOUND
        buses = {b for n in self.npus for b in n.cycle_buses}
        if any(b not in buses for b in self.required_buses): return BioOutcome.NOACK
        n = len(self.npus)
        bio = sum(x.biodiversity_index for x in self.npus) / n
        res = sum(x.resilience for x in self.npus) / n
        car = sum(x.carbon_function for x in self.npus) / n
        wat = sum(x.water_function for x in self.npus) / n
        if bio >= self.min_biodiversity and res >= self.min_resilience:
            if car >= self.min_carbon and wat >= self.min_water: return BioOutcome.BIO_BOUND
            if car >= self.min_carbon: return BioOutcome.CARBON_REMOVAL_BOUND
            if wat >= self.min_water: return BioOutcome.WATER_CYCLE_BOUND
            return BioOutcome.RESTORATION_BOUND
        return BioOutcome.NOACK

@dataclass
class WorkerToken:
    name: str
    current_sector: str
    age: int
    skills: List[str]
    wage_protection: bool
    pension_protection: bool
    retraining_access: bool
    clean_job_available: bool
    retirement_eligible: bool
    state: WorkerState = WorkerState.FOSSIL_ATTACHED
    notes: List[str] = field(default_factory=list)

class WorkerTransitionOperator:
    def transition(self, w):
        if w.retirement_eligible and w.pension_protection:
            w.state = WorkerState.RETIRED; w.notes.append("Worker exited fossil sector through protected retirement.")
        elif w.retraining_access and w.clean_job_available and w.wage_protection:
            w.state = WorkerState.CLEAN_ATTACHED; w.notes.append("Worker transitioned from fossil role to clean-sector job with wage protection.")
        elif w.retraining_access and w.wage_protection:
            w.state = WorkerState.TRANSITIONING; w.notes.append("Worker is in protected transition; clean placement not yet complete.")
        elif w.wage_protection or w.pension_protection:
            w.state = WorkerState.PROTECTED_EXIT; w.notes.append("Worker has partial protection but no completed clean reattachment.")
        else:
            w.state = WorkerState.STRANDED; w.notes.append("Worker stranded by fossil exit without protection or reattachment path.")
        return w

REQUIRED = ["Project Finance Queue","Permitting / Authorization Queue","Deliverability Queue","Adequacy Queue","Materials Queue","Workforce Throughput Queue","Utility Revenue Stabilization Queue","Nuclear Fleet Stability Queue","Emerging Market De-risking Queue"]

def q(name, cap, dem, lat, ttl, bound, closed=False): return Queue(name, cap, dem, lat, ttl, bound, closed)

def make_queues(fossil_fallback=False):
    return {
        "Project Finance Queue": q("Project Finance Queue",100,90,1,3,"finance-bound"),
        "Permitting / Authorization Queue": q("Permitting / Authorization Queue",100,80,1,3,"permit-bound"),
        "Deliverability Queue": q("Deliverability Queue",100,95,2,4,"wpu/supply/permit-bound"),
        "Adequacy Queue": q("Adequacy Queue",100,90,2,4,"wpu/finance/supply-bound"),
        "Fossil Retirement Queue": q("Fossil Retirement Queue",90,100,3,4,"wpu/regulatory-bound"),
        "Fossil Fallback Queue": q("Fossil Fallback Queue",80 if fossil_fallback else 0,70,1,5,"legacy/fossil-bound",closed=not fossil_fallback),
        "Materials Queue": q("Materials Queue",100,80,1,4,"supply-bound"),
        "Workforce Throughput Queue": q("Workforce Throughput Queue",100,90,1,4,"wpu-bound"),
        "Utility Revenue Stabilization Queue": q("Utility Revenue Stabilization Queue",100,85,1,4,"regulatory/finance-bound"),
        "Nuclear Fleet Stability Queue": q("Nuclear Fleet Stability Queue",100,75,1,4,"firm-clean/maintenance-bound"),
        "Emerging Market De-risking Queue": q("Emerging Market De-risking Queue",100,95,2,4,"finance/sovereign-risk-bound"),
    }

def make_fabrics(): return {"Deliverability Fabric": Fabric("Deliverability Fabric", REQUIRED), "Fossil Constraint Fabric": Fabric("Fossil Constraint Fabric", ["Fossil Fallback Queue"])}
def make_attractors():
    return [
        AttractorPattern("Reliability Panic Attractor","Adequacy Queue",BoundOutcome.FOSSIL_BOUND),
        AttractorPattern("Finance Stall Attractor","Project Finance Queue",BoundOutcome.NOACK),
        AttractorPattern("Transmission Failure Attractor","Deliverability Queue",BoundOutcome.FOSSIL_BOUND),
        AttractorPattern("Workforce Bottleneck Attractor","Workforce Throughput Queue",BoundOutcome.NOACK),
        AttractorPattern("Materials Shock Attractor","Materials Queue",BoundOutcome.NOACK),
        AttractorPattern("Utility Friction Attractor","Utility Revenue Stabilization Queue",BoundOutcome.MIXED_BOUND),
        AttractorPattern("Firm Clean Gap Attractor","Nuclear Fleet Stability Queue",BoundOutcome.FOSSIL_BOUND),
        AttractorPattern("Emerging Market Lock-in Attractor","Emerging Market De-risking Queue",BoundOutcome.FOSSIL_BOUND),
    ]
def make_identity(): return IdentityToken("Datacenter Load Identity",3,2026,REQUIRED)

def run_scenario(label, shocks=None, fossil_fallback=False, year=2028):
    queues = make_queues(fossil_fallback)
    for shock in shocks or []: shock.apply(queues)
    scheduler = SynchronizationScheduler(queues, make_fabrics(), make_attractors())
    result = DeliveryAlignmentSwitch(scheduler).bind(make_identity(), year)
    req_clear = scheduler.required_clear(result.required_queues)
    print("="*72); print(label); print("="*72)
    print(f"Identity: {result.name}")
    print(f"Temporal State: {result.temporal_state(year, req_clear).value}")
    print(f"Binding Event: {result.binding_event.value}")
    print(f"Outcome: {result.outcome.value}")
    print(f"State: {result.state.value}")
    print("Notes:")
    for note in result.notes: print(f"  - {note}")
    b = scheduler.bottlenecks()
    print("Bottlenecks:" if b else "Bottlenecks: none")
    for name, status, ratio in b: print(f"  - {name}: {status.value}, clearance={ratio:.2f}")
    c = scheduler.closed_queues()
    if c:
        print("Closed pathways:")
        for name in c: print(f"  - {name}")
    print()

def run_rebinding_demo():
    queues = make_queues(True); scheduler = SynchronizationScheduler(queues, make_fabrics(), make_attractors())
    switch = DeliveryAlignmentSwitch(scheduler)
    token = switch.bind(make_identity(), 2028)
    switch.revoke(token, "fossil fallback retired and clean-only service contract enforced")
    queues["Fossil Fallback Queue"].capacity = 0; queues["Fossil Fallback Queue"].intentionally_closed = True
    result = switch.bind(token, 2028)
    print("="*72); print("Scenario 6: revoke fossil/mixed binding and rebind clean"); print("="*72)
    print(f"Identity: {result.name}\nBinding Event: {result.binding_event.value}\nOutcome: {result.outcome.value}\nState: {result.state.value}")
    print("Notes:")
    for note in result.notes: print(f"  - {note}")
    print("History:")
    for event in result.history: print(f"  - {event}")
    print()

def run_appendix_failure_modes():
    scenarios = [
        ("B1/C2: transmission permitting and buildout failure",[ShockOperator("Permitting delay","Permitting / Authorization Queue",latency_delta=4), ShockOperator("Transmission overload","Deliverability Queue",demand_multiplier=1.7,latency_delta=2)], True),
        ("B2/C3: workforce bottleneck",[ShockOperator("Training lag","Workforce Throughput Queue",capacity_multiplier=0.45,latency_delta=3)], False),
        ("B3/C4: storage duration gap / adequacy underbuild",[ShockOperator("Storage gap","Adequacy Queue",demand_multiplier=1.8,latency_delta=2)], True),
        ("B4/C9: critical materials disruption",[ShockOperator("Materials disruption","Materials Queue",capacity_multiplier=0.35,latency_delta=3)], False),
        ("B5: utility revenue-model friction",[ShockOperator("Utility friction","Utility Revenue Stabilization Queue",capacity_multiplier=0.5,latency_delta=3)], True),
        ("B6/C10: nuclear or firm-clean fleet instability",[ShockOperator("Firm clean shock","Nuclear Fleet Stability Queue",capacity_multiplier=0.4,latency_delta=3)], True),
        ("B7/C6: emerging-market capital-cost barrier",[ShockOperator("EM WACC risk","Emerging Market De-risking Queue",capacity_multiplier=0.35,latency_delta=3)], True),
        ("C1: fossil majors block financial repricing",[ShockOperator("Fossil finance remains liquid","Project Finance Queue",capacity_multiplier=0.65,latency_delta=2)], True),
        ("C5: AI / datacenter load growth outruns clean build",[ShockOperator("Large load overshoot","Adequacy Queue",demand_multiplier=1.7), ShockOperator("Grid pressure","Deliverability Queue",demand_multiplier=1.45)], True),
        ("C7: carbon-pricing backlash / policy reset",[ShockOperator("Policy reset","Permitting / Authorization Queue",latency_delta=3), ShockOperator("Investor uncertainty","Project Finance Queue",capacity_multiplier=0.7)], True),
        ("C8: fossil asset bailouts",[ShockOperator("Bailout preserves fallback","Fossil Fallback Queue",capacity_multiplier=1.5)], True),
        ("C11: coordinated fossil retrenchment strategy",[ShockOperator("Counter-cascade","Project Finance Queue",capacity_multiplier=0.7,latency_delta=2), ShockOperator("Reliability panic","Adequacy Queue",demand_multiplier=1.5)], True),
    ]
    print("="*72); print("Appendix B/C Failure Mode Stress Tests"); print("="*72)
    for label, shocks, fossil in scenarios: run_scenario(label, shocks, fossil)

def run_biosphere_demo():
    buses = ["Land Cycle Bus","Ocean Cycle Bus","Water-Cycle Bus","Carbon-Cycle Bus","Cryosphere Feedback Bus","Ecosystem Metabolism Bus"]
    healthy = BiosphereFabric([
        BioNPU("Forest NPU",["Land Cycle Bus","Carbon-Cycle Bus","Water-Cycle Bus","Ecosystem Metabolism Bus"],BioNPUState.RESILIENT,0.82,0.76,0.71,0.84),
        BioNPU("Peatland NPU",["Land Cycle Bus","Carbon-Cycle Bus","Water-Cycle Bus","Ecosystem Metabolism Bus"],BioNPUState.RECOVERING,0.68,0.88,0.77,0.70),
        BioNPU("Kelp / Ocean NPU",["Ocean Cycle Bus","Carbon-Cycle Bus","Ecosystem Metabolism Bus"],BioNPUState.PRODUCTIVE,0.74,0.69,0.58,0.73),
        BioNPU("Glacier / Cryosphere NPU",["Cryosphere Feedback Bus","Water-Cycle Bus"],BioNPUState.PRODUCTIVE,0.62,0.52,0.81,0.64),
    ], buses)
    harmed = BiosphereFabric([
        BioNPU("Monoculture Carbon Plantation NPU",["Land Cycle Bus","Carbon-Cycle Bus"],BioNPUState.DEGRADED,0.22,0.75,0.30,0.25),
        BioNPU("Damaged Watershed NPU",["Water-Cycle Bus","Ecosystem Metabolism Bus"],BioNPUState.DISCONNECTED,0.31,0.35,0.42,0.28),
    ], buses)
    print("="*72); print("Scenario 7: Biosphere Fabric healthy nested-cycle evaluation"); print("="*72)
    print(f"BioFabric Outcome: {healthy.evaluate().value}")
    print("Notes:\n  - Biodiversity is a Bio-NPU health/resilience metric, not its own bus.\n")
    print("="*72); print("Scenario 8: Biosphere Fabric harm-bound evaluation"); print("="*72)
    print(f"BioFabric Outcome: {harmed.evaluate().value}")
    print("Notes:\n  - Carbon function alone is not enough; degraded cycle participation produces HarmBound.\n")

def run_worker_transition_demo():
    workers = [
        WorkerToken("Coal plant electrician","coal power",44,["electrical"],True,True,True,True,False),
        WorkerToken("Refinery operator near retirement","oil refining",63,["operations"],True,True,False,False,True),
        WorkerToken("Gas field contractor without transition support","gas extraction",39,["field ops"],False,False,False,False,False),
    ]
    op = WorkerTransitionOperator()
    print("="*72); print("Scenario 9: Fossil worker transition under fossil exit"); print("="*72)
    for i, worker in enumerate(workers, 1):
        result = op.transition(worker)
        print(f"Test Case {i}\nWorker: {result.name}\nState: {result.state.value}")
        for note in result.notes: print(f"  - {note}")
        print()


# =====================================================
# WEIGHTED CASCADE / APPENDIX C RANKING SEMANTICS
# =====================================================

@dataclass
class PressureToken:
    """Accumulated stress on a BioFabric bus or transition-system queue."""
    name: str
    target: str
    weight: float
    confidence: float = 1.0


@dataclass
class WeightedCascadeAttractor:
    """Thresholded attractor activated by accumulated cross-bus/queue pressure."""
    code: str
    name: str
    category: str
    trigger_targets: List[str]
    affected_targets: List[str]
    threshold: float
    likelihood: float
    consequence: float
    coupling_multiplier: float
    irreversibility: float
    confidence: float
    notes: str = ""

    def accumulated_pressure(self, pressures: List[PressureToken]) -> float:
        targets = set(self.trigger_targets + self.affected_targets)
        return sum(p.weight * p.confidence for p in pressures if p.target in targets)

    def pressure_ratio(self, pressures: List[PressureToken]) -> float:
        return 1.0 if self.threshold <= 0 else self.accumulated_pressure(pressures) / self.threshold

    def tipped(self, pressures: List[PressureToken]) -> bool:
        return self.pressure_ratio(pressures) >= 1.0

    def risk_score(self, pressures: List[PressureToken]) -> float:
        pressure_factor = min(1.5, self.pressure_ratio(pressures))
        return self.likelihood * self.consequence * self.coupling_multiplier * self.irreversibility * self.confidence * pressure_factor


def make_default_pressure_tokens() -> List[PressureToken]:
    return [
        PressureToken("fossil finance persistence", "Project Finance Queue", 1.8, 0.85),
        PressureToken("fossil fallback availability", "Fossil Fallback Queue", 1.6, 0.80),
        PressureToken("transmission congestion", "Deliverability Queue", 1.5, 0.85),
        PressureToken("storage duration gap", "Adequacy Queue", 1.4, 0.80),
        PressureToken("workforce shortage", "Workforce Throughput Queue", 1.2, 0.75),
        PressureToken("materials fragility", "Materials Queue", 1.0, 0.70),
        PressureToken("emerging market WACC stress", "Emerging Market De-risking Queue", 1.7, 0.85),
        PressureToken("utility friction", "Utility Revenue Stabilization Queue", 0.9, 0.70),
        PressureToken("firm clean instability", "Nuclear Fleet Stability Queue", 0.8, 0.65),
        PressureToken("cryosphere albedo loss", "Cryosphere Feedback Bus", 2.1, 0.80),
        PressureToken("ice-to-ocean freshwater forcing", "Ocean Cycle Bus", 1.4, 0.70),
        PressureToken("permafrost carbon feedback", "Carbon-Cycle Bus", 1.9, 0.80),
        PressureToken("tropical forest moisture stress", "Land Cycle Bus", 1.7, 0.75),
        PressureToken("water-cycle instability", "Water-Cycle Bus", 1.5, 0.70),
        PressureToken("ecosystem metabolism degradation", "Ecosystem Metabolism Bus", 1.4, 0.70),
    ]


def make_appendix_c_attractors() -> List[WeightedCascadeAttractor]:
    A = WeightedCascadeAttractor
    return [
        A("C1", "Fossil financial repricing blocked", "transition", ["Project Finance Queue", "Fossil Fallback Queue"], ["Fossil Retirement Queue"], 2.2, 0.85, 1.00, 1.25, 0.95, 0.85, "Fossil remains financeable or insurable long enough to preserve persistence pathways."),
        A("C2", "Transmission / deliverability failure", "transition", ["Deliverability Queue"], ["Adequacy Queue"], 1.2, 0.80, 0.90, 1.15, 0.75, 0.85, "Clean generation cannot become usable delivered output fast enough."),
        A("C3", "Workforce bottleneck", "transition", ["Workforce Throughput Queue"], ["Deliverability Queue", "Adequacy Queue"], 1.0, 0.70, 0.85, 1.10, 0.65, 0.75, "Execution substrate cannot clear queues inside the synchronization window."),
        A("C4", "Storage / adequacy underbuild", "transition", ["Adequacy Queue"], ["Fossil Fallback Queue"], 1.1, 0.70, 0.90, 1.20, 0.75, 0.80, "Reliability remains fossil-dependent because storage, flexibility, and firm clean lag."),
        A("C5", "AI / datacenter demand outruns clean build", "transition", ["Adequacy Queue", "Deliverability Queue"], ["Fossil Fallback Queue"], 2.0, 0.60, 0.85, 1.15, 0.65, 0.70, "New load arrives out of sequence and binds to fossil fallback."),
        A("C6", "Emerging-market fossil lock-in", "transition", ["Emerging Market De-risking Queue"], ["Project Finance Queue", "Fossil Fallback Queue"], 1.5, 0.70, 1.00, 1.25, 0.95, 0.85, "Clean capital fails to clear high-growth regions before fossil default pathways harden."),
        A("C7", "Carbon-pricing backlash / policy reset", "transition", ["Project Finance Queue", "Permitting / Authorization Queue"], ["Fossil Fallback Queue"], 1.8, 0.50, 0.70, 1.05, 0.60, 0.65, "Policy instability resets investment and authorization queues."),
        A("C8", "Fossil asset bailouts", "transition", ["Fossil Fallback Queue"], ["Project Finance Queue"], 1.0, 0.55, 0.85, 1.15, 0.75, 0.70, "Emergency support preserves fossil capacity in a zombie or fallback state."),
        A("C9", "Critical materials disruption", "transition", ["Materials Queue"], ["Deliverability Queue", "Adequacy Queue"], 0.9, 0.55, 0.70, 1.05, 0.55, 0.70, "Materials shocks slow clean buildout and storage deployment."),
        A("C10", "Nuclear / firm-clean instability", "transition", ["Nuclear Fleet Stability Queue"], ["Adequacy Queue", "Fossil Fallback Queue"], 0.7, 0.45, 0.60, 1.05, 0.50, 0.65, "Firm clean gap increases fossil fallback under reliability stress."),
        A("C11", "Coordinated fossil retrenchment strategy", "transition", ["Project Finance Queue", "Adequacy Queue", "Fossil Fallback Queue"], ["Emerging Market De-risking Queue"], 3.0, 0.55, 0.95, 1.30, 0.85, 0.70, "Fossil incumbents exploit price, reliability, and political stress to preserve lock-in."),
        A("C12", "Cryosphere albedo / ice-to-land cascade", "biosphere", ["Cryosphere Feedback Bus"], ["Ocean Cycle Bus", "Water-Cycle Bus", "Carbon-Cycle Bus"], 2.0, 0.55, 1.00, 1.45, 1.00, 0.75, "Ice loss lowers albedo, raises sea level, perturbs freshwater fluxes, and stresses ocean/water cycles."),
        A("C13", "Permafrost carbon and methane feedback", "biosphere", ["Carbon-Cycle Bus"], ["Cryosphere Feedback Bus", "Ecosystem Metabolism Bus"], 1.6, 0.55, 0.95, 1.40, 0.95, 0.75, "Permafrost thaw becomes a carbon-cycle amplifier rather than a passive consequence."),
        A("C14", "Amazon / tropical forest dieback", "biosphere", ["Land Cycle Bus", "Water-Cycle Bus"], ["Carbon-Cycle Bus", "Ecosystem Metabolism Bus"], 2.2, 0.50, 0.95, 1.35, 0.90, 0.70, "A keystone ecosystem shifts from carbon sink/resilience anchor toward fire, drought, and carbon release."),
        A("C15", "AMOC / ocean-circulation disruption", "biosphere", ["Ocean Cycle Bus"], ["Cryosphere Feedback Bus", "Water-Cycle Bus", "Ecosystem Metabolism Bus"], 1.4, 0.45, 1.00, 1.50, 0.95, 0.65, "Ocean circulation disruption changes regional climate, sea-level patterns, and biosphere stability."),
        A("C16", "Freshwater-cycle / monsoon destabilization", "biosphere", ["Water-Cycle Bus"], ["Land Cycle Bus", "Ecosystem Metabolism Bus"], 1.3, 0.45, 0.85, 1.30, 0.80, 0.60, "Hydrological instability stresses food systems, forests, watersheds, and adaptation capacity."),
        A("C17", "Compound biosphere cascade", "biosphere", ["Land Cycle Bus", "Ocean Cycle Bus", "Water-Cycle Bus", "Carbon-Cycle Bus", "Cryosphere Feedback Bus", "Ecosystem Metabolism Bus"], [], 7.0, 0.35, 1.00, 1.70, 1.00, 0.55, "Multiple BioFabric buses degrade together; failure modes stop being separable."),
    ]


def rank_appendix_c_failure_modes(pressures: List[PressureToken], limit: Optional[int] = None):
    rows = []
    for attractor in make_appendix_c_attractors():
        rows.append((
            attractor.risk_score(pressures),
            attractor.accumulated_pressure(pressures),
            attractor.pressure_ratio(pressures),
            attractor.tipped(pressures),
            attractor,
        ))
    rows.sort(key=lambda row: row[0], reverse=True)
    return rows[:limit] if limit else rows


def run_appendix_c_dynamic_ranking() -> None:
    pressures = make_default_pressure_tokens()
    ranked = rank_appendix_c_failure_modes(pressures)

    print("=" * 72)
    print("Appendix C Dynamic Ranking: Weighted Cascade Attractors")
    print("=" * 72)
    print("Ranking is heuristic and scenario-sensitive; weights are toy defaults.")
    print("Score = likelihood × consequence × coupling × irreversibility × confidence × pressure factor.")
    print()

    for rank, (score, pressure, ratio, tipped, attractor) in enumerate(ranked, start=1):
        status = "TIPPED" if tipped else "stress-accumulating"
        print(f"{rank:02d}. {attractor.code}: {attractor.name}")
        print(f"    category={attractor.category}, status={status}")
        print(f"    score={score:.3f}, pressure={pressure:.2f}, threshold={attractor.threshold:.2f}, ratio={ratio:.2f}")
        print(f"    affected={', '.join(attractor.affected_targets) if attractor.affected_targets else 'compound/all'}")
        print(f"    note: {attractor.notes}")
    print()

    print("Appendix C recommended publication set: top 15")
    for rank, (_, _, _, tipped, attractor) in enumerate(ranked[:15], start=1):
        marker = "*" if tipped else "-"
        print(f"  {rank:02d}. {marker} {attractor.code}: {attractor.name}")
    print()

if __name__ == "__main__":
    run_scenario("Scenario 1: synchronized clean delivery")
    run_scenario("Scenario 2: adequacy bottleneck triggers fossil fallback attractor", [ShockOperator("Storage / flexibility underbuild","Adequacy Queue",demand_multiplier=1.6)], True)
    run_scenario("Scenario 3: finance shock causes NoAck", [ShockOperator("WACC spike","Project Finance Queue",capacity_multiplier=0.4,latency_delta=3)])
    run_scenario("Scenario 4: stale success after TTL", year=2031)
    run_scenario("Scenario 5: mixed-bound delivery while fossil fallback remains available", fossil_fallback=True)
    run_rebinding_demo()
    run_appendix_failure_modes()
    run_biosphere_demo()
    run_appendix_c_dynamic_ranking()
    run_worker_transition_demo()
