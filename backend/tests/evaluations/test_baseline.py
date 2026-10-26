from app.evaluations.runner import baseline


def test_known_truth_baseline():
    result = baseline()
    assert result["cases"] == 13
    assert result["classifications_correct"] == 13
    assert result["proposal_precision"] == 1
    assert result["proposal_recall"] == 1
