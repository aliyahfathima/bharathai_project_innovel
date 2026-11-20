import os
import streamlit as st
from dotenv import load_dotenv

from modules.models import CitizenProfile
from modules.ai import extract_profile, ask_gemini
from modules.search import search_schemes
from modules.eligibility import evaluate_eligibility
from modules.storage import save_search, recent_searches, init_db
from modules.i18n import LANGUAGES, STATES, t, opt

load_dotenv()

st.set_page_config(
    page_title="BharatScheme AI",
    page_icon="🇮🇳",
    layout="wide",
    initial_sidebar_state="expanded",
)
init_db()

# ----------------------------- Styling -------------------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700;800&family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
:root { --ink:#14213d; --muted:#667085; --teal:#087f8c; --orange:#f4a261; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background:linear-gradient(135deg,#f6fbff 0%,#f7f8fc 48%,#fff8f1 100%); }
.block-container { padding-top:1.5rem; max-width:1320px; }
section[data-testid="stSidebar"] { background:linear-gradient(180deg,#102a43,#123e52); }
section[data-testid="stSidebar"] * { color:#f4f8fb !important; }
.hero { background:linear-gradient(120deg,#102a43 0%,#087f8c 62%,#13a89e 100%);
 padding:2.3rem 2.5rem; border-radius:26px; color:white; position:relative; overflow:hidden;
 box-shadow:0 18px 45px rgba(8,75,95,.18); }
.hero:after {content:'🇮🇳';position:absolute;right:4%;top:8%;font-size:6rem;opacity:.15;}
.hero h1 {font-family:'Plus Jakarta Sans';font-size:2.7rem;line-height:1.1;margin:0;color:white;}
.hero p {font-size:1.08rem;color:#e4f7f7;margin:.8rem 0 0;}
.eyebrow {letter-spacing:2px;text-transform:uppercase;font-size:.72rem;font-weight:800;color:#ffd6a5;}
.section-title {font-family:'Plus Jakarta Sans';font-size:1.35rem;font-weight:800;color:#14213d;margin:.4rem 0 .8rem;}
.info-card {background:white;border:1px solid #e8edf3;border-radius:18px;padding:1.1rem 1.25rem;
 box-shadow:0 7px 22px rgba(25,50,80,.045);height:100%;}
.info-card h4 {margin:0 0 .35rem;color:#14213d;font-size:1rem;}
.info-card p {margin:0;color:#667085;font-size:.9rem;line-height:1.5;}
.metric-card {background:white;border:1px solid #e8edf3;border-radius:16px;padding:1rem;text-align:center;}
.metric-card strong {display:block;font-size:1.6rem;color:#087f8c;}
.metric-card span {font-size:.8rem;color:#667085;}
.scheme-card {background:white;border:1px solid #e5ebf1;border-radius:20px;padding:1.25rem 1.35rem;
 box-shadow:0 10px 26px rgba(22,48,75,.06);margin:.7rem 0 1rem;}
.scheme-card h3 {margin:.1rem 0 .3rem;color:#14213d;font-size:1.18rem;}
.small-muted {color:#667085;font-size:.82rem;}
.pill {display:inline-block;background:#e7f7f5;color:#087f8c;border-radius:30px;padding:.25rem .65rem;
 font-size:.74rem;font-weight:700;margin:.15rem .2rem .15rem 0;}
.stButton>button {border-radius:12px;font-weight:700;min-height:2.8rem;}
div[data-testid="stForm"] {background:white;border:1px solid #e8edf3;padding:1.2rem;border-radius:18px;}
div[data-testid="stTabs"] button {font-weight:700;}
footer {visibility:hidden;}
</style>
""", unsafe_allow_html=True)

# ----------------------------- Session state ------------------------------
if "results" not in st.session_state:
    st.session_state.results = []
if "profile" not in st.session_state:
    st.session_state.profile = None
if "source_context" not in st.session_state:
    st.session_state.source_context = ""
if "language" not in st.session_state:
    st.session_state.language = "English"


def tr(key, **kwargs):
    """Translated UI text, with English fallback supplied by modules.i18n."""
    return t(st.session_state.language, key, **kwargs)


def display_option(group, value):
    """Translate display text without changing the English value sent to backend."""
    return opt(group, value, st.session_state.language)


# ----------------------------- Sidebar -------------------------------------
with st.sidebar:
    st.markdown("## 🇮🇳 BharatScheme AI")
    st.caption("Your intelligent government scheme companion")

    st.selectbox(
        "🌐 Language / மொழி / भाषा",
        options=list(LANGUAGES.keys()),
        key="language",
        format_func=lambda language: language,
    )
    lang = st.session_state.language

    st.markdown("---")
    page_labels = {
        "Discover Schemes": {
            "English": "Discover Schemes",
            "தமிழ்": "திட்டங்களைக் கண்டறிய",
            "हिन्दी": "योजनाएँ खोजें",
        },
        "How It Works": {
            "English": "How It Works",
            "தமிழ்": "இது எவ்வாறு செயல்படுகிறது",
            "हिन्दी": "यह कैसे काम करता है",
        },
        "Search History": {
            "English": "Search History",
            "தமிழ்": "தேடல் வரலாறு",
            "हिन्दी": "खोज इतिहास",
        },
        "About & Trust": {
            "English": "About & Trust",
            "தமிழ்": "தகவல் மற்றும் நம்பகத்தன்மை",
            "हिन्दी": "जानकारी और विश्वसनीयता",
        },
    }
    page_keys = list(page_labels.keys())
    selected_page = st.radio(
        "NAVIGATION",
        page_keys,
        format_func=lambda key: page_labels[key].get(lang, key),
    )
    page = selected_page

    st.markdown("---")
    st.markdown("**LIVE SERVICES**")
    st.caption("Tavily: " + ("Connected" if os.getenv("TAVILY_API_KEY") else "API key required"))
    st.caption("Gemini: " + ("Connected" if os.getenv("GEMINI_API_KEY") else "Fallback mode"))
    st.markdown("---")
    st.caption("Always verify eligibility and application details on the official government portal.")

# ----------------------------- Discover ------------------------------------
if page == "Discover Schemes":
    hero_title = {
        "English": "Benefits are for everyone.<br>Finding them should be simple.",
        "தமிழ்": "அரசுத் திட்டங்கள் அனைவருக்கும்.<br>அவற்றைக் கண்டறிவது எளிதாகட்டும்.",
        "हिन्दी": "लाभ सभी के लिए हैं।<br>उन्हें खोजना आसान होना चाहिए।",
    }.get(lang)
    hero_subtitle = {
        "English": "Tell us about yourself. Discover relevant government schemes, understand eligibility<br>and get clear application guidance — all in one place.",
        "தமிழ்": "உங்களைப் பற்றிய விவரங்களைப் பகிர்ந்து, பொருத்தமான அரசுத் திட்டங்கள்,<br>தகுதி மற்றும் விண்ணப்ப வழிகாட்டுதலை ஒரே இடத்தில் பெறுங்கள்.",
        "हिन्दी": "अपने बारे में बताएँ। संबंधित सरकारी योजनाएँ खोजें, पात्रता समझें<br>और आवेदन संबंधी मार्गदर्शन एक ही जगह पाएँ।",
    }.get(lang)

    st.markdown(f"""
    <div class="hero">
      <div class="eyebrow">Every citizen. Every scheme. One intelligent guide.</div>
      <h1>{hero_title}</h1>
      <p>{hero_subtitle}</p>
    </div>""", unsafe_allow_html=True)

    st.write("")
    m1, m2, m3, m4 = st.columns(4)
    metric_labels = {
        "English": ["States", "Union Territories", "Citizen-first platform", "Digital discovery"],
        "தமிழ்": ["மாநிலங்கள்", "ஒன்றியப் பிரதேசங்கள்", "குடிமக்கள் தளம்", "டிஜிட்டல் தேடல்"],
        "हिन्दी": ["राज्य", "केंद्र शासित प्रदेश", "नागरिक-केंद्रित मंच", "डिजिटल खोज"],
    }.get(lang)
    for col, num, label in zip(
        (m1, m2, m3, m4), ("28", "8", "01", "24×7"), metric_labels
    ):
        col.markdown(
            f'<div class="metric-card"><strong>{num}</strong><span>{label}</span></div>',
            unsafe_allow_html=True,
        )

    st.write("")
    left, right = st.columns([1.05, 1], gap="large")

    with left:
        st.markdown(
            f'<div class="section-title">✨ {tr("profile_header")}</div>',
            unsafe_allow_html=True,
        )
        intro = {
            "English": "Complete the profile so we can compare your details with scheme conditions.",
            "தமிழ்": "திட்ட நிபந்தனைகளுடன் உங்கள் விவரங்களை ஒப்பிட இந்தப் படிவத்தை நிரப்பவும்.",
            "हिन्दी": "योजना की शर्तों से आपकी जानकारी की तुलना करने के लिए प्रोफ़ाइल भरें।",
        }.get(lang)
        st.write(intro)

        with st.form("profile_form"):
            c1, c2 = st.columns(2)
            name = c1.text_input("Name (optional)")
            age = c2.number_input(tr("age"), min_value=0, max_value=120, value=21)

            state_options = STATES
            default_state = "Tamil Nadu"
            state = c1.selectbox(
                tr("state"),
                state_options,
                index=state_options.index(default_state),
            )
            district = c2.text_input(
                tr("district"),
                value="Madurai" if state == "Tamil Nadu" else "",
            )
            income = c1.number_input(
                tr("income"), min_value=0, step=10000, value=200000
            )

            occupation_values = [
                "student", "farmer", "unemployed", "self-employed",
                "daily wage worker", "homemaker", "employed", "retired",
            ]
            occupation = c2.selectbox(
                tr("occupation"),
                occupation_values,
                format_func=lambda value: display_option("occupation", value),
            )

            education_values = [
                "School", "Diploma / ITI", "Undergraduate", "Postgraduate"
            ]
            education = c1.selectbox(
                tr("education"),
                education_values,
                format_func=lambda value: display_option("education", value),
            )

            gender_values = ["Not specified", "Female", "Male", "Other"]
            gender = c2.selectbox(
                tr("gender"),
                gender_values,
                format_func=lambda value: (
                    tr("not_specified") if value == "Not specified"
                    else display_option("gender", value)
                ),
            )

            category_values = ["Not specified", "General", "OBC", "SC", "ST", "EWS"]
            category = c1.selectbox(
                tr("category"),
                category_values,
                format_func=lambda value: (
                    tr("not_specified") if value == "Not specified"
                    else display_option("category", value)
                ),
            )

            family_size = c1.number_input("Family size", min_value=1, max_value=30, value=4)

            need_values = [
                "Scholarship / college fee support",
                "Health insurance / medical support",
                "Farmer support",
                "Housing support",
                "Pension / elderly support",
                "Women welfare",
                "Skill training / employment",
                "Business / self-employment loan",
                "Disability support",
            ]
            need = st.selectbox(
                tr("need"),
                need_values,
                format_func=lambda value: display_option("need", value),
            )
            story = st.text_area(
                tr("desc"),
                placeholder={
                    "English": "Example: I am a 21-year-old student from Madurai. My family income is around ₹2 lakh per year and I need help paying college fees.",
                    "தமிழ்": "எ.கா.: நான் மதுரையைச் சேர்ந்த 21 வயது மாணவர். குடும்ப ஆண்டு வருமானம் சுமார் ₹2 லட்சம். கல்லூரிக் கட்டண உதவி தேவை.",
                    "हिन्दी": "उदाहरण: मैं मदुरै का 21 वर्षीय विद्यार्थी हूँ। मेरे परिवार की वार्षिक आय लगभग ₹2 लाख है और मुझे कॉलेज फीस में सहायता चाहिए।",
                }.get(lang),
                height=100,
                help=tr("desc_help"),
            )
            submitted = st.form_submit_button(
                f"🔎 {tr('find_btn')}",
                type="primary",
                use_container_width=True,
            )

        if submitted:
            defaults = {
                "name": name or None,
                "age": int(age) if age else None,
                "state": state,
                "district": district or None,
                "annual_income": float(income) if income else None,
                "occupation": occupation,
                "education": education,
                "gender": None if gender == "Not specified" else gender,
                "category": None if category == "Not specified" else category,
                "family_size": int(family_size),
                "need": need,
            }
            with st.spinner(tr("searching")):
                profile, mode = extract_profile(story, defaults)
                results, error = search_schemes(profile)

            st.session_state.profile = profile
            st.session_state.results = results
            st.session_state.extract_mode = mode
            st.session_state.search_error = error
            st.session_state.source_context = "\n\n".join(
                f"{result['title']}\n{result['url']}\n{result['content']}"
                for result in results
            )
            st.session_state.answer = ""
            save_search(profile, len(results))
            st.rerun()

    with right:
        journey_title = {
            "English": "🧭 Your journey",
            "தமிழ்": "🧭 உங்கள் பயணம்",
            "हिन्दी": "🧭 आपकी प्रक्रिया",
        }.get(lang)
        st.markdown(
            f'<div class="section-title">{journey_title}</div>',
            unsafe_allow_html=True,
        )
        journey = {
            "English": [
                ("01 · Share your details", "Tell us your age, location, income and the support you need."),
                ("02 · Smart profile extraction", "AI structures your information. Missing details are highlighted."),
                ("03 · Official scheme discovery", "Live search prioritises government domains and official portals."),
                ("04 · Eligibility comparison", "See matching, missing and verification-needed conditions."),
                ("05 · Apply with confidence", "Review documents, steps and the official application link."),
            ],
            "தமிழ்": [
                ("01 · விவரங்களைப் பகிரவும்", "வயது, இருப்பிடம், வருமானம் மற்றும் தேவையான உதவியைத் தெரிவிக்கவும்."),
                ("02 · AI விவரப் பகுப்பாய்வு", "AI உங்கள் தகவல்களை ஒழுங்குபடுத்தி விடுபட்ட விவரங்களைக் காட்டும்."),
                ("03 · அரசு திட்டத் தேடல்", "அரசு இணையதளங்களுக்கு முன்னுரிமை அளித்து தேடும்."),
                ("04 · தகுதி ஒப்பீடு", "பொருந்தும் மற்றும் சரிபார்க்க வேண்டிய நிபந்தனைகளைக் காணலாம்."),
                ("05 · நம்பிக்கையுடன் விண்ணப்பிக்கவும்", "ஆவணங்கள், படிகள் மற்றும் அதிகாரப்பூர்வ இணைப்பைப் பாருங்கள்."),
            ],
            "हिन्दी": [
                ("01 · जानकारी साझा करें", "अपनी आयु, स्थान, आय और आवश्यक सहायता बताएँ।"),
                ("02 · स्मार्ट प्रोफ़ाइल", "AI जानकारी व्यवस्थित करेगा और छूटे विवरण दिखाएगा।"),
                ("03 · सरकारी योजनाओं की खोज", "सरकारी डोमेन और आधिकारिक पोर्टल को प्राथमिकता मिलेगी।"),
                ("04 · पात्रता की तुलना", "मेल खाने वाली और सत्यापन योग्य शर्तें देखें।"),
                ("05 · विश्वास के साथ आवेदन", "दस्तावेज़, चरण और आधिकारिक लिंक देखें।"),
            ],
        }.get(lang)
        for title, desc in journey:
            st.markdown(
                f'<div class="info-card" style="margin-bottom:.65rem"><h4>{title}</h4><p>{desc}</p></div>',
                unsafe_allow_html=True,
            )
        privacy_text = {
            "English": "Your information is used for this session's recommendation. Do not enter Aadhaar, bank account, OTP or other sensitive numbers.",
            "தமிழ்": "உங்கள் தகவல்கள் இந்த அமர்வின் பரிந்துரைக்காக மட்டுமே பயன்படுத்தப்படும். ஆதார், வங்கிக் கணக்கு அல்லது OTP விவரங்களை உள்ளிட வேண்டாம்.",
            "हिन्दी": "आपकी जानकारी इस सत्र की अनुशंसा के लिए उपयोग होती है। आधार, बैंक खाता या OTP जैसी संवेदनशील जानकारी न दें।",
        }.get(lang)
        st.info(privacy_text)

    # Results remain visible after Streamlit reruns and language changes.
    if st.session_state.profile is not None:
        st.markdown("---")
        result_heading = {
            "English": "🎯 Your scheme discovery results",
            "தமிழ்": "🎯 திட்டத் தேடல் முடிவுகள்",
            "हिन्दी": "🎯 योजना खोज परिणाम",
        }.get(lang)
        st.markdown(
            f'<div class="section-title">{result_heading}</div>',
            unsafe_allow_html=True,
        )
        profile = st.session_state.profile
        profile_line = (
            f"Profile: {profile.age or 'Age not provided'} years · {profile.state} · "
            f"{profile.occupation or 'Occupation not provided'} · "
            f"Income ₹{profile.annual_income:,.0f}"
            if profile.annual_income is not None
            else f"Profile: {profile.state} · {profile.occupation or 'Occupation not provided'}"
        )
        st.caption(profile_line)
        st.caption(
            tr("profile_method", m=st.session_state.get("extract_mode", ""))
        )
        if st.session_state.get("search_error"):
            st.warning(st.session_state.search_error)

        results = st.session_state.results
        if not results:
            st.warning(tr("no_results"))
        else:
            st.markdown(f"**{tr('results_header', n=len(results))}**")
            for index, result in enumerate(results, 1):
                evaluation = evaluate_eligibility(
                    profile, result["content"] + " " + result["title"]
                )
                colors = {
                    "Potential Match": "#d9f7e9",
                    "Possible Match": "#fff1d6",
                    "More Information Required": "#e9efff",
                    "Potential Mismatch": "#ffe2e2",
                }
                st.markdown(
                    f"""
                    <div class="scheme-card">
                      <div><span class="pill">OFFICIAL DOMAIN RESULT</span>
                      <span style="background:{colors.get(evaluation.status, '#e9efff')};padding:.25rem .65rem;border-radius:20px;font-size:.74rem;font-weight:800">{evaluation.status}</span></div>
                      <h3>{index:02d}. {result['title']}</h3>
                      <div class="small-muted">{result['url']}</div>
                      <p style="color:#475467;margin:.7rem 0">{result['content'][:850]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander(tr("analysis") + " & " + tr("guidance_header")):
                    st.write(evaluation.explanation)
                    if evaluation.satisfied:
                        st.markdown(f"**{tr('satisfied')}**")
                        for item in evaluation.satisfied:
                            st.write("✅ " + item)
                    if evaluation.not_satisfied:
                        st.markdown(f"**{tr('not_satisfied')}**")
                        for item in evaluation.not_satisfied:
                            st.write("❌ " + item)
                    if evaluation.missing:
                        st.markdown(f"**{tr('missing')}**")
                        for item in evaluation.missing:
                            st.write("🟡 " + item)
                    if evaluation.needs_verification:
                        st.markdown(f"**{tr('verify')}**")
                        for item in evaluation.needs_verification:
                            st.write("🔎 " + item)

                    st.markdown(f"**{tr('guidance_header')}**")
                    for step_number, step in enumerate(tr("guide_steps"), 1):
                        st.write(f"{step_number}. {step}")
                    st.link_button(
                        f"{tr('open_source')} ↗",
                        result["url"],
                    )
                    st.caption(
                        "Documents, deadline, benefit amount and contact details were not inferred from search snippets. Verify them on the source page."
                    )

        st.markdown("---")
        st.markdown(
            f'<div class="section-title">💬 {tr("assistant_header")}</div>',
            unsafe_allow_html=True,
        )
        question = st.text_input(
            "Ask about these results",
            placeholder=tr("ask_placeholder"),
        )
        if st.button(tr("ask_btn"), disabled=not bool(question.strip())):
            with st.spinner("Preparing a source-grounded answer..."):
                st.session_state.answer = ask_gemini(
                    question, st.session_state.source_context
                )
        if st.session_state.get("answer"):
            st.markdown(f"**{tr('answer_header')}**")
            st.info(st.session_state.answer)

# ----------------------------- How it works -------------------------------
elif page == "How It Works":
    heading = {
        "English": "How BharatScheme AI works",
        "தமிழ்": "BharatScheme AI எவ்வாறு செயல்படுகிறது",
        "हिन्दी": "BharatScheme AI कैसे काम करता है",
    }.get(lang)
    st.markdown(f'<div class="section-title">{heading}</div>', unsafe_allow_html=True)
    st.write("A transparent five-stage workflow from citizen profile to official application portal.")
    columns = st.columns(5)
    stages = [
        ("📝", "Describe", "Form + free text"),
        ("🧠", "Extract", "Gemini + Pydantic"),
        ("🌐", "Search", "Tavily official-domain search"),
        ("⚖️", "Analyse", "Conservative eligibility checks"),
        ("🚀", "Guide", "Steps + official source links"),
    ]
    for column, (icon, title, description) in zip(columns, stages):
        column.markdown(
            f'<div class="info-card"><div style="font-size:2rem">{icon}</div><h4>{title}</h4><p>{description}</p></div>',
            unsafe_allow_html=True,
        )
    st.markdown("### Technology architecture")
    st.code(
        "Citizen → Streamlit UI → Gemini profile extraction → Pydantic validation\n"
        "       → Tavily official-domain search → Eligibility engine\n"
        "       → Source-linked results → Application guidance\n"
        "       → SQLite search history",
        language="text",
    )
    st.warning(
        "Eligibility checks are indicative, not an official decision. Scheme rules may include conditions that require reading the full notification."
    )

# ----------------------------- Search history ------------------------------
elif page == "Search History":
    st.markdown(
        f'<div class="section-title">🕘 {tr("history_header")}</div>',
        unsafe_allow_html=True,
    )
    rows = recent_searches()
    if rows:
        for created, state, need, count in rows:
            st.markdown(
                f'<div class="info-card" style="margin-bottom:.6rem"><b>{created}</b><p>{state} · {need} · {count} results</p></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info(tr("history_empty"))

# ----------------------------- About & trust -------------------------------
else:
    about_heading = {
        "English": "🔐 Trust, safety & source verification",
        "தமிழ்": "🔐 நம்பிக்கை, பாதுகாப்பு மற்றும் மூலச் சரிபார்ப்பு",
        "हिन्दी": "🔐 विश्वास, सुरक्षा और स्रोत सत्यापन",
    }.get(lang)
    st.markdown(
        f'<div class="section-title">{about_heading}</div>',
        unsafe_allow_html=True,
    )
    st.markdown("""
    <div class="info-card">
    <h4>Official sources first</h4>
    <p>Search is restricted to government domains such as myscheme.gov.in, india.gov.in,
    gov.in and nic.in where available. Search snippets are leads, not final proof.</p><br>
    <h4>No false promises</h4>
    <p>The app never guarantees scheme approval. Unclear conditions are labelled for
    official verification. Deadlines, benefit amounts and document lists are not invented.</p><br>
    <h4>Privacy by design</h4>
    <p>Do not enter Aadhaar, bank account, OTP or other sensitive identifiers. Search history
    stores a limited profile summary locally in SQLite. Delete the local database file to clear it.</p><br>
    <h4>API key safety</h4>
    <p>Store API keys in .env or Streamlit secrets. Never commit real keys to GitHub.</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("### Important limitation")
    st.write(
        "This prototype searches official-domain pages and compares a small set of clearly recognisable conditions. It does not crawl every government scheme or parse every full notification. Always confirm the latest eligibility, deadlines and application steps with the responsible department."
    )
