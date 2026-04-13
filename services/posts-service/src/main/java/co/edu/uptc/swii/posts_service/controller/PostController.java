package co.edu.uptc.swii.posts_service.controller;

import co.edu.uptc.swii.posts_service.dto.CreatePostRequest;
import co.edu.uptc.swii.posts_service.dto.PostResponse;
import co.edu.uptc.swii.posts_service.dto.UpdatePostRequest;
import co.edu.uptc.swii.posts_service.exception.ApiException;
import co.edu.uptc.swii.posts_service.security.AuthenticatedUser;
import co.edu.uptc.swii.posts_service.service.PostService;
import jakarta.validation.Valid;
import org.springframework.http.HttpStatus;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.bind.annotation.PutMapping;

@RestController
@RequestMapping("/api/posts")
public class PostController {

    private final PostService postService;

    public PostController(PostService postService) {
        this.postService = postService;
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public PostResponse createPost(
        @Valid @RequestBody CreatePostRequest request,
        @AuthenticationPrincipal AuthenticatedUser user
    ) {
        if (user == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }
        if (!"estudiante".equalsIgnoreCase(user.role()) && !"student".equalsIgnoreCase(user.role())) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Only students can create posts");
        }
        return postService.createPost(request, user.userId());
    }

    @GetMapping("/{postId}")
    public PostResponse accessPost(
        @PathVariable Integer postId,
        @AuthenticationPrincipal AuthenticatedUser user
    ) {
        if (user == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }
        if (!"estudiante".equalsIgnoreCase(user.role()) && !"student".equalsIgnoreCase(user.role()) && !"admin".equalsIgnoreCase(user.role())) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Only admin or student can access posts");
        }
        return postService.accessPost(postId, user.userId());
    }

    @PutMapping("/{postId}")
    public PostResponse updatePost(
        @PathVariable Integer postId,
        @Valid @RequestBody UpdatePostRequest request,
        @AuthenticationPrincipal AuthenticatedUser user
    ) {
        if (user == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }
        if (!"estudiante".equalsIgnoreCase(user.role()) && !"student".equalsIgnoreCase(user.role())) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Only students can update posts");
        }
        return postService.updatePost(postId, request, user.userId());
    }

    @DeleteMapping("/{postId}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void deletePost(
        @PathVariable Integer postId,
        @AuthenticationPrincipal AuthenticatedUser user
    ) {
        if (user == null) {
            throw new ApiException(HttpStatus.UNAUTHORIZED, "User is not authenticated");
        }
        if (!"estudiante".equalsIgnoreCase(user.role()) && !"student".equalsIgnoreCase(user.role()) && !"admin".equalsIgnoreCase(user.role())) {
            throw new ApiException(HttpStatus.FORBIDDEN, "Only admin or student can delete posts");
        }
        postService.deletePost(postId, user.userId(), user.role());
    }
}
