import sys
import json
import random
import os
import shutil
from datetime import datetime
# from kivy.app import App
# from kivy.uix.widget import Widget
# from kivy.clock import Clock
# from kivy.properties import (
#     NumericProperty, ReferenceListProperty, ObjectProperty, StringProperty
# )


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class Vocab:
    def __init__(self, vocab_file):
        self._vocab_file = vocab_file
        self._vocab_dicts = json.load(open(vocab_file))
        self.active_target = None

    def __getitem__(self, item):
        return self._vocab_dicts[item]

    def get_weighted_random_entry(self):
        max_val = sum(map(lambda x: x.get('frequency'), self._vocab_dicts))
        selector = random.randint(0, int(max_val))
        counter = 0
        target_idx = -1
        for i, e in enumerate(self._vocab_dicts):
            counter += e.get('frequency')
            if counter >= selector:
                target_idx = i
                break
        self.active_target = self[target_idx]
        return self.active_target

    def multiply_frequency(self, coef):
        self.active_target['frequency'] = max(1, self.active_target.get('frequency') * coef)
        self._write_vocab()

    def make_next_char_possible(self):
        added = None
        for v in self._vocab_dicts:
            if v.get('frequency') == 0:
                v['frequency'] = 4
                added = v
                break
        self._write_vocab()
        return pretty_format_vocab([added], False)

    def ratio_of_chars_in_testset(self):
        return f"{self.chars_in_traning_set()}/{len(self._vocab_dicts)}"

    def chars_in_traning_set(self):
        return sum(map(lambda x: 0 if x.get('frequency') == 0 else 1, self._vocab_dicts))

    def check_if_all_leq_one(self):
        for v in self._vocab_dicts:
            if v.get('frequency') > 1:
                return False
        return True

    def set_all_frequencies(self, val):
        for v in self._vocab_dicts:
            v['frequency'] = val
        self._write_vocab()

    def record_test_result(self, answer_correct):
        self.active_target['correct' if answer_correct else 'incorrect'].append(datetime.now().strftime("%d/%m/%Y_%H:%M:%S"))

    def str_total_correct(self):
        n_correct = sum(map(lambda x: len(x.get('correct')), self._vocab_dicts))
        n_incorrect = sum(map(lambda x: len(x.get('incorrect')), self._vocab_dicts))
        return f"{n_correct} / {n_correct + n_incorrect}"

    def active_high_frequency_sorted(self):
        active = filter(lambda x: x.get('frequency') != 0, self._vocab_dicts)
        return sorted(active, key=lambda x: x.get('frequency'), reverse=True)

    def _write_vocab(self):
        dump = json.dumps(self._vocab_dicts, indent=4)
        with open(self._vocab_file, 'w') as f:
            f.write(dump)


def pretty_format_vocab(vocab, show_frequency=True):
    str_v = ''
    for i,e in enumerate(vocab):
        str_v += f"{e.get('target')} - {e.get('translation')}{'  ' + str(e.get('frequency')) if show_frequency else ''}" + ("\n" if i < len(vocab) - 1 else '')
    return str_v


def repl():
    vocab_base_file = 'Vocabularies/alternating_kana_base.json'
    vocab_file = 'Vocabularies/alternating_kana_default.json'
    if not os.path.isfile(vocab_file):
        if os.path.isfile(vocab_base_file):
            print(f"{bcolors.WARNING}No progression safe file found. Generating new progression safe file.{bcolors.ENDC}\n")
            shutil.copyfile(vocab_base_file, vocab_file)
        else:
            raise Exception(f"The base vacabulary file {os.path.abspath(vocab_base_file)} is missing.")
    # while True:
    #     input_val = input("Type exit at any prompt to close application.\n"
    #                       "Enter 1 to train hiragana, enter 2 to train katakana.")
    #     if input_val == "1":
    #         vocab_file = 'hiragana_data_1.json'
    #         break
    #     elif input_val == "2":
    #         vocab_file = 'katakana_data_1.json'
    #         break
    #     elif input_val == "exit":
    #         sys.exit(0);
    #     else:
    #         print("Not a valid option");

    print("Type exit at any prompt to close application.\n"
          "Type stats to see your statistics.\n"
          "Enter the correct romaji.");
    vocab = Vocab(vocab_file)
    while True:
        entry = vocab.get_weighted_random_entry()
        wrong_answers = 0
        while True:
            answer = input(f"\n{entry.get('target')}: ")
            if answer == 'exit':
                sys.exit(0)
            elif answer == 'stats':
                print(f"You got {vocab.str_total_correct()} correct in total.")
                print(f"{vocab.ratio_of_chars_in_testset()} chars in test-set.")
                print(f"Highest frequency entries:")
                print(pretty_format_vocab(vocab.active_high_frequency_sorted()[:6]))
            elif answer == entry.get('translation'):
                vocab.multiply_frequency(0.5)
                print(f"{bcolors.OKBLUE}correct, f:{entry.get('frequency')}{bcolors.ENDC}")
                vocab.record_test_result(True)
                if vocab.check_if_all_leq_one():
                    added_char = vocab.make_next_char_possible()
                    if added_char:
                        print(f"{bcolors.OKGREEN}{bcolors.BOLD}{added_char}{bcolors.ENDC} added to test-set. {vocab.ratio_of_chars_in_testset()} chars in test-set.")
                break
            else:
                vocab.multiply_frequency(4)
                wrong_answers += 1
                print(f"{bcolors.WARNING}WRONG f:{entry.get('frequency')}{bcolors.ENDC}" + (f" => {entry.get('translation')}" if wrong_answers > 1 else ''))
                vocab.record_test_result(False)


# class Questioner(Widget):
#     def logic(self):
#         cli_game()
#
#
# class KanaApp(App):
#     def build(self):
#         q = Questioner()
#         Clock.schedule_interval(q.logic(), 1.0 / 60.0)
#         return q


if __name__ == '__main__':
    repl()
    #KanaApp().run()