# Library API Tests with PIT

This module contains the `BookService` unit tests plus PIT mutation testing.

## What is covered

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

The current suite reaches 100% line coverage and 100% mutation coverage for `BookService`.
