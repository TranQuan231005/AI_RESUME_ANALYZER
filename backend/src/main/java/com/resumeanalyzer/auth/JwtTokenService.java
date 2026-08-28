package com.resumeanalyzer.auth;

import com.resumeanalyzer.user.User;
import java.time.Clock;
import java.time.Instant;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.JwtClaimsSet;
import org.springframework.security.oauth2.jwt.JwtEncoder;
import org.springframework.security.oauth2.jwt.JwtEncoderParameters;
import org.springframework.security.oauth2.jwt.JwsHeader;
import org.springframework.stereotype.Service;

@Service
public class JwtTokenService {
    private final JwtEncoder encoder;
    private final Clock clock;
    private final long expirationMs;

    public JwtTokenService(
        JwtEncoder encoder,
        Clock clock,
        @Value("${app.security.jwt.expiration-ms}") long expirationMs
    ) {
        if (expirationMs <= 0) {
            throw new IllegalArgumentException("JWT expiration must be positive.");
        }
        this.encoder = encoder;
        this.clock = clock;
        this.expirationMs = expirationMs;
    }

    public IssuedToken issue(User user) {
        Instant issuedAt = clock.instant();
        Instant expiresAt = issuedAt.plusMillis(expirationMs);
        JwtClaimsSet claims = JwtClaimsSet.builder()
            .subject(user.getId().toString())
            .issuedAt(issuedAt)
            .expiresAt(expiresAt)
            .claim("email", user.getEmail())
            .claim("role", user.getRole())
            .build();
        JwsHeader headers = JwsHeader.with(MacAlgorithm.HS256).type("JWT").build();
        String value = encoder.encode(JwtEncoderParameters.from(headers, claims)).getTokenValue();
        return new IssuedToken(value, expirationMs / 1000);
    }

    public record IssuedToken(String value, long expiresInSeconds) {}
}
