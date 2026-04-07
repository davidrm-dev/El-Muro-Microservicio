package co.edu.uptc.swii.posts_service.model;

import java.time.LocalDateTime;

import org.springframework.data.annotation.Id;
import org.springframework.data.mongodb.core.mapping.Document;

import lombok.Data;

@Data
@Document(collection = "posts")
public class Post {
    
    @Id
    private Integer id;
    private String title;
    private String description;
    private String fileUrl;
    private String contentText;
    private Integer votes;
    private String accesPoints;
    private Boolean isblocked;
    private LocalDateTime creationDate;
    private Integer userId;
}
