package com.resumeanalyzer.auth.dto;

public record LoginResponse(
    String accessToken,
    String tokenType,
    long expiresIn,
    UserDto user
) {
    @Override
    public String toString() {
        return "LoginResponse[accessToken=[REDACTED], tokenType=" + tokenType
            + ", expiresIn=" + expiresIn + ", user=" + user + "]";
    }
}
