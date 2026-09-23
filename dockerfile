FROM ubuntu:26.10
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y python3-full
WORKDIR /work
COPY . /work
CMD ["python3", "-m", "http.server"]