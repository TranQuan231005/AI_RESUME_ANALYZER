package com.resumeanalyzer.analysis;

import static org.assertj.core.api.Assertions.assertThat;

import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import java.util.List;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;

@DataJpaTest
class AnalysisResultRepositoryTest {
    @Autowired
    private AnalysisResultRepository repository;

    @Autowired
    private UserRepository userRepository;

    @Test
    void savesAllImportantFieldsAndReadsStoredJson() {
        User user = user("owner@example.com");
        AnalysisResult result = result(user, "RESUME", "cv.pdf");
        result.setCandidateName("Alex Nguyen");
        result.setCandidateEmail("alex@example.com");
        result.setPredictedField("TECHNOLOGY");
        result.setResumeScore(91);
        result.setAiProvider("RULE_BASED");
        result.setAiModel("deterministic-v1");
        result.setUsedFallback(true);
        result.setProcessingMs(740);
        result.setResultJson("{\"score\":91,\"skills\":[\"Java\"]}");

        AnalysisResult saved = repository.saveAndFlush(result);
        AnalysisResult loaded = repository.findById(saved.getId()).orElseThrow();

        assertThat(loaded.getUser().getId()).isEqualTo(user.getId());
        assertThat(loaded.getAnalysisType()).isEqualTo("RESUME");
        assertThat(loaded.getFileName()).isEqualTo("cv.pdf");
        assertThat(loaded.getCandidateName()).isEqualTo("Alex Nguyen");
        assertThat(loaded.getCandidateEmail()).isEqualTo("alex@example.com");
        assertThat(loaded.getPredictedField()).isEqualTo("TECHNOLOGY");
        assertThat(loaded.getResumeScore()).isEqualTo(91);
        assertThat(loaded.getResultJson()).contains("Java");
        assertThat(loaded.getAiProvider()).isEqualTo("RULE_BASED");
        assertThat(loaded.getAiModel()).isEqualTo("deterministic-v1");
        assertThat(loaded.isUsedFallback()).isTrue();
        assertThat(loaded.getProcessingMs()).isEqualTo(740);
        assertThat(loaded.getCreatedAt()).isNotNull();
    }

    @Test
    void filtersByOwnerAndAnalysisTypeWithDefaultPagination() {
        User owner = user("owner@example.com");
        User other = user("other@example.com");
        repository.saveAllAndFlush(List.of(
            result(owner, "RESUME", "resume-1.pdf"),
            result(owner, "MATCH", "resume-2.pdf"),
            result(other, "RESUME", "private.pdf")
        ));

        Page<AnalysisResult> page = repository.findByUserIdAndAnalysisType(
            owner.getId(),
            "RESUME",
            PageRequest.of(0, 10, Sort.by(Sort.Order.desc("createdAt"), Sort.Order.desc("id")))
        );

        assertThat(page.getNumber()).isZero();
        assertThat(page.getSize()).isEqualTo(10);
        assertThat(page.getTotalElements()).isEqualTo(1);
        assertThat(page.getContent()).extracting(AnalysisResult::getFileName)
            .containsExactly("resume-1.pdf");
    }

    @Test
    void returnsOnlyOwnerRecordsInDescendingCreationOrder() {
        User owner = user("owner@example.com");
        User other = user("other@example.com");
        AnalysisResult first = repository.saveAndFlush(result(owner, "RESUME", "older.pdf"));
        AnalysisResult second = repository.saveAndFlush(result(owner, "MATCH", "newer.pdf"));
        repository.saveAndFlush(result(other, "RESUME", "private.pdf"));

        Page<AnalysisResult> page = repository.findByUserId(
            owner.getId(),
            PageRequest.of(0, 10, Sort.by(Sort.Order.desc("createdAt"), Sort.Order.desc("id")))
        );

        assertThat(page.getTotalElements()).isEqualTo(2);
        assertThat(page.getContent()).extracting(AnalysisResult::getId)
            .containsExactly(second.getId(), first.getId());
        assertThat(page.getContent()).allMatch(item -> item.getUser().getId().equals(owner.getId()));
    }

    @Test
    void detailLookupCannotCrossOwnerBoundary() {
        User owner = user("owner@example.com");
        User other = user("other@example.com");
        AnalysisResult result = repository.saveAndFlush(result(owner, "RESUME", "private.pdf"));

        assertThat(repository.findByIdAndUserId(result.getId(), owner.getId())).isPresent();
        assertThat(repository.findByIdAndUserId(result.getId(), other.getId())).isEmpty();
    }

    private User user(String email) {
        User user = new User();
        user.setEmail(email);
        user.setFullName("Test User");
        user.setPasswordHash("hash");
        user.setRole("USER");
        return userRepository.saveAndFlush(user);
    }

    private AnalysisResult result(User user, String type, String fileName) {
        AnalysisResult result = new AnalysisResult();
        result.setUser(user);
        result.setAnalysisType(type);
        result.setFileName(fileName);
        result.setResultJson("{\"ok\":true}");
        result.setAiProvider("RULE_BASED");
        result.setAiModel("deterministic-v1");
        result.setProcessingMs(10);
        return result;
    }
}
