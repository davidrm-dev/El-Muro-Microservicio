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
    public int getUserPoints(Integer userId) {
        try {
            return authClient.getUserPoints(userId);
        } catch (Exception e) {
            // For development: if Auth Service is not available or internal endpoints don't exist,
            // assume user has plenty of points (1000)
            System.out.println("WARNING: Could not retrieve user points from Auth Service (" + e.getMessage() + "), assuming 1000 points for user " + userId);
            return 1000;
        }
    }

    @CacheEvict(cacheNames = CacheNames.USER_POINTS, key = "#userId")
    public void evictUserPoints(Integer userId) {
    }
}
