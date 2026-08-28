package com.resumeanalyzer.analysis;

public class AnalysisForbiddenException extends RuntimeException {
    public AnalysisForbiddenException() {
        super("Access denied. Required role or resource ownership missing.");
    }
}
