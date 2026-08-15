"""Ground Truth Sovereign Pillars — the 33-pillar library.

Scaffolded for the ItE Dashboard sovereign audit contract. Every pillar
subclasses BasePillar and implements health_check() -> (ok, detail).

Use:
    sys.path.append(r"C:\\Users\\Jan\\Documents\\AOP")
    import pillars
    classes = pillars.__load_all__()   # 33 pillar classes
"""
from __future__ import annotations

from .base import BasePillar, PIPELINE_ROOT, load_ground_truth  # noqa: F401
from .federation import (  # noqa: F401
    FederationEngine,
    SeedCouncil,
    ExpansionAssembly,
    ContinuityWardens,
    RecoveryEngine,
)
from .truth import (  # noqa: F401
    VerificationOracle,
    EvidenceLedger,
    MerkleChainKeeper,
    StateHashVerifier,
    ProvenanceAuditor,
)
from .research import (  # noqa: F401
    ResearchAcademy,
    ExplorationDivision,
    PredictionEngine,
    InnovationLab,
    KnowledgeSystem,
)
from .operations import (  # noqa: F401
    MissionScheduler,
    TaskOrchestrator,
    DeliveryIntegrator,
    MutationPolicyGate,
    FreezeController,
)
from .intelligence import (  # noqa: F401
    DataSourceRegistry,
    ConfidenceScorer,
    CouplingAnalyzer,
    PlanningEngine,
    WorkerCoordinator,
)
from .boundary import (  # noqa: F401
    ExecutionBoundary,
    GovernanceGate,
    RecoveryLedger,
    TelemetryBeacon,
    SovereignRegistrar,
)
from .xxxii_continuum import UnifiedEconomicContinuum  # noqa: F401
from .xxxiii_enterprise_value import EnterpriseValueCreation  # noqa: F401
from .xxxiv_trading import MarketTrading  # noqa: F401

ALL_PILLARS: list[type[BasePillar]] = [
    FederationEngine,
    SeedCouncil,
    ExpansionAssembly,
    ContinuityWardens,
    RecoveryEngine,
    VerificationOracle,
    EvidenceLedger,
    MerkleChainKeeper,
    StateHashVerifier,
    ProvenanceAuditor,
    ResearchAcademy,
    ExplorationDivision,
    PredictionEngine,
    InnovationLab,
    KnowledgeSystem,
    MissionScheduler,
    TaskOrchestrator,
    DeliveryIntegrator,
    MutationPolicyGate,
    FreezeController,
    DataSourceRegistry,
    ConfidenceScorer,
    CouplingAnalyzer,
    PlanningEngine,
    WorkerCoordinator,
    ExecutionBoundary,
    GovernanceGate,
    RecoveryLedger,
    TelemetryBeacon,
    SovereignRegistrar,
    UnifiedEconomicContinuum,
    EnterpriseValueCreation,
    MarketTrading,
]


def __load_all__() -> list[type[BasePillar]]:
    """Return all 34 sovereign pillar classes."""
    return list(ALL_PILLARS)


def pillar_count() -> int:
    return len(ALL_PILLARS)
