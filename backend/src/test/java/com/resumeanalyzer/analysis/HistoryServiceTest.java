package com.resumeanalyzer.analysis;

import static org.assertj.core.api.Assertions.assertThat;
import static org.assertj.core.api.Assertions.assertThatThrownBy;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.fasterxml.jackson.databind.node.ArrayNode;
import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.fasterxml.jackson.databind.node.NullNode;
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
import org.springframework.data.domain.PageImpl;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;

class HistoryServiceTest {
    private AnalysisResultRepository repository;
    private UserRepository userRepository;
    private AnalysisService service;

    @BeforeEach
    void setUp() {
        repository = mock(AnalysisResultRepository.class);
        userRepository = mock(UserRepository.class);
        service = new AnalysisService(repository, userRepository, new ObjectMapper());
    }

    @Test
    void saveResultAssignsTheOwnerAndPreservesStoredJson() {
        User owner = user(7L);
        AnalysisResult result = result(31L, owner, "RESUME", "resume.pdf");
        when(userRepository.findById(7L)).thenReturn(Optional.of(owner));
        when(repository.save(result)).thenReturn(result);

        AnalysisResult saved = service.saveResult(7L, result);

        assertThat(saved.getUser()).isSameAs(owner);
        assertThat(saved.getResultJson().get("score").asInt()).isEqualTo(82);
        verify(result).setUser(owner);
        verify(repository).save(result);
    }

    @Test
    void historyMapsAllSummaryFieldsAndUsesDescendingCreatedAtSort() {
        User owner = user(7L);
        AnalysisResult analysis = result(31L, owner, "RESUME", "resume.pdf");
        PageRequest expectedPage = PageRequest.of(
            0,
            10,
            Sort.by(Sort.Direction.DESC, "createdAt")
        );
        when(repository.findByUserId(7L, expectedPage))
            .thenReturn(new PageImpl<>(List.of(analysis), expectedPage, 1));

        PagedAnalysisSummary response = service.getHistory(7L, 0, 10, null);

        assertThat(response.page()).isZero();
        assertThat(response.size()).isEqualTo(10);
        assertThat(response.totalItems()).isEqualTo(1);
        assertThat(response.totalPages()).isEqualTo(1);
        assertThat(response.items()).singleElement().satisfies(summary -> {
            assertThat(summary.id()).isEqualTo(31L);
            assertThat(summary.analysisType()).isEqualTo("RESUME");
            assertThat(summary.fileName()).isEqualTo("resume.pdf");
            assertThat(summary.candidateName()).isEqualTo("Synthetic Candidate");
            assertThat(summary.predictedField()).isEqualTo("Data Science");
            assertThat(summary.resumeScore()).isEqualTo(82);
            assertThat(summary.matchScore()).isEqualTo(75);
            assertThat(summary.targetRole()).isEqualTo("Data Analyst");
            assertThat(summary.aiProvider()).isEqualTo("RULE_BASED");
            assertThat(summary.usedFallback()).isTrue();
            assertThat(summary.createdAt()).isEqualTo(Instant.parse("2026-01-03T00:00:00Z"));
        });
    }

    @Test
    void historyFiltersByAnalysisTypeForTheAuthenticatedOwner() {
        PageRequest pageable = PageRequest.of(
            1,
            5,
            Sort.by(Sort.Direction.DESC, "createdAt")
        );
        when(repository.findByUserIdAndAnalysisType(7L, "MATCH", pageable))
            .thenReturn(new PageImpl<>(List.of(), pageable, 0));

        service.getHistory(7L, 1, 5, "MATCH");

        verify(repository).findByUserIdAndAnalysisType(7L, "MATCH", pageable);
    }

    @Test
    void detailReturnsEveryContractFieldForAnOwnedResult() {
        AnalysisResult analysis = result(31L, user(7L), "RESUME", "resume.pdf");
        when(repository.findByIdAndUserId(31L, 7L)).thenReturn(Optional.of(analysis));

        AnalysisDetailResponse detail = service.getDetail(7L, 31L);

        assertThat(detail.id()).isEqualTo(31L);
        assertThat(detail.analysisType()).isEqualTo("RESUME");
        assertThat(detail.fileName()).isEqualTo("resume.pdf");
        assertThat(detail.createdAt()).isEqualTo(Instant.parse("2026-01-03T00:00:00Z"));
        assertThat(detail.resultJson().get("score").asInt()).isEqualTo(82);
    }

    @Test
    void anotherUsersResultIsForbiddenWithoutReturningItsPayload() {
        when(repository.findByIdAndUserId(31L, 7L)).thenReturn(Optional.empty());
        when(repository.existsById(31L)).thenReturn(true);

        assertThatThrownBy(() -> service.getDetail(7L, 31L))
            .isInstanceOf(AnalysisForbiddenException.class)
            .hasMessage("Access denied. Required role or resource ownership missing.");
    }

    @Test
    void unknownResultIsNotFound() {
        when(repository.findByIdAndUserId(404L, 7L)).thenReturn(Optional.empty());
        when(repository.existsById(404L)).thenReturn(false);

        assertThatThrownBy(() -> service.getDetail(7L, 404L))
            .isInstanceOf(AnalysisNotFoundException.class);
    }

    @Test
    void malformedOrNonObjectStoredJsonReturnsSafeContractObject() {
        ArrayNode array = JsonNodeFactory.instance.arrayNode().add(1).add(2).add(3);
        for (var storedJson : List.of(TextNode.valueOf("not-json"), array, NullNode.instance)) {
            AnalysisResult analysis = result(31L, user(7L), "RESUME", "resume.pdf");
            when(analysis.getResultJson()).thenReturn(storedJson);
            when(repository.findByIdAndUserId(any(), any())).thenReturn(Optional.of(analysis));

            AnalysisDetailResponse detail = service.getDetail(7L, 31L);

            assertThat(detail.resultJson().isObject()).isTrue();
            assertThat(detail.resultJson().get("unavailable").asBoolean()).isTrue();
            assertThat(detail.resultJson()).isNotEqualTo(storedJson);
        }
    }

    private User user(Long id) {
        User user = mock(User.class);
        when(user.getId()).thenReturn(id);
        return user;
    }

    private AnalysisResult result(Long id, User owner, String type, String fileName) {
        AnalysisResult result = mock(AnalysisResult.class);
        when(result.getId()).thenReturn(id);
        when(result.getUser()).thenReturn(owner);
        when(result.getAnalysisType()).thenReturn(type);
        when(result.getFileName()).thenReturn(fileName);
        when(result.getCandidateName()).thenReturn("Synthetic Candidate");
        when(result.getPredictedField()).thenReturn("Data Science");
        when(result.getResumeScore()).thenReturn(82);
        when(result.getMatchScore()).thenReturn(75);
        when(result.getTargetRole()).thenReturn("Data Analyst");
        when(result.getResultJson()).thenReturn(
            JsonNodeFactory.instance.objectNode().put("score", 82)
        );
        when(result.getAiProvider()).thenReturn("RULE_BASED");
        when(result.isUsedFallback()).thenReturn(true);
        when(result.getCreatedAt()).thenReturn(Instant.parse("2026-01-03T00:00:00Z"));
        return result;
    }
}
