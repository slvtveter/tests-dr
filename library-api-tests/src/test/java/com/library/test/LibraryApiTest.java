package com.library.test;

import org.junit.jupiter.api.AfterAll;
import org.junit.jupiter.api.BeforeAll;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

public class LibraryApiTest {

    private static final String BASE_URL = "http://localhost:3000";
    private HttpClient client;

    // Paths for database seeding
    private static final Path DB_PATH = Paths.get("../Library-DB-Express/library.db");
    private static final Path DB_BACKUP_PATH = Paths.get("../Library-DB-Express/library.db.backup");

    @BeforeAll
    public static void setupDatabaseBackup() throws IOException {
        // Create a backup of the current database before tests start
        if (Files.exists(DB_PATH)) {
            Files.copy(DB_PATH, DB_BACKUP_PATH, StandardCopyOption.REPLACE_EXISTING);
            System.out.println("Created database backup.");
        }
    }

    @AfterAll
    public static void restoreDatabase() throws IOException {
        // Restore the original database after all tests are done
        if (Files.exists(DB_BACKUP_PATH)) {
            Files.copy(DB_BACKUP_PATH, DB_PATH, StandardCopyOption.REPLACE_EXISTING);
            Files.delete(DB_BACKUP_PATH);
            System.out.println("Restored database from backup.");
        }
    }

    @BeforeEach
    public void setup() {
        client = HttpClient.newBuilder()
                .version(HttpClient.Version.HTTP_1_1)
                .build();
    }

    @Test
    public void testGetBooks_ReturnsStatus200() throws IOException, InterruptedException {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/books"))
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        assertEquals(200, response.statusCode());
        assertTrue(response.body().contains("Books"));
    }

    @Test
    public void testSearchBooks_ValidQuery() throws IOException, InterruptedException {
        // App uses /books?search=query
        String query = URLEncoder.encode("Harry", StandardCharsets.UTF_8);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/books?search=" + query))
                .GET()
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        assertEquals(200, response.statusCode());
        // Since we don't know exact DB contents, we just check if the page loads and form is there
        assertTrue(response.body().contains("Search"));
    }

    @Test
    public void testCreateBook_ValidData_Redirects() throws IOException, InterruptedException {
        String formData = "title=" + URLEncoder.encode("Test Book", StandardCharsets.UTF_8) +
                "&author=" + URLEncoder.encode("Test Author", StandardCharsets.UTF_8) +
                "&genre=" + URLEncoder.encode("Testing", StandardCharsets.UTF_8) +
                "&year=2024";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/books/new"))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(formData))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        // Express res.redirect sends a 302 Found
        assertEquals(302, response.statusCode());
        assertEquals("/books", response.headers().firstValue("Location").orElse(""));
    }

    @Test
    public void testCreateBook_MissingTitle_ReturnsValidationErrors() throws IOException, InterruptedException {
        // Missing title field
        String formData = "author=" + URLEncoder.encode("Test Author", StandardCharsets.UTF_8) +
                "&year=2024";

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/books/new"))
                .header("Content-Type", "application/x-www-form-urlencoded")
                .POST(HttpRequest.BodyPublishers.ofString(formData))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());

        // It should render the form again with a 200 OK
        assertEquals(200, response.statusCode());
        assertTrue(response.body().contains("error")); // Contains error messages
    }
}