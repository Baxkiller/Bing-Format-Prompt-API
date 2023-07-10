# -*- codeing = utf-8 -*-
# @Time       : 2023/7/10 17:37
# @Author     : Baxkiller
# @File       : class_library.py
# @Software   : PyCharm
# @Description: 使用的相关类定义和实现
import json
import copy


class Responce:
    def __init__(self, save_path):
        self.save_path = save_path
        try:
            with open(save_path, "r", encoding = 'utf-8') as f:
                self.responces = json.load(f)
        except json.decoder.JSONDecodeError:
            self.responces = {}

    def save(self):
        with open(self.save_path, "w", encoding = 'utf-8') as f:
            json.dump(self.responces, f, indent = 2, ensure_ascii = False)

    def update(self, paper, prompt, responce: str):
        responce = responce.encode('utf-8')
        if isinstance(responce, bytes):
            responce = str(responce, encoding = 'utf-8')
        if responce is None or responce == "" or responce == " ":
            return

        paper_title = paper["title"]
        if paper_title not in self.responces:
            self.responces[paper_title] = copy.deepcopy(paper)

        if "chat" not in self.responces[paper_title]:
            self.responces[paper_title]["chat"] = []
        self.responces[paper_title]["chat"].append(prompt)
        self.responces[paper_title]["chat"].append(responce)

        self.save()


class Papers:
    def __init__(self, load_path):
        self.filepath = load_path
        with open(load_path, "r", encoding = "utf-8") as f:
            self.papers = json.load(f)
        self.index = 0
        self.first = True

    def get_new_paper(self):
        # 保存上次已经完成的论文
        if not self.first:
            self.papers[self.index]["prompted"] = True
            with open(self.filepath, "w", encoding = 'utf-8') as f:
                json.dump(self.papers, f, indent = 2)
        else:
            self.first = False

        index = self.index
        # 找到下一个新的未经问询的论文
        while "prompted" in self.papers[index] and self.papers[index]["prompted"] is True:
            index += 1
            if index == len(self.papers):
                print("FINISHED ALL!")

        # 返回下个论文
        self.index = index
        return self.papers[self.index]


class Prompt:
    def __init__(self, load_path, sequence):
        self.filepath = load_path
        self.sequence = sequence
        with open(load_path, "r", encoding = 'utf-8') as f:
            self.prompts = json.load(f)
        self.index = -1

    def get_next_prompt(self):
        try:
            self.index = self.index + 1
            key = self.sequence[self.index]
        except IndexError:
            self.index = -1
            return None
        print(f"Prompt Index: {self.index}")
        return self.prompts[key]

    def __getitem__(self, index):
        prompt_key = self.sequence[index]
        return self.prompts[prompt_key]

    def __len__(self):
        return len(self.sequence)


class InstGenerator:
    def __init__(self, prompt_sequence, prompt_filepath,
                 paper_filepath, responce_filepath):
        self.papers = Papers(paper_filepath)
        self.prompts = Prompt(prompt_filepath, prompt_sequence)
        self.responce = Responce(responce_filepath)

        self.prompt = None
        self.paper = self.papers.get_new_paper()

    def get_prompt(self, resp):
        self.responce.update(self.paper, self.prompt, resp)

        self.prompt = self.prompts.get_next_prompt()
        if self.prompt is None:
            self.prompt = self.prompts.get_next_prompt()
            self.paper = self.papers.get_new_paper()

        paper_info = self.paper
        paper_title = ":".join(paper_info["title"].split(":")[1:])
        return self.prompt.format(paper_title)
