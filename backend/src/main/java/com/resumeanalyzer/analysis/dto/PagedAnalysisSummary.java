package com.resumeanalyzer.analysis.dto;

import java.util.List;

public record PagedAnalysisSummary(
    List<AnalysisSummaryDto> items,
    int page,
    int size,
    long totalItems,
    int totalPages
) {}
