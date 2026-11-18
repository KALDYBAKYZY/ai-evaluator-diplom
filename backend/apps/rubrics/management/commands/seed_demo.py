from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.accounts.models import Assignment, Course, Enrollment, User
from apps.rubrics.models import Criterion, Rubric

LEVELS = {
    "1": "Не раскрыто или нет данных",
    "2": "Упомянуто без обоснования",
    "3": "Раскрыто частично, допущения не подтверждены",
    "4": "Раскрыто, есть отдельные подтверждения",
    "5": "Раскрыто полно, подтверждено данными или проверяемыми действиями",
}

CRITERIA = [
    ("market", "Рынок и клиент", "Целевой сегмент, размер рынка, конкуренты, подтверждение спроса.", "0.20", "market"),
    ("business_model", "Бизнес-модель", "Клиент, проблема, ценность продукта, способ заработка, основные экономические допущения.", "0.25", "business_model"),
    ("finance", "Финансы", "Финансовый план, реалистичность расчётов, потребность в инвестициях.", "0.20", "finance"),
    ("technology", "Технология", "Реализуемость решения, MVP или прототип, технические риски.", "0.20", "technology"),
    ("innovation", "Инновационность", "Новизна, отличие от аналогов, масштабируемость.", "0.15", "innovation"),
]

USERS = [
    ("teacher", "Демо", "Преподаватель", Enrollment.Role.INSTRUCTOR),
    ("student", "Демо", "Студент", Enrollment.Role.STUDENT),
    ("expert", "Демо", "Эксперт", Enrollment.Role.EXPERT),
]


class Command(BaseCommand):
    help = "Создаёт демо-курс, пользователей и черновик рубрики"

    def add_arguments(self, parser):
        parser.add_argument("--password", default="demo12345")

    @transaction.atomic
    def handle(self, *args, **options):
        rubric, _ = Rubric.objects.get_or_create(title="AI Startup Evaluator", version=1)
        for order, (code, name, description, weight, agent_type) in enumerate(CRITERIA):
            Criterion.objects.update_or_create(
                rubric=rubric,
                code=code,
                defaults={
                    "name": name,
                    "description": description,
                    "weight": Decimal(weight),
                    "agent_type": agent_type,
                    "levels": LEVELS,
                    "order": order,
                },
            )
        course, _ = Course.objects.get_or_create(title="Демо-курс: Технологическое предпринимательство")
        Assignment.objects.get_or_create(course=course, title="Питч стартапа", defaults={"rubric": rubric})
        for username, first, last, role in USERS:
            user, created = User.objects.get_or_create(username=username, defaults={"first_name": first, "last_name": last})
            if created:
                user.set_password(options["password"])
                user.save()
            Enrollment.objects.get_or_create(user=user, course=course, role=role)
        self.stdout.write(self.style.SUCCESS("Демо-данные созданы: teacher / student / expert"))
