import urllib.request
import urllib.parse

BASE = "http://localhost:57951"


def test_division_option_and_by_zero():
    """AC1: Interface includes division option. AC2: Dividing by zero shows error."""
    # GET home page — verify division option exists in the select
    with urllib.request.urlopen(f"{BASE}/") as resp:
        html = resp.read().decode("utf-8")
    assert '<option value="divide"' in html, "Division option missing from interface"

    # POST division by zero — expect error message
    data = urllib.parse.urlencode({"num1": "5", "num2": "0", "operation": "divide"}).encode()
    req = urllib.request.Request(f"{BASE}/", data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8")
    assert "Division by zero is not allowed" in html


def test_invalid_input_validation():
    """AC3: Non-numeric input triggers validation error. AC4: No crash (HTTP 200)."""
    data = urllib.parse.urlencode({"num1": "abc", "num2": "xyz", "operation": "divide"}).encode()
    req = urllib.request.Request(f"{BASE}/", data=data, method="POST")
    with urllib.request.urlopen(req) as resp:
        assert resp.status == 200, "Server crashed on invalid input"
        html = resp.read().decode("utf-8")
    assert "Invalid input" in html or "Please enter both numbers" in html
