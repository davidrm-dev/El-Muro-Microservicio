package co.edu.uptc.swii.posts_service.client;

public interface AuthClient {

    int getUserPoints(String userId);

    void deductPoints(String userId, int points, String reason);
    
    void addPoints(String userId, int points, String reason);
}
