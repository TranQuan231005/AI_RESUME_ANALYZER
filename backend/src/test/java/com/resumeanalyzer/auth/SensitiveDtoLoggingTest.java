package com.resumeanalyzer.auth;

import static org.assertj.core.api.Assertions.assertThat;

import com.resumeanalyzer.auth.dto.LoginRequest;
import com.resumeanalyzer.auth.dto.LoginResponse;
import com.resumeanalyzer.auth.dto.UserDto;
import org.junit.jupiter.api.Test;

class SensitiveDtoLoggingTest {
    @Test
    void authDtoStringRepresentationsRedactPasswordAndToken() {
        LoginRequest request = new LoginRequest("user@example.test", "NeverLogThisPassword");
        LoginResponse response = new LoginResponse(
            "NeverLogThisToken",
            "Bearer",
            7200,
            new UserDto(1L, "user@example.test", "Demo User", "USER")
        );

        assertThat(request.toString())
            .contains("password=[REDACTED]")
            .doesNotContain("NeverLogThisPassword");
        assertThat(response.toString())
            .contains("accessToken=[REDACTED]")
            .doesNotContain("NeverLogThisToken");
    }
}
