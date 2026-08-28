package com.resumeanalyzer.auth;

import com.resumeanalyzer.auth.dto.LoginRequest;
import com.resumeanalyzer.auth.dto.LoginResponse;
import com.resumeanalyzer.auth.dto.UserDto;
import com.resumeanalyzer.security.AuthenticatedUser;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api")
public class AuthController {
    private final AuthService authService;

    public AuthController(AuthService authService) {
        this.authService = authService;
    }

    @PostMapping("/auth/login")
    public LoginResponse login(@Valid @RequestBody LoginRequest request) {
        return authService.login(request);
    }

    @GetMapping("/me")
    public UserDto me(AuthenticatedUser authenticatedUser) {
        return authService.currentUser(authenticatedUser.id());
    }
}
