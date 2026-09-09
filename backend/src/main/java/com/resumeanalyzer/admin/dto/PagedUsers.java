package com.resumeanalyzer.admin.dto;

import com.resumeanalyzer.auth.dto.UserDto;
import java.util.List;

public record PagedUsers(
    List<UserDto> items,
    int page,
    int size,
    long totalItems,
    int totalPages
) {}
