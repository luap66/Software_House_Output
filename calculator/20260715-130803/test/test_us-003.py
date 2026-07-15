import urllib.request
import re


def test_clear_button_and_behavior():
    """Verify Clear button visibility, input/result clearing, and no-refresh reset."""
    url = "http://localhost:57951/"

    # Fetch the page
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=5) as resp:
        html = resp.read().decode("utf-8")

    # Criterion 1: A 'Clear' or 'Reset' button is visible on the interface.
    assert re.search(r'<button[^>]*id="clearBtn"[^>]*>(Clear|Reset)</button>', html), \
        "Clear/Reset button not found in HTML"

    # Criterion 2 & 3: Clicking the button empties all input fields and clears result display.
    # The JS handler must exist to clear num1, num2, reset operation, and remove results.
    assert 'document.getElementById(\'clearBtn\').addEventListener' in html, \
        "Clear button click handler not found"
    assert "document.getElementById('num1').value = ''" in html, \
        "JS does not clear num1 input"
    assert "document.getElementById('num2').value = ''" in html, \
        "JS does not clear num2 input"
    assert "document.getElementById('operation').value = 'add'" in html, \
        "JS does not reset operation to default"
    assert '.result' in html and 'remove()' in html, \
        "JS does not remove result display area"

    # Criterion 4: Calculator returns to initial ready state without requiring a page refresh.
    # The clear button is type="button" (not "submit"), so it performs client-side clearing
    # without triggering a form POST or navigation — satisfying the no-refresh requirement.
    assert re.search(r'<button[^>]*type="button"[^>]*id="clearBtn"', html), \
        "Clear button must be type='button' to avoid page refresh"
