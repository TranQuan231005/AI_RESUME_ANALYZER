package com.resumeanalyzer.analysis;

import com.resumeanalyzer.analysis.dto.AnalysisDetailResponse;
import com.resumeanalyzer.analysis.dto.PagedAnalysisSummary;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestHeader;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/analyses")
public class AnalysisController {
    private final AnalysisService service;

    public AnalysisController(AnalysisService service) {
        this.service = service;
    }

    @GetMapping
    public PagedAnalysisSummary history(
        @RequestHeader("X-User-Id") Long userId,
        @RequestParam(defaultValue = "0") @Min(0) int page,
        @RequestParam(defaultValue = "10") @Min(1) @Max(50) int size,
        @RequestParam(required = false) String type
    ) {
        return service.getHistory(userId, page, size, type);
    }

    @GetMapping("/{id}")
    public AnalysisDetailResponse detail(
        @RequestHeader("X-User-Id") Long userId,
        @PathVariable Long id
    ) {
        return service.getDetail(userId, id);
    }
}
