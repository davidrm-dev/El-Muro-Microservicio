package co.edu.uptc.swii.posts_service.client.dto;

import lombok.AllArgsConstructor;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Getter
@AllArgsConstructor
@NoArgsConstructor
public class AddPointsRequest {
    private int points;
    private String reason;
}