FROM maven:3.9.12-eclipse-temurin-21 AS build
WORKDIR /app
COPY pom.xml /app/pom.xml
RUN mvn -q -e -DskipTests dependency:go-offline
COPY src /app/src
RUN mvn -q -DskipTests package

FROM eclipse-temurin:21-jre
WORKDIR /app
COPY --from=build /app/target/churninsight-0.0.1-SNAPSHOT.jar /app/app.jar
EXPOSE 8080
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
ENTRYPOINT ["java","-jar","/app/app.jar"]