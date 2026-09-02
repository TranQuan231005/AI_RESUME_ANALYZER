package com.resumeanalyzer.analysis;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.multipart;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.resumeanalyzer.analysis.dto.PersistedResumeAnalysisResponse;
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
class ResumeAnalysisControllerTest {

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
    void analyzeResumeSuccessReturns201() throws Exception {
        MockMultipartFile file = new MockMultipartFile(
            "file",
            "resume.pdf",
            "application/pdf",
            "%PDF-1.4 sample content".getBytes()
        );

        ObjectNode resultJson = objectMapper.createObjectNode();
        resultJson.put("fileName", "resume.pdf");
        resultJson.put("candidateName", "Alex Morgan");
        resultJson.put("resumeScore", 85);

        PersistedResumeAnalysisResponse response = new PersistedResumeAnalysisResponse(
            101L,
            Instant.parse("2026-08-31T12:00:00Z"),
            resultJson
        );

        when(service.analyzeResume(eq(1L), any())).thenReturn(response);

        mockMvc.perform(multipart("/api/analyses/resume").file(file))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(101))
            .andExpect(jsonPath("$.result.candidateName").value("Alex Morgan"))
            .andExpect(jsonPath("$.result.resumeScore").value(85));
    }
}
