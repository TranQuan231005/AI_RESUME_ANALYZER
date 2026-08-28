package com.resumeanalyzer.auth;

import static org.assertj.core.api.Assertions.assertThat;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.times;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import java.util.Optional;
import org.junit.jupiter.api.Test;
import org.mockito.ArgumentCaptor;
import org.springframework.boot.ApplicationArguments;
import org.springframework.security.crypto.password.PasswordEncoder;

class UserSeederTest {
    @Test
    void repeatedRunsKeepExistingAccountsAndCreateEachMissingAccountOnce() {
        UserRepository repository = mock(UserRepository.class);
        PasswordEncoder encoder = mock(PasswordEncoder.class);
        User existingUser = new User();
        User savedAdmin = new User();
        when(repository.findByEmailIgnoreCase("user@example.test"))
            .thenReturn(Optional.of(existingUser));
        when(repository.findByEmailIgnoreCase("admin@example.test"))
            .thenReturn(Optional.empty(), Optional.of(savedAdmin));
        when(encoder.encode("Admin@123456")).thenReturn("bcrypt-admin-hash");
        UserSeeder seeder = new UserSeeder(
            repository,
            encoder,
            "user@example.test",
            "User@123456",
            "Demo User",
            "admin@example.test",
            "Admin@123456",
            "Demo Admin"
        );

        seeder.run(mock(ApplicationArguments.class));
        seeder.run(mock(ApplicationArguments.class));

        ArgumentCaptor<User> created = ArgumentCaptor.forClass(User.class);
        verify(repository, times(1)).save(created.capture());
        assertThat(created.getValue().getEmail()).isEqualTo("admin@example.test");
        assertThat(created.getValue().getFullName()).isEqualTo("Demo Admin");
        assertThat(created.getValue().getPasswordHash()).isEqualTo("bcrypt-admin-hash");
        assertThat(created.getValue().getRole()).isEqualTo("ADMIN");
        verify(encoder, times(1)).encode("Admin@123456");
    }
}
