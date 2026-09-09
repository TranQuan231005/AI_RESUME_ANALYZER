package com.resumeanalyzer.analysis.dto;

import java.time.Instant;

public record AnalysisSummaryDto(
    Long id,
    String analysisType,
    String fileName,
    String candidateName,
    String predictedField,
    Integer resumeScore,
    Integer matchScore,
    String targetRole,
    String aiProvider,
    boolean usedFallback,
    Instant createdAt
) {}
