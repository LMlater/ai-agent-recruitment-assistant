FROM maven:3.9-eclipse-temurin-17 AS build

WORKDIR /workspace
COPY pom.xml .
RUN mvn -q -DskipTests dependency:go-offline
COPY src ./src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:17-jre

WORKDIR /app
ENV MYSQL_URL=jdbc:mysql://mysql:3306/smart_credit_multi_agent?useUnicode=true\&characterEncoding=utf8\&serverTimezone=Asia/Shanghai\&allowPublicKeyRetrieval=true\&useSSL=false \
    MYSQL_USER=smartcredit \
    MYSQL_PASSWORD=smartcredit_dev_password \
    REDIS_HOST=redis \
    REDIS_PORT=6379 \
    AGENT_SERVICE_BASE_URL=http://agent-service:8001 \
    JWT_SECRET=smart-credit-local-demo-secret-change-before-real-deployments-123456

COPY --from=build /workspace/target/*.jar app.jar

EXPOSE 8080

ENTRYPOINT ["java", "-jar", "app.jar"]
