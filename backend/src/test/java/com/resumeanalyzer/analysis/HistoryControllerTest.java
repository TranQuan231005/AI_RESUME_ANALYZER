package com.resumeanalyzer.analysis;

import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.verifyNoInteractions;
import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.jwt;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import com.resumeanalyzer.analysis.dto.PagedAnalysisSummary;
import com.resumeanalyzer.security.AuthenticatedUserArgumentResolver;
import com.resumeanalyzer.security.SecurityConfiguration;
import com.resumeanalyzer.security.SecurityErrorHandler;
import com.resumeanalyzer.security.WebMvcConfiguration;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.WebMvcTest;
import org.springframework.boot.test.mock.mockito.MockBean;
import org.springframework.context.annotation.Import;
import org.springframework.dao.DataAccessResourceFailureException;
import org.springframework.test.web.servlet.MockMvc;

@WebMvcTest(AnalysisController.class)
@Import({
    AuthenticatedUserArgumentResolver.class,
    WebMvcConfiguration.class,
    SecurityConfiguration.class,
    SecurityErrorHandler.class
})
class HistoryControllerTest {
    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private AnalysisService service;

    @Test
    void defaultsHistoryToPageZeroAndSizeTen() throws Exception {
        when(service.getHistory(7L, 0, 10, null))
            .thenReturn(new PagedAnalysisSummary(List.of(), 0, 10, 0, 0));

        mockMvc.perform(
            get("/api/analyses")
                .with(jwt().jwt(token -> token.subject("7").claim("role", "USER")))
        )
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.page").value(0))
            .andExpect(jsonPath("$.size").value(10));

        verify(service).getHistory(7L, 0, 10, null);
    }

    @Test
    void serverVerifiedIdentityCannotBeReplacedByClientUserIdHeader() throws Exception {
        mockMvc.perform(get("/api/analyses").header("X-User-Id", "7"))
            .andExpect(status().isUnauthorized())
            .andExpect(jsonPath("$.code").value("UNAUTHORIZED"))
            .andExpect(jsonPath("$.fieldErrors").isMap())
            .andExpect(jsonPath("$.requestId").isNotEmpty());

        verifyNoInteractions(service);
    }

    @Test
    void invalidPaginationAndTypeUseMalformedRequestContract() throws Exception {
        for (String path : List.of(
            "/api/analyses?page=-1",
            "/api/analyses?size=0",
            "/api/analyses?size=51",
            "/api/analyses?type=OTHER"
        )) {
            mockMvc.perform(
                get(path).with(jwt().jwt(token -> token.subject("7").claim("role", "USER")))
            )
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.code").value("MALFORMED_REQUEST"))
                .andExpect(jsonPath("$.message").value("Invalid request parameters."));
        }
    }

    @Test
    void ownershipViolationUsesForbiddenContractWithoutResultData() throws Exception {
        when(service.getDetail(7L, 31L)).thenThrow(new AnalysisForbiddenException());

        mockMvc.perform(
            get("/api/analyses/31")
                .with(jwt().jwt(token -> token.subject("7").claim("role", "USER")))
        )
            .andExpect(status().isForbidden())
            .andExpect(jsonPath("$.code").value("FORBIDDEN"))
            .andExpect(jsonPath("$.message").value(
                "Access denied. Required role or resource ownership missing."
            ))
            .andExpect(jsonPath("$.resultJson").doesNotExist());
    }

    @Test
    void unknownAnalysisUsesNotFoundContract() throws Exception {
        when(service.getDetail(7L, 404L)).thenThrow(new AnalysisNotFoundException(404L));

        mockMvc.perform(
            get("/api/analyses/404")
                .with(jwt().jwt(token -> token.subject("7").claim("role", "USER")))
        )
            .andExpect(status().isNotFound())
            .andExpect(jsonPath("$.code").value("NOT_FOUND"));
    }

    @Test
    void databaseFailureUsesSafeInternalErrorContract() throws Exception {
        when(service.getHistory(7L, 0, 10, null)).thenThrow(
            new DataAccessResourceFailureException(
                "jdbc:mysql://internal-host/private?password=secret"
            )
        );

        mockMvc.perform(
            get("/api/analyses")
                .with(jwt().jwt(token -> token.subject("7").claim("role", "USER")))
        )
            .andExpect(status().isInternalServerError())
            .andExpect(jsonPath("$.code").value("INTERNAL_ERROR"))
            .andExpect(jsonPath("$.message").value(
                "An internal error occurred. Please try again later."
            ))
            .andExpect(jsonPath("$.message").value(
                org.hamcrest.Matchers.not(org.hamcrest.Matchers.containsString("secret"))
            ));
    }
}
