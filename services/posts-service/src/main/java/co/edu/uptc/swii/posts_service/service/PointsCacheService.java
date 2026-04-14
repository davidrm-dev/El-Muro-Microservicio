package co.edu.uptc.swii.posts_service.service;

import co.edu.uptc.swii.posts_service.client.AuthClient;
import co.edu.uptc.swii.posts_service.config.CacheNames;
import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.stereotype.Service;

@Service
public class PointsCacheService {

    private final AuthClient authClient;

    public PointsCacheService(AuthClient authClient) {
        this.authClient = authClient;
    }

    @Cacheable(cacheNames = CacheNames.USER_POINTS, key = "#userId")
    public int getUserPoints(String userId) {
        return authClient.getUserPoints(userId);
    }

    @CacheEvict(cacheNames = CacheNames.USER_POINTS, key = "#userId")
    public void evictUserPoints(String userId) {
    }
}
