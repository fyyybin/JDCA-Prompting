from api import *
from prompt import *
import random
import threading
from tqdm import tqdm
import argparse
from data.mbti_initial_weight import Players

class GeneratedAgent:
    def __init__(self, args):
        self.args = args
        self.all_question = self.load_data(args.dataset)
        self.roles = Players
        self.all_mbti = [args.single_mbti] if args.single else self.load_data('mbti')
        self.lock = threading.Lock()
        self.threads = []
        self.local_data = threading.local()

        self.progress_bars=[]

        self.results = []
        self.counts = []
    def load_data(self, data_type):
        if args.method == 'get_eval' and data_type != 'mbti':
            if 'llama-3-8b' in args.model:
                modelname = 'llama-3-8b'
            elif 'llama-3-70b' in args.model:
                modelname = 'llama-3-70b'
            else:
                modelname = args.model
            with open('result/judge/'+ args.dataset + '_' + modelname + '_get_judge' + '.json', encoding='UTF-8') as file:
                answers = json.load(file)
            with open(f'data/{data_type}_data.json', encoding='UTF-8') as file:
                questions = json.load(file)
            q = []
            if 'beliefQAs' not in args.dataset:
                for i in range(len(answers)):
                    q.append({
                        "content": questions[i]['content'],
                        "question":questions[i]['question'],
                        "fact_q": questions[i]['fact_q'],
                        "fact_a": questions[i]['fact_a'],
                        "answerOptions": questions[i]['answerOptions'],
                        "Answers": answers[i]['Answers']
                    })
            else:
                for i in range(len(answers)):
                    q.append({
                        "content": questions[i]['content'],
                        "question":questions[i]['question'],
                        # "fact_q": questions[i]['fact_q'],
                        # "fact_a": questions[i]['fact_a'],
                        "answerOptions": questions[i]['answerOptions'],
                        "Answers": answers[i]['Answers']
                    })
            return q
        
        elif data_type == 'mbti':
            if args.method != 'inherent':
                return list(WEIGHT.keys())
                # return ['ESTP','ESTJ','INTP','ENFJ','ENFP','ESFJ']
            else:
                return ['ENTJ']
        else:
            with open(f'data/{data_type}_data.json', encoding='UTF-8') as file:
                questions = json.load(file)
            return questions

    def workers(self, thread_id):
        """线程函数：生成数组数据"""
        mbti_res =  {self.all_mbti[thread_id] : []}
        # mbti = self.all_mbti[thread_id]
        # mbti_1_res =  {self.all_mbti[thread_id] : []}
        count = 0
        for QA in self.all_question:
            question = QA['question']
            
            if args.method == 'inherent':
                prompt = get_inherent_prompt(self.roles[thread_id]['name'], QA, self.all_mbti[thread_id], args.dataset)
                message = get_response(prompt, args.model, args.temperature)  # Call the api interface
                if message is None:
                    while message is None:
                        print('again\n')
                        message = get_response(prompt, args.model, args.temperature)

                for op in QA['answerOptions']:
                    if message['answer'] == op['type']:
                        if op['score'] == 1:
                            count += 1
                mbti_res[self.all_mbti[thread_id]].append({'Content': QA['content'], 'Question' : question, 'Answers': message})
                self.progress_bars[thread_id].update(1)
            elif args.method == 'conditioned':


                response = get_response(get_fandom_dimension(QA), args.model, args.temperature)
                if response is None:
                    while response is None:
                        response = get_response(get_fandom_dimension(QA), args.model, args.temperature)
                if response['answer'] == '':
                    while response['answer'] == '':
                        response = get_response(get_fandom_dimension(QA), args.model, args.temperature)

                # print(f'1------------{response}')
                prompt = get_conditioned_fandom_prompt(self.roles[thread_id]['name'], QA, self.all_mbti[thread_id], response['answer'])
                
                message = get_response(prompt, args.model, args.temperature)  # Call the api interface
                if message is None:
                    while message is None:
                        print('again\n')
                        message = get_response(prompt, args.model, args.temperature)

                for op in QA['answerOptions']:
                    if message['answer'] == op['type']:
                        if op['score'] == 1:
                            count += 1

                mbti_res[self.all_mbti[thread_id]].append({'Content': QA['content'], 'Question' : question, 'Answers': message})
                self.progress_bars[thread_id].update(1) 

            elif args.method == 'get_judge':
                response = get_response(get_fandom_dimension(QA), args.model, args.temperature)
                if response is None:
                    while response is None:
                        response = get_response(get_fandom_dimension(QA), args.model, args.temperature)
                # elif response['answer'] == '' or response['answer'] == 'unknown':
                #     while response['answer'] == '' or response['answer'] == 'unknown':
                #         response = get_response(get_fandom_dimension(QA), args.model, args.temperature)
            
                mbti_res[self.all_mbti[thread_id]].append({'Content': QA['content'], 'Question' : question, 'Answers': response})
                self.progress_bars[thread_id].update(1)        

            elif args.method == 'get_eval':
                
                prompt = get_conditioned_fandom_prompt(self.roles[thread_id]['name'], QA, self.all_mbti[thread_id], QA['Answers']['answer'])
                print(prompt)
                message = get_response(prompt, args.model, args.temperature)  # Call the api interface
                if message is None:
                    while message is None:
                        # print('again\n')
                        message = get_response(prompt, args.model, args.temperature)
                elif 'answer' not in message :
                    while 'answer' not in message:
                        message = get_response(prompt, args.model, args.temperature)
                elif message['answer'] == '' or message['answer'] == 'Cannot be determined':
                    while message['answer'] == '' or message['answer'] == 'Cannot be determined':
                        message = get_response(prompt, args.model, args.temperature)

                for op in QA['answerOptions']:
                    if message['answer'] == op['type']:
                        if op['score'] == 1:
                            count += 1
                mbti_res[self.all_mbti[thread_id]].append({'Content': QA['content'], 'Question' : question, 'Answers': message})
                self.progress_bars[thread_id].update(1) 
        # 线程安全地将数据存入字典
        with self.lock:
            self.results.append(mbti_res)
            self.counts.append({self.all_mbti[thread_id]: count})

    def start_threads(self, num_threads: int) -> None:
        """启动指定数量的线程"""
        self.threads.clear()
        if args.single:
            thread = threading.Thread(
                target=self.workers, 
                args=(0,),
                name=f"Worker-{0}"
            )
            self.threads.append(thread)
            thread.start()

        else:
            for i in range(num_threads, num_threads + 16):
                thread = threading.Thread(
                    target=self.workers, 
                    args=(i,),
                    name=f"Worker-{i}"
                )
                self.threads.append(thread)
                thread.start()

        
    
    def start_progress_bars(self, num_threads):
        if args.single:
            pbar = tqdm(
                        total=int(len(self.all_question)), 
                        desc=f"任务 {self.all_mbti[0]}", 
                        position=0
                    )  
            self.progress_bars.append(pbar)
        else:
            for i in range(num_threads, num_threads + 16):
                pbar = tqdm(
                    total=int(len(self.all_question)), 
                    desc=f"任务 {self.all_mbti[i]}", 
                    position=i
                )  
                self.progress_bars.append(pbar)

    def wait_for_completion(self) -> None:
        """等待所有线程完成"""
        for thread in self.threads:
            thread.join()
        print("所有线程已完成执行")

    def print_results(self) -> None:
        """打印结果字典"""
        with self.lock:
            if not self.results:
                print("error")
                return
            # if args.method == 'inherent':
            #     n = self.all_mbti[0] +'_'+ args.dataset if args.single else args.dataset
            #     with open('result/eval/' + n + args.dataset+'_' + args.model + '_' + args.method + '.json', "w") as file2:
            #         json.dump(self.results, file2, ensure_ascii=False, indent=4)
            #     with open('result/eval/' + n + args.dataset+'_' + args.model + '_' + args.method + '_score.json', "w") as file2:
            #         json.dump(self.counts, file2, ensure_ascii=False, indent=4)
            if args.method == 'conditioned':
                with open('result/eval/'+ args.dataset+'_' + args.model + '_' + args.method + '.json', "w") as file2:
                    json.dump(self.results, file2, ensure_ascii=False, indent=4)
                with open('result/eval/'+ args.dataset+'_' + args.model + '_' +  args.method + '_score.json', "w") as file2:
                    json.dump(self.counts, file2, ensure_ascii=False, indent=4)
            elif args.method == 'get_judge':
                n = self.all_mbti[0] +'_'+ args.dataset if args.single else args.dataset
                if 'llama-3-8b' in args.model:
                    modelname = 'llama-3-8b'
                elif 'llama-3-70b' in args.model:
                    modelname = 'llama-3-70b'
                else:
                    modelname = args.model
                with open('data/' + n +'_' + modelname + '_' + args.method + '.json', "w") as file2:
                    json.dump(self.results, file2, ensure_ascii=False, indent=4)
            elif args.method == 'get_eval':
                n = self.all_mbti[0] +'_'+ args.dataset if args.single else args.dataset
                if 'llama-3-8b' in args.model:
                    modelname = 'llama-3-8b'
                elif 'llama-3-70b' in args.model:
                    modelname = 'llama-3-70b'
                else:
                    modelname = args.model
                with open('result/eval/'+ n + '_' + modelname + '_' + args.method + '.json', "w") as file2:
                    json.dump(self.results, file2, ensure_ascii=False, indent=4)
                with open('result/eval/'+ n + '_' + modelname + '_' +  args.method + '_score.json', "w") as file2:
                    json.dump(self.counts, file2, ensure_ascii=False, indent=4)
            elif args.method == 'inherent':
                n = self.all_mbti[0] +'_'+ args.dataset if args.single else args.dataset
                if 'llama-3-8b' in args.model:
                    modelname = 'llama-3-8b'
                elif 'llama-3-70b' in args.model:
                    modelname = 'llama-3-70b'
                else:
                    modelname = args.model
                with open('result/eval/'+ n + '_' + modelname + '_' + args.method + '.json', "w") as file2:
                    json.dump(self.results, file2, ensure_ascii=False, indent=4)
                with open('result/eval/'+ n + '_' + modelname + '_' +  args.method + '_score.json', "w") as file2:
                    json.dump(self.counts, file2, ensure_ascii=False, indent=4)
class FandomEvalAgent:
    def __init__(self):
        self.dataset = self.load_data()

    def load_data(self):
        with open('data/fantom_v1.json', encoding='UTF-8') as file:
            fantom = json.load(file)
        return fantom
    
    def setup_fantom(self):
        
        beliefQAs = []
        nfoAccessibilityQA = []
        answerabilityQA = []
        for _qa in self.dataset:
            context = _qa['full_context']
            for _belief_qa in _qa['beliefQAs']:
                # Multiple Choice Belief Questions
                choices, answer_goes_last = self.set_beliefQA_multiple_choices(_belief_qa)
                if answer_goes_last:
                    answer_A = 1
                    answer_B = 0
                else:
                    answer_A = 0
                    answer_B = 1
                beliefQAs.append({
                    'content': context,
                    'question': _belief_qa['question'],
                    "answerOptions": [
                        { "type": "A", "answer": choices[0], "score": answer_A },
                        { "type": "B", "answer": choices[1], "score": answer_B }
                    ]
                })
            for _infoAccessibilityQAs_binary in _qa['infoAccessibilityQAs_binary']:
                if _infoAccessibilityQAs_binary['correct_answer'] == 'yes':
                    answer_A = 1
                    answer_B = 0
                else:
                    answer_A = 0
                    answer_B = 1
                nfoAccessibilityQA.append({
                    'content': context,
                    'fact_q': _qa['factQA']['question'],
                    'fact_a': _qa['factQA']['correct_answer'],
                    'question': _infoAccessibilityQAs_binary['question'],
                    "answerOptions": [
                        { "type": "A", "answer": 'yes', "score": answer_A },
                        { "type": "B", "answer": 'no', "score": answer_B }
                    ]
                })
            
            for _answerabilityQAs_binary in _qa['answerabilityQAs_binary']:
                if _answerabilityQAs_binary['correct_answer'] == 'yes':
                    answer_A = 1
                    answer_B = 0
                else:
                    answer_A = 0
                    answer_B = 1
                answerabilityQA.append({
                    'content': context,
                    'fact_q': _qa['factQA']['question'],
                    'fact_a': _qa['factQA']['correct_answer'],
                    'question': _answerabilityQAs_binary['question'],
                    "answerOptions": [
                        { "type": "A", "answer": 'yes', "score": answer_A },
                        { "type": "B", "answer": 'no', "score": answer_B }
                    ]
                })
        
        print(len(beliefQAs), len(nfoAccessibilityQA), len(answerabilityQA))
        with open('beliefQAs_data.json', "w") as file:
                json.dump(beliefQAs, file, ensure_ascii=False, indent=4)
        with open('nfoAccessibilityQA_data.json', "w") as file:
                json.dump(nfoAccessibilityQA, file, ensure_ascii=False, indent=4)
        with open('answerabilityQA_data.json', "w") as file:
                json.dump(answerabilityQA, file, ensure_ascii=False, indent=4)

    def set_beliefQA_multiple_choices(self, qa):
        option_correct = qa['correct_answer']
        option_wrong = qa['wrong_answer']
        answer_goes_last = random.choice([True, False])
        if answer_goes_last:
            choices = [option_correct, option_wrong]
        else:
            choices = [option_wrong, option_correct]

        return choices, answer_goes_last
    
    def evaluate_binary_q(self):
        return True

def main(args):

    if args.get_fandom_dataset:
        fandom = FandomEvalAgent()
        fandom.setup_fantom()
    else:
        for step in range(args.steps):
            # 创建数据管理器实例
            data_manager = GeneratedAgent(args)
            for group in [0]:
                # 启动2个线程
                data_manager.start_progress_bars(group)
                data_manager.start_threads(group)
                # 等待线程完成
                data_manager.wait_for_completion()
            # 打印结果
            data_manager.print_results()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--method', 
                        type=str, 
                        default = 'get_eval'
    ) # inherent, direct, conditioned, get_judge, get_eval
    parser.add_argument('--temperature', 
                        type=float, 
                        default= 0.6
    )
    parser.add_argument('--model', 
                        type=str, 
                        default= 'gemini-2.5-pro'
    )# gpt-3.5-turbo-1106, gpt-4o, llama-3-8b-instruct, llama-3-70b-instruct, gemini-2.5-pro, gemini-2.5-flash
    parser.add_argument('--steps', 
                        type=int, 
                        default= 1
    )
    # )# 1571 ----  beliefQAs, 3571  ----   answerabilityQA, nfoAccessibilityQA
    parser.add_argument('--get-fandom-dataset', 
                        type=bool, 
                        default= False
    )
    parser.add_argument('--dataset', 
                        type=str, 
                        default= 'nfoAccessibilityQA7'
    )# beliefQAs, answerabilityQA, nfoAccessibilityQA
    parser.add_argument('--single', 
                        type=bool, 
                        default= True
    )
    parser.add_argument('--single-mbti', 
                        type=str, 
                        default= 'ENTJ'
    )#ENFJ,ENTJ ---3
    args = parser.parse_args()
    main(args)
    

