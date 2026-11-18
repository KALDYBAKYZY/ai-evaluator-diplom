Роль: {role}

Оцени один критерий по шкале 1–5.

Критерий:
code: {code}
name: {name}
description: {description}
Уровни шкалы:
{levels}

<document>
{document}
</document>

Верни JSON:
{{"score": 1-5, "justification": "кратко, 2-4 предложения", "evidence": [{{"slide_no": число, "quote": "дословная цитата"}}], "missing": ["что не раскрыто"]}}
