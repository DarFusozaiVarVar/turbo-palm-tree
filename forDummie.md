# Docker image
docker build --no-cache -t fastapi-poetry-exported .
# Docker container 
docker run --rm -t -p 8000:8000 --name kega_python fastapi-poetry-exported:latest
docker run --rm -t -p 8000:8000 -v $(pwd)/logs:/app/logs --name kega_python fastapi-poetry-exported:latest
# Проверка локально с UVICORN
poetry run uvicorn simpleServer:app --reload

docker build -t my-custom-postgres .     

docker run --name my-postgres-container -p 5433:5432 -v custom_pg_data:/var/lib/postgresql/18/docker -d my-custom-postgres:latest

# psql from Docker
- docker exec -it my-custom-postgres psql -U admin -d demo_db -c "SELECT * FROM users;"

# For CMD 
    set PGPASSWORD=secretpassword
    psql -h localhost -p 5433 -U admin -d demo_db -c "SELECT * FROM users;"

# Where could I find volumes in docker
    \\wsl.localhost\docker-desktop\mnt\docker-desktop-disk\data\docker\volumes 

