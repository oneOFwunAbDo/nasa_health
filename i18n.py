"""
All user-facing text for the Space Health app, in English and Arabic.
Every screen reads its text from here, so the language switch covers the whole app.
"""

STATIONS = ["ISS", "Moon", "Mars"]

MONTHS = {
    "en": ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
           "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    "ar": ["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
           "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
}

# index 0 = Sunday, matching the heatmap rows
DAY_LABELS = {
    "en": ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    "ar": ["أحد", "اثنين", "ثلاثاء", "أربعاء", "خميس", "جمعة", "سبت"],
}

TEXT = {
    "en": {
        # shared
        "app": "Space Health",
        "toggle": "العربية",
        "back": "Back",
        "continue": "Continue",
        "finish": "Finish",
        "lang_en": "English",
        "lang_ar": "العربية",
        "language": "Language",
        "st_ISS": "International Space Station",
        "st_Moon": "The Moon",
        "st_Mars": "Mars",
        # welcome + login
        "welcome": "Track your health, wherever you are in orbit.",
        "log_in": "Log in",
        "sign_up": "Sign up",
        "look_camera": "Look at the camera to log in",
        "scanning": "Scanning...",
        "matched": "Welcome back, {name}!",
        "no_match": "Face not recognised.",
        "retry": "Try again",
        "use_password": "Use username & password instead",
        "camera_fault": "Camera not available. Use username & password.",
        "username": "Username",
        "password": "Password",
        "wrong_pw": "Wrong username or password.",
        "fill_all": "Please fill in all fields.",
        # sign up
        "first": "First name",
        "last": "Last name",
        "user_taken": "That username is already taken.",
        "short_pw": "Password must be at least 6 characters.",
        "scan_title": "Face scan",
        "scan_hint": "Look at the camera. We'll take 5 snapshots.",
        "scan_progress": "Captured {n} of 5",
        "no_face": "No face detected",
        "many_faces": "More than one face. Only you should be in view.",
        "scan_dup": "This face is already registered.",
        "station_title": "Choose your station",
        "language_title": "Choose your language",
        # homepage
        "home_welcome": "Welcome back, {name}",
        "home_sub": "Keep the streak alive.",
        "tasks_total": "{n} health tasks completed in the last year",
        "streak": "🔥 {n}-day streak",
        "no_tasks": "No tasks yet. Your mission starts today.",
        "orbiting": "Orbiting: {station}",
        "station_line": "Station: {station}",
        "profile": "Profile",
        "crew": "FELLOW ASTRONAUTS",
        "no_crew": "No crew yet",
        "settings": "SETTINGS",
        "current_station": "Current station",
        "reminders": "Daily reminders",
        "animate": "Animate station model",
        "less": "Less",
        "more": "More",
        "topic_Fitness": "Fitness",
        "topic_Hydration": "Hydration",
        "topic_Sleep": "Sleep",
        "topic_Nutrition": "Nutrition",
        "topic_Mindfulness": "Mindfulness",
        "topic_Medication": "Medication",
        "topic_Progress": "Progress",
        # mission day & tasks
        "mission_day": "Mission Day {d}",
        "mission_tasks_title": "Mission Day {d} — Task List",
        "mission_tasks_sub": "Time moves differently in space. Select your mission day to view and complete your protocol.",
        "task_item": "Task {n}",
        "tasks_done_count": "{done} / {total} completed",
        # branding + heatmap tooltip
        "brand": "SPACE HEALTH",
        "mission_control": "MISSION CONTROL // BIOMETRICS",
        "heat_tip": "{date}  •  {n} completed",
        # menu + spaceflight hazards
        "menu_topics": "HEALTH TOPICS",
        "hazards_menu": "SPACEFLIGHT HAZARDS",
        "hazards_title": "5 HAZARDS OF HUMAN SPACEFLIGHT  ·  NASA",
        "hz_risks": "KEY RISKS",
        "hz_counter": "COUNTERMEASURES",
        "hz_link": "HOW YOUR DAILY TASKS HELP",
        "hz_close": "Close",
        # Inside TEXT["en"]
        "nut_select_placeholder": "Select a menu item...",
        "nut_add_item": "+ Add",
        # nutrition page (add inside TEXT["en"])
        "nut_title": "Astronaut Nutrition",
        "nut_sub": "Select consumed menu items for Mission Day {d} (Menu Rotation Day {r}) to track daily micronutrients.",
        "nut_chart_title": "Daily Micronutrient Intake (% of Target)",
        "nut_chart_sub": "All 21 micronutrients normalized against daily target / limit (100% dashed line).",
        "nut_meal_breakfast": "Breakfast",
        "nut_meal_lunch": "Lunch",
        "nut_meal_dinner": "Dinner",
        "nut_meal_snacks": "Snacks",
        "nut_planned_kcal": "Planned menu: {kcal} kcal",
        "nut_missing_warn": "Missing nutrient data in backend for: {items}",
        "nut_demo_notice": "Using demo nutrient file (food_nutrients_DEMO.json).",
        "nut_no_data": "No nutrient data file found. Run make_demo_data.py first.",
        "nut_reset": "Clear Day",
        "nut_status_low": "Low (<70%)",
        "nut_status_near": "Near (70-99%)",
        "nut_status_met": "Met (≥100%)",
        "nut_status_ok": "Sodium OK (≤100%)",
        "nut_status_over": "Over Limit (>100%)",
        "nut_tip": "{name}: {amount:.1f} / {target} {unit} ({pct:.0f}%)",
    },
    "ar": {
        "app": "صحة الفضاء",
        "toggle": "English",
        "back": "رجوع",
        "continue": "متابعة",
        "finish": "إنهاء",
        "lang_en": "English",
        "lang_ar": "العربية",
        "language": "اللغة",
        "st_ISS": "محطة الفضاء الدولية",
        "st_Moon": "القمر",
        "st_Mars": "المريخ",
        "welcome": "تابع صحتك، أينما كنت في المدار.",
        "log_in": "تسجيل الدخول",
        "sign_up": "إنشاء حساب",
        "look_camera": "انظر إلى الكاميرا لتسجيل الدخول",
        "scanning": "جارٍ المسح...",
        "matched": "أهلاً بعودتك، {name}!",
        "no_match": "لم يتم التعرف على الوجه.",
        "retry": "حاول مرة أخرى",
        "use_password": "استخدام اسم المستخدم وكلمة المرور",
        "camera_fault": "الكاميرا غير متاحة. استخدم اسم المستخدم وكلمة المرور.",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "wrong_pw": "اسم المستخدم أو كلمة المرور غير صحيحة.",
        "fill_all": "يرجى ملء جميع الحقول.",
        "first": "الاسم الأول",
        "last": "اسم العائلة",
        "user_taken": "اسم المستخدم مستخدم بالفعل.",
        "short_pw": "يجب أن تتكون كلمة المرور من 6 أحرف على الأقل.",
        "scan_title": "مسح الوجه",
        "scan_hint": "انظر إلى الكاميرا. سنلتقط 5 صور.",
        "scan_progress": "تم التقاط {n} من 5",
        "no_face": "لم يتم اكتشاف وجه",
        "many_faces": "أكثر من وجه. يجب أن تكون وحدك في الإطار.",
        "scan_dup": "هذا الوجه مسجل بالفعل.",
        "station_title": "اختر محطتك",
        "language_title": "اختر لغتك",
        "home_welcome": "أهلاً بعودتك، {name}",
        "home_sub": "حافظ على سلسلتك مستمرة.",
        "tasks_total": "{n} مهمة صحية مكتملة خلال السنة الماضية",
        "streak": "🔥 سلسلة {n} يوم",
        "no_tasks": "لا توجد مهام بعد. مهمتك تبدأ اليوم.",
        "orbiting": "في المدار: {station}",
        "station_line": "المحطة: {station}",
        "profile": "الملف الشخصي",
        "crew": "أفراد الطاقم",
        "no_crew": "لا يوجد طاقم بعد",
        "settings": "الإعدادات",
        "current_station": "المحطة الحالية",
        "reminders": "تذكيرات يومية",
        "animate": "تحريك نموذج المحطة",
        "less": "أقل",
        "more": "أكثر",
        "topic_Fitness": "اللياقة",
        "topic_Hydration": "الترطيب",
        "topic_Sleep": "النوم",
        "topic_Nutrition": "التغذية",
        "topic_Mindfulness": "الذهن",
        "topic_Medication": "الأدوية",
        "topic_Progress": "التقدم",
        # mission day & tasks
        "mission_day": "يوم المهمة {d}",
        "mission_tasks_title": "يوم المهمة {d} — قائمة المهام",
        "mission_tasks_sub": "الوقت يمر بشكل مختلف في الفضاء. اختر يوم مهمتك لعرض وإكمال مهامك.",
        "task_item": "مهمة {n}",
        "tasks_done_count": "تم إنجاز {done} من {total}",
        # branding + heatmap tooltip
        "brand": "صحة الفضاء",
        "mission_control": "مركز التحكم // المؤشرات الحيوية",
        "heat_tip": "{date}  •  {n} مكتملة",
        # Inside TEXT["en"]
        "nut_select_placeholder": "Select a menu item...",
        "nut_add_item": "+ Add",
        "menu_topics": "المواضيع الصحية",
        "hazards_menu": "مخاطر الرحلات الفضائية",
        "hazards_title": "المخاطر الخمسة للرحلات الفضائية البشرية  ·  ناسا",
        "hz_risks": "أبرز المخاطر",
        "hz_counter": "إجراءات التصدي",
        "hz_link": "كيف تساعد مهامك اليومية",
        "hz_close": "إغلاق",
        # nutrition page (add inside TEXT["ar"])
        "nut_title": "تغذية رواد الفضاء",
        "nut_sub": "اختر الوجبات المتناولة ليوم المهمة {d} (دورة القائمة يوم {r}) لتتبع المغذيات الدقيقة.",
        "nut_chart_title": "المدخول اليومي من المغذيات الدقيقة (% من الهدف)",
        "nut_chart_sub": "جميع المغذيات الدقيقة الـ 21 نسبةً إلى الهدف / الحد اليومي (خط 100%).",
        "nut_meal_breakfast": "الإفطار",
        "nut_meal_lunch": "الغداء",
        "nut_meal_dinner": "العشاء",
        "nut_meal_snacks": "الوجبات الخفيفة",
        "nut_planned_kcal": "السعرات المخططة: {kcal} سعرة",
        "nut_missing_warn": "بيانات المغذيات غير متوفرة لـ: {items}",
        "nut_demo_notice": "يتم استخدام بيانات تجريبية (food_nutrients_DEMO.json).",
        "nut_no_data": "لم يتم العثور على ملف بيانات الغذاء. شغّل make_demo_data.py أولاً.",
        "nut_reset": "مسح اليوم",
        "nut_status_low": "منخفض (<70%)",
        "nut_status_near": "قريب (70-99%)",
        "nut_status_met": "مكتمل (≥100%)",
        "nut_status_ok": "الصوديوم طبيعي (≤100%)",
        "nut_status_over": "تجاوز الحد (>100%)",
        "nut_tip": "{name}: {amount:.1f} / {target} {unit} ({pct:.0f}%)",
    },
}


# ---------------------------------------------------------------------------
# NASA's 5 Hazards of Human Spaceflight (RIDGE).
# "topics" are keys of the health topics (topic_<key> in TEXT) that these hazards
# connect to, shown as chips under "How your daily tasks help".
# ---------------------------------------------------------------------------
HAZARDS = [
    {
        "id": "radiation", "icon": "☢", "topics": ["Nutrition", "Sleep", "Medication"],
        "en": {
            "name": "Space Radiation",
            "short": "Space Radiation",
            "summary": "Beyond Earth's protective magnetic field, crews are exposed to galactic "
                       "cosmic rays and solar particle events that can damage cells and DNA.",
            "risks": ["Higher lifetime cancer risk",
                      "Possible effects on the brain and nervous system",
                      "Cardiovascular and other tissue changes"],
            "counter": ["Shielding and storm shelters for solar events",
                        "Personal dosimeters track each crew member's exposure",
                        "Mission planning limits time in high-radiation conditions"],
            "link": "Nutrition and sleep tasks support your overall resilience, and medication "
                    "tasks keep any prescribed regimen on schedule.",
        },
        "ar": {
            "name": "الإشعاع الفضائي",
            "short": "الإشعاع الفضائي",
            "summary": "خارج المجال المغناطيسي للأرض، يتعرض الطاقم للأشعة الكونية المجرّية "
                       "وللجسيمات الصادرة عن العواصف الشمسية، وقد تتلف الخلايا والحمض النووي.",
            "risks": ["ارتفاع خطر الإصابة بالسرطان على مدى العمر",
                      "احتمال تأثر الدماغ والجهاز العصبي",
                      "تغيّرات في القلب والأوعية وأنسجة الجسم"],
            "counter": ["دروع واقية وملاجئ للعواصف الشمسية",
                        "أجهزة قياس شخصية لتتبع تعرّض كل فرد من الطاقم",
                        "تخطيط المهمة للحد من البقاء في مناطق الإشعاع العالي"],
            "link": "مهام التغذية والنوم تدعم مرونة جسمك العامة، ومهام الدواء تحافظ على "
                    "انتظام أي علاج موصوف لك.",
        },
    },
    {
        "id": "isolation", "icon": "🔒", "topics": ["Mindfulness", "Sleep", "Fitness"],
        "en": {
            "name": "Isolation and Confinement",
            "short": "Isolation & Confinement",
            "summary": "Months in a small, shared space with the same few people strain "
                       "sleep, mood and teamwork.",
            "risks": ["Sleep disruption and fatigue",
                      "Anxiety, low mood and loss of motivation",
                      "Conflict within a small crew"],
            "counter": ["Regular private calls with family and friends",
                        "Crew meetings and behavioral-health check-ins",
                        "Personal time, hobbies and exercise routines"],
            "link": "Mindfulness, sleep and fitness tasks build the habits that protect your "
                    "mood and focus.",
        },
        "ar": {
            "name": "العزلة والحيّز المحصور",
            "short": "العزلة والحصر",
            "summary": "أشهر طويلة في مساحة صغيرة مع الأشخاص أنفسهم تضغط على النوم والمزاج "
                       "والعمل الجماعي.",
            "risks": ["اضطراب النوم والإرهاق",
                      "القلق وانخفاض المزاج وفقدان الحافز",
                      "خلافات داخل الطاقم الصغير"],
            "counter": ["مكالمات خاصة منتظمة مع الأهل والأصدقاء",
                        "اجتماعات للطاقم وجلسات متابعة للصحة النفسية",
                        "وقت شخصي وهوايات وروتين رياضي"],
            "link": "مهام الذهن والنوم واللياقة تبني العادات التي تحمي مزاجك وتركيزك.",
        },
    },
    {
        "id": "distance", "icon": "🌍", "topics": ["Medication", "Progress", "Nutrition"],
        "en": {
            "name": "Distance from Earth",
            "short": "Distance from Earth",
            "summary": "Far from home, help cannot arrive quickly. Communication delays and "
                       "limited resupply mean crews handle many problems on their own.",
            "risks": ["Message delays: ~1.3 s to the Moon, up to ~20 min to Mars",
                      "Limited medical evacuation and supplies",
                      "More reliance on self-monitoring and onboard care"],
            "counter": ["Medical self-care training and onboard health kits",
                        "Pre-planned procedures and delayed-messaging tools",
                        "Careful stocking and tracking of food and medication"],
            "link": "Logging your tasks and medication every day gives you and your team "
                    "reliable health records when live support is far away.",
        },
        "ar": {
            "name": "البعد عن الأرض",
            "short": "البعد عن الأرض",
            "summary": "بعيداً عن الوطن لا تصل المساعدة بسرعة. التأخر في الاتصالات وقلة "
                       "الإمدادات يعنيان أن الطاقم يعالج كثيراً من المشكلات بنفسه.",
            "risks": ["تأخر الرسائل: نحو 1.3 ثانية إلى القمر، وحتى نحو 20 دقيقة إلى المريخ",
                      "صعوبة الإخلاء الطبي ومحدودية الإمدادات",
                      "اعتماد أكبر على المراقبة الذاتية والرعاية على متن المركبة"],
            "counter": ["تدريب على الرعاية الطبية الذاتية وحقائب صحية على متن المركبة",
                        "إجراءات مُعدّة مسبقاً وأدوات مراسلة مؤجلة",
                        "تخزين وتتبع دقيق للغذاء والأدوية"],
            "link": "تسجيل مهامك وأدويتك يومياً يمنحك ويمنح فريقك سجلات صحية موثوقة حين "
                    "يكون الدعم المباشر بعيداً.",
        },
    },
    {
        "id": "gravity", "icon": "⚖", "topics": ["Fitness", "Hydration", "Nutrition"],
        "en": {
            "name": "Gravity Fields",
            "short": "Gravity Fields",
            "summary": "Microgravity on the ISS and reduced gravity on the Moon and Mars change "
                       "how bones, muscles, the heart and body fluids behave.",
            "risks": ["Bone density and muscle loss",
                      "Cardiovascular deconditioning and fluid shifts",
                      "Balance problems and vision changes after long flights"],
            "counter": ["Around two hours of resistance and aerobic exercise most days",
                        "Enough calcium, vitamin D and protein",
                        "Readaptation training after landing"],
            "link": "Fitness, hydration and nutrition tasks are your daily gravity "
                    "countermeasures.",
        },
        "ar": {
            "name": "مجالات الجاذبية",
            "short": "مجالات الجاذبية",
            "summary": "انعدام الوزن على المحطة الدولية وضعف الجاذبية على القمر والمريخ "
                       "يغيّران سلوك العظام والعضلات والقلب وسوائل الجسم.",
            "risks": ["فقدان كثافة العظام والكتلة العضلية",
                      "ضعف لياقة القلب والأوعية وانتقال السوائل في الجسم",
                      "اضطراب التوازن وتغيّر الرؤية بعد الرحلات الطويلة"],
            "counter": ["نحو ساعتين من تمارين المقاومة والتمارين الهوائية في معظم الأيام",
                        "كمية كافية من الكالسيوم وفيتامين د والبروتين",
                        "تدريب على إعادة التكيّف بعد الهبوط"],
            "link": "مهام اللياقة والترطيب والتغذية هي إجراءاتك اليومية لمواجهة الجاذبية.",
        },
    },
    {
        "id": "environment", "icon": "🌡", "topics": ["Hydration", "Sleep", "Nutrition"],
        "en": {
            "name": "Hostile / Closed Environments",
            "short": "Closed Environments",
            "summary": "A spacecraft or habitat is a sealed system. Air, water, temperature, "
                       "noise, light and microbes all have to be managed carefully.",
            "risks": ["Poor air quality or high carbon dioxide",
                      "Noise, vibration and disrupted day-night light cycles",
                      "Microbes and contamination in shared water and surfaces"],
            "counter": ["Air and water recycling with constant monitoring",
                        "Regular cleaning and hygiene routines",
                        "Lighting schedules that mimic day and night"],
            "link": "Hydration, sleep and nutrition tasks help you adapt to the habitat's "
                    "rhythm and stay healthy in a shared space.",
        },
        "ar": {
            "name": "البيئات القاسية والمغلقة",
            "short": "البيئات المغلقة",
            "summary": "المركبة أو المأوى نظام مغلق، ويجب إدارة الهواء والماء والحرارة "
                       "والضجيج والإضاءة والميكروبات بعناية.",
            "risks": ["رداءة الهواء أو ارتفاع ثاني أكسيد الكربون",
                      "الضجيج والاهتزاز واضطراب دورة الضوء بين النهار والليل",
                      "الميكروبات والتلوث في المياه والأسطح المشتركة"],
            "counter": ["إعادة تدوير الهواء والماء مع مراقبة مستمرة",
                        "روتين منتظم للنظافة والتعقيم",
                        "جداول إضاءة تحاكي النهار والليل"],
            "link": "مهام الترطيب والنوم والتغذية تساعدك على التكيّف مع إيقاع المأوى "
                    "والبقاء بصحة جيدة في مساحة مشتركة.",
        },
    },
]


def tr(lang, key, **kwargs):
    """Return the text for a key in the given language, filling in {placeholders}."""
    text = TEXT[lang][key]
    return text.format(**kwargs) if kwargs else text 