package co.edu.uptc.swii.posts_service.client;

import java.util.List;

import org.springframework.cloud.client.ServiceInstance;
import org.springframework.cloud.client.discovery.DiscoveryClient;
import org.springframework.stereotype.Component;

import co.edu.uptc.swii.posts_service.exception.ApiException;

import org.springframework.http.HttpStatus;

@Component
public class ServiceDiscoveryClient {

    private final DiscoveryClient discoveryClient;

    public ServiceDiscoveryClient(DiscoveryClient discoveryClient) {
        this.discoveryClient = discoveryClient;
    }

    public String resolveBaseUrl(String serviceName) {
        List<ServiceInstance> instances = discoveryClient.getInstances(serviceName);
        if (instances == null || instances.isEmpty()) {
            throw new ApiException(HttpStatus.SERVICE_UNAVAILABLE, "Service not found in Eureka: " + serviceName);
        }

        ServiceInstance selected = instances.stream()
            .filter(instance -> !instance.isSecure())
            .findFirst()
            .orElse(instances.get(0));

        return selected.getUri().toString();
    }
}
