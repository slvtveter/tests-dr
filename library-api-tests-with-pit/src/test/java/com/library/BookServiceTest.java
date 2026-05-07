package com.library;

import org.junit.jupiter.api.Test;
import static org.junit.jupiter.api.Assertions.*;

public class BookServiceTest {

    BookService service = new BookService();

    @Test
    void testLoginCorrect() {
        boolean result = service.login("admin", "password123");
        assertTrue(result);
    }

    @Test
    void testLoginWrong() {
        boolean result = service.login("user", "123");
        assertFalse(result);
    }

    @Test
    void testSearchBook() {
        boolean result = service.searchBook("Harry Potter");
        assertTrue(result);
    }

    @Test
    void testSearchEmpty() {
        boolean result = service.searchBook("");
        assertFalse(result);
    }

    @Test
    void testCart() {
        boolean result = service.addBookToCart(2);
        assertTrue(result);
    }

    @Test
    void testCartWrong() {
        boolean result = service.addBookToCart(0);
        assertFalse(result);
    }

    @Test
    void testCheckout() {
        boolean result = service.checkout("Street 5", "Visa");
        assertTrue(result);
    }

    @Test
    void testCheckoutWrong() {
        boolean result = service.checkout("", "");
        assertFalse(result);
    }

    @Test
    void testCheckoutPaymentEmpty() {
        boolean result = service.checkout("Street 5", "");
        assertFalse(result);
    }
}