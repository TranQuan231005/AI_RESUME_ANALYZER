package com.resumeanalyzer.analysis;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.http.MediaType;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.test.web.servlet.MvcResult;
import org.springframework.transaction.annotation.Transactional;

@SpringBootTest
@AutoConfigureMockMvc
@Transactional
class HistoryJwtIntegrationTest {
    @Autowired private MockMvc mockMvc;
    @Autowired private ObjectMapper objectMapper;
    @Autowired private UserRepository userRepository;
    @Autowired private AnalysisResultRepository analysisRepository;
    @Autowired private PasswordEncoder passwordEncoder;

    private User userA;
    private User userB;
    private AnalysisResult userBAnalysis;

    @BeforeEach
    void persistOwnedHistory() {
        userA = saveUser("user-a@example.test", "User A", "PasswordA@123");
        userB = saveUser("user-b@example.test", "User B", "PasswordB@123");
        analysisRepository.saveAndFlush(result(userA, "owned-by-a.pdf"));
        userBAnalysis = analysisRepository.saveAndFlush(result(userB, "private-to-b.pdf"));
    }

    @Test
    void loginTokenControlsHistoryEvenWhenClientSpoofsAnotherUserHeader() throws Exception {
        String token = login("user-a@example.test", "PasswordA@123");

        mockMvc.perform(get("/api/analyses")
                .header("Authorization", "Bearer " + token)
                .header("X-User-Id", userB.getId()))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.totalItems").value(1))
            .andExpect(jsonPath("$.items.length()").value(1))
            .andExpect(jsonPath("$.items[0].fileName").value("owned-by-a.pdf"));
    }

    @Test
    void userATokenCannotReadUserBAnalysisDetail() throws Exception {
        String token = login("user-a@example.test", "PasswordA@123");

        mockMvc.perform(get("/api/analyses/{id}", userBAnalysis.getId())
                .header("Authorization", "Bearer " + token))
            .andExpect(status().isForbidden())
            .andExpect(jsonPath("$.code").value("FORBIDDEN"))
            .andExpect(jsonPath("$.message").value(
                "Access denied. Required role or resource ownership missing."
            ))
            .andExpect(jsonPath("$.resultJson").doesNotExist());
    }

    private String login(String email, String password) throws Exception {
        MvcResult response = mockMvc.perform(post("/api/auth/login")
                .contentType(MediaType.APPLICATION_JSON)
                .content(objectMapper.writeValueAsString(new Credentials(email, password))))
            .andExpect(status().isOk())
            .andReturn();
        return objectMapper.readTree(response.getResponse().getContentAsString())
            .path("accessToken")
            .asText();
    }

    private User saveUser(String email, String fullName, String password) {
        User user = new User();
        user.setEmail(email);
        user.setFullName(fullName);
        user.setPasswordHash(passwordEncoder.encode(password));
        user.setRole("USER");
        return userRepository.saveAndFlush(user);
    }

    private AnalysisResult result(User owner, String fileName) {
        AnalysisResult result = new AnalysisResult();
        result.setUser(owner);
        result.setAnalysisType("RESUME");
        result.setFileName(fileName);
        result.setCandidateName("Synthetic Candidate");
        result.setResumeScore(80);
        result.setResultJson(JsonNodeFactory.instance.objectNode().put("resumeScore", 80));
        result.setAiProvider("RULE_BASED");
        result.setAiModel("deterministic-v1");
        result.setUsedFallback(false);
        result.setProcessingMs(100L);
        return result;
    }

    private record Credentials(String email, String password) {}
}
