package co.edu.uptc.swii.posts_service.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;

public record UpdatePostRequest(
    @NotBlank String title,
    @NotBlank String description,
    String fileUrl,
    String textContent,
    @NotNull @Min(0) Integer accessPoints,
    @NotNull Integer topicId
) {
}
