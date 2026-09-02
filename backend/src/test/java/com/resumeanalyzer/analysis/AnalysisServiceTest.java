package com.resumeanalyzer.analysis;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.eq;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.TextNode;
import com.resumeanalyzer.analysis.dto.AnalysisDetailResponse;
import com.resumeanalyzer.analysis.dto.PagedAnalysisSummary;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import java.time.Instant;
import java.util.List;
import java.util.Optional;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.ArgumentCaptor;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;

@ExtendWith(MockitoExtension.class)
class AnalysisServiceTest {
    @Mock
    private AnalysisResultRepository repository;

    @Mock
    private UserRepository userRepository;

    @Mock
    private com.resumeanalyzer.ai.AiServiceClient aiServiceClient;

    private AnalysisService service;

    @BeforeEach
    void setUp() {
        service = new AnalysisService(repository, userRepository, new ObjectMapper(), aiServiceClient);
    }

    @Test
    void saveResultAssignsOwnerBeforePersisting() {
        User user = new User();
        AnalysisResult result = result("RESUME");
        when(userRepository.findById(7L)).thenReturn(Optional.of(user));
        when(repository.save(result)).thenReturn(result);

        assertThat(service.saveResult(7L, result)).isSameAs(result);
        assertThat(result.getUser()).isSameAs(user);
        verify(repository).save(result);
    }

    @Test
    void getHistoryUsesRequestedPageAndTypeAndMapsSummary() {
        AnalysisResult result = result("MATCH");
        result.setFileName("resume.pdf");
        result.setTargetRole("Backend Engineer");
        result.setMatchScore(82);
        when(repository.findByUserIdAndAnalysisType(any(Long.class), any(String.class), any(PageRequest.class)))
            .thenReturn(new PageImpl<>(List.of(result)));

        PagedAnalysisSummary history = service.getHistory(7L, 2, 5, "MATCH");

        ArgumentCaptor<PageRequest> pageable = ArgumentCaptor.forClass(PageRequest.class);
        verify(repository).findByUserIdAndAnalysisType(
            eq(7L),
            eq("MATCH"),
            pageable.capture()
        );
        assertThat(pageable.getValue()).isEqualTo(
            PageRequest.of(2, 5, Sort.by(Sort.Order.desc("createdAt"), Sort.Order.desc("id")))
        );
        assertThat(history.page()).isEqualTo(0);
        assertThat(history.size()).isEqualTo(1);
        assertThat(history.totalItems()).isEqualTo(1);
        assertThat(history.items().get(0).analysisType()).isEqualTo("MATCH");
        assertThat(history.items().get(0).matchScore()).isEqualTo(82);
    }

    @Test
    void getDetailOnlyReturnsRecordOwnedByCaller() {
        AnalysisResult result = result("RESUME");
        when(repository.findByIdAndUserId(11L, 7L)).thenReturn(Optional.of(result));

        AnalysisDetailResponse detail = service.getDetail(7L, 11L);

        verify(repository).findByIdAndUserId(11L, 7L);
        assertThat(detail.analysisType()).isEqualTo("RESUME");
        assertThat(detail.resultJson().get("score").asInt()).isEqualTo(91);
    }

    @Test
    void getDetailHidesRecordOwnedByAnotherUser() {
        when(repository.findByIdAndUserId(11L, 7L)).thenReturn(Optional.empty());
        when(repository.existsById(11L)).thenReturn(true);

        assertThatThrownBy(() -> service.getDetail(7L, 11L))
            .isInstanceOf(AnalysisForbiddenException.class);
    }

    @Test
    void getDetailReturnsMalformedStoredJsonAsSafeRawValue() {
        AnalysisResult result = result("RESUME");
        result.setResultJson(TextNode.valueOf("not-json"));
        when(repository.findByIdAndUserId(11L, 7L)).thenReturn(Optional.of(result));

        AnalysisDetailResponse detail = service.getDetail(7L, 11L);

        assertThat(detail.resultJson().get("unavailable").asBoolean()).isTrue();
    }

    private AnalysisResult result(String type) {
        AnalysisResult result = new AnalysisResult();
        result.setAnalysisType(type);
        result.setFileName("cv.pdf");
        result.setResultJson(JsonNodeFactory.instance.objectNode().put("score", 91));
        result.setAiProvider("RULE_BASED");
        result.setAiModel("deterministic-v1");
        result.setProcessingMs(10);
        return result;
    }
}
