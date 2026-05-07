package com.library;

public class BookService {

    public boolean login(String username, String password) {
        if(username.equals("admin") && password.equals("password123")) {
            return true;
        }
        return false;
    }

    public boolean searchBook(String name) {
        if(name.isEmpty()) {
            return false;
        }
        return true;
    }

    public boolean addBookToCart(int amount) {
        if(amount > 0) {
            return true;
        }
        return false;
    }

    public boolean checkout(String address, String payment) {
        if(address.isEmpty()) {
            return false;
        }
        if(payment.isEmpty()) {
            return false;
        }
        return true;
    }
}