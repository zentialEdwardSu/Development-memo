from questionary_extansion import *
from mdutils import *
import questionary
from enum import Enum,auto
from typing import List
from datetime import datetime
import pickle
import os
import shutil
import time


BASE_URL = "https://img.shields.io/badge"

def timedelta() ->str:
    return datetime.now().strftime("%m_%d_%H_%M_%S_%f")[:-3]

class STATUS(Enum):
    nostatus = auto()
    canceled = auto()
    done = auto()
    planing = auto()
    pending = auto()
    working = auto()

    def __lt__(self,other):
        return self.value < other.value

    def __str__(self) -> str:
        switcher = {
            STATUS.nostatus:"NoStatus",
            STATUS.canceled:"Canceled-d91e32",
            STATUS.planing:"Planing-7fb8de",
            STATUS.pending:"Pending-f4de89",
            STATUS.working:"Working-1a7f37",
            STATUS.done: "Done-03263f"
        }

        return switcher.get(self,"Planing-7fb8de")

def STATUS_formatter(ss:str) -> STATUS:
    switcher = {
        "None":STATUS.nostatus,
        "Canceled":STATUS.canceled,
        "Planing":STATUS.planing,
        "Pending":STATUS.pending,
        "Working":STATUS.working,
        "Done":STATUS.done,
    }

    return switcher.get(ss,STATUS.nostatus)

def parsetag(status:STATUS) -> str:
    '''
    parsetag will parse STATUS to a shield.io's badage
    '''
    if status == STATUS.nostatus:
        return ""
    return f"![tag]({BASE_URL}/{status})"


class ProjectSection(object):
    '''
    <ProjectName> Name of project
    <Description> Description of project
    <RepoUrl> Repo of project
    <Detail> Project detail
    <Notice> Project Notice
    '''
    ProjectName:str
    Description:str
    RepoUrl:str
    Status:STATUS
    Detail:str
    Notice:str

    def __init__(self,**data):
        self.__dict__.update(data)

    @classmethod
    def init_from_question(cls:Type[T]) -> T:
        customs = {
            "Status":custom_option( # for STATUS
                "Status",
                questionary.select("Select Prooject Status",
                                   choices=["None","Canceled","Planing","Pending","Working","Done"],
                                   default="None"),
                STATUS_formatter
            ),
            "Detail":custom_option( # to to failepath and check suffix
                "Detail", 
                questionary.path("Project detail(endwith .md)",
                                 file_filter=lambda path: path.endswith('.md'),
                                 validate=lambda path: path.endswith('.md') or path=="")
            ),
        }
        return class_init_from_question(cls,customs)

    def __lt__(self,other:'ProjectSection'):
        self.Status < other.Status

    def __str__(self) -> str:
        return f'''
                Project: {self.ProjectName}
                Description: {self.Description}
                - repo: {self.RepoUrl}
                - status: {self.Status}
                - detail: {self.Detail}
                notice: {self.Notice}
                '''

    def update_from_question(self):
        '''
        update attritube by asking question
        '''
        new = ProjectSection().init_from_question()
        for attr_name in self.__dict__:
            new_attr = getattr(new,attr_name)
            if new_attr and new_attr != getattr(self, attr_name):
                if new_attr != STATUS.nostatus:
                    setattr(self, attr_name, new_attr)
        print(self)

    def generate_md(self)->List[str]:
        '''
        parse ProjectSection to markdown text
        '''
        lines = []
        
        lines.append(f"{n_level_title(3,self.ProjectName)}\n") ### ProjectName
        lines.append("\n")

        if self.Description:
            lines.append(f"{self.Description}\n") # the project is for xxx
            lines.append("\n")

        if self.RepoUrl == "": 
            lines.append(f"- repo: X\n")
        else:
            lines.append(f"- repo: {hyperlink(self.ProjectName,self.RepoUrl)}\n")
        lines.append(f"- status: {parsetag(self.Status)}\n")
        if self.Detail == "" or self.Detail[-3:] != ".md":
            lines.append(f"- detail: X\n")
        else: 
            lines.append(f"- detail: {hyperlink(self.Detail[:-3], self.Detail)}\n")
        lines.append("\n")

        if self.Notice:
            lines.append(f"> {self.Notice}\n")
            lines.append("\n")
        lines.append("---\n")

        return lines

def init_many_ProjectSection(        
        confrim_msg:str = '>> Continue create Project?',
        qmark:str="?",
        auto_enter:bool = False
    ) -> List[ProjectSection]:
    
    confrim_q = questionary.confirm(confrim_msg,qmark=qmark,auto_enter=auto_enter)
    res:List[ProjectSection] = []
    keep_on = True

    while keep_on:
        answer = ProjectSection.init_from_question()
        keep_on = confrim_q.ask()
        res.append(answer)

    return res
    

class readmeMetaData(object):

    Title:str
    MainDescription:List[str]
    Projects:List[ProjectSection]

    def __init__(self,Title:str,MainDescription:List[str],Projects:List[ProjectSection]):
        self.Title = Title
        self.MainDescription = MainDescription
        self.Projects = Projects

    def persist(self,path:str,backup:bool = False):
        '''
        use pickle to serialize obj for buffering
        '''
        fpath = path
        if os.path.exists(fpath) and backup:
            shutil.move(fpath,f"{fpath}.{timedelta()}.backup")

        with open(fpath,"wb") as f:
            pickle.dump(self,f)

    @classmethod
    def init_from_persist(cls:Type[T],path:str) -> 'readmeMetaData':
        '''
        read buffer and get the origin obj
        '''
        if not os.path.exists(path):
            return readmeMetaData("NOTITLE",[""],[])
        with open(path,"rb") as f:
            return pickle.load(f)

    def generate_readme(self,path:str):
        '''
        '''
        with open(path,"w") as md:
            write_with_white_line(md,n_level_title(1,self.Title))

            for line in self.MainDescription:
                write_with_white_line(md,line)
            
            write_with_white_line(md,n_level_title(2, "Projects"))
            write_with_white_line(md,"---")
            for project in self.Projects:
                md.writelines(project.generate_md())



def remove_backup_files(folder_path):
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        if os.path.isfile(file_path) and file_name.endswith(".backup"):
            os.remove(file_path)

def make_buffer(path) -> bool:
    meta_path = os.path.join(path,"readme.meta")
    buffer_path = os.path.join(path,"meta.buffer")

    if os.path.exists(meta_path):
        shutil.copy(meta_path,buffer_path)
        return True
    else:
        return False
    
if __name__ == '__main__':
    # print(n_level_title(2,"Hello"))
    # print(STATUS.working > STATUS.canceled)
    p = ProjectSection().init_from_question()

    print(p)
    print(parsetag(p.Status))

    print("doing section update")
    p.update_from_question()

    print(p)

    # rm = readmeMetaData("test",["hihi"],[p])

    # rm.persist("./metadata/metadata.pkl",True)

    # nrm = readmeMetaData.init_from_persist("./metadata/metadata.pkl")

    # nrm.generate_readme("./")

    # print(vars(nrm))
    # remove_backup_files("./")