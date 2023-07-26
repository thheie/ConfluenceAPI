import json
import requests
import openpyxl
from requests.auth import HTTPBasicAuth
from csv import DictReader
from logger import logger


def readFromCsv(filename):
    with open(filename, 'r') as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
        # print(list_of_dict)
    return list_of_dict[0]

class Confluence_api():

    def __init__(self):
        '''
        Initializes the Confluence_API object
        '''
        self.space_list = []
        self.user_list = []
        self.space_permission_list_raw = []
        self.space_permission_list=[]
        self.space_permissision_tab=[]
        setup_params = readFromCsv('setup.csv')
        self.base_url = setup_params['baseurl']
        self.username = setup_params['username']
        self.token = setup_params['token']
        self.auth = HTTPBasicAuth(self.username, self.token)

    def set_space_permission(self, space_key, identifier, type, key, target):
        '''
        Sets a specific permission to a confluence space for a user, or group. All permissions must be set separately.
        Valid permissions are:
            'create': 'page', 'blogpost', 'comment', 'attachment'
            'read': 'space'
            'delete': 'page', 'blogpost', 'comment', 'attachment', 'space'
            'export': 'space'
            'administer': 'space'
            'archive': 'page'
            'restrict_content': 'space'
        :param space_key: the key used by Confluence to identefy the space
        :param identifier: name off the group or email of the user that gets this permission
        :param user or group
        :param key: What type off persmission that is given Valid values are: Create, read, delete, export, archive, restrict_content
        :param target: What type of object the persmission is for: space, page, blogpost, comment, attachment
        :return: Api responce.status_code
        '''
        #todo endre slik at metoden også hånterer personer grupper og apper
        url = f'https://{self.base_url}/wiki/rest/api/space/{space_key}/permission'
        headers = {
                   "Accept": "application/json",
                   "Content-Type": "application/json"
                    }
        payload = json.dumps({
                              "subject": {
                                            "type":type,
                                            "identifier":identifier
                                            },
                              "operation": {
                                            "key": key,
                                            "target": target
                                            },
                              "_links": {}
                                })
        # Send API-forespørselen
        response = requests.request(
                                 "POST",
                                 url,
                                 data=payload,
                                 auth=self.auth,
                                 headers=headers)
        # Sjekk svaret fra serveren
        if response.status_code == 200:
            print(f'Lesetilgang er gitt til {key}, {identifier}')
        #     todo Oppdaterer space_permission_list og space_permission_tab (pri: lav)
        else:
            print(f'En feil oppsto: Statuskode: {response.status_code}')
            print(f'Feilmelding: {response.text}')
        return response.status_code
    def delete_space_permission(self, space_key, id):
        '''
        Deleite a spesicic space permission
        :param space_key:  the key used by Confluence to identefy the space
        :param id: the id of the mermission that is to be deleted
        :return:
        '''
        url = f'https://{self.base_url}/wiki/rest/api/space/{space_key}/permission/{id}'
        response = requests.request(
            "DELETE",
            url,
            auth=self.auth
        )
        if response.status_code == 200:
            print(f'Tilgangen til spacet: {space_key} er sletter')
            print(json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")))
        else:
            print("En feil oppstod. Statuskode:", response.status_code)
            print("Feilmelding:", response.text)

    def get_space_permissions(self):
        url =  f'https://{self.base_url}/wiki/rest/api/space?expand=permissions'
        response = requests.request(
            'GET',
            url,
            auth=self.auth
        )
        if response.status_code == 200:
            print(f'Lastet alle space persmissions ok')
            result = json.loads(response.text)
            self.space_permission_list_raw = result['results']
        else:
            print("En feil oppstod. Statuskode:", response.status_code)
            print("Feilmelding:", response.text)

    def list_spaces(self):
        if len(self.space_permission_list_raw) > 0:
            for space in self.space_permission_list_raw:
                print(f' Space: {space["name"]}  Space type: {space["type"]}')

    def decode_space_persmissions(self):
        api_call_trial = 0
        api_read_sucess = True
        while len(self.space_permission_list_raw) == 0:
            self.get_space_permissions()
            if api_call_trial >= 3:
                api_read_sucess = False
                break
            api_call_trial += 1
        if api_read_sucess:
            for space in self.space_permission_list_raw:
                # self.space_permission_list.append(space_details)
                space_permissions = space['permissions']
                if space['key'] not in self.space_list:
                    self.space_list.append(space['key'])
                for permission in space_permissions:
                    record_compleate = True
                    permission_details = {}
                    permission_details['space_id'] = space['id']
                    permission_details['space_key'] = space['key']
                    permission_details['space_name'] = space['name']
                    permission_details['space_type'] = space['type']
                    permission_details['permissions_id'] = permission['id']
                    if 'subjects' in permission:
                        if 'user' in permission['subjects']:
                            account_details = permission['subjects']['user']['results'][0]
                            if account_details['accountType'] == 'atlassian':
                                permission_details['user_id']=account_details['accountId']
                                permission_details['user_email']=account_details['email']
                                permission_details['user_public_name']=account_details['publicName']
                                permission_details['user_type']='user'
                                if permission_details['user_id'] not in self.user_list:
                                    self.user_list.append(permission_details['user_id'])
                            else:
                                record_compleate = False
                        elif 'group' in permission['subjects']:
                            account_details = permission['subjects']['group']['results'][0]
                            permission_details['user_id'] = account_details['name']
                            permission_details['user_type'] = 'group'
                        else:
                            # print (permission)
                            record_compleate = False
                    else:
                        # print (permission)
                        record_compleate = False
                    if 'operation' in permission:
                        permission_details['operation']=permission['operation']['operation']
                        permission_details['target_type']=permission['operation']['targetType']
                    else:
                        # print(permission)
                        record_compleate = False
                    if record_compleate:
                        self.space_permission_list.append(permission_details)
        for item in self.space_permission_list:
            print (item)

    def group_permissions(self):
        '''
        Goes thru the list of permissions and group all permissions for a person/groups togeher.
        the result is stored in spect_permissision_tab

        :return:
        '''
        if len(self.space_permission_list) > 0:
            for space_key in self.space_list:
                permission_tab_detail = {}
                for user_id in self.user_list:
                    for permission in self.space_permission_list:
                        if permission['space_key'] == space_key and user_id == permission['user_id']:
                            operation = permission['operation']
                            target_type = permission['target_type']
                            if operation == 'read' and target_type == 'space':
                                permission_type = 'view_space'
                            elif operation == 'delete' and target_type == 'space':
                                permission_type = 'delete_own'
                            elif operation == 'create' and target_type == 'page':
                                permission_type = 'add_page'
                            elif operation == 'archive' and target_type == 'page':
                                permission_type = 'archive_page'
                            elif operation == 'delete' and target_type == 'page':
                                permission_type = 'delete_page'
                            elif operation == 'create' and target_type == 'blogpost':
                                permission_type = 'add_blogg'
                            elif operation == 'delete' and target_type == 'blogpost':
                                permission_type = 'delete_blogg'
                            elif operation == 'create' and target_type == 'comment':
                                permission_type = 'add_comment'
                            elif operation == 'delete' and target_type == 'comment':
                                permission_type = 'delete_comment'
                            elif operation == 'create' and target_type == 'attachment':
                                permission_type = 'add_attachment'
                            elif operation == 'delete' and target_type == 'attachment':
                                permission_type = 'delete_attachment'
                            elif operation == 'restrict_content' and target_type == 'space':
                                permission_type = 'add_delete_restrictions'
                            elif operation == 'export' and target_type == 'space':
                                permission_type = 'export_space'
                            elif operation == 'administer' and target_type == 'space':
                                permission_type = 'administer_space'
                            permission_tab_detail[permission_type] = permission['permissions_id']
                    permission_tab_detail['user_id'] = user_id
                    permission_tab_detail['user_type'] = permission['user_type']
                permission_tab_detail['space_key'] = space_key
                self.space_permissision_tab.append(permission_tab_detail)
                print (permission_tab_detail)




    def write_to_excel(self):
        wb = openpyxl.Workbook()
        ws = wb.active
        row_number = 1
        collum_number = 1
        ws.cell(row=row_number, column=collum_number, value='Space_key')
        ws.cell(row=row_number, column=collum_number +1, value='user_id')
        ws.cell(row=row_number, column=collum_number +2, value='user_type')
        ws.cell(row=row_number, column=collum_number +3, value='view_space')
        ws.cell(row=row_number, column=collum_number +4, value='delete_own')
        ws.cell(row=row_number, column=collum_number +5, value='add_page')
        ws.cell(row=row_number, column=collum_number +6, value='archive_page')
        ws.cell(row=row_number, column=collum_number +7, value='add_blogg')
        ws.cell(row=row_number, column=collum_number +8, value='delete_blogg')
        ws.cell(row=row_number, column=collum_number +9, value='add_comment')
        ws.cell(row=row_number, column=collum_number +10, value='delete_comment')
        ws.cell(row=row_number, column=collum_number +11, value='add_attachment')
        ws.cell(row=row_number, column=collum_number +12, value='delete_attachment')
        ws.cell(row=row_number, column=collum_number +13, value='add_delete_restrictions')
        ws.cell(row=row_number, column=collum_number +14, value='export_space')
        ws.cell(row=row_number, column=collum_number +15, value='administer_space')

        for spect_permissision in self.space_permissision_tab:
            row_number += 1
            ws.cell(row=row_number, column=collum_number, value=spect_permissision['space_key'])
            ws.cell(row=row_number, column=collum_number+1, value=spect_permissision['user_id'])
            ws.cell(row=row_number, column=collum_number+2, value=spect_permissision['user_type'])
            if 'space_key' in  spect_permissision:
                ws.cell(row=row_number, column=collum_number+3, value='X')
            if 'view_space' in spect_permissision:
                ws.cell(row=row_number, column=collum_number + 4, value='X')
            if 'delete_own' in spect_permissision:
                ws.cell(row=row_number, column=collum_number + 5, value='X')
            if 'add_page' in spect_permissision:
                ws.cell(row=row_number, column=collum_number + 6, value='X')
            if 'archive_page' in spect_permissision:
                ws.cell(row=row_number, column=collum_number + 7, value='X')
                break
        wb.save('permission.xlsx')







    def find_types(self):
        user_types = []
        if len(self.space_permission_list_raw) > 0:
            for space in self.space_permission_list_raw:
                space_permissions = space['permissions']
                for permission in space_permissions:
                    if 'subjects' in permission:
                        if 'user' in permission['subjects']:
                          account_details = permission['subjects']['user']['results']
                          for detail in account_details:
                            if detail['accountType'] not in user_types:
                                user_types.append(detail['accountType'])
                    elif 'operation' not in permission:
                        print(permission)
            print(user_types)

    def bach_delete_permissions(self, spacekey, user_email='', group_name = ''):
        if len(self.space_permission_list) > 0:
            for permission in self.space_permission_list:
                if len(user_email) > 0:
                    if 'user_email' in permission:
                        if permission['space_key'] == spacekey and permission['user_email'] == user_email:
                            self.delete_space_permission(spacekey, permission['permissions_id'])






