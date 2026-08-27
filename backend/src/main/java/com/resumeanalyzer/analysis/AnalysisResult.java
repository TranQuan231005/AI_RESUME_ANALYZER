package com.resumeanalyzer.analysis;

import com.resumeanalyzer.user.User;
import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.FetchType;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import jakarta.persistence.JoinColumn;
import jakarta.persistence.Lob;
import jakarta.persistence.ManyToOne;
import jakarta.persistence.Table;
import java.time.Instant;

@Entity
@Table(name = "analysis_results")
public class AnalysisResult {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "user_id")
    private User user;

    @Column(name = "analysis_type", nullable = false, length = 20)
    private String analysisType;

    @Column(name = "file_name", nullable = false)
    private String fileName;

    @Column(name = "candidate_name")
    private String candidateName;

    @Column(name = "candidate_email")
    private String candidateEmail;

    @Column(name = "predicted_field")
    private String predictedField;

    @Column(name = "resume_score")
    private Integer resumeScore;

    @Column(name = "match_score")
    private Integer matchScore;

    @Column(name = "target_role")
    private String targetRole;

    @Lob
    @Column(name = "result_json", nullable = false, columnDefinition = "json")
    private String resultJson;

    @Column(name = "ai_provider", nullable = false)
    private String aiProvider;

    @Column(name = "ai_model", nullable = false)
    private String aiModel;

    @Column(name = "used_fallback", nullable = false)
    private boolean usedFallback;

    @Column(name = "processing_ms", nullable = false)
    private long processingMs;

    @Column(name = "created_at", nullable = false, insertable = false, updatable = false)
    private Instant createdAt;

    public Long getId() { return id; }
    public User getUser() { return user; }
    public void setUser(User user) { this.user = user; }
    public String getAnalysisType() { return analysisType; }
    public void setAnalysisType(String analysisType) { this.analysisType = analysisType; }
    public String getFileName() { return fileName; }
    public void setFileName(String fileName) { this.fileName = fileName; }
    public String getCandidateName() { return candidateName; }
    public void setCandidateName(String candidateName) { this.candidateName = candidateName; }
    public String getCandidateEmail() { return candidateEmail; }
    public void setCandidateEmail(String candidateEmail) { this.candidateEmail = candidateEmail; }
    public String getPredictedField() { return predictedField; }
    public void setPredictedField(String predictedField) { this.predictedField = predictedField; }
    public Integer getResumeScore() { return resumeScore; }
    public void setResumeScore(Integer resumeScore) { this.resumeScore = resumeScore; }
    public Integer getMatchScore() { return matchScore; }
    public void setMatchScore(Integer matchScore) { this.matchScore = matchScore; }
    public String getTargetRole() { return targetRole; }
    public void setTargetRole(String targetRole) { this.targetRole = targetRole; }
    public String getResultJson() { return resultJson; }
    public void setResultJson(String resultJson) { this.resultJson = resultJson; }
    public String getAiProvider() { return aiProvider; }
    public void setAiProvider(String aiProvider) { this.aiProvider = aiProvider; }
    public String getAiModel() { return aiModel; }
    public void setAiModel(String aiModel) { this.aiModel = aiModel; }
    public boolean isUsedFallback() { return usedFallback; }
    public void setUsedFallback(boolean usedFallback) { this.usedFallback = usedFallback; }
    public long getProcessingMs() { return processingMs; }
    public void setProcessingMs(long processingMs) { this.processingMs = processingMs; }
    public Instant getCreatedAt() { return createdAt; }
}
