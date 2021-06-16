# encoding=utf8

import os
import sys

import boto3
from boto3.dynamodb.conditions import Key, Attr
from botocore.exceptions import ClientError

from pprint import pprint

import datetime
import time
 
import ast
import json
import simplejson
import urllib.request

import zipfile
import shutil

class simpy:
    dynamodb = boto3.resource('dynamodb', region_name='eu-west-1')
    client = boto3.client('dynamodb')
    table = None

    def __init__(self, name):
        self.table = self.dynamodb.Table(name)
        self.currentTable = name
        primaryKey = {
            "Candidat": "id_candidat",
            "Certif": "Licence",
            "EvalInvit": "token",
            "EvalPack": "slug",
            "EvalRecruiter": "mail",
            "Exercise": "id_exercise",
            "Test": "id_test",
            "Token": "token",
            }
        try:
            self.primary = primaryKey[name]
        except:
            self.primary = "id"

    def query(self, key="", value="", item=""):
        key = self.primary
        response = self.table.query(
            KeyConditionExpression=Key(key).eq(value)
        )
        needed = list()
        for i in response['Items']:
            needed.append((i[item]))
        return (needed)

    def scan(self, attribute, value, request):  #recherche scan
        response = self.table.scan(
            FilterExpression=Attr(attribute).eq(value)
        )
        needed = list()
        for i in response['Items']:
            needed.append(i[request])
        return (needed)

    def scanTable(self, attribute="", value=""):
        if (attribute == ""):
            response = self.table.scan()
            new_data = response["Items"]
            while 'LastEvaluatedKey' in response:
                response2 = self.table.scan(
                ExclusiveStartKey=response['LastEvaluatedKey']
                )
                new_data = new_data + response2["Items"]
                response = response2
        else:
            response = self.table.scan(
                FilterExpression=Attr(attribute).eq(value),
            )
            new_data = response["Items"]
            while 'LastEvaluatedKey' in response:
                response2 = self.table.scan(
                FilterExpression=Attr(attribute).eq(value),
                ExclusiveStartKey=response['LastEvaluatedKey']
                )
                new_data = new_data + response2["Items"]
                response = response2
        return (new_data)

    def filter(self, request):
        keys = []
        for key in request.keys():
           fe = Attr(key).eq(request[key])
           keys.append(fe)
        filters = keys[0]
        for key in keys:
           filters = filters & key
        response = self.table.scan(
            FilterExpression=filters
        )
        new_data = response["Items"]
        while 'LastEvaluatedKey' in response:
            response2 = self.table.scan(
            FilterExpression=filters,
            ExclusiveStartKey=response['LastEvaluatedKey']
            )
            new_data = new_data + response2["Items"]
            response = response2
        return (new_data)

    def update(self, key, value, to_update, new_value):
        key = self.primary
        to_update = 'SET ' + to_update + ' = :key'
        self.table.update_item(
        Key={
            key: value
            },
        UpdateExpression = to_update,
        ExpressionAttributeValues = {
            ':key': new_value,
            }
        )

    def reservedUpdate(self, key, value, to_update, new_value):
        key = self.primary
        self.table.update_item(
        Key={
            key: value
            },
        UpdateExpression = 'SET #attr = :key',
        ExpressionAttributeValues = {
            ':key': new_value,
            },
        ExpressionAttributeNames = {
            '#attr': to_update
            }
        )

    def remove_attr(self, value, toDelete):
        key = self.primary
        to_update = 'REMOVE ' + toDelete
        self.table.update_item(
        Key={
            self.primary: value
            },
        UpdateExpression = to_update,
        )

    def delete(self, value):
        self.table.delete_item(
            Key = {
                self.primary : value
            }
        )

    def getItem(self, value):
        if (type(value) is str):
            response = self.table.get_item(Key={ self.primary:value})
        elif (type(value) is int):
            response = self.table.get_item(Key={ self.primary:value })
        if ('Item' in response):
            response = simplejson.dumps(response['Item'])
            d = json.loads(response)
            return (d)
        else:
            return (None)

    def gsiGetter(self, gsi, key, value):
        kce = key + " = :key"
        res = self.table.query(
            IndexName=gsi,
            KeyConditionExpression=kce,
            ExpressionAttributeValues={":key": value},
            ScanIndexForward=False,
        )
        new_data = res["Items"]
        while 'LastEvaluatedKey' in res:
            print('next elem' + str(res['LastEvaluatedKey']))
            response2 = conn.table.query(
                IndexName=gsi,
                KeyConditionExpression=kce,
                ExpressionAttributeValues={":key": value},

                ScanIndexForward=False,
                ExclusiveStartKey=res['LastEvaluatedKey'],
            )
            new_data = new_data + response2["Items"]
            res = response2['Items']
        return (new_data)

    def getNextId(self):
        idList = list()
        dataTable = self.scanTable()
        try:
            for item in dataTable:
                idList.append(item['id'])
            idList = [int(n) for n in idList]
            idList.sort()
            tempId = [x for x in range(idList[0], idList[-1] + 1)]
            idList = set(idList)
            final = list(idList ^ set(tempId))
            if (len(final) == 0):
                idItem = len(dataTable) + 1
            else:
                idItem = final[0]
        except IndexError:
            idItem = 1
        return (idItem)

    def createBackup(self, name=None):
        if name == None:
            date = datetime.datetime.utcfromtimestamp(int(time.time())).strftime('%d-%m-%Y')
            name = self.currentTable + "_AutoBackup_" + date
        self.client.create_backup(
            TableName=self.currentTable,
            BackupName=name
        )

    def listBackups(self):
        response = self.client.list_backups(
            TableName=self.currentTable
        )
        final = []
        for backup in response['BackupSummaries']:
            item = {
                "backup_name": backup['BackupName'],
                "table_name": backup['TableName'],
                "date": backup['BackupCreationDateTime'],
                "size": backup['BackupSizeBytes'],
                "arn": backup['BackupArn']
            }
            final.append(item)
        return (final)

class bupy:
    client = boto3.client('s3')
    s3 = boto3.resource('s3')

    def __init__(self):
        pass

    def upload(self, path, bucket, destinationName, metadata=None, public=None):
        if metadata == None and public == None:
            self.s3.meta.client.upload_file(path, bucket, destinationName)
            return
        if public == True:
            public = "public-read"
        else:
            self.s3.meta.client.upload_file(path, bucket, destinationName, ExtraArgs={'ContentType': metadata})
            return
        self.s3.meta.client.upload_file(path, bucket, destinationName, ExtraArgs={'ContentType': metadata, 'ACL': public})

    def changeMetadata(self, bucket, key, metadata, newMeta="Content-Type"):
        k = self.client.head_object(Bucket = bucket, Key = key)
        m = k["Metadata"]
        m[newMeta] = metadata
        self.client.copy_object(Bucket = bucket, Key = key, CopySource = bucket + '/' + key, Metadata = m, MetadataDirective='REPLACE')

    def download(self, bucket, filename, folder=False):
        if (folder == False):
            self.s3.meta.client.download_file(bucket, filename, filename)
        else:
            filename = filename + "/"
            kwargs = {'Bucket': bucket}
            listS3 = []
            while True:
                temp=self.client.list_objects_v2(**kwargs)
                try:
                    kwargs['ContinuationToken'] = temp['NextContinuationToken']
                except KeyError:
                    for item in temp['Contents']:
                        listS3.append(item)
                    break
                for item in temp['Contents']:
                    listS3.append(item)
            for s3_key in listS3:
                if not os.path.exists(filename):
                    os.makedirs(filename)
                if (s3_key['Key'].startswith(filename)):
                    s3_object = s3_key['Key']
                    if not s3_object.endswith("/"):
                        self.s3.meta.client.download_file(bucket, s3_object, s3_object)
                    else:
                        if not os.path.exists(s3_object):
                            os.makedirs(s3_object)
            # path = "s3://" + bucket + "/" + filename + " " + destFolder
            # os.system("aws s3 cp --recursive " + path)
        return ("ok")

    def getList(self, bucket):
        objList = []
        kwargs = {'Bucket': bucket}
        listS3 = []
        while True:
            temp=self.client.list_objects_v2(**kwargs)
            try:
                kwargs['ContinuationToken'] = temp['NextContinuationToken']
            except KeyError:
                for item in temp['Contents']:
                    listS3.append(item)
                break
            for item in temp['Contents']:
                listS3.append(item)
        # response = self.client.list_objects(Bucket=bucket)
        for key in listS3:
            objList.append(key['Key'])
        return (objList)

class inspy(object):
    client = boto3.client('ec2')
    ec2 = boto3.resource('ec2')

    def __init__(self):
        pass

    def listInstances(self, data=None):
        if (data == None):
            response = self.client.describe_instances()
        else:
            response = data
        instanceList = list()
        i = 0
        pprint(response)
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                instanceList.append(instance['InstanceId'])
        return (instanceList)

    def getInstancesFromTag(self, key, value):
        response = self.client.describe_instances(
            Filters=[
                {
                    'Name': 'tag:'+key,
                    'Values': [value]
                }
            ]
        )
        return (response)
    # def getInstancesFromTag(self, key="", value=""):
    #     response = self.ec2.Instance("i-04156ac3be1c245b4")
    #     for tags in response.tags:
    #         if tags["Key"] == 'group':
    #             instancename = tags["Value"]
    #             return instancename
    #     return(response)

class messpy:
    client = boto3.client('sns')

    def __init__(self):
        pass

    def send(self, number, message):
        self.client.publish(
        PhoneNumber=number,
        Message=message
        )

class toolpy:
    EvalInvit = simpy("EvalInvit")
    TrainUser = simpy("TrainUser")
    EvalExo = simpy("EvalExo")
    EvalRecruiter = simpy("EvalRecruiter")
    EvalRecruiterEx = simpy("EvalRecruiterEx")
    Certification = simpy("Certif")
    TrainPack = simpy("TrainPack")
    TrainUser = simpy("TrainUser")
    s3 = boto3.resource('s3')

    def __init__(self):
        pass

    def getMailFromToken(self, token):
        return (self.EvalInvit.query("token", token, "mail")[0])

    def getExoName(self, idExo):
        return (self.EvalExo.query("id", idExo, "name")[0])

    def downloadEvalExo(self, exoName): # Télecharge un exercice (AMI)
        try:
            exoName = exoName + ".zip"
            path = "/home/ubuntu/dst_jupyterhub/dynamoDB/"
            fullPath = path + exoName
            self.s3.meta.client.download_file("eval-exo", exoName, fullPath)
            #raise error_class("Exercise not Found")
        except:
            print("Exercise not found")
        zipExo = zipfile.ZipFile(fullPath, 'r')
        zipExo.extractall(path)
        zipExo.close()
        try:
            os.remove(fullPath)
            shutil.rmtree(path + "__MACOSX")
        except:
            print("Deletion impossible")

    def getNotebook(self, token): #
        notebook = self.EvalInvit.query("token", token, "notebook_data")[0]
        if (len(notebook) == 0):
            return (None)
        return (simplejson.dumps(notebook))

    def convertNotebook(self, notebook):
        pass

    def uploadNotebook(self, filename, token):
        notebook = open(filename, 'r')
        content = json.loads(notebook.read())
        self.EvalInvit.update("token", token, "notebook_data", content)
        return None

    def getStatusUpdate(self, token):
        return (self.EvalInvit.query("token", token, "status_updates"))

    def getExamTime(self, token):
        return (self.EvalInvit.query("token", token, "test_duration"))

    def getUserList(self, recruiter):
        return(self.EvalInvit.scan("recruiter", recruiter, "mail"))

    def getUserList2(self, recruiter):
        userInfo = list()
        userData = dict()
        data = self.EvalInvit.scan("recruiter", recruiter, "mail")
        for mail in data:
            token = self.EvalInvit.scan("mail", mail, "token")[0]
            userData = {
                "mail" : mail,
                "first_name" : self.EvalInvit.query("token", token, "first_name")[0],
                "last_name" : self.EvalInvit.query("token", token, "last_name")[0],
                "pack_slug" : self.EvalInvit.query("token", token, "pack_slug")[0]
            }
            userInfo.append(userData)
        return (userInfo)

    def getTimeTest(self, token):
        status = self.getStatusUpdate(token)
        try:
            start = status[0]["start"]
            end = status[0]["finish"]
        except KeyError:
            print("status does not exist")
            return (None)
        elapsedTime = end - start
        elapsedTime = elapsedTime / 60
        self.EvalInvit.update("token", token, "Elapsed_Time", elapsedTime)
        return (elapsedTime)

    def checkUser(self, mail, psswd):
        try:
            confirmedPass = self.EvalRecruiter.query("mail", mail, "password")[0]
        except:
            print("User does not exist")
            return False
        if psswd == confirmedPass:
            print("Wrong password")
            return True
        return False

    def getCompany(self, user):
        return (self.EvalRecruiter.query("mail", user, "company")[0])

    def getRecrutor(self, recruiter):
        response = self.EvalRecruiterEx.table.scan(
            FilterExpression=Attr("id").eq(recruiter)
            )
        return (response)

    def getCompanyFromToken(self, token):
        return (self.EvalInvit.query("token", token, "recruiter")[0])

    def getNameFromeSlug(self, slug):
        return (self.EvalExo.query("id", slug, "name")[0])

    def getInfoForCertif(self, token):
        item = self.EvalInvit.getItem(token)
        first_name = item['first_name']
        last_name = item['last_name']
        mail = item['mail']
        slug = item['pack_slug']
        language = item['language']
        certif = self.getNameFromeSlug(slug)
        userdata = {
            "first_name" : first_name,
            "last_name" : last_name,
            "mail" : mail,
            "certif" : certif,
            "language" : language
        }
        return (userdata)

    def getFinishedTest(self):
        dataContainer = []
        data = {}
        response = self.EvalInvit.scanTable()
        certifList = self.Certification.scanTable()
        lenCertif = len(certifList)
        uncertified = list()
        for item in response:
            find = 0
            for certif in certifList:
                if (item['token'] == certif['token']):
                    find = 1
            if (find == 0):
                uncertified.append(item)
        for item in uncertified:
            if ('finish' in item['status_updates']):
                if(item['status_updates']['finish'] > 0):
                    data = {
                        "token" : item['token'],
                        "first_name" : item['first_name'],
                        "last_name" : item['last_name'],
                        "language" : item['language'],
                        "mail" : item['mail'],
                        "pack_slug" : item['pack_slug'],
                        "recruiter" : item['recruiter'],
                        "status_updates" : item['status_updates'],
                    }
                    dataContainer.append(data)
        return (dataContainer)

    def getSessionInformation(self, user):
        contents = urllib.request.urlopen("https://beta.datascientest.com/user/"+ user + "/api/sessions").read()
        contents = str(contents, "utf-8")
        contents = contents[1:][:-1]
        contents = ast.literal_eval(contents)
        # timestamp = time.mktime(datetime.datetime.strptime(contents['kernel']['last_activity'], "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
        # contents['kernel']['timestamp'] = int(timestamp)
        return (contents)

    def sendNotif(self, key, msg, link):
        if (isinstance(key, int)):
            connTable = self.TrainUser
        else:
            connTable = self.EvalRecruiter
        newNotif = {
          "date": int(time.time()),
          "link": link,
          "message": msg,
          "view": False
          }
        connTable.table.update_item(
            Key={
                'id': key
                },
            UpdateExpression="SET notifications = list_append(notifications, :i)",
            ExpressionAttributeValues={
                ':i': [newNotif],
                },
        )

    def getNotif(self, key):
        if (isinstance(key, int)):
            connTable = self.TrainUser
        else:
            connTable = self.EvalRecruiter
        try:
            return(connTable.query("id", key, "notifications")[0])
        except KeyError:
            return([])

    def getPackList(self, idUser):
        packList = list()
        item = self.TrainUser.getItem(int(idUser))
        for pack in item['packs']:
            curPack = self.TrainPack.getItem(int(pack['id']))
            packDict = dict()
            packDict['id'] = pack['id']
            packDict['name'] = curPack['name_pack']
            packDict['linked_certif'] = curPack['linked_certif']
            if 'language_certif' in curPack:
                packDict['language'] = curPack['language_certif']
            total = 0
            for exercice in curPack['exercises']:
                total += 1
            packDict['total'] = total
            finishedExo = 0
            for exos in pack['exos']:
                if ('finish' in pack['exos'][exos]):
                    finishedExo += 1
            packDict['finish'] = finishedExo
            packList.append(packDict)
        return (packList)
