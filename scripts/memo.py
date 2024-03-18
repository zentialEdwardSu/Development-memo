'''memo is a faster, more powerful and easier-to-use development memo management tool'''
import typer
import questionary
import os.path as osp
from scripts_structs import *

pkl_dir="./metadata"
nqmark="memo > "
buffer = osp.join(pkl_dir,"meta.buffer")
meta = osp.join(pkl_dir,"readme.meta")

app = typer.Typer()

def gurantee_buffer(meta_path:str,buffer_path:str,pass_check:bool=False) -> bool:
    '''
    gurantee_buffer will gurantee there always a buffer file for memo
    '''
    if not osp.exists(meta_path) and not osp.exists(buffer_path):
        typer.echo(f"No readme.meta found in {pkl_dir}, Please use 'memo.py new' to create one first")
        return False
    if osp.exists(buffer_path):
        if pass_check:
            return True
        if osp.exists(meta_path):
            cover = questionary.confirm("Buffer already found, overwrite it?",qmark=nqmark).ask()
            if not cover:
                return True
    if osp.exists(meta_path):
        shutil.copy(meta_path,buffer_path)
    return True

@app.command(help="Create new Readme meta")
def new():
    if osp.exists(meta):# check if readme.meta exists
        if not questionary.confirm("readme.meta exists, overwrite it?",qmark=nqmark):
            return
    typer.echo("We are now creating a new readme.meta")
    # prepare to init a new readmeMetaData
    title = questionary.text("Main Title of readme", "DevelopmentMemo",qmark=nqmark).ask()
    maindescription = ask_multiple_times(
        questionary.text("Section of description",qmark=nqmark),
        confrim_msg="Next section?",
        auto_enter=True
    )
    typer.echo("Init Projects")
    projects = init_many_ProjectSection(auto_enter=True,qmark=nqmark)
    projects.sort(key=lambda x:x.Status,reverse=True)

    # init and persist to buffer
    metaclass = readmeMetaData(title,maindescription,projects)
    metaclass.persist(buffer)
    typer.echo(f"Success: buffer created in {buffer}")

@app.command(help="list all project")
def list():
    '''
    list all the Project in buffer
    '''
    if not gurantee_buffer(meta,buffer,True):exit(-1)
    rmeta = readmeMetaData.init_from_persist(buffer)
    typer.echo("All project are below")
    for project in rmeta.Projects:
        typer.echo(f"{project}")
    typer.echo("END")

@app.command(help="Change Maindescription or Project,use main to update MainDescription")
def update(item: str = typer.Argument(None)):

    if not gurantee_buffer(meta,buffer):exit(-1)
    rmeta = readmeMetaData.init_from_persist(buffer)
    name_cache = [project.ProjectName for project in rmeta.Projects]

    if item in name_cache:
        typer.echo(f"Updating item {item}")
        item_idx = name_cache.index(item)
        typer.echo(f"we are now updating Project: {item}, any not null attribute below will be updated")
        rmeta.Projects[item_idx].update_from_question()
        
        # sort by Status and persist
        rmeta.Projects.sort(key=lambda x:x.Status,reverse=True)
        rmeta.persist(buffer)

    elif item=="main":
        # edit Maindescription
        ans = ask_multiple_times(
            questionary.text("Section of description",qmark=nqmark),
            confrim_msg="Next section?",
            auto_enter=True
            )

        if ans:
            rmeta.MainDescription = ans
            rmeta.persist(buffer)
    else:
        typer.echo(f"Invaild Project name {item}")

@app.command(help="Add new Project")
def add():
    if not gurantee_buffer(meta,buffer):exit(-1)
    rmeta = readmeMetaData.init_from_persist(buffer)
    name_cache = [project.ProjectName for project in rmeta.Projects]

    typer.echo("We are now creating new project")
    new_project = ProjectSection.init_from_question()

    if new_project.ProjectName in name_cache:
        typer.echo(f"Project Name {new_project.ProjectName} already exists")
    else:
        rmeta.Projects.append(new_project)

        rmeta.Projects.sort(key=lambda x:x.Status,reverse=True)
        rmeta.persist(buffer)

        typer.echo(f"Project: {new_project.ProjectName} was added successfully")

@app.command(help="Remove a Project")
def delete(item: str = typer.Argument(None)):
    if not gurantee_buffer(meta,buffer):exit(-1)
    rmeta = readmeMetaData.init_from_persist(buffer)
    name_cache = [project.ProjectName for project in rmeta.Projects]

    if item in name_cache:
        typer.echo(f"Project {item} will be deleted")
        typer.echo(f"ProjectInfo:{rmeta.Projects[name_cache.index(item)]}")

        if questionary.confirm("Are you sure?",qmark=nqmark,default=False).ask():
            rmeta.Projects.pop(name_cache.index(item))

            rmeta.Projects.sort(key=lambda x:x.Status,reverse=True)
            rmeta.persist(buffer)
            typer.echo(f"Project: {item} was deleted successfully")
    else:
        typer.echo(f"Invaild Project name {item}")

@app.command(help="Render README.md")
def render():
    '''
    generate README.md from buffer'''
    if not gurantee_buffer(meta,buffer,True):exit(-1)
    rmeta = readmeMetaData.init_from_persist(buffer)

    typer.echo("Rendering README.md")
    rmeta.generate_readme("./README.md")

    typer.echo("Generating readme.meta")
    if questionary.confirm("Clean buffer?",qmark=nqmark,auto_enter=True).ask():
        shutil.move(buffer,meta)
    else:
        shutil.copy(buffer,meta)

if __name__ == "__main__":
    app()