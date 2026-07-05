# Learning Log

## Docker Setup — Local PostgreSQL in Docker

**Date:** July 2026

**What I did:**
- Pulled official postgres:15 image from Docker Hub
- Created postgres-dbt container running on port 5433
- Kept separate from existing PostgreSQL on port 5432 to avoid conflicts
- Connected DBeaver to Docker Postgres successfully in 58ms

**Commands used:**
```bash
docker run --name postgres-dbt \
  -e POSTGRES_USER=dbt_user \
  -e POSTGRES_PASSWORD=dbt_password \
  -e POSTGRES_DB=dbt_practice \
  -p 5433:5432 \
  -d postgres:15

docker ps   # verify container running
```

**What I learned:**
- Docker runs PostgreSQL as an isolated container — doesn't interfere with system PostgreSQL
- Port mapping: 5433 on host maps to 5432 inside container
- Environment variables (-e flags) configure the database on first startup
- Container is stateless by default — data lost if container removed (need volumes for persistence)
- DBeaver connects to Docker Postgres same way as local — just different port

**Why Docker Postgres over system Postgres:**
- Portable — same setup works on any machine
- Isolated — each project can have its own Postgres version
- Required for dbt in Week 4 — dbt connects via Docker network
- Easy to reset — delete container and start fresh anytime

**Next step:**
- Use this database for dbt practice in Week 4
- Add Docker volume for data persistence
- Set up docker-compose.yml for multi-container setup