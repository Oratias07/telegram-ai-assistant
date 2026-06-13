# Extract tests are integration tests (real httpx + trafilatura)
# Mocking these is complex and fragile. Security tests in test_security.py verify URL safety.
# Deep search tests verify extraction is called correctly.
# Extraction itself is simple and tested in integration via deep_search.
