package com.resumeanalyzer.common;

import com.resumeanalyzer.ai.AiServiceException;
import com.resumeanalyzer.ai.InvalidPdfException;
import com.resumeanalyzer.analysis.AnalysisForbiddenException;
import com.resumeanalyzer.analysis.AnalysisNotFoundException;
import com.resumeanalyzer.auth.InvalidCredentialsException;
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
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestControllerAdvice;
import org.springframework.web.method.annotation.HandlerMethodValidationException;
import org.springframework.web.method.annotation.MethodArgumentTypeMismatchException;
import org.springframework.web.multipart.MaxUploadSizeExceededException;

@RestControllerAdvice
@Order(Ordered.HIGHEST_PRECEDENCE)
public class ApiExceptionHandler {
    @ExceptionHandler(InvalidCredentialsException.class)
    @ResponseStatus(HttpStatus.UNAUTHORIZED)
    public ApiError handleInvalidCredentials(InvalidCredentialsException ex, HttpServletRequest request) {
        return error(401, "BAD_CREDENTIALS", ex.getMessage(), request);
    }

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

    @ExceptionHandler(InvalidPdfException.class)
    @ResponseStatus(HttpStatus.UNPROCESSABLE_ENTITY)
    public ApiError handleInvalidPdf(InvalidPdfException ex, HttpServletRequest request) {
        return error(422, "INVALID_PDF", ex.getMessage(), request);
    }

    @ExceptionHandler(MaxUploadSizeExceededException.class)
    @ResponseStatus(HttpStatus.PAYLOAD_TOO_LARGE)
    public ApiError handlePayloadTooLarge(MaxUploadSizeExceededException ex, HttpServletRequest request) {
        return error(413, "FILE_TOO_LARGE", "File size exceeds the 5MB limit.", request);
    }

    @ExceptionHandler(AiServiceException.class)
    @ResponseStatus(HttpStatus.BAD_GATEWAY)
    public ApiError handleAiServiceError(AiServiceException ex, HttpServletRequest request) {
        return error(502, "AI_SERVICE_ERROR", "AI service is currently unavailable or failed to process.", request);
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ApiError handleIllegalArgument(IllegalArgumentException ex, HttpServletRequest request) {
        if (ex.getMessage() != null && ex.getMessage().contains("5MB")) {
            return error(413, "FILE_TOO_LARGE", ex.getMessage(), request);
        }
        if (ex.getMessage() != null && ex.getMessage().contains("50 characters")) {
            return error(422, "JD_REQUIRED", ex.getMessage(), request);
        }
        return error(400, "MALFORMED_REQUEST", ex.getMessage(), request);
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
