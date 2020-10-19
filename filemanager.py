import json
import os.path

class FileManager():

    def update_log(log_str):
        if not os.path.exists('log.txt'):
            file = open("log.txt", "w")
        else:
            file = open("log.txt", "a")
        file.writelines([log_str, '<br>', '\n'])
        file.close()



    def get_log():
        result_str = 'log: <br>'
        with open("log.txt", "r") as log_file:
            contents = log_file.readlines()
        contents.reverse()
        for line in contents:
            result_str += line
        return result_str        


    def find_cached_value(str_func_with_args):
        if not os.path.exists('cach.json'):
            file = open("cach.json", "w")
            file.writelines('{}')
            file.close()
        with open("cach.json", "r") as cach_file:
            functions_questions_and_answers = json.load(cach_file)
        if str_func_with_args in functions_questions_and_answers:
            return functions_questions_and_answers[str_func_with_args]
        else:
            return None


    def upload_value_to_cach(str_func_with_args_as_key, value):
        if not os.path.exists('cach.json'):
            file = open("cach.json", "w")
            file.writelines('{}')
            file.close()
        with open("cach.json", "r") as cach_file:
            functions_questions_and_answers = json.load(cach_file)
        new_data = {str_func_with_args_as_key: value}
        functions_questions_and_answers.update(new_data)
        with open("cach.json", "w") as cach_file:
            json.dump(functions_questions_and_answers, cach_file)
