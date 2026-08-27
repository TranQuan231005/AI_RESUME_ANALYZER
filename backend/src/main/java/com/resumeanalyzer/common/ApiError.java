package com.resumeanalyzer.common;

import java.util.Map;

public record ApiError(
    String timestamp,
    int status,
    String code,
    String message,
    String path,
    Map<String, String> fieldErrors,
    String requestId
) {}
