package com.resumeanalyzer.common;

import com.resumeanalyzer.analysis.AnalysisForbiddenException;
import com.resumeanalyzer.analysis.AnalysisNotFoundException;
import com.resumeanalyzer.security.UnauthenticatedException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.validation.ConstraintViolationException;
import java.time.Instant;
import java.util.Map;
import java.util.UUID;
import org.springframework.core.Ordered;
import org.springframework.core.annotation.Order;
import org.springframework.dao.DataAccessException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;

@RestControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE)
public class ApiExceptionHandler {
    @ExceptionHandler(AnalysisNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ApiError handleNotFound(AnalysisNotFoundException ex, HttpServletRequest request) {
        return error(404, "NOT_FOUND", ex.getMessage(), request);
    }

    @ExceptionHandler(AnalysisForbiddenException.class)
    @ResponseStatus(HttpStatus.FORBIDDEN)
    public ApiError handleForbidden(AnalysisForbiddenException ex, HttpServletRequest request) {
        return error(403, "FORBIDDEN", ex.getMessage(), request);
    }

    @ExceptionHandler(UnauthenticatedException.class)
    @ResponseStatus(HttpStatus.UNAUTHORIZED)
    public ApiError handleUnauthorized(UnauthenticatedException ex, HttpServletRequest request) {
        return error(401, "UNAUTHORIZED", ex.getMessage(), request);
    }

    @ExceptionHandler({
        MethodArgumentNotValidException.class,
        ConstraintViolationException.class,
        HandlerMethodValidationException.class,
        MethodArgumentTypeMismatchException.class
    })
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiError handleValidation(Exception ex, HttpServletRequest request) {
        return error(400, "MALFORMED_REQUEST", "Invalid request parameters.", request);
    }

    @ExceptionHandler(DataAccessException.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiError handleDatabaseError(DataAccessException ex, HttpServletRequest request) {
        return internalError(request);
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ApiError handleUnexpectedError(Exception ex, HttpServletRequest request) {
        return internalError(request);
    }

    private ApiError internalError(HttpServletRequest request) {
        return error(
            500,
            "INTERNAL_ERROR",
            "An internal error occurred. Please try again later.",
            request
        );
    }

    private ApiError error(int status, String code, String message, HttpServletRequest request) {
        return new ApiError(
            Instant.now().toString(),
            status,
            code,
            message,
            request.getRequestURI(),
            Map.of(),
            UUID.randomUUID().toString()
        );
    }

}
