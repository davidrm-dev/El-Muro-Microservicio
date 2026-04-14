package co.edu.uptc.swii.posts_service.service;

import java.time.Duration;
import java.time.LocalDateTime;
import java.util.List;

import org.springframework.cache.annotation.CacheEvict;
import org.springframework.cache.annotation.Cacheable;
import org.springframework.data.domain.PageRequest;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;

import co.edu.uptc.swii.posts_service.client.AuthClient;
import co.edu.uptc.swii.posts_service.client.TopicClient;
import co.edu.uptc.swii.posts_service.config.CacheNames;
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
    private final PointsCacheService pointsCacheService;

    public PostService(
        RepositoryPost postRepository,
        TopicClient topicClient,
        AuthClient authClient,
        PointsCacheService pointsCacheService
    ) {
        this.postRepository = postRepository;
        this.topicClient = topicClient;
        this.authClient = authClient;
        this.pointsCacheService = pointsCacheService;
    }

    @CacheEvict(cacheNames = CacheNames.FEED_LATEST, allEntries = true)
    public PostResponse createPost(CreatePostRequest request, Integer authenticatedUserId) {
        if (authenticatedUserId == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }

        boolean topicExists = topicClient.existsById(request.topicId());
        //boolean topicExists = true; // TODO: Descomentar esta línea y eliminar la siguiente cuando el TopicClient esté implementado
        if (!topicExists) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "Topic does not exist");
        }

        int currentPoints = pointsCacheService.getUserPoints(authenticatedUserId);
        if (request.accessPoints() > 0 && currentPoints < request.accessPoints()) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Insufficient points for this post");
        }

        if (request.accessPoints() > 0) {
            authClient.deductPoints(authenticatedUserId, request.accessPoints(), "create-post-access");
            pointsCacheService.evictUserPoints(authenticatedUserId);
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
            if (post.getUnlockedByUsers() == null || !post.getUnlockedByUsers().contains(authenticatedUserId)) {
                int points = pointsCacheService.getUserPoints(authenticatedUserId);
                if (points < post.getAccessPoints()) {
                    throw new ApiException(HttpStatus.FORBIDDEN, "Insufficient points to access this post");
                }
                
                authClient.deductPoints(authenticatedUserId, post.getAccessPoints(), "access-post");
                pointsCacheService.evictUserPoints(authenticatedUserId);

                if (post.getUnlockedByUsers() == null) {
                    post.setUnlockedByUsers(new java.util.HashSet<>());
                }
                post.getUnlockedByUsers().add(authenticatedUserId);
                postRepository.save(post);
            }
        }

        return mapToResponse(post);
    }

    @CacheEvict(cacheNames = CacheNames.FEED_LATEST, allEntries = true)
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

    @CacheEvict(cacheNames = CacheNames.FEED_LATEST, allEntries = true)
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

    @CacheEvict(cacheNames = CacheNames.FEED_LATEST, allEntries = true)
    public PostResponse votePost(Integer postId, Integer authenticatedUserId) {
        if (authenticatedUserId == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }

        Post post = postRepository.findById(postId)
            .orElseThrow(() -> new ApiException(HttpStatus.NOT_FOUND, "Post not found"));

        if (post.getAuthorId().equals(authenticatedUserId)) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "You cannot vote your own post");
        }
        if (post.getVotedByUsers() != null && post.getVotedByUsers().contains(authenticatedUserId)) {
            throw new ApiException(HttpStatus.BAD_REQUEST, "You have already voted this post");
        }

        if (post.getVotedByUsers() == null) {
            post.setVotedByUsers(new java.util.HashSet<>());
        }
        post.getVotedByUsers().add(authenticatedUserId);
        post.setVotes(post.getVotes() + 1);
        Post saved = postRepository.save(post);

        // Sumar un punto al creador del post
        authClient.addPoints(post.getAuthorId(), 1, "post-voted");
        pointsCacheService.evictUserPoints(post.getAuthorId());

        return mapToResponse(saved);
    }

    @Cacheable(cacheNames = CacheNames.FEED_LATEST, key = "#limit")
    public List<PostResponse> getLatestFeed(Integer limit) {
        return postRepository.findAllByOrderByCreatedAtDesc(PageRequest.of(0, limit))
            .stream()
            .map(this::mapToResponse)
            .toList();
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
