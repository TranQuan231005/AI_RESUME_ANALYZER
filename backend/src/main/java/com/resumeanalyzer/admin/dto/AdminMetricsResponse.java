package com.resumeanalyzer.admin.dto;

public record AdminMetricsResponse(
    long totalAnalyses,
    long resumeAnalysesCount,
    long matchAnalysesCount,
    double fallbackRate,
    double avgLatencyMs,
    double p95LatencyMs
) {}
