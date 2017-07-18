from flask import json, request, session
from flask_login import current_user, logout_user, login_user
from bson import ObjectId
from werkzeug.security import check_password_hash, generate_password_hash
from . import models


class ConfigurationService:
    def __init__(self):
        self.model = models

    def getConfiguration(self):
        model = self.model.Configuration()
        result = model.getConfiguration()
        return result


class UserService:
    def __init__(self):
        self.model = models

    def getCurrentUser(self):
        userstatus = {"is_active": current_user.is_active, "is_authenticated": current_user.is_authenticated,
                      "is_anonymous": current_user.is_anonymous}
        if current_user.is_active and current_user.userInfo != None:
            userstatus["uid"] = str(current_user.userInfo['_id'])
            userstatus["username"] = current_user.userInfo['username']
            userstatus["license"] = current_user.userInfo['license']
            userstatus["permissions"] = current_user.userInfo['permissions']
            userstatus["authorization"] = current_user.userInfo['authorization']
        else:
            logout_user()
            session.clear()
        userstatus["sid"] = session.sid
        return json.dumps(userstatus)

    def get_users(self):
        usersAll = self.model.UserModel().get_all()
        return json.dumps(usersAll)

    def register(self):
        register = json.loads(request.data)
        # parameters: username,password, email, groups, avatar,authentication,permissions
        existUser = self.model.UserModel()._get_username(register['originalUsername'])
        if existUser == None:
            uid = str(ObjectId())
            password = generate_password_hash(register['password']).replace('pbkdf2:sha256:50000$', '')
            update = True
        else:
            uid = existUser['_id']
            password = existUser['password']
            update = check_password_hash('pbkdf2:sha256:50000$' + existUser['password'], register['password'])
        if update:
            userModel = self.model.UserModel(uid)
            eLicense = userModel._get_eLicense()
            # resp = userModel._set_on_server(uid=uid,
            #                                 username=register['username'],
            #                                 password=password,
            #                                 email=register['email'],
            #                                 groups=register['groups'],
            #                                 avatar=register['avatar'],
            #                                 # eLicense=eLicense['SN'],
            #                                 entityID=eLicense['entityID'],
            #                                 authorization=register['authorization'],
            #                                 permissions=register['permissions']
            #                                 )
            # if resp:
            userModel._set(username=register['username'],
                           password=password,
                           email=register['email'],
                           groups=register['groups'],
                           avatar=register['avatar'],
                           authorization=register['authorization'],
                           permissions=register['permissions'],
                           entityID=eLicense['entityID'])
            return self.getCurrentUser()
        else:
            return json.dumps({'message': 'Password is wrong.'})

    def login(self):
        user = json.loads(request.data)
        # parameters: username,password
        userInfo = self.model.UserModel()._get_username(user['username'])
        if userInfo != None:
            checkedPassword = check_password_hash('pbkdf2:sha256:50000$' + userInfo['password'], user['password'])
            eLicense = self.model.UserModel()._get_eLicense()['eLicense']
            uLicense = userInfo['license']
            authorization = self.model.UserModel().checkLicenses(userInfo['_id'], uLicense, eLicense)
            print("User Name: ", str(userInfo['username']) + ',', "checkedPassword: ", str(checkedPassword) + ',',
                  "authorization: ", authorization)
            if checkedPassword and authorization:
                login_user(self.model.UserModel(id=userInfo['_id']))
            else:
                session.clear()
                if not checkedPassword:
                    return json.dumps({"message": "password"})
                if not authorization:
                    return json.dumps({"message": "authorization"})
        else:
            return json.dumps({"message": "password"})
        return self.getCurrentUser()

    def logout(self):
        logout_user()
        session.clear()
        return self.getCurrentUser()

    def delete(self):
        user = json.loads(request.data)
        # parameters: uid, if no uid, delete current user.
        if current_user.is_active:
            try:
                uid = user['_id']
                userModel = self.model.UserModel(uid)

                userModel._del()
            except:
                pass
        return self.getCurrentUser()
