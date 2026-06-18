"""Career guide analysis with an offline fallback."""

from typing import Dict, List

from app.schemas.ai import AICareerResponse
from app.schemas.guide import GuideAnalyzeRequest


# Each entry maps one sub-specialty to its parent interest and dimension profile.
# Multiple sub-specialties share the same interest slug so the selection bonus
# applies to the whole family. Dimensions are the 2-3 most diagnostic for that role.
CAREERS: Dict[str, dict] = {
    # ── Information Technology ──────────────────────────────────────────────
    "it_software": {
        "interest": "it",
        "names": {"en": "Software Engineer", "ru": "Разработчик ПО", "uz": "Dasturiy ta'minot muhandisi"},
        "focus": {
            "en": "building reliable systems, writing clean code, debugging, and designing APIs",
            "ru": "создание надёжных систем, чистый код, отладка и проектирование API",
            "uz": "ishonchli tizim yaratish, toza kod yozish, xatolarni topish va API loyihalash",
        },
        "dimensions": ["logic", "technical"],
        "skills": ["Python or JavaScript", "Git and GitHub", "REST APIs", "databases"],
        "links": [
            "CS50 — https://cs50.harvard.edu/x/",
            "freeCodeCamp — https://www.freecodecamp.org/",
            "The Pragmatic Programmer — https://pragprog.com/titles/tpp20/",
            "roadmap.sh Backend — https://roadmap.sh/backend",
        ],
    },
    "it_data": {
        "interest": "it",
        "names": {"en": "Data Scientist", "ru": "Учёный по данным", "uz": "Data fanlari mutaxassisi"},
        "focus": {
            "en": "analysing data, building predictive models, data visualisation, and storytelling",
            "ru": "анализ данных, построение предсказательных моделей, визуализация и презентация",
            "uz": "ma'lumot tahlili, prognoz modellari yaratish, vizualizatsiya va taqdimot",
        },
        "dimensions": ["data", "logic"],
        "skills": ["Python", "pandas / NumPy", "SQL", "data visualisation"],
        "links": [
            "Kaggle Learn — https://www.kaggle.com/learn",
            "fast.ai Practical Deep Learning — https://course.fast.ai/",
            "Python for Data Analysis — https://wesmckinney.com/book/",
            "Towards Data Science — https://towardsdatascience.com/",
        ],
    },
    "it_devops": {
        "interest": "it",
        "names": {"en": "DevOps / Cloud Engineer", "ru": "DevOps / Облачный инженер", "uz": "DevOps / Cloud muhandisi"},
        "focus": {
            "en": "CI/CD pipelines, infrastructure as code, containerisation, and monitoring",
            "ru": "конвейеры CI/CD, инфраструктура как код, контейнеризация и мониторинг",
            "uz": "CI/CD pipeline, kod sifatida infratuzilma, konteynerlashtirish va monitoring",
        },
        "dimensions": ["technical", "data"],
        "skills": ["Linux", "Docker / Kubernetes", "Terraform", "cloud platforms"],
        "links": [
            "AWS Skill Builder — https://skillbuilder.aws/",
            "Docker Docs — https://docs.docker.com/",
            "The Phoenix Project — https://itrevolution.com/product/the-phoenix-project/",
            "roadmap.sh DevOps — https://roadmap.sh/devops",
        ],
    },
    # ── Design ──────────────────────────────────────────────────────────────
    "design_ux": {
        "interest": "design",
        "names": {"en": "UX/UI Designer", "ru": "UX/UI-дизайнер", "uz": "UX/UI dizayner"},
        "focus": {
            "en": "user research, interaction design, prototyping, and usability testing",
            "ru": "исследование пользователей, взаимодействие, прототипирование и юзабилити",
            "uz": "foydalanuvchi tadqiqoti, interfeys dizayni, prototiplash va foydalilikni sinash",
        },
        "dimensions": ["creativity", "people"],
        "skills": ["user research", "Figma", "usability testing", "design systems"],
        "links": [
            "Google UX Certificate — https://grow.google/certificates/ux-design/",
            "Nielsen Norman Group — https://www.nngroup.com/articles/",
            "The Design of Everyday Things — https://mitpress.mit.edu/9780262525671/the-design-of-everyday-things/",
            "Figma Learn — https://help.figma.com/hc/en-us/categories/360002051613",
        ],
    },
    "design_graphic": {
        "interest": "design",
        "names": {"en": "Graphic Designer", "ru": "Графический дизайнер", "uz": "Grafik dizayner"},
        "focus": {
            "en": "visual communication, typography, brand identity, and layout composition",
            "ru": "визуальная коммуникация, типографика, айдентика бренда и компоновка",
            "uz": "vizual kommunikatsiya, tipografiya, brend identifikatsiyasi va kompozitsiya",
        },
        "dimensions": ["creativity", "technical"],
        "skills": ["Adobe Illustrator / Photoshop", "typography", "color theory", "brand systems"],
        "links": [
            "Canva Design School — https://www.canva.com/designschool/",
            "Adobe Education Exchange — https://edex.adobe.com/",
            "Thinking with Type — http://thinkingwithtype.com/",
            "Behance — https://www.behance.net/",
        ],
    },
    "design_product": {
        "interest": "design",
        "names": {"en": "Product Designer", "ru": "Продуктовый дизайнер", "uz": "Mahsulot dizayneri"},
        "focus": {
            "en": "end-to-end product thinking, user journey mapping, cross-team collaboration, and design strategy",
            "ru": "сквозное продуктовое мышление, карты пользовательского пути и стратегия дизайна",
            "uz": "to'liq mahsulot tafakkuri, foydalanuvchi yo'lini xaritalash va dizayn strategiyasi",
        },
        "dimensions": ["people", "logic"],
        "skills": ["product strategy", "journey mapping", "stakeholder communication", "data-informed design"],
        "links": [
            "Interaction Design Foundation — https://www.interaction-design.org/",
            "IDEO Design Thinking — https://designthinking.ideo.com/",
            "Hooked — https://www.nirandfar.com/hooked/",
            "UX Collective — https://uxdesign.cc/",
        ],
    },
    # ── Marketing ───────────────────────────────────────────────────────────
    "marketing_digital": {
        "interest": "marketing",
        "names": {"en": "Digital Marketing Specialist", "ru": "Специалист по цифровому маркетингу", "uz": "Raqamli marketing mutaxassisi"},
        "focus": {
            "en": "audience research, paid campaigns, analytics, and multi-channel strategy",
            "ru": "исследование аудитории, платные кампании, аналитика и мультиканальная стратегия",
            "uz": "auditoriya tadqiqoti, pullik kampaniyalar, tahlil va ko'p kanalli strategiya",
        },
        "dimensions": ["creativity", "data"],
        "skills": ["Google Ads", "Meta Ads", "analytics", "campaign strategy"],
        "links": [
            "Google Skillshop — https://skillshop.withgoogle.com/",
            "Meta Blueprint — https://www.facebook.com/business/learn",
            "Marketing Made Simple — https://storybrand.com/marketing-made-simple-book/",
            "HubSpot Academy — https://academy.hubspot.com/",
        ],
    },
    "marketing_content": {
        "interest": "marketing",
        "names": {"en": "Content Strategist", "ru": "Контент-стратег", "uz": "Kontent strategisti"},
        "focus": {
            "en": "editorial planning, audience storytelling, SEO-driven writing, and brand voice",
            "ru": "редакционное планирование, сторителлинг, SEO-тексты и голос бренда",
            "uz": "tahririyat rejalashtirish, hikoya qilish, SEO yozuv va brend ovozi",
        },
        "dimensions": ["creativity", "people"],
        "skills": ["copywriting", "editorial calendar", "SEO basics", "content analytics"],
        "links": [
            "Copyblogger — https://copyblogger.com/",
            "HubSpot Content Marketing — https://academy.hubspot.com/courses/content-marketing",
            "Everybody Writes — https://annhandley.com/everybodywrites/",
            "Semrush Academy — https://www.semrush.com/academy/",
        ],
    },
    "marketing_seo": {
        "interest": "marketing",
        "names": {"en": "SEO / Growth Analyst", "ru": "SEO / Аналитик роста", "uz": "SEO / O'sish tahlilchisi"},
        "focus": {
            "en": "keyword research, technical SEO, link building, analytics, and growth experiments",
            "ru": "ключевые слова, технический SEO, ссылочная масса, аналитика и эксперименты роста",
            "uz": "kalit so'zlar, texnik SEO, havolalar, tahlil va o'sish tajribalari",
        },
        "dimensions": ["data", "logic"],
        "skills": ["keyword research", "Google Search Console", "analytics", "A/B testing"],
        "links": [
            "Ahrefs Academy — https://ahrefs.com/academy",
            "Google Search Central — https://developers.google.com/search/docs",
            "Moz Beginner's Guide — https://moz.com/beginners-guide-to-seo",
            "Reforge Blog — https://www.reforge.com/blog",
        ],
    },
    # ── Finance ─────────────────────────────────────────────────────────────
    "finance_analyst": {
        "interest": "finance",
        "names": {"en": "Financial Analyst", "ru": "Финансовый аналитик", "uz": "Moliyaviy tahlilchi"},
        "focus": {
            "en": "financial modelling, ratio analysis, forecasting, and business evaluation",
            "ru": "финансовое моделирование, коэффициентный анализ, прогнозирование и оценка",
            "uz": "moliyaviy modellashtirish, koeffitsientli tahlil, prognozlash va baholash",
        },
        "dimensions": ["data", "logic"],
        "skills": ["Excel", "financial modelling", "accounting basics", "business analysis"],
        "links": [
            "Corporate Finance Institute — https://corporatefinanceinstitute.com/",
            "Khan Academy Finance — https://www.khanacademy.org/economics-finance-domain",
            "Financial Intelligence — https://www.harpercollinsleadership.com/9781422144114/financial-intelligence/",
            "Aswath Damodaran — https://pages.stern.nyu.edu/~adamodar/",
        ],
    },
    "finance_investment": {
        "interest": "finance",
        "names": {"en": "Investment Analyst", "ru": "Инвестиционный аналитик", "uz": "Investitsiya tahlilchisi"},
        "focus": {
            "en": "equity research, valuation, portfolio analysis, and investment thesis writing",
            "ru": "исследование акций, оценка стоимости, анализ портфеля и инвестиционный тезис",
            "uz": "aksiya tadqiqoti, baholash, portfel tahlili va investitsiya thezisi yozish",
        },
        "dimensions": ["data", "creativity"],
        "skills": ["equity research", "DCF modelling", "Bloomberg basics", "investment writing"],
        "links": [
            "CFA Institute — https://www.cfainstitute.org/",
            "Yale Financial Markets — https://oyc.yale.edu/economics/econ-252-11",
            "Principles of Corporate Finance — https://www.mheducation.com/highered/product/principles-corporate-finance-brealey.html",
            "SEC EDGAR — https://www.sec.gov/edgar/search-and-access",
        ],
    },
    "finance_planning": {
        "interest": "finance",
        "names": {"en": "Financial Planner", "ru": "Финансовый планировщик", "uz": "Moliyaviy rejalashtiruvchi"},
        "focus": {
            "en": "personal finance, client advisory, retirement planning, and risk management",
            "ru": "личные финансы, консультирование клиентов, пенсионное планирование и управление рисками",
            "uz": "shaxsiy moliya, mijoz maslahati, pensiya rejalashtirish va risklarni boshqarish",
        },
        "dimensions": ["people", "data"],
        "skills": ["financial planning", "client communication", "risk assessment", "tax basics"],
        "links": [
            "CFP Board — https://www.cfp.net/",
            "Investopedia — https://www.investopedia.com/",
            "The Millionaire Next Door — https://www.thomasjstanley.com/the-millionaire-next-door/",
            "Coursera Personal Finance — https://www.coursera.org/learn/personal-finance",
        ],
    },
    # ── Engineering ─────────────────────────────────────────────────────────
    "engineering_mechanical": {
        "interest": "engineering",
        "names": {"en": "Mechanical Engineer", "ru": "Инженер-механик", "uz": "Mexanika muhandisi"},
        "focus": {
            "en": "mechanical design, CAD modelling, stress analysis, and prototyping",
            "ru": "механическое проектирование, CAD, расчёт нагрузок и прототипирование",
            "uz": "mexanik loyiha, CAD modellashtirish, kuchlanish tahlili va prototiplash",
        },
        "dimensions": ["technical", "logic"],
        "skills": ["engineering mathematics", "CAD (SolidWorks / AutoCAD)", "mechanics", "materials science"],
        "links": [
            "MIT OpenCourseWare Mechanical — https://ocw.mit.edu/search/?d=Mechanical%20Engineering",
            "Autodesk Learning — https://www.autodesk.com/learn",
            "Engineering Mechanics — https://www.pearson.com/en-us/subject-catalog/p/engineering-mechanics-statics/P200000003387",
            "edX Engineering — https://www.edx.org/learn/engineering",
        ],
    },
    "engineering_electrical": {
        "interest": "engineering",
        "names": {"en": "Electrical Engineer", "ru": "Инженер-электрик", "uz": "Elektr muhandisi"},
        "focus": {
            "en": "circuit design, electronics, embedded systems, and power systems",
            "ru": "проектирование схем, электроника, встроенные системы и энергосистемы",
            "uz": "sxema loyiha, elektronika, o'rnatilgan tizimlar va energiya tizimlari",
        },
        "dimensions": ["technical", "data"],
        "skills": ["circuit analysis", "Arduino / Raspberry Pi", "MATLAB", "PCB design"],
        "links": [
            "All About Circuits — https://www.allaboutcircuits.com/",
            "MIT 6.002 Electronics — https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/",
            "The Art of Electronics — https://artofelectronics.net/",
            "Coursera Embedded Systems — https://www.coursera.org/learn/introduction-embedded-systems",
        ],
    },
    "engineering_civil": {
        "interest": "engineering",
        "names": {"en": "Civil Engineer", "ru": "Гражданский инженер", "uz": "Qurilish muhandisi"},
        "focus": {
            "en": "structural design, infrastructure planning, materials, and project management",
            "ru": "проектирование конструкций, планирование инфраструктуры и управление проектами",
            "uz": "konstruksiya loyiha, infratuzilma rejalashtirish, materiallar va loyiha boshqaruvi",
        },
        "dimensions": ["logic", "people"],
        "skills": ["structural analysis", "AutoCAD Civil 3D", "project management", "materials testing"],
        "links": [
            "ASCE — https://www.asce.org/",
            "MIT OCW Civil Engineering — https://ocw.mit.edu/search/?d=Civil%20and%20Environmental%20Engineering",
            "Construction Project Management — https://www.coursera.org/learn/construction-project-management",
            "Engineering Fundamentals — https://www.coursera.org/learn/engineering-fundamentals",
        ],
    },
    # ── Healthcare ──────────────────────────────────────────────────────────
    "healthcare_clinician": {
        "interest": "healthcare",
        "names": {"en": "Healthcare Specialist", "ru": "Специалист в здравоохранении", "uz": "Sog'liqni saqlash mutaxassisi"},
        "focus": {
            "en": "patient care, clinical decision-making, evidence-based practice, and medical ethics",
            "ru": "уход за пациентами, клинические решения, доказательная медицина и медицинская этика",
            "uz": "bemorga g'amxo'rlik, klinik qarorlar, dalilga asoslangan amaliyot va tibbiy etika",
        },
        "dimensions": ["people", "data"],
        "skills": ["biology", "patient communication", "evidence-based practice", "clinical ethics"],
        "links": [
            "Khan Academy Health — https://www.khanacademy.org/science/health-and-medicine",
            "OpenWHO — https://openwho.org/",
            "Coursera Health — https://www.coursera.org/browse/health",
            "WHO Careers — https://www.who.int/careers",
        ],
    },
    "healthcare_public": {
        "interest": "healthcare",
        "names": {"en": "Public Health Analyst", "ru": "Аналитик общественного здоровья", "uz": "Jamoat salomatligi tahlilchisi"},
        "focus": {
            "en": "epidemiology, health data analysis, policy evaluation, and population-level interventions",
            "ru": "эпидемиология, анализ данных о здоровье, оценка политики и вмешательства на уровне популяции",
            "uz": "epidemiologiya, sog'liqqa oid ma'lumotlarni tahlil qilish va aholini sog'liqlashtirish",
        },
        "dimensions": ["data", "logic"],
        "skills": ["epidemiology", "statistical analysis", "health policy", "data visualisation"],
        "links": [
            "CDC Learning — https://www.cdc.gov/learning/",
            "Coursera Epidemiology — https://www.coursera.org/learn/epidemiology",
            "Our World in Data — https://ourworldindata.org/",
            "Johns Hopkins Public Health — https://publicspheres.jhu.edu/",
        ],
    },
    "healthcare_research": {
        "interest": "healthcare",
        "names": {"en": "Clinical Researcher", "ru": "Клинический исследователь", "uz": "Klinik tadqiqotchi"},
        "focus": {
            "en": "clinical trial design, biostatistics, regulatory affairs, and research ethics",
            "ru": "дизайн клинических испытаний, биостатистика, регуляторные вопросы и этика",
            "uz": "klinik sinovlar dizayni, biostatistika, tartibga solish va tadqiqot etikasi",
        },
        "dimensions": ["logic", "technical"],
        "skills": ["research methodology", "biostatistics", "GCP guidelines", "data management"],
        "links": [
            "NIH Research Training — https://researchtraining.nih.gov/",
            "Coursera Clinical Trials — https://www.coursera.org/learn/clinical-trials",
            "ClinicalTrials.gov — https://clinicaltrials.gov/",
            "Good Clinical Practice — https://ichgcp.net/",
        ],
    },
    # ── Education ───────────────────────────────────────────────────────────
    "education_designer": {
        "interest": "education",
        "names": {"en": "Learning Experience Designer", "ru": "Методист образовательных программ", "uz": "Ta'lim dasturlari metodisti"},
        "focus": {
            "en": "curriculum design, learner empathy, assessment creation, and instructional strategy",
            "ru": "проектирование учебных программ, эмпатия к учащимся, создание заданий и стратегия обучения",
            "uz": "o'quv dasturlari loyihalash, o'quvchiga empatiya, vazifa yaratish va o'qitish strategiyasi",
        },
        "dimensions": ["people", "creativity"],
        "skills": ["instructional design", "learning objectives", "assessment design", "LMS tools"],
        "links": [
            "OpenLearn Education — https://www.open.edu/openlearn/education-development",
            "Design for How People Learn — https://www.peachpit.com/store/design-for-how-people-learn-9780134211282",
            "Coursera Learning How to Learn — https://www.coursera.org/learn/learning-how-to-learn",
            "Edutopia — https://www.edutopia.org/",
        ],
    },
    "education_edtech": {
        "interest": "education",
        "names": {"en": "Educational Technologist", "ru": "Специалист по образовательным технологиям", "uz": "Ta'lim texnologiyalari mutaxassisi"},
        "focus": {
            "en": "learning management systems, educational software evaluation, blended learning, and digital literacy",
            "ru": "системы управления обучением, оценка образовательного ПО и смешанное обучение",
            "uz": "o'quv boshqaruv tizimlari, ta'lim dasturlari baholash va aralash o'qitish",
        },
        "dimensions": ["technical", "creativity"],
        "skills": ["LMS (Canvas / Moodle)", "instructional video production", "e-learning tools", "data analytics"],
        "links": [
            "ISTE — https://www.iste.org/",
            "Coursera Teaching Online — https://www.coursera.org/learn/teaching-online",
            "H5P — https://h5p.org/",
            "TED-Ed — https://ed.ted.com/",
        ],
    },
    "education_teacher": {
        "interest": "education",
        "names": {"en": "Teacher / Instructor", "ru": "Преподаватель", "uz": "O'qituvchi / Muallim"},
        "focus": {
            "en": "classroom facilitation, lesson planning, differentiated instruction, and formative assessment",
            "ru": "фасилитация, планирование уроков, дифференцированное обучение и формативная оценка",
            "uz": "dars o'tkazish, dars rejalashtirish, farqli o'qitish va formativ baholash",
        },
        "dimensions": ["people", "logic"],
        "skills": ["lesson planning", "classroom management", "formative assessment", "communication"],
        "links": [
            "Teach For All — https://teachforall.org/",
            "Khan Academy Teacher Resources — https://www.khanacademy.org/teacher",
            "Edutopia — https://www.edutopia.org/",
            "Harvard Graduate School of Education — https://www.gse.harvard.edu/ideas/usable-knowledge",
        ],
    },
    # ── Business ────────────────────────────────────────────────────────────
    "business_pm": {
        "interest": "business",
        "names": {"en": "Product Manager", "ru": "Продакт-менеджер", "uz": "Mahsulot menejeri"},
        "focus": {
            "en": "customer discovery, roadmapping, cross-team alignment, and evidence-based product decisions",
            "ru": "исследование клиентов, дорожная карта, кросс-командная работа и продуктовые решения",
            "uz": "mijozni o'rganish, yo'l xaritasi, jamoalar o'rtasidagi kelishuv va mahsulot qarorlari",
        },
        "dimensions": ["people", "logic"],
        "skills": ["customer discovery", "product roadmap", "data analysis", "stakeholder management"],
        "links": [
            "Y Combinator Startup School — https://www.startupschool.org/",
            "Product School — https://productschool.com/resources",
            "The Lean Startup — https://theleanstartup.com/book",
            "Strategyzer — https://www.strategyzer.com/",
        ],
    },
    "business_analyst": {
        "interest": "business",
        "names": {"en": "Business Analyst", "ru": "Бизнес-аналитик", "uz": "Biznes tahlilchi"},
        "focus": {
            "en": "requirements gathering, process mapping, stakeholder interviews, and solution design",
            "ru": "сбор требований, картирование процессов, интервью и проектирование решений",
            "uz": "talablarni yig'ish, jarayon xaritalash, manfaatdorlar bilan suhbat va yechim loyihalash",
        },
        "dimensions": ["data", "people"],
        "skills": ["requirements analysis", "process mapping", "SQL basics", "stakeholder communication"],
        "links": [
            "IIBA — https://www.iiba.org/",
            "Coursera Business Analysis — https://www.coursera.org/professional-certificates/ibm-business-analyst",
            "Business Analysis Body of Knowledge — https://www.iiba.org/career-resources/a-business-analysis-professional-s-foundation-for-success/babok/",
            "Lucidchart — https://www.lucidchart.com/pages/",
        ],
    },
    "business_strategy": {
        "interest": "business",
        "names": {"en": "Strategy Consultant", "ru": "Стратегический консультант", "uz": "Strategik konsultant"},
        "focus": {
            "en": "market analysis, competitive intelligence, structured problem-solving, and executive presentations",
            "ru": "анализ рынка, конкурентная разведка, структурированное решение задач и презентации",
            "uz": "bozor tahlili, raqobat razvedkasi, tizimli muammo yechish va taqdimotlar",
        },
        "dimensions": ["logic", "creativity"],
        "skills": ["structured problem-solving", "PowerPoint / slides", "financial literacy", "frameworks (MECE, etc.)"],
        "links": [
            "Harvard Business Review — https://hbr.org/",
            "McKinsey & Company Insights — https://www.mckinsey.com/insights",
            "Consulting Case Interview — https://www.caseinterview.com/",
            "The Pyramid Principle — https://barbaraminto.com/",
        ],
    },
}


TEXT = {
    "en": {
        "summary": "Your answers show a practical learner who wants work that matches personal interests and creates visible results. You appear ready to build skills step by step, test ideas through projects, and improve through feedback. The paths below balance your selected interests with your preferred way of solving problems, collaborating, and learning.",
        "strengths": ["Curiosity and willingness to learn", "Practical problem solving", "Ability to connect interests with goals", "Growth-oriented mindset"],
        "weaknesses": ["Build a consistent weekly learning routine", "Gain more experience through real projects", "Practice explaining your decisions clearly"],
        "reason": "This path closely matches one of your selected interests and gives you room to combine structured learning with practical projects. Your assessment suggests that you can grow fastest by learning the foundations, building a visible portfolio, and getting feedback from people already working in the field.",
        "levels": [
            "Months 1-2: learn the foundations and essential terminology",
            "Months 3-4: practice the core tools through small weekly tasks",
            "Months 5-6: build two portfolio projects and document the process",
            "Months 7-9: complete an internship, bootcamp, or mentored project",
            "Months 10-12: specialise, improve your portfolio, and prepare for interviews",
            "Year 2: earn a respected certificate or complete university-level coursework",
            "Year 2: contribute to a real team, open-source project, or professional community",
            "Year 3: lead a substantial project and develop a clear specialisation",
        ],
    },
    "ru": {
        "summary": "Ваши ответы показывают практичного и любознательного человека, которому важно видеть результат своей работы. Вы готовы развивать навыки поэтапно, проверять знания на проектах и становиться сильнее благодаря обратной связи. Рекомендации ниже объединяют выбранные интересы с вашим стилем решения задач, обучения и командной работы.",
        "strengths": ["Любознательность и готовность учиться", "Практический подход к задачам", "Умение связывать интересы с целями", "Ориентация на развитие"],
        "weaknesses": ["Создать стабильный недельный график обучения", "Получить опыт на реальных проектах", "Учиться ясно объяснять свои решения"],
        "reason": "Это направление соответствует одному из ваших главных интересов и позволяет совмещать системное обучение с практикой. По ответам видно, что лучший рост даст изучение основ, создание портфолио и регулярная обратная связь от специалистов.",
        "levels": [
            "1-2 месяц: изучить основы и ключевые термины",
            "3-4 месяц: освоить основные инструменты на небольших задачах",
            "5-6 месяц: создать два проекта для портфолио",
            "7-9 месяц: пройти стажировку, буткемп или проект с ментором",
            "10-12 месяц: выбрать специализацию и подготовиться к собеседованиям",
            "2 год: получить признанный сертификат или пройти университетский курс",
            "2 год: поработать в реальной команде или профессиональном сообществе",
            "3 год: возглавить крупный проект и углубить специализацию",
        ],
    },
    "uz": {
        "summary": "Javoblaringiz siz natijasi ko'rinadigan ishni qadrlaydigan, qiziquvchan va amaliy o'rganuvchi ekaningizni ko'rsatadi. Siz ko'nikmalarni bosqichma-bosqich rivojlantirishga, bilimni loyihalarda sinashga va fikr-mulohaza orqali o'sishga tayyorsiz. Quyidagi yo'nalishlar tanlagan qiziqishlaringizni muammo yechish, o'rganish va jamoada ishlash uslubingiz bilan birlashtiradi.",
        "strengths": ["Qiziquvchanlik va o'rganishga tayyorlik", "Muammolarga amaliy yondashuv", "Qiziqishlarni maqsad bilan bog'lash", "Rivojlanishga yo'nalgan fikrlash"],
        "weaknesses": ["Barqaror haftalik o'quv rejimini yaratish", "Real loyihalarda ko'proq tajriba olish", "Qarorlarni aniq tushuntirishni mashq qilish"],
        "reason": "Bu kasb siz tanlagan asosiy qiziqishlardan biriga mos keladi va tizimli o'qishni amaliy loyihalar bilan birlashtiradi. Javoblaringizga ko'ra, asoslarni o'rganish, ko'rinadigan portfolio yaratish va soha mutaxassislaridan muntazam fikr olish sizga eng tez o'sish imkonini beradi.",
        "levels": [
            "1-2 oy: asoslar va muhim atamalarni o'rganish",
            "3-4 oy: asosiy vositalarni kichik haftalik vazifalarda ishlatish",
            "5-6 oy: portfolio uchun ikkita loyiha yaratish",
            "7-9 oy: stajirovka, bootcamp yoki mentorli loyihada qatnashish",
            "10-12 oy: ixtisoslik tanlash va suhbatlarga tayyorlanish",
            "2-yil: tan olingan sertifikat yoki universitet darajasidagi kursni tugatish",
            "2-yil: real jamoa yoki professional hamjamiyat loyihasida ishlash",
            "3-yil: katta loyihani boshqarish va ixtisoslikni chuqurlashtirish",
        ],
    },
}


DIMENSION_LABELS = {
    "uz": {
        "logic": "mantiqiy muammo yechish",
        "data": "raqam va dalillar bilan ishlash",
        "creativity": "yangi g'oya yaratish",
        "people": "odamlarni tushunish va muloqot",
        "technical": "texnik va amaliy vazifalar",
    },
    "ru": {
        "logic": "логическое решение задач",
        "data": "работа с числами и фактами",
        "creativity": "создание новых идей",
        "people": "понимание людей и общение",
        "technical": "технические и практические задачи",
    },
    "en": {
        "logic": "logical problem solving",
        "data": "working with numbers and evidence",
        "creativity": "creating new ideas",
        "people": "understanding and communicating with people",
        "technical": "technical and hands-on work",
    },
}


def _career_reason(
    language: str,
    career: dict,
    key: str,
    selected: List[str],
    averages: Dict[str, float],
    strongest_answers: List[str],
) -> str:
    dimensions = career["dimensions"]
    ranked_dimensions = sorted(
        dimensions,
        key=lambda dimension: averages.get(dimension, 3),
        reverse=True,
    )
    strongest = ranked_dimensions[0]
    developing = ranked_dimensions[-1]
    evidence = "; ".join(strongest_answers[:2])
    interest = career["interest"]
    selected_text = {
        "uz": "Bu sohani qiziqish sifatida o'zingiz tanlaganingiz ham tavsiyani kuchaytiradi."
        if interest in selected else
        "Bu yo'nalish tanlangan sohalardan tashqarida bo'lsa-da, javoblaringizdagi kuchli signallar sabab top-3 ga kirdi.",
        "ru": "То, что вы сами выбрали эту сферу среди интересов, дополнительно усиливает рекомендацию."
        if interest in selected else
        "Хотя эта профессия не была среди выбранных сфер, сильные сигналы в ответах вывели ее в топ-3.",
        "en": "Your explicit interest in this field strengthens the recommendation."
        if interest in selected else
        "Although this was not a selected field, strong assessment signals placed it in the top three.",
    }[language]

    if language == "uz":
        return (
            f"Bu yo'nalish sizdagi {DIMENSION_LABELS[language][strongest]} ko'rsatkichi "
            f"({averages.get(strongest, 3):.1f}/5) bilan yaxshi mos tushadi. Ayniqsa "
            f'"{evidence}" degan javoblaringiz kasb uchun kerak bo\'ladigan {career["focus"][language]} '
            f"ko'nikmalariga yaqin ekaningizni ko'rsatadi. {selected_text} Shu bilan birga, "
            f"{DIMENSION_LABELS[language][developing]} ko'rsatkichi "
            f"({averages.get(developing, 3):.1f}/5) mustahkamlash kerak bo'lgan yo'nalish: uni kichik amaliy "
            f"loyihalar va muntazam fikr-mulohaza orqali rivojlantirish kerak. Dastlab real vazifa "
            f"bajaring, natijani portfolio sifatida yozib boring va shu sohadagi mutaxassisdan tekshirtiring."
        )
    if language == "ru":
        return (
            f"Это направление хорошо согласуется с вашим показателем «{DIMENSION_LABELS[language][strongest]}» "
            f"({averages.get(strongest, 3):.1f}/5). Ответы «{evidence}» особенно связаны с такими "
            f"задачами профессии, как {career['focus'][language]}. {selected_text} При этом показатель "
            f"«{DIMENSION_LABELS[language][developing]}» ({averages.get(developing, 3):.1f}/5) полезно "
            f"целенаправленно развивать через небольшие практические проекты и регулярную обратную связь. "
            f"Начните с реальной задачи, оформляйте результат как кейс для портфолио и просите специалиста "
            f"проверять не только итог, но и ход ваших решений."
        )
    return (
        f"This path aligns well with your {DIMENSION_LABELS[language][strongest]} score "
        f"({averages.get(strongest, 3):.1f}/5). Your responses \"{evidence}\" connect directly to "
        f"career work involving {career['focus'][language]}. {selected_text} Your "
        f"{DIMENSION_LABELS[language][developing]} score ({averages.get(developing, 3):.1f}/5) is worth "
        f"strengthening through small practical projects and regular feedback. Start with one real "
        f"task, document the result as a portfolio case study, and ask a practitioner to review both your "
        f"outcome and the reasoning behind it."
    )


def build_fallback_recommendations(request: GuideAnalyzeRequest) -> AICareerResponse:
    language = request.language
    copy = TEXT[language]
    # Collect parent interest slugs that the user selected and that we know about
    known_interests = {career["interest"] for career in CAREERS.values()}
    selected = [item for item in request.interests if item in known_interests]

    # Average score per assessment dimension
    category_scores: Dict[str, List[int]] = {}
    for answer in request.answers:
        category_scores.setdefault(answer.category, []).append(answer.score)
    averages = {
        category: sum(scores) / len(scores)
        for category, scores in category_scores.items()
    }

    # Normalized domain bonus: average of the career's key dimension scores
    # (equal weight per career regardless of how many dimensions it uses)
    SELECTION_BONUS = 4.0
    domain_bonus = {
        key: sum(averages.get(dim, 3.0) for dim in career["dimensions"]) / len(career["dimensions"])
        for key, career in CAREERS.items()
    }
    ranking_score = {
        key: domain_bonus[key] + (SELECTION_BONUS if CAREERS[key]["interest"] in selected else 0.0)
        for key in CAREERS
    }

    # Pick top 3 sub-specialties; guarantee at least 2 come from selected interests when possible
    ranked_keys = sorted(CAREERS, key=lambda k: ranking_score[k], reverse=True)
    selected_picks: List[str] = []
    other_picks: List[str] = []
    for key in ranked_keys:
        if CAREERS[key]["interest"] in selected:
            selected_picks.append(key)
        else:
            other_picks.append(key)
    top3: List[str] = []
    needed_from_selected = min(2, len(selected_picks))
    top3.extend(selected_picks[:needed_from_selected])
    for key in ranked_keys:
        if len(top3) >= 3:
            break
        if key not in top3:
            top3.append(key)

    careers_out: List[dict] = []
    for index, key in enumerate(top3):
        career = CAREERS[key]
        links = career["links"]
        strongest_answers = [
            answer.question
            for answer in sorted(request.answers, key=lambda item: item.score, reverse=True)
            if answer.category in career["dimensions"] and answer.score >= 4
        ]
        if len(strongest_answers) < 2:
            strongest_answers = [
                answer.question
                for answer in sorted(request.answers, key=lambda item: item.score, reverse=True)[:2]
            ]
        rs = ranking_score[key]
        careers_out.append({
            "name": career["names"][language],
            "match_score": min(95, max(65, round(rs * 10 + 20 - index * 7))),
            "reason": _career_reason(language, career, key, selected, averages, strongest_answers),
            "roadmap": {
                "beginner": copy["levels"][:4],
                "intermediate": copy["levels"][4:7],
                "advanced": copy["levels"][7:],
            },
            "resources": {
                "books": [links[2]],
                "courses": links[:2],
                "youtube_channels": [
                    f"YouTube — https://www.youtube.com/results?search_query={career['names']['en'].replace(' ', '+')}+tutorial"
                ],
                "websites": [links[3]],
            },
        })

    return AICareerResponse(
        personality_summary=copy["summary"],
        strengths=copy["strengths"],
        weaknesses=copy["weaknesses"],
        recommended_careers=careers_out,
    )
