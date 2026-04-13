package co.edu.uptc.swii.posts_service.service;

import java.time.Duration;
import java.time.LocalDateTime;

import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import co.edu.uptc.swii.posts_service.client.AuthClient;
import co.edu.uptc.swii.posts_service.client.TopicClient;
import co.edu.uptc.swii.posts_service.dto.CreatePostRequest;
import co.edu.uptc.swii.posts_service.dto.PostResponse;
import co.edu.uptc.swii.posts_service.dto.UpdatePostRequest;
import co.edu.uptc.swii.posts_service.exception.ApiException;
import co.edu.uptc.swii.posts_service.model.Post;
import co.edu.uptc.swii.posts_service.repository.RepositoryPost;

@Service
public class PostService {

    private final RepositoryPost postRepository;
    private final TopicClient topicClient;
    private final AuthClient authClient;

    public PostService(RepositoryPost postRepository, TopicClient topicClient, AuthClient authClient) {
        this.postRepository = postRepository;
        this.topicClient = topicClient;
        this.authClient = authClient;
    }

    public PostResponse createPost(CreatePostRequest request, Integer authenticatedUserId) {
        if (authenticatedUserId == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }

        boolean topicExists = topicClient.existsById(request.topicId());
        //boolean topicExists = true; // TODO: Descomentar esta línea y eliminar la siguiente cuando el TopicClient esté implementado
        if (!topicExists) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "Topic does not exist");
        }

        int currentPoints = authClient.getUserPoints(authenticatedUserId);
        if (request.accessPoints() > 0 && currentPoints < request.accessPoints()) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Insufficient points for this post");
        }

        if (request.accessPoints() > 0) {
            authClient.deductPoints(authenticatedUserId, request.accessPoints(), "create-post-access");
        }

        Post post = new Post();
        post.setId(generatePostId());
        post.setTitle(request.title());
        post.setDescription(request.description());
        post.setFileUrl(request.fileUrl());
        post.setTextContent(request.textContent());
        post.setVotes(0);
        post.setAccessPoints(request.accessPoints());
        post.setBlocked(request.accessPoints() > 0);
        post.setCreatedAt(LocalDateTime.now());
        post.setAuthorId(authenticatedUserId);
        post.setTopicId(request.topicId());

        Post saved = postRepository.save(post);
        return mapToResponse(saved);
    }

    public PostResponse accessPost(Integer postId, Integer authenticatedUserId) {
        if (authenticatedUserId == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }

        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Post not found"));

        if (Boolean.TRUE.equals(post.getBlocked()) && !post.getAuthorId().equals(authenticatedUserId)) {
            int points = authClient.getUserPoints(authenticatedUserId);
            if (points < post.getAccessPoints()) {
                throw new ApiException(HttpStatus.FORBIDDEN, "Insufficient points to access this post");
            }
        }

        return mapToResponse(post);
    }

    public PostResponse updatePost(Integer postId, UpdatePostRequest request, Integer authenticatedUserId) {
        if (authenticatedUserId == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }

        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Post not found"));

        if (!post.getAuthorId().equals(authenticatedUserId)) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Only the post owner can update this post");
        }

        long minutesFromCreation = Duration.between(post.getCreatedAt(), LocalDateTime.now()).toMinutes();
        if (minutesFromCreation > 10) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Post can only be updated during the first 10 minutes");
        }

        boolean topicExists = topicClient.existsById(request.topicId());
        if (!topicExists) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "Topic does not exist");
        }

        post.setTitle(request.title());
        post.setDescription(request.description());
        post.setFileUrl(request.fileUrl());
        post.setTextContent(request.textContent());
        post.setAccessPoints(request.accessPoints());
        post.setBlocked(request.accessPoints() > 0);
        post.setTopicId(request.topicId());

        Post saved = postRepository.save(post);
        return mapToResponse(saved);
    }

    public void deletePost(Integer postId, Integer authenticatedUserId, String role) {
        if (authenticatedUserId == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }

        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Post not found"));

        boolean isAdmin = "admin".equalsIgnoreCase(role);
        boolean isOwner = post.getAuthorId().equals(authenticatedUserId);
        if (!isAdmin && !isOwner) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Only admin or post owner can delete this post");
        }

        postRepository.deleteById(postId);
    }

    private Integer generatePostId() {
        return postRepository.findTopByOrderByIdDesc()
            .map(Post::getId)
            .orElse(0) + 1;
    }

    private PostResponse mapToResponse(Post post) {
        return new PostResponse(
            post.getId(),
            post.getTitle(),
            post.getDescription(),
            post.getFileUrl(),
            post.getTextContent(),
            post.getVotes(),
            post.getAccessPoints(),
            post.getBlocked(),
            post.getCreatedAt().toString(),
            post.getAuthorId(),
            post.getTopicId()
        );
    }
}
