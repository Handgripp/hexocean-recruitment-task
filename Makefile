run-app:
	docker-compose up --build

migrate:
	docker-compose exec web python /app/recruitment_task/manage.py migrate

create-superuser:
	docker-compose exec web python /app/recruitment_task/manage.py createsuperuser

down:
	docker-compose down