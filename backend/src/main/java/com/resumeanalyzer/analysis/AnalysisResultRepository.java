package com.resumeanalyzer.analysis;

import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

public interface AnalysisResultRepository extends JpaRepository<AnalysisResult, Long> {
    Page<AnalysisResult> findByUserId(Long userId, Pageable pageable);
    Page<AnalysisResult> findByUserIdAndAnalysisType(Long userId, String analysisType, Pageable pageable);
    Optional<AnalysisResult> findByIdAndUserId(Long id, Long userId);
}
