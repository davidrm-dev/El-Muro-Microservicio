package co.edu.uptc.swii.posts_service.client.impl;

import java.time.Instant;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;

import co.edu.uptc.swii.posts_service.client.AuthClient;
import co.edu.uptc.swii.posts_service.client.ServiceDiscoveryClient;
import co.edu.uptc.swii.posts_service.client.dto.AddPointsRequest;
import co.edu.uptc.swii.posts_service.client.dto.DeductPointsRequest;
import co.edu.uptc.swii.posts_service.client.dto.InternalPointsResponse;
import co.edu.uptc.swii.posts_service.util.HmacSigner;

@Component
public class AuthWebClient implements AuthClient {

    private static final Logger logger = LoggerFactory.getLogger(AuthWebClient.class);
    private final WebClient webClient;
    private final HmacSigner hmacSigner;
    private final ServiceDiscoveryClient serviceDiscoveryClient;

    public AuthWebClient(WebClient webClient, HmacSigner hmacSigner, ServiceDiscoveryClient serviceDiscoveryClient) {
        this.webClient = webClient;
        this.hmacSigner = hmacSigner;
        this.serviceDiscoveryClient = serviceDiscoveryClient;
    }

    @Value("${integration.auth-service.service-name}")
    private String authServiceName;

    @Value("${integration.auth-service.points-sign-path:/internal/users/{userId}/points}")
    private String pointsSignPathTemplate;

    @Value("${integration.auth-service.points-api-path:/api/auth/internal/users/{userId}/points}")
    private String pointsApiPathTemplate;

    @Value("${integration.auth-service.deduct-points-api-path}")
    private String deductPointsApiPath;

    @Value("${integration.auth-service.deduct-points-sign-path}")
    private String deductPointsSignPath;

    @Value("${integration.auth-service.add-points-api-path}")
    private String addPointsApiPath;

    @Value("${integration.auth-service.add-points-sign-path}")
    private String addPointsSignPath;

    @Value("${integration.internal.service-id}")
    private String serviceId;

    @Override
    public int getUserPoints(String userId) {
        if (userId == null || userId.isBlank()) {
            throw new IllegalArgumentException("User ID cannot be null or empty");
        }
        String apiPath = pointsApiPathTemplate.replace("{userId}", userId);
        String signPath = pointsSignPathTemplate.replace("{userId}", userId);
        String timestamp = String.valueOf(Instant.now().toEpochMilli());
        String signature = hmacSigner.sign(serviceId, timestamp, HttpMethod.GET.name(), signPath);
        String authBaseUrl = serviceDiscoveryClient.resolveBaseUrl(authServiceName);

        InternalPointsResponse response = webClient.get()
            .uri(authBaseUrl + apiPath)
            .headers(headers -> {
                headers.add("x-service-id", serviceId);
                headers.add("x-service-timestamp", timestamp);
                headers.add("x-service-signature", signature);
            })
            .retrieve()
            .bodyToMono(InternalPointsResponse.class)
            .block();

        if (response == null || response.points() == null) {
            throw new IllegalStateException("Invalid points response");
        }

        return response.points();
    }

    @Override
    public void deductPoints(String userId, int points, String reason) {
        if (userId == null || userId.isBlank()) {
            logger.warn("Attempted to deduct points with null or empty userId");
            return;
        }
        String apiPath = deductPointsApiPath.replace("{userId}", userId);
        String signPath = deductPointsSignPath.replace("{userId}", userId);
        String timestamp = String.valueOf(Instant.now().toEpochMilli());
        String signature = hmacSigner.sign(serviceId, timestamp, HttpMethod.PATCH.name(), signPath);
        String authBaseUrl = serviceDiscoveryClient.resolveBaseUrl(authServiceName);

        // Call asynchronously without blocking - log errors but don't fail the request
        try {
            webClient.patch()
                .uri(authBaseUrl + apiPath)
                .headers(headers -> {
                    headers.add("x-service-id", serviceId);
                    headers.add("x-service-timestamp", timestamp);
                    headers.add("x-service-signature", signature);
                })
                .bodyValue(new DeductPointsRequest(points, reason))
                .retrieve()
                .toBodilessEntity()
                .timeout(java.time.Duration.ofSeconds(2))
                .subscribe(
                    response -> logger.debug("Successfully deducted points for user {}", userId),
                    error -> logger.warn("Error calling Auth Service deductPoints for user {}: {}", userId, error.getMessage())
                );
        } catch (Exception exception) {
            logger.warn("Error initiating Auth Service deductPoints call for user {}: {}", userId, exception.getMessage());
        }
    }

    @Override
    public void addPoints(String userId, int points, String reason) {
        if (userId == null || userId.isBlank()) {
            logger.warn("Attempted to add points with null or empty userId");
            return;
        }
        String apiPath = addPointsApiPath.replace("{userId}", userId);
        String signPath = addPointsSignPath.replace("{userId}", userId);
        String timestamp = String.valueOf(Instant.now().toEpochMilli());
        String signature = hmacSigner.sign(serviceId, timestamp, HttpMethod.PATCH.name(), signPath);
        String authBaseUrl = serviceDiscoveryClient.resolveBaseUrl(authServiceName);

        // Call asynchronously without blocking - log errors but don't fail the request
        try {
            webClient.patch()
                .uri(authBaseUrl + apiPath)
                .headers(headers -> {
                    headers.add("x-service-id", serviceId);
                    headers.add("x-service-timestamp", timestamp);
                    headers.add("x-service-signature", signature);
                })
                .bodyValue(new AddPointsRequest(points, reason))
                .retrieve()
                .toBodilessEntity()
                .timeout(java.time.Duration.ofSeconds(2))
                .subscribe(
                    response -> logger.debug("Successfully added points for user {}", userId),
                    error -> logger.warn("Error calling Auth Service addPoints for user {}: {}", userId, error.getMessage())
                );
        } catch (Exception exception) {
            logger.warn("Error initiating Auth Service addPoints call for user {}: {}", userId, exception.getMessage());
        }
    }
}
