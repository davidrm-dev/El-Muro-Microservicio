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
    public boolean existsById(Integer topicId) {
        try {
            webClient.get()
                .uri(topicBaseUrl + topicExistsPath, topicId)
                .retrieve()
                .toBodilessEntity()
                .block();
            return true;
        } catch (WebClientResponseException exception) {
            if (exception.getStatusCode() == HttpStatus.NOT_FOUND) {
                return false;
            }
            throw exception;
        }
    }
}
