package com.resumeanalyzer.security;

import java.util.Objects;

/**
 * Server-verified identity derived from a signed JWT subject.
 */
public record AuthenticatedUser(Long id) {
    public AuthenticatedUser {
        Objects.requireNonNull(id, "Authenticated user id is required.");
        if (id <= 0) {
            throw new IllegalArgumentException("Authenticated user id must be positive.");
        }
    }
}
