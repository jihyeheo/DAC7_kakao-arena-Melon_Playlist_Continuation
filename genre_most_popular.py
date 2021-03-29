# -*- coding: utf-8 -*-
from collections import Counter

import fire
from tqdm import tqdm

from arena_util import load_json
from arena_util import write_json
from arena_util import remove_seen
from arena_util import most_popular


class GenreMostPopular:
    def _song_mp_per_genre(self, song_meta, global_mp):
        res = {}
        # key는 song_meta에 있던 genre, value는 해당 genre에 속한 id값
        for sid, song in song_meta.items():
            for genre in song['song_gn_gnr_basket']:
                res.setdefault(genre, []).append(sid)

        for genre, sids in res.items():
            # Before: res {genre : song_id}
            # After: res {genre : Counter(song_id : 개수)}
            res[genre] = Counter({k: global_mp.get(int(k), 0) for k in sids})
            # 가장 많은 상위 200개 song_id만 추출
            res[genre] = [k for k, v in res[genre].most_common(200)]

        return res

    def _generate_answers(self, song_meta_json, train, questions):
        # key를 song_id value를 해당 song_id에 대한 정보로 dictionary 생성
        song_meta = {int(song["id"]): song for song in song_meta_json}
        # 상위 200개 곡
        song_mp_counter, song_mp = most_popular(train, "songs", 200)
        # 상위 100개 태그
        tag_mp_counter, tag_mp = most_popular(train, "tags", 100)
        song_mp_per_genre = self._song_mp_per_genre(song_meta, song_mp_counter)

        answers = []
        for q in tqdm(questions):
            genre_counter = Counter()

            for sid in q["songs"]:
                for genre in song_meta[sid]["song_gn_gnr_basket"]:
                    genre_counter.update({genre: 1})

            top_genre = genre_counter.most_common(1)
            # 가장 인기있는 장르가 존재하면
            if len(top_genre) != 0:
                # 해당 장르에서 가장 많이 등장한 song 추천
                cur_songs = song_mp_per_genre[top_genre[0][0]]
            else:
                # 아니면 가장 많이 등장한 노래 추천
                cur_songs = song_mp

            answers.append({
                "id": q["id"],
                "songs": remove_seen(q["songs"], cur_songs)[:100],
                "tags": remove_seen(q["tags"], tag_mp)[:10]
            })

        return answers

    def run(self, song_meta_fname, train_fname, question_fname):
        print("Loading song meta...")
        song_meta_json = load_json(song_meta_fname)

        print("Loading train file...")
        train_data = load_json(train_fname)

        print("Loading question file...")
        questions = load_json(question_fname)

        print("Writing answers...")
        answers = self._generate_answers(song_meta_json, train_data, questions)
        write_json(answers, "results/results.json")


if __name__ == "__main__":
    fire.Fire(GenreMostPopular)
