"""Rental property: vacancy risk, tenant risk, and condition-based valuation."""
import random

from eldoria.models import PopulationTier, RentalProperty
from eldoria.world import real_estate


def _prop(**overrides) -> RentalProperty:
    base = dict(location_id="1_1", location_name="Testville", purchase_price=1000)
    base.update(overrides)
    return RentalProperty(**base)


def test_no_event_before_a_full_cycle_elapses():
    prop = _prop(last_event_tick=0)
    updated, lines, gold = real_estate.process_cycle(prop, real_estate.EVENT_CYCLE_TICKS - 1, random.Random(1))
    assert updated == prop
    assert lines == []
    assert gold == 0


def test_vacant_property_can_gain_a_tenant_or_stay_vacant():
    prop = _prop(last_event_tick=0)
    got_tenant = False
    stayed_vacant = False
    for seed in range(50):
        updated, lines, gold = real_estate.process_cycle(prop, real_estate.EVENT_CYCLE_TICKS, random.Random(seed))
        assert gold == 0, "moving in or staying vacant never itself pays out gold"
        if updated.is_occupied:
            got_tenant = True
        else:
            stayed_vacant = True
    assert got_tenant and stayed_vacant, "both outcomes must be reachable -- vacancy is a real, recurring risk"


def test_condemned_property_earns_nothing_until_repaired():
    prop = _prop(condition=0, last_event_tick=0, tenant_name="Someone", tenant_quality="good")
    updated, lines, gold = real_estate.process_cycle(prop, real_estate.EVENT_CYCLE_TICKS, random.Random(1))
    assert gold == 0
    assert updated.is_condemned
    assert any("condemned" in line for line in lines)


def test_purchase_price_scales_with_settlement_wealth_and_danger():
    village_price = real_estate.purchase_price_for(PopulationTier.COUNTRYSIDE, 1)
    city_price = real_estate.purchase_price_for(PopulationTier.CITY, 1)
    assert city_price > village_price
    assert real_estate.purchase_price_for(PopulationTier.CITY, 5) > real_estate.purchase_price_for(PopulationTier.CITY, 1)


def test_sell_price_rewards_good_condition_over_neglect():
    pristine = _prop(condition=100)
    ruined = _prop(condition=10)
    assert real_estate.sell_price(pristine) > real_estate.sell_price(ruined)


def test_repair_cost_scales_with_how_much_condition_is_missing():
    lightly_worn = _prop(condition=90)
    heavily_worn = _prop(condition=10)
    assert real_estate.repair_cost(heavily_worn) > real_estate.repair_cost(lightly_worn)
    assert real_estate.repair_cost(_prop(condition=100)) == 0
