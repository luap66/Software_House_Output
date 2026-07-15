import urllib.request
import urllib.parse


BASE = "http://localhost:57951"


def test_ui_structure():
    """Criteria 1 & 2: Interface displays two numeric input fields and operation dropdown."""
    req = urllib.request.Request(BASE)
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")

    # Criterion 1: Two numeric input fields (num1, num2)
    assert 'id="num1"' in html, "Missing Number 1 input field"
    assert 'id="num2"' in html, "Missing Number 2 input field"
    assert 'input type="number"' in html, "Inputs are not numeric type"

    # Criterion 2: Dropdown with add, subtract, multiply options
    assert '<select id="operation"' in html, "Missing operation dropdown"
    assert 'value="add"' in html, "Missing Addition option"
    assert 'value="subtract"' in html, "Missing Subtraction option"
    assert 'value="multiply"' in html, "Missing Multiplication option"


def test_calculate_and_error_handling():
    """Criteria 3, 4 & 5: Calculate button processes inputs; correct result displayed; empty inputs show error."""

    # Criterion 3 & 4: POST with valid inputs returns correct results for each operation
    cases = [
        ("10", "5", "add", "15"),
        ("10", "5", "subtract", "5"),
        ("10", "5", "multiply", "50"),
    ]
    for num1, num2, op, expected in cases:
        data = urllib.parse.urlencode({"num1": num1, "num2": num2, "operation": op}).encode()
        req = urllib.request.Request(BASE, data=data, method="POST")
        with urllib.request.urlopen(req) as resp:
            html = resp.read().decode("utf-8")

        assert f'Result:</strong> {expected}' in html, (
            f"Expected result '{expected}' for {num1} {op} {num2}, but got unexpected output"
        )
        # Criterion 3: Calculate button triggers processing — verified by POST returning a result page

    # Criterion 5: Empty inputs show error message
    data = b"num1=&num2=&operation=add"
    req = urllib.request.Request(BASE, data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")

    assert 'class="result error"' in html, "Empty inputs did not produce an error result block"
    assert "Please enter both numbers" in html, "Error message for empty inputs is missing or incorrect"
