package com.resumeanalyzer.security;

import java.util.Objects;

/**
 * Server-verified identity attached to a request by the authentication layer.
 * Clients cannot populate servlet request attributes through HTTP headers.
 */
public record AuthenticatedUser(Long id) {
    public static final String REQUEST_ATTRIBUTE = AuthenticatedUser.class.getName();

    public AuthenticatedUser {
        Objects.requireNonNull(id, "Authenticated user id is required.");
        if (id <= 0) {
            throw new IllegalArgumentException("Authenticated user id must be positive.");
        }
    }
}
