from api import *
from prompt import *
import random
import threading
from tqdm import tqdm
import argparse
from data.mbti_initial_weight import Players

class MbtiFitness:
    def __init__(self):
        # Initialize eight functions with starting value of 23
        self.functions = {
            'I': 0,
            'E': 0,
            'S': 0,
            'N': 0,
            'F': 0,
            'T': 0,
            'P': 0,
            'J': 0
        }
    def update_score(self, question, answer):
        """
        Update function score based on question and answer
        
        Parameters:
            question: Question content (not used in calculation, but kept for interface)
            answer: Answer value, must be integer from A and B
        """
        if answer == 'A':
            dimension = question['answerOptions'][0]['score']
            self.functions[dimension] += 1
        elif answer == 'B':
            dimension = question['answerOptions'][1]['score']
            self.functions[dimension] += 1

    def get_scores(self):
        """
        Get current scores of all functions
        
        Returns:
            Dictionary containing scores of all eight functions
        """
        return self.functions.copy()
    
    def reset_scores(self):
        """
        Reset all function scores to initial value of 0
        """
        for function in self.functions:
            self.functions[function] = 0

class GeneratedAgent(MbtiFitness):
    def __init__(self, args):
        self.args = args
        self.all_question = self.load_data('question')
        self.roles = Players
        self.all_mbti = self.load_data('mbti')
        # self.all_mbti = ['INTJ']
        self.lock = threading.Lock()
        self.threads = []
        self.local_data = threading.local()

        self.progress_bars=[]

        self.results = []
        self.counts = {}
    def load_data(self, data_type):
        if data_type == 'question':
            with open('mbti_93_en.json', encoding='UTF-8') as file:
                questions = json.load(file)
            return questions
        elif data_type == 'mbti':
            if args.method != 'inherent':
                return list(WEIGHT.keys())
            else:
                return ['ENTJ']

    def workers(self, thread_id):
        """线程函数：生成数组数据"""
        self.local_data.mbti_fitness = MbtiFitness()

        mbti_res =  {self.all_mbti[thread_id] : []}
        for QA in self.all_question:
            question = QA['question']
            # dimension = QA['answerOptions'][0]['score']
            
            if args.method == 'direct':
                prompt = get_direct_prompt(self.roles[thread_id]['name'], QA, self.all_mbti[thread_id])
                # if response is None:
                #     while response is None:
                #         response = get_direct_prompt(self.roles[thread_id]['name'], question, self.all_mbti[thread_id])
    
            # elif args.method == 'direct':
            #     prompt = get_direct_prompt(self.roles[thread_id]['name'], question, self.all_mbti[thread_id])
            elif args.method == 'conditioned':
                response = get_response(get_question_dimension(QA), args.model, args.temperature)
                if response is None:
                    while response is None:
                        response = get_response(get_question_dimension(QA), args.model, args.temperature)
                if response['answer'] == '':
                    while response['answer'] == '':
                        response = get_response(get_question_dimension(QA), args.model, args.temperature)
                # print(f'1------------{response}')
                prompt = get_conditioned_prompt(self.roles[thread_id]['name'], QA, self.all_mbti[thread_id], response['answer'])
            message = get_response(prompt, args.model, args.temperature)  # Call the api interface
            if message is None:
                while message is None:
                    print('again\n')
                    message = get_response(prompt, args.model, args.temperature)

            self.local_data.mbti_fitness.update_score(QA, message['answer'])
            
            mbti_res[self.all_mbti[thread_id]].append({'Question' : question, 'Answers': message})
            self.progress_bars[thread_id].update(1) 

        # 线程安全地将数据存入字典
        with self.lock:
            self.results.append(mbti_res)
            self.counts[self.all_mbti[thread_id]] = self.local_data.mbti_fitness.get_scores()

    def start_threads(self, num_threads: int) -> None:
        """启动指定数量的线程"""
        self.threads.clear()
        
        for i in range(num_threads, num_threads + 8):
            thread = threading.Thread(
                target=self.workers, 
                args=(i,),
                name=f"Worker-{i}"
            )
            self.threads.append(thread)
            thread.start()

        # thread = threading.Thread(
        #         target=self.workers, 
        #         args=(0,),
        #         name=f"Worker-{0}"
        #     )
        # self.threads.append(thread)
        # thread.start()
    
    def start_progress_bars(self, num_threads):

        for i in range(num_threads, num_threads + 8):
            pbar = tqdm(
                total=int(args.question_num), 
                desc=f"任务 {self.all_mbti[i]}", 
                position=i
            )  
            self.progress_bars.append(pbar)


        # pbar = tqdm(
        #     total=int(args.question_num), 
        #     desc=f"任务 {self.all_mbti[0]}", 
        #     position=0
        # )  
        # self.progress_bars.append(pbar)

    def wait_for_completion(self) -> None:
        """等待所有线程完成"""
        for thread in self.threads:
            thread.join()
        print("所有线程已完成执行")
    
    def get_results(self):
        """获取结果"""
        with self.lock:
            return self.results.copy, self.counts.copy  # 返回副本避免外部修改
    
    def clear_results(self) -> None:
        """清空结果"""
        with self.lock:
            self.results.clear()
            self.counts.clear()
        print("结果已清空")
    
    def print_results(self) -> None:
        """打印结果字典"""
        with self.lock:
            if not self.results:
                print("error")
                return
            if 'llama-3-8b' in args.model:
                modelname = 'llama-3-8b'
            elif 'llama-3-70b' in args.model:
                modelname = 'llama-3-70b'
            else:
                modelname = args.model
            with open('result/exp1_' + modelname + '_' + args.method + '.json', "w") as file2:
                json.dump(self.results, file2, ensure_ascii=False, indent=4)
            with open('result/exp1_' + modelname + '_' +  args.method + '_score.json', "w") as file2:
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
                choices, answer = self.set_beliefQA_multiple_choices(_belief_qa)
                beliefQAs.append({
                    'context': context,
                    'question': _belief_qa['question'],
                    "answerOptions": [
                        { "type": "A", "answer": choices[0], "score": answer },
                        { "type": "B", "answer": choices[1], "score": not answer }
                    ]
                })
            for _infoAccessibilityQAs_binary in _qa['infoAccessibilityQAs_binary']:
                if _infoAccessibilityQAs_binary['correct_answer'] == 'yes':
                    answer = True
                else:
                    answer = False
                nfoAccessibilityQA.append({
                    'context': context,
                    'question': _infoAccessibilityQAs_binary['question'],
                    "answerOptions": [
                        { "type": "A", "answer": 'yes', "score": answer },
                        { "type": "B", "answer": 'no', "score": not answer }
                    ]
                })
            
            for _answerabilityQAs_binary in _qa['answerabilityQAs_binary']:
                if _answerabilityQAs_binary['correct_answer'] == 'yes':
                    answer = True
                else:
                    answer = False
                answerabilityQA.append({
                    'context': context,
                    'question': _answerabilityQAs_binary['question'],
                    "answerOptions": [
                        { "type": "A", "answer": 'yes', "score": answer },
                        { "type": "B", "answer": 'no', "score": not answer }
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
        if qa['question_type'].endswith(":inaccessible"):
            option_a = qa['wrong_answer']
            option_b = qa['correct_answer']
        else:
            option_a = qa['wrong_answer']
            option_b = qa['correct_answer']

        answer_goes_last = random.choice([True, False])
        if answer_goes_last:
            choices = [option_b, option_a]
        else:
            choices = [option_a, option_b]

        return choices, answer_goes_last
    
    def evaluate_binary_q(self):
        return True

def main(args):

    if args.fandom_dataset:
        fandom = FandomEvalAgent()
        fandom.setup_fantom()
    else:
        for step in range(args.steps):
            personlity = MbtiFitness()
            # 创建数据管理器实例
            data_manager = GeneratedAgent(personlity)
            for group in [0, 8]:
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
                        default = 'direct'
    ) # inherent, direct, conditioned
    parser.add_argument('--temperature', 
                        type=float, 
                        default= 0.6
    )
    parser.add_argument('--model', 
                        type=str, 
                        default= 'gemini-2.5-flash'
    )# gpt-3.5-turbo-1106, gpt-4o, llama-3-8b-instruct, meta-llama/llama-3-70b-instruct, gemini-2.5-pro, gemini-2.5-flash
    parser.add_argument('--steps', 
                        type=int, 
                        default= 1
    )
    parser.add_argument('--question_num', 
                        type=int, 
                        default= 93
    )
    parser.add_argument('--fandom-dataset', 
                        type=bool, 
                        default= False
    )
    # parser.add_argument('--degree', type=str, default= 'MID')
    args = parser.parse_args()
    main(args)
    

