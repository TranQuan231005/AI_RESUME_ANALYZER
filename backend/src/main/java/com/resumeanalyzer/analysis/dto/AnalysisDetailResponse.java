package com.resumeanalyzer.analysis.dto;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Instant;

public record AnalysisDetailResponse(
    Long id,
    String analysisType,
    String fileName,
    Instant createdAt,
    JsonNode resultJson
) {}
