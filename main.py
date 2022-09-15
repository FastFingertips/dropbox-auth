from urllib.parse import quote
import webbrowser as wb
import dropbox
import pick

DROPBOX_TOKEN = ''

class dropboxApp:
    def __init__(self, token):
        self.dbx = dropbox.Dropbox(token)
        self.dbx.users_get_current_account()

    def getDirs(self, path=''):
        folderList, fileList = [], []
        items = self.dbx.files_list_folder(path).entries
        for i in items:
            if self.checkFileOrFolder(i) == 'Folder': folderList.append(i.path_lower)
            elif self.checkFileOrFolder(i) == 'File': fileList.append(i.path_lower)
        return folderList, fileList

    def searchFiles(self, query, path='', start=0, max_results=100, mode=dropbox.files.SearchMode.filename):
        items = self.dbx.files_search(path, query, start, max_results, mode).matches
        return [i.metadata.path_lower for i in items]

    def print_full_account(self):
        account = self.dbx.users_get_current_account()
        print(f"{'Account ID':15} : ", account.account_id)
        print(f"{'Name':15} : ", account.name.display_name)
        print(f"{'Email':15} : ", account.email)
        print(f"{'Account Type':15} : ", account.account_type)
        print(f"{'Locale':15} : ", account.locale)
        print(f"{'Referral Link':15} : ", account.referral_link)
        print(f"{'Is Paired':15} : ", account.is_paired)
        print(f"{'Team':15} : ", account.team)
        print(f"{'Team Member ID':15} : ", account.team_member_id)
        print(f"{'Profile Photo URL':15.15} : ", account.profile_photo_url)
        print(f"{'Disabled':15} : ", account.disabled)

    def print_space_usage(self):
        space = self.dbx.users_get_space_usage()
        print(f"{'Used':15} : ", space.used)
        print(f"{'Allocation':15} : ", space.allocation)
        
    def checkFileOrFolder(self, path):
        if isinstance(path, dropbox.files.FolderMetadata): return 'Folder'
        # elif isinstance(path, dropbox.files.FileMetadata): return 'File'
        else: return 'File'
        
    def downloadFile(self, path):
        fileInfos = self.fileInfos(path)
        print(f'Name: {fileInfos.name}')
        print(f'Client Modified: {fileInfos.client_modified}')
        print(f'Server Modified: {fileInfos.server_modified}')
        print(f'File size: {fileInfos.size/1024/1024:.2f} MB')

        fileName = path.split('/')[-1] # '/../../1.txt' -> '1.txt'

        if fileInfos.is_downloadable:
            if self.checkFileOrFolder(path) == 'File':
                print(f'Downloading https://www.dropbox.com/home{quote(path)}')
                self.dbx.files_download_to_file(fileName, path)
            elif self.checkFileOrFolder(path) == 'Folder':
                print(f'Folder {path} can not be downloaded')
        else: print(f'File {path} is not downloadable')
        
    def fileInfos(self, path):
        file = self.dbx.files_get_metadata(path)
        """fileInfos = {
            'client_modified': file.client_modified,
            'content_hash': file.content_hash,
            'export_info': file.export_info,
            'file_lock_info': file.file_lock_info,
            'has_explicit_shared_members': file.has_explicit_shared_members,
            'id': file.id,
            'is_downloadable': file.is_downloadable,
            'media_info': file.media_info,
            'name': file.name,
            'parent_shared_folder_id': file.parent_shared_folder_id,
            'path_display': file.path_display,
            'path_lower': file.path_lower,
            'preview_url': file.preview_url,
            'property_groups': file.property_groups,
            'rev': file.rev,
            'server_modified': file.server_modified,
            'sharing_info': file.sharing_info,
            'size': file.size,
            'symlink_info': file.symlink_info
        }"""
        return file

def itemsPrinter(items):
    for no, item in enumerate(items):
        print(no, item)

def dropboxWeb(path):
    wb.open(f'https://www.dropbox.com/home{quote(path)}')

def main():
    x = dropboxApp(DROPBOX_TOKEN)
    x.print_full_account()
    # x.print_space_usage()
    # x.getDirs() # '/test
    methods = ["[DROPBOX]", "[SEARCH]"]
    option = pick.pick(methods, "Select an option")[0] # 0: option, 1: index
    if option == methods[0]:
        dPath = ''
        ffList = []
        while True:
            folderList, fileList = x.getDirs(dPath)
            ffList = folderList + fileList
            itemsPrinter(ffList)
            print(f'Folders: {len(folderList)} Files: {len(fileList)}')
            print(f'h: Home, q: Quit, d+no: Download')
            userInput = input('>>: ')

            try:
                userInput = int(userInput)
                if userInput < len(ffList):
                    if ffList[userInput] in fileList:   dropboxWeb(ffList[userInput])
                    else: dPath = ffList[userInput]
                else: print(f'Invalid number, please enter a number between 0 and {len(ffList)-1}')
            except ValueError: # if userInput is not a number
                if userInput == 'h':
                    dPath = ''
                    ffList = []
                elif userInput.startswith('d'):
                    try:
                        userInput = int(userInput[1:])
                        if userInput < len(ffList): x.downloadFile(ffList[userInput]) # '/test/test.txt'
                        else: print(f'Invalid number, please enter a number between 0 and {len(ffList)-1}')
                    except ValueError: print(f'Invalid number {userInput}')
                elif userInput == 'q': break
                else: print(f'Invalid input: {userInput}')
    elif option == methods[1]:
        while True:
            query = input('Search: ')
            items = x.searchFiles(query)
            itemsPrinter(items)
            print(f'q: Quit, d+no: Download, o+no: Open')
            userInput = input('>>: ')
            try:
                userInput = int(userInput)
                if userInput < len(items):
                    print(f'o: Open, d: Download')
                    itemInput = input('>>: ').lower()
                    if itemInput.startswith('d'): x.downloadFile(items[userInput])
                    elif itemInput.startswith('o'): dropboxWeb(items[userInput])
            except ValueError:
                userInput = userInput.lower()
                if userInput.startswith('d'):
                    try:
                        userInput = int(userInput[1:])
                        if userInput < len(items): x.downloadFile(items[userInput]) # '/test/test.txt'
                    except ValueError: print(f'Invalid number {userInput}')
                elif userInput.startswith('o'):
                    try:
                        userInput = int(userInput[1:])
                        if userInput < len(items): dropboxWeb(items[userInput])
                    except ValueError: print(f'Invalid number {userInput}')
                elif userInput == 'q': break
    else:  print('Invalid option')

if __name__ == '__main__': 
    if not DROPBOX_TOKEN:
        print('Invalid token.')
        DROPBOX_TOKEN = input('Enter your Dropbox token: ')

    main()