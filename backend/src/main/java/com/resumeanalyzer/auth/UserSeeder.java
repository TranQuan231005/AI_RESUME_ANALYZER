package com.resumeanalyzer.auth;

import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.ApplicationArguments;
import org.springframework.boot.ApplicationRunner;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

@Component
@ConditionalOnProperty(name = "app.seed.enabled", havingValue = "true")
public class UserSeeder implements ApplicationRunner {
    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final SeedAccount user;
    private final SeedAccount admin;

    public UserSeeder(
        UserRepository userRepository,
        PasswordEncoder passwordEncoder,
        @Value("${app.seed.user.email}") String userEmail,
        @Value("${app.seed.user.password}") String userPassword,
        @Value("${app.seed.user.full-name}") String userFullName,
        @Value("${app.seed.admin.email}") String adminEmail,
        @Value("${app.seed.admin.password}") String adminPassword,
        @Value("${app.seed.admin.full-name}") String adminFullName
    ) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.user = new SeedAccount(userEmail, userPassword, userFullName, "USER");
        this.admin = new SeedAccount(adminEmail, adminPassword, adminFullName, "ADMIN");
    }

    @Override
    public void run(ApplicationArguments args) {
        seedIfMissing(user);
        seedIfMissing(admin);
    }

    private void seedIfMissing(SeedAccount account) {
        validate(account);
        if (userRepository.findByEmailIgnoreCase(account.email()).isPresent()) {
            return;
        }
        User entity = new User();
        entity.setEmail(account.email().trim().toLowerCase(java.util.Locale.ROOT));
        entity.setFullName(account.fullName().trim());
        entity.setPasswordHash(passwordEncoder.encode(account.password()));
        entity.setRole(account.role());
        userRepository.save(entity);
    }

    private static void validate(SeedAccount account) {
        if (account.email().isBlank() || account.password().isBlank() || account.fullName().isBlank()) {
            throw new IllegalStateException("Enabled seed accounts require email, password, and full name.");
        }
    }

    private record SeedAccount(String email, String password, String fullName, String role) {}
}
