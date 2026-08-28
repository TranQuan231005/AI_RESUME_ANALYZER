package com.resumeanalyzer.auth.dto;

import com.resumeanalyzer.user.User;

public record UserDto(Long id, String email, String fullName, String role) {
    public static UserDto from(User user) {
        return new UserDto(user.getId(), user.getEmail(), user.getFullName(), user.getRole());
    }
}
