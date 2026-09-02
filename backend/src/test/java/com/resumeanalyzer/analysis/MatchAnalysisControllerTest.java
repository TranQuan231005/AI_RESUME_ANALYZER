package com.resumeanalyzer.analysis;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.resumeanalyzer.analysis.dto.PersistedMatchResponse;
import com.resumeanalyzer.security.AuthenticatedUser;
import com.resumeanalyzer.security.AuthenticatedUserArgumentResolver;
import com.resumeanalyzer.security.SecurityConfiguration;
import com.resumeanalyzer.security.SecurityErrorHandler;
import com.resumeanalyzer.security.WebMvcConfiguration;
import java.time.Instant;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(controllers = AnalysisController.class)
@Import({
    SecurityConfiguration.class,
    SecurityErrorHandler.class,
    WebMvcConfiguration.class
})
class MatchAnalysisControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AnalysisService service;

    @MockBean
    private AuthenticatedUserArgumentResolver userResolver;

    private final ObjectMapper objectMapper = new ObjectMapper();

    @BeforeEach
    void setUp() {
        when(userResolver.supportsParameter(any())).thenCallRealMethod();
        when(userResolver.resolveArgument(any(), any(), any(), any()))
            .thenReturn(new AuthenticatedUser(1L));
    }

    @Test
    @WithMockUser(username = "1", roles = "USER")
    void analyzeMatchSuccessReturns201() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
            "file",
            "resume.pdf",
            "application/pdf",
            "%PDF-1.4 sample content".getBytes()
        );

        ObjectNode resultJson = objectMapper.createObjectNode();
        resultJson.put("fileName", "resume.pdf");
        resultJson.put("targetRole", "Senior Java Engineer");
        resultJson.put("matchScore", 90);

        PersistedMatchResponse response = new PersistedMatchResponse(
            102L,
            Instant.parse("2026-08-31T12:00:00Z"),
            resultJson
        );

        when(service.analyzeMatch(eq(1L), any(), eq("We are looking for a Senior Java Engineer with 5+ years experience in Spring Boot, MySQL, Docker, and REST APIs."), eq("Senior Java Engineer")))
            .thenReturn(response);

        mockMvc.perform(multipart("/api/analyses/match")
                .file(file)
                .param("jobDescription", "We are looking for a Senior Java Engineer with 5+ years experience in Spring Boot, MySQL, Docker, and REST APIs.")
                .param("targetRole", "Senior Java Engineer"))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(102))
            .andExpect(jsonPath("$.result.targetRole").value("Senior Java Engineer"))
            .andExpect(jsonPath("$.result.matchScore").value(90));
    }
}
