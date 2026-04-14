package co.edu.uptc.swii.posts_service.repository;

import org.springframework.data.mongodb.repository.MongoRepository;
import org.springframework.data.domain.Pageable;
import org.springframework.stereotype.Repository;

import co.edu.uptc.swii.posts_service.model.Post;
import java.util.List;
import java.util.Optional;

@Repository
public interface RepositoryPost extends MongoRepository<Post, Integer> {

    Optional<Post> findTopByOrderByIdDesc();

    List<Post> findAllByOrderByCreatedAtDesc(Pageable pageable);

    List<Post> findByTopicIdOrderByCreatedAtDesc(String topicId);

}
