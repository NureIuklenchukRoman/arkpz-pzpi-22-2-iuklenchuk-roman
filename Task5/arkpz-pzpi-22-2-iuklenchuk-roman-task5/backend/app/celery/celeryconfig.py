from kombu import Exchange, Queue

# Celery configuration
# http://docs.celeryproject.org/en/latest/configuration.html

task_create_missing_queues = True
# task_always_eager = True
task_queues = (
    Queue('cpu', Exchange('cpu'), routing_key='cpu'),
)

task_default_queue = 'low'
task_default_exchange = 'low'
task_default_routing_key = 'low'

imports = {
    "app.resources.rent.tasks",
    "app.utils.email",
}

broker_url = "redis://redis:6379/0"
result_backend = 'redis://redis:6379/0'

# sqlalchemy_url = "postgresql://database:database@pgbouncer:6432/database"
