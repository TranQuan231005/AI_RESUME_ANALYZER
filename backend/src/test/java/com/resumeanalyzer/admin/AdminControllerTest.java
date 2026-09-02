package com.resumeanalyzer.admin;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyBoolean;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.resumeanalyzer.admin.dto.AdminMetricsResponse;
import com.resumeanalyzer.admin.dto.PagedAdminAnalyses;
import com.resumeanalyzer.admin.dto.PagedUsers;
import com.resumeanalyzer.analysis.dto.AnalysisSummaryDto;
import com.resumeanalyzer.auth.dto.UserDto;
import com.resumeanalyzer.security.AuthenticatedUserArgumentResolver;
import com.resumeanalyzer.security.SecurityConfiguration;
import com.resumeanalyzer.security.SecurityErrorHandler;
import com.resumeanalyzer.security.WebMvcConfiguration;
import java.time.Instant;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.security.test.context.support.WithMockUser;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(controllers = AdminController.class)
@Import({
    SecurityConfiguration.class,
    SecurityErrorHandler.class,
    WebMvcConfiguration.class
})
class AdminControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AdminService service;

    @MockBean
    private AuthenticatedUserArgumentResolver userResolver;

    @Test
    @WithMockUser(username = "1", roles = "USER")
    void nonAdminGetsForbiddenForMetrics() throws Exception {
        mockMvc.perform(get("/api/admin/metrics"))
            .andExpect(status().isForbidden());
    }

    @Test
    @WithMockUser(username = "2", roles = "ADMIN")
    void adminCanGetMetrics() throws Exception {
        AdminMetricsResponse metrics = new AdminMetricsResponse(
            50L,
            30L,
            20L,
            0.05,
            345.5,
            620.0
        );
        when(service.getMetrics()).thenReturn(metrics);

        mockMvc.perform(get("/api/admin/metrics"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.totalAnalyses").value(50))
            .andExpect(jsonPath("$.resumeAnalysesCount").value(30))
            .andExpect(jsonPath("$.fallbackRate").value(0.05));
    }

    @Test
    @WithMockUser(username = "2", roles = "ADMIN")
    void adminCanGetUsers() throws Exception {
        PagedUsers users = new PagedUsers(
            List.of(new UserDto(1L, "admin@test.com", "Admin User", "ADMIN")),
            0,
            10,
            1L,
            1
        );
        when(service.getUsers(anyInt(), anyInt())).thenReturn(users);

        mockMvc.perform(get("/api/admin/users"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.totalItems").value(1))
            .andExpect(jsonPath("$.items[0].email").value("admin@test.com"));
    }

    @Test
    @WithMockUser(username = "2", roles = "ADMIN")
    void adminCanGetAnalyses() throws Exception {
        PagedAdminAnalyses analyses = new PagedAdminAnalyses(
            List.of(new AnalysisSummaryDto(
                1L,
                "RESUME",
                "resume.pdf",
                "Alex",
                "Web Development",
                85,
                null,
                null,
                "OLLAMA",
                false,
                Instant.parse("2026-08-31T12:00:00Z")
            )),
            0,
            10,
            1L,
            1
        );
        when(service.getAnalyses(anyInt(), anyInt(), any(), any(), any())).thenReturn(analyses);

        mockMvc.perform(get("/api/admin/analyses"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.totalItems").value(1))
            .andExpect(jsonPath("$.items[0].fileName").value("resume.pdf"));
    }
}
