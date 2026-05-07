# Project Overview

This repository contains test automation for three test areas:

1. **dr.com.tr Books / New Releases** — a live e-commerce website tested through the browser with Selenium WebDriver.
2. **Library-DB-Express** — a local Node.js / Express REST API for a library system tested with JUnit.
3. **library-api-tests-with-pit** — JUnit unit tests for `BookService` with PIT mutation coverage.

## What the project covers

### dr.com.tr

The browser tests focus on the Books / New Releases section and cover:

- book search
- search filters
- product listing and pagination
- product details
- shopping cart
- login and register flow
- checkout form validation

These tests are black-box system tests driven through Chrome.

### Library-DB-Express

The local library app provides CRUD-style API endpoints for a library database.
The tests verify:

- `GET`, `POST`, `PUT`, and `DELETE` behavior
- status codes and response bodies
- validation for missing or invalid input
- coverage and mutation testing support

## Repository contents

- `Library-DB-Express/` — the Express + SQLite library application
- `library-api-tests-with-pit/` — unit tests and PIT coverage for `BookService`
- `test_search.py`, `test_login.py`, `test_cart.py`, `test_checkout.py` — Selenium tests for dr.com.tr

## Run the projects

### Prerequisites

- Node.js and npm for `Library-DB-Express`
- Java 21+ and Maven for `library-api-tests-with-pit`
- Python 3.10+ for the Selenium tests
- Google Chrome for browser automation

### Library app

```bash
cd Library-DB-Express
npm install
npm start
```

Open the app at:

```bash
http://localhost:3000
```

### BookService + PIT tests

```bash
cd library-api-tests-with-pit
mvn test
mvn org.pitest:pitest-maven:mutationCoverage
```

This module is focused on the `BookService` class and its mutation coverage report.

### Selenium tests

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pytest
```

The Python tests rely on the packages listed in `requirements.txt`.

Some Python tests also use `config.json` for real dr.com.tr login credentials.
That file is kept out of Git because it may contain private email and password data.
If you run the login or checkout tests, add your own valid credentials locally in `config.json`.

The login and checkout flows now wait longer for CAPTCHA completion and reuse an authenticated Chrome profile plus temporary cookies so the session can carry across test files.
If you need to rerun only those scenarios, `pytest test_login.py test_checkout.py` is the fastest path.
