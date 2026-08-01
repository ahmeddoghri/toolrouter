"""Tests for the circular benchmark, the tokenizer bug, and the fixes."""

from __future__ import annotations

from toolrouter.adversarial import ADVERSARIAL_ITEMS, HOLDOUT_ITEMS
from toolrouter.corpus import QUERIES, registry
from toolrouter.corpus_v2 import registry_v2
from toolrouter.eval_v2 import _route_all, build_report
from toolrouter.router import Router

# --- the finding: the bundled benchmark is circular -------------------------

def test_original_registry_top1_accuracy_is_poor_on_natural_queries():
    result = _route_all(registry(), ADVERSARIAL_ITEMS)
    assert result["top1_accuracy"] <= 0.4


def test_original_misses_are_abstentions_not_wrong_routes():
    """The original router never fires a wrong tool on these queries, it
    just refuses to answer most of them."""
    router = Router(registry(), min_confidence=0.15)
    wrong_routes = 0
    for item in ADVERSARIAL_ITEMS:
        r = router.route(item.query)
        if not r.abstained and r.tool.name != item.expected:
            wrong_routes += 1
    assert wrong_routes == 0


# --- the fix: vocabulary enrichment + apostrophe tokenizer bug -------------

def test_fixed_registry_gets_all_adversarial_queries_right():
    result = _route_all(registry_v2(), ADVERSARIAL_ITEMS)
    assert result["top1_accuracy"] == 1.0, result["misses"]


def test_contraction_does_not_produce_a_stray_token():
    """"what's" must not tokenize to a leftover single-letter "s" that can
    coincidentally tie against unrelated tools."""
    from toolrouter.corpus_v2 import _tokens_v2

    assert "s" not in _tokens_v2("what's the weather", drop_stopwords=True)


def test_fixed_registry_still_abstains_on_every_intentionally_ambiguous_query():
    """The vocabulary fix must not accidentally resolve a genuine tie."""
    router = Router(registry_v2(), min_confidence=0.15)
    ambiguous = [q for q, t in QUERIES if t is None]
    for q in ambiguous:
        assert router.route(q).abstained, q


def test_fixed_registry_does_not_regress_the_original_clear_queries():
    clear = [(q, t) for q, t in QUERIES if t is not None]
    router = Router(registry_v2(), min_confidence=0.15)
    correct = sum(1 for q, t in clear if (r := router.route(q)).tool and r.tool.name == t)
    assert correct == len(clear)


# --- held out, evaluated once ------------------------------------------------

def test_holdout_is_disjoint_from_the_tuning_set():
    adversarial_qs = {i.query for i in ADVERSARIAL_ITEMS}
    holdout_qs = {i.query for i in HOLDOUT_ITEMS}
    assert not (adversarial_qs & holdout_qs)


def test_holdout_fix_never_regresses_a_correct_v1_answer():
    """v2 is allowed to still miss slang it wasn't built to anticipate, but
    it must never turn a v1-correct answer into a wrong one."""
    router1 = Router(registry(), min_confidence=0.15)
    router2 = Router(registry_v2(), min_confidence=0.15)
    for item in HOLDOUT_ITEMS:
        r1 = router1.route(item.query)
        g1 = "ABSTAIN" if r1.abstained else r1.tool.name
        if g1 == item.expected:
            r2 = router2.route(item.query)
            g2 = "ABSTAIN" if r2.abstained else r2.tool.name
            assert g2 == item.expected, item.query


# --- the original benchmark is unaffected -----------------------------------

def test_original_registry_module_untouched():
    import toolrouter.registry as registry_module

    assert not hasattr(registry_module, "ToolRegistryV2")


def test_original_benchmark_still_reproduces():
    from toolrouter.eval import run as run_original

    reg = registry()
    clear = [(q, t) for q, t in QUERIES if t is not None]
    ambiguous = [(q, t) for q, t in QUERIES if t is None]

    always = Router(reg, min_confidence=0.0)
    a_correct = sum(1 for q, t in clear if (r := always.route(q)).tool and r.tool.name == t)
    a_wrong = sum(1 for q, _ in ambiguous if always.route(q).tool is not None)
    assert a_correct == len(clear)
    assert a_wrong == len(ambiguous)

    gated = Router(reg, min_confidence=0.15)
    b_correct = sum(1 for q, t in clear if (r := gated.route(q)).tool and r.tool.name == t)
    b_wrong = sum(1 for q, _ in ambiguous if gated.route(q).tool is not None)
    assert b_correct == len(clear)
    assert b_wrong == 0

    run_original()  # smoke test: must not raise


# --- the full report ---------------------------------------------------------

def test_report_is_reproducible():
    assert build_report() == build_report()


def test_report_shows_v2_beating_v1_on_adversarial():
    report = build_report()
    assert report["adversarial"]["v2"]["top1_accuracy"] > report["adversarial"]["v1"]["top1_accuracy"]
