import json
import requests
import openpyxl
from requests.auth import HTTPBasicAuth
from csv import DictReader
from api_decode_proc import find_permission_type
from api_decode_proc import exel_collumn_mapping
from logger import logger


def readFromCsv(filename):
    with open(filename, 'r') as f:
        dict_reader = DictReader(f)
        list_of_dict = list(dict_reader)
        # print(list_of_dict)
    return list_of_dict

class Confluence_api():

    def __init__(self):
        '''
        Initializes the Confluence_API object
        '''
        self.space_dict = {}
        self.space_user_dict = {}
        self.space_permission_list_raw = []
        self.space_permission_list=[]
        self.space_permissision_tab=[]
        setup_params_list = readFromCsv('setup.csv')
        setup_params = setup_params_list[0]
        self.base_url = setup_params['baseurl']
        self.username = setup_params['username']
        self.token = setup_params['token']
        self.auth = HTTPBasicAuth(self.username, self.token)
        logger.info('Script initialiced')

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
        :param type: user or group
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
            logger.info(f'Lesetilgang er gitt til {key}, {identifier}')
            print(f'Lesetilgang er gitt til {key}, {identifier}')
        #     todo Oppdaterer space_permission_list (pri: lav)
        else:
            logger.info(f'En feil oppsto: Statuskode: {response.status_code}')
            print(f'En feil oppsto: Statuskode: {response.status_code}')
            print(f'Feilmelding: {response.text}')
        return response.status_code
    def delete_space_permission(self, space_key, id, permission_type):
        '''
        Deleite a spesicic space permission
        :param space_key:  the key used by Confluence to identefy the space
        :param id: the id of the mermission that is to be deleted
        :param permission_type Refers to the permission type that is deleted. Is only in logging to make them more readable.
        :return: Status code from the API (204 is ok)
        '''
        url = f'https://{self.base_url}/wiki/rest/api/space/{space_key}/permission/{id}'
        response = requests.request(
            "DELETE",
            url,
            auth=self.auth
        )
        if response.status_code == 204:
            logger.info(f'The permission {id} to {space_key} has been deleted')
        else:
            logger.critical(f'Failed to delete permission {id} in {space_key}')
            logger.critical(f'{response.text}')
        return response.status_code




    def get_space_permissions(self):
        space_loaded = 0
        space_list = readFromCsv('confluence_space.csv')
        for space in space_list:
            spacekey = space['space_key']
            url =  f'https://{self.base_url}/wiki/rest/api/space/{spacekey}?expand=permissions'
            headers = {'Accept': 'application/json'}
            response = requests.request(
                'GET',
                url,
                headers=headers,
                auth=self.auth
                )

            if response.status_code == 200:
                logger.info(f'Loaded all permissions for space: {space["space_name"]}')
                print(f'Loaded all permissions for space: {space["space_name"]}')
                result = json.loads(response.text)
                self.space_permission_list_raw.append(result)
                space_loaded +=1
            else:
                logtext = f'Error loading space permissions for space {space["space_name"]}. Status code:,{response.status_code}'
                print(logtext)
                logger.critical(logtext)
                logger.critical(f'{response.text}')
                load_permission_sucess = False
        logtext = f'Loaded {space_loaded} of {len(space_list)} spaces'
        print (logtext)
        logger.info(logtext)

    def decode_space_persmissions(self):
        if len(self.space_permission_list_raw)  == 0:
            load_permission_sucess = self.get_space_permissions()
        if len(self.space_permission_list_raw)  > 0:
            for space in self.space_permission_list_raw:
                space_key = space['key']
                if space_key not in self.space_dict:
                    space_detail = {'id':space['id'],
                                    'key': space_key,
                                    'name': space['name'],
                                    'type': space['type']
                                    }
                    self.space_dict[space_key] = space_detail
                space_permission = space['permissions']
                for permission in space_permission:
                    if 'subjects' in permission:
                        if 'user' in permission['subjects']:
                            account_details = permission['subjects']['user']['results'][0]
                            if account_details['accountType'] == 'atlassian':
                                user_id = account_details['accountId']
                                user_type = 'singel_user'
                                user_details = {'user_id': user_id,
                                                'email': account_details['email'],
                                                'name': account_details['publicName'],
                                                'type': user_type
                                                }
                            elif account_details['accountType'] == 'app':
                                user_type = 'app'
                                user_id = account_details['accountId']
                                user_details = {'user_id': user_id,
                                                'name': account_details['publicName'],
                                                'type': user_type
                                                }
                        elif 'group' in permission['subjects']:
                            account_details = permission['subjects']['group']['results'][0]
                            user_type = 'group'
                            user_id = account_details['id']
                            user_details = {'user_id': user_id,
                                            'name': account_details['name'],
                                            'type': user_type
                                            }
                        self.space_user_dict[user_id] = user_details
                    if 'operation' in permission:
                        operation = permission['operation']['operation']
                        target = permission['operation']['targetType']
                        permissions_type = find_permission_type(operation, target)
                        permission_detail = {'space_key': space_key,
                                             'user_id': user_id,
                                             'user_type': user_type,
                                             'operation': operation,
                                             'target': target,
                                             'permissions_type': permissions_type,
                                             'permissions_id':permission['id']
                                             }
                        self.space_permission_list.append(permission_detail)


    def write_to_excel(self):
        self.decode_space_persmissions()
        wb = openpyxl.Workbook()
        collumn_mapping = exel_collumn_mapping()
        ws = wb.active
        row_number = 1
        # writing cullumn names
        for cullumn in collumn_mapping:
            ws.cell(row=row_number, column=collumn_mapping[cullumn], value=cullumn)
        for space in self.space_dict:
            print(space)
            for user in self.space_user_dict:
                user_name = self.space_user_dict[user]['name']
                user_info_written = False
                for permission in self.space_permission_list:
                    if permission['space_key'] == space and permission['user_id'] == user:
                        if not user_info_written:
                            row_number += 1
                            ws.cell(row=row_number, column=collumn_mapping['space_key'], value=permission['space_key'])
                            ws.cell(row=row_number, column=collumn_mapping['user_name'], value=user_name)
                            ws.cell(row=row_number, column=collumn_mapping['user_id'], value=permission['user_id'])
                            ws.cell(row=row_number, column=collumn_mapping['user_type'], value=permission['user_type'])
                            user_info_written = True
                        if permission['permissions_type'] != 'unknown':
                            permission_name =  permission['permissions_type']
                            ws.cell(row=row_number, column=collumn_mapping[permission_name], value='X')
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

    def bach_delete_user_permissions(self, space_list=[]):
        for space in self.space_dict:
            # checks to see if the space is on of those where permissions is to be delted
            if space in space_list or len(space_list) == 0:
                # removes all permissions for this space for this user exept view space
                for permission in self.space_permission_list:
                    permission_type =  permission['permissions_type']
                    if user_id == permission['user_id'] and permission['space_key'] == space:
                        if permission_type != 'view_space':
                            result = self.delete_space_permission(space,permission['permissions_id'])
                            if result == 204:
                                print(f'{permission_type} permission for user {user_id} in space {space} has been deleted')
                                logger.info(f'{permission_type} permission for user {user_id} in space {space} has been deleted')
                            else:
                                print(f'delition of permission {permission_type} for user {user_id} in space {space} failed')
                                logger.info (f'delition of permission {permission_type} for user {user_id} in space {space} failed')
                # removes view space for this user for this space
                for permission in self.space_permission_list:
                    permission_type =  permission['permissions_type']
                    if user_id == permission['user_id'] and permission['space_key'] == space:
                        if permission_type == 'view_space':
                            result = self.delete_space_permission(space,permission['permissions_id'])
                            if result == 204:
                                print(f'{permission_type} permission for user {user_id} in space {space} has been deleted')
                                logger.info(f'{permission_type} permission for user {user_id} in space {space} has been deleted')
                            else:
                                print(f'delition of permission {permission_type} for user {user_id} in space {space} failed')
                                logger.info (f'delition of permission {permission_type} for user {user_id} in space {space} failed')




