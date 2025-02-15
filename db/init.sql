--
-- PostgreSQL database dump
--

-- Dumped from database version 16.0
-- Dumped by pg_dump version 16.0

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.admins (
    user_id integer NOT NULL,
    user_name text NOT NULL
);


ALTER TABLE public.admins OWNER TO postgres;

--
-- Name: questions_answers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.questions_answers (
    qa_id integer NOT NULL,
    topic_id integer,
    question text NOT NULL,
    answer text NOT NULL
);


ALTER TABLE public.questions_answers OWNER TO postgres;

--
-- Name: questions_answers; Type: TABLE; Schema: public; Owner: postgres
--
--
-- Name: questions_answers_qa_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.questions_answers_qa_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.questions_answers_qa_id_seq OWNER TO postgres;

--
-- Name: questions_answers_qa_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.questions_answers_qa_id_seq OWNED BY public.questions_answers.qa_id;


--
-- Name: submitted_applications; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.submitted_applications (
    telegram_id integer NOT NULL,
    last_name character varying(255) NOT NULL,
    first_name character varying(255) NOT NULL,
    country character varying(255),
    date_of_birth date,
    contact_phone character varying(20),
    email character varying(255),
    previous_education_country character varying(255),
    passport_file character varying(255),
    passport_text text,
    passport_translation_file character varying(255),
    passport_translation_text text,
    visa_application_form_file character varying(255),
    visa_application_form_text text,
    bank_statement_file character varying(255),
    bank_statement_text text,
    comments text,
    status character varying(20),
    application_for_self integer
);


ALTER TABLE public.submitted_applications OWNER TO postgres;

--
-- Name: topics; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.topics (
    topic_id integer NOT NULL,
    topic_name text NOT NULL
);


ALTER TABLE public.topics OWNER TO postgres;

--
-- Name: topics_topic_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.topics_topic_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.topics_topic_id_seq OWNER TO postgres;

--
-- Name: topics_topic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.topics_topic_id_seq OWNED BY public.topics.topic_id;


--
-- Name: users_lang; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users_lang (
    user_id integer NOT NULL,
    user_lang text
);


ALTER TABLE public.users_lang OWNER TO postgres;

--
-- Name: questions_answers qa_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions_answers ALTER COLUMN qa_id SET DEFAULT nextval('public.questions_answers_qa_id_seq'::regclass);


--
-- Name: topics topic_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topics ALTER COLUMN topic_id SET DEFAULT nextval('public.topics_topic_id_seq'::regclass);


--
-- Data for Name: admins; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.admins (user_id, user_name) FROM stdin;
530261570	Седиров Арсен
\.


--
-- Data for Name: questions_answers; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.questions_answers (qa_id, topic_id, question, answer) FROM stdin;
1	1	How do I apply to Ural Federal University?	Please find out all information concerning the application to UrFU [here](https://urfu.ru/en/international/information-for-prospective-international-students/application-information/).
2	1	What are the entry requirements and application deadlines?	Please read about the entry requirements and application deadlines for the type of program you wish to apply for [here](https://urfu.ru/en/international/information-for-prospective-international-students/entry-requirements/).
3	1	Do I have to speak Russian to study at UrFU?	Speaking Russian is *not* required if you apply for one of our [English-taught Master''s programs](https://urfu.ru/en/studies/programs-and-courses/masters-degree-programs-in-english/), [Doctoral (PhD) programs in English](https://urfu.ru/en/international/programs-and-courses/postgraduate-programs-in-english/) or *short-term summer and winter schools* held in English. \nFor [Master''s programs in Russian](https://urfu.ru/en/international/programs-and-courses/mastersinrussian/) and all [Bachelor''s programs](https://urfu.ru/en/international/programs-and-courses/bachelors-degree-programs-in-russian/), Russian language is required. You can learn Russian at [UrFU Russian Language School](https://rfl.urfu.ru/en/).
4	1	Why don''t the Admission Managers reply to my emails?	Managers have to respond to hundreds of emails every day, so it may take *at least 24 hours* to process your request. Please note that Ekaterinburg is in the *GMT + 5* time zone. Please also note that Saturdays and Sundays are officially non-working days in Russia.
7	2	Can I study on a Russian-taught program?	Studying on a Russian-taught program is possible after completing a preparatory year at the [UrFU Russian Language School](https://rfl.urfu.ru/en/) (or any other accredited Russian language school) and receiving a Russian language certificate.
30	8	How does the Russian higher education system work?	The Russian education system is a multistage process that encourages lifelong learning. This system includes compulsory general education (kindergartens and schools) and professional education (colleges, technical schools, universities). In turn, professional education is divided into secondary and higher education. Professional development and retraining programs are considered the final educational stage.\n\n*Bachelor''s and Specialist''s degrees*\n\nRussia has adopted the Bologna Process, which is a three-cycle educational system consisting of an undergraduate degree (4 years) and a Master''s degree (2 years) During their Bachelor''s degree, students gain a broad understanding of their chosen specialty, with the opportunity to explore various areas of interest. Graduates with a Bachelor''s degree can immediately begin working in their chosen profession, or they can continue their studies at the next level. Additionally, some universities still offer specialist programs, a level that only exists in Russia. Specialist programs provide a more focused education over 5–6 years that emphasizes practical skills.\n\n*Master''s degree*\n\nThe Master''s Degree is the second stage of higher education in the Bologna Process. To be admitted into a Master''s program, applicants must have a Bachelor''s or Specialist''s degree. These programs are generally more research-oriented, providing students with an in-depth understanding of their chosen subject. Master''s programs usually last two years and focus mainly on the Student''s ability to independently grasp the material.\n\n*Postgraduate program*\n\nPostgraduate programs are mainly for training research and teaching personnel. To be admitted into a postgraduate program, applicants must have a Master''s or Specialist''s Degree. These programs include educational aspects, pedagogical and practical work, and research. Graduate students must choose a scientific area and research topic for their dissertation. In-person, full-time programs are at least 3 years, while part-time programs are at least 4. At the end of the program, successful candidates receive a postgraduate diploma with a qualification (Researcher, Research Teacher). After defending their dissertation, graduate students are awarded a Candidate of Science degree, which is the first of two doctoral-level scientific degrees. Candidates of Sciences are then eligible for the Doctor of Sciences degree (the second doctoral-level scientific degree), which is awarded following the defense of a doctoral dissertation.\n\n For more information, visit the [Education in Russia](https://education-in-russia.com/how-to-proceed/education-levels) web page.
25	7	Where is Ekaterinburg?	Ekaterinburg is located on the border between Europe and Asia in the Ural Federal District. It is the 4th largest city in Russia with a population of nearly 1.5 million.
20	6	How many people are there in a dormitory room?	There are usually two or three people living in one dormitory room.
29	7	Can I visit other Russian cities or other countries while I study at UrFU?	Yes, you can. However, please note that, according to the Russian legislation, whenever you intend to go outside Ekaterinburg for any period of time during your studies OR holidays, you MUST inform the International Student Support Office (19 Mira Street, office GUK-109) at least 48 hours prior to your trip. The managers will consult you on further steps.
28	7	What is the weather like in Ekaterinburg?	Ekaterinburg is located in a mid-continental climate zone with distinct seasons. Weather conditions are variable and can sometimes be very unstable and unpredictable. The average temperature in winter is from -15℃ to -25℃ and in summer it is from 20℃ to 30℃.
27	7	What is there to see and do in Ekaterinburg?	Please see the website of the Ekaterinburg Guide Center: http://www.ekaterinburgguide.com/eng/
6	2	Does UrFU offer English-taught programs?	Yes. UrFU offers a number of [English-taught Master''s programs](https://urfu.ru/en/studies/programs-and-courses/masters-degree-programs-in-english/), *English-taught Doctoral Programs* and *Short-term Schools.*\n*Please note that UrFU also offers* [Bachelor''s programs taught 50% in English](https://urfu.ru/en/studies/programs-and-courses/bachelors-degree-programs-in-english/).
8	2	Does UrFU offer MBA programs for international students?	Learn more about [MBA courses at UrFU](https://mba.mba-urfu.com/) (in Russian).
10	3	What are the tuition fees at UrFU?	Tuition fees at Ural Federal University depend on the program you choose. Please check the list of available programs in the [Programs and Courses](https://urfu.ru/en/international/programs-and-courses/) section. All information regarding tuition fees can be found in this section.
13	4	I applied for a visa invitation a few days/weeks ago and still haven''t received it. What should I do in this situation?	There is nothing to worry about. The invitation is issued by the Ministry of Foreign Affairs of the Russian Federation and takes *at least 30 days* to be prepared. If you do not receive your invitation 40 days after submitting the application, please contact the Admissions Office at admission@urfu.ru.
22	6	What is the address of my dormitory?	The address of your dormitory will be written in the voucher for the dormitory, which you will receive in the International Students Adaptation Center. You can find its address [here](https://vk.com/adaptationurfu).
15	5	Can anyone meet and assist me at the airport when I arrive?	Yes! A Buddy student can meet you at the airport or train station and take you to the campus. All taxi rides must be paid for by you, including your Buddy''s ride to the airport. Please fill in the [Arrival Form](https://urfu.ru/en/international/information-for-prospective-international-students/application-information/arrival-form/) *at least 10 days prior to your arrival.*\n*Contacts:*\n--- adaptation@urfu.ru\n--- Mr. Iakov Firsov: iakov.firsov@urfu.ru
33	9	Can I do any sports/music/dancing at UrFU?	*Ural Federal University Sports Club* organizes sports activities, events, and works with university teams. They have 32 sports teams and host the New Year''s podium to award the best athletes.\n\n*Student Art Center* offers opportunities for creative individuals to continue and develop their talents. They host events, produce performances, and have various creative groups.\n\n*UrFU Welcome Center* is a student tourism cluster that offers opportunities for traveling, cultural events, and promotion of Urals culture and history.\n\n*The Creative Opportunity Fair* is held at the beginning of the academic year to showcase creative activities at the university. Students can join different creative teams or even start their own.\n\n*UrFU ESports league (USL)* organizes championships in cybersports and programming, providing a platform for students to participate in esports events.\n\n*Rifey Tourist Club* focuses on different types of tourism, including mountain, water, hiking, and skiing tours. They train athletes and organize competitions and training sessions for students.\n\n*Romantic Tourist Club* is a meeting place for travel enthusiasts since 1951. They organize tourist meetings, tours, hikes, and cultural events.\n\n*Lingua-T Linguistic Theater* is a unique polyglot theater that performs plays in foreign languages with consecutive translations into Russian.\n\n[For more info](https://urfu.ru/en/prospective-students/faq/).
31	8	What is the Point-Grade System (БРС)?	The Point-Grade System is a digital mark for evaluating students learning activities and achievements. The Point-Grade System is a system for determining the level of student success based on the cumulative principle of assessing academic performance and its results.
14	4	How do I extend my visa?	Please visit the GUK-109 office *at least six weeks prior to the expiration date of your current visa.* You will be consulted on the visa extension procedures.
9	3	Are there any scholarships available for international students?	Each year, the Russian government allocates a certain number of state-funded places for studies at Russian universities for international students. You can apply for the Scholarship of the Ministry of Science and Higher Education of the Russian Federation at the [website of the Ministry](https://education-in-russia.com/). If you have any problems with the registration, please check [this instruction](https://urfu.ru/en/international/information-for-prospective-international-students/russian-government-scholarship/).
11	3	Are there any discounts?	The University has a flexible tuition fee discount system:\n--- a 4 % discount on advance payment (for each year of study),\n--- applicants who get 40 and more points at the entrance exam, get a tuition fee discount between 10 and 30% for the entire period of study. \nYou can contact the UrFU Admission Team at admission@urfu.ru or on +7 (992) 000-77-03 (WhatsApp) for more information.
5	2	What can I study at UrFU?	Ural Federal University offers hundreds of educational programs at the undergraduate (Bachelor''s), graduate (Master''s) and PhD levels, as well as short-term programs and Russian language courses. You can choose from the following programs:\n*Russian-taught:*\n--- [Bachelor''s programs](https://urfu.ru/en/international/programs-and-courses/bachelors-degree-programs-in-russian/)\n--- [Master''s programs](https://urfu.ru/en/international/programs-and-courses/mastersinrussian/)\n--- [Doctoral programs](https://urfu.ru/en/international/programs-and-courses/postgraduate-programs-in-russian/)\n*English-taught:*\n--- [Master''s programs](https://urfu.ru/en/studies/programs-and-courses/masters-degree-programs-in-english/)\n--- Doctoral programs\n--- Short-term programs\n*Preparatory courses:*\n--- Learn Russian\n*Please note that UrFU does not offer English-taught Bachelor''s (4-year, undergraduate) programs. All Bachelor''s programs are taught in the Russian medium.*
12	3	Are there any additional fees?	Please keep in mind that Ural Federal University *does not claim* any deposits for tuition fees or charge any additional registration fees for internal admission procedures (including application*, admission interviews, expert evaluation of educational documents etc).\nIf you are applying to a university through recruitment agencies or private intermediaries who may require payment for their services — for these transactions the University has *no financial liability.*\n\\*with the exception of the Stamp Duty fee (800 RUB) charged by the Ministry of Foreign Affairs for document processing for certain visa types.
17	5	What should I do when I first arrive to UrFU?	As soon as you arrive, please visit the Admissions Office (19 Mira Street, office GUK-109). You will be instructed on the further steps. Also, you can find detailed instructions and check-lists in our [International Student Handbook](https://urfu.ru/en/prospective-students/how-to-apply/international-student-handbook/).\nIP: We also have a mobile app named *UrFU Guide*, which contains interactive checklists, campus navigation and a lot of other useful features and information!\n\nDownload: [iOS](https://apps.apple.com/ru/app/urfu-guide/id1097001738?l=en) | [Android](https://play.google.com/store/apps/details?id=com.ftsoft.urfuguide&hl=en*US)
19	6	Does UrFU provide accommodation for international students?	All international students of UrFU receive a place in one of the campus dormitories. The approximate accommodation fee is 1800 rubles per month. You can find more info [here](https://urfu.ru/en/current-students/accommodation/).
21	6	Will my dormitory room be ready when I arrive?	Every student has the right to get a room in an university dormitory if places are available or free. However, please keep in mind that, according to the legislation, every student must undergo a standard *medical examination* before they are allowed to check into a university dormitory room. Since the medical examination may take up more than one day, *you might need to book a hotel room* for this time. Should you need any help with booking, please contact our Buddy System coordinators.\n\n*Contacts:*\n\nadaptatiom.urfu.ru, https://vk.com/adaptationurfu
23	6	What do I need to do before I check in?	According to the legislation, all students must undergo a standard *medical examination* before checking into a dormitory room. You will receive all required information in the Admissions Office (19 Mira Street, office GUK-109).\n\n*Please have the following documents with you:*\n\n--- Recent photofluorography\n--- Vaccination certificate/other vaccination info\n--- Description of your general state of health from your physician\n--- Other medical certificates that might be necessary
24	6	Are there any other accommodation options?	If you prefer renting a flat to living in a dormitory, our Student Union can help you find a suitable paid accommodation and – if necessary – a flatmate.\n\n*Contacts:*\n\n+7 (343) 375-45-18
26	7	What is the cost of living in Ekaterinburg?	For a comfortable living in Ekaterinburg you will need the following amount of money (per person per month):\n\n--- Food: 10,000 - 15,000 rubles\n--- Accommodation: about 1,500 rubles if you live in an UrFU dormitory, 15,000 - 20,000 rubles for a one-room apartment (less if you live with your roommate(s))\n--- Transport: 1,700 rubles for unlimited urban transport pass\n--- Entertainment: 5,000 - 10,000 rubles\nPlease note that the above figures are average and will vary depending on your needs and habits.
32	8	When do lectures begin and finish?	All the information about dates can be found [here](https://urfu.ru/en/current-students/academic-planning/academic-calendar/).
34	9	What else can I do at UrFU?	For more information about extracurricular activities check this [page](https://urfu.ru/en/activities/).
18	5	Where can I stay when I arrive?	UrFU offers on-campus accommodation for all international students for a price of just 1800 rubles per month. However, please keep in mind that, according to the legislation, every student must undergo a standard *medical examination* before they are allowed to check into a university dormitory room. Since the medical examination may take up more than one day, *you might need to book a hotel room* for this period of time. Should you need any help with booking, please contact our Buddy-coordinator.\n\nContacts:\n\nMr. Iakov Firsov\niakov.firsov@urfu.ru
16	5	How do I get to the University campus from the airport on my own?	*Taxi*\nThe easiest and most convenient way to get to the university campus is to take a taxi. You can order a taxi through such apps as *Uber* or *Yandex Taxi*. The cost of the trip ranges from 400 to 1,000 rubles, depending on the traffic congestion.\n\n*From:*\n*Koltsovo International Airport*\nМеждународный аэропорт Кольцово\n\n*To:*\n*19 Mira Street, Ekaterinburg*\nУлица Мира, 19, Екатеринбург\n\n\n*Public Transport*\nAlthough we strongly advise you to take a taxi, you can still reach UrFU campus by public transport. The fare for one ride is 33 rubles. Tickets are bought inside the vehicles.\n\n*From:*\n*Koltsovo Airport bus stop*\nОстановка Кольцово\n*Line:* Bus №*1*\n\n*Change at:*\n*Sibirskiy Trakt bus stop* \n Остановка Сибирский тракт \n *Line:* Bus №*18* \n\n *To:* \n *Ural Federal University bus stop* \n Остановка Уральский федеральный университет \n\n\n *TIP:* There are some useful mobile apps that will help you get around in Ekaterinburg: \n *2GIS:* Interactive city map with search and navigation (works offline) \n [IOS](https://apps.apple.com/ru/app/2гис-карты-навигатор-места/id481627348) | [Android](https://play.google.com/store/apps/details?id=com.dss.doublegis) \n *Hubb:* Real-time public transport tracker \n [IOS](https://apps.apple.com/ru/app/hubb-городской-транспорт/id1231297352) | [Android](https://play.google.com/store/apps/details?id=com.hubbmap)
\.


--
-- Data for Name: submitted_applications; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.submitted_applications (last_name, first_name, country, date_of_birth, contact_phone, email, previous_education_country, passport_file, passport_translation_file, visa_application_form_file, bank_statement_file, comments, status, application_for_self, telegram_id) FROM stdin;
\.


--
-- Data for Name: topics; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.topics (topic_id, topic_name) FROM stdin;
1	Application and Admission
2	Study Programs
3	Fees and Scholarships
4	Visa
5	Arrival to Ekaterinburg
6	Accommodation
7	Life in Ekaterinburg
8	Studies
9	Extracurricular
\.


----
---- Data for Name: users_lang; Type: TABLE DATA; Schema: public; Owner: postgres
----
--
--COPY public.users_lang (user_id, user_lang) FROM stdin;
--530261570	en
--648110443	ru
--\.


--
-- Name: questions_answers_qa_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.questions_answers_qa_id_seq', 1, true);


--
-- Name: topics_topic_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.topics_topic_id_seq', 3, true);


--
-- Name: admins admins_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.admins
    ADD CONSTRAINT admins_pkey PRIMARY KEY (user_id);


--
-- Name: questions_answers questions_answers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions_answers
    ADD CONSTRAINT questions_answers_pkey PRIMARY KEY (qa_id);


--
-- Name: submitted_applications submitted_applications_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.submitted_applications
    ADD CONSTRAINT submitted_applications_pkey PRIMARY KEY (telegram_id);


--
-- Name: topics topics_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.topics
    ADD CONSTRAINT topics_pkey PRIMARY KEY (topic_id);


--
-- Name: users_lang users_lang_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users_lang
    ADD CONSTRAINT users_lang_pkey PRIMARY KEY (user_id);

--
-- Name: questions_answers questions_answers_topic_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.questions_answers
    ADD CONSTRAINT questions_answers_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(topic_id);

CREATE TABLE IF NOT EXISTS public.questions_files
(
    file_id SERIAL PRIMARY KEY,
    qa_id integer,
    file_name text COLLATE pg_catalog."default" NOT NULL,
    file_path text COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT questions_files_qa_id_fkey FOREIGN KEY (qa_id)
        REFERENCES public.questions_answers (qa_id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
);

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.questions_files
    OWNER to postgres;
