package com.resumeanalyzer.common;

import com.resumeanalyzer.analysis.AnalysisNotFoundException;
import com.resumeanalyzer.analysis.UnauthenticatedAnalysisRequestException;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.dao.DataAccessException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
public class ApiExceptionHandler {
    @ExceptionHandler(AnalysisNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiError handleNotFound(AnalysisNotFoundException ex, HttpServletRequest request) {
        return new ApiError(Instant.now().toString(), 404, "NOT_FOUND", ex.getMessage(), request.getRequestURI(), Map.of(), "local");
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiError handleValidation(MethodArgumentNotValidException ex, HttpServletRequest request) {
        return new ApiError(Instant.now().toString(), 400, "MALFORMED_REQUEST", "Invalid request payload.", request.getRequestURI(), Map.of(), "local");
    }

    @ExceptionHandler(UnauthenticatedAnalysisRequestException.class)
    @ResponseStatus(HttpStatus.UNAUTHORIZED)
    public ApiError handleUnauthenticated(UnauthenticatedAnalysisRequestException ex, HttpServletRequest request) {
        return new ApiError(Instant.now().toString(), 401, "UNAUTHORIZED", "Authentication is required.", request.getRequestURI(), Map.of(), "local");
    }

    @ExceptionHandler(jakarta.validation.ConstraintViolationException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiError handleConstraintViolation(jakarta.validation.ConstraintViolationException ex, HttpServletRequest request) {
        return new ApiError(Instant.now().toString(), 400, "MALFORMED_REQUEST", "Invalid request parameters.", request.getRequestURI(), Map.of(), "local");
    }

    @ExceptionHandler(DataAccessException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiError handleDataAccess(DataAccessException ex, HttpServletRequest request) {
        return new ApiError(Instant.now().toString(), 500, "INTERNAL_ERROR", "The analysis could not be processed.", request.getRequestURI(), Map.of(), "local");
    }
}
