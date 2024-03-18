def write_white_line(f):
    f.write("\n")

def n_level_title(n:int,title:str) -> str:
    res = ""
    for i in range(n):
        res += "#"
    return f"{res} {title}"

def hyperlink(show:str,link:str):
    return f"[{show}]({link})"

def write_with_white_line(f,context:str):
    f.write(f"{context}\n\n")

if __name__ == '__main__':
    with open("./test.md","w") as f:
        write_with_white_line(f,n_level_title(1,"hello"))

        write_white_line(f)

        f.write("nonono")
        # write_with_white_line(f,"nonono")