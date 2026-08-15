"""Pillar XXXII: Unified Economic Continuum — canonical research-layer reference."""

from __future__ import annotations

from pillars.xxxii_continuum import UnifiedEconomicContinuum


def continuum_equation(valuations, attentions, taus, frictions,
                       marginal_utilities, prices,
                       consumption, investment, gov_spending, exports, imports,
                       N, T):
    engine = UnifiedEconomicContinuum()
    return engine.omega_total(
        valuations=valuations,
        attentions=attentions,
        taus=taus,
        frictions=frictions,
        marginal_utilities=marginal_utilities,
        prices=prices,
        consumption=consumption,
        investment=investment,
        gov_spending=gov_spending,
        exports=exports,
        imports=imports,
        N=N,
        T=T,
    )
