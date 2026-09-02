package com.resumeanalyzer.admin;

import com.resumeanalyzer.admin.dto.AdminMetricsResponse;
import com.resumeanalyzer.admin.dto.PagedAdminAnalyses;
import com.resumeanalyzer.admin.dto.PagedUsers;
import com.resumeanalyzer.analysis.AnalysisResult;
import com.resumeanalyzer.analysis.AnalysisResultRepository;
import com.resumeanalyzer.analysis.dto.AnalysisSummaryDto;
import com.resumeanalyzer.auth.dto.UserDto;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import java.util.List;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

@Service
public class AdminService {
    private final UserRepository userRepository;
    private final AnalysisResultRepository analysisRepository;

    public AdminService(
        UserRepository userRepository,
        AnalysisResultRepository analysisRepository
    ) {
        this.userRepository = userRepository;
        this.analysisRepository = analysisRepository;
    }

    public PagedUsers getUsers(int page, int size) {
        PageRequest pageable = PageRequest.of(page, size, Sort.by("id").ascending());
        Page<User> usersPage = userRepository.findAll(pageable);
        return new PagedUsers(
            usersPage.map(UserDto::from).toList(),
            usersPage.getNumber(),
            usersPage.getSize(),
            usersPage.getTotalElements(),
            usersPage.getTotalPages()
        );
    }

    public PagedAdminAnalyses getAnalyses(
        int page,
        int size,
        String type,
        String provider,
        Boolean usedFallback
    ) {
        Specification<AnalysisResult> spec = Specification.where(null);
        if (type != null && !type.isBlank()) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("analysisType"), type));
        }
        if (provider != null && !provider.isBlank()) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("aiProvider"), provider));
        }
        if (usedFallback != null) {
            spec = spec.and((root, query, cb) -> cb.equal(root.get("usedFallback"), usedFallback));
        }

        PageRequest pageable = PageRequest.of(
            page,
            size,
            Sort.by(Sort.Order.desc("createdAt"), Sort.Order.desc("id"))
        );
        Page<AnalysisResult> results = analysisRepository.findAll(spec, pageable);

        return new PagedAdminAnalyses(
            results.map(this::toSummary).toList(),
            results.getNumber(),
            results.getSize(),
            results.getTotalElements(),
            results.getTotalPages()
        );
    }

    public AdminMetricsResponse getMetrics() {
        long total = analysisRepository.count();
        long resumeCount = analysisRepository.countByAnalysisType("RESUME");
        long matchCount = analysisRepository.countByAnalysisType("MATCH");
        long fallbackCount = analysisRepository.countByUsedFallback(true);
        double fallbackRate = total > 0 ? (double) fallbackCount / total : 0.0;

        List<Long> latencies = analysisRepository.findAllProcessingMsSorted();
        double avgLatency = 0.0;
        double p95Latency = 0.0;

        if (!latencies.isEmpty()) {
            long sum = 0;
            for (Long lat : latencies) {
                sum += (lat != null ? lat : 0L);
            }
            avgLatency = (double) sum / latencies.size();
            int p95Index = (int) Math.ceil(0.95 * latencies.size()) - 1;
            if (p95Index < 0) p95Index = 0;
            if (p95Index >= latencies.size()) p95Index = latencies.size() - 1;
            p95Latency = latencies.get(p95Index) != null ? latencies.get(p95Index) : 0.0;
        }

        return new AdminMetricsResponse(
            total,
            resumeCount,
            matchCount,
            Math.round(fallbackRate * 1000.0) / 1000.0,
            Math.round(avgLatency * 100.0) / 100.0,
            Math.round(p95Latency * 100.0) / 100.0
        );
    }

    private AnalysisSummaryDto toSummary(AnalysisResult result) {
        return new AnalysisSummaryDto(
            result.getId(),
            result.getAnalysisType(),
            result.getFileName(),
            result.getCandidateName(),
            result.getPredictedField(),
            result.getResumeScore(),
            result.getMatchScore(),
            result.getTargetRole(),
            result.getAiProvider(),
            result.isUsedFallback(),
            result.getCreatedAt()
        );
    }
}
