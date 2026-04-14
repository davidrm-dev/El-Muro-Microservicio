package co.edu.uptc.swii.posts_service.service;

import java.time.LocalDateTime;
import java.util.HashSet;
import java.util.Optional;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.ArgumentMatchers.anyInt;
import static org.mockito.ArgumentMatchers.anyString;
import static org.mockito.ArgumentMatchers.eq;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import static org.mockito.Mockito.never;
import static org.mockito.Mockito.verify;
import static org.mockito.Mockito.when;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.http.HttpStatus;

import co.edu.uptc.swii.posts_service.client.AuthClient;
import co.edu.uptc.swii.posts_service.client.TopicClient;
import co.edu.uptc.swii.posts_service.dto.CreatePostRequest;
import co.edu.uptc.swii.posts_service.dto.PostResponse;
import co.edu.uptc.swii.posts_service.exception.ApiException;
import co.edu.uptc.swii.posts_service.model.Post;
import co.edu.uptc.swii.posts_service.repository.RepositoryPost;

@ExtendWith(MockitoExtension.class)
public class PostServiceTest {

    @Mock
    private RepositoryPost postRepository;

    @Mock
    private TopicClient topicClient;

    @Mock
    private AuthClient authClient;

    @Mock
    private PointsCacheService pointsCacheService;

    @InjectMocks
    private PostService postService;

    private Post mockPost;
    private final Integer POST_ID = 1;
    private final Integer AUTHOR_ID = 100;
    private final Integer OTHER_USER_ID = 101;

    @BeforeEach
    void setUp() {
        mockPost = new Post();
        mockPost.setId(POST_ID);
        mockPost.setTitle("Test Post");
        mockPost.setDescription("Description");
        mockPost.setTextContent("Content");
        mockPost.setVotes(0);
        mockPost.setAccessPoints(10);
        mockPost.setBlocked(true);
        mockPost.setCreatedAt(LocalDateTime.now().minusMinutes(5));
        mockPost.setAuthorId(AUTHOR_ID);
        mockPost.setTopicId("69ddcd39af373c03557ec194");
    }

    @Test
    void testCreatePost_Success() {
        CreatePostRequest request = new CreatePostRequest("Title", "Desc", null, "Content", 10, "69ddcd39af373c03557ec194");
        
        when(topicClient.existsById("69ddcd39af373c03557ec194")).thenReturn(true);
        when(pointsCacheService.getUserPoints(AUTHOR_ID)).thenReturn(20);
        when(postRepository.findTopByOrderByIdDesc()).thenReturn(Optional.empty());
        when(postRepository.save(any(Post.class))).thenAnswer(i -> {
            Post p = i.getArgument(0);
            p.setId(1);
            return p;
        });

        PostResponse response = postService.createPost(request, AUTHOR_ID);

        assertNotNull(response);
        assertEquals(1, response.id());
        verify(authClient).deductPoints(eq(AUTHOR_ID), eq(10), anyString());
        verify(postRepository).save(any(Post.class));
    }

    @Test
    void testAccessPost_ByAuthor_Success() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(mockPost));
        
        PostResponse response = postService.accessPost(POST_ID, AUTHOR_ID);
        
        assertNotNull(response);
        verify(authClient, never()).deductPoints(anyInt(), anyInt(), anyString());
    }

    @Test
    void testAccessPost_ByOtherUser_InsufficientPoints() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(mockPost));
        when(pointsCacheService.getUserPoints(OTHER_USER_ID)).thenReturn(5); // cost is 10
        
        ApiException exception = assertThrows(ApiException.class, () -> {
            postService.accessPost(POST_ID, OTHER_USER_ID);
        });
        
        assertEquals(HttpStatus.FORBIDDEN, exception.getStatus());
        assertTrue(exception.getMessage().contains("Insufficient points"));
    }

    @Test
    void testAccessPost_ByOtherUser_SuccessAndUnlock() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(mockPost));
        when(pointsCacheService.getUserPoints(OTHER_USER_ID)).thenReturn(15); // cost is 10
        
        PostResponse response = postService.accessPost(POST_ID, OTHER_USER_ID);
        
        assertNotNull(response);
        assertTrue(mockPost.getUnlockedByUsers().contains(OTHER_USER_ID));
        verify(authClient).deductPoints(eq(OTHER_USER_ID), eq(10), anyString());
        verify(postRepository).save(mockPost);
    }

    @Test
    void testAccessPost_ByOtherUser_AlreadyUnlocked() {
        mockPost.setUnlockedByUsers(new HashSet<>());
        mockPost.getUnlockedByUsers().add(OTHER_USER_ID);
        
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(mockPost));
        
        PostResponse response = postService.accessPost(POST_ID, OTHER_USER_ID);
        
        assertNotNull(response);
        // Debe poder acceder sin gastar puntos otra vez
        verify(authClient, never()).deductPoints(anyInt(), anyInt(), anyString());
        verify(postRepository, never()).save(any(Post.class));
    }

    @Test
    void testVotePost_Success() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(mockPost));
        when(postRepository.save(any(Post.class))).thenReturn(mockPost);
        
        PostResponse response = postService.votePost(POST_ID, OTHER_USER_ID);
        
        assertNotNull(response);
        assertEquals(1, mockPost.getVotes());
        assertTrue(mockPost.getVotedByUsers().contains(OTHER_USER_ID));
        verify(authClient).addPoints(eq(AUTHOR_ID), eq(1), eq("post-voted"));
    }

    @Test
    void testVotePost_OwnPost_ThrowsException() {
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(mockPost));
        
        ApiException exception = assertThrows(ApiException.class, () -> {
            postService.votePost(POST_ID, AUTHOR_ID);
        });
        
        assertEquals(HttpStatus.BAD_REQUEST, exception.getStatus());
        assertTrue(exception.getMessage().contains("own post"));
    }

    @Test
    void testVotePost_AlreadyVoted_ThrowsException() {
        mockPost.setVotedByUsers(new HashSet<>());
        mockPost.getVotedByUsers().add(OTHER_USER_ID);
        
        when(postRepository.findById(POST_ID)).thenReturn(Optional.of(mockPost));
        
        ApiException exception = assertThrows(ApiException.class, () -> {
            postService.votePost(POST_ID, OTHER_USER_ID);
        });
        
        assertEquals(HttpStatus.BAD_REQUEST, exception.getStatus());
        assertTrue(exception.getMessage().contains("already voted"));
    }
}
