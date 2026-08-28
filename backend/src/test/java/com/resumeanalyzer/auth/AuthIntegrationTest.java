package com.resumeanalyzer.auth;

import static org.assertj.core.api.Assertions.assertThat;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import java.time.Duration;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.security.oauth2.jwt.JwtDecoder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class AuthIntegrationTest {
    @Autowired private MockMvc mockMvc;
    @Autowired private ObjectMapper objectMapper;
    @Autowired private UserRepository userRepository;
    @Autowired private PasswordEncoder passwordEncoder;
    @Autowired private JwtDecoder jwtDecoder;

    private User user;

    @BeforeEach
    void saveUser() {
        user = new User();
        user.setEmail("user@example.test");
        user.setFullName("Demo User");
        user.setPasswordHash(passwordEncoder.encode("User@123456"));
        user.setRole("USER");
        user = userRepository.saveAndFlush(user);
        assertThat(user.getPasswordHash()).startsWith("$2a$12$");
    }

    @Test
    void loginIsCaseInsensitiveAndTokenAuthenticatesMe() throws Exception {
        MvcResult login = mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email":"USER@EXAMPLE.TEST","password":"User@123456"}
                    """))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.tokenType").value("Bearer"))
            .andExpect(jsonPath("$.expiresIn").value(7200))
            .andExpect(jsonPath("$.user.id").value(user.getId()))
            .andExpect(jsonPath("$.user.email").value("user@example.test"))
            .andExpect(jsonPath("$.user.fullName").value("Demo User"))
            .andExpect(jsonPath("$.user.role").value("USER"))
            .andReturn();

        JsonNode loginBody = objectMapper.readTree(login.getResponse().getContentAsString());
        String token = loginBody.path("accessToken").asText();
        Jwt jwt = jwtDecoder.decode(token);

        assertThat(jwt.getSubject()).isEqualTo(user.getId().toString());
        assertThat(jwt.getClaimAsString("email")).isEqualTo("user@example.test");
        assertThat(jwt.getClaimAsString("role")).isEqualTo("USER");
        assertThat(Duration.between(jwt.getIssuedAt(), jwt.getExpiresAt())).isEqualTo(Duration.ofHours(2));

        mockMvc.perform(get("/api/me").header("Authorization", "Bearer " + token))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.id").value(user.getId()))
            .andExpect(jsonPath("$.email").value("user@example.test"))
            .andExpect(jsonPath("$.role").value("USER"));
    }

    @Test
    void invalidCredentialsUseSafeFrozenErrorContract() throws Exception {
        mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email":"user@example.test","password":"wrong-password"}
                    """))
            .andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.code").value("BAD_CREDENTIALS"))
            .andExpect(jsonPath("$.message").value("Invalid email or password."))
            .andExpect(jsonPath("$.fieldErrors").isMap())
            .andExpect(jsonPath("$.requestId").isNotEmpty())
            .andExpect(jsonPath("$.password").doesNotExist())
            .andExpect(jsonPath("$.accessToken").doesNotExist());
    }

    @Test
    void unsignedClientIdentityCannotAuthenticate() throws Exception {
        mockMvc.perform(get("/api/me").header("X-User-Id", user.getId()))
            .andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
            .andExpect(jsonPath("$.message").value("Authentication is required to access this resource."));
    }

    @Test
    void userTokenCannotAccessAdminApi() throws Exception {
        MvcResult login = mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"email":"user@example.test","password":"User@123456"}
                    """))
            .andExpect(status().isOk())
            .andReturn();
        String token = objectMapper.readTree(login.getResponse().getContentAsString())
            .path("accessToken")
            .asText();

        mockMvc.perform(get("/api/admin/system").header("Authorization", "Bearer " + token))
            .andExpect(status().isForbidden())
            .andExpect(jsonPath("$.code").value("FORBIDDEN"))
            .andExpect(jsonPath("$.accessToken").doesNotExist());
    }
}
