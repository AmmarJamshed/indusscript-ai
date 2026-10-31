from normalisation.signs import (
    MappingRegistry,
    normalise_sequence,
    normalise_token,
)


def test_normalise_damaged():
    assert normalise_token("...") == "[DAMAGED]"
    assert normalise_token("?") == "[DAMAGED]" or normalise_token("#") == "[DAMAGED]"


def test_uncertain_prefix():
    assert normalise_token("?abc").startswith("?")


def test_reverse_sequence():
    assert normalise_sequence(["A", "B", "C"], force_reverse=True) == ["C", "B", "A"]


def test_cross_civ_requires_approval():
    reg = MappingRegistry()
    try:
        reg.propose_cross_link("indus", "A", "egyptian", "B", "looks similar", approved=False)
        assert False, "should have raised"
    except ValueError:
        pass
    reg.propose_cross_link("indus", "A", "egyptian", "B", "explicit evidence X", approved=True)
    assert len(reg.cross_civilisation_links) == 1
