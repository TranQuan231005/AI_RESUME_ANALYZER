package com.resumeanalyzer.analysis;

public class UnauthenticatedAnalysisRequestException extends RuntimeException {
    public UnauthenticatedAnalysisRequestException() {
        super("Authenticated user identity is required.");
    }
}