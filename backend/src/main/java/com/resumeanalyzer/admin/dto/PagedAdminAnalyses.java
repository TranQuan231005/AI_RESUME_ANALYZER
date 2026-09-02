package com.resumeanalyzer.admin.dto;

import com.resumeanalyzer.analysis.dto.AnalysisSummaryDto;
import java.util.List;

public record PagedAdminAnalyses(
    List<AnalysisSummaryDto> items,
    int page,
    int size,
    long totalItems,
    int totalPages
) {}
