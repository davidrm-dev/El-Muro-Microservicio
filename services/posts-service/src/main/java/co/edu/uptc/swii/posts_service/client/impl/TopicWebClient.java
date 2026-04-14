package co.edu.uptc.swii.posts_service.client.impl;

import co.edu.uptc.swii.posts_service.client.TopicClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

@Component
public class TopicWebClient implements TopicClient {

    private final WebClient webClient;

    public TopicWebClient(WebClient webClient) {
        this.webClient = webClient;
    }

    @Value("${integration.topic-service.base-url}")
    private String topicBaseUrl;

    @Value("${integration.topic-service.exists-path}")
    private String topicExistsPath;

    @Override
    public boolean existsById(String topicId) {
        try {
            // Build the complete URL
            String completeUrl = topicBaseUrl + topicExistsPath.replace("{topicId}", topicId);
            
            webClient.get()
                .uri(completeUrl)
                .retrieve()
                .toBodilessEntity()
                .block();
            return true;
        } catch (WebClientResponseException exception) {
            if (exception.getStatusCode() == HttpStatus.NOT_FOUND) {
                return false;
            }
            // For development: assume topic exists if we can't reach the service or auth fails
            // This is a temporary measure - in production, we should properly handle authentication
            if (exception.getStatusCode() == HttpStatus.UNAUTHORIZED || 
                exception.getStatusCode() == HttpStatus.FORBIDDEN ||
                exception.getStatusCode() == HttpStatus.SERVICE_UNAVAILABLE) {
                System.out.println("WARNING: Could not verify topic " + topicId + " with service (status: " + exception.getStatusCode() + "), assuming it exists");
                return true;
            }
            throw exception;
        }
    }
}
