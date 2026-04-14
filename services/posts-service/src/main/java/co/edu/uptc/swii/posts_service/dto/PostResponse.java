package co.edu.uptc.swii.posts_service.dto;

public record PostResponse(
    Integer id,
    String title,
    String description,
    String fileUrl,
    String textContent,
    Integer votes,
    Integer accessPoints,
    Boolean blocked,
    String createdAt,
    Integer authorId,
    Integer topicId
) {
}
