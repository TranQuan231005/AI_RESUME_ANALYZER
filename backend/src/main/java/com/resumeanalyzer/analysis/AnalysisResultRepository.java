package com.resumeanalyzer.analysis;

import java.util.List;
import java.util.Optional;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.data.jpa.repository.Query;

public interface AnalysisResultRepository extends JpaRepository<AnalysisResult, Long>, JpaSpecificationExecutor<AnalysisResult> {
    Page<AnalysisResult> findByUserId(Long userId, Pageable pageable);
    Page<AnalysisResult> findByUserIdAndAnalysisType(Long userId, String analysisType, Pageable pageable);
    Optional<AnalysisResult> findByIdAndUserId(Long id, Long userId);

    long countByAnalysisType(String analysisType);
    long countByAiProvider(String aiProvider);
    long countByUsedFallback(boolean usedFallback);

    @Query("SELECT a.processingMs FROM AnalysisResult a ORDER BY a.processingMs ASC")
    List<Long> findAllProcessingMsSorted();
}
