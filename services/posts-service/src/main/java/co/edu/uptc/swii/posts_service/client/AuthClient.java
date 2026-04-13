package co.edu.uptc.swii.posts_service.client;

public interface AuthClient {

    int getUserPoints(Integer userId);

    void deductPoints(Integer userId, int points, String reason);
    
    void addPoints(Integer userId, int points, String reason);
}
