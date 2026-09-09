package com.resumeanalyzer.analysis;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.resumeanalyzer.ai.AiServiceClient;
import com.resumeanalyzer.analysis.dto.AnalysisDetailResponse;
import com.resumeanalyzer.analysis.dto.AnalysisSummaryDto;
import com.resumeanalyzer.analysis.dto.PagedAnalysisSummary;
import com.resumeanalyzer.analysis.dto.PersistedMatchResponse;
import com.resumeanalyzer.analysis.dto.PersistedResumeAnalysisResponse;
import com.resumeanalyzer.user.User;
import com.resumeanalyzer.user.UserRepository;
import java.time.Instant;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.PageRequest;
import org.springframework.data.domain.Sort;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;
import org.springframework.web.multipart.MultipartFile;

@Service
public class AnalysisService {
    private final AnalysisResultRepository repository;
    private final UserRepository userRepository;
    private final ObjectMapper objectMapper;
    private final AiServiceClient aiServiceClient;

    public AnalysisService(
        AnalysisResultRepository repository,
        UserRepository userRepository,
        ObjectMapper objectMapper,
        AiServiceClient aiServiceClient
    ) {
        this.repository = repository;
        this.userRepository = userRepository;
        this.objectMapper = objectMapper;
        this.aiServiceClient = aiServiceClient;
    }

    @Transactional
    public PersistedResumeAnalysisResponse analyzeResume(Long userId, MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Resume file is required.");
        }
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new IllegalArgumentException("File size exceeds 5MB limit.");
        }

        User user = userRepository.findById(userId)
            .orElseThrow(() -> new IllegalArgumentException("User not found: " + userId));

        JsonNode aiResult = aiServiceClient.analyzeResume(file);

        AnalysisResult result = new AnalysisResult();
        result.setUser(user);
        result.setAnalysisType("RESUME");
        result.setFileName(truncate(aiResult.hasNonNull("fileName") ? aiResult.get("fileName").asText() : (file.getOriginalFilename() != null ? file.getOriginalFilename() : "resume.pdf"), 255));
        result.setCandidateName(truncate(aiResult.hasNonNull("candidateName") ? aiResult.get("candidateName").asText() : null, 160));
        result.setCandidateEmail(truncate(aiResult.hasNonNull("candidateEmail") ? aiResult.get("candidateEmail").asText() : null, 190));
        result.setPredictedField(truncate(aiResult.hasNonNull("predictedField") ? aiResult.get("predictedField").asText() : "Unknown", 60));
        result.setResumeScore(aiResult.hasNonNull("resumeScore") ? aiResult.get("resumeScore").asInt() : 0);
        result.setMatchScore(null);
        result.setTargetRole(null);
        result.setResultJson(aiResult);

        JsonNode aiMetadata = aiResult.get("ai");
        if (aiMetadata != null) {
            result.setAiProvider(truncate(aiMetadata.hasNonNull("provider") ? aiMetadata.get("provider").asText() : "RULE_BASED", 40));
            result.setAiModel(truncate(aiMetadata.hasNonNull("model") ? aiMetadata.get("model").asText() : "deterministic-v1", 80));
            result.setUsedFallback(aiMetadata.hasNonNull("usedFallback") && aiMetadata.get("usedFallback").asBoolean());
            result.setProcessingMs(aiMetadata.hasNonNull("processingMs") ? aiMetadata.get("processingMs").asLong() : 0L);
        } else {
            result.setAiProvider("RULE_BASED");
            result.setAiModel("deterministic-v1");
            result.setUsedFallback(true);
            result.setProcessingMs(0L);
        }

        AnalysisResult saved = repository.save(result);
        return new PersistedResumeAnalysisResponse(
            saved.getId(),
            saved.getCreatedAt() != null ? saved.getCreatedAt() : Instant.now(),
            saved.getResultJson()
        );
    }

    @Transactional
    public PersistedMatchResponse analyzeMatch(Long userId, MultipartFile file, MultipartFile jdFile, String jobDescription, String targetRole) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Resume file is required.");
        }
        if (file.getSize() > 5 * 1024 * 1024) {
            throw new IllegalArgumentException("File size exceeds 5MB limit.");
        }

        boolean hasJdFile = jdFile != null && !jdFile.isEmpty();
        boolean hasJdText = jobDescription != null && !jobDescription.trim().isEmpty();

        if (!hasJdFile && !hasJdText) {
            throw new IllegalArgumentException("Job description text (min 50 characters) or valid JD PDF file is required.");
        }

        if (hasJdFile && jdFile.getSize() > 5 * 1024 * 1024) {
            throw new IllegalArgumentException("Job description file size exceeds 5MB limit.");
        }

        if (!hasJdFile && jobDescription.trim().length() < 50) {
            throw new IllegalArgumentException("Job description must be at least 50 characters.");
        }

        User user = userRepository.findById(userId)
            .orElseThrow(() -> new IllegalArgumentException("User not found: " + userId));

        JsonNode aiResult = aiServiceClient.analyzeMatch(file, jdFile, jobDescription, targetRole);

        AnalysisResult result = new AnalysisResult();
        result.setUser(user);
        result.setAnalysisType("MATCH");
        result.setFileName(truncate(aiResult.hasNonNull("fileName") ? aiResult.get("fileName").asText() : (file.getOriginalFilename() != null ? file.getOriginalFilename() : "resume.pdf"), 255));
        result.setCandidateName(null);
        result.setCandidateEmail(null);
        result.setPredictedField(null);
        result.setResumeScore(null);
        result.setMatchScore(aiResult.hasNonNull("matchScore") ? aiResult.get("matchScore").asInt() : 0);
        result.setTargetRole(truncate(aiResult.hasNonNull("targetRole") ? aiResult.get("targetRole").asText() : (targetRole != null ? targetRole : "Unspecified Role"), 160));
        result.setResultJson(aiResult);

        JsonNode aiMetadata = aiResult.get("ai");
        if (aiMetadata != null) {
            result.setAiProvider(truncate(aiMetadata.hasNonNull("provider") ? aiMetadata.get("provider").asText() : "RULE_BASED", 40));
            result.setAiModel(truncate(aiMetadata.hasNonNull("model") ? aiMetadata.get("model").asText() : "deterministic-v1", 80));
            result.setUsedFallback(aiMetadata.hasNonNull("usedFallback") && aiMetadata.get("usedFallback").asBoolean());
            result.setProcessingMs(aiMetadata.hasNonNull("processingMs") ? aiMetadata.get("processingMs").asLong() : 0L);
        } else {
            result.setAiProvider("RULE_BASED");
            result.setAiModel("deterministic-v1");
            result.setUsedFallback(true);
            result.setProcessingMs(0L);
        }

        AnalysisResult saved = repository.save(result);
        return new PersistedMatchResponse(
            saved.getId(),
            saved.getCreatedAt() != null ? saved.getCreatedAt() : Instant.now(),
            saved.getResultJson()
        );
    }

    @Transactional
    public PersistedMatchResponse analyzeMatch(Long userId, MultipartFile file, String jobDescription, String targetRole) {
        return analyzeMatch(userId, file, null, jobDescription, targetRole);
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

    private String truncate(String val, int maxLen) {
        if (val == null) {
            return null;
        }
        String trimmed = val.trim();
        return trimmed.length() <= maxLen ? trimmed : trimmed.substring(0, maxLen);
    }
}

