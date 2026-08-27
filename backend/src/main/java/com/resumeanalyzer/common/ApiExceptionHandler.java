package com.resumeanalyzer.common;

import com.resumeanalyzer.analysis.AnalysisNotFoundException;
import jakarta.servlet.http.HttpServletRequest;
import java.time.Instant;
import java.util.Map;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
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
}
