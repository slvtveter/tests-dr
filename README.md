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

### Library app

```bash
cd Library-DB-Express
npm install
npm start
```

### Library API tests

```bash
cd library-api-tests
mvn test
```

### Selenium tests

```bash
pytest
```
