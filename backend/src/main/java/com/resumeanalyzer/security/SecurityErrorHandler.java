package com.resumeanalyzer.security;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.resumeanalyzer.common.ApiError;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import java.io.IOException;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.http.MediaType;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.security.core.AuthenticationException;
import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.access.AccessDeniedHandler;
import org.springframework.stereotype.Component;

@Component
public class SecurityErrorHandler implements AuthenticationEntryPoint, AccessDeniedHandler {
    private final ObjectMapper objectMapper;

    public SecurityErrorHandler(ObjectMapper objectMapper) {
        this.objectMapper = objectMapper;
    }

    @Override
    public void commence(
        HttpServletRequest request,
        HttpServletResponse response,
        AuthenticationException exception
    ) throws IOException {
        write(response, request, 401, "UNAUTHORIZED", "Authentication is required to access this resource.");
    }

    @Override
    public void handle(
        HttpServletRequest request,
        HttpServletResponse response,
        AccessDeniedException exception
    ) throws IOException {
        write(
            response,
            request,
            403,
            "FORBIDDEN",
            "Access denied. Required role or resource ownership missing."
        );
    }

    private void write(
        HttpServletResponse response,
        HttpServletRequest request,
        int status,
        String code,
        String message
    ) throws IOException {
        response.setStatus(status);
        response.setContentType(MediaType.APPLICATION_JSON_VALUE);
        objectMapper.writeValue(response.getOutputStream(), new ApiError(
            Instant.now().toString(),
            status,
            code,
            message,
            request.getRequestURI(),
            Map.of(),
            UUID.randomUUID().toString()
        ));
    }
}
