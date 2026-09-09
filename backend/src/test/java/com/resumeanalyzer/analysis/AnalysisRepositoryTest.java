package com.resumeanalyzer.analysis;

import static org.assertj.core.api.Assertions.assertThat;

import com.fasterxml.jackson.databind.node.JsonNodeFactory;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import jakarta.persistence.EntityManager;
import java.sql.Timestamp;
import java.time.Instant;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.orm.jpa.DataJpaTest;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.test.context.TestPropertySource;

@DataJpaTest
@TestPropertySource(properties = "spring.jpa.hibernate.ddl-auto=validate")
class AnalysisRepositoryTest {
    @Autowired
    private AnalysisResultRepository repository;

    @Autowired
    private UserRepository userRepository;

    @Autowired
    private JdbcTemplate jdbcTemplate;

    @Autowired
    private EntityManager entityManager;

    @Test
    void migrationAllowsSavingAndRetrievingEveryImportantAnalysisField() {
        User user = saveUser("owner@example.test", "Owner");
        AnalysisResult saved = repository.saveAndFlush(result(user, "RESUME", "first.pdf"));
        Long savedId = saved.getId();
        entityManager.clear();

        AnalysisResult retrieved = repository.findById(savedId).orElseThrow();

        assertThat(retrieved.getUser().getId()).isEqualTo(user.getId());
        assertThat(retrieved.getAnalysisType()).isEqualTo("RESUME");
        assertThat(retrieved.getFileName()).isEqualTo("first.pdf");
        assertThat(retrieved.getCandidateName()).isEqualTo("Synthetic Candidate");
        assertThat(retrieved.getCandidateEmail()).isEqualTo("candidate@example.test");
        assertThat(retrieved.getPredictedField()).isEqualTo("Data Science");
        assertThat(retrieved.getResumeScore()).isEqualTo(82);
        assertThat(retrieved.getMatchScore()).isEqualTo(75);
        assertThat(retrieved.getTargetRole()).isEqualTo("Data Analyst");
        assertThat(retrieved.getResultJson().get("resumeScore").asInt()).isEqualTo(82);
        assertThat(retrieved.getAiProvider()).isEqualTo("RULE_BASED");
        assertThat(retrieved.getAiModel()).isEqualTo("deterministic-v1");
        assertThat(retrieved.isUsedFallback()).isTrue();
        assertThat(retrieved.getProcessingMs()).isEqualTo(125L);
        assertThat(retrieved.getCreatedAt()).isNotNull();
    }

    @Test
    void historyIsOwnedFilteredPagedAndOrderedByCreatedAtDescending() {
        User owner = saveUser("history-owner@example.test", "History Owner");
        User other = saveUser("other-owner@example.test", "Other Owner");
        AnalysisResult oldest = repository.saveAndFlush(result(owner, "RESUME", "oldest.pdf"));
        AnalysisResult middle = repository.saveAndFlush(result(owner, "MATCH", "middle.pdf"));
        AnalysisResult newest = repository.saveAndFlush(result(owner, "RESUME", "newest.pdf"));
        repository.saveAndFlush(result(other, "RESUME", "private.pdf"));

        setCreatedAt(oldest.getId(), Instant.parse("2026-01-01T00:00:00Z"));
        setCreatedAt(middle.getId(), Instant.parse("2026-01-02T00:00:00Z"));
        setCreatedAt(newest.getId(), Instant.parse("2026-01-03T00:00:00Z"));

        PageRequest firstTwo = PageRequest.of(
            0,
            2,
            Sort.by(Sort.Direction.DESC, "createdAt")
        );
        Page<AnalysisResult> page = repository.findByUserId(owner.getId(), firstTwo);

        assertThat(page.getContent())
            .extracting(AnalysisResult::getFileName)
            .containsExactly("newest.pdf", "middle.pdf");
        assertThat(page.getTotalElements()).isEqualTo(3);
        assertThat(page.getTotalPages()).isEqualTo(2);

        Page<AnalysisResult> filtered = repository.findByUserIdAndAnalysisType(
            owner.getId(),
            "RESUME",
            PageRequest.of(0, 10, Sort.by(Sort.Direction.DESC, "createdAt"))
        );
        assertThat(filtered.getContent())
            .extracting(AnalysisResult::getFileName)
            .containsExactly("newest.pdf", "oldest.pdf");
        assertThat(filtered.getContent())
            .allMatch(item -> item.getUser().getId().equals(owner.getId()));
    }

    private User saveUser(String email, String fullName) {
        User user = new User();
        user.setEmail(email);
        user.setFullName(fullName);
        user.setPasswordHash("$2a$10$syntheticHashForPersistenceTestsOnly");
        user.setRole("USER");
        return userRepository.saveAndFlush(user);
    }

    private AnalysisResult result(User user, String type, String fileName) {
        AnalysisResult result = new AnalysisResult();
        result.setUser(user);
        result.setAnalysisType(type);
        result.setFileName(fileName);
        result.setCandidateName("Synthetic Candidate");
        result.setCandidateEmail("candidate@example.test");
        result.setPredictedField("Data Science");
        result.setResumeScore(82);
        result.setMatchScore(75);
        result.setTargetRole("Data Analyst");
        result.setResultJson(JsonNodeFactory.instance.objectNode().put("resumeScore", 82));
        result.setAiProvider("RULE_BASED");
        result.setAiModel("deterministic-v1");
        result.setUsedFallback(true);
        result.setProcessingMs(125L);
        return result;
    }

    private void setCreatedAt(Long id, Instant createdAt) {
        jdbcTemplate.update(
            "UPDATE analysis_results SET created_at = ? WHERE id = ?",
            Timestamp.from(createdAt),
            id
        );
    }
}
