# Hexocean - Recruitment Task

## Stack:

- Django
- PostgreSQL
- Docker

## Main features:

- Ability to upload and fetch images
- Ability to create a link to an image with an expiration time

## How to run?

### Requirements:

- docker

### Step by step:

- `cp .env.example .env`
- fill envs with proper values
- run: `make run-app`
- run: `make migrate`
- run: `make create-superuser`


## Endpoints

- `GET /login`
- `POST /images/upload accepts a file in the request body`
- `GET /images`
- `GET /images/<image_id>`
- `POST /images/<image_id>/generate-link`

