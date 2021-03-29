# -*- coding: utf-8 -*-
import fire
from tqdm import tqdm

from arena_util import load_json
from arena_util import write_json
from arena_util import remove_seen
from arena_util import most_popular


class MostPopular:
    def _generate_answers(self, train, questions):
        # 빈도수가 가장 높은 값을 출력한다.
        _, song_mp = most_popular(train, "songs", 200)
        _, tag_mp = most_popular(train, "tags", 100)

        answers = []

        for q in tqdm(questions):
            answers.append({
                "id": q["id"],
                "songs": remove_seen(q["songs"], song_mp)[:100],
                "tags": remove_seen(q["tags"], tag_mp)[:10],
            })

        return answers # question에 적힌 노래를 제외한 상위를 불러오기
    
    # train_fname=train.json, question_fname=val.json
    def run(self, train_fname, question_fname):
        print("Loading train file...")
        train = load_json(train_fname)

        print("Loading question file...")
        questions = load_json(question_fname)

        print("Writing answers...")
        answers = self._generate_answers(train, questions)
        write_json(answers, "results/results.json")


# MostPopular이 class로 정의되어있는데하나의 클래스를 interpreter 형식으로 인식시켜주게 만들어준다.
# interpreter란 사용자가 입력한 소스 코드를 실행하는 환경을 뜻한다.
if __name__ == "__main__":
    fire.Fire(MostPopular)
