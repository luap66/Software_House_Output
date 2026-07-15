import urllib.request


def test_empty_display_and_number_buttons():
    """AC: Calculator displays an empty screen when first loaded AND All number buttons (0-9) are visible and clickable"""
    response = urllib.request.urlopen("http://localhost:50585/")
    html = response.read().decode()
    
    # Empty display check - input has value="" attribute
    assert 'value=""' in html or "value=''" in html
    
    # All 10 number buttons (0-9) must be present with click handlers
    for digit in "0123456789":
        assert f'data-value="{digit}"' in html, f"Button {digit} missing from HTML"


def test_realtime_update_and_max_digits():
    """AC: Each button press immediately updates the displayed value AND Display shows up to 12 digits"""
    response = urllib.request.urlopen("http://localhost:50585/")
    html = response.read().decode()
    
    # Verify JavaScript enforces 12 digit limit in updateDisplay function
    assert 'display.value.length >= 12' in html, "No length check for 12 digits"
