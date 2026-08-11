import streamlit as st
import database
import ai

from datetime import date, datetime
import os
import html


# =========================================================
# PAGE SETUP
# =========================================================

st.set_page_config(
    page_title="ConnectAI",
    page_icon="ðŸš€",
    layout="wide"
)


# =========================================================
# BASE DIRECTORY
# =========================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)


# =========================================================
# LOAD CSS
# =========================================================

css_path = os.path.join(
    BASE_DIR,
    "style.css"
)

if os.path.exists(css_path):

    try:

        with open(
            css_path,
            encoding="utf-8"
        ) as f:

            st.markdown(
                f"<style>{f.read()}</style>",
                unsafe_allow_html=True
            )

    except Exception:
        pass


# =========================================================
# DATABASE
# =========================================================

database.init_db()


# =========================================================
# SESSION STATE
# =========================================================

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = {}

if "message_results" not in st.session_state:
    st.session_state.message_results = {}

if "conversion_results" not in st.session_state:
    st.session_state.conversion_results = {}

if "editing_contact" not in st.session_state:
    st.session_state.editing_contact = None


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_lead_status(score):

    if score >= 70:
        return "ðŸ”¥ Ù…Ø´ØªØ±ÛŒ Ø¯Ø§Øº", "#EF4444"

    if score >= 40:
        return "ðŸŸ  Ù…Ø´ØªØ±ÛŒ Ù…ØªÙˆØ³Ø·", "#F59E0B"

    return "âšª Ù…Ø´ØªØ±ÛŒ Ø³Ø±Ø¯", "#64748B"


def calculate_lead_score(contact):

    score = 0

    if contact.get("contact_type") == "Ú©Ø§Ø±ÛŒ":
        score += 30

    if contact.get("phone"):
        score += 10

    if contact.get("email"):
        score += 10

    if contact.get("note"):
        score += 15

    if contact.get("vip", 0):
        score += 15

    try:

        followup = contact.get(
            "followup",
            ""
        )

        if followup:

            followup_date = datetime.strptime(
                followup,
                "%Y-%m-%d"
            ).date()

            diff = (
                followup_date - date.today()
            ).days

            if diff <= 3:
                score += 20

    except Exception:
        pass

    return min(score, 100)


# =========================================================
# STATUS
# =========================================================

def get_status(followup):

    if not followup:

        return (
            "#64748B",
            "Ø¨Ø¯ÙˆÙ† Ù¾ÛŒÚ¯ÛŒØ±ÛŒ"
        )

    try:

        d = datetime.strptime(
            followup,
            "%Y-%m-%d"
        ).date()

    except Exception:

        return (
            "#64748B",
            "ØªØ§Ø±ÛŒØ® Ù†Ø§Ù…Ø¹ØªØ¨Ø±"
        )

    diff = (
        d - date.today()
    ).days

    if diff < 0:

        return (
            "#EF4444",
            f"âš ï¸ {abs(diff)} Ø±ÙˆØ² Ú¯Ø°Ø´ØªÙ‡"
        )

    if diff == 0:

        return (
            "#EF4444",
            "ðŸ”´ Ø§Ù…Ø±ÙˆØ²"
        )

    if diff <= 3:

        return (
            "#F59E0B",
            f"ðŸŸ  {diff} Ø±ÙˆØ² Ù…Ø§Ù†Ø¯Ù‡"
        )

    return (
        "#3B82F6",
        f"ðŸ”µ {diff} Ø±ÙˆØ² Ù…Ø§Ù†Ø¯Ù‡"
    )


# =========================================================
# AVATAR
# =========================================================

def get_avatar(name):

    name = str(
        name or ""
    ).strip()

    if not name:

        return (
            "#3B82F6",
            "?"
        )

    colors = [
        "#3B82F6",
        "#10B981",
        "#F59E0B",
        "#EF4444",
        "#8B5CF6"
    ]

    color = colors[
        sum(
            map(
                ord,
                name
            )
        ) % len(colors)
    ]

    return (
        color,
        name[0]
    )


# =========================================================
# AI ANALYSIS
# =========================================================

def smart_analysis(contact):

    try:

        return ai.analyze_contact(
            contact
        )

    except Exception as e:

        return (
            "âŒ Ø®Ø·Ø§ Ø¯Ø± Ø§Ø¬Ø±Ø§ÛŒ Ù‡ÙˆØ´ Ù…ØµÙ†ÙˆØ¹ÛŒ:\n\n"
            f"{e}"
        )


# =========================================================
# AI MESSAGE
# =========================================================

def smart_message(contact):

    try:

        return ai.generate_message(
            contact
        )

    except Exception:

        name = (
            contact.get("name")
            or "Ù…Ø®Ø§Ø·Ø¨"
        )

        return ai.fallback_message(
            name
        )


# =========================================================
# CONVERSION PROBABILITY
# =========================================================

def smart_conversion(contact):

    try:

        return ai.predict_conversion(
            contact
        )

    except Exception as e:

        return (
            "âŒ Ø®Ø·Ø§ Ø¯Ø± Ù¾ÛŒØ´â€ŒØ¨ÛŒÙ†ÛŒ Ø§Ø­ØªÙ…Ø§Ù„ ØªØ¨Ø¯ÛŒÙ„:\n\n"
            f"{e}"
        )


# =========================================================
# HEADER
# =========================================================

st.title(
    "ðŸš€ ConnectAI"
)

st.caption(
    "Your smart contact assistant"
)


# =========================================================
# ADD CONTACT
# =========================================================

st.subheader(
    "âž• Ø§ÙØ²ÙˆØ¯Ù† Ù…Ø®Ø§Ø·Ø¨ Ø¬Ø¯ÛŒØ¯"
)

with st.container():

    col1, col2 = st.columns(2)

    with col1:

        new_name = st.text_input(
            "ðŸ‘¤ Ø§Ø³Ù… Ù…Ø®Ø§Ø·Ø¨",
            key="new_name"
        )

        new_phone = st.text_input(
            "ðŸ“ž Ø´Ù…Ø§Ø±Ù‡ ØªÙ„ÙÙ†",
            key="new_phone"
        )

        new_email = st.text_input(
            "ðŸ“§ Ø§ÛŒÙ…ÛŒÙ„",
            key="new_email"
        )

    with col2:

        new_note = st.text_area(
            "ðŸ“ ÛŒØ§Ø¯Ø¯Ø§Ø´Øª",
            key="new_note"
        )

        new_followup = st.date_input(
            "ðŸ“… ØªØ§Ø±ÛŒØ® Ù¾ÛŒÚ¯ÛŒØ±ÛŒ",
            value=date.today(),
            key="new_followup"
        )

        new_type = st.selectbox(
            "ðŸ·ï¸ Ù†ÙˆØ¹ Ù…Ø®Ø§Ø·Ø¨",
            [
                "Ø´Ø®ØµÛŒ",
                "Ú©Ø§Ø±ÛŒ"
            ],
            key="new_type"
        )


if st.button(
    "ðŸš€ Ø°Ø®ÛŒØ±Ù‡ Ù…Ø®Ø§Ø·Ø¨",
    use_container_width=True
):

    if not new_name.strip():

        st.warning(
            "Ù„Ø·ÙØ§Ù‹ Ù†Ø§Ù… Ù…Ø®Ø§Ø·Ø¨ Ø±Ø§ ÙˆØ§Ø±Ø¯ Ú©Ù†ÛŒØ¯."
        )

    else:

        database.add_contact(
            new_name.strip(),
            new_phone.strip(),
            new_email.strip(),
            new_note.strip(),
            new_followup.isoformat(),
            new_type
        )

        st.success(
            "âœ… Ù…Ø®Ø§Ø·Ø¨ Ø¨Ø§ Ù…ÙˆÙÙ‚ÛŒØª Ø°Ø®ÛŒØ±Ù‡ Ø´Ø¯."
        )

        st.rerun()


# =========================================================
# LOAD CONTACTS
# =========================================================

contacts = database.get_contacts()


# =========================================================
# DASHBOARD CALCULATIONS
# =========================================================

total_count = len(contacts)

today_count = 0
late_count = 0
vip_count = 0
hot_count = 0
work_count = 0

for contact in contacts:

    if contact.get("vip", 0):
        vip_count += 1

    if contact.get(
        "contact_type"
    ) == "Ú©Ø§Ø±ÛŒ":

        work_count += 1

    if calculate_lead_score(
        contact
    ) >= 70:

        hot_count += 1

    try:

        followup = contact.get(
            "followup",
            ""
        )

        if followup:

            d = datetime.strptime(
                followup,
                "%Y-%m-%d"
            ).date()

            diff = (
                d - date.today()
            ).days

            if diff == 0:

                today_count += 1

            elif diff < 0:

                late_count += 1

    except Exception:
        pass


# =========================================================
# DASHBOARD
# =========================================================

st.divider()

st.subheader(
    "ðŸ“Š Ø¯Ø§Ø´Ø¨ÙˆØ±Ø¯"
)

c1, c2, c3 = st.columns(3)

with c1:

    st.metric(
        "ðŸ‘¥ Ú©Ù„ Ù…Ø®Ø§Ø·Ø¨ÛŒÙ†",
        total_count
    )

with c2:

    st.metric(
        "ðŸ”´ Ù¾ÛŒÚ¯ÛŒØ±ÛŒ Ø§Ù…Ø±ÙˆØ²",
        today_count
    )

with c3:

    st.metric(
        "âš ï¸ Ù¾ÛŒÚ¯ÛŒØ±ÛŒ Ú¯Ø°Ø´ØªÙ‡",
        late_count
    )


c4, c5, c6 = st.columns(3)

with c4:

    st.metric(
        "â­ VIP",
        vip_count
    )

with c5:

    st.metric(
        "ðŸ”¥ Ù…Ø´ØªØ±ÛŒ Ø¯Ø§Øº",
        hot_count
    )

with c6:

    st.metric(
        "ðŸ’¼ Ú©Ø§Ø±ÛŒ",
        work_count
    )


# =========================================================
# SEARCH & SORT
# =========================================================

st.divider()

search_col, sort_col = st.columns(
    [3, 1]
)

with search_col:

    search = st.text_input(
        "ðŸ” Ø¬Ø³ØªØ¬ÙˆÛŒ Ù…Ø®Ø§Ø·Ø¨",
        placeholder="Ù†Ø§Ù…ØŒ Ø´Ù…Ø§Ø±Ù‡ØŒ Ø§ÛŒÙ…ÛŒÙ„ ÛŒØ§ ÛŒØ§Ø¯Ø¯Ø§Ø´Øª..."
    )

with sort_col:

    sort_option = st.selectbox(
        "ðŸ”€ Ù…Ø±ØªØ¨â€ŒØ³Ø§Ø²ÛŒ",
        [
            "Ù†Ø²Ø¯ÛŒÚ©â€ŒØªØ±ÛŒÙ† ØªØ§Ø±ÛŒØ® Ù¾ÛŒÚ¯ÛŒØ±ÛŒ",
            "Ø§Ø³Ù… (Ø§Ù„ÙØ¨Ø§ÛŒÛŒ)",
            "Ø§Ù…ØªÛŒØ§Ø² Ù„ÛŒØ¯",
            "Ø¬Ø¯ÛŒØ¯ØªØ±ÛŒÙ†"
        ]
    )


# =========================================================
# SEARCH
# =========================================================

if search:

    search_lower = search.lower()

    contacts = [

        contact

        for contact in contacts

        if (
            search_lower
            in (
                contact.get("name")
                or ""
            ).lower()
        )

        or (

            search_lower
            in (
                contact.get("phone")
                or ""
            ).lower()
        )

        or (

            search_lower
            in (
                contact.get("email")
                or ""
            ).lower()
        )

        or (

            search_lower
            in (
                contact.get("note")
                or ""
            ).lower()
        )

    ]


# =========================================================
# SORT
# =========================================================

if sort_option == "Ø§Ø³Ù… (Ø§Ù„ÙØ¨Ø§ÛŒÛŒ)":

    contacts = sorted(
        contacts,
        key=lambda x: (
            x.get("name")
            or ""
        ).lower()
    )

elif sort_option == "Ø§Ù…ØªÛŒØ§Ø² Ù„ÛŒØ¯":

    contacts = sorted(
        contacts,
        key=lambda x:
            calculate_lead_score(x),
        reverse=True
    )

elif sort_option == "Ø¬Ø¯ÛŒØ¯ØªØ±ÛŒÙ†":

    contacts = sorted(
        contacts,
        key=lambda x:
            x.get(
                "id",
                0
            ),
        reverse=True
    )

else:

    contacts = sorted(
        contacts,
        key=lambda x:
            x.get(
                "followup"
            )
            or "9999-12-31"
    )


# =========================================================
# CONTACTS
# =========================================================

st.subheader(
    "ðŸ‘¥ Ù…Ø®Ø§Ø·Ø¨ÛŒÙ†"
)


if not contacts:

    st.info(
        "Ù‡Ù†ÙˆØ² Ù…Ø®Ø§Ø·Ø¨ÛŒ Ø¨Ø±Ø§ÛŒ Ù†Ù…Ø§ÛŒØ´ ÙˆØ¬ÙˆØ¯ Ù†Ø¯Ø§Ø±Ø¯."
    )


else:

    for contact in contacts:

        contact_id = contact["id"]

        name = str(
            contact.get("name")
            or "Ù…Ø®Ø§Ø·Ø¨"
        ).strip()

        color, avatar = get_avatar(
            name
        )

        status_color, status_text = get_status(
            contact.get(
                "followup",
                ""
            )
        )

        score = calculate_lead_score(
            contact
        )

        lead_status, lead_color = get_lead_status(
            score
        )


        # =================================================
        # CONTACT CARD
        # =================================================

        with st.container():

            st.markdown(
                f"""
                <div class="contact-card">

                    <div style="
                        display:flex;
                        align-items:center;
                        gap:20px;
                    ">

                        <div style="
                            background:{color};
                            width:60px;
                            height:60px;
                            min-width:60px;
                            border-radius:50%;
                            display:flex;
                            align-items:center;
                            justify-content:center;
                            color:white;
                            font-size:28px;
                            font-weight:bold;
                        ">
                            {html.escape(avatar)}
                        </div>

                        <div style="
                            flex:1;
                        ">

                            <div style="
                                font-size:25px;
                                font-weight:800;
                                margin-bottom:8px;
                            ">
                                {html.escape(name)}
                            </div>

                            <div>
                                ðŸ“ž {html.escape(
                                    str(
                                        contact.get("phone")
                                        or "-"
                                    )
                                )}
                            </div>

                            <div>
                                ðŸ“§ {html.escape(
                                    str(
                                        contact.get("email")
                                        or "-"
                                    )
                                )}
                            </div>

                            <div>
                                ðŸ“ {html.escape(
                                    str(
                                        contact.get("note")
                                        or "-"
                                    )
                                )}
                            </div>

                            <div>
                                ðŸ“… {html.escape(
                                    str(
                                        contact.get("followup")
                                        or "-"
                                    )
                                )}
                            </div>

                            <div style="
                                color:{status_color};
                                font-weight:bold;
                                margin-top:5px;
                            ">
                                {html.escape(status_text)}
                            </div>

                        </div>

                        <div style="
                            text-align:center;
                            min-width:100px;
                        ">

                            <div style="
                                font-size:28px;
                                font-weight:800;
                            ">
                                {score}
                            </div>

                            <div>
                                ðŸ”¥ Lead Score
                            </div>

                            <div style="
                                color:{lead_color};
                                font-weight:700;
                                margin-top:5px;
                            ">
                                {html.escape(lead_status)}
                            </div>

                        </div>

                    </div>

                </div>
                """,
                unsafe_allow_html=True
            )


            # =================================================
            # BUTTONS
            # =================================================

            b1, b2, b3, b4, b5 = st.columns(
                5
            )


            # =================================================
            # VIP
            # =================================================

            with b1:

                vip_icon = (
                    "â­"
                    if contact.get("vip", 0)
                    else "â˜†"
                )

                if st.button(
                    vip_icon,
                    key=f"vip_{contact_id}",
                    use_container_width=True
                ):

                    database.toggle_vip(
                        contact_id,
                        contact.get(
                            "vip",
                            0
                        )
                    )

                    st.rerun()


            # =================================================
            # AI ANALYSIS
            # =================================================

            with b2:

                if st.button(
                    "ðŸ§  ØªØ­Ù„ÛŒÙ„",
                    key=f"ai_{contact_id}",
                    use_container_width=True
                ):

                    with st.spinner(
                        "ðŸ§  Ø¯Ø± Ø­Ø§Ù„ ØªØ­Ù„ÛŒÙ„ Ù…Ø®Ø§Ø·Ø¨..."
                    ):

                        result = smart_analysis(
                            contact
                        )

                    st.session_state.analysis_results[
                        contact_id
                    ] = result


            # =================================================
            # AI MESSAGE
            # =================================================

            with b3:

                if st.button(
                    "ðŸ¤– Ù¾ÛŒØ§Ù…",
                    key=f"msg_{contact_id}",
                    use_container_width=True
                ):

                    with st.spinner(
                        "âœï¸ Ø¯Ø± Ø­Ø§Ù„ Ø³Ø§Ø®Øª Ù¾ÛŒØ§Ù…..."
                    ):

                        result = smart_message(
                            contact
                        )

                    st.session_state.message_results[
                        contact_id
                    ] = result


            # =================================================
            # EDIT
            # =================================================

            with b4:

                if st.button(
                    "âœï¸ ÙˆÛŒØ±Ø§ÛŒØ´",
                    key=f"edit_{contact_id}",
                    use_container_width=True
                ):

                    st.session_state.editing_contact = (
                        contact_id
                    )

                    st.rerun()


            # =================================================
            # DELETE
            # =================================================

            with b5:

                if st.button(
                    "ðŸ—‘ Ø­Ø°Ù",
                    key=f"delete_{contact_id}",
                    use_container_width=True
                ):

                    database.delete_contact(
                        contact_id
                    )

        