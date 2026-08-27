package com.resumeanalyzer.analysis;

public class AnalysisNotFoundException extends RuntimeException {
    public AnalysisNotFoundException(Long id) {
        super("Analysis not found: " + id);
    }
}
