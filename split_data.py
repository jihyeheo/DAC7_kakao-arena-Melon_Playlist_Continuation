# -*- coding: utf-8 -*-
import copy
import random
# fire 패키지는 파이썬에서 모든 객체를 command line interface로 만들어준다.
import fire
import numpy as np

# 같은 폴더에 arena_util.py에서 함수 호출
from arena_util import load_json
from arena_util import write_json


class ArenaSplitter:
    def _split_data(self, playlists):
        tot = len(playlists)
        # 8:2로 나누기
        train = playlists[:int(tot*0.80)]
        val = playlists[int(tot*0.80):]

        return train, val

    def _mask(self, playlists, mask_cols, del_cols):
        # 깊은 복사 : 내부에 객체들까지 모두 새롭게 copy 
        q_pl = copy.deepcopy(playlists)
        a_pl = copy.deepcopy(playlists)

        for i in range(len(playlists)):
            # 삭제할 컬럼
            for del_col in del_cols:
                q_pl[i][del_col] = []
                if del_col == 'songs':
                    # 상위 100개 곡 추출
                    a_pl[i][del_col] = a_pl[i][del_col][:100]
                elif del_col == 'tags':
                    # 상위 10개 태그 추출
                    a_pl[i][del_col] = a_pl[i][del_col][:10]
            # masking
            for col in mask_cols:
                mask_len = len(playlists[i][col])
                mask = np.full(mask_len, False)
                # 절반은 true, 절반은 false
                mask[:mask_len//2] = True
                np.random.shuffle(mask)

                q_pl[i][col] = list(np.array(q_pl[i][col])[mask])
                a_pl[i][col] = list(np.array(a_pl[i][col])[np.invert(mask)])

        return q_pl, a_pl

    def _mask_data(self, playlists):
        playlists = copy.deepcopy(playlists)
        tot = len(playlists)
        song_only = playlists[:int(tot * 0.3)] # 곡만 존재
        song_and_tags = playlists[int(tot * 0.3):int(tot * 0.8)] # 곡, 태그 둘 다 존재
        tags_only = playlists[int(tot * 0.8):int(tot * 0.95)] # 태그만 존재
        title_only = playlists[int(tot * 0.95):] # 제목만 존재

        print(f"Total: {len(playlists)}, "
              f"Song only: {len(song_only)}, "
              f"Song & Tags: {len(song_and_tags)}, "
              f"Tags only: {len(tags_only)}, "
              f"Title only: {len(title_only)}")

        song_q, song_a = self._mask(song_only, ['songs'], ['tags'])
        songtag_q, songtag_a = self._mask(song_and_tags, ['songs', 'tags'], [])
        tag_q, tag_a = self._mask(tags_only, ['tags'], ['songs'])
        title_q, title_a = self._mask(title_only, [], ['songs', 'tags'])

        q = song_q + songtag_q + tag_q + title_q
        a = song_a + songtag_a + tag_a + title_a
        
        # random하게 섞기
        shuffle_indices = np.arange(len(q))
        np.random.shuffle(shuffle_indices)

        q = list(np.array(q)[shuffle_indices])
        a = list(np.array(a)[shuffle_indices])

        return q, a
    # run method 지정해주기
    def run(self, fname):
        # raondom shuffle 때문에 seed 지정
        random.seed(777)

        print("Reading data...\n")
        # json 파일 불러오기
        playlists = load_json(fname)
        # 불러온 파일 순서 섞기
        random.shuffle(playlists)
        print(f"Total playlists: {len(playlists)}")

        print("Splitting data...")
        # split
        train, val = self._split_data(playlists)

        # train, val 나눈 데이터 json 파일 작성
        print("Original train...")
        write_json(train, "orig/train.json")
        print("Original val...")
        write_json(val, "orig/val.json")

        print("Masked val...")
        # masking 작업 
        val_q, val_a = self._mask_data(val)
        write_json(val_q, "questions/val.json")
        write_json(val_a, "answers/val.json")


if __name__ == "__main__":
    fire.Fire(ArenaSplitter)
