package com.resumeanalyzer.security;

public class UnauthenticatedException extends RuntimeException {
    public UnauthenticatedException() {
        super("Authentication is required to access this resource.");
    }
}
