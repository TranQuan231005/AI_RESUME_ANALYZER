package com.resumeanalyzer.analysis;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.resumeanalyzer.analysis.dto.AnalysisDetailResponse;
import com.resumeanalyzer.analysis.dto.AnalysisSummaryDto;
import com.resumeanalyzer.analysis.dto.PagedAnalysisSummary;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service
public class AnalysisService {
    private final AnalysisResultRepository repository;
    private final UserRepository userRepository;
    private final ObjectMapper objectMapper;

    public AnalysisService(
        AnalysisResultRepository repository,
        UserRepository userRepository,
        ObjectMapper objectMapper
    ) {
        this.repository = repository;
        this.userRepository = userRepository;
        this.objectMapper = objectMapper;
    }

    @Transactional
    public AnalysisResult saveResult(Long userId, AnalysisResult result) {
        User user = userRepository.findById(userId)
            .orElseThrow(() -> new IllegalArgumentException("User not found: " + userId));
        result.setUser(user);
        return repository.save(result);
    }

    public PagedAnalysisSummary getHistory(Long userId, int page, int size, String type) {
        PageRequest pageable = PageRequest.of(
            page,
            size,
            Sort.by(Sort.Order.desc("createdAt"), Sort.Order.desc("id"))
        );
        Page<AnalysisResult> results = type == null || type.isBlank()
            ? repository.findByUserId(userId, pageable)
            : repository.findByUserIdAndAnalysisType(userId, type, pageable);

        return new PagedAnalysisSummary(
            results.map(this::toSummary).toList(),
            results.getNumber(),
            results.getSize(),
            results.getTotalElements(),
            results.getTotalPages()
        );
    }

    public AnalysisDetailResponse getDetail(Long userId, Long id) {
        AnalysisResult result = repository.findByIdAndUserId(id, userId).orElse(null);
        if (result == null) {
            if (repository.existsById(id)) {
                throw new AnalysisForbiddenException();
            }
            throw new AnalysisNotFoundException(id);
        }
        return new AnalysisDetailResponse(
            result.getId(),
            result.getAnalysisType(),
            result.getFileName(),
            result.getCreatedAt(),
            parseJson(result.getResultJson())
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

    private JsonNode parseJson(JsonNode json) {
        if (json != null && json.isObject()) {
            return json;
        }
        return objectMapper.createObjectNode().put("unavailable", true);
    }
}
