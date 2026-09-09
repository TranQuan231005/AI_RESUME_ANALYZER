package com.resumeanalyzer.ai;

import com.fasterxml.jackson.databind.JsonNode;
import java.io.IOException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.core.io.ByteArrayResource;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.util.LinkedMultiValueMap;
import org.springframework.util.MultiValueMap;
import org.springframework.web.client.HttpClientErrorException;
import org.springframework.web.client.HttpServerErrorException;
import org.springframework.web.client.ResourceAccessException;
import org.springframework.web.client.RestClient;
import org.springframework.web.multipart.MultipartFile;

@Component
public class AiServiceClient {
    private final RestClient restClient;

    public AiServiceClient(@Value("${app.ai-service.base-url:http://localhost:8000}") String baseUrl) {
        this.restClient = RestClient.builder().baseUrl(baseUrl).build();
    }

    public JsonNode analyzeResume(MultipartFile file) {
        try {
            ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename() != null ? file.getOriginalFilename() : "resume.pdf";
                }
            };

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", fileResource);

            return restClient.post()
                .uri("/api/analyze-resume")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(body)
                .retrieve()
                .body(JsonNode.class);
        } catch (HttpClientErrorException ex) {
            if (ex.getStatusCode() == HttpStatus.UNPROCESSABLE_ENTITY) {
                throw new InvalidPdfException("Unprocessable PDF file: invalid format, encrypted, or empty text.");
            }
            if (ex.getStatusCode() == HttpStatus.PAYLOAD_TOO_LARGE) {
                throw new IllegalArgumentException("File size exceeds 5MB limit.");
            }
            throw new AiServiceException("AI service failed with status " + ex.getStatusCode(), ex);
        } catch (HttpServerErrorException | ResourceAccessException ex) {
            throw new AiServiceException("AI service failed to process request: " + ex.getMessage(), ex);
        } catch (IOException ex) {
            throw new InvalidPdfException("Failed to read uploaded PDF: " + ex.getMessage());
        }
    }

    public JsonNode analyzeMatch(MultipartFile file, MultipartFile jdFile, String jobDescription, String targetRole) {
        try {
            ByteArrayResource fileResource = new ByteArrayResource(file.getBytes()) {
                @Override
                public String getFilename() {
                    return file.getOriginalFilename() != null ? file.getOriginalFilename() : "resume.pdf";
                }
            };

            MultiValueMap<String, Object> body = new LinkedMultiValueMap<>();
            body.add("file", fileResource);

            if (jdFile != null && !jdFile.isEmpty()) {
                ByteArrayResource jdResource = new ByteArrayResource(jdFile.getBytes()) {
                    @Override
                    public String getFilename() {
                        return jdFile.getOriginalFilename() != null ? jdFile.getOriginalFilename() : "job_description.pdf";
                    }
                };
                body.add("jdFile", jdResource);
            }

            if (jobDescription != null && !jobDescription.isBlank()) {
                body.add("jobDescription", jobDescription);
            }

            if (targetRole != null && !targetRole.isBlank()) {
                body.add("targetRole", targetRole);
            }

            return restClient.post()
                .uri("/api/analyze-match")
                .contentType(MediaType.MULTIPART_FORM_DATA)
                .body(body)
                .retrieve()
                .body(JsonNode.class);
        } catch (HttpClientErrorException ex) {
            if (ex.getStatusCode() == HttpStatus.UNPROCESSABLE_ENTITY) {
                throw new InvalidPdfException("Unprocessable PDF file or job description.");
            }
            if (ex.getStatusCode() == HttpStatus.PAYLOAD_TOO_LARGE) {
                throw new IllegalArgumentException("File size exceeds 5MB limit.");
            }
            throw new AiServiceException("AI service failed with status " + ex.getStatusCode(), ex);
        } catch (HttpServerErrorException | ResourceAccessException ex) {
            throw new AiServiceException("AI service failed to process request: " + ex.getMessage(), ex);
        } catch (IOException ex) {
            throw new InvalidPdfException("Failed to read uploaded PDF: " + ex.getMessage());
        }
    }

    public JsonNode analyzeMatch(MultipartFile file, String jobDescription, String targetRole) {
        return analyzeMatch(file, null, jobDescription, targetRole);
    }
}
