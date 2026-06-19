"""Detailed learning paths and offline module tutoring."""

import re
from functools import lru_cache
from typing import Dict, List, Tuple

from app.schemas.guide import (
    LearningPathRequest,
    LearningPathResponse,
    ModuleChatRequest,
    ModuleChatResponse,
    ModuleQuizQuestion,
    QuizOption,
)
from app.services.learning import (
    KeywordCatalogResolver,
    LearningPathBuilder,
    TutorContextService,
)


Resource = Tuple[str, str, str]
ModuleSeed = Tuple[str, str, List[str], List[Resource]]

_catalog_resolver = KeywordCatalogResolver()
_tutor_context = TutorContextService()


COMMON = {
    "uz": {
        "overview": "{career} uchun ushbu yo'l asoslardan boshlab amaliy portfolio va ishga tayyorgarlikkacha olib boradi. Har bir modulni tartib bilan o'qing, loyihani bajaring va testdan o'ting.",
        "duration": "8-12 oy",
        "objectives": ["Asosiy tushunchalarni amalda qo'llash", "Portfolio uchun ko'rinadigan natija yaratish", "Bilimni test va loyiha bilan tekshirish"],
        "project": "{topic} bo'yicha kichik, ishlaydigan loyiha yarating va qarorlaringizni README faylida tushuntiring.",
        "quiz_question": "{topic} modulini o'rganishda eng to'g'ri yondashuv qaysi?",
        "quiz_options": ["Nazariyani amaliy mashq bilan mustahkamlash", "Faqat atamalarni yodlash", "Loyihani tekshirmasdan tugatish", "Fikr-mulohazani e'tiborsiz qoldirish"],
        "quiz_explanation": "Nazariya amaliy mashq, tekshiruv va fikr-mulohaza bilan birga qo'llanganda bilim mustahkamlanadi.",
        "chat": "Siz hozir “{module}” modulini o‘rganyapsiz. Savolingiz: “{question}”. Avval moduldagi asosiy tushunchani kichik qismlarga ajrating, keyin bitta sodda misolda sinab ko‘ring va natijani tekshiring. Muayyan tushuncha yoki vazifani yozsangiz, uni bosqichma-bosqich tushuntirib beraman.",
        "suggestions": ["Oddiy misol bilan tushuntir", "Menga mashq ber", "Bilimimni tekshir"],
    },
    "ru": {
        "overview": "Этот путь по профессии «{career}» ведет от основ к практическому портфолио и подготовке к работе. Проходите модули по порядку, выполняйте проекты и проверяйте знания тестами.",
        "duration": "8-12 месяцев",
        "objectives": ["Применить основные понятия на практике", "Создать заметный результат для портфолио", "Проверить знания проектом и тестом"],
        "project": "Создайте небольшой рабочий проект по теме «{topic}» и объясните решения в README.",
        "quiz_question": "Какой подход лучше всего подходит для изучения модуля «{topic}»?",
        "quiz_options": ["Закреплять теорию практикой", "Только запоминать термины", "Не проверять готовый проект", "Игнорировать обратную связь"],
        "quiz_explanation": "Знания закрепляются, когда теория сопровождается практикой, проверкой результата и обратной связью.",
        "chat": "Сейчас вы изучаете модуль «{module}». Ваш вопрос: «{question}». Разделите тему на небольшие части, проверьте одну идею на простом примере и сравните результат с целью модуля. Напишите конкретное понятие или задание, и я объясню его по шагам.",
        "suggestions": ["Объясни на простом примере", "Дай мне упражнение", "Проверь мои знания"],
    },
    "en": {
        "overview": "This {career} path takes you from foundations to a practical portfolio and job preparation. Complete modules in order, build each project, and use the quizzes to check your understanding.",
        "duration": "8-12 months",
        "objectives": ["Apply the core concepts in practice", "Create a visible portfolio outcome", "Validate learning through a project and quiz"],
        "project": "Build a small working project about {topic} and explain your decisions in a README.",
        "quiz_question": "What is the best approach when studying the {topic} module?",
        "quiz_options": ["Reinforce theory with practice", "Only memorize terminology", "Finish without checking the result", "Ignore feedback"],
        "quiz_explanation": "Learning becomes durable when theory is combined with practice, result checking, and feedback.",
        "chat": "You are studying the “{module}” module. Your question is: “{question}”. Break the topic into small parts, test one idea with a simple example, and compare the result with the module goal. Share a specific concept or task and I will explain it step by step.",
        "suggestions": ["Explain with a simple example", "Give me an exercise", "Test my knowledge"],
    },
}


CATALOGS: Dict[str, List[ModuleSeed]] = {
    "technology": [
        ("Python Foundations", "syntax, variables, conditions, loops, functions, and debugging", ["Python syntax", "Data types and control flow", "Functions and modules", "Errors and debugging", "Small command-line programs"], [
            ("Python Tutorial", "https://docs.python.org/3/tutorial/", "documentation"),
            ("CS50P", "https://cs50.harvard.edu/python/", "course"),
            ("Automate the Boring Stuff with Python", "https://automatetheboringstuff.com/", "book"),
            ("Real Python", "https://realpython.com/", "article"),
        ]),
        ("Git and Developer Workflow", "version control, GitHub, collaboration, and clean project structure", ["Repositories and commits", "Branches and merges", "Pull requests", "README and documentation", "Issue-based workflow"], [
            ("Pro Git", "https://git-scm.com/book/en/v2", "book"),
            ("GitHub Skills", "https://skills.github.com/", "course"),
            ("Git Documentation", "https://git-scm.com/doc", "documentation"),
            ("GitHub Docs", "https://docs.github.com/", "documentation"),
        ]),
        ("Data Structures and Algorithms", "problem solving, complexity, collections, searching, and sorting", ["Complexity basics", "Lists, stacks, and queues", "Maps and sets", "Searching and sorting", "Problem-solving patterns"], [
            ("Open Data Structures", "https://opendatastructures.org/", "book"),
            ("VisuAlgo", "https://visualgo.net/en", "article"),
            ("LeetCode Explore", "https://leetcode.com/explore/", "course"),
            ("MIT 6.006", "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/", "course"),
        ]),
        ("Web APIs and Backend", "HTTP, REST APIs, FastAPI, validation, and testing", ["HTTP request lifecycle", "REST resource design", "FastAPI routes", "Pydantic validation", "API tests and error handling"], [
            ("FastAPI Tutorial", "https://fastapi.tiangolo.com/tutorial/", "documentation"),
            ("MDN HTTP", "https://developer.mozilla.org/en-US/docs/Web/HTTP", "documentation"),
            ("Postman Learning Center", "https://learning.postman.com/", "course"),
            ("pytest Documentation", "https://docs.pytest.org/", "documentation"),
        ]),
        ("Databases and SQL", "relational modeling, SQL queries, PostgreSQL, and application integration", ["Tables and relationships", "SELECT and filtering", "Joins and aggregation", "Indexes and transactions", "ORM integration"], [
            ("SQLBolt", "https://sqlbolt.com/", "course"),
            ("PostgreSQL Tutorial", "https://www.postgresql.org/docs/current/tutorial.html", "documentation"),
            ("SQLAlchemy Tutorial", "https://docs.sqlalchemy.org/en/20/tutorial/", "documentation"),
            ("Database Design for Mere Mortals", "https://www.pearson.com/en-us/subject-catalog/p/database-design-for-mere-mortals/P200000000494", "book"),
        ]),
        ("Portfolio and Job Readiness", "deployment, system design basics, portfolio quality, and interview preparation", ["Deploying an application", "Logging and configuration", "System design fundamentals", "Portfolio case studies", "Technical interview practice"], [
            ("roadmap.sh Backend", "https://roadmap.sh/backend", "article"),
            ("The System Design Primer", "https://github.com/donnemartin/system-design-primer", "article"),
            ("Render Docs", "https://render.com/docs", "documentation"),
            ("GitHub Student Developer Pack", "https://education.github.com/pack", "community"),
        ]),
    ],
    "finance": [
        ("Accounting Foundations", "financial statements, bookkeeping, and accounting principles", ["Income statement", "Balance sheet", "Cash flow statement", "Double-entry accounting", "Accounting ratios"], [
            ("Khan Academy Finance", "https://www.khanacademy.org/economics-finance-domain", "course"),
            ("AccountingCoach", "https://www.accountingcoach.com/", "course"),
            ("OpenStax Principles of Accounting", "https://openstax.org/details/books/principles-financial-accounting", "book"),
        ]),
        ("Excel for Financial Analysis", "spreadsheets, formulas, data cleaning, and dashboards", ["Core formulas", "Lookup functions", "Pivot tables", "Charts and dashboards", "Model organization"], [
            ("Microsoft Excel Training", "https://support.microsoft.com/en-us/excel", "documentation"),
            ("ExcelJet", "https://exceljet.net/", "article"),
            ("CFI Excel Courses", "https://corporatefinanceinstitute.com/resources/excel/", "course"),
        ]),
        ("Corporate Finance", "time value of money, capital structure, valuation, and investment decisions", ["Time value of money", "Cost of capital", "Capital budgeting", "Risk and return", "Company valuation"], [
            ("Damodaran Online", "https://pages.stern.nyu.edu/~adamodar/", "course"),
            ("MIT Finance Theory I", "https://ocw.mit.edu/courses/15-401-finance-theory-i-fall-2008/", "course"),
            ("Principles of Corporate Finance", "https://www.mheducation.com/highered/product/principles-corporate-finance-brealey.html", "book"),
        ]),
        ("Financial Modeling", "forecasting, scenario analysis, and three-statement models", ["Revenue forecasting", "Expense assumptions", "Three-statement links", "Scenario analysis", "Model checks"], [
            ("CFI Financial Modeling", "https://corporatefinanceinstitute.com/resources/financial-modeling/", "course"),
            ("Wall Street Prep Resources", "https://www.wallstreetprep.com/knowledge/", "article"),
            ("SEC EDGAR", "https://www.sec.gov/edgar/search-and-access", "documentation"),
        ]),
        ("Markets and Risk", "financial markets, portfolio concepts, and risk management", ["Asset classes", "Diversification", "Market risk", "Credit risk", "Portfolio measurement"], [
            ("Investor.gov", "https://www.investor.gov/introduction-investing", "article"),
            ("CFA Institute Insights", "https://www.cfainstitute.org/insights", "article"),
            ("Yale Financial Markets", "https://oyc.yale.edu/economics/econ-252-11", "course"),
        ]),
        ("Analyst Portfolio and Interviews", "case studies, reports, presentations, and analyst recruitment", ["Company research", "Investment memo", "Dashboard presentation", "Ethics and communication", "Interview cases"], [
            ("CFA Institute Career Resources", "https://www.cfainstitute.org/programs/cfa-program/careers", "community"),
            ("Financial Modeling World Cup", "https://fmworldcup.com/", "community"),
            ("Harvard Business Review Finance", "https://hbr.org/topic/subject/finance-and-investing", "article"),
        ]),
    ],
    "marketing": [
        ("Marketing Foundations", "customers, positioning, funnels, and value propositions", ["Customer needs", "Segmentation", "Positioning", "Marketing funnel", "Value proposition"], [
            ("HubSpot Academy", "https://academy.hubspot.com/", "course"),
            ("Google Digital Garage", "https://grow.google/intl/en_pk/courses-and-tools/", "course"),
            ("Marketing Made Simple", "https://storybrand.com/marketing-made-simple-book/", "book"),
        ]),
        ("Content and Copywriting", "content strategy, persuasive writing, and editorial planning", ["Audience research", "Headlines", "Content formats", "Editorial calendar", "Calls to action"], [
            ("Copyblogger", "https://copyblogger.com/", "article"),
            ("HubSpot Content Marketing", "https://academy.hubspot.com/courses/content-marketing", "course"),
            ("Everybody Writes", "https://annhandley.com/everybodywrites/", "book"),
        ]),
        ("SEO and Web Analytics", "search intent, technical SEO, measurement, and reporting", ["Keyword intent", "On-page SEO", "Technical basics", "Google Analytics", "Search reporting"], [
            ("Google Search Central", "https://developers.google.com/search/docs", "documentation"),
            ("Google Analytics Academy", "https://skillshop.exceedlms.com/student/catalog/list?category_ids=6431-google-analytics", "course"),
            ("Ahrefs SEO Guide", "https://ahrefs.com/seo", "article"),
        ]),
        ("Paid Campaigns", "campaign planning, targeting, creative testing, and optimization", ["Campaign objectives", "Audience targeting", "Creative variants", "Budgeting", "Performance optimization"], [
            ("Google Ads Skillshop", "https://skillshop.withgoogle.com/googleads", "course"),
            ("Meta Blueprint", "https://www.facebook.com/business/learn", "course"),
            ("TikTok Academy", "https://www.tiktokacademy.com/", "course"),
        ]),
        ("Research and Growth Experiments", "market research, experimentation, retention, and lifecycle marketing", ["Interview research", "Survey design", "Experiment hypotheses", "A/B testing", "Retention metrics"], [
            ("Think with Google", "https://www.thinkwithgoogle.com/", "article"),
            ("Optimizely Experimentation", "https://www.optimizely.com/optimization-glossary/ab-testing/", "article"),
            ("Reforge Blog", "https://www.reforge.com/blog", "article"),
        ]),
        ("Portfolio and Campaign Strategy", "integrated strategy, case studies, reporting, and job preparation", ["Campaign brief", "Channel mix", "Measurement plan", "Case study writing", "Portfolio presentation"], [
            ("Google Trends", "https://trends.google.com/", "documentation"),
            ("Canva Design School", "https://www.canva.com/designschool/", "course"),
            ("AMA Marketing Resources", "https://www.ama.org/marketing-news/", "community"),
        ]),
    ],
    "design": [
        ("Design Thinking and Research", "user research, problem framing, empathy maps, and design briefs", ["Empathy mapping", "User interviews", "Problem statements", "How-might-we questions", "Design brief writing"], [
            ("IDEO Design Thinking", "https://designthinking.ideo.com/", "article"),
            ("Nielsen Norman Group", "https://www.nngroup.com/articles/", "article"),
            ("Stanford d.school Resources", "https://dschool.stanford.edu/resources", "course"),
            ("Google Design", "https://design.google/", "article"),
        ]),
        ("Visual Foundations", "typography, colour theory, grid systems, and visual hierarchy", ["Typography basics", "Colour and contrast", "Grid and spacing", "Visual hierarchy", "Design principles"], [
            ("Canva Design School", "https://www.canva.com/designschool/", "course"),
            ("Refactoring UI", "https://www.refactoringui.com/", "book"),
            ("Google Fonts", "https://fonts.google.com/", "documentation"),
            ("Coolors", "https://coolors.co/", "article"),
        ]),
        ("Figma and Prototyping", "components, auto-layout, frames, variants, and interactive prototypes", ["Frames and groups", "Components and variants", "Auto-layout", "Interactive prototypes", "Developer handoff"], [
            ("Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613", "documentation"),
            ("Figma Community Files", "https://www.figma.com/community", "community"),
            ("UI Prep", "https://www.uiprep.com/", "course"),
            ("Design+Code", "https://designcode.io/", "course"),
        ]),
        ("UX Writing and Microcopy", "interface language, error messages, onboarding copy, and tone", ["Microcopy principles", "Error and empty states", "Onboarding flows", "Tone and voice", "Accessibility in language"], [
            ("Google Material Writing", "https://m3.material.io/foundations/content/overview", "documentation"),
            ("UX Writing Hub", "https://uxwritinghub.com/", "course"),
            ("Mailchimp Content Style Guide", "https://styleguide.mailchimp.com/", "article"),
            ("Microsoft Writing Style Guide", "https://learn.microsoft.com/en-us/style-guide/welcome/", "documentation"),
        ]),
        ("Usability Testing and Iteration", "test planning, moderated sessions, affinity mapping, and design revisions", ["Test script writing", "Moderated sessions", "Affinity mapping", "Priority revisions", "Iteration cycles"], [
            ("Maze Research", "https://maze.co/guides/usability-testing/", "article"),
            ("UsabilityHub", "https://www.usabilityhub.com/", "course"),
            ("Nielsen Norman UX Research", "https://www.nngroup.com/courses/ux-research/", "course"),
            ("Optimal Workshop", "https://www.optimalworkshop.com/learn/", "article"),
        ]),
        ("Portfolio and Design Career", "case study writing, portfolio presentation, design interviews, and job search", ["Case study structure", "Portfolio site setup", "Design challenge practice", "Design critique", "Interview preparation"], [
            ("UX Portfolio Formula", "https://www.uxportfolioformula.com/", "article"),
            ("Behance", "https://www.behance.net/", "community"),
            ("Dribbble", "https://dribbble.com/", "community"),
            ("Designer News", "https://www.designernews.co/", "community"),
        ]),
    ],
    "engineering": [
        ("Engineering Fundamentals", "mathematics, physics, units, and problem-solving methodology", ["Dimensional analysis", "Free body diagrams", "Unit conversions", "Engineering math review", "Problem-solving frameworks"], [
            ("MIT OpenCourseWare Engineering", "https://ocw.mit.edu/courses/find-by-topic/#cat=engineering", "course"),
            ("Khan Academy Physics", "https://www.khanacademy.org/science/physics", "course"),
            ("Engineering Toolbox", "https://www.engineeringtoolbox.com/", "documentation"),
            ("Paul's Online Math Notes", "https://tutorial.math.lamar.edu/", "article"),
        ]),
        ("CAD and Technical Drawing", "2D drafting, 3D modelling, tolerancing, and drawing standards", ["2D technical drawings", "3D solid modelling", "Geometric tolerancing", "Drawing standards", "Assembly drawings"], [
            ("Autodesk Fusion 360 Learn", "https://www.autodesk.com/products/fusion-360/learn-training-tutorials", "course"),
            ("GrabCAD Community", "https://grabcad.com/library", "community"),
            ("Engineering Drawing Academy", "https://www.udemy.com/topic/technical-drawing/", "course"),
            ("Thingiverse", "https://www.thingiverse.com/", "community"),
        ]),
        ("Materials and Manufacturing", "material properties, selection, manufacturing processes, and quality", ["Metals and polymers", "Material selection", "Machining and casting", "Joining methods", "Quality and inspection"], [
            ("MIT Materials", "https://ocw.mit.edu/courses/3-091-introduction-to-solid-state-chemistry-fall-2018/", "course"),
            ("ASM International", "https://www.asminternational.org/learn", "article"),
            ("Granta EduPack", "https://www.ansys.com/academic/educators/ansys-granta-edupack", "documentation"),
            ("Manufacturing Engineering and Technology", "https://www.pearson.com/en-us/subject-catalog/p/manufacturing-engineering-and-technology/P200000003472", "book"),
        ]),
        ("Structural and Systems Analysis", "stress analysis, failure modes, FEA basics, and system reliability", ["Stress and strain", "Failure mode analysis", "FEA fundamentals", "Factor of safety", "Reliability concepts"], [
            ("MIT Structural Mechanics", "https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/", "course"),
            ("SimScale FEA", "https://www.simscale.com/docs/simulation-setup/analysis-types/static-analysis/", "documentation"),
            ("Shigley's Mechanical Engineering Design", "https://www.mheducation.com/highered/product/shigley-s-mechanical-engineering-design-budynas-nisbett/M9781264228829.html", "book"),
            ("ASME", "https://www.asme.org/learning-development/find-course-publication", "community"),
        ]),
        ("Project Execution and Standards", "project management, engineering documentation, codes, and handover", ["Project scoping", "Engineering standards", "Risk and change management", "Technical documentation", "Project handover"], [
            ("PMI Engineering PM", "https://www.pmi.org/", "community"),
            ("ISO Standards Portal", "https://www.iso.org/standards.html", "documentation"),
            ("Engineering Project Management", "https://www.coursera.org/learn/engineering-project-management", "course"),
            ("NASA Systems Engineering Handbook", "https://www.nasa.gov/seh/", "book"),
        ]),
        ("Engineering Portfolio and Career", "case studies, technical presentations, professional registration, and interviews", ["Project case studies", "Technical report writing", "Professional registration", "Engineering interviews", "Continuing education"], [
            ("Engineers Without Borders", "https://www.ewb-usa.org/", "community"),
            ("IEEE Career Resources", "https://careers.ieee.org/", "community"),
            ("IMechE Career Resources", "https://www.imeche.org/career-development", "community"),
            ("GitHub Engineering Portfolio", "https://github.com/", "community"),
        ]),
    ],
    "healthcare": [
        ("Human Biology and Anatomy", "body systems, physiology, homeostasis, and clinical relevance", ["Body systems overview", "Cell biology basics", "Cardiovascular system", "Nervous system", "Homeostasis and disease"], [
            ("Khan Academy Health and Medicine", "https://www.khanacademy.org/science/health-and-medicine", "course"),
            ("Visible Body", "https://www.visiblebody.com/", "course"),
            ("OpenStax Anatomy and Physiology", "https://openstax.org/details/books/anatomy-and-physiology-2e", "book"),
            ("TeachMe Anatomy", "https://teachmeanatomy.info/", "article"),
        ]),
        ("Clinical Assessment and Documentation", "patient history, physical examination, clinical reasoning, and record keeping", ["Patient history taking", "Physical examination basics", "Clinical reasoning", "SOAP notes", "Electronic health records"], [
            ("Geeky Medics", "https://geekymedics.com/", "article"),
            ("Osmosis Clinical Skills", "https://www.osmosis.org/", "course"),
            ("BMJ Learning", "https://learning.bmj.com/", "course"),
            ("UpToDate", "https://www.uptodate.com/home/medical-education", "documentation"),
        ]),
        ("Evidence-Based Practice", "research literacy, clinical guidelines, systematic reviews, and applying evidence", ["Reading research papers", "Study designs", "Critical appraisal", "Clinical guidelines", "Applying evidence to patients"], [
            ("Cochrane Library", "https://www.cochranelibrary.com/", "article"),
            ("PubMed", "https://pubmed.ncbi.nlm.nih.gov/", "documentation"),
            ("Centre for Evidence-Based Medicine", "https://www.cebm.ox.ac.uk/resources", "article"),
            ("BMJ Best Practice", "https://bestpractice.bmj.com/", "documentation"),
        ]),
        ("Patient Communication and Ethics", "therapeutic communication, informed consent, shared decision making, and ethics", ["Active listening", "Breaking bad news", "Informed consent", "Shared decision making", "Ethical frameworks"], [
            ("Institute for Healthcare Communication", "https://healthcarecomm.org/", "article"),
            ("Beryl Institute Patient Experience", "https://www.theberylinstitute.org/", "community"),
            ("Coursera Health Communication", "https://www.coursera.org/courses?query=health%20communication", "course"),
            ("Medical Ethics Toolkit", "https://www.ama-assn.org/delivering-care/ethics", "documentation"),
        ]),
        ("Public Health and Prevention", "epidemiology, population health, screening, and health promotion", ["Epidemiology basics", "Disease prevention tiers", "Screening programmes", "Health data interpretation", "Health promotion strategies"], [
            ("CDC Public Health 101", "https://www.cdc.gov/training/publichealth101/", "course"),
            ("WHO Health Topics", "https://www.who.int/health-topics", "documentation"),
            ("Coursera Public Health", "https://www.coursera.org/browse/health/public-health", "course"),
            ("Johns Hopkins Bloomberg Public Health", "https://www.jhsph.edu/", "course"),
        ]),
        ("Healthcare Career and Continuing Education", "specialisation, licensing, portfolio building, and professional development", ["Specialisation pathways", "Licensing requirements", "Clinical portfolio", "Continuing education", "Healthcare leadership"], [
            ("WHO Health Workforce", "https://www.who.int/health-topics/health-workforce", "article"),
            ("Medscape Education", "https://www.medscape.com/", "course"),
            ("BMJ Career Resources", "https://www.bmj.com/careers", "community"),
            ("NEJM Career Center", "https://careers.nejm.org/", "community"),
        ]),
    ],
    "education": [
        ("Learning Science Foundations", "how people learn, memory, cognitive load, and motivation", ["How memory works", "Cognitive load theory", "Motivation and engagement", "Feedback and retrieval practice", "Growth mindset"], [
            ("Learning Scientists", "https://www.learningscientists.org/", "article"),
            ("Make It Stick", "https://www.retrievalpractice.org/make-it-stick", "book"),
            ("Coursera Learning How to Learn", "https://www.coursera.org/learn/learning-how-to-learn", "course"),
            ("Edutopia", "https://www.edutopia.org/", "article"),
        ]),
        ("Curriculum and Lesson Design", "learning objectives, sequencing, UbD, and lesson planning", ["Writing learning objectives", "Understanding by Design", "Lesson sequencing", "Scope and sequence", "Lesson plan structure"], [
            ("Understanding by Design", "https://jaymctighe.com/resources/", "book"),
            ("Bloom's Taxonomy Guide", "https://www.bloomstaxonomy.net/", "article"),
            ("TeachThought Lesson Design", "https://www.teachthought.com/", "article"),
            ("Buck Institute PBL", "https://www.pblworks.org/", "course"),
        ]),
        ("Assessment and Feedback", "formative assessment, rubrics, feedback quality, and data-driven teaching", ["Formative vs summative", "Rubric design", "Exit tickets and checks", "Analysing assessment data", "Feedback that moves learning"], [
            ("Dylan Wiliam Assessment", "https://www.dylanwiliamcenter.com/resources/", "article"),
            ("ASCD Assessment Resources", "https://www.ascd.org/topics/assessment", "article"),
            ("Google Forms for Assessment", "https://support.google.com/docs/topic/9055404", "documentation"),
            ("Standards-Based Grading", "https://www.marzanoresources.com/", "book"),
        ]),
        ("Classroom Management and Culture", "routines, relationships, behaviour management, and inclusive environments", ["Building routines", "Positive relationships", "Behaviour frameworks", "Inclusive classroom design", "Restorative practices"], [
            ("Responsive Classroom", "https://www.responsiveclassroom.org/", "book"),
            ("Edutopia Classroom Management", "https://www.edutopia.org/classroom-management", "article"),
            ("PBIS World", "https://www.pbisworld.com/", "documentation"),
            ("Culturally Responsive Teaching", "https://www.gln.harvard.edu/", "course"),
        ]),
        ("Educational Technology", "LMS platforms, instructional video, interactive tools, and blended learning", ["Choosing an LMS", "Creating instructional video", "Interactive quiz tools", "Blended learning models", "Digital accessibility"], [
            ("Google for Education", "https://edu.google.com/", "course"),
            ("Khan Academy for Teachers", "https://www.khanacademy.org/coach-res", "course"),
            ("Canva Education", "https://www.canva.com/education/", "course"),
            ("ISTE Standards", "https://www.iste.org/standards", "documentation"),
        ]),
        ("Teaching Portfolio and Career", "professional development, teaching philosophy, and career progression", ["Teaching philosophy statement", "Portfolio evidence", "Peer observation", "Professional learning communities", "Career pathways"], [
            ("ASCD Professional Development", "https://www.ascd.org/professional-learning", "community"),
            ("National Board Certification", "https://www.nbpts.org/", "community"),
            ("Edutopia Teacher Growth", "https://www.edutopia.org/professional-development", "article"),
            ("Teaching Channel", "https://www.teachingchannel.com/", "video"),
        ]),
    ],
    "business": [
        ("Business Strategy Foundations", "industry analysis, competitive positioning, value chains, and strategic frameworks", ["Porter's Five Forces", "SWOT analysis", "Value chain analysis", "Business model canvas", "Strategic positioning"], [
            ("Harvard Business Review Strategy", "https://hbr.org/topic/subject/strategy", "article"),
            ("Coursera Business Strategy", "https://www.coursera.org/learn/uva-darden-foundations-business-strategy", "course"),
            ("Good Strategy Bad Strategy", "https://www.penguinrandomhouse.com/books/208626/good-strategy-bad-strategy-by-richard-rumelt/", "book"),
            ("McKinsey Insights", "https://www.mckinsey.com/insights", "article"),
        ]),
        ("Market Research and Customer Insight", "primary research, segmentation, personas, and customer jobs-to-be-done", ["Survey and interview design", "Customer segmentation", "Persona development", "Jobs-to-be-done framework", "Competitive benchmarking"], [
            ("Think with Google", "https://www.thinkwithgoogle.com/", "article"),
            ("Statista", "https://www.statista.com/", "documentation"),
            ("SurveyMonkey Learn", "https://www.surveymonkey.com/curiosity/", "article"),
            ("Harvard JTBD", "https://hbr.org/2016/09/know-your-customers-jobs-to-be-done", "article"),
        ]),
        ("Financial Literacy for Business", "reading financial statements, business metrics, unit economics, and budgeting", ["Income statement basics", "Cash flow management", "Unit economics", "KPI dashboards", "Business budgeting"], [
            ("Corporate Finance Institute Business", "https://corporatefinanceinstitute.com/", "course"),
            ("Khan Academy Finance", "https://www.khanacademy.org/economics-finance-domain", "course"),
            ("HBR Finance for Managers", "https://hbr.org/topic/subject/finance", "article"),
            ("Investopedia Business", "https://www.investopedia.com/", "article"),
        ]),
        ("Product Management and Execution", "roadmaps, prioritisation, Agile, sprint planning, and stakeholder management", ["Product roadmaps", "Prioritisation frameworks", "Agile and Scrum basics", "Sprint planning", "Stakeholder alignment"], [
            ("Product School", "https://productschool.com/resources/", "course"),
            ("Mind the Product", "https://www.mindtheproduct.com/", "community"),
            ("Inspired by Marty Cagan", "https://www.svpg.com/books/inspired-how-to-create-tech-products-customers-love-2nd-edition/", "book"),
            ("Atlassian Agile", "https://www.atlassian.com/agile", "documentation"),
        ]),
        ("Communication and Influence", "executive presentations, stakeholder communication, negotiation, and persuasion", ["Structured communication", "Executive presentations", "Negotiation principles", "Influence without authority", "Difficult conversations"], [
            ("HBR Communication", "https://hbr.org/topic/subject/communication", "article"),
            ("Coursera Influencing", "https://www.coursera.org/courses?query=negotiation", "course"),
            ("Never Split the Difference", "https://www.blackswanltd.com/never-split-the-difference", "book"),
            ("TED Talks Business", "https://www.ted.com/topics/business", "video"),
        ]),
        ("Business Case and Career Portfolio", "business case writing, case interview prep, and professional branding", ["Business case structure", "Consulting case frameworks", "Professional LinkedIn profile", "Case study portfolio", "Business career pathways"], [
            ("Case Interview Prep", "https://www.mckinsey.com/careers/interviewing/case-interview-prep", "article"),
            ("Coursera Business Case", "https://www.coursera.org/learn/making-successful-decisions", "course"),
            ("LinkedIn Learning Business", "https://www.linkedin.com/learning/topics/business-analysis", "course"),
            ("Harvard Business School Online", "https://online.hbs.edu/", "course"),
        ]),
    ],
}


# ── Per-sub-specialty catalogs ────────────────────────────────────────────────
# Matched by _find_catalog_key() before falling back to the broader CATALOGS.
SUB_CATALOGS: Dict[str, List[ModuleSeed]] = {
    # ── IT ───────────────────────────────────────────────────────────────────
    "it_software": [
        ("Programming Foundations", "Python syntax, data types, control flow, functions, OOP, and error handling", ["Variables and data types", "Control flow and loops", "Functions and scope", "Classes and objects", "Exception handling"], [
            ("CS50P — Python", "https://cs50.harvard.edu/python/", "course"),
            ("Python Official Tutorial", "https://docs.python.org/3/tutorial/", "documentation"),
            ("Automate the Boring Stuff", "https://automatetheboringstuff.com/", "book"),
            ("Real Python", "https://realpython.com/", "article"),
        ]),
        ("Version Control and Collaboration", "Git workflow, GitHub, pull requests, code review, and project structure", ["Commits and branching", "Merging and rebasing", "Pull requests and review", "Issue tracking", "README and documentation"], [
            ("Pro Git Book", "https://git-scm.com/book/en/v2", "book"),
            ("GitHub Skills", "https://skills.github.com/", "course"),
            ("Conventional Commits", "https://www.conventionalcommits.org/", "documentation"),
            ("GitHub Docs", "https://docs.github.com/", "documentation"),
        ]),
        ("Data Structures and Algorithms", "complexity analysis, arrays, hashmaps, trees, sorting, and problem-solving", ["Big-O complexity", "Arrays and linked lists", "Hash maps and sets", "Trees and graphs", "Sorting and searching"], [
            ("VisuAlgo", "https://visualgo.net/en", "article"),
            ("LeetCode Explore", "https://leetcode.com/explore/", "course"),
            ("MIT 6.006 Introduction to Algorithms", "https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-fall-2011/", "course"),
            ("Open Data Structures", "https://opendatastructures.org/", "book"),
        ]),
        ("Backend APIs and Databases", "REST APIs, FastAPI, SQL, database design, authentication, and testing", ["HTTP and REST principles", "FastAPI routes and validation", "SQL queries and joins", "Database schema design", "Auth and automated tests"], [
            ("FastAPI Documentation", "https://fastapi.tiangolo.com/tutorial/", "documentation"),
            ("SQLBolt", "https://sqlbolt.com/", "course"),
            ("PostgreSQL Tutorial", "https://www.postgresql.org/docs/current/tutorial.html", "documentation"),
            ("pytest Docs", "https://docs.pytest.org/", "documentation"),
        ]),
        ("Software Architecture and Clean Code", "SOLID principles, design patterns, clean code, and system design basics", ["SOLID principles", "Common design patterns", "Clean code practices", "Refactoring techniques", "System design fundamentals"], [
            ("The Pragmatic Programmer", "https://pragprog.com/titles/tpp20/", "book"),
            ("Refactoring Guru", "https://refactoring.guru/design-patterns", "article"),
            ("System Design Primer", "https://github.com/donnemartin/system-design-primer", "article"),
            ("Clean Code by Robert Martin", "https://www.pearson.com/en-us/subject-catalog/p/clean-code-a-handbook-of-agile-software-craftsmanship/P200000009044", "book"),
        ]),
        ("Deployment and Engineering Career", "Docker, CI/CD, cloud basics, portfolio projects, and interview preparation", ["Containerising an app with Docker", "GitHub Actions CI pipeline", "Cloud deployment basics", "Engineering portfolio case studies", "Technical interview practice"], [
            ("Docker Get Started", "https://docs.docker.com/get-started/", "documentation"),
            ("GitHub Actions Docs", "https://docs.github.com/en/actions", "documentation"),
            ("roadmap.sh Backend", "https://roadmap.sh/backend", "article"),
            ("NeetCode", "https://neetcode.io/", "course"),
        ]),
    ],
    "it_data": [
        ("Python for Data Science", "NumPy, pandas, matplotlib, Seaborn, and Jupyter notebook workflows", ["NumPy arrays and operations", "pandas DataFrames", "Data cleaning and wrangling", "matplotlib and Seaborn charts", "Jupyter notebooks"], [
            ("Kaggle Python Course", "https://www.kaggle.com/learn/python", "course"),
            ("pandas Documentation", "https://pandas.pydata.org/docs/getting_started/", "documentation"),
            ("Python for Data Analysis", "https://wesmckinney.com/book/", "book"),
            ("Matplotlib Tutorials", "https://matplotlib.org/stable/tutorials/index.html", "documentation"),
        ]),
        ("Statistics and Probability", "descriptive statistics, probability distributions, hypothesis testing, and correlation", ["Descriptive statistics", "Probability fundamentals", "Distributions and CLT", "Hypothesis testing", "Correlation and regression"], [
            ("Khan Academy Statistics", "https://www.khanacademy.org/math/statistics-probability", "course"),
            ("StatQuest with Josh Starmer", "https://statquest.org/", "video"),
            ("Think Stats", "https://greenteapress.com/wp/think-stats-2e/", "book"),
            ("Coursera Statistics with Python", "https://www.coursera.org/specializations/statistics-with-python", "course"),
        ]),
        ("SQL and Data Engineering", "SQL queries, joins, window functions, data pipelines, and warehouse basics", ["SQL SELECT and filtering", "Joins and aggregations", "Window functions", "CTEs and subqueries", "ETL pipeline concepts"], [
            ("Mode SQL Tutorial", "https://mode.com/sql-tutorial/", "course"),
            ("SQLBolt", "https://sqlbolt.com/", "course"),
            ("dbt Learn", "https://courses.getdbt.com/", "course"),
            ("BigQuery Sandbox", "https://cloud.google.com/bigquery/docs/sandbox", "documentation"),
        ]),
        ("Machine Learning", "supervised and unsupervised learning, scikit-learn, model evaluation, and feature engineering", ["Linear and logistic regression", "Decision trees and random forests", "Model evaluation metrics", "Feature engineering", "Cross-validation and tuning"], [
            ("Kaggle ML Courses", "https://www.kaggle.com/learn/intro-to-machine-learning", "course"),
            ("scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html", "documentation"),
            ("Hands-On Machine Learning", "https://www.oreilly.com/library/view/hands-on-machine-learning/9781492032632/", "book"),
            ("Google ML Crash Course", "https://developers.google.com/machine-learning/crash-course", "course"),
        ]),
        ("Deep Learning and NLP", "neural networks, PyTorch, NLP fundamentals, transformers, and LLM prompting", ["Neural network architecture", "Training and backpropagation", "CNNs and RNNs", "Transformers and BERT", "Prompt engineering basics"], [
            ("fast.ai Practical Deep Learning", "https://course.fast.ai/", "course"),
            ("PyTorch Tutorials", "https://pytorch.org/tutorials/", "documentation"),
            ("Hugging Face Course", "https://huggingface.co/learn/nlp-course/", "course"),
            ("Andrej Karpathy YouTube", "https://www.youtube.com/@AndrejKarpathy", "video"),
        ]),
        ("MLOps and Data Science Career", "model deployment, monitoring, experiment tracking, Kaggle, and portfolio", ["Model deployment with FastAPI", "Experiment tracking with MLflow", "Data versioning with DVC", "Kaggle competition workflow", "Data science portfolio and interviews"], [
            ("MLflow Documentation", "https://mlflow.org/docs/latest/", "documentation"),
            ("Towards Data Science", "https://towardsdatascience.com/", "article"),
            ("Made With ML", "https://madewithml.com/", "course"),
            ("Kaggle Competitions", "https://www.kaggle.com/competitions", "community"),
        ]),
    ],
    "it_devops": [
        ("Linux and Shell Scripting", "command line, bash scripting, permissions, processes, and networking basics", ["File system navigation", "File permissions and users", "Bash scripting fundamentals", "Processes and signals", "Networking commands"], [
            ("The Linux Command Line", "https://linuxcommand.org/tlcl.php", "book"),
            ("Linux Journey", "https://linuxjourney.com/", "course"),
            ("OverTheWire Bandit", "https://overthewire.org/wargames/bandit/", "course"),
            ("Bash Scripting Tutorial", "https://www.shellscript.sh/", "documentation"),
        ]),
        ("Docker and Containerisation", "images, containers, Dockerfile, Docker Compose, and container registries", ["Docker images and containers", "Writing Dockerfiles", "Docker Compose services", "Container networking", "Registry and image tagging"], [
            ("Docker Official Docs", "https://docs.docker.com/", "documentation"),
            ("Docker and Kubernetes — Full Course", "https://www.youtube.com/watch?v=Wf2eSG3owoA", "video"),
            ("Docker Deep Dive — Nigel Poulton", "https://nigelpoulton.com/books/docker-deep-dive/", "book"),
            ("Play with Docker", "https://labs.play-with-docker.com/", "community"),
        ]),
        ("CI/CD Pipelines", "GitHub Actions, automated testing, build pipelines, and deployment automation", ["Pipeline concepts", "GitHub Actions workflows", "Automated testing in CI", "Artifact management", "Deployment strategies"], [
            ("GitHub Actions Documentation", "https://docs.github.com/en/actions", "documentation"),
            ("CI/CD with GitLab", "https://docs.gitlab.com/ee/ci/", "documentation"),
            ("The DevOps Handbook", "https://itrevolution.com/product/the-devops-handbook/", "book"),
            ("Awesome CI/CD", "https://github.com/ligurio/awesome-ci", "community"),
        ]),
        ("Cloud Platforms", "AWS/GCP/Azure core services, IAM, VPC, S3, compute, and managed databases", ["Cloud provider overview", "IAM and access control", "Virtual networks and subnets", "Storage services", "Managed compute and databases"], [
            ("AWS Skill Builder", "https://skillbuilder.aws/", "course"),
            ("Google Cloud Skills Boost", "https://cloudskillsboost.google/", "course"),
            ("Cloud Guru", "https://acloudguru.com/", "course"),
            ("AWS Documentation", "https://docs.aws.amazon.com/", "documentation"),
        ]),
        ("Infrastructure as Code and Kubernetes", "Terraform, Ansible, Kubernetes objects, Helm, and GitOps", ["Terraform basics and state", "Ansible playbooks", "Kubernetes pods and deployments", "Services and ingress", "Helm charts and GitOps"], [
            ("Terraform Learn", "https://developer.hashicorp.com/terraform/tutorials", "documentation"),
            ("Kubernetes Documentation", "https://kubernetes.io/docs/tutorials/", "documentation"),
            ("Kubernetes Up and Running", "https://www.oreilly.com/library/view/kubernetes-up-and/9781098110192/", "book"),
            ("roadmap.sh DevOps", "https://roadmap.sh/devops", "article"),
        ]),
        ("Observability and DevOps Career", "Prometheus, Grafana, alerting, SRE principles, and engineering portfolio", ["Metrics and Prometheus", "Grafana dashboards", "Log aggregation", "Incident response and on-call", "DevOps engineer portfolio"], [
            ("Prometheus Documentation", "https://prometheus.io/docs/", "documentation"),
            ("Grafana Learn", "https://grafana.com/tutorials/", "documentation"),
            ("Site Reliability Engineering Book", "https://sre.google/sre-book/table-of-contents/", "book"),
            ("DevOps Institute", "https://www.devopsinstitute.com/", "community"),
        ]),
    ],
    # ── Design ───────────────────────────────────────────────────────────────
    "design_ux": [
        ("Design Thinking and User Research", "empathy maps, user interviews, personas, journey maps, and problem framing", ["Empathy mapping", "User interview planning and facilitation", "Persona development", "User journey mapping", "How-might-we problem framing"], [
            ("Google UX Design Certificate", "https://grow.google/certificates/ux-design/", "course"),
            ("Nielsen Norman Group Articles", "https://www.nngroup.com/articles/", "article"),
            ("The Design of Everyday Things", "https://www.basicbooks.com/titles/don-norman/the-design-of-everyday-things/9780465050659/", "book"),
            ("IDEO Design Thinking", "https://designthinking.ideo.com/", "article"),
        ]),
        ("Information Architecture and Wireframing", "sitemaps, content hierarchies, wireframes, user flows, and navigation patterns", ["Site maps and content inventory", "User flow diagrams", "Low-fidelity wireframing", "Navigation and labelling", "Accessibility basics"], [
            ("Interaction Design Foundation — IA", "https://www.interaction-design.org/literature/topics/information-architecture", "article"),
            ("Wireframing Guide — Figma", "https://www.figma.com/resource-library/what-is-wireframing/", "article"),
            ("Web Application Design Patterns", "https://www.oreilly.com/library/view/designing-web-interfaces/9780596156220/", "book"),
            ("Figma Community Wireframe Kits", "https://www.figma.com/community/tag/wireframe", "community"),
        ]),
        ("Visual Design and UI Principles", "typography, colour, spacing, grid, visual hierarchy, and design systems", ["Typography pairing and sizing", "Colour theory and contrast", "8-point grid and spacing", "Visual hierarchy and emphasis", "Introduction to design tokens"], [
            ("Refactoring UI", "https://www.refactoringui.com/", "book"),
            ("Material Design Guidelines", "https://m3.material.io/", "documentation"),
            ("Apple Human Interface Guidelines", "https://developer.apple.com/design/human-interface-guidelines/", "documentation"),
            ("Contrast Checker — WebAIM", "https://webaim.org/resources/contrastchecker/", "article"),
        ]),
        ("Figma and Interactive Prototyping", "components, auto-layout, variants, interactive prototypes, and developer handoff", ["Components and instances", "Auto-layout and responsive frames", "Variants and component properties", "Interactive prototype flows", "Developer handoff and inspect"], [
            ("Figma Learn", "https://help.figma.com/hc/en-us/categories/360002051613", "documentation"),
            ("UI Prep", "https://www.uiprep.com/", "course"),
            ("Design+Code", "https://designcode.io/", "course"),
            ("Figma Community Plugins", "https://www.figma.com/community/plugins", "community"),
        ]),
        ("Usability Testing and Iteration", "test planning, facilitation, affinity mapping, prioritised revisions, and metrics", ["Writing a usability test script", "Moderated and unmoderated sessions", "Affinity mapping findings", "Prioritising design revisions", "Tracking UX metrics over time"], [
            ("Maze Usability Testing Guide", "https://maze.co/guides/usability-testing/", "article"),
            ("Nielsen Norman Research Methods", "https://www.nngroup.com/articles/which-ux-research-methods/", "article"),
            ("Optimal Workshop", "https://www.optimalworkshop.com/learn/", "article"),
            ("UsabilityHub", "https://www.usabilityhub.com/", "course"),
        ]),
        ("UX Portfolio and Career", "case study structure, portfolio presentation, design interviews, and job search", ["Case study problem-solution-outcome format", "Portfolio site setup", "Design challenge walk-throughs", "Whiteboard design practice", "UX job search strategy"], [
            ("UX Portfolio Formula", "https://www.uxportfolioformula.com/", "article"),
            ("Behance UX Work", "https://www.behance.net/", "community"),
            ("ADPList Mentorship", "https://adplist.org/", "community"),
            ("UX Collective", "https://uxdesign.cc/", "article"),
        ]),
    ],
    "design_graphic": [
        ("Visual Design Principles", "visual hierarchy, balance, contrast, proximity, repetition, and white space", ["Visual hierarchy basics", "Balance and composition", "Contrast and emphasis", "Proximity and grouping", "Negative space"], [
            ("Canva Design School", "https://www.canva.com/designschool/", "course"),
            ("Design School — Ellen Lupton", "https://papress.com/products/graphic-design-the-new-basics", "book"),
            ("Vanseo Design Blog", "https://vanseodesign.com/category/design-theory/", "article"),
            ("Dribbble Learning", "https://dribbble.com/stories/categories/designers-jobs", "community"),
        ]),
        ("Typography", "typeface anatomy, selection, pairing, hierarchy, and web versus print", ["Typeface anatomy and classification", "Selecting and pairing typefaces", "Typographic hierarchy", "Kerning, tracking, and leading", "Web-safe and variable fonts"], [
            ("Thinking with Type", "http://thinkingwithtype.com/", "book"),
            ("Google Fonts", "https://fonts.google.com/", "documentation"),
            ("Fonts in Use", "https://fontsinuse.com/", "article"),
            ("Typography Handbook", "https://typographyhandbook.com/", "article"),
        ]),
        ("Colour Theory and Brand Colour", "colour models, palette creation, brand colour systems, and accessibility", ["RGB, CMYK, and Pantone", "Colour harmony and palettes", "Brand colour systems", "Colour accessibility (WCAG)", "Colour in print vs screen"], [
            ("Adobe Color", "https://color.adobe.com/", "documentation"),
            ("Colour Theory Guide — Canva", "https://www.canva.com/colors/color-wheel/", "article"),
            ("Coolors", "https://coolors.co/", "article"),
            ("Practical Colour Theory — UX Collective", "https://uxdesign.cc/color-theory-for-designers-a-quick-reference-guide-3a7967e53888", "article"),
        ]),
        ("Adobe Creative Suite", "Illustrator, Photoshop, and InDesign core workflows for print and digital", ["Illustrator vector and pen tool", "Photoshop retouching and compositing", "InDesign layouts and grids", "Exporting for print and web", "Smart objects and linked assets"], [
            ("Adobe Education Exchange", "https://edex.adobe.com/", "course"),
            ("Adobe Help Centre", "https://helpx.adobe.com/creative-cloud.html", "documentation"),
            ("Envato Tuts+ Design", "https://design.tutsplus.com/", "article"),
            ("Phlearn", "https://phlearn.com/", "video"),
        ]),
        ("Brand Identity Design", "logo design, brand guidelines, stationery, iconography, and visual systems", ["Logo mark and wordmark design", "Brand guidelines document", "Stationery and print materials", "Icon set design", "Brand application across touchpoints"], [
            ("Logo Modernism — Gestalten", "https://www.gestalten.com/products/logo-modernism", "book"),
            ("Identity Designed", "https://identitydesigned.com/", "article"),
            ("Brand New Blog — UnderConsideration", "https://www.underconsideration.com/brandnew/", "article"),
            ("Behance", "https://www.behance.net/", "community"),
        ]),
        ("Portfolio and Graphic Design Career", "print production, client workflow, portfolio presentation, and job search", ["Print production specifications", "Client brief and presentation", "Portfolio site and PDF deck", "Freelance pricing basics", "Design job search and interviews"], [
            ("AIGA Career Resources", "https://www.aiga.org/career-advice", "community"),
            ("HOW Design", "https://www.howdesign.com/", "article"),
            ("Dribbble Jobs", "https://dribbble.com/jobs", "community"),
            ("Freelancers Union", "https://www.freelancersunion.org/resources/", "community"),
        ]),
    ],
    "design_product": [
        ("Product Thinking and Strategy", "business goals, user goals, success metrics, product vision, and OKRs", ["User problems vs business goals", "Defining product vision", "OKRs and success metrics", "Product strategy frameworks", "Competitive landscape analysis"], [
            ("Inspired — Marty Cagan", "https://www.svpg.com/books/inspired-how-to-create-tech-products-customers-love-2nd-edition/", "book"),
            ("UX Collective — Product Design", "https://uxdesign.cc/tagged/product-design", "article"),
            ("Lenny's Newsletter", "https://www.lennysnewsletter.com/", "article"),
            ("Product School", "https://productschool.com/resources/", "course"),
        ]),
        ("Research and Discovery at Scale", "quantitative research, surveys, cohort analysis, and research synthesis", ["Survey design and analysis", "Cohort and funnel analysis", "Jobs-to-be-done interviews", "Research repository management", "Synthesis and insight presentation"], [
            ("Dovetail Research Platform", "https://dovetail.com/learn/", "article"),
            ("Nielsen Norman Research Methods", "https://www.nngroup.com/articles/which-ux-research-methods/", "article"),
            ("Quantitative UX Research", "https://www.oreilly.com/library/view/quantitative-ux-research/9781098115470/", "book"),
            ("Maze Research Guide", "https://maze.co/guides/", "article"),
        ]),
        ("Design Systems", "atoms to organisms, tokens, documentation, component libraries, and governance", ["Atomic design principles", "Design tokens and variables", "Component documentation", "Accessibility in design systems", "Cross-team governance"], [
            ("Design Systems Handbook", "https://www.designbetter.co/design-systems-handbook", "book"),
            ("Storybook Docs", "https://storybook.js.org/docs/", "documentation"),
            ("Figma Variables Guide", "https://help.figma.com/hc/en-us/sections/14506605769879-Variables", "documentation"),
            ("Design Systems Repo", "https://designsystemsrepo.com/", "community"),
        ]),
        ("Data-Informed Design", "A/B testing, analytics dashboards, funnel analysis, and design decisions", ["Analytics dashboard setup", "Funnel drop-off analysis", "A/B test design and interpretation", "Behavioural data patterns", "Data-informed design decisions"], [
            ("Mixpanel Analytics", "https://mixpanel.com/blog/", "article"),
            ("Hotjar Learning Centre", "https://www.hotjar.com/product-analytics/", "article"),
            ("Lean Analytics", "https://leananalyticsbook.com/", "book"),
            ("Google Analytics 4 Docs", "https://support.google.com/analytics/answer/10089681", "documentation"),
        ]),
        ("Cross-functional Collaboration", "working with PMs, engineers, leadership, and design critique", ["Partnering with product managers", "Communicating design intent to engineers", "Design critique facilitation", "Stakeholder presentation", "Managing design feedback"], [
            ("Hooked — Nir Eyal", "https://www.nirandfar.com/hooked/", "book"),
            ("Interaction Design Foundation", "https://www.interaction-design.org/", "course"),
            ("IDEO Design Thinking Field Guide", "https://www.ideo.com/post/design-thinking-for-educators", "article"),
            ("UX Collective Collaboration", "https://uxdesign.cc/tagged/cross-functional", "article"),
        ]),
        ("Product Design Career", "portfolio case studies, system design exercises, career ladders, and interviews", ["Portfolio case study structure", "Product design challenge practice", "Design system interview prep", "Career ladder navigation", "Job search and networking"], [
            ("Figma Jobs", "https://www.figma.com/jobs/", "community"),
            ("ADPList Mentors", "https://adplist.org/", "community"),
            ("UX Portfolio Formula", "https://www.uxportfolioformula.com/", "article"),
            ("Dribbble — Product Design", "https://dribbble.com/shots/popular/product-design", "community"),
        ]),
    ],
    # ── Marketing ────────────────────────────────────────────────────────────
    "marketing_digital": [
        ("Digital Marketing Foundations", "customer acquisition, funnel stages, channel mix, and campaign budgeting", ["Customer acquisition concepts", "Marketing funnel stages", "Channel mix strategy", "Campaign budgeting basics", "Brand vs performance marketing"], [
            ("HubSpot Academy Marketing", "https://academy.hubspot.com/", "course"),
            ("Google Digital Garage", "https://grow.google/intl/en_uk/courses-and-tools/", "course"),
            ("Marketing Made Simple", "https://storybrand.com/marketing-made-simple-book/", "book"),
            ("Think with Google", "https://www.thinkwithgoogle.com/", "article"),
        ]),
        ("Google Ads and Paid Search", "campaign structure, keyword bidding, ad copy, Quality Score, and optimization", ["Campaign and ad group structure", "Keyword match types and bidding", "Writing high-CTR ad copy", "Quality Score optimization", "Negative keywords and targeting"], [
            ("Google Skillshop", "https://skillshop.withgoogle.com/googleads", "course"),
            ("Google Ads Help Centre", "https://support.google.com/google-ads/", "documentation"),
            ("WordStream Blog", "https://www.wordstream.com/blog", "article"),
            ("Optmyzr Resources", "https://www.optmyzr.com/resources/", "article"),
        ]),
        ("Social Media Advertising", "Meta Ads, TikTok Ads, audience targeting, creative testing, and retargeting", ["Meta Ads Manager setup", "Audience targeting and Lookalikes", "Creative A/B testing", "TikTok campaign structure", "Retargeting and pixel setup"], [
            ("Meta Blueprint", "https://www.facebook.com/business/learn", "course"),
            ("TikTok Business Learning Center", "https://www.tiktok.com/business/en-US/blog", "article"),
            ("Social Media Examiner", "https://www.socialmediaexaminer.com/", "article"),
            ("Hootsuite Academy", "https://education.hootsuite.com/", "course"),
        ]),
        ("Analytics and Performance Measurement", "GA4, UTM tracking, attribution models, dashboards, and reporting", ["GA4 setup and events", "UTM parameter tracking", "Attribution modelling", "Looker Studio dashboards", "Performance reporting templates"], [
            ("Google Analytics Academy", "https://skillshop.exceedlms.com/student/catalog/list?category_ids=6431-google-analytics", "course"),
            ("Measureschool", "https://measureschool.com/", "article"),
            ("GA4 Documentation", "https://support.google.com/analytics/answer/10089681", "documentation"),
            ("Looker Studio Help", "https://support.google.com/looker-studio/", "documentation"),
        ]),
        ("Email and CRM Marketing", "list segmentation, email automation, deliverability, and lifecycle campaigns", ["List segmentation strategy", "Email automation flows", "Subject line and copy best practices", "Deliverability and spam avoidance", "Lifecycle email campaigns"], [
            ("Mailchimp Resources", "https://mailchimp.com/resources/", "article"),
            ("Klaviyo Academy", "https://academy.klaviyo.com/", "course"),
            ("Email Marketing Benchmarks", "https://www.campaignmonitor.com/resources/guides/email-marketing-benchmarks/", "article"),
            ("Really Good Emails", "https://reallygoodemails.com/", "community"),
        ]),
        ("Campaign Strategy and Career", "integrated campaigns, client reporting, certifications, and portfolio", ["Integrated campaign brief writing", "Cross-channel reporting", "Google and Meta certification prep", "Campaign case study presentation", "Digital marketing portfolio"], [
            ("Google Skillshop Certifications", "https://skillshop.withgoogle.com/", "course"),
            ("HubSpot Certifications", "https://academy.hubspot.com/certifications", "course"),
            ("Marketing Week Jobs", "https://jobs.marketingweek.com/", "community"),
            ("Marketing Dive", "https://www.marketingdive.com/", "article"),
        ]),
    ],
    "marketing_content": [
        ("Content Strategy Foundations", "audience research, content pillars, brand voice, editorial mission, and strategy docs", ["Audience persona research", "Content pillar definition", "Brand voice and tone guidelines", "Editorial mission statement", "Content strategy document"], [
            ("Content Marketing Institute", "https://contentmarketinginstitute.com/", "article"),
            ("HubSpot Content Marketing Course", "https://academy.hubspot.com/courses/content-marketing", "course"),
            ("Everybody Writes — Ann Handley", "https://annhandley.com/everybodywrites/", "book"),
            ("Copyblogger", "https://copyblogger.com/", "article"),
        ]),
        ("Copywriting and Persuasion", "headlines, CTAs, long-form writing, storytelling frameworks, and conversion copy", ["Headline formulas that convert", "AIDA and PAS copywriting frameworks", "Long-form article structure", "CTA writing principles", "Email and ad copywriting"], [
            ("The Copywriter's Handbook — Bly", "https://www.holtpaperbcks.com/9780805078909/the-copywriters-handbook/", "book"),
            ("Kopywriting Kourse", "https://kopywritingkourse.com/", "course"),
            ("Swipe File — Copywriting examples", "https://www.swipeFile.club/", "community"),
            ("Conversion Copywriting — Joanna Wiebe", "https://copyhackers.com/", "article"),
        ]),
        ("SEO Writing and Content Optimization", "keyword research, search intent mapping, on-page SEO, and content briefs", ["Keyword research and intent", "Content brief creation", "On-page SEO elements", "Internal linking strategy", "Content refresh and updates"], [
            ("Ahrefs SEO Blog", "https://ahrefs.com/blog/", "article"),
            ("Semrush Academy SEO", "https://www.semrush.com/academy/courses/", "course"),
            ("Google Search Central", "https://developers.google.com/search/docs", "documentation"),
            ("Clearscope Blog", "https://www.clearscope.io/blog", "article"),
        ]),
        ("Content Operations", "editorial calendar, content workflow, repurposing, distribution, and tooling", ["Editorial calendar management", "Content production workflow", "Content repurposing strategy", "Distribution channel management", "Content management tools"], [
            ("CoSchedule Blog", "https://coschedule.com/blog", "article"),
            ("Notion Templates for Content", "https://www.notion.so/templates/content-calendar", "documentation"),
            ("Buffer Resources", "https://buffer.com/resources/", "article"),
            ("Trello Content Board", "https://trello.com/templates/marketing", "documentation"),
        ]),
        ("Content Analytics and Measurement", "traffic analysis, engagement metrics, content audits, and performance loops", ["GA4 for content teams", "Engagement rate and time on page", "Content audit methodology", "A/B testing content formats", "Content ROI reporting"], [
            ("Google Analytics for Content", "https://support.google.com/analytics/answer/10089681", "documentation"),
            ("Ahrefs Site Audit Guide", "https://ahrefs.com/blog/content-audit/", "article"),
            ("Content Measurement Guide — CMI", "https://contentmarketinginstitute.com/articles/", "article"),
            ("Hotjar for Content", "https://www.hotjar.com/", "article"),
        ]),
        ("Content Portfolio and Career", "content samples, case studies, editorial pitch, and job search strategy", ["Building a content portfolio site", "Writing case studies with metrics", "Editorial pitch writing", "Freelance rates and contracts", "Content job search and applications"], [
            ("Contently Portfolio", "https://contently.com/", "community"),
            ("Muck Rack", "https://muckrack.com/", "community"),
            ("The Write Life", "https://thewritelife.com/", "article"),
            ("LinkedIn for Content Creators", "https://www.linkedin.com/learning/topics/content-creation", "course"),
        ]),
    ],
    "marketing_seo": [
        ("Search Engine Fundamentals", "how search engines work, crawling, indexing, ranking signals, and E-E-A-T", ["How Googlebot crawls and indexes", "Ranking signals overview", "E-E-A-T principles", "SERP features and rich results", "Google Search Console setup"], [
            ("Google Search Central Documentation", "https://developers.google.com/search/docs", "documentation"),
            ("Moz Beginner's Guide to SEO", "https://moz.com/beginners-guide-to-seo", "article"),
            ("Ahrefs SEO Course for Beginners", "https://ahrefs.com/academy/seo-training-course", "course"),
            ("Search Engine Journal", "https://www.searchenginejournal.com/", "article"),
        ]),
        ("Keyword Research and Content Strategy", "keyword tools, search intent, content gap, and topic clustering", ["Keyword tools (Ahrefs, Semrush)", "Search intent classification", "Content gap analysis", "Topic cluster and pillar strategy", "Keyword prioritisation matrix"], [
            ("Ahrefs Keywords Explorer Guide", "https://ahrefs.com/blog/keyword-research/", "article"),
            ("Semrush Keyword Magic", "https://www.semrush.com/analytics/keywordmagic/", "documentation"),
            ("Content Strategy for SEO — Clearscope", "https://www.clearscope.io/blog", "article"),
            ("Google Trends", "https://trends.google.com/", "documentation"),
        ]),
        ("Technical SEO", "site architecture, Core Web Vitals, sitemaps, structured data, and crawl budget", ["Site architecture and URL structure", "Core Web Vitals (LCP, FID, CLS)", "XML sitemaps and robots.txt", "Structured data and schema markup", "Crawl budget management"], [
            ("Google Developers — Web Vitals", "https://web.dev/vitals/", "documentation"),
            ("Screaming Frog SEO Spider", "https://www.screamingfrog.co.uk/seo-spider/", "article"),
            ("Schema.org Documentation", "https://schema.org/", "documentation"),
            ("Technical SEO Guide — Ahrefs", "https://ahrefs.com/blog/technical-seo/", "article"),
        ]),
        ("Link Building and Off-Page SEO", "link earning strategies, digital PR, outreach, and brand mentions", ["Link quality and authority", "Digital PR and link earning", "Outreach email templates", "Broken link building", "Brand mention monitoring"], [
            ("Ahrefs Link Building Guide", "https://ahrefs.com/blog/link-building/", "article"),
            ("Backlinko Link Building", "https://backlinko.com/link-building", "article"),
            ("HARO (Help a Reporter Out)", "https://www.helpareporter.com/", "community"),
            ("Hunter.io for Outreach", "https://hunter.io/", "documentation"),
        ]),
        ("SEO Analytics and Reporting", "Google Search Console, GA4 for SEO, rank tracking, and stakeholder reports", ["GSC performance reports", "GA4 organic traffic analysis", "Rank tracking setup", "SEO dashboards in Looker Studio", "Monthly SEO report structure"], [
            ("Google Search Console Help", "https://support.google.com/webmasters/", "documentation"),
            ("Ahrefs Rank Tracker", "https://ahrefs.com/rank-tracker", "documentation"),
            ("Looker Studio SEO Dashboard", "https://lookerstudio.google.com/", "documentation"),
            ("SEMrush Analytics", "https://www.semrush.com/analytics/organic/", "documentation"),
        ]),
        ("Growth Experiments and SEO Career", "CRO basics, A/B testing, SEO case studies, and portfolio", ["CRO and landing page optimisation", "Content A/B testing", "SEO case study documentation", "Algorithm update response", "SEO portfolio and job search"], [
            ("Optimizely Experimentation", "https://www.optimizely.com/optimization-glossary/ab-testing/", "article"),
            ("Reforge Growth Blog", "https://www.reforge.com/blog", "article"),
            ("Whiteboard Friday — Moz", "https://moz.com/blog/category/whiteboard-friday", "video"),
            ("SEO Career Roadmap", "https://roadmap.sh/", "article"),
        ]),
    ],
    # ── Finance ──────────────────────────────────────────────────────────────
    "finance_analyst": [
        ("Accounting and Financial Statements", "income statement, balance sheet, cash flow, accounting ratios, and bookkeeping", ["Income statement line items", "Balance sheet structure", "Cash flow statement (direct/indirect)", "Key financial ratios", "Double-entry accounting"], [
            ("Khan Academy Finance and Capital Markets", "https://www.khanacademy.org/economics-finance-domain", "course"),
            ("AccountingCoach", "https://www.accountingcoach.com/", "course"),
            ("Financial Intelligence — Berman", "https://www.harpercollinsleadership.com/9781422144114/financial-intelligence/", "book"),
            ("OpenStax Principles of Accounting", "https://openstax.org/details/books/principles-financial-accounting", "book"),
        ]),
        ("Excel for Financial Analysis", "advanced formulas, lookup functions, pivot tables, and financial dashboard design", ["IF, SUMIF, and COUNTIF", "VLOOKUP and INDEX-MATCH", "Pivot tables and slicers", "Dynamic charts and dashboards", "Model audit techniques"], [
            ("CFI Excel Courses", "https://corporatefinanceinstitute.com/resources/excel/", "course"),
            ("ExcelJet", "https://exceljet.net/", "article"),
            ("Microsoft Excel Help", "https://support.microsoft.com/en-us/excel", "documentation"),
            ("Wall Street Prep Excel Crash Course", "https://www.wallstreetprep.com/knowledge/excel-crash-course/", "course"),
        ]),
        ("Financial Modeling", "three-statement model, assumptions, scenario analysis, and model auditing", ["Revenue and cost driver assumptions", "Income statement build", "Balance sheet and working capital", "Cash flow statement linkage", "Scenario and sensitivity analysis"], [
            ("CFI Financial Modeling", "https://corporatefinanceinstitute.com/resources/financial-modeling/", "course"),
            ("Wall Street Prep", "https://www.wallstreetprep.com/", "course"),
            ("Financial Modeling and Valuation — Pignataro", "https://www.wiley.com/en-us/Financial+Modeling+and+Valuation%2C+2nd+Edition-p-9781119808893", "book"),
            ("Damodaran Spreadsheets", "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/spreadsh.htm", "documentation"),
        ]),
        ("Valuation Methods", "DCF, comparable companies, precedent transactions, EV/EBITDA, and LBO basics", ["Discounted cash flow (DCF) model", "Comparable company analysis", "Precedent transaction analysis", "EV and equity bridge", "LBO model introduction"], [
            ("Aswath Damodaran — Valuation", "https://pages.stern.nyu.edu/~adamodar/", "course"),
            ("Investment Banking — Joshua Rosenbaum", "https://www.wiley.com/en-us/Investment+Banking%2C+3rd+Edition-p-9781119801436", "book"),
            ("SEC EDGAR", "https://www.sec.gov/edgar/search-and-access", "documentation"),
            ("Macrotrends Financial Data", "https://www.macrotrends.net/", "documentation"),
        ]),
        ("Industry Analysis and Reporting", "industry benchmarking, investment memo writing, and analyst presentations", ["Industry KPI benchmarking", "Peer comparison tables", "Analyst research note structure", "Executive summary writing", "Data visualisation for finance"], [
            ("CFA Institute Research", "https://www.cfainstitute.org/en/research", "article"),
            ("Harvard Business Review Finance", "https://hbr.org/topic/subject/finance-and-investing", "article"),
            ("Bloomberg Market Concepts", "https://www.bloomberg.com/professional/product/bloomberg-market-concepts/", "course"),
            ("Financial Modeling World Cup", "https://fmworldcup.com/", "community"),
        ]),
        ("CFA Preparation and Career", "CFA Level 1 concepts, analyst interview prep, and portfolio case studies", ["CFA Level 1 topic overview", "Ethics and professional standards", "Equity and fixed income basics", "Analyst interview case practice", "Financial analyst portfolio"], [
            ("CFA Institute Learning Ecosystem", "https://www.cfainstitute.org/en/programs/cfa-program", "course"),
            ("IFT CFA Prep", "https://ift.world/", "course"),
            ("Wall Street Oasis", "https://www.wallstreetoasis.com/", "community"),
            ("Corporate Finance Institute Career", "https://corporatefinanceinstitute.com/resources/career/", "article"),
        ]),
    ],
    "finance_investment": [
        ("Capital Markets and Asset Classes", "equities, fixed income, derivatives, market structure, and risk/return", ["Equity and debt markets", "Bond pricing and yield", "Derivatives overview", "Market microstructure", "Risk/return trade-off"], [
            ("Yale Financial Markets — Shiller", "https://oyc.yale.edu/economics/econ-252-11", "course"),
            ("CFA Institute Fundamentals", "https://www.cfainstitute.org/", "course"),
            ("Principles of Corporate Finance — Brealey", "https://www.mheducation.com/highered/product/principles-corporate-finance-brealey.html", "book"),
            ("Investopedia", "https://www.investopedia.com/", "article"),
        ]),
        ("Equity Research and Business Analysis", "business model analysis, competitive moat, management quality, and industry dynamics", ["Business model canvas for investing", "Competitive moat assessment", "Management quality evaluation", "Industry dynamics and cycles", "Reading earnings call transcripts"], [
            ("Common Stocks and Uncommon Profits — Fisher", "https://www.wiley.com/en-us/Common+Stocks+and+Uncommon+Profits+and+Other+Writings-p-9780471445500", "book"),
            ("Damodaran on Valuation", "https://pages.stern.nyu.edu/~adamodar/", "course"),
            ("SEC EDGAR", "https://www.sec.gov/edgar/search-and-access", "documentation"),
            ("Motley Fool Stock Advisor", "https://www.fool.com/", "article"),
        ]),
        ("DCF and Advanced Modelling", "free cash flow, WACC, terminal value, LBO modelling, and model checks", ["Free cash flow calculation", "WACC components and estimation", "Terminal value approaches", "LBO model mechanics", "Model sensitivity and checks"], [
            ("Wall Street Prep", "https://www.wallstreetprep.com/", "course"),
            ("Investment Banking — Rosenbaum", "https://www.wiley.com/en-us/Investment+Banking%2C+3rd+Edition-p-9781119801436", "book"),
            ("Damodaran Spreadsheets", "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/spreadsh.htm", "documentation"),
            ("Macroaxis Financial Data", "https://www.macroaxis.com/", "documentation"),
        ]),
        ("Portfolio Theory and Management", "MPT, factor investing, risk attribution, rebalancing, and performance measurement", ["Modern portfolio theory", "Efficient frontier and Sharpe ratio", "Factor models (Fama-French)", "Portfolio rebalancing", "Performance attribution"], [
            ("CFA Institute Portfolio Management", "https://www.cfainstitute.org/en/programs/cfa-program/curriculum/study-sessions", "course"),
            ("Expected Returns — Ilmanen", "https://www.wiley.com/en-us/Expected+Returns%3A+An+Investor%27s+Guide+to+Harvesting+Market+Rewards-p-9781119990727", "book"),
            ("Portfolio Visualizer", "https://www.portfoliovisualizer.com/", "documentation"),
            ("MSCI Factor Investing", "https://www.msci.com/our-solutions/factor-investing", "article"),
        ]),
        ("Alternative Investments", "private equity, venture capital, real estate, hedge funds, and due diligence", ["Private equity fund structure", "Venture capital deal flow", "Real estate investment basics", "Hedge fund strategies", "Due diligence checklist"], [
            ("ILPA — PE Resources", "https://ilpa.org/resources/", "community"),
            ("National Venture Capital Association", "https://nvca.org/research/", "article"),
            ("Preqin Insights", "https://www.preqin.com/insights", "article"),
            ("CAIA Association", "https://caia.org/", "community"),
        ]),
        ("Investment Career and CFA", "CFA Level 2 topics, Bloomberg terminal, investment writing, and interviews", ["CFA Level 2 equity deep dive", "Bloomberg terminal navigation", "Investment thesis writing", "Pitch book structure", "Buy-side and sell-side interviews"], [
            ("CFA Level 2 Prep — IFT", "https://ift.world/cfa-level-2/", "course"),
            ("Bloomberg Market Concepts", "https://www.bloomberg.com/professional/product/bloomberg-market-concepts/", "course"),
            ("Wall Street Oasis IB Forum", "https://www.wallstreetoasis.com/", "community"),
            ("Breaking Into Wall Street", "https://breakingintowallstreet.com/", "course"),
        ]),
    ],
    "finance_planning": [
        ("Personal Finance Fundamentals", "budgeting, savings, debt management, emergency funds, and financial habits", ["Income, expenses, and net worth", "Budgeting methods (50/30/20)", "Debt payoff strategies", "Emergency fund sizing", "Financial goal setting"], [
            ("Investopedia Personal Finance", "https://www.investopedia.com/personal-finance-4427765", "article"),
            ("The Total Money Makeover — Ramsey", "https://www.ramseysolutions.com/store/", "book"),
            ("Coursera Personal Finance — Duke", "https://www.coursera.org/learn/personal-finance", "course"),
            ("NerdWallet Learning Centre", "https://www.nerdwallet.com/", "article"),
        ]),
        ("Investment Planning and Asset Allocation", "asset allocation, fund selection, tax-advantaged accounts, and rebalancing", ["Asset allocation models", "Mutual funds and ETFs", "Tax-advantaged accounts (401k, IRA)", "Risk tolerance assessment", "Rebalancing strategies"], [
            ("Vanguard Investor Education", "https://investor.vanguard.com/investor-resources-education", "article"),
            ("Morningstar Investing", "https://www.morningstar.com/learn", "article"),
            ("The Little Book of Common Sense Investing — Bogle", "https://www.wiley.com/en-us/The+Little+Book+of+Common+Sense+Investing%2C+Updated+and+Revised-p-9781119404507", "book"),
            ("Investor.gov", "https://www.investor.gov/", "documentation"),
        ]),
        ("Retirement Planning", "retirement income needs, social security, pension analysis, and drawdown strategies", ["Retirement income calculation", "Social security optimisation", "Pension and defined benefit plans", "Safe withdrawal rate (4% rule)", "Sequence-of-returns risk"], [
            ("CFP Board Retirement Resources", "https://www.cfp.net/", "community"),
            ("Kitces Financial Planning", "https://www.kitces.com/", "article"),
            ("Social Security Administration", "https://www.ssa.gov/pubs/", "documentation"),
            ("Coursera Retirement Planning", "https://www.coursera.org/courses?query=retirement+planning", "course"),
        ]),
        ("Insurance and Risk Management", "life, health, disability, property insurance assessment, and risk mitigation", ["Types of life insurance", "Health insurance plan comparison", "Disability insurance income protection", "Property and casualty basics", "Risk management framework"], [
            ("NAIC Insurance Education", "https://content.naic.org/consumer", "documentation"),
            ("Policygenius Insurance Guide", "https://www.policygenius.com/insurance/", "article"),
            ("Life Happens — Insurance Education", "https://www.lifehappens.org/", "article"),
            ("Insurance Information Institute", "https://www.iii.org/", "documentation"),
        ]),
        ("Tax Planning and Estate", "income tax basics, tax-loss harvesting, deductions, and estate planning concepts", ["Income tax brackets and calculation", "Capital gains tax strategies", "Tax-loss harvesting", "Deductions and credits", "Will, trust, and estate basics"], [
            ("IRS Publication 17", "https://www.irs.gov/forms-pubs/about-publication-17", "documentation"),
            ("Kiplinger Tax Guide", "https://www.kiplinger.com/taxes", "article"),
            ("Bogleheads Tax-Efficient Investing", "https://www.bogleheads.org/wiki/Tax-efficient_fund_placement", "article"),
            ("Nolo Estate Planning", "https://www.nolo.com/legal-encyclopedia/estate-planning", "article"),
        ]),
        ("CFP Exam and Advisory Practice", "CFP exam prep, client advisory skills, compliance, and business development", ["CFP exam topic overview", "Client financial plan structure", "Fiduciary duty and compliance", "Client communication and discovery", "Building an advisory practice"], [
            ("CFP Board Exam", "https://www.cfp.net/get-certified/the-cfp-exam", "course"),
            ("College for Financial Planning", "https://www.kaplan.com/cfp/", "course"),
            ("NAPFA — Financial Advisors", "https://www.napfa.org/", "community"),
            ("Financial Planning Association", "https://www.onefpa.org/", "community"),
        ]),
    ],
    # ── Engineering ──────────────────────────────────────────────────────────
    "engineering_mechanical": [
        ("Engineering Mathematics and Physics", "calculus, linear algebra, differential equations, and applied physics review", ["Calculus for engineers", "Linear algebra applications", "Ordinary differential equations", "Newtonian mechanics review", "Numerical methods basics"], [
            ("MIT OCW Calculus", "https://ocw.mit.edu/courses/18-01-single-variable-calculus-fall-2006/", "course"),
            ("Khan Academy Physics", "https://www.khanacademy.org/science/physics", "course"),
            ("Engineering Mathematics — Stroud", "https://www.bloomsbury.com/uk/engineering-mathematics-9781352010268/", "book"),
            ("Paul's Online Math Notes", "https://tutorial.math.lamar.edu/", "article"),
        ]),
        ("Statics and Mechanics of Materials", "equilibrium, free body diagrams, stress, strain, bending, and torsion", ["Static equilibrium and reactions", "Free body diagrams", "Axial stress and strain", "Beam bending and shear diagrams", "Torsion and shaft design"], [
            ("MIT OCW Statics", "https://ocw.mit.edu/courses/2-001-mechanics-materials-i-fall-2006/", "course"),
            ("Engineering Mechanics Statics — Hibbeler", "https://www.pearson.com/en-us/subject-catalog/p/engineering-mechanics-statics/P200000003387", "book"),
            ("Shigley's Machine Design", "https://www.mheducation.com/highered/product/shigley-s-mechanical-engineering-design-budynas-nisbett/M9781264228829.html", "book"),
            ("Engineering Toolbox", "https://www.engineeringtoolbox.com/", "documentation"),
        ]),
        ("CAD and Technical Drawing", "SolidWorks or AutoCAD, GD&T, tolerancing, and engineering drawing standards", ["SolidWorks sketch and features", "Assembly modelling", "Technical drawing standards", "Geometric dimensioning and tolerancing", "Drawing review and approval"], [
            ("SolidWorks Tutorials", "https://www.solidworks.com/sw/education/mechanical-engineering-tutorial.htm", "course"),
            ("Autodesk AutoCAD Learning", "https://www.autodesk.com/products/autocad/learn-training", "course"),
            ("GD&T Basics", "https://www.gdandtbasics.com/", "article"),
            ("GrabCAD Community", "https://grabcad.com/library", "community"),
        ]),
        ("Thermodynamics and Fluid Mechanics", "thermodynamic cycles, heat transfer, fluid statics, and pipe flow", ["Thermodynamic laws and cycles", "Heat transfer modes", "Fluid statics and pressure", "Bernoulli equation and pipe flow", "HVAC system basics"], [
            ("MIT OCW Thermodynamics", "https://ocw.mit.edu/courses/2-006-thermal-fluids-engineering-ii-spring-2008/", "course"),
            ("Fundamentals of Fluid Mechanics — Munson", "https://www.wiley.com/en-us/Fundamentals+of+Fluid+Mechanics%2C+8th+Edition-p-9781119080701", "book"),
            ("Engineering Toolbox Thermodynamics", "https://www.engineeringtoolbox.com/thermodynamics-t_60.html", "documentation"),
            ("Coursera Thermal Engineering", "https://www.coursera.org/courses?query=thermodynamics", "course"),
        ]),
        ("Manufacturing and Materials Science", "material properties, selection, machining, casting, welding, and quality", ["Metals, polymers, and composites", "Material selection criteria", "Machining processes (turning, milling)", "Joining methods (welding, fasteners)", "Quality and inspection basics"], [
            ("ASM International", "https://www.asminternational.org/learn", "article"),
            ("Manufacturing Engineering and Technology — Kalpakjian", "https://www.pearson.com/en-us/subject-catalog/p/manufacturing-engineering-and-technology/P200000003472", "book"),
            ("Granta EduPack", "https://www.ansys.com/academic/educators/ansys-granta-edupack", "documentation"),
            ("MIT OCW Manufacturing", "https://ocw.mit.edu/search/?d=Mechanical%20Engineering", "course"),
        ]),
        ("Engineering Career and Portfolio", "PE exam concepts, engineering ethics, capstone project, and portfolio", ["Professional engineer (PE) overview", "Engineering ethics and safety", "Capstone project documentation", "Technical report writing", "Mechanical engineering job search"], [
            ("ASME Student Resources", "https://www.asme.org/membership/students", "community"),
            ("Engineer.org Career Resources", "https://www.engineer.org/career-resources/", "article"),
            ("edX Engineering Career", "https://www.edx.org/learn/engineering", "course"),
            ("LinkedIn Engineering Groups", "https://www.linkedin.com/", "community"),
        ]),
    ],
    "engineering_electrical": [
        ("Circuit Theory", "Ohm's law, Kirchhoff's laws, AC/DC circuits, phasors, Thevenin/Norton theorem", ["Ohm's law and power", "Kirchhoff's current and voltage laws", "AC circuits and phasors", "Thevenin and Norton equivalents", "Frequency response basics"], [
            ("All About Circuits Textbooks", "https://www.allaboutcircuits.com/textbook/", "book"),
            ("MIT 6.002 Circuits and Electronics", "https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/", "course"),
            ("Khan Academy Electrical Engineering", "https://www.khanacademy.org/science/electrical-engineering", "course"),
            ("CircuitLab Simulator", "https://www.circuitlab.com/", "documentation"),
        ]),
        ("Electronics and Analog Design", "diodes, transistors, op-amps, filters, and analog circuit design", ["Diode characteristics and applications", "BJT and MOSFET amplifiers", "Op-amp configurations", "Active filter design", "Power supply circuits"], [
            ("The Art of Electronics — Horowitz", "https://artofelectronics.net/", "book"),
            ("Analog Devices Learning Centre", "https://www.analog.com/en/education/education-library.html", "article"),
            ("SparkFun Electronics Tutorials", "https://learn.sparkfun.com/", "article"),
            ("LTspice Simulator", "https://www.analog.com/en/design-center/design-tools-and-calculators/ltspice-simulator.html", "documentation"),
        ]),
        ("Digital Systems and Logic Design", "Boolean algebra, combinational and sequential logic, and FPGAs", ["Logic gates and Boolean algebra", "Combinational circuits (MUX, encoder)", "Flip-flops and sequential logic", "Finite state machines", "FPGA introduction with VHDL/Verilog"], [
            ("Nandland FPGA Guide", "https://nandland.com/", "article"),
            ("Digital Design — Mano", "https://www.pearson.com/en-us/subject-catalog/p/digital-design/P200000003578", "book"),
            ("MIT OpenCourseWare Digital Systems", "https://ocw.mit.edu/courses/6-004-computation-structures-spring-2017/", "course"),
            ("Coursera Digital Systems", "https://www.coursera.org/learn/digital-systems", "course"),
        ]),
        ("Embedded Systems Programming", "microcontrollers, C for embedded, RTOS, and communication protocols", ["Arduino and STM32 basics", "Embedded C programming", "Interrupts and timers", "UART, I2C, and SPI protocols", "RTOS task scheduling"], [
            ("Embedded Systems — Jonathan Valvano", "https://users.ece.utexas.edu/~valvano/", "course"),
            ("Coursera Embedded Systems — UC Boulder", "https://www.coursera.org/learn/introduction-embedded-systems", "course"),
            ("Bare Metal Programming with ARM", "https://github.com/cpq/bare-metal-programming-guide", "article"),
            ("STM32 CubeIDE Documentation", "https://www.st.com/en/development-tools/stm32cubeide.html", "documentation"),
        ]),
        ("Power Systems and Signal Processing", "power electronics, motor drives, DSP fundamentals, and Fourier analysis", ["Power electronics converters", "AC motor drives and VFDs", "Fourier series and transform", "Digital filters (FIR, IIR)", "Control systems basics"], [
            ("MIT OCW Power Electronics", "https://ocw.mit.edu/courses/6-334-power-electronics-spring-2007/", "course"),
            ("Understanding DSP — Lyons", "https://www.pearson.com/en-us/subject-catalog/p/understanding-digital-signal-processing/P200000003310", "book"),
            ("Texas Instruments Training", "https://training.ti.com/", "course"),
            ("Control Tutorials for MATLAB", "https://ctms.engin.umich.edu/CTMS/", "article"),
        ]),
        ("PCB Design and Electrical Career", "KiCad layout, EMC basics, engineering portfolio, and career pathways", ["KiCad schematic capture", "PCB layout and design rules", "EMC and signal integrity basics", "Electrical engineering portfolio", "IEEE student membership and career"], [
            ("KiCad Documentation", "https://docs.kicad.org/", "documentation"),
            ("IPC PCB Design Standards", "https://www.ipc.org/", "community"),
            ("IEEE Career Resources", "https://careers.ieee.org/", "community"),
            ("Hackaday Projects", "https://hackaday.io/projects", "community"),
        ]),
    ],
    "engineering_civil": [
        ("Structural Analysis", "beams, trusses, frames, influence lines, and indeterminate structures", ["Static determinacy and reactions", "Beam shear and moment diagrams", "Truss analysis (method of joints)", "Frame analysis", "Indeterminate structure basics"], [
            ("MIT OCW Structural Analysis", "https://ocw.mit.edu/courses/1-050-solid-mechanics-fall-2004/", "course"),
            ("Structural Analysis — Hibbeler", "https://www.pearson.com/en-us/subject-catalog/p/structural-analysis/P200000003383", "book"),
            ("Engineering Toolbox Civil", "https://www.engineeringtoolbox.com/", "documentation"),
            ("SkyCiv Structural Calculator", "https://skyciv.com/", "article"),
        ]),
        ("Geotechnical Engineering", "soil mechanics, site investigation, foundations, and slope stability", ["Soil classification and properties", "Effective stress and pore pressure", "Foundation types and bearing capacity", "Consolidation and settlement", "Slope stability analysis"], [
            ("MIT OCW Soil Mechanics", "https://ocw.mit.edu/courses/1-361-advanced-soil-mechanics-fall-2004/", "course"),
            ("Principles of Geotechnical Engineering — Das", "https://www.cengage.com/c/principles-of-geotechnical-engineering-9e-das/9781305970939/", "book"),
            ("GeoTechDataBase", "https://www.geotechdata.info/", "documentation"),
            ("ASCE Geotechnical Resources", "https://www.asce.org/communities/institutes-and-technical-groups/geo-institute", "community"),
        ]),
        ("Structural Design and Building Codes", "reinforced concrete, steel design, load combinations, and building codes", ["Load types and load combinations", "Reinforced concrete design (ACI 318)", "Steel design (AISC 360)", "Connection design", "Reading structural drawings"], [
            ("ACI Learning — Concrete", "https://www.concrete.org/education/acilearning.aspx", "course"),
            ("AISC Steel Design Guide", "https://www.aisc.org/education/", "course"),
            ("Design of Concrete Structures — Nilson", "https://www.mheducation.com/highered/product/design-concrete-structures-nilson/M9781259820960.html", "book"),
            ("ASCE 7 Standards", "https://www.asce.org/publications-and-news/asce-7", "documentation"),
        ]),
        ("Construction Management and BIM", "project scheduling, cost estimation, BIM workflows, and site safety", ["Critical path method (CPM)", "Cost estimating and takeoff", "BIM introduction with Revit/Navisworks", "Construction contracts", "Site safety (OSHA basics)"], [
            ("Coursera Construction Management", "https://www.coursera.org/learn/construction-project-management", "course"),
            ("Autodesk Revit Learning", "https://www.autodesk.com/products/revit/learn-training", "course"),
            ("OSHA Construction Safety", "https://www.osha.gov/construction", "documentation"),
            ("Construction Specifications Institute", "https://www.csiresources.org/", "community"),
        ]),
        ("Transportation and Environmental Engineering", "road geometry, drainage, environmental impact, and sustainability", ["Highway alignment and geometry", "Stormwater drainage design", "Traffic flow fundamentals", "Environmental impact assessment", "Green infrastructure and sustainability"], [
            ("Highway Engineering — Garber", "https://www.cengage.com/c/highway-engineering-planning-design-and-operations-garber-hoel/9780357370155/", "book"),
            ("US DOT Federal Highway Resources", "https://highways.dot.gov/research-technology", "documentation"),
            ("EPA Stormwater Management", "https://www.epa.gov/npdes/stormwater-management", "documentation"),
            ("Transportation Research Board", "https://www.trb.org/", "community"),
        ]),
        ("Professional Practice and Civil Career", "PE exam, engineering ethics, report writing, and portfolio", ["PE exam overview (Civil)", "Engineering ethics and professional responsibility", "Technical report and design documentation", "Civil engineering portfolio", "Career pathways in civil engineering"], [
            ("ASCE — PE Exam Resources", "https://www.asce.org/career-growth/professional-licensure", "community"),
            ("NCEES PE Exam Prep", "https://ncees.org/engineering/pe/", "documentation"),
            ("Civil Engineering Forum", "https://www.eng-tips.com/", "community"),
            ("LinkedIn Civil Engineering Groups", "https://www.linkedin.com/", "community"),
        ]),
    ],
    # ── Healthcare ───────────────────────────────────────────────────────────
    "healthcare_clinician": [
        ("Human Anatomy and Physiology", "body systems, organ function, homeostasis, and clinical relevance", ["Musculoskeletal system", "Cardiovascular and respiratory systems", "Nervous system and neuroanatomy", "Endocrine and immune systems", "Homeostasis and disease mechanisms"], [
            ("Khan Academy Health and Medicine", "https://www.khanacademy.org/science/health-and-medicine", "course"),
            ("OpenStax Anatomy and Physiology", "https://openstax.org/details/books/anatomy-and-physiology-2e", "book"),
            ("Visible Body", "https://www.visiblebody.com/", "course"),
            ("TeachMe Anatomy", "https://teachmeanatomy.info/", "article"),
        ]),
        ("Clinical Assessment and Reasoning", "history taking, physical examination, differential diagnosis, and SOAP documentation", ["Patient history taking (HPI, PMH)", "Systems-based physical examination", "Differential diagnosis construction", "SOAP note writing", "Clinical handoff communication"], [
            ("Geeky Medics Clinical Skills", "https://geekymedics.com/clinical-skills/", "article"),
            ("Bates' Guide to Physical Examination", "https://www.wolterskluwer.com/en/know/clinical-effectiveness-blog/bates-guide-to-physical-examination", "book"),
            ("Osmosis Clinical Reasoning", "https://www.osmosis.org/", "course"),
            ("Stanford Medicine 25", "https://stanfordmedicine25.stanford.edu/", "article"),
        ]),
        ("Pharmacology and Therapeutics", "drug classes, mechanisms, dosing principles, and adverse effects", ["Drug receptor mechanisms", "Major drug classes overview", "Pharmacokinetics (ADME)", "Adverse effects and drug interactions", "Prescribing principles and safety"], [
            ("Sketchy Pharmacology", "https://www.sketchy.com/", "course"),
            ("Rang and Dale's Pharmacology", "https://www.elsevier.com/books/rang-and-dales-pharmacology/ritter/978-0-7020-8060-9", "book"),
            ("RxList Drug Information", "https://www.rxlist.com/", "documentation"),
            ("UpToDate Drug Monographs", "https://www.uptodate.com/", "documentation"),
        ]),
        ("Evidence-Based Practice", "reading research, clinical guidelines, critical appraisal, and applying evidence", ["Study design hierarchy", "Critically appraising RCTs", "Systematic reviews and meta-analysis", "Clinical guideline interpretation", "Applying evidence to individual patients"], [
            ("Cochrane Library", "https://www.cochranelibrary.com/", "article"),
            ("PubMed", "https://pubmed.ncbi.nlm.nih.gov/", "documentation"),
            ("Centre for Evidence-Based Medicine", "https://www.cebm.ox.ac.uk/resources", "article"),
            ("BMJ Best Practice", "https://bestpractice.bmj.com/", "documentation"),
        ]),
        ("Patient Safety and Medical Ethics", "infection control, medication safety, informed consent, and ethical frameworks", ["Infection control protocols", "Medication safety (5 rights)", "Informed consent process", "Medical ethics principles", "Duty of care and confidentiality"], [
            ("WHO Patient Safety", "https://www.who.int/teams/integrated-health-services/patient-safety", "documentation"),
            ("Institute for Healthcare Improvement", "https://www.ihi.org/", "article"),
            ("AMA Medical Ethics", "https://www.ama-assn.org/delivering-care/ethics", "documentation"),
            ("BMJ Medical Ethics", "https://jme.bmj.com/", "article"),
        ]),
        ("Healthcare Career and Specialisation", "licensing pathways, CPD, specialisation, and professional portfolio", ["Medical licensing requirements", "Continuing professional development", "Specialty training pathways", "Clinical portfolio development", "Healthcare job search and interviews"], [
            ("WHO Health Workforce Resources", "https://www.who.int/health-topics/health-workforce", "article"),
            ("Medscape Education", "https://www.medscape.com/education/", "course"),
            ("BMJ Careers", "https://www.bmj.com/careers", "community"),
            ("NEJM Career Centre", "https://careers.nejm.org/", "community"),
        ]),
    ],
    "healthcare_public": [
        ("Epidemiology Fundamentals", "disease frequency, study designs, bias, causality, and surveillance systems", ["Incidence and prevalence", "Study designs (cohort, case-control, RCT)", "Bias and confounding", "Causality (Bradford-Hill criteria)", "Disease surveillance systems"], [
            ("Coursera Epidemiology — Johns Hopkins", "https://www.coursera.org/learn/epidemiology", "course"),
            ("CDC Epidemiology 101", "https://www.cdc.gov/training/publichealth101/", "course"),
            ("Modern Epidemiology — Rothman", "https://www.wolterskluwer.com/en/solutions/ovid/modern-epidemiology-109", "book"),
            ("Our World in Data", "https://ourworldindata.org/", "article"),
        ]),
        ("Biostatistics for Public Health", "descriptive statistics, regression, survival analysis, and R or SPSS", ["Descriptive statistics in health data", "Chi-square and t-tests", "Logistic and linear regression", "Survival analysis basics", "R or SPSS for public health"], [
            ("Johns Hopkins Biostatistics", "https://www.coursera.org/learn/biostatistics", "course"),
            ("OpenEpi Tools", "https://www.openepi.com/", "documentation"),
            ("R for Epidemiology", "https://www.r4epi.com/", "book"),
            ("StatQuest Biostatistics", "https://statquest.org/", "video"),
        ]),
        ("Health Data and Informatics", "health databases, EHR data, data quality, GIS mapping, and reporting", ["Electronic health records and data", "Public health databases (CDC, WHO)", "Data cleaning and quality", "GIS mapping for health", "Public health dashboards"], [
            ("CDC Public Health Data", "https://www.cdc.gov/datastatistics/", "documentation"),
            ("WHO Global Health Observatory", "https://www.who.int/data/gho", "documentation"),
            ("Health GIS — Esri", "https://www.esri.com/en-us/industries/health/overview", "article"),
            ("Coursera Data Science for Health", "https://www.coursera.org/courses?query=health+data", "course"),
        ]),
        ("Health Policy and Systems", "health system models, policy cycle, financing, advocacy, and evaluation", ["Health system frameworks (WHO)", "Policy cycle analysis", "Health financing models", "Policy brief writing", "Health program evaluation"], [
            ("WHO Health Systems", "https://www.who.int/health-topics/health-systems-governance", "documentation"),
            ("Johns Hopkins Health Policy", "https://www.coursera.org/learn/health-policy-and-the-affordable-care-act", "course"),
            ("Nuffield Trust Policy Reports", "https://www.nuffieldtrust.org.uk/", "article"),
            ("Lancet Health Policy", "https://www.thelancet.com/journals/lancet/issue/current", "article"),
        ]),
        ("Disease Prevention and Global Health", "vaccination, outbreak investigation, NCD prevention, and SDG health goals", ["Vaccination programme design", "Outbreak investigation steps", "NCD risk factor reduction", "Global health burden (GBD)", "SDG health targets"], [
            ("WHO Disease Control Priorities", "https://www.dcp-3.org/", "book"),
            ("CDC Global Health", "https://www.cdc.gov/globalhealth/", "documentation"),
            ("Coursera Global Health — Duke", "https://www.coursera.org/learn/global-health", "course"),
            ("Lancet Global Health", "https://www.thelancet.com/journals/langlo/home", "article"),
        ]),
        ("Public Health Career and Portfolio", "MPH pathways, grant writing, research poster, and career planning", ["MPH programme overview", "Grant writing basics", "Research poster design", "Public health portfolio", "Career paths in public health"], [
            ("ASPPH Graduate Programs", "https://www.aspph.org/", "community"),
            ("CDC Public Health Fellows", "https://www.cdc.gov/phap/", "community"),
            ("Public Health Foundation", "https://www.phf.org/", "community"),
            ("LinkedIn Public Health Groups", "https://www.linkedin.com/", "community"),
        ]),
    ],
    "healthcare_research": [
        ("Research Design and Methodology", "experimental, observational, and qualitative designs with protocol writing", ["Research question and hypothesis", "Experimental and observational designs", "Qualitative research methods", "Study protocol writing", "Sample size justification"], [
            ("NIH Research Training", "https://researchtraining.nih.gov/", "course"),
            ("BMJ Research Methods", "https://www.bmj.com/research-methods", "article"),
            ("Clinical Research: A Practical Guide", "https://www.cambridge.org/core/books/clinical-research/", "book"),
            ("Coursera Clinical Research Design", "https://www.coursera.org/learn/clinical-trials", "course"),
        ]),
        ("Biostatistics and Statistical Analysis", "power calculations, regression, survival analysis, and R/SAS", ["Power and sample size", "Descriptive and inferential statistics", "Regression modelling", "Survival analysis (Kaplan-Meier)", "R or SAS for clinical data"], [
            ("Coursera Biostatistics in Public Health", "https://www.coursera.org/specializations/biostatistics-public-health", "course"),
            ("Analysis of Clinical Trials Using SAS", "https://www.sas.com/en_us/home.html", "book"),
            ("OpenEpi Statistical Tools", "https://www.openepi.com/", "documentation"),
            ("R for Clinical Data", "https://r4ds.had.co.nz/", "book"),
        ]),
        ("GCP, Ethics, and Regulatory Affairs", "ICH-GCP, IRB/ethics approval, adverse event reporting, and FDA/EMA basics", ["ICH-GCP principles", "IRB and ethics committee submission", "Informed consent for research", "Adverse event and SAE reporting", "FDA and EMA regulatory overview"], [
            ("ICH GCP Guidelines", "https://www.ich.org/page/e6r2-good-clinical-practice-integrated-addendum", "documentation"),
            ("CITI Program GCP Training", "https://www.citiprogram.org/", "course"),
            ("FDA Clinical Trials", "https://www.fda.gov/patients/clinical-trials-what-patients-need-know", "documentation"),
            ("EMA Guidelines", "https://www.ema.europa.eu/en/human-regulatory/research-development/clinical-trials", "documentation"),
        ]),
        ("Clinical Data Management", "CRF design, EDC systems, data cleaning, CDISC, and data quality", ["Case report form (CRF) design", "EDC systems (Medidata, REDCap)", "Data cleaning and query resolution", "CDISC CDASH and SDTM standards", "Database lock procedures"], [
            ("REDCap Data Management", "https://www.project-redcap.org/", "documentation"),
            ("CDISC Standards", "https://www.cdisc.org/standards", "documentation"),
            ("SCDM Clinical Data Management", "https://www.scdm.org/", "community"),
            ("Society for Clinical Data Management", "https://www.scdm.org/", "community"),
        ]),
        ("Statistical Reporting and Submission", "CONSORT reporting, statistical analysis plan, meta-analysis, and regulatory submission", ["Statistical analysis plan (SAP)", "CONSORT reporting checklist", "Systematic review and meta-analysis", "Regulatory submission packages", "Clinical study report (CSR)"], [
            ("CONSORT Statement", "https://www.consort-statement.org/", "documentation"),
            ("Cochrane Handbook", "https://training.cochrane.org/handbook", "book"),
            ("FDA Guidance Documents", "https://www.fda.gov/drugs/guidance-compliance-regulatory-information/guidances-drugs", "documentation"),
            ("RevMan Software", "https://training.cochrane.org/online-learning/core-software/revman", "documentation"),
        ]),
        ("Publication and Research Career", "scientific writing, peer review, grant funding, and research portfolio", ["Scientific manuscript structure (IMRaD)", "Peer review process", "Grant proposal writing", "Presenting at conferences", "Building a research portfolio"], [
            ("Elsevier Researcher Academy", "https://researcheracademy.elsevier.com/", "course"),
            ("PubMed Writing Resources", "https://www.ncbi.nlm.nih.gov/pmc/about/intro/", "documentation"),
            ("NIH Grant Writing", "https://grants.nih.gov/grants/how-to-apply-application-guide.htm", "documentation"),
            ("Research4Life", "https://www.research4life.org/", "community"),
        ]),
    ],
    # ── Education ────────────────────────────────────────────────────────────
    "education_designer": [
        ("Learning Theory and Instructional Science", "behaviourism, cognitivism, constructivism, adult learning, and motivation", ["Behaviourist conditioning models", "Cognitive load theory", "Constructivism and discovery learning", "Adult learning (andragogy) principles", "Motivation and engagement theories"], [
            ("Learning Scientists", "https://www.learningscientists.org/", "article"),
            ("Make It Stick — Brown", "https://www.retrievalpractice.org/make-it-stick", "book"),
            ("Coursera Learning How to Learn", "https://www.coursera.org/learn/learning-how-to-learn", "course"),
            ("Association for Talent Development", "https://www.td.org/", "community"),
        ]),
        ("Instructional Design Models", "ADDIE, SAM, backward design, and rapid prototyping workflows", ["ADDIE process and phases", "SAM and iterative design", "Backward design (Understanding by Design)", "Rapid prototyping approach", "Choosing the right ID model"], [
            ("Understanding by Design — Wiggins", "https://jaymctighe.com/resources/", "book"),
            ("ATD Instructional Design Resources", "https://www.td.org/topics/instructional-design", "article"),
            ("ID Models Comparison — Eduflow", "https://www.eduflow.com/blog/instructional-design-models", "article"),
            ("ISTE Standards for Educators", "https://www.iste.org/standards/educators", "documentation"),
        ]),
        ("Content Development and Scripting", "script writing, storyboarding, visual design for learning, and narration", ["Learning objective-aligned scripting", "Storyboard creation", "Visual design for learning materials", "Narration script and recording", "Accessibility in content design"], [
            ("Articulate Community", "https://community.articulate.com/", "community"),
            ("The eLearning Designer's Action Guide", "https://www.td.org/books/the-elearning-designers-action-guide-to-writing-great-elearning", "book"),
            ("Adobe Captivate Tutorials", "https://elearning.adobe.com/adobe-captivate/", "course"),
            ("Canva for Educators", "https://www.canva.com/education/", "course"),
        ]),
        ("eLearning Development Tools", "Articulate 360, Rise, H5P, video production, SCORM, and xAPI", ["Articulate Storyline basics", "Rise 360 responsive courses", "H5P interactive content", "Video editing for learning", "SCORM and xAPI publishing"], [
            ("Articulate 360 Training", "https://community.articulate.com/series/articulate-360", "course"),
            ("H5P Content Types", "https://h5p.org/content-types-and-applications", "documentation"),
            ("iSpring Suite Tutorials", "https://www.ispringsolutions.com/ispring-suite/tutorials", "course"),
            ("EdTech Hub Tools", "https://edtechhub.org/", "article"),
        ]),
        ("Assessment Design and Kirkpatrick Evaluation", "formative assessment, summative tests, rubrics, and Kirkpatrick four levels", ["Alignment of objectives and assessment", "Formative and summative design", "Rubric and scoring guide creation", "Kirkpatrick Level 1–4 evaluation", "Learner data analysis"], [
            ("Kirkpatrick Model Guide", "https://www.kirkpatrickpartners.com/", "article"),
            ("ASCD Assessment Resources", "https://www.ascd.org/topics/assessment", "article"),
            ("EdApp Assessment Features", "https://www.edapp.com/blog/types-of-assessments/", "article"),
            ("Survey Tools for L&D", "https://www.surveymonkey.com/mp/learning-and-development/", "article"),
        ]),
        ("LMS Administration and ID Career", "Moodle, Canvas, portfolio building, and instructional design job search", ["LMS platform comparison", "Course publishing and learner management", "ID portfolio with case studies", "Freelance vs corporate ID pathways", "ID job search and interviews"], [
            ("Moodle Documentation", "https://docs.moodle.org/", "documentation"),
            ("Canvas by Instructure", "https://community.canvaslms.com/", "community"),
            ("eLearning Industry Jobs", "https://elearningindustry.com/jobs", "community"),
            ("LinkedIn Learning for ID", "https://www.linkedin.com/learning/topics/instructional-design", "course"),
        ]),
    ],
    "education_edtech": [
        ("EdTech Landscape and Trends", "learning platforms, major players, adoption barriers, and futures of learning", ["History of educational technology", "LMS and learning platform comparison", "Edtech startup landscape", "Adoption barriers in education", "Emerging trends (AI, VR, micro-learning)"], [
            ("EdSurge", "https://www.edsurge.com/", "article"),
            ("HolonIQ EdTech Research", "https://www.holoniq.com/", "article"),
            ("Coursera EdTech for Educators", "https://www.coursera.org/learn/edtech", "course"),
            ("MIT Teaching Systems Lab", "https://tsl.mit.edu/", "article"),
        ]),
        ("Learning Design for Digital Environments", "microlearning, gamification, adaptive learning, and social learning design", ["Microlearning content design", "Gamification mechanics for learning", "Adaptive learning path design", "Social and peer learning models", "Mobile-first learning design"], [
            ("Growth Engineering Gamification", "https://www.growthengineering.co.uk/gamification-in-elearning/", "article"),
            ("Designing for Behavior Change", "https://www.oreilly.com/library/view/designing-for-behavior/9781449367008/", "book"),
            ("EdTech UX Guide — Nielsen Norman", "https://www.nngroup.com/articles/elearning-usability/", "article"),
            ("Duolingo Research Blog", "https://blog.duolingo.com/", "article"),
        ]),
        ("LMS Implementation and Management", "platform setup, user management, SCORM/xAPI, and integrations", ["LMS selection and setup", "User roles and enrolment management", "SCORM and xAPI content publishing", "LMS integration with HR/SIS", "Troubleshooting and support"], [
            ("Moodle Admin Guide", "https://docs.moodle.org/en/Administrator_documentation", "documentation"),
            ("Canvas Administration", "https://community.canvaslms.com/t5/Admin-Guide/tkb-p/admin_guide", "documentation"),
            ("TalentLMS Blog", "https://www.talentlms.com/blog/", "article"),
            ("ADL xAPI Resources", "https://adlnet.gov/projects/xapi/", "documentation"),
        ]),
        ("Learning Analytics and Data", "completion data, assessment analytics, xAPI/LRS, and data-driven improvement", ["Learning analytics fundamentals", "Engagement and completion metrics", "xAPI statement design", "LRS setup and querying", "Data-informed course improvement"], [
            ("Society for Learning Analytics Research", "https://www.solaresearch.org/", "community"),
            ("xAPI Spec Documentation", "https://github.com/adlnet/xAPI-Spec", "documentation"),
            ("Watershed LRS Learning", "https://watershedlrs.com/resources/", "article"),
            ("Coursera Learning Analytics", "https://www.coursera.org/learn/learning-analytics", "course"),
        ]),
        ("AI and Emerging Technologies in Education", "AI tutors, generative AI for content creation, and ethical considerations", ["AI tutoring systems overview", "Generative AI for lesson and quiz creation", "Personalised learning with AI", "Bias and ethics in EdTech AI", "AI tool evaluation for educators"], [
            ("UNESCO AI in Education", "https://www.unesco.org/en/digital-education/artificial-intelligence", "article"),
            ("Khan Academy Khanmigo AI", "https://www.khanacademy.org/khan-labs", "article"),
            ("AI for Education — TeachAI", "https://www.teachai.org/", "article"),
            ("MIT Media Lab Education Research", "https://www.media.mit.edu/groups/personal-robots/overview/", "article"),
        ]),
        ("EdTech Product and Career", "product management for ed, UX research in learning, portfolio, and job search", ["EdTech product management basics", "UX research for learning products", "Accessibility in education technology", "EdTech portfolio with case studies", "EdTech job search and companies"], [
            ("EdTech Product Management Guide", "https://productschool.com/resources/", "article"),
            ("ISTE EdTech Certification", "https://www.iste.org/", "community"),
            ("EdSurge Jobs", "https://www.edsurge.com/jobs", "community"),
            ("eLearning Industry EdTech Resources", "https://elearningindustry.com/", "article"),
        ]),
    ],
    "education_teacher": [
        ("Pedagogy and Learning Science", "learning theories, memory research, differentiation, and inclusive teaching", ["Behaviourism, cognitivism, and constructivism", "Retrieval practice and spaced repetition", "Differentiated instruction", "Universal design for learning (UDL)", "Cultural responsiveness in teaching"], [
            ("Learning Scientists", "https://www.learningscientists.org/", "article"),
            ("Edutopia Teaching Strategies", "https://www.edutopia.org/", "article"),
            ("Teach Like a Champion — Lemov", "https://teachlikeachampion.org/", "book"),
            ("ASCD Learning Sciences", "https://www.ascd.org/", "community"),
        ]),
        ("Curriculum and Lesson Planning", "standards alignment, backward design, lesson structure, and pacing guides", ["Standards unpacking", "Backward design for lessons", "Lesson plan structure (objectives, activities, closure)", "Pacing guide development", "Long-range curriculum planning"], [
            ("Understanding by Design", "https://jaymctighe.com/resources/", "book"),
            ("Bloom's Taxonomy", "https://www.bloomstaxonomy.net/", "article"),
            ("Teachers Pay Teachers", "https://www.teacherspayteachers.com/", "community"),
            ("Buck Institute PBL", "https://www.pblworks.org/", "course"),
        ]),
        ("Instructional Strategies and Active Learning", "direct instruction, cooperative learning, inquiry, and project-based learning", ["Direct instruction techniques", "Think-pair-share and cooperative learning", "Inquiry-based learning design", "Project-based learning (PBL)", "Flipped classroom approach"], [
            ("Kagan Cooperative Learning", "https://www.kaganonline.com/", "book"),
            ("Buck Institute PBL", "https://www.pblworks.org/", "course"),
            ("Harvard Project Zero", "https://pz.harvard.edu/", "article"),
            ("Edutopia Active Learning", "https://www.edutopia.org/active-learning", "article"),
        ]),
        ("Assessment, Feedback, and Grading", "formative checks, rubrics, feedback quality, standards-based grading", ["Exit tickets and formative checks", "Rubric design and alignment", "Feedback language and timeliness", "Standards-based grading principles", "Assessment data for re-teaching"], [
            ("Dylan Wiliam Formative Assessment", "https://www.dylanwiliamcenter.com/", "article"),
            ("Marzano Research Grading", "https://www.marzanoresources.com/", "book"),
            ("ASCD Assessment", "https://www.ascd.org/topics/assessment", "article"),
            ("Google Forms for Formative Assessment", "https://support.google.com/docs/topic/9055404", "documentation"),
        ]),
        ("Classroom Management and Positive Culture", "routines, relationships, proactive management, and restorative practices", ["Building classroom routines", "Positive teacher-student relationships", "Proactive behaviour management", "Restorative conversations", "Inclusive classroom environment"], [
            ("Responsive Classroom", "https://www.responsiveclassroom.org/", "book"),
            ("PBIS World", "https://www.pbisworld.com/", "documentation"),
            ("Edutopia Classroom Management", "https://www.edutopia.org/classroom-management", "article"),
            ("Culturally Responsive Teaching — Hammond", "https://www.zarrettahammond.com/", "book"),
        ]),
        ("Teaching Career and Professional Development", "teaching portfolio, reflection, CPD, and career pathways", ["Teaching philosophy statement", "Portfolio evidence and artefacts", "Peer observation and mentoring", "Professional learning communities (PLC)", "Career pathways (leadership, curriculum, coaching)"], [
            ("National Board Certification", "https://www.nbpts.org/", "community"),
            ("ASCD Professional Development", "https://www.ascd.org/professional-learning", "community"),
            ("Teaching Channel", "https://www.teachingchannel.com/", "video"),
            ("Edutopia Teacher Growth", "https://www.edutopia.org/professional-development", "article"),
        ]),
    ],
    # ── Business ─────────────────────────────────────────────────────────────
    "business_pm": [
        ("Product Thinking and Vision", "customer problems, product vision, success metrics, OKRs, and strategy", ["Customer problem framing", "Product vision and strategy", "OKRs and north star metrics", "Competitive landscape analysis", "Product market fit signals"], [
            ("Inspired — Marty Cagan", "https://www.svpg.com/books/inspired-how-to-create-tech-products-customers-love-2nd-edition/", "book"),
            ("Lenny's Newsletter", "https://www.lennysnewsletter.com/", "article"),
            ("Product School", "https://productschool.com/resources/", "course"),
            ("Mind the Product", "https://www.mindtheproduct.com/", "community"),
        ]),
        ("Discovery and Validation", "user interviews, problem sizing, prototype testing, and opportunity prioritisation", ["User interview facilitation", "Jobs-to-be-done framework", "Opportunity sizing (TAM, SAM, SOM)", "Rapid prototype testing", "Kill criteria and decision gates"], [
            ("The Mom Test — Rob Fitzpatrick", "https://www.momtestbook.com/", "book"),
            ("IDEO Design Thinking", "https://designthinking.ideo.com/", "article"),
            ("Maze User Research", "https://maze.co/guides/", "article"),
            ("Superhuman Product Research", "https://review.firstround.com/how-superhuman-built-an-engine-to-find-product-market-fit", "article"),
        ]),
        ("Roadmapping and Prioritisation", "RICE/ICE scoring, stakeholder alignment, trade-off decisions, and roadmap formats", ["Prioritisation frameworks (RICE, ICE, MoSCoW)", "Roadmap types and formats", "Stakeholder alignment workshops", "Trade-off and dependency management", "Communicating roadmap changes"], [
            ("Productboard Roadmap Guide", "https://www.productboard.com/blog/product-roadmap-guide/", "article"),
            ("SVPG Articles", "https://www.svpg.com/articles/", "article"),
            ("Aha! Roadmapping", "https://www.aha.io/roadmapping/guide", "article"),
            ("Product Plan Templates", "https://www.productplan.com/learn/", "article"),
        ]),
        ("Agile and Delivery", "Scrum ceremonies, sprint planning, backlog grooming, and delivery metrics", ["Scrum roles and ceremonies", "Sprint planning and backlog refinement", "Definition of done and acceptance criteria", "Velocity and throughput metrics", "Agile retrospective facilitation"], [
            ("Atlassian Agile Coach", "https://www.atlassian.com/agile", "documentation"),
            ("Scrum Guide", "https://scrumguides.org/", "documentation"),
            ("Shape Up — Basecamp", "https://basecamp.com/shapeup", "book"),
            ("Jira Product Management", "https://www.atlassian.com/software/jira/guides/product-management", "documentation"),
        ]),
        ("Product Analytics and Growth", "funnel analysis, cohort retention, A/B experiments, and growth loops", ["Funnel definition and measurement", "Cohort retention analysis", "A/B experiment design", "Growth loop identification", "Dashboard creation in Mixpanel or Amplitude"], [
            ("Mixpanel Analytics", "https://mixpanel.com/blog/", "article"),
            ("Amplitude Product Analytics", "https://amplitude.com/blog/", "article"),
            ("Lean Analytics — Maurya", "https://leananalyticsbook.com/", "book"),
            ("Reforge Growth", "https://www.reforge.com/", "course"),
        ]),
        ("Go-to-Market and PM Career", "launch planning, pricing, PM interview prep, and portfolio", ["Product launch checklist", "Pricing strategy basics", "Product sense interview practice", "Execution interview frameworks", "PM portfolio and case studies"], [
            ("PM Interview — Lewis Lin", "https://www.lewis-lin.com/decode-and-conquer", "book"),
            ("Exponent PM Courses", "https://www.tryexponent.com/", "course"),
            ("ProductHunt Community", "https://www.producthunt.com/", "community"),
            ("Cracking the PM Interview", "https://www.crackingthepminterview.com/", "book"),
        ]),
    ],
    "business_analyst": [
        ("Business Analysis Foundations", "BA role, stakeholder mapping, requirements types, and BABOK overview", ["BA role and responsibilities", "Stakeholder identification and mapping", "Requirements types (business, functional, non-functional)", "BABOK knowledge areas overview", "Business analysis planning"], [
            ("IIBA BABOK Guide", "https://www.iiba.org/career-resources/a-business-analysts-body-of-knowledge/", "book"),
            ("Business Analysis Excellence", "https://www.modernanalyst.com/", "article"),
            ("Coursera Business Analysis", "https://www.coursera.org/learn/uva-darden-getting-started-agile", "course"),
            ("BA Times", "https://www.batimes.com/", "article"),
        ]),
        ("Requirements Elicitation and Documentation", "interviews, workshops, user stories, use cases, and acceptance criteria", ["Elicitation techniques (interview, workshop, observation)", "User stories and epics", "Use case specification", "Acceptance criteria writing", "Requirements traceability matrix"], [
            ("User Story Mapping — Jeff Patton", "https://www.jpattonassociates.com/user-story-mapping/", "book"),
            ("Agile Requirements — Lucidchart", "https://www.lucidchart.com/blog/requirements-in-agile-projects", "article"),
            ("Aha! Requirements Guide", "https://www.aha.io/roadmapping/guide/requirements-management", "article"),
            ("IBM Engineering Requirements", "https://www.ibm.com/products/engineering-requirements-quality-studio", "documentation"),
        ]),
        ("Process Modelling and Analysis", "BPMN, AS-IS/TO-BE mapping, value stream, and gap analysis", ["Business process mapping (BPMN 2.0)", "AS-IS process documentation", "TO-BE process design", "Value stream mapping", "Gap and root cause analysis"], [
            ("OMG BPMN Standard", "https://www.omg.org/spec/BPMN/2.0/", "documentation"),
            ("Lucidchart BPMN Templates", "https://www.lucidchart.com/pages/bpmn-diagram-tool", "documentation"),
            ("Learning to See — Rother", "https://www.amazon.com/Learning-See-Stream-Mapping-Eliminate/dp/0966784308", "book"),
            ("BPM Institute", "https://www.bpminstitute.org/", "community"),
        ]),
        ("Data Analysis for Business Decisions", "Excel, SQL basics, dashboard creation, and business reporting", ["Advanced Excel for BA", "SQL for business queries", "Data visualisation (Tableau/Power BI)", "Business KPI dashboard", "Communicating data insights"], [
            ("Mode Analytics SQL Tutorial", "https://mode.com/sql-tutorial/", "course"),
            ("Tableau Desktop Public Training", "https://www.tableau.com/learn/training", "course"),
            ("Power BI Learning", "https://learn.microsoft.com/en-us/power-bi/", "documentation"),
            ("CFI Excel for BA", "https://corporatefinanceinstitute.com/resources/excel/", "course"),
        ]),
        ("Solution Design and UAT", "functional specifications, UAT planning, change management, and delivery", ["Functional specification writing", "Test scenario and test case design", "UAT facilitation and sign-off", "Change impact assessment", "Solution handover documentation"], [
            ("ISTQB Software Testing Foundation", "https://www.istqb.org/", "community"),
            ("Agile Testing — Crispin", "https://agiletester.ca/", "book"),
            ("Change Management Toolkit — Prosci", "https://www.prosci.com/", "article"),
            ("TestRail Testing Management", "https://www.testrail.com/", "documentation"),
        ]),
        ("Business Analysis Career", "CBAP certification, BA portfolio, case interviews, and career planning", ["CBAP exam overview", "BA portfolio artefact types", "Business case presentation practice", "Consulting and in-house BA paths", "BA job search and networking"], [
            ("IIBA Certification", "https://www.iiba.org/certification/", "community"),
            ("Modern Analyst Career", "https://www.modernanalyst.com/Careers.aspx", "article"),
            ("LinkedIn Business Analysis Groups", "https://www.linkedin.com/", "community"),
            ("BA Career Centre — BA Times", "https://www.batimes.com/career-centre.html", "community"),
        ]),
    ],
    "business_strategy": [
        ("Strategic Frameworks and Analysis", "Porter's Five Forces, SWOT, PESTLE, value chain, and BCG matrix", ["Porter's Five Forces analysis", "SWOT and TOWS matrix", "PESTLE environmental scan", "Value chain analysis", "BCG portfolio matrix"], [
            ("Harvard Business Review Strategy", "https://hbr.org/topic/subject/strategy", "article"),
            ("Coursera Business Strategy — Darden", "https://www.coursera.org/learn/uva-darden-foundations-business-strategy", "course"),
            ("Good Strategy Bad Strategy — Rumelt", "https://www.penguinrandomhouse.com/books/208626/good-strategy-bad-strategy-by-richard-rumelt/", "book"),
            ("McKinsey Insights", "https://www.mckinsey.com/insights", "article"),
        ]),
        ("Market and Competitive Intelligence", "industry sizing, competitor profiling, market entry, and primary research", ["Total addressable market (TAM) sizing", "Competitor profiling and benchmarking", "Market entry strategy assessment", "Primary research design", "Competitive intelligence sources"], [
            ("Statista Market Research", "https://www.statista.com/", "documentation"),
            ("Gartner Research", "https://www.gartner.com/en/research", "article"),
            ("Forrester Research", "https://www.forrester.com/", "article"),
            ("Think with Google Market Finder", "https://marketfinder.thinkwithgoogle.com/", "documentation"),
        ]),
        ("Financial Analysis for Strategy", "P&L interpretation, scenario modelling, ROI analysis, and business cases", ["P&L and cash flow for strategists", "Return on investment (ROI) analysis", "Scenario and sensitivity modelling", "Business case financial section", "Capital allocation decisions"], [
            ("Damodaran Corporate Finance", "https://pages.stern.nyu.edu/~adamodar/", "course"),
            ("HBR Finance for Strategists", "https://hbr.org/topic/subject/finance", "article"),
            ("CFI Strategy Finance", "https://corporatefinanceinstitute.com/resources/", "course"),
            ("SEC EDGAR Annual Reports", "https://www.sec.gov/edgar/search-and-access", "documentation"),
        ]),
        ("Strategy Development and Execution", "vision-to-execution, scenario planning, strategic options, and OKRs", ["Strategic vision and purpose", "Scenario planning methodology", "Strategic options evaluation", "OKRs and execution cadence", "Strategy communication (town halls, memos)"], [
            ("Playing to Win — Lafley and Martin", "https://www.hbs.edu/faculty/Pages/item.aspx?num=46132", "book"),
            ("OKR Framework — Google re:Work", "https://rework.withgoogle.com/guides/set-goals-with-okrs/steps/introduction/", "documentation"),
            ("BCG Perspectives", "https://www.bcg.com/publications", "article"),
            ("Strategy Tools — Strategyzer", "https://www.strategyzer.com/", "article"),
        ]),
        ("Innovation and Business Models", "business model canvas, disruption theory, lean startup, and pivot decisions", ["Business model canvas design", "Jobs-to-be-done for innovation", "Disruptive innovation theory (Christensen)", "Lean startup hypothesis testing", "Pivot vs persevere decisions"], [
            ("Business Model Generation — Osterwalder", "https://www.strategyzer.com/books/business-model-generation", "book"),
            ("The Innovator's Dilemma — Christensen", "https://www.hbs.edu/faculty/Pages/item.aspx?num=46", "book"),
            ("Lean Startup — Ries", "https://theleanstartup.com/", "book"),
            ("IDEO Innovation Resources", "https://www.ideo.com/post/design-thinking", "article"),
        ]),
        ("Strategy Communication and Career", "executive presentations, consulting case interviews, and MBA pathway", ["Executive memo and presentation structure", "Pyramid principle communication", "McKinsey-style case interview prep", "Consulting vs in-house strategy roles", "MBA application and strategy career"], [
            ("McKinsey Case Interview Prep", "https://www.mckinsey.com/careers/interviewing/case-interview-prep", "article"),
            ("Bain Case Interviews", "https://www.bain.com/careers/interview-prep/", "article"),
            ("Case In Point — Marc Cosentino", "https://www.consultingcase101.com/", "book"),
            ("HBS Online CORe", "https://online.hbs.edu/courses/core/", "course"),
        ]),
    ],
}


GENERIC_SEEDS: List[ModuleSeed] = [
    ("Career Basics and Daily Work", "what this career does every day, who it helps, and what good work looks like", ["Daily responsibilities", "People served by the role", "Common beginner tasks", "Examples of good work", "Ethical and responsible behavior"], [
        ("MIT OpenCourseWare", "https://ocw.mit.edu/", "course"),
        ("Coursera", "https://www.coursera.org/", "course"),
        ("OpenLearn", "https://www.open.edu/openlearn/", "course"),
    ]),
    ("Beginner Tools and First Practice", "the first tools to try, how to practice safely, and how to record progress", ["Choosing a beginner tool", "Setting up a simple workspace", "Following one guided example", "Saving notes and screenshots", "Checking your first result"], [
        ("edX", "https://www.edx.org/", "course"),
        ("LinkedIn Learning", "https://www.linkedin.com/learning/", "course"),
        ("O'Reilly Learning", "https://www.oreilly.com/online-learning/", "book"),
    ]),
    ("Problem Solving With Evidence", "how to define a small problem, gather simple evidence, compare options, and choose a next step", ["Writing the problem in one sentence", "Collecting simple evidence", "Comparing two possible solutions", "Choosing the lower-risk next step", "Explaining the decision clearly"], [
        ("Harvard Business Review", "https://hbr.org/", "article"),
        ("Khan Academy", "https://www.khanacademy.org/", "course"),
        ("MIT OpenCourseWare", "https://ocw.mit.edu/", "course"),
    ]),
    ("Working With People and Feedback", "how to understand a request, communicate progress, receive feedback, and improve the work", ["Understanding a task brief", "Asking clarifying questions", "Sharing progress updates", "Using feedback to improve", "Finishing with a clear handoff"], [
        ("Coursera Professional Certificates", "https://www.coursera.org/professional-certificates", "course"),
        ("Project Management Institute", "https://www.pmi.org/learning", "community"),
        ("TED Talks", "https://www.ted.com/talks", "video"),
    ]),
    ("Small Portfolio Project", "a small end-to-end project that proves you can apply the basics and explain your choices", ["Choosing one realistic project idea", "Defining the expected result", "Building the first version", "Measuring what worked", "Writing a simple case study"], [
        ("GitHub", "https://github.com/", "community"),
        ("Notion Templates", "https://www.notion.so/templates", "documentation"),
        ("Canva Design School", "https://www.canva.com/designschool/", "course"),
    ]),
    ("Career Launch Preparation", "how to choose a focus, present your portfolio, practice interviews, and find first opportunities", ["Choosing a focused direction", "Improving the portfolio story", "Practicing common interview questions", "Finding beginner-friendly opportunities", "Planning the next 30 days"], [
        ("LinkedIn Jobs Guide", "https://www.linkedin.com/help/linkedin/topic/a507663", "article"),
        ("Coursera Career Academy", "https://www.coursera.org/career-academy", "course"),
        ("edX Career Resources", "https://www.edx.org/resources", "article"),
    ]),
]


LOCALIZED_GENERIC_SEEDS: Dict[str, List[ModuleSeed]] = {
    "en": GENERIC_SEEDS,
    "uz": [
        ("Kasb Asoslari va Kundalik Ish", "bu kasbda har kuni nima qilinishi, kimlarga yordam berilishi va yaxshi ish qanday ko'rinishi", ["Kundalik vazifalar", "Bu kasb kimlarga yordam beradi", "Yangi boshlovchi uchun oddiy topshiriqlar", "Yaxshi ish namunalarini tushunish", "Mas'uliyatli va halol ishlash"], [
            ("MIT OpenCourseWare", "https://ocw.mit.edu/", "course"),
            ("Coursera", "https://www.coursera.org/", "course"),
            ("OpenLearn", "https://www.open.edu/openlearn/", "course"),
        ]),
        ("Boshlang'ich Vositalar va Birinchi Amaliyot", "birinchi sinab ko'riladigan vositalar, xavfsiz mashq qilish va progressni yozib borish", ["Boshlang'ich vositani tanlash", "Oddiy ish joyini tayyorlash", "Bitta yo'riqli misolni bajarish", "Eslatma va skrinshotlarni saqlash", "Birinchi natijani tekshirish"], [
            ("edX", "https://www.edx.org/", "course"),
            ("LinkedIn Learning", "https://www.linkedin.com/learning/", "course"),
            ("O'Reilly Learning", "https://www.oreilly.com/online-learning/", "book"),
        ]),
        ("Dalil Bilan Muammo Yechish", "kichik muammoni aniqlash, oddiy dalil yig'ish, variantlarni solishtirish va keyingi qadamni tanlash", ["Muammoni bir gapda yozish", "Oddiy dalil yig'ish", "Ikki yechimni solishtirish", "Kamroq xavfli keyingi qadamni tanlash", "Qarorni aniq tushuntirish"], [
            ("Harvard Business Review", "https://hbr.org/", "article"),
            ("Khan Academy", "https://www.khanacademy.org/", "course"),
            ("MIT OpenCourseWare", "https://ocw.mit.edu/", "course"),
        ]),
        ("Odamlar va Fikr-mulohaza Bilan Ishlash", "topshiriqni tushunish, progressni aytish, feedback olish va ishni yaxshilash", ["Topshiriq mazmunini tushunish", "Aniqlashtiruvchi savollar berish", "Progress haqida qisqa xabar berish", "Feedback asosida yaxshilash", "Ishni aniq topshirish"], [
            ("Coursera Professional Certificates", "https://www.coursera.org/professional-certificates", "course"),
            ("Project Management Institute", "https://www.pmi.org/learning", "community"),
            ("TED Talks", "https://www.ted.com/talks", "video"),
        ]),
        ("Kichik Portfolio Loyihasi", "asoslarni qo'llay olishingizni va qarorlaringizni tushuntira olishingizni ko'rsatadigan kichik loyiha", ["Realistik loyiha g'oyasini tanlash", "Kutilgan natijani belgilash", "Birinchi versiyani yaratish", "Nima ishlaganini o'lchash", "Oddiy case study yozish"], [
            ("GitHub", "https://github.com/", "community"),
            ("Notion Templates", "https://www.notion.so/templates", "documentation"),
            ("Canva Design School", "https://www.canva.com/designschool/", "course"),
        ]),
        ("Karyeraga Kirishga Tayyorgarlik", "yo'nalish tanlash, portfolio taqdim etish, suhbatga tayyorlanish va birinchi imkoniyatlarni topish", ["Aniq yo'nalish tanlash", "Portfolio hikoyasini yaxshilash", "Oddiy suhbat savollariga tayyorlanish", "Boshlovchilar uchun imkoniyatlarni topish", "Keyingi 30 kunlik rejani tuzish"], [
            ("LinkedIn Jobs Guide", "https://www.linkedin.com/help/linkedin/topic/a507663", "article"),
            ("Coursera Career Academy", "https://www.coursera.org/career-academy", "course"),
            ("edX Career Resources", "https://www.edx.org/resources", "article"),
        ]),
    ],
    "ru": [
        ("Основы Профессии и Ежедневная Работа", "что специалист делает каждый день, кому помогает и как выглядит качественная работа", ["Ежедневные задачи", "Кому помогает роль", "Простые задачи для новичка", "Примеры хорошей работы", "Ответственное и честное поведение"], [
            ("MIT OpenCourseWare", "https://ocw.mit.edu/", "course"),
            ("Coursera", "https://www.coursera.org/", "course"),
            ("OpenLearn", "https://www.open.edu/openlearn/", "course"),
        ]),
        ("Инструменты Новичка и Первая Практика", "первые инструменты, безопасная практика и фиксация прогресса", ["Выбор первого инструмента", "Настройка простого рабочего места", "Один пример по инструкции", "Заметки и скриншоты", "Проверка первого результата"], [
            ("edX", "https://www.edx.org/", "course"),
            ("LinkedIn Learning", "https://www.linkedin.com/learning/", "course"),
            ("O'Reilly Learning", "https://www.oreilly.com/online-learning/", "book"),
        ]),
        ("Решение Задач Через Факты", "как определить маленькую проблему, собрать простые факты, сравнить варианты и выбрать следующий шаг", ["Записать проблему одним предложением", "Собрать простые факты", "Сравнить два решения", "Выбрать менее рискованный шаг", "Объяснить решение понятно"], [
            ("Harvard Business Review", "https://hbr.org/", "article"),
            ("Khan Academy", "https://www.khanacademy.org/", "course"),
            ("MIT OpenCourseWare", "https://ocw.mit.edu/", "course"),
        ]),
        ("Работа С Людьми и Обратной Связью", "как понять задачу, сообщать о прогрессе, принимать feedback и улучшать работу", ["Понять задачу", "Задать уточняющие вопросы", "Коротко сообщить о прогрессе", "Улучшить работу по feedback", "Передать результат понятно"], [
            ("Coursera Professional Certificates", "https://www.coursera.org/professional-certificates", "course"),
            ("Project Management Institute", "https://www.pmi.org/learning", "community"),
            ("TED Talks", "https://www.ted.com/talks", "video"),
        ]),
        ("Маленький Проект Для Портфолио", "небольшой проект, который показывает применение основ и объяснение решений", ["Выбрать реалистичную идею", "Определить ожидаемый результат", "Сделать первую версию", "Измерить, что сработало", "Написать простой case study"], [
            ("GitHub", "https://github.com/", "community"),
            ("Notion Templates", "https://www.notion.so/templates", "documentation"),
            ("Canva Design School", "https://www.canva.com/designschool/", "course"),
        ]),
        ("Подготовка К Старту Карьеры", "выбор фокуса, презентация портфолио, практика интервью и поиск первых возможностей", ["Выбрать фокус", "Улучшить историю портфолио", "Практиковать вопросы интервью", "Найти возможности для новичков", "Составить план на 30 дней"], [
            ("LinkedIn Jobs Guide", "https://www.linkedin.com/help/linkedin/topic/a507663", "article"),
            ("Coursera Career Academy", "https://www.coursera.org/career-academy", "course"),
            ("edX Career Resources", "https://www.edx.org/resources", "article"),
        ]),
    ],
}


def _career_domain(career_name: str) -> str:
    """Backward-compatible broad catalog resolver."""
    return _catalog_resolver.resolve_broad(career_name)


def _find_catalog_key(career_name: str) -> str:
    """Map a localized career name to a curriculum catalog key."""
    return _catalog_resolver.resolve(career_name)


def _slug(value: str, index: int) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or f"module-{index}"


PYTHON_QUIZZES = {
    "uz": [
        (
            "`name = \"Ali\"` kodida `name` nima?",
            ["Funksiya", "O'zgaruvchi", "Shart operatori", "Modul"],
            "b",
            "O'zgaruvchi qiymatni nom bilan saqlaydi. Bu yerda `name` matn qiymatini saqlamoqda.",
        ),
        (
            "`range(3)` bilan ishlaydigan `for` sikli qaysi sonlarni oladi?",
            ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "Faqat 3"],
            "b",
            "`range(3)` boshlang'ich qiymat berilmasa 0 dan boshlanadi va 3 ni o'z ichiga olmaydi.",
        ),
        (
            "Funksiyadan hisoblangan natijani tashqariga qaytarish uchun qaysi kalit so'z ishlatiladi?",
            ["print", "return", "import", "break"],
            "b",
            "`return` natijani chaqiruvchi kodga beradi; `print` esa faqat ekranga chiqaradi.",
        ),
        (
            "`numbers = [2, 4, 6]` ro'yxatining birinchi elementini qanday olasiz?",
            ["numbers[1]", "numbers.first()", "numbers[0]", "numbers[-0]"],
            "c",
            "Python indekslari 0 dan boshlanadi, shuning uchun birinchi element `numbers[0]` bo'ladi.",
        ),
        (
            "Dastur `NameError` bersa, birinchi navbatda nimani tekshirish kerak?",
            ["O'zgaruvchi nomi to'g'ri yozilgan va oldin yaratilganini", "Internet ulanishini", "Kompyuter xotirasini", "Python rang mavzusini"],
            "a",
            "`NameError` odatda nom xato yozilganda yoki o'zgaruvchi ishlatilishidan oldin yaratilmaganda chiqadi.",
        ),
    ],
    "ru": [
        (
            "Что такое `name` в коде `name = \"Ali\"`?",
            ["Функция", "Переменная", "Условие", "Модуль"],
            "b",
            "Переменная хранит значение под именем. Здесь `name` хранит строку.",
        ),
        (
            "Какие числа перебирает цикл `for` с `range(3)`?",
            ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "Только 3"],
            "b",
            "`range(3)` начинается с 0 и не включает конечное значение 3.",
        ),
        (
            "Какое слово возвращает вычисленный результат из функции?",
            ["print", "return", "import", "break"],
            "b",
            "`return` передает результат вызывающему коду, а `print` только выводит его.",
        ),
        (
            "Как получить первый элемент списка `numbers = [2, 4, 6]`?",
            ["numbers[1]", "numbers.first()", "numbers[0]", "numbers[-0]"],
            "c",
            "Индексы Python начинаются с 0, поэтому первый элемент доступен как `numbers[0]`.",
        ),
        (
            "Что проверить первым при ошибке `NameError`?",
            ["Правильность имени и его объявление", "Интернет", "Объем памяти", "Цветовую тему редактора"],
            "a",
            "`NameError` обычно означает опечатку в имени или использование переменной до ее создания.",
        ),
    ],
    "en": [
        (
            "What is `name` in `name = \"Ali\"`?",
            ["A function", "A variable", "A condition", "A module"],
            "b",
            "A variable stores a value under a name. Here `name` stores a string.",
        ),
        (
            "Which numbers does a `for` loop using `range(3)` receive?",
            ["1, 2, 3", "0, 1, 2", "0, 1, 2, 3", "Only 3"],
            "b",
            "`range(3)` starts at 0 and excludes its stop value, 3.",
        ),
        (
            "Which keyword sends a computed value back from a function?",
            ["print", "return", "import", "break"],
            "b",
            "`return` gives the result to the calling code; `print` only displays it.",
        ),
        (
            "How do you access the first item in `numbers = [2, 4, 6]`?",
            ["numbers[1]", "numbers.first()", "numbers[0]", "numbers[-0]"],
            "c",
            "Python indexes start at 0, so the first item is `numbers[0]`.",
        ),
        (
            "What should you check first after a `NameError`?",
            ["Whether the name is spelled correctly and already defined", "The internet connection", "Available memory", "The editor color theme"],
            "a",
            "`NameError` usually means a misspelled name or a variable used before it was defined.",
        ),
    ],
}


def _quiz(
    module_id: str,
    topic: str,
    lessons: List[str],
    language: str,
) -> List[ModuleQuizQuestion]:
    if module_id == "python-foundations":
        return [
            ModuleQuizQuestion(
                id=f"{module_id}-q{index}",
                question=question,
                options=[
                    QuizOption(id=option_id, text=text)
                    for option_id, text in zip(["a", "b", "c", "d"], options)
                ],
                correct_option_id=correct,
                explanation=explanation,
            )
            for index, (question, options, correct, explanation) in enumerate(
                PYTHON_QUIZZES[language],
                1,
            )
        ]

    correct_ids = ["a", "c", "b", "d", "a"]
    action_sets = {
        "uz": [
            {
                "question": "“{lesson}”ni o'rganayotganda birinchi foydali amaliy qadam qaysi?",
                "correct": "Mavzuni o'z so'zingiz bilan tushuntirib, kichik real misolda sinab ko'rish.",
                "wrong": [
                    "Avval faqat ta'rifni yozib, amaliy misolni keyinga qoldirish.",
                    "Bitta misolni ko'rib, uni o'zingiz qayta tushuntirib bermaslik.",
                    "Natijani yozmasdan keyingi kichik vazifaga o'tish.",
                ],
                "explanation": "Birinchi qadam tushuncha va amaliy misolni bog'lashdir; shunda mavzu yodlangan emas, ishlatiladigan ko'nikmaga aylanadi.",
            },
            {
                "question": "“{lesson}”ni “{related}” bilan bog'lab o'rganishdan maqsad nima?",
                "correct": "Ular bir ish jarayonida qayerda qo'llanishini ajratib olish.",
                "wrong": [
                    "Ikkala mavzuni qayerda farqlanishini yozmasdan yonma-yon qo'yish.",
                    "Faqat ta'riflarni yozib, ish jarayonidagi o'rnini ko'rsatmaslik.",
                    "Mavzular ro'yxatini tuzib, kichik misolda sinab ko'rmaslik.",
                ],
                "explanation": "Bog'lashning maqsadi mavzularni chalkashtirish emas, qaysi vaziyatda qaysi biri kerakligini tushunishdir.",
            },
            {
                "question": "“{lesson}” bo'yicha loyiha bajarganda natijani qanday tekshirish kerak?",
                "correct": "Oldindan kutilgan natijani yozib, ish yakunida real natija bilan solishtirish.",
                "wrong": [
                    "Faqat tashqi ko'rinishga qarab, kutilgan natijani solishtirmaslik.",
                    "Tekshiruv mezonini loyiha tugagandan keyin o'ylab ko'rish.",
                    "Faqat yakuniy natijani yozib, nimani tuzatganingizni ko'rsatmaslik.",
                ],
                "explanation": "Sifatli loyiha kutilgan natija, real natija va xatolardan chiqarilgan xulosa bilan tekshiriladi.",
            },
            {
                "question": "“{lesson}”ni portfolio ishida ko'rsatishning eng yaxshi yo'li qaysi?",
                "correct": "Muammo, bajargan qadamlar, qaror sababi va natijani qisqa yozib berish.",
                "wrong": [
                    "Faqat final natijani qo'yib, qaror sabablarini yozmaslik.",
                    "Jarayondagi o'zgarishlarni yozmasdan faqat oxirgi versiyani ko'rsatish.",
                    "Mavzuni misolsiz tushuntirib, natijaga qanday ta'sir qilganini ko'rsatmaslik.",
                ],
                "explanation": "Portfolio ishida faqat natija emas, fikrlash jarayoni va qarorlar ham ko'rinishi kerak.",
            },
            {
                "question": "Modul yakunida “{lesson}” bo'yicha tayyorlikni qanday bilasiz?",
                "correct": "Mavzuni yangi kichik vazifada mustaqil qo'llab, natijani tushuntira olsangiz.",
                "wrong": [
                    "Mavzu nomini bilish bilan cheklanib, yangi vazifada sinab ko'rmaslik.",
                    "Bitta materialni ko'rib, o'zingiz kichik natija yaratmaslik.",
                    "Tayyor namunani qaytarib, o'z qaroringizni izohlamaslik.",
                ],
                "explanation": "Tayyorlik mustaqil qo'llash va natijani tushuntirish orqali bilinadi.",
            },
        ],
        "ru": [
            {
                "question": "Какой первый полезный практический шаг при изучении темы «{lesson}»?",
                "correct": "Объяснить тему своими словами и проверить ее на маленьком реальном примере.",
                "wrong": [
                    "Сначала записать только определение и отложить практический пример.",
                    "Посмотреть один пример, но не объяснить его своими словами.",
                    "Перейти к следующей маленькой задаче, не записав результат.",
                ],
                "explanation": "Первый шаг - связать понятие с практическим примером, чтобы тема стала навыком, а не только запомненным термином.",
            },
            {
                "question": "Зачем связывать «{lesson}» с темой «{related}»?",
                "correct": "Понять, где каждая тема применяется в одном рабочем процессе.",
                "wrong": [
                    "Поставить темы рядом, но не записать, чем они отличаются.",
                    "Записать определения, но не показать их место в рабочем процессе.",
                    "Составить список тем, но не проверить его на маленьком примере.",
                ],
                "explanation": "Связь нужна не для смешивания тем, а чтобы понять, какая тема нужна в конкретной ситуации.",
            },
            {
                "question": "Как проверить результат проекта по теме «{lesson}»?",
                "correct": "Заранее записать ожидаемый результат и сравнить его с реальным итогом.",
                "wrong": [
                    "Оценить только внешний вид и не сравнить с ожидаемым результатом.",
                    "Придумать критерии проверки только после завершения проекта.",
                    "Показать только итог и не объяснить, что было исправлено.",
                ],
                "explanation": "Качественный проект проверяется через ожидаемый результат, реальный итог и выводы из ошибок.",
            },
            {
                "question": "Как лучше показать «{lesson}» в портфолио?",
                "correct": "Коротко описать проблему, шаги, причину решений и результат.",
                "wrong": [
                    "Показать только финальный результат без причин решений.",
                    "Показать только последнюю версию без изменений в процессе.",
                    "Объяснить тему без примера и без связи с результатом.",
                ],
                "explanation": "В портфолио должен быть виден не только результат, но и ход мышления.",
            },
            {
                "question": "Как понять, что вы готовы по теме «{lesson}» в конце модуля?",
                "correct": "Вы можете самостоятельно применить тему в новой маленькой задаче и объяснить результат.",
                "wrong": [
                    "Ограничиться названием темы и не применить ее в новой задаче.",
                    "Посмотреть один материал, но не создать маленький результат.",
                    "Повторить готовый пример без объяснения своих решений.",
                ],
                "explanation": "Готовность видна через самостоятельное применение и объяснение результата.",
            },
        ],
        "en": [
            {
                "question": "What is the first useful practical step when learning “{lesson}”?",
                "correct": "Explain it in your own words and test it on a small real example.",
                "wrong": [
                    "Write only the definition first and postpone a practical example.",
                    "Look at one example but not explain it in your own words.",
                    "Move to the next small task without writing down the result.",
                ],
                "explanation": "The first step is connecting the idea to a practical example so it becomes a usable skill, not just a memorized term.",
            },
            {
                "question": "Why should you connect “{lesson}” with “{related}”?",
                "correct": "To understand where each topic is used in one working process.",
                "wrong": [
                    "Put the topics side by side without writing how they differ.",
                    "Write definitions without showing where they fit in the workflow.",
                    "Make a topic list without testing it on a small example.",
                ],
                "explanation": "Connecting topics should clarify when each one is needed, not blur them together.",
            },
            {
                "question": "How should you check a project result for “{lesson}”?",
                "correct": "Write the expected result first, then compare it with the actual outcome.",
                "wrong": [
                    "Judge only the appearance without comparing it to the expected result.",
                    "Create quality checks only after the project is already finished.",
                    "Show only the final result without explaining what changed.",
                ],
                "explanation": "A quality project is checked through expected outcome, actual outcome, and what you learned from mistakes.",
            },
            {
                "question": "What is the best way to show “{lesson}” in a portfolio?",
                "correct": "Briefly explain the problem, steps, decision reasons, and result.",
                "wrong": [
                    "Show only the final result without decision reasons.",
                    "Show only the last version without process changes.",
                    "Explain the topic without an example or link to the result.",
                ],
                "explanation": "A portfolio should show not only the result, but also your thinking process.",
            },
            {
                "question": "How do you know you are ready with “{lesson}” at the end of the module?",
                "correct": "You can apply it independently to a new small task and explain the result.",
                "wrong": [
                    "Stop at knowing the topic name without using it in a new task.",
                    "Watch one resource without creating a small result.",
                    "Repeat a ready-made example without explaining your decisions.",
                ],
                "explanation": "Readiness means independent application and a clear explanation of the result.",
            },
        ],
    }[language]
    questions = []
    for index, lesson in enumerate(lessons[:5], 1):
        correct_id = correct_ids[index - 1]
        related = lessons[index % len(lessons)] if lessons else topic
        spec = action_sets[index - 1]
        wrong_values = iter(spec["wrong"])
        options = []
        for option_id in ["a", "b", "c", "d"]:
            text = spec["correct"] if option_id == correct_id else next(wrong_values)
            options.append(QuizOption(
                id=option_id,
                text=text.format(topic=topic, lesson=lesson, related=related),
            ))
        questions.append(ModuleQuizQuestion(
            id=f"{module_id}-q{index}",
            question=spec["question"].format(topic=topic, lesson=lesson, related=related),
            options=options,
            correct_option_id=correct_id,
            explanation=spec["explanation"].format(topic=topic, lesson=lesson, related=related),
        ))
    return questions


_OBJECTIVE_SUFFIXES: Dict[str, List[str]] = {
    "en": ["— understand and apply in practice", "— work with independently", "— use in a small project"],
    "uz": "— ni tushunish va amalda qo'llash|— bilan mustaqil ishlash|— asosida kichik loyiha yaratish".split("|"),
    "ru": ["— понять и применить на практике", "— уверенно использовать в работе", "— применить в маленьком проекте"],
}


def _module_objectives(lessons: List[str], language: str) -> List[str]:
    """Derive up to 3 module-specific objectives from its lesson list."""
    if not lessons:
        return COMMON[language]["objectives"]
    picks = (lessons * 3)[:3]
    suffixes = _OBJECTIVE_SUFFIXES[language]
    return [f"{pick} {suffix}" for pick, suffix in zip(picks, suffixes)]


def build_fallback_learning_path(request: LearningPathRequest) -> LearningPathResponse:
    """Build a detailed, usable curriculum without an external AI call."""
    return _get_path_builder().build(request)


@lru_cache(maxsize=1)
def _get_path_builder() -> LearningPathBuilder:
    """Create the process-wide immutable learning path builder."""
    return LearningPathBuilder(
        resolver=_catalog_resolver,
        common=COMMON,
        broad_catalogs=CATALOGS,
        specialized_catalogs=SUB_CATALOGS,
        generic_catalogs=LOCALIZED_GENERIC_SEEDS,
        quiz_factory=_quiz,
    )


def _context_lessons(module_context: str) -> List[str]:
    """Extract individual lesson topics from the module context string.

    Handles the frontend format:
        {description}
        Objectives: ...
        Lessons: topic1; topic2; topic3; ...
        Project: ...
    """
    return list(_tutor_context.lessons(module_context))


def _pick_lesson(lessons: List[str], text: str) -> str:
    return _tutor_context.pick_lesson(lessons, text)


def build_streaming_suggestions(module_context: str, module_title: str, language: str) -> List[str]:
    """Generate contextual follow-up suggestions from module context without an AI call."""
    return _tutor_context.suggestions(module_context, module_title, language)


def build_fallback_chat(request: ModuleChatRequest) -> ModuleChatResponse:
    """Return contextual module guidance when no external AI call is available."""
    language = request.language
    question = request.messages[-1].content.strip()
    normalized = question.lower()
    lessons = _context_lessons(request.module_context)
    focus = _pick_lesson(lessons, question)
    second = lessons[1] if len(lessons) > 1 else focus
    third = lessons[2] if len(lessons) > 2 else second

    asks_for_quiz = any(word in normalized for word in ["test", "quiz", "тест", "sinov", "tekshir"])
    asks_for_exercise = any(word in normalized for word in ["mashq", "exercise", "упражнен", "задач", "practice"])
    asks_for_code = any(word in normalized for word in ["code", "kod", "код", "javascript", "sql", "script"])
    asks_about_function = any(word in normalized for word in ["function", "funksi", "функц"])

    if asks_about_function:
        answers = {
            "uz": (
                "Funksiya - bir vazifani bajaradigan, qayta ishlatish mumkin bo'lgan kod bo'lagi.\n\n"
                "Oddiy misol: salomlashish matnini har safar boshqatdan yozmaslik uchun uni funksiya qilamiz.\n\n"
                "```python\n"
                "def greet(name):\n"
                "    return f\"Salom, {name}!\"\n\n"
                "print(greet(\"Ali\"))\n"
                "```\n\n"
                "`name` - kiruvchi qiymat, `return` - natijani qaytaradi. Ko'p uchraydigan xato: `print()` natijani ekranga chiqaradi, "
                "`return` esa natijani keyingi kod ishlatishi uchun qaytaradi.\n\n"
                "Tekshiruv savoli: agar `greet(\"Malika\")` chaqirilsa, funksiya qanday matn qaytaradi?"
            ),
            "ru": (
                "Функция - это часть кода, которая выполняет одну задачу и может использоваться повторно.\n\n"
                "Простой пример: чтобы не писать приветствие каждый раз заново, мы делаем функцию.\n\n"
                "```python\n"
                "def greet(name):\n"
                "    return f\"Привет, {name}!\"\n\n"
                "print(greet(\"Ali\"))\n"
                "```\n\n"
                "`name` - входное значение, `return` возвращает результат. Частая ошибка: `print()` только выводит на экран, "
                "а `return` передает результат дальше в код.\n\n"
                "Проверочный вопрос: какой текст вернет `greet(\"Malika\")`?"
            ),
            "en": (
                "A function is a reusable piece of code that performs one task.\n\n"
                "Simple example: instead of writing a greeting again and again, we put it in a function.\n\n"
                "```python\n"
                "def greet(name):\n"
                "    return f\"Hello, {name}!\"\n\n"
                "print(greet(\"Ali\"))\n"
                "```\n\n"
                "`name` is the input value, and `return` sends the result back. Common mistake: `print()` only displays text, "
                "while `return` gives the result to the next part of the code.\n\n"
                "Check question: what text does `greet(\"Malika\")` return?"
            ),
        }
    elif asks_for_quiz:
        answers = {
            "uz": (
                f"Mini test: javoblarni hozircha ko'rsatmayman.\n\n"
                f"1. “{focus}” mavzusida eng muhim qaror nimani aniqlaydi?\n"
                f"2. “{second}” bo'yicha amaliy ishda qaysi xatoni birinchi tekshirish kerak?\n"
                f"3. “{third}” natijasini sifatli deb bilish uchun qanday dalil kerak?\n\n"
                "Javoblaringizni 1-3 ko'rinishida yuboring. Keyin har birini qisqa izoh bilan tekshiraman."
            ),
            "ru": (
                f"Мини-тест: ответы пока не раскрываю.\n\n"
                f"1. Какое главное решение нужно принять в теме «{focus}»?\n"
                f"2. Какую ошибку стоит проверить первой в практической работе по «{second}»?\n"
                f"3. Какое доказательство покажет, что результат по «{third}» качественный?\n\n"
                "Отправьте ответы в формате 1-3, затем я проверю каждый с коротким объяснением."
            ),
            "en": (
                f"Mini quiz: I will keep the answers hidden for now.\n\n"
                f"1. What is the most important decision in “{focus}”?\n"
                f"2. In practical work on “{second}”, which mistake should you check first?\n"
                f"3. What evidence would prove that the result for “{third}” is good quality?\n\n"
                "Send answers as 1-3 and I will check each one with a short explanation."
            ),
        }
    elif asks_for_exercise:
        answers = {
            "uz": (
                f"Mashq: “{focus}”ni amalda tushunish.\n\n"
                f"Misol vaziyat: siz {request.career_name} bo'yicha yangi boshlovchisiz va kichik vazifani tushunarli qilib bajarishingiz kerak.\n\n"
                f"1. “{focus}”ni 2-3 gapda o'z so'zingiz bilan yozing.\n"
                f"2. “{second}” bilan bog'lab bitta oddiy misol tuzing.\n"
                f"3. “{third}” asosida natija yaxshi chiqqanini tekshiradigan 2 ta mezon yozing.\n"
                "4. Yakunda 5-6 qatordan iborat qisqa xulosa yozing: nima qildingiz, nima o'rgandingiz, keyingi qadam nima.\n\n"
                "Topshiriladigan natija: ta'rif, misol, 2 ta tekshiruv mezoni, qisqa xulosa.\n\n"
                "Mini-test:\n"
                f"1. “{focus}” qaysi muammoni tushunishga yordam beradi?\n"
                f"2. “{second}” bilan bog'lash nimani aniqlashtiradi?\n"
                f"3. “{third}” bo'yicha natijani tekshirish uchun qanday dalil kerak?"
            ),
            "ru": (
                f"Упражнение: понять «{focus}» на практике.\n\n"
                f"Ситуация: вы начинающий специалист в направлении {request.career_name} и должны выполнить маленькую задачу понятно и аккуратно.\n\n"
                f"1. Объясните «{focus}» своими словами в 2-3 предложениях.\n"
                f"2. Свяжите это с «{second}» и придумайте один простой пример.\n"
                f"3. На основе «{third}» напишите 2 критерия, по которым можно проверить результат.\n"
                "4. В конце напишите короткий вывод на 5-6 строк: что сделали, что поняли, какой следующий шаг.\n\n"
                "Что прислать: объяснение, пример, 2 критерия проверки, короткий вывод.\n\n"
                "Мини-тест:\n"
                f"1. Какую проблему помогает понять «{focus}»?\n"
                f"2. Что уточняет связь с темой «{second}»?\n"
                f"3. Какое доказательство нужно для проверки результата по «{third}»?"
            ),
            "en": (
                f"Exercise: understand “{focus}” through practice.\n\n"
                f"Scenario: you are a beginner in {request.career_name} and need to complete one small task clearly.\n\n"
                f"1. Explain “{focus}” in your own words in 2-3 sentences.\n"
                f"2. Connect it with “{second}” and create one simple example.\n"
                f"3. Using “{third}”, write 2 checks that prove the result is good.\n"
                "4. Finish with a 5-6 line reflection: what you did, what you learned, and the next step.\n\n"
                "Submit: explanation, example, 2 quality checks, short reflection.\n\n"
                "Mini-test:\n"
                f"1. What problem does “{focus}” help you understand?\n"
                f"2. What does connecting it with “{second}” clarify?\n"
                f"3. What evidence would verify the result for “{third}”?"
            ),
        }
    elif asks_for_code:
        answers = {
            "uz": (
                f"“{focus}”ni kod orqali o'rganayotganda avval input, qoida va outputni ajrating.\n\n"
                "```python\n"
                "def check_result(input_value, rule):\n"
                "    result = rule(input_value)\n"
                "    return {\"input\": input_value, \"result\": result, \"valid\": result is not None}\n"
                "```\n\n"
                f"Bu skelet {request.module_title} modulida foydali: inputni yashirmaydi, natijani alohida saqlaydi, "
                "va tekshiruvni ko'rinadigan qiladi. Kodingizni yuborsangiz, uni aynan modul maqsadiga moslab tuzataman."
            ),
            "ru": (
                f"Когда изучаете «{focus}» через код, сначала разделите input, правило и output.\n\n"
                "```python\n"
                "def check_result(input_value, rule):\n"
                "    result = rule(input_value)\n"
                "    return {\"input\": input_value, \"result\": result, \"valid\": result is not None}\n"
                "```\n\n"
                f"Этот каркас полезен в модуле «{request.module_title}»: input остается видимым, результат хранится отдельно, "
                "а проверка становится явной. Пришлите код, и я адаптирую его под цель модуля."
            ),
            "en": (
                f"When learning “{focus}” through code, separate the input, rule, and output first.\n\n"
                "```python\n"
                "def check_result(input_value, rule):\n"
                "    result = rule(input_value)\n"
                "    return {\"input\": input_value, \"result\": result, \"valid\": result is not None}\n"
                "```\n\n"
                f"This structure fits the {request.module_title} module because it keeps the input visible, stores the result separately, "
                "and makes validation explicit. Send your code and I will adapt it to the module goal."
            ),
        }
    else:
        answers = {
            "uz": (
                f"Qisqa javob: “{focus}” - {request.module_title} modulida amaliy natijaga olib boradigan asosiy bo'laklardan biri.\n\n"
                f"Uni 3 qadamda o'rganing: avval tushunchani o'z so'zingiz bilan ta'riflang, keyin “{second}” bilan bog'lab kichik misol qiling, "
                f"oxirida “{third}” orqali natijani tekshiring. Eng ko'p uchraydigan xato - mavzuni yodlash, lekin qaysi vaziyatda ishlatishni "
                "aniqlamaslik. Hozir bitta real misol yozsangiz, men uni modul maqsadiga moslab tahlil qilaman."
            ),
            "ru": (
                f"Короткий ответ: «{focus}» - одна из ключевых частей модуля «{request.module_title}», которая должна привести к практическому результату.\n\n"
                f"Изучайте это в 3 шага: сначала объясните понятие своими словами, затем свяжите его с «{second}» на маленьком примере, "
                f"после этого проверьте результат через «{third}». Частая ошибка - запомнить термин, но не понять, в какой ситуации он применяется. "
                "Напишите один реальный пример, и я разберу его относительно цели модуля."
            ),
            "en": (
                f"Short answer: “{focus}” is one of the core parts of the {request.module_title} module that should lead to a practical outcome.\n\n"
                f"Study it in 3 steps: define it in your own words, connect it to “{second}” with a small example, then verify the result through “{third}”. "
                "The common mistake is memorizing the term without knowing where to apply it. Share one real example and I will review it against the module goal."
            ),
        }

    suggestions = {
        "uz": [f"“{focus}” uchun misol ber", "Menga amaliy mashq ber", "Javobimni tekshir"],
        "ru": [f"Дай пример по «{focus}»", "Дай практическое упражнение", "Проверь мой ответ"],
        "en": [f"Give an example for “{focus}”", "Give me a practical exercise", "Check my answer"],
    }

    return ModuleChatResponse(
        answer=answers[language],
        suggested_questions=suggestions[language],
    )
