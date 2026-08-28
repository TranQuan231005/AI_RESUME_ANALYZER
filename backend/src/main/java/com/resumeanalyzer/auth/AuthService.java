package com.resumeanalyzer.auth;

import com.resumeanalyzer.auth.dto.LoginRequest;
import com.resumeanalyzer.auth.dto.LoginResponse;
import com.resumeanalyzer.auth.dto.UserDto;
import com.resumeanalyzer.security.UnauthenticatedException;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenService jwtTokenService;

    public AuthService(
        UserRepository userRepository,
        PasswordEncoder passwordEncoder,
        JwtTokenService jwtTokenService
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.jwtTokenService = jwtTokenService;
    }

    public LoginResponse login(LoginRequest request) {
        User user = userRepository.findByEmailIgnoreCase(request.email().trim())
            .filter(candidate -> passwordEncoder.matches(request.password(), candidate.getPasswordHash()))
            .orElseThrow(InvalidCredentialsException::new);
        JwtTokenService.IssuedToken token = jwtTokenService.issue(user);
        return new LoginResponse(token.value(), "Bearer", token.expiresInSeconds(), UserDto.from(user));
    }

    public UserDto currentUser(Long userId) {
        return userRepository.findById(userId)
            .map(UserDto::from)
            .orElseThrow(UnauthenticatedException::new);
    }
}
