"""
generate_questions.py
Membuat bank soal EPT lengkap: 180 soal (60 Listening + 60 Structure + 60 Reading)
Output: bank_soal_ept.csv (siap upload ke sistem)
"""

import csv, random, os

# ─────────────────────────────────────────────────────────────────────────────
#  BANK SOAL LISTENING (60 soal)
#  Format: question, option_a, option_b, option_c, option_d, correct (0=A), script
# ─────────────────────────────────────────────────────────────────────────────
LISTENING = [
    # MUDAH (1–20)
    {
        "question": "What does the woman want to do this weekend?",
        "options": ["Go shopping", "Visit her parents", "Stay at home", "Travel abroad"],
        "correct": 1,
        "script": "Woman: I'm planning to visit my parents this weekend. It's been a while since I last saw them.",
    },
    {
        "question": "Where is the man going?",
        "options": ["To the library", "To the gym", "To the office", "To the market"],
        "correct": 1,
        "script": "Man: I need to work out. I haven't been to the gym in two weeks, so I'm heading there now.",
    },
    {
        "question": "What is the woman's problem?",
        "options": ["She lost her keys", "She missed the bus", "She forgot her wallet", "She is late for work"],
        "correct": 2,
        "script": "Woman: Oh no! I left home without my wallet. I can't pay for anything today.",
    },
    {
        "question": "What does the man suggest?",
        "options": ["Taking a taxi", "Walking to work", "Calling a friend", "Taking the subway"],
        "correct": 3,
        "script": "Man: Traffic is terrible today. I think taking the subway would be much faster than driving.",
    },
    {
        "question": "What time does the meeting start?",
        "options": ["At 9:00 AM", "At 10:00 AM", "At 2:00 PM", "At 3:00 PM"],
        "correct": 1,
        "script": "Woman: Don't forget, the team meeting starts at ten o'clock sharp. Please be on time.",
    },
    {
        "question": "What is the man ordering?",
        "options": ["A sandwich and juice", "A burger and coffee", "A salad and water", "A pasta and tea"],
        "correct": 1,
        "script": "Man: I'd like a cheeseburger and a large coffee, please. That's all for me.",
    },
    {
        "question": "Why is the woman calling?",
        "options": ["To confirm a reservation", "To cancel an appointment", "To ask for directions", "To make a complaint"],
        "correct": 0,
        "script": "Woman: Hello, I'm calling to confirm my reservation for two people on Friday evening at seven.",
    },
    {
        "question": "What does the man want the woman to do?",
        "options": ["Return a book", "Lend him money", "Help him move", "Proofread his report"],
        "correct": 3,
        "script": "Man: I've just finished writing my report. Could you read through it and check for any errors before I submit it?",
    },
    {
        "question": "How does the woman feel about the presentation?",
        "options": ["Excited", "Nervous", "Bored", "Angry"],
        "correct": 1,
        "script": "Woman: I have to present in front of fifty people tomorrow. My hands are already shaking just thinking about it.",
    },
    {
        "question": "What is the weather like today?",
        "options": ["Sunny and hot", "Cold and windy", "Rainy and cloudy", "Warm and humid"],
        "correct": 2,
        "script": "Man: Don't forget your umbrella. It's been raining since morning and the sky looks really cloudy.",
    },
    {
        "question": "What did the woman buy at the store?",
        "options": ["Bread and milk", "Vegetables and fruits", "Meat and fish", "Snacks and drinks"],
        "correct": 1,
        "script": "Woman: I just got back from the market. I bought a lot of fresh vegetables and some fruits for the week.",
    },
    {
        "question": "What is the man's job?",
        "options": ["A teacher", "A doctor", "An engineer", "A chef"],
        "correct": 2,
        "script": "Man: I work on designing bridges and buildings. Being a civil engineer is challenging but very rewarding.",
    },
    {
        "question": "What does the woman recommend?",
        "options": ["A new restaurant", "A movie theater", "A book store", "A coffee shop"],
        "correct": 0,
        "script": "Woman: You should try the new Italian restaurant downtown. The pasta there is absolutely amazing.",
    },
    {
        "question": "What is the man's plan for tomorrow?",
        "options": ["Work overtime", "Visit a museum", "Play football", "Study for an exam"],
        "correct": 3,
        "script": "Man: I have a big exam on Thursday, so I'll be spending all day tomorrow reviewing my notes and studying.",
    },
    {
        "question": "How many people are coming to the party?",
        "options": ["About ten", "About twenty", "About thirty", "About fifty"],
        "correct": 1,
        "script": "Woman: I've sent invitations to all my friends. Around twenty people said they're coming to the party.",
    },
    {
        "question": "What did the man forget?",
        "options": ["His phone", "His passport", "His ticket", "His bag"],
        "correct": 2,
        "script": "Man: I got to the station and realized I didn't have my ticket. I had to rush back home to get it.",
    },
    {
        "question": "Where did the woman grow up?",
        "options": ["In the city", "In the countryside", "Near the ocean", "In the mountains"],
        "correct": 2,
        "script": "Woman: I spent my childhood near the beach. I used to swim in the ocean every single day.",
    },
    {
        "question": "What sport does the man play?",
        "options": ["Basketball", "Tennis", "Football", "Swimming"],
        "correct": 1,
        "script": "Man: I've been playing tennis since I was twelve. I practice at the club every weekend.",
    },
    {
        "question": "What does the woman think about the movie?",
        "options": ["It was excellent", "It was boring", "It was too long", "It was confusing"],
        "correct": 2,
        "script": "Woman: The story was interesting, but honestly the movie was way too long. Three hours is just too much.",
    },
    {
        "question": "How does the man travel to work?",
        "options": ["By car", "By bicycle", "By bus", "On foot"],
        "correct": 1,
        "script": "Man: I cycle to work every morning. It takes about twenty minutes and I get my exercise at the same time.",
    },
    # SEDANG (21–40)
    {
        "question": "What is the main topic of their conversation?",
        "options": ["Finding a new apartment", "Renovating the kitchen", "Buying new furniture", "Moving to another city"],
        "correct": 0,
        "script": "Woman: The rent in my neighborhood has gone up so much. I'm thinking about looking for a new place. Man: That's a good idea. I can help you search online for available apartments.",
    },
    {
        "question": "What can be inferred about the man?",
        "options": ["He has never traveled abroad", "He prefers trains to planes", "He travels frequently for work", "He is afraid of flying"],
        "correct": 2,
        "script": "Man: This is my fourth business trip this month. I'm starting to feel exhausted from all the traveling.",
    },
    {
        "question": "What will the woman probably do next?",
        "options": ["Call the manager", "Leave the store", "Ask for a refund", "Try a different size"],
        "correct": 2,
        "script": "Woman: This jacket has a defect — the zipper is completely broken. I only bought it two days ago. I need to speak to someone about getting my money back.",
    },
    {
        "question": "What does the man imply about his colleague?",
        "options": ["She is very hardworking", "She often arrives late", "She is about to quit", "She recently got promoted"],
        "correct": 1,
        "script": "Man: Sarah has missed the morning briefing three times this week. The boss is starting to notice.",
    },
    {
        "question": "What problem does the woman mention?",
        "options": ["Her computer crashed", "The internet is slow", "The printer is broken", "The software has a bug"],
        "correct": 2,
        "script": "Woman: I need to submit this document by noon, but the printer keeps jamming. Every time I try, the paper gets stuck inside.",
    },
    {
        "question": "What does the man say about the new policy?",
        "options": ["He strongly supports it", "He finds it unnecessary", "He thinks it needs improvement", "He is completely neutral"],
        "correct": 2,
        "script": "Man: The policy is a step in the right direction, but there are a few areas that still need to be revised before it's fully effective.",
    },
    {
        "question": "Why is the woman unable to attend the conference?",
        "options": ["She has another meeting", "She is traveling overseas", "She is not feeling well", "She wasn't invited"],
        "correct": 2,
        "script": "Woman: I woke up with a fever this morning. There is no way I can make it to the conference today.",
    },
    {
        "question": "What does the conversation suggest about the project?",
        "options": ["It is ahead of schedule", "It has been completed", "It is facing delays", "It was cancelled"],
        "correct": 2,
        "script": "Man: We've had several unexpected issues this week. I'm worried we won't be able to meet the original deadline. Woman: We should notify the client as soon as possible.",
    },
    {
        "question": "What is the woman's opinion of the new manager?",
        "options": ["She respects his experience", "She thinks he is too strict", "She finds him approachable", "She is unsure about him"],
        "correct": 3,
        "script": "Woman: He's only been here for two weeks. It's still too early to form a proper opinion about his leadership style.",
    },
    {
        "question": "What will the man do after the meeting?",
        "options": ["Send a report to the director", "Revise the budget proposal", "Call an overseas client", "Take the rest of the day off"],
        "correct": 0,
        "script": "Man: Once the meeting wraps up, I need to put together a summary and send it directly to the director before end of day.",
    },
    {
        "question": "What is the announcement about?",
        "options": ["A store closure", "A new product launch", "A seasonal sale", "A change in store hours"],
        "correct": 2,
        "script": "Announcement: Attention all shoppers. Our annual end-of-year sale begins this Friday. All items will be discounted by up to fifty percent for one week only.",
    },
    {
        "question": "What does the woman suggest they do about the situation?",
        "options": ["Ignore it completely", "Report it to authorities", "Handle it internally", "Postpone the decision"],
        "correct": 2,
        "script": "Woman: I don't think we need to involve anyone outside the company. We can resolve this among ourselves if we communicate properly.",
    },
    {
        "question": "What does the man ask the woman to prepare?",
        "options": ["A financial summary", "A list of attendees", "A presentation slide", "A draft contract"],
        "correct": 0,
        "script": "Man: Before the board meeting on Thursday, I need you to compile the quarterly financial summary for the past three months.",
    },
    {
        "question": "What can be inferred about the company?",
        "options": ["It is expanding rapidly", "It recently lost a client", "It is facing a budget cut", "It hired many new employees"],
        "correct": 2,
        "script": "Woman: We've been asked to reduce spending in every department. Even business travel has been restricted unless absolutely necessary.",
    },
    {
        "question": "What does the speaker say about the training program?",
        "options": ["It is mandatory for all staff", "It has been postponed", "It was very effective", "It will be conducted online"],
        "correct": 3,
        "script": "Speaker: Due to recent developments, this year's training will be delivered entirely online through our learning management system.",
    },
    {
        "question": "What is the relationship between the two speakers?",
        "options": ["Classmates", "Colleagues", "Doctor and patient", "Shopkeeper and customer"],
        "correct": 1,
        "script": "Man: Did you review the proposal I sent yesterday? Woman: Yes, I made some comments. Let's go through them together at the office.",
    },
    {
        "question": "What does the woman want to know?",
        "options": ["The price of a product", "The store's return policy", "The opening hours", "The location of the store"],
        "correct": 1,
        "script": "Woman: I purchased this item last week and it stopped working. I wanted to ask — what is your policy on returning defective products?",
    },
    {
        "question": "How does the man feel about the job offer?",
        "options": ["He is very enthusiastic", "He is undecided", "He has rejected it", "He has already accepted it"],
        "correct": 1,
        "script": "Man: The salary is good, but the commute would be two hours each way. I'm still weighing the pros and cons before making a decision.",
    },
    {
        "question": "What is the purpose of the phone call?",
        "options": ["To reschedule a delivery", "To track an order", "To place a new order", "To file a complaint"],
        "correct": 0,
        "script": "Woman: Hello, I have a delivery scheduled for tomorrow morning, but something came up. Is it possible to move it to the afternoon instead?",
    },
    {
        "question": "What does the announcement say about the flight?",
        "options": ["It has been cancelled", "It is boarding now", "It has been delayed", "It has landed early"],
        "correct": 2,
        "script": "Announcement: We regret to inform passengers of flight GA-217 to Bali that the flight will be delayed by approximately ninety minutes due to weather conditions.",
    },
    # SULIT (41–60)
    {
        "question": "What does the man imply by saying 'That ship has sailed'?",
        "options": ["The deadline has passed", "The project was cancelled", "The meeting was moved", "The team has left"],
        "correct": 0,
        "script": "Man: I wish we had addressed this problem earlier. But that ship has sailed — we'll have to deal with the consequences now.",
    },
    {
        "question": "What can be concluded from the conversation?",
        "options": ["The merger was successful", "The negotiations have broken down", "The deal is still being reviewed", "Both parties are satisfied"],
        "correct": 1,
        "script": "Woman: We haven't been able to agree on the terms even after six rounds of discussion. Man: I know. It looks like we may have to walk away from this deal entirely.",
    },
    {
        "question": "What is the underlying message of the speaker's talk?",
        "options": ["Technology is replacing human workers", "Innovation requires collaboration", "Remote work reduces productivity", "Management skills are outdated"],
        "correct": 1,
        "script": "Speaker: No breakthrough has ever been achieved by a single person working in isolation. History shows us time and again that the most transformative ideas emerge when diverse minds come together with a shared purpose.",
    },
    {
        "question": "What does the woman mean when she says 'It's not rocket science'?",
        "options": ["The task is very simple", "The task requires expertise", "Science is not involved", "The instructions are unclear"],
        "correct": 0,
        "script": "Woman: I don't understand why the team is struggling with this. The process has been documented step by step — it's not rocket science.",
    },
    {
        "question": "What concern does the man raise about the proposal?",
        "options": ["The timeline is unrealistic", "The budget is insufficient", "The team lacks experience", "The market is too competitive"],
        "correct": 0,
        "script": "Man: I appreciate the ambition here, but I'm skeptical. Completing all of these milestones within four months seems extremely optimistic given our current resources.",
    },
    {
        "question": "What is the speaker's main argument?",
        "options": ["Urban planning needs reform", "Public transport is inefficient", "Green spaces improve mental health", "Housing prices are rising"],
        "correct": 2,
        "script": "Speaker: Studies consistently demonstrate that people living near parks and natural environments report significantly lower levels of stress and higher overall life satisfaction.",
    },
    {
        "question": "What does the woman imply about her supervisor?",
        "options": ["He micromanages his team", "He delegates too much", "He is rarely available", "He shows favouritism"],
        "correct": 0,
        "script": "Woman: He reviews every single email I send before it goes out. Sometimes I feel like he doesn't trust me to handle even minor communications independently.",
    },
    {
        "question": "What does the conversation reveal about company culture?",
        "options": ["Employees rarely receive feedback", "The hierarchy is very flat", "Work-life balance is prioritized", "Competition among staff is high"],
        "correct": 2,
        "script": "Man: They actually encourage people to leave at five. Nobody expects you to stay late unless there's a real emergency. Woman: That's incredibly rare in this industry.",
    },
    {
        "question": "What strategy does the woman propose to address declining sales?",
        "options": ["Cutting prices across the board", "Launching a loyalty rewards program", "Increasing the advertising budget", "Entering a new market segment"],
        "correct": 1,
        "script": "Woman: Rather than just reducing prices, I think we should focus on retaining existing customers through a well-designed loyalty program that rewards repeat purchases.",
    },
    {
        "question": "What does the professor suggest about the research methodology?",
        "options": ["It lacks sufficient data", "It relies too heavily on surveys", "It needs a control group", "It should use qualitative methods"],
        "correct": 2,
        "script": "Professor: Your findings are interesting, but without a proper control group, it's difficult to attribute the results solely to the variable you're testing. You need to account for confounding factors.",
    },
    {
        "question": "What issue does the speaker raise about the new regulation?",
        "options": ["It is too vague to enforce", "It places too much burden on small businesses", "It contradicts existing laws", "It was passed without public consultation"],
        "correct": 1,
        "script": "Speaker: While the intention behind this regulation is sound, the compliance costs are particularly problematic for smaller enterprises that don't have the resources of larger corporations.",
    },
    {
        "question": "What does the man mean when he says the decision was 'a double-edged sword'?",
        "options": ["The decision was made by two people", "The decision has both benefits and drawbacks", "The decision was difficult to implement", "The decision reversed a previous policy"],
        "correct": 1,
        "script": "Man: Expanding into that market was really a double-edged sword. We gained significant revenue, but we also took on risks that are now proving very difficult to manage.",
    },
    {
        "question": "What can be inferred about the research findings?",
        "options": ["They support the original hypothesis", "They are consistent with previous studies", "They challenge widely accepted assumptions", "They require further peer review"],
        "correct": 2,
        "script": "Researcher: These results are quite surprising. They directly contradict what the field has generally accepted for the past two decades, which means we need to completely rethink our models.",
    },
    {
        "question": "What does the woman suggest about the team's communication?",
        "options": ["Meetings are too frequent", "Emails are being overlooked", "Information is not shared transparently", "Feedback is overly critical"],
        "correct": 2,
        "script": "Woman: The problem is that different departments are making decisions without informing each other. There's a serious lack of transparency, and it's causing unnecessary duplication of effort.",
    },
    {
        "question": "What is the speaker's attitude toward the current education system?",
        "options": ["Fully supportive", "Cautiously optimistic", "Strongly critical", "Completely indifferent"],
        "correct": 2,
        "script": "Speaker: The system continues to prioritize rote memorization over critical thinking. We are producing graduates who can recite facts but struggle profoundly when asked to solve real-world problems.",
    },
    {
        "question": "What does the man suggest could be a long-term consequence of the decision?",
        "options": ["A decrease in employee morale", "Loss of key partnerships", "A shift in company culture", "A reduction in product quality"],
        "correct": 2,
        "script": "Man: If we keep restructuring the organization like this every two years, people will lose a sense of stability. Eventually it will fundamentally alter how people identify with the company and its values.",
    },
    {
        "question": "How does the woman respond to the criticism?",
        "options": ["She dismisses it entirely", "She partially agrees with it", "She becomes defensive", "She redirects the conversation"],
        "correct": 1,
        "script": "Woman: Some of those points are valid — I'll admit the timeline was overly ambitious. However, I do think the core strategy was sound, even if the execution could have been better.",
    },
    {
        "question": "What does the consultant imply about the company's future?",
        "options": ["It will grow steadily", "It faces significant risk", "It should consider merging", "It is in a stable position"],
        "correct": 1,
        "script": "Consultant: Based on the data I've reviewed, if the company continues on its current trajectory without making strategic adjustments, it will be in a very precarious position within eighteen months.",
    },
    {
        "question": "What distinction does the speaker draw between leadership and management?",
        "options": ["Leaders are born, managers are trained", "Leadership focuses on vision, management on execution", "Managers deal with people, leaders deal with strategy", "Leadership is long-term, management is reactive"],
        "correct": 1,
        "script": "Speaker: Management is about ensuring the right processes are followed and targets are met. Leadership, on the other hand, is about inspiring people toward a future that doesn't yet exist.",
    },
    {
        "question": "What does the woman ultimately conclude about the situation?",
        "options": ["Immediate action is needed", "The situation will resolve itself", "External help should be sought", "The root cause must be identified first"],
        "correct": 3,
        "script": "Woman: We keep addressing the symptoms rather than looking at what's actually causing this. Until we properly diagnose the root of the problem, nothing we do will have a lasting effect.",
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  BANK SOAL STRUCTURE (60 soal)
#  Topics: Tenses, Passive Voice, Conditional, Relative Clause, S-V Agreement,
#          Gerund/Infinitive, Articles, Modals, Comparison, Conjunctions
# ─────────────────────────────────────────────────────────────────────────────
STRUCTURE = [
    # TENSES (1–15)
    {"question": "She ___ English for five years before she moved to London.", "options": ["studies","studied","has studied","had studied"], "correct": 3},
    {"question": "The train ___ when we arrived at the station.", "options": ["already left","has already left","had already left","already leaves"], "correct": 2},
    {"question": "By the time the exam starts, I ___ all the chapters.", "options": ["will review","review","will have reviewed","have reviewed"], "correct": 2},
    {"question": "He ___ in this company since 2015.", "options": ["works","is working","has been working","worked"], "correct": 2},
    {"question": "Water ___ at 100 degrees Celsius.", "options": ["boils","is boiling","has boiled","boiled"], "correct": 0},
    {"question": "When I got home, my mother ___ dinner.", "options": ["cooks","cooked","was cooking","has cooked"], "correct": 2},
    {"question": "They ___ the project by the end of this month.", "options": ["finish","finished","will finish","are finishing"], "correct": 2},
    {"question": "I ___ to the cinema three times this week.", "options": ["go","went","have gone","had gone"], "correct": 2},
    {"question": "She realized she ___ her keys at home.", "options": ["leaves","left","has left","had left"], "correct": 3},
    {"question": "Every morning, he ___ up at six and ___ for a run.", "options": ["wakes / goes","woke / went","has woken / goes","wakes / went"], "correct": 0},
    {"question": "The scientists ___ on this research for over a decade before the breakthrough.", "options": ["work","worked","have worked","had been working"], "correct": 3},
    {"question": "By next year, she ___ her PhD.", "options": ["completes","will complete","will have completed","has completed"], "correct": 2},
    {"question": "I ___ her since we were children.", "options": ["know","knew","have known","had known"], "correct": 2},
    {"question": "The package ___ tomorrow morning.", "options": ["arrives","arrived","will arrive","has arrived"], "correct": 2},
    {"question": "While she ___ a book, the phone rang.", "options": ["reads","read","was reading","has read"], "correct": 2},
    # PASSIVE VOICE (16–25)
    {"question": "The new bridge ___ by the government last year.", "options": ["built","was built","has built","is built"], "correct": 1},
    {"question": "The report ___ by the manager before the meeting.", "options": ["is reviewing","will review","must be reviewed","reviews"], "correct": 2},
    {"question": "A new policy ___ by the board next week.", "options": ["will announce","is announced","will be announced","announced"], "correct": 2},
    {"question": "The injured players ___ to the hospital immediately.", "options": ["took","was taken","were taken","are taking"], "correct": 2},
    {"question": "English ___ as an official language in many countries.", "options": ["spoken","speaks","is spoken","has spoken"], "correct": 2},
    {"question": "The essay should ___ before the deadline.", "options": ["submit","be submitted","submitted","submitting"], "correct": 1},
    {"question": "The new software ___ by the IT team at the moment.", "options": ["is being installed","installs","is installing","has installed"], "correct": 0},
    {"question": "The criminal ___ by the police last night.", "options": ["arrested","was arrested","has arrested","were arrested"], "correct": 1},
    {"question": "The product ___ to more than fifty countries every year.", "options": ["is exported","exports","exported","has exported"], "correct": 0},
    {"question": "It is believed that the ancient city ___ around 3000 BC.", "options": ["founded","has founded","was founded","is founding"], "correct": 2},
    # CONDITIONAL (26–35)
    {"question": "If I ___ rich, I would travel around the world.", "options": ["am","was","were","had been"], "correct": 2},
    {"question": "If you heat water to 100°C, it ___.", "options": ["boils","would boil","boiled","will have boiled"], "correct": 0},
    {"question": "She ___ the job if she had arrived on time.", "options": ["gets","got","would get","would have gotten"], "correct": 3},
    {"question": "If it rains tomorrow, we ___ the picnic.", "options": ["cancel","cancelled","will cancel","would cancel"], "correct": 2},
    {"question": "Had he studied harder, he ___ the exam.", "options": ["passes","would pass","would have passed","had passed"], "correct": 2},
    {"question": "If I were you, I ___ that offer immediately.", "options": ["accept","accepted","will accept","would accept"], "correct": 3},
    {"question": "She could speak French fluently if she ___ it every day.", "options": ["practice","practiced","had practiced","will practice"], "correct": 1},
    {"question": "We would have arrived on time if the traffic ___ so heavy.", "options": ["isn't","wasn't","hadn't been","wouldn't be"], "correct": 2},
    {"question": "If he works harder, he ___ promoted.", "options": ["will get","would get","had gotten","gets"], "correct": 0},
    {"question": "Unless you ___ now, you will miss the flight.", "options": ["leave","left","will leave","would leave"], "correct": 0},
    # RELATIVE CLAUSE (36–43)
    {"question": "The woman ___ is standing over there is my professor.", "options": ["which","whose","who","whom"], "correct": 2},
    {"question": "The book ___ I borrowed from the library was fascinating.", "options": ["who","whom","which","whose"], "correct": 2},
    {"question": "The student ___ father is a doctor won the scholarship.", "options": ["who","whose","which","that"], "correct": 1},
    {"question": "This is the city ___ I was born.", "options": ["which","where","who","that"], "correct": 1},
    {"question": "The man ___ I spoke to yesterday is the new director.", "options": ["who","which","whom","whose"], "correct": 2},
    {"question": "The reason ___ she left the job is still unknown.", "options": ["which","why","when","where"], "correct": 1},
    {"question": "This is the moment ___ everything changed.", "options": ["where","whose","when","which"], "correct": 2},
    {"question": "The company ___ products are sold worldwide is based in Germany.", "options": ["which","who","whose","that"], "correct": 2},
    # SUBJECT-VERB AGREEMENT (44–49)
    {"question": "Neither the students nor the teacher ___ present at the meeting.", "options": ["were","was","are","have been"], "correct": 1},
    {"question": "The news ___ shocking to everyone in the room.", "options": ["were","are","was","have been"], "correct": 2},
    {"question": "Everyone in both classes ___ required to submit the assignment.", "options": ["are","were","is","have been"], "correct": 2},
    {"question": "A number of students ___ absent because of the holiday.", "options": ["was","is","were","has been"], "correct": 2},
    {"question": "The committee ___ unable to reach a decision yesterday.", "options": ["were","is","was","are"], "correct": 2},
    {"question": "Each of the participants ___ given a certificate.", "options": ["were","are","was","have been"], "correct": 2},
    # GERUND / INFINITIVE / MODALS / MISC (50–60)
    {"question": "She is looking forward to ___ her family during the holidays.", "options": ["see","sees","seeing","have seen"], "correct": 2},
    {"question": "He refused ___ the contract without consulting his lawyer.", "options": ["sign","signing","to sign","having signed"], "correct": 2},
    {"question": "You ___ see a doctor. That cough sounds serious.", "options": ["should","would","might","could"], "correct": 0},
    {"question": "She ___ have forgotten the meeting — she never misses one.", "options": ["can't","must","should","would"], "correct": 0},
    {"question": "The more you practice, ___ you become.", "options": ["good","better","the better","the best"], "correct": 2},
    {"question": "Not only ___ he finish the project, but he also exceeded expectations.", "options": ["he did","did he","does he","had he"], "correct": 1},
    {"question": "It is essential that every employee ___ the safety guidelines.", "options": ["follows","follow","followed","following"], "correct": 1},
    {"question": "I ___ rather stay home than go to that party.", "options": ["will","would","should","must"], "correct": 1},
    {"question": "The CEO, along with her senior advisors, ___ attending the summit.", "options": ["are","were","is","have been"], "correct": 2},
    {"question": "Hardly ___ sat down when the fire alarm went off.", "options": ["I had","had I","I have","have I"], "correct": 1},
    {"question": "She suggested ___ the meeting to the following week.", "options": ["to postpone","postponing","postpone","postponed"], "correct": 1},
]

# ─────────────────────────────────────────────────────────────────────────────
#  BANK SOAL READING (60 soal — 12 passage × 5 soal)
# ─────────────────────────────────────────────────────────────────────────────
PASSAGES = [
    # PASSAGE 1
    {
        "passage": "The Amazon rainforest, often called the 'lungs of the Earth,' produces approximately 20% of the world's oxygen and is home to more than 10% of all species on the planet. Despite its vital importance, the Amazon has been facing unprecedented deforestation rates. Between 2019 and 2021, the region lost millions of hectares of forest due to agricultural expansion, illegal logging, and land clearing for cattle ranching. Scientists warn that if deforestation continues at this pace, the Amazon could reach a tipping point — a moment where the forest can no longer sustain itself and begins to degrade irreversibly. Conservation organizations and governments are working to establish protected areas, enforce environmental regulations, and promote sustainable land use practices to prevent this catastrophe.",
        "questions": [
            {"question": "What is the main purpose of this passage?", "options": ["To describe the biodiversity of the Amazon", "To discuss threats to the Amazon and conservation efforts", "To explain how the Amazon produces oxygen", "To compare deforestation rates in different countries"], "correct": 1},
            {"question": "According to the passage, what percentage of the world's species live in the Amazon?", "options": ["More than 20%", "Exactly 10%", "More than 10%", "Approximately 5%"], "correct": 2},
            {"question": "What does the term 'tipping point' refer to in the passage?", "options": ["A moment of rapid economic growth", "The point at which deforestation becomes irreversible", "The peak of biodiversity in the forest", "The maximum capacity for oxygen production"], "correct": 1},
            {"question": "Which of the following is NOT mentioned as a cause of deforestation?", "options": ["Agricultural expansion", "Illegal logging", "Mining operations", "Cattle ranching"], "correct": 2},
            {"question": "What can be inferred about the current state of the Amazon?", "options": ["It has already passed its tipping point", "It is under serious environmental threat", "Conservation efforts have been completely successful", "Deforestation rates have recently decreased"], "correct": 1},
        ],
    },
    # PASSAGE 2
    {
        "passage": "Remote work, once considered a temporary measure during the pandemic, has now become a permanent feature of the modern workplace. A 2023 survey found that more than 58% of knowledge workers in developed economies work remotely at least part of the time. Proponents argue that remote work increases employee satisfaction, reduces commuting time, and allows companies to recruit talent from a global pool. However, critics point to challenges such as difficulty in collaboration, feelings of isolation among employees, and the blurring of boundaries between work and personal life. To address these issues, many organizations are adopting hybrid models that combine in-office and remote work, aiming to capture the benefits of both while minimizing the downsides.",
        "questions": [
            {"question": "What is the passage primarily about?", "options": ["The history of remote work", "The impact of the pandemic on employment", "The rise and challenges of remote work", "Why companies prefer in-office work"], "correct": 2},
            {"question": "According to the survey mentioned, what percentage of knowledge workers work remotely at least part of the time?", "options": ["More than 68%", "Less than 50%", "More than 58%", "Exactly 58%"], "correct": 2},
            {"question": "Which of the following is listed as a benefit of remote work?", "options": ["Better collaboration", "Access to global talent", "Clearer work-life boundaries", "Improved mental health"], "correct": 1},
            {"question": "What is a 'hybrid model' as described in the passage?", "options": ["A combination of full-time and part-time work", "A mix of remote and in-office work", "A system using both technology and manual processes", "An approach combining freelance and permanent employment"], "correct": 1},
            {"question": "What does the word 'proponents' mean in the context of the passage?", "options": ["Critics", "Researchers", "Supporters", "Employers"], "correct": 2},
        ],
    },
    # PASSAGE 3
    {
        "passage": "Artificial intelligence is transforming numerous industries, from healthcare to finance. In medicine, AI algorithms can now analyze medical images with accuracy comparable to experienced radiologists, enabling earlier and more precise diagnoses of conditions such as cancer and heart disease. In the financial sector, AI-powered systems detect fraudulent transactions in real time by identifying unusual patterns in millions of data points simultaneously. Despite these advancements, concerns persist about ethical issues — particularly algorithmic bias, where AI systems may produce outcomes that inadvertently discriminate against certain groups. Experts emphasize that responsible AI development must involve transparency, diverse training data, and rigorous human oversight to ensure that these powerful tools benefit all of society equitably.",
        "questions": [
            {"question": "What is the central theme of the passage?", "options": ["The history of artificial intelligence", "AI's applications and ethical concerns", "How AI is used in the financial industry", "The dangers of machine learning"], "correct": 1},
            {"question": "According to the passage, how does AI assist in medicine?", "options": ["By replacing doctors in surgery", "By managing patient records", "By analyzing medical images for diagnosis", "By developing new medications"], "correct": 2},
            {"question": "What is 'algorithmic bias' as mentioned in the passage?", "options": ["A preference for certain AI companies", "Errors caused by computer hardware", "AI producing discriminatory outcomes unintentionally", "Bias in how researchers interpret AI data"], "correct": 2},
            {"question": "What do experts suggest is needed for responsible AI development?", "options": ["Faster computing systems and lower costs", "Transparency, diverse data, and human oversight", "Restricting AI to government use only", "Giving AI systems full autonomy"], "correct": 1},
            {"question": "The word 'inadvertently' in the passage most nearly means:", "options": ["Deliberately", "Accidentally", "Frequently", "Severely"], "correct": 1},
        ],
    },
    # PASSAGE 4
    {
        "passage": "Sleep is far more than a period of rest. During sleep, the brain undergoes critical processes that are essential for learning, memory consolidation, and emotional regulation. Research shows that people who consistently sleep fewer than seven hours per night are at significantly higher risk for chronic conditions such as obesity, diabetes, cardiovascular disease, and depression. Despite this, modern society often treats sleep deprivation as a badge of honor, with productivity culture glorifying long working hours at the expense of adequate rest. Sleep scientists advocate for a shift in cultural attitudes, arguing that prioritizing sleep is not a sign of laziness but rather a fundamental investment in one's long-term health, cognitive performance, and overall well-being.",
        "questions": [
            {"question": "What is the main argument of the passage?", "options": ["People should work fewer hours", "Sleep is critically important for health and well-being", "Modern society is obsessed with productivity", "Scientists have discovered new sleep disorders"], "correct": 1},
            {"question": "According to the passage, what happens to the brain during sleep?", "options": ["It stops all activity", "It repairs physical injuries", "It consolidates memory and regulates emotions", "It generates new neural pathways randomly"], "correct": 2},
            {"question": "What health risks are associated with sleeping fewer than seven hours?", "options": ["Vision problems and migraines", "Obesity, diabetes, and cardiovascular disease", "Joint pain and muscle weakness", "Allergies and immune disorders"], "correct": 1},
            {"question": "How does modern society view sleep deprivation according to the author?", "options": ["As a serious health issue requiring treatment", "As something to be avoided at all costs", "As a sign of dedication and productivity", "As a natural consequence of technology use"], "correct": 2},
            {"question": "What does the author mean by 'a fundamental investment' in relation to sleep?", "options": ["Sleep requires financial resources", "Prioritizing sleep has long-term benefits", "Sleep is a luxury only some can afford", "Good sleep requires expensive equipment"], "correct": 1},
        ],
    },
    # PASSAGE 5
    {
        "passage": "Climate change poses one of the greatest challenges of the 21st century, affecting ecosystems, economies, and human health on a global scale. The primary driver of contemporary climate change is the dramatic increase in greenhouse gas emissions resulting from industrial activity, deforestation, and the burning of fossil fuels. Rising global temperatures are causing glaciers and polar ice caps to melt at unprecedented rates, contributing to sea level rise that threatens coastal communities worldwide. While international agreements such as the Paris Agreement represent significant diplomatic progress, experts argue that current national commitments remain insufficient to limit warming to the 1.5°C target set by climate scientists. Transformative action — including rapid transition to renewable energy, carbon capture technologies, and systemic changes in consumption patterns — is urgently needed.",
        "questions": [
            {"question": "What is the primary cause of climate change according to the passage?", "options": ["Natural volcanic activity", "Greenhouse gas emissions from human activity", "Changes in Earth's orbit", "Ocean temperature fluctuations"], "correct": 1},
            {"question": "What consequence of rising temperatures is specifically mentioned?", "options": ["Increased frequency of earthquakes", "Disruption of ocean currents", "Melting glaciers causing sea level rise", "Widespread droughts across continents"], "correct": 2},
            {"question": "What does the author suggest about current national climate commitments?", "options": ["They exceed what is scientifically necessary", "They are exactly on target", "They are not sufficient to meet the 1.5°C goal", "They have already reduced emissions significantly"], "correct": 2},
            {"question": "Which of the following solutions is NOT mentioned in the passage?", "options": ["Renewable energy transition", "Carbon capture technologies", "Geoengineering the atmosphere", "Changing consumption patterns"], "correct": 2},
            {"question": "The word 'transformative' in the passage most closely means:", "options": ["Gradual and incremental", "Fundamental and far-reaching", "Temporary and reversible", "Politically motivated"], "correct": 1},
        ],
    },
    # PASSAGE 6
    {
        "passage": "The global food system faces mounting pressure to feed a projected population of nearly ten billion people by 2050 while simultaneously reducing its environmental footprint. Industrial agriculture, which dominates global food production, relies heavily on chemical fertilizers, pesticides, and large amounts of water — practices that have enabled remarkable productivity gains but have also led to soil degradation, water pollution, and significant greenhouse gas emissions. Alternative approaches such as regenerative agriculture, vertical farming, and precision agriculture — which uses data and technology to optimize resource use — are gaining traction as more sustainable solutions. However, scaling these innovations to meet global food demands requires significant investment, policy support, and changes in consumer behavior.",
        "questions": [
            {"question": "What is the central challenge discussed in the passage?", "options": ["Reducing meat consumption worldwide", "Feeding a growing population sustainably", "Improving food distribution networks", "Managing food waste in developed countries"], "correct": 1},
            {"question": "What is a negative consequence of industrial agriculture mentioned in the passage?", "options": ["Decreased food productivity", "Higher food prices for consumers", "Soil degradation and water pollution", "Reduced access to technology"], "correct": 2},
            {"question": "What does 'precision agriculture' refer to according to the passage?", "options": ["Small-scale organic farming methods", "Using data and technology to optimize farming", "Traditional farming techniques updated for modern use", "Farming in controlled indoor environments"], "correct": 1},
            {"question": "What does the passage suggest is needed to scale alternative farming methods?", "options": ["Eliminating industrial agriculture completely", "Investment, policy support, and behavior change", "More research into genetic engineering", "Reducing the global population target"], "correct": 1},
            {"question": "The word 'footprint' in the first sentence most likely refers to:", "options": ["Physical land area used for farming", "Environmental impact of food production", "Economic cost of the food system", "Number of workers in agriculture"], "correct": 1},
        ],
    },
]

# ─────────────────────────────────────────────────────────────────────────────
#  BUILD ROWS
# ─────────────────────────────────────────────────────────────────────────────
rows = []

# Listening
for i, q in enumerate(LISTENING):
    rows.append({
        "pool_id": f"L{i+1:03d}",
        "type": "listening",
        "question": q["question"],
        "option_a": q["options"][0],
        "option_b": q["options"][1],
        "option_c": q["options"][2],
        "option_d": q["options"][3],
        "correct": q["correct"],
        "script": q.get("script", ""),
        "passage": "",
        "difficulty": "easy" if i < 20 else ("medium" if i < 40 else "hard"),
    })

# Structure
for i, q in enumerate(STRUCTURE):
    rows.append({
        "pool_id": f"S{i+1:03d}",
        "type": "structure",
        "question": q["question"],
        "option_a": q["options"][0],
        "option_b": q["options"][1],
        "option_c": q["options"][2],
        "option_d": q["options"][3],
        "correct": q["correct"],
        "script": "",
        "passage": "",
        "difficulty": "easy" if i < 20 else ("medium" if i < 40 else "hard"),
    })

# Reading — expand passage per question
reading_idx = 0
for p_idx, p_block in enumerate(PASSAGES):
    for q in p_block["questions"]:
        rows.append({
            "pool_id": f"R{reading_idx+1:03d}",
            "type": "reading",
            "question": q["question"],
            "option_a": q["options"][0],
            "option_b": q["options"][1],
            "option_c": q["options"][2],
            "option_d": q["options"][3],
            "correct": q["correct"],
            "script": "",
            "passage": p_block["passage"],
            "difficulty": "easy" if p_idx < 2 else ("medium" if p_idx < 4 else "hard"),
        })
        reading_idx += 1

# Write CSV
output_path = os.path.join(os.path.dirname(__file__), "bank_soal_ept.csv")
fieldnames = ["pool_id","type","question","option_a","option_b","option_c","option_d","correct","script","passage","difficulty"]

with open(output_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"✅ Bank soal berhasil dibuat: {len(rows)} soal")
print(f"   📁 Disimpan ke: {output_path}")

# Summary
from collections import Counter
types  = Counter(r["type"] for r in rows)
levels = Counter(r["difficulty"] for r in rows)
print(f"\n📊 Distribusi Tipe:")
for t, n in sorted(types.items()): print(f"   {t}: {n} soal")
print(f"\n🎯 Distribusi Level:")
for l, n in sorted(levels.items()): print(f"   {l}: {n} soal")

# ── ADDITIONAL PASSAGES 7–12 (append to PASSAGES list before rows are built) ──
