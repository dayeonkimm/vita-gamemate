# 1. 기본 Python 이미지를 지정합니다.
FROM python:3.12-slim
# Python 3.12 환경을 기반으로 컨테이너를 만들기 위해서
# slim 태그로 더 작은 이미지를 사용하여 성능과 효율성을 높이기 위한 선택

# 2. 필수 패키지 설치
RUN apt-get update && apt-get install -y \
    curl \
    git \
    build-essential \
    libssl-dev \
    zlib1g-dev \
    libbz2-dev \
    libreadline-dev \
    wget \
    llvm \
    libncurses5-dev \
    libncursesw5-dev \
    xz-utils \
    tk-dev \
    libffi-dev \
    liblzma-dev \
    python3-openssl \
    default-libmysqlclient-dev \
    libmariadb-dev-compat \
    pkg-config \
    nano \
    lsof \
    nginx \
    certbot \
    && rm -rf /var/lib/apt/lists/*

# 3. Poetry 설치
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# 4. 프로젝트 파일 복사 및 의존성 설치
WORKDIR /app

COPY pyproject.toml poetry.lock ./
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi

# 5. 프로젝트 소스 코드 복사
COPY . /app

# 6. ENTRYPOINT 설정
COPY scripts/entrypoint.sh /app/entrypoint.sh
COPY nginx.conf /etc/nginx/conf.d/default.conf

RUN chmod +x /app/entrypoint.sh

# 7. Gunicorn이 8000 포트에서 수신하도록 EXPOSE
EXPOSE 8000
