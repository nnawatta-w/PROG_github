from implementation import analyze_scores


def test_normal_scores():
    scores = [80, 70, 90]
    result = analyze_scores(scores)

    assert result["count"] == 3
    assert result["average"] == 80
    assert result["highest"] == 90
    assert result["lowest"] == 70

    print("Normal score test passed")


def test_decimal_scores():
    scores = [75.5, 80.5, 90]
    result = analyze_scores(scores)

    assert result["count"] == 3
    assert result["average"] == 82
    assert result["highest"] == 90
    assert result["lowest"] == 75.5

    print("Decimal score test passed")


test_normal_scores()
test_decimal_scores()