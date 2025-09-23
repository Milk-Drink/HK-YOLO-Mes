import os


###处理文件


class Files():
    Path=""##初始化路径
    Files_list=[]##初始化文件列表
    def __init__(self,path:str) -> None:
        self.Path=path
        if os.path.exists(path):
            print("Path Is Ok")
            self.Files_list=os.listdir(path)
        else:
            return "Path Is Not Found"
    def files(self):
        return self.Files_list
    
    def files_remove(self,files_name:str):
        if os.path.exists(self.Path+"/"+files_name):
            os.remove(self.Path+"/"+files_name)
            print(f"The File {files_name} Is Remove")
            return True
        else:
            return f"The File {files_name} Is Not Found,Path {self.Path}"
    def files_remove_all(self,files_list:list):
        if os.path.exists(self.Path):
            for file in files_list:
                if os.path.exists(self.Path+"/"+file)==False:
                    return f"The File {file} Is Not Found"
            for file in files_list:
                os.remove(self.Path+"/"+file)
            return f"The Fils {files_list} Is Remove"
    def files_rename_all(self,rename):

        if os.path.exists(self.Path):
            for file in self.Files_list:
                if os.path.exists(self.Path+"/"+file)==False:
                    return f"The File {file} Is Not Found"
            
            for file in self.Files_list:
                file_name, file_extension = os.path.splitext(file)
                os.rename(self.Path+"/"+file,self.Path+"/"+rename+f"-{file_name}-.txt")
            return f"The Files {self.Files_list} Is Update"
    



# if __name__=="__main__":
#     path=r"D:\LaiJin-YOLO8\Camera_screenshot"
#     OSclass=Files(path)
#     # result=OSclass.files_remove(OSclass.files()[0])
#     files_list=OSclass.files()
#     # files_list.append("0.jpg")
#     result=OSclass.files_remove_all(files_list)
#     print(result)
        
        