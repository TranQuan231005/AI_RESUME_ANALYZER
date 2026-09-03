package com.resumeanalyzer.analysis;

import com.resumeanalyzer.analysis.dto.AnalysisDetailResponse;
import com.resumeanalyzer.analysis.dto.PagedAnalysisSummary;
import com.resumeanalyzer.analysis.dto.PersistedMatchResponse;
import com.resumeanalyzer.analysis.dto.PersistedResumeAnalysisResponse;
import com.resumeanalyzer.security.AuthenticatedUser;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/analyses")
@Validated
public class AnalysisController {
    private final AnalysisService service;

    public AnalysisController(AnalysisService service) {
        this.service = service;
    }

    @PostMapping(value = "/resume", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    public PersistedResumeAnalysisResponse analyzeResume(
        AuthenticatedUser authenticatedUser,
        @RequestParam("file") MultipartFile file
    ) {
        return service.analyzeResume(authenticatedUser.id(), file);
    }

    @PostMapping(value = "/match", consumes = MediaType.MULTIPART_FORM_DATA_VALUE)
    @ResponseStatus(HttpStatus.CREATED)
    public PersistedMatchResponse analyzeMatch(
        AuthenticatedUser authenticatedUser,
        @RequestParam("file") MultipartFile file,
        @RequestParam(value = "jdFile", required = false) MultipartFile jdFile,
        @RequestParam(value = "jobDescription", required = false) String jobDescription,
        @RequestParam(value = "targetRole", required = false) String targetRole
    ) {
        return service.analyzeMatch(authenticatedUser.id(), file, jdFile, jobDescription, targetRole);
    }

    @GetMapping
    public PagedAnalysisSummary history(
        AuthenticatedUser authenticatedUser,
        @RequestParam(defaultValue = "0") @Min(0) int page,
        @RequestParam(defaultValue = "10") @Min(1) @Max(50) int size,
        @RequestParam(required = false) @Pattern(regexp = "RESUME|MATCH") String type
    ) {
        return service.getHistory(authenticatedUser.id(), page, size, type);
    }

    @GetMapping("/{id}")
    public AnalysisDetailResponse detail(
        AuthenticatedUser authenticatedUser,
        @PathVariable Long id
    ) {
        return service.getDetail(authenticatedUser.id(), id);
    }
}
