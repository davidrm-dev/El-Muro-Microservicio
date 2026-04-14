package co.edu.uptc.swii.posts_service.client.impl;

import co.edu.uptc.swii.posts_service.client.TopicClient;
import co.edu.uptc.swii.posts_service.client.ServiceDiscoveryClient;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Component;
import org.springframework.web.reactive.function.client.WebClient;
import org.springframework.web.reactive.function.client.WebClientResponseException;

@Component
public class TopicWebClient implements TopicClient {

    private final WebClient webClient;
    private final ServiceDiscoveryClient serviceDiscoveryClient;

    public TopicWebClient(WebClient webClient, ServiceDiscoveryClient serviceDiscoveryClient) {
        this.webClient = webClient;
        this.serviceDiscoveryClient = serviceDiscoveryClient;
    }

    @Value("${integration.topic-service.service-name}")
    private String topicServiceName;

    @Value("${integration.topic-service.exists-path}")
    private String topicExistsPath;

    @Override
    public boolean existsById(String topicId) {
        try {
            String topicBaseUrl = serviceDiscoveryClient.resolveBaseUrl(topicServiceName);
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
            throw exception;
        }
    }
}
