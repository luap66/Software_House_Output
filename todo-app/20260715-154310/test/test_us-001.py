import urllib.request
import urllib.parse


BASE = "http://localhost:53889"


def _get():
    req = urllib.request.Request(BASE)
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode("utf-8")


def _post(task_text):
    data = urllib.parse.urlencode({"task": task_text}).encode()
    req = urllib.request.Request(BASE, data=data, method="POST")
    with urllib.request.urlopen(req, timeout=5) as resp:
        return resp.read().decode("utf-8")


def test_add_todo():
    """Criteria 1 & 2 & 4: page has input+button; submitting adds task to visible list; stored in memory."""

    # Criterion 1: GET / displays input field and submit button
    html = _get()
    assert 'id="todo-input"' in html, "Input field missing"
    assert 'type="submit"' in html, "Submit button missing"

    # Criterion 2 & 4: POST adds task to visible list (in-memory persistence)
    task_name = "Buy groceries"
    html_after = _post(task_name)
    assert "<li class=\"todo-item\">Buy groceries</li>" in html_after, \
        f"Task not added to visible list. Got:\n{html_after}"

    # Criterion 4: persists across requests (in-memory storage during session)
    html_second = _get()
    assert "Buy groceries" in html_second, \
        "Task disappeared on subsequent GET — not stored in memory."


def test_empty_input_validation():
    """Criterion 3: Submitting empty input shows a validation message."""

    html = _post("")
    assert 'error-message' in html and 'visible' in html, \
        f"Empty submission did not show validation. Got:\n{html}"
    # Verify the error text is present
    assert "Please enter a task." in html, \
        f"Validation message missing expected text. Got:\n{html}"
