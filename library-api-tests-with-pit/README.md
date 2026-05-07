# Library API Tests with PIT

This module now contains both the request-based library API tests and the `BookService` unit tests with PIT mutation coverage.

## What is covered

- API requests for listing, searching, and creating books
- login validation
- book search validation
- cart quantity checks
- checkout address and payment validation

## Run the tests

```bash
cd library-api-tests-with-pit
mvn test
```

## Run PIT mutation coverage

```bash
cd library-api-tests-with-pit
mvn org.pitest:pitest-maven:mutationCoverage
```

The `BookService` suite reaches 100% line coverage and 100% mutation coverage.
