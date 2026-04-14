package co.edu.uptc.swii.posts_service.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;

@Service
public class JwtService {

    private static final Logger logger = LoggerFactory.getLogger(JwtService.class);
    private final SecretKey secretKey;

    public JwtService(@Value("${security.jwt.secret}") String jwtSecret) {
        this.secretKey = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
        logger.info("JwtService initialized with secret length: {}", jwtSecret.length());
    }

    public AuthenticatedUser parseToken(String token) {
        logger.debug("Attempting to parse token: {}", token.substring(0, Math.min(50, token.length())));
        try {
            Claims claims = Jwts.parser()
                .verifyWith(secretKey)
                .build()
                .parseSignedClaims(token)
                .getPayload();

            logger.debug("Token claims: userId={}, role={}", claims.get("userId"), claims.get("role"));

            String userId = readStringClaim(claims.get("userId"));
            String role = readRole(claims);

            if (userId == null || userId.isBlank()) {
                throw new IllegalArgumentException("JWT without userId");
            }

            logger.debug("Successfully parsed token for userId: {}", userId);
            return new AuthenticatedUser(userId, role == null ? "" : role);
        } catch (Exception e) {
            logger.error("Error parsing JWT token: {}", e.getMessage(), e);
            throw e;
        }
    }

    private String readRole(Claims claims) {
        String role = claims.get("role", String.class);
        if (role == null || role.isBlank()) {
            role = claims.get("rol", String.class);
        }
        return role == null ? "" : role;
    }

    private String readStringClaim(Object value) {
        if (value instanceof String text && !text.isBlank()) {
            return text;
        }
        if (value != null) {
            return value.toString();
        }
        return null;
    }
}
