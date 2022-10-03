CLASS_NAME_TEXT = {
    'Advanced Data Analytics for Management Support': 'The module Advanced Data Analytics for Management Support (ADAMS) introduces students to the latest developments in the scope of data-driven management support. It covers relevant theories and concepts in machine learning against the background of concrete real-world applications in management science. Special emphasize is given to the analysis of textual data and other forms of complex data such as sequences or images. Corresponding data is typically approached using the framework of deep artificial neural networks. The module recognizes the importance of deep learning and elaborates on corresponding methodologies. Frameworks and practices to use advanced (deep) machine learning technology and deploy corresponding solutions are of critical importance and will be elaborated in tutorial sessions. The topics covered in the module include but are not limited to: Fundamentals of artificial neural networks, Recurrent and convolutional neural networks for sequential data processing, Fundamentals of natural language processing(NLP), Text embedding and language models, Sentiment Analysis Approaches for NLP transfer learning. The module is designed as a follow-up to the module Business Analytics and Data Science (BADS). We expect students to have completed that module prior to taking ADAMS. More specifically, it is strongly recommended to join this module with a solid understanding of (supervised) machine learning practices and algorithms. Some experience in Python programming is also expected since we use the Python programming language in tutorials. The grading of the module will be based on a practical assignment, which also involves Python programming.',
    'Intercultural Textuality': 'In this course, students will practise developing their spoken and written competence in English in a variety of contexts including participating in discussions and debates on literary/cultural themes and writing texts of their own in the areas of fiction, non-fiction and creative writing. The focus will be on finding just the right words, tone and style to communicate naturally and effectively in different spoken/authorial situations using the textual dynamics and cultural codes of English. This course will involve blended learning. Interested students should send an email to michael.davies@hu-berlin.de by Wednesday, 13th April 2022 and include details of language courses they have already attended in modules 1a and 1b of the MA English Literatures programme.',
    'Modernist Poetry': 'The class offers a critical interpretation of poetry written before, during, and after World War I as well as contemporary theories of poetry. On the one hand, we will explore what constitutes its modernist innovations and, on the other, trace relations to the Romantic and Victorian heritage. The seminar will focus on the poetry of 3 canonical modernist poets: W.B. Yeats, T.S. Eliot, and Ezra Pound. In order to investigate the variety of the poetry of that period we will also study a selection of texts by D.H. Lawrence, Siegfried Sassoon, Wilfred Owen, and others. password Moodle: mod',
    'Scientific Writing': 'Writing is central to scientific communication and academic work. This course will introduce you to writing and reviewing scientific articles and theses. We will use a mixture of lectures, individual and group work, and article discussions to understand the DOs and DONTs in scientific writing. Foremost, you will learn strategies that are common to both thesis and paper writing, including (i) how to plan, organise and structure your article/thesis, (ii) how to research relevant literature, (iii) how to write different parts of articles/theses, (iv) how to plan and integrate visual items, (v) how to evaluate articles/theses of your peers, (vi) how to identify and avoid plagiarism, and (vii) how to cite correctly. Additionally, we will discuss certain aspects that are specific to writing scientific articles, for example journal aims and scopes, editorial processes. Also, soft skills will be trained and practiced during the course including the preparation/development of own high quality presentations. In the end, you should be able to communicate your scientific results in a correct, structured and appealing way, for your thesis or academia.',
    'Classroom Discourse': 'This course is designed to give future teachers practice using English on the job before they find themselves in charge of a class! Participants will practice designing classroom activities for different learner proficiency levels in speaking, listening, reading, and writing, and familiarizing themselves with students oral and written abilities at each level - all in English. Special attention will be paid to appropriate classroom vocabulary and making activities interesting and effective. This is a blended learning course and will primarily meet in person. MA Education students only. Interested students should register by Wednesday, 13th April 2022 using the form on the MA Ed English Sprachpraxis Course Registration SoSe 2022 Moodle page. The password is: sprchprxs22',
    'Decision-Making under Uncertainty': 'Topics will be: Preferences over uncertain prospects, expected utility under risk, probability weighting, exptected utility without known probabilities, ambiguity attitudes, standard financial investment problems, dynamic investments.',
    'Industrial Organization': 'Learning objectives: The students know the general principles, topics and methods of the economic analysis of industrial organization, based on theoretical models and stylized facts (in particular, case studies). They are familiar with various topics organization and have a deeper understanding of the structure, functioning and outcomes of markets with imperfect competition. Lecture topics: The theory of the firm, monopoly, oliopoly, collusion, product differentiation, vertical relationships and restraints, mergers, entry and market structure, search and switching costs, two-sided markets, R&D, advertising, asymmetric information. Exercise topics: Solutions to problem sets and discussion of case studies and articles related to the topics from the lecture. Recommended module or comparable previous knowledge: Mikroökonomie I and Mikroökonomie II are prequisites. Einführung in die Spieltheorie is helpful but not required (all game theory required beyond Mikroökonomie II will be taught in this module).'
}

class QuestionBody:

    def __init__(self, class_name):
        self.general_questions = list()
        question1 = 'What are the topics?'
        question2 = 'What is this class about?'
        question3 = 'What is this module about?'
        question4 = f'What is the main objective of {class_name}?'
        question5 = f'What is the topic of {class_name}?'
        question6 = f'Who is the target group for the class {class_name}?'
        question7 = f'What will I learn in {class_name}?'
        self.general_questions.append(question1)
        self.general_questions.append(question2)
        self.general_questions.append(question3)
        self.general_questions.append(question4)
        self.general_questions.append(question5)
        self.general_questions.append(question6)
        self.general_questions.append(question7)

        self.specific_questions = list()
        if class_name == 'Advanced Data Analytics for Management Support':
            s_question = 'What is the grading for this course?'
            self.specific_questions.append(s_question)
        elif class_name == 'Intercultural Textuality':
            s_question = 'Should the students register?'
            self.specific_questions.append(s_question)
        elif class_name == 'Modernist Poetry' or class_name == 'Scientific Writing':
            s_question = 'What is the moodle password?'
            self.specific_questions.append(s_question)
        elif class_name == 'Classroom Discourse':
            s_question1 = 'Will the class take place in person or online?'
            s_question2 = 'Will this be an online class?'
            s_question3 = 'For which students is this class?'
            s_question4 = 'What is the moodle password?'
            s_question5 = 'Should the students register?'
            s_question6 = 'How should students register?'
            self.specific_questions.append(s_question1)
            self.specific_questions.append(s_question2)
            self.specific_questions.append(s_question3)
            self.specific_questions.append(s_question4)
            self.specific_questions.append(s_question5)
            self.specific_questions.append(s_question6)
        elif class_name == 'Industrial Organization':
            s_question1 = 'What are the prerequisites for this module??'
            s_question2 = 'Is any previous knowledge needed??'
            self.specific_questions.append(s_question1)
            self.specific_questions.append(s_question2)
