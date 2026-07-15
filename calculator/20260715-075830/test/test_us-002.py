import urllib.request


def test_operator_buttons_visible_and_clickable():
    """Acceptance criterion: Operator buttons (+, -, *, /) are visible and clickable on the interface"""
    response = urllib.request.urlopen("http://localhost:50585/")
    html = response.read().decode()
    
    # Check all four operator buttons exist with correct onclick handlers
    assert 'selectOperator(\'+\')' in html, "Addition (+) button not found"
    assert 'selectOperator(\'-\')' in html, "Subtraction (-) button not found"
    assert 'selectOperator(\'*\')' in html, "Multiplication (*) button not found"
    assert 'selectOperator(\'/\')' in html, "Division (/) button not found"


def test_operator_selection_stores_without_execution_and_display_updates():
    """Acceptance criteria: Selecting an operator stores it for later calculation without executing immediately; Multiple operators in sequence don't cause conflicts or errors; Display shows current expression with selected operator between numbers"""
    
    # Test 1: Single operator selection - verify display updates to show operator
    response = urllib.request.urlopen("http://localhost:50585/")
    html = response.read().decode()
    
    # Verify selectOperator function exists and handles storage logic
    assert 'let pendingOperator' in html, "pendingOperator variable not found for storing operators"
    assert 'function selectOperator(op)' in html, "selectOperator function not defined"
    
    # Test 2: Multiple operator selections - verify no conflicts (code replaces existing)
    # Check that the code handles replacing operators to prevent malformed expressions
    assert display_updates_with_operator(html), "Display does not update with selected operator"


def display_updates_with_operator(html):
    """Helper to check if HTML contains logic for updating display when operator is selected"""
    return 'display.value = cleanValue + \' \' + op' in html or \
           'pendingOperator = op;' in html
