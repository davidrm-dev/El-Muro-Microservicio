package co.edu.uptc.swii.posts_service.config;

import java.time.LocalDateTime;
import java.util.List;

import org.springframework.boot.CommandLineRunner;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

import co.edu.uptc.swii.posts_service.model.Post;
import co.edu.uptc.swii.posts_service.repository.RepositoryPost;

@Configuration
public class SeedPostsConfig {

    @Bean
    CommandLineRunner seedPosts(RepositoryPost repositoryPost) {
        return args -> {
            if (repositoryPost.count() > 0) {
                return;
            }

            Post post1 = new Post();
            post1.setId(1);
            post1.setTitle("Guia de derivadas");
            post1.setDescription("Resumen rapido de reglas de derivacion");
            post1.setTextContent("Incluye ejemplos de producto, cociente y cadena");
            post1.setFileUrl(null);
            post1.setVotes(2);
            post1.setAccessPoints(0);
            post1.setBlocked(false);
            post1.setCreatedAt(LocalDateTime.now().minusDays(2));
            post1.setAuthorId("seed-student-1");
            post1.setTopicId("tema-derivadas");

            Post post2 = new Post();
            post2.setId(2);
            post2.setTitle("Banco de integrales");
            post2.setDescription("Coleccion de integrales frecuentes para parcial");
            post2.setTextContent("Incluye sustitucion, partes y fracciones parciales");
            post2.setFileUrl(null);
            post2.setVotes(5);
            post2.setAccessPoints(10);
            post2.setBlocked(true);
            post2.setCreatedAt(LocalDateTime.now().minusDays(1));
            post2.setAuthorId("seed-student-2");
            post2.setTopicId("tema-integrales");

            Post post3 = new Post();
            post3.setId(3);
            post3.setTitle("Ejercicios de limites");
            post3.setDescription("Listado de limites resueltos paso a paso");
            post3.setTextContent("Ideal para practicar indeterminaciones");
            post3.setFileUrl(null);
            post3.setVotes(1);
            post3.setAccessPoints(0);
            post3.setBlocked(false);
            post3.setCreatedAt(LocalDateTime.now().minusHours(8));
            post3.setAuthorId("seed-student-1");
            post3.setTopicId("tema-limites");

            repositoryPost.saveAll(List.of(post1, post2, post3));
        };
    }
}
