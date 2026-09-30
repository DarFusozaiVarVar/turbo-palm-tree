# Docker image
- docker build --no-cache -t fastapi-poetry-exported .
# Docker container 
- docker run --rm -t -p 8000:8000 --name kega_python fastapi-poetry-exported:latest
# Проверка локально с UVICORN
- poetry run uvicorn simpleServer:app --reload

# psql from Docker
- docker exec -it my-postgres-container psql -U admin -d demo_db -c "SELECT * FROM users;"

# For CMD 
    set PGPASSWORD=secretpassword
    psql -h localhost -p 5432 -U admin -d demo_db -c "SELECT * FROM users;"
