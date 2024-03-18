''' questionary extansion provide a helper to directly init a class from asking question'''
import questionary
from typing import Callable, Optional, TypeVar, Type,TypeAlias, Any, Dict,List,get_origin


T = TypeVar('T')
K = TypeVar('K')
V = TypeVar('V')

class custom_option():
    ''' 
    custom init question of specific field

    return_formatter will get the answer and *args,**kwargs as input
    '''
    def __init__(self,name:str,custom_question:questionary.Question,return_formatter:Optional[Callable] = None,*args,**kwargs):
        self.name = name
        self.custom_question:str = custom_question
        self.return_formatter:Callable = return_formatter
        self.r_args = args
        self.r_kwargs = kwargs
    def to_dict(self):
        return {
            self.name:{
                'question':self.custom_question,
                'return':self.return_formatter,
                'params_for formater':[self.r_args,self.r_kwargs]
            }
        }

def type_check(x:str,t:type):
    match t.__name__:
        case 'int':
            return x.isnumeric()
        case 'str':
            return x.strip()
        case _:
            raise TypeError('Not support type')

def get_feild(cls:Type[T]) -> Dict[str,str]:
    '''
    get comment of A class
    Notice: only support patern like` <Args_name> Comments`'''
    res = {}

    for line in cls.__dict__.get('__doc__','').strip().replace('\n','').split('<'):
        # print(f'Line:{line}')
        if line:
            r = line.replace('\n','').split('>')
            if r:
                res[r[0]] = r[1].strip()
    return res

def is_dict_type(tp: Type) -> bool:
    origin = get_origin(tp)
    return origin is not None and issubclass(origin, dict)

def is_list_type(tp: Type) -> bool:
    origin = get_origin(tp)
    return origin is not None and issubclass(origin, list)

def class_init_from_question(cls:Type[T],customoption:Optional[Dict[str,custom_option]] = {}) -> T:
    '''
    init a class from user input

    Question mag comes from the comment of the class. using format { <attribute> QuestionMsg }

    cls.__init__ should be 
    ```
    def __init__(self,**data):
        self.__dict__.update(data)
    ```

    customoption:[
        'name':{
            'question': <Question>
            'return': <Callable>
        ]
    }'''
    instance_dict = {}
    field = get_feild(cls)
    for field_name, field_type in cls.__annotations__.items():
        field_help = field.get(field_name,f'Please input {field_name}')
        # as key
        if field_name in customoption: # we first consider key with customoption
            custom_field = customoption.get(field_name,None)
            question:questionary.Question = custom_field.custom_question
            return_formatter:Callable = custom_field.return_formatter
            if question and isinstance(question,questionary.Question):
                ans = question.ask()
                if return_formatter:
                    ans = return_formatter(ans,*custom_field.r_args,**custom_field.r_kwargs)
                # end return formatter
            # end question
            instance_dict[field_name] = ans
            continue
        # end customation

        # below will derive question based on attribute type
        if is_list_type(field_type):
            # member_type = field_type.__args__
            question = questionary.text(
                f'{field_help}:',
                # validate=lambda x: x.strip()
            )
            answer = ask_multiple_times(question)
            instance_dict[field_name] = answer
        elif field_type == int:
            question = questionary.text(
                f'{field_help}:',
                validate=lambda x: x.isnumeric(),
            )
            answer = question.ask()
            instance_dict[field_name] = int(answer)
        elif field_type == str:
            question = questionary.text(
                f'{field_help}:',
                # validate=lambda x: x.strip(),
            )
            answer = question.ask()
            instance_dict[field_name] = answer
        elif field_type == bool:
            question = questionary.confirm(
                f'{field_help}'
            )
            instance_dict[field_name] = question.ask()
        elif is_dict_type(field_type):
            question = questionary.text(
                f'{field_help}',
                validate=lambda x: ':' in x
            )
            answer = ask_multiple_times(question)

            answer_dict = {}
            for eachkv in answer:
                afsp = eachkv.split(':',1) # only split first :
                if len(afsp) > 1:
                    answer_dict[afsp[0]] = afsp[1]

            instance_dict[field_name] = answer_dict
        else:
            raise ValueError(f'Unsupported type for field {field_name}: {field_type}')
    return cls(**instance_dict)


def ask_multiple_times(
        question:questionary.Question,
        confrim_msg:str = 'Continue type in?',
        auto_enter:bool = False
    ) -> List[str]:
    '''
    Ask a question for many times, return List<answer>'''

    confrim_q = questionary.confirm(confrim_msg,qmark='',auto_enter=auto_enter)
    answers:List[str] = []
    keep_on = True

    while keep_on:
        answer = question.ask()
        keep_on = confrim_q.ask()
        # print(f'in ask multiple {answer}')
        answers.append(answer)

    return answers

# class QuestionaryExtansionTimedelta(questionary.Question):
#     '''return dict which can init timedelta class
#     Return:
#         {'days': x, 'hours': x,'minutes':x}'''
#     def __init__(self) -> 'QuestionaryExtansionTimedelta':
#         # super().__init__(application)
#         pass
#     @classmethod
#     def ask(cls) -> Dict[str,str]:
#         while True:
#             days = int(questionary.text('申请使用的天数：',default='0',
#                                     validate= lambda x: x.isnumeric()).ask())
#             hours = int(questionary.text('申请使用的小时：',default='0',
#                                     validate= lambda x: x.isnumeric()).ask())
#             minutes = int(questionary.text('申请使用的分钟：',default='1',
#                                     validate= lambda x: x.isnumeric()).ask())
#             if days or hours or minutes:
#                 return {'days': days, 'minutes':minutes,'hours':hours}
#             else:
#                 print('非法输入，请重新输入')
        