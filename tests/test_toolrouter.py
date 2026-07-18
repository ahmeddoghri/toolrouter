from toolrouter.corpus import QUERIES, registry
from toolrouter.registry import ToolRegistry
from toolrouter.router import Router


def _reg():
    return registry()


def test_routes_clear_query():
    r = Router(_reg())
    result = r.route("what is the weather in paris")
    assert result.tool is not None
    assert result.tool.name == "weather"
    assert not result.abstained


def test_abstains_on_ambiguous():
    r = Router(_reg())
    result = r.route("convert this")
    assert result.abstained
    assert result.tool is None


def test_abstains_on_no_match():
    r = Router(_reg())
    result = r.route("xyzzy plugh frobnicate")
    assert result.abstained


def test_confidence_is_the_margin():
    r = Router(_reg())
    result = r.route("run a sql query on the database")
    # confidence is top minus runner-up, not the raw top score
    assert abs(result.confidence - (result.top_score - result.runner_up_score)) < 1e-9


def test_threshold_controls_abstention():
    reg = _reg()
    # "check the price" has a clear winner but a modest margin (0.5), so a very
    # strict threshold abstains on it while a loose one routes it.
    strict = Router(reg, min_confidence=0.9)
    loose = Router(reg, min_confidence=0.0)
    q = "check the price"
    assert strict.route(q).abstained
    assert not loose.route(q).abstained


def test_gating_avoids_wrong_calls_on_ambiguous():
    reg = _reg()
    always = Router(reg, min_confidence=0.0)
    gated = Router(reg, min_confidence=0.15)
    ambiguous = [q for q, t in QUERIES if t is None]
    always_wrong = sum(1 for q in ambiguous if always.route(q).tool is not None)
    gated_wrong = sum(1 for q in ambiguous if gated.route(q).tool is not None)
    assert gated_wrong < always_wrong


def test_explain_is_human_readable():
    r = Router(_reg())
    assert "ROUTE" in r.route("what is the weather").explain()
    assert "ABSTAIN" in r.route("convert this").explain()


def test_empty_registry_abstains():
    r = Router(ToolRegistry())
    assert r.route("anything").abstained


def test_clear_query_accuracy_is_high():
    r = Router(_reg())
    clear = [(q, t) for q, t in QUERIES if t is not None]
    correct = sum(1 for q, t in clear if (res := r.route(q)).tool and res.tool.name == t)
    assert correct / len(clear) >= 0.8
