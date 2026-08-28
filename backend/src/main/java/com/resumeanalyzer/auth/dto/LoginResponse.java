package com.resumeanalyzer.auth.dto;

public record LoginResponse(
    String accessToken,
    String tokenType,
    long expiresIn,
    UserDto user
) {}
