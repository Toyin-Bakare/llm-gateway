from llm_gateway.redact import redact


def test_email_phone_ssn():
    text, n = redact("mail bob@x.com or call 415-555-1234, ssn 123-45-6789")
    assert "[EMAIL]" in text and "[PHONE]" in text and "[SSN]" in text
    assert n == 3


def test_api_key():
    text, n = redact("key sk-abcdefghijklmnopqrstuvwxyz1234")
    assert "[API_KEY]" in text and n == 1


def test_clean_text_untouched():
    text, n = redact("build failed at step 3")
    assert text == "build failed at step 3" and n == 0
