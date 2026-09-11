"""Profil katalogi — kod bilan birga yashaydigan ro'yxatlar.

Texnologiyalar `simple-icons` paketidagi slug bilan AYNAN bir xil: frontend
ikonkani shu slug bo'yicha oladi. Ro'yxat qo'lda yig'ilgan, lekin har bir
slug paketda borligi o'lchab tekshirilgan — `csharp` va `java` u yerda yo'q,
o'rniga `dotnet` va `openjdk`.
"""

from __future__ import annotations

#: slug → ko'rsatiladigan nom. Tartib — sozlamalardagi tartib.
TECHNOLOGIES: dict[str, str] = {
    "cplusplus": "C++",
    "c": "C",
    "python": "Python",
    "openjdk": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "go": "Go",
    "rust": "Rust",
    "kotlin": "Kotlin",
    "dotnet": "C# / .NET",
    "php": "PHP",
    "ruby": "Ruby",
    "swift": "Swift",
    "dart": "Dart",
    "haskell": "Haskell",
    "scala": "Scala",
    "lua": "Lua",
    "r": "R",
    "julia": "Julia",
    "elixir": "Elixir",
    "ocaml": "OCaml",
    "react": "React",
    "vuedotjs": "Vue",
    "angular": "Angular",
    "nextdotjs": "Next.js",
    "nodedotjs": "Node.js",
    "tailwindcss": "Tailwind CSS",
    "graphql": "GraphQL",
    "django": "Django",
    "flask": "Flask",
    "fastapi": "FastAPI",
    "spring": "Spring",
    "laravel": "Laravel",
    "flutter": "Flutter",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "linux": "Linux",
    "git": "Git",
    "numpy": "NumPy",
    "pandas": "pandas",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
}

#: O'zbekistonning 14 hududi. Mamlakat `UZ` bo'lsa viloyat SHU ro'yxatdan
#: tanlanadi — erkin matn bo'lsa bitta hudud o'n xil yozilardi va viloyat
#: bo'yicha reyting qurib bo'lmasdi. Boshqa mamlakatda — erkin matn.
UZ_REGIONS: tuple[str, ...] = (
    "toshkent-shahri",
    "toshkent",
    "andijon",
    "fargona",
    "namangan",
    "sirdaryo",
    "jizzax",
    "samarqand",
    "qashqadaryo",
    "surxondaryo",
    "buxoro",
    "navoiy",
    "xorazm",
    "qoraqalpogiston",
)

#: Ko'nikmalar katalogi — `slug → (uz, ru, en)`.
SKILLS: dict[str, tuple[str, str, str]] = {
    "algorithms": ("Algoritmlar", "Алгоритмы", "Algorithms"),
    "data-structures": ("Ma'lumotlar tuzilmalari", "Структуры данных", "Data structures"),
    "dynamic-programming": (
        "Dinamik dasturlash",
        "Динамическое программирование",
        "Dynamic programming",
    ),
    "graphs": ("Graflar", "Графы", "Graphs"),
    "math": ("Matematika", "Математика", "Mathematics"),
    "number-theory": ("Sonlar nazariyasi", "Теория чисел", "Number theory"),
    "geometry": ("Geometriya", "Геометрия", "Geometry"),
    "strings": ("Satrlar", "Строки", "Strings"),
    "greedy": ("Ochko'z algoritmlar", "Жадные алгоритмы", "Greedy algorithms"),
    "combinatorics": ("Kombinatorika", "Комбинаторика", "Combinatorics"),
    "competitive-programming": (
        "Sport dasturlash",
        "Спортивное программирование",
        "Competitive programming",
    ),
    "web-development": ("Veb-dasturlash", "Веб-разработка", "Web development"),
    "backend": ("Backend", "Бэкенд", "Backend"),
    "frontend": ("Frontend", "Фронтенд", "Frontend"),
    "mobile": ("Mobil dasturlash", "Мобильная разработка", "Mobile development"),
    "data-science": ("Data Science", "Data Science", "Data science"),
    "machine-learning": ("Mashinaviy o'qitish", "Машинное обучение", "Machine learning"),
    "devops": ("DevOps", "DevOps", "DevOps"),
    "databases": ("Ma'lumotlar bazalari", "Базы данных", "Databases"),
    "cybersecurity": ("Kiberxavfsizlik", "Кибербезопасность", "Cybersecurity"),
    "game-development": ("O'yin yaratish", "Разработка игр", "Game development"),
    "web-scraping": ("Veb-skreyping", "Веб-скрейпинг", "Web scraping"),
}
