"""Constantes de domínio (regras de negócio nomeadas)."""

# Tasks
TASK_STATUSES = ("pending", "in_progress", "done", "cancelled")
DEFAULT_TASK_STATUS = "pending"
STATUS_DONE = "done"
CLOSED_STATUSES = ("done", "cancelled")  # tasks nesses status nunca ficam atrasadas

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
HIGH_PRIORITY_MAX = 2  # prioridades 1 e 2 contam como "alta prioridade" no relatório do usuário
PRIORITY_LABELS = {1: "critical", 2: "high", 3: "medium", 4: "low", 5: "minimal"}

MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
DUE_DATE_FORMAT = "%Y-%m-%d"
TAGS_SEPARATOR = ","

# Usuários
USER_ROLES = ("user", "admin", "manager")
DEFAULT_ROLE = "user"
ADMIN_ROLE = "admin"
MIN_PASSWORD_LENGTH = 4
LEGACY_TOKEN_PREFIX = "fake-jwt-token-"  # token não verificado (ver pendências da refatoração)

# Categorias
DEFAULT_CATEGORY_COLOR = "#000000"

# Relatórios
RECENT_ACTIVITY_DAYS = 7

# API
API_NAME = "Task Manager API"
API_VERSION = "1.0"
