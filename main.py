from urllib.parse import quote
import dropbox

DROPBOX_TOKEN = ''

class dropboxApp:
    def __init__(self, token):
        self.dbx = dropbox.Dropbox(token)
        self.dbx.users_get_current_account()

    def getDirs(self, path=''):
        """
        .name
        .id
        .path_lower
        .path_display
        .parent_shared_folder_id
        .sharing_info.read_only
        .sharing_info.parent_shared_folder_id
        .sharing_info.modified_by
        .property_groups.template_id
        .property_groups.fields.name
        .property_groups.fields.value
        """
        entrys = self.dbx.files_list_folder(path).entries
        for entry in entrys:
            print(f'{entry.path_lower}')

    def searchFiles(self, query, path=''):
        entrys = self.dbx.files_search(path, query).matches
        print(f'Found {len(entrys)} files')
        entrysList = []
        for entry in entrys:
            """
            .metadata.name
            .metadata.id
            .metadata.path_lower
            .metadata.path_display
            .metadata.client_modified
            .metadata.server_modified
            .metadata.rev
            .metadata.size
            .metadata.content_hash
            .metadata.is_downloadable
            .metadata.has_explicit_shared_members
            """
            # print(f'Dropbox Url: https://www.dropbox.com/home{quote(entry.metadata.path_lower)}')
            entrysList.append(entry.metadata.path_lower)
        return entrysList
    def print_full_account(self):
        """
        .account_id
        .name.given_name
        .name.surname
        .name.familiar_name
        .name.display_name
        .email
        .email_verified
        .disabled
        .is_teammate
        .profile_photo_url
        .country
        .locale
        .referral_link
        .is_paired
        .account_type
        .root_info.root_namespace_id
        .root_info.home_namespace_id
        .team.team_id
        .team.name
        .team.external_id
        """
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

    def print_space_usage(self): # https://www.dropbox.com/developers/documentation/http/documentation#users-get_space_usage
        """
        .allocation.allocated
        .used
        """
        space = self.dbx.users_get_space_usage()
        print(f"{'Used':15} : ", space.used)
        print(f"{'Allocation':15} : ", space.allocation)
        
    def downloadFile(self, path, local_path):
        self.dbx.files_download_to_file(local_path, path)

def main():
    x = dropboxApp(DROPBOX_TOKEN)
    x.print_full_account()
    # x.print_space_usage()
    # x.getDirs() # '/test'

    userQSearch = input('Enter a search query: ')
    paths = x.searchFiles(userQSearch)
    if paths:
        pathLength = len(paths)

        for no, path in enumerate(paths):
            print(f'{no:2}: {path}') # max 100 results but start from 0 to 99 -> {no:2}

        if pathLength > 0:
            while True:
                userQDownload = int(input('Enter a file to download: '))
                try:
                    path = paths[userQDownload]
                    file = path.split('/')[-1]
                except IndexError: 
                    print(f'Invalid number, please enter a path no between 0 and {pathLength-1}')
                    continue
                print(f'Downloading https://www.dropbox.com/home{quote(paths[userQDownload])}')
                try: 
                    x.downloadFile(path, file)
                    print(f'Downloaded {file}')
                except Exception as e: print(f'Download failed: {e}')
                break
    else: print('No files found')

if __name__ == '__main__': 
    if not DROPBOX_TOKEN:
        print('Invalid token.')
        DROPBOX_TOKEN = input('Enter your Dropbox token: ')

    main()