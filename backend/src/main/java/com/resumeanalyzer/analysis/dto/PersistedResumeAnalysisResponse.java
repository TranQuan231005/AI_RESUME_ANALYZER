package com.resumeanalyzer.analysis.dto;

import com.fasterxml.jackson.databind.JsonNode;
import java.time.Instant;

public record PersistedResumeAnalysisResponse(
    Long id,
    Instant createdAt,
    JsonNode result
) {}
