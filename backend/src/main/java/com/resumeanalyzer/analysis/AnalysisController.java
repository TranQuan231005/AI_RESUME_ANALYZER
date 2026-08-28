package com.resumeanalyzer.analysis;

import com.resumeanalyzer.analysis.dto.AnalysisDetailResponse;
import com.resumeanalyzer.analysis.dto.PagedAnalysisSummary;
import java.security.Principal;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/analyses")
@Validated
public class AnalysisController {
    private final AnalysisService service;

    public AnalysisController(AnalysisService service) {
        this.service = service;
    }

    @GetMapping
    public PagedAnalysisSummary history(
        Principal principal,
        @RequestParam(defaultValue = "0") @Min(0) int page,
        @RequestParam(defaultValue = "10") @Min(1) @Max(50) int size,
        @RequestParam(required = false) String type
    ) {
        return service.getHistory(authenticatedUserId(principal), page, size, type);
    }

    @GetMapping("/{id}")
    public AnalysisDetailResponse detail(
        Principal principal,
        @PathVariable Long id
    ) {
        return service.getDetail(authenticatedUserId(principal), id);
    }

    private Long authenticatedUserId(Principal principal) {
        if (principal == null) {
            throw new UnauthenticatedAnalysisRequestException();
        }
        try {
            return Long.valueOf(principal.getName());
        } catch (NumberFormatException ex) {
            throw new UnauthenticatedAnalysisRequestException();
        }
    }
}
