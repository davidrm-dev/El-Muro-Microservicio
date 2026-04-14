package co.edu.uptc.swii.posts_service.security;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import java.nio.charset.StandardCharsets;
import javax.crypto.SecretKey;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

@Service
public class JwtService {

    private final SecretKey secretKey;

    public JwtService(@Value("${security.jwt.secret}") String jwtSecret) {
        this.secretKey = Keys.hmacShaKeyFor(jwtSecret.getBytes(StandardCharsets.UTF_8));
    }

    public AuthenticatedUser parseToken(String token) {
        Claims claims = Jwts.parser()
            .verifyWith(secretKey)
            .build()
            .parseSignedClaims(token)
            .getPayload();

        Integer userId = readIntegerClaim(claims.get("userId"));
        String role = readRole(claims);

        if (userId == null) {
            throw new IllegalArgumentException("JWT without userId");
        }

        return new AuthenticatedUser(userId, role == null ? "" : role);
    }

    private String readRole(Claims claims) {
        String role = claims.get("role", String.class);
        if (role == null || role.isBlank()) {
            role = claims.get("rol", String.class);
        }
        return role == null ? "" : role;
    }

    private Integer readIntegerClaim(Object value) {
        if (value instanceof Number number) {
            return number.intValue();
        }
        if (value instanceof String text && !text.isBlank()) {
            return Integer.valueOf(text);
        }
        return null;
    }
}
