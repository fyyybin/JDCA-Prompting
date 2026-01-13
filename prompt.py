from data.mbti_initial_weight import WEIGHT, MBTI, Players
# def get_choose_type():

def get_inherent_prompt(name : str, question, mbti: str, dataset):

    # info_information = "**Based on Jung's personality theory, role-play as " + name + " with the personality described below to solve the presented problem.**\n\n##Basic Information##\nName:" + name
    info_information = f"**Based on Jung's personality theory, role-play as {name} with the personality described below to solve the presented problem.**\n\n##Basic Information##\nName: {name}"
    
    all_character = Players
    for i in all_character:
        if i['name'] == name:
            character_info = i
    players_information = "\ngender:" + character_info['gender'] + "\n" + "age:" + character_info['age'] + "\n"
    info_prompt = info_information + players_information
    if 'beliefQAs' not in dataset:
        question_prompt = f"\nNow, please strictly follow the information above, especially the content in ## {name} Psychological Type ## and answer the multiple-choice questions carefully as {name}. Please answer the questions based on the content. The question is as follows:\nContent: {question['content']}\nInformation: {question['fact_q']} {question['fact_a']}\nQuestion: {question['question']}\nOption {question['answerOptions'][0]['type']}: {question['answerOptions'][0]['answer']}\nOption {question['answerOptions'][1]['type']}: {question['answerOptions'][1]['answer']}"
    else:
        question_prompt = f"\nNow, please strictly follow the information above, especially the content in ## {name} Psychological Type ## and answer the multiple-choice questions carefully as {name}. Please answer the questions based on the content. The question is as follows:\nContent: {question['content']}\nQuestion: {question['question']}\nOption {question['answerOptions'][0]['type']}: {question['answerOptions'][0]['answer']}\nOption {question['answerOptions'][1]['type']}: {question['answerOptions'][1]['answer']}"
    
    answer_prompt = "\n\nYou must return your response in the following structure only(output with English),with absolutely no content beyond the specified example structure:\n{\n'answer' : 'A', // only the single letter of the option\n}"

  
    return info_prompt + question_prompt + answer_prompt

def get_direct_prompt(name : str, question, mbti: str):
    
    info_information = f"**Based on Jung's personality theory, role-play as {name} with the personality described below to solve the presented problem.**\n\n##Basic Information##\nName: {name}"
    all_character = Players
    for i in all_character:
        if i['name'] == name:
            character_info = i
    players_information = f"\ngender: {character_info['gender']}\nage: {character_info['age']}\n"
    info_prompt = info_information + players_information
    desp_information = f"\n## {name} Psychological Type Processing Mechanism##\nPsychological Type: {mbti}\n"
    question_prompt = f"\nNow, please strictly follow the information above, especially the content in ## {name} Psychological Type ## and answer the multiple-choice questions carefully as {name}. Please response the question. The question is as follows:\nQuestion: {question['question']}\nOption {question['answerOptions'][0]['type']}: {question['answerOptions'][0]['answer']}\nOption {question['answerOptions'][1]['type']}: {question['answerOptions'][1]['answer']}"
    answer_prompt = "\n\nYou must return your response in the following structure only(output with English),with absolutely no content beyond the specified example structure:\n{\n'answer' : 'A', // only the single letter of the option\n}"

    return info_prompt + desp_information + question_prompt + answer_prompt

def get_question_dimension(question):
    prompt1 = "##Player##\nNow you need to accurately identify the dimension (I/E, N/S, T/F, J/P) to which the question belongs based on the user's question and answer options.\n\n## Dimension Definition##\n1. I/E (Introversion/Extroversion)\n- Core: Energy Direction and Focus\n- Key Characteristics: The question addresses social preferences (solitude vs. group), energy sources (internal reflection vs. external interaction), and expression style (introversion vs. extroversion).\n- Example: 'How do you recharge after social activities?' → I/E\n2. N/S (Intuition/Sensing)\n- Core: Information Acquisition Style\n- Key Characteristics: The question focuses on information processing details (concrete facts vs. abstract concepts), time focus (present reality vs. future possibilities), and description style (actual experience vs. theoretical association). - Example: 'How do you understand the meaning of this metaphor?' → N/S\n3. T/F (Thinking/Feeling)\n- Core: Decision-making Logic\n- Key Characteristics: The question involves decision-making criteria (objective logic vs. subjective emotion), value orientation (fairness vs. interpersonal relationships), and conflict resolution (reasoning vs. emphasizing harmony).\n- Example: 'Do you rely more on logic or empathy when making decisions?' → T/F\n4. J/P (Judgment/Perception)\n- Core: Attitude toward the External World\n- Key Characteristics: The question addresses behavioral patterns (planning vs. flexibility), organizational style (structured vs. spontaneous), and goal-oriented approach (results-oriented vs. process-oriented). \n- Example: 'Do you make a detailed itinerary before traveling?' → J/P\n\n## Analysis Process##\nPlease reason strictly according to the steps: \n1. Understand the Essence of the Question\n- Extract keywords and behavioral scenarios from the question (e.g., 'going out,' 'making decisions,' 'social interaction'). \n2. Compare Answer Options\n- Analyze the cognitive preferences implied by each option (e.g., 'Planning' → Structured; 'Going Directly' → Spontaneous). \n3. Match Dimensions\n- Compare the question characteristics with the dimension definitions: \n- If it involves 'Energy Source/Social Orientation' → I/E\n- If it involves 'Information Processing Style' → N/S\n- If it involves 'Decision-Making Logic' → T/F\n- If it involves 'Planning/Flexibility' → J/P\n4. Eliminate Distractions\n- Ensure there is no confusion between dimensions (e.g., planning belongs to J/P, not T/F). \n\n## Example Analysis##\nQuestion: What do you do when you have to go out all day? \nOption A: Plan what you will do and when\nOption B: Just go\nReasoning Process: \n1. Question Essence: Behavior patterns when out (planning vs. improvisation). \n2. Option Comparison: \n- A emphasizes structure (planning time/items) → Judging (J) \n- B emphasizes flexibility (unplanned action) → Perceiving (P) \n3. Dimension Match: The difference in behavior patterns directly corresponds to the J/P dimension (Judging vs. Perceiving). \n4. Interference Elimination: No social/decision-making/information processing elements, excluding I/E/T/F/N/S. \nOutput: \n{'answer': 'J/P'} \n\n Please determine the dimension of the question. The question is as follows:\n"

    # print(question)
    prompt2 = "\nQuestion:" + question['question'] + "\nOption " + question['answerOptions'][0]['type'] + ":" + \
              question['answerOptions'][0]['answer'] + "\nOption " + question['answerOptions'][1]['type'] + ":" + \
              question['answerOptions'][1]['answer']
    prompt3 = "\n\nResponse output format (strictly defined, JSON only): \n{\n'answer': 'J/P', //option letters only\n}\n"
    
    return prompt1 + prompt2 + prompt3

def get_conditioned_prompt(name : str, question, mbti: str, dimension):
    
    info_information = f"**Based on Jung's personality theory, role-play as {name} with the personality described below to solve the presented problem.**\n\n##Basic Information##\nName: {name}"
    all_character = Players
    for i in all_character:
        if i['name'] == name:
            character_info = i
    players_information = f"\ngender: {character_info['gender']}\nage: {character_info['age']}\n"
    info_prompt = info_information + players_information

    main_func = WEIGHT[mbti]['main_function'] #主导人格
    assist_func = WEIGHT[mbti]['assist_function'] #辅助人格
    
    main_description = MBTI['FUNCTION'][main_func]['HIGH']
    assist_description =  MBTI['FUNCTION'][assist_func]['MID']
    balance_description = MBTI['MBTI'][mbti]['balance']

    
    if mbti in ['INTP', 'ISTP', 'INFP', 'ISFP', 'ENTJ', 'ESTJ', 'ENFJ', 'ESFJ']:
        if dimension == 'I/E' or dimension[0] in 'I/E':
            get_mechanism = main_description
        elif dimension == 'N/S' or dimension[0] in 'N/S':
            get_mechanism = assist_description
        elif dimension == 'T/F' or dimension[0] in 'T/F':
            get_mechanism = main_description
        elif dimension == 'J/P' or dimension[0] in 'J/P':
            get_mechanism = balance_description
    else:
        if dimension == 'I/E' or dimension[0] in 'I/E':
            get_mechanism = main_description
        elif dimension == 'N/S' or dimension[0] in 'N/S':
            get_mechanism = main_description
        elif dimension == 'T/F' or dimension[0] in 'T/F':
            get_mechanism = assist_description
        elif dimension == 'J/P' or dimension[0] in 'J/P':
            get_mechanism = balance_description
    
    if get_mechanism is None:
        print(dimension)

    desp_information = f"\n## {name} Psychological Type Processing Mechanism##\n{get_mechanism}\n"
    
    question_prompt = f"\nNow, please strictly follow the information above, especially the content in ## {name} Psychological Type ## and answer the multiple-choice questions carefully as {name}. Please response the question. The question is as follows:\nQuestion: {question['question']}\nOption {question['answerOptions'][0]['type']}: {question['answerOptions'][0]['answer']}\nOption {question['answerOptions'][1]['type']}: {question['answerOptions'][1]['answer']}"
    
    answer_prompt = "\n\nYou must return your response in the following structure only(output with English),with absolutely no content beyond the specified example structure:\n{\n'answer' : 'A', // only the single letter of the option\n}"

    # question_prompt = f"\nNow, please strictly follow the information above, especially the content in ## {name} Psychological Type ## and answer the multiple-choice questions carefully as {name}. Provide the reasoning behind your choice and which mode you chose. The question is as follows:\nQuestion: {question['question']}\nOption {question['answerOptions'][0]['type']}: {question['answerOptions'][0]['answer']}\nOption question['answerOptions'][1]['type']: {question['answerOptions'][1]['answer']}"
    # question_prompt = f"\nNow, please strictly follow the information above, answer the multiple-choice questions carefully as {name}. Please choose a function to answer the given question. For the given question, provide 5 answers corresponding to levels 1 to 5. \n1 represents completely negative\n2 represents somewhat negative\n3 represents neutral\n4 represents somewhat positive\n5 represents completely positive\nProvide the answer which level you chose and provide the answer which type you chose to use. The question is as follows:\nQuestion: {question}\nYou must return your response in the following structure only(output with English), with absolutely no content beyond the specified example structure:\n'answer' : '1', // only the single letter of the option\n'type': '', // psychological type\n"
    # answer_prompt =  "\n\nYou must return your response in the following structure only(output with English),with absolutely no content beyond the specified example structure:\n{\n'answer' : 'A', // only the single letter of the option\n}"

    return info_prompt + desp_information + question_prompt + answer_prompt

def get_fandom_dimension(question):
    prompt1 = "##Player##\nNow you need to accurately identify the dimension (I/E, N/S, T/F, J/P) to which the question belongs based on the user's question and answer options.\n\n## Dimension Definition##\n1. I/E (Introversion/Extroversion)\n- Core: Energy Direction and Focus\n- Key Characteristics: The question addresses social preferences (solitude vs. group), energy sources (internal reflection vs. external interaction), and expression style (introversion vs. extroversion).\n- Example: 'How do you recharge after social activities?' → I/E\n2. N/S (Intuition/Sensing)\n- Core: Information Acquisition Style\n- Key Characteristics: The question focuses on information processing details (concrete facts vs. abstract concepts), time focus (present reality vs. future possibilities), and description style (actual experience vs. theoretical association). - Example: 'How do you understand the meaning of this metaphor?' → N/S\n3. T/F (Thinking/Feeling)\n- Core: Decision-making Logic\n- Key Characteristics: The question involves decision-making criteria (objective logic vs. subjective emotion), value orientation (fairness vs. interpersonal relationships), and conflict resolution (reasoning vs. emphasizing harmony).\n- Example: 'Do you rely more on logic or empathy when making decisions?' → T/F\n4. J/P (Judgment/Perception)\n- Core: Attitude toward the External World\n- Key Characteristics: The question addresses behavioral patterns (planning vs. flexibility), organizational style (structured vs. spontaneous), and goal-oriented approach (results-oriented vs. process-oriented). \n- Example: 'Do you make a detailed itinerary before traveling?' → J/P\n\n## Analysis Process##\nPlease reason strictly according to the steps: \n1. Understand the Essence of the Question\n- Extract keywords and behavioral scenarios from the question (e.g., 'going out,' 'making decisions,' 'social interaction'). \n2. Compare Answer Options\n- Analyze the cognitive preferences implied by each option (e.g., 'Planning' → Structured; 'Going Directly' → Spontaneous). \n3. Match Dimensions\n- Compare the question characteristics with the dimension definitions: \n- If it involves 'Energy Source/Social Orientation' → I/E\n- If it involves 'Information Processing Style' → N/S\n- If it involves 'Decision-Making Logic' → T/F\n- If it involves 'Planning/Flexibility' → J/P\n4. Eliminate Distractions\n- Ensure there is no confusion between dimensions (e.g., planning belongs to J/P, not T/F). \n\n## Example Analysis##\nQuestion: What do you do when you have to go out all day? \nOption A: Plan what you will do and when\nOption B: Just go\nReasoning Process: \n1. Question Essence: Behavior patterns when out (planning vs. improvisation). \n2. Option Comparison: \n- A emphasizes structure (planning time/items) → Judging (J) \n- B emphasizes flexibility (unplanned action) → Perceiving (P) \n3. Dimension Match: The difference in behavior patterns directly corresponds to the J/P dimension (Judging vs. Perceiving). \n4. Interference Elimination: No social/decision-making/information processing elements, excluding I/E/T/F/N/S. \nOutput: \n{'answer': 'J/P'} \n\n Please determine the dimension of the question based on the content. The question is as follows:\n"

    # print(question)
    prompt2 = "Content: " + question['content'] + "\nQuestion:" + question['question']
    prompt3 = "\n\nResponse output format (strictly defined, JSON only): \n{\n'answer': 'J/P', //option letters only\n}\n"
    
    return prompt1 + prompt2 + prompt3

def get_conditioned_fandom_prompt(name : str, question, mbti: str, dimension):

    info_information = f"**Based on Jung's personality theory, role-play as {name} with the personality described below to solve the presented problem.**\n\n##Basic Information##\nName: {name}"
    all_character = Players
    for i in all_character:
        if i['name'] == name:
            character_info = i
    players_information = f"\ngender: {character_info['gender']}\nage: {character_info['age']}\n"
    info_prompt = info_information + players_information

    main_func = WEIGHT[mbti]['main_function'] #主导人格
    assist_func = WEIGHT[mbti]['assist_function'] #辅助人格
    
    main_description = MBTI['FUNCTION'][main_func]['HIGH']
    assist_description =  MBTI['FUNCTION'][assist_func]['MID']
    balance_description = MBTI['MBTI'][mbti]['balance']

    
    if mbti in ['INTP', 'ISTP', 'INFP', 'ISFP', 'ENTJ', 'ESTJ', 'ENFJ', 'ESFJ']:
        if dimension == 'I/E' or dimension[0] in 'I/E':
            get_mechanism = main_description
        elif dimension == 'N/S' or dimension[0] in 'N/S':
            get_mechanism = assist_description
        elif dimension == 'T/F' or dimension[0] in 'T/F':
            get_mechanism = main_description
        elif dimension == 'J/P' or dimension[0] in 'J/P':
            get_mechanism = balance_description
    else:
        if dimension == 'I/E' or dimension[0] in 'I/E':
            get_mechanism = main_description
        elif dimension == 'N/S' or dimension[0] in 'N/S':
            get_mechanism = main_description
        elif dimension == 'T/F' or dimension[0] in 'T/F':
            get_mechanism = assist_description
        elif dimension == 'J/P' or dimension[0] in 'J/P':
            get_mechanism = balance_description
    
    try:
        if get_mechanism is None:
            print(dimension)
    except:
        print(question)
        print(dimension)

    desp_information = f"\n## {name} Psychological Type Processing Mechanism##\n{get_mechanism}\n"
    
    if 'fact_q' not in question:
        question_prompt = f"\nNow, please strictly follow the information above, especially the content in ## {name} Psychological Type ## and answer the multiple-choice questions carefully as {name}. Please answer the questions based on the content. The question is as follows:\nContent: {question['content']}\nQuestion: {question['question']}\nOption {question['answerOptions'][0]['type']}: {question['answerOptions'][0]['answer']}\nOption {question['answerOptions'][1]['type']}: {question['answerOptions'][1]['answer']}"
    else:
        question_prompt = f"\nNow, please strictly follow the information above, especially the content in ## {name} Psychological Type ## and answer the multiple-choice questions carefully as {name}. Please answer the questions based on the content. The question is as follows:\nContent: {question['content']}\nInformation: {question['fact_q']} {question['fact_a']}\nQuestion: {question['question']}\nOption {question['answerOptions'][0]['type']}: {question['answerOptions'][0]['answer']}\nOption {question['answerOptions'][1]['type']}: {question['answerOptions'][1]['answer']}"

    answer_prompt = "\n\nYou must return your response in the following structure only(output with English),with absolutely no content beyond the specified example structure:\n{\n'answer' : 'A', // only the single letter of the option\n}"

    return info_prompt + desp_information + question_prompt + answer_prompt


