package co.edu.uptc.swii.posts_service.client.impl;

import co.edu.uptc.swii.posts_service.client.AuthClient;
import co.edu.uptc.swii.posts_service.client.dto.DeductPointsRequest;
import co.edu.uptc.swii.posts_service.client.dto.InternalPointsRequest;
import co.edu.uptc.swii.posts_service.client.dto.InternalPointsResponse;
import co.edu.uptc.swii.posts_service.util.HmacSigner;
import java.time.Instant;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

@Component
public class AuthWebClient implements AuthClient {

    private final WebClient webClient;
    private final HmacSigner hmacSigner;

    public AuthWebClient(WebClient webClient, HmacSigner hmacSigner) {
        this.webClient = webClient;
        this.hmacSigner = hmacSigner;
    }

    @Value("${integration.auth-service.base-url}")
    private String authBaseUrl;

    @Value("${integration.auth-service.points-api-path}")
    private String pointsApiPath;

    @Value("${integration.auth-service.points-sign-path}")
    private String pointsSignPath;

    @Value("${integration.auth-service.deduct-points-api-path}")
    private String deductPointsApiPath;

    @Value("${integration.auth-service.deduct-points-sign-path}")
    private String deductPointsSignPath;

    @Value("${integration.internal.service-id}")
    private String serviceId;

    @Override
    public int getUserPoints(Integer userId) {
        String timestamp = String.valueOf(Instant.now().toEpochMilli());
        String signature = hmacSigner.sign(serviceId, timestamp, HttpMethod.POST.name(), pointsSignPath);

        InternalPointsResponse response = webClient.post()
            .uri(authBaseUrl + pointsApiPath)
            .headers(headers -> {
                headers.add("x-service-id", serviceId);
                headers.add("x-service-timestamp", timestamp);
                headers.add("x-service-signature", signature);
            })
            .bodyValue(new InternalPointsRequest(userId))
            .retrieve()
            .bodyToMono(InternalPointsResponse.class)
            .block();

        if (response == null || response.points() == null) {
            throw new IllegalStateException("Invalid points response");
        }

        return response.points();
    }

    @Override
    public void deductPoints(Integer userId, int points, String reason) {
        String apiPath = deductPointsApiPath.replace("{userId}", String.valueOf(userId));
        String signPath = deductPointsSignPath.replace("{userId}", String.valueOf(userId));
        String timestamp = String.valueOf(Instant.now().toEpochMilli());
        String signature = hmacSigner.sign(serviceId, timestamp, HttpMethod.PATCH.name(), signPath);

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
                .block();
        } catch (WebClientResponseException exception) {
            if (exception.getStatusCode() == HttpStatus.BAD_REQUEST || exception.getStatusCode() == HttpStatus.NOT_FOUND) {
                throw exception;
            }
            throw new WebClientResponseException(
                "Auth service call failed",
                HttpStatus.BAD_GATEWAY.value(),
                HttpStatus.BAD_GATEWAY.getReasonPhrase(),
                null,
                null,
                null
            );
        }
    }
}
