import mysql.connector
import os
import srt
import re

from Cut import utils

# 数据库
class DatabaseConnector:
    def __init__(self, filename):
        self.filename = filename
        self.basename, _ = os.path.splitext(os.path.basename(self.filename))
        # self.dbname = dbname
        self.dbname = "video"

    # 获得数据库连接
    def getConnect(self):
        connector = mysql.connector.connect(
            host='localhost',
            user='root',
            password='root',  #密码
            db=self.dbname,
            auth_plugin='mysql_native_password' #如果有报错，添加此行代码
            # 报错信息mysql.connector.errors.NotSupportedError: Authentication plugin 'caching_sha2_password' is not supported
        )
        return connector

    # 新建一个数据库并插入数据
    def initDb(self):
        self.creatTable()
        self.insertAttribute()

    # 建表
    def creatTable(self):

        con = self.getConnect()
        cursor = con.cursor()

        cursor.execute(f"DROP TABLE IF EXISTS {self.basename}")
        creat_table = f"""

        CREATE TABLE {self.basename}(
        indexid  INT NOT NULL  PRIMARY KEY,
        starttime  varchar(20),
        endtime  varchar(20),
        content  varchar(255)
        )

        """
        try:
            # 执行SQL语句
            cursor.execute(creat_table)
            print("创建数据库成功")
        except Exception as e:
            print("创建数据库失败：case%s" % e)

        finally:
            # 关闭游标连接
            cursor.close()
            # 关闭数据库连接
            con.close()

    # 插入数据
    def insertAttribute(self):
        srt_file = utils.changeExt(self.filename, "srt")
        with open(srt_file, encoding="utf-8") as f:
            result = list(srt.parse(f.read()))

        con = self.getConnect()
        cursor = con.cursor()

        for r in result:
            insert_attribute = f"""

            INSERT INTO {self.basename} (indexid, starttime, endtime, content)
            VALUES (%s, %s, %s, %s)

            """
            value = (r.index, f'{r.start.seconds // 60:02d}:{r.start.seconds % 60:02d}', f'{r.end.seconds // 60:02d}:{r.end.seconds % 60:02d}', r.content)
            # print(value)
            try:
                # 执行SQL语句
                cursor.execute(insert_attribute, value)
                con.commit()
            except Exception as e:
                print("插入数据库失败：case%s" % e)

        print("插入数据完成")

        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        con.close()

    # 删除全部
    def deleteAllAttribute(self):
        con = self.getConnect()
        cursor = con.cursor()

        delete_attribute = f"""
            
        DELETE * FROM {self.basename}

        """

        cursor.execute(delete_attribute)

        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        con.close()

    # 删除某个id对应的数据
    def deleteByIndexid(self, indexid):
        con = self.getConnect()
        cursor = con.cursor()

        delete_attribute_by_id = f"""
        
                DELETE * FROM {self.basename}
                WHERE indexid = {indexid}

                """

        cursor.execute(delete_attribute_by_id)

        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        con.close()

    # select全部数据
    def selectAllAttribute(self):
        con = self.getConnect()
        cursor = con.cursor()

        select_attribute_all = f"""

                SELECT indexid, starttime, content  FROM {self.basename}

                """
        try:
            # 执行SQL语句
            cursor.execute(select_attribute_all)
            select_result = cursor.fetchall()
            return select_result
        except Exception as e:
            print("SELECT数据失败：case%s" % e)

        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        con.close()

    # select某一个数据
    def selectByIndexid(self, indexid):
        con = self.getConnect()
        cursor = con.cursor()

        select_attribute_by_id = f"""

                       SELECT indexid, starttime, content FROM {self.basename}
                       WHERE indexid = {indexid}

                       """
        try:
            # 执行SQL语句
            cursor.execute(select_attribute_by_id)
            select_result = cursor.fetchall()
            return select_result
        except Exception as e:
            print("SELECT数据失败：case%s" % e)

        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        con.close()

    # update某一个数据
    def updateByIndexid(self, indexid, update_content):
        con = self.getConnect()
        cursor = con.cursor()

        update_attribute_by_id = f"""

                               UPDATE {self.basename}
                               SET content = %s 
                               WHERE indexid = {indexid}

                               """
        try:
            # 执行SQL语句
            cursor.execute(update_attribute_by_id, (update_content, ))
            con.commit()
        except Exception as e:
            print("SELECT数据失败：case%s" % e)

        # 关闭游标连接
        cursor.close()
        # 关闭数据库连接
        con.close()

    # 句内去重
    def removeContentDuplicate(self):
        text = self.selectAllAttribute()
        for indexid, starttime, content in text:
            # 去除重复，保留后面的
            content = re.sub(r'\b(\w+)(?:\W+\1\b)+', r'\1', content, flags=re.IGNORECASE)
            self.updateByIndexid(indexid, content)
        return self.selectAllAttribute()

    # 整句子去重
    def removeSentenceDuplicate(self):
        text = self.removeContentDuplicate()
        unique_sentences = {}  # 用字典保存去重后的句子和对应的id
        for indexid, starttime, content in text:
            if content != "<<--   NULL   -->>":
                if content not in unique_sentences:
                    unique_sentences[content] = indexid
                else:
                    # 已存在重复内容，保留后面的部分
                    unique_sentences[content[-100:]] = indexid

        # 将去重后的结果转换为列表，并同时返回id列表
        unique_id_list = list(unique_sentences.values())
        return unique_id_list

    # 整句子去重保留空白
    def removeSentenceDuplicateKeepBlank(self):
        text = self.removeContentDuplicate()
        unique_sentences = {}  # 用字典保存去重后的句子和对应的id
        list_for_null = []
        for indexid, starttime, content in text:
            if content != "<<--   NULL   -->>":
                if content not in unique_sentences:
                    unique_sentences[content] = indexid
                else:
                    # 已存在重复内容，保留后面的部分
                    unique_sentences[content[-100:]] = indexid
            else:
                list_for_null.append(indexid)

        # 将去重后的结果转换为列表，并同时返回id列表
        unique_id_list = list(unique_sentences.values())+list_for_null
        return unique_id_list

