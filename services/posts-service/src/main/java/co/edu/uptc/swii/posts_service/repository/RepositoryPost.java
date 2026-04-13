package co.edu.uptc.swii.posts_service.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.stereotype.Repository;

import co.edu.uptc.swii.posts_service.model.Post;
import java.util.Optional;

@Repository
public interface RepositoryPost extends MongoRepository<Post, Integer> {

    Optional<Post> findTopByOrderByIdDesc();

}
