package com.resumeanalyzer.admin;

import com.resumeanalyzer.admin.dto.AdminMetricsResponse;
import com.resumeanalyzer.admin.dto.PagedAdminAnalyses;
import com.resumeanalyzer.admin.dto.PagedUsers;
import jakarta.validation.constraints.Max;
import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.Pattern;
import org.springframework.validation.annotation.Validated;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/admin")
@Validated
public class AdminController {
    private final AdminService service;

    public AdminController(AdminService service) {
        this.service = service;
    }

    @GetMapping("/users")
    public PagedUsers getUsers(
        @RequestParam(defaultValue = "0") @Min(0) int page,
        @RequestParam(defaultValue = "10") @Min(1) @Max(50) int size
    ) {
        return service.getUsers(page, size);
    }

    @GetMapping("/analyses")
    public PagedAdminAnalyses getAnalyses(
        @RequestParam(defaultValue = "0") @Min(0) int page,
        @RequestParam(defaultValue = "10") @Min(1) @Max(50) int size,
        @RequestParam(required = false) @Pattern(regexp = "RESUME|MATCH") String type,
        @RequestParam(required = false) @Pattern(regexp = "OLLAMA|RULE_BASED") String provider,
        @RequestParam(required = false) Boolean usedFallback
    ) {
        return service.getAnalyses(page, size, type, provider, usedFallback);
    }

    @GetMapping("/metrics")
    public AdminMetricsResponse getMetrics() {
        return service.getMetrics();
    }
}
