# Project Overview

This repository contains test automation for two applications:

1. **dr.com.tr Books / New Releases** — a live e-commerce website tested through the browser with Selenium WebDriver.
2. **Library-DB-Express** — a local Node.js / Express REST API for a library system tested with JUnit.

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
- `library-api-tests/` — JUnit tests for the library API
- `test_search.py`, `test_login.py`, `test_cart.py`, `test_checkout.py` — Selenium tests for dr.com.tr

## Run the projects

### Prerequisites

- Node.js and npm for `Library-DB-Express`
- Java 17+ and Maven for `library-api-tests`
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

### Library API tests

In a second terminal, after the app is running:

```bash
cd library-api-tests
mvn test
```

This project already uses `pom.xml` for Java dependencies, so no extra Java requirements file is needed.

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
